"""Shared text/color primitives for the deck scripts.

ja_len / HW / hw / token_rgb / header_slots は build_deck・validate_spec・lint_render・
contact_sheet で共有する単一実装。複製すると validate⇔build の字数判定や lint の readback
照合が片側の変更で黙って乖離するため、ここ以外に実装を持たないこと。
"""
import json
import math
import sys
from pathlib import Path

TOKENS_PATH = Path(__file__).resolve().parent.parent / "references" / "tokens.json"


def load_tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text())


def ja_len(s: str) -> float:
    """Approximate display length: full-width chars count 1, half-width 0.55."""
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in s or "")


def one_line_chars(width_in: float, size_pt: float) -> float:
    """1行に収まる字数(全角相当) = 描画ボックス幅 ÷ 字送り(pt/72)。

    見出しの字数上限をトークンへ直書きせず、ここで幾何から導出する。型スケールや
    レイアウト幅を変えれば上限も自動で追従し、validate の判定と build の折返し推定が
    同じ式を共有する(片側だけ古い定数を持つ事故が起きない)。"""
    return width_in / (size_pt / 72.0)


def _box_width_in(box: str, tokens: dict) -> float:
    """ヘッダー契約が参照する描画ボックスの実効幅。名前で引ける3種だけを持ち、
    レンダラ(build_deck)と検証(validate_spec)が同じ幅を見るようにする。"""
    lay, slide = tokens["layout"], tokens["slide"]
    if box == "header":
        return lay["header"]["title_w_in"]
    if box == "content":
        return slide["width_in"] - 2 * lay["margin_x_in"]
    if box == "divider":
        d = lay["divider"]
        return d["panel_x_in"] - lay["margin_x_in"] - d["text_gap_in"]
    raise KeyError(f"unknown header box '{box}'")


def header_slots(pattern: str, tokens: dict | None = None) -> list[dict]:
    """パターンのヘッダー契約(見出しスロット)を解決して返す。

    契約は tokens.json の `header_contract` に宣言する。`default` が全パターンに効き、
    描画のしかたが本当に違うパターン(cover / section_divider)だけが上書きする —
    パターンを増やしても既定の契約(タイトル+サブタイトル、各1行)が自動で適用される。

    返す各スロット: {slot, field, type, lines, width_in, size_pt, max_chars}
      field    : deck.json 上のキー名(章扉の副題は 'desc' のように別名になる)
      lines    : そのスロットが占めるべき行数(cover の副題だけ 2)
      max_chars: 1行あたりの上限字数(全角相当) — 幾何から導出した実測容量
    """
    tokens = tokens or load_tokens()
    contract = tokens["header_contract"]
    spec = {**contract["default"], **contract.get(pattern, {})}
    slots = []
    for slot, cfg in spec.items():
        if slot.startswith("$"):
            continue
        width_in = _box_width_in(cfg["box"], tokens)
        size_pt = tokens["type_scale_pt"][cfg["type"]]
        slots.append({
            "slot": slot,
            "field": cfg.get("field", slot),
            "type": cfg["type"],
            "lines": cfg.get("lines", 1),
            "width_in": width_in,
            "size_pt": size_pt,
            # 切り捨て: 端数を許すと「上限ちょうど」の見出しが実描画で折り返しうる
            "max_chars": math.floor(one_line_chars(width_in, size_pt)),
        })
    return slots


# Full-width alnum/% → half-width. Applied to every rendered string so spec
# sloppiness cannot leak mixed-width digits into the deliverable (執筆規律).
HW = {c: c - 0xFEE0 for c in [*range(0xFF10, 0xFF1A), *range(0xFF21, 0xFF3B),
                              *range(0xFF41, 0xFF5B), 0xFF05, 0xFF0D]}


def hw(s):
    return s.translate(HW) if isinstance(s, str) else s


_token_warned = False


def token_rgb(key: str, fallback: tuple) -> tuple:
    """tokens.json の色を (r, g, b) で返す。読めないときは fallback に退避するが、
    黙って退避すると lint の基準色ずれに気づけないため一度だけ警告を出す。"""
    global _token_warned
    try:
        tokens = json.loads((Path(__file__).resolve().parent.parent
                             / "references" / "tokens.json").read_text())
        return tuple(int(tokens["colors"][key][i:i + 2], 16) for i in (0, 2, 4))
    except Exception as e:
        if not _token_warned:
            print(f"WARN: tokens.json unreadable for color '{key}' ({e}); "
                  "falling back to hardcoded colors", file=sys.stderr)
            _token_warned = True
        return fallback
