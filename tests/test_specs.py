"""The committed specs are valid, and the lifecycle / lock rules hold."""
import copy

import pytest

from lvx import runner, spec


def test_all_committed_specs_validate():
    for e in spec.all_experiments():
        assert spec.validate(e) == [], e.id


def test_ids_are_unique_and_match_folders():
    ids = [e.id for e in spec.all_experiments()]
    assert len(ids) == len(set(ids))
    for e in spec.all_experiments():
        assert e.dir.name == f"{e.id}-{e.slug}"


def test_frozen_hash_changes_with_a_frozen_field_only():
    e = spec.find("EXP-001")
    h = spec.frozen_hash(e.spec)
    s2 = copy.deepcopy(e.spec)
    s2["code_change"] = "different"           # not frozen
    assert spec.frozen_hash(s2) == h
    s2["prediction"] = "something else"       # frozen
    assert spec.frozen_hash(s2) != h


def test_variant_with_two_changes_is_rejected(tmp_path):
    e = spec.find("EXP-001")
    bad = spec.Experiment(e.dir, copy.deepcopy(e.spec))
    bad.spec["variants"][0]["overrides"]["lio.max_iter"] = 6
    assert any("changes 2 things" in m for m in spec.validate(bad))


def test_status_transitions_are_enforced(tmp_path, monkeypatch):
    e = spec.find("EXP-001")
    tmp = spec.Experiment(tmp_path, copy.deepcopy(e.spec))
    with pytest.raises(SystemExit):
        spec.set_status(tmp, "concluded")      # planned -> concluded is not allowed
    spec.set_status(tmp, "abandoned", reason="test")
    assert tmp.spec["status"] == "abandoned"
    assert (tmp_path / "spec.yaml").exists()


def test_run_plan_includes_paired_baseline():
    e = spec.find("EXP-001")
    keys = runner.plan(e)
    variants = {k.variant for k in keys}
    assert "baseline" in variants and len(variants) == 1 + len(e.spec["variants"])
    assert len(keys) == len(variants) * len(e.missions()) * e.spec["repeats"]


def test_se3lvio_command_maps_overrides_to_flags():
    e = spec.find("EXP-001")
    cfg = runner.resolve_config(e, e.spec["variants"][0]["id"])
    cmd = runner.se3lvio_command(cfg, "arc-6", "EXP-001-x", cpus="0-3")
    assert "--set residual_gate_sigma=2.0" in cmd and "--lio-only" in cmd and "arc-6" in cmd


def test_commands_are_publishable_and_self_explaining():
    """Machine locations are $VARIABLES set at run time, so the recorded command is the one that ran."""
    e = spec.find("EXP-001")
    cmds = [runner.se3lvio_command(runner.resolve_config(e, "baseline"), "arc-6", "t", cpus="0-3"),
            runner.lightning_command("arc-6", cpus="0-3")]
    for cmd in cmds:
        assert "/home/" not in cmd and "/hdd/" not in cmd
        for var in ("OUT", "GRANDTOUR", "MISSION", "IMAGE", "LIGHTNING_WS", "BAG"):
            if f"${var}" in cmd:
                assert var in runner.ENV_MEANING
    assert '"$OUT/estimate.tum"' in cmds[1] and "--timing /out/timing.csv" in cmds[1]


def test_baseline_swap_variant_resolves_other_system():
    e = spec.find("EXP-000")
    cfg = runner.resolve_config(e, "ll_stock")
    assert cfg["system"] == "lightning-lm"
    assert cfg["config_hash"] != runner.resolve_config(e, "baseline")["config_hash"]
