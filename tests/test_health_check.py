#!/usr/bin/env python3
"""Focused tests for scripts/health-check.sh."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HEALTH_CHECK = REPO_ROOT / "scripts" / "health-check.sh"


def assert_eq(actual, expected, msg: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{msg}: expected {expected!r}, got {actual!r}")


def run_health_check(env: dict[str, str]) -> dict:
    result = subprocess.run(
        ["sh", str(HEALTH_CHECK), "--json"],
        cwd=REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_health_check_flags_mismatch_managed_and_legacy_dir() -> None:
    with tempfile.TemporaryDirectory(prefix="health-check-test-") as tmp:
        home = Path(tmp)
        claude_home = home / ".claude"
        codex_home = home / ".codex"
        gemini_home = home / ".gemini"
        skills_dir = home / ".agents" / "skills"
        legacy_dir = home / ".llm-config" / "hooks" / "scripts"

        claude_home.mkdir(parents=True)
        codex_home.mkdir(parents=True)
        gemini_home.mkdir(parents=True)
        skills_dir.mkdir(parents=True)
        legacy_dir.mkdir(parents=True)

        settings = {
            "hooks": {
                "PreToolUse": [
                    {
                        "_ai_agent_config_managed": True,
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}/scripts/safe_delete_guard.py" --current claude',
                                "timeout": 10,
                            }
                        ],
                    }
                ]
            }
        }
        (claude_home / "settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "AI_AGENT_CONFIG_HOME": str(REPO_ROOT),
                "AI_AGENT_CODEX_HOME": str(codex_home),
                "AI_AGENT_CLAUDE_HOME": str(claude_home),
                "AI_AGENT_GEMINI_HOME": str(gemini_home),
                "AI_AGENT_SKILLS_DIR": str(skills_dir),
                "AI_AGENT_HEALTH_REDACT": "0",
            }
        )

        payload = run_health_check(env)
        assert_eq(payload["links"]["claude-hooks"], "mismatch-managed", "legacy command should not pass as appended")
        assert_eq(payload["legacy"]["llm_config_dir"], "present", "legacy state dir should be reported")
        assert_eq(payload["overall"], "warn", "mismatch and legacy residue should warn")


TESTS = [test_health_check_flags_mismatch_managed_and_legacy_dir]


def main() -> int:
    failures: list[tuple[str, str]] = []
    for test in TESTS:
        try:
            test()
        except Exception:  # noqa: BLE001 - direct test runner needs broad capture
            failures.append((test.__name__, traceback.format_exc()))
    passed = len(TESTS) - len(failures)
    print(f"health-check tests: {passed}/{len(TESTS)} passed")
    if failures:
        for name, tb in failures:
            print(f"\n--- FAIL: {name} ---", file=sys.stderr)
            sys.stderr.write(tb)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
