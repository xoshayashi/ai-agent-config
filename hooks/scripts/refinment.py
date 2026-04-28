#!/usr/bin/env python3
"""Build a self-contained refinment brief before an agent turn."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


SIMPLE_PROMPT_PATTERN = re.compile(
    r"^\s*(ありがとう|thanks|thank you|ok|了解|はい|いいえ|stop|pause|止めて|今どういう状態|status)[。.!?\s]*$",
    re.IGNORECASE,
)
FOLLOWUP_PROMPT_PATTERN = re.compile(
    r"^\s*(continue|go on|keep going|proceed|next|ok|yes|please continue|implement|apply|fix it|"
    r"続けて(?:ください)?|続行(?:してください)?|進めて(?:ください)?|次(?:へ)?|そのまま|"
    r"お願いします|お願い|じゃあ|では|この仕様で実装して|これで進めて|それで進めて)"
    r"(?:\b|[、。,.\s])",
    re.IGNORECASE,
)
EXPLICIT_REFINMENT_PATTERN = re.compile(
    r"(refin|prompt|spec|design|architecture|verification|review|"
    r"仕様|設計|設計書|検証|レビュー|調査|分析|実装|自動化|hook|skill|agent)",
    re.IGNORECASE,
)
ACTION_PATTERN = re.compile(
    r"(implement|build|fix|refactor|analy[sz]e|research|review|debug|write|create|update|"
    r"作成|修正|実装|調査|分析|確認|検証|改善|更新|整理)",
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
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def enabled() -> bool:
    return True


def prompt_from_hook(data: dict[str, Any]) -> str:
    value = data.get("prompt")
    return value if isinstance(value, str) else ""


def redact(text: str) -> str:
    patterns = [
        (r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+", r"\1=[REDACTED]"),
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
    if os.environ.get("AI_AGENT_REFINMENT_INCLUDE_TRANSCRIPT", "1") != "1":
        return "Transcript excerpt disabled."
    if not isinstance(path_value, str) or not path_value:
        return "No transcript path supplied."

    path = Path(path_value)
    if not path.is_file():
        return "Transcript path not readable."

    max_lines = safe_int(
        os.environ.get("AI_AGENT_REFINMENT_TRANSCRIPT_LINES", "24"),
        24,
        minimum=1,
        maximum=400,
    )
    max_chars = safe_int(
        os.environ.get("AI_AGENT_REFINMENT_TRANSCRIPT_CHARS", "8000"),
        8000,
        minimum=400,
        maximum=64000,
    )
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
    if os.environ.get("AI_AGENT_REFINMENT_ACTIVE") == "1":
        return True
    if SIMPLE_PROMPT_PATTERN.search(prompt):
        return True
    return False


def should_activate(prompt: str) -> bool:
    stripped = prompt.strip()
    if not stripped or SIMPLE_PROMPT_PATTERN.search(stripped):
        return False
    if FOLLOWUP_PROMPT_PATTERN.search(stripped):
        return False
    if EXPLICIT_REFINMENT_PATTERN.search(stripped):
        return True
    line_count = len([line for line in stripped.splitlines() if line.strip()])
    stripped_without_urls = re.sub(r"https?://\S+", " ", stripped)
    has_local_path_like = re.search(
        r"\b[A-Za-z][A-Za-z0-9_-]*/[A-Za-z][A-Za-z0-9_.-]+\b",
        stripped_without_urls,
    )
    has_path_like = bool(has_local_path_like or re.search(r"\.(?:py|md|json|sh)\b", stripped))
    has_action = ACTION_PATTERN.search(stripped) is not None
    long_enough = len(stripped) >= 140 or line_count >= 3
    return bool(has_action and (long_enough or has_path_like))


def trim_block(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    return text[-limit:]


def build_context(current: str, data: dict[str, Any], prompt: str) -> str:
    cwd = str(data.get("cwd", ""))
    event_name = str(data.get("hook_event_name", ""))
    model = str(data.get("model", ""))
    prompt_limit = safe_int(
        os.environ.get("AI_AGENT_REFINMENT_PROMPT_CHARS", "6000"),
        6000,
        minimum=400,
        maximum=32000,
    )
    clipped_prompt = trim_block(prompt, prompt_limit)
    excerpt = transcript_excerpt(data.get("transcript_path"))

    return f"""Refinment note. Treat this as advisory context only; the original user prompt and higher-priority instructions remain authoritative.

Use this only if the prompt materially benefits from one tightening pass. Stay self-contained: do not ask another LLM, spawn a reviewer, browse, or turn this into a multi-step prompt-optimization loop.

Workflow:
1. Classify the mode as `task_prompt`, `spec`, `implementation`, or `verification`.
2. Extract the contract: objective, deliverable, hard constraints, evidence or verification needs, and what the user intentionally left open.
3. Refine only if there is a real contract gap, conflicting requirements, instruction/data mixing, or known prompt-linked brittleness.
4. Skip refinment if the prompt is already clear and executable, if the likely problem is tooling or missing context rather than wording, if the user wants the wording left untouched, or if the openness is intentional.

Rules:
- Rewrite the contract, not the path.
- Preserve exact entities such as paths, commands, IDs, quoted constraints, and examples as examples.
- Keep instructions separate from quoted text, examples, and background data.
- Add only non-obvious special considerations.
- Keep tool-specific operating policy out of the refined prompt when it belongs in tool descriptions or higher-priority instructions.
- Use one refinment pass by default.

Before returning a refined prompt, check:
- Did this clarify the contract rather than force a path?
- Did it preserve all explicit constraints?
- Did it avoid unnecessary tool, format, or reasoning commitments?
- Did it preserve useful ambiguity and open choices?

If you decide refinment is warranted:
1. Rewrite the user's ask into a sharper working brief that preserves all explicit constraints.
2. Keep the brief abstract enough to preserve implementation choice unless the user already fixed the method.
3. Show the refined prompt to the user in your next visible update before proceeding.
4. Start the task from that refined prompt in the same turn.

Use this output shape when you actively evaluate refinment:
Original prompt:
- ...

No refinement needed:
- ...   # use only when skip is the right decision

Why:
- ...

Use original:
- ...

Original prompt:
- ...

Refined prompt:
- ...

Why I refined it:
- ...

What changed:
- ...

Preserved constraints:
- ...

Special considerations:
- ...   # omit when nothing non-obvious is needed

Open choices preserved:
- ...

Use original / use refined:
- ...

Current agent: {current}
Hook event: {event_name}
Current working directory: {cwd}
Active model: {model}

Original prompt:
{clipped_prompt}

Recent redacted transcript excerpt:
{excerpt}
""".strip()


def hook_output(current: str, event_name: str, context: str) -> dict[str, Any]:
    system_message = "Refinment context prepared."
    if current == "gemini" or event_name == "BeforeAgent":
        return {
            "systemMessage": system_message,
            "hookSpecificOutput": {
                "hookEventName": "BeforeAgent",
                "additionalContext": context,
            },
        }
    return {
        "systemMessage": system_message,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["claude", "codex", "gemini"], required=True)
    args = parser.parse_args()

    data = load_input()
    prompt = prompt_from_hook(data)
    if not enabled() or should_skip(prompt) or not should_activate(prompt):
        print("{}")
        return 0

    context = build_context(args.current, data, prompt)
    print(json.dumps(hook_output(args.current, str(data.get("hook_event_name", "")), context), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
