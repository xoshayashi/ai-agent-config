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

- Open or render the workbook when practical.
- Verify that the workbook renders with readable columns, visible overflow
  where intended, compact row rhythm, semantic fills, no frozen panes,
  source / unit alignment, and calm accent usage.
- Inspect the print/render canvas: each sheet should end at the last real value
  row and column, including chart and drawing anchors, with print area bound to
  that rendered range and no styled blank rows or columns extending the visual
  surface.
- Review borders and background fills as a system. Row rules should support
  scanning, section and total borders should create hierarchy, and fills should
  sit on repeated semantic roles rather than isolated or noisy cells.
- Confirm generated plans use simple editable grids, direct formulas, raw
  base-currency money values, correct unit labels, and consistent font-color
  semantics.

## Closeout

If any test, workbook inspection, render check, or checklist item fails, treat
that finding as work still in progress: fix the concrete failed item, rerun the
same check, and repeat until the check passes or a real blocker is documented.
Do not replace failed verification with a narrative explanation.

In the final response, state what was built, what was verified, and which
assumptions, placeholders, or source gaps remain. Do not present a weak-source
or unrecalculated workbook as fully proven.
