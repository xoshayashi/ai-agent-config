# AI Prompt Research Patterns

Public AI-agent and financial-modeling-prompt material belongs in the workflow
only after it has been translated into the same evidence discipline as a
workbook, benchmark set, or diligence note. Use this reference to turn prompt
ideas into auditable model gates, not into model evidence.

## Research Snapshot

Checked on 2026-07-05:

- X API recent search for financial-modeling + AI / agent / prompt posts from
  the prior 7 days. Representative posts emphasized: define the model purpose
  and decision user before asking an AI to create a spreadsheet; AI can speed up
  modeling, but assumption checks still determine trust; model-audit workflows
  remain valuable; and finance agents are being marketed for modeling, earnings,
  GL reconciliation, and close workflows. Treat this as weak signal about prompt
  demand, not as evidence for any financial assumption. Useful post ids:
  `2073279493335343165`, `2072297746707734690`, `2072755148774928787`,
  `2072666875977199816`, `2073083855548858783`.
- FAST Standard 02c: models should be simple, structured, transparent,
  reviewable by others, adaptable, and built from clear workbook/worksheet/line
  item rules.
- ICAEW Financial Modelling Code: use consistent sign conventions, clear sheet
  names, worksheet purpose coding/labels, meaningful ranges when used, and
  reviewer-readable workbook structure.
- Wall Street Prep / Training The Street / Financial Edge: common IB model
  conventions separate inputs, calculations, outputs, and links; hardcodes /
  assumptions are blue, same-sheet formulas black, internal sheet links green,
  and external file links red; formulas should be direct, row-consistent, and
  easy to audit.
- Financial Modeling Institute: core best-practice themes include model flow,
  assumption management, scenario pages, repeat-and-link discipline, and
  forecast periodicity.
- Macabacus: color is useful only when it separates roles consistently; random
  colors increase cognitive load.

Source URLs:

- https://fast-standard.org/wp-content/uploads/2019/10/FAST-Standard-02c-July-2019.pdf
- https://www.icaew.com/-/media/corporate/files/technical/technology/excel/financial-modelling-code.ashx
- https://www.wallstreetprep.com/knowledge/financial-modeling/
- https://trainingthestreet.com/fmaamoc-article-2-formatting-a-financial-model/
- https://www.fe.training/free-resources/financial-modeling/financial-model-formatting-numbers/
- https://fminstitute.com/modeling-resources/financial-modeling-best-practices/
- https://macabacus.com/blog/improving-model-readability-with-color-formatting

## Prompt Contract

Convert public prompt ideas into this contract before writing YAML, xlsx, or an
audit plan:

1. Decision: name who uses the model, what decision it supports, and what would
   change the decision.
2. Evidence packet: list source facts, management targets, benchmarks,
   estimates, placeholders, and unknowns separately.
3. Economic kernel: identify the actual unit of economics before selecting
   sheets. Do not default to SaaS, marketplace, or hardware metrics from labels
   alone.
4. Driver tree: decompose material assumptions into selected driver,
   explanatory drivers, implied value, support ratio/variance, evidence status,
   and decision impact.
5. Workbook design: apply the IB design system for colors, units, raw money
   values, font sizes, no wrap/merge/freeze, 20px hierarchy columns, sparse
   fills/borders, and role-based alignment.
6. Financing and ownership: calculate runway, funding gap, dilution, option
   pool, converts, SAFEs/J-KISS, debt, warrants, preference, and investor /
   founder proceeds on a fully diluted basis when returns are evaluated.
7. Valuation and return: choose methods by credibility, explain exclusions, and
   reconcile selected value to MOIC / IRR / founder proceeds, not only a revenue
   multiple.
8. Audit: run strict workbook checks, source/fact checks, formula checks,
   rendered readability checks, and scenario/sensitivity checks before closeout.

## Prompt Skeletons

Use these as internal scaffolds, not as user-visible boilerplate:

### Build From Equity Story

```
Decision:
Source facts:
Management targets:
Unknowns:
Economic unit:
Material assumptions:
Required sheets:
Return / dilution questions:
Design and audit gates:
```

### Audit An Existing Workbook

```
Decision supported by workbook:
Source boundary visible in workbook:
Sheets that earn their place:
Broken formulas / references:
Input-formula-link color violations:
Unit / number-format mismatches:
Assumption support gaps:
FD ownership / return gaps:
Rendered readability defects:
Fix order:
```

### Convert A Prompt Claim Into A Finance Model Gate

```
Prompt claim:
Reusable part:
Unsupported part:
Required evidence:
Required formula/check:
Sheet / row where it belongs:
Closeout verification:
```

## Guardrails

- Do not treat X posts, AI-product marketing, or generic prompt threads as
  financial sources. They can influence workflow shape only.
- Do not create a sheet because a prompt asked for it. Apply
  `_sheet_quality_rubric.md`: purpose, source boundary, dependency flow, checks,
  and interpretation decide inclusion.
- Do not hide AI uncertainty in polished formatting. Weak assumptions must
  surface as evidence status, scenario/sensitivity, benchmark refresh, or DD.
- Do not use "AI generated" as provenance. Record the underlying source,
  estimate method, or open unknown.
- When public prompt research changes the skill, update evals or a deterministic
  metric pack so the workflow insight is testable rather than buried in prose.
