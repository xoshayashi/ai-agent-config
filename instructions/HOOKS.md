# HOOKS.md

This document defines the shared self-check Hook behavior for this repository.

## Same-CLI Subprocess Check

The Hook installed by this repository is **opt-in and advisory**. It does not
push any specific skill on the CLI, and it does not enforce a spec-first
lifecycle. Its only job is to ask the **same CLI in non-interactive
subprocess mode** for the next concrete step (or a completion signal) at hook
boundaries, and surface that subprocess output to the main session.

The hook script is `hooks/scripts/subprocess_check.py`. It is shared across:

- Codex (uses `codex exec --json -`)
- Claude Code (uses `claude -p --output-format json`)
- Gemini CLI (uses `gemini -p`)
- GitHub Copilot CLI (uses `copilot -p -s --no-ask-user`)

The subprocess inherits the user's environment, so any installed skills
(refinment, brainstorming, debugging, and others) activate via each skill's own
conditions during the subprocess turn — without the hook quoting any skill
name.

## Lifecycle

```
[main CLI]
    ↓ Hook event (UserPromptSubmit / Stop / ...)
[hook: subprocess_check.py]
    ↓ lightweight Python gate
       - skip if disabled, completed, hard cap reached
       - skip Stop-style events whose response is short / answer-only / contains
         `[[TASK_DONE]]`
    ↓ build small advisor prompt (event + original task + last response)
[same-CLI subprocess]
    ↓ runs as a one-shot, non-interactive turn with
      AI_AGENT_SELF_WORKFLOW_ACTIVE=1 set so its own hook is suppressed
    ↓ replies with either
        - first line `STATUS: complete`           → task is done
        - any other text                          → next concrete step
[hook]
    ↓ if `STATUS: complete`: stop, mark task complete in state
    ↓ if instruction: return it as a continuation prompt to the main session
```

The subprocess's reply is passed back as the continuation prompt verbatim. It
does not need to follow a phase model and does not need to emit any keyword.

## Completion Signals

Two signals are recognized; everything else is treated as "more work needed":

- **`STATUS: complete`** as the first line of the subprocess output. The hook
  records the task as complete and stops continuing.
- **`[[TASK_DONE]]`** on a standalone line in the **main session's** response.
  The hook treats this as a shortcut: the main session is confident the task is
  done, so the hook skips the subprocess call for that turn.

There are no other completion keywords. The previous `[[SPEC_DONE]]`,
`[[IMPLEMENTATION_DONE]]`, `[[VERIFICATION_DONE]]`, and structured
`phase_signal` packets are not part of this design.

## Safety Limits

| Control | Default | Override |
|---|---|---|
| Per-task subprocess call cap | 8 | `AI_AGENT_SUBPROCESS_CHECK_MAX` |
| Subprocess timeout (seconds) | 180 | `AI_AGENT_SUBPROCESS_CHECK_TIMEOUT` |
| Min response length to consider a Stop event substantive | 200 chars | `AI_AGENT_SUBPROCESS_CHECK_MIN_OUTPUT` |
| Recursion guard for nested subprocess calls | always on | `AI_AGENT_SELF_WORKFLOW_ACTIVE=1` (set automatically) |
| Off switch | enabled | `AI_AGENT_SUBPROCESS_CHECK=0` disables the hook entirely |

If a subprocess call fails (binary missing, non-zero exit, timeout), the hook
returns no continuation. The main session keeps control.

## State and Audit Log

State and audit log live under `${AI_AGENT_STATE_DIR:-$HOME/.ai-agent-config}/subprocess-check/`:

- `<session_id>.json` — per-session counters (`calls_used`, `completed`,
  `original_prompt`).
- `decisions.jsonl` — newline-delimited JSON of every hook decision (skip /
  instruction / complete / empty), useful for debugging or auditing the
  advisor's behavior after the fact.

State is cleared automatically when a session begins a clearly new task. There
is no phase machine to keep in sync.

## What the Hook Does Not Do

- It does not push the use of any skill (refinment, brainstorming, etc.). The
  subprocess decides what skills, if any, to invoke based on each skill's own
  activation conditions.
- It does not require the main session to draft a specification first.
- It does not parse `[[SPEC_DONE]]` / `[[IMPLEMENTATION_DONE]]` /
  `[[VERIFICATION_DONE]]` or any structured phase packet. Those keywords are no
  longer part of this design.
- It does not call other LLMs or external reviewer subprocesses. The
  subprocess is the **same CLI** running in non-interactive mode.

## Human-in-the-loop

If the subprocess returns content that looks unsafe, ambiguous, or out of
scope, treat it as advisory. The user can interrupt at any time, and the hard
caps are designed to stop runaway loops automatically.
