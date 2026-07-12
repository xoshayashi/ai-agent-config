# Excel Generation Architecture

This skill generates editable investor workbooks, not static reports. The
architecture therefore optimizes for traceable formulas, deterministic styling,
post-generation inspection, and future sheet composition.

## Library Boundary

Use `openpyxl` as the canonical workbook engine.

Rationale:

- The skill must create `.xlsx` files and then reopen them for structural,
  formula, style, row/column, data-validation, chart, and workbook-default-font
  inspection.
- `openpyxl` supports both write and read/modify flows, which lets the same
  runtime build the workbook and audit the saved artifact.
- `XlsxWriter` is strong for write-only, richly formatted report generation,
  but it cannot read back or modify workbooks. It is therefore not the primary
  engine for this skill. Consider it only for a future isolated exporter where
  the output is write-only and the audit still reopens the result with
  `openpyxl`.
- Avoid COM automation, `xlwings`, or live Excel dependencies in the core
  builder. They are hard to run in headless agent environments and weaken
  deterministic testing.
- Avoid pandas as the workbook composition layer. DataFrames are useful for
  tabular data preparation, but model sheets need cell-level formulas, formats,
  comments, widths, row semantics, and sparse design spans.

`scripts/requirements.txt` should stay minimal unless a new dependency is
needed by the deterministic builder or verifier. Any dependency added for
research, API retrieval, or optional enrichment should degrade gracefully when
unavailable.

## Layering Contract

The builder has three layers:

1. Economic inference layer: source extraction, business-mechanics scoring,
   assumption defaults, driver decomposition, forecast primitives, and economic
   coherence checks. This belongs in `economic_kernel.py`.
2. Workbook composition layer: sheet bundles, dependency closure, row
   selection, formulas, charts, and sheet-specific calculation surfaces. This
   belongs in `source_plan_builder.py`, `cap_table_builder.py`, and
   `build_model.py`.
3. Presentation and audit layer: fonts, colors, borders, alignment, widths,
   validations, formula color semantics, blank-cell cleanup, rendered bounds,
   and invariant checks. This belongs in `ib_format.py`, `audit_workbook`, and
   `scripts/quality_gate.py`.

Do not move business-mechanic inference into a layout helper. Do not let sheet
renderers invent local colors, font sizes, number formats, column widths, or
wrap behavior outside the design system.

## Intermediate Representation

The flexible unit of design is not a hard-coded worksheet template. It is a
small set of structured contracts that renderers consume:

- `WorkbookSpec`, `SheetSpec`, `RowSpec`, `CellSpec`, `FormulaExpr`, and
  `StyleRole`: typed workbook IR for new or refactored sheet surfaces.
- `SourceFacts`: normalized company, currency, period, driver, financing,
  ownership, benchmark, and evidence inputs.
- `LayoutSpec`: canonical column roles and widths.
- `SOURCE_PLAN_SHEETS`, `MODE_BUNDLE_SEEDS`, and `SHEET_DEPENDENCIES`: visible
  workbook composition and dependency closure.
- Row builders such as `_label`, `_write_values`, `_section`, `_note`, and the
  cap-table state-machine helpers: spreadsheet rendering primitives.
- `ib_format` semantic helpers: the only allowed low-level style surface.

When adding a new sheet or model mode, first express the economic surface in
the kernel / facts / dependencies, then render it through the existing layout
and style primitives. A new direct cell-writing helper is acceptable only when
it represents a reusable workbook role that the existing primitives cannot
cover.

## Formula Discipline

Use live Excel formulas for dependent model logic so a finance reviewer can
trace the calculation in the workbook. Use direct references rather than hidden
defined names. Keep formulas simple, row-consistent, and copyable across
periods where possible.

Generated formulas must not use volatile functions such as `OFFSET`,
`INDIRECT`, `RAND`, `RANDBETWEEN`, `NOW`, `TODAY`, `CELL`, or `INFO`. They make
calculation less predictable and are usually unnecessary in a generated model.
If a date or scenario selector is needed, use an explicit input cell and direct
references.

The strict audit should reopen the saved workbook and block:

- omitted-sheet references;
- `#REF!`;
- hidden defined names;
- wrap / merge / freeze-pane regressions;
- non-canonical font, width, color, alignment, border, and comment-column
  behavior;
- volatile formula functions.

When available, use a spreadsheet engine such as LibreOffice only as an
additional recalc check. It supplements but does not replace formula-string,
style, and economic-coherence audits.

## Extension Rules

- Prefer adding one typed primitive or role helper over scattering local cell
  writes across sheet functions.
- Keep workbook defaults deterministic; do not depend on a user's Excel
  preferences.
- Keep focused modes dependency-complete. If a sheet is omitted, neutralize
  only references that were intentionally outside the compact bundle and leave
  a terminal `Comment` explanation.
- New output modes must add deterministic tests, strict-audit coverage, and a
  rubric or architecture-gate check when they change the generation substrate.
