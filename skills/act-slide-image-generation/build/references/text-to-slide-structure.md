# Text To Slide Structure

Use this reference when the input is a long memo, strategy narrative, research note, transcript, operating brief, policy note, technical explainer, education material, internal report, or dense bullet dump. Do not send long prose directly to image generation. Convert it into a deck structure first.

## Contents

- Principles
- Workflow
- Density Design Best Practices
- Output Fields
- Source Notes

## Principles

- One slide must carry one standalone message. If the page needs two messages, split it.
- One slide must use one dominant structure. A table, comparison axis, flow, roadmap, matrix, loop, or supporting context region can dominate, but do not make two structures compete.
- Use action titles: the H1 should state the takeaway, not just name the topic.
- Build the storyline before designing slides. Read only the action titles in order; they should form the deck's argument without body text.
- Start with a high-signal opening thesis, not a title-only first slide. The opener can use the deck's main phrase, but it should also carry the core thesis, 2-4 proof/tension points, a visible market-shift / matrix / causal-map / wedge structure, and a bridge into the next section.
- Put the conclusion or recommendation early enough for an intended decision-maker to understand the point before details.
- Every slide needs a role in the story: set context, prove urgency, explain a solution, compare options, show differentiation, summarize evidence, explain operations, teach a concept, size impact, prove traction/plan, handle risk, or close the thesis.
- Treat message, evidence, visual, and source as separate jobs: message says `so what`, evidence says `why believe`, visual says `how to see`, and source says `can we trust it`.
- Map each message to evidence and source policy before image prompting. Unsupported facts are either removed from the slide or marked as research/source needs.
- Convert prose into visual grammar: comparison, table, flow, roadmap, loop, matrix, KPI strip, architecture stack, or signature visual. Avoid prose boxes as the default.
- Use the expanded layout palette positively: full-field, asymmetric main/supporting-context, balanced diptych, top-bottom, center-hub, process, matrix, small-multiple, swimlane, and staircase families are all available when they clarify the message.
- Create `layout_diversity_plan` before final prompts. Let repeated layouts serve deliberate comparison, and let composition change when the message role, evidence type, time horizon, or decision question changes.
- Apply `layout_rotation_guard` during deck review so the sequence feels intentionally edited around the argument instead of locked to one repeated width habit.
- Apply `density_lift_lock`: raise useful information density during both slide-structure planning and slide-image prompting. Useful density means more decision-relevant comparison, evidence, units, assumptions, annotations, and source cues with one clear reading path.
- Apply `impact_clarity_density_gate`: every slide should earn attention quickly, explain itself without narration, stay visually simple, and still carry enough decision-relevant evidence. If a slide feels flat, vague, thin, or cluttered, repair the message, evidence, and dominant structure before image prompting.
- Apply `message_sharpness_lock`: rewrite each action title until it contains a clear actor/topic, change/tension, and implication. Avoid generic topic labels, vague positive claims, and slogans that do not say what changed or why it matters.
- Apply `evidence_compression_ladder`: compress evidence into the smallest structure that still proves the message: one sharp number, ranked comparison, before/after delta, driver tree, causal chain, 2x2, mini table, or evidence strip. Use speaker notes or appendix candidates for detail that does not change the slide decision.
- Apply `structure_choice_bias`: gently prefer structured presentation logic when it clarifies the message, without forcing it on every slide.
- Apply `structured_density_bias`: add one or two useful evidence layers, labels, drivers, or comparison cues when the slide has room and the reader benefits.
- Use structured presentation patterns as an option, not a quota: issue trees, driver trees, 2x2 matrices, value chains, funnels, waterfalls, KPI bridges, decision tables, before/after bridges, and hypothesis-evidence-implication rows are available when they make the argument easier to scan.
- Apply `structure_first_visual_mix`: lead with charts, tables, matrices, flows, maps, comparison axes, and evidence strips when they carry the argument; use illustration as support, memory, or navigation.
- Apply `imageability_lock`: every slide prompt must name a concrete visual anchor, observable scene or object, viewpoint/crop, and 2-4 specific visual details before generation.
- Apply `visible_text_only_lock` and `render_contract_lock`: separate on-slide strings from planning, workflow, audit, speaker-note, file-path, and packaging metadata; only quoted `exact_text` can be visible.
- Apply `prompt_order_lock`: final image prompts should be ordered as drawing action, exact visible text, canvas/style system, fixed components, layout/reading path, main visual/structure details, optional Insight, then focused blockers.
- Apply `edit_scope_lock`: repair prompts should be single-delta (`issue_observed`, `change_only`, `preserve`, `re_check`) and avoid global restyle unless explicitly required.
- Apply `editorial_polish_repair_loop`: raise slide quality with a stronger visual anchor, more specific evidence objects, tighter component geometry, clearer focal hierarchy, and a composed editorial rhythm.
- Apply `visual_subject_open_set`: keep visual subject choices open; select the clearest concrete subject from the slide message, evidence, and audience context.
- Apply `message_led_composition_lock`: choose the structure, viewpoint, region balance, and focal relationship from the slide message before adding supporting elements.
- Apply `region_balance_policy`: choose the relative weight of main, supporting, and optional context regions from the slide message, evidence shape, reading path, and body silhouette.
- Apply `composition_fit_plan`: set the main visual field, supporting regions, whitespace role, and Insight footprint before generation so the canvas has deliberate occupancy and breathing room.
- Apply `secondary_region_integrity_lock`: in split or auxiliary-region layouts, make the secondary region a complete decision panel with matched vertical rhythm, enough useful content, and top/bottom alignment to the main field.
- Apply `body_silhouette_lock`: plan the body as one closed visual block by aligning outer edges, lower edges, and footer clearance across main and secondary regions.
- Plan visual richness before prompt writing, with the argument-carrying structure as the reader's path. Long decks can stay varied through data visuals, matrices, flows, evidence strips, and small diagram-embedded illustrations; restrained human-designed editorial illustrations work best on chapter openers, turning points, and final vision slides, while quiet tables serve truly tabular arguments.
- Apply visual design quality traits as design treatment only: near-white warm base, compact fixed header, thin rules, pale equalized cards/tables, restrained line icons, small explanatory technical line drawings, and intentional canvas occupancy. Do not change slide count, message order, or storyline solely to match a visual style.
- Apply `near_white_slide_base_lock`: use `#FFFDFC` as the default ACT slide canvas, with `#FAFAF7` only as a subtle warm off-white tint; keep `#F7FBF9` for panels/cards, not the full slide background, and avoid darker cream/beige page bases.
- Apply `deck_tone_signature_lock`: keep one material system across the deck for base, typography, rule weight, card/table surfaces, icon stroke, illustration linework, accent budget, density rhythm, Insight treatment, and Source behavior. Vary message-led layouts without changing the deck's visual language.
- Apply `illustration_tone_lock`: keep all illustrations in one deck on the same editorial vector system.
- Define `illustration_style_sheet` before prompt writing and reuse it across the deck: domain-matched flat 2D editorial/vector scenes, with objects selected from the brief, audience context, and slide message. Optional motifs include people, devices, documents, evidence artifacts, UI panels, operational objects, handoff points, map routes, and small icon badges; keep soft pale mint or warm gray fills, Petrol and charcoal linework, restrained Honey highlights, consistent 2-3px stroke, crop, facial detail, body proportion, and fill opacity.
- Set illustration intensity before prompt writing: `0_none`, `1_marginal`, `2_integrated`, or `3_restrained_signature`. Use `3_restrained_signature` sparingly. Most slides should use `1_marginal` or `2_integrated`, where the chart, table, matrix, or roadmap remains primary.
- Set `creative_variance` before prompt writing when the user asks for higher temperature, freshness, or surprise. Use `low`, `medium`, or `high`. High variance changes composition choices, viewpoint, crop, visual metaphor, and layout rhythm; it does not relax brand rules, exact text, source policy, header master, or readability.
- Prefer human-designed editorial/vector illustration over generated-looking concept art or rough hand-drawn sketch: clean controlled strokes, crisp silhouettes, intentional simplification, restrained fills, clear figure-ground separation, a clear focal motif, and only useful supporting details. Keep the projection, viewpoint, abstraction level, and motif message-led.
- Set density intentionally. A strategic deck can be slightly dense, but density should mean more decision-relevant information per view, not more objects or smaller type. Use structured layers, supporting context regions, evidence strips, mini charts, comparison baselines, and short labels while keeping body text at 18pt equivalent or larger.
- Do not impose a default numeric cap. Preserve decision-relevant sourced or explicitly assumed numbers when they help comparison, sizing, prioritization, credibility, or decision-making.
- Apply `exact_text_fidelity_lock`: freeze every visible H1, subtitle, label, number, source string, and optional Insight as quoted `exact_text`; generated copy that is missing, invented, garbled, duplicated, or rewritten is repair_required.
- Apply `revised_prompt_review_lock`: when the image tool exposes a revised or rewritten prompt, compare it against `exact_text`, source policy, header master, and visible/non-visible boundaries before approving the PNG.
- Apply `chart_semantic_integrity_lock`: chart/table/matrix/flow/map structures should explain what is compared, which unit/denominator/period applies, and how rows, columns, axes, arrows, or legends connect; decorative pseudo-data is a major issue.
- Apply `thumbnail_legibility_lock` and `reading_path_lock`: the main claim, focal structure, region boundaries, and key numbers should remain understandable in slide-sorter/contact-sheet review, with a clear path from H1 to main visual, evidence/context, optional Insight, and Source.
- Apply `insight_absence_default_lock`: start each slide with `insight_decision: none`; keep no message box unless the slide has a specific interpretation gap, decision signal, or reading bridge that the title, visual structure, and labels cannot already carry.
- Apply `insight_justification_required`: when an Insight/message-box is kept, record the exact reason, the non-redundant sentence, and why it improves reading speed or decision clarity. If the reason is weak, repetitive, decorative, or simply fills space, remove the component.
- Message boxes and Insight surfaces are optional, not default. Use them only when a one-sentence interpretation, decision signal, or reading bridge genuinely helps; many slides should use no message box.
- Message boxes and Insight surfaces should use a flat solid fill only. Do not add patterns, textures, gradients, motifs, icon wallpaper, dashed outlines, or internal illustration inside message boxes.
- Apply `message_box_scale_lock`: Insight/message-box components are compact interpretation surfaces sized after the main content area, not display surfaces. A lower, quieter height is welcome when it gives the body, figure, table, or diagram more useful room while the sentence remains legible and optically centered. For bottom Insight bars, target 72-96px height on the 1672 basis and allow up to 108px only for a necessary two-line sentence. Prefer one short judgment sentence, one line when possible and two lines maximum; trim, move explanation to notes/body, or remove the component instead of enlarging the box.
- Apply `content_area_priority_lock`: allocate height to the body, figure, table, or diagram first; size any optional Insight/message-box from the remaining calculated space so it supports rather than compresses the main content area.
- Apply `message_box_text_size_lock`: Insight/message-box text defaults to 20-24pt, uses 24-26pt only by exception, stays at least 6pt smaller than H1, and must not become a second title or compete with subtitle.
- Apply `message_box_compactness_blocker_lock`: an Insight/message-box that dominates the slide, behaves like a banner, spans beyond the interpreted region, grows tall to carry prose, or compensates for layout imbalance is a blocker. A lower, quieter box that returns space to the body, figure, table, or diagram is preferred when the sentence remains legible and optically centered.
- Apply `message_box_text_alignment_lock`: Insight/message-box text sits at the optical center of the surface, both horizontally and vertically, using balanced padding and a centered line box.
- Apply `insight_surface_placement_lock`: decide the Insight footprint with the body silhouette and footer rhythm. Bottom Insight variants should bridge the body content and Source footer area with clear breathing room, centered to the interpreted region or full body block, while Source remains separate on its invisible baseline. Honey is preferred only for this bottom-bar decision-signal role, not for main content cards.
- Apply `honey_selective_signal_lock`: Honey starts as absent. Use Honey only after the slide passes `insight_justification_required`, and only when a quiet bottom decision signal is more helpful than no component or a neutral outlined treatment. Honey is never a default message-box color.
- Apply `honey_justification_required`: when Honey is selected, record why the pale Honey treatment improves decision clarity without overpowering the body. If it is decorative, repeats the title, fills empty space, or becomes a yellow card/banner, remove Honey or remove the Insight.
- Apply `max_text_size_lock`: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
- Lock deck-level header and footer masters before slide design. Apply `header_identity_lock`: the header is always the same compact left vertical line + H1 + subtitle system, never a slide-specific decoration surface. Every slide must reuse the same visible header elements, exact selected geometry, title color, subtitle size/color, visual alignment rule, body_start_y, and clear zone. Header fields must be exact values in final prompts, not ranges or loose descriptions. Do not render a separate ACT wordmark, logo, title kicker, badge, or brand label in the header unless the user explicitly supplies it as visible exact_text.
- Apply `header_line_top_rule`: the left vertical line is the approved header-block anchor, not a short title tick. On the 1672x941 basis, use `vertical_line x=50 y=40 w=10 h=120 #008A80` unless a newer embedded master is supplied. Its top must never sit above the first visible H1 glyph/title top; align it with the title top or place it 0-6px below. Any upward protrusion, page-top floating, clipping outside `header_safe_area`, detachment from H1/subtitle, or body intrusion is a blocker. If it fails, repair the line x/y/h before touching H1.
- Apply `header_integrity_blocker_lock`: malformed, missing, oversized, recolored, right-decorated, or intruded headers are blockers; repair header identity before other visual polish.
- Apply `header_footer_text_color_lock`: H1 `#2D332E`, subtitle `#4D544E`, footer/source/table-note text `#6E756E`. Do not use Petrol, Honey, yellow, or arbitrary gray for header/footer text.
- Define `deck_tone_master_lock` before image generation and check generated images for whole-deck tone consistency before PPTX/PDF packaging.
- Check `illustration_consistency_status` after image generation by comparing first, middle, and last thirds for stroke weight, fill opacity, face/detail level, object treatment, and illustration density.
- After image generation, run `post_generation_design_balance_check` on actual PNGs: whitespace/occupancy balance, typography size/weight balance, color consistency, outer padding consistency, and header integrity.
- Use `visual_asset_judgment`: add illustration/icons only when they help understanding, memory, comparison, or navigation; do not add them by quota.
- Keep long-text overflow outside the slide: use `message_backlog`, `evidence_ledger`, and `appendix_candidates` rather than cramming all extracted points into the canvas.
- Reduce prose before generation. Keep H1, subtitle, short labels, decision-relevant numbers, and one Insight sentence when needed; remove only unsupported, redundant, unreadable, or decorative numbers.
- Freeze display text before generation. Put all on-slide strings in quoted `exact_text` fields; do not let image generation invent or rewrite slide copy.
- Draft speaker notes as part of slide structure, before image generation. Apply `speaker_notes_depth_lock`: notes should help the presenter say the argument clearly without adding unsupported messages, using 4-7 substantive Japanese sentences or roughly 180-320 Japanese chars per slide unless the user requests brief notes. Include framing, 2-3 evidence/assumption cues, implication, source caveat when needed, and transition cue.
- Create a text budget per slide. If the visual would need dense paragraphs, split the slide or move detail to notes.
- Use a pilot-first process for image generation: generate 1-2 representative slides, audit quality, then expand.

