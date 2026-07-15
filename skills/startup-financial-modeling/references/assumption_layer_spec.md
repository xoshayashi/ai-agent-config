All research complete. Here is the implementable spec.

---

# Assumption-Layer Specification for Model Generation Engine

Reference contract distilled from the FAST Standard v02a ([fast-standard.org PDF](http://www.fast-standard.org/wp-content/uploads/2015/03/FASTStandard_02a.pdf)), the [ICAEW Financial Modelling Code](https://www.icaew.com/-/media/corporate/files/technical/technology/excel/financial-modelling-code.ashx), [Wall Street Prep](https://www.wallstreetprep.com/knowledge/income-statement-forecasting/), [Forvis Mazars model audit](https://financialmodelling.forvismazars.com/forvis-mazars/financial-model-audit/), and driver-based planning literature ([CFI](https://corporatefinanceinstitute.com/resources/fpa/driver-based-planning-guide/), [KPMG](https://kpmg.com/us/en/articles/2023/innovate-fp-and-a-driver-planning.html)).

## 1. Layer architecture (non-negotiable rules)

1. **Inputs → Calculations → Outputs, strictly one-way.** No input lives on a calculation sheet; no calculation lives on the assumptions sheet (ICAEW Code; FAST 2.04). The assumptions sheet contains *only* hardcoded values.
2. **No embedded constants in formulas** except universal ones (12 months, 1000s) — FAST 3.04-01. Every commercial number is a named, labeled input row.
3. **One line item per row; consistent formula across the row** — FAST 3.02-01 ("one of only a few universally accepted principles"). A reviewer checks only column F (constants) and the first series cell — FAST 2.01-03 "make only two columns matter".
4. **Each column has a single purpose** — FAST 2.01-01: dedicated columns for label, **units**, constants, then the time series. "A separate units column causes the question of units to be begged, never a bad thing."
5. **Constants vs series are separated** — FAST 3.01-01/3.01-03: a value that doesn't vary over time is entered once in the constants column, never copied across years.
6. **No purposeful circularity** — FAST 1.01-11. Pre/post quantities (e.g., bonus % of post-bonus profit) must be defined algebraically, not iteratively.
7. **Dedicated comments/source column on input sheets** — FAST 2.04-02; input sheets must be self-documenting (FAST 2.04-03: the model is its own data book).

## 2. Assumption register schema (fields per driver row)

Per [FE Training](https://www.fe.training/free-resources/financial-modeling/modeling-assumptions/), [CFI documentation guidance](https://corporatefinanceinstitute.com/resources/excel/documenting-excel-models-best-practices/), and model-audit practice of tying every input back to source documentation ([Forvis Mazars](https://financialmodelling.forvismazars.com/forvis-mazars/financial-model-audit/)):

| Field | Type | Rule |
|---|---|---|
| `id` | string | Stable key (e.g. `REV.SAAS.ARPU`); referenced by calc engine, never by cell address |
| `label` | string | Human name; balances say "balance", flows get display totals (FAST 3.05/3.01) |
| `unit` | enum | `JPY`, `JPY_k`, `%`, `count`, `months`, `x`, `per_unit` … Required; own column |
| `driver_tree` | ref | Parent P&L line + position in tree (e.g. `Revenue > SaaS > New ARR`) |
| `value_base / value_up / value_down` | number/series | Adjacent scenario columns (see §5) |
| `shape` | enum | `constant` \| `flat_series` \| `stepped` \| `ramp` \| `explicit_series` (see §4) |
| `evidence_basis` | enum | `actual` \| `contracted` \| `company_provided` \| `analyst_estimate` \| `benchmark` \| `placeholder` \| `back_solved` |
| `source` | string | Doc + locator syntax, e.g. `FY25 monthly TB`, `2024 AR Note 12 p.73`, URL |
| `as_of` | date | When evidence was current; register also carries `last_reviewed` |
| `rationale` | string | 1–2 sentence justification (comments column, FAST 2.04-02) |
| `confidence` | enum | `H/M/L` |
| `sensitivity_flag` | bool | TRUE if in top drivers by output swing (tornado-ranked, see §6) |
| `owner` | string | Who signs off the number (diligence models) |

**Grouping:** by driver-tree section mirroring calc-sheet chapters — Revenue / COGS / Opex / Headcount / Capex / WC / Financing / Tax / Macro (FAST 2.04-01: group by nature — constants vs series, actuals vs forecast — then by commercial area; FAST 1.02-04: functional chapters). Not alphabetical, not by scenario.

## 3. Driver decomposition patterns catalog

Standard: decompose until each leaf is a number someone can *evidence or own*; stop there. 10–15 drivers explain 80%+ of outcomes — more is maintenance cost, not accuracy ([CFI](https://corporatefinanceinstitute.com/resources/fpa/driver-based-planning-guide/), [Planful](https://planful.com/blog/what-is-driver-based-planning/)). Aggregate growth % is an *output* of the build, never an input, once you have a thesis on components ([WSP](https://www.wallstreetprep.com/knowledge/income-statement-forecasting/)). Presentation: FAST 2.02 calculation blocks — child driver rows (ingredients) listed directly above the parent calculation row, which is the last row of the block.

| Pattern | When to use | Standard row layout (top → bottom) |
|---|---|---|
| **Price × Volume** | Any transactional revenue; COGS as unit cost × volume | Volume (units) → Price/ARPU (¥/unit) → `= P × V` revenue. Segment-level if thesis differs by segment |
| **Funnel** | Sales-led / marketing-led acquisition | Top-of-funnel volume → conversion % per stage (each its own row) → wins → × ACV. Never multiply two conversion rates in one formula |
| **Stock-flow (installed base)** | Subscriptions, contracts, customers | Opening base → + adds → − churn (% of opening) → closing; use FAST corkscrew block (FAST 2.02-05). Revenue = avg base × ARPU |
| **Headcount-driven cost** | Payroll, and any cost scaling with people | HC by dept (FTE corkscrew: opening + hires − attrition) → avg fully-loaded cost/FTE → per-head opex ratios (PC, rent/FTE). Headcount is usually the largest cost driver ([CFI](https://corporatefinanceinstitute.com/resources/fpa/driver-based-planning-guide/)) |
| **Rate × Base** | Interest, tax, commissions, %-of-revenue opex | Base line (link from calc sheet) → rate (%) → product. Rule: rate must apply to a *money or unit base*, never to another rate |
| **Per-unit × Count** | Hosting/COGS per customer, support cost per ticket | Count driver (link) → cost per unit (¥) → product |

Ratios (% of revenue) are acceptable only for genuinely variable, non-thesis lines; anything with an operational story gets a primitive driver.

## 4. Time-series input conventions

- **Constant vs series discipline:** if a value is genuinely flat, it is a constant in the constants column (FAST 3.01-03) — do not paste it across years, because updating a copied row is error-prone. If it varies, it is a full series row with a value in every period (blue = overridable per year).
- **Stepped inputs:** enter the series explicitly per year (price rises, planned hires). Do not encode steps inside formulas with nested IFs (FAST 3.03-07); use flags/factors on the calc sheet if timing logic is needed (FAST 2.02-06).
- **Growth-rate drivers vs direct series:** derive from a growth-rate driver when the *rate* is the thesis (mature lines); input the series directly when the *level* is the evidence (bottoms-up capacity, signed contracts, hiring plan). Never both for the same line.
- **Ramps:** model as `% of steady state` per period (own input row, unit %) applied to a steady-state driver, or an S-curve (logistic/Gompertz) with named parameters — capacity K, growth rate, inflection — as three labeled inputs, not a buried formula ([SumProduct](https://sumproduct.com/thought/models-with-s-curves/), [Glencoyne](https://www.glencoyne.com/guides/production-forecasting-s-curve)). Hire-to-productivity ramps (e.g. 0→100% over 2–4 quarters) are an explicit row.
- **Back-solved targets:** acceptable — this is the reverse-DCF/backsolve pattern of asking "what must be true" ([WSP Reverse DCF](https://www.wallstreetprep.com/knowledge/reverse-dcf-model/)) — but only if (a) the solved value is pasted as a normal input with `evidence_basis = back_solved`, `source =` the target (e.g. "Y5 ARR ¥5bn per equity story"), (b) the target itself appears as a check row (`model output vs target`, ✓/✗), and (c) implied intermediates (implied win rate, implied reps) are displayed for reasonableness. A live Goal Seek/circular link to the target is prohibited (FAST 1.01-11). Undocumented back-solving is the failure mode; labeled back-solving is standard equity-story practice.

## 5. Scenario switch design

Standard IB/project-finance pattern ([FMI](https://fminstitute.com/modeling-resources/how-to-create-a-scenario-switch-in-excel/), [Pivotal180](https://pivotal180.com/creating-scenarios-in-an-excel-financial-model/), [Bodmer](https://edbodmer.com/scenario-analysis-with-index-and-data-table/), [WSP CHOOSE](https://www.wallstreetprep.com/knowledge/choose-function/)):

- One **active-case selector cell** (1=Base, 2=Up, 3=Down; data-validated dropdown), positioned at the top of the assumptions sheet and echoed on every output sheet header.
- Per scenario-driven assumption: three adjacent input columns (Base/Up/Down) plus one **live column** = `INDEX(base:down, switch)` or `CHOOSE(switch, …)`. Only the live column feeds calculations; FAST 3.03-06 mandates INDEX/CHOOSE over IF, and FAST 2.01-07.1 sanctions this vertical/columnar "scenario picking" layout.
- Not every assumption is scenario-varied. Flag `scenario_driven: true` only for sensitivity-flagged drivers; others carry one value used in all cases (blank Up/Down = inherits Base). Never maintain three model copies.
- Sensitivities (one-driver deltas for tornado/data tables) are separate from scenarios (coherent multi-driver narratives): implement sensitivities as additive/multiplicative flex inputs defaulting to 0%/1.00× on top of the active case.

## 6. Evidence labeling conventions

- **Color code (universal IB convention):** blue = hardcoded input, black = same-sheet formula, green = link from another sheet, red = external link/flag ([Macabacus](https://macabacus.com/blog/improving-model-readability-with-color-formatting), [WSO](https://www.wallstreetoasis.com/resources/financial-modeling/financial-model-color-formatting)). Publish the key in the model (FAST 2.05-05). Engine rule: a blue cell outside the assumptions sheet is a defect.
- **Provenance column** (`evidence_basis` + `source` + `as_of`, §2) is the register-level analogue: model audits verify inputs back to financing/legal/diligence documents ([Forvis Mazars](https://financialmodelling.forvismazars.com/forvis-mazars/financial-model-audit/)), so every input must name a checkable document. `placeholder` is a legal state but must be visibly styled (FAST 3.02-02: temporary code marked with square brackets + yellow shade) and listed on the open-items log.
- Maintain a **"model qualifications and weaknesses" list** in the workbook — FAST 2.06-02: undocumented implicit assumptions "may be construed as nothing more than 'serious model error'".

## 7. Quality bar: 60-point vs 95-point assumptions layer

Failure modes (60-point):
- Hardcodes buried in formulas (`=B12*1.08`) — the most common defect found in review ([Alpha Apex](https://www.alphaapexgroup.com/blog/financial-modeling-mistakes); FAST 3.04-01).
- Aggregate growth % where a component thesis exists; **rates-on-rates** (growth applied to a margin, conversion × conversion in one cell).
- Missing units; % vs ¥ ambiguity (violates FAST 2.01-01 units column).
- **Orphan assumptions** (input rows nothing references) and **plugs** masking imbalances ([CFI](https://corporatefinanceinstitute.com/resources/financial-modeling/common-causes-imbalanced-3-statement-models/)).
- Flat values pasted across years as series; nested-IF step logic; circular pre/post definitions; scenario logic via three saved file copies; unlabeled back-solves.

Hallmarks (95-point):
- Every input: unit + evidence basis + source/as-of + rationale, zero exceptions; placeholders visibly flagged and counted.
- Driver trees mirror calc-sheet chapters; each parent line reconstructable from its children on sight (FAST 2.02 block structure).
- Sensitivity-flagged top drivers identified by tornado ranking (largest output swing first — [Bodmer](https://edbodmer.com/fundamentals-of-creating-a-tornado-diagram-and-creating-sensitivity-analysis/)), and effort/evidence concentrated there.
- Single scenario switch, INDEX-driven live column, active case echoed on outputs; check rows for back-solved targets; a maintained qualifications list; the input sheet readable as the model's own data book (FAST 2.04-03).

**Engine acceptance checks:** (1) no blue cells outside assumptions; (2) every register row referenced ≥1 time; (3) every row has unit + basis + source; (4) no rate applied to a rate; (5) scenario switch flows through INDEX only; (6) back-solved rows have a paired check row; (7) placeholder count surfaced on the summary sheet.
