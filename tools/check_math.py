#!/usr/bin/env python3
"""Maths in tracked Markdown uses only the forms GitHub renders correctly (checked on GitHub, 2026-10-07).

  display   a ```math fence, numbered with "\\qquad (n)" at the end of its line
  inline    $`...`$

Rejected, with what GitHub does to them:
  $$...$$    markdown eats the backslash of \\, \\; \\! so thin spaces become commas
  \\tag{n}   the equation is laid out one symbol per line (a vertical stack)
  $...$      inline maths with \\, or _ can be mangled into commas or italics

The site renders the same source: mkdocs.yml maps ```math to MathJax, and tools/mkdocs_links.py turns
$`...`$ into MathJax inline maths.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
GOOD_INLINE = re.compile(r"\$`[^`\n]+`\$")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
BARE_INLINE = re.compile(r"(?<![\\$\w])\$(?![\s$])[^$\n]*?[\\_^{}][^$\n]*?(?<![\s\\])\$(?![\w$])")


def problems(text: str):
    """(line number, message) for every maths form GitHub breaks."""
    fence, fence_is_math = "", False        # the open fence's marker (e.g. ```` closes only with ````)
    for n, line in enumerate(text.split("\n"), 1):
        m = FENCE.match(line)
        if m and not fence:
            fence, fence_is_math = m.group(1), m.group(2).strip() == "math"
            continue
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            fence = ""
            continue
        if fence:
            if fence_is_math and "\\tag{" in line:
                yield n, "\\tag{} inside ```math: GitHub stacks the symbols vertically; end the line with \\qquad (n)"
            continue
        line = GOOD_INLINE.sub("", line)
        line = CODE_SPAN.sub("", line)
        if "$$" in line:
            yield n, "$$...$$: GitHub turns \\, into commas; use a ```math fence"
        if "\\tag{" in line:
            yield n, "\\tag{}: GitHub stacks the symbols vertically; use \\qquad (n) in a ```math fence"
        if BARE_INLINE.search(line):
            yield n, "inline $...$: write $`...`$ so GitHub keeps \\, and _ intact"


def main() -> int:
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"], capture_output=True, text=True,
                           check=True).stdout.split()
    errors = [f"{f}:{n}: {msg}" for f in files if not f.startswith("systems/")
              for n, msg in problems((ROOT / f).read_text())]
    if errors:
        print(f"check_math: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print("check_math: OK (only ```math fences and $`...`$ inline maths)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
