# Prompt Recipes

Use these recipes after applying `embedded ACT design system in SKILL.md`. Keep final prompts concrete, coordinate-aware, and explicit that final bitmap generation uses `gpt-image-2`.

Quality anchor vocabulary for evaluation and prompt consistency:
- all_text_font_lock: Noto Sans JP
- layout modes include asymmetric main + context region, center-hub + surrounding-nodes, top-map + bottom-detail-table, and bottom-main compact
- Honey surfaces must feel quieter than Petrol surfaces
- visual language is technical editorial line illustration, not generic decoration

## Contents

- Image Generation Settings Block
- Text To Slide Structure Prompt
- Base Image Contract
- Single Slide Planning Block
- Single Slide Image Prompt
- Deck Planning Prompt
- Screenshot Or Render Repair Prompt
- Insight Decision Prompt
- Balance Repair Prompt
- Self-Audit Prompt

## Image Generation Settings Block

```text
generation_mode: new_image / image_edit
image_model: gpt-image-2
image_size: 1536x864 for draft, 2048x1152 for working review, or 2560x1440 for final 16:9
image_size_label: 1920x1080 is FHD delivery only; 2048x1152 is 16:9 2K-width; 3840x2160 is 4K UHD
image_quality: low for draft, medium/high for final or text-heavy slides
image_background: opaque or auto
image_output_format: png
image_output_compression: none unless jpeg/webp
image_moderation: auto
image_n: 1 for final text-heavy slides; variations only for drafts
image_streaming: optional for exploration, final QA uses completed image
image_delivery_size: 1920x1080 after resize if exact ACT delivery size is required
generation_route: Codex built-in image generation
generation_status: generated_with_builtin_gpt-image-2 / blocked
pptx_delivery: image-only PPTX roll-up after generated PNGs pass QA, unless user asks for files only
pptx_status: pending_generated_images_and_pre_package_image_review / created / blocked
google_slides_delivery: optional image-only roll-up after generated PNGs pass QA when explicitly requested
speaker_notes_status: drafted / inserted / blocked
post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion
all_generated_images_reviewed: false until every output PNG has been opened and reviewed
weak_slide_regeneration_queue: [slides needing regeneration or edit before completion]
content_quality_status: pending / approved / repair_required
design_quality_status: pending / approved / repair_required
deck_unity_status: pending / approved / repair_required
completion_ready_status: blocked until all image, content, design, and deck-unity gates are approved
regenerate_until_quality_approved: keep regenerating or editing weak slides until completion_ready_status is approved
generation_block_rule: if generation or repair is blocked, mark completion_ready_status: blocked and do not package or report complete
review_manifest: required JSON record covering every generated PNG before PPTX packaging
review_manifest_status: approved
validate_review_manifest: run before PPTX packaging
output_artifact_mastering_lock: slides_final/ is the only loose-PNG master for approved generated slide images
single_final_png_master_lock: review manifests and package mappings reference the slides_final/ master path
no_duplicate_png_output_lock: do not keep duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/
contact_sheet_mastering_lock: keep one retained contact sheet by default, render_check/contact_sheet_review.png, built from slides_final/
single_contact_sheet_policy: do not retain parallel contact_sheet_generated*, contact_sheet_package*, and contact_sheet_pdf_render* files for the same slide set
```

Do not request `1920x1080` directly from `gpt-image-2`; use a valid multiple-of-16 image-generation size and resize after generation when needed.
Do not substitute local rendering, screenshots, SVG, PIL, canvas, or PPT exports for final image-generation output.
PPTX is a delivery wrapper only; never use PPTX, PowerPoint export, screenshots, local rendering, HTML, SVG, canvas, or PIL to create final PNGs.
Correct order: gpt-image-2 PNG generation -> PNG review/repair -> PPTX roll-up.
If gpt-image-2 image generation is blocked, stop rather than manufacturing final PNGs through PPTX or local rendering.
completion_blocker: do not report complete while any generated slide has blocker, major, deck-consistency, content-quality, or design-quality issues.
PPTX package gate requires an approved review manifest.
Output artifact gate: keep approved generated PNGs only under `slides_final/`; `slides_package/` contains PPTX, speaker notes, review manifest, and metadata only; `render_check/pdf_pages/` is disposable render QA output only.
Contact sheet gate: keep one retained `render_check/contact_sheet_review.png` by default. If package/PDF render QA needs comparison, create one `render_check/contact_sheet_delivery_compare.png` or `render_check/render_diff_report.json`, not parallel generated/package/pdf_render contact sheets.

## Base Image Contract

