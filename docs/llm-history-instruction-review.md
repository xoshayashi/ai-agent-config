# LLM History Instruction Review

Use `$daily-llm-history-instruction-review` as an on-demand maintenance skill
when recent Claude Code, Codex, or Gemini CLI history shows repeated friction.
Do not run it on a standing schedule by default.

## Review Goal

The review should reduce future user steering. When the history shows repeated
prompts such as "continue", "status?", "restart?", "verify this", or "finish the
PR", treat those prompts as evidence that the agent should have managed more of
the workflow itself.

Do not turn those prompts into narrow trigger-response rules. Translate them
into durable agent behavior, such as:

- leaving compact checkpoints before long or fragile work
- resuming from memory, artifacts, git state, PR state, and recent tool results
- reporting current state and next action before waiting
- verifying before claiming completion
- carrying explicit closeout requests through commit, PR, review, merge, and
  cleanup when that scope is already clear

## Run Shape

Open the repository in Codex and ask for a bounded review with the skill:

```text
Use the `$daily-llm-history-instruction-review` skill.

Review recent Claude Code, Codex, and Gemini CLI history. If a repeated pattern
is worth encoding, update the shared instructions and matching skill/docs. Focus
on how the agent should behave so that the user's repeated steering prompts
become less necessary.
```

If repository changes are made, use the normal branch, commit, PR, review, and
merge closeout requested by the user for that run.

## Checks

After edits, run:

```sh
AI_AGENT_CONFIG_HOME="${AI_AGENT_CONFIG_HOME:-$PWD}" AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh
sh scripts/validate-repo.sh
git diff --check
```
