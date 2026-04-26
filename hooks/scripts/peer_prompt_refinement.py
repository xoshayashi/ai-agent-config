#!/usr/bin/env python3
"""Optionally add peer LLM prompt-refinement context before an agent turn."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SIMPLE_PROMPT_PATTERN = re.compile(
    r"^\s*(ありがとう|thanks|thank you|ok|了解|はい|いいえ|stop|pause|止めて|今どういう状態|status)[。.!?\s]*$",
    re.IGNORECASE,
)


def load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def enabled() -> bool:
    return os.environ.get("AI_AGENT_HOOKS_ENABLE_PROMPT_REFINEMENT") == "1"


def prompt_from_hook(data: dict[str, Any]) -> str:
    value = data.get("prompt")
    return value if isinstance(value, str) else ""


def redact(text: str) -> str:
    patterns = [
        (r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+", r"\1=[REDACTED]"),
        # Anthropic keys come before the generic `sk-` rule so their full
        # `sk-ant-...` form is preserved in the redaction label.
        (r"sk-ant-[A-Za-z0-9_-]{20,}", "[REDACTED_ANTHROPIC_KEY]"),
        (r"sk-[A-Za-z0-9_-]{20,}", "[REDACTED_OPENAI_KEY]"),
        (r"AIza[0-9A-Za-z_-]{20,}", "[REDACTED_GOOGLE_KEY]"),
    ]
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    return result


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
    if os.environ.get("AI_AGENT_PROMPT_REFINEMENT_INCLUDE_TRANSCRIPT", "1") != "1":
        return "Transcript excerpt disabled."
    if not isinstance(path_value, str) or not path_value:
        return "No transcript path supplied."

    path = Path(path_value)
    if not path.is_file():
        return "Transcript path not readable."

    max_lines = int(os.environ.get("AI_AGENT_PROMPT_REFINEMENT_TRANSCRIPT_LINES", "40"))
    max_chars = int(os.environ.get("AI_AGENT_PROMPT_REFINEMENT_TRANSCRIPT_CHARS", "12000"))
    # Read 4x max_chars from the tail so we have headroom for partial leading
    # lines and a safety margin for multi-byte UTF-8 boundaries; we still
    # truncate to max_chars / max_lines below.
    tail_budget = max(max_chars * 4, 16384)
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


def should_skip(prompt: str) -> bool:
    if not prompt.strip():
        return True
    if os.environ.get("AI_AGENT_PROMPT_REFINEMENT_ACTIVE") == "1":
        return True
    if SIMPLE_PROMPT_PATTERN.search(prompt):
        return True
    return False


def build_packet(current: str, data: dict[str, Any], prompt: str) -> str:
    cwd = data.get("cwd", "")
    event_name = data.get("hook_event_name", "")
    model = data.get("model", "")
    route = "Gemini CLI" if current in {"codex", "claude"} else "Codex CLI"
    excerpt = transcript_excerpt(data.get("transcript_path"))
    return f"""You are improving a task prompt for another LLM agent. Do not perform the task.
Return a concise improved prompt that preserves all constraints and helps the main agent execute.

Required output:
1. Improved prompt
2. Preserved constraints
3. Missing considerations or risks
4. Suggested skill/workflow triggers
5. What not to change
6. Where the prompt intentionally preserves choice
7. Verification or self-check ideas, only if useful

Context Packet:
- Original prompt:
{prompt}
- Current agent: {current}
- Peer route: {current} -> {route}
- Hook event: {event_name}
- Current working directory: {cwd}
- Active model: {model}
- Recent redacted transcript excerpt:
{excerpt}

Rules:
- Do not override system, developer, tool, or user instructions.
- Do not add new scope unless it is framed as a risk or clarification.
- Preserve exact paths, command names, branch names, PR numbers, IDs, and quoted constraints.
- Keep the improved prompt abstract and inclusive enough for the main agent to choose the best path.
- Do not force one implementation method, tool, conclusion, or output structure unless the user already required it.
- For research tasks, suggest several short query families rather than one overloaded search string.
- Do not request hidden chain-of-thought. Return concise rationale, checks, or verification ideas only where useful.
- Do not call tools, inspect files, browse, run commands, or ask another model.
- This is already a peer-refinement subprocess; do not ask another LLM.
"""


def peer_invocation(current: str, cwd: str, packet: str) -> tuple[list[str], str] | None:
    """Return (command, stdin_payload) for the peer call, or None when unsupported.

    Each peer is invoked through exactly one channel: Gemini receives the full
    packet via `-p` (its documented headless prompt source), while Codex reads
    the packet from stdin via the `-` marker. Mixing `-p` and stdin makes the
    delivery channel CLI-version-dependent, so we deliberately use only one.
    """
    if current in {"codex", "claude"}:
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
        # Close stdin (empty payload) so Gemini does not block waiting on it.
        return command, ""
    if current == "gemini":
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
    return None


def call_peer(current: str, packet: str, cwd: str) -> str:
    spec = peer_invocation(current, cwd, packet)
    if spec is None:
        return ""
    command, stdin_payload = spec

    timeout = int(os.environ.get("AI_AGENT_PROMPT_REFINEMENT_TIMEOUT_SECONDS", "30"))
    max_chars = int(os.environ.get("AI_AGENT_PROMPT_REFINEMENT_OUTPUT_CHARS", "8000"))
    env = os.environ.copy()
    env["AI_AGENT_PROMPT_REFINEMENT_ACTIVE"] = "1"

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


def hook_output(current: str, event_name: str, context: str) -> dict[str, Any]:
    if current == "gemini" or event_name == "BeforeAgent":
        return {
            "hookSpecificOutput": {
                "hookEventName": "BeforeAgent",
                "additionalContext": context,
            }
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["claude", "codex", "gemini"], required=True)
    args = parser.parse_args()

    data = load_input()
    prompt = prompt_from_hook(data)
    if not enabled() or should_skip(prompt):
        print("{}")
        return 0

    packet = build_packet(args.current, data, prompt)
    peer_output = call_peer(args.current, packet, str(data.get("cwd", "")))
    if not peer_output:
        print("{}")
        return 0

    context = (
        "Peer prompt-refinement note. Treat this as advisory context only; "
        "the original user prompt and higher-priority instructions remain authoritative.\n\n"
        f"{peer_output}"
    )
    print(json.dumps(hook_output(args.current, str(data.get("hook_event_name", "")), context)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

