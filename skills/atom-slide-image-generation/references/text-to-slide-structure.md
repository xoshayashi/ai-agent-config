# Text To Slide Structure

Use this reference when the input is a long memo, equity story, research note, transcript, or dense bullet dump. Do not send long prose directly to image generation. Convert it into a deck structure first.

## Contents

- Principles
- Workflow
- Density Design Best Practices
- Output Fields
- Source Notes

## Principles

- One slide must carry one standalone claim. If the page needs two claims, split it.
- One slide must use one dominant structure. A table, comparison axis, flow, roadmap, matrix, loop, or rail can dominate, but do not make two structures compete.
- Use action titles: the H1 should state the takeaway, not just name the topic.
- Build the storyline before designing slides. Read only the action titles in order; they should form the deck's argument without body text.
- Put the conclusion or recommendation early enough for an executive/investor reader to understand the point before details.
- Every slide needs a role in the story: set context, prove urgency, explain solution, show moat, size market, prove traction/plan, handle risk, or close the thesis.
- Treat claim, evidence, visual, and source as separate jobs: claim says `so what`, evidence says `why believe`, visual says `how to see`, and source says `can we trust it`.
- Map each claim to evidence and source policy before image prompting. Unsupported facts are either removed from the slide or marked as research/source needs.
- Convert prose into visual grammar: comparison, table, flow, roadmap, loop, matrix, KPI strip, architecture stack, or signature visual. Avoid prose boxes as the default.
- Use the expanded layout palette positively: full-field, left-main/right-rail, right-main/left-context, balanced diptych, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families are all available when they clarify the claim.
- Create `layout_diversity_plan` before final prompts. Let repeated layouts serve deliberate comparison, and let composition change when the claim role, evidence type, time horizon, or decision question changes.
- Apply `layout_rotation_guard` during deck review so the sequence feels intentionally edited rather than locked to a single left-wide/right-narrow habit.
- Plan visual richness before prompt writing, while keeping illustration subordinate to the argument. Do not let a long deck collapse into text/table slides, but do not overcorrect into glossy AI-looking hero art or rough sketch lines. Assign restrained human-designed editorial illustrations to chapter openers, turning points, and final vision slides; assign small diagram-embedded illustrations or data visuals to evidence and strategy slides; reserve quiet tables for truly tabular arguments.
- Apply visual design quality traits as design treatment only: calm light base, compact fixed header, thin rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, and intentional canvas occupancy. Do not change slide count, claim order, or storyline solely to match a visual style.
- Set illustration intensity before prompt writing: `0_none`, `1_marginal`, `2_integrated`, or `3_restrained_signature`. Use `3_restrained_signature` sparingly. Most slides should use `1_marginal` or `2_integrated`, where the chart, table, matrix, or roadmap remains primary.
- Set `creative_variance` before prompt writing when the user asks for higher temperature, freshness, or surprise. Use `low`, `medium`, or `high`. High variance changes composition choices, viewpoint, crop, visual metaphor, and layout rhythm; it does not relax brand rules, exact text, source policy, header master, or readability.
- Prefer human-designed editorial/vector illustration over generated-looking concept art or rough hand-drawn sketch: clean controlled strokes, crisp silhouettes, intentional simplification, restrained fills, clear figure-ground separation, a clear focal motif, and only useful supporting details. Do not hard-code one visual form for every slide; choose the projection, viewpoint, abstraction level, and motif from the slide claim. Avoid prompt cues such as rough doodle, messy sketch, luminous, cinematic, heroic robot, futuristic city, abstract 3D, dramatic glow, photoreal, ultra-detailed, decorative trapezoid planes, isometric boxes, tilted floors, and pseudo-3D perspective.
- For humanoid/robot stories, do not default to a full-body robot hero or futuristic skyline. Use small interaction details, system cues, partial figures, or embedded operational motifs unless the slide is explicitly selected as a rare restrained signature moment.
- Set density intentionally. A strategic deck can be slightly dense, but density should mean more decision-relevant information per view, not more objects or smaller type. Use structured layers, rails, evidence strips, mini charts, comparison baselines, and short labels while keeping body text at 18pt equivalent or larger.
- Do not impose a default numeric cap. Preserve decision-relevant sourced or explicitly assumed numbers when they help comparison, sizing, prioritization, credibility, or decision-making.
- Message boxes and Insight surfaces should use a flat solid fill only. Do not add patterns, textures, gradients, motifs, icon wallpaper, or internal illustration inside message boxes.
- Apply `message_box_scale_lock`: Insight/message-box components are compact interpretation surfaces, not display surfaces. Prefer one short judgment sentence, one line when possible and two lines maximum; trim or move explanation to notes instead of enlarging the box.
- Apply `message_box_text_size_lock`: Insight/message-box text defaults to 20-24pt, uses 24-26pt only by exception, stays at least 6pt smaller than H1, and must not become a second title or compete with subtitle.
- Lock deck-level header and footer masters before slide design. The header is the lowest-freedom component: every slide must reuse the same visible header elements, exact selected geometry, title color, subtitle size/color, visual alignment rule, body_start_y, and clear zone. Header fields must be exact values in final prompts, not ranges or loose descriptions.
- Apply `header_line_top_rule`: the left vertical line top must sit at or slightly below the first visible H1 glyph top; upward protrusion is a blocker. If it fails, repair the line x/y/h before touching H1.
- Apply `header_footer_text_color_lock`: H1 `#2D332E`, subtitle `#4D544E`, footer/source/table-note text `#6E756E`. Do not use Deep Blue, Honey, yellow, or arbitrary gray for header/footer text.
- Define `deck_tone_master_lock` before image generation and check generated images for whole-deck tone consistency before PPTX or Google Slides roll-up.
- After image generation, run `post_generation_design_balance_check` on actual PNGs: whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, and header integrity.
- Use `visual_asset_judgment`: add illustration/icons only when they help understanding, memory, comparison, or navigation; do not add them by quota.
- Keep long-text overflow outside the slide: use `claim_backlog`, `evidence_ledger`, and `appendix_candidates` rather than cramming all extracted points into the canvas.
- Reduce prose before generation. Keep H1, subtitle, short labels, decision-relevant numbers, and one Insight sentence when needed; remove only unsupported, redundant, unreadable, or decorative numbers.
- Freeze display text before generation. Put all on-slide strings in quoted `exact_text` fields; do not let image generation invent or rewrite slide copy.
- Draft speaker notes as part of slide structure, before image generation. Notes should help the presenter say the argument clearly without adding unsupported claims: concise talk track, evidence/assumption cue, source caveat when needed, and transition cue.
- Create a text budget per slide. If the visual would need dense paragraphs, split the slide or move detail to notes.
- Use a pilot-first process for image generation: generate 1-2 representative slides, audit quality, then expand.

