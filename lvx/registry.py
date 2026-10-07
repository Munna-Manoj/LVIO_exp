"""Missions, systems, baselines and hosts: the shared registries every experiment points into."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from . import paths


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}


def missions() -> Dict[str, Dict[str, Any]]:
    return load_yaml(paths.MISSIONS_FILE)["missions"]


def mission_sets() -> Dict[str, List[str]]:
    return load_yaml(paths.MISSIONS_FILE).get("sets", {})


def resolve_missions(spec_missions: Dict[str, Any]) -> List[str]:
    """`{set: dev}` or `{list: [arc-6, spx-2]}` -> mission names, validated against the registry."""
    known = missions()
    if "set" in spec_missions:
        sets = mission_sets()
        name = spec_missions["set"]
        if name not in sets:
            raise ValueError(f"unknown mission set '{name}' (known: {sorted(sets)})")
        names = list(sets[name])
    elif "list" in spec_missions:
        names = list(spec_missions["list"])
    else:
        raise ValueError("missions needs `set:` or `list:`")
    unknown = [m for m in names if m not in known]
    if unknown:
        raise ValueError(f"missions not in configs/missions.yaml: {unknown}")
    return names


def systems() -> Dict[str, Dict[str, Any]]:
    return load_yaml(paths.SYSTEMS_FILE)


def baseline(name: str) -> Dict[str, Any]:
    path = paths.BASELINES / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"baseline '{name}' not found in configs/baselines/")
    data = load_yaml(path)
    if data.get("system") not in systems():
        raise ValueError(f"baseline '{name}' names unknown system '{data.get('system')}'")
    return data


def baseline_names() -> List[str]:
    return sorted(p.stem for p in paths.BASELINES.glob("*.yaml"))


def host(name: str) -> Dict[str, Any]:
    path = paths.HOSTS / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"host profile '{name}' not found in configs/hosts/")
    return load_yaml(path)
