"""Run planning and execution. One run = (experiment, variant, mission, repeat), one manifest.

lvx executes on the machine that holds the data (the reference host). From a laptop, call it over ssh
and bring the small results back with `lvx sync` (see docs/how-to/run-an-experiment.md).

Run outputs are append-only:  <run_root>/<EXP>/<variant>/<mission>/r<k>/   (run_root from lvx.local.yaml)
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import __version__, config, paths, registry
from .spec import Experiment, set_status

CODE_PATHS = ["lvx", "configs", "systems", "tools"]  # dirtiness here invalidates a run


@dataclass
class RunKey:
    variant: str
    mission: str
    repeat: int

    @property
    def run_id(self) -> str:
        return f"{self.variant}__{self.mission}__r{self.repeat}"


def plan(exp: Experiment, variant: Optional[str] = None, mission: Optional[str] = None) -> List[RunKey]:
    variants = exp.variant_ids()
    missions = exp.missions()
    if variant and variant not in variants:
        raise SystemExit(f"{exp.id} has no variant '{variant}' (spec lists {variants})")
    if mission and mission not in missions:
        raise SystemExit(f"{exp.id} does not list mission '{mission}' (spec lists {missions})")
    keys = []
    for v in variants:
        for m in missions:
            for r in range(1, exp.spec["repeats"] + 1):
                if (variant is None or v == variant) and (mission is None or m == mission):
                    keys.append(RunKey(v, m, r))
    return keys


# --- configuration resolution -----------------------------------------------------------------

def resolve_config(exp: Experiment, variant: str) -> Dict[str, Any]:
    """Baseline config + the variant's single change -> the full config stored in the manifest."""
    base_name = exp.spec["baseline"]
    v: Dict[str, Any] = {}
    if variant != "baseline":
        v = next(x for x in exp.spec["variants"] if x["id"] == variant)
        base_name = v.get("baseline", base_name)
    base = registry.baseline(base_name)
    modes = [m for m in base.get("modes", []) if m not in (v.get("modes_remove") or [])]
    modes += [m for m in (v.get("modes_add") or []) if m not in modes]
    overrides = dict(base.get("overrides") or {})
    overrides.update(v.get("overrides") or {})
    cfg = {
        "baseline": base_name,
        "system": base["system"],
        "modes": modes,
        "overrides": overrides,
        "overrides_file": base.get("overrides_file"),
        "estimate": base.get("estimate", "estimate_prism"),
        "stress": exp.spec.get("stress"),
    }
    cfg["config_hash"] = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]
    return cfg


def _fmt(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(x) for x in value)
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def se3lvio_command(cfg: Dict[str, Any], mission: str, run_tag: str) -> str:
    sysdef = registry.systems()["se3-lvio"]
    mode_flags = " ".join(sysdef["modes"][m] for m in cfg["modes"])
    sets, backend = [], []
    for key, value in sorted(cfg["overrides"].items()):
        scope, _, field = key.partition(".")
        if scope == "lio":
            sets.append(f"--set {shlex.quote(field + '=' + _fmt(value))}")
        elif scope == "backend":
            backend.append(f"{field}={_fmt(value)}")
        else:
            raise SystemExit(f"se3-lvio override '{key}' must start with lio. or backend.")
    backend_flags = f"--backend-set {shlex.quote(','.join(backend))}" if backend else ""
    return sysdef["run"].format(mission=mission, run_tag=run_tag, mode_flags=mode_flags,
                                set_flags=" ".join(sets), backend_flags=backend_flags)


def set_dotted(tree: Dict[str, Any], key: str, value: Any) -> None:
    node = tree
    parts = key.split(".")
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    if parts[-1] not in node:
        raise KeyError(f"override '{key}' does not exist in the base config")
    node[parts[-1]] = value


def lightning_config(cfg: Dict[str, Any], upstream_dir: Path) -> Dict[str, Any]:
    """Upstream base config + our override file(s) + variant overrides. Upstream is never copied into git."""
    sysdef = registry.systems()["lightning-lm"]
    with open(upstream_dir / sysdef["base_config"]) as f:
        tree = yaml.safe_load(f)
    chain: List[Dict[str, Any]] = []
    path = paths.ROOT / cfg["overrides_file"] if cfg.get("overrides_file") else None
    while path is not None:
        layer = registry.load_yaml(path)
        chain.insert(0, layer)
        parent = layer.pop("_extends", None)
        path = path.parent / parent if parent else None
    missing_ok = {"fasterlio.plane_icp_weight", "fasterlio.proj_kfs"}  # absent upstream in default_robosense.yaml
    for layer in chain + [cfg["overrides"]]:
        for key, value in layer.items():
            try:
                set_dotted(tree, key, value)
            except KeyError:
                if key not in missing_ok:
                    raise
                tree.setdefault(key.split(".")[0], {})[key.split(".")[1]] = value
    return tree


# --- provenance -------------------------------------------------------------------------------

