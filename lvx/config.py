"""Machine configuration: the ONLY place real paths, ssh aliases and local image tags live.

Tracked files name things logically (dataset `sad-ulhk`, system `sad`, host profile `reference`). This module
maps those names to this machine, from (highest priority first):

  1. environment variables   LVX_DATA_ROOT, LVX_RUN_ROOT, LVX_SAD_ROOT   (CI, one-off overrides)
  2. lvx.local.yaml          at the repo root, or the file named by LVX_CONFIG   (git-ignored, see
                             configs/local.example.yaml; create it with `lvx init`)
  3. defaults                datasets live at <data_root>/<dataset dir from configs/datasets.yaml>
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import paths

LOCAL_FILE = paths.ROOT / "lvx.local.yaml"
EXAMPLE_FILE = paths.CONFIGS / "local.example.yaml"
ENV = {"data_root": "LVX_DATA_ROOT", "run_root": "LVX_RUN_ROOT"}


class NotConfigured(SystemExit):
    """Raised with a message that tells the user exactly what to set."""


def local_file() -> Path:
    return Path(os.environ["LVX_CONFIG"]).expanduser() if os.environ.get("LVX_CONFIG") else LOCAL_FILE


def load() -> Dict[str, Any]:
    f = local_file()
    if not f.exists():
        return {}
    with open(f) as fh:
        return yaml.safe_load(fh) or {}


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


# --- datasets ----------------------------------------------------------------------------------

def dataset_registry() -> Dict[str, Dict[str, Any]]:
    with open(paths.CONFIGS / "datasets.yaml") as f:
        return yaml.safe_load(f)["datasets"]


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
        return [str(d.name) + "/"]
    return [f for f in dataset_registry()[name].get("files") or [] if not any(d.glob(f))]


# --- systems, images, hosts --------------------------------------------------------------------

def system_root(name: str) -> Path:
    env = {"sad": "LVX_SAD_ROOT"}.get(name)
    if env and os.environ.get(env):
        return _path(os.environ[env])
    root = ((load().get("systems") or {}).get(name) or {}).get("root")
    if root:
        return _path(root)
    return run_root() / "systems" / name


def image(name: str) -> str:
    """The container image for a system: local tag override, else the neutral tag in systems/systems.yaml."""
    local = ((load().get("systems") or {}).get(name) or {}).get("image")
    if local:
        return local
    with open(paths.SYSTEMS_FILE) as f:
        return yaml.safe_load(f)[name]["image"]


def host(profile: str) -> Dict[str, Any]:
    """How to reach the machine that plays a tracked host profile (ssh alias, checkout, python)."""
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
