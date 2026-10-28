"""Shared Act theme adapter.

Single source of truth for every rendering backend. Reads `references/tokens.json` (the same
file the native python-pptx builder consumes as C/TS/LAY/CH) and exposes the Act palette, fonts,
and per-backend style config for Vega-Lite (act_vega) and Graphviz. No backend re-declares a colour.

Keeping colour/type in one file is what makes a native chart, a Vega-Lite chart image, and a
Graphviz diagram look like one deck.
"""
from __future__ import annotations

import json
from pathlib import Path

_TOKENS_PATH = Path(__file__).resolve().parent.parent / "references" / "tokens.json"

# The active template. build_deck calls use_template() so image assets (Vega-Lite charts,
# Graphviz diagrams) carry the SAME palette as the native slides, and the content-addressed
# asset cache is keyed by template — two templates that differ only in colour must not collide.
_TEMPLATE = "standard"
TOKENS = json.loads(_TOKENS_PATH.read_text())

# hex strings WITH leading '#', ready for Vega-Lite / Graphviz (native builder uses RGBColor)
COLORS = {k: "#" + v for k, v in TOKENS["colors"].items()}
FONTS = TOKENS["fonts"]
CHART = TOKENS["chart_style"]

# Latin from Geist, Japanese falls back to Noto Sans JP (the font-family list act_vega passes to Vega).
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
