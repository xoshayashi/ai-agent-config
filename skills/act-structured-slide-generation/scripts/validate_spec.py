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

from deck_text import header_slots, ja_len

TOKENS = json.loads((Path(__file__).resolve().parent.parent / "references" / "tokens.json").read_text())
BUDGET = TOKENS["text_budget"]
ALLOWED_COLORS = set(TOKENS["colors"].values())
FORBIDDEN = set(TOKENS["color_policy"]["forbidden_colors"])
ACCENT = TOKENS["colors"]["accent"]
# build_deck.py の CHART_TYPES と同期(テスト test_chart_type_lists_stay_in_sync が担保)
SUPPORTED_CHART_TYPES = ("column", "stacked_column", "bar", "line", "donut")

# 各パターンの必須「データ」フィールド(本文の中身)。見出し(title / subtitle / desc)は
# ここに書かない — 有無も行数も _check_header_contract がヘッダー契約から一元的に見る
# (両方で見ると同じ欠落に二重のエラーが出る)
PATTERNS = {
    "cover": [],
    "agenda": ["items"],
    "section_divider": [],
    "executive_summary": ["points"],
    "kpi_dashboard": ["kpis"],
    "chart_insight": ["chart"],
    "market_sizing": ["stages"],
    "comparison_table": ["table"],
    "competitive_landscape": ["players"],
    "financial_summary": [],
    "waterfall": ["items"],
    "roadmap": ["phases"],
    "two_column": ["left", "right"],
    "process_flow": ["steps"],
    "statement": ["statement"],
    "financial_highlights": ["groups"],
    "metrics_rows": ["columns"],
    "driver_decomposition": ["factors"],
    "guidance_progress": ["current"],
    "diagram": ["diagram"],
    "chart_grid": ["charts"],
}
EVIDENCE_PATTERNS = {
    "chart_insight", "market_sizing", "comparison_table", "competitive_landscape",
    "financial_summary", "waterfall", "kpi_dashboard",
    "financial_highlights", "metrics_rows", "driver_decomposition", "guidance_progress",
    "diagram", "chart_grid",
}
# chart/diagram objects rendered via the image-asset backend (act_assets), not native charts.
# 必須フィールドは act_assets の各レンダラーが spec[...] で直接参照するキー —
# ここで検査しないと validate は 0 errors で通り、build が KeyError/ValueError で落ちる
IMAGE_KIND_REQUIRED = {
    "combo": ("categories", "bar", "line"),
    "area": ("categories", "series"),
    "line_multi": ("categories", "series"),
    "scatter": ("points",),
    "bubble": ("points",),
    "waterfall": ("items",),
    "radar": ("axes", "series"),
    "ring": ("segments",),
    "funnel": ("stages",),
    "pyramid": ("tiers",),
    "venn": ("sets",),
    "matrix": ("rows", "cols"),
    "org_tree": ("nodes", "edges"),
    "node_graph": ("nodes", "edges"),
}
IMAGE_ASSET_KINDS = {
    "combo", "area", "radar", "scatter", "bubble", "waterfall", "line_multi",
    "org_tree", "node_graph", "ring", "funnel", "pyramid", "venn", "matrix",
}

# 日本語プレゼンの標準話速(NHKアナウンス基準の目安)。トークスクリプト総量の照合に使う
TALK_CHARS_PER_MIN = 300


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


