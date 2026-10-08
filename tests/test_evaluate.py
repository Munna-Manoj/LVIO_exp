"""Noise-floor verdicts and timing parsing, on synthetic rows (no data, no evo needed)."""
import json

from lvx import evaluate, spec


def _rows(exp, values):
    rows = []
    for (v, m), xs in values.items():
        for i, x in enumerate(xs, 1):
            rows.append({"run_id": f"{v}__{m}__r{i}", "variant": v, "mission": m, "repeat": i, "status": "ok",
                         "ate_rmse_cm": x, "ms_p95": 40.0, "ate_max_cm": 2 * x, "inliers_mean": 1900.0})
    return rows


def test_effect_needs_more_than_two_sigma(monkeypatch):
    e = spec.find("EXP-001")
    missions = e.missions()                                  # every mission of the spec's set gets data
    monkeypatch.setattr(evaluate, "noise_sigma", lambda name: {m: 0.01 for m in missions})
    vals = {(v, m): [0.80, 0.81, 0.82] for v in e.variant_ids() for m in missions}
    for m in missions:
        vals[("gate_2p0", m)] = [0.86, 0.87, 0.88]          # +0.06 > 2σ -> worse
        vals[("gate_4p0", m)] = [0.80, 0.82, 0.83]          # +0.007 -> within noise
    s = evaluate.summarise(e, _rows(e, vals))
    for c in s["cells"]:
        want = {"gate_2p0": "worse", "gate_4p0": "none", "baseline": None}.get(c["variant"], "none")
        assert c["effect"] == want, c
    assert s["complete"]


def test_missing_noise_floor_is_flagged_not_guessed(monkeypatch):
    e = spec.find("EXP-001")
    monkeypatch.setattr(evaluate, "noise_sigma", lambda name: {})
    vals = {(v, m): [0.8, 0.8, 0.8] for v in e.variant_ids() for m in e.missions()}
    s = evaluate.summarise(e, _rows(e, vals))
    assert {c["effect"] for c in s["cells"] if c["variant"] != "baseline"} == {"no-noise-floor"}


def test_incomplete_runs_are_reported():
    e = spec.find("EXP-001")
    vals = {(v, "arc-6"): [0.8] for v in e.variant_ids()}   # 1 of 3 repeats
    s = evaluate.summarise(e, _rows(e, vals))
    assert not s["complete"]
    json.dumps(s)


def test_timing_parsing(tmp_path):
    p = tmp_path / "timing.csv"
    p.write_text("stamp,ms,rss_mb,leaf_m,inliers\n1,10,100,0.2,0\n2,20,120,0.2,2000\n3,30,110,0.2,1800\n")
    t = evaluate.timing(p)
    assert t["ms_mean"] == 20 and t["ms_max"] == 30 and t["rss_mb"] == 120 and t["inliers_mean"] == 1900
