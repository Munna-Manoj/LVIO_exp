"""A01 · Lesson 3, animated: one robot at a time walks 1 m, then slips by a random turn. Two scenarios side by side,
with the SAME random slips:

  left : slips ADD UP     facing_k = facing_(k-1) + slip_k   (a real robot: a heading error is remembered)
  right: slips FORGOTTEN  facing_k = slip_k                  (re-aim at +x after every step: not how robots work)

The first robots are shown step by step with notes; then robots are fast-forwarded and the end points pile up.

python live_walk.py                  # live window   (space = pause / resume; close the window to stop)
python live_walk.py --turn-std 1     # smaller slips: std 1 deg per step (facing after 10 steps: about ±3 deg)
python live_walk.py --slow 1 --robots 60 --gif   # write results/live_walk.gif instead
"""
import argparse
from pathlib import Path

import matplotlib

ap = argparse.ArgumentParser()
ap.add_argument("--turn-std", type=float, default=6.0, help="std of the slip per step, deg (facing spreads by "
                                                              "about turn-std x sqrt(10) after 10 steps)")
ap.add_argument("--slow", type=int, default=3, help="robots shown step by step")
ap.add_argument("--robots", type=int, default=300, help="robots in total")
ap.add_argument("--seed", type=int, default=3)
ap.add_argument("--gif", action="store_true")
args = ap.parse_args()
matplotlib.use("Agg" if args.gif else "TkAgg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.patches import Arc  # noqa: E402

from lesson3_walk import STEPS, unit, walk  # noqa: E402

WALK_F, TURN_F, HOLD_F = (6, 6, 3) if args.gif else (12, 12, 8)    # frames per step
SLIPS = np.random.default_rng(args.seed).normal(size=(args.robots, STEPS)) * args.turn_std   # deg, same both sides


def frames():
    for r in range(args.robots):
        if r < args.slow:
            for k in range(STEPS):
                for i in range(WALK_F):
                    yield r, k, "walk", (i + 1) / WALK_F
                for i in range(TURN_F):
                    yield r, k, "slip", (i + 1) / TURN_F
                for _ in range(HOLD_F):
                    yield r, k, "hold", 1.0
            for _ in range(4 * HOLD_F):
                yield r, STEPS - 1, "done", 1.0
        else:
            yield r, STEPS - 1, "fast", 1.0
    for _ in range(40):
        yield args.robots - 1, STEPS - 1, "end", 1.0


fig, axes = plt.subplots(2, 2, figsize=(15, 9.5), gridspec_kw={"height_ratios": [1.15, 1]})
panels = []
for col, (add_up, title) in enumerate([(True, "Slips ADD UP (a real robot)"),
                                       (False, "Slips FORGOTTEN (re-aim at +x after each step)")]):
    big, zoom = axes[0, col], axes[1, col]
    big.set(aspect="equal", xlim=(-0.5, 11), ylim=(-4.5, 4.5), xlabel="x (m)", ylabel="y (m)", title=title)
    big.axhline(0, color="0.85", ls=":", lw=1)
    note = big.text(0.01, 0.99, "", transform=big.transAxes, va="top", family="monospace", fontsize=9,
                    bbox=dict(boxstyle="round", fc="white", ec="0.7", alpha=0.95), zorder=10)
    spread = big.text(0.99, 0.01, "", transform=big.transAxes, ha="right", va="bottom", fontsize=9, zorder=10)
    panels.append(dict(add_up=add_up, big=big, zoom=zoom, note=note, spread=spread, ends=[], dyn=[], done=-1))
fig.suptitle(f"Slip per step: std {args.turn_std:g}° (facing after {STEPS} steps: about "
             f"±{args.turn_std * np.sqrt(STEPS):.1f}°).   Red = the 1 m walked, orange = the slip after it, "
             "green dashed = the new facing.\nGrey = earlier robots, black = where they ended.", fontsize=10)


def draw(ax, corners, facings, k, phase, s, scale):
    """The path so far, the robot (triangle) and, during the slip, the turn arc and the new facing."""
    out = []
    c, e = corners[k], corners[k + 1]
    P = c + s * (e - c) if phase == "walk" else e
    f_now = facings[k] + (s * (facings[k + 1] - facings[k]) if phase == "slip" else 0.0)
    if phase in ("hold", "done"):
        f_now = facings[k + 1]
    out += ax.plot(*np.vstack([corners[: k + 1], P]).T, "-", color="tab:red", lw=2, zorder=4)
    out += ax.plot(*corners[: k + 1].T, "o", color="tab:red", ms=3, zorder=4)
    if phase != "walk":
        lo, hi = sorted((facings[k], f_now))
        arc = Arc(e, 1.2 * scale, 1.2 * scale, theta1=lo, theta2=hi, color="tab:orange", lw=2.5, zorder=5)
        ax.add_patch(arc)
        out.append(arc)
        out += ax.plot(*np.c_[e, e + 1.3 * scale * unit(facings[k])], ":", color="0.5", lw=1, zorder=3)
        out += ax.plot(*np.c_[e, e + 1.3 * scale * unit(f_now)], "--", color="tab:green", lw=1.5, zorder=3)
    out += ax.plot(*P, marker=(3, 0, f_now - 90), ms=14 * min(1.0, 2 * scale), color="k", zorder=6)
    return out


def update(f):
    r, k, phase, s = f
    for p in panels:
        for a in p["dyn"]:
            a.remove()
        p["dyn"] = []
        corners, facings = walk(SLIPS[r], add_up=p["add_up"])
        big, zoom = p["big"], p["zoom"]
        if phase in ("done", "fast") and p["done"] < r:                     # finished: leave a grey trail
            big.plot(*corners.T, color="0.75", lw=0.6, zorder=1)
            big.plot(*corners[-1], "k.", ms=4, zorder=2)
            p["ends"].append(corners[-1])
            p["done"] = r
        if len(p["ends"]) > 1:
            e = np.array(p["ends"])
            p["spread"].set_text(f"{len(e)} robots: end y spread ±{e[:, 1].std():.2f} m, "
                                 f"end x {e[:, 0].min():.2f} … {e[:, 0].max():.2f} m")
        if phase in ("fast", "end"):
            p["note"].set_text(f"fast-forward: robot {r + 1} of {args.robots}\nwatch where the end points pile up")
            zoom.cla()
            zoom.plot(*np.array(p["ends"]).T, "k.", ms=4)
            zoom.set(xlim=(7.0, 10.4), ylim=(-4.5, 4.5), xlabel="x (m), stretched", ylabel="y (m)",
                     title="where the robots ended (x stretched to show the curve)")
            continue
        p["dyn"] += draw(big, corners, facings, k, phase, s, 1.0)
        p["dyn"] += draw(zoom, corners, facings, k, phase, s, 0.6)
        c = corners[k]
        zoom.set(aspect="equal", xlim=(c[0] - 0.3, c[0] + 1.9), ylim=(c[1] - 0.8, c[1] + 0.8), xticks=[], yticks=[],
                 title="zoom on the robot")
        q = corners[k + 1]
        lines = [f"robot {r + 1}, step {k + 1} of {STEPS}",
                 f"walk 1 m facing {facings[k]:+6.1f}°",
                 f"  dx = cos({facings[k]:+.1f}°) = {np.cos(np.radians(facings[k])):.3f}",
                 f"  dy = sin({facings[k]:+.1f}°) = {np.sin(np.radians(facings[k])):+.3f}",
                 f"  -> ({q[0]:.2f}, {q[1]:+.2f})"]
        if phase != "walk":
            lines += [f"then slip         {SLIPS[r, k]:+6.1f}°",
                      f"new facing        {facings[k + 1]:+6.1f}°" +
                      (f" = {facings[k]:+.1f} {SLIPS[r, k]:+.1f}" if p["add_up"]
                       else "  (the old facing is forgotten)")]
        if phase == "done":
            lines += ["", f"END ({corners[-1][0]:.2f}, {corners[-1][1]:+.2f}) after 10 m of walking"]
        p["note"].set_text("\n".join(lines))
    return []


n = args.slow * (STEPS * (WALK_F + TURN_F + HOLD_F) + 4 * HOLD_F) + args.robots - args.slow + 40
anim = FuncAnimation(fig, update, frames=frames, interval=40, cache_frame_data=False, repeat=False, save_count=n)
paused = [False]


def toggle(event):
    if event.key == " ":
        (anim.resume if paused[0] else anim.pause)()
        paused[0] = not paused[0]


fig.canvas.mpl_connect("key_press_event", toggle)
fig.tight_layout()
if args.gif:
    anim.save(Path(__file__).parent / "results" / "live_walk.gif", writer=PillowWriter(fps=15), dpi=45)
else:
    plt.show()
