# KPI Analytics

KPI work is not a fixed dashboard. It is the analytical layer that tells the
reader whether the model's economic engine is investable, fundable, and
operationally credible.

The KPI surface is a block of at most 10 rows on the Summary sheet, not a
dedicated tab. Each row carries the metric, its unit, and a compact
benchmark-context note (gray) sourced from the Evidence register.

## Selection Protocol

Choose KPIs from the economic mechanism, the decision, and the model stage. A
KPI is useful only if it changes a financing, pricing, hiring, valuation, risk,
or diligence decision. For a recurring-software mechanism the natural set is
ARR, growth, gross margin %, NRR, churn, CAC payback, LTV/CAC, burn multiple,
Rule of 40, and revenue per FTE — but treat that as an example of
mechanism-fit selection, not a template.

For each candidate KPI, ask:

- What decision does it inform?
- Which independent drivers move it?
- Is it leading, lagging, or a check metric?
- What benchmark, source fact, or management target gives context?
- What downside trigger would make the plan fail?
- Which scenario or sensitivity should pressure-test it?

Do not include a metric because it is fashionable. If ARR, LTV/CAC, GMV,
payback, NRR, robot utilization, loan loss, or Rule of 40 is not meaningful for
the actual economics, omit it or label why it is not decision-useful.

## KPI Families

Use families, not templates:

| Family | Purpose | Example metrics |
|---|---|---|
| Scale | Shows whether the operating base is large enough for the decision | units, customers, sites, GMV, ARR, originations, deployed assets |
| Monetization | Shows value capture and pricing power | ARPU, ACV, take rate, usage revenue, attach rate, contract value |
| Retention / quality | Shows durability | logo retention, NRR, repeat rate, utilization, renewal, churn, loss rate |
| Unit economics | Shows whether growth creates value | gross margin, contribution margin, payback, revenue / unit, service cost / unit |
| Capacity | Shows whether the plan can be executed | sales capacity, deployment capacity, support load, manufacturing throughput, FTE productivity |
| Cash and capital | Shows survivability and financing need | burn, runway, funding gap, capex intensity, working-capital drag, debt capacity |
| Ownership and return | Shows investor/founder economics | dilution, option pool, investor ownership, MOIC, IRR, founder proceeds |
| Evidence / diligence | Shows what is proven vs assumed | evidence status, support coverage, benchmark variance, open DD item count |

## Interpretation Notes

Every KPI row should have enough context to be read, not just calculated:

- selected KPI value or trend;
- source / driver and evidence status;
- benchmark or target range when available;
- scenario or sensitivity that pressures it;
- investment implication or diligence question.

The KPI interpretation register survives as compact notes on the Summary KPI
block, not as a separate sheet. When a note needs more room, put the evidence
detail in the Evidence register and the judgment in the Summary recommendation
block or the IC Memo (when present). Do not leave interpretation only in the
final chat.

## Maturity and Mechanic Signals

Maturity and mechanics are signals for selecting metrics, not metric packs. If
decision-relevant, prioritize from these candidate areas and replace them when
the actual driver tree points elsewhere:

- Proof still ahead: runway, milestone burn, hiring, prototype cost,
  grant/convertible coverage, next financing need, and ownership. Commercial
  KPIs should appear only as explicit placeholders or future validation tests.
- Commercial proof emerging: conversion, pricing proof, customer ROI, sales
  cycle, gross margin bridge, support load, cash runway, and next-round
  readiness.
- Repeatability / scaling pressure: retention, cohort quality, GTM capacity,
  operating leverage, working capital, capex, capital efficiency, and downside
  funding need.
- Institutional / pre-exit complexity: segment economics, consolidation, tax,
  debt/lease capacity, covenant headroom, secondary, SOTP valuation,
  IPO-support metrics, and investor/founder return.

These are prompts for selection, not required sheet templates. Use only the
metrics that the decision can actually use.

## KPI Definition Discipline

For each material KPI, keep a compact definition record:

| Field | Purpose |
|---|---|
| Formula | How the metric is calculated from workbook drivers |
| Applies when | Economic condition that makes the KPI decision-useful |
| Do not use when | Condition that would make the KPI misleading |
| Source context | Benchmark, target, actual, or estimate used for interpretation |
| Downside trigger | Threshold or trend that would change the decision |
| IC implication | Financing, valuation, hiring, pricing, or DD implication |

Common KPI names are not definitions. Burn multiple, NRR, payback, Rule of 40,
loan loss, capital efficiency, and similar metrics must be formula-defined in
the artifact or omitted. Keep the record as compact notes attached to the
Summary KPI rows (driver/source column plus note column); it does not justify
a separate sheet.
