# HOOKS.md

This document defines the shared Hook policy for this repository.

## Design Principle

Hooks are thin, deterministic guardrails. They are **not** the main workflow
engine.

The main session should own specification, implementation, verification, and
self-review. If a task needs a tighter brief, use `refinment` inside that same
session instead of relying on a Hook to inject prompts, manage phases, or
auto-continue work.

## What Hooks Are For

- actions that must run every time with clear pass/fail behavior
- lightweight safety or policy checks around tool use
- small, fast checks that should behave the same across Codex, Claude Code, and Gemini CLI

## What Hooks Are Not For

- prompt bootstrapping on every task
- phase state machines or auto-continuation loops
- completion keywords or hidden task routing
- routine peer-LLM orchestration

If a behavior is slow, stateful, model-dependent, or only useful sometimes, it
should usually live in shared instructions, a Skill, or the main session flow
instead of a managed Hook.

## Current Managed Hooks

The default shared install keeps one managed runtime guardrail:

- `safe_delete_guard.py`
  Blocks permanent shell deletion commands and tells the agent to use the safer
  `trash` workflow instead.

## Implementation Rules

- keep Hooks fast and quiet by default
- fail open unless the Hook is an explicit safety gate
- prefer one user-global managed layer over duplicated project/user installs
- merge only managed Hook entries during setup/update
- remove stale managed legacy Hook entries when the source config no longer declares them

## CLI Scope

- Codex: `PreToolUse` shell-command guard
- Claude Code: `PreToolUse` shell-command guard
- Gemini CLI: `BeforeTool` shell-command guard

No shared completion keywords are required.
