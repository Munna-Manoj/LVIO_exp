import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def isolated_machine_config(tmp_path, monkeypatch):
    """Tests never read the developer's lvx.local.yaml or environment."""
    monkeypatch.setenv("LVX_CONFIG", str(tmp_path / "lvx.local.yaml"))
    for var in ("LVX_DATA_ROOT", "LVX_RUN_ROOT", "LVX_SAD_ROOT"):
        monkeypatch.delenv(var, raising=False)
    yield
    os.environ.pop("LVX_CONFIG", None)
