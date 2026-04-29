#!/usr/bin/env python3
"""Focused tests for scripts/autonomous_runner.py."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "autonomous_runner.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("autonomous_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("failed to load autonomous_runner module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNNER_MODULE = load_runner_module()


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


def git_stdout(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["/usr/bin/git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def init_repo(root: Path, branch: str = "main") -> Path:
    repo = root / "work"
    remote = root / "remote.git"
    repo.mkdir()
    subprocess.run(
        ["/usr/bin/git", "init", "--bare", str(remote)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    run_git(repo, "init")
    run_git(repo, "config", "user.name", "Test User")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "checkout", "-b", branch)
    run_git(repo, "remote", "add", "origin", str(remote))
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "init")
    run_git(repo, "push", "-u", "origin", branch)
    return repo


def init_workspace(root: Path) -> Path:
    workspace = root / "workspace"
    workspace.mkdir()
    return workspace


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def make_fake_provider(bin_dir: Path) -> None:
    script = textwrap.dedent(
        """\
        #!/usr/bin/env python3
        import json
        import os
        import sys
        from pathlib import Path

        repo = Path(os.environ["TEST_REPO"])
        phase = os.environ.get("AI_AGENT_RUNTIME_PHASE", "")
        payload = {
            "phase": phase,
            "backend": os.environ.get("AI_AGENT_DELIVERY_BACKEND", ""),
            "state_file": os.environ.get("AI_AGENT_STATE_FILE", ""),
            "workdir": os.environ.get("AI_AGENT_WORKDIR", ""),
        }
        (repo / ".provider-env.json").write_text(json.dumps(payload), encoding="utf-8")
        if phase == "work":
            (repo / "feature.txt").write_text("implemented\\n", encoding="utf-8")
            (repo / ".phase-state").write_text("opened\\n", encoding="utf-8")
        elif phase == "followup":
            (repo / "review.txt").write_text("review fixed\\n", encoding="utf-8")
            (repo / ".phase-state").write_text("ready\\n", encoding="utf-8")
        elif phase == "verify" and not (repo / "feature.txt").exists():
            print('RUNNER_RESULT: {"status":"failed","summary":"missing feature"}')
            raise SystemExit(0)
        print(json.dumps({"phase": phase}))
        print('RUNNER_RESULT: {"status":"completed","summary":"fake provider completed"}')
        """
    )
    write_executable(bin_dir / "fake-provider", script)


def make_fake_gh(bin_dir: Path) -> None:
    script = textwrap.dedent(
        """\
        #!/usr/bin/env python3
        import json
        import os
        import sys
        from pathlib import Path

        repo = Path(os.environ["TEST_REPO"])
        phase = (repo / ".phase-state").read_text(encoding="utf-8").strip() if (repo / ".phase-state").exists() else "opened"
        merged = (repo / ".merged").exists()
        review_required_only = (repo / ".review-required-only").exists()
        argv = sys.argv[1:]
        if argv[:3] == ["repo", "view", "--json"]:
            print(json.dumps({"nameWithOwner": "octo/test"}))
            sys.exit(0)
        if argv[:2] == ["pr", "create"]:
            print("https://example.invalid/pr/1")
            sys.exit(0)
        if argv[:5] == ["pr", "list", "--state", "open", "--head"]:
            print(json.dumps([{"number": 1, "url": "https://example.invalid/pr/1"}]))
            sys.exit(0)
        if argv[:2] == ["pr", "view"]:
            review_decision = "REVIEW_REQUIRED" if review_required_only else ("APPROVED" if phase == "ready" or merged else "CHANGES_REQUESTED")
            payload = {
                "number": 1,
                "title": "test pr",
                "url": "https://example.invalid/pr/1",
                "state": "MERGED" if merged else "OPEN",
                "closed": merged,
                "mergedAt": "2026-01-01T00:00:00Z" if merged else None,
                "isDraft": False,
                "mergeable": "MERGEABLE",
                "mergeStateStatus": "CLEAN",
                "reviewDecision": review_decision,
                "headRefOid": "abc123",
                "comments": [],
                "reviews": [],
            }
            print(json.dumps(payload))
            sys.exit(0)
        if argv[:2] == ["pr", "checks"]:
            if review_required_only or phase == "ready":
                print(json.dumps([{"name": "validate", "bucket": "pass", "state": "SUCCESS", "workflow": "test"}]))
                sys.exit(0)
            print(json.dumps([{"name": "validate", "bucket": "fail", "state": "FAILURE", "workflow": "test"}]))
            sys.exit(0)
        if argv[:2] == ["api", "graphql"]:
            if (repo / ".truth-fail").exists():
                print("graphql unavailable", file=sys.stderr)
                sys.exit(1)
            unresolved = 0 if review_required_only or phase == "ready" else 1
            print(json.dumps({
                "data": {
                    "repository": {
                        "pullRequest": {
                            "reviewThreads": {
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                                "nodes": [{"isResolved": unresolved == 0, "isOutdated": False}],
                            }
                        }
                    }
                }
            }))
            sys.exit(0)
        if argv[:2] == ["pr", "merge"]:
            if not (repo / ".never-merge").exists():
                (repo / ".merged").write_text("yes\\n", encoding="utf-8")
            print("merged")
            sys.exit(0)
        raise SystemExit(f"unsupported gh invocation: {argv}")
        """
    )
    write_executable(bin_dir / "gh", script)


def run_runner(workdir: Path, config: Path, extra_env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TEST_REPO"] = str(workdir)
    env["PATH"] = f"{extra_env['BIN_DIR']}{os.pathsep}{env['PATH']}"
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(RUNNER), "run", "--repo", str(workdir), "--config", str(config), *args],
        cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def write_config(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def extract_first_json_block(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    marker = "```json\n"
    start = content.find(marker)
    if start == -1:
        raise AssertionError(f"json code block not found in {path}")
    start += len(marker)
    end = content.find("\n```", start)
    if end == -1:
        raise AssertionError(f"json code block terminator not found in {path}")
    return json.loads(content[start:end])


def make_state(
    repo: Path,
    task: str,
    phase: str,
    delivery_backend: str,
    head_branch: str = "",
    artifacts: dict[str, object] | None = None,
    backend_state: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "version": 4,
        "run_id": "state-test",
        "repo": str(repo),
        "provider": "fake",
        "base_branch": "main",
        "origin_branch": "main",
        "head_branch": head_branch,
        "delivery_backend": delivery_backend,
        "task": task,
        "phase": phase,
        "status": "running",
        "counters": {"verification_retries": 0},
        "history": [],
        "artifacts": artifacts or {},
        "backend_state": backend_state or {},
        "last_verification": [],
    }


def test_workspace_backend_runs_without_git_repository() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": [{"type": "path_exists", "path": "feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Create feature.txt in a plain workspace.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["status"] == "completed", f"unexpected payload: {payload}")
        assert_true(payload["delivery_backend"] == "workspace", f"unexpected backend: {payload}")
        assert_true(payload["artifacts"] == {}, f"workspace backend should not publish artifacts: {payload}")
        assert_true((workspace / "feature.txt").is_file(), "provider did not create feature.txt")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["origin_branch"] == "", f"workspace backend should not require git state: {state}")
        assert_true(state["backend_state"] == {}, f"workspace backend should keep empty backend state: {state}")


def test_workspace_resume_does_not_add_github_namespaces() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": [{"type": "path_exists", "path": "feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "run_id": "workspace-state",
                    "created_at": "2026-04-29T00:00:00+00:00",
                    "updated_at": "2026-04-29T00:00:00+00:00",
                    "repo": str(workspace),
                    "provider": "fake",
                    "base_branch": "main",
                    "origin_branch": "",
                    "head_branch": "",
                    "delivery_backend": "workspace",
                    "task": "Resume a workspace run.",
                    "phase": "work",
                    "status": "running",
                    "counters": {"verification_retries": 0},
                    "history": [],
                    "artifacts": {},
                    "backend_state": {},
                    "last_verification": [],
                }
            ),
            encoding="utf-8",
        )
        result = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true("delivery" not in state["artifacts"], f"workspace resume should not add delivery artifacts: {state}")
        assert_true("github_pr" not in state["backend_state"], f"workspace resume should not add github backend state: {state}")


def test_branch_delivery_pushes_when_enabled() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "branch",
                    "backends": {"branch": {"push_branch": True}},
                },
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Implement feature.txt and deliver a branch.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        branch_info = payload["artifacts"]["delivery"]["branch"]
        assert_true(payload["delivery_backend"] == "branch", f"unexpected backend: {payload}")
        assert_true(branch_info["pushed"] is True, f"branch should be pushed: {payload}")
        remote_ref = git_stdout(repo, "rev-parse", "--verify", f"origin/{branch_info['name']}")
        assert_true(bool(remote_ref), "remote branch ref was not created")


def test_github_review_loop_merges_when_ready() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {
                        "github_pr": {
                            "allow_followup_fixes": True,
                            "allow_completion": True,
                            "review_policy": {"min_required_checks": 1},
                        }
                    },
                },
                "runtime": {
                    "max_verification_retries": 1,
                    "max_followup_retries": 2,
                    "max_pending_polls": 0,
                    "poll_interval_seconds": 0,
                },
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Implement feature.txt and resolve PR feedback until merge-ready.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["status"] == "completed", f"unexpected payload: {payload}")
        assert_true((repo / ".merged").is_file(), "merge step did not run")
        assert_true((repo / "review.txt").is_file(), "followup phase did not run")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        github_state = state["backend_state"]["github_pr"]
        assert_true(github_state["followup_retries"] == 1, f"unexpected followup count: {state}")
        assert_true(github_state["completion_requested"] is True, f"expected completion request to be recorded: {state}")


def test_followup_resume_switches_back_to_work_branch() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-followup")
        (repo / "feature.txt").write_text("implemented\n", encoding="utf-8")
        run_git(repo, "add", "feature.txt")
        run_git(repo, "commit", "-m", "feature")
        run_git(repo, "push", "-u", "origin", "auto/test-followup")
        run_git(repo, "checkout", "main")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {"github_pr": {"allow_followup_fixes": True, "allow_completion": False}},
                },
                "runtime": {"max_pending_polls": 0, "poll_interval_seconds": 0},
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "Resume a GitHub followup run safely.",
                    "followup",
                    "github_pr",
                    head_branch="auto/test-followup",
                    artifacts={"delivery": {"github_pr": {"pull_request": {"number": 1, "url": "https://example.invalid/pr/1"}}}},
                    backend_state={"github_pr": {"pr_ref": "1", "followup_retries": 0, "pending_polls": 0}},
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
            "--allow-dirty",
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        assert_true(git_stdout(repo, "branch", "--show-current") == "auto/test-followup", "runtime did not restore work branch")
        assert_true((repo / "review.txt").is_file(), "followup fix was not applied")


def test_provider_runtime_env_exposes_generic_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": [{"type": "path_exists", "path": "feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Inspect provider runtime env.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        env_payload = json.loads((workspace / ".provider-env.json").read_text(encoding="utf-8"))
        assert_true(env_payload["phase"] == "work", f"unexpected runtime phase: {env_payload}")
        assert_true(env_payload["backend"] == "workspace", f"unexpected backend env: {env_payload}")
        assert_true(Path(env_payload["state_file"]).name == state_file.name, f"unexpected state path env: {env_payload}")
        assert_true(Path(env_payload["workdir"]).resolve() == workspace.resolve(), f"unexpected workdir env: {env_payload}")


def test_resume_identity_requires_force() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "branch"},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "Old task",
                    "sync",
                    "branch",
                    head_branch="auto/identity",
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Different task",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode != 0, "resume with mismatched task should fail")
        assert_true("mismatched state metadata" in result.stderr, f"unexpected stderr: {result.stderr}")


def test_verification_string_shorthand_maps_to_shell_step() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": ["test -f feature.txt"]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Use shorthand verification syntax.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["last_verification"][0]["type"] == "shell", f"string verification shorthand did not normalize: {state}")


def test_builtin_provider_templates_follow_generic_placeholder_contract() -> None:
    example = json.loads((REPO_ROOT / "docs" / "examples" / "autonomous-runner.example.json").read_text(encoding="utf-8"))
    providers = example["providers"]
    for name in ["codex", "claude", "gemini"]:
        template = providers[name]
        assert_true(isinstance(template, list) and template, f"missing provider template: {name}")
        assert_true(any("{prompt}" in part for part in template), f"{name} template should include prompt placeholder")
        rendered = RUNNER_MODULE.substitute_template(
            template,
            {
                "repo": "/tmp/repo",
                "prompt": "do work",
                "state_file": "/tmp/state.json",
                "provider": name,
            },
        )
        assert_true(all("{" not in part for part in rendered), f"{name} template left unresolved placeholders: {rendered}")


def test_example_config_uses_namespaced_backend_settings() -> None:
    example = json.loads((REPO_ROOT / "docs" / "examples" / "autonomous-runner.example.json").read_text(encoding="utf-8"))
    delivery = example["delivery"]
    branch_cfg = delivery["backends"]["branch"]
    github_cfg = delivery["backends"]["github_pr"]
    assert_true(delivery["backend"] == "workspace", "example config should default to workspace backend")
    assert_true(branch_cfg["push_branch"] is False, "branch backend should default to local delivery")
    assert_true(github_cfg["allow_completion"] is False, "github backend should default to merge disabled")
    assert_true(isinstance(github_cfg["review_policy"], dict), "github backend should namespace review policy")


def test_doc_config_example_matches_example_file() -> None:
    example = json.loads((REPO_ROOT / "docs" / "examples" / "autonomous-runner.example.json").read_text(encoding="utf-8"))
    doc_example = extract_first_json_block(REPO_ROOT / "docs" / "autonomous-runner.md")
    assert_true(doc_example == example, "markdown config example drifted from the canonical example file")


def test_legacy_config_shape_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "workflow": {"allow_push": True},
                "validation": {"commands": ["test -f feature.txt"]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Reject legacy config.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode != 0, "legacy config shape should be rejected")
        assert_true("unsupported legacy config shape" in result.stderr, f"unexpected stderr: {result.stderr}")


def test_legacy_state_schema_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": [{"type": "path_exists", "path": "feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                {
                    "version": 3,
                    "run_id": "legacy-state",
                    "repo": str(repo),
                    "provider": "fake",
                    "base_branch": "main",
                    "task": "Legacy state",
                    "phase": "implement",
                    "status": "running",
                }
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode != 0, "legacy state schema should be rejected")
        assert_true("unsupported state schema" in result.stderr, f"unexpected stderr: {result.stderr}")


def test_semantic_provider_blocker_is_respected() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        blocking = textwrap.dedent(
            """\
            #!/usr/bin/env python3
            print('RUNNER_RESULT: {"status":"blocked","blocker_class":"missing_credentials","summary":"Need API key"}')
            """
        )
        write_executable(bin_dir / "fake-provider", blocking)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        result = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "This should block semantically.",
            "--state-file",
            str(state_file),
        )
        assert_true(result.returncode == 2, f"runtime should have blocked, rc={result.returncode}, stderr={result.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["status"] == "blocked", f"unexpected state: {state}")
        assert_true(state["blocker_class"] == "missing_credentials", f"unexpected blocker: {state}")


def test_blocked_state_can_resume_after_fix() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        workspace = init_workspace(root)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        blocking = textwrap.dedent(
            """\
            #!/usr/bin/env python3
            print('RUNNER_RESULT: {"status":"blocked","blocker_class":"missing_credentials","summary":"Need API key"}')
            """
        )
        write_executable(bin_dir / "fake-provider", blocking)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "workspace"},
                "verification": {"steps": [{"type": "path_exists", "path": "feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        first = run_runner(
            workspace,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--task",
            "Block once, then resume.",
            "--state-file",
            str(state_file),
        )
        assert_true(first.returncode == 2, f"first run should block: rc={first.returncode}, stderr={first.stderr}")
        make_fake_provider(bin_dir)
        resumed = run_runner(workspace, config, {"BIN_DIR": str(bin_dir)}, "--state-file", str(state_file))
        assert_true(resumed.returncode == 0, f"resumed run failed: rc={resumed.returncode}, stderr={resumed.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["status"] == "completed", f"blocked state did not resume cleanly: {state}")


def test_review_truth_failure_blocks_immediately() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-truth")
        (repo / "feature.txt").write_text("implemented\n", encoding="utf-8")
        run_git(repo, "add", "feature.txt")
        run_git(repo, "commit", "-m", "feature")
        run_git(repo, "push", "-u", "origin", "auto/test-truth")
        (repo / ".truth-fail").write_text("1\n", encoding="utf-8")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {"github_pr": {"allow_followup_fixes": True, "allow_completion": False}},
                },
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "Stop when review truth is unavailable.",
                    "followup",
                    "github_pr",
                    head_branch="auto/test-truth",
                    artifacts={"delivery": {"github_pr": {"pull_request": {"number": 1, "url": "https://example.invalid/pr/1"}}}},
                    backend_state={"github_pr": {"pr_ref": "1", "followup_retries": 0, "pending_polls": 0}},
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
            "--allow-dirty",
        )
        assert_true(result.returncode == 2, f"runtime should have blocked, rc={result.returncode}, stderr={result.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["blocker_class"] == "review_truth_unavailable", f"unexpected blocker: {state}")


def test_review_truth_is_optional_when_policy_disables_thread_gate() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-truth-optional")
        (repo / "feature.txt").write_text("implemented\n", encoding="utf-8")
        run_git(repo, "add", "feature.txt")
        run_git(repo, "commit", "-m", "feature")
        run_git(repo, "push", "-u", "origin", "auto/test-truth-optional")
        (repo / ".phase-state").write_text("ready\n", encoding="utf-8")
        (repo / ".truth-fail").write_text("1\n", encoding="utf-8")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {
                        "github_pr": {
                            "allow_followup_fixes": False,
                            "allow_completion": False,
                            "review_policy": {
                                "require_zero_unresolved_threads": False,
                                "min_required_checks": 1,
                            },
                        }
                    },
                },
                "runtime": {"max_pending_polls": 0, "poll_interval_seconds": 0},
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "Do not block when thread truth is optional.",
                    "followup",
                    "github_pr",
                    head_branch="auto/test-truth-optional",
                    artifacts={"delivery": {"github_pr": {"pull_request": {"number": 1, "url": "https://example.invalid/pr/1"}}}},
                    backend_state={"github_pr": {"pr_ref": "1", "followup_retries": 0, "pending_polls": 0}},
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
            "--allow-dirty",
        )
        assert_true(result.returncode == 0, f"runtime should complete when thread truth is optional: rc={result.returncode}, stderr={result.stderr}")


def test_merge_pending_blocks_when_auto_merge_does_not_finish() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-merge-pending")
        (repo / "feature.txt").write_text("implemented\n", encoding="utf-8")
        run_git(repo, "add", "feature.txt")
        run_git(repo, "commit", "-m", "feature")
        run_git(repo, "push", "-u", "origin", "auto/test-merge-pending")
        (repo / ".phase-state").write_text("ready\n", encoding="utf-8")
        (repo / ".never-merge").write_text("1\n", encoding="utf-8")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {
                        "github_pr": {
                            "allow_followup_fixes": False,
                            "allow_completion": True,
                            "review_policy": {"min_required_checks": 1},
                        }
                    },
                },
                "runtime": {"max_pending_polls": 0, "poll_interval_seconds": 0},
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "Auto-merge should not complete early.",
                    "followup",
                    "github_pr",
                    head_branch="auto/test-merge-pending",
                    artifacts={"delivery": {"github_pr": {"pull_request": {"number": 1, "url": "https://example.invalid/pr/1"}}}},
                    backend_state={"github_pr": {"pr_ref": "1", "followup_retries": 0, "pending_polls": 0}},
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
            "--allow-dirty",
        )
        assert_true(result.returncode == 2, f"runtime should have blocked, rc={result.returncode}, stderr={result.stderr}")
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert_true(state["blocker_class"] == "merge_pending", f"unexpected blocker: {state}")


def test_no_merge_flag_overrides_completion() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-no-merge-flag")
        (repo / "feature.txt").write_text("implemented\n", encoding="utf-8")
        run_git(repo, "add", "feature.txt")
        run_git(repo, "commit", "-m", "feature")
        run_git(repo, "push", "-u", "origin", "auto/test-no-merge-flag")
        (repo / ".phase-state").write_text("ready\n", encoding="utf-8")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_provider(bin_dir)
        make_fake_gh(bin_dir)
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {
                    "backend": "github_pr",
                    "backends": {
                        "github_pr": {
                            "allow_followup_fixes": False,
                            "allow_completion": True,
                            "review_policy": {"min_required_checks": 1},
                        }
                    },
                },
                "runtime": {"max_pending_polls": 0, "poll_interval_seconds": 0},
                "verification": {"steps": [{"type": "shell", "command": "test -f feature.txt"}]},
                "providers": {"fake": ["fake-provider", "{prompt}"]},
            },
        )
        state = make_state(
            repo,
            "No-merge flag should disable completion.",
            "followup",
            "github_pr",
            head_branch="auto/test-no-merge-flag",
            artifacts={"delivery": {"github_pr": {"pull_request": {"number": 1, "url": "https://example.invalid/pr/1"}}}},
            backend_state={"github_pr": {"pr_ref": "1", "followup_retries": 0, "pending_polls": 0}},
        )
        state_file.write_text(json.dumps(state), encoding="utf-8")
        result = run_runner(
            repo,
            config,
            {"BIN_DIR": str(bin_dir)},
            "--state-file",
            str(state_file),
            "--allow-dirty",
            "--no-completion",
        )
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        assert_true(not (repo / ".merged").exists(), "no-merge flag should suppress completion")


def test_followup_phase_completes_when_backend_has_no_adapter() -> None:
    with tempfile.TemporaryDirectory(prefix="autonomous-runtime-") as tmp:
        root = Path(tmp)
        repo = init_repo(root)
        run_git(repo, "checkout", "-b", "auto/test-no-followup")
        config = root / "runtime.json"
        state_file = root / "state.json"
        write_config(
            config,
            {
                "provider": "fake",
                "delivery": {"backend": "branch"},
                "providers": {"fake": ["python3", "-c", "print('RUNNER_RESULT: {\"status\":\"completed\",\"summary\":\"ok\"}')"]},
            },
        )
        state_file.write_text(
            json.dumps(
                make_state(
                    repo,
                    "No followup adapter should still complete cleanly.",
                    "followup",
                    "branch",
                    head_branch="auto/test-no-followup",
                )
            ),
            encoding="utf-8",
        )
        result = run_runner(repo, config, {"BIN_DIR": str(root / "bin")}, "--state-file", str(state_file))
        assert_true(result.returncode == 0, f"runtime failed: rc={result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["status"] == "completed", f"unexpected payload: {payload}")


TESTS = [
    test_workspace_backend_runs_without_git_repository,
    test_workspace_resume_does_not_add_github_namespaces,
    test_branch_delivery_pushes_when_enabled,
    test_github_review_loop_merges_when_ready,
    test_followup_resume_switches_back_to_work_branch,
    test_provider_runtime_env_exposes_generic_contract,
    test_resume_identity_requires_force,
    test_verification_string_shorthand_maps_to_shell_step,
    test_builtin_provider_templates_follow_generic_placeholder_contract,
    test_example_config_uses_namespaced_backend_settings,
    test_doc_config_example_matches_example_file,
    test_legacy_config_shape_is_rejected,
    test_legacy_state_schema_is_rejected,
    test_semantic_provider_blocker_is_respected,
    test_blocked_state_can_resume_after_fix,
    test_review_truth_failure_blocks_immediately,
    test_review_truth_is_optional_when_policy_disables_thread_gate,
    test_merge_pending_blocks_when_auto_merge_does_not_finish,
    test_no_merge_flag_overrides_completion,
    test_followup_phase_completes_when_backend_has_no_adapter,
]


def main() -> int:
    failures: list[tuple[str, str]] = []
    for test in TESTS:
        try:
            test()
        except Exception:  # noqa: BLE001 - direct-run test reporting
            failures.append((test.__name__, traceback.format_exc()))
    passed = len(TESTS) - len(failures)
    print(f"autonomous-runner tests: {passed}/{len(TESTS)} passed")
    if failures:
        for name, tb in failures:
            print(f"\n--- FAIL: {name} ---", file=sys.stderr)
            sys.stderr.write(tb)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