## Workflow

1. **Intake**
   - Identify audience, decision, intended use, language, required source strictness, and output count flexibility.
   - Use the embedded ACT design system in SKILL.md as the source of style and component truth.
   - Preserve source URLs and source names separately from the narrative.
   - Apply `source_real_only_lock`: render Source only for real traceable external/provided sources; if no real source exists, set `source_line: none` and draw no Source footer.
   - Apply `source_placeholder_blocklist`: never use brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, working assumptions, upload names, or draft provenance as Source text.
   - Apply `output_artifact_mastering_lock`: approved generated PNGs live once in `slides_final/`; `slides_package/` holds PPTX, notes, manifest, and metadata only; `render_check/pdf_pages/` is disposable render QA output.
   - Apply `nonconforming_existing_png_regeneration_lock`: if existing/source PNGs are `1672x941` or any non-approved package size, do not treat the package-script rejection as final blockage and do not convert, upscale, HTML-render, API-render, or locally redraw them. Reuse the approved slide specification and generate new `2048x1152` `slides_final/` masters with Codex built-in gpt-image-2, then review and package those generated masters.
   - Apply `pdf_export_source_lock`: create PDF outputs from `slides_final/` master PNGs; do not use `render_check/pdf_pages/` as a source image folder.
   - Apply `contact_sheet_mastering_lock`: keep one retained `render_check/contact_sheet_review.png` by default; use one comparison sheet or render diff report only when delivery/render QA needs it.
   - Apply `image_generation_tool_lock`, `script_boundary_lock`, `credential_setup_blocker`, and `progress_update_route_lock`: final PNG pixels come from Codex built-in image generation; prompt/package scripts may scaffold, validate, or wrap approved artifacts, but never render, draw, screenshot, export, simulate, replace slide images, inspect local setup, probe save routes, or narrate setup checks as prerequisites.
   - Apply `source_line_lock`: render `Source: ...` when traceable sources exist; use `source_line: none` only when no traceable source exists.
   - Apply `source_separator_lock`: Source is text-only; no gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline may appear above, below, behind, or adjacent to Source.
   - Split the input into chapters, paragraphs, data points, quotes, assumptions, and uncertainties. Assign stable `source_span_id` values when source tracing matters.

