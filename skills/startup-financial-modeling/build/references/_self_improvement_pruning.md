# Self-Improvement Pruning Discipline

Use this reference in the classification step before turning a failure into a
durable SFM rule. The menu of possible improvements is not a template: refusing
to add a rule is often the highest-quality action.

## Why This Exists

Self-improvement most often fails by accumulation. Every extra rule consumes
attention, creates new interaction surfaces, and can make future runs slower or
less decisive. SFM therefore accepts only the smallest durable change that
protects a reusable invariant.

## Decision Rules

- Treat "do not reflect" as a valid quality decision.
- Keep n=1 evidence as a deferred candidate unless it has an independently
  verified invariant and a narrow regression proof. For permanent doctrine,
  prefer n>=2 evidence or a failed check plus a holdout/adversarial example.
- Patch the lowest durable layer: runtime/helper for deterministic behavior,
  tests/evals/gates for missing verification, reference protocol for judgment,
  and `SKILL.md` only for trigger or first-step routing.
- Rules fail at the prompt and succeed at the boundary. If a deterministic
  script can prevent the defect, do not rely on prose.
- Prune duplicate guidance. One file is the source of truth; other files point
  to it instead of restating it.
- If the proposal adds always-loaded text, justify why a reference, eval, gate,
  or runtime helper cannot carry it.

## Deferred Candidate Format

When evidence is promising but not durable, record only a one-line sanitized
candidate in the existing progress log if one exists:

```md
- deferred: <generalized issue, no raw logs or source text> | evidence: n=1 |
  stop: <why not reflected> | revisit: <what evidence would promote it>
```

Never create a raw-log archive or a separate changelog just to preserve a
candidate.
