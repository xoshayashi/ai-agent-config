# Composition atoms

Purpose: reusable composition atoms for evidence-led IR and investor pages. These are not slide
types. Choose and combine them from the reader question, focal object, evidence strategy,
density, and rhythm role.

Use this with `slide-decision-engine.md` and `composition-vocabulary.md`. If an atom starts to
behave like a fixed template, return to the reader question and evidence.

## Selection Gate

Before choosing an atom, answer:

- What reader question does the page answer?
- What is the single takeaway?
- What object proves it fastest: number, table, chart, diagram, image, text, note?
- What is the evidence status: fact, estimate, assumption, anecdote, open?
- What role does whitespace play: emphasis, separation, breathing, interpretation, legal?
- What fails if the page is rendered at thumbnail size?

## Atoms

### 1. Chart + Interpretation Rail
- **Use when**: a chart proves the claim but needs a cause, implication, or caveat beside it.
- **Do not use when**: the rail merely repeats the chart labels.
- **Parameters**: proof field span, rail width, cause bullets, source/assumption split.
- **Failure/repair**: if the rail is generic, replace it with quantified drivers or delete it.

### 2. Growth Series + Period Band + Event Markers
- **Use when**: quarterly or annual trends need seasonality, fiscal-year grouping, or event
  explanation.
- **Do not use when**: only current value matters.
- **Parameters**: year band, latest-period color, event markers, forecast styling.
- **Failure/repair**: if every bar is labeled and annotated, keep only the turning points and
  the current value.

### 3. Dual KPI Pair With Shared Grammar
- **Use when**: two related metrics answer one question, such as scale and profitability, users
  and monetization, or amount and rate.
- **Do not use when**: the metrics are unrelated peers.
- **Parameters**: mirrored axes, shared unit logic, per-metric conclusion label.
- **Failure/repair**: if the reader cannot compare them by row position, align labels and
  baselines or split.

### 4. Actual / Plan / Prior-Year Accountability Table
- **Use when**: progress must be judged against both plan and prior year.
- **Do not use when**: no plan or prior-year basis exists.
- **Parameters**: actual column, plan column, prior column, progress rate, YoY delta.
- **Failure/repair**: if the table is too wide, keep actual/plan/prior and move extra variance
  math to notes.

### 5. Protagonist Column Financial Table
- **Use when**: a P&L, BS, or KPI table contains one column the title points to.
- **Do not use when**: no column is more important than the others; use strict appendix style.
- **Parameters**: protagonist column, row groups, subrows for margin/ratio, unit outside table.
- **Failure/repair**: if the eye cannot find the protagonist in 3 seconds, add a restrained
  frame/fill and reduce non-protagonist contrast.

### 6. Table-Outside Hero KPI
- **Use when**: a dense table proves exact values but one KPI carries the message.
- **Do not use when**: pulling the KPI out would detach it from its calculation basis.
- **Parameters**: hero value, supporting table, connection label, source line.
- **Failure/repair**: if hero and table disagree visually, align them on one axis and label the
  extraction rule.

### 7. Current-Position Gauge + Facts Rail
- **Use when**: only current progress and a denominator/range exist.
- **Do not use when**: comparable historical bars exist; use comparison bars then.
- **Parameters**: current %, denominator, remaining range, facts rail, assumption.
- **Failure/repair**: if it becomes a single-value bar, replace with gauge/range card and add
  the denominator.

### 8. Comparison Bars With Seasonality Context
- **Use when**: current progress should be compared with prior years or benchmarks.
- **Do not use when**: prior bars are not comparable.
- **Parameters**: same-period bars, current actual, guidance/target range, forecast styling.
- **Failure/repair**: if benchmarks are invented or incomparable, remove them and use Atom 7.

### 9. Driver Equation / KPI Tree
- **Use when**: a result is produced by a small number of drivers.
- **Do not use when**: drivers cannot be quantified or reconciled.
- **Parameters**: operator labels, factor cards, focal result, driver notes.
- **Failure/repair**: if operators are decorative, write the formula in text and verify the
  units.

### 10. Waterfall / Bridge With Cause Labels
- **Use when**: a total changes and management must explain the difference.
- **Do not use when**: values do not add to a clear start/end bridge.
- **Parameters**: start, end, signed drivers, one-time/recurring tags.
- **Failure/repair**: if signs or totals are ambiguous, convert to a comparison table or fix the
  reconciliation.

### 11. Stacked Components + Color-Linked Cause Panel
- **Use when**: total and segment mix both matter, and each segment has a reason.
- **Do not use when**: segments are too many or causes are not segment-specific.
- **Parameters**: segment labels, bar-top total, matched cause panel, protagonist segment.
- **Failure/repair**: if color does all the work, add direct labels and simplify the palette.

### 12. Concept Left / Evidence Right
- **Use when**: a strategy, policy, or mechanism needs third-party evidence or a concrete proof.
- **Do not use when**: the right side is only decorative context.
- **Parameters**: claim block, evidence object, citation, implication line.
- **Failure/repair**: if concept and evidence do not answer the same question, split.

