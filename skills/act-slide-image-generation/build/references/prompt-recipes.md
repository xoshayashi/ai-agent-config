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
image_size: 2048x1152 for generated slide output, review, PPTX packaging, and PDF packaging
image_size_label: 2048x1152 is the single 16:9 2K-width PNG master size; 1672x941 is layout-coordinate basis only
image_quality: low for draft, medium/high for final or text-heavy slides
image_background: opaque or auto
image_output_format: png
image_output_compression: none for PNG slide masters
image_moderation: auto
image_n: 1 for final text-heavy slides; variations only for drafts
image_streaming: optional for exploration, final QA uses completed image
image_delivery_size: 2048x1152; use the same approved slides_final/ PNG masters for PPTX/PDF delivery wrappers
nonconforming_existing_png_regeneration_lock: existing/source PNGs at 1672x941 or any non-approved size are not final blockers and must not be converted, upscaled, HTML-rendered, API-rendered, or locally redrawn; reuse the approved slide specification and generate new 2048x1152 slides_final/ masters with Codex built-in gpt-image-2
generation_route: Codex built-in image generation
builtin_generation_lock: invoke Codex built-in image generation directly and start generating slide PNGs; do not pause for local environment preflight or local artifact-route probing before generation
codex_image_artifact_rule: the image returned by Codex built-in image generation is the authoritative generated PNG artifact; use the Codex-provided artifact/download/attachment path to materialize approved outputs under slides_final/ when a filesystem path is needed for PPTX packaging
image_generation_tool_lock: final slide PNG pixels must be produced by Codex built-in image generation, not by repo scripts, local renderers, screenshots, or presentation exports
script_boundary_lock: prompt builder scripts are planning helpers only; package scripts run only after approved Codex image artifacts exist and must never render, draw, screenshot, export, simulate, or replace final slide PNGs
local_env_non_blocker: local environment uncertainty is not a blocker and must not be reported as the reason PPTX is unfinished
credential_setup_blocker: do not create, request, decrypt, configure, inspect, or wait for account credentials, local tokens, SDK setup, or environment variables; use Codex built-in image generation directly
progress_update_route_lock: in user-facing progress updates, do not mention local credential, environment, SDK, save-route, or alternate account/setup checks as prerequisites; say that slide structuring and built-in image generation are starting
generation_status: generated_with_builtin_gpt-image-2 / blocked
package_delivery: requested PPTX/PDF wrappers after generated PNGs pass QA, unless user asks for PNG files only
pptx_status: pending_generated_images_and_pre_package_image_review / created / blocked
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
speaker_notes_persuasion_lock:
speaker_notes_text:
speaker_notes_landing:
speaker_notes_signpost:
notes_hook:
notes_objection_preempt:
notes_delivery_markers:
notes_persuasion_arc:
opening_slide_role:
first_slide_not_title_only:
opening_density_gate:
ask_present:
top_risk_named:
governing_thought:
pyramid_logic_lock:
predecessor_question:
title_exhibit_proof_match:
mece_support_gate:
body_logic:
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
chart_emphasis_lock:
encoding_consistency_lock:
number_format_normalization_lock:
benchmark_reference_line:
imageability_lock:
concrete_visual_anchor:
observable_scene_or_object:
viewpoint_crop:
specific_visual_details:
visual_specificity_plan:
editorial_polish_repair_loop:
visual_subject_open_set:
message_led_composition_lock:
region_balance_policy:
composition_fit_plan:
design_balance_gate:
occupancy_density_fit_lock:
font_scale_unity_lock:
palette_role_unity_lock:
multimodal_design_review_lock:
design_breakage_blocker_lock:
secondary_region_integrity_lock:
body_silhouette_lock:
post_generation_design_balance_check:
post_generation_design_balance_status:
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
review_manifest_design_status_gate:
validate_review_manifest:
whitespace_occupancy_balance_status:
density_balance_status:
typography_balance_status:
color_consistency_status:
outer_padding_consistency_status:
header_integrity_status:
multimodal_design_review_status:
design_balance_gate_status:
occupancy_density_fit_status:
font_scale_unity_status:
palette_role_unity_status:
design_breakage_blocker_status:
deck_header_master_lock:
  coordinate_basis:
  status: exact_required_before_generation
  header_safe_area:
  vertical_line:
  header_line_top_rule:
  header_left_accent_master_lock:
  header_left_accent_reference_lock:
  header_left_accent_shape_lock:
  header_left_accent_no_protrusion_rule:
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
visible_brand_label_blocker: no separate ACT wordmark, logo, title kicker, badge, or brand label in the header unless exact_text explicitly requests it
message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement
insight_absence_default_lock: start from no Insight/message-box on each slide; add one only when it passes insight_justification_required
insight_justification_required: keep an Insight/message-box only with a clear non-redundant interpretation, decision signal, or reading bridge
honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
honey_justification_required: keep Honey only with a written reason tied to decision clarity; remove decorative or space-filling Honey
message_box_scale_lock: compact interpretation surface sized after the main content area; lower height is welcome when it gives the body, figure, table, or diagram more useful room; bottom bars target 72-96px on the 1672 basis
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
  information_units: [message, context, comparison, trend, mechanism, risk, implication, assumption, source]
  semantic_sentence_layer: [1-3 compact meaningful clauses/sentences in body labels, rows, annotations, or optional Insight that explain relationship, reason, consequence, or decision relevance]
  semantic_copy_gate: [major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names]
  icon_restraint_plan: [necessary icons, why they clarify, and which icon candidates were removed because text/structure communicates better]
  icon_density_budget: [default 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise]
  density_levers: [KPI strip, supporting context region, evidence strip, small multiples, annotations, benchmark/context column, benchmark/target/prior-period reference line, source cue]
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
  height: calculated after body and footer rhythm; use the lowest comfortable height when it helps the main content area
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
- prompt/package scripts are helpers only: use them to scaffold prompts, validate manifests, or package already-approved Codex image artifacts; never use scripts to render, draw, screenshot, export, simulate, or replace final slide PNGs
- use generation_mode new_image for new single-slide images or image_edit for screenshot/reference repair
- use image_size 2048x1152 for generated slide output, review, PPTX packaging, and PDF packaging; do not create separate 1920x1080, 1672x941, draft-size, QHD, or 4K delivery PNG masters
- if existing/source PNGs are 1672x941 or another non-approved package size, do not stop at the package-script rejection and do not convert, upscale, HTML-render, API-render, or locally redraw them; reuse the approved slide specification and generate new 2048x1152 slides_final/ masters with Codex built-in gpt-image-2, then review and package those generated masters
- treat strict DCI 2K 2048x1080 and DCI 4K 4096x2160 as non-target cinema sizes, not ACT 16:9 slide generation sizes
- use image_background opaque or auto, never transparent
- use png for slide fidelity unless latency or file size matters
- use moderation auto by default
- use n=1 for final text-heavy slides; use multiple variations only for draft exploration
- 1 slide = 1 primary message
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
- apply deck_tone_signature_lock before slide-level variation; vary layouts from messages while keeping material language consistent
- apply illustration_tone_lock and illustration_style_sheet before image prompting; keep people, devices, document objects, UI panels, icon badges, linework, fills, and crop consistent across the deck
- lock footer_anchor_baseline even when source_line is none
- lock header_footer_text_color_lock: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E
- keep source_line separate from table_note_microline
- source_real_only_lock: render Source only for real traceable external/provided sources; otherwise source_line none and no Source footer
- source_placeholder_blocklist: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source
- source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
- source_separator_lock: Source is text-only; no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline may appear above, below, behind, or adjacent to Source
- output_artifact_mastering_lock: slides_final/ is the only loose-PNG master; package and render-check folders hold only derivative artifacts
- no_duplicate_png_output_lock: no duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/
- contact_sheet_mastering_lock: one retained contact_sheet_review.png by default; comparison sheet only when delivery QA requires it
- Do not drop real source names to reduce visual density; shorten or group source names instead.
- draft speaker_notes_text for every deck slide before image generation; apply speaker_notes_depth_lock so PPT notes are substantial Japanese talk scripts, not terse bullets; keep notes off the slide image and out of the exact on-slide text
- speaker_notes_persuasion_lock: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and may add a justified hook, objection pre-empt, or delivery markers; keep this persuasion layer off the slide image
- assign visual_richness_role, illustration_intensity, creative_variance, and density_tier before generation
- define density_design before generation: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails
- density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
- sentence_density_lift_lock: raise density one step with compact meaningful clauses or short sentences in body labels, rows, annotations, and optional Insight; avoid icon-and-keyword-only slides
- semantic_copy_gate: major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names
- icon_restraint_lock: icons are sparse wayfinding or evidence markers, not the primary content layer; remove generic icon rows, icon wallpaper, and icons that replace clearer text or structure
- icon_density_budget: default to 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise
- structure_choice_bias: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide
- structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits; add layers only until the body silhouette is filled with deliberate content, then split rather than overcrowd
- use issue trees, driver trees, 2x2 matrices, value chains, funnels, waterfalls, KPI bridges, decision tables, before/after bridges, or hypothesis-evidence-implication rows when they improve the reader's decision path; skip them when they would clutter the focal message
- structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
- add density through decision-relevant comparisons, benchmarks, units, denominators, assumptions, annotations, evidence strips, supporting context regions, small multiples, and source cues; never through smaller type or decorative illustration detail
- chart_emphasis_lock: gray out non-focal data, place the decision-carrying number as a direct on-mark label, and label series directly instead of using a legend; render non-focal series/bars/rows/nodes in one quiet neutral gray so the accent color marks only the element the action title is about, and use a separate legend only when 5+ series force it
- encoding_consistency_lock: same meaning keeps the same fill/color/shape and scale across the deck, and no distinction relies on hue alone; reuse one deck-level encoding legend for scenario (actual/plan/forecast), variance sign, and category, keep one non-truncated scale per repeated unit, and pair every color difference with a label, shape, fill pattern, or position cue; the chart_emphasis_lock focal layer (accent vs neutral gray) overrides category hue on a slide where the category is non-focal and is not an encoding inconsistency
- number_format_normalization_lock: normalize decimal precision, magnitude abbreviation, axis ticks, and period notation before freezing exact_text so the same metric formats identically across the deck
- when a chart shows a level or trend, add one thin labeled reference line (target, prior period, or peer benchmark) so the value reads as above or below a meaningful bar
- imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
- editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
- visual_subject_open_set, message_led_composition_lock, and composition_fit_plan: choose the visual subject, focal relationship, and canvas occupancy from the argument before image prompting; occupancy is observable - no quadrant of the body content area is conspicuously empty and no major region overflows its grid track
- design_balance_gate: freeze planned body occupancy, useful whitespace role, content-area weight, text-role sizes, background role, and accent role before generation; approve only when the actual PNG matches those choices
- occupancy_density_fit_lock: body occupancy must fit the selected density_tier without dead zones, margin crush, overcrowding, or density created by shrinking body text below 18pt equivalent
- font_scale_unity_lock: reuse one deck-level type scale for H1, subtitle, body, data labels, table labels, Source, and optional Insight; repair size/weight/color drift before packaging
- palette_role_unity_lock: keep ACT colors in stable roles across canvas, panels/cards, text, footnotes, Petrol accent, and rare Honey signal; repair arbitrary background, text, accent, or saturation drift
- region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette
- secondary_region_integrity_lock: in split or auxiliary-region layouts, design the secondary region as a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
- body_silhouette_lock: make the body read as one closed visual block with aligned outer edges, lower edges, and footer clearance
- make abstract messages imageable through a specific operating view, workflow handoff, document stack, data row, map route, queue, machine cell, screen state, evidence artifact, or customer moment that fits the message
- keep decision-relevant numbers when they are legible and grouped; do not force a minimal-numbers rule
- use human-designed editorial/vector illustrations for chapter openers, turning points, complex systems, and final vision slides
- keep illustration subordinate: a clear focal motif, only useful supporting details, clean controlled flat 2D linework, crisp silhouettes, restrained fills, rounded UI panels, small icon badges, a projection/viewpoint chosen from the message, no rough sketch, no arbitrary pseudo-depth, and no glossy AI concept-art finish
- max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
- use ACT typography: H1 30-34pt, subtitle 21-23pt, body 18pt equivalent
- use ACT header rules: H1 Forest Charcoal #2D332E, subtitle #4D544E, exact compact left vertical line, no blue H1, no right-side header decoration
- use the default exact compact ACT header unless the user explicitly provides a newer embedded master: 1672x941 basis; header_safe_area x=44 y=24 w=1584 h=136; vertical_line x=50 y=40 w=10 h=120 #008A80; H1 x=88 y=34 w=1332 max_lines=1 size=32pt weight=700 line_height=1.14 #2D332E; subtitle x=88 y=82 w=1332 max_lines=1 size=22pt weight=400 line_height=1.18 #4D544E; visual_alignment accent top aligns with the first visible H1 glyph/title top or sits 0-6px below it, never above it, and accent bottom sits 4-10px below subtitle lower visual edge; body_start_y=180; upper_right_clear_zone x=1420 y=24 w=208 h=88 empty
- make the slide feel human-crafted through priority, breathing room, and editorial rhythm
- keep the slide in a strategy operating-deck look: useful occupancy, small explanatory visuals, crisp rules, low-contrast surfaces, and no ornamental depth
- let structure, spacing, rules, numbers, and typography carry hierarchy
- use the embedded ACT design system's accent color structurally with a restrained area budget; for ACT work, Petrol uses a 6-12% area budget and never appears as body text
- start from `insight_decision: none`; use Insight component only if it adds non-redundant interpretation, decision weight, or a reading bridge and is compatible with the embedded ACT design system; many slides should use no message box
- apply insight_justification_required: if the same sentence is already clear from H1, subtitle, chart/table labels, or notes, remove the Insight/message-box
- apply honey_selective_signal_lock: Honey starts absent; use it only when a justified bottom decision signal is stronger than no component or a neutral outlined treatment
- if Honey is used in ACT or compatible guidelines, use it only as a justified bottom Insight bar with #FBF3D7 very pale fill, #C49A2C thin 2-3px outline/separator, optional left icon well with a small 20-24px icon on the 1672 basis, #2D332E text, one component maximum
- keep all Insight/message boxes flat solid fill only; no patterns, textures, gradients, motifs, icon wallpaper, dashed outlines, or internal illustrations
- apply content_area_priority_lock before sizing an Insight/message-box: give the body, figure, table, or diagram the needed height first, then use the remaining calculated space for the optional box
- apply message_box_scale_lock: keep Insight/message boxes compact, one short judgment sentence, one line preferred and two lines maximum; bottom bars target 72-96px on the 1672 basis; move detail to notes instead of growing the surface
- keep Insight/message-box text 20-24pt by default, 24-26pt only by exception, at least 6pt smaller than H1, visually below subtitle; it must not become a second title or second hero headline
- keep Insight/message-box surfaces compact, occasional, and content-area-aware; if the surface starts to dominate, behave like a banner, grow tall, or rescue weak layout, shorten text, narrow it, move detail to body/notes, or remove it
- keep Honey quiet: no saturated yellow fill, no dark yellow message box, no large yellow area, no dashed Honey card, no Honey placeholder region, no Honey title underline, and no Honey color variation across a deck
- Source: render only real traceable source names; when no real source exists, use source_line: none and do not show a Source footer. Never use brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, working assumptions, or other placeholder provenance as Source text.
- Output files: keep `slides_final/` as the only loose-PNG master. Do not duplicate approved generated PNGs into `slides_package/` or `render_check/pdf_pages/`; package and render-check artifacts must reference the `slides_final/` master. PDF creation also references `slides_final/` masters directly.
- Keep only one retained contact sheet by default: `render_check/contact_sheet_review.png`. Use one comparison contact sheet or a render diff JSON only when delivery/render QA needs it.
- final bitmap generation must use gpt-image-2
- if actual Codex built-in image generation is blocked by the image tool after invocation, stop and report that tool-level blocker; missing local environment uncertainty is not a blocker and must not be used to leave the PPTX unfinished
- after all generated PNGs pass QA, create the requested PPTX/PDF package unless the user asks for PNG files only: one full-bleed generated PNG per slide, same order, no extra overlays, and speaker notes inserted when supported
- place every literal string under `Exact text` in quotes and request ONLY those strings
- use "Draw" or "Create" for generation prompts, and "Edit" plus preservation language for repair prompts
- for healthcare, finance, law, or regulated domains, do not add market, clinical, regulatory, or compliance facts unless sources are provided or researched

