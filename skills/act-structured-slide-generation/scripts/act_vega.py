#!/usr/bin/env python3
"""Vega-Lite で描くグラフ(画像トラック)。データ + mark + encoding の宣言でどんなグラフも書け、
Act の見た目(フォント・配色・軸・余白)はここで一括で当てる。

なぜ Vega-Lite か(references/charts-vega.md):
- 図の文法(grammar of graphics)。棒・線・面・点・ヒートマップ・スロープ・ダンベル・マリメッコまで、
  データの行と「どの列をどの視覚変数に割り当てるか」だけで書ける。種類ごとの描画関数を足していかなくてよい。
- 宣言的な JSON なので、書き手(LLM)がそのまま書ける。描く前にコンパイルして誤りを検出できる。
- vl-convert(Rust 製、ブラウザ不要)で、同じ入力から同じ PNG が出る。

使い方(chart オブジェクトとして、chart_insight / composite / chart_grid / metric_proof に置く):
  {"kind": "vega", "unit": "億円", "data": [{...}, ...], "mark": "bar", "encoding": {...},
   "focal": {"field": "segment", "equals": "自社"}, "labels": true}
  {"kind": "mekko" | "slope" | "dumbbell" | "bullet", ...}   # 戦略ファーム定番のレシピ(下の build_*)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import act_theme as theme

# 画像で描くグラフ・図はすべてここ(matplotlib は使わない)。関係図(org_tree / node_graph)だけ Graphviz
VEGA_KINDS = frozenset({"vega", "mekko", "slope", "dumbbell", "bullet",
                        "combo", "area", "line_multi", "scatter", "bubble", "radar",
                        "ring", "funnel", "pyramid", "venn", "matrix"})
_FONTS_REGISTERED = False
# 1 pt = 1 px で組み、書き出すときに拡大する。スライドに置いた画像の文字の大きさが、スライドの
# 型(pt)と一致する(14.5pt の軸ラベルは 14.5pt で見える)
PX_PER_IN = 72.0
EXPORT_SCALE = 200 / 72.0          # 200dpi 相当(他の画像アセットと同じ解像度)


def _register_fonts() -> None:
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    import vl_convert as vlc
    for d in (Path.home() / "Library" / "Fonts", Path("/Library/Fonts"), Path(__file__).resolve().parent):
        if d.exists():
            try:
                vlc.register_font_directory(str(d))
            except Exception:
                pass
    _FONTS_REGISTERED = True


def font_stack() -> str:
    """ネイティブのグラフと同じ組: 欧文は Geist、和文は Noto Sans JP(vl-convert はこの順で字を探す)。"""
    return f"{theme.FONTS['latin']}, {theme.FONTS['ea']}"


def act_config() -> dict:
    """Act の見た目を Vega-Lite の config にする。値はネイティブのグラフ(build_deck.add_act_chart)と同じ
    トークンから取り、画像のグラフとネイティブのグラフが並んでも差が出ないようにする:
    - 値軸: 線なし・目盛りなし、目盛り線は chart_gray_light / gridline_width_pt、目盛りの字は ink_faint
    - 項目軸: 線は ink_faint 1.25pt、字は ink、目盛りなし
    - 字の大きさ: 軸 chart_axis、値ラベル chart_label 太字 ink
    - 凡例: 上、四角の記号、chart_axis、ink_subtle
    - 棒: 間隔は gap_width_pct(100% = 棒と同じ幅の隙間)、角は丸めない。線: 2.25pt、点なし
    テンプレート(act_theme.use_template)の色をそのまま読む。"""
    C = theme.COLORS
    T = theme.TOKENS["type_scale_pt"]
    CH = theme.CHART
    font = font_stack()
    gap = CH["gap_width_pct"] / 100.0
    inner = gap / (1.0 + gap)                     # 棒の幅 1 に対して隙間 gap
    return {
        "background": C["canvas"],
        "font": font,
        "padding": 4,
        "view": {"stroke": None},
        "axis": {
            "labelFont": font, "titleFont": font, "labelFontSize": T["chart_axis"], "titleFontSize": T["chart_axis"],
            "labelColor": C["ink_faint"], "titleColor": C["ink_faint"], "titleFontWeight": 400,
            "gridColor": C["chart_gray_light"], "gridWidth": CH["gridline_width_pt"],
            "domainColor": C["ink_faint"], "domainWidth": 1.25, "ticks": False, "labelPadding": 6, "titlePadding": 8,
        },
        "axisX": {"grid": False, "labelAngle": 0, "labelColor": C["ink"]},
        "axisY": {"domain": False, "tickCount": 5},
        "axisBand": {"labelColor": C["ink"]},
        "scale": {"bandPaddingInner": inner, "bandPaddingOuter": inner / 2},
        "legend": {"orient": "top", "direction": "horizontal", "title": None, "labelFont": font,
                   "labelFontSize": T["chart_axis"], "labelColor": C["ink_subtle"], "symbolType": "square",
                   "symbolSize": 110, "columnPadding": 18, "layout": {"top": {"anchor": "middle"}}},
        "title": {"font": font, "fontSize": T["chart_axis"], "color": C["ink_faint"], "anchor": "start",
                  "fontWeight": 400, "offset": 6},
        "text": {"font": font, "fontSize": T["chart_label"], "color": C["ink"], "fontWeight": 700},
        "range": {"category": list(theme.SERIES_PALETTE)},
        "bar": {"color": C["primary"]},
        "line": {"strokeWidth": 2.25, "color": C["primary"]},
        "point": {"filled": True, "size": 60, "color": C["primary"]},
        "area": {"color": C["primary"], "opacity": 1},
        "rule": {"color": C["ink_faint"]},
        "arc": {"stroke": C["canvas"], "strokeWidth": 2},
        "header": {"labelFont": font, "titleFont": font, "labelFontSize": T["chart_axis"], "labelColor": C["ink"]},
    }


def d3_format(spec: dict, default: str = ",.1f") -> str:
    """値ラベルの書式。label_format(d3)が無ければ、ネイティブと同じ number_format(Excel 形式)を d3 に直す。
    既定はネイティブの既定 "#,##0.0" と同じ ",.1f" — 同じ数字が画像とネイティブで違う桁で出ないように。"""
    if spec.get("label_format"):
        return spec["label_format"]
    nf = spec.get("number_format")
    if not nf:
        return default
    pct = "%" in nf
    dec = len(nf.split(".", 1)[1].rstrip("%")) if "." in nf else 0
    return f"{',' if ',' in nf else ''}.{dec}{'%' if pct else 'f'}"


def _focal_color(spec: dict) -> dict | None:
    """focal: {"field": f, "equals": v} → 主役だけ主色、ほかは灰。色の凡例は出さない(主役は直接ラベルで名指す)。"""
    f = spec.get("focal")
    if not isinstance(f, dict) or "field" not in f:
        return None
    C = theme.COLORS
    return {"condition": {"test": {"field": f["field"], "equal": f.get("equals")}, "value": C["primary"]},
            "value": theme.NONFOCAL}


PASSTHROUGH = ("title", "mark", "encoding", "transform", "layer", "facet", "spec", "repeat", "concat", "hconcat",
               "vconcat", "resolve", "params", "projection", "selection")


def to_vegalite(spec: dict, size_in: tuple[float, float]) -> dict:
    """chart オブジェクト → 完全な Vega-Lite 仕様。レシピは先に展開する。"""
    kind = spec.get("kind")
    w, h = size_in
    if kind in RECIPES:
        spec = {**spec, **RECIPES[kind](spec, (w * PX_PER_IN, h * PX_PER_IN))}
    vl: dict = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "width": round(w * PX_PER_IN), "height": round(h * PX_PER_IN),
                "autosize": {"type": "fit", "contains": "padding"},
                "config": act_config()}
    data = spec.get("data")
    if isinstance(data, list):
        vl["data"] = {"values": data}
    elif isinstance(data, dict):
        vl["data"] = data
    for k in PASSTHROUGH:
        if k in spec:
            vl[k] = copy.deepcopy(spec[k])
    # 主役の強調: 単一ビューの color を条件色にする(layer なら各層の color を持たない mark へ)
    fc = _focal_color(spec)
    if fc:
        targets = vl.get("layer") or [vl]
        for t in targets:
            enc = t.setdefault("encoding", {})
            if "color" not in enc and t.get("mark") not in (None,) and _mark_type(t) not in ("text", "rule"):
                enc["color"] = fc
    # 直接ラベル: 棒・点の値を描き、凡例に頼らない(Umbrex / Zelazny: direct labels over legends)
    if spec.get("labels") and "mark" in vl and "layer" not in vl:
        enc = vl.get("encoding", {})
        y = enc.get("y", {})
        x = enc.get("x", {})
        val = y if y.get("type") == "quantitative" else x
        horizontal = x.get("type") == "quantitative"
        base = {k: vl.pop(k) for k in ("mark", "encoding")}
        text_enc = {**base["encoding"], "text": {"field": val.get("field"), "type": "quantitative",
                                                 "format": d3_format(spec)}}
        # ネイティブと同じく、1 系列に値ラベルがあるなら値軸と目盛り線は出さない(値はラベルで読む)
        if "color" not in enc or "condition" in (enc.get("color") or {}):
            qch = "x" if horizontal else "y"
            base["encoding"][qch] = {**base["encoding"][qch], "axis": None}
            text_enc[qch] = {**text_enc[qch], "axis": None}
        text_enc.pop("color", None)
        vl["layer"] = [base, {"mark": {"type": "text", "dy": 0 if horizontal else -8, "dx": 6 if horizontal else 0,
                                       "align": "left" if horizontal else "center", "baseline": "middle" if horizontal else "bottom",
                                       "fontWeight": 600},
                              "encoding": text_enc}]
    # 単位はネイティブの add_unit_note と同じく、図の左上に「(億円)」を置く(軸の題にはしない)
    if "title" not in vl and spec.get("unit") and not spec.get("no_unit_note"):
        vl["title"] = {"text": f"({spec['unit']})"}
    _strip_axis_titles(vl)
    return vl


def _mark_type(view: dict) -> str | None:
    m = view.get("mark")
    return m.get("type") if isinstance(m, dict) else m


def _strip_axis_titles(vl: dict) -> None:
    """軸には題を出さない(ネイティブと同じ。単位は左上の注記、項目は目盛りの字で読む)。列の名前("c" など)が
    軸の下に出るのを防ぐ。書き手が title を書いた軸(散布図の x_label など)はそのまま残す。"""
    def walk(v):
        for ch in ("y", "x"):
            e = (v.get("encoding") or {}).get(ch)
            if isinstance(e, dict) and "title" not in e:
                e["title"] = None
        for sub in v.get("layer") or []:
            walk(sub)
    walk(vl)


# ---------------------------------------------------------------- consulting recipes
# 定番のグラフを、単純なデータから Vega-Lite に組み立てる。どれも書き手が mark / encoding を書かずに済む。

def build_mekko(spec: dict, px=None) -> dict:
    """マリメッコ: 列の幅 = 市場の大きさ(列の合計)、列の中の高さ = シェア。主役(focal、例: 自社)を主色に。
    columns: [{label, segments: [{label, value}]}]。列の幅の比と、各セグメントのシェアはここで計算する。"""
    cols = spec.get("columns", [])
    focal = spec.get("focal")
    totals = [sum(float(s.get("value", 0)) for s in c.get("segments", [])) for c in cols]
    grand = sum(totals) or 1.0
    rows = []
    x0 = 0.0
    for c, tot in zip(cols, totals):
        width = tot / grand
        y0 = 0.0
        for sgm in c.get("segments", []):
            share = (float(sgm.get("value", 0)) / tot) if tot else 0.0
            rows.append({"col": c.get("label", ""), "seg": sgm.get("label", ""), "x": x0, "x2": x0 + width,
                         "y": y0, "y2": y0 + share, "share": share, "value": sgm.get("value"),
                         "xm": x0 + width / 2, "ym": y0 + share / 2,
                         # ラベルは入る面だけ(シェア 10% 以上)。主役は 5% あれば名指す — 小さくても読み手の関心はそこにある
                         "big": width >= 0.08 and (share >= 0.10 or (sgm.get("label") == focal and share >= 0.05))})
            y0 += share
        rows.append({"col": c.get("label", ""), "seg": "_total", "xm": x0 + width / 2, "total": tot,
                     "width_share": width, "x": x0, "x2": x0 + width})
        x0 += width
    unit = spec.get("unit", "")
    C = theme.COLORS
    color = ({"condition": {"test": f"datum.seg === {json.dumps(focal, ensure_ascii=False)}", "value": C["primary"]},
              "value": C["chart_gray_light"]} if focal else {"field": "seg", "type": "nominal", "legend": None})
    seg = {"filter": "datum.seg !== '_total'"}
    tot = {"filter": "datum.seg === '_total'"}
    return {"data": rows, "layer": [
        {"transform": [seg], "mark": {"type": "rect", "stroke": C["canvas"], "strokeWidth": 2},
         "encoding": {"x": {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": [0, 1]}},
                      "x2": {"field": "x2"},
                      "y": {"field": "y", "type": "quantitative", "scale": {"domain": [0, 1]},
                            "axis": {"format": "%", "values": [0, 0.5, 1], "title": None}},
                      "y2": {"field": "y2"}, "color": color}},
        {"transform": [seg, {"filter": "datum.big"},
                       {"calculate": "datum.seg + ' ' + format(datum.share, '.0%')", "as": "lab"}],
         "mark": {"type": "text", "fontWeight": 600},
         "encoding": {"x": {"field": "xm", "type": "quantitative"}, "y": {"field": "ym", "type": "quantitative"},
                      "text": {"field": "lab"},
                      "color": {"condition": {"test": f"datum.seg === {json.dumps(focal, ensure_ascii=False)}",
                                              "value": C["canvas"]}, "value": C["ink"]}}},
        {"transform": [tot, {"calculate": f"datum.col + '\\n' + format(datum.total, ',') + {json.dumps(unit, ensure_ascii=False)}",
                             "as": "lab"}],
         "mark": {"type": "text", "baseline": "top", "dy": 8, "lineBreak": "\n", "fontWeight": 600},
         "encoding": {"x": {"field": "xm", "type": "quantitative"}, "y": {"datum": 0, "type": "quantitative"},
                      "text": {"field": "lab"}}},
    ]}


def build_slope(spec: dict, px=None) -> dict:
    """スロープ: 2 時点の変化を系列ごとの線で。両端に名前と値を直接ラベル。focal の系列を主色に。
    periods: [start, end], series: [{name, values: [a, b]}]"""
    p0, p1 = (spec.get("periods") or ["前", "後"])[:2]
    rows = []
    for s in spec.get("series", []):
        a, b = (s.get("values") or [None, None])[:2]
        rows += [{"name": s.get("name"), "t": p0, "v": a, "end": 0}, {"name": s.get("name"), "t": p1, "v": b, "end": 1}]
    focal = spec.get("focal")
    C = theme.COLORS
    col = ({"condition": {"test": f"datum.name === {json.dumps(focal, ensure_ascii=False)}", "value": C["primary"]},
            "value": theme.NONFOCAL} if focal else {"field": "name", "type": "nominal", "legend": None})
    x = {"field": "t", "type": "ordinal", "sort": [p0, p1], "axis": {"title": None, "labelFontWeight": 600},
         "scale": {"padding": 0.6}}
    y = {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}
    fmt = d3_format(spec)
    return {"data": rows, "layer": [
        {"mark": {"type": "line", "point": True}, "encoding": {"x": x, "y": y, "detail": {"field": "name"}, "color": col}},
        {"transform": [{"filter": "datum.end === 0"}, {"calculate": f"datum.name + '  ' + format(datum.v, '{fmt}')", "as": "lab"}],
         "mark": {"type": "text", "align": "right", "dx": -10},
         "encoding": {"x": x, "y": y, "text": {"field": "lab"}, "color": col}},
        {"transform": [{"filter": "datum.end === 1"}, {"calculate": f"format(datum.v, '{fmt}') + '  ' + datum.name", "as": "lab"}],
         "mark": {"type": "text", "align": "left", "dx": 10},
         "encoding": {"x": x, "y": y, "text": {"field": "lab"}, "color": col}},
    ]}


def build_dumbbell(spec: dict, px=None) -> dict:
    """ダンベル: カテゴリごとに 2 つの値(前と後、自社と競合)を線で結ぶ。差の大きい順に並べる。
    categories: [...], from: {name, values}, to: {name, values}。2 つの点は色の凡例で名指す(前 = 灰、後 = 主色)。"""
    cats = spec.get("categories", [])
    fr, to = spec.get("from") or {}, spec.get("to") or {}
    n_from, n_to = fr.get("name", "前"), to.get("name", "後")
    wide, long_ = [], []
    for i, c in enumerate(cats):
        a = (fr.get("values") or [None] * len(cats))[i]
        b = (to.get("values") or [None] * len(cats))[i]
        gap = abs((b or 0) - (a or 0))
        wide.append({"cat": c, "a": a, "b": b, "gap": gap})
        long_ += [{"cat": c, "s": n_from, "v": a, "gap": gap, "side": "from"},
                  {"cat": c, "s": n_to, "v": b, "gap": gap, "side": "to"}]
    C = theme.COLORS
    order = {"field": "gap", "order": "descending"} if spec.get("sort", True) else None
    y = {"field": "cat", "type": "nominal", "sort": order, "axis": {"title": None, "labelColor": C["ink"], "domain": False}}
    vals = [v for r in wide for v in (r["a"], r["b"]) if isinstance(v, (int, float))]
    lo, hi = (min(vals), max(vals)) if vals else (0, 1)
    pad = (hi - lo) * 0.12 or 1
    xq = {"type": "quantitative", "title": None,
          "scale": {"domain": [lo - pad, hi + pad], "nice": False}, "axis": {"tickCount": 6, "format": spec.get("axis_format", "~s")}}
    fmt = d3_format(spec)
    color = {"field": "s", "type": "nominal", "scale": {"domain": [n_from, n_to], "range": [theme.NONFOCAL, C["primary"]]},
             "legend": {"orient": "top", "title": None}}
    return {"layer": [
        {"data": {"values": wide}, "mark": {"type": "rule", "strokeWidth": 3, "color": C["rule"]},
         "encoding": {"y": y, "x": {"field": "a", **xq}, "x2": {"field": "b"}}},
        {"data": {"values": long_}, "mark": {"type": "point", "filled": True, "size": 160, "opacity": 1},
         "encoding": {"y": y, "x": {"field": "v", **xq}, "color": color}},
        {"data": {"values": long_}, "transform": [{"filter": "datum.side === 'to'"}],
         "mark": {"type": "text", "dy": -14, "fontWeight": 700, "color": C["primary_deep"]},
         "encoding": {"y": y, "x": {"field": "v", **xq}, "text": {"field": "v", "format": fmt}}},
        {"data": {"values": long_}, "transform": [{"filter": "datum.side === 'from'"}],
         "mark": {"type": "text", "dy": -14, "color": C["ink_subtle"]},
         "encoding": {"y": y, "x": {"field": "v", **xq}, "text": {"field": "v", "format": fmt}}},
    ]}


def build_bullet(spec: dict, px=None) -> dict:
    """ブレット: 実績(濃い棒)を、評価の帯(淡い灰の段)と目標(縦の目盛り)に重ねる。KPI の達成度を一覧で。
    items: [{label, actual, target?, ranges?: [低, 中, 高]}]"""
    C = theme.COLORS
    rows = []
    for it in spec.get("items", []):
        rng = it.get("ranges") or []
        rows.append({"label": it.get("label"), "actual": it.get("actual"), "target": it.get("target"),
                     "r1": rng[0] if len(rng) > 0 else None, "r2": rng[1] if len(rng) > 1 else None,
                     "r3": rng[2] if len(rng) > 2 else None})
    y = {"field": "label", "type": "nominal", "sort": None, "axis": {"title": None, "labelColor": C["ink"]}}
    xq = {"type": "quantitative", "title": None}
    fmt = d3_format(spec)
    layers = []
    for fld, shade in (("r3", C["surface"]), ("r2", C["chart_gray_light"]), ("r1", C["chart_gray"])):
        layers.append({"transform": [{"filter": f"datum.{fld} != null"}], "mark": {"type": "bar", "color": shade, "size": 28},
                       "encoding": {"y": y, "x": {"field": fld, **xq}}})
    layers += [
        {"mark": {"type": "bar", "color": C["primary_deep"], "size": 10}, "encoding": {"y": y, "x": {"field": "actual", **xq}}},
        {"transform": [{"filter": "datum.target != null"}],
         "mark": {"type": "tick", "color": C["ink"], "thickness": 3, "size": 30}, "encoding": {"y": y, "x": {"field": "target", **xq}}},
        {"mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": 700, "color": C["primary_deep"]},
         "encoding": {"y": y, "x": {"field": "actual", **xq}, "text": {"field": "actual", "format": fmt}}},
    ]
    return {"data": rows, "layer": layers}


def _fmt(v) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{f:,.0f}" if f.is_integer() else f"{f:,.1f}"


def _annotation_layer(spec: dict, anchors: list, x_enc: dict, y_enc: dict, base_dy: float = 26) -> list:
    """注記(annotations): [{target: 項目の添字 | {x, y}, text, dy?}]。添字は各レシピの印の位置(棒の上端など)。
    注記は印の上に浮かせた太字の短文(凡例ではなく、その印の理由を言う)。"""
    rows = []
    for a in spec.get("annotations") or []:
        t = a.get("target")
        if isinstance(t, dict) and "x" in t and "y" in t:
            ax, ay = t["x"], t["y"]
        elif isinstance(t, int) and 0 <= t < len(anchors):
            ax, ay = anchors[t]
        else:
            continue
        rows.append({"ax": ax, "ay": ay, "text": a.get("text", ""), "dy": -abs(float(a.get("dy", base_dy)))})
    if not rows:
        return []
    C = theme.COLORS
    # 浮かせる量は印の上に一律(mark の dy)。行ごとの yOffset は vl-convert で効かないため使わない
    lift = rows[0]["dy"]
    return [{"data": {"values": rows}, "mark": {"type": "text", "fontWeight": 600, "color": C["ink"], "baseline": "bottom",
                                                "dy": lift},
             "encoding": {"x": {**x_enc, "field": "ax"}, "y": {**y_enc, "field": "ay"}, "text": {"field": "text"}}}]


def build_combo(spec: dict, px=None) -> dict:
    """棒 + 第2軸の折れ線(売上と粗利率など)。棒は下の帯(高さの 55% まで)に置いて値を棒の上(ネイティブの
    縦棒と同じ太字 ink)、線は上の帯(高さの 72-90%)に通して値を点の上 — 帯を分けるので値どうしが重ならない。
    左上の注記に「棒: 名前(単位)  線: 名前(単位)」。注記(annotations)の添字は棒の上端。"""
    cats = spec.get("categories", [])
    bar, line = spec.get("bar") or {}, spec.get("line") or {}
    fmt = d3_format(spec)
    rows = [{"cat": c, "b": bv, "l": lv} for c, bv, lv in zip(cats, bar.get("values", []), line.get("values", []))]
    C = theme.COLORS
    x = {"field": "cat", "type": "ordinal", "sort": None, "axis": {"title": None}}
    bvals = [r["b"] for r in rows] or [1]
    lvals = [r["l"] for r in rows] or [1]
    bmax = max(bvals) / 0.55
    lo, hi = min(lvals), max(lvals)
    rng = (hi - lo) / 0.18 if hi > lo else (abs(hi) or 1) * 2
    d0 = lo - 0.72 * rng
    yb = {"field": "b", "type": "quantitative", "axis": None, "scale": {"domain": [0, bmax]}}
    yl = {"field": "l", "type": "quantitative", "axis": None, "scale": {"domain": [d0, d0 + rng]}}
    anchors = [(r["cat"], r["b"]) for r in rows]
    lunit = line.get("unit", "")
    title = f"棒: {bar.get('name', '')}({bar.get('unit', '')})   線: {line.get('name', '')}({lunit})"
    return {"data": rows, "title": {"text": title}, "resolve": {"scale": {"y": "independent"}}, "layer": [
        {"layer": [{"mark": {"type": "bar", "color": theme.SERIES_PALETTE[0]}, "encoding": {"x": x, "y": yb}},
                   {"mark": {"type": "text", "baseline": "bottom", "dy": -6},
                    "encoding": {"x": x, "y": yb, "text": {"field": "b", "type": "quantitative", "format": fmt}}},
                   *_annotation_layer(spec, anchors, {"type": "ordinal", "sort": None},
                                      {"type": "quantitative", "scale": {"domain": [0, bmax]}, "axis": None}, base_dy=50)]},
        {"layer": [{"mark": {"type": "line", "color": C["navy"], "strokeWidth": 2.25,
                             "point": {"color": C["navy"], "size": 50}}, "encoding": {"x": x, "y": yl}},
                   {"transform": [{"calculate": f"format(datum.l, '{fmt}') + {json.dumps(lunit, ensure_ascii=False)}", "as": "ll"}],
                    "mark": {"type": "text", "baseline": "bottom", "dy": -9, "color": C["navy"]},
                    "encoding": {"x": x, "y": yl, "text": {"field": "ll"}}}]},
    ]}


_LINE_LEGEND = {"symbolType": "stroke", "symbolStrokeWidth": 2.5}   # 折れ線の凡例は線分(ネイティブと同じ)


def _long_series(spec: dict) -> list:
    cats = spec.get("categories", [])
    return [{"cat": c, "s": s.get("name", ""), "v": v, "order": si}
            for si, s in enumerate(spec.get("series", [])) for c, v in zip(cats, s.get("values", []))]


def build_area(spec: dict, px=None) -> dict:
    """積み上げの面(構成の推移)。凡例は上。注記の添字は項目の位置(積み上げの上端)。"""
    rows = _long_series(spec)
    x = {"field": "cat", "type": "ordinal", "sort": None, "axis": {"title": None}, "scale": {"padding": 0}}
    names = [s.get("name", "") for s in spec.get("series", [])]
    tops = {}
    for r in rows:
        tops[r["cat"]] = tops.get(r["cat"], 0) + (r["v"] or 0)
    anchors = [(c, tops.get(c, 0)) for c in spec.get("categories", [])]
    return {"data": rows, "layer": [
        {"mark": {"type": "area", "opacity": 1},
         "encoding": {"x": x, "y": {"field": "v", "type": "quantitative", "stack": "zero"},
                      "color": {"field": "s", "type": "nominal", "sort": names},
                      "order": {"field": "order"}}},
        *_annotation_layer(spec, anchors, {"type": "ordinal", "sort": None, "scale": {"padding": 0}},
                           {"type": "quantitative"})]}


def build_line_multi(spec: dict, px=None) -> dict:
    """複数系列の折れ線。凡例は上(ネイティブの折れ線と同じ)。注記の添字は項目の位置(その項目の最大値)。"""
    rows = _long_series(spec)
    names = [s.get("name", "") for s in spec.get("series", [])]
    x = {"field": "cat", "type": "ordinal", "sort": None, "axis": {"title": None}}
    peak = {}
    for r in rows:
        peak[r["cat"]] = max(peak.get(r["cat"], float("-inf")), r["v"] if r["v"] is not None else float("-inf"))
    anchors = [(c, peak.get(c, 0)) for c in spec.get("categories", [])]
    return {"data": rows, "layer": [
        {"mark": {"type": "line"},
         "encoding": {"x": x, "y": {"field": "v", "type": "quantitative"},
                      "color": {"field": "s", "type": "nominal", "sort": names, "legend": _LINE_LEGEND},
                      # ネイティブの折れ線と同じ: 1 本目(主役)は 2.25pt、ほかは 1.5pt。線の太さは条件では効かないので尺度で渡す
                      "strokeWidth": {"field": "s", "type": "ordinal", "legend": None,
                                      "scale": {"domain": names, "range": [2.25] + [1.5] * max(0, len(names) - 1)}}}},
        *_annotation_layer(spec, anchors, {"type": "ordinal", "sort": None}, {"type": "quantitative"})]}


def _build_scatter(spec: dict, bubble: bool) -> dict:
    pts = spec.get("points", [])
    rows = [{"x": p_.get("x"), "y": p_.get("y"), "size": p_.get("size", 1), "label": p_.get("label", ""),
             "focal": bool(p_.get("focal"))} for p_ in pts]
    C = theme.COLORS
    pad = 40 if bubble else 18                    # 端の点・泡が軸の線に乗らない余白(px)
    xe = {"field": "x", "type": "quantitative", "title": spec.get("x_label") or None,
          "scale": {"zero": False, "nice": False, "padding": pad}}
    ye = {"field": "y", "type": "quantitative", "title": spec.get("y_label") or None,
          "scale": {"zero": False, "nice": False, "padding": pad}}
    any_focal = any(r["focal"] for r in rows)
    color = ({"condition": {"test": "datum.focal", "value": C["primary"]}, "value": theme.NONFOCAL}
             if any_focal else {"value": C["primary"]})
    enc = {"x": xe, "y": ye, "color": color}
    if bubble:
        enc["size"] = {"field": "size", "type": "quantitative", "legend": None, "scale": {"range": [120, 2600]}}
    anchors = [(r["x"], r["y"]) for r in rows]
    return {"data": rows, "layer": [
        {"mark": {"type": "point", "filled": True, "opacity": 0.8 if bubble else 1, "stroke": C["canvas"],
                  "strokeWidth": 1, **({} if bubble else {"size": 90})}, "encoding": enc},
        {"mark": {"type": "text", "align": "left", "dx": 9, "dy": -6, "fontWeight": 400, "color": C["ink_subtle"]},
         "encoding": {"x": xe, "y": ye, "text": {"field": "label"}}},
        *_annotation_layer(spec, anchors, {"type": "quantitative", "scale": xe["scale"]},
                           {"type": "quantitative", "scale": ye["scale"]})]}


def build_scatter(spec: dict, px=None) -> dict:
    """散布図。points: [{x, y, label?, focal?}]、軸の題は x_label / y_label。"""
    return _build_scatter(spec, bubble=False)


def build_bubble(spec: dict, px=None) -> dict:
    """バブル。points の size で面積。"""
    return _build_scatter(spec, bubble=True)


def build_radar(spec: dict, px=None) -> dict:
    """レーダー: 軸を 12 時から時計回りに置き、系列を閉じた多角形の線で描く。目盛りは 25% 刻みの淡い多角形。
    Vega-Lite に極座標は無いので、座標はここで計算する(値は全系列の最大値で 0-1 に正規化)。"""
    import math
    axes = spec.get("axes", [])
    n = max(1, len(axes))
    series = spec.get("series", [])
    vmax = max([v for s_ in series for v in s_.get("values", []) if isinstance(v, (int, float))] or [1]) or 1

    def pt(k, r):
        a = -math.pi / 2 + 2 * math.pi * k / n
        return r * math.cos(a), -r * math.sin(a)
    rows, grid_rows, spoke_rows, lab_rows = [], [], [], []
    for si, s_ in enumerate(series):
        vals = list(s_.get("values", []))
        for k in range(n + 1):
            v = vals[k % n] if vals else 0
            x, y = pt(k, (v or 0) / vmax)
            rows.append({"s": s_.get("name", ""), "x": x, "y": y, "o": k})
    for lv in (0.25, 0.5, 0.75, 1.0):
        for k in range(n + 1):
            x, y = pt(k, lv)
            grid_rows.append({"lv": lv, "x": x, "y": y, "o": k})
    for k, name in enumerate(axes):
        x, y = pt(k, 1.0)
        spoke_rows.append({"x": 0, "y": 0, "x2": x, "y2": y})
        lx, ly = pt(k, 1.16)
        lab_rows.append({"x": lx, "y": ly, "t": name})
    C = theme.COLORS
    sc = {"domain": [-1.3, 1.3]}
    X = {"field": "x", "type": "quantitative", "axis": None, "scale": sc}
    Y = {"field": "y", "type": "quantitative", "axis": None, "scale": sc}
    names = [s_.get("name", "") for s_ in series]
    return {"layer": [
        {"data": {"values": grid_rows}, "mark": {"type": "line", "color": C["chart_gray_light"], "strokeWidth": 0.75},
         "encoding": {"x": X, "y": Y, "detail": {"field": "lv"}, "order": {"field": "o"}}},
        {"data": {"values": spoke_rows}, "mark": {"type": "rule", "color": C["chart_gray_light"], "strokeWidth": 0.75},
         "encoding": {"x": X, "y": Y, "x2": {"field": "x2"}, "y2": {"field": "y2"}}},
        {"data": {"values": rows}, "mark": {"type": "line", "strokeWidth": 2.25},
         "encoding": {"x": X, "y": Y, "color": {"field": "s", "type": "nominal", "sort": names, "legend": _LINE_LEGEND},
                      "order": {"field": "o"}}},
        {"data": {"values": lab_rows}, "mark": {"type": "text", "fontWeight": 600, "color": C["ink"]},
         "encoding": {"x": X, "y": Y, "text": {"field": "t"}}},
    ]}


def build_ring(spec: dict, px=(600, 340)) -> dict:
    """リング(ドーナツ)。値がすべて同じなら循環として扱い、時計回りに「1. 」から番号を振る(cycle: false で止める)。
    中央に center の語。ラベルは輪の外。"""
    segs = spec.get("segments", [])
    vals = [sg.get("value", 0) for sg in segs]
    cycle = spec.get("cycle", len(set(vals)) == 1 and len(segs) >= 3)
    rows = [{"t": (f"{i + 1}. " if cycle else "") + str(sg.get("label", "")), "v": sg.get("value", 0), "o": i}
            for i, sg in enumerate(segs)]
    w, h = px or (600, 340)
    outer = min(w, h) / 2 * 0.72
    C = theme.COLORS
    theta = {"field": "v", "type": "quantitative", "stack": True}
    layers = [
        {"mark": {"type": "arc", "innerRadius": outer * 0.62, "outerRadius": outer},
         "encoding": {"theta": theta, "order": {"field": "o"},
                      "color": {"field": "t", "type": "nominal", "sort": [r["t"] for r in rows], "legend": None}}},
        {"mark": {"type": "text", "radius": outer + 26, "fontWeight": 600, "color": C["ink"]},
         "encoding": {"theta": theta, "order": {"field": "o"}, "text": {"field": "t"}}},
    ]
    if spec.get("center"):
        layers.append({"data": {"values": [{"t": spec["center"]}]},
                       "mark": {"type": "text", "fontSize": theme.TOKENS["type_scale_pt"]["section_heading"],
                                "color": C["primary_deep"], "x": w / 2, "y": h / 2},
                       "encoding": {"text": {"field": "t"}}})
    return {"data": rows, "layer": layers}


def build_funnel(spec: dict, px=None) -> dict:
    """ファネル: 段ごとに中央寄せの帯、幅は値に比例。帯の中に「段の名前 値」。注記の添字は段。"""
    stages = spec.get("stages", [])
    vmax = max([st.get("value", 0) for st in stages] or [1]) or 1
    rows = [{"t": st.get("label", ""), "v": st.get("value", 0), "x": -st.get("value", 0) / vmax / 2,
             "x2": st.get("value", 0) / vmax / 2, "lab": f"{st.get('label', '')}  {_fmt(st.get('value', 0))}", "o": i}
            for i, st in enumerate(stages)]
    C = theme.COLORS
    y = {"field": "t", "type": "nominal", "sort": [r["t"] for r in rows], "axis": None,
         "scale": {"paddingInner": 0.08}}
    X = {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": [-0.5, 0.5]}}
    return {"data": rows, "layer": [
        {"mark": {"type": "bar"},
         "encoding": {"y": y, "x": X, "x2": {"field": "x2"},
                      "color": {"field": "t", "type": "nominal", "sort": [r["t"] for r in rows], "legend": None}}},
        # 帯が広い段は中に白で、狭い段(幅 35% 未満)は帯の右に ink で — 字が帯からはみ出さない
        {"transform": [{"filter": "datum.x2 - datum.x >= 0.35"}], "mark": {"type": "text", "color": C["canvas"]},
         "encoding": {"y": y, "x": {"datum": 0, "type": "quantitative", "scale": {"domain": [-0.5, 0.5]}},
                      "text": {"field": "lab"}}},
        {"transform": [{"filter": "datum.x2 - datum.x < 0.35"}], "mark": {"type": "text", "align": "left", "dx": 10},
         "encoding": {"y": y, "x": {"field": "x2", "type": "quantitative", "scale": {"domain": [-0.5, 0.5]}},
                      "text": {"field": "lab"}}},
    ]}


def build_pyramid(spec: dict, px=None) -> dict:
    """ピラミッド: 上から下へ広がる中央寄せの帯。tiers は [{label}] でも ["経営", "現場"] でもよい。"""
    tiers = [t if isinstance(t, dict) else {"label": str(t)} for t in spec.get("tiers", [])]
    n = max(1, len(tiers))
    rows = [{"t": t.get("label", ""), "x": -(i + 1) / n / 2, "x2": (i + 1) / n / 2, "o": i} for i, t in enumerate(tiers)]
    C = theme.COLORS
    y = {"field": "t", "type": "nominal", "sort": [r["t"] for r in rows], "axis": None, "scale": {"paddingInner": 0.08}}
    X = {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": [-0.5, 0.5]}}
    return {"data": rows, "layer": [
        {"mark": {"type": "bar"},
         "encoding": {"y": y, "x": X, "x2": {"field": "x2"},
                      "color": {"field": "t", "type": "nominal", "sort": [r["t"] for r in rows], "legend": None}}},
        {"mark": {"type": "text", "color": C["canvas"]},
         "encoding": {"y": y, "x": {"datum": 0, "type": "quantitative", "scale": {"domain": [-0.5, 0.5]}},
                      "text": {"field": "t"}}},
    ]}


def _lens_area(r1: float, r2: float, d: float) -> float:
    """半径 r1, r2 の円が中心距離 d で重なる面積。"""
    import math
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2
    a1 = r1 * r1 * math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    a2 = r2 * r2 * math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    return a1 + a2 - 0.5 * math.sqrt(max(0.0, (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2)))


def _distance_for_overlap(r1: float, r2: float, target: float) -> float:
    """重なりの面積が target になる中心距離(二分探索)。面積は大きさ(size)に比例させる。"""
    lo, hi = abs(r1 - r2), r1 + r2
    for _ in range(60):
        mid = (lo + hi) / 2
        if _lens_area(r1, r2, mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build_venn(spec: dict, px=(600, 340)) -> dict:
    """ベン図(2-3 集合): 円の面積を size に、重なりの面積を overlaps({"AB": n, ...})に比例させて配置する。
    overlaps が無ければ小さい方の 30%。円は半透明の塗り、名前と大きさを円の外側寄りに。"""
    import math
    sets = spec.get("sets", [])[:3]
    sizes = [float(st.get("size", 10)) for st in sets]
    ov = {str(k).upper(): float(v) for k, v in (spec.get("overlaps") or {}).items()}
    rad = [math.sqrt(sz / math.pi) for sz in sizes]
    keys = ["AB", "AC", "BC"]

    def dist(i, j, key):
        target = ov.get(key, 0.3 * min(sizes[i], sizes[j]))
        target = max(0.0, min(target, min(sizes[i], sizes[j]) * 0.95))
        return _distance_for_overlap(rad[i], rad[j], target)
    if len(sets) == 2:
        d = dist(0, 1, "AB")
        centers = [(0.0, 0.0), (d, 0.0)]
    else:
        dab, dac, dbc = dist(0, 1, keys[0]), dist(0, 2, keys[1]), dist(1, 2, keys[2])
        cx = (dac ** 2 - dbc ** 2 + dab ** 2) / (2 * dab) if dab else 0.0
        cy = -math.sqrt(max(0.0, dac ** 2 - cx ** 2))
        centers = [(0.0, 0.0), (dab, 0.0), (cx, cy)]
    xs = [c[0] - r for c, r in zip(centers, rad)] + [c[0] + r for c, r in zip(centers, rad)]
    ys = [c[1] - r for c, r in zip(centers, rad)] + [c[1] + r for c, r in zip(centers, rad)]
    w, h = px or (600, 340)
    span = max(max(xs) - min(xs), (max(ys) - min(ys)) * w / h) * 1.25
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    xd = [mx - span / 2, mx + span / 2]
    yd = [my - span / 2 * h / w, my + span / 2 * h / w]
    px_per = w / span
    rows = [{"x": c[0], "y": c[1], "s": st.get("label", ""), "size": math.pi * (r * px_per) ** 2,
             "lab": f"{st.get('label', '')}\n{_fmt(st.get('size', ''))}", "ly": c[1] + r * (0.45 if c[1] >= my else -0.45)}
            for c, r, st in zip(centers, rad, sets)]
    X = {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": xd}}
    Y = {"field": "y", "type": "quantitative", "axis": None, "scale": {"domain": yd}}
    C = theme.COLORS
    return {"data": rows, "layer": [
        {"mark": {"type": "point", "shape": "circle", "filled": True, "opacity": 0.45, "stroke": C["canvas"], "strokeWidth": 2},
         "encoding": {"x": X, "y": Y, "size": {"field": "size", "type": "quantitative", "scale": None, "legend": None},
                      "color": {"field": "s", "type": "nominal", "legend": None}}},
        {"mark": {"type": "text", "lineBreak": "\n", "color": C["ink"]},
         "encoding": {"x": X, "y": {**Y, "field": "ly"}, "text": {"field": "lab"}}},
    ]}


def build_matrix(spec: dict, px=None) -> dict:
    """被覆のマトリクス: 行 × 列のセル、cells {"行,列": true} のセルを淡い主色に塗って ● を置く。"""
    rows_, cols = spec.get("rows", []), spec.get("cols", [])
    cells = spec.get("cells", {})
    data = [{"r": r, "c": c, "on": bool(cells.get(f"{ri},{ci}", False))}
            for ri, r in enumerate(rows_) for ci, c in enumerate(cols)]
    C = theme.COLORS
    x = {"field": "c", "type": "nominal", "sort": cols, "axis": {"orient": "top", "title": None, "domain": False,
                                                                 "labelColor": C["ink"]}}
    y = {"field": "r", "type": "nominal", "sort": rows_, "axis": {"title": None, "domain": False, "labelColor": C["ink"]}}
    return {"data": data, "layer": [
        {"mark": {"type": "rect", "stroke": C["rule"], "strokeWidth": 1},
         "encoding": {"x": x, "y": y, "color": {"condition": {"test": "datum.on", "value": C["primary_pale"]},
                                                "value": C["surface_tint"]}}},
        {"transform": [{"filter": "datum.on"}], "mark": {"type": "text", "text": "●", "color": C["primary"], "fontSize": 18},
         "encoding": {"x": x, "y": y}},
    ]}


RECIPES = {"mekko": build_mekko, "slope": build_slope, "dumbbell": build_dumbbell, "bullet": build_bullet,
           "combo": build_combo, "area": build_area, "line_multi": build_line_multi, "scatter": build_scatter,
           "bubble": build_bubble, "radar": build_radar, "ring": build_ring, "funnel": build_funnel,
           "pyramid": build_pyramid, "venn": build_venn, "matrix": build_matrix}


def compile_check(spec: dict, size_in: tuple[float, float] = (8.6, 4.7)) -> str | None:
    """描く前に Vega-Lite → Vega のコンパイルを通す。誤りがあればその文面を返す(validate が使う)。"""
    try:
        import vl_convert as vlc
    except ImportError:
        return "vl-convert-python が入っていない(pip install --user vl-convert-python)"
    try:
        vlc.vegalite_to_vega(json.dumps(to_vegalite(spec, size_in), ensure_ascii=False))
    except Exception as exc:  # vl-convert の誤り文をそのまま返す
        return str(exc).strip().splitlines()[0][:240]
    return None


def render(spec: dict, png: Path, size_in: tuple[float, float]) -> None:
    import vl_convert as vlc
    _register_fonts()
    vl = to_vegalite(spec, size_in)
    png.write_bytes(vlc.vegalite_to_png(json.dumps(vl, ensure_ascii=False), scale=EXPORT_SCALE))
