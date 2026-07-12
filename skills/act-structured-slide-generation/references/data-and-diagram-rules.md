# Data And Diagram Rules

Use this file when selecting charts, tables, diagrams, images, and other evidence carriers.

## Two Rendering Tracks: Native First, Image When Native Cannot

Every object routes to the most editable representation it can faithfully take (see
`slide-decision-engine.md`, the `render_route` step). There are two tracks:

- **Native track (default).** python-pptx text, tables, native charts (column/bar/line/donut/
  stacked_column), and autoshapes. Fully editable in PowerPoint and auditable. Prove titles with
  the emphasis knobs (`emphasis_col`, `focal_category`, `segment_labels`, `annotation.badge`,
  `color_negatives`, `focal`, table `col0_spans` for grouped row labels) rather than a bespoke
  layout. Assume a data/argument slide is native unless an object genuinely exceeds it.
- **Image-asset track (escalation).** For objects the native engine cannot draw, an Act-styled
  deterministic image is generated (matplotlib for charts + schematic diagrams, Graphviz for
  relationship graphs) and embedded as a picture. Use it only for the single hard object on a
  slide; keep the title, rail, tables, and body native. The image is a cache of a spec — a
  sidecar keeps its numbers, so the pixels are non-editable but the data stays auditable and
  regenerable. Now covers, as an image `kind`:
  - **combo / dual-axis** (columns + a ratio line: margin, ARPU, payout) — `chart.kind: "combo"`
  - **area / stacked-area** (`area`), **radar / scatter / bubble / waterfall / line_multi**
  - **org / ownership tree**, **freeform node graph / ecosystem** — `diagram.kind: org_tree | node_graph`
  - **ring / flywheel / cycle**, **funnel**, **pyramid**, **area-proportional Venn**, **coverage
    matrix** — `diagram.kind: ring | funnel | pyramid | venn | matrix`

  When a simple 2×2, ≤6-node tree, or ≤5-step flow reads fine natively, keep it native — do not
  reach for an image just because the image track exists.

### Small-multiples and the annotation layer (common IR moves)

- **Small-multiples** (2-4 coordinated trend charts sharing one claim, each with a CAGR badge):
  use the native `chart_grid` pattern — the cells are native charts, still editable, each taking
  the emphasis knobs (`focal_category`, `annotation.badge`/`trend_arrow`). Route a single cell to
  the image track only if that chart itself needs a kind native cannot draw. Do not image the
  whole grid by default.
- **Leader-line cause callouts** anchored to a specific bar / waterfall step / point (the "explain
  the driver behind this movement" move): add `annotations: [{target, text, dy}]` to a
  matplotlib-rendered image chart (int `target` on `combo`/`waterfall`, else `{x,y}`). Native pptx
  connectors cannot anchor to chart internals, so this is the one case where the annotation itself
  is the reason to use the image track. Not on Graphviz `org_tree`/`node_graph` (use edge labels).
  Keep to 1-3 per exhibit.

### Still out of scope (re-express or flag)

Do not approximate these with a low-fidelity substitute:

- **Geographic map as the coverage object** — not yet in the image track; use a coverage
  `comparison_table` or a metric, or supply a prepared map image.
- **Proportional ribbon Sankey** — deferred (no clean deterministic renderer yet); use a
  waterfall, a driver equation, or a share table.
- **Raster proof grid** (photo / logo / product-screenshot / headshot wall as the evidence) —
  requires user-supplied assets; otherwise an evidence strip with a count, strongest item as a
  case card. Never auto-fetch or invent an image.
- **Whole-slide bespoke layout** that cannot be decomposed into native chrome plus one image
  object — reconsider the slide; a full-slide screenshot forfeits editability and audit.

### Rejected renderers (do not add)

Considered and rejected so the deterministic, browser-free, editable core holds: plotly+kaleido
and pyecharts and bokeh (need an external browser/webdriver for static export), mermaid-cli
(Node + Chromium), geopandas/GDAL and cartopy (heavy native-dep friction), wkhtmltoimage
(abandonware), and any Chromium/Playwright full-slide HTML route (non-deterministic + destroys
editability).

## Chart Choice By Claim

- **Level**: hero number, table row, column/bar comparison, or KPI field.
- **Change over time**: line, column series, stacked trend, period bands, or event markers.
- **Composition**: stacked chart, waterfall, bridge, or driver tree.
- **Comparison**: grouped bars/columns, table, quadrant, small multiples, or paired KPI fields.
- **Progress to target**: gauge, range, current-position marker, or target table.
- **Relationship / process**: labeled flow, system map, driver equation, or timeline.

If a bar or column chart has only one value, it is not comparative enough. Convert it to a
hero number, gauge, range, or facts rail unless a second period, scenario, or peer is added.

## Read Without Help

- Title, visual, labels, and source must explain the slide without oral narration.
- Every chart needs unit, period, and direct value labels when practical.
- Actual, forecast, target, and assumption values must be visually distinguishable.
- Do not use legends when direct labels would be clearer.
- Use one protagonist emphasis only.

## Diagram Rules

- Label relationships on arrows or connectors.
- Keep depth controlled; a diagram with every node is usually not a proof page.
- Highlight one path, actor, lever, or decision point.
- Use equal shapes only for equal roles. Different roles need different weight, position, or
  grouping.
- Avoid decorative arrows. An arrow must name movement, dependency, sequence, or ownership.

## Image And Asset Rules

- Use images, screenshots, logos, and product crops as evidence.
- Avoid generic stock visuals, dark crops, blurred backgrounds, or decorative screenshots.
- Product/UI crops must show actual capability or workflow.
- Customer logos, awards, and quotes require source, date, and permission assumptions when
  relevant.

