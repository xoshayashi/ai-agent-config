#!/usr/bin/env python3
"""Unit tests for hooks/scripts/self_workflow.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "self_workflow.py"


def load_module():
    spec = importlib.util.spec_from_file_location("self_workflow", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SWF = load_module()


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


def test_parse_json_from_text() -> None:
    parsed = SWF.parse_json_from_text('{"action":"continue","next_prompt_for_codex":"x"}')
    assert_eq(parsed.get("action"), "continue", "direct JSON parse")


def test_parse_json_from_fenced_text() -> None:
    text = """result:
```json
{"status":"done","implementation_brief":"ok"}
```
"""
    parsed = SWF.parse_json_from_text(text)
    assert_eq(parsed.get("status"), "done", "fenced JSON parse")


def test_completion_keywords_from_hooks_md() -> None:
    with tempfile.TemporaryDirectory(prefix="hooks-md-test-") as tmp:
        hooks_md = Path(tmp) / "HOOKS.md"
        hooks_md.write_text(
            "# test\n\n- [[SPEC_DONE]]\n- [[IMPLEMENTATION_DONE]]\n- [[TASK_DONE]]\n",
            encoding="utf-8",
        )

        def _run() -> None:
            spec_done, implementation_done, verification_done, task_done = SWF.completion_keywords()
            assert_eq(spec_done, "[[SPEC_DONE]]", "spec keyword")
            assert_eq(implementation_done, "[[IMPLEMENTATION_DONE]]", "implementation keyword")
            assert_eq(verification_done, "[[VERIFICATION_DONE]]", "verification keyword default")
            assert_eq(task_done, "[[TASK_DONE]]", "task keyword")

        with_env({"AI_AGENT_HOOKS_RULES_DOC": str(hooks_md)}, _run)


def test_completion_keywords_prefer_first_match_per_category() -> None:
    with tempfile.TemporaryDirectory(prefix="hooks-md-test-") as tmp:
        hooks_md = Path(tmp) / "HOOKS.md"
        hooks_md.write_text(
            "\n".join(
                [
                    "# test",
                    "",
                    "- [[SPEC_DONE]]",
                    "- [[IMPLEMENTATION_DONE]]",
                    "- [[IMPLEMENTATION_DONE:V2]]",
                    "- [[VERIFICATION_DONE]]",
                    "- [[VERIFICATION_DONE:V2]]",
                    "- [[TASK_DONE]]",
                    "- [[TASK_DONE:V2]]",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        def _run() -> None:
            spec_done, implementation_done, verification_done, task_done = SWF.completion_keywords()
            assert_eq(spec_done, "[[SPEC_DONE]]", "spec keyword")
            assert_eq(implementation_done, "[[IMPLEMENTATION_DONE]]", "implementation keyword prefers first")
            assert_eq(verification_done, "[[VERIFICATION_DONE]]", "verification keyword prefers first")
            assert_eq(task_done, "[[TASK_DONE]]", "task keyword prefers first")

        with_env({"AI_AGENT_HOOKS_RULES_DOC": str(hooks_md)}, _run)


def test_should_skip_only_on_recursion_or_wrong_event() -> None:
    data = {"hook_event_name": "UserPromptSubmit", "stop_hook_active": False}
    assert SWF.should_skip("codex", data) is False

    def _run() -> None:
        assert SWF.should_skip("codex", data) is True

    with_env({"AI_AGENT_SELF_WORKFLOW_ACTIVE": "1"}, _run)


def test_stop_output_formats_for_codex_and_gemini() -> None:
    payload = SWF.stop_output(
        "codex",
        {"continue": True, "prompt": "次のステップを実行", "note": "missing verification"},
    )
    gemini_payload = SWF.stop_output(
        "gemini",
        {"continue": True, "prompt": "次のステップを実行", "note": "missing verification"}
    )
    assert_eq(payload.get("decision"), "block", "stop continuation decision")
    assert_eq(gemini_payload.get("decision"), "deny", "gemini continuation decision")
    assert payload.get("reason")


def test_turn_context_output_formats_for_claude_and_gemini() -> None:
    claude_payload = SWF.turn_context_output("claude", "UserPromptSubmit", "context")
    gemini_payload = SWF.turn_context_output("gemini", "BeforeAgent", "context")
    assert_eq(claude_payload.get("hookSpecificOutput", {}).get("hookEventName"), "UserPromptSubmit", "claude hook event")
    assert_eq(claude_payload.get("hookSpecificOutput", {}).get("additionalContext"), "context", "claude context")
    assert_eq(gemini_payload.get("hookSpecificOutput", {}).get("additionalContext"), "context", "gemini context")


def test_should_keep_current_task_followup_prompt() -> None:
    assert SWF.should_keep_current_task("続けて")
    assert SWF.should_keep_current_task("続けて。テストも追加して、最後に差分確認して")
    assert SWF.should_keep_current_task("この仕様で実装して")
    assert SWF.should_keep_current_task("fix it")
    assert not SWF.should_keep_current_task("新しい機能を追加したい")


def test_should_activate_self_workflow_prefers_complex_or_explicit_prompts() -> None:
    assert SWF.should_activate_self_workflow("このコードベースを分析して詳細な設計書を書いて")
    assert SWF.should_activate_self_workflow("Hook の仕様と実装計画を確認して修正して")
    assert not SWF.should_activate_self_workflow("ありがとう")
    assert not SWF.should_activate_self_workflow("status")
    assert not SWF.should_activate_self_workflow("sandbox と approval の違いを教えて")
    assert not SWF.should_activate_self_workflow("Codex の sandbox 設計について説明して")
    assert not SWF.should_activate_self_workflow("hooks/scripts/self_workflow.py の構成を説明して")
    assert not SWF.should_activate_self_workflow("improve the docstring")
    assert not SWF.should_activate_self_workflow("fix the error in https://example.com/api")
    assert not SWF.should_activate_self_workflow("fix 1/4 of the tests")


def test_is_answer_only_request_distinguishes_explanation_from_execution() -> None:
    assert SWF.is_answer_only_request("sandbox と approval の違いを教えて")
    assert SWF.is_answer_only_request("hooks/scripts/self_workflow.py の構成を説明して")
    assert not SWF.is_answer_only_request("hooks/scripts/self_workflow.py を修正して")


def test_spec_status_from_keyword() -> None:
    packet = {"status": "unknown", "spec_markdown": "ready\n[[SPEC_DONE]]"}
    status = SWF.spec_status_from(packet, "[[SPEC_DONE]]")
    assert_eq(status, "done", "spec status inferred from keyword")


def test_contains_explicit_keyword_requires_standalone_line() -> None:
    assert SWF.contains_explicit_keyword("done\n[[IMPLEMENTATION_DONE]]\n", "[[IMPLEMENTATION_DONE]]")
    assert SWF.contains_explicit_keyword("- [[TASK_DONE]]", "[[TASK_DONE]]")
    assert not SWF.contains_explicit_keyword("explain [[IMPLEMENTATION_DONE]] usage", "[[IMPLEMENTATION_DONE]]")


def test_spec_is_review_candidate_requires_markdown_headings() -> None:
    numbered_only = "\n".join(
        [
            "1. purpose",
            "2. scope / non-goals",
            "3. acceptance criteria",
            "4. constraints",
            "5. risks",
            "6. implementation plan",
            "説明" * 500,
        ]
    )
    assert not SWF.spec_is_review_candidate(numbered_only)

    structured = "\n".join(
        [
            "# 目的",
            "説明" * 500,
            "## scope / non-goals",
            "## acceptance criteria",
            "## constraints",
            "## risks",
            "## implementation plan",
        ]
    )
    assert SWF.spec_is_review_candidate(structured)


def test_build_spec_authoring_context_mentions_keyword_and_skill() -> None:
    text = SWF.build_spec_authoring_context("task", "[[SPEC_DONE]]")
    assert "[[SPEC_DONE]]" in text
    assert "$refinment" in text
    assert "show the refined prompt to the user" in text.lower()
    assert "Draft the specification yourself in this CLI first" in text


def test_default_implementation_start_prompt_uses_spec_and_skill() -> None:
    text = SWF.default_implementation_start_prompt("spec body", "brief", "[[BUILD_DONE]]")
    assert "spec body" in text
    assert "brief" in text
    assert "$refinment" in text
    assert "[[BUILD_DONE]]" in text
    assert "verification_ready" in text


def test_default_verification_start_prompt_mentions_structured_completion() -> None:
    text = SWF.default_verification_start_prompt(
        "spec body",
        "implemented",
        "[[VERIFICATION_DONE]]",
        "[[TASK_DONE]]",
    )
    assert "$refinment" in text
    assert "phase_signal" in text
    assert "[[VERIFICATION_DONE]]" in text
    assert "delta only" in text


def test_default_spec_refinement_prompt_uses_supplied_keyword() -> None:
    text = SWF.default_spec_refinement_prompt("spec body", "[[READY_FOR_BUILD]]")
    assert "spec body" in text
    assert "[[READY_FOR_BUILD]]" in text


def test_build_continue_decision_requests_skill_driven_review() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 0,
        "same_prompt_count": 0,
        "last_continuation_prompt": "",
        "spec_markdown": "spec",
    }
    decision = SWF.build_continue_decision(state, {"transcript_path": ""}, "latest response")
    assert decision["continue"] is True
    assert "$refinment" in decision["prompt"]
    assert "Skill-driven implementation refinment requested" in decision["note"]


def test_build_continue_decision_avoids_external_reviewer_language() -> None:
    state = {
        "implementation_turn": 3,
        "continuation_count": 0,
        "same_prompt_count": 0,
        "last_continuation_prompt": "",
        "spec_markdown": "spec",
    }
    decision = SWF.build_continue_decision(state, {"transcript_path": ""}, "latest response")
    assert decision["continue"] is True
    assert "Gemini" not in decision["prompt"]
    assert "peer" not in decision["note"].lower()


def test_build_continue_decision_stops_at_continuation_cap() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 1,
        "same_prompt_count": 1,
        "last_continuation_prompt": "x",
        "spec_markdown": "spec",
    }

    def _run() -> None:
        decision = SWF.build_continue_decision(state, {"transcript_path": ""}, "latest response")
        assert decision["continue"] is False
        assert "Continuation cap reached" in decision["note"]

    with_env({"AI_AGENT_SELF_WORKFLOW_MAX_CONTINUATIONS_PER_TASK": "1"}, _run)


def test_build_continue_decision_stops_on_repeated_prompt() -> None:
    state = {
        "implementation_turn": 1,
        "continuation_count": 0,
        "same_prompt_count": 2,
        "last_continuation_prompt": re_normalized_prompt(
            SWF.default_implementation_continue_prompt("spec", "latest response", "[[IMPLEMENTATION_DONE]]")
        ),
        "spec_markdown": "spec",
    }

    def _run() -> None:
        decision = SWF.build_continue_decision(state, {"transcript_path": ""}, "latest response")
        assert decision["continue"] is False
        assert "Repeated continuation prompt detected" in decision["note"]

    with_env({"AI_AGENT_SELF_WORKFLOW_MAX_SAME_PROMPT": "2"}, _run)


def test_handle_user_prompt_submit_bootstraps_spec_phase() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        payload = SWF.handle_user_prompt_submit("codex", "UserPromptSubmit", {"prompt": "このコードベースを分析して設計書を書いて"}, {}, state_path)
        output = payload.get("hookSpecificOutput", {})
        assert_eq(output.get("hookEventName"), "UserPromptSubmit", "bootstrap event")
        assert "[[SPEC_DONE]]" in str(output.get("additionalContext", ""))
        assert "$refinment" in str(output.get("additionalContext", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "spec_authoring", "spec phase initialized")
        assert_eq(saved.get("spec_revision_count"), 0, "spec revision count initialized")


def test_handle_user_prompt_submit_skips_light_prompts() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        payload = SWF.handle_user_prompt_submit("codex", "UserPromptSubmit", {"prompt": "ありがとう"}, {}, state_path)
        assert_eq(payload, {}, "light prompt should not trigger self-workflow")
        assert not state_path.exists()


def test_handle_session_start_resumes_context_for_implementation() -> None:
    payload = SWF.handle_session_start(
        "codex",
        {
            "phase": "implementation",
            "spec_markdown": "approved spec body",
        },
    )
    output = payload.get("hookSpecificOutput", {})
    assert_eq(output.get("hookEventName"), "SessionStart", "session start event")
    assert "approved spec body" in str(output.get("additionalContext", ""))


def test_handle_session_start_idle_returns_empty() -> None:
    payload = SWF.handle_session_start("codex", {"phase": "idle"})
    assert_eq(payload, {}, "idle session start should not inject context")


def test_handle_session_start_done_returns_new_task_message() -> None:
    payload = SWF.handle_session_start("codex", {"phase": "done"})
    output = payload.get("hookSpecificOutput", {})
    assert_eq(output.get("hookEventName"), "SessionStart", "session start event")
    assert "Start a new task prompt" in str(output.get("additionalContext", ""))


def test_handle_stop_spec_authoring_requests_skill_review_when_ready() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature", "spec_revision_count": 0}
        payload = SWF.handle_stop("codex", {"response": "draft\n[[SPEC_DONE]]"}, state, state_path)
        assert_eq(payload.get("decision"), "block", "should auto-continue into spec review")
        assert "$refinment" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "spec_review", "state promoted to spec_review")


def test_handle_stop_spec_authoring_can_use_structured_fallback_review() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_authoring", "original_prompt": "build feature", "spec_revision_count": 1}
        structured_spec = "\n".join(
            [
                "# 目的",
                "説明" * 500,
                "## scope / non-goals",
                "## acceptance criteria",
                "## constraints",
                "## risks",
                "## implementation plan",
            ]
        )
        payload = SWF.handle_stop("codex", {"response": structured_spec}, state, state_path)
        assert_eq(payload.get("decision"), "block", "fallback review should continue")
        assert "$refinment" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "spec_review", "fallback review enters spec_review")


def test_handle_stop_spec_review_done_moves_to_implementation() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_review", "spec_markdown": "draft"}
        payload = SWF.handle_stop("codex", {"response": "approved spec\n[[SPEC_DONE]]"}, state, state_path)
        assert_eq(payload.get("decision"), "block", "implementation should auto-continue")
        assert "Start implementation" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "implementation", "state promoted to implementation")


def test_handle_stop_spec_review_without_keyword_requests_refinement() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {"phase": "spec_review", "spec_markdown": "draft"}
        payload = SWF.handle_stop("codex", {"response": "still missing edge cases"}, state, state_path)
        assert_eq(payload.get("decision"), "block", "spec review should continue refining")
        assert "Refine the specification" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "spec_authoring", "returns to spec authoring")


def test_handle_stop_implementation_done_moves_to_verification() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        payload = SWF.handle_stop("codex", {"response": "work finished\n[[IMPLEMENTATION_DONE]]"}, state, state_path)
        assert_eq(payload.get("decision"), "block", "should continue into verification")
        assert "[[VERIFICATION_DONE]]" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "state promoted to verification")
        assert_eq(saved.get("verification_turn"), 0, "verification turn initialized")


def test_handle_stop_structured_verification_ready_moves_to_verification() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        payload = SWF.handle_stop(
            "codex",
            {"response": '```json\n{"phase_signal":"verification_ready","summary":"ready for checks"}\n```'},
            state,
            state_path,
        )
        assert_eq(payload.get("decision"), "block", "structured signal should continue into verification")
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "state promoted to verification")
        assert_eq(saved.get("last_phase_signal"), "verification_ready", "phase signal recorded")
        assert_eq(saved.get("verification_summary"), "ready for checks", "summary recorded")


def test_handle_stop_task_done_without_verification_keeps_verifying() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        payload = SWF.handle_stop("codex", {"response": "all done\n[[TASK_DONE]]"}, state, state_path)
        assert_eq(payload.get("decision"), "block", "should force verification before stop")
        assert "[[VERIFICATION_DONE]]" in str(payload.get("reason", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "task done alone should not finish")


def test_handle_stop_structured_task_complete_without_verification_keeps_verifying() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "implementation",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
            "implementation_turn": 0,
        }
        payload = SWF.handle_stop(
            "codex",
            {
                "response": '```json\n{"phase_signal":"task_complete","summary":"tests passed","checks_run":["python3 tests/test_self_workflow.py"],"diff_reviewed":true,"self_review_complete":true}\n```'
            },
            state,
            state_path,
        )
        assert_eq(payload.get("decision"), "block", "structured task complete should still force verification")
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "verification", "structured task complete alone should not finish")
        assert_eq(saved.get("checks_run_count"), 1, "checks count recorded")
        assert saved.get("diff_reviewed") is True
        assert saved.get("self_review_complete") is True


def test_handle_stop_verification_done_and_task_done_finishes() -> None:
    with tempfile.TemporaryDirectory(prefix="mlo-state-") as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "phase": "verification",
            "spec_markdown": "approved spec [[SPEC_DONE]]",
        }
        payload = SWF.handle_stop(
            "codex",
            {"response": "checks passed\n[[VERIFICATION_DONE]]\n[[TASK_DONE]]"},
            state,
            state_path,
        )
        assert "Verification completion detected." in str(payload.get("systemMessage", ""))
        saved = SWF.load_state(state_path)
        assert_eq(saved.get("phase"), "done", "verification plus task done should finish")


def test_build_verification_decision_accepts_structured_completion_evidence() -> None:
    state = {
        "phase": "verification",
        "spec_markdown": "approved spec [[SPEC_DONE]]",
        "verification_turn": 1,
        "continuation_count": 2,
        "same_prompt_count": 1,
        "last_continuation_prompt": "continue verification",
    }
    decision = SWF.build_verification_decision(
        state,
        {"transcript_path": ""},
        '```json\n{"phase_signal":"task_complete","summary":"all checks complete","checks_run":["python3 tests/test_self_workflow.py","sh scripts/validate-repo.sh"],"diff_reviewed":true,"self_review_complete":true}\n```',
        "[[VERIFICATION_DONE]]",
        "[[TASK_DONE]]",
    )
    assert decision["continue"] is False
    assert "Verification completion detected." in decision["note"]
    assert_eq(state.get("phase"), "done", "structured verification should finish")
    assert_eq(state.get("verification_summary"), "all checks complete", "summary stored")
    assert_eq(state.get("checks_run_count"), 2, "checks count stored")
    assert state.get("diff_reviewed") is True
    assert state.get("self_review_complete") is True
    assert_eq(state.get("continuation_count"), 0, "continuation count reset")
    assert_eq(state.get("same_prompt_count"), 0, "same prompt count reset")


def test_build_verification_decision_continues_with_skill_prompt() -> None:
    state = {
        "phase": "verification",
        "spec_markdown": "approved spec [[SPEC_DONE]]",
        "verification_turn": 1,
        "continuation_count": 0,
        "same_prompt_count": 0,
        "last_continuation_prompt": "",
    }
    decision = SWF.build_verification_decision(
        state,
        {"transcript_path": ""},
        "verification still running",
        "[[VERIFICATION_DONE]]",
        "[[TASK_DONE]]",
    )
    assert decision["continue"] is True
    assert "$refinment" in decision["prompt"]
    assert "Skill-driven verification refinment requested" in decision["note"]
    assert "delta only" in decision["prompt"]


def test_default_verification_continue_prompt_prefers_delta_after_correction_style_response() -> None:
    text = SWF.default_verification_continue_prompt(
        "spec body",
        "補足: macOS では network_access = true が効かない",
        "[[VERIFICATION_DONE]]",
        "[[TASK_DONE]]",
    )
    assert "delta-only" in text
    assert "Do not restate unchanged background." in text


def test_build_verification_decision_stops_at_verification_cap() -> None:
    state = {
        "phase": "verification",
        "spec_markdown": "approved spec [[SPEC_DONE]]",
        "verification_turn": 4,
        "continuation_count": 2,
        "same_prompt_count": 1,
        "last_continuation_prompt": "continue verification",
    }
    decision = SWF.build_verification_decision(
        state,
        {"transcript_path": ""},
        "verification still running",
        "[[VERIFICATION_DONE]]",
        "[[TASK_DONE]]",
    )
    assert decision["continue"] is False
    assert "Verification turn cap reached" in decision["note"]
    assert_eq(state.get("verification_turn"), 0, "verification turn reset")


def re_normalized_prompt(text: str) -> str:
    import re

    return re.sub(r"\s+", " ", text).strip().lower()


def run_tests() -> int:
    tests = [
        test_parse_json_from_text,
        test_parse_json_from_fenced_text,
        test_completion_keywords_from_hooks_md,
        test_completion_keywords_prefer_first_match_per_category,
        test_should_skip_only_on_recursion_or_wrong_event,
        test_stop_output_formats_for_codex_and_gemini,
        test_turn_context_output_formats_for_claude_and_gemini,
        test_should_keep_current_task_followup_prompt,
        test_should_activate_self_workflow_prefers_complex_or_explicit_prompts,
        test_is_answer_only_request_distinguishes_explanation_from_execution,
        test_spec_status_from_keyword,
        test_contains_explicit_keyword_requires_standalone_line,
        test_spec_is_review_candidate_requires_markdown_headings,
        test_build_spec_authoring_context_mentions_keyword_and_skill,
        test_default_implementation_start_prompt_uses_spec_and_skill,
        test_default_verification_start_prompt_mentions_structured_completion,
        test_default_spec_refinement_prompt_uses_supplied_keyword,
        test_build_continue_decision_requests_skill_driven_review,
        test_build_continue_decision_avoids_external_reviewer_language,
        test_build_continue_decision_stops_at_continuation_cap,
        test_build_continue_decision_stops_on_repeated_prompt,
        test_handle_user_prompt_submit_bootstraps_spec_phase,
        test_handle_user_prompt_submit_skips_light_prompts,
        test_handle_session_start_resumes_context_for_implementation,
        test_handle_session_start_idle_returns_empty,
        test_handle_session_start_done_returns_new_task_message,
        test_handle_stop_spec_authoring_requests_skill_review_when_ready,
        test_handle_stop_spec_authoring_can_use_structured_fallback_review,
        test_handle_stop_spec_review_done_moves_to_implementation,
        test_handle_stop_spec_review_without_keyword_requests_refinement,
        test_handle_stop_implementation_done_moves_to_verification,
        test_handle_stop_structured_verification_ready_moves_to_verification,
        test_handle_stop_task_done_without_verification_keeps_verifying,
        test_handle_stop_structured_task_complete_without_verification_keeps_verifying,
        test_handle_stop_verification_done_and_task_done_finishes,
        test_build_verification_decision_accepts_structured_completion_evidence,
        test_build_verification_decision_continues_with_skill_prompt,
        test_default_verification_continue_prompt_prefers_delta_after_correction_style_response,
        test_build_verification_decision_stops_at_verification_cap,
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
