# HOOKS.md

This document defines shared self-workflow behavior for Hook-based workflows.

## Hook Event Scope

The shared `self_workflow.py` runs only at *post-work* hook events
(`Stop` / `SubagentStop` / `AfterAgent`). Pre-work events
(`UserPromptSubmit` / `SessionStart` / `BeforeAgent`) are intentionally
unwired so the hook never fires on every prompt — the main session is
capable of starting its own work, and adding a hook on every keystroke
boundary only adds overhead. Phase transitions (`[[SPEC_DONE]]` etc.) are
detected at the post-work boundary instead.

### Idle-phase bootstrap

For brand-new sessions there is no `phase` recorded on disk, so the LLM
explicitly opts into the auto-continuation loop by emitting `[[SPEC_DONE]]`
on a standalone line. When the post-work hook sees that signal on an idle
phase, it records the response as the spec draft, promotes the phase to
`spec_review`, and dispatches the standard refinment gate. Without that
keyword on an idle phase, the hook stays silent — the LLM is free to
answer simple turns without engaging the workflow.

## Same-LLM Self-Workflow

When a managed Hook receives a qualifying non-trivial task, the current CLI
should stay responsible for finishing its own work. The default sequence is:

1. **Specification loop (pre-implementation)**  
   The current CLI drafts the specification itself first. On qualifying tasks, it may use the `refinment` Skill once before drafting. When it does, it should show the refined prompt to the user in the next visible update, then continue from that refined brief. The CLI initializes the spec phase on its own (no startup hook fires); `[[SPEC_DONE]]` on the standalone line of the response is the primary readiness signal, and the post-work hook picks up that signal at the next `Stop` boundary. Structured fallback review may also be used for later drafts when the keyword is missing.
2. **Specification review gate**  
   When the current CLI emits `[[SPEC_DONE]]`, or when a later draft is reviewable enough for fallback review, the completion hook auto-continues that same CLI with a prompt that tells it to use the `refinment` Skill. The CLI refines the spec itself and either keeps refining or proceeds toward implementation.
3. **Implementation loop**  
   After the refined spec is ready, the same CLI implements step-by-step. At each material completion boundary, the hook may auto-continue it with a prompt that tells it to use `refinment` for a tighter next-step or verification-readiness brief.
4. **Verification loop**  
   `[[IMPLEMENTATION_DONE]]` is not a final stop signal. It means implementation is ready to move into verification. The CLI may also use a structured packet with `phase_signal="verification_ready"`. During verification, it should use `refinment` when it needs a tighter completion brief before declaring the task done.

The managed loop should use a generic intent split:

- **answer-only turns** stay outside the loop by default
- **artifact / execution turns** can enter the loop when they need bounded
  multi-step work

Do not promote simple "what is the difference" or "explain this" prompts into
spec -> implementation -> verification work unless they also ask for a concrete
change or deliverable.

If a self-workflow phase is already active, any non-follow-up user turn that
does not continue the current loop and does not start a new qualifying task
should clear the active loop state before the next stop boundary. This prevents
stale auto-continuation after interruptions, acknowledgements, or answer-only
detours.

This workflow is generic across Codex, Claude Code, and Gemini CLI. No
external peer reviewer is part of the main path.

## Completion Keywords

Use explicit keywords in assistant responses when a phase is complete:

- `[[SPEC_DONE]]` for specification readiness
- `[[IMPLEMENTATION_DONE]]` for implementation handoff into verification
- `[[VERIFICATION_DONE]]` for completed verification and self-review
- `[[TASK_DONE]]` for final end-to-end completion after verification

The self-workflow hook should treat these keywords as **phase transitions, not just raw stop conditions**:

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

If `[[SPEC_DONE]]` is absent, the hook should surface that the spec is still in refinement instead of failing silently.

When verification discovers only a narrow omission or factual correction,
prefer a delta-only follow-up instead of repeating the whole earlier answer.
Use correction-like signals for that branch; do not treat generic "updated"
status text as delta-only by itself.

## Safety Limits

Apply these guardrails in hook implementations:

- recursion guard environment flags
- bounded auto-continuation loops and repeated-prompt caps
- local state persistence keyed by session id

## Human-in-the-loop

If a task is high-risk, ambiguous, or changes scope materially, the hook should stop auto-continuation and ask for explicit user direction.
