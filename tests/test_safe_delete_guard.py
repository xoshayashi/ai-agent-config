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
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SDG = load_module()


def assert_eq(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def test_command_from_hook_reads_copilot_tool_args_json() -> None:
    command = SDG.command_from_hook(
        {
            "toolName": "bash",
            "toolArgs": '{"command":"rm -rf dist","description":"clean"}',
        }
    )
    assert_eq(command, "rm -rf dist", "copilot toolArgs command")


def test_should_block_copilot_bash_rm() -> None:
    should_block = SDG.should_block(
        {
            "toolName": "bash",
            "toolArgs": '{"command":"rm -rf dist","description":"clean"}',
        }
    )
    assert should_block is True


def test_block_output_for_copilot_uses_permission_decision() -> None:
    payload = SDG.block_output("copilot", "PreToolUse", "no rm")
    assert_eq(payload.get("permissionDecision"), "deny", "copilot decision")
    assert_eq(payload.get("permissionDecisionReason"), "no rm", "copilot reason")


def run_tests() -> int:
    tests = [
        test_command_from_hook_reads_copilot_tool_args_json,
        test_should_block_copilot_bash_rm,
        test_block_output_for_copilot_uses_permission_decision,
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
