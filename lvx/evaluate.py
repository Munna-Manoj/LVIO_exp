"""Evaluation: one protocol for every system (ADR-0002), then the noise-floor verdict (ADR-0004).

ATE follows the COMFORT/Codabench scorer: evo point_distance APE, rigid alignment without scale,
pairing with t_max = min(GT dt, est dt)/2 + 5 ms capped at 50 ms. Results are written to
experiments/<EXP>/results/runs.csv and summary.json. Nothing else may write those files.
"""
from __future__ import annotations

import csv
import datetime as _dt
import gzip
import json
import math
import shutil
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Dict, List, Optional

import numpy as np

from . import course, runner
from .spec import Experiment, all_experiments, set_status

RUN_COLUMNS = [
    "run_id", "variant", "mission", "repeat", "status", "ate_rmse_cm", "ate_median_cm", "ate_max_cm",
    "n_pair", "n_gt", "pair_ratio", "ms_mean", "ms_p95", "ms_max", "rss_mb", "inliers_mean", "wall_s",
    "config_hash", "repo_commit", "system_commit", "host",
]
NOISE_K = 2.0          # an effect must exceed NOISE_K * sigma_noise (ADR-0004)
NOISE_EXPERIMENT = "EXP-000"
SIGMA_MIN_CM = 0.005   # floor when runs are (near) deterministic (ADR-0004)


def t_max_rule(t_ref: np.ndarray, t_est: np.ndarray) -> float:
    dt = min(float(np.median(np.diff(t_ref))), float(np.median(np.diff(t_est))))
    return min(dt / 2 + 0.005, 0.05)


def ate(est_tum: Path, gt_tum: Path) -> Dict[str, float]:
    from evo.core import sync
    from evo.core.metrics import PoseRelation
    from evo.main_ape import ape
    from evo.tools import file_interface

    ref = file_interface.read_tum_trajectory_file(str(gt_tum))
    est = file_interface.read_tum_trajectory_file(str(est_tum))
    n_gt = ref.num_poses
    ref, est = sync.associate_trajectories(ref, est, t_max_rule(ref.timestamps, est.timestamps))
    if ref.num_poses < 10:
        return {"n_pair": ref.num_poses, "n_gt": n_gt}
    s = ape(ref, est, PoseRelation.point_distance, align=True, correct_scale=False, n_to_align=-1,
            align_origin=False).stats
    return {"ate_rmse_cm": 100 * s["rmse"], "ate_median_cm": 100 * s["median"], "ate_max_cm": 100 * s["max"],
            "n_pair": ref.num_poses, "n_gt": n_gt, "pair_ratio": ref.num_poses / n_gt}


def timing(csv_path: Path) -> Dict[str, float]:
    """timing.csv columns: stamp, ms, rss_mb [, leaf_m, inliers]. Same columns for both systems."""
    if not csv_path.exists():
        return {}
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {}
    ms = np.array([float(r["ms"]) for r in rows])
    out = {"ms_mean": float(ms.mean()), "ms_p95": float(np.percentile(ms, 95)), "ms_max": float(ms.max()),
           "rss_mb": max(float(r["rss_mb"]) for r in rows)}
    if "inliers" in rows[0]:
        inl = [float(r["inliers"]) for r in rows if float(r["inliers"]) > 0]
        if inl:
            out["inliers_mean"] = float(mean(inl))
    return out


def evaluate_run(exp: Experiment, key: runner.RunKey) -> Dict[str, Any]:
    out = runner.run_dir(exp, key)
    row: Dict[str, Any] = {"run_id": key.run_id, "variant": key.variant, "mission": key.mission,
                           "repeat": key.repeat}
    mpath = out / "manifest.json"
    if not mpath.exists():
        row["status"] = "missing"
        return row
    with open(mpath) as f:
        man = json.load(f)
    row.update(status=man["status"], wall_s=man.get("wall_s"), config_hash=man["config"]["config_hash"],
               repo_commit=man["repo"]["commit"][:10], system_commit=str(man["system_git"]["commit"])[:10],
               host=man["host"])
    gt = runner.mission_dir(key.mission) / "comfort_offline" / "gt.tum"
    if man["status"] == "ok" and gt.exists():
        row.update(ate(out / "estimate.tum", gt))
        if "ate_rmse_cm" not in row:
            row["status"] = "failed"
    row.update(timing(out / "timing.csv"))
    return row


def write_runs(exp: Experiment, rows: List[Dict[str, Any]]) -> None:
    exp.results.mkdir(parents=True, exist_ok=True)
    with open(exp.results / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RUN_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k in RUN_COLUMNS})


def read_runs(exp: Experiment) -> List[Dict[str, Any]]:
    path = exp.results / "runs.csv"
    if not path.exists():
        return []
    with open(path) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in RUN_COLUMNS:
            if r.get(k) not in (None, "") and k not in ("run_id", "variant", "mission", "status", "config_hash",
                                                        "repo_commit", "system_commit", "host"):
                r[k] = float(r[k])
    return rows


