#!/usr/bin/env python3
"""Safely parse llm-config state env files without shell evaluation."""

from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path


ALLOWED_KEYS = {
    "AI_AGENT_CONFIG_HOME",
    "AI_AGENT_CODEX_HOME",
    "AI_AGENT_CLAUDE_HOME",
    "AI_AGENT_GEMINI_HOME",
    "AI_AGENT_COPILOT_HOME",
    "AI_AGENT_SKILLS_DIR",
    "AI_AGENT_EXTRA_SKILLS_DIRS",
    "AI_AGENT_INSTALL_INSTRUCTIONS",
    "AI_AGENT_INSTALL_SKILLS",
    "AI_AGENT_INSTALL_HOOKS",
    "AI_AGENT_HOOKS_RUNTIME_LINK",
    "AI_AGENT_CONFLICT_MODE",
    "AI_AGENT_REQUIRE_LLM_CLIS",
    "AI_AGENT_STATE_DIR",
    "AI_AGENT_STATE_FILE",
}


UNQUOTED_SAFE = re.compile(r"^[A-Za-z0-9_./:@%+=,~-]*$")
ASSIGNMENT = re.compile(r"^([A-Z0-9_]+)=(.*)$")


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def parse_single_quoted(expr: str) -> str:
    """Parse shell-safe single-quoted concatenation with escaped single quotes.

    Accepts values produced by setup.sh quote_sh, e.g.:
    'abc'\''def'
    """

    out: list[str] = []
    index = 0
    length = len(expr)
    while index < length:
        char = expr[index]
        if char == "'":
            end = expr.find("'", index + 1)
            if end == -1:
                raise ValueError("unterminated single-quoted value")
            out.append(expr[index + 1 : end])
            index = end + 1
            continue
        if expr.startswith("\\'", index):
            out.append("'")
            index += 2
            continue
        raise ValueError("invalid single-quoted token sequence")
    return "".join(out)


def parse_value(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""

    if value.startswith("'"):
        return parse_single_quoted(value)

    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        # setup.sh always writes single-quoted values via quote_sh, so this
        # branch only exists for forward-compatible reading of simple files.
        # Keep it intentionally strict: support plain double-quoted strings
        # with only \" and \\ escapes, and reject any other raw quote usage.
        inner = value[1:-1]
        if re.search(r'(?<!\\)"', inner):
            raise ValueError("unescaped double quote in double-quoted value")
        inner = inner.replace(r"\\", "\\").replace(r"\"", '"')
        return inner

    if not UNQUOTED_SAFE.fullmatch(value):
        raise ValueError("unsafe unquoted value")
    return value


def validate_permissions(path: Path) -> None:
    info = path.stat()
    if info.st_uid != os.getuid():
        raise PermissionError("state file owner mismatch")
    mode = stat.S_IMODE(info.st_mode)
    if mode & 0o022:
        raise PermissionError("state file must not be group/world writable")


def main() -> int:
    if len(sys.argv) != 2:
        return fail("usage: read-state-config.py <config.env>")

    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.is_file():
        return fail(f"state file not found: {path}")

    try:
        validate_permissions(path)
    except PermissionError as exc:
        return fail(f"{exc}: {path}")
    except OSError as exc:
        return fail(f"cannot stat state file: {exc}")

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return fail(f"cannot read state file: {exc}")

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = ASSIGNMENT.match(stripped)
        if not match:
            return fail(f"invalid line {lineno}: expected KEY=VALUE")
        key, raw_value = match.group(1), match.group(2)
        if key not in ALLOWED_KEYS:
            # Ignore unknown keys to stay forward-compatible with benign
            # extensions, while preserving a tight allowlist for consumption.
            continue
        try:
            value = parse_value(raw_value)
        except ValueError as exc:
            return fail(f"invalid value for {key} at line {lineno}: {exc}")
        # Tab-delimited key/value pairs for POSIX-shell parsing without eval.
        print(f"{key}\t{value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
