#!/usr/bin/env python3
"""Deterministic helper to dispatch one milestone review to an external CLI.

Supported external reviewers:
- codex       → `codex exec --skip-git-repo-check -` (prompt via stdin)
- claude      → `claude -p` in isolated one-shot mode (prompt via stdin)
- antigravity → `agy -p <prompt> --print-timeout <t>s` (falls back to the
                `antigravity` binary name if `agy` is not on PATH)

Host exclusion is enforced when the caller passes its host identity
(`--host` / `host=`): dispatching to the CLI the calling agent is running
inside raises ValueError / exits non-zero, because that is the same model
family reviewing its own work (see SKILL.md "Host awareness"). The library
`run_reviewer(host=None)` skips the guard for programmatic callers, but the
CLI (`_main`) refuses to dispatch unless you pass `--host` or the explicit
`--no-host-guard` opt-out, so the guard is never off by accident.

Dispatch design (v3) — every choice below is measured, not guessed
(2026-07-12 bench, macOS, all three CLIs live):

1. **Realistic timeout.** The old 180s default caused a real incident: a
   claude review of a large digest timed out and the milestone silently
   degraded to a single-family review. A trivial `claude -p` round trip is
   ~4s, a trivial `agy -p` round trip is ~41s, and a real review of a
   1000+-line diff on a heavyweight default model takes minutes. Default is
   now 600s per attempt; lower it explicitly for quick mechanical checks.
2. **Isolated claude startup.** `claude -p` is dispatched with
   `--strict-mcp-config --mcp-config '{"mcpServers":{}}' --setting-sources ""`
   so the review does not pay for (or hang on) the host user's MCP servers,
   plugins, and hooks. A review prompt is self-contained by contract
   (SKILL.md prompt rules), so the reviewer needs no MCP tools.
3. **codex outside git repos.** `codex exec` hard-refuses to run outside a
   trusted git repository unless `--skip-git-repo-check` is passed (measured:
   rc=1 in 0.1s). Reviews are read-and-answer, so the flag is safe and the
   route now works from non-repo working directories.
4. **agy's internal wait.** `agy -p` has its own print-mode wait (default
   5m) that silently caps long reviews below our timeout. The helper now
   passes `--print-timeout` matching `--timeout` so there is one effective
   timeout, ours.
5. **Prompt via stdin** for codex and claude (agy has no stdin prompt mode).
   This removes the argv length ceiling for big diffs and keeps the prompt
   out of `ps` for those two routes.
6. **Preflight (`--doctor`).** Measures a trivial round trip through every
   reviewer in the host's pool and reports per-route status + seconds, so a
   dead or slow route is discovered before a milestone depends on it.

All failure modes (timeout, non-zero exit, missing CLI) degrade to
`ReviewResult(status="error", ...)`, never an exception, so a calling loop
can keep moving and surface the degraded result to the human in progress.md.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from typing import Sequence


SUPPORTED_REVIEWERS: tuple[str, ...] = ("codex", "claude", "antigravity")
# Per-attempt ceiling. Sized from measurement (see module docstring): trivial
# round trips are 4s (claude) / 41s (agy); real reviews on heavyweight default
# models run minutes. 600s clears the observed 180s-timeout incident with >3x
# headroom while still bounding a two-candidate failover at 20 minutes.
DEFAULT_TIMEOUT_SECONDS: int = 600
# Doctor probes ask for a two-letter answer; 120s is ~3x the slowest measured
# trivial round trip (agy, 41s).
DOCTOR_TIMEOUT_SECONDS: int = 120
DOCTOR_PROMPT: str = "Reply with exactly: OK"

# Host-CLI session markers that must not leak into a reviewer child process:
# a nested CLI that sees them may change behavior (or refuse to run).
SCRUBBED_ENV_VARS: tuple[str, ...] = (
    "CLAUDECODE",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_SSE_PORT",
)

# Blocking markers for --strict-gate. Deliberately only unambiguous,
# opt-in annotations: free-text phrases like "blocking issue" false-positive
# on negations ("no blocking issue found"). The gate only works if the
# reviewer uses the markers, so --strict-gate appends the instruction below
# to the prompt itself — guaranteed by construction, not by the caller
# remembering to write it.
STRICT_GATE_MARKERS: tuple[str, ...] = ("[BLOCKING]", "[CRITICAL]", "❌")
STRICT_GATE_PROMPT_SUFFIX: str = (
    "\n\nGate instruction: this review is an automated quality gate. Tag "
    "every finding that must block the milestone inline with [BLOCKING] "
    "(use [CRITICAL] for severity-critical findings). If nothing blocks, "
    "do not use these markers anywhere in your answer."
)

# Host identity → the external reviewer that would be self-review from it.
# "claude" is accepted as an alias for "claude-code" so agents can pass
# whichever spelling their host reports.
HOST_BLOCKED_REVIEWER: dict[str, str] = {
    "claude-code": "claude",
    "claude": "claude",
    "codex": "codex",
    "antigravity": "antigravity",
}
SUPPORTED_HOSTS: tuple[str, ...] = tuple(HOST_BLOCKED_REVIEWER)


def external_pool_for_host(host: str) -> list[str]:
    """Reviewers that are NOT host self-review — the valid route pool.

    Derived from ``SUPPORTED_REVIEWERS`` minus the host's own CLI so it can
    never drift from the guard or from the "Effective external pool per host"
    table in ``references/_reviewer_routing.md``. Callers and error messages
    use this to re-route in one step instead of re-reading SKILL.md.
    """
    normalized = host.strip().lower()
    if normalized not in HOST_BLOCKED_REVIEWER:
        raise ValueError(
            f"unknown host {host!r}; supported: {SUPPORTED_HOSTS}. "
            "Pass the CLI the calling agent runs inside."
        )
    blocked = HOST_BLOCKED_REVIEWER[normalized]
    return [reviewer for reviewer in SUPPORTED_REVIEWERS if reviewer != blocked]


@dataclass
class ReviewResult:
    reviewer: str
    status: str  # "ok" | "error"
    stdout: str
    stderr: str
    returncode: int
    cmd: list[str]
    duration_seconds: float


def is_reviewer_available(reviewer: str) -> bool:
    """Check if the required CLI binary for the reviewer is present on PATH."""
    if reviewer == "codex":
        return shutil.which("codex") is not None
    if reviewer == "claude":
        return shutil.which("claude") is not None
    if reviewer == "antigravity":
        return shutil.which("agy") is not None or shutil.which("antigravity") is not None
    return False


def _antigravity_binary() -> str:
    """Antigravity ships its CLI as `agy`; some installs expose `antigravity`.

    Resolution failure is not an error here — returning the preferred name
    lets subprocess degrade to ReviewResult(status="error") like any other
    missing CLI, preserving the never-raises contract.
    """
    for candidate in ("agy", "antigravity"):
        if shutil.which(candidate):
            return candidate
    return "agy"


def _build_dispatch(
    reviewer: str, prompt: str, timeout: float
) -> "tuple[list[str], str | None]":
    """Return (argv, stdin_payload) for one reviewer dispatch.

    stdin_payload is the prompt for CLIs that read it from stdin (codex,
    claude) and None for CLIs that only take it as argv (antigravity).
    Rationale for each flag is in the module docstring ("Dispatch design").
    """
    if reviewer == "codex":
        return ["codex", "exec", "--skip-git-repo-check", "-"], prompt
    if reviewer == "claude":
        return [
            "claude",
            "-p",
            "--strict-mcp-config",
            "--mcp-config",
            '{"mcpServers":{}}',
            "--setting-sources",
            "",
        ], prompt
    if reviewer == "antigravity":
        # agy's internal wait starts after process launch, so an equal value
        # could never fire before our subprocess kill. Give agy a 30s head
        # start (for timeouts that can afford it): it then gives up first
        # with its own error — a timeout stays distinguishable from a review.
        wait = math.ceil(timeout) - 30 if timeout > 60 else math.ceil(timeout)
        return [
            _antigravity_binary(),
            "-p",
            prompt,
            "--print-timeout",
            f"{max(1, wait)}s",
        ], None
    raise ValueError(
        f"unknown reviewer {reviewer!r}; supported via CLI: {SUPPORTED_REVIEWERS}. "
        "advisor / self are handled by SKILL.md (not this helper)."
    )


def _child_env() -> dict:
    """Reviewer child env: the caller's env minus host-session markers."""
    return {k: v for k, v in os.environ.items() if k not in SCRUBBED_ENV_VARS}


