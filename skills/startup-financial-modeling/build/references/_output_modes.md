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

Every included sheet must satisfy `_sheet_quality_rubric.md`: a distinct
purpose, source boundary, dependency flow, checks where errors would matter,
and interpretation for output surfaces. The full-workbook order is a reading
flow, not permission to include low-value tabs.

## Focused Finance Module

Use when the user explicitly asks for a focused output such as pricing, unit
economics, runway, cap table, M&A exit, valuation, market sizing, or comparables
without asking for a full company plan.

Run:

```sh
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --mode <mode> --input model.yaml --output model_output.xlsx
```

Exact runtime mode values:

| User wording | Mode value | Visible-surface target |
|---|---|---|
| full model / fundraising / board plan | `full` | Integrated decision workbook |
| pricing / ROI / willingness-to-pay | `pricing` | Compact pricing workbook without P&L/BS/CF by default |
| unit economics | `unit_economics` | KPI and scenario surfaces needed to audit economic unit |
| cap table / SAFE / J-KISS / option pool | `cap_table` | Ownership state-machine workbook, not a full operating model |
| M&A / exit | `ma_exit` | Proceeds, valuation, scenarios, sensitivity, memo |
| DCF / valuation only | `dcf_only` | Valuation and sensitivity with required formula dependencies |
| burn / runway | `burn_runway` | Cash, financing timing, runway, downside |
| three-statement | `three_statement` | P&L, BS, CF with required dependencies |
| market sizing | `market_sizing` | Market support and benchmark register |
| comparables / comps | `comps_only` | Valuation, market support, benchmark register, memo |

Keep the artifact as small as the decision allows, but never at the expense of
formula completeness. Focused modes should include supporting sheets when a
visible output needs them. If the choice is between a larger workbook and
silently neutralized decision formulas, choose the larger workbook.

Reject sheet exclusions that would leave remaining formulas pointing to missing
sheets unless the dependent surfaces are also removed or rewired in the same
pass. When a user asks for an external-ready xlsx, run the strict audit path so
omitted-sheet references, `#REF!` markers, missing sheet-quality markers, and
workbook design regressions block handoff.
The generator attempts public-market comparable refresh by default. Explicit
tickers are an override, not a prerequisite; private-company, funding-round,
transaction, market-report, customer, or internal benchmarks should be supplied
through structured evidence fields and remain visible in the benchmark
register. Failed retrieval remains visible and should feed the IC gate.
Formula dependency is not the same as visible-sheet dependency, but formulas
that remain in the artifact must be auditable. A pricing request can still
include CF, valuation, or KPI support if those sheets are needed to preserve
calculation lineage. A cap-table request should route to the ownership state
machine unless the user also asks for an operating plan.

Structured inputs should be accepted as first-class model facts, not only as
free-text narrative. In particular, `currency`, `display_scale`, `grain`,
`periods`, `segments`, operating driver series, financing instruments, and
valuation scalars should flow into the generated workbook.

## Candidate Depth Checks

Use modes as output shapes, not templates:

| Request | Candidate depth checks |
|---|---|
| pricing | customer ROI, cost-to-serve, selected price, support ratio, margin, sales cycle, risk, validation test |
| unit economics | true economic unit, price, unit cost, margin, retention/utilization, payback, capacity, benchmark context, cohort or channel gap |
| burn / runway | cash roll-forward, burn drivers, financing timing, funding gap, runway breakpoint, milestone / covenant / facility gap |
| cap table | ownership by holder class, option pool, converts, warrants, secondary, dilution, proceeds, exit impact, preference-stack caveats |
| valuation | method credibility, method exclusions, selected range, supportability score, SOTP credibility, investor/founder return |
| M&A / exit | exit EV, net debt, transaction costs, proceeds waterfall, preference floor, investor MOIC/IRR, founder proceeds, buyer-view caveats |
| market sizing | TAM/SAM/SOM method, source freshness, reachability, bottom-up plan-to-market bridge, source gaps |
| IC memo | recommendation, price/terms stance, KPI readout, what must be true, downside triggers, ranked DD gates, walk-away conditions, source boundary |

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
