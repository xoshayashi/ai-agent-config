# Prompt Recipes

Use `scripts/build_act_slide_prompt.py` as the executable scaffold. Apply the three current source-of-truth references before final prompting:

1. `content-and-story.md`
2. `core-layout-and-typography.md`
3. `generation-review-packaging.md`

## Current Header Contract

```text
deck_wide_header_consistency_lock:
  H1: x=72 y=80 w=1528, one line, Noto Sans JP, 38pt/700, #2D332E
  subtitle: x=72 y=126 w=1528, one line, Noto Sans JP, 32pt/400, #626A64
header_copy_budget_lock:
  H1: <=28 Japanese full-width-equivalent characters
  subtitle: <=36 Japanese full-width-equivalent characters
  rendered_width: <=92% of each fixed text box
visible_outer_padding_lock:
  measure: top_visible_margin, bottom_visible_margin
  approval_1672: abs(top_visible_margin - bottom_visible_margin) <=4px
  approval_scaled: normalized difference ratio <=0.005
```

## Current Balance Contract

```text
edge_margin_balance_lock:
  T1 side margins: 96-160px
  T2-T4 side margins: 24-72px
intentional_space_coverage_lock:
  grid: 4 columns x 3 rows
  blank caps: T1<=5, T2<=2, T3/T4<=1
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