def check_host_exclusion(reviewer: str, host: "str | None") -> None:
    """Raise ValueError when ``reviewer`` is the CLI ``host`` runs inside.

    Same model family reviewing its own work is self-review in disguise;
    treat it like an unknown reviewer name — a routing bug the caller must
    fix, not a degradable CLI failure.
    """
    if host is None:
        return
    normalized = host.strip().lower()
    if normalized not in HOST_BLOCKED_REVIEWER:
        raise ValueError(
            f"unknown host {host!r}; supported: {SUPPORTED_HOSTS}. "
            "Pass the CLI the calling agent runs inside."
        )
    if HOST_BLOCKED_REVIEWER[normalized] == reviewer:
        # Self-correcting error: name the valid pool inline so the caller
        # re-routes in one step instead of paying a re-read-SKILL round trip.
        # This still raises (routing bug, not a degradable CLI failure) — it
        # attaches the answer to the error, it does not auto-pick.
        pool = external_pool_for_host(normalized)
        raise ValueError(
            f"host self-review blocked: host {host!r} must not dispatch to "
            f"reviewer {reviewer!r} (same model family reviewing its own "
            f"work). Pick one of: {', '.join(pool)} — see SKILL.md "
            "'Host awareness'."
        )


def run_reviewer(
    reviewer: str,
    prompt: str,
    *,
    timeout: float | int | None = None,
    host: "str | None" = None,
) -> ReviewResult:
    """Run an external CLI reviewer with ``prompt`` and return a ReviewResult.

    Never raises on subprocess failure modes (timeout, non-zero exit,
    missing binary). Raises ``ValueError`` only for routing bugs — unknown
    reviewer names, unknown hosts, or a host-self-review dispatch — so the
    caller fails fast rather than silently routing nowhere.
    """
    check_host_exclusion(reviewer, host)
    timeout = DEFAULT_TIMEOUT_SECONDS if timeout is None else timeout
    cmd, stdin_payload = _build_dispatch(reviewer, prompt, timeout)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            input=stdin_payload,
            stdin=subprocess.DEVNULL if stdin_payload is None else None,
            capture_output=True,
            text=True,
            errors="replace",  # primary defense — never raise on invalid UTF-8 from a reviewer CLI
            timeout=timeout,
            env=_child_env(),
        )
    except subprocess.TimeoutExpired as exc:
        # Keep whatever the reviewer managed to say: partial output is the
        # difference between "dead route" and "route needs a longer timeout"
        # when a human audits the degraded milestone.
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", "replace")
        return ReviewResult(
            reviewer=reviewer,
            status="error",
            stdout=partial,
            stderr=(
                f"timeout after {timeout}s"
                + (f" (partial stdout kept, {len(partial)} chars)" if partial else "")
            ),
            returncode=-1,
            cmd=cmd,
            duration_seconds=time.monotonic() - started,
        )
    except OSError as exc:
        # FileNotFoundError, PermissionError, NotADirectoryError, and other
        # OS-level launch failures all live here. FileNotFoundError is one
        # OSError subclass — catching only it lets siblings propagate and
        # break the "never raises on CLI failure" contract.
        return ReviewResult(
            reviewer=reviewer,
            status="error",
            stdout="",
            stderr=f"CLI launch failed: {exc}",
            returncode=-1,
            cmd=cmd,
            duration_seconds=time.monotonic() - started,
        )
    except UnicodeDecodeError as exc:
        # Belt-and-suspenders for the errors="replace" defense above. The
        # decode path inside subprocess.run is the documented contract here;
        # this catch protects callers that monkeypatch subprocess.run away
        # (tests) or that disable errors="replace" in a future refactor.
        return ReviewResult(
            reviewer=reviewer,
            status="error",
            stdout="",
            stderr=f"output decode failed: {exc}",
            returncode=-1,
            cmd=cmd,
            duration_seconds=time.monotonic() - started,
        )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode == 0 and not stdout.strip():
        status = "error"
        stderr = "Reviewer returned empty stdout." + (f" Stderr: {stderr}" if stderr.strip() else "")
    else:
        status = "ok" if completed.returncode == 0 else "error"

    return ReviewResult(
        reviewer=reviewer,
        status=status,
        stdout=stdout,
        stderr=stderr,
        returncode=completed.returncode,
        cmd=cmd,
        duration_seconds=time.monotonic() - started,
    )


