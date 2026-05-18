#!/usr/bin/env python3
"""Build a guideline-aware slide image prompt scaffold from a rough brief."""

from __future__ import annotations

import argparse
from pathlib import Path


UNRESOLVED_ARCHETYPE = "UNRESOLVED - choose one guideline-compatible layout_archetype before final prompt"
UNRESOLVED_GRID_MODE = "UNRESOLVED - choose one grid_mode before final prompt"
IMAGE_MODEL = "gpt-image-2"
ALLOWED_16_9_SIZES = {"2048x1152"}
SIZE_LABELS = {
    "2048x1152": "default 16:9 2K-width image-generation output size",
}
REQUIRED_PROMPT_FIELDS = [
    "slide_message",
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
    "default_2k_generation_lock",
    "nonconforming_existing_png_regeneration_lock",
    "pdf_export_source_lock",
    "visible_text_only_lock",
    "render_contract_lock",
    "prompt_order_lock",
    "positive_quality_lock",
    "edit_scope_lock",
    "revised_prompt_review_lock",
    "exact_text_fidelity_lock",
    "chart_semantic_integrity_lock",
    "thumbnail_legibility_lock",
    "reading_path_lock",
    "editorial_polish_repair_loop",
    "visual_subject_open_set",
    "message_led_composition_lock",
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
    "illustration_tone_lock",
    "illustration_style_sheet",
    "illustration_consistency_status",
    "creative_variance",
    "density_tier",
    "density_layers",
    "density_design",
    "reader_mode",
    "decision_question",
    "information_units",
    "sentence_density_lift_lock",
    "semantic_sentence_layer",
    "semantic_copy_gate",
    "icon_restraint_plan",
    "icon_restraint_lock",
    "icon_density_budget",
    "information_unit_budget",
    "density_levers",
    "density_guardrails",
    "overload_controls",
    "near_white_slide_base_lock",
    "header_anchor",
    "header_left_accent_master_lock",
    "header_left_accent_reference_lock",
    "header_left_accent_shape_lock",
    "header_left_accent_no_protrusion_rule",
    "header_left_accent_top_protrusion_blocker",
    "footer_anchor_baseline",
    "header_footer_text_color_lock",
    "message_box_scale_lock",
    "message_box_text_size_lock",
    "post_generation_design_balance_check",
    "source_policy",
    "source_real_only_lock",
    "source_placeholder_blocklist",
    "output_artifact_mastering_lock",
    "single_final_png_master_lock",
    "no_duplicate_png_output_lock",
    "contact_sheet_mastering_lock",
    "single_contact_sheet_policy",
    "speaker_notes_depth_lock",
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
        raise SystemExit(f"Invalid --size '{size}'. Use 2048x1152 for 16:9 2K slide PNG masters.") from exc

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
    unresolved = REQUIRED_PROMPT_FIELDS.copy()
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
  slide_message: [one sentence]
  primary_guideline: {primary_guideline}
  guideline_priority: embedded ATOM design system in SKILL.md is the default source of truth
  generation_mode: {"image_edit" if mode == "repair" else "new_image"}
  image_model: {IMAGE_MODEL}
  model_route_assumption: Codex built-in image generation is the gpt-image-2 route for this skill unless image metadata proves otherwise
  image_size: {size}
  image_size_label: {size_label(size)}
  image_quality: {quality}
  image_background: opaque
  image_output_format: png
  image_moderation: auto
  image_n: 1
  image_streaming: optional for exploration, final QA uses completed image
  image_delivery_size: 2048x1152; PPTX/PDF packaging uses the same approved 2K slides_final/ PNG masters
  default_2k_generation_lock: use image_size 2048x1152 as the generated slide output for review, repair, PPTX, and PDF packaging; do not create alternate 16:9 delivery PNG masters
  nonconforming_existing_png_regeneration_lock: existing/source PNGs at 1672x941 or any non-approved size are not final blockers and must not be converted, upscaled, HTML-rendered, API-rendered, or locally redrawn; reuse the approved slide specification and generate new 2048x1152 slides_final/ masters with Codex built-in gpt-image-2, then review and package those generated masters
  pdf_export_source_lock: create PDF outputs from the approved slides_final/ PNG masters; do not copy final PNGs into render_check/pdf_pages/ as a second source of truth
  generation_route: Codex built-in image generation
  builtin_generation_lock: when slide images are requested in Codex, invoke Codex built-in image generation directly and start generating; do not pause for local environment preflight or local artifact-route probing before generation
  codex_image_artifact_rule: Codex built-in image generation returns the authoritative generated PNG artifact; use the Codex-provided artifact/download/attachment path to materialize approved outputs under slides_final/ when a filesystem path is needed for PPTX packaging
  image_generation_tool_lock: final slide PNG pixels must be produced by Codex built-in image generation, not by repo scripts, local renderers, screenshots, or presentation exports
  script_boundary_lock: prompt builder scripts are planning helpers only; package scripts run only after approved Codex image artifacts exist and must never render, draw, screenshot, export, simulate, or replace final slide PNGs
  local_env_non_blocker: local environment uncertainty is not a blocker and must not be reported as the reason PPTX is unfinished
  credential_setup_blocker: do not create, request, decrypt, configure, inspect, or wait for account credentials, local tokens, SDK setup, or environment variables; use Codex built-in image generation directly
  progress_update_route_lock: user-facing progress updates must not narrate local credentials, environment variables, SDK setup, save-route probing, or alternate account/setup routes as prerequisites; say that slide structuring and built-in image generation are starting
  visible_text_only_lock: list every on-slide string under exact_text before generation; render only those strings and no lock names, YAML keys, review statuses, or workflow instructions
  render_contract_lock: keep non-rendered instructions, audit fields, lock names, and route/status metadata outside the visible slide content; if any appears in the PNG, repair or regenerate
  prompt_order_lock: final prompts should lead with draw/edit action, visible text contract, canvas/layout, concrete visual anchor, semantic graphics, style system, source/footer behavior, then targeted blockers
  positive_quality_lock: state the desired calm editorial slide quality before blockers; use hard blockers only for concrete failure modes and avoid broad aesthetic negation that weakens the desired composition
  edit_scope_lock: repair prompts must name target region, preserve list, change list, and forbidden side effects before invoking edit
  revised_prompt_review_lock: if the image tool exposes a revised_prompt or rewritten prompt, compare it against exact_text, source policy, header master, and visible/non-visible boundaries before approving the generated PNG
  generation_route_lock: PPTX is a delivery wrapper only; never use PPTX, PowerPoint export, screenshots, local rendering, HTML, SVG, canvas, or PIL to create final PNGs.
  pptx_first_blocker: do not create a presentation deck as the source of truth before image generation; generate and review slide PNGs first, then package approved PNGs into PPTX at the end
  image_generation_order: Correct order: generate gpt-image-2 PNGs, review and repair PNGs, then package approved PNGs into requested PPTX/PDF outputs.
  blocked_generation_rule: only mark blocked after invoking Codex built-in image generation and the tool itself fails, is unavailable, or refuses the request; local environment uncertainty is not a generation blocker
  generation_status: pending_builtin_generation
  output_files: [filled after Codex image generation]
  output_artifact_mastering_lock: slides_final/ is the only loose-PNG master for approved generated slide images; package and review artifacts reference it instead of making additional loose PNG copies
  single_final_png_master_lock: keep each approved final PNG in exactly one master path under slides_final/ and record that path in review_manifest, package_image_mapping, pptx_image_mapping, pdf_image_mapping
  slides_package_policy: slides_package/ contains PPTX, speaker notes, review_manifest, and metadata only; do not copy final PNG files into slides_package/
  render_check_policy: render_check/pdf_pages/ is optional disposable QA output from PDF/PPT render checks, not a second source of truth; do not copy slides_final/ PNGs there, and overwrite or ignore stale render_check artifacts between checks
  pdf_export_source_lock: PDF outputs reference slides_final/ master PNGs; render_check/pdf_pages/ may contain only disposable pages rendered back from a PDF/PPT for QA, not source images for PDF creation
  no_duplicate_png_output_lock: do not keep duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/; when duplication appears, preserve slides_final/ as master and update manifests/mappings to reference it
  contact_sheet_mastering_lock: keep one retained contact sheet by default, render_check/contact_sheet_review.png, built from slides_final/ master PNGs
  single_contact_sheet_policy: do not retain parallel contact_sheet_generated*, contact_sheet_package*, and contact_sheet_pdf_render* files for the same slide set; if delivery QA requires comparison, create one render_check/contact_sheet_delivery_compare.png or render_check/render_diff_report.json and remove or ignore intermediate contact sheets
  package_delivery: requested outputs only after all generated PNGs pass QA; PPTX and PDF are delivery wrappers from slides_final/ masters
  pptx_delivery: requested PPTX wrapper after all generated PNGs pass QA
  pptx_status: pending_generated_images_and_pre_package_image_review
  pdf_delivery: optional delivery wrapper when requested, built directly from approved slides_final/ PNG masters
  pdf_status: not_requested / pending_generated_images_and_pre_package_image_review / created / blocked
  pptx_title: [filled when creating PPTX deck]
  pdf_title: [filled when creating PDF deck]
  pptx_output_path: [filled after PPTX creation]
  pdf_output_path: [filled after PDF creation]
  pptx_slide_count: [must match generated image count]
  pdf_slide_count: [must match generated image count]
  pptx_packaging_route: scripts/package_slide_images_to_pptx.py / blocked
  pdf_packaging_route: scripts/package_slide_images_to_pdf.py / blocked
  package_image_mapping: [slide_id -> slides_final PNG path -> requested output index]
  pptx_image_mapping: [slide_id -> generated PNG path -> PPTX slide index]
  pdf_image_mapping: [slide_id -> generated PNG path -> PDF page index]
  pptx_speaker_notes_mapping: [slide_id -> note source -> inserted / sidecar / blocked]
  speaker_notes_plan: one substantial note per deck slide, drafted before image generation and inserted into PPTX after image roll-up when the packaging route supports notes
  speaker_notes_status: drafted / inserted / blocked
  speaker_notes_depth_lock: [PPT talk script should be 4-7 substantive Japanese sentences or roughly 180-320 Japanese chars per slide unless the user requests brief notes; include opening framing, 2-3 evidence/assumption talking points, implication, caveat when relevant, and transition; do not invent facts]
  speaker_notes_persuasion_lock: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and may add a justified hook, objection pre-empt, or delivery markers
  speaker_notes_text: [substantial PPT talk script + evidence/assumption cue + source caveat if relevant + transition cue; keep off slide image]
  speaker_notes_landing: [one sentence crystallizing the slide takeaway in a memorable breath, placed before the transition]
  speaker_notes_signpost: [transition that opens a curiosity loop or calls back an earlier slide; keeps the deck reading as one argument]
  notes_hook: [optional one attention-grabbing line; use only on the opener, chapter turns, and turning points]
  notes_objection_preempt: [optional one sentence naming the most likely objection and its answer; use only on contestable-claim slides]
  notes_delivery_markers: [up to two deck-language pause/emphasis/slow cues per note, e.g. 【一拍】【強調】【ゆっくり】 (Japanese) or [beat] [emphasis] [slow] (English)]
  notes_persuasion_arc: [keep consistent with the deck-level notes_persuasion_arc; do not redefine it per slide]
  opening_slide_role: opening_thesis_slide / standard_story_slide
  first_slide_not_title_only: true / N/A
  opening_density_gate: slide 1 has core thesis, 2-4 proof/tension points, visible market-shift/matrix/causal-map/wedge structure, and bridge
  pre_package_image_review: required on actual generated PNG before any PPTX/PDF roll-up or completion
  post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion
  all_generated_images_reviewed: false until every output PNG path has been opened and reviewed
  image_review_iteration: 0 before first review; increment after each regenerated or edited PNG
  image_review_status: pending / approved / repair_required / blocked
  image_review_findings: [blocker/major/minor findings from multimodal self-review]
  revised_prompt_review_status: not_available / approved / repair_required
  image_repair_prompt: [concrete repair prompt if blockers or majors remain]
  image_repair_history: [iteration -> issue -> repair action -> regenerated PNG path -> re-audit result]
  repair_or_regenerate_decision: edit for localized text, source, header, color, spacing, or single-object defects; regenerate when composition, density, tone, reading path, semantic graphic structure, or visual anchor fails
  image_review_matrix: [slide_id -> iteration -> png_path -> blockers -> majors -> repair_prompt -> new_png_path -> status]
  weak_slide_regeneration_queue: [slide_id -> reason -> regenerate_or_edit_action -> new_png_path -> review_status]
  deck_consistency_matrix: [first_third -> middle_third -> last_third -> tone/layout/spacing/source consistency findings]
  final_image_quality_status: pending until every generated PNG has no blockers or majors and deck-level consistency passes
  content_quality_status: pending / approved / repair_required
  design_quality_status: pending / approved / repair_required
  deck_unity_status: pending / approved / repair_required
  completion_ready_status: blocked until all_generated_images_reviewed is true, weak_slide_regeneration_queue is empty, and all image/content/design/deck-unity statuses are approved
  regenerate_until_quality_approved: keep regenerating or editing weak slides until completion_ready_status is approved
  completion_blocker: do not report complete while any generated slide has blocker, major, deck-consistency, content-quality, or design-quality issues
  generation_block_rule: if Codex built-in generation or repair is actually blocked by the image tool, mark completion_ready_status: blocked and do not package or report complete; do not use local environment uncertainty as the blocker
  review_manifest: required JSON record covering every generated PNG before PPTX packaging
  review_manifest_status: approved only when every image path is covered and all quality statuses are approved
  validate_review_manifest: run before PPTX packaging; reject missing, partial, pending, blocked, weak-slide, or duplicate-loose-PNG manifests
  deck_tone_consistency_review: [first third vs middle third vs last third tone comparison after generation]
  deck_tone_consistency_status: pending / approved / repair_required
  deck_tone_repair_plan: [slides to regenerate or edit if tone drift appears]
  post_generation_design_balance_check: required on actual generated PNGs before PPTX/PDF packaging; checks whitespace/occupancy balance, density balance against the planned density tier, typography size/weight balance, color consistency, outer padding consistency, and header integrity
  whitespace_occupancy_balance_status: pending / approved / repair_required
  density_balance_status: pending / approved / repair_required
  typography_balance_status: pending / approved / repair_required
  color_consistency_status: pending / approved / repair_required
  outer_padding_consistency_status: pending / approved / repair_required
  header_identity_lock: header is always the same compact left vertical line + H1 + subtitle system, never a slide-specific decoration surface
  header_integrity_blocker_lock: malformed, missing, oversized, recolored, right-decorated, or intruded header is a blocker and must be repaired before other polish
  header_integrity_status: pending / approved / repair_required
  layout_archetype: {archetype}
  layout_family: full-field / asymmetric-main-supporting-context / balanced-diptych / top-bottom / center-hub / process / matrix / small-multiple / swimlane / staircase
  composition_family: [same family label used for deck-level rhythm review]
  layout_diversity_plan: [deck-level plan for rotating compatible layout families according to message type, evidence type, and decision question]
  layout_rotation_guard: [review neighboring slides for mechanical repetition; repeated families must serve comparison or deliberate rhythm]
  layout_sequence_table: [slide_number -> section_role -> message_type -> layout_family -> composition_family -> previous_family -> repeat_or_change_reason]
  recent_layout_memory: [previous 3-5 slide layout families and why this slide repeats or changes]
  grid_mode: {grid_mode}
  column_spans: [12-column spans, integer columns only]
  row_tracks: [header/body/supporting-context/insight/source alignment baselines; source baseline is not a visible rule]
  column_tracks: [outer shell, main columns, separator, supporting/context columns]
  separator_x: [required when the selected composition uses a visible or structural separator; none when there is no split]
  outer_padding: 1672 basis left/right 44-56px, top/bottom 24-52px; select one exact left/right value and one exact top/bottom value at deck-master time and reuse them verbatim on every slide
  major_regions: [max three]
  coordinate_inventory_1672:
    - object: [major object name]
      x: [px]
      y: [px]
      w: [px]
      h: [px]
  master_components: [header, invisible footer alignment baseline, card/table/insight/icon masters]
  deck_master_refs: [reuse refs for header/footer/insight/table/card if deck-level]
  deck_tone_master_lock: [slide base, typography scale, header/footer, Deep Blue use, Honey use, illustration style, icon family, density rhythm, whitespace/occupancy rhythm, card/table geometry, outer padding, invisible source alignment baseline, negative prompt]; freeze one exact value (not a range) for outer_padding, footer baseline x/y, card radius, and each text-role point size at deck-master time and reuse it verbatim on every slide, exactly as the header master is frozen
  deck_tone_signature_lock: preserve one material system across the deck for base, typography, rules, card/table surfaces, icon stroke, illustration linework, accent budget, density rhythm, Insight treatment, and Source behavior while varying only message-led layouts
  near_white_slide_base_lock: use #FCFBF8 as the default ATOM slide canvas, with optional #F4F3EF only as a barely visible warm light-neutral tint; keep #DDE3EA/#D6E1EE for panels/cards, not the page background; avoid darker cream/beige page bases
  illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system
  illustration_style_sheet: domain-matched flat 2D editorial/vector illustration; choose objects from the brief, audience context, and slide message; optional motifs include people, devices, documents, evidence artifacts, UI panels, operational objects, handoff points, map routes, and small icon badges; keep soft pale blue-gray or warm gray fills, Deep Blue and charcoal linework, restrained Honey highlights, consistent 2-3px stroke, face detail, body proportion, crop, and fill opacity
  illustration_consistency_status: pending / approved / repair_required
  visual_design_quality_traits: [design treatment only: calm light base, compact fixed header, thin structural rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, intentional canvas occupancy, concrete visual anchor, crisp focal hierarchy; do not change slide count, message order, or storyline solely for this]
  imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
  default_2k_generation_lock: 2048x1152 is the standard generated PNG size for working review, final slide image output, PPTX packaging, and PDF packaging
  nonconforming_existing_png_regeneration_lock: if existing/source PNGs are 1672x941 or another non-approved package size, continue by generating new 2048x1152 masters with Codex built-in gpt-image-2 from the same slide specification; do not stop, convert, upscale, HTML-render, API-render, or locally redraw them
  pdf_export_source_lock: PDF export, when requested, references approved slides_final/ PNG masters; render_check/pdf_pages/ is disposable render QA only and not a storage location for final PNGs
  visible_text_only_lock: exact_text is the only source of visible words; lock names, field names, route/status metadata, speaker notes, and audit instructions are non-rendered
  render_contract_lock: image prompt receives drawing-relevant instructions only: canvas, visible text, layout, visual hierarchy, palette, typography, source rendering, and repair scope
  prompt_order_lock: [draw/edit action -> exact visible text -> canvas and style system -> fixed header/source components -> layout and reading path -> main visual/chart/table/illustration details -> optional Insight -> focused blockers]
  positive_quality_lock: desired quality is calm editorial slide design with clear figure-ground separation, exact text, compact fixed header, one dominant structure, grouped evidence, stable line weight, restrained accent area, and a concrete visual anchor
  edit_scope_lock: repair prompt includes issue_observed, change_only, preserve, and re_check; no global restyle unless explicitly required
  revised_prompt_review_lock: revised_prompt_status checked when available; final approval still depends on actual PNG review
  exact_text_fidelity_lock: freeze every visible string before generation; after generation, compare H1, subtitle, labels, numbers, source text, and optional Insight against exact_text and repair missing, invented, garbled, or rewritten copy
  chart_semantic_integrity_lock: charts, tables, matrices, flows, maps, and evidence strips must be structurally meaningful, with legible labels, aligned rows/columns/arrows, plausible relationships, and no fake glyph texture or decorative data marks
  thumbnail_legibility_lock: the slide must preserve the main claim, focal structure, region boundaries, and key numbers when viewed as a slide-sorter thumbnail or contact-sheet tile; repair if it only works at full size
  reading_path_lock: plan a clear reading order from H1 to main visual, evidence/context, optional Insight, and Source; keep one primary focal point and at most two supporting focal points
  concrete_visual_anchor: [the one object, scene, interface, workflow moment, artifact, evidence strip, map detail, or operational motif the reader can picture]
  observable_scene_or_object: [specific visible subject, not an abstract noun]
  viewpoint_crop: [front-on / top-down / close crop / cutaway / over-the-shoulder / operating view / process lane view, chosen from the message]
  specific_visual_details: [2-4 concrete details such as rows, screens, gauges, handoff points, document snippets, machine cells, routes, timestamps, labels, annotations, or evidence artifacts]
  visual_specificity_plan: [how the concrete anchor, chart/table/matrix/flow, and details make the message imaginable]
  editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
  visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide message, evidence, and audience context
  message_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide message before adding supporting elements
  region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette
  composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy; occupancy is observable - no quadrant of the body content area is conspicuously empty and no major region overflows its grid track]
  content_area_priority_lock: allocate height to the body, figure, table, or diagram first; size any optional Insight/message-box from the remaining calculated space so it supports rather than compresses the main content area
  secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
  body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions
  deck_header_master_lock:
    coordinate_basis: 1672x941
    status: exact_required_before_generation
    header_safe_area: [x/y/w/h exact selected values; ATOM default x=44 y=24 w=1584 h=136]
    vertical_line: [x/y/w/h/color exact selected values; ATOM default x=50 y=40 w=10 h=120 color #0B2F5B]
    header_line_top_rule: [accent top must never sit above the first visible H1 glyph/title top; align it to the title top or place it 0-6px below]
    header_left_accent_master_lock: [single header-block left accent copied verbatim on every slide; it spans the H1 + subtitle stack; it is not a page-edge rail, sidebar, body marker, chapter stripe, or slide-specific decoration]
    header_left_accent_reference_lock: [match approved reference geometry on a 1672x941 basis: x=50 y=40 w=10 h=120 color #0B2F5B]
    header_left_accent_shape_lock: [single solid vertical rectangle, 10px wide, 0-2px radius, no pill caps, shadow, glow, gradient, split segments, or duplicate accent]
    header_left_accent_no_protrusion_rule: [the accent top aligns with the H1 glyph/title top or sits 0-6px below it; any upward protrusion above H1 is a blocker]
    header_left_accent_top_protrusion_blocker: [any visible accent pixel above the first visible H1 glyph/title top, clipped/floating near page top, detached from H1/subtitle, or extending into body_start_y is a blocker]
    h1: [x/y/w/max_lines/font_family/font_size/weight/line_height/color exact selected values; ATOM default x=88 y=34 w=1332 max_lines=1 font_family=Noto Sans JP size=32pt weight=700 line_height=1.14 color #2D332E]
    subtitle: [x/y/w/max_lines/font_family/font_size/weight/line_height/color exact selected values; ATOM default x=88 y=82 w=1332 max_lines=1 font_family=Noto Sans JP size=22pt weight=400 line_height=1.18 color #4D544E]
    visual_alignment: [visible accent top aligns with the H1 glyph/title top or sits 0-6px below it; visible accent bottom lands 4-10px below subtitle lower visual edge; no upward protrusion]
    body_start_y: [exact selected value; ATOM default 180, or 218 only if explicit two-line H1 fallback is declared]
    upper_right_clear_zone: [x/y/w/h exact selected values and empty; ATOM default x=1420 y=24 w=208 h=88]
    forbidden_header_elements: [separate ATOM wordmark or brand label, slide number, title kicker, header badge, logo/right object unless the user explicitly provides it as visible exact_text, right-side header decoration, body objects above body_start_y]
  component_inventory: [master components and coordinates]
  equalized_groups: [cards, rows, phase cards, icons]
  shared_edges: [header, main structure, supporting region, insight, source alignment baseline; no visible Source separator]
  hand_placed_exceptions: [max two]
  visual_richness_role: restrained_signature_illustration / diagram_embedded_illustration / data_visual / icon_evidence / quiet_table
  signature_visual_plan: [main motif, supporting motifs, style, and why this slide deserves a memorable but restrained visual]
  illustration_region: [x/y/w/h in 1672 basis, or none for quiet table]
  illustration_intensity: 0_none / 1_marginal / 2_integrated / 3_restrained_signature
  human_designed_illustration_style: clean controlled flat 2D editorial/vector illustration, crisp silhouette, intentional simplification, restrained fills, clear focal motif, only useful supporting details, projection/viewpoint chosen from the slide message, no rough sketch, no arbitrary pseudo-depth, and no glossy AI concept-art finish
  creative_variance: low / medium / high; high acts like the requested higher temperature for composition, crop, viewpoint, and layout rhythm while locking brand/header/text/source rules
  density_tier: T1_sparse / T2_balanced / T3_dense / T4_appendix_dense
  density_layers: [main figure/table, evidence strip, context panel/legend, optional Insight]
  density_design:
    reader_mode: scan / read / reference
    decision_question: [what the reader can answer without narration]
    information_units: [message, context, comparison, trend, mechanism, risk, implication, assumption, source]
    semantic_sentence_layer: [1-3 compact meaningful clauses/sentences in body labels, rows, annotations, or optional Insight that explain relationship, reason, consequence, or decision relevance]
    semantic_copy_gate: [major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names]
    icon_restraint_plan: [which icons are necessary, what they clarify, and which icon candidates were removed because text/structure communicates better]
    icon_density_budget: [default 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise]
    density_levers: [KPI strip, supporting context region, evidence strip, small multiples, annotation, benchmark/context column, benchmark/target/prior-period reference line, source cue]
    overload_controls: [one dominant structure, max three major regions, body >=18pt equivalent, grouped labels, no decorative density]
  impact_clarity_density_gate: [one unmistakable takeaway, one dominant visual structure, one useful evidence layer, simple reading path, clear hierarchy]
  message_sharpness_lock: action title names actor/topic, change/tension, and implication; repair generic labels, vague benefit claims, or slogans before image prompting
  pyramid_logic_lock: state one governing thought, ladder each action title to the question its predecessor raises, and prove each title with a named exhibit element
  governing_thought: [the single sentence the whole deck exists to prove]
  predecessor_question: [N/A for slide 1; for slides 2+, the one-line question the previous slide's action title raises that this slide answers]
  title_exhibit_proof_match: [name the exact exhibit element (bar, delta, slope, cell, row, node) that proves the action title; the title claims nothing the exhibit cannot show]
  mece_support_gate: a slide's supporting points are mutually exclusive and collectively exhaustive, and each slide declares body_logic as inductive or deductive
  body_logic: inductive (parallel MECE reasons) / deductive (premise chain with each premise independently defensible)
  ask_present: [for a decision/recommendation deck, the explicit ask or next step is on the opener or slide 2]
  top_risk_named: [for a decision/recommendation deck, the single most likely objection or dependency is named on the opener or slide 2]
  evidence_compression_ladder: choose the smallest proof structure that makes the message credible: key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation
  chart_emphasis_lock: gray out non-focal data, place the decision-carrying number as a direct on-mark label, and label series directly instead of using a legend
  encoding_consistency_lock: same meaning keeps the same fill/color/shape and scale across the deck, and no distinction relies on hue alone
  number_format_normalization_lock: normalize decimal precision, magnitude abbreviation, axis ticks, and period notation before freezing exact_text
  benchmark_reference_line: none / [one thin labeled target, prior-period, or peer-benchmark line on a level or trend chart]
  density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
  sentence_density_lift_lock: raise density one step with compact meaningful clauses or short sentences in body labels, rows, annotations, and optional Insight; avoid icon-and-keyword-only slides
  semantic_copy_gate: major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names
  icon_restraint_lock: icons are sparse wayfinding or evidence markers, not the primary content layer
  icon_density_budget: default to 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise
  structure_choice_bias: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide
  structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits; add layers only until the body silhouette is filled with deliberate content, then split the slide instead, because overcrowding is not solved with more density
  structure_choice_status: not_applicable / applied / intentionally_skipped / repair_required
  structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
  useful_density_plan: [2-4 proof/context/comparison points, units/denominators where relevant, source cue when traceable, and one clear reading path]
  information_unit_budget: [H1, subtitle, grouped body labels, decision-relevant data labels or rows, optional one-sentence Insight, required source when traceable; no default cap on decision-relevant numbers]
  density_guardrails: [preserve distinct messages, combine only repeated or shared-comparison slides, no smaller body text, no decorative illustration detail]
  header_anchor:
    vertical_line: exact x/y/w/h/color copied from deck_header_master_lock
    header_line_top_rule: copied from deck_header_master_lock and checked after generation
    header_left_accent_master_lock: exact header-block left accent spanning H1 + subtitle; not a page-edge rail, sidebar, body marker, or decoration
    header_left_accent_reference_lock: exact reference geometry x=50 y=40 w=10 h=120 on 1672x941 basis unless a newer embedded master is supplied
    header_left_accent_shape_lock: single solid vertical rectangle, 10px wide, 0-2px radius, no cap/glow/shadow/gradient/split
    header_left_accent_no_protrusion_rule: accent top aligns with H1 glyph/title top or sits 0-6px below it; any upward protrusion above H1 is a blocker
    header_left_accent_top_protrusion_blocker: any visible accent pixel above H1 glyph/title top, page-top floating, clipping, detachment from H1/subtitle, or body intrusion is a blocker; repair x/y/h before any other polish
    h1: exact x/y/w/max_lines/font_family/font_size/weight/line_height/color copied from deck_header_master_lock
    subtitle: exact x/y/w/max_lines/font_family/font_size/weight/line_height/color copied from deck_header_master_lock
    visual_alignment: exact visual alignment rule copied from deck_header_master_lock
    body_start_y: exact selected y copied from deck_header_master_lock
    upper_right_clear_zone: exact x/y/w/h copied from deck_header_master_lock and kept empty
  footer_anchor_baseline: 1672 basis x=44-56 baseline y=895-912, invisible alignment position only, planned even if source_line is none; select one exact x and one exact baseline y at deck-master time and reuse them verbatim
  header_footer_text_color_lock: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E; no Deep Blue/Honey/arbitrary gray in header or footer text
  message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement; many slides should use no message box
  insight_absence_default_lock: start each slide from insight_decision: none; add an Insight/message-box only when it passes insight_justification_required
  insight_justification_required: keep an Insight/message-box only with a clear non-redundant interpretation, decision signal, or reading bridge; remove it if it repeats H1/subtitle/labels or fills empty space
  message_box_scale_lock: compact interpretation surface sized after the main content area; shorter height is welcome when it gives the body, figure, table, or diagram more useful room, while remaining legible; trim text, move detail to body/notes, or remove Insight instead of enlarging the box
  message_box_text_size_lock: message-box/Insight text default 20-24pt, 24-26pt only by exception; always at least 6pt smaller than selected H1, visually below subtitle, and never a second title
  message_box_compactness_blocker_lock: Insight/message-box surfaces that dominate the slide, behave like a banner, or compensate for layout imbalance are blockers
  message_box_text_alignment_lock: center Insight/message-box text optically both horizontally and vertically within its surface; plan line box, padding, and baseline so the sentence sits at the visual center
  insight_surface_placement_lock: when an Insight/message-box is kept, place it as a deliberate interpretation bridge tied to the body silhouette and footer baseline; bottom variants sit in the breathing space between body content and Source, centered to the interpreted region or full body block, with Source kept separate on its invisible baseline
  honey_bottom_bar_lock: Honey is a quiet optional bottom Insight bar treatment, not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
  honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
  honey_justification_required: keep Honey only with a written reason tied to decision clarity; remove decorative or space-filling Honey
  max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
  table_note_microline: none / [one text note line above source text; text only, never drawn as a horizontal rule]
  source_real_only_lock: render Source footer only for real traceable external/provided sources; if no real source exists, set source_line: none and draw no Source footer text
  source_placeholder_blocklist: never use placeholder provenance labels such as brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source text
  source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
  source_separator_lock: Source is text-only; no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline may appear above, below, behind, or adjacent to Source
  source_line: Source: [traceable source names copied from provided or researched sources only] / none only when no traceable source exists
  source_policy: real traceable sources only; no draft, upload, internal-note, or production-route wording
  source_density_rule: Do not drop real source names to reduce visual density; shorten or group source names instead.
  brand_accent_usage_budget: restrained visual area; for ATOM work, Deep Blue uses standard 4-8%, may reach 10% on dense table slides, and may reach 12% only for rare chapter/closing slides; it never appears as body text
  deep_blue_usage_lock: exact #0B2F5B structural use; one active body blue system; no blue H1/subtitle/body/footer text; no extra blue hues
  brand_accent_system_role: left header accent / rule / icon / number / badge / matrix highlight / none, adjusted to the embedded ATOM design system; never a separate visible ATOM label in the header
  visible_brand_label_blocker: do not render ATOM, a logo, or any brand word as a separate header label unless it is explicitly listed in exact_text as the H1 or body copy
  visual_asset_judgment: use illustration/icons only if they improve understanding, memory, comparison, or navigation; no quota and no filler
  visual_asset_role: integrated_line_illustration / margin_vignette / icon_evidence_strip / diagram_embedded_icons / process_icons / data_icon_markers / none
  icon_system_plan: none / [role, style, stroke, color logic, grouping, why it helps]
  illustration_presence: none / marginal / integrated / restrained_signature
  insight_decision:
    insight_absence_default_lock: start from keep_remove: remove / variant: none
    insight_justification_required: keep only when the slide loses non-redundant interpretation, decision signal, or reading bridge without it
    honey_selective_signal_lock: Honey starts absent and is considered only for a justified bottom decision signal
    honey_justification_required: if Honey is selected, explain why a quiet Honey bar improves decision clarity more than none or a neutral outline
    keep_remove: [keep/remove]
    reason: [interpretation or decision need]
    variant: none / bottom-main / top-thesis / side-context-wide / side-context-tall / inline-pill / outlined thesis / outlined bottom / accent surface / dark accent surface / Honey bottom bar when ATOM
    deck_count_check: [single slide or deck-level count]
    geometry: [x/y/w/h in 1672 basis if kept; choose the smallest legible width tied to the interpreted region, not full-canvas width by default]
    height: [calculated after body and footer rhythm; use the lowest comfortable height when it helps the main content area; bottom Insight bars target 72-96px on the 1672 basis, with 108px only for a necessary two-line sentence]
    radius: 8px or 12px; select one deck radius at deck-master time and reuse it on every card
    padding: [balanced px; enough for centered text but not a tall band]
    honey_bar_style: [N/A unless Honey bottom bar is selected; then use #FBF3D7 very pale Honey fill, #C49A2C thin 2-3px outline, optional left icon well with a small 20-24px icon on the 1672 basis, one #C49A2C vertical separator, #2D332E text, and no dashed border]
    left_accent: [Honey bottom bars use a thin separator after the optional icon well, not a full-height far-left stripe; Deep Blue uses embedded ATOM design system accent line spec only outside Honey]
    background: [flat solid fill color only; Honey message box uses #FBF3D7; no pattern, texture, gradient, motif, dashed outline, or internal illustration]
    text_alignment: [optically centered horizontally and vertically within the surface]
    placement_relation: [inside the 12-column grid; tied to the interpreted body region; bottom variants bridge body content and Source without touching either]
    text: [one judgment sentence if kept]
  human_crafted_feel: priority, breathing room, editorial rhythm
  qa_risks: [overcrowding, weak hierarchy, source uncertainty, decorative accent surface, unresolved grid]
  blocking_unresolved_items: {unresolved_text}"""


def mode_guidance(mode: str) -> str:
    if mode == "text-structure":
        return """mode_guidance:
  - Convert the long text into a slide-image deck structure before writing image prompts.
  - Use the embedded ATOM design system in SKILL.md; do not load an external ATOM pattern file.
  - Define deck_thesis, audience_decision, storyline_frame, section_map, and slide-level action_title messages.
  - Plan slide 1 as opening_thesis_slide, not a title-only opener: include the core thesis, 2-4 proof/tension points, a real visual structure, and a narrative bridge.
  - Map every message to evidence, source_policy, visual_structure, layout_archetype, grid_mode, exact_text_budget, and split_merge_decision.
  - Apply message_sharpness_lock: rewrite each action title until it names actor/topic, change/tension, and implication; reject generic labels, vague positive claims, and slogans.
  - Apply pyramid_logic_lock: state one governing thought, run governing_thought_gate, build a vertical_logic_chain so each title answers the question its predecessor raises, and confirm title_exhibit_proof_match for every slide.
  - Apply mece_support_gate: run mece_check on multi-point slides and declare body_logic as inductive or deductive; for decision/recommendation decks confirm ask_present and top_risk_named on the opener or slide 2.
  - Apply chart_emphasis_lock, encoding_consistency_lock, and number_format_normalization_lock on chart/table/matrix slides before freezing exact_text.
  - Apply speaker_notes_persuasion_lock: stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, record notes_persuasion_arc, and add a justified notes_hook, notes_objection_preempt, or delivery markers only where they help.
  - Apply source_real_only_lock and source_line_lock: render Source: ... only for real traceable external/provided sources; use source_line: none and draw no Source footer when no real source exists.
  - Apply output_artifact_mastering_lock, single_final_png_master_lock, and no_duplicate_png_output_lock: use slides_final/ as the single loose-PNG master; slides_package/ stores PPTX/notes/manifest only; render_check/pdf_pages/ is disposable QA output only.
  - Apply contact_sheet_mastering_lock and single_contact_sheet_policy: keep one retained contact sheet from slides_final/ by default; generate a comparison contact sheet only when delivery/render QA needs it.
  - Build layout_diversity_plan: assign layout_family for each slide across full-field, asymmetric main/supporting-context, balanced comparison, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families when the argument benefits.
  - Use layout_rotation_guard to keep repeated structures purposeful: repeat a family for like-for-like comparison, and change family when message type, evidence type, or decision question changes.
  - Draft speaker_notes_text for every slide with speaker_notes_depth_lock: substantial Japanese PPT talk script, 4-7 sentences or roughly 180-320 Japanese chars, with framing, evidence/assumption cues, implication, caveat if relevant, and transition.
  - Add pre_package_image_review, post_generation_full_deck_review_loop, all_generated_images_reviewed, weak_slide_regeneration_queue, content_quality_status, design_quality_status, deck_unity_status, completion_ready_status, and regenerate_until_quality_approved fields so generated PNGs are reviewed, repaired, and re-reviewed before PPTX, or completion.
  - Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide before image prompting.
  - Apply illustration_tone_lock and illustration_style_sheet before image prompting so people, devices, UI panels, document objects, icon badges, linework, fills, and crop stay consistent across the deck.
  - Run impact_clarity_density_gate before image prompting: every slide needs one unmistakable takeaway, one dominant visual structure, a useful evidence layer, and a simple reading path; repair slides that feel flat, vague, thin, or cluttered.
  - Run density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
  - Apply evidence_compression_ladder: choose the smallest proof structure that makes the message credible before adding prose or decorative detail.
  - Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting.
  - Apply structure_choice_bias and structured_density_bias as a gentle direction: use issue trees, driver trees, 2x2 matrices, value chains, waterfalls, KPI bridges, decision tables, or hypothesis-evidence-implication rows when they clarify the message; intentionally skip them when a simpler visual is stronger.
  - Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  - Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  - Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  - Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  - Apply visual_subject_open_set, message_led_composition_lock, region_balance_policy, composition_fit_plan, secondary_region_integrity_lock, and body_silhouette_lock so the visual subject, region balance, focal relationship, canvas occupancy, secondary region, and body outline are chosen from the argument before image prompting.
  - Add useful density through comparison, benchmarks, denominators, assumptions, annotations, evidence strips, supporting context regions, small multiples, and source cues; do not add density through smaller type or decorative illustration detail.
  - Preserve distinct messages as separate slides; combine only repeated messages or evidence that must be compared in one view.
  - Define deck_header_master_lock with exact x/y/w/h/color/font values, then repeat it verbatim in every slide prompt.
  - Read only the action titles in order; repair gaps before image generation.
  - Do not generate final images until every selected slide has a canonical planning block."""
    if mode == "deck-plan":
        return """mode_guidance:
  - Define deck thesis and one primary message per slide.
  - Apply message_sharpness_lock: each slide message should name actor/topic, change/tension, and implication; repair section-label or slogan-like messages before prompt writing.
  - Apply pyramid_logic_lock and mece_support_gate: state one governing thought, ladder each title to the question its predecessor raises, prove each title with a named exhibit element, keep within-slide supporting points MECE, and declare body_logic as inductive or deductive.
  - Apply chart_emphasis_lock, encoding_consistency_lock, and number_format_normalization_lock on chart/table/matrix slides.
  - Apply speaker_notes_persuasion_lock: stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and record notes_persuasion_arc.
  - Use the embedded ATOM design system in SKILL.md; do not load an external ATOM pattern file.
  - Apply builtin_generation_lock: invoke Codex built-in image generation directly for gpt-image-2 slide PNGs, without local environment preflight or local artifact-route probing before generation.
  - Apply image_generation_tool_lock and script_boundary_lock: prompt/package scripts may plan, validate, or wrap approved artifacts, but final PNG pixels must come from Codex built-in image generation, never from scripts, screenshots, local renderers, or presentation exports.
  - Apply credential_setup_blocker: do not create, request, decrypt, configure, inspect, or wait for account credentials, local tokens, SDK setup, or environment variables; start Codex built-in image generation instead.
  - Apply progress_update_route_lock: do not tell the user that local credentials, environment variables, SDK setup, save-route probing, or alternate account/setup routes are being checked before generation; describe the next step as slide structuring and Codex built-in image generation.
  - Apply pptx_first_blocker: do not create a presentation deck as the source of truth before image generation; generate and review slide PNGs first, then package approved PNGs into PPTX at the end.
  - Start with opening_thesis_slide rather than a title-only first slide: the opener should make the main phrase memorable while also showing the thesis, tension/proof points, structure, and bridge.
  - Select layout_archetype and grid_mode for every slide.
  - Apply source_real_only_lock and source_line_lock: render Source: ... only for real traceable external/provided sources; use source_line: none and draw no Source footer when no real source exists.
  - Apply output_artifact_mastering_lock, single_final_png_master_lock, and no_duplicate_png_output_lock: use slides_final/ as the single loose-PNG master; slides_package/ stores PPTX/notes/manifest only; render_check/pdf_pages/ is disposable QA output only.
  - Apply contact_sheet_mastering_lock and single_contact_sheet_policy: keep one retained contact sheet from slides_final/ by default; generate a comparison contact sheet only when delivery/render QA needs it.
  - Create layout_diversity_plan and layout_rotation_guard before final prompts so the deck can use the expanded pattern catalogue without drifting from ATOM brand and header rules.
  - Define deck_header_master_lock before any slide-level prompt. Do not leave header coordinates as ranges.
  - Apply header_identity_lock, header_integrity_blocker_lock, deck_tone_signature_lock, illustration_tone_lock, illustration_style_sheet, and message_box_compactness_blocker_lock before slide-level variation.
  - Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide; use the same flat 2D editorial workflow illustration style on chapter openers, turning points, complex systems, and final vision slides.
  - Run impact_clarity_density_gate: every slide needs one unmistakable takeaway, one dominant visual structure, a useful evidence layer, and a simple reading path; repair low-impact, hard-to-understand, empty, or cluttered slides before image prompting.
  - Assign density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
  - Apply evidence_compression_ladder: compress proof into a key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation before adding prose.
  - Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting.
  - Apply structure_choice_bias and structured_density_bias as a gentle direction: use issue trees, driver trees, 2x2 matrices, value chains, waterfalls, KPI bridges, decision tables, or hypothesis-evidence-implication rows when they clarify the message; intentionally skip them when a simpler visual is stronger.
  - Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  - Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  - Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  - Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  - Apply visual_subject_open_set, message_led_composition_lock, region_balance_policy, composition_fit_plan, secondary_region_integrity_lock, and body_silhouette_lock so the visual subject, region balance, focal relationship, canvas occupancy, secondary region, and body outline are chosen from the argument before image prompting.
  - Preserve distinct messages as separate slides; combine only repeated messages or evidence that must be compared in one view.
  - Define deck master refs for header, invisible footer alignment baseline, Insight surfaces, tables, cards, and icon circles.
  - Allocate Insight components selectively across the deck and avoid mechanical card-only repetition; apply message_box_compactness_blocker_lock so oversized banner-like Insight surfaces are repaired before generation.
  - Draft speaker_notes_text for every slide with speaker_notes_depth_lock and plan PPTX/PDF roll-up with one full-bleed generated PNG plus corresponding substantial speaker notes per slide.
  - Plan post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion, classify blocker/major/minor issues, fill weak_slide_regeneration_queue, repair/regenerate, and continue until all_generated_images_reviewed is true, the queue is empty, and completion_ready_status is approved.
  - Apply completion_blocker: do not report complete while any generated slide has blocker, major, deck-consistency, content-quality, or design-quality issues.
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
  - Include pre_package_image_review, post_generation_full_deck_review_loop, all_generated_images_reviewed, weak_slide_regeneration_queue, content_quality_status, design_quality_status, deck_unity_status, completion_ready_status, regenerate_until_quality_approved, and repair_iteration_plan; do not treat first generation as final without inspecting the actual PNG.
  - Apply completion_blocker: do not report complete while any generated slide has blocker, major, deck-consistency, content-quality, or design-quality issues.
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
model_route_assumption: Codex built-in image generation is the gpt-image-2 route for this skill unless image metadata proves otherwise
generation_route: Codex built-in image generation
builtin_generation_lock: invoke Codex built-in image generation directly; do not pause for local environment preflight or local artifact-route probing before generation
credential_setup_blocker: do not create, request, decrypt, configure, inspect, or wait for account credentials, local tokens, SDK setup, or environment variables; use Codex built-in image generation directly
progress_update_route_lock: do not narrate local credentials, environment variables, SDK setup, save-route probing, or alternate account/setup routes as prerequisites; progress should move from slide structuring to Codex built-in image generation
image_generation_tool_lock: final slide PNG pixels must be produced by Codex built-in image generation, not by repo scripts, local renderers, screenshots, or presentation exports
script_boundary_lock: prompt builder scripts are planning helpers only; package scripts run only after approved Codex image artifacts exist and must never render, draw, screenshot, export, simulate, or replace final slide PNGs
prompt_readiness: draft_scaffold_until_blocking_unresolved_items_none

final_generation_prompt_payload:
{prompt_lead}
  canvas_and_style: use the embedded ATOM design system, 1672x941 layout basis, 2048x1152 generated output, near-white slide base, fixed compact header, Noto Sans JP, and ATOM palette; ATOM is style metadata, not a visible header wordmark unless exact_text explicitly asks for it.
  exact_visible_text: render only the strings listed under exact_text; no lock names, field names, file paths, audit labels, route/status fields, manifests, or speaker notes.
  layout_and_reading_path: use selected layout_family, 12-column grid, fixed header/source anchors, one primary focal point, and a clear path from H1 to main structure to evidence/context to optional Insight to Source.
  visual_structure: choose the message-led chart, table, matrix, map, flow, evidence strip, or domain-matched editorial illustration that makes the argument observable.
  source_rendering: render Source only when source_line contains real traceable sources; if source_line is none, leave the footer source area blank and draw no separator.
  focused_blockers: wrong image size, missing/malformed header, invented/garbled text, invented Source, Source separator line, broken chart semantics, unreadable body text, visible workflow metadata, or out-of-scope repair.

non_rendered_workflow_qa:
  Use the fields below only for planning, review, packaging, and QA. Do not include them as visible slide content or in the final image prompt payload.

draft_image_prompt_scaffold:
  Distill the final image prompt from final_generation_prompt_payload; keep non_rendered_workflow_qa, PPTX packaging, manifests, credential blockers, contact sheets, and audit statuses outside the image prompt payload.
  Use the embedded ATOM design system in SKILL.md. Do not load an external ATOM pattern file.
  Apply prompt_order_lock: keep the final generation prompt ordered as draw/edit action, exact visible text, canvas and style system, fixed header/source components, layout and reading path, main visual/chart/table/illustration details, optional Insight, then focused blockers.
  Apply render_contract_lock: pass drawing-relevant instructions to image generation; keep PPTX packaging, file paths, manifests, credentials, contact sheets, speaker notes, and audit/status fields outside visible slide content.
  Apply visible_text_only_lock: render only exact_text strings on the slide; do not render lock names, YAML keys, route/status fields, audit labels, speaker notes, file paths, or workflow instructions.
  Apply positive_quality_lock: state the desired calm editorial slide quality before blockers: clear figure-ground separation, exact text, compact fixed header, one dominant structure, grouped evidence, stable line weight, restrained accent area, and a concrete visual anchor.
  PPTX is a delivery wrapper only. Never create final PNGs by exporting, rendering, or screenshotting a PPTX.
  Prompt builder scripts are planning helpers only; they must never render, draw, screenshot, export, or simulate final slide PNGs.
  Package scripts run only after approved Codex built-in image artifacts exist, and package scripts must not be used as a workaround for missing image generation.
  Apply pptx_first_blocker: do not create a presentation deck as the source of truth before image generation; generate and review slide PNGs first, then package approved PNGs into PPTX at the end.
  Correct order: generate gpt-image-2 PNGs, review and repair PNGs, then package approved PNGs into requested PPTX/PDF outputs.
  Only mark image generation blocked after invoking Codex built-in image generation and the image tool itself fails, is unavailable, or refuses the request. Local environment uncertainty is not a blocker.
  Apply progress_update_route_lock: never present local credential, environment, SDK, save-route, or alternate setup checks as parallel prerequisites before built-in image generation.
  Apply output_artifact_mastering_lock: write approved generated PNGs once under slides_final/ and treat that path as the sole loose-PNG master.
  Apply single_final_png_master_lock: review_manifest, package_image_mapping, pptx_image_mapping, pdf_image_mapping must reference the slides_final/ master path rather than copied PNGs.
  Apply slides_package_policy: slides_package/ contains PPTX, speaker notes, review_manifest, and metadata only; do not copy final PNG files into slides_package/.
  Apply render_check_policy: render_check/pdf_pages/ is optional disposable QA output from rendered PDF/PPT checks only, not another copy of final PNGs.
  Apply pdf_export_source_lock: create PDFs from slides_final/ master PNGs and keep render_check/pdf_pages/ limited to disposable rendered-back QA pages.
  Apply no_duplicate_png_output_lock: do not keep duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/.
  Apply contact_sheet_mastering_lock: keep one retained contact sheet by default, render_check/contact_sheet_review.png, built from slides_final/ master PNGs.
  Apply single_contact_sheet_policy: do not retain parallel contact_sheet_generated*, contact_sheet_package*, and contact_sheet_pdf_render* files for the same slide set; if package/PDF render QA needs comparison, create one contact_sheet_delivery_compare.png or render_diff_report.json instead.

  Plan coordinates on a 1672x941 basis, but generate approved PNG masters only at 2048x1152.
  Apply default_2k_generation_lock: use 2048x1152 as the generated slide output size for review, final PNGs, PPTX packaging, and PDF packaging; do not create separate 1920x1080 or other 16:9 delivery masters.
  Apply nonconforming_existing_png_regeneration_lock: when existing/source PNGs are 1672x941 or another non-approved package size, do not treat package-script rejection as final blockage and do not convert, upscale, HTML-render, API-render, or locally redraw them. Reuse the approved slide specification and generate new 2048x1152 slides_final/ masters with Codex built-in gpt-image-2, then review and package those generated masters.
  Apply pdf_export_source_lock: build PDF outputs from approved slides_final/ master PNGs; never duplicate final PNG masters into render_check/pdf_pages/ for PDF creation.
  Use size terminology consistently: 1672x941 is layout-coordinate basis only, and 2048x1152 is the single 16:9 2K-width generated PNG master size for delivery wrappers.
  Use a 12-column grid, 8px spacing rhythm, precise shared edges, and fixed header/footer anchors.
  Define deck_tone_master_lock and deck_tone_signature_lock before slide-level prompting and preserve them through the whole deck: slide base, typography scale, header/footer, Deep Blue role, Honey treatment, illustration style, icon family, density rhythm, whitespace/occupancy rhythm, card/table geometry, outer padding, invisible source alignment baseline, and negative prompt. Later slides must feel like the same deck as the first approved pilot slides.
  Apply illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system.
  Define illustration_style_sheet before generation and reuse it verbatim across the deck: domain-matched flat 2D editorial/vector illustration; choose objects from the brief, audience context, and slide message; optional examples include simplified people, devices, documents, evidence artifacts, UI panels, operational objects, handoff points, map routes, and small icon badge objects; soft pale blue-gray or warm gray fills; Deep Blue and charcoal linework; restrained Honey highlights; consistent 2-3px stroke, crop, shadow softness, and fill opacity.
  Apply visual_design_quality_traits as design treatment: calm light base, compact fixed header, thin structural rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, concrete visual anchor, crisp focal hierarchy, and deliberate canvas occupancy. Do not alter slide count, message order, or storyline solely for visual style.
  Apply imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
  Apply revised_prompt_review_lock: when Codex/image generation exposes a revised_prompt or rewritten prompt, verify it preserved exact_text, source behavior, header master, and visible/non-visible boundaries before approving the PNG; if no revised prompt is exposed, continue with actual PNG review.
  Apply exact_text_fidelity_lock: freeze H1, subtitle, labels, numbers, source text, and optional Insight as quoted exact_text before generation; after generation, compare the actual visible text to exact_text and repair any missing, invented, garbled, duplicated, or rewritten copy.
  Apply chart_semantic_integrity_lock: charts, tables, matrices, flows, maps, and evidence strips must read as real argument structures, not decorative texture; keep rows, columns, arrows, axes, legends, units, and comparisons aligned, labeled, and plausibly connected.
  Apply thumbnail_legibility_lock: design for both full-size review and slide-sorter/contact-sheet review; the main claim, focal structure, region boundaries, and key numbers should remain understandable at reduced scale without adding oversized hero typography.
  Apply reading_path_lock: make the visual path traceable from H1 to main visual, evidence/context, optional Insight, and Source; keep one primary focal point and at most two supporting focal points.
  Apply editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
  Apply visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide message, evidence, and audience context.
  Apply message_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide message before adding supporting elements.
  Apply region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette.
  Apply composition_fit_plan: set the main visual field, supporting regions, whitespace role, and Insight footprint before generation so the canvas has deliberate occupancy and breathing room. Occupancy is observable: no quadrant of the body content area should be conspicuously empty and no major region should overflow its grid track.
  Apply content_area_priority_lock: allocate height to the body, figure, table, or diagram first, then size any optional Insight/message-box from the remaining calculated space so it supports rather than compresses the main content area.
  Apply secondary_region_integrity_lock: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field.
  Apply body_silhouette_lock: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions.
  Apply layout_diversity_plan at deck level: choose layout families from full-field, asymmetric main/supporting-context, balanced diptych, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase patterns according to the slide message. Use layout_rotation_guard so neighboring slides do not fall into the same composition by habit; repeated families should make comparison easier.
  Apply credential_setup_blocker: do not create, request, decrypt, configure, inspect, or wait for account credentials, local tokens, SDK setup, or environment variables. The next action after an image-ready prompt is Codex built-in image generation.
  Apply codex_image_artifact_rule before generation: call Codex built-in image generation for each final slide prompt, treat the returned image as the generated PNG artifact, and materialize approved artifacts into slides_final/ through the Codex-provided artifact/download/attachment path before PPTX packaging. Do not inspect or mention local environment setup as a reason to stop.
  Apply header_identity_lock: the header is always the same compact left vertical line + H1 + subtitle system, never a slide-specific decoration surface.
  Apply header_left_accent_master_lock: the left accent is a fixed header-block anchor tied to the H1/subtitle stack and copied verbatim on every slide; it is not a page-edge rail, tall sidebar, body marker, chapter stripe, or slide-specific ornament.
  Apply header_left_accent_reference_lock: match the approved reference geometry on a 1672x941 basis unless a newer embedded master is explicitly supplied: x=50 y=40 w=10 h=120, color #0B2F5B.
  Apply header_left_accent_shape_lock: draw one solid vertical rectangle only, 10px wide, with square or 0-2px radius ends and no pill caps, shadow, glow, gradient, split segments, duplicate marks, or decorative extension.
  Apply header_left_accent_no_protrusion_rule: the accent top must align with the first visible H1 glyph/title top or sit 0-6px below it; any upward protrusion above H1 is a blocker because the accent should start with the title, not above it.
  Apply header_left_accent_top_protrusion_blocker: if any visible accent pixel sits above the first visible H1 glyph/title top, floats near the page top, clips outside the header safe area, detaches from the H1/subtitle stack, or enters body_start_y, mark the slide repair_required and fix the accent x/y/h before any other polish.
  Define and preserve one deck_header_master_lock with exact selected values, not ranges: coordinate_basis, header_safe_area, vertical_line x/y/w/h/color, header_line_top_rule, header_left_accent_master_lock, header_left_accent_reference_lock, header_left_accent_no_protrusion_rule, H1 x/y/w/max_lines/font_size/weight/line_height/color, subtitle x/y/w/max_lines/font_size/weight/line_height/color, visual_alignment, body_start_y, and upper_right_clear_zone. Repeat it verbatim across the deck. Treat the header as the lowest-freedom component; no_header_ranges_in_final_prompts.
  Include coordinate_inventory_1672 and reuse master_components before generating repeated objects.
  Use Noto Sans JP for every visible text string, including Latin/English letters, numbers, symbols, and Japanese. Do not mix in any other typeface; if exact font rendering is unavailable in image generation, use the closest Noto Sans JP-like rendering without changing the font family intent.
  Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
  Apply near_white_slide_base_lock: use #FCFBF8 as the default ATOM slide canvas, optionally #F4F3EF as only a barely visible warm light-neutral tint; the page should read closer to white than beige. Keep #DDE3EA/#D6E1EE for panels/cards only, not the full slide background.
  For ATOM work, use #FCFBF8 primary slide base and optional #F4F3EF subtle warm light-neutral tint, #2D332E text, #4D544E subtitle, #6E756E footer/source/table-note text, and #0B2F5B Deep Blue structure. Avoid darker cream/beige page backgrounds; #DDE3EA/#D6E1EE are reserved for panels/cards, not the full slide canvas.
  H1 30-34pt weight 700 #2D332E, subtitle 21-23pt weight 400 #4D544E, body 18pt equivalent. Use the exact compact ATOM header: 1672 basis header_safe_area x=44 y=24 w=1584 h=136; vertical_line x=50 y=40 w=10 h=120 #0B2F5B; header_line_top_rule accent top must not sit above the first visible H1 glyph/title top and should align with it or sit 0-6px below it; H1 x=88 y=34 w=1332 max_lines=1 size=32pt weight=700 line_height=1.14 #2D332E; subtitle x=88 y=82 w=1332 max_lines=1 size=22pt weight=400 line_height=1.18 #4D544E; visual_alignment accent spans the H1 + subtitle block with no upward protrusion and bottom 4-10px below subtitle lower visual edge; body_start_y=180; upper_right_clear_zone x=1420 y=24 w=208 h=88 empty. Two-line H1 fallback: vertical_line y=40 with h recalculated to end 6-10px below subtitle lower visual edge, subtitle y=118, body_start_y=218. No separate ATOM wordmark, logo, kicker, or badge. No Deep Blue H1. No right-side header decoration or body object in the header safe area.
  Lock header and footer text colors as one Ink-family hierarchy: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E. Do not use Deep Blue, Honey, yellow, or arbitrary gray for header/footer text.
  Apply header_integrity_blocker_lock: malformed, missing, oversized, recolored, right-decorated, or intruded headers are blockers; repair header identity before any other visual polish.
  Let structure, numbers, rules, spacing, and typography carry the hierarchy.
  Use small Lucide-style line icons as quiet wayfinding only when they clarify reading order, evidence, or interaction.
  Include visual_richness_role, illustration_intensity, creative_variance, and density_tier in the prompt. Use flat 2D human-designed editorial/vector workflow illustrations and purpose-built motifs where they add memory, scanning help, or navigation.
  For deck openers, apply opening_density_gate: first slide role is opening_thesis_slide, first_slide_not_title_only is true, and the slide includes a core thesis, 2-4 proof/tension points, one visible market-shift/matrix/causal-map/wedge structure, and a bridge to the next section.
  Include density_design in the prompt. Density should answer the reader's decision_question through grouped information units, comparison baselines, evidence strips, supporting context regions, small multiples, annotations, units, assumptions, and source cues. Do not solve density with smaller body text, extra decorative cards, or illustration detail.
  Apply density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting. Prefer adding decision-relevant comparison, benchmark, denominator, unit, assumption, source cue, or annotation before adding decorative space.
  Apply sentence_density_lift_lock: body labels, card rows, chart/table annotations, and optional Insight should include compact meaningful clauses or short sentences that explain relationship, reason, consequence, or decision relevance. A slide made mostly of icons plus one-word labels is under-dense and must be repaired before generation.
  Apply semantic_copy_gate before freezing exact_text: rewrite noun-only body labels into compact meaning-bearing copy, typically label + change/reason/implication. Noun-only text is acceptable only for table headers, axes, legends, or category names; card grids with only nouns are repair_required.
  Apply icon_restraint_lock: icons are quiet wayfinding or evidence markers only. Reduce icon count when icons repeat generic ideas, compete with the main structure, or replace explanatory text; prefer a short sentence, mini table, causal chain, labeled diagram, or data row when that carries meaning better.
  Apply icon_density_budget: default to 0-3 purposeful icons per slide, avoid one icon per card/row as a habit, and keep icon count below semantic text units unless the visual logic explicitly needs more.
  Apply structure_choice_bias: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide. Good candidates include issue tree, driver tree, 2x2 matrix, value chain, funnel, waterfall, KPI bridge, decision table, before/after bridge, and hypothesis-evidence-implication rows.
  Apply structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits; keep hierarchy readable and intentionally skip the added structure when it would dilute the focal message. Add layers only until the body silhouette is filled with deliberate content; past that, split the slide rather than overcrowd it.
  Apply structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
  Apply chart_emphasis_lock: render non-focal series, bars, rows, and nodes in one quiet neutral gray so the accent color marks only the element the action title is about; place the decision-carrying number as a bold direct label on the exact mark it describes with a short verdict clause; label series directly at the line end, bar, or segment, and use a separate legend only when 5+ series force it.
  Apply encoding_consistency_lock: reuse one deck-level encoding legend so each scenario (actual/plan/forecast), variance sign, and category keeps one fixed fill, color, and shape on every slide, and any repeated unit uses one consistent non-truncated scale; pair every color-encoded distinction with a label, shape, fill pattern, or position cue so it survives grayscale and thumbnail review. The chart_emphasis_lock focal layer (accent on the focal element, neutral gray on non-focal data) is a separate emphasis layer that overrides category hue on a slide where the category is non-focal; muting a non-focal category is not an encoding_consistency_lock violation.
  Apply number_format_normalization_lock: before freezing exact_text, give each metric one decimal-precision rule, one magnitude-abbreviation style, rounded axis ticks, and explicit period notation so the same metric formats identically across the deck.
  When a chart shows a level or trend, add one thin labeled reference line (target, prior period, or peer benchmark) so the value reads as above or below a meaningful bar rather than in isolation.
  Apply pyramid_logic_lock and mece_support_gate as planning checks before prompting: the deck has one governing thought, each action title answers the question its predecessor raises and is proven by a named exhibit element, and within-slide supporting points are MECE with a declared inductive or deductive body_logic.
  When creative_variance is high, vary composition, viewpoint, crop, asymmetric region balance, visual metaphor, and layout rhythm; keep brand, header, exact text, grid, and source policy locked.
  Let the planned chart/table/matrix/roadmap carry the argument where it is the clearest reader path; illustration adds memory, wayfinding, and selective emphasis through a clear focal motif, useful supporting details, clean controlled linework, crisp silhouettes, restrained fills, rounded UI panels, small icon badges, and short annotations.
  Make abstract messages imageable by naming the concrete visual anchor and visible details: an operating view, workflow handoff, document stack, data row, map route, queue, machine cell, screen state, evidence artifact, or customer moment that fits the message.
  Apply speaker_notes_depth_lock: for PPTX decks, write speaker notes as a substantial Japanese talk script, normally 4-7 sentences or roughly 180-320 Japanese characters per slide unless the user requests brief notes. Include opening framing, 2-3 evidence or assumption talking points, the implication to say aloud, caveat/source context when relevant, and a transition to the next slide.
  Apply speaker_notes_persuasion_lock: order each note as framing/tension, evidence cues, implication, landing sentence, then signpost transition. The framing should stage the gap between the current state and the intended future; balance evidence (logos) with selective ethos and, on 2-4 pivotal slides, one pathos beat naming a concrete human or operational consequence; end with a landing sentence that crystallizes the takeaway in one memorable breath, then a signpost transition that opens a curiosity loop or calls back an earlier slide. Use at most one rhetorical device per note, and translate one key statistic into a concrete imageable sentence on pivotal evidence slides. Add notes_hook only on the opener, chapter turns, and turning points; add notes_objection_preempt only on contestable-claim slides; add up to two deck-language delivery markers per note. Keep every note consistent with notes_persuasion_arc and bound by the no-unsupported-facts and no-invented-sources rules.
  Keep speaker notes out of the slide image. Speaker notes are inserted later into PPTXs and should not appear as visible on-slide text.
  Do not hard-code one visual grammar across slides. Select the projection, viewpoint, abstraction level, motif, and level of detail from the slide message; use depth or spatial perspective only when it carries meaning. Do not use decorative trapezoid planes, fake perspective floors, isometric boxes, tilted architectural slabs, vanishing points, or pseudo-3D depth as a shortcut for freshness.
  Keep visual subject selection open and message-led; use the subject that makes the argument most observable through scale, interaction, place, evidence, or operating context.
  Create freshness through viewpoint, asymmetric composition, designed margin vignettes, evidence strips, partial cutaways, and magnified details, not decoration or glossy concept art.
  Use Deep Blue structurally with a 4-8% visual area budget, up to 12% only for strong closing slides, and never for body text.
  Apply insight_absence_default_lock and insight_justification_required: start from no Insight/message-box; keep one only when the slide loses non-redundant interpretation, decision signal, or reading bridge without it.
  Use Honey only for ATOM or compatible guidelines where it is a justified bottom decision signal: #FBF3D7 very pale Honey fill, #C49A2C thin 2-3px outline, optional left icon well with a small 20-24px icon on the 1672 basis, one #C49A2C vertical separator, #2D332E text, one component maximum. Apply honey_selective_signal_lock and honey_justification_required: Honey starts absent, is never the default message-box color, and must be removed if it is decorative, redundant, space-filling, or stronger than the body content.
  Use flat solid fills for all message boxes and Insight surfaces; do not add patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations inside the box.
  Apply message_box_scale_lock: message boxes are compact interpretation surfaces sized after the main content area, not display surfaces. A lower, quieter height is welcome when it gives the body, figure, table, or diagram more useful room while the sentence remains legible and optically centered. For bottom Insight bars, target 72-96px height on the 1672 basis and allow up to 108px only for a necessary two-line sentence. Keep copy to one short judgment sentence, prefer one line, max two lines, and do not enlarge the surface to rescue long prose.
  Apply message_box_text_size_lock: message-box/Insight text defaults to 20-24pt, uses 24-26pt only by exception, stays at least 6pt smaller than the selected H1, remains visually below the subtitle, and never becomes a second title or second hero headline.
  Apply message_box_compactness_blocker_lock: an Insight/message-box that dominates the slide, becomes a banner, spans more than the interpreted region needs, grows tall to carry prose, or compensates for layout imbalance is a blocker. Prefer a lower, quieter box that returns space to the body, figure, table, or diagram; repair by shortening the sentence, narrowing the surface, moving detail into the body/notes, or removing the component.
  Apply message_box_text_alignment_lock: center Insight/message-box text optically both horizontally and vertically within its surface; use balanced padding and line-box placement so the sentence reads intentional, not baseline-drifted.
  Apply insight_surface_placement_lock: when kept, the Insight/message-box belongs to the body composition and footer rhythm; bottom variants sit in the breathing space between body content and Source, centered to the interpreted region or full body block, while Source remains a separate footer cue on its invisible baseline.
  Enforce max_text_size_lock across every visible string; do not use display typography, hero numerals, badges, or message-box text above the cap.
  Keep Honey quiet and consistent: no saturated yellow fills, no dark yellow message boxes, no large yellow areas, no yellow title underline, no Honey color variation across a deck, and no Honey on slides where neutral/no Insight is clearer.
  Use illustrations/icons when they help understanding, memory, comparison, or navigation; do not add them by quota. A slide with no icon or illustration is acceptable when the structure already carries the message.
  Keep icons below the semantic sentence layer: if icons and nouns are doing the work that a reader needs sentences, relationships, or proof to do, rewrite the content before image generation.
  Do not minimize numbers by default. Keep sourced or explicitly assumed numbers when they help comparison, sizing, prioritization, credibility, or decision-making; remove only unsupported, redundant, unreadable, or decorative numbers.
  Render ONLY the exact text strings listed in the planning block or final prompt; do not invent extra labels.
  Keep diagram, chart, table, matrix, map, and flow text simple enough to audit after generation; if the visual needs many tiny labels, group or move detail to speaker notes instead of relying on illegible microtext.
  Keep footer_anchor_baseline planned as an invisible alignment position even when source_line is none.
  Apply source_real_only_lock: render Source footer only for real traceable external/provided sources; if no real source exists, set source_line: none and draw no Source footer text.
  Apply source_placeholder_blocklist: never use placeholder provenance labels such as brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source text.
  Apply source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists.
  Apply source_separator_lock: Source is text-only; do not draw any gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline above, below, behind, or adjacent to Source.
  Do not drop real source names to reduce visual density; shorten or group source names instead.
  Do not include slide numbers, title kickers, numbered header badges, KEY INSIGHT labels, invented sources, placeholder source labels, or production-route source wording.
  Make the composition feel human-crafted through visible priority, breathing room, and editorial rhythm.

negative_prompt_hard_blockers:
  local-rendered substitute, non-gpt-image output, missing or malformed header line, uncontrolled header accent protrusion, header accent floating near page top,
  oversized header, decorative header badge or right-side header ornament, H1/subtitle/source color drift, any gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline near Source/footer, body content invading header/footer, visible text above max_text_size_lock, unreadable body text below 18pt equivalent,
  invented labels or sources, garbled or rewritten exact_text, visible lock names, visible YAML keys, visible route/status fields, decorative pseudo-chart/table/map glyphs, unreadable thumbnail-level hierarchy, broken reading path, placeholder Source footer such as brand assumptions or brand analysis, speaker notes visible on slide, thin or perfunctory PPT talk script, darker beige/cream page background, duplicate loose final PNG copies across output folders, parallel contact sheets for generated/package/pdf_render of the same slide set, unresolved grid, severe grid drift, hard-to-picture abstract visual,
  title-only first slide or low-density opener without proof/tension points,
  icon-and-keyword-only slide, noun-only card grid, generic icon grid, icon wallpaper, repeated decorative icon row, one-icon-per-card habit, icon-only composition with no explanatory sentence layer,
  patterned or textured message box, oversized message box, full-width banner-like Insight, message-box text competing with H1/subtitle,
  saturated yellow message box, deck tone drift, mixed illustration tone, inconsistent face detail or body proportion, inconsistent icon family, inconsistent card/table surface weight, decorative pseudo-3D depth, rough sketch aesthetic,
  mechanical repeated composition without narrative or comparison purpose, generic icon-only composition, dated template composition, slide number, title kicker, logo in upper-right clear zone

post_generation_audit:
  - image model is {IMAGE_MODEL}
  - generation_route is Codex built-in image generation, not local rendering or a local credential workaround
  - image_generation_tool_lock is honored: the final PNG pixels came from Codex built-in image generation, not scripts, local renderers, screenshots, or presentation exports
  - script_boundary_lock is honored: prompt/package scripts were used only for planning, validation, or delivery wrapping after approved Codex image artifacts existed
  - credential_setup_blocker is honored: no account credential, local token, SDK setup, or environment-variable workflow was attempted before generation
  - progress_update_route_lock is honored: user-facing progress did not describe local credential, environment, SDK, save-route, or alternate setup checks as prerequisites
  - image_size {size} is valid for gpt-image-2, labeled as {size_label(size)}, and final delivery wrappers reuse the same 2048x1152 slides_final/ PNG masters without resizing or alternate master creation
  - default_2k_generation_lock is honored: generated slide PNG masters use 2048x1152 for review, PPTX, and PDF packaging
  - nonconforming_existing_png_regeneration_lock is honored: any existing/source PNG at 1672x941 or another non-approved package size was not treated as a final blocker or converted locally; a new 2048x1152 Codex built-in gpt-image-2 master was generated from the approved specification before packaging
  - prompt_order_lock is fulfilled: the prompt led with draw/edit action, exact visible text, canvas/style, fixed components, layout/reading path, visual details, optional Insight, then focused blockers
  - render_contract_lock is fulfilled: operational metadata stayed out of visible slide content
  - visible_text_only_lock is fulfilled: only exact_text strings appear on the slide
  - positive_quality_lock is fulfilled: blockers did not replace the positive composition target
  - revised_prompt_review_lock is fulfilled when revised_prompt is available; otherwise actual PNG review remains the source of truth
  - H1 and subtitle hierarchy is clear
  - near_white_slide_base_lock is honored: the slide canvas reads as #FCFBF8 / very near white, with #F4F3EF only as a subtle tint and no darker cream/beige page background
  - max_text_size_lock is honored: no visible text exceeds 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
  - header_identity_lock is honored: the header remains the compact left vertical line + H1 + subtitle system, with no slide-specific decoration surface
  - deck_header_master_lock is visible and consistent; left header accent is present, matches header_left_accent_reference_lock unless superseded by a newer embedded master, obeys header_line_top_rule and header_left_accent_master_lock, anchors the H1 + subtitle stack, is not a page-edge rail/sidebar/body marker, and H1 color follows the embedded ATOM design system
  - header_left_accent_shape_lock passes: the accent is one solid 10px vertical rectangle with no pill cap, glow, shadow, gradient, duplicate mark, or decorative extension
  - header_left_accent_no_protrusion_rule passes: the accent starts at the first visible H1 glyph/title top or 0-6px below it, with no upward protrusion
  - header_left_accent_top_protrusion_blocker passes: no visible accent pixel sits above the first visible H1 glyph/title top, outside header_safe_area, detached from H1/subtitle, or inside body_start_y
  - header_integrity_blocker_lock is clear: no malformed, missing, oversized, recolored, right-decorated, or intruded header remains
  - header_footer_text_color_lock is honored: H1 #2D332E, subtitle #4D544E, footer/source/table-note #6E756E
  - header/footer text does not use Deep Blue, Honey, yellow, or arbitrary gray
  - deck_tone_signature_lock is honored: base, typography, rule weight, card/table surfaces, icon stroke, illustration linework, accent budget, density rhythm, Insight treatment, and Source behavior feel like one material system
  - illustration_tone_lock is honored: all illustrations share one flat 2D editorial vector system across the generated PNG set
  - illustration_style_sheet is visible when illustration is used: selected people, devices, documents, UI panels, operational objects, icon badges, fills, stroke, crop, and detail level match the declared domain-matched style sheet
  - illustration_consistency_status is approved after comparing first, middle, and last thirds for stroke weight, fill opacity, face/detail level, object treatment, and illustration density
  - visual_richness_role is fulfilled; planned illustration or visual motif is present when required
  - imageability_lock is fulfilled: a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details are present
  - exact_text_fidelity_lock is fulfilled: every visible H1, subtitle, label, number, source string, and optional Insight matches exact_text; missing, invented, garbled, duplicated, or rewritten copy is a repair_required issue
  - chart_semantic_integrity_lock is fulfilled: any chart, table, matrix, flow, map, or evidence strip has meaningful structure, aligned rows/columns/arrows, legible labels, and no decorative fake data texture
  - thumbnail_legibility_lock is fulfilled: the slide still communicates its main claim, focal structure, region boundaries, and key numbers when reviewed as a slide-sorter thumbnail or contact-sheet tile
  - reading_path_lock is fulfilled: the eye can move from H1 to main visual, evidence/context, optional Insight, and Source without competing primary focal points
  - editorial_polish_repair_loop has improved specificity, proportion, rhythm, and focal hierarchy
  - visual_subject_open_set is fulfilled: the selected visual subject comes from the slide message, evidence, and audience context rather than a fixed asset menu
  - message_led_composition_lock is fulfilled: one focal relationship carries the argument before supporting elements
  - region_balance_policy is fulfilled: region weight follows the slide message, evidence shape, reading path, and body silhouette rather than a fixed template
  - composition_fit_plan is fulfilled: the main visual field, supporting regions, whitespace role, and Insight footprint feel intentionally balanced
  - content_area_priority_lock is fulfilled: the body, figure, table, or diagram gets the needed height first, and any optional Insight/message-box is sized from the remaining calculated space
  - secondary_region_integrity_lock is fulfilled: any split or auxiliary region reads as a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field
  - body_silhouette_lock is fulfilled: the body reads as one closed visual block with aligned outer edges, lower edges, and footer clearance
  - illustration_intensity is respected; illustration feels designer-authored, flat 2D, and does not overpower the slide
  - density_tier and density_design are fulfilled without shrinking body text below 18pt equivalent
  - impact_clarity_density_gate is fulfilled: the slide has a sharp takeaway, clear structure, useful evidence, simplicity, and hierarchy
  - message_sharpness_lock is fulfilled: the H1/action title is not a vague label or slogan
  - pyramid_logic_lock is fulfilled: a single governing thought is stated, each action title answers the question its predecessor raises, the title read-through is one connected argument, and a named exhibit element proves each title
  - mece_support_gate is fulfilled: within-slide supporting points are mutually exclusive and collectively exhaustive, and body_logic is declared inductive or deductive
  - evidence_compression_ladder is fulfilled: proof is compressed into a readable structure rather than prose or decoration
  - chart_emphasis_lock is fulfilled: non-focal data is grayed out, the decision-carrying number is a direct on-mark label, and series are labeled directly unless 5+ series force a legend
  - encoding_consistency_lock is fulfilled: scenario/variance/category encodings and repeated-unit scales are constant across the deck, and no distinction relies on hue alone
  - number_format_normalization_lock is fulfilled: decimal precision, magnitude abbreviation, axis ticks, and period notation are normalized for each metric
  - density_lift_lock is fulfilled in both the slide structure and final image prompt
  - sentence_density_lift_lock is fulfilled: body labels, rows, annotations, or optional Insight contain compact meaningful clauses/sentences that explain relationship, reason, consequence, or decision relevance
  - semantic_copy_gate is fulfilled: major body labels are not noun-only unless they are headers, axes, legends, or categories
  - icon_restraint_lock is fulfilled: icons are sparse, purposeful wayfinding/evidence markers and never replace the semantic sentence layer or dominate the content
  - icon_density_budget is fulfilled: icon count is normally 0-3 per slide, below semantic text units, and never follows a one-icon-per-card habit
  - structure_choice_bias is considered: structured presentation patterns are used where they clarify the message, and not forced where they would add noise
  - structured_density_bias is fulfilled when useful: one or two evidence layers, labels, drivers, or comparison cues add decision value without crowding
  - structure_choice_status is not_applicable, applied, intentionally_skipped, or repair_required with a clear reason
  - structure_first_visual_mix is fulfilled through argument-carrying charts, tables, matrices, flows, maps, comparison axes, or evidence strips where appropriate, with illustration used as support
  - density_levers improve the message through comparison, evidence, annotation, grouping, or source cues rather than decoration
  - decision-relevant numbers are preserved when legible; numbers are not minimized by default
  - message boxes and Insight surfaces use flat solid fills only, with no decorative patterns or motifs
  - message_box_scale_lock is honored: message boxes stay compact, are sized from the remaining layout space after the main content area, and are not enlarged to carry long prose
  - message_box_text_size_lock is honored: message-box/Insight text is smaller than H1 and subtitle and never reads as a second title
  - message_box_compactness_blocker_lock is clear: no Insight/message-box dominates the slide, behaves like a banner, grows tall for prose, or compensates for layout imbalance
  - message_box_text_alignment_lock is honored: Insight/message-box text is optically centered horizontally and vertically inside the surface
  - insight_surface_placement_lock is honored: kept Insight/message-box surfaces bridge the interpreted body region and footer rhythm without competing with either
  - visible_brand_label_blocker passes: no separate ATOM wordmark, logo, title kicker, or brand label appears in the header unless exact_text explicitly requested it
  - If a Honey Insight/message-box is justified and kept, it uses #FBF3D7 very pale fill, #C49A2C thin outline/separator, optional left icon well with a small 20-24px icon, and #2D332E text consistently
  - Honey is not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
  - Honey is absent from main content cards, missing-body placeholders, dashed outlines, category badges, title underlines, and decorative yellow blocks
  - saturated yellow, dark yellow, or large yellow areas are absent
  - coordinate_inventory_1672 matches visible major objects
  - all major regions snap to grid/shared edges
  - layout_family matches the slide message, and layout_diversity_plan / layout_rotation_guard make deck-level composition feel intentionally varied rather than mechanically repeated
  - repeated elements are equalized
  - body text remains readable
  - embedded ATOM design system palette and typography are followed
  - brand accent is structural and not body text
  - Insight component is selective, compatible with the embedded ATOM design system, and not decorative
  - invisible footer alignment baseline is preserved without drawing a line
  - output_artifact_mastering_lock is honored: slides_final/ is the single loose-PNG master, slides_package/ contains package artifacts only, and render_check/pdf_pages/ is disposable QA output only
  - pdf_export_source_lock is honored: PDF outputs are built from slides_final/ master PNGs, and render_check/pdf_pages/ is not used as a source image folder
  - no_duplicate_png_output_lock is honored: no duplicate loose final PNG copies are retained across slides_final/, slides_package/, and render_check/pdf_pages/
  - contact_sheet_mastering_lock is honored: the retained contact sheet is a single render_check/contact_sheet_review.png from slides_final/ unless one explicit delivery comparison sheet or render_diff_report is needed
  - single_contact_sheet_policy is honored: no parallel contact_sheet_generated*, contact_sheet_package*, and contact_sheet_pdf_render* files are retained for the same slide set
  - Source footer follows source_real_only_lock: Source appears only for real traceable external/provided sources; no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions appear as Source text
  - Source footer follows source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
  - Source footer follows source_separator_lock: Source is text-only, with no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline above, below, behind, or adjacent to Source
  - footer/source/table-note text uses #6E756E consistently when present
  - speaker_notes_depth_lock is honored: speaker_notes_text exists for deck slides, is substantial enough for PPT presentation delivery, and does not appear on the slide image
  - speaker_notes_persuasion_lock is honored: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, stay consistent with notes_persuasion_arc, and add hook/objection-preempt/delivery markers only where justified
  - post_generation_full_deck_review_loop is complete: after generating slide PNGs, every actual image has been opened, compared against the deck, and reviewed before claiming completion
  - all_generated_images_reviewed is true for the current output file set
  - weak_slide_regeneration_queue is empty after reviewing tone consistency, content quality, design quality, text legibility, source/footer/header integrity, illustration consistency, structure fit, and deck unity
  - deck_tone_consistency_status is approved after comparing first third, middle third, and last third for palette, linework, icon family, illustration intensity, density rhythm, card geometry, and source behavior
  - content_quality_status is approved: no slide has a weak message, missing evidence, misleading source use, vague labels, or shallow structure when structure would clarify the argument
  - design_quality_status is approved: no slide looks mechanically generated, under-composed, over-dense, off-grid, typographically awkward, or visually weaker than the rest of the deck
  - deck_unity_status is approved: all generated PNGs feel like one deck in palette, illustration tone, icon family, component geometry, information density, header/footer behavior, and editorial rhythm
  - completion_ready_status is approved only after all review queues are empty and all content/design/deck-unity statuses are approved
  - regenerate_until_quality_approved has been applied to every weak slide
  - completion_blocker: do not report complete while any generated slide has blocker, major, deck-consistency, content-quality, or design-quality issues
  - generation_block_rule: only if Codex built-in generation or repair is actually blocked by the image tool, mark completion_ready_status: blocked and do not package or report complete; do not use local environment uncertainty as the blocker
  - credential_setup_blocker: no account credential, local token, SDK setup, or environment-variable workflow is part of the route
  - review_manifest_status: approved after validate_review_manifest covers every generated PNG path, confirms slides_final/ master paths are used, confirms weak_slide_regeneration_queue is empty, and confirms all final/content/design/deck-unity/completion statuses are approved
  - post_generation_design_balance_check is approved on actual generated PNGs: whitespace/occupancy balance, density balance against the planned density tier, typography size/weight balance, color consistency, outer padding consistency, header integrity, card/table height equalization, line-weight consistency, icon-family consistency, Deep Blue scatter, Honey strength, and human-designed operational diagram feel
  - pre_package_image_review has inspected the actual generated PNG, not only the prompt
  - image_review_status is approved only when there are no blocker or major issues
  - PPTX/PDF roll-up starts only after final_image_quality_status is approved for every generated PNG
  - PPTX/PDF roll-up contains one full-bleed generated PNG per slide in order, with speaker notes inserted when packaging supports notes

pre_package_image_review:
  - Inspect the actual generated PNG with multimodal review before any PPTX/PDF roll-up or completion.
  - Review every actual generated image in the deck as a set before claiming completion.
  - Score model route, exact text, header lock, grid/shared edges, typography, density, illustration clarity, human-designed feel, source hygiene, and speaker-notes separation.
  - Score layout_family fit and layout_rotation_guard across the generated image set.
  - Score deck_tone_consistency across all generated PNGs after every generation or repair batch.
  - Score illustration_consistency_status across all generated PNGs after every generation or repair batch.
  - Score content_quality_status, design_quality_status, and deck_unity_status; queue any slide that feels content-weak, design-weak, inconsistent, or below the deck bar.
  - Score post_generation_design_balance_check: whitespace/occupancy balance, density balance against the planned density tier, typography size/weight balance, color consistency, outer padding consistency, and header integrity.
  - Classify each finding as blocker, major, minor, or accepted.
  - If any blocker, major, deck-consistency, content-quality, design-quality, or deck-unity issue exists, create image_repair_prompt, add the slide to weak_slide_regeneration_queue, regenerate or edit the PNG, replace the output file, and repeat this review.
  - Apply edit_scope_lock in every repair prompt: issue_observed, change_only, preserve, re_check, and no global restyle unless explicitly required.
  - Apply repair_or_regenerate_decision: edit localized defects; regenerate when the core composition, density, tone, reading path, semantic graphic structure, or visual anchor fails.
  - Continue until all_generated_images_reviewed is true, weak_slide_regeneration_queue is empty, final_image_quality_status is approved, and completion_ready_status is approved.
  - If generation or repair is blocked, set completion_ready_status: blocked, keep unresolved slides in the review_manifest, and do not package or report complete.
  - PPTX/PDF package gate requires an approved review manifest; run validate_review_manifest before packaging.

repair_iteration_plan:
  - iteration_0: first generated PNG review
  - iteration_n: repair prompt -> regenerated/edited PNG -> re-review -> update weak_slide_regeneration_queue
  - approval_condition: no blockers, no majors, minor issues only if they do not affect readability, brand fidelity, source integrity, or deck consistency
  - review_manifest: [slide_id -> png_path -> image_review_status -> blockers -> majors -> final/content/design/deck-unity/completion status]
"""


def deck_plan_tail() -> str:
    return """deck_plan_output:
  - deck_thesis:
  - governing_thought:
  - governing_thought_gate:
  - notes_persuasion_arc:
  - vertical_logic_chain:
  - primary_guideline:
  - guideline_priority:
  - brand_style_notes:
  - opening_slide_rule:
      opening_slide_role: opening_thesis_slide
      first_slide_not_title_only: true
      opening_density_gate: core thesis + 2-4 proof/tension points + visible market-shift/matrix/causal-map/wedge structure + bridge
      ask_present: [decision/recommendation deck: explicit ask or next step on the opener or slide 2]
      top_risk_named: [decision/recommendation deck: single most likely objection or dependency named on the opener or slide 2]
      low_density_opener_repair: add evidence, tension, comparison, or mechanism before image generation
  - slide_list:
      - slide_number:
        slide_message:
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
        illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system
        illustration_style_sheet:
        illustration_consistency_status:
        creative_variance:
        density_tier:
        signature_visual_plan:
        insight_decision:
        message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement; many slides should use no message box
        insight_absence_default_lock: start from no Insight/message-box
        insight_justification_required: keep only with a non-redundant interpretation, decision signal, or reading bridge
        honey_bottom_bar_lock: Honey is a quiet optional bottom Insight bar treatment, not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
        honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
        honey_justification_required: keep Honey only with a written reason tied to decision clarity
        output_artifact_mastering_lock: slides_final/ is the only loose-PNG master; package and render-check folders hold only derivative artifacts
        single_final_png_master_lock: review manifests and package mappings reference the slides_final/ master path
        no_duplicate_png_output_lock: no duplicate loose PNG copies across slides_final/, slides_package/, and render_check/pdf_pages/
        contact_sheet_mastering_lock: one retained contact_sheet_review.png by default; comparison sheet only when delivery QA requires it
        single_contact_sheet_policy: no parallel generated/package/pdf_render contact sheets for the same slide set
        source_real_only_lock: render Source only for real traceable external/provided sources; otherwise source_line none and no Source footer
        source_placeholder_blocklist: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source
        source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
        source_separator_lock: Source is text-only; no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline may appear above, below, behind, or adjacent to Source
        source_policy:
        source_line:
        density_risk:
        impact_clarity_density_gate:
        message_sharpness_lock:
        pyramid_logic_lock: state one governing thought, ladder each action title to the question its predecessor raises, and prove each title with a named exhibit element
        predecessor_question:
        title_exhibit_proof_match:
        mece_support_gate: a slide's supporting points are mutually exclusive and collectively exhaustive, and each slide declares body_logic as inductive or deductive
        body_logic: inductive / deductive
        evidence_compression_ladder: choose the smallest proof structure that makes the message credible: key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation
        chart_emphasis_lock: gray out non-focal data, place the decision-carrying number as a direct on-mark label, and label series directly instead of using a legend
        encoding_consistency_lock: same meaning keeps the same fill/color/shape and scale across the deck, and no distinction relies on hue alone
        number_format_normalization_lock: normalize decimal precision, magnitude abbreviation, axis ticks, and period notation before freezing exact_text
        speaker_notes_depth_lock: substantial PPT talk script, 4-7 Japanese sentences or roughly 180-320 Japanese chars unless user requests brief notes
        speaker_notes_persuasion_lock: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and may add a justified hook, objection pre-empt, or delivery markers
        speaker_notes_text:
        speaker_notes_source_cues:
        speaker_notes_transition:
        speaker_notes_landing:
        speaker_notes_signpost:
        notes_hook:
        notes_objection_preempt:
        notes_delivery_markers:
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
        density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
        sentence_density_lift_lock: raise density one step with compact meaningful clauses or short sentences in body labels, rows, annotations, and optional Insight; avoid icon-and-keyword-only slides
        semantic_copy_gate: major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names
        icon_restraint_lock: icons are sparse wayfinding/evidence markers and not the primary content layer
        icon_density_budget: default to 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise
        structure_choice_bias: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide
        structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits; add layers only until the body silhouette is filled with deliberate content, then split the slide instead, because overcrowding is not solved with more density
        structure_choice_status:
        structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
        max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
        imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
        editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
        visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide message, evidence, and audience context
        message_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide message before adding supporting elements
        region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette
        composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy; occupancy is observable - no quadrant of the body content area is conspicuously empty and no major region overflows its grid track]
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
        message_type:
        layout_family:
        composition_family:
        previous_family:
        repeat_or_change_reason:
  - deck_tone_master_lock:
  - deck_tone_signature_lock:
  - near_white_slide_base_lock: #FCFBF8 default ATOM slide canvas; optional #F4F3EF subtle warm light-neutral tint only; keep #DDE3EA/#D6E1EE for panels/cards and avoid darker cream/beige page backgrounds
  - illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system
  - illustration_style_sheet:
  - illustration_consistency_status:
  - visual_design_quality_traits:
  - deck_header_master_lock:
  - header_identity_lock:
  - header_line_top_rule:
  - header_left_accent_master_lock:
  - header_left_accent_reference_lock:
  - header_left_accent_shape_lock:
  - header_left_accent_no_protrusion_rule:
  - header_left_accent_top_protrusion_blocker:
  - header_integrity_blocker_lock:
  - visible_brand_label_blocker: no separate ATOM wordmark, logo, title kicker, badge, or brand label in the header unless exact_text explicitly requests it
  - deep_blue_usage_lock:
  - visual_asset_judgment:
  - visual_richness_mix_plan:
  - density_tier_plan:
  - structure_choice_bias:
  - structured_density_bias:
  - structure_choice_status:
  - density_design_plan:
  - insight_count_plan:
  - message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement; many slides should use no message box
  - insight_absence_default_lock: start each slide from no Insight/message-box
  - insight_justification_required: use a message box only when the slide loses needed interpretation, decision signal, or reading bridge without it
  - honey_bottom_bar_lock: Honey is a quiet optional bottom Insight bar treatment, not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
  - honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
  - honey_justification_required: keep Honey only with a written reason tied to decision clarity
  - message_box_scale_lock: bottom Insight bars target 72-96px on the 1672 basis, with 108px only for a necessary two-line sentence
  - message_box_compactness_blocker_lock:
  - source_collection_needs:
  - speaker_notes_plan:
  - speaker_notes_depth_lock: substantial Japanese PPT talk script, 4-7 sentences or roughly 180-320 Japanese chars per slide unless user requests brief notes
  - pre_package_image_review_plan:
  - post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion
  - all_generated_images_reviewed:
  - image_review_matrix:
      - slide_id:
        iteration:
        png_path:
        blockers:
        majors:
        repair_prompt:
        new_png_path:
        status:
  - weak_slide_regeneration_queue:
      - slide_id:
        reason:
        regenerate_or_edit_action:
        new_png_path:
        review_status:
  - deck_consistency_matrix:
      first_third:
      middle_third:
      last_third:
      tone_layout_spacing_source_findings:
  - content_quality_status:
  - design_quality_status:
  - deck_unity_status:
  - completion_ready_status:
  - regenerate_until_quality_approved:
  - generation_block_rule: only if Codex built-in generation or repair is actually blocked by the image tool, mark completion_ready_status: blocked and do not package or report complete; do not use local environment uncertainty as the blocker
  - review_manifest:
  - review_manifest_status: approved
  - package_gate: PPTX/PDF package gate requires an approved review manifest
  - validate_review_manifest:
  - package_delivery:
  - pdf_delivery:
  - pdf_status:
  - pdf_output_path:
  - pdf_slide_count:
  - package_image_mapping:
  - pdf_image_mapping:
  - pptx_rollup_plan:
  - slides_requiring_full_planning_block:
  - blocking_unresolved_items: all slide-level planning blocks remain required before image generation
"""


def text_structure_tail() -> str:
    return """text_to_slide_structure_output:
  deck_thesis:
  governing_thought:
  governing_thought_gate:
  notes_persuasion_arc:
  vertical_logic_chain:
  audience_decision:
  primary_guideline:
  guideline_priority:
  brand_style_notes:
  storyline_frame: SCQA / problem-solution-evidence / past-present-future / context-problem-solution-differentiation / thesis-risk-milestones
  message_backlog:
  evidence_ledger:
  source_ledger:
  appendix_candidates:
  open_questions:
  opening_slide_rule:
    opening_slide_role: opening_thesis_slide
    first_slide_not_title_only: true
    opening_density_gate: core thesis + 2-4 proof/tension points + visible market-shift/matrix/causal-map/wedge structure + bridge
    ask_present: [decision/recommendation deck: explicit ask or next step on the opener or slide 2]
    top_risk_named: [decision/recommendation deck: single most likely objection or dependency named on the opener or slide 2]
    low_density_opener_repair:
  section_map:
    - section:
      role:
      slide_ids:
  slide_structure:
    - slide_id:
      chapter:
      action_title:
      pyramid_logic_lock: state one governing thought, ladder each action title to the question its predecessor raises, and prove each title with a named exhibit element
      predecessor_question:
      title_exhibit_proof_match:
      mece_support_gate: a slide's supporting points are mutually exclusive and collectively exhaustive, and each slide declares body_logic as inductive or deductive
      mece_check:
      body_logic: inductive / deductive
      opening_slide_role: opening_thesis_slide / standard_story_slide
      first_slide_not_title_only: true / N/A
      opening_density_gate:
      reader_question_answered:
      message_type: context / urgency / solution / evidence / differentiation / market / economics / roadmap / risk / vision
      evidence_items:
      evidence_strength:
      source_span_ids:
      source_policy: real source / none / research needed
      output_artifact_mastering_lock:
      single_final_png_master_lock:
      no_duplicate_png_output_lock:
      contact_sheet_mastering_lock:
      single_contact_sheet_policy:
      source_real_only_lock: render Source only for real traceable external/provided sources; otherwise source_line none and no Source footer
      source_placeholder_blocklist: no brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions as Source
      source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists
      source_separator_lock: Source is text-only; no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline may appear above, below, behind, or adjacent to Source
      source_line: Source: [traceable source names copied from provided or researched sources only] / none only when no traceable source exists
      source_urls:
      assumptions:
      speaker_notes_depth_lock:
      speaker_notes_persuasion_lock: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and signpost transition, and may add a justified hook, objection pre-empt, or delivery markers
      speaker_notes_text:
      speaker_notes_source_cues:
      speaker_notes_transition:
      speaker_notes_landing:
      speaker_notes_signpost:
      notes_hook:
      notes_objection_preempt:
      notes_delivery_markers:
      pre_package_image_review:
      post_generation_full_deck_review_loop: after generating slide PNGs, review every actual image before claiming completion
      all_generated_images_reviewed:
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
      weak_slide_regeneration_queue:
        slide_id:
        reason:
        regenerate_or_edit_action:
        new_png_path:
        review_status:
      final_image_quality_status:
      content_quality_status:
      design_quality_status:
      deck_unity_status:
      completion_ready_status:
      regenerate_until_quality_approved:
      generation_block_rule: only if Codex built-in generation or repair is actually blocked by the image tool, mark completion_ready_status: blocked and do not package or report complete; do not use local environment uncertainty as the blocker
      review_manifest:
      review_manifest_status: approved
      validate_review_manifest:
      deck_tone_consistency_review:
      deck_tone_consistency_status:
      deck_tone_signature_lock:
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
      illustration_tone_lock: keep all illustrations in one deck on the same editorial vector system
      illustration_style_sheet:
      illustration_consistency_status:
      creative_variance: low / medium / high
      density_tier: T1_sparse / T2_balanced / T3_dense / T4_appendix_dense
      impact_clarity_density_gate:
      message_sharpness_lock:
      evidence_compression_ladder: choose the smallest proof structure that makes the message credible: key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation
      chart_emphasis_lock: gray out non-focal data, place the decision-carrying number as a direct on-mark label, and label series directly instead of using a legend
      encoding_consistency_lock: same meaning keeps the same fill/color/shape and scale across the deck, and no distinction relies on hue alone
      number_format_normalization_lock: normalize decimal precision, magnitude abbreviation, axis ticks, and period notation before freezing exact_text
      benchmark_reference_line:
      density_layers:
      density_design:
        reader_mode: scan / read / reference
        decision_question:
        information_units:
        semantic_sentence_layer:
        semantic_copy_gate:
        icon_restraint_plan:
        icon_density_budget:
        density_levers:
        overload_controls:
      density_lift_lock: raise useful information density during both slide-structure planning and slide-image prompting
      sentence_density_lift_lock: raise density one step with compact meaningful clauses or short sentences in body labels, rows, annotations, and optional Insight; avoid icon-and-keyword-only slides
      semantic_copy_gate: major body labels use meaningful clauses/sentences; noun-only labels are allowed only for headers, axes, or category names
      icon_restraint_lock: icons are sparse wayfinding/evidence markers and not the primary content layer
      icon_density_budget: default to 0-3 purposeful icons per slide and keep icon count below semantic text units unless the visual logic demands otherwise
      structure_choice_bias: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide
      structured_density_bias: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits; add layers only until the body silhouette is filled with deliberate content, then split the slide instead, because overcrowding is not solved with more density
      structure_choice_status:
      structure_first_visual_mix: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation
      information_unit_budget:
      density_guardrails:
      deck_header_master_lock:
      header_line_top_rule:
      header_left_accent_master_lock:
      header_left_accent_reference_lock:
      header_left_accent_shape_lock:
      header_left_accent_no_protrusion_rule:
      header_left_accent_top_protrusion_blocker:
      deck_tone_master_lock:
      illustration_tone_lock:
      illustration_style_sheet:
      illustration_consistency_status:
      deep_blue_usage_lock:
      header_footer_text_color_lock:
      visible_brand_label_blocker: no separate ATOM wordmark, logo, title kicker, badge, or brand label in the header unless exact_text explicitly requests it
      message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement; many slides should use no message box
      insight_absence_default_lock: start from no Insight/message-box
      insight_justification_required: keep only with a non-redundant interpretation, decision signal, or reading bridge
      honey_bottom_bar_lock: Honey is a quiet optional bottom Insight bar treatment, not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
      honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
      honey_justification_required: keep Honey only with a written reason tied to decision clarity
      message_box_scale_lock:
      message_box_text_size_lock:
      message_box_compactness_blocker_lock:
      message_box_text_alignment_lock:
      insight_surface_placement_lock:
      max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt
      imageability_lock: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation
      editorial_polish_repair_loop: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm
      visual_subject_open_set: keep visual subject choices open; select the clearest concrete subject from the slide message, evidence, and audience context
      message_led_composition_lock: choose the structure, viewpoint, region balance, and focal relationship from the slide message before adding supporting elements
      region_balance_policy: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette
      composition_fit_plan: [main visual field, supporting regions, whitespace role, Insight footprint, and intended occupancy; occupancy is observable - no quadrant of the body content area is conspicuously empty and no major region overflows its grid track]
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
        body_labels: [compact meaningful clauses/sentences except headers/categories]
        chart_labels: [legible labels; noun-only allowed for axes/legends/categories]
        insight_text:
      data_to_render:
      exact_text_budget: H1 + subtitle + short labels + decision-relevant numbers + optional one-sentence Insight
      insight_decision:
      insight_absence_default_lock: start from no Insight/message-box
      insight_justification_required: keep only with a non-redundant interpretation, decision signal, or reading bridge
      honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
      honey_justification_required: keep Honey only with a written reason tied to decision clarity
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
  next_step: create canonical planning blocks for image_prompt_ready slides, run Codex built-in image generation pilot, then run pre_package_image_review before any PPTX/PDF roll-up or completion."""


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
    parser.add_argument("--size", default="2048x1152")
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
