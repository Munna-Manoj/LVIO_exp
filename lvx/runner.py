"""From a frozen spec to the exact command that runs, in one file. One run = (experiment, variant, mission,
repeat) = one directory with one manifest.

    spec.yaml ──resolve_config()──> baseline YAML + the variant's one change
              ──*_command()───────> the shell command, written out below for each system
              ──execute()─────────> runs it, writes manifest.json (command, config, commits, timing)

The command never contains a machine path: every location is an environment variable ($OUT, $GRANDTOUR,
…) that execute() sets from lvx.local.yaml. So the manifest holds exactly the command that ran, and it can
be published as it is (the report's Reproduce section shows it). ENV_MEANING says what each variable is.

lvx runs on the machine that holds the data (host profile `reference`); `lvx sync` brings results back.
Run outputs are append-only:  <run_root>/<EXP>/<variant>/<mission>/r<k>/
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

from . import __version__, config
from .spec import Experiment, set_status

CODE_PATHS = ["lvx", "configs", "systems", "tools"]  # uncommitted changes here make a run "dirty"
ENV_MEANING = {
    "OUT": "this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>",
    "GRANDTOUR": "dataset `grandtour` (configs/datasets.yaml)",
    "MISSION": "the mission folder inside $GRANDTOUR",
    "IMAGE": "the system's container image (systems/systems.yaml; local tag in lvx.local.yaml)",
    "LIGHTNING_WS": "the lightning-lm colcon workspace built by scripts/build_lightning.sh",
    "BAG": "the mission as a ROS 2 bag: <run_root>/derived/lightning-bags/<mission>",
    "PATH": "the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)",
}


@dataclass
class RunKey:
    variant: str
    mission: str
    repeat: int

    @property
    def run_id(self) -> str:
        return f"{self.variant}__{self.mission}__r{self.repeat}"


def plan(exp: Experiment, variant: Optional[str] = None, mission: Optional[str] = None) -> List[RunKey]:
    """Every (variant, mission, repeat) the spec asks for, optionally filtered."""
    if variant and variant not in exp.variant_ids():
        raise SystemExit(f"{exp.id} has no variant '{variant}' (spec lists {exp.variant_ids()})")
    if mission and mission not in exp.missions():
        raise SystemExit(f"{exp.id} does not list mission '{mission}' (spec lists {exp.missions()})")
    return [RunKey(v, m, r)
            for v in exp.variant_ids() if variant in (None, v)
            for m in exp.missions() if mission in (None, m)
            for r in range(1, exp.spec["repeats"] + 1)]


def run_dir(exp: Experiment, key: RunKey) -> Path:
    return config.run_root() / exp.id / key.variant / key.mission / f"r{key.repeat}"


# --- 1. spec -> configuration ------------------------------------------------------------------------

def resolve_config(exp: Experiment, variant: str) -> Dict[str, Any]:
    """configs/baselines/<baseline>.yaml + the variant's single change -> the config stored in the manifest."""
    base_name = exp.spec["baseline"]
    v: Dict[str, Any] = {}
    if variant != "baseline":
        v = next(x for x in exp.spec["variants"] if x["id"] == variant)
        base_name = v.get("baseline", base_name)
    base = config.baseline(base_name)
    modes = [m for m in base.get("modes", []) if m not in (v.get("modes_remove") or [])]
    modes += [m for m in (v.get("modes_add") or []) if m not in modes]
    cfg = {
        "baseline": base_name,
        "system": base["system"],
        "modes": modes,
        "overrides": {**(base.get("overrides") or {}), **(v.get("overrides") or {})},
        "overrides_file": base.get("overrides_file"),
        "estimate": base.get("estimate", "estimate_prism"),
        "stress": exp.spec.get("stress"),
    }
    cfg["config_hash"] = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]
    return cfg


# --- 2. configuration -> command, one function per system ------------------------------------------

SE3LVIO_MODE_FLAGS = {"lio_only": "--lio-only", "lidar_multi": "--lidar multi", "backend": "--backend"}
LIGHTNING_NEW_KEYS = {"fasterlio.plane_icp_weight", "fasterlio.proj_kfs"}  # absent upstream in default_robosense


