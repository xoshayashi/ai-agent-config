# Argument Closure And Deck Logic

Use this contract before visual layout. It turns a brief into a complete decision argument at slide level and deck level.

## Governing Decision

Freeze one audience, one decision, one governing thesis, one decision horizon, and one completion condition. Write them in `deck_argument_plan`. Every slide advances the same decision by resolving one named question.

## Slide Argument Unit

Register every slide as one closed reasoning unit:

1. `question`: the precise question the page resolves.
2. `claim`: one answer-first proposition expressed by the action title.
3. `evidence`: the minimum sufficient facts, estimates, assumptions, or observations that establish the claim.
4. `warrant`: the causal or comparative rule that explains why the evidence supports the claim.
5. `implication`: the consequence for the governing decision.
6. `action_or_transition`: the decision, action, or next question produced by the page.
7. `owner`, `timing`, and `success_measure`: the accountable role, decision horizon, and observable result carried forward by the page.

Bind each field to visible exhibit elements or speaker-note evidence. The title, body, and takeaway express the same proposition at different levels of detail. A reader can reconstruct the reasoning without adding an unstated premise.

## Deck Argument Chain

Build the deck as an ordered dependency graph rather than a topic list. Each slide declares:

- `inputs_from_prior`: prior conclusions used as premises
- `new_contribution`: the new conclusion established here
- `outputs_to_next`: the premise handed to the next slide
- `decision_impact`: how the governing decision changes

The first slide frames the decision and governing thesis. Intermediate slides establish the problem, mechanism, evidence, choice, economics or feasibility, operating model, and risks in the order required by the brief. The final slide converts the accumulated conclusions into explicit decisions, owners, timing, and success measures.

Approve the chain when every load-bearing conclusion has an originating slide, every originating slide is used downstream, and every transition can be read as “therefore” or “to establish this, next.” Parallel slides use an explicit synthesis page or synthesis region before the deck advances.

## Counterargument And Boundary Coverage

For each decision-critical claim, record the strongest plausible alternative, the boundary where the claim holds, and the evidence that distinguishes the selected path. Express the distinction on-slide when it changes the decision; retain supporting detail in speaker notes when it protects rigor without improving the visual argument.

Use `closure_matrix` with rows for claim, evidence, warrant, implication, alternative, boundary, owner, timing, and success measure. Mark every required cell `resolved`, `explicit_assumption`, or `open_with_owner_and_due_date`. This preserves a complete line of reasoning while keeping uncertainty visible and actionable.

Bind resolved owner, timing, and success-measure rows to the corresponding explicit values in `slide_argument_plan`. Pair every `open_with_owner_and_due_date` row with a matching `open_items` entry containing its text, owner, and due date; keep both lists empty when the page is fully resolved.

## Copy And Exhibit Fit

Select one exhibit grammar that proves the claim directly. Every visible object has one argumentative role: premise, evidence, relationship, contrast, implication, or action. Labels state what the object means; values state how much; connectors state how conclusions follow. The takeaway completes the implication rather than introducing a second proposition.

## Approval Gates

Apply `argument_closure_lock` before layout and again at contact-sheet review:

- slide question, claim, evidence, warrant, implication, and action/transition: 100% registered
- load-bearing claim coverage: 100%
- evidence-to-claim binding: 100%
- unstated decision-critical premise count: 0
- unused load-bearing slide conclusion count: 0
- unresolved contradiction count: 0
- open decision-critical item coverage by owner and due date: 100%
- adjacent-slide transition coverage: 100%
- final decision/action coverage by owner, timing, and success measure: 100%

Repair by strengthening the missing field, merging redundant pages, splitting overloaded reasoning, moving a prerequisite earlier, or adding an explicit synthesis step. Preserve the governing decision and evidence classification throughout the repair.
