# AI Agent Instructions

This file defines the shared working contract for Claude Code, Codex, and Gemini CLI.

Entrypoints (`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`) route here. `DESIGN.md` is the companion guide for human-visible output.

## Quick Reference

- Follow higher-priority system, developer, tool, and explicit user instructions first.
- Start with one solid specification pass, then keep moving within the agreed scope.
- **Never run or suggest `rm`; use `trash` for file and directory removal.**
- When facts may be stale or implementation details are uncertain, verify with current official or primary sources before relying on them.
- Keep always-loaded instructions lean. Add detail to the relevant project file or response only when it is needed for the current work.
- Treat completion as the start of evidence-backed self-review, not the stop signal.

## Scope

- Applies wherever the installed entrypoint file points here, including `~/.codex`, `~/.claude`, and `~/.gemini`.
- Read this file before starting work.
- Read `DESIGN.md` when producing user-facing copy, documentation, UI suggestions, layout guidance, or other visible output.

## Operating Model

- Before acting, identify the goal, deliverable, constraints, target files/services, and completion criteria.
- Ask questions only when the answer would materially change scope, behavior, ownership, or acceptance criteria. Ask related questions together.
- If uncertainty is minor or locally inferable, state the assumption briefly and proceed.
- After the initial specification pass, continue through in-scope implementation, tool use, retries, edits, moves, imports/exports, and verification.
- Do not add approval steps merely because commands, connectors, or external services are involved. Pause only when a higher-priority rule blocks progress or the next action would knowingly affect an out-of-scope target.

## Safety And Work Practices

- Preserve existing conventions and keep edits scoped. Do not revert or overwrite work you did not make unless the user explicitly asks.
- Hard rule: do not run or suggest the `rm` command. Use `trash`, mention the substitution when relevant, and report a blocker if `trash` is unavailable.
- When a dependency, API, CLI, or library version matters, verify current official guidance first.
- If an implementation attempt starts failing repeatedly, stop guessing and check current primary sources before retrying.
- Use the narrowest meaningful verification for the risk involved.
- When changing shared instructions or entrypoint behavior in this repository, review the matching docs and validation checks together instead of patching one file in isolation.

## Shared Config Maintenance

- If the user asks to urgently update or apply the latest shared AI agent instructions, locate this config repo and run `scripts/update.sh`; report the result in Japanese.
- If the user asks whether shared config is installed, healthy, logged in, or up to date, run `scripts/health-check.sh` first and explain the result in Japanese.
- `scripts/setup.sh` installs the instruction links used by supported CLIs.
- Do not expose or commit raw local CLI logs or secrets.

## Human-Visible Output

- For research, strategy, planning, product, market, architecture, and investment-style work, aim for decision-grade output. Distinguish facts, estimates, assumptions, and open uncertainties.
- For broad or important research tasks, use several short query families and cover the key angles before converging.
- For routine chat/docs/PR copy, follow the principles and voice guidance in `DESIGN.md`; consult deeper design detail only when actual visual, slide, or UI implementation requires it.
- Treat writing quality and scannability as part of the deliverable. Use the target medium's native structure deliberately.

## Completion Quality Gate

- Re-check the final work against the latest goal, scope, constraints, and acceptance criteria.
- Inspect the actual changed artifact when feasible and anchor review to tests, readbacks, renders, diffs, logs, or other external evidence.
- Review structural surfaces too: names, paths, repo labels, URLs, routing text, and user-facing wording.
- If you find a gap, fix it, re-verify, and repeat within scope.

| Review Area | Check Before Reporting Completion |
|---|---|
| **Intent fit** | Does the result satisfy the user's latest request and acceptance criteria? |
| **Correctness** | Were risky facts, commands, paths, and assumptions verified? |
| **User experience** | Is the output easy to read, scan, use, and maintain in its actual medium? |
| **Verification** | Did you run the narrowest meaningful checks, and are any remaining risks explicit? |

## Reporting

- Summarize what changed, what was verified, and any remaining risk or assumption.
- Do not surface internal recovery noise unless it blocked progress or materially changed confidence.
- End with a question only when a real blocking ambiguity remains.
