"""B01 · Make a ground-truth motion and the IMU readings it would produce.

The truth is a figure-eight you can draw by hand: 6 m wide, 3 m deep, gently rising and falling, with
the body turning to face where it goes and rocking a little (like a handheld scanner or a legged robot).
Every quantity is written as a formula of time, so the truth is exact and every error you see later
comes from the IMU or the integrator, never from this file.
"""
import numpy as np

from so3 import so3_log

GRAVITY = np.array([0.0, 0.0, -9.81])  # world frame, z up (m/s^2)


def rot_x(a):
    return np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])


def rot_y(a):
    return np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])


def rot_z(a):
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


def figure_eight(duration=20.0, rate=200.0):
    """Ground truth sampled at `rate` Hz: time t, position p, velocity v, acceleration a (world), rotation R."""
    t = np.arange(0.0, duration + 1e-9, 1.0 / rate)
    w = 2 * np.pi / 10.0                                    # one figure-eight every 10 s
    p = np.stack([3.0 * np.sin(w * t), 1.5 * np.sin(2 * w * t), 0.3 * np.sin(3 * w * t)], axis=1)
    v = np.stack([3.0 * w * np.cos(w * t), 3.0 * w * np.cos(2 * w * t), 0.9 * w * np.cos(3 * w * t)], axis=1)
    a = np.stack([-3.0 * w**2 * np.sin(w * t), -6.0 * w**2 * np.sin(2 * w * t),
                  -2.7 * w**2 * np.sin(3 * w * t)], axis=1)
    yaw = np.unwrap(np.arctan2(v[:, 1], v[:, 0]))          # face the direction of travel
    pitch = 0.10 * np.sin(0.9 * t)                          # gentle rocking
    roll = 0.15 * np.sin(1.3 * t)
    R = np.array([rot_z(yaw[k]) @ rot_y(pitch[k]) @ rot_x(roll[k]) for k in range(len(t))])
    return t, p, v, a, R


def imu_readings(t, a, R):
    """What a perfect body-mounted IMU reports between samples k and k+1, for k = 0 .. N-2."""
    dt = t[1] - t[0]
    n = len(t) - 1
    gyro = np.array([so3_log(R[k].T @ R[k + 1]) / dt for k in range(n)])      # (Eq. 6)
    accel = np.array([R[k].T @ (a[k] - GRAVITY) for k in range(n)])          # (Eq. 7)
    return gyro, accel


def add_imu_errors(gyro, accel, dt, rng, gyro_noise=0.0, accel_noise=0.0, gyro_bias=0.0, accel_bias=0.0):
    """A real IMU: perfect readings + white noise + a constant bias.

    gyro_noise, accel_noise: white-noise densities (rad/s/sqrt(Hz), m/s^2/sqrt(Hz)).
    gyro_bias, accel_bias:   constant offsets (rad/s, m/s^2), same size on every axis, random sign.
    """
    n = len(gyro)
    # A noise density becomes a per-sample standard deviation by dividing by sqrt(dt).  (Eq. 8)
    gyro = gyro + gyro_bias * rng.choice([-1.0, 1.0], 3) + gyro_noise / np.sqrt(dt) * rng.standard_normal((n, 3))
    accel = accel + accel_bias * rng.choice([-1.0, 1.0], 3) + accel_noise / np.sqrt(dt) * rng.standard_normal((n, 3))
    return gyro, accel
