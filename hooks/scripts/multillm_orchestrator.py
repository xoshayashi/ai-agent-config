#!/usr/bin/env python3
"""Codex-centered multi-LLM orchestration hook.

This hook keeps Codex as the execution hub while using:
- Claude for spec review/finalization and implementation guidance
- Gemini for periodic implementation critique

Design goals:
- Fail-open by default (never brick the session if a peer CLI is unavailable)
- Explicit recursion guards
- Deterministic, session-scoped state on local disk
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SUPPORTED_EVENTS: dict[str, set[str]] = {
    "codex": {"SessionStart", "UserPromptSubmit", "Stop"},
}

DEFAULT_SPEC_DONE_KEYWORD = "[[SPEC_DONE]]"
DEFAULT_IMPLEMENTATION_DONE_KEYWORD = "[[IMPLEMENTATION_DONE]]"
DEFAULT_VERIFICATION_DONE_KEYWORD = "[[VERIFICATION_DONE]]"
DEFAULT_TASK_DONE_KEYWORD = "[[TASK_DONE]]"
FOLLOWUP_PROMPT_PATTERN = re.compile(
    r"^\s*(continue|go on|keep going|proceed|next|ok|yes|please continue|implement|apply|fix it|"
    r"続けて(?:ください)?|続行(?:してください)?|進めて(?:ください)?|次(?:へ)?|そのまま|"
    r"お願いします|お願い|じゃあ|では|この仕様で実装して|これで進めて|それで進めて)"
    r"(?:\b|[、。,.\s])",
    re.IGNORECASE,
)
TRIVIAL_PROMPT_PATTERN = re.compile(
    r"^\s*(ありがとう|thanks|thank you|ok|了解|はい|いいえ|stop|pause|status|進捗|止めて)[。.!?\s]*$",
    re.IGNORECASE,
)
ORCHESTRATION_EXPLICIT_TRIGGER_PATTERN = re.compile(
    r"(orchestrat|spec|design doc|architecture|review|verification|pull request|\bpr\b|"
    r"仕様|設計|設計書|アーキテクチャ|実装計画|検証|レビュー|調査|分析|ブランチ|フック|"
    r"hook|skill|agent|automation|自動化|リファクタ|テスト|不具合|バグ)",
    re.IGNORECASE,
)
ORCHESTRATION_ACTION_PATTERN = re.compile(
    r"(implement|build|fix|refactor|analy[sz]e|research|review|debug|write|create|update|"
    r"作成|修正|実装|調査|分析|確認|検証|改善|更新|整理)",
    re.IGNORECASE,
)
COMPLEXITY_SIGNAL_PATTERN = re.compile(
    r"(architecture|orchestrat|migration|trade[- ]?off|risk|security|performance|complex|ambiguous|"
    r"設計|仕様|移行|互換|安全|性能|複雑|曖昧|リスク)",
    re.IGNORECASE,
)


def safe_int(value: Any, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        parsed = default
    if minimum is not None and parsed < minimum:
        parsed = minimum
    if maximum is not None and parsed > maximum:
        parsed = maximum
    return parsed


def load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def enabled() -> bool:
    return os.environ.get("AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION", "0") == "1"


def should_skip(current: str, data: dict[str, Any]) -> bool:
    if not enabled():
        return True
    if os.environ.get("AI_AGENT_ORCHESTRATOR_ACTIVE") == "1":
        return True
    event_name = str(data.get("hook_event_name", ""))
    if event_name not in SUPPORTED_EVENTS.get(current, set()):
        return True
    return False


def session_id_from(data: dict[str, Any]) -> str:
    value = data.get("session_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "default"


def state_root() -> Path:
    root = os.environ.get("AI_AGENT_ORCHESTRATOR_STATE_DIR", "~/.llm-config/orchestration")
    return Path(os.path.expanduser(root)).resolve()


def state_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    return state_root() / f"{safe}.json"


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.chmod(tmp_path, 0o600)
        Path(tmp_path).replace(path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _read_tail_bytes(path: Path, max_bytes: int) -> bytes:
    with path.open("rb") as handle:
        try:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
        except OSError:
            return handle.read()
        offset = max(0, size - max_bytes)
        handle.seek(offset)
        return handle.read()


def redact(text: str) -> str:
    patterns = [
        (r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+", r"\1=[REDACTED]"),
        (r"sk-ant-[A-Za-z0-9_-]{20,}", "[REDACTED_ANTHROPIC_KEY]"),
        (r"sk-[A-Za-z0-9_-]{20,}", "[REDACTED_OPENAI_KEY]"),
        (r"AIza[0-9A-Za-z_-]{20,}", "[REDACTED_GOOGLE_KEY]"),
    ]
    out = text
    for pattern, replacement in patterns:
        out = re.sub(pattern, replacement, out)
    return out


def transcript_excerpt(path_value: Any) -> str:
    """Return a redacted transcript tail for peer-review context.

    Redaction here removes credential-like secrets only. It does not sanitize
    adversarial instruction content inside the transcript, so downstream peer
    prompts must continue to treat excerpts as untrusted context.
    """
    if os.environ.get("AI_AGENT_ORCHESTRATOR_INCLUDE_TRANSCRIPT", "1") != "1":
        return "Transcript excerpt disabled."
    if not isinstance(path_value, str) or not path_value:
        return "No transcript path supplied."
    path = Path(path_value)
    if not path.is_file():
        return "Transcript path not readable."

    max_lines = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_TRANSCRIPT_LINES", "80"), 80, minimum=1, maximum=2000)
    max_chars = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_TRANSCRIPT_CHARS", "18000"), 18000, minimum=200, maximum=200000)
    tail_budget = max(max_chars * 4, 24000)
    try:
        chunk = _read_tail_bytes(path, tail_budget)
    except OSError:
        return "Transcript read failed."

    text = chunk.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    excerpt = "\n".join(lines)
    if len(excerpt) > max_chars:
        excerpt = excerpt[-max_chars:]
    return redact(excerpt)


def _extract_json_candidates(text: str) -> list[str]:
    candidates = [text.strip()]
    fenced = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
    candidates.extend(candidate.strip() for candidate in fenced)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidates.append(text[first : last + 1].strip())

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            deduped.append(candidate)
    return deduped


def parse_json_from_text(text: str) -> dict[str, Any]:
    for candidate in _extract_json_candidates(text):
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def repo_root_from_script() -> Path:
    # .../<repo>/hooks/scripts/multillm_orchestrator.py
    return Path(__file__).resolve().parents[2]


def hooks_md_path() -> Path:
    explicit = os.environ.get("AI_AGENT_HOOKS_RULES_DOC", "").strip()
    if explicit:
        return Path(os.path.expanduser(explicit)).resolve()
    return repo_root_from_script() / "instructions" / "HOOKS.md"


def completion_keywords() -> tuple[str, str, str, str]:
    path = hooks_md_path()
    if not path.is_file():
        return (
            DEFAULT_SPEC_DONE_KEYWORD,
            DEFAULT_IMPLEMENTATION_DONE_KEYWORD,
            DEFAULT_VERIFICATION_DONE_KEYWORD,
            DEFAULT_TASK_DONE_KEYWORD,
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return (
            DEFAULT_SPEC_DONE_KEYWORD,
            DEFAULT_IMPLEMENTATION_DONE_KEYWORD,
            DEFAULT_VERIFICATION_DONE_KEYWORD,
            DEFAULT_TASK_DONE_KEYWORD,
        )
    tokens = sorted(set(re.findall(r"\[\[[A-Z0-9_:-]+\]\]", text)))
    spec_done = DEFAULT_SPEC_DONE_KEYWORD
    implementation_done = DEFAULT_IMPLEMENTATION_DONE_KEYWORD
    verification_done = DEFAULT_VERIFICATION_DONE_KEYWORD
    task_done = DEFAULT_TASK_DONE_KEYWORD

    for token in tokens:
        if "SPEC_DONE" in token:
            spec_done = token
            break

    for token in tokens:
        if "IMPLEMENTATION_DONE" in token:
            implementation_done = token
        elif "VERIFICATION_DONE" in token:
            verification_done = token
        elif "TASK_DONE" in token:
            task_done = token
    return spec_done, implementation_done, verification_done, task_done


def contains_explicit_keyword(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    pattern = re.compile(
        rf"(?m)^\s*(?:[-*+]\s+|[0-9]+[.)]\s+)?{re.escape(keyword)}\s*$"
    )
    return pattern.search(text) is not None


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def peer_env() -> dict[str, str]:
    env = os.environ.copy()
    env["AI_AGENT_ORCHESTRATOR_ACTIVE"] = "1"
    env["AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION"] = "0"
    env["AI_AGENT_HOOKS_ENABLE_PROMPT_REFINEMENT"] = "0"
    env["AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY"] = "0"
    env["AI_AGENT_PROMPT_REFINEMENT_ACTIVE"] = "1"
    env["AI_AGENT_RESPONSE_STRATEGY_ACTIVE"] = "1"
    return env


def run_cli(command: list[str]) -> str:
    timeout = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_TIMEOUT_SECONDS", "45"), 45, minimum=3, maximum=60)
    output_limit = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_OUTPUT_CHARS", "20000"), 20000, minimum=1000, maximum=200000)
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=peer_env(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    output = completed.stdout.strip()
    if not output:
        return ""
    return output[:output_limit]


def claude_effort_level(kind: str, *signals: str) -> str:
    simple = os.environ.get("AI_AGENT_ORCHESTRATOR_CLAUDE_SIMPLE_EFFORT", "low").strip().lower() or "low"
    complex_level = os.environ.get("AI_AGENT_ORCHESTRATOR_CLAUDE_COMPLEX_EFFORT", "high").strip().lower() or "high"
    allowed = {"low", "medium", "high", "xhigh", "max"}
    if simple not in allowed:
        simple = "low"
    if complex_level not in allowed:
        complex_level = "high"

    text = "\n".join(signal for signal in signals if signal).strip()
    if kind == "spec_review":
        if len(text) >= 4000 or COMPLEXITY_SIGNAL_PATTERN.search(text):
            return complex_level
        return simple
    if kind == "implementation_guidance":
        if len(text) >= 6000 or COMPLEXITY_SIGNAL_PATTERN.search(text):
            return complex_level
        return simple
    return simple


def call_claude(packet: str, kind: str = "simple", *signals: str) -> str:
    if not command_available("claude"):
        return ""
    effort = claude_effort_level(kind, packet, *signals)
    command = [
        "claude",
        "-p",
        packet,
        "--output-format",
        "text",
        "--permission-mode",
        "plan",
        "--effort",
        effort,
        "--max-turns",
        "1",
    ]
    return run_cli(command)


def call_gemini(packet: str) -> str:
    if not command_available("gemini"):
        return ""
    command = [
        "gemini",
        "--skip-trust",
        "--approval-mode",
        "plan",
        "--output-format",
        "text",
        "-p",
        packet,
    ]
    return run_cli(command)


def prompt_from(data: dict[str, Any]) -> str:
    value = data.get("prompt")
    return value if isinstance(value, str) else ""


def response_from(data: dict[str, Any]) -> str:
    for key in ("prompt_response", "last_assistant_message", "response"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def should_keep_current_task(prompt: str) -> bool:
    stripped = prompt.strip()
    if not stripped:
        return True
    if FOLLOWUP_PROMPT_PATTERN.search(stripped):
        return True
    return False


def should_activate_orchestration(prompt: str) -> bool:
    stripped = prompt.strip()
    if not stripped:
        return False
    if TRIVIAL_PROMPT_PATTERN.search(stripped):
        # Keep lightweight acknowledgements as plain user turns even when a task
        # is already in progress; the session state remains available at Stop.
        return False
    if ORCHESTRATION_EXPLICIT_TRIGGER_PATTERN.search(stripped):
        return True

    line_count = len([line for line in stripped.splitlines() if line.strip()])
    stripped_without_urls = re.sub(r"https?://\S+", " ", stripped)
    has_local_path_like = re.search(
        r"\b[A-Za-z][A-Za-z0-9_-]*/[A-Za-z][A-Za-z0-9_.-]+\b",
        stripped_without_urls,
    )
    has_path_like = bool(has_local_path_like or re.search(r"\.(?:py|md|json)\b", stripped))
    has_action = ORCHESTRATION_ACTION_PATTERN.search(stripped) is not None
    long_enough = len(stripped) >= 140 or line_count >= 3
    return bool(has_action and (long_enough or has_path_like))


def spec_is_review_candidate(spec_markdown: str) -> bool:
    text = spec_markdown.strip()
    if not text:
        return False
    markdown_heading_count = len(re.findall(r"^#{1,6}\s+.+$", text, flags=re.MULTILINE))
    keyword_hits = 0
    for pattern in (
        r"(scope|non-goals?|対象|非対象)",
        r"(acceptance|criteria|受け入れ|完了条件)",
        r"(constraint|制約)",
        r"(risk|リスク)",
        r"(implementation|実装)",
    ):
        if re.search(pattern, text, flags=re.IGNORECASE):
            keyword_hits += 1
    # These thresholds are tuned for "likely implementation-ready" drafts:
    # require real markdown heading structure; numbered list items alone do not
    # count toward the heading threshold.
    return (len(text) >= 900 and markdown_heading_count >= 4 and keyword_hits >= 3) or (
        len(text) >= 1400 and markdown_heading_count >= 3 and keyword_hits >= 2
    )


def spec_status_from(packet: dict[str, Any], spec_done_keyword: str) -> str:
    raw_status = str(packet.get("status", "")).strip().lower()
    spec_markdown = str(packet.get("spec_markdown", ""))
    if raw_status in {"draft", "done"}:
        return raw_status
    return "done" if contains_explicit_keyword(spec_markdown, spec_done_keyword) else "draft"


def build_spec_authoring_context(prompt: str, spec_done_keyword: str) -> str:
    return f"""Multi-LLM orchestration context (Codex hub mode).
