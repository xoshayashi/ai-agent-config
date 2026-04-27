#!/usr/bin/env python3
"""Unit tests for hooks/scripts/peer_prompt_refinement.py."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "hooks" / "scripts" / "peer_prompt_refinement.py"


def load_module():
    spec = importlib.util.spec_from_file_location("peer_prompt_refinement", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PPR = load_module()


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


def patch_which(fake):
    original = PPR.shutil.which
    PPR.shutil.which = fake
    return original


def test_auto_route_codex_to_claude() -> None:
    def _run() -> None:
        assert_eq(PPR.choose_provider("codex"), "claude", "auto route codex")

    with_env({"AI_AGENT_PROMPT_REFINEMENT_PROVIDER": "auto"}, _run)


def test_auto_route_claude_to_codex() -> None:
    def _run() -> None:
        assert_eq(PPR.choose_provider("claude"), "codex", "auto route claude")

    with_env({"AI_AGENT_PROMPT_REFINEMENT_PROVIDER": "auto"}, _run)


def test_explicit_provider_override() -> None:
    def _run() -> None:
        assert_eq(PPR.choose_provider("codex"), "gemini", "explicit provider override")

    with_env({"AI_AGENT_PROMPT_REFINEMENT_PROVIDER": "gemini"}, _run)


def test_peer_invocation_claude_channel() -> None:
    def _run() -> None:
        original = patch_which(lambda name: "/usr/bin/claude" if name == "claude" else None)
        try:
            _, command, stdin_payload = PPR.peer_invocation("codex", "/tmp", "packet") or ("", [], "")
        finally:
            PPR.shutil.which = original
        assert command and command[0] == "claude"
        assert_eq(stdin_payload, "", "claude invocation should use -p channel only")

    with_env({"AI_AGENT_PROMPT_REFINEMENT_PROVIDER": "claude"}, _run)


def test_peer_invocation_codex_channel() -> None:
    def _run() -> None:
        original = patch_which(lambda name: "/usr/bin/codex" if name == "codex" else None)
        try:
            _, command, stdin_payload = PPR.peer_invocation("claude", "/tmp", "packet") or ("", [], "")
        finally:
            PPR.shutil.which = original
        assert command and command[0] == "codex"
        assert_eq(stdin_payload, "packet", "codex invocation should use stdin channel")

    with_env({"AI_AGENT_PROMPT_REFINEMENT_PROVIDER": "codex"}, _run)


def test_strict_mode_defaults_on() -> None:
    def _run() -> None:
        os.environ.pop("AI_AGENT_PROMPT_REFINEMENT_REQUIRED", None)
        assert_eq(PPR.strict_mode(), True, "strict mode should default on")

    _run()


def test_emit_block_for_codex_returns_json() -> None:
    import io

    original_stdout = sys.stdout
    capture = io.StringIO()
    sys.stdout = capture
    try:
        code = PPR.emit_block("codex", "timeout")
    finally:
        sys.stdout = original_stdout

    assert_eq(code, 0, "codex block should return zero with block payload")
    payload = json.loads(capture.getvalue())
    assert_eq(payload.get("decision"), "block", "codex block decision")
    assert "timeout" in str(payload.get("reason", ""))


def run_tests() -> int:
    tests = [
        test_auto_route_codex_to_claude,
        test_auto_route_claude_to_codex,
        test_explicit_provider_override,
        test_peer_invocation_claude_channel,
        test_peer_invocation_codex_channel,
        test_strict_mode_defaults_on,
        test_emit_block_for_codex_returns_json,
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
