#!/usr/bin/env python3
"""Unit tests for hooks/scripts/safe_delete_guard.py."""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "safe_delete_guard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("safe_delete_guard", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - import safety
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SDG = load_module()


def assert_eq(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def test_should_block_bash_rm() -> None:
    payload = {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}}
    assert SDG.should_block(payload) is True


def test_should_block_absolute_rm_path() -> None:
    payload = {"tool_name": "run_shell_command", "tool_input": {"cmd": "/bin/rm -f tmp.txt"}}
    assert SDG.should_block(payload) is True


def test_should_not_block_safe_command() -> None:
    payload = {"tool_name": "Bash", "tool_input": {"command": "trash build"}}
    assert SDG.should_block(payload) is False


def test_should_not_block_non_shell_tool() -> None:
    payload = {"tool_name": "Read", "tool_input": {"file_path": "build/output.txt"}}
    assert SDG.should_block(payload) is False


def test_block_output_shapes() -> None:
    codex_payload = SDG.block_output("codex", "PreToolUse", "nope")
    gemini_payload = SDG.block_output("gemini", "BeforeTool", "nope")
    assert_eq(
        codex_payload["hookSpecificOutput"]["permissionDecision"],
        "deny",
        "codex deny shape",
    )
    assert_eq(gemini_payload["decision"], "deny", "gemini deny shape")


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    failures: list[tuple[str, BaseException, str]] = []
    for test in tests:
        try:
            test()
        except BaseException as exc:  # pragma: no cover - direct-run reporting
            failures.append((test.__name__, exc, traceback.format_exc()))

    if failures:
        for name, exc, tb in failures:
            print(f"FAIL {name}: {exc}", file=sys.stderr)
            print(tb, file=sys.stderr)
        print(f"{len(failures)} test(s) failed", file=sys.stderr)
        return 1

    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
