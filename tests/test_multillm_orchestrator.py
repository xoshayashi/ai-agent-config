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
            spec_done, implementation_done, verification_done, task_done = MLO.completion_keywords()
            assert_eq(spec_done, "[[SPEC_DONE]]", "spec keyword")
            assert_eq(implementation_done, "[[IMPLEMENTATION_DONE]]", "implementation keyword")
            assert_eq(verification_done, "[[VERIFICATION_DONE]]", "verification keyword default")
            assert_eq(task_done, "[[TASK_DONE]]", "task keyword")

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
    assert MLO.should_keep_current_task("続けて。テストも追加して、最後に差分確認して"), "detailed follow-up should keep current task"
    assert MLO.should_keep_current_task("この仕様で実装して"), "implementation handoff should keep current task"
    assert MLO.should_keep_current_task("fix it"), "common English follow-up should keep current task"
    assert not MLO.should_keep_current_task("新しい機能を追加したい"), "new detailed prompt should start a new task"


def test_should_activate_orchestration_prefers_complex_or_explicit_prompts() -> None:
    assert MLO.should_activate_orchestration("このコードベースを分析して詳細な設計書を書いて")
    assert MLO.should_activate_orchestration("Hook の仕様と実装計画を確認して修正して")
    assert not MLO.should_activate_orchestration("ありがとう")
    assert not MLO.should_activate_orchestration("status")
    assert not MLO.should_activate_orchestration("improve the docstring")
    assert not MLO.should_activate_orchestration("fix the error in https://example.com/api")


def test_spec_status_from_keyword() -> None:
    packet = {"status": "unknown", "spec_markdown": "ready\n[[SPEC_DONE]]"}
    status = MLO.spec_status_from(packet, "[[SPEC_DONE]]")
    assert_eq(status, "done", "spec status inferred from keyword")


def test_contains_explicit_keyword_requires_standalone_line() -> None:
    assert MLO.contains_explicit_keyword("done\n[[IMPLEMENTATION_DONE]]\n", "[[IMPLEMENTATION_DONE]]")
    assert MLO.contains_explicit_keyword("- [[TASK_DONE]]", "[[TASK_DONE]]")
    assert not MLO.contains_explicit_keyword("explain [[IMPLEMENTATION_DONE]] usage", "[[IMPLEMENTATION_DONE]]")


def test_build_spec_authoring_context_mentions_keyword() -> None:
    text = MLO.build_spec_authoring_context("task", "[[SPEC_DONE]]")
    assert "[[SPEC_DONE]]" in text
    assert "Draft the specification yourself in Codex first" in text


def test_default_implementation_start_prompt_uses_spec() -> None:
    text = MLO.default_implementation_start_prompt("spec body", "brief")
    assert "spec body" in text
    assert "brief" in text


def test_claude_effort_level_defaults_low_for_simple_calls() -> None:
    assert_eq(MLO.claude_effort_level("simple", "tiny prompt"), "low", "simple effort default")


def test_claude_effort_level_raises_for_complex_spec_review() -> None:
    text = "仕様レビューです。複雑な設計とリスクを確認してください。"
    assert_eq(MLO.claude_effort_level("spec_review", text), "high", "complex review effort")


def test_claude_effort_level_allows_env_override() -> None:
    def _run() -> None:
        assert_eq(MLO.claude_effort_level("spec_review", "simple"), "medium", "simple override")
        assert_eq(MLO.claude_effort_level("implementation_guidance", "complex design risk"), "max", "complex override")

    with_env(
        {
            "AI_AGENT_ORCHESTRATOR_CLAUDE_SIMPLE_EFFORT": "medium",
            "AI_AGENT_ORCHESTRATOR_CLAUDE_COMPLEX_EFFORT": "max",
        },
        _run,
    )


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
        original_claude = patch_attr(MLO, "call_claude", lambda *args: json_text(decision_payload))
        original_gemini = patch_attr(MLO, "call_gemini", lambda _: "")
        try:
            decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response")
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
        original_claude = patch_attr(MLO, "call_claude", lambda *args: json_text(decision_payload))
        original_gemini = patch_attr(MLO, "call_gemini", lambda _: "")
        try:
            decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response")
        finally:
            MLO.transcript_excerpt = original_transcript
            MLO.call_claude = original_claude
            MLO.call_gemini = original_gemini
        assert decision["continue"] is False
        assert "Repeated continuation prompt detected" in decision["note"]

    with_env({"AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT": "2"}, _run)


