"""B01 — IMU propagation: why IMU-only odometry drifts, and how fast.

Run from the repo root:  python course/chapters/B01-imu-propagation/run.py
Writes results/run.txt, results/metrics.json and the figures in docs/assets/learn/B01/.
Regions marked [snippet:...] are shown on the chapter page (tools/sync_course.py keeps them in sync).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "course"))
sys.path.insert(0, str(ROOT))

from lvio_course import imu, sim  # noqa: E402

from lvx import plotstyle  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = ROOT / "docs" / "assets" / "learn" / "B01"
CHECKPOINTS = [1.0, 5.0, 10.0, 20.0]  # s


def main() -> dict:
    # [snippet:simulate]
    truth = sim.figure_eight(duration=20.0, rate=200.0)          # 20 s, 200 Hz, analytic ground truth
    dt = truth.t[1] - truth.t[0]
    clean = sim.ImuNoise(gyro_density=0.0, accel_density=0.0)     # a perfect IMU
    noisy = sim.ImuNoise()                                        # MEMS-class white noise only
    gyro_only = sim.ImuNoise(accel_density=0.0)                   # the same, split by sensor
    accel_only = sim.ImuNoise(gyro_density=0.0)
    biased = sim.ImuNoise(gyro_bias=0.001, accel_bias=0.02)       # + small constant biases
    print(f"trajectory: {len(truth.t)} samples, dt = {dt * 1e3:.1f} ms, "
          f"path length {np.linalg.norm(np.diff(truth.p, axis=0), axis=1).sum():.1f} m")
    # [/snippet]

    # [snippet:propagate]
    runs = 200
    results = {}
    cases = {"perfect": clean, "accel noise": accel_only, "gyro noise": gyro_only,
             "white noise": noisy, "noise + bias": biased}
    for name, noise in cases.items():
        gyro, accel = sim.imu_from_truth(truth, noise, seed=1, n_runs=1 if name == "perfect" else runs)
        R, v, p = imu.propagate(truth.R[0], truth.v[0], truth.p[0], gyro, accel, dt)
        if name == "perfect":
            p_perfect = p[0]                                      # same integrator, no sensor error
            err = np.linalg.norm(p - truth.p[None], axis=-1)      # discretisation error only
        else:
            err = np.linalg.norm(p - p_perfect[None], axis=-1)    # error caused by the sensor alone
        results[name] = np.sqrt((err**2).mean(axis=0))            # RMS over Monte Carlo runs
        row = "  ".join(f"{c:>4.0f} s: {results[name][int(c / dt)]:9.4f} m" for c in CHECKPOINTS)
        print(f"{name:>13} | {row}")
    print(f"perfect IMU: largest error over 20 s = {results['perfect'].max() * 100:.2f} cm (discretisation only; "
          "noise rows are measured against this perfect-IMU path)")
    # [/snippet]

    # [snippet:covariance]
    gyro1, accel1 = sim.imu_from_truth(truth, clean, n_runs=1)
    P = imu.propagate_covariance(truth.R, gyro1[0], accel1[0], dt, noisy.gyro_density, noisy.accel_density)
    sigma_pred = np.sqrt(np.trace(P[:, 6:9, 6:9], axis1=1, axis2=2))   # predicted position std (m)
    ratio = results["white noise"][-1] / sigma_pred[-1]
    print(f"at 20 s: Monte Carlo RMS {results['white noise'][-1]:.4f} m, "
          f"covariance predicts {sigma_pred[-1]:.4f} m  (ratio {ratio:.2f})")
    # [/snippet]

    metrics = {
        "dt_s": dt,
        "runs": runs,
        "perfect_imu_max_error_m": float(results["perfect"].max()),
        "rms_position_error_m": {k: {f"{c:g}s": float(v[int(c / dt)]) for c in CHECKPOINTS}
                                 for k, v in results.items()},
        "predicted_sigma_20s_m": float(sigma_pred[-1]),
        "mc_over_predicted_20s": float(ratio),
    }
    figures(truth, results, sigma_pred, dt)
    return metrics


def figures(truth, results, sigma_pred, dt):
    import matplotlib.pyplot as plt

    plotstyle.apply()
    FIG.mkdir(parents=True, exist_ok=True)
    t = truth.t[1:]
    colors = {"perfect": plotstyle.GT, "accel noise": plotstyle.VARIANT_COLORS[3],
              "gyro noise": plotstyle.VARIANT_COLORS[2], "white noise": plotstyle.VARIANT_COLORS[0],
              "noise + bias": plotstyle.VARIANT_COLORS[1]}
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for name, rms in results.items():
        ax.loglog(t, rms[1:], color=colors[name], lw=1.2 if name in ("accel noise", "gyro noise") else 2,
                  ls="-." if name in ("accel noise", "gyro noise") else "-", label=name)
    ax.loglog(t, sigma_pred[1:], color=plotstyle.SYSTEM_COLORS["se3-lvio"], ls="--", lw=1.5,
              label="covariance prediction (white noise)")
    i1 = int(1.0 / dt) - 1
    for name, k, label in (("accel noise", 1.5, "t^1.5"), ("gyro noise", 2.5, "t^2.5"), ("noise + bias", 2.0, "t^2")):
        y = results[name][1:][i1] * (t / 1.0) ** k                # guide through the curve at t = 1 s
        ax.loglog(t, y, color=plotstyle.NOISE_BAND, lw=1, ls=":")
        ax.text(t[-1] * 1.08, y[-1], f"∝ {label}", fontsize=8, color="#495057", va="center", ha="left")
    ax.set_xlabel("time since start (s)")
    ax.set_ylabel("position error, RMS over 200 runs (m)")
    ax.set_title("IMU-only drift grows like a power of time")
    ax.set_xlim(2e-2, 60)
    ax.legend(fontsize=8, loc="upper left")
    fig.savefig(FIG / "drift_vs_time.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.plot(truth.p[:, 0], truth.p[:, 1], color=plotstyle.GT, lw=2, label="ground truth")
    gyro, accel = sim.imu_from_truth(truth, sim.ImuNoise(gyro_bias=0.001, accel_bias=0.02), seed=3, n_runs=6)
    _, _, p = imu.propagate(truth.R[0], truth.v[0], truth.p[0], gyro, accel, dt)
    for i in range(p.shape[0]):
        ax.plot(p[i, :, 0], p[i, :, 1], color=plotstyle.VARIANT_COLORS[1], lw=1, alpha=0.6,
                label="IMU only, noise + bias" if i == 0 else None)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Six IMU-only runs, 20 s")
    ax.legend(fontsize=8, loc="lower left")
    fig.savefig(FIG / "trajectories.png")
    plt.close(fig)


if __name__ == "__main__":
    m = main()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    with open(out / "metrics.json", "w") as f:
        json.dump(m, f, indent=2)
