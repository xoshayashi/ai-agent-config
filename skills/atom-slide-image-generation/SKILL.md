---
name: atom-slide-image-generation
description: "Create ATOM-style 16:9 strategy slide image prompts and actual gpt-image-2 bitmap slide images from briefs, long text, notes, screenshots, rendered slide images, or deck outlines. Use as the primary skill for ATOM slide-structure planning, ATOM bitmap/image-prompt planning, Codex built-in image generation, critique, iterative pre-Google Slides image self-review, repair, and image-only Google Slides roll-up with speaker notes. The ATOM design system is embedded in this SKILL.md; do not load or depend on an external ATOM slide pattern file. When the user asks for slide image generation, do not substitute deterministic renders, screenshots, or exports for gpt-image-2 output."
---

# ATOM Slide Image Generation

## Purpose

Create ATOM strategy slide image specifications and final `gpt-image-2` prompts. This skill is self-contained: do not read an external ATOM slide pattern file to know the design system. Long text is first converted into a deck storyline and per-slide structure; each slide then keeps one claim, one dominant structure, fixed header/footer anchors, object-level coordinates, master components, selective Insight components, ATOM visual language, and speaker notes for Google Slides delivery.

Generate final bitmap slide images with Codex's built-in image generation capability, treating that as the `gpt-image-2` route when the user asks for `gpt-image-2`. Do not silently substitute another model, a code-rendered slide, or a user-key implementation.

For multi-slide image decks, assemble the approved generated PNGs into an image-only native Google Slides deck at the end of the workflow unless the user explicitly asks for image files only. The Google Slides deck is a delivery wrapper: each slide is one full-bleed generated slide image in the same order, with speaker notes attached to the corresponding slide. It is not a replacement for `gpt-image-2` generation and not a claim that the slide contents are editable objects.

Do not treat first generated images as complete. Before any Google Slides insertion, run a multimodal self-review on the actual generated PNGs, repair and regenerate failed slides, and repeat until the slide images are judged presentation-quality against the ATOM gates below.

## Non-Negotiable Generation Rule

When the user asks to `generate`, `create`, `output`, `export`, or `produce` slide images, the deliverable must be actual image-generation output from `gpt-image-2`.

- Do not satisfy the request with PIL, SVG, web-rendered screenshots, canvas, matplotlib, PowerPoint export, or another deterministic local renderer.
- Use Codex's built-in image generation capability for final slide images. Do not switch to a user-key implementation inside this skill.
- If the built-in image tool does not expose model selection, still use the built-in image generation path and record `generation_route: Codex built-in image generation`; do not invent an API-key requirement.
- Do not package prompt files, contact sheets, or locally rendered previews as the completed image deliverable.
- Google Slides roll-up is allowed only after actual generated slide images exist. It must not be used to disguise screenshots, local renders, HTML exports, or PPT exports as generated slide images.
- Google Slides insertion is allowed only after `pre_google_slides_image_review` has approved every generated image. Do not create the Slides deck as the completion step immediately after first image generation.
- Speaker notes are required for Google Slides roll-up unless the user explicitly refuses them. Notes are presentation support text, not on-slide content, and must not add unsupported factual claims or invented sources.
- Local rendering is allowed only as an internal wireframe/layout sketch, clearly labeled as non-final, or when the user explicitly asks for code-rendered assets.
- If built-in image generation is unavailable in the session, mark image generation as blocked and ask for a Codex image-generation route. Do not require `OPENAI_API_KEY` and do not continue by creating faux final images.
- For large decks, first produce a deck plan and 1-2 `gpt-image-2` pilot slides, review the visual quality, then batch the rest.

## Embedded ATOM Design System

### 0. Premise

- The coordinate basis is `1672x941`. Plan every object in this coordinate system before generating or scaling.
- The presentation delivery target is `1920x1080`; use it as the visual target, not necessarily the direct image-generation size.
- The slide should feel like an ATOM strategy document: calm, structured, slightly dense, claim-led, and designed with visible editorial judgment.
- Do not show page numbers. The reading start is created only by the left vertical line, H1, and subtitle.
- Header visual inventory is exactly three items: left vertical line, H1 title, subtitle.
- Slide title equals H1. H1 is the slide claim itself.
- Numbering belongs inside body step badges only when the body truly shows sequence, phase, or process.
- The grammar is `role / region / edge / rhythm`: choose card count, left-right split, and conclusion surface naturally from the slide claim.

### 1. Core Rules

- `1 slide = 1 claim`.
- `1 slide = 1 dominant structure`.
- Before image generation, define `deck_tone_master_lock` and reuse it through the whole deck. This prevents late-deck tone drift.
- Use a calm, dense operating-deck look: light neutral base, fixed compact header, precise thin-line grid, equalized pale cards/tables, restrained line icons, small technical editorial illustrations, and one quiet interpretation surface when useful.
- Major regions are max 3. A repeated table, row system, card group, or panel group counts as 1 region when it is one system.
- Information density may be slightly high, but body text remains `18pt` equivalent or larger.
- Do not impose a default numeric cap. Keep as many decision-relevant numbers, denominators, comparisons, units, and assumptions as the slide can keep legible and well-grouped.
- H1 is `30-34pt`; subtitle is `26-30pt`; body is around `18pt`.
- Use `30-32pt` H1 for long Japanese titles; use `34pt` only for short mixed alphanumeric titles.
- Slide beauty comes from structure, typography, numbers, whitespace, rules, and quiet visual rhythm.
- Use illustrations and icons when they help the reader understand, remember, compare, or navigate the claim; they are not mandatory on every slide.
- Use small symbols and icons as reading anchors, category markers, evidence cues, or step markers; avoid decorative icon scattering.
- Use no realistic photos. Translate sites, people, products, robots, facilities, stores, factories, and cities into diagrams, line drawings, table icons, or editorial illustrations.
- Illustration should be edited and designer-authored, not rough hand-drawn, glossy AI concept art, photoreal, cinematic, or decorative pseudo-3D.
- Insight components are selective. Use them only when they advance interpretation, decision, turning point, conclusion, or reading speed.
- Source contains only traceable real information sources. Draft names, upload filenames, production notes, internal memos, or original manuscript labels never appear in Source.
- Grid fidelity is a quality condition before decoration.

Deck tone master:

