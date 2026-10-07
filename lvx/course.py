"""The curriculum (course/curriculum.yaml) and C++ labs on the official SAD code.

A lab runs one SAD app in a scratch sandbox, because SAD apps write their outputs into ./data/:
  sandbox/ bin, lib, config -> read-only SAD tree;  data/ch<N> copied;  /data -> the lab's dataset (ro)
Recorded (tracked) in course/chapters/<ID>-<slug>/results/labs/<lab>/: manifest.json + log_tail.txt.
Full logs and outputs stay in <run_root>/labs/<lab>/r<k>/ (append-only; run_root from lvx.local.yaml).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from . import __version__, config, paths, registry
from .data import dataset

CURRICULUM = paths.ROOT / "course" / "curriculum.yaml"
CHAPTER_DIRS = paths.ROOT / "course" / "chapters"
ID_RE = re.compile(r"^([A-GX]|I)\d{2}$")  # I = bridge chapters (not in the SAD book)
STATUSES = ["planned", "drafted", "done"]
LOG_TAIL_LINES = 60


def curriculum() -> Dict[str, Any]:
    return registry.load_yaml(CURRICULUM)


def chapters() -> List[Dict[str, Any]]:
    return curriculum()["chapters"]


def chapter(cid: str) -> Dict[str, Any]:
    for c in chapters():
        if c["id"] == cid:
            return c
    raise SystemExit(f"no chapter {cid} in course/curriculum.yaml")


def chapter_name(c: Dict[str, Any]) -> str:
    return f"{c['id']}-{c['slug']}"


def labs() -> Dict[str, Dict[str, Any]]:
    return curriculum().get("labs") or {}


def validate() -> List[str]:
    cur = curriculum()
    err: List[str] = []
    parts = cur["parts"]
    ids = [c["id"] for c in cur["chapters"]]
    if len(ids) != len(set(ids)):
        err.append("duplicate chapter ids")
    datasets = registry.load_yaml(paths.CONFIGS / "datasets.yaml")["datasets"]
    exp_ids = {p.name[:7] for p in paths.EXPERIMENTS.glob("EXP-*")}
    seen: List[str] = []
    for c in cur["chapters"]:
        where = c["id"]
        bridge = c.get("kind") == "bridge"
        if not ID_RE.match(c["id"]) or c["part"] not in parts or (c["id"][0] != ("I" if bridge else c["part"])):
            err.append(f"{where}: id must be <part letter><2 digits>, or I<2 digits> for a bridge chapter")
        if bridge and (c.get("sad") or not c.get("datasets")):
            err.append(f"{where}: a bridge chapter has no `sad:` entry and must list real `datasets`")
        for ds in c.get("datasets") or []:
            if ds not in datasets:
                err.append(f"{where}: dataset {ds} not in configs/datasets.yaml")
        if c["status"] not in STATUSES:
            err.append(f"{where}: status '{c['status']}' not in {STATUSES}")
        for d in c.get("depends_on") or []:
            if d not in seen:
                err.append(f"{where}: depends_on {d} must be an EARLIER chapter (the course is ordered)")
        for e in c.get("experiments") or []:
            if e not in exp_ids:
                err.append(f"{where}: experiment {e} does not exist")
        for lab in c.get("labs") or []:
            if lab not in cur.get("labs", {}):
                err.append(f"{where}: lab {lab} not defined under labs:")
        seen.append(c["id"])
    for lab_id, lab in (cur.get("labs") or {}).items():
        if lab["chapter"] not in ids:
            err.append(f"lab {lab_id}: chapter {lab['chapter']} unknown")
        elif lab_id not in (chapter(lab["chapter"]).get("labs") or []):
            err.append(f"lab {lab_id}: not listed in chapter {lab['chapter']} labs")
        if lab["dataset"] not in datasets:
            err.append(f"lab {lab_id}: dataset {lab['dataset']} not in configs/datasets.yaml")
        if lab.get("status") not in ("planned", "verified"):
            err.append(f"lab {lab_id}: status must be planned or verified")
        if lab.get("status") == "verified" and not (lab_results_dir(lab_id) / "manifest.json").exists():
            err.append(f"lab {lab_id}: verified but no recorded manifest")
    return err


# --- labs ---------------------------------------------------------------------------------------

def lab_results_dir(lab_id: str) -> Path:
    lab = labs()[lab_id]
    return CHAPTER_DIRS / chapter_name(chapter(lab["chapter"])) / "results" / "labs" / lab_id


def sad_root() -> Path:
    root = config.system_root("sad")
    if not (root / "bin").is_dir():
        raise SystemExit(f"SAD build not found at {root}: set `systems: {{sad: {{root: <dir>}}}}` in "
                         "lvx.local.yaml (or LVX_SAD_ROOT). See docs/how-to/setup.md")
    return root


def run_lab(lab_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Run one SAD app in a sandbox. Container view:
         /sad      sandbox (bin, lib, config -> /sad_src;  data/ch<N> copied, the app writes here)
         /sad_src  the SAD build, read-only
         /data     the lab's dataset, read-only ({data} in the lab args)
    """
    if lab_id not in labs():
        raise SystemExit(f"no lab {lab_id} (see `lvx lab list`)")
    lab = labs()[lab_id]
    sysdef = registry.systems()["sad"]
    root = sad_root()
    sad_chapter = chapter(lab["chapter"])["sad"]["chapter"]
    data_dirs = sorted({f"ch{sad_chapter}"} | ({"ch3"} if sad_chapter == 4 else set()))
    data_mount = ""
    if lab["dataset"] != "sad-builtin":
        data_mount = f"-v {dataset(lab['dataset'])}:/data:ro "
    base = config.run_root() / "labs" / lab_id
    k = 1
    while (base / f"r{k}").exists():
        k += 1
    out = base / f"r{k}"
    image = config.image("sad")
    inner = sysdef["run"].format(app=lab["app"], args=lab["args"].format(data="/data"))
    cmd = (f"podman run --rm -v {out}/sandbox:/sad -v {root}:/sad_src:ro {data_mount}"
           f"-w /sad {image} bash -c {shlex.quote(inner)}")
    manifest: Dict[str, Any] = {
        "lvx_version": __version__, "lab": lab_id, "chapter": lab["chapter"], "app": lab["app"],
        "args": lab["args"], "dataset": lab["dataset"], "repeat": k,
        "sad_commit": _git_head(root), "pinned_commit": sysdef["pinned_commit"],
        "image_id": _image_id(image), "command": cmd,
    }
    if dry_run:
        print(json.dumps(manifest, indent=2))
        return manifest
    sandbox = out / "sandbox"
    (sandbox / "data").mkdir(parents=True)
    for name in ("bin", "lib", "config"):
        os.symlink(f"/sad_src/{name}", sandbox / name)       # resolved inside the container
    for d in data_dirs:
        if (root / "data" / d).exists():
            shutil.copytree(root / "data" / d, sandbox / "data" / d)
    manifest["started"] = _dt.datetime.now().isoformat(timespec="seconds")
    t0 = time.time()
    with open(out / "log.txt", "w") as log:
        proc = subprocess.run(cmd, shell=True, stdout=log, stderr=subprocess.STDOUT)
    manifest.update(ended=_dt.datetime.now().isoformat(timespec="seconds"), wall_s=round(time.time() - t0, 1),
                    exit_code=proc.returncode, status="ok" if proc.returncode == 0 else "failed")
    with open(out / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    record = lab_results_dir(lab_id)
    record.mkdir(parents=True, exist_ok=True)
    tracked = {k2: v for k2, v in manifest.items() if k2 != "command"}   # the command holds local paths
    with open(record / "manifest.json", "w") as f:
        json.dump(tracked, f, indent=2)
    lines = (out / "log.txt").read_text(errors="replace").splitlines()[-LOG_TAIL_LINES:]
    (record / "log_tail.txt").write_text("\n".join(scrub(x) for x in lines) + "\n")
    return manifest


def _git_head(root: Path) -> str:
    r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def _image_id(image: str) -> str:
    """Content digest of the local image: identifies the build without leaking the local tag."""
    if not shutil.which("podman"):
        return "unknown"
    r = subprocess.run(["podman", "image", "inspect", "--format", "{{.Id}}", image], capture_output=True, text=True)
    return r.stdout.strip()[:19] if r.returncode == 0 else "unknown"


def scrub(line: str) -> str:
    """Remove machine-specific paths and private tokens from text that gets tracked."""
    line = re.sub(r"/(home|hdd|Users|mnt|media|srv)/[^\s'\"]+", "<host-path>", line)
    for token in config.private_tokens():
        line = re.sub(re.escape(token), "<private>", line, flags=re.I)
    return line
