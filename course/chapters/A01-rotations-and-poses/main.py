"""A01 · Run the three scenes: a box turned on its own side vs the world's, the right Jacobian, and the banana.

python main.py      # about 10 s; prints the table in the README, writes results/
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from se3 import drive, propagate_covariance, se3_exp, se3_log  # noqa: E402
from so3 import so3_exp, so3_log, so3_right_jacobian  # noqa: E402

OUT = Path(__file__).parent / "results"
RUNS = 2000                                      # Monte Carlo robots
STEPS = 10                                       # 1 m each
STEP = np.array([1.0, 0, 0, 0, 0, 0])            # xi = [rho, phi]: 1 m forward, no turn
SIGMA = np.array([0.01, 0.01, 0.01, np.radians(0.5), np.radians(0.5), np.radians(6.0)])   # per step


# --- scene 1: the same small rotation applied on the box's side (right) or the world's side (left) -----

def box_edges(R, size=(2.0, 1.0, 0.5)):
    """The 12 edges of a box centred at the origin, rotated by R; a list of (2,3) segments."""
    corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]) * np.array(size) / 2
    corners = corners @ R.T
    return [corners[[i, j]] for i in range(8) for j in range(i + 1, 8) if bin(i ^ j).count("1") == 1]


def draw_box(ax, R, title):
    for e in box_edges(R):
        ax.plot(*e.T, color="0.3", lw=1.2)
    for axis, colour in zip(R.T, ("tab:red", "tab:green", "tab:blue")):   # the box's own x, y, z
        ax.quiver(0, 0, 0, *(1.4 * axis), color=colour, lw=2, arrow_length_ratio=0.15)
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), zlim=(-1.5, 1.5), xticks=[], yticks=[], zticks=[], title=title)
    ax.set_box_aspect((1, 1, 1))


def scene_box(rng):
    R = so3_exp([0, 0, np.radians(90)])                      # the box faces world +y
    d = np.array([np.radians(40), 0, 0])                     # 40 deg about "x"
    R_right = R @ so3_exp(d)                                 # (Eq. 4) about the box's own x: it rolls
    R_left = so3_exp(d) @ R                                  # (Eq. 4) about the world's x: it pitches
    worst = 0.0
    for _ in range(1000):                                    # (Eq. 5) R Exp(d) == Exp(R d) R, for any R, d
        Rr, dd = so3_exp(rng.normal(size=3)), rng.normal(size=3)
        worst = max(worst, np.abs(Rr @ so3_exp(dd) - so3_exp(Rr @ dd) @ Rr).max())
    fig = plt.figure(figsize=(12, 4.2))
    for i, (Ri, t) in enumerate([(R, "start: the box faces world +y"),
                                 (R_right, "R · Exp(δ): about its own x (rolls)"),
                                 (R_left, "Exp(δ) · R: about the world's x (pitches)")]):
        draw_box(fig.add_subplot(1, 3, i + 1, projection="3d"), Ri, t)
    fig.suptitle("The same δ = 40° about x, applied on the right or on the left (red/green/blue = the box's x/y/z)")
    fig.savefig(OUT / "box_perturbation.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return {"right_vs_left_deg": float(np.degrees(np.linalg.norm(so3_log(R_right.T @ R_left)))),
            "eq5_max_error": float(worst)}


# --- scene 2: what the right Jacobian buys --------------------------------------------------------------

def scene_jacobian(rng):
    angles = np.radians(np.linspace(1, 175, 60))
    err_plain, err_jr = [], []
    for th in angles:
        plain, jr = [], []
        for _ in range(50):                                              # 50 random axes and nudges per angle
            a, d = rng.normal(size=3), rng.normal(size=3)
            w, d = th * a / np.linalg.norm(a), 1e-3 * d / np.linalg.norm(d)
            exact = so3_exp(w + d)                                       # nudge the rotation vector itself
            plain.append(np.linalg.norm(so3_log(exact.T @ so3_exp(w) @ so3_exp(d))))            # ignore J_r
            jr.append(np.linalg.norm(so3_log(exact.T @ so3_exp(w) @ so3_exp(so3_right_jacobian(w) @ d))))  # (Eq. 6)
        err_plain.append(np.mean(plain))
        err_jr.append(np.mean(jr))
    err_plain, err_jr = np.array(err_plain), np.array(err_jr)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.semilogy(np.degrees(angles), err_plain / 1e-3, label="Exp(w)·Exp(δ): J_r ignored")
    ax.semilogy(np.degrees(angles), err_jr / 1e-3, label="Exp(w)·Exp(J_r(w)·δ)  (Eq. 6)")
    ax.set(xlabel="size of the rotation w (deg)", ylabel="error / |δ|",
           title="Nudging a rotation vector by |δ| = 0.001 (mean of 50)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.savefig(OUT / "jacobian_error.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    at = lambda e, deg: float(np.interp(np.radians(deg), angles, e) / 1e-3)   # noqa: E731
    return {"plain_at_60deg": at(err_plain, 60), "jr_at_60deg": at(err_jr, 60),
            "plain_at_170deg": at(err_plain, 170), "jr_max": float(err_jr.max() / 1e-3)}


# --- scene 3: the banana ----------------------------------------------------------------------------------

def banana(rng, sigma):
    """Monte Carlo end positions, and samples from the two Gaussian models of where the robot could be."""
    ends, xis = np.empty((RUNS, 3)), np.empty((RUNS, 6))
    T_mean, Sigma = propagate_covariance(STEP, STEPS, sigma)                  # (Eq. 10) no samples
    for i in range(RUNS):
        T = drive(STEP, rng.normal(size=(STEPS, 6)) * sigma)                  # (Eq. 9)
        ends[i], xis[i] = T[:3, 3], se3_log(np.linalg.inv(T_mean) @ T)
    xy = ends[:, :2]
    xy_model = rng.multivariate_normal(xy.mean(0), np.cov(xy.T), RUNS)        # best Gaussian in x-y
    se3_model = np.array([(T_mean @ se3_exp(x))[:2, 3]
                          for x in rng.multivariate_normal(np.zeros(6), Sigma, RUNS)])
    tree = cKDTree(xy)
    reach = np.percentile(tree.query(xy, k=2)[0][:, 1], 99)   # "on the cloud" = this close to some endpoint
    off = lambda pts: float(np.mean(tree.query(pts)[0] > reach))   # noqa: E731
    sample_cov = np.cov(xis.T)
    return dict(xy=xy, xy_model=xy_model, se3_model=se3_model, mean=xy.mean(0),
                off_xy=off(xy_model), off_se3=off(se3_model),
                mean_gap_cm=float(100 * np.min(np.linalg.norm(xy - xy.mean(0), axis=1))),
                trace_ratio=float(np.trace(sample_cov) / np.trace(Sigma)),
                along_track_ratio=float(sample_cov[0, 0] / Sigma[0, 0]),
                lateral_ratio=float(sample_cov[1, 1] / Sigma[1, 1]))


def scene_banana(rng):
    b = banana(rng, SIGMA)
    paths = []
    for _ in range(25):                                       # a few whole paths, to see the fan open
        T, path, U = np.eye(4), [np.zeros(2)], se3_exp(STEP)
        for w in rng.normal(size=(STEPS, 6)) * SIGMA:
            T = T @ U @ se3_exp(w)
            path.append(T[:2, 3])
        paths.append(np.array(path))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)
    for ax, key, colour, name, off in [(axes[0], "xy_model", "tab:blue", "a Gaussian in x–y", b["off_xy"]),
                                       (axes[1], "se3_model", "tab:orange", "a Gaussian on SE(3)", b["off_se3"])]:
        for p in paths:
            ax.plot(*p.T, color="0.75", lw=0.6, zorder=1)
        ax.scatter(*b[key].T, s=4, color=colour, alpha=0.3, label=f"samples from {name}", zorder=2)
        ax.scatter(*b["xy"].T, s=1, color="black", label=f"{RUNS} robots (Monte Carlo)", zorder=3)
        ax.set(title=f"{name}: {off:.0%} of its samples are off the cloud", xlabel="x (m)", aspect="equal")
        ax.legend(loc="lower left", markerscale=4)
    axes[0].plot(*b["mean"], "kx", ms=10, mew=2, zorder=4)
    axes[0].annotate("x–y average", b["mean"], (6.0, 1.5), arrowprops={"arrowstyle": "->"})
    axes[0].set_ylabel("y (m)")
    fig.suptitle(f"{STEPS} steps of 1 m, heading noise 6° per step: the cloud of end points is a banana")
    fig.savefig(OUT / "banana.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    worse = banana(rng, SIGMA * np.array([1, 1, 1, 1, 1, 10 / 6]))
    return {**{k: v for k, v in b.items() if not isinstance(v, np.ndarray)},
            "break_10deg_off_xy": worse["off_xy"], "break_10deg_off_se3": worse["off_se3"]}


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(0)
    m = {"box": scene_box(rng), "jacobian": scene_jacobian(rng), "banana": scene_banana(rng)}
    box, jac, ban = m["box"], m["jacobian"], m["banana"]
    lines = [
        f"box: R·Exp(δ) and Exp(δ)·R end {box['right_vs_left_deg']:.1f}° apart; "
        f"Eq. 5 holds to {box['eq5_max_error']:.1e}",
        f"J_r: error/|δ| at 60° is {jac['plain_at_60deg']:.3f} without J_r, {jac['jr_at_60deg']:.5f} with it; "
        f"at 170° {jac['plain_at_170deg']:.2f} without",
        f"banana ({RUNS} runs, {STEPS} x 1 m, 6°/step heading noise):",
        f"  x-y average is {ban['mean_gap_cm']:.1f} cm from the nearest robot",
        f"  samples off the cloud: Gaussian in x-y {ban['off_xy']:.1%}, Gaussian on SE(3) {ban['off_se3']:.1%}",
        f"  Monte Carlo / predicted covariance (Eq. 10): total {ban['trace_ratio']:.2f}, "
        f"lateral {ban['lateral_ratio']:.2f}, along-track {ban['along_track_ratio']:.1f}",
        f"break it, 10°/step: off the cloud x-y {ban['break_10deg_off_xy']:.1%}, "
        f"SE(3) {ban['break_10deg_off_se3']:.1%}",
    ]
    text = "\n".join(lines)
    print(text)
    (OUT / "output.txt").write_text(text + "\n")
    (OUT / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")


if __name__ == "__main__":
    main()
