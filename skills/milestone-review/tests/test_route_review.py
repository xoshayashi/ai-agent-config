#!/usr/bin/env python3
"""Contract tests for skills/milestone-review/scripts/route_review.py.

These are plain assert + print-style tests, matching the SFM skill's
test convention (no pytest fixtures). Subprocess is faked by swapping
`route_review.subprocess.run` so we exercise the wrapper logic without
ever spawning a real CLI.
"""

from __future__ import annotations

import sys
from dataclasses import is_dataclass
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import route_review  # noqa: E402


class _FakeCompleted:
    def __init__(self, *, stdout: str = "review OK", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _install_fake_run(
    captured: dict,
    *,
    completed: "_FakeCompleted | None" = None,
    raise_timeout: bool = False,
    raise_filenotfound: bool = False,
):
    import subprocess as _sp

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        captured["kwargs"] = kwargs
        if raise_timeout:
            raise _sp.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout"))
        if raise_filenotfound:
            raise FileNotFoundError("not found")
        return completed or _FakeCompleted()

    route_review.subprocess.run = fake_run
    return fake_run


def test_review_result_is_a_dataclass_with_expected_fields() -> None:
    assert is_dataclass(route_review.ReviewResult), "ReviewResult must be a dataclass"
    result = route_review.ReviewResult(
        reviewer="codex",
        status="ok",
        stdout="output",
        stderr="",
        returncode=0,
        cmd=["codex", "exec", "prompt"],
        duration_seconds=0.1,
    )
    assert result.reviewer == "codex"
    assert result.status == "ok"
    assert result.cmd == ["codex", "exec", "prompt"]
    print("ok    test_review_result_is_a_dataclass_with_expected_fields")


def test_run_reviewer_codex_invokes_codex_exec() -> None:
    captured: dict = {}
    _install_fake_run(
        captured,
        completed=_FakeCompleted(stdout="codex says hi", returncode=0),
    )
    result = route_review.run_reviewer("codex", "Please review the diff.", timeout=30)
    assert captured["cmd"][0] == "codex", f"expected first arg 'codex', got {captured['cmd']!r}"
    assert "exec" in captured["cmd"], f"missing 'exec' in {captured['cmd']!r}"
    assert "Please review the diff." in captured["cmd"], "prompt must be passed to codex"
    assert result.status == "ok"
    assert result.reviewer == "codex"
    assert result.stdout == "codex says hi"
    assert result.returncode == 0
    print("ok    test_run_reviewer_codex_invokes_codex_exec")





def test_run_reviewer_claude_invokes_claude_p() -> None:
    captured: dict = {}
    _install_fake_run(
        captured,
        completed=_FakeCompleted(stdout="claude says hi", returncode=0),
    )
    result = route_review.run_reviewer("claude", "Review please", timeout=30)
    assert captured["cmd"] == ["claude", "-p", "Review please"], (
        f"expected exact argv ['claude', '-p', <prompt>], got {captured['cmd']!r}"
    )
    assert result.status == "ok"
    assert result.reviewer == "claude"
    print("ok    test_run_reviewer_claude_invokes_claude_p")


def test_run_reviewer_antigravity_invokes_print_mode() -> None:
    """Antigravity's binary is `agy` (with `antigravity` as a PATH fallback);
    either name must be dispatched in one-shot print mode (`-p`)."""
    captured: dict = {}
    _install_fake_run(
        captured,
        completed=_FakeCompleted(stdout="antigravity says hi", returncode=0),
    )
    result = route_review.run_reviewer("antigravity", "Review please", timeout=30)
    assert captured["cmd"] in (
        ["agy", "-p", "Review please"],
        ["antigravity", "-p", "Review please"],
    ), f"expected exact argv [<agy|antigravity>, '-p', <prompt>], got {captured['cmd']!r}"
    assert result.status == "ok"
    assert result.reviewer == "antigravity"
    print("ok    test_run_reviewer_antigravity_invokes_print_mode")


def test_antigravity_binary_prefers_agy_then_falls_back() -> None:
    """Resolution order contract: `agy` when present, `antigravity` as PATH
    fallback, and `agy` again when neither resolves so the missing binary
    degrades inside subprocess handling instead of raising here."""
    original_which = route_review.shutil.which
    try:
        route_review.shutil.which = lambda name: f"/fake/{name}" if name == "agy" else None
        assert route_review._antigravity_binary() == "agy"
        route_review.shutil.which = (
            lambda name: f"/fake/{name}" if name == "antigravity" else None
        )
        assert route_review._antigravity_binary() == "antigravity"
        route_review.shutil.which = lambda name: None
        assert route_review._antigravity_binary() == "agy"
    finally:
        route_review.shutil.which = original_which
    print("ok    test_antigravity_binary_prefers_agy_then_falls_back")


def test_host_exclusion_blocks_every_host_reviewer_pair() -> None:
    """Each host's own CLI must be refused as a reviewer BEFORE any
    subprocess dispatch (host self-review is a routing bug, not a
    degradable CLI failure)."""
    pairs = [
        ("claude-code", "claude"),
        ("claude", "claude"),
        ("codex", "codex"),
        ("antigravity", "antigravity"),
    ]
    for host, reviewer in pairs:
        captured: dict = {}
        _install_fake_run(captured, completed=_FakeCompleted())
        raised = False
        try:
            route_review.run_reviewer(reviewer, "prompt", host=host)
        except ValueError as exc:
            raised = True
            msg = str(exc)
            assert "self-review" in msg.lower(), (
                f"error should name self-review for {host}/{reviewer}, got {exc!r}"
            )
            # Self-correcting contract: the blocked-route error must name at
            # least one valid reviewer so the caller re-routes in one step
            # (no re-read of SKILL.md), and must NOT suggest the blocked CLI.
            pool = route_review.external_pool_for_host(host)
            assert pool, f"host {host!r} must have a non-empty valid pool"
            assert any(r in msg for r in pool), (
                f"error for {host}/{reviewer} must name a valid reviewer from "
                f"{pool}, got {msg!r}"
            )
            assert reviewer not in pool, (
                f"blocked reviewer {reviewer!r} must not appear in the "
                f"suggested pool {pool}"
            )
        assert raised, f"host={host!r} reviewer={reviewer!r} must raise ValueError"
        assert "cmd" not in captured, (
            f"blocked dispatch must not reach subprocess for {host}/{reviewer}"
        )
    print("ok    test_host_exclusion_blocks_every_host_reviewer_pair")


def test_external_pool_for_host_excludes_only_the_host_cli() -> None:
    """The valid route pool is derived from SUPPORTED_REVIEWERS minus the
    host's own CLI, so it can never drift from the guard logic."""
    expected = {
        "claude-code": ["codex", "antigravity"],
        "claude": ["codex", "antigravity"],
        "codex": ["claude", "antigravity"],
        "antigravity": ["codex", "claude"],
    }
    for host, want in expected.items():
        got = route_review.external_pool_for_host(host)
        assert got == want, f"pool for host {host!r}: expected {want}, got {got}"
        assert route_review.HOST_BLOCKED_REVIEWER[host] not in got, (
            f"host {host!r} own CLI must be excluded from its pool"
        )
    print("ok    test_external_pool_for_host_excludes_only_the_host_cli")


def test_external_pool_for_host_rejects_unknown_host() -> None:
    raised = False
    try:
        route_review.external_pool_for_host("cursor")
    except ValueError as exc:
        raised = True
        assert "host" in str(exc).lower()
    assert raised, "unknown host must raise ValueError, not return a bogus pool"
    print("ok    test_external_pool_for_host_rejects_unknown_host")


def test_host_exclusion_allows_cross_family_dispatch() -> None:
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(stdout="hi", returncode=0))
    result = route_review.run_reviewer("antigravity", "prompt", host="codex", timeout=30)
    assert result.status == "ok", "non-host reviewer must dispatch normally"
    assert captured["cmd"] in (
        ["agy", "-p", "prompt"],
        ["antigravity", "-p", "prompt"],
    )
    print("ok    test_host_exclusion_allows_cross_family_dispatch")


