# 財務モデル xlsx デザイン — 業界標準調査（C2 成果物）

Phase 1 Task 1.5 で `_layout_canonical.md` / `_ib_workbook_design_system.md` に反映する。

## 一次情報源

- FAST Standard: https://fast-standard.org/the-fast-standard/
- ICAEW Financial Modelling Code (2024): https://www.icaew.com/technical/technology/excel/financial-modelling-code
- IBCS: https://www.ibcs.com/
- CFI Financial Modeling Guidelines: https://corporatefinanceinstitute.com/resources/financial-modeling/free-financial-modeling-guide/
- Macabacus: https://macabacus.com/blog/improving-model-readability-with-color-formatting
- BIWS Excel Formatting Best Practices / Training The Street: https://trainingthestreet.com/fmaamoc-article-2-formatting-a-financial-model/

## Gap 分析サマリ

既存2ファイルは罫線スパン・no-wrap・no-merge・塗り規律・色コードを業界標準と同等以上に明文化済み。
垢抜けなさの主因は規律欠如ではなく以下の欠落:

- **G5（最重要）**: 列幅をコンテンツに連動させる規律の不在。固定値（54/14/16）のみで「あふれたら広げる／
  同役割は横断で統一／フォント縮小・wrap・merge で逃げない」が未定義。
- G1-G3, G10: 数値書式の具体性不足（負数は括弧、ゼロはダッシュ、通貨記号は表の最上段/最下段のみ、
  計算%は斜体、スケジュール内で小数桁統一）。
- G4: 「2列だけが意味を持つ（constants列＋第1期間列）」レビュー契約の未明文化。
- G6: シート順序・計算フロー（Cover→Dashboard→Assumptions→Calc→Statements→Checks、左→右・上→下）。
- G8: 入力セルをフォント色だけで識別している可能性（fill or border も必須）。
- G9: 書式キー（凡例）の同梱。

逸脱（正統選択として根拠明記すべき）: フリーズペイン禁止・ネイティブインデント不使用は、
Google Sheets 互換／スクリーンショット再現性のため正当。ICAEW の「label tree」とも整合。

## 反映する具体ルール文案（既存ドキュメントの voice に合わせたコピペ可能文）

### A. `_layout_canonical.md` `## Workbook Style` — 列幅コンテンツ連動 (G5)

```
- Column width follows content, not a fixed number. The role widths in
  `_ib_workbook_design_system.md` are starting widths, not ceilings. Every
  populated cell in a column must display its full content at the workbook
  font without clipping and without wrapping. If the longest label, source
  note, period value, or unit in a column does not fit at the role's starting
  width, widen the column until it fits. Numeric columns must be wide enough
  that the largest formatted value -- including currency symbol, thousands
  separators, parentheses for negatives, and decimal places -- is fully
  visible. A clipped number, a `#####` cell, or a value that visually touches
  the next column is a design defect, not an acceptable density trade-off.
- Column width is role-consistent across the whole workbook. When content
  forces a column wider than its starting width, apply that same widened
  width to every column of the same role on every sheet. The label column,
  the unit column, and each period/value column keep one width per role
  across all sheets; a model must not have a 16-wide period column on one
  sheet and a 22-wide period column on another. Resolve the width from the
  widest content that role carries anywhere in the workbook, then apply it
  everywhere.
- Never solve a width problem by shrinking the font below the workbook base
  size, by enabling wrap, or by merging. Widen the column, shorten the copy,
  or move long prose to a dedicated note column.
- Period/value columns are equal width to each other within a sheet. All
  period columns in one time ruler render at an identical width so magnitudes
  scan cleanly down and across the grid.
```

### B. `_layout_canonical.md` `## Workbook Style` — 2列レビュー契約 (G4)

```
- Series rows are built with one consistent formula copied across every
  period column. The audit contract is that only two columns carry the
  logic: the constants/driver column and the first period column. A
  reviewer confirms those two cells and trusts the row because the formula
  is identical across the rest of the ruler. Do not break this contract with
  per-period one-off formulas, embedded constants, or interrupting subtotal
  columns inside the time ruler. If the first period legitimately differs
  (a ramp start, an opening balance), keep that the only exception and make
  it visible.
```

