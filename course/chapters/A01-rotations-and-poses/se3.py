"""A01 · Poses: the SE(3) exp/log maps, the adjoint, and how a pose's uncertainty travels along a path.

A pose T = [[R, t], [0, 1]] maps body coordinates to world coordinates. Its tangent vector is xi = [rho, phi]:
translation part first, rotation part second (the DS-MSP order). se3_exp, se3_log and se3_adjoint are DS-MSP's
(ds_msp/core/lie.py), copied verbatim; drive and propagate_covariance are this chapter's.
"""

from __future__ import annotations

import numpy as np

from so3 import hat, so3_exp, so3_left_jacobian, so3_log


def se3_exp(xi: np.ndarray) -> np.ndarray:
    """Exp map ``ℝ⁶ → SE(3)``. ``xi = [ρ (3), φ (3)]`` (translation tangent, then rotation).
    Returns a ``4×4`` homogeneous transform ``[[R, J_l(φ)ρ], [0, 1]]``."""
    xi = np.asarray(xi, float)
    rho, phi = xi[:3], xi[3:]
    R = so3_exp(phi)
    T = np.eye(4)
    T[:3, :3] = R                                                                   # (Eq. 7)
    T[:3, 3] = so3_left_jacobian(phi) @ rho                                         # (Eq. 7)
    return T


def se3_log(T: np.ndarray) -> np.ndarray:
    """Inverse of :func:`se3_exp`: ``SE(3) → ℝ⁶`` as ``[ρ, φ]``."""
    T = np.asarray(T, float)
    phi = so3_log(T[:3, :3])
    rho = np.linalg.solve(so3_left_jacobian(phi), T[:3, 3])
    return np.concatenate([rho, phi])


def se3_adjoint(T: np.ndarray) -> np.ndarray:
    """Adjoint ``Ad_T (6,6)`` of SE(3) for ``xi = [ρ, φ]``: ``T·se3_exp(ξ)·T⁻¹ = se3_exp(Ad_T·ξ)``.
    Moves a perturbation across a pose: ``T·Exp(ξ) = Exp(Ad_T·ξ)·T`` (right ↔ left)."""
    T = np.asarray(T, float)
    R, t = T[:3, :3], T[:3, 3]
    Ad = np.zeros((6, 6))
    Ad[:3, :3] = R                                                                  # (Eq. 8)
    Ad[:3, 3:] = hat(t) @ R                                                         # (Eq. 8)
    Ad[3:, 3:] = R                                                                  # (Eq. 8)
    return Ad


def drive(u, noise):
    """Compose one step u (a tangent vector) per row of `noise`; each step lands off by its noise row,
    in the body frame. Returns the end pose (4,4)."""
    U = se3_exp(u)
    T = np.eye(4)
    for w in noise:
        T = T @ U @ se3_exp(w)                                                      # (Eq. 9)
    return T


def propagate_covariance(u, n_steps, sigma):
    """Mean end pose and the 6x6 covariance of xi in T = T_mean · Exp(xi), without a single sample (Eq. 10)."""
    U = se3_exp(u)
    Ad_inv = se3_adjoint(np.linalg.inv(U))
    Q = np.diag(np.asarray(sigma, float) ** 2)
    T_mean, Sigma = np.eye(4), np.zeros((6, 6))
    for _ in range(n_steps):
        T_mean = T_mean @ U
        Sigma = Ad_inv @ Sigma @ Ad_inv.T + Q                                       # (Eq. 10)
    return T_mean, Sigma
