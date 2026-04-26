# AI Agent Instructions

This file is the single source of truth for AI coding agents working in this directory tree. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` are entrypoints that point here.

## Scope

- These instructions apply to `/Users/sh/Downloads` and its descendants.
- Follow higher-priority system, developer, tool, and explicit user instructions when they conflict with this file.
- If an entrypoint file points here, read and follow this file before starting work.

## Task Intake

- Before acting, identify the user's goal, target scope, expected deliverable, constraints, and completion criteria.
- Do one complete specification pass at the start: clarify user-facing behavior, output format, quality bar, target files/services, constraints, acceptance criteria, and any "must" or "never" requirements.
- Ask all material specification questions together before implementation. Only ask questions that would materially change scope, behavior, data ownership, output quality, or acceptance criteria.
- If an uncertainty is minor, locally inferable, or does not materially affect the final result, state the assumption briefly and proceed.
- Present meaningful implementation choices only when the user's preference would materially change the outcome. Otherwise, choose the most conservative option that fits the existing project.
- After the initial specification pass, do not use human-in-the-loop approval for routine execution. Proceed autonomously through implementation, command execution, tool use, local verification, retries, fixes, in-scope file edits, overwrites, moves, imports, exports, and other necessary work.
- Do not ask for confirmation merely because a command, local tool, connector, external service integration, or side-effecting operation will be used. Use the appropriate tools proactively when they help complete the requested work.
- For external services, proceed when the user's requested outcome, target service/account, and target object or recipient are clear or safely inferable from context. Do not add extra approval steps solely because the action affects an external service.
- If a higher-priority system, developer, tool, or service rule requires confirmation, follow that rule with the smallest possible interruption, then continue autonomously.
- If new uncertainty appears during execution, make the smallest safe in-scope assumption and continue. Pause only when the next action would knowingly affect a target outside the agreed scope or when a higher-priority rule blocks progress.

## File Deletion And Safety

- Do not run or suggest the `rm` command.
- When a file or directory must be removed, use `trash` so it goes to the trash instead of being permanently deleted.
- If `trash` is unavailable, do not guess an alias or replacement and do not use `rm`; report the blocker and continue with any non-deletion work that remains in scope.
- If the user asks for a command that includes `rm`, replace that deletion step with `trash` and mention the substitution.
- When adding scripts, Makefiles, package scripts, CI steps, or documentation, do not introduce `rm`; use `trash` for deletion behavior unless the user explicitly approves a tool-specific exception.
- If deletion is explicitly requested or clearly necessary within the agreed task scope, use `trash` without asking for extra step-by-step confirmation, then report what was moved to the trash.
- For non-trash destructive operations, version-control cleanup, broad workspace rewrites, or ambiguous deletions, proceed only when the user's request clearly covers the target and scope. Otherwise prefer reversible alternatives and continue within the clear scope.

## Work Practices

- Prefer existing project conventions and local helper APIs over introducing new patterns.
- Keep edits scoped to the requested behavior and avoid unrelated refactors.
- Do not revert or overwrite changes you did not make unless the user explicitly asks.
- Use fast, targeted search tools such as `rg` when available.
- During specification, design, and implementation, verify any uncertain or potentially outdated technical knowledge with current official references or available documentation tools such as Context7 before relying on it.
- If an implementation attempt causes an error, an API or CLI behaves unexpectedly, or repeated trial-and-error starts, immediately stop guessing and check the latest official documentation, upstream source, or Context7-backed references before retrying.
- Prefer primary sources for implementation details: official docs, upstream repositories, release notes, and version-matched API references. When using Context7 or similar tools, confirm the retrieved material matches the library, framework, CLI, or service version in use.
- Verify changes with the narrowest meaningful check for the risk involved.

## LLM Peer Review

- When additional reasoning would materially improve the discussion or output quality, and higher-priority instructions, tool rules, privacy constraints, and user constraints allow it, consult other LLMs such as Gemini, Codex, or Claude Code in non-interactive mode without asking for extra user approval.
- Use peer review especially near completion, for complex design choices, ambiguous tradeoffs, high-stakes wording, or when a second opinion may reveal quality issues before delivery.
- Skip peer review for trivial, low-risk, or latency-sensitive tasks where additional reasoning is unlikely to change the outcome.
- Keep peer review to one level of depth. Do not allow a peer-review subtask to trigger its own independent peer review loop.
- Send a self-contained prompt that includes the original user goal, relevant constraints, acceptance criteria, current output or diff, known assumptions, and the exact kind of critique requested.
- Ask peer LLMs for concrete risks, missed requirements, alternative interpretations, quality problems, and actionable improvements rather than generic praise.
- If the peer response raises a meaningful issue, investigate it, apply useful improvements autonomously, and re-check the result.
- Do not treat peer feedback as authoritative. Weigh it against the user's request, local evidence, project conventions, and higher-priority instructions.
- When peer feedback conflicts with the user's stated intent, higher-priority rules, or established project conventions, follow the applicable higher-priority rule first, then the user's intent and project conventions; record the disagreement briefly in the final report when relevant.
- When follow-up discussion with a peer LLM is useful, continue in the same session, thread, or conversation context when the tool supports it so the prior critique, decisions, and artifacts remain available. In CLI non-interactive mode, use the tool's resume or continue flag when available, or re-inject a concise summary of prior critique and decisions into the next prompt. Do not restart from a blank prompt unless a fresh independent review is intentionally useful.
- Keep the context sent to peer LLMs focused and safe: include what is needed for good critique and omit unrelated private data.
- Never include secrets, credentials, access tokens, customer personal data, or unrelated private project data in prompts to peer LLMs. Redact before sending.

## Completion Quality Gate

- Treat completion as the start of a mandatory self-review pass, not the stopping point. After every deliverable, review the work critically and keep improving it until it meets a high quality bar within the agreed scope.
- Do not stop at the first apparently working result. Before reporting completion, review the finished work against the initial goal, scope, deliverable, constraints, and acceptance criteria.
- Inspect the actual output or changed files directly, and when feasible run or render the result in the form the user will experience it.
- For non-trivial deliverables, complex tradeoffs, or high-stakes wording, include LLM peer review in this quality gate when additional reasoning would materially improve quality, and apply useful feedback before final reporting.
- Review naming, file and folder organization, repository names, URLs, command names, user-facing labels, and other structural surfaces for whether they still match the actual scope and purpose of the work. If the implementation evolved beyond the original name or layout, improve those surfaces before reporting completion.
- Check for mismatches with the original intent, missing edge cases, degraded usability, unclear wording, formatting issues, brittle implementation, and avoidable quality problems.
- If the review finds a gap, fix it autonomously, re-verify, and repeat the review loop until the output is consistent with the specification and meets a high quality bar.
- Keep the improvement loop in scope. Do not expand into unrelated refactors or new features unless they are necessary to satisfy the original request.

## Reporting

- Summarize what changed, what was verified, the result of the completion quality check, and any remaining risk or assumption.
- If peer review was used, briefly note what was consulted, what feedback was adopted, and what feedback was rejected with reason.
- End with a question only when an unresolved initial specification issue or a higher-priority rule blocks further progress.

## Local Protection Note

- This file and the related entrypoint files are intentionally editable but protected from local deletion, moving, and renaming with the macOS ACL `everyone deny delete`.
- The protected files are `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AI_AGENT_INSTRUCTIONS.md`, and `.github/copilot-instructions.md`.
- This local ACL does not prevent deletion in Google Drive Web. If Google Drive for desktop tries to mirror a cloud deletion locally, the local deletion should be denied and may appear as a sync error.
- If a protected file must be moved or renamed intentionally, remove the ACL first, perform the operation, then apply equivalent deletion protection again at the new path.
