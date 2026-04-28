# Codex Hub Orchestration (No Ollama)

## Goal

Implement a Codex-centered autonomous workflow where:

1. Initial prompt enters Codex
2. Codex drafts the specification itself first
3. Codex uses self-contained `refinment` to tighten that spec at the stop boundary
4. Codex executes implementation steps
5. Codex uses self-contained `refinment` again when the next-step or completion brief is unclear

## Why Codex as Hub

- Single execution owner reduces loop races and split-brain state
- Hook decisions stay localized to one CLI event stream
- Status and stop conditions are easier to audit
- Startup and phase-boundary refinment stay inside Codex instead of launching reviewer subprocesses

## Hook Wiring

Codex events:

- `SessionStart` -> orchestration state resume
- `UserPromptSubmit` -> spec loop bootstrap
- `Stop` -> continuation decision

Hook script:

- `hooks/scripts/codex_hook_gate.py`
- `hooks/scripts/multillm_orchestrator.py`

The managed Codex hook is always routed through this path. There is no routine
feature flag for Codex orchestration now; qualifying-task detection decides
whether the loop activates.

Even with the managed hook always present, orchestration should not claim every prompt. The practical
activation surface is:

- explicit design / specification / review / automation asks
- long or multi-part implementation requests
- prompts with repository/file-context plus action verbs

Light chat, thanks, and simple status prompts should pass through without
starting the orchestration loop.

## Lifecycle

With skill-driven orchestration, the default flow is:

1. `UserPromptSubmit`: inject a spec-authoring brief into Codex and let Codex decide whether to use `refinment`
2. If `refinment` is used on the original task prompt, Codex shows the refined prompt to the user before continuing
3. `Stop` while spec is incomplete: save the draft and ask Codex to keep refining
4. `Stop` when Codex emits `[[SPEC_DONE]]`, or when a later draft is structured enough to qualify for fallback review: auto-continue Codex with a prompt that tells it to use `refinment`
5. If the refined spec is still draft, continue Codex with one more refinement prompt
6. If the refined spec is ready, continue Codex into implementation
7. During implementation, the continuation prompt tells Codex to use `refinment` for the next-step or verification-ready decision
8. When implementation is ready, Codex can emit `[[IMPLEMENTATION_DONE]]` or a structured packet with `phase_signal="verification_ready"` to enter verification
9. Verification continues under the same Skill-driven refinment pattern until explicit completion keywords or a structured `phase_signal="task_complete"` packet with checks, diff review, and self-review evidence is present

## Completion And Stop Rules

Defined in `instructions/HOOKS.md`:

- `[[SPEC_DONE]]`
- `[[IMPLEMENTATION_DONE]]`
- `[[VERIFICATION_DONE]]`
- `[[TASK_DONE]]`

The orchestrator also accepts structured phase packets inside fenced JSON:

- `{"phase_signal":"verification_ready","summary":"..."}`
- `{"phase_signal":"task_complete","summary":"...","checks_run":["..."],"diff_reviewed":true,"self_review_complete":true}`

## Safety Design

- No external-review loop on raw prompt submission; Codex authors the first draft directly
- Qualifying prompt refinment is optional and Skill-driven
- Recursion guards (`AI_AGENT_ORCHESTRATOR_ACTIVE`)
- Continuation loop caps (`AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK`, `AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT`)
- Hook routing is always on for Codex; qualifying-task detection decides whether orchestration activates
- Session-scoped local state (`~/.llm-config/orchestration`)
- Draft spec phase keeps implementation blocked by policy and injected guidance, not by a hard phase lock on tools

## References

- Codex hooks: <https://developers.openai.com/codex/hooks>
- Claude hooks: <https://code.claude.com/docs/en/hooks>
- Gemini CLI hooks reference: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/hooks/reference.md>