2. **Storyline Frame**
   - Choose one frame:
     - `SCQA`: situation, complication, question, answer.
     - `problem-solution-evidence`: pain, solution, proof, next step.
     - `context-problem-solution-differentiation`: why now, unmet need, product, differentiation, economics.
     - `thesis-risk-milestones`: thesis, upside, proof, risks, milestones.
     - `past-present-future`: historical shift, current bottleneck, future state.

3. **Action Title Draft**
   - Draft one sentence per slide.
   - Each sentence should answer "so what?".
   - Prefer concrete nouns, active verbs, and useful sourced numbers.
   - Reject topic labels such as `Market`, `Solution`, `Roadmap`, or `Differentiation` unless they are part of a full message.
   - Apply `message_sharpness_lock`: every action title should name what changed, who/what is affected, and why the reader should care. Repair titles that read like a section label, vague benefit, or slogan.
   - Set slide 1 as `opening_thesis_slide` and record `first_slide_not_title_only: true`.
   - Run `opening_density_gate`: repair slide 1 before generation if it only contains a brand/name/slogan, lacks proof or tension, lacks a real visual structure, or does not bridge into the deck.

4. **Message To Evidence Map**
   - For each slide, list evidence type: sourced fact, user assumption, analogy, forecast, operating model, or strategic interpretation.
   - Keep `message_backlog`, `evidence_ledger`, `source_ledger`, `appendix_candidates`, and `open_questions` separate from final slide text.
   - Decide `source_line`: `Source: ...` with real traceable source names / `none` only when no traceable source exists / research needed.
   - Do not drop real source names to reduce visual density; shorten or group source names instead.
   - Do not place internal process notes, upload filenames, draft provenance, brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, or working assumptions in Source.
   - Keep package and render-check artifacts pointing at `slides_final/` master PNGs; do not duplicate the same final PNG set into `slides_package/` or `render_check/pdf_pages/`. PDF creation also references `slides_final/` directly.

