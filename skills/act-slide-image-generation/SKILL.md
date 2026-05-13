---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use `scripts/build_act_slide_prompt.py` only to scaffold planning blocks and image prompts; full rules live in `build/references`. Prompt/package scripts are helpers, never final image renderers.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX/PDF roll-up.

Start Codex built-in image generation directly. Do not run local preflight, account/credential/token/SDK/env setup, artifact-route probing, save-route probing, or local substitute generation. Progress updates should say that slide structure and built-in image generation are starting; they must not narrate missing local credentials, environment variables, SDK setup, or alternate account/setup routes as prerequisites. Do not write or run Python, HTML, SVG, canvas, PIL, PPTX, screenshot, or other scripts to draw final slide PNGs. Only the Codex image tool itself can block generation.
Generate slide PNG masters at `2048x1152` for review, PPTX, and PDF packaging. Treat `1672x941` as layout-coordinate basis only, not an output PNG size, and do not create alternate delivery PNG masters.

Use the embedded ACT system in the prompt builder: Noto Sans JP, 1672x941, near-white base, Petrol accent, compact header, real-source-only footer, and one editorial illustration tone.

Favor message-led structure, useful density, compact message boxes, exact visible text, meaningful graphics, thumbnail legibility, and clear reading path. Only `exact_text` may render visibly; workflow/audit metadata and speaker notes stay non-rendered.

Do not report complete while actual PNG review has blockers, majors, tone drift, weak content/design, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Returned Codex image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when needed, then package with `scripts/package_slide_images_to_pptx.py` or `scripts/package_slide_images_to_pdf.py`. Packaging scripts run only after approved Codex image artifacts exist; they never create, simulate, or replace slide images. PPTX/PDF outputs reference `slides_final/` master PNGs; `render_check/pdf_pages/` is rendered-back QA only, not a source image folder. Speaker notes are required for PPTX unless explicitly disabled.
