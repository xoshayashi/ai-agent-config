#!/usr/bin/env python3
"""Build a guideline-aware slide image prompt scaffold from a rough brief."""

from __future__ import annotations

import argparse
from pathlib import Path


UNRESOLVED_ARCHETYPE = "UNRESOLVED - choose one guideline-compatible layout_archetype before final prompt"
UNRESOLVED_GRID_MODE = "UNRESOLVED - choose one grid_mode before final prompt"
IMAGE_MODEL = "gpt-image-2"
ALLOWED_16_9_SIZES = {"1536x864", "2048x1152", "2560x1440", "3840x2160"}
SIZE_LABELS = {
    "1536x864": "fast draft 16:9 image-generation size",
    "2048x1152": "practical 16:9 2K-width image-generation size for working review",
    "2560x1440": "QHD/1440p 16:9 image-generation size for high-fidelity final",
    "3840x2160": "4K UHD 16:9 image-generation size; explicit request only",
}
PLACEHOLDER_BLOCKERS = [
    "slide_claim",
    "column_spans",
    "row_tracks",
    "column_tracks",
    "separator_x",
    "outer_padding",
    "major_regions",
    "coordinate_inventory_1672",
    "master_components",
    "deck_master_refs",
    "deck_header_master_lock",
    "visual_design_quality_traits",
    "concrete_visual_anchor",
    "visual_specificity_plan",
    "observable_scene_or_object",
    "viewpoint_crop",
    "specific_visual_details",
    "imageability_lock",
    "editorial_polish_repair_loop",
    "visual_subject_open_set",
    "claim_led_composition_lock",
    "region_balance_policy",
    "composition_fit_plan",
    "secondary_region_integrity_lock",
    "body_silhouette_lock",
    "layout_family",
    "layout_diversity_plan",
    "layout_rotation_guard",
    "layout_sequence_table",
    "recent_layout_memory",
    "component_inventory",
    "equalized_groups",
    "shared_edges",
    "hand_placed_exceptions",
    "visual_richness_role",
    "signature_visual_plan",
    "illustration_region",
    "illustration_intensity",
    "human_designed_illustration_style",
    "creative_variance",
    "density_tier",
    "density_layers",
    "density_design",
    "reader_mode",
    "decision_question",
    "information_units",
    "information_unit_budget",
    "density_levers",
    "density_guardrails",
    "overload_controls",
    "header_anchor",
    "footer_anchor_baseline",
    "header_footer_text_color_lock",
    "message_box_scale_lock",
    "message_box_text_size_lock",
    "post_generation_design_balance_check",
    "source_policy",
    "speaker_notes_text",
    "pptx_rollup_plan",
    "pptx_package_status",
    "image_review_matrix",
    "deck_consistency_matrix",
    "brand_accent_usage_budget",
    "brand_accent_system_role",
    "insight_decision",
    "human_crafted_feel",
]


def read_brief(path: str | None) -> str:
    if not path:
        return "[paste or summarize the user brief here]"
    return Path(path).read_text(encoding="utf-8").strip()


def validate_size(size: str) -> str:
    try:
        width_raw, height_raw = size.lower().split("x", 1)
        width = int(width_raw)
        height = int(height_raw)
    except ValueError as exc:
        raise SystemExit(f"Invalid --size '{size}'. Use WIDTHxHEIGHT, e.g. 2560x1440.") from exc

    if width % 16 or height % 16:
        raise SystemExit(f"Invalid --size '{size}'. gpt-image-2 requires both edges to be multiples of 16.")
    if max(width, height) > 3840:
        raise SystemExit(f"Invalid --size '{size}'. Maximum edge must be <= 3840px.")
    if max(width, height) / min(width, height) > 3:
        raise SystemExit(f"Invalid --size '{size}'. Long:short ratio must be <= 3:1.")
    pixels = width * height
    if pixels < 655_360 or pixels > 8_294_400:
        raise SystemExit(f"Invalid --size '{size}'. Total pixels must be 655,360 to 8,294,400.")
    normalized = f"{width}x{height}"
    if normalized not in ALLOWED_16_9_SIZES:
        allowed = ", ".join(sorted(ALLOWED_16_9_SIZES))
        raise SystemExit(f"Invalid --size '{normalized}'. This ATOM slide skill only supports 16:9 gpt-image-2 sizes: {allowed}.")
    return normalized


def size_label(size: str) -> str:
    return SIZE_LABELS[size]


def unresolved_items(archetype: str, grid_mode: str) -> list[str]:
    unresolved = PLACEHOLDER_BLOCKERS.copy()
    if archetype.startswith("UNRESOLVED"):
        unresolved.insert(1, "layout_archetype")
    if grid_mode.startswith("UNRESOLVED"):
        unresolved.insert(2, "grid_mode")
    return unresolved


