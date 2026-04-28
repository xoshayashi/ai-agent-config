#!/usr/bin/env python3
"""Route Codex hook events through the managed Codex orchestrator."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def load_input() -> tuple[str, dict[str, object]]:
    raw = sys.stdin.read()
    if not raw.strip():
        return "{}", {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw, {}
    if not isinstance(parsed, dict):
        return raw, {}
    return raw, parsed


def script_path(name: str) -> str:
    return str((Path(__file__).resolve().parent / name).resolve())


def run_script(raw_input: str, name: str) -> int:
    command = [sys.executable, script_path(name), "--current", "codex"]
    completed = subprocess.run(
        command,
        input=raw_input,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
        check=False,
    )
    stdout = completed.stdout.strip()
    if stdout:
        print(stdout)
    elif completed.returncode == 0:
        print("{}")
    if completed.returncode != 0 and completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", choices=["codex"], required=True)
    args = parser.parse_args()
    del args

    raw_input, data = load_input()
    event_name = str(data.get("hook_event_name", ""))
    if event_name in {"SessionStart", "UserPromptSubmit", "Stop"}:
        return run_script(raw_input, "multillm_orchestrator.py")

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
