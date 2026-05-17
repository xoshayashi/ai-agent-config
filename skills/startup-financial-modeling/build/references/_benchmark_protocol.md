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
