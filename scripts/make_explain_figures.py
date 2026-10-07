#!/usr/bin/env python3
"""Figures for docs/explain/. Regenerate with:  python scripts/make_explain_figures.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lvx import plotstyle  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "explain"


def so3_exp(phi: np.ndarray) -> np.ndarray:
    th = np.linalg.norm(phi)
    k = np.array([[0, -phi[2], phi[1]], [phi[2], 0, -phi[0]], [-phi[1], phi[0], 0]])
    if th < 1e-12:
        return np.eye(3) + k
    return np.eye(3) + np.sin(th) / th * k + (1 - np.cos(th)) / th**2 * k @ k


def left_jacobian(phi: np.ndarray) -> np.ndarray:
    th = np.linalg.norm(phi)
    k = np.array([[0, -phi[2], phi[1]], [phi[2], 0, -phi[0]], [-phi[1], phi[0], 0]])
    if th < 1e-12:
        return np.eye(3) + 0.5 * k
    return np.eye(3) + (1 - np.cos(th)) / th**2 * k + (th - np.sin(th)) / th**3 * k @ k


def retraction_paths() -> None:
    import matplotlib.pyplot as plt

    rho, phi = np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, np.pi / 2])
    s = np.linspace(0, 1, 60)
    se3 = np.array([left_jacobian(t * phi) @ (t * rho) for t in s])
    sep = np.array([t * rho for t in s])
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    ax.plot(sep[:, 0], sep[:, 1], color=plotstyle.SYSTEM_COLORS["lightning-lm"], lw=2.2,
            label="SO(3)×R³: straight line")
    ax.plot(se3[:, 0], se3[:, 1], color=plotstyle.SYSTEM_COLORS["se3-lvio"], lw=2.2, label="SE(3): screw (arc)")
    for t in (0, 0.5, 1):
        for path, col in ((se3, plotstyle.SYSTEM_COLORS["se3-lvio"]), (sep, plotstyle.SYSTEM_COLORS["lightning-lm"])):
            i = int(t * (len(s) - 1))
            r = so3_exp(t * phi)
            ax.annotate("", xy=path[i, :2] + 0.18 * r[:2, 0], xytext=path[i, :2],
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.4))
    ax.set_aspect("equal")
    ax.set_ylim(-0.05, 0.85)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Same correction δ = [ρ = 1 m x, φ = 90° z], two retractions")
    ax.legend(loc="upper left")
    fig.savefig(OUT / "retraction_paths.png")
    plt.close(fig)


def coupling_size() -> None:
    import matplotlib.pyplot as plt

    phis = np.logspace(-4, 0, 50)  # rad
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    for rho_m, ls in ((0.01, "-"), (0.1, "--"), (1.0, ":")):
        gap = [np.linalg.norm((left_jacobian(np.array([0, 0, p])) - np.eye(3)) @ np.array([rho_m, 0, 0])) for p in phis]
        ax.loglog(phis, np.array(gap) * 1e3, ls, color=plotstyle.SYSTEM_COLORS["se3-lvio"], label=f"|ρ| = {rho_m:g} m")
    ax.axvspan(1e-4, 5e-3, color=plotstyle.NOISE_BAND, alpha=0.3, lw=0)
    ax.text(1.2e-4, 3e2, "typical per-scan\nIEKF correction", fontsize=8)
    ax.set_xlabel("rotation part of the correction |φ| (rad)")
    ax.set_ylabel("position difference (mm)")
    ax.set_title("How far apart the two retractions land")
    ax.legend()
    fig.savefig(OUT / "retraction_gap.png")
    plt.close(fig)


def gate_vs_kernels() -> None:
    import matplotlib.pyplot as plt

    r = np.linspace(-6, 6, 600)
    huber = np.where(np.abs(r) <= 1.345, 1.0, 1.345 / np.abs(r))
    cauchy = 1 / (1 + (r / 2.385) ** 2)
    gate = (np.abs(r) <= 3).astype(float)
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(r, gate, color=plotstyle.GT, lw=2, label="hard 3σ gate (SE(3)-LVIO today)")
    ax.plot(r, huber, color=plotstyle.VARIANT_COLORS[0], lw=1.8, label="Huber (k = 1.345)")
    ax.plot(r, cauchy, color=plotstyle.VARIANT_COLORS[1], lw=1.8, label="Cauchy (c = 2.385)")
    for mu, a, stage in ((0.5, 0.35, "early"), (3.0, 0.6, "middle"), (20.0, 0.95, "late")):
        c2 = 9.0
        w = np.clip(np.sqrt(mu * (mu + 1) * c2 / np.maximum(r**2, 1e-9)) - mu, 0, 1)
        ax.plot(r, w, color=plotstyle.VARIANT_COLORS[2], lw=1.4, alpha=a, label=f"GNC-TLS, {stage} (μ = {mu:g})")
    ax.set_xlabel("normalised residual r / σ")
    ax.set_ylabel("weight in the update")
    ax.set_title("Who gets a vote: gate, kernels, and GNC annealing")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    fig.savefig(OUT / "weights.png")
    plt.close(fig)


if __name__ == "__main__":
    plotstyle.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    retraction_paths()
    coupling_size()
    gate_vs_kernels()
    print("\n".join(sorted(str(p.relative_to(OUT.parent.parent.parent)) for p in OUT.glob("*.png"))))
