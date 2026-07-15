---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use the smallest reference set required for the current phase:

- `build/references/core-layout-and-typography.md` for geometry and rendered type
- `build/references/design-tokens.json` for the replaceable semantic color system
- `build/references/grid-flex-layout.md` for the mandatory alignment lattice, recursive layout tree, and occupancy audit
- `build/references/consulting-grid-rigidity.md` for strategy-exhibit precision, component anchors, structural rules, orthogonal connectors, and grid-rigidity scoring
- `build/references/image-model-adaptive-construction.md` for content atoms, copy capacity, model-fit gates, concise render-prompt compilation, and repair routing
- `build/references/clarity-first-composition.md` for one relationship, one visual grammar, element economy, independent regions, and the three-second reading-path gate
- `build/references/content-and-story.md` for argument, evidence, and reading order
- `build/references/argument-closure-and-deck-logic.md` for closed slide reasoning, dependency-complete deck sequencing, counterarguments, and decision coverage
- `build/references/generation-review-packaging.md` for production, review, and delivery
- `build/references/prompt-recipes.md` for a prompt scaffold
- `build/references/openai-gpt-image-2-best-practices.md` for model semantics

Generate final PNG pixels with Codex built-in `gpt-image-2`. Keep each approved master once in `slides_final/`, inspect every actual PNG, then package approved masters with the PPTX/PDF scripts.

## Core Master

Use Noto Sans JP and keep geometry and color as separate contracts. `build/references/canonical-geometry.json` owns dimensions; `build/references/design-tokens.json` owns changeable color roles. Apply the `equity_story_master` profile on the 1672x941 basis: outer insets `top=50px right=72px bottom=17px left=72px`. H1 uses `x=72 y=50 w=1492`, one line, `28pt/700` with the `main_message` role. Subtitle uses `x=72 y=123 w=1492`, one line, `20pt/400` with the `sub_message` role. Both use square wrapping, zero text insets, top anchoring, and the same left alignment. Calibrate their rendered pixels against the supplied equity-story render: H1 centers at 48px visible height and subtitle at 34px. The first approved slide becomes the header pilot for the deck.

Resolve design decisions in this order: governing decision and closed argument; exact text and meaning; one header identity; safe shell and readable type; connected reading path; grouped body silhouette; optical balance; decorative refinement.

Apply `argument_closure_lock` before layout. Freeze a `deck_argument_plan` and `closure_matrix`. Each slide registers its question, claim, evidence, warrant, implication, and action or transition; each deck transition registers prior inputs, new contribution, next output, and decision impact. Include `slide_argument_plan` and `closure_matrix` in every validated layout plan. Pass 100% load-bearing claim coverage, 100% evidence-to-claim binding, 100% adjacent-slide transition coverage, zero unstated decision-critical premises, zero unresolved contradictions, and 100% owner/due-date coverage for decision-critical open items. The final page converts the accumulated argument into decisions, owners, timing, and success measures.

Compile every content slide through seven image-model gates: content contract, copy capacity, topology/complexity, full geometry validation, 2048-basis render-prompt compilation, one-slide PNG audit, and measured repair routing. Keep the detailed validator plan separate from the concise image-model prompt. Bind every visible string to one registered component with one expected occurrence.

## Rendered Type

Approve actual pixel boxes on the 1672x941 basis:

- H1 visible height: 47-50px on the 1672x941 basis; calibrated center 48px
- Subtitle: 33-35px on the 1672x941 basis; calibrated center 34px
- Section heading: 28-34px
- Primary body label: 22-28px
- Supporting text: 18-24px
- Integrated takeaway: 26-32px and at or below section-heading scale

Keep corresponding H1 and subtitle visible heights within 2px of the approved pilot across the deck, while every slide also stays inside the absolute rendered bands. Fit copy through rewriting, body redistribution, or slide splitting while preserving the fixed 28pt/20pt master. Keep H1 within 28 full-width-equivalent characters and subtitle within 36 as the first-pass copy budget, followed by rendered-width review.

## Body Composition

Derive one primary relationship from the message and evidence, then select one matching visual grammar for the complete body. Use 2-4 independently legible major regions with one role each, one start, one ordered path, and one landing. Supporting evidence stays inside the selected grammar through aligned rows, columns, labels, or values. Translate the composition into the mandatory recursive Grid/Flex layout tree in `grid-flex-layout.md` and keep every body pixel inside the canonical shell and selected body band.

Measure the body envelope and body-only optical centroid. Compare them with the selected content band and a pilot with comparable visual weight when available. Without a pilot, preserve deliberate breathing above and below and judge the body as one coordinated composition. Intentional asymmetry is approved when the visual anchor and endpoint explain it.

At thumbnail size, the header acts as a compact entry point and the body carries the dominant visual mass. Recompose the responsible group when header and body compete or when the body reads as a compact island.

