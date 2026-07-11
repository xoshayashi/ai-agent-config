# Design Principles

The Act structured deck style is a banker-grade base with modern editorial impact. The base
is investment-bank / strategy-consulting: action title, one claim, tight proof hierarchy,
auditable sources, and disciplined comparison. Freshness comes second and must be earned
through composition, object scale, asymmetry, and density control.

## Typography And Whitespace

- Use the type scale from `tokens.json`; do not shrink body evidence to fit a weak layout.
- Important body text, table values, chart labels, process outcomes, and metric deltas must
  be readable from the back row.
- Footer/source text may be small because it is provenance, not the page's argument.
- Increase impact by enlarging the focal object and tightening structure, not by adding
  decoration.
- Keep enough line spacing for multi-line Japanese text. A value and its YoY / delta line are
  two hierarchy levels; the delta must have a deliberate metric-subline gap.
- Avoid over-large closing-slide text when it creates a left-heavy imbalance. Closing slides
  need scale contrast, but the body must remain composed.

## Canvas And Header

- The header is a navigation contract, not a decorative template.
- The title states the conclusion. The subtitle scopes period, segment, audience, or metric.
- Do not add a kicker line above the title.
- Keep title line count and subtitle use consistent enough that the deck feels controlled.
- The body starts after the header with a consistent content top. If a two-line title changes
  body position, review the header strip.
- Do not render page numbers.

## Color

- Use the Act palette from `tokens.json`. Avoid pure black, neon colors, gradients, shadows,
  and excessive fills.
- Use deep green / teal as the serious base. Use yellow accent sparingly and only for a true
  protagonist mark.
- In time-series charts, the latest or conclusion period may be darkest; historical periods
  recede.
- Color meaning must remain stable across the deck. Do not use the same accent for unrelated
  meanings.
- Modern freshness must come from layout and hierarchy, not color noise.

## Charts And Evidence

- Charts must support the title directly. If the chart cannot prove the title, rewrite one of
  them.
- Prefer direct data labels and minimal axes. Keep units visible.
- Bars and columns require comparison: time, segment, scenario, plan, prior year, or peer.
  A single current bar is not a chart; use a hero number, gauge, range card, or table row.
- Actual, forecast, plan, and target values must be distinguishable without relying on a
  long legend.
- Do not place YoY and QoQ callouts together unless the story truly needs both; usually one
  comparison is the protagonist.
- Tables are accountability tools. Highlight the row or column that proves the title and keep
  gridlines light.
- Guidance and target ranges need a denominator and progress context, not a lone bar.

## Structural Slides

### Section Dividers

Use a strong but quiet reset. A divider should signal the next chapter, not fill space. Scale
contrast matters: chapter number or section label may be large, but the page must still hint
at the next proof arc.

**When to use dividers — length and reading mode decide, not habit.** Section dividers are a
navigation aid for *long, read-oriented* decks (board / IR / leave-behind documents, roughly
18+ slides, or any deck the audience reads without a presenter). There, a reset every 3-5
proof slides helps the reader keep the map.

**When to omit them.** In a short talk deck (a ~10-minute pitch, roughly a dozen-odd slides),
a hard section page before a 1-2 slide "chapter" injects a hard narrative break — it stops the
story just as it builds momentum — while adding nothing to readability. Prefer a continuous
flow carried by action titles, with the executive summary acting as the chapter map. Remove a
divider when: the deck is short and reads just as clearly without it; the "chapter" it opens
holds only one or two slides; or the reset breaks the presentation's momentum. If a talk deck
needs a breath, a quiet `statement` beat disrupts flow less than a full section page.

Rule of thumb: a divider must open a chapter of at least ~3 proof slides and the deck must be
long enough to need navigation. Otherwise fold the chapter label into the next slide's subtitle
and drop the divider.

### Process Flow

Steps must share a disciplined silhouette. Outcome labels after arrows should be large enough
to read as design objects and centered in their target area when that improves balance.

### Statement / Closing

Statement slides are flexible. Decide the closing role:

- closing thesis
- decision request
- next actions
- proof recap
- legal/disclaimer close
- quote from a named person

Do not default to oversized left text plus company/date metadata. Omit company/date unless it
is legally or operationally required. A close should feel like the deck's final move, not a
fixed end-card.

## Density And Composition

- Avoid both underfilled pages and overstuffed pages. Dense does not mean cramped; it means
  the evidence field is full, aligned, and legible.
- If a page has too much whitespace, first enlarge the focal object, row heights, proof field,
  or interpretation rail. Do not add decorative objects.
- If a page is cramped, reduce claims, move supporting detail to notes/appendix, or split the
  slide. Do not shrink the typography below the token scale.
- Use whitespace by role: section separation, focal authority, quiet reset, or legal buffer.
  Unexplained whitespace is a defect.
- Repetition is useful only when the reader needs comparison. Repeating a fixed layout for
  unrelated claims makes the deck look generated.

## Evidence And Source Discipline

- Every evidence slide needs a source or a clear reason why the data is internal. A true
  citation names the organization, report, and date; a whole-deck internal origin (one
  meeting, one internal doc) is declared once in `meta.basis`, not stamped per slide.
- Separate source, assumption, and note. Do not bury assumptions inside source text.
- Future-looking claims require assumption language and, when possible, sensitivity or range.
- Bad news must use the same grammar as good news: show cause, action, and recovery path.
- Do not use placeholder sources or generic internal labels unless the work itself produced
  the analysis.

## Common Proof Arcs

### Earnings / IR

Typical arc: opening summary -> quarter highlights -> KPI trend -> revenue / profit bridge
-> driver decomposition -> guidance progress -> strategy update -> risks or assumptions ->
closing thesis. Challenge this sequence when the audience question requires a different arc.

### Proposal / Strategy

Typical arc: decision context -> market or problem -> customer/economic proof -> competitive
position -> strategy options -> operating model -> financial impact -> risks -> decision
request. Replace generic self-introduction slides with proof that changes the reader's mind.

## Defects To Hunt

- title and evidence mismatch
- a main object too small for the claim
- cards used as a default rather than an evidence structure
- YoY / delta text cramped against the value
- single-bar chart with no comparison
- fixed or left-heavy closing page
- section dividers in a short talk deck, or a divider opening a 1-2 slide chapter — a reset
  that breaks momentum without aiding readability; reserve dividers for long read decks
- grid/flex contract visible in notes but violated in render
- content block not vertically centered in the content area — asymmetric top/bottom margin
  makes a table, rail, or card block drift downward (or upward) instead of sitting centered
- large empty zones around small objects
- excessive source/footer prominence
- decoration used to create impact