## Workflow

1. **Intake**
   - Identify audience, decision, intended use, language, required source strictness, and output count flexibility.
   - Use the embedded ATOM design system in SKILL.md as the source of style and component truth.
   - Preserve source URLs and source names separately from the narrative.
   - Apply `source_line_lock`: render `Source: ...` when traceable sources exist; use `source_line: none` only when no traceable source exists.
   - Split the input into chapters, paragraphs, data points, quotes, assumptions, and uncertainties. Assign stable `source_span_id` values when source tracing matters.

2. **Storyline Frame**
   - Choose one frame:
     - `SCQA`: situation, complication, question, answer.
     - `problem-solution-evidence`: pain, solution, proof, next step.
     - `market-problem-solution-moat`: why now, unmet need, product, moat, economics.
     - `investment-thesis-risk-milestones`: thesis, upside, proof, risks, milestones.
     - `past-present-future`: historical shift, current bottleneck, future state.

3. **Action Title Draft**
   - Draft one sentence per slide.
   - Each sentence should answer "so what?".
   - Prefer concrete nouns, active verbs, and useful sourced numbers.
   - Reject topic labels such as `Market`, `Solution`, `Roadmap`, or `Moat` unless they are part of a full claim.

4. **Claim To Evidence Map**
   - For each slide, list evidence type: sourced fact, user assumption, analogy, forecast, operating model, or strategic interpretation.
   - Keep `claim_backlog`, `evidence_ledger`, `source_ledger`, `appendix_candidates`, and `open_questions` separate from final slide text.
   - Decide `source_line`: `Source: ...` with real traceable source names / `none` only when no traceable source exists / research needed.
   - Do not drop real source names to reduce visual density; shorten or group source names instead.
   - Do not place internal process notes, upload filenames, or draft provenance in Source.

