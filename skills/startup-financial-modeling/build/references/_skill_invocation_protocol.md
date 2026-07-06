# Skill Invocation Protocol

This file preserves the full invocation, routing, workbook, design, analysis,
and closeout gates that should not live in the always-loaded `SKILL.md`.

## Reference Loading

References live in `build/references/`; load the smallest set that covers the
decision. Start with `_output_modes.md`, `_generic_composition_protocol.md`,
and `_self_review_protocol.md`. When a run reaches post-output closeout, a user
asks to improve a prior skill output, or logs show failed checks, repeated
workarounds, cleanup noise, or tool/routing inefficiency, load
`_self_improvement_protocol.md`; it routes to the reviewer-panel,
failure-mode, pruning, and closeout-consistency references only when that
learning path is active. Xlsx generation or repair also needs
`_layout_canonical.md`, `_ib_workbook_design_system.md`, and
`_sheet_quality_rubric.md`. Full plans, fundraising, DD, or investor outputs
draw from `_modeling_kernel.md`, `_coverage_universe.md`,
`_assumption_decomposition_patterns.md`, `_kpi_analytics.md`,
`_scenario_sensitivity_playbook.md`, `_valuation_and_return_logic.md`,
`_ic_memo_depth.md`, `_benchmark_protocol.md`, and `_terminology.md` as the
decision requires. External material enters the model only through its evidence
role: comps, market reports, and benchmarks use `_benchmark_protocol.md`;
public prompt or agent-workflow material uses `_ai_prompt_research_patterns.md`
to become source-bound assumptions, formulas, checks, and closeout inspection;
it shapes workflow, never the evidence for a financial claim.

## Routing Quick Map

| Request signal                                          | Default output shape                                           | Required refs                                                                                   | Skip by default                                  |
| ------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| pricing / ROI / willingness-to-pay                      | compact pricing model, assumption register, or validation plan | `_output_modes.md`, `_generic_composition_protocol.md`, `_assumption_decomposition_patterns.md` | BS/CF/cap table unless explicitly needed         |
| cap table / SAFE / J-KISS / option pool / exit proceeds | cap-table state-machine workbook or ownership audit            | `_output_modes.md`, `_valuation_and_return_logic.md`, `_self_review_protocol.md`                | full P&L/BS/CF unless financing plan requires it |
| runway / burn / lender plan                             | cash/runway model with downside and financing timing           | `_output_modes.md`, `_scenario_sensitivity_playbook.md`, `_kpi_analytics.md`                    | valuation and IC memo unless requested           |
| market sizing / comps / benchmark                       | source-backed Evidence register or market-sizing workbook      | `_benchmark_protocol.md`, `_output_modes.md`                                                    | static benchmark truth without refresh date      |
| fundraising / board / investor-ready model              | integrated decision workbook                                   | full finance reference stack                                                                    | low-value tabs that fail sheet quality           |
| ambiguous memo or weak evidence                         | model spec, assumption register, DD questions                  | `_generic_composition_protocol.md`, `_assumption_decomposition_patterns.md`                     | xlsx generation until mechanics are clear        |

## Core Pattern

Compose from decision and dependencies; examples, maturity cues, sectors, and
modes are prompts for reasoning, not templates. Treat outside workflow ideas the
same way: translate only the reusable reasoning pattern into drivers, formulas,
checks, or closeout gates. Build the driver tree, select material variables,
keep primitive drivers as assumptions, and calculate dependent outputs as
formulas or checks.

## Self-Improvement Trigger

At every closeout and every improvement prompt, decide whether the current run
contains a reusable learning. If command logs, tool failures, user feedback,
artifact repair, or repeated manual work reveal a generalizable weakness, follow
`_self_improvement_protocol.md`: inspect sanitized evidence, classify one-off
artifact fixes separately from reusable skill gaps, patch the lowest durable
layer, add regression proof, and rerun the failed check plus a broader gate.
Before writing any Reflection Record, progress-log learning, or proposed skill
change based on the run, validate the record with
`build/runtime/self_improvement.py`
(`validate_reflection_record_for_acceptance`) or an equivalent
validator-plus-panel scanner. The first gate preserves privacy, source
discipline, regression proof, and anti-overfit rules; the second gate asks
whether the change truly improves reusable quality. Do not store raw logs or
confidential source text in the skill, and do not turn one company-specific
fact or n=1 preference into a global rule.