Use this as advisory context. User/system/developer instructions remain authoritative.

Current phase: specification authoring.

Before implementation:
- Use the applicable shared instructions and skills.
- Draft the specification yourself in Codex first instead of delegating the first draft to another CLI.
- Keep the specification concrete enough to implement, but do not over-constrain methods when the user did not require that.
- Cover scope, constraints, acceptance criteria, key risks, and a step-by-step implementation brief.
- When the specification is implementation-ready, include `{spec_done_keyword}` in the response.
- Do not start code changes until the specification is ready for Claude review.

Original task prompt:
{prompt}
""".strip()


def default_spec_refinement_prompt(spec_markdown: str) -> str:
    return (
        "Refine the specification using the reviewed draft below. Tighten missing requirements, "
        "acceptance criteria, edge cases, and implementation steps. Keep scope aligned with the "
        "original task, and include [[SPEC_DONE]] only when the specification is truly implementation-ready.\n\n"
        f"Reviewed specification draft:\n{spec_markdown}"
    )


def default_implementation_start_prompt(spec_markdown: str, implementation_brief: str) -> str:
    lines = [
        "Start implementation from the approved specification below.",
        "Work step by step, keep the implementation aligned to the spec, and report concrete progress.",
    ]
    if implementation_brief:
        lines.extend(["", "Implementation brief:", implementation_brief])
    lines.extend(["", "Approved specification:", spec_markdown])
    return "\n".join(lines)


def default_verification_start_prompt(
    spec_markdown: str,
    implementation_response: str,
    verification_done_keyword: str,
    task_done_keyword: str,
) -> str:
    return (
        "Implementation appears complete enough to begin verification.\n"
        "Do not stop yet. Run the most relevant tests or verification checks, inspect the diff, "
        "and perform a focused self-review against the approved specification.\n"
        f"Use {verification_done_keyword} only when verification and self-review are complete. "
        f"Use {task_done_keyword} only when the task is truly complete end-to-end.\n\n"
        f"Approved specification:\n{spec_markdown}\n\n"
        f"Latest implementation summary:\n{implementation_response}"
    )


def review_spec_with_claude(
    data: dict[str, Any],
    original_prompt: str,
    draft_spec: str,
    spec_done_keyword: str,
) -> dict[str, Any]:
    cwd = str(data.get("cwd", ""))
    model = str(data.get("model", ""))
    excerpt = transcript_excerpt(data.get("transcript_path"))
    hooks_doc = hooks_md_path()

    claude_review_packet = f"""You are reviewing a Codex-authored specification before implementation starts.
