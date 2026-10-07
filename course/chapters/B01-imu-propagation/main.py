"""B01 · IMU-only odometry: how fast does it drift, and can we predict it?

Run it from this folder:   python main.py      (about 30 s, no dataset)
It prints the table in README.md and writes everything to results/.
"""
import json
from pathlib import Path

import matplotlib
import numpy as np

from propagate import propagate, propagate_covariance
from simulate import add_imu_errors, figure_eight, imu_readings

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).parent / "results"
RUNS = 50                           # Monte Carlo runs per case
CHECKPOINTS = [0.1, 1.0, 5.0, 10.0, 20.0]  # s
GYRO_NOISE = 2.4e-4                 # rad/s/sqrt(Hz)  - a typical MEMS IMU (BMI088 class)
ACCEL_NOISE = 1.7e-3                # m/s^2/sqrt(Hz)
GYRO_BIAS, ACCEL_BIAS = 0.001, 0.02  # rad/s, m/s^2   - small, uncorrected biases
lines = []


def say(text):
    print(text)
    lines.append(text)


# 1. The truth: a 20 s figure-eight, sampled at 200 Hz -------------------------------------------
t, p_true, v_true, a_true, R_true = figure_eight(duration=20.0, rate=200.0)
dt = t[1] - t[0]
say(f"trajectory: {len(t)} samples, dt = {dt * 1e3:.1f} ms, "
    f"path length {np.linalg.norm(np.diff(p_true, axis=0), axis=1).sum():.1f} m")

# 2. A perfect IMU: the only error left is the integrator's own step error -----------------------
gyro_perfect, accel_perfect = imu_readings(t, a_true, R_true)
R_perfect, _, p_perfect = propagate(R_true[0], v_true[0], p_true[0], gyro_perfect, accel_perfect, dt)
step_error = np.linalg.norm(p_perfect - p_true, axis=1)

# 3. Noisy IMUs: 50 runs per case, each measured against the perfect-IMU path ---------------------
#    (so the numbers show what the sensor alone costs)
cases = {
    "accel noise": dict(accel_noise=ACCEL_NOISE),
    "gyro noise": dict(gyro_noise=GYRO_NOISE),
    "white noise": dict(gyro_noise=GYRO_NOISE, accel_noise=ACCEL_NOISE),
    "noise + bias": dict(gyro_noise=GYRO_NOISE, accel_noise=ACCEL_NOISE, gyro_bias=GYRO_BIAS, accel_bias=ACCEL_BIAS),
}
rms_error, paths = {}, {}
rng = np.random.default_rng(1)
for name, sensor in cases.items():
    errors, paths[name] = [], []
    for run in range(RUNS):
        gyro, accel = add_imu_errors(gyro_perfect, accel_perfect, dt, rng, **sensor)
        _, _, p = propagate(R_true[0], v_true[0], p_true[0], gyro, accel, dt)
        errors.append(np.linalg.norm(p - p_perfect, axis=1))
        paths[name].append(p)
    rms_error[name] = np.sqrt(np.mean(np.square(errors), axis=0))    # RMS over the runs, at every time step

say(f"{'':>13} | " + "  ".join(f"{c:>8g} s" for c in CHECKPOINTS))
for name, e in rms_error.items():
    say(f"{name:>13} | " + "  ".join(f"{e[int(c / dt)]:8.4f} m" for c in CHECKPOINTS))
say(f"perfect IMU: largest step error over 20 s = {step_error.max() * 100:.2f} cm")
crossover = t[np.argmax(rms_error["gyro noise"] > rms_error["accel noise"])]
say(f"gyro noise overtakes accel noise after {crossover:.1f} s")

# 4. Predict the white-noise error with the covariance - no random numbers at all -------------------
P = propagate_covariance(R_perfect, gyro_perfect, accel_perfect, dt, GYRO_NOISE, ACCEL_NOISE)
sigma_p = np.sqrt(np.trace(P[:, 6:9, 6:9], axis1=1, axis2=2))          # predicted position error (m)
ratio = rms_error["white noise"][-1] / sigma_p[-1]
say(f"at 20 s: Monte Carlo {rms_error['white noise'][-1]:.4f} m, covariance predicts {sigma_p[-1]:.4f} m "
    f"(ratio {ratio:.2f})")