## Workbook Helper

`--input` structured YAML is the primary path. You read the source — a
narrative, a brief, a conversation — with full understanding, decide the
economic drivers, and write them as YAML. Do not delegate that reading to the
generator: `--source-md` is a best-effort fallback whose regex extraction
silently misses a figure stated apart from its count noun — a maturity target
phrased "... to 9,000 by FY2031" (a number, then a date, with no adjacent
"customers" / "units") is read as the current count. When you only have a
narrative, extract it to YAML yourself, then build from the YAML.

```sh
# Primary: build from drivers you extracted into structured YAML.
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --input model.yaml --output model_output.xlsx
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --mode pricing --input model.yaml --output model_output.xlsx
# Fallback only: let the generator regex-extract a raw narrative.
python3 skills/startup-financial-modeling/scripts/build_model.py \
  --source-md path/to/source.md --output model_output.xlsx
```

Exact mode values: `full`, `pricing`, `unit_economics`, `cap_table`,
`ma_exit`, `dcf_only`, `burn_runway`, `three_statement`, `market_sizing`,
and `comps_only`. Focused modes prioritize formula completeness. Include
supporting sheets when needed rather than hiding broken dependencies behind
placeholders.

Structured YAML may define company/currency/display scale/grain/periods,
segments, operating drivers, financing instruments, and valuation scalars.
`grain: hybrid` (monthly for the first two fiscal years plus annual to five,
with a months-in-period ruler) is the YAML default for `full` and
`three_statement`; `burn_runway` is monthly and the other modes are annual.
The `--source-md` narrative fallback stays annual five-year.
Money inputs are raw base-currency values; `_yen` names are money-driver names.
Carry every figure the source states — especially the demand driver as a
per-period list (`customers` for subscription/account models, `new_units` for
unit-sale models), pricing (`monthly_price_yen`), `target_gross_margin`,
`churn_rate`, and the first round (`equity_raise_yen`, `post_money_yen`); a
marketplace adds `gmv_yen` and `take_rate`. Give the list one value per period
so the stated current figure and the stated maturity figure are both pinned —
that is how a maturity target is honored. Staffing scales with revenue by
default; state `product_headcount` / `gtm_headcount` / `operations_headcount` /
`ga_headcount` as per-period lists when a plan's headcount is known — the
revenue-scaled default runs lean for a high-volume, low-price business. When
you must fall back to
`--source-md`, the regex extractor can silently read an interim or current
figure as the target; `_self_review_protocol.md` requires you to check the
built model's terminal demand against the source before closeout.

## Workbook Gates

Workbook gates: blue inputs, black formulas, green internal links, red external
links, raw money values with display formats, compact unit labels, direct
formulas, editable grid structure, unnumbered sections, traceable sources, no
merged cells, Google-Sheets-20px hierarchy / indent columns (`2.14` xlsx
width), no native indent or leading-space indentation, and generated cells
with `wrap_text` off. Period-axis sheets carry the header contract: FY-label
ruler in row 4, months-in-period ruler in row 5 (period formulas reference it
so one formula shape spans monthly and annual columns), period headers in row
6, freeze pane at F7, and a master-check echo cell in the frozen header.
Number formats use red `▲` negatives and dash zeros with no per-cell `¥`
symbol — scale is declared by the sheet-corner unit caption plus the unit
column. Display scale is two-tier: statement/engine sheets use one sheet-level
scale (per-unit and ratio rows excepted); register sheets (Assumptions,
Evidence, Financing, Cap Table) may scale per row against the unit column. Treat text wrapping as prohibited for
generated workbook cells. Classify the cell role before changing wrap settings:
horizontal-read titles, explanations, instructions, notes, bullets, source
caveats, and memo lines keep wrap off and read through blank unmerged unstyled
overflow cells. Use the IB wrap decision ladder before any exception: shorten
or split the copy, widen the role column, reserve blank unstyled overflow
cells, or move prose to a dedicated note / interpretation column, source
register, memo sheet, or separate row. Use a wrapped/manual-line-break
exception only for user-approved bounded table prose that must stay inside one
column because adjacent cells carry meaningful values, formulas, units, or
notes. Do not place horizontal-read text in the final printed/rendered column
where it cannot overflow visibly. If an exception uses wrapping or manual line
breaks, set row height to the exact rendered visible line count so text is not
clipped or padded.

