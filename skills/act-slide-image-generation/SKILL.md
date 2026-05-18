---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Use `scripts/build_act_slide_prompt.py` only to scaffold planning blocks and image prompts; full rules live in `build/references`. Prompt/package scripts are helpers, never final image renderers.

Route: scaffold -> Codex built-in gpt-image-2 PNGs -> review/repair -> approved manifest -> PPTX/PDF roll-up.

Start Codex built-in image generation directly. Do not run local preflight, account/credential/token/SDK/env setup, artifact-route probing, save-route probing, or local substitute generation. Progress updates should say that slide structure and built-in image generation are starting; they must not narrate missing local credentials, environment variables, SDK setup, or alternate account/setup routes as prerequisites. Do not write or run Python, HTML, SVG, canvas, PIL, PPTX, screenshot, or other scripts to draw final slide PNGs. Only the Codex image tool itself can block generation.
Generate slide PNG masters at `2048x1152` for review, PPTX, and PDF packaging. Treat `1672x941` as layout-coordinate basis only, not an output PNG size, and do not create alternate delivery PNG masters.
Apply `nonconforming_existing_png_regeneration_lock`: if existing or user-provided PNGs are `1672x941` or any non-approved size, do not stop at the package-script rejection and do not convert, upscale, HTML-render, API-render, or locally redraw them. Reuse the approved slide specification and start Codex built-in gpt-image-2 generation for new `2048x1152` `slides_final/` masters, then review and package those generated masters.

Use the embedded ACT system in the prompt builder: Noto Sans JP, 1672x941, near-white base, Petrol accent, compact header, real-source-only footer, and one editorial illustration tone.

Favor message-led structure, useful density, compact and occasional message boxes, exact visible text, meaningful graphics, thumbnail legibility, and clear reading path. The highest-priority rules stay fixed: exact `exact_text` only, the locked header master, and real-source-only footers. Only `exact_text` may render visibly; workflow/audit metadata and speaker notes stay non-rendered.

Story logic: during slide-structure planning, apply `impact_clarity_density_gate`, `message_sharpness_lock`, and `evidence_compression_ladder` so each slide has a sharp takeaway, self-explanatory logic, simple dominant structure, and enough decision-relevant proof before image prompting. Apply `pyramid_logic_lock` and `mece_support_gate` so the deck has one stated governing thought, each action title answers the question its predecessor raises with a named exhibit element, and within-slide supporting points are mutually exclusive and collectively exhaustive with a declared inductive or deductive `body_logic`.

Density and copy: apply `sentence_density_lift_lock` and `semantic_copy_gate` so body labels, card rows, annotations, and optional Insight use compact meaningful clauses or short sentences that explain relationship, reason, consequence, or decision relevance; avoid icon-and-keyword-only slides and noun-only card grids. Apply `icon_restraint_lock` and `icon_density_budget`: icons are quiet wayfinding or evidence markers, not the main content layer, and must be removed when a short sentence, mini table, causal chain, or labeled diagram communicates better.

Chart craft: on chart, table, and matrix slides apply `chart_emphasis_lock` (gray out non-focal data, place the decision-carrying number as a direct on-mark label, label series directly instead of using a legend), `encoding_consistency_lock` (same meaning keeps the same fill/color/shape and scale across the deck, no distinction relies on hue alone), and `number_format_normalization_lock` (normalize decimal precision, magnitude abbreviation, axis ticks, and period notation before freezing exact_text). The `chart_emphasis_lock` focal layer (accent on the focal element, neutral gray on non-focal data) overrides category hue on a given slide and is not an `encoding_consistency_lock` violation; encoding consistency governs how a category looks when it is shown in its own right.

Message boxes: apply `insight_absence_default_lock` and `insight_justification_required`: many slides should have no message box; keep one only when it adds a non-redundant interpretation, decision signal, or reading bridge. Apply `honey_selective_signal_lock` and `honey_justification_required`: Honey starts absent and appears only as a justified quiet bottom decision signal, never as a default message-box color or decorative yellow surface.

Do not report complete while actual PNG review has blockers, majors, tone drift, weak content/design, source/header issues, pending status, or non-empty `weak_slide_regeneration_queue`.

Returned Codex image artifacts are the authoritative PNGs. Materialize approved artifacts under `slides_final/` only when needed, then package with `scripts/package_slide_images_to_pptx.py` or `scripts/package_slide_images_to_pdf.py`. Packaging scripts run only after approved Codex image artifacts exist; they never create, simulate, or replace slide images. PPTX/PDF outputs reference `slides_final/` master PNGs; `render_check/pdf_pages/` is rendered-back QA only, not a source image folder. Speaker notes are required for PPTX unless explicitly disabled, and apply `speaker_notes_persuasion_lock`: notes stage current-state vs intended-future tension, balance logos with selective ethos and pathos, end with a landing sentence and a signpost transition, and add a justified hook, objection pre-empt, or deck-language delivery markers only where they help.
