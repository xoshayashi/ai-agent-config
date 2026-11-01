"""論証の抽出層: deck.json のどこが「証拠」で、どこが「主張」で、どこが「出所」かを一箇所で定義する。

audit_argument.py と validate_spec.py が同じ物差しで読むための単一実装。証拠と主張を混ぜて
数えると、スライドが自分の主張で自分を証明できてしまう(タイトルの数字がタイトルによって
裏づけられる)ので、キーの仕分けはここでしか行わない。
"""
from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path

LEXICON_PATH = Path(__file__).resolve().parent.parent / "references" / "commitment-lexicon.json"
TOKENS_PATH = Path(__file__).resolve().parent.parent / "references" / "tokens.json"
COMPOSITION_LABEL_MIN_WIDTH_IN = 0.7
COMPOSITION_MAX_SEGMENTS = 6
PROGRESS_MAX_ROWS = 8
TARGET_BARS_MAX_ROWS = 8
FUNNEL_MAX_STAGES = 6
PRICING_MAX_TIERS = 4
RANKING_MAX_ITEMS = 10

# 証拠(EXHIBIT): 構造化された図表の中身。ここに出る数値だけが「示された数値」
EXHIBIT_KEYS = {
    "chart", "charts", "table", "kpis", "stages", "items", "phases", "rows", "cells",
    "steps", "groups", "columns", "factors", "players", "diagram", "bars", "current",
    "side", "segments", "metrics", "recap_metrics", "series", "values", "headers",
    "hero", "facts", "root", "branches", "leaves", "hub", "numbers",
}
# 主張(CLAIM): 散文。読み手に向かって言い切る場所
CLAIM_KEYS = {
    "title", "subtitle", "desc", "lead", "insight", "statement", "recap", "takeaways",
    "points", "left", "right", "bullets", "attribution", "heading", "body", "kicker",
    "notes", "takeaways_heading", "outcome",
}
# 出所(PROVENANCE): 主張の裏づけがどこから来たか
PROV_KEYS = {"source", "assumption", "note", "qualifier"}
# 制御(CONTROL): 描画の指示であって、データではない
CONTROL_KEYS = {
    "focal_category", "forecast_from", "emphasis_col", "emphasis_row", "focal_phase",
    "focal_step", "col_widths", "col0_spans", "dx", "dy", "target", "number_format",
    "axis_number_format", "x", "y", "focal", "pattern", "variant", "layout", "speaker_notes",
    "derivation", "qualifier", "unit_label", "delta_dir", "positive_is_good", "kind",
}

# 単位は「長いものから」並べる。万 を先に置くと「2,404万人」が「2,404万」として切れ、
# 主張と図表のトークンが一致しなくなる(人・件・社は万の後ろに付く)
UNIT = (r"(?:億円|兆円|万円|百万円|万人|億人|万件|万社|万時間|万台|億円超|"
        r"億|兆|万|円|%|％|件|社|名|人|カ月|ヶ月|か月|週間|時間|倍|pt|日|時間/日)")
NUM = r"(?:△|▲|-|−|\+)?\d[\d,]*(?:\.\d+)?"
MATERIAL = re.compile(rf"({NUM})\s*({UNIT})")
YEARLIKE = re.compile(r"20\d{2}\s*年|FY\s?\d{2,4}|第[1-4]四半期|Q[1-4]")


@lru_cache(maxsize=1)
def lexicon() -> dict:
    """言い切りの語彙表。壊れていたら止まる — 黙って無力化させない。"""
    data = json.loads(LEXICON_PATH.read_text())
    required = {"promise", "rank", "hedge", "motion", "euphemism", "self_source"}
    missing = required - set(data.get("classes", {}))
    if missing:
        raise ValueError(f"commitment-lexicon.json に必要なクラスが無い: {sorted(missing)}")
    return data


def to_number(text) -> float | None:
    """表示用の数値文字列を数に。△▲ は負値、桁区切りは無視する。"""
    if isinstance(text, (int, float)):
        return float(text)
    if not isinstance(text, str):
        return None
    s = text.strip().replace(",", "").replace("−", "-")
    neg = s.startswith(("△", "▲"))
    s = s.lstrip("△▲")
    m = re.match(rf"^{NUM}$", s)
    if not m:
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        if not m:
            return None
        s = m.group()
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg and v > 0 else v