Unit and scale discipline is mandatory: monetary cell values stay in raw base
currency and display scale is handled by Excel `number_format`, not by
pre-dividing model values or turning numbers into text. When inspecting a
reference workbook or generated output, read cell values and formatting
together: `number_format`, font color, fill, border, alignment, wrapping,
merged-cell state, row height, and column width are part of the model contract.
Do not infer units only from visible text.

This money-display rule must not leak into non-money rows. Preserve operational
units such as units, customers, count, FTE, days, months, percentages, and
multiples with their own formats and formulas.

Text position is part of auditability: labels, sources, notes, titles, memos,
and interpretation text are left-aligned; numeric values, formulas, money,
percentages, multiples, counts, and unit labels are right-aligned; only period
headers, scenario/matrix headers, and short column headers are centered. Do not
center long prose or labels, do not use native indent or spaces for hierarchy,
and keep the same label/source/unit/value positions across sheets whenever
possible.

Font size discipline is equally strict: body/model cells use Arial 10pt,
source/note/unit helper text uses 9pt italic gray, compact section/header rows
use 10-11pt bold, and sheet titles use 14pt bold. Do not create presentation
hierarchy with many font sizes, 8pt footnote cells, oversized 16pt+ titles, or
large pasted memo text. If something needs emphasis, prefer role, placement,
bold, sparse fill/border, or whitespace before changing size.

## Design Gates

Design gates: `_layout_canonical.md` owns grid, columns, hierarchy widths, units,
formulas, and layout mechanics. `_ib_workbook_design_system.md` owns visual
roles, font, color, borders, highlights, charts, and render expectations.

Color discipline is a hard workbook gate, not a polish preference: background
fills are selective accents for major semantic moments only, filled row
components use one consistent rectangular column span, and that span is chosen
from the attached table/block rather than from which cells contain text. Do not
stop a fill because a cell is blank; do not repeat the same non-heatmap fill on
adjacent rows; do not color several rows merely because they are nearby.
Section/block dividers, header/label rows, selected outputs/checks, input
sections, and caution rows are the normal fill roles. Keep the palette small
and calm: avoid rainbow palettes, decorative alternating fills, and high-chroma
backgrounds that compete with the model logic. Use `ib_format.py` semantic
row-span helpers for generated xlsx fill/border row components instead of
hand-painting arbitrary cells.

Border discipline follows the same rule and is equally strict: meaningful row
rules use the same table/block column span as the attached data surface,
including blank member cells where that keeps the section, header, total, or
check row aligned. Do not stop a border because a cell is blank, and do not draw
borders only around populated cells when the data table continues farther right.
Stop the rule at the edge of the related table/block or comparable row span;
leave only trailing canvas and unrelated overflow spacer cells borderless.
Dedicated hierarchy / indent columns stay borderless; draw the rule from the
row's actual hierarchy-position label/data column, not across earlier 20px
spacer columns. Memo, source, note, and interpretation cells are usually
borderless; they read through typography and placement, not grid lines. Borders
are not row-by-row decoration. Use them mainly before or around meaningful rows
where a structural accent is needed. As with background fills, avoid repeating
the same prominent top/bottom rule across adjacent rows unless it is an
explicitly declared table grid; use typography, spacing, or quiet whitespace
for supporting rows. Use three border weights by meaning: normal thin for
ordinary structural breaks, one-step-thicker medium for major section or
decision boundaries, and normal dotted for soft/provisional separations such
as optional checks or supporting context. Border colors are black by default.
Do not introduce gray, colored, or decorative border colors unless the user
supplies a house style; visual priority comes from sparsity, placement, and
thin/medium/dotted weight, not from color.

## Analysis Gates

