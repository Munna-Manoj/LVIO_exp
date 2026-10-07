"""The standard figure set of an experiment (CLAUDE.md §5). Output: docs/assets/experiments/<EXP>/."""
from __future__ import annotations

import gzip
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from . import config, plotstyle
from .evaluate import load_summary
from .spec import Experiment

FIGURES = ["effect.png", "pareto.png", "error_time.png", "traj_top.png"]


def _variant_index(exp: Experiment) -> Dict[str, int]:
    return {v: i for i, v in enumerate(exp.variant_ids())}


def effect_plot(exp: Experiment, summary: dict, out: Path) -> None:
    import matplotlib.pyplot as plt

    primary = summary["primary"]
    missions = exp.missions()
    variants = [v for v in exp.variant_ids() if v != "baseline"]
    idx = _variant_index(exp)
    cells = {(c["variant"], c["mission"]): c for c in summary["cells"]}
    fig, ax = plt.subplots(figsize=(1.6 + 1.1 * len(missions), 3.4))
    x = np.arange(len(missions))
    for j, m in enumerate(missions):
        s = cells[("baseline", m)].get("sigma_noise")
        if s:
            ax.add_patch(plt.Rectangle((j - 0.45, -2 * s), 0.9, 4 * s, color=plotstyle.NOISE_BAND, alpha=0.35, lw=0))
    width = 0.8 / max(1, len(variants))
    for k, v in enumerate(variants):
        d = [cells[(v, m)]["delta"] for m in missions]
        d = [np.nan if y is None else y for y in d]
        ax.bar(x - 0.4 + width * (k + 0.5), d, width, color=plotstyle.variant_color(idx[v]), label=v)
    ax.axhline(0, color=plotstyle.GT, lw=0.8)
    ax.set_xticks(x, missions)
    ax.set_ylabel(f"Δ {primary} vs baseline")
    ax.set_title("Effect per mission (grey band = ±2σ run-to-run noise)")
    ax.legend(ncol=min(4, len(variants)), loc="upper left", bbox_to_anchor=(0, -0.12))
    fig.savefig(out / "effect.png")
    plt.close(fig)


def pareto_plot(exp: Experiment, summary: dict, out: Path) -> None:
    import matplotlib.pyplot as plt

    primary = summary["primary"]
    idx = _variant_index(exp)
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for v in exp.variant_ids():
        cs = [c for c in summary["cells"] if c["variant"] == v]
        acc = [c[primary]["mean"] for c in cs if c[primary]["mean"] is not None]
        ms = [c["ms_p95"]["mean"] for c in cs if c.get("ms_p95", {}).get("mean") is not None]
        if acc and ms:
            ax.scatter(np.mean(ms), np.mean(acc), s=60, color=plotstyle.variant_color(idx[v]), label=v, zorder=3)
    for budget, name in ((plotstyle.BUDGET_20HZ_MS, "20 Hz"), (plotstyle.BUDGET_10HZ_MS, "10 Hz")):
        ax.axvline(budget, color=plotstyle.NOISE_BAND, ls="--", lw=1)
        ax.text(budget, ax.get_ylim()[1], f" {name}", va="top", fontsize=8, color="#495057")
    ax.set_xlabel("ms per scan, p95 (mean over missions)")
    ax.set_ylabel(f"{primary} (mean over missions)")
    ax.set_title("Accuracy vs cost (lower-left is better)")
    ax.legend(fontsize=8)
    fig.savefig(out / "pareto.png")
    plt.close(fig)


def _read_tum(path: Path) -> Optional[np.ndarray]:
    if not path.exists():
        return None
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return np.loadtxt(f, comments="#")


def _aligned_error(est: np.ndarray, gt: np.ndarray):
    """Nearest-time pairing + Umeyama rigid alignment (plot only; numbers come from evaluate.py)."""
    t_max = min(np.median(np.diff(gt[:, 0])), np.median(np.diff(est[:, 0]))) / 2 + 0.005
    j = np.clip(np.searchsorted(est[:, 0], gt[:, 0]), 1, len(est) - 1)
    j = np.where(np.abs(est[j - 1, 0] - gt[:, 0]) < np.abs(est[j, 0] - gt[:, 0]), j - 1, j)
    ok = np.abs(est[j, 0] - gt[:, 0]) < min(t_max, 0.05)
    p, q = est[j[ok], 1:4], gt[ok, 1:4]
    mp, mq = p.mean(0), q.mean(0)
    u, _, vt = np.linalg.svd((q - mq).T @ (p - mp))
    s = np.diag([1, 1, np.sign(np.linalg.det(u @ vt))])
    r = u @ s @ vt
    p_al = (r @ (p - mp).T).T + mq
    return gt[ok, 0], p_al, q


def trajectory_plots(exp: Experiment, summary: dict, out: Path) -> None:
    import matplotlib.pyplot as plt

    primary = summary["primary"]
    cells = [c for c in summary["cells"] if c["variant"] != "baseline" and c.get("delta") is not None]
    if not cells:
        return
    worst = max(cells, key=lambda c: abs(c["delta"]))
    m, v = worst["mission"], worst["variant"]
    gt = _read_tum(config.mission_dir(m) / "comfort_offline" / "gt.tum")
    idx = _variant_index(exp)
    tracks = {name: _read_tum(exp.results / "traj" / f"{name}__{m}__r1.tum.gz") for name in ("baseline", v)}
    if gt is None or any(t is None for t in tracks.values()):
        return
    fig_t, ax_t = plt.subplots(figsize=(7, 2.8))
    fig_m, ax_m = plt.subplots(figsize=(5, 5))
    for name, est in tracks.items():
        t, p, q = _aligned_error(est, gt)
        col = plotstyle.variant_color(idx[name])
        ax_t.plot(t - t[0], 100 * np.linalg.norm(p - q, axis=1), color=col, lw=1, label=name)
        ax_m.plot(p[:, 0], p[:, 1], color=col, lw=1, label=name)
    ax_m.plot(q[:, 0], q[:, 1], color=plotstyle.GT, lw=0.8, ls=":", label="GT prism")
    ax_t.set_xlabel("time since start (s)")
    ax_t.set_ylabel("position error (cm)")
    ax_t.set_title(f"Error over time on {m} (largest |Δ{primary}|)")
    ax_t.legend()
    ax_m.set_aspect("equal")
    ax_m.set_xlabel("x (m)")
    ax_m.set_ylabel("y (m)")
    ax_m.set_title(f"Top view, {m}")
    ax_m.legend()
    fig_t.savefig(out / "error_time.png")
    fig_m.savefig(out / "traj_top.png")
    plt.close(fig_t)
    plt.close(fig_m)


def make(exp: Experiment) -> List[Path]:
    summary = load_summary(exp)
    if summary is None:
        raise SystemExit(f"{exp.id}: no summary.json yet, run `lvx eval {exp.id}` first")
    plotstyle.apply()
    out = exp.figures_dir
    out.mkdir(parents=True, exist_ok=True)
    if exp.spec["variants"]:
        effect_plot(exp, summary, out)
    pareto_plot(exp, summary, out)
    trajectory_plots(exp, summary, out)
    return sorted(out.glob("*.png"))
