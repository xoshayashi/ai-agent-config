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
| `self_workflow.py` | Registered / **Always routed on managed events, selectively active on qualifying tasks** | Same-LLM self-workflow: the current CLI drafts the spec, uses Skill-driven refinment at task start and phase boundaries, and boundedly auto-continues through implementation and verification. |

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

`self_workflow.py` is called directly from the managed hook configs for Claude
Code, Codex, and Gemini CLI. There is no routine enable flag for the main
self-workflow path now; the managed hook is always present, and
qualifying-task detection decides when the loop actually activates.

This self-workflow mode still has a real latency footprint, but it is lighter
than the earlier design because it does not launch external LLM subprocesses from
the main path.
Even with the managed hook always installed, the runtime should activate only
for heavier design / implementation / review prompts rather than every trivial
turn.
The runtime should make a generic intent split: answer-only turns stay outside
the loop, while artifact/execution turns can enter it when they need bounded
multi-step work.

The active Skill path is self-contained. `skills/refinment` refines the working
brief inside the current CLI instead of shelling out to another model. Keep that Skill
focused on selective use, minimal edits, and visible `Refined prompt:` output
when it changes startup behavior.

`refinment` is invoked through the CLI's native skill-routing path, not as a
separately registered Hook script.

In same-LLM mode, managed hooks use this flow:

1. Startup event (`UserPromptSubmit` or `BeforeAgent`): inject a specification brief and let the current CLI decide whether to use `refinment`
2. If `refinment` is used on the original task prompt, the CLI shows the refined prompt to the user before continuing
3. Completion event after a spec draft is ready enough for review: auto-continue the same CLI with a prompt that tells it to use `refinment`
4. Completion event during implementation: auto-continue the same CLI with a prompt that tells it to use `refinment` for the next-step or verification-ready decision
5. Completion event during verification: auto-continue the same CLI with a prompt that tells it to use `refinment` before declaring completion, and prefer delta-only corrections when only a narrow omission was found

Completion keywords and stop conditions are defined in `instructions/HOOKS.md`.
When `self_workflow.py` auto-continues from a Claude/Codex/Gemini completion
hook, the UI may still label that event as `blocked` or `denied`; this is the
current official continuation mechanism rather than an error.

Key guardrails:

- Re-entry guard via `AI_AGENT_SELF_WORKFLOW_ACTIVE=1`
- Bounded continuation count and repeated-prompt caps
- Verification turn caps
- Session-scoped local state under `~/.llm-config/self-workflow`
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

Managed JSON hook groups include `_llm_config_managed: true`.  
`scripts/merge-hook-config.py` uses this explicit marker first, with a narrow
legacy fallback, so user-authored hooks are less likely to be misclassified.