def test_build_continue_decision_reports_claude_guidance_visibility() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 0,
        "same_prompt_count": 0,
        "last_continuation_prompt": "",
        "spec_markdown": "spec",
        "gemini_review_every": 99,
    }
    decision_payload = {
        "action": "continue",
        "next_prompt_for_codex": "verify tests",
        "reason": "One more concrete verification pass is worthwhile.",
    }

    original_transcript = patch_attr(MLO, "transcript_excerpt", lambda _: "excerpt")
    original_claude = patch_attr(MLO, "call_claude", lambda *args: json_text(decision_payload))
    original_gemini = patch_attr(MLO, "call_gemini", lambda _: "")
    try:
        decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response")
    finally:
        MLO.transcript_excerpt = original_transcript
        MLO.call_claude = original_claude
        MLO.call_gemini = original_gemini

    assert decision["continue"] is True
    assert "Claude implementation guidance received." in decision["note"]


def test_build_continue_decision_reports_gemini_and_claude_visibility() -> None:
    state = {
        "implementation_turn": 3,
        "continuation_count": 0,
        "same_prompt_count": 0,
        "last_continuation_prompt": "",
        "spec_markdown": "spec",
        "gemini_review_every": 3,
    }
    gemini_payload = {
        "simpler_option": "narrower fix",
        "spec_change_needed": False,
        "rationale": "keep it lean",
        "actionable_note_for_claude": "Ask Codex to trim the scope.",
    }
    claude_payload = {
        "action": "allow_stop",
        "next_prompt_for_codex": "",
        "reason": "",
    }

    original_transcript = patch_attr(MLO, "transcript_excerpt", lambda _: "excerpt")
    original_claude = patch_attr(MLO, "call_claude", lambda *args: json_text(claude_payload))
    original_gemini = patch_attr(MLO, "call_gemini", lambda _: json_text(gemini_payload))
    try:
        decision = MLO.build_continue_decision(state, {"transcript_path": ""}, "latest response")
    finally:
        MLO.transcript_excerpt = original_transcript
        MLO.call_claude = original_claude
        MLO.call_gemini = original_gemini

    assert decision["continue"] is False
    assert "Claude implementation guidance received; Gemini critique also applied." in decision["note"]


def test_handle_user_prompt_submit_bootstraps_spec_phase() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        original_keywords = patch_attr(MLO, "completion_keywords", lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"))
        try:
            payload = MLO.handle_user_prompt_submit({"prompt": "このコードベースを分析して設計書を書いて"}, {}, state_path)
        finally:
            MLO.completion_keywords = original_keywords
        output = payload.get("hookSpecificOutput", {})
        assert_eq(output.get("hookEventName"), "UserPromptSubmit", "bootstrap event")
        assert "[[SPEC_DONE]]" in str(output.get("additionalContext", ""))
        saved = MLO.load_state(state_path)
        assert_eq(saved.get("phase"), "spec_authoring", "spec phase initialized")
        assert_eq(saved.get("spec_revision_count"), 0, "spec revision count initialized")


def test_handle_user_prompt_submit_skips_light_prompts() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        payload = MLO.handle_user_prompt_submit({"prompt": "ありがとう"}, {}, state_path)
        assert_eq(payload, {}, "light prompt should not trigger orchestration")
        assert not state_path.exists()


def test_handle_stop_promotes_done_spec_to_implementation() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature"}
        review_payload = {
            "spec_markdown": "approved spec\n[[SPEC_DONE]]",
            "status": "done",
            "implementation_brief": "brief",
            "next_step_prompt_for_codex": "start coding",
        }
        original_review = patch_attr(MLO, "review_spec_with_claude", lambda data, prompt, draft, keyword: review_payload)
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop({"response": "draft\n[[SPEC_DONE]]"}, state, state_path)
        finally:
            MLO.review_spec_with_claude = original_review
            MLO.completion_keywords = original_keywords
        assert_eq(payload.get("decision"), "block", "implementation should auto-continue")
        assert_eq(payload.get("reason"), "start coding", "next step prompt")
        saved = MLO.load_state(state_path)
        assert_eq(saved.get("phase"), "implementation", "state promoted to implementation")


def test_handle_stop_generates_default_start_prompt_when_review_omits_one() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature"}
        review_payload = {
            "spec_markdown": "approved spec\n[[SPEC_DONE]]",
            "status": "done",
            "implementation_brief": "brief",
            "next_step_prompt_for_codex": "",
        }
        original_review = patch_attr(MLO, "review_spec_with_claude", lambda data, prompt, draft, keyword: review_payload)
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop({"response": "draft\n[[SPEC_DONE]]"}, state, state_path)
        finally:
            MLO.review_spec_with_claude = original_review
            MLO.completion_keywords = original_keywords
        assert_eq(payload.get("decision"), "block", "fallback prompt should continue into implementation")
        assert "approved spec\n[[SPEC_DONE]]" in str(payload.get("reason", ""))


def test_handle_stop_spec_authoring_returns_wait_message_before_keyword() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature", "spec_revision_count": 0}
        payload = MLO.handle_stop({"response": "短い仕様ドラフト"}, state, state_path)
        assert "specification draft saved" in str(payload.get("systemMessage", ""))


def test_handle_stop_spec_authoring_can_use_structured_fallback_review() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature", "spec_revision_count": 1}
        structured_spec = "\n".join(
            [
                "1. 目的",
                "説明" * 500,
                "2. scope / non-goals",
                "3. acceptance criteria",
                "4. constraints",
                "5. risks",
                "6. implementation plan",
            ]
        )
        review_payload = {
            "spec_markdown": structured_spec + "\n[[SPEC_DONE]]",
            "status": "done",
            "implementation_brief": "brief",
            "next_step_prompt_for_codex": "start coding",
        }
        original_review = patch_attr(MLO, "review_spec_with_claude", lambda data, prompt, draft, keyword: review_payload)
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop({"response": structured_spec}, state, state_path)
        finally:
            MLO.review_spec_with_claude = original_review
            MLO.completion_keywords = original_keywords
        assert_eq(payload.get("decision"), "block", "fallback review should continue into implementation")
        assert_eq(payload.get("reason"), "start coding", "fallback review next prompt")


def test_handle_stop_implementation_done_moves_to_verification() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop({"response": "work finished\n[[IMPLEMENTATION_DONE]]"}, state, state_path)
        finally:
            MLO.completion_keywords = original_keywords
        assert_eq(payload.get("decision"), "block", "should continue into verification")
        assert "[[VERIFICATION_DONE]]" in str(payload.get("reason", ""))
        saved = MLO.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "state promoted to verification")


