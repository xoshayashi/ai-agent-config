#!/usr/bin/env python3
"""Subprocess-based self-check hook for Codex, Claude Code, Gemini CLI, and Copilot CLI.

The advisor runs only at *post-work* hook events (Stop / SubagentStop /
AfterAgent). It reviews the main session's latest response and either returns
a concrete next-step instruction or `STATUS: complete` to stop.

Pre-work hook events (UserPromptSubmit / SessionStart / BeforeAgent) are
intentionally NOT supported: empirically those calls returned no usable output
~85% of the time while still imposing visible latency on every prompt
submission. The main session is fully capable of deciding the first step on
its own; the advisor adds value only as a post-execution review.

Design:
- No phase state machine. The main session decides shape; the subprocess
  decides whether more work is needed after it stops.
- Skill activation (refinment, brainstorming, etc.) happens inside the
  subprocess via each skill's own activation conditions.
- Python keeps only: a lightweight gate, a per-task call counter, a recursion
  guard, a timeout, an audit log, and an off switch.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Supported events per CLI ─────────────────────────────────────────────────

SUPPORTED_EVENTS: dict[str, set[str]] = {
    "codex":   {"Stop"},
    "claude":  {"Stop", "SubagentStop"},
    "gemini":  {"AfterAgent"},
    "copilot": {"Stop"},
}

# ── Subprocess command per CLI ───────────────────────────────────────────────
#
# `prompt_via` controls how the prompt reaches the child:
#   "stdin": passed via stdin (Codex, Claude Code)
#   "argv":  passed as the last positional argument (Gemini, Copilot)

SUBPROCESS_COMMANDS: dict[str, dict[str, Any]] = {
    "codex":   {"argv": ["codex", "exec", "--json", "-"], "prompt_via": "stdin"},
    "claude":  {"argv": ["claude", "-p", "--output-format", "json"], "prompt_via": "stdin"},
    "gemini":  {"argv": ["gemini", "-p"], "prompt_via": "argv"},
    "copilot": {"argv": ["copilot", "-p", "-s", "--no-ask-user"], "prompt_via": "argv"},
}

# ── Defaults (overridable via env) ───────────────────────────────────────────

DEFAULT_MAX_CALLS = 8
DEFAULT_TIMEOUT_SEC = 180
DEFAULT_MIN_OUTPUT_CHARS = 200
DEFAULT_PROMPT_BODY_CHARS = 8000

COMPLETE_MARKER = "STATUS: complete"
EARLY_EXIT_PATTERN = re.compile(r"(?m)^\s*\[\[TASK_DONE\]\]\s*$")
ANSWER_ONLY_NEGATIVE_PATTERN = re.compile(
    r"(```|^\s*[+\-]\s+|変更|追加|修正|削除|実行|完了|"
    r"\bedit\b|\bcreated\b|\bdeleted\b|\bupdated\b|\bran\b|\bpushed\b|\bcommitted\b)",
    re.IGNORECASE | re.MULTILINE,
)

# ── Small helpers ────────────────────────────────────────────────────────────

def env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    raw = os.environ.get(name, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        value = default
    if minimum is not None and value < minimum:
        value = minimum
    if maximum is not None and value > maximum:
        value = maximum
    return value


def max_calls() -> int:
    return env_int("AI_AGENT_SUBPROCESS_CHECK_MAX", DEFAULT_MAX_CALLS, minimum=1, maximum=64)


def timeout_sec() -> int:
    return env_int("AI_AGENT_SUBPROCESS_CHECK_TIMEOUT", DEFAULT_TIMEOUT_SEC, minimum=10, maximum=900)


def min_output_chars() -> int:
    return env_int("AI_AGENT_SUBPROCESS_CHECK_MIN_OUTPUT", DEFAULT_MIN_OUTPUT_CHARS, minimum=0, maximum=10000)


def is_disabled() -> bool:
    return os.environ.get("AI_AGENT_SUBPROCESS_CHECK", "1").strip() == "0"


# ── State and audit log ──────────────────────────────────────────────────────

def state_root() -> Path:
    base = os.environ.get("AI_AGENT_STATE_DIR") or os.path.expanduser("~/.ai-agent-config")
    return Path(os.path.expanduser(base)).resolve() / "subprocess-check"


def state_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id) or "default"
    return state_root() / f"{safe}.json"


def decision_log_path() -> Path:
    return state_root() / "decisions.jsonl"


def load_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


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


def log_decision(session_id: str, event: str, kind: str, detail: str) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": session_id,
        "event": event,
        "kind": kind,
        "detail": detail[:500],
    }
    path = decision_log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ── Input parsing ────────────────────────────────────────────────────────────

def load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def session_id_from(data: dict[str, Any]) -> str:
    value = data.get("session_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "default"


def response_from(data: dict[str, Any]) -> str:
    for key in ("prompt_response", "last_assistant_message", "response"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def clip(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[-limit:]


# ── Recursion / skip guard ───────────────────────────────────────────────────

def is_recursive_subprocess() -> bool:
    return os.environ.get("AI_AGENT_SELF_WORKFLOW_ACTIVE") == "1"


def should_skip_event(current: str, data: dict[str, Any]) -> bool:
    if is_recursive_subprocess():
        return True
    event_name = str(data.get("hook_event_name", ""))
    if event_name not in SUPPORTED_EVENTS.get(current, set()):
        return True
    return False


# ── Lightweight gate ─────────────────────────────────────────────────────────

def looks_like_answer_only(text: str) -> bool:
    """Heuristic: True when the response is a plain answer with no execution markers.

    Used to skip subprocess for trivial Q&A turns. Conservative: false positives
    are cheap (one extra subprocess), false negatives waste a subprocess call.
    """
    return ANSWER_ONLY_NEGATIVE_PATTERN.search(text) is None


def should_skip_subprocess(state: dict[str, Any], event: str, response: str) -> tuple[bool, str]:
    """Return (skip, reason).

    All supported events are post-work (Stop / SubagentStop / AfterAgent),
    so the gate always applies the response-based filters.
    """
    if is_disabled():
        return True, "AI_AGENT_SUBPROCESS_CHECK=0"

    if state.get("completed"):
        return True, "task already marked complete"

    used = int(state.get("calls_used", 0) or 0)
    if used >= max_calls():
        return True, f"hard cap {max_calls()} reached"

    if EARLY_EXIT_PATTERN.search(response):
        return True, "[[TASK_DONE]] shortcut from main session"
    if len(response.strip()) < min_output_chars():
        return True, "response shorter than min_output threshold"
    if looks_like_answer_only(response):
        return True, "looks like an answer-only turn"

    return False, ""


# ── Subprocess invocation ────────────────────────────────────────────────────

def build_subprocess_prompt(event: str, response: str) -> str:
    intent = {
        "Stop": (
            "Read the main session's latest response and decide the smallest next "
            "concrete step. If the task is fully complete, reply with "
            f"`{COMPLETE_MARKER}` on the first line."
        ),
        "SubagentStop": (
            "A subagent finished. Decide the smallest next concrete step the main "
            f"session should take, or reply with `{COMPLETE_MARKER}` if nothing remains."
        ),
        "AfterAgent": (
            "An agent turn finished. Decide the smallest next concrete step, or "
            f"reply with `{COMPLETE_MARKER}` if the task is complete."
        ),
    }.get(event, "Decide the smallest next concrete step or signal completion.")

    body = [
        "You are the same-CLI advisor for the main session. Read the context below "
        "and reply with one of:",
        f"  - `{COMPLETE_MARKER}` on the first line (the task is done; no further work).",
        "  - One to three sentences describing the next concrete step the main session "
        "    should take. Be specific about file paths or commands when relevant. "
        "    Do not paste large file contents back. Do not push any specific skill; "
        "    let the main session decide which skills to use.",
        "",
        f"Event: {event}",
        f"Intent: {intent}",
        "",
        "Most recent main-session response:",
        clip(response or "(empty)", DEFAULT_PROMPT_BODY_CHARS),
    ]
    return "\n".join(body)


def call_subprocess(current: str, prompt: str) -> str | None:
    """Run the same CLI in non-interactive mode and return its raw stdout, or None on failure."""
    spec = SUBPROCESS_COMMANDS.get(current)
    if not spec:
        return None
    argv = list(spec["argv"])
    if shutil.which(argv[0]) is None:
        return None

    env = os.environ.copy()
    env["AI_AGENT_SELF_WORKFLOW_ACTIVE"] = "1"

    try:
        if spec["prompt_via"] == "stdin":
            result = subprocess.run(
                argv,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout_sec(),
                env=env,
            )
        else:
            result = subprocess.run(
                argv + [prompt],
                capture_output=True,
                text=True,
                timeout=timeout_sec(),
                env=env,
            )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None

    if result.returncode != 0:
        return None
    return result.stdout


def parse_subprocess_output(current: str, raw: str | None) -> tuple[str, str]:
    """Return (kind, text) where kind is one of: 'complete', 'instruction', 'empty'."""
    if not raw or not raw.strip():
        return "empty", ""

    stripped = raw.strip()
    looks_like_json = stripped.startswith("{") or stripped.startswith("[")

    text: str | None = None

    # CLIs that emit machine-readable output: try to parse. If the input *looks*
    # like JSON but parsing fails to find assistant text, treat as 'empty'
    # rather than leaking raw JSON into the continuation. Plain text passes
    # through as-is (some CLIs/configurations may emit plain text).
    if current == "codex":
        text = extract_text_from_codex_jsonl(raw)
        if text is None and not looks_like_json:
            text = stripped
    elif current == "claude":
        text = extract_text_from_claude_json(raw)
        if text is None and not looks_like_json:
            text = stripped
    else:
        text = stripped

    if not text:
        return "empty", ""

    text = text.strip()
    if not text:
        return "empty", ""

    first_line = text.splitlines()[0].strip()
    if first_line == COMPLETE_MARKER:
        return "complete", text
    return "instruction", text


def extract_text_from_codex_jsonl(raw: str) -> str | None:
    """Best-effort extraction of assistant text from `codex exec --json` output."""
    chunks: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        # Common shapes: {"type":"message","content":[{"type":"text","text":"..."}]}
        content = parsed.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_value = item.get("text")
                    if isinstance(text_value, str):
                        chunks.append(text_value)
        elif isinstance(parsed.get("message"), str):
            chunks.append(parsed["message"])
        elif isinstance(parsed.get("text"), str):
            chunks.append(parsed["text"])
    return "\n".join(chunk for chunk in chunks if chunk.strip()).strip() or None


def extract_text_from_claude_json(raw: str) -> str | None:
    """Best-effort extraction from `claude -p --output-format json` output.

    Handles both formats produced by recent Claude Code releases:
      - Single-object: {"result": "...", "session_id": "...", ...}
      - Array of stream events: [{"type":"system",...}, {"type":"assistant",...},
                                  {"type":"result","result":"..."}]
    """
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None

    # Single-object envelope
    if isinstance(parsed, dict):
        for key in ("result", "response", "message", "text"):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return None

    # Array of stream events: prefer the final `result` event, then assistant text.
    if isinstance(parsed, list):
        for entry in reversed(parsed):
            if not isinstance(entry, dict):
                continue
            if entry.get("type") == "result":
                value = entry.get("result")
                if isinstance(value, str) and value.strip():
                    return value
        chunks: list[str] = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            if entry.get("type") != "assistant":
                continue
            message = entry.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_value = item.get("text")
                        if isinstance(text_value, str):
                            chunks.append(text_value)
        joined = "\n".join(chunk for chunk in chunks if chunk.strip()).strip()
        return joined or None

    return None


# ── Output adapters per CLI ──────────────────────────────────────────────────

def stop_continuation_output(current: str, instruction: str, note: str) -> dict[str, Any]:
    if current == "gemini":
        payload: dict[str, Any] = {"decision": "deny", "reason": instruction}
    else:
        payload = {"decision": "block", "reason": instruction}
    if note:
        payload["systemMessage"] = f"subprocess-check: {note}"
    return payload


# ── Event dispatch ───────────────────────────────────────────────────────────

def handle_event(current: str, data: dict[str, Any]) -> dict[str, Any]:
    event = str(data.get("hook_event_name", ""))
    session_id = session_id_from(data)
    path = state_path(session_id)
    state = load_state(path)

    response = response_from(data)

    skip, reason = should_skip_subprocess(state, event, response)
    if skip:
        log_decision(session_id, event, "skip", reason)
        if state:
            save_state(path, state)
        return {}

    advisor_prompt = build_subprocess_prompt(event, response)
    raw = call_subprocess(current, advisor_prompt)
    state["calls_used"] = int(state.get("calls_used", 0) or 0) + 1
    state.setdefault("completed", False)

    kind, text = parse_subprocess_output(current, raw)

    if kind == "empty":
        save_state(path, state)
        log_decision(session_id, event, "empty", "")
        # Silent on empty: surfacing a warning here only adds noise to the
        # main session after a wasted advisor call. The audit log keeps the
        # record for debugging.
        return {}

    if kind == "complete":
        state["completed"] = True
        save_state(path, state)
        log_decision(session_id, event, "complete", text[:200])
        return {"systemMessage": "subprocess-check: advisor reports task complete."}

    save_state(path, state)
    log_decision(session_id, event, "instruction", text[:200])

    return stop_continuation_output(current, text, f"continuation #{state['calls_used']}")


# ── Entrypoint ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=list(SUPPORTED_EVENTS.keys()), required=True)
    args = parser.parse_args()

    data = load_input()
    if should_skip_event(args.current, data):
        print("{}")
        return 0

    output = handle_event(args.current, data)
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