```text
Draw a 16:9 strategy slide image with gpt-image-2.
Generate at 1536x864 for drafts, 2048x1152 for 16:9 2K-width working review, or 2560x1440 for final output.
Plan all layout using a 1672x941 coordinate basis, with ACT delivery target 1920x1080 after resize if required.
Treat 1920x1080 as FHD/1080p delivery, 2048x1152 as practical 16:9 2K-width generation, and 3840x2160 as 4K UHD generation.
Use a shared 12-column grid, 8px spacing rhythm, and precise header/footer anchors.
For decks, define and reuse one deck header master. Apply header_identity_lock: the header is always the same compact left vertical line + H1 + subtitle system, never a slide-specific decoration surface. Treat the header as the lowest-freedom component: repeat the same left accent, H1, subtitle, visual alignment rule, body-start y, header safe area, and clear zone in every slide prompt. no_header_ranges_in_final_prompts: final prompts must use exact selected x/y/w/h/color/font_family/font values for the header, not ranges. Apply header_left_accent_master_lock: the accent is a fixed header-block anchor tied to the H1/subtitle stack and copied verbatim across the deck, not a page-edge rail, tall sidebar, body marker, chapter stripe, or ornament. Apply header_left_accent_reference_lock: match the approved 1672x941 reference geometry x=50 y=40 w=10 h=120 color #008A80 unless a newer embedded master is supplied. Apply header_left_accent_shape_lock: one solid 10px vertical rectangle, square or 0-2px radius ends, no pill caps, glow, shadow, gradient, split segments, or duplicate marks. Apply header_left_accent_controlled_overhang_rule: controlled 8-16px top overhang above the first visible H1 glyph top is correct because the accent anchors H1 + subtitle. Apply header_left_accent_top_protrusion_blocker: more than 18px above H1, page-top floating, clipping outside header_safe_area, detachment from H1/subtitle, or body intrusion is a blocker. Apply header_integrity_blocker_lock: malformed, missing, oversized, recolored, right-decorated, or intruded headers are blockers.
For decks, apply deck_tone_signature_lock: preserve one material system for base, typography, rule weight, card/table surfaces, icon stroke, illustration linework, accent budget, density rhythm, Insight treatment, and Source behavior while varying only claim-led layouts.
For decks, apply illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system. Define illustration_style_sheet before generation and reuse it verbatim: flat 2D business and healthcare workflow illustration; simplified people; tablets, laptops, document stacks, CRM panels, report cards, timelines, handoff arrows, and small icon badges; soft pale mint or warm gray fills; Petrol and charcoal linework; restrained Honey highlights; consistent 2-3px stroke, crop, face detail, body proportion, and fill opacity.
For decks, apply post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion. Maintain all_generated_images_reviewed, weak_slide_regeneration_queue, content_quality_status, design_quality_status, deck_unity_status, final_image_quality_status, and completion_ready_status; use regenerate_until_quality_approved until the queue is empty or generation is blocked.
For decks, define layout_diversity_plan and layout_rotation_guard before final prompts. Choose layout families from full-field, asymmetric main/supporting-context, balanced diptych, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase patterns according to the slide claim and evidence type.
For decks, use opening_density_gate on slide 1: make it an opening_thesis_slide, set first_slide_not_title_only, and combine the memorable main phrase with a core thesis, 2-4 proof/tension points, a visible market-shift/matrix/causal-map/wedge structure, and a bridge into the deck.
Request Noto Sans JP for every visible string, including Latin/English letters, numbers, symbols, and Japanese. Do not request or mix any other typeface; keep text short enough to audit.
max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
For ACT work, use Forest Charcoal #2D332E for H1/body, Ink-2 #4D544E for subtitle, Ink-3 #6E756E for footer/source/table-note text, Petrol #008A80 for structure, and Honey only as a quiet decision signal.
Lock header/footer text colors as one Ink-family hierarchy: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E. Do not use Petrol, Honey, yellow, or arbitrary gray for header/footer text.
source_real_only_lock: render Source footer only for real traceable external/provided sources; if no real source exists, set source_line: none and draw no Source footer text.
source_placeholder_blocklist: never use placeholder provenance labels such as brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source text.
source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists. Do not drop real source names to reduce visual density; shorten or group source names instead.
source_separator_lock: no horizontal divider, rule, underline, or hairline above Source. Treat the footer/source baseline as an invisible alignment position, not a visible stroke.
density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting.
structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide claim, evidence, and audience context.
claim_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide claim before adding supporting elements.
region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette.
composition_fit_plan: set the main visual field, supporting regions, whitespace role, and Insight footprint before generation so the canvas has deliberate occupancy and breathing room.
secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field.
body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions.
No slide numbers, no title kicker, no numbered header badge.
Use the embedded palette with restrained contrast, flat fills, quiet rules, and purposeful visual subjects.
Use small Lucide-style line icons only as quiet wayfinding where they clarify reading order.
Use human-designed editorial/vector illustrations and purpose-built motifs when the claim needs memory, freshness, scanning help, or comparison support; do not add them by quota. Keep charts, tables, matrices, or roadmaps as the primary structure when they carry the argument.
Use calm operating-deck visual quality traits: near-white warm base, compact fixed header, thin structural rules, pale equalized cards/tables, restrained line icons, small technical editorial illustrations, and deliberate canvas occupancy. Treat these as design treatment only, not as a reason to change slide count, claim order, or storyline.
Apply near_white_slide_base_lock: use #FFFDFC as the default ACT slide canvas, with #FAFAF7 only as a subtle warm off-white tint; keep #F7FBF9 for panels/cards, not the page background, and avoid darker cream/beige page bases.
Design information density before image generation. Density should answer more of the reader's decision question in one view through hierarchy, evidence, comparison, annotation, source cues, and context layers; do not use smaller type, extra decoration, or visual noise as density.
Do not minimize numbers by default. Keep decision-relevant sourced or explicitly assumed numbers when they support comparison, sizing, prioritization, credibility, or decision-making.
Message boxes and Insight surfaces must use flat solid fills only; no patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations inside the box.
Apply message_box_scale_lock: message boxes are compact interpretation surfaces, not display surfaces; use one short judgment sentence, prefer one line, allow two lines maximum, and trim, move explanation to notes/body, or remove the component instead of increasing the box.
Apply message_box_text_size_lock: Insight/message-box text defaults to 20-24pt, uses 24-26pt only by exception, stays at least 6pt smaller than the selected H1, remains visually below subtitle, and must never become a second title.
Apply message_box_compactness_blocker_lock: an Insight/message-box that dominates the slide, behaves like a banner, spans beyond the interpreted region, grows tall to carry prose, or compensates for layout imbalance is a blocker.
Honey message boxes have one fixed treatment: #F5E2A8 flat pale fill, #C49A2C 4-5px full-height left accent line, #2D332E text. Avoid saturated yellow fills, dark yellow boxes, large yellow areas, and yellow title underlines.
Preserve distinct claims as distinct slides. Combine slides only when claims repeat, the same comparison must be seen together, or the user explicitly requests a shorter deck.
Choose a concrete visual grammar per slide from the claim and evidence. Select the projection, viewpoint, abstraction level, motif, and level of detail deliberately; the chosen visual can be a diagram, scene, system view, comparison, object detail, spatial view, sequence, or metaphor when it clarifies the argument.
Create polish through clear figure-ground separation, composed region balance, precise edges, useful details, and calm surface treatment rather than arbitrary pseudo-depth or glossy concept-art effects.
When the user asks to raise temperature, use `creative_variance: high` rather than claiming an API temperature parameter. High variance means more freedom in viewpoint, crop, asymmetry, visual metaphor, and layout rhythm, while all brand, header, exact text, grid, and source constraints remain locked.
Required image model: gpt-image-2.
Final slide image files must be actual Codex built-in image-generation outputs. Local wireframes or deterministic renders are not final generated images.
For multi-slide decks, roll approved generated PNGs into a PPTX deck as image-only full-bleed slides, then attach speaker notes when the packaging route supports notes. Speaker notes are generated from the deck structure, not from image generation. Apply speaker_notes_depth_lock: notes should be substantial Japanese PPT talk scripts, normally 4-7 sentences or roughly 180-320 Japanese chars per slide, with opening framing, 2-3 evidence/assumption talking points, implication, caveat/source context when relevant, and transition cue. Create Google Slides only when explicitly requested.
Before PPTX or Google Slides roll-up, run post_generation_design_balance_check on actual generated PNGs: whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, header integrity, and layout family rhythm.
```

