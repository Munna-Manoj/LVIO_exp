"""Law 0 is enforced: tools/check_chapters.py rejects code a learner could not read on its own."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import check_chapters  # noqa: E402


def problems(tmp_path, code):
    f = tmp_path / "main.py"
    f.write_text(code)
    return " ".join(check_chapters.check_python(f, {"main", "propagate"}))


def test_plain_chapter_code_passes(tmp_path):
    assert problems(tmp_path, "import json\nimport numpy as np\nfrom propagate import propagate\n") == ""


def test_shared_packages_and_other_chapters_are_rejected(tmp_path):
    assert "imports 'lvx" in problems(tmp_path, "from lvx import plotstyle\n")
    assert "imports 'lvio_course'" in problems(tmp_path, "import lvio_course\n")
    assert "relative import" in problems(tmp_path, "from . import helpers\n")
    assert "sys.path" in problems(tmp_path, "import sys\nsys.path.insert(0, '..')\n")


def test_abstractions_are_rejected(tmp_path):
    assert "inherits" in problems(tmp_path, "class Filter(Base):\n    pass\n")
    assert "@lru_cache" in problems(tmp_path, "from functools import lru_cache\n@lru_cache\ndef f():\n    pass\n")
    assert "lines >" in problems(tmp_path, "x = 1\n" * 400)
