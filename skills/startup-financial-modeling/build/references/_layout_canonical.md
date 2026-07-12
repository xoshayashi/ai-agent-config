# Layout Canonical

## Workbook Style

- Use directly auditable cell references and simple editable grid structures;
  generated investor plans keep each label, section, and value in its own cell.
- Keep assumptions on their own rows with unit and source/note columns.
- Represent hierarchy through dedicated columns, not Excel native indent or
  leading spaces. A is a narrow visual gutter. Every hierarchy / indentation
  column starts at B and must render as exactly 20px wide in Google Sheets.
  In xlsx / openpyxl terms that is exactly column width `2.14`, not `20.0`
  and not "about 2.14" — generated workbooks pin this via
  `ib.INDENT_COL_WIDTH` and `ib.apply_indent_column_widths`, audited by
  `ib.audit_indent_column_widths`. This rule applies to every sheet without
  exception, including non-period table sheets such as Guide, Driver Tree,
  Exit Waterfall, and Benchmarks: data tables in those sheets start at the
  first non-indent column (C in the default 1-deep hierarchy), not at B.
  Section or hierarchy text may live in B only when the cells to the right are
  intentionally blank so the text can overflow visibly in Google Sheets. If a
  model needs deeper hierarchy, add more 2.14-wide hierarchy columns
  to the right, then leave the overflow cells blank or place the lowest-level
  line item in the first wide label column. Source / driver, unit, and value
  columns follow that label column.
- The default generated period layout is A gutter, B 20px hierarchy / indent
  marker, C line item or section text, D source / driver, E unit, and F onward
  for periods or values, followed immediately by one terminal `Comment` column.
  Custom matrices and scenario tables must derive their first data column from
  the same layout object instead of hard-coding C/D/E or E:I ranges.
  Non-period table sheets follow the same indent contract:
  B stays a 2.14-wide spacer (filled only with section labels that overflow
  into deliberately blank cells), and the table itself starts at C.
- Do not freeze rows or columns in generated workbooks. Keep the layout readable
  without relying on pane state.
- Use alignment by meaning: prose, sources, and comments are left-aligned;
  units and numbers are right-aligned; period headers are centered.
- Monetary cells store raw base-currency values. Show `円`, `千円`, `百万円`,
  `$`, `$K`, `$M`, or other selected display scales through Excel number
  formats only. Formulas calculate business logic in raw values, while number
  formats handle presentation scale.
- Unit columns show compact atomic labels. Monetary rows use `円`, `千円`,
  `百万円`, `$`, `$K`, or `$M`; operational rows use units such as `units`,
  `count`, `customers`, `FTE`, `months`, `%`, or `x`.
- The terminal `Comment` column is part of the standard period-sheet contract,
  not an optional overflow scratch area. It carries row-level explanations and
  should be the last populated column in the sheet.
- No-Wrap Rule: generated cells keep `wrap_text` disabled. Do not use wrapped
  text as a layout tool in model sheets. Long labels, sources, and notes either
  fit the role column, use a wider table-specific column, move to a dedicated
  note / interpretation column, or overflow into intentionally empty adjacent
  cells.
- No-Merge Rule: do not merge cells to make titles, section bands, headers,
  notes, or long text look wider. Merged cells make filtering, selection,
  filling, formulas, and Google Sheets editing worse. Use normal cells,
  column widths, fill spans, and truly blank unstyled overflow cells instead.
- Classify text before changing wrap settings. If the cell is a title,
  subtitle, instruction line, explanation, bullet, source caveat, or note row
  and the cells to the right can be left empty, keep wrapping off and let the
  text read horizontally through those blank cells without merging. Use
  wrapping only for user-approved bounded table prose that must stay inside one
  column because adjacent cells carry meaningful values, formulas, units, or
  notes.
- Any proposed `wrap_text=True` change is a design failure unless the user has
  explicitly requested a prose-heavy workbook exception; prefer restructuring
  the grid before considering that exception.
- When a user-approved exception uses wrapped text or manual line breaks,
  adjust the row height deliberately to the rendered line count. A wrapped
  two-line cell should have a two-line row, a three-line cell should have a
  three-line row, and so on; clipped text, auto-height guesses, or oversized
  padded rows are design defects.
- Spacer cells that support text overflow remain truly blank and unstyled;
  formatting appears where it carries table, header, output, or status meaning.
- Empty cells can still be part of the design. When a row is a semantic
  component such as a header/label row, selected output, check, caution, or
  interpretation band, extend the background fill across the same useful
  columns as comparable rows even where some cells have no text. This keeps the
  row visually aligned and intentional; absence of text alone is not a reason
  to stop the fill.
- Filled row components must be rectangular and column-consistent: decide the
  span from the table/block being introduced or evaluated, then fill every cell
  in that span. Avoid ragged fills whose start/end columns change row by row.
- Section headers should usually carry their band across the full width of the
  table they introduce. If the following table spans six columns, the section
  band spans those six useful columns too, even when only the leftmost section
  cell has text.
- Fill span is row-level alignment, not permission to color blocks. Do not stack
  the same background color across consecutive rows except for true heatmaps.
  Keep accent rows selective so each filled row has a clear structural or
  decision meaning.