Return strict JSON:
{{
  "spec_markdown": "string",
  "status": "draft|done",
  "implementation_brief": "string",
  "next_step_prompt_for_codex": "string"
}}

Requirements:
- Preserve user constraints, intent, and scope.
- Improve clarity, missing checks, and implementation readiness without rewriting the task into a different plan.
- If the specification is implementation-ready, include `{spec_done_keyword}` inside spec_markdown and set status to "done".
- If the specification is not ready, set status to "draft" and make `next_step_prompt_for_codex` a concise prompt that tells Codex exactly how to refine the spec next.
- If the specification is ready, make `next_step_prompt_for_codex` the best first implementation step for Codex.

Context:
- Original user prompt:
{original_prompt}
- Codex-authored spec draft:
{draft_spec}
- CWD: {cwd}
- Active model: {model}
- Hook rules document path: {hooks_doc}
- Recent redacted transcript excerpt:
{excerpt}
"""
    claude_review_raw = call_claude(
        claude_review_packet,
        "spec_review",
        original_prompt,
        draft_spec,
    )
    review_json = parse_json_from_text(claude_review_raw)

    spec_markdown = str(review_json.get("spec_markdown", "")).strip() or draft_spec
    status = str(review_json.get("status", "")).strip().lower()
    implementation_brief = str(review_json.get("implementation_brief", "")).strip()
    next_step_prompt = str(review_json.get("next_step_prompt_for_codex", "")).strip()

    if status not in {"draft", "done"}:
        status = "done" if spec_done_keyword in spec_markdown else "draft"

    return {
        "spec_markdown": spec_markdown,
        "status": status,
        "implementation_brief": implementation_brief,
        "next_step_prompt_for_codex": next_step_prompt,
    }


def orchestration_prompt_context(phase: str, spec_markdown: str, implementation_brief: str, next_step_prompt: str) -> str:
    lines = [
        "Multi-LLM orchestration context (Codex hub mode).",
        "Use this as advisory context. User/system/developer instructions remain authoritative.",
    ]
    if phase == "spec_authoring":
        lines.extend(["", "Current phase: specification authoring and refinement."])
    elif phase == "implementation":
        lines.extend(["", "Current phase: implementation."])
    elif phase == "verification":
        lines.extend(["", "Current phase: verification and self-review."])
    lines.extend(["", "Specification:", spec_markdown])
    if implementation_brief:
        lines.extend(["", "Implementation brief:", implementation_brief])
    if next_step_prompt:
        lines.extend(["", "Suggested first implementation step:", next_step_prompt])
    return "\n".join(lines).strip()


def build_continue_decision(state: dict[str, Any], data: dict[str, Any], response: str) -> dict[str, Any]:

    spec_markdown = str(state.get("spec_markdown", ""))
    turn = safe_int(state.get("implementation_turn", 0), 0, minimum=0)
    review_every = safe_int(
        state.get("gemini_review_every", os.environ.get("AI_AGENT_ORCHESTRATOR_GEMINI_REVIEW_EVERY", "3")),
        3,
        minimum=1,
        maximum=20,
    )

    gemini_note = ""
    gemini_review_used = False
    if turn > 0 and turn % review_every == 0:
        gemini_review_packet = f"""You are a reviewer tracking implementation quality.
