"""Experiment specs: schema, pre-registration lock, and the status lifecycle.

A spec is `experiments/EXP-NNN-<slug>/spec.yaml`. The pre-registered fields (FROZEN) are hashed into
`spec.lock` by `lvx exp freeze`; after that, any edit to them is a governance failure.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import config

STATUSES = ["planned", "approved", "running", "analysed", "concluded", "abandoned"]
PHASES = {
    "P0": "Foundation: baselines and noise floor",
    "P1": "Outliers and robustness",
    "P2": "Filter safeguards",
    "P3": "Map quality",
    "P4": "State formulation",
    "P5": "Camera and backend",
    "P6": "Stress tests",
    "P7": "Embedded real time",
    "PX": "Cross-system comparison",
}
VERDICTS = ["adopt", "reject", "inconclusive"]
METRICS = [
    "ate_rmse_cm", "ate_median_cm", "ate_max_cm", "ms_mean", "ms_p95", "ms_max", "rss_mb",
    "inliers_mean", "pose_coverage",
]
FROZEN = [
    "question", "hypothesis", "prediction", "falsified_if", "baseline", "variants", "missions",
    "repeats", "metrics", "decision_rule", "stress", "host",
]
REQUIRED = ["id", "slug", "title", "phase", "status", "created", "system", "depends_on"] + FROZEN
ID_RE = re.compile(r"^EXP-\d{3}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VARIANT_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")
TODO = "TODO"


@dataclass
class Experiment:
    dir: Path
    spec: Dict[str, Any]

    @property
    def id(self) -> str:
        return self.spec["id"]

    @property
    def slug(self) -> str:
        return self.spec["slug"]

    @property
    def name(self) -> str:
        return f"{self.id}-{self.slug}"

    @property
    def status(self) -> str:
        return self.spec["status"]

    @property
    def spec_path(self) -> Path:
        return self.dir / "spec.yaml"

    @property
    def lock_path(self) -> Path:
        return self.dir / "spec.lock"

    @property
    def results(self) -> Path:
        return self.dir / "results"

    @property
    def report_path(self) -> Path:
        return config.REPORTS / f"{self.name}.md"

    @property
    def figures_dir(self) -> Path:
        return config.FIGURES / self.id

    def variant_ids(self) -> List[str]:
        """Planned variants; the baseline is always run inside the experiment as variant `baseline`."""
        return ["baseline"] + [v["id"] for v in self.spec.get("variants") or []]

    def missions(self) -> List[str]:
        return config.resolve_missions(self.spec["missions"])

    def save(self) -> None:
        with open(self.spec_path, "w") as f:
            yaml.safe_dump(self.spec, f, sort_keys=False, allow_unicode=True, width=100)


def load(path: Path) -> Experiment:
    d = path if path.is_dir() else path.parent
    with open(d / "spec.yaml") as f:
        return Experiment(d, yaml.safe_load(f))


def all_experiments() -> List[Experiment]:
    return [load(p.parent) for p in sorted(config.EXPERIMENTS.glob("EXP-*/spec.yaml"))]


def find(exp_id: str) -> Experiment:
    for e in all_experiments():
        if e.id == exp_id or e.name == exp_id:
            return e
    raise SystemExit(f"no experiment {exp_id}")


def next_id() -> str:
    ids = [int(e.id[4:]) for e in all_experiments()]
    return f"EXP-{(max(ids) + 1 if ids else 0):03d}"


# --- pre-registration lock -------------------------------------------------------------------

def frozen_hash(spec: Dict[str, Any]) -> str:
    payload = json.dumps({k: spec.get(k) for k in FROZEN}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def read_lock(exp: Experiment) -> Optional[Dict[str, Any]]:
    if not exp.lock_path.exists():
        return None
    with open(exp.lock_path) as f:
        return yaml.safe_load(f)


def freeze(exp: Experiment, approved_by: str) -> None:
    if exp.status != "planned":
        raise SystemExit(f"{exp.id} is '{exp.status}', only 'planned' experiments can be frozen")
    errors = validate(exp, strict_todo=True)
    if errors:
        raise SystemExit("cannot freeze, fix the spec first:\n  " + "\n  ".join(errors))
    lock = {
        "id": exp.id,
        "frozen_at": _dt.date.today().isoformat(),
        "approved_by": approved_by,
        "sha256": frozen_hash(exp.spec),
        "fields": FROZEN,
    }
    with open(exp.lock_path, "w") as f:
        yaml.safe_dump(lock, f, sort_keys=False)
    set_status(exp, "approved")


# --- lifecycle ---------------------------------------------------------------------------------

ALLOWED = {
    "planned": {"approved", "abandoned"},
    "approved": {"running", "abandoned"},
    "running": {"analysed", "abandoned"},
    "analysed": {"running", "concluded", "abandoned"},  # back to running only to add missing repeats
    "concluded": set(),
    "abandoned": set(),
}


def set_status(exp: Experiment, new: str, **fields: Any) -> None:
    old = exp.status
    if new != old and new not in ALLOWED[old]:
        raise SystemExit(f"{exp.id}: status {old} -> {new} is not allowed")
    exp.spec["status"] = new
    history = exp.spec.setdefault("history", [])
    history.append({"date": _dt.date.today().isoformat(), "status": new, **fields})
    exp.spec.update({k: v for k, v in fields.items() if k in ("verdict", "reason", "superseded_by")})
    exp.save()


# --- validation --------------------------------------------------------------------------------

def _has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return TODO in value
    if isinstance(value, dict):
        return any(_has_todo(v) for v in value.values())
    if isinstance(value, list):
        return any(_has_todo(v) for v in value)
    return False


def validate(exp: Experiment, strict_todo: bool = False) -> List[str]:
    """Schema + cross-reference checks. strict_todo: TODO placeholders are errors (freeze time)."""
    s, err = exp.spec, []
    for k in REQUIRED:
        if k not in s:
            err.append(f"missing field '{k}'")
    if err:
        return err
    if not ID_RE.match(str(s["id"])):
        err.append(f"id '{s['id']}' must look like EXP-NNN")
    if not SLUG_RE.match(str(s["slug"])):
        err.append(f"slug '{s['slug']}' must be kebab-case")
    if exp.dir.name != f"{s['id']}-{s['slug']}":
        err.append(f"folder '{exp.dir.name}' must be '{s['id']}-{s['slug']}'")
    if s["phase"] not in PHASES:
        err.append(f"phase '{s['phase']}' not in {sorted(PHASES)}")
    if s["status"] not in STATUSES:
        err.append(f"status '{s['status']}' not in {STATUSES}")
    if s["system"] not in list(config.systems()) + ["both"]:
        err.append(f"system '{s['system']}' unknown")
    try:
        config.baseline(s["baseline"])
    except ValueError as e:
        err.append(str(e))
    try:
        exp.missions()
    except ValueError as e:
        err.append(str(e))
    try:
        config.host_profile(s["host"])
    except ValueError as e:
        err.append(str(e))
    if s.get("stress") and s["stress"] not in (config.stress_profiles()):
        err.append(f"stress profile '{s['stress']}' not in configs/stress.yaml")
    for link in s.get("learn_links") or []:
        if not (config.ROOT / link).exists():
            err.append(f"learn_links '{link}' does not exist")
    if not isinstance(s["repeats"], int) or s["repeats"] < 1:
        err.append("repeats must be a positive integer")
    m = s["metrics"] or {}
    if m.get("primary") not in METRICS:
        err.append(f"metrics.primary must be one of {METRICS}")
    for x in m.get("secondary") or []:
        if x not in METRICS:
            err.append(f"metrics.secondary '{x}' unknown")
    seen = set()
    for v in s["variants"] or []:
        vid = v.get("id", "")
        if not VARIANT_RE.match(vid) or vid == "baseline":
            err.append(f"variant id '{vid}' must be snake_case and not 'baseline'")
        if vid in seen:
            err.append(f"duplicate variant id '{vid}'")
        seen.add(vid)
        if not v.get("change"):
            err.append(f"variant '{vid}' needs a one-line `change`")
        n_changes = len(v.get("overrides") or {}) + len(v.get("modes_add") or []) + len(v.get("modes_remove") or [])
        n_changes += 1 if v.get("baseline") else 0
        if n_changes == 0:
            err.append(f"variant '{vid}' changes nothing")
        if n_changes > 1 and not v.get("single_change_reason"):
            err.append(f"variant '{vid}' changes {n_changes} things; split it or give `single_change_reason`")
    if not s["variants"] and s["phase"] != "P0":
        err.append("only P0 experiments may have no variants")
    for dep in s["depends_on"] or []:
        if not ID_RE.match(str(dep)):
            err.append(f"depends_on '{dep}' is not an experiment id")
    if strict_todo:
        for k in FROZEN:
            if _has_todo(s.get(k)):
                err.append(f"'{k}' still contains {TODO}")
    if s["status"] == "concluded" and s.get("verdict") not in VERDICTS:
        err.append(f"concluded experiment needs verdict in {VERDICTS}")
    if s["status"] == "abandoned" and not s.get("reason"):
        err.append("abandoned experiment needs a reason")
    return err
