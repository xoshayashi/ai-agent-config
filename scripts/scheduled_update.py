#!/usr/bin/env python3
"""Launchd-safe scheduled updater for ai-agent-config."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def say(message: str) -> None:
    print(message)


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def parse_flag(name: str, raw: str) -> bool:
    if raw not in {"0", "1"}:
        raise ValueError(f"{name} must be 0 or 1")
    return raw == "1"


def load_state_file(parser: Path, state_file: Path) -> tuple[dict[str, str], bool]:
    if not state_file.is_file():
        return {}, False
    if not parser.is_file():
        warn(f"state parser not found: {parser}")
        return {}, False

    result = subprocess.run(
        [sys.executable, str(parser), str(state_file)],
        cwd="/",
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown parser error"
        warn(f"state file could not be read safely: {state_file} ({detail})")
        return {}, False

    parsed: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition("\t")
        if key:
            parsed[key] = value
    return parsed, True


def git_bin() -> Optional[str]:
    if Path("/usr/bin/git").exists():
        return "/usr/bin/git"
    return shutil.which("git")


def format_command(args: list[str]) -> str:
    return " ".join(shlex.quote(arg) for arg in args)


def run_command(
    args: list[str],
    *,
    dry_run: bool,
    env: Optional[dict[str, str]] = None,
    capture_output: bool = False,
) -> Optional[subprocess.CompletedProcess[str]]:
    if dry_run:
        say(f"would run: {format_command(args)}")
        return None
    return subprocess.run(
        args,
        cwd="/",
        env=env,
        capture_output=capture_output,
        text=True,
        check=False,
    )


def run_git(
    git: str,
    config_home: Path,
    git_args: list[str],
    *,
    capture_output: bool = False,
    dry_run: bool = False,
) -> Optional[subprocess.CompletedProcess[str]]:
    args = [git, "-C", str(config_home), *git_args]
    return run_command(args, dry_run=dry_run, capture_output=capture_output)


def completed_stderr(proc: Optional[subprocess.CompletedProcess[str]]) -> str:
    if proc is None:
        return ""
    return (proc.stderr or "").strip()


def completed_stdout(proc: Optional[subprocess.CompletedProcess[str]]) -> str:
    if proc is None:
        return ""
    return (proc.stdout or "").strip()


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_config_home = script_dir.parent

    initial_state_dir = Path(os.path.expanduser(os.environ.get("AI_AGENT_STATE_DIR", "~/.ai-agent-config"))).resolve()
    initial_state_file = Path(
        os.path.expanduser(os.environ.get("AI_AGENT_STATE_FILE", str(initial_state_dir / "config.env")))
    ).resolve()

    parsed_state, state_loaded = load_state_file(script_dir / "read-state-config.py", initial_state_file)
    config = parsed_state.copy()
    config.update(os.environ)

    state_dir = Path(os.path.expanduser(config.get("AI_AGENT_STATE_DIR", str(initial_state_dir)))).resolve()
    state_file = Path(os.path.expanduser(config.get("AI_AGENT_STATE_FILE", str(initial_state_file)))).resolve()
    config_home = Path(os.path.expanduser(config.get("AI_AGENT_CONFIG_HOME", str(default_config_home)))).resolve()
    remote = config.get("AI_AGENT_UPDATE_REMOTE", "origin")
    branch = config.get("AI_AGENT_UPDATE_BRANCH", "main")

    try:
        dry_run = parse_flag("AI_AGENT_DRY_RUN", config.get("AI_AGENT_DRY_RUN", config.get("AI_AGENT_UPDATE_DRY_RUN", "0")))
        allow_dirty = parse_flag("AI_AGENT_UPDATE_ALLOW_DIRTY", config.get("AI_AGENT_UPDATE_ALLOW_DIRTY", "0"))
        rerun_setup = parse_flag("AI_AGENT_UPDATE_RERUN_SETUP", config.get("AI_AGENT_UPDATE_RERUN_SETUP", "1"))
        skip_when_dirty = parse_flag(
            "AI_AGENT_UPDATE_SKIP_WHEN_DIRTY",
            config.get("AI_AGENT_UPDATE_SKIP_WHEN_DIRTY", "1"),
        )
        skip_when_branch_mismatch = parse_flag(
            "AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH",
            config.get("AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH", "0"),
        )
    except ValueError as exc:
        return fail(str(exc))

    git = git_bin()
    if git is None:
        return fail("git is required")
    if not config_home.exists():
        return fail(f"config directory does not exist: {config_home}")

    say("AI agent config update")
    say(f"config: {config_home}")
    say(f"remote: {remote}")
    say(f"branch: {branch}")
    if not state_loaded:
        warn(f"state file not loaded; using environment/defaults: {state_file}")

    current_branch_proc = run_git(
        git,
        config_home,
        ["rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        dry_run=False,
    )
    if current_branch_proc is None:
        return fail("internal error: git branch check returned no result")
    if current_branch_proc.returncode != 0:
        detail = completed_stderr(current_branch_proc) or "unable to read current branch"
        return fail(detail)
    current_branch = completed_stdout(current_branch_proc)
    if current_branch != branch:
        message = (
            f"config repository is on '{current_branch}', not '{branch}'. "
            "Set AI_AGENT_UPDATE_BRANCH or switch branches before updating."
        )
        if skip_when_branch_mismatch:
            say(f"skip: {message}")
            return 0
        return fail(message)

    dirty_proc = run_git(
        git,
        config_home,
        ["status", "--porcelain"],
        capture_output=True,
        dry_run=False,
    )
    if dirty_proc is None:
        return fail("internal error: git status check returned no result")
    if dirty_proc.returncode != 0:
        detail = completed_stderr(dirty_proc) or "unable to inspect repository status"
        return fail(detail)
    dirty = bool(completed_stdout(dirty_proc))
    if dirty and not allow_dirty:
        message = (
            "config repository has local changes. Commit them, move them aside, "
            "or set AI_AGENT_UPDATE_ALLOW_DIRTY=1 if you know this is safe."
        )
        if skip_when_dirty:
            say(f"skip: {message}")
            return 0
        return fail(message)

    fetch_proc = run_git(git, config_home, ["fetch", remote, branch], dry_run=dry_run)
    if fetch_proc is not None and fetch_proc.returncode != 0:
        detail = completed_stderr(fetch_proc) or f"git fetch failed for {remote} {branch}"
        return fail(detail)

    merge_proc = run_git(git, config_home, ["merge", "--ff-only", "FETCH_HEAD"], dry_run=dry_run)
    if merge_proc is not None and merge_proc.returncode != 0:
        detail = completed_stderr(merge_proc) or "git merge --ff-only FETCH_HEAD failed"
        return fail(detail)

    if rerun_setup:
        say("re-apply setup")
        home = Path.home()
        # Keep scheduler registration enabled here so setup refreshes the
        # runtime wrappers and launchd/systemd definitions after an update.
        setup_env = os.environ.copy()
        setup_env.update(
            {
                "AI_AGENT_CONFIG_HOME": str(config_home),
                "AI_AGENT_CODEX_HOME": config.get("AI_AGENT_CODEX_HOME", str(home / ".codex")),
                "AI_AGENT_CLAUDE_HOME": config.get("AI_AGENT_CLAUDE_HOME", str(home / ".claude")),
                "AI_AGENT_GEMINI_HOME": config.get("AI_AGENT_GEMINI_HOME", str(home / ".gemini")),
                "AI_AGENT_SKILLS_DIR": config.get("AI_AGENT_SKILLS_DIR", str(home / ".agents" / "skills")),
                "AI_AGENT_EXTRA_SKILLS_DIRS": config.get("AI_AGENT_EXTRA_SKILLS_DIRS", ""),
                "AI_AGENT_INSTALL_INSTRUCTIONS": config.get("AI_AGENT_INSTALL_INSTRUCTIONS", "1"),
                "AI_AGENT_INSTALL_SKILLS": config.get("AI_AGENT_INSTALL_SKILLS", "1"),
                "AI_AGENT_INSTALL_HOOKS": config.get("AI_AGENT_INSTALL_HOOKS", "1"),
                "AI_AGENT_HOOKS_RUNTIME_LINK": config.get(
                    "AI_AGENT_HOOKS_RUNTIME_LINK", str(home / ".ai-agent-config" / "hooks")
                ),
                "AI_AGENT_CONFLICT_MODE": config.get("AI_AGENT_CONFLICT_MODE", "backup"),
                "AI_AGENT_REQUIRE_LLM_CLIS": config.get("AI_AGENT_REQUIRE_LLM_CLIS", "1"),
                "AI_AGENT_STATE_DIR": str(state_dir),
                "AI_AGENT_STATE_FILE": str(state_file),
                "AI_AGENT_DRY_RUN": "1" if dry_run else "0",
            }
        )
        setup_args = ["/bin/sh", str(config_home / "scripts" / "setup.sh")]
        setup_proc = run_command(setup_args, dry_run=dry_run, env=setup_env)
        if setup_proc is not None and setup_proc.returncode != 0:
            detail = completed_stderr(setup_proc) or "setup re-apply failed"
            return fail(detail)
    else:
        say("skip: setup re-apply disabled")

    say("update complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
