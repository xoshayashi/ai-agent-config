#!/usr/bin/env python3
"""Codex-centered multi-LLM orchestration hook.

This hook keeps Codex as the execution hub while using:
- Claude for spec drafting/finalization and implementation guidance
- Gemini for independent spec/progress critique

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
from pathlib import Path
from typing import Any


SUPPORTED_EVENTS: dict[str, set[str]] = {
    "codex": {"SessionStart", "UserPromptSubmit", "Stop"},
}

DEFAULT_SPEC_DONE_KEYWORD = "[[SPEC_DONE]]"
DEFAULT_IMPL_DONE_KEYWORDS = {"[[IMPLEMENTATION_DONE]]", "[[TASK_DONE]]"}
FOLLOWUP_PROMPT_PATTERN = re.compile(
    r"^\s*(continue|go on|next|ok|yes|続けて|続行|進めて|次|そのまま|お願いします|お願い)\b",
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
    return os.environ.get("AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION", "1") == "1"


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
    path.write_text(payload, encoding="utf-8")


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


def completion_keywords() -> tuple[str, set[str]]:
    path = hooks_md_path()
    if not path.is_file():
        return DEFAULT_SPEC_DONE_KEYWORD, set(DEFAULT_IMPL_DONE_KEYWORDS)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return DEFAULT_SPEC_DONE_KEYWORD, set(DEFAULT_IMPL_DONE_KEYWORDS)
    tokens = sorted(set(re.findall(r"\[\[[A-Z0-9_:-]+\]\]", text)))
    spec_done = DEFAULT_SPEC_DONE_KEYWORD
    impl_done = set(DEFAULT_IMPL_DONE_KEYWORDS)

    for token in tokens:
        if "SPEC_DONE" in token:
            spec_done = token
            break

    for token in tokens:
        if "IMPLEMENTATION_DONE" in token or "TASK_DONE" in token:
            impl_done.add(token)
    return spec_done, impl_done


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


def run_cli(command: list[str], stdin_payload: str, cwd: str) -> str:
    timeout = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_TIMEOUT_SECONDS", "10"), 10, minimum=3, maximum=60)
    output_limit = safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_OUTPUT_CHARS", "20000"), 20000, minimum=1000, maximum=200000)
    try:
        completed = subprocess.run(
            command,
            input=stdin_payload,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd or None,
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


def call_claude(packet: str) -> str:
    if not command_available("claude"):
        return ""
    command = [
        "claude",
        "-p",
        packet,
        "--output-format",
        "text",
        "--permission-mode",
        "plan",
        "--max-turns",
        "1",
    ]
    return run_cli(command, "", "")


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
    return run_cli(command, "", "")


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
    if len(stripped) <= 48 and FOLLOWUP_PROMPT_PATTERN.search(stripped):
        return True
    return False


def spec_status_from(packet: dict[str, Any], spec_done_keyword: str) -> str:
    raw_status = str(packet.get("status", "")).strip().lower()
    spec_markdown = str(packet.get("spec_markdown", ""))
    if raw_status in {"draft", "done"}:
        return raw_status
    return "done" if spec_done_keyword in spec_markdown else "draft"


def build_spec_by_claude_and_gemini(data: dict[str, Any], prompt: str, spec_done_keyword: str) -> dict[str, Any]:
    cwd = str(data.get("cwd", ""))
    model = str(data.get("model", ""))
    excerpt = transcript_excerpt(data.get("transcript_path"))
    hooks_doc = hooks_md_path()

    claude_seed_packet = f"""You are the specification lead for a Codex-centered implementation workflow.
Return strict JSON:
{{
  "spec_markdown": "string",
  "status": "draft|done",
  "implementation_brief": "string"
}}

Requirements:
- Preserve user constraints and scope.
- Keep the spec concrete enough for implementation but avoid over-constraining methods.
- If the spec is implementation-ready, include `{spec_done_keyword}` inside spec_markdown.

Context:
- User prompt:
{prompt}
- CWD: {cwd}
- Active model: {model}
- Hook rules document path: {hooks_doc}
- Recent redacted transcript excerpt:
{excerpt}
"""
    claude_seed_raw = call_claude(claude_seed_packet)
    claude_seed_json = parse_json_from_text(claude_seed_raw)
    seed_spec = str(claude_seed_json.get("spec_markdown", "")).strip() or claude_seed_raw

    gemini_review_packet = f"""You are an independent reviewer.
Given this specification draft, return strict JSON:
{{
  "critical_gaps": ["..."],
  "simplifications": ["..."],
  "risk_checks": ["..."]
}}

Do not re-write the full spec. Focus on missing requirements, simplification opportunities, and risk checks.

Spec draft:
{seed_spec}
"""
    gemini_review_raw = call_gemini(gemini_review_packet)
    gemini_review_json = parse_json_from_text(gemini_review_raw)
    gemini_review = gemini_review_json if gemini_review_json else {"critical_gaps": [], "simplifications": [], "risk_checks": []}

    claude_finalize_packet = f"""You are the specification lead finalizing a build-ready spec for Codex.
Return strict JSON:
{{
  "spec_markdown": "string",
  "status": "draft|done",
  "implementation_brief": "string",
  "next_step_prompt_for_codex": "string"
}}

Rules:
- Keep scope aligned with the user request.
- Integrate useful reviewer feedback.
- If build-ready, include `{spec_done_keyword}` in spec_markdown.
- Keep implementation brief short and actionable.

User prompt:
{prompt}

Seed spec:
{seed_spec}

