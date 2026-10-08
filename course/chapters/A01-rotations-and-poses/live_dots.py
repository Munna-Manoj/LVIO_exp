"""A01 · Lesson 3, animated: how each blue and each orange dot of the banana is made, then why orange is SE(3).

The robots are lesson3_banana.py's: 2000 drive 10 x 1 m with noise after every step (Eq. 9) -> the black dots.

PART 1  how the dots of the chapter figure are made
  blue   : a bell curve in x and y, FITTED to the black dots. Draw (x, y), put a dot there. A dot has no facing.
  orange : a bell curve over xi = [rho, phi] (move, turn), PREDICTED by Eq. 10 without the black dots.
           Draw xi, then drive from the mean pose:  T = T_mean . se3_exp(xi).

PART 2  the SAME six random numbers xi = [rho, phi], used two ways
  left  (not SE(3)): p = p_mean + rho, and separately R = R_mean . Exp(phi)   -> the turn never moves the point
  right (SE(3))    : T = T_mean . se3_exp([rho, phi])                         -> moving and turning happen together

python live_dots.py            # both parts, live window (space = pause / resume)
python live_dots.py --part 2   # only part 2
python live_dots.py --part 2 --slow 2 --gif   # write results/live_dots.gif instead
"""
import argparse
from pathlib import Path

import matplotlib

ap = argparse.ArgumentParser()
ap.add_argument("--part", type=int, choices=(1, 2), help="run only this part")
ap.add_argument("--slow", type=int, default=4, help="dots shown one by one")
ap.add_argument("--gif", action="store_true")
args = ap.parse_args()
matplotlib.use("Agg" if args.gif else "TkAgg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402

from lesson3_banana import SIGMA, off_cloud, robots, separate, together  # noqa: E402
from so3 import so3_left_jacobian  # noqa: E402

SLOW, FAST, PER_FRAME = args.slow, 1000, 25    # dots shown one by one; dots in total; dots per fast frame
DRAW_F, MOVE_F, LAND_F = (10, 14, 10) if args.gif else (22, 30, 22)   # frames per slow dot

rng = np.random.default_rng(0)
ends, T_mean, Sigma = robots(rng, SIGMA)                          # (Eq. 9) the truth, (Eq. 10) the prediction
truth = np.array([T[:2, 3] for T in ends])
m_xy, C_xy = truth.mean(0), np.cov(truth.T)                       # recipe A is fitted to the truth
is_off = off_cloud(truth)
std = np.sqrt(np.diag(Sigma))


def on_cloud(p):
    return is_off(np.atleast_2d(p)) == 0.0


def yaw(T):
    return np.degrees(np.arctan2(T[1, 0], T[0, 0]))


def not_se3(xi, s=1.0):
    return separate(T_mean, s * xi)                               # p_mean + s rho, R_mean Exp(s phi)


def se3(xi, s=1.0):
    return together(T_mean, s * xi)                               # T_mean Exp(s xi): part of the drive


# ---- the random draws, made up front -----------------------------------------------------------------------
L_xy = np.linalg.cholesky(C_xy)
part1_blue = m_xy + rng.normal(size=(FAST, 2)) @ L_xy.T
part1_xi = rng.multivariate_normal(np.zeros(6), Sigma, FAST)
pool = rng.multivariate_normal(np.zeros(6), Sigma, FAST + 200)
by_turn = np.argsort(-np.abs(pool[:200, 5]))                     # part 2's slow dots: big, medium, small, no turn
slow2 = [by_turn[12], by_turn[40], by_turn[100], by_turn[-1]]
part2_xi = np.vstack([pool[slow2], pool[200:200 + FAST - SLOW]])

# ---- figure ---------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(15, 9.6))
gs = fig.add_gridspec(2, 2, height_ratios=[3.2, 1])
axes = [fig.add_subplot(gs[0, i]) for i in range(2)]
notes = [fig.add_subplot(gs[1, i]) for i in range(2)]
for ax in notes:
    ax.axis("off")
note_txt = [ax.text(0.0, 1.0, "", va="top", family="monospace", fontsize=9.5, transform=ax.transAxes) for ax in notes]
for ax in axes:
    ax.scatter(*truth.T, s=1, color="0.15", alpha=0.5, zorder=1)
    ax.set(aspect="equal", xlim=(5.5, 11.2), ylim=(-5.2, 5.2), xlabel="x (m)", ylabel="y (m)")
landed = [ax.scatter([], [], s=6, alpha=0.55, zorder=3) for ax in axes]
counter = [ax.text(0.02, 0.01, "", transform=ax.transAxes, fontsize=10, fontweight="bold", zorder=10) for ax in axes]
dyn, state = [], {}


def mean_pose_marker(ax):
    """The mean pose: where a noise-free robot ends, facing +x, with its own x (red) and y (green) axes."""
    p = T_mean[:2, 3]
    out = ax.plot(*p, marker=(3, 0, -90), ms=13, color="k", zorder=6)
    out.append(ax.annotate("", p + [0.8, 0], p, arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.5), zorder=6))
    out.append(ax.annotate("", p + [0, 0.8], p, arrowprops=dict(arrowstyle="-|>", color="tab:green", lw=1.5), zorder=6))
    out.append(ax.text(*(p + [0.15, -0.35]), "mean pose\nT_mean", fontsize=8, zorder=6))
    return out


