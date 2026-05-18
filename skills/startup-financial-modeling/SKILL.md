---
name: startup-financial-modeling
description: "Use when the user needs startup-finance artifacts, especially xlsx models: financial plans, model specs, assumption registers, workbook audits, cap tables, valuation, pricing, runway, unit economics, M&A exit, or IC memo support."
---

# Startup Financial Modeling

Build from economic primitives and separate facts, estimates, assumptions, and
unknowns. First read `build/references/_skill_invocation_protocol.md`; then load
only the smallest needed refs.

Use `scripts/build_model.py`. Read the source — narrative, brief, or
conversation — yourself, decide the drivers, and pass them as structured YAML
via `--input`; that is the primary path. `--source-md` is a best-effort
narrative fallback whose regex extraction can miss any figure not adjacent to
its keyword. `--mode` selects `full`, `pricing`, `unit_economics`, `cap_table`,
`ma_exit`, `dcf_only`, `burn_runway`, `three_statement`, `market_sizing`, or
`comps_only`. Focused modes prioritize formula completeness over tiny sheet
counts. Comparable
evidence runs by default for public ticker peers; `--live-comps TICKER...`
overrides only that public peer set. Use YAML `private_comps`,
`transaction_comps`, or `benchmark_sources` for private companies, funding
rounds, M&A comps, market reports, and internal/user-provided evidence.

For xlsx outputs, run command checks plus rendered/recalculated inspection; when
possible inspect spreadsheet-engine `data_only=True` values for errors.