- deck_tone_master_lock includes slide base, typography scale, header/footer lock, Deep Blue usage, Honey usage, illustration style, density rhythm, whitespace/occupancy rhythm, card/table geometry, outer padding, Source baseline, and negative prompt.
- Use the first 1-2 approved pilot slides as `deck_consistency_reference`; later slides must feel like the same deck, not a new template.
- tone_drift_guard: review the last third of a deck against the first third. Block if later slides become more saturated, more glossy, more illustrated, more card-heavy, more icon-heavy, darker, or looser in spacing without an explicit section reason.
- Section opener or closing slides may vary composition, but not palette roles, header/footer, typography scale, illustration language, message-box treatment, or source behavior.
- Keep the mix stable: if early slides use restrained line illustration and structured tables, later slides should use the same family of linework, fills, icons, card radius, and rule weights.

Visual design quality traits:

- Overall feel: an investor/strategy operating deck, not a poster. Calm, precise, information-rich, with visible human editorial hierarchy.
- Canvas use: body regions should feel usefully occupied while retaining clean margins. Avoid both dead blank zones and edge-to-edge crowding; a strong slide usually has a filled main field plus one controlled rail, strip, or conclusion surface.
- Surfaces: use pale solid Light Gray cards/tables with thin rules, small radii, consistent padding, and equalized heights. Prefer a single component skeleton reused across table cells, cards, rails, and process nodes.
- Lines: use crisp, thin structural lines and dividers. Strong borders, heavy shadows, thick boxes, or decorative outlines make the deck feel less precise and less human-edited.
- Header: the same compact header master appears on every slide. The body begins below the same visual y-line, and no illustration, chart, badge, or card enters the header shell.
- Typography: H1 leads, subtitle supports, body labels and table text are compact but legible. Section labels, row labels, and tiny chart annotations stay subordinate to the H1/subtitle hierarchy.
- Color: Deep Blue is the only strong recurring color and reads as one system per slide. Pale gray fills and Charcoal Ink carry most of the page. Honey is rare, pale, flat, and used for interpretation only.
- Icons: use small, consistent line icons as semantic anchors inside circles, table cells, cards, process badges, or evidence strips. Icon families, stroke weight, circle size, and color logic stay consistent across the deck.
- Illustration: use small technical editorial line drawings embedded in the layout, such as facility cuts, shelves, roads, bridges, devices, hands, tools, partial robots, and simple operating scenes. Keep them flat, quiet, and explanatory; avoid big hero art.
- Density: density comes from organized panels, small multiples, KPI strips, labels, arrows, and annotations. Do not increase density through noisy decoration, random icon scatter, or smaller unreadable text.
- Freshness: make the slide feel fresh through a precise viewpoint, an elegant table/diagram hybrid, a memorable small line illustration, or a clean spatial relationship. Do not use pseudo-3D, trapezoids, tilted slabs, dramatic perspective, glow, or cinematic concept art.

Visual asset judgment:

- visual_asset_judgment: every generated slide should decide whether an illustration/icon system helps the claim, and briefly state the reason.
- Use roles such as `integrated_line_illustration`, `margin_vignette`, `icon_evidence_strip`, `diagram_embedded_icons`, `process_icons`, `data_icon_markers`, or `none`.
- Chapter openers, turning points, and final vision slides often benefit from `integrated_line_illustration` or `margin_vignette`, but only when it adds memory or emotional clarity.
- Evidence, market, economics, and roadmap slides often benefit from `icon_evidence_strip`, `diagram_embedded_icons`, `process_icons`, or `data_icon_markers`, but only when they improve scanning or comparison.
- Icons and illustrations must explain the claim: actor, task, object, constraint, flow, environment, risk, or outcome. Do not use generic decorative symbols.
- Keep illustration intensity mostly `1_marginal` or `2_integrated`; use `3_restrained_signature` only for a small number of memorable slides.
- Icon style is deck-locked: Lucide-like line icons, consistent stroke, consistent circle/label geometry, same color logic, and no mixed icon families.

### 2. Grid Strategy

Coordinate and conversion:

| Use | Basis | Conversion |
| --- | ---: | --- |
| reference / coordinate inventory | `1672x941` | source coordinate system |
| image generation visual target | `1920x1080` | `x * 1.1483`, `y * 1.1477` |
| PPT 16:9 | `960x540 pt` | `x * 0.5742`, `y * 0.5739` |

12-column grid:

- Always use a shared 12-column grid.
- Outer margin on `1672` basis: left/right `44-56px`, top/bottom `24-52px`.
- Outer margin on `1920` basis: left/right `50-64px`, top/bottom `28-60px`.
- Gutter is `24px` or `32px`; keep it fixed within a deck.
- Spacing rhythm is `8px`; use `4px` only for final optical correction.
- Object gap: minimum `12px`, standard `16-24px`, large region gap `40-56px`.
- Major object left/right edges must snap to column lines.
- Column-spanning objects use integer columns.
- At least 3 of a major region's `left / right / top / bottom` edges should align to a column line, row track, outer shell, or deck master line.
- Same-row cards, tables, process nodes, and persona cards share top edge, bottom edge, and center line.
- Tables, phase cards, matrix cells, and process lanes require `row_tracks` and `column_tracks` before generation.
- Icon circles use shared diameter and center coordinate.
- Hand-placed exceptions max 2 per slide; allowed only for overlap badges, optical icon correction, or arrow connection points.

Grid modes:

| Mode | Use | Typical structure | Split |
| --- | --- | --- | --- |
| `full-12` | wide table, roadmap, governance | one broad integrated field | no split |
| `60/40` | left main figure + right rail | flow + rail, matrix + rail | separator x `1015-1035` |
| `70/30` | large left table/figure + helper rail | market table + interpretation rail | separator x `1145-1168` |
| `3-column` | parallel comparison | markets, personas, product groups | fixed `24-32px` gaps |
| `4-phase` | horizontal time | GTM roadmap, phase plan | equalized phase cards |
| `matrix` | 2-axis positioning | strategic positioning | locked axes/quadrants |

Generation gate before final text:

```text
grid_mode:
layout_archetype:
column_spans:
row_tracks:
column_tracks:
major_regions:
separator_x:
outer_padding:
component_inventory:
equalized_groups:
shared_edges:
hand_placed_exceptions:
source_policy:
```

Learned layout grammar:

- `top-thesis surface`: H1直下で解釈を1文に圧縮する横長surface。
- `Deep Blue-headed system`: table, card, phase, matrixに読み順を与えるheader band。
- `left-main + right-rail`: 主情報と読み解き/補助根拠を分ける。
- `bottom-conclusion surface`: Sourceより上で「だから何か」を回収するcontained Insight surface。
- `process lane`: 4-6 stepの遷移を示す横/縦timeline。
- `evidence strip`: 市場レイヤー、資産蓄積、追い風を短く示す下段/右レール内反復。
- If top and bottom surfaces coexist, one must be the lead and the other must be secondary.
- Deep Blue-headed systems require equal header heights and equal color role.
- Bottom conclusion surfaces have fixed side breathing room (`80px`) and are separate from the Source baseline.

