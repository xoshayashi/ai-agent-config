# Prompt Recipes

Use `scripts/build_act_slide_prompt.py` as the executable scaffold. Apply the three current source-of-truth references before final prompting:

1. `content-and-story.md`
2. `core-layout-and-typography.md`
3. `generation-review-packaging.md`

## Current Header Contract

```text
deck_wide_header_consistency_lock:
  H1: x=72 y=72 w=1528, one line, Noto Sans JP, 38pt/700, #2D332E
  subtitle: x=72 y=136 w=1528, one line, Noto Sans JP, 32pt/400, #626A64
rendered_header_scale_gate:
  H1 visible glyph height: 42-50px on 1672x941
  subtitle visible glyph height: 28-36px and 65-78% of H1
  pilot deviation: <=4px when a pilot exists
rendered_body_scale_gate:
  section headings: 28-34px visible height
  primary body labels: 22-28px
  supporting text: 18-24px
  integrated takeaway: 26-32px and <= section-heading scale
header_copy_budget_lock:
  H1: <=28 Japanese full-width-equivalent characters
  subtitle: <=36 Japanese full-width-equivalent characters
  rendered_width: <=92% of each fixed text box
canvas_edge_and_optical_balance:
  measure: header anchor, body envelope, footer clearance, body-only optical centroid
  approval: header matches the deck master; body stays inside its band and passes pilot-calibrated optical review
canvas_furniture_allowlist:
  top outer band: exact H1 and subtitle only
  side and bottom outer bands: quiet canvas, plus a genuine source on the approved footer baseline when source_line is traceable
  review: inventory every visible outer-band mark and repair any mark absent from frozen exact_text
```

## Current Balance Contract

```text
edge_margin_balance_lock:
  T1 side margins: 48-96px
  T2-T4 side margins: 24-72px
intentional_space_coverage_lock:
  grid: 4 columns x 3 rows
  calibration: occupancy, blank cells, region weights, and blank bands are compared within the selected layout family and approved pilot
  proximity: group-internal gaps < group-separation gaps; heading-to-owned-content gap < separation above heading
  rhythm: repeated same-level gaps snap to the 8px grid within a half-unit
  centroid: body-only deviation triggers multimodal review rather than automatic centering
  vertical body utilization: pilot-calibrated; without a pilot preserve deliberate breathing rather than a fill target
  header/body proportion: compact header, body as dominant visual mass
  safe-shell containment: all meaningful body pixels remain inside x=72..1600 and the selected vertical band
  canvas-edge balance: all meaningful pixels remain inside the four-side 72px safe shell; comparable opposite-side clearances differ by <=8px
focal_aspect_preservation_lock:
  single chart, diagram, or illustration: native aspect ratio within 5%
```

The final prompt states desired visible states, measured acceptance bands, and the corrective action selected from the signed measurement difference.

## Stable Quality Vocabulary

- `all_text_font_lock: Noto Sans JP`
- Layout candidates may include `asymmetric main + context region`, `center-hub + surrounding-nodes`, `top-map + bottom-detail-table`, and `bottom-main compact`; select by message rather than rotation quota.
- Icons stay inside compact component geometry; `icons must not enlarge boxes`.
- Decision-relevant numbers follow the evidence; `Do not impose a default numeric cap`.
- Honey is a selective signal: `Honey surfaces must feel quieter than Petrol surfaces`.
- Footer hierarchy uses footer/source/table-note text `#6E756E`.
- Source rule: `Source: render only real traceable source names; when no real source exists, use source_line: none and do not show a Source footer.`
- Artifact rule: Output files: keep `slides_final/` as the only loose-PNG master.
- Illustration vocabulary: `technical editorial line illustration`.