## Single Slide Planning Block

This is the canonical planning template. Mirror this field set in scripts and task outputs.

```text
slide_claim:
primary_guideline:
guideline_priority:
generation_mode:
image_model:
image_size:
image_size_label:
image_quality:
image_background:
image_output_format:
image_moderation:
image_n:
image_streaming:
image_delivery_size:
generation_route:
generation_status:
output_files:
output_artifact_mastering_lock:
single_final_png_master_lock:
no_duplicate_png_output_lock:
contact_sheet_mastering_lock:
single_contact_sheet_policy:
google_slides_delivery: optional only when explicitly requested
google_slides_status: not_requested unless explicitly requested
google_slides_title: N/A unless explicitly requested
google_slides_file_id: N/A unless explicitly requested
google_slides_url: N/A unless explicitly requested
google_slides_slide_count: N/A unless explicitly requested
google_slides_route: N/A unless explicitly requested
google_slides_image_mapping: N/A unless explicitly requested
google_slides_speaker_notes_mapping: N/A unless explicitly requested
pptx_delivery:
pptx_status:
pptx_output_path:
pptx_slide_count:
pptx_packaging_route:
pptx_image_mapping:
pptx_speaker_notes_mapping:
speaker_notes_plan:
speaker_notes_status:
speaker_notes_depth_lock:
speaker_notes_text:
opening_slide_role:
first_slide_not_title_only:
opening_density_gate:
layout_archetype:
layout_family:
composition_family:
layout_diversity_plan:
layout_rotation_guard:
layout_sequence_table:
grid_mode:
column_spans:
row_tracks:
column_tracks:
separator_x:
outer_padding:
major_regions:
coordinate_inventory_1672:
  - object:
    x:
    y:
    w:
    h:
master_components:
deck_master_refs:
deck_tone_master_lock:
visual_design_quality_traits:
imageability_lock:
concrete_visual_anchor:
observable_scene_or_object:
viewpoint_crop:
specific_visual_details:
visual_specificity_plan:
editorial_polish_repair_loop:
visual_subject_open_set:
claim_led_composition_lock:
region_balance_policy:
composition_fit_plan:
secondary_region_integrity_lock:
body_silhouette_lock:
post_generation_design_balance_check:
pre_package_image_review:
post_generation_full_deck_review_loop:
all_generated_images_reviewed:
image_review_matrix:
deck_consistency_matrix:
weak_slide_regeneration_queue:
content_quality_status:
design_quality_status:
deck_unity_status:
completion_ready_status:
regenerate_until_quality_approved:
generation_block_rule:
review_manifest:
review_manifest_status: approved
validate_review_manifest:
whitespace_occupancy_balance_status:
typography_balance_status:
color_consistency_status:
outer_padding_consistency_status:
header_integrity_status:
deck_header_master_lock:
  coordinate_basis:
  status: exact_required_before_generation
  header_safe_area:
  vertical_line:
  header_line_top_rule:
  header_left_accent_master_lock:
  header_left_accent_reference_lock:
  header_left_accent_shape_lock:
  header_left_accent_controlled_overhang_rule:
  header_left_accent_top_protrusion_blocker:
  h1:
  subtitle:
  visual_alignment:
  body_start_y:
  upper_right_clear_zone:
  forbidden_header_elements:
header_footer_text_color_lock:
  h1: "#2D332E"
  subtitle: "#4D544E"
  footer_source_table_note: "#6E756E"
  forbidden_text_colors: Petrol, Honey, yellow, arbitrary gray
message_box_scale_lock:
message_box_text_size_lock:
max_text_size_lock:
petrol_usage_lock:
visual_asset_judgment:
component_inventory:
equalized_groups:
shared_edges:
hand_placed_exceptions:
visual_richness_role:
visual_asset_role:
icon_system_plan:
signature_visual_plan:
illustration_region:
illustration_presence:
illustration_intensity:
human_designed_illustration_style:
creative_variance:
density_tier:
density_layers:
density_design:
  reader_mode: scan / read / reference
  decision_question:
  information_units: [claim, context, comparison, trend, mechanism, risk, implication, assumption, source]
  density_levers: [KPI strip, supporting context region, evidence strip, small multiples, annotations, benchmark/context column, source cue]
  overload_controls: [one dominant structure, max three major regions, body >=18pt equivalent, grouped labels, no decorative density]
information_unit_budget:
density_number_policy: no default cap on decision-relevant numbers; remove only unsupported, redundant, unreadable, or decorative numbers
density_guardrails:
header_anchor:
  vertical_line:
  h1:
  subtitle:
  body_start_y:
  upper_right_clear_zone:
footer_anchor_baseline:
table_note_microline:
source_real_only_lock:
source_placeholder_blocklist:
source_line_lock:
source_separator_lock:
source_line:
source_policy:
brand_accent_usage_budget:
brand_accent_system_role:
insight_decision:
  keep_remove:
  reason:
  variant:
  deck_count_check:
  geometry:
  height:
  radius:
  padding:
  left_accent:
  background:
  text:
human_crafted_feel:
qa_risks:
blocking_unresolved_items:
```

