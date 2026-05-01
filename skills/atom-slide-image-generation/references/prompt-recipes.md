# Prompt Recipes

Use these recipes after applying `embedded ATOM design system in SKILL.md`. Keep final prompts concrete, coordinate-aware, and explicit that final bitmap generation uses `gpt-image-2`.

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
image_delivery_size: 1920x1080 after resize if exact ATOM delivery size is required
generation_route: Codex built-in image generation
generation_status: generated_with_builtin_gpt-image-2 / blocked
google_slides_delivery: image-only roll-up after generated PNGs pass QA, unless user asks for files only
speaker_notes_status: drafted / inserted / blocked
```

Do not request `1920x1080` directly from `gpt-image-2`; use a valid multiple-of-16 image-generation size and resize after generation when needed.
Do not substitute local rendering, screenshots, SVG, PIL, canvas, or PPT exports for final image-generation output.

## Base Image Contract

```text
Draw a 16:9 strategy slide image with gpt-image-2.
Generate at 1536x864 for drafts, 2048x1152 for 16:9 2K-width working review, or 2560x1440 for final output.
Plan all layout using a 1672x941 coordinate basis, with ATOM delivery target 1920x1080 after resize if required.
Treat 1920x1080 as FHD/1080p delivery, 2048x1152 as practical 16:9 2K-width generation, and 3840x2160 as 4K UHD generation.
Use a shared 12-column grid, 8px spacing rhythm, and precise header/footer anchors.
For decks, define and reuse one deck header master. Repeat the same left vertical line, H1, subtitle, visual alignment rule, body-start y, header safe area, and clear zone in every slide prompt. Final prompts must use exact selected x/y/w/h/color/font values for the header, not ranges. The line must align to the visible H1/subtitle glyph block; it must not protrude above the H1 just because the text box starts higher.
Request Noto Sans JP style or the closest clean Japanese sans-serif and keep text short enough to audit.
For ATOM work, use Charcoal Ink #2D332E for H1/body, grey Ink #4D544E or #6E756E for subtitle/footer, Deep Blue #0B2F5B for structure, and Honey only as a quiet decision signal.
No slide numbers, no title kicker, no numbered header badge.
Avoid pure black, old Mustard, neon teal, heavy shadows, glow, glassmorphism, decorative gradients, and generic stock imagery.
Use small Lucide-style line icons only as quiet wayfinding where they clarify reading order.
Use human-designed editorial/vector illustrations and purpose-built motifs when the claim needs memory or freshness; avoid long runs of text/table-only slides, but keep charts, tables, matrices, or roadmaps as the primary structure when they carry the argument.
Design information density before image generation. Density should answer more of the reader's decision question in one view through hierarchy, evidence, comparison, annotation, source cues, and context layers; do not use smaller type, extra decoration, or visual noise as density.
Do not minimize numbers by default. Keep decision-relevant sourced or explicitly assumed numbers when they support comparison, sizing, prioritization, credibility, or decision-making.
Message boxes and Insight surfaces must use flat solid fills only; no patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations inside the box.
Honey message boxes have one fixed treatment: #F7EECF flat pale fill, #C49A2C 4-5px full-height left accent line, #2D332E text. Avoid saturated yellow fills, dark yellow boxes, large yellow areas, and yellow title underlines.
Preserve distinct claims as distinct slides. Combine slides only when claims repeat, the same comparison must be seen together, or the user explicitly requests a shorter deck.
Do not prompt for rough hand-drawn sketches, glossy AI-looking hero art, or arbitrary pseudo-depth. Avoid rough doodle, messy sketch, luminous, cinematic, heroic robot, futuristic city, abstract 3D, dramatic glow, photoreal, ultra-detailed, decorative trapezoid planes, tilted floors, isometric boxes, vanishing-point perspective, or wallpaper-like concept art unless the user explicitly asks for that style.
Do not hard-code one visual grammar for every slide. Select the projection, viewpoint, abstraction level, motif, and level of detail from the slide claim; the chosen visual can be a diagram, scene, system view, comparison, object detail, spatial view, sequence, or metaphor when it clarifies the argument.
For humanoid/robot decks, represent the idea through small interaction details, system cues, partial figures, or embedded operational motifs by default. A full-body robot or city skyline must be rare and secondary to the slide's structure.
When the user asks to raise temperature, use `creative_variance: high` rather than claiming an API temperature parameter. High variance means more freedom in viewpoint, crop, asymmetry, visual metaphor, and layout rhythm, while all brand, header, exact text, grid, and source constraints remain locked.
Required image model: gpt-image-2.
Final slide image files must be actual Codex built-in image-generation outputs. Local wireframes or deterministic renders are not final generated images.
For multi-slide decks, roll approved generated PNGs into a native Google Slides deck as image-only full-bleed slides, then attach speaker notes to each slide's notes page. Speaker notes are generated from the deck structure, not from image generation, and should contain talk track, evidence/assumption cue, source caveat if needed, and transition cue.
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
google_slides_delivery:
google_slides_status:
google_slides_title:
google_slides_file_id:
google_slides_url:
google_slides_slide_count:
google_slides_route:
google_slides_image_mapping:
google_slides_speaker_notes_mapping:
speaker_notes_plan:
speaker_notes_status:
speaker_notes_text:
layout_archetype:
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
deck_header_master_lock:
  coordinate_basis:
  status: exact_required_before_generation
  header_safe_area:
  vertical_line:
  h1:
  subtitle:
  visual_alignment:
  body_start_y:
  upper_right_clear_zone:
  forbidden_header_elements:
