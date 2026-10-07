#!/usr/bin/env python3
"""Keep course pages in sync with the code and results they show; with --check, fail on any drift.

A chapter page (docs/learn/<ID>-<slug>.md) never contains hand-copied code, output or result numbers.
Three markers are filled from the chapter folder course/chapters/<ID>-<slug>/:

  <!-- snippet:begin run.py#simulate -->      region `# [snippet:simulate]` ... `# [/snippet]` of run.py
  <!-- snippet:end -->
  <!-- output:begin results/run.txt -->       the captured stdout of run.py
  <!-- output:end -->
  <!-- m:rms_position_error_m/gyro noise/20s|.2f -->1.38<!-- /m -->   one number from results/metrics.json

Generated blocks (from course/curriculum.yaml and recorded lab manifests):
  <!-- course:begin book --> ... <!-- course:end book -->           on a chapter: SAD book chapter, code, apps
  <!-- course:begin labs --> ... <!-- course:end labs -->           on a chapter: its C++ labs and their records
  <!-- course:begin curriculum --> ... <!-- course:end curriculum --> on docs/learn/README.md: the course tables

--check also verifies the curriculum and the chapter contract: sections in order, results present, a test exists.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lvx import course, registry  # noqa: E402

CHAPTERS = ROOT / "course" / "chapters"
PAGES = ROOT / "docs" / "learn"
TESTS = ROOT / "tests" / "course"
SECTIONS = ["## What you will build", "## Intuition", "## The math", "## Build it", "## See it", "## Break it",
            "## Run it in C++", "## On real data", "## In the real systems", "## Experiment hooks", "## Try it",
            "## Next"]
LAB_SECTION = "## Run it in C++"     # required only for chapters with SAD labs
REAL_SECTION = "## On real data"     # required for bridge chapters, optional elsewhere (order still enforced)
BLOCK = re.compile(r"<!-- course:begin (?P<name>\w+) -->\n(?P<body>.*?)<!-- course:end (?P=name) -->", re.S)
SAD_BOOK = "https://github.com/gaoxiang12/slam-in-ad-en/blob/main/sad-en.pdf"
SAD_CODE = "https://github.com/gaoxiang12/slam_in_autonomous_driving/tree/master/src"
STATUS_ICON = {"planned": "⬜", "drafted": "🟨", "done": "✅"}
SNIPPET = re.compile(r"(<!-- snippet:begin (?P<src>[^#\s]+)#(?P<name>[\w-]+) -->\n)(?P<body>.*?)(<!-- snippet:end -->)",
                     re.S)
OUTPUT = re.compile(r"(<!-- output:begin (?P<src>\S+) -->\n)(?P<body>.*?)(<!-- output:end -->)", re.S)
METRIC = re.compile(r"(<!-- m:(?P<key>[^|]+)\|(?P<fmt>[^ ]+) -->)(?P<body>.*?)(<!-- /m -->)")


def region(path: Path, name: str) -> str:
    text = path.read_text()
    m = re.search(rf"^[ \t]*# \[snippet:{re.escape(name)}\]\n(.*?)^[ \t]*# \[/snippet\]", text, re.S | re.M)
    if not m:
        raise SystemExit(f"{path}: no snippet region '{name}'")
    return textwrap.dedent(m.group(1))


def lookup(metrics: dict, key: str):
    node = metrics
    for part in key.split("/"):
        node = node[part]
    return node


def render(page: Path, chapter: Path, c: dict) -> str:
    text = fill_blocks(page.read_text(), c)
    text = SNIPPET.sub(lambda m: m.group(1) + "```python\n" + region(chapter / m["src"], m["name"]) + "```\n"
                       + m.group(5), text)
    text = OUTPUT.sub(lambda m: m.group(1) + "```text\n" + (chapter / m["src"]).read_text() + "```\n" + m.group(4),
                      text)
    metrics_path = chapter / "results" / "metrics.json"
    if METRIC.search(text):
        metrics = json.loads(metrics_path.read_text())
        text = METRIC.sub(lambda m: m.group(1) + format(lookup(metrics, m["key"]), m["fmt"]) + m.group(5), text)
    return text


def chapters():
    """(chapter dir, page, curriculum entry) for every chapter that has started (dir exists or not planned)."""
    for c in course.chapters():
        d = CHAPTERS / course.chapter_name(c)
        if c["status"] != "planned" or (d / "run.py").exists():
            yield d, PAGES / f"{course.chapter_name(c)}.md", c


def render_book(c: dict) -> str:
    sad = c.get("sad")
    data = ", ".join(f"`{d}`" for d in c.get("datasets") or []) or "synthetic only"
    if c.get("kind") == "bridge":
        return (f"> [!IMPORTANT]\n> **Bridge chapter:** the SAD book does not cover this, but the systems in the "
                f"capstone depend on it. Real data used here: {data} ([Get the data](../how-to/get-the-data.md)).\n")
    if not sad:
        return (f"> [!NOTE]\n> Beyond the SAD book: this chapter has no book counterpart. "
                f"Real data used here: {data}.\n")
    apps = ", ".join(f"`{a}`" for a in sad.get("apps", [])) or "–"
    return (f"> [!NOTE]\n> **Book companion:** *SLAM in Autonomous Driving*, chapter {sad['chapter']} "
            f"([English PDF]({SAD_BOOK})) · code [`src/ch{sad['chapter']}`]({SAD_CODE}/ch{sad['chapter']}) · "
            f"apps {apps}. Read the book chapter for the full derivation; this page builds the idea "
            f"from scratch and connects it to the study.\n")


def render_labs(c: dict) -> str:
    labs = course.labs()
    rows = ["| Lab | App + arguments | Dataset | Last recorded run |", "|---|---|---|---|"]
    for lab_id in c.get("labs") or []:
        lab = labs[lab_id]
        rec = CHAPTERS / course.chapter_name(c) / "results" / "labs" / lab_id / "manifest.json"
        if rec.exists():
            m = json.loads(rec.read_text())
            last = f"{m['status']}, {m['wall_s']:.0f} s, SAD `{m['sad_commit'][:7]}`, {m['ended'][:10]}"
        else:
            last = "not recorded yet"
        rows.append(f"| `{lab_id}` | `{lab['app']} {lab['args']}`".rstrip() + f" | {lab['dataset']} | {last} |")
    return ("\n".join(rows) + "\n\n```bash\n" + "\n".join(f"lvx lab run {x}" for x in c.get("labs") or [])
            + "\n```\n")


def render_curriculum() -> str:
    cur = course.curriculum()
    out = []
    for part, meta in cur["parts"].items():
        book = ", ".join(str(x) for x in meta["sad_chapters"]) or "–"
        out.append(f"### Part {part} · {meta['title']}  <sub>(SAD ch. {book})</sub>\n")
        out.append("| # | Chapter | You build | C++ labs | Real data | Experiments | Status |\n"
                   "|---|---|---|---|---|---|---|")
        for c in cur["chapters"]:
            if c["part"] != part:
                continue
            title = c["title"]
            if c["status"] != "planned":
                title = f"[{title}]({course.chapter_name(c)}.md)"
            if c.get("kind") == "bridge":
                title = f"🔗 {title}"
            data = ", ".join(d.replace("sad-", "") for d in c.get("datasets") or []) or "–"
            builds = ", ".join(f"`{b}`" for b in c.get("builds") or []) or "–"
            labs = str(len(c.get("labs") or [])) if c.get("labs") else "–"
            exps = ", ".join(f"[{e}](../experiments/{_exp_page(e)})" for e in c.get("experiments") or []) or "–"
            out.append(f"| {c['id']} | {title} | {builds} | {labs} | {data} | {exps} | {STATUS_ICON[c['status']]} |")
        out.append("")
    out.append("🔗 = bridge chapter: not in the SAD book, needed for the capstone systems; always has an "
               "\"On real data\" step.\n")
    return "\n".join(out)


def render_datasets() -> str:
    """The dataset table of docs/how-to/get-the-data.md, from configs/datasets.yaml."""
    reg = registry.load_yaml(ROOT / "configs" / "datasets.yaml")["datasets"]
    rows = ["| Dataset | What | Size | Put it in (default) | Files lvx checks | Used by |", "|---|---|---|---|---|---|"]
    for name, d in reg.items():
        size = f"{d['size_gb']} GB" if "size_gb" in d else f"~{d.get('size_gb_per_mission', '?')} GB / mission"
        link = d.get("official") or d.get("huggingface")
        what = f"{d['title']}" + (f" ([official]({link}))" if link else "")
        where = "(ships with SAD)" if name == "sad-builtin" else f"`<data_root>/{d['dir']}/`"
        used = ", ".join(d.get("used_by") or []) or "– (extra)"
        files = ", ".join(f"`{x}`" for x in d.get("files") or []) or "–"
        rows.append(f"| `{name}` | {what} | {size} | {where} | {files} | {used} |")
    return "\n".join(rows) + "\n"


def _exp_page(exp_id: str) -> str:
    hits = sorted((ROOT / "docs" / "experiments").glob(f"{exp_id}-*.md"))
    return hits[0].name if hits else "index.md"


def fill_blocks(text: str, c=None) -> str:
    def sub(m):
        name = m["name"]
        body = {"book": lambda: render_book(c), "labs": lambda: render_labs(c),
                "curriculum": render_curriculum, "datasets": render_datasets}[name]()
        return f"<!-- course:begin {name} -->\n{body}<!-- course:end {name} -->"
    return BLOCK.sub(sub, text)


def check_contract(chapter: Path, page: Path, c: dict) -> list:
    errs = []
    cid = c["id"]
    if not page.exists():
        return [f"{chapter.name}: page {page.relative_to(ROOT)} missing"]
    text = page.read_text()
    if not text.startswith(f"# {cid} — "):
        errs.append(f"{page.name}: first line must be '# {cid} — <title>'")
    bridge = c.get("kind") == "bridge"
    sections = [x for x in SECTIONS
                if (x != LAB_SECTION or c.get("labs"))
                and (x != REAL_SECTION or bridge or f"\n{REAL_SECTION}\n" in text)]
    pos = [text.find("\n" + x + "\n") for x in sections]
    missing = [x for x, p in zip(sections, pos) if p < 0]
    if missing:
        errs.append(f"{page.name}: missing sections {missing}")
    elif pos != sorted(pos):
        errs.append(f"{page.name}: sections out of order")
    for f in ("run.py", "results/run.txt", "results/metrics.json"):
        if not (chapter / f).exists():
            errs.append(f"{chapter.name}: {f} missing (run `python course/chapters/{chapter.name}/run.py`)")
    if not (TESTS / f"test_{cid}.py").exists():
        errs.append(f"{chapter.name}: tests/course/test_{cid}.py missing")
    if "TODO" in text:
        errs.append(f"{page.name}: TODO left")
    for block in ("book",) + (("labs",) if c.get("labs") else ()):
        if f"<!-- course:begin {block} -->" not in text:
            errs.append(f"{page.name}: generated block '{block}' missing")
    if c["status"] == "planned":
        errs.append(f"{cid}: has a chapter folder but curriculum status is 'planned' (set drafted/done)")
    return errs


def _sync(page: Path, new: str, check: bool, errors: list) -> None:
    if new == page.read_text():
        return
    if check:
        errors.append(f"{page.relative_to(ROOT)}: out of sync (run `python tools/sync_course.py`)")
    else:
        page.write_text(new)
        print(f"synced {page.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    errors, n = list(course.validate()), 0
    known = {course.chapter_name(c) for c in course.chapters()}
    for d in sorted(p for p in CHAPTERS.iterdir() if p.is_dir()):
        if d.name not in known:
            errors.append(f"course/chapters/{d.name}: not a chapter in course/curriculum.yaml")
    targets = [(c, p, e) for c, p, e in chapters()]
    for chapter, page, c in targets:
        n += 1
        errs = check_contract(chapter, page, c)
        if errs:
            errors += errs
            continue
        _sync(page, render(page, chapter, c), a.check, errors)
    for page in (PAGES / "README.md", ROOT / "docs" / "how-to" / "get-the-data.md"):
        _sync(page, fill_blocks(page.read_text()), a.check, errors)
    if errors:
        print(f"sync_course: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print(f"sync_course: OK ({n} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