### 3. Header, Source Baseline, Typography

Header anchor:

- Treat the header as the lowest-freedom component in the slide. Creative variance, illustration style, density, and layout archetype never change it.
- Header is `left vertical line + H1 + subtitle`.
- Left vertical line is Deep Blue `#0B2F5B`, no number attached.
- H1 is Charcoal Ink `#2D332E`, `700`, `30-34pt`.
- Subtitle is Ink-2 `#4D544E`, `400`, `26-30pt`, line-height `1.16-1.24`.
- Header/footer text color lock: H1 `#2D332E`, subtitle `#4D544E`, footer/source/table-note text `#6E756E`. These are one Ink-family hierarchy and must not vary by slide.
- Deep Blue and Honey are not header/footer text colors. Deep Blue appears in the header line or structural rules; Honey appears only in approved Insight/message surfaces.
- Subtitle is a supporting sentence, not body text or caption; it should be clearly larger than body text and one step smaller than H1.
- Draft planning may use ranges to choose a header, but no_header_ranges_in_final_prompts: final image prompts must resolve the header to exact `x/y/w/h/color/font` values before generation.
- Standard exact `1672` ATOM header line is `x=50 y=48 w=10 h=104`. Standard exact H1 starts at `x=88 y=34`.
- Standard exact `1920` equivalent after resize is approximately `x=57 y=55 w=12 h=119`; use the `1672x941` master as the prompt basis unless the user explicitly asks for another basis.
- Header right clear zone is exact by default: `1672 x=1420 y=24 w=208 h=88`. Keep it empty across the deck.
- header_line_top_rule: the vertical line top must sit at or slightly below the first visible H1 glyph top; allowed downward gap `0-6px`; upward protrusion is `0px` and is a blocker.
- If the generator makes the line protrude, repair by shortening or lowering the line, not by moving H1 upward or shrinking the header.
- The line bottom may extend `4-8px` below the subtitle visual bottom; it must not become a tall decorative bar.
- Header-to-body breathing room is `40-52px`.
- H1 max 2 lines. If H1 becomes 2 lines, lower subtitle and body start.

Default exact header lock for image prompts, `1672x941` basis:

```text
header_safe_area: x=44 y=24 w=1584 h=136
vertical_line: x=50 y=48 w=10 h=104 color #0B2F5B
H1: x=88 y=34 w=1332 max_lines=1 size=32pt weight=700 line_height=1.10 color #2D332E
subtitle: x=88 y=78 w=1332 max_lines=1 size=28pt weight=400 line_height=1.18 color #4D544E
visual_alignment: line top at or 0-6px below visible H1 glyph top, never above; line bottom 4-8px below subtitle lower visual edge
body_start_y: 190
upper_right_clear_zone: x=1420 y=24 w=208 h=88 empty
forbidden_header_elements: slide number, title kicker, badge, logo, right object, body object
```

Two-line H1 fallback:

```text
H1 max_lines=2
vertical_line y=48 h=132
subtitle y=112
body_start_y=224
```

Header QA blockers:

- Missing left vertical line, H1, or subtitle.
- Any extra header element: slide number, title kicker, badge, logo, decorative icon, right-side object, or body object inside the header safe area.
- H1, subtitle, or footer/source/table-note text color outside `header_footer_text_color_lock`.
- Left vertical line protrudes above the visible H1 glyph top, looks detached from the H1/subtitle block, or changes x/y/w/h across slides without an explicit new master.

Source baseline:

- Source is optional and appears only when real traceable sources exist.
- If no real source exists, display no Source and keep the lower area quiet.
- Source is fixed left-bottom with one baseline across the deck.
- `1672` standard: `x=44-56`, baseline `y=895-912`.
- `1920` standard: `x=50-64`, baseline `y=1027-1046`.
- Source font: `11-12pt`, `400`, `#6E756E`.
- Footer/source/table-note text always uses Ink-3 `#6E756E`, `400`. Do not use Deep Blue, Honey, Charcoal Ink, random gray, or opacity variants for footer text.
- If the footer has multiple fragments, all footer fragments share the same `#6E756E` color and baseline hierarchy.
- Source format: `Source: 情報源A / 情報源B / 情報源C`.
- Table notes, if needed, are a separate `table_note_microline` above Source.

Typography:

- Japanese: Noto Sans JP.
- Latin/numerals: Geist Sans when available; otherwise Noto Sans JP is acceptable.
- Google Fonts CSS for Noto Sans JP: `https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap`.
- Use tabular numerals for market size, CAGR, KPI, years, quantities, and prices.
- Use only weights `400 / 600 / 700`.
- H1 uses `700`; subtitle uses `400`; section headings use `600`; body uses `400`; emphasized body words max `600`.
- One slide uses max 3 weight levels.
- Japanese letter spacing is `0` or `0.02em`.

### 4. Color And Accent

Palette:

| Token | Color | Use |
| --- | --- | --- |
| Slide base | `#FAFAFA` | slide background |
| Light Gray | `#DDE3EA` | panel / neutral box background |
| Charcoal Ink | `#2D332E` | H1 / body / Insight text |
| Ink-2 | `#4D544E` | subtitle / secondary text |
| Ink-3 | `#6E756E` | Source / tertiary text |
| Deep Blue | `#0B2F5B` | header line / structural accents / table header |
| Deep Blue deep | `#071F3D` | dark Deep Blue surface |
| Deep Blue mist | `#D6E1EE` | quiet Deep Blue surface |
| Honey surface | `#F7EECF` | flat pale Honey message box fill |
| Honey accent | `#C49A2C` | thin Honey left accent line only |
| Honey micro | `#ECC85A` | optional tiny cue only, never message box fill |

Deep Blue:

- deep_blue_usage_lock: Deep Blue is a structural color, not a general emphasis color.
- Exact primary Deep Blue is `#0B2F5B`. Do not introduce extra navy, royal blue, cyan-blue, blue gradients, or opacity-made variants.
- Always use Deep Blue for the left header line.
- In the body, choose one active Deep Blue system per slide: table/card header band, process lane spine, matrix axes/quadrant highlight, structural divider/rule, step badges, or one key-number marker system.
- The header line does not count against the active body system. Body Deep Blue should read as one coordinated system, not separate blue decorations.
- Standard Deep Blue area budget is `4-8%`; dense table slides may reach `10%`; rare chapter/closing slides may reach `12%`. Do not exceed `12%`.
- Do not use Deep Blue as H1, subtitle, body paragraph text, footer/source/table-note text, arbitrary icon color, decorative illustration fill, or message-box wallpaper.
- Deep Blue deep `#071F3D` is reserved for rare dark surfaces or strongest header bands; if used, it replaces other strong blue areas on that slide.
- Deep Blue mist `#D6E1EE` is a quiet structural tint only. Text on mist stays Charcoal Ink `#2D332E`; do not make blue-on-blue text.
- If a dark Deep Blue bottom surface is used, quiet the table header, right rail, card headers, icons, and key numbers so only one blue area leads.

Insight surface family:

- Honey and Deep Blue boxes share the same geometry: radius, height, padding, text baseline, left accent line, background treatment.
- Deep Blue surface is for structure, trust, system logic, and quiet conclusion.
- Honey surface is for turning points, decisions, winning logic, and interpretation.
- Standard surface = `left accent line + role surface background + Ink text`.
- Message boxes and Insight surfaces use a flat solid fill only. Do not add decorative patterns, textures, gradients, motifs, icon wallpaper, or internal illustration inside the box.
- Deep Blue surface background: `#D6E1EE`; left accent: `#0B2F5B` or `#071F3D`.
- Honey surface background: flat pale Honey `#F7EECF`; left accent: muted Honey `#C49A2C`.
- Honey surfaces must feel quieter than Deep Blue surfaces. Use pale fill, Charcoal Ink text, and one thin left accent line; do not use saturated yellow as a large area.
- message_box_scale_lock: Message boxes are compact interpretation surfaces, not display surfaces. Prefer the smallest variant that keeps the sentence legible; do not enlarge the box to rescue long prose.
- message_box_text_size_lock: Insight/message-box text must always be smaller than the selected H1 and subtitle. Default to `20-24pt / 600`; use `24-26pt / 600` only for rare section-close or dark-surface moments. Keep it at least `6pt` smaller than selected H1. If H1 is `30pt`, message-box text is max `24pt`; if H1 is `32pt`, message-box text is max `26pt` only by exception and should normally stay `22-24pt`.
- Message boxes must never become a second title, second hero headline, second subtitle, or larger visual voice than the H1.
- Message box copy is a short judgment sentence: target one line, max two lines. If the sentence needs more than two lines, trim it, split the slide, or move explanation to speaker notes instead of increasing surface height.
- Bottom Insight surface is not a footer. Use it selectively.
- Dark Deep Blue bottom appears in about 1 slide for an 8-10 slide deck and 1-2 slides for a 12 slide deck.

Honey:

- Honey is a decision signal.
- Use Honey only if it makes the reader's decision or interpretation faster.
- Honey component uses a thin muted-Honey left vertical line plus a flat pale Honey background.
- Honey sentence must be a judgment sentence, not a label.
- Honey is max 1 component per slide.
- Saturated Honey area should stay near zero. `#ECC85A` is allowed only as a tiny cue if necessary, never as the message box background.
- Honey message box fill must be `#F7EECF`; accent line must be `#C49A2C`; text remains Charcoal Ink `#2D332E`.
- Honey left accent line is `4-5px` wide and full height. Do not vary its thickness, color, or side within a deck.
- If Honey is used, quiet one of the Deep Blue surface, right rail, or heavy heading.
- Do not add decorative marks inside or around Honey message boxes; use the flat fill, left accent line, and text only.

Honey component variants:

| Variant | Use | Placement | Strength |
| --- | --- | --- | --- |
| `bottom-main` | slide conclusion | body region bottom, above Source, side margin `96px` | low-medium |
| `top-thesis` | chapter / market definition / strategic thesis | below header | medium, compact height |
| `rail-wide` | right rail interpretation | lower right rail | low-medium |
| `rail-tall` | future state / design principle | lower-right rail only when rail owns interpretation | medium, use sparingly |
| `inline-pill` | short in-table cue | row or small card | weak |

Insight surface coordinates, `1672` basis:

```text
bottom-main compact default: x=96 y=812 w=1480 h=56
bottom-main standard max: x=96 y=790 w=1480 h=78
bottom-main tall exception: x=96 y=760 w=1480 h=104, only for rare section-close slides with no competing rail or table emphasis
right edge default: x=1576
left accent line: 4-5px, full height
radius: 8px
padding: 18-22px horizontal, 12-16px vertical
text lines: 1 line preferred, 2 lines maximum
Source separation: keep Source on its own baseline below
```

### 5. Component Library

Icons:

- Default icon style is Lucide-like line icon, `1.5pt` stroke.
- Icon color follows current text/line role.
- Icon circle uses pale Light Gray field and Deep Blue stroke icon.
- Circle diameter is equalized within a slide.
- Dark filled icon circles are limited to one role system.
- Use an icon system when it improves navigation, comparison, or evidence grouping; skip it when the table/chart/text hierarchy already carries the slide cleanly.
- Avoid decorative icon filler. A slide with no icons is acceptable when that absence feels intentional rather than empty.
- Step badge: Deep Blue filled circle, white number, diameter `30-42px`.
- Icons support reading order; meaning must still be conveyed by text and structure.

Signature illustration / diagram:

- Use for chapter openers, turning points, final vision, complex systems, worldview, and moments worth remembering.
- Use illustration because the claim needs it, not because of slide number.
- Start illustration as a grid-aligned supporting region; promote it only when it carries evidence, worldview, or system intuition.
- ATOM visuals are editorial illustration, diagram, structure map, and line icon visuals.
- Avoid realistic photography, photoreal people/offices/scenery, stock-photo aesthetics, cinematic scenes, glossy AI art, abstract 3D, isometric boxes, trapezoid planes, fake perspective floors, and decorative depth.
- technical editorial line illustration: clean controlled vector linework, crisp silhouettes, intentional simplification, pale Light Gray fills, restrained flat shading, a clear focal motif, only useful supporting details, deliberate whitespace, Deep Blue structural accents, optional Honey focus cue when it aids interpretation.
- For workflow/process/before-after claims, use technical storyboard grammar when helpful: three aligned line-illustration panels, Deep Blue arrows, lower icon strip, separate Insight surface.
- Translate rooms, workers, robots, tools, dashboards, facilities, stores, factories, and streets into clean line drawings with pale Light Gray fills.
- For AI/robot/future themes, prefer small workflow cuts, hand/detail scenes, UI fragments, tool-use moments, partial figures, or embedded operational motifs over central full-body robots or futuristic skylines.

