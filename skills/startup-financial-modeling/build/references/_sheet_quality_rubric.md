# Sheet Quality Rubric

This rubric turns financial-modeling best practice into sheet-by-sheet quality
gates. It is stricter than a generic workbook checklist: every sheet must earn
its place, expose its inputs and sources, calculate from upstream drivers, show
checks where errors would matter, and interpret the decision impact where the
sheet is an output surface.

Use this with `_modeling_kernel.md`, `_output_modes.md`,
`_self_review_protocol.md`, and `_ib_workbook_design_system.md`.

## Better-Than-Best-Practice Bar

External modeling codes and IB/FP&A practice consistently point to a few core
principles: separate inputs, calculations, and outputs; make model flow readable
left-to-right and top-to-bottom; keep assumptions traceable; use consistent
timing blocks; include checks; keep formatting clear; and audit the workbook
before relying on it. This skill should go further by making every sheet
decision-relevant, evidence-aware, dependency-complete, and visually scannable.

For every generated sheet, verify:

- **Purpose:** row 2/3 should make the sheet's decision role obvious.
- **Ownership:** the sheet should own a distinct input, calculation, output,
  evidence, or interpretation surface. If not, omit it or merge its logic.
- **Source boundary:** facts, estimates, management targets, placeholders, and
  unknowns should be visibly distinguishable.
- **Dependency flow:** formulas should flow from source facts and assumptions to
  calculations, checks, outputs, and memo implications.
- **Unit integrity:** money values should remain raw base-currency numbers,
  with display scale, currency symbol, negative display, and zero display
  handled by `number_format`; visible unit labels must match those formats.
  Non-money units such as units, customers, count, FTE, days, months, `%`, and
  `x` should keep their own formats and should not be normalized as currency.
- **Checks:** reconciliation, balance, ownership, cash, unit, or evidence checks
  should exist where an error would change the decision.
- **Interpretation:** output sheets should state what the result means, not only
  calculate it.
- **Design:** use the canonical no-wrap, no-merge, sparse-fill, sparse-border,
  black-border, workbook-consistent role-width, table-local span, and
  role-based palette rules. Design is part of model quality.

## Sheet-Level Gates

| Sheet | Must prove | Failure smell |
|---|---|---|
| Guide | Decision, business mechanics, source boundary, sheet map, formatting key (colors, ▲, sign convention, hybrid-axis boundary), and model qualifications orient a new reviewer in under a minute. | Generic instructions, missing formatting key, or navigation that does not match actual sheets. |
| Summary | Answers the first five minutes of investor questions without opening engine tabs: annual condensed P&L, cash & runway, mechanism-fit KPIs (≤10) with benchmark context, all-scenario comparison with a staleness check, consolidated checks + master check, cross-checks (final-year market share, revenue per FTE, growth vs market), and a recommendation with conditions. | A metrics dump without judgment; scenario numbers that cannot be traced or verified; missing master check. |
| Assumptions | Every driver row has value, unit, source/driver explanation, and evidence status; scenario toggle + case table actually drives the engine; the driver map shows what matters and who owns it; no irrelevant-mechanic or all-zero placeholder rows. | Dependent outputs hardcoded as assumptions; rows without source status; scenario table disconnected from the model body. |
| Revenue Build | Calculates revenue bottom-up from the real economic unit (customers, units, GMV × take rate, utilization × rate) with retention/churn logic, plus demand-support (funnel coverage) and price-support (ROI / cost floor) verification blocks and a revenue bridge check. | Revenue entered directly, derived from TAM × share, or SaaS defaults forced onto non-SaaS mechanics. |
| Cost Build | Separates variable COGS, delivery/cloud/support cost-to-serve, department opex programs, and capex tied to activity drivers, with a gross-margin-vs-target check. | Margin assumed directly while cost drivers stay hidden; opex as one blanket % of revenue. |
| People Plan | Department FTE × loaded compensation (statutory welfare rate handled), capacity checks (customers per CS FTE, required support FTE), and a headcount-vs-revenue-growth sanity flag. | FTE grows as a flat percentage without capacity logic; payroll ignores social-insurance load. |
| P&L | Presents revenue, gross profit, opex, EBITDA, D&A, interest, tax, and net income purely from upstream schedules (tax-exclusive), with margins and a consistency check. | P&L contains independent assumptions or buried hardcodes. |
| BS | Balances cash, working capital (site-based AR), assets, tax-timing balances, debt, and equity with an explicit tolerance-based balance check. | Plugs, or a balance sheet that does not reconcile to CF and P&L. |
| CF | Tax-inclusive cash plan: operating cash with consumption-tax / withholding / social-insurance balance deltas (simplifications noted), capex, financing by instrument, ending cash, runway months, and a cash-shortfall check. | Cash flow duplicates P&L without cash timing; runway absent; tax timing silently ignored. |
| Financing | Sources & uses, instrument terms, post-raise runway ≥18 months check, and a live downside funding gap. | Funding need not tied to runway or milestone coverage. |
| Cap Table | Rounds register with pre/post money, price per share, share counts by class, issued and fully diluted ownership, voting-threshold flags (66.67/50.01/33.34%), option-pool range check, and a 100% reconciliation check. | Percent-only dilution with no share math; converts/options ignored; no reconciliation. |
| Evidence | Real comparable/benchmark evidence only (source, date, applicability, freshness); retrieval failures and evidence gaps are visible rows; market sanity (TAM/SAM/SOM) is isolated from the revenue chain and feeds only cross-checks. | Fake or placeholder source rows; market size feeding revenue formulas. |
| Pricing | Connects customer ROI/value capture, cost-plus floor, willingness-to-pay evidence, margin, sales friction, and validation tests. | Price copied from management target without triangulation. |
| Unit Economics | Per-unit P&L (price, cost-to-serve, margin), CAC/LTV, payback, retention basis, and benchmark context tied to the economic unit. | Generic SaaS metrics detached from the actual unit. |
| Valuation & Exit | Method matrix (rows = methods, columns = low/mid/high + credibility), selected range, exit waterfall (net debt, transaction costs, preference, proceeds by holder), and investor return with guarded division. | Period columns abused as method ranges; averages methods blindly; MOIC divides by a floor constant. |
| Segments | Real per-segment economics (requires ≥2 stated segments), source status, and a consolidation bridge check. | Segment labels sharing one blended assumption set. |
| IC Memo | Recommendation, KPI readout, what must be true, downside triggers, valuation support, financing/ownership implication, ranked DD questions, and source boundary. | Memo summarizes tabs instead of making an investment judgment. |

## Sheet Inclusion And Omission

Do not generate a sheet merely because it is in the canonical full-workbook
order. Include a sheet only if it owns a distinct decision surface or is needed
for dependency closure. For focused modules, either omit irrelevant sheets or
replace them with compact registers that preserve traceability without creating
empty theater.

When a sheet is omitted:

- confirm no formulas point to the missing sheet;
- preserve any needed upstream assumptions or downstream checks in a compact
  dependency-complete surface;
- state what analysis was intentionally out of scope.

## Cross-Sheet Flow

The workbook should read like a decision argument:

1. Guide defines the decision, evidence, mechanics, and scope.
2. Assumptions (register + driver map + scenario table) selects the material
   variables.
3. Operating schedules calculate revenue, cost, people, assets, cash, capital,
   and ownership from those variables.
4. Summary's KPI block, scenario comparison, cross-checks, and the Evidence
   register test the weak links.
5. The Summary recommendation block (or a conditional IC Memo) converts the
   model into recommendation, risks, and diligence action.

If this flow is broken, repair the model structure before polishing formatting.
