# Hooks

This directory is the canonical source for shared LLM CLI hooks.

`scripts/setup.sh` installs these hook settings into each supported CLI's
official **global** config directory:

| CLI | Linked Config |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Codex | `~/.codex/config.toml` and `~/.codex/hooks.json` |
| Gemini CLI | `~/.gemini/settings.json` |

The hook commands call scripts through the stable link:

```text
${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.ai-agent-config/hooks} -> <this repository>/hooks
```

This keeps hook logic version-controlled in this repository while letting each
CLI load hooks from the locations it already expects.

## Installed Hooks

| Hook | Default | Purpose |
|---|---|---|
| `safe_delete_guard.py` | On | Blocks permanent shell deletion commands and tells the agent to use the safer trash workflow. |

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

This repository intentionally keeps the managed Hook layer minimal. Hooks are
for deterministic safety and policy checks, not for prompt bootstrapping,
phase machines, or auto-continuation.

Prompt tightening and multi-step task execution belong in the main session.
When a task brief genuinely needs clarification, the current CLI can use
`skills/refinment` through its native skill path instead of waiting for a Hook
to inject or route work.

During setup or update, `scripts/merge-hook-config.py` also removes stale
managed legacy Hook entries when the source configs no longer declare them.
That cleanup path is what retires older orchestration-era registrations from
existing user settings.

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
accidental 1000x off-by-error.

## Scope

Setup installs one managed Hook layer at user scope. Project-level hook
installation by this repository was removed to reduce duplicate execution and
cross-layer conflicts.

When a CLI settings file already exists, setup does not replace it. It appends
or merges the managed Hook entries and prints `append:` so the user can see
which settings file was updated. If the destination is missing, setup uses a
symlink to the managed config file in this repository.

Managed JSON hook groups include `_ai_agent_config_managed: true`.
`scripts/merge-hook-config.py` uses this explicit marker first, with a narrow
match policy, so user-authored hooks are less likely to be misclassified.
