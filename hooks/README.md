# Hooks

This directory is the canonical source for shared LLM CLI hooks.

`scripts/setup.sh` installs these hook settings into each supported CLI's
official **global** config directory:

| CLI | Linked Config |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Codex | `~/.codex/config.toml` and `~/.codex/hooks.json` |
| Gemini CLI | `~/.gemini/settings.json` |
| GitHub Copilot CLI | `~/.copilot/settings.json` |

The hook commands call scripts through each CLI's own `hooks/` link:

```text
~/.claude/hooks   -> <this repository>/hooks
~/.codex/hooks    -> <this repository>/hooks
~/.gemini/hooks   -> <this repository>/hooks
~/.copilot/hooks  -> <this repository>/hooks
```

This keeps hook logic version-controlled in this repository while letting each
CLI load hooks from the locations it already expects.

GitHub Copilot CLI is part of this global hook installation path. This
repository manages Copilot's user-level hooks through `~/.copilot/settings.json`
and also tracks `.github/copilot-instructions.md` for this repository's own
repo-level Copilot instructions.

## Installed Hooks

| Hook | Default | Purpose |
|---|---|---|
| `safe_delete_guard.py` | On | Blocks permanent shell deletion commands and tells the agent to use the safer trash workflow. |
| `subprocess_check.py` | Registered / **Always routed on managed events** | Same-CLI advisor: asks the current CLI in non-interactive mode for the next concrete step or `STATUS: complete`. |
| `self_workflow.py` | Compatibility only | Thin shim that forwards old managed hook configs to `subprocess_check.py` until local settings are refreshed. |

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

`subprocess_check.py` is called directly from the managed hook configs for Claude
Code, Codex, Gemini CLI, and GitHub Copilot CLI. The managed hook is always
present, but the Python gate may immediately no-op on unsupported events,
recursive subprocesses, short answer-only turns, or after the per-task cap.

The active Skill path is self-contained. `skills/refinment` may still refine
the working brief inside the current CLI, but the hook itself does not force
any specific Skill.

In same-CLI mode, managed hooks use this flow:

1. Startup event (`UserPromptSubmit`, `SessionStart`, or `BeforeAgent`): ask the same CLI for the smallest first concrete step
2. Stop-style event: skip trivial / answer-only turns, otherwise ask for the next concrete step
3. If the subprocess returns `STATUS: complete` on the first line, mark the task complete and stop continuing
4. Otherwise surface the returned instruction as the continuation prompt

Completion signals and stop conditions are defined in `instructions/HOOKS.md`.
When `subprocess_check.py` auto-continues from a Claude/Codex/Gemini completion
hook, the UI may still label that event as `blocked` or `denied`; this is the
current official continuation mechanism rather than an error.

Key guardrails:

- Re-entry guard via `AI_AGENT_SELF_WORKFLOW_ACTIVE=1`
- Bounded continuation count and repeated-prompt caps
- Verification turn caps
- Session-scoped local state under `~/.ai-agent-config/subprocess-check`
- Fail-open behavior for non-qualifying or unsupported events

## CLI Conventions

Each CLI has its own hook config schema; the values in this directory follow
the per-CLI conventions deliberately.

| CLI | Tool matcher (shell tool) | `timeout` unit |
|---|---|---|
| Claude Code | `Bash` | seconds |
| Codex | `^Bash$` | seconds |
| Gemini CLI | `run_shell_command` | **milliseconds** |

The timeout unit is **not** consistent: Claude/Codex use seconds (e.g. `10` =
10 s) while Gemini uses milliseconds (e.g. `10000` = 10 s). When editing these
files, double-check the unit before changing a `timeout` value to avoid an
accidental 1000× off-by-error.

## Scope

Setup installs one managed hook layer at user scope. Project-level hook
installation by this repository was removed to reduce duplicate execution and
cross-layer conflicts.

When a CLI settings file already exists, setup does not replace it. It appends
or merges the managed Hook entries and prints `append:` so the user can see
which settings file was updated. If the destination is missing, setup uses a
symlink to the managed config file in this repository.

Managed JSON hook groups include `_ai_agent_config_managed: true`.  
`scripts/merge-hook-config.py` uses this explicit marker so user-authored hooks
are less likely to be misclassified.
