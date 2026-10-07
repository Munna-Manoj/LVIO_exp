"""Everything lvx looks up, in one file: repo paths, the tracked YAML registries, and this machine's setup.

Tracked files name things logically (dataset `sad-ulhk`, system `sad`, host profile `reference`, mission
`arc-6`). This module maps those names to files, from (highest priority first):

  1. environment variables   LVX_DATA_ROOT, LVX_RUN_ROOT, LVX_SAD_ROOT   (CI, one-off overrides)
  2. lvx.local.yaml          at the repo root, or the file named by LVX_CONFIG   (git-ignored, see
                             configs/local.example.yaml; create it with `lvx init`)
  3. defaults                datasets live at <data_root>/<dataset dir from configs/datasets.yaml>

Real paths, ssh aliases and local image tags live ONLY in lvx.local.yaml (CLAUDE.md §12).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# --- repository paths (the only form written into tracked files is rel(path)) --------------------
ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = ROOT / "experiments"
TEMPLATE = EXPERIMENTS / "_template"
CONFIGS = ROOT / "configs"
BASELINES = CONFIGS / "baselines"
HOSTS = CONFIGS / "hosts"
DOCS = ROOT / "docs"
REPORTS = DOCS / "experiments"
FIGURES = DOCS / "assets" / "experiments"
REGISTRY = EXPERIMENTS / "registry.md"
README = ROOT / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
LOCAL_FILE = ROOT / "lvx.local.yaml"
ENV = {"data_root": "LVX_DATA_ROOT", "run_root": "LVX_RUN_ROOT"}


def rel(path: Path) -> str:
    """Repo-relative POSIX path."""
    return Path(path).resolve().relative_to(ROOT).as_posix()


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f) or {}


class NotConfigured(SystemExit):
    """Raised with a message that tells the user exactly what to set."""


# --- tracked registries: missions, systems, baselines, host profiles, stress profiles --------------

def missions() -> Dict[str, Dict[str, Any]]:
    return load_yaml(CONFIGS / "missions.yaml")["missions"]


def resolve_missions(spec_missions: Dict[str, Any]) -> List[str]:
    """`{set: dev}` or `{list: [arc-6, spx-2]}` -> mission names, checked against configs/missions.yaml."""
    known = missions()
    if "set" in spec_missions:
        sets = load_yaml(CONFIGS / "missions.yaml").get("sets", {})
        if spec_missions["set"] not in sets:
            raise ValueError(f"unknown mission set '{spec_missions['set']}' (known: {sorted(sets)})")
        names = list(sets[spec_missions["set"]])
    elif "list" in spec_missions:
        names = list(spec_missions["list"])
    else:
        raise ValueError("missions needs `set:` or `list:`")
    unknown = [m for m in names if m not in known]
    if unknown:
        raise ValueError(f"missions not in configs/missions.yaml: {unknown}")
    return names


def systems() -> Dict[str, Dict[str, Any]]:
    return load_yaml(ROOT / "systems" / "systems.yaml")


def baseline(name: str) -> Dict[str, Any]:
    path = BASELINES / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"baseline '{name}' not found in configs/baselines/")
    data = load_yaml(path)
    if data.get("system") not in systems():
        raise ValueError(f"baseline '{name}' names unknown system '{data.get('system')}'")
    return data


def host_profile(name: str) -> Dict[str, Any]:
    """Tracked hardware description (configs/hosts/<name>.yaml): CPUs to pin, cores. No paths."""
    path = HOSTS / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"host profile '{name}' not found in configs/hosts/")
    return load_yaml(path)


def stress_profiles() -> Dict[str, Any]:
    return load_yaml(CONFIGS / "stress.yaml").get("profiles") or {}


# --- this machine (lvx.local.yaml + env) -----------------------------------------------------------

def local_file() -> Path:
    return Path(os.environ["LVX_CONFIG"]).expanduser() if os.environ.get("LVX_CONFIG") else LOCAL_FILE


def load() -> Dict[str, Any]:
    f = local_file()
    return load_yaml(f) if f.exists() else {}


def _path(value: str, base: Optional[Path] = None) -> Path:
    p = Path(os.path.expandvars(str(value))).expanduser()
    return p if p.is_absolute() or base is None else base / p


def _root(key: str) -> Path:
    if os.environ.get(ENV[key]):
        return _path(os.environ[ENV[key]])
    cfg = load()
    if cfg.get(key):
        return _path(cfg[key])
    raise NotConfigured(f"`{key}` is not configured: run `lvx init --{key.replace('_', '-')} <dir>` "
                        f"(writes lvx.local.yaml) or set {ENV[key]}. See docs/how-to/setup.md")


def data_root() -> Path:
    return _root("data_root")


def run_root() -> Path:
    return _root("run_root")


def system_root(name: str) -> Path:
    """Where a system built outside the repo lives (SAD, the lightning-lm workspace)."""
    if name == "sad" and os.environ.get("LVX_SAD_ROOT"):
        return _path(os.environ["LVX_SAD_ROOT"])
    root = ((load().get("systems") or {}).get(name) or {}).get("root")
    return _path(root) if root else run_root() / "systems" / name


def image(name: str) -> str:
    """The container image for a system: local tag override, else the neutral tag in systems/systems.yaml."""
    local = ((load().get("systems") or {}).get(name) or {}).get("image")
    return local or systems()[name]["image"]


def host(profile: str) -> Dict[str, Any]:
    """How to reach the machine that plays a host profile (ssh alias, checkout): local only."""
    h = (load().get("hosts") or {}).get(profile)
    if not h:
        raise NotConfigured(f"host profile '{profile}' has no local entry: add `hosts: {{{profile}: "
                            f"{{ssh: <alias>, repo: <path>}}}}` to lvx.local.yaml")
    return h


def private_tokens() -> List[str]:
    """Words that must never appear in tracked files (user names, host names); local only."""
    return [t for t in (load().get("private_tokens") or []) if t]


def write_local(values: Dict[str, Any]) -> Path:
    cfg = load()
    cfg.update({k: v for k, v in values.items() if v is not None})
    f = local_file()
    with open(f, "w") as fh:
        fh.write("# Machine-specific lvx configuration. Git-ignored: never commit it. "
                 "Template: configs/local.example.yaml\n")
        yaml.safe_dump(cfg, fh, sort_keys=False)
    return f


# --- datasets by name -------------------------------------------------------------------------------

def dataset_registry() -> Dict[str, Dict[str, Any]]:
    return load_yaml(CONFIGS / "datasets.yaml")["datasets"]


def dataset_dir(name: str) -> Path:
    """Where dataset `name` lives on this machine: a local override, else <data_root>/<dir>."""
    reg = dataset_registry()
    if name not in reg:
        raise SystemExit(f"unknown dataset '{name}' (known: {', '.join(reg)})")
    override = (load().get("datasets") or {}).get(name)
    if override:
        return _path(override, data_root())
    if name == "sad-builtin":
        return system_root("sad") / "data"
    return data_root() / reg[name]["dir"]


def dataset_missing(name: str) -> List[str]:
    """Expected files (configs/datasets.yaml `files`) that are absent; [] when the dataset is ready."""
    d = dataset_dir(name)
    if not d.is_dir():
        return [d.name + "/"]
    return [f for f in dataset_registry()[name].get("files") or [] if not any(d.glob(f))]


def dataset(name: str) -> Path:
    """Directory of dataset `name`; raises with the official download links if it is not there yet."""
    d = dataset_dir(name)
    missing = dataset_missing(name)
    if missing:
        reg = dataset_registry()[name]
        links = []
        if reg.get("source") == "sad_download":
            dl = load_yaml(CONFIGS / "datasets.yaml")["sad_download"]
            links += [f"OneDrive {dl['onedrive']}", f"Baidu {dl['baidu']}"]
        links += [f"{k} {reg[k]}" for k in ("huggingface", "official") if reg.get(k)]
        raise SystemExit(
            f"dataset '{name}' not ready at {d} (missing: {', '.join(missing)}).\n"
            f"  get it: {'; '.join(links) or 'see docs/how-to/get-the-data.md'}\n"
            f"  then place it there, or point lvx at it: lvx init --dataset {name}=<dir>\n"
            f"  details: docs/how-to/get-the-data.md")
    return d


def data_status() -> List[Dict[str, object]]:
    """One row per registered dataset: where lvx looks, whether it is ready, which chapters/labs use it."""
    rows = []
    for name, reg in dataset_registry().items():
        try:
            where: Optional[Path] = dataset_dir(name)
            missing = dataset_missing(name)
            state = "ready" if not missing else f"missing {', '.join(missing)}"
        except SystemExit:
            where, state = None, "not configured (run `lvx init`)"
        rows.append({"name": name, "where": where, "state": state, "used_by": reg.get("used_by") or [],
                     "title": reg["title"]})
    return rows


def mission_dir(mission: str) -> Path:
    """The GrandTour mission folder (…/<NN>_<MISSION>_release_hf/) inside dataset `grandtour`."""
    root = dataset_dir("grandtour")
    hits = sorted(root.glob(f"*_{mission.upper()}_release_*"))
    if not hits:
        raise SystemExit(f"GrandTour mission {mission} not found in dataset 'grandtour' ({root}); "
                         "see docs/how-to/get-the-data.md")
    return hits[0]
