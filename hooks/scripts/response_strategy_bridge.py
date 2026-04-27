#!/usr/bin/env python3
"""Generate a post-response strategy via a peer LLM hook.

This hook is intentionally fail-open:
- If disabled, unavailable, timed out, or unparsable, it returns `{}`.
- It never blocks the agent loop unless an explicit strategy is produced.
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


TRIVIAL_PROMPT_PATTERN = re.compile(
    r"^\s*(ありがとう|thanks|thank you|ok|了解|はい|いいえ|stop|pause|status|進捗|止めて)[。.!?\s]*$",
    re.IGNORECASE,
)

SUPPORTED_EVENTS: dict[str, set[str]] = {
    "claude": {"Stop", "SubagentStop"},
    "codex": {"Stop"},
    "gemini": {"AfterAgent"},
}


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
    return os.environ.get("AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY") == "1"


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


def transcript_excerpt(path_value: Any) -> str:
    if os.environ.get("AI_AGENT_RESPONSE_STRATEGY_INCLUDE_TRANSCRIPT", "1") != "1":
        return "Transcript excerpt disabled."
    if not isinstance(path_value, str) or not path_value:
        return "No transcript path supplied."
    path = Path(path_value)
    if not path.is_file():
        return "Transcript path not readable."

    max_lines = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_TRANSCRIPT_LINES", "60"))
    max_chars = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_TRANSCRIPT_CHARS", "16000"))
    tail_budget = max(max_chars * 4, 20000)
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


def prompt_from_hook(data: dict[str, Any]) -> str:
    value = data.get("prompt")
    return value if isinstance(value, str) else ""


def response_from_hook(data: dict[str, Any]) -> str:
    for key in ("prompt_response", "last_assistant_message", "response"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def should_skip(current: str, data: dict[str, Any], prompt: str, response: str) -> bool:
    if not enabled():
        return True
    if os.environ.get("AI_AGENT_RESPONSE_STRATEGY_ACTIVE") == "1":
        return True

    event_name = str(data.get("hook_event_name", ""))
    allowed = SUPPORTED_EVENTS.get(current, set())
    if event_name not in allowed:
        return True

    if data.get("stop_hook_active") is True and os.environ.get("AI_AGENT_RESPONSE_STRATEGY_ALLOW_REENTRY") != "1":
        return True

    min_response_chars = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_MIN_RESPONSE_CHARS", "120"))
    if len(response.strip()) < min_response_chars:
        return True

    if TRIVIAL_PROMPT_PATTERN.search(prompt):
        return True

    return False


def choose_provider(current: str) -> str:
    requested = os.environ.get("AI_AGENT_RESPONSE_STRATEGY_PROVIDER", "auto").strip().lower()
    if requested in {"gemini", "codex", "ollama"}:
        return requested

    # Auto route preserves the user's desired pattern:
    # - Claude/Codex -> Gemini
    # - Gemini -> Codex
    if current in {"claude", "codex"}:
        return "gemini"
    return "codex"


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def resolve_invocation(current: str, cwd: str, packet: str) -> tuple[list[str], str] | None:
    provider = choose_provider(current)

    if provider == "gemini":
        if not command_available("gemini"):
            return None
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
        return command, ""

    if provider == "codex":
        if not command_available("codex"):
            return None
        command = [
            "codex",
            "exec",
            "--cd",
            cwd or os.getcwd(),
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "-",
        ]
        return command, packet

    if provider == "ollama":
        if not command_available("ollama"):
            return None
        model = os.environ.get("AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL", "").strip()
        if not model:
            return None
        command = ["ollama", "run", model]
        return command, packet

    return None


def build_packet(current: str, data: dict[str, Any], prompt: str, response: str) -> str:
    cwd = str(data.get("cwd", ""))
    model = str(data.get("model", ""))
    event_name = str(data.get("hook_event_name", ""))
    excerpt = transcript_excerpt(data.get("transcript_path"))

    peer = choose_provider(current)
    route = f"{current} -> {peer}"
    max_strategy_chars = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_MAX_PROMPT_CHARS", "1800"))

    return f"""You are an external response reviewer in a multi-LLM autonomous loop.
Your job is to decide whether the main agent should continue one more turn, and if so, provide one high-quality continuation prompt.