def canonical_planning_block(
    archetype: str,
    grid_mode: str,
    mode: str,
    size: str,
    quality: str,
    primary_guideline: str,
) -> str:
    unresolved = unresolved_items(archetype, grid_mode)
    unresolved_text = ", ".join(unresolved) if unresolved else "none"

    return f"""planning_block:
  slide_claim: [one sentence]
  primary_guideline: {primary_guideline}
  guideline_priority: embedded ATOM design system in SKILL.md is the default source of truth
  generation_mode: {"image_edit" if mode == "repair" else "new_image"}
  image_model: {IMAGE_MODEL}
  image_size: {size}
  image_size_label: {size_label(size)}
  image_quality: {quality}
  image_background: opaque
  image_output_format: png
  image_moderation: auto
  image_n: 1
  image_streaming: optional for exploration, final QA uses completed image
  image_delivery_size: 1920x1080 after resize if exact ATOM delivery size is required
  generation_route: Codex built-in image generation
  generation_route_lock: PPTX is a delivery wrapper only; never use PPTX, PowerPoint export, screenshots, local rendering, HTML, SVG, canvas, or PIL to create final PNGs.
  image_generation_order: Correct order: generate gpt-image-2 PNGs, review and repair PNGs, then package approved PNGs into PPTX.
  blocked_generation_rule: If gpt-image-2 image generation is blocked, stop rather than manufacturing final PNGs through PPTX or local rendering.
  generation_status: pending_builtin_generation
  output_files: [filled after Codex image generation]
  google_slides_delivery: optional only when explicitly requested; otherwise not_requested
  google_slides_status: not_requested / pending_generated_images_and_pre_google_slides_image_review / inserted / blocked
  google_slides_title: N/A unless explicitly requested
  google_slides_file_id: N/A unless explicitly requested
  google_slides_url: N/A unless explicitly requested
  google_slides_slide_count: N/A unless explicitly requested; if requested, must match generated image count
  google_slides_route: N/A unless explicitly requested / direct_native_slides_batch_update / packaging_pptx_import / blocked
  google_slides_image_mapping: N/A unless explicitly requested; if requested, [slide_id -> generated PNG path -> Google slide objectId]
  google_slides_speaker_notes_mapping: N/A unless explicitly requested; if requested, [slide_id -> speakerNotesObjectId -> inserted note status]
  pptx_delivery: default image-only roll-up after all generated PNGs pass QA, unless user asks for image files only
  pptx_status: pending_generated_images_and_pre_package_image_review
  pptx_title: [filled when creating PPTX deck]
  pptx_output_path: [filled after PPTX creation]
  pptx_slide_count: [must match generated image count]
  pptx_packaging_route: scripts/package_slide_images_to_pptx.py / presentation_app_import / blocked
  pptx_image_mapping: [slide_id -> generated PNG path -> PPTX slide index]
  pptx_speaker_notes_mapping: [slide_id -> note source -> inserted / sidecar / blocked]
  speaker_notes_plan: one note per deck slide, drafted before image generation and inserted into PPTX or Google Slides notes page after image roll-up when the packaging route supports notes
  speaker_notes_status: drafted / inserted / blocked
  speaker_notes_text: [talk track + evidence/assumption cue + source caveat if relevant + transition cue; keep off slide image]
  opening_slide_role: opening_thesis_slide / standard_story_slide
  first_slide_not_title_only: true / N/A
  opening_density_gate: slide 1 has core thesis, 2-4 proof/tension points, visible market-shift/matrix/causal-map/wedge structure, and bridge
  pre_google_slides_image_review: required on actual generated PNG before any Google Slides insertion
  pre_package_image_review: required on actual generated PNG before any PPTX or Google Slides insertion
  image_review_iteration: 0 before first review; increment after each regenerated or edited PNG
  image_review_status: pending / approved / repair_required / blocked
  image_review_findings: [blocker/major/minor findings from multimodal self-review]
  image_repair_prompt: [concrete repair prompt if blockers or majors remain]
  image_repair_history: [iteration -> issue -> repair action -> regenerated PNG path -> re-audit result]
  image_review_matrix: [slide_id -> iteration -> png_path -> blockers -> majors -> repair_prompt -> new_png_path -> status]
  deck_consistency_matrix: [first_third -> middle_third -> last_third -> tone/layout/spacing/source consistency findings]
  final_image_quality_status: pending until every generated PNG has no blockers or majors and deck-level consistency passes
  deck_tone_consistency_review: [first third vs middle third vs last third tone comparison after generation]
  deck_tone_consistency_status: pending / approved / repair_required
  deck_tone_repair_plan: [slides to regenerate or edit if tone drift appears]
  post_generation_design_balance_check: required on actual generated PNGs before PPTX or Google Slides insertion; checks whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, and header integrity
  whitespace_occupancy_balance_status: pending / approved / repair_required
  typography_balance_status: pending / approved / repair_required
  color_consistency_status: pending / approved / repair_required
  outer_padding_consistency_status: pending / approved / repair_required
  header_integrity_status: pending / approved / repair_required
  layout_archetype: {archetype}
  layout_family: full-field / asymmetric-main-supporting-context / balanced-diptych / top-bottom / center-hub / process / matrix / small-multiple / swimlane / staircase
  composition_family: [same family label used for deck-level rhythm review]
  layout_diversity_plan: [deck-level plan for rotating compatible layout families according to claim type, evidence type, and decision question]
  layout_rotation_guard: [review neighboring slides for mechanical repetition; repeated families must serve comparison or deliberate rhythm]
  layout_sequence_table: [slide_number -> section_role -> claim_type -> layout_family -> composition_family -> previous_family -> repeat_or_change_reason]
  recent_layout_memory: [previous 3-5 slide layout families and why this slide repeats or changes]
  grid_mode: {grid_mode}
  column_spans: [12-column spans, integer columns only]
  row_tracks: [header/body/supporting-context/insight/source alignment baselines; source baseline is not a visible rule]
  column_tracks: [outer shell, main columns, separator, supporting/context columns]
  separator_x: [required when the selected composition uses a visible or structural separator; none when there is no split]
  outer_padding: 1672 basis left/right 44-56px, top/bottom 24-52px
  major_regions: [max three]
  coordinate_inventory_1672:
    - object: [major object name]
      x: [px]
      y: [px]
      w: [px]
      h: [px]
  master_components: [header, invisible footer alignment baseline, card/table/insight/icon masters]
  deck_master_refs: [reuse refs for header/footer/insight/table/card if deck-level]
  deck_tone_master_lock: [slide base, typography scale, header/footer, Deep Blue use, Honey use, illustration style, icon family, density rhythm, whitespace/occupancy rhythm, card/table geometry, outer padding, invisible source alignment baseline, negative prompt]
  visual_design_quality_traits: [design treatment only: calm light base, compact fixed header, thin structural rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, intentional canvas occupancy, concrete visual anchor, crisp focal hierarchy; do not change slide count, claim order, or storyline solely for this]
  imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
  concrete_visual_anchor: [the one object, scene, interface, workflow moment, artifact, evidence strip, map detail, or operational motif the reader can picture]
  observable_scene_or_object: [specific visible subject, not an abstract noun]
  viewpoint_crop: [front-on / top-down / close crop / cutaway / over-the-shoulder / operating view / process lane view, chosen from the claim]
  specific_visual_details: [2-4 concrete details such as rows, screens, gauges, handoff points, document snippets, machine cells, routes, timestamps, labels, annotations, or evidence artifacts]
  visual_specificity_plan: [how the concrete anchor, chart/table/matrix/flow, and details make the claim imaginable]
  editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
  visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide claim, evidence, and audience context
  claim_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide claim before adding supporting elements
  region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette
  composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy rhythm]
  secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
  body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions
  deck_header_master_lock:
    coordinate_basis: 1672x941
    status: exact_required_before_generation
    header_safe_area: [x/y/w/h exact selected values; ATOM default x=44 y=24 w=1584 h=136]
    vertical_line: [x/y/w/h/color exact selected values; ATOM default x=50 y=48 w=10 h=104 color #0B2F5B]
    header_line_top_rule: [line top at or 0-6px below visible H1 glyph top, never above; upward protrusion is blocker]
    h1: [x/y/w/max_lines/font_family/font_size/weight/line_height/color exact selected values; ATOM default x=88 y=34 w=1332 max_lines=1 font_family=Noto Sans JP size=32pt weight=700 line_height=1.10 color #2D332E]
    subtitle: [x/y/w/max_lines/font_family/font_size/weight/line_height/color exact selected values; ATOM default x=88 y=78 w=1332 max_lines=1 font_family=Noto Sans JP size=28pt weight=400 line_height=1.18 color #4D544E]
    visual_alignment: [visible line top at or 0-6px below visible H1 glyph top; visible line bottom 4-8px below subtitle lower visual edge; never protrude upward]
    body_start_y: [exact selected value; ATOM default 190, or 224 only if explicit two-line H1 fallback is declared]
    upper_right_clear_zone: [x/y/w/h exact selected values and empty; ATOM default x=1420 y=24 w=208 h=88]
    forbidden_header_elements: [slide number, title kicker, header badge, logo/right object unless guideline requires it, body objects above body_start_y]
  component_inventory: [master components and coordinates]
  equalized_groups: [cards, rows, phase cards, icons]
  shared_edges: [header, main structure, supporting region, insight, source alignment baseline; no visible Source separator]
  hand_placed_exceptions: [max two]
  visual_richness_role: restrained_signature_illustration / diagram_embedded_illustration / data_visual / icon_evidence / quiet_table
  signature_visual_plan: [main motif, supporting motifs, style, and why this slide deserves a memorable but restrained visual]
  illustration_region: [x/y/w/h in 1672 basis, or none for quiet table]
  illustration_intensity: 0_none / 1_marginal / 2_integrated / 3_restrained_signature
  human_designed_illustration_style: clean controlled editorial/vector illustration, crisp silhouette, intentional simplification, restrained fills, clear focal motif, only useful supporting details, projection/viewpoint chosen from the slide claim, no rough sketch, no arbitrary pseudo-depth, and no glossy AI concept-art finish
  creative_variance: low / medium / high; high acts like the requested higher temperature for composition, crop, viewpoint, and layout rhythm while locking brand/header/text/source rules
  density_tier: T1_sparse / T2_balanced / T3_dense / T4_appendix_dense
  density_layers: [main figure/table, evidence strip, context panel/legend, optional Insight]
  density_design:
    reader_mode: scan / read / reference
    decision_question: [what the reader can answer without narration]
    information_units: [claim, context, comparison, trend, mechanism, risk, implication, assumption, source]
    density_levers: [KPI strip, supporting context region, evidence strip, small multiples, annotation, benchmark/context column, source cue]
    overload_controls: [one dominant structure, max three major regions, body >=18pt equivalent, grouped labels, no decorative density]
  density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
  structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
  useful_density_plan: [2-4 proof/context/comparison points, units/denominators where relevant, source cue when traceable, and one clear reading path]
  information_unit_budget: [H1, subtitle, grouped body labels, decision-relevant data labels or rows, optional one-sentence Insight, required source when traceable; no default cap on decision-relevant numbers]
  density_guardrails: [preserve distinct claims, combine only repeated or shared-comparison slides, no smaller body text, no decorative illustration detail]
  header_anchor:
    vertical_line: exact x/y/w/h/color copied from deck_header_master_lock
    header_line_top_rule: copied from deck_header_master_lock and checked after generation
    h1: exact x/y/w/max_lines/font_family/font_size/weight/line_height/color copied from deck_header_master_lock
    subtitle: exact x/y/w/max_lines/font_family/font_size/weight/line_height/color copied from deck_header_master_lock
    visual_alignment: exact visual alignment rule copied from deck_header_master_lock
    body_start_y: exact selected y copied from deck_header_master_lock
    upper_right_clear_zone: exact x/y/w/h copied from deck_header_master_lock and kept empty
  footer_anchor_baseline: 1672 basis x=44-56 baseline y=895-912, invisible alignment position only, planned even if source_line is none
  header_footer_text_color_lock: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E; no Deep Blue/Honey/arbitrary gray in header or footer text
  message_box_scale_lock: compact interpretation surface; use the smallest legible variant; do not enlarge the box to carry long prose
  message_box_text_size_lock: message-box/Insight text default 20-24pt, 24-26pt only by exception; always at least 6pt smaller than selected H1, visually below subtitle, and never a second title
  max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
  table_note_microline: none / [one text note line above source text; not a horizontal rule]
  source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
  source_separator_lock: no horizontal divider, rule, underline, or hairline above Source
  source_line: Source: [traceable source names copied from provided or researched sources only] / none only when no traceable source exists
  source_policy: real traceable sources only; no draft, upload, internal-note, or production-route wording
  source_density_rule: Do not drop real source names to reduce visual density; shorten or group source names instead.
  brand_accent_usage_budget: restrained visual area; for ATOM work, Deep Blue uses standard 4-8%, may reach 10% on dense table slides, and may reach 12% only for rare chapter/closing slides; it never appears as body text
  deep_blue_usage_lock: exact #0B2F5B structural use; one active body blue system; no blue H1/subtitle/body/footer text; no extra blue hues
  brand_accent_system_role: header band / rule / icon / number / badge / matrix highlight / none, adjusted to the embedded ATOM design system
  visual_asset_judgment: use illustration/icons only if they improve understanding, memory, comparison, or navigation; no quota and no filler
  visual_asset_role: integrated_line_illustration / margin_vignette / icon_evidence_strip / diagram_embedded_icons / process_icons / data_icon_markers / none
  icon_system_plan: none / [role, style, stroke, color logic, grouping, why it helps]
  illustration_presence: none / marginal / integrated / restrained_signature
  insight_decision:
    keep_remove: [keep/remove]
    reason: [interpretation or decision need]
    variant: none / bottom-main / top-thesis / side-context-wide / side-context-tall / inline-pill / outlined thesis / outlined bottom / brand surface / dark brand surface / Honey surface when ATOM
    deck_count_check: [single slide or deck-level count]
    geometry: [x/y/w/h in 1672 basis if kept]
    height: [px]
    radius: 8px or 12px
    padding: [px]
    left_accent: [Honey uses #C49A2C 4-5px full-height left line; Deep Blue uses embedded ATOM design system accent line spec]
    background: [flat solid fill color only; Honey message box uses #F7EECF; no pattern, texture, gradient, motif, or internal illustration]
    text: [one judgment sentence if kept]
  human_crafted_feel: priority, breathing room, editorial rhythm
  qa_risks: [overcrowding, weak hierarchy, source uncertainty, decorative accent surface, unresolved grid]
  blocking_unresolved_items: {unresolved_text}"""


