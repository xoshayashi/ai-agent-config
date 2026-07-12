# Reviewer routing reference

The deep playbook behind `SKILL.md`. Read once per task at first review,
and re-read when the question shape changes.

## Routing table

| Reviewer | Nature | Best for | Worst for | Invocation |
|---|---|---|---|---|
| **advisor** (Claude Code host tool only) | Reads the full live session transcript: every tool call, every result. Deep reasoning. Single instance per call. Does not exist on other hosts — see "Host awareness" below for the substitute. | Structural soundness, "what did I miss", strategy reviews, end-of-task self-audit, deciding between two designs grounded in the conversation. | Anything the transcript does not cover. Parallel fan-out. Re-running with different prompts cheaply. | Host tool `advisor()` from inside a Claude Code agent. |
| **Codex CLI** | External one-shot process. Sees only the prompt you pass. Strong on concrete code / diff / logic. | Reviewing a specific diff, a function for correctness bugs, a test for what it actually proves, a regex / SQL / config snippet. Parallelizable. | Questions that need the live conversation context the prompt cannot reconstruct. Reviews dispatched from a Codex host (self-review). | `codex exec <prompt>` via `scripts/route_review.py --reviewer codex`. |
| **Claude CLI** | External one-shot process (`claude -p`). Anthropic model family. | Structural judgement and design-taste review when the host is not Claude Code; the transcript-aware substitute via a context digest. | Reviews dispatched from a Claude Code host (self-review — use `advisor()` there instead, which also sees more). | `claude -p <prompt>` via `scripts/route_review.py --reviewer claude`. |
| **Antigravity CLI** | External one-shot process (`agy -p`, print mode). Google model family by default. | An additional independent route when the other CLIs are the host or unavailable; second opinion. | Reviews dispatched from an Antigravity host. | `agy -p <prompt>` via `scripts/route_review.py --reviewer antigravity`. |
| **self** | The calling agent immediately rechecks. | Mechanical, rule-based checks: linter exit code, schema match, regex pass, test runner green. | Anything requiring judgement or design taste. Self-review of one's own claim of correctness. |

`route_review.py` dispatches the external CLIs (**codex**,
**claude**, **antigravity**) — advisor and self are driven from
`SKILL.md` flow steps directly.

## Host awareness & Auto-Routing

The skill can be invoked from Claude Code, Codex, or
Antigravity. Two consequences:

1. **Host exclusion.** Never route an external review to the CLI you
   are running inside — it is the same model family re-reading its own
   work. `route_review.py` enforces this when you pass
   `--host <claude-code|codex|antigravity>`: a host-self-review
   dispatch exits 2 without running anything ("claude" is accepted as
   an alias for "claude-code"). 
   
   To simplify this, use **`--reviewer auto`** (the default):
   - **Host Detection**: It automatically reads your `--host` and derives the safe, valid pool of non-host external CLIs.
   - **Binary Auto-Detection**: It checks which external CLIs are actually installed and on your PATH (using `shutil.which`).
   - **Priority Sorting**: It places available binaries at the front of the queue.
   - **Automatic Failover & Resilience**: If the preferred peer CLI fails (timeout, missing, or rate limited), the router automatically and transparently attempts failover to the next compatible peer CLI in the pool, ensuring maximum milestone resilience (can be disabled with `--no-failover`).

   Effective external pool per host:

   | Host | Transcript-aware route | External pool |
   |---|---|---|
   | Claude Code | `advisor()` host tool | codex, antigravity |
   | Codex | context digest → claude (or antigravity) | claude, antigravity |
   | Antigravity | context digest → claude (or codex) | codex, claude |

2. **Transcript-aware substitute.** Outside Claude Code there is no
   tool that reads the live transcript. Reconstruct it: write a context
   digest and send it with the structural question to a
   different-family external CLI. Mark the record with "digest route" —
   it only knows what you chose to include, so it cannot catch omissions
   the way a real transcript reader can. Bias the digest toward what you
   might be wrong about, not what you did.

   Digest checklist (a weak digest launders your blind spot into the
   review, so treat each line as required, not optional):
   - **Goal + done-criterion** — what the task must achieve and how
     completion is judged.
   - **Constraints** — spec, user directives, invariants that must hold.
   - **Decisions already made** and the ones you were unsure about
     (name the alternatives you rejected).
   - **Current state** — what is built, what is verified, what is not.
   - **The exact artifact under review** — paste the diff / file slice,
     do not describe it.
   - **What you suspect you got wrong** — the single most useful line;
     without it the reviewer just re-reads your reasoning.
   Save the digest alongside the record so a later session can see what
   the reviewer was and was not shown.