Output:
1. canonical planning block
2. image_model: gpt-image-2
3. final image prompt
4. negative prompt
5. generation route and output files, or blocker
6. PPTX/PDF roll-up status with speaker notes status for decks
7. requested PPTX/PDF packaging status
8. post-generation audit checklist
```

## Text To Slide Structure Prompt

```text
Convert the following long text into a guideline-aware slide-image deck structure before writing any image prompt.

Process:
1. Extract the deck thesis and audience decision.
2. Create intake_map with source_span_id values for chapters, facts, quotes, assumptions, and uncertainties.
3. Choose one storyline frame: SCQA, problem-solution-evidence, past-present-future, context-problem-solution-differentiation, or thesis-risk-milestones. State the deck's single governing_thought and run governing_thought_gate so every action title answers a question that thought raises; record notes_persuasion_arc.
4. Draft slide-level action titles as standalone messages. No topic labels; slide 1 should be an opening_thesis_slide, not a title-only opener. For decision/recommendation decks confirm ask_present and top_risk_named on the opener or slide 2.
5. Apply message_sharpness_lock: each action title names actor/topic, change/tension, and implication; repair vague labels, slogans, or generic benefit claims. Apply pyramid_logic_lock: build a vertical_logic_chain so each title answers the question its predecessor raises.
6. Build message_backlog, evidence_ledger, source_ledger, appendix_candidates, and open_questions. Apply mece_support_gate: run mece_check on multi-point slides and declare body_logic as inductive or deductive.
7. For each message, assign supporting evidence, source policy, visual structure, visual richness role, illustration intensity, creative variance, density tier, and density risk. Run title_exhibit_proof_match: name the exhibit element that proves the action title. Apply chart_emphasis_lock, encoding_consistency_lock, and number_format_normalization_lock on chart/table slides.
8. Run impact_clarity_density_gate: each slide has one unmistakable takeaway, one dominant visual structure, a useful evidence layer, and a simple reading path; repair slides that feel flat, vague, thin, or cluttered.
9. Run a density design gate for each slide: set reader_mode, decision_question, information_units, semantic_sentence_layer, semantic_copy_gate, icon_restraint_plan, icon_density_budget, density_levers, overload_controls, information_unit_budget, and density_guardrails.
10. Apply sentence_density_lift_lock, semantic_copy_gate, icon_restraint_lock, and icon_density_budget before image prompting: if the slide reads as icons plus noun labels, add compact explanatory clauses/sentences and reduce icons until the argument is understandable without narration.
11. Apply evidence_compression_ladder: choose the smallest proof structure that makes the message credible: key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation.
12. Split any slide that has more than one message, more than one dominant structure, more than three major regions, or would force body text below 18pt equivalent.
13. Combine adjacent slides only when messages repeat, the same comparison must be seen together, or the user explicitly requests a shorter deck.
14. Define deck_header_master_lock, invisible footer alignment baseline, Insight surface master, and repeated table/card/icon masters before image generation.
15. Read only the action titles in order and repair logical gaps before image generation.
16. Freeze quoted exact_text for every slide; do not leave copywriting to image generation.
17. Draft speaker_notes_text for every slide with speaker_notes_depth_lock: 4-7 substantive Japanese sentences or roughly 180-320 Japanese chars, covering framing, 2-3 evidence/assumption cues, implication, caveat/source context when relevant, and transition cue. Apply speaker_notes_persuasion_lock: stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and a signpost transition, and add a justified notes_hook, notes_objection_preempt, or delivery markers only where they help.
18. For each final slide, produce the canonical planning block and then the image prompt.