5. **Visual Structure Assignment**
   - Pick one dominant structure per slide:
     - chronological shift -> timeline / sequence / staged flow
     - market or labor statistics -> KPI strip / trend table
     - competing options -> comparison table / 2x2 matrix
     - system, solution, workflow, or technical architecture -> architecture flow / stack
     - compounding asset -> loop
     - rollout plan -> phase roadmap
     - use cases -> grid/table
     - vision or chapter opener -> signature visual
   - Assign `layout_archetype`, `layout_family`, `layout_diversity_plan`, `layout_rotation_guard`, and `grid_mode` before writing final on-slide text.
   - Assign `visual_richness_role`: `restrained_signature_illustration`, `diagram_embedded_illustration`, `data_visual`, `icon_evidence`, or `quiet_table`.
   - Assign `illustration_intensity`: `0_none`, `1_marginal`, `2_integrated`, or `3_restrained_signature`.
   - Assign `creative_variance`: `low`, `medium`, or `high`.
   - Assign `human_designed_illustration_style` for slides where the audience should remember a clear designed illustration, not just a metric.
   - Assign `illustration_tone_lock` and `illustration_style_sheet` before image prompting whenever any slide in the deck uses people, devices, document objects, UI panels, icon badges, or workflow scenes.
   - If illustration competes with the chart/diagram, reduce intensity or split the slide.

