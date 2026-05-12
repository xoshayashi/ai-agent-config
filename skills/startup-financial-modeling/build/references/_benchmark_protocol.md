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

- pricing, valuation, interest rates, market size, public comps, or funding
  terms are decision-critical;
- the source date is missing or older than the decision context warrants;
- the user asks for investor-ready, board, lender, DD, or fundraising output;
- a weak benchmark is the only support for a material assumption.

When live research is not performed, label the benchmark as placeholder,
estimate, or needs refresh.

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
| source type | actual, contract, pipeline, benchmark, management target, estimate, placeholder, or unknown |
| date / period | Date of observation or benchmark period |
| URL / file / owner | Traceable location or internal owner |
| applicability limits | Geography, customer type, contract length, evidence stage, or method caveat |
| freshness status | current, stale, needs refresh, or not externally sourced |
| linked assumption | Driver or KPI that uses the evidence |
| refresh-needed flag | Whether the item must be refreshed before external circulation |

Do not create fake entries to make the register look complete. Empty evidence
should remain visibly unresolved.
