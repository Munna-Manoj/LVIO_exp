"""A01 · Lesson 1, animated: the same turn, growing from 0 to delta, applied on the right and on the left of a POSE.

The box is a pose T = [R, t]: it sits --distance m from the world origin, along world y, the way it faces.
  left panel : T · T_δ   the box turns about its OWN axis, through its own centre: it spins in place
  right panel: T_δ · T   the box turns about the WORLD's axis, through the world origin: it also swings
                         around the origin (the dotted trail), so its position changes too

python live_box.py                       # the box faces world +y (yaw 90 deg), delta = 40 deg about x
python live_box.py --distance 0          # the box at the origin: only its orientation differs, it can't swing
python live_box.py --start-yaw 0         # the box faces +x: its axes ARE the world's, both sides agree
python live_box.py --axis z --turn 60    # turn about z instead
python live_box.py --gif                 # write results/live_box.gif instead
"""
import argparse
from pathlib import Path

import matplotlib

ap = argparse.ArgumentParser()
ap.add_argument("--start-yaw", type=float, default=90.0, help="how the box faces before the turn, deg")
ap.add_argument("--turn", type=float, default=40.0, help="size of delta, deg")
ap.add_argument("--axis", choices="xyz", default="x", help="delta is about this axis")
ap.add_argument("--distance", type=float, default=2.0, help="how far the box sits from the world origin, m")
ap.add_argument("--gif", action="store_true")
args = ap.parse_args()
matplotlib.use("Agg" if args.gif else "TkAgg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from lesson1_sides import box_edges, gap_deg  # noqa: E402
from so3 import so3_exp  # noqa: E402

T = np.eye(4)
T[:3, :3] = so3_exp([0, 0, np.radians(args.start_yaw)])
T[:3, 3] = [0, args.distance, 0]
delta = np.radians(args.turn) * np.eye(3)["xyz".index(args.axis)]
LIM = 1.3 + args.distance


def turned_pose(s):
    """Both sides of Eq. 4 for the 4x4 pose: T · T_δ (right) and T_δ · T (left), with T_δ a pure turn."""
    T_d = np.eye(4)
    T_d[:3, :3] = so3_exp(s * delta)
    return T @ T_d, T_d @ T
S = np.r_[np.zeros(15), np.linspace(0, 1, 50), np.ones(40)]          # pause, turn, pause

fig = plt.figure(figsize=(12, 6))
axes = [fig.add_subplot(1, 2, i + 1, projection="3d") for i in range(2)]
note = fig.text(0.5, 0.02, "", ha="center", family="monospace", fontsize=10)
fig.suptitle(f"The box starts {args.distance:g} m from the world origin, facing yaw {args.start_yaw:g}°. "
             f"δ = {args.turn:g}° about {args.axis}, applied on each side.\nColoured arrows = the box's own x/y/z "
             "(columns of R), at its centre. Grey arrows = the world's x/y/z, at the origin (+).")


def update(i):
    s = S[i]
    right, left = turned_pose(s)
    trail = [turned_pose(u) for u in S[: i + 1]]
    for k, (ax, Ti, title) in enumerate(zip(axes, (right, left),
                                            (f"T · T_δ (right): about the box's own {args.axis}, in place",
                                             f"T_δ · T (left): about the world's {args.axis}, through the origin"))):
        ax.cla()
        Ri, ti = Ti[:3, :3], Ti[:3, 3]
        for e in box_edges(T[:3, :3]):                                    # the start, for comparison
            ax.plot(*(e + T[:3, 3]).T, color="0.85", lw=1)
        for e in box_edges(Ri):
            ax.plot(*(e + ti).T, color="0.3", lw=1.2)
        for axis in np.eye(3):
            ax.quiver(0, 0, 0, *(1.6 * axis), color="0.75", lw=1, arrow_length_ratio=0.08)
        ax.plot([0], [0], [0], "k+", ms=12)
        ax.plot(*np.array([P[k][:3, 3] for P in trail]).T, ":", color="tab:purple", lw=2)    # where the centre went
        for axis, colour in zip(Ri.T, ("tab:red", "tab:green", "tab:blue")):
            ax.quiver(*ti, *(1.3 * axis), color=colour, lw=2.5, arrow_length_ratio=0.15)
        ax.set(xlim=(-LIM, LIM), ylim=(-LIM, LIM), zlim=(-LIM, LIM), xticks=[], yticks=[], zticks=[], title=title)
        ax.set_xlabel("world x")
        ax.set_ylabel("world y")
        ax.set_zlabel("world z")
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=12, azim=-25)
    moved = [np.linalg.norm(P[:3, 3] - T[:3, 3]) for P in (right, left)]
    note.set_text(f"turned so far: {s * args.turn:5.1f}°    orientations differ by "
                  f"{gap_deg(right[:3, :3], left[:3, :3]):5.1f}°    box centre moved: right {moved[0]:.2f} m, "
                  f"left {moved[1]:.2f} m")
    return []


anim = FuncAnimation(fig, update, frames=len(S), interval=50, repeat=not args.gif)
if args.gif:
    anim.save(Path(__file__).parent / "results" / "live_box.gif", writer=PillowWriter(fps=15), dpi=60)
else:
    plt.show()