6. **Density And Split Gate**
   - Assign `density_tier`: `T1_sparse`, `T2_balanced`, `T3_dense`, or `T4_appendix_dense`.
   - Run `impact_clarity_density_gate` before image prompting: the slide must have one unmistakable takeaway, one dominant visual structure, a useful evidence layer, and a simple reading path. Repair any slide that feels low-impact, hard to understand, over-simplified to emptiness, or dense without hierarchy.
   - Define `reader_mode`, `decision_question`, `information_units`, `density_levers`, and `overload_controls`.
   - Use `density_lift_lock` to add one or two useful evidence layers before image prompting when a slide feels too empty for the decision question.
   - Use `evidence_compression_ladder` to choose the smallest proof structure that makes the message credible: key number, ranked list, before/after delta, driver tree, causal chain, 2x2, mini table, evidence strip, or source-backed annotation.
   - Use `structure_choice_bias` and `structured_density_bias` to add issue-tree, driver-tree, matrix, value-chain, KPI-bridge, or decision-table structure only when it improves the reader's decision path.
   - Use `structure_first_visual_mix` to choose a chart, table, matrix, flow, map, comparison axis, or evidence strip when that structure gives the reader a clearer path than a standalone illustration.
   - Use `imageability_lock` to convert abstract messages into concrete visual anchors that make the message observable.
   - Use `visual_subject_open_set`, `message_led_composition_lock`, `region_balance_policy`, and `composition_fit_plan` before image prompting so the selected subject, region balance, focal relationship, and canvas occupancy are designed from the argument.
   - Use `secondary_region_integrity_lock` and `body_silhouette_lock` for split or auxiliary-region layouts so the supporting region has a complete role and the body closes as one designed block.
   - Use `editorial_polish_repair_loop` to improve specificity, proportion, rhythm, and focal hierarchy.
   - For `T3_dense`, define density layers explicitly: main figure/table, evidence strip, context panel/legend, comparison baseline, annotations, source cues, and optional Insight. Keep paragraph text out.
   - Split when a slide has multiple messages, mixed structures, more than 3 major regions, too many source facts, or text that would fall below 18pt equivalent.
   - Combine adjacent slides only when they repeat the same message, depend on the same comparison, or require one shared decision frame.

