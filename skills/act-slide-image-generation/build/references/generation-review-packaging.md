# Generation, Review, And Packaging

Use this file for production and delivery.

## Pilot And Same-Deck Reference

Generate one representative pilot content slide and complete its header pixel-inventory review first. Derive a temporary style board from the audited H1/subtitle crop on uninterrupted canvas, canvas tone, palette swatches, body-rule weight, corner treatment, and type-role examples. Use this style board as the visual reference for new pages. The pilot freezes material and header tokens while later prompts vary body composition from the message.

## Reference-role isolation

Assign each referenced image one role: `content_target`, `style_board`, or `asset_reference`. New-slide generation uses at most one style board and text instructions as content. Repair generation uses the target slide as the first and normally sole image reference; express deck tokens in text. Asset references contain only the named asset. Multiple full-slide references return to one target, one style board, or zero-base generation.

After every generation or repair, compare the actual PNG with frozen exact text and the body specification. A duplicate header, copied exhibit, split canvas, foreign label, repeated claim, or any visible material from another reference is a `reference_contamination_blocker`. Place the page in `weak_slide_regeneration_queue` and regenerate it. Require one header group, one governing thought, and one connected reading path across the full canvas.

## Contact-Sheet Consistency Gate

Review all actual PNGs together before packaging. Confirm that each header is an uninterrupted canvas containing its registered H1 and subtitle, that outer bands follow their declared furniture inventory, and that typography, alignment, canvas, card/rule material, and navigation treatment match the approved pilot. Record pages that need restoration in `weak_slide_regeneration_queue` and keep packaging blocked until the queue is empty.

## Approved Production Route

Generate final PNG pixels exclusively with Codex built-in `gpt-image-2`. Use `2048x1152` when available and retain a directly generated `1672x941` result as the approved fallback. Keep final loose PNG masters in `slides_final/`.

Planning scripts scaffold prompts and validate manifests. Packaging scripts wrap approved PNG masters into PPTX/PDF.

## Prompt Order

1. Drawing action and intended use
2. Exact visible text
3. Master shell and rendered typography targets
4. Footer mode and available content band
5. Content footprint and optical targets
6. Main structure, visual anchor, and reading path
7. ACT material system
8. Focused preservation and repair criteria

Write prompts in positive directive language. Describe the selected route, visible target, measurable range, and corrective action.

Keep the generation prompt concise and spatially explicit: purpose, exact visible text, zone bounds, governing relationship, then material system. Use one style board or one content target per role. During refinement, change one region at a time, repeat the fixed header and edge-furniture state, and preserve every approved element outside the named region. This applies OpenAI's image prompting guidance to slide production while keeping the deck contract measurable.

## Review Loop

### Focused image correction

Use the built-in image editing route for one isolated text, color, icon, or local-spacing variance after the composition passes. Name one region and one change category, then restate the approved header, exact-copy ledger, grid skeleton, outer-band furniture, and reference roles. Route any topology, silhouette, occupancy, multi-region alignment, or reading-path variance to zero-base regeneration from the frozen specification. After two focused edits, regenerate from the frozen specification.

Open every generated PNG and review:

- exact text and title uniformity
- rendered H1/subtitle visible heights against the absolute bands and the approved pilot within 2px
- header/body quiet band
- deck-wide `equity_story_master` outer-shell profile with consistent `50/72/17/72px` top/right/bottom/left containment
- body width/height footprint
- top-level container footprint, allocated-region area fill, and meaningful foreground fill
- text-bbox union and meaningful-object union
- 16-column grid-line alignment and 8px baseline alignment
- recursive Flex basis, gap, wrap, fill, minimum-size, and overflow measurements
- component edge and text-anchor registration, repeated-module dimensions, shared vertical/horizontal axes, and orphan regions
- structural-rule endpoints, stroke tokens, connector ports, orthogonal routes, bends, and crossings
- grid-rigidity score and structured-cell fill
- horizontal and vertical optical center
- footer consistency, exact `Source: ` / `Assumption: ` / `Note: ` prefixes, external-reference provenance, and canonical one- or two-line footer geometry
- text-only message-box construction, zero icon children/atoms, and copy-derived box height
- evidence-state encoding
- font and palette unity
- illustration and icon consistency

Record each item as `approved` or `repair_required`. For repair, name one observed delta, the target state, the region that changes, and the elements that remain preserved. Continue until every slide and deck-level status is approved and the regeneration queue is empty.

Require the render audit to mirror the generation plan field-for-field. A complete review contains `layout_tree`, `grid_plan`, `flex_plan`, `occupancy_plan`, and their measured audit counterparts. Register every rendered body element, keep grid and baseline error within 4px, and record zero overflow pixels, clipped items, and text overlaps.

## Packaging

Create `slides_package/speaker_notes.json` with ordered slide IDs and speaker notes. Package one full-bleed approved PNG per slide. Render the package back for QA and compare it with the `slides_final/` masters.

Apply `speaker_notes_persuasion_lock`: each note explains the evidence-to-claim warrant, ends with a landing sentence, and hands the audience to the next slide through a concise signpost transition. Register the `notes_persuasion_arc`, and use a hook or objection pre-emption only when it materially improves the decision argument.

### Output deduplication

Keep each final slide PNG exactly once under `slides_final/`. Keep one composite `contact_sheet_review.png`, one requested delivery wrapper, and compact metadata such as `speaker_notes.json` and `review_manifest.json`. Place render-back QA files in a temporary directory outside the delivery root and remove that directory after visual verification. A PDF created only as an intermediate render is temporary. Before delivery, scan by content hash and remove duplicate PNGs outside `slides_final/`; the contact sheet is the only approved derived PNG because it combines all pages for review.