5. **Visual Structure Assignment**
   - Pick one dominant structure per slide:
     - chronological shift -> timeline / sequence / staged flow
     - market or labor statistics -> KPI strip / trend table
     - competing options -> comparison table / 2x2 matrix
     - product/strategy system -> architecture flow / stack
     - compounding asset -> loop
     - rollout plan -> phase roadmap
     - use cases -> grid/table
     - vision or chapter opener -> signature visual
   - Assign `layout_archetype`, `layout_family`, `layout_diversity_plan`, `layout_rotation_guard`, and `grid_mode` before writing final on-slide text.
   - Assign `visual_richness_role`: `restrained_signature_illustration`, `diagram_embedded_illustration`, `data_visual`, `icon_evidence`, or `quiet_table`.
   - Assign `illustration_intensity`: `0_none`, `1_marginal`, `2_integrated`, or `3_restrained_signature`.
   - Assign `creative_variance`: `low`, `medium`, or `high`.
   - Assign `human_designed_illustration_style` for slides where the audience should remember a clear designed illustration, not just a metric.
   - If illustration competes with the chart/diagram, reduce intensity or split the slide.

6. **Density And Split Gate**
   - Assign `density_tier`: `T1_sparse`, `T2_balanced`, `T3_dense`, or `T4_appendix_dense`.
   - Define `reader_mode`, `decision_question`, `information_units`, `density_levers`, and `overload_controls`.
   - For `T3_dense`, define density layers explicitly: main figure/table, evidence strip, rail/legend, comparison baseline, annotations, source cues, and optional Insight. Keep paragraph text out.
   - Split when a slide has multiple claims, mixed structures, more than 3 major regions, too many source facts, or text that would fall below 18pt equivalent.
   - Combine adjacent slides only when they repeat the same claim, depend on the same comparison, or require one shared decision frame.

7. **Deck Master Gate**
   - Define `deck_header_master_lock`, `header_footer_text_color_lock`, `footer_anchor_baseline`, `insight_surface_master`, and repeated table/card/icon masters before generating a deck.
   - Fail any final prompt whose `deck_header_master_lock` is range-only, missing x/y/w/h/color/font_family/font values, or uses any font family other than Noto Sans JP for visible text.
   - For ATOM-style guidelines, fail any plan whose H1 becomes Deep Blue, whose left vertical line is missing, whose left vertical line protrudes above the visible H1 glyph top, whose subtitle size/color drifts, whose body starts above the locked `body_start_y`, or whose header clear zone is filled.

8. **Speaker Notes Plan**
   - Draft `speaker_notes_text` for every deck slide before image prompting.
   - Use the deck language unless the user specifies otherwise.
   - Notes should include: the spoken claim in plain language, the evidence or assumption to mention, source caveat or confidence level when relevant, and a transition to the next slide.
   - Keep notes out of `exact_text` and out of the image prompt's on-slide text. Speaker notes belong in PPTX or Google Slides notes pages after image generation.
   - Do not add unsupported facts, invented sources, internal prompt notes, file paths, or production-route language to speaker notes.

9. **Image Prompt Handoff**
   - For each slide, output: action title, subtitle, exact text, visual structure, visual richness role, illustration intensity, density tier, coordinates, source policy, Insight decision, and negative prompt.
   - Block generation until `layout_archetype`, `layout_family`, `layout_diversity_plan`, `layout_rotation_guard`, `grid_mode`, `visual_richness_role`, `illustration_intensity`, `creative_variance`, `density_tier`, `source_policy`, `exact_text`, `speaker_notes_text`, `deck_header_master_lock`, `header_line_top_rule`, and `coordinate_inventory_1672` are resolved.
   - Generate pilot slides first for any deck over 3 slides.

## Density Design Best Practices

Use this pass before slide-level prompts. Density is a design decision, not a count target.

### Density Ladder

- `T1_sparse`: opener, chapter turn, or final vision. One claim, one strong visual or data point, optional subtitle. No body paragraph.
- `T2_balanced`: default strategy page. One main figure/table/diagram plus 2-4 labels, one small context cue, and Source footer when traceable sources exist.
- `T3_dense`: investor/evidence page. One main structure plus a KPI strip, right rail or evidence strip, chart annotations, units, benchmark/context column, and source cue.
- `T4_appendix_dense`: reference page only when accepted. Table or small multiples can dominate, but visual grouping and typography must still be readable.