def mode_guidance(mode: str) -> str:
    if mode == "text-structure":
        return """mode_guidance:
  - Convert the long text into a slide-image deck structure before writing image prompts.
  - Use the embedded ATOM design system in SKILL.md; do not load an external ATOM pattern file.
  - Define deck_thesis, audience_decision, storyline_frame, section_map, and slide-level action_title claims.
  - Plan slide 1 as opening_thesis_slide, not a title-only opener: include the core thesis, 2-4 proof/tension points, a real visual structure, and a narrative bridge.
  - Map every claim to evidence, source_policy, visual_structure, layout_archetype, grid_mode, exact_text_budget, and split_merge_decision.
  - Apply source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists.
  - Build layout_diversity_plan: assign layout_family for each slide across full-field, asymmetric main/supporting-context, balanced comparison, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families when the argument benefits.
  - Use layout_rotation_guard to keep repeated structures purposeful: repeat a family for like-for-like comparison, and change family when claim type, evidence type, or decision question changes.
  - Draft speaker_notes_text for every slide: concise talk track, evidence/assumption cue, source caveat if relevant, and transition cue.
  - Add pre_package_image_review and pre_google_slides_image_review fields for every slide so generated PNGs are reviewed and repaired before PPTX or Slides insertion.
  - Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide before image prompting.
  - Run density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
  - Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting.
  - Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  - Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  - Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  - Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  - Apply visual_subject_open_set, claim_led_composition_lock, region_balance_policy, composition_fit_plan, secondary_region_integrity_lock, and body_silhouette_lock so the visual subject, region balance, focal relationship, canvas occupancy, secondary region, and body outline are chosen from the argument before image prompting.
  - Add useful density through comparison, benchmarks, denominators, assumptions, annotations, evidence strips, supporting context regions, small multiples, and source cues; do not add density through smaller type or decorative illustration detail.
  - Preserve distinct claims as separate slides; combine only repeated claims or evidence that must be compared in one view.
  - Define deck_header_master_lock with exact x/y/w/h/color/font values, then repeat it verbatim in every slide prompt.
  - Read only the action titles in order; repair gaps before image generation.
  - Do not generate final images until every selected slide has a canonical planning block."""
    if mode == "deck-plan":
        return """mode_guidance:
  - Define deck thesis and one claim per slide.
  - Use the embedded ATOM design system in SKILL.md; do not load an external ATOM pattern file.
  - Start with opening_thesis_slide rather than a title-only first slide: the opener should make the main phrase memorable while also showing the thesis, tension/proof points, structure, and bridge.
  - Select layout_archetype and grid_mode for every slide.
  - Apply source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists.
  - Create layout_diversity_plan and layout_rotation_guard before final prompts so the deck can use the expanded pattern catalogue without drifting from ATOM brand and header rules.
  - Define deck_header_master_lock before any slide-level prompt. Do not leave header coordinates as ranges.
  - Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide; use human-designed editorial/vector illustrations on chapter openers, turning points, complex systems, and final vision slides.
  - Assign density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
  - Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting.
  - Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  - Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  - Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  - Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  - Apply visual_subject_open_set, claim_led_composition_lock, region_balance_policy, composition_fit_plan, secondary_region_integrity_lock, and body_silhouette_lock so the visual subject, region balance, focal relationship, canvas occupancy, secondary region, and body outline are chosen from the argument before image prompting.
  - Preserve distinct claims as separate slides; combine only repeated claims or evidence that must be compared in one view.
  - Define deck master refs for header, invisible footer alignment baseline, Insight surfaces, tables, cards, and icon circles.
  - Allocate Insight components selectively across the deck and avoid mechanical card-only repetition.
  - Draft speaker_notes_text for every slide and plan PPTX roll-up with one full-bleed generated PNG plus corresponding speaker notes per slide. Plan Google Slides only when explicitly requested.
  - Plan a pre_package_image_review loop: inspect actual generated PNGs, classify blocker/major/minor issues, repair/regenerate, and approve only after image quality is sufficient.
  - Do not generate final images until each slide has its own canonical planning block."""
    if mode == "repair":
        return """mode_guidance:
  - Inspect the screenshot or rendered slide first.
  - Inventory visible header/footer, grid, row/column tracks, repeated sizes, typography, brand accent/Insight use, and source hygiene.
  - Audit missing Source footer when traceable sources exist, missing header line, H1 color drift, subtitle drift, missing illustration, overpowered AI-looking illustration, under-dense structure, weak visual subject, unclear focal relationship, and unbalanced canvas occupancy.
  - Rebuild the canonical planning block from the observed slide before revising.
  - Fix grid drift and text overflow before color or decorative changes."""
    if mode == "audit":
        return """mode_guidance:
  - Audit Guideline/Brand, Layout, Typography, Content, Model, and Deck gates.
  - Mark each gate pass/fail.
  - For every fail, choose trim, split, regrid, quiet hierarchy, add/remove Insight, or source cleanup.
  - Re-audit after proposed changes."""
    return """mode_guidance:
  - Produce one slide planning block, then image_model, draft_image_prompt_scaffold, negative_prompt_hard_blockers, and post_generation_audit.
  - Include pre_package_image_review, pre_google_slides_image_review, and repair_iteration_plan; do not treat first generation as final without inspecting the actual PNG.
  - Treat unresolved layout_archetype or grid_mode as blockers before final generation."""