component_inventory:
equalized_groups:
shared_edges:
hand_placed_exceptions:
visual_richness_role:
signature_visual_plan:
illustration_region:
illustration_intensity:
human_designed_illustration_style:
creative_variance:
density_tier:
density_layers:
density_design:
  reader_mode: scan / read / reference
  decision_question:
  information_units: [claim, context, comparison, trend, mechanism, risk, implication, assumption, source]
  density_levers: [KPI strip, right rail, evidence strip, small multiples, annotations, benchmark/context column, source cue]
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
final_image_prompt:
negative_prompt:
post_generation_audit:
```

Block generation if `layout_archetype`, `grid_mode`, `coordinate_inventory_1672`, `master_components`, or `source_policy` remains unresolved.

## Single Slide Image Prompt

```text
Brief:
[paste user brief]

ATOM slide contract:
- primary_guideline is the embedded ATOM design system in SKILL.md
- embedded ATOM style is the default, palette, typography, and components
- use embedded ATOM design mechanics
- use image_model gpt-image-2
- use generation_mode new_image for new single-slide images or image_edit for screenshot/reference repair
- use image_size 1536x864 for drafts, 2048x1152 for 16:9 2K-width working review, or 2560x1440 for final output; resize to 1920x1080 after generation if exact FHD/1080p delivery size is required
- treat strict DCI 2K 2048x1080 and DCI 4K 4096x2160 as non-target cinema sizes, not ATOM 16:9 slide generation sizes
- use image_background opaque or auto, never transparent
- use png for slide fidelity unless latency or file size matters
- use moderation auto by default
- use n=1 for final text-heavy slides; use multiple variations only for draft exploration
- 1 slide = 1 claim
- 1 dominant structure
- select one layout_archetype and grid_mode before writing text
- define coordinate_inventory_1672 with x/y/w/h for major objects
- define master_components and deck_master_refs before repeating cards, rows, icons, or bands
- define deck_header_master_lock before any slide prompt and repeat it verbatim across the deck; exact header values are required before generation
- define component_inventory, row_tracks, column_tracks, equalized_groups, and shared_edges
- lock header anchor first: left vertical line + H1 + subtitle + visual alignment + header safe area + body_start_y + upper-right clear zone
- lock footer_anchor_baseline even when source_line is none
- keep source_line separate from table_note_microline
- draft speaker_notes_text for every deck slide before image generation; keep notes off the slide image and out of the exact on-slide text
- assign visual_richness_role, illustration_intensity, creative_variance, and density_tier before generation
- define density_design before generation: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails
- add density through decision-relevant comparisons, benchmarks, units, denominators, assumptions, annotations, evidence strips, right rails, small multiples, and source cues; never through smaller type or decorative illustration detail
- keep decision-relevant numbers when they are legible and grouped; do not force a minimal-numbers rule
- use human-designed editorial/vector illustrations for chapter openers, turning points, complex systems, and final vision slides
- keep illustration subordinate: one clear focal motif, 2-3 supporting details, clean controlled linework, crisp silhouettes, restrained fills, a projection/viewpoint chosen from the claim, no rough sketch, no arbitrary pseudo-depth, and no glossy AI concept-art finish
- keep H1 28-32pt, subtitle 21-23pt grey, body 18pt equivalent
- if primary_guideline is ATOM, use ATOM header rules instead: H1 Charcoal Ink #2D332E, subtitle 30-32pt #4D544E, exact left vertical line, no blue H1
- if the ATOM guideline does not provide a more specific master, use the default exact ATOM header: 1672x941 basis; header_safe_area x=44 y=24 w=1584 h=136; vertical_line x=50 y=56 w=10 h=104 #0B2F5B; H1 x=84 y=28 w=1380 max_lines=1 size=30pt weight=700 line_height=1.14 #2D332E; subtitle x=84 y=72 w=1380 max_lines=1 size=30pt weight=400 line_height=1.12 #4D544E; visual_alignment line top flush with visible H1 glyph top and line bottom flush with subtitle lower visual edge; body_start_y=190; upper_right_clear_zone x=1450 y=24 w=178 h=124 empty
- make the slide feel human-crafted through priority, breathing room, and editorial rhythm
- let structure, spacing, rules, numbers, and typography carry hierarchy
- use the embedded ATOM design system's accent color structurally with a restrained area budget; for ATOM work, Deep Blue uses a 6-12% area budget and never appears as body text
- use Insight component only if it adds interpretation or decision weight and is compatible with the embedded ATOM design system
- if Honey is used in ATOM or compatible guidelines, use #F7EECF flat pale fill + #C49A2C 4-5px full-height left accent line + #2D332E text, one component maximum
- keep all Insight/message boxes flat solid fill only; no patterns, textures, gradients, motifs, icon wallpaper, or internal illustrations
- keep Honey quiet: no saturated yellow fill, no dark yellow message box, no large yellow area, and no Honey color variation across a deck
- Source only if traceable real sources are available
- final bitmap generation must use gpt-image-2
- if actual Codex built-in image generation is blocked, stop and report the blocker; do not create final images via code rendering or a user-key workaround
- after all generated PNGs pass QA, create a Google Slides roll-up unless the user asks for image files only: one full-bleed generated PNG per slide, same order, no extra overlays, and speaker notes inserted into the corresponding slide notes page
- place every literal string under `Exact text` in quotes and request ONLY those strings
- use "Draw" or "Create" for generation prompts, and "Edit" plus preservation language for repair prompts
- for healthcare, finance, law, or regulated domains, do not add market, clinical, regulatory, or compliance facts unless sources are provided or researched

