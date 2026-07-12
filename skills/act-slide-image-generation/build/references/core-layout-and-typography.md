# Core Layout And Typography

This file is the geometry and typography source of truth for every ACT 16:9 slide.

## Positive Directive Contract

Write every instruction as a target state, selected option, measurable range, and corrective action. Use `place`, `keep`, `select`, `preserve`, `scale`, `rewrite`, and `repair by`. Describe quiet regions as intentional blank canvas and technical routes as the exclusive approved path.

## 1672x941 Master Shell

- Outer shell: `x=72..1600`, `y=80..861`
- Canvas padding: 72px left/right and 80px top/bottom
- H1: `x=72 y=80 w=1528`, one uniform line, 40pt/700, 36pt floor, 42pt cap, `#2D332E`
- Subtitle: `x=72 y=126 w=1528`, 32pt/400, 30pt floor, 34pt cap, `#4D544E`
- Header stack gap: actual glyph-to-glyph gap 14-22px, target 18px
- Header/body quiet band: actual subtitle bottom to first body mark >=64px, target 72-88px
- Body start: `y=270`
- Footer absent: available band `y=270..861`, optical target `y=595`
- Footer present: available band `y=270..810`, footer `y=810..861`, baseline `y=852`, optical target `y=570`
- Horizontal optical target: `x=836`

Scale all coordinates proportionally for an approved output size.

## Title Fit

H1 uses one uniform line and one text run. Estimate rendered width before freezing `exact_text`. Rewrite until 40pt fits comfortably, retaining topic, change/tension, and implication. Place dates, scope qualifiers, and secondary clauses in subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

## Rendered Type Review

- H1 visible glyph height: 46-56px on the 1672 basis
- Subtitle visible glyph height: 36-44px
- Subtitle optical height: 75-85% of H1
- Body/card/table/data text: >=20pt equivalent

When the rendered hierarchy falls outside these bands, regenerate with the shell preserved and the target rendered size reinforced.

## Content Footprint And Balance

Measure the combined body silhouette, including main and supporting regions.

- `T2_balanced`, `T3_dense`, `T4_appendix_dense`: target 90-94% of available width and 86-92% of available height; repair below 88% width or 82% height
- `T1_sparse`: target 72-84% width and 66-80% height
- Horizontal center tolerance: 12px
- Vertical center tolerance: 8px
- Left/right breathing difference: <=16px
- Footer-absent lower edge for T2-T4: `y>=835`
- Footer-present lower edge for T2-T4: `y>=780`

Repair a compact-island composition by scaling the focal structure and supporting regions together, widening the body silhouette, and redistributing regions toward the optical targets while preserving 20pt body text and the outer shell.

