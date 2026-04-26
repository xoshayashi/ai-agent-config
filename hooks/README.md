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
${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks} -> <this repository>/hooks
```

This keeps hook logic version-controlled in this repository while letting each
CLI load hooks from the locations it already expects.

## Installed Hooks

| Hook | Default | Purpose |
|---|---|---|
| `safe_delete_guard.py` | On | Blocks permanent shell deletion commands and tells the agent to use the safer trash workflow. |

`peer_prompt_refinement.py` remains in `hooks/scripts/` for advanced
customization, but it is not wired into default hook configs. This keeps
day-to-day latency and complexity low.

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

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
