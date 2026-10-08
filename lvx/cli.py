"""`lvx` command line. Every command is safe to re-run; every state change goes through lvx.spec."""
from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import subprocess
import sys
from typing import List, Optional

import yaml

from . import config, report, spec


def cmd_exp_new(a: argparse.Namespace) -> None:
    if not spec.SLUG_RE.match(a.slug):
        raise SystemExit("slug must be kebab-case, e.g. chi2-gate-sweep")
    if a.phase not in spec.PHASES:
        raise SystemExit(f"phase must be one of {sorted(spec.PHASES)}")
    exp_id = spec.next_id()
    d = config.EXPERIMENTS / f"{exp_id}-{a.slug}"
    d.mkdir()
    with open(config.TEMPLATE / "spec.yaml") as f:
        data = yaml.safe_load(f)
    data.update(id=exp_id, slug=a.slug, phase=a.phase, created=_dt.date.today().isoformat(), status="planned")
    if a.supersedes:
        old = spec.find(a.supersedes)
        data["supersedes"] = old.id
        data["depends_on"] = sorted(set(old.spec.get("depends_on") or []))
    e = spec.Experiment(d, data)
    e.save()
    report.write_report(e)
    report.write_index()
    print(f"created {config.rel(d)}/spec.yaml and {config.rel(e.report_path)}; fill every TODO, then ask for approval")


def cmd_exp_freeze(a: argparse.Namespace) -> None:
    e = spec.find(a.exp)
    spec.freeze(e, approved_by=a.approved_by)
    report.write_report(e)
    report.write_index()
    print(f"{e.id} frozen (sha256 {spec.read_lock(e)['sha256'][:12]}), status approved")


def cmd_exp_conclude(a: argparse.Namespace) -> None:
    e = spec.find(a.exp)
    if e.status != "analysed":
        raise SystemExit(f"{e.id} is '{e.status}'; only 'analysed' experiments can be concluded")
    text = e.report_path.read_text()
    todo = [h for h in report.HAND_WRITTEN if h in text and "TODO" in text.split(h, 1)[1].split("\n## ", 1)[0]]
    if todo or "**TL;DR:** TODO" in text:
        raise SystemExit(f"write the report first; TODO left in: {todo or ['TL;DR']}")
    spec.set_status(e, "concluded", verdict=a.verdict)
    report.write_report(e)
    report.write_index()


def cmd_exp_abandon(a: argparse.Namespace) -> None:
    e = spec.find(a.exp)
    spec.set_status(e, "abandoned", reason=a.reason, **({"superseded_by": a.superseded_by} if a.superseded_by else {}))
    report.write_report(e)
    report.write_index()


def cmd_exp_list(a: argparse.Namespace) -> None:
    for e in spec.all_experiments():
        print(f"{e.id}  {e.status:10s} {e.spec['phase']}  {e.spec['title']}")


def cmd_run(a: argparse.Namespace) -> None:
    from . import runner

    e = spec.find(a.exp)
    if e.status not in ("approved", "running", "analysed"):
        raise SystemExit(f"{e.id} is '{e.status}': only approved (frozen) experiments run (CLAUDE.md law 2)")
    planned = runner.plan(e, a.variant, a.mission)
    pending = planned if a.dry_run else [k for k in planned if not (runner.run_dir(e, k) / "manifest.json").exists()]
    print(f"{e.id}: {len(pending)} run(s) to do")
    for k in pending:
        m = runner.execute(e, k, host_name=a.host or e.spec["host"], allow_dirty=a.allow_dirty, dry_run=a.dry_run)
        print(f"  {k.run_id}: {m['status']}" + (f" ({m.get('wall_s')} s)" if "wall_s" in m else ""))
        if a.dry_run:
            break


def cmd_eval(a: argparse.Namespace) -> None:
    from .evaluate import evaluate

    e = spec.find(a.exp)
    s = evaluate(e)
    print(f"{e.id}: {len(s['cells'])} cells, complete={s['complete']}, status {spec.find(a.exp).status}")


def cmd_figures(a: argparse.Namespace) -> None:
    from .figures import make

    for p in make(spec.find(a.exp)):
        print(config.rel(p))


def cmd_viewer(a: argparse.Namespace) -> None:
    from .viewer import make

    for p in make(spec.find(a.exp), [a.mission] if a.mission else None):
        print(config.rel(p))


def cmd_report(a: argparse.Namespace) -> None:
    if a.exp:
        print(config.rel(report.write_report(spec.find(a.exp))))
    if a.index or not a.exp:
        report.write_index()
        print(config.rel(config.REGISTRY))


