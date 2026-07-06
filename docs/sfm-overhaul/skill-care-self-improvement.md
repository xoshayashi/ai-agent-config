# SFM Self-Improvement Import From Skill-Care

This note records the clean-base import of the four skill-care self-improvement
specs into `skills/startup-financial-modeling`. It is a scope table, not a
runtime instruction source; the skill sources of truth are the referenced
SFM files below.

## Source Constraint

The requested local source path
`/Users/shunsuke_hayashi/Documents/internal_audit/skills/internal_audit_skill_care/`
was not present on this machine. Google Drive search did not surface an
`internal_audit_skill_care` folder. The implementation therefore uses the
attached prompt's extracted four-spec contract as the source requirements and
maps those specs into SFM's existing self-improvement architecture without
weakening existing gates.

## Import Map

| Skill-care spec | SFM reflection target | Regression proof |
| --- | --- | --- |
| Independent reviewer panel for semantic quality | `build/references/_self_improvement_reviewer_panel.md`; runtime hooks `score_reflection_panel` and `validate_reflection_record_for_acceptance` in `build/runtime/self_improvement.py`; closeout pointer in `_self_improvement_protocol.md`; eval `self_improvement_panel_rejects_schema_valid_degradation` | `test_self_improvement_panel_rejects_schema_valid_quality_degradation`; `quality_gates.py` G-K fixture where `validate_reflection_record` passes but panel rejects |
| Convergence condition and independent closeout consistency check | `_self_improvement_protocol.md` closeout step; deterministic script `build/runtime/closeout_consistency.py`; eval `self_improvement_closeout_consistency_drift` | `test_self_improvement_closeout_consistency_catches_links_and_count_drift`; `quality_gates.py` G-K dangling-ref and count-drift fixture |
| Failure-mode mitigations | `build/references/_self_improvement_failure_modes.md`; linked from `_self_improvement_protocol.md`; eval `self_improvement_failure_modes_mitigated`; rubric checks in `emit-startup-finance-rubric.js` | `test_self_improvement_failure_modes_and_pruning_are_linked_from_gates`; domain rubric `session-log-self-improvement` criterion |
| Pruning discipline: menu, not template | `build/references/_self_improvement_pruning.md`; classification step in `_self_improvement_protocol.md`; panel R3 n=1 blocker; eval `self_improvement_pruning_deferred_candidate` | `test_self_improvement_panel_rejects_schema_valid_quality_degradation`; `test_self_improvement_failure_modes_and_pruning_are_linked_from_gates` |

## Existing Strengths Preserved

- `validate_reflection_record` remains the first gate; the reviewer panel is
  additive and cannot replace privacy/schema/overfit validation.
- Secret, PII, raw-log, X-handle/status URL, company-specific, and
  instance-shaped lessons remain rejected in `build/runtime/self_improvement.py`.
- `regression_proof` remains required for reusable records; the panel makes weak
  subjective proof a blocker rather than a fallback.
- Audit/privacy/doctrine changes still require `milestone_review`; the panel
  adds another review signal, not a bypass.
- The branch is git-managed and isolated from unrelated ACT/milestone-review
  dirty files in the original checkout.

## Closeout Evidence To Keep Current

- `python3 /Users/sh/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/startup-financial-modeling`
- `python3 -m json.tool skills/startup-financial-modeling/build/evals/evals.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest skills/startup-financial-modeling/build/tests -p no:cacheprovider -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 skills/startup-financial-modeling/build/evals/quality_gates.py`
- `node skills/startup-financial-modeling/build/evals/startup-finance-rubric/emit-startup-finance-rubric.js skills/startup-financial-modeling`
- `plugin-eval analyze skills/startup-financial-modeling --format markdown`
