"""B01 · Rotations, copied from A01 (which explains them): hat, and the exp/log maps (Eq. 1 uses so3_exp).

These are DS-MSP's functions (github.com/Munna-Manoj/DS-MSP, ds_msp/core/lie.py), copied verbatim
(tools/check_lie.py keeps them identical).
"""

from __future__ import annotations

import numpy as np

_EPS = 1e-8


def hat(w: np.ndarray) -> np.ndarray:
    """so(3) hat: axis-angle vector ``(3,)`` → skew-symmetric ``[w]_× (3,3)``."""
    w = np.asarray(w, float)
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def vee(W: np.ndarray) -> np.ndarray:
    """Inverse of :func:`hat`: skew-symmetric ``(3,3)`` → axis-angle vector ``(3,)``."""
    W = np.asarray(W, float)
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def so3_exp(w: np.ndarray) -> np.ndarray:
    """Exp map ``ℝ³ → SO(3)`` (Rodrigues), numerically safe at ``θ = 0``."""
    w = np.asarray(w, float)
    theta2 = float(w @ w)
    Wx = hat(w)
    if theta2 < _EPS ** 2:                                  # Taylor: I + [w]_× + ½[w]_×²
        return np.eye(3) + Wx + 0.5 * (Wx @ Wx)
    theta = np.sqrt(theta2)
    return (np.eye(3) + (np.sin(theta) / theta) * Wx
            + ((1 - np.cos(theta)) / theta2) * (Wx @ Wx))


def so3_log(R: np.ndarray) -> np.ndarray:
    """Log map ``SO(3) → ℝ³``, safe at ``θ = 0`` and ``θ = π``."""
    R = np.asarray(R, float)
    c = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    theta = np.arccos(c)
    if theta < _EPS:
        return vee(R - R.T) * 0.5                           # small angle
    if np.pi - theta < 1e-5:                                # near π: axis from the largest diagonal
        A = (R + np.eye(3)) / 2.0                           # ≈ a aᵀ
        k = int(np.argmax(np.diag(A)))
        axis = A[:, k] / np.sqrt(max(A[k, k], _EPS))
        axis = axis / np.linalg.norm(axis)
        return theta * axis
    return (theta / (2.0 * np.sin(theta))) * vee(R - R.T)

