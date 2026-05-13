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
`_layout_canonical.md` and `_ib_workbook_design_system.md`. Add `_modeling_kernel.md`,
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
formulas, editable grid structure, unnumbered sections, traceable sources,
Google-Sheets-20px hierarchy / indent columns (`2.14` xlsx width), no native
indent or leading-space indentation, no frozen panes, and generated cells with
`wrap_text` off. Treat text wrapping as prohibited for
generated workbook cells; fix long text with column width, table structure, or
blank overflow space instead of enabling `wrap_text=True`. If the user
explicitly requests a prose-heavy exception with wrapping or manual line breaks,
row height must be set to the exact visible line count so no text is clipped and
the row still looks intentional.

Design gates: `_layout_canonical.md` owns grid, columns, hierarchy widths, units,
formulas, and layout mechanics. `_ib_workbook_design_system.md` owns visual
roles, font, color, borders, highlights, charts, and render expectations.
Use background fills and prominent borders as selective semantic signals: extend
them through blank cells when that completes a row component or section band,
but avoid repeating the same fill or heavy rule across consecutive rows unless
the adjacent rows form a deliberate table structure or heatmap.

Analysis gates: material assumptions need selected driver, explanatory drivers,
implied value, support ratio/variance, and evidence status. Weak evidence feeds
scenario/sensitivity/benchmark/DD. KPI, scenario, valuation, benchmark, and memo
surfaces interpret the model and connect evidence to next actions. Write memos
from a clean base rather than preserving legacy layout compatibility; include
only the necessary and sufficient supplemental context for the current decision.

Before completion, recalculate or open/render the xlsx when practical and follow
`_self_review_protocol.md`. If tests, workbook inspection, render checks, or
artifact self-review find failures, fix the concrete failed items and rerun the
same checks. Do not close out while known test or inspection failures remain
unless a blocker is explicitly documented.