def test_host_exclusion_rejects_unknown_host() -> None:
    raised = False
    try:
        route_review.run_reviewer("antigravity", "prompt", host="cursor")
    except ValueError as exc:
        raised = True
        assert "host" in str(exc).lower()
    assert raised, "unknown host must raise ValueError, not silently skip the guard"
    print("ok    test_host_exclusion_rejects_unknown_host")


def test_main_exits_nonzero_on_host_self_review() -> None:
    """CLI surface: --host <x> --reviewer <x's CLI> must exit 2 without
    dispatching, so a calling loop cannot record a review that never ran."""
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted())
    rc, _ = _run_main(
        ["--reviewer", "codex", "--host", "codex", "--prompt", "p", "--json"]
    )
    assert rc == 2, f"expected exit code 2 for blocked dispatch, got {rc!r}"
    assert "cmd" not in captured, "blocked dispatch must not reach subprocess"
    print("ok    test_main_exits_nonzero_on_host_self_review")


def _run_main(argv: list) -> "tuple[int, str]":
    """Run _main capturing BOTH streams so a passing test stays quiet: return
    (rc, stderr). stdout (the reviewer's echoed output) is swallowed, not
    returned — no test asserts on it, and letting it leak prints reviewer
    text into the test log."""
    import contextlib
    import io

    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        rc = route_review._main(argv)
    return rc, err.getvalue()