Then output:

```text
image_model: gpt-image-2
prompt_readiness:
draft_image_prompt_scaffold:
negative_prompt_hard_blockers:
post_generation_audit:
```

Block generation if `layout_archetype`, `layout_family`, `layout_diversity_plan`, `layout_rotation_guard`, `layout_sequence_table`, `grid_mode`, `coordinate_inventory_1672`, `master_components`, or `source_policy` remains unresolved.

## Single Slide Image Prompt

```text
Brief:
[paste user brief]

ACT slide contract:
- primary_guideline is the embedded ACT design system in SKILL.md
- embedded ACT style is the default, palette, typography, and components
- use embedded ACT design mechanics
- use image_model gpt-image-2
- use generation_mode new_image for new single-slide images or image_edit for screenshot/reference repair
- use image_size 1536x864 for drafts, 2048x1152 for 16:9 2K-width working review, or 2560x1440 for final output; resize to 1920x1080 after generation if exact FHD/1080p delivery size is required
- treat strict DCI 2K 2048x1080 and DCI 4K 4096x2160 as non-target cinema sizes, not ACT 16:9 slide generation sizes
- use image_background opaque or auto, never transparent
- use png for slide fidelity unless latency or file size matters
- use moderation auto by default
- use n=1 for final text-heavy slides; use multiple variations only for draft exploration
- 1 slide = 1 claim
- 1 dominant structure
- for deck openers, first_slide_not_title_only: use opening_thesis_slide with a thesis, 2-4 proof/tension points, a visible structure, and a bridge
- select one layout_archetype and grid_mode before writing text
- define layout_family, layout_diversity_plan, and layout_rotation_guard for decks before writing final prompts
- define coordinate_inventory_1672 with x/y/w/h for major objects
- define master_components and deck_master_refs before repeating cards, rows, icons, or bands
- define deck_header_master_lock before any slide prompt and repeat it verbatim across the deck; exact header values are required before generation
- apply visual_design_quality_traits as design treatment: near-white warm base, compact fixed header, thin rules, pale equalized surfaces, restrained icons/line drawings, intentional canvas occupancy
- apply near_white_slide_base_lock: #FFFDFC default slide canvas, optional #FAFAF7 subtle tint, no darker cream/beige page background
- define component_inventory, row_tracks, column_tracks, equalized_groups, and shared_edges
- lock header anchor first: left vertical line + H1 + subtitle + visual alignment + header safe area + body_start_y + upper-right clear zone
- apply header_identity_lock and header_integrity_blocker_lock before visual polish
- apply deck_tone_signature_lock before slide-level variation; vary layouts from claims while keeping material language consistent
- apply illustration_tone_lock and illustration_style_sheet before image prompting; keep people, devices, document objects, UI panels, icon badges, linework, fills, and crop consistent across the deck
- lock footer_anchor_baseline even when source_line is none
- lock header_footer_text_color_lock: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E
- keep source_line separate from table_note_microline
- source_real_only_lock: render Source only for real traceable external/provided sources; otherwise source_line none and no Source footer
- source_placeholder_blocklist: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source
- source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
- source_separator_lock: no horizontal divider, rule, underline, or hairline above Source
- output_artifact_mastering_lock: slides_final/ is the only loose-PNG master; package and render-check folders hold only derivative artifacts
- no_duplicate_png_output_lock: no duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/
- contact_sheet_mastering_lock: one retained contact_sheet_review.png by default; comparison sheet only when delivery QA requires it
- Do not drop real source names to reduce visual density; shorten or group source names instead.
- draft speaker_notes_text for every deck slide before image generation; apply speaker_notes_depth_lock so PPT notes are substantial Japanese talk scripts, not terse bullets; keep notes off the slide image and out of the exact on-slide text
- assign visual_richness_role, illustration_intensity, creative_variance, and density_tier before generation
- define density_design before generation: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails
- density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
- consulting_structure_bias: gently prefer strategy-consulting style structure when it clarifies the claim, without forcing it on every slide
- structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits
- use issue trees, driver trees, 2x2 matrices, value chains, funnels, waterfalls, KPI bridges, decision tables, before/after bridges, or hypothesis-evidence-implication rows when they improve the reader's decision path; skip them when they would clutter the focal claim
- structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
- add density through decision-relevant comparisons, benchmarks, units, denominators, assumptions, annotations, evidence strips, supporting context regions, small multiples, and source cues; never through smaller type or decorative illustration detail
- imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
- editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
- visual_subject_open_set, claim_led_composition_lock, and composition_fit_plan: choose the visual subject, focal relationship, and canvas occupancy from the argument before image prompting
- region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette
- secondary_region_integrity_lock: in split or auxiliary-region layouts, design the secondary region as a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
- body_silhouette_lock: make the body read as one closed visual block with aligned outer edges, lower edges, and footer clearance
- make abstract claims imageable through a specific operating view, workflow handoff, document stack, data row, map route, queue, machine cell, screen state, evidence artifact, or customer moment that fits the claim
- keep decision-relevant numbers when they are legible and grouped; do not force a minimal-numbers rule
- use human-designed editorial/vector illustrations for chapter openers, turning points, complex systems, and final vision slides
- keep illustration subordinate: a clear focal motif, only useful supporting details, clean controlled flat 2D linework, crisp silhouettes, restrained fills, rounded UI panels, small icon badges, a projection/viewpoint chosen from the claim, no rough sketch, no arbitrary pseudo-depth, and no glossy AI concept-art finish
- max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
- use ACT typography: H1 30-34pt, subtitle 21-23pt, body 18pt equivalent
- use ACT header rules: H1 Forest Charcoal #2D332E, subtitle #4D544E, exact compact left vertical line, no blue H1, no right-side header decoration
- use the default exact compact ACT header unless the user explicitly provides a newer embedded master: 1672x941 basis; header_safe_area x=44 y=24 w=1584 h=136; vertical_line x=50 y=40 w=10 h=120 #008A80; H1 x=88 y=34 w=1332 max_lines=1 size=32pt weight=700 line_height=1.14 #2D332E; subtitle x=88 y=82 w=1332 max_lines=1 size=22pt weight=400 line_height=1.18 #4D544E; visual_alignment accent top uses controlled 8-16px overhang above the first visible H1 glyph top, never more than 18px above it, and accent bottom sits 4-10px below subtitle lower visual edge; body_start_y=180; upper_right_clear_zone x=1420 y=24 w=208 h=88 empty
- make the slide feel human-crafted through priority, breathing room, and editorial rhythm
- keep the slide in a strategy operating-deck look: useful occupancy, small explanatory visuals, crisp rules, low-contrast surfaces, and no ornamental depth
- let structure, spacing, rules, numbers, and typography carry hierarchy
- use the embedded ACT design system's accent color structurally with a restrained area budget; for ACT work, Petrol uses a 6-12% area budget and never appears as body text
- use Insight component only if it adds interpretation or decision weight and is compatible with the embedded ACT design system
- if Honey is used in ACT or compatible guidelines, use #F5E2A8 flat pale fill + #C49A2C 4-5px full-height left accent line + #2D332E text, one component maximum
- keep all Insight/message boxes flat solid fill only; no patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations
- apply message_box_scale_lock: keep Insight/message boxes compact, one short judgment sentence, one line preferred and two lines maximum; trim or move explanation to notes instead of growing the surface
- keep Insight/message-box text 20-24pt by default, 24-26pt only by exception, at least 6pt smaller than H1, visually below subtitle; it must not become a second title or second hero headline
- keep Insight/message-box surfaces compact; if the surface starts to dominate, behave like a banner, or rescue weak layout, shorten text, narrow it, move detail to body/notes, or remove it
- keep Honey quiet: no saturated yellow fill, no dark yellow message box, no large yellow area, and no Honey color variation across a deck
- Source: render only real traceable source names; when no real source exists, use source_line: none and do not show a Source footer. Never use brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, working assumptions, or other placeholder provenance as Source text.
- Output files: keep `slides_final/` as the only loose-PNG master. Do not duplicate approved generated PNGs into `slides_package/` or `render_check/pdf_pages/`; package and render-check artifacts must reference the `slides_final/` master.
- Keep only one retained contact sheet by default: `render_check/contact_sheet_review.png`. Use one comparison contact sheet or a render diff JSON only when delivery/render QA needs it.
- final bitmap generation must use gpt-image-2
- if actual Codex built-in image generation is blocked, stop and report the blocker; do not create final images via code rendering or a user-key workaround
- after all generated PNGs pass QA, create a PPTX roll-up unless the user asks for image files only: one full-bleed generated PNG per slide, same order, no extra overlays, and speaker notes inserted when supported; create Google Slides only when explicitly requested
- place every literal string under `Exact text` in quotes and request ONLY those strings
- use "Draw" or "Create" for generation prompts, and "Edit" plus preservation language for repair prompts
- for healthcare, finance, law, or regulated domains, do not add market, clinical, regulatory, or compliance facts unless sources are provided or researched

Output:
1. canonical planning block
2. image_model: gpt-image-2
3. final image prompt
4. negative prompt
5. generation route and output files, or blocker
6. PPTX roll-up status with speaker notes status for decks
7. Google Slides roll-up status when explicitly requested
8. post-generation audit checklist
```

