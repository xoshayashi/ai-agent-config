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

Core master: Noto Sans JP, near-white ACT surface, one fixed outer shell `x=72..1600 y=80..861` on the 1672x941 basis, 72px left/right and 80px top/bottom canvas padding, and a quiet text-only header aligned to the shell. Use H1 `x=72 y=80 w=1528`, one line, uniform 38pt/700 with 36pt emergency floor and 40pt cap. Use subtitle `x=72 y=126 w=1528`, 32pt/400 with 30pt floor and 34pt cap, in neutral gray `#626A64`. Keep the actual H1-to-subtitle glyph gap at 14-22px, target 18px. Place the first body mark at `y>=270` and keep 64-96px of quiet canvas below the subtitle.

Deck-wide header consistency lock: freeze the approved H1 and subtitle master before generating slide 1, then reuse it verbatim on every slide. H1 stays `38pt/700 #2D332E`, one line, at `x=72 y=80 w=1528`; subtitle stays `32pt/400 #626A64`, one line, at `x=72 y=126 w=1528`. Copy the same font family, weight, point size, color, line box, baseline, and width across the deck. Resolve fit through title rewriting, subtitle/body redistribution, or slide splitting while retaining the master. During actual-PNG review, compare all slides side by side and approve when H1 visible glyph heights differ by <=2px, subtitle heights differ by <=2px, and header baselines remain aligned after proportional scaling.

Header alignment lock: use left alignment as the default for every content, strategy, IR, proposal, and appendix slide. H1 and subtitle share the same left anchor `x=72`, fixed width `w=1528`, and ragged-right line ending. During actual-PNG review, require their first visible glyph x-coordinates to differ by <=2px and the H1 left edge to align with the main body grid within <=4px. Center alignment is reserved for an explicitly requested cover, interstitial, or closing slide and is recorded as `header_alignment_exception`; otherwise repair by left-aligning the complete H1/subtitle group without changing its internal spacing or type scale.

Title fit: estimate rendered width before freezing `exact_text`. Rewrite the title until the uniform 38pt line fits comfortably while retaining topic, change/tension, and implication. Move dates, scope qualifiers, and secondary clauses into subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

Header copy-budget lock: count Japanese text in full-width equivalents before generation. Keep H1 at <=28 full-width-equivalent characters and subtitle at <=36. Treat ASCII letters, digits, and spaces by their measured rendered width, using two half-width characters as roughly one full-width equivalent for the first-pass count. Passing the count remains subordinate to actual rendered-width fit. When either line exceeds its budget or fills more than 92% of the fixed text box, rewrite by removing setup phrases, dates, scope qualifiers, duplicated nouns, and secondary clauses; move necessary detail into body copy. Generation readiness requires both lines to pass the copy budget and width check while retaining the fixed deck-wide type master.

Visible outer-padding lock: approve padding from the actual rendered PNG rather than text-box coordinates. Measure `top_visible_margin` from the canvas top to the topmost meaningful title glyph and `bottom_visible_margin` from the canvas bottom to the lowest meaningful border or glyph. Require `abs(top_visible_margin - bottom_visible_margin) <= 4px` and record both values in review metadata. Resolve the signed difference symmetrically: when the top margin is larger, translate the complete header group upward by the measured difference while preserving its internal geometry and header/body clearance; when the bottom margin is larger, translate the complete bottom-most component downward by the difference; when either move would violate the safe shell, redistribute the body as one group. Preserve the fixed deck-wide type scale and corresponding normalized test at every approved output size.

Outer-padding correction priority: compare actual visible edges first, then choose the smallest edge-local translation that closes the measured difference. Keep the H1/subtitle together as one header group and keep a bottom evidence strip or footer together as one bottom group. Preserve internal gaps, alignment, font scale, and component dimensions during translation. Use the normalized difference ratio `abs(top_visible_margin - bottom_visible_margin) / canvas_height <= 0.005` for output sizes other than the 1672 basis.

Footer-aware balance: select `footer_mode` before layout. With no visible footer, use `available_content_band y=270..861`, bottom gap 26-80px, and soft optical target `y=595` with tolerance 12px. With a genuine visible Source or required note, use `available_content_band y=270..810`, bottom gap 30-80px, footer baseline `y=852`, and soft optical target `y=570` with tolerance 11px. Keep the horizontal optical target at `x=836` with tolerance 12px and left/right breathing within 16px.

Body balance: use edge margins and intentional-space coverage rather than forcing every visual family into one rectangular fill ratio. For T2-T4, keep body side margins 24-72px inside the outer shell; for T1, use 96-160px. Divide the available body band into a 4-column x 3-row review grid. Mark each cell as occupied or intentionally blank; allow up to five blank cells for T1, two for T2, and one for T3/T4. Preserve a single chart, diagram, or illustration aspect ratio within 5% and satisfy balance through margins, grouping, and declared blank cells. Prioritize shell bounds, >=20pt body text, edge margins, then optical-center refinement.

Content and evidence: preserve one governing thought, a connected action-title chain, a named exhibit element proving each title, MECE support, and declared inductive or deductive body logic. Use `ordinal_semantics_lock`: visible numbering carries sequence, rank, deductive, temporal, or causal meaning; parallel groups use position, alignment, and semantic labels.

Visible Source policy: render a Source footer only for a genuine, independently traceable published source such as an official report, public dataset, statute, research paper, or cited article with a stable title or URL. Keep meeting notes, transcripts, internal documents, uploads, filenames, company materials, and generated summaries in the source ledger or speaker notes with `source_line: none`.

Directive language: express generation and repair guidance as the desired visible state, selected route, measurable target, and next corrective action. Use verbs such as `use`, `keep`, `place`, `select`, `preserve`, `rewrite`, and `repair by`.

Completion requires actual-PNG multimodal review, approved content/design/deck-unity statuses, an empty `weak_slide_regeneration_queue`, and an approved package manifest. Notes live at `slides_package/speaker_notes.json` as ordered `slides[{slide_id, per_slide_time_budget_seconds, speaker_notes_text}]`.
