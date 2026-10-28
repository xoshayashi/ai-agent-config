"""Image-asset backend for the Act slide engine.

Renders Act-styled, deterministic, headless graphics that the native python-pptx track cannot
draw — every chart and schematic diagram via Vega-Lite (act_vega, rendered by vl-convert), and
relationship graphs via Graphviz — and returns a PNG path the builder embeds with `add_picture`.
matplotlib is not used.

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
from pathlib import Path

import act_theme as theme

BACKEND_VERSION = "3"  # bump on renderer-code changes or a Graphviz CLI upgrade (not in the hash). 3: matplotlib を廃止し Vega-Lite へ


def _renderer_versions() -> str:
    """Pin cached assets to the renderer versions that produced them: text layout shifts across
    versions, so an upgrade must bust the content cache. Uses metadata lookup (no heavy import)
    for the pip packages; the Graphviz CLI is covered by BACKEND_VERSION."""
    from importlib import metadata
    parts = []
    for pkg in ("vl-convert-python", "graphviz"):
        try:
            parts.append(pkg + metadata.version(pkg))
        except Exception:
            parts.append(pkg + "?")
    return ";".join(parts)

DIAGRAM_GRAPHVIZ = {"org_tree", "node_graph"}
# グラフと模式図はすべて Vega-Lite(act_vega)。waterfall はネイティブのグラフ(build_deck.add_waterfall_chart)
from act_vega import VEGA_KINDS  # noqa: E402
ASSET_KINDS = DIAGRAM_GRAPHVIZ | VEGA_KINDS


# ---------------------------------------------------------------- cache / manifest / audit

def _vega_fingerprint() -> str:
    """Vega のグラフは、vl-convert の版と act_vega.py(テーマとレシピ)の中身で描き方が決まる。
    どちらかが変われば作り直す — 手で BACKEND_VERSION を上げ忘れても古い画像を使わない。"""
    from importlib import metadata
    try:
        ver = metadata.version("vl-convert-python")
    except Exception:
        ver = "?"
    src = (Path(__file__).resolve().parent / "act_vega.py").read_bytes()
    return ver + ":" + hashlib.sha1(src).hexdigest()[:12]


def asset_id(spec: dict, size_in: tuple[float, float]) -> str:
    key = {"spec": spec, "size": [round(size_in[0], 3), round(size_in[1], 3)],
           "backend": BACKEND_VERSION, "renderers": _renderer_versions(),
           "tokens": theme.tokens_hash()}
    if spec.get("kind") in VEGA_KINDS:
        key["vega"] = _vega_fingerprint()
    payload = json.dumps(key, sort_keys=True, ensure_ascii=False)
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
            import act_vega
            act_vega.render(spec, png, size_in)
        # audit sidecar: pixels are opaque, the numbers stay auditable + regenerable
        (cache / f"{aid}.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    _record_manifest(cache, aid, kind, png)
    return png


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