def test_main_exit_code_reflects_review_status() -> None:
    """G2: a shell loop that only checks the exit code must be able to tell a
    real review (0) from a degraded one (1: timeout / missing CLI / non-zero
    exit) without parsing --json. Routing bugs stay distinct at 2."""
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(stdout="ok", returncode=0))
    rc, _ = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p"])
    assert rc == 0, f"status='ok' review must exit 0, got {rc!r}"

    _install_fake_run(captured, completed=_FakeCompleted(stderr="boom", returncode=7))
    rc, _ = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p"])
    assert rc == 1, f"degraded (non-zero exit) review must exit 1, got {rc!r}"

    _install_fake_run(captured, raise_timeout=True)
    rc, _ = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p"])
    assert rc == 1, f"timeout review must exit 1, got {rc!r}"
    print("ok    test_main_exit_code_reflects_review_status")


def test_main_refuses_dispatch_when_host_guard_not_addressed() -> None:
    """G1/B: the host self-review guard must not be off by accident. On the
    CLI, passing neither --host nor --no-host-guard refuses to dispatch
    (exit 2, nothing run) — a forgotten flag can't permit host self-review
    even for a loop that ignores stderr. --no-host-guard is the explicit,
    auditable opt-out (warns and runs). --host runs clean."""
    # Neither flag: refuse, do not dispatch.
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    rc, err = _run_main(["--reviewer", "codex", "--prompt", "p"])
    assert rc == 2, f"missing host guard must refuse with exit 2, got {rc!r}"
    assert "cmd" not in captured, "refused dispatch must not reach subprocess"
    assert "--host" in err and "--no-host-guard" in err, (
        f"refusal must name both ways to proceed, got stderr={err!r}"
    )

    # Explicit opt-out: warns loudly but runs.
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    rc, err = _run_main(["--reviewer", "codex", "--no-host-guard", "--prompt", "p"])
    assert rc == 0, "explicit --no-host-guard must run"
    assert "WARNING" in err and "not blocked" in err.lower(), (
        f"--no-host-guard must warn the guard is off, got stderr={err!r}"
    )
    assert captured.get("cmd", [None])[0] == "codex", "opt-out still dispatches"

    # --host given: clean, no guard warning.
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    rc, err = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p"])
    assert rc == 0 and "WARNING" not in err, (
        f"--host must run clean without a guard warning, got rc={rc!r} stderr={err!r}"
    )
    print("ok    test_main_refuses_dispatch_when_host_guard_not_addressed")


def test_main_reads_prompt_from_file_and_stdin() -> None:
    """G3: --prompt-file keeps the big prompt out of THIS invocation's argv
    (length limit) and the agent's shell history, and sidesteps shell quoting
    of multi-line text. (It does NOT hide the prompt from `ps`: the reviewer
    still receives it as a child argv — see cmd below.) File and '-' (stdin)
    sources must reach the reviewer as the prompt."""
    import io
    import tempfile

    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write("multi\nline\nprompt from file")
        path = fh.name
    _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt-file", path])
    assert "multi\nline\nprompt from file" in captured["cmd"], (
        f"file prompt must be dispatched verbatim, got {captured['cmd']!r}"
    )

    # stdin via '-'
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    orig_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO("prompt from stdin")
        _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt-file", "-"])
    finally:
        sys.stdin = orig_stdin
    assert "prompt from stdin" in captured["cmd"], (
        f"stdin prompt must be dispatched, got {captured['cmd']!r}"
    )
    print("ok    test_main_reads_prompt_from_file_and_stdin")


