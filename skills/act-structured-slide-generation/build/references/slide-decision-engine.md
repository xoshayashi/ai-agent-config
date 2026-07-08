# Slide decision engine

Purpose: the corpus-derived decision flow for turning source material into slide blueprints.
Use this before writing `deck.json`. It keeps the skill a judgment engine instead of a
slide-type template catalog.

Core flow:

`source understanding -> reader_question -> single_takeaway -> focal_object -> evidence_strategy -> composition_move -> density_control -> visual QA -> repair`

## 1. Source Understanding

Before slide planning, classify every input item:

- **fact**: externally or internally verifiable statement supplied in the materials.
- **estimate**: calculated or researched estimate; needs method and source.
- **assumption**: management plan, scenario, or internal basis.
- **anecdote**: one example, customer, quote, image, or project.
- **open**: missing or unverified item; keep as `[open]` or `[to verify]`.

Do not build a proof slide around open data. If the claim cannot be supported, insert a
research step or make the uncertainty visible.

## 2. Deck-Level Decisions

Set these before slide bodies:

- **audience_question_sequence**: the order of doubts the deck must answer.
- **governing_thought**: the deck's one claim.
- **trust_threshold**: what evidence this audience needs before accepting the claim.
- **density_rhythm**: where the deck is dense, quiet, comparative, or conclusive.
- **evidence_mix**: which pages rely on numbers, tables, diagrams, images, notes, or quotes.

## 3. Per-Slide Minimum Vocabulary

Every slide blueprint must include these fields, even if the final `deck.json` maps them to
existing spec fields:

- **reader_question**: the question this page answers.
- **single_takeaway**: the one conclusion the reader should remember.
- **focal_object**: the first visual object the eye should land on.
- **evidence_strategy**: how the takeaway is proven and what evidence status it has.
- **composition_move**: the body composition atom or combination chosen.
- **information_architecture**: how information is split and ordered.
- **density_control**: why the page is sparse, medium, dense, or appendix-like.
- **whitespace_role**: emphasis, separation, interpretation space, rhythm reset, or legal.
- **hierarchy_spine**: the primary reading path or alignment spine.
- **annotation_policy**: what goes in body, source, assumption, note, or speaker notes.
- **rhythm_role**: proof, transition, current-location, rest, appendix, or close.
- **failure_mode**: the most likely way this page will break.
- **repair_instruction**: the first local repair to try.

## 4. Evidence-To-Composition Decision Tree

Choose by the claim and evidence, not by a slide label.

- **Change over time** -> trend chart, period band, latest highlight, event annotations.
- **Composition or mix** -> stacked components, direct labels, protagonist segment.
- **Progress vs target** -> current-position gauge or comparable progress bars; never a
  single current-value bar.
- **Financial accountability** -> protagonist-column table, actual/plan/prior basis, source
  and definitions outside the body.
- **Cause of change** -> waterfall, driver equation, factor cards, or variance table.
- **Business mechanism** -> labeled flow, system map, driver tree, or real-object panel.
- **Opportunity whitespace** -> coverage matrix with actual vs potential state separation.
- **External context** -> concept/evidence split or vertical cause flow landing on company
  action.
- **Credibility proof** -> evidence strip, image-proof panel, quote with source, third-party
  citation.
- **Navigation/rhythm** -> current-location agenda, section reset, quiet conclusion.
- **Legal/admin** -> dedicated quiet text page or concise source/assumption line.

If two branches seem equally right, create 2-3 visual directions and select the one that proves
the `single_takeaway` with the least reader effort.

## 5. Blueprint Output

Before `deck.json`, write slide blueprints in this shape:

```text
Slide N: [action title]
reader_question:
single_takeaway:
focal_object:
evidence_strategy:
composition_move:
information_architecture:
density_control:
whitespace_role:
hierarchy_spine:
annotation_policy:
rhythm_role:
on_slide_text:
speaker_notes:
assumptions_or_open_items:
QA_gate:
repair_if_failed:
```

Then map the blueprint into the closest `deck-spec.md` implementation primitive. If the
primitive cannot express the blueprint without shrinking text, overloading the body, or
inventing layout overrides, change the blueprint or add an engine primitive in a separate
implementation pass.

## 6. Pre-Render QA Gates

Reject or repair the blueprint before building if any gate fails:

- The `reader_question` is not answerable from visible evidence.
- The `single_takeaway` contains a number or period not shown in the exhibit.
- The `focal_object` is not the strongest evidence.
- The `composition_move` was chosen because of slide type rather than evidence.
- The page has no `whitespace_role`.
- Actuals, forecasts, assumptions, and opportunities are visually indistinguishable.
- Notes, definitions, and caveats are mixed into the body instead of source/assumption/notes.
- The expected failure mode has no local repair instruction.

## 7. Post-Render Repair Logic

Use local repairs before redesign:

- **Unclear protagonist**: enlarge or recolor the proof object; mute peers.
- **Crowded body**: delete, group, or split; never shrink below token scale.
- **Weak trust**: add source, assumption, definition, or proof image.
- **Chart scan cost**: direct-label, reduce series, align periods, remove redundant axes.
- **Diagram ambiguity**: label relation types and highlight one path.
- **Misleading future state**: restyle as forecast/assumption/opportunity.
- **Dead slide**: if it does not change a decision, delete or move to appendix.

## 8. Mapping To Existing References

- Composition atom details: `corpus-derived-composition-atoms.md`
- Core design principles: `ir-slide-design-principles.md`
- Grid/flex contract: `grid-and-flex-strategy.md`
- Claims and trust: `evidence-and-claim-rules.md`
- Chart/diagram/image choice: `data-and-diagram-rules.md`
- Review and repair: `visual-qa-and-repair-rubric.md`, `review-and-repair-rubric.md`,
  `anti-patterns.md`

## 9. Continuous Corpus Updates

When a new IR-slide abstraction corpus is added, do not paste all new observations into the
skill. First classify each candidate insight:

- **existing_rule_support**: supports an existing rule; do not add unless it changes a
  condition or repair.
- **existing_rule_refinement**: improves when to use, when not to use, parameters, failure, or
  repair for an existing principle or atom.
- **new_composition_atom**: adds a genuinely new composition move that transfers across
  companies, categories, and evidence types.
- **anti_pattern**: improves failure detection or repair.
- **ignore**: company-specific, duplicate, visual-surface-only, or low-transfer noise.

Add only refinements that satisfy all gates:

- use case is clear
- non-use case is clear
- adjustable parameters exist
- failure mode and repair are explicit
- rule works beyond one company or one original slide
- it does not turn the skill into a fixed slide-type taxonomy

If a candidate fails these gates, leave it out and keep the skill lean.
