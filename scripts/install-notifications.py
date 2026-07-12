#!/usr/bin/env python3
"""Install or remove the shared notification hook in each CLI's config.

Claude Code, Codex, and Gemini CLI each run shell commands on lifecycle
events ("hooks"). This helper wires the repo's notifications/notify.sh into
those configs so a desktop notification fires when an agent finishes a turn
or needs attention.

All three target files are JSON, so they are merged in place rather than
symlinked: the CLI config files hold unrelated user settings that must be
preserved. The merge is idempotent and reversible — managed entries are
identified by the notify.sh path inside their command string.
"""

import argparse
import datetime as _dt
import difflib
import json
import os
import shlex
import sys
from pathlib import Path

# Path fragment that marks a hook entry as managed by this repo.
MANAGED_MARKER = "/notifications/notify.sh"

# Per-CLI wiring. Each event maps to a notification category understood by
# notify.sh ("done" = turn complete, "attention" = needs input/approval).
CLI_CONFIG = {
    "claude": {
        "label": "Claude Code",
        "config_file": "settings.json",
        "events": {"Stop": "done", "Notification": "attention"},
    },
    "codex": {
        "label": "Codex",
        "config_file": "hooks.json",
        "events": {"Stop": "done", "PermissionRequest": "attention"},
    },
}


def build_command(notify_script: Path, label: str, category: str) -> str:
    """Build the hook command string for one event."""
    return "sh {} {} {}".format(
        shlex.quote(str(notify_script)),
        shlex.quote(label),
        shlex.quote(category),
    )


def is_managed_group(group: dict) -> bool:
    """True when a matcher group was created by this repo."""
    if not isinstance(group, dict):
        return False
    for hook in group.get("hooks", []):
        if isinstance(hook, dict) and MANAGED_MARKER in str(hook.get("command", "")):
            return True
    return False


def strip_managed(hooks_obj: dict) -> dict:
    """Return a copy of a hooks object with all managed groups removed."""
    cleaned = {}
    for event, groups in hooks_obj.items():
        if not isinstance(groups, list):
            cleaned[event] = groups
            continue
        kept = [g for g in groups if not is_managed_group(g)]
        if kept:
            cleaned[event] = kept
    return cleaned


def desired_config(cli: str, notify_script: Path, existing: dict) -> dict:
    """Compute the target config for one CLI without mutating the input."""
    config = json.loads(json.dumps(existing))  # deep copy
    hooks_obj = config.get("hooks")
    hooks_obj = strip_managed(hooks_obj) if isinstance(hooks_obj, dict) else {}

    spec = CLI_CONFIG[cli]
    for event, category in spec["events"].items():
        command = build_command(notify_script, spec["label"], category)
        group = {"hooks": [{"type": "command", "command": command}]}
        hooks_obj.setdefault(event, []).append(group)

    if hooks_obj:
        config["hooks"] = hooks_obj
    else:
        config.pop("hooks", None)
    return config


def removed_config(existing: dict) -> dict:
    """Compute the config after removing managed entries only."""
    config = json.loads(json.dumps(existing))
    hooks_obj = config.get("hooks")
    if not isinstance(hooks_obj, dict):
        return config
    hooks_obj = strip_managed(hooks_obj)
    if hooks_obj:
        config["hooks"] = hooks_obj
    else:
        config.pop("hooks", None)
    return config


def load_json(path: Path):
    """Return (data, error). Missing file yields an empty object."""
    if not path.exists():
        return {}, None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, "cannot read {}: {}".format(path, exc)
    if not text.strip():
        return {}, None
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, "invalid JSON in {}: {}".format(path, exc)


def dump_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def apply_to_cli(cli: str, target: Path, notify_script: Path, mode: str, dry_run: bool) -> int:
    """Apply install/uninstall to one CLI. Return 0 on success, 1 on error."""
    if mode == "uninstall" and not target.exists():
        # Nothing was installed here; never create a file just to uninstall.
        print("{}: not present ({})".format(cli, target))
        return 0

    existing, error = load_json(target)
    if error is not None:
        print("error: {}".format(error), file=sys.stderr)
        return 1

    if mode == "install":
        updated = desired_config(cli, notify_script, existing)
    else:
        updated = removed_config(existing)

    old_text = dump_json(existing) if target.exists() else ""
    new_text = dump_json(updated)
    events = ", ".join(CLI_CONFIG[cli]["events"])

    if old_text == new_text:
        print("{}: unchanged ({})".format(cli, target))
        return 0

    if dry_run:
        print("{}: would update {} [{}]".format(cli, target, events))
        diff = difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile="{} (current)".format(target.name),
            tofile="{} (proposed)".format(target.name),
        )
        sys.stdout.writelines(diff)
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name("{}.bak-{}".format(target.name, stamp))
        suffix = 1
        while backup.exists():
            backup = target.with_name("{}.bak-{}.{}".format(target.name, stamp, suffix))
            suffix += 1
        try:
            backup.write_text(old_text, encoding="utf-8")
        except OSError as exc:
            print("error: cannot write backup {}: {}".format(backup, exc), file=sys.stderr)
            return 1
        print("{}: backup {}".format(cli, backup))

    # Write to a sibling temp file and rename, so an interrupted run never
    # leaves a partially written config behind.
    tmp = target.with_name(target.name + ".tmp")
    try:
        tmp.write_text(new_text, encoding="utf-8")
        os.replace(tmp, target)
    except OSError as exc:
        print("error: cannot write {}: {}".format(target, exc), file=sys.stderr)
        try:
            tmp.unlink()
        except OSError:
            pass
        return 1

    verb = "installed" if mode == "install" else "removed"
    print("{}: notification hook {} ({}) [{}]".format(cli, verb, target, events))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["install", "uninstall"], required=True)
    parser.add_argument("--config-home", required=True,
                        help="repository root holding notifications/notify.sh")
    parser.add_argument("--claude-home", required=True)
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    notify_script = Path(args.config_home).expanduser().resolve() / "notifications" / "notify.sh"
    if args.mode == "install" and not notify_script.exists():
        print("error: notify script not found: {}".format(notify_script), file=sys.stderr)
        return 1

    homes = {
        "claude": Path(args.claude_home).expanduser(),
        "codex": Path(args.codex_home).expanduser(),
    }

    status = 0
    for cli, home in homes.items():
        target = home / CLI_CONFIG[cli]["config_file"]
        status |= apply_to_cli(cli, target, notify_script, args.mode, args.dry_run)
    return status


if __name__ == "__main__":
    sys.exit(main())