def _walk(obj, keys: set[str], collect):
    """指定したキーの部分木だけを歩く。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in CONTROL_KEYS:
                continue
            if k in keys:
                collect(v)
            else:
                _walk(v, keys, collect)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, keys, collect)


def _strings_and_numbers(obj, out: list):
    if isinstance(obj, dict):
        # value と unit が並ぶ構造(hero / facts / root / branches / kpis)は、その組で1トークンにする。
        # 平らにして「12.8」と「億円」に分けると、図表が示す「12.8億円」が消え、逆に図表全体の単位
        # (chart.unit)が無関係な値に付く(Codex レビュー指摘、PR #158)
        if "value" in obj and obj.get("unit") and not isinstance(obj["value"], (dict, list)):
            out.append(f"{obj['value']}{obj['unit']}")
        for k, v in obj.items():
            if k in CONTROL_KEYS:
                continue
            if k in ("value", "unit") and "value" in obj and obj.get("unit"):
                continue
            _strings_and_numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings_and_numbers(v, out)
    elif isinstance(obj, (str, int, float)):
        out.append(obj)


def composition_bar_width_in(template: str | None = None) -> float:
    """12-column body width used by composition_bar under the deck's selected template."""
    from deck_text import resolve_tokens
    tokens = resolve_tokens(template)
    layout, slide = tokens["layout"], tokens["slide"]
    columns, gutter = layout["grid_columns"], layout["gutter_in"]
    margin, slide_w = layout["margin_x_in"], slide["width_in"]
    try:
        numeric_columns = float(columns)
    except (TypeError, ValueError, OverflowError):
        numeric_columns = float("nan")
    if (not isinstance(columns, (int, float)) or isinstance(columns, bool)
            or not math.isfinite(numeric_columns) or not numeric_columns.is_integer() or numeric_columns < 12):
        raise ValueError("layout.grid_columns は12以上の整数")
    columns = int(numeric_columns)
    if any(not _finite_nonnegative(value) for value in (margin, gutter, slide_w)):
        raise ValueError("テンプレートのスライド幅・余白・列間隔は有限の非負数")
    margin, gutter, slide_w = float(margin), float(gutter), float(slide_w)
    try:
        content_w = slide_w - 2 * margin
        if content_w <= 0 or content_w - gutter * (columns - 1) <= 0:
            raise ValueError("テンプレートのグリッド幅は正の数")
        col_w = (content_w - gutter * (columns - 1)) / columns
        width = 12 * col_w + 11 * gutter
    except ArithmeticError as exc:
        raise ValueError("テンプレートのグリッド幅を計算できない") from exc
    if not math.isfinite(width) or width <= 0:
        raise ValueError("構成バーの幅は有限の正の数")
    return width


def _finite_nonnegative(value) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        number = float(value)
    except OverflowError:
        return False
    return math.isfinite(number) and number >= 0


def composition_bar_label(value: float, total: float, segment_width_in: float) -> str | None:
    """Label text shared by the renderer and the audit; narrow segments have no visible percentage."""
    if not math.isfinite(segment_width_in) or segment_width_in < COMPOSITION_LABEL_MIN_WIDTH_IN:
        return None
    return f"{value / total * 100:.0f}%" if total else "0%"


def _audit_number(value, default: float = 0.0) -> float:
    try:
        result = float(value) if value not in (None, "") else default
        return result if math.isfinite(result) else default
    except (TypeError, ValueError, OverflowError):
        return default


def _audit_items(value, limit: int) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value[:limit] if isinstance(item, dict)]


def _visible_fields(items: list[dict], *fields: str) -> list[dict]:
    return [{key: item[key] for key in fields if key in item} for item in items]


def material_tokens(values: list) -> set[str]:
    """「数値+単位」のトークン集合。年や四半期は数えない(データではなく期間)。"""
    tokens: set[str] = set()
    for v in values:
        if isinstance(v, (int, float)):
            continue                      # 単位の無い裸の数は、単位付きトークンと突き合わせない
        if not isinstance(v, str):
            continue
        for m in MATERIAL.finditer(v):
            token = f"{m.group(1)}{m.group(2)}"
            if YEARLIKE.fullmatch(token.strip()):
                continue
            if m.group(2) == "年":
                continue
            tokens.add(token.replace(",", ""))
    return tokens


