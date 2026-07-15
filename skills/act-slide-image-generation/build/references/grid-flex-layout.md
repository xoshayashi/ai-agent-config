# Grid And Flex Layout Contract

Use this contract to turn a content-led composition into a measurable layout tree. Grid governs two-dimensional alignment. Flex governs one-dimensional distribution inside a declared region. This preserves compositional variety while making placement, spacing, and occupancy auditable.

Apply `consulting-grid-rigidity.md` with this file. The Grid/Flex tree defines parent allocation; the component, rule, and connector registries extend the same coordinates through every meaningful internal element.

## Explicit Parent Grid

On the 1672x941 basis, construct the body alignment lattice inside `x=72..1600` as 16 columns of 73px with fifteen 24px gutters. The arithmetic closes exactly: `16 × 73 + 15 × 24 = 1528`. Use grid lines 1..17. Place every top-level region with integer `column_start` and `column_end` values, plus explicit top and bottom positions on the 8px vertical baseline. Major region edges, repeated text anchors, and aligned object edges land within 4px of their declared grid line.

Treat the 8px baseline as an ACT operating token rather than a web standard. Select spacing from `8, 16, 24, 32, 48, 64px`; use 24px as the standard column gutter. Assign each gap one semantic role: inline, within-group, between-group, or section. Keep within-group gaps at least 8px smaller than their owning between-group gap. Apply optical correction within ±4px.

Nested two-dimensional regions inherit the parent column lines and gutter through a subgrid-equivalent plan. Register every top-level and nested region before generation. The layout audit contains zero implicit tracks and zero unregistered regions.

## Recursive Layout Tree

Freeze `layout_tree` before image generation. Every body element has exactly one parent. Every parent declares `layout: grid | flex`. A meaningful overlay declares its anchor, paired elements, and z-order.

Each grid parent declares:

- `bounds: {x, y, w, h}`
- `columns`, `track_px`, `gutter_px`, and `line_snap_tolerance_px`
- every child’s `column_start`, `column_end`, `row_start`, and `row_end`
- `nested_alignment: inherit_parent_lines | local_explicit_grid`

Each flex parent declares:

- `bounds: {x, y, w, h}` and `main_axis: row | column`
- `wrap: nowrap | wrap`, plus `line_plan` for every container; `nowrap` uses one line containing every child
- one `gap_px` token, `justify`, and `align`
- for every child: `basis_px`, `grow`, `shrink`, `min_main_px`, `min_cross_px`, `allocation_bounds`, and content priority

Use `justify:start` with `align:start | baseline` for text-led groups, `align:stretch` for equivalent comparison regions, and centered alignment for compact icons or numbers. Select Flex gaps from `16, 24, 32, 48px`. Use the declared gap as the spacing source. When distributed alignment is selected, keep every rendered gap within ±4px of the declared value.

For `nowrap`, satisfy `sum(basis_px) + (item_count - 1) × gap_px <= container_main_px`. Apply the same equation to every planned wrap line. After distribution, main-axis fill is 92-100% and cross-axis fill is 82-100%. Keep each rendered item within ±20% of its declared basis and at or above its minimum size. A wrap plan declares line count and item count per line; the final line fills at least 75% of its main axis.

## Occupancy And Content Fill

Measure four distinct quantities against the selected footer-mode body band:

1. `primary_body_visible_envelope`: horizontal union of meaningful non-message components plus the vertical union of every painted body component; width 78-92%; footer-absent height 82-94% of the reachable body band; footer-present height 78-90%. The canonical full-width message box is an auxiliary conclusion band and stays outside only the horizontal-width measure.
2. `top_level_layout_container`: union of declared main-grid regions; width 82-94%; footer-absent height 65-80% of the reachable body band; footer-present height 65-85%.
3. `allocated_region_area_fill`: union of child `allocation_bounds` divided by the available footer-mode body-band area; 58-80%.
4. `meaningful_foreground_area_fill`: visible text glyphs plus meaningful object surfaces divided by the body visible envelope; initial range 18-38%, then pilot-calibrated within the same content mode.

Count text glyph ink, data marks, icons, filled shapes, and information-bearing image regions as meaningful foreground. Treat thin rules, isolated edge marks, empty panel interiors, and background fills as alignment or material rather than occupancy. Measure `text_ink_area_share` at 6-20% and `object_ink_area_share` at 10-30% of the visible body envelope. Their spatial union is `meaningful_foreground_area_fill`; overlapping labels and objects contribute once to the union. Confirm that both categories use their assigned tracks.

For an aspect-locked focal object, preserve its 55-88% object-width band while the complete body passes the standard width band and its selected footer-mode height band.

Measure the area-weighted vertical centroid of every painted body component, including direct Grid children and the painted message box, against the full 941px canvas height: 58-62% without a footer and 55-60% with a footer. Include the message box in vertical mass, allocated area, and bottom closure while measuring primary-body horizontal occupancy from non-message components. Footer-present layouts use the dedicated `y=190..842` body envelope and omit the canonical bottom message box. In footer-absent mode, place the lowest meaningful allocation edge at `y=857..869` and keep the actual first-H1-pixel margin versus canvas-bottom/body margin difference within 12px.

## Plan And Render Audit

The generation handoff includes `layout_tree`, `grid_plan`, `flex_plan`, `occupancy_plan`, and one geometric `quiet_region`. The quiet region declares `bounds`, `role`, and adjacent regions.

After generation, create the matching `layout_audit` and measure:

- grid-line and baseline error
- registered versus rendered regions
- flex basis deviation, main/cross fill, and rendered gaps
- wrap line counts and final-line fill
- body envelope, allocated-region fill, meaningful foreground fill, text union, and object union
- overflow pixels, clipped items, and text overlaps

Approval requires every declared field to have a measured counterpart, every major element to be registered, line and baseline errors within 4px, and overflow, clipping, and text overlap equal to zero. The same audit passes `edge_registration_score >= 0.90`, `repeated_module_consistency >= 0.95`, `gap_token_compliance >= 0.95`, structural-rule and connector endpoint pass rates of `1.00`, `structured_cell_fill = 0.65..0.85`, `orphan_region_count = 0`, and `grid_rigidity_score >= 0.93`. A missing plan field or measurement enters `repair_required` and returns to layout planning.

## Research Basis

- [W3C CSS Grid Layout Module Level 2](https://www.w3.org/TR/css-grid-2/): explicit tracks, flexible sizing, gutters, alignment, and subgrid inheritance.
- [W3C CSS Flexible Box Layout Module Level 1](https://www.w3.org/TR/css-flexbox-1/): main/cross axes, basis, grow, shrink, wrapping, and minimum sizing.
- [W3C CSS Box Alignment Module Level 3](https://www.w3.org/TR/css-align-3/): alignment containers, subjects, distributed alignment, and gaps.
- [MDN: Relationship of flexbox to other layout methods](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Flexible_box_layout/Relationship_with_other_layout_methods): Grid for two-dimensional alignment and Flexbox for one-dimensional distribution.
