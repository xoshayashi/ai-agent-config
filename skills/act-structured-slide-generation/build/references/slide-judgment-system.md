# Slide Judgment System

Use this file before composing any content slide. It defines the required decision fields
for a slide. It is not a template catalog and must not be used to pick a fixed layout from
a topic label.

## Anti-Template Audit

Run this audit while designing and again after rendering. If any answer is yes, repair the
slide before delivery.

- Did the page default to cards, an equal grid, or a two-column layout before the claim and
  evidence were understood?
- Could the same structure be reused for a different company without changing its reasoning?
- Is the main object too small because the slide is preserving a habitual layout?
- Is the body area sparse while the title carries too much of the work?
- Does the close look fixed: oversized left text, redundant company/date metadata, or no
  connection to the deck's actual decision?
- Does a value's YoY / delta line touch the value line, making two hierarchy levels read as
  one cramped block?
- Does a bar chart contain only one bar, preventing comparison?
- Does the declared grid/flex strategy fail in the render: misaligned columns, uneven gaps,
  floating rails, or body blocks drifting away from the content field?

## Deck-Level Judgment

Define these before slide writing:

1. Audience: who decides, approves, invests, buys, or acts.
2. Desired action: the specific action after the deck.
3. Governing thought: the one claim the whole deck proves.
4. Chapter spine: how the reader's belief changes from opening to close.
5. Evidence inventory: facts, estimates, assumptions, anecdotes, and open items.
6. Proof rhythm: dense proof pages, quiet resets, transition pages, and decision pages.
7. Design stance: investment-bank / strategy-consulting structure first; modern freshness
   through composition, not decoration.

## Per-Slide Judgment

For every content slide, write these 22 fields in working notes before authoring the final
JSON. The fields are intentionally granular so the slide stays flexible without becoming
loose.

1. **reader_question** — the question this slide answers for the actual reader.
2. **single_takeaway** — the one sentence the reader should remember.
3. **narrative_role** — opens, proves, decomposes, contrasts, transitions, warns, or closes.
4. **evidence_status** — fact / estimate / assumption / anecdote / open for each load-bearing
   proof item.
5. **focal_object** — the chart, value, table row, diagram path, image, or statement carrying
   the page.
6. **evidence_strategy** — why this evidence type is sufficient for the claim.
7. **composition_move** — the visual move selected from `composition-vocabulary.md` or
   `corpus-derived-composition-atoms.md`.
8. **density_control** — what stays on the page, what moves to notes or appendix, and why.
9. **whitespace_role** — whether whitespace separates roles, gives a hero object authority,
   or creates a quiet reset; never leave dead space accidentally.
10. **hierarchy_spine** — the reading order from title to focal object to supporting proof.
11. **grid_role_map** — header, body, proof field, interpretation rail, source/footer, and
    any secondary band.
12. **column_span_plan** — how many grid columns each major object spans and why.
13. **alignment_spine** — the hard left/top/baseline/center line that holds the page together.
14. **body_band_plan** — vertical bands in the body area, including row heights and section
    gaps.
15. **edge_lock** — which objects lock to the same left, right, top, bottom, or center edge.
16. **cross_slide_consistency** — what must stay consistent with neighboring slides and what
    may vary for rhythm.
17. **main_axis** — the flex direction of the main body: row, column, wrap row, or stacked
    bands.
18. **cross_axis_align** — start, center, end, baseline, or stretch, with the reason.
19. **gap_scale** — gap sizes for section gaps, object gaps, and metric-subline gaps.
20. **grow_rule** — what grows when space is available: chart field, table rows, hero value,
    image crop, or interpretation rail.
21. **shrink_guard** — what must not shrink: body text below readability, YoY/delta spacing,
    chart labels, source separation, or legal notes.
22. **wrap_rule** — which text may wrap, the maximum line count, and what to simplify if it
    wraps beyond that.

Then add:

- **annotation_policy** — what is labeled directly and what remains implicit.
- **rhythm_role** — how the slide changes pace relative to the previous and next pages.
- **fill_repair** — how to use accidental dead space without decoration: enlarge proof,
  widen a rail, add a comparative field, or split the slide.
- **failure_mode** — the most likely defect after rendering.
- **repair_instruction** — the first repair to attempt if that defect appears.

## Fact / Estimate / Assumption / Open Discipline

Classify every important number before placing it:

- **fact**: disclosed or verified actual result.
- **estimate**: model output or external estimate with a method and date.
- **assumption**: management plan, target, scenario, or sensitivity driver.
- **anecdote**: case, quote, or example that cannot carry a structural claim alone.
- **open**: needed but not yet supported. Mark it and ask; do not invent.

Different statuses must not look identical. Actuals, forecasts, targets, internal estimates,
and open assumptions need visual or textual separation.

## 2-3 Direction Exploration

Before committing a slide, generate two or three alternatives that differ in focal object,
density, and composition. Examples:

- hero value + facts rail
- comparative table with one highlighted row
- chart with interpretation rail
- driver equation
- current-position gauge
- evidence strip
- asymmetric split contrast

Choose the direction that best answers the reader question with the fewest unsupported
inferences. Do not choose the one that merely matches a familiar slide type.
