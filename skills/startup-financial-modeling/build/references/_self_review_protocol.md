# Self Review Protocol

Completion means the workbook or finance artifact has been inspected against
the decision it is supposed to support. This is a checklist, not a scorecard or
heavy process.

## Fit To Request

- Does the artifact answer the user's decision?
- Is the model grain, currency, horizon, entity scope, and source boundary
  explicit?
- Is the artifact the smallest complete output for the task, with dependency
  closure where formulas need upstream/downstream sheets?
- Are irrelevant metrics or sheets omitted, or clearly labeled as placeholders?

## Model Logic

- Are source facts, selected assumptions, explanatory drivers, checks, and
  decision outputs separated?
- Are material assumptions triangulated with implied values and support ratios?
- Do weak-evidence drivers flow into scenario, sensitivity, benchmarks, or DD
  questions?
- Are dependent outputs calculated from primitive drivers rather than assumed
  independently?
- Do balance, cash, ownership, valuation, and return logic reconcile?

## Analysis Depth

- Does KPI selection match the business mechanics and decision?
- Are scenarios coherent cases rather than unrelated scalar shocks?
- Are sensitivity axes chosen from material uncertainty and decision impact?
- Does valuation state method credibility, exclusions, scenario range, and
  investor/founder return?
- Does the memo explain implications rather than only restating tabs?

## Source and Benchmark Hygiene

- Are true sources separated from estimates, management targets, placeholders,
  and unknowns?
- Are benchmark sources fresh enough for the decision or marked as needing
  refresh?
- Are fake source labels avoided?
- Are source gaps carried into DD questions or validation tests?

## Visual and Editability Inspection

- Model generation is not the finish line. Closeout requires two independent
  verification surfaces: command-based workbook checks and rendered-output
  inspection. Apply both to the finance model itself and to sheet design.
- For generated or repaired xlsx files, always run an inspection pass before
  closeout. At minimum, inspect the workbook with openpyxl/XML checks for
  widths, fonts, wraps, merged cells, frozen panes, row heights, blank-cell
  styles, semantic fill spans, print areas, chart anchors, and number formats.
  When LibreOffice/PDF/screenshot rendering is available, render and inspect
  the visible output. Use an actual Google Sheets import/readback when the
  handoff target is Google Sheets.
- Verify that the workbook renders with readable columns, visible overflow
  where intended, compact row rhythm, semantic fills, no frozen panes,
  source / unit alignment, and calm accent usage.
- Confirm workbook default font and populated cell fonts use the canonical
  design tokens: Arial 10pt body/default, 9pt italic gray notes, 14pt title,
  and compact bold section/header rows.
- Confirm hierarchy / indentation uses dedicated Google-Sheets-20px columns
  (`2.14` xlsx width), with no native Excel indent, no leading-space
  indentation, and no wrapped generated cells.
- If a user-approved exception uses wrapping or manual line breaks, verify the
  row height is sized to the exact visible line count and the rendered text is
  neither clipped nor padded into a loose-looking row.
- Inspect the print/render canvas: each sheet should end at the last real value
  row and column, including chart and drawing anchors, with print area bound to
  that rendered range and no styled blank rows or columns extending the visual
  surface.
- Review borders and background fills as a system. Row rules should support
  scanning, section and total borders should create hierarchy, and fills should
  sit on repeated semantic roles rather than isolated or noisy cells.
- Check fill span positively: semantic rows such as headers, selected outputs,
  checks, caution, and interpretation bands may include filled blank cells to
  match the column width of related rows. Treat that as good alignment when it
  is role-based and bounded; only trailing canvas or unrelated blank fills are
  defects.
- For every filled row, name its role and inspect the start column, end column,
  and adjacent rows. The fill should be one rectangular span aligned to the
  related table/block, not a ragged set of populated cells.
- For section headers, verify the band width matches the attached table or
  block width, not merely the one cell containing the section label.
- Check color sparsity. The same non-heatmap background color should not appear
  across consecutive rows as a decorative block. Filled rows should mark major
  semantic moments, with borders and typography carrying the quieter rows.
- Check border sparsity with the same eye. Prominent rules should mark table
  starts, totals, checks, section changes, and interpretation rows; repeated
  heavy rules across consecutive rows should have an explicit structural reason.
- Confirm generated plans use simple editable grids, direct formulas, raw
  base-currency money values, correct unit labels, and consistent font-color
  semantics.

## Command Checks

- Run the narrowest available command checks that prove model quality:
  formula/link integrity, reconciliations, balance/cash/ownership checks,
  unit and display-scale consistency, source/benchmark hygiene, no workbook
  names unless explicitly required, and mode-specific dependency closure.
- Run the workbook-design checks that prove visible sheet quality:
  canonical fonts, no wrap/freeze/merge/native indent, Google-Sheets-20px
  hierarchy columns, row heights, semantic fill spans, sparse colors/borders,
  blank-cell style cleanup, print areas, chart anchors, and rendered bounds.
- Treat command output and rendered screenshots/PDFs as complementary evidence.
  Passing commands do not excuse a visibly poor sheet; a good-looking render
  does not excuse broken formulas, units, sources, or reconciliations.

## Closeout

If any test, command check, workbook inspection, render check, or checklist
item fails, treat that finding as work still in progress: fix the concrete
failed item, rerun the same check, and repeat until both the model logic and
the visible sheet design pass or a real blocker is documented. Do not replace
failed verification with a narrative explanation.

In the final response, state what was built, what was verified, and which
assumptions, placeholders, or source gaps remain. Do not present a weak-source
or unrecalculated workbook as fully proven.