def test_main_unreadable_prompt_file_exits_2_without_dispatch() -> None:
    """Fix C: an unreadable --prompt-file is an invocation error (nothing
    dispatched), so it exits 2 like a routing bug — the fix is the command
    line, not a re-route — and must not reach the reviewer subprocess."""
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(returncode=0))
    rc, err = _run_main(
        ["--reviewer", "codex", "--host", "claude-code",
         "--prompt-file", "/no/such/path/really.txt"]
    )
    assert rc == 2, f"unreadable --prompt-file must exit 2, got {rc!r}"
    assert "cmd" not in captured, "must not dispatch when the prompt can't be read"
    assert "prompt-file" in err.lower(), f"error must name --prompt-file, got {err!r}"
    print("ok    test_main_unreadable_prompt_file_exits_2_without_dispatch")


def test_main_requires_exactly_one_prompt_source() -> None:
    """--prompt and --prompt-file are mutually exclusive and one is required,
    so a caller cannot dispatch an empty review or an ambiguous double source."""
    import contextlib
    import io

    for argv in (
        ["--reviewer", "codex", "--host", "claude-code"],  # neither
        [  # both
            "--reviewer", "codex", "--host", "claude-code",
            "--prompt", "p", "--prompt-file", "f",
        ],
    ):
        raised = False
        try:
            # argparse prints usage to stderr on the error path; swallow it so
            # a passing test stays quiet.
            with contextlib.redirect_stderr(io.StringIO()):
                route_review._main(argv)
        except SystemExit as exc:  # argparse error path
            raised = True
            assert exc.code != 0, "prompt-source misuse must be a non-zero argparse exit"
        assert raised, f"argv {argv!r} must be rejected by argparse"
    print("ok    test_main_requires_exactly_one_prompt_source")


def test_docs_pool_table_matches_external_pool_helper() -> None:
    """G7/doc-drift: the 'Effective external pool per host' table in
    references/_reviewer_routing.md must match external_pool_for_host() for
    every host, so the doc can never advertise a pool the guard would reject."""
    from pathlib import Path

    ref = (SKILL_ROOT / "references" / "_reviewer_routing.md").read_text()
    # Each host row lists its external pool; the row must name exactly the
    # reviewers the helper allows and never the host's own blocked CLI.
    rows = {
        "Claude Code": "claude-code",
        "Codex": "codex",
        "Antigravity": "antigravity",
    }
    for label, host in rows.items():
        pool = route_review.external_pool_for_host(host)
        blocked = route_review.HOST_BLOCKED_REVIEWER[host]
        # find the table row for this host
        line = next(
            (ln for ln in ref.splitlines() if ln.strip().startswith(f"| {label} ")),
            None,
        )
        assert line is not None, f"no pool-table row found for {label!r}"
        for reviewer in pool:
            assert reviewer in line, (
                f"{label} row must list valid reviewer {reviewer!r}: {line!r}"
            )
        # the blocked CLI must not appear in the external-pool cell (last cell)
        pool_cell = line.rsplit("|", 2)[-2]
        assert blocked not in pool_cell, (
            f"{label} external-pool cell must not list its own CLI {blocked!r}: {pool_cell!r}"
        )
    print("ok    test_docs_pool_table_matches_external_pool_helper")


def test_supported_reviewers_cover_all_three_external_clis() -> None:
    """The skill is host-agnostic across Claude Code / Codex /
    Antigravity: whichever CLI is the host, the other model families must
    remain reachable as external reviewers."""
    assert set(route_review.SUPPORTED_REVIEWERS) == {
        "codex",
        "claude",
        "antigravity",
    }, f"unexpected reviewer set: {route_review.SUPPORTED_REVIEWERS!r}"
    print("ok    test_supported_reviewers_cover_all_three_external_clis")


def test_run_reviewer_returns_error_status_on_timeout() -> None:
    captured: dict = {}
    _install_fake_run(captured, raise_timeout=True)
    result = route_review.run_reviewer("codex", "prompt", timeout=1)
    assert result.status == "error", "timeout must degrade to status='error', not raise"
    assert "timeout" in (result.stderr or "").lower(), f"stderr should mention timeout, got {result.stderr!r}"
    print("ok    test_run_reviewer_returns_error_status_on_timeout")