Human-crafted feel:

- Human-designed slides show priority, breathing room, and editorial rhythm.
- Repeated cards can be equalized, but focus should come from headings, numbers, rules, spacing, and comparison axes.
- Internal density may vary naturally inside equalized regions.
- At least one of title, subtitle, table, rail, or Insight should lead; the rest supports.
- Whitespace is an editing tool.
- Avoid auto-filled sameness. Vary dominant structure across the deck.

Tables:

- Table = `header band + body rows + thin gridlines`.
- Header band is Deep Blue fill with `#FAFAFA` or white text.
- Header text is short.
- Row height, column width, and icon column width are fixed per table.
- Icon circle diameter is equalized for all rows.
- Highlight key numbers in Deep Blue; body explanation stays Charcoal Ink.
- Row highlight uses Light Gray. Honey only for decision signal.
- Data table, layer table, before-after table, risk table, and pricing table each use one table grammar per slide.

Right rail:

| Rail type | Use | Typical elements |
| --- | --- | --- |
| `bullet rail` | why now / tailwind / evidence | icon heading + rule + bullets |
| `principle rail` | principles / criteria | numbered badges + icon circles |
| `stacked table rail` | market layers / product groups / KPI | small tables + headings |
| `vision rail` | 2030 image / long-term value | icon list + rail Insight |

- Right rail has a left separator, `1.0pt`, `rgba(45,51,46,0.18)`.
- `60/40` separator x: `1015-1035`.
- `70/30` separator x: `1145-1168`.
- Right rail heading = icon + heading + horizontal rule.
- Right rail emphasis max 2 levels.
- Rail and bottom Insight can coexist, but the rail must not compete with the conclusion surface.

Cards and panels:

- Radius options: `4`, `8`, `12`, or pill only.
- Prefer lines and whitespace over nested cards.
- Card border is thin Deep Blue or thin Ink.
- Same-row cards equalize `width / height / padding / icon diameter / heading position`.
- Card padding is `18-28px`.
- Card gap is `24-32px`.
- Repeated cards should clarify columns/rows, not simply fill space.

Flows, matrices, loops:

- Arrows only show causality, transition, or loop.
- Standard arrow line: `1.5-2.25pt`.
- Arrowhead size equalized within a slide.
- Before/after table uses a fixed central arrow column.
- 2x2 matrix locks axes, labels, center dashed lines, and highlighted quadrant.
- Portfolio loop locks direction, curve, and node spacing.
- Flow nodes are either card-based or icon-circle-based, not mixed.

Thesis and conclusion surfaces:

| Surface type | Use | Style |
| --- | --- | --- |
| `outlined top thesis` | early thesis | `#FAFAFA` fill + Deep Blue border + bold centered text |
| `icon thesis band` | market definition / beachhead / why now | left icon circle + sentence |
| `outlined bottom conclusion` | readout after table/figure | `#FAFAFA` fill + Deep Blue border |
| `Deep Blue surface conclusion` | structure/trust/system readout | Deep Blue mist surface |
| `dark Deep Blue conclusion` | strong section close | dark Deep Blue fill + `#FAFAFA` text |
| `Honey conclusion` | strategic turning point | Honey surface |

- Surface height is deck-mastered.
- Top thesis preserves breathing room below header.
- Bottom conclusion sits above Source, not on Source baseline.
- H1/subtitle and dominant structure can be enough; quiet bottom is valid.

Deep Blue header systems:

- Tables, phase cards, matrix panels, and persona card groups can use Deep Blue header bands.
- Same hierarchy = same header band height.
- Header text is white or `#FAFAFA`, `600` or `700`, short.
- Large tables can have fixed left icon or label column.
- Multiple Deep Blue headers must align to column lines and read as one system.

### 6. Pattern Catalogue

| Archetype | Use | Grid mode | Major regions | Insight |
| --- | --- | --- | ---: | --- |
| `architecture-flow + right-rail` | business architecture / value proposition / components | `60/40` | 3 | bottom-main optional |
| `market-table + layered-rail` | market size / competitive space / TAM interpretation | `70/30` | 3 | rail-wide or bottom-main |
| `competitive-layer-table + verdict-cards` | tech trend / falling vs rising value | `60/40` | 3 | bottom-main |
| `2x2-positioning + principle-rail` | strategic positioning | `60/40` | 3 | bottom-main |
| `three-column-launch-plan` | initial market / current-to-be / personas/products | `3-column` | 3 | top-thesis |
| `phase-roadmap + support-row` | GTM / phased expansion | `4-phase` | 2 | support-row quiet |
| `portfolio-loop + asset-rail` | compounding asset / KPI | `60/40` | 3 | bottom-main |
| `thesis-banner + governance-panels` | risk / trust / long-term vision | `full-12` or `3-column` | 3 | rail-tall |
| `mission-cards + why-now-row` | mission / value chain / why now | `full-12` | 3 | outlined bottom |
| `intersection-definition + meaning-table` | market definition / overlap | `60/40` or `50/50` | 3 | bottom conclusion |
| `trend-table + value-polarity` | tech trend / value polarity | `60/40` | 3 | outlined bottom |
| `quadrant-grid-set` | multiple 2x2 tests | `full-12` | 2 | bottom conclusion |
| `beachhead-definition + persona-grid` | beachhead / customer / adoption reason | `50/50` or `60/40` | 3 | bottom conclusion |
| `product-stack + trust-capability-grid` | product stack / functions / trust | `full-12` | 3 | dark Deep Blue bottom |
| `phase-roadmap + asset-compounding` | GTM and compounding assets | `4-phase` | 3 | bottom support |
| `process-timeline + double-rail` | onboarding / channel / asset accumulation | `60/40` | 3 | bottom conclusion |

Archetype selection:

- If table is the lead, keep right rail interpretive.
- If right rail is strong, give left main figure breathing room.
- If bottom Insight exists, separate it from the body region and Source.
- If using left main + strong right rail + strong bottom surface, clearly assign lead/support/close.
- Phase roadmap uses max 2 layers: upper phase cards and lower support row.
- Governance slides should land in trust design rather than fear.
- Omit top thesis when H1/subtitle already make the claim clear.
- Quadrant-grid-set equalizes all axis labels, dashed lines, highlighted cards, and quadrant cells.
- Product-stack pages can become dense; pre-lock layer heights.

