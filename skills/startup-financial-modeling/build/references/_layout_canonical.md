# Layout Canonical

## Workbook Style

- Use directly auditable cell references and simple editable grid structures;
  generated investor plans keep each label, section, and value in its own cell.
- Keep assumptions on their own rows with unit and source/note columns.
- Represent hierarchy through dedicated columns, not Excel native indent or
  leading spaces. A is a narrow visual gutter. Every hierarchy / indentation
  column starts at B and must render as 20px wide in Google Sheets. In xlsx /
  openpyxl terms that is approximately column width `2.14`, not `20.0`.
  Section or hierarchy text may live in B only when the cells to the right are
  intentionally blank so the text can overflow visibly in Google Sheets. If a
  model needs deeper hierarchy, add more Google-Sheets-20px hierarchy columns
  to the right, then leave the overflow cells blank or place the lowest-level
  line item in the first wide label column. Source / driver, unit, and value
  columns follow that label column.
- The default generated period layout is A gutter, B 20px hierarchy / indent
  marker, C line item or section text, D source / driver, E unit, and F onward
  for periods or values. Custom matrices and scenario tables must derive their
  first data column from the same layout object instead of hard-coding C/D/E or
  E:I ranges.
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
- No-Wrap Rule: generated cells keep `wrap_text` disabled. Do not use wrapped
  text as a layout tool in model sheets. Long labels, sources, and notes either
  fit the role column, use a wider table-specific column, move to a dedicated
  note / interpretation column, or overflow into intentionally empty adjacent
  cells.
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
  or a decision row needs attention. Avoid repeated heavy rules across
  consecutive rows unless the repetition is the table structure itself.
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
