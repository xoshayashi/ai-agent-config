# IR slide design principles

Purpose: distilled operating principles from the 5,394 abstracted IR-slide corpus. These are
not templates and do not preserve company-specific facts, colors, or layouts. Use them as
decision rules when a slide must convince investors, IR teams, executives, or analysts with
evidence-rich but readable pages.

Each principle has: **Use when / Why it works / Parameters / Failure / Repair**.

## 1. Start From The Reader Question
- **Use when**: composing any slide, especially dense IR pages.
- **Why it works**: the corpus pages are strongest when each page answers a specific doubt:
  what changed, why believe it, how far along, what risk remains.
- **Parameters**: reader type, skepticism, decision moment, required evidence strength.
- **Failure**: a topic page lists information but cannot say which reader question it answers.
- **Repair**: rewrite the slide around one `reader_question`; move unrelated items to notes or
  appendix.

## 2. Make One Takeaway Carry The Page
- **Use when**: a page contains multiple metrics, diagrams, or narrative blocks.
- **Why it works**: even high-density IR pages resolve into one message: growth continues,
  costs are explainable, progress is on track, risk is bounded.
- **Parameters**: one title claim, one focal object, one final landing point.
- **Failure**: two equally strong claims compete, or the title is only a label.
- **Repair**: split the page or demote the weaker claim into a rail, note, or subordinate row.

## 3. Give The Strongest Evidence The Strongest Visual Weight
- **Use when**: selecting between chart, table, KPI, diagram, photo, or text.
- **Why it works**: readers trust the page faster when the evidence that proves the title is
  visibly primary.
- **Parameters**: size, placement, color weight, row/column highlight, caption proximity.
- **Failure**: an illustrative diagram or card grid is louder than the actual proof.
- **Repair**: enlarge the proof field, reduce decorative weight, and align the title's number
  to the exhibit that proves it.

## 4. Pair Numbers With Their Interpretation
- **Use when**: displaying KPIs, financial results, segment performance, or market figures.
- **Why it works**: the best corpus pages avoid leaving numbers as raw facts; they attach a
  short cause, implication, or caveat near the value.
- **Parameters**: interpretation rail, metric subline, callout, row note, speaker note.
- **Failure**: cards or tables show values with no "so what".
- **Repair**: add one concise interpretation line next to the number; if it needs a paragraph,
  move the detail to `speaker_notes`.

## 5. Use Tables For Accountability, Not Decoration
- **Use when**: exact comparisons matter: actual vs prior year, actual vs plan, forecast,
  segment rows, P&L/BS details.
- **Why it works**: tables give auditability when one protagonist column or row is made clear.
- **Parameters**: protagonist column, comparison basis, row grouping, unit, delta notation.
- **Failure**: every cell has equal weight and the reader must hunt for the answer.
- **Repair**: highlight one protagonist column/row, group rows by meaning, and move definitions
  outside the table body.

## 6. Treat Actual, Plan, Forecast, And Opportunity As Different States
- **Use when**: presenting guidance, medium-term plans, coverage matrices, pipeline, or market
  estimates.
- **Why it works**: IR trust depends on not letting potential or forecasts impersonate actuals.
- **Parameters**: solid vs pale vs dashed, labels, assumption line, source separation.
- **Failure**: future opportunity cells, forecast bars, and actual values share one style.
- **Repair**: restyle future/potential as pale or dashed, add an assumption, and reserve solid
  filled emphasis for actuals.

## 7. Make Progress Pages Show A Denominator
- **Use when**: communicating guidance progress, plan execution, roadmap stage, or current
  chapter.
- **Why it works**: progress is meaningful only against a full-year plan, total range, agenda,
  or defined universe.
- **Parameters**: actual, denominator, range, current marker, remaining space, caveat.
- **Failure**: a progress rate appears as a naked percentage or single bar.
- **Repair**: add the denominator and render a gauge, range, or actual/plan table; if no
  comparable bar exists, do not invent one.

## 8. Show Change With Time Grouping And Events
- **Use when**: quarterly trends, seasonality, implementation history, growth curves, or
  dividend/shareholder-return pages.
