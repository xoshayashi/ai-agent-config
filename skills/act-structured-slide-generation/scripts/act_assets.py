"""Image-asset backend for the Act slide engine.

Renders Act-styled, deterministic, headless graphics that the native python-pptx track cannot
draw — combo/dual-axis and other chart types via matplotlib, relationship graphs via Graphviz,
schematic diagrams (ring/funnel/pyramid/Venn) via matplotlib — and returns a PNG path the
builder embeds with `add_picture`.

Discipline (see references/data-and-diagram-rules.md):
- Native-first: this track is an escalation for objects native cannot faithfully express.
- One token core: every colour/font comes from act_theme (references/tokens.json).
- Deterministic + regenerable: assets are content-addressed; a `.json` sidecar keeps the spec
  and numbers so the pixels are non-editable but the data stays auditable and re-renderable.
- No network, no invention: charts/diagrams draw only supplied values.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import act_theme as theme

BACKEND_VERSION = "1"  # bump on renderer-code changes or a Graphviz CLI upgrade (not in the hash)


def _renderer_versions() -> str:
    """Pin cached assets to the renderer versions that produced them: matplotlib/freetype text
    layout shifts across versions, so an upgrade must bust the content cache. Uses metadata
    lookup (no heavy import) for the pip packages; the Graphviz CLI is covered by BACKEND_VERSION."""
    from importlib import metadata
    parts = []
    for pkg in ("matplotlib", "matplotlib-venn", "graphviz"):
        try:
            parts.append(pkg + metadata.version(pkg))
        except Exception:
            parts.append(pkg + "?")
    return ";".join(parts)

CHART_KINDS = {"combo", "area", "radar", "scatter", "bubble", "waterfall", "line_multi"}
DIAGRAM_GRAPHVIZ = {"org_tree", "node_graph"}
DIAGRAM_MPL = {"ring", "funnel", "pyramid", "venn", "matrix"}
ASSET_KINDS = CHART_KINDS | DIAGRAM_GRAPHVIZ | DIAGRAM_MPL


# ---------------------------------------------------------------- cache / manifest / audit

def asset_id(spec: dict, size_in: tuple[float, float]) -> str:
    payload = json.dumps({"spec": spec, "size": [round(size_in[0], 3), round(size_in[1], 3)],
                          "backend": BACKEND_VERSION, "renderers": _renderer_versions(),
                          "tokens": theme.tokens_hash()},
                         sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _cache_dir(out_root: Path) -> Path:
    d = out_root / "assets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_manifest(cache: Path, aid: str, kind: str, png: Path):
    man = cache / "asset-manifest.json"
    data = json.loads(man.read_text()) if man.exists() else {}
    data[aid] = {"kind": kind, "png": png.name, "sidecar": aid + ".json"}
    man.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def render_asset(spec: dict, out_root: Path, size_in: tuple[float, float] = (8.6, 4.7)) -> Path:
    """Render one asset spec to a cached PNG and return its path.

    spec = {"kind": <ASSET_KINDS>, ...kind-specific fields..., "source": optional}
    Uses a content-addressed cache: identical spec+size+theme → same file, no re-render.
    """
    kind = spec.get("kind")
    if kind not in ASSET_KINDS:
        raise ValueError(f"unknown asset kind '{kind}'. valid: {sorted(ASSET_KINDS)}")
    cache = _cache_dir(Path(out_root))
    aid = asset_id(spec, size_in)
    png = cache / f"{aid}.png"
    if not png.exists():
        if kind in DIAGRAM_GRAPHVIZ:
            _render_graphviz(kind, spec, png)
        else:
            _render_matplotlib(kind, spec, png, size_in)
        # audit sidecar: pixels are opaque, the numbers stay auditable + regenerable
        (cache / f"{aid}.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    _record_manifest(cache, aid, kind, png)
    return png


# ---------------------------------------------------------------- matplotlib charts + schematics

def _style_axes(ax):
    ax.tick_params(length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _render_matplotlib(kind: str, spec: dict, png: Path, size_in):
    palette = theme.apply_matplotlib()
    from matplotlib import pyplot as plt
    C = theme.COLORS
    fig, ax = plt.subplots(figsize=size_in)

    if kind == "combo":
        _chart_combo(ax, spec, palette, C)
    elif kind == "area":
        _chart_area(ax, spec, palette, C)
    elif kind == "line_multi":
        _chart_line_multi(ax, spec, palette, C)
    elif kind in ("scatter", "bubble"):
        _chart_scatter(ax, spec, palette, C, bubble=(kind == "bubble"))
    elif kind == "waterfall":
        _chart_waterfall(ax, spec, palette, C)
    elif kind == "radar":
        fig.clf(); ax = fig.add_subplot(111, projection="polar"); _chart_radar(ax, spec, palette, C)
    elif kind == "ring":
        _diag_ring(ax, spec, palette, C)
    elif kind == "funnel":
        _diag_funnel(ax, spec, palette, C)
    elif kind == "pyramid":
        _diag_pyramid(ax, spec, palette, C)
    elif kind == "venn":
        _diag_venn(ax, spec, palette, C)
    elif kind == "matrix":
        _diag_matrix(ax, spec, palette, C)

    _apply_annotations(ax, spec, C)
    fig.tight_layout(pad=0.4)
    fig.savefig(png, dpi=200, facecolor=C["canvas"])
    plt.close(fig)


def _apply_annotations(ax, spec, C):
    """Generic annotation layer shared by every image chart/diagram: leader-line callout boxes
    anchored to a specific mark, plus badges. This is the recurring IR "explain each step / point
    to the driver" move that native pptx connectors cannot anchor to chart internals.

    spec["annotations"] = [{"target": <int cat index | {"x":, "y":}>, "text": str,
                            "dx": float, "dy": float}]
    An int target resolves against the per-kind anchor list the builder stored on the axes
    (bar tops / step tops / stage centres). dx/dy nudge the callout to avoid collisions."""
    anns = spec.get("annotations") or []
    if not anns:
        return
    anchors = getattr(ax, "_act_anchors", None)
    box = dict(boxstyle="round,pad=0.3", fc=C["surface_tint"], ec=C["rule"], lw=0.8)
    arrow = dict(arrowstyle="-", color=C["ink_faint"], lw=0.8)
    for a in anns:
        t = a.get("target")
        if isinstance(t, dict):
            x, y = t.get("x", 0), t.get("y", 0)
        elif isinstance(t, int) and anchors and 0 <= t < len(anchors):
            x, y = anchors[t]
        else:
            continue
        dx, dy = a.get("dx", 0.0), a.get("dy", None)
        if dy is None:  # default: float the callout above the mark with a short leader
            span = (ax.get_ylim()[1] - ax.get_ylim()[0]) or 1
            dy = span * 0.22
        ax.annotate(a.get("text", ""), xy=(x, y), xytext=(x + dx, y + dy),
                    ha="center", va="center", fontsize=10, color=C["ink"],
                    bbox=box, arrowprops=arrow, zorder=6, wrap=True)


def _chart_combo(ax, spec, palette, C):
    """Columns + a line on a second axis — the dominant IR motif native pptx can't draw."""
    cats = spec["categories"]
    x = range(len(cats))
    bar = spec["bar"]        # {"name":..,"values":[...],"unit":..}
    line = spec["line"]      # {"name":..,"values":[...],"unit":..}
    ax.bar(x, bar["values"], width=0.62, color=palette[0], zorder=2)
    ax._act_anchors = [(xi, v) for xi, v in zip(x, bar["values"])]  # for annotations layer
    # bar values sit INSIDE the bar top (white) so the 2nd-axis line + its labels, which pass
    # near the bar tops, never collide with them (combo label-overlap fix).
    for xi, v in zip(x, bar["values"]):
        ax.annotate(f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}", (xi, v),
                    textcoords="offset points", xytext=(0, -6), ha="center", va="top",
                    fontsize=12, fontweight="bold", color=C["canvas"])
    ax.set_xticks(list(x)); ax.set_xticklabels(cats)
    ax.set_ylim(0, max(bar["values"]) * 1.32)
    _style_axes(ax); ax.set_yticks([])
    ax2 = ax.twinx()
    ax2.plot(x, line["values"], color=C["navy"], marker="o", markersize=5, lw=2.2, zorder=3)
    chip = dict(boxstyle="round,pad=0.15", fc=C["canvas"], ec="none", alpha=0.9)
    for xi, v in zip(x, line["values"]):
        ax2.annotate(f"{v:,.1f}%", (xi, v), textcoords="offset points", xytext=(0, 9),
                     ha="center", fontsize=11, fontweight="bold", color=C["navy"],
                     bbox=chip, zorder=4)
    # headroom so the line + its %-labels sit clear BELOW the bar-top zone even when the last bar
    # is tallest and the line ends highest (the common growth-story case): give the 2nd axis extra
    # top space so the whole line drops into the mid-band and its labels never meet the bar labels.
    ax2.set_ylim(0, max(line["values"]) * 1.75)
    for s in ("top", "left", "right"):
        ax2.spines[s].set_visible(False)
    ax2.set_yticks([]); ax2.tick_params(length=0)
    if bar.get("unit") or line.get("unit"):
        ax.set_title(f"棒: {bar.get('name','')} ({bar.get('unit','')})   線: {line.get('name','')} ({line.get('unit','')})",
                     fontsize=11, color=C["ink_faint"], loc="left", pad=6)


