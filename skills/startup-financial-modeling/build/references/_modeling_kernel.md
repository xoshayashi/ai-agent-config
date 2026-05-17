# Modeling Kernel

The default architecture is an economic kernel that can handle seed to pre-IPO
companies without assuming a fixed sector or maturity template.

## Kernel Inputs

- Decision: what choice the model must support.
- Model grain: annual, quarterly, or monthly periods, fiscal year, currency,
  display scale, consolidation scope, and forecast horizon.
- Evidence map: source facts, management targets, estimates, assumptions, and
  unknowns.
- Entity map: parent, subsidiaries, segments, products, geographies, customers,
  assets, instruments, and shareholders where relevant.

## Driver Tree

Build a driver tree before adding workbook tabs. Start with primitive flows:

- Demand: leads, customers, sites, units, transactions, utilization, retention,
  cohort behavior, renewals, churn, expansion, and pipeline conversion.
- Monetization: price, take rate, subscription, usage, service, hardware,
  license, financing, setup, maintenance, or success fees.
- Delivery: COGS, hosting, field service, implementation, support, robot or
  equipment economics, warranty, returns, and supplier constraints.
- Capacity: hiring, productivity, facilities, manufacturing, inventory,
  working capital, capex, leases, debt capacity, and cash runway.
- Financing: equity, converts, venture debt, leases, grants, customer advances,
  project finance, secondary, and exit proceeds.

## Variable Selection Protocol

The driver tree may contain many possible variables. The model should deepen
only the variables that matter for the decision.

Rank candidate variables by:

- decision relevance: whether the variable changes pricing, runway, financing,
  valuation, hiring, ownership, or diligence;
- financial impact: effect on cash, gross margin, EBITDA, funding gap,
  covenant headroom, dilution, valuation, or return;
- evidence weakness: whether support is actual/contracted, benchmarked,
  management target, estimate, placeholder, or unknown;
- controllability: whether management can act on the variable;
- time variability: whether the driver changes materially across periods;
- investor scrutiny: whether investors, lenders, or acquirers are likely to
  question it.

Use primitive independent drivers as assumptions. Calculate dependent outputs
from those drivers. Do not assume both a dependent output and the primitive
drivers that create it unless the duplicated value is explicitly labeled as a
check.

Examples:

- assume lead volume, conversion, quota capacity, and churn; calculate new
  customers and ending customers;
- assume BOM, service workload, support tickets, and cost per ticket; calculate
  COGS and gross margin;
- assume round size, pre-money value, option pool, debt/lease capacity, and
  secondary; calculate dilution and proceeds;
- assume segment primitives and calculate SOTP; do not use SOTP as evidence
  for the segment assumptions.

## Assumption Depth

Do not stop at one-step assumptions when the evidence is thin. A selected
driver should be decomposed until a reader can see why the number is plausible
or which missing proof would change it.

Use this pattern for important assumptions:

- Selected driver: the row downstream formulas use.
- Explanation drivers: funnel volume, conversion, workload, price/value,
  capacity, cost stack, or financing terms that explain the selected driver.
- Implied value: a formula that calculates what the explanation drivers imply.
- Support ratio / variance: a formula that compares the implied value to the
  selected driver and surfaces whether the assumption is over- or under-backed.
- Evidence status: source fact, management target, estimate, placeholder, or
  unknown.

Examples:

- Demand: qualified pool x conversion = implied new units, compared with
  selected new units.
- Pricing: customer annual value x capture share and cost-plus floor, compared
  with selected monthly price.
- Cost: delivery, cloud, support tickets, and cost per ticket, compared with
  selected COGS and unit margin.
- People: squads, GTM productivity, and support load, compared with selected
  headcount.
- Capital: capex per unit, other capex, revenue intensity, and financing
  coverage, compared with the selected raise and runway.

Keep the decomposition registry in the economic-kernel layer. Sheet renderers
may resolve rows, columns, formats, and styles, but they should not hard-code a
universal assumption block or bury business-mechanic logic inside layout code.

