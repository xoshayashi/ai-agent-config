# IB Workbook Design System

The workbook should look like a clean, reviewable investment-banking model:
quiet grid, clear hierarchy, auditable formulas, and enough room for labels and
notes to be read in Excel and Google Sheets.

## Sheet Rhythm

Every sheet follows the same reading rhythm:

| Zone | Design intent |
|---|---|
| Title area | Row 2 in the first wide label/text column contains the sheet title; row 3 contains a short gray italic purpose line |
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
| Hierarchy columns | 20px in Google Sheets (`2.14` xlsx width) | left |
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
instead of silently accepting it. If the user explicitly approves a prose-heavy
exception with wrapping or manual line breaks, row height becomes part of the
design contract: set it to the exact number of visible text lines so the text
is neither clipped nor floating inside excess whitespace.
Use the row-height helper in `ib_format.py` rather than relying on spreadsheet
auto-height guesses.

Before allowing any wrap exception, classify the text row:

- Horizontal-read rows keep wrap off. This includes sheet titles, subtitles,
  guide/instruction rows, explanatory notes, bullets, source caveats, and short
  memo lines when adjacent cells to the right can stay empty for overflow. A
  horizontal note is better as one low row that reads across blank unmerged
  cells than as a tall wrapped or merged cell.
- Bounded table prose may use a user-approved wrap exception only when the text
  must remain inside one column because adjacent cells carry related table
  values, formulas, units, or notes. Even then, the row height must match the
  rendered line count exactly.
- If a screenshot shows a tall row created only by wrapping a horizontal-read
  note, repair by turning wrap off, clearing the overflow cells, and widening
  or restructuring the row before considering any wrap exception. Do not use
  merged cells as the repair.

## Workbook Tokens

Use these tokens instead of inventing local formatting:

| Token | Value | Use |
|---|---|---|
| Base font | Arial 10pt | All body cells and generated default workbook font |
| Comment font | Arial 9pt italic gray `#808080` | Sources, notes, explanations, unit helpers |
| Title font | Arial 14pt bold | Sheet title row |
| Section font | Arial 10-11pt bold | Section or block labels |
| Input font | Blue `#0000FF` | Typed assumptions and source facts |
| Formula font | Black `#000000` | Same-sheet formulas and calculated values |
| Internal link font | Green `#008000` | Cross-sheet formulas |
| External link font | Red `#FF0000` | External file / URL references |
| Header / label row fill | Light blue `#D9EAF7` | A row that names a model block, matrix, register, or period/value area |
| Total/check band fill | Pale blue `#EAF2F8` | Totals and reconciliation rows when they need a band |
| Section band fill | Navy `#1F3A66` | Block/section dividers across the attached block width |
| Selected output fill | Pale yellow `#FFF9C4` | One chosen output/check/caution row |
| Body row height | 15pt | Normal model rows |
| Header row height | 18pt | Row 5 or compact header/label rows |
| Section row height | 20-22pt | Section/block divider rows |
| Wrapped exception height | 15pt x visible line count | User-approved wrap/manual-break exceptions only |
| Money formats | Raw stored values with display formats | `円`, `千円`, `百万円`, `億円`, `$`, `$K`, `$M`; negatives show red and zeros may show dash |
| Percent / multiple | `%`, `x` formats | Percentages right-aligned, multiples as `0.0x` / `0.00x` |

The xlsx default font must also be Arial 10pt so newly inserted rows inherit
the same look after the user opens the workbook.

## Color Roles

Color should help a reviewer understand the workbook faster:

| Role | Treatment |
|---|---|
| Inputs | Blue font for typed assumptions and source facts |
| Same-sheet formulas | Black font |
| Cross-sheet formulas | Green font |
| External links | Red font |
| Sources / notes / units | Gray, with sources and notes in italic |
| Header / label rows | Light blue fill with dark text |
| Section labels | Navy band across the attached table/block width, compact and repeated |
| Totals / checks / selected outputs | Pale blue or pale yellow fill on the selected semantic row |
| Caution / placeholder | Pale yellow for a small number of decision-critical cells |

The base grid stays white. Background fills are selective accents for major
semantic moments only: section band, header/label row, selected output/check,
caution/placeholder, or deliberate heatmap. A filled row should feel like an
event in the sheet.

Fill span rules:

- Use one rectangular span per filled row component: same start column, same end
  column, no gaps.
- Choose the end column from the attached table, matrix, interpretation block,
  or comparable row width. Do not choose the end column only from cells that
  happen to contain text.
- Fill blank cells inside that span when they complete the row component. A
  blank cell can belong to the section/header/check band even though it has no
  value.
- Keep trailing canvas, overflow spacer cells outside the component, and
  unrelated blank columns unfilled.
- Section headers inherit the width of the table/block they introduce. If the
  following table spans B:K, the section band spans B:K even when only B has
  the label.
- Header/label rows and selected output/check rows align their fill width to
  the same model block so the reviewer sees a clean vertical edge.
- Do not repeat the same non-heatmap background fill on adjacent rows. If two
  nearby rows feel important, fill the single decision row and use font weight,
  borders, spacing, or comments for the supporting row.
- Do not create decorative color blocks. Several consecutive rows with the same
  fill are acceptable only for true heatmaps or an intentionally defined table
  component with a different visual mechanism.

Generated xlsx builders should use the semantic fill helper in `ib_format.py`
for row components. Hand-painting isolated cells is a smell unless the row has
a documented table/block span.

## Borders And Spacing

Use borders as the primary structure:

- Light hairline row rules guide scanning inside tables.
- Subtotals use a single top border and bold text.
- Grand totals and key checks use a top border plus double bottom border.
- Section starts use a compact navy label or rule.
- Prominent borders follow the same meaning-first rule as fills. They should
  mark real structure: table starts, subtotals, grand totals, checks,
  interpretation bands, or a deliberately repeated table grid. Avoid stacking
  the same heavy top/bottom rule across many consecutive rows because it turns
  hierarchy into noise.
- Avoid repeated filled rows. A filled row should read as an event in the
  sheet, not as continuous wallpaper.
- Row heights stay close to 15-18 points for body rows and 20-22 points for
  section rows.
- Wrapped exception rows are sized by line count rather than by the normal
  compact scale. Match the height to the actual rendered lines and inspect the
  result at 100% zoom.

The result should be dense but calm: enough structure for auditing, without
large blocks of color or oversized empty areas.

## Google Sheets Visibility

Design for the rendered sheet, not only the xlsx file:

- Source, memo, and note text is left-aligned and readable at 100% zoom.
- Unit labels are consistently right-aligned next to values.
- Prose cells are left-aligned, while period headers are the main centered text.
- Empty spacer cells remain truly empty and unstyled, preserving overflow.
- Do not freeze rows or columns; generated workbooks should open without fixed
  panes and remain readable through column widths and repeated header structure.
- The workbook canvas ends at the last rendered row and column on every sheet:
  values, charts, and drawings stay inside the print area, while trailing blank
  rows or columns do not carry fills, borders, or row-height styling.
- Background fills appear on headers, sections, selected outputs, checks, and
  their aligned row spans. Blank cells that complete those row components may
  carry the same fill; trailing canvas and overflow spacer cells outside a
  semantic row stay visually quiet.

When screenshots show clipped labels, hidden notes, noisy color, or inconsistent
alignment, repair the design system and rerun artifact inspection rather than
treating it as a one-off polish issue.
