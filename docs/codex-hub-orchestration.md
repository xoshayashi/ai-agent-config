# Codex Hub Orchestration (No Ollama)

## Goal

Implement a Codex-centered autonomous workflow where:

1. Initial prompt enters Codex
2. Codex Hook runs Claude -> Gemini -> Claude specification loop
3. Codex executes implementation steps
4. Claude guides next implementation prompts at stop points
5. Gemini periodically critiques simplification/spec drift

## Why Codex as Hub

- Single execution owner reduces loop races and split-brain state
- Hook decisions stay localized to one CLI event stream
- Status and stop conditions are easier to audit

## Hook Wiring

Codex events:

- `SessionStart` -> orchestration state resume
- `UserPromptSubmit` -> spec loop bootstrap
- `Stop` -> continuation decision

Hook script:

- `hooks/scripts/multillm_orchestrator.py`

Default is enabled. Disable only when needed:

```sh
export AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=0
```

## Completion And Stop Rules

Defined in `instructions/HOOKS.md`:

- `[[SPEC_DONE]]`
- `[[IMPLEMENTATION_DONE]]`
- `[[TASK_DONE]]`

The orchestrator treats `[[IMPLEMENTATION_DONE]]` or `[[TASK_DONE]]` as stop conditions.

## Safety Design

- Fail-open when peer CLI unavailable or output invalid
- Recursion guards (`AI_AGENT_ORCHESTRATOR_ACTIVE`)
- Bounded timeout/output size for peer calls
- Continuation loop caps (`AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK`, `AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT`)
- Session-scoped local state (`~/.llm-config/orchestration`)
- Draft spec phase keeps implementation blocked until spec is marked done

## References

- Codex hooks: <https://developers.openai.com/codex/hooks>
- Claude hooks: <https://code.claude.com/docs/en/hooks>
- Gemini CLI hooks reference: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/hooks/reference.md>
