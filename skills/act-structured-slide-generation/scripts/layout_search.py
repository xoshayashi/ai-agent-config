#!/usr/bin/env python3
"""composite の配置探索: 役割つきのブロックから grid の候補を列挙し、検証できる指標で順位を付ける。

考え方(references/layout-search.md):
- 書き手(LLM)は「何が主役か」を決める — 読み手の問いに答えるブロックに role: focal、補足に support、
  結論の一文に conclusion、前提に context。これは内容の判断で、推論が強い部分。
- 配置は候補を文法で列挙し、描画と同じ寸法計算(build_deck._composite_layout / block_need_h)で測って
  点を付ける。視覚言語モデルの美的判断は当てにならない(AeSlides 2026: 検出が偶然以下のこともある)
  ので、見た目の良し悪しは計算で測る(LayoutPrompter の ranker、AeSlides の verifiable reward)。
- 点数の内訳を残す。上位案のどれを採るかは、書き手が内容の理由で決めてよい(既定は最上位)。

使い方:
  python3 scripts/layout_search.py deck.json --slide 3 --top 3          # 候補と内訳を表示
  python3 scripts/layout_search.py deck.json --slide 3 --emit out.json  # 上位案を grid に書いた deck
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROLES = ("focal", "support", "context", "conclusion")

# 1 行に並べる列の取り分。左右非対称(主役を広く)と等分の両方を持つ。順序は各ブロックの並べ替えで作る
ROW_SPANS = {
    1: [(12,)],
    2: [(6, 6), (7, 5), (8, 4), (9, 3), (5, 7), (4, 8), (3, 9)],
    3: [(4, 4, 4), (6, 3, 3), (3, 3, 6), (5, 4, 3), (3, 4, 5), (6, 4, 2)],
    4: [(3, 3, 3, 3), (6, 2, 2, 2)],
}
WEIGHT_PAIRS = [(1, 1), (2, 1), (3, 1), (1, 2), (1, 3)]
# 定番の組み立て(consulting-page-catalogue.md)。行ごとの (列, 種別) が一致する案に小さな加点 —
# 似た手本を当てる効果(LayoutPrompter の dynamic exemplar selection)を、検索ではなく既知の型で近似する
CATALOGUE = {
    ((("7", "chart"), ("5", "text")),),
    ((("7", "chart"), ("5", "text")), (("12", "callout"),)),
    ((("12", "chart"),), (("12", "callout"),)),
    ((("12", "kpi"),), (("12", "table"),)),
    ((("3", "kpi"), ("9", "chart")),),
    ((("6", "chart"), ("6", "chart")), (("12", "callout"),)),
    ((("4", "text"), ("4", "text"), ("4", "text")), (("12", "callout"),)),
    ((("4", "text"), ("4", "text"), ("4", "callout")),),
    ((("12", "callout"),), (("4", "text"), ("4", "text"), ("4", "text"))),
}
STRETCHY = ("chart", "table", "diagram")


def role_of(b: dict, i: int, blocks: list[dict]) -> str:
    """明示が無ければ: callout は結論。本文ブロックがすべて同じ種別(論点・示唆・打ち手の text 3枚など)
    なら同格の support — 1枚目だけを主役にして大きくしない。そうでなければ最初の本文ブロックが主役。"""
    r = b.get("role")
    if r in ROLES:
        return r
    if b.get("type") == "callout":
        return "conclusion"
    body = [x for x in blocks if x.get("type") != "callout"]
    if any(x.get("role") == "focal" for x in blocks):
        return "support"
    if len(body) > 1 and len({x.get("type") for x in body}) == 1 and not any(x.get("role") for x in body):
        return "support"
    # 主役の既定は「役割を書いていない最初の本文ブロック」— 1枚目に support と明示されていても主役が消えない
    first_free = next((j for j, x in enumerate(blocks) if x.get("type") != "callout" and not x.get("role")), None)
    return "focal" if i == first_free else "support"


def _orderings(body: list[int], blocks: list[dict], roles: list[str]):
    """本文ブロックの並び順。同じ種別・同じ役割の同格ブロック(論点カード3枚など)は、書き手の順を保つ —
    入れ替えても同じ形になるうえ、同格の並び順は書き手の決めた読み順だから。"""
    sig = {i: (blocks[i].get("type"), roles[i]) for i in body}
    for perm in itertools.permutations(body):
        ok = True
        for a_, b_ in itertools.combinations(range(len(perm)), 2):
            if sig[perm[a_]] == sig[perm[b_]] and perm[a_] > perm[b_]:
                ok = False
                break
        if ok:
            yield perm


def _rows_of(body: list[int], conclusion: list[int], perms: list):
    """本文ブロック(添字)の並べ方 × 結論の行。結論は全幅の最下行(複数なら横に並べる)。"""
    k = len(body)
    shapes = []
    # 1 行
    for spans in ROW_SPANS.get(k, []):
        for perm in perms:
            shapes.append([list(zip(spans, perm))])
    # 2 行: 上 a 個 / 下 k-a 個
    for a in range(1, k):
        top_spans = ROW_SPANS.get(a, [])
        bot_spans = ROW_SPANS.get(k - a, [])
        for perm in perms:
            for ts in top_spans:
                for bs in bot_spans:
                    shapes.append([list(zip(ts, perm[:a])), list(zip(bs, perm[a:]))])
    out = []
    concl_row = []
    if conclusion:
        cs = ROW_SPANS.get(len(conclusion), [(12,)])[0]
        concl_row = [list(zip(cs, conclusion))]
    for sh in shapes:
        if len(sh) + len(concl_row) > 3:
            continue
        out.append(sh + concl_row)
    # 結論を本文の右に置く SCR 型(本文 2 個 + 結論 1 個 → 1 行 3 列)
    if len(conclusion) == 1 and 1 <= k <= 2:
        for spans in ROW_SPANS[k + 1]:
            for perm in perms:
                out.append([list(zip(spans, list(perm) + conclusion))])
    return out


def _weights_for(n_rows: int, has_concl: bool):
    if n_rows == 1:
        return [(1,)]
    if n_rows == 2:
        return WEIGHT_PAIRS
    return [(2, 1, 1), (1, 1, 1), (3, 2, 1), (2, 2, 1)]


def candidates(blocks: list[dict]):
    """(grid, roles) を列挙する。grid は composite の grid と同じ形。"""
    roles = [role_of(b, i, blocks) for i, b in enumerate(blocks)]
    body = [i for i, r in enumerate(roles) if r != "conclusion"]
    concl = [i for i, r in enumerate(roles) if r == "conclusion"]
    seen = set()
    perms = list(_orderings(body, blocks, roles))
    for shape in _rows_of(body, concl, perms):
        for wts in _weights_for(len(shape), bool(concl)):
            key = (tuple(tuple(r) for r in shape), wts)
            if key in seen:
                continue
            seen.add(key)
            grid = [{"height": wt, "cells": [{"span": sp, "block": blocks[idx]} for sp, idx in row]}
                    for row, wt in zip(shape, wts)]
            yield grid, roles, shape


def score(spec: dict, grid: list, roles: list[str], shape, bd, h: float) -> dict | None:
    """1 案の点数と内訳。入らない・グラフが狭すぎる案は None(候補から外す)。
    すべて 0-1 の「良さ」に正規化し、重みつきの和を total にする(重みは定数で固定 — 学習しない)。"""
    trial = {**spec, "grid": grid}
    L = bd._composite_layout(trial, h)
    if L["overflow"]:
        return None
    rects = []        # (x, y, w, h, block_index)
    y = 0.0
    for row, cells, rh in zip(shape, L["cells"], L["row_h"]):
        for (sp, idx), (cx, cw, b) in zip(row, cells):
            t = b.get("type")
            if t == "chart" and sp < 4:
                return None
            if t == "table" and cw < 1.05 * len((b.get("table") or {}).get("headers", [])):
                return None
            rects.append((cx, y, cw, rh, idx))
        y += rh + L["GAP"]
    total_h = max(1e-6, y - L["GAP"])
    used = sum(L["row_h"]) / max(1e-6, L["avail"])                     # 本文帯の使い方(1 = 全部)
    areas = {idx: w * hh for _x, _y, w, hh, idx in rects}
    focal = [i for i, r in enumerate(roles) if r == "focal"]
    others = [a for i, a in areas.items() if i not in focal and roles[i] != "conclusion"]
    # 階層: 主役の面積が他の本文ブロックより大きいほど良い(最大の 1.2 倍で満点)。KPI と callout は
    # 面積ではなく大きな数字・濃い面で立つので、最上段に置かれていれば満たす(下の段なら半分)
    order0 = sorted(rects, key=lambda r: (round(r[1], 2), r[0]))
    if focal and others:
        fb = grid_block(grid, focal[0], shape)
        if fb.get("type") in ("kpi", "callout"):
            top_y = order0[0][1]
            hierarchy = 1.0 if any(r[4] == focal[0] and abs(r[1] - top_y) < 1e-6 for r in rects) else 0.5
        else:
            hierarchy = min(1.0, areas[focal[0]] / (1.2 * max(others)))
    else:
        hierarchy = 1.0
    # 一貫性: 同じ種別・同じ役割のブロック(同格の論点カード等)は同じ大きさで並ぶほど良い(類同の原理)
    groups: dict = {}
    for i, r in enumerate(roles):
        b = blocks_of(grid, shape).get(i, {})
        if r != "conclusion":
            groups.setdefault((b.get("type"), r), []).append(areas.get(i, 0.0))
    consistency = 1.0
    for g in groups.values():
        if len(g) > 1 and max(g) > 0:
            consistency -= 0.6 * (1.0 - min(g) / max(g))
    consistency = max(0.0, consistency)
    # 読み順: 主役が最初(上・左)に読まれるほど良い。結論は最後
    order = sorted(rects, key=lambda r: (round(r[1], 2), r[0]))
    pos = [r[4] for r in order]
    reading = 1.0
    if focal:
        reading -= 0.35 * pos.index(focal[0]) / max(1, len(pos) - 1)
    concl = [i for i, r in enumerate(roles) if r == "conclusion"]
    if concl and pos[-1] not in concl and not any(r[1] == order[-1][1] for r in rects if r[4] in concl):
        reading -= 0.25
    # 空洞: 伸びない中身(テキスト・KPI)が、グラフや表と同じ行で高く引き伸ばされた下の空き
    hollow_pen = 0.0
    for (row, cells, rh) in zip(shape, L["cells"], L["row_h"]):
        for _sp_idx, (_cx, cw, b) in zip(row, cells):
            if b.get("type") in ("text", "kpi"):
                need = bd.block_need_h(b, cw)
                hollow_pen = max(hollow_pen, max(0.0, 1.0 - need / max(1e-6, rh)) - 0.35)
    fill = max(0.0, 1.0 - hollow_pen / 0.65)
    # 重心: 中身の量(必要高 × 幅)で重みを付けた重心が、本文帯の中心から外れるほど減点(AeSlides の
    # visual imbalance を、描画前の矩形で近似。横のずれを重く見る)
    x0 = bd.grid(0, 12)[0]
    W = bd.grid(0, 12)[1]
    mass = cx_sum = cy_sum = 0.0
    for x, yy, w, hh, idx in rects:
        b = grid_block(grid, idx, shape)
        ink = min(hh, bd.block_need_h(b, w)) if b.get("type") not in STRETCHY else hh * 0.8
        m = w * ink
        mass += m
        cx_sum += m * (x + w / 2)
        cy_sum += m * (yy + ink / 2)
    if mass > 0:
        dx = (cx_sum / mass - (x0 + W / 2)) / W
        dy = (cy_sum / mass - total_h / 2) / max(1e-6, total_h)
        dist = ((dx / 0.12) ** 2 + (dy / 0.25) ** 2) ** 0.5
        balance = max(0.0, 1.0 - max(0.0, dist - 1.0) / 2.0)
    else:
        balance = 1.0
    # 形の良さ: グラフの縦横比(横長 1.2-2.6 が読みやすい)、セル数の少なさ
    shape_ok = 1.0
    for x, yy, w, hh, idx in rects:
        b = grid_block(grid, idx, shape)
        if b.get("type") == "chart":
            ar = w / max(1e-6, hh)
            if ar < 1.0 or ar > 3.2:
                shape_ok -= 0.4
            elif ar < 1.2 or ar > 2.6:
                shape_ok -= 0.15
    shape_ok = max(0.0, shape_ok)
    # 読みやすさ: 本文の1行が短すぎる列は読めない(和文 16pt で 1 行 13 字 ≈ 2.9in を下限の目安 —
    # 3 列の論点カードは card の内側余白を引いて約 15 字で、これは定番として通す)。
    # KPI は1つあたり KPI_MIN_W、表は列あたり 1.05in を割ると詰まる(後者は候補から外してある)
    em = bd.TS["body"] / 72.0
    legible = 1.0
    for x, yy, w, hh, idx in rects:
        b = grid_block(grid, idx, shape)
        if b.get("type") == "text":
            chars = (w - (2 * bd.CARD_INSET if b.get("style") == "card" else 0.0)) / em
            if chars < 13:
                legible -= 0.5 * (13 - chars) / 13 + 0.2
        if b.get("type") == "callout":
            chars = w / (bd.TS["insight"] / 72.0)
            if chars < 14:
                legible -= 0.3
    legible = max(0.0, legible)
    sig = tuple(tuple((str(c["span"]), c["block"].get("type")) for c in r["cells"]) for r in grid)
    prior = 1.0 if sig in CATALOGUE else 0.0
    simplicity = 1.0 - 0.1 * (len(rects) - 1) - 0.1 * (len(grid) - 1)
    parts = {"hierarchy": hierarchy, "reading": reading, "fill": fill, "legible": legible,
             "consistency": consistency, "balance": balance, "shape": shape_ok, "used": min(1.0, used),
             "catalogue": prior, "simplicity": simplicity}
    weights = {"hierarchy": 0.18, "reading": 0.12, "fill": 0.14, "legible": 0.14, "consistency": 0.12,
               "balance": 0.09, "shape": 0.09, "used": 0.06, "catalogue": 0.04, "simplicity": 0.02}
    total = sum(weights[k] * v for k, v in parts.items())
    return {"total": round(total, 4), "parts": {k: round(v, 3) for k, v in parts.items()},
            "geom": tuple(round(v, 2) for v in L["row_h"])}


def blocks_of(grid, shape) -> dict:
    return {i: c["block"] for row, r in zip(shape, grid) for (sp, i), c in zip(row, r["cells"])}


def grid_block(grid, idx, shape):
    for row, r in zip(shape, grid):
        for (sp, i), c in zip(row, r["cells"]):
            if i == idx:
                return c["block"]
    return {}


def describe(grid: list) -> str:
    """人が読む 1 行: 行を / で、セルを空白で区切る(例: chart:7 text:5 / callout:12, h=3:1)。"""
    rows = " / ".join(" ".join(f"{c['block'].get('type')}:{c['span']}" for c in r["cells"]) for r in grid)
    hs = ":".join(str(r.get("height", 1)) for r in grid)
    return f"{rows}  (h {hs})"


def search(spec: dict, top: int = 3, bd=None) -> list[dict]:
    """composite の blocks から grid 候補を順位づけて返す。[{grid, total, parts, desc}]。"""
    if bd is None:
        import build_deck as bd
    blocks = [b for b in (spec.get("blocks") or []) if isinstance(b, dict)]
    if not blocks:
        return []
    spec = {**spec, "blocks": blocks}
    _, h = bd.body_region(spec)
    seen_geom: dict = {}
    # 同じブロック・同じ幅の必要高は何度も測らない(候補は数百、ブロックは数個)。探索の間だけ差し替える
    orig = bd.block_need_h
    cache: dict = {}

    def memo(b, w):
        k = (id(b), round(w, 4))
        if k not in cache:
            cache[k] = orig(b, w)
        return cache[k]

    bd.block_need_h = memo
    try:
        for grid, roles, shape in candidates(blocks):
            sc = score(spec, grid, roles, shape, bd, h)
            if sc is None:
                continue
            desc = describe(grid)
            key = desc.split("  (h")[0]          # 同じ並びの重み違いは最良の1案だけ残す(上位案は並びで比べる)
            entry = {"grid": grid, "desc": desc, **{k: v for k, v in sc.items() if k != "geom"}}
            prev = seen_geom.get(key)
            if prev is None or entry["total"] > prev["total"]:
                seen_geom[key] = entry
    finally:
        bd.block_need_h = orig
    ranked = list(seen_geom.values())
    # 同点は「行が少ない → 記述が短い」で決める(毎回同じ案を返す)
    ranked.sort(key=lambda c: (-c["total"], len(c["grid"]), c["desc"]))
    return ranked[:top]


def resolve(spec: dict, bd=None) -> list:
    """build / validate 用: grid が無く blocks がある composite に、最上位案の grid を返す。案が無ければ []。"""
    best = search(spec, top=1, bd=bd)
    return best[0]["grid"] if best else []


def main() -> int:
    ap = argparse.ArgumentParser(description="composite の配置候補を、検証できる指標で順位づける")
    ap.add_argument("deck")
    ap.add_argument("--slide", type=int, required=True, help="1 始まりのスライド番号")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--emit", help="上位案ごとに grid を書き込んだ deck.json を出力(並べて見比べる用)")
    args = ap.parse_args()
    deck = json.loads(Path(args.deck).read_text())
    import build_deck as bd
    tpl = bd.template_of(deck)                  # テンプレートの寸法で測る(build と同じ手順)
    if tpl != "standard":
        bd._apply_tokens(bd.resolve_tokens(tpl))
    s = deck["slides"][args.slide - 1]
    if s.get("pattern") != "composite" or not s.get("blocks"):
        print("このスライドは blocks を持つ composite ではない(grid を省き、blocks に role を付けて書く)")
        return 1
    ranked = search(s, top=args.top, bd=bd)
    if not ranked:
        print("入る配置が無い — ブロックの中身を減らすか、スライドを分ける")
        return 1
    for k, c in enumerate(ranked, start=1):
        parts = " ".join(f"{n}={v:.2f}" for n, v in c["parts"].items())
        print(f"#{k}  {c['total']:.3f}  {c['desc']}\n    {parts}")
    if args.emit:
        slides = []
        for c in ranked:
            slides.append({**{k: v for k, v in s.items() if k != "blocks"}, "grid": c["grid"]})
        Path(args.emit).write_text(json.dumps({**deck, "slides": slides}, ensure_ascii=False, indent=1))
        print(f"emitted {len(slides)} candidate slides → {args.emit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