## When to pick which (heuristics)

- Question phrased as "did I miss anything", "is this approach right",
  "what is the risk of this plan" → **transcript-aware route** (advisor
  on Claude Code; digest → claude or another non-host CLI elsewhere).
- Question phrased as "does this diff implement X correctly", "is this
  function free of bug Y", "does this query do what the test claims" →
  **Codex** on the exact diff or file slice (or **claude** when Codex
  is the host).
- Question phrased as "give me an independent take that does not assume
  what I just decided", "challenge the consensus", "what would another
  reviewer notice" → **Antigravity** (or **claude** when
  Antigravity is the host).
- Question is "did this command pass", "does this file parse", "does
  this regex match these examples" → **self**, with the command output
  attached.

When two roles fit one question, dispatch both in parallel and
adjudicate. Common pairs (pick equivalents from your host's external
pool):

- transcript-aware + Codex — structural soundness and diff-level
  correctness for the same milestone.
- Codex + Antigravity — implementation review with a model-diversity check.
  (Antigravity default models are Gemini-family, so pairing it with codex or claude provides a real cross-family check.)

Three-way (transcript-aware + two external CLIs from different model
families) for milestone gates at the end of a phase or before a
hard-to-reverse decision.

## Stakes ↔ route count (operational rule)

To keep an autonomous loop from over-routing (cost / latency burn) or
under-routing (skipping reviews that mattered):

- **Interior task gate** — a single task inside a phase finishing, with
  passing unit tests on its own scope. **One route is enough.** Use
  a code-focused external CLI (Codex, or claude when Codex is the host)
  on the diff for code-touching tasks; `self` for mechanical audits
  (lint exit code, schema parse, regex pass) where the rule is explicit
  and not under negotiation.
- **Phase gate** — end of a phase, or before any commit that other
  phases will build on. **Two or three routes**, including the
  transcript-aware route. Common shape: transcript-aware (structural) +
  code-focused CLI (diff-level correctness), add a third CLI from a
  different model family when you want explicit diversity to challenge
  consensus.
