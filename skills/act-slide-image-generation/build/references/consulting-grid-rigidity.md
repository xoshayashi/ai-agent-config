# Consulting Grid Rigidity

Use this contract to create the precise, evidence-led structure associated with strong strategy-consulting exhibits. Apply the principles across topics and visual grammars; the contract governs alignment quality rather than a fixed slide template.

## Structural Skeleton

Freeze the structural skeleton before material styling. Use the 16-column ACT parent grid and the 8px vertical baseline as the shared coordinate system for region edges, text anchors, rules, values, icons, and connector ports. The balanced top-level body container uses parent-grid lines `2..16`, giving equal 97px side clearances inside the 72px safe shell. Subdivide its 14-column interior with a small repeated recipe selected from the content, such as `7+7`, `8+6`, `5+5+4`, or `4+3+3+4`; nested regions may merge or subdivide these integer spans.

Build each evidence region as a compact hierarchy: one claim label, its evidence directly below or beside it, and an implication attached to the same column system. A complete content slide normally uses 2-4 evidence regions, with 2-5 repeated modules inside a region when repetition carries meaning. Keep the reading sequence visible through shared axes, alignment, and proximity.

## Component Geometry Plan

Add `component_geometry_plan` to every generation and repair plan. Register every meaningful component with:

- `id`, `type`, `parent_id`, and `bounds`
- `left_anchor_line` and `right_anchor_line` for rectangular components
- `top_baseline_step` and `bottom_baseline_step` on the 8px basis
- `text_anchor_line` and `first_baseline_step` for text
- `center_anchor_line` for centered icons, numbers, or compact marks
- `role` and `peer_group` when the component repeats

At least 90% of registered major edges land within 4px of a declared column line or baseline. Establish at least three shared vertical anchors and three shared horizontal anchors in the body. Each major component shares one vertical and one horizontal axis with another meaningful component. Record `orphan_region_count: 0`.

## Repeated Modules

Treat peer modules with table-like precision. Within each `peer_group`, keep width, height, internal padding, heading baseline, evidence baseline, and structural-rule position within 4px. Use `16, 24, 32, 48px` gaps; at least 95% of measured gaps use the declared token. Record `repeated_module_consistency >= 0.95`.

Use rectangular cells, shared rules, and aligned text as the primary grouping material. Apply a surface fill when it carries state or emphasis. One slide-wide emphasis system highlights either the key column, key value, or conclusion row, with `single_focus_fill` reserved for the single most important signal.

## Structural Rules

Add `structural_rule_plan`. Register every information-bearing line with `id`, `role`, `parent_id`, `orientation`, `start_anchor`, `end_anchor`, `baseline_step`, explicit `start_point` and `end_point`, `stroke_px`, and `color_role`. The prompt compiler converts the explicit points to render-basis pixels and keeps anchor indices in the validator manifest.

Use roles such as `section_boundary`, `comparison_baseline`, `column_divider`, and `leader` inside the body composition. Keep structural rules horizontal or vertical, terminate them on declared grid lines or component centers within 4px, and use a shared 1-2px stroke token at the same hierarchy. A 2-3px rule is available for one primary body emphasis. Place rules where they clarify rows, columns, ownership, or a comparison baseline.

## Connector Geometry

Add `connector_plan` whenever the exhibit contains a flow. Register `from_id`, `to_id`, source and target ports, route orientation, waypoints, bend count, crossing count, line token, and arrowhead token. Use horizontal or vertical segments with grid-snapped ports and waypoints. Standard flows use 0-2 right-angle bends and `crossing_count: 0`. A true loop may use one declared arc with center, radius, and tangent endpoints.

Keep nodes in repeated rectangular cells with equal dimensions when they are peers. Align connector centerlines to the shared row or column axes. This produces a crisp causal path without adding decorative geometry.

## Grid Rigidity Score

Plan and audit these measured values:

- `edge_registration_score >= 0.90`
- `repeated_module_consistency >= 0.95`
- `gap_token_compliance >= 0.95`
- `structural_rule_pass_rate = 1.00`
- `connector_endpoint_pass_rate = 1.00` when connectors exist
- `structured_cell_fill = 0.65..0.85`
- `orphan_region_count = 0`

Calculate `grid_rigidity_score = 0.35 × edge_registration + 0.25 × module_consistency + 0.20 × gap_compliance + 0.10 × rule_pass + 0.10 × connector_pass`. Use `1.00` for connector pass when the exhibit has no connectors. Approve at `>= 0.93`.

At thumbnail size, the column and row structure remains visible through repeated edges, aligned labels, equal modules, and consistent gaps even when few rules are drawn. At full size, every planned anchor has a measured counterpart.

## Prompt Translation

State the structural skeleton before visual material. Use prompt language such as `precise shared column edges`, `repeated equal modules`, `compact ruled comparison`, `orthogonal connectors`, and `table-like alignment`. Preserve compositional variety through declared spans, nesting, merges, evidence forms, and emphasis choices inside the registered grid.

## Research Basis

- [IBM Design Language: 2x Grid](https://www.ibm.com/design/language/2x-grid/): columns, rows, equal divisions, gutters, base units, and repeatable spatial rhythm.
- [Carbon Design System: 2x Grid](https://carbondesignsystem.com/elements/2x-grid/overview/): 16-column geometry, fixed margins, padding, gutters, and type alignment.
- [Microsoft PowerPoint: Gridlines and Snap-to-Grid](https://support.microsoft.com/en-US/PowerPoint/work-with-gridlines-and-use-snap-to-grid-in-powerpoint): grid snapping, guides, smart guides, and straight-line drawing.
- [Microsoft PowerPoint Auto Fix](https://support.microsoft.com/en-US/PowerPoint/align-your-content-quickly-and-easily-with-auto-fix): alignment, uniform sizing, distribution, and connector straightening as one cleanup system.
- [GOV.UK Design System: Layout](https://design-system.service.gov.uk/styles/layout/): repeatable fractions and nested grids.
- [W3C CSS Grid Layout](https://www.w3.org/TR/css-grid/): explicit two-dimensional tracks, gutters, nesting, and alignment.
- [BCG, The Energy Transition's Next Chapter](https://web-assets.bcg.com/5c/4d/5796b7ef46beb3110c30feed6216/the-energy-transitions-next-chapter-sep-2025-edit-04.pdf) and [McKinsey China Consumer Report 2021](https://www.mckinsey.com/southern-us/~/media/mckinsey/featured%20insights/china/china%20still%20the%20worlds%20growth%20engine%20after%20covid%2019/mckinsey%20china%20consumer%20report%202021.pdf): public-exhibit examples used only to infer recurring claim-evidence hierarchy, repeated modules, and common baselines.
