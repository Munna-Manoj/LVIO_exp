"""A01 · Lesson 3, part 3: what the bell curve is FOR. A filter stores "where I might be" so it can combine it with
the next measurement. Here one measurement arrives: a wall tells the robot its sideways position y (± 5 cm).

Combining a bell curve with a measurement is a small least-squares problem (Eq. 12), solved by Gauss-Newton:
the same kind of optimisation a LiDAR filter runs on every scan. Each bell curve gives a different answer for x.
"""
import matplotlib.pyplot as plt
import numpy as np

from lesson3_banana import separate, together

SIGMA_Y = 0.05                                      # the measurement's std, m


def gauss_newton(T_mean, Sigma, apply, y_meas, iters=8):
    """Minimise cost(xi) = xi^T Sigma^-1 xi + ((y(xi) - y_meas) / SIGMA_Y)^2, from xi = 0 (the mean pose).

    apply(T_mean, xi) is one of the two ways of Eq. 11; y(xi) is the sideways position it gives.
    Returns the estimate's position and every iteration (cost, x, y), so the steps can be printed.
    """
    L = np.linalg.cholesky(np.linalg.inv(Sigma)).T     # L^T L = Sigma^-1, so |L xi|^2 is the prior cost

    def residual(xi):
        return np.r_[L @ xi, (apply(T_mean, xi)[1, 3] - y_meas) / SIGMA_Y]   # (Eq. 12) the two residuals

    xi = np.zeros(6)
    steps = [(float(residual(xi) @ residual(xi)), *apply(T_mean, xi)[:2, 3].tolist())]   # iteration 0: the mean
    for _ in range(iters):
        r = residual(xi)
        J = np.zeros((7, 6))
        for i in range(6):                              # by finite differences: what a nudge of xi does to r
            d = np.zeros(6)
            d[i] = 1e-6
            J[:, i] = (residual(xi + d) - r) / 1e-6
        xi = xi - np.linalg.lstsq(J, r, rcond=None)[0]                   # (Eq. 12) one Gauss-Newton step
        steps.append((float(residual(xi) @ residual(xi)), *apply(T_mean, xi)[:2, 3].tolist()))
    return apply(T_mean, xi)[:2, 3], xi, steps


def xy_bell_curve(xy, y_meas):
    """Recipe A with the same measurement: condition the x-y bell curve on y (linear, so one step is exact)."""
    m, C = xy.mean(0), np.cov(xy.T)
    return m[0] + C[0, 1] / (C[1, 1] + SIGMA_Y**2) * (y_meas - m[1])


def scene_fuse(out, ends, T_mean, Sigma, y_meas=-2.7):
    """The truth (robots near the measured y), and the three answers; then the knob over y_meas."""
    xy = np.array([T[:2, 3] for T in ends])
    rows = {}
    for ym in (-0.5, -1.5, -2.7, -3.5):
        near = np.abs(xy[:, 1] - ym) < 3 * SIGMA_Y
        rows[ym] = {"robots": int(near.sum()), "true_x": float(xy[near, 0].mean()),
                    "se3_x": float(gauss_newton(T_mean, Sigma, together, ym)[0][0]),
                    "separate_x": float(gauss_newton(T_mean, Sigma, separate, ym)[0][0]),
                    "xy_x": float(xy_bell_curve(xy, ym))}
    p_se3, xi, steps = gauss_newton(T_mean, Sigma, together, y_meas)
    p_sep = gauss_newton(T_mean, Sigma, separate, y_meas)[0]
    x_xy = xy_bell_curve(xy, y_meas)
    near = np.abs(xy[:, 1] - y_meas) < 3 * SIGMA_Y
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.scatter(*xy.T, s=1, color="0.6", label="2000 real robots")
    ax.axhspan(y_meas - SIGMA_Y, y_meas + SIGMA_Y, color="tab:green", alpha=0.25,
               label=f"the measurement: y = {y_meas} ± {SIGMA_Y} m")
    ax.scatter(*xy[near].T, s=8, color="black", label="robots that really are there", zorder=3)
    for x, c, name in [(x_xy, "tab:blue", "x–y bell curve"), (p_sep[0], "tab:purple", "SO(3)×R³"),
                       (p_se3[0], "tab:orange", "SE(3)")]:
        ax.plot(x, y_meas, "o", ms=12, mfc="none", mew=3, color=c, label=f"{name}: x = {x:.2f} m", zorder=4)
    ax.set(aspect="equal", xlim=(8.0, 10.6), ylim=(-4.0, 0.5), xlabel="x (m)", ylabel="y (m)",
           title="One measurement of y arrives. Where is the robot in x?")
    ax.legend(loc="upper left", fontsize=9)
    fig.savefig(out / "fuse.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return {"y_meas": y_meas, "true_x": float(xy[near, 0].mean()), "robots_near": int(near.sum()),
            "se3_x": float(p_se3[0]), "separate_x": float(p_sep[0]), "xy_x": float(x_xy),
            "se3_yaw_deg": float(np.degrees(xi[5])),
            "true_yaw_deg": float(np.degrees(np.mean([np.arctan2(T[1, 0], T[0, 0]) for T, n in zip(ends, near)
                                                       if n]))),
            "steps": steps[:4], "knob": rows}
