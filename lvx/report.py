"""Experiment reports, the experiment registry and the README index.

Generated content sits between `<!-- lvx:begin NAME -->` and `<!-- lvx:end NAME -->`. render_*() is
deterministic (same spec + summary -> same text), so tools/check_reports.py can detect hand edits.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import config
from .evaluate import load_summary
from .spec import PHASES, Experiment, all_experiments

BLOCK_RE = re.compile(r"<!-- lvx:begin (?P<name>[\w:-]+) -->\n(?P<body>.*?)<!-- lvx:end (?P=name) -->", re.S)
SECTIONS = [
    "## Question & hypothesis", "## Setup", "## Results", "## Discussion", "## Verdict",
    "## Threats to validity", "## Failures", "## Reproduce",
]
HAND_WRITTEN = ["## Discussion", "## Verdict", "## Threats to validity", "## Failures"]
STATUS_BADGE = {
    "planned": "🗒️ planned", "approved": "🔒 approved (pre-registered)", "running": "⏳ running",
    "analysed": "📊 analysed", "concluded": "✅ concluded", "abandoned": "⛔ abandoned",
}
VERDICT_BADGE = {"adopt": "🟢 adopt", "reject": "🔴 reject", "inconclusive": "🟡 inconclusive"}


def _fmt(x: Optional[float], nd: int = 2) -> str:
    return "–" if x is None else f"{x:.{nd}f}"


# --- blocks -----------------------------------------------------------------------------------

def render_status(exp: Experiment) -> str:
    s = exp.spec
    deps = ", ".join(s.get("depends_on") or []) or "none"
    verdict = f" · verdict **{VERDICT_BADGE[s['verdict']]}**" if s.get("verdict") else ""
    return (f"**Status:** {STATUS_BADGE[s['status']]}{verdict} · **Phase:** {s['phase']} "
            f"({PHASES[s['phase']]}) · **System:** `{s['system']}` · **Depends on:** {deps}\n")


def render_hypothesis(exp: Experiment) -> str:
    s = exp.spec
    lock = "pre-registered" if exp.lock_path.exists() else "draft, not frozen yet"
    return (
        f"| | |\n|---|---|\n"
        f"| **Question** | {s['question'].strip()} |\n"
        f"| **Hypothesis** | {s['hypothesis'].strip()} |\n"
        f"| **Prediction** | {s['prediction'].strip()} |\n"
        f"| **Falsified if** | {s['falsified_if'].strip()} |\n"
        f"| **Decision rule** | {s['decision_rule'].strip()} |\n\n"
        f"<sub>Fields above are {lock} (`spec.lock`).</sub>\n"
    )


def _manifest_commits(exp: Experiment) -> Dict[str, List[str]]:
    out: Dict[str, set] = {"repo": set(), "system": set(), "host": set()}
    for p in sorted((exp.results / "manifests").glob("*.json")):
        with open(p) as f:
            m = json.load(f)
        out["repo"].add(m["repo"]["commit"][:10])
        out["system"].add(str(m["system_git"]["commit"])[:10])
        out["host"].add(m["host"])
    return {k: sorted(v) for k, v in out.items()}


def render_setup(exp: Experiment) -> str:
    s = exp.spec
    rows = [f"| `baseline` | {s['baseline']} as is |"]
    for v in s["variants"] or []:
        rows.append(f"| `{v['id']}` | {v['change']} |")
    commits = _manifest_commits(exp)
    run_info = (f"- **Commits:** repo {', '.join(commits['repo'])} · system {', '.join(commits['system'])}\n"
                if commits["repo"] else "- **Commits:** recorded per run once runs exist\n")
    stress = f"- **Stress profile:** `{s['stress']}`\n" if s.get("stress") else ""
    return (
        "| Variant | The one change |\n|---|---|\n" + "\n".join(rows) + "\n\n"
        f"- **Missions:** {', '.join(exp.missions())} (`{json.dumps(s['missions'])}`)\n"
        f"- **Repeats:** {s['repeats']} per variant × mission\n"
        f"- **Host:** `{s['host']}` (configs/hosts/{s['host']}.yaml)\n"
        f"- **Metrics:** primary `{s['metrics']['primary']}`, secondary "
        f"{', '.join(f'`{m}`' for m in s['metrics'].get('secondary') or []) or '–'}\n"
        + stress + run_info
    )


def render_results(exp: Experiment) -> str:
    summary = load_summary(exp)
    if summary is None:
        return f"> [!NOTE]\n> Not run yet (status `{exp.status}`). Numbers appear here after `lvx eval {exp.id}`.\n"
    primary = summary["primary"]
    lines = [f"Primary metric `{primary}`: mean ± std over repeats. Δ is against `baseline` on the same mission; "
             f"the effect is called only when |Δ| > {summary['noise_k']:g}σ of run-to-run noise "
             f"(σ from {summary['noise_source'] or 'this experiment'}).\n",
             "| Mission | Variant | " + primary + " | Δ | Effect | ms p95 | runs ok / failed |",
             "|---|---|---|---|---|---|---|"]
    for c in summary["cells"]:
        p = c[primary]
        effect = {"better": "🟢 better", "worse": "🔴 worse", "none": "⚪ within noise",
                  "no-noise-floor": "❔ no noise floor", None: ""}[c.get("effect")]
        delta = "" if c["variant"] == "baseline" else (f"{c['delta']:+.3f}" if c.get("delta") is not None else "–")
        lines.append(f"| {c['mission']} | `{c['variant']}` | {_fmt(p['mean'], 3)} ± {_fmt(p['std'], 3)} | {delta} | "
                     f"{effect} | {_fmt(c.get('ms_p95', {}).get('mean'), 1)} | {c['n_ok']} / {c['n_failed']} |")
    if not summary["complete"]:
        lines.append("\n> [!WARNING]\n> Incomplete: some planned runs are missing. No verdict may be drawn yet.")
    figs = [f for f in ("effect.png", "pareto.png", "error_time.png", "traj_top.png")
            if (exp.figures_dir / f).exists()]
    for f in figs:
        rel = os.path.relpath(exp.figures_dir / f, exp.report_path.parent).replace(os.sep, "/")
        lines.append(f"\n![{f[:-4]}]({rel})")
    return "\n".join(lines) + "\n"


def render_reproduce(exp: Experiment) -> str:
    text = (
        "```bash\n"
        f"lvx run {exp.id} --host {exp.spec['host']}     # every variant × mission × repeat, on the reference host\n"
        f"lvx eval {exp.id}                  # runs.csv + summary.json\n"
        f"lvx figures {exp.id}\n"
        f"lvx report {exp.id}\n"
        "```\n"
    )
    manifests = sorted((exp.results / "manifests").glob("*__r1.json"))
    if not manifests:
        return text
    text += "\nWhat `lvx run` executed for each variant (repeat 1; all runs are in `results/manifests/`):\n"
    seen = set()
    for path in manifests:
        man = json.loads(path.read_text())
        if man["variant"] in seen:
            continue
        seen.add(man["variant"])
        env = ", ".join(f"`${k}` = {v}" for k, v in man.get("env", {}).items())
        text += f"\n**{man['variant']}** (from `{man['cwd']}`; {env}):\n\n```bash\n{man['command']}\n```\n"
    return text


BLOCKS: Dict[str, Callable[[Experiment], str]] = {
    "status": render_status,
    "hypothesis": render_hypothesis,
    "setup": render_setup,
    "results": render_results,
    "reproduce": render_reproduce,
}


def _block(name: str, body: str) -> str:
    return f"<!-- lvx:begin {name} -->\n{body}<!-- lvx:end {name} -->"


def skeleton(exp: Experiment) -> str:
    s = exp.spec
    return f"""# {s['id']} — {s['title']}

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

