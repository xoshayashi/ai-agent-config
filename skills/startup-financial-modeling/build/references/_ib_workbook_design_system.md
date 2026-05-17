# IB Workbook Design System

The workbook should look like a clean, reviewable investment-banking model:
quiet grid, clear hierarchy, auditable formulas, and enough room for labels and
notes to be read in Excel and Google Sheets.

## Sheet Rhythm

Every sheet follows the same reading rhythm:

| Zone                | Design intent                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Title area          | Row 2 in the first wide label/text column contains the sheet title; row 3 contains a short gray italic purpose line |
| Header row          | Row 5 anchors metadata columns and period/value columns                                                             |
| Body                | Each row has one role: section, line item, source/note, unit, value, or output                                      |
| Interpretation area | KPI, scenario, sensitivity, valuation, benchmark, and memo sheets include concise judgment rows                     |

The first useful row should be visible without scrolling. The sheet should feel
compact enough for repeated model review, with blank space used as breathing
room rather than as decoration.

## Column System

Use columns to express hierarchy and readability:

| Column role            |                               Width guide | Alignment                                         |
| ---------------------- | ----------------------------------------: | ------------------------------------------------- |
| A gutter               |                                         3 | visual margin                                     |
| Hierarchy columns      | 20px in Google Sheets (`2.14` xlsx width) | left                                              |
| Lowest-level line item |                               54 or wider | left                                              |
| Source / driver        |                               54 or wider | left, gray italic                                 |
| Unit                   |                                        14 | right, gray                                       |
| Period / value         |                                        16 | right for numbers, center only for period headers |
| Notes / interpretation |                                     60-72 | left, gray italic                                 |

Long labels receive enough width in their role column or move to a dedicated
notes / interpretation column. Adjacent cells that support text overflow remain
plain empty cells, so Google Sheets can show the full text.

## Text Position And Alignment

Investment-banking model alignment is functional, not decorative. A reviewer
should be able to infer the role of a cell from its position before reading the
formula. Keep the alignment system boring and consistent:

- Row labels, section labels, source text, notes, memo text, and interpretation
  text are left-aligned. Text reads from the model spine outward.
- Numeric values, formulas, percentages, multiples, dates used as values,
  counts, and money amounts are right-aligned so magnitudes, decimals, signs,
  dashes, and parentheses scan vertically.
- Unit labels are right-aligned in the unit column immediately before the first
  value column. Units belong visually to the value block, not to the prose
  label.
- Period headers, scenario-case headers, and compact matrix column headers are
  the main centered text. Do not center long prose, line-item labels, source
  caveats, notes, or memo sentences.
- Sheet titles and subtitle/purpose lines are left-aligned in the first wide
  text column. They should read horizontally across blank unmerged overflow
  cells, not sit centered above the grid.
- Vertical alignment is center for normal compact rows. Do not use vertical
  centering to justify tall wrapped rows; fix the row structure or exact row
  height instead.
- Hierarchy is expressed with dedicated hierarchy/indent columns, each 20px in
  Google Sheets (`2.14` xlsx width). Do not use native Excel indent, leading
  spaces, or centered indentation to fake hierarchy.
- Keep column roles stable across sheets. The same role should appear in the
  same horizontal position whenever possible: hierarchy/label/source/unit first,
  then periods/values, then notes/interpretation. This is more important than
  squeezing one sheet into fewer columns.
- Avoid "presentation centering" in model grids. Centering is acceptable for
  short headers over a value block; it is a defect when it makes labels, notes,
  or assumptions harder to audit.

No-Wrap Rule: do not solve readability by turning on cell text wrapping. If
text clips, follow the IB wrap decision ladder below. Generated workbook
helpers should reject `wrap_text=True` instead of silently accepting it. A
wrap/manual-line-break exception is valid only for user-approved bounded table
prose that must stay in one populated table column. When an exception is
approved, row height becomes part of the design contract: set it to the exact
rendered visible line count so the text is neither clipped nor floating inside
excess whitespace. Use the row-height helper in `ib_format.py` rather than
relying on spreadsheet auto-height guesses.

IB wrap decision ladder:

1. Shorten the label, source caveat, note, or memo sentence.
2. Widen the role column if the wider column remains consistent with the sheet.
3. Reserve blank, unstyled overflow cells to the right so horizontal-read text
   can display without wrapping or merging.
4. Move longer prose to a dedicated note / interpretation column, source
   register, memo sheet, or separate lower row.
5. Use a wrapped/manual-line-break exception only for user-approved bounded
   table prose that must remain inside one populated table column because
   adjacent cells carry meaningful values, formulas, units, or notes.

Before allowing any wrap exception, classify the text row:

- Horizontal-read rows keep wrap off. This includes sheet titles, subtitles,
  guide/instruction rows, explanatory notes, bullets, source caveats, and short
  memo lines when adjacent cells to the right can stay empty for overflow. A
  horizontal note is better as one low row that reads across blank unmerged
  cells than as a tall wrapped or merged cell.