## Text To Slide Structure Prompt

```text
Convert the following long text into a guideline-aware slide-image deck structure before writing any image prompt.

Process:
1. Extract the deck thesis and audience decision.
2. Create intake_map with source_span_id values for chapters, facts, quotes, assumptions, and uncertainties.
3. Choose one storyline frame: SCQA, problem-solution-evidence, past-present-future, market-problem-solution-moat, or investment-thesis-risk-milestones.
4. Draft slide-level action titles as standalone claims. No topic labels; slide 1 should be an opening_thesis_slide, not a title-only opener.
5. Build claim_backlog, evidence_ledger, source_ledger, appendix_candidates, and open_questions.
6. For each claim, assign supporting evidence, source policy, visual structure, visual richness role, illustration intensity, creative variance, density tier, and density risk.
7. Run a density design gate for each slide: set reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
8. Split any slide that has more than one claim, more than one dominant structure, more than three major regions, or would force body text below 18pt equivalent.
9. Combine adjacent slides only when claims repeat, the same comparison must be seen together, or the user explicitly requests a shorter deck.
10. Define deck_header_master_lock, invisible footer alignment baseline, Insight surface master, and repeated table/card/icon masters before image generation.
11. Read only the action titles in order and repair logical gaps before image generation.
12. Freeze quoted exact_text for every slide; do not leave copywriting to image generation.
13. Draft speaker_notes_text for every slide with speaker_notes_depth_lock: 4-7 substantive Japanese sentences or roughly 180-320 Japanese chars, covering framing, 2-3 evidence/assumption cues, implication, caveat/source context when relevant, and transition cue.
14. For each final slide, produce the canonical planning block and then the image prompt.

Output:
- deck_thesis:
- audience_decision:
- primary_guideline:
- guideline_priority:
- brand_style_notes:
- storyline_frame:
- section_map:
- claim_backlog:
- evidence_ledger:
- source_ledger:
- appendix_candidates:
- open_questions:
- slide_structure:
  - slide_id:
    chapter:
    action_title:
    opening_slide_role:
    first_slide_not_title_only:
    opening_density_gate:
    reader_question_answered:
    claim_type:
    evidence_items:
    evidence_strength:
    source_span_ids:
    source_policy:
    source_real_only_lock:
    source_placeholder_blocklist:
    output_artifact_mastering_lock:
    single_final_png_master_lock:
    no_duplicate_png_output_lock:
    contact_sheet_mastering_lock:
    single_contact_sheet_policy:
    source_line_lock:
    source_separator_lock:
    source_line:
    source_urls:
    assumptions:
    speaker_notes_text:
    speaker_notes_source_cues:
    speaker_notes_transition:
    visual_structure:
    visual_richness_role:
    signature_visual_plan:
    density_tier:
    density_layers:
    density_design:
      reader_mode:
      decision_question:
      information_units:
      density_levers:
      overload_controls:
    information_unit_budget:
    density_guardrails:
    deck_header_master_lock:
    header_line_top_rule:
    deck_tone_master_lock:
    petrol_usage_lock:
    visual_asset_judgment:
    visual_asset_role:
    icon_system_plan:
    layout_archetype:
    layout_family:
    layout_diversity_plan:
    layout_rotation_guard:
    grid_mode:
    exact_text:
      h1:
      subtitle:
      body_labels:
      chart_labels:
      insight_text:
    data_to_render:
    exact_text_budget:
    split_merge_decision:
    prompt_text_budget:
    image_prompt_ready: yes/no
- title_readthrough_check:
- unresolved_items:
```