{_block('status', render_status(exp))}

## Question & hypothesis

{_block('hypothesis', render_hypothesis(exp))}

## Setup

{_block('setup', render_setup(exp))}

## Results

{_block('results', render_results(exp))}

TODO up to 5 observations, each pointing at a table cell or figure.

## Discussion

TODO why it happened; link the theory in docs/explain/.

## Verdict

TODO adopt / reject / inconclusive, citing the decision rule.

## Threats to validity

TODO what could make this conclusion wrong.

## Failures

TODO failed or dirty runs and why (or "none").

## Reproduce

{_block('reproduce', render_reproduce(exp))}
"""


def update_blocks(text: str, renderers: Dict[str, Callable[[], str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        name = m.group("name")
        return _block(name, renderers[name]()) if name in renderers else m.group(0)
    return BLOCK_RE.sub(sub, text)


def write_report(exp: Experiment) -> Path:
    path = exp.report_path
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(skeleton(exp))
    else:
        path.write_text(update_blocks(path.read_text(), {k: (lambda f=f: f(exp)) for k, f in BLOCKS.items()}))
    return path


def report_drift(exp: Experiment) -> List[str]:
    """Blocks whose content differs from a fresh render (i.e. hand-edited or stale)."""
    if not exp.report_path.exists():
        return ["report missing"]
    text = exp.report_path.read_text()
    found = {m.group("name"): m.group("body") for m in BLOCK_RE.finditer(text)}
    bad = []
    for name, fn in BLOCKS.items():
        if name not in found:
            bad.append(f"block '{name}' missing")
        elif found[name] != fn(exp):
            bad.append(f"block '{name}' is stale or hand-edited (run `lvx report {exp.id}`)")
    return bad


# --- index (config.md + README) -------------------------------------------------------------

def _headline(exp: Experiment) -> str:
    summary = load_summary(exp)
    if not summary or exp.status != "concluded":
        return ""
    cells = [c for c in summary["cells"] if c["variant"] != "baseline" and c.get("delta") is not None]
    if not cells:
        return ""
    best = min(cells, key=lambda c: c["delta"])
    return f"best `{best['variant']}`: {best['delta']:+.3f} {summary['primary']} on {best['mission']}"


def render_index(link_prefix: str) -> str:
    rows = ["| ID | Question | Phase | Status | Verdict | Headline |", "|---|---|---|---|---|---|"]
    for e in all_experiments():
        link = f"{link_prefix}{e.name}.md"
        verdict = VERDICT_BADGE.get(e.spec.get("verdict") or "", "")
        rows.append(f"| [{e.id}]({link}) | {e.spec['title']} | {e.spec['phase']} | {STATUS_BADGE[e.status]} | "
                    f"{verdict} | {_headline(e)} |")
    return "\n".join(rows) + "\n"


def write_index() -> None:
    reg = config.REGISTRY
    body = ("# Experiment registry\n\nGenerated by `lvx report --index`. Do not edit by hand.\n\n"
            + _block("registry", render_index("../docs/experiments/")) + "\n")
    reg.write_text(body)
    for path, prefix in ((config.README, "docs/experiments/"), (config.REPORTS / "index.md", "")):
        if path.exists():
            path.write_text(update_blocks(path.read_text(), {"index": lambda p=prefix: render_index(p)}))


def index_drift() -> List[str]:
    bad = []
    expected = render_index("../docs/experiments/")
    if not config.REGISTRY.exists() or _block("registry", expected) not in config.REGISTRY.read_text():
        bad.append("experiments/config.md is stale (run `lvx report --index`)")
    for path, prefix in ((config.README, "docs/experiments/"), (config.REPORTS / "index.md", "")):
        if path.exists() and _block("index", render_index(prefix)) not in path.read_text():
            bad.append(f"{config.rel(path)} index block is stale (run `lvx report --index`)")
    return bad
