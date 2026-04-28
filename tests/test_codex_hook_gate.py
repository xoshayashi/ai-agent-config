#!/usr/bin/env python3
"""Unit tests for hooks/scripts/codex_hook_gate.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "codex_hook_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("codex_hook_gate", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GATE = load_module()


def assert_eq(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def test_stop_routes_to_orchestrator() -> None:
    captured: list[tuple[str, str]] = []
    original_run_script = GATE.run_script
    try:
        GATE.run_script = lambda raw_input, name: captured.append((raw_input, name)) or 0
        original_stdin = sys.stdin
        original_argv = sys.argv
        try:
            sys.stdin = io.StringIO('{"hook_event_name":"Stop"}')
            sys.argv = ["codex_hook_gate.py", "--current", "codex"]
            result = GATE.main()
        finally:
            sys.stdin = original_stdin
            sys.argv = original_argv
        assert_eq(result, 0, "main return code")
    finally:
        GATE.run_script = original_run_script

    assert_eq(captured, [('{"hook_event_name":"Stop"}', "multillm_orchestrator.py")], "stop route")


def test_session_start_routes_to_orchestrator() -> None:
    captured: list[tuple[str, str]] = []
    original_run_script = GATE.run_script
    try:
        GATE.run_script = lambda raw_input, name: captured.append((raw_input, name)) or 0
        original_stdin = sys.stdin
        original_argv = sys.argv
        try:
            sys.stdin = io.StringIO('{"hook_event_name":"SessionStart"}')
            sys.argv = ["codex_hook_gate.py", "--current", "codex"]
            result = GATE.main()
        finally:
            sys.stdin = original_stdin
            sys.argv = original_argv
        assert_eq(result, 0, "main return code")
    finally:
        GATE.run_script = original_run_script

    assert_eq(captured, [('{"hook_event_name":"SessionStart"}', "multillm_orchestrator.py")], "session route")


def test_unknown_event_returns_empty_payload() -> None:
    stdout = io.StringIO()
    original_stdin = sys.stdin
    original_argv = sys.argv
    try:
        sys.stdin = io.StringIO('{"hook_event_name":"Unknown"}')
        sys.argv = ["codex_hook_gate.py", "--current", "codex"]
        with contextlib.redirect_stdout(stdout):
            result = GATE.main()
    finally:
        sys.stdin = original_stdin
        sys.argv = original_argv
    assert_eq(result, 0, "main return code")
    assert_eq(stdout.getvalue().strip(), "{}", "empty payload")


def test_run_script_passes_env_and_emits_empty_json_on_blank_stdout() -> None:
    captured: dict[str, object] = {}

    class FakeCompleted:
        returncode = 0
        stdout = ""
        stderr = ""

    original_subprocess_run = GATE.subprocess.run
    try:
        def fake_run(command, input, text, capture_output, env, check):
            captured["command"] = command
            captured["input"] = input
            captured["text"] = text
            captured["capture_output"] = capture_output
            captured["env"] = env
            captured["check"] = check
            return FakeCompleted()

        GATE.subprocess.run = fake_run
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = GATE.run_script('{"hook_event_name":"Stop"}', "multillm_orchestrator.py")
    finally:
        GATE.subprocess.run = original_subprocess_run

    assert_eq(result, 0, "run_script return code")
    assert_eq(stdout.getvalue().strip(), "{}", "blank stdout fallback")
    assert_eq(captured.get("input"), '{"hook_event_name":"Stop"}', "stdin forwarded")
    assert captured.get("env") == os.environ.copy()


def run_tests() -> int:
    tests = [
        test_stop_routes_to_orchestrator,
        test_session_start_routes_to_orchestrator,
        test_unknown_event_returns_empty_payload,
        test_run_script_passes_env_and_emits_empty_json_on_blank_stdout,
    ]

    failures = 0
    for test in tests:
        try:
            test()
        except Exception:  # pragma: no cover - script runner
            failures += 1
            print(f"FAIL: {test.__name__}", file=sys.stderr)
            traceback.print_exc()

    if failures:
        print(f"{failures} test(s) failed", file=sys.stderr)
        return 1
    print(f"ok: {len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
