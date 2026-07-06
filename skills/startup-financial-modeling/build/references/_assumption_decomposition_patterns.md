# Assumption Decomposition Patterns

Good startup models do not ask the reader to trust a single unsupported input.
Every material assumption should show the selected value, the drivers that
explain it, the implied value from those drivers, and a support check.

## Core Pattern

| Layer | Purpose |
|---|---|
| Selected driver | The value downstream formulas consume. |
| Explanation drivers | Operating facts that would make the selected value plausible. |
| Implied value | Formula output from the explanation drivers. |
| Support ratio / variance | Comparison of implied value to selected value. |
| Evidence status | `actual`, `contracted`, `pipeline-backed`, `benchmark`, `management target`, `estimate`, `placeholder`, or `unknown`. |

In the workbook this pattern renders as: selected drivers with evidence status
in the Assumptions register, and support blocks next to the engine that
consumes them — demand and price support on Revenue Build, cost-to-serve
support on Cost Build, capacity checks on People Plan, funding coverage on
Financing, external evidence on Evidence. It is not a separate sheet.

## Evidence Strength Ladder

Evidence status should change modeling depth:

| Status | Meaning | Modeling response |
|---|---|---|
| actual | Observed company data | May be shallow if immaterial; still preserve source and period |
| contracted | Signed or committed future fact | Link timing and scope; test delivery / collection risk if material |
| pipeline-backed | Named pipeline or probability-weighted support | Decompose conversion, timing, probability, and capacity |
| benchmark | External or comparable reference | State applicability and freshness; compare to selected value |
| management target | Company plan or target | Add primitives and support ratio if material |
| estimate | Modeler estimate | Decompose and push into sensitivity / DD |
| placeholder | Temporary value | Mark visibly and do not treat as proven |
| unknown | Missing support | Carry into DD questions and scenario downside |

If evidence is management target or weaker and the driver is material, do not
leave it as a one-step input.

## Decomposition Depth Ladder

Use only as much depth as materiality requires:

| Level | Purpose |
|---|---|
| L0 selected driver | The value used by downstream formulas |
| L1 operating primitives | Demand, price, cost, capacity, timing, or financing inputs that explain L0 |
| L2 constraint / capacity check | Sales capacity, deployment capacity, hiring, manufacturing, cash, covenant, or working-capital check |
| L3 evidence triangulation | Source fact, benchmark, actual, contracted, management target, or estimate comparison |
| L4 decision impact | Sensitivity, scenario, DD question, valuation impact, funding gap, or ownership impact |

Stop when the driver is either immaterial to the decision or sufficiently
triangulated for the reader to see what would change the decision. Continue
decomposing when support is weak, the output is highly sensitive, or investors
are likely to challenge it.

## Driver Role Discipline

Do not confuse driver roles:

- source facts and benchmarks support assumptions;
- selected assumptions feed formulas;
- explanatory drivers justify selected assumptions;
- checks compare selected and implied values;
- dependent outputs measure consequences.

Do not justify an upstream assumption with a downstream output caused by that
assumption. If a downstream output is useful, label it as a check or decision
output, not evidence.

## Archetypes

| Assumption | Explanation Drivers | Support Check |
|---|---|---|
| New customers / units | Qualified pool, reachable %, lead volume, conversion, sales capacity | Implied units / selected units |
| Price / take rate | Customer ROI, value capture %, willingness-to-pay, cost-plus floor, benchmark range | Selected price / max(value price, cost floor) |
| Retention / churn | Opening cohort, logo churn, expansion, repeat rate, renewal motion | Implied NRR / selected NRR |
| Gross margin / COGS | Delivery cost, cloud cost, support workload, ticket cost, BOM, warranty, payment/fraud/incentives | Implied COGS % / selected COGS % |
| Headcount | Product squads, quota/ramped rep, customers per CS FTE, support ticket capacity | Selected FTE / required FTE |
| CapEx / working capital | Units deployed, capex per unit, inventory buffer, AR/AP days, customer advances | Implied cash need / selected funding |
| Financing | Minimum runway, milestone timing, debt capacity, lease capacity, customer advances, dilution tolerance | Committed financing / cash need; runway / target runway |
| Valuation | Revenue, GP, EBITDA, growth, margin, Rule of 40, comps, DCF assumptions | Selected value / supported value range |

## Maturity Signals

Use maturity as context, not as a fixed template. When these signals are
present, consider the listed drivers, combine them freely, and omit anything
that is not decision-relevant:

- Proof still ahead: milestone cost, prototype or trial cost, hiring plan,
  grants, converts, next-round timing, runway to proof points, and ownership.
- Commercial proof emerging: customer ROI, pricing proof, conversion, sales
  cycle, support load, gross-margin bridge, and next-round readiness.
- Repeatability / scaling pressure: retention, cohort quality, GTM capacity,
  deployment capacity,
  working capital, capex, debt/lease capacity, and operating leverage.
- Institutional / pre-exit complexity: segment economics, consolidation,
  tax/NOL, covenants,
  secondary, option pool refresh, SOTP, IPO-support metrics, and investor /
  founder return.

## Mechanic-Specific Emphasis

Use these as candidate mechanics. A company may combine several mechanics or
fit none cleanly. Apply them only when the revenue, cost, capital, or risk flows
are evidenced:

- Two-sided network / transaction flow: do not validate revenue from TAM share
  alone. Typical primitives may include GMV, take rate, payment fees,
  incentives, fraud/loss, buyer/seller liquidity, and repeat behavior.
- Recurring contract / usage flow: typical primitives may include customers,
  ACV, churn, expansion, sales capacity, implementation load, and support cost.
- Asset / deployed-equipment flow: typical primitives may include units
  deployed, BOM or capex per unit, utilization, warranty/service cost, lease
  financing, and working capital.
- Balance-sheet or regulated flow: typical primitives may include origination,
  loss rate, funding cost, regulatory capital, warehouse/debt capacity, and
  collection timing.
- Proof-before-revenue flow: typical primitives may include milestone spend,
  prototype cost, hiring, grants, converts, runway to proof points, and
  next-round evidence.

## Completion Gate

If a critical assumption lacks explanation drivers, implied value, support
ratio or variance, and evidence status, the model is incomplete. Add the missing
rows or explicitly label why the assumption is not decision-critical.
