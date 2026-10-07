#!/usr/bin/env python3
"""Governance: every experiment spec is valid, pre-registered when it should be, and its lifecycle is honest.

Fails (exit 1) on:
  - schema / cross-reference errors in any spec (lvx.spec.validate)
  - status >= approved without spec.lock, or frozen fields edited after freezing (hash mismatch)
  - status >= running without run manifests; >= analysed without runs.csv + summary.json
  - running/analysed/concluded while a depends_on experiment is not concluded (EXP-000 excepted)
  - duplicate ids, a supersedes/superseded_by pointing nowhere
  - an experiment id missing from ROADMAP.md
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lvx import config, spec  # noqa: E402
from lvx.evaluate import results_exist  # noqa: E402

ORDER = {s: i for i, s in enumerate(spec.STATUSES)}


def check() -> list:
    errors = []
    exps = spec.all_experiments()
    by_id = {}
    for e in exps:
        if e.id in by_id:
            errors.append(f"{e.id}: duplicate id ({by_id[e.id].dir.name}, {e.dir.name})")
        by_id[e.id] = e
    roadmap = config.ROADMAP.read_text() if config.ROADMAP.exists() else ""
    for e in exps:
        where = e.dir.name
        errors += [f"{where}: {m}" for m in spec.validate(e)]
        st = e.status
        if st not in ORDER:
            continue
        frozen_needed = st in ("approved", "running", "analysed", "concluded")
        lock = spec.read_lock(e)
        if frozen_needed and lock is None:
            errors.append(f"{where}: status '{st}' requires spec.lock (lvx exp freeze)")
        if lock is not None and lock.get("sha256") != spec.frozen_hash(e.spec):
            errors.append(f"{where}: pre-registered fields changed after freezing (make a superseding experiment)")
        if st in ("analysed", "concluded") and not list((e.results / "manifests").glob("*.json")):
            errors.append(f"{where}: status '{st}' but no run manifests in results/manifests/")
        if st in ("analysed", "concluded") and not results_exist(e):
            errors.append(f"{where}: status '{st}' requires results/runs.csv and results/summary.json")
        if st in ("running", "analysed", "concluded") and e.id != "EXP-000":
            for dep in e.spec.get("depends_on") or []:
                if dep not in by_id:
                    errors.append(f"{where}: depends_on {dep} does not exist")
                elif by_id[dep].status != "concluded":
                    errors.append(f"{where}: is '{st}' but dependency {dep} is '{by_id[dep].status}'")
        for k in ("supersedes", "superseded_by"):
            ref = e.spec.get(k)
            if ref and ref not in by_id:
                errors.append(f"{where}: {k} {ref} does not exist")
        if e.id not in roadmap:
            errors.append(f"{where}: {e.id} is not tracked in ROADMAP.md")
        if (e.results).exists() and st in ("planned", "approved"):
            errors.append(f"{where}: results/ exists while status is '{st}' (results without a running experiment)")
    return errors


def main() -> int:
    errors = check()
    n = len(spec.all_experiments())
    if errors:
        print(f"check_experiments: {len(errors)} problem(s) in {n} experiments")
        for e in errors:
            print("  -", e)
        return 1
    print(f"check_experiments: OK ({n} experiments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
