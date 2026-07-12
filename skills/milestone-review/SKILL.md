---
name: milestone-review
description: "Use at the milestone / hand-off boundary of any non-trivial task to route a review to the right reviewer (transcript-aware host tool / external CLI reviewers: Codex, Claude, Antigravity / self), construct a context-rich prompt for that reviewer, run it, and verify the answer before continuing — so the caller cannot rubber-stamp its own work or blindly adopt an outside take. Host-agnostic: usable from Claude Code, Codex, or Antigravity."
---

# milestone-review

A general-purpose routing skill any other skill or agent can invoke at a
milestone boundary. It (1) picks the right reviewer for the question, (2)
constructs a prompt that the reviewer can actually act on, (3) runs the
review, (4) verifies the answer instead of accepting or rejecting it
blindly, and (5) records the outcome so a fresh session can recover.

The deep reference is `references/_reviewer_routing.md`. Read it before
your first review of a task and once the question shape changes. Re-read
on demand for prompt templates and the per-reviewer prompt construction
rules.

## Host awareness (read first)

This skill is host-agnostic: the calling agent may be running inside
Claude Code, Codex, Antigravity, or another agent CLI. Name
your host before routing anything, then apply two rules:

- **Exclude your own host from external routes.** Dispatching a review
  to the CLI you are running inside is the same model family re-reading
  its own work — self-review in disguise. Pick external reviewers from
  the remaining CLIs (running in Codex → route to claude /
  antigravity; and so on). The dispatch helper enforces this: pass `--host` and it
  refuses a host-self-review dispatch with exit code 2.
- **The transcript-aware route depends on the host.** Claude Code
  provides an `advisor()` host tool that reads the live session
  transcript. Other hosts have no equivalent: substitute it by writing
  a context digest yourself (goal, key decisions so far, current state,
  what is being evaluated) and sending it to an external CLI of a
  different model family. This substitute is weaker than a true
  transcript reader — record that the milestone used the digest route.

## When to invoke

- A phase / component finished and is about to be merged or handed off.
- About to commit to an interpretation that the next step builds on.
- A loop is repeatedly failing the same check and the cause is unclear.
- Multiple plausible designs and you need a tiebreaker.
- Before declaring a long task complete.

Do not invoke for cosmetic edits, lookup-style questions, or where the
verification is already obvious from `git diff` and a passing test.

## Reviewer routing (one-line summary)

- **transcript-aware** — depth on the current task; use once per
  milestone for "did I miss something structural" judgement. On Claude
  Code this is the `advisor()` host tool (full transcript, cannot be
  parallelized). On other hosts, a context-digest prompt to a
  different-family external CLI.
- **External CLI reviewers** — one-shot processes, prompt-only context,
  parallel-friendly. Dispatched via `scripts/route_review.py`:
  - **codex** (`codex exec`) — concrete code / diff / logic checks.
  - **claude** (`claude -p`) — structural judgement and design-taste
    review when the host is not Claude Code.
  - **antigravity** (`agy -p`) — an additional independent route when
    the other CLIs are the host or unavailable.
  Never pick the CLI you are running inside (see Host awareness).
- **self** — immediate, in-process. Use only for mechanical checks
  (style, schema, regex, test-runner exit code) where rules are explicit
  and not under negotiation.

Full table + selection heuristics in `references/_reviewer_routing.md`.

## Flow

1. **Detect the milestone.** Name it: what just finished, what comes next,
   what decision the review will gate. Also name your host CLI.
2. **Classify the review.** Map the question to one or more reviewer
   roles using `_reviewer_routing.md`. If two roles fit, dispatch both
   (transcript-aware + a code-focused external CLI is the common pair).
3. **Construct the prompt.** External CLIs see nothing but the prompt.
   Include: background (one paragraph the reviewer can read cold), the
   specific target (path, lines, diff, or copy-pasted excerpt), and a
   single sharp question. Templates in `_reviewer_routing.md`.
