---
name: atom-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ATOM 16:9 strategy slide images with gpt-image-2."
---

# ATOM Slide Image Generation

Use `scripts/build_atom_slide_prompt.py`; full rules live in `build/references`.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX roll-up.

Start Codex built-in image generation directly. Do not run local preflight, artifact-route probing, account setup, credential setup, token setup, SDK setup, or environment-variable setup. Only the image tool itself can block generation.

Returned image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when a filesystem path is needed.

Never make final PNGs from PPTX export, screenshots, local rendering, HTML, SVG, canvas, or PIL. PPTX is only the final wrapper.

Design defaults: Noto Sans JP, 1672x941, Deep Blue `#0B2F5B`, Charcoal `#2D332E`, light gray `#DDE3EA`, quiet Honey `#F7EECF/#C49A2C`, one editorial illustration tone.

Bias toward message-led structure and useful density when it clarifies the slide.

Do not report complete while review has blockers, majors, tone drift, weak content/design, unreadable text, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Source footer appears only for real traceable sources; otherwise use source_line: none.
Source is text-only: never draw gray rules, separator lines, underlines, baselines, or hairlines above, below, behind, or adjacent to Source.

Package with `scripts/package_slide_images_to_pptx.py` after the Codex-generated PNG artifacts are approved and materialized under `slides_final/`. Speaker notes are required unless explicitly disabled.
