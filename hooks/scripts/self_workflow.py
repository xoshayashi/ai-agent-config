#!/usr/bin/env python3
"""Generic self-workflow hook for Codex, Claude Code, and Gemini CLI.

This hook keeps each CLI responsible for finishing its own work by using:
- A self-contained refinment skill for startup prompt tightening
- A self-contained self-workflow state machine for spec, implementation,
  verification, and completion boundaries

Design goals:
- No external LLM reviewer subprocess in the main path
- One reusable workflow across Codex, Claude Code, and Gemini CLI
- Explicit recursion guards
- Deterministic, session-scoped state on local disk
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

SUPPORTED_EVENTS: dict[str, set[str]] = {
    "codex": {"Stop"},
    "claude": {"Stop", "SubagentStop"},
    "gemini": {"AfterAgent"},
}
REFINMENT_SKILL = "$refinment"

DEFAULT_SPEC_DONE_KEYWORD = "[[SPEC_DONE]]"
DEFAULT_IMPLEMENTATION_DONE_KEYWORD = "[[IMPLEMENTATION_DONE]]"
DEFAULT_VERIFICATION_DONE_KEYWORD = "[[VERIFICATION_DONE]]"
DEFAULT_TASK_DONE_KEYWORD = "[[TASK_DONE]]"
DELTA_ONLY_RESPONSE_PATTERN = re.compile(
    r"(\bdelta\b|\bcorrection\b|\berrata\b|\bclarification\b|"
    r"補足|追記|訂正|修正|差分|追加確認)",
    re.IGNORECASE,
)
PHASE_SIGNAL_PATTERN = re.compile(
    r"^(verification_ready|task_complete|verification_incomplete|implementation_in_progress)$"
)


def env_value(name: str, legacy_name: str, default: str) -> str:
    if name in os.environ:
        return os.environ[name]
    if legacy_name in os.environ:
        return os.environ[legacy_name]
    return default


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


def should_skip(current: str, data: dict[str, Any]) -> bool:
    if os.environ.get("AI_AGENT_SELF_WORKFLOW_ACTIVE") == "1":
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
    root = env_value(
        "AI_AGENT_SELF_WORKFLOW_STATE_DIR",
        "AI_AGENT_ORCHESTRATOR_STATE_DIR",
        "~/.llm-config/self-workflow",
    )
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
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


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
    # .../<repo>/hooks/scripts/self_workflow.py
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
    return (
        choose_completion_keyword(tokens, DEFAULT_SPEC_DONE_KEYWORD, "SPEC_DONE"),
        choose_completion_keyword(tokens, DEFAULT_IMPLEMENTATION_DONE_KEYWORD, "IMPLEMENTATION_DONE"),
        choose_completion_keyword(tokens, DEFAULT_VERIFICATION_DONE_KEYWORD, "VERIFICATION_DONE"),
        choose_completion_keyword(tokens, DEFAULT_TASK_DONE_KEYWORD, "TASK_DONE"),
    )


def choose_completion_keyword(tokens: list[str], default: str, marker: str) -> str:
    if default in tokens:
        return default
    for token in tokens:
        if marker in token:
            return token
    return default


def contains_explicit_keyword(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    pattern = re.compile(
        rf"(?m)^\s*(?:[-*+]\s+|[0-9]+[.)]\s+)?{re.escape(keyword)}\s*$"
    )
    return pattern.search(text) is not None


def clip_text(text: str, default_limit: int = 6000) -> str:
    limit = safe_int(
        env_value(
            "AI_AGENT_SELF_WORKFLOW_PROMPT_BODY_CHARS",
            "AI_AGENT_ORCHESTRATOR_PROMPT_BODY_CHARS",
            str(default_limit),
        ),
        default_limit,
        minimum=400,
        maximum=40000,
    )
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[-limit:]


def response_from(data: dict[str, Any]) -> str:
    for key in ("prompt_response", "last_assistant_message", "response"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def prefer_delta_only_followup(response: str) -> bool:
    return DELTA_ONLY_RESPONSE_PATTERN.search(response) is not None


def normalize_checks_run(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def extract_phase_packet(response: str) -> dict[str, Any]:
    payload = parse_json_from_text(response)
    if not payload:
        return {}
    phase_signal = str(payload.get("phase_signal", "")).strip().lower()
    if not phase_signal or not PHASE_SIGNAL_PATTERN.fullmatch(phase_signal):
        return {}
    checks_run = normalize_checks_run(payload.get("checks_run"))
    packet: dict[str, Any] = {
        "phase_signal": phase_signal,
        "summary": str(payload.get("summary", "")).strip(),
        "checks_run": checks_run,
        "checks_run_count": len(checks_run),
        "diff_reviewed": bool(payload.get("diff_reviewed", False)),
        "self_review_complete": bool(payload.get("self_review_complete", False)),
    }
    return packet


def update_state_from_phase_packet(state: dict[str, Any], packet: dict[str, Any]) -> None:
    if not packet:
        return
    state["last_phase_signal"] = str(packet.get("phase_signal", "")).strip()
    if packet.get("summary"):
        state["verification_summary"] = str(packet.get("summary", "")).strip()
    state["checks_run_count"] = safe_int(packet.get("checks_run_count", 0), 0, minimum=0)
    state["diff_reviewed"] = bool(packet.get("diff_reviewed", False))
    state["self_review_complete"] = bool(packet.get("self_review_complete", False))


def verification_evidence_complete(packet: dict[str, Any], response: str, verification_done_keyword: str, task_done_keyword: str) -> bool:
    if contains_explicit_keyword(response, verification_done_keyword) and contains_explicit_keyword(response, task_done_keyword):
        return True
    if not packet:
        return False
    return (
        str(packet.get("phase_signal", "")).strip().lower() == "task_complete"
        and bool(packet.get("diff_reviewed"))
        and bool(packet.get("self_review_complete"))
        and safe_int(packet.get("checks_run_count", 0), 0, minimum=0) > 0
    )


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


def default_spec_refinement_prompt(spec_markdown: str, spec_done_keyword: str) -> str:
    return (
        "Refine the specification using the reviewed draft below. Tighten missing requirements, "
        "acceptance criteria, edge cases, and implementation steps. Keep scope aligned with the "
        f"original task, and include {spec_done_keyword} only when the specification is truly implementation-ready.\n\n"
        f"Reviewed specification draft:\n{spec_markdown}"
    )


def default_spec_refinment_gate_prompt(spec_markdown: str, spec_done_keyword: str) -> str:
    return (
        f"Use {REFINMENT_SKILL} to tighten the specification draft yourself. "
        "Decide whether the draft is implementation-ready, then revise it in place. "
        "Preserve scope, constraints, acceptance criteria, and concrete implementation steps. "
        f"If the spec is ready, return the revised spec with {spec_done_keyword} on its own line. "
        f"If it is not ready, return a tighter draft without {spec_done_keyword}. "
        "Do not start code changes in this response.\n\n"
        f"Draft specification:\n{spec_markdown}"
    )


def default_implementation_start_prompt(
    spec_markdown: str,
    implementation_brief: str,
    implementation_done_keyword: str,
) -> str:
    lines = [
        "Start implementation from the approved specification below.",
        "Work step by step, keep the implementation aligned to the spec, and report concrete progress.",
        f"At material stop boundaries, use {REFINMENT_SKILL} when you need a tighter next-step brief or a clearer decision on whether verification should begin.",
        f"When implementation is ready for verification, emit {implementation_done_keyword} on its own line or include a fenced JSON object with phase_signal set to verification_ready and a short summary.",
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
        f"Do not stop yet. Before deciding completion, use {REFINMENT_SKILL} to tighten the verification brief. "
        "Then run the most relevant tests or verification checks, inspect the diff, "
        "and perform a focused self-review against the approved specification.\n"
        "If verification finds only a narrow factual omission or recommendation change, do not restate the whole earlier answer. "
        "Respond with the delta only: the corrected point, why it matters, and the revised conclusion.\n"
        "If verification confirms the prior answer as-is, do not repeat the answer body. Briefly note the checks and finish.\n"
        f"Use {verification_done_keyword} only when verification and self-review are complete. "
        f"Use {task_done_keyword} only when the task is truly complete end-to-end.\n\n"
        "If you want to report structured completion evidence, include a fenced JSON object with:\n"
        '{"phase_signal":"task_complete","summary":"...","checks_run":["..."],"diff_reviewed":true,"self_review_complete":true}\n\n'
        f"Approved specification:\n{spec_markdown}\n\n"
        f"Latest implementation summary:\n{implementation_response}"
    )


def default_implementation_continue_prompt(
    spec_markdown: str,
    response: str,
    implementation_done_keyword: str,
) -> str:
    lines = [
        f"Use {REFINMENT_SKILL} on the latest implementation state.",
        "Decide whether one more concrete implementation step is needed or whether the task is ready for verification.",
        "After the refinment pass, act on it yourself in the same turn.",
    ]
    lines.extend(
        [
            f"If implementation is ready for verification, emit {implementation_done_keyword} on its own line or include a fenced JSON object with `phase_signal` set to `verification_ready`.",
            "If more work remains, do the next concrete implementation step now instead of only summarizing it.",
            "",
            "Approved specification:",
            spec_markdown,
            "",
            "Latest implementation response:",
            clip_text(response),
        ]
    )
    return "\n".join(lines)


def default_verification_continue_prompt(
    spec_markdown: str,
    response: str,
    verification_done_keyword: str,
    task_done_keyword: str,
) -> str:
    delta_guidance = (
        "When only a small correction or supplement is needed, give the delta only instead of retelling the whole answer.\n"
    )
    if prefer_delta_only_followup(response):
        delta_guidance = (
            "Keep the follow-up delta-only unless verification uncovered a broader problem. "
            "Do not restate unchanged background.\n"
        )
    return (
        f"Use {REFINMENT_SKILL} on the verification state. "
        "Decide whether any meaningful verification, diff inspection, or self-review work is still missing. "
        "Then perform the smallest missing verification or fix yourself in the same turn.\n"
        f"{delta_guidance}"
        f"Emit {verification_done_keyword} and {task_done_keyword} only when the task is truly complete, "
        'or return a fenced JSON packet such as {"phase_signal":"task_complete","summary":"...","checks_run":["..."],"diff_reviewed":true,"self_review_complete":true} when the completion evidence is real.\n\n'
        f"Approved specification:\n{spec_markdown}\n\n"
        f"Latest verification response:\n{clip_text(response)}"
    )


def apply_continuation_safety(state: dict[str, Any], next_prompt: str, note: str) -> dict[str, Any]:
    max_continuations = safe_int(
        env_value(
            "AI_AGENT_SELF_WORKFLOW_MAX_CONTINUATIONS_PER_TASK",
            "AI_AGENT_ORCHESTRATOR_MAX_CONTINUATIONS_PER_TASK",
            "5",
        ),
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
        env_value(
            "AI_AGENT_SELF_WORKFLOW_MAX_SAME_PROMPT",
            "AI_AGENT_ORCHESTRATOR_MAX_SAME_PROMPT",
            "2",
        ),
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

    return {"continue": True, "prompt": next_prompt, "note": note}


def build_continue_decision(state: dict[str, Any], _data: dict[str, Any], response: str) -> dict[str, Any]:
    spec_markdown = str(state.get("spec_markdown", ""))
    _, implementation_done_keyword, _, _ = completion_keywords()
    next_prompt = default_implementation_continue_prompt(
        spec_markdown,
        response,
        implementation_done_keyword,
    )
    note = f"Skill-driven implementation refinment requested via {REFINMENT_SKILL}."
    return apply_continuation_safety(state, next_prompt, note)


def build_verification_decision(
    state: dict[str, Any],
    _data: dict[str, Any],
    response: str,
    verification_done_keyword: str,
    task_done_keyword: str,
) -> dict[str, Any]:
    verification_turn = safe_int(state.get("verification_turn", 0), 0, minimum=0)
    max_verification_turns = safe_int(
        env_value(
            "AI_AGENT_SELF_WORKFLOW_MAX_VERIFICATION_TURNS",
            "AI_AGENT_ORCHESTRATOR_MAX_VERIFICATION_TURNS",
            "3",
        ),
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

    phase_packet = extract_phase_packet(response)
    update_state_from_phase_packet(state, phase_packet)
    if verification_evidence_complete(phase_packet, response, verification_done_keyword, task_done_keyword):
        state["phase"] = "done"
        state["verification_turn"] = 0
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        return {"continue": False, "prompt": "", "note": "Verification completion detected."}

    spec_markdown = str(state.get("spec_markdown", ""))
    next_prompt = default_verification_continue_prompt(
        spec_markdown,
        response,
        verification_done_keyword,
        task_done_keyword,
    )
    return apply_continuation_safety(
        state,
        next_prompt,
        f"Skill-driven verification refinment requested via {REFINMENT_SKILL}.",
    )


def stop_output(current: str, decision: dict[str, Any]) -> dict[str, Any]:
    if decision.get("continue") and decision.get("prompt"):
        if current == "gemini":
            payload: dict[str, Any] = {
                "decision": "deny",
                "reason": str(decision.get("prompt", "")).strip(),
            }
        else:
            payload = {
                "decision": "block",
                "reason": str(decision.get("prompt", "")).strip(),
            }
        note = str(decision.get("note", "")).strip()
        if note:
            payload["systemMessage"] = f"Auto-continuing via self-workflow: {note}"
        return payload
    note = str(decision.get("note", "")).strip()
    if note:
        return {"systemMessage": f"Self-workflow: {note}"}
    return {}


def handle_stop(current: str, data: dict[str, Any], state: dict[str, Any], path: Path) -> dict[str, Any]:
    response = response_from(data)
    if not response:
        return {}

    phase = str(state.get("phase", ""))
    spec_done_keyword, implementation_done_keyword, verification_done_keyword, task_done_keyword = completion_keywords()

    # Bootstrap path for idle sessions: with the pre-work hook gone, a brand-new
    # session has no `phase` set when its first response arrives. The LLM signals
    # opt-in to the auto-continuation loop by emitting `[[SPEC_DONE]]`. When we
    # see that on an idle phase, treat the response as a freshly authored spec
    # so the existing `spec_authoring` branch can transition into `spec_review`.
    if not phase and contains_explicit_keyword(response, spec_done_keyword):
        phase = "spec_authoring"
        state["phase"] = phase
        state.setdefault("spec_revision_count", 0)
        state.setdefault("original_prompt", "")

    if phase == "spec_authoring":
        spec_revision_count = safe_int(state.get("spec_revision_count", 0), 0, minimum=0) + 1
        state["spec_revision_count"] = spec_revision_count
        state["spec_markdown"] = response
        spec_ready = contains_explicit_keyword(response, spec_done_keyword)
        spec_review_fallback = (
            not spec_ready
            and spec_revision_count >= 2
            and spec_is_review_candidate(response)
        )
        if not spec_ready and not spec_review_fallback:
            # Persist the draft (and incremented revision count) so the next
            # Stop sees the latest progress.
            save_state(path, state)
            return {
                "systemMessage": (
                    f"Self-workflow: specification draft saved. Continue refining and include "
                    f"{spec_done_keyword} when it is ready for the next refinment gate."
                )
            }
        # Single write at the final phase. This avoids a window where a crash
        # between the draft-save and the spec_review-save would leave disk state
        # in spec_authoring with revision count incremented.
        state["phase"] = "spec_review"
        save_state(path, state)
        return stop_output(
            current,
            {
                "continue": True,
                "prompt": default_spec_refinment_gate_prompt(response, spec_done_keyword),
                "note": (
                    f"Skill-driven specification refinment requested via {REFINMENT_SKILL}."
                    if spec_ready
                    else f"Structured specification draft qualified for refinment via {REFINMENT_SKILL}."
                ),
            }
        )

    if phase == "spec_review":
        state["spec_markdown"] = response
        state["implementation_brief"] = ""
        state["next_step_prompt"] = ""
        state["implementation_turn"] = 0
        state["verification_turn"] = 0
        state["continuation_count"] = 0
        state["same_prompt_count"] = 0
        state["last_continuation_prompt"] = ""
        state["last_phase_signal"] = ""
        state["verification_summary"] = ""
        state["checks_run_count"] = 0
        state["diff_reviewed"] = False
        state["self_review_complete"] = False
        if contains_explicit_keyword(response, spec_done_keyword):
            state["phase"] = "implementation"
            save_state(path, state)
            return stop_output(
                current,
                {
                    "continue": True,
                    "prompt": default_implementation_start_prompt(
                        response,
                        "",
                        implementation_done_keyword,
                    ),
                    "note": "Refined specification is ready. Starting implementation under the self-workflow.",
                }
            )
        state["phase"] = "spec_authoring"
        save_state(path, state)
        return stop_output(
            current,
            {
                "continue": True,
                "prompt": default_spec_refinement_prompt(response, spec_done_keyword),
                "note": f"Specification still needs refinment. Continuing specification work after {REFINMENT_SKILL}.",
            }
        )

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
        return stop_output(current, decision)

    if phase != "implementation":
        return {}

    state["implementation_turn"] = safe_int(state.get("implementation_turn", 0), 0, minimum=0) + 1
    phase_packet = extract_phase_packet(response)
    update_state_from_phase_packet(state, phase_packet)
    phase_signal = str(phase_packet.get("phase_signal", "")).strip().lower()
    verification_ready = phase_signal == "verification_ready"
    task_complete_signal = phase_signal == "task_complete"
    if contains_explicit_keyword(response, task_done_keyword) or task_complete_signal:
        if contains_explicit_keyword(response, verification_done_keyword):
            state["phase"] = "done"
            state["verification_turn"] = 0
            save_state(path, state)
            return stop_output(
                current,
                {"continue": False, "prompt": "", "note": "Verification and task completion keywords detected."}
            )
        state["phase"] = "verification"
        state["verification_turn"] = 0
        save_state(path, state)
        return stop_output(
            current,
            {
                "continue": True,
                "prompt": default_verification_start_prompt(
                    str(state.get("spec_markdown", "")),
                    response,
                    verification_done_keyword,
                    task_done_keyword,
                ),
                "note": (
                    "Structured task-complete signal appeared before verification completion; continuing into verification."
                    if task_complete_signal and not contains_explicit_keyword(response, task_done_keyword)
                    else "Task completion keyword appeared before verification completion; continuing into verification."
                ),
            }
        )
    if contains_explicit_keyword(response, implementation_done_keyword) or verification_ready:
        state["phase"] = "verification"
        state["verification_turn"] = 0
        save_state(path, state)
        return stop_output(
            current,
            {
                "continue": True,
                "prompt": default_verification_start_prompt(
                    str(state.get("spec_markdown", "")),
                    response,
                    verification_done_keyword,
                    task_done_keyword,
                ),
                "note": (
                    "Structured verification-ready signal detected; switching to verification phase."
                    if verification_ready and not contains_explicit_keyword(response, implementation_done_keyword)
                    else "Implementation completion keyword detected; switching to verification phase."
                ),
            }
        )

    decision = build_continue_decision(state, data, response)
    save_state(path, state)
    return stop_output(current, decision)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["claude", "codex", "gemini"], required=True)
    args = parser.parse_args()

    data = load_input()
    if should_skip(args.current, data):
        print("{}")
        return 0

    session_id = session_id_from(data)
    path = state_path(session_id)
    state = load_state(path)
    event_name = str(data.get("hook_event_name", ""))

    if event_name in {"Stop", "SubagentStop", "AfterAgent"}:
        output = handle_stop(args.current, data, state, path)
    else:
        output = {}

    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