- **Why it works**: year bands, latest-period emphasis, and event markers explain both shape and
  cause.
- **Parameters**: period grouping, latest highlight, forecast split, event annotation, source.
- **Failure**: a long series of equal bars asks the reader to infer the period and turning point.
- **Repair**: group quarters by fiscal year, highlight the current period, and annotate only
  the events that explain the claim.

## 9. Decompose Before Explaining
- **Use when**: explaining ARR, GMV, revenue, profit change, cost burden, or conversion.
- **Why it works**: factor equations and waterfalls show where management can act.
- **Parameters**: formula, drivers, operator labels, contribution size, positive/negative sign.
- **Failure**: commentary claims "because of X" but the numbers do not decompose the result.
- **Repair**: turn the claim into factor cards, a bridge, or a driver table; verify the parts
  reconcile to the stated total.

## 10. Put Bad News In The Same Grammar As Good News
- **Use when**: showing decline, loss, missed plan, one-time cost, or revised guidance.
- **Why it works**: calm disclosure raises credibility more than hiding or stylizing the issue.
- **Parameters**: sign notation, cause, response, one-time vs structural split, forecast caveat.
- **Failure**: negative values are hidden, overcolored, or explained only in prose.
- **Repair**: show the number plainly, add cause and management action, and use the same table or
  chart grammar as positive results.

## 11. Separate External Evidence From Internal Interpretation
- **Use when**: mixing public statistics, third-party reports, company plans, and management
  judgment.
- **Why it works**: readers can audit what is externally verifiable and what is an assumption.
- **Parameters**: `source`, `assumption`, quoted asset, citation year, definition note.
- **Failure**: external data and internal estimate sit in one undifferentiated text block.
- **Repair**: put external provenance in `source`, internal logic in `assumption`, and keep both
  visually quiet.

## 12. Use Images Only As Evidence
- **Use when**: a real facility, product, UI, customer workflow, or completed asset makes a
  qualitative claim concrete.
- **Why it works**: real images reduce abstraction and prove that the business exists outside
  the spreadsheet.
- **Parameters**: crop, caption, date/location/spec, relationship to title claim.
- **Failure**: stock images or decorative photos fill whitespace without proving anything.
- **Repair**: replace with a real object or remove the image; add a short factual caption if the
  image remains.

## 13. Name The Relationship In Every Diagram
- **Use when**: drawing flows, systems, funnels, matrices, loops, hierarchies, or ecosystem maps.
- **Why it works**: the corpus diagrams work when arrows mean cause, flow, dependency, sequence,
  or ownership, not just "connectedness".
- **Parameters**: relation type, edge label, highlighted path, muted context.
- **Failure**: boxes and arrows look structural but do not prove causality or advantage.
- **Repair**: label each edge with what passes through it or what changes; delete nodes that
  cannot carry a role.

## 14. Use Coverage Matrices For Expansion Potential
- **Use when**: showing product rollout across sites, modules, factories, customer segments, or
  accounts.
- **Why it works**: filled and unfilled cells make current penetration and whitespace tangible.
- **Parameters**: row/column universe, actual cells, potential cells, timing tags, dashed future.
- **Failure**: opportunity is shown as a generic TAM number with no adoption path.
- **Repair**: define the universe, mark actual adoption, and show potential as dashed or pale
  cells with an assumption note.

## 15. Current-Location Slides Must Preserve The Whole Map
- **Use when**: agenda, roadmap, chapter divider, transformation plan, or phased strategy.
- **Why it works**: the reader understands both where they are and what remains.
- **Parameters**: full sequence, active state, muted inactive steps, progress label.
- **Failure**: the page shows only the current chapter and loses context.
- **Repair**: keep the full map visible, highlight the current location once, and avoid adding
  dense evidence to structural pages.

## 16. Use Quiet Pages As Rhythm, Not Fillers
- **Use when**: section dividers, agenda, disclaimer, closing statement, or between dense proof
  pages.
- **Why it works**: quiet pages reset attention and make subsequent dense evidence easier to
  read.