# 5. Figures ------------------------------------------------------------------------------------
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3, "font.size": 9})
color = {"accel noise": "#2b8a3e", "gyro noise": "#e8590c", "white noise": "#1971c2", "noise + bias": "#c92a2a"}

# 5a. The whole story in one 3D picture: the true figure-eight and 30 IMU-only runs fanning out.
fig = plt.figure(figsize=(7.5, 5.0))
ax = fig.add_subplot(projection="3d")
for p in paths["noise + bias"][:30]:
    ax.plot(p[:, 0], p[:, 1], p[:, 2], color=color["noise + bias"], lw=0.7, alpha=0.45)
ax.plot(p_true[:, 0], p_true[:, 1], p_true[:, 2], color="black", lw=2.5, label="truth (two laps)")
ax.plot([], [], color=color["noise + bias"], label="30 IMU-only runs, noise + bias")
ax.scatter(*p_true[0], color="black", s=30)
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_zlabel("z (m)")
ax.set_title("Same start, same motion, different IMU noise: 20 s later they are metres apart")
ax.legend(loc="upper left")
fig.savefig(OUT / "drift_3d.png", bbox_inches="tight")
plt.close(fig)

# 5b. The covariance knows how wrong the IMU will be: endpoints of all runs vs the predicted 3-sigma ellipse.
fig, ax = plt.subplots(figsize=(6.0, 4.6))
ax.plot(p_true[:, 0], p_true[:, 1], color="black", lw=2, label="truth")
for c, mark in ((10.0, "o"), (20.0, "s")):
    k = int(c / dt)
    ends = np.array([p[k] for p in paths["white noise"]])
    ax.scatter(ends[:, 0], ends[:, 1], s=8, marker=mark, color=color["white noise"], alpha=0.6,
               label=f"{RUNS} runs at {c:.0f} s")
    vals, vecs = np.linalg.eigh(P[k, 6:8, 6:8])                       # x-y block of the position covariance
    ang = np.linspace(0, 2 * np.pi, 100)
    ellipse = p_perfect[k, :2, None] + vecs @ (3 * np.sqrt(vals)[:, None] * np.array([np.cos(ang), np.sin(ang)]))
    ax.plot(ellipse[0], ellipse[1], color="#343a40", ls="--", lw=1.3, label="predicted 3σ" if c == 10.0 else None)
ax.set_aspect("equal")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_title("The covariance predicts the spread without a single random number")
ax.legend(fontsize=7, loc="lower left")
fig.savefig(OUT / "covariance_ellipses.png", bbox_inches="tight")
plt.close(fig)

# 5c. How fast: error vs time on log-log axes, where a power law is a straight line.
fig, ax = plt.subplots(figsize=(6.2, 4.0))
for name, e in rms_error.items():
    ax.loglog(t[1:], e[1:], color=color[name], lw=2, label=name)
ax.loglog(t[1:], sigma_p[1:], color="black", ls="--", lw=1.2, label="covariance prediction (white noise)")
k1 = int(1.0 / dt)
for name, power in (("accel noise", 1.5), ("gyro noise", 2.5), ("noise + bias", 2.0)):
    guide = rms_error[name][k1] * (t[1:] / 1.0) ** power                # a line of slope `power` through t = 1 s
    ax.loglog(t[1:], guide, color="#adb5bd", lw=1, ls=":")
    ax.text(t[-1] * 1.08, guide[-1], f"$\\propto t^{{{power}}}$", fontsize=8, va="center")
ax.set_xlim(2e-2, 60)
ax.set_xlabel("time since start (s)")
ax.set_ylabel(f"position error, RMS over {RUNS} runs (m)")
ax.set_title("IMU-only drift grows like a power of time")
ax.legend(fontsize=7, loc="upper left")
fig.savefig(OUT / "drift_vs_time.png", bbox_inches="tight")
plt.close(fig)

# 6. Save what was printed (README.md quotes it) and the numbers the tests check -------------------
(OUT / "output.txt").write_text("\n".join(lines) + "\n")
metrics = {name: {f"{c:g}s": float(e[int(c / dt)]) for c in CHECKPOINTS} for name, e in rms_error.items()}
metrics.update(step_error_max_m=float(step_error.max()), gyro_overtakes_accel_s=float(crossover),
               predicted_20s_m=float(sigma_p[-1]), mc_over_predicted=ratio)
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
