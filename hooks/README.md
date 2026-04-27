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
| `multillm_orchestrator.py` | Registered / **On by default (Codex)** | Codex-centered orchestration: Claude+Gemini spec loop on prompt submit, then Claude-guided implementation continuation on stop. |
| `peer_prompt_refinement.py` | Registered / **Off by default** | At prompt-submission events (`UserPromptSubmit` / `BeforeAgent`), optionally asks a peer LLM to refine the incoming prompt context before work begins. |
| `response_strategy_bridge.py` | Registered / **Off by default** | At response-finalization events (`Stop` / `AfterAgent`), optionally asks a peer LLM for one more-turn strategy and can trigger an automatic continuation. |

The safe-delete hook is a runtime guardrail, not the only safety layer. The
shared instructions still require agents to use the safer trash workflow even
if hooks are disabled or unavailable.

`multillm_orchestrator.py` is wired in Codex hook settings and is enabled by
default. Disable only when needed:

```sh
export AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=0
```

This default-on mode has a real cost/latency footprint. On each Codex
`UserPromptSubmit`, it can make up to 3 peer CLI/API calls
(`Claude -> Gemini -> Claude`), and on each `Stop` it can make an additional
continuation-decision call. Keep it enabled only when you want that behavior.

With this enabled, Codex hooks use this flow:

1. `UserPromptSubmit`: Claude -> Gemini -> Claude specification loop
2. `Stop`: Claude continuation guidance for Codex implementation
3. Every N implementation turns, Gemini critique is injected into the Claude guidance step

Completion keywords and stop conditions are defined in `instructions/HOOKS.md`.
When orchestration mode is enabled, prompt-refinement and response-strategy hooks
for Codex are automatically bypassed by command guards to avoid conflicting
continuation decisions.

`peer_prompt_refinement.py` is wired into hook settings but remains inert
unless explicitly enabled:

```sh
export AI_AGENT_HOOKS_ENABLE_PROMPT_REFINEMENT=1
```

Prompt-refinement default routing is:

- Codex -> Claude Code
- Claude Code -> Codex
- Gemini CLI -> Claude Code

Override provider when needed:

```sh
export AI_AGENT_PROMPT_REFINEMENT_PROVIDER=claude  # or gemini / codex
```

`response_strategy_bridge.py` is wired into hook settings but remains inert
unless explicitly enabled:

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
hook fail-opens and skips peer review.

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
