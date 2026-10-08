"""B01's claims, asserted: the code is correct and every number the README states holds."""
import json
import sys
from pathlib import Path

import numpy as np

CHAPTER = Path(__file__).resolve().parents[2] / "course" / "chapters" / "B01-imu-propagation"
sys.path.insert(0, str(CHAPTER))      # the test reaches into the chapter; the chapter never reaches out

from propagate import propagate  # noqa: E402
from simulate import figure_eight, imu_readings  # noqa: E402
from so3 import so3_exp, so3_log  # noqa: E402

M = json.loads((CHAPTER / "results" / "metrics.json").read_text())


def test_exp_and_log_are_inverses():
    rng = np.random.default_rng(0)
    for _ in range(200):
        phi = rng.normal(size=3)
        phi *= rng.uniform(0, 0.99 * np.pi) / np.linalg.norm(phi)
        R = so3_exp(phi)
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
        assert np.allclose(so3_log(R), phi, atol=1e-9)


def test_perfect_imu_reproduces_rotation_exactly():
    t, p, v, a, R = figure_eight(duration=5.0)
    gyro, accel = imu_readings(t, a, R)
    R_est, _, _ = propagate(R[0], v[0], p[0], gyro, accel, t[1] - t[0])
    assert max(np.linalg.norm(so3_log(Rt.T @ Re)) for Rt, Re in zip(R, R_est)) < 1e-9


def test_readme_claims_hold():
    assert M["gyro noise"]["20s"] > 5 * M["accel noise"]["20s"]           # gyro dominates drift
    assert M["noise + bias"]["20s"] > 2 * M["white noise"]["20s"]          # biases matter
    assert 0.8 < M["mc_over_predicted"] < 1.25                             # the covariance is consistent
    assert M["step_error_max_m"] < 0.02                                    # Euler floor ~1 cm
    assert 1.5 < M["gyro_overtakes_accel_s"] < 4.0                         # crossover after a few seconds
    assert max(M[k]["0.1s"] for k in ("accel noise", "gyro noise", "white noise", "noise + bias")) <= 2e-4


def test_slopes_match_theory():
    def slope(case):
        return np.log(M[case]["20s"] / M[case]["5s"]) / np.log(4.0)
    assert 1.3 < slope("accel noise") < 1.7                                # t^1.5
    assert 2.2 < slope("gyro noise") < 2.8                                 # t^2.5
