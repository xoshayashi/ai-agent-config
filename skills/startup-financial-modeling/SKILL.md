---
name: startup-financial-modeling
description: "Use when the user needs startup-finance xlsx work: financial plans, cap tables, valuation, pricing, runway, unit economics, M&A exit, or IC memo support."
---

# Startup Financial Modeling

Build startup finance outputs from economic primitives. First define the
decision, model grain, currency, fiscal year, time horizon, entities, and source
boundary. Separate facts, estimates, assumptions, and unknowns.

References live in `build/references/`; load the smallest set that covers the
decision. Start with `_output_modes.md`, `_generic_composition_protocol.md`,
and `_self_review_protocol.md`. For any xlsx generation or repair, also load
`_layout_canonical.md`, `_ib_workbook_design_system.md`, and
`_sheet_quality_rubric.md`. Add `_modeling_kernel.md`,
`_coverage_universe.md`, `_assumption_decomposition_patterns.md`,
`_kpi_analytics.md`, `_scenario_sensitivity_playbook.md`,
`_valuation_and_return_logic.md`, `_ic_memo_depth.md`,
`_benchmark_protocol.md`, `_terminology.md` for full plans, fundraising, DD,
or investor outputs.

Core pattern: compose from decision and dependencies; examples, maturity cues,
sectors, and modes are prompts for reasoning, not templates. Build the driver
tree, select material variables, keep primitive drivers as assumptions, and
calculate dependent outputs as formulas or checks.

Workbook helper:

```sh
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --source-md path/to/source.md --output model_output.xlsx
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --mode pricing --input model.yaml --output model_output.xlsx
```

Structured YAML may define company/currency/display scale/grain/periods,
segments, operating drivers, financing instruments, and valuation scalars.
Money inputs are raw base-currency values; `_yen` names are money-driver names.

Workbook gates: blue inputs, black formulas, green internal links, red external
links, raw money values with display formats, compact unit labels, direct
formulas, editable grid structure, unnumbered sections, traceable sources, no
merged cells, Google-Sheets-20px hierarchy / indent columns (`2.14` xlsx
width), no native indent or leading-space indentation, no frozen panes, and
generated cells with `wrap_text` off. Treat text wrapping as prohibited for
generated workbook cells; fix long text with column width, table structure, or
blank overflow space instead of enabling `wrap_text=True`. Before accepting
any wrap exception, classify the cell's role and the right-side space:
titles, explanatory lines, instructions, notes, bullets, and source caveats
with empty cells to the right should keep wrapping off and read horizontally
through blank overflow cells without merging cells. Reserve wrapping only for
user-approved prose or table cells that must stay inside a bounded column
because adjacent cells carry meaningful values, formulas, units, or notes. If
such an exception uses wrapping or manual line breaks, row height must be set
to the exact visible line count so no text is clipped and the row still looks
intentional.

Design gates: `_layout_canonical.md` owns grid, columns, hierarchy widths, units,
formulas, and layout mechanics. `_ib_workbook_design_system.md` owns visual
roles, font, color, borders, highlights, charts, and render expectations.
Color discipline is a hard workbook gate, not a polish preference: background
fills are selective accents for major semantic moments only, filled row
components use one consistent rectangular column span, and that span is chosen
from the attached table/block rather than from which cells contain text. Do not
stop a fill because a cell is blank; do not repeat the same non-heatmap fill on
adjacent rows; do not color several rows merely because they are nearby.
Section/block dividers, header/label rows, selected outputs/checks, input
sections, and caution rows are the normal fill roles. Keep the palette small
and calm: avoid rainbow palettes, decorative alternating fills, and high-chroma
backgrounds that compete with the model logic. Use `ib_format.py` semantic row-span helpers
for generated xlsx fill/border row components instead of hand-painting
arbitrary cells. Border discipline
follows the same rule and is equally strict: meaningful row rules use the same
table/block column span as the attached data surface, including blank member
cells where that keeps the section, header, total, or check row aligned. Do not
stop a border because a cell is blank, and do not draw borders only around
populated cells when the data table continues farther right. Stop the rule at
the edge of the related table/block or comparable row span; leave only trailing
canvas and unrelated overflow spacer cells borderless. Dedicated hierarchy /
indent columns stay borderless; draw the rule from the row's actual
hierarchy-position label/data column, not across earlier 20px spacer columns.
Memo, source, note, and interpretation cells are usually borderless; they read
through typography and placement, not grid lines. Borders are not row-by-row
decoration. Use them mainly before or around meaningful rows where a structural
accent is needed. As with background fills, avoid repeating the same prominent
top/bottom rule across adjacent rows unless it is an explicitly declared table
grid; use typography, spacing, or quiet whitespace for supporting rows. Use
three border weights by meaning: normal thin for ordinary structural breaks,
one-step-thicker medium for major section or decision boundaries, and normal
dotted for soft/provisional separations such as optional checks or supporting
context. Border colors are black by default. Do not introduce gray, colored, or
decorative border colors unless the user supplies a house style; visual priority
comes from sparsity, placement, and thin/medium/dotted weight, not from color.

Analysis gates: material assumptions need selected driver, explanatory drivers,
implied value, support ratio/variance, and evidence status. Weak evidence feeds
scenario/sensitivity/benchmark/DD. KPI, scenario, valuation, benchmark, and memo
surfaces interpret the model and connect evidence to next actions. Write memos
from a clean base rather than preserving legacy layout compatibility; include
only the necessary and sufficient supplemental context for the current decision.
For xlsx outputs, each generated sheet must pass the sheet-level quality rubric:
it needs a distinct purpose, source boundary, dependency flow, checks where
errors would matter, and interpretation where it is an output surface. Do not
create a sheet just because it belongs to a canonical full-workbook order.

Do not treat model construction as completion. Before closeout, run command
checks and rendered-output inspection for both finance logic and sheet design:
formulas, reconciliation, unit/scale integrity, source status, styles, layout,
fonts, fills, borders, print/canvas bounds, and visible readability. Render or
open the xlsx/PDF/screenshot whenever tooling is available; if rendering is
blocked, document the blocker and still run workbook inspection commands.
Follow `_self_review_protocol.md`. If tests, workbook inspection, render
checks, or artifact self-review find failures, fix the concrete failed items
and rerun the same checks. Keep iterating until the model logic and the visible
sheet design are both sufficient, or a real blocker is explicitly documented.