4. **Run the review.**
   - transcript-aware → on Claude Code call `advisor()` directly; on
     other hosts send your context digest through the helper to a
     non-host external CLI.
   - external CLIs → call the helper, where `<skill_dir>` is the
     directory containing this SKILL.md (the skill is symlinked into
     each host's config home, so resolve it from where you loaded this
     file):
      ```sh
      # Before the first review of a session (or after any route degraded):
      # probe every pool route with a trivial prompt, report status + seconds.
      python3 <skill_dir>/scripts/route_review.py --doctor --host claude-code

      # Dispatch one review. auto = first available non-host CLI, with
      # automatic failover to the next peer if the primary fails.
      python3 <skill_dir>/scripts/route_review.py \
          --reviewer auto \
          --host claude-code|codex|antigravity \
          --prompt-file <review_ask.md> \
          [--include-git] [--strict-gate] [--timeout 600] [--json]
      ```
      Always pass `--host` (the CLI you are running inside): it enables the
      host self-review guard, which hard-blocks a dispatch to your own host
      CLI with exit code 2 before running anything.

      Dispatch mechanics you should know (each is measured, not assumed —
      details and bench numbers in `_reviewer_routing.md` "Latency and
      timeouts"):
      - **Timeout is 600s per attempt by default** and is forwarded to
        antigravity's internal `--print-timeout`. Real reviews on
        heavyweight default models take minutes; a 180s-style short timeout
        is how a healthy route gets misrecorded as degraded. Lower it only
        for quick mechanical checks; raise it for very large diffs.
      - **Prompts travel via stdin** for codex and claude (no argv length
        ceiling, not visible in `ps`); antigravity takes argv. Prefer
        `--prompt-file` for anything multi-line.
      - **claude runs isolated** (no host MCP servers / plugins / hooks) and
        **codex runs with `--skip-git-repo-check`** (it otherwise refuses to
        start outside a trusted git repo). You do not need to pass these —
        the helper builds them in.
      - **`--include-git`** appends `git status` + `git diff HEAD` (and
        untracked files) to the prompt so a cold reviewer sees the live
        changes.
      - **`--strict-gate`** exits 3 when any attempt's output contains
        `[BLOCKING]`, `[CRITICAL]`, or `❌`. Only these opt-in markers count
        (free-text phrases false-positive on negations like "no blocking
        issue"). The helper appends the tagging instruction to the prompt
        automatically, so the reviewer always knows to mark blockers with
        `[BLOCKING]`.

      **Exit codes drive shell loops without `--json`:**
      - `0` = Review ran clean on the first route and passed the quality gate.
      - `1` = Review degraded (timeout, missing CLI, final non-zero exit) — no usable review.
      - `2` = Invocation error, nothing dispatched (host self-review, missing host guard, or unreadable prompt-file).
      - `3` = **Strict gate failed** (a reviewer ran, but a blocking marker was found — scanned across every attempt, including partial output from a timed-out one).
      - `4` = **Reviewed via failover**: a valid review came back, but only after one or more routes degraded. Treat the answer as a real review, and record the failed route(s) as `degraded` in the milestone log — exit 4 exists precisely so reduced reviewer independence can never look like a clean 0 to a shell loop. The helper also prints a one-line `route_review: attempts: ...` summary to stderr on every multi-attempt dispatch.

      Do not let an exit-1 or exit-3 review pass the milestone; an exit-4
      review passes only with the degraded route recorded.
5. **Verify the answer** against four checks. Apply each in order; do
   not skip any.
   1. **Grounded?** Does each load-bearing claim cite a file, a line, a
      test output, or a primary source you can re-open?
   2. **Consistent with primary evidence?** If the reviewer says X but
      the file says Y, the file wins. Note the contradiction back to the
      reviewer rather than picking silently.
   3. **Adjudication.** When two reviewers disagree, identify the
      constraint that breaks the tie (test, spec, source code, user
      directive). Do not average.
   4. **Predictive plausibility.** Given this answer, can you predict
      the outcome of the next step? If not, the answer is too vague and
      needs to be re-asked.
6. **Record.** Append a short entry to the calling task's progress log
   (e.g. `docs/sfm-overhaul/progress.md`) so a fresh session can audit
   whether the review was *valid*, not just what it concluded: host,
   reviewer(s) + each route's `status` (ok / degraded / blocked), whether
   a digest substitute route was used, the one-line conclusion, the
   verification verdict (which of the four checks passed / what
   contradiction was reconciled and how), and the next action. Name the
   end state explicitly — **reviewed**, **degraded route** (reduced
   independence), or **unreviewed / blocked** (no independent route was
   possible; see Failure handling). Never let a degraded or blocked
   milestone read as a clean **reviewed** in the log. Copy-paste template
   (keeps the record uniform so a later run can diff it):

   ```md
   - milestone: <what finished> | host: <cli> | end state: reviewed|degraded|blocked
     routes: <reviewer>=<ok|degraded|blocked>[, ...] | digest route: yes|no
     conclusion: <one line>
     verified: <which of the 4 checks held / contradiction + how reconciled>
     next: <action>
   ```

## Anti-patterns (refuse these)

- **Blind adoption.** Reviewer says "rewrite X"; you do it without
  re-checking the file. Do not.
- **Blind rejection.** Reviewer's claim conflicts with what you already
  believe; you dismiss without testing. Do not. Make the conflict
  explicit and ask a follow-up.
- **Single-route certainty.** A transcript-aware review alone on a
  code-logic question is weak signal; pair with an external CLI on the
  diff. An external CLI alone on a "does this make sense in context"
  question is weak signal; pair with the transcript-aware route.
- **Self-review masquerading as review.** Calling `milestone-review` and
  routing the answer back to yourself is no review. Self route is for
  mechanical checks only.
- **Host-CLI self-review.** Routing an external review to the CLI you
  are running inside (Codex agent calling `codex exec`, Claude Code agent
  calling `claude -p`, ...). Same model family, no independence. Pick a
  different CLI. The helper refuses this (exit 2) when `--host` is
  passed, and refuses to dispatch at all when neither `--host` nor
  `--no-host-guard` is passed — so omitting `--host` no longer works
  around the guard, it just blocks you.
- **Silent CLI failure.** Helper returned `status="error"`; you treat
  it as a pass. Do not. Record and either retry, switch reviewer, or
  flag as a blocker.

## Failure handling

- CLI returned `status="error"` (timeout / missing binary / non-zero):
  first look at *why* (`--json` includes the failover trace in
  `attempts`; a timeout keeps the reviewer's partial stdout). A timeout
  with substantial partial output means the route is healthy and the
  question is big — re-dispatch with a higher `--timeout`, do not switch
  reviewer. Retry once if the cause might be transient (rate limit);
  otherwise switch to a different reviewer for that question; otherwise
  record the milestone as reviewed by a reduced route and surface the
  gap. After any degraded route, run `--doctor` so the next milestone
  starts with measured knowledge of which routes work.
- All external CLIs unavailable: on **Claude Code**, fall back to the
  `advisor()` transcript-aware tool — still an independent review —
  and record the reduced route. On **other hosts there is no
  independent route left** (self is not one — it is the caller
  re-reading its own work, mechanical checks only). For a **judgment**
  call, do not launder self into a review: stop with an explicit
  **unreviewed / blocked** end state, record why in progress.md, and
  hand back for a human or a later run with CLIs available. Only a
  **mechanical** check (lint / schema / test exit code) may proceed on
  self alone here.
- Reviewer disagrees with itself on rerun: take that as a signal the
  prompt is under-specified; tighten the question, do not pick one
  answer.

## Tests

```sh
PYTHONPYCACHEPREFIX=$(mktemp -d) \
    python3 <skill_dir>/tests/test_route_review.py
```