7. **Deck Master Gate**
   - Define `deck_header_master_lock`, `header_identity_lock`, `header_left_accent_reference_lock`, `header_left_accent_no_protrusion_rule`, `header_integrity_blocker_lock`, `deck_tone_signature_lock`, `illustration_tone_lock`, `illustration_style_sheet`, `header_footer_text_color_lock`, `footer_anchor_baseline`, `insight_surface_master`, and repeated table/card/icon masters before generating a deck.
   - Fail any final prompt whose `deck_header_master_lock` is range-only, missing x/y/w/h/color/font_family/font values, or uses any font family other than Noto Sans JP for visible text.
   - For ACT-style guidelines, fail any plan whose H1 becomes Petrol, whose left vertical line is missing, whose left vertical line does not match the approved header-block geometry, whose line top sits above the visible H1 glyph/title top, whose line floats near the page top or detaches from H1/subtitle, whose subtitle size/color drifts, whose body starts above the locked `body_start_y`, or whose header clear zone is filled.
   - Fail any deck whose slides change material language without a message-led reason: random base colors, rule weights, card/table fills, icon families, illustration finish, accent intensity, Insight treatment, or Source behavior.

8. **Speaker Notes Plan**
   - Draft `speaker_notes_text` for every deck slide before image prompting, with `speaker_notes_depth_lock` so PPT notes are substantial enough to present from.
   - Use the deck language unless the user specifies otherwise.
   - Notes should include: the spoken message in plain language, the evidence or assumption to mention, source caveat or confidence level when relevant, and a transition to the next slide.
   - Keep notes out of `exact_text` and out of the image prompt's on-slide text. Speaker notes belong in PPTX or PPTX speaker notes after image generation.
   - Do not add unsupported facts, invented sources, internal prompt notes, file paths, or production-route language to speaker notes.