### 13. Business Model Flow + Real Object
- **Use when**: explaining how participants, assets, transactions, or workflows create revenue.
- **Do not use when**: a simple sentence would be clearer.
- **Parameters**: actors, arrows with relationship labels, example asset/photo/screenshot.
- **Failure/repair**: if the flow is abstract, attach a real example or remove the image.

### 14. Vertical Cause Flow To Company Action
- **Use when**: external environment leads to regulation, market change, or management action.
- **Do not use when**: no company-specific response follows.
- **Parameters**: upstream issue, external actor, company response, landing block.
- **Failure/repair**: if the slide ends at context, add the decision/action or drop the slide.

### 15. Coverage Matrix / Expansion Whitespace
- **Use when**: adoption can be shown across sites, modules, accounts, processes, or regions.
- **Do not use when**: the universe of rows/columns is undefined.
- **Parameters**: row universe, column universe, actual cells, potential cells, timing tags.
- **Failure/repair**: if opportunity looks promised, switch future cells to dashed/pale and add
  an assumption.

### 16. Phase Band + Mapping Row
- **Use when**: a roadmap has stages and each stage maps to initiatives, metrics, or evidence.
- **Do not use when**: there are more than five phases or no stage-specific evidence.
- **Parameters**: phase labels, active phase, mapped row, milestone dates.
- **Failure/repair**: if phases are decorative, tie each to a metric or decision point.

### 17. Current-Location Agenda / Chapter Map
- **Use when**: orienting readers in a deck or chapter sequence.
- **Do not use when**: the page needs to prove a business claim.
- **Parameters**: full sequence, active item, muted rest, optional subitems.
- **Failure/repair**: if it carries too much content, strip it back to navigation.

### 18. Evidence Strip
- **Use when**: trust comes from logos, examples, certifications, customers, or project count.
- **Do not use when**: items require individual explanation.
- **Parameters**: count label, equal sizing, source/date, grouping.
- **Failure/repair**: if logos/examples look random, group them or turn the strongest one into
  a case card.

### 19. Image-Proof Panel
- **Use when**: real assets, locations, products, screens, or operations prove a qualitative
  statement.
- **Do not use when**: the image cannot be inspected or tied to the claim.
- **Parameters**: crop, factual caption, date/location/spec label, related metric.
- **Failure/repair**: if it looks like stock, replace with a real artifact or remove.

### 20. Disclaimer / Legal Text Block
- **Use when**: forward-looking statements, definitions, trademarks, or legal caveats are
  mandatory.
- **Do not use when**: caveats can be handled as concise source/assumption lines.
- **Parameters**: paragraph grouping, readable line height, quiet title, footer.
- **Failure/repair**: if legal text crowds proof pages, move it to a dedicated admin page or
  footnote.

### 21. Quiet Section Reset
- **Use when**: the deck needs a rhythm break after dense evidence.
- **Do not use when**: the slide is only filler.
- **Parameters**: chapter number, short claim, visual rest, next-section hint.
- **Failure/repair**: if it feels empty, sharpen the chapter claim; do not add unrelated copy.

### 22. Closing Thesis + Proof Strip
- **Use when**: ending with a decision ask, investment takeaway, or recap of proof.
- **Do not use when**: the close is a legal or contact page.
- **Parameters**: thesis sentence, 2-4 proof metrics, next action, residual caveat.
- **Failure/repair**: if the close is generic, tie each proof metric to the deck spine.

## Atom Mixing Rules

- Mix at most two atoms on a mainline slide unless one is a quiet support strip.
- If atoms have different evidence states, separate them spatially and label assumptions.
- If a slide needs chart + table + diagram + photo, split it or move one object to appendix.
- Reuse the same atom across adjacent slides only when the reader should compare differences.
- Freshness comes from choosing the right atom and scale, not from new colors or decoration.

## Evidence-emphasis move → renderer knob map

Each of these emphasis moves is expressed through a spec knob (see `deck-spec.md`). Reach for
the knob instead of building a bespoke layout; that is what turns these atoms into output. This
is a mapping of intent to knob, not a template.

| Evidence-emphasis move | Reach for |
|---|---|
| Protagonist column (actual / forecast / latest) in a table (atoms 4, 5, 6) | table `emphasis_col` (or `emphasis_row`) |
| Decline / loss carried by color as well as glyph (principle 10) | table `color_negatives` + `△` notation in cell |
| Latest-period / turning-point bar stands out (atoms 2, 8) | chart `focal_category` |
| Stacked total + per-segment values readable (atom 11) | chart `segment_labels` on `stacked_column` |
| Pulled-out CAGR / multiple / net-change chip on the key bar | chart `annotation.badge` |
| YoY chip / diagonal growth arrow on the key bar | chart `annotation.yoy` / `annotation.trend_arrow` |
| Actual vs forecast kept visibly distinct (principle 6, 22) | chart `forecast_from` |
| One hero KPI leads, peers recede (atoms 3, 6) | KPI `focal` |
| Direct value labels instead of an axis | chart `value_labels` (+ `axis_less`) |

If the move you need is not in this map, check the capability boundary in
`data-and-diagram-rules.md`: it may be an object the renderer does not draw (re-express it a
different way) rather than a missing knob.
