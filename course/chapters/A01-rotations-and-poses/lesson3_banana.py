"""A01 · Lesson 3, part 2: describe the cloud of end points with ONE bell curve. Two recipes, then the same numbers
used two ways (SO(3)xR3 vs SE(3)), then the knob: how much heading doubt before it matters.

The robots are Eq. 9 with 6-D noise: 1 cm per step in position, 0.5 deg roll and pitch, 6 deg yaw.
"Off the cloud" = farther from every real robot than 99% of the robots are from their nearest neighbour.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

from se3 import drive, propagate_covariance, se3_exp, se3_log
from so3 import so3_exp

RUNS, STEPS = 2000, 10
STEP = np.array([1.0, 0, 0, 0, 0, 0])            # xi = [rho, phi]: 1 m forward, no turn
SIGMA = np.array([0.01, 0.01, 0.01, np.radians(0.5), np.radians(0.5), np.radians(6.0)])   # per step


def separate(T_mean, xi):
    """SO(3)xR3: p <- p + rho and, separately, R <- R Exp(phi). The turn never moves the point."""
    T = np.eye(4)
    T[:3, :3] = T_mean[:3, :3] @ so3_exp(xi[3:])                         # (Eq. 11) left
    T[:3, 3] = T_mean[:3, 3] + xi[:3]                                     # (Eq. 11) left
    return T


def together(T_mean, xi):
    """SE(3): T <- T Exp([rho, phi]). Moving and turning in one Exp: the turn bends the move."""
    return T_mean @ se3_exp(xi)                                           # (Eq. 11) right


def robots(rng, sigma):
    """The truth: RUNS robots driven with noise (Eq. 9); their end poses, and the predicted bell curve (Eq. 10)."""
    T_mean, Sigma = propagate_covariance(STEP, STEPS, sigma)              # (Eq. 10) no samples
    ends = [drive(STEP, rng.normal(size=(STEPS, 6)) * sigma) for _ in range(RUNS)]   # (Eq. 9)
    return ends, T_mean, Sigma


def off_cloud(xy):
    tree = cKDTree(xy)
    reach = np.percentile(tree.query(xy, k=2)[0][:, 1], 99)
    return lambda pts: float(np.mean(tree.query(pts)[0] > reach))


def scene_recipes(out, rng, ends, T_mean, Sigma):
    """The chapter's money plot: recipe A (bell curve in x-y, fitted) vs recipe B (bell curve over xi, predicted)."""
    xy = np.array([T[:2, 3] for T in ends])
    off = off_cloud(xy)
    A = rng.multivariate_normal(xy.mean(0), np.cov(xy.T), RUNS)                     # recipe A: fitted to the truth
    xis = rng.multivariate_normal(np.zeros(6), Sigma, RUNS)                          # recipe B: predicted
    B = np.array([together(T_mean, x)[:2, 3] for x in xis])
    S = np.array([separate(T_mean, x)[:2, 3] for x in xis])                          # the same numbers, SO(3)xR3
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5), sharey=True)
    for ax, pts, c, t in [(axes[0], A, "tab:blue", f"A: a bell curve in x and y (fitted)\n{off(A):.1%} off the cloud"),
                          (axes[1], B, "tab:orange", f"B: a bell curve over ξ, then se3_exp (predicted)\n"
                                                     f"{off(B):.1%} off the cloud")]:
        ax.scatter(*pts.T, s=3, color=c, alpha=0.35, label="the recipe's guesses")
        ax.scatter(*xy.T, s=1, color="black", label=f"{RUNS} real robots")
        ax.set(aspect="equal", xlim=(6.0, 11.0), ylim=(-5, 5), xlabel="x (m)", title=t)
        ax.legend(loc="lower left", markerscale=5)
    axes[0].plot(*xy.mean(0), "x", color="tab:blue", ms=12, mew=2.5)
    axes[0].set_ylabel("y (m)")
    fig.savefig(out / "banana.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5), sharey=True)
    for ax, pts, c, t in [(axes[0], S, "tab:purple", f"SO(3)×R³: p + ρ, then turn on the spot\n{off(S):.1%} off"),
                          (axes[1], B, "tab:orange", f"SE(3): T · se3_exp([ρ, φ])\n{off(B):.1%} off")]:
        ax.scatter(*pts.T, s=3, color=c, alpha=0.35, label="the same 2000 draws of ξ")
        ax.scatter(*xy.T, s=1, color="black", label="real robots")
        ax.set(aspect="equal", xlim=(6.0, 11.0), ylim=(-5, 5), xlabel="x (m)", title=t)
        ax.legend(loc="lower left", markerscale=5)
    axes[0].set_ylabel("y (m)")
    fig.savefig(out / "same_numbers.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    sample = np.cov(np.array([se3_log(np.linalg.inv(T_mean) @ T) for T in ends]).T)   # the truth, as xi
    x = next(x for x in xis if 25 < abs(np.degrees(x[5])) < 35)                      # one draw with a big turn
    return {"off_xy": off(A), "off_se3": off(B), "off_separate": off(S),
            "mean_gap_cm": float(100 * np.min(np.linalg.norm(xy - xy.mean(0), axis=1))),
            "x_std_m": float(xy[:, 0].std()), "y_std_m": float(xy[:, 1].std()), "x_mean_m": float(xy[:, 0].mean()),
            "pred_std": np.sqrt(np.diag(Sigma)).tolist(),
            "trace_ratio": float(np.trace(sample) / np.trace(Sigma)),
            "lateral_ratio": float(sample[1, 1] / Sigma[1, 1]), "along_track_ratio": float(sample[0, 0] / Sigma[0, 0]),
            "example_xi": x.tolist(), "example_separate": separate(T_mean, x)[:2, 3].tolist(),
            "example_together": together(T_mean, x)[:2, 3].tolist()}


def scene_knob(rng):
    """Turn the knob: the yaw noise per step. Below a few degrees of heading doubt the two models agree."""
    rows = {}
    for deg in (0.5, 1.0, 2.0, 6.0, 10.0):
        sigma = SIGMA.copy()
        sigma[5] = np.radians(deg)
        ends, T_mean, Sigma = robots(rng, sigma)
        off = off_cloud(np.array([T[:2, 3] for T in ends]))
        xis = rng.multivariate_normal(np.zeros(6), Sigma, RUNS)
        rows[deg] = {"facing_std_deg": float(deg * np.sqrt(STEPS)),
                     "off_separate": off(np.array([separate(T_mean, x)[:2, 3] for x in xis])),
                     "off_se3": off(np.array([together(T_mean, x)[:2, 3] for x in xis]))}
    return rows
