#!/usr/bin/env python3
"""Optional autonomous runtime for whole-task coding loops.

This runtime keeps orchestration outside Hooks. It drives one task through:

work -> verify -> sync -> followup

The core is generic. Backend capabilities and verification step registries own
backend- and check-specific behavior.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 4,
    "provider": "codex",
    "base_branch": "main",
    "state_dir": "~/.ai-agent-config/runner",
    "runtime": {
        "branch_prefix": "auto/",
        "max_verification_retries": 2,
        "max_followup_retries": 2,
        "poll_interval_seconds": 20,
        "max_pending_polls": 15,
        "provider_timeout_seconds": None,
    },
    "delivery": {
        "backend": "workspace",
        "backends": {
            "workspace": {},
            "branch": {
                "push_branch": False,
                "commit_message_prefix": "Autonomous runtime:",
            },
            "github_pr": {
                "push_branch": True,
                "allow_followup_fixes": False,
                "allow_completion": False,
                "commit_message_prefix": "Autonomous runtime:",
                "pr_title_prefix": "[auto]",
                "completion_method": "squash",
                "review_policy": {
                    "require_zero_unresolved_threads": True,
                    "required_checks_only": True,
                    "min_required_checks": 0,
                },
            },
        },
    },
    "verification": {
        "steps": [],
    },
    "providers": {
        "codex": [
            "codex",
            "exec",
            "--cd",
            "{repo}",
            "--full-auto",
            "{prompt}",
        ],
        "claude": [
            "claude",
            "-p",
            "{prompt}",
            "--permission-mode",
            "bypassPermissions",
        ],
        "gemini": [
            "gemini",
            "-p",
            "{prompt}",
            "--approval-mode",
            "yolo",
            "--skip-trust",
        ],
    },
}


TERMINAL_STATES = {"completed", "failed"}
FAILED_CHECK_BUCKETS = {"fail", "cancel"}
PENDING_CHECK_BUCKETS = {"pending"}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an autonomous headless workflow runtime.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run or resume an autonomous workflow.")
    run.add_argument("--repo", default=".", help="Working directory to operate on.")
    run.add_argument("--config", default=os.getenv("AI_AGENT_AUTONOMOUS_RUNNER_CONFIG", "~/.ai-agent-config/autonomous-runner.json"))
    run.add_argument("--provider", choices=["codex", "claude", "gemini"], default="")
    run.add_argument("--task", default="", help="Task brief. If empty, stdin is used when available.")
    run.add_argument("--task-file", default="", help="Read the task brief from a file.")
    run.add_argument("--state-file", default="", help="Persist state here; resume if the file already exists.")
    run.add_argument("--trace-json", default="", help="Append JSONL trace events to this file.")
    run.add_argument("--dry-run", action="store_true", default=os.getenv("AI_AGENT_DRY_RUN") == "1")
    run.add_argument("--allow-dirty", action="store_true", default=os.getenv("AI_AGENT_AUTONOMOUS_RUNNER_ALLOW_DIRTY") == "1")
    run.add_argument("--allow-completion", dest="allow_completion", action="store_true", default=False, help="Override config to allow completion for this run.")
    run.add_argument("--no-completion", dest="no_completion", action="store_true", default=False, help="Override config to disable completion for this run.")
    run.add_argument("--force-resume", action="store_true", default=False, help="Allow resuming even when repo/provider/base/task metadata differ.")
    return parser.parse_args()


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value))


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deep_copy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"error: config must be a JSON object: {path}")
    return data


def reject_legacy_config_shape(raw: dict[str, Any], path: Path) -> None:
    legacy_top_level = [key for key in ["workflow", "validation", "review"] if key in raw]
    delivery = raw.get("delivery")
    legacy_delivery_keys: list[str] = []
    if isinstance(delivery, dict):
        legacy_delivery_keys = [key for key in ["target", "push_branch", "allow_review_fix", "allow_merge", "commit_message_prefix", "pr_title_prefix", "merge_method"] if key in delivery]
    legacy_keys = legacy_top_level + [f"delivery.{key}" for key in legacy_delivery_keys]
    if legacy_keys:
        raise SystemExit(
            f"error: unsupported legacy config shape in {path}: "
            + ", ".join(legacy_keys)
            + ". Rewrite the file to the current delivery.backends / verification.steps schema."
        )


def normalize_verification_steps(config: dict[str, Any]) -> list[dict[str, Any]]:
    raw = config.get("verification", {}).get("steps", [])
    if not isinstance(raw, list):
        raise SystemExit("error: verification.steps must be a list")
    steps: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if isinstance(item, str):
            step = {"type": "shell", "command": item}
        elif isinstance(item, dict):
            step = dict(item)
        else:
            raise SystemExit(f"error: verification step #{index + 1} must be a string or object")
        step_type = str(step.get("type") or "shell")
        if step_type not in VERIFICATION_REGISTRY:
            raise SystemExit(f"error: unsupported verification step type: {step_type}")
        if step_type == "shell" and not str(step.get("command") or "").strip():
            raise SystemExit(f"error: verification step #{index + 1} missing command")
        if step_type == "path_exists" and not str(step.get("path") or "").strip():
            raise SystemExit(f"error: verification step #{index + 1} missing path")
        step["type"] = step_type
        steps.append(step)
    return steps


def load_config(path: Path, provider_override: str, allow_completion: bool, no_completion: bool) -> dict[str, Any]:
    raw = load_json(path)
    reject_legacy_config_shape(raw, path)
    config = merge_dicts(DEFAULT_CONFIG, raw)
    if provider_override:
        config["provider"] = provider_override
    backend = delivery_backend_name(config)
    if backend not in BACKEND_TEMPLATES:
        raise SystemExit(f"error: unsupported delivery.backend: {backend}")
    if allow_completion:
        ensure_backend_options(config)["allow_completion"] = True
    if no_completion:
        ensure_backend_options(config)["allow_completion"] = False
    config["verification"]["steps"] = normalize_verification_steps(config)
    return config


def read_task(args: argparse.Namespace) -> str:
    if args.task_file:
        return Path(args.task_file).read_text(encoding="utf-8").strip()
    if args.task:
        return args.task.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def ensure_task(task: str, state_path: Path) -> None:
    if task:
        return
    if state_path.is_file():
        return
    raise SystemExit("error: task is required for a new run")


def delivery_backend_name(config: dict[str, Any]) -> str:
    return str(config.get("delivery", {}).get("backend", "workspace"))


def ensure_backend_options(config: dict[str, Any], backend: str | None = None) -> dict[str, Any]:
    name = backend or delivery_backend_name(config)
    delivery = config.setdefault("delivery", {})
    backends = delivery.setdefault("backends", {})
    backend_map = backends.setdefault(name, {})
    if not isinstance(backend_map, dict):
        raise SystemExit(f"error: delivery.backends.{name} must be an object")
    return backend_map


def backend_options(config: dict[str, Any], backend: str | None = None) -> dict[str, Any]:
    return dict(ensure_backend_options(config, backend))


def review_policy_for(config: dict[str, Any], backend: str) -> dict[str, Any]:
    return dict(backend_options(config, backend).get("review_policy", {}))


@dataclass(frozen=True)
class DeliveryBackendTemplate:
    name: str
    needs_git: bool
    needs_branch: bool
    supports_push_branch: bool
    supports_pull_request: bool
    publication_adapter: str | None
    followup_adapter: str | None
    required_tools: tuple[str, ...]


@dataclass(frozen=True)
class DeliveryPlan:
    backend: str
    needs_git: bool
    needs_branch: bool
    required_tools: tuple[str, ...]
    push_branch: bool
    open_pull_request: bool
    publication_adapter: str | None
    allow_followup_fixes: bool
    allow_completion: bool
    followup_adapter: str | None
    commit_message_prefix: str
    pr_title_prefix: str
    completion_method: str

    @property
    def requires_sync(self) -> bool:
        return self.needs_branch or self.open_pull_request or self.push_branch


@dataclass(frozen=True)
class VerificationStepSpec:
    name: str
    describe: Callable[[dict[str, Any]], str]
    execute: Callable[[Path, dict[str, Any], bool], dict[str, Any]]
    render_failure: Callable[[dict[str, Any]], list[str]]


BACKEND_TEMPLATES: dict[str, DeliveryBackendTemplate] = {
    "workspace": DeliveryBackendTemplate("workspace", needs_git=False, needs_branch=False, supports_push_branch=False, supports_pull_request=False, publication_adapter=None, followup_adapter=None, required_tools=()),
    "branch": DeliveryBackendTemplate("branch", needs_git=True, needs_branch=True, supports_push_branch=True, supports_pull_request=False, publication_adapter=None, followup_adapter=None, required_tools=("git",)),
    "github_pr": DeliveryBackendTemplate("github_pr", needs_git=True, needs_branch=True, supports_push_branch=True, supports_pull_request=True, publication_adapter="github_pr", followup_adapter="github_pr", required_tools=("git", "gh")),
}


def resolve_repo_path(repo: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo / path


def describe_shell_step(step: dict[str, Any]) -> str:
    return f"shell: {step['command']}"


def execute_shell_step(repo: Path, step: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    result = run_command(["/bin/sh", "-c", str(step["command"])], repo, dry_run=dry_run, check=False)
    success = result.returncode == 0
    return {
        "type": "shell",
        "step": describe_shell_step(step),
        "status": "passed" if success else "failed",
        "summary": "command passed" if success else "command failed",
        "evidence": {
            "command": str(step["command"]),
            "returncode": result.returncode,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
        },
    }


def render_shell_failure(result: dict[str, Any]) -> list[str]:
    evidence = dict(result.get("evidence", {}))
    lines = [f"- Step: {result['step']}", f"  summary: {result.get('summary', 'failed')}"]
    if evidence.get("stdout"):
        lines.append("  stdout:")
        lines.extend(f"    {line}" for line in str(evidence["stdout"]).splitlines()[:20])
    if evidence.get("stderr"):
        lines.append("  stderr:")
        lines.extend(f"    {line}" for line in str(evidence["stderr"]).splitlines()[:20])
    return lines


def describe_path_exists_step(step: dict[str, Any]) -> str:
    return f"path_exists: {step['path']}"


def execute_path_exists_step(repo: Path, step: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    target = resolve_repo_path(repo, str(step["path"]))
    exists = True if dry_run else target.exists()
    return {
        "type": "path_exists",
        "step": describe_path_exists_step(step),
        "status": "passed" if exists else "failed",
        "summary": f"path {'exists' if exists else 'is missing'}: {target}",
        "evidence": {
            "path": str(target),
            "exists": exists,
        },
    }


def render_path_exists_failure(result: dict[str, Any]) -> list[str]:
    return [f"- Step: {result['step']}", f"  summary: {result.get('summary', 'path missing')}"]


VERIFICATION_REGISTRY: dict[str, VerificationStepSpec] = {
    "shell": VerificationStepSpec("shell", describe_shell_step, execute_shell_step, render_shell_failure),
    "path_exists": VerificationStepSpec("path_exists", describe_path_exists_step, execute_path_exists_step, render_path_exists_failure),
}


def resolve_delivery_plan(config: dict[str, Any]) -> DeliveryPlan:
    backend = delivery_backend_name(config)
    template = BACKEND_TEMPLATES[backend]
    options = backend_options(config, backend)
    push_branch = template.supports_pull_request or (
        template.supports_push_branch and bool(options.get("push_branch", False))
    )
    allow_followup_fixes = template.supports_pull_request and bool(options.get("allow_followup_fixes", False))
    allow_completion = template.supports_pull_request and bool(options.get("allow_completion", False))
    return DeliveryPlan(
        backend=backend,
        needs_git=template.needs_git,
        needs_branch=template.needs_branch,
        required_tools=template.required_tools,
        push_branch=push_branch,
        open_pull_request=template.supports_pull_request,
        publication_adapter=template.publication_adapter,
        allow_followup_fixes=allow_followup_fixes,
        allow_completion=allow_completion,
        followup_adapter=template.followup_adapter,
        commit_message_prefix=str(options.get("commit_message_prefix", "Autonomous runtime:")),
        pr_title_prefix=str(options.get("pr_title_prefix", "[auto]")),
        completion_method=str(options.get("completion_method", "squash")),
    )


def state_file_for(config: dict[str, Any], explicit: str) -> Path:
    if explicit:
        return expand_path(explicit)
    state_dir = expand_path(str(config["state_dir"]))
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json"


def current_branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current").stdout.strip()


def initial_head_branch(config: dict[str, Any]) -> str:
    if not resolve_delivery_plan(config).needs_branch:
        return ""
    prefix = str(config.get("runtime", {}).get("branch_prefix", "auto/"))
    return f"{prefix}{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"


def load_or_init_state(
    state_path: Path,
    repo: Path,
    task: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    if state_path.is_file():
        with state_path.open(encoding="utf-8") as handle:
            state = json.load(handle)
        if not isinstance(state, dict):
            raise SystemExit(f"error: state file must contain a JSON object: {state_path}")
        version = state.get("version")
        phase = str(state.get("phase") or "")
        if version != 4 or phase not in {"work", "verify", "sync", "followup", "completed", "failed", "blocked"}:
            raise SystemExit(f"error: unsupported state schema in {state_path}; rerun with a fresh v4 state file")
        return state

    plan = resolve_delivery_plan(config)
    origin_branch = current_branch(repo) if plan.needs_git else ""
    return {
        "version": 4,
        "run_id": uuid.uuid4().hex,
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "repo": str(repo),
        "provider": config["provider"],
        "base_branch": config["base_branch"],
        "origin_branch": origin_branch,
        "head_branch": initial_head_branch(config),
        "delivery_backend": plan.backend,
        "task": task,
        "phase": "work",
        "status": "running",
        "counters": {"verification_retries": 0},
        "history": [],
        "artifacts": {},
        "backend_state": {},
        "last_verification": [],
    }


def validate_resume_identity(
    state: dict[str, Any],
    repo: Path,
    task: str,
    config: dict[str, Any],
    force_resume: bool,
) -> None:
    mismatches: list[str] = []
    stored_repo = str(state.get("repo") or "")
    if stored_repo and Path(stored_repo).resolve() != repo:
        mismatches.append(f"repo mismatch: state={stored_repo} current={repo}")
    stored_provider = str(state.get("provider") or "")
    if stored_provider and stored_provider != str(config["provider"]):
        mismatches.append(f"provider mismatch: state={stored_provider} current={config['provider']}")
    stored_base = str(state.get("base_branch") or "")
    if stored_base and stored_base != str(config["base_branch"]):
        mismatches.append(f"base branch mismatch: state={stored_base} current={config['base_branch']}")
    if task and str(state.get("task") or "") != task:
        mismatches.append("task mismatch between state file and current request")
    if mismatches and not force_resume:
        raise SystemExit(
            "error: refusing to resume with mismatched state metadata. "
            "Re-run with --force-resume only if this is intentional. "
            + "; ".join(mismatches)
        )


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_utc()
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def append_trace(trace_path: Path | None, event: dict[str, Any]) -> None:
    if trace_path is None:
        return
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        json.dump(event, handle, ensure_ascii=False)
        handle.write("\n")


def record_event(state: dict[str, Any], trace_path: Path | None, kind: str, **payload: Any) -> None:
    event = {"timestamp": now_utc(), "kind": kind, "phase": state.get("phase"), **payload}
    state.setdefault("history", []).append(event)
    append_trace(trace_path, event)


def format_command(args: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in args)


def require_tool(command: str) -> None:
    if Path(command).is_absolute():
        if Path(command).exists():
            return
    elif shutil.which(command):
        return
    raise SystemExit(f"error: required tool is not available on PATH: {command}")


def run_command(
    args: list[str],
    cwd: Path,
    *,
    dry_run: bool = False,
    capture_output: bool = True,
    check: bool = False,
    env_overrides: dict[str, str] | None = None,
    timeout_seconds: float | None = None,
) -> subprocess.CompletedProcess[str]:
    if dry_run:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=f"dry-run: {format_command(args)}\n", stderr="")
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=capture_output,
            check=False,
            env=env,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        missing = exc.filename or args[0]
        raise SystemExit(f"error: required tool is not available on PATH: {missing}") from exc
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise SystemExit(f"error: command failed: {format_command(args)}\n{detail}")
    return result


def git(repo: Path, *git_args: str, dry_run: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_command(["git", *git_args], repo, dry_run=dry_run, check=check)


def working_tree_dirty(repo: Path) -> bool:
    return bool(git(repo, "status", "--porcelain").stdout.strip())


def ensure_clean(repo: Path, allow_dirty: bool) -> None:
    if working_tree_dirty(repo) and not allow_dirty:
        raise SystemExit("error: repository has local changes; rerun with --allow-dirty only when this automation owns them")


def checkout_base_if_needed(repo: Path, base_branch: str, dry_run: bool) -> None:
    branch = current_branch(repo)
    if branch == base_branch:
        return
    git(repo, "switch", base_branch, dry_run=dry_run)


def branch_exists(repo: Path, branch: str) -> bool:
    result = git(repo, "rev-parse", "--verify", "--quiet", branch, check=False)
    return result.returncode == 0


def ensure_work_branch(repo: Path, state: dict[str, Any], dry_run: bool) -> None:
    head_branch = str(state.get("head_branch") or "")
    if not head_branch:
        return
    if branch_exists(repo, head_branch):
        git(repo, "switch", head_branch, dry_run=dry_run)
        return
    checkout_base_if_needed(repo, str(state["base_branch"]), dry_run)
    git(repo, "switch", "-c", head_branch, dry_run=dry_run)


def summarize_task(task: str, limit: int = 72) -> str:
    one_line = " ".join(task.split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 3].rstrip() + "..."


def substitute_template(parts: list[str], values: dict[str, str]) -> list[str]:
    return [part.format(**values) for part in parts]


def build_provider_command(config: dict[str, Any], provider: str, repo: Path, prompt: str, state_path: Path) -> list[str]:
    providers = config.get("providers", {})
    template = providers.get(provider)
    if not isinstance(template, list) or not template:
        raise SystemExit(f"error: missing provider command template for {provider}")
    return substitute_template(
        [str(item) for item in template],
        {
            "repo": str(repo),
            "prompt": prompt,
            "state_file": str(state_path),
            "provider": provider,
        },
    )


def describe_verification_steps(steps: list[dict[str, Any]]) -> list[str]:
    return [VERIFICATION_REGISTRY[str(step["type"])].describe(step) for step in steps]


def build_work_prompt(state: dict[str, Any], config: dict[str, Any]) -> str:
    steps = describe_verification_steps(list(config.get("verification", {}).get("steps", [])))
    backend = delivery_backend_name(config)
    lines = [
        f"You are executing an autonomous task in working directory: {state['repo']}",
        "",
        "Task:",
        state["task"],
        "",
        "Rules:",
        "- Make routine implementation decisions autonomously.",
        "- Use local tools, repository tools, and in-scope external services when they are needed to complete the task.",
        "- Pause only if the next step truly requires missing credentials, an ambiguous target, or a policy block.",
        "- Do not perform final git delivery such as branch publication, PR creation, or merge; the external runtime owns that.",
        "- Respect repository instructions and safe deletion rules.",
        "",
        f"Delivery backend after verification: {backend}",
    ]
    if steps:
        lines.append("- Prefer to run relevant verification while working when useful.")
        lines.append("Verification steps the runtime will also execute:")
        lines.extend(f"  - {item}" for item in steps)
    lines.extend(
        [
            "",
            "Finish by printing a concise summary of the work completed and any remaining risk.",
            'End with one exact line: RUNNER_RESULT: {"status":"completed","summary":"..."}',
            'If you must stop for missing credentials, ambiguous target selection, or a policy block, end with: RUNNER_RESULT: {"status":"blocked","blocker_class":"missing_credentials|ambiguous_target|policy_block","summary":"..."}',
        ]
    )
    return "\n".join(lines)


def build_verification_fix_prompt(state: dict[str, Any], failures: list[dict[str, Any]]) -> str:
    lines = [
        f"You are fixing verification failures in working directory: {state['repo']}",
        "",
        "Original task:",
        state["task"],
        "",
        "Address only the issues required to make the verification steps pass.",
        "Do not perform final git delivery such as branch publication, PR creation, or merge.",
        "",
        "Failing verification steps:",
    ]
    for item in failures:
        renderer = VERIFICATION_REGISTRY[str(item["type"])].render_failure
        lines.extend(renderer(item))
    lines.extend(
        [
            "",
            "Finish by printing a concise summary of the fix.",
            'End with one exact line: RUNNER_RESULT: {"status":"completed","summary":"..."}',
            'If you cannot continue without missing credentials, an ambiguous target, or a policy block, end with: RUNNER_RESULT: {"status":"blocked","blocker_class":"missing_credentials|ambiguous_target|policy_block","summary":"..."}',
        ]
    )
    return "\n".join(lines)


def build_github_followup_prompt(state: dict[str, Any], pr_snapshot: dict[str, Any]) -> str:
    checks = list(pr_snapshot.get("checks", []))
    lines = [
        f"You are addressing GitHub pull-request feedback in working directory: {state['repo']}",
        "",
        f"Pull request: {pr_snapshot.get('url') or pr_snapshot.get('number')}",
        "",
        "Original task:",
        state["task"],
        "",
        "Requirements:",
        "- Read current pull-request comments and review threads through gh only.",
        "- Address actionable review feedback and failing check causes only.",
        "- Keep scope tied to the original task and current review/check feedback.",
        "- Do not push or merge; the external runtime owns publication.",
        "- Re-run local verification after edits when possible.",
        "",
    ]
    unresolved = pr_snapshot.get("unresolved_threads")
    if isinstance(unresolved, int):
        lines.append(f"Current unresolved review threads: {unresolved}")
    if checks:
        lines.append("Current required checks:")
        for check in checks:
            lines.append(f"- {check.get('name')}: bucket={check.get('bucket')} state={check.get('state')}")
    lines.extend(
        [
            "",
            "Finish by printing a concise summary of what feedback you addressed.",
            'End with one exact line: RUNNER_RESULT: {"status":"completed","summary":"..."}',
            'If you cannot continue without missing credentials, an ambiguous target, or a policy block, end with: RUNNER_RESULT: {"status":"blocked","blocker_class":"missing_credentials|ambiguous_target|policy_block","summary":"..."}',
        ]
    )
    return "\n".join(lines)


def parse_runner_result(stdout: str) -> dict[str, Any] | None:
    for raw_line in reversed(stdout.splitlines()):
        line = raw_line.strip()
        if not line.startswith("RUNNER_RESULT:"):
            continue
        payload = line.split("RUNNER_RESULT:", 1)[1].strip()
        if not payload:
            return None
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None
    return None


def provider_env(state: dict[str, Any], state_path: Path) -> dict[str, str]:
    return {
        "AI_AGENT_STATE_FILE": str(state_path),
        "AI_AGENT_RUNTIME_PHASE": str(state.get("phase") or ""),
        "AI_AGENT_DELIVERY_BACKEND": str(state.get("delivery_backend") or ""),
        "AI_AGENT_WORKDIR": str(state.get("repo") or ""),
    }


def provider_timeout_seconds(config: dict[str, Any]) -> float | None:
    raw = config.get("runtime", {}).get("provider_timeout_seconds")
    if raw is None:
        return None
    try:
        timeout = float(raw)
    except (TypeError, ValueError) as exc:
        raise SystemExit("error: runtime.provider_timeout_seconds must be a number or null") from exc
    if timeout <= 0:
        raise SystemExit("error: runtime.provider_timeout_seconds must be greater than zero when set")
    return timeout


def run_provider(
    config: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
    repo: Path,
    prompt: str,
    trace_path: Path | None,
    dry_run: bool,
) -> subprocess.CompletedProcess[str]:
    cmd = build_provider_command(config, state["provider"], repo, prompt, state_path)
    require_tool(cmd[0])
    record_event(state, trace_path, "provider_command", command=cmd)
    timeout_value = provider_timeout_seconds(config)
    try:
        result = run_command(
            cmd,
            repo,
            dry_run=dry_run,
            check=False,
            env_overrides=provider_env(state, state_path),
            timeout_seconds=timeout_value,
        )
    except subprocess.TimeoutExpired as exc:
        state["status"] = "failed"
        state["blocker_class"] = "provider_timeout"
        state["last_error"] = f"provider command timed out after {timeout_value} seconds"
        raise SystemExit(state["last_error"]) from exc
    record_event(
        state,
        trace_path,
        "provider_result",
        returncode=result.returncode,
        stdout=(result.stdout or "").strip()[:4000],
        stderr=(result.stderr or "").strip()[:4000],
    )
    if result.returncode != 0:
        state["status"] = "failed"
        state["blocker_class"] = "provider_error"
        state["last_error"] = (result.stderr or result.stdout or "").strip() or "provider command failed"
        raise SystemExit(f"error: provider command failed for {state['provider']}")
    runner_result = parse_runner_result(result.stdout or "")
    if runner_result:
        record_event(state, trace_path, "provider_runner_result", result=runner_result)
        status = str(runner_result.get("status") or "").lower()
        if status == "blocked":
            blocker_class = str(runner_result.get("blocker_class") or "provider_blocked")
            message = str(runner_result.get("summary") or "provider reported a blocker")
            phase_blocked(state, str(state.get("phase") or "running"), blocker_class, message, trace_path)
        elif status == "failed":
            state["status"] = "failed"
            state["blocker_class"] = str(runner_result.get("blocker_class") or "provider_failed")
            state["last_error"] = str(runner_result.get("summary") or "provider reported failure")
            raise SystemExit(f"error: provider reported failure for {state['provider']}")
    return result


def run_verification_steps(repo: Path, steps: list[dict[str, Any]], dry_run: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for step in steps:
        step_type = str(step["type"])
        results.append(VERIFICATION_REGISTRY[step_type].execute(repo, step, dry_run))
    return results


def verification_failures(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in results if str(item.get("status") or "") != "passed"]


def repo_has_changes(repo: Path) -> bool:
    return bool(git(repo, "status", "--porcelain").stdout.strip())


def branch_ahead_count(repo: Path, base_branch: str) -> int:
    result = git(repo, "rev-list", "--count", f"{base_branch}..HEAD")
    raw = result.stdout.strip() or "0"
    try:
        return int(raw)
    except ValueError as exc:
        raise SystemExit(f"error: could not parse branch-ahead count: {raw}") from exc


def commit_all(repo: Path, message: str, dry_run: bool) -> None:
    # The runtime assumes the automation owns the worktree; callers should
    # keep untracked files out of scope or disable commit/push delivery.
    git(repo, "add", "-A", dry_run=dry_run)
    git(repo, "commit", "-m", message, dry_run=dry_run)


def backend_state(state: dict[str, Any], backend: str | None = None) -> dict[str, Any]:
    name = backend or str(state.get("delivery_backend") or "")
    return state.setdefault("backend_state", {}).setdefault(name, {})


def delivery_artifacts(state: dict[str, Any]) -> dict[str, Any]:
    return state.setdefault("artifacts", {}).setdefault("delivery", {})


def backend_delivery_artifact(state: dict[str, Any], backend: str) -> dict[str, Any]:
    return delivery_artifacts(state).setdefault(backend, {})


def find_open_pr_for_branch(repo: Path, branch: str, dry_run: bool) -> dict[str, Any] | None:
    if dry_run:
        return None
    result = run_command(
        ["gh", "pr", "list", "--state", "open", "--head", branch, "--json", "number,url,headRefName"],
        repo,
        check=True,
    )
    payload = json.loads(result.stdout or "[]")
    if not payload:
        return None
    return payload[0]


def create_pr(repo: Path, state: dict[str, Any], plan: DeliveryPlan, dry_run: bool) -> dict[str, Any]:
    summary = summarize_task(state["task"], limit=60)
    title = f"{plan.pr_title_prefix} {summary}".strip()
    body = (
        "Autonomous runtime generated this pull request.\n\n"
        f"Task: {state['task']}\n\n"
        "The runtime owns branch publication, review synchronization, and merge gating."
    )
    if dry_run:
        return {"number": 1, "url": "https://example.invalid/pr/1"}
    existing = find_open_pr_for_branch(repo, state["head_branch"], dry_run)
    if existing:
        return existing
    run_command(
        [
            "gh",
            "pr",
            "create",
            "--base",
            state["base_branch"],
            "--head",
            state["head_branch"],
            "--title",
            title,
            "--body",
            body,
        ],
        repo,
        check=True,
    )
    refreshed = find_open_pr_for_branch(repo, state["head_branch"], dry_run)
    if refreshed:
        return refreshed
    raise SystemExit(f"error: could not find open PR for branch {state['head_branch']}")


def sync_github_pr_publication(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    plan: DeliveryPlan,
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    backend = backend_state(state, plan.backend)
    artifact = backend_delivery_artifact(state, plan.backend)
    existing_pr = dict(artifact.get("pull_request") or {})
    if not existing_pr:
        maybe_existing = find_open_pr_for_branch(repo, state["head_branch"], dry_run)
        if maybe_existing:
            existing_pr = maybe_existing
    pr_info = existing_pr or create_pr(repo, state, plan, dry_run)
    artifact["pull_request"] = pr_info
    backend["pr_ref"] = str(pr_info.get("number") or pr_info.get("url") or "")
    backend.setdefault("followup_retries", 0)
    backend.setdefault("pending_polls", 0)
    record_event(state, trace_path, "delivery_ready", backend=plan.backend, artifact=pr_info)
    if plan.followup_adapter and (plan.allow_followup_fixes or plan.allow_completion):
        state["phase"] = "followup"
        return
    phase_complete(state, f"pull request {pr_info.get('url') or pr_info.get('number')} opened", trace_path)


def unresolved_threads(repo: Path, number: int, dry_run: bool) -> int:
    if dry_run:
        return 0
    repo_view = run_command(["gh", "repo", "view", "--json", "nameWithOwner"], repo, check=True)
    payload = json.loads(repo_view.stdout)
    owner, name = str(payload["nameWithOwner"]).split("/", 1)
    query = """