Output:
- deck_thesis:
- governing_thought:
- governing_thought_gate:
- notes_persuasion_arc:
- vertical_logic_chain:
- audience_decision:
- primary_guideline:
- guideline_priority:
- brand_style_notes:
- storyline_frame:
- section_map:
- message_backlog:
- evidence_ledger:
- source_ledger:
- appendix_candidates:
- open_questions:
- slide_structure:
  - slide_id:
    chapter:
    action_title:
    message_sharpness_lock:
    pyramid_logic_lock:
    predecessor_question:
    title_exhibit_proof_match:
    mece_support_gate:
    mece_check:
    body_logic:
    opening_slide_role:
    first_slide_not_title_only:
    opening_density_gate:
    ask_present:
    top_risk_named:
    reader_question_answered:
    message_type:
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
    speaker_notes_depth_lock:
    speaker_notes_persuasion_lock:
    speaker_notes_text:
    speaker_notes_source_cues:
    speaker_notes_transition:
    speaker_notes_landing:
    speaker_notes_signpost:
    notes_hook:
    notes_objection_preempt:
    notes_delivery_markers:
    visual_structure:
    visual_richness_role:
    signature_visual_plan:
    density_tier:
    impact_clarity_density_gate:
    density_layers:
    density_design:
      reader_mode:
      decision_question:
      information_units:
      semantic_sentence_layer:
      semantic_copy_gate:
      icon_restraint_plan:
      icon_density_budget:
      density_levers:
      overload_controls:
    evidence_compression_ladder:
    chart_emphasis_lock:
    encoding_consistency_lock:
    number_format_normalization_lock:
    benchmark_reference_line:
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
1. Define the deck thesis and the single governing_thought; run governing_thought_gate and record notes_persuasion_arc.
2. Read and apply the embedded ACT design system first; use bundled ACT mechanics only where compatible.
3. Define each slide message as one sentence, with slide 1 as an opening_thesis_slide that passes opening_density_gate. Apply pyramid_logic_lock so each title answers the question its predecessor raises; for decision decks confirm ask_present and top_risk_named. Apply mece_support_gate on multi-point slides and declare body_logic as inductive or deductive.
4. Select one layout_archetype, layout_family, and grid_mode for each slide.
5. Create layout_diversity_plan and layout_rotation_guard so the sequence can use full-field, asymmetric main/supporting-context, balanced comparison, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families where useful.
6. Define the deck_header_master_lock with exact selected x/y/w/h/color/font values and carry it verbatim into every slide prompt.
7. Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide, with a deck-level mix of human-designed editorial/vector illustrations, data visuals, small system scenes, icon evidence, and quiet tables.
8. Assign density_design for every slide: reader_mode, decision_question, information_units, semantic_sentence_layer, semantic_copy_gate, icon_restraint_plan, icon_density_budget, density_levers, overload_controls, information_unit_budget, and density_guardrails.
9. Ensure sentence_density_lift_lock, semantic_copy_gate, icon_restraint_lock, and icon_density_budget are satisfied before the final prompt: body content should read as meaningful clauses/sentences, while icons remain sparse support.
10. Assign visual_design_quality_traits as visual treatment only: compact fixed header, thin structural lines, pale cards/tables, restrained icons, explanatory line drawings, stable outer padding, concrete visual anchor, and crisp focal hierarchy.
11. Assign Insight components selectively across the deck only when they add non-redundant interpretation, decision weight, or reading speed. Start each slide from `insight_decision: none`, and keep a component only when `insight_justification_required` is satisfied. Apply `honey_selective_signal_lock`: Honey remains rare, purposeful, and bottom-bar-only.
12. Vary dominant structures so the deck feels edited around the argument. On chart/table slides apply chart_emphasis_lock, encoding_consistency_lock, and number_format_normalization_lock, and run title_exhibit_proof_match.
13. Mark restrained illustration candidates where the idea becomes more memorable or fresh without becoming a rough sketch or glossy hero illustration.
14. Flag slides that should split because density would force body below 18pt equivalent or create competing major regions.
15. Define source policy per slide: none / real source list.
16. Define deck-level master refs: header, invisible footer alignment baseline, Insight surface skeleton, table/card masters, icon circle sizes.
17. Draft speaker_notes_text for every slide before generation. Each note should support presentation delivery, not duplicate all visible text: use speaker_notes_depth_lock with a substantial Japanese talk script, key evidence or assumptions to mention, source caveat if needed, implication, and transition to the next slide. Apply speaker_notes_persuasion_lock: stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and add a justified notes_hook, notes_objection_preempt, or delivery markers only where they help.
18. Run Guideline/Brand, Header Master, Layout, Typography, Visual Richness, Density, Content, and Deck gates.
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
- source hygiene and unsupported messages

