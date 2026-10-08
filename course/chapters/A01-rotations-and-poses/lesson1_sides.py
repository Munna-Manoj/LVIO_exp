"""A01 · Lesson 1: the same small turn, applied on the right (the body's own axes) or on the left (the world's axes).

A rotation R maps body coordinates to world coordinates: p_w = R p_b. Read a product right to left, the way a
point travels through it:
  R @ so3_exp(d) @ p_b   the point is turned while still in body coordinates   -> about the body's own axes
  so3_exp(d) @ R @ p_b   the point is turned after it reached world coordinates -> about the world's axes
"""
import matplotlib.pyplot as plt
import numpy as np

from so3 import so3_exp, so3_log

NOSE = np.array([1.0, 0, 0])                         # the box's nose, in body coordinates
TURN = np.array([np.radians(40), 0, 0])              # delta: 40 deg about "x"


def box_edges(R, size=(2.0, 1.0, 0.5)):
    """The 12 edges of a box centred at the origin, rotated by R; a list of (2,3) segments."""
    corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]) * np.array(size) / 2
    corners = corners @ R.T
    return [corners[[i, j]] for i in range(8) for j in range(i + 1, 8) if bin(i ^ j).count("1") == 1]


def draw_box(ax, R, title):
    for e in box_edges(R):
        ax.plot(*e.T, color="0.3", lw=1.2)
    for axis, colour in zip(R.T, ("tab:red", "tab:green", "tab:blue")):   # the box's own x, y, z (columns of R)
        ax.quiver(0, 0, 0, *(1.4 * axis), color=colour, lw=2, arrow_length_ratio=0.15)
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), zlim=(-1.5, 1.5), xticks=[], yticks=[], zticks=[], title=title)
    ax.set_xlabel("world x")
    ax.set_ylabel("world y")
    ax.set_box_aspect((1, 1, 1))


def turned(R, d):
    """Both sides of Eq. 4 for the same delta."""
    return R @ so3_exp(d), so3_exp(d) @ R                     # (Eq. 4) right: body axes; left: world axes


def gap_deg(R1, R2):
    return float(np.degrees(np.linalg.norm(so3_log(R1.T @ R2))))


def scene_box(out, rng):
    """The money plot of lesson 1, the nose worked through by hand, and Eq. 5 checked on random rotations."""
    R = so3_exp([0, 0, np.radians(90)])                       # the box faces world +y
    R_right, R_left = turned(R, TURN)
    worst = 0.0
    for _ in range(1000):                                     # (Eq. 5) R Exp(d) == Exp(R d) R, for any R, d
        Rr, dd = so3_exp(rng.normal(size=3)), rng.normal(size=3)
        worst = max(worst, np.abs(Rr @ so3_exp(dd) - so3_exp(Rr @ dd) @ Rr).max())
    fig = plt.figure(figsize=(12, 4.2))
    for i, (Ri, t) in enumerate([(R, "start: the box faces world +y"),
                                 (R_right, "R · Exp(δ): about its own x (rolls)"),
                                 (R_left, "Exp(δ) · R: about the world's x (pitches)")]):
        draw_box(fig.add_subplot(1, 3, i + 1, projection="3d"), Ri, t)
    fig.suptitle("The same δ = 40° about x, applied on the right or on the left (red/green/blue = the box's x/y/z)")
    fig.savefig(out / "box_perturbation.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    knob = {}
    for yaw in (0, 30, 60, 90, 180):                          # turn the knob: how the box faces before the turn
        knob[yaw] = gap_deg(*turned(so3_exp([0, 0, np.radians(yaw)]), TURN))
    t = np.array([0, 2.0, 0])                                 # live_box.py: the box 2 m out along world y
    swing = float(np.linalg.norm(so3_exp(TURN) @ t - t))      # a left turn moves its centre; a right one doesn't
    return {"right_vs_left_deg": gap_deg(R_right, R_left), "eq5_max_error": float(worst), "box_2m_left_moved_m": swing,
            "nose_start": (R @ NOSE).tolist(), "nose_right": (R_right @ NOSE).tolist(),
            "nose_left": (R_left @ NOSE).tolist(), "gap_by_start_yaw_deg": knob}


def scene_pose(out):
    """The same trap for a pose: a left turn spins the robot about the WORLD origin, so its position swings too."""
    T = np.eye(4)
    T[:3, 3] = [10.0, 0, 0]                                   # 10 m from the origin, facing +x
    T_d = np.eye(4)
    T_d[:3, :3] = so3_exp([0, 0, np.radians(5)])              # a pure turn: 5 deg of yaw
    T_right, T_left = T @ T_d, T_d @ T                        # (Eq. 4) the same two sides, for a 4x4 pose
    fig, ax = plt.subplots(figsize=(9, 4.4))
    a = np.radians(np.linspace(0, 5, 30))
    ax.plot(10 * np.cos(a), 10 * np.sin(a), ":", color="tab:purple", lw=1.5,
            label="left: swings about the world origin")
    for P, colour, name in [(T, "0.4", "start"), (T_right, "tab:orange", "T · T_δ (right)"),
                            (T_left, "tab:purple", "T_δ · T (left)")]:
        yaw = np.degrees(np.arctan2(P[1, 0], P[0, 0]))
        ax.plot(*P[:2, 3], marker=(3, 0, yaw - 90), ms=16, color=colour, ls="", label=name, alpha=0.85)
        ax.annotate("", P[:2, 3] + 0.8 * P[:2, 0], P[:2, 3], arrowprops=dict(arrowstyle="-|>", color=colour, lw=2))
    ax.plot(0, 0, "k+", ms=12)
    ax.annotate("world origin", (0, 0), (0.3, 0.25))
    ax.set(aspect="equal", xlim=(-0.5, 11.5), ylim=(-1.2, 2.4), xlabel="world x (m)", ylabel="world y (m)",
           title="A robot 10 m from the origin, turned 5° on the right or on the left")
    ax.legend(loc="center", fontsize=9)
    fig.savefig(out / "pose_left_right.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return {"right_moved_m": float(np.linalg.norm(T_right[:3, 3] - T[:3, 3])),
            "left_moved_m": float(np.linalg.norm(T_left[:3, 3] - T[:3, 3]))}
