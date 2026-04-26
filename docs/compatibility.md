# LLM CLI Compatibility

Use this document when reviewing shared instructions, setup flows, skills, or agent workflows that should work across Claude Code, Codex, and Gemini CLI.

## Source Of Truth

The machine-readable compatibility matrix is:

```text
compatibility/llm-cli-matrix.yml
```

## Review Rules

- **Portable first:** Shared instructions should be written in natural language and should avoid tool-specific commands unless the fallback is clear.
- **Entry points stay thin:** `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` should keep pointing to `AI_AGENT_INSTRUCTIONS.md`.
- **Tag tool-specific behavior:** If a rule only works in one LLM CLI, label it with the relevant compatibility tag in the PR or nearby documentation.
- **Natural-language setup must remain complete:** A beginner should be able to paste the setup request into a supported LLM CLI and continue through GitHub login, checkout or pull, dry-run preview, setup, update scheduling, verification, health check, and urgent update.
- **Skills need activation checks:** New or updated skills should include should-trigger and should-not-trigger prompts, either in the skill references or in `skills/template/tests/activation-prompts.md` when starting from the template.

## Validation

Run the repository validation script before opening or updating a pull request:

```sh
sh scripts/validate-repo.sh
```

This checks shell syntax, required setup documents, compatibility metadata, skill template safety, installable skill frontmatter, and whether the natural-language setup still names Claude Code, Codex, and Gemini CLI.

## Compatibility Tags

| Tag | Meaning |
|---|---|
| `portable` | Expected to work across Claude Code, Codex, and Gemini CLI. |
| `claude-code-only` | Uses Claude Code-specific behavior. |
| `codex-only` | Uses Codex-specific behavior. |
| `gemini-cli-only` | Uses Gemini CLI-specific behavior. |
| `unknown` | Compatibility has not been verified. Treat as a review blocker for shared instructions. |

## Reviewer Checklist

1. Does the change alter an entrypoint file, setup flow, skill activation text, or shared instruction?
2. If yes, does `compatibility/llm-cli-matrix.yml` still describe the behavior accurately?
3. Does a non-technical user still have a natural-language path through the workflow?
4. Are tool-specific commands clearly marked and paired with a fallback?
5. Were dry-run, uninstall, or recovery paths affected?
6. Did `scripts/validate-repo.sh` pass?
7. If `compatibility/llm-cli-matrix.yml` changed, was its `updated` field reviewed and bumped when appropriate?