def scaffold_header(brief: str, mode: str, language: str, size: str, quality: str, primary_guideline: str) -> str:
    return f"""Slide image prompt scaffold

mode: {mode}
language: {language}
primary_guideline: {primary_guideline}
image_model: {IMAGE_MODEL}
image_size: {size}
image_size_label: {size_label(size)}
image_quality: {quality}

brief:
{brief}

{mode_guidance(mode)}
"""


def image_prompt_tail(size: str, quality: str, mode: str, primary_guideline: str) -> str:
    if mode == "repair":
        prompt_lead = f"""  Edit the provided slide image/reference with {IMAGE_MODEL}, image_size {size}, image_quality {quality}, background opaque, output_format png, moderation auto, n=1.
  Change only the issues listed in the planning block or repair brief.
  Preserve everything else: layout, grid, arrows, labels, source text position, typography hierarchy, colors, icons, and surrounding objects."""
    else:
        prompt_lead = f"""  Draw a 16:9 strategy slide image with {IMAGE_MODEL}, image_size {size}, image_quality {quality}, background opaque, output_format png, moderation auto, n=1."""
    return f"""image_model: {IMAGE_MODEL}
generation_route: Codex built-in image generation
prompt_readiness: draft_scaffold_until_blocking_unresolved_items_none

draft_image_prompt_scaffold:
{prompt_lead}
  Use the embedded ATOM design system in SKILL.md. Do not load an external ATOM pattern file.
  PPTX is a delivery wrapper only. Never create final PNGs by exporting, rendering, or screenshotting a PPTX.
  Correct order: generate gpt-image-2 PNGs, review and repair PNGs, then package approved PNGs into PPTX.
  If gpt-image-2 image generation is blocked, stop rather than manufacturing final PNGs through PPTX or local rendering.

  Plan coordinates on a 1672x941 basis with ATOM delivery target 1920x1080 after resize if required.
  Use size terminology consistently: 1920x1080 is FHD/1080p delivery, 2048x1152 is 16:9 2K-width generation, 2560x1440 is QHD/1440p generation, and 3840x2160 is 4K UHD generation.
  Use a 12-column grid, 8px spacing rhythm, precise shared edges, and fixed header/footer anchors.
  Define deck_tone_master_lock before slide-level prompting and preserve it through the whole deck: slide base, typography scale, header/footer, Deep Blue role, Honey treatment, illustration style, icon family, density rhythm, whitespace/occupancy rhythm, card/table geometry, outer padding, invisible source alignment baseline, and negative prompt. Later slides must feel like the same deck as the first approved pilot slides.
  Apply visual_design_quality_traits as design treatment: calm light base, compact fixed header, thin structural rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, concrete visual anchor, crisp focal hierarchy, and deliberate canvas occupancy. Do not alter slide count, claim order, or storyline solely for visual style.
  Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  Apply visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide claim, evidence, and audience context.
  Apply claim_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide claim before adding supporting elements.
  Apply region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette.
  Apply composition_fit_plan: set the main visual field, supporting regions, whitespace role, and Insight footprint before generation so the canvas has deliberate occupancy and breathing room.
  Apply secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field.
  Apply body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions.
  Apply layout_diversity_plan at deck level: choose layout families from full-field, asymmetric main/supporting-context, balanced diptych, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase patterns according to the slide claim. Use layout_rotation_guard so neighboring slides do not fall into the same composition by habit; repeated families should make comparison easier.
  Define and preserve one deck_header_master_lock with exact selected values, not ranges: coordinate_basis, header_safe_area, vertical_line x/y/w/h/color, header_line_top_rule, H1 x/y/w/max_lines/font_size/weight/line_height/color, subtitle x/y/w/max_lines/font_size/weight/line_height/color, visual_alignment, body_start_y, and upper_right_clear_zone. Repeat it verbatim across the deck. Treat the header as the lowest-freedom component; no_header_ranges_in_final_prompts.
  Include coordinate_inventory_1672 and reuse master_components before generating repeated objects.
  Use Noto Sans JP for every visible text string, including Latin/English letters, numbers, symbols, and Japanese. Do not mix in any other typeface; if exact font rendering is unavailable in image generation, use the closest Noto Sans JP-like rendering without changing the font family intent.
  Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  For ATOM work, use #FCFBF8 to #F4F3EF slide base, #2D332E text, #4D544E subtitle, #6E756E footer/source/table-note text, and #0B2F5B Deep Blue structure.
  H1 30-34pt weight 700 #2D332E, subtitle 26-30pt weight 400 #4D544E, body 18pt equivalent. Use the exact default ATOM header: 1672 basis header_safe_area x=44 y=24 w=1584 h=136; vertical_line x=50 y=48 w=10 h=104 #0B2F5B; header_line_top_rule line top at or 0-6px below visible H1 glyph top, never above; H1 x=88 y=34 w=1332 max_lines=1 size=32pt weight=700 line_height=1.10 #2D332E; subtitle x=88 y=78 w=1332 max_lines=1 size=28pt weight=400 line_height=1.18 #4D544E; visual_alignment line top never protrudes above H1 and line bottom 4-8px below subtitle lower visual edge; body_start_y=190; upper_right_clear_zone x=1420 y=24 w=208 h=88 empty. Two-line H1 fallback: vertical_line y=48 with h recalculated to end 4-8px below subtitle lower visual edge, subtitle y=112, body_start_y=224. No Deep Blue H1.
  Lock header and footer text colors as one Ink-family hierarchy: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E. Do not use Deep Blue, Honey, yellow, or arbitrary gray for header/footer text.
  Let structure, numbers, rules, spacing, and typography carry the hierarchy.
  Use small Lucide-style line icons as quiet wayfinding only when they clarify reading order, evidence, or interaction.
  Include visual_richness_role, illustration_intensity, creative_variance, and density_tier in the prompt. Use human-designed editorial/vector illustrations and purpose-built motifs where they add memory, scanning help, or navigation.
  Include density_design in the prompt. Density should answer the reader's decision_question through grouped information units, comparison baselines, evidence strips, supporting context regions, small multiples, annotations, units, assumptions, and source cues. Do not solve density with smaller body text, extra decorative cards, or illustration detail.
  Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting. Prefer adding decision-relevant comparison, benchmark, denominator, unit, assumption, source cue, or annotation before adding decorative space.
  Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  When creative_variance is high, vary composition, viewpoint, crop, asymmetric region balance, visual metaphor, and layout rhythm; keep brand, header, exact text, grid, and source policy locked.
  Let the planned chart/table/matrix/roadmap carry the argument where it is the clearest reader path; illustration adds memory, wayfinding, and selective emphasis through a clear focal motif, useful supporting details, clean controlled linework, crisp silhouettes, restrained fills, and small annotations.
  Make abstract claims imageable by naming the concrete visual anchor and visible details: an operating view, workflow handoff, document stack, data row, map route, queue, machine cell, screen state, evidence artifact, or customer moment that fits the claim.
  Keep speaker notes out of the slide image. Speaker notes are inserted later into Google Slides notes pages and should not appear as visible on-slide text.
  Do not hard-code one visual grammar across slides. Select the projection, viewpoint, abstraction level, motif, and level of detail from the slide claim; use depth or spatial perspective only when it carries meaning. Do not use decorative trapezoid planes, fake perspective floors, isometric boxes, tilted architectural slabs, vanishing points, or pseudo-3D depth as a shortcut for freshness.
  Keep visual subject selection open and claim-led; use the subject that makes the argument most observable through scale, interaction, place, evidence, or operating context.
  Create freshness through viewpoint, asymmetric composition, designed margin vignettes, evidence strips, partial cutaways, and magnified details, not decoration or glossy concept art.
  Use Deep Blue structurally with a 4-8% visual area budget, up to 12% only for strong closing slides, and never for body text.
  Use Honey only for ATOM or compatible guidelines where it is a decision signal: #F7EECF flat pale Honey fill, #C49A2C 4-5px full-height left accent line, #2D332E text, one component maximum.
  Use flat solid fills for all message boxes and Insight surfaces; do not add patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations inside the box.
  Apply message_box_scale_lock: message boxes are compact interpretation surfaces, not display surfaces; keep copy to one short judgment sentence, prefer one line, max two lines, and do not enlarge the surface to rescue long prose.
  Apply message_box_text_size_lock: message-box/Insight text defaults to 20-24pt, uses 24-26pt only by exception, stays at least 6pt smaller than the selected H1, remains visually below the subtitle, and never becomes a second title or second hero headline.
  Enforce max_text_size_lock across every visible string; do not use display typography, hero numerals, badges, or message-box text above the cap.
  Keep Honey quiet and consistent: no saturated yellow fills, no dark yellow message boxes, no large yellow areas, no yellow title underline, and no Honey color variation across a deck.
  Use illustrations/icons when they help understanding, memory, comparison, or navigation; do not add them by quota. A slide with no icon or illustration is acceptable when the structure already carries the claim.
  Do not minimize numbers by default. Keep sourced or explicitly assumed numbers when they help comparison, sizing, prioritization, credibility, or decision-making; remove only unsupported, redundant, unreadable, or decorative numbers.
  Render ONLY the exact text strings listed in the planning block or final prompt; do not invent extra labels.
  Keep footer_anchor_baseline planned as an invisible alignment position even when source_line is none.
  Apply source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists.
  Apply source_separator_lock: no horizontal divider, rule, underline, or hairline above Source.
  Do not drop real source names to reduce visual density; shorten or group source names instead.
  Do not include slide numbers, title kickers, numbered header badges, KEY INSIGHT labels, invented sources, or production-route source wording.
  Make the composition feel human-crafted through visible priority, breathing room, and editorial rhythm.

negative_prompt_hard_blockers:
  local-rendered substitute, non-gpt-image output, missing or malformed header line, header line protruding above H1,
  H1/subtitle/source color drift, horizontal divider above Source, body content invading header/footer, visible text above max_text_size_lock, unreadable body text below 18pt equivalent,
  invented labels or sources, speaker notes visible on slide, unresolved grid, severe grid drift, hard-to-picture abstract visual,
  patterned or textured message box, oversized message box, message-box text competing with H1/subtitle,
  saturated yellow message box, decorative pseudo-3D depth, rough sketch aesthetic,
  mechanical repeated composition without narrative or comparison purpose, generic icon-only composition, dated template composition, slide number, title kicker, logo in upper-right clear zone

post_generation_audit:
  - image model is {IMAGE_MODEL}
  - generation_route is Codex built-in image generation, not local rendering or a user-key workaround
  - image_size {size} is valid for gpt-image-2, labeled as {size_label(size)}, and final delivery is resized only after generation if needed
  - H1 and subtitle hierarchy is clear
  - max_text_size_lock is honored: no visible text exceeds 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
  - deck_header_master_lock is visible and consistent; left header line is present, obeys header_line_top_rule, does not protrude above the H1 glyph top, and H1 color follows the embedded ATOM design system
  - header_footer_text_color_lock is honored: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E
  - header/footer text does not use Deep Blue, Honey, yellow, or arbitrary gray
  - visual_richness_role is fulfilled; planned illustration or visual motif is present when required
  - imageability_lock is fulfilled: a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details are present
  - editorial_polish_repair_loop has improved specificity, proportion, rhythm, and focal hierarchy
  - visual_subject_open_set is fulfilled: the selected visual subject comes from the slide claim, evidence, and audience context rather than a fixed asset menu
  - claim_led_composition_lock is fulfilled: one focal relationship carries the argument before supporting elements
  - region_balance_policy is fulfilled: region weight follows the slide claim, evidence shape, reading path, and body silhouette rather than a fixed template
  - composition_fit_plan is fulfilled: the main visual field, supporting regions, whitespace role, and Insight footprint feel intentionally balanced
  - secondary_region_integrity_lock is fulfilled: any split or auxiliary region reads as a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
  - body_silhouette_lock is fulfilled: the body reads as one closed visual block with aligned outer edges, lower edges, and footer clearance
  - illustration_intensity is respected; illustration feels designer-authored and does not overpower the slide
  - density_tier and density_design are fulfilled without shrinking body text below 18pt equivalent
  - density_lift_lock is fulfilled in both the slide structure and final image prompt
  - structure_first_visual_mix is fulfilled through argument-carrying charts, tables, matrices, flows, maps, comparison axes, or evidence strips where appropriate, with illustration used as support
  - density_levers improve the claim through comparison, evidence, annotation, grouping, or source cues rather than decoration
  - decision-relevant numbers are preserved when legible; numbers are not minimized by default
  - message boxes and Insight surfaces use flat solid fills only, with no decorative patterns or motifs
  - message_box_scale_lock is honored: message boxes stay compact and are not enlarged to carry long prose
  - message_box_text_size_lock is honored: message-box/Insight text is smaller than H1 and subtitle and never reads as a second title
  - Honey message boxes use #F7EECF fill, #C49A2C 4-5px left accent line, and #2D332E text consistently
  - saturated yellow, dark yellow, or large yellow areas are absent
  - coordinate_inventory_1672 matches visible major objects
  - all major regions snap to grid/shared edges
  - layout_family matches the slide claim, and layout_diversity_plan / layout_rotation_guard make deck-level composition feel intentionally varied rather than mechanically repeated
  - repeated elements are equalized
  - body text remains readable
  - embedded ATOM design system palette and typography are followed
  - brand accent is structural and not body text
  - Insight component is selective, compatible with the embedded ATOM design system, and not decorative
  - invisible footer alignment baseline is preserved without drawing a line
  - Source footer follows source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
  - Source footer follows source_separator_lock: no horizontal divider, rule, underline, or hairline above Source
  - footer/source/table-note text uses #6E756E consistently when present
  - speaker_notes_text exists for deck slides but does not appear on the slide image
  - deck_tone_consistency_status is approved after comparing first third, middle third, and last third for palette, linework, icon family, illustration intensity, density rhythm, card geometry, and source behavior
  - post_generation_design_balance_check is approved on actual generated PNGs: whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, header integrity, card/table height equalization, line-weight consistency, icon-family consistency, Deep Blue scatter, Honey strength, and human-designed operational diagram feel
  - pre_package_image_review has inspected the actual generated PNG, not only the prompt
  - pre_google_slides_image_review is also approved when Google Slides roll-up is requested
  - image_review_status is approved only when there are no blocker or major issues
  - PPTX roll-up starts only after final_image_quality_status is approved for every generated PNG
  - PPTX roll-up contains one full-bleed generated PNG per slide in order, with speaker notes inserted when packaging supports notes
  - Google Slides roll-up, when requested, contains one full-bleed generated PNG per slide and speaker notes inserted on every corresponding slide

pre_package_image_review:
  - Inspect the actual generated PNG with multimodal review before any PPTX or Google Slides insertion.
  - Score model route, exact text, header lock, grid/shared edges, typography, density, illustration clarity, human-designed feel, source hygiene, and speaker-notes separation.
  - Score layout_family fit and layout_rotation_guard across the generated image set.
  - Score deck_tone_consistency across all generated PNGs after every generation or repair batch.
  - Score post_generation_design_balance_check: whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, and header integrity.
  - Classify each finding as blocker, major, minor, or accepted.
  - If any blocker or major exists, create image_repair_prompt, regenerate or edit the PNG, replace the output file, and repeat this review.
  - Continue until final_image_quality_status is approved, or stop at five review/regeneration iterations and report unresolved issues.

repair_iteration_plan:
  - iteration_0: first generated PNG review
  - iteration_1_to_5: repair prompt -> regenerated/edited PNG -> re-review
  - approval_condition: no blockers, no majors, minor issues only if they do not affect readability, brand fidelity, source integrity, or deck consistency
"""


