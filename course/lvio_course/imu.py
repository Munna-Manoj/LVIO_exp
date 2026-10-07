"""IMU propagation of the mean and of the error-state covariance (chapter B01).

State: rotation R (body->world), velocity v and position p in the world frame.
Error state (9): [dtheta (body frame), dv, dp]. Biases enter in chapter B02.
"""
from __future__ import annotations

import numpy as np

from . import so3
from .sim import GRAVITY


def propagate(R0, v0, p0, gyro, accel, dt):
    """Integrate a batch of IMU sequences. gyro/accel: (B, N, 3). Returns R (B,N+1,3,3), v, p (B,N+1,3)."""
    B, N, _ = gyro.shape
    R = np.empty((B, N + 1, 3, 3))
    v = np.empty((B, N + 1, 3))
    p = np.empty((B, N + 1, 3))
    R[:, 0], v[:, 0], p[:, 0] = R0, v0, p0
    for k in range(N):
        a_w = np.einsum("bij,bj->bi", R[:, k], accel[:, k]) + GRAVITY     # world acceleration
        p[:, k + 1] = p[:, k] + v[:, k] * dt + 0.5 * a_w * dt**2
        v[:, k + 1] = v[:, k] + a_w * dt
        R[:, k + 1] = R[:, k] @ so3.exp(gyro[:, k] * dt)
    return R, v, p


def propagate_covariance(R, gyro, accel, dt, gyro_density, accel_density):
    """Discrete error-state covariance along one nominal trajectory. Returns P (N+1, 9, 9), P0 = 0."""
    N = gyro.shape[0]
    sg2, sa2 = gyro_density**2 / dt, accel_density**2 / dt          # discrete noise variances
    P = np.zeros((N + 1, 9, 9))
    for k in range(N):
        F = np.eye(9)
        F[0:3, 0:3] = so3.exp(-gyro[k] * dt)                          # attitude error rotates with the body
        F[3:6, 0:3] = -R[k] @ so3.hat(accel[k]) * dt                  # tilt error -> wrong gravity removal
        F[6:9, 0:3] = -0.5 * R[k] @ so3.hat(accel[k]) * dt**2
        F[6:9, 3:6] = np.eye(3) * dt
        G = np.zeros((9, 6))
        G[0:3, 0:3] = -np.eye(3) * dt
        G[3:6, 3:6] = -R[k] * dt
        G[6:9, 3:6] = -0.5 * R[k] * dt**2
        Q = np.diag([sg2] * 3 + [sa2] * 3)
        P[k + 1] = F @ P[k] @ F.T + G @ Q @ G.T
    return P
