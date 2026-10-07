#!/usr/bin/env python3
"""Publish the course to the docs site, and keep the generated index tables in sync.

A chapter's lesson is its own `course/chapters/<ID>-<slug>/README.md`, written by hand and read on GitHub
as it is. This tool never edits a chapter. It only:

  1. copies each started chapter's README.md + results/ figures to docs/learn/<ID>-<slug>/ (git-ignored),
     rewriting links so they also work on the site: other repo files -> GitHub URLs, docs/ -> site pages;
  2. fills the generated tables  <!-- course:begin curriculum -->  in docs/learn/README.md and
     <!-- course:begin datasets -->  in docs/how-to/get-the-data.md, from the YAML that owns them.

--check: validate course/curriculum.yaml and fail if a generated table is stale. The chapter rules
themselves (self-contained, equations, results) are checked by tools/check_chapters.py.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lvx import course, registry  # noqa: E402

CHAPTERS = ROOT / "course" / "chapters"
SITE_LEARN = ROOT / "docs" / "learn"
REPO_URL = "https://github.com/Munna-Manoj/LVIO_exp/blob/main"
BLOCK = re.compile(r"<!-- course:begin (?P<name>\w+) -->\n(?P<body>.*?)<!-- course:end (?P=name) -->", re.S)
LINK = re.compile(r"(\]\()(?P<target>[^)#\s]+)(?P<rest>[^)]*\))")
STATUS_ICON = {"planned": "⬜", "drafted": "🟨", "done": "✅"}


def started():
    """Curriculum entries whose chapter folder has a README.md."""
    for c in course.chapters():
        if (CHAPTERS / course.chapter_name(c) / "README.md").exists():
            yield c


def _inside(path: Path, folder: Path) -> bool:
    try:
        path.relative_to(folder)
        return True
    except ValueError:
        return False


# --- 1. publish chapters --------------------------------------------------------------------------

def site_link(target: str, chapter: Path) -> str:
    """A link written for GitHub (relative to the chapter folder) -> the same link on the site."""
    if "://" in target or target.startswith("mailto:"):
        return target
    path = (chapter / target).resolve()
    if _inside(path, chapter / "results"):
        return target                                       # figures are copied next to the page
    if _inside(path, ROOT / "docs"):
        return "../../" + path.relative_to(ROOT / "docs").as_posix()
    if _inside(path, CHAPTERS) and path.name == "README.md":
        return f"../{path.parent.name}/index.md"
    return f"{REPO_URL}/{path.relative_to(ROOT).as_posix()}"


def publish() -> int:
    for d in SITE_LEARN.iterdir():
        if d.is_dir():
            shutil.rmtree(d)
    n = 0
    for c in started():
        chapter = CHAPTERS / course.chapter_name(c)
        dst = SITE_LEARN / chapter.name
        (dst / "results").mkdir(parents=True)
        text = (chapter / "README.md").read_text()
        text = LINK.sub(lambda m, here=chapter: m.group(1) + site_link(m["target"], here) + m["rest"], text)
        (dst / "index.md").write_text(text)
        for f in (chapter / "results").iterdir():
            if f.suffix in (".png", ".gif", ".svg", ".txt"):
                shutil.copy(f, dst / "results" / f.name)
        n += 1
    return n


# --- 2. generated tables ----------------------------------------------------------------------------

def render_curriculum() -> str:
    cur = course.curriculum()
    have = {c["id"] for c in started()}
    out = []
    for part, meta in cur["parts"].items():
        book = ", ".join(str(x) for x in meta["sad_chapters"]) or "–"
        out.append(f"### Part {part} · {meta['title']}  <sub>(SAD ch. {book})</sub>\n")
        out.append("| # | Chapter | Synthetic scene | Real data | Experiments | Status |\n|---|---|---|---|---|---|")
        for c in cur["chapters"]:
            if c["part"] != part:
                continue
            title = c["title"]
            if c["id"] in have:
                title = f"[{title}]({course.chapter_name(c)}/index.md)"
            if c.get("kind") == "bridge":
                title = f"🔗 {title}"
            scene = c.get("scene") or "–"
            data = ", ".join(d.replace("sad-", "") for d in c.get("datasets") or []) or "–"
            exps = ", ".join(f"[{e}](../experiments/{_exp_page(e)})" for e in c.get("experiments") or []) or "–"
            out.append(f"| {c['id']} | {title} | {scene} | {data} | {exps} | {STATUS_ICON[c['status']]} |")
        out.append("")
    out.append("🔗 = bridge chapter: not in the SAD book, needed for the capstone systems; always has an "
               "\"On real data\" step.\n")
    return "\n".join(out)


def render_datasets() -> str:
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


def fill_blocks(text: str) -> str:
    render = {"curriculum": render_curriculum, "datasets": render_datasets}
    return BLOCK.sub(lambda m: f"<!-- course:begin {m['name']} -->\n{render[m['name']]()}"
                               f"<!-- course:end {m['name']} -->", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate and report stale tables; write nothing")
    a = ap.parse_args()
    errors = list(course.validate())
    known = {course.chapter_name(c) for c in course.chapters()}
    for d in sorted(p for p in CHAPTERS.iterdir() if p.is_dir()):
        if d.name not in known:
            errors.append(f"course/chapters/{d.name}: not a chapter in course/curriculum.yaml")
    for page in (SITE_LEARN / "README.md", ROOT / "docs" / "how-to" / "get-the-data.md"):
        new = fill_blocks(page.read_text())
        if new != page.read_text():
            if a.check:
                errors.append(f"{page.relative_to(ROOT)}: generated table is stale (run `python tools/sync_course.py`)")
            else:
                page.write_text(new)
                print(f"updated {page.relative_to(ROOT)}")
    if errors:
        print(f"sync_course: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    if a.check:
        print("sync_course: OK")
    else:
        print(f"sync_course: published {publish()} chapter(s) to docs/learn/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