def se3lvio_command(cfg: Dict[str, Any], mission: str, run_tag: str, cpus: str) -> str:
    """systems/se3-lvio/scripts/run_se3lio.sh, run from the submodule. It reads DATA, CPUSET and IMAGE
    from the environment and writes results/<mission>-se3lio…-<tag>/ inside the submodule."""
    flags = [SE3LVIO_MODE_FLAGS[m] for m in cfg["modes"]]
    backend = []
    for key, value in sorted(cfg["overrides"].items()):        # lio.<field> -> --set, backend.<key> -> --backend-set
        scope, _, field = key.partition(".")
        if scope == "lio":
            flags.append(f"--set {shlex.quote(f'{field}={_fmt(value)}')}")
        elif scope == "backend":
            backend.append(f"{field}={_fmt(value)}")
        else:
            raise SystemExit(f"se3-lvio override '{key}' must start with lio. or backend.")
    if backend:
        flags.append(f"--backend-set {shlex.quote(','.join(backend))}")
    return (f'DATA="$GRANDTOUR" CPUSET={cpus} IMAGE="$IMAGE" '
            f"bash scripts/run_se3lio.sh {mission} --tag {run_tag} {' '.join(flags)}").strip()


def lightning_command(mission: str, cpus: str) -> str:
    """Our headless runner (systems/lightning-lm/runner/run_lio_tum.cc) in the lightning-lm image, on the
    mission bag, with the config lvx wrote to $OUT/config.yaml; then the same IMU -> prism conversion
    SE(3)-LVIO uses. Run from the repo root."""
    inner = ("source /opt/ros/humble/setup.bash && source /ws/install/setup.bash && "
             f"taskset -c {cpus} ./bin/run_lio_tum --input_bag /bag --config /out/config.yaml "
             f"--output /out/{mission}_imu.tum --timing /out/timing.csv --log_dir /out")
    return ('podman run --rm -v "$LIGHTNING_WS":/ws -v "$BAG":/bag:ro -v "$OUT":/out -w /ws/src/lightning-lm '
            f'"$IMAGE" bash -c {shlex.quote(inner)} > "$OUT/run.log" 2>&1 && '
            'python3 systems/se3-lvio/tools/to_prism.py "$MISSION/comfort_offline/calib.json" '
            f'"$OUT/{mission}_imu.tum" "$OUT/estimate.tum"')


def lightning_config(cfg: Dict[str, Any], upstream_dir: Path) -> Dict[str, Any]:
    """Upstream config/default_robosense.yaml + our override file + the variant's overrides (dotted keys).
    Upstream is never copied into git (no licence, ADR-0003); only the keys we change are tracked."""
    with open(upstream_dir / "config" / "default_robosense.yaml") as f:
        tree = yaml.safe_load(f)
    layers = [config.load_yaml(config.ROOT / cfg["overrides_file"])] if cfg.get("overrides_file") else []
    for layer in layers + [cfg["overrides"]]:
        for key, value in layer.items():
            *parents, leaf = key.split(".")
            node = tree
            for p in parents:
                node = node.setdefault(p, {})
            if leaf not in node and key not in LIGHTNING_NEW_KEYS:
                raise KeyError(f"override '{key}' does not exist in upstream default_robosense.yaml")
            node[leaf] = value
    return tree


def _fmt(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(x) for x in value)
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


# --- 3. run it ---------------------------------------------------------------------------------------