def _chart_area(ax, spec, palette, C):
    cats = spec["categories"]; x = range(len(cats))
    series = spec["series"]  # [{"name","values"}]
    ax.stackplot(list(x), *[s["values"] for s in series],
                 labels=[s["name"] for s in series], colors=palette[:len(series)], alpha=0.9)
    ax.set_xticks(list(x)); ax.set_xticklabels(cats); ax.set_xlim(0, len(cats) - 1)
    _style_axes(ax)
    ax.legend(loc="upper left", frameon=False, fontsize=11)


def _chart_line_multi(ax, spec, palette, C):
    cats = spec["categories"]; x = range(len(cats))
    for i, s in enumerate(spec["series"]):
        ax.plot(x, s["values"], color=palette[i % len(palette)], marker="o", lw=2, label=s["name"])
    ax.set_xticks(list(x)); ax.set_xticklabels(cats)
    _style_axes(ax); ax.legend(loc="best", frameon=False, fontsize=11)


def _chart_scatter(ax, spec, palette, C, bubble=False):
    pts = spec["points"]  # [{"x","y","size"?,"label"?}]
    xs = [p["x"] for p in pts]; ys = [p["y"] for p in pts]
    sizes = [p.get("size", 1) * 400 for p in pts] if bubble else 80
    ax.scatter(xs, ys, s=sizes, color=palette[0], alpha=0.75, edgecolor=C["canvas"])
    for p in pts:
        if p.get("label"):
            ax.annotate(p["label"], (p["x"], p["y"]), fontsize=10, color=C["ink_subtle"],
                        textcoords="offset points", xytext=(6, 4))
    ax.set_xlabel(spec.get("x_label", "")); ax.set_ylabel(spec.get("y_label", ""))
    _style_axes(ax)


