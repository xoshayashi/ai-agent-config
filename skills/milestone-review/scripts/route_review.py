#!/usr/bin/env python3
"""Deterministic helper to dispatch one milestone review to an external CLI.

Supported external reviewers:
- codex       → `codex exec <prompt>` (one-shot non-interactive)
- claude      → `claude -p <prompt>`  (one-shot non-interactive)
- antigravity → `agy -p <prompt>`     (print mode; falls back to the
                `antigravity` binary name if `agy` is not on PATH)

Host exclusion is enforced when the caller passes its host identity
(`--host` / `host=`): dispatching to the CLI the calling agent is running
inside raises ValueError / exits non-zero, because that is the same model
family reviewing its own work (see SKILL.md "Host awareness"). The library
`run_reviewer(host=None)` skips the guard for programmatic callers, but the
CLI (`_main`) refuses to dispatch unless you pass `--host` or the explicit
`--no-host-guard` opt-out, so the guard is never off by accident.

Features added in v2 (Ideal Milestone Upgrade):
1. **auto reviewer routing**: `--reviewer auto` detects your host and automatically selects
   the first available peer CLI on PATH that isn't your own host.
2. **failover support**: Automatically tries alternate peer CLIs in the pool if the
   primary candidate suffers a CLI launch failure, timeout, or non-zero exit, providing
   resilience against temporary API issues (can be disabled with `--no-failover`).
3. **git context capture**: `--include-git` dynamically appends `git status` and `git diff`
   to the prompt, sidestepping manual state collection by the calling agent.
4. **strict gate evaluation**: `--strict-gate` scans the reviewer output for critical blocking
   phrases (like [BLOCKING], [CRITICAL], ❌, fails gate) and exits with code 3 if any are found,
   enabling automated CI/CD style quality gates.

All failure modes (timeout, non-zero exit, missing CLI) degrade to
`ReviewResult(status="error", ...)`, never an exception, so a calling loop
can keep moving and surface the degraded result to the human in progress.md.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from typing import Sequence


SUPPORTED_REVIEWERS: tuple[str, ...] = ("codex", "claude", "antigravity")
DEFAULT_TIMEOUT_SECONDS: int = 180

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


def _build_cmd(reviewer: str, prompt: str) -> list[str]:
    if reviewer == "codex":
        return ["codex", "exec", prompt]
    if reviewer == "claude":
        return ["claude", "-p", prompt]
    if reviewer == "antigravity":
        return [_antigravity_binary(), "-p", prompt]
    raise ValueError(
        f"unknown reviewer {reviewer!r}; supported via CLI: {SUPPORTED_REVIEWERS}. "
        "advisor / self are handled by SKILL.md (not this helper)."
    )


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
    cmd = _build_cmd(reviewer, prompt)
    timeout = DEFAULT_TIMEOUT_SECONDS if timeout is None else timeout
    started = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            errors="replace",  # primary defense — never raise on invalid UTF-8 from a reviewer CLI
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return ReviewResult(
            reviewer=reviewer,
            status="error",
            stdout="",
            stderr=f"timeout after {timeout}s: {exc}",
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
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        ).stdout.strip()

        diff = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        ).stdout.strip()

        context = []
        if status:
            context.append("### Git Status\n```text\n" + status + "\n```")
        if diff:
            lines = diff.splitlines()
            if len(lines) > 1500:
                diff = "\n".join(lines[:1500]) + "\n... [TRUNCATED DUE TO SIZE LIMIT] ..."
            context.append("### Git Diff\n```diff\n" + diff + "\n```")

        if context:
            return "\n\n## Auto-Captured Git Context\n" + "\n\n".join(context)
    except Exception as exc:
        return f"\n\n[Warning: Failed to capture Git context: {exc}]"
    return ""


def check_strict_gate_violations(text: str) -> list[str]:
    """Scan review stdout for blocking annotations and return found triggers."""
    blocking_patterns = [
        (r"\[BLOCKING\]", "[BLOCKING]"),
        (r"\[CRITICAL\]", "[CRITICAL]"),
        (r"❌", "❌"),
        (r"\bblocking issue\b", "blocking issue"),
        (r"\bcritical issue\b", "critical issue"),
        (r"\bfails gate\b", "fails gate"),
    ]
    violations = []
    for pattern, label in blocking_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(label)
    return violations


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
    prompt_src = parser.add_mutually_exclusive_group(required=True)
    prompt_src.add_argument(
        "--prompt",
        help="Full review prompt as a single string (background, target, question).",
    )
    prompt_src.add_argument(
        "--prompt-file",
        help=(
            "Read the prompt from this file (use '-' for stdin) instead of "
            "--prompt. Prefer this for real diffs / logs: it sidesteps shell "
            "quoting of multi-line text, keeps the big prompt out of THIS "
            "invocation's argv (length limit) and the agent's shell history. "
            "Note: the reviewer CLI still receives the prompt as a child argv, "
            "so it is not hidden from `ps`."
        ),
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
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
            "Emit JSON of the ReviewResult to stdout instead of raw "
            "stdout/stderr. Note its `cmd` field contains the full prompt "
            "(the reviewer argv), so redirect --json output like any file that "
            "may hold the diff/log under review — do not log it to a shared "
            "channel."
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
        help="Enforce a strict quality gate: search stdout for blocking keywords (like [BLOCKING], [CRITICAL], ❌) and exit with code 3 if found."
    )
    parser.add_argument(
        "--no-failover",
        action="store_true",
        help="Disable automatic failover/retry to alternative peer CLIs in the pool if the primary candidate fails."
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

    result = None
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

    if args.json:
        json.dump(asdict(result), sys.stdout)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

    if result.status != "ok":
        return 1

    if args.strict_gate:
        violations = check_strict_gate_violations(result.stdout)
        if violations:
            sys.stderr.write(
                f"\nroute_review: STRICT GATE FAILED! Found blocking triggers: {', '.join(violations)}\n"
            )
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
