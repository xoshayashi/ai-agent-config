# deck.json Spec And Slide-Building Primitives

`deck.json` is the source for an editable PowerPoint deck. Pattern names are implementation
primitives, not design templates. Choose and combine them after the judgment process.

## Top Level

```json
{
  "meta": {
    "title": "Deck title",
    "date": "Optional display date",
    "company": "Optional company name"
  },
  "slides": []
}
```

`meta` is optional. Do not force company/date onto closing slides; use metadata only where
the selected primitive displays it appropriately.

## Fields Common To Slides

- `pattern` (required): one of the implemented primitives below.
- `title` (required except special appendix cases): conclusion-oriented action title.
- `subtitle` (optional): scope line, not a second claim.
- `source` (required on evidence slides): external or internal provenance.
- `assumption` (optional): internal estimate, plan, target, or scenario basis.
- `note` (optional): definition, caveat, or denominator.
- `speaker_notes` (optional): presenter script and judgment notes.
- `variant` (optional): primitive-specific variation when documented below.

## The 19 Patterns

### 1. `cover`

Opening title slide. Use for title, subtitle, date, and optional presenter context.

### 2. `agenda`

Table of contents or current-location page. Keep `items` to six or fewer. Use a highlighted
current item only when the reader benefits from navigation.

### 3. `section_divider`

Chapter reset. Keep it quiet and strong; do not overfill it with body proof.

### 4. `executive_summary`

Opening summary with up to four `points`. The chapter spine and executive summary must agree.

### 5. `kpi_dashboard`

KPI cards or value fields. `kpis` supports label, value, unit, delta, delta_dir, note, and
focal/hero flags. Use cards only when side-by-side KPI comparison is the point.

### 6. `chart_insight`

Chart plus interpretation. Use `chart`, optional `insight`, optional `bullets`, and optional
`annotation`. The chart must prove the title; the interpretation rail explains the implication.

### 7. `market_sizing`

TAM/SAM/SOM or reachable-opportunity sizing. Include values, units, assumptions, and the
reachable opportunity, not just total market scale.

### 8. `comparison_table`

Comparison table with rows and columns. Highlight one row or column when it carries the claim.
Keep axes fair and specific.

### 9. `competitive_landscape`

2x2 positioning or bubble map. Axes must be meaningful, non-self-serving, and labeled.

### 10. `financial_summary`

Financial table and chart combination. When both table and chart are present, they should
cross-check one conclusion rather than duplicate decoration.

### 11. `waterfall`

Bridge chart. Items require start, positive/negative drivers, and end. Cause labels should
explain the movement, not merely repeat numbers.

### 12. `roadmap`

Phase roadmap with up to four phases. Use for time, sequence, or staged execution. Each phase
needs outcome and evidence of feasibility.

### 13. `two_column`

Contrast primitive: options, before/after, current/future, problem/solution. Use asymmetry
when one side is more important; do not default to equal columns.

### 14. `process_flow`

Step flow with up to five steps. Include what each step yields. Outcome labels after arrows
should be large and centered when they are the key design objects.

### 15. `statement`

Flexible closing, thesis, quote, decision request, legal close, or proof recap. Use variants
such as `thesis`, `evidence_strip`, `decision_request`, `next_actions`, `legal`, or `quote`
when available. Avoid fixed left-heavy endings and redundant company/date metadata.

### 16. `financial_highlights`

Earnings highlights. Supports grouped highlights and hero metrics. Metric deltas such as YoY
must be separate sublines with visible spacing.

### 17. `metrics_rows`

Numeric summary rows with label, value, unit, delta, note, and focal flags. Use when row
alignment and comparability matter. Keep row heights large enough to fill the content field.

### 18. `guidance_progress`

Guidance progress against a full-year range or target. Prefer current-position gauge plus
facts rail. Do not represent a current-only value as a lone bar.

### 19. `driver_decomposition`

KPI driver decomposition such as volume x price = result. Each driver needs value, unit,
delta, note, and a clear relationship to the result.

## Chart Spec

Shared by `chart_insight` and `financial_summary`:

```json
{
  "type": "column | stacked_column | bar | line | donut",
  "unit": "unit label",
  "categories": ["2024", "2025", "2026"],
  "series": [
    {"name": "Revenue", "values": [10, 12, 15], "color": "primary"}
  ],
  "forecast_from": 2,
  "annotation": "optional callout"
}
```

Rules:

- Use bars/columns for comparison, not a single current value.
- Match the type to the question: `column`/`bar` compare, `line` shows trend, `stacked_column`
  shows composition over time, `donut` shows a single share split. There is no `combo`, `area`,
  or dual-axis type; keep a second measure (e.g. margin %) on its own `line` slide or in a table.
- Negatives render wrong in `column`/`bar`/`stacked_column` under LibreOffice QA — put a series
  with negative values in a `line` chart, the `waterfall` pattern, or a table.
- Keep actual and forecast styling distinct.
- Label values directly when possible.
- Put unit, base period, and denominator where the reader can verify the claim.
- Do not mix too many series unless the slide's question is explicitly about interaction
  between those series.

## Japanese Slide Copy Discipline

The generated deck is usually Japanese even though this manual is English. Write:

- conclusion-oriented noun-phrase titles
- no sentence-final full stop in slide-visible text
- no polite spoken endings in titles or bullets
- half-width alphanumerics
- short, concrete labels
- one number in evidence-slide titles when possible

Avoid topic titles, two claims joined into one title, generic adjectives, and labels that do
not explain the business implication.

## Writing Discipline

- Every content slide answers one reader question.
- Every title is proven by the same slide's evidence.
- Every material number has source, period, unit, denominator, and status.
- Every forecast, plan, target, or estimate is visually or textually distinguished from actual
  results.
- Every dense page earns its density through alignment, row/column structure, and hierarchy.

