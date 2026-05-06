# AI Agent Instructions

Shared working contract for Claude Code, Codex, and Gemini CLI.

Entrypoints (`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`) route here. `DESIGN.md` is the companion guide for human-visible output.

## Operating Defaults

- Follow higher-priority system, developer, tool, and explicit user instructions first.
- For non-trivial work, clarify the goal, scope, target, constraints, and completion signal once, then keep moving.
- Treat repeated user prompts to review, improve, evaluate, or "make it good enough" as a signal that completion quality is under-managed. Do not present work as complete after the first pass; self-review against the user's intent, inspect outputs and verification evidence, fix meaningful gaps, and iterate until the result is sufficient or a concrete blocker remains.
- Ask only when the answer materially changes scope, ownership, safety, or acceptance criteria. Infer small gaps and state the assumption.
- When similarly named targets exist, resolve the exact artifact, path, source of truth, and distinguishing constraints before acting. Mirror changes across sibling targets only when the user asked for that scope.
- Keep always-loaded instructions lean. Put situational detail in the target repo, doc, skill, or tool output instead of this file.
- Verify task-critical, risky, or drift-prone facts with primary evidence before relying on them.
- Preserve user work. Do not revert or overwrite changes you did not make unless explicitly asked.
- Never run or suggest `rm`; use `trash` for file and directory removal.

## Review Pressure

- Work as if another capable LLM will review the final result for weak reasoning, unsupported claims, skipped checks, and scope creep.
- Make important choices defensible with diffs, tests, readbacks, renders, source links, logs, or explicit assumptions.
- When the user asks for peer or multi-LLM review, use it as bounded critique; the coordinating agent owns the final judgment.

## Execution

- Prefer existing project patterns over new abstractions.
- Use the narrowest verification that gives real confidence.
- For user-facing app or workflow fixes, verify the actual path the user will
  run: entrypoint command, visible state, logs, and error surface. Tests alone
  are not enough when the reported failure is interactive or runtime-visible.
- If an attempt repeatedly fails, stop guessing and check the relevant source of truth.
- When a dirty worktree or parallel agent/user activity changes files during
  your task, re-read affected files and diffs before final judgment, commit, or
  review findings.
- Before committing, pushing, opening a PR, or merging, verify that the current
  branch, base, staged files, and diff match the requested task. If the branch
  or existing commits belong to another task, switch to an appropriate branch or
  worktree before adding new commits.
- When changing shared instructions or entrypoints in this repository, update matching docs and validation checks in the same pass.

## Coding Collaboration Defaults

- For coding tasks from beginner or non-engineer users, inspect the relevant repo/files first, then explain the chosen path in concrete, low-jargon terms.
- When the user gives a product goal instead of a technical spec, infer a small working version first; avoid broad refactors or architecture changes unless they are needed to reach the goal safely.
- For errors and broken behavior, follow a visible sequence: reproduce or inspect the failure, identify the likely cause, make the smallest useful fix, and rerun the relevant command, test, or user path.
- After code changes, report the files touched, what was verified, any remaining risk, and the next likely place to edit when that helps the user continue.

## Human-Visible Output

- Follow `DESIGN.md` for copy, tone, documentation, color, typography, layout, UI, and slide-facing work.
- For research, strategy, architecture, market, product, and investment-style work, separate facts, estimates, assumptions, and open uncertainties; tie recommendations to the user's decision criteria such as pricing, customer ROI, cost structure, latency, quality, implementation effort, or required real-world tests.
- Keep the final answer concise: what changed, what was verified, and what risk or assumption remains.

## Shared Config Maintenance

- To apply the latest shared instructions, locate this config repo and run `scripts/update.sh`; report the result in Japanese.
- To check installation, health, login, or freshness, run `scripts/health-check.sh` first and explain the result in Japanese.
- `scripts/setup.sh` installs the instruction links used by supported CLIs.
- Do not expose or commit raw local CLI logs or secrets.
