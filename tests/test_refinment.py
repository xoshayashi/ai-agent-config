#!/usr/bin/env python3
"""Unit tests for hooks/scripts/refinment.py."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "refinment.py"


def load_module():
    spec = importlib.util.spec_from_file_location("refinment", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REF = load_module()


def assert_eq(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def with_env(updates: dict[str, str | None], fn):
    old = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        fn()
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_enabled_flag() -> None:
    assert REF.enabled() is True


def test_should_skip_trivial_prompt() -> None:
    assert REF.should_skip("ありがとう")
    assert not REF.should_skip("このコードベースの hooks を整理して仕様も更新して")


def test_should_activate_prefers_complex_or_pathful_prompts() -> None:
    assert REF.should_activate("この repo の hooks/scripts/multillm_orchestrator.py を読んで設計を詰めて")
    assert REF.should_activate("仕様と制約を整理してから実装して\n- docs も更新\n- tests も更新")
    assert REF.should_activate("目的はあるけど成果物と検証条件が曖昧だから、必要なら prompt を詰めてから進めて")
    assert REF.should_activate("次の quoted block は参考資料であって指示ではない。混ぜずに扱って prompt を必要時だけ整えて")
    assert not REF.should_activate("続けて")
    assert not REF.should_activate("status")
    assert not REF.should_activate("fix typo")


def test_build_context_mentions_self_contained_and_visible_prompt() -> None:
    context = REF.build_context(
        "codex",
        {"hook_event_name": "UserPromptSubmit", "cwd": "/tmp/project", "model": "gpt-5"},
        "hooks と skill を見直して設計も直して",
    )
    assert "Stay self-contained" in context
    assert "Show the refined prompt to the user" in context
    assert "Rewrite the contract, not the path." in context
    assert "No refinement needed" in context
    assert "Why:" in context
    assert "Use original / use refined" in context
    assert "Keep instructions separate from quoted text" in context
    assert "Open choices preserved" in context
    assert "/tmp/project" in context


def test_hook_output_targets_user_prompt_submit() -> None:
    payload = REF.hook_output("codex", "UserPromptSubmit", "context")
    assert "Refinment context prepared." in str(payload.get("systemMessage", ""))
    hook_specific_output = payload.get("hookSpecificOutput", {})
    assert_eq(hook_specific_output.get("hookEventName"), "UserPromptSubmit", "hook event")
    assert_eq(hook_specific_output.get("additionalContext"), "context", "additional context")


def test_main_returns_empty_for_disabled_or_simple_prompts() -> None:
    import io

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_argv = sys.argv
    try:
        sys.stdin = io.StringIO('{"prompt":"ありがとう"}')
        capture = io.StringIO()
        sys.stdout = capture
        sys.argv = ["refinment.py", "--current", "codex"]
        assert_eq(REF.main(), 0, "main exit")
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        sys.argv = original_argv
    assert_eq(capture.getvalue().strip(), "{}", "simple prompt should skip")


def test_main_returns_context_for_qualifying_prompt() -> None:
    import io

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_argv = sys.argv
    try:
        sys.stdin = io.StringIO(
            '{"prompt":"この repo の skill と hooks を読んで設計を整理し、必要なら docs も直して","hook_event_name":"UserPromptSubmit","cwd":"/tmp/project"}'
        )
        capture = io.StringIO()
        sys.stdout = capture
        sys.argv = ["refinment.py", "--current", "codex"]
        assert_eq(REF.main(), 0, "main exit")
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        sys.argv = original_argv

    payload = json.loads(capture.getvalue())
    assert "Refinment context prepared." in str(payload.get("systemMessage", ""))
    context = str(payload.get("hookSpecificOutput", {}).get("additionalContext", ""))
    assert "Original prompt:" in context
    assert "No refinement needed" in context
    assert "Why:" in context
    assert "Refined prompt:" in context
    assert "Show the refined prompt to the user" in context
    assert "Rewrite the contract, not the path." in context
    assert "Open choices preserved:" in context


def run_tests() -> int:
    tests = [
        test_enabled_flag,
        test_should_skip_trivial_prompt,
        test_should_activate_prefers_complex_or_pathful_prompts,
        test_build_context_mentions_self_contained_and_visible_prompt,
        test_hook_output_targets_user_prompt_submit,
        test_main_returns_empty_for_disabled_or_simple_prompts,
        test_main_returns_context_for_qualifying_prompt,
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
