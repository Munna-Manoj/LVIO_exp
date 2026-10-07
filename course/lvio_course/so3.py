"""Rotations (chapter A01). Batched: every function accepts (..., 3) vectors / (..., 3, 3) matrices."""
from __future__ import annotations

import numpy as np


def hat(v: np.ndarray) -> np.ndarray:
    """(..., 3) vector -> (..., 3, 3) skew-symmetric matrix, so hat(a) @ b == cross(a, b)."""
    v = np.asarray(v, dtype=float)
    out = np.zeros(v.shape[:-1] + (3, 3))
    out[..., 0, 1], out[..., 0, 2] = -v[..., 2], v[..., 1]
    out[..., 1, 0], out[..., 1, 2] = v[..., 2], -v[..., 0]
    out[..., 2, 0], out[..., 2, 1] = -v[..., 1], v[..., 0]
    return out


def exp(phi: np.ndarray) -> np.ndarray:
    """Rotation vector (rad) -> rotation matrix (Rodrigues), stable near zero."""
    phi = np.asarray(phi, dtype=float)
    th = np.linalg.norm(phi, axis=-1)[..., None, None]
    k = hat(phi)
    small = th < 1e-8
    a = np.where(small, 1.0 - th**2 / 6.0, np.sin(th) / np.where(small, 1.0, th))
    b = np.where(small, 0.5 - th**2 / 24.0, (1.0 - np.cos(th)) / np.where(small, 1.0, th) ** 2)
    return np.eye(3) + a * k + b * (k @ k)


def log(R: np.ndarray) -> np.ndarray:
    """Rotation matrix -> rotation vector (rad), angle in [0, pi)."""
    R = np.asarray(R, dtype=float)
    cos = np.clip((np.trace(R, axis1=-2, axis2=-1) - 1.0) / 2.0, -1.0, 1.0)
    th = np.arccos(cos)[..., None]
    w = np.stack([R[..., 2, 1] - R[..., 1, 2], R[..., 0, 2] - R[..., 2, 0], R[..., 1, 0] - R[..., 0, 1]], axis=-1)
    small = th < 1e-8
    return np.where(small, 0.5 * w, th / (2.0 * np.sin(np.where(small, 1.0, th))) * w)
