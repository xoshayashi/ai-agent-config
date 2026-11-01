#!/usr/bin/env python3
"""追加のページの型(24 種)。build_deck の部品(グリッド・インク積みのテキスト・矩形)だけで組む。

どの型も同じ契約に従う:
  - *_layout(spec, h) が中身の量から必要な高さ need_h を測り、本文帯に入らなければ overflow を返す。
    validate_spec の FIT_CHECKS がビルド前に同じ関数で止める。型(文字の大きさ)は縮めない。
  - 入りきらないときも、図形の枠は本文帯の中に置く(はみ出しは中身の側で報告する)。
  - 色はトークンの役割だけ(primary / primary_deep / primary_pale / surface_tint / ink …)。
  - 項目数の上限・必須キーは SPEC に書く。validate_spec はこの表を読む(描画と検査が同じ表を見る)。

build_deck からは install(module) で登録する。この模块は build_deck を import しない
(build_deck を __main__ として実行したときの二重読み込みを避ける) — 部品は B 経由で引く。
"""
from __future__ import annotations

from deck_argument import (
    COMPOSITION_MAX_SEGMENTS,
    FUNNEL_MAX_STAGES,
    PRICING_MAX_TIERS,
    PROGRESS_MAX_ROWS,
    RANKING_MAX_ITEMS,
    TARGET_BARS_MAX_ROWS,
)

B = None        # install() が build_deck のモジュールを入れる


def install(mod) -> None:
    global B
    B = mod
    mod.PATTERNS.update(RENDERERS)


# ---------------------------------------------------------------- 検査の表(validate_spec が読む)
#
# pattern: (一覧のキー, 下限, 上限, 項目に要るキー, 図表のページか)
SPEC = {
    "big_number": (None, 0, 0, (), True),
    "number_strip": ("numbers", 2, 4, ("value", "label"), True),
    "progress_bars": ("bars", 2, PROGRESS_MAX_ROWS, ("label", "value"), True),
    "ranking": ("items", 3, RANKING_MAX_ITEMS, ("label", "value"), True),
    "funnel": ("stages", 3, FUNNEL_MAX_STAGES, ("label", "value"), True),
    "pyramid": ("tiers", 3, 5, ("label",), False),
    "composition_bar": ("segments", 2, COMPOSITION_MAX_SEGMENTS, ("label", "value"), True),
    "heatmap_table": ("rows", 2, 8, (), True),
    "swot": (None, 0, 0, (), False),
    "pros_cons": (None, 0, 0, (), False),
    "versus": ("rows", 2, 6, ("label", "left", "right"), False),
    "cycle": ("steps", 3, 6, ("label",), False),
    "value_chain": ("stages", 3, 6, ("label",), False),
    "layer_stack": ("layers", 2, 5, ("label",), False),
    "org_chart": ("children", 2, 5, ("name",), False),
    "checklist": ("items", 3, 8, ("label", "status"), False),
    "numbered_steps": ("steps", 3, 6, ("label",), False),
    "vertical_timeline": ("events", 3, 7, ("date", "label"), False),
    "faq": ("pairs", 2, 6, ("q", "a"), False),
    "team": ("people", 2, 6, ("name", "role"), False),
    "pricing_tiers": ("tiers", 2, PRICING_MAX_TIERS, ("name", "price"), True),
    "quote_grid": ("quotes", 2, 4, ("quote", "attribution"), False),
    "nine_box": ("items", 1, 12, ("label", "x", "y"), False),
    "target_bars": ("rows", 2, TARGET_BARS_MAX_ROWS, ("label", "actual", "target"), True),
}
REQUIRED = {p: ([k] if k else []) for p, (k, *_r) in SPEC.items()}
REQUIRED["big_number"] = ["value", "label"]
REQUIRED["heatmap_table"] = ["rows", "columns", "values"]
REQUIRED["swot"] = ["strengths", "weaknesses", "opportunities", "threats"]
REQUIRED["pros_cons"] = ["pros", "cons"]
REQUIRED["versus"] = ["left", "right", "rows"]
REQUIRED["org_chart"] = ["root", "children"]
EVIDENCE = {p for p, v in SPEC.items() if v[4]}
FIT_HINT = "項目を減らすか、各項目の文を短くする(型は縮めない)"


def check(s: dict) -> list[str]:
    """型ごとの形の検査(件数・必須キー・値の型)。エラー文の一覧を返す。寸法は FIT_CHECKS が見る。"""
    pat = s.get("pattern")
    key, lo, hi, need, _ev = SPEC[pat]
    errs = []
    if key:
        items = s.get(key)
        if not isinstance(items, list):
            return [f"{pat} の {key} は配列"]
        if not lo <= len(items) <= hi:
            errs.append(f"{pat} の {key} は {lo}-{hi} 個({len(items)} 個)")
        for j, it in enumerate(items if need else []):     # need が空 = 項目は文字列(heatmap の行名)
            if not isinstance(it, dict):
                errs.append(f"{pat} の {key}[{j}] は {{{', '.join(need)}}} の形(文字列だけは書けない)")
                continue
            for k in need:
                if it.get(k) in (None, ""):
                    errs.append(f"{pat} の {key}[{j}] に {k} がない")
        if sum(1 for it in items if isinstance(it, dict) and it.get("focal")) > 2:
            errs.append(f"{pat} の focal は2つまで(強調は判断に関わるものに絞る)")
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)  # noqa: E731
    if pat in ("progress_bars", "ranking", "funnel", "composition_bar"):
        for j, it in enumerate(s.get(key) or []):
            if isinstance(it, dict) and not num(it.get("value")):
                errs.append(f"{pat} の {key}[{j}].value は数値")
    if pat == "composition_bar":
        for j, it in enumerate(s.get("segments") or []):
            if isinstance(it, dict) and num(it.get("value")) and it["value"] <= 0:
                errs.append(f"composition_bar の segments[{j}].value={it['value']} — 構成の値は正の数")
    if pat == "progress_bars":
        for j, it in enumerate(s.get("bars") or []):
            if isinstance(it, dict) and num(it.get("value")) and not 0 <= it["value"] <= 1.5:
                errs.append(f"progress_bars の bars[{j}].value={it['value']} — 達成率は 0-1(1.0 = 100%)")
    if pat == "target_bars":
        for j, it in enumerate(s.get("rows") or []):
            if isinstance(it, dict) and not (num(it.get("actual")) and num(it.get("target")) and it["target"] > 0):
                errs.append(f"target_bars の rows[{j}] は actual と target(正の数)が要る")
    if pat == "big_number":
        if len(s.get("context") or []) > 3:
            errs.append("big_number の context は3つまで")
    if pat == "heatmap_table":
        rows, cols, vals = s.get("rows") or [], s.get("columns") or [], s.get("values") or []
        if not 2 <= len(cols) <= 7:
            errs.append(f"heatmap_table の columns は 2-7 列({len(cols)} 列)")
        if len(vals) != len(rows) or any(not isinstance(r, list) or len(r) != len(cols)
                                         or any(not num(v) for v in r) for r in vals):
            errs.append("heatmap_table の values は rows × columns の数値の表")
    if pat == "swot":
        for q in ("strengths", "weaknesses", "opportunities", "threats"):
            if not 1 <= len(s.get(q) or []) <= 4:
                errs.append(f"swot の {q} は 1-4 項目")
    if pat == "pros_cons":
        for q in ("pros", "cons"):
            if not 1 <= len(s.get(q) or []) <= 5:
                errs.append(f"pros_cons の {q} は 1-5 項目")
    if pat == "versus":
        for side in ("left", "right"):
            if not isinstance(s.get(side), dict) or not s[side].get("name"):
                errs.append(f"versus の {side} は {{name, note?}}")
        for j, r in enumerate(s.get("rows") or []):
            if isinstance(r, dict) and r.get("winner") not in (None, "left", "right"):
                errs.append(f"versus の rows[{j}].winner は left / right")
    if pat == "org_chart" and not (isinstance(s.get("root"), dict) and s["root"].get("name")):
        errs.append("org_chart の root は {name, role?}")
    if pat == "checklist":
        for j, it in enumerate(s.get("items") or []):
            if isinstance(it, dict) and it.get("status") not in ("done", "todo", "risk"):
                errs.append(f"checklist の items[{j}].status は done / todo / risk")
    if pat == "nine_box":
        for j, it in enumerate(s.get("items") or []):
            if isinstance(it, dict) and not all(isinstance(it.get(a), int) and not isinstance(it.get(a), bool)
                                                and 0 <= it[a] <= 2 for a in ("x", "y")):
                errs.append(f"nine_box の items[{j}] の x / y は 0-2 の整数")
        if not (s.get("x_label") and s.get("y_label")):
            errs.append("nine_box に x_label と y_label が要る(軸の意味)")
    if pat == "pricing_tiers":
        for j, t in enumerate(s.get("tiers") or []):
            if isinstance(t, dict):
                features = t.get("features")
                if features is not None and (not isinstance(features, list)
                                             or any(not isinstance(f, str) for f in features)):
                    errs.append(f"pricing_tiers の tiers[{j}].features は文字列の配列")
                elif len(features or []) > 6:
                    errs.append(f"pricing_tiers の tiers[{j}].features は6つまで")
    return errs


# ---------------------------------------------------------------- 共通の部品

def _b(text, size, weight=400, color=None, gap=0.0, name=None, kind="text"):
    blk = {"parts": [(str(text), size, weight, color if color is not None else B.C["ink"])], "size": size, "kind": kind}
    if gap:
        blk["gap_before"] = gap
        blk["gap_name"] = name
    return blk


def _h(blocks, w):
    return B._stack_drawn_h(blocks, w) if blocks else 0.0


def _draw(slide, x, y, w, blocks):
    if blocks:
        B.stack_block(slide, x, y, w, B.stack_optical_height(blocks, w), blocks)


def _gap(name):
    return B.OPT["gap_in"][name]


def _oval(slide, cx, cy, d, fill, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches, Pt
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.0)
    sh.shadow.inherit = False
    B._strip_style(sh)
    return sh


