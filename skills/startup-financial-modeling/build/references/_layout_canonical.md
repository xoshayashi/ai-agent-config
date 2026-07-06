# Layout Canonical

Research basis: FAST Standard 02c (1.01-02/03, 2.01, 2.03), ICAEW Financial
Modelling Code 2018, IB conventions (BIWS/TTS), and Japanese startup planning
practice (smartround / Zaimo / CFO practitioners). See
`_ib_workbook_design_system.md` for visual roles and fonts.

## Column System (one grid, every sheet)

Every generated sheet uses the same column roles and width contract (FAST
1.01-02: consistent column structure even if some sheets leave columns unused):

| Column | Role | Width contract (xlsx chars) |
|---|---|---|
| A | gutter / navigation | 1.5 |
| B | hierarchy / indent marker | 2.14 (renders 20px in Google Sheets) |
| C | line-item label (wide) | starting floor, then content-driven by workbook-wide role max |
| D | source / driver | starting floor, then content-driven by workbook-wide role max |
| E | unit designator | 9 |
| F onward | periods / values — **one uniform width on every sheet** | 11.5 exactly |
| last+1 | notes / interpretation / evidence status | starting floor, then content-driven by workbook-wide role max |

- Hierarchy is expressed through dedicated indent columns (B, exactly `2.14`
  wide — never native Excel indent or leading spaces). Deeper hierarchies add
  more 2.14 columns; tables then start at the first non-indent column.
- Text-role widths follow content, not a fixed local number. Resolve the
  label, source/driver, and notes widths from the widest visible content that
  role carries anywhere in the workbook, clamp to the role's min/max guardrails,
  then apply that one resolved width to every sheet using the role. Do not
  solve clipped labels, sources, or notes with font shrink, wrap, or merge.
- Period-column width is audited across the workbook:
  `len(set(period column widths)) == 1`.
- Non-period register sheets (Cap Table, Guide, Evidence registers) keep the
  same A/B/C spine; table-specific value columns may use declared widths, but
  the table starts at C and column roles stay single-purpose (FAST 2.01-01).

## Header Contract (period-axis sheets)

| Row | Content |
|---|---|
| 2 | C: sheet title (14pt bold). First period column: master-check echo cell (gray, `checks OK` / `CHECK FAILED`) |
| 3 | C: purpose line (gray italic) |
| 4 | C: unit caption `(単位: 百万円)` etc. F→: fiscal-year label ruler (gray, centered) |
| 5 | F→: months-in-period ruler (gray, right-aligned integers: 1 monthly, 12 annual) |
| 6 | C `Line item`, D `Driver`, E `Unit`, F→ period headers (bold, centered, header band) |
| 8→ | data rows |

- **Freeze panes at F7** on every period-axis sheet (ICAEW / FAST / IB
  consensus): labels A–E and header rows 1–6 stay visible. Non-period sheets
  (Guide, Cap Table, IC Memo) may omit panes.
- All per-period formulas reference the months ruler (row 5) for any
  annualization (`=F9*F11*F$5`), so one row formula is copy-identical across
  monthly and annual columns (FAST 3.02-01 row consistency).
- Rows meaningful only within one grain (growth vs prior period) guard with
  the ruler: `=IF(F$5<>E$5,"-",...)` — still copy-consistent.

## Time Axis

- Default full-model axis is **hybrid**: monthly columns for the first two
  fiscal years, then whole-fiscal-year annual columns to five fiscal years
  total (Japanese fundraising standard: 月次24ヶ月+年次3期; smartround).
  Monthly labels are `YYYY/MM`; annual labels are `FY20XX`.
- The fiscal year end month is a model parameter (default March). Every
  annual column is a whole fiscal year (`months_in_period == 12`); audited.
- The monthly/annual boundary is visually declared: a medium vertical rule
  before the first annual column plus the Guide legend entry (ICAEW
  variegated-timeline exception, explicitly documented).
- Focused modes choose their grain from the decision: burn/runway is monthly;
  M&A / DCF / comps are annual. The `--source-md` narrative fallback stays
  annual unless the narrative requests otherwise.
- Summary is the one declared annual-presentation sheet: five fiscal-year
  columns rolled up from engine sheets via SUMIF over the FY-label ruler
  (flows) and INDEX of each fiscal-year-end column (stocks).