# composite のブロック種 → 監査で見せるキー。セル(cells)は roadmap の表セルと同じ名前で EXHIBIT に
# 入っているため、そのまま歩くと text / callout の主張まで「図表が示した数値」になり、裏づけの無い
# 数字が監査を素通りする(Claude レビュー指摘、2026-10-28)。ブロックごとに主張と証拠へ振り分ける
_COMPOSITE_KEYS = {"chart": ("chart",), "table": ("table",), "kpi": ("kpis",), "diagram": ("diagram",),
                   "text": ("heading", "points"), "callout": ("heading", "statement")}


def audit_view(slide: dict, template: str | None = None) -> dict:
    """監査が歩く形のスライド。composite は grid を外し、ブロックの中身を種別どおりのキーで並べ直す
    (text の見出し・要点と callout は主張、chart / table / kpi / diagram は証拠)。他のパターンはそのまま。"""
    if slide.get("pattern") == "big_number":
        view = dict(slide)
        if slide.get("value") not in (None, ""):
            view["facts"] = [{"value": slide["value"], "unit": slide.get("unit", "")}]
        return view
    pattern = slide.get("pattern")
    if pattern in {"progress_bars", "target_bars", "composition_bar", "funnel", "pricing_tiers", "ranking"}:
        # Start from visible text only; arbitrary evidence-shaped or pattern-inapplicable
        # fields must not become facts just because they are present in the input.
        visible_keys = {"pattern"}
        visible_keys.update(key for key in ("title", "subtitle", "insight", "sticker")
                            if isinstance(slide.get(key), str))
        view = {key: slide[key] for key in visible_keys if key in slide}
        facts: list = []
        if pattern == "progress_bars":
            bars = _audit_items(slide.get("bars"), PROGRESS_MAX_ROWS)
            view["bars"] = _visible_fields(bars, "label", "note")
            facts.extend(r.get("display") or f"{_audit_number(r.get('value')) * 100:.0f}%" for r in bars)
        elif pattern == "target_bars":
            if isinstance(slide.get("legend"), str):
                facts.append(slide["legend"])
            rows = _audit_items(slide.get("rows"), TARGET_BARS_MAX_ROWS)
            view["rows"] = _visible_fields(rows, "label", "note")
            facts.extend(r.get("display") or f"{_audit_number(r.get('actual')) / (_audit_number(r.get('target'), 1.0) or 1.0) * 100:.0f}%"
                         for r in rows)
        elif pattern == "composition_bar":
            segments = _audit_items(slide.get("segments"), COMPOSITION_MAX_SEGMENTS)
            view["segments"] = _visible_fields(segments, "label", "note")
            total = sum(_audit_number(s.get("value")) for s in segments) or 1.0
            bar_width = composition_bar_width_in(template)
            if isinstance(slide.get("total_label"), str) and slide["total_label"]:
                facts.append(slide["total_label"])
            facts.extend(label for s in segments
                         if (label := composition_bar_label(_audit_number(s.get("value")), total,
                                                            bar_width * _audit_number(s.get("value")) / total)) is not None)
        elif pattern == "funnel":
            stages = _audit_items(slide.get("stages"), FUNNEL_MAX_STAGES)
            view["stages"] = _visible_fields(stages, "label", "note")
            facts.extend(s.get("display") or f"{_audit_number(s.get('value')):,.0f}" for s in stages)
            for i in range(1, len(stages)):
                previous = _audit_number(stages[i - 1].get("value"))
                if previous:
                    facts.append(f"{_audit_number(stages[i].get('value')) / previous * 100:.0f}%")
        elif pattern == "pricing_tiers":
            tiers = _audit_items(slide.get("tiers"), PRICING_MAX_TIERS)
            visible_tiers = _visible_fields(tiers, "name", "note")
            for visible, tier in zip(visible_tiers, tiers):
                if isinstance(tier.get("features"), list):
                    visible["features"] = [feature for feature in tier["features"] if isinstance(feature, str)]
            view["tiers"] = visible_tiers
            if isinstance(slide.get("focal_label"), str) and slide["focal_label"] and any(t.get("focal") for t in tiers):
                facts.append(slide["focal_label"])
            facts.extend({"value": t.get("price", ""), "unit": t.get("unit", ""),
                          "label": t.get("name", ""), "note": t.get("note", ""),
                          "features": ([feature for feature in t["features"] if isinstance(feature, str)]
                                       if isinstance(t.get("features"), list) else [])}
                         for t in tiers)
        elif pattern == "ranking":
            items = _audit_items(slide.get("items"), RANKING_MAX_ITEMS)
            unit = slide.get("unit", "")
            view["items"] = _visible_fields(items, "label")
            facts.extend(item.get("display") or f"{_audit_number(item.get('value')):g}{unit}" for item in items)
        view["facts"] = facts
        return view
    if slide.get("pattern") != "composite":
        return slide
    view = {k: v for k, v in slide.items() if k not in ("grid", "blocks")}
    claims: list = []
    exhibits: list = []
    charts = []
    if slide.get("grid"):
        cell_blocks = [(c.get("block") or {}) for r in slide["grid"] for c in (r.get("cells") or [])]
    else:                                        # 配置探索に任せた形(blocks)も同じ振り分け
        cell_blocks = [b for b in (slide.get("blocks") or []) if isinstance(b, dict)]
    for b in cell_blocks:
        keys = _COMPOSITE_KEYS.get(b.get("type"), ())
        part = {k: b[k] for k in keys if k in b}
        if b.get("type") in ("text", "callout"):
            # パネルの hero(大きな数字+名前)は KPI と同じく「示す」数 — 図表側に数える。
            # 一文(statement)は主張のまま(hero の数を言い換えた文は、図表の数で裏付けられる)
            hero = b.get("hero") if b.get("type") == "callout" else None
            if isinstance(hero, dict) and hero.get("value") not in (None, ""):
                exhibits.append({"hero": hero})
            if part:
                claims.append(part)
        else:
            if b.get("heading"):
                claims.append({"heading": b["heading"]})
            exhibits.append(part)
            if b.get("type") == "chart" and isinstance(b.get("chart"), dict):
                charts.append(b["chart"])
    view["points"] = claims                      # CLAIM_KEYS の 1 つ: 主張として歩かれる
    view["facts"] = exhibits                     # EXHIBIT_KEYS の 1 つ: 証拠として歩かれる
    if len(charts) == 1 and "chart" not in view:
        view["chart"] = charts[0]                # 図表の単位(chart.unit)を裸の数に付けるため
    return view


