---
name: atom-slide-image-generation
description: "Use when generating, reviewing, repairing, or PPTX-packaging ATOM 16:9 strategy slide images from briefs, text, notes, screenshots, or deck outlines. Final PNGs use gpt-image-2 via Codex built-in image generation; local renders are sketches only."
---

# ATOM Slide Image Generation

The ATOM design system is embedded in this SKILL.md; do not read an external ATOM slide pattern file. Details live in `references/prompt-recipes.md`, `references/text-to-slide-structure.md`, and `references/openai-gpt-image-2-best-practices.md`.

Mandatory: final images use `gpt-image-2` through Codex built-in image generation; first PNGs need review and repair; speaker notes accompany PPTX; Create Google Slides only when explicitly requested.

Design: `12-column grid`, `1672x941`, `#0B2F5B`, `#2D332E`, `#DDE3EA`, `#F7EECF`, `#C49A2C`, footer/source/table-note text `#6E756E`, `all_text_font_lock: Noto Sans JP for every visible string including Latin/English/numbers/symbols/Japanese`, `header_footer_text_color_lock`, `header_line_top_rule`, `no_header_ranges_in_final_prompts`, `deep_blue_usage_lock`, `brand_accent_usage_budget`, `message_box_scale_lock`, `message_box_text_size_lock`, `flat solid fill`, Honey surfaces must feel quieter than Deep Blue surfaces, `technical editorial line illustration`.

Logic: `1 slide = 1 claim`, `1 slide = 1 dominant structure`, Do not impose a default numeric cap, `visual_design_quality_traits`, `visual_asset_judgment`, `layout_diversity_plan`, `layout_rotation_guard`, `layout_sequence_table`, `right-main + left-context-rail`, `center-hub + surrounding-nodes`, `top-map + bottom-detail-table`, `bottom-main compact`.

Output keys: `generation_route: Codex built-in image generation`, `image_model: gpt-image-2`, `speaker_notes_text`, `pre_google_slides_image_review`, `pre_package_image_review`, `image_review_matrix`, `deck_consistency_matrix`, `final_image_quality_status`, `deck_tone_master_lock`, `deck_tone_consistency_status`, `post_generation_design_balance_check`, `whitespace_occupancy_balance_status`, `typography_balance_status`, `color_consistency_status`, `outer_padding_consistency_status`, `header_integrity_status`, `coordinate_inventory_1672`, `master_components`, `source_policy`, `prompt_readiness`, `draft_image_prompt_scaffold`, `negative_prompt_hard_blockers`, `repair_iteration_plan`.

Do not label a prompt final while `layout_archetype`, `layout_family`, `layout_sequence_table`, `grid_mode`, `coordinate_inventory_1672`, `master_components`, `source_policy`, `speaker_notes_text`, or `image_review_matrix` is unresolved.

Review: use `pre_package_image_review`, `pre_google_slides_image_review`, `post_generation_design_balance_check`, `image_review_matrix`, and `deck_consistency_matrix`; approve only when `final_image_quality_status: approved` and `deck_tone_consistency_status: approved`.

PPTX Roll-Up / PPTX package gate: use `scripts/package_slide_images_to_pptx.py`, one approved PNG per slide, full-bleed, with `pptx_slide_count`, `pptx_image_mapping`, and `pptx_speaker_notes_mapping`. Scaffold prompts with `scripts/build_atom_slide_prompt.py`.
