# deck.json Spec And Slide-Building Primitives

`deck.json` is the source for an editable PowerPoint deck. Pattern names are implementation
primitives, not design templates. Choose and combine them after the judgment process.

## Contents

- Top Level
- Fields Common To Slides
- The 21 Patterns
- Chart Spec (native types, emphasis/annotation knobs, image chart kinds, annotation layer)
- Table Spec
- KPI / Metrics Spec
- Image-Asset Track
- Japanese Slide Copy Discipline
- Writing Discipline

## Top Level

```json
{
  "meta": {
    "title": "Deck title",
    "template": "standard | navy | monochrome | bold",
    "date": "Optional display date",
    "company": "Optional company name"
  },
  "slides": []
}
```

`meta` is optional. Do not force company/date onto closing slides; use metadata only where
the selected primitive displays it appropriately. `meta.basis` (optional) records the single
internal artifact a deck derives from (e.g. one meeting's minutes); it satisfies the
evidence-source check without printing an internal-provenance footer on every slide.

`meta.template` (optional, default `standard`) selects the deck-level design template — the
look every slide wears. The valid set is the files in `references/templates/`; list them with
`build_deck.py --templates` and see `templates.md`. `validate_spec.py` errors on an unknown
name. An absent template resolves to `standard`, which is byte-for-byte the pre-template output.

## Fields Common To Slides

- `pattern` (required): one of the implemented primitives below.
- `title` (required on EVERY slide, cover and statement included): conclusion-oriented action
  title. Always ONE line — no `\n`, no wrapping.
- `subtitle` (required on every slide): scope line, not a second claim. One line — except on
  the `cover`, where it is exactly TWO lines joined with `\n`. On `section_divider` the
  subtitle slot is the `desc` field instead (that pattern draws no header chrome, so a
  `subtitle` there would be silently dropped and is rejected).
- The slots, their line counts, and their per-line character limits are not restated here:
  they are declared in `tokens.json` → `header_contract` and derived from the render geometry
  by `deck_text.header_slots()`. `validate_spec.py` errors on any violation; fix it by
  shortening the copy, never by shrinking the type.
- `source` (evidence slides with external data): a TRUE citation only — organization, report or
  dataset, and date, or a verifiable named internal system. Never stamp a deck-wide internal
  artifact (meeting minutes, a workshop, one internal doc) as a per-slide Source footer; that is
  noise and it debases real citations. When the whole deck derives from one internal artifact,
  record it once in `meta.basis` (validated, never rendered) and omit per-slide `source`.
- `assumption` (optional): internal estimate, plan, target, or scenario basis.
- `note` (optional): definition, caveat, or denominator.
- `speaker_notes` (optional): the presenter's TALK SCRIPT only — spoken-form claim,
  evidence walk in reading order, so-what with caveats, bridge to the next slide
  (~150-300 JA chars per content slide, natural spoken register). The script and the
  slide must be the same argument: every spoken number/date/noun exists on the slide (or
  its note), and consecutive scripts read as one continuous narration, each picking up
  from the previous bridge. Judgment/design metadata never goes here; it belongs in
  working notes (outline/blueprints). See SKILL.md "Talk Script"; validate_spec flags
  metadata leakage, thin scripts, non-spoken register, title-verbatim openings, and
  slide-absent numbers.
- `variant` (optional): primitive-specific variation when documented below.
- `render` (optional, on a chart/diagram object): `"image"` forces the image-asset track even
  for a kind the native engine could attempt. Default (unset) keeps native unless the `kind` is
  image-only (combo/area/org_tree/…). Escalate to image only for objects native cannot draw.

## The 21 Patterns

### 1. `cover`

Opening title slide. Use for title, subtitle, date, and optional presenter context.
The cover subtitle is always exactly two lines, authored with `\n` (see Fields Common
To Slides); the cover title stays one line.

### 2. `agenda`

Table of contents or current-location page. Keep `items` to six or fewer. Use a highlighted
current item only when the reader benefits from navigation.

### 3. `section_divider`

Chapter reset. Keep it quiet and strong; do not overfill it with body proof. Reserve dividers
for long, read-oriented decks (~18+ slides / document-style) where each chapter carries at
least ~3 proof slides. In a short talk deck they inject a hard narrative break without aiding
readability — omit them and let action titles plus the executive summary carry the structure
(see design-principles: Section Dividers).

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
should be large and centered when they are the key design objects. `focal_step` (0-based,
default last) picks which step gets the solid emphasis chevron — set it when the title's
claim hinges on a mid-flow step, so the visual focus matches the argument.

## Argument fields (enforced by `audit_argument.py`)

- `meta.thesis` — `{statement, value, unit}`: the deck's one claim and the figure that settles
  it. Required; the figure must appear in some slide's exhibit.
- `derivation` (per slide) — `{kind, value, unit, ...operands}`: how a computed figure was
  computed. Kinds: `cagr`, `growth`, `multiple`, `share`, `ratio`, `delta`, `sum`. Operands are
  numbers, lists, or paths into the slide (`"chart.series[0].values"`, `"current.actual"`).
  The gate recomputes and compares at the precision printed.
- `qualifier` (per slide) — `{universe, as_of}`: required on a slide that claims a rank or a
  uniqueness, alongside a `source`.

### 15. `statement`

`lead` (optional) is the one line that says the point, set at statement size; `statement` is
the sentence that supports it, set smaller below. A statement written as one clause joined by
a dash is opened into the same two tiers automatically.

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

### 20. `diagram`

Relationship or schematic diagram rendered via the image-asset track (see the Image-Asset Track
section) because the native engine cannot draw it. `diagram` carries an asset spec:
`{"kind": "org_tree" | "node_graph" | "ring" | "funnel" | "pyramid" | "venn" | "matrix", …}`.
Optional `takeaways` add an interpretation rail beside the diagram, exactly like `chart_insight`.
Use only when the relationship genuinely exceeds a native `process_flow` / `two_column` /
`competitive_landscape`; a simple ≤6-node tree or ≤5-step flow stays native and editable.

### 21. `chart_grid`

Small-multiples: 2-4 coordinated NATIVE charts sharing one claim, tiled in a row so each stays
editable. `charts` is a list of `{"title": optional cell heading, "chart": {…native chart spec…}}`.
Each cell's chart takes the full native chart spec including the emphasis knobs
(`focal_category`, `annotation.badge`/`trend_arrow`, `value_labels`), so per-chart CAGR badges
and latest-bar emphasis work. This is the native, editable way to do the common IR "3-up trend
grid, each with a CAGR badge" page. Prefer it over an image; escalate an individual cell to the
image track only if that chart itself needs a kind native cannot draw.

## Chart Spec

Shared by `chart_insight` and `financial_summary`:

```json
{
  "type": "column | stacked_column | bar | line | donut",
  "unit": "unit label",
  "categories": ["2024", "2025", "2026"],
  "series": [
    {"name": "Revenue", "values": [10, 12, 15], "focal": true}
  ],
  "value_labels": true,
  "focal_category": 2,
  "segment_labels": true,
  "forecast_from": 2,
  "number_format": "#,##0",
  "annotation": {"badge": "3-yr 2.8x", "yoy": "+17.8%", "trend_arrow": true}
}
```

### Emphasis and annotation knobs (use these instead of inventing layout)

These render primitives already exist; reach for them from the judgment layer so IR
evidence-emphasis moves are reproduced without a bespoke slide:

- `focal_category` (int): highlight one category's bar in the protagonist color while the
  rest go muted grey. This is the "latest-period / turning-point emphasis" move on a
  single-series `column`/`bar`. Defaults to the last category when annotation is present.
- `series[].focal` (bool): on multi-series `line`, `focal: true` thickens the protagonist line;
  to also grey out the peers you must set `focal: false` on each non-protagonist series (a line
  only mutes when its `focal` is explicitly `false`, not merely absent).
- `value_labels` (bool): direct value labels (defaults on for single series). Prefer direct
  labels over a value axis when the reader needs exact numbers.
- `segment_labels` (bool, `stacked_column` only): print each component value inside its band.
  This is the "stacked total + segment values" evidence move; pair it with a total or
  ratio stated in the interpretation rail rather than a fragile total-on-top overlay. Labels are
  ink, so they read best on mid/light segment fills; keep the most saturated-dark segment small
  or unlabelled if contrast looks marginal.
- `forecast_from` (int): index from which bars/points switch to forecast styling, keeping
  actual and forecast visibly distinct (audit trail for future-looking claims).
- `annotation` (object): mark-anchored callouts on the focal bar —
  `badge` (a pulled-out CAGR / multiple / net-change chip, e.g. "3-yr 2.8x"),
  `yoy` (a YoY chip), and `trend_arrow` (a diagonal growth arrow). Use one, not all three.
- `number_format`: e.g. `"#,##0"` or `"#,##0.0"`; also `axis_number_format` for the axis only.

### Image chart kinds (rendered by the image-asset track)

When a chart type is outside the five native types, set `kind` (not `type`) and the chart is
rendered as an Act-styled image. `chart_insight` still supplies the title and `takeaways` rail
natively around it.

- `{"kind": "combo", "categories": [...], "bar": {"name","values","unit"}, "line": {"name","values","unit"}}`
  — columns + a line on a second axis (margin/ARPU/payout); the dominant IR motif native cannot draw.
- `{"kind": "area", "categories": [...], "series": [{"name","values"}, …]}` — stacked-area over time.
- `{"kind": "line_multi" | "radar" | "scatter" | "bubble" | "waterfall", …}` — see act_assets for fields.

Use an image chart only when the native five cannot express the claim; native charts stay editable.

**Annotation layer (matplotlib-rendered charts/diagrams).** Add `annotations` to attach
leader-line callout boxes anchored to a specific mark — the recurring IR "point to the driver
behind this step/bar" move that native connectors cannot anchor to chart internals:
`"annotations": [{"target": <int category/step index | {"x":, "y":}>, "text": "cause…", "dy": 40, "dx": 0}]`.
An int `target` resolves to a bar top on `combo` / step top on `waterfall`; on the other
matplotlib kinds give an explicit `{"x":,"y":}` in data coordinates. `dy`/`dx` nudge the box
(positive `dy` above, negative below). Keep to 1-3 per exhibit. Not supported on the Graphviz
relationship graphs (`org_tree`, `node_graph`) — label those with edge labels instead.

Rules:

- Use bars/columns for comparison, not a single current value.
- Match the type to the question: `column`/`bar` compare, `line` shows trend, `stacked_column`
  shows composition over time, `donut` shows a single share split. There is no native `combo`,
  `area`, or dual-axis `type`; when amount and rate must be read together, escalate to the
  image-asset `kind: "combo"` (see Image chart kinds above), or keep the second measure on its
  own `line` slide or in a table when separation reads more clearly.
- Negatives render wrong in `column`/`bar`/`stacked_column` under LibreOffice QA — put a series
  with negative values in a `line` chart, the `waterfall` pattern, or a table.
- Keep actual and forecast styling distinct.
- Label values directly when possible.
- Put unit, base period, and denominator where the reader can verify the claim.
- Do not mix too many series unless the slide's question is explicitly about interaction
  between those series.

## Table Spec

Used by `comparison_table` and `financial_summary` (the `table` field):

```json
{
  "headers": ["Item", "Prior", "Latest", "YoY chg", "YoY %"],
  "rows": [["Revenue", "120.4", "137.9", "+17.5", "+14.5%"], ["Non-op. loss", "12.1", "9.4", "△2.7", "△22.3%"]],
  "col_widths": [2.2, 1.4, 1.4, 1.4, 1.2],
  "align": ["l", "r", "r", "r", "r"],
  "emphasis_col": 2,
  "emphasis_row": null,
  "color_negatives": true
}
```

- `emphasis_col` / `emphasis_row` (int): tint one column or row in the protagonist pale-brand
  fill. This is the "protagonist column" move — make the actual/forecast/latest column
  the entry point. Set at most one protagonist per table; do not tint decoratively.
- `color_negatives` (bool): render value cells that start with `△ ▲ ▼ - −` in the danger
  color, so decline/loss is carried by color and glyph, not glyph alone. Use IR `△` notation
  for negatives (not `-`) in the cell text itself.
- `col0_spans` (list of `[start_row, length]`, 0-based data rows): vertically merge the first
  (label) column so one category brackets several metric rows (e.g. a segment name spanning its
  sales and profit rows). Put the label in the group's first row and `""` in the rest; the table
  stays a native, editable PowerPoint table. Add `group_dividers: true` when the row-to-group
  correspondence is hard to track (many rows per group, no other cue): each group's last row
  then gets a dashed grey bottom rule (final row keeps the normal hairline). This is opt-in
  judgment, not a default — omit it when groups read at a glance.
- Sub-row hierarchy: author indented breakdown rows by prefixing the label with a full-width
  space (a leading U+3000, e.g. an "excl. one-time items" sub-line under its parent metric);
  keep the parent line bold via row order and put the unit outside the table body.
- Keep the protagonist column near the left-to-right reading landing; move variance math and
  definitions to `note`/`source` when the table would exceed a comfortable width.

## KPI / Metrics Spec

`kpi_dashboard`, `metrics_rows`, and `financial_highlights` take items with
`label, value, unit, delta, delta_dir, note` and a `focal` flag. Set `focal: true` on the one
metric the title is about — it gets the pale-brand hero card and the protagonist value color;
the rest stay in ink so a single message leads. Keep `delta` (YoY / vs-plan) as a separate
subline, never glued to the value. Keep `value` compact — an over-wide value plus a
multi-character `unit` can wrap and collide with the delta, so move long qualifiers to `note`.

## Image-Asset Track

Objects the native engine cannot draw (image chart kinds, the `diagram` pattern) are rendered by
`scripts/act_assets.py` into Act-styled PNGs and embedded with `add_picture`. All colour and
type come from the one token core via `act_theme.py`, so an embedded chart and a native table look
like one deck. The renderers are deterministic and browser-free (matplotlib Agg, Graphviz `dot`).

- Assets are **content-addressed** on spec + box + theme + renderer versions → same cached file,
  no re-render; a renderer upgrade (matplotlib/Graphviz) busts the cache so output never goes
  stale. They live in an `assets/` dir beside the built `.pptx`, with an `asset-manifest.json`.
- Each asset keeps a **`.json` sidecar** of its spec and numbers. The picture is not editable in
  PowerPoint, but the data stays auditable and regenerable — so embed the smallest object that
  needs it and keep the surrounding title, rail, tables, and body native.
- The image is sized to its on-slide box in inches, so aspect matches and nothing distorts.

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

