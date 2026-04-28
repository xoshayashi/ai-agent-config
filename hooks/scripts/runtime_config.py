#!/usr/bin/env python3
"""Shared runtime state-config helpers for hook scripts."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path


ALLOWED_KEYS = {
    "AI_AGENT_STATE_DIR",
    "AI_AGENT_STATE_FILE",
}

UNQUOTED_SAFE = re.compile(r"^[A-Za-z0-9_./:@%+=,~-]*$")
ASSIGNMENT = re.compile(r"^([A-Z0-9_]+)=(.*)$")


def expand_home(value: str) -> str:
    if value == "~":
        return os.path.expanduser("~")
    if value.startswith("~/"):
        return os.path.join(os.path.expanduser("~"), value[2:])
    return value


def parse_single_quoted(expr: str) -> str:
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
        inner = value[1:-1]
        if re.search(r'(?<!\\)"', inner):
            raise ValueError("unescaped double quote in double-quoted value")
        return inner.replace(r"\\", "\\").replace(r"\"", '"')
    if not UNQUOTED_SAFE.fullmatch(value):
        raise ValueError("unsafe unquoted value")
    return value


def default_state_file() -> Path:
    state_dir = expand_home(os.environ.get("AI_AGENT_STATE_DIR", "~/.llm-config"))
    state_file = os.environ.get("AI_AGENT_STATE_FILE", "").strip()
    if state_file:
        return Path(expand_home(state_file)).resolve()
    return (Path(state_dir).expanduser().resolve() / "config.env")


@lru_cache(maxsize=1)
def load_state_config() -> dict[str, str]:
    path = default_state_file()
    if not path.is_file():
        return {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    parsed: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = ASSIGNMENT.match(stripped)
        if not match:
            continue
        key, raw_value = match.group(1), match.group(2)
        if key not in ALLOWED_KEYS:
            continue
        try:
            parsed[key] = parse_value(raw_value)
        except ValueError:
            continue
    return parsed


def flag_value(name: str, default: str = "0") -> str:
    if name in os.environ:
        return os.environ.get(name, default)
    return load_state_config().get(name, default)


def flag_enabled(name: str, default: bool = False) -> bool:
    fallback = "1" if default else "0"
    return flag_value(name, fallback) == "1"
