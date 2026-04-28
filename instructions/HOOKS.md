# HOOKS.md

This document defines shared orchestration behavior for Hook-based workflows.

## Multi-LLM Orchestration (Codex Hub)

When Codex receives a qualifying non-trivial task through the managed hook layer,
use this sequence:

1. **Specification loop (pre-implementation)**  
   Codex stays in charge and drafts the specification first. On qualifying tasks, Codex may use the `refinment` Skill once before drafting. When it does, Codex should show the refined prompt to the user in the next visible update, then continue from that refined brief. The initial `UserPromptSubmit` hook injects a spec-authoring brief and waits for Codex to produce a reviewable spec. `[[SPEC_DONE]]` is the primary readiness signal, but structured fallback review may also be used for later drafts when the keyword is missing.
2. **Specification review gate**  
   When Codex emits `[[SPEC_DONE]]`, or when a later draft is reviewable enough for fallback review, the `Stop` hook auto-continues Codex with a prompt that tells it to use the `refinment` Skill. Codex refines the spec itself and either keeps refining or proceeds toward implementation.
3. **Implementation loop**  
   After the refined spec is ready, Codex implements step-by-step. At each material `Stop`, the hook may auto-continue Codex with a prompt that tells it to use `refinment` for a tighter next-step or verification-readiness brief.
4. **Verification loop**  
   `[[IMPLEMENTATION_DONE]]` is not a final stop signal. It means implementation is ready to move into verification. Codex may also use a structured packet with `phase_signal="verification_ready"`. During verification, Codex should use `refinment` when it needs a tighter completion brief before declaring the task done.

Codex remains the execution hub and final action owner.

## Completion Keywords

Use explicit keywords in assistant responses when a phase is complete:

- `[[SPEC_DONE]]` for specification readiness
- `[[IMPLEMENTATION_DONE]]` for implementation handoff into verification
- `[[VERIFICATION_DONE]]` for completed verification and self-review
- `[[TASK_DONE]]` for final end-to-end completion after verification

The orchestrator hook should treat these keywords as **phase transitions, not just raw stop conditions**:

- `[[IMPLEMENTATION_DONE]]` moves the task into verification
- `[[VERIFICATION_DONE]]` marks verification readiness
- only `[[VERIFICATION_DONE]]` together with `[[TASK_DONE]]` should allow final completion
- verification should also have its own bounded turn cap so it cannot continue forever on repeated reviewer guidance

Structured phase packets are also valid when they appear as fenced JSON:

- `{"phase_signal":"verification_ready","summary":"..."}`
- `{"phase_signal":"task_complete","summary":"...","checks_run":["..."],"diff_reviewed":true,"self_review_complete":true}`

The second packet is valid for final completion only when it includes concrete
verification evidence (`checks_run`, `diff_reviewed=true`, and
`self_review_complete=true`).

Keyword detection should be strict. Treat them as valid only when they appear as standalone lines or list items, not when they are merely mentioned inside prose, examples, or documentation.

If `[[SPEC_DONE]]` is absent, the orchestrator should surface that the spec is still in refinement instead of failing silently.

## Safety Limits

Apply these guardrails in hook implementations:

- recursion guard environment flags
- bounded auto-continuation loops and repeated-prompt caps
- local state persistence keyed by session id

## Human-in-the-loop

If a task is high-risk, ambiguous, or changes scope materially, the orchestrator should stop auto-continuation and ask for explicit user direction.
