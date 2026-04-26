#!/usr/bin/env python3
"""Merge llm-config hook registrations into existing CLI settings."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


MANAGED_BEGIN = "# BEGIN llm-config managed hooks"
MANAGED_END = "# END llm-config managed hooks"


def atomic_write(destination: Path, payload: str) -> None:
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=destination.name + ".", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp_path, destination)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def contains_managed_hook(value: Any) -> bool:
    """Heuristic: does this hook group originate from llm-config?

    Known limitation: this is a string-match heuristic, not a structural
    flag. A user-authored hook whose command happens to contain one of the
    sentinel substrings (most commonly ``llm-config/hooks`` or
    ``AI_AGENT_HOOKS_RUNTIME_LINK`` because it wraps or extends a managed
    hook) will be classified as managed. If such a user-authored group does
    not match any source group exactly, the next ``setup.sh`` merge will
    treat it as stale and remove it.

    A long-term fix would be to add an explicit ``_llm-config-managed: true``
    marker on every managed hook group and check that first. That is a
    multi-file schema change touching every hook config, so it is left as a
    follow-up. Until then, do NOT name personal hook commands with these
    sentinels if you want them to survive automated merges.
    """
    if isinstance(value, str):
        return (
            "AI_AGENT_HOOKS_RUNTIME_LINK" in value
            or "llm-config/hooks" in value
            or "peer_prompt_refinement.py" in value
            or "safe_delete_guard.py" in value
        )
    if isinstance(value, list):
        return any(contains_managed_hook(item) for item in value)
    if isinstance(value, dict):
        return any(contains_managed_hook(item) for item in value.values())
    return False


def merge_hooks_json(source: Path, destination: Path) -> tuple[dict[str, Any], bool]:
    source_data = load_json(source)
    destination_data = load_json(destination)
    source_hooks = source_data.get("hooks", {})
    if not isinstance(source_hooks, dict):
        raise ValueError(f"source hooks must be an object: {source}")

    destination_hooks = destination_data.setdefault("hooks", {})
    if not isinstance(destination_hooks, dict):
        raise ValueError(f"destination hooks must be an object: {destination}")

    changed = False

    # Visit every event present in either side so that stale managed hooks
    # under events the source no longer declares are also cleaned up.
    event_names = list(source_hooks.keys()) + [
        name for name in destination_hooks.keys() if name not in source_hooks
    ]

    for event_name in event_names:
        source_groups = source_hooks.get(event_name, [])
        if not isinstance(source_groups, list):
            raise ValueError(f"source hook event must be a list: {event_name}")
        if event_name in source_hooks:
            destination_groups = destination_hooks.setdefault(event_name, [])
        else:
            destination_groups = destination_hooks.get(event_name, [])
        if not isinstance(destination_groups, list):
            raise ValueError(f"destination hook event must be a list: {event_name}")

        source_keys = {canonical(group) for group in source_groups}
        cleaned_groups = []
        for group in destination_groups:
            key = canonical(group)
            if contains_managed_hook(group) and key not in source_keys:
                changed = True
                continue
            cleaned_groups.append(group)
        if len(cleaned_groups) != len(destination_groups):
            destination_hooks[event_name] = cleaned_groups
            destination_groups = cleaned_groups

        existing = {canonical(group) for group in destination_groups}
        for group in source_groups:
            key = canonical(group)
            if key in existing:
                continue
            destination_groups.append(group)
            existing.add(key)
            changed = True

        if not destination_groups and not source_groups:
            destination_hooks.pop(event_name, None)

    if changed and not destination_hooks:
        destination_data.pop("hooks", None)

    return destination_data, changed


def remove_hooks_json(source: Path, destination: Path) -> tuple[dict[str, Any], bool]:
    source_data = load_json(source)
    destination_data = load_json(destination)
    source_hooks = source_data.get("hooks", {})
    destination_hooks = destination_data.get("hooks", {})
    if not isinstance(source_hooks, dict) or not isinstance(destination_hooks, dict):
        return destination_data, False

    changed = False
    # Iterate destination events, not only source events. This guarantees
    # uninstall can remove managed hooks from legacy events even after newer
    # releases stop declaring those events in source hook config.
    for event_name, destination_groups in list(destination_hooks.items()):
        source_groups = source_hooks.get(event_name, [])
        if not isinstance(source_groups, list):
            source_groups = []
        destination_groups = destination_hooks.get(event_name)
        if not isinstance(destination_groups, list):
            continue
        source_keys = {canonical(group) for group in source_groups}
        kept = [
            group
            for group in destination_groups
            if canonical(group) not in source_keys and not contains_managed_hook(group)
        ]
        if len(kept) != len(destination_groups):
            changed = True
            if kept:
                destination_hooks[event_name] = kept
            else:
                destination_hooks.pop(event_name, None)

    if changed and not destination_hooks:
        destination_data.pop("hooks", None)
    return destination_data, changed


def merge_json_file(source: Path, destination: Path, dry_run: bool) -> bool:
    merged, changed = merge_hooks_json(source, destination)
    if changed and not dry_run:
        payload = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
        atomic_write(destination, payload)
    return changed


def remove_json_file(source: Path, destination: Path, dry_run: bool) -> bool:
    merged, changed = remove_hooks_json(source, destination)
    if changed and not dry_run:
        payload = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
        atomic_write(destination, payload)
    return changed


def merge_codex_config(_source: Path, destination: Path, dry_run: bool) -> bool:
    if destination.exists():
        lines = destination.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    changed = False
    in_features = False
    features_start = None
    insert_at = None
    codex_line = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_features and insert_at is None:
                insert_at = index
            in_features = stripped == "[features]"
            if in_features:
                features_start = index
            continue
        if in_features:
            if stripped.startswith("codex_hooks"):
                codex_line = index
            insert_at = index + 1

    if codex_line is not None:
        if lines[codex_line].strip() == "codex_hooks = true":
            return False
        previous = lines[codex_line].strip()
        previous_marker = f"# llm-config managed hooks previous: {previous}"
        if codex_line == 0 or not lines[codex_line - 1].strip().startswith("# llm-config managed hooks previous:"):
            lines.insert(codex_line, previous_marker)
            codex_line += 1
        lines[codex_line] = "codex_hooks = true"
        changed = True
    elif features_start is not None:
        if insert_at is None:
            insert_at = features_start + 1
        lines.insert(insert_at, "# llm-config managed hooks")
        lines.insert(insert_at + 1, "codex_hooks = true")
        changed = True
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([MANAGED_BEGIN, "[features]", "codex_hooks = true", MANAGED_END])
        changed = True

    if changed and not dry_run:
        atomic_write(destination, "\n".join(lines) + "\n")
    return changed


def remove_codex_config(_source: Path, destination: Path, dry_run: bool) -> bool:
    if not destination.exists():
        return False
    lines = destination.read_text(encoding="utf-8").splitlines()
    changed = False
    result: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() == MANAGED_BEGIN:
            begin_index = index
            scan = index + 1
            while scan < len(lines) and lines[scan].strip() != MANAGED_END:
                scan += 1
            if scan >= len(lines):
                # MANAGED_END is missing — preserve the orphaned block as-is
                # so the user can recover instead of silently losing content.
                result.extend(lines[begin_index:])
                index = len(lines)
                continue
            # Skip from MANAGED_BEGIN through MANAGED_END inclusive.
            index = scan + 1
            changed = True
            continue
        if line.strip() == "# llm-config managed hooks":
            next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if next_line.startswith("codex_hooks"):
                index += 2
                changed = True
                continue
        if line.strip().startswith("# llm-config managed hooks previous:"):
            previous = line.split("previous:", 1)[1].strip()
            next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if next_line.startswith("codex_hooks"):
                result.append(previous)
                index += 2
                changed = True
                continue
        result.append(line)
        index += 1

    if changed and not dry_run:
        atomic_write(destination, "\n".join(result).rstrip() + "\n")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["json", "codex-config"])
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    destination = Path(args.destination)

    if args.kind == "json" and args.remove:
        changed = remove_json_file(source, destination, args.dry_run)
    elif args.kind == "json":
        changed = merge_json_file(source, destination, args.dry_run)
    elif args.remove:
        changed = remove_codex_config(source, destination, args.dry_run)
    else:
        changed = merge_codex_config(source, destination, args.dry_run)

    verb = "remove" if args.remove else "append"
    action = f"would {verb}" if args.dry_run and changed else verb
    if not changed:
        action = "already present"
        if args.remove:
            action = "already absent"
    print(f"{action}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