### 7. PPT Reproducibility

- Use simple shapes: rectangles, rounded rectangles, lines, circles, standard arrows.
- Texture comes from whitespace and alignment, not effects.
- First lock Header.
- Then lock grid mode and major regions.
- Then place table/card/rail/Insight master components.
- Last, swap text.
- Resolve overflow with `trim / split / move to notes`; never shrink body below `18pt`.
- Object x/y error max `+-2px`.
- Column edge drift max `+-1px`.
- Equalized group width/height delta max `+-2px`.
- For large illustration/diagram regions, prioritize visual consistency of header line, separator, Source baseline, and component equalization.
- In PPT-style packaging, first place deck master: outer shell, header line, title x, subtitle x, Source baseline, bottom conclusion y.

### 8. QA Checklist

Brand token gate:

- H1/body are Charcoal Ink.
- Deep Blue `#0B2F5B` and Light Gray `#DDE3EA` are structural.
- Honey is a decision signal.
- The visual treatment stays calm and dense: light base, compact fixed header, thin-line structures, equalized pale surfaces, restrained icons/line drawings.
- Color consistency check: palette roles stay consistent across slides; no late-slide saturation jump, random accent color, arbitrary gray, or unplanned blue/yellow emphasis appears.
- Subtitle is `#4D544E`, `400`, `26-30pt`, and visually secondary to H1 but larger than body.
- Header/footer text color lock is honored: H1 `#2D332E`, subtitle `#4D544E`, footer/source/table-note text `#6E756E`.
- No Deep Blue, Honey, saturated yellow, or arbitrary gray appears in header/footer text.
- Honey max 1 per slide; Honey component uses left accent + tint background.
- Deep Blue and Honey surfaces share one component skeleton.
- Insight and Honey message boxes use flat solid fills only; no pattern, texture, gradient, motif, or internal illustration.
- message_box_scale_lock is honored: message boxes stay compact and are not enlarged to carry long prose.
- message_box_text_size_lock is honored: Insight/message-box text is smaller than H1 and subtitle and never behaves like a second title.
- Honey message boxes use `#F7EECF` fill, `#C49A2C` left line, and `#2D332E` text consistently. Strong yellow fills are not part of the component.
- Raw Honey appears only as a tiny cue when necessary, never as a full box fill or title emphasis.
- Icons are quiet wayfinding or evidence cues, never filler.
- visual_asset_judgment is satisfied: illustrations/icons are present when helpful, absent when unnecessary, and never generic decoration.

Layout gate:

- `layout_archetype`, `grid_mode`, `component_inventory`, `row_tracks`, `column_tracks`, `shared_edges` exist.
- Major region count is in budget.
- Canvas occupancy is intentional: body space is substantially used by a clear main field plus optional rail/strip/conclusion surface, without broad accidental emptiness.
- Whitespace and occupancy balance feels intentional: the slide is neither accidentally empty nor crowded, and the main structure owns the canvas without crushing the margins.
- Header anchor and upper-right clear zone are consistent.
- Source baseline anchor is fixed.
- Outer padding consistency is visible across the deck: left/right/top/bottom margins do not drift slide to slide, and body content does not creep into the header/footer shell.
- Separator x matches grid mode.
- Main object edges snap to grid.
- Same-row objects share top/bottom lines.
- Table/card/phase/process centers align.
- Hand-placed exceptions max 2.
- Rail and Insight hierarchy is clear.
- Signature illustration is one major region and grid-aligned.

Typography gate:

- H1 `30-34pt / 700`.
- Subtitle `26-30pt / 400 / #4D544E`.
- Footer/source/table-note text `11-12pt / 400 / #6E756E`.
- Insight/message-box text: default `20-24pt / 600`; `24-26pt / 600` only by exception, always at least `6pt` smaller than selected H1 and visually below subtitle.
- Body is readable at `18pt` equivalent.
- H1 max 2 lines; subtitle max 2 lines.
- Weights are `400 / 600 / 700`.
- Typography balance check: size and weight hierarchy is stable across slides; body labels, table headers, Insight text, and captions do not compete with H1/subtitle or randomly change weight.
- Numerals use tabular alignment.

Content gate:

- One claim, one dominant structure.
- H1 is claim; subtitle supports.
- Insight adds interpretation beyond H1.
- Source contains only traceable real sources.
- Table note and Source are separated.
- Unsupported facts are flagged.

Deck gate:

- Deck keeps precise alignment while showing priority, rhythm, and breathing room.
- Visual design traits are stable across the deck: light base, line weight, card radius, pale fills, icon stroke, illustration density, and header compactness do not drift.
- deck_tone_master_lock is stable from first third to last third: palette, linework, icon family, illustration intensity, density rhythm, card geometry, and source behavior do not drift.
- Header and Source baseline are consistent.
- Insight component geometry and baseline are consistent.
- Honey count and variants feel selective.
- Deep Blue area fits slide role.
- Visual asset mix is intentional: icons/illustrations appear where they improve comprehension or memorability, and are absent where the structure is already strong.
- Freshness comes from composition, whitespace, viewpoint, comparison axis, or quiet illustration, not decoration.
- Large illustrations appear only where claim memory benefits.
- Avoid long card-led stretches in a deck; vary composition when the argument benefits from a different structure.
- Density and calm coexist.

Pre-Google Slides generated image gate:

