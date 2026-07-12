# Benchmark and Source Protocol

Benchmarking should support assumptions and investment judgment without
pretending that stale or weak sources are facts.

## Source Hierarchy

Use the strongest available source type for the decision:

1. Actual company data, signed contracts, invoices, cohort exports, bank data.
2. Pipeline with named customer status, probability, timing, and stage.
3. Public filings, audited financials, investor presentations, official data.
4. Current market reports or reputable third-party datasets.
5. Comparable company / transaction data with clear relevance limits.
6. Management target or operating plan.
7. Modeler estimate.
8. Placeholder or unknown.

Label the evidence type. Do not blur management targets, benchmarks, and facts.

## Refresh Triggers

Refresh or explicitly mark benchmark support as stale when:

- pricing, valuation, interest rates, market size, comparable evidence, or
  funding terms are decision-critical;
- the source date is missing or older than the decision context warrants;
- the user asks for investor-ready, board, lender, DD, or fundraising output;
- a weak benchmark is the only support for a material assumption.

The workbook generator should attempt public-market comparable refresh by
default for valuation-facing outputs. If the auto-selected public ticker set is
not appropriate, override it with explicit ticker symbols. Private-company,
funding-round, M&A, market-report, customer, and internal benchmarks should be
accepted through structured evidence fields and kept in the same register with
source date and applicability limits. If live retrieval fails, keep the failure
in the Benchmarks sheet and mark the support as needing refresh rather than
silently falling back to stale multiples.

## Applicability Check

Every benchmark should state why it is comparable:

- stage, geography, customer type, contract length, and sales motion;
- gross margin definition and revenue recognition;
- capex, lease, debt, or working-capital differences;
- public vs private company differences;
- segment mix and accounting policy differences.

If the benchmark is directionally useful but not directly comparable, say so in
the Source / driver or Benchmarks sheet.

## Source Hygiene

Source fields should contain traceable sources, source categories, or evidence
status. Modeler-created assumptions are labeled `estimate`,
`management target`, `placeholder`, or `unknown` as appropriate, while traceable
sources carry their date, owner, file, or URL.

## Register Fields

When benchmarks or source facts are material, keep a compact register with:

| Field | Purpose |
|---|---|
| source_id | Stable short identifier used by assumption, KPI, and memo rows |
| source type | Use the canonical evidence status vocabulary from `_terminology.md` |
| date / period | Date of observation or benchmark period |
| URL / file / owner | Traceable location or internal owner |
| applicability limits | Geography, customer type, contract length, evidence stage, or method caveat |
| freshness status | current, stale, needs refresh, or not externally sourced |
| linked assumption | Driver or KPI that uses the evidence |
| refresh-needed flag | Whether the item must be refreshed before external circulation |

Do not create fake entries to make the register look complete. Empty evidence
should remain visibly unresolved.

## Comparable Evidence Coverage

Do not hard-code the evidence universe to one market-data endpoint. Gather the
widest relevant set that can be traced and caveated:

- public traded comps from market data, filings, investor materials, and index
  or sector datasets;
- private-company comparables from funding rounds, post-money valuations,
  reported ARR/revenue, credible data-room exports, databases, or press
  releases;
- precedent M&A transactions, tender offers, secondary transactions, and
  strategic investments;
- market reports, procurement benchmarks, customer ROI studies, pricing surveys,
  and usage/cohort datasets;
- internal contracts, pipeline, customer references, invoices, cohort exports,
  and board-approved operating plans.

For each comparable, capture company/target name, type, source type, source URL
or file/owner, date or period, geography/stage, revenue or EBITDA multiple when
available, and explicit applicability limits. Use medians as valuation support
only when at least one comparable returns or provides a usable multiple. Treat
private and transaction data as evidence that needs provenance, not as audited
truth: identify whether the value is enterprise value, equity value, post-money,
secondary price, or reported headline figure before comparing it to model EV.

For public comps, still call out scale, listing liquidity, accounting policy,
growth, profitability, and segment-mix differences. For private comps, call out
round terms, liquidation preferences, security type, disclosure quality, stage,
growth, margin, geography, and whether revenue/ARR is actual, run-rate, or
management-reported.

For pre-revenue or milestone companies, listed public peers are usually only a
conservative fallback anchor. Treat them as a prompt to gather private funding
rounds, milestone-triggered licensing deals, grants/non-dilutive financing,
strategic investments, and precedent transactions before relying on a public
multiple.

## Material Evidence Lenses

When a driver is material, benchmark support should be organized around the
kind of decision it informs, not around a fixed company template. Add a compact
register, table, or separate support sheet only when the evidence changes the
decision or protects the model from a weak assumption.

Common evidence lenses:

