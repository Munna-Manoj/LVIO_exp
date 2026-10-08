"""A01's claims, asserted: the Lie-group code is correct and every number the README states holds."""
import json
import sys
from pathlib import Path

import numpy as np

CHAPTER = Path(__file__).resolve().parents[2] / "course" / "chapters" / "A01-rotations-and-poses"
sys.path.insert(0, str(CHAPTER))      # the test reaches into the chapter; the chapter never reaches out

from se3 import propagate_covariance, se3_adjoint, se3_exp, se3_log  # noqa: E402
from so3 import hat, so3_exp, so3_log, so3_right_jacobian, vee  # noqa: E402

M = json.loads((CHAPTER / "results" / "metrics.json").read_text())
RNG = np.random.default_rng(0)


def random_pose():
    return se3_exp(np.r_[RNG.normal(size=3), RNG.normal(size=3)])


def test_hat_is_the_cross_product_and_vee_inverts_it():
    a, b = RNG.normal(size=3), RNG.normal(size=3)
    assert np.allclose(hat(a) @ b, np.cross(a, b))
    assert np.allclose(vee(hat(a)), a)


def test_so3_exp_and_log_are_inverses_including_near_pi():
    for _ in range(200):
        w = RNG.normal(size=3)
        w *= RNG.uniform(0, 0.99 * np.pi) / np.linalg.norm(w)
        R = so3_exp(w)
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12) and np.isclose(np.linalg.det(R), 1.0)
        assert np.allclose(so3_log(R), w, atol=1e-9)
    near_pi = np.array([0.0, 0.0, np.pi - 1e-7])
    assert np.allclose(so3_exp(so3_log(so3_exp(near_pi))), so3_exp(near_pi), atol=1e-6)


def test_right_jacobian_matches_finite_differences():
    w, h = np.array([0.4, -0.7, 1.1]), 1e-6
    J = np.empty((3, 3))
    for i in range(3):
        d = np.zeros(3)
        d[i] = h
        J[:, i] = so3_log(so3_exp(w).T @ so3_exp(w + d)) / h       # Exp(w + d) = Exp(w) Exp(J_r d)
    assert np.allclose(J, so3_right_jacobian(w), atol=1e-5)


def test_se3_exp_log_and_the_adjoint_identity():
    for _ in range(50):
        xi = np.r_[RNG.normal(size=3), 0.9 * RNG.normal(size=3)]
        assert np.allclose(se3_log(se3_exp(xi)), xi, atol=1e-9)
        T = random_pose()
        assert np.allclose(T @ se3_exp(xi) @ np.linalg.inv(T), se3_exp(se3_adjoint(T) @ xi), atol=1e-9)
        T2 = random_pose()
        assert np.allclose(se3_adjoint(T @ T2), se3_adjoint(T) @ se3_adjoint(T2), atol=1e-9)


def test_covariance_needs_no_samples_and_is_symmetric():
    _, S = propagate_covariance(np.array([1.0, 0, 0, 0, 0, 0]), 10, np.full(6, 0.01))
    assert np.allclose(S, S.T) and np.all(np.linalg.eigvalsh(S) > 0)


def test_lesson1_claims_hold():
    box, pose = M["box"], M["pose"]
    assert box["eq5_max_error"] < 1e-12                                     # Eq. 5 is exact
    assert box["right_vs_left_deg"] > 30                                    # the two sides really differ
    assert np.allclose(box["nose_right"], box["nose_start"])                # right: it rolls about its nose
    assert box["nose_left"][2] > 0.5                                        # left: the nose lifts (pitch)
    gaps = box["gap_by_start_yaw_deg"]
    assert gaps["0"] < 1e-9 and gaps["30"] < gaps["60"] < gaps["90"] < gaps["180"]   # the knob
    assert pose["right_moved_m"] < 1e-12 and 0.8 < pose["left_moved_m"] < 0.9      # a left turn swings the pose


def test_lesson2_claims_hold():
    ex, ar, jac = M["example"], M["arrows"], M["jacobian"]
    assert np.allclose(ex["example_exact"], ex["example_jr"], atol=1e-4)    # J_r predicts it, up to second order
    assert abs(ex["example_tilt_deg"] + 45) < 0.5 and 0.89 < ex["example_shrink"] < 0.91   # half the angle
    lengths = [ar["arrow_length"][k] for k in ("0", "45", "90", "135", "180")]
    assert lengths == sorted(lengths, reverse=True) and abs(lengths[0] - 1) < 1e-12   # shrinks with |w|
    assert abs(lengths[-1] - 2 / np.pi) < 1e-9                              # sin(θ/2)/(θ/2) at 180°
    assert jac["plain_at_60deg"] > 1000 * jac["jr_at_60deg"]                # J_r removes the first-order error
    assert jac["plain_at_10deg"] > 0.05 and jac["plain_at_170deg"] > 0.5    # even small rotations need it
    assert jac["along_w_at_60deg"] < 1e-6                                   # one axis: turns add like numbers


def test_lesson3_claims_hold():
    one, many, ban, knob = M["one"], M["many"], M["banana"], M["knob"]
    assert one["cos_sin_vs_se3_max_m"] < 1e-12                              # the toy walk IS Eq. 9
    assert np.allclose(np.cumsum(one["turns_deg"]), one["facings_deg"][1:])  # the slips add up
    assert many["end_r_std_m"] < 0.1 < many["end_y_std_m"]                  # thin along r, wide sideways
    assert many["forgotten_end_y_std_m"] < 0.25 * many["end_y_std_m"]       # forgotten slips: no fan
    assert ban["off_xy"] > 3 * ban["off_se3"] and ban["off_xy"] > 0.35 and ban["off_se3"] < 0.2
    assert ban["off_separate"] > 2.5 * ban["off_se3"]                       # same numbers: SE(3) bends, SO(3)xR3 not
    xs, xt = ban["example_separate"], ban["example_together"]
    assert xt[0] < xs[0] - 0.3                                              # SE(3) curls the big-turn draw back
    assert 0.9 < ban["trace_ratio"] < 1.1 and 0.9 < ban["lateral_ratio"] < 1.1   # Eq. 10 is right ...
    assert ban["along_track_ratio"] > 5                                     # ... except along the track
    small, large = knob["1.0"], knob["6.0"]
    assert abs(small["off_separate"] - small["off_se3"]) < 0.02             # small heading doubt: they agree
    assert large["off_separate"] > 3 * large["off_se3"]                     # large: SE(3) wins
