---
name: startup-financial-modeling
description: "Use when the user needs startup-finance xlsx work: financial plans, cap tables, valuation, pricing, runway, unit economics, M&A exit, or IC memo support."
---

# Startup Financial Modeling

Build startup finance outputs from economic primitives. First define the
decision, model grain, currency, fiscal year, time horizon, entities, and source
boundary. Separate facts, estimates, assumptions, and unknowns.

References live in `build/references/`. Use `_modeling_kernel.md`,
`_coverage_universe.md`, `_generic_composition_protocol.md`,
`_assumption_decomposition_patterns.md`, `_output_modes.md`,
`_layout_canonical.md`, `_ib_workbook_design_system.md`, `_terminology.md`,
`_kpi_analytics.md`, `_scenario_sensitivity_playbook.md`,
`_valuation_and_return_logic.md`, `_ic_memo_depth.md`,
`_benchmark_protocol.md`, `_self_review_protocol.md`. Load the smallest bundle
that covers the decision; investor-ready, DD, valuation, audit/repair, and full
plan work need the KPI/scenario/valuation/benchmark/memo/self-review refs.

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
formulas, editable grid structure, unnumbered sections, traceable sources, and
generated cells with `wrap_text` off.

Design gates: `_ib_workbook_design_system.md` and `_layout_canonical.md` are the
source of truth. Use column hierarchy, quiet white grid, semantic fills, readable
label/source widths, real overflow lanes, aligned Source/Unit columns, centered
period headers, left prose, and one primary chart unit per axis.

Analysis gates: material assumptions need selected driver, explanatory drivers,
implied value, support ratio/variance, and evidence status. Weak evidence feeds
scenario/sensitivity/benchmark/DD. KPI, scenario, valuation, benchmark, and memo
surfaces interpret the model and connect evidence to next actions.

Before completion, recalculate or open/render the xlsx when practical and follow
`_self_review_protocol.md`.