Gemini review:
{json.dumps(gemini_review, ensure_ascii=False)}
"""
    claude_final_raw = call_claude(claude_finalize_packet)
    final_json = parse_json_from_text(claude_final_raw)

    spec_markdown = str(final_json.get("spec_markdown", "")).strip() or seed_spec
    status = str(final_json.get("status", "")).strip().lower()
    implementation_brief = str(final_json.get("implementation_brief", "")).strip()
    next_step_prompt = str(final_json.get("next_step_prompt_for_codex", "")).strip()

    if status not in {"draft", "done"}:
        status = "done" if spec_done_keyword in spec_markdown else "draft"

    return {
        "spec_markdown": spec_markdown,
        "status": status,
        "implementation_brief": implementation_brief,
        "next_step_prompt_for_codex": next_step_prompt,
        "gemini_review": gemini_review,
    }


def orchestration_prompt_context(phase: str, spec_markdown: str, implementation_brief: str, next_step_prompt: str) -> str:
    lines = [
        "Multi-LLM orchestration context (Codex hub mode).",
        "Use this as advisory context. User/system/developer instructions remain authoritative.",
    ]
    if phase == "spec_draft":
        lines.extend(["", "Current phase: specification refinement."])
    elif phase == "implementation":
        lines.extend(["", "Current phase: implementation."])
    lines.extend(["", "Specification:", spec_markdown])
    if implementation_brief:
        lines.extend(["", "Implementation brief:", implementation_brief])
    if next_step_prompt:
        lines.extend(["", "Suggested first implementation step:", next_step_prompt])
    return "\n".join(lines).strip()


def build_continue_decision(state: dict[str, Any], data: dict[str, Any], response: str, impl_done_keywords: set[str]) -> dict[str, Any]:
    if any(keyword in response for keyword in impl_done_keywords):
        state["phase"] = "done"
        return {"continue": False, "prompt": "", "note": "Implementation completion keyword detected."}

    spec_markdown = str(state.get("spec_markdown", ""))
    turn = safe_int(state.get("implementation_turn", 0), 0, minimum=0)
    review_every = safe_int(
        state.get("gemini_review_every", os.environ.get("AI_AGENT_ORCHESTRATOR_GEMINI_REVIEW_EVERY", "3")),
        3,
        minimum=1,
        maximum=20,
    )

    gemini_note = ""
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
    claude_decision_raw = call_claude(claude_decision_packet)
    decision_json = parse_json_from_text(claude_decision_raw)
    action = str(decision_json.get("action", "")).strip().lower()
    next_prompt = str(decision_json.get("next_prompt_for_codex", "")).strip()
    reason = str(decision_json.get("reason", "")).strip()

    should_continue = action == "continue" and bool(next_prompt)
    if not should_continue:
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        return {"continue": False, "prompt": "", "note": reason}

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

    return {"continue": True, "prompt": next_prompt, "note": reason}


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
            payload["systemMessage"] = f"Orchestrator continuation: {note}"
        return payload
    note = str(decision.get("note", "")).strip()
    if note:
        return {"systemMessage": f"Orchestrator: {note}"}
    return {}


def codex_session_start_output(state: dict[str, Any]) -> dict[str, Any]:
    phase = str(state.get("phase", "idle"))
    if phase in {"implementation", "spec_draft"}:
        spec = str(state.get("spec_markdown", ""))
        if spec:
            label = "Current specification"
            if phase == "spec_draft":
                label = "Current draft specification (needs refinement)"
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
    if phase == "spec_draft" and state.get("spec_markdown") and should_keep_current_task(prompt):
        context = orchestration_prompt_context(
            "spec_draft",
            str(state.get("spec_markdown", "")),
            str(state.get("implementation_brief", "")),
            str(state.get("next_step_prompt_for_codex", "")),
        )
        return codex_user_prompt_output(context)

    spec_done_keyword, _ = completion_keywords()
    if phase in {"implementation", "spec_draft"} and not should_keep_current_task(prompt):
        state.clear()

    spec_packet = build_spec_by_claude_and_gemini(data, prompt, spec_done_keyword)
    spec_status = spec_status_from(spec_packet, spec_done_keyword)
    next_phase = "implementation" if spec_status == "done" else "spec_draft"
    state.update(
        {
            "phase": next_phase,
            "spec_markdown": spec_packet["spec_markdown"],
            "implementation_brief": spec_packet.get("implementation_brief", ""),
            "next_step_prompt_for_codex": spec_packet.get("next_step_prompt_for_codex", ""),
            "gemini_review": spec_packet.get("gemini_review", {}),
            "spec_status": spec_status,
            "implementation_turn": 0,
            "gemini_review_every": safe_int(os.environ.get("AI_AGENT_ORCHESTRATOR_GEMINI_REVIEW_EVERY", "3"), 3, minimum=1, maximum=20),
            "continuation_count": 0,
            "same_prompt_count": 0,
            "last_continuation_prompt": "",
        }
    )
    save_state(path, state)
    context = orchestration_prompt_context(
        next_phase,
        str(state.get("spec_markdown", "")),
        str(state.get("implementation_brief", "")),
        str(state.get("next_step_prompt_for_codex", "")),
    )
    return codex_user_prompt_output(context)


def handle_stop(data: dict[str, Any], state: dict[str, Any], path: Path) -> dict[str, Any]:
    if str(state.get("phase", "")) != "implementation":
        return {}

    response = response_from(data)
    if not response:
        return {}

    state["implementation_turn"] = safe_int(state.get("implementation_turn", 0), 0, minimum=0) + 1
    _, impl_done_keywords = completion_keywords()
    decision = build_continue_decision(state, data, response, impl_done_keywords)
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
