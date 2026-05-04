---
name: daily-llm-history-instruction-review
description: "Review recent Claude Code, Codex, and Gemini CLI interaction history, identify repeated user-agent inefficiencies, and update shared instruction files only when a durable improvement is clear. Use for the ai-agent-config daily instruction review, especially from Codex App Automations."
---

# Daily LLM History Instruction Review

## Purpose

Run a bounded review of recent Claude Code, Codex, and Gemini CLI activity for
the `ai-agent-config` repository. The goal is to improve shared instructions
only when recent history shows a repeated, durable pattern that is worth
encoding.

This skill is intended for Codex App Automations. Keep the output concise and
safe because it may run unattended.

## Repository And Scope

- Repository: the current `ai-agent-config` checkout. If needed, set
  `AI_AGENT_CONFIG_HOME` to that checkout path before running verification.
- Editable scope by default: `instructions/`
- If an instruction change also requires docs or validation alignment, edit the
  smallest matching files in `README.md`, `setup.md`, `docs/`, or
  `scripts/validate-repo.sh`.
- Do not alter CLI home configuration or modify raw history files.
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

- repeated user prompts that compensate for missing completion-quality behavior,
  such as requests to self-review, evaluate, iterate, improve quality, rerun
  checks, inspect the real artifact, or avoid calling a first pass "done"
- preventable clarification loops
- stale assumptions that should have been verified
- recurring tool mistakes or permission misunderstandings
- instruction routing confusion
- output style drift
- missing validation or weak completion checks
- unsafe or overly broad edits

For repeated user prompts, do not merely encode "when the user says X, do Y".
Translate the pattern into proactive agent behavior that should make the prompt
less necessary next time. For quality loops, the durable behavior is usually:
self-review before declaring completion, compare the actual artifact against the
user's intent, run the relevant checks or readbacks, improve material gaps, and
repeat until the result is good enough or a concrete blocker remains.

Do not update instructions for one-off preferences, isolated mistakes, or
content that belongs in a project-specific file, skill, or temporary note.

## Editing Rules

- Keep instruction updates compact and generic.
- Rewrite nearby guidance instead of appending isolated rules.
- Prefer behavior-level guidance that reduces future user steering over
  trigger-response rules tied to a specific phrase.
- Preserve the core layer plus companion guide model:
  `AI_AGENT_INSTRUCTIONS.md` is the core shared contract, and `DESIGN.md` is the
  companion guide for human-visible output.
- If no durable instruction change is justified, make no repository edits.

## Verification

After any edit, run:

```sh
AI_AGENT_CONFIG_HOME="${AI_AGENT_CONFIG_HOME:-$PWD}" AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh
sh scripts/validate-repo.sh
git diff --check
```

If no files changed, run at least:

```sh
sh scripts/validate-repo.sh
```

## GitHub Closeout

For Codex App Automation runs, complete repository closeout when the review
creates repository changes:

- Create a branch named `daily-llm-history-instruction-review-YYYYMMDD` using
  the local run date, unless that branch or an open PR for the same run already
  exists. Continue the existing branch/PR if present.
- Commit only the intended review changes. Preserve unrelated user work.
- Push the branch and open a pull request against `main`.
- Add `codex` and `codex-automation` labels when those labels exist. If they do
  not exist, skip them and mention that in the summary.
- Monitor checks, review comments, and unresolved review threads until the PR is
  clean. Address actionable feedback with follow-up commits and rerun the
  verification commands.
- Mark the PR ready if it was opened as draft, then merge it when checks pass,
  review feedback is resolved, and the merge state is clean. Prefer squash merge
  and delete the remote branch.

If no repository files changed, do not open a PR.

## Final Summary

Print one concise Markdown summary:

- reviewed sources and unreadable sources
- inefficiency patterns found
- instruction changes made, or why no change was made
- verification commands and results
- PR URL and merge status when changes were made
- remaining risk or follow-up
