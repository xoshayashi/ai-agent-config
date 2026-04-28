# Codex Hub Orchestration (Historical Note)

This file is kept as a migration note only.

The active architecture is no longer a Codex-only multi-LLM orchestration
stack. The current main path is the generic same-LLM self-workflow described
in [self-workflow-hooks.md](./self-workflow-hooks.md).

What changed:

- `multillm_orchestrator.py` was replaced by `self_workflow.py`
- `codex_hook_gate.py` was removed from the active path
- startup and phase-boundary tightening still use `refinment`
- the same lifecycle now applies across Codex, Claude Code, and Gemini CLI

Use this file only when you need historical context for the earlier
Codex-as-hub migration.
