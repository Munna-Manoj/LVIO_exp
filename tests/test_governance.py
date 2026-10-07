"""The checkers pass on the committed tree and catch the violations they exist for."""
import copy

import yaml

from lvx import report, spec
from tools import check_experiments, check_reports


def test_checkers_pass_on_repo():
    assert check_experiments.check() == []
    assert check_reports.check() == []


def test_edit_after_freeze_is_detected(tmp_path, monkeypatch):
    e = spec.find("EXP-001")
    tmp = spec.Experiment(tmp_path, copy.deepcopy(e.spec))
    tmp.spec["status"] = "approved"
    (tmp_path / "spec.lock").write_text(yaml.safe_dump({"sha256": spec.frozen_hash(tmp.spec)}))
    assert spec.read_lock(tmp)["sha256"] == spec.frozen_hash(tmp.spec)
    tmp.spec["hypothesis"] = "rewritten after seeing data"
    assert spec.read_lock(tmp)["sha256"] != spec.frozen_hash(tmp.spec)


def test_hand_edited_block_is_detected(tmp_path, monkeypatch):
    e = spec.find("EXP-001")
    text = e.report_path.read_text().replace("| **Question** |", "| **Question (edited)** |")
    fake = tmp_path / e.report_path.name
    fake.write_text(text)
    monkeypatch.setattr(spec.Experiment, "report_path", property(lambda self: fake))
    assert any("hypothesis" in m for m in report.report_drift(e))


def test_reproduce_shows_the_exact_recorded_command(tmp_path):
    import json
    import shutil
    src = spec.find("EXP-001").dir
    shutil.copytree(src, tmp_path / src.name)
    e = spec.load(tmp_path / src.name)
    (e.results / "manifests").mkdir(parents=True)
    man = {"variant": "baseline", "cwd": "systems/se3-lvio", "env": {"GRANDTOUR": "dataset `grandtour`"},
           "command": 'DATA="$GRANDTOUR" CPUSET=0-3 bash scripts/run_se3lio.sh arc-6 --tag t --lio-only'}
    (e.results / "manifests" / "baseline__arc-6__r1.json").write_text(json.dumps(man))
    text = report.render_reproduce(e)
    assert man["command"] in text and "`$GRANDTOUR` = dataset `grandtour`" in text
