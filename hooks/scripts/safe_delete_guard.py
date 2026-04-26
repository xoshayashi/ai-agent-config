#!/usr/bin/env python3
"""Block permanent shell deletion commands in supported LLM CLI hooks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


# Match `rm` invoked at the start of a command, after a separator, or after
# whitespace, with an optional absolute path prefix (any directory ending in
# `/`). This deliberately covers `/bin/rm`, `/usr/bin/rm`, `/usr/local/bin/rm`,
# `/opt/homebrew/bin/rm`, and bare `rm`.
#
# Known false positives (accepted as fail-safe):
#   - `echo rm -rf /tmp` — the literal string `rm` appears as an argument.
#     The guard cannot distinguish "echo rm" from "execute rm" without a
#     full shell parser, so it errs on the side of blocking.
#   - `printf '%s' 'rm -rf /tmp'`, `cat | grep rm`, etc. — same class.
#
# Known false negatives (accepted; supplementary by design):
#   - `\rm`, `'rm'`, `"rm"` — alias-bypass forms.
#   - `command rm`, `env rm`, `exec rm` — wrapped invocations.
#   - Scripts or shell functions that internally call `rm`.
#   - User-defined aliases that ultimately resolve to `rm`.
#
# This guard is a runtime guardrail, not a sandbox. The shared CLI-side
# instructions still require agents to use the trash workflow even when this
# hook is bypassed.
DELETE_PATTERN = re.compile(r"(^|[;&|()\s])((?:/\S+/)?rm)(\s|$)")


def load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def command_from_hook(data: dict[str, Any]) -> str:
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
        command = tool_input.get("cmd")
        if isinstance(command, str):
            return command
    return ""


def tool_name(data: dict[str, Any]) -> str:
    value = data.get("tool_name") or data.get("original_request_name") or ""
    return value if isinstance(value, str) else ""


def should_block(data: dict[str, Any]) -> bool:
    command = command_from_hook(data)
    if not command:
        return False

    name = tool_name(data).lower()
    shellish = (
        name in {"bash", "run_shell_command", "shell_command", "execute_shell"}
        or "shell" in name
        or "bash" in name
    )
    return shellish and DELETE_PATTERN.search(command) is not None


def block_output(current: str, event_name: str, reason: str) -> dict[str, Any]:
    if current == "gemini" or event_name == "BeforeTool":
        return {
            "decision": "deny",
            "reason": reason,
            "systemMessage": "Blocked permanent deletion command.",
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["claude", "codex", "gemini"], required=True)
    args = parser.parse_args()

    data = load_input()
    if not should_block(data):
        print("{}")
        return 0

    reason = (
        "Permanent shell deletion is blocked by shared LLM config. "
        "Use the safe trash workflow instead."
    )
    print(json.dumps(block_output(args.current, str(data.get("hook_event_name", "")), reason)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
