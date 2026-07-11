# Composition Vocabulary

This file names reusable composition moves. These are not slide types. Use them to create
2-3 distinct directions for a slide, then map the chosen direction to an implemented
`deck.json` primitive.

## Selection Rule

Choose a move from the reader question and focal evidence:

- number proof
- change over time
- decomposition
- comparison
- relationship / system
- sequence / process
- proof recap
- quiet reset
- decision request

Do not choose a move because a topic traditionally uses it.

## Evidence And Number Moves

### Oversized Number + Evidence Rail

Use when one number changes the reader's belief. Make the number dominant, then place source,
denominator, comparison, and caveat in a rail. Repair if the rail becomes a list of weak facts.

### Chart + Interpretation Rail

Use when the chart proves the title but the reader needs the implication stated. Keep the
chart large and the rail subordinate but readable.

### Table With One Dominant Conclusion

Use when accountability across rows/columns matters. Highlight one protagonist row or column.
Repair if every cell appears equally important.

### Dense Annotation Field Around One Chart

Use when one chart needs event labels, period bands, or driver notes. Keep annotation local to
the relevant data point.

### Evidence Strip

Use for logos, proof points, customer cases, milestones, or third-party validation. It should
support a claim, not decorate a closing page.

### Quote As Evidence

Use only when the quoted person, organization, date, and context matter. The quote must prove
or sharpen the slide's claim.

## Data-Shape Moves

### Two-Axis Combo

Use when an amount and a rate must be read together. Keep units explicit and roles stable:
amount as bar/column, rate as line.

### Waterfall / Bridge

Use for start-to-end movement with drivers. Cause labels matter more than ornamented bars.

### Layered Accumulation Stack

Use when component contribution over time matters. Repair if the stack hides the protagonist
component.

### KPI Grid

Use only when comparing KPIs side by side is the point. Do not use cards as default layout.

### Driver Equation / Tree

Use when outcome equals drivers. Make the equation or causal tree visible before explaining
initiatives.

### Nested Scale / TAM

Use when inclusion or reachable opportunity matters. Always show assumptions and current
position.

### Actual / Forecast Pair

Use when the reader must distinguish disclosed actuals from plan, forecast, target, or
scenario. Styling separation is mandatory.

## Diagram And Structure Moves

### Highlighted Path Diagram

Use when one path through a system matters. Label relationships, not just nodes.

### Controlled-Depth System Map

Use when the business system must be understood without full technical detail. Limit depth and
make the focal layer explicit.

### Hub And Spoke

Use when one asset, platform, capability, or channel coordinates several parts. Spokes need
relationship labels.

### Process Flow With Business Implication

Use when sequence and outcome both matter. Step outcomes must be prominent and centered when
they carry the design.

### Timeline With Decision Points

Use when dates, milestones, and decisions interact. Emphasize decision points, not every
event.

### Positioning Quadrant / Bubble Map

Use when two axes reveal strategic position. Axes must be fair and non-obvious.

### Before / After Contrast

Use when change is the argument. Keep both sides visually comparable and highlight only the
difference.

### Asymmetric Split Contrast

Use when one side is the protagonist and the other is reference context. Asymmetry must still
align to the grid.

### Small Multiples

Use when the same grammar across several units helps comparison. Keep axes and scales stable.

## Editorial Structure Moves

### Thin Editorial Rules

Use fine rule lines to separate roles without adding heavy boxes.

### Editorial Sidebar

Use for interpretation, caveat, or decision request. The sidebar must have a clear alignment
relationship to the proof field.

### High-Density Appendix

Use only for backup material. Keep strict hierarchy and source discipline.

### One Accent Object In A Calm Page

Use when a single mark, quote, product crop, or value should create contrast. The accent must
carry meaning.

### Wide Quiet Margin With One Claim

Use for rhythm or a decisive thesis. Avoid empty space that exists only because content is
thin.

## Whole-Page Framing Moves

### Action Title + Lead Two-Layer

Use a conclusion title with a subtitle/scope line. The subtitle must not introduce a second
claim.

### Product / Interface Crop

Use real product evidence when it helps the reader understand actual capability. Avoid dark,
blurred, or generic stock-like crops.

### Current-Location Agenda

Use when navigation itself matters. Preserve the whole map and mark current position.

### Quiet Section Reset

Use when the deck needs a pause before a new proof arc.

### Flexible Close

Use thesis, proof strip, decision request, next actions, quote, or legal close according to
the story. Do not use a fixed closing template.

## Mapping To Implemented Primitives

- Waterfall -> `waterfall`
- KPI grid / oversized number -> `kpi_dashboard`, `metrics_rows`, `financial_highlights`
- Nested scale -> `market_sizing`
- Positioning quadrant -> `competitive_landscape`
- Table conclusion -> `comparison_table`
- Chart + interpretation rail -> `chart_insight`
- Before/after or asymmetric split -> `two_column`
- Process flow -> `process_flow`
- Current-location agenda -> `agenda`
- Guidance progress -> `guidance_progress`
- Driver equation -> `driver_decomposition`
- Flexible close -> `statement`

When the fit is weak, compose primitives or extend the renderer rather than forcing the
evidence into a rigid pattern.

