# Consulting Page Catalogue

Strategy-firm decks reuse a small set of page archetypes. Most of them are not new shapes:
they are *combinations* of a few blocks on the 12-column grid. This catalogue maps each
archetype to either a dedicated pattern (when its geometry is specific) or a `composite`
recipe (when it is a combination). It is a lookup, not a template list: start from the reader
question and the evidence (`slide-decision-engine.md`), then use this page to find the
primitive that draws the chosen composition.

## How To Use

1. Name the archetype the composition needs (the reader question decides, not the topic).
2. If the table points to a dedicated pattern, use it.
3. If it points to a `composite` recipe, write the `grid` with the spans shown. Spans are
   column shares of 12; `h` is the row-height weight.
4. If nothing fits, compose a new `grid` from the six blocks. Only when a page needs a shape
   no block can draw (a new geometry, not a new arrangement) add a dedicated pattern.

## Blocks (`composite`)

| Block | Draws | Evidence key |
|---|---|---|
| `text` | optional heading + rule, then heading/body points | claim (`points`) |
| `kpi` | 1-4 KPIs (label, value + unit, delta, note); a row in a wide cell, a stack in a tall one | exhibit (`kpis`) |
| `callout` | so-what box: `statement` (+ small `heading`); `style` primary / accent / navy | claim (`statement`) |
| `chart` | any native chart spec (or an image `kind`), unit note and annotations included | exhibit (`chart`) |
| `table` | the table spec of `comparison_table` | exhibit (`table`) |
| `diagram` | an image-track asset (`node_graph`, `funnel`, `pyramid`, `venn`, ...) | exhibit (`diagram`) |

Rows without a chart, table or diagram never grow past 1.3x their content (the occupancy
contract): spare height goes to rows that can stretch, or the whole grid is centred. Rows that
need more than their weight's share get what they need first. Validate errors when the blocks
cannot fit the body, and `rules: true` on a row draws thin vertical rules between cells.

## Archetypes

### Evidence and numbers

| Archetype | Use when | Primitive |
|---|---|---|
| Chart + so-what rail | one chart proves the title, the reader needs the implication | `chart_insight`, or composite `[chart 7, text 5]` |
| Chart + so-what bar | the implication is one sentence the room must remember | composite `[chart 12] h3` / `[callout 12] h1` |
| Chart + rail + bar | the chart needs reading notes *and* one decision line | composite `[chart 7, text 5] h3` / `[callout 12] h1` |
| KPI strip + table | headline numbers, then the line items behind them | composite `[kpi 12] h1` / `[table 12] h2` |
| KPI rail + chart | three numbers frame one trend | composite `[kpi 3, chart 9]` |
| Two charts, one claim | two views (volume and rate, two segments) prove one point | composite `[chart 6, chart 6] h3` / `[callout 12] h1` |
| Small multiples | same grammar across 2-4 units | `chart_grid` |
| Hero number proof | one number changes the belief | `metric_proof` |
| Bridge | start-to-end movement with drivers | `waterfall` |
| Benchmark table | accountability across rows and columns | `comparison_table` |
| Before / after | measured change across aligned dimensions | `before_after` |
| Customer proof | 2-4 cases, each with a result | `case_strip` |

### Structure and logic

| Archetype | Use when | Primitive |
|---|---|---|
| Issue → implication → action | a diagnosis page that ends in a move | composite `[text 4, text 4, text 4] rules` / `[callout 12]` |
| Situation / complication / resolution | the SCR spine on one page | composite `[text 4, text 4, callout 4]` |
| Pillars / framework | 2-4 parallel strategic thrusts | `column_framework` |
| Issue / driver tree | outcome decomposed into drivers | `logic_tree` |
| Driver equation | outcome = factor x factor | `driver_decomposition` |
| 2x2 with quadrant content | SWOT, prioritisation, portfolio, option sorting | `matrix_2x2` |
| Positioning map | players placed on two axes | `competitive_landscape` |
| Hub and spoke | one platform coordinates several parts | `hub_spoke` |
| Risk assessment | likelihood x impact with responses | `risk_matrix` |
| Option evaluation | options scored on criteria, one recommended | `harvey_table` |

### Time and execution

| Archetype | Use when | Primitive |
|---|---|---|
| Workplan | who does what, from when to when | `gantt` |
| Decision timeline | when each decision is taken | `milestone_timeline` |
| Phased roadmap | stages and what each delivers | `roadmap` |
| Process with outcomes | sequence where each step yields something | `process_flow` |
| Guidance progress | where the year stands against the range | `guidance_progress` |

### Framing and close

| Archetype | Use when | Primitive |
|---|---|---|
| Executive summary | the deck's argument in 3-4 points | `executive_summary` |
| Recommendation + rationale | the ask, then three reasons | composite `[callout 12] h1` / `[text 4, text 4, text 4] h2` |
| Decision request | the meeting must decide one thing | `statement` (`decision_request`) |
| Chapter reset | long, read-oriented decks only | `section_divider` |

## A Full Recipe

Chart, reading notes, and one decision line:

```json
{"pattern": "composite",
 "title": "...", "subtitle": "...",
 "grid": [
   {"height": 3, "cells": [
     {"span": 7, "block": {"type": "chart", "chart": {"type": "stacked_column", "unit": "...",
                                                     "categories": ["..."], "series": [{"name": "...", "values": [1]}]}}},
     {"span": 5, "block": {"type": "text", "heading": "...", "points": [{"heading": "...", "body": "..."}]}}]},
   {"height": 1, "cells": [
     {"span": 12, "block": {"type": "callout", "heading": "...", "statement": "..."}}]}
 ],
 "source": "..."}
```

## Caps And Checks

- `composite`: 1-3 rows, 1-4 cells per row, spans 2-12 summing to at most 12 (a warning when
  fewer: say so if the empty columns are intended), KPI blocks hold at most 4, charts get at
  least 4 columns (warning). Each block must carry its key (`points`, `kpis`, `statement`,
  `chart`, `table`, `diagram`). An `accent` callout uses the slide's one accent.
- A composite counts as an evidence page (`source` / `assumption`, a number in the title) when
  it holds a chart, table, KPI or diagram block; a text-and-callout composite is qualitative.
- Two composites in a row are "the same pattern" only when their grids match (same spans and
  block types per row), so varied composites do not trip the monotony warning.
