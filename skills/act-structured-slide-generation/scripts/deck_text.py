"""Shared text/color primitives for the deck scripts.

ja_len / HW / hw / token_rgb は build_deck・validate_spec・lint_render・contact_sheet で
共有する単一実装。複製すると validate⇔build の字数判定や lint の readback 照合が
片側の変更で黙って乖離するため、ここ以外に実装を持たないこと。
"""
import json
import sys
from pathlib import Path


def ja_len(s: str) -> float:
    """Approximate display length: full-width chars count 1, half-width 0.55."""
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in s or "")


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
