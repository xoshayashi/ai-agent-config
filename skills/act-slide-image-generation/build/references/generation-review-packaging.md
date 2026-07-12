# Generation, Review, And Packaging

Use this file for production and delivery.

## Pilot And Same-Deck Reference

Generate and approve one representative pilot content slide first. Derive a temporary style board that contains only its header crop, canvas tone, palette swatches, rule weight, corner treatment, and type-role examples. Use the style board, not the complete pilot slide, as the visual reference for new pages. The pilot freezes material and header tokens while later prompts vary body composition from the message without importing another page's exhibit.

## Reference-role isolation

Assign each referenced image one role: `content_target`, `style_board`, or `asset_reference`. New-slide generation uses at most one style board and text instructions as content. Repair generation uses the target slide as the first and normally sole image reference; express deck tokens in text. Asset references contain only the named asset. Multiple full-slide references return to one target, one style board, or zero-base generation.

After every generation or repair, compare the actual PNG with frozen exact text and the body specification. A duplicate header, copied exhibit, split canvas, foreign label, repeated claim, or any visible material from another reference is a `reference_contamination_blocker`. Place the page in `weak_slide_regeneration_queue` and regenerate it. Require one header group, one governing thought, and one connected reading path across the full canvas.

## Contact-Sheet Consistency Gate

Review all actual PNGs together before packaging. Reject and regenerate any page that introduces serif type, centered content headers, dark top bands, sidebars, logos, ACT wordmarks, page numbers, chapter labels, decorative rails, gradients, shadows, unrequested navigation furniture, or a different card/rule material system. Record failing pages in `weak_slide_regeneration_queue` and keep packaging blocked until the queue is empty.

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

### Geometry-only final correction

Use image generation for meaning, copy, typography, component, and composition changes. After a slide is otherwise approved, deterministic geometry repair may translate a complete body or bottom-evidence group while preserving every content pixel and keeping the header fixed. Fill the revealed strip from the existing canvas surface, exclude the displaced border from the pasted region, and restore the quiet canvas edge. Record the operation as `geometry_only_repair`, then re-measure safe-shell bounds, header/body clearance, footer clearance, and body centroid. Return to image-generation repair whenever the correction would alter text, color, scale, components, internal spacing, composition, or reading path.

Open every generated PNG and review:

- exact text and title uniformity
- rendered H1/subtitle size and stack gap
- header/body quiet band
- outer padding
- body width/height footprint
- horizontal and vertical optical center
- footer mode
- evidence-state encoding
- font and palette unity
- illustration and icon consistency

Record each item as `approved` or `repair_required`. For repair, name one observed delta, the target state, the region that changes, and the elements that remain preserved. Continue until every slide and deck-level status is approved and the regeneration queue is empty.

## Packaging

Create `slides_package/speaker_notes.json` with ordered slide IDs and speaker notes. Package one full-bleed approved PNG per slide. Render the package back for QA and compare it with the `slides_final/` masters.

### Output deduplication

Keep each final slide PNG exactly once under `slides_final/`. Keep one composite `contact_sheet_review.png`, one requested delivery wrapper, and compact metadata such as `speaker_notes.json` and `review_manifest.json`. Place render-back QA files in a temporary directory outside the delivery root and remove that directory after visual verification. A PDF created only as an intermediate render is temporary. Before delivery, scan by content hash and remove duplicate PNGs outside `slides_final/`; the contact sheet is the only approved derived PNG because it combines all pages for review.
