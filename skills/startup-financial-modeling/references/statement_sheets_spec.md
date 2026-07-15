All research complete. Here is the spec.

---

# STATEMENT Sheet Quality Spec — Private-Company Operating Model (IB/FAS Grade)

Scope: P&L, Cash Flow, Working Capital, Headcount, Opex cost-build sheets of a growth-company operating model. Feeds a model-generation engine. Standards synthesized from the FAST Standard, ICAEW Financial Modelling Code, Wall Street Prep, CFI, Macabacus, and model-audit practice (Gridlines, dbrown, ZAFtool).

## 0. Global conventions (apply to every sheet)

- **Uniform time ruler**: identical column-per-period grid on all sheets, same start column, same periodicity; period headers (label, period-end date, FY flag) linked from one timeline block. Mixed monthly/annual on one grid is a break — annualization happens in a dedicated annual view, never inline.
- **One calculation per row**; a row is one item with one formula filled uniformly across all periods. No formula changes mid-row.
- **Sign convention declared once and labeled per row** (recommend: revenue/inflows positive, costs shown positive within cost blocks and negated only at statement subtotals). ICAEW: label the convention next to values.
- **No daisy chains**: link only to the original source cell, never to a cell that itself is a link.
- **No plugs, no hardcodes in calc rows**: every constant lives on the assumptions sheet (blue font); calc rows are black formulas.
- **Units column** on every row (円/千円/人/%/ヶ月); unit changes between linked rows require an explicit conversion row.

## 1. Cost build architecture (Opex sheet)

Decompose every cost into exactly one of five driver classes; the class is a labeled column:

1. **Headcount-driven**: FTE (from Headcount sheet) × loaded cost, or per-head rate (PC/tools/recruiting per FTE).
2. **Volume-driven**: units/orders/customers × per-unit rate (support cost per ticket, hosting per customer).
3. **Revenue-linked**: % of the *specific* revenue stream (sales commissions, payment fees, revenue share) — never % of total revenue.
4. **Stepped/fixed**: tier table keyed to a capacity driver (rent tiers by headcount band, license tiers).
5. **One-time**: dated events (office move, audit setup) flagged `one-time` so EBITDA can be shown ex-items.

Required blocks:
- **Driver → P&L mapping matrix**: every cost row carries {driver class, P&L category (COGS/S&M/R&D/G&A), recurring flag}. P&L category totals are SUMIFs over this matrix — the P&L never re-derives costs.
- **Contribution view**: per revenue stream, revenue − variable COGS − revenue-linked costs = contribution margin, before shared/fixed opex (管理会計の限界利益に対応).
- **%-of-revenue policy**: acceptable only for immaterial residual lines (<~5% of opex each) with the % benchmarked to history; a red flag when applied to headcount-heavy lines (S&M, R&D) or when it makes costs scale linearly with revenue with no capacity logic. Investors read blanket %-of-revenue opex as "budget, not plan."

## 2. Headcount sheet

- **Hiring plan table**: one row per role (or role×cohort): function, level, start period, base salary, count. FTE per period = count × in-period weighting (start-month proration: 0.5 default for mid-month starts, or day-count).
- **Attrition/backfill**: annual attrition % by function → monthly leave rate; backfill with configurable lag (e.g. 2 months vacancy). Net FTE corkscrew: opening + hires − leavers = closing.
- **Loaded cost**: base × (1 + burden %: social insurance ~15–16% JP / 25–40% US) + per-head recurring (tools, office) + per-hire one-time (recruiting fee % of base, equipment).
- **Ramped productivity**: revenue-generating roles (sales) carry a ramp vector (e.g. 0/33/66/100% of quota over 4 months); capacity model can back-solve required reps from bookings targets.
- **Sanity rows (alert checks)**: span of control (ICs per manager 5–8), revenue per FTE, personnel cost as % of opex (SaaS norm 60–80%).
- **Dual mapping**: each role maps to COGS (delivery/CS engineers) or an opex function, feeding the §1 matrix — headcount must reconcile: Σ mapped FTE = total FTE (check).

