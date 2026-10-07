#!/usr/bin/env python3
"""Governance: every experiment has a report of the fixed shape, generated blocks are untouched, and the
registry / README index are in sync.

Fails on:
  - missing report, missing or out-of-order sections (lvx.report.SECTIONS)
  - generated `lvx:` blocks that differ from a fresh render (hand edits or stale results)
  - TODO left in the TL;DR or a hand-written section of a concluded experiment
  - MkDocs-only syntax (`///`, `!!!`, `{* ... *}`) in reports or README (they must render on GitHub too)
  - images referenced by a report that do not exist
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lvx import config, report, spec  # noqa: E402

MKDOCS_ONLY = re.compile(r"^(///|!!! |\?\?\? )|\{\* .* \*\}", re.M)
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")


def check() -> list:
    errors = []
    for e in spec.all_experiments():
        where = config.rel(e.report_path) if e.report_path.exists() else e.report_path.name
        if not e.report_path.exists():
            errors.append(f"{e.id}: report {e.report_path.name} missing (lvx report {e.id})")
            continue
        text = e.report_path.read_text()
        if not text.startswith(f"# {e.id} — "):
            errors.append(f"{where}: first line must be '# {e.id} — <title>'")
        pos = [text.find("\n" + h + "\n") for h in report.SECTIONS]
        missing = [h for h, p in zip(report.SECTIONS, pos) if p < 0]
        if missing:
            errors.append(f"{where}: missing sections {missing}")
        elif pos != sorted(pos):
            errors.append(f"{where}: sections out of order (expected {report.SECTIONS})")
        errors += [f"{where}: {m}" for m in report.report_drift(e)]
        if e.status == "concluded":
            if "**TL;DR:** TODO" in text:
                errors.append(f"{where}: TL;DR still TODO")
            for h in report.HAND_WRITTEN:
                body = text.split("\n" + h + "\n", 1)[-1].split("\n## ", 1)[0]
                if "TODO" in body:
                    errors.append(f"{where}: '{h}' still contains TODO")
        if MKDOCS_ONLY.search(text):
            errors.append(f"{where}: MkDocs-only syntax; use GitHub alerts (> [!NOTE]) instead")
        for img in IMG.findall(text):
            if not img.startswith("http") and not (e.report_path.parent / img).resolve().exists():
                errors.append(f"{where}: image {img} not found")
    errors += report.index_drift()
    if config.README.exists() and MKDOCS_ONLY.search(config.README.read_text()):
        errors.append("README.md: MkDocs-only syntax")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print(f"check_reports: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print(f"check_reports: OK ({len(spec.all_experiments())} reports)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