## Engines

Use only the engines needed by the decision:

- Operating engine: converts units, customers, usage, capacity, and prices into
  revenue and gross profit.
- Cost engine: links headcount, commissions, R&D, G&A, sales, service, and
  variable cost to activity levels.
- Asset engine: models capex, depreciation, inventory, leases, deployed assets,
  and hardware cost curves.
- Working-capital engine: models receivables, payables, deferred revenue,
  inventory, advances, and tax timing.
- Capital stack: traces cash sources, debt, interest, covenants, equity rounds,
  converts, warrants, option pool, and ownership.
- Scenario engine: centralizes base/downside/upside, sensitivity, break-even,
  runway, covenant, dilution, valuation, and exit cases.

## Output Logic

Start from the smallest complete graph of dependent logic. Add a sheet only
when it owns a distinct calculation surface or makes a decision auditable.

Use direct formulas. Keep source facts separate from assumptions. Where the
source is thin, show the placeholder assumption and the decision sensitivity it
controls.

Store monetary inputs as raw base-currency values and express `actual`,
`thousand`, `million`, or other display scales through Excel number formats and
unit labels. Operational units such as units, customers, FTE, days, months,
percentages, and multiples should keep their own non-money units.

## Narrative Anchoring And Governors

Sector profiles carry default ramp shapes and cost-to-serve drivers calibrated
for a generic company. Applied unchanged to an out-of-profile narrative they
produce economically incoherent plans (a hardware-priced delivery cost on a
SaaS seat once yielded a -789% gross margin). The kernel therefore reconciles
profile defaults against what the narrative actually states, before any
workbook tab is rendered:

- Gross-margin governor: when a target or stated gross margin exists, rescale
  the cost-to-serve components (variable COGS %, delivery, cloud, support) by
  one per-period factor so total COGS lands on `(1 - target gross margin) x
  revenue`. Scale all components proportionally so the profile's cost *mix* is
  preserved while its *level* is corrected; each component still reads as an
  honest decomposition of COGS.
- Stated-margin extraction: a narrative gross-margin figure (`gross margin ...
  78%`, `粗利率 78%`) overrides the profile default.
- Demand retargeting: a stated maturity ARR or customer count rescales the unit
  and customer ramps so the plan reaches its own headline scale. A plan that
  lands an order of magnitude short of its stated target is not investor-grade.
- Conservative grain detection: the forecast architecture is annual (revenue,
  cost, and comp formulas annualize per period). Only an explicit monthly or
  quarterly *model* request flips the grain; metric phrases like `monthly burn`
  or `18-month runway` stay annual.

Keep these reconciliations in the economic-kernel layer, not in sheet
renderers. They are economic inference, not layout.

## Best-Practice Benchmark Lens

Use external benchmarks as context for questions, not as frozen truth. Current
startup finance practice consistently rewards:

- driver-based assumptions separated from dependent outputs;
- assumptions supported by historical data, source facts, benchmarks, or clear
  evidence status;
- unit economics at the real economic-unit level rather than blended averages;
- runway and funding need tied to burn, milestones, working capital, capex,
  financing capacity, and dilution;
- scenario and sensitivity axes chosen from high-impact weak evidence;
- valuation tied to method credibility, financing risk, ownership, and investor
  returns;
- a memo that names the breakpoint and DD action rather than only summarizing
  tabs.

If the model cannot source a benchmark, mark the benchmark as needing refresh
and carry the unsupported driver into scenario, sensitivity, and diligence.

## Implementation Boundary

The workbook builder should keep economic inference separate from spreadsheet
rendering:

- `economic_kernel.py` owns source extraction, business-mechanics scoring,
  generic driver surfaces, and reusable forecast primitives.
- Workbook renderers own sheet layout, cell styles, formulas, charts, and file
  output.

Do not bury category detection, pricing defaults, capital-stack assumptions, or
driver-tree composition inside a sheet-rendering function.
