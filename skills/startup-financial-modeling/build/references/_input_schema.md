# YAML input schema (`--input`)

The `--input` route to `build_model.py` accepts a YAML mapping that
overrides the kernel's narrative-derived primitives before derivation
runs. Every key below is optional; an unspecified key falls back to the
profile / narrative default and the resulting field is tagged with
`evidence_status` so the audit and the workbook surfaces flag it as
inferred rather than stated.

Field semantics mirror `economic_kernel.SourceFacts`. Series-typed
fields accept a list of length `periods`; a shorter list is right-padded
with its last value (so a single scalar passed as `[0.78]` reads as a
flat 78% across the plan).

## Identity / scope

| Key | Type | Default | Notes |
|---|---|---|---|
| `company`, `company_name` | str | `"Startup"` | Plan title and IC-memo identifier |
| `mechanics`, `business_model`, `model_type` | str | `"generic startup"` | Used when no narrative is supplied; the profile selector still runs on the synthesized narrative |
| `source_text`, `narrative`, `story`, `memo`, `description` | str | empty | If present, full mechanic / price / churn extraction runs on it |
| `periods`, `horizon_periods`, `horizon` | int (or `"3 years"`) | from narrative or 5 | Capped at `MAX_FORECAST_PERIODS` |
| `grain`, `model_grain` | `"annual" \| "quarterly" \| "monthly"` | inferred | Drives period labels and ramp shapes. Known limitation: kernel economics (recurring ×12, D&A ×12/life) are annualized per period — treat non-annual grains as label/ramp devices and validate any monthly/quarterly cash figures before investor use |
| `start_year`, `fiscal_year` | int | inferred | Fiscal-year anchor |
| `period_labels` | list[str] | inferred | Overrides the auto-built `FY2026 / Q1 26 / Jan-26` labels |
| `currency` | str | `"JPY"` | Auth source of truth for `money_scale` |
| `jpy_per_usd`, `fx_rate` | float | `DEFAULT_JPY_PER_USD` | Used when `currency != "JPY"` |
| `segments` | list[str] | from profile | Free-form segment names |
| `unknowns` | list[str] | from narrative | Audit / IC-memo surface |

## Demand drivers

| Key | Type | Default | Notes |
|---|---|---|---|
| `customers` | list[int] | profile ramp | **K1 input fidelity** (Task 2.2): when pinned, drives recurring revenue's installed base directly via `_facts_installed_base(facts)`. Sets `facts.customers_pinned = True`. |
| `new_units` | list[int] | inferred from `customers` or ramp | Pins the demand ramp; if absent but `customers` is set, the new-unit series is inverted from `customers`. Also sets `customers_pinned = True`. |
| `churn_rate` | float | `0.08` (or `0.18` for marketplace) | **K2** (Task 2.2): when present, flows into `ending_units(new_units, churn_rate=…)` in the fallback path |
| `gmv_yen`, `gmv` | list[int] | profile default; forced to `[0]` when `profile.key != "marketplace"` | **K5** (Task 2.4): off-mechanics suppression makes this marketplace-only |
| `take_rate`, `take` | list[float] (or %) | `0.0` when not marketplace | **K5** (Task 2.4): same suppression |

## Monetization

| Key | Type | Default | Notes |
|---|---|---|---|
| `monthly_price_yen`, `monthly_price` | list[int] | extracted price × period ramp | Per-customer recurring price under `recurring` mode; per-unit sale price under `unit_sale` |
| `target_gross_margin` | list[float] (or %) | profile default | Anchors `calibrate_cost_stack_to_gross_margin` |
| `revenue_mode` | `"recurring" \| "unit_sale"` | inferred | One-shot sale plans set this to `unit_sale` |

## Cost stack (calibrated to `target_gross_margin`)

| Key | Type | Notes |
|---|---|---|
| `variable_cogs_pct`, `variable_cogs` | list[float] (or %) | Percentage-of-revenue COGS slice |
| `delivery_cost_yen`, `delivery_cost` | list[int] | Field-service / install per-unit per-month |
| `cloud_cost_yen`, `cloud_cost` | list[int] | Infrastructure per-unit per-month |
| `support_cost_yen`, `support_cost` | list[int] | Per-customer support per-month |
| `capex_per_unit_yen`, `capex_per_unit` | list[int] | Hardware deploy cost |
| `avg_comp_yen`, `avg_comp` | list[int] | Loaded annual comp per FTE |

## Headcount / OpEx

| Key | Type | Notes |
|---|---|---|
| `product_headcount`, `gtm_headcount`, `operations_headcount`, `ga_headcount` | list[int] | Per-function FTE plan |
| `sm_pct_revenue` | list[float] (or %) | Sales & marketing as percent of revenue |
| `rd_program_per_product_fte_yen` | list[int] | Non-people R&D per product FTE |
| `rd_program_floor_yen` | list[int] | Minimum R&D program spend |
| `ga_pct_revenue` | list[float] (or %) | G&A as percent of revenue |
| `fixed_ga_yen` | list[int] | Fixed G&A floor |