Output:
1. canonical planning block
2. image_model: gpt-image-2
3. final image prompt
4. negative prompt
5. generation route and output files, or blocker
6. Google Slides roll-up status with speaker notes status for decks
7. post-generation audit checklist
```

## Text To Slide Structure Prompt

```text
Convert the following long text into a guideline-aware slide-image deck structure before writing any image prompt.

Process:
1. Extract the deck thesis and audience decision.
2. Create intake_map with source_span_id values for chapters, facts, quotes, assumptions, and uncertainties.
3. Choose one storyline frame: SCQA, problem-solution-evidence, past-present-future, market-problem-solution-moat, or investment-thesis-risk-milestones.
4. Draft slide-level action titles as standalone claims. No topic labels.
5. Build claim_backlog, evidence_ledger, source_ledger, appendix_candidates, and open_questions.
6. For each claim, assign supporting evidence, source policy, visual structure, visual richness role, illustration intensity, creative variance, density tier, and density risk.
7. Run a density design gate for each slide: set reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
8. Split any slide that has more than one claim, more than one dominant structure, more than three major regions, or would force body text below 18pt equivalent.
9. Combine adjacent slides only when claims repeat, the same comparison must be seen together, or the user explicitly requests a shorter deck.
10. Define deck_header_master_lock, footer baseline, Insight surface master, and repeated table/card/icon masters before image generation.
11. Read only the action titles in order and repair logical gaps before image generation.
12. Freeze quoted exact_text for every slide; do not leave copywriting to image generation.
13. Draft speaker_notes_text for every slide: talk track, evidence/assumption cue, source caveat when relevant, and transition cue.
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
    reader_question_answered:
    claim_type:
    evidence_items:
    evidence_strength:
    source_span_ids:
    source_policy:
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
    layout_archetype:
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
Embedded ATOM design system:
Output type:
Priority:
Design constraints:

Process:
1. Define the deck thesis.
2. Read and apply the embedded ATOM design system first; use bundled ATOM mechanics only where compatible.
3. Define each slide claim as one sentence.
4. Select one layout_archetype and one grid_mode for each slide.
5. Define the deck_header_master_lock with exact selected x/y/w/h/color/font values and carry it verbatim into every slide prompt.
6. Assign visual_richness_role, illustration_intensity, creative_variance, and density_tier for every slide, with a deck-level mix of human-designed editorial/vector illustrations, data visuals, small system scenes, icon evidence, and quiet tables.
7. Assign density_design for every slide: reader_mode, decision_question, information_units, density_levers, overload_controls, information_unit_budget, and density_guardrails.
8. Assign Insight components selectively across the deck: 8 slides usually need 2-3 total Insight components and 1-2 Honey components; 12 slides usually need 3-5 total Insight components and 2-3 Honey components, only when compatible with the embedded ATOM design system.
9. Vary dominant structures so the deck does not feel template-filled.
10. Mark restrained illustration candidates where the idea becomes more memorable or fresh without becoming a rough sketch or glossy hero illustration.
11. Flag slides that should split because density would force body below 18pt equivalent or create competing major regions.
12. Define source policy per slide: none / real source list.
13. Define deck-level master refs: header, footer baseline, Insight surface skeleton, table/card masters, icon circle sizes.
14. Draft speaker_notes_text for every slide before generation. Each note should support presentation delivery, not duplicate all visible text: short talk track, key evidence or assumption to mention, source caveat if needed, and transition to the next slide.
15. Run Guideline/Brand, Header Master, Layout, Typography, Visual Richness, Density, Content, and Deck gates.
```

## Screenshot Or Render Repair Prompt

```text
Inspect this screenshot/rendered slide before revising it.

Inventory:
- visible slide size/aspect ratio
- header anchor: vertical line, H1, subtitle, body gap
- footer baseline, source line, and table note microline
- dominant structure and major regions
- inferred grid_mode, column tracks, row tracks, separator_x, outer padding
- repeated objects and whether width/height/centers are equalized
- coordinate_inventory_1672 for visible major objects
- typography hierarchy and text overflow
- Deep Blue area and role
- brand accent/Insight use, variant, and whether it is a decision signal
- source hygiene and unsupported claims

Repair:
1. Keep the original claim if valid.
2. Rebuild the canonical planning block.
3. Fix grid drift before color or decorative changes.
4. Trim, split, or regrid crowded text; do not shrink body below 18pt equivalent.
5. Add useful density only through hierarchy, grouping, comparison, annotation, evidence strip, right rail, small multiples, or source cue.
6. Add, remove, or quiet Insight only after deciding the interpretation need.
7. Use generation_mode image_edit with model gpt-image-2 when a screenshot/reference image is available.
8. Use explicit preservation language: change only the failing element and keep layout, arrows, labels, spacing, brand colors, footer baseline, and surrounding objects unchanged.
9. Output image_model: gpt-image-2 and a revised final image prompt.
```

## Insight Decision Prompt

```text
Decide whether this slide needs an Insight component.