Return strict JSON only:
{{
  "action": "continue" | "allow_stop",
  "strategy_prompt": "string",
  "strategy_rationale": "short string",
  "needs_human": true | false,
  "human_question": "string"
}}

Decision rule:
- Use "continue" only when one more turn is materially valuable (missed requirement, risky assumption, unverified claim, obvious next check).
- Use "allow_stop" when the answer is already sufficient.

If action is "continue", strategy_prompt must:
- Preserve user constraints and scope.
- Stay abstract and inclusive (do not force a single implementation path unless explicitly required).
- Include concrete verification guidance where useful.
- Be <= {max_strategy_chars} characters.

If action is "allow_stop", strategy_prompt should be an empty string.
If human confirmation is needed, set needs_human=true and provide a concise human_question.

Context packet:
- Route: {route}
- Hook event: {event_name}
- Working directory: {cwd}
- Active model: {model}
- User prompt:
{prompt}
- Latest assistant response:
{response}
- Recent redacted transcript excerpt:
{excerpt}
"""


def call_peer(current: str, packet: str, cwd: str) -> str:
    spec = resolve_invocation(current, cwd, packet)
    if spec is None:
        return ""
    command, stdin_payload = spec

    timeout = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_TIMEOUT_SECONDS", "35"))
    max_chars = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_OUTPUT_CHARS", "12000"))

    env = os.environ.copy()
    env["AI_AGENT_RESPONSE_STRATEGY_ACTIVE"] = "1"

    try:
        completed = subprocess.run(
            command,
            input=stdin_payload,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd or None,
            env=env,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    if completed.returncode != 0:
        return ""

    output = completed.stdout.strip()
    if not output:
        return ""
    return output[:max_chars]


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


def parse_peer_json(output: str) -> dict[str, Any]:
    for candidate in _extract_json_candidates(output):
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def review_to_decision(review: dict[str, Any]) -> dict[str, Any]:
    action_raw = review.get("action")
    action = action_raw.lower() if isinstance(action_raw, str) else ""
    strategy_prompt = review.get("strategy_prompt")
    strategy = strategy_prompt.strip() if isinstance(strategy_prompt, str) else ""
    rationale = review.get("strategy_rationale")
    rationale_text = rationale.strip() if isinstance(rationale, str) else ""
    needs_human = _as_bool(review.get("needs_human"))
    human_question = review.get("human_question")
    human_question_text = human_question.strip() if isinstance(human_question, str) else ""

    max_strategy_chars = int(os.environ.get("AI_AGENT_RESPONSE_STRATEGY_MAX_PROMPT_CHARS", "1800"))
    if len(strategy) > max_strategy_chars:
        strategy = strategy[:max_strategy_chars]

    should_continue = action == "continue" and bool(strategy) and not needs_human
    message_parts = []
    if rationale_text:
        message_parts.append(f"Peer rationale: {rationale_text}")
    if needs_human and human_question_text:
        message_parts.append(f"Human-in-the-loop check: {human_question_text}")
    message = "\n".join(message_parts)

    return {
        "continue": should_continue,
        "strategy_prompt": strategy,
        "system_message": message,
    }


def build_hook_output(current: str, decision: dict[str, Any]) -> dict[str, Any]:
    should_continue = bool(decision.get("continue"))
    strategy_prompt = str(decision.get("strategy_prompt", "")).strip()
    system_message = str(decision.get("system_message", "")).strip()

    if should_continue and strategy_prompt:
        if current == "gemini":
            payload: dict[str, Any] = {"decision": "deny", "reason": strategy_prompt}
        else:
            payload = {"decision": "block", "reason": strategy_prompt}
        if system_message:
            payload["systemMessage"] = system_message
        return payload

    if system_message:
        return {"systemMessage": system_message}

    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["claude", "codex", "gemini"], required=True)
    args = parser.parse_args()

    data = load_input()
    prompt = prompt_from_hook(data)
    response = response_from_hook(data)
    if should_skip(args.current, data, prompt, response):
        print("{}")
        return 0

    packet = build_packet(args.current, data, prompt, response)
    peer_output = call_peer(args.current, packet, str(data.get("cwd", "")))
    if not peer_output:
        print("{}")
        return 0

    review = parse_peer_json(peer_output)
    if not review:
        print("{}")
        return 0

    decision = review_to_decision(review)
    print(json.dumps(build_hook_output(args.current, decision), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
