# Prompt Recipes

Use `scripts/build_act_slide_prompt.py` as the executable scaffold. Apply the current source-of-truth references before final prompting:

1. `content-and-story.md`
2. `core-layout-and-typography.md`
3. `generation-review-packaging.md`
4. `grid-flex-layout.md`
5. `consulting-grid-rigidity.md`
6. `image-model-adaptive-construction.md`
7. `openai-gpt-image-2-best-practices.md`
8. `clarity-first-composition.md`

## Current Header Contract

```text
deck_wide_header_consistency_lock:
  H1: x=72 y=50 w=1492, one line, Noto Sans JP, 28pt/700, main_message role
  subtitle: x=72 y=123 w=1492, one line, Noto Sans JP, 20pt/400, sub_message role
  text_frame: square wrap, zero insets, top anchor, left align
rendered_header_scale_gate:
  H1 visible glyph height: 47-50px on 1672x941; calibrated center 48px
  subtitle visible glyph height: 33-35px on 1672x941; calibrated center 34px
  pilot deviation: <=2px from the first approved slide
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
header_furniture_contract:
  header_furniture_plan: surface=uninterrupted_canvas; visible_component_ids=[header_h1, header_subtitle]; visible_geometry_count=0
  side and bottom outer bands: quiet canvas; provenance footer is available through source_plan, with Source reserved for an approved external reference
  review: inventory the two registered header text components and continuous canvas surface
```

## Current Balance Contract

```text
edge_margin_balance_lock:
  body side margins: derive from the 78-92% width-utilization target; asymmetry is available when the body union remains optically balanced
intentional_space_coverage_lock:
  approval: every content slide passes 78-92% body width; footer-absent body height 82-94% of the reachable band; footer-present body height 78-90%
  container_fill: top-level container passes 82-94% width; footer-absent height 86-96%; footer-present height 84-94%
  area_fill: allocated child rectangles cover 58-80% of the available body band; meaningful text and object foreground covers 18-38% of the visible body envelope
  ink_fill: text ink covers 6-20% and meaningful-object ink covers 10-30% of the visible body envelope; their spatial union defines foreground fill
  proximity: group-internal gaps < group-separation gaps; heading-to-owned-content gap < separation above heading
  rhythm: repeated same-level gaps snap to the 8px grid within a half-unit
  centroid: area-weighted painted body components, including direct Grid children and the painted message box, 58-62% in both footer modes; deviation is repair_required
  vertical body utilization: apply the selected footer-mode height band; a pilot refines distribution inside that band
  footer_absent_closure: lowest meaningful body pixel y=857..869; actual H1-top margin and canvas-bottom body margin differ by <=12px
  header/body proportion: compact header, body as dominant visual mass
  safe-shell containment: all meaningful body pixels remain inside x=72..1600 and the selected vertical band
  canvas-edge balance: all meaningful pixels remain inside the equity_story_master shell with 50/72/17/72px top/right/bottom/left insets; the four outside bands remain measured quiet canvas; the body union's left/right clearances differ by <=8px; vertical balance follows its envelope and centroid target
focal_aspect_preservation_lock:
  single aspect-locked chart, diagram, or illustration: native aspect ratio within 5% and object width utilization 55-88%; the complete body passes the standard width and selected footer-mode height bands
grid_flex_layout_lock:
  parent_grid: 16 columns, 73px tracks, 24px gutters, grid lines 1..17
  baseline: 8px unit; line and baseline snap tolerance ±4px
  layout_tree: every body element belongs to exactly one declared grid or flex parent
  flex_plan: bounds, axis, wrap, line plan, gap, justify, align, and child basis/grow/shrink/min sizes
  flex_audit: main-axis fill 92-100%; cross-axis fill 82-100%; rendered basis deviation <=20%; overflow, clipping, and text overlap equal zero
consulting_grid_rigidity_lock:
  component_geometry: register every meaningful text anchor, module edge, icon/value center, rule endpoint, and connector port
  shared_axes: at least 3 vertical and 3 horizontal anchors; every major component shares one axis in each direction with another component
  peer_modules: width, height, padding, heading baseline, evidence baseline, and rule position agree within 4px
  structural_rules: role-based 1-2px rules terminate on declared grid lines or component centers
  connectors: grid-snapped horizontal/vertical segments, 0-2 right-angle bends, zero crossings
  score_gate: edge registration >=0.90; module consistency >=0.95; gap compliance >=0.95; rule and connector pass=1.00; structured-cell fill 0.65-0.85; orphan regions=0; weighted rigidity >=0.93
clarity_first_composition_lock:
  relationship: one primary relationship expressed through one visual grammar
  regions: 2-4 independently legible regions with one role each, explicit start, reading path, and landing
  economy: one visual anchor, one emphasis system, one connector set, zero redundant encodings
  enclosure: one common outer frame only for semantic containment
  softness: major surfaces use 8px or 12px radii; peer modules use 4px or 8px with >=0.95 consistency
luminous_tone_vocabulary_lock:
  token_source: build/references/design-tokens.json or --design-tokens PATH
  ambient: slide_background role
  lifted: neutral_panel role
  structural: structural_panel role
  focal: one single_focus_fill conclusion or decision region
  role_assignments: ambient->canvas; lifted/structural->named regions; focal->one named decision or conclusion atom
  consistency: one tone per semantic role, paired with labels or boundaries and repeated across the deck
external_reference_source_lock:
  external_none: visibility=none, reference fields empty, source_line=none
  external_visible: visibility=visible, reference_class=external_publication, traceable locator, Source entry begins exactly with `Source: `
  annotations: zero or one `Assumption: ` followed by zero or one `Note: `
  footer_atom: combine active entries with three spaces in one footer_master atom; one or two lines
  footer_absent: source and annotation sets are both empty
message_box_text_only_lock:
  empty_shape: {"boxes": []}
  icon_children: zero
  icon_atoms: zero
  geometry: x=72 y=796 w=1528 h=73 on 1672x941
  typography: one centered 17pt line, 25px line metric
  padding_y: 24px
  padding_x: 24px
  colors: single_focus_fill, single_focus_stroke, and main_message roles
```

The final prompt states desired visible states, measured acceptance bands, and the corrective action selected from the signed measurement difference.

## Stable Quality Vocabulary

- `all_text_font_lock: Noto Sans JP`
- Composition vocabulary remains open; describe the relationships, visual weight, reading path, and evidence role instead of selecting from a fixed catalog.
- Icons stay inside compact non-message components; message boxes use the dedicated text-only contract.
- Decision-relevant numbers follow the evidence and use the quantity needed to support the decision.
- `single_focus_fill` is a selective signal and remains quieter than `primary_accent`.
- Footer/source/table-note text uses the `footer` semantic role.
- Provenance rule: `Use Source: only for an approved external reference; use Assumption: and Note: for labeled internal provenance; combine active entries in the canonical footer_master.`
- Artifact rule: Output files: keep `slides_final/` as the only loose-PNG master.
- Illustration vocabulary: `technical editorial line illustration`.