def _badge(slide, cx, cy, d, text, fill, ink, pt=None):
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    pt = pt or B.TS["kpi_sub"]
    _oval(slide, cx, cy, d, fill)
    B.add_text(slide, cx - d / 2, cy - d / 2 - B.ink_center_offset_in(pt, "numeral"), d, d,
               [[(str(text), pt, 700, ink)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)


def _cols(n, gut=None, x0=0, span=12):
    """本文の幅を n 等分した (x, w) の列。"""
    x, w = B.grid(x0, span)
    gut = B.LAY["gutter_in"] * 1.5 if gut is None else gut
    cw = (w - gut * (n - 1)) / n
    return [(x + i * (cw + gut), cw) for i in range(n)], gut


def _fit(need, h, **kw):
    return dict(need_h=need, overflow=need > h - 0.10, **kw)


def _top(y0, h, used):
    """中身の高さ used を本文帯に置く上端(光学中心よりやや上)。"""
    return y0 + 0.05 + max(0.0, (h - 0.10 - used) * 0.42)


def _ratio_text(v, decimals=0):
    return f"{v * 100:.{decimals}f}%"


def _warn(pat, L, h):
    if L["overflow"]:
        print(f"WARN: {pat} が本文帯に収まらない({L['need_h']:.2f}in > {h - 0.10:.2f}in) — {FIT_HINT}")


def _spread(mins, h, cap):
    """行の高さ: 最小の高さに、本文帯の余りを等しく足す(1行 cap まで)。帯に入らなければ帯に縮める。"""
    avail = h - 0.10
    slack = max(0.0, avail - sum(mins)) / max(1, len(mins))
    hs = [min(m + slack, max(m, cap)) for m in mins]
    if sum(hs) > avail > 0:
        hs = [x * avail / sum(hs) for x in hs]
    return hs


def _tile_grid(n, cols, h, tile_min, gut):
    """タイルの行列: 1枚の高さは中身から、帯に入らなければ帯の高さで止める。"""
    rows = -(-n // cols)
    avail = h - 0.10 - gut * (rows - 1)
    tile_h = min(max(tile_min, avail / rows * 0.9), avail / rows)
    need = rows * tile_min + gut * (rows - 1)
    return rows, tile_h, need


# ---------------------------------------------------------------- 1. big_number

BIG_PT = 120


def _big_number_layout(spec, h):
    lx, lw = B.grid(0, 7)
    rx, rw = B.grid(7, 5)
    num_h = B.drawn_line_h(BIG_PT) + 0.05
    label = [_b(spec.get("label", ""), 22, 700, B.C["ink"])]
    if spec.get("sublabel"):          # note はフッターの注記(共通欄)なので、数字の下の一文は sublabel
        label.append(_b(spec["sublabel"], B.TS["body"], 400, B.C["ink_subtle"], _gap("heading_body"), "bn_note"))
    left = num_h + 0.18 + _h(label, lw)
    ctx = [_b(c, B.TS["body"], 400, B.C["ink"]) for c in (spec.get("context") or [])]
    right = sum(_h([c], rw - 0.3) + 0.36 for c in ctx)
    need = max(left, right)
    hint = None
    if _value_w(spec, BIG_PT, 32, 700) > lw:          # 120pt の数字が左の7列に1行で入ること
        need = max(need, h + 1.0)
        hint = f"数字 {spec.get('value')} が1行に入らない — 桁を丸めるか単位を大きくする(万→億)"
    return _fit(need, h, hint=hint, lx=lx, lw=lw, rx=rx, rw=rw, num_h=num_h, label=label, ctx=ctx, left=left, right=right)


def p_big_number(slide, spec, deck):
    """一つの数字が信念を変えるページ: 120pt の数字 → 名前 → 注記、右に文脈の事実を罫で区切って2-3個。
    metric_proof(数字 + 証明のグラフ)より静かに、数字そのものを主役にする。"""
    y0, h = B.body_region(spec)
    L = _big_number_layout(spec, h)
    _warn("big_number", L, h)
    top = _top(y0, h, L["need_h"])
    parts = [(str(spec.get("value", "")), BIG_PT, 700, B.C["primary_deep"])]
    if spec.get("unit"):
        parts.append((" " + spec["unit"], 32, 700, B.C["primary_deep"]))
    B.add_text(slide, L["lx"], top + (L["need_h"] - L["left"]) / 2, L["lw"], L["num_h"], [parts], wrap=False)
    _draw(slide, L["lx"], top + (L["need_h"] - L["left"]) / 2 + L["num_h"] + 0.18, L["lw"], L["label"])
    y = top + (L["need_h"] - L["right"]) / 2
    for i, c in enumerate(L["ctx"]):
        B.add_rect(slide, L["rx"], y + 0.04, 0.06, _h([c], L["rw"] - 0.3), B.C["primary"])
        _draw(slide, L["rx"] + 0.3, y, L["rw"] - 0.3, [c])
        y += _h([c], L["rw"] - 0.3) + 0.36


# ---------------------------------------------------------------- 2. number_strip

STRIP_PT = 60


def _value_w(n, vpt, upt, uw=600):
    """数字と単位を1行に組んだときの幅(in)。uw は描画と同じ単位の太さ。"""
    w = B.text_width_in(str(n.get("value", "")), vpt, 700)
    if n.get("unit"):
        w += B.text_width_in(" " + str(n["unit"]), upt, uw)
    return w + vpt / 72.0 * 0.3              # 折返しの安全マージン(wrap_display と同じ 0.3em)


def _strip_blocks(n):
    b = [_b(n.get("label", ""), B.TS["kpi_label"], 600, B.C["ink_subtle"])]
    parts = [(str(n.get("value", "")), STRIP_PT, 700, B.C["primary_deep"] if n.get("focal") else B.C["ink"])]
    if n.get("unit"):
        parts.append(B._unit_part(n["unit"], 22))
    b.append({"parts": parts, "size": STRIP_PT, "kind": "numeral", "gap_before": _gap("metric_subline"),
              "gap_name": "strip_value"})
    if n.get("note"):
        b.append(_b(n["note"], B.TS["body_small"], 400, B.C["ink_subtle"], _gap("heading_body"), "strip_note"))
    return b


def _number_strip_layout(spec, h):
    nums = (spec.get("numbers") or [])[:4]
    cols, gut = _cols(max(1, len(nums)), gut=0.5)
    hs = [_h(_strip_blocks(n), cols[0][1]) for n in nums]
    need = max(hs, default=0.3) + 0.5
    # 数字(+単位)は1行に収まること: 折り返すと「10,59 / 0」のように数が割れる。入らなければ溢れとして止める
    too_wide = [n.get("value") for n in nums if _value_w(n, STRIP_PT, 22) > cols[0][1]]
    if too_wide:
        need = max(need, h + 1.0)
    hint = f"数字 {', '.join(map(str, too_wide))} が列に1行で入らない — 数字を減らすか単位を短くする" if too_wide else None
    band = min(h - 0.10, max(need, (h - 0.10) * 0.62))     # 数字の柱は帯の 6 割まで伸ばす(上の罫から下の罫まで)
    return _fit(need, h, nums=nums, cols=cols, gut=gut, hs=hs, band=band, hint=hint)


def p_number_strip(slide, spec, deck):
    """大きな数字の帯: 2-4 個の数字をカードなしで横に並べ、上の太い罫と下の細い罫で柱を区切る。数字の大きさそのものが
    構造になる(Apple / Stripe の基調講演の数字ページ)。focal の数字だけ主色の濃い側で立てる。"""
    y0, h = B.body_region(spec)
    L = _number_strip_layout(spec, h)
    _warn("number_strip", L, h)
    top = _top(y0, h, L["band"])
    for i, (n, (x, w)) in enumerate(zip(L["nums"], L["cols"])):
        B.add_rect(slide, x, top, w, 0.06, B.C["primary"] if n.get("focal") else B.C["ink"])
        B.add_line(slide, x, top + L["band"], x + w, top + L["band"], B.C["rule"], 0.75)
        bl = _strip_blocks(n)
        _draw(slide, x, top + 0.06 + (L["band"] - 0.06 - _h(bl, w)) / 2, w, bl)


# ---------------------------------------------------------------- 3. progress_bars / 24. target_bars

BAR_H = 0.22
LEGEND_H = 0.36
TL_HEAD = 0.08


def _bar_rows_layout(spec, h, key):
    limit = PROGRESS_MAX_ROWS if key == "bars" else TARGET_BARS_MAX_ROWS
    rows = (spec.get(key) or [])[:limit]
    lx, lw = B.grid(0, 4)
    bx, bw = B.grid(4, 7)
    vx, vw = B.grid(11, 1)
    labels = [[_b(r.get("label", ""), B.RAIL_HEAD_PT, 600, B.C["ink"])]
              + ([_b(r["note"], B.TS["kpi_sub"], 400, B.C["ink_subtle"], 0.06, "bar_note")] if r.get("note") else [])
              for r in rows]
    mins = [max(_h(lb, lw), BAR_H + 0.10) + 0.16 for lb in labels]
    foot = LEGEND_H if key == "rows" else 0.0          # target_bars は凡例の行を本文帯の中に持つ
    row_hs = _spread(mins, h - foot, 0.80)
    return _fit(sum(mins) + foot, h, rows=rows, lx=lx, lw=lw, bx=bx, bw=bw, vx=vx, vw=vw, labels=labels, row_hs=row_hs)


def _progress_bars_layout(spec, h):
    return _bar_rows_layout(spec, h, "bars")


def _target_bars_layout(spec, h):
    return _bar_rows_layout(spec, h, "rows")


def _bar_value_text(slide, x, y, w, rh, text, focal):
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    B.add_text(slide, x, y, w, rh, [[(text, B.TS["kpi_label"], 700, B.C["primary_deep"] if focal else B.C["ink"])]],
               anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.RIGHT, wrap=False)


def p_progress_bars(slide, spec, deck):
    """達成率の棒: 行ごとに 名前(+注記) → 淡い軌道の上の棒 → %。6 行を超える比較では Harvey ball より
    速く読める。棒は 100% で止め、% の字は実際の値を書く。focal の行は主色、他は主色の濃い側を淡く。"""
    y0, h = B.body_region(spec)
    L = _progress_bars_layout(spec, h)
    _warn("progress_bars", L, h)
    y = _top(y0, h, sum(L["row_hs"]))
    for r, lb, rh in zip(L["rows"], L["labels"], L["row_hs"]):
        focal = bool(r.get("focal"))
        lh = _h(lb, L["lw"])
        _draw(slide, L["lx"], y + (rh - lh) / 2, L["lw"], lb)
        by = y + (rh - BAR_H) / 2
        B.add_rect(slide, L["bx"], by, L["bw"], BAR_H, B.C["surface_tint"], radius_pt=4)
        frac = max(0.0, min(1.0, float(r.get("value") or 0)))
        if frac > 0:
            B.add_rect(slide, L["bx"], by, max(BAR_H, L["bw"] * frac), BAR_H,
                       B.C["primary"] if focal else B.C["chart_gray"], radius_pt=4)
        _bar_value_text(slide, L["vx"], y, L["vw"], rh, r.get("display") or _ratio_text(float(r.get("value") or 0)), focal)
        y += rh


def p_target_bars(slide, spec, deck):
    """実績と目標: 行ごとに実績の棒と目標の縦線を描き、右に達成率。目標は線、実績は面 — どちらが計画で
    どちらが結果かを形で分ける。尺度は行ごと(その行の実績と目標の大きい方の 1.15 倍) — 件数と % のように
    単位の違う指標を同じ物差しに載せない。行どうしは棒の長さではなく達成率で比べる。"""
    y0, h = B.body_region(spec)
    L = _target_bars_layout(spec, h)
    _warn("target_bars", L, h)
    y = _top(y0, h, sum(L["row_hs"]) + LEGEND_H)
    for r, lb, rh in zip(L["rows"], L["labels"], L["row_hs"]):
        a, t = float(r.get("actual") or 0), float(r.get("target") or 1)
        top_v = max(a, t) * 1.15 or 1.0       # 行ごとの尺度: 単位の違う指標を同じ物差しに載せない
        hit = a >= t
        lh = _h(lb, L["lw"])
        _draw(slide, L["lx"], y + (rh - lh) / 2, L["lw"], lb)
        by = y + (rh - BAR_H) / 2
        B.add_rect(slide, L["bx"], by, L["bw"], BAR_H, B.C["surface_tint"], radius_pt=4)
        if a > 0:
            B.add_rect(slide, L["bx"], by, max(BAR_H, L["bw"] * a / top_v), BAR_H,
                       B.C["primary"] if hit else B.C["chart_gray"], radius_pt=4)
        tx = L["bx"] + L["bw"] * t / top_v
        B.add_line(slide, tx, by - 0.10, tx, by + BAR_H + 0.10, B.C["ink"], 2.0)
        _bar_value_text(slide, L["vx"], y, L["vw"], rh, r.get("display") or _ratio_text(a / t), hit)
        y += rh
    from pptx.enum.text import PP_ALIGN
    B.add_text(slide, L["bx"], y + 0.04, L["bw"], LEGEND_H - 0.06,
               [[(spec.get("legend", "棒: 実績 / 縦線: 目標"), B.TS["kpi_sub"], 400, B.C["ink_subtle"])]],
               align=PP_ALIGN.RIGHT, wrap=False)


# ---------------------------------------------------------------- 4. ranking

def _ranking_layout(spec, h):
    items = (spec.get("items") or [])[:RANKING_MAX_ITEMS]
    nx, nw = B.grid(0, 1)
    lx, lw = B.grid(1, 4)
    bx, bw = B.grid(5, 6)
    vx, vw = B.grid(11, 1)
    lab = [[_b(it.get("label", ""), B.RAIL_HEAD_PT, 600, B.C["ink"])] for it in items]
    mins = [max(_h(lb, lw), 0.30) + 0.14 for lb in lab]
    row_hs = _spread(mins, h, 0.62)
    return _fit(sum(mins), h, items=items, nx=nx, nw=nw, lx=lx, lw=lw, bx=bx, bw=bw, vx=vx, vw=vw, lab=lab, row_hs=row_hs)


def p_ranking(slide, spec, deck):
    """順位: 順位の数字 → 名前 → 最大値にそろえた棒 → 値。上位 N の比較(顧客・製品・地域)を、表より
    速く、棒グラフより名前を読みやすく。focal(自社など)の行だけ主色。"""
    from pptx.enum.text import MSO_ANCHOR
    y0, h = B.body_region(spec)
    L = _ranking_layout(spec, h)
    _warn("ranking", L, h)
    mx = max((float(it.get("value") or 0) for it in L["items"]), default=1.0) or 1.0
    y = _top(y0, h, sum(L["row_hs"]))
    unit = spec.get("unit", "")
    for i, (it, lb, rh) in enumerate(zip(L["items"], L["lab"], L["row_hs"])):
        focal = bool(it.get("focal"))
        B.add_text(slide, L["nx"], y, L["nw"], rh, [[(f"{i + 1}", 20, 700, B.C["primary"] if focal else B.C["ink_faint"])]],
                   anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        lh = _h(lb, L["lw"])
        _draw(slide, L["lx"], y + (rh - lh) / 2, L["lw"], lb)
        bh = min(0.26, rh * 0.5)
        v = float(it.get("value") or 0)
        if v > 0:
            B.add_rect(slide, L["bx"], y + (rh - bh) / 2, max(0.04, L["bw"] * v / mx), bh,
                       B.C["primary"] if focal else B.C["chart_gray"])
        _bar_value_text(slide, L["vx"], y, L["vw"], rh, it.get("display") or f"{v:g}{unit}", focal)
        if i < len(L["items"]) - 1:
            B.add_line(slide, L["lx"], y + rh, L["vx"] + L["vw"], y + rh, B.C["rule"], 0.5)
        y += rh


# ---------------------------------------------------------------- 5. funnel

def _funnel_layout(spec, h):
    st = (spec.get("stages") or [])[:FUNNEL_MAX_STAGES]
    fx, fw = B.grid(0, 8)
    rx, rw = B.grid(8, 4)
    n = max(1, len(st))
    gap = 0.08
    notes = [[_b(s.get("note", ""), B.TS["body_small"], 400, B.C["ink_subtle"])] if s.get("note") else [] for s in st]
    step_min = max([0.56] + [_h(nb, rw - 0.9) + 0.12 for nb in notes])
    avail = h - 0.10
    step_h = min(max(step_min, (avail - gap * (n - 1)) / n * 0.92), max(step_min, 0.95), (avail - gap * (n - 1)) / n)
    need = n * step_min + gap * (n - 1)
    mx = max((float(s.get("value") or 0) for s in st), default=1.0) or 1.0
    too_wide = []
    for s in st:
        v = float(s.get("value") or 0)
        bar_w = fw * max(0.28, v / mx)
        disp = s.get("display") or f"{v:,.0f}"
        label_w = B.text_width_in(str(s.get("label", "")) + "  ", B.TS["kpi_label"], 600)
        value_w = B.text_width_in(str(disp), B.TS["kpi_label"] + 2, 700)
        if label_w + value_w > bar_w:
            too_wide.append(str(s.get("label", "")))
    hint = (f"funnel の段階ラベルと値が帯に1行で入らない: {', '.join(too_wide[:3])} — "
            "段階名を短くするか表示値を丸める") if too_wide else None
    if too_wide:
        need = max(need, h + 1.0)
    return _fit(need, h, hint=hint, st=st, fx=fx, fw=fw, rx=rx, rw=rw, gap=gap, notes=notes, step_h=step_h)


def p_funnel(slide, spec, deck):
    """ファネル: 段ごとに値に比例した帯を中央にそろえて積み(最小幅 28%)、右に次の段への転換率と注記。
    最後の段(または focal の段)だけ主色。転換率は値から計算して書く(手で書いた率と食い違わない)。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _funnel_layout(spec, h)
    _warn("funnel", L, h)
    st = L["st"]
    mx = max((float(s.get("value") or 0) for s in st), default=1.0) or 1.0
    y = _top(y0, h, len(st) * L["step_h"] + L["gap"] * (len(st) - 1))
    for i, s in enumerate(st):
        v = float(s.get("value") or 0)
        frac = max(0.28, v / mx)
        w = L["fw"] * frac
        x = L["fx"] + (L["fw"] - w) / 2
        focal = s.get("focal") or (i == len(st) - 1 and not any(t.get("focal") for t in st))
        fill = B.C["primary_deep"] if focal else (B.C["primary_pale"] if i % 2 == 0 else B.C["surface_tint"])
        ink = B.C["canvas"] if focal else B.C["ink"]
        B.add_rect(slide, x, y, w, L["step_h"], fill, radius_pt=3)
        disp = s.get("display") or f"{v:,.0f}"
        B.add_text(slide, x, y, w, L["step_h"], [[(f"{s.get('label', '')}  ", B.TS["kpi_label"], 600, ink),
                                                  (disp, B.TS["kpi_label"] + 2, 700, ink)]],
                   anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, wrap=False)
        if i:
            prev = float(st[i - 1].get("value") or 0)
            rate = _ratio_text(v / prev) if prev else "-"
            B.add_text(slide, L["rx"], y - L["gap"] / 2 - 0.16, 0.85, 0.32,
                       [[(f"↓ {rate}", B.TS["kpi_sub"], 700, B.C["primary_deep"])]], wrap=False)
        if L["notes"][i]:
            _draw(slide, L["rx"] + 0.9, y + 0.06, L["rw"] - 0.9, L["notes"][i])
        y += L["step_h"] + L["gap"]


# ---------------------------------------------------------------- 6. pyramid

def _pyramid_layout(spec, h):
    tiers = (spec.get("tiers") or [])[:5]
    px, pw = B.grid(0, 6)
    dx, dw = B.grid(6, 6)
    n = max(1, len(tiers))
    gap = 0.08
    descs = [[_b(t["desc"], B.TS["body_small"], 400, B.C["ink_subtle"])] if t.get("desc") else [] for t in tiers]
    tier_min = max([0.58] + [_h(d, dw - 0.3) + 0.14 for d in descs])
    avail = h - 0.10
    tier_h = min(max(tier_min, (avail - gap * (n - 1)) / n * 0.9), max(tier_min, 1.0), (avail - gap * (n - 1)) / n)
    too_tall = []
    for i, t in enumerate(tiers):
        frac = 0.40 + 0.60 * (i / max(1, n - 1))
        tier_w = pw * frac
        lines = B._text_lines(str(t.get("label", "")), max(0.05, tier_w - 0.24), B.TS["kpi_label"], 700)
        if lines * B.drawn_line_h(B.TS["kpi_label"]) > tier_h:
            too_tall.append(str(t.get("label", "")))
    need = n * tier_min + gap * (n - 1)
    hint = (f"pyramid の段階名が段に収まらない: {', '.join(too_tall[:3])} — 名前を短くする") if too_tall else None
    if too_tall:
        need = max(need, h + 1.0)
    return _fit(need, h, hint=hint, tiers=tiers, px=px, pw=pw, dx=dx, dw=dw, gap=gap, descs=descs, tier_h=tier_h)


def p_pyramid(slide, spec, deck):
    """ピラミッド: 上ほど狭い段を中央にそろえて積み(頂点 = 目的・上位概念)、各段の右に説明を罫でつなぐ。
    段の幅は等差で、意味の階層(数量ではない)を表す。頂点の段だけ主色の濃い面。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _pyramid_layout(spec, h)
    _warn("pyramid", L, h)
    n = len(L["tiers"])
    y = _top(y0, h, n * L["tier_h"] + L["gap"] * (n - 1))
    for i, t in enumerate(L["tiers"]):
        frac = 0.40 + 0.60 * (i / max(1, n - 1))
        w = L["pw"] * frac
        x = L["px"] + (L["pw"] - w) / 2
        top_tier = i == 0
        B.add_rect(slide, x, y, w, L["tier_h"], B.C["primary_deep"] if top_tier else
                   (B.C["primary_pale"] if i % 2 else B.C["surface_tint"]), radius_pt=3)
        B.add_text(slide, x, y, w, L["tier_h"], [[(t.get("label", ""), B.TS["kpi_label"], 700,
                                                  B.C["canvas"] if top_tier else B.C["ink"])]],
                   anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        if L["descs"][i]:
            B.add_line(slide, x + w + 0.08, y + L["tier_h"] / 2, L["dx"] + 0.2, y + L["tier_h"] / 2, B.C["rule"], 0.75)
            dh = _h(L["descs"][i], L["dw"] - 0.3)
            _draw(slide, L["dx"] + 0.3, y + (L["tier_h"] - dh) / 2, L["dw"] - 0.3, L["descs"][i])
        y += L["tier_h"] + L["gap"]


# ---------------------------------------------------------------- 7. composition_bar

COMP_BAR_H = 0.9


def _composition_layout(spec, h):
    segs = (spec.get("segments") or [])[:COMPOSITION_MAX_SEGMENTS]
    x, w = B.grid(0, 12)
    legend_cols, _g = _cols(min(3, max(1, len(segs))), gut=0.4)
    rows = -(-len(segs) // 3) if segs else 1
    leg_blocks = [[_b(s.get("label", ""), B.RAIL_HEAD_PT, 600, B.C["ink"]),
                   _b(s.get("note", ""), B.TS["body_small"], 400, B.C["ink_subtle"], 0.06, "comp_note")]
                  if s.get("note") else [_b(s.get("label", ""), B.RAIL_HEAD_PT, 600, B.C["ink"])] for s in segs]
    leg_h = max((_h(lb, legend_cols[0][1] - 0.32) for lb in leg_blocks), default=0.3) + 0.2
    need = 0.40 + COMP_BAR_H + 0.40 + rows * leg_h
    bar_h = COMP_BAR_H + max(0.0, min(0.9, (h - 0.10 - need) * 0.5))     # 余りの半分で棒を太くする(最大 1.8in)
    return _fit(need, h, segs=segs, x=x, w=w, legend_cols=legend_cols, leg_blocks=leg_blocks, leg_h=leg_h,
                bar_h=bar_h, used=need - COMP_BAR_H + bar_h)


def _seg_fill(i, focal):
    if focal:
        return B.C["primary"], B.C["canvas"]
    seq = [B.C["primary_deep"], B.C["chart_gray"], B.C["primary_pale"], B.C["chart_gray_light"], B.C["surface_tint"]]
    f = seq[i % len(seq)]
    return f, (B.C["canvas"] if i % len(seq) == 0 else B.C["ink"])


def p_composition_bar(slide, spec, deck):
    """構成の一本棒: 100% の横棒を値の比で分け、各区分に % を書き、下に凡例(名前・注記)を並べる。
    ドーナツより比が読みやすく、区分が6つまでなら1本で全体が見える。focal の区分だけ主色。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _composition_layout(spec, h)
    _warn("composition_bar", L, h)
    segs = L["segs"]
    tot = sum(float(s.get("value") or 0) for s in segs) or 1.0
    top = _top(y0, h, L["used"])
    if spec.get("total_label"):
        B.add_text(slide, L["x"], top, L["w"], 0.34, [[(spec["total_label"], B.TS["kpi_label"], 600, B.C["ink_subtle"])]], wrap=False)
    by = top + 0.40
    x = L["x"]
    fills = []
    from deck_argument import composition_bar_label
    for i, s in enumerate(segs):
        sw = L["w"] * float(s.get("value") or 0) / tot
        f, ink = _seg_fill(i, s.get("focal"))
        fills.append(f)
        B.add_rect(slide, x, by, sw, L["bar_h"], f)
        label = composition_bar_label(float(s.get("value") or 0), tot, sw)
        if label is not None:
            B.add_text(slide, x, by, sw, L["bar_h"], [[(label, 18, 700, ink)]],
                       anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, wrap=False)
        x += sw
    ly = by + L["bar_h"] + 0.40
    for i, (s, lb) in enumerate(zip(segs, L["leg_blocks"])):
        cx, cw = L["legend_cols"][i % 3]
        yy = ly + (i // 3) * L["leg_h"]
        B.add_rect(slide, cx, yy + 0.06, 0.20, 0.20, fills[i], line=B.C["rule"] if fills[i] == B.C["surface_tint"] else None)
        _draw(slide, cx + 0.32, yy, cw - 0.32, lb)


# ---------------------------------------------------------------- 8. heatmap_table

def _heatmap_layout(spec, h):
    rows, cols = spec.get("rows") or [], spec.get("columns") or []
    x, w = B.grid(0, 12)
    lab_w = w * 0.26
    cw = (w - lab_w) / max(1, len(cols))
    head_h = max((_h([_b(c, B.TS["kpi_sub"], 600, B.C["ink_subtle"])], cw - 0.1) for c in cols), default=0.3) + 0.14
    lab_h = max((_h([_b(r, B.RAIL_HEAD_PT, 600)], lab_w - 0.1) for r in rows), default=0.3)
    row_min = max(lab_h, 0.42) + 0.10
    avail = h - 0.10 - head_h
    row_h = min(max(row_min, avail / max(1, len(rows))), max(row_min, 0.78), avail / max(1, len(rows)))
    return _fit(head_h + len(rows) * row_min, h, rows=rows, cols=cols, x=x, w=w, lab_w=lab_w, cw=cw, head_h=head_h, row_h=row_h)


def p_heatmap_table(slide, spec, deck):
    """ヒートマップの表: 値の大きさを主色の4段の濃さで塗る(淡い面 → 淡い主色 → 主色 → 濃い主色)。
    数字は必ず書く(色だけで値を伝えない)。濃い2段は白字。lower_is_better なら濃さを反転する。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _heatmap_layout(spec, h)
    _warn("heatmap_table", L, h)
    vals = [[float(v) for v in r] for r in (spec.get("values") or [])]
    flat = [v for r in vals for v in r] or [0.0]
    lo, hi = min(flat), max(flat)
    span = (hi - lo) or 1.0
    levels = [(B.C["surface_tint"], B.C["ink"]), (B.C["primary_pale"], B.C["ink"]),
              (B.C["primary"], B.C["canvas"]), (B.C["primary_deep"], B.C["canvas"])]
    fmt = spec.get("format") or ("{:,.0f}" if all(v == int(v) for v in flat) else "{:,.1f}")
    unit = spec.get("unit", "")
    top = _top(y0, h, L["head_h"] + len(L["rows"]) * L["row_h"])
    for j, c in enumerate(L["cols"]):
        cx = L["x"] + L["lab_w"] + j * L["cw"]
        B.add_text(slide, cx, top, L["cw"], L["head_h"] - 0.06, [[(c, B.TS["kpi_sub"], 600, B.C["ink_subtle"])]],
                   align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    y = top + L["head_h"]
    for i, r in enumerate(L["rows"]):
        B.add_text(slide, L["x"], y, L["lab_w"] - 0.1, L["row_h"], [[(r, B.RAIL_HEAD_PT, 600, B.C["ink"])]],
                   anchor=MSO_ANCHOR.MIDDLE)
        for j in range(len(L["cols"])):
            v = vals[i][j] if i < len(vals) and j < len(vals[i]) else 0.0
            t = (v - lo) / span
            if spec.get("lower_is_better"):
                t = 1 - t
            fill, ink = levels[min(3, int(t * 4))]
            cx = L["x"] + L["lab_w"] + j * L["cw"]
            B.add_rect(slide, cx + 0.03, y + 0.03, L["cw"] - 0.06, L["row_h"] - 0.06, fill, radius_pt=3)
            B.add_text(slide, cx, y, L["cw"], L["row_h"], [[(fmt.format(v) + unit, B.TS["kpi_label"], 600, ink)]],
                       anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, wrap=False)
        y += L["row_h"]


# ---------------------------------------------------------------- 9. swot

SWOT = (("strengths", "S", "強み"), ("weaknesses", "W", "弱み"), ("opportunities", "O", "機会"), ("threats", "T", "脅威"))


def _swot_items(items):
    out = []
    for k, it in enumerate(items):
        out.append(_b(it if isinstance(it, str) else it.get("label", ""), B.TS["body"], 400, B.C["ink"],
                      _gap("heading_body") if k else 0.0, "swot_item"))
    return out


def _swot_layout(spec, h):
    cols, gut = _cols(2)
    pad = 0.24
    head = 0.56
    body = [_h(_swot_items(spec.get(q) or []), cols[0][1] - 2 * pad) for q, *_ in SWOT]
    row1, row2 = max(body[0], body[1]), max(body[2], body[3])
    need = 2 * (head + 2 * pad) + row1 + row2 + gut
    avail = h - 0.10
    extra = max(0.0, avail - need) / 2
    return _fit(need, h, cols=cols, gut=gut, pad=pad, head=head, rows=(row1 + extra * 0.8, row2 + extra * 0.8))


def p_swot(slide, spec, deck):
    """SWOT: 4象限の各面に、主色の頭文字(S / W / O / T)と名前の帯、その下に1-4項目。内部(強み・弱み)
    は上段、外部(機会・脅威)は下段。好ましい側(S / O)は淡い主色、もう一方は淡い面。"""
    y0, h = B.body_region(spec)
    L = _swot_layout(spec, h)
    _warn("swot", L, h)
    labels = spec.get("labels") or {}
    top = _top(y0, h, 2 * (L["head"] + 2 * L["pad"]) + sum(L["rows"]) + L["gut"])
    for k, (q, letter, name) in enumerate(SWOT):
        r, c = divmod(k, 2)
        x, w = L["cols"][c]
        y = top + r * (L["head"] + 2 * L["pad"] + L["rows"][0] + L["gut"])
        ch = L["head"] + 2 * L["pad"] + L["rows"][r]
        good = q in ("strengths", "opportunities")
        B.add_rect(slide, x, y, w, ch, B.C["primary_pale"] if good else B.C["surface_tint"], radius_pt=B.LAY["card"]["radius_pt"])
        _badge(slide, x + L["pad"] + 0.22, y + L["pad"] + 0.22, 0.44, letter,
               B.C["primary_deep"] if good else B.C["ink_subtle"], B.C["canvas"], pt=18)
        from pptx.enum.text import MSO_ANCHOR
        B.add_text(slide, x + L["pad"] + 0.58, y + L["pad"], w - 2 * L["pad"] - 0.58, 0.44,
                   [[(labels.get(q, name), 18, 700, B.C["ink"])]], anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        _draw(slide, x + L["pad"], y + L["pad"] + L["head"] + 0.06, w - 2 * L["pad"], _swot_items(spec.get(q) or []))


# ---------------------------------------------------------------- 10. pros_cons

def _pc_items(items):
    return [[_b(it if isinstance(it, str) else it.get("label", ""), B.TS["body"], 400, B.C["ink"])] for it in items]


def _pros_cons_layout(spec, h):
    cols, gut = _cols(2)
    w = cols[0][1] - 0.6
    sides = []
    for q in ("pros", "cons"):
        its = _pc_items(spec.get(q) or [])
        sides.append([max(_h(b, w), 0.36) for b in its])
    head = 0.80
    body = max(sum(s) + 0.22 * max(0, len(s) - 1) for s in sides)
    verdict = 0.0
    if spec.get("verdict"):
        verdict = _h([_b(spec["verdict"], B.TS["insight"], 600)], B.grid(0, 12)[1] - 0.6) + 0.5
    need = head + body + verdict + 0.2
    return _fit(need, h, cols=cols, w=w, sides=sides, head=head, body=body, verdict=verdict)


def p_pros_cons(slide, spec, deck):
    """利点と懸念: 左に ✓ の利点、右に × の懸念を同じ文法で並べ、下に判断の帯(verdict)。
    比べる側の数をそろえる必要はない(重さを数で偽らない)。判断は濃い帯で一つだけ。"""
    from pptx.enum.text import MSO_ANCHOR
    y0, h = B.body_region(spec)
    L = _pros_cons_layout(spec, h)
    _warn("pros_cons", L, h)
    top = _top(y0, h, L["need_h"])
    heads = (spec.get("pros_label", "利点"), spec.get("cons_label", "懸念"))
    for c, (q, mark, col) in enumerate((("pros", "✓", B.C["primary"]), ("cons", "×", B.C["danger"]))):
        x, w = L["cols"][c]
        B.add_text(slide, x, top, w, 0.4, [[(heads[c], 20, 700, B.C["ink"])]], anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        B.add_rect(slide, x, top + 0.46, w, 0.05, col)
        y = top + L["head"]
        for it, ih in zip(spec.get(q) or [], L["sides"][c]):
            _badge(slide, x + 0.18, y + 0.18, 0.32, mark, col, B.C["canvas"], pt=13)
            _draw(slide, x + 0.6, y, L["w"], [_b(it if isinstance(it, str) else it.get("label", ""), B.TS["body"], 400, B.C["ink"])])
            y += ih + 0.22
    if spec.get("verdict"):
        vx, vw = B.grid(0, 12)
        vy = top + L["head"] + L["body"] + 0.2
        B.add_rect(slide, vx, vy, vw, L["verdict"] - 0.2, B.C["primary_deep"], radius_pt=4)
        B.add_text(slide, vx + 0.3, vy, vw - 0.6, L["verdict"] - 0.2,
                   [[(spec["verdict"], B.TS["insight"], 600, B.C["canvas"])]], anchor=MSO_ANCHOR.MIDDLE)


# ---------------------------------------------------------------- 11. versus

def _versus_layout(spec, h):
    rows = (spec.get("rows") or [])[:6]
    lx, lw = B.grid(0, 4)
    cx, cw = B.grid(4, 4)
    rx, rw = B.grid(8, 4)
    def side_h(d):
        d = d or {}
        b = [_b(d.get("name", ""), 20, 700)] + ([_b(d["note"], B.TS["kpi_sub"], 400, gap=0.04, name="vs_note")] if d.get("note") else [])
        return _h(b, lw - 0.3)
    head = max(0.85, max(side_h(spec.get("left")), side_h(spec.get("right"))) + 0.36)   # 名前と注記を測って帯の高さに
    cells = []
    for r in rows:
        hs = [_h([_b(r.get("left", ""), B.TS["body"])], lw - 0.4), _h([_b(r.get("label", ""), B.TS["kpi_sub"], 600)], cw - 0.2),
              _h([_b(r.get("right", ""), B.TS["body"])], rw - 0.4)]
        cells.append(max(hs) + 0.16)
    row_hs = _spread(cells, h - head, 0.8)
    return _fit(head + sum(cells), h, rows=rows, lx=lx, lw=lw, cx=cx, cw=cw, rx=rx, rw=rw, head=head, row_hs=row_hs)


def p_versus(slide, spec, deck):
    """二者の比較(A vs B): 左右に二者の名前、中央に比べる観点、行ごとに優れる側を主色の印と太字で示す。
    3案以上なら harvey_table。中央の観点は二者のどちらにも寄せない(公平に読ませる)。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _versus_layout(spec, h)
    _warn("versus", L, h)
    top = _top(y0, h, L["head"] + sum(L["row_hs"]))
    for side, x, w in (("left", L["lx"], L["lw"]), ("right", L["rx"], L["rw"])):
        d = spec.get(side) or {}
        win = d.get("focal")
        B.add_rect(slide, x, top, w, L["head"] - 0.15, B.C["primary_deep"] if win else B.C["surface_tint"], radius_pt=4)
        paras = [[(d.get("name", ""), 20, 700, B.C["canvas"] if win else B.C["ink"])]]
        if d.get("note"):
            paras.append([(d["note"], B.TS["kpi_sub"], 400, B.C["primary_pale"] if win else B.C["ink_subtle"])])
        B.add_text(slide, x, top, w, L["head"] - 0.15, paras, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
    _badge(slide, L["cx"] + L["cw"] / 2, top + (L["head"] - 0.15) / 2, 0.56, "VS", B.C["ink"], B.C["canvas"], pt=14)
    y = top + L["head"]
    for r, rh in zip(L["rows"], L["row_hs"]):
        B.add_line(slide, L["lx"], y, L["rx"] + L["rw"], y, B.C["rule"], 0.5)
        B.add_text(slide, L["cx"] + 0.1, y, L["cw"] - 0.2, rh, [[(r.get("label", ""), B.TS["kpi_sub"], 600, B.C["ink_subtle"])]],
                   anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        for side, x, w, al in (("left", L["lx"], L["lw"], PP_ALIGN.RIGHT), ("right", L["rx"], L["rw"], PP_ALIGN.LEFT)):
            win = r.get("winner") == side
            B.add_text(slide, x + 0.2, y, w - 0.4, rh, [[(r.get(side, ""), B.TS["body"], 700 if win else 400,
                                                          B.C["primary_deep"] if win else B.C["ink"])]],
                       anchor=MSO_ANCHOR.MIDDLE, align=al)
            if win:
                mx = x + w - 0.08 if side == "left" else x + 0.08
                _oval(slide, mx, y + rh / 2, 0.12, B.C["primary"])
        y += rh


# ---------------------------------------------------------------- 12. cycle

def _cycle_layout(spec, h):
    steps = (spec.get("steps") or [])[:6]
    x, w = B.grid(0, 12)
    lab_w = 2.7
    blocks = [[_b(s.get("label", ""), B.RAIL_HEAD_PT, 700, B.C["ink"])]
              + ([_b(s["desc"], B.TS["body_small"], 400, B.C["ink_subtle"], _gap("heading_body"), "cyc_desc")] if s.get("desc") else [])
              for s in steps]
    lab_h = max((_h(b, lab_w) for b in blocks), default=0.3)
    R = min(1.55, (h - 0.10 - lab_h) / 2)
    cw = 1.5 * max(R, 0.9)
    center = [_b(spec["center"], 18, 700, B.C["primary_deep"])] if spec.get("center") else []
    ch = _h(center, cw)
    # 円は半径 0.9in 以上(番号の丸と中心の文が重ならない大きさ)。中心の文は円の内側(高さ R まで)に入ること
    need = 2 * 0.9 + lab_h
    over = need > h - 0.10 or ch > max(R, 0.9) * 1.1
    return dict(need_h=need if not over or need > h - 0.10 else h + 1.0, overflow=over,
                hint="中心の文が円に入らない — 短くする" if ch > max(R, 0.9) * 1.1 else None,
                steps=steps, x=x, w=w, lab_w=lab_w, blocks=blocks, lab_h=lab_h, R=max(0.9, R), cw=cw, center=center, ch=ch)


def p_cycle(slide, spec, deck):
    """循環: 3-6 段を円周に番号の丸で置き、隣どうしを罫でつなぎ、中心に循環が生む価値を書く。
    最初の段は12時の位置、時計回り。名前と説明は丸の外側に、円の左右で寄せ方を変えて置く。"""
    import math
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _cycle_layout(spec, h)
    _warn("cycle", L, h)
    cx = L["x"] + L["w"] / 2
    cy = y0 + h / 2
    R = L["R"]
    n = len(L["steps"])
    pts = [(cx + R * math.sin(2 * math.pi * i / n), cy - R * math.cos(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        B.add_line(slide, x1, y1, x2, y2, B.C["rule"], 2.0)
    if L["center"]:
        for b in L["center"]:
            b["align"] = PP_ALIGN.CENTER
        B.stack_block(slide, cx - L["cw"] / 2, cy - L["ch"] / 2, L["cw"], B.stack_optical_height(L["center"], L["cw"]),
                      L["center"], align=PP_ALIGN.CENTER)
    for i, ((px, py), s, blk) in enumerate(zip(pts, L["steps"], L["blocks"])):
        focal = s.get("focal")
        _badge(slide, px, py, 0.56, i + 1, B.C["primary"] if focal or i == 0 else B.C["primary_deep"], B.C["canvas"], pt=16)
        bh = _h(blk, L["lab_w"])
        if abs(px - cx) < 0.3:                              # 真上・真下: 丸の横に置く
            bx, al = px + 0.42, PP_ALIGN.LEFT
            by = py - bh / 2
        elif px > cx:
            bx, al = px + 0.42, PP_ALIGN.LEFT
            by = py - bh / 2
        else:
            bx, al = px - 0.42 - L["lab_w"], PP_ALIGN.RIGHT
            by = py - bh / 2
        for b in blk:
            b["align"] = al
        bx = max(B.MX, min(bx, B.MX + B.CONTENT_W - L["lab_w"]))
        by = max(y0, min(by, y0 + h - bh))
        B.stack_block(slide, bx, by, L["lab_w"], B.stack_optical_height(blk, L["lab_w"]), blk, align=al)


# ---------------------------------------------------------------- 13. value_chain

def _vc_items(st):
    return [_b(it, B.TS["body_small"], 400, B.C["ink"], _gap("heading_body") if k else 0.0, "vc_item")
            for k, it in enumerate(st.get("items") or [])]


def _value_chain_layout(spec, h):
    st = (spec.get("stages") or [])[:6]
    cols, gut = _cols(max(1, len(st)), gut=0.06)
    chev_h = 0.72
    body = max((_h(_vc_items(s), c[1] - 0.46) for s, c in zip(st, cols)), default=0.3)
    too_tall = []
    for stage, (_x, w) in zip(st, cols):
        lines = B._text_lines(str(stage.get("label", "")), max(0.05, w - 0.3), B.TS["kpi_label"], 700)
        if lines * B.drawn_line_h(B.TS["kpi_label"]) > chev_h:
            too_tall.append(str(stage.get("label", "")))
    out = _h([_b(spec["outcome"], B.TS["insight"], 600)], B.grid(0, 12)[1] - 0.6) + 0.5 if spec.get("outcome") else 0.0
    need = chev_h + 0.2 + body + 0.36 + out
    hint = (f"value_chain の矢羽ラベルが収まらない: {', '.join(too_tall[:3])} — 名前を短くする") if too_tall else None
    if too_tall:
        need = max(need, h + 1.0)
    return _fit(need, h, hint=hint, st=st, cols=cols, chev_h=chev_h, body=body, out=out)


def p_value_chain(slide, spec, deck):
    """価値の連鎖: 段の名前を矢羽で左から右へつなぎ、各段の下にその段の活動を並べ、最後に連鎖が生む成果の帯。
    矢羽は同じ色(順番に意味がある — 色の差で優劣を示さない)、focal の段だけ主色。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _value_chain_layout(spec, h)
    _warn("value_chain", L, h)
    top = _top(y0, h, L["need_h"])
    for s, (x, w) in zip(L["st"], L["cols"]):
        focal = s.get("focal")
        last = s is L["st"][-1]
        B.add_chevron(slide, x, top, w if last else w + 0.12, L["chev_h"], B.C["primary"] if focal else B.C["primary_deep"])
        B.add_text(slide, x + 0.12, top, w - 0.3, L["chev_h"], [[(s.get("label", ""), B.TS["kpi_label"], 700, B.C["canvas"])]],
                   anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        by = top + L["chev_h"] + 0.2
        B.add_rect(slide, x, by, w - 0.06, L["body"] + 0.36, B.C["surface_tint"], radius_pt=4)
        _draw(slide, x + 0.2, by + 0.18, w - 0.46, _vc_items(s))
    if L["out"]:
        vx, vw = B.grid(0, 12)
        oy = top + L["chev_h"] + 0.2 + L["body"] + 0.36 + 0.14
        B.add_rect(slide, vx, oy, vw, L["out"] - 0.14, B.C["primary_pale"], radius_pt=4)
        B.add_text(slide, vx + 0.3, oy, vw - 0.6, L["out"] - 0.14, [[(spec["outcome"], B.TS["insight"], 600, B.C["primary_deep"])]],
                   anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------- 14. layer_stack

def _layer_stack_layout(spec, h):
    layers = (spec.get("layers") or [])[:5]
    lx, lw = B.grid(0, 3)
    bx, bw = B.grid(3, 9)
    gap = 0.10
    bodies = [_h([_b(" / ".join(l.get("items") or []) or l.get("desc", ""), B.TS["body"], 400)], bw - 0.4) for l in layers]
    mins = [max(b, _h([_b(l.get("label", ""), B.TS["kpi_label"], 700)], lw - 0.3)) + 0.32 for b, l in zip(bodies, layers)]
    hs = _spread(mins, h - gap * (len(layers) - 1), 1.0)
    return _fit(sum(mins) + gap * (len(layers) - 1), h, layers=layers, lx=lx, lw=lw, bx=bx, bw=bw, gap=gap, hs=hs)


def p_layer_stack(slide, spec, deck):
    """層の積み重ね(アーキテクチャ・提供体制): 上から下へ層を全幅の帯で積み、左に層の名前の濃い面、
    右にその層の構成要素。上の層ほど利用者に近い。focal の層だけ主色で立てる。"""
    from pptx.enum.text import MSO_ANCHOR
    y0, h = B.body_region(spec)
    L = _layer_stack_layout(spec, h)
    _warn("layer_stack", L, h)
    y = _top(y0, h, sum(L["hs"]) + L["gap"] * (len(L["layers"]) - 1))
    for l, lh in zip(L["layers"], L["hs"]):
        focal = l.get("focal")
        B.add_rect(slide, L["lx"], y, L["lw"] + 0.1, lh, B.C["primary"] if focal else B.C["primary_deep"], radius_pt=4)
        B.add_text(slide, L["lx"] + 0.2, y, L["lw"] - 0.3, lh, [[(l.get("label", ""), B.TS["kpi_label"], 700, B.C["canvas"])]],
                   anchor=MSO_ANCHOR.MIDDLE)
        B.add_rect(slide, L["bx"], y, L["bw"], lh, B.C["primary_pale"] if focal else B.C["surface_tint"], radius_pt=4)
        B.add_text(slide, L["bx"] + 0.2, y, L["bw"] - 0.4, lh,
                   [[(" / ".join(l.get("items") or []) or l.get("desc", ""), B.TS["body"], 400, B.C["ink"])]],
                   anchor=MSO_ANCHOR.MIDDLE)
        y += lh + L["gap"]


# ---------------------------------------------------------------- 15. org_chart

def _person_blocks(p, dark=False):
    ink, sub = (B.C["canvas"], B.C["primary_pale"]) if dark else (B.C["ink"], B.C["ink_subtle"])
    b = [_b(p.get("name", ""), B.RAIL_HEAD_PT + 1, 700, ink)]
    if p.get("role"):
        b.append(_b(p["role"], B.TS["kpi_sub"], 600, sub, 0.06, "org_role"))
    for k, it in enumerate(p.get("items") or []):
        b.append(_b(it, B.TS["body_small"], 400, sub, _gap("heading_body") if k == 0 else 0.04, "org_item"))
    return b


def _org_chart_layout(spec, h):
    ch = (spec.get("children") or [])[:5]
    cols, gut = _cols(max(1, len(ch)))
    rx, rw = B.grid(4, 4)
    pad = 0.2
    root_h = _h(_person_blocks(spec.get("root") or {}, True), rw - 2 * pad) + 2 * pad
    kid_h = max((_h(_person_blocks(c), cols[0][1] - 2 * pad) for c in ch), default=0.3) + 2 * pad
    link = 0.7
    need = root_h + link + kid_h
    return _fit(need, h, ch=ch, cols=cols, rx=rx, rw=rw, pad=pad, root_h=root_h, kid_h=min(kid_h, max(0.3, h - 0.10 - root_h - link)), link=link)


def p_org_chart(slide, spec, deck):
    """体制図(2階層): 上に責任者の濃い面、罫で下の2-5チームへ枝分かれし、各チームに名前・役割・担当を書く。
    3階層以上は logic_tree か図(diagram)に。focal のチームだけ淡い主色の面。"""
    y0, h = B.body_region(spec)
    L = _org_chart_layout(spec, h)
    _warn("org_chart", L, h)
    top = _top(y0, h, L["root_h"] + L["link"] + L["kid_h"])
    B.add_rect(slide, L["rx"], top, L["rw"], L["root_h"], B.C["primary_deep"], radius_pt=4)
    _draw(slide, L["rx"] + L["pad"], top + L["pad"], L["rw"] - 2 * L["pad"], _person_blocks(spec.get("root") or {}, True))
    mid = top + L["root_h"] + L["link"] / 2
    rcx = L["rx"] + L["rw"] / 2
    B.add_line(slide, rcx, top + L["root_h"], rcx, mid, B.C["ink_subtle"], 1.25)
    xs = [x + w / 2 for x, w in L["cols"]]
    B.add_line(slide, xs[0], mid, xs[-1], mid, B.C["ink_subtle"], 1.25)
    ky = top + L["root_h"] + L["link"]
    for c, (x, w), kx in zip(L["ch"], L["cols"], xs):
        B.add_line(slide, kx, mid, kx, ky, B.C["ink_subtle"], 1.25)
        B.add_rect(slide, x, ky, w, L["kid_h"], B.C["primary_pale"] if c.get("focal") else B.C["surface_tint"], radius_pt=4)
        _draw(slide, x + L["pad"], ky + L["pad"], w - 2 * L["pad"], _person_blocks(c))


# ---------------------------------------------------------------- 16. checklist

CHECK_ICON = {"done": ("circle-check", "success"), "todo": ("circle", "ink_faint"), "risk": ("circle-x", "danger")}
CHECK_WORD = {"done": "完了", "todo": "未着手", "risk": "要対応"}


def _check_blocks(it):
    b = [_b(it.get("label", ""), B.RAIL_HEAD_PT, 600, B.C["ink"])]
    if it.get("note"):
        b.append(_b(it["note"], B.TS["body_small"], 400, B.C["ink_subtle"], 0.06, "chk_note"))
    return b


def _checklist_layout(spec, h):
    items = (spec.get("items") or [])[:8]
    two = len(items) > 4
    cols, gut = _cols(2 if two else 1, gut=0.5)
    per = -(-len(items) // (2 if two else 1))
    tw = cols[0][1] - 0.6 - 0.9
    mins = [_h(_check_blocks(it), tw) + 0.26 for it in items]
    need = max((sum(mins[c * per:(c + 1) * per]) for c in range(len(cols))), default=0.3)
    cols_hs = [_spread(mins[c * per:(c + 1) * per], h, 1.15) for c in range(len(cols))]
    hs = [x for col in cols_hs for x in col]
    return _fit(need, h, items=items, cols=cols, per=per, tw=tw, hs=hs, used=max(sum(c) for c in cols_hs) if cols_hs else 0)


def p_checklist(slide, spec, deck):
    """確認表: 項目ごとに状態のアイコン(完了 ✓ / 未着手 ○ / 要対応 ×)→ 名前 → 注記、右端に状態の語。
    色だけで状態を伝えない(アイコンと語を必ず添える)。5項目以上は2列。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _checklist_layout(spec, h)
    _warn("checklist", L, h)
    top = _top(y0, h, L["used"])
    for c, (x, w) in enumerate(L["cols"]):
        y = top
        for k in range(c * L["per"], min(len(L["items"]), (c + 1) * L["per"])):
            it, ih = L["items"][k], L["hs"][k]
            icon, role = CHECK_ICON.get(it.get("status"), CHECK_ICON["todo"])
            cb = _check_blocks(it)
            oy = max(0.0, (ih - 0.12 - _h(cb, L["tw"])) / 2) - 0.04
            B.draw_icon(slide, icon, x, y + oy + 0.02, size=0.40, color=B.C[role])
            _draw(slide, x + 0.6, y + oy + 0.04, L["tw"], cb)
            B.add_text(slide, x + w - 0.9, y + oy, 0.9, 0.4, [[(it.get("status_label") or CHECK_WORD.get(it.get("status"), ""),
                                                               B.TS["kpi_sub"], 700, B.C[role] if role != "ink_faint" else B.C["ink_subtle"])]],
                       align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
            y += ih
            B.add_line(slide, x, y - 0.12, x + w, y - 0.12, B.C["rule"], 0.5)


# ---------------------------------------------------------------- 17. numbered_steps

STEP_NUM_PT = 40


def _step_blocks(st):
    b = [_b(st.get("label", ""), 18, 700, B.C["ink"])]
    if st.get("desc"):
        b.append(_b(st["desc"], B.TS["body"], 400, B.C["ink_subtle"], _gap("heading_body"), "step_desc"))
    return b


def _numbered_steps_layout(spec, h):
    steps = (spec.get("steps") or [])[:6]
    two = len(steps) > 3
    cols, gut = _cols(2 if two else 1, gut=0.6, x0=0 if two else 1, span=12 if two else 10)
    per = -(-len(steps) // (2 if two else 1))
    tw = cols[0][1] - 1.1 - 0.5
    mins = [max(_h(_step_blocks(s), tw), B.drawn_line_h(STEP_NUM_PT)) + 0.50 for s in steps]
    need = max((sum(mins[c * per:(c + 1) * per]) for c in range(len(cols))), default=0.3)
    cols_hs = [_spread(mins[c * per:(c + 1) * per], h, 1.6) for c in range(len(cols))]
    hs = [x for col in cols_hs for x in col]
    return _fit(need, h, steps=steps, cols=cols, per=per, tw=tw, hs=hs, used=max(sum(c) for c in cols_hs) if cols_hs else 0)


def p_numbered_steps(slide, spec, deck):
    """番号つきの手順: 40pt の番号 → 手順の名前 → 説明を、縦に積む(4項目以上は2列、左列から読む)。
    process_flow(横の矢羽)より説明を長く持てる。focal の手順の番号だけ主色、他は淡い主色。"""
    y0, h = B.body_region(spec)
    L = _numbered_steps_layout(spec, h)
    _warn("numbered_steps", L, h)
    top = _top(y0, h, L["used"])
    for c, (x, w) in enumerate(L["cols"]):
        y = top
        for k in range(c * L["per"], min(len(L["steps"]), (c + 1) * L["per"])):
            st, sh = L["steps"][k], L["hs"][k]
            focal = st.get("focal")
            B.add_rect(slide, x, y, w, sh - 0.14, B.C["primary_pale"] if focal else B.C["surface_tint"],
                       radius_pt=B.LAY["card"]["radius_pt"])
            sb = _step_blocks(st)
            oy = max(0.0, (sh - 0.14 - max(_h(sb, L["tw"]), B.drawn_line_h(STEP_NUM_PT))) / 2)
            B.add_text(slide, x + 0.25, y + oy - 0.06, 1.0, B.drawn_line_h(STEP_NUM_PT) + 0.1,
                       [[(f"{k + 1:02d}", STEP_NUM_PT, 700, B.C["primary"] if focal or not any(s.get("focal") for s in L["steps"])
                          else B.C["primary_pale"])]], wrap=False)
            _draw(slide, x + 1.35, y + oy, L["tw"], sb)
            y += sh


# ---------------------------------------------------------------- 18. vertical_timeline

def _event_blocks(e):
    b = [_b(e.get("label", ""), B.RAIL_HEAD_PT + 1, 700, B.C["ink"])]
    if e.get("desc"):
        b.append(_b(e["desc"], B.TS["body_small"], 400, B.C["ink_subtle"], 0.06, "ev_desc"))
    return b


def _vertical_timeline_layout(spec, h):
    ev = (spec.get("events") or [])[:7]
    dx, dw = B.grid(1, 2)
    tx, tw = B.grid(3, 8)
    hs = [max(_h(_event_blocks(e), tw - 0.4), 0.32) + 0.16 for e in ev]
    row_hs = _spread(hs, h - TL_HEAD, 0.9)          # TL_HEAD: 先頭の focal の帯が本文帯の上へ出ない余白
    return _fit(sum(hs) + TL_HEAD, h, ev=ev, dx=dx, dw=dw, tx=tx, tw=tw, row_hs=row_hs)


def p_vertical_timeline(slide, spec, deck):
    """縦の年表: 中央寄りの縦線に節目の点を置き、左に日付、右に出来事と説明。横の milestone_timeline より
    説明を長く持てる(3-7件)。focal の節目だけ大きな主色の点と淡い主色の帯。"""
    from pptx.enum.text import PP_ALIGN
    y0, h = B.body_region(spec)
    L = _vertical_timeline_layout(spec, h)
    _warn("vertical_timeline", L, h)
    top = _top(y0, h, sum(L["row_hs"]) + TL_HEAD) + TL_HEAD
    lx = L["tx"] - 0.12
    B.add_line(slide, lx, top + 0.12, lx, top + sum(L["row_hs"]) - L["row_hs"][-1] + 0.16 if L["row_hs"] else top, B.C["rule"], 2.0)
    y = top
    for e, rh in zip(L["ev"], L["row_hs"]):
        focal = e.get("focal")
        if focal:
            eh = _h(_event_blocks(e), L["tw"] - 0.4)
            B.add_rect(slide, L["tx"] + 0.1, y - TL_HEAD, L["tw"] - 0.1, min(eh + 0.16, rh - 0.02), B.C["primary_pale"], radius_pt=4)
        _oval(slide, lx, y + 0.16, 0.24 if focal else 0.16, B.C["primary"] if focal else B.C["primary_deep"])
        B.add_text(slide, L["dx"], y, L["dw"] - 0.3, 0.36, [[(e.get("date", ""), B.TS["kpi_label"], 700,
                                                            B.C["primary_deep"])]], align=PP_ALIGN.RIGHT, wrap=False)
        _draw(slide, L["tx"] + 0.3, y, L["tw"] - 0.4, _event_blocks(e))
        y += rh


# ---------------------------------------------------------------- 19. faq

def _qa_blocks(p):
    return [_b(p.get("q", ""), B.RAIL_HEAD_PT + 1, 700, B.C["ink"]),
            _b(p.get("a", ""), B.TS["body"], 400, B.C["ink_subtle"], _gap("heading_body"), "qa_a")]


def _faq_layout(spec, h):
    pairs = (spec.get("pairs") or [])[:6]
    two = len(pairs) > 3
    cols, gut = _cols(2 if two else 1, gut=0.5)
    per = -(-len(pairs) // (2 if two else 1))
    tw = cols[0][1] - 0.62 - 0.4
    mins = [_h(_qa_blocks(p), tw) + 0.54 for p in pairs]
    need = max((sum(mins[c * per:(c + 1) * per]) for c in range(len(cols))), default=0.3)
    cols_hs = [_spread(mins[c * per:(c + 1) * per], h, 1.8) for c in range(len(cols))]
    hs = [x for col in cols_hs for x in col]
    return _fit(need, h, pairs=pairs, cols=cols, per=per, tw=tw, hs=hs, used=max(sum(c) for c in cols_hs) if cols_hs else 0)


def p_faq(slide, spec, deck):
    """想定問答: 主色の Q の印 → 問い(太字)→ 答え。経営会議の想定質問、導入時のよくある質問に。
    4問以上は2列。答えは一文目で言い切る(印象ではなく判断の材料を書く)。"""
    y0, h = B.body_region(spec)
    L = _faq_layout(spec, h)
    _warn("faq", L, h)
    top = _top(y0, h, L["used"])
    for c, (x, w) in enumerate(L["cols"]):
        y = top
        for k in range(c * L["per"], min(len(L["pairs"]), (c + 1) * L["per"])):
            hh = L["hs"][k]
            B.add_rect(slide, x, y, w, hh - 0.14, B.C["surface_tint"], radius_pt=B.LAY["card"]["radius_pt"])
            qb = _qa_blocks(L["pairs"][k])
            oy = max(0.0, (hh - 0.14 - _h(qb, L["tw"])) / 2)
            _badge(slide, x + 0.4, y + oy + 0.16, 0.40, "Q", B.C["primary_deep"], B.C["canvas"], pt=15)
            _draw(slide, x + 0.82, y + oy, L["tw"], qb)
            y += hh


# ---------------------------------------------------------------- 20. team

def _initials(p):
    if p.get("initials"):
        return str(p["initials"])[:2]
    return str(p.get("name", "?")).strip()[:1]


def _team_layout(spec, h):
    ppl = (spec.get("people") or [])[:6]
    n = max(1, len(ppl))
    cols_n = n if n <= 3 else 3
    cols, gut = _cols(cols_n)
    pad = 0.24
    disc = 0.72
    body = max((_h(_person_blocks({**p, "items": [p["desc"]] if p.get("desc") else []}), cols[0][1] - 2 * pad - disc - 0.2)
                for p in ppl), default=0.3)
    tile_min = 2 * pad + max(disc, body)
    rows, tile_h, need = _tile_grid(n, cols_n, h, tile_min, gut)
    return _fit(need, h, ppl=ppl, cols=cols, cols_n=cols_n, gut=gut, pad=pad, disc=disc, tile_h=min(tile_h, max(tile_min, 3.0)), rows=rows)


def p_team(slide, spec, deck):
    """体制の顔ぶれ: 人ごとに頭文字の円 → 名前 → 役割 → 担当の一文。写真が無くても顔ぶれが読める。
    頭文字は initials で指定できる(既定は名前の最初の1字)。focal の人(責任者)だけ濃い円。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _team_layout(spec, h)
    _warn("team", L, h)
    top = _top(y0, h, L["rows"] * L["tile_h"] + L["gut"] * (L["rows"] - 1))
    for i, p in enumerate(L["ppl"]):
        r, c = divmod(i, L["cols_n"])
        x, w = L["cols"][c]
        y = top + r * (L["tile_h"] + L["gut"])
        B.add_rect(slide, x, y, w, L["tile_h"], B.C["surface_tint"], radius_pt=B.LAY["card"]["radius_pt"])
        focal = p.get("focal")
        dcx, dcy = x + L["pad"] + L["disc"] / 2, y + L["pad"] + L["disc"] / 2
        _oval(slide, dcx, dcy, L["disc"], B.C["primary_deep"] if focal else B.C["primary_pale"])
        B.add_text(slide, dcx - L["disc"] / 2, dcy - L["disc"] / 2 - B.ink_center_offset_in(22), L["disc"], L["disc"],
                   [[(_initials(p), 22, 700, B.C["canvas"] if focal else B.C["primary_deep"])]],
                   align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        tx = x + L["pad"] + L["disc"] + 0.2
        _draw(slide, tx, y + L["pad"], w - (tx - x) - L["pad"],
              _person_blocks({**p, "items": [p["desc"]] if p.get("desc") else []}))


# ---------------------------------------------------------------- 21. pricing_tiers

def _tier_blocks(t, dark):
    ink, sub = (B.C["canvas"], B.C["primary_pale"]) if dark else (B.C["ink"], B.C["ink_subtle"])
    b = [_b(t.get("name", ""), 18, 700, ink)]
    parts = [(str(t.get("price", "")), 36, 700, ink if dark else B.C["primary_deep"])]
    if t.get("unit"):
        parts.append((" " + t["unit"], B.TS["kpi_sub"], 600, sub))
    b.append({"parts": parts, "size": 36, "kind": "numeral", "gap_before": _gap("metric_subline"), "gap_name": "tier_price"})
    if t.get("note"):
        b.append(_b(t["note"], B.TS["body_small"], 400, sub, _gap("heading_body"), "tier_note"))
    return b


def _tier_features(t):
    features = t.get("features")
    return [feature for feature in features if isinstance(feature, str)] if isinstance(features, list) else []


TAG_H = 0.36
FEAT_GAP = 0.05


def _pricing_layout(spec, h):
    tiers = (spec.get("tiers") or [])[:PRICING_MAX_TIERS]
    cols, gut = _cols(max(1, len(tiers)))
    pad = 0.22
    tw = cols[0][1] - 2 * pad
    head = max((_h(_tier_blocks(t, False), tw) for t in tiers), default=0.5)
    feats = max((sum(_h([_b(f, B.TS["body_small"])], tw - 0.34) + FEAT_GAP for f in _tier_features(t)) for t in tiers), default=0)
    need = TAG_H + 2 * pad + head + 0.40 + feats
    hint = None
    if any(_value_w({"value": t.get("price"), "unit": t.get("unit")}, 36, B.TS["kpi_sub"]) > tw for t in tiers):
        need = max(need, h + 1.0)                 # 価格(+単位)は1行に入ること
        hint = "価格と単位が1行に入らない — 案を減らすか単位を短くする"
    return _fit(need, h, hint=hint, tiers=tiers, cols=cols, pad=pad, tw=tw, head=head, card_h=min(max(need, (h - 0.10) * 0.85), h - 0.10))


def p_pricing_tiers(slide, spec, deck):
    """料金プラン(段階の比較): 2-4 案を同じ高さのカードで並べ、名前 → 価格 → 注記 → ✓ の機能一覧。
    推奨(focal)のカードだけ濃い主色の面にして「推奨」の札を付ける。機能は上位の案ほど増える順に書く。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _pricing_layout(spec, h)
    _warn("pricing_tiers", L, h)
    top = _top(y0, h, L["card_h"])
    for t, (x, w) in zip(L["tiers"], L["cols"]):
        dark = bool(t.get("focal"))
        B.add_rect(slide, x, top, w, L["card_h"], B.C["primary_deep"] if dark else B.C["surface_tint"],
                   radius_pt=B.LAY["card"]["radius_pt"])
        if dark:
            # 推奨の札はカードの上端の帯(TAG_H)。全カードの中身を同じ高さから始めるので、価格の行が横一列にそろう
            B.add_rect(slide, x, top, w, TAG_H, B.C["primary"], radius_pt=B.LAY["card"]["radius_pt"])
            B.add_rect(slide, x, top + TAG_H / 2, w, TAG_H / 2, B.C["primary"])
            B.add_text(slide, x, top, w, TAG_H, [[(spec.get("focal_label", "推奨"), B.TS["kpi_sub"], 700, B.C["canvas"])]],
                       align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        _draw(slide, x + L["pad"], top + TAG_H + L["pad"], L["tw"], _tier_blocks(t, dark))
        fy = top + TAG_H + L["pad"] + L["head"] + 0.18
        B.add_line(slide, x + L["pad"], fy, x + w - L["pad"], fy, B.C["primary"] if dark else B.C["rule"], 0.75)
        fy += 0.22
        for f in _tier_features(t):
            B.add_text(slide, x + L["pad"], fy - 0.02, 0.3, 0.3, [[("✓", B.TS["body_small"], 700,
                                                                    B.C["primary_pale"] if dark else B.C["primary"])]], wrap=False)
            fb = [_b(f, B.TS["body_small"], 400, B.C["canvas"] if dark else B.C["ink"])]
            _draw(slide, x + L["pad"] + 0.34, fy, L["tw"] - 0.34, fb)
            fy += _h(fb, L["tw"] - 0.34) + FEAT_GAP


# ---------------------------------------------------------------- 22. quote_grid

QG_MARK_PT = 36            # 引用符。箱は字の行の高さぶん取り、声はその下から始める(枠を重ねない)


def _qg_blocks(q):
    text = str(q.get("quote", "")).strip("「」")
    return [_b(f"「{text}」", 17, 600, B.C["ink"]),
            _b(q.get("attribution", ""), B.TS["kpi_sub"], 600, B.C["primary_deep"], _gap("item"), "qg_attr")] + (
        [_b(q["role"], B.TS["body_small"], 400, B.C["ink_subtle"], 0.04, "qg_role")] if q.get("role") else [])


def _quote_grid_layout(spec, h):
    qs = (spec.get("quotes") or [])[:4]
    n = max(1, len(qs))
    cols_n = n if n <= 3 else 2
    cols, gut = _cols(cols_n)
    pad = 0.24
    body = max((_h(_qg_blocks(q), cols[0][1] - 2 * pad) for q in qs), default=0.3)
    tile_min = 2 * pad + B.drawn_line_h(QG_MARK_PT) + body
    rows, tile_h, need = _tile_grid(n, cols_n, h, tile_min, gut)
    return _fit(need, h, qs=qs, cols=cols, cols_n=cols_n, gut=gut, pad=pad, tile_h=min(tile_h, max(tile_min, 3.4)), rows=rows)


def p_quote_grid(slide, spec, deck):
    """声の束: 2-4 人の短い声をカードで並べ、それぞれに だれが(立場)を添える。1 人の声を深く見せるなら
    pull_quote。声どうしが同じことを言うなら1枚にまとめる(数を水増ししない)。focal の声だけ淡い主色。"""
    y0, h = B.body_region(spec)
    L = _quote_grid_layout(spec, h)
    _warn("quote_grid", L, h)
    top = _top(y0, h, L["rows"] * L["tile_h"] + L["gut"] * (L["rows"] - 1))
    for i, q in enumerate(L["qs"]):
        r, c = divmod(i, L["cols_n"])
        x, w = L["cols"][c]
        y = top + r * (L["tile_h"] + L["gut"])
        B.add_rect(slide, x, y, w, L["tile_h"], B.C["primary_pale"] if q.get("focal") else B.C["surface_tint"],
                   radius_pt=B.LAY["card"]["radius_pt"])
        B.add_text(slide, x + L["pad"] - 0.04, y + L["pad"] - 0.06, 0.6, B.drawn_line_h(QG_MARK_PT), [[("“", QG_MARK_PT, 700, B.C["primary"])]],
                   wrap=False)
        _draw(slide, x + L["pad"], y + L["pad"] + B.drawn_line_h(QG_MARK_PT), w - 2 * L["pad"], _qg_blocks(q))


# ---------------------------------------------------------------- 23. nine_box

def _nine_box_layout(spec, h):
    items = (spec.get("items") or [])[:12]
    gx, gw = B.grid(1, 7)
    rx, rw = B.grid(8, 4)
    axis = 0.4
    cell_w = (gw - axis) / 3
    per_cell = {}
    for it in items:
        per_cell.setdefault((it.get("x", 0), it.get("y", 0)), []).append(it)
    cell_need = max((sum(_h([_b(it.get("label", ""), B.TS["kpi_sub"], 600)], cell_w - 0.24) + 0.06 for it in its)
                     for its in per_cell.values()), default=0.3) + 0.2
    cell_h = min(max(cell_need, (h - 0.10 - axis) / 3), (h - 0.10 - axis) / 3)
    rail = _h([_b(spec["reading"], B.TS["body"], 400)], rw) + 0.5 if spec.get("reading") else 0.0
    need = max(3 * cell_need + axis, rail)
    return _fit(need, h, items=items, gx=gx, gw=gw, rx=rx, rw=rw, axis=axis, cell_w=cell_w, cell_h=cell_h, per_cell=per_cell)


def p_nine_box(slide, spec, deck):
    """9 マス(3 × 3): 2 軸を低・中・高で区切り、各マスに対象を置く(人材・事業ポートフォリオ・顧客)。
    右上(両軸とも高い)のマスほど濃い主色、左下ほど淡い面。対象は x / y(0-2)で置き、右に読み方を書く。"""
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    y0, h = B.body_region(spec)
    L = _nine_box_layout(spec, h)
    _warn("nine_box", L, h)
    top = _top(y0, h, 3 * L["cell_h"] + L["axis"])
    ox = L["gx"] + L["axis"]
    shades = [B.C["surface_tint"], B.C["primary_pale"], B.C["primary"]]
    for gy in range(3):
        for gxi in range(3):
            score = gxi + (2 - gy)
            fill = shades[0] if score <= 1 else (shades[1] if score <= 3 else shades[2])
            dark = fill == shades[2]
            cx = ox + gxi * L["cell_w"]
            cy = top + gy * L["cell_h"]
            B.add_rect(slide, cx + 0.03, cy + 0.03, L["cell_w"] - 0.06, L["cell_h"] - 0.06, fill, radius_pt=3)
            its = L["per_cell"].get((gxi, 2 - gy), [])
            blocks = [_b(it.get("label", ""), B.TS["kpi_sub"], 700 if it.get("focal") else 600,
                         B.C["canvas"] if dark else B.C["ink"], 0.06 if k else 0.0, "nb_item") for k, it in enumerate(its)]
            _draw(slide, cx + 0.12, cy + 0.12, L["cell_w"] - 0.24, blocks)
    B.add_text(slide, ox, top + 3 * L["cell_h"] + 0.04, 3 * L["cell_w"], 0.32,
               [[(f"{spec.get('x_label', '')} →", B.TS["kpi_sub"], 600, B.C["ink_subtle"])]], align=PP_ALIGN.CENTER, wrap=False)
    B.add_text(slide, L["gx"] - 0.2, top, L["axis"] + 0.1, 3 * L["cell_h"],
               [[(f"{spec.get('y_label', '')} ↑", B.TS["kpi_sub"], 600, B.C["ink_subtle"])]],
               anchor=MSO_ANCHOR.MIDDLE, wrap=True)
    if spec.get("reading"):           # note はフッターの注記(共通欄)。マスの読み方は reading
        _draw(slide, L["rx"], top, L["rw"], [_b(spec.get("reading_heading", "読み方"), 16, 600, B.C["primary_deep"]),
                                             _b(spec["reading"], B.TS["body"], 400, B.C["ink_subtle"], _gap("heading_body"), "nb_note")])


RENDERERS = {
    "big_number": p_big_number, "number_strip": p_number_strip, "progress_bars": p_progress_bars,
    "ranking": p_ranking, "funnel": p_funnel, "pyramid": p_pyramid, "composition_bar": p_composition_bar,
    "heatmap_table": p_heatmap_table, "swot": p_swot, "pros_cons": p_pros_cons, "versus": p_versus,
    "cycle": p_cycle, "value_chain": p_value_chain, "layer_stack": p_layer_stack, "org_chart": p_org_chart,
    "checklist": p_checklist, "numbered_steps": p_numbered_steps, "vertical_timeline": p_vertical_timeline,
    "faq": p_faq, "team": p_team, "pricing_tiers": p_pricing_tiers, "quote_grid": p_quote_grid,
    "nine_box": p_nine_box, "target_bars": p_target_bars,
}
LAYOUTS = {
    "big_number": _big_number_layout, "number_strip": _number_strip_layout, "progress_bars": _progress_bars_layout,
    "ranking": _ranking_layout, "funnel": _funnel_layout, "pyramid": _pyramid_layout,
    "composition_bar": _composition_layout, "heatmap_table": _heatmap_layout, "swot": _swot_layout,
    "pros_cons": _pros_cons_layout, "versus": _versus_layout, "cycle": _cycle_layout,
    "value_chain": _value_chain_layout, "layer_stack": _layer_stack_layout, "org_chart": _org_chart_layout,
    "checklist": _checklist_layout, "numbered_steps": _numbered_steps_layout,
    "vertical_timeline": _vertical_timeline_layout, "faq": _faq_layout, "team": _team_layout,
    "pricing_tiers": _pricing_layout, "quote_grid": _quote_grid_layout, "nine_box": _nine_box_layout,
    "target_bars": _target_bars_layout,
}
