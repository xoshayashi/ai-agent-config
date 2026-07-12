# Generation, Review, And Packaging

Use this file for production and delivery.

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

## Review Loop

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