def exhibit_values(slide: dict, template: str | None = None) -> list:
    """図表が持つ値(文字列・数値)を平らに集める。"""
    out: list = []
    _walk(audit_view(slide, template), EXHIBIT_KEYS, lambda v: _strings_and_numbers(v, out))
    return out


def claim_values(slide: dict) -> list:
    """主張(散文)の文字列を集める。"""
    out: list = []
    _walk(audit_view(slide), CLAIM_KEYS, lambda v: _strings_and_numbers(v, out))
    return [v for v in out if isinstance(v, str)]


# 図表全体の単位(chart.unit / slide.unit)を付けてよい裸の数の在り処。facts・hero・table のような
# 隣接する構造の数に chart.unit を付けると「8420」が「8420億円」に化ける(Codex レビュー指摘、PR #158)
UNIT_SCOPED_KEYS = {"chart", "charts", "series", "values", "items", "bars", "current", "stages", "phases"}


def _unit_scoped_values(slide: dict, template: str | None = None) -> list:
    """図表そのものの数値(chart の series 値、waterfall の items 等)だけを平らに集める。"""
    out: list = []
    _walk(audit_view(slide, template), UNIT_SCOPED_KEYS, lambda v: _strings_and_numbers(v, out))
    return out


def exhibit_tokens(slide: dict, template: str | None = None) -> set[str]:
    """その図表が「示している」数値。"""
    values = exhibit_values(slide, template)
    tokens = material_tokens(values)
    # 図表の裸の数値(chart の values 等)も、単位を付けたトークンとして数える — ただし対象は
    # 図表データそのものだけで、facts / hero / table の数には付けない
    view = audit_view(slide, template)
    unit = view.get("unit") or (view.get("chart") or {}).get("unit")
    if unit:
        for v in _unit_scoped_values(slide, template):
            # 図表全体の単位を付けるのは「裸の数」だけ。「114%」のように単位を持つ文字列や、
            # 単位と組になった値には付けない(そうしないと 114% が 114億円 に化ける)
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                n = float(v)
            elif isinstance(v, str) and re.fullmatch(NUM, v.strip().replace(",", "")):
                n = to_number(v)
            else:
                continue
            if isinstance(n, float):
                tokens.add(_fmt(n) + str(unit))
    return tokens


def claim_tokens(slide: dict) -> set[str]:
    """その散文が「言っている」数値。"""
    return material_tokens(claim_values(slide))