def _chart_waterfall(ax, spec, palette, C):
    items = spec["items"]  # [{"label","value","kind":"start|end|pos|neg"}]
    cum = 0; xs = range(len(items)); anchors = []
    for i, it in enumerate(items):
        v = it["value"]; k = it.get("kind", "pos" if v >= 0 else "neg")
        if k in ("start", "end"):
            ax.bar(i, v, color=palette[0], width=0.6); cum = v
        else:
            color = C["primary"] if v >= 0 else C["danger"]
            ax.bar(i, v, bottom=cum, color=color, width=0.6); cum += v
        ax.annotate(("△" if v < 0 else "") + f"{abs(v):,.0f}", (i, cum), ha="center",
                    va="bottom", fontsize=11, fontweight="bold", color=C["ink"],
                    xytext=(0, 3), textcoords="offset points")
        anchors.append((i, cum))  # top of each step, for cause callouts
    ax._act_anchors = anchors
    ax.set_xticks(list(xs)); ax.set_xticklabels([it["label"] for it in items], fontsize=11)
    _style_axes(ax); ax.set_yticks([])


def _chart_radar(ax, spec, palette, C):
    axes = spec["axes"]; N = len(axes)
    ang = [n / N * 2 * math.pi for n in range(N)] + [0]
    for i, s in enumerate(spec["series"]):
        vals = s["values"] + s["values"][:1]
        ax.plot(ang, vals, color=palette[i % len(palette)], lw=2, label=s["name"])
        ax.fill(ang, vals, color=palette[i % len(palette)], alpha=0.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(axes, fontsize=11, color=C["ink"])
    ax.set_yticklabels([]); ax.spines["polar"].set_color(C["rule"])
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), frameon=False, fontsize=10)


def _diag_ring(ax, spec, palette, C):
    segs = spec["segments"]  # [{"label","value"}]
    vals = [s["value"] for s in segs]; labels = [s["label"] for s in segs]
    ax.pie(vals, labels=labels, colors=palette[:len(segs)], startangle=90,
           wedgeprops=dict(width=0.38, edgecolor=C["canvas"], linewidth=2),
           textprops=dict(color=C["ink"], fontsize=12))
    if spec.get("center"):
        ax.text(0, 0, spec["center"], ha="center", va="center", fontsize=15,
                fontweight="bold", color=C["primary_deep"])
    ax.set_aspect("equal")


