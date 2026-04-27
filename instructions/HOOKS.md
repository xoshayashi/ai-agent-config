# HOOKS.md

This document defines shared orchestration behavior for Hook-based workflows.

## Multi-LLM Orchestration (Codex Hub)

When `AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=1`, use this sequence:

1. **Specification loop (pre-implementation)**  
   Codex stays in charge and drafts the specification first. The initial `UserPromptSubmit` hook only injects a spec-authoring brief and waits for Codex to produce a reviewable spec. `[[SPEC_DONE]]` is the primary readiness signal, but structured fallback review may also be used for later drafts when the keyword is missing.
2. **Specification review gate**  
   When Codex emits `[[SPEC_DONE]]`, the `Stop` hook sends that draft to Claude for review. Claude either approves it for implementation or sends one more spec-refinement prompt back to Codex.
3. **Implementation loop**  
   After Claude approves the spec, Codex implements step-by-step. At each `Stop`, Claude may provide the next implementation prompt.
4. **Verification loop**  
   `[[IMPLEMENTATION_DONE]]` is not a final stop signal. It means implementation is ready to move into verification. Codex must run validation, inspect the diff, and self-review before the task can finish.
5. **Periodic review loop**  
   Gemini periodically critiques simplification opportunities and possible spec drift, and that note is fed into Claude's implementation guidance.

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

Keyword detection should be strict. Treat them as valid only when they appear as standalone lines or list items, not when they are merely mentioned inside prose, examples, or documentation.

If `[[SPEC_DONE]]` is absent, the orchestrator should surface that the spec is still in refinement instead of failing silently.

## Safety Limits

Apply these guardrails in hook implementations:

- recursion guard environment flags
- bounded timeout per peer CLI call
- fail-open behavior when peer CLIs are unavailable or outputs are invalid
- local state persistence keyed by session id

## Human-in-the-loop

If a task is high-risk, ambiguous, or changes scope materially, the orchestrator should stop auto-continuation and ask for explicit user direction.