## Deck Planning Prompt

```text
Create a guideline-aware slide image deck plan.

Purpose:
Audience:
Inputs:
Language:
Embedded ACT design system:
Output type:
Priority:
Design constraints:

Process:
1. Define the deck thesis.
2. Read and apply the embedded ACT design system first; use bundled ACT mechanics only where compatible.
3. Define each slide claim as one sentence, with slide 1 as an opening_thesis_slide that passes opening_density_gate.
4. Select one layout_archetype, layout_family, and grid_mode for each slide.
5. Create layout_diversity_plan and layout_rotation_guard so the sequence can use full-field, asymmetric main/supporting-context, balanced comparison, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families where useful.
6. Define the deck_header_master_lock with exact selected x/y/w/h/color/font values and carry it verbatim into every slide prompt.
7. Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide, with a deck-level mix of human-designed editorial/vector illustrations, data visuals, small system scenes, icon evidence, and quiet tables.
8. Assign density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
9. Assign visual_design_quality_traits as visual treatment only: compact fixed header, thin structural lines, pale cards/tables, restrained icons, explanatory line drawings, stable outer padding, concrete visual anchor, and crisp focal hierarchy.
10. Assign Insight components selectively across the deck only when they add interpretation, decision weight, or reading speed; Honey remains rare and purposeful.
11. Vary dominant structures so the deck feels edited around the argument.
12. Mark restrained illustration candidates where the idea becomes more memorable or fresh without becoming a rough sketch or glossy hero illustration.
13. Flag slides that should split because density would force body below 18pt equivalent or create competing major regions.
14. Define source policy per slide: none / real source list.
15. Define deck-level master refs: header, invisible footer alignment baseline, Insight surface skeleton, table/card masters, icon circle sizes.
16. Draft speaker_notes_text for every slide before generation. Each note should support presentation delivery, not duplicate all visible text: use speaker_notes_depth_lock with a substantial Japanese talk script, key evidence or assumptions to mention, source caveat if needed, implication, and transition to the next slide.
17. Run Guideline/Brand, Header Master, Layout, Typography, Visual Richness, Density, Content, and Deck gates.
```

## Screenshot Or Render Repair Prompt