def get_git_context() -> str:
    """Retrieve git status and diff HEAD, formatting them as a markdown context block."""
    try:
        # Check if inside git repo
        is_git = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if is_git.returncode != 0 or is_git.stdout.strip() != "true":
            return ""

        status = subprocess.run(
            ["git", "-c", "core.quotePath=false", "status", "--porcelain"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        ).stdout.strip()

        diff_runs = []
        diff = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        ).stdout.strip()
        if diff:
            diff_runs.append(diff)

        # Enumerate ALL untracked files accurately (resolves directory collapsing and non-ASCII quoting)
        untracked_files_out = subprocess.run(
            ["git", "-c", "core.quotePath=false", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        ).stdout.strip()

        if untracked_files_out:
            for line in untracked_files_out.splitlines():
                path = line.strip()
                if not path:
                    continue
                # Run git diff --no-index /dev/null <path> to capture its entire content as an added file diff
                untracked_diff = subprocess.run(
                    ["git", "diff", "--no-index", "--", "/dev/null", path],
                    capture_output=True,
                    text=True,
                    errors="replace",
                    timeout=10,
                ).stdout.strip()
                if untracked_diff:
                    diff_runs.append(untracked_diff)

        combined_diff = "\n\n".join(diff_runs)

        context = []
        if status:
            context.append("### Git Status\n```text\n" + status + "\n```")
        if combined_diff:
            lines = combined_diff.splitlines()
            if len(lines) > 1500:
                combined_diff = "\n".join(lines[:1500]) + "\n... [TRUNCATED DUE TO SIZE LIMIT] ..."
            context.append("### Git Diff\n```diff\n" + combined_diff + "\n```")

        if context:
            return "\n\n## Auto-Captured Git Context\n" + "\n\n".join(context)
    except Exception as exc:
        return f"\n\n[Warning: Failed to capture Git context: {exc}]"
    return ""


def check_strict_gate_violations(text: str) -> list[str]:
    """Scan review stdout for blocking annotations and return found triggers.

    Only the opt-in markers in STRICT_GATE_MARKERS count. Free-text phrases
    are deliberately excluded: "blocking issue" would fire on "no blocking
    issue found" and turn a clean review into a false gate failure.
    """
    violations = []
    for marker in STRICT_GATE_MARKERS:
        if re.search(re.escape(marker), text, re.IGNORECASE):
            violations.append(marker)
    return violations


def _attempt_summary(result: ReviewResult) -> dict:
    """Compact per-attempt record for --json output and the doctor report."""
    return {
        "reviewer": result.reviewer,
        "status": result.status,
        "returncode": result.returncode,
        "duration_seconds": round(result.duration_seconds, 1),
        "stderr_tail": (result.stderr or "")[-200:],
    }


def _run_doctor(candidates: "list[str]", timeout: float, as_json: bool) -> int:
    """Probe every candidate with a trivial prompt and report measured health.

    Exit 0 when at least one route answered (a review can run), 1 when the
    whole pool is dead. Probes run sequentially so per-route seconds are not
    distorted by each other.
    """
    probes = []
    for candidate in candidates:
        if not is_reviewer_available(candidate):
            probes.append(
                {
                    "reviewer": candidate,
                    "status": "error",
                    "returncode": -1,
                    "duration_seconds": 0.0,
                    "stderr_tail": "binary not found on PATH",
                }
            )
            continue
        result = run_reviewer(candidate, DOCTOR_PROMPT, timeout=timeout)
        summary = _attempt_summary(result)
        # Challenge-response: an exit-0 route that did not actually consume
        # the prompt (e.g. a CLI that stopped reading stdin) must not be
        # reported healthy — check the answer, not just the exit code.
        if result.status == "ok" and "OK" not in result.stdout:
            summary["status"] = "error"
            summary["stderr_tail"] = (
                "probe answered unexpectedly (route may not be reading the "
                f"prompt): {result.stdout.strip()[:80]!r}"
            )
        probes.append(summary)
    if as_json:
        json.dump({"doctor": probes}, sys.stdout)
        sys.stdout.write("\n")
    else:
        for probe in probes:
            sys.stdout.write(
                f"{probe['reviewer']:<12} {probe['status']:<6} "
                f"{probe['duration_seconds']:>6.1f}s  "
                f"{probe['stderr_tail'] if probe['status'] != 'ok' else ''}\n".rstrip()
                + "\n"
            )
    return 0 if any(p["status"] == "ok" for p in probes) else 1


def _main(argv: "Sequence[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dispatch a milestone review to one external CLI reviewer."
    )
    parser.add_argument(
        "--reviewer",
        default="auto",
        choices=SUPPORTED_REVIEWERS + ("auto",),
        help=(
            "The external CLI reviewer to dispatch to. Default is 'auto', "
            "which resolves and dispatches to the first available peer CLI on PATH "
            "that is compatible with your host (not self-review)."
        ),
    )
    prompt_src = parser.add_mutually_exclusive_group(required=False)
    prompt_src.add_argument(
        "--prompt",
        help="Full review prompt as a single string (background, target, question).",
    )
    prompt_src.add_argument(
        "--prompt-file",
        help=(
            "Read the prompt from this file (use '-' for stdin) instead of "
            "--prompt. Prefer this for real diffs / logs: it sidesteps shell "
            "quoting of multi-line text and keeps the big prompt out of argv "
            "and shell history. codex/claude then receive it via their stdin "
            "(not visible in `ps`); antigravity still gets it as a child argv."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "Per-attempt ceiling in seconds (default "
            f"{DEFAULT_TIMEOUT_SECONDS}). Sized for real reviews on "
            "heavyweight models; lower it for quick mechanical checks. "
            "Also forwarded to antigravity's --print-timeout."
        ),
    )
    parser.add_argument(
        "--host",
        choices=SUPPORTED_HOSTS,
        default=None,
        help=(
            "CLI the calling agent runs inside. Always pass it: dispatching "
            "to your own host CLI is blocked as self-review (exit 2). Without "
            "--host (and without --no-host-guard) the CLI refuses to dispatch "
            "(exit 2), so the guard is never off by accident."
        ),
    )
    parser.add_argument(
        "--no-host-guard",
        action="store_true",
        help=(
            "Explicitly run WITHOUT the host self-review guard (for a "
            "programmatic one-off call that has no host to declare). Prefer "
            "--host. Without either flag the CLI refuses to dispatch, so the "
            "guard can never be off by accident."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Emit JSON of the ReviewResult (plus an `attempts` failover "
            "trace) to stdout instead of raw stdout/stderr. The antigravity "
            "route's `cmd` field contains the full prompt, so redirect "
            "--json output like any file that may hold the diff/log under "
            "review — do not log it to a shared channel."
        ),
    )
    parser.add_argument(
        "--include-git",
        action="store_true",
        help="Automatically capture `git status` and `git diff HEAD` and append them to the prompt context."
    )
    parser.add_argument(
        "--strict-gate",
        action="store_true",
        help=(
            "Enforce a strict quality gate: search every attempt's stdout "
            "(including partial output from a timed-out attempt) for the "
            f"blocking markers {', '.join(STRICT_GATE_MARKERS)} and exit 3 "
            "if found. Instruct the reviewer in the prompt to tag real "
            "blockers with [BLOCKING] so the gate has something unambiguous "
            "to match."
        ),
    )
    parser.add_argument(
        "--no-failover",
        action="store_true",
        help="Disable automatic failover/retry to alternative peer CLIs in the pool if the primary candidate fails."
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help=(
            "Preflight: probe every reviewer in the host's pool with a "
            "trivial prompt and report measured status + seconds per route "
            f"(probe timeout {DOCTOR_TIMEOUT_SECONDS}s unless --timeout is "
            "lowered below it). Exit 0 if at least one route answers, 1 if "
            "the pool is dead. Run it before the first milestone of a "
            "session, or after any route degraded."
        ),
    )
    args = parser.parse_args(argv)

    # G1/B: the host self-review guard is what this skill exists to enforce, so
    # it must not be off by accident. On the CLI, refuse to dispatch unless the
    # caller either declares --host (guard active) or explicitly opts out with
    # --no-host-guard (auditable). A forgotten flag no longer silently permits
    # host self-review even for a loop that ignores stderr. (The library
    # run_reviewer still accepts host=None for programmatic callers.)
    if args.host is None and not args.no_host_guard:
        sys.stderr.write(
            "route_review: refusing to dispatch with the host self-review "
            "guard silently off. Pass --host="
            "<claude-code|codex|antigravity> to enable it, or "
            "--no-host-guard to run without it on purpose.\n"
        )
        return 2
    if args.host is None:  # --no-host-guard was given
        sys.stderr.write(
            "route_review: WARNING running with --no-host-guard; host "
            "self-review is NOT blocked for this dispatch.\n"
        )

    # Determine pool of candidates
    if args.reviewer == "auto":
        if args.host is None:
            # We are running with --no-host-guard, so any supported reviewer is valid
            candidates = list(SUPPORTED_REVIEWERS)
        else:
            candidates = external_pool_for_host(args.host)
    else:
        candidates = [args.reviewer]

    # Reorder candidates: prioritize available binaries
    if args.reviewer == "auto":
        available_candidates = [c for c in candidates if is_reviewer_available(c)]
        unavailable_candidates = [c for c in candidates if not is_reviewer_available(c)]
        candidates = available_candidates + unavailable_candidates
        if not candidates:
            sys.stderr.write("route_review: no valid reviewers available in pool.\n")
            return 2

    if args.doctor:
        # --doctor never dispatches a review, so any review-shaping flag on
        # the same invocation is a caller mistake that must fail loudly: a
        # wrapper that runs `--doctor --strict-gate && record_pass` would
        # otherwise record a gate pass for a run that gated nothing.
        conflicting = [
            name
            for name, given in (
                ("--prompt", args.prompt is not None),
                ("--prompt-file", args.prompt_file is not None),
                ("--strict-gate", args.strict_gate),
                ("--include-git", args.include_git),
                ("--no-failover", args.no_failover),
            )
            if given
        ]
        if conflicting:
            sys.stderr.write(
                "route_review: --doctor probes routes and never dispatches "
                f"a review; drop {', '.join(conflicting)}.\n"
            )
            return 2
        # --timeout below the doctor default tightens the probe; the doctor
        # default itself stays small so a hung route fails fast.
        probe_timeout = min(args.timeout, DOCTOR_TIMEOUT_SECONDS)
        # Skip candidates the guard would block (auto pools are pre-filtered;
        # an explicit --reviewer is validated like a normal dispatch).
        for candidate in candidates:
            try:
                check_host_exclusion(candidate, args.host)
            except ValueError as exc:
                sys.stderr.write(f"route_review: {exc}\n")
                return 2
        return _run_doctor(candidates, probe_timeout, args.json)

    if args.prompt is None and args.prompt_file is None:
        parser.error("one of --prompt / --prompt-file is required (or --doctor)")

    if args.prompt_file is not None:
        try:
            if args.prompt_file == "-":
                prompt = sys.stdin.read()
            else:
                with open(args.prompt_file, "r", errors="replace") as fh:
                    prompt = fh.read()
        except OSError as exc:
            # exit 2 = invocation error, nothing dispatched (same bucket as a
            # routing bug): the fix is the command line, not a re-route.
            sys.stderr.write(f"route_review: cannot read --prompt-file: {exc}\n")
            return 2
    else:
        prompt = args.prompt

    # Append git context if requested
    if args.include_git:
        git_ctx = get_git_context()
        if git_ctx:
            prompt += git_ctx

    # The gate's precondition (reviewer knows the markers) is guaranteed by
    # construction: the instruction rides with the prompt itself.
    if args.strict_gate:
        prompt += STRICT_GATE_PROMPT_SUFFIX

    result = None
    all_results: list[ReviewResult] = []
    attempts: list[dict] = []
    run_candidates = list(candidates)

    for i, candidate in enumerate(run_candidates):
        try:
            check_host_exclusion(candidate, args.host)
        except ValueError as exc:
            # If explicit reviewer failed host exclusion, fail loud (exit 2)
            if args.reviewer != "auto":
                sys.stderr.write(f"route_review: {exc}\n")
                return 2
            # For auto, just skip this candidate
            continue

        sys.stderr.write(f"route_review: attempting dispatch to reviewer {candidate!r}...\n")

        try:
            result = run_reviewer(
                candidate, prompt, timeout=args.timeout, host=args.host
            )
        except ValueError as exc:
            sys.stderr.write(f"route_review: {exc}\n")
            return 2

        all_results.append(result)
        attempts.append(_attempt_summary(result))
        if result.status == "ok":
            sys.stderr.write(f"route_review: successfully received review from {candidate!r}.\n")
            break
        else:
            sys.stderr.write(f"route_review: reviewer {candidate!r} failed/degraded: {result.stderr or 'Unknown error'}\n")

            if args.no_failover:
                sys.stderr.write("route_review: failover is disabled. Stopping.\n")
                break
            if i < len(run_candidates) - 1:
                sys.stderr.write("route_review: attempting failover to next candidate...\n")
                continue

    if result is None:
        sys.stderr.write("route_review: no reviewer could be executed.\n")
        return 1

    # One greppable line per dispatch: a caller that ignores --json and
    # per-attempt chatter can still not mistake a failover for a clean
    # primary run (external review 2026-07-12: exit code + attempts trace
    # must together make reduced independence visible, not --json alone).
    if len(attempts) > 1:
        sys.stderr.write(
            "route_review: attempts: "
            + ", ".join(f"{a['reviewer']}={a['status']}" for a in attempts)
            + "\n"
        )

    if args.json:
        payload = asdict(result)
        payload["attempts"] = attempts
        json.dump(payload, sys.stdout)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

    if result.status != "ok":
        return 1

    if args.strict_gate:
        # Scan EVERY attempt's stdout, including partial output a timed-out
        # reviewer managed to emit: a [BLOCKING] from a truncated review is a
        # human-must-look signal, and only the fail-closed reading keeps a
        # clean fallback from laundering it (external review 2026-07-12).
        violations: list[str] = []
        for attempted in all_results:
            for marker in check_strict_gate_violations(attempted.stdout):
                if marker not in violations:
                    violations.append(marker)
        if violations:
            sys.stderr.write(
                f"\nroute_review: STRICT GATE FAILED! Found blocking triggers: {', '.join(violations)}\n"
            )
            return 3

    if any(attempted.status != "ok" for attempted in all_results):
        # Review ran, but only after one or more routes degraded. Exit 4 is
        # the documented "reviewed via failover" state: distinguishable from
        # a clean 0 by exit code alone, while still distinct from 1 (no
        # review happened). Loops that treat nonzero as failure fail closed.
        sys.stderr.write(
            "route_review: NOTE review succeeded via failover; record the "
            "failed route(s) as degraded in the milestone log (exit 4).\n"
        )
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
