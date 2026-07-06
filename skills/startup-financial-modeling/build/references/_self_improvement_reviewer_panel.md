# Self-Improvement Reviewer Panel

Use this reference only after a proposed Reflection Record already passes
`validate_reflection_record`. The validator is the privacy, shape, and overfit
gate; this panel is the semantic-quality gate. Both must pass before a durable
skill change is accepted.

## Why This Exists

A record can be private-safe, schema-complete, and still make the skill worse:
it may add a vague rule, optimize a single proxy, weaken verification discipline,
or turn one artifact quirk into permanent process. The panel catches that class
of failure by scoring whether the proposed change really improves reusable SFM
quality.

## Independence

The writer of the Reflection Record does not score it. Use an independent
reviewer, subagent, or deterministic panel function. The reviewer must cite the
record evidence it relies on; impression scores without citations are not admissible.

## Four Lenses

Score each lens on four anchored levels. Use the score as an additional
acceptance signal, never as a replacement for the validator.

| Lens | Max | Level 4 | Level 3 | Level 2 | Level 1 |
| --- | ---: | --- | --- | --- | --- |
| R1 correctness and doctrine compliance | 25 | Preserves strict audit, privacy, source discipline, regression proof, human-review triggers, and git-managed changes | Minor wording risk but no doctrine weakening | Ambiguous interaction with audit/privacy/source discipline | Weakens or bypasses an existing hard gate |
| R2 verification depth and honesty | 35 | Cites failed evidence, fixed evidence, regression proof, and one broader gate; admits residual limits | Has a concrete targeted check and broader gate but limited adversarial coverage | Relies mostly on manual review or indirect evidence | Subjective proof, missing broader gate, or claims more than evidence supports |
| R3 generality and design health | 20 | Names a reusable invariant, has n>=2 evidence or an explicit deferred disposition, and patches the lowest durable layer | Reusable invariant is plausible but evidence is thin | Mostly incident-shaped or patches too high in the stack | n=1 preference made permanent or one-off local issue generalized |
| R4 artifact quality and readability | 20 | Improves the workbook/memo/audit workflow with a small, readable change at the right layer | Improves quality but adds some complexity | Adds process weight with unclear artifact benefit | Bloats always-loaded instructions or obscures the original workflow |

Accept only if total score is at least 80/100, every lens meets its floor, and
there are no blockers. R2 has the largest weight because SFM quality depends on
honest proof: a plausible rule without a failing check, a repaired check, and a
broader rerun is not a durable improvement.

## Bias Controls

- Suppress sycophancy: do not raise a score because the proposal sounds aligned
  with a user preference; ask which artifact failure it prevents next time.
- Suppress self-preference: the author may summarize evidence but may not grade
  acceptance.
- Suppress Goodharting: do not accept a change because it improves one eval while
  privacy, audit, source discipline, or artifact quality get thinner.
- Keep citations local and sanitized: cite command names, check IDs, eval IDs,
  or redacted evidence summaries, not raw logs or confidential source text.

## Runtime Hook

`build/runtime/self_improvement.py` owns the deterministic guardrail:
`score_reflection_panel(record)` and
`validate_reflection_record_for_acceptance(record)`. The deterministic function
does not replace human or subagent review for high-risk doctrine/privacy/audit
changes; it gives the skill a repeatable floor for common Reflection Records.
