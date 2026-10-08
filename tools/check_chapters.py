#!/usr/bin/env python3
"""Law 0: a learner can read one chapter alone (CLAUDE.md §0, §11; ADR-0010).

For every chapter folder course/chapters/<ID>-<slug>/ with a README.md:

  self-contained   imports only the standard library, ALLOWED third-party packages and files of the same
                   folder; no sys.path edits, no relative/package imports, no lvx, no other chapter
  plain code       no class inheritance, no decorators except @dataclass, files <= MAX_LINES lines
  maths <-> code   every equation numbered "\\qquad (n)" in README.md is cited as "(Eq. n)" in the code,
                   and every cited n exists
  honest numbers   results/output.txt exists and README.md quotes it verbatim in a ```text block;
                   every image README.md shows exists
  page shape       title line, the fixed sections in order, a test in tests/course/, an entry in mkdocs nav
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "course" / "chapters"
ALLOWED = {"numpy", "scipy", "matplotlib", "mpl_toolkits", "rosbags"}
MAX_LINES = 300
SECTIONS = ["## What you will build", "## Intuition", "## The math", "## Build it", "## See it", "## Break it",
            "## Run it in C++", "## On real data", "## In the real systems", "## Experiment hooks", "## Try it",
            "## Next"]
TAG = re.compile(r"\\qquad \((\d+)\)\s*$", re.M)   # end of a line inside a ```math fence
EQ_REF = re.compile(r"\(Eq\. (\d+)\)")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
STDLIB = set(getattr(sys, "stdlib_module_names", ())) or {  # Python < 3.10: the modules chapters need
    "__future__", "argparse", "bisect", "collections", "csv", "dataclasses", "functools", "glob", "heapq",
    "itertools", "json", "math", "os", "pathlib", "random", "sys", "time", "typing"}


def check_python(f: Path, siblings: set) -> list:
    errs = []
    src = f.read_text()
    rel = f.relative_to(ROOT) if ROOT in f.parents else f
    n = src.count("\n")
    if n > MAX_LINES:
        errs.append(f"{rel}: {n} lines > {MAX_LINES}; split it by concept (one file per idea), not into helpers")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.level:
            errs.append(f"{rel}:{node.lineno}: relative import; import a file of this folder by name")
        mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        for mod in mods:
            top = mod.split(".")[0]
            if top and top not in STDLIB and top not in ALLOWED and top not in siblings:
                errs.append(f"{rel}:{node.lineno}: imports '{mod}'. A chapter uses only the standard library, "
                            f"{sorted(ALLOWED)} and its own files; copy what you need from earlier chapters")
        if isinstance(node, ast.Attribute) and node.attr == "path" and getattr(node.value, "id", "") == "sys":
            errs.append(f"{rel}:{node.lineno}: sys.path edits are not allowed; the chapter runs from its folder")
        if isinstance(node, ast.ClassDef) and node.bases:
            errs.append(f"{rel}:{node.lineno}: class {node.name} inherits; use plain functions and arrays")
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            for d in node.decorator_list:
                name = d.id if isinstance(d, ast.Name) else getattr(d, "attr", "?")
                if name != "dataclass":
                    errs.append(f"{rel}:{node.lineno}: decorator @{name}; only @dataclass is allowed")
    return errs


def check_chapter(d: Path, entry: dict, nav: str) -> list:
    errs = []
    rel = d.relative_to(ROOT)
    readme = (d / "README.md").read_text()
    py = sorted(d.glob("*.py"))
    if not (d / "main.py").exists():
        errs.append(f"{rel}: main.py missing (`python main.py` from the folder runs the chapter)")
    siblings = {f.stem for f in py}
    code = ""
    for f in py:
        errs += check_python(f, siblings)
        code += f.read_text()

    tags, refs = set(TAG.findall(readme)), set(EQ_REF.findall(code))
    for n in sorted(tags - refs, key=int):
        errs.append(f"{rel}: README Eq. {n} (`\\qquad ({n})`) is never cited as '(Eq. {n})' in the code")
    for n in sorted(refs - tags, key=int):
        errs.append(f"{rel}: code cites (Eq. {n}) but README.md has no equation ending `\\qquad ({n})`")

    out = d / "results" / "output.txt"
    if not out.exists():
        errs.append(f"{rel}: results/output.txt missing (run `python main.py`)")
    elif f"```text\n{out.read_text()}```" not in readme:
        errs.append(f"{rel}: README.md must quote results/output.txt verbatim in a ```text block "
                    "(rerun main.py, paste the new output)")
    for img in IMAGE.findall(readme):
        if "://" not in img and not (d / img).exists():
            errs.append(f"{rel}: README.md shows {img}, which does not exist")

    cid = entry["id"]
    if not readme.startswith(f"# {cid} — "):
        errs.append(f"{rel}/README.md: first line must be '# {cid} — <title>'")
    wanted = [s for s in SECTIONS
              if (s != "## Run it in C++" or entry.get("labs"))
              and (s != "## On real data" or entry.get("kind") == "bridge" or f"\n{s}\n" in readme)]
    pos = [readme.find("\n" + s + "\n") for s in wanted]
    missing = [s for s, p in zip(wanted, pos) if p < 0]
    if missing:
        errs.append(f"{rel}/README.md: missing sections {missing}")
    elif pos != sorted(pos):
        errs.append(f"{rel}/README.md: sections out of order (CLAUDE.md §11)")
    if "TODO" in readme:
        errs.append(f"{rel}/README.md: TODO left")
    if not (ROOT / "tests" / "course" / f"test_{cid}.py").exists():
        errs.append(f"{rel}: tests/course/test_{cid}.py missing")
    if f"learn/{d.name}/index.md" not in nav:
        errs.append(f"{rel}: add `learn/{d.name}/index.md` to the nav in mkdocs.yml")
    if entry["status"] == "planned":
        errs.append(f"{rel}: has a README but curriculum status is 'planned' (set drafted/done)")
    return errs


def main() -> int:
    curriculum = yaml.safe_load((ROOT / "course" / "curriculum.yaml").read_text())
    entries = {f"{c['id']}-{c['slug']}": c for c in curriculum["chapters"]}
    nav = (ROOT / "mkdocs.yml").read_text()
    errors, n = [], 0
    for d in sorted(p for p in CHAPTERS.iterdir() if p.is_dir()):
        if d.name not in entries:
            errors.append(f"{d.relative_to(ROOT)}: not in course/curriculum.yaml")
        elif (d / "README.md").exists():
            n += 1
            errors += check_chapter(d, entries[d.name], nav)
        elif any(d.glob("*.py")):
            errors.append(f"{d.relative_to(ROOT)}: code without README.md; the README is the lesson")
    if errors:
        print(f"check_chapters: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print(f"check_chapters: OK ({n} chapter(s) readable on their own)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
