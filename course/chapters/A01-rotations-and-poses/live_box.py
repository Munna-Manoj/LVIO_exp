"""A01 · Lesson 1, animated: the same turn, growing from 0 to delta, applied on the right and on the left of R.

  left panel : R · Exp(s·δ)   the box turns about its OWN axis (the coloured arrows move with it)
  right panel: Exp(s·δ) · R   the box turns about the WORLD's axis (the grey arrows stay put)

python live_box.py                       # the box faces world +y (yaw 90 deg), delta = 40 deg about x
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
ap.add_argument("--gif", action="store_true")
args = ap.parse_args()
matplotlib.use("Agg" if args.gif else "TkAgg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from lesson1_sides import box_edges, gap_deg, turned  # noqa: E402
from so3 import so3_exp  # noqa: E402

R = so3_exp([0, 0, np.radians(args.start_yaw)])
delta = np.radians(args.turn) * np.eye(3)["xyz".index(args.axis)]
S = np.r_[np.zeros(15), np.linspace(0, 1, 50), np.ones(40)]          # pause, turn, pause

fig = plt.figure(figsize=(12, 6))
axes = [fig.add_subplot(1, 2, i + 1, projection="3d") for i in range(2)]
note = fig.text(0.5, 0.02, "", ha="center", family="monospace", fontsize=10)
fig.suptitle(f"The box starts facing yaw {args.start_yaw:g}°. δ = {args.turn:g}° about {args.axis}, applied on "
             "each side.\nColoured arrows = the box's own x/y/z (columns of R). Grey arrows = the world's x/y/z.")


def update(i):
    s = S[i]
    for ax, (Ri, title) in zip(axes, [(turned(R, s * delta)[0], f"R · Exp(s·δ): about the box's own {args.axis}"),
                                       (turned(R, s * delta)[1], f"Exp(s·δ) · R: about the world's {args.axis}")]):
        ax.cla()
        for e in box_edges(Ri):
            ax.plot(*e.T, color="0.3", lw=1.2)
        for axis in np.eye(3):
            ax.quiver(0, 0, 0, *(1.6 * axis), color="0.75", lw=1, arrow_length_ratio=0.08)
        for axis, colour in zip(Ri.T, ("tab:red", "tab:green", "tab:blue")):
            ax.quiver(0, 0, 0, *(1.3 * axis), color=colour, lw=2.5, arrow_length_ratio=0.15)
        ax.set(xlim=(-1.6, 1.6), ylim=(-1.6, 1.6), zlim=(-1.6, 1.6), xticks=[], yticks=[], zticks=[], title=title)
        ax.set_xlabel("world x")
        ax.set_ylabel("world y")
        ax.set_zlabel("world z")
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=22, azim=-60)
    right, left = turned(R, s * delta)
    note.set_text(f"turned so far: {s * args.turn:5.1f}°      the two boxes now differ by {gap_deg(right, left):5.1f}°"
                  f"      nose (body x) right {np.round(right[:, 0], 2)}  left {np.round(left[:, 0], 2)}")
    return []


anim = FuncAnimation(fig, update, frames=len(S), interval=50, repeat=not args.gif)
if args.gif:
    anim.save(Path(__file__).parent / "results" / "live_box.gif", writer=PillowWriter(fps=15), dpi=45)
else:
    plt.show()
