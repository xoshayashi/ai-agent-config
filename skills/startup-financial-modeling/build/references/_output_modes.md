# Output Shapes

Choose output shape from the decision and the driver tree. Do not pick sheets
from a fixed classification grid.

## Integrated Decision Workbook

Use when the user asks for a fundraising model, 収支計画, financial plan,
board plan, lender plan, or investor-ready xlsx. The workbook may be annual,
quarterly, or monthly depending on model grain, but it should connect operating
logic, cash, financing, ownership, scenarios, and valuation.

Run:

```sh
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --source-md path/to/source.md \
  --output model_output.xlsx
```

Expected surfaces:

- Guide / source map / modeling assumptions.
- Driver tree and operating engine.
- Revenue, cost, people, capex, working capital, P&L, balance sheet, and cash
  flow where the decision requires them.
- Capital stack, ownership, venture debt/equity, dilution, secondary, lease, or
  project-finance modules when those flows matter.
- KPI, scenarios, sensitivity, valuation, market support, benchmarks, and IC
  memo where they clarify the decision.

## Focused Finance Module

Use when the user explicitly asks for a focused output such as pricing, unit
economics, runway, cap table, M&A exit, valuation, market sizing, or comparables
without asking for a full company plan.

Run:

```sh
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --mode <mode> --input model.yaml --output model_output.xlsx
```

Keep the artifact as small as the decision allows and dependency-complete. If a
focused sheet contains live formulas, include the upstream or downstream sheets
needed to audit those formulas. If the user needs a standalone artifact, compose
or rewire the logic as a compact spec or register so no remaining surface
depends on omitted sheets. A pricing model may need customer ROI and
contribution margin; a cap table may need option pool, secondary, tax, and
financing round mechanics.

Structured inputs should be accepted as first-class model facts, not only as
free-text narrative. In particular, `currency`, `display_scale`, `grain`,
`periods`, `segments`, operating driver series, financing instruments, and
valuation scalars should flow into the generated workbook.

## Candidate Depth Checks

Use modes as output shapes, not templates:

| Request | Candidate depth checks |
|---|---|
| pricing | customer ROI, cost-to-serve, selected price, support ratio, margin, sales cycle, risk, validation test |
| unit economics | true economic unit, price, unit cost, margin, retention/utilization, payback, capacity, benchmark context |
| burn / runway | cash roll-forward, burn drivers, financing timing, funding gap, runway breakpoint, downside case |
| cap table | ownership by holder class, option pool, converts, warrants, secondary, dilution, proceeds, exit impact |
| valuation | method credibility, method exclusions, scenario range, sensitivity, investor/founder return |
| M&A / exit | exit EV, net debt, proceeds waterfall, investor MOIC/IRR, founder proceeds, tax/secondary if relevant |
| market sizing | TAM/SAM/SOM method, source freshness, reachability, plan-to-market bridge, source gaps |
| IC memo | recommendation, KPI readout, what must be true, downside triggers, DD questions, source boundary |

These are not mandatory bundles. Select, substitute, or omit checks based on the
user's decision, available evidence, and the selected driver tree. If a request
uses a familiar label such as pricing, valuation, or cap table but the economic
dependencies point elsewhere, follow the dependencies.

The output may be xlsx, `model.yaml`, `model_spec.md`, `assumptions.csv`, or
`audit_report.md` when that better answers the user. If the user explicitly
asks for an xlsx, generate or repair the workbook and then inspect it.

## Audit Or Repair Report

Use when the user provides an existing workbook and asks to inspect, repair, or
compare it. Report concrete sheet/cell locations, formula logic, color
semantics, unit handling, raw money-value storage, and missing decision logic.