- Review the actual generated PNGs, not only the prompt or plan.
- Run at least one multimodal self-review pass before Google Slides insertion.
- Run a deck-level tone consistency pass after every generation/repair batch, before Google Slides insertion.
- Score each image on model route, exact text, visual design quality traits, header lock, grid/shared edges, typography, information density, illustration clarity, human-designed feel, source hygiene, speaker-notes separation, and deck consistency.
- Run `post_generation_design_balance_check` on the actual generated PNGs: whitespace and occupancy balance, typography size/weight balance, color consistency, outer padding consistency, and header integrity.
- In `post_generation_design_balance_check`, explicitly inspect canvas occupancy versus blank zones, external padding drift, header line/H1/subtitle integrity, card/table height equalization, line-weight consistency, icon-family consistency, Deep Blue scatter, Honey strength, and whether illustrations look like human-designed operational diagrams rather than generated concept art.
- Score the whole image set on `deck_tone_consistency`: palette role consistency, Deep Blue usage consistency, Honey treatment consistency, header/footer consistency, illustration style family, icon family, density rhythm, card/table geometry, whitespace rhythm, source baseline, and first-third vs last-third tone match.
- Compare the first third, middle third, and last third of the generated deck. The last third must not become more saturated, darker, glossier, more icon-heavy, more illustrated, more card-heavy, or looser in spacing unless the planned section role explicitly requires it.
- Classify issues as `blocker`, `major`, `minor`, or `accepted`.
- Any blocker or major issue requires a repair prompt and a regenerated or edited PNG before roll-up.
- Typical blockers: wrong/non-generated route, missing or malformed header line, header deformation, title/color drift, unreadable body text, invented labels/sources, speaker notes visible on slide, severe grid drift, body content invading header/footer margins, or wrong slide claim.
- Typical major issues: weak header consistency, weak visual design quality, low information density against the plan, unclear illustration, AI-looking illustration, excessive illustration dominance, message-box text larger than or equal to H1, unbalanced whitespace/occupancy, inconsistent outer padding, unstable text size/weight hierarchy, color role drift, card/table height inconsistency, icon-family mixing, repeated-card monotony, source baseline drift, mismatch between slide claim and visual structure, late-deck tone drift, missing useful visual assets where the slide feels sparse, or generic decorative icon filler.
- Minor issues can remain only if they do not affect readability, brand fidelity, source integrity, or deck consistency.
- Continue iterations until every slide has no blockers or majors and `deck_tone_consistency_status: approved`.
- Default practical ceiling is five review/regeneration iterations per slide. If the ceiling is reached, report unresolved issues and do not silently claim final quality.

### 9. Prompt Patterns

Base contract:

```text
ATOM slide contract:
- use embedded ATOM design system in SKILL.md
- do not load an external ATOM pattern file
- 1 slide = 1 claim
- 1 slide = 1 dominant structure
- choose layout_archetype and grid_mode before drafting
- use 1672x941 coordinate basis and 12-column grid
- output component_inventory, row_tracks, column_tracks, shared_edges before final text
- lock deck_header_master: left vertical line #0B2F5B, H1 #2D332E / 700 / 30-34pt, subtitle #4D544E / 400 / 26-30pt
- keep header visible inventory exactly left vertical line, H1 title, subtitle
- keep upper-right clear zone quiet
- use insight_surface_master for message boxes
- use Deep Blue and Honey Insight surfaces in one surface family
- message boxes use flat solid fills only, with no pattern, texture, gradient, motif, or internal illustration
- message boxes use message_box_scale_lock: compact surface, smallest legible variant, no long-prose enlargement
- message boxes use message_box_text_size_lock: text is never equal to or larger than H1 or subtitle
- keep body readable at 18pt equivalent
- omit page numbers
- use editorial illustration/diagram/structure map/line icons, never photoreal stock
- use Source only for traceable real information sources
```

Deck planning process:

1. Define audience, decision, purpose, language, source strictness, and output type.
2. Extract deck thesis.
3. Build slide claims as standalone H1 candidates.
4. Read only H1 claims in order and repair logical gaps.
5. Assign each slide: claim type, evidence, source policy, visual structure, layout archetype, grid mode, density tier, visual richness role, illustration intensity, creative variance, Insight decision, and speaker notes.
6. Freeze exact on-slide text.
7. Produce canonical planning block for each slide.
8. Generate 1-2 pilot slides with Codex built-in `gpt-image-2`.
9. Audit, repair prompts, then generate remaining slides.
10. Assemble approved generated PNGs into Google Slides with speaker notes.

Slide draft output fields:

```text
slide_claim:
layout_archetype:
grid_mode:
column_spans:
row_tracks:
column_tracks:
major_regions:
coordinate_inventory_1672:
header_anchor:
source_baseline_anchor:
insight_surface_master:
subtitle:
exact_text:
equalized_groups:
shared_edges:
icon_visual_treatment:
human_crafted_feel:
insight_decision:
source_line:
speaker_notes_text:
```

Self-audit process:

- Audit each slide as pass/fail against Brand Token, Layout, Typography, Content, Deck, Model Route, and Google Slides/Speaker Notes gates.
- For every fail, choose one: `trim`, `split`, `regrid`, `quiet hierarchy`, `add Insight`, `remove Insight`, `repair source`, `repair header`, `repair illustration`.
- Re-audit after repair.
- After image generation, run `pre_google_slides_image_review` on the actual PNG. If blockers or majors remain, generate a repair prompt, regenerate or edit the image, and re-audit before any Google Slides roll-up.

## Workflow

1. Identify the output: prompt only, one slide image, slide-image deck plan, screenshot/render critique, image repair, or Google Slides roll-up.
2. Use the embedded ATOM design system above. Do not load any external ATOM pattern file.
3. If the input is long text, notes, memo prose, transcript, or an equity story, convert it into slide structure before any image prompt: deck thesis, audience decision, storyline frame, section map, slide claims, evidence/source map, visual archetype, density design, information-unit budget, density risk, split/merge decisions, and speaker notes plan.
4. Create a claim-title storyline first. Every planned slide must have a standalone claim, not a topic label.
5. Run density design before deciding to split, merge, or generate.
6. Define the deck master before slide-by-slide prompting.
7. Lock the header first and treat it as the lowest-freedom part of the slide.
8. Draft speaker notes before image generation for every planned deck slide.
9. Run generation readiness: built-in image generation available, prompt final, size valid, sources resolved, ATOM design system reflected, header master locked, visual richness/density complete, speaker notes drafted, pilot plan chosen.
10. Generate final images using Codex built-in `gpt-image-2` image generation only.
11. Run `pre_google_slides_image_review` on the actual generated PNGs. Do not call the deck complete just because images were produced.
12. For every blocker or major issue, write a concrete repair prompt, regenerate or edit the image, replace the PNG, and review again.
13. Continue the review/repair loop until every slide is approved and the deck-level consistency gate passes, or until the iteration ceiling is reached and unresolved issues are explicitly reported.
14. For multi-slide decks, after generated PNGs pass QA, create an image-only Google Slides roll-up with one full-bleed PNG per slide and speaker notes in each slide's notes page.
15. If image generation cannot be completed, report `blocked: Codex built-in gpt-image-2 image generation was not run`.

## Output Contract

Use this planning block before image generation:

```text
slide_claim:
generation_mode:
image_model:
image_size:
image_size_label:
image_quality:
image_background:
image_output_format:
image_moderation:
image_n:
image_streaming:
image_delivery_size:
generation_route:
generation_status:
output_files:
google_slides_delivery:
google_slides_status:
google_slides_title:
google_slides_file_id:
google_slides_url:
google_slides_slide_count:
google_slides_route:
google_slides_image_mapping:
google_slides_speaker_notes_mapping:
speaker_notes_plan:
speaker_notes_status:
speaker_notes_text:
pre_google_slides_image_review:
image_review_iteration:
image_review_status:
image_review_findings:
image_repair_prompt:
image_repair_history:
final_image_quality_status:
deck_tone_consistency_review:
deck_tone_consistency_status:
deck_tone_repair_plan:
post_generation_design_balance_check:
visual_design_quality_traits:
whitespace_occupancy_balance_status:
typography_balance_status:
color_consistency_status:
outer_padding_consistency_status:
header_integrity_status:
layout_archetype:
grid_mode:
column_spans:
row_tracks:
column_tracks:
separator_x:
outer_padding:
major_regions:
coordinate_inventory_1672:
master_components:
deck_master_refs:
deck_tone_master_lock:
deck_header_master_lock:
header_line_top_rule:
deep_blue_usage_lock:
visual_asset_judgment:
component_inventory:
equalized_groups:
shared_edges:
hand_placed_exceptions:
visual_richness_role:
visual_asset_role:
icon_system_plan:
signature_visual_plan:
illustration_region:
illustration_presence:
illustration_intensity:
human_designed_illustration_style:
creative_variance:
density_tier:
density_layers:
density_design:
information_unit_budget:
density_levers:
density_guardrails:
header_anchor:
footer_anchor_baseline:
header_footer_text_color_lock:
message_box_scale_lock:
message_box_text_size_lock:
table_note_microline:
source_line:
source_policy:
brand_accent_usage_budget:
brand_accent_system_role:
insight_decision:
human_crafted_feel:
qa_risks:
blocking_unresolved_items:
```

Then output:

```text
image_model: gpt-image-2
final_image_prompt:
negative_prompt:
post_generation_audit:
pre_google_slides_image_review:
repair_iteration_plan:
```

Do not label a prompt final when `layout_archetype`, `grid_mode`, `coordinate_inventory_1672`, `master_components`, `source_policy`, or `speaker_notes_text` is unresolved.

## Image Prompt Rules

- Specify `image_model: gpt-image-2`, `16:9`, valid image-generation size, ATOM target `1920x1080`, and `1672x941` coordinate basis.
- Use `generation_mode: new_image` for a single new slide image and `generation_mode: image_edit` for screenshot/reference repair.
- Use `size: "1536x864"` for fast 16:9 drafts, `size: "2048x1152"` for 2K-width working review, and `size: "2560x1440"` for final high-fidelity 16:9 slide images.
- Treat `1920x1080` as FHD/1080p delivery, not direct generation. `1080` is not divisible by 16.
- Treat strict DCI `2048x1080` and `4096x2160` as non-target cinema sizes.
- Use `3840x2160` only when explicitly requested as 4K UHD.
- Use `quality: "high"` for final text-heavy or brand-sensitive slides.
- Use `background: "opaque"` or `auto`; do not request transparent background.
- Use `output_format: "png"` for slide fidelity.
- Use `n=1` for final text-heavy slides.
- The built-in image route does not expose temperature. When the user asks to raise temperature, record `creative_variance: high`: vary composition, crop, viewpoint, asymmetry, and metaphor while preserving header, exact text, grid, source, and readability.
- Put literal slide text in quotes and request only those strings.
- Keep speaker notes out of the image prompt's visible text.
- After a multi-slide deck is approved, roll up final generated PNGs into Google Slides as image-only slides with speaker notes.
- Before Google Slides roll-up, inspect the generated PNGs visually and iterate repairs until `final_image_quality_status: approved`.

Negative prompt essentials:

```text
pure black, old mustard, neon teal, generic gradient, glassmorphism, glow, heavy shadow,
stock template feel, missing header line, header line protruding above H1, blue H1, header safe area filled,
header deformation, inconsistent outer padding, body content invading margins, accidental empty dead zone, overcrowded canvas,
slide number, header number badge, title kicker, logo in upper-right clear zone,
blue body text, blue subtitle, blue footer text, honey footer text, yellow footer text, random footer gray, mismatched source color,
multiple blue hues, arbitrary blue highlights, blue gradient, decorative blue fill, blue icon clutter,
patterned message box, textured message box, gradient message box, decorative motif inside message box,
oversized message box, over-tall message box, bulky insight surface, message box text larger than H1,
message box text competing with subtitle, message box as title, oversized insight text, unstable text weights, random bold text,
strong yellow message box, saturated yellow fill, dark yellow fill, large yellow area, yellow title underline,
rough doodle, messy hand-drawn sketch, overpowered AI-looking illustration,
trapezoid planes, fake perspective floor, isometric boxes, tilted slab, vanishing-point grid, pseudo-3D depth,
central full-body robot, large city skyline, luminous touch point, heroic robot, abstract 3D, cinematic glow,
body text below 18pt equivalent, invented source, upload filename as source, speaker notes visible on slide
```

## Google Slides Roll-Up

For generated image decks:

- Start only after `pre_google_slides_image_review` approves every generated PNG.
- Create or use a native Google Slides deck.
- Keep exactly one slide per generated PNG.
- Insert each local generated PNG full-bleed in 16:9.
- Preserve slide order.
- Remove any extra blank slides.
- Attach speaker notes to each slide's notes page.
- Verify slide count, image mapping, and notes mapping.
- If direct image insertion or notes insertion is blocked, report the blocker and deliver generated images plus notes text separately.

Speaker notes should include:

- spoken claim in plain language
- key evidence or assumption to mention
- source caveat or confidence level if relevant
- transition cue to next slide

## Helper Script

Use `scripts/build_atom_slide_prompt.py` to create a prompt scaffold from a rough brief:

```bash
python3 scripts/build_atom_slide_prompt.py brief.md
python3 scripts/build_atom_slide_prompt.py long-memo.md --mode text-structure --size 2048x1152
python3 scripts/build_atom_slide_prompt.py brief.md --mode single-slide-image --archetype "market-table + layered-rail" --grid-mode "70/30"
python3 scripts/build_atom_slide_prompt.py brief.md --mode repair
python3 scripts/build_atom_slide_prompt.py brief.md --mode audit
```

The script is a drafting accelerator, not a substitute for applying judgment. Treat any `UNRESOLVED` field it emits as a blocker before image generation.

For final image generation, invoke Codex's built-in image generation tool directly from the final prompt. The helper script only scaffolds prompts; it must not be used to create substitute slide PNGs.
