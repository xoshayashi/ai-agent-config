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

- For Codex skill use, final slide images should be generated with Codex's built-in image generation capability, not with a user-key implementation.
- Treat the built-in image generation capability as the correct `gpt-image-2` route when the user requests `gpt-image-2` inside Codex.
- Official documentation examples are reference material for prompt/settings semantics only. Do not require `OPENAI_API_KEY` or add a user-key execution route in this skill.
- If the built-in image tool does not expose model selection, do not invent an API blocker; use the built-in generation route and report `generation_route: Codex built-in image generation`.

## Hard Delivery Rule

If the user asks for slide image generation, final images must come from `gpt-image-2`.

- Do not replace image generation with PIL, SVG, web-rendered screenshots, canvas, matplotlib, PowerPoint exports, or other deterministic rendering.
- Use Codex's built-in image generation function for final images.
- Prompt packs and local mockups are planning artifacts, not generated image deliverables.
- If Codex built-in image generation is unavailable, stop with a blocker. Do not ask for `OPENAI_API_KEY` as the default fix and do not create substitute "final" images.
- For decks over 3 slides, generate 1-2 pilot slides first and inspect them before batch generation.

## Required GPT Image 2 Settings

Use these defaults for ACT slide images:

```text
generation_mode: new_image / image_edit
image_model: gpt-image-2
image_size: 1536x864 for drafts, 2048x1152 for working review, 2560x1440 for final high-fidelity 16:9
image_size_label: 1920x1080 is FHD delivery only; 2048x1152 is 16:9 2K-width; 3840x2160 is 4K UHD
image_quality: low for fast layout drafts, medium/high for dense text or final slides
image_background: opaque or auto
image_output_format: png
image_output_compression: only when output_format is jpeg or webp
image_moderation: auto
image_n: 1 for final text-heavy slides; multiple variations only for drafts
image_streaming: optional for exploration, final QA uses completed image
generation_route: Codex built-in image generation
generation_status: generated_with_builtin_gpt-image-2 / blocked
```

Important size rule:

- `gpt-image-2` requires both edges to be multiples of `16`.
- `1920x1080` is not a valid direct generation size because `1080` is not divisible by `16`.
- Keep ACT planning and delivery thinking in `1920x1080`, but generate at `1536x864`, `2048x1152`, or `2560x1440`, then resize to `1920x1080` if exact delivery dimensions are required.
- `1536x864`: fast draft layout and composition checks.
- `2048x1152`: 16:9 2K-width working review when you need more detail without jumping to the largest practical size.
- `2560x1440`: recommended high-fidelity final 16:9 slide image size.
- `3840x2160`: valid 16:9 4K UHD size, but use only when explicitly requested because it is more expensive, slower, and may be more variable.
- Strict cinema/DCI sizes such as `2048x1080` and `4096x2160` are not ACT 16:9 slide targets; `4096x2160` also exceeds the current `3840px` maximum edge constraint for this workflow.

Other model constraints from the official references:

- Prompt length for GPT image models can be long enough for detailed slide specs, but keep the final prompt structured and only include text that should render.
- `n` can be used for variations when exploring, but generate one final text-heavy slide at a time for easier QA.
- `gpt-image-2` does not support transparent background. Requests with `background: "transparent"` fail.
- Omit `input_fidelity` for `gpt-image-2`; image inputs are processed at high fidelity automatically.
- `png` is the fidelity-safe default. `jpeg` is faster; `webp` or `jpeg` may use `output_compression`.
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
size=2560x1440
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
[embedded ACT palette, typography, icon style, human-crafted rhythm]

Constraints:
[preserve grid, no extra text, no logos, no stock imagery, source policy]

Negative prompt:
[things to avoid]

QA:
[post-generation checks]
```

## Text And Dense Layout Rules

- Put every literal on-slide string in quotes.
- Use `Render ONLY these text strings, verbatim:` to reduce extra text.
- Keep text short; reduce labels before asking the model to render many small words.
- Specify font style, size, color, and placement for text.
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
Keep everything else exactly the same: layout, grid, arrows, labels, source baseline, typography hierarchy, colors, icons, and surrounding objects.
```

- Repeat critical invariants on every edit turn because image edits can drift.
- If the runtime revises prompts internally, inspect any visible revised prompt or generated result for drift; regenerate with a tighter prompt if ACT constraints weaken.

## Slide-Specific Quality Heuristics

- Prefer low-quality built-in image-generation drafts for rough composition variants when the tool exposes quality controls.
- Move to `quality: "high"` for final ACT slides with Japanese text, small labels, tables, diagrams, or brand-sensitive components.
- Generate one slide at a time for text-heavy slides; batch only when text is minimal or the slide family is simple.
- Use reference images for screenshot repair or style matching, but name each input explicitly: `Image 1: current slide render`, `Image 2: style reference`.
- Preserve footer/source baseline even when no Source text is rendered.
- Run a visual QA pass after generation, preferably with high-detail/original vision inspection for dense screenshots.
- Model/route QA must explicitly confirm the image used Codex built-in image generation, not local rendering.
