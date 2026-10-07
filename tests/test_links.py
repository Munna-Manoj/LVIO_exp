"""Links work in both places: on GitHub as written (check_links) and on the site after the hook rewrites them."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import mkdocs_links  # noqa: E402


def test_every_tracked_link_opens_on_github():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_links.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_course_map_links_to_the_chapter_on_github_and_on_the_site():
    md = "[B01](../../course/chapters/B01-imu-propagation/README.md)"
    assert mkdocs_links.rewrite(md, "learn/README.md") == "[B01](B01-imu-propagation/index.md)"


def test_chapter_page_links():
    page = "learn/B01-imu-propagation/index.md"         # published copy of course/chapters/B01-.../README.md
    out = mkdocs_links.rewrite("[e](../../../docs/experiments/EXP-010-x.md) ![f](results/a.png) "
                               "[c](propagate.py) [m](../../../docs/learn/README.md)", page)
    assert "[e](../../experiments/EXP-010-x.md)" in out
    assert "![f](results/a.png)" in out
    code_url = "https://github.com/Munna-Manoj/LVIO_exp/blob/main/course/chapters/B01-imu-propagation/propagate.py"
    assert f"[c]({code_url})" in out
    assert "[m](../README.md)" in out


def test_urls_and_anchors_are_untouched():
    md = "[a](https://example.org) [b](#intuition)"
    assert mkdocs_links.rewrite(md, "learn/README.md") == md