## 3. P&L sheet

Line hierarchy for a growth company:

```
Revenue by stream → Total revenue (+ YoY % row)
COGS by stream → Gross profit by stream + total (+ GM % rows)
[Contribution margin per stream — optional block, from §1]
Opex by function: S&M / R&D / G&A (+ % of revenue rows each)
EBITDA (+ margin %) ← headline for growth cos (pre-profitability)
D&A → Operating income (営業利益)
Non-operating / interest → 経常利益 → Pre-tax → Tax → Net income
```

- **Ratio rows** interleaved, formatted %, never on the same row as values.
- EBITDA leads while the company is pre-profit / cash-burn stage; operating income leads once D&A is material or for JGAAP audiences.
- **Stock comp & one-timers**: shown as separate labeled rows; EBITDA presented both reported and adjusted — never silently netted.
- **JGAAP vs 管理会計**: keep the JGAAP shell (売上総利益/販管費/営業利益/経常利益) as the statutory view; the 管理会計 view (変動費/固定費 → 限界利益) is a separate presentation block fed from the same driver rows, not a second calculation.

## 4. Cash flow & working capital

- **CF = indirect method starting from net income** (not EBITDA-start shortcuts): NI + D&A + stock comp ± Δworking-capital ± Δdeferred revenue = operating CF; then investing (capex from schedule), financing (equity/debt draws). Every CF line references a schedule — nothing computed on the CF sheet itself (WSP rule).
- **Corkscrew template** (all balance-sheet items):

```
Opening balance   = prior closing
(+) Additions     ← driver-linked flow
(−) Releases      ← driver-linked flow
Closing balance   → BS; Δ → CF
```

- **Corkscrews required** for: deferred revenue (billings + − revenue recognized), PP&E/intangibles per asset class (capex + − depreciation, straight-line by useful life; fully-depreciated cutoff), debt (draw + − repayment; interest on opening balance to avoid circularity), equity/retained earnings (NI − dividends).
- **Days-ratio shortcuts acceptable** for AR (DSO × revenue/365), AP (DPO × COGS/365), inventory (DIO) *when* the balance is a passive by-product of trading — but still present them in corkscrew layout (opening/Δ/closing) so BS and CF tie mechanically. Prepaid subscriptions billed annually must use a true corkscrew, not DSO.
- **Minimum cash & revolver (optional module)**: cash floor input; shortfall → revolver draw, surplus → sweep repayment (`MAX/MIN` logic); interest on opening balance — no iterative calc. If no debt: a "cash-out month" alert row instead.
- FX: skip for single-currency (JPY) models; note the assumption on the assumptions sheet.

## 5. Checks architecture

Three check classes (FM-magazine/ICAEW taxonomy), each row returning 1/0 with tolerance (e.g. ±1円):

- **Error checks (must be zero to ship)**: BS balances every period; every corkscrew closing = next opening; CF closing cash = BS cash; Σ stream revenue = total; Σ mapped costs = Σ opex sheet; Σ mapped FTE = total FTE; no #REF!/#DIV0 (ISERROR sweep); retained earnings rollforward ties to NI.
- **Alert checks (review, may ship)**: negative cash, GM% outside band, revenue/FTE outliers, span-of-control breach, opex line >20% YoY jump, one-time items in terminal year.
- **Sensitivity checks**: flag when scenario selector ≠ base case.
- **Surfacing**: per-sheet check block at top of each sheet; dedicated Checks sheet listing every check with hyperlink to source; single master flag = MAX(all checks), displayed in the frozen header of every sheet, conditional-formatted red on breach. Errors and alerts are visually distinct (red vs amber).

## 6. 60-point vs 95-point: audit-grade checklist

Failure modes (what auditors flag):
- [ ] Balancing **plugs** or hardcoded BS balances anywhere
- [ ] %-of-revenue used for headcount-heavy opex; costs with no named driver
- [ ] Mixed timing conventions (monthly ops on annual grid; interest on average balance creating circularity)
- [ ] Daisy-chained links; formulas that change mid-row; overwritten cells in calc ranges
- [ ] Unlabeled unit breaks (千円 feeding 円), missing sign labels
- [ ] CF built by differencing the BS with manual fudges; deferred revenue absent for prepaid-billing businesses
- [ ] Checks exist but no master flag, or checks reference the same cell they test

