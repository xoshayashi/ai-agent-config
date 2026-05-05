---
name: act-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ACT 16:9 strategy slide images from briefs, text, notes, screenshots, or deck outlines. Final PNGs use gpt-image-2 via Codex built-in image generation; local renders are sketches only."
---

# ACT Slide Image Generation

The ACT design system is embedded in this SKILL.md; do not read an external ACT slide pattern file. Details live in `references/prompt-recipes.md`, `references/text-to-slide-structure.md`, and `references/openai-gpt-image-2-best-practices.md`.

Mandatory: final images use `gpt-image-2` through Codex built-in image generation; first PNGs need review and repair; speaker notes accompany PPTX; Create Google Slides only when explicitly requested.

Generation route lock: PPTX is a delivery wrapper only; never use PPTX, PowerPoint export, screenshots, local rendering, HTML, SVG, canvas, or PIL to create final PNGs. Correct order: gpt-image-2 PNG generation -> PNG review/repair -> PPTX roll-up. If gpt-image-2 image generation is blocked, stop rather than manufacturing final PNGs through PPTX or local rendering.

Source line lock: `source_line_lock: render Source: ... when traceable sources exist; use source_line: none only when no traceable source exists`. Do not drop real source names to reduce visual density; shorten or group source names instead.

Design: `12-column grid`, `1672x941`, `#008A80`, `#2D332E`, `#F7FBF9`, `#F5E2A8`, `#C49A2C`, footer/source/table-note text `#6E756E`, `all_text_font_lock: Noto Sans JP for every visible string including Latin/English/numbers/symbols/Japanese`, `header_footer_text_color_lock`, `header_line_top_rule`, `no_header_ranges_in_final_prompts`, `petrol_usage_lock`, `message_box_scale_lock`, `message_box_text_size_lock`, `flat solid fill`, Honey surfaces must feel quieter than Petrol surfaces, `technical editorial line illustration`.

Logic: `1 slide = 1 claim`, `1 slide = 1 dominant structure`, Do not impose a default numeric cap, `visual_design_quality_traits`, `visual_asset_judgment`, `layout_diversity_plan`, `layout_rotation_guard`, `layout_sequence_table`, `right-main + left-context-rail`, `center-hub + surrounding-nodes`, `top-map + bottom-detail-table`, `bottom-main compact`.

Opening: use `opening_thesis_slide`, `first_slide_not_title_only`, and `opening_density_gate`; the first slide may be catchy, but it must carry a real thesis, 2-4 proof/tension points, a visible market-shift / matrix / causal-map / wedge structure, and a bridge into the deck.

Output keys: `generation_route: Codex built-in image generation`, `image_model: gpt-image-2`, `speaker_notes_text`, `pre_google_slides_image_review`, `pre_package_image_review`, `image_review_matrix`, `deck_consistency_matrix`, `final_image_quality_status`, `deck_tone_master_lock`, `deck_tone_consistency_status`, `post_generation_design_balance_check`, `whitespace_occupancy_balance_status`, `typography_balance_status`, `color_consistency_status`, `outer_padding_consistency_status`, `header_integrity_status`, `coordinate_inventory_1672`, `master_components`, `source_policy`, `prompt_readiness`, `draft_image_prompt_scaffold`, `negative_prompt_hard_blockers`, `repair_iteration_plan`.

Do not label a prompt final while `layout_archetype`, `layout_family`, `layout_sequence_table`, `grid_mode`, `coordinate_inventory_1672`, `master_components`, `source_policy`, `speaker_notes_text`, `opening_density_gate`, or `image_review_matrix` is unresolved.

Review: use `pre_package_image_review`, `pre_google_slides_image_review`, `post_generation_design_balance_check`, `image_review_matrix`, and `deck_consistency_matrix`; approve only when `final_image_quality_status: approved` and `deck_tone_consistency_status: approved`.

PPTX Roll-Up / PPTX package gate: use `scripts/package_slide_images_to_pptx.py`, one approved PNG per slide, full-bleed, with `pptx_slide_count`, `pptx_image_mapping`, and `pptx_speaker_notes_mapping`. Scaffold prompts with `scripts/build_act_slide_prompt.py`.
