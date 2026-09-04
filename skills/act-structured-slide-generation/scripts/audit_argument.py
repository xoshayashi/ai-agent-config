#!/usr/bin/env python3
"""論証の検査: 主張に逃げ道が無いかを、計算と参照で確かめる。

Usage: audit_argument.py <deck.json> [--strict]

このゲートが見るのは「構造と算数」であって「真偽」ではない。だが、次のものは構造的に
起こせなくなる:
  - 図表が示していない数値を、タイトルが言う
  - 成長率・倍率・シェアを、図表から計算し直せない形で書く
  - 比較(前年比)を、比べる相手のないスライドで言う
  - ウォーターフォールの積み上げが、宣言した合計と合わない
  - 出所が「自社調べ」のように、誰も請求できない文字列である
  - 締めのスライドが、そこで初めて出てくる数値で締める
  - 「必ず」「No.1」「可能性があります」で、言い切りを回避する

exit 0 = すべての検査を通過(警告はあり得る) / exit 1 = 論証の欠陥。直すのはスペックであって、
検査ではない。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deck_argument import (  # noqa: E402
    MATERIAL, claim_tokens, claim_values, compute, exhibit_tokens, exhibit_values,
    lexicon, matches, resolve_path, to_number, visible_strings,
)

SYNTHESIS = {"executive_summary", "statement", "two_column", "column_framework",
             "cover", "section_divider", "agenda"}
STRUCTURAL = {"cover", "section_divider", "agenda"}
FORWARD_PATTERNS = {"roadmap", "guidance_progress"}


def _slide_id(i: int, s: dict) -> str:
    return f"slide {i} ({s.get('pattern', '?')})"


def _lex_hits(text: str, cls: dict) -> list[str]:
    hits = []
    for term in cls["terms"]:
        if term.lower() in text.lower():
            if any(neg in text for neg in cls.get("negatives", [])):
                continue
            hits.append(term)
    return hits


def check_language(i, s, errors, warns) -> None:
    """言い切りの強さ。約束・順位・ぼかし・変化語を語彙表で見る(語を足すのは語彙表)。"""
    lex = lexicon()["classes"]
    visible = " ".join(visible_strings(s))
    notes = s.get("speaker_notes", "") or ""
    loc = _slide_id(i, s)

    for hit in _lex_hits(visible + " " + notes, lex["promise"]):
        errors.append(f"{loc}: 約束の言葉「{hit}」— {lex['promise']['fix']}")
    for hit in _lex_hits(visible, lex["hedge"]):
        errors.append(f"{loc}: ぼかした言葉「{hit}」— {lex['hedge']['fix']}")
    for hit in _lex_hits(visible + " " + notes, lex["rank"]):
        q = s.get("qualifier") or {}
        universe = (q.get("universe") or "").strip()
        as_of = (q.get("as_of") or "").strip()
        src = (s.get("source") or "").strip()
        if universe in ("", "業界", "市場", "国内", "世界") or not as_of or not src:
            errors.append(
                f"{loc}: 順位・唯一性の主張「{hit}」— {lex['rank']['fix']}"
                "(qualifier.universe / qualifier.as_of / source を添える)")
    for hit in _lex_hits(visible, lex["motion"]):
        if not claim_tokens(s) and not exhibit_tokens(s):
            warns.append(f"{loc}: 量のない変化語「{hit}」— {lex['motion']['fix']}")
    for hit in _lex_hits(visible, lex["euphemism"]):
        warns.append(f"{loc}: 和らげた言葉「{hit}」— {lex['euphemism']['fix']}")


def check_source(i, s, errors) -> None:
    """出所は、読み手が請求できる文書の名前であること。"""
    lex = lexicon()["classes"]["self_source"]
    src = (s.get("source") or "").strip()
    if not src:
        return
    stripped = src
    for term in lex["terms"]:
        stripped = stripped.replace(term, "")
    stripped = re.sub(r"^Source:\s*", "", stripped, flags=re.I)
    stripped = re.sub(r"[、,・/\s「」（）()]", "", stripped)
    if not stripped:
        errors.append(f"{_slide_id(i, s)}: 出所が請求できない「{src}」— {lex['fix']}")


def check_provenance(i, s, deck, errors, proved_before) -> None:
    """数値を語るスライドは、出所か前提を名乗る。要約スライドは、他のスライドの図表で足りる。"""
    if s.get("pattern") in STRUCTURAL:
        return
    tokens = exhibit_tokens(s) | claim_tokens(s)
    if not tokens:
        return
    if s.get("source") or s.get("assumption"):
        return
    if s.get("pattern") in SYNTHESIS and tokens <= proved_before:
        return                                        # 前のページで証明済みの数値の要約
    if (deck.get("meta") or {}).get("basis"):
        return
    missing = sorted(tokens - proved_before)[:3]
    errors.append(f"{_slide_id(i, s)}: 数値を語るのに出所も前提も無い({', '.join(missing)}) — "
                  "source(外部の文書) か assumption(自分の推計) を書く")


def check_claim_grounded(i, s, errors, warns) -> None:
    """図表が示していない数値は、導出として宣言するか、前のページで証明されていること。"""
    lex = lexicon()["relation_markers"]
    ex, cl = exhibit_tokens(s), claim_tokens(s)
    loc = _slide_id(i, s)
    deriv = s.get("derivation")

    for text in claim_values(s):
        if any(neg in text for neg in lex["negatives"]):
            continue
        for m in MATERIAL.finditer(text):
            token = f"{m.group(1)}{m.group(2)}".replace(",", "")
            kind = _relation_kind(text, m, lex)
            if not kind:
                continue
            # 関係の主張(成長率・倍率・シェア)は、図表から計算し直せなければならない
            if deriv and str(deriv.get("value")) and _declared_matches(s, deriv, token):
                continue
            series = _single_series(s)
            if series is None:
                if token in ex:
                    continue
                warns.append(f"{loc}: 関係の数値「{token}」を示す図表がない — "
                             "図表を置くか、derivation で計算を宣言する")
                continue
            try:
                got = _recompute(kind, series, s)
            except Exception:
                warns.append(f"{loc}: 関係の数値「{token}」を図表から計算できない — "
                             "derivation で計算を宣言する")
                continue
            declared = to_number(m.group(1))
            if declared is None or got is None:
                continue
            if matches(got, declared, m.group(1)):
                continue
            if s.get("source") and s.get("note"):
                warns.append(f"{loc}: 「{token}」は図表の計算値({got:.1f})と違う — "
                             "出所の期間・母集団を note が説明していることを確認する")
                continue
            errors.append(f"{loc}: 「{token}」が図表と合わない(図表から計算すると {got:.1f}) — "
                          "コピーを直すか、derivation を宣言するか、出所の期間・母集団を note に書く")


def _relation_kind(text: str, m, lex) -> str | None:
    window = text[max(0, m.start() - 8):m.end() + 8]
    for kind in ("cagr", "growth", "multiple", "share"):
        if any(mk in window for mk in lex[kind]):
            return kind
    if re.match(r"^[+＋]", m.group(1)) or m.group(1).startswith(("△", "▲")):
        return "growth"
    return None


def _single_series(s: dict) -> list[float] | None:
    """単一系列の図表(比較の相手が一意に決まるもの)。"""
    chart = s.get("chart") or {}
    series = chart.get("series") or []
    if len(series) == 1 and isinstance(series[0], dict):
        vals = [to_number(v) for v in series[0].get("values", [])]
        return [v for v in vals if v is not None] or None
    cur = s.get("current") or {}
    if cur.get("actual") is not None and cur.get("guidance_low") is not None:
        low, high = to_number(cur["guidance_low"]), to_number(cur.get("guidance_high", cur["guidance_low"]))
        return [to_number(cur["actual"]), (low + high) / 2]
    return None


def _recompute(kind: str, series: list[float], s: dict) -> float | None:
    if len(series) < 2:
        return None
    a, b = series[0], series[-1]
    if kind == "cagr":
        n = len(series) - 1
        return ((b / a) ** (1 / n) - 1) * 100 if a > 0 else None
    if kind == "growth":
        a2, b2 = series[-2], series[-1]
        return (b2 / a2 - 1) * 100 if a2 else None
    if kind == "multiple":
        return b / a if a else None
    if kind == "share":
        return series[0] / series[1] * 100 if series[1] else None
    return None


def _declared_matches(s, deriv, token) -> bool:
    try:
        got = compute(s, deriv)
    except Exception:
        return False
    return matches(got, to_number(deriv["value"]), str(deriv["value"]))


def check_derivation(i, s, errors) -> None:
    """宣言された導出は、計算し直して一致すること(宣言は計算で贖われる)。"""
    deriv = s.get("derivation")
    if not deriv:
        return
    loc = _slide_id(i, s)
    try:
        got = compute(s, deriv)
    except Exception as exc:
        errors.append(f"{loc}: derivation が計算できない({exc})")
        return
    declared = to_number(deriv.get("value"))
    if declared is None:
        errors.append(f"{loc}: derivation に value がない")
        return
    if not matches(got, declared, str(deriv.get("value"))):
        errors.append(f"{loc}: derivation が合わない(宣言 {declared} / 計算 {got:.2f})")


def check_comparison_base(i, s, errors) -> None:
    """比較の主張には、比べる相手が同じページにあること。"""
    lex = lexicon()["relation_markers"]
    chart = s.get("chart") or {}
    table = s.get("table") or {}
    if not chart and not table:
        return
    text = " ".join(claim_values(s))
    if any(neg in text for neg in lex["negatives"]):
        return
    markers = lex["growth"] + lex["cagr"]
    if not any(mk in text for mk in markers) or not MATERIAL.search(text):
        return
    points = 0
    for ser in chart.get("series", []) or []:
        points = max(points, len(ser.get("values", [])))
    if table:
        points = max(points, len(table.get("headers", [])) - 1)
    if points < 2:
        errors.append(f"{_slide_id(i, s)}: 比較の主張に、比べる相手がない — "
                      "前期・前年のデータを同じページに置く")


def check_identity(i, s, errors) -> None:
    """図表がそれ自身と合っていること(積み上げ・入れ子)。"""
    loc = _slide_id(i, s)
    if s.get("pattern") == "waterfall":
        items = s.get("items") or []
        start = next((to_number(it.get("value")) for it in items if it.get("kind") == "start"), None)
        end = next((to_number(it.get("value")) for it in items if it.get("kind") == "end"), None)
        deltas = [to_number(it.get("value")) for it in items
                  if it.get("kind") not in ("start", "end") and it.get("value") is not None]
        if start is not None and end is not None and all(d is not None for d in deltas):
            total = start + sum(deltas)
            if abs(total - end) > max(0.05, abs(end) * 0.005):
                errors.append(f"{loc}: 積み上げが合わない(起点 {start} + 増減 {sum(deltas)} = "
                              f"{total} ≠ 終点 {end})")
    if s.get("pattern") == "market_sizing":
        nums = [to_number(st.get("numeric", st.get("value"))) for st in s.get("stages") or []]
        nums = [n for n in nums if n is not None]
        if len(nums) >= 2 and any(a < b for a, b in zip(nums, nums[1:])):
            errors.append(f"{loc}: 入れ子が逆(TAM ≥ SAM ≥ SOM の順に小さくなること): {nums}")
    if s.get("pattern") == "metric_proof":
        _check_hero_in_chart(loc, s, errors)


def _chart_numbers(chart: dict, unit: str = "") -> list[float]:
    """図表データの数値 — 配列の中の数(native の series.values、画像図表 combo の bar/line の values、
    area の series …)。focal_category や y_max のような単独のスカラーは制御値であって数えない。
    categories / labels / headers の配列は軸ラベルなので数えない。unit を渡すと、その単位の配列だけを
    返す: 配列の単位は最も近い上位の dict の unit(combo の bar.unit / line.unit、native の chart.unit)。
    二軸の combo で % の折れ線の 12.8 を 12.8億円 の証拠にしない(Codex / Claude レビュー指摘、PR #158)。"""
    out: list[float] = []

    def walk(node, in_list: bool, scope: str) -> None:
        if isinstance(node, dict):
            scope = str(node.get("unit") or scope)
            for k, v in node.items():
                if k not in ("categories", "labels", "headers"):
                    walk(v, False, scope)
        elif isinstance(node, list):
            for v in node:
                walk(v, True, scope)
        elif in_list and not isinstance(node, bool) and (not unit or not scope or scope == unit):
            n = to_number(node)
            if n is not None:
                out.append(n)
    walk(chart, False, "")
    return out


def _chart_units(chart: dict) -> set[str]:
    units: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            if node.get("unit"):
                units.add(str(node["unit"]))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(chart)
    return units


def _same(v: float, val: float, printed: str) -> bool:
    """書かれた桁で一致し、符号も同じ(-12.8 は 12.8 の証拠ではない)。"""
    return (v >= 0) == (val >= 0) and matches(v, val, printed)


def _derivation_grounded(deriv: dict, nums: list[float]) -> bool:
    """derivation の被演算子が図表の値(hero と同じ単位の配列)から取られているか。数はどれかの図表の値と
    一致、文字列は chart への参照パスであること。value / unit / kind は結果の宣言であって被演算子ではない。"""
    def ok(node) -> bool:
        if isinstance(node, bool):
            return False
        if isinstance(node, (int, float)):
            return any(_same(n, float(node), str(node)) for n in nums)
        if isinstance(node, str):
            return node.startswith("chart")
        if isinstance(node, dict):
            return all(ok(v) for v in node.values())
        if isinstance(node, list):
            return all(ok(v) for v in node)
        return False
    # from / to / years / n は位置や期間の指定であって図表の値ではない(Codex レビュー指摘)
    operands = {k: v for k, v in deriv.items()
                if k not in ("value", "unit", "kind", "label", "years", "from", "to", "n", "index", "at")}
    return bool(operands) and ok(operands)


def _check_hero_in_chart(loc: str, s: dict, errors) -> None:
    """metric_proof の hero は、隣の chart が証明する数。hero は exhibit 側に数えるので、それ自身で
    結論トークンを満たしてしまう — hero の値が (a) 図表データの値、(b) 積み上げ型の最終カテゴリの合計、
    (c) 図表の値から導いた同じ単位の derivation の値、のどれかと符号ごと一致することを求める
    (Codex レビュー指摘、PR #158)。画像図表(combo / area など)も数値配列を持つので同じく照合する。
    単位が違う図表や、照合できる数値の無い図表は、hero を証明していないので error。"""
    hero, chart = s.get("hero") or {}, s.get("chart") or {}
    val = to_number(hero.get("value"))
    if val is None or not chart:
        return
    printed = str(hero.get("value"))
    h_unit = str(hero.get("unit") or "")
    # 図表の値から導いた同じ単位の derivation は、単位が図表と違っても(億円の系列から CAGR の %)証明になる
    deriv = s.get("derivation") or {}
    d_val = to_number(deriv.get("value")) if deriv else None
    if d_val is not None and str(deriv.get("unit") or "") == h_unit \
            and _derivation_grounded(deriv, _chart_numbers(chart)) and _same(d_val, val, printed):
        return
    c_units = _chart_units(chart)
    if h_unit and c_units and h_unit not in c_units:
        errors.append(f"{loc}: hero の単位「{h_unit}」が chart の単位({' / '.join(sorted(c_units))})と違う — "
                      "hero を証明する図表は同じ単位で描くか、図表の値から導く derivation を宣言する")
        return
    nums = _chart_numbers(chart, h_unit)
    if not nums:
        errors.append(f"{loc}: hero の値 {printed}{h_unit} を照合できる図表データが chart に無い — "
                      "同じ単位の系列の値を持つ図表で hero を証明する")
        return
    shown = list(nums)
    ctype, kind = chart.get("type", "column"), chart.get("kind")
    series = chart.get("series") or []
    if (ctype in ("stacked_column", "stacked_bar", "stacked_column_100") and not kind) or kind == "area":
        last = [to_number((ser.get("values") or [None])[-1]) for ser in series if isinstance(ser, dict)]
        if last and all(v is not None for v in last):
            shown.append(sum(last))                         # 積み上げの最終カテゴリの合計
    if not any(_same(v, val, printed) for v in shown):
        errors.append(f"{loc}: hero の値 {printed}{h_unit} が chart に無い — "
                      "系列の値か、図表の値から導いた同じ単位の derivation で hero を図表から導く"
                      "(hero が自分を証明してはいけない)")


def check_recap(deck, errors) -> None:
    """締めのスライドは、そこで初めて出る数値で締めない。"""
    slides = deck.get("slides", [])
    if not slides:
        return
    last_i = len(slides)
    last = slides[-1]
    if last.get("pattern") not in ("statement", "closing", "kpi_dashboard"):
        return
    proved: set[str] = set()
    for s in slides[:-1]:
        proved |= exhibit_tokens(s)
    new = sorted(claim_tokens(last) | exhibit_tokens(last))
    unproved = [t for t in new if t not in proved]
    if unproved:
        errors.append(f"slide {last_i} (締め): 前のページで示していない数値で締めている"
                      f"({', '.join(unproved[:3])}) — 締めは新しい主張を出さない")


def check_thesis(deck, errors) -> None:
    """デッキは一つの結論を名乗り、その数値はどこかの図表で示されていること。"""
    meta = deck.get("meta") or {}
    thesis = meta.get("thesis")
    if not isinstance(thesis, dict) or not thesis.get("statement"):
        errors.append("meta.thesis がない — デッキが証明する結論(と、その数値)を宣言する")
        return
    value, unit = thesis.get("value"), thesis.get("unit")
    if not value or not unit:
        errors.append("meta.thesis に value と unit がない — 結論は数値で言い切る")
        return
    token = f"{value}{unit}".replace(",", "")
    # 結論の数値は、図表の数値トークン(数値+単位)か、図表の文字列そのもの(「街づくりの7段階」の
    # ような構造の数、単位表に無い単位)のどちらかで示されていればよい。構造の数を単位表に足すと、
    # 「3段階の打ち手」のような語りの数まで出所を要求してしまう(レビュー指摘、2026-09-04)
    # 文字列で探すときは数値を丸ごと一致させる — 「7段階」を「17段階」「27段階」で満たさない
    # (Codex レビュー指摘、PR #158)
    # 符号も一致させる — 「7段階」を「-7段階」「△7段階」で満たさない(Codex レビュー指摘、PR #158)
    whole = re.compile(r"(?<![\d.,\-−△▲+±])" + re.escape(token) + r"(?!\d)")

    def _shown(s: dict) -> bool:
        if token in exhibit_tokens(s):
            return True
        return any(whole.search(str(v).replace(",", "")) for v in exhibit_values(s) if isinstance(v, str))
    if not any(_shown(s) for s in deck.get("slides", [])):
        errors.append(f"meta.thesis の数値「{token}」を示す図表がどのページにも無い")


def check_forward_drivers(i, s, warns) -> None:
    """未来を語るページは、その前提を数値で名乗る。"""
    chart = s.get("chart") or {}
    forward = s.get("pattern") in FORWARD_PATTERNS or chart.get("forecast_from") is not None
    if not forward:
        return
    assumption = s.get("assumption") or ""
    if not MATERIAL.search(assumption):
        warns.append(f"{_slide_id(i, s)}: 見通しのページに、数値の前提がない — "
                     "assumption に前提の数値(成長率・単価・解約率など)を書く")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    deck = json.loads(Path(sys.argv[1]).read_text())
    slides = deck.get("slides", [])
    errors: list[str] = []
    warns: list[str] = []

    lexicon()                                     # 語彙表が壊れていたら、ここで止まる
    check_thesis(deck, errors)
    check_recap(deck, errors)

    proved: set[str] = set()
    for i, s in enumerate(slides, start=1):
        check_language(i, s, errors, warns)
        check_source(i, s, errors)
        check_provenance(i, s, deck, errors, proved)
        check_derivation(i, s, errors)
        check_claim_grounded(i, s, errors, warns)
        check_comparison_base(i, s, errors)
        check_identity(i, s, errors)
        check_forward_drivers(i, s, warns)
        proved |= exhibit_tokens(s)

    for w in warns:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(slides)} slides / {len(errors)} errors / {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