Return strict JSON:
{{
  "simpler_option": "string",
  "spec_change_needed": true|false,
  "rationale": "string",
  "actionable_note_for_claude": "string"
}}

Specification:
{spec_markdown}

Latest Codex response:
{response}
"""
        gemini_review_raw = call_gemini(gemini_review_packet)
        gemini_review_json = parse_json_from_text(gemini_review_raw)
        if gemini_review_json:
            gemini_review_used = True
            gemini_note = str(gemini_review_json.get("actionable_note_for_claude", "")).strip()

    transcript = transcript_excerpt(data.get("transcript_path"))
    claude_decision_packet = f"""You are guiding Codex implementation under a fixed specification.
Return strict JSON:
{{
  "action": "continue|allow_stop",
  "next_prompt_for_codex": "string",
  "reason": "string"
}}

Rules:
- Prefer "allow_stop" when progress is sufficient for this turn.
- Use "continue" only when one immediate next step is clearly beneficial.
- Keep next_prompt_for_codex concise, concrete, and scope-safe.

Specification:
{spec_markdown}

Latest Codex response:
{response}

Gemini reviewer note (optional):
{gemini_note or "none"}

Recent redacted transcript excerpt:
{transcript}
"""
    claude_decision_raw = call_claude(
        claude_decision_packet,
        "implementation_guidance",
        spec_markdown,
        response,
        gemini_note,
    )
    decision_json = parse_json_from_text(claude_decision_raw)
    action = str(decision_json.get("action", "")).strip().lower()
    next_prompt = str(decision_json.get("next_prompt_for_codex", "")).strip()
    reason = str(decision_json.get("reason", "")).strip()
    peer_prefix = "Claude implementation guidance received"
    if gemini_review_used:
        peer_prefix += "; Gemini critique also applied"

    should_continue = action == "continue" and bool(next_prompt)
    if not should_continue:
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        note = reason or "No immediate continuation suggested."
        return {"continue": False, "prompt": "", "note": f"{peer_prefix}. {note}"}

    max_continuations = safe_int(
        os.environ.get("AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK", "5"),
        5,
        minimum=1,
        maximum=30,
    )
    continuation_count = safe_int(state.get("continuation_count", 0), 0, minimum=0) + 1
    state["continuation_count"] = continuation_count
    if continuation_count > max_continuations:
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        return {
            "continue": False,
            "prompt": "",
            "note": f"Continuation cap reached ({max_continuations}). Waiting for user direction.",
        }

    normalized_prompt = re.sub(r"\s+", " ", next_prompt).strip().lower()
    previous_prompt = str(state.get("last_continuation_prompt", ""))
    same_prompt_count = safe_int(state.get("same_prompt_count", 0), 0, minimum=0)
    if normalized_prompt and normalized_prompt == previous_prompt:
        same_prompt_count += 1
    else:
        same_prompt_count = 1
    state["last_continuation_prompt"] = normalized_prompt
    state["same_prompt_count"] = same_prompt_count

    max_same_prompt = safe_int(
        os.environ.get("AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT", "2"),
        2,
        minimum=1,
        maximum=10,
    )
    if same_prompt_count > max_same_prompt:
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        return {
            "continue": False,
            "prompt": "",
            "note": "Repeated continuation prompt detected. Stopping auto-loop for safety.",
        }

    note = reason or "Continuing with the next implementation step."
    return {"continue": True, "prompt": next_prompt, "note": f"{peer_prefix}. {note}"}


def build_verification_decision(
    state: dict[str, Any],
    data: dict[str, Any],
    response: str,
    verification_done_keyword: str,
    task_done_keyword: str,
) -> dict[str, Any]:
    verification_turn = safe_int(state.get("verification_turn", 0), 0, minimum=0)
    max_verification_turns = safe_int(
        os.environ.get("AI_AGENT_ORCHESTRATOR_MAX_VERIFICATION_TURNS", "3"),
        3,
        minimum=1,
        maximum=20,
    )
    if verification_turn > max_verification_turns:
        state["verification_turn"] = 0
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        return {
            "continue": False,
            "prompt": "",
            "note": f"Verification turn cap reached ({max_verification_turns}). Waiting for user direction.",
        }

    verification_done = contains_explicit_keyword(response, verification_done_keyword)
    task_done = contains_explicit_keyword(response, task_done_keyword)
    if verification_done and task_done:
        state["phase"] = "done"
        state["verification_turn"] = 0
        return {"continue": False, "prompt": "", "note": "Verification and task completion keywords detected."}

    spec_markdown = str(state.get("spec_markdown", ""))
    transcript = transcript_excerpt(data.get("transcript_path"))
    claude_decision_packet = f"""You are reviewing Codex output during the verification phase.
