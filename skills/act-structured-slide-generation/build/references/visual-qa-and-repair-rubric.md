# Visual QA and repair rubric

Purpose: corpus-derived review lens for generated slide blueprints, rendered PNGs, or PPTX.
Use after `review-and-repair-rubric.md` when the deck is IR, investor, earnings, or any
evidence-heavy decision material.

Output findings in priority order:

```text
Severity: High / Medium / Low
Slide:
Finding:
Why it matters:
Repair:
Acceptance check:
```

Final verdict:

- **approve**: shippable after normal proofread.
- **repair**: local fixes can pass.
- **redesign**: claim/evidence/composition must be rebuilt.

## 1. Investor Lens

Ask:

- Does the page answer one underwriting question?
- Is the conclusion adjacent to the evidence that proves it?
- Is the page about growth, profitability, risk, progress, capital allocation, or credibility?
- Can a skeptical reader identify what changed and why it matters?

High-severity findings:

- The slide does not change an investment belief.
- The claim is stronger than the evidence.
- Bad news is hidden or reframed without cause and action.

Repair:

- Rewrite the takeaway around the investor question.
- Move strongest evidence to the focal position.
- Add cause, mitigation, or residual risk for negative movement.

Acceptance check:

- A reader can state the investor implication in one sentence without presenter narration.

## 2. IR Owner Lens

Ask:

- Are facts, estimates, assumptions, plans, and open items separated?
- Are definitions, periods, units, denominators, and sources visible where needed?
- Does any title overpromise future results?
- Are proprietary metrics defined at first use?

High-severity findings:

- Forecast/target looks like actual.
- Source or assumption is missing for a material number.
- Adjusted metric is undefined.

Repair:

- Split `source` and `assumption`.
- Restyle forecast/opportunity as pale/dashed and label it.
- Add concise definition footnote and move calculation detail to notes.

Acceptance check:

- A reviewer can point to the evidence state of every material number.

## 3. Designer Lens

Ask:

- Is there one focal object and one hierarchy spine?
- Is whitespace serving emphasis, separation, rhythm, interpretation, or legal readability?
- Does the grid/flex contract show through: role map, alignment spine, gap scale, fill repair?
- Is freshness coming from composition and scale rather than decoration?
- Does the page differ from neighbors without breaking deck system?

High-severity findings:

- Body objects float as small islands or collide.
- Multiple objects compete as protagonist.
- A fixed card/two-column shell repeats without evidence-led reason.

Repair:

- Reassign focal object, increase proof field, mute secondary regions.
- Use section gaps between different roles and metric-subline gaps for value/YoY.
- Change the composition atom if the current atom cannot carry the evidence.

Acceptance check:

- Thumbnail view shows where the eye lands first and why.

## 4. Data Visualization Lens

Ask:

- Does the chart form match the data question?
- Are actual/forecast, basis/variance, amount/rate, and scale/quality separated?
- Are axes, direct labels, units, periods, and annotations sufficient?
- Are comparisons fair and comparable?

High-severity findings:

- Single current-value bar used as if comparison exists.
- Non-comparable bars or axes imply false comparison.
- Axis or missing denominator distorts the story.

Repair:

- Replace single bar with hero number, gauge, range card, or KPI field.
- Align comparison basis, or remove comparison.
- Direct-label the necessary points and disclose denominator/axis break.

Acceptance check:

- The visual can be read correctly without a legend hunt or presenter explanation.

## 5. Legal / Disclaimer Lens

Ask:

- Are forward-looking statements, targets, estimates, external data, trademarks, and
  assumptions handled with appropriate caveats?
- Does the page imply a commitment where only a plan or scenario exists?
- Is legal text readable but not dominating proof pages?

High-severity findings:

- Target, opportunity, or scenario is written as guaranteed outcome.
- Required caveat is absent or buried in body prose.
- Legal/admin page is unreadably compressed.

Repair:

- Add assumption/caveat line and soften promise-like language.
- Move long disclaimer to a dedicated quiet page.
- Preserve line spacing and paragraph grouping for legal text.

Acceptance check:

- A legal/IR reviewer can approve the certainty level without editing the body claim.

## 6. Implementer Lens

Ask:

- Can the slide be rendered in editable 16:9 PPTX without manual coordinates?
- Are text budgets, table columns, image ratios, and gap scales within the engine's capacity?
- Is the repair instruction local and executable?
- Did changes affect only intended slides in render diff?

High-severity findings:

- Design requires hand-edited coordinates or rasterized slides.
- Text only fits by shrinking below token scale.
- Repair instruction says "make it better" without a concrete change.

Repair:

- Pick a supported pattern/atom or add an engine primitive.
- Shorten, group, split, or move detail to notes.
- Express repairs as specific focal/hierarchy/gap/source/content changes.

Acceptance check:

- `validate_spec`, `build_deck`, `verify_deck`, render, and `lint_render` pass; visual diff
  matches intended repairs.

## Severity Guide

- **High**: misleads, cannot be read, cannot be audited, or fails the slide's core purpose.
- **Medium**: readable but weakens trust, hierarchy, comparison, or rhythm.
- **Low**: polish issue with limited decision impact.

## Repair-Or-Redesign Decision

Use **repair** when:

- Reader question and evidence are right.
- The focal object is present but weak.
- Notes/source/gap/hierarchy can be fixed locally.

Use **redesign** when:

- Reader question is wrong or absent.
- Evidence cannot prove the takeaway.
- The composition atom is mismatched to the data shape.
- More than one main claim must remain visible.

Use **approve** only when all lenses have no High findings and no unresolved Medium finding
that affects trust, readability, or implementation.
