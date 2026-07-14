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

## Content Area Contract (vertical centering)

The body of every content slide lives in one shared **content area**: the band between the
bottom of the header block (title + optional subtitle) and the top of the bottom edge
(footer line, or the insight band when a slide has one). This band is the single source of
truth for vertical placement — patterns receive it as `(y, h)` and must not invent their own
top/bottom offsets from the slide edges.

Rules that keep the area consistent across the deck:

- **Symmetric breathing.** Apply the same gap below the header and above the bottom edge. An
  asymmetric margin (more air under the header than above the footer) makes any centered block
  read as *shifted down* even though the code "centered" it — the block sits centered inside a
  region that is itself off-center. Equal margins are what make centering look centered.
- **Center by default, top-anchor by intent.** Content-sized blocks (tables, 2x2 rails, hero
  clusters, short card pairs) center in the area so they do not float against the header or the
  footer. A block that deliberately reads top-down (a flow, a stepped roadmap) may top-anchor,
  but then its *floor* still comes from the shared area so it keeps clearance from the footer.
- **Reserve bands, do not special-case slides.** The insight band and any other fixed bottom
  strip are subtracted from the shared area once, generically, so every pattern inherits the
  correct floor. Never hard-code a per-slide nudge to fix one page — fix the shared area.
- **Fill, then center the remainder.** A block first grows to fill a healthy fraction of the
  area (avoid a tiny object in a large field); whatever height is left becomes equal top/bottom
  margin. Do not stretch a block to 100% of the area just to remove whitespace — centered
  breathing is preferable to a wall of edge-to-edge content.

## Container Breathing Contract

These rules govern any content-sized container (cards, table rows, roadmap cells, step
boxes). They exist because every violation reads as the same defect: text pressed against
an edge while another edge floats.

- **Symmetric insets.** A container sized from its content gets equal top and bottom inner
  padding. The bottom inset must never be visibly thinner than the top; height mistakes must
  eat slack space, not the bottom padding.
- **Measure with the drawing's own parameters.** Height estimates must use the exact
  line-spacing the renderer draws with, times the CJK line-box correction (see
  pptx-pitfalls). Any gap between estimated and drawn height is silently subtracted from the
  bottom inset — which is why under-measurement always shows up as bottom-edge crowding.
- **Proximity pairs.** A heading and its own body are one semantic pair: the intra-pair gap
  must be clearly smaller than the gap between items, which is smaller than the section gap.
  If a pair reads as two blocks, tighten the pair gap; do not widen the card.
- **Content-proportional rows.** In multi-row bands (roadmap workstreams, table rows,
  stacked cards), derive each row's height from its measured wrapped-line count plus a
  minimum symmetric pad; distribute leftover height evenly. Equal division starves exactly
  the rows with the most text — the opposite of what breathing requires.
- **Header-band edge lock.** A band header (chevron, phase arrow, column header strip)
  must share its right edge with the content column it captions; only a deliberate tip
  overhang may exceed it. Sizing the last header by the inter-header gap instead of the
  column's own edge rule leaves it visibly short — compute header width from the same
  edge rule as the cells below.
- **Cross-column row alignment.** In a two-column contrast whose items correspond 1:1
  (before/after, option A/B), the columns form rows: derive each row's height from
  max(left, right) and draw both columns' item i at the same y. Flowing each column
  independently makes one side drift downward and the correspondence unreadable.
- **Uniform row pitch when space allows.** Within an aligned item stack, prefer one
  shared pitch (the tallest block) for every row whenever it fits the region; fall back
  to per-row heights only when space forbids. Per-row heights expose wrap-estimate
  jitter as visibly uneven gaps ("the gap after block 1 is wider than after block 2"),
  which reads as sloppiness even when each row is individually correct.
- **Fill the band share.** Cards in an N-card band (e.g. an executive-summary stack) take
  the band's share of the region; with middle-anchored content the surplus becomes
  symmetric air. Shrink-wrapping cards while the band has room produces exactly the
  thin-inset defect this contract exists to prevent.
- **Reclaim height before cutting copy.** When a band's content plus minimum insets
  exceeds its share, exhaust the structural reclaims first — they preserve information:
  (1) release reserved bands that hold nothing (a slide with no source/assumption/note
  does not need the footer breathing; `body_region` extends the floor automatically),
  (2) move to the compact in-card line spacing, (3) compress inter-card gaps to the
  floor. The header is NOT a reclaim source: the subtitle is part of the header
  contract and is never dropped for density. Only when the structural reclaims still
  leave a deficit is the copy too long — then cut text, never typography.
