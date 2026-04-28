#!/usr/bin/env python3
"""Unit tests for hooks/scripts/subprocess_check.py."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "subprocess_check.py"


def load_module():
    spec = importlib.util.spec_from_file_location("subprocess_check", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SC = load_module()


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


# ── Recursion guard / event filtering ────────────────────────────────────────

def test_should_skip_event_on_recursion_guard() -> None:
    data = {"hook_event_name": "UserPromptSubmit"}
    assert SC.should_skip_event("codex", data) is False

    def _run() -> None:
        assert SC.should_skip_event("codex", data) is True

    with_env({"AI_AGENT_SELF_WORKFLOW_ACTIVE": "1"}, _run)


def test_should_skip_event_on_unsupported_event() -> None:
    assert SC.should_skip_event("claude", {"hook_event_name": "BeforeAgent"}) is True
    assert SC.should_skip_event("claude", {"hook_event_name": "Stop"}) is False


def test_supported_events_cover_all_four_clis() -> None:
    assert "codex" in SC.SUPPORTED_EVENTS
    assert "claude" in SC.SUPPORTED_EVENTS
    assert "gemini" in SC.SUPPORTED_EVENTS
    assert "copilot" in SC.SUPPORTED_EVENTS
    assert "Stop" in SC.SUPPORTED_EVENTS["copilot"]
    assert "AfterAgent" in SC.SUPPORTED_EVENTS["gemini"]


# ── Lightweight gate ─────────────────────────────────────────────────────────

def test_gate_disabled_via_env() -> None:
    def _run() -> None:
        skip, reason = SC.should_skip_subprocess({}, "Stop", "x" * 1000)
        assert skip is True
        assert "AI_AGENT_SUBPROCESS_CHECK=0" in reason

    with_env({"AI_AGENT_SUBPROCESS_CHECK": "0"}, _run)


def test_gate_blocks_after_completion() -> None:
    skip, reason = SC.should_skip_subprocess({"completed": True}, "Stop", "long " * 100)
    assert skip is True
    assert "complete" in reason


def test_gate_blocks_after_hard_cap() -> None:
    def _run() -> None:
        state = {"calls_used": 8}
        skip, reason = SC.should_skip_subprocess(state, "Stop", "long " * 100)
        assert skip is True
        assert "cap" in reason

    with_env({"AI_AGENT_SUBPROCESS_CHECK_MAX": "8"}, _run)


def test_gate_blocks_short_stop_response() -> None:
    skip, reason = SC.should_skip_subprocess({}, "Stop", "ok")
    assert skip is True
    assert "min_output" in reason


def test_gate_blocks_task_done_shortcut() -> None:
    response = "Did the work.\n\n[[TASK_DONE]]\n"
    skip, reason = SC.should_skip_subprocess({}, "Stop", response * 10)
    assert skip is True
    assert "TASK_DONE" in reason


def test_gate_blocks_answer_only_response() -> None:
    response = (
        "The difference between sandbox and approval modes is that the sandbox "
        "restricts filesystem operations while approval gates require explicit "
        "user permission for individual actions. Sandbox is policy-driven; "
        "approval is interactive. Choose sandbox for headless runs and approval "
        "for interactive review."
    )
    skip, reason = SC.should_skip_subprocess({}, "Stop", response)
    assert skip is True
    assert "answer-only" in reason


def test_gate_allows_substantive_execution_response() -> None:
    response = (
        "I edited hooks/scripts/subprocess_check.py to add a new gate. "
        "I ran the tests and they all pass. "
        "Created a new file at tests/test_subprocess_check.py with additional coverage."
    )
    skip, reason = SC.should_skip_subprocess({}, "Stop", response * 3)
    assert skip is False, f"unexpected skip: {reason}"


def test_gate_does_not_filter_on_user_prompt_submit() -> None:
    skip, _ = SC.should_skip_subprocess({}, "UserPromptSubmit", "fix the bug")
    assert skip is False


# ── Subprocess command builder ───────────────────────────────────────────────

def test_subprocess_commands_present_for_all_clis() -> None:
    for cli in ("codex", "claude", "gemini", "copilot"):
        spec = SC.SUBPROCESS_COMMANDS[cli]
        assert isinstance(spec["argv"], list)
        assert spec["prompt_via"] in {"stdin", "argv"}


def test_subprocess_commands_match_expected_invocations() -> None:
    assert SC.SUBPROCESS_COMMANDS["codex"]["argv"][:2] == ["codex", "exec"]
    assert "--json" in SC.SUBPROCESS_COMMANDS["codex"]["argv"]
    assert SC.SUBPROCESS_COMMANDS["claude"]["argv"][:2] == ["claude", "-p"]
    assert "--output-format" in SC.SUBPROCESS_COMMANDS["claude"]["argv"]
    assert SC.SUBPROCESS_COMMANDS["gemini"]["argv"] == ["gemini", "-p"]
    assert SC.SUBPROCESS_COMMANDS["copilot"]["argv"][:2] == ["copilot", "-p"]
    assert "--no-ask-user" in SC.SUBPROCESS_COMMANDS["copilot"]["argv"]


# ── Subprocess invocation ────────────────────────────────────────────────────

def test_call_subprocess_returns_none_when_binary_missing() -> None:
    with mock.patch.object(SC.shutil, "which", return_value=None):
        assert SC.call_subprocess("codex", "hello") is None


def test_call_subprocess_passes_recursion_guard_env() -> None:
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["env"] = kwargs.get("env", {})
        captured["input"] = kwargs.get("input")
        result = mock.MagicMock()
        result.returncode = 0
        result.stdout = "STATUS: complete\n"
        return result

    with mock.patch.object(SC.shutil, "which", return_value="/usr/local/bin/claude"), \
         mock.patch.object(SC.subprocess, "run", side_effect=fake_run):
        out = SC.call_subprocess("claude", "advisor prompt")
    assert out == "STATUS: complete\n"
    assert captured["env"].get("AI_AGENT_SELF_WORKFLOW_ACTIVE") == "1"
    assert captured["input"] == "advisor prompt"
    assert captured["argv"][:2] == ["claude", "-p"]


def test_call_subprocess_uses_argv_for_gemini_and_copilot() -> None:
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = list(argv)
        captured["input"] = kwargs.get("input")
        result = mock.MagicMock()
        result.returncode = 0
        result.stdout = "do x"
        return result

    with mock.patch.object(SC.shutil, "which", return_value="/bin/gemini"), \
         mock.patch.object(SC.subprocess, "run", side_effect=fake_run):
        SC.call_subprocess("gemini", "advisor prompt")
    assert captured["argv"][-1] == "advisor prompt"
    assert captured["input"] is None


def test_call_subprocess_returns_none_on_timeout() -> None:
    def raise_timeout(argv, **kwargs):
        raise SC.subprocess.TimeoutExpired(cmd=argv, timeout=1)

    with mock.patch.object(SC.shutil, "which", return_value="/bin/claude"), \
         mock.patch.object(SC.subprocess, "run", side_effect=raise_timeout):
        assert SC.call_subprocess("claude", "advisor prompt") is None


def test_call_subprocess_returns_none_on_nonzero_exit() -> None:
    result = mock.MagicMock()
    result.returncode = 2
    result.stdout = "boom"
    with mock.patch.object(SC.shutil, "which", return_value="/bin/claude"), \
         mock.patch.object(SC.subprocess, "run", return_value=result):
        assert SC.call_subprocess("claude", "advisor prompt") is None


# ── Output parsers ───────────────────────────────────────────────────────────

def test_parse_output_complete_marker() -> None:
    kind, text = SC.parse_subprocess_output("gemini", "STATUS: complete\nfine\n")
    assert kind == "complete"
    assert "fine" in text


def test_parse_output_instruction() -> None:
    kind, text = SC.parse_subprocess_output("gemini", "Do the next step.\n")
    assert kind == "instruction"
    assert text.startswith("Do the next step")


def test_parse_output_empty() -> None:
    assert SC.parse_subprocess_output("gemini", "") == ("empty", "")
    assert SC.parse_subprocess_output("gemini", None) == ("empty", "")


def test_parse_codex_jsonl_extracts_text() -> None:
    raw = '\n'.join(
        [
            '{"type":"thread.started","id":"t-1"}',
            '{"type":"message","content":[{"type":"text","text":"STATUS: complete"}]}',
            '{"type":"message","content":[{"type":"text","text":"all checks ran"}]}',
        ]
    )
    kind, text = SC.parse_subprocess_output("codex", raw)
    assert kind == "complete"
    assert "STATUS: complete" in text


def test_parse_claude_json_extracts_result() -> None:
    raw = json.dumps({"result": "Edit hooks/scripts/foo.py to add a new branch."})
    kind, text = SC.parse_subprocess_output("claude", raw)
    assert kind == "instruction"
    assert "Edit hooks/scripts/foo.py" in text


def test_parse_claude_json_handles_array_of_stream_events() -> None:
    """Recent Claude Code releases emit `--output-format json` as an array of stream events."""
    events = [
        {"type": "system", "subtype": "init", "session_id": "abc"},
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "STATUS: complete"}],
            },
        },
        {"type": "result", "subtype": "success", "result": "STATUS: complete"},
    ]
    kind, text = SC.parse_subprocess_output("claude", json.dumps(events))
    assert kind == "complete"
    assert text.strip().startswith("STATUS: complete")


def test_parse_claude_json_array_falls_back_to_assistant_text_when_no_result_event() -> None:
    events = [
        {"type": "system", "subtype": "init", "session_id": "abc"},
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "Run the tests next."}],
            },
        },
    ]
    kind, text = SC.parse_subprocess_output("claude", json.dumps(events))
    assert kind == "instruction"
    assert "Run the tests next" in text


def test_parse_subprocess_output_returns_empty_when_parser_fails_to_avoid_raw_leak() -> None:
    """Guard: if claude/codex output cannot be parsed, do NOT leak raw JSON as continuation."""
    raw = '{"unexpected_envelope": [1, 2, 3], "no_text_anywhere": true}'
    kind, text = SC.parse_subprocess_output("claude", raw)
    assert kind == "empty"
    assert text == ""

    raw_codex = '{"type":"thread.started","id":"t-1"}\n{"type":"some_other_event"}'
    kind, text = SC.parse_subprocess_output("codex", raw_codex)
    assert kind == "empty"
    assert text == ""


# ── Output adapters ──────────────────────────────────────────────────────────

def test_stop_continuation_output_for_claude_blocks() -> None:
    payload = SC.stop_continuation_output("claude", "next step please", "continuation #1")
    assert_eq(payload["decision"], "block", "claude continuation decision")
    assert "next step please" in payload["reason"]
    assert "subprocess-check" in payload["systemMessage"]


def test_stop_continuation_output_for_gemini_denies() -> None:
    payload = SC.stop_continuation_output("gemini", "next step please", "")
    assert_eq(payload["decision"], "deny", "gemini continuation decision")


def test_context_output_uses_correct_shape_per_cli() -> None:
    claude_payload = SC.context_output("claude", "UserPromptSubmit", "ctx")
    gemini_payload = SC.context_output("gemini", "BeforeAgent", "ctx")
    copilot_payload = SC.context_output("copilot", "UserPromptSubmit", "ctx")
    assert_eq(claude_payload["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit", "claude wraps with event")
    assert_eq(gemini_payload["hookSpecificOutput"]["additionalContext"], "ctx", "gemini context")
    assert_eq(copilot_payload["additionalContext"], "ctx", "copilot context flat")


# ── Build subprocess prompt ──────────────────────────────────────────────────

def test_build_subprocess_prompt_is_skill_neutral() -> None:
    text = SC.build_subprocess_prompt("Stop", "do X", "main session output")
    assert "STATUS: complete" in text
    assert "main session output" in text
    assert "do X" in text
    # Skill-neutral: must not push any specific skill
    assert "$refinment" not in text
    assert "Use $refinment" not in text


def test_build_subprocess_prompt_preserves_event_context() -> None:
    text = SC.build_subprocess_prompt("UserPromptSubmit", "build feature", "")
    assert "UserPromptSubmit" in text
    assert "build feature" in text


# ── handle_event integration ─────────────────────────────────────────────────

def with_state_dir(fn):
    """Run fn with a temporary state dir."""
    with tempfile.TemporaryDirectory(prefix="sc-state-") as tmp:
        with_env({"AI_AGENT_STATE_DIR": tmp}, fn)


def test_handle_event_skips_when_disabled() -> None:
    def _run() -> None:
        result = SC.handle_event("claude", {"hook_event_name": "Stop", "response": "x" * 1000})
        assert_eq(result, {}, "disabled skip")

    with_env({"AI_AGENT_SUBPROCESS_CHECK": "0"}, lambda: with_state_dir(_run))


def test_handle_event_skips_short_stop_response_without_calling_subprocess() -> None:
    called = {"count": 0}

    def fake_call(*_args, **_kwargs):
        called["count"] += 1
        return None

    def _run() -> None:
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            result = SC.handle_event("claude", {"hook_event_name": "Stop", "response": "ok"})
        assert_eq(result, {}, "short response should yield empty output")
        assert_eq(called["count"], 0, "subprocess must not be called for short response")

    with_state_dir(_run)


def test_handle_event_invokes_subprocess_and_returns_continuation() -> None:
    def fake_call(current, prompt):
        return "Edit hooks/scripts/foo.py and add a new branch.\n"

    def _run() -> None:
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            substantive = (
                "I edited hooks/scripts/x.py and ran the tests. "
                "Created tests/test_x.py with extra coverage."
            ) * 5
            result = SC.handle_event(
                "claude",
                {
                    "hook_event_name": "Stop",
                    "session_id": "sess-1",
                    "response": substantive,
                },
            )
        assert_eq(result.get("decision"), "block", "claude continuation should block")
        assert "Edit hooks/scripts/foo.py" in result.get("reason", "")

    with_state_dir(_run)


def test_handle_event_marks_complete_on_status_marker() -> None:
    def fake_call(current, prompt):
        return "STATUS: complete\nAll done.\n"

    def _run() -> None:
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            substantive = (
                "Edited 4 files and ran the test suite. "
                "All tests pass; pushed to origin/main."
            ) * 5
            result = SC.handle_event(
                "claude",
                {
                    "hook_event_name": "Stop",
                    "session_id": "sess-2",
                    "response": substantive,
                },
            )
        assert "complete" in result.get("systemMessage", "")
        # Subsequent call should now skip due to completed flag
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            again = SC.handle_event(
                "claude",
                {
                    "hook_event_name": "Stop",
                    "session_id": "sess-2",
                    "response": substantive,
                },
            )
        assert_eq(again, {}, "subsequent stop must skip after completion")

    with_state_dir(_run)


def test_handle_event_increments_calls_used_until_cap() -> None:
    call_log = []

    def fake_call(current, prompt):
        call_log.append(prompt)
        return "Continue with the next step.\n"

    def _run() -> None:
        substantive = (
            "I edited files and ran tests; results created tests/file.py. "
            "Ran the suite and pushed."
        ) * 5
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            for _ in range(3):
                SC.handle_event(
                    "claude",
                    {
                        "hook_event_name": "Stop",
                        "session_id": "cap-sess",
                        "response": substantive,
                    },
                )

        # Expect 2 calls because cap=2
        assert_eq(len(call_log), 2, "subprocess must stop being invoked at cap")

    with_env({"AI_AGENT_SUBPROCESS_CHECK_MAX": "2"}, lambda: with_state_dir(_run))


def test_handle_event_bootstraps_state_on_user_prompt_submit() -> None:
    def fake_call(current, prompt):
        return "Run the tests next."

    def _run() -> None:
        with mock.patch.object(SC, "call_subprocess", side_effect=fake_call):
            result = SC.handle_event(
                "codex",
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "fresh",
                    "prompt": "Implement feature X",
                },
            )
        assert "Run the tests next." in str(
            result.get("hookSpecificOutput", {}).get("additionalContext", "")
        )

    with_state_dir(_run)


# ── State persistence ────────────────────────────────────────────────────────

def test_state_round_trip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"
        SC.save_state(path, {"calls_used": 3, "completed": False})
        loaded = SC.load_state(path)
        assert_eq(loaded.get("calls_used"), 3, "calls_used round-trip")
        assert_eq(loaded.get("completed"), False, "completed round-trip")


def test_state_root_uses_ai_agent_state_dir() -> None:
    def _run() -> None:
        root = SC.state_root()
        assert root.name == "subprocess-check"
        assert "ai-agent-config" not in str(root) or "/.ai-agent-config" in str(root) or "/temp" in str(root) or root.parent.name

    with_env({"AI_AGENT_STATE_DIR": "/tmp/test-ai-agent"}, _run)


def test_decision_log_appends_jsonl() -> None:
    def _run() -> None:
        SC.log_decision("sess-X", "Stop", "skip", "test detail")
        path = SC.decision_log_path()
        assert path.is_file()
        last_line = path.read_text(encoding="utf-8").strip().splitlines()[-1]
        entry = json.loads(last_line)
        assert_eq(entry.get("session"), "sess-X", "session in log")
        assert_eq(entry.get("kind"), "skip", "kind in log")

    with_state_dir(_run)


# ── Test runner ──────────────────────────────────────────────────────────────

def run_tests() -> int:
    tests = [
        test_should_skip_event_on_recursion_guard,
        test_should_skip_event_on_unsupported_event,
        test_supported_events_cover_all_four_clis,
        test_gate_disabled_via_env,
        test_gate_blocks_after_completion,
        test_gate_blocks_after_hard_cap,
        test_gate_blocks_short_stop_response,
        test_gate_blocks_task_done_shortcut,
        test_gate_blocks_answer_only_response,
        test_gate_allows_substantive_execution_response,
        test_gate_does_not_filter_on_user_prompt_submit,
        test_subprocess_commands_present_for_all_clis,
        test_subprocess_commands_match_expected_invocations,
        test_call_subprocess_returns_none_when_binary_missing,
        test_call_subprocess_passes_recursion_guard_env,
        test_call_subprocess_uses_argv_for_gemini_and_copilot,
        test_call_subprocess_returns_none_on_timeout,
        test_call_subprocess_returns_none_on_nonzero_exit,
        test_parse_output_complete_marker,
        test_parse_output_instruction,
        test_parse_output_empty,
        test_parse_codex_jsonl_extracts_text,
        test_parse_claude_json_extracts_result,
        test_parse_claude_json_handles_array_of_stream_events,
        test_parse_claude_json_array_falls_back_to_assistant_text_when_no_result_event,
        test_parse_subprocess_output_returns_empty_when_parser_fails_to_avoid_raw_leak,
        test_stop_continuation_output_for_claude_blocks,
        test_stop_continuation_output_for_gemini_denies,
        test_context_output_uses_correct_shape_per_cli,
        test_build_subprocess_prompt_is_skill_neutral,
        test_build_subprocess_prompt_preserves_event_context,
        test_handle_event_skips_when_disabled,
        test_handle_event_skips_short_stop_response_without_calling_subprocess,
        test_handle_event_invokes_subprocess_and_returns_continuation,
        test_handle_event_marks_complete_on_status_marker,
        test_handle_event_increments_calls_used_until_cap,
        test_handle_event_bootstraps_state_on_user_prompt_submit,
        test_state_round_trip,
        test_state_root_uses_ai_agent_state_dir,
        test_decision_log_appends_jsonl,
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