def _check_header_contract(errors: list, loc: str, pattern: str, slide: dict) -> None:
    """ヘッダー契約(tokens.json の header_contract)をパターン非依存に検査する。

    契約はデータで宣言され、ここはそれを機械的に適用するだけ — パターンごとの分岐や
    字数のマジックナンバーは持たない。規則は3つだけ:
      1. 契約の全スロット(タイトル・副題)が埋まっていること
      2. 各スロットは lines で宣言された行数ちょうどであること(既定1行)
      3. どの行も描画幅から導出した1行容量に収まること(折返し禁止 — 縮小もしない)
    描画されないフィールドを書いた場合(章扉の subtitle 等)は、黙って捨てられるより
    誤りとして返すほうが安全なので弾く。
    """
    slots = header_slots(pattern)
    for cfg in slots:
        field, text = cfg["field"], slide.get(cfg["field"], "") or ""
        want = cfg["lines"]
        if not text.strip():
            errors.append(f"{loc}: {field} がない — 全スライドにメインタイトルと副題を必ず付ける"
                          f"({pattern} の副題フィールドは "
                          f"'{next(c['field'] for c in slots if c['slot'] == 'subtitle')}')")
            continue
        lines = text.split("\n")
        if len([l for l in lines if l.strip()]) != want or len(lines) != want:
            got = len([l for l in lines if l.strip()])
            detail = ("改行禁止" if want == 1 else f'"\\n" 区切りでちょうど{want}行')
            errors.append(f"{loc}: {field} は{want}行ちょうどで書く({detail}) — 現在 {got} 行")
        for i, line in enumerate(lines, start=1):
            if ja_len(line) > cfg["max_chars"]:
                where = f"{i}行目" if want > 1 else field
                errors.append(
                    f"{loc}: {where} が1行に収まらない "
                    f"({ja_len(line):.0f} > {cfg['max_chars']:.0f} 全角相当、{cfg['size_pt']}pt × "
                    f"{cfg['width_in']:.1f}in) — 字を小さくせずコピーを短く研ぐ")

    # 契約に無い見出しフィールドを書いても描画されない(黙って消えるのを防ぐ)
    declared = {c["field"] for c in slots}
    for ghost in ({"title", "subtitle", "desc"} - declared) & set(slide):
        if slide.get(ghost):
            owner = next(c["field"] for c in slots if c["slot"] == "subtitle")
            errors.append(f"{loc}: {pattern} は '{ghost}' を描画しない — 副題は '{owner}' に書く")


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

        _check_header_contract(errors, loc, pat, s)
        title = s.get("title", "")
        if s.get("insight") and ja_len(s["insight"]) > BUDGET["insight_max_chars_ja"]:
            errors.append(f"{loc}: insight too long ({ja_len(s['insight']):.0f} > {BUDGET['insight_max_chars_ja']}) — one short judgment sentence only")

        # フッター(source / assumption / note)は帯の高さぶん = 2行までしか描かれない。
        # 超えた分は下端の外周パディングへはみ出し、レンダーで見切れる — 帯を広げるのでは
        # なく、出典・前提・注記を短く書くのが正しい直し方
        foot_txt = "".join(
            f"{label}: {s[key]}   " for key, label in
            (("source", "Source"), ("assumption", "Assumption"), ("note", "Note"))
            if s.get(key))
        if ja_len(foot_txt) > BUDGET["footnote_max_chars_ja"]:
            errors.append(f"{loc}: フッターが長い ({ja_len(foot_txt):.0f} > "
                          f"{BUDGET['footnote_max_chars_ja']} 全角相当) — source / assumption / note は"
                          "合わせて2行以内。出典名を短くするか、注記を本文へ移す")
        if pat == "statement" and s.get("statement"):
            # 孤立行対策の節分割は中央ヒーロー文(既定)のみ。recap 駆動の strip/split 変種は
            # 左寄せの別レイアウトのため、この警告は中央ヒーロー描画に限定する。
            _variant = s.get("variant", s.get("layout", "center_hero"))
            _center_hero = not (s.get("recap") and _variant in (
                "evidence_strip", "thesis_strip", "closing_grid", "split_evidence", "editorial_split"))
            # 節長は「、」を除いた実測。build_deck のパッカーは「、」を再結合してから測る
            # ため約1字ずれるが、22字閾値のマージン内なので意図的に同一視しない
            _clauses = [c for c in s["statement"].split("、") if c]
            _longest = max((ja_len(c) for c in _clauses), default=ja_len(s["statement"]))
            if _center_hero and _longest > 22:
                if "、" in s["statement"]:
                    warns.append(f"{loc}: 締めのステートメントの節が長い(最長 {_longest:.0f}字) — 中央ヒーロー文は節ごとに折返すため、各節を22字以内・全体を60字前後に短縮すると尾行の孤立が消える")
                else:
                    warns.append(f"{loc}: 締めのステートメントが読点のない一文({_longest:.0f}字) — 節折返しが効かず語中で改行される。「、」で節に区切るか60字前後に短縮する")

        if pat not in STRUCTURAL and title:
            # action title should be a sentence (predicate), not a topic label
            if ja_len(title) < 12:
                warns.append(f"{loc}: title '{title}' looks like a topic label — use a full action-title sentence (actor + change + implication)")
            if "。" in title.rstrip("。"):
                warns.append(f"{loc}: タイトルに文が2つ — 1スライド1メッセージ。分割するか一文に絞る")
            # competitive_landscape / diagram は関係・構造の定性主張が正当なため数字必須から除外
            if pat in EVIDENCE_PATTERNS and pat not in ("competitive_landscape", "diagram") and not any(ch.isdigit() for ch in title):
                warns.append(f"{loc}: エビデンススライドのタイトルに数字がない — 図表が証明する結論の数値を1つ入れる")

        if pat == "financial_highlights" and len(s.get("groups", [])) > 3:
            warns.append(f"{loc}: financial_highlights の groups が {len(s['groups'])} 件 — ヒーローカードは3枚まで。"
                         "4件目以降の主指標は補助ストリップへ回るため、グループを3つに絞るかスライドを分割する")

        # speaker_notes はトークスクリプト専用。設計メタデータの混入と、読み上げに
        # 耐えない薄さを検出する(cover と構造スライドは薄くてよい)
        notes = s.get("speaker_notes", "")
        META_MARKERS = ("judgment", "reader_question", "composition", "focal", "rhythm",
                        "evidence_strategy", "single_takeaway", "grid_role")
        leaked = [m for m in META_MARKERS if m in notes]
        if leaked:
            warns.append(f"{loc}: speaker_notes に設計メタデータが混入({', '.join(leaked[:3])}) — "
                         "ノートは読み上げ用トークスクリプトのみ。判断フィールドは outline/作業ノートへ")
        if pat not in STRUCTURAL and pat != "cover" and notes and len(notes) < 80:
            warns.append(f"{loc}: speaker_notes が薄い({len(notes)}字) — 主張→根拠の順路→含意→次スライドへの"
                         "橋渡しを話し言葉で150-300字目安に書く")
        if notes and pat != "cover":
            import re as _re_ts
            # 話法: スクリプトは読み上げ用の敬体。体言止めのメモ書きはナレーションにならない
            if len(notes) >= 80 and "です" not in notes and "ます" not in notes:
                warns.append(f"{loc}: speaker_notes が話し言葉でない(です/ます不在) — "
                             "読み上げられる敬体のナラティブに書き直す")
            # タイトル逐語読みの冒頭は禁止(主張は話し言葉で言い換えて開く)
            if title and len(title) >= 8 and title in notes[: len(title) + 15]:
                warns.append(f"{loc}: speaker_notes の冒頭がタイトルの逐語読み — 主張を話し言葉で言い換えて開く")
            # 内容整合: スライドに存在しない「数値+単位」がスクリプトにあるのは、本体改稿への
            # 追従漏れ(スクリプトドリフト)か幻覚の兆候。数字だけの照合では単位違い
            # (スライド 120社 / スクリプト 120億円)を素通しするため、単位ペアで照合する。
            # スライド側コーパスは可視文字列に加え、数値リーフ(チャートの values 等の
            # int/float)も取り込む — 文字列だけだとネイティブチャートの数値を話した正しい
            # スクリプトが偽陽性になる。value/values と unit が同じ dict にある構造
            # (KPI・チャート系列)は「値+単位」の結合トークンとしても照合する。
            _corpus_parts, _unit_pairs = [], set()
            _UNIT_RE = _re_ts.compile(r"(億円|兆円|億|兆|万|円|%|％|件|社|名|人|カ月|ヶ月|か月|週間|時間|倍|pt)")
            def _numstr(x):
                xs = str(x)
                return xs[:-2] if xs.endswith(".0") else xs
            def _num_variants(xs):
                xs = xs.lstrip("+△▲-−").replace(",", "")
                out = {xs}
                if xs.endswith(".0"):
                    out.add(xs[:-2])
                if "." not in xs:
                    out.add(xs + ".0")
                return out
            def _is_neg(x):
                if isinstance(x, (int, float)):
                    return x < 0
                return isinstance(x, str) and x.strip()[:1] in ("△", "▲", "-", "−")
            _neg_pairs = set()  # 負値として現れた number+unit
            _pos_pairs = set()  # 正値としても現れた number+unit(負専用判定の除外用)
            # 描画制御メタデータ(強調 index・予想開始 index・注記オフセット等)はデータ値では
            # ないので unit とペアにしない — focal_category:1 が「1億円」を通してしまう
            _CTRL_KEYS = {"focal_category", "forecast_from", "emphasis_col", "emphasis_row",
                          "focal_phase", "focal_step", "col_widths", "col0_spans",
                          "dx", "dy", "target", "number_format", "axis_number_format"}
            def _subtree_numbers(o, acc):
                if isinstance(o, dict):
                    for kk, vv in o.items():
                        if kk in _CTRL_KEYS:
                            continue
                        _subtree_numbers(vv, acc)
                elif isinstance(o, list):
                    for vv in o:
                        _subtree_numbers(vv, acc)
                elif isinstance(o, (int, float)) and not isinstance(o, bool):
                    acc.add(_numstr(o))
                elif isinstance(o, str) and _re_ts.fullmatch(r"[△▲+\-−]?\d[\d,.]*", o.strip()):
                    acc.add(o.strip())
            def _walk_nums(o):
                if isinstance(o, dict):
                    o = {kk: vv for kk, vv in o.items() if kk not in _CTRL_KEYS}
                    unit = o.get("unit") if isinstance(o.get("unit"), str) else None
                    if unit:
                        # unit はその dict のサブツリー全体の数値に適用される(チャートの
                        # series[].values、waterfall items[].value、guidance の current 等)
                        nums = set()
                        _subtree_numbers(o, nums)
                        v = o.get("value")
                        if isinstance(v, str):
                            nums.add(v)
                        for n in nums:
                            for var in _num_variants(n):
                                _unit_pairs.add(var + unit)
                                (_neg_pairs if _is_neg(n) else _pos_pairs).add(var + unit)
                    if isinstance(o.get("headers"), list) and isinstance(o.get("rows"), list):
                        # 表: ヘッダー内の単位表記("(億円)" 等)を数値セルとペア化する。
                        # ヘッダーに単位が1種類なら表全体に適用(「(億円)」を先頭列に置く
                        # 財務表の慣行)。複数単位が混在する表では各単位を自列のセルに
                        # 限定する — 表全体ペアリングは列跨ぎの誤値(売上10億円の表で
                        # 「10%」)を素通しする
                        col_units = [set(_UNIT_RE.findall(hd)) if isinstance(hd, str) else set()
                                     for hd in o["headers"]]
                        distinct = set().union(*col_units) if col_units else set()
                        if len(distinct) == 1:
                            cells = set()
                            for row in o["rows"]:
                                if isinstance(row, list):
                                    for c in row:
                                        _subtree_numbers(c, cells)
                            u = next(iter(distinct))
                            for c in cells:
                                for var in _num_variants(c):
                                    _unit_pairs.add(var + u)
                                    (_neg_pairs if _is_neg(c) else _pos_pairs).add(var + u)
                        elif distinct:
                            for ci_, units in enumerate(col_units):
                                if not units:
                                    continue
                                cells = set()
                                for row in o["rows"]:
                                    if isinstance(row, list) and ci_ < len(row):
                                        _subtree_numbers(row[ci_], cells)
                                for c in cells:
                                    for var in _num_variants(c):
                                        for u in units:
                                            _unit_pairs.add(var + u)
                                            (_neg_pairs if _is_neg(c) else _pos_pairs).add(var + u)
                    for vv in o.values():
                        _walk_nums(vv)
                elif isinstance(o, list):
                    for vv in o:
                        _walk_nums(vv)
                elif isinstance(o, str):
                    _corpus_parts.append(o)
                elif isinstance(o, (int, float)) and not isinstance(o, bool):
                    _corpus_parts.append(_numstr(o))
            _walk_nums({k: v for k, v in s.items() if k not in ("speaker_notes", "pattern")})
            # 区切りなし連結は JSON のキー順次第で「1」+「億円」が隣接し偽陰性を生む。
            # 連続性は単一文字列内でのみ意味を持つため、パーツ間に区切り子を挟む
            _corpus = "|".join(_corpus_parts).replace(",", "").replace(" ", "")
            alien = []
            sign_flips = []
            _NEG_MARKERS = ("△", "▲", "-", "−", "マイナス", "赤字", "損失", "減少", "減益", "減収", "減")
            # 構造カウント(ステップ/フェーズ/行/列/セル等)は「スライドの構成要素を数えた」
            # 正当なナレーションなので照合対象にしない — 対象は証拠数値の単位のみ
            for m in _re_ts.finditer(r"(\d[\d,.]*)(億円|兆円|億|兆|万|円|%|％|件|社|名|人|カ月|ヶ月|か月|週間|時間|倍|pt)", notes):
                token = m.group(1).replace(",", "") + m.group(2)
                if token not in _unit_pairs and token not in _corpus:
                    alien.append(m.group(0))
                elif token in _neg_pairs and token not in _pos_pairs and token not in _corpus:
                    # スライド上では負値(△/−)としてのみ現れる数。スクリプト側の文脈に
                    # 負方向の語(赤字/△/減 等)が無ければ、損益の向きが反転して
                    # 語られている可能性がある
                    ctx = notes[max(0, m.start() - 10): m.end() + 4]
                    if not any(mk in ctx for mk in _NEG_MARKERS):
                        sign_flips.append(m.group(0))
            if alien:
                warns.append(f"{loc}: speaker_notes にスライド上に無い数値: {', '.join(dict.fromkeys(alien))} — "
                             "スクリプトは本体と同じ根拠だけを話す(本体改稿後の追従漏れ/幻覚の兆候)")
            if sign_flips:
                warns.append(f"{loc}: speaker_notes の {', '.join(dict.fromkeys(sign_flips))} はスライド上では負値(△) — "
                             "赤字/減少などの向きを示す語を添えるか、符号の反転がないか確認する")

        import re as _re
        zenkaku = [t for t in iter_texts({k: v for k, v in s.items() if k != "pattern"})
                   if _re.search(r"[０-９Ａ-Ｚａ-ｚ％\uFF0D]", t)]
        if zenkaku:
            warns.append(f"{loc}: 全角英数字が含まれる — 英数字は半角に統一: '{zenkaku[0][:24]}'")

        # source は真の出典(外部の組織・レポート・日付、または検証可能な内部システム名)のみ。
        # 会議録や社内資料など単一の内部アーティファクトから作る資料は、meta.basis に一度だけ
        # 記録すれば足りる(スライドには描画されない)。全スライドへ同一の内部出典フッターを
        # スタンプするのはノイズであり、source の信頼性自体を毀損する。
        deck_basis = (deck.get("meta") or {}).get("basis")
        if pat in EVIDENCE_PATTERNS and not (s.get("source") or s.get("assumption") or deck_basis):
            warns.append(f"{loc}: evidence slide without 'source' — add a real external source, "
                         "'assumption' for internal estimates, or meta.basis when the whole deck "
                         "derives from one internal artifact")
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

        # スライド本体の chart と chart_grid の各セルを同じ検査に通す。セルは image-kind の
        # セル単位エスカレーションを持てるため、本体だけ検査すると同じ「黙って落ちる」罠が
        # セル側に残る(annotation 系の警告・型/系列チェックとも共通)。
        _charts = []
        if s.get("chart"):
            _charts.append((s["chart"], loc))
        if pat == "chart_grid":
            if len(s.get("charts", [])) > 4:
                errors.append(f"{loc}: chart_grid の charts が {len(s['charts'])} 件 — パターン契約は2-4。"
                              "5件目以降はビルドで黙って切り捨てられるため、セルを絞るかスライドを分割する")
            for _ci, _cell in enumerate(s.get("charts", []), start=1):
                if isinstance(_cell, dict):
                    _charts.append((_cell.get("chart", _cell), f"{loc} cell {_ci}"))
        if pat == "diagram":
            # diagram の asset spec も同じ image-kind 検査(必須フィールド/annotations 罠)に通す。
            # バイパスすると org_tree の edges 欠落などが 0 errors で通り、Graphviz 描画で落ちる
            _dg = s.get("diagram") or {}
            if _dg.get("kind") not in IMAGE_ASSET_KINDS:
                errors.append(f"{loc}: diagram kind '{_dg.get('kind')}' は未対応 — "
                              f"{', '.join(sorted(IMAGE_ASSET_KINDS))} から選ぶ")
            else:
                _charts.append((_dg, f"{loc} diagram"))
        for chart, cloc in _charts:
            if chart and chart.get("render") == "image" and chart.get("kind") not in IMAGE_ASSET_KINDS:
                # 強制 image 指定でも未知 kind は画像バックエンドが受けない(build が落ちる)
                errors.append(f"{cloc}: render:'image' だが kind '{chart.get('kind')}' は image バックエンド非対応 — "
                              f"{', '.join(sorted(IMAGE_ASSET_KINDS))} から選ぶか render を外す")
                chart = None
            if chart and chart.get("kind") in IMAGE_ASSET_KINDS:
                # image-asset chart (combo/area/…): rendered by act_assets, not the native engine.
                k = chart.get("kind")
                missing = [fld for fld in IMAGE_KIND_REQUIRED.get(k, ()) if not chart.get(fld)]
                if missing:
                    errors.append(f"{cloc}: image chart '{k}' に必須フィールドがない: {', '.join(missing)}")
                else:
                    # データ形状の検査。ネイティブ検査(長さ/数値)をスキップする分、image kind も
                    # ここで同等の検査を通す — 素通しすると matplotlib が build 時に落ちる
                    def _nums_ok(vals):
                        return isinstance(vals, list) and vals and all(
                            isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals)
                    cats_n = len(chart.get("categories") or [])
                    if k == "combo":
                        for part in ("bar", "line"):
                            pv = (chart.get(part) or {}).get("values")
                            if not _nums_ok(pv):
                                errors.append(f"{cloc}: combo の {part}.values は数値リスト必須")
                            elif len(pv) != cats_n:
                                errors.append(f"{cloc}: combo の {part}.values が {len(pv)} 件で categories {cats_n} 件と不一致")
                    elif k in ("area", "line_multi"):
                        for ser in chart.get("series", []):
                            pv = ser.get("values")
                            if not _nums_ok(pv):
                                errors.append(f"{cloc}: {k} series '{ser.get('name')}' の values は数値リスト必須")
                            elif len(pv) != cats_n:
                                errors.append(f"{cloc}: {k} series '{ser.get('name')}' が {len(pv)} 件で categories {cats_n} 件と不一致")
                    elif k == "radar":
                        axes_n = len(chart.get("axes") or [])
                        for ser in chart.get("series", []):
                            pv = ser.get("values")
                            if not _nums_ok(pv):
                                errors.append(f"{cloc}: radar series '{ser.get('name')}' の values は数値リスト必須")
                            elif len(pv) != axes_n:
                                errors.append(f"{cloc}: radar series '{ser.get('name')}' が {len(pv)} 件で axes {axes_n} 件と不一致")
                    elif k == "waterfall":
                        bad = [it_.get("label") for it_ in chart.get("items", [])
                               if not isinstance(it_.get("value"), (int, float)) or isinstance(it_.get("value"), bool)]
                        if bad:
                            errors.append(f"{cloc}: waterfall items の value が数値でない: {', '.join(str(b) for b in bad[:3])}")
                    elif k in ("scatter", "bubble"):
                        for pt_ in chart.get("points", []):
                            if not all(isinstance(pt_.get(ax_), (int, float)) and not isinstance(pt_.get(ax_), bool)
                                       for ax_ in ("x", "y")):
                                errors.append(f"{cloc}: {k} points は数値の x/y 必須")
                                break
                    elif k in ("ring", "funnel"):
                        key = "segments" if k == "ring" else "stages"
                        segs_ = chart.get(key, [])
                        bad = [seg.get("label") for seg in segs_
                               if not isinstance(seg.get("value"), (int, float)) or isinstance(seg.get("value"), bool)]
                        if bad:
                            errors.append(f"{cloc}: {k} {key} の value が数値でない: {', '.join(str(b) for b in bad[:3])}")
                        else:
                            vals_ = [seg.get("value") for seg in segs_]
                            if vals_ and (max(vals_) <= 0):
                                # レンダラーは最大値/合計で正規化するため、全て0以下だと
                                # ゼロ除算で build が落ちる — preflight で弾く
                                errors.append(f"{cloc}: {k} {key} の value が全て0以下 — 正の値を1つ以上入れる")
                            elif any(v < 0 for v in vals_):
                                errors.append(f"{cloc}: {k} {key} に負の値 — {k} は非負の量のみ表現できる")
                # track trap: native badge on an image chart is ignored — image uses `annotations`
                if chart.get("annotation"):
                    warns.append(f"{cloc}: image chart '{k}' ignores native `annotation` — use `annotations:[{{target,text}}]`")
                if chart.get("annotations") and k in ("org_tree", "node_graph"):
                    warns.append(f"{cloc}: `annotations` are not rendered on Graphviz '{k}' — use edge labels")
                elif chart.get("annotations") and k not in ("combo", "waterfall") and any(
                        isinstance(a, dict) and isinstance(a.get("target"), int) for a in chart["annotations"]):
                    warns.append(f"{cloc}: image chart '{k}' は int target のアンカーを持たず黙って落ちる — "
                                 "combo/waterfall 以外は target を {'x','y'} のデータ座標で指定する")
                chart = None  # skip native-chart checks below
            if chart:
                # track trap: image `annotations` on a native chart is silently ignored
                if chart.get("annotations"):
                    warns.append(f"{cloc}: native chart ignores `annotations` — use `annotation.badge/trend_arrow`, or set an image `kind`")
                ctype = chart.get("type", "column")
                if ctype not in SUPPORTED_CHART_TYPES:
                    errors.append(f"{cloc}: chart type '{ctype}' は未対応 — {' / '.join(SUPPORTED_CHART_TYPES)} から選ぶ")
                cats, series = chart.get("categories", []), chart.get("series", [])
                if not cats or not series:
                    errors.append(f"{cloc}: chart needs categories and series")
                values_numeric = True
                for ser in series:
                    if len(ser.get("values", [])) != len(cats):
                        errors.append(f"{cloc}: series '{ser.get('name')}' has {len(ser.get('values', []))} values for {len(cats)} categories")
                    bad = [v for v in ser.get("values", []) if isinstance(v, bool) or not isinstance(v, (int, float))]
                    if bad:
                        values_numeric = False
                        errors.append(f"{cloc}: series '{ser.get('name')}' の values に数値でない要素: {bad[0]!r}")
                if len(series) > 4:
                    errors.append(f"{cloc}: {len(series)} series — max 4; aggregate or split the chart")
                ff = chart.get("forecast_from")
                if ff is not None:
                    try:
                        ff = int(ff)
                    except (TypeError, ValueError):
                        errors.append(f"{cloc}: forecast_from は整数 index で指定する(現在: {ff!r})")
                        ff = None
                if ff is not None:
                    if len(series) > 1 or chart.get("type", "column") not in ("column", "bar"):
                        warns.append(f"{cloc}: forecast_from は単一系列の column/bar のみ有効 — line・複数系列では描き分けされない。categories の E 表記+注記で区別するか column に変える")
                    else:
                        def _marked(c):
                            cs = str(c)
                            return cs.endswith("E") or any(m in cs for m in ("予", "計画", "見込", "見通し", "目標"))
                        unmarked = [str(c) for c in cats[ff:] if not _marked(c)]
                        if unmarked:
                            warns.append(f"{cloc}: forecast_from 以降のカテゴリに予想表記(E/計画/予想)がない: {', '.join(unmarked[:3])}")
                if not chart.get("unit"):
                    warns.append(f"{cloc}: chart has no 'unit' — add one (e.g. 億円, %) unless truly unitless")
                if values_numeric and chart.get("type", "column") in ("column", "bar", "stacked_column") and any(
                        float(v) < 0 for ser in series for v in ser.get("values", [])):
                    warns.append(f"{cloc}: negative values in a {chart.get('type', 'column')} chart — LibreOffice render-QA draws them wrong (PowerPoint is fine); prefer 'line', the waterfall pattern, or keep negatives in a table")

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
        # 比較表の列上限(rubric.json layout と同じ 4 列)。年度列が並ぶ financial_summary は対象外
        if pat == "comparison_table":
            ncols = len((s.get("table") or {}).get("headers", []))
            if ncols > 4:
                warns.append(f"{loc}: 比較表が{ncols}列 — ラベル列を含め4列以内にする(超える対象は列統合か絞り込み、残りは note か別スライドへ)")
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
        if nado > 1:
            warns.append(f"{loc}: 「など/等」が{nado}回 — 名前を列挙するか削る(1スライド1回まで)")

    # emphasis-device rationing: insight / kicker lose force when they appear everywhere
    n_insight = sum(1 for s in slides if s.get("insight"))
    if n_insight > 4:
        warns.append(f"insight バーが{n_insight}枚 — 非自明な判断がある 2-4 枚に絞る(全部に置くと強調が消える)")
    # header kicker (label above the title) is retired — it breaks header uniformity
    for i, s in enumerate(slides, start=1):
        if s.get("kicker"):
            warns.append(f"slide {i}: ヘッダー上の kicker「{s['kicker']}」— ヘッダーの統一性を崩すため使わない。問いはサブタイトルか speaker_notes へ(build_deck は描画しない)")

    # executive_summary の points は section_divider の章立てと整合させる(冒頭サマリー=章マップ)。
    # 許容形は (a) 1:1 で kicker=章タイトル、または (b) 各章が同数の点をまとめる均等グルーピング
    # (例: 4点を2章で 2点ずつ)。点数が章数で割り切れない中途半端な対応をドリフトとして検出する。
    dividers = [s.get("title", "") for s in slides if s.get("pattern") == "section_divider"]
    for i, s in enumerate(slides, start=1):
        if s.get("pattern") != "executive_summary":
            continue
        pts = s.get("points", [])
        klabels = [p.get("kicker", "") for p in pts]
        if dividers and pts:
            nd, npt = len(dividers), len(pts)
            if npt == nd:
                if klabels != dividers:
                    warns.append(f"slide {i}: executive_summary の kicker が章タイトルと不一致 — 各点の kicker を章扉と同じ語順・同じ語に揃える: points={klabels} / 章={dividers}")
            elif npt < nd or npt % nd != 0:
                warns.append(f"slide {i}: executive_summary {npt}点 ↔ 章扉{nd}章がズレている — 1:1(kicker=章タイトル)か、各章が同数の点をまとめる均等グルーピング(例 {nd}章なら {nd} か {nd*2} 点)に揃える")

    # adjacent-slide monotony: same content pattern back to back reads as a template loop
    prev_pat = None
    for i, s in enumerate(slides, start=1):
        pat = s.get("pattern")
        if pat and pat == prev_pat and pat not in STRUCTURAL:
            warns.append(f"slide {i}: 直前のスライドと同じパターン '{pat}' が連続 — 内容が同型でないなら構成を散らす")
        prev_pat = pat

    # --- Section dividers belong to LONGER / read-oriented decks ---
    # A short talk deck should flow on its action titles; a hard section reset before a
    # 1-2 slide "chapter" only injects 断絶 (a full stop that breaks narrative momentum)
    # without improving readability. Dividers earn their place when the deck is long enough
    # to need navigation AND each chapter carries real proof. [design-principles: Section
    # Dividers / slide-decision-engine §4 Navigation]
    LONG_DECK_MIN = 18  # total slides; at/above this a deck reads as a document, not a talk
    is_long_deck = len(slides) >= LONG_DECK_MIN
    div_idx = [i for i, s in enumerate(slides) if s.get("pattern") == "section_divider"]
    D = len(div_idx)
    content_n = sum(1 for s in slides if s.get("pattern") not in STRUCTURAL)
    if D:
        bounds = div_idx + [len(slides)]
        thin = [slides[div_idx[k]].get("title", f"#{div_idx[k] + 1}")
                for k in range(D)
                if sum(1 for s in slides[bounds[k] + 1:bounds[k + 1]]
                       if s.get("pattern") not in STRUCTURAL) <= 1]
        if thin:
            warns.append(f"section_divider の章が内容1枚以下: {'、'.join(thin)} — 区切りが読みやすさに寄与せず断絶を生む。次スライドに折り込むか区切りを削る")
        if not is_long_deck and content_n < 3 * (D + 1):
            warns.append(f"短いデック({len(slides)}枚)に区切り{D}枚 — 1章あたり内容{content_n / (D + 1):.1f}枚。区切りは枚数が多い/読ませる資料向け。短いプレゼンはアクションタイトルで流し、区切りは削るか最小限に")

    # visual rhythm: only a LONGER read deck suffers the wall-of-content problem; a short
    # talk deck is meant to flow continuously, so it is not pushed toward a rest/divider
    # there. In a read deck, insert a rest (section_divider or a quiet statement) every
    # 3-5 slides. [design-principles 11b]
    if is_long_deck:
        run = 0
        for i, s in enumerate(slides, start=1):
            if s.get("pattern") in STRUCTURAL:
                run = 0
                continue
            run += 1
            if run == 6:
                warns.append(f"slide {i}: コンテンツが6枚以上連続 — 読ませるデックでは3-5枚ごとに休符(section_divider / statement)を挟む(視覚リズム)")

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

    # NOTE: タイトル行数・サブタイトル有無の「混在」警告は廃止 — 1行超過も subtitle 欠落も
    # per-slide の ERROR に昇格したため(全スライド必須・各1行)、混在は起こり得ない

    # kicker length budget (short label, not a sentence)
    for i, s in enumerate(slides, start=1):
        if s.get("kicker") and ja_len(s["kicker"]) > BUDGET["kicker_max_chars_ja"]:
            warns.append(f"slide {i}: kicker が{ja_len(s['kicker']):.0f}字 — {BUDGET['kicker_max_chars_ja']}字以内の短いラベルにする(文にしない)")

    # process_flow density: ≤3 bullets per step card (4カード×3行で既に12行 —
    # それ以上は「概要+ステップ別詳細スライド」に分割する)
    for i, s in enumerate(slides, start=1):
        if s.get("pattern") == "process_flow":
            fs = s.get("focal_step")
            n_steps = len(s.get("steps", []))
            if fs is not None and not (isinstance(fs, int) and 0 <= fs < n_steps):
                warns.append(f"slide {i}: focal_step={fs} が 0..{n_steps - 1} の整数でない — "
                             "整数の範囲外はクランプ、非数値は既定(最終ステップ)へフォールバックする。"
                             "意図したステップか確認する")
            fat = [st.get("label", f"step{j+1}") for j, st in enumerate(s.get("steps", []))
                   if len(st.get("items", [])) > 3]
            if fat:
                warns.append(f"slide {i}: ステップの項目が3個超({', '.join(fat)}) — カードあたり3項目以内。超える分は詳細スライドか speaker_notes へ")

    # 文体規約: スライド表示テキストは体言止め・句点なし。speaker_notes を除く可視文字列に
    # 句点(。／．)が残っていれば体言止めへの直し漏れとして警告する(build は末尾のみ自動除去)
    def _visible_strings(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k != "speaker_notes":
                    yield from _visible_strings(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from _visible_strings(v)
        elif isinstance(obj, str):
            yield obj
    period_slides = [i for i, s in enumerate(slides, start=1)
                     if any(("。" in t or "．" in t) for t in _visible_strings(s))]
    if period_slides:
        warns.append("表示テキストに句点(。)が残る: slide "
                     f"{', '.join(map(str, period_slides))} — スライドは体言止め・句点なし。"
                     "文を名詞句へ言い換えるか2項目に分ける(speaker_notes は対象外)")

    # talk script: 全コンテンツスライドに語り原稿(speaker_notes)を書く。
    # meta.talk_minutes(発表分数)があれば 300字/分 目安で総量を照合する
    content = [(i, s) for i, s in enumerate(slides, start=1) if s.get("pattern") not in STRUCTURAL]
    notes_total = sum(ja_len(s.get("speaker_notes", "")) for s in slides)
    missing_notes = [i for i, s in content if not s.get("speaker_notes")]
    if missing_notes:
        warns.append(f"speaker_notes が無いコンテンツスライド: slide {', '.join(map(str, missing_notes))}"
                     " — トークスクリプトを全コンテンツスライドに書く(表紙・扉はつなぎの一言でよい)")
    talk_min = (deck.get("meta") or {}).get("talk_minutes")
    if talk_min is not None:
        try:
            talk_min = float(talk_min)
            if talk_min <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append("meta.talk_minutes は正の数値(分)で指定する")
            talk_min = None
    if talk_min:
        est_min = notes_total / TALK_CHARS_PER_MIN
        if abs(est_min - talk_min) > talk_min * 0.25:
            warns.append(f"トークスクリプト総量 約{notes_total:,.0f}字 ≈ {est_min:.1f}分 が"
                         f" meta.talk_minutes={talk_min:g}分 と±25%超乖離 —"
                         f" {TALK_CHARS_PER_MIN}字/分 目安で各スライドの語りを増減する")
    if notes_total:
        target = f"(target {talk_min:g}分)" if talk_min else "(meta.talk_minutes 未指定)"
        print(f"talk script: 約{notes_total:,.0f}字 ≈ {notes_total / TALK_CHARS_PER_MIN:.1f}分 {target}")

    for w in warns:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(slides)} slides / {len(errors)} errors / {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
