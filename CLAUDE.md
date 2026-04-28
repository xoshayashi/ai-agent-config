# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A distribution repository that installs **Instructions / Skills / Hooks** as **global** configuration for three LLM CLIs: Claude Code, Codex, and Gemini CLI. Everything is opt-in via `scripts/setup.sh`; the repo never modifies a target machine until that script runs.

## Common commands

```sh
# Full validation (matches CI in .github/workflows/validate.yml)
sh scripts/validate-repo.sh

# Individual unit test files
python3 tests/test_merge_hook_config.py
python3 tests/test_response_strategy_bridge.py
python3 tests/test_refinment.py
python3 tests/test_multillm_orchestrator.py

# Setup / update / health-check / uninstall, dry-run first
AI_AGENT_DRY_RUN=1 sh scripts/setup.sh
AI_AGENT_DRY_RUN=1 sh scripts/uninstall.sh
sh scripts/health-check.sh
sh scripts/health-check.sh --json   # masked by default; set AI_AGENT_HEALTH_REDACT=0 for full

# Skill-improvement scan against local LLM CLI logs
python3 scripts/skill-improvement-bot.py scan
```

There is no test runner, no linter, and no package manager. `validate-repo.sh` does: `sh -n` syntax checks for shell scripts, `python3 -m py_compile` for Python, doc-grep assertions on README/setup, the four unit tests above, and a fixture scan for the skill-improvement bot.

## Architecture

### Single source of truth pattern

`instructions/AI_AGENT_INSTRUCTIONS.md` is the canonical instruction set. The per-CLI files (`instructions/CLAUDE.md`, `instructions/AGENTS.md` for Codex, `instructions/GEMINI.md`) are **thin entrypoints** that `@`-import or point to `AI_AGENT_INSTRUCTIONS.md`, plus `DESIGN.md` (Act design language) and `HOOKS.md` (orchestration lifecycle). When updating shared behavior, edit `AI_AGENT_INSTRUCTIONS.md`; only touch entrypoint files when the entrypoint mechanism itself changes.

### Stable-link installation model

`scripts/setup.sh` does not copy files. It creates **symlinks** from each CLI's official global config directory back into this repo:

| CLI | Instructions link | Hook config link |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` → `instructions/CLAUDE.md` | `~/.claude/settings.json` (merged) |
| Codex | `~/.codex/AGENTS.md` → `instructions/AGENTS.md` | `~/.codex/config.toml` + `~/.codex/hooks.json` (merged) |
| Gemini CLI | `~/.gemini/GEMINI.md` → `instructions/GEMINI.md` | `~/.gemini/settings.json` (merged) |

Hook scripts in `hooks/scripts/*.py` are referenced through one indirection — the stable link `${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}` → `<repo>/hooks`. This means CLI hook config can keep an absolute path like `~/.llm-config/hooks/scripts/safe_delete_guard.py` while the underlying repo can move.

### Existing-config policy

`setup.sh` never overwrites existing `settings.json` / `config.toml`. It uses `scripts/merge-hook-config.py` to **append/merge** managed hook entries, with conflicts going to `$AI_AGENT_BACKUP_DIR` (default mode `backup`; `AI_AGENT_CONFLICT_MODE=skip|fail` available). `uninstall.sh` removes only managed links and managed hook entries, and uses `trash` rather than `rm` for any deletion.

### Hook layers

Three hook scripts in `hooks/scripts/`, each with a different default:

| Hook | Default | Trigger |
|---|---|---|
| `safe_delete_guard.py` | **On** | Blocks `rm`-style commands and redirects to `trash` |
| `multillm_orchestrator.py` | Registered, **always routed for Codex** | Selectively activates on qualifying tasks |
| `response_strategy_bridge.py` | Registered, **off** | `AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY=1` |

The orchestrator implements a Codex-as-hub loop driven by completion keywords (`[[SPEC_DONE]]` → spec refinment gate → `[[IMPLEMENTATION_DONE]]` → verification → `[[VERIFICATION_DONE]]` → `[[TASK_DONE]]`) plus structured phase packets. Startup and phase-boundary brief tightening live in the self-contained `refinment` Skill. The lifecycle and stop conditions live in `instructions/HOOKS.md`; do not duplicate them elsewhere.

### Skills

Each subdirectory of `skills/` is a self-contained skill that gets symlinked into `$AI_AGENT_SKILLS_DIR` (default `~/.agents/skills`). The `template/` skill is the structural reference for new skills.

### Editable-but-protected entrypoints

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AI_AGENT_INSTRUCTIONS.md`, and `.github/copilot-instructions.md` carry the macOS ACL `everyone deny delete` after setup (`AI_AGENT_PROTECT_LINKS=auto`). Files can be edited freely, but moving or renaming them locally requires removing the ACL first and reapplying it at the new path.

## Conventions enforced by validation

`scripts/validate-repo.sh` will fail the build if:

- `README.md` or `setup.md` stop mentioning all three CLI names, the three global config dirs (`~/.codex`, `~/.claude`, `~/.gemini`), or "Hook"
- `README.md` stops referencing `skill-improvement-bot.py`, or `setup.md` stops referencing `schedule-skill-improvement.sh`
- `docs/skill-improvement-automation.md` stops naming the `AI_AGENT_IMPROVEMENT_CREATE_PR` opt-in variable
- The skill-improvement fixture scan no longer detects `skill-design-research` in `tests/fixtures/skill-logs/`

When changing user-facing surface area in those files, run `sh scripts/validate-repo.sh` before committing.

## Concurrent-agent caution

Codex and Claude Code instances may both work in this repo from different terminals. Before creating a branch or modifying tracked files, check `git worktree list` and `git status` — if another agent's uncommitted work is in the main checkout, use `git worktree add` to create an isolated workspace rather than switching branches in place.