def git_state(repo: Path, subpaths: Optional[List[str]] = None) -> Dict[str, Any]:
    def g(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout.strip()
    status = g("status", "--porcelain", "--", *(subpaths or ["."]))
    return {"commit": g("rev-parse", "HEAD"), "dirty": bool(status)}


def image_digest(image: str) -> str:
    for tool in ("podman", "docker"):
        if shutil.which(tool):
            out = subprocess.run([tool, "image", "inspect", "--format", "{{.Id}}", image],
                                 capture_output=True, text=True)
            if out.returncode == 0:
                return out.stdout.strip()
    return "unknown"


def run_dir(exp: Experiment, key: RunKey) -> Path:
    return config.run_root() / exp.id / key.variant / key.mission / f"r{key.repeat}"


def mission_dir(mission: str) -> Path:
    root = config.dataset_dir("grandtour")
    hits = sorted(root.glob(f"*_{mission.upper()}_release_*"))
    if not hits:
        raise SystemExit(f"GrandTour mission {mission} not found in dataset 'grandtour' ({root}); "
                         "see docs/how-to/get-the-data.md")
    return hits[0]


# --- execution --------------------------------------------------------------------------------

def execute(exp: Experiment, key: RunKey, host_name: str, allow_dirty: bool = False,
            dry_run: bool = False) -> Dict[str, Any]:
    out = run_dir(exp, key)
    if (out / "manifest.json").exists():
        raise SystemExit(f"{out} already exists; runs are append-only (use a new repeat)")
    cfg = resolve_config(exp, key.variant)
    host = registry.host(host_name)
    system = cfg["system"]
    sysdef = registry.systems()[system]
    sys_dir = paths.ROOT / "systems" / system
    repo = git_state(paths.ROOT, CODE_PATHS)
    sysgit = git_state(sys_dir) if (sys_dir / ".git").exists() else {"commit": sysdef["pinned_commit"], "dirty": False}
    dirty = repo["dirty"] or sysgit["dirty"]
    if dirty and not allow_dirty:
        raise SystemExit("code is dirty (lvx/, configs/, systems/ or the system checkout); commit first")

    if system == "se3-lvio":
        cmd = se3lvio_command(cfg, key.mission, run_tag=f"{exp.id}-{key.run_id}")
        env = {"DATA": str(config.dataset_dir("grandtour")), "CPUSET": host["pinned_cpus"]}
        cwd = sys_dir
    else:
        cmd, env, cwd = lightning_invocation(cfg, key, host, out)

    manifest: Dict[str, Any] = {
        "lvx_version": __version__,
        "experiment": exp.id,
        "run_id": key.run_id,
        "variant": key.variant,
        "mission": key.mission,
        "repeat": key.repeat,
        "system": system,
        "config": cfg,
        "repo": repo,
        "system_git": sysgit,
        "image_digest": image_digest(config.image(system)),
        "host": host_name,
        "cpus": host["pinned_cpus"],
        "command": cmd,
        "status": "dirty" if dirty else "pending",
    }
    if dry_run:
        print(json.dumps(manifest, indent=2))
        return manifest

    out.mkdir(parents=True)
    if exp.status == "approved":
        set_status(exp, "running")
    manifest["started"] = _dt.datetime.now().isoformat(timespec="seconds")
    t0 = time.time()
    with open(out / "lvx_stdout.log", "w") as log:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, env={**os.environ, **env}, stdout=log,
                              stderr=subprocess.STDOUT)
    manifest.update(ended=_dt.datetime.now().isoformat(timespec="seconds"),
                    wall_s=round(time.time() - t0, 1), exit_code=proc.returncode)
    if system == "se3-lvio":
        collect_se3lvio(sys_dir, key, exp, out)
    if manifest["status"] != "dirty":
        manifest["status"] = "ok" if proc.returncode == 0 and (out / "estimate.tum").exists() else "failed"
    with open(out / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def collect_se3lvio(sys_dir: Path, key: RunKey, exp: Experiment, out: Path) -> None:
    """run_se3lio.sh writes results/<mission>-se3lio...-<tag>...; move it into the append-only run dir."""
    tag = f"{exp.id}-{key.run_id}"
    hits = [p for p in (sys_dir / "results").glob(f"{key.mission}-se3lio*") if tag in p.name]
    if not hits:
        return
    src = hits[0]
    cfg = resolve_config(exp, key.variant)
    estimate = {"estimate_prism": f"{key.mission}.tum",
                "estimate_backend_prism": f"{key.mission}_backend_prism.tum"}[cfg["estimate"]]
    for name in os.listdir(src):
        shutil.move(str(src / name), str(out / name))
    src.rmdir()
    if (out / estimate).exists():
        shutil.copy(out / estimate, out / "estimate.tum")


def lightning_invocation(cfg: Dict[str, Any], key: RunKey, host: Dict[str, Any], out: Path):
    """podman run of our runner on the mission bag; to_prism with the same tool as SE(3)-LVIO."""
    sysdef = registry.systems()["lightning-lm"]
    workspace = config.system_root("lightning-lm") / f"lightning-lm-{sysdef['pinned_commit']}"
    upstream = workspace / "src" / "lightning-lm"
    bag = config.run_root() / "derived" / "lightning-bags" / key.mission    # made by offline_to_ros2bag.py
    if not (upstream / "bin" / "run_lio_tum").exists():
        raise SystemExit(f"lightning-lm not built at {upstream}; run scripts/build_lightning.sh first")
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "config.yaml", "w") as f:
        yaml.safe_dump(lightning_config(cfg, upstream), f, sort_keys=False)
    inner = sysdef["run"].format(cpus=host["pinned_cpus"], bag="/bag", config="/out/config.yaml",
                                 out_imu_tum=f"/out/{key.mission}_imu.tum", timing_csv="/out/timing.csv",
                                 log_dir="/out")
    mdir = mission_dir(key.mission) / "comfort_offline"
    se3 = paths.ROOT / "systems" / "se3-lvio"
    cmd = (
        f"podman run --rm -v {upstream}:/ll -v {bag}:/bag:ro -v {out}:/out -w /ll {config.image('lightning-lm')} "
        f"bash -c {shlex.quote(inner)} > {out}/run.log 2>&1 && "
        f"python3 {se3}/tools/to_prism.py {mdir}/calib.json {out}/{key.mission}_imu.tum {out}/estimate.tum"
    )
    return cmd, {}, out