```text
Inspect this screenshot/rendered slide before revising it.

Inventory:
- visible slide size/aspect ratio
- header anchor: vertical line, H1, subtitle, body gap
- invisible footer alignment baseline, source line, and table note microline
- dominant structure and major regions
- inferred grid_mode, column tracks, row tracks, separator_x, outer padding
- repeated objects and whether width/height/centers are equalized
- coordinate_inventory_1672 for visible major objects
- typography hierarchy and text overflow
- Petrol area and role
- brand accent/Insight use, variant, and whether it is a decision signal
- source hygiene and unsupported claims

Repair:
1. Keep the original claim if valid.
2. Rebuild the canonical planning block.
3. Fix grid drift before color or decorative changes.
4. Trim, split, or regrid crowded text; do not shrink body below 18pt equivalent.
5. Add useful density only through hierarchy, grouping, comparison, annotation, evidence strip, supporting context region, small multiples, or source cue.
6. Add, remove, or quiet Insight only after deciding the interpretation need.
7. Use generation_mode image_edit with model gpt-image-2 when a screenshot/reference image is available.
8. Use explicit preservation language: change only the failing element and keep layout, arrows, labels, spacing, brand colors, invisible footer alignment baseline, and surrounding objects unchanged.
9. Output image_model: gpt-image-2 and a revised final image prompt.
```

## Insight Decision Prompt

```text
Decide whether this slide needs an Insight component.

Evaluate:
- Does the table, diagram, or comparison need a one-sentence interpretation?
- Does the slide contain a strategic turning point, winning logic, or decision?
- Would the component become a second title or second hero?
- Can the component stay as one short judgment sentence, preferably one line and never more than two?
- Is the component text smaller than the selected H1 by at least 6pt and visually below subtitle?
- Is the deck underusing or overusing Insight components?
- Which choice is quietest and clearest under the embedded ACT design system: none, outlined thesis, outlined bottom, brand surface, dark brand surface, or Honey surface when ACT?
- If Honey is chosen, does it help the reader decide faster?
- Does the Honey component use the fixed pale treatment (#F5E2A8 fill, #C49A2C 4-5px left line, #2D332E text)?
- Is the Insight/message-box footprint tied to the interpreted body region and footer rhythm rather than floating in leftover space?
- For bottom variants, does it sit as a centered bridge between body content and Source, with clear breathing room above and below?
- Is the Insight/message-box text optically centered inside the surface both horizontally and vertically?

Output:
- keep/remove
- variant: bottom-main / top-thesis / side-context-wide / side-context-tall / inline-pill / outlined thesis / outlined bottom / brand surface / dark brand surface / Honey surface when ACT
- reason
- deck_count_check
- one-sentence component text if kept
- surface skeleton: geometry, height, radius, padding, left accent, background, text color
- scale lock: compact surface, smallest legible variant, no long-prose enlargement
- text size lock: default 20-24pt, 24-26pt only by exception, at least 6pt smaller than H1 and below subtitle
- alternative visual guidance if removed
```

## Balance Repair Prompt

```text
Repair this slide image prompt for text balance, grid fidelity, and visual hierarchy.

Priority:
1. Do not solve crowding by shrinking body text below 18pt equivalent.
2. Keep ACT header fixed: compact left accent + H1 + subtitle, H1 30-34pt #2D332E, subtitle 21-23pt #4D544E, exact header-block left accent, header_left_accent_reference_lock, header_left_accent_controlled_overhang_rule, header_left_accent_top_protrusion_blocker, header_identity_lock, header_integrity_blocker_lock, and no header ranges in the final prompt.
3. Rebuild grid_mode, column_spans, row_tracks, column_tracks, separator_x, outer_padding, and shared_edges.
4. Add coordinate_inventory_1672 and master_components if missing.
5. Remove repeated explanation and weak labels.
6. Use headings, numbers, rules, spacing, and comparison axes for reading order.
7. Reduce equal-strength regions.
8. Add, change, or remove Insight component based on interpretation need and the embedded ACT design system.
9. Keep every message-box/Insight text smaller than H1; repair oversized boxes before other visual polish.
10. Split the slide if the claim or structure is overloaded.
11. Clean source policy.

Output:
- revised canonical planning block
- image_model: gpt-image-2
- revised final image prompt
- deleted or moved content
- remaining risks
```

## Self-Audit Prompt

