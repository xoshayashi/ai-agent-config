---
name: daily-llm-history-instruction-review
description: "Review recent Claude Code, Codex, and Gemini CLI interaction history, identify repeated user-agent inefficiencies, and update shared instruction files only when a durable improvement is clear. Use for the ai-agent-config daily instruction review, especially from Codex App Automations."
---

# Daily LLM History Instruction Review

## Purpose

Run a bounded review of recent Claude Code, Codex, and Gemini CLI activity for the
`ai-agent-config` repository. The goal is to improve shared instructions only
when recent history shows a repeated, durable pattern that is worth encoding.

This skill is intended for Codex App Automations. Keep the output concise and
safe because it may run unattended.

## Repository And Scope

- Repository: `/Users/sh/Documents/ai-agent-config`
- Editable scope by default: `instructions/`
- If an instruction change also requires docs or validation alignment, edit the
  smallest matching files in `README.md`, `setup.md`, `docs/`, or
  `scripts/validate-repo.sh`.
- Do not commit, push, open PRs, alter CLI home configuration, or modify raw
  history files.
- Preserve user work. If the repository is dirty, read the relevant diffs before
  editing and avoid unrelated files.

## Sources To Review

Prefer the latest two calendar days of activity. If exact timestamps are hard to
compare, sample conservatively by recent modification time.

Inspect only what is needed from:

- `~/.claude/history.jsonl`
- `~/.claude/sessions/`
- `~/.claude/projects/`
- `~/.codex/history.jsonl`
- `~/.codex/session_index.jsonl`
- `~/.codex/sessions/`
- `~/.gemini/history`

If a source is missing, unreadable, too large, or permission-blocked, record that
as unreadable in the final summary and continue with the sources that are safe
to inspect.

## Privacy Rules

- Do not copy raw logs, secrets, tokens, private messages, or long verbatim
  excerpts into the repository or final summary.
- Summarize patterns abstractly. Use short paraphrases only when necessary.
- Do not write temporary copies of history into the repository.
- If you create temporary files, keep them outside the repository and remove them
  with `trash` when finished.

## Review Criteria

Look for repeated or high-leverage patterns such as:

- preventable clarification loops
- stale assumptions that should have been verified
- recurring tool mistakes or permission misunderstandings
- instruction routing confusion
- output style drift
- missing validation or weak completion checks
- unsafe or overly broad edits

Do not update instructions for one-off preferences, isolated mistakes, or
content that belongs in a project-specific file, skill, or temporary note.

## Editing Rules

- Keep instruction updates compact and generic.
- Rewrite nearby guidance instead of appending isolated rules.
- Preserve the core layer plus companion guide model:
  `AI_AGENT_INSTRUCTIONS.md` is the core shared contract, and `DESIGN.md` is the
  companion guide for human-visible output.
- If no durable instruction change is justified, make no repository edits.

## Verification

After any edit, run:

```sh
AI_AGENT_CONFIG_HOME="/Users/sh/Documents/ai-agent-config" AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh
sh scripts/validate-repo.sh
git diff --check
```

If no files changed, run at least:

```sh
sh scripts/validate-repo.sh
```

## Final Summary

Print one concise Markdown summary:

- reviewed sources and unreadable sources
- inefficiency patterns found
- instruction changes made, or why no change was made
- verification commands and results
- remaining risk or follow-up