- **Bottom edge-lock for conclusion strips.** A card that ends in a conclusion strip
  (rule + marker + outcome) anchors that strip to the card BOTTOM with the same inset as
  the top; the body content anchors to the top. All estimate error then lands in the
  flexible middle gap — never below the conclusion. Centering the whole group instead
  lets height mis-estimates sink the strip against the bottom edge, and it also breaks
  the cross-card alignment of the strips (shared strip height + bottom lock keeps every
  card's rule/marker/outcome on one line).
- **Group separators.** When a label column brackets several rows (merged first column) AND
  the row-to-group correspondence is hard to track — many rows per group, no other visual
  cue — mark each group boundary with a subtle dashed hairline whose role visibly differs
  from the normal row hairline. This is a judgment call, not a default: a short table whose
  groups read at a glance needs no extra line. Decide per table and opt in explicitly.

## One Box, One Group (the stack contract)

A group that reads as one thing is built as one text box. Label -> value -> note, heading ->
body, an interpretation rail's whole column: all of it lives in a single frame, as
paragraphs. The frame is then the only thing anyone positions, and the rhythm inside it
comes from the type itself:

- **Leading follows the type size.** `tokens.leading` maps a size to its line spacing, and
  every paragraph draws with the spacing its size declares. Text of the same size reads at
  the same density on every slide and in every card, because there is one place that decides
  it. The height a line actually occupies is `max(natural_em, spacing x cjk_line_box)` — a
  renderer never draws a line box shorter than the font's own line height — so every height
  and every gap is computed from that drawn height (`deck_text.drawn_line_h`), calibrated at
  300dpi.
- **Space between paragraphs is authored as ink distance.** The visible gap is between the
  glyph faces, not the line boxes: Japanese text carries room below its ink, and a large
  numeral sits high in a tall line box. `stack_block` measures the slack each neighbouring
  line already contributes (`deck_text.ink_slacks`) — that sum is the smallest gap that can
  exist — and sets the paragraph spacing to whatever is still needed to reach the gap you
  asked for (`tokens.layout.optical_stack.gap_in`). Junctions that share a `gap_name` are
  equalised to the largest of their floors, so the gap above a value equals the gap below it
  even though its line box is not symmetric.
- **Proximity is expressed in the gaps.** The gap inside a heading/body pair
  (`gap_in.heading_body`) is smaller than the gap between items (`gap_in.item`), so the pair
  reads as one thing and the items read as several.
- **A frame is the size of its text.** Height comes from the lines that will actually be
  drawn; a no-wrap label's width comes from the measured width of its string
  (`build_deck._label_w`). Frames sized this way sit beside each other cleanly, and
  `verify_deck` reports any pair that overlaps.
- **A chart's unit sits inside the plot.** The vertical-axis unit is a caption on the plot,
  not a line of its own: it is placed inside the chart region at the axis side, aligned to
  the top of the plot, with the insets declared once in `tokens.layout.chart.unit_note`.
- **Count lines in exactly one place.** Every height that depends on wrapping comes from
  `build_deck._text_lines`, which measures with the real font and the weight the text is
  drawn at.

Separate boxes are for things that are genuinely separate objects: a chart, a card's
background, a label pinned to a data point. Everything a reader takes in as one block is
one block.

## Message Slides (form and footprint)

A symbolic slide says its point in one line and supports it with one sentence. `lead` carries
the payoff at statement size; the sentence below it, set smaller and lighter, gives the
reason. Authors write both (`statement.lead` + `statement`), and a statement written as one
long clause joined by a dash is opened into the same two tiers automatically
(`build_deck.split_message`). The lead is composed as a form; the supporting sentence fills
its lines like any other prose and keeps a margin of whitespace on the right.

`build_deck.shape_message` chooses the measure and the line breaks of the lead together:

- Lines change where the sentence changes — at a comma or a dash, so the phrasing is visible
  in the silhouette. A clause too long for one line is broken at a phrase boundary, and a
  word is never broken.
- Line lengths are balanced (a DP over clause/phrase units minimises the spread), and the
  last line stays long enough to hold the sentence's weight.
- The measure is chosen shorter than the available width, so the block keeps a margin of
  whitespace on the right and reads as placed rather than packed. The block is then centred
  in the free region above the supporting strip.

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