- Horizontal-read rows must also have visual runway: do not place them in the
  final print/render column or immediately before a styled/filled/bordered
  overflow blocker. If the text cannot overflow visibly, restructure the row.
- Bounded table prose may use a user-approved wrap exception only when the text
  must remain inside one column because adjacent cells carry related table
  values, formulas, units, or notes. Even then, the row height must match the
  rendered line count exactly.
- Manual line breaks are treated as wrapped exceptions. They need the same
  user approval, `wrap_text=True`, and exact line-count row height.
- If a screenshot shows a tall row created only by wrapping a horizontal-read
  note, repair by turning wrap off, clearing the overflow cells, and widening
  or restructuring the row before considering any wrap exception. Do not use
  merged cells as the repair.

## Workbook Tokens

Use these tokens instead of inventing local formatting:

| Token                    | Value                                  | Use                                                                                         |
| ------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| Base font                | Arial 10pt                             | All body cells and generated default workbook font                                          |
| Comment font             | Arial 9pt italic gray `#666666`        | Sources, notes, explanations, unit helpers                                                  |
| Title font               | Arial 14pt bold                        | Sheet title row                                                                             |
| Section font             | Arial 10-11pt bold                     | Section or block labels                                                                     |
| Input font               | Blue `#0000FF`                         | Typed assumptions and source facts                                                          |
| Formula font             | Black `#000000`                        | Same-sheet formulas and calculated values                                                   |
| Internal link font       | Green `#008000`                        | Cross-sheet formulas                                                                        |
| External link font       | Red `#FF0000`                          | External file / URL references                                                              |
| Header / label row fill  | Light blue `#D9EAF7`                   | A row that names a model block, matrix, register, or period/value area                      |
| Total/check band fill    | Pale blue `#EAF2F8`                    | Totals and reconciliation rows when they need a band                                        |
| Section band fill        | Navy `#1F3A66`                         | Block/section dividers across the attached block width                                      |
| Selected output fill     | Pale yellow `#FFF9C4`                  | One chosen output/check/caution row                                                         |
| Body row height          | 15pt                                   | Normal model rows                                                                           |
| Header row height        | 18pt                                   | Row 5 or compact header/label rows                                                          |
| Section row height       | 20-22pt                                | Section/block divider rows                                                                  |
| Wrapped exception height | 15pt x visible line count              | User-approved wrap/manual-break exceptions only                                             |
| Money formats            | Raw stored values with display formats | `円`, `千円`, `百万円`, `億円`, `$`, `$K`, `$M`; negatives show red and zeros may show dash |
| Percent / multiple       | `%`, `x` formats                       | Percentages right-aligned, multiples as `0.0x` / `0.00x`                                    |

The xlsx default font must also be Arial 10pt so newly inserted rows inherit
the same look after the user opens the workbook.

## Unit And Number-Format Discipline

Financial values keep their arithmetic meaning in the cell value. Do not scale
money by dividing the stored value to make the cell look like thousands,
millions, hundred-millions, billions, or trillions.
Store base-currency values and use Excel display formats for presentation. Use
`number_format` to control display scale, currency symbol, negative-red
presentation, parentheses, and dash-zero treatment. The unit label tells the
reader the displayed scale; the cell value keeps the raw monetary amount.

Examples:

- `320000` yen monthly price stays `320000`; use a yen display format.
- `6000000000` yen revenue stays `6000000000`; use a million-yen display
  format when the sheet unit is `百万円`.
- `$12000000` stays `12000000`; use `$M` or `$K` display formats as needed.

Avoid formulas such as `=Revenue/1000`, `=Revenue/1000000`, or
`=Revenue/1000000000` only to change presentation. The same rule applies when
reading a reference workbook: inspect `number_format`, font color, alignment,
fill, border, wrap, merged cells, and row/column dimensions before concluding
what unit or design system the workbook uses.

This is a money-unit rule, not a blanket numeric rule. Operational quantities
keep their natural units and formats: `units`, `customers`, `count`, `FTE`,
`days`, `months`, `%`, and `x` should not be converted into currency display
formats or have their formulas rewritten for monetary scaling. When a
non-money row legitimately divides by a large number for density, penetration,
or per-unit analysis, preserve that formula and label the unit clearly.

## Font Size Discipline

Investment-banking models should look dense, legible, and standardized. Font
size is a small hierarchy system, not a decorative palette:

- Use Arial 10pt for ordinary body cells, labels, inputs, formulas, values,
  period headers, subtotals, grand totals, and generated default cells. This is
  the modeler's working size and should carry almost all workbook content.
- Use Arial 9pt italic gray for supporting source, note, unit-helper, footnote,
  and interpretation-helper text. Do not use 8pt cell text to squeeze content;
  widen the column, shorten the copy, or move it to a proper note surface.
- Use 10-11pt bold for section labels and compact header rows. Prefer bold,
  sparse fill, or a border to show structure before increasing size.
- Use Arial 14pt bold for sheet titles and cover/title surfaces only. Do not
  use 16pt+ title styles inside model grids; the workbook should not feel like
  a slide deck.