Material assumptions need selected driver, explanatory drivers, implied value,
support ratio/variance, and evidence status. Weak evidence feeds
scenario/sensitivity/benchmark/DD. KPI, scenario, valuation, benchmark, and memo
surfaces interpret the model and connect evidence to next actions. Write memos
from a clean base rather than preserving legacy layout compatibility; include
only the necessary and sufficient supplemental context for the current decision.
For xlsx outputs, each generated sheet must pass the sheet-level quality rubric:
it needs a distinct purpose, source boundary, dependency flow, checks where
errors would matter, and interpretation where it is an output surface. Do not
create a sheet just because it belongs to a canonical full-workbook order.
Focused modes should remain as compact as possible after formula completeness
is satisfied. Compact-mode placeholders are a last resort for non-decision
helper cells, not an acceptable substitute for valuation, runway, pricing,
scenario, or memo formulas.

## Closeout Gate

Do not treat model construction as completion. Before closeout, run command
checks and rendered-output inspection for both finance logic and sheet design:
formulas, reconciliation, unit/scale integrity, source status, styles, layout,
fonts, fills, borders, print/canvas bounds, and visible readability. Render or
open the xlsx/PDF/screenshot whenever tooling is available. For xlsx outputs,
recalculate with a spreadsheet engine such as LibreOffice when available and
inspect `data_only=True` values for `#VALUE!`, `#REF!`, `#DIV/0!`, and related
errors; formula-string checks alone are not sufficient. If rendering or
recalculation is blocked, document the blocker and still run workbook
inspection commands.
Use the generator's strict audit option when producing an xlsx for handoff:
`python build_model.py --input model.yaml --output model.xlsx --strict-audit`.
It should fail if omitted-sheet references, `#REF!` markers, missing
sheet-quality markers, merged cells, missing or mis-anchored freeze panes,
generated wrapping/manual line breaks, non-standard fonts, or semantic
alignment regressions remain.
Strict audit also runs a profile-independent economic-coherence check: the plan
fails the gate if implied gross margin diverges from its target, if projected
ending cash goes negative, if any period has non-positive revenue, if the
projected balance sheet does not balance (assets != liabilities + equity), or
if the first period carries no funding round. Structural cleanliness is
necessary but not sufficient — a workbook can pass every layout check while the
economics are incoherent.
The generator attempts public-market comparable refresh by default and records
current multiples, provided comparable evidence, or retrieval failures in the
Evidence sheet. Override the auto-selected public ticker set only when the
decision needs specific listed peers: `--live-comps CRM NOW DDOG`. For
non-public companies, funding rounds, M&A transactions, market reports, customer
benchmarks, or internal/user-provided sources, use YAML `private_comps`,
`transaction_comps`, or `benchmark_sources` with source date and applicability
limits. `live_comps` / `public_comps` may contain ticker strings and comparable
evidence mappings in one list; strings are treated as public tickers, mappings
are treated as provided evidence.

For deeper investor-ready models, choose evidence lenses from the material
driver, not from a fixed template. Labor / HR comps support hiring and
productivity, venture equity / funding comps support round feasibility and
valuation, venture debt / non-dilutive capacity supports runway and dilution,
pricing / customer ROI comps support monetization, and market / competitive
benchmarks support reachability. Use a compact register or support sheet only
when the lens changes the decision.

```yaml
live_comps: [CRM, NOW]
private_comps:
  - name: PrivateAI
    company_type: private
    source_type: funding round / press release
    post_money: 12000000000
    arr: 1000000000
    as_of_date: 2026-04-30
    applicability_limits: ARR reported by company; verify security terms
transaction_comps:
  - name: Strategic SaaS acquisition
    enterprise_value: 50000000000
    revenue: 5000000000
    source_url: https://example.test/ma-announcement
    as_of_date: 2025-12-15
```

Follow `_self_review_protocol.md`. If tests, workbook inspection, render
checks, artifact self-review, or the self-improvement trigger finds failures,
fix the concrete failed items and rerun the same checks. Keep iterating until
the model logic and the visible sheet design are both sufficient; when the
self-improvement trigger applies, reusable skill-learning proof must also be
sufficient, or a real blocker is explicitly documented.
