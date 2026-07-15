Research complete. Here is the implementable spec.

# ANALYSIS Layer Spec — Private-Company Plan Model (IB / Financial-Consulting Grade)

Scope: the four analysis surfaces (Summary, KPI & Unit Economics, Scenarios & Sensitivities, Valuation & Returns) that sit on top of the operating engine. Governing principle (FAST "Presentation" layer + ICAEW single-source rule): **every cell on these surfaces is a formula referencing the engine or the assumptions layer — zero retyped values, zero local hardcodes.** Inputs live once, in one place; analysis surfaces only read.

## 1. Summary / Dashboard sheet

One sheet, one screen-width, printable — the FAST ideal is a presentation page that "answers the original question": headline outputs, one small chart, scenario results, and the assumptions that drive them. Design test: a partner reads it in 5 minutes and can state trajectory, cash risk, financing need, and the bet — the same first-question discipline as an IC memo executive summary ("what are we approving, on what terms, why").

Required blocks (top to bottom):
1. **Header strip** — company, model version/date, active scenario name (formula-linked to the switch cell, e.g. `="Scenario: "&INDEX(ScenarioNames,Switch)`), master-check status cell (`=IF(AllChecksOK,"OK","ERROR")` with red conditional format).
2. **Headline P&L trajectory** — 5–7 rows (Revenue, YoY %, Gross profit/%, EBITDA/%, Net income) × plan years, all `=` links to PL sheet.
3. **Cash & runway** — ending cash by year, minimum cash balance and its month/year (`=MIN(CashRow)` + `INDEX/MATCH` for timing), months of runway at current burn, pre-financing cumulative funding need.
4. **Financing plan** — round timing, amount, pre/post-money, cumulative dilution — links to Cap Table.
5. **Case comparison table** — Base/Upside/Downside side-by-side on 4–6 headline outputs (see §3 mechanism).
6. **Target tie-out block** — every externally stated target (e.g. "ARR ¥X by FY28", "EBITDA-positive in FY27") as: stated value (input) | model value (formula) | delta | ✓/✗ check.
7. **Charts (max 2–3, data-linked, never pasted)** — revenue build stacked by segment, and cash balance line with min-cash point marked. Sparse: charts only where shape carries information (WSP: outputs sheet = summary + executive summary + charts fulfilling the model's purpose).

## 2. KPI & Unit Economics sheet

All metrics computed from engine rows; each metric row carries: value by year | benchmark band | evaluation formula (`=IF(val<=good,"◎",IF(val<=ok,"○","△"))` style — text verdict, not color-only).

- **Growth & retention**: ARR/revenue growth %, NRR/GRR (only if churn is modeled), logo count.
- **Unit economics decomposition**: ARPU/price per unit → variable cost per unit → contribution per unit and margin; CAC (fully-loaded S&M / new customers); CAC payback in months (benchmark: ~12–18 mo mid-market, ≤24 enterprise; median B2B ~15 mo); LTV:CAC (≥3x floor, 4x+ healthy).
- **Efficiency scores, staged by maturity**: Burn multiple = net burn / net new ARR (≤1.0x elite, 1–1.5x good at growth stage; 2.5x+ tolerated only at seed) — show only while burning. Rule of 40 (growth % + FCF margin ≥ 40) — introduce once revenue scale makes growth % meaningful (~$5M+), label "reference" before that.
- **Cohort metrics deferral rule**: with no actuals, do NOT fabricate cohort curves. State the retention assumption as a single driver, mark cohort/NDR analysis "populate from actuals," and keep a placeholder structure. Investors read invented cohort tables as a credibility flag.
- Benchmark values are **inputs with source labels** (a16z/Kruze/OpenView-style benchmarks), not hardcodes inside formulas.

## 3. Scenario architecture (formula-level spec)

Professional standard = **single-model, central-switch** design. Never fork the model into per-scenario sheets or copies — forks desynchronize immediately and are the classic audit failure; one calculation engine, scenario differences expressed only as alternative input columns (WSP, FMI, FE Training all teach the switch pattern; FAST's single-source rule prohibits duplicated logic).

- **Switch cell**: one named input cell `Switch` (1/2/3), data-validated dropdown, styled as input (blue font/yellow fill per Wall Street convention), placed on Assumptions and mirrored (by formula) on Summary.
- **Scenario table**: on the Assumptions sheet, a block with one row per scenario-varied driver (pick 5–15 that matter: growth/win rate, pricing, churn, gross margin, hiring pace, CAC…), columns = Base | Upside | Downside. Live value column: `=INDEX(BaseCol:DownCol, Switch)` or `=CHOOSE(Switch, Base, Up, Down)` — INDEX over a contiguous 2-D block scales best; nested IFs are prohibited (unauditable). All engine formulas reference **only the live column**.
- **Definitions discipline**: Downside = operationally coherent stress (slower sales cycle, higher churn, delayed hires), not "Base × 0.8" on every line. Upside must cost money (more CAC/headcount to buy more growth). Document each scenario's narrative in one line next to the table.
- **Side-by-side case summary without data tables**: a static case-comparison table (cases × 4–6 outputs) on Summary. Since Excel data tables are disallowed (calc-mode/recalc hazards — Excel defaults to "Automatic Except Data Tables" precisely because they're fragile), the standard fallback is: values are **snapshot-pasted per case and date-stamped**, OR (preferred for a generation engine) computed live by running the scenario deltas through lightweight duplicate formulas for headline lines only (revenue/EBITDA/min-cash per case as direct formulas off the scenario table — a "mini-engine" for 3–5 outputs, clearly boxed and labeled, never a full model fork).
- **First Chicago (VC context)**: probability weights per case (inputs summing to 100%, with a `=SUM=1` check) × per-case exit equity value → expected value row. Present as a supplement to, never a replacement for, the three discrete cases.
- **Switch integrity check**: a check cell verifying `Switch∈{1,2,3}` and that the live column equals the selected case column (`SUMPRODUCT` delta = 0).

## 4. Sensitivity standards

All sensitivity surfaces are **explicit formula grids** (no `TABLE()` arrays): each cell recomputes the target metric from a compact closed-form or mini-chain off the drivers — this keeps the workbook recalc-safe and portable.

- **2-way grids (2–3 tables)**: canonical pairs — growth × gross margin → EBITDA or equity value; exit multiple × exit year → IRR/MOIC; price × churn → runway or min cash. Row/column headers as absolute driver values (not "+10%") centered on the Base value. **Mid-cell tie-back check**: the center cell must equal the Base-case model output (`=IF(ABS(center−model)<tol,"OK","TIE-OUT FAIL")`).
- **1-way strips**: single driver × 5 steps → one output; use where a 2-way adds nothing.
- **Tornado / driver-impact ranking (consulting style)**: flex each of the 8–12 key drivers ±10% (or ± its plausible range) one at a time, record impact on **EBITDA (or terminal-year cash)**, rank by absolute swing, largest on top. In xlsx: a ranked table (driver | low impact | high impact | swing) plus a data-linked horizontal bar chart. Purpose: tells management which assumptions deserve diligence — the ranking table is the deliverable, the chart is decoration.
- **Which outputs to sensitize** (pick per model purpose, ≤4): EBITDA (terminal year), minimum cash / cash low point, equity value, investor IRR/MOIC.

## 5. Valuation & Returns integration

- **Separation**: valuation sits on its own sheet(s), **fed only by bound engine outputs** (revenue/EBITDA/FCF rows) — never re-forecasting inside the valuation sheet. Changing the scenario switch must flow through to valuation automatically.
- **Methods & football field**: 2–4 methods (revenue/EBITDA multiples on exit-year metrics; DCF only if cash flows support it; last-round reference). Football field = floating-bar chart of per-method ranges; each bar's low/high must trace to a stated assumption pair (e.g. multiple range 4–8x, or the DCF WACC±100bps / g-range corners of a sensitivity grid). No bar without a labeled source; the chosen range is a judgment call annotated on the sheet.
- **Returns chain**: exit enterprise value → net debt bridge → equity value → **waterfall** (liquidation preferences, option pool, per-class allocation from Cap Table) → per-investor proceeds → MOIC and IRR (`=(proceeds/invested)^(1/years)−1` or XIRR on dated flows).
- **Credible vs promotional** — the returns page must show: (a) MOIC/IRR under **all three cases including Downside** (does the investor get money back if the plan slips?); (b) **dilution disclosure** — returns net of modeled future rounds, with ownership % walked from entry to exit; (c) exit multiple × exit timing sensitivity grid on IRR; (d) probability-weighted expected return (First Chicago) where VC-facing. A returns page showing only the Base/Upside case is promotional by construction.

## 6. 60→95 separators (analysis layer)

Failure modes (caps a model at ~60):
- Orphan dashboard: retyped/pasted values that drift from the engine.
- Scenario sheets that fork the model (three copies of the P&L).
- Sensitivity tables that don't recalc (dead `TABLE()` arrays, stale pastes with no date stamp, mid-cell ≠ model output).
- Vanity KPIs: LTV:CAC with fabricated retention, Rule of 40 at pre-revenue, cohort tables with no actuals.
- Targets stated in the deck that the model never reproduces.
- Downside case = uniform haircut; returns shown only for Base/Upside.

Hallmarks (95):
- All-formula surfaces; single-source inputs; blue-input/black-formula convention.
- Scenario switch with integrity check; every check rolled into one master flag visible on Summary.
- Sensitivity mid-cells tie back to Base within tolerance (automated check cells).
- Downside survivability explicit: min cash, runway, and covenant/financing implication under Downside on the Summary.
- Every stated target has a tie-out row with ✓/✗.
- KPI verdicts against sourced benchmark bands; metrics staged to company maturity.
- Returns shown with dilution, downside case, and exit-timing sensitivity.

## Quality checklist (engine gate)

1. `COUNT` of hardcoded constants on Summary/KPI/Valuation sheets = 0 (excluding labels/benchmark inputs).
2. Toggling Switch 1→2→3 changes Summary headline, valuation, and returns without any manual step.
3. Case-comparison table: refresh method documented; if snapshot, date-stamped.
4. Every sensitivity grid center cell = live model value (check cell OK).
5. Tornado ranking sums correctly and drivers match the scenario table's driver list.
6. All charts data-linked; deleting no chart breaks any formula.
7. Master check = OK in all three scenarios.
8. Tie-out block: all stated targets ✓ (or explicitly flagged with reason).
9. Returns page shows Downside MOIC and post-dilution ownership.
10. Probability weights (if used) sum to 100% with check.

## Sources

- Wall Street Prep — [Financial Modeling Guide](https://www.wallstreetprep.com/knowledge/financial-modeling/), [Scenario Analysis lesson](https://www.wallstreetprep.com/knowledge/financial-modeling-techniques-selecting-operating-and-financing-scenarios/), [Sensitivity (What-If) lesson](https://www.wallstreetprep.com/knowledge/financial-modeling-techniques-sensitivity-what-if-analysis-2/), [First Chicago Method](https://www.wallstreetprep.com/knowledge/first-chicago-method/), [Football Field](https://www.wallstreetprep.com/knowledge/football-field-valuation-real-example-excel-template/)
- FAST Standard — [The FAST Standard](https://fast-standard.org/the-fast-standard/); Gridlines — [What is FAST Financial Modelling](https://www.gridlines.com/blog/fast-financial-modelling/), [Financial Modelling Tips](https://www.gridlines.com/blog/financial-modelling-tips/)
- FMI — [How to Create a Scenario Switch](https://fminstitute.com/modeling-resources/how-to-create-a-scenario-switch-in-excel/), [Scenario Manager](https://fminstitute.com/modeling-resources/scenario-manager-excel/); FE Training — [CHOOSE for Scenario Analysis](https://www.fe.training/free-resources/excel/choose-function-formula-scenario-analysis/)
- Macabacus — [Football Field Chart in Excel](https://macabacus.com/blog/build-football-field-chart-excel); BIWS — [Football Field Valuation](https://breakingintowallstreet.com/kb/excel/football-field-valuation/)
- Tornado method — [Equitest DCF Tornado Chart guide](https://www.equitest.net/what-is-a-dcf-tornado-chart-a-complete-guide-to-sensitivity-analysis-in-business-valuation.html), [Onetribe Advisory sensitivity analysis](https://www.onetribeadvisory.com/knowledge-hub/sensitivity-analysis-financial-planning/)
- KPI benchmarks — [Fiscallion SaaS unit economics](https://www.fiscallion.io/blog/saas-unit-economics), [SaaS Mag capital efficiency 2026](https://www.saasmag.com/saas-capital-efficiency-metrics/), [CFO Advisors Series A board KPI benchmarks](https://cfoadvisors.com/blog/2026-series-a-board-deck-kpi-benchmarks)
- IC memo standards — [The VC Factory IC Memos](https://thevcfactory.com/investment-committee-memos/), [Visible.vc Investment Memo](https://visible.vc/blog/investment-memo/)
- Credibility of projections — [Finro: what investors look for](https://www.finrofca.com/news/startup-financial-projections), [Graphite: projections that withstand scrutiny](https://graphitefinancial.com/blog/building-financial-projections-investor-scrutiny/)
- Data-table recalc hazards — [Becker one-way data tables](https://www.becker.com/blog/accounting/dr-winstons-excel-tip-sensitivity-analysis-with-one-way-data-tables), [EngineerExcel data tables](https://engineerexcel.com/design-sensitivity-analysis-excel-data-tables/)
