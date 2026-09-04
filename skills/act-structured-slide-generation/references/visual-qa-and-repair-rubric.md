# Visual QA and repair rubric

Purpose: the render-based review and repair loop for every deck (SKILL.md §4). Run it after
`lint_render` and before the independent rubric loop, on the rendered PNGs and `deck.json`
together. Investor-heavy lenses weigh more on IR / earnings decks, but every lens is asked of
every substantive slide. Severity uses the same P0 / P1 / P2 scale as SKILL.md and
`review-log.md`.

Output findings in priority order:

```text
Severity: P0 / P1 / P2
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

P0 findings:

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

P0 findings:

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

P0 findings:

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

P0 findings:

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

P0 findings:

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

P0 findings:

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

## 7. Narrative And Strategy Lens

Ask:

- What strategic belief, priority, or decision does this slide move? Is it more than a neutral
  fact introduction?
- What role does the slide play in the deck's argument? Does it bridge from the previous page
  and set up the next one?
- Could the slide be shuffled elsewhere in the deck without anyone noticing?

P0 findings:

- The slide moves no belief and asks for no decision.
- The title read-through breaks at this slide (the claim does not follow from the previous one).

Repair:

- Rewrite the takeaway around the decision it should move, or fold the slide into its neighbour.
- Fix the bridge in the title sequence first, then in the `speaker_notes`.

Acceptance check:

- Reading only the action titles, the argument still runs through this slide.

## Severity Guide

- **P0**: factual contradiction, unreadable proof, overlap, cut-off text, impossible source,
  broken render, or a slide that fails its core purpose.
- **P1**: grid/flex breach, weak evidence, title mismatch, excessive whitespace, cramped
  hierarchy, single-bar chart, fixed closing page — readable but weakens trust, hierarchy,
  comparison, or rhythm.
- **P2**: polish, minor rhythm, small alignment drift, or optional copy tightening.

Repair in severity order (P0 -> P1 -> P2) and record every finding in `review-log.md`.

## Repair Menu

- **R1. Rewrite title**: use when the slide has a topic title or claim/evidence mismatch.
- **R2. Split slide**: use when two claims or protagonists compete.
- **R3. Strengthen evidence**: add source, denominator, period, or better proof.
- **R4. Change composition move**: switch from cards/two-column/equal grid to a move that
  matches the evidence.
- **R5. Enlarge focal object**: scale chart/table/value/image before adding decoration.
- **R6. Rebuild grid/flex**: redefine role map, spans, alignment spine, bands, and gaps.
- **R7. Repair density**: move excess detail to notes/appendix or fill dead space with larger
  proof objects.
- **R8. Repair metric spacing**: separate value, unit, and YoY/delta subline.
- **R9. Replace single-bar chart**: use comparison, gauge, range, hero number, or table row.
- **R10. Rebalance close**: choose thesis, proof strip, decision request, next actions, quote,
  or legal close.
- **R11. Normalize color**: reduce accent, remove decoration, stabilize meaning.
- **R12. Fix source discipline**: separate source, assumption, note, and legal caveat.
- **R13. Fix production defect**: overflow, cropping, font substitution, broken render.
- **R14. Return to outline**: use when the chapter spine, governing thought, or evidence base
  is wrong.

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

Use **approve** only when all lenses have no P0 findings and no unresolved P1 finding
that affects trust, readability, or implementation. The scoring gate (`evals/rubric.json`,
at least 95 after independent judging) is a separate, later step: a beautiful deck with
unsupported claims still fails it.