- Charts bind to a single-grain range only (the monthly window or an annual
  block) — never across the grain boundary.

## Money, Units, And Display Scale

- Monetary cells always store raw base-currency values. Display scale is
  expressed only through `number_format` (`#,##0,` 千円 / `#,##0,,` 百万円) —
  never by dividing stored values (FAST/ICAEW; JP practice).
- JPY formats use the Japanese triangle-negative convention with dash zero:
  `#,##0,,;[Red]"▲"#,##0,,;"-"`. USD uses paren negatives. Per-cell `¥`
  symbols are not used; the sheet declares its scale in the row-4 caption.
- **Two-tier scale rule:**
  - Statement / engine sheets (P&L, BS, CF, Revenue, Cost, People, Summary):
    one scale per sheet, chosen from the sheet's dominant magnitude and
    declared in the caption. Only per-unit / per-customer / ratio rows are
    exempt and carry their own unit (`円`, `%`) in column E.
  - Register sheets (Assumptions, Evidence, Financing, Cap Table): per-row
    scale, caption reads `(単位: 単位列参照)`.
  - Scale selection is deterministic (magnitude thresholds with hysteresis);
    the unit label in column E must always match the applied number format
    (audited).
- The JPY scale ladder is 円 → 千円 → 百万円 → 十億円 (億円 is not
  expressible with comma scaling and is not used).
- Non-money units keep their own formats: `%` = `0.0%` (italic), multiples =
  `0.0x`, factors 4dp, months 1dp, `units` / `customers` / `FTE` / `count`
  integer. Every line item carries a unit designator in column E.

## Formula Discipline

- Direct cell references only — no defined names, OFFSET/INDIRECT, array
  formulas, or merged cells.
- No hardcoded constants inside formulas except {0, 1, -1, 2, 3, 12, 24, 100,
  365, 1000-scale}; every other number is an input cell (ICAEW #14).
- Row formulas are copy-identical across all period columns (audited via
  R1C1 comparison).
- No circular references; iterative calculation stays off. Interest uses
  beginning-of-period balances (noted on the sheet).
- Declared sign convention: P&L carries costs as positive values (Japanese
  statement convention, subtraction in subtotal formulas); CF shows inflows
  positive / outflows negative. The convention is stated in the Guide
  formatting key and never mixed.

## Text, Wrap, And Merge Rules

- No merged cells, ever. No wrapped text in generated cells; long labels
  shorten, widen their role column, overflow into intentionally blank cells,
  or move to the notes column (wrap exceptions require explicit user
  approval and exact line-count row heights).
- Alignment is semantic: labels/sources/notes left; numbers/units right;
  period and case headers centered. Prose is never centered.
- Spacer/overflow cells stay truly blank and unstyled. Semantic row
  components (header bands, checks, section rules) fill/border their full
  rectangular block span, including blank member cells; see
  `_ib_workbook_design_system.md` for fill/border discipline.
- When one worksheet row contains two side-by-side semantic tables, block
  detection must choose the table used by the target row rather than fusing the
  left table, gutter, and right table into one min/max span. Legitimate internal
  source/unit gaps inside a table remain part of that table's span.

## Checks Architecture (ICAEW #18–20)

- Every statement / engine sheet carries at least one check row where an
  error would change the decision (balance check, cash tie, sources = uses,
  ownership = 100%, revenue bridge), formatted OK/ERROR with a rounding
  tolerance.
- Summary carries the consolidated checks block and a single master check.
  When the bundle includes Summary, every other period-axis sheet echoes that
  master check in its frozen header. Focused bundles without a Summary (e.g.
  `dcf_only`, `ma_exit`) have no consolidated master check to echo; each of
  their sheets still carries its own decision-relevant check row.

## Model Design Bar

- The workbook reads like a decision document: Summary answers the first
  five minutes of investor questions without opening engine tabs.
- Include a sheet only if it owns a distinct decision surface (target 6–10
  core tabs; hard cap 12 without an explicit flag).
- Gridlines off; light, sparse structural rules; charts only where they
  clarify (revenue ramp, cash runway), placed after the data block, bound to
  a single grain.
