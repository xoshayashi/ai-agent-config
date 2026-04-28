# Self-Workflow Hooks (2026-04)

## Goal

Use Hooks so the current LLM CLI can finish its own work without handing the
main path to another model.

The shared pattern is:

1. the user sends a task to Codex, Claude Code, or Gemini CLI
2. the startup hook injects a specification-first brief
3. the CLI optionally uses `refinment` when the prompt or phase brief really
   needs tightening
4. completion hooks decide whether to stop or auto-continue that **same CLI**
5. the loop ends only after verification evidence is present

## Active Runtime

- Hook script: `hooks/scripts/self_workflow.py`
- Supporting skill: `skills/refinment/`
- State root: `~/.llm-config/self-workflow`
- Shared lifecycle rules: `instructions/HOOKS.md`

This is the current main path. External reviewer subprocesses are not part of
the default flow.

## Event Mapping

| CLI | Startup event | Completion event |
|---|---|---|
| Codex | `UserPromptSubmit` / `SessionStart` | `Stop` |
| Claude Code | `UserPromptSubmit` | `Stop`, `SubagentStop` |
| Gemini CLI | `BeforeAgent` | `AfterAgent` |

The hook injects context on startup and returns a continuation prompt on
completion when more work is needed.

## Phase Flow

1. **Specification authoring**  
   The CLI drafts the spec itself. `refinment` is optional and should stay
   sparse.
2. **Specification review gate**  
   `[[SPEC_DONE]]` or a structured fallback draft moves the task into a tighter
   spec pass.
3. **Implementation**  
   The CLI continues step by step and uses `refinment` only when the next step
   or verification-readiness decision is unclear.
4. **Verification**  
   `[[IMPLEMENTATION_DONE]]` is only a handoff into verification, not final
   completion.
5. **Done**  
   Completion requires `[[VERIFICATION_DONE]]` plus `[[TASK_DONE]]`, or a
   structured `phase_signal="task_complete"` packet with real evidence.

## Safety Design

- recursion guard: `AI_AGENT_SELF_WORKFLOW_ACTIVE=1`
- bounded continuation count and repeated-prompt caps
- bounded verification-turn caps
- session-scoped local state
- fail-open behavior for unsupported or non-qualifying turns

## Design Intent

- keep execution ownership inside the current CLI
- keep prompt tightening visible to the user
- avoid routine cross-LLM reviewer latency
- reuse one lifecycle across Codex, Claude Code, and Gemini CLI

## Related Docs

- Current architecture summary: [hooks-architecture-review.md](./hooks-architecture-review.md)