Return strict JSON:
{{
  "action": "continue|allow_stop",
  "next_prompt_for_codex": "string",
  "reason": "string"
}}

Rules:
- The task is not complete unless both `{verification_done_keyword}` and `{task_done_keyword}` are explicitly present as standalone lines.
- If they are missing, prefer "continue" and tell Codex the smallest next verification or self-review step.
- Keep next_prompt_for_codex concise, concrete, and scope-safe.

Specification:
{spec_markdown}

Latest Codex verification response:
{response}

Recent redacted transcript excerpt:
{transcript}
"""
    claude_decision_raw = call_claude(
        claude_decision_packet,
        "implementation_guidance",
        spec_markdown,
        response,
    )
    decision_json = parse_json_from_text(claude_decision_raw)
    action = str(decision_json.get("action", "")).strip().lower()
    next_prompt = str(decision_json.get("next_prompt_for_codex", "")).strip()
    reason = str(decision_json.get("reason", "")).strip()

    if action == "allow_stop":
        note = reason or "Verification review did not confirm final completion keywords."
        return {
            "continue": False,
            "prompt": "",
            "note": f"Claude verification guidance received. {note}",
        }

    if next_prompt:
        note = reason or "Continue verification and self-review."
        return {
            "continue": True,
            "prompt": next_prompt,
            "note": f"Claude verification guidance received. {note}",
        }

    fallback_prompt = (
        "Continue verification. Run or summarize the most relevant checks, inspect changed files, "
        f"and only emit {verification_done_keyword} plus {task_done_keyword} when the task is truly complete."
    )
    return {
        "continue": True,
        "prompt": fallback_prompt,
        "note": "Claude verification guidance received. Verification is still incomplete.",
    }


def codex_user_prompt_output(context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def codex_stop_output(decision: dict[str, Any]) -> dict[str, Any]:
    if decision.get("continue") and decision.get("prompt"):
        payload: dict[str, Any] = {
            "decision": "block",
            "reason": str(decision.get("prompt", "")).strip(),
        }
        note = str(decision.get("note", "")).strip()
        if note:
            payload["systemMessage"] = f"Auto-continuing via orchestration: {note}"
        return payload
    note = str(decision.get("note", "")).strip()
    if note:
        return {"systemMessage": f"Orchestrator: {note}"}
    return {}


def codex_session_start_output(state: dict[str, Any]) -> dict[str, Any]:
    phase = str(state.get("phase", "idle"))
    if phase in {"implementation", "spec_authoring", "verification"}:
        spec = str(state.get("spec_markdown", ""))
        if spec:
            label = "Current specification"
            if phase == "spec_authoring":
                label = "Current draft specification (needs refinement)"
            elif phase == "verification":
                label = "Current approved specification (verification in progress)"
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "Resuming orchestration context.\n\n" + label + ":\n" + spec[:4000],
                }
            }
    if phase == "done":
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "Previous orchestration session is marked done. Start a new task prompt to create a new spec loop.",
            }
        }
    return {}


def handle_user_prompt_submit(data: dict[str, Any], state: dict[str, Any], path: Path) -> dict[str, Any]:
    prompt = prompt_from(data)
    if not prompt.strip():
        return {}

    phase = str(state.get("phase", ""))
    if phase == "implementation" and state.get("spec_markdown") and should_keep_current_task(prompt):
        context = orchestration_prompt_context(
            "implementation",
            str(state.get("spec_markdown", "")),
            str(state.get("implementation_brief", "")),
            "",
        )
        return codex_user_prompt_output(context)
    if phase == "verification" and state.get("spec_markdown") and should_keep_current_task(prompt):
        context = orchestration_prompt_context(
            "verification",
            str(state.get("spec_markdown", "")),
            str(state.get("implementation_brief", "")),
            "",
        )
        return codex_user_prompt_output(context)
    if phase == "spec_authoring" and state.get("spec_markdown") and should_keep_current_task(prompt):
        context = orchestration_prompt_context(
            "spec_authoring",
            str(state.get("spec_markdown", "")),
            str(state.get("implementation_brief", "")),
            str(state.get("next_step_prompt_for_codex", "")),
        )
        return codex_user_prompt_output(context)

    if not should_activate_orchestration(prompt):
        return {}

    spec_done_keyword, _, _, _ = completion_keywords()
    if phase in {"implementation", "spec_authoring"} and not should_keep_current_task(prompt):
        state.clear()
    state.update(
        {
            "phase": "spec_authoring",
            "original_prompt": prompt,
            "spec_markdown": "",
            "implementation_brief": "",
            "next_step_prompt_for_codex": "",
            "implementation_turn": 0,
            "verification_turn": 0,
            "spec_revision_count": 0,
            "continuation_count": 0,
            "same_prompt_count": 0,
            "last_continuation_prompt": "",
        }
    )
    save_state(path, state)
    return codex_user_prompt_output(build_spec_authoring_context(prompt, spec_done_keyword))


def handle_stop(data: dict[str, Any], state: dict[str, Any], path: Path) -> dict[str, Any]:
    response = response_from(data)
    if not response:
        return {}

    phase = str(state.get("phase", ""))
    spec_done_keyword, implementation_done_keyword, verification_done_keyword, task_done_keyword = completion_keywords()
    if phase == "spec_authoring":
        spec_revision_count = safe_int(state.get("spec_revision_count", 0), 0, minimum=0) + 1
        state["spec_revision_count"] = spec_revision_count
        state["spec_markdown"] = response
        save_state(path, state)
        spec_ready = contains_explicit_keyword(response, spec_done_keyword)
        spec_review_fallback = (
            not spec_ready
            and spec_revision_count >= 2
            and spec_is_review_candidate(response)
        )
        if not spec_ready and not spec_review_fallback:
            return {
                "systemMessage": (
                    f"Orchestrator: specification draft saved. Continue refining and include "
                    f"{spec_done_keyword} when it is ready for Claude review."
                )
            }

        spec_packet = review_spec_with_claude(
            data,
            str(state.get("original_prompt", "")),
            response,
            spec_done_keyword,
        )
        if not str(spec_packet.get("spec_markdown", "")).strip():
            return {"systemMessage": "Orchestrator: specification review returned no usable output."}

        spec_status = spec_status_from(spec_packet, spec_done_keyword)
        next_phase = "implementation" if spec_status == "done" else "spec_authoring"
        state.update(
            {
                "phase": next_phase,
                "spec_markdown": spec_packet["spec_markdown"],
                "implementation_brief": spec_packet.get("implementation_brief", ""),
                "next_step_prompt_for_codex": spec_packet.get("next_step_prompt_for_codex", ""),
                "implementation_turn": 0,
                "verification_turn": 0,
                "continuation_count": 0,
                "same_prompt_count": 0,
                "last_continuation_prompt": "",
            }
        )
        save_state(path, state)
        next_prompt = str(spec_packet.get("next_step_prompt_for_codex", "")).strip()
        if spec_status == "done" and not next_prompt:
            next_prompt = default_implementation_start_prompt(
                str(spec_packet.get("spec_markdown", "")),
                str(spec_packet.get("implementation_brief", "")),
            )
        if spec_status == "draft" and not next_prompt:
            next_prompt = default_spec_refinement_prompt(str(spec_packet.get("spec_markdown", "")))
        if spec_status == "done" and next_prompt:
            return codex_stop_output(
                {
                    "continue": True,
                    "prompt": next_prompt,
                    "note": (
                        "Claude reviewed the specification and approved implementation."
                        if spec_ready
                        else "Claude reviewed a structured spec draft via fallback and approved implementation."
                    ),
                }
            )
        if spec_status == "draft" and next_prompt:
            return codex_stop_output(
                {
                    "continue": True,
                    "prompt": next_prompt,
                    "note": (
                        "Claude requested one more specification refinement pass."
                        if spec_ready
                        else "Claude reviewed a structured spec draft via fallback and requested one more refinement pass."
                    ),
                }
            )
        note = "specification approved" if spec_status == "done" else "specification still needs refinement"
        return {"systemMessage": f"Orchestrator: Claude review complete; {note}."}

    if phase == "verification":
        state["verification_turn"] = safe_int(state.get("verification_turn", 0), 0, minimum=0) + 1
        decision = build_verification_decision(
            state,
            data,
            response,
            verification_done_keyword,
            task_done_keyword,
        )
        save_state(path, state)
        return codex_stop_output(decision)

    if phase != "implementation":
        return {}

    state["implementation_turn"] = safe_int(state.get("implementation_turn", 0), 0, minimum=0) + 1
    if contains_explicit_keyword(response, task_done_keyword):
        if contains_explicit_keyword(response, verification_done_keyword):
            state["phase"] = "done"
            state["verification_turn"] = 0
            save_state(path, state)
            return codex_stop_output(
                {"continue": False, "prompt": "", "note": "Verification and task completion keywords detected."}
            )
        state["phase"] = "verification"
        state["verification_turn"] = 0
        save_state(path, state)
        return codex_stop_output(
            {
                "continue": True,
                "prompt": default_verification_start_prompt(
                    str(state.get("spec_markdown", "")),
                    response,
                    verification_done_keyword,
                    task_done_keyword,
                ),
                "note": "Task completion keyword appeared before verification completion; continuing into verification.",
            }
        )
    if contains_explicit_keyword(response, implementation_done_keyword):
        state["phase"] = "verification"
        state["verification_turn"] = 0
        save_state(path, state)
        return codex_stop_output(
            {
                "continue": True,
                "prompt": default_verification_start_prompt(
                    str(state.get("spec_markdown", "")),
                    response,
                    verification_done_keyword,
                    task_done_keyword,
                ),
                "note": "Implementation completion keyword detected; switching to verification phase.",
            }
        )

    decision = build_continue_decision(state, data, response)
    save_state(path, state)
    return codex_stop_output(decision)


def handle_session_start(state: dict[str, Any]) -> dict[str, Any]:
    return codex_session_start_output(state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["codex"], required=True)
    args = parser.parse_args()

    data = load_input()
    if should_skip(args.current, data):
        print("{}")
        return 0

    session_id = session_id_from(data)
    path = state_path(session_id)
    state = load_state(path)
    event_name = str(data.get("hook_event_name", ""))

    if event_name == "SessionStart":
        output = handle_session_start(state)
    elif event_name == "UserPromptSubmit":
        output = handle_user_prompt_submit(data, state, path)
    elif event_name == "Stop":
        output = handle_stop(data, state, path)
    else:
        output = {}

    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