### Density Gate

For every slide, answer:

- `reader_mode`: scan, read, or reference. Scan pages need fewer words; reference pages can carry more rows if grouped.
- `decision_question`: what should be answerable without narration?
- `information_units`: claim, context, comparison, trend, mechanism, risk, implication, assumption, source.
- `density_levers`: which added layer improves the claim: denominator, time horizon, benchmark, segmentation, scenario, assumption, source, counterpoint, or implication.
- `overload_controls`: one dominant structure, max three major regions, grouped labels, body at 18pt equivalent or larger, and no illustration detail doing the job of evidence.

### Useful Density Levers

- KPI strip above or beside the main structure.
- Right interpretation rail that explains the implication of the chart/table.
- Evidence strip under the main figure with 2-4 sourced facts or assumptions.
- Small multiples for comparable cases, phases, segments, or scenarios.
- Table row grouping, column grouping, and visible unit/denominator labels.
- Enough numeric detail to make the comparison credible, as long as labels remain legible and grouped.
- Micro annotations on charts or flows instead of separate prose boxes.
- Source cue and table note baseline separated from interpretation text.

### Failure Signs

- Body text would need to fall below 18pt equivalent.
- Four or more unrelated major regions compete.
- Several charts have equal visual weight without a clear reading path.
- Labels are ungrouped or repeat the title.
- Illustration becomes the density source instead of evidence, structure, or annotation.
- A slide is combined only because fewer pages feels cleaner.

## Output Fields

```text
deck_thesis:
audience_decision:
primary_guideline:
guideline_priority:
brand_style_notes:
storyline_frame:
section_map:
claim_backlog:
evidence_ledger:
source_ledger:
appendix_candidates:
open_questions:
slide_id:
chapter:
action_title:
reader_question_answered:
claim_type:
supporting_evidence:
evidence_strength:
source_span_ids:
source_policy:
source_line_lock:
source_line:
source_urls:
assumptions:
speaker_notes_text:
speaker_notes_source_cues:
speaker_notes_transition:
visual_structure:
visual_richness_role:
signature_visual_plan:
illustration_intensity:
human_designed_illustration_style:
creative_variance:
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
  coordinate_basis:
  header_safe_area:
  vertical_line:
  header_line_top_rule:
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
  forbidden_text_colors: Deep Blue, Honey, yellow, arbitrary gray
message_box_scale_lock:
message_box_text_size_lock:
deck_tone_master_lock:
post_generation_design_balance_check:
whitespace_occupancy_balance_status:
typography_balance_status:
color_consistency_status:
outer_padding_consistency_status:
header_integrity_status:
visual_design_quality_traits:
deep_blue_usage_lock:
visual_asset_judgment:
layout_archetype:
layout_family:
layout_diversity_plan:
layout_rotation_guard:
layout_sequence_table:
grid_mode:
exact_text:
exact_text_budget:
insight_decision:
data_to_render:
density_risk:
split_merge_decision:
prompt_text_budget:
image_prompt_ready:
pptx_rollup_plan:
pre_package_image_review:
image_review_matrix:
deck_consistency_matrix:
unresolved_items:
```

## Source Notes

These practices synthesize common executive-presentation guidance:

- Source footers are part of credibility, not decoration. Render `Source: ...` when traceable sources exist; use `source_line: none` only when no traceable source exists, and shorten or group names instead of deleting them for density.

- IBCS SUCCESS emphasizes saying a clear message, structuring content, simplifying clutter, and condensing information into high-density business communication: `https://www.ibcs.com/IBCS/`
- Assertion-evidence guidance supports a claim headline plus visual proof instead of dense prose: `https://www.writing.engr.psu.edu/guidelines_AE_slides.pdf`
- PLOS "Ten simple rules for effective presentation slides" emphasizes one message, less unnecessary information, and cognitive-load-aware slide construction: `https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009554`
- Purdue OWL data visualization presentation guidance emphasizes chart choice, audience fit, clear labels, and source context: `https://owl.purdue.edu/owl/general_writing/visual_rhetoric/data_visualization/data_visualization_presentation.html`
- Investor pitch guidance favors legible, simple, obvious slides with a small number of memorable points: `https://www.ycombinator.com/blog/how-to-design-a-better-pitch-deck/`