def deck_plan_tail() -> str:
    return """deck_plan_output:
  - deck_thesis:
  - primary_guideline:
  - guideline_priority:
  - brand_style_notes:
  - opening_slide_rule:
      opening_slide_role: opening_thesis_slide
      first_slide_not_title_only: true
      opening_density_gate: core thesis + 2-4 proof/tension points + visible market-shift/matrix/causal-map/wedge structure + bridge
      low_density_opener_repair: add evidence, tension, comparison, or mechanism before image generation
  - slide_list:
      - slide_number:
        slide_claim:
        opening_slide_role: opening_thesis_slide / standard_story_slide
        first_slide_not_title_only: true / N/A
        opening_density_gate:
        layout_archetype:
        layout_family:
        composition_family:
        previous_layout_family:
        repeat_or_change_reason:
        grid_mode:
        visual_richness_role:
        illustration_intensity:
        creative_variance:
        density_tier:
        signature_visual_plan:
        insight_decision:
        source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
        source_separator_lock: no horizontal divider, rule, underline, or hairline above Source
        source_policy:
        source_line:
        density_risk:
        speaker_notes_text:
        speaker_notes_source_cues:
        speaker_notes_transition:
        density_design:
          reader_mode:
          decision_question:
          information_units:
          density_levers:
          overload_controls:
        density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
        structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
        max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
        imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
        editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
        visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide claim, evidence, and audience context
        claim_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide claim before adding supporting elements
        region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette
        composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy rhythm]
        secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
        body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions
        information_unit_budget:
        density_guardrails:
        concrete_visual_anchor:
        visual_specificity_plan:
  - deck_master_refs:
  - layout_diversity_plan:
  - layout_rotation_guard:
  - layout_sequence_table:
      - slide_number:
        section_role:
        claim_type:
        layout_family:
        composition_family:
        previous_family:
        repeat_or_change_reason:
  - deck_tone_master_lock:
  - visual_design_quality_traits:
  - deck_header_master_lock:
  - header_line_top_rule:
  - deep_blue_usage_lock:
  - visual_asset_judgment:
  - visual_richness_mix_plan:
  - density_tier_plan:
  - density_design_plan:
  - insight_count_plan:
  - source_collection_needs:
  - speaker_notes_plan:
  - pre_google_slides_review_plan:
  - pre_package_image_review_plan:
  - image_review_matrix:
      - slide_id:
        iteration:
        png_path:
        blockers:
        majors:
        repair_prompt:
        new_png_path:
        status:
  - deck_consistency_matrix:
      first_third:
      middle_third:
      last_third:
      tone_layout_spacing_source_findings:
  - pptx_rollup_plan:
  - google_slides_rollup_plan: optional only when explicitly requested
  - slides_requiring_full_planning_block:
  - blocking_unresolved_items: all slide-level planning blocks remain required before image generation
"""


