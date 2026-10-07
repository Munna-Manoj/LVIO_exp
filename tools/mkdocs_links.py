"""MkDocs hook (mkdocs.yml `hooks:`): make Markdown written for GitHub work on the site.

Inline maths: GitHub's $`...`$ becomes MathJax's $...$ (display maths needs nothing: ```math fences are
mapped to MathJax in mkdocs.yml).

Links: authors write every link relative to the Markdown file's place in the repository, so it opens on GitHub
(tools/check_links.py enforces that). At build time each link is resolved the same way and sent to:

  course/chapters/<ID>/README.md or the folder    -> the published chapter page   learn/<ID>/index.md
  course/chapters/<ID>/results/<file>             -> the copy next to it          learn/<ID>/results/<file>
  docs/<page>                                     -> the same page on the site
  anything else in the repo (code, specs, ...)    -> the file on GitHub

Published chapter pages are copies (tools/sync_course.py), so their links resolve from the chapter folder.
"""
from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/Munna-Manoj/LVIO_exp"
LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
CHAPTER_PAGE = re.compile(r"^learn/([A-GXI]\d{2}-[a-z0-9-]+)/index\.md$")


def source_of(page_uri: str) -> PurePosixPath:
    """Where the page's Markdown lives in the repository."""
    m = CHAPTER_PAGE.match(page_uri)
    if m:
        return PurePosixPath("course/chapters") / m.group(1) / "README.md"
    return PurePosixPath("docs") / page_uri


def site_target(repo_path: str, page_uri: str) -> str:
    """A repository path -> the link to put on the site page `page_uri` (a URL or a page-relative path)."""
    parts = PurePosixPath(repo_path).parts
    if parts[:2] == ("course", "chapters") and len(parts) >= 3:
        rest = parts[3:]
        if not rest or rest == ("README.md",):
            target = f"learn/{parts[2]}/index.md"
        elif rest[0] == "results":
            target = "/".join(("learn", parts[2]) + rest)
        else:
            return f"{REPO_URL}/blob/main/{repo_path}"
    elif parts[:1] == ("docs",) and not repo_path.startswith("docs/process/"):
        target = "/".join(parts[1:])
    else:
        kind = "tree" if (ROOT / repo_path).is_dir() else "blob"
        return f"{REPO_URL}/{kind}/main/{repo_path}"
    return os.path.relpath(target, str(PurePosixPath(page_uri).parent)).replace(os.sep, "/")


def rewrite(markdown: str, page_uri: str) -> str:
    src_dir = source_of(page_uri).parent

    def fix(m: re.Match) -> str:
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            return m.group(0)
        path, _, anchor = target.partition("#")
        repo_path = os.path.normpath(str(src_dir / path)).replace(os.sep, "/")
        if repo_path.startswith(".."):
            return m.group(0)
        new = site_target(repo_path, page_uri) + (f"#{anchor}" if anchor else "")
        return m.group(1) + new + m.group(3)

    return LINK.sub(fix, markdown)


GITHUB_INLINE_MATH = re.compile(r"\$`([^`\n]+)`\$")


def on_page_markdown(markdown, page, config, files):  # noqa: ARG001 (MkDocs hook signature)
    markdown = GITHUB_INLINE_MATH.sub(r"$\1$", markdown)
    return rewrite(markdown, page.file.src_uri)
