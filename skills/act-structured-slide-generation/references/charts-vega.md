# Charts With Vega-Lite

Any chart the native engine cannot draw well is written as a Vega-Lite specification:
rows of data, a mark, and an encoding that maps columns to position, colour and size.
`scripts/act_vega.py` applies the Act look (font, palette, axes, legend, spacing) and
renders through vl-convert (headless, no browser, same input → same PNG). Consulting
staples that would take many layers to write by hand are provided as recipes compiled to
Vega-Lite: `mekko`, `slope`, `dumbbell`, `bullet`.

## Native Or Vega

Native python-pptx charts stay the default for plain column, bar, line, stacked and donut
charts: they are editable in PowerPoint and the emphasis knobs (`focal_category`,
`annotation.badge`) work on them. Use Vega when the chart needs something native cannot do:

- a consulting shape: Mekko (size x mix), slope (two-point change), dumbbell (gap per item),
  bullet (actual vs target vs bands);
- binned distributions, heat maps, faceted small multiples, layered reference lines or
  bands, direct labels on many series, computed fields (`transform`);
- a chart that must highlight one entity across many marks (`focal`).

A Vega chart is an image: the numbers stay auditable in the asset sidecar JSON and in
`deck.json`, but the chart cannot be edited in PowerPoint. Say so when the reader will
need to edit it.

## Choosing The Chart (Zelazny, *Say It With Charts*)

Decide the comparison the title makes, then the chart. The same rule appears in current
practitioner guides (Umbrex, *The Busy Consultant's Guide to Quantitative Charts*).

| The title says... | Comparison | Chart |
|---|---|---|
| X is n% of the total / the mix shifted | component | stacked or 100% column; `mekko` when size and mix both matter |
| A ranks above B | item | horizontal bar, sorted by value (not alphabetically) |
| X grew / fell over time | time series | column (few periods) or line (many) |
| Most cases fall in band n | frequency | histogram (`vega` with `bin`) |
| X rises with Y | correlation | scatter or bubble; four-quadrant scatter for portfolios |
| We got from A to B because of ... | bridge | `waterfall` |
| A moved from a to b, B from c to d | change between two points | `slope` (few items) or `dumbbell` (many items) |
| Each KPI against its target | performance vs target | `bullet` |

Highlight one thing (the client, the gaining segment, the decisive period) in the primary
colour and keep the rest grey. Label values directly instead of with a legend. Bars start
at zero.

## The Chart Object

Place it wherever a chart goes: `chart_insight.chart`, a `composite` chart block,
`chart_grid` cells, `metric_proof.chart`.

```json
{"kind": "vega", "unit": "cases",
 "data": [{"m": "1", "n": 8}, {"m": "2", "n": 14}, {"m": "3", "n": 42}],
 "mark": "bar",
 "encoding": {"x": {"field": "m", "type": "ordinal", "title": "months since onboarding"},
              "y": {"field": "n", "type": "quantitative"}},
 "focal": {"field": "m", "equals": "3"},
 "labels": true}
```

- `data` is a list of rows (tidy data). `mark`, `encoding`, `transform`, `layer`, `facet`,
  `hconcat`, `vconcat`, `repeat`, `resolve`, `params` and `title` pass straight through to
  Vega-Lite.
- `unit` becomes the quantitative axis title "(unit)" unless the encoding sets a title, and the
  argument audit attaches it to bare data values.
- `focal: {field, equals}` colours the matching marks primary and every other mark grey.
- `labels: true` adds value labels to a single-mark bar or point chart (`label_format` sets
  the d3 format, default `,`).
- Size, font, colours and spacing come from the slide box and the deck template; do not set
  `width`, `height` or `config`.

## Recipes

| Kind | Data | Draws |
|---|---|---|
| `mekko` | `columns: [{label, segments: [{label, value}]}]`, `unit`, `focal?` | Column width = column total (market size), segment height = share; segment labels "name n%" where they fit (the focal segment from 5%), column label and total below |
| `slope` | `periods: [start, end]`, `series: [{name, values: [a, b]}]`, `unit`, `focal?` | One line per series between two points, "name value" at both ends |
| `dumbbell` | `categories`, `from: {name, values}`, `to: {name, values}`, `unit`, `sort?` | A rule and two dots per category (from grey, to primary), sorted by gap, values over each dot, colour legend on top |
| `bullet` | `items: [{label, actual, target?, ranges?: [low, mid, high]}]`, `unit` | Grey qualitative bands, the actual as a dark bar, the target as a tick, the value labelled |

## Checks

- Validate compiles every Vega chart (`vegalite_to_vega`) and reports the Vega-Lite error text,
  so a malformed spec fails before the build. It also requires `data` (`vega`) or the recipe's
  fields, a `mark` / `layer` / `facet` / concat for `vega`, an existing `focal` segment and 2-8
  columns for `mekko`, and warns when a recipe has no `unit`.
- Rendered assets are cached by spec, box size, template tokens, the vl-convert version and
  the source of `act_vega.py`, so a theme or recipe change re-renders automatically.
- Dependency: `vl-convert-python` (in `scripts/requirements.txt`, installed by `setup.sh`,
  checked by `health-check.sh`). Fonts come from the same Noto Sans JP files the slide uses.

## Sources

- Gene Zelazny, *Say It With Charts* (McKinsey & Company; McGraw-Hill)
- Umbrex, *The Busy Consultant's Guide to Quantitative Charts* — "From Question to Chart"
- Satyanarayan et al., "Vega-Lite: A Grammar of Interactive Graphics", IEEE TVCG 2017