def git_state(repo: Path, subpaths: Optional[List[str]] = None) -> Dict[str, Any]:
    def g(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout.strip()
    return {"commit": g("rev-parse", "HEAD"), "dirty": bool(g("status", "--porcelain", "--", *(subpaths or ["."])))}


def image_digest(image: str) -> str:
    for tool in ("podman", "docker"):
        if shutil.which(tool):
            out = subprocess.run([tool, "image", "inspect", "--format", "{{.Id}}", image],
                                 capture_output=True, text=True)
            if out.returncode == 0:
                return out.stdout.strip()
    return "unknown"


def execute(exp: Experiment, key: RunKey, host_name: str, allow_dirty: bool = False,
            dry_run: bool = False) -> Dict[str, Any]:
    out = run_dir(exp, key)
    if (out / "manifest.json").exists():
        raise SystemExit(f"{out} already exists; runs are append-only (use a new repeat)")
    cfg = resolve_config(exp, key.variant)
    system = cfg["system"]
    pin = str(config.systems()[system]["pinned_commit"])
    cpus = config.host_profile(host_name)["pinned_cpus"]

    # Provenance: this repo and the system's code are committed, and the system sits at its pin.
    repo = git_state(config.ROOT, CODE_PATHS)
    sys_dir = config.ROOT / "systems" / system
    sysgit = git_state(sys_dir) if (sys_dir / ".git").exists() else {"commit": pin, "dirty": False}
    dirty = repo["dirty"] or sysgit["dirty"]
    if dirty and not allow_dirty:
        raise SystemExit("code is dirty (lvx/, configs/, systems/ or the system checkout); commit first")
    if not (sysgit["commit"].startswith(pin) or pin.startswith(sysgit["commit"])):
        raise SystemExit(f"systems/{system} is at {sysgit['commit'][:7]} but systems.yaml pins {pin[:7]}: "
                         "run `git submodule update`, or bump the pin in its own commit")

    # The command, and the machine locations it refers to (in env only, never in the command text).
    env = {"OUT": str(out), "GRANDTOUR": str(config.dataset_dir("grandtour")),
           "MISSION": str(config.mission_dir(key.mission)), "IMAGE": config.image(system)}
    if config.extra_path():
        env["PATH"] = os.pathsep.join([*map(str, config.extra_path()), os.environ.get("PATH", "")])
    if system == "se3-lvio":
        command = se3lvio_command(cfg, key.mission, run_tag=f"{exp.id}-{key.run_id}", cpus=cpus)
        cwd = "systems/se3-lvio"
    else:
        workspace = config.system_root("lightning-lm") / f"lightning-lm-{pin}"
        if not (workspace / "src" / "lightning-lm" / "bin" / "run_lio_tum").exists():
            raise SystemExit(f"lightning-lm not built at {workspace}; run scripts/build_lightning.sh first")
        env["LIGHTNING_WS"] = str(workspace)
        env["BAG"] = str(config.run_root() / "derived" / "lightning-bags" / key.mission)
        command = lightning_command(key.mission, cpus)
        cwd = "."

    manifest: Dict[str, Any] = {
        "lvx_version": __version__, "experiment": exp.id, "run_id": key.run_id, "variant": key.variant,
        "mission": key.mission, "repeat": key.repeat, "system": system, "config": cfg,
        "command": command, "cwd": cwd, "env": {k: ENV_MEANING[k] for k in env},
        "repo": repo, "system_git": sysgit, "image_digest": image_digest(env["IMAGE"]),
        "host": host_name, "cpus": cpus, "status": "dirty" if dirty else "pending",
    }
    if dry_run:
        print(json.dumps(manifest, indent=2))
        return manifest

    out.mkdir(parents=True)
    if system == "lightning-lm":
        upstream = Path(env["LIGHTNING_WS"]) / "src" / "lightning-lm"
        (out / "config.yaml").write_text(yaml.safe_dump(lightning_config(cfg, upstream), sort_keys=False))
    if exp.status == "approved":
        set_status(exp, "running")
    manifest["started"] = _dt.datetime.now().isoformat(timespec="seconds")
    t0 = time.time()
    with open(out / "lvx_stdout.log", "w") as log:
        proc = subprocess.run(command, shell=True, executable="/bin/bash", cwd=config.ROOT / cwd,
                              env={**os.environ, **env}, stdout=log, stderr=subprocess.STDOUT)
    manifest.update(ended=_dt.datetime.now().isoformat(timespec="seconds"),
                    wall_s=round(time.time() - t0, 1), exit_code=proc.returncode)
    if system == "se3-lvio":
        collect_se3lvio(sys_dir, key, exp, out, cfg["estimate"])
    if manifest["status"] != "dirty":
        manifest["status"] = "ok" if proc.returncode == 0 and (out / "estimate.tum").exists() else "failed"
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def collect_se3lvio(sys_dir: Path, key: RunKey, exp: Experiment, out: Path, estimate: str) -> None:
    """run_se3lio.sh writes systems/se3-lvio/results/<mission>-se3lio…-<tag>…/; move it into the run dir
    and copy the estimate this baseline is scored on to `estimate.tum`."""
    tag = f"{exp.id}-{key.run_id}"
    hits = [p for p in (sys_dir / "results").glob(f"{key.mission}-se3lio*") if tag in p.name]
    if not hits:
        return
    for f in hits[0].iterdir():
        shutil.move(str(f), str(out / f.name))
    hits[0].rmdir()
    name = {"estimate_prism": f"{key.mission}.tum", "estimate_backend_prism": f"{key.mission}_backend_prism.tum"}
    if (out / name[estimate]).exists():
        shutil.copy(out / name[estimate], out / "estimate.tum")