Freeze a `zonal_mass_plan`, `layout_tree`, `grid_plan`, `flex_plan`, and `occupancy_plan` before generation. On the 1672x941 basis, header visible marks stay within `y=66..155`; the body envelope stays within `y=190..869` in both footer modes, and the first meaningful body region begins 48-112px below the `y=170` header clearance datum. A visible provenance footer uses `x=72 y=866 w=1528 h=48`, 9pt `footer` text, zero insets, left alignment, centered vertical anchoring, and a one- or two-line budget. Footer-absent slides pass 82-94% body height and 86-96% top-level-container height; footer-present slides pass 78-90% body height and 84-94% container height. Both modes pass 78-92% primary-body width, 82-94% primary-container width, 58-80% allocated-region area fill, and 18-38% meaningful-foreground fill. Measure text ink at 6-20% and meaningful-object ink at 10-30% of the visible body envelope. A single aspect-locked focal object keeps its 55-88% object-width band while the complete body passes its footer-mode bands. Compute vertical centroid from every painted body component, including components attached directly to a Grid parent and the painted message box; it passes 58-62% of the full canvas height in both modes. The full-width message box is an auxiliary conclusion band: include it in vertical mass, area fill, and closure, while primary-body horizontal occupancy is measured from the main grid regions. This middle-band contract keeps the body visually substantial while preserving distinct header, content, and footer zones.

Apply `footer_absent_vertical_balance_lock` whenever `footer_mode: absent`. Place the lowest meaningful body or allocation pixel within `y=857..869`. Measure the top visible margin from canvas top to the first H1 pixel and the bottom visible margin from the last meaningful body pixel to canvas bottom; their absolute difference is <=12px on the 1672x941 basis. The plan validator uses the calibrated 66px first-H1-pixel proxy and the PNG audit replaces it with the measured first H1 pixel. Footer-present slides retain their dedicated envelope and centroid without this closure rule.

Use the explicit 16-column parent grid: 73px tracks, 24px gutters, and grid lines 1..17 across the 1528px shell. Align vertical positions and internal spacing to the 8px baseline with ±4px tolerance. Register every body element in exactly one Grid/Flex parent. Every Flex parent freezes bounds, main axis, wrap plan, gap, justify, align, and each child’s basis, grow, shrink, and minimum sizes. Rendered audits match every plan field, keep grid and baseline error within 4px, flex main-axis fill at 92-100%, cross-axis fill at 82-100%, and overflow, clipping, and text overlap at zero. Any absent field or out-of-range measurement is `repair_required`.

Generation and repair start from a validated `--layout-plan` JSON containing `slide_argument_plan`, `closure_matrix`, `footer_mode`, `header_furniture_plan`, `content_atom_registry`, `model_fit_plan`, `clarity_plan`, `surface_plan`, `tone_plan`, `layout_tree`, `grid_plan`, `flex_plan`, `component_geometry_plan`, `structural_rule_plan`, `connector_plan`, `rigidity_plan`, `occupancy_plan`, and `quiet_region`. The prompt builder validates argument closure, complete header inventory, exact-copy binding, content complexity, one visual grammar, region independence, surface-radius and luminous-tone systems, parent geometry, component anchors, rules, connectors, grid rigidity, occupancy, shell containment, and quiet regions before compiling a concise render contract. Use this compiled contract for the first render as well as repairs so the declared slide furniture remains stable from the first output.

Apply `consulting_grid_rigidity_lock` to content slides. Register text anchors, module edges, rule endpoints, icon centers, values, and connector ports on the shared column and baseline system. Pass edge registration >=90%, repeated-module consistency >=95%, gap-token compliance >=95%, structural-rule and connector endpoint pass rates of 100%, structured-cell fill 65-85%, orphan region count 0, and the weighted grid-rigidity score >=0.93. Preserve compositional variety through declared spans, nesting, merges, evidence forms, and emphasis choices inside this registered geometry.

Apply `clarity_first_composition_lock`: one primary relationship, one visual grammar, one visual anchor, one emphasis system, and one connector set. Use 2-4 independently legible regions and create unity through shared axes and spacing. Select a common outer frame only for semantic containment. Use one mark language across peer regions with >=95% consistency and balance owned-content distribution across peer internal bands at >=90%. Use 8px or 12px major-region radii and 4px or 8px peer-module radii for a precise structure with slight warmth.

Apply `luminous_tone_vocabulary_lock` through `design-tokens.json`: resolve `ambient`, `lifted`, `structural`, and `focal` through the stable semantic roles `slide_background`, `neutral_panel`, `structural_panel`, and `single_focus_fill`. Pair each tone with labels or boundaries and preserve the same role mapping across the deck. Create another complete token file with any palette-key names, map the stable roles to those keys, and pass `--design-tokens PATH` when a different color guide is required; geometry, typography, hierarchy, contrast checks, and semantic role names remain unchanged.