def _diag_funnel(ax, spec, palette, C):
    from matplotlib.patches import Polygon
    stages = spec["stages"]  # [{"label","value"}]
    n = len(stages); maxv = max(s["value"] for s in stages)
    h = 1.0 / n
    for i, s in enumerate(stages):
        wt = s["value"] / maxv
        wb = stages[i + 1]["value"] / maxv if i + 1 < n else wt * 0.72
        yt = 1 - i * h; yb = 1 - (i + 1) * h
        poly = Polygon([(0.5 - wt / 2, yt), (0.5 + wt / 2, yt),
                        (0.5 + wb / 2, yb), (0.5 - wb / 2, yb)],
                       closed=True, facecolor=palette[i % len(palette)], edgecolor=C["canvas"], lw=2)
        ax.add_patch(poly)
        ax.text(0.5, (yt + yb) / 2, f"{s['label']}\n{s['value']:,}", ha="center", va="center",
                fontsize=12, color=C["canvas"], fontweight="bold")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def _diag_pyramid(ax, spec, palette, C):
    from matplotlib.patches import Polygon
    tiers = spec["tiers"]  # top→bottom [{"label"}]
    n = len(tiers); h = 1.0 / n
    for i, t in enumerate(tiers):
        yt = 1 - i * h; yb = 1 - (i + 1) * h
        wt = (i) / n; wb = (i + 1) / n
        poly = Polygon([(0.5 - wt / 2, yt), (0.5 + wt / 2, yt),
                        (0.5 + wb / 2, yb), (0.5 - wb / 2, yb)],
                       closed=True, facecolor=palette[i % len(palette)], edgecolor=C["canvas"], lw=2)
        ax.add_patch(poly)
        ax.text(0.5, (yt + yb) / 2, t["label"], ha="center", va="center",
                fontsize=12, color=C["canvas"], fontweight="bold")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def _diag_venn(ax, spec, palette, C):
    from matplotlib_venn import venn2, venn3
    sets = spec["sets"]  # [{"label","size"}] len 2 or 3, plus optional "overlaps"
    labels = [s["label"] for s in sets]
    if len(sets) == 2:
        v = venn2(subsets=spec.get("subsets", (10, 10, 4)), set_labels=labels, ax=ax)
    else:
        v = venn3(subsets=spec.get("subsets", (10, 10, 3, 10, 3, 3, 2)), set_labels=labels, ax=ax)
    # venn2 のリージョン id と venn3 の全 id(単集合+重なり)を両方カバーする。
    # 重なり id("110","101","011","111")を落とすとそこだけ matplotlib_venn の
    # 既定色が残り、act_theme 一元化の契約が破れる
    for i, patch_id in enumerate(("10", "01", "11",
                                  "100", "010", "001", "110", "101", "011", "111")):
        try:
            p = v.get_patch_by_id(patch_id)
            if p:
                p.set_color(palette[i % len(palette)]); p.set_alpha(0.55); p.set_edgecolor(C["canvas"])
        except Exception:
            pass


def _diag_matrix(ax, spec, palette, C):
    """2x2 (or NxM) labelled coverage matrix with filled/empty cells."""
    rows = spec["rows"]; cols = spec["cols"]; cells = spec.get("cells", {})
    from matplotlib.patches import Rectangle
    nr, nc = len(rows), len(cols)
    for r in range(nr):
        for c in range(nc):
            filled = cells.get(f"{r},{c}", False)
            ax.add_patch(Rectangle((c, nr - 1 - r), 0.94, 0.94,
                         facecolor=C["primary_pale"] if filled else C["surface_tint"],
                         edgecolor=C["rule"]))
            if filled:
                ax.text(c + 0.47, nr - 1 - r + 0.47, "●", ha="center", va="center",
                        color=C["primary"], fontsize=16)
    ax.set_xticks([c + 0.47 for c in range(nc)]); ax.set_xticklabels(cols, fontsize=11)
    ax.set_yticks([nr - 1 - r + 0.47 for r in range(nr)]); ax.set_yticklabels(rows, fontsize=11)
    ax.set_xlim(0, nc); ax.set_ylim(0, nr)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)


# ---------------------------------------------------------------- graphviz relationship graphs

def _render_graphviz(kind: str, spec: dict, png: Path):
    import graphviz

    engine = "dot" if kind == "org_tree" else spec.get("engine", "dot")
    g = graphviz.Digraph(engine=engine, format="png")
    g.attr(dpi="200", **theme.graphviz_graph_attr())
    if kind == "org_tree":
        g.attr(rankdir=spec.get("rankdir", "TB"))
    g.attr("node", **theme.graphviz_node_attr())
    g.attr("edge", **theme.graphviz_edge_attr())
    # deterministic emission: fixed node/edge order
    for n in sorted(spec["nodes"], key=lambda d: d["id"]):
        attrs = {}
        if n.get("focal"):
            attrs.update(fillcolor=theme.COLORS["primary_pale"], color=theme.COLORS["primary"],
                         penwidth="1.6")
        g.node(n["id"], n.get("label", n["id"]), **attrs)
    for e in sorted(spec["edges"], key=lambda d: (d["from"], d["to"])):
        g.edge(e["from"], e["to"], label=e.get("label", ""))
    data = g.pipe(format="png")
    png.write_bytes(data)
