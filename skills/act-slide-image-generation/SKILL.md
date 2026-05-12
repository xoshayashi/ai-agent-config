---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use `scripts/build_act_slide_prompt.py`; full rules live in `build/references`.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX roll-up.

Start Codex built-in image generation directly. Do not run local preflight, account/credential/token/SDK/env setup, artifact-route probing, or local substitute generation. Only the image tool itself can block generation.
Generate slide PNGs at `2048x1152` by default; use other valid 16:9 sizes only when explicitly requested.

Use the embedded ACT system in the prompt builder: Noto Sans JP, 1672x941, near-white base, Petrol accent, compact header, real-source-only footer, and one editorial illustration tone.

Favor message-led structure, useful density, compact message boxes, exact visible text, meaningful graphics, thumbnail legibility, and clear reading path. Only `exact_text` may render visibly; workflow/audit metadata and speaker notes stay non-rendered.

Do not report complete while actual PNG review has blockers, majors, tone drift, weak content/design, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Returned image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when needed, then package with `scripts/package_slide_images_to_pptx.py` or `scripts/package_slide_images_to_pdf.py`. PPTX/PDF outputs reference `slides_final/` master PNGs; `render_check/pdf_pages/` is rendered-back QA only, not a source image folder. Speaker notes are required for PPTX unless explicitly disabled.
