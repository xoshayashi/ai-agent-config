# Design Richness Without Breakage

A deck can pass every geometric check and still be poor: white pages with grey boxes, no place for
the eye to land, every page the same weight. Published slide rubrics name this directly: "Lack of
Style" (AeSlides) and "no hierarchy / cluttered / unbalanced" (SlideAudit). PresentBench reports
visual design as the main weakness of every generator it tested. This file is how this skill makes
pages rich while keeping the grid, type scale and palette fixed, which the same rubrics require.

## Contents

- The four levers
- Visual anchors (one per content page)
- Icons
- Inverse surfaces and rhythm
- Layout diversity
- Contrast
- Checks that enforce this
- Sources

## The four levers

Richness comes from contrast inside one system, never from new colours, gradients or shadows:

| Lever | What changes | Tool |
|---|---|---|
| Emphasis | one item regains colour, the rest stay grey | `focal` on points, cards, rows, series; `focal_category`; `emphasis_col` |
| Scale | one number or line is much larger than the rest | hero numbers (`metric_proof`, `kpi_dashboard`, `case_strip`, `recap`) |
| Surface | a page or panel takes the dark brand surface | `tone: "inverse"` on cover / statement / section_divider; `callout` panels |
| Marker | parallel items carry a semantic icon | `icon` on points, KPIs, pillars, spokes, composite blocks |

Use one emphasis attribute per message (colour, size, position or weight); stacking several adds
clutter.

## Visual anchors (one per content page)

Every content page needs one object the eye lands on first: a hero number, a highlighted series or
row, a `focal` card, an icon row, a dark or tinted panel, or a diagram. A page that is only text
boxes in a row fails the glance test (the point must come across in about three seconds).
Patterns that draw an anchor by themselves (charts, waterfall, risk grid, timelines, cases, hub,
Harvey balls, ...) pass automatically; text patterns (`executive_summary`, `two_column`,
`column_framework`, text-only `composite`) need a `focal`, an `icon` set, or a callout.

## Icons

- The set is a curated subset of Lucide in `assets/icons/` (ISC licence, `assets/icons/LICENSE`),
  drawn as native freeform vectors by `scripts/act_icons.py`: editable, recoloured by the deck
  template, crisp at any size. Add an icon by copying its SVG from lucide-static into that folder.
- Lucide's geometry is kept: 24-unit grid, a stroke of 2/24 of the icon size, round caps and
  joins. All icons in one context share one size (`ICON_ROW`), so strokes match.
- An icon is a semantic marker for an item in a parallel set (summary points, KPIs, pillars,
  spokes), always next to its label; most icons carry no agreed meaning on their own. Give every
  item in the set an icon, or none. Never use an icon as decoration or as the only carrier of
  meaning.
- Placement is fixed per pattern so capacity does not change: the kicker column (summary), the
  label line's right edge (KPIs, spokes), the header band (pillars), before a block heading
  (composite).

## Inverse surfaces and rhythm

- `tone: "inverse"` paints the slide background with the template's brand dark (`primary_deep`)
  and swaps every text and fill role in pairs, so pairs that contrasted on the light surface still
  contrast. The background is the slide's own background property, never a full-bleed rectangle.
- Allowed on `cover`, `statement` and `section_divider` only. Evidence pages stay on the light
  surface, where charts and tables are read.
- Rhythm: a deck of eight or more slides needs at least one peak (an inverse cover or close, or a
  hero-number page). Keep inverse pages to about a quarter of the deck at most, or dark stops
  meaning "this matters". Section dividers belong to long, read-oriented decks.

## Layout diversity

`validate_spec` computes the effective number of layouts across content slides (a Vendi score with
same-layout similarity 1, different 0, which equals exp(entropy) of the layout distribution).
Template-based generators score low on this measure (DeepPresenter reports 0.17-0.35 for them,
against up to 0.79 for free-form generation). Below half the content-slide count (capped at eight),
replace repeats with a `composite` arrangement or another pattern. Two composites count as the same
layout only when their drawn grids match.

## Contrast

`verify_deck` checks every text run against what is actually behind it (its own fill, the nearest
filled shape under its centre, the slide background, then the master background) and fails a WCAG
2.1 contrast ratio below 3:1. This is what makes inverse pages, dark bands and tinted cards safe.

## Checks that enforce this

| Check | Tool | Severity |
|---|---|---|
| Unknown icon name (with suggestions), icon without label | validate | error |
| Icon on only part of a parallel set | validate | warning |
| `tone` other than inverse, or inverse on an evidence pattern | validate | error |
| Content page with no visual anchor | validate | warning |
| No peak page in a deck of 8+, inverse over 25%, low layout diversity | validate | warning |
| Text-to-ground contrast below 3:1 | verify | failure |
| Every pattern at min / max / overload with icons and inverse on, all templates | stress_deck | regression |

## Sources

- AeSlides (2026), verifiable aesthetic rewards and the "Lack of Style" label — arXiv 2604.22840
- SlideAudit (UIST 2025), 27 slide design flaw types — arXiv 2508.03630
- PresentBench (2026), visual design checklist — arXiv 2603.07244
- DeepPresenter (2026), Vendi diversity of generated decks — arXiv 2602.22839; Vendi score — arXiv 2210.02410
- Lucide icon design guide — lucide.dev/contribute/icon-design-guide; NN/g on icon usability (labels)
- Datawrapper on emphasis with colour (grey first, then restore colour to one item)
- Duarte, the glance test and the sparkline story structure
- WCAG 2.1 contrast ratio