def setup(part):
    """Reset both panels for a part: titles, colours, the fixed drawings."""
    for a in state.get("fixed", []):
        a.remove()
    fixed = []
    if part == 1:
        titles = ["BLUE: a bell curve in x and y\n(fitted to the black dots)",
                  "ORANGE: a bell curve over ξ = [move, turn], then se3_exp\n"
                  "(predicted by Eq. 10, never sees the dots)"]
        colours = ["tab:blue", "tab:orange"]
        vals, vecs = np.linalg.eigh(C_xy)
        for k in (1, 2):                                                   # 1-sigma and 2-sigma ellipses of recipe A
            tilt = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
            e = Ellipse(m_xy, 2 * k * np.sqrt(vals[1]), 2 * k * np.sqrt(vals[0]), angle=tilt,
                        fill=False, color="tab:blue", ls="--", lw=1.2, zorder=2)
            axes[0].add_patch(e)
            fixed.append(e)
        fixed += axes[0].plot(*m_xy, "x", color="tab:blue", ms=12, mew=2.5, zorder=6)
        fixed.append(axes[0].text(*(m_xy + [0.12, 0.25]), "x–y average", color="tab:blue", fontsize=9, zorder=6))
    else:
        titles = ["NOT SE(3): p = p_mean + ρ,  R = R_mean·Exp(φ)\n(move and turn applied separately)",
                  "SE(3): T = T_mean · se3_exp([ρ, φ])\n(move and turn applied together)"]
        colours = ["tab:purple", "tab:orange"]
        fixed += mean_pose_marker(axes[0])
    fixed += mean_pose_marker(axes[1])
    for ax, t, c, sc in zip(axes, titles, colours, landed):
        ax.set_title(t, fontsize=11)
        sc.set_offsets(np.empty((0, 2)))
        sc.set_color(c)
    state.update(fixed=fixed, pts=[[], []], off=[0, 0], part=part, landed_set=set())
    fig.suptitle(f"PART {part} of 2" + ("  —  how the two kinds of dots in the chapter figure are made"
                                       if part == 1 else
                 "  —  the SAME six random numbers per dot, used two ways"), fontsize=13, fontweight="bold")


