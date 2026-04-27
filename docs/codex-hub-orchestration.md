# Codex Hub Orchestration (No Ollama)

## Goal

Implement a Codex-centered autonomous workflow where:

1. Initial prompt enters Codex
2. Codex drafts the specification itself first
3. Claude reviews and finalizes that spec at the stop boundary
4. Codex executes implementation steps
5. Claude guides next implementation prompts at stop points
6. Gemini periodically critiques simplification/spec drift

## Why Codex as Hub

- Single execution owner reduces loop races and split-brain state
- Hook decisions stay localized to one CLI event stream
- Status and stop conditions are easier to audit
- Heavy peer calls are concentrated at review boundaries instead of every prompt submission

## Hook Wiring

Codex events:

- `SessionStart` -> orchestration state resume
- `UserPromptSubmit` -> spec loop bootstrap
- `Stop` -> continuation decision

Hook script:

- `hooks/scripts/multillm_orchestrator.py`

Default is disabled. Enable only when needed:

```sh
export AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=1
```

## Lifecycle

With orchestration enabled, the default flow is:

1. `UserPromptSubmit`: inject a spec-authoring brief into Codex
2. `Stop` while spec is incomplete: do nothing special
3. `Stop` when Codex emits `[[SPEC_DONE]]`: ask Claude to review the spec
4. If Claude says the spec is still draft, continue Codex with one more refinement prompt
5. If Claude approves the spec, continue Codex into implementation
6. During implementation, Claude suggests the next step and Gemini periodically critiques simplification or spec drift

## Completion And Stop Rules

Defined in `instructions/HOOKS.md`:

- `[[SPEC_DONE]]`
- `[[IMPLEMENTATION_DONE]]`
- `[[TASK_DONE]]`

The orchestrator treats `[[IMPLEMENTATION_DONE]]` or `[[TASK_DONE]]` as stop conditions.

## Safety Design

- No peer spec loop on raw prompt submission; Codex authors the first draft directly
- Fail-open when peer CLI unavailable or output invalid
- Recursion guards (`AI_AGENT_ORCHESTRATOR_ACTIVE`)
- Bounded timeout/output size for peer calls
- Continuation loop caps (`AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK`, `AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT`)
- Session-scoped local state (`~/.llm-config/orchestration`)
- Draft spec phase keeps implementation blocked until Claude review marks it done

## References

- Codex hooks: <https://developers.openai.com/codex/hooks>
- Claude hooks: <https://code.claude.com/docs/en/hooks>
- Gemini CLI hooks reference: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/hooks/reference.md>