9. **Image Prompt Handoff**
   - For each slide, output: action title, subtitle, exact text, visual structure, visual richness role, illustration intensity, density tier, coordinates, source policy, Insight decision, and negative prompt.
   - Block generation until `layout_archetype`, `layout_family`, `layout_diversity_plan`, `layout_rotation_guard`, `grid_mode`, `visual_richness_role`, `illustration_intensity`, `creative_variance`, `density_tier`, `source_policy`, `exact_text`, `speaker_notes_depth_lock`, `speaker_notes_text`, `near_white_slide_base_lock`, `deck_header_master_lock`, `header_identity_lock`, `header_left_accent_reference_lock`, `header_left_accent_no_protrusion_rule`, `header_left_accent_top_protrusion_blocker`, `header_integrity_blocker_lock`, `deck_tone_signature_lock`, `illustration_tone_lock`, `illustration_style_sheet`, `header_line_top_rule`, `message_box_compactness_blocker_lock`, and `coordinate_inventory_1672` are resolved.
   - Generate pilot slides first for any deck over 3 slides.

## Density Design Best Practices

Use this pass before slide-level prompts. Density is a design decision, not a count target.

### Density Ladder

- `T1_sparse`: opener, chapter turn, or final vision. One message, one strong visual or data point, optional subtitle. No body paragraph.
- `T2_balanced`: default strategy page. One main figure/table/diagram plus 2-4 labels, one small context cue, and Source footer when traceable sources exist.
- `T3_dense`: evidence-heavy page. One main structure plus a KPI strip, supporting context region or evidence strip, chart annotations, units, benchmark/context column, and source cue.
- `T4_appendix_dense`: reference page only when accepted. Table or small multiples can dominate, but visual grouping and typography must still be readable.

### Density Gate

For every slide, answer:

- `reader_mode`: scan, read, or reference. Scan pages need fewer words; reference pages can carry more rows if grouped.
- `decision_question`: what should be answerable without narration?
- `information_units`: message, context, comparison, trend, mechanism, risk, implication, assumption, source.
- `impact_clarity_density_gate`: attention hook, self-explanatory logic, simple dominant structure, sufficient evidence, and clear hierarchy.
- `message_sharpness_lock`: action title includes actor/topic, change/tension, and implication.
- `evidence_compression_ladder`: smallest proof structure that supports the decision without adding prose.
- `density_levers`: which added layer improves the message: denominator, time horizon, benchmark, segmentation, scenario, assumption, source, counterpoint, or implication.
- `overload_controls`: one dominant structure, max three major regions, grouped labels, body at 18pt equivalent or larger, and no illustration detail doing the job of evidence.

### Useful Density Levers

- KPI strip above or beside the main structure.
- Supporting interpretation region that explains the implication of the chart/table.
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
opening_slide_rule:
  opening_slide_role: opening_thesis_slide
  first_slide_not_title_only: true
  opening_density_gate:
  low_density_opener_repair:
primary_guideline:
guideline_priority:
brand_style_notes:
storyline_frame:
section_map:
message_backlog:
evidence_ledger:
source_ledger:
appendix_candidates:
open_questions:
slide_id:
chapter:
action_title:
opening_slide_role:
first_slide_not_title_only:
opening_density_gate:
reader_question_answered:
message_type:
supporting_evidence:
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
speaker_notes_text:
speaker_notes_source_cues:
speaker_notes_transition:
visual_structure:
visual_richness_role:
signature_visual_plan:
illustration_intensity:
human_designed_illustration_style:
illustration_tone_lock:
illustration_style_sheet:
illustration_consistency_status:
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
visible_brand_label_blocker: no separate ACT wordmark, logo, title kicker, badge, or brand label in the header unless exact_text explicitly requests it
header_identity_lock:
header_integrity_blocker_lock:
header_footer_text_color_lock:
  h1: "#2D332E"
  subtitle: "#4D544E"
  footer_source_table_note: "#6E756E"
  forbidden_text_colors: Petrol, Honey, yellow, arbitrary gray
