"""Synthetic ground truth and IMU measurements (chapter B01). Deterministic for a given seed.

The trajectory is a smooth 3D figure-eight with turning and tilting, like a handheld or legged robot.
Truth is defined analytically; the IMU is derived from it, so every error the reader sees comes from the
estimator, never from the simulator.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import so3

GRAVITY = np.array([0.0, 0.0, -9.81])  # world frame, z up (m/s^2)


@dataclass
class ImuNoise:
    """Continuous-time noise densities and constant biases (SI units)."""
    gyro_density: float = 2.4e-4   # rad/s/sqrt(Hz)  (~0.014 deg/s/sqrt(Hz), BMI088-class MEMS)
    accel_density: float = 1.7e-3  # m/s^2/sqrt(Hz)  (~175 ug/sqrt(Hz))
    gyro_bias: float = 0.0         # rad/s, constant per axis magnitude (drawn with a random sign)
    accel_bias: float = 0.0        # m/s^2


@dataclass
class Truth:
    t: np.ndarray      # (N,) s
    p: np.ndarray      # (N, 3) world position, m
    v: np.ndarray      # (N, 3) world velocity, m/s
    R: np.ndarray      # (N, 3, 3) body-to-world rotation
    a_w: np.ndarray    # (N, 3) world acceleration, m/s^2


def figure_eight(duration: float = 20.0, rate: float = 200.0) -> Truth:
    t = np.arange(0.0, duration + 1e-9, 1.0 / rate)
    w = 2 * np.pi / 10.0
    p = np.stack([3 * np.sin(w * t), 1.5 * np.sin(2 * w * t), 0.3 * np.sin(3 * w * t)], axis=1)
    v = np.stack([3 * w * np.cos(w * t), 3 * w * np.cos(2 * w * t), 0.9 * w * np.cos(3 * w * t)], axis=1)
    a = np.stack([-3 * w**2 * np.sin(w * t), -6 * w**2 * np.sin(2 * w * t), -2.7 * w**2 * np.sin(3 * w * t)], axis=1)
    yaw = np.arctan2(v[:, 1], v[:, 0])                     # face the direction of travel
    yaw = np.unwrap(yaw)
    roll, pitch = 0.15 * np.sin(1.3 * t), 0.10 * np.sin(0.9 * t)
    R = so3.exp(np.stack([np.zeros_like(t), np.zeros_like(t), yaw], 1)) \
        @ so3.exp(np.stack([np.zeros_like(t), pitch, np.zeros_like(t)], 1)) \
        @ so3.exp(np.stack([roll, np.zeros_like(t), np.zeros_like(t)], 1))
    return Truth(t, p, v, R, a)


def imu_from_truth(truth: Truth, noise: ImuNoise, seed: int = 0, n_runs: int = 1):
    """Ideal + noisy IMU samples. Returns gyro, accel of shape (n_runs, N-1, 3) for the interval [t_k, t_k+1].

    gyro_k  = Log(R_k^T R_{k+1}) / dt + bias + noise     (exact mean rate over the interval)
    accel_k = R_k^T (a_w,k - g) + bias + noise            (specific force at t_k)
    """
    rng = np.random.default_rng(seed)
    dt = truth.t[1] - truth.t[0]
    n = len(truth.t) - 1
    gyro = so3.log(np.swapaxes(truth.R[:-1], -1, -2) @ truth.R[1:]) / dt
    accel = np.einsum("nji,nj->ni", truth.R[:-1], truth.a_w[:-1] - GRAVITY)
    sg, sa = noise.gyro_density / np.sqrt(dt), noise.accel_density / np.sqrt(dt)   # discrete-time std
    bg = noise.gyro_bias * rng.choice([-1.0, 1.0], size=(n_runs, 1, 3))
    ba = noise.accel_bias * rng.choice([-1.0, 1.0], size=(n_runs, 1, 3))
    g = gyro[None] + bg + sg * rng.standard_normal((n_runs, n, 3))
    f = accel[None] + ba + sa * rng.standard_normal((n_runs, n, 3))
    return g, f
