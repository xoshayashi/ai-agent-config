# Core Layout And Typography

This file is the geometry and typography source of truth for every ACT 16:9 slide.

## Positive Directive Contract

Write every instruction as a target state, selected option, measurable range, and corrective action. Use `place`, `keep`, `select`, `preserve`, `scale`, `rewrite`, and `repair by`. Describe quiet regions as intentional blank canvas and technical routes as the exclusive approved path.

## 1672x941 Master Shell

- Outer shell: `x=72..1600`, `y=50..924`
- Canvas padding: the deck-wide `equity_story_master` profile, `50/72/17/72px` top/right/bottom/left
- H1: `x=72 y=50 w=1492`, one uniform line, 28pt/700, `main_message`
- Subtitle: `x=72 y=123 w=1492`, one uniform line, 20pt/400, `sub_message`
- Header text frames: square wrapping, zero insets, top anchoring, left alignment
- Header scale: H1 visible height 47-50px with calibrated center 48px; subtitle visible height 33-35px with calibrated center 34px
- Reference-render calibration: the deck source uses 28pt/700 and 20pt/400 at a shared 0.58in left anchor; rendered approval targets the centers above so image-model type stays visually aligned with the source deck
- Header pilot: the first approved slide; corresponding H1/subtitle visible heights stay within 2px throughout the deck
- Header/body quiet band: the first meaningful body region begins 48-112px below the `y=170` header clearance datum, selected with the footer mode and body-height target
- Footer absent: target envelope `y=190..869`, lowest meaningful body pixel `y=857..869`, area-weighted body centroid 58-62% of canvas height
- Footer present: target envelope `y=190..869`; provenance frame `x=72 y=866 w=1528 h=48`, 9pt, zero insets, left aligned, vertically centered, 14px line metric, one or two lines
- Horizontal optical target: `x=836`

Scale all coordinates proportionally for an approved output size.

## Title Fit

H1 uses one uniform line and one text run. Estimate rendered width before freezing `exact_text`. Rewrite until 28pt fits comfortably, retaining topic, change/tension, and implication. Place dates, scope qualifiers, and secondary clauses in subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

Apply `header_copy_budget_lock` before generation. H1 uses <=28 Japanese full-width-equivalent characters and subtitle uses <=36; two half-width ASCII characters count as roughly one full-width equivalent for the first-pass estimate. Then verify actual rendered width and keep each line at <=92% of its fixed text box. Repair overflow through copy editing and body redistribution while preserving the deck-wide 28pt/20pt master.

## Rendered Type Review

- H1 visible glyph height: 47-50px on the 1672 basis
- Subtitle visible glyph height: 33-35px on the 1672 basis
- Subtitle color: `sub_message`; visually subordinate to H1 and distinct from the `primary_accent` role
- Body/card/table/data text: >=20pt equivalent
- Section heading visible height: 28-34px on the 1672 basis
- Primary body-label visible height: 22-28px
- Supporting-text visible height: 18-24px
- Integrated-takeaway visible height: 26-32px and no larger than the section-heading role

When the rendered hierarchy falls outside these bands, regenerate with the shell preserved and the target rendered size reinforced.

Approve the first rendered slide as the header pilot only when both roles pass the absolute bands and visually match the supplied reference-render header crop. Keep corresponding H1/subtitle visible heights within 2px of that pilot on every subsequent slide. Repair scale drift by preserving the fixed point-size master, restating the calibrated rendered centers, and regenerating the affected slide.

## Deck-Wide Header Consistency

Freeze one header master before slide generation: H1 `28pt/700 main_message`, one line, `x=72 y=50 w=1492`; subtitle `20pt/400 sub_message`, one line, `x=72 y=123 w=1492`. Use square wrapping, zero text insets, top anchoring, and left alignment. Treat these as deck-wide fixed tokens and verify actual rendered height against the absolute bands plus the pilot because image models do not guarantee point sizes exactly. Resolve copy fit through rewriting, redistribution, or slide splitting. Approve when the header reads as the same role and scale at contact-sheet size and the rendered glyph heights stay within 2px of the pilot.

Apply `header_alignment_lock`: content slides use left-aligned H1 and subtitle with the shared `x=72 w=1492` text frame and ragged-right endings. Approve when their first visible glyph x-coordinates differ by <=2px and the H1 aligns to the main body grid within <=4px. Use centered headers only for an explicitly requested cover, interstitial, or closing slide recorded as `header_alignment_exception`.

## Canvas Edges And Optical Balance

Measure the rendered header anchor, body envelope, footer clearance, and body-only optical centroid separately. Keep the header fixed to the deck master. In footer-present mode, use top-title and bottom-content margins as descriptive evidence. In footer-absent mode, apply `footer_absent_vertical_balance_lock`: actual H1-top visible margin and canvas-bottom body margin differ by <=12px.