def _fmt(v: float) -> str:
    return str(int(v)) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def visible_strings(slide: dict) -> list[str]:
    """スライド上に描かれる文字列(出所・注記・トークスクリプトを除く)。"""
    out: list[str] = []

    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in PROV_KEYS or k == "speaker_notes" or k in CONTROL_KEYS:
                    continue
                rec(v)
        elif isinstance(o, list):
            for v in o:
                rec(v)
        elif isinstance(o, str):
            out.append(o)

    rec(slide)
    return out


# ---------------------------------------------------------------------------
# derivation: 計算された数値は、計算し直せる形で宣言する
# ---------------------------------------------------------------------------
KINDS = {"cagr", "growth", "multiple", "share", "ratio", "delta", "sum", "product"}


def resolve_path(slide: dict, path):
    """"chart.series[0].values" のようなパスを、スライドの中の値へ解決する(eval しない)。
    数、数の並び、集約({"mid": [...]})も受ける — 図表を持たない要約ページでも、計算を宣言できる。"""
    if isinstance(path, bool):
        raise ValueError("真偽値は数値ではない")
    if isinstance(path, (int, float)):
        return float(path)
    if isinstance(path, list):
        return [to_number(v) for v in path]
    if isinstance(path, dict):                       # {"mid": [a, b]} / {"sum": [...]} / {"avg": [...]}
        for op, args in path.items():
            vals = [resolve_path(slide, a) for a in args]
            flat: list[float] = []
            for v in vals:
                flat.extend(v if isinstance(v, list) else [v])
            if op == "mid":
                return sum(flat) / len(flat)
            if op == "sum":
                return sum(flat)
            if op == "avg":
                return sum(flat) / len(flat)
            raise ValueError(f"未知の集約: {op}")
    if not isinstance(path, str):
        raise ValueError(f"パスが文字列でない: {path!r}")
    cur = slide
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if part.startswith("["):
            cur = cur[int(part[1:-1])]
        else:
            cur = cur[part]
    if isinstance(cur, list):
        return [to_number(v) for v in cur]
    return to_number(cur)


def compute(slide: dict, deriv: dict) -> float:
    """宣言された導出を計算する。"""
    kind = deriv.get("kind")
    if kind not in KINDS:
        raise ValueError(f"未知の kind: {kind}")
    if kind == "cagr":
        if "years" in deriv:                          # 起点・終点・年数(図表を持たない要約ページ向け)
            a = resolve_path(slide, deriv["a"])
            b = resolve_path(slide, deriv["b"])
            n = int(deriv["years"])
        else:                                         # 図表の系列から(始点と終点の位置を指定)
            series = resolve_path(slide, deriv["of"])
            i, j = int(deriv["from"]), int(deriv["to"])
            if not isinstance(series, list) or j <= i or j >= len(series):
                raise ValueError("cagr: from < to かつ系列の範囲内であること")
            a, b, n = series[i], series[j], j - i
        if not a or a <= 0 or b is None or n <= 0:
            raise ValueError("cagr: 起点が正の値、年数が正であること")
        return ((b / a) ** (1 / n) - 1) * 100
    a = resolve_path(slide, deriv.get("a", deriv.get("part", deriv.get("of"))))
    b = resolve_path(slide, deriv.get("b", deriv.get("whole")))
    if isinstance(a, list) and kind == "sum":
        return sum(v for v in a if v is not None)
    if kind == "growth":
        return (b / a - 1) * 100
    if kind == "multiple":
        return b / a
    if kind == "share":
        return a / b * 100
    if kind == "ratio":
        return a / b
    if kind == "delta":
        return b - a
    if kind == "product":                             # 母数 × 比率(SAM の積み上げ等)
        return a * b
    raise ValueError(f"計算できない kind: {kind}")


def matches(computed: float, declared, printed: str | None = None) -> bool:
    """書かれた桁で一致するか。

    「17倍」と書いてあるなら、17.14 は 17 に丸めて一致とみなす — 書かれていない桁で
    不一致を主張しない。精度は「書かれた文字列」から取る(浮動小数の表記から取ると、
    17.0 のように勝手に1桁が生まれる)。"""
    text = printed if printed is not None else (declared if isinstance(declared, str) else f"{declared:g}")
    places = len(str(text).split(".")[1]) if "." in str(text) else 0
    value = to_number(declared) if not isinstance(declared, float) else declared
    if value is None:
        return False
    factor = 10 ** places
    got = math.floor(abs(computed) * factor + 0.5) / factor
    return abs(got - abs(round(value, places))) < 1e-9
