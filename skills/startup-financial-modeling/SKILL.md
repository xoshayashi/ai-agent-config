---
name: startup-financial-modeling
description: "Use when the user needs startup-finance artifacts: xlsx financial plans, model specs, assumption registers, workbook audits, cap tables, valuation, pricing, runway, unit economics, M&A exit, IC memo support, or AI-assisted model prompt workflows."
---

# Startup Financial Modeling

Build from economic primitives. Separate facts, estimates, assumptions, and
unknowns. Use a former investment-banker / startup-CFO stance: convert the
equity story into auditable economics, financing, dilution, and return logic.
First read `build/references/_skill_invocation_protocol.md`; then load only the
smallest needed refs. For generator, library, formula, or workbook-architecture
changes, also read `build/references/_excel_generation_architecture.md`.

Use `scripts/build_model.py`. Primary path: read the source yourself, choose
drivers, and pass structured YAML with `--input`; `--source-md` is fallback.
Modes: `full`, `pricing`, `unit_economics`, `cap_table`, `ma_exit`,
`dcf_only`, `burn_runway`, `three_statement`, `market_sizing`, `comps_only`.
Use `--live-comps` for specific public tickers and YAML `private_comps`,
`transaction_comps`, or `benchmark_sources` for provided evidence.

For xlsx outputs, run command checks plus rendered/recalculated inspection; when
possible inspect spreadsheet-engine `data_only=True` values for errors.
Before handoff, run `python3 scripts/quality_gate.py --full` when time allows,
or `python3 scripts/quality_gate.py --skip-pytest` as the minimum deterministic
rubric + strict-audit gate. Do not close below the 95/100 domain rubric
threshold unless you state the blocker.

## YAML input schema

When taking the `--input` route, see `build/references/_input_schema.md` for
the full set of YAML keys, their defaults, and the K-set audit invariants
(K1 / K2 / K4 / K5) they flow through.
