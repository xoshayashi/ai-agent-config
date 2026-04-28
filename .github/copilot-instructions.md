# GitHub Copilot Instructions

This repository distributes shared AI-agent configuration for Claude Code, Codex, Gemini CLI, and GitHub Copilot CLI.

Before starting work in this repository:

- Read and follow `instructions/AI_AGENT_INSTRUCTIONS.md`
- For user-facing output that touches tone, copy, color, typography, layout, or UI suggestions, also follow `instructions/DESIGN.md`
- For Hook-driven self-workflow behavior and completion keywords, also follow `instructions/HOOKS.md`

If any of these files cannot be read, **ask the user how to proceed before continuing**.

Repository-specific guidance:

- Canonical instructions live in `instructions/`
- Reusable skills live in `skills/`
- Shared hook configs and runtime scripts live in `hooks/`
- Installer, updater, health-check, and validation scripts live in `scripts/`
- Unit tests live in `tests/`
- Validate full changes with `sh scripts/validate-repo.sh`
- When iterating on hook behavior, also run `python3 tests/test_self_workflow.py` or `python3 tests/test_merge_hook_config.py`
- Use `trash` instead of `rm`