Prompts follow a short two-layer contract: first state purpose, exact text, zone bounds, and the governing visual relationship; then state palette and material. Repeat the fixed header and edge furniture once in the final acceptance sentence. Refinement edits name one region, one measured delta, and the elements to preserve.

## Canvas Edges

On the 1672x941 basis, keep all meaningful pixels inside the `equity_story_master` shell `x=72..1600 y=50..924`. Reuse its `50/72/17/72px` top/right/bottom/left inset profile on every slide and measure the four outside bands as quiet canvas on the first render. The body union keeps its left/right clearance difference within 8px. Vertical balance follows the selected envelope and centroid, plus `footer_absent_vertical_balance_lock` when no footer exists. Adjust the top through the header master, the sides through the registered grid envelope, and the bottom through body/footer composition. Scale proportionally for other outputs.

Freeze `header_furniture_plan` before generation as `surface: uninterrupted_canvas`, `visible_component_ids: [header_h1, header_subtitle]`, and `visible_geometry_count: 0`. This makes the header a continuous canvas surface whose complete visible inventory is the left-aligned H1 and subtitle. Apply the same inventory during pixel review. Keep the side and bottom outer bands as quiet canvas, with a genuine traceable source placed on the approved footer baseline when present. Restore the declared surface and component inventory during repair while preserving the approved body.

## Readability And Evidence

Use >=4.5:1 contrast for normal text and >=3:1 for large text. Keep Japanese paragraph lines within 40 CJK glyphs, use ragged-right alignment, and use 1.4-1.5 line height for multi-line explanatory text. Pair color with labels, shape, position, or pattern.

For quantitative comparisons, use a common baseline with position, bars, or aligned dots. Place the decision-carrying value beside its mark and label series directly when space permits.

Every layout plan includes `source_plan` with an `annotations` list. A visible source is approved only when `visibility: visible`, `reference_class: external_publication`, and a traceable HTTPS, DOI, statute, or public-dataset locator are all present; its entry begins exactly with `Source: `. Add at most one `Assumption: ` and one `Note: ` annotation, in that order, and combine the active entries into one left-aligned `footer_master` atom separated by three spaces. `visibility: none` keeps the external-reference fields empty and `source_line: none`; it may still use a provenance footer for explicitly labeled assumptions or notes. The footer master is a transparent text frame with zero painted geometry, so its canonical frame can meet the body envelope while visible marks remain separated by their baselines. An empty source and annotation set uses `footer_mode: absent`. Internal filenames, meeting records, uploads, and generated summaries remain in the source ledger or speaker notes rather than being labeled as Source.

## Message Box

Every layout plan includes `message_box_plan`; use `{"boxes": []}` when the slide has no message box. A message box uses the canonical component id `message_box` and is a dedicated text-only component with zero icon children and zero icon atoms. On the 1672x941 basis, use the full-width master `x=72 y=796 w=1528 h=73`, one centered line at `17pt`, a 25px line metric, 24px vertical and horizontal padding, and zero text insets. Bind its fill to `single_focus_fill`, stroke to `single_focus_stroke`, and text to `main_message`. Rewrite the message or split the slide whenever the claim needs more than one line.

## Reference And Repair Routes

Approve one pilot through the header pixel-inventory gate, then create a temporary `style_board` containing the audited H1/subtitle crop on uninterrupted canvas, canvas tone, palette swatches, body-rule weight, corner treatment, and type-role examples. New slides use one style board plus text-only exact content. This order makes the approved header inventory, rather than an unreviewed first render, the reusable deck identity.

Assign every reference one role: `content_target`, `style_board`, or `asset_reference`. Preservation repairs use the content target as the first and primary image. Asset references contain the named asset. Visible output matches the frozen exact text and selected reference roles.

Use focused editing for one local element when reading order, hierarchy, and body silhouette already pass. Use zero-base regeneration for structural, hierarchy, density, reference-fidelity, or overall-balance changes. After two focused iterations, return to the frozen specification and regenerate.

## Review And Delivery

Review every PNG at full size and in one contact sheet. Approve header anchors, glyph scales, canvas tone, palette roles, rule weights, corner treatment, footer behavior, reading order, body balance, and deck rhythm.

Approve the contact sheet when every slide presents the shared header, one evidence-led body, and the selected footer source treatment as its complete furniture system. The deck uses these recurring elements to create unity while each body composition follows its message.

Completion includes approved content, design, and deck-unity statuses; an empty `weak_slide_regeneration_queue`; and a package manifest with reviewer, timestamp, and `png_sha256_by_slide`. Packaging re-measures PNG margins and verifies hashes. Speaker notes live at `slides_package/speaker_notes.json`.

Keep one composite `contact_sheet_review.png`, one requested delivery wrapper, compact metadata, and one final PNG per slide. Use a temporary directory for render-back QA and clear it after verification.
