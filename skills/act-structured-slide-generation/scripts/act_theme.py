"""Shared Act theme adapter.

Single source of truth for every rendering backend. Reads `references/tokens.json` (the same
file the native python-pptx builder consumes as C/TS/LAY/CH) and exposes the Act palette, fonts,
and per-backend style config for matplotlib and Graphviz. No backend re-declares a colour.

Keeping colour/type in one file is what makes a native table, a matplotlib chart image, and a
Graphviz diagram look like one deck.
"""
from __future__ import annotations

import json
from pathlib import Path

_TOKENS_PATH = Path(__file__).resolve().parent.parent / "references" / "tokens.json"

# The active template. build_deck calls use_template() so image assets (matplotlib charts,
# Graphviz diagrams) carry the SAME palette as the native slides, and the content-addressed
# asset cache is keyed by template — two templates that differ only in colour must not collide.
_TEMPLATE = "standard"
TOKENS = json.loads(_TOKENS_PATH.read_text())

# hex strings WITH leading '#', ready for matplotlib / Graphviz (native builder uses RGBColor)
COLORS = {k: "#" + v for k, v in TOKENS["colors"].items()}
FONTS = TOKENS["fonts"]
CHART = TOKENS["chart_style"]

# Latin from Geist, Japanese falls back to Noto Sans JP (matplotlib font fallback list).
FONT_STACK = [FONTS["latin"], FONTS["ea"]]

# Ordered categorical palette (primary → navy → accent → …), reused across backends.
SERIES_PALETTE = ["#" + c for c in CHART["comparison_series_colors"]]
NONFOCAL = COLORS["chart_gray"]


def use_template(name: str | None) -> None:
    """Switch the active design template so every image-asset backend recolours with it.

    Reassigns the module constants the chart/diagram functions read at call time (COLORS,
    CHART, SERIES_PALETTE, NONFOCAL, FONT_STACK). resolve_tokens keeps the leading/optical/font
    model fixed, so only colour and chart palette move — exactly what an image chart shows."""
    global _TEMPLATE, TOKENS, COLORS, FONTS, CHART, FONT_STACK, SERIES_PALETTE, NONFOCAL
    from deck_text import resolve_tokens
    _TEMPLATE = name or "standard"
    TOKENS = resolve_tokens(_TEMPLATE)
    COLORS = {k: "#" + v for k, v in TOKENS["colors"].items()}
    FONTS = TOKENS["fonts"]
    CHART = TOKENS["chart_style"]
    FONT_STACK = [FONTS["latin"], FONTS["ea"]]
    SERIES_PALETTE = ["#" + c for c in CHART["comparison_series_colors"]]
    NONFOCAL = COLORS["chart_gray"]


def tokens_hash() -> str:
    """Stable short hash of the ACTIVE theme, for content-addressed asset caching. Includes the
    template name so a navy chart and a teal chart from the same numbers get different cache keys."""
    import hashlib

    return hashlib.sha1(_TOKENS_PATH.read_bytes() + _TEMPLATE.encode()).hexdigest()[:12]


def fonts_present() -> list[str]:
    """Return the Act font families matplotlib cannot resolve (empty = all present)."""
    from matplotlib import font_manager as fm

    missing = []
    for fam in (FONTS["latin"], FONTS["ea"]):
        try:
            fm.findfont(fam, fallback_to_default=False)
        except Exception:
            missing.append(fam)
    return missing


def apply_matplotlib():
    """Apply the Act look to matplotlib rcParams and return the series palette.

    Calm surface, ink text, no top/right spines, no grid noise, direct labels preferred.
    """
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": COLORS["canvas"],
        "axes.facecolor": COLORS["canvas"],
        "savefig.facecolor": COLORS["canvas"],
        "text.color": COLORS["ink"],
        "axes.labelcolor": COLORS["ink_subtle"],
        "axes.edgecolor": COLORS["ink_faint"],
        "xtick.color": COLORS["ink"],
        "ytick.color": COLORS["ink_faint"],
        "font.family": FONT_STACK,
        "font.size": 15,
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 1.0,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "svg.fonttype": "none",
        "figure.dpi": 200,
    })
    return list(SERIES_PALETTE)


def graphviz_graph_attr() -> dict:
    return {"bgcolor": COLORS["canvas"], "fontname": FONTS["latin"],
            "fontcolor": COLORS["ink"], "rankdir": "TB", "nodesep": "0.35", "ranksep": "0.5"}


def graphviz_node_attr() -> dict:
    return {"shape": "box", "style": "filled,rounded", "fillcolor": COLORS["surface_tint"],
            "color": COLORS["rule"], "fontname": FONTS["ea"], "fontcolor": COLORS["ink"],
            "fontsize": "13", "penwidth": "1", "margin": "0.14,0.08"}


def graphviz_edge_attr() -> dict:
    return {"color": COLORS["ink_faint"], "fontname": FONTS["ea"],
            "fontcolor": COLORS["ink_subtle"], "fontsize": "11", "penwidth": "1",
            "arrowsize": "0.7"}
