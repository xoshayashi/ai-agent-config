---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX/PDF-packaging ACT 16:9 strategy slide images with gpt-image-2."
---

# ACT Slide Image Generation

Read only the reference required for the current phase:

- `build/references/core-layout-and-typography.md` for geometry, title fit, rendered type, and balance
- `build/references/content-and-story.md` for brief-to-deck reasoning, evidence, density, and ordinal semantics
- `build/references/generation-review-packaging.md` for production, repair, review, and delivery
- `build/references/prompt-recipes.md` when a concrete prompt scaffold is needed
- `build/references/openai-gpt-image-2-best-practices.md` when model/tool semantics need confirmation

Use `scripts/build_act_slide_prompt.py` for planning scaffolds. Produce each final master directly with Codex built-in `gpt-image-2`, keep approved masters in `slides_final/`, inspect the actual PNGs, repair until approved, then package with `scripts/package_slide_images_to_pptx.py` or `scripts/package_slide_images_to_pdf.py`.

Core master: Noto Sans JP, near-white ACT surface, one fixed outer shell `x=72..1600 y=80..861` on the 1672x941 basis, 72px left/right and 80px top/bottom canvas padding, and a quiet text-only header aligned to the shell. Use H1 `x=72 y=80 w=1528`, one line, uniform 40pt/700 with 36pt emergency floor and 42pt cap. Use subtitle `x=72 y=126 w=1528`, 32pt/400 with 30pt floor and 34pt cap. Keep the actual H1-to-subtitle glyph gap at 14-22px, target 18px. Place the first body mark at `y>=270` and keep 64-96px of quiet canvas below the subtitle.

Title fit: estimate rendered width before freezing `exact_text`. Rewrite the title until the uniform 40pt line fits comfortably while retaining topic, change/tension, and implication. Move dates, scope qualifiers, and secondary clauses into subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

Footer-aware balance: select `footer_mode` before layout. With no visible footer, use `available_content_band y=270..861`, bottom gap 26-80px, and soft optical target `y=595` with tolerance 12px. With a genuine visible Source or required note, use `available_content_band y=270..810`, bottom gap 30-80px, footer baseline `y=852`, and soft optical target `y=570` with tolerance 11px. Keep the horizontal optical target at `x=836` with tolerance 12px and left/right breathing within 16px.

Body balance: use edge margins and intentional-space coverage rather than forcing every visual family into one rectangular fill ratio. For T2-T4, keep body side margins 24-72px inside the outer shell; for T1, use 96-160px. Divide the available body band into a 4-column x 3-row review grid. Mark each cell as occupied or intentionally blank; allow up to five blank cells for T1, two for T2, and one for T3/T4. Preserve a single chart, diagram, or illustration aspect ratio within 5% and satisfy balance through margins, grouping, and declared blank cells. Prioritize shell bounds, >=20pt body text, edge margins, then optical-center refinement.

Content and evidence: preserve one governing thought, a connected action-title chain, a named exhibit element proving each title, MECE support, and declared inductive or deductive body logic. Use `ordinal_semantics_lock`: visible numbering carries sequence, rank, deductive, temporal, or causal meaning; parallel groups use position, alignment, and semantic labels.

Visible Source policy: render a Source footer only for a genuine, independently traceable published source such as an official report, public dataset, statute, research paper, or cited article with a stable title or URL. Keep meeting notes, transcripts, internal documents, uploads, filenames, company materials, and generated summaries in the source ledger or speaker notes with `source_line: none`.

Directive language: express generation and repair guidance as the desired visible state, selected route, measurable target, and next corrective action. Use verbs such as `use`, `keep`, `place`, `select`, `preserve`, `rewrite`, and `repair by`.

Completion requires actual-PNG multimodal review, approved content/design/deck-unity statuses, an empty `weak_slide_regeneration_queue`, and an approved package manifest. Notes live at `slides_package/speaker_notes.json` as ordered `slides[{slide_id, per_slide_time_budget_seconds, speaker_notes_text}]`.
