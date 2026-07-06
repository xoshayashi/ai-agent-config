---
name: startup-financial-modeling
description: "Use when the user needs startup-finance artifacts: xlsx financial plans, model specs, assumption registers, workbook audits, cap tables, valuation, pricing, runway, unit economics, M&A exit, IC memo support, AI-assisted model prompt workflows, or post-output/session-log-driven improvements to this skill."
---

# Startup Financial Modeling

Build from economic primitives. Separate facts, estimates, assumptions, and
unknowns. Use a former investment-banker / startup-CFO stance: convert the
equity story into auditable economics, financing, dilution, and return logic.
First read `build/references/_skill_invocation_protocol.md`; then load only the
smallest needed refs.

Use `scripts/build_model.py`. Primary path: read the source yourself, choose
drivers, write structured YAML, and run `--input ... --strict-audit`;
`--source-md` is fallback only. Mode names, sheet bundles, YAML keys, public /
private comps, design gates, and closeout checks are in the invocation protocol
and `build/references/_input_schema.md`.

For xlsx outputs, do not stop at file creation. Run strict audit, recalc/render
when available, inspect `data_only=True` errors, then run
`python3 build/evals/quality_gates.py` (offline by default;
`--allow-live-comps` opts into public comparable refresh) and the pytest suite.
For post-output feedback, failed checks, or improvement prompts, follow the
self-improvement gate in the invocation protocol before closeout.
