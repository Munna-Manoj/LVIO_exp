#!/usr/bin/env python3
"""Governance: the tracked tree stays clean.

Fails on:
  - a top-level entry not in the allowlist (new top-level items need an ADR)
  - a tracked file over 2 MB that is not stored with Git LFS
  - machine-specific absolute paths (/home/x/, /hdd/x/, /Users/x/, /mnt/x/, /media/x/, C:\\...) in tracked text
  - any word from `private_tokens` in the local, git-ignored lvx.local.yaml (user and host names)
  - lvx.local.yaml itself being tracked
  - upstream lightning-lm sources in the tree (no licence, ADR-0003)
  - files under experiments/*/results/ that lvx does not write
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_TOP = {
    ".claude", ".github", ".gitignore", ".gitattributes", ".gitmodules", "CLAUDE.md", "CONTRIBUTING.md",
    "LICENSE", "LICENSING.md", "README.md", "ROADMAP.md", "CITATION.cff", "configs", "course", "docs", "experiments",
    "lvx", "mkdocs.yml", "pyproject.toml", "scripts", "systems", "tests", "tools", "web",
}
MAX_BYTES = 2 * 1024 * 1024
PERSONAL_PATH = re.compile(r"(?<![\w.])/(home|hdd|Users|mnt|media|srv)/[A-Za-z0-9_.-]+/|\b[A-Z]:\\\\[A-Za-z]")
LIGHTNING_OURS = re.compile(
    r"^systems/lightning-lm/(runner/run_lio_tum\.cc|offline_to_ros2bag\.py|Containerfile|README\.md|overrides/[^/]+\.yaml)$")
RESULTS_OK = re.compile(
    r"^experiments/EXP-\d{3}-[a-z0-9-]+/results/(runs\.csv|summary\.json|manifests/[^/]+\.json|traj/[^/]+\.tum\.gz)$")
COURSE_OK = re.compile(
    r"^course/(curriculum\.yaml|lvio_course/[\w/]+\.py|chapters/[A-GXI]\d{2}-[a-z0-9-]+/"
    r"(run\.py|results/(run\.txt|metrics\.json|labs/[a-z0-9-]+/(manifest\.json|log_tail\.txt))))$")
TEXT_SUFFIX = {".py", ".md", ".yaml", ".yml", ".toml", ".txt", ".cc", ".h", ".sh", ".json", ".csv", ".cff", ""}


def tracked() -> list:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         capture_output=True, text=True).stdout
    return [p for p in out.split("\0") if p]


def lfs_files() -> set:
    out = subprocess.run(["git", "-C", str(ROOT), "lfs", "ls-files", "-n"], capture_output=True, text=True)
    return set(out.stdout.split()) if out.returncode == 0 else set()


def private_tokens() -> list:
    sys.path.insert(0, str(ROOT))
    from lvx import config  # noqa: E402

    return config.private_tokens()


def check() -> list:
    errors = []
    files = tracked()
    tokens = [(t, re.compile(re.escape(t), re.I)) for t in private_tokens()]
    if "lvx.local.yaml" in files:
        errors.append("lvx.local.yaml is tracked: it is machine-specific (git rm --cached lvx.local.yaml)")
    lfs = lfs_files()
    for top in sorted({f.split("/", 1)[0] for f in files}):
        if top not in ALLOWED_TOP:
            errors.append(f"top-level '{top}' not allowed (add it via an ADR + ALLOWED_TOP)")
    for f in files:
        p = ROOT / f
        if not p.is_file():
            continue
        if p.stat().st_size > MAX_BYTES and f not in lfs:
            errors.append(f"{f}: {p.stat().st_size / 1e6:.1f} MB > 2 MB and not in Git LFS")
        if f.startswith("systems/lightning-lm/") and not LIGHTNING_OURS.match(f):
            errors.append(f"{f}: only our own lightning-lm files may be tracked (ADR-0003)")
        if f.startswith("course/") and not COURSE_OK.match(f):
            errors.append(f"{f}: course/ holds only lvio_course modules and chapter run.py + results (ADR-0007)")
        if re.match(r"^experiments/EXP-[^/]+/results/", f) and not RESULTS_OK.match(f):
            errors.append(f"{f}: not an lvx-written results file")
        if p.suffix in TEXT_SUFFIX and p.stat().st_size < MAX_BYTES and f != "tools/check_tree.py":
            try:
                text = p.read_text()
            except UnicodeDecodeError:
                continue
            m = PERSONAL_PATH.search(text)
            if m:
                errors.append(f"{f}: machine-specific path '{m.group(0)}' (name the dataset/system instead; "
                              "paths live in lvx.local.yaml)")
            for t, rx in tokens:
                if rx.search(text) or rx.search(f):
                    errors.append(f"{f}: contains private token '{t}' (from lvx.local.yaml private_tokens)")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print(f"check_tree: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print("check_tree: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
