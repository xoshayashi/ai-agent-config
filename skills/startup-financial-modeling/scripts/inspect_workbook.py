#!/usr/bin/env python3
"""IBフォーマット作法の機械検査。references/ib_format_spec.md の実装契約を検証する。

使い方: python3 inspect_workbook.py <xlsx>
終了コード 0=全パス / 1=違反あり
"""
from __future__ import annotations

import re
import sys

import openpyxl

ALLOWED_FMTS = {
    "General",
    '#,##0,,_);(#,##0,,);"-"_)',
    '#,##0_);(#,##0);"-"_)',
    "0.0%_);(0.0%)",
    '#,##0.0_);(#,##0.0);"-"_)',
    "0.0x_);(0.0x)",
    '0.0"x"_);(0.0"x");"-"_)',
}
VOLATILE = re.compile(r"\b(OFFSET|INDIRECT|NOW|TODAY|RAND|RANDBETWEEN)\s*\(",
                      re.IGNORECASE)
PURE_LINK = re.compile(r"^='[^'!]+'!\$?[A-Z]{1,3}\$?\d+$")
BANNED_HEADERS = ("source", "driver", "ソース列")

BLUE = "FF0000FF"
BLACK = "FF000000"
GREEN = "FF008000"
GRAY = "FF808080"
WHITE = "FFFFFFFF"
NAVY = "FF1F3864"


def color_of(cell):
    f = cell.font
    if f is None or f.color is None or f.color.rgb is None:
        return BLACK
    return str(f.color.rgb)


def main(path):
    wb = openpyxl.load_workbook(path)
    fails = []
    ok = []

    def gate(cond, label, detail=""):
        (ok if cond else fails).append(f"{label}" + (f" — {detail}" if detail and not cond else ""))

    gate(len(wb.sheetnames) <= 10, f"シート数≦10（{len(wb.sheetnames)}）")

    for ws in wb.worksheets:
        t = ws.title
        # A列スペーサー・B列起点
        a_vals = [c.value for row in ws.iter_rows(min_col=1, max_col=1)
                  for c in row if c.value not in (None, "")]
        gate(not a_vals, f"[{t}] A列が空", str(a_vals[:3]))
        gate((ws.column_dimensions["A"].width or 8.43) <= 2,
             f"[{t}] A列幅≦2")
        for ic in ("B", "C"):
            gate((ws.column_dimensions[ic].width or 8.43) <= 2.5,
                 f"[{t}] インデント列{ic}の幅≦2.5")
        indented = [c.coordinate for row in ws.iter_rows() for c in row
                    if c.alignment is not None and c.alignment.indent]
        gate(not indented, f"[{t}] ネイティブインデント不使用", str(indented[:3]))
        row1 = [c.value for row in ws.iter_rows(min_row=1, max_row=1)
                for c in row if c.value not in (None, "")]
        gate(not row1, f"[{t}] 1行目が空", str(row1[:3]))
        gate(ws.cell(row=2, column=2).value not in (None, ""),
             f"[{t}] タイトルがB2")
        # 結合セル・行高・グリッド線
        gate(len(ws.merged_cells.ranges) == 0, f"[{t}] 結合セルなし",
             str(len(ws.merged_cells.ranges)))
        heights = [rd.height for rd in ws.row_dimensions.values()
                   if rd.height is not None]
        gate(not heights, f"[{t}] 行高はデフォルトのまま", str(heights[:3]))
        gate(ws.sheet_view.showGridLines is False, f"[{t}] グリッド線オフ")
        # 禁止ヘッダー（Source/driver列）
        banned = [c.value for row in ws.iter_rows(max_row=8)
                  for c in row if isinstance(c.value, str)
                  and c.value.strip().lower() in BANNED_HEADERS]
        gate(not banned, f"[{t}] Source/driver列なし", str(banned))

        fills = 0
        for row in ws.iter_rows():
            for c in row:
                if c.value is None and (c.fill is None or
                                        c.fill.patternType is None):
                    continue
                # フィルはタイトル帯（1行目ネイビー）のみ
                if c.fill is not None and c.fill.patternType == "solid":
                    fg = str(c.fill.fgColor.rgb)
                    if not (c.row == 2 and fg == NAVY):
                        fills += 1
                if c.value is None:
                    continue
                # フォント統一
                f = c.font
                if f.name != "Arial" or (f.size or 10) != 10:
                    fails.append(f"[{t}]{c.coordinate} フォント Arial10 以外: "
                                 f"{f.name}{f.size}")
                    continue
                # 数値書式ホワイトリスト
                if c.number_format not in ALLOWED_FMTS:
                    fails.append(f"[{t}]{c.coordinate} 書式外: {c.number_format}")
                # カラーコード検査（数値・数式セルのみ。C列以降）
                if c.column >= 5 and c.row > 5:
                    col = color_of(c)
                    if isinstance(c.value, str) and c.value.startswith("="):
                        gate(not VOLATILE.search(c.value),
                             f"[{t}]{c.coordinate} 揮発関数なし", c.value)
                        expect = GREEN if PURE_LINK.match(c.value) else BLACK
                        if col not in (expect,):
                            fails.append(
                                f"[{t}]{c.coordinate} 数式の色: {col} "
                                f"期待{expect} {c.value[:40]}")
                    elif isinstance(c.value, (int, float)):
                        if col != BLUE:
                            fails.append(
                                f"[{t}]{c.coordinate} 入力値が青字でない: {col}")
        gate(fills == 0, f"[{t}] フィルはタイトル帯のみ", f"{fills}件の逸脱")

    print(f"PASS {sum(1 for _ in ok)} 項目")
    if fails:
        print(f"FAIL {len(fails)} 件:")
        for x in fails[:40]:
            print("  -", x)
        return 1
    print("全ゲート通過")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