- Keep the generated cell-size set intentionally small: 9, 10, 11, and 14pt.
  Chart axis ticks or non-cell drawing labels may use smaller sizes when the
  chart remains readable, but populated worksheet cells should not.
- Avoid mixing font sizes within a row or table unless the role changes
  materially. A row's meaning should come from role, placement, number format,
  color semantics, and sparse borders/fills, not from local size improvisation.
- If a render looks crowded at 10pt, fix the layout: column width, row count,
  table structure, overflow space, print area, or copy length. Do not shrink
  the model to 8pt or 7pt.

## Color Roles

Color should help a reviewer understand the workbook faster:

| Role                               | Treatment                                                             |
| ---------------------------------- | --------------------------------------------------------------------- |
| Inputs                             | Blue font for typed assumptions and source facts                      |
| Same-sheet formulas                | Black font                                                            |
| Cross-sheet formulas               | Green font                                                            |
| External links                     | Red font                                                              |
| Sources / notes / units            | Gray, with sources and notes in italic                                |
| Header / label rows                | Light blue fill with dark text                                        |
| Section labels                     | Navy band across the attached table/block width, compact and repeated |
| Totals / checks / selected outputs | Pale blue or pale yellow fill on the selected semantic row            |
| Caution / placeholder              | Pale yellow for a small number of decision-critical cells             |

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
- Keep fills finance-model calm: light blue/near-white for table headers,
  navy for section anchors, pale yellow for a single selected output or caution,
  and white for ordinary calculation rows. Avoid rainbow palettes, saturated
  backgrounds, decorative alternating row fills, and one-off colors that do not
  map to a repeated workbook role.
- Input emphasis should primarily come from blue font and, only when useful, a
  very light input-section fill. Do not shade every editable cell if it creates
  a block of color that overwhelms formulas or outputs.

Generated xlsx builders should use the semantic row-span helper in
`ib_format.py` for fill/border row components. Hand-painting isolated cells is
a smell unless the row has a documented table/block span.

## Borders And Spacing

Use borders as sparse structural accents:

- Borders are sparse accents, not row gridlines. Do not draw a bottom rule on
  every body row; that creates visual noise. Ordinary rows can stay borderless
  and rely on alignment, spacing, and typography.
- Memo, source, note, and interpretation cells are usually borderless. They are
  explanatory surfaces, not table boundaries.
- Subtotals use a single normal thin top border and bold text.
- Grand totals and key checks use a normal thin top border plus the one-step
  thicker medium bottom border only when the stronger rule has real
  check/closing meaning.
- Section starts use a compact navy label or rule.
- Border spans are semantic row components, exactly like fill spans. Decide the
  start and end columns from the attached table, matrix, interpretation block,
  or comparable row width; then draw the rule across that full span, including
  blank cells inside the component. A blank cell inside the table/header/check
  width still receives the border so the reviewer sees one clean vertical edge.
- Hierarchy / indent columns are intentionally quiet. Fills may include a
  hierarchy column when it is part of the visual band, but borders begin at the
  row's real label/data start column. In the default layout that means B stays
  borderless and row rules begin at C; deeper layouts start the rule at the
  actual hierarchy-position column, not across earlier spacer columns.
- Do not draw borders cell-by-cell around only populated cells. Ragged borders
  whose right edge changes row by row are defects unless they mark an explicitly
  smaller nested table. A table that spans B:K should have header, body,
  subtotal, total, and check rules aligned to B:K.
- Keep trailing canvas, overflow spacer cells, and unrelated blank columns
  borderless. The rule is "complete the component span", not "decorate empty
  worksheet space".
- Prominent borders follow the same meaning-first rule as fills. They should
  mark real structure: table starts, subtotals, grand totals, checks,
  interpretation bands, or a deliberately repeated table grid. Avoid stacking
  the same heavy top/bottom rule across many consecutive rows because it turns
  hierarchy into noise.
- The same prominent border should not repeat on adjacent rows by default. If
  two consecutive rows feel meaningful, border the row that carries the main
  structural meaning and let typography, spacing, a comment, or whitespace
  support the other row. Consecutive heavy borders need an explicit table
  grid or nested-component reason.
- Use three border styles by meaning, similar to how background-color intensity
  is chosen by role: normal thin for ordinary structural breaks, one-step
  thicker medium for major section or decision boundaries, and normal dotted for
  soft/provisional separations such as optional checks, scenario support, or
  secondary context. Avoid extra weights unless the user supplies a house style.
- Border color is black by default across thin, medium, and dotted rules.
  This follows finance-model convention: structure should be readable and
  consistent, while emphasis comes from where the rule appears and which of the
  three weights it uses. Avoid gray, blue, red, or decorative border colors
  unless a user-provided house style explicitly requires them.
- Prefer top borders for calculation/summation rows when the row summarizes the
  numbers above; use a bottom medium rule only for a true closing total or key
  check. Use outside/box borders sparingly for matrices or callout blocks, not
  as a default around every row.
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
