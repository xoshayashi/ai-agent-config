#!/usr/bin/env python3
"""Unit tests for hooks/scripts/response_strategy_bridge.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "response_strategy_bridge.py"


def load_module():
    spec = importlib.util.spec_from_file_location("response_strategy_bridge", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RSB = load_module()


def assert_eq(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def with_env(updates: dict[str, str], fn):
    old = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            os.environ[key] = value
        fn()
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_parse_peer_json_direct() -> None:
    parsed = RSB.parse_peer_json('{"action":"allow_stop","strategy_prompt":"","needs_human":false}')
    assert_eq(parsed.get("action"), "allow_stop", "direct JSON parse")


def test_parse_peer_json_fenced() -> None:
    text = """result:
```json
{"action":"continue","strategy_prompt":"verify tests","needs_human":false}
```
"""
    parsed = RSB.parse_peer_json(text)
    assert_eq(parsed.get("action"), "continue", "fenced JSON parse")


def test_review_to_decision_continue() -> None:
    decision = RSB.review_to_decision(
        {
            "action": "continue",
            "strategy_prompt": "次のターンでは要件漏れがないか検証し、必要なら最小差分で修正して。",
            "needs_human": False,
        }
    )
    assert decision["continue"] is True
    assert decision["strategy_prompt"]


def test_review_to_decision_human_gate() -> None:
    decision = RSB.review_to_decision(
        {
            "action": "continue",
            "strategy_prompt": "continue anyway",
            "needs_human": True,
            "human_question": "本番反映しますか？",
        }
    )
    assert decision["continue"] is False
    assert "Human-in-the-loop check" in decision["system_message"]


def test_build_hook_output() -> None:
    codex_payload = RSB.build_hook_output(
        "codex",
        {"continue": True, "strategy_prompt": "run one more verification pass", "system_message": ""},
    )
    gemini_payload = RSB.build_hook_output(
        "gemini",
        {"continue": True, "strategy_prompt": "retry with narrower scope", "system_message": ""},
    )
    assert_eq(codex_payload.get("decision"), "block", "codex continue decision")
    assert_eq(gemini_payload.get("decision"), "deny", "gemini continue decision")


def test_should_skip_reentry_guard() -> None:
    def _run() -> None:
        data = {"hook_event_name": "Stop", "stop_hook_active": True}
        should_skip = RSB.should_skip(
            current="codex",
            data=data,
            prompt="この件を直して",
            response="x" * 200,
        )
        assert should_skip is True

    with_env({"AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY": "1"}, _run)


def test_safe_int_falls_back_on_invalid_env_values() -> None:
    def _run() -> None:
        should_skip = RSB.should_skip(
            current="codex",
            data={"hook_event_name": "Stop", "stop_hook_active": False},
            prompt="この件を直して",
            response="x" * 200,
        )
        assert should_skip is False

        excerpt = RSB.transcript_excerpt("")
        assert excerpt == "No transcript path supplied."

    with_env(
        {
            "AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY": "1",
            "AI_AGENT_RESPONSE_STRATEGY_MIN_RESPONSE_CHARS": "not-a-number",
            "AI_AGENT_RESPONSE_STRATEGY_TRANSCRIPT_LINES": "bad",
            "AI_AGENT_RESPONSE_STRATEGY_TRANSCRIPT_CHARS": "bad",
        },
        _run,
    )


def run_tests() -> int:
    tests = [
        test_parse_peer_json_direct,
        test_parse_peer_json_fenced,
        test_review_to_decision_continue,
        test_review_to_decision_human_gate,
        test_build_hook_output,
        test_should_skip_reentry_guard,
        test_safe_int_falls_back_on_invalid_env_values,
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
