#!/usr/bin/env python3
"""Unit tests for hooks/scripts/multillm_orchestrator.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "multillm_orchestrator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("multillm_orchestrator", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MLO = load_module()


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


def patch_attr(obj, name: str, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    return original


def test_parse_json_from_text() -> None:
    parsed = MLO.parse_json_from_text('{"action":"continue","next_prompt_for_codex":"x"}')
    assert_eq(parsed.get("action"), "continue", "direct JSON parse")


def test_parse_json_from_fenced_text() -> None:
    text = """result:
```json
{"status":"done","implementation_brief":"ok"}
```
"""
    parsed = MLO.parse_json_from_text(text)
    assert_eq(parsed.get("status"), "done", "fenced JSON parse")


def test_completion_keywords_from_hooks_md() -> None:
    with tempfile.TemporaryDirectory(prefix="hooks-md-test-") as tmp:
        hooks_md = Path(tmp) / "HOOKS.md"
        hooks_md.write_text(
            "# test\n\n- [[SPEC_DONE]]\n- [[IMPLEMENTATION_DONE]]\n- [[TASK_DONE]]\n",
            encoding="utf-8",
        )

        def _run() -> None:
            spec_done, impl_done = MLO.completion_keywords()
            assert_eq(spec_done, "[[SPEC_DONE]]", "spec keyword")
            assert "[[IMPLEMENTATION_DONE]]" in impl_done
            assert "[[TASK_DONE]]" in impl_done

        with_env({"AI_AGENT_HOOKS_RULES_DOC": str(hooks_md)}, _run)


def test_should_skip_when_enabled_and_event_matches() -> None:
    data = {"hook_event_name": "UserPromptSubmit", "stop_hook_active": False}

    def _run() -> None:
        skipped = MLO.should_skip("codex", data)
        assert skipped is False

    with_env({"AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION": "1"}, _run)


def test_codex_stop_output_continue() -> None:
    payload = MLO.codex_stop_output(
        {"continue": True, "prompt": "次のステップを実行", "note": "missing verification"}
    )
    assert_eq(payload.get("decision"), "block", "stop continuation decision")
    assert payload.get("reason")


def test_should_keep_current_task_followup_prompt() -> None:
    assert MLO.should_keep_current_task("続けて"), "follow-up prompt should keep current task"
    assert not MLO.should_keep_current_task("新しい機能を追加したい"), "new detailed prompt should start a new task"


def test_spec_status_from_keyword() -> None:
    packet = {"status": "unknown", "spec_markdown": "ready [[SPEC_DONE]]"}
    status = MLO.spec_status_from(packet, "[[SPEC_DONE]]")
    assert_eq(status, "done", "spec status inferred from keyword")


def test_build_continue_decision_stops_at_continuation_cap() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 1,
        "same_prompt_count": 1,
        "last_continuation_prompt": "verify tests",
        "spec_markdown": "spec",
        "gemini_review_every": 99,
    }
    decision_payload = {
        "action": "continue",
        "next_prompt_for_codex": "verify tests",
        "reason": "one more pass",
    }

    def _run() -> None:
        original_transcript = patch_attr(MLO, "transcript_excerpt", lambda _: "excerpt")
        original_claude = patch_attr(MLO, "call_claude", lambda _: json_text(decision_payload))
        original_gemini = patch_attr(MLO, "call_gemini", lambda _: "")
        try:
            decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response", set())
        finally:
            MLO.transcript_excerpt = original_transcript
            MLO.call_claude = original_claude
            MLO.call_gemini = original_gemini
        assert decision["continue"] is False
        assert "Continuation cap reached" in decision["note"]

    with_env({"AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK": "1"}, _run)


def test_build_continue_decision_stops_on_repeated_prompt() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 0,
        "same_prompt_count": 2,
        "last_continuation_prompt": "verify tests",
        "spec_markdown": "spec",
        "gemini_review_every": 99,
    }
    decision_payload = {
        "action": "continue",
        "next_prompt_for_codex": "verify tests",
        "reason": "repeat",
    }

    def _run() -> None:
        original_transcript = patch_attr(MLO, "transcript_excerpt", lambda _: "excerpt")
        original_claude = patch_attr(MLO, "call_claude", lambda _: json_text(decision_payload))
        original_gemini = patch_attr(MLO, "call_gemini", lambda _: "")
        try:
            decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response", set())
        finally:
            MLO.transcript_excerpt = original_transcript
            MLO.call_claude = original_claude
            MLO.call_gemini = original_gemini
        assert decision["continue"] is False
        assert "Repeated continuation prompt detected" in decision["note"]

    with_env({"AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT": "2"}, _run)


def test_handle_user_prompt_submit_fail_open_on_empty_spec() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        original_builder = patch_attr(
            MLO,
            "build_spec_by_claude_and_gemini",
            lambda data, prompt, keyword: {"spec_markdown": "", "status": "draft"},
        )
        original_keywords = patch_attr(MLO, "completion_keywords", lambda: ("[[SPEC_DONE]]", {"[[TASK_DONE]]"}))
        try:
            payload = MLO.handle_user_prompt_submit({"prompt": "task"}, {}, state_path)
        finally:
            MLO.build_spec_by_claude_and_gemini = original_builder
            MLO.completion_keywords = original_keywords
        assert_eq(payload, {}, "empty spec should fail open")
        assert not state_path.exists()


def json_text(payload: dict[str, object]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False)


def run_tests() -> int:
    tests = [
        test_parse_json_from_text,
        test_parse_json_from_fenced_text,
        test_completion_keywords_from_hooks_md,
        test_should_skip_when_enabled_and_event_matches,
        test_codex_stop_output_continue,
        test_should_keep_current_task_followup_prompt,
        test_spec_status_from_keyword,
        test_build_continue_decision_stops_at_continuation_cap,
        test_build_continue_decision_stops_on_repeated_prompt,
        test_handle_user_prompt_submit_fail_open_on_empty_spec,
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