- **Hard-to-reverse decision** — three routes minimum, plus an
  explicit re-prediction step ("given this outcome, what do I expect
  the next step to produce?") before acting.

## Prompt construction rules

External CLIs have zero conversation context. The prompt is the entire
input. Every external-reviewer prompt has three blocks, in this order:

### 1. Background (one short paragraph)

What the agent is doing, why, what was already tried, what is being
evaluated now. Aimed at a smart reviewer who walks in cold. No jargon
that depends on prior turns.

### 2. Target (concrete artifact)

The thing being reviewed, pasted or referenced unambiguously:

- A code diff (`git diff <commit>..HEAD -- path`) pasted into the
  prompt as a fenced block.
- A file slice with absolute path + line numbers
  (`skills/.../source_plan_builder.py:445-510`), and the slice content
  itself if the reviewer cannot read the filesystem.
- A test output (last 50 lines, including the assertion that fired).
- A spec section with the headline.

Never reference "the file you saw earlier" — the reviewer did not see
anything earlier.

### 3. Question (single sharp ask)

One question that has an actionable answer. Examples:

- "Does the new `apply_semantic_border_span` correctly cover the empty
  D/E cells of the table block in row 18, or does it leave a gap?"
- "Is `nol_balance` rollforward at line 1570 free of double-counting
  when EBT is negative two periods in a row?"
- Not: "Anything to fix?" — too vague, you will get noise back.

If you need two answers, send two prompts. One question per call.

### Tone

Plain English (or Japanese — both work; match the codebase). Do not
flatter the reviewer or ask for "your honest opinion". Just ask the
question and give the context it needs.

## Answer verification protocol (the four checks)

Apply each, in order, before acting on the answer.

### 1. Grounded?

For every load-bearing claim in the answer, look for a citation: file
path, line range, test output, primary source URL, or quoted spec
fragment. If the reviewer says "this could leak" with no pointer to
where, ask one follow-up requesting the location. Do not act on
un-anchored claims.

### 2. Consistent with primary evidence?

For each cited file or line, open it and check the claim against the
actual content. If the reviewer says line 1483 does X but the file at
line 1483 does Y, the file wins. Write a short reconciliation prompt
back to the reviewer noting the contradiction (the reviewer may have
underweighted what you already saw) before adopting or rejecting.

### 3. Adjudication when reviewers disagree

If two reviewers contradict each other on the same question, identify
the tiebreaker — test exit code, spec text, user directive, source
code. Do not average opinions or pick the "more confident" tone. Quote
the tiebreaker in the decision record and move on. If no tiebreaker
exists, the question is under-specified; tighten it and re-ask.

### 4. Predictive plausibility

Given the answer, predict the outcome of the next step (the next test
run, the next eval, the next user view of the change). If you cannot,
the answer is too abstract; ask the reviewer for the concrete next
action they expect. An answer that does not let you predict the next
step is not actionable.

## Known limitations (read before Phase 2)

- **Codex sandbox posture.** `codex exec` runs with `approval=never
  sandbox=workspace-write` by default. For pure review prompts
  ("read this diff and answer X") this is exactly right and matches
  what the bootstrap (2026-05-25) confirmed works end-to-end. For
  "verify by actually running" prompts — execute a script, run a
  test, mutate a file — the no-approval sandboxed posture will
  silently degrade the review (Codex refuses the action and returns
  a hedged answer that reads as a real review but is not grounded
  in execution). Route those questions to `self` (the calling agent
  has tool access and can actually run the test) instead.
- **Claude / Antigravity print-mode posture.** `claude -p` and
  `agy -p` are one-shot print modes intended for read-and-answer
  prompts. Like Codex above, do not send them "verify by actually
  running" prompts and trust the answer — route execution questions
  to `self`. Antigravity's print mode has its own wait timeout
  (default 5m); the helper's `--timeout` still bounds the overall
  call.
- **Antigravity binary name.** The helper resolves `agy` first and
  falls back to `antigravity` if only that name is on PATH. If
  neither resolves, the route degrades to `status="error"` like any
  missing CLI.
- **Prompt length, Context Capture, and argv exposure.** No external reviewer CLI has
  unbounded context. To simplify context collection:
  - **Auto Git Context (`--include-git`)**: Recommended for live code changes. It automatically runs `git status` and `git diff HEAD`, formatting and appending them to your prompt inside a markdown block. This ensures that a cold-running reviewer has absolute clarity on your changes without any manual copy-pasting.
  - **Manual Redirection (`--prompt-file <path>`)**: If you need to include massive build logs, execution traces, or custom file extracts, read the prompt from a file or stdin (`--prompt-file -`). This removes the shell-quoting pain of multi-line text and keeps the big prompt out of the `route_review.py` argv.
  
  Note that prompt contents are **not** hidden from local processes: the reviewer CLI still receives the prompt as a child-process argv (`codex exec <prompt>`, etc.). Treat review prompts as visible to any local process list — do not paste secrets or credentials. The automatic git diff capture is limited to 1500 lines to avoid blowing up the context window.
- **Stale aliases.** Shell aliases (e.g. `codex` / `claude` aliased
  to flag-bearing forms like `--dangerously-bypass-approvals-and-sandbox`
  or `--yolo`) are not honored by `subprocess.run`; this helper
  invokes the plain forms of all four CLIs. If a route ever needs an
  alias-only flag, extend `_build_cmd` rather than relying on the
  shell alias.

## Failure handling

- `route_review.py` returns `status="error"` on timeout, missing
  binary (any `OSError` including `PermissionError`), non-zero exit,
  or output decode failure. Treat as a real review skip, not silent
  success. Retry once if the cause looks transient (rate limit, brief
  network blip); otherwise switch reviewer or record the gap.
- All non-host external CLIs unavailable: on Claude Code fall back to
  `advisor()` (still independent) and record the reduced route.
  Elsewhere no independent route remains — self is the caller re-reading
  its own work, not a review. For a **judgment** call, stop with an
  explicit **unreviewed / blocked** end state and hand back rather than
  letting self masquerade as the review; only **mechanical** checks
  (lint / schema / test exit code) may proceed on self alone. Document
  the end state in progress.md either way.
- Same reviewer disagrees with itself on rerun: the prompt is
  under-specified. Do not pick one answer. Tighten the question.
- Reviewer claims it cannot read a file or saw an empty input: the
  prompt did not include the artifact. Paste the artifact and re-ask.

## Anti-patterns (do not do these)

- **Blind adoption.** Reviewer says "rename X to Y"; you rename
  without checking call sites. Almost always wrong.
- **Blind rejection.** Reviewer surfaces a point you find
  unconvincing; you discard without testing it. Often the most
  expensive miss. Test it first, then decide.
- **Self-review masquerading.** Routing a judgement question to
  `self`. Self is for mechanical checks only.
- **Host-CLI self-review.** A Codex agent dispatching `codex exec`, a
  Claude Code agent dispatching `claude -p`, and so on. Same model family
  reviewing itself — pick from the host's external pool instead.
- **Single-route over-trust.** A single reviewer's claim is one data
  point, not a verdict. Pair routes when the stakes warrant it.
- **Silent CLI failure.** Treating `status="error"` as a pass because
  the loop has to move. The whole point of this skill is that the
  review actually happened.

## Worked example

Host: Claude Code (so `advisor()` is available and codex /
antigravity form the external pool). Milestone: finished implementing
`apply_semantic_border_span` and replaced the `_write_values` bold path
in `source_plan_builder.py`.

1. **Classify.** "Does the new helper correctly cover all table-block
   cells, including empty middle cells?" → diff-level correctness →
   **Codex** is primary. "Did I introduce a regression in the existing
   span-based design contract for non-period sheets?" → structural →
   **advisor** is primary. Dispatch both.
2. **Codex prompt** (sketch):
   - Background: "Phase 1 of an SFM workbook layout overhaul. Previously
     `_write_values` only applied table borders to a hardcoded column
     range `[label_col, *period_cols]` and skipped empty cells. We
     replaced that with `apply_semantic_border_span` driven by
     `detect_table_block`."
   - Target: paste the diff for `source_plan_builder.py` and the new
     helper.
   - Question: "For a row whose table block runs C-N with empty D and
     E, does the new code apply identical borders to D and E?"
3. **advisor**: ask the host tool — it will see this full transcript.
4. **Verify**: open `source_plan_builder.py` at the cited lines, run
   `test_build_model.py`, confirm new test for D/E coverage passes,
   reconcile any Codex/advisor disagreement against the test result.
5. **Record** the outcome in `progress.md` and continue.

## Automated Quality Gates (`--strict-gate`)

For highly automated environments or CI/CD pipelines, a raw text review is hard to act upon without human intervention. The `--strict-gate` flag transforms `route_review.py` from a passive dispatcher into an active quality gate.

When `--strict-gate` is specified:
1. The script dispatches the prompt and retrieves the reviewer's output.
2. It scans the response text for critical blocking indicators (case-insensitively):
   - `[BLOCKING]`
   - `[CRITICAL]`
   - `❌` (red cross emoji)
   - `blocking issue`
   - `critical issue`
   - `fails gate`
3. If **any** of these blocking indicators are found, even if the reviewer CLI exited with code `0` (success), `route_review.py` will:
   - Output a high-visibility warning to `stderr`: `route_review: STRICT GATE FAILED! Found blocking triggers: ...`
   - Exit with **exit code 3** (Strict Gate Failed).

This allows shell scripts and agent loops to conditionally halt or block a merge based on exit code:
```sh
python3 route_review.py --reviewer auto --host claude-code --prompt-file review_ask.txt --include-git --strict-gate
rc=$?

if [ $rc -eq 3 ]; then
    echo "Gate blocked! Resolving critical issues before proceeding."
    exit 3
elif [ $rc -ne 0 ]; then
    echo "Review failed to run or degraded (rc=$rc)."
    exit $rc
fi

echo "Gate passed!"
```
