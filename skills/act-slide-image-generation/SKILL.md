---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ACT 16:9 strategy slide images from briefs, text, notes, screenshots, or deck outlines with gpt-image-2 and review-gated PNG/PPTX output."
---

# ACT Slide Image Generation

Use `scripts/build_act_slide_prompt.py` for deck or single-slide prompt scaffolds; it loads full runtime rules from `build/references`. Use `scripts/package_slide_images_to_pptx.py` only after approved PNGs, notes, and review manifest exist.

Route: final PNGs must come from Codex built-in image generation with `gpt-image-2`; never from PPTX export, screenshots, local rendering, HTML, SVG, canvas, or PIL. Flow: scaffold -> gpt-image-2 PNG -> full-deck review/repair -> approved manifest -> PPTX roll-up.

Design: Noto Sans JP, 12-column 1672x941, Petrol `#008A80`, Forest Charcoal `#2D332E`, mint `#F7FBF9`, quiet Honey `#F5E2A8/#C49A2C`, and one flat 2D editorial illustration style across people, UI, icons, linework, fills, crop, and face/body detail.

Structure: one claim and one dominant structure per slide. Add consulting-style density with charts, tables, matrices, flows, labels, drivers, comparisons, or evidence layers when they clarify the claim.

Completion: no complete status while any slide has blockers/majors, tone drift, weak content/design, unreadable text, broken header/footer/source, mixed illustration style, pending status, or non-empty `weak_slide_regeneration_queue`. Regenerate until all quality statuses are approved.

PPTX: `validate_review_manifest` must cover every PNG path and reject missing, partial, blocked, pending, or mismatched image sets. Speaker notes are required unless explicitly disabled.
