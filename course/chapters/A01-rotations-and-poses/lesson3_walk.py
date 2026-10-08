"""A01 · Lesson 3, part 1: a blindfolded robot walks 10 x 1 m. One robot step by step, then many.

Each step: walk 1 m the way you face, then slip by a random turn (bell curve, 6 deg). The turns ADD UP: a heading
error is remembered and steers every later metre. First in plain cos/sin, then the same walk with se3_exp (Eq. 9).
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc

from se3 import se3_exp

STEPS, TURN_STD_DEG = 10, 6.0


def unit(deg):
    return np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])


def walk(turns_deg, add_up=True):
    """Corners p_0..p_N and the facing after each step (deg). add_up=False: each slip is forgotten (re-aim at +x)."""
    p, facing, corners, facings = np.zeros(2), 0.0, [np.zeros(2)], [0.0]
    for t in turns_deg:
        p = p + unit(facing)                                  # walk 1 m: dx = cos(facing), dy = sin(facing)
        facing = facing + t if add_up else t                  # then slip by the random turn
        corners.append(p)
        facings.append(facing)
    return np.array(corners), np.array(facings)


def walk_se3(turns_deg):
    """The same walk as poses: T <- T Exp(u) Exp(w), u = 1 m forward, w = the slip (a yaw only)."""
    T, ends = np.eye(4), [np.zeros(2)]
    for t in turns_deg:
        T = T @ se3_exp([1.0, 0, 0, 0, 0, 0]) @ se3_exp([0, 0, 0, 0, 0, np.radians(t)])      # (Eq. 9)
        ends.append(T[:2, 3])
    return np.array(ends)


def scene_one_robot(out, rng):
    """The overview and one zoomed panel per step, with the angles written on them."""
    turns = rng.normal(size=STEPS) * TURN_STD_DEG
    corners, facings = walk(turns)
    fig = plt.figure(figsize=(18, 10.5))
    gs = fig.add_gridspec(3, 5, height_ratios=[1.1, 1, 1])
    ax = fig.add_subplot(gs[0, :])
    ax.plot([0, 10], [0, 0], ":", color="0.6", label="+x: straight ahead at the start")
    for k in range(STEPS):
        a, b = corners[k], corners[k + 1]
        ax.annotate("", b, a, arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2))
        ax.text(*(a + b) / 2 + [0, 0.25 if k % 2 else -0.4],
                f"{k + 1}: facing {facings[k]:+.1f}°\nthen slip {turns[k]:+.1f}°", fontsize=8, ha="center")
    ax.plot(*corners.T, "ko", ms=3)
    ax.set(aspect="equal", xlim=(-0.3, 10.6), ylim=(-2.2, 1.2), xlabel="x (m)", ylabel="y (m)",
           title=f"One robot. End: ({corners[-1, 0]:.2f}, {corners[-1, 1]:+.2f}) m, facing {facings[-1]:+.1f}°")
    ax.legend(loc="lower left", fontsize=8)
    for k in range(STEPS):                                    # step k: walk with the old facing, then turn
        ax = fig.add_subplot(gs[1 + k // 5, k % 5])
        c, e = corners[k], corners[k + 1]
        ax.plot(*corners[: k + 1].T, "-o", color="0.6", ms=3)
        ax.plot(*np.c_[e, e + 0.6 * unit(0)], ":", color="0.6", lw=1)
        ax.annotate("", e, c, arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.2))
        ax.plot(*np.c_[e, e + 0.6 * unit(facings[k + 1])], "--", color="tab:green", lw=1.5)
        lo, hi = sorted((facings[k], facings[k + 1]))
        ax.add_patch(Arc(e, 1.0, 1.0, theta1=lo, theta2=hi, color="tab:orange", lw=2.5))
        ax.text(0.03, 0.88, f"walk 1 m facing {facings[k]:+.1f}°", transform=ax.transAxes, color="tab:red",
                fontsize=9, fontweight="bold")
        ax.text(0.03, 0.05, f"slip {turns[k]:+.1f}° → facing {facings[k + 1]:+.1f}°", transform=ax.transAxes,
                color="tab:orange", fontsize=9, fontweight="bold")
        ax.set(aspect="equal", xlim=(c[0] - 0.2, c[0] + 1.6), ylim=(c[1] - 0.75, c[1] + 0.75), xticks=[], yticks=[])
        ax.set_title(f"step {k + 1}", fontsize=9)
    fig.suptitle("Red = the 1 m walked, in the direction the robot faces.  Orange = the random slip after it.  "
                 "Green dashed = the new facing, which every later metre follows.", fontsize=11)
    fig.savefig(out / "one_robot.png", dpi=90, bbox_inches="tight")
    plt.close(fig)
    se3_ends = walk_se3(turns)
    return {"turns_deg": turns.tolist(), "facings_deg": facings.tolist(), "corners": corners.tolist(),
            "cos_sin_vs_se3_max_m": float(np.abs(se3_ends - corners).max())}


def scene_many(out, rng, runs=2000):
    """1, 5, 50, 2000 robots; then why the paths look smooth: the turns add up."""
    turns = rng.normal(size=(runs, STEPS)) * TURN_STD_DEG
    paths = [walk(t)[0] for t in turns]
    ends = np.array([p[-1] for p in paths])
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2), sharey=True)
    for ax, n in zip(axes, (1, 5, 50, runs)):
        for p in paths[: min(n, 60)]:
            ax.plot(*p.T, color="0.7", lw=0.6)
        ax.scatter(*ends[:n].T, s=4 if n > 50 else 18, color="black", zorder=3)
        ax.set(aspect="equal", xlim=(-0.5, 11), ylim=(-5.5, 5.5), xlabel="x (m)", title=f"{n} robot{'s' * (n > 1)}")
    axes[0].set_ylabel("y (m)")
    fig.suptitle("The same walk, new random slips each time: the end points pile up on a curve")
    fig.savefig(out / "many_robots.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    big = rng.normal(size=(40, STEPS)) * 30.0
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    forgotten = np.array([walk(t, add_up=False)[0][-1] for t in turns])
    for ax, ps, title in [(axes[0], paths[:40], "6° slips that ADD UP (the robot above):\nsmooth, and it fans out"),
                          (axes[1], [walk(t)[0] for t in big], "30° slips that add up:\nnow you see the zig-zag"),
                          (axes[2], [walk(t, add_up=False)[0] for t in turns[:40]],
                           "6° slips that are FORGOTTEN (re-aim at +x):\nno fan, no banana")]:
        for i, p in enumerate(ps):
            ax.plot(*p.T, color="tab:red" if i == 0 else "0.7", lw=2 if i == 0 else 0.7, zorder=2 if i == 0 else 1)
            ax.plot(*p[-1], "k.", ms=5)
        ax.set(aspect="equal", xlim=(-1, 11), ylim=(-7, 7), xlabel="x (m)", title=title)
    axes[0].set_ylabel("y (m)")
    fig.savefig(out / "turns_add_up.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    r = np.linalg.norm(ends, axis=1)
    return {"end_y_std_m": float(ends[:, 1].std()), "end_x_min_m": float(ends[:, 0].min()),
            "end_r_mean_m": float(r.mean()), "end_r_std_m": float(r.std()),
            "forgotten_end_y_std_m": float(forgotten[:, 1].std()),
            "facing_std_deg": float(turns.sum(axis=1).std())}


def scene_exp_arc(out):
    """What se3_exp does: drive 10 m forward while turning steadily by theta. The ends bend back, like the robots."""
    fig, ax = plt.subplots(figsize=(7, 5.2))
    ends = {}
    for deg in (-40, -20, 0, 20, 40):
        xi = np.array([10.0, 0, 0, 0, 0, np.radians(deg)])
        arc = np.array([se3_exp(s * xi)[:2, 3] for s in np.linspace(0, 1, 50)])   # (Eq. 7) along the way
        ax.plot(*arc.T, lw=2)
        ax.annotate(f"θ = {deg:+d}°", arc[-1], (8, 0), textcoords="offset points", fontsize=9)
        ends[deg] = arc[-1].tolist()
    ax.set(aspect="equal", xlabel="x (m)", ylabel="y (m)",
           title="se3_exp([10 m forward, 0, 0, 0, 0, yaw θ]):\ndrive 10 m while turning steadily by θ")
    fig.savefig(out / "exp_arc.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return {"arc_end_20deg": ends[20], "arc_end_40deg": ends[40]}