def test_run_reviewer_returns_error_status_on_nonzero_exit() -> None:
    captured: dict = {}
    _install_fake_run(
        captured,
        completed=_FakeCompleted(stdout="", stderr="boom", returncode=2),
    )
    result = route_review.run_reviewer("codex", "prompt", timeout=30)
    assert result.status == "error", "non-zero exit must report status='error'"
    assert result.returncode == 2
    assert result.stderr == "boom"
    print("ok    test_run_reviewer_returns_error_status_on_nonzero_exit")


def test_run_reviewer_returns_error_status_on_empty_stdout() -> None:
    captured: dict = {}
    _install_fake_run(
        captured,
        completed=_FakeCompleted(stdout="   ", stderr="some warning", returncode=0),
    )
    result = route_review.run_reviewer("codex", "prompt", timeout=30)
    assert result.status == "error", "empty stdout must report status='error' even with returncode=0"
    assert "empty stdout" in result.stderr.lower()
    assert "some warning" in result.stderr
    print("ok    test_run_reviewer_returns_error_status_on_empty_stdout")


def test_run_reviewer_returns_error_status_when_cli_is_missing() -> None:
    captured: dict = {}
    _install_fake_run(captured, raise_filenotfound=True)
    result = route_review.run_reviewer("codex", "prompt", timeout=30)
    assert result.status == "error", "missing CLI must degrade, not raise"
    assert "not found" in (result.stderr or "").lower() or result.returncode != 0
    print("ok    test_run_reviewer_returns_error_status_when_cli_is_missing")


def test_run_reviewer_rejects_unknown_reviewer() -> None:
    raised = False
    try:
        route_review.run_reviewer("openai", "prompt")
    except ValueError as exc:
        raised = True
        msg = str(exc).lower()
        assert "openai" in msg or "reviewer" in msg, f"ValueError should name the bad reviewer, got {exc!r}"
    assert raised, "ValueError expected for unknown reviewer name"
    print("ok    test_run_reviewer_rejects_unknown_reviewer")


def test_run_reviewer_advisor_is_documented_as_unsupported_in_cli_router() -> None:
    """advisor / self are not external CLIs — calling run_reviewer for them must ValueError."""
    for name in ("advisor", "self"):
        raised = False
        try:
            route_review.run_reviewer(name, "prompt")
        except ValueError:
            raised = True
        assert raised, f"run_reviewer('{name}') must raise ValueError; SKILL.md handles those routes."
    print("ok    test_run_reviewer_advisor_is_documented_as_unsupported_in_cli_router")


def test_run_reviewer_returns_error_status_on_permission_error() -> None:
    """Bootstrap finding (codex 2026-05-25): catching FileNotFoundError alone
    leaves sibling OSError subclasses (PermissionError, NotADirectoryError, ...)
    propagating out and breaking the "never raises on CLI failure" contract.
    """
    captured: dict = {}
    import subprocess as _sp  # noqa: F401

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        captured["kwargs"] = kwargs
        raise PermissionError("permission denied")

    route_review.subprocess.run = fake_run
    result = route_review.run_reviewer("codex", "prompt", timeout=30)
    assert result.status == "error", "PermissionError must degrade, not raise"
    assert (
        "permission" in (result.stderr or "").lower()
        or "denied" in (result.stderr or "").lower()
        or result.returncode != 0
    ), f"stderr should hint at OS-level launch failure, got {result.stderr!r}"
    print("ok    test_run_reviewer_returns_error_status_on_permission_error")


def test_run_reviewer_returns_error_status_on_unicode_decode_error() -> None:
    """Bootstrap finding (codex + gemini 2026-05-25): with `text=True` and no
    explicit errors policy, invalid UTF-8 in the reviewer's stdout/stderr makes
    subprocess.run raise UnicodeDecodeError before completed is returned.
    """
    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        captured["kwargs"] = kwargs
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")

    route_review.subprocess.run = fake_run
    result = route_review.run_reviewer("codex", "prompt", timeout=30)
    assert result.status == "error", "UnicodeDecodeError must degrade, not raise"
    assert "decode" in (result.stderr or "").lower() or result.returncode != 0
    print("ok    test_run_reviewer_returns_error_status_on_unicode_decode_error")


def test_subprocess_run_receives_errors_replace_for_resilient_decoding() -> None:
    """Defensive UTF-8 policy: subprocess.run must be invoked with
    errors='replace' so real reviewer output never crashes the decode path
    even when the catch above is removed by a future refactor."""
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted())
    route_review.run_reviewer("codex", "p")
    assert captured["kwargs"].get("errors") == "replace", (
        f"subprocess.run must receive errors='replace', got {captured['kwargs'].get('errors')!r}"
    )
    print("ok    test_subprocess_run_receives_errors_replace_for_resilient_decoding")


