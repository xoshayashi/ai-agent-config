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
| `multillm_orchestrator.py` | Registered / **Always routed for Codex, selectively active on qualifying tasks** | Codex-centered orchestration: Codex-first spec authoring, Skill-driven refinment at task start and phase boundaries, and bounded auto-continuation through implementation and verification. |
| `response_strategy_bridge.py` | Registered / **Legacy opt-in** | At response-finalization events (`Stop` / `AfterAgent`), optionally asks a peer LLM for one more-turn strategy. This is no longer part of the main Codex hub flow. |

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

`multillm_orchestrator.py` is routed through
`hooks/scripts/codex_hook_gate.py`. There is no routine enable flag for Codex
hub orchestration now; the managed hook is always present, and
qualifying-task detection decides when the orchestration loop actually
activates.

This orchestration mode still has a real latency footprint, but it is lighter
than the earlier design because it does not launch external LLM subprocesses from
the main Codex path.
Even with the managed hook always installed, the runtime should activate only
for heavier design / implementation / review prompts rather than every trivial
turn.

The active Skill path is self-contained. `skills/refinment` refines the working
brief inside Codex instead of shelling out to Claude or Gemini. Keep that Skill
focused on selective use, minimal edits, and visible `Refined prompt:` output
when it changes startup behavior.

In skill-driven mode, Codex hooks use this flow:

1. `UserPromptSubmit`: inject a Codex-first specification brief and let Codex decide whether to use `refinment`
2. If `refinment` is used on the original task prompt, Codex shows the refined prompt to the user before continuing
3. `Stop` after a spec draft is ready enough for review: auto-continue Codex with a prompt that tells it to use `refinment`
4. `Stop` during implementation: auto-continue Codex with a prompt that tells it to use `refinment` for the next-step or verification-ready decision
5. `Stop` during verification: auto-continue Codex with a prompt that tells it to use `refinment` before declaring completion

Completion keywords and stop conditions are defined in `instructions/HOOKS.md`.
The Codex `Stop` hook now stays entirely on the orchestrator path, so
`response_strategy_bridge.py` no longer competes with the main Codex hub flow.
The Codex `Stop` configuration is routed through a single managed hook so the
UI shows one post-response hook status line instead of separate orchestration
and response-strategy entries.
When the orchestrator auto-continues from a Codex `Stop` hook, Codex's UI may
still label that event as `blocked`; this is Codex's current official
continuation mechanism rather than an orchestration error.

The reusable `refinment.py` script remains in this repository as a
hook-compatible helper, but the active Codex hub path relies on the
installable `refinment` Skill rather than on hook-level external LLM calls.

`response_strategy_bridge.py` is still available for legacy non-Codex flows and
remains inert unless explicitly enabled:

```sh
export AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY=1
```

When disabled, it returns `{}` immediately and does not alter turn flow.
When enabled, the default routing is:

- Claude Code / Codex -> Gemini CLI reviewer
- Gemini CLI -> Codex reviewer

You can override with:

```sh
export AI_AGENT_RESPONSE_STRATEGY_PROVIDER=gemini   # or codex / ollama
export AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL=qwen2.5:latest
```

For `ollama`, set `AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL`; otherwise the
hook fail-opens and skips external review.

Key guardrails:

- Re-entry guard via `AI_AGENT_RESPONSE_STRATEGY_ACTIVE=1` in subprocess calls
- Skip when `stop_hook_active=true` unless `AI_AGENT_RESPONSE_STRATEGY_ALLOW_REENTRY=1`
- Minimum response-length threshold (`AI_AGENT_RESPONSE_STRATEGY_MIN_RESPONSE_CHARS`, default `120`)
- Timeout and output caps (`AI_AGENT_RESPONSE_STRATEGY_TIMEOUT_SECONDS`, `AI_AGENT_RESPONSE_STRATEGY_OUTPUT_CHARS`)
- Optional redacted transcript context window for better review quality

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
