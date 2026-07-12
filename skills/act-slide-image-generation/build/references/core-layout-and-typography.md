# Core Layout And Typography

This file is the geometry and typography source of truth for every ACT 16:9 slide.

## Positive Directive Contract

Write every instruction as a target state, selected option, measurable range, and corrective action. Use `place`, `keep`, `select`, `preserve`, `scale`, `rewrite`, and `repair by`. Describe quiet regions as intentional blank canvas and technical routes as the exclusive approved path.

## 1672x941 Master Shell

- Outer shell: `x=72..1600`, `y=72..869`
- Canvas padding: one 72px inset on top, right, bottom, and left
- H1: `x=72 y=72 w=1528`, one uniform line, 38pt/700, 36pt floor, 40pt cap, `#2D332E`
- Subtitle: `x=72 y=136 w=1528`, 32pt/400, 30pt floor, 34pt cap, neutral gray `#626A64`
- Header stack gap: actual glyph-to-glyph gap 14-22px, target 18px
- Header/body quiet band: actual subtitle bottom to first body mark >=64px, target 64-80px
- Body start: `y=238`
- Footer absent: available band `y=238..869`, target envelope `y=248..815`, body-only centroid `y=508..546`
- Footer present: available band `y=238..806`, target envelope `y=248..759`, baseline `y=858`
- Horizontal optical target: `x=836`

Scale all coordinates proportionally for an approved output size.

## Title Fit

H1 uses one uniform line and one text run. Estimate rendered width before freezing `exact_text`. Rewrite until 38pt fits comfortably, retaining topic, change/tension, and implication. Place dates, scope qualifiers, and secondary clauses in subtitle or body. Split the message across slides when one governing claim still exceeds the title box.

Apply `header_copy_budget_lock` before generation. H1 uses <=28 Japanese full-width-equivalent characters and subtitle uses <=36; two half-width ASCII characters count as roughly one full-width equivalent for the first-pass estimate. Then verify actual rendered width and keep each line at <=92% of its fixed text box. Repair overflow through copy editing and body redistribution while preserving the deck-wide 38pt/32pt master.

## Rendered Type Review

- H1 visible glyph height: 42-50px on the 1672 basis
- Subtitle visible glyph height: 28-36px
- Subtitle optical height: 65-78% of H1
- Subtitle color: `#626A64`; visually subordinate to H1 and distinct from Petrol body emphasis
- Body/card/table/data text: >=20pt equivalent
- Section heading visible height: 28-34px on the 1672 basis
- Primary body-label visible height: 22-28px
- Supporting-text visible height: 18-24px
- Integrated-takeaway visible height: 26-32px and no larger than the section-heading role

When the rendered hierarchy falls outside these bands, regenerate with the shell preserved and the target rendered size reinforced.

Treat an oversized rendered H1 as a hierarchy blocker even when it remains on one line. With a pilot, keep corresponding glyph-box deviation within 4px. Without a pilot, use the rendered bands above as the fallback calibration.

## Deck-Wide Header Consistency

Freeze one header master before slide generation: H1 `38pt/700 #2D332E`, one line, `x=72 y=72 w=1528`; subtitle `32pt/400 #626A64`, one line, `x=72 y=136 w=1528`. Treat these as the target token system; verify the rendered PNG by comparison with the pilot because image models do not guarantee point sizes or baselines exactly. Resolve copy fit through rewriting, redistribution, or slide splitting. Approve when the header reads as the same role and scale at contact-sheet size, the rendered anchors stay within the pilot-calibrated tolerance, and no slide creates a competing header hierarchy.

Apply `header_alignment_lock`: content slides use left-aligned H1 and subtitle with the shared `x=72 w=1528` anchor and ragged-right endings. Approve when their first visible glyph x-coordinates differ by <=2px and the H1 aligns to the main body grid within <=4px. Use centered headers only for an explicitly requested cover, interstitial, or closing slide recorded as `header_alignment_exception`.

## Canvas Edges And Optical Balance

Measure the rendered header anchor, body envelope, footer clearance, and body-only optical centroid separately. Keep the header fixed to the deck master; the lowest body element does not move the header. Use top-title and bottom-content margins as descriptive evidence rather than a symmetry target. Repair body imbalance inside the selected content band, preserving header clearance, safe-shell bounds, and footer mode.

On the 1672x941 basis, keep all meaningful pixels inside `x=72..1600 y=72..869`. Measure the same visible-bound method on all four sides and keep comparable opposite-side clearance differences within 8px. Repair the top through the header master, the sides through the body envelope, and the bottom through body/footer composition.

Freeze a `canvas_furniture_allowlist` with the exact-text specification. The top outer band contains the shared left-aligned H1 and subtitle only. Side and bottom outer bands remain quiet canvas; a genuine traceable source may occupy the approved footer baseline. During full-size review, inventory every visible mark in the outer bands and compare it with the allowlist. Any running header, brand label, deck descriptor, page marker, navigation cue, corner annotation, or decorative rail is classified as `outer_band_contamination` and repaired by restoring the canvas surface without moving the approved header or body.

## Content Footprint And Balance

Measure the combined body silhouette, including main and supporting regions, through safe bounds, grouping proximity, reading path, and pilot-calibrated optical balance.

- `T2_balanced`, `T3_dense`, `T4_appendix_dense`: body side margins 24-72px inside the shell
- `T1_sparse`: body side margins 48-96px inside the shell
- Footer absent: bottom gap 26-80px
- Footer present: bottom gap 30-80px
- Coverage grid: divide the body band into 4 columns x 3 rows; classify each cell as occupied or intentionally blank
- Occupancy, blank cells, region weights, and blank bands: diagnostic measurements calibrated by layout family and approved pilot, not universal quotas
- Proximity: related-element gaps are smaller than group-separation gaps; heading-to-owned-content gap is smaller than the separation above the heading
- Rhythm: repeated same-level gaps snap to the shared 8px grid within a half-unit tolerance
- Optical centroid: compare body-only centroid with the selected content band and reading path; large deviations trigger multimodal review
- Vertical body utilization: compare first/last meaningful body rows with the selected family and pilot; without a pilot, preserve deliberate breathing above and below rather than targeting a universal fill percentage
- Header/body proportion: the compact header introduces the page and the body remains the dominant visual mass at thumbnail size
- Single chart, diagram, or illustration: preserve native aspect ratio within 5%

Prioritize shell bounds, >=20pt body text, connected reading path, grouping proximity, occupied silhouette, then optical review. Repair compact islands, weak endpoints, disconnected evidence groups, and accidental blank bands by recomposing meaningful regions. Preserve aspect ratio and intentional asymmetry when it clarifies hierarchy.

### Zonal mass plan

Freeze the three-zone silhouette before prompting:

- Header visible marks: `y=72..172`, compact text-only entry
- Footer absent target body envelope: `y=248..815`; footer present: `y=248..759`
- Typical body width utilization: 72-92% of the available body width
- Typical body height utilization: 70-90% of the available body height
- Footer-absent body-only vertical centroid: 54-58% of canvas height
- Remaining blank space: one explicitly named quiet region that supports the reading path

Judge width and height together. A wide-but-shallow strip, a narrow-and-tall island, or several disconnected mini-panels returns to composition planning. Repair by scaling and redistributing the complete body group inside its fixed band, while the header and footer anchors remain unchanged.