def cmd_sync(a: argparse.Namespace) -> None:
    """Pull an experiment's (or chapter's) small, tracked results from the host that plays a profile."""

    h = config.host(a.host)
    if not shutil.which("rsync"):
        raise SystemExit("rsync not found")
    if a.target.startswith("EXP-"):
        e = spec.find(a.target)
        rels = [config.rel(e.dir) + "/", config.rel(e.figures_dir) + "/", config.rel(e.report_path)]
    else:
        from . import course
        rels = [f"course/chapters/{course.chapter_name(course.chapter(a.target))}/results/"]
    for rel in rels:
        src = f"{h['ssh']}:{h['repo']}/{rel}"
        subprocess.run(["rsync", "-a", "--mkpath", src, str(config.ROOT / rel)], check=False)
        print(f"synced {rel}")


def cmd_init(a: argparse.Namespace) -> None:

    values = {"data_root": a.data_root, "run_root": a.run_root}
    cfg = config.load()
    if a.dataset:
        ds = dict(cfg.get("datasets") or {})
        for item in a.dataset:
            name, _, where = item.partition("=")
            config.dataset_registry()[name]             # validates the name
            ds[name] = where
        values["datasets"] = ds
    if a.system:
        sy = dict(cfg.get("systems") or {})
        for item in a.system:
            key, _, val = item.partition("=")          # sad.root=/x  or  sad.image=localhost/sad:v1
            name, _, field = key.partition(".")
            sy.setdefault(name, {})[field] = val
        values["systems"] = sy
    if a.private_token:
        values["private_tokens"] = sorted(set((cfg.get("private_tokens") or []) + a.private_token))
    f = config.write_local(values)
    print(f"wrote {f.name} (git-ignored). Next: lvx data check")


def cmd_config(a: argparse.Namespace) -> None:

    if a.action == "show":
        f = config.local_file()
        print(f"# {f.name}: {'present' if f.exists() else 'missing (run lvx init)'}")
        print(yaml.safe_dump({k: v for k, v in config.load().items() if k != 'private_tokens'}, sort_keys=False))
        return
    getters = {"data-root": lambda n: config.data_root(), "run-root": lambda n: config.run_root(),
               "dataset": config.dataset_dir, "system-root": config.system_root, "image": config.image}
    print(getters[a.key](a.name))


def cmd_data_check(a: argparse.Namespace) -> None:

    for r in config.data_status():
        mark = "✅" if r["state"] == "ready" else "⬜"
        print(f"{mark} {r['name']:14s} {str(r['state'])[:40]:40s} used by {', '.join(r['used_by']) or '–'}")
    print("\nMissing data? docs/how-to/get-the-data.md has the official links; "
          "point lvx at a dataset with `lvx init --dataset <name>=<dir>`.")


def cmd_lab_list(a: argparse.Namespace) -> None:
    from . import course

    for lab_id, lab in course.labs().items():
        print(f"{lab_id:28s} {lab['chapter']}  {lab['status']:9s} {lab['dataset']:14s} {lab['app']} {lab['args']}")


def cmd_lab_run(a: argparse.Namespace) -> None:
    from . import course

    m = course.run_lab(a.lab, dry_run=a.dry_run)
    if not a.dry_run:
        where = config.rel(course.lab_results_dir(a.lab))
        print(f"{a.lab} r{m['repeat']}: {m['status']} in {m['wall_s']} s -> {where}")


