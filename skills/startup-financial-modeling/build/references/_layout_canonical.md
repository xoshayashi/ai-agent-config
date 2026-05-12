# Layout Canonical

## Workbook Style

- Use directly auditable cell references and simple editable grid structures;
  generated investor plans keep each label, section, and value in its own cell.
- Keep assumptions on their own rows with unit and source/note columns.
- Represent hierarchy through dedicated columns. A is a narrow visual gutter. B
  is the parent hierarchy column at width 20. If a model needs deeper
  hierarchy, add more width-20 hierarchy columns to the right, then place the
  lowest-level line item in the first wide label column. Source / driver, unit,
  and value columns follow that label column.
- The default generated period layout is A gutter, B section, C line item, D
  source / driver, E unit, and F onward for periods or values. Custom matrices
  and scenario tables must derive their first data column from the same layout
  object instead of hard-coding C/D/E or E:I ranges.
- Freeze panes must preserve every metadata column before the first value
  column. In the default layout, freeze at F6 for period sheets so B-E stay
  visible while scrolling through forecast periods.
- Use alignment by meaning: prose, sources, and comments are left-aligned;
  units and numbers are right-aligned; period headers are centered.
- Monetary cells store raw base-currency values. Show `円`, `千円`, `百万円`,
  `$`, `$K`, `$M`, or other selected display scales through Excel number
  formats only. Formulas calculate business logic in raw values, while number
  formats handle presentation scale.
- Unit columns show compact atomic labels. Monetary rows use `円`, `千円`,
  `百万円`, `$`, `$K`, or `$M`; operational rows use units such as `units`,
  `count`, `customers`, `FTE`, `months`, `%`, or `x`.
- Generated cells keep `wrap_text` disabled. Long labels, sources, and notes
  either fit the role column, use a wider table-specific column, or overflow
  into intentionally empty adjacent cells.
- Spacer cells that support text overflow remain truly blank and unstyled;
  formatting appears where it carries table, header, output, or status meaning.
- Evidence status cells in period columns must use compact, controlled labels
  such as `actual`, `contracted`, `pipeline-backed`, `benchmark`,
  `management target`, `estimate`, `placeholder`, or `unknown`; keep longer
  explanations in source / note columns.
- Section headers are unnumbered descriptive labels.
- Use direct cell references in formulas so model logic can be audited without
  hidden aliases.
- Use compact financial-model typography: Arial or compatible sans, clear
  section bands, frozen panes where useful, and readable number formats.

## Layout-Linked Visual Semantics

`_ib_workbook_design_system.md` owns visual roles, colors, borders, highlights,
and rendered appearance. This file only defines the layout implications of
those roles.

- Treat background color as a workbook-level design surface, not as isolated
  single-cell decoration. Generated sheets should keep the base grid quiet and
  concentrate color in recurring structural or semantic roles, such as
  table-header bands, section typography or rules, selected outputs, checks,
  caution, or status.
- Background fills belong to repeated semantic roles: table headers, section
  dividers, total/check rows, selected outputs, caution states, and heatmaps.
- Use a blue-based structural palette inside sheets by default: near-white blue
  table headers and navy section labels/rules are a safe default, but other
  accents may be used when their role is explicit and repeated consistently.
  The base grid stays quiet, with structural palette roles repeated
  consistently so important accents stay immediately visible.
- Background highlights must be selected from an explicit semantic role
  palette and must not conflict with the workbook's font-color semantics.
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

- Hard-coded input / assumption: blue `#0000FF`.
- Formula: black `#000000`.
- Cross-sheet link: green `#008000`.
- External source or external-link style marker: red `#FF0000`.

The formula-color rule is repeated here only as a layout audit cue; the
canonical visual treatment lives in `_ib_workbook_design_system.md`.

## Model Design Bar

- The workbook should read like an investor diligence package: compact,
  reviewable, and visibly structured around the decision.
- Use gridlines-off plus explicit light row rules and section/header borders so
  table structure remains visible without default spreadsheet grid noise.
- Include charts where they clarify the plan: revenue mix, cash runway, market
  support, scenario range, or valuation.
- Prefer the smallest complete workbook that supports the decision and includes
  the logic surfaces needed to make the model auditable.