- **Parameters**: whitespace role, title scale, minimal meta, source/legal needs.
- **Failure**: structural pages become content pages or feel empty because the role is unclear.
- **Repair**: define the `rhythm_role`; either strip the page to its structural purpose or turn
  it into a real evidence slide.

## 17. Let Dense Pages Earn Their Density
- **Use when**: financial statements, appendix-like summaries, segment details, or multi-metric
  executive summaries.
- **Why it works**: density is acceptable when hierarchy, grouping, and protagonist fields lower
  scan cost.
- **Parameters**: row grouping, dominant column, fixed labels, small but readable type, notes.
- **Failure**: high-density tables flatten into a wall of equally strong cells.
- **Repair**: group rows, create one visual entry point, lower non-protagonist contrast, and
  split if more than one question is being answered.

## 18. Define Specialized Metrics At First Use
- **Use when**: ARR, NRR, EBITDA, adjusted profit, MAU, occupancy, conversion, or other domain
  KPIs appear.
- **Why it works**: IR readers may know the metric family but still need the company's exact
  definition.
- **Parameters**: definition note, calculation basis, numerator/denominator, period.
- **Failure**: a proprietary metric appears as if self-evident.
- **Repair**: add a short definition in footnote/source/assumption and keep the main body clean.

## 19. Keep Color Meaning Stable
- **Use when**: comparing periods, segments, bars, commentary panels, or diagram paths.
- **Why it works**: color is useful when it reduces lookup cost by matching a segment to its
  explanation.
- **Parameters**: protagonist color, reference gray, segment palette, actual/forecast style.
- **Failure**: the same color means different things on adjacent slides or every segment is
  equally saturated.
- **Repair**: define the color meaning for the slide, color one protagonist, and use direct
  labels instead of legends where possible.

## 20. Pair Absolute Amounts With Rates When Both Matter
- **Use when**: growth, margin, progress, cost absorption, or KPI quality is being evaluated.
- **Why it works**: amount tells scale; rate tells efficiency or intensity.
- **Parameters**: amount row, rate row, percentage-point notation, metric-subline gap.
- **Failure**: a high growth rate hides small scale, or a large amount hides weak conversion.
- **Repair**: place amount and rate as parent/child rows or value/subline; use pt for rate
  changes.

## 21. Use External Context To Explain, Not Excuse
- **Use when**: regulation, macro demand, market data, labor cost, FX, or industry issues frame
  company action.
- **Why it works**: external context is persuasive when it leads to a company-specific decision
  or mitigation.
- **Parameters**: external problem, source, company response, expected timing.
- **Failure**: the slide stops at "environment is changing" without a decision or action.
- **Repair**: add the company's response as the landing block and keep the external evidence
  muted upstream.

## 22. Preserve The Audit Trail For Future-Looking Claims
- **Use when**: forecasts, medium-term plans, pipeline, market estimates, or scenario pages.
- **Why it works**: readers need to see whether a future claim is plan, assumption, estimate, or
  target.
- **Parameters**: certainty label, forecast style, assumption line, risk note.
- **Failure**: a target is visually indistinguishable from a committed outcome.
- **Repair**: mark forecast/target visibly, add assumption language, and avoid promise-like
  copy in the title.

## 23. Keep Appendix Logic Out Of Mainline Proof Pages
- **Use when**: deciding whether dense detail belongs in the main deck.
- **Why it works**: mainline pages should advance a decision; appendices support audit.
- **Parameters**: reader need, narrative role, density, source detail, speaker notes.
- **Failure**: a mainline slide exists only because the data is available.
- **Repair**: state the decision it changes; if none, move it to appendix or delete.

## 24. Repair Locally Before Redesigning Globally
- **Use when**: rendered slides have issues but the claim and evidence are still right.
- **Why it works**: many corpus-derived failures are local: protagonist unclear, note mixed into
  body, gap too tight, comparison basis missing.
- **Parameters**: focal object, hierarchy, whitespace role, annotation policy, proof proximity.
- **Failure**: every finding triggers a complete redesign, creating new regressions.
- **Repair**: first adjust the focal object, evidence proximity, gap scale, note separation, and
  color meaning; redesign only when the reader question or evidence is wrong.
