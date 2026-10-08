"""3D viewer data (ROADMAP M2.2): the map and trajectories of an experiment, for docs/viewer/ and the README.

For every mission of the experiment, from the repeat-1 runs on the host:

  <mission>.bin       the map: the baseline's estimated IMU poses + every 5th Hesai scan, each scan placed with
                      the nearest pose (no per-point deskew: a picture, not a metric), thinned to <= MAX_POINTS.
                      uint16 x, y, z per point; origin and step are in the .json
  <mission>.json      trajectories (GT prism, baseline, each variant) as polylines, GT gaps as breaks
  <mission>_map.png   top view of the same map and trajectories, for GitHub (which can't run three.js)

Everything is in the GT (total-station) frame. Each estimate is moved there by its own rigid fit to GT, the
fit lvx/figures.py plots with; the map gets the baseline's fit. A plot-side alignment: numbers come from
evaluate.py. Written to docs/assets/experiments/<EXP>/viewer/ (lvx sync pulls it with the figures).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from . import config, plotstyle, runner
from .figures import _read_tum
from .spec import Experiment

MAX_POINTS = 300_000      # 6 bytes each: <= 1.8 MB per mission, under check_tree's 2 MB without Git LFS
SCAN_STRIDE = 5           # every 5th scan (2 Hz) is plenty for a map
RANGE_M = (1.0, 40.0)     # drop the robot itself and far, sparse returns
TRACK_DT_S = 0.2          # trajectory polylines sampled every 0.2 s
GT_GAP_S = 1.0            # the total station lost the prism: break the GT line
XT32 = np.dtype({"names": ["x", "y", "z", "intensity", "ring", "timestamp"],
                 "formats": ["<f4", "<f4", "<f4", "<f4", "<u2", "<f8"],
                 "offsets": [0, 4, 8, 12, 16, 18], "itemsize": 26})   # comfort_offline/lidar/*.bin (Hesai XT32)


def rigid_fit(est: np.ndarray, gt: np.ndarray):
    """R, t moving estimate positions onto GT: nearest-time pairs within the ADR-0002 window, then Umeyama."""
    t_max = min(min(np.median(np.diff(gt[:, 0])), np.median(np.diff(est[:, 0]))) / 2 + 0.005, 0.05)
    j = np.clip(np.searchsorted(est[:, 0], gt[:, 0]), 1, len(est) - 1)
    j = np.where(np.abs(est[j - 1, 0] - gt[:, 0]) < np.abs(est[j, 0] - gt[:, 0]), j - 1, j)
    ok = np.abs(est[j, 0] - gt[:, 0]) < t_max
    p, q = est[j[ok], 1:4], gt[ok, 1:4]
    mp, mq = p.mean(0), q.mean(0)
    u, _, vt = np.linalg.svd((q - mq).T @ (p - mp))
    R = u @ np.diag([1, 1, np.sign(np.linalg.det(u @ vt))]) @ vt
    return R, mq - R @ mp


def quat_to_R(q: np.ndarray) -> np.ndarray:
    """TUM quaternions (qx, qy, qz, qw), shape (N, 4) -> rotation matrices (N, 3, 3)."""
    x, y, z, w = (q / np.linalg.norm(q, axis=1, keepdims=True)).T
    return np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
                     2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
                     2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)], 1).reshape(-1, 3, 3)


def voxel(p: np.ndarray, size: float) -> np.ndarray:
    _, i = np.unique(np.floor(p / size).astype(np.int64), axis=0, return_index=True)
    return p[i]


def build_map(poses: np.ndarray, offline: Path) -> np.ndarray:
    """World points from IMU-frame poses (TUM) and the mission's Hesai scans. Each scan's points take the pose
    of the nearest estimate in time (10 Hz poses; within a scan the robot moves < 5 cm)."""
    T_il = np.array(json.loads((offline / "calib.json").read_text())["T_imu_lidar"])
    R_all, t = quat_to_R(poses[:, 4:8]), poses[:, 0]
    chunks = []
    for f in sorted((offline / "lidar").glob("*.bin"))[::SCAN_STRIDE]:
        a = np.fromfile(f, dtype=XT32)
        p = np.stack([a["x"], a["y"], a["z"]], 1).astype(np.float64)
        r = np.linalg.norm(p, axis=1)
        p = p[(r > RANGE_M[0]) & (r < RANGE_M[1])]
        k = int(np.argmin(np.abs(t - int(f.stem) / 1e9)))
        if abs(t[k] - int(f.stem) / 1e9) > 0.06 or len(p) < 100:
            continue                                                      # no pose for this scan
        p_imu = p @ T_il[:3, :3].T + T_il[:3, 3]
        chunks.append(voxel(p_imu @ R_all[k].T + poses[k, 1:4], 0.05))
    return np.concatenate(chunks)


def thin(points: np.ndarray, budget: int = MAX_POINTS) -> np.ndarray:
    size = 0.08
    out = voxel(points, size)
    while len(out) > budget:
        size *= 1.2
        out = voxel(points, size)
    return out


def polyline(xyz: np.ndarray, t: np.ndarray, gap_s: Optional[float] = None) -> List[Optional[List[float]]]:
    """Every TRACK_DT_S, rounded to 1 cm; None where the source has a gap (GT lost the prism)."""
    out: List[Optional[List[float]]] = []
    last = -1e18
    for i in range(len(t)):
        if gap_s is not None and i and t[i] - t[i - 1] > gap_s:
            out.append(None)
        if t[i] - last >= TRACK_DT_S - 1e-6:                       # tolerance: 0.1 s steps sum to 0.19999…
            out.append([round(float(v), 2) for v in xyz[i]])
            last = t[i]
    return out


def mission_data(exp: Experiment, mission: str) -> Dict:
    gt = _read_tum(config.mission_dir(mission) / "comfort_offline" / "gt.tum")
    if gt is None:
        raise SystemExit(f"{mission}: no gt.tum, the viewer needs GT to place the map")
    variants = exp.variant_ids()
    systems = {v: runner.resolve_config(exp, v)["system"] for v in variants}
    tracks, colours = {"GT prism": polyline(gt[:, 1:4], gt[:, 0], GT_GAP_S)}, {"GT prism": plotstyle.GT}
    fit = {}
    for i, v in enumerate(variants):
        est = _read_tum(runner.run_dir(exp, runner.RunKey(v, mission, 1)) / "estimate.tum")
        if est is None:
            continue
        R, tr = rigid_fit(est, gt)
        fit[v] = (R, tr)
        tracks[v] = polyline(est[:, 1:4] @ R.T + tr, est[:, 0])
        colours[v] = plotstyle.variant_color(i, systems[v])
    base = runner.run_dir(exp, runner.RunKey("baseline", mission, 1))
    imu = next(iter(sorted(base.glob("*_imu.tum"))), None)
    if imu is None or "baseline" not in fit:
        raise SystemExit(f"{mission}: the baseline r1 run has no IMU-frame estimate (*_imu.tum) to build the map")
    R, tr = fit["baseline"]                    # prism and IMU estimates share one world frame: one fit for both
    pts = thin(build_map(np.loadtxt(imu), config.mission_dir(mission) / "comfort_offline") @ R.T + tr)
    return {"points": pts, "tracks": tracks, "colours": colours, "systems": systems}


def write(exp: Experiment, mission: str, out: Path) -> List[Path]:
    import matplotlib.pyplot as plt

    d = mission_data(exp, mission)
    pts = d["points"]
    lo, hi = pts.min(0), pts.max(0)
    step = float(max((hi - lo).max() / 65535, 0.001))
    (out / f"{mission}.bin").write_bytes(np.round((pts - lo) / step).astype("<u2").tobytes())
    meta = {"experiment": exp.id, "mission": mission, "frame": "GT prism (total station)", "n_points": len(pts),
            "origin": [round(float(v), 4) for v in lo], "step": step, "colours": d["colours"],
            "tracks": d["tracks"], "baseline": exp.spec["baseline"]}
    (out / f"{mission}.json").write_text(json.dumps(meta, separators=(",", ":")))
    plotstyle.apply()
    fig, ax = plt.subplots(figsize=(7, 7))
    gt_z = np.array([q[2] for q in d["tracks"]["GT prism"] if q is not None])
    band = pts[(pts[:, 2] > gt_z.min() - 0.6) & (pts[:, 2] < gt_z.max() + 1.5)]   # walls: no floor, no ceiling
    z = band[:, 2]
    ax.scatter(band[:, 0], band[:, 1], c=z, s=0.2, cmap="turbo", vmin=np.percentile(z, 2),
               vmax=np.percentile(z, 98), rasterized=True, linewidths=0)
    (x0, y0), (x1, y1) = np.percentile(band[:, :2], 0.5, axis=0), np.percentile(band[:, :2], 99.5, axis=0)
    pad = 0.05 * max(x1 - x0, y1 - y0)
    ax.set(xlim=(x0 - pad, x1 + pad), ylim=(y0 - pad, y1 + pad))
    for name, line in d["tracks"].items():
        segs, cur = [], []
        for p in line + [None]:
            if p is None:
                segs.append(cur)
                cur = []
            else:
                cur.append(p)
        for i, s in enumerate(x for x in segs if len(x) > 1):
            s = np.array(s)
            ax.plot(s[:, 0], s[:, 1], color=d["colours"][name], lw=1.6 if name == "GT prism" else 1.0,
                    label=name if i == 0 else None)
    ax.set(aspect="equal", xlabel="x (m)", ylabel="y (m)",
           title=f"{exp.id} · {mission}: map (path height −0.6 to +1.5 m) and trajectories")
    ax.grid(False)
    ax.legend(loc="best", fontsize=8)
    fig.savefig(out / f"{mission}_map.png", dpi=130)
    plt.close(fig)
    return [out / f"{mission}{s}" for s in (".bin", ".json", "_map.png")]


def make(exp: Experiment, missions: Optional[List[str]] = None) -> List[Path]:
    out = exp.figures_dir / "viewer"
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for m in missions or exp.missions():
        files += write(exp, m, out)
    done = sorted(f.stem for f in out.glob("*.json") if f.stem != "index")
    report = f"../experiments/{exp.report_path.stem}/"                          # the site URL of the report page
    (out / "index.json").write_text(json.dumps({"experiment": exp.id, "title": exp.spec["title"], "missions": done,
                                                "report": report}))
    return files + [out / "index.json"]


def hero_gif(exp: Experiment, mission: str, frames: int = 36, budget_pts: int = 60_000) -> Path:
    """A slowly turning 3D view of one mission's map and trajectories (README, ROADMAP M2.3), from the viewer
    files already written for it; <= 2 MB so it is tracked without Git LFS."""
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    out = exp.figures_dir / "viewer"
    meta = json.loads((out / f"{mission}.json").read_text())
    raw = np.frombuffer((out / f"{mission}.bin").read_bytes(), dtype="<u2").reshape(-1, 3)
    pts = np.array(meta["origin"]) + raw * meta["step"]
    gt_z = np.array([q[2] for q in meta["tracks"]["GT prism"] if q is not None])
    pts = pts[pts[:, 2] < gt_z.max() + 1.5]                                   # no ceiling
    pts = pts[np.random.default_rng(0).permutation(len(pts))[:budget_pts]]
    plotstyle.apply()
    fig = plt.figure(figsize=(8.0, 4.5), facecolor="#0d1117")
    ax = fig.add_subplot(projection="3d", facecolor="#0d1117", computed_zorder=False)   # trajectories on top
    z = pts[:, 2]
    ax.scatter(*pts.T, c=z, cmap="turbo", s=0.8, alpha=0.8, vmin=np.percentile(z, 2), vmax=np.percentile(z, 98),
               linewidths=0, depthshade=False)
    for name, line in meta["tracks"].items():
        seg = np.array([p if p is not None else [np.nan] * 3 for p in line], float)
        ax.plot(*seg.T, color="#ffffff" if name == "GT prism" else meta["colours"][name],
                lw=2.6 if name == "GT prism" else 1.6, zorder=5)
    lo, hi = np.percentile(pts, 1, axis=0), np.percentile(pts, 99, axis=0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set(xlim=(c[0] - r, c[0] + r), ylim=(c[1] - r, c[1] + r), zlim=(c[2] - r / 2, c[2] + r / 2))
    ax.set_box_aspect((1, 1, 0.5), zoom=1.5)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.text(0.02, 0.94, f"{exp.id} · {mission}: map from the estimate; white = GT prism", color="#e6edf3",
             fontsize=10)
    anim = FuncAnimation(fig, lambda k: ax.view_init(elev=35, azim=-60 + 360 * k / frames), frames=frames)
    path = out / f"{mission}.gif"
    anim.save(path, writer=PillowWriter(fps=10), dpi=80, savefig_kwargs={"facecolor": "#0d1117"})
    plt.close(fig)
    return path
