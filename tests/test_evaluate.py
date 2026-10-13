"""Noise-floor verdicts and timing parsing, on synthetic rows (no data, no evo needed)."""
import copy
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


def test_usable_scans_count_only_scans_inside_the_imu_span(tmp_path):
    (tmp_path / "lidar").mkdir()
    for t in (100, 200, 300, 400, 500):                         # ns, as the converter names scan files
        (tmp_path / "lidar" / f"{t}.bin").touch()
    (tmp_path / "imu.txt").write_text("150 0 0 0 0 0 9.8\n250 0 0 0 0 0 9.8\n420 0 0 0 0 0 9.8\n")
    assert evaluate.usable_scans(tmp_path) == 3                 # 200, 300, 400; the IMU stopped at 420


def test_each_baseline_takes_its_floor_from_the_experiment_that_measured_it():
    from lvx import evaluate
    assert evaluate.noise_source("se3lvio_S8") == "EXP-000"
    assert evaluate.noise_source("lightning_stock") == "EXP-000"
    assert evaluate.noise_source("not_a_baseline") is None
    assert evaluate.noise_source("genz_stock") == "EXP-022"         # not EXP-021, which is superseded



def _two_system_spec():
    s = copy.deepcopy(spec.find("EXP-001").spec)
    s["variants"] = [
        {"id": "gate_2p0", "change": "gate 2.0σ", "overrides": {"lio.residual_gate_sigma": 2.0}},
        {"id": "genz", "change": "GenZ-LIO stock", "baseline": "genz_stock"},
        {"id": "genz_gate_2p0", "change": "GenZ-LIO plane gate 2.0σ", "baseline": "genz_stock",
         "reference": "genz", "overrides": {"mapping.sigma_num": 2.0}},
    ]
    return s


def test_a_variant_is_paired_with_its_reference_and_its_own_noise_floor(tmp_path, monkeypatch):
    from lvx import evaluate
    measured = evaluate.noise_sigma
    monkeypatch.setattr(evaluate, "noise_sigma",                          # a fixed floor, not the repo's
                        lambda b: {m: 0.0 for m in ("arc-6", "eig-2", "snow-3")} if b == "genz_stock" else measured(b))
    d = tmp_path / "EXP-001-chi2-gate-sweep"
    d.mkdir()
    e = spec.Experiment(d, _two_system_spec())
    assert spec.validate(e) == []
    rows = []
    for v, ate in [("baseline", 1.0), ("gate_2p0", 0.9), ("genz", 2.0), ("genz_gate_2p0", 2.004)]:
        for m in e.missions():
            for _ in range(3):
                rows.append({"variant": v, "mission": m, "status": "ok", "ate_rmse_cm": ate, "ms_p95": 30.0})
    cells = {(c["variant"], c["mission"]): c for c in evaluate.summarise(e, rows)["cells"]}
    c = cells[("genz_gate_2p0", "arc-6")]
    assert c["reference"] == "genz" and abs(c["delta"] - 0.004) < 1e-9     # against GenZ-LIO stock, not S8
    assert c["sigma_noise"] == evaluate.SIGMA_MIN_CM and c["effect"] == "none"   # GenZ-LIO's floor: 0.004 < 2 x 0.005
    assert cells[("genz", "arc-6")]["reference"] == "baseline"             # the cross-system row stays as before


def test_reference_must_be_a_plain_swap_of_the_same_config(tmp_path):
    s = _two_system_spec()
    s["variants"][2]["baseline"] = "se3lvio_S9a"                         # not the reference's config
    assert any("same baseline config" in x for x in spec.validate(spec.Experiment(tmp_path, s)))
    s = _two_system_spec()
    del s["variants"][2]["reference"]                                    # swap + change against S8: two changes
    assert any("pair it with a plain swap" in x for x in spec.validate(spec.Experiment(tmp_path, s)))