query($owner:String!, $name:String!, $number:Int!, $after:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$after) {
        pageInfo { hasNextPage endCursor }
        nodes { isResolved isOutdated }
      }
    }
  }
}
"""
    after = ""
    unresolved = 0
    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
            "-F",
            f"number={number}",
            "-f",
            f"query={query}",
        ]
        if after:
            cmd.extend(["-f", f"after={after}"])
        result = run_command(cmd, repo, check=False)
        if result.returncode != 0:
            return -1
        data = json.loads(result.stdout)
        threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]
        unresolved += sum(1 for node in threads["nodes"] if not node.get("isResolved") and not node.get("isOutdated"))
        page = threads["pageInfo"]
        if not page.get("hasNextPage"):
            return unresolved
        after = str(page.get("endCursor") or "")
        if not after:
            return -1


def inspect_pr(repo: Path, config: dict[str, Any], pr_ref: str, dry_run: bool) -> dict[str, Any]:
    policy = review_policy_for(config, "github_pr")
    if dry_run:
        return {
            "number": 1,
            "url": "https://example.invalid/pr/1",
            "state": "OPEN",
            "closed": False,
            "mergedAt": None,
            "isDraft": False,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
            "headRefOid": "deadbeef",
            "reviewDecision": "APPROVED",
            "unresolved_threads": 0,
            "checks": [],
            "min_required_checks": int(policy.get("min_required_checks", 0)),
        }
    view = run_command(
        [
            "gh",
            "pr",
            "view",
            pr_ref,
            "--json",
            "number,title,url,state,closed,mergedAt,isDraft,mergeable,mergeStateStatus,reviewDecision,headRefOid,comments,reviews",
        ],
        repo,
        check=True,
    )
    data = json.loads(view.stdout)
    checks_cmd = ["gh", "pr", "checks", pr_ref, "--json", "name,bucket,state,workflow"]
    if bool(policy.get("required_checks_only", True)):
        checks_cmd.append("--required")
    checks = run_command(checks_cmd, repo, check=False)
    if checks.returncode not in {0, 8}:
        raise SystemExit("error: could not inspect PR checks")
    data["checks"] = json.loads(checks.stdout or "[]")
    data["min_required_checks"] = int(policy.get("min_required_checks", 0))
    data["unresolved_threads"] = unresolved_threads(repo, int(data["number"]), dry_run)
    return data


def checks_summary(snapshot: dict[str, Any]) -> tuple[str, list[str]]:
    checks = list(snapshot.get("checks", []))
    min_required = int(snapshot.get("min_required_checks", 0) or 0)
    if not checks:
        if min_required > 0:
            return "fail", [f"expected at least {min_required} required check(s), found 0"]
        return "pass", []
    if min_required > 0 and len(checks) < min_required:
        return "fail", [f"expected at least {min_required} required check(s), found {len(checks)}"]
    pending = [item["name"] for item in checks if item.get("bucket") in PENDING_CHECK_BUCKETS]
    failed = [item["name"] for item in checks if item.get("bucket") in FAILED_CHECK_BUCKETS]
    if failed:
        return "fail", failed
    if pending:
        return "pending", pending
    return "pass", []


def merge_blockers(snapshot: dict[str, Any], config: dict[str, Any]) -> list[str]:
    policy = review_policy_for(config, "github_pr")
    blockers: list[str] = []
    if snapshot.get("isDraft"):
        blockers.append("pull request is still a draft")
    mergeable = str(snapshot.get("mergeable", "")).upper()
    if mergeable in {"CONFLICTING", "UNKNOWN"}:
        blockers.append(f"mergeable state is {mergeable}")
    review_decision = str(snapshot.get("reviewDecision") or "").upper()
    if review_decision == "CHANGES_REQUESTED":
        blockers.append("review decision requests changes")
    elif review_decision == "REVIEW_REQUIRED":
        blockers.append("review decision still requires approval")
    merge_state = str(snapshot.get("mergeStateStatus", "")).upper()
    if merge_state in {"BLOCKED", "BEHIND", "DIRTY", "DRAFT", "UNKNOWN"}:
        blockers.append(f"merge state status is {merge_state}")
    check_state, details = checks_summary(snapshot)
    if check_state == "fail":
        blockers.append("required checks failed: " + ", ".join(details))
    elif check_state == "pending":
        blockers.append("required checks are pending: " + ", ".join(details))
    unresolved = snapshot.get("unresolved_threads")
    if bool(policy.get("require_zero_unresolved_threads", True)):
        if unresolved == -1:
            blockers.append("could not inspect unresolved review threads")
        elif int(unresolved or 0) > 0:
            blockers.append(f"{unresolved} unresolved review thread(s) remain")
    return blockers


def actionable_review_feedback(snapshot: dict[str, Any]) -> bool:
    unresolved = snapshot.get("unresolved_threads")
    if isinstance(unresolved, int) and unresolved > 0:
        return True
    review_decision = str(snapshot.get("reviewDecision") or "").upper()
    if review_decision == "CHANGES_REQUESTED":
        return True
    check_state, _details = checks_summary(snapshot)
    return check_state == "fail"


def merge_pr(repo: Path, plan: DeliveryPlan, snapshot: dict[str, Any], pr_ref: str, dry_run: bool) -> None:
    method = plan.completion_method.lower()
    method_flag = {"merge": "--merge", "rebase": "--rebase"}.get(method, "--squash")
    cmd = [
        "gh",
        "pr",
        "merge",
        pr_ref,
        method_flag,
        "--auto",
        "--match-head-commit",
        str(snapshot["headRefOid"]),
    ]
    run_command(cmd, repo, dry_run=dry_run, check=True)


def pr_merged(snapshot: dict[str, Any]) -> bool:
    if snapshot.get("mergedAt"):
        return True
    return str(snapshot.get("state") or "").upper() == "MERGED"


def phase_complete(state: dict[str, Any], message: str, trace_path: Path | None) -> None:
    state["status"] = "completed"
    state["phase"] = "completed"
    state["result"] = message
    record_event(state, trace_path, "completed", message=message)


def phase_blocked(state: dict[str, Any], phase: str, blocker_class: str, message: str, trace_path: Path | None) -> None:
    state["status"] = "blocked"
    state["phase"] = phase
    state["blocker_class"] = blocker_class
    state["last_error"] = message
    record_event(state, trace_path, "blocked", blocker_class=blocker_class, message=message)


def prepare_branch_delivery(
    repo: Path,
    state: dict[str, Any],
    commit_prefix: str,
    trace_path: Path | None,
    dry_run: bool,
) -> bool:
    has_changes = repo_has_changes(repo)
    ahead_count = 1 if dry_run else branch_ahead_count(repo, state["base_branch"])
    if not has_changes and ahead_count == 0 and not dry_run:
        phase_blocked(state, "sync", "no_changes", "provider run produced no repository changes to deliver", trace_path)
        return False
    message = f"{commit_prefix} {summarize_task(state['task'], 60)}"
    if has_changes or dry_run:
        commit_all(repo, message, dry_run)
    return True


def work_phase(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    prompt = build_work_prompt(state, config)
    run_provider(config, state, state_path, repo, prompt, trace_path, dry_run)
    if state.get("status") != "running":
        return
    state["phase"] = "verify"


def verify_phase(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    steps = list(config["verification"].get("steps", []))
    plan = resolve_delivery_plan(config)
    next_phase = "sync" if plan.requires_sync else "completed"
    if not steps:
        if next_phase == "completed":
            phase_complete(state, "task work completed; no verification steps configured", trace_path)
        else:
            state["phase"] = next_phase
        return

    results = run_verification_steps(repo, steps, dry_run)
    state["last_verification"] = results
    record_event(state, trace_path, "verification_results", results=results)
    failures = verification_failures(results)
    if not failures:
        if next_phase == "completed":
            phase_complete(state, "task work and verification completed", trace_path)
        else:
            state["phase"] = next_phase
        return

    counters = state.setdefault("counters", {})
    counters["verification_retries"] = int(counters.get("verification_retries", 0)) + 1
    max_retries = int(config["runtime"].get("max_verification_retries", 2))
    if counters["verification_retries"] > max_retries:
        phase_blocked(state, "verify", "validation_failure", "verification failed after the configured retry budget", trace_path)
        return

    prompt = build_verification_fix_prompt(state, failures)
    run_provider(config, state, state_path, repo, prompt, trace_path, dry_run)


def followup_github_pr_backend(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    plan = resolve_delivery_plan(config)
    backend = backend_state(state, "github_pr")
    artifact = backend_delivery_artifact(state, "github_pr")
    pr_data = dict(artifact.get("pull_request") or {})
    pr_ref = str(backend.get("pr_ref") or pr_data.get("number") or pr_data.get("url") or "")
    if not pr_ref:
        phase_blocked(state, "followup", "missing_pr", "GitHub followup requested without an open pull request", trace_path)
        return

    snapshot = inspect_pr(repo, config, pr_ref, dry_run)
    backend["pr_ref"] = str(snapshot.get("number") or snapshot.get("url") or pr_ref)
    backend["head_ref_oid"] = str(snapshot.get("headRefOid") or "")
    backend["last_checks"] = list(snapshot.get("checks", []))
    artifact["pull_request"] = {"number": snapshot.get("number"), "url": snapshot.get("url")}
    record_event(state, trace_path, "pr_snapshot", snapshot=snapshot)

    if pr_merged(snapshot):
        phase_complete(state, f"pull request {pr_ref} is merged", trace_path)
        return
    policy = review_policy_for(config, "github_pr")
    if snapshot.get("unresolved_threads") == -1 and bool(policy.get("require_zero_unresolved_threads", True)):
        phase_blocked(state, "followup", "review_truth_unavailable", "could not inspect unresolved review threads", trace_path)
        return

    blockers = merge_blockers(snapshot, config)
    if not blockers:
        if plan.allow_completion:
            if not bool(backend.get("completion_requested", False)):
                merge_pr(repo, plan, snapshot, pr_ref, dry_run)
                backend["completion_requested"] = True
                record_event(state, trace_path, "completion_requested", pr=pr_ref)
                snapshot = inspect_pr(repo, config, pr_ref, dry_run)
                backend["head_ref_oid"] = str(snapshot.get("headRefOid") or "")
                backend["last_checks"] = list(snapshot.get("checks", []))
                record_event(state, trace_path, "pr_snapshot_after_completion_request", snapshot=snapshot)
                if pr_merged(snapshot):
                    phase_complete(state, f"pull request {pr_ref} is merged", trace_path)
                    return
            backend["pending_polls"] = int(backend.get("pending_polls", 0)) + 1
            if backend["pending_polls"] <= int(config["runtime"].get("max_pending_polls", 15)):
                interval = int(config["runtime"].get("poll_interval_seconds", 20))
                if not dry_run and interval > 0:
                    time.sleep(interval)
                return
            phase_blocked(state, "followup", "merge_pending", "auto-merge was requested but the pull request is not merged yet", trace_path)
        else:
            phase_complete(state, f"pull request {pr_ref} is ready; completion disabled by policy", trace_path)
        return

    check_state, _details = checks_summary(snapshot)
    if check_state == "pending":
        backend["pending_polls"] = int(backend.get("pending_polls", 0)) + 1
        if backend["pending_polls"] <= int(config["runtime"].get("max_pending_polls", 15)):
            interval = int(config["runtime"].get("poll_interval_seconds", 20))
            record_event(state, trace_path, "pending_checks_wait", seconds=interval, blockers=blockers)
            if not dry_run and interval > 0:
                time.sleep(interval)
            return
        phase_blocked(state, "followup", "pending_checks", "; ".join(blockers), trace_path)
        return

    if not plan.allow_followup_fixes:
        phase_blocked(state, "followup", "review_fix_disabled", "; ".join(blockers), trace_path)
        return
    if not actionable_review_feedback(snapshot):
        phase_blocked(state, "followup", "non_actionable_merge_blocker", "; ".join(blockers), trace_path)
        return

    backend["followup_retries"] = int(backend.get("followup_retries", 0)) + 1
    if backend["followup_retries"] > int(config["runtime"].get("max_followup_retries", 2)):
        phase_blocked(state, "followup", "review_fix_exhausted", "; ".join(blockers), trace_path)
        return

    prompt = build_github_followup_prompt(state, snapshot)
    run_provider(config, state, state_path, repo, prompt, trace_path, dry_run)
    if state.get("status") != "running":
        return
    verification_results = run_verification_steps(repo, list(config["verification"].get("steps", [])), dry_run)
    state["last_verification"] = verification_results
    failures = verification_failures(verification_results)
    record_event(state, trace_path, "followup_verification", results=verification_results)
    if failures:
        phase_blocked(state, "followup", "validation_failure", "followup changes did not pass local verification", trace_path)
        return
    if repo_has_changes(repo) or dry_run:
        commit_prefix = plan.commit_message_prefix
        commit_all(repo, f"{commit_prefix} {summarize_task(state['task'], 48)}", dry_run)
        git(repo, "push", "-u", "origin", state["head_branch"], dry_run=dry_run)
    backend["pending_polls"] = 0


FOLLOWUP_HANDLERS: dict[str, Callable[[Path, dict[str, Any], dict[str, Any], Path, Path | None, bool], None]] = {
    "github_pr": followup_github_pr_backend,
}

SYNC_PUBLICATION_HANDLERS: dict[str, Callable[[Path, dict[str, Any], dict[str, Any], DeliveryPlan, Path | None, bool], None]] = {
    "github_pr": sync_github_pr_publication,
}


def sync_phase(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    plan = resolve_delivery_plan(config)
    if not plan.requires_sync:
        phase_complete(state, "task work completed in the working directory", trace_path)
        return

    if not prepare_branch_delivery(repo, state, plan.commit_message_prefix, trace_path, dry_run):
        return

    pushed = False
    if plan.push_branch:
        git(repo, "push", "-u", "origin", state["head_branch"], dry_run=dry_run)
        pushed = True
    artifact = backend_delivery_artifact(state, plan.backend)
    artifact["name"] = state["head_branch"]
    artifact["pushed"] = pushed

    if not plan.open_pull_request:
        if pushed:
            phase_complete(state, f"branch {state['head_branch']} delivered and pushed", trace_path)
        else:
            phase_complete(state, f"branch {state['head_branch']} delivered locally", trace_path)
        return

    handler = SYNC_PUBLICATION_HANDLERS.get(plan.publication_adapter or "")
    if handler is None:
        phase_blocked(state, "sync", "delivery_adapter_missing", f"no sync publication adapter is registered for backend {plan.backend}", trace_path)
        return
    handler(repo, config, state, plan, trace_path, dry_run)


def followup_phase(
    repo: Path,
    config: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
    trace_path: Path | None,
    dry_run: bool,
) -> None:
    plan = resolve_delivery_plan(config)
    handler = FOLLOWUP_HANDLERS.get(plan.followup_adapter or "")
    if handler is None:
        phase_complete(state, f"delivery backend {plan.backend} has no followup loop", trace_path)
        return
    handler(repo, config, state, state_path, trace_path, dry_run)


def run_workflow(args: argparse.Namespace) -> int:
    repo = expand_path(args.repo)
    config_path = expand_path(args.config)
    config = load_config(config_path, args.provider, args.allow_completion, args.no_completion)
    plan = resolve_delivery_plan(config)
    state_path = state_file_for(config, args.state_file)
    trace_path = expand_path(args.trace_json) if args.trace_json else None
    task = read_task(args)
    ensure_task(task, state_path)

    for tool in plan.required_tools:
        require_tool(tool)

    state = load_or_init_state(state_path, repo, task, config)
    validate_resume_identity(state, repo, task, config, args.force_resume)
    if state.get("status") == "blocked":
        state["status"] = "running"
        state.pop("blocker_class", None)
        state.pop("last_error", None)

    if state.get("status") in TERMINAL_STATES:
        save_state(state_path, state)
        print(json.dumps({"status": state["status"], "phase": state["phase"], "state_file": str(state_path)}, ensure_ascii=False))
        return 0 if state["status"] == "completed" else 1

    state["provider"] = config["provider"]
    state["repo"] = str(repo)
    state["base_branch"] = config["base_branch"]
    state["delivery_backend"] = plan.backend
    save_state(state_path, state)

    if plan.needs_git:
        ensure_clean(repo, args.allow_dirty)
    record_event(
        state,
        trace_path,
        "run_start",
        state_file=str(state_path),
        config=str(config_path),
        dry_run=args.dry_run,
        delivery_backend=plan.backend,
    )

    try:
        while state.get("status") not in TERMINAL_STATES:
            phase = state.get("phase")
            save_state(state_path, state)
            if plan.needs_branch and phase in {"work", "verify", "sync", "followup"}:
                ensure_work_branch(repo, state, args.dry_run)
            if phase == "work":
                work_phase(repo, config, state, state_path, trace_path, args.dry_run)
            elif phase == "verify":
                verify_phase(repo, config, state, state_path, trace_path, args.dry_run)
            elif phase == "sync":
                sync_phase(repo, config, state, trace_path, args.dry_run)
            elif phase == "followup":
                followup_phase(repo, config, state, state_path, trace_path, args.dry_run)
            elif phase == "completed":
                state["status"] = "completed"
            else:
                state["status"] = "failed"
                state["blocker_class"] = "unknown_phase"
                state["last_error"] = f"unknown phase: {phase}"
                break
            if state.get("status") == "blocked":
                break
    except SystemExit as exc:
        if state.get("status") not in TERMINAL_STATES and state.get("status") != "blocked":
            state["status"] = "failed"
            state["blocker_class"] = state.get("blocker_class") or "runtime_error"
            detail = str(exc) or "workflow aborted"
            state["last_error"] = state.get("last_error") or detail
            # Persist terminal state before re-raising so an interrupted run can resume cleanly.
            record_event(state, trace_path, "failed", blocker_class=state["blocker_class"], message=state["last_error"])
        save_state(state_path, state)
        raise

    if state.get("status") == "blocked":
        save_state(state_path, state)
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "phase": state.get("phase"),
                    "blocker_class": state.get("blocker_class"),
                    "message": state.get("last_error"),
                    "delivery_backend": state.get("delivery_backend"),
                    "state_file": str(state_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    if state.get("status") != "completed":
        state["status"] = "failed"
        save_state(state_path, state)
        print(
            json.dumps(
                {
                    "status": "failed",
                    "phase": state.get("phase"),
                    "message": state.get("last_error") or "workflow failed",
                    "delivery_backend": state.get("delivery_backend"),
                    "state_file": str(state_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    save_state(state_path, state)
    print(
        json.dumps(
            {
                "status": "completed",
                "phase": state.get("phase"),
                "result": state.get("result"),
                "delivery_backend": state.get("delivery_backend"),
                "artifacts": state.get("artifacts"),
                "state_file": str(state_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "run":
        return run_workflow(args)
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