def text_structure_tail() -> str:
    return """text_to_slide_structure_output:
  deck_thesis:
  audience_decision:
  primary_guideline:
  guideline_priority:
  brand_style_notes:
  storyline_frame: SCQA / problem-solution-evidence / past-present-future / market-problem-solution-moat / investment-thesis-risk-milestones
  claim_backlog:
  evidence_ledger:
  source_ledger:
  appendix_candidates:
  open_questions:
  opening_slide_rule:
    opening_slide_role: opening_thesis_slide
    first_slide_not_title_only: true
    opening_density_gate: core thesis + 2-4 proof/tension points + visible market-shift/matrix/causal-map/wedge structure + bridge
    low_density_opener_repair:
  section_map:
    - section:
      role:
      slide_ids:
  slide_structure:
    - slide_id:
      chapter:
      action_title:
      opening_slide_role: opening_thesis_slide / standard_story_slide
      first_slide_not_title_only: true / N/A
      opening_density_gate:
      reader_question_answered:
      claim_type: context / urgency / solution / evidence / moat / market / economics / roadmap / risk / vision
      evidence_items:
      evidence_strength:
      source_span_ids:
      source_policy: real source / none / research needed
      source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
      source_separator_lock: no horizontal divider, rule, underline, or hairline above Source
      source_line: Source: [traceable source names copied from provided or researched sources only] / none only when no traceable source exists
      source_urls:
      assumptions:
      speaker_notes_text:
      speaker_notes_source_cues:
      speaker_notes_transition:
      pre_google_slides_image_review:
      pre_package_image_review:
      image_review_iteration:
      image_review_status:
      image_review_findings:
      image_repair_prompt:
      image_repair_history:
      image_review_matrix:
        slide_id:
        iteration:
        png_path:
        blockers:
        majors:
        repair_prompt:
        new_png_path:
        status:
      final_image_quality_status:
      deck_tone_consistency_review:
      deck_tone_consistency_status:
      deck_consistency_matrix:
        first_third:
        middle_third:
        last_third:
        tone_layout_spacing_source_findings:
      visual_design_quality_traits:
      visual_structure: comparison / table / flow / roadmap / loop / matrix / KPI strip / architecture stack / signature visual
      visual_richness_role: restrained_signature_illustration / diagram_embedded_illustration / data_visual / icon_evidence / quiet_table
      visual_asset_judgment:
      visual_asset_role: integrated_line_illustration / margin_vignette / icon_evidence_strip / diagram_embedded_icons / process_icons / data_icon_markers / none
      icon_system_plan:
      signature_visual_plan:
      illustration_presence: none / marginal / integrated / restrained_signature
      illustration_intensity: 0_none / 1_marginal / 2_integrated / 3_restrained_signature
      human_designed_illustration_style:
      creative_variance: low / medium / high
      density_tier: T1_sparse / T2_balanced / T3_dense / T4_appendix_dense
      density_layers:
      density_design:
        reader_mode: scan / read / reference
        decision_question:
        information_units:
        density_levers:
        overload_controls:
      density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
      structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
      information_unit_budget:
      density_guardrails:
      deck_header_master_lock:
      header_line_top_rule:
      deck_tone_master_lock:
      deep_blue_usage_lock:
      header_footer_text_color_lock:
      message_box_scale_lock:
      message_box_text_size_lock:
      max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
      imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
      editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
      visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide claim, evidence, and audience context
      claim_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide claim before adding supporting elements
      region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide claim, evidence shape, reading path, and body silhouette
      composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy rhythm]
      secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
      body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions
      concrete_visual_anchor:
      visual_specificity_plan:
      layout_archetype:
      layout_family:
      composition_family:
      layout_diversity_plan:
      layout_rotation_guard:
      layout_sequence_table:
      recent_layout_memory:
      grid_mode:
      exact_text:
        h1:
        subtitle:
        body_labels:
        chart_labels:
        insight_text:
      data_to_render:
      exact_text_budget: H1 + subtitle + short labels + decision-relevant numbers + optional one-sentence Insight
      insight_decision:
      density_risk:
      split_merge_decision:
      prompt_text_budget:
      image_prompt_ready: yes/no
  title_readthrough_check:
  layout_diversity_plan:
  layout_rotation_guard:
  layout_sequence_table:
  unresolved_items:
  pptx_rollup_plan:
  google_slides_rollup_plan: optional only when explicitly requested
  next_step: create canonical planning blocks for image_prompt_ready slides, run Codex built-in image generation pilot, then run pre_package_image_review before any PPTX or Google Slides insertion."""