def cmd_course_status(a: argparse.Namespace) -> None:
    """Which chapters can run on this machine: Build it (always), On real data, C++ labs."""
    from . import course

    ready = {}
    for name in config.dataset_registry():
        try:
            ready[name] = not config.dataset_missing(name)
        except SystemExit:
            ready[name] = False
    labs = course.labs()
    try:
        sad_ok = (config.system_root("sad") / "bin").is_dir()
    except SystemExit:
        sad_ok = False
    print(f"{'ID':4s} {'status':8s} {'real data':12s} {'C++ labs':10s} title")
    for c in course.chapters():
        ds = c.get("datasets") or []
        real = "–" if not ds else ("ready" if all(ready.get(d) for d in ds) else
                                   "need " + ",".join(d for d in ds if not ready.get(d)))
        ls = c.get("labs") or []
        lab = "–" if not ls else ("ready" if sad_ok and all(ready.get(labs[x]["dataset"]) for x in ls) else "blocked")
        print(f"{c['id']:4s} {c['status']:8s} {real:12s} {lab:10s} {c['title'][:70]}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lvx", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    exp = sub.add_parser("exp", help="experiment lifecycle").add_subparsers(dest="exp_cmd", required=True)
    x = exp.add_parser("new", help="create a planned experiment from the template")
    x.add_argument("slug")
    x.add_argument("--phase", required=True)
    x.add_argument("--supersedes")
    x.set_defaults(fn=cmd_exp_new)
    x = exp.add_parser("freeze", help="pre-register: hash the frozen fields, status -> approved")
    x.add_argument("exp")
    x.add_argument("--approved-by", required=True, help="who approved the spec (GitHub handle)")
    x.set_defaults(fn=cmd_exp_freeze)
    x = exp.add_parser("conclude", help="record the verdict (report must be written)")
    x.add_argument("exp")
    x.add_argument("--verdict", required=True, choices=spec.VERDICTS)
    x.set_defaults(fn=cmd_exp_conclude)
    x = exp.add_parser("abandon")
    x.add_argument("exp")
    x.add_argument("--reason", required=True)
    x.add_argument("--superseded-by")
    x.set_defaults(fn=cmd_exp_abandon)
    x = exp.add_parser("list")
    x.set_defaults(fn=cmd_exp_list)

    x = sub.add_parser("run", help="execute planned runs (append-only)")
    x.add_argument("exp")
    x.add_argument("--variant")
    x.add_argument("--mission")
    x.add_argument("--host")
    x.add_argument("--allow-dirty", action="store_true")
    x.add_argument("--dry-run", action="store_true", help="print the first manifest, run nothing")
    x.set_defaults(fn=cmd_run)
    x = sub.add_parser("eval", help="ATE + timing -> runs.csv, summary.json")
    x.add_argument("exp")
    x.set_defaults(fn=cmd_eval)
    x = sub.add_parser("figures", help="the standard figure set")
    x.add_argument("exp")
    x.set_defaults(fn=cmd_figures)
    x = sub.add_parser("viewer", help="3D viewer data: map + trajectories per mission (run on the host)")
    x.add_argument("exp")
    x.add_argument("--mission")
    x.set_defaults(fn=cmd_viewer)
    x = sub.add_parser("report", help="regenerate report blocks; --index for registry + README")
    x.add_argument("exp", nargs="?")
    x.add_argument("--index", action="store_true")
    x.set_defaults(fn=cmd_report)
    x = sub.add_parser("sync", help="pull an experiment's or chapter's results from the host (lvx.local.yaml hosts)")
    x.add_argument("target", help="EXP-NNN or a chapter id (B01)")
    x.add_argument("--host", default="reference", help="host profile; reached via lvx.local.yaml")
    x.set_defaults(fn=cmd_sync)
    x = sub.add_parser("init", help="write/update this machine's lvx.local.yaml (git-ignored)")
    x.add_argument("--data-root", help="folder holding the datasets (default layout: configs/datasets.yaml dir)")
    x.add_argument("--run-root", help="append-only run outputs")
    x.add_argument("--dataset", action="append", metavar="NAME=DIR",
                   help="a dataset somewhere else, e.g. sad-nclt=<dir>")
    x.add_argument("--system", action="append", metavar="NAME.FIELD=VALUE",
                   help="e.g. sad.root=<dir>, sad.image=<local tag>")
    x.add_argument("--private-token", action="append", metavar="WORD",
                   help="word that must never appear in tracked files (your user/host names)")
    x.set_defaults(fn=cmd_init)
    x = sub.add_parser("config", help="show the resolved machine configuration")
    x.add_argument("action", choices=["show", "get"])
    x.add_argument("key", nargs="?", choices=["data-root", "run-root", "dataset", "system-root", "image"])
    x.add_argument("name", nargs="?")
    x.set_defaults(fn=cmd_config)

    lab = sub.add_parser("lab", help="C++ labs on the official SAD code").add_subparsers(dest="lab_cmd", required=True)
    x = lab.add_parser("list")
    x.set_defaults(fn=cmd_lab_list)
    x = lab.add_parser("run", help="run one lab in a scratch sandbox and record its manifest")
    x.add_argument("lab")
    x.add_argument("--dry-run", action="store_true")
    x.set_defaults(fn=cmd_lab_run)
    data = sub.add_parser("data", help="datasets").add_subparsers(dest="data_cmd", required=True)
    x = data.add_parser("check", help="every dataset: where lvx looks, ready or missing, which chapters use it")
    x.set_defaults(fn=cmd_data_check)
    crs = sub.add_parser("course", help="the course").add_subparsers(dest="course_cmd", required=True)
    x = crs.add_parser("status", help="which chapters (real data, C++ labs) can run on this machine")
    x.set_defaults(fn=cmd_course_status)
    return p


def main(argv: Optional[List[str]] = None) -> None:
    a = build_parser().parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main(sys.argv[1:])
