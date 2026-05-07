---
name: atom-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ATOM 16:9 strategy slide images with gpt-image-2."
---

# ATOM Slide Image Generation

Use `scripts/build_atom_slide_prompt.py` for deck or single-slide prompt scaffolds; it loads the full rules from `build/references`.

Route: scaffold -> gpt-image-2 PNG -> full-deck review/repair -> approved manifest -> PPTX roll-up. Never make final PNGs from PPTX export, screenshots, local rendering, HTML, SVG, canvas, or PIL.

Design defaults: Noto Sans JP, 1672x941, Deep Blue `#0B2F5B`, Charcoal `#2D332E`, light gray `#DDE3EA`, quiet Honey `#F7EECF/#C49A2C`, one editorial illustration tone.

Bias toward claim-led consulting structure and useful density when it clarifies the slide.

Do not report complete while review has blockers, majors, tone drift, weak content/design, unreadable text, source/header issues, mixed illustration tone, pending status, or non-empty `weak_slide_regeneration_queue`.

Source footer appears only for real traceable sources; otherwise use source_line: none.

Keep `slides_final/` as the only loose-PNG master. `slides_package/` holds PPTX, notes, manifest, metadata; `render_check/pdf_pages/` is disposable QA.

Package with `scripts/package_slide_images_to_pptx.py` only after `validate_review_manifest` approves every PNG. Speaker notes are required unless explicitly disabled.