### C. `_layout_canonical.md` 新セクション — シート順序と計算フロー (G6)

```
## Sheet Order And Logic Flow

- Sheets are ordered so calculation flows left to right and the reader
  meets the decision first: Cover / contents, Dashboard or selected
  outputs, Assumptions / inputs, Calculation sheets (grouped into
  functional chapters such as revenue, cost, headcount, financing, tax),
  Financial statements (P&L, BS, CF), then Checks. Interpretation, KPI,
  scenario, valuation, and IC-memo sheets sit with the outputs they support.
- Within every sheet, logic flows top to bottom and left to right. A row
  below uses rows above; a column to the right uses columns to the left.
  Counter-flows (an opening balance pulled from a later position) are kept
  to a minimum and visibly marked.
- Inputs, calculations, and outputs are segregated -- on separate sheets or
  in clearly demarcated, separately headed sections on one sheet.
```

### D. `_ib_workbook_design_system.md` `## Color Roles` — 入力セル識別 (G8)

```
- Input cells must be identifiable by more than font color. Typed
  assumptions and source facts use blue font, and decision-critical input
  cells additionally carry a light input fill or a cell border so the cell
  reads as editable even in grayscale, in a screenshot, or to a color-blind
  reviewer. Never rely on a text label alone to mark an input cell. Keep the
  supporting fill light and reserved for true input cells.
```

### E. `_ib_workbook_design_system.md` `## Unit And Number-Format Discipline` — 数値書式 (G1,G2,G3,G10)

```
- Negative numbers display in parentheses, not with a leading minus.
  Use an accounting-style format so positives and negatives align on the
  decimal. Zeros display as a dash, not `0`, in money and count schedules.
- Currency symbols appear only at the top and bottom of each schedule --
  the first line item and the closing total of a statement or block.
  Intermediate rows omit the symbol and rely on the schedule unit label.
- Calculated percentages and ratios are shown in italic so they read as
  derived quantities. Percentage and ratio assumptions that are themselves
  inputs are NOT italicized -- they stay upright in the blue input style.
- Decimal places are uniform within a schedule. Money rows normally show
  zero decimals; per-share and price rows show two. Do not vary decimal
  count row by row.
```

### F. `_ib_workbook_design_system.md` `## Borders` — 合計罫線慣行 (G7)

```
- Follow the accounting underline convention: a subtotal carries a single
  thin top border above the figure; a grand total or closing check carries
  a single thin top border plus a medium bottom border. Prefer a top border
  over a bottom border on any row that sums the numbers above it -- a top
  border survives row insertion into the block without leaving an orphaned
  rule.
```

### G. `_ib_workbook_design_system.md` 新セクション — 書式キーと逸脱の根拠 (G9 + 逸脱明記)

```
## Formatting Key And Documented Deviations

- Every generated workbook includes a compact formatting key explaining the
  color and format system: blue = typed input, black = same-sheet formula,
  green = cross-sheet link, red = external link, italic = calculated
  percentage, light fill / border = input cell, navy band = section,
  pale fill = total/check/selected output.
- This workbook deliberately departs from two common IB-model conventions
  for rendering reasons:
  - No frozen panes. Generated workbooks must render identically in Google
    Sheets and in static screenshots, where pane state is unreliable.
    Readability is carried by stable column widths and repeated headers.
  - No native Excel indent and no "center across selection". Hierarchy is
    expressed only through dedicated hierarchy columns, which reproduce
    faithfully in Google Sheets and rendered images. This matches the ICAEW
    "label tree" recommendation of a separate column per hierarchy layer.
```

## 重点3論点

1. **列幅コンテンツ連動**: 業界総意は「数字が必ず表示される幅」「同役割の列は横断統一」「フォント縮小・
   wrap・merge で逃げない」。本スキル最大の欠落 → ルール A で補強、コード（C1 Task 1.4）で強制。
2. **罫線テーブルブロック単位**: 既存 `_layout_canonical.md` L86-102 は業界文献を上回る精度。gap でなく、
   合計行の「上罫線優先（行挿入耐性）」理由をルール F で補強するのみ。
3. **階層インデント列**: 専用列方式は ICAEW「label tree」の正統解。逸脱でなく正統選択。ルール G で根拠明記。