Repair:
1. Keep the original message if valid.
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
- Start from none. What would be lost if the slide had no Insight/message-box?
- Is the proposed sentence non-redundant with the H1, subtitle, labels, or visual structure?
- Does the table, diagram, or comparison need a one-sentence interpretation?
- Does the slide contain a strategic turning point, winning logic, or decision?
- Would the component become a second title or second hero?
- Can the component stay as one short judgment sentence, preferably one line and never more than two?
- Is the component text smaller than the selected H1 by at least 6pt and visually below subtitle?
- Is the deck underusing or overusing Insight components?
- Would keeping no component make the slide simpler, stronger, and give the body more room?
- Which choice is quietest and clearest under the embedded ACT design system: none, outlined thesis, outlined bottom, accent surface, dark accent surface, or Honey bottom bar when ACT?
- If Honey is chosen, does it help the reader decide faster?
- If Honey is chosen, is there a written honey_justification_required reason tied to decision clarity rather than decoration?
- Does the Honey component use the fixed bottom-bar treatment (#FBF3D7 very pale fill, #C49A2C 2-3px outline/separator, optional left icon well with a small 20-24px icon, #2D332E text)?
- Is the Insight/message-box footprint tied to the interpreted body region and footer rhythm rather than floating in leftover space?
- For bottom variants, does it sit as a centered bridge between body content and Source, with clear breathing room above and below?
- Is the Insight/message-box text optically centered inside the surface both horizontally and vertically?

Output:
- keep/remove
- variant: bottom-main / top-thesis / side-context-wide / side-context-tall / inline-pill / outlined thesis / outlined bottom / accent surface / dark accent surface / Honey bottom bar when ACT
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
2. Keep ACT header fixed: compact left accent + H1 + subtitle, H1 30-34pt #2D332E, subtitle 21-23pt #4D544E, exact header-block left accent, header_left_accent_reference_lock, header_left_accent_no_protrusion_rule, header_left_accent_top_protrusion_blocker, header_identity_lock, header_integrity_blocker_lock, and no header ranges in the final prompt.
3. Rebuild grid_mode, column_spans, row_tracks, column_tracks, separator_x, outer_padding, and shared_edges.
4. Add coordinate_inventory_1672 and master_components if missing.
5. Apply design_balance_gate: set body occupancy, useful whitespace, content-area weight, text-role sizes, background role, and accent role explicitly.
6. Apply occupancy_density_fit_lock: repair accidental empty zones, weak body occupancy, crushed margins, overcrowding, or density created by smaller text.
7. Apply font_scale_unity_lock and palette_role_unity_lock: restore the deck type scale and ACT color roles before any decorative polish.
8. Remove repeated explanation and weak labels.
9. Use headings, numbers, rules, spacing, and comparison axes for reading order.
10. Reduce equal-strength regions.
11. Add, change, or remove Insight component based on interpretation need and the embedded ACT design system.
12. Keep every message-box/Insight text smaller than H1; repair oversized boxes before other visual polish.
13. Split the slide if the message or structure is overloaded.
14. Clean source policy.

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
- visible_brand_label_blocker passes: no separate ACT wordmark, logo, title kicker, or brand label appears in the header unless exact_text explicitly requested it
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
- header_left_accent_no_protrusion_rule passes: the top aligns with the first visible H1 glyph/title top or sits 0-6px below it
- header_left_accent_top_protrusion_blocker passes: no visible accent pixel sits above the first visible H1 glyph/title top, outside header_safe_area, detached from H1/subtitle, or inside body_start_y
- header_integrity_blocker_lock passes: no malformed, missing, oversized, recolored, right-decorated, or intruded header remains
- Whitespace and occupancy balance is intentional: no accidental empty dead zone, no overcrowded canvas, no content crushing the margins
- design_balance_gate passes: intended body occupancy, whitespace role, content-area weight, type-role sizes, background role, and accent role were frozen before generation and match the actual PNG
- occupancy_density_fit_lock passes: body occupancy matches the selected density_tier without dead zones, margin crush, overcrowding, or smaller-than-18pt body text
- font_scale_unity_lock passes: one deck-level type scale holds across H1, subtitle, body, data labels, table labels, Source, and optional Insight
- palette_role_unity_lock passes: ACT colors keep stable roles across canvas, panels/cards, text, footnotes, Petrol accent, and rare Honey signal
- multimodal_design_review_lock passes: actual PNGs were inspected multimodally for layout collapse, occupancy/density imbalance, font-size/color drift, background/accent mismatch, and deck-unity drift
- design_breakage_blocker_lock passes: no layout collapse, accidental empty zone, overcrowding, inconsistent font scale, wrong text color, wrong background color, excessive/random accent use, or off-system illustration tone remains
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
- Insight/message-box compactness passes: the surface stays compact and content-area-aware, does not dominate the slide, behave like a banner, grow tall for prose, or compensate for layout imbalance
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
- one message
- title is a message, subtitle supports
- pyramid_logic_lock passes: a single governing thought is stated, each action title answers the question its predecessor raises, and the title read-through is one connected argument
- title_exhibit_proof_match passes: a named exhibit element proves the action title and the title claims nothing the exhibit cannot show
- mece_support_gate passes: supporting points are mutually exclusive and collectively exhaustive, and body_logic is declared inductive or deductive
- chart_emphasis_lock passes: non-focal data is grayed out, the decision-carrying number is a direct on-mark label, and series are labeled directly unless 5+ series force a legend
- encoding_consistency_lock passes: scenario/variance/category encodings and repeated-unit scales are constant across the deck, and no distinction relies on hue alone
- number_format_normalization_lock passes: decimal precision, magnitude abbreviation, axis ticks, and period notation are normalized for each metric
- density_design answers a clear decision_question and does not rely on smaller type or decorative detail
- structure_choice_bias and structured_density_bias are applied selectively: structure and density increase the decision value without turning every slide into a rigid template
- sentence_density_lift_lock is applied: the slide uses compact meaningful clauses/sentences where the reader needs relationships, reasons, consequences, or decision relevance, and is not an icon-and-keyword-only composition
- semantic_copy_gate is applied: major body labels are not noun-only unless they are headers, axes, legends, or categories
- icon_restraint_lock is applied: icons are purposeful, sparse support and do not dominate or substitute for the semantic sentence layer
- icon_density_budget is applied: icons normally stay within 0-3 purposeful uses and below semantic text units
- information units are grouped and each added layer improves the message
- Insight adds interpretation, not repetition
- Insight/message-box placement creates a calm reading bridge between the relevant content and the footer when used at the bottom
- Source is optional and real-source only
- source_line and table_note_microline are separate
- source_real_only_lock passes: Source footer is shown only for real traceable external/provided sources
- source_placeholder_blocklist passes: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions appears as Source text
- nonconforming_existing_png_regeneration_lock passes: any existing/source PNG at 1672x941 or another non-approved package size was not treated as a final blocker or converted locally; a new 2048x1152 Codex built-in gpt-image-2 master was generated from the approved specification before packaging
- output_artifact_mastering_lock passes: `slides_final/` is the only loose-PNG master and package/render-check artifacts reference it
- review_manifest_design_status_gate passes: deck-level and slide-level manifest entries approve post_generation_design_balance_status, whitespace_occupancy_balance_status, density_balance_status, typography_balance_status, color_consistency_status, outer_padding_consistency_status, header_integrity_status, multimodal_design_review_status, design_balance_gate_status, occupancy_density_fit_status, font_scale_unity_status, palette_role_unity_status, and design_breakage_blocker_status
- pdf_export_source_lock passes: PDF outputs are created from `slides_final/` master PNGs; `render_check/pdf_pages/` is rendered-back QA only
- no_duplicate_png_output_lock passes: no duplicate loose final PNG copies remain across `slides_final/`, `slides_package/`, and `render_check/pdf_pages/`
- contact_sheet_mastering_lock passes: only one retained contact sheet exists by default, unless one explicit delivery comparison sheet or render diff report is needed
- source_separator_lock passes: Source is text-only, with no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline above, below, behind, or adjacent to Source
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
- post_generation_design_balance_check is approved for generated PNGs before PPTX/PDF packaging, including density balance against the planned density tier
- post_generation_full_deck_review_loop has reviewed every actual generated image before completion
- all_generated_images_reviewed is true, weak_slide_regeneration_queue is empty, and completion_ready_status is approved
- content_quality_status, design_quality_status, and deck_unity_status are approved across the full generated image set
- regenerate_until_quality_approved has been used for every slide with weak content, weak design, tone inconsistency, text/source/header issues, or poor deck unity
- generation_block_rule passes: if generation or repair is blocked, completion_ready_status is blocked and PPTX packaging does not start
- review_manifest_status is approved after validate_review_manifest confirms every generated PNG is covered exactly once, rejects duplicate image input and duplicate png_path entries, and all quality gates are approved
- deck_tone_consistency_status is approved after comparing first, middle, and last thirds
- visual design quality traits stay consistent from first to last slide: line weight, pale surfaces, card radius, icon family, illustration density, Petrol role, Honey treatment, and outer padding
- no mechanical card-only repetition
- Insight components are selective and compatible with the embedded ACT design system
- PPTX/PDF roll-up contains exactly one full-bleed generated PNG per slide, in order
- speaker_notes_depth_lock passes: speaker notes exist on every slide, are substantial enough for PPT delivery, and match the slide message, evidence, caveats, implication, and transition
- speaker_notes_persuasion_lock passes: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, stay consistent with notes_persuasion_arc, and add hook/objection-preempt/delivery markers only where justified

For every fail:
1. Explain the issue.
2. Choose trim, split, regrid, quiet hierarchy, add Insight, remove Insight, or source cleanup.
3. Provide the revised prompt section.
4. Re-audit.
```
