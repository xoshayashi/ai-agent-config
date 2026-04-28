# HOOKS.md

This document defines shared self-workflow behavior for Hook-based workflows.

## Same-LLM Self-Workflow

The self-workflow Hook is **opt-in and advisory**. It does not push any specific
skill on the CLI, and it does not force a spec-first lifecycle on every
non-trivial task. The CLI is responsible for deciding whether and when to draft
a specification, run verification, or invoke any helper skill (such as
`refinment`). The hook's role is limited to:

- detecting completion keywords in CLI output and tracking phase state
- providing minimal advisory context when a phase is already active
- enforcing safety limits (recursion guard, continuation caps, verification cap)

The available phases (specification authoring, specification review,
implementation, verification, done) form a **convention**, not a mandatory
ladder. A CLI may skip phases entirely, complete a task in one turn without
emitting any keyword, or use only the keywords it actually finds useful.

When the CLI does choose to use the workflow:

1. **Specification phase (optional).** The CLI may draft a specification when
   the task benefits from one. `[[SPEC_DONE]]` marks specification readiness.
   If a structured draft (real headings, scope/acceptance/risks/constraints/
   implementation sections, sufficient body) appears without the keyword, the
   hook may treat it as a fallback review candidate.
2. **Specification revision (optional).** After `[[SPEC_DONE]]` the hook hands
   the draft back for one revision pass. The CLI revises the spec itself; the
   hook does not instruct it to use any particular skill.
3. **Implementation.** The CLI implements step by step. Whether it splits the
   work, uses skills, or asks the user is up to the CLI.
4. **Verification.** `[[IMPLEMENTATION_DONE]]` is a handoff into verification,
   not a final stop signal. Verification ends with `[[VERIFICATION_DONE]]` plus
   `[[TASK_DONE]]`, or with a structured `phase_signal="task_complete"` packet
   that carries real evidence (`checks_run`, `diff_reviewed=true`,
   `self_review_complete=true`).

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
external peer reviewer is part of the main path. Skill activation (refinment,
brainstorming, debugging, and so on) is decided by each skill's own activation
conditions, not by hook-injected instructions.

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

## Minimal Completion Signal

Emit completion signals minimally. The hook needs only one valid signal per
phase transition; redundant signals add visual noise without changing detection.

- Prefer a single completion keyword on its own line at the end of the response.
- Use a structured JSON packet **only** when the hook needs the structured
  evidence — for example, the final `task_complete` packet that carries
  `checks_run`, `diff_reviewed`, and `self_review_complete`.
- Do not emit both a keyword and an equivalent JSON packet for the same
  transition. Pick the one form the moment actually requires.
- Keep the user-facing report and the completion signal visually separated:
  put the report first, then a blank line, then the signal as the final line.
- Do not wrap the signal inside emphasis, headings, or other formatting that
  could break the standalone-line / fenced-JSON detection rule above.

## Safety Limits

Apply these guardrails in hook implementations:

- recursion guard environment flags
- bounded auto-continuation loops and repeated-prompt caps
- local state persistence keyed by session id

## Human-in-the-loop

If a task is high-risk, ambiguous, or changes scope materially, the hook should stop auto-continuation and ask for explicit user direction.