def audit_tail() -> str:
    return """audit_output:
  - brand_gate: pass/fail with fixes
  - layout_gate: pass/fail with fixes
  - typography_gate: pass/fail with fixes
  - content_gate: pass/fail with fixes
  - model_route_gate: pass/fail with fixes
  - deck_gate: pass/fail with fixes
  - required_repairs:
  - re_audit_result:
"""


def build_prompt(
    brief: str,
    mode: str,
    archetype: str,
    grid_mode: str,
    language: str,
    size: str,
    quality: str,
    primary_guideline: str,
) -> str:
    header = scaffold_header(brief, mode, language, size, quality, primary_guideline)
    if mode == "text-structure":
        return f"{header}\n{text_structure_tail()}"
    if mode == "deck-plan":
        return f"{header}\n{deck_plan_tail()}"
    if mode == "audit":
        return f"{header}\n{audit_tail()}"
    planning = canonical_planning_block(archetype, grid_mode, mode, size, quality, primary_guideline)
    return f"{header}\n{planning}\n\n{image_prompt_tail(size, quality, mode, primary_guideline)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", nargs="?", help="Path to a UTF-8 text/markdown brief")
    parser.add_argument("--mode", default="single-slide-image", choices=["single-slide-image", "text-structure", "deck-plan", "repair", "audit"])
    parser.add_argument("--archetype", default=UNRESOLVED_ARCHETYPE)
    parser.add_argument("--grid-mode", default=UNRESOLVED_GRID_MODE)
    parser.add_argument("--language", default="Japanese")
    parser.add_argument("--size", default="2560x1440")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument(
        "--primary-guideline",
        default="embedded ATOM design system",
        help="Optional label only; embedded ATOM design system is the default and no external pattern file is required.",
    )
    args = parser.parse_args()

    brief = read_brief(args.brief)
    size = validate_size(args.size)
    print(build_prompt(brief, args.mode, args.archetype, args.grid_mode, args.language, size, args.quality, args.primary_guideline))


if __name__ == "__main__":
    main()
