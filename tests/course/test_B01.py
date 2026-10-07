"""B01 claims, asserted: building blocks are correct and the chapter's printed numbers hold."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "course"))

from lvio_course import imu, sim, so3  # noqa: E402

RESULTS = ROOT / "course" / "chapters" / "B01-imu-propagation" / "results" / "metrics.json"


def test_so3_exp_log_roundtrip():
    phi = np.random.default_rng(0).normal(size=(100, 3))
    phi *= (np.pi * 0.99 * np.random.default_rng(1).random((100, 1))) / np.linalg.norm(phi, axis=1, keepdims=True)
    assert np.allclose(so3.log(so3.exp(phi)), phi, atol=1e-9)
    R = so3.exp(phi)
    assert np.allclose(R @ np.swapaxes(R, -1, -2), np.eye(3), atol=1e-12)


def test_perfect_imu_reproduces_rotation_exactly():
    truth = sim.figure_eight(duration=5.0)
    g, f = sim.imu_from_truth(truth, sim.ImuNoise(0.0, 0.0))
    R, _, _ = imu.propagate(truth.R[0], truth.v[0], truth.p[0], g, f, truth.t[1] - truth.t[0])
    assert np.abs(so3.log(np.swapaxes(R[0], -1, -2) @ truth.R)).max() < 1e-9


def test_chapter_claims_hold():
    m = json.loads(RESULTS.read_text())
    e = m["rms_position_error_m"]
    assert e["gyro noise"]["20s"] > 5 * e["accel noise"]["20s"]           # gyro dominates drift
    assert e["noise + bias"]["20s"] > 2 * e["white noise"]["20s"]          # biases matter
    assert 0.8 < m["mc_over_predicted_20s"] < 1.25                         # covariance is consistent
    assert m["perfect_imu_max_error_m"] < 0.02                             # discretisation floor ~1 cm


def test_slopes_match_theory():
    truth = sim.figure_eight(duration=20.0)
    dt = truth.t[1] - truth.t[0]
    g0, f0 = sim.imu_from_truth(truth, sim.ImuNoise(0.0, 0.0))
    _, _, p0 = imu.propagate(truth.R[0], truth.v[0], truth.p[0], g0, f0, dt)
    g, f = sim.imu_from_truth(truth, sim.ImuNoise(accel_density=0.0), seed=2, n_runs=100)
    _, _, p = imu.propagate(truth.R[0], truth.v[0], truth.p[0], g, f, dt)
    rms = np.sqrt((np.linalg.norm(p - p0[0][None], axis=-1) ** 2).mean(0))
    slope = np.log(rms[int(16 / dt)] / rms[int(4 / dt)]) / np.log(4.0)
    assert 2.2 < slope < 2.8                                                # gyro noise ~ t^2.5