On the 1672x941 basis, apply `equity_story_master` unchanged across the deck and keep all meaningful pixels inside `x=72..1600 y=50..924`. Treat the four bands outside that shell as measured quiet canvas during first-render review as well as repair review. The body union keeps its left/right clearance difference within 8px. Vertical balance follows the selected envelope and centroid, plus the <=12px visible-margin-difference lock in footer-absent mode. Repair the top through the header master, the sides through the registered grid envelope, and the bottom through body/footer composition.

## Text-led message boxes

Register every message box in `message_box_plan`. Use one dedicated text component, zero icon children, and zero icon atoms. On the 1672x941 basis, use `x=72 y=796 w=1528 h=73`, one centered 17pt line, a 25px line metric, 24px vertical and horizontal padding, zero text insets, and centered vertical anchoring. Bind fill, stroke, and text to `single_focus_fill`, `single_focus_stroke`, and `main_message`. Rewrite the message or split the slide to preserve the one-line master.

Freeze `header_furniture_plan` with the exact-text specification. Set the header surface to `uninterrupted_canvas`, register `[header_h1, header_subtitle]` as its complete visible component set, and set visible geometry to zero. Side and bottom outer bands remain quiet canvas; a genuine traceable source may occupy the approved footer baseline. During full-size review, inventory the header pixels against these two registered text components and the continuous canvas surface. Repair restores that declared surface and inventory without moving the approved body.

## Content Footprint And Balance

Measure the combined body silhouette, including main and supporting regions, through safe bounds, grouping proximity, reading path, and pilot-calibrated optical balance.

- Body side margins are selected from the target width utilization and may be asymmetric when visual weight remains balanced
- Footer absent: lowest meaningful body pixel lands at `y=857..869`; canvas-bottom visible margin and actual H1-top visible margin differ by <=12px
- Footer present: treat the provenance frame as bottom furniture; keep decision-carrying body text visually clear of its `y=866..914` band
- Occupancy, region weights, and blank bands: measure visible envelope, top-level container, allocated region area, meaningful foreground area, text union, and object union according to `grid-flex-layout.md`
- Proximity: related-element gaps are smaller than group-separation gaps; heading-to-owned-content gap is smaller than the separation above the heading
- Rhythm: repeated same-level gaps use the declared spacing token and snap to the shared 8px grid within ±4px
- Optical centroid: the body-only centroid passes the footer-mode range; values outside the range are repair-required
- Vertical body utilization: footer-absent 82-94% and footer-present 78-90% of the reachable `y=190..869` band
- Header/body proportion: the compact header introduces the page and the body remains the dominant visual mass at thumbnail size
- Single aspect-locked chart, diagram, or illustration: preserve native aspect ratio within 5% and use the dedicated 55-88% body-width band

Prioritize shell bounds, >=20pt body text, connected reading path, grouping proximity, occupied silhouette, then optical review. Repair compact islands, weak endpoints, disconnected evidence groups, and accidental blank bands by recomposing meaningful regions. Preserve aspect ratio and intentional asymmetry when it clarifies hierarchy.

### Zonal mass plan

Freeze the three-zone silhouette before prompting:

- Header visible marks: `y=66..155`, compact text-only entry
- Body target envelope: `y=190..869` in both footer modes; visible sources occupy the separate footer frame
- Required body width utilization: 78-92% of the 1528px available body width; a single aspect-locked focal object uses 55-88% while its complete body passes 78-92%
- Required body height utilization: footer-absent 82-94% of the reachable body band; footer-present 78-90%
- Top-level layout container: 82-94% width; footer-absent 86-96% height; footer-present 84-94% height
- Allocated child-region area fill: 58-80% of the available footer-mode body band
- Meaningful foreground fill: 18-38% of the visible body envelope, pilot-calibrated within the same content mode
- Text ink area: 6-20% of the visible body envelope; meaningful-object ink area: 10-30%; their spatial union defines foreground fill
- Footer-absent area-weighted body vertical centroid: 58-62% of the full 941px canvas height
- Footer-present area-weighted body vertical centroid: 58-62% of the full 941px canvas height
- Centroid mass: every painted body component, including direct Grid children and the painted message box, weighted by rectangle area; the message box remains outside primary-body horizontal occupancy
- Remaining blank space: one explicitly named quiet region that supports the reading path

Judge width, height, allocation area, foreground fill, and text/object unions together. Repair a sparse or fragmented silhouette by resizing and redistributing registered regions on the explicit Grid/Flex layout tree while the header and footer anchors remain unchanged.
