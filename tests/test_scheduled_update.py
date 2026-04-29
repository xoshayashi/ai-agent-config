#!/usr/bin/env python3
"""Focused tests for scripts/scheduled_update.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "scheduled_update.py"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["/usr/bin/git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def init_repo(root: Path, branch: str) -> Path:
    repo = root / "config-repo"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "config", "user.name", "Test User")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "checkout", "-b", branch)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "init")
    return repo


def run_runner(repo: Path, extra_env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="scheduled-update-home-") as tmp_home:
        home = Path(tmp_home)
        state_dir = home / ".ai-agent-config"
        state_dir.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "AI_AGENT_STATE_DIR": str(state_dir),
                "AI_AGENT_CONFIG_HOME": str(repo),
                "AI_AGENT_UPDATE_RERUN_SETUP": "0",
            }
        )
        env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )


def test_dirty_repo_is_skipped_by_default() -> None:
    with tempfile.TemporaryDirectory(prefix="scheduled-update-test-") as tmp:
        repo = init_repo(Path(tmp), "main")
        (repo / "local.txt").write_text("dirty\n", encoding="utf-8")
        result = run_runner(
            repo,
            {
                "AI_AGENT_UPDATE_BRANCH": "main",
            },
        )
        assert_true(result.returncode == 0, f"expected success, got rc={result.returncode}, stderr={result.stderr}")
        assert_true(
            "skip: config repository has local changes." in result.stdout,
            f"expected dirty skip message, stdout was: {result.stdout!r}",
        )


def test_branch_mismatch_is_skipped_by_default() -> None:
    with tempfile.TemporaryDirectory(prefix="scheduled-update-test-") as tmp:
        repo = init_repo(Path(tmp), "feature")
        result = run_runner(
            repo,
            {
                "AI_AGENT_UPDATE_BRANCH": "main",
            },
        )
        assert_true(result.returncode == 0, f"expected success, got rc={result.returncode}, stderr={result.stderr}")
        assert_true(
            "skip: config repository is on 'feature', not 'main'." in result.stdout,
            f"expected branch skip message, stdout was: {result.stdout!r}",
        )


TESTS = [
    test_dirty_repo_is_skipped_by_default,
    test_branch_mismatch_is_skipped_by_default,
]


def main() -> int:
    failures: list[tuple[str, str]] = []
    for test in TESTS:
        try:
            test()
        except Exception:  # noqa: BLE001 - direct-run test reporting
            failures.append((test.__name__, traceback.format_exc()))
    passed = len(TESTS) - len(failures)
    print(f"scheduled-update tests: {passed}/{len(TESTS)} passed")
    if failures:
        for name, tb in failures:
            print(f"\n--- FAIL: {name} ---", file=sys.stderr)
            sys.stderr.write(tb)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
