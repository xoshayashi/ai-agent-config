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

# 証拠(EXHIBIT): 構造化された図表の中身。ここに出る数値だけが「示された数値」
EXHIBIT_KEYS = {
    "chart", "charts", "table", "kpis", "stages", "items", "phases", "rows", "cells",
    "steps", "groups", "columns", "factors", "players", "diagram", "bars", "current",
    "side", "segments", "metrics", "recap_metrics", "series", "values", "headers",
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
        for k, v in obj.items():
            if k in CONTROL_KEYS:
                continue
            _strings_and_numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings_and_numbers(v, out)
    elif isinstance(obj, (str, int, float)):
        out.append(obj)


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


def exhibit_values(slide: dict) -> list:
    """図表が持つ値(文字列・数値)を平らに集める。"""
    out: list = []
    _walk(slide, EXHIBIT_KEYS, lambda v: _strings_and_numbers(v, out))
    return out


def claim_values(slide: dict) -> list:
    """主張(散文)の文字列を集める。"""
    out: list = []
    _walk(slide, CLAIM_KEYS, lambda v: _strings_and_numbers(v, out))
    return [v for v in out if isinstance(v, str)]


def exhibit_tokens(slide: dict) -> set[str]:
    """その図表が「示している」数値。"""
    values = exhibit_values(slide)
    tokens = material_tokens(values)
    # 図表の裸の数値(chart の values 等)も、単位を付けたトークンとして数える
    unit = slide.get("unit") or (slide.get("chart") or {}).get("unit")
    if unit:
        for v in values:
            n = to_number(v) if not isinstance(v, bool) else None
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
