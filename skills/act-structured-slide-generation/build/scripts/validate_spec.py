#!/usr/bin/env python3
"""Validate a deck.json spec BEFORE building: structure, text budgets, color policy,
writing discipline (AI-tells), and story-level uniformity.

Usage: validate_spec.py <deck.json> [--outline]
--outline prints the action-title sequence only (ghost-deck test: the titles alone
must read as one continuous argument) and exits 0.
Exit 0 = OK (warnings allowed), exit 1 = errors that must be fixed in the spec.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from deck_text import ja_len

TOKENS = json.loads((Path(__file__).resolve().parent.parent / "references" / "tokens.json").read_text())
BUDGET = TOKENS["text_budget"]
ALLOWED_COLORS = set(TOKENS["colors"].values())
FORBIDDEN = set(TOKENS["color_policy"]["forbidden_colors"])
ACCENT = TOKENS["colors"]["accent"]

PATTERNS = {
    "cover": [],
    "agenda": ["items"],
    "section_divider": ["title"],
    "executive_summary": ["title", "points"],
    "kpi_dashboard": ["title", "kpis"],
    "chart_insight": ["title", "chart"],
    "market_sizing": ["title", "stages"],
    "comparison_table": ["title", "table"],
    "competitive_landscape": ["title", "players"],
    "financial_summary": ["title"],
    "waterfall": ["title", "items"],
    "roadmap": ["title", "phases"],
    "two_column": ["title", "left", "right"],
    "process_flow": ["title", "steps"],
    "statement": ["statement"],
    "financial_highlights": ["title", "groups"],
    "metrics_rows": ["title", "columns"],
    "driver_decomposition": ["title", "factors"],
    "guidance_progress": ["title", "bars", "current"],
}
EVIDENCE_PATTERNS = {
    "chart_insight", "market_sizing", "comparison_table", "competitive_landscape",
    "financial_summary", "waterfall", "kpi_dashboard",
    "financial_highlights", "metrics_rows", "driver_decomposition", "guidance_progress",
}


BANNED_PHRASES = [
    "と言えるでしょう", "と考えられます", "が期待されます", "一概には言えませんが",
    "することが重要です", "まとめると", "いかがでしたか",
    "delve", "leverage", "seamless", "game-changer", "it's important to note",
]
META_DECLARATIONS = ["以下の3点", "本資料では", "について説明します", "ご紹介します"]


def iter_texts(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_texts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_texts(v)


def iter_colors(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "color" and isinstance(v, str):
                yield v.upper().lstrip("#")
            else:
                yield from iter_colors(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_colors(v)


STRUCTURAL = ("cover", "section_divider", "statement", "agenda")


def print_outline(slides: list) -> None:
    """Ghost-deck readout: titles in sequence. Read top to bottom — if this is not
    one continuous argument, fix the outline before touching slide bodies."""
    for i, s in enumerate(slides, start=1):
        pat = s.get("pattern", "?")
        title = s.get("title") or s.get("statement") or ""
        marker = "  " if pat in STRUCTURAL else "● "
        print(f"{i:2d} {marker}[{pat}] {title}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--outline"]
    outline_mode = "--outline" in sys.argv[1:]
    if len(args) != 1:
        print(__doc__)
        return 1
    try:
        deck = json.loads(Path(args[0]).read_text())
    except Exception as e:
        print(f"ERROR: cannot parse JSON: {e}")
        return 1

    errors: list[str] = []
    warns: list[str] = []
    slides = deck.get("slides")
    if not isinstance(slides, list) or not slides:
        print("ERROR: deck.slides must be a non-empty array")
        return 1
    if outline_mode:
        print_outline(slides)
        return 0

    for i, s in enumerate(slides, start=1):
        loc = f"slide {i}"
        pat = s.get("pattern")
        if pat not in PATTERNS:
            errors.append(f"{loc}: unknown pattern '{pat}' (valid: {', '.join(sorted(PATTERNS))})")
            continue
        loc = f"slide {i} ({pat})"
        for req in PATTERNS[pat]:
            if not s.get(req):
                errors.append(f"{loc}: missing required field '{req}'")

        title = s.get("title", "")
        if title and ja_len(title) > BUDGET["action_title_two_line_max_chars_ja"]:
            errors.append(f"{loc}: title too long ({ja_len(title):.0f} > {BUDGET['action_title_two_line_max_chars_ja']} 全角相当) — shorten or split the message")
        if s.get("subtitle") and ja_len(s["subtitle"]) > BUDGET["subtitle_max_chars_ja"]:
            errors.append(f"{loc}: subtitle too long — shorten")
        if s.get("insight") and ja_len(s["insight"]) > BUDGET["insight_max_chars_ja"]:
            errors.append(f"{loc}: insight too long ({ja_len(s['insight']):.0f} > {BUDGET['insight_max_chars_ja']}) — one short judgment sentence only")

        if pat not in STRUCTURAL and title:
            # action title should be a sentence (predicate), not a topic label
            if ja_len(title) < 12:
                warns.append(f"{loc}: title '{title}' looks like a topic label — use a full action-title sentence (actor + change + implication)")
            if "。" in title.rstrip("。"):
                warns.append(f"{loc}: タイトルに文が2つ — 1スライド1メッセージ。分割するか一文に絞る")
            # competitive_landscape はポジショニングの定性主張が正当なため数字必須から除外
            if pat in EVIDENCE_PATTERNS and pat != "competitive_landscape" and not any(ch.isdigit() for ch in title):
                warns.append(f"{loc}: エビデンススライドのタイトルに数字がない — 図表が証明する結論の数値を1つ入れる")

        import re as _re
        zenkaku = [t for t in iter_texts({k: v for k, v in s.items() if k != "pattern"})
                   if _re.search(r"[０-９Ａ-Ｚａ-ｚ％\uFF0D]", t)]
        if zenkaku:
            warns.append(f"{loc}: 全角英数字が含まれる — 英数字は半角に統一: '{zenkaku[0][:24]}'")

        if pat in EVIDENCE_PATTERNS and not (s.get("source") or s.get("assumption")):
            warns.append(f"{loc}: evidence slide without 'source' — add a real source, or 'assumption' for internal estimates")
        for key in ("source", "assumption"):
            v = (s.get(key) or "").lower()
            if any(b in v for b in ("lorem", "xxx", "tbd", "dummy", "placeholder")):
                errors.append(f"{loc}: {key} contains placeholder text")

        colors = list(iter_colors(s))
        for cval in colors:
            if cval in FORBIDDEN:
                errors.append(f"{loc}: forbidden color #{cval}")
            elif cval not in ALLOWED_COLORS:
                errors.append(f"{loc}: color #{cval} is outside the Act palette (see references/tokens.json)")
        # insight_style "primary" は淡緑バンドで描画され Accent を使わない(build_deck の描画と対応)
        insight_uses_accent = bool(s.get("insight")) and s.get("insight_style", "accent") == "accent"
        accent_uses = colors.count(ACCENT) + (1 if insight_uses_accent else 0)
        if accent_uses > TOKENS["color_policy"]["accent_max_uses_per_slide"]:
            errors.append(f"{loc}: Accent #{ACCENT} used {accent_uses}x — max 1 per slide (insight bar counts as the one use)")

        chart = s.get("chart")
        if chart:
            cats, series = chart.get("categories", []), chart.get("series", [])
            if not cats or not series:
                errors.append(f"{loc}: chart needs categories and series")
            values_numeric = True
            for ser in series:
                if len(ser.get("values", [])) != len(cats):
                    errors.append(f"{loc}: series '{ser.get('name')}' has {len(ser.get('values', []))} values for {len(cats)} categories")
                bad = [v for v in ser.get("values", []) if isinstance(v, bool) or not isinstance(v, (int, float))]
                if bad:
                    values_numeric = False
                    errors.append(f"{loc}: series '{ser.get('name')}' の values に数値でない要素: {bad[0]!r}")
            if len(series) > 4:
                errors.append(f"{loc}: {len(series)} series — max 4; aggregate or split the chart")
            ff = chart.get("forecast_from")
            if ff is not None:
                try:
                    ff = int(ff)
                except (TypeError, ValueError):
                    errors.append(f"{loc}: forecast_from は整数 index で指定する(現在: {ff!r})")
                    ff = None
            if ff is not None:
                if len(series) > 1 or chart.get("type", "column") not in ("column", "bar"):
                    warns.append(f"{loc}: forecast_from は単一系列の column/bar のみ有効 — line・複数系列では描き分けされない。categories の E 表記+注記で区別するか column に変える")
                else:
                    def _marked(c):
                        cs = str(c)
                        return cs.endswith("E") or any(m in cs for m in ("予", "計画", "見込", "見通し", "目標"))
                    unmarked = [str(c) for c in cats[ff:] if not _marked(c)]
                    if unmarked:
                        warns.append(f"{loc}: forecast_from 以降のカテゴリに予想表記(E/計画/予想)がない: {', '.join(unmarked[:3])}")
            if not chart.get("unit"):
                warns.append(f"{loc}: chart has no 'unit' — add one (e.g. 億円, %) unless truly unitless")
            if values_numeric and chart.get("type", "column") in ("column", "bar", "stacked_column") and any(
                    float(v) < 0 for ser in series for v in ser.get("values", [])):
                warns.append(f"{loc}: negative values in a {chart.get('type', 'column')} chart — LibreOffice render-QA draws them wrong (PowerPoint is fine); prefer 'line', the waterfall pattern, or keep negatives in a table")

        if pat == "waterfall":
            kinds = [it.get("kind", "delta") for it in s.get("items", [])]
            if kinds and (kinds[0] != "start" or kinds[-1] != "end"):
                errors.append(f"{loc}: waterfall items must begin with kind='start' and finish with kind='end'")

        for k in s.get("kpis", []):
            if ja_len(k.get("label", "")) > BUDGET["kpi_label_max_chars_ja"]:
                errors.append(f"{loc}: kpi label '{k.get('label')}' too long")
        if pat == "kpi_dashboard" and len(s.get("kpis", [])) > 8:
            errors.append(f"{loc}: {len(s['kpis'])} KPIs — max 8")
        if pat == "agenda" and len(s.get("items", [])) > 6:
            errors.append(f"{loc}: {len(s['items'])} agenda items — max 6")
        if pat == "executive_summary" and len(s.get("points", [])) > 4:
            errors.append(f"{loc}: {len(s['points'])} points — max 4 for readability")
        if pat == "process_flow" and len(s.get("steps", [])) > 5:
            errors.append(f"{loc}: {len(s['steps'])} steps — max 5")
        if pat == "roadmap" and len(s.get("phases", [])) > 4:
            errors.append(f"{loc}: {len(s['phases'])} phases — max 4")
        if len(s.get("takeaways", [])) > 3:
            errors.append(f"{loc}: {len(s['takeaways'])} takeaways — max 3")
        if pat == "financial_summary" and not (s.get("table") or s.get("chart")):
            errors.append(f"{loc}: financial_summary には table か chart の少なくとも一方が必要")
        if pat == "competitive_landscape":
            for pl in s.get("players", []):
                pname = pl.get("name", "?")
                for ax in ("x", "y"):
                    v = pl.get(ax)
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        errors.append(f"{loc}: player '{pname}' の {ax} がない/数値でない(0-1 で指定)")
                    elif not 0.0 <= float(v) <= 1.0:
                        errors.append(f"{loc}: player '{pname}' の {ax}={v} が 0-1 の範囲外")

        texts = list(iter_texts({k: v for k, v in s.items() if k != "pattern"}))
        joined = " ".join(texts)
        for b in BANNED_PHRASES:
            if b.lower() in joined.lower():
                warns.append(f"{loc}: AI常套句「{b}」— 具体的な言い回しに書き直す(references/humanize.md)")
        for b in META_DECLARATIONS:
            if b in joined:
                warns.append(f"{loc}: メタ宣言「{b}」— 内容で構造を示し、宣言は削除する")
        nado = sum(t.count("など") + t.count("等") for t in texts)
        if nado > 2:
            warns.append(f"{loc}: 「など/等」が{nado}回 — 名前を列挙するか削る(1スライド1回まで)")

    # emphasis-device rationing: insight / kicker lose force when they appear everywhere
    n_insight = sum(1 for s in slides if s.get("insight"))
    if n_insight > 4:
        warns.append(f"insight バーが{n_insight}枚 — 非自明な判断がある 2-4 枚に絞る(全部に置くと強調が消える)")
    n_kicker = sum(1 for s in slides if s.get("kicker"))
    if n_kicker > 3:
        warns.append(f"kicker が{n_kicker}枚 — 修辞疑問はデッキ内 2-3 枚まで")

    # adjacent-slide monotony: same content pattern back to back reads as a template loop
    prev_pat = None
    for i, s in enumerate(slides, start=1):
        pat = s.get("pattern")
        if pat and pat == prev_pat and pat not in STRUCTURAL:
            warns.append(f"slide {i}: 直前のスライドと同じパターン '{pat}' が連続 — 内容が同型でないなら構成を散らす")
        prev_pat = pat

    # structural uniformity (the strongest AI tell): too many exactly-3-item slides
    counts = []
    for s in slides:
        for key in ("points", "takeaways", "kpis", "items", "steps", "notes", "factors", "groups"):
            if isinstance(s.get(key), list) and s.get("pattern") not in ("agenda", "waterfall"):
                counts.append(len(s[key]))
    if counts and len([c for c in counts if c == 3]) / len(counts) > 0.6:
        warns.append(f"リスト項目が3個のスライドが{len([c for c in counts if c == 3])}/{len(counts)} — 「常に3項目」は AI 的な均一性。内容に応じて 2 や 4 に散らす")

    # chapter numbering must match the agenda position of the same-labeled item
    agenda = next((s for s in slides if s.get("pattern") == "agenda"), None)
    if agenda:
        labels = [(it if isinstance(it, str) else it.get("label", "")) for it in agenda.get("items", [])]
        for s in slides:
            if s.get("pattern") == "section_divider" and s.get("number") and s.get("title") in labels:
                expect = labels.index(s["title"]) + 1
                try:
                    num = int(s["number"])
                except (TypeError, ValueError):
                    errors.append(f"section_divider「{s['title']}」の number={s['number']!r} が数値でない")
                    continue
                if num != expect:
                    errors.append(f"section_divider「{s['title']}」の number={s['number']} がアジェンダ上の位置 {expect:02d} と矛盾 — 揃える")

    # minus-sign notation: use △ (not -) in display strings
    for i, s in enumerate(slides, start=1):
        for t in iter_texts({k: v for k, v in s.items() if k not in ("pattern", "chart", "bars", "current")}):
            import re as _re
            if _re.search(r"[  ((]-\d", t) or t.startswith("-"):
                warns.append(f"slide {i}: 表示文字列にマイナス記号「-」— IR 慣行の「△」に統一する: '{t[:30]}'")
                break

    titled = [s.get("title", "") for s in slides if s.get("pattern") not in ("cover", "section_divider", "statement", "agenda")]
    if len(titled) != len(set(titled)):
        warns.append("duplicate action titles across slides — each slide should carry one distinct message")

    # header uniformity: 行数が混在すると本文開始位置とバー高がスライド毎に揺れる
    # (サイズは常に一定 — 行数で縮小しない)。1行に揃えるのが最も確実
    one_line_max = BUDGET["action_title_max_chars_ja"]
    two_liners = [(i, ja_len(s.get("title", ""))) for i, s in enumerate(slides, start=1)
                  if s.get("pattern") not in ("cover", "section_divider")
                  and s.get("title") and ja_len(s["title"]) > one_line_max]
    n_chrome = sum(1 for s in slides if s.get("pattern") not in ("cover", "section_divider") and s.get("title"))
    if two_liners and len(two_liners) < n_chrome:
        detail = ", ".join(f"slide {i}({n:.0f}字)" for i, n in two_liners)
        warns.append(f"タイトル1行と2行が混在 — 本文開始位置とバー高がスライド毎に揺れる。{detail} を{one_line_max}字以内に短縮して全スライド1行に揃える")

    # kicker length budget (short label, not a sentence)
    for i, s in enumerate(slides, start=1):
        if s.get("kicker") and ja_len(s["kicker"]) > BUDGET["kicker_max_chars_ja"]:
            warns.append(f"slide {i}: kicker が{ja_len(s['kicker']):.0f}字 — {BUDGET['kicker_max_chars_ja']}字以内の短いラベルにする(文にしない)")

    # process_flow density: ≤3 bullets per step card (4カード×3行で既に12行 —
    # それ以上は「概要+ステップ別詳細スライド」に分割する)
    for i, s in enumerate(slides, start=1):
        if s.get("pattern") == "process_flow":
            fat = [st.get("label", f"step{j+1}") for j, st in enumerate(s.get("steps", []))
                   if len(st.get("items", [])) > 3]
            if fat:
                warns.append(f"slide {i}: ステップの項目が3個超({', '.join(fat)}) — カードあたり3項目以内。超える分は詳細スライドか speaker_notes へ")

    # subtitle uniformity: content slides follow all-or-none (有無が混ざると
    # アクセントバー高と本文開始位置がスライド毎に変わる)
    content = [(i, s) for i, s in enumerate(slides, start=1) if s.get("pattern") not in STRUCTURAL]
    no_sub = [i for i, s in content if not s.get("subtitle")]
    if no_sub and len(no_sub) < len(content):
        warns.append(f"サブタイトルの有無が混在(無し: slide {', '.join(map(str, no_sub))}) — ヘッダー高が揺れる。全コンテンツスライドに付けるか全て外す")

    for w in warns:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(slides)} slides / {len(errors)} errors / {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