Evaluate:
- Does the table, diagram, or comparison need a one-sentence interpretation?
- Does the slide contain a strategic turning point, winning logic, or decision?
- Would the component become a second title or second hero?
- Is the deck underusing or overusing Insight components?
- Which choice is quietest and clearest under the embedded ATOM design system: none, outlined thesis, outlined bottom, brand surface, dark brand surface, or Honey surface when ATOM?
- If Honey is chosen, does it help the reader decide faster?
- Does the Honey component use the fixed pale treatment (#F7EECF fill, #C49A2C 4-5px left line, #2D332E text)?

Output:
- keep/remove
- variant: bottom-main / top-thesis / rail-wide / rail-tall / inline-pill / outlined thesis / outlined bottom / brand surface / dark brand surface / Honey surface when ATOM
- reason
- deck_count_check
- one-sentence component text if kept
- surface skeleton: geometry, height, radius, padding, left accent, background, text color
- alternative visual guidance if removed
```

## Balance Repair Prompt

```text
Repair this slide image prompt for text balance, grid fidelity, and visual hierarchy.

Priority:
1. Do not solve crowding by shrinking body text below 18pt equivalent.
2. Keep H1 28-32pt and subtitle 21-23pt grey.
3. Rebuild grid_mode, column_spans, row_tracks, column_tracks, separator_x, outer_padding, and shared_edges.
4. Add coordinate_inventory_1672 and master_components if missing.
5. Remove repeated explanation and weak labels.
6. Use headings, numbers, rules, spacing, and comparison axes for reading order.
7. Reduce equal-strength regions.
8. Add, change, or remove Insight component based on interpretation need and the embedded ATOM design system.
9. Split the slide if the claim or structure is overloaded.
10. Clean source policy.

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
- Embedded ATOM palette and type hierarchy are followed
- ATOM Honey is not decorative when used; it is a quiet pale signal, never a strong yellow block
- Primary accent is structural and not body text; for ATOM work, Deep Blue has a 6-12% area budget

Layout:
- layout_archetype, grid_mode, component_inventory exist
- coordinate_inventory_1672 and master_components exist
- row_tracks, column_tracks, equalized_groups, shared_edges exist
- header/footer anchors are fixed
- repeated elements are equalized
- rail and Insight do not compete

Typography:
- H1 28-32pt, default 30pt
- long Japanese H1 uses 28-30pt; short mixed titles may use 32pt
- subtitle 21-23pt grey
- body readable at 18pt equivalent
- weights stay within 400/600/700

Content:
- one claim
- title is a claim, subtitle supports
- density_design answers a clear decision_question and does not rely on smaller type or decorative detail
- information units are grouped and each added layer improves the claim
- Insight adds interpretation, not repetition
- Source is optional and real-source only
- source_line and table_note_microline are separate
- no unsupported facts

Model:
- final bitmap generation uses gpt-image-2
- image size is valid for gpt-image-2 and not direct 1920x1080
- background is opaque or auto, not transparent
- prompt uses exact quoted text and no extra text
- output text was audited after generation

Deck:
- layouts vary naturally
- visible priority, rhythm, and breathing room
- no mechanical card-only repetition
- Insight components are selective and compatible with the embedded ATOM design system
- Google Slides roll-up contains exactly one full-bleed generated PNG per slide, in order
- speaker notes exist on every slide and match the slide claim, evidence, caveats, and transition

For every fail:
1. Explain the issue.
2. Choose trim, split, regrid, quiet hierarchy, add Insight, remove Insight, or source cleanup.
3. Provide the revised prompt section.
4. Re-audit.
```