def test_default_timeout_is_finite_and_reasonable() -> None:
    """A defaulted timeout exists so a stuck CLI can't hang the loop."""
    assert hasattr(route_review, "DEFAULT_TIMEOUT_SECONDS")
    assert 30 <= route_review.DEFAULT_TIMEOUT_SECONDS <= 600
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted())
    route_review.run_reviewer("codex", "p")  # no explicit timeout
    assert "timeout" in captured["kwargs"], "subprocess.run must receive timeout kwarg"
    assert captured["kwargs"]["timeout"] == route_review.DEFAULT_TIMEOUT_SECONDS
    print("ok    test_default_timeout_is_finite_and_reasonable")


def main() -> None:
    test_review_result_is_a_dataclass_with_expected_fields()
    test_run_reviewer_codex_invokes_codex_exec()
    test_run_reviewer_claude_invokes_claude_p()
    test_run_reviewer_antigravity_invokes_print_mode()
    test_antigravity_binary_prefers_agy_then_falls_back()
    test_host_exclusion_blocks_every_host_reviewer_pair()
    test_external_pool_for_host_excludes_only_the_host_cli()
    test_external_pool_for_host_rejects_unknown_host()
    test_host_exclusion_allows_cross_family_dispatch()
    test_host_exclusion_rejects_unknown_host()
    test_main_exits_nonzero_on_host_self_review()
    test_main_exit_code_reflects_review_status()
    test_main_refuses_dispatch_when_host_guard_not_addressed()
    test_main_reads_prompt_from_file_and_stdin()
    test_main_unreadable_prompt_file_exits_2_without_dispatch()
    test_main_requires_exactly_one_prompt_source()
    test_docs_pool_table_matches_external_pool_helper()
    test_supported_reviewers_cover_all_three_external_clis()
    test_run_reviewer_returns_error_status_on_timeout()
    test_run_reviewer_returns_error_status_on_nonzero_exit()
    test_run_reviewer_returns_error_status_on_empty_stdout()
    test_run_reviewer_returns_error_status_when_cli_is_missing()
    test_run_reviewer_returns_error_status_on_permission_error()
    test_run_reviewer_returns_error_status_on_unicode_decode_error()
    test_subprocess_run_receives_errors_replace_for_resilient_decoding()
    test_run_reviewer_rejects_unknown_reviewer()
    test_run_reviewer_advisor_is_documented_as_unsupported_in_cli_router()
    test_default_timeout_is_finite_and_reasonable()
    
    # New Upgraded Features (v2) Tests
    test_reviewer_availability_check()
    test_main_auto_reviewer_resolves_and_dispatches()
    test_main_auto_reviewer_failover()
    test_main_no_failover_disables_retry()
    test_git_context_capture()
    test_strict_gate_violations()
    
    print("done")


def test_reviewer_availability_check() -> None:
    original_which = route_review.shutil.which
    try:
        route_review.shutil.which = lambda name: f"/fake/{name}" if name == "codex" else None
        assert route_review.is_reviewer_available("codex") is True
        assert route_review.is_reviewer_available("claude") is False
    finally:
        route_review.shutil.which = original_which
    print("ok    test_reviewer_availability_check")


def test_main_auto_reviewer_resolves_and_dispatches() -> None:
    captured: dict = {}
    _install_fake_run(captured, completed=_FakeCompleted(stdout="review ok", returncode=0))
    original_which = route_review.shutil.which
    try:
        # Pretend only "antigravity" (agy) is installed
        route_review.shutil.which = lambda name: "/fake/agy" if name == "agy" else None
        
        # Host is claude-code, external pool is codex and antigravity.
        # Since only agy is installed, it should auto-select antigravity.
        rc, err = _run_main(["--reviewer", "auto", "--host", "claude-code", "--prompt", "p"])
        assert rc == 0, f"expected rc 0, got {rc!r}"
        assert captured["cmd"][0] in ("agy", "antigravity"), f"expected agy/antigravity command, got {captured['cmd']!r}"
    finally:
        route_review.shutil.which = original_which
    print("ok    test_main_auto_reviewer_resolves_and_dispatches")


