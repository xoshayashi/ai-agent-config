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

VEGA_KINDS = frozenset({"vega", "mekko", "slope", "dumbbell", "bullet"})
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


def act_config() -> dict:
    """Act の見た目を Vega-Lite の config にする。テンプレート(act_theme.use_template)の色をそのまま読む。
    方針: 罫と枠は最小(y 軸の線を消し、目盛り線は淡い1本)、凡例は上に横並びで題なし、値は直接ラベルで読ませる。"""
    C = theme.COLORS
    T = theme.TOKENS["type_scale_pt"]
    font = "Noto Sans JP"
    return {
        "background": C["canvas"],
        "font": font,
        "padding": 4,
        "view": {"stroke": None},
        "axis": {
            "labelFont": font, "titleFont": font, "labelFontSize": T["chart_axis"], "titleFontSize": T["chart_axis"],
            "labelColor": C["ink_subtle"], "titleColor": C["ink_subtle"], "titleFontWeight": 400,
            "gridColor": C["rule"], "gridWidth": theme.CHART["gridline_width_pt"], "domainColor": C["ink_faint"],
            "tickColor": C["ink_faint"], "ticks": False, "labelPadding": 6, "titlePadding": 8,
        },
        "axisX": {"grid": False, "labelAngle": 0},
        "axisY": {"domain": False, "tickCount": 5},
        "axisBand": {"domain": True},
        "legend": {"orient": "top", "direction": "horizontal", "title": None, "labelFont": font,
                   "labelFontSize": T["chart_label"], "labelColor": C["ink"], "symbolType": "circle",
                   "symbolSize": 120, "columnPadding": 18},
        "title": {"font": font, "fontSize": T["chart_label"], "color": C["ink"], "anchor": "start", "fontWeight": 600},
        "text": {"font": font, "fontSize": T["chart_label"], "color": C["ink"]},
        "range": {"category": list(theme.SERIES_PALETTE)},
        "bar": {"cornerRadiusEnd": 2, "color": C["primary"]},
        "line": {"strokeWidth": 2.5, "color": C["primary"]},
        "point": {"filled": True, "size": 70, "color": C["primary"]},
        "area": {"color": C["primary"], "opacity": 0.85},
        "rule": {"color": C["ink_faint"]},
        "header": {"labelFont": font, "titleFont": font, "labelFontSize": T["chart_label"], "labelColor": C["ink"]},
    }


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
    if kind in RECIPES:
        spec = RECIPES[kind](spec)
    w, h = size_in
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
                                                 "format": spec.get("label_format", ",")}}
        text_enc.pop("color", None)
        vl["layer"] = [base, {"mark": {"type": "text", "dy": 0 if horizontal else -8, "dx": 6 if horizontal else 0,
                                       "align": "left" if horizontal else "center", "baseline": "middle" if horizontal else "bottom",
                                       "fontWeight": 600},
                              "encoding": text_enc}]
    if spec.get("unit"):
        _set_quant_axis_title(vl, spec["unit"])
    return vl


def _mark_type(view: dict) -> str | None:
    m = view.get("mark")
    return m.get("type") if isinstance(m, dict) else m


def _set_quant_axis_title(vl: dict, unit: str) -> None:
    """単位を量の軸の題に置く(書き手が題を書いていなければ)。"""
    views = vl.get("layer") or [vl]
    for v in views:
        for ch in ("y", "x"):
            e = (v.get("encoding") or {}).get(ch)
            if isinstance(e, dict) and e.get("type") == "quantitative" and "title" not in e:
                e["title"] = f"({unit})"
                return


# ---------------------------------------------------------------- consulting recipes
# 定番のグラフを、単純なデータから Vega-Lite に組み立てる。どれも書き手が mark / encoding を書かずに済む。

def build_mekko(spec: dict) -> dict:
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


def build_slope(spec: dict) -> dict:
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
    fmt = spec.get("label_format", ",")
    return {"data": rows, "layer": [
        {"mark": {"type": "line", "point": True}, "encoding": {"x": x, "y": y, "detail": {"field": "name"}, "color": col}},
        {"transform": [{"filter": "datum.end === 0"}, {"calculate": f"datum.name + '  ' + format(datum.v, '{fmt}')", "as": "lab"}],
         "mark": {"type": "text", "align": "right", "dx": -10},
         "encoding": {"x": x, "y": y, "text": {"field": "lab"}, "color": col}},
        {"transform": [{"filter": "datum.end === 1"}, {"calculate": f"format(datum.v, '{fmt}') + '  ' + datum.name", "as": "lab"}],
         "mark": {"type": "text", "align": "left", "dx": 10},
         "encoding": {"x": x, "y": y, "text": {"field": "lab"}, "color": col}},
    ]}


def build_dumbbell(spec: dict) -> dict:
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
    xq = {"type": "quantitative", "title": f"({spec['unit']})" if spec.get("unit") else None,
          "scale": {"domain": [lo - pad, hi + pad], "nice": False}, "axis": {"tickCount": 6, "format": spec.get("axis_format", "~s")}}
    fmt = spec.get("label_format", ",")
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


def build_bullet(spec: dict) -> dict:
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
    xq = {"type": "quantitative", "title": f"({spec['unit']})" if spec.get("unit") else None}
    fmt = spec.get("label_format", ",")
    layers = []
    for fld, shade in (("r3", C["surface"]), ("r2", C["chart_gray_light"]), ("r1", C["chart_gray"])):
        layers.append({"transform": [{"filter": f"datum.{fld} != null"}], "mark": {"type": "bar", "color": shade, "size": 28,
                                                                              "cornerRadiusEnd": 0},
                       "encoding": {"y": y, "x": {"field": fld, **xq}}})
    layers += [
        {"mark": {"type": "bar", "color": C["primary_deep"], "size": 10}, "encoding": {"y": y, "x": {"field": "actual", **xq}}},
        {"transform": [{"filter": "datum.target != null"}],
         "mark": {"type": "tick", "color": C["ink"], "thickness": 3, "size": 30}, "encoding": {"y": y, "x": {"field": "target", **xq}}},
        {"mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": 700, "color": C["primary_deep"]},
         "encoding": {"y": y, "x": {"field": "actual", **xq}, "text": {"field": "actual", "format": fmt}}},
    ]
    return {"data": rows, "layer": layers}


RECIPES = {"mekko": build_mekko, "slope": build_slope, "dumbbell": build_dumbbell, "bullet": build_bullet}


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
