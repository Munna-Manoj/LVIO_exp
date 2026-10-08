"""A01 · Lesson 2: nudge a rotation VECTOR w by delta. Which small turn of the body is that? Not delta: J_r(w) delta.

In 2-D every rotation is about the same axis, so turning angles add like numbers. In 3-D they don't: changing
the vector w = 90 deg about z by a little along x turns the body about a tilted, shorter axis. J_r tells which.
"""
import matplotlib.pyplot as plt
import numpy as np

from so3 import so3_exp, so3_log, so3_right_jacobian


def body_turn(w, d):
    """The small turn of the body, in its own axes, caused by changing the rotation vector from w to w + d."""
    return so3_log(so3_exp(w).T @ so3_exp(w + d))


def scene_example():
    """One case by hand: w = 90 deg about z, nudged by 0.01 rad along x."""
    w, d = np.array([0, 0, np.radians(90)]), np.array([0.01, 0, 0])
    exact = body_turn(w, d)
    predicted = so3_right_jacobian(w) @ d                                # (Eq. 6)
    return {"example_exact": exact.tolist(), "example_jr": predicted.tolist(),
            "example_shrink": float(np.linalg.norm(exact) / np.linalg.norm(d)),
            "example_tilt_deg": float(np.degrees(np.arctan2(exact[1], exact[0])))}


def scene_arrows(out):
    """The step by step picture: as w grows about z, the body turn for a nudge along x tilts and shrinks."""
    angles = [0, 45, 90, 135, 180]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.annotate("", (1, 0), (0, 0), arrowprops=dict(arrowstyle="-|>", color="0.5", lw=3))
    ax.text(1.02, 0.03, "δ: the nudge you made\nto the vector (along x)", color="0.4", fontsize=9)
    colours = plt.cm.viridis(np.linspace(0, 0.9, len(angles)))
    shrink = {}
    for deg, c in zip(angles, colours):
        g = so3_right_jacobian(np.array([0, 0, np.radians(deg)])) @ np.array([1.0, 0, 0])   # (Eq. 6)
        shrink[deg] = float(np.linalg.norm(g))
        ax.annotate("", g[:2], (0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2))
        ax.text(*(g[:2] * 1.06 + [0, -0.05]), f"|w| = {deg}°", color=c, fontsize=9)
    ax.set(aspect="equal", xlim=(-0.2, 1.7), ylim=(-1.0, 0.35), xlabel="body x", ylabel="body y",
           title="J_r(w)·δ: the turn the body really makes,\nfor w about z of growing size")
    ax.grid(alpha=0.3)
    fig.savefig(out / "jacobian_arrows.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return {"arrow_length": shrink}


def scene_error(out, rng):
    """Two ways side by side: pretend the nudge is delta (no J_r), or use J_r(w) delta; mean of 50 random cases."""
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
    fig.savefig(out / "jacobian_error.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    at = lambda e, deg: float(np.interp(np.radians(deg), angles, e) / 1e-3)   # noqa: E731
    w = np.radians(60) * np.array([0.6, 0.0, 0.8])                            # the knob: nudge ALONG w's axis
    d = 1e-3 * w / np.linalg.norm(w)
    along = np.linalg.norm(so3_log(so3_exp(w + d).T @ so3_exp(w) @ so3_exp(d)))   # J_r ignored, same axis
    return {"plain_at_60deg": at(err_plain, 60), "jr_at_60deg": at(err_jr, 60),
            "plain_at_10deg": at(err_plain, 10), "plain_at_170deg": at(err_plain, 170),
            "jr_max": float(err_jr.max() / 1e-3), "along_w_at_60deg": float(along / 1e-3)}
