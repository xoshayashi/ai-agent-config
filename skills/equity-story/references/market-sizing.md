# Market Sizing — Equity Story Reference

The market section answers one question: **is the prize big enough to matter,
and is the path to it credible?** This reference is the discipline for answering
it at investment-grade rigour. Read it when the story turns on the size of the
opportunity — most of all for IPO, late-stage, and any argument that rests on a
headline market number.

## 1. The discipline — proportionate rigour, not length

Rigour means the *method* is sound and cross-checked, not that the section is
long. A 40-page market chapter is not more credible than a tight two-page one
done right; padding is the opposite of rigour. Apply the depth the stage
warrants: a seed story needs a bottom-up SOM and a sane TAM; an IPO or a
headline-number argument needs triangulation, budget-source SAM, and scenarios.
Do only what the claim requires — but do that part properly.

## 2. Bottom-up first

Build the market from **customers × price**, with the calculation visible. State
it SOM → SAM → TAM (or SOM → TAM when SAM is implicit): the wedge the company can
take, then the served market, then the category the wedge opens. A top-down "the market is $X billion" as the
headline reads as hand-waving and draws the most scrutiny — TAM is context for
ambition; the round is underwritten on the SOM. This is the floor. Everything
below raises a headline-number argument from plausible to defensible.

## 3. Triangulation — converge on the number from independent routes

A market number reached one way is an assertion; the same number reached two or
three *independent* ways is evidence. Derive TAM by routes that share no inputs
— for example: (a) a macro labour or spend gap × the share a solution captures;
(b) an analyst's category forecast; (c) a top-down economic-value estimate × the
relevant function's share. If the routes converge on the same order of
magnitude, the number is credible. If they diverge widely, the assumptions are
wrong — find which, and fix it; do not average a contradiction away.

- **Do:** show each route's calculation, then state the convergence explicitly.
- **Don't:** present routes that secretly share an input — they cannot
  cross-check each other.

## 4. SAM by budget source — not by stacking market names

Do not build SAM by adding up published market-report figures: they overlap and
double-count, and the sum means nothing. Build it from **where the buyer's money
actually comes from**. List three to five budget pools (e.g. the sales-ops
budget, the marketing budget, the compliance budget), and for each: addressable
customers × annual revenue per account. Sum to a **Gross SAM**, then subtract an
explicit **overlap discount** — the same buyer drawing on two pools, or the same
user across use-cases — to a **Net SAM**. State the discount rate and the reason
for it. A SAM with no netting step is almost always inflated.

## 5. SOM in four scenarios

A single SOM number is a guess dressed as a fact. Present four —
**Conservative / Base / Target / Upside**. Each scenario must change the *driver
assumptions* (customer count, ARPA, attach or penetration rate), not just apply
a bigger multiplier to one figure; a "scenario" that only re-multiplies Base is
not a scenario. For each, state SOM as a **percentage of SAM and of TAM** (the
penetration rate) and place it beside named comparable companies' actual
penetration at the equivalent stage — so the reader sees "Base sits within the
range these comparables reached; Upside exceeds it." Penetration that lands an
order of magnitude off precedent, unexplained, is the signal of an unanchored
plan.

## 6. Comparable-company cross-check

Validate the projected customer counts and penetration against real companies at
a comparable stage: their disclosed customer count, large-account count, ARR,
and penetration of their *own* stated TAM at IPO or the equivalent round (S-1s
and annual filings are the source). Choose comparables genuinely close in
business model and go-to-market motion — a flattering, mismatched comp set is
seen through immediately (see `stage-playbooks.md`). The cross-check answers "is
this reachable" with precedent rather than optimism.

## 7. Unit-level stress-test

When a headline number looks large — a big monthly contract value, a big
aggregate — decompose it to the unit and show the unit figure is modest. Reduce
it to per-customer, per-site, per-day: "the headline monthly figure is X per
transaction, ~Y per branch per day — below what the manual process it replaces
costs." Use this only when a number invites a "that looks aggressive" reaction;
it is a targeted move, not a routine step.

## 8. Failure modes

- A single top-down billion presented as the headline TAM.
- SAM built by stacking market-report numbers — overlap and double-count.
- A single SOM with no scenarios; or scenarios that only re-multiply one figure
  without changing the driver assumptions.
- A comparable set cherry-picked to flatter.
- A SOM whose penetration of TAM is an order of magnitude off precedent, with no
  explanation.
- Triangulation routes that share inputs — not independent, so they cannot
  actually cross-check.
- Length mistaken for rigour: a long market section that never triangulates or
  cross-checks anything.

## Illustrative micro-example

*Fictional, for illustration only — every figure below is invented. Your own
numbers must be derived independently, never copied from an example.*

A fictional B2B compliance-automation company, at IPO:

- **TAM, triangulated.** Route A: ~80,000 mid-and-large firms × ~$50k annual
  compliance-tooling spend ≈ $4.0B. Route B: an analyst category forecast for
  compliance software ≈ $4.4B. The two independent routes converge near $4B —
  credible. `[estimate]`
- **SAM, by budget source.** Compliance-software budget ($1.6B) + audit-services
  budget the product displaces ($0.9B) + risk-ops headcount budget ($0.7B) =
  Gross SAM $3.2B; less a 15% overlap discount (firms drawing on two pools) →
  **Net SAM ~$2.7B**. `[derived]`
- **SOM, four scenarios** (5-year), each with penetration vs. Net SAM:
  Conservative $34M (1.3%) · Base $68M (2.5%) · Target $120M (4.4%) · Upside
  $190M (7.0%). Cross-check: two B2B-software comparables reached ~2.1% and
  ~2.8% of their stated SAM at IPO — Base's 2.5% sits within that range; Upside
  (7.0%) exceeds it and is flagged as the bull case. `[estimate]`

## Sources

- Aswath Damodaran, *Narrative and Numbers* (2017) — discipline on tying market
  narrative to defensible numbers.
- Comparable-company S-1 filings and annual reports — the primary source for the
  cross-check in section 6 (customer counts, ARR, TAM penetration at IPO).
- `stage-playbooks.md` — comparable-company *valuation* framing (distinct from
  the customer-count cross-check here).
- `examples.md` Example 2 (ヤモリ) — the Japan-IPO worked example that
  demonstrates these disciplines applied end to end.