| Lens | Use when material | Minimum fields |
|---|---|---|
| Labor / HR comps | headcount, compensation, hiring pace, R&D mix, support capacity, or productivity drives burn or proof timing | company / source, role or function, geography, headcount or comp metric, period, applicability limit |
| Venture equity / funding comps | round size, valuation, investor quality, dilution, or financing feasibility drives the case | company, round, date, amount, valuation basis, investor, stage/geography, security caveat |
| Venture debt / non-dilutive capacity | debt, warehouse lines, grants, customer advances, or other non-dilutive financing changes runway or dilution | lender/provider, facility type, size, term, rate, collateral/covenants if relevant, geography, decision implication |
| Pricing / customer ROI comps | price, value capture, willingness-to-pay, implementation cost, or ROI proof drives revenue quality | customer segment, value metric, price/fee, ROI bridge, source date, contract/proof status |
| Market / competitive benchmarks | TAM/SAM/SOM, adoption pace, utilization, cost curve, or competitive position supports the plan | source, metric, geography, period, methodology, linked model driver |

The sheet set can remain generic: these lenses may live in Benchmarks, Market
Support, People Plan, Financing, Pricing, or a user-requested support sheet.
The gate is not the sheet name; the gate is whether the material assumption has
traceable evidence, a freshness status, an applicability limit, and a linked
decision implication.

## Quantitative Reference Bands

Use these as review anchors, not frozen truth: confirm the period basis,
revenue definition, stage, and vintage before treating any number as a gate,
and refresh against the cited source before external circulation. Each band is
Healthy / Warning / Anomaly. Reserve Anomaly for values outside any defensible
range — a likely modeling error or an unsupported assumption.

Gross margin by business model (report on net revenue for marketplace, on
subscription revenue for SaaS, on net interest margin for lending):

| Model | Healthy | Warning | Anomaly |
|---|---|---|---|
| B2B SaaS (pure software) | 75-85% | 65-75% or 85-90% | <60% or >92% |
| AI-native software | 50-65% | 40-50% or 65-75% | <35% |
| Marketplace (on net revenue) | 50-70% | 30-50% | <25% |
| Hardware / asset-heavy | 30-50% | 20-30% or 50-65% | <15% or >65% |
| Fintech — software/infra fees | 70-85% | 55-70% | <45% |

A model whose gross margin sits outside its declared vertical's band — a
"hardware" plan at 85%, a "marketplace" margin computed on GMV not net revenue —
is a model-vertical mismatch and should be hard-flagged.

Unit economics and capital efficiency (steady-state heuristics; apply stage
context — early-stage values are legitimately weaker):

| Metric | Healthy | Warning | Anomaly |
|---|---|---|---|
| LTV / CAC | 3-5x | 1-3x or >6x | <1x or >10x |
| CAC payback | <12 mo | 12-24 mo | >24 mo |
| Net revenue retention | >=110% | 95-110% | <90% |
| Gross revenue retention | >=90% | 80-90% | <75% |
| Rule of 40 (growth% + FCF margin%) | >=40% | 0-40% | <-20% |
| Burn multiple (net burn / net new ARR) | <1.5x | 1.5-3x | >3x or <0 with positive net new ARR |
| SaaS magic number | >=0.75 | 0.5-0.75 | <0.5 |
| Revenue (ARR) per FTE at scale | >=$200-250K | 25% below stage median | <$50K beyond seed |
| Runway at the planned raise | 18-24+ mo | 12-18 mo | <12 mo |

Operating-expense ratios as % of revenue, seed to Series B (R&D dominates OpEx
until roughly $5-10M ARR, when S&M crosses above it):

| Line | Healthy | Warning | Anomaly |
|---|---|---|---|
| R&D | 25-50% | 20-25% or 50-65% | <15% or >75% |
| S&M | 20-50% | 50-65% | >80% |
| G&A | 8-20% | 20-30% | >35% |

Sources (refresh before external use): OpenView 2023 SaaS Benchmarks (last
edition); Bessemer State of the Cloud 2024; ICONIQ Growth 2024-2025; a16z "16
Startup Metrics" 2015 / Growth Metrics 2022; David Skok / forEntrepreneurs SaaS
Metrics ~2010; David Sacks "SaaS Metrics That Matter" 2022; Carta State of
Private Markets 2024; Finro fintech framework 2024-2025.

The bands above are review anchors for the modeler, not the generator's
evaluation axis. The generated KPI sheet carries a `KPI vs live public peers`
block whose comparison axis is fetched at generation time: peer gross-margin
and EBITDA-margin median / low / high come from the live public comparable
retrieval, and the plan-vs-peer verdict is a formula against that fetched
range. Do not hard-code benchmark constants into the generator or the
workbook; when live peer margins cannot be retrieved, mark the block for
refresh rather than back-filling a stale number.
