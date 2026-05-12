---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use `scripts/build_act_slide_prompt.py`; full rules live in `build/references`.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX roll-up.

Start Codex built-in image generation directly. Do not run local preflight, artifact-route probing, account setup, credential setup, token setup, SDK setup, or environment-variable setup. Only the image tool itself can block generation.

Returned image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when a filesystem path is needed.

Never make final PNGs from PPTX export, screenshots, local rendering, HTML, SVG, canvas, or PIL. PPTX is only the final wrapper.

Design defaults: Noto Sans JP, 1672x941, `#FFFDFC/#FAFAF7`, Petrol `#008A80`, Charcoal `#2D332E`, mint `#F7FBF9`, quiet Honey `#F5E2A8/#C49A2C`, one editorial illustration tone.

Bias toward message-led structure and useful density when it clarifies the slide.

Do not report complete while review has blockers, majors, tone drift, weak content/design, unreadable text, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Source footer appears only for real traceable sources; otherwise use source_line: none.

Package with `scripts/package_slide_images_to_pptx.py` after the Codex-generated PNG artifacts are approved and materialized under `slides_final/`. Speaker notes are required unless explicitly disabled.
