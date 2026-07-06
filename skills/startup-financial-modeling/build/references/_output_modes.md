# Output Shapes

Choose output shape from the decision and the driver tree. Do not pick sheets
from a fixed classification grid. Research basis: practitioner consensus is
6–10 core tabs with a hard cap of 12 (Northstar / Kruze / Foresight); every
sheet must own a distinct decision surface.

## Integrated Decision Workbook

Use when the user asks for a fundraising model, 収支計画, financial plan,
board plan, lender plan, or investor-ready xlsx.

Run:

```sh
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --input model.yaml --output model_output.xlsx --strict-audit
```

Default `full` sheet set (12 sheets; BS is included when working capital,
inventory, capex, or debt is material — otherwise 11):

| Sheet | Owns |
|---|---|
| Guide | Decision, mechanics, sheet map, formatting key, model qualifications |
| Summary | Annual condensed P&L, cash & runway, KPI block, scenario comparison + staleness check, consolidated checks / master check, cross-checks (検算), recommendation |
| Assumptions | Driver register (value / unit / source / evidence status), scenario toggle + case table, driver map |
| Revenue Build | Bottom-up revenue engine + demand and price support blocks |
| Cost Build | COGS, department opex programs, capex, cost-to-serve support |
| People Plan | Department FTE × loaded comp (statutory welfare rate), capacity checks |
| P&L | Statements presentation (tax-exclusive), reference-only |
| BS | Compact balance sheet + balance check (conditional) |
| CF | Cash plan (tax-inclusive 資金繰り): consumption tax / withholding / social-insurance balances, runway, shortfall check |
| Financing | Sources & uses, instruments, post-raise runway check, downside funding gap |
| Cap Table | Rounds register: pre/post, price, shares, issued & fully diluted ownership, voting thresholds, pool range check |
| Evidence | Comparable / benchmark register (real evidence only) + isolated market sanity block |

Conditional sheets (never by default; via mode or `--additional-sheets`):
`Valuation & Exit`, `IC Memo`, `Segments` (requires ≥2 real segments),
`Pricing`, `Unit Economics`.

The default time axis for the YAML route is hybrid (monthly for the first two
fiscal years + annual to five fiscal years). The `--source-md` narrative
fallback stays annual five-year unless the narrative requests otherwise.

## Focused Finance Module

Use when the user explicitly asks for a focused output. Bundles are lean by
design; builders write bundle-aware formulas (a missing upstream sheet means
the formula recomputes from Assumptions inside the bundle — never a stale
embedded constant downstream of an editable input).

| User wording | Mode value | Bundle |
|---|---|---|
| full model / fundraising / board plan | `full` | 12-sheet set above |
| pricing / ROI / willingness-to-pay | `pricing` | Guide, Assumptions, Pricing, Summary |
| unit economics | `unit_economics` | Guide, Assumptions, Unit Economics, Summary |
| cap table / SAFE / J-KISS / option pool | `cap_table` | ownership state-machine workbook (3 sheets) |
| M&A / exit | `ma_exit` | Guide, Assumptions, Valuation & Exit, Evidence, IC Memo |
| DCF / valuation only | `dcf_only` | Guide, Assumptions, Valuation & Exit, Evidence |
| burn / runway | `burn_runway` | Guide, Assumptions, CF (monthly), Financing, Summary |
| three-statement | `three_statement` | Guide, Assumptions, P&L, BS, CF, Summary |
| market sizing | `market_sizing` | Guide, Evidence |
| comparables / comps | `comps_only` | Guide, Evidence, Valuation & Exit, IC Memo |

Keep the artifact as small as the decision allows, but never at the expense of
formula completeness. Reject sheet exclusions that would leave live formulas
pointing at missing sheets. When a user asks for an external-ready xlsx, run
the strict audit path.

The generator attempts public-market comparable refresh by default; results,
provided private/transaction evidence, and retrieval failures land in the
Evidence sheet. Structured inputs (`currency`, `display_scale`, `grain`,
`fiscal_year_end_month`, `periods`, `segments`, driver series, financing
instruments, valuation scalars, `statutory_welfare_rate`,
`consumption_tax_rate`, AR/AP sites) are first-class model facts.

## Candidate Depth Checks

Use modes as output shapes, not templates:

| Request | Candidate depth checks |
|---|---|
| pricing | customer ROI, cost-to-serve, selected price, support ratio, margin, sales cycle, validation test |
| unit economics | true economic unit, price, unit cost, margin, retention/utilization, payback, CAC/LTV, benchmark context |
| burn / runway | cash roll-forward, burn drivers, financing timing, funding gap, runway breakpoint, shortfall month |
| cap table | ownership by holder class, option pool, converts, dilution, proceeds, voting thresholds |
| valuation | method credibility, method exclusions, selected range, investor/founder return |
| M&A / exit | exit EV, net debt, transaction costs, proceeds waterfall, preference floor, investor MOIC/IRR |
| market sizing | TAM/SAM/SOM method, source freshness, reachability, bottom-up plan-to-market bridge |
| IC memo | recommendation, KPI readout, what must be true, downside triggers, ranked DD gates, walk-away conditions |

These are not mandatory bundles. If a request uses a familiar label but the
economic dependencies point elsewhere, follow the dependencies.

The output may be xlsx, `model.yaml`, `model_spec.md`, `assumptions.csv`, or
`audit_report.md` when that better answers the user.

## Audit Or Repair Report

Use when the user provides an existing workbook and asks to inspect, repair, or
compare it. Report concrete sheet/cell locations, formula logic, color
semantics, unit handling, raw money-value storage, and missing decision logic.
