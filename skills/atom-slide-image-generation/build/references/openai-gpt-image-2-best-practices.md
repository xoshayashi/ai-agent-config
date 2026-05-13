# OpenAI GPT Image 2 Best Practices

Official sources checked:

- `https://developers.openai.com/api/docs/models/gpt-image-2`
- `https://developers.openai.com/api/docs/guides/image-generation`
- `https://developers.openai.com/api/docs/guides/tools-image-generation`
- `https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide`
- `https://openai.com/academy/image-generation/`

## Contents

- Generation Route
- Hard Delivery Rule
- Required GPT Image 2 Settings
- Prompt Shape For Slide Images
- Text And Dense Layout Rules
- Iteration And Repair
- Slide-Specific Quality Heuristics

## Generation Route

- For Codex skill use, final slide images should be generated with Codex's built-in image generation capability, not with a local credential implementation.
- Treat the built-in image generation capability as the correct `gpt-image-2` route when the user requests `gpt-image-2` inside Codex. Record `model_route_assumption: Codex built-in image generation is the gpt-image-2 route for this skill unless image metadata proves otherwise`.
- Official documentation examples are reference material for prompt/settings semantics only. Do not require local credential setup or add a local credential execution route in this skill.
- Do not pause slide generation to inspect local environment state; in Codex, start from the built-in image generation route.
- In progress updates, do not frame absent local credentials, environment variables, SDK setup, local save mechanics, or alternate account/setup routes as prerequisites. Say that structure planning and built-in image generation are starting.
- If the built-in image tool does not expose model selection, do not invent an API blocker; use the built-in generation route and report `generation_route: Codex built-in image generation`.
- Prompt builder scripts only create planning text and final prompts. Package scripts only wrap already-approved Codex image artifacts. Neither class of script may render, draw, screenshot, export, simulate, or replace final slide PNGs.

## Hard Delivery Rule

If the user asks for slide image generation, final images must come from `gpt-image-2`.

- Do not replace image generation with PIL, SVG, web-rendered screenshots, canvas, matplotlib, PowerPoint exports, or other deterministic rendering.
- Use Codex's built-in image generation function for final images.
- Prompt packs and local mockups are planning artifacts, not generated image deliverables.
- Do not write a new script to create final slide images when the request is for slide image generation. If a script is useful, it may only scaffold prompts, validate manifests, or package images that already came from Codex built-in image generation.
- If Codex built-in image generation is unavailable, stop with a blocker. Do not ask for local API credentials as the default fix and do not create substitute "final" images.
- For decks over 3 slides, generate 1-2 pilot slides first and inspect them before batch generation.

## Required GPT Image 2 Settings

Use these defaults for ATOM slide images:

```text
generation_mode: new_image / image_edit
image_model: gpt-image-2
image_size: 2048x1152 for generated slide output, review, PPTX packaging, and PDF packaging
image_size_label: 2048x1152 is the single 16:9 2K-width PNG master size; 1672x941 is layout-coordinate basis only
image_quality: low for fast layout drafts, medium/high for dense text or final slides
image_background: opaque or auto
image_output_format: png
image_output_compression: none for PNG slide masters
image_moderation: auto
image_n: 1 for final text-heavy slides; multiple variations only for drafts
image_streaming: optional for exploration, final QA uses completed image
generation_route: Codex built-in image generation
image_generation_tool_lock: final slide PNG pixels must be produced by Codex built-in image generation
script_boundary_lock: prompt/package scripts never render, draw, screenshot, export, simulate, or replace final slide PNGs
progress_update_route_lock: progress updates must not narrate local credentials, environment variables, SDK setup, save-route probing, or alternate account/setup routes as prerequisites
generation_status: generated_with_builtin_gpt-image-2 / blocked
```

Important size rule:

- `gpt-image-2` requires both edges to be multiples of `16`.
- `1920x1080` is not a valid direct generation size because `1080` is not divisible by `16`.
- Keep ATOM layout planning on the `1672x941` coordinate basis, but generate and package approved PNG masters at `2048x1152`.
- `2048x1152`: required 16:9 2K-width generated slide output for working review, final PNGs, PPTX packaging, and PDF packaging.
- Do not create separate `1920x1080`, `1672x941`, draft-size, QHD, or 4K delivery PNG masters for this skill.
- Strict cinema/DCI sizes such as `2048x1080` and `4096x2160` are not ATOM 16:9 slide targets; `4096x2160` also exceeds the current `3840px` maximum edge constraint for this workflow.

Other model constraints from the official references:

- Prompt length for GPT image models can be long enough for detailed slide specs, but keep the final prompt structured and only include text that should render.
- `n` can be used for variations when exploring, but generate one final text-heavy slide at a time for easier QA.
- `gpt-image-2` does not support transparent background. Requests with `background: "transparent"` fail.
- Omit `input_fidelity` for `gpt-image-2`; image inputs are processed at high fidelity automatically.
- `png` is the required slide-master format for this skill; do not use non-PNG masters.
- `moderation: "auto"` is the default and should remain the default for slide workflows.
- Streaming and partial images can provide earlier visual feedback during exploration; final decisions must use the completed image.
- Complex prompts and final-quality images may take up to about two minutes.
- Response-format parameters such as `b64_json` are not used by this skill's Codex built-in image-generation route.

## Temperature And Creative Variance

- In Codex built-in image-generation mode, this skill does not expose a model `temperature` parameter.
- When a user asks to raise temperature, translate that into `creative_variance: high` in the planning and prompt language.
- High creative variance should change composition, viewpoint, crop, region balance, visual metaphor, editorial rhythm, asymmetric composition, and viewpoint variation.
- High creative variance must not loosen exact text, source hygiene, header master, brand tokens, grid alignment, readability, or model route.
- For decks, test high variance with 1-2 pilot slides before generating the full set.

## Prompt Shape For Slide Images

Use a skimmable production template:

```text
Goal:
Create/draw a guideline-aware strategy slide image for [audience/use].

Image generation settings:
model=gpt-image-2
size=2048x1152
quality=high
background=opaque
format=png

Layout:
[coordinate-aware grid, regions, component inventory, x/y/w/h]

Exact text:
Render ONLY these text strings, verbatim:
- H1: "..."
- Subtitle: "..."
- Label 1: "..."

Style:
[embedded ATOM palette, typography, icon style, human-crafted rhythm]

Constraints:
[preserve grid, no extra text, brand-safe visual subject selection, source policy]

Negative prompt:
[things to avoid]

QA:
[post-generation checks]
```

## Text And Dense Layout Rules

- Put every literal on-slide string in quotes.
- Use `Render ONLY these text strings, verbatim:` to reduce extra text.
- Keep text short; reduce labels before asking the model to render many small words.
- Convert abstract messages into a concrete visual anchor before generation: name the observable scene or object, viewpoint/crop, and 2-4 specific visual details.
- Specify font style, size, color, and placement for text.
- Apply max_text_size_lock: no visible text may exceed 34pt; H1 max 34pt, subtitle max 30pt, message-box/Insight max 26pt, body/data labels max 24pt.
- For brand names or unusual words, spell them letter-by-letter.
- Ask for sharp text rendering and high contrast.
- Use `quality: "medium"` or `quality: "high"` for dense text, small labels, multi-font layouts, and final slides.
- For Japanese-heavy slide images, enlarge text, keep copy shorter than a normal PPT slide, and audit every rendered character after generation.
- Do not rely on bitmap generation for legal/financial fine print, dense citations, or production-perfect microtext.

## Iteration And Repair

- Start with a clean base prompt and refine through small, targeted revisions.
- Change one thing at a time when repairing: typography, grid, one text string, one color, or one region.
- For edits, use explicit preservation language:

```text
Change only [specific issue].
Keep everything else exactly the same: layout, grid, arrows, labels, source text position, typography hierarchy, colors, icons, and surrounding objects.
```

- Repeat critical invariants on every edit turn because image edits can drift.
- If the runtime revises prompts internally, inspect any visible revised prompt or generated result for drift; regenerate with a tighter prompt if ATOM constraints weaken.

## Slide-Specific Quality Heuristics

- Prefer low-quality built-in image-generation drafts for rough composition variants when the tool exposes quality controls.
- Move to `quality: "high"` for final ATOM slides with Japanese text, small labels, tables, diagrams, or brand-sensitive components.
- Generate one slide at a time for text-heavy slides; batch only when text is minimal or the slide family is simple.
- Use reference images for screenshot repair or style matching, but name each input explicitly: `Image 1: current slide render`, `Image 2: style reference`.
- Preserve the footer/source alignment position even when no Source text is rendered; do not draw a visible horizontal line for that baseline.
- Run a visual QA pass after generation, preferably with high-detail/original vision inspection for dense screenshots.
- Model/route QA must explicitly confirm the image used Codex built-in image generation, not local rendering.
- Script-boundary QA must explicitly confirm that any prompt builder or packaging script was not used to create the final PNG pixels.
