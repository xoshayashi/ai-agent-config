---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use the smallest reference set required for the current phase:

- `build/references/core-layout-and-typography.md` for geometry and rendered type
- `build/references/content-and-story.md` for argument, evidence, and reading order
- `build/references/generation-review-packaging.md` for production, review, and delivery
- `build/references/prompt-recipes.md` for a prompt scaffold
- `build/references/openai-gpt-image-2-best-practices.md` for model semantics

Generate final PNG pixels with Codex built-in `gpt-image-2`. Keep each approved master once in `slides_final/`, inspect every actual PNG, then package approved masters with the PPTX/PDF scripts.

## Core Master

Use Noto Sans JP, a near-white ACT canvas, and `build/references/canonical-geometry.json` as the coordinate source. On the 1672x941 basis, the outer shell is `x=72..1600 y=80..861`. H1 uses `x=72 y=80 w=1528`, one line, `38pt/700 #2D332E`. Subtitle uses `x=72 y=126 w=1528`, one line, `32pt/400 #626A64`. The first body mark begins at `y>=270` after 64-96px of quiet clearance.

Resolve design decisions in this order: exact text and meaning; one header identity; safe shell and readable type; connected reading path; grouped body silhouette; optical balance; decorative refinement.

## Rendered Type

Approve actual pixel boxes on the 1672x941 basis:

- H1 visible height: 42-50px
- Subtitle: 28-36px and 65-78% of H1
- Section heading: 28-34px
- Primary body label: 22-28px
- Supporting text: 18-24px
- Integrated takeaway: 26-32px and at or below section-heading scale

With a pilot, keep corresponding header glyph boxes within 4px across the deck. Fit copy through rewriting, body redistribution, or slide splitting while preserving the type-role scale. Keep H1 within 28 full-width-equivalent characters and subtitle within 36 as the first-pass copy budget, followed by rendered-width review.

## Body Composition

Select a layout family from the message and content budget. Use one governing thought, one dominant evidence object, and one meaningful reading order. Keep every body pixel inside the canonical shell and selected body band. Related-element gaps are smaller than group-separation gaps; repeated same-level gaps align to the shared 8px grid within a half-unit.

Measure the body envelope and body-only optical centroid. Compare them with the selected content band and a same-family pilot. Without a pilot, preserve deliberate breathing above and below and judge the body as one complete group. Intentional asymmetry is approved when the visual anchor and endpoint explain it.

At thumbnail size, the header acts as a compact entry point and the body carries the dominant visual mass. Recompose the responsible group when header and body compete or when the body reads as a compact island.

Freeze a `zonal_mass_plan` before generation. On the 1672x941 basis, the header's visible marks stay within `y=80..170`, the body envelope uses `y=270..830` for footer-absent slides or `y=270..790` with a footer, and the outer bands retain deliberate canvas. A typical content slide uses 72-92% of the available body width and 70-90% of the available body height; the selected layout family may use the remaining space as one named quiet region. Review the header, body, and footer as three weighted zones: compact entry, dominant evidence, quiet provenance. Repair by redistributing the body as one group while preserving the fixed header and footer baselines.

Prompts follow a short two-layer contract: first state purpose, exact text, zone bounds, and the governing visual relationship; then state palette and material. Repeat the fixed header and edge furniture once in the final acceptance sentence. Refinement edits name one region, one measured delta, and the elements to preserve.

## Canvas Edges

On the 1672x941 basis, place the topmost and bottommost meaningful pixels within the shared 56-88px edge band and keep their difference within 16px. Adjust the top through the header master and the bottom through body/footer composition. Scale proportionally for other outputs.

Apply a `canvas_furniture_allowlist` before generation and again during pixel review. The top outer band contains only the approved H1 and subtitle beginning at the shared left anchor. The side and bottom outer bands remain quiet canvas, except for a genuine traceable source placed on the approved footer baseline. Treat every visible label, running header, brand name, deck descriptor, page marker, navigation cue, decorative rail, and corner annotation outside the frozen exact-text specification as reference contamination. Repair by restoring the quiet canvas edge while preserving the approved header and body.

## Readability And Evidence

Use >=4.5:1 contrast for normal text and >=3:1 for large text. Keep Japanese paragraph lines within 40 CJK glyphs, use ragged-right alignment, and use 1.4-1.5 line height for multi-line explanatory text. Pair color with labels, shape, position, or pattern.

For quantitative comparisons, use a common baseline with position, bars, or aligned dots. Place the decision-carrying value beside its mark and label series directly when space permits.

Visible Source appears for a genuine independently traceable publication, public dataset, statute, research paper, or stable article. Internal notes, uploads, filenames, company materials, and generated summaries remain in the source ledger or speaker notes with `source_line: none`.

## Reference And Repair Routes

Approve one pilot, then create a temporary `style_board` containing its header crop, canvas tone, palette swatches, rule weight, corner treatment, and type-role examples. New slides use one style board plus text-only exact content.

Assign every reference one role: `content_target`, `style_board`, or `asset_reference`. Preservation repairs use the content target as the first and primary image. Asset references contain the named asset. Visible output matches the frozen exact text and selected reference roles.

Use focused editing for one local element when reading order, hierarchy, and body silhouette already pass. Use zero-base regeneration for structural, hierarchy, density, reference-fidelity, or overall-balance changes. After two focused iterations, return to the frozen specification and regenerate.

## Review And Delivery

Review every PNG at full size and in one contact sheet. Approve header anchors, glyph scales, canvas tone, palette roles, rule weights, corner treatment, footer behavior, reading order, body balance, and deck rhythm.

Approve the contact sheet when every slide presents the shared header, one evidence-led body, and the selected footer source treatment as its complete furniture system. The deck uses these recurring elements to create unity while each body composition follows its message.

Completion includes approved content, design, and deck-unity statuses; an empty `weak_slide_regeneration_queue`; and a package manifest with reviewer, timestamp, and `png_sha256_by_slide`. Packaging re-measures PNG margins and verifies hashes. Speaker notes live at `slides_package/speaker_notes.json`.

Keep one composite `contact_sheet_review.png`, one requested delivery wrapper, compact metadata, and one final PNG per slide. Use a temporary directory for render-back QA and clear it after verification.
