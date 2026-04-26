# Peer CLI Routing

Use these command patterns when `peer-prompt-refinement` needs another LLM to improve the current prompt.

## Routing Matrix

| Current Agent | Peer LLM CLI | Non-Interactive Pattern |
|---|---|---|
| Codex | Gemini CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini --skip-trust --approval-mode plan --output-format text -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task."` |
| Claude Code | Gemini CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini --skip-trust --approval-mode plan --output-format text -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task."` |
| Gemini CLI | Codex CLI | `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 codex exec --cd "$PWD" --sandbox read-only --ask-for-approval never -` |

## Safe Transfer Pattern

Prefer stdin or a quoted here-doc so user text is not interpreted by the shell or exposed as a long command-line argument.

For Gemini CLI:

```sh
cat <<'_PEER_REFINEMENT_CONTEXT_' | AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 gemini \
  --skip-trust \
  --approval-mode plan \
  --output-format text \
  -p "Improve the task prompt using the Context Packet from stdin. Do not perform the task."
<peer prompt with Context Packet>
_PEER_REFINEMENT_CONTEXT_
```

For very large Context Packets, write the packet to a safe temporary file and redirect stdin from that file instead of placing the packet in command arguments.

For Codex CLI:

```sh
AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1 codex exec \
  --cd "$PWD" \
  --sandbox read-only \
  --ask-for-approval never \
  - <<'_PEER_REFINEMENT_CONTEXT_'
<peer prompt with Context Packet>
_PEER_REFINEMENT_CONTEXT_
```

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
- If Gemini reports workspace trust issues for a prompt-only refinement, retry once with `--skip-trust`.
- If the peer output lacks an improved prompt or drops important constraints, use the original prompt plus your own missing-consideration checklist.
- Report fallback briefly only when it affects confidence, latency, or user expectations.

## Notes

- Gemini CLI help on this machine identifies `-p` / `--prompt` as non-interactive headless mode, supports `--output-format text|json`, and accepts stdin as extra prompt context.
- Codex CLI help on this machine identifies `codex exec` as non-interactive execution and supports stdin with `-`, `--sandbox read-only`, and `--ask-for-approval never`.
- Claude Code help on this machine identifies `-p` / `--print` as non-interactive output; this skill's required route still sends Claude Code prompts to Gemini.