def test_handle_stop_task_done_without_verification_keeps_verifying() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop({"response": "all done\n[[TASK_DONE]]"}, state, state_path)
        finally:
            MLO.completion_keywords = original_keywords
        assert_eq(payload.get("decision"), "block", "should force verification before stop")
        assert "[[VERIFICATION_DONE]]" in str(payload.get("reason", ""))
        saved = MLO.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "task done alone should not finish")


def test_handle_stop_verification_done_and_task_done_finishes() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "verification",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
        }
        original_keywords = patch_attr(
            MLO,
            "completion_keywords",
            lambda: ("[[SPEC_DONE]]", "[[IMPLEMENTATION_DONE]]", "[[VERIFICATION_DONE]]", "[[TASK_DONE]]"),
        )
        try:
            payload = MLO.handle_stop(
                {"response": "checks passed\n[[VERIFICATION_DONE]]\n[[TASK_DONE]]"},
                state,
                state_path,
            )
        finally:
            MLO.completion_keywords = original_keywords
        assert "Verification and task completion keywords detected." in str(payload.get("systemMessage", ""))
        saved = MLO.load_state(state_path)
        assert_eq(saved.get("phase"), "done", "verification plus task done should finish")


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
        test_should_activate_orchestration_prefers_complex_or_explicit_prompts,
        test_spec_status_from_keyword,
        test_build_spec_authoring_context_mentions_keyword,
        test_default_implementation_start_prompt_uses_spec,
        test_claude_effort_level_defaults_low_for_simple_calls,
        test_claude_effort_level_raises_for_complex_spec_review,
        test_claude_effort_level_allows_env_override,
        test_build_continue_decision_stops_at_continuation_cap,
        test_build_continue_decision_stops_on_repeated_prompt,
        test_build_continue_decision_reports_claude_guidance_visibility,
        test_build_continue_decision_reports_gemini_and_claude_visibility,
        test_handle_user_prompt_submit_bootstraps_spec_phase,
        test_handle_user_prompt_submit_skips_light_prompts,
        test_handle_stop_promotes_done_spec_to_implementation,
        test_handle_stop_generates_default_start_prompt_when_review_omits_one,
        test_handle_stop_spec_authoring_returns_wait_message_before_keyword,
        test_handle_stop_spec_authoring_can_use_structured_fallback_review,
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
