#!/usr/bin/env python3
"""検査対象（印刷面）と統制行を、モデルに依存せず構造だけで決める共有モジュール。

なぜラベルで決めてはいけないか（このスキルで最も高くついた失敗）:
  「（参考）アンレバードFCF」はラベルに「参考」を含むが、DCFが参照する唯一の
  FCF行だった。ラベルで検査対象から外していたため、ゼロ化してDCF株式価値が+72%
  動いても総合判定はOKのままだった。**ラベルは名前であって型ではない。**
  同様に、シンク（帰結）を「当期純利益・期末現金」等と列挙すると、列挙し忘れた
  領域（バリュエーション・資本政策・KPI・サマリー）が丸ごと検査対象外になる。

そこで、検査対象は**印刷面**という構造で定義する:

  契約: **印刷範囲に出る導出セルは、すべてエラー級チェックで守られていること。**
        （投資家が読む数字は、壊れたら必ず総合判定が鳴る）

  - 対象 = 印刷範囲内の数式セル（文字列を返す式・統制行・入力シートを除く）
  - 統制行 = サマリーの集約ブロックが読んでいる行（＝チェック行そのもの）と、
             総合判定・警告件数・集約行・ソース照合が読む差異行
  - 入力シート（前提条件）は境界。入力値の誤りはチェックでは原理的に検知できない

この定義はモデル（事業の形）にも、行ラベルの言い回しにも依存しない。
"""
from __future__ import annotations

import re

INPUT_SHEET = "前提条件"
SUMMARY_SHEET = "サマリー"
NOTE_TOKENS = ("免責", "注記")          # 数式を持たない注記行（保険）

_RANGE = re.compile(r"(?:'([^']+)'!)?\$?[A-Z]{1,2}\$?(\d+):\$?[A-Z]{1,2}\$?\d+")
_IFERR = re.compile(r"IFERROR\([A-Z]{1,2}(\d+)")
_ABSREF = re.compile(r"ABS\([A-Z]{1,2}(\d+)\)")


def label_of(ws, r):
    for c in (2, 3, 4):
        v = ws.cell(row=r, column=c).value
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def print_end(ws) -> int:
    """印刷範囲の最終行（チェック明細は印刷範囲外に置かれる）。"""
    pa = str(ws.print_area or "").replace("$", "")
    m = re.search(r":([A-Z]{1,2})(\d+)$", pa)
    return int(m.group(2)) if m else ws.max_row


def control_rows(wb) -> set:
    """統制行（チェック行・集約行・総合判定・照合の差異行）を構造的に特定する。"""
    out = set()
    if SUMMARY_SHEET not in wb.sheetnames:
        return out
    ws = wb[SUMMARY_SHEET]
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if not isinstance(v, str) or not v.startswith("="):
                continue
            for sh, r in _RANGE.findall(v):        # 集約が読むチェック行
                out.add((sh or SUMMARY_SHEET, int(r)))
            if "SUMPRODUCT(--(ABS(" in v or "IFERROR(" in v:
                out.add((SUMMARY_SHEET, c.row))    # 集約行・総合判定そのもの
            for r in _IFERR.findall(v):            # 総合判定が直接読む行
                out.add((SUMMARY_SHEET, int(r)))
            for r in _ABSREF.findall(v):           # ソース照合が読む差異行
                out.add((SUMMARY_SHEET, int(r)))
    return out


def _split_args(s: str):
    """深さ0のカンマで引数を分割する。"""
    out, depth, cur, inq = [], 0, "", False
    for ch in s:
        if ch == '"':
            inq = not inq
        if not inq:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                out.append(cur)
                cur = ""
                continue
        cur += ch
    out.append(cur)
    return out


def _always_text(formula: str) -> bool:
    """その式が「常に文字列を返す」か。数値を返す枝が1つでもあれば False。

    ここを『引用符を含む式は除外』にしていたため、`IF(x=0,"—",数値)` の行が
    動的・静的の両ゲートから丸ごと消え、KPIの効率指標3行（営業効率・顧客獲得単価・
    資金燃焼倍率）が無検査のまま出荷された（3ジャッジ全員が実証）。
    **型は式の分岐であって、引用符の有無ではない。**

    判定: 先頭が IF(...) なら、返り値の2枝がどちらも文字列リテラルのときだけ文字列行。
    それ以外は「数値を返しうる」とみなして検査対象にする（安全側）。
    """
    f = formula.lstrip("=").strip()
    if '"' not in f:
        return False
    if not f.upper().startswith("IF(") or not f.endswith(")"):
        # IF以外で引用符を含む式（文字列連結など）は文字列行とみなす
        stripped = re.sub(r'"[^"]*"', "", f)
        return not re.search(r"[A-Z]{1,2}\d+", stripped)
    args = _split_args(f[3:-1])
    if len(args) < 3:
        return False
    branches = [a.strip() for a in args[1:3]]
    return all(b.startswith('"') and b.endswith('"') for b in branches)


def surface_cells(wb, excluded=None):
    """印刷面の導出セル [(sheet, row, col, label)]。これが検査対象の全体。

    **除外は「セル種別」で決める。シート名でも式の型でもない。**
      - 青字の入力セル（境界。入力値の誤りはチェックでは原理的に検知できない）
      - 統制行（チェック行そのもの）
      - 印刷範囲外（監査証跡）
      - **常に文字列を返す式**（「期間内なし」等。算術タイで守れない）

    入力シート（前提条件）を丸ごと除外すると、そこに置いた導出セル
    （ケースの採用値＝CHOOSE行）が検査対象から抜ける（実際に60セルが無検査で
    出荷され、製造原価をゼロ化しても総合判定OKだった）。**シートで除外しない。**

    excluded に list を渡すと、除外したセルを記録する（沈黙の除外を禁じる）。
    """
    ctrl = control_rows(wb)
    out = []
    for ws in wb.worksheets:
        last = print_end(ws)
        for r in range(6, last + 1):
            lab = label_of(ws, r)
            if not lab or any(t in lab for t in NOTE_TOKENS):
                continue
            if (ws.title, r) in ctrl:
                continue
            for c in range(6, 13):
                cell = ws.cell(row=r, column=c)
                v = cell.value
                if not (isinstance(v, str) and v.startswith("=")):
                    continue
                # 文字列行の判定は「式の見た目」ではなく**セルの数値書式**で決める。
                # 数値書式が付いている＝数値を印刷する意図の行。そこに文字列の枝が
                # あっても検査対象から外さない（`IF(x=0,"—",数値)` を除外した結果、
                # KPIの効率指標3行が無検査で出荷された）。
                is_text = ('"' in v and cell.number_format == "General")
                if is_text:
                    if excluded is not None:
                        excluded.append(f"{ws.title}!{r} {lab[:20]}（表示専用）")
                    continue
                out.append((ws.title, r, c, lab))
    return out
