# Peer CLI Routing

Use these command patterns when `peer-prompt-refinement` needs another LLM to improve the current prompt.

## Routing Matrix

| Current Agent | Peer LLM CLI | Non-Interactive Pattern |
|---|---|---|
| Codex | Gemini CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini --skip-trust --approval-mode plan --output-format text -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task. Do not use tools; return text only."` |
| Claude Code | Gemini CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini --skip-trust --approval-mode plan --output-format text -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task. Do not use tools; return text only."` |
| Gemini CLI | Codex CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 codex exec --cd "$PWD" --sandbox read-only -` |

## Safe Transfer Pattern

Prefer stdin or a quoted here-doc so user text is not interpreted by the shell or exposed as a long command-line argument.

Use a caller-enforced timeout for peer calls. Recommended default: `PEER_REFINEMENT_TIMEOUT_SECONDS=45`. If a local timeout wrapper is unavailable, the coordinating agent should enforce the same deadline through its tool/session timeout and fall back to the original prompt when the deadline fires.

Optional portable timeout wrapper for Unix-like systems:

```sh
peer_refinement_timeout() {
  perl -e 'alarm shift @ARGV; exec @ARGV' "${PEER_REFINEMENT_TIMEOUT_SECONDS:-45}" "$@"
}
```

This wrapper assumes `perl` is available. If it is not, use `timeout`, `gtimeout`, or the coordinating agent's own tool/session timeout with the same deadline.

For Gemini CLI:

```sh
cat <<'_PEER_REFINEMENT_CONTEXT_' | peer_refinement_timeout env AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini \
  --skip-trust \
  --approval-mode plan \
  --output-format text \
  -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task. Do not use tools; return text only."
<peer prompt with Context Packet>
_PEER_REFINEMENT_CONTEXT_
```

For very large Context Packets, write the packet to a safe temporary file and redirect stdin from that file instead of placing the packet in command arguments.

For Codex CLI:

```sh
peer_refinement_timeout env AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 codex exec \
  --cd "$PWD" \
  --sandbox read-only \
  - <<'_PEER_REFINEMENT_CONTEXT_'
<peer prompt with Context Packet>
_PEER_REFINEMENT_CONTEXT_
```

`--approval-mode plan` is intentional for Gemini because this peer step should be read-only and text-only. Do not use `yolo` or auto-edit modes for prompt refinement. If Gemini still attempts a tool action, waits for approval, or prints a plan instead of the required sections, treat the output as unusable and fall back. `--skip-trust` is also intentionally included because local `gemini --help` identifies it as the session-level workspace trust bypass.

## Context Packet Rules

- Include relevant conversation context, not only the latest user sentence.
- Summarize older context instead of copying long history.
- Include in-progress state from the current work session when it affects the next action.
- Include durable constraints and negative constraints explicitly.
- Include target repository, branch, files, services, and output format when known.
- Include likely skill candidates when obvious, but ask the peer to treat them as suggestions.
- Preserve exact technical entities such as file paths, branch names, command names, function names, error codes, PR numbers, and quoted constraints.
- Exclude secrets, credentials, tokens, unrelated personal data, and unrelated private project details.

## Fallbacks

- If the peer CLI is missing, unauthenticated, rate-limited, or blocked by workspace trust, continue with the original prompt.
- If the peer CLI exceeds the timeout budget or blocks on approval, stop waiting and continue with the original prompt.
- If Gemini reports workspace trust issues for a prompt-only refinement, retry once with `--skip-trust`.
- If peer output is present but missing one or more required sections, salvage only safe missing-consideration hints from the sections present and treat the missing sections as if the peer returned only chatter.
- If the peer output lacks an improved prompt, misses required sections, drops important constraints, or returns only chatter/tool plans, use the original prompt plus your own missing-consideration checklist.
- Report fallback briefly only when it affects confidence, latency, or user expectations.

## Notes

- Gemini CLI help on this machine identifies `-p` / `--prompt` as non-interactive headless mode, supports `--skip-trust`, `--output-format text|json|stream-json`, accepts stdin as extra prompt context, and supports `--approval-mode plan` as read-only mode.
- Codex CLI help on this machine identifies `codex exec` as non-interactive execution and supports stdin with `-`, `--cd` / `-C`, and `--sandbox read-only`. Current `codex exec --help` does not list `--ask-for-approval`; use read-only sandboxing, the text-only peer prompt, and the timeout fallback instead.
- Claude Code help on this machine identifies `-p` / `--print` as non-interactive output; this skill's required route still sends Claude Code prompts to Gemini.