```text
Audit each slide as pass/fail.

Guideline/Brand:
- Embedded ACT palette and type hierarchy are followed
- Header/footer text color lock is followed: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E
- Petrol and Honey are absent from header/footer text
- ACT Honey is not decorative when used; it is a quiet pale signal, never a strong yellow block
- Primary accent is structural and not body text; for ACT work, Petrol has a 6-12% area budget
- Color consistency is stable across the deck: no random accent, arbitrary gray, saturation jump, or late-slide color drift
- Deck tone signature is stable: base, typography, rule weight, card/table surfaces, icon stroke, illustration linework, accent budget, density rhythm, Insight treatment, and Source behavior feel like one material system
- Illustration tone is stable: illustration_tone_lock, illustration_style_sheet, and illustration_consistency_status pass across people, devices, documents, CRM/report panels, UI cards, icon badges, fills, stroke, crop, and facial detail

Layout:
- layout_archetype, layout_family, layout_diversity_plan, layout_rotation_guard, grid_mode, component_inventory exist
- coordinate_inventory_1672 and master_components exist
- row_tracks, column_tracks, equalized_groups, shared_edges exist
- header/footer anchors are fixed with exact values, not ranges
- header_identity_lock passes: the header remains the compact left accent + H1 + subtitle system, not a slide-specific decoration surface
- header_left_accent_master_lock passes: the accent is a fixed header-block anchor spanning H1 + subtitle, not a page-edge rail, tall sidebar, body marker, chapter stripe, or ornament
- header_left_accent_reference_lock passes: the accent matches the approved reference geometry x=50 y=40 w=10 h=120 on the 1672x941 basis unless a newer embedded master is supplied
- header_left_accent_shape_lock passes: the accent is one solid 10px vertical rectangle with square or 0-2px radius ends and no pill cap, glow, shadow, gradient, split segment, or duplicate mark
- header_left_accent_controlled_overhang_rule passes: the top uses a controlled 8-16px overhang above the first visible H1 glyph top
- header_left_accent_top_protrusion_blocker passes: no visible accent pixel sits more than 18px above the first visible H1 glyph top, outside header_safe_area, detached from H1/subtitle, or inside body_start_y
- header_integrity_blocker_lock passes: no malformed, missing, oversized, recolored, right-decorated, or intruded header remains
- Whitespace and occupancy balance is intentional: no accidental empty dead zone, no overcrowded canvas, no content crushing the margins
- Secondary regions in split or auxiliary-region layouts read as complete decision panels, not loose leftover areas
- Body silhouette is closed: main and secondary regions share intentional outer edges, lower edges, and footer clearance
- Outer padding is consistent with the deck master and does not drift between slides
- Header integrity is intact: no missing line, warped line, shifted H1/subtitle, or body content inside the header shell
- Visual design quality traits are present: thin rules, pale equalized surfaces, consistent card/table heights, consistent icon stroke/circle sizes, and small explanatory line drawings where useful
- Illustration style sheet is visible where illustration is used: flat 2D workflow scenes, simplified human figures, device/document/UI objects, restrained fills, and consistent Petrol/charcoal linework
- Imageability is present: concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details are named before generation
- Editorial polish repair has improved specificity, proportion, rhythm, and focal hierarchy
- repeated elements are equalized
- supporting region and Insight do not compete
- Insight/message-box compactness passes: the surface does not dominate the slide, behave like a banner, grow tall for prose, or compensate for layout imbalance
- Insight/message-box placement is integrated with the body silhouette and Source baseline rather than used as a patch for an empty corner
- Insight/message-box text is optically centered horizontally and vertically within its surface

Typography:
- max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
- H1 30-34pt, default 32pt
- long Japanese H1 uses 30-32pt; short mixed titles may use 34pt
- subtitle 21-23pt #4D544E
- Insight/message-box text 20-24pt by default, 24-26pt only by exception, and at least 6pt smaller than selected H1 and visually below subtitle
- body readable at 18pt equivalent
- weights stay within 400/600/700
- Typography balance is stable: size and weight hierarchy does not drift slide to slide, and no label/table/Insight text competes with H1

Content:
- one claim
- title is a claim, subtitle supports
- density_design answers a clear decision_question and does not rely on smaller type or decorative detail
- consulting_structure_bias and structured_density_bias are applied selectively: structure and density increase the decision value without turning every slide into a consulting template
- information units are grouped and each added layer improves the claim
- Insight adds interpretation, not repetition
- Insight/message-box placement creates a calm reading bridge between the relevant content and the footer when used at the bottom
- Source is optional and real-source only
- source_line and table_note_microline are separate
- source_real_only_lock passes: Source footer is shown only for real traceable external/provided sources
- source_placeholder_blocklist passes: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions appears as Source text
- output_artifact_mastering_lock passes: `slides_final/` is the only loose-PNG master and package/render-check artifacts reference it
- no_duplicate_png_output_lock passes: no duplicate loose final PNG copies remain across `slides_final/`, `slides_package/`, and `render_check/pdf_pages/`
- contact_sheet_mastering_lock passes: only one retained contact sheet exists by default, unless one explicit delivery comparison sheet or render diff report is needed
- source_separator_lock passes: no horizontal divider, rule, underline, or hairline appears above Source
- no unsupported facts

Model:
- final bitmap generation uses gpt-image-2
- image size is valid for gpt-image-2 and not direct 1920x1080
- background is opaque or auto, not transparent
- prompt uses exact quoted text and no extra text
- output text was audited after generation

Deck:
- layouts vary naturally
- layout_diversity_plan and layout_rotation_guard are reflected in the generated image sequence
- visible priority, rhythm, and breathing room
- post_generation_design_balance_check is approved for generated PNGs before PPTX or Google Slides roll-up
- post_generation_full_deck_review_loop has reviewed every actual generated image before completion
- all_generated_images_reviewed is true, weak_slide_regeneration_queue is empty, and completion_ready_status is approved
- content_quality_status, design_quality_status, and deck_unity_status are approved across the full generated image set
- regenerate_until_quality_approved has been used for every slide with weak content, weak design, tone inconsistency, text/source/header issues, or poor deck unity
- generation_block_rule passes: if generation or repair is blocked, completion_ready_status is blocked and PPTX packaging does not start
- review_manifest_status is approved after validate_review_manifest confirms every generated PNG is covered and all quality gates are approved
- deck_tone_consistency_status is approved after comparing first, middle, and last thirds
- visual design quality traits stay consistent from first to last slide: line weight, pale surfaces, card radius, icon family, illustration density, Petrol role, Honey treatment, and outer padding
- no mechanical card-only repetition
- Insight components are selective and compatible with the embedded ACT design system
- PPTX roll-up contains exactly one full-bleed generated PNG per slide, in order
- Google Slides roll-up contains exactly one full-bleed generated PNG per slide when explicitly requested
- speaker_notes_depth_lock passes: speaker notes exist on every slide, are substantial enough for PPT delivery, and match the slide claim, evidence, caveats, implication, and transition

For every fail:
1. Explain the issue.
2. Choose trim, split, regrid, quiet hierarchy, add Insight, remove Insight, or source cleanup.
3. Provide the revised prompt section.
4. Re-audit.
```
