"""The one visual style for every figure in the repo. Figures never set colours or fonts themselves."""
from __future__ import annotations

from typing import Dict

GT = "#111111"
SYSTEM_COLORS: Dict[str, str] = {"se3-lvio": "#0f9d8a", "lightning-lm": "#e8710a"}
VARIANT_COLORS = ["#3b5bdb", "#c2255c", "#5f3dc4", "#2b8a3e", "#e67700", "#1098ad", "#862e9c", "#495057"]
NOISE_BAND = "#adb5bd"
BUDGET_10HZ_MS = 100.0
BUDGET_20HZ_MS = 50.0


def apply() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "legend.frameon": False,
    })


def variant_color(index: int, system: str = "se3-lvio") -> str:
    """index 0 is the baseline and takes the system colour."""
    return SYSTEM_COLORS.get(system, GT) if index == 0 else VARIANT_COLORS[(index - 1) % len(VARIANT_COLORS)]
