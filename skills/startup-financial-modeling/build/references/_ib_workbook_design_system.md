# IB Workbook Design System

The workbook should look like a clean, reviewable investment-banking model:
quiet grid, clear hierarchy, auditable formulas, and enough room for labels and
notes to be read in Excel and Google Sheets.

## Sheet Rhythm

Every sheet follows the same reading rhythm:

| Zone | Design intent |
|---|---|
| Title area | B2 contains the sheet title; B3 contains a short gray italic purpose line |
| Header row | Row 5 anchors metadata columns and period/value columns |
| Body | Each row has one role: section, line item, source/note, unit, value, or output |
| Interpretation area | KPI, scenario, sensitivity, valuation, benchmark, and memo sheets include concise judgment rows |

The first useful row should be visible without scrolling. The sheet should feel
compact enough for repeated model review, with blank space used as breathing
room rather than as decoration.

## Column System

Use columns to express hierarchy and readability:

| Column role | Width guide | Alignment |
|---|---:|---|
| A gutter | 3 | visual margin |
| Hierarchy columns | 20 each | left |
| Lowest-level line item | 54 or wider | left |
| Source / driver | 54 or wider | left, gray italic |
| Unit | 14 | right, gray |
| Period / value | 16 | right for numbers, center only for period headers |
| Notes / interpretation | 60-72 | left, gray italic |

Long labels receive enough width in their role column or move to a dedicated
notes / interpretation column. Adjacent cells that support text overflow remain
plain empty cells, so Google Sheets can show the full text.

No-Wrap Rule: do not solve readability by turning on cell text wrapping. If
text clips, widen the relevant role column, split the content into shorter
rows, move commentary to a note / interpretation column, or reserve blank
overflow cells. Generated workbook helpers should reject `wrap_text=True`
instead of silently accepting it.

## Color Roles

Color should help a reviewer understand the workbook faster:

| Role | Treatment |
|---|---|
| Inputs | Blue font for typed assumptions and source facts |
| Same-sheet formulas | Black font |
| Cross-sheet formulas | Green font |
| External links | Red font |
| Sources / notes / units | Gray, with sources and notes in italic |
| Table headers | Light blue fill with dark text |
| Section labels | Navy text or navy rule, compact and repeated |
| Totals / checks / selected outputs | Pale blue or pale yellow fill on the selected populated row only |
| Caution / placeholder | Pale yellow for a small number of decision-critical cells |

The base grid stays white. Filled backgrounds form a coherent row, header,
total, check, or interpretation component. A sheet normally has only a few
highlighted rows, so the important rows are easy to find.

## Borders And Spacing

Use borders as the primary structure:

- Light hairline row rules guide scanning inside tables.
- Subtotals use a single top border and bold text.
- Grand totals and key checks use a top border plus double bottom border.
- Section starts use a compact navy label or rule.
- Row heights stay close to 15-18 points for body rows and 20-22 points for
  section rows.

The result should be dense but calm: enough structure for auditing, without
large blocks of color or oversized empty areas.

## Google Sheets Visibility

Design for the rendered sheet, not only the xlsx file:

- Source, memo, and note text is left-aligned and readable at 100% zoom.
- Unit labels are consistently right-aligned next to values.
- Prose cells are left-aligned, while period headers are the main centered text.
- Empty spacer cells remain truly empty and unstyled, preserving overflow.
- Freeze panes keep row 5 and all metadata columns visible while values scroll.
- The workbook canvas ends at the last rendered row and column on every sheet:
  values, charts, and drawings stay inside the print area, while trailing blank
  rows or columns do not carry fills, borders, or row-height styling.
- Background fills appear on populated headers, sections, selected outputs, and
  checks. Blank cells stay visually quiet, so filled regions feel intentional
  rather than like a colored spreadsheet canvas.

When screenshots show clipped labels, hidden notes, noisy color, or inconsistent
alignment, repair the design system and rerun artifact inspection rather than
treating it as a one-off polish issue.
