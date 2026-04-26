# Hooks

This directory is the canonical source for shared LLM CLI hooks.

`scripts/setup.sh` links these files into each supported CLI's official
project-level config directory by default:

| CLI | Linked Config |
|---|---|
| Claude Code | `.claude/settings.json` |
| Codex | `.codex/config.toml` and `.codex/hooks.json` |
| Gemini CLI | `.gemini/settings.json` |

The hook commands call scripts through the stable link:

```text
${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks} -> <this repository>/hooks
```

This keeps hook logic version-controlled in this repository while letting each
CLI load hooks from the locations it already expects.

## Installed Hooks

| Hook | Default | Purpose |
|---|---|---|
| `peer_prompt_refinement.py` | Off | Optional preflight prompt review by a peer LLM CLI. Enable with `AI_AGENT_HOOKS_ENABLE_PROMPT_REFINEMENT=1`. |
| `safe_delete_guard.py` | On | Blocks permanent shell deletion commands and tells the agent to use the safer trash workflow. |

The safe-delete Hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if a CLI disables hooks or a hook runtime is unavailable.

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

By default setup installs project-level hook config under `AI_AGENT_TARGET_DIR`.
Use `AI_AGENT_HOOKS_SCOPE=user` to link into user-level CLI config folders, or
`AI_AGENT_HOOKS_SCOPE=both` to install both.

When a CLI settings file already exists, setup does not replace it. It appends
or merges the managed Hook entries and prints `append:` so the user can see
which personal settings file was updated. If the destination is missing, setup
uses a symlink to the managed config file in this repository.

User-level scope can affect existing personal settings, so setup explains this
before the real run and dry-run output should be reviewed first.