Hallmarks of 95-point sheets:
- [ ] One timeline, one calc per row, every constant an input, every balance a corkscrew
- [ ] Driver→P&L mapping matrix makes every yen traceable input→driver→statement in ≤3 hops
- [ ] Headcount reconciles to both COGS and opex; loaded cost and ramp explicit
- [ ] P&L reads as the equity story: streams → GM by stream → contribution → functional opex → EBITDA, with ratio and YoY rows
- [ ] Full check suite green, master flag on every sheet, error/alert distinction respected

## Sources

- FAST Standard — corkscrews, structure, checks: https://fast-standard.org/the-fast-standard/ (full PDF: FAST-Standard-02c)
- ICAEW Financial Modelling Code (sign conventions, master check, tolerances): https://www.icaew.com/-/media/corporate/files/technical/technology/excel/financial-modelling-code.ashx and error-check article: https://www.icaew.com/technical/technology/excel-community/excel-community-articles/2021/intro-to-financial-modelling-part-12
- FM Magazine — 3 types of checks (error/sensitivity/alert, master flag): https://www.fm-magazine.com/issues/2025/mar/excel-modelling-how-to-implement-3-types-of-checks/
- Wall Street Prep — 3-statement build order, schedules, revolver, no-hardcode CF: https://www.wallstreetprep.com/knowledge/build-integrated-3-statement-financial-model/ and revolver: https://www.wallstreetprep.com/knowledge/modeling-revolving-credit-line-excel-free-template/
- CFI — supporting schedules & model audit: https://corporatefinanceinstitute.com/resources/fpa/supporting-schedules-financial-modeling/ , https://corporatefinanceinstitute.com/resources/financial-modeling/model-audit/
- Macabacus — working capital days ratios & cash sweep: https://macabacus.com/operating-model/working-capital , https://macabacus.com/operating-model/revolver-cash-sweep
- F1F9 — modelling balances (corkscrew mechanics): https://www.f1f9.com/blog/model-balances-excel/
- Investment Banking Analysts — WC rollforward structure: https://investmentbankinganalysts.com/modeling-working-capital-drivers-and-schedules-in-three-statement-models/
- Breaking Into Wall Street — CFO indirect method, NI vs EBITDA start: https://breakingintowallstreet.com/kb/accounting/cash-flow-from-operations/ ; debt schedule: https://breakingintowallstreet.com/kb/leveraged-buyouts-and-lbo-models/debt-schedule/
- Model audit checklists — dbrown: https://www.dbrownconsulting.net/blog/how-to-audit-review-financial-model , ZAFtool: https://www.zaftool.com/blog/how-to-audit-financial-model-excel/ , Gridlines: https://www.gridlines.com/blog/what-is-a-model-audit/
- Headcount/loaded cost — Glencoyne (1.25–1.4x burden): https://www.glencoyne.com/guides/fully-loaded-cost-us-employee , SaaStr/Janz quota-capacity plan: https://www.saastr.com/saas-financial-plan-2-0-from-christoph-janz/ , The SaaS CFO: https://www.thesaascfo.com/saas-startup-financial-model/
- Growth-co P&L reading — G Squared (opex by function, S&M dominance): https://www.gsquaredcfo.com/blog/investors-saas-p-and-l , Finro (intentional cost build): https://www.finrofca.com/news/financial-modeling-for-startups
- JGAAP/管理会計 presentation — ZEIKEN PRESS (管理会計PL・限界利益): https://www.zeiken.co.jp/zeikenpress/column/0011zp20210527/ , GLOBIS (人件費の原価/販管費区分): https://globis.jp/article/5440/ , J-Net21 損益計画: https://j-net21.smrj.go.jp/startup/manual/list5/5-2-8.html
