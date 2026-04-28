# Repository Guidelines

## Project Structure & Module Organization

This repository distributes shared AI-agent configuration for Claude Code, Codex, and Gemini CLI. Core guidance lives in `instructions/`, with `AI_AGENT_INSTRUCTIONS.md` as the shared source of truth and thin CLI entrypoints beside it. Reusable skills live in `skills/<skill-name>/`, each centered on a `SKILL.md` plus optional `references/`, `tests/`, or `agents/` files. Hook configuration and runtime scripts live in `hooks/`; installer, updater, health-check, and validation utilities live in `scripts/`. Repository tests are in `tests/`, long-form design notes are in `docs/`, and CI workflows are in `.github/workflows/`.

## Build, Test, and Development Commands

- `sh scripts/validate-repo.sh`: run the full repository validation used by CI.
- `python3 tests/test_multillm_orchestrator.py`: run one focused Python test file; replace the filename for other suites.
- `AI_AGENT_DRY_RUN=1 sh scripts/setup.sh`: preview global config links and hook merges without applying changes.
- `sh scripts/health-check.sh`: inspect the installed configuration state.

There is no package-manager build step; most checks are shell syntax, Python syntax, health-check behavior, and direct unit scripts.

## Coding Style & Naming Conventions

Write shell scripts as POSIX `sh` where possible, starting with `set -eu`. Keep Python scripts compatible with Python 3.11 and prefer standard-library code unless a dependency is clearly justified. Use kebab-case for shell scripts such as `schedule-update.sh`, snake_case for Python modules such as `merge_hook_config.py`, and descriptive skill folders such as `refinment`.

## Testing Guidelines

Add or update direct test scripts in `tests/` when changing hook behavior, config merging, prompt refinement, or skill-log scanning. Keep fixture updates under `tests/fixtures/` small and intentional. Before opening a PR, run `sh scripts/validate-repo.sh`; for narrow changes, also run the affected `python3 tests/test_*.py` file while iterating.

## Commit & Pull Request Guidelines

Follow the existing concise, lower-case imperative style, for example `tighten orchestration activation heuristics` or `simplify refinment activation notes`. PR descriptions should state the affected area, behavior change, validation command results, and any setup or migration impact. Include screenshots only when changing generated visual documentation.

## Agent-Specific Instructions

Before contributor or agent work, read `instructions/AI_AGENT_INSTRUCTIONS.md`; also read `instructions/DESIGN.md` for user-facing copy or layout guidance, and `instructions/HOOKS.md` for orchestration changes. For deletion work, use the safer `trash` workflow described in the shared instructions.