def frames():
    for part in ([args.part] if args.part else [1, 2]):
        yield part, "setup", 0, 0
        for i in range(SLOW):
            for _ in range(DRAW_F):
                yield part, "draw", i, 0.0
            for f in range(MOVE_F):
                yield part, "move", i, (f + 1) / MOVE_F
            for _ in range(LAND_F):
                yield part, "land", i, 1.0
        for i in range(SLOW, FAST, PER_FRAME):
            yield part, "fast", i, 1.0
        for _ in range(90):
            yield part, "end", FAST, 1.0


def fmt(v):
    return "[" + ", ".join(f"{x:+.2f}" for x in v) + "]"


def xi_text(xi):
    return (f"  move ρ = [forward {xi[0]:+.3f}, sideways {xi[1]:+.2f}, up {xi[2]:+.2f}] m\n"
            f"  turn φ = [roll {np.degrees(xi[3]):+.1f}°, pitch {np.degrees(xi[4]):+.1f}°, "
            f"yaw {np.degrees(xi[5]):+.1f}°]")


def land(k, p):
    state["pts"][k].append(p)
    state["off"][k] += not on_cloud(p)
    landed[k].set_offsets(np.array(state["pts"][k]))


def update(f):
    part, phase, i, s = f
    while dyn:
        dyn.pop().remove()
    if phase == "setup":
        setup(part)
        return []
    if phase in ("fast", "end"):
        if phase == "fast":
            for j in range(i, min(i + PER_FRAME, FAST)):
                if part == 1:
                    land(0, part1_blue[j])
                    land(1, se3(part1_xi[j])[:2, 3])
                else:
                    land(0, not_se3(part2_xi[j])[:2, 3])
                    land(1, se3(part2_xi[j])[:2, 3])
        n = len(state["pts"][0])
        msg = ("fast-forward: the same recipe, " + str(n) + " dots") if phase == "fast" else f"done: {n} dots each"
        for k in range(2):
            note_txt[k].set_text(msg + f"\n{100 * state['off'][k] / n:.1f} % of them landed where NO real robot is"
                                 + ("" if phase == "fast" else ("\n\n" + END[part][k])))
    else:
        for k in range(2):
            draw_slow(part, k, phase, i, s)
    for k in range(2):
        n = len(state["pts"][k])
        if n:
            counter[k].set_text(f"{n} dot{'s' if n > 1 else ''}, {100 * state['off'][k] / n:.1f} % off the cloud")
    return []


END = {1: ["Blue knows only a point (x, y): no facing, no link between\n'went far sideways' and 'must have "
           "fallen back in x'.\nIt fills a straight blob, even though it was fitted to the truth.",
           "Orange draws (move, turn) and lets se3_exp drive the robot:\na big sideways move comes with a big turn "
           "(Eq. 10 learned\nthat link step by step), and Exp bends it back onto the banana."],
       2: ["Same numbers, but the turn φ is applied on the spot:\nthe position is p_mean + ρ, a straight shift. "
           "The cloud of\npositions is a straight ellipse. This is 'SO(3) × R³'.",
           "Same numbers, one se3_exp: the position is p_mean + J_l(φ)·ρ.\nThe turn bends the move, so position and "
           "rotation stay tied\ntogether. This is what 'on SE(3)' means."]}


def robot(ax, T, colour):
    return ax.plot(*T[:2, 3], marker=(3, 0, yaw(T) - 90), ms=14, color=colour, zorder=7)