## Financing

| Key | Type | Notes |
|---|---|---|
| `beginning_cash_yen`, `beginning_cash` | int | Opening cash balance |
| `equity_raise_yen` | list[int] | Per-period rounds. Period 0 honored as stated; follow-ons still auto-sized to keep cash solvent |
| `stated_first_round` | int | Convenience alias for `equity_raise_yen[0]` |
| `stated_post_money` | int | Period-0 post-money valuation |
| `debt_raise_yen` | list[int] | New debt drawn per period. Stated schedules replace the auto debt plan and feed sizing |
| `debt_interest_rate` | list[float] (or %) | Per-period interest rate on the debt + convertibles + lease balance |
| `debt_amortization_yen`, `debt_amortization` | list[int] | Contractual principal repayments; balance = cumulative drawn − cumulative repaid, interest accrues on the declining balance (K3) |
| `grants_yen` | list[int] | Non-dilutive cash; adds to ending cash and reduces auto-sized equity (K3). Simplified BS treatment: credited to contributed capital (visible as its own Financing row), not routed through P&L income |
| `convertibles_yen`, `lease_financing_yen` | list[int] | Join the interest-bearing balance; add to ending cash and reduce auto-sized equity (K3). Conversion dilution is a cap-table concern (Ownership / cap_table), not modeled in the debt balance |
| `customer_advances_yen` | list[int] | Deferred-liability level per period; shifts cash timing via working capital, not funding (K3) |
| `secondary_yen` | list[int] | Company-funded shareholder liquidity (share redemption / facilitated buyback): subtracts from ending cash and contributed capital, and must pair with a concurrent equity round (K3 audit). A pure investor-to-shareholder secondary has zero company cash impact — leave this 0 and model it as ownership transfer in the Ownership sheet |
| `onboarding_months` | float or list[float] | One-time onboarding fee = price × months (recurring plans). Unstated → 3-month default, labeled `placeholder` on Assumptions (F) |
| `one_time_revenue_per_unit_yen` | list[int] | Direct per-unit one-time fee; overrides the onboarding-months path (F) |
| `nol_yen` | list[int] | Opening NOL balance. Period-0 value feeds `project_free_cash_flow(opening_nol_yen=…)` |
| `tax_rate` | list[float] (or %) | Statutory tax rate per period |

## Working capital

| Key | Type | Notes |
|---|---|---|
| `ar_days` | list[int] | Days-sales-outstanding |
| `ap_days` | list[int] | Days-payable-outstanding |
| `deferred_revenue_share` | list[float] (or %) | Revenue billed but not yet recognized |
| `inventory_wip_pct_capex` | list[float] (or %) | Working capital tied up in WIP |
| `depreciation_life_months` | list[int] | Straight-line depreciation life |

## Valuation

| Key | Type | Notes |
|---|---|---|
| `revenue_multiple`, `gross_profit_multiple`, `ebitda_multiple` | list[float] | Comparable multiples |
| `discount_rate` | float | WACC for DCF |

## Audit invariants (spec.md §3 K-set)

The values above flow through these audit gates in
`audit_economic_coherence`. A breakdown that violates any of them is
returned as a `[…]` issue and `--strict-audit` refuses to ship:

- **K1** — when `customers` is pinned, the new-unit rollforward must
  land at a similar order of magnitude (ratio 0.25 ≤ implied / stated ≤ 4).
  Otherwise capex / headcount / funding are sized for a different customer
  base than the one the plan claims to serve.
- **K2** — `churn_rate` flows into `ending_units` in the fallback path
  (and downstream into the revenue projection), so changing it must move
  the terminal fleet and ARR.
- **K3** — stated grants / convertibles / lease / advances / secondary /
  debt reach the FCF projection and the equity-round sizing (never a
  post-derivation display override); convertibles and lease accrue
  interest with debt; secondary scheduled without a concurrent equity
  round is flagged.
- **K4** — cumulative cash tax must not exceed
  `max(tax_rate) × max(0, cumulative EBT)`. Earlier-period losses
  accumulate in an NOL balance that absorbs later positive taxable
  income.
- **K5** — a non-marketplace profile must emit `gmv_yen = [0]` and
  `take_rate = [0]` to facts; surfacing a transaction-revenue row on a
  hardware deck is a generator regression.

## Notes on partial inputs

- A single YAML key that pins a series sets the structured-input flag
  (`prims.demand_pinned` / `facts.customers_pinned`) and bypasses the
  narrative-scale retargeting step. Mix and match: pin `customers`
  while leaving `monthly_price_yen` to the narrative-extracted figure.
- Percentages can be written as either `0.78` or `78` — the loader
  treats values `> 1.5` as percent-of-100.
- Money fields are raw base-currency values (yen for `currency: JPY`).
  Display scale (`百万円`, `JPY M`) is applied by the workbook, not by
  the input loader.
