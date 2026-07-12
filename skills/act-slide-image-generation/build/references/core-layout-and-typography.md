# Core Layout And Typography

This file is the geometry and typography source of truth for every ACT 16:9 slide.

## Positive Directive Contract

Write every instruction as a target state, selected option, measurable range, and corrective action. Use `place`, `keep`, `select`, `preserve`, `scale`, `rewrite`, and `repair by`. Describe quiet regions as intentional blank canvas and technical routes as the exclusive approved path.

## 1672x941 Master Shell

- Outer shell: `x=72..1600`, `y=80..861`
- Canvas padding: 72px left/right and 80px top/bottom
- H1: `x=72 y=80 w=1528`, one uniform line, 38pt/700, 36pt floor, 40pt cap, `#2D332E`
- Subtitle: `x=72 y=126 w=1528`, 32pt/400, 30pt floor, 34pt cap, neutral gray `#626A64`
- Header stack gap: actual glyph-to-glyph gap 14-22px, target 18px
- Header/body quiet band: actual subtitle bottom to first body mark >=64px, target 72-88px
- Body start: `y=270`
- Footer absent: available band `y=270..861`, optical target `y=595`
- Footer present: available band `y=270..810`, footer `y=810..861`, baseline `y=852`, optical target `y=570`
- Horizontal optical target: `x=836`

Scale all coordinates proportionally for an approved output size.

## Title Fit

H1 uses one uniform line and one text run. Estimate rendered width before freezing `exact_text`. Rewrite until 38pt fits comfortably, retaining topic, change/tension, and implication. Place dates, scope qualifiers, and secondary clauses in subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

Apply `header_copy_budget_lock` before generation. H1 uses <=28 Japanese full-width-equivalent characters and subtitle uses <=36; two half-width ASCII characters count as roughly one full-width equivalent for the first-pass estimate. Then verify actual rendered width and keep each line at <=92% of its fixed text box. Repair overflow through copy editing and body redistribution while preserving the deck-wide 38pt/32pt master.

## Rendered Type Review

- H1 visible glyph height: 43-52px on the 1672 basis
- Subtitle visible glyph height: 36-44px
- Subtitle optical height: 75-85% of H1
- Subtitle color: `#626A64`; visually subordinate to H1 and distinct from Petrol body emphasis
- Body/card/table/data text: >=20pt equivalent

When the rendered hierarchy falls outside these bands, regenerate with the shell preserved and the target rendered size reinforced.

## Deck-Wide Header Consistency

Freeze one header master before slide generation and copy it verbatim across every slide: H1 `38pt/700 #2D332E`, one line, `x=72 y=80 w=1528`; subtitle `32pt/400 #626A64`, one line, `x=72 y=126 w=1528`. Preserve font family, weight, point size, color, line box, baseline, and width. Resolve copy fit through rewriting, redistribution, or slide splitting. Approve the contact-sheet comparison when H1 visible glyph-height spread is <=2px, subtitle spread is <=2px, and corresponding baselines align after proportional scaling.

Apply `header_alignment_lock`: content slides use left-aligned H1 and subtitle with the shared `x=72 w=1528` anchor and ragged-right endings. Approve when their first visible glyph x-coordinates differ by <=2px and the H1 aligns to the main body grid within <=4px. Use centered headers only for an explicitly requested cover, interstitial, or closing slide recorded as `header_alignment_exception`.

## Visible Outer Padding

Measure the actual outermost meaningful pixels on the rendered PNG and record `top_visible_margin` and `bottom_visible_margin`. Require `abs(top_visible_margin - bottom_visible_margin) <=4px` on the 1672 basis. Use the signed difference to select the correction: a larger top margin moves the complete H1/subtitle group upward; a larger bottom margin moves the complete bottom-most component downward; a shell collision triggers whole-body redistribution. Preserve each translated group's internal gaps, alignment, type scale, and dimensions. For other output sizes, require normalized difference ratio <=0.005.

## Content Footprint And Balance

Measure the combined body silhouette, including main and supporting regions, through edge margins and intentional-space coverage.

- `T2_balanced`, `T3_dense`, `T4_appendix_dense`: body side margins 24-72px inside the shell
- `T1_sparse`: body side margins 96-160px inside the shell
- Footer absent: bottom gap 26-80px
- Footer present: bottom gap 30-80px
- Horizontal center tolerance: 12px
- Vertical center tolerance: 12px absent, 11px present
- Left/right breathing difference: <=16px
- Coverage grid: divide the body band into 4 columns x 3 rows; classify each cell as occupied or intentionally blank
- Intentional blank-cell cap: T1 <=5, T2 <=2, T3/T4 <=1
- Single chart, diagram, or illustration: preserve native aspect ratio within 5%

Prioritize shell bounds, >=20pt body text, edge-margin bands, then optical-center refinement. Repair a compact-island composition by widening or regrouping meaningful regions and reducing undeclared blank cells. Preserve aspect ratio and satisfy balance through margins and intentional blank space.
