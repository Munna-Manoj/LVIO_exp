"""lvx viewer helpers: the geometry is right and the files stay inside their budgets (no data needed)."""
import numpy as np

from lvx import viewer


def test_quat_to_R_matches_a_known_rotation():
    half = np.radians(90) / 2
    R = viewer.quat_to_R(np.array([[0.0, 0.0, np.sin(half), np.cos(half)]]))[0]   # 90 deg about z
    assert np.allclose(R @ [1, 0, 0], [0, 1, 0])


def test_rigid_fit_recovers_a_known_transform():
    rng = np.random.default_rng(0)
    t = np.arange(0, 60, 0.1)
    gt = np.c_[t, rng.normal(size=(len(t), 3)) * 5, np.zeros((len(t), 4))]
    c, s = np.cos(0.7), np.sin(0.7)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    est = gt.copy()
    est[:, 1:4] = (gt[:, 1:4] - [1, 2, 3]) @ R                    # est = R^T (gt - t): the fit must undo it
    R_fit, t_fit = viewer.rigid_fit(est, gt)
    assert np.allclose(est[:, 1:4] @ R_fit.T + t_fit, gt[:, 1:4], atol=1e-9)


def test_thin_respects_the_point_budget():
    pts = np.random.default_rng(1).uniform(0, 50, size=(200_000, 3))
    assert len(viewer.thin(pts, budget=20_000)) <= 20_000


def test_polyline_breaks_at_gt_gaps_and_samples_every_0p2_s():
    t = np.r_[np.arange(0, 1, 0.05), np.arange(5, 6, 0.05)]       # a 4 s gap
    line = viewer.polyline(np.c_[t, t, t], t, gap_s=1.0)
    assert line.count(None) == 1
    assert sum(p is not None for p in line) == 10                  # 5 per second, two 1 s pieces
