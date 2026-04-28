# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A distribution repository that installs **Instructions / Skills / Hooks** as **global** configuration for three LLM CLIs: Claude Code, Codex, and Gemini CLI. It also keeps the canonical repo-local instructions file for GitHub Copilot. Everything is opt-in via `scripts/setup.sh`; the repo never modifies a target machine until that script runs.

This `CLAUDE.md` at the repository root is **the project guide for Claude Code working on this repo**. It is distinct from `instructions/CLAUDE.md`, which is the **thin entrypoint that gets symlinked into `~/.claude/CLAUDE.md`** by `setup.sh`. Do not conflate the two.

## Common commands

```sh
# Full validation (matches CI in .github/workflows/validate.yml)
sh scripts/validate-repo.sh

# Individual unit test files invoked by validate-repo.sh
python3 tests/test_merge_hook_config.py
python3 tests/test_self_workflow.py

# One-shot install (wraps setup.sh; offers package-manager install for trash)
sh scripts/install.sh

# Setup / update / health-check / uninstall (dry-run first when unsure)
AI_AGENT_DRY_RUN=1 sh scripts/setup.sh
AI_AGENT_DRY_RUN=1 sh scripts/uninstall.sh
sh scripts/update.sh
sh scripts/health-check.sh
sh scripts/health-check.sh --json   # masked by default; set AI_AGENT_HEALTH_REDACT=0 for full

# Skill-improvement scan against local LLM CLI logs
python3 scripts/skill-improvement-bot.py scan
```

There is no test runner, no linter, and no package manager. `validate-repo.sh` does: `sh -n` syntax checks for shell scripts, `python3 -m py_compile` for every Python file in `scripts/` and `hooks/scripts/`, an integration smoke run of `health-check.sh --json`, doc-grep assertions on README/setup, the two unit tests above, and a fixture scan for the skill-improvement bot.

## Architecture

### Single source of truth pattern

`instructions/AI_AGENT_INSTRUCTIONS.md` is the canonical instruction set. The per-CLI files (`instructions/CLAUDE.md`, `instructions/AGENTS.md` for Codex, `instructions/GEMINI.md`, and `instructions/.github/copilot-instructions.md`) are **thin entrypoints** that import or point to `AI_AGENT_INSTRUCTIONS.md`, plus `DESIGN.md` (Act design language) and `HOOKS.md` (self-workflow lifecycle) where supported. When updating shared behavior, edit `AI_AGENT_INSTRUCTIONS.md`; only touch entrypoint files when the entrypoint mechanism itself changes.

### Stable-link installation model

`scripts/setup.sh` does not copy files. It creates **symlinks** from each CLI's official global config directory back into this repo:

| CLI | Instructions link | Hook config source (merged into user global) |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` → `instructions/CLAUDE.md` | `hooks/claude/settings.json` → `~/.claude/settings.json` |
| Codex | `~/.codex/AGENTS.md` → `instructions/AGENTS.md` | `hooks/codex/config.toml` + `hooks/codex/hooks.json` → `~/.codex/...` |
| Gemini CLI | `~/.gemini/GEMINI.md` → `instructions/GEMINI.md` | `hooks/gemini/settings.json` → `~/.gemini/settings.json` |

Hook scripts in `hooks/scripts/*.py` are referenced through one indirection — the stable link `${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}` → `<repo>/hooks`. This means CLI hook config can keep an absolute path like `~/.llm-config/hooks/scripts/safe_delete_guard.py` while the underlying repo can move.

GitHub Copilot is intentionally different: the canonical file lives at `instructions/.github/copilot-instructions.md`, but `setup.sh` does not install it globally or manage a repo's `/.github/copilot-instructions.md` for you.

### Existing-config policy

`setup.sh` never overwrites existing `settings.json` / `config.toml`. It uses `scripts/merge-hook-config.py` to **append/merge** managed hook entries from `hooks/<cli>/` into the user global config, with conflicts going to `$AI_AGENT_BACKUP_DIR` (default mode `backup`; `AI_AGENT_CONFLICT_MODE=skip|fail` available). `uninstall.sh` removes only managed links and managed hook entries, and uses `trash` rather than `rm` for any deletion.

### Hook layers

Active hook scripts in `hooks/scripts/`:

| Hook | Default | Trigger |
|---|---|---|
| `safe_delete_guard.py` | **On** | Blocks `rm`-style commands and redirects to `trash` |
| `self_workflow.py` | Registered for Claude/Codex/Gemini managed events | Selectively activates on qualifying tasks |

`self_workflow.py` implements a same-LLM loop driven by completion keywords (`[[SPEC_DONE]]` → spec refinment gate → `[[IMPLEMENTATION_DONE]]` → verification → `[[VERIFICATION_DONE]]` → `[[TASK_DONE]]`) plus structured phase packets. Startup and phase-boundary brief tightening live in the `refinment` Skill. The lifecycle and stop conditions live in `instructions/HOOKS.md`; do not duplicate them elsewhere.

`hooks/scripts/multillm_orchestrator.py` is a **deprecated** script from the removed multi-LLM continuation path. It is not on the main hook flow; do not re-register it without an explicit design decision.

### Skills

Each subdirectory of `skills/` is a self-contained skill that gets symlinked into `$AI_AGENT_SKILLS_DIR` (default `~/.agents/skills`). The repo currently ships:

- `skills/refinment/` — used by `self_workflow.py` for spec/phase brief tightening. `validate-repo.sh` requires `SKILL.md`, `agents/openai.yaml`, `references/research-notes.md`, and `tests/activation-prompts.md`.
- `skills/skill-design-research/` — the always-installed research/design skill. The skill-improvement fixture scan asserts it is present.
- `skills/template/` — structural reference for new skills. **Must keep `SKILL.md.template`, never `SKILL.md`** (validation fails otherwise, since a real `SKILL.md` would install the template as an active skill).

### Editable entrypoints

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AI_AGENT_INSTRUCTIONS.md`, and `.github/copilot-instructions.md` under `instructions/` are now ordinary editable files. They may be changed, moved, or renamed as needed; keep the shared-source-of-truth pattern intact when doing so.

The repo root may also contain `/AGENTS.md`, `/CLAUDE.md`, `/GEMINI.md`, `/.github/copilot-instructions.md` generated by CLI `/init`-style commands. These are **local-only and gitignored**; the canonical files live under `instructions/`.

## Conventions enforced by validation

`scripts/validate-repo.sh` will fail the build if:

- `README.md` or `setup.md` stop mentioning all three CLI names, Copilot scope, the three global config dirs (`~/.codex`, `~/.claude`, `~/.gemini`), or "Hook"
- `README.md` stops referencing `skill-improvement-bot.py`, or `setup.md` stops referencing `schedule-skill-improvement.sh`
- `docs/skill-improvement-automation.md` stops naming the `AI_AGENT_IMPROVEMENT_CREATE_PR` opt-in variable
- The skill-improvement fixture scan no longer detects `skill-design-research` in `tests/fixtures/skill-logs/`
- Any installable `skills/*/SKILL.md` is missing `name:` or `description:` frontmatter
- `skills/template/SKILL.md` exists (the template must stay as `SKILL.md.template`)

When changing user-facing surface area in those files, run `sh scripts/validate-repo.sh` before committing.

## Concurrent-agent caution

Codex and Claude Code instances may both work in this repo from different terminals. Before creating a branch or modifying tracked files, check `git worktree list` and `git status` — if another agent's uncommitted work is in the main checkout, use `git worktree add` to create an isolated workspace rather than switching branches in place.