- Apply the same principle to borders: thin table rules can support ordinary
  grids, but prominent top/bottom borders should appear where structure changes
  or a decision row needs attention. Choose the border span from the data table,
  section, or row component being framed, then draw the rule across that full
  useful width, including blank cells that belong to the component. Do not stop
  a border merely because the next cell is empty; stop it at the edge of the
  related table/block or comparable row span. Avoid repeated heavy rules across
  consecutive rows unless the repetition is the table structure itself.
- Data-table border spans are table-owned, not row-owned. If a table's header
  defines columns B:K, then body row rules, subtotal rules, total/check rules,
  and interpretation rules that belong to that table should share the B:K edge
  even when an individual row has values only in B:F. Only an explicitly nested
  subtable may use a narrower declared border span.
- Dedicated hierarchy / indent columns are not border surfaces. They may carry
  hierarchy spacing, labels, or fills where the design needs a band, but table
  rules start at the row's actual hierarchy-position label/data column. In the
  default generated layout, B is a 20px hierarchy spacer, so table/header/total
  borders start at C unless the row explicitly declares a deeper hierarchy
  column as its label/data start. Do not drag a border through earlier spacer
  columns merely to make the row look wider.
- Border rhythm follows the same non-consecutive accent rule as background
  fills. Do not put the same prominent top/bottom rule on adjacent rows merely
  because nearby rows are important. Pick the structural row, then use font
  weight, spacing, comments, or quiet whitespace for the rows around
  it. Consecutive heavier borders are acceptable only when they are the declared
  mechanism of a real table grid or nested component.
- Borders are not default row gridlines. Most ordinary body rows and memo /
  source / note / interpretation cells should be borderless. Add a rule before
  a row when the row introduces, closes, checks, or materially changes a block;
  do not add a rule simply because a row has values. Avoid any heavy border
  pattern or ragged populated-cell-only rule that makes the workbook busier
  without adding hierarchy.
- Use exactly three border styles by meaning: normal thin for ordinary
  structural breaks, one-step-thicker medium for major section/decision
  boundaries, and normal dotted for softer provisional/supporting separations.
  Treat them like color accents: pick the lightest style that communicates the
  semantic difference. Border colors are black by default; do not use gray or
  colored borders to create extra hierarchy when spacing, typography, and the
  three approved line styles are enough.
- Borderless blank cells are allowed only when they are outside the component:
  trailing canvas, overflow spacer cells for no-wrap text, or unrelated blank
  columns. Blank cells inside a semantic row or data table width receive the
  same border as the row component.
- Evidence status cells in period columns must use compact, controlled labels
  such as `actual`, `contracted`, `pipeline-backed`, `benchmark`,
  `management target`, `estimate`, `placeholder`, or `unknown`; keep longer
  explanations in source / note columns.
- Section headers are unnumbered descriptive labels.
- Use direct cell references in formulas so model logic can be audited without
  hidden aliases.
- Use the workbook font defined in `_ib_workbook_design_system.md`, clear
  section bands, no frozen panes, and readable number formats.

## Layout-Linked Visual Semantics

`_ib_workbook_design_system.md` owns visual roles, colors, borders, highlights,
and rendered appearance. This file only defines the layout implications of
those roles.

- Treat background color as a workbook-level design surface, not as isolated
  single-cell decoration. Generated sheets should keep the base grid quiet and
  concentrate color in recurring structural or semantic roles, such as
  header/label row bands, section typography or rules, selected outputs, checks,
  caution, or status.
- Background fills belong to repeated semantic roles: header/label rows, section
  dividers, total/check rows, selected outputs, caution states, and heatmaps.
- Use a blue-based structural palette inside sheets by default: near-white blue
  header/label rows and navy section labels/rules are a safe default, but other
  accents may be used when their role is explicit and repeated consistently.
  The base grid stays quiet, with structural palette roles repeated
  consistently so important accents stay immediately visible.
- Avoid rainbow palettes, saturated fills, and decorative alternating row bands
  in model tabs. If alternating row shading is useful for a raw data table, keep
  it light, table-scoped, and distinct from semantic accent fills so it does not
  compete with headers, checks, and selected outputs.
- Alignment is semantic: source / memo text is left-aligned gray italic, units
  are right-aligned gray, period headers are centered, numeric values are
  right-aligned, and prose is never centered just because it sits in a table.
- Chart axis titles and sheet-tab colors are part of the design system. Axis
  units must derive from workbook currency / display scale. Tabs should be
  colored by semantic workbook role or block, so adjacent sheet groups can be
  scanned quickly without forcing every tab into the same hue family.
- Charts use one coherent primary unit per axis. Operating units, headcount,
  months, percentages, and money are charted separately or converted into a
  clearly labeled indexed view.

Font colors and highlight colors are owned by `_ib_workbook_design_system.md`.

## Model Design Bar

- The workbook should read like an investor diligence package: compact,
  reviewable, and visibly structured around the decision.
- Use gridlines-off plus explicit light row rules and section/header borders so
  table structure remains visible without default spreadsheet grid noise.
- Include charts where they clarify the plan: revenue mix, cash runway, market
  support, scenario range, or valuation.
- Prefer the smallest complete workbook that supports the decision and includes
  the logic surfaces needed to make the model auditable.