def test_main_auto_reviewer_failover() -> None:
    original_which = route_review.shutil.which
    original_run = route_review.subprocess.run
    try:
        # Pretend both are available
        route_review.shutil.which = lambda name: f"/fake/{name}"
        
        runs = []
        def fake_run(cmd, **kwargs):
            runs.append(list(cmd))
            if cmd[0] == "codex":
                # First candidate fails with non-zero
                return _FakeCompleted(stdout="", stderr="rate limit", returncode=1)
            # Second candidate succeeds
            return _FakeCompleted(stdout="Review looks great", returncode=0)
            
        route_review.subprocess.run = fake_run
        
        # Host is claude-code, external pool is [codex, antigravity]
        rc, err = _run_main(["--reviewer", "auto", "--host", "claude-code", "--prompt", "p"])
        assert rc == 0, f"failover should succeed and exit 0, got {rc!r}"
        assert len(runs) == 2, f"should have run 2 candidates, got {runs!r}"
        assert runs[0][0] == "codex", f"first should be codex, got {runs[0]!r}"
        assert runs[1][0] in ("agy", "antigravity"), f"second should be antigravity, got {runs[1]!r}"
    finally:
        route_review.shutil.which = original_which
        route_review.subprocess.run = original_run
    print("ok    test_main_auto_reviewer_failover")


def test_main_no_failover_disables_retry() -> None:
    original_which = route_review.shutil.which
    original_run = route_review.subprocess.run
    try:
        route_review.shutil.which = lambda name: f"/fake/{name}"
        runs = []
        def fake_run(cmd, **kwargs):
            runs.append(list(cmd))
            return _FakeCompleted(stdout="", stderr="error", returncode=1)
            
        route_review.subprocess.run = fake_run
        rc, err = _run_main(["--reviewer", "auto", "--host", "claude-code", "--prompt", "p", "--no-failover"])
        assert rc == 1, f"should fail and exit 1, got {rc!r}"
        assert len(runs) == 1, "should stop after first failure when no-failover is set"
    finally:
        route_review.shutil.which = original_which
        route_review.subprocess.run = original_run
    print("ok    test_main_no_failover_disables_retry")


def test_git_context_capture() -> None:
    original_run = route_review.subprocess.run
    try:
        captured_cmds = []
        def fake_run(cmd, **kwargs):
            cmd_list = list(cmd)
            captured_cmds.append(cmd_list)
            if any("rev-parse" in arg for arg in cmd_list):
                return _FakeCompleted(stdout="true", returncode=0)
            if any("status" in arg for arg in cmd_list):
                return _FakeCompleted(stdout=" M file.py", returncode=0)
            if any("diff" in arg for arg in cmd_list):
                return _FakeCompleted(stdout="+print('hello')", returncode=0)
            # The actual reviewer run
            return _FakeCompleted(stdout="review ok", returncode=0)
            
        route_review.subprocess.run = fake_run
        
        rc, err = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p", "--include-git"])
        assert rc == 0, f"expected rc 0, got {rc!r}"
        
        reviewer_call = [c for c in captured_cmds if "codex" in c]
        assert reviewer_call, "reviewer must have been executed"
        prompt_passed = reviewer_call[0][-1]
        assert "Auto-Captured Git Context" in prompt_passed
        assert "M file.py" in prompt_passed
        assert "+print('hello')" in prompt_passed
    finally:
        route_review.subprocess.run = original_run
    print("ok    test_git_context_capture")


def test_strict_gate_violations() -> None:
    captured: dict = {}
    
    # 1. Has blocking issue -> should exit 3
    _install_fake_run(captured, completed=_FakeCompleted(stdout="This has a [BLOCKING] security issue.", returncode=0))
    rc, err = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p", "--strict-gate"])
    assert rc == 3, f"strict gate violation should exit 3, got {rc!r}"
    assert "STRICT GATE FAILED" in err
    
    # 2. No blocking issue -> should exit 0
    _install_fake_run(captured, completed=_FakeCompleted(stdout="LGTM, minor cleanup needed.", returncode=0))
    rc, err = _run_main(["--reviewer", "codex", "--host", "claude-code", "--prompt", "p", "--strict-gate"])
    assert rc == 0, f"clean review should pass strict gate, got {rc!r}"
    
    print("ok    test_strict_gate_violations")


if __name__ == "__main__":
    main()
