# Grid And Flex Strategy

Grid/flex is the structure contract for the slide. It creates consistency, density, and
editorial precision without forcing a fixed template. Use it whenever a page feels loose,
overly empty, cramped, or visually inconsistent with the deck.

## Grid Contract

Think in relationships, not coordinates. A slide must declare:

- **grid_role_map**: header, body, proof field, interpretation rail, source/footer, and any
  secondary band.
- **column_span_plan**: how each major object spans the page grid.
- **alignment_spine**: the hard line that organizes the page: left edge, centerline, baseline,
  top edge, or chart axis.
- **body_band_plan**: vertical bands, row heights, and section gaps.
- **edge_lock**: shared edges that keep objects from floating.
- **cross_slide_consistency**: which placements stay stable across the deck.

This contract is not a fixed template. It is the page-specific explanation of why the layout
will hold together.

## Flexbox Mental Model

For every body cluster, define:

- **main_axis**: row, column, wrapped row, or stacked bands.
- **cross_axis_align**: start, center, end, baseline, or stretch.
- **gap_scale**: section gap, group gap, object gap, and metric-subline gap.
- **grow_rule**: the object that expands to use available space.
- **shrink_guard**: the object that must not shrink.
- **wrap_rule**: what may wrap, maximum line count, and fallback when it overflows.
- **fill_repair**: how to use dead space: enlarge evidence, widen the proof field, add a
  rail, convert to rows, or split the slide.

## Fine-grained adjustment loop

After each render:

1. Check the header frame, body top, body bottom, and source/footer line.
2. Check whether the main body occupies enough of the content field. If not, enlarge the
   focal object or change the composition before adding decoration.
3. Check object relationships: shared left edges, equal row heights, consistent baselines,
   and deliberate section gaps.
4. Check text hierarchy: title, section heading, body, metric value, metric subline, source.
5. Check metric-subline spacing. YoY, delta, vs plan, and prior-year text must sit on a
   separate line with visible air below the value.
6. Check comparative charts. A bar or column chart must show comparison across categories,
   periods, segments, or scenarios. A single current value should become a hero number,
   gauge, range, table row, or facts rail.
7. Check whether the design looks fresh through scale and composition rather than a repeated
   layout shell.

## Banker Order + Modern Freshness

Layer 1: investment-bank / strategy-consulting discipline.

- stable title and source frame
- one action title
- one proof hierarchy
- clear table/chart accountability
- understated color
- no decorative motion or generic cards

Layer 2: controlled freshness.

- asymmetric but aligned proof fields
- large object scale
- interpretation rails
- current-position gauges
- editorial rule lines
- evidence strips
- quiet pages used for rhythm
- stronger center alignment only when it improves comprehension

Freshness fails when it weakens comparability, source discipline, or reading order.

## Strategy Examples, Not Presets

- **Metric proof page**: large value cluster on the left, comparison chart on the right,
  facts rail under the chart. Lock value baseline to chart plot top.
- **Guidance progress page**: current-position gauge plus facts rail. Do not draw a single
  standalone bar.
- **Process page**: steps share height; outcome labels are centered and large enough to act
  as design objects, not footnotes.
- **Closing page**: choose the role from the deck. Use thesis + proof strip, decision request,
  next actions, legal close, or quote. Avoid fixed left text and redundant company/date.
- **Dense table page**: a highlighted row or column becomes the protagonist; row heights grow
  to fill the content field and avoid a tiny table floating in whitespace.

## Review Prompts

- Can the layout be described as relationships rather than coordinates?
- Is the main proof field large enough for the claim's importance?
- Are gaps consistent by role, not arbitrary?
- Does each repeated page repeat grammar only where the reader needs comparison?
- Would removing the grid/flex contract make the slide visibly worse?
