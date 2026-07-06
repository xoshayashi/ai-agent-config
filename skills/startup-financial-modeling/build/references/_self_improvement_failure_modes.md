# Self-Improvement Failure Modes

Use this reference when a session-log or post-output improvement looks reusable
and the Reflection Record validator has no privacy or overfit findings. The
purpose is to prevent the improvement process itself from quietly degrading SFM.

## Model Collapse

Do not let synthetic examples dilute human or artifact-derived failures. A
generated scenario may stress a rule, but the anchor must remain a real user
workflow, a real failed check, a real workbook/memo defect, or a clearly stated
holdout/adversarial eval. If the only evidence is synthetic, keep the item as a
deferred candidate rather than making it doctrine.

Linked gates: `validate_reflection_record` rejects raw logs, private text, and
company-specific overfit; `score_reflection_panel` requires cited evidence and a
quality effect before acceptance.

## Reward Hacking / Goodhart

Do not optimize a single proxy. A rule that makes one eval pass while weakening
strict audit, privacy, source discipline, or rendered workbook quality is a
regression. Periodically sample accepted Reflection Records against the hard
gates: privacy findings, audit/human-review flags, regression proof, and a
broader closeout gate must still be meaningful.

Linked gates: `quality_gates.py` runs the self-improvement validator and panel
cases; evals include self-improvement scenarios but do not supersede workbook
strict-audit gates.

## Sycophancy

User feedback can reveal a real defect, but the durable rule must be grounded in
artifact evidence and SFM doctrine, not in pleasing the latest phrasing. If the
user preference conflicts with auditability, source discipline, or financial
truthfulness, keep the artifact fix local and do not promote the preference.

Linked gates: the reviewer panel requires independent scoring and cited
evidence; the writer is not the reviewer.

## Eval Overfit

Passing fewer than ten self-improvement evals or examples is not enough to call
a behavior generic. A small regression test can protect a known failure, but it
does not prove the broader workflow. For broad claims, pair the targeted proof
with a broader gate such as `quality_gates.py`, the pytest suite, plugin-eval,
or a holdout/adversarial example not tuned during the same iteration.

Linked gates: Reflection Records must name regression proof; panel R2 requires a
broader gate to rerun.

## Non-Convergence

If each iteration only adds process while scores or artifact quality plateau,
stop. Closure is justified by one of three conditions: the target score/gate is
met, no new reusable gap appears, or the iteration bound is reached and the
remaining issue is recorded as deferred. Continuing to add rules after
saturation is itself a quality failure.

Linked gates: pruning discipline owns deferred candidates; closeout consistency
checks catch dangling references, count drift, and process bloat before merge.
