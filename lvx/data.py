"""Datasets by name: the only way chapters, labs and experiments reach data.

    from lvx.data import dataset
    bag = dataset("sad-ulhk") / "test2.bag"      # resolved from lvx.local.yaml, never a hard-coded path

A missing dataset raises a message with the official download link and the expected location.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from . import config, paths, registry


def _how_to_get(name: str) -> str:
    reg = config.dataset_registry()[name]
    links = []
    if reg.get("source") == "sad_download":
        dl = registry.load_yaml(paths.CONFIGS / "datasets.yaml")["sad_download"]
        links += [f"OneDrive {dl['onedrive']}", f"Baidu {dl['baidu']}"]
    for k in ("huggingface", "official"):
        if reg.get(k):
            links.append(f"{k} {reg[k]}")
    return "; ".join(links) or "see docs/how-to/get-the-data.md"


def dataset(name: str) -> Path:
    """Directory of dataset `name` on this machine; raises a helpful error if it is not there yet."""
    d = config.dataset_dir(name)
    missing = config.dataset_missing(name)
    if missing:
        raise SystemExit(
            f"dataset '{name}' not ready at {d} (missing: {', '.join(missing)}).\n"
            f"  get it: {_how_to_get(name)}\n"
            f"  then place it there, or point lvx at it: lvx init --dataset {name}=<dir>\n"
            f"  details: docs/how-to/get-the-data.md")
    return d


def status() -> List[Dict[str, object]]:
    """One row per registered dataset: where lvx looks, whether it is ready, which chapters/labs use it."""
    rows = []
    for name, reg in config.dataset_registry().items():
        try:
            where = config.dataset_dir(name)
            missing = config.dataset_missing(name)
            state = "ready" if not missing else f"missing {', '.join(missing)}"
        except SystemExit:
            where, state = None, "not configured (run `lvx init`)"
        rows.append({"name": name, "where": where, "state": state, "used_by": reg.get("used_by") or [],
                     "title": reg["title"]})
    return rows