message_box_scale_lock:
message_box_text_size_lock:
message_box_compactness_blocker_lock:
message_box_text_alignment_lock:
insight_surface_placement_lock:
message_box_optionality_lock: Insight/message-box is selective and occasional, never a default slide requirement
insight_absence_default_lock: start from no Insight/message-box; add one only when it passes insight_justification_required
insight_justification_required: keep an Insight/message-box only with a clear non-redundant interpretation, decision signal, or reading bridge
honey_bottom_bar_lock: Honey is a quiet optional bottom Insight bar treatment, not a main content card, missing-body placeholder, dashed outline, category badge, title underline, or decorative yellow block
honey_selective_signal_lock: Honey starts absent and appears only when a justified bottom decision signal is stronger than no component or neutral outline
honey_justification_required: keep Honey only with a written reason tied to decision clarity; remove decorative or space-filling Honey
max_text_size_lock:
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
secondary_region_integrity_lock:
body_silhouette_lock:
deck_tone_master_lock:
deck_tone_signature_lock:
illustration_tone_lock:
illustration_style_sheet:
illustration_consistency_status:
structure_choice_bias:
structured_density_bias:
structure_choice_status:
post_generation_design_balance_check:
whitespace_occupancy_balance_status:
typography_balance_status:
color_consistency_status:
outer_padding_consistency_status:
header_integrity_status:
visual_design_quality_traits:
petrol_usage_lock:
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
insight_absence_default_lock:
insight_justification_required:
honey_selective_signal_lock:
honey_justification_required:
data_to_render:
density_risk:
split_merge_decision:
prompt_text_budget:
image_prompt_ready:
pptx_rollup_plan:
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
nonconforming_existing_png_regeneration_lock:
review_manifest:
review_manifest_status: approved
validate_review_manifest:
slides_final_master_path:
slides_package_policy:
render_check_policy:
pdf_export_source_lock:
contact_sheet_review_path:
render_diff_report:
unresolved_items:
```

## Source Notes

These practices synthesize common professional-presentation guidance:

- Source footers are part of credibility, not decoration. Render `Source: ...` only when traceable real external/provided sources exist; use `source_line: none` and draw no Source footer when no traceable source exists. Never render brand assumptions, brand analysis, internal analysis, our analysis, AI-generated analysis, working assumptions, upload names, or draft provenance as Source.
- Source footers sit on an invisible alignment baseline. Do not draw a gray rule, separator line, divider, underline, baseline stroke, footer rail, or hairline above, below, behind, or adjacent to Source.
- Source footers remain separate from Insight/message-box text. Treat the space above Source as part of the composition rhythm: it can hold a centered bottom Insight when interpretation is useful, but the Insight and Source should read as two different layers.

## Output Artifact Notes

- `slides_final/` is the single loose-PNG master for approved generated slide images.
- `slides_package/` should contain PPTX, speaker notes, review manifest, and metadata only. It should not contain copied slide PNGs.
- `render_check/pdf_pages/` is disposable QA output from a rendered PDF/PPT check. It is not a source of truth and can be regenerated.
- PDF outputs should be created from `slides_final/` master PNGs, not from copied PNGs under `render_check/pdf_pages/`.
- Keep one retained contact sheet by default: `render_check/contact_sheet_review.png` from `slides_final/`.
- If delivery QA needs generated-vs-package-vs-PDF comparison, create one `render_check/contact_sheet_delivery_compare.png` or `render_check/render_diff_report.json`; do not retain parallel `contact_sheet_generated*`, `contact_sheet_package*`, and `contact_sheet_pdf_render*` files for the same slide set.

- IBCS SUCCESS emphasizes saying a clear message, structuring content, simplifying clutter, and condensing information into high-density business communication: `https://www.ibcs.com/IBCS/`
- Assertion-evidence guidance supports a message headline plus visual proof instead of dense prose: `https://www.writing.engr.psu.edu/guidelines_AE_slides.pdf`
- PLOS "Ten simple rules for effective presentation slides" emphasizes one message, less unnecessary information, and cognitive-load-aware slide construction: `https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009554`
- Purdue OWL data visualization presentation guidance emphasizes chart choice, audience fit, clear labels, and source context: `https://owl.purdue.edu/owl/general_writing/visual_rhetoric/data_visualization/data_visualization_presentation.html`
- Investor pitch guidance favors legible, simple, obvious slides with a small number of memorable points: `https://www.ycombinator.com/blog/how-to-design-a-better-pitch-deck/`
