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
- **Checks:** reconciliation, balance, ownership, cash, unit, or evidence checks
  should exist where an error would change the decision.
- **Interpretation:** output sheets should state what the result means, not only
  calculate it.
- **Design:** use the canonical no-wrap, no-merge, sparse-fill, sparse-border,
  black-border, and role-based palette rules. Design is part of model quality.

## Sheet-Level Gates

| Sheet | Must prove | Failure smell |
|---|---|---|
| Guide | Decision, source story, model grain, sheet map, color/font conventions, and known source gaps are clear enough for a new reviewer to orient in under a minute. | Generic instructions, missing source boundary, or navigation that does not match actual sheets. |
| Kernel | Business mechanics, economic unit, period grain, currency/scale, entity scope, and driver families are summarized before formulas branch outward. | Sector label replaces real mechanics; kernel repeats sheet outputs without explaining why drivers matter. |
| Assumptions | Primitive drivers have units, source/driver status, evidence status, selected value, explanatory drivers, implied value, and support ratio where material. | Dependent outputs are hardcoded as assumptions; important rows lack source status or unit clarity. |
| Driver Tree | Shows value creation from demand, monetization, delivery, capacity, capital, ownership, valuation, and evidence into workbook owner and decision relevance. | A list of metrics without dependency hierarchy, owner, source status, or decision relevance. |
| Revenue Build | Calculates revenue from the real economic unit: customers, units, GMV, utilization, price, take rate, attach rate, retention, or segment mix as relevant. | ARR/SaaS defaults forced onto non-SaaS models; revenue is entered directly without driver proof. |
| Cost Build | Separates variable cost, COGS, delivery, cloud, support, service, BOM, warranty, and fixed operating cost drivers tied to activity. | Margin assumed directly while cost-to-serve, workload, or capacity drivers are hidden. |
| People Plan | Links headcount to work units, productivity, squads, support load, GTM capacity, hiring timing, and fully loaded cost. | FTE grows as a flat percentage without capacity or role logic. |
| P&L | Presents revenue, gross profit, opex, EBITDA/operating profit, and key margins from upstream schedules with no buried hardcodes. | P&L contains independent assumptions that should live in assumptions or operating schedules. |
| BS | Balances from cash, working capital, capex/assets, debt/leases, equity, retained earnings, and retained losses with an explicit balance check. | Balance sheet plugs unexplained assets/liabilities or does not reconcile to CF and P&L. |
| CF | Reconciles opening cash, operating cash flow, working capital, capex, financing, and ending cash/runway. | Cash flow is an afterthought or duplicates P&L without explaining cash timing. |
| Capital Stack | Traces equity, converts, debt, leases, grants, advances, interest, covenants, capacity, maturity, and runway/funding gap. | Financing is a single raise amount with no instrument terms, debt capacity, or covenant logic. |
| Ownership | Reconciles founders, option pool, employees, investors, converts, warrants, secondary, and new rounds to 100.00%. | Dilution is directional only; holder classes do not sum cleanly or ignore converts/options. |
| Pricing | Connects customer ROI/value capture, cost-plus floor, willingness-to-pay evidence, margin, sales friction, and validation tests. | Price is copied from management target without value, cost, or evidence triangulation. |
| Financing | Shows raise need, timing, runway, downside gap, source of funds, use of funds, dilution, debt/lease/grant capacity, and milestone coverage. | Funding need is not tied to runway, milestone plan, or scenario pressure. |
| Exit Waterfall | Converts exit EV/equity value into proceeds by instrument, preference, debt, secondary, option pool, founder, and investor return. | Exit value is shown without proceeds waterfall or return math. |
| Segments | Defines segment economics, source status, intercompany/NCI/tax handling where relevant, and consolidation bridge. | Segment labels exist but each segment uses the same blended assumptions. |
| KPI | Selects KPIs from the economic mechanism and decision, defines formula, applicability, source context, downside trigger, and IC implication. | Generic SaaS KPIs appear when they do not affect the decision or mechanics. |
| Scenarios | Coherent cases move linked drivers together and show outputs, breakpoints, decision implication, and DD action. | Downside/base/upside are unrelated scalar shocks without narrative cause. |
| Sensitivity | Axes come from high-impact weak evidence, are anchored to a scenario, and show the output and threshold that changes the decision. | Decorative 2D grid using arbitrary volume x price defaults. |
| Valuation | States method credibility, exclusions, scenario range, DCF/multiple/SOTP bridge where relevant, and investor/founder return support. | Averages methods blindly or applies a revenue multiple without quality, margin, or risk context. |
| Market Support | TAM/SAM/SOM, reachability, source freshness, plan-to-market bridge, and gaps tie market evidence to assumptions. | Market size is a headline number with no source freshness or connection to revenue drivers. |
| Benchmarks | Each benchmark has source id, type, period, applicability limits, freshness, linked assumption/KPI, and refresh need. | Fake or stale source labels appear without applicability limits or linked driver. |
| IC Memo | Gives recommendation, KPI readout, what must be true, downside triggers, valuation support, financing/ownership implication, DD questions, and source boundary. | Memo summarizes tabs instead of making an investment judgment. |

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

1. Guide and Kernel define the decision, evidence, mechanics, and scope.
2. Assumptions and Driver Tree select the material variables.
3. Operating schedules calculate revenue, cost, people, assets, cash, capital,
   and ownership from those variables.
4. KPI, scenario, sensitivity, valuation, market support, and benchmarks test
   the weak links.
5. IC Memo converts the model into recommendation, risks, and diligence action.

If this flow is broken, repair the model structure before polishing formatting.
