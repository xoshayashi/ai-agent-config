---
name: atom-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ATOM 16:9 strategy slide images with gpt-image-2."
---

# ATOM Slide Image Generation

Use `scripts/build_atom_slide_prompt.py` only to scaffold planning blocks and image prompts; full rules live in `build/references`. Prompt/package scripts are helpers, never final image renderers.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX/PDF roll-up.

Start Codex built-in image generation directly. Do not run local preflight, account/credential/token/SDK/env setup, artifact-route probing, save-route probing, or local substitute generation. Progress updates should say that slide structure and built-in image generation are starting; they must not narrate missing local credentials, environment variables, SDK setup, or alternate account/setup routes as prerequisites. Do not write or run Python, HTML, SVG, canvas, PIL, PPTX, screenshot, or other scripts to draw final slide PNGs. Only the Codex image tool itself can block generation.
Generate slide PNG masters at `2048x1152` for review, PPTX, and PDF packaging. Treat `1672x941` as layout-coordinate basis only, not an output PNG size, and do not create alternate delivery PNG masters.

Use the embedded ATOM system in the prompt builder: Noto Sans JP, 1672x941, light neutral base, Deep Blue accent, compact header, real-source-only footer, and one editorial illustration tone.

Favor message-led structure, useful density, compact and occasional message boxes, exact visible text, meaningful graphics, thumbnail legibility, and clear reading path. During slide-structure planning, apply `impact_clarity_density_gate`, `message_sharpness_lock`, and `evidence_compression_ladder` so each slide has a sharp takeaway, self-explanatory logic, simple dominant structure, and enough decision-relevant proof before image prompting. Apply `insight_absence_default_lock` and `insight_justification_required`: many slides should have no message box; keep one only when it adds a non-redundant interpretation, decision signal, or reading bridge. Apply `honey_selective_signal_lock` and `honey_justification_required`: Honey starts absent and appears only as a justified quiet bottom decision signal, never as a default message-box color or decorative yellow surface. Only `exact_text` may render visibly; workflow/audit metadata and speaker notes stay non-rendered.

Do not report complete while actual PNG review has blockers, majors, tone drift, weak content/design, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Returned Codex image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when needed, then package with `scripts/package_slide_images_to_pptx.py` or `scripts/package_slide_images_to_pdf.py`. Packaging scripts run only after approved Codex image artifacts exist; they never create, simulate, or replace slide images. PPTX/PDF outputs reference `slides_final/` master PNGs; `render_check/pdf_pages/` is rendered-back QA only, not a source image folder. Speaker notes are required for PPTX unless explicitly disabled.
