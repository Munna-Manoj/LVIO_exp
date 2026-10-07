"""Repository and data locations. Code never hard-codes a path; it asks here."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = ROOT / "experiments"
TEMPLATE = EXPERIMENTS / "_template"
CONFIGS = ROOT / "configs"
BASELINES = CONFIGS / "baselines"
HOSTS = CONFIGS / "hosts"
MISSIONS_FILE = CONFIGS / "missions.yaml"
SYSTEMS_FILE = ROOT / "systems" / "systems.yaml"
DOCS = ROOT / "docs"
REPORTS = DOCS / "experiments"
FIGURES = DOCS / "assets" / "experiments"
REGISTRY = EXPERIMENTS / "registry.md"
README = ROOT / "README.md"
ROADMAP = ROOT / "ROADMAP.md"


def rel(path: Path) -> str:
    """Repo-relative POSIX path, the only form written into tracked files."""
    return Path(path).resolve().relative_to(ROOT).as_posix()