def copy_artifacts(exp: Experiment, keys: List[runner.RunKey]) -> None:
    """Keep repeat 1 of each (variant, mission) in git: manifest + gzipped estimate. Everything else stays
    in run_root. Tracked manifests drop the command line and are scrubbed of machine paths."""
    for key in keys:
        src = runner.run_dir(exp, key)
        man_dir = exp.results / "manifests"
        man_dir.mkdir(parents=True, exist_ok=True)
        if (src / "manifest.json").exists():
            with open(src / "manifest.json") as f:
                man = json.load(f)
            man.pop("command", None)                                  # holds machine paths; stays in run_root
            with open(man_dir / f"{key.run_id}.json", "w") as f:
                f.write(course.scrub(json.dumps(man, indent=2)))
        if key.repeat == 1 and (src / "estimate.tum").exists():
            (exp.results / "traj").mkdir(exist_ok=True)
            dst = exp.results / "traj" / f"{key.run_id}.tum.gz"
            with open(src / "estimate.tum", "rb") as fi, gzip.open(dst, "wb") as fo:
                shutil.copyfileobj(fi, fo)


# --- aggregation + noise floor ----------------------------------------------------------------

def noise_sigma(system_baseline: str) -> Dict[str, float]:
    """Per-mission run-to-run std of ATE for a baseline config, from EXP-000's summary."""
    for e in all_experiments():
        if e.id == NOISE_EXPERIMENT and (e.results / "summary.json").exists():
            with open(e.results / "summary.json") as f:
                s = json.load(f)
            return s.get("noise_floor", {}).get(system_baseline, {})
    return {}


def _stats(values: List[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"mean": None, "std": None, "median": None}
    return {"mean": mean(values), "std": pstdev(values) if len(values) > 1 else 0.0, "median": median(values)}


def summarise(exp: Experiment, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    primary = exp.spec["metrics"]["primary"]
    metrics = [primary] + list(exp.spec["metrics"].get("secondary") or [])
    for m in ("ate_rmse_cm", "ms_p95"):
        if m not in metrics:
            metrics.append(m)
    variants, missions = exp.variant_ids(), exp.missions()
    cells = []
    for v in variants:
        for m in missions:
            rs = [r for r in rows if r["variant"] == v and r["mission"] == m]
            ok = [r for r in rs if r["status"] == "ok"]
            cell: Dict[str, Any] = {"variant": v, "mission": m, "n_ok": len(ok),
                                    "n_failed": sum(r["status"] == "failed" for r in rs),
                                    "n_dirty": sum(r["status"] == "dirty" for r in rs),
                                    "n_missing": exp.spec["repeats"] - len(ok) - sum(r["status"] in ("failed", "dirty")
                                                                                     for r in rs)}
            for k in metrics:
                cell[k] = _stats([float(r[k]) for r in ok if r.get(k) not in (None, "")])
            cells.append(cell)

    sigma = noise_sigma(exp.spec["baseline"])
    if exp.id == NOISE_EXPERIMENT:
        sigma = {}
    by = {(c["variant"], c["mission"]): c for c in cells}
    for c in cells:
        base = by[("baseline", c["mission"])][primary]["mean"]
        val = c[primary]["mean"]
        s = sigma.get(c["mission"])
        s = None if s is None else max(s, SIGMA_MIN_CM)
        c["delta"] = None if base is None or val is None else val - base
        if c["variant"] == "baseline" or c["delta"] is None:
            c["effect"] = None
        elif s is None:
            c["effect"] = "no-noise-floor"
        elif abs(c["delta"]) <= NOISE_K * s:
            c["effect"] = "none"
        else:
            c["effect"] = "better" if c["delta"] < 0 else "worse"
        c["sigma_noise"] = s

    summary: Dict[str, Any] = {
        "experiment": exp.id,
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "primary": primary,
        "noise_k": NOISE_K,
        "noise_source": None if exp.id == NOISE_EXPERIMENT else NOISE_EXPERIMENT,
        "complete": all(c["n_ok"] + c["n_failed"] + c["n_dirty"] >= exp.spec["repeats"] for c in cells),
        "cells": cells,
    }
    if exp.id == NOISE_EXPERIMENT:
        floor: Dict[str, Dict[str, float]] = {}
        for c in cells:
            name = exp.spec["baseline"] if c["variant"] == "baseline" else next(
                v.get("baseline") for v in exp.spec["variants"] if v["id"] == c["variant"])
            if c["ate_rmse_cm"]["std"] is not None:
                floor.setdefault(name, {})[c["mission"]] = c["ate_rmse_cm"]["std"]
        summary["noise_floor"] = floor
    return summary


def evaluate(exp: Experiment) -> Dict[str, Any]:
    keys = runner.plan(exp)
    rows = [evaluate_run(exp, k) for k in keys]
    write_runs(exp, rows)
    copy_artifacts(exp, keys)
    summary = summarise(exp, read_runs(exp))
    with open(exp.results / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x)
    if summary["complete"] and exp.status == "running":
        set_status(exp, "analysed")
    return summary


def load_summary(exp: Experiment) -> Optional[Dict[str, Any]]:
    path = exp.results / "summary.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def results_exist(exp: Experiment) -> bool:
    return (exp.results / "runs.csv").exists() and (exp.results / "summary.json").exists()

