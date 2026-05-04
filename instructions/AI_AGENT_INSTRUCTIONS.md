# AI Agent Instructions

Shared working contract for Claude Code, Codex, and Gemini CLI.

Entrypoints (`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`) route here. `DESIGN.md` is the companion guide for human-visible output.

## Operating Defaults

- Follow higher-priority system, developer, tool, and explicit user instructions first.
- For non-trivial work, clarify the goal, scope, target, constraints, and completion signal once, then keep moving.
- Treat repeated user prompts to review, improve, evaluate, or "make it good enough" as a signal that completion quality is under-managed. Do not present work as complete after the first pass; self-review against the user's intent, inspect outputs and verification evidence, fix meaningful gaps, and iterate until the result is sufficient or a concrete blocker remains.
- Ask only when the answer materially changes scope, ownership, safety, or acceptance criteria. Infer small gaps and state the assumption.
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
- If an attempt repeatedly fails, stop guessing and check the relevant source of truth.
- When changing shared instructions or entrypoints in this repository, update matching docs and validation checks in the same pass.

## Human-Visible Output

- Follow `DESIGN.md` for copy, tone, documentation, color, typography, layout, UI, and slide-facing work.
- For research, strategy, architecture, market, product, and investment-style work, separate facts, estimates, assumptions, and open uncertainties; tie recommendations to the user's decision criteria such as pricing, customer ROI, cost structure, latency, quality, implementation effort, or required real-world tests.
- Keep the final answer concise: what changed, what was verified, and what risk or assumption remains.

## Shared Config Maintenance

- To apply the latest shared instructions, locate this config repo and run `scripts/update.sh`; report the result in Japanese.
- To check installation, health, login, or freshness, run `scripts/health-check.sh` first and explain the result in Japanese.
- `scripts/setup.sh` installs the instruction links used by supported CLIs.
- Do not expose or commit raw local CLI logs or secrets.
