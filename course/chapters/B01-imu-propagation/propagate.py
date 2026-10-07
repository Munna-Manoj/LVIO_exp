"""B01 · Turn IMU readings into a trajectory, and predict how wrong that trajectory will be.

State: rotation R (body -> world), velocity v and position p (world frame).
Everything here is the README's "The math" section, one equation per block.
"""
import numpy as np

GRAVITY = np.array([0.0, 0.0, -9.81])  # world frame, z up (m/s^2)


def hat(w):
    """Vector -> skew-symmetric matrix, so that hat(a) @ b == np.cross(a, b)."""
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def so3_exp(phi):
    """Rotation vector (rad) -> rotation matrix (Rodrigues' formula)."""
    th = np.linalg.norm(phi)
    if th < 1e-8:
        return np.eye(3) + hat(phi)
    K = hat(phi / th)
    return np.eye(3) + np.sin(th) * K + (1.0 - np.cos(th)) * K @ K


def propagate(R0, v0, p0, gyro, accel, dt):
    """Dead reckoning: integrate N IMU readings from the start state. Returns R (N+1,3,3), v, p (N+1,3)."""
    n = len(gyro)
    R, v, p = np.empty((n + 1, 3, 3)), np.empty((n + 1, 3)), np.empty((n + 1, 3))
    R[0], v[0], p[0] = R0, v0, p0
    for k in range(n):
        a_world = R[k] @ accel[k] + GRAVITY                              # (Eq. 2) remove gravity
        p[k + 1] = p[k] + v[k] * dt + 0.5 * a_world * dt**2             # (Eq. 4)
        v[k + 1] = v[k] + a_world * dt                                   # (Eq. 3)
        R[k + 1] = R[k] @ so3_exp(gyro[k] * dt)                          # (Eq. 1)
    return R, v, p


def propagate_covariance(R, gyro, accel, dt, gyro_noise, accel_noise):
    """Covariance of the 9-dim error [d_theta, d_v, d_p] along a trajectory, starting from zero (Eq. 5)."""
    n = len(gyro)
    Q = np.diag([gyro_noise**2 / dt] * 3 + [accel_noise**2 / dt] * 3)   # (Eq. 8) per-sample noise variances
    P = np.zeros((n + 1, 9, 9))
    for k in range(n):
        F = np.eye(9)                                                    # how an error at k becomes one at k+1
        F[0:3, 0:3] = so3_exp(-gyro[k] * dt)                             # attitude error turns with the body
        F[3:6, 0:3] = -R[k] @ hat(accel[k]) * dt                         # tilt error -> leaked gravity in v
        F[6:9, 0:3] = -0.5 * R[k] @ hat(accel[k]) * dt**2                # ... and in p
        F[6:9, 3:6] = np.eye(3) * dt                                     # velocity error -> position error
        G = np.zeros((9, 6))                                             # how one sample's noise enters
        G[0:3, 0:3] = -np.eye(3) * dt
        G[3:6, 3:6] = -R[k] * dt
        G[6:9, 3:6] = -0.5 * R[k] * dt**2
        P[k + 1] = F @ P[k] @ F.T + G @ Q @ G.T                          # (Eq. 5)
    return P