def draw_slow(part, k, phase, i, s):
    ax = axes[k]
    pm = T_mean[:2, 3]
    if part == 1 and k == 0:                                       # BLUE: a straight jump to a drawn (x, y)
        p = part1_blue[i]
        cur = m_xy + s * (p - m_xy)
        sx, sy = np.sqrt(np.diag(C_xy))
        lines = [f"blue dot {i + 1}:  draw x and y from the bell curve fitted to the black dots",
                 f"  x ~ {m_xy[0]:.2f} ± {sx:.2f} m   ->  drew x = {p[0]:.2f}",
                 f"  y ~ {m_xy[1]:+.2f} ± {sy:.2f} m   ->  drew y = {p[1]:+.2f}"]
        if phase != "draw":
            dyn.extend(ax.plot(*np.c_[m_xy, cur], "-", color="tab:blue", lw=2, zorder=5))
            dyn.extend(ax.plot(*cur, "o", color="tab:blue", ms=9, zorder=7))
            lines += ["  move there in a straight line. The dot is just a point: it has no facing."]
        start = m_xy
    else:
        xi = part1_xi[i] if part == 1 else part2_xi[i]
        T_end = se3(xi) if k == 1 else not_se3(xi)
        colour = "tab:orange" if k == 1 else "tab:purple"
        p = T_end[:2, 3]
        start = pm
        if k == 1:
            head = (f"orange dot {i + 1}:  draw 6 numbers ξ = [ρ, φ] from the PREDICTED bell curve (Eq. 10)"
                    if part == 1 else f"dot {i + 1}:  the six random numbers (same on both sides)")
            lines = [head, xi_text(xi)]
            if part == 1:
                lines[1] += f"\n  (spreads: sideways ±{std[1]:.2f} m, yaw ±{np.degrees(std[5]):.0f}°)"
        else:
            lines = [f"dot {i + 1}:  the six random numbers (same on both sides)", xi_text(xi)]
        if phase != "draw":
            ss = np.linspace(0, s, 40)
            path = np.array([(se3(xi, u) if k == 1 else not_se3(xi, u))[:2, 3] for u in ss])
            dyn.extend(ax.plot(*path.T, "-", color=colour, lw=2.2, zorder=5))
            dyn.extend(robot(ax, se3(xi, s) if k == 1 else not_se3(xi, s), colour))
            if k == 1:
                Jr = so3_left_jacobian(xi[3:]) @ xi[:3]
                lines += ["  T = T_mean · se3_exp(ξ): drive from the mean pose, moving AND turning at once",
                          f"  position = p_mean + J_l(φ)·ρ = (10, 0) + {fmt(Jr[:2])}  ->  ({p[0]:.2f}, {p[1]:+.2f})",
                          f"  facing {yaw(T_end):+.1f}°: the turn bent the move {fmt(xi[:2])} into {fmt(Jr[:2])}"]
            else:
                lines += [f"  position = p_mean + ρ = (10, 0) + {fmt(xi[:2])}  ->  ({p[0]:.2f}, {p[1]:+.2f})",
                          f"  facing = {yaw(T_end):+.1f}°, turned on the spot: the turn did NOT move the point"]
    if phase == "land":
        ok = on_cloud(p)
        dyn.extend(ax.plot(*p, "o", ms=16, mfc="none", mew=2.5, color="green" if ok else "red", zorder=8))
        lines += ["  -> landed ON the cloud: a real robot could be here" if ok else
                  "  -> landed OFF the cloud: no real robot ends here"]
        if (part, k, i) not in state["landed_set"]:              # count each slow dot once
            state["landed_set"].add((part, k, i))
            land(k, p)
    note_txt[k].set_text("\n".join(lines))
    del start


setup(args.part or 1)
n_frames = sum(1 + SLOW * (DRAW_F + MOVE_F + LAND_F) + len(range(SLOW, FAST, PER_FRAME)) + 90
               for _ in ([args.part] if args.part else [1, 2]))
anim = FuncAnimation(fig, update, frames=frames, interval=40, cache_frame_data=False, repeat=False,
                     save_count=n_frames)
paused = [False]


def toggle(event):
    if event.key == " ":
        (anim.resume if paused[0] else anim.pause)()
        paused[0] = not paused[0]


fig.canvas.mpl_connect("key_press_event", toggle)
fig.tight_layout()
if args.gif:
    anim.save(Path(__file__).parent / "results" / "live_dots.gif", writer=PillowWriter(fps=15), dpi=45)
else:
    plt.show()
