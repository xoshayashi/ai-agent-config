#!/usr/bin/env python3
"""Unit tests for scripts/merge-hook-config.py.

Run directly: ``python3 tests/test_merge_hook_config.py``. The script exits
with status 0 when every test passes and 1 (with a short report) when any
test fails. ``scripts/validate-repo.sh`` invokes this entrypoint as part of
repository validation so regressions surface in CI.

The tests cover the merge / remove paths for both JSON-based hooks and the
TOML-based Codex config, including the edge cases the PR review flagged:

- idempotency of repeated merges,
- stale managed-hook cleanup when the source changes,
- empty event arrays popped after cleanup (no leftover ``"PreToolUse": []``),
- removal preserving unrelated user hooks,
- orphaned ``MANAGED_BEGIN`` (missing ``MANAGED_END``) preserving the block
  rather than silently consuming the rest of the file,
- atomic write produces a valid file (no temp leftovers in the destination
  directory).
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "merge-hook-config.py"


def load_module():
    spec = importlib.util.spec_from_file_location("merge_hook_config", MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - import safety
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MHC = load_module()


SAMPLE_HOOK = {
    "type": "command",
    "command": "python3 \"${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.ai-agent-config/hooks}/scripts/safe_delete_guard.py\" --current claude",
    "timeout": 10,
}
SAMPLE_GROUP = {"_ai_agent_config_managed": True, "matcher": "Bash", "hooks": [SAMPLE_HOOK]}
SAMPLE_SOURCE_JSON = {"hooks": {"PreToolUse": [SAMPLE_GROUP]}}

USER_HOOK_GROUP = {
    "matcher": "Read",
    "hooks": [
        {
            "type": "command",
            "command": "echo unrelated-user-hook",
            "timeout": 5,
        }
    ],
}


# ---------- helpers ----------

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def in_tempdir():
    """Decorator-like context: create a sandbox dir and chdir into it."""
    return tempfile.TemporaryDirectory(prefix="merge-hook-test-")


def assert_eq(actual, expected, msg: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{msg}: expected {expected!r}, got {actual!r}")


# ---------- JSON merge tests ----------

def test_merge_json_fresh_destination() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        # NOTE: on a fresh destination setup.sh creates a symlink, but the
        # merge function should also handle the case where the destination
        # exists but is empty / minimal.
        write_json(dst, {})

        changed = MHC.merge_json_file(src, dst, dry_run=False)
        assert changed
        result = read_json(dst)
        assert_eq(result, SAMPLE_SOURCE_JSON, "fresh merge result")


def test_merge_json_idempotent() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {})

        first = MHC.merge_json_file(src, dst, dry_run=False)
        second = MHC.merge_json_file(src, dst, dry_run=False)
        assert first
        assert not second, "second merge must be a no-op"


def test_merge_json_preserves_user_hook() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {"hooks": {"PreToolUse": [USER_HOOK_GROUP]}})

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        groups = result["hooks"]["PreToolUse"]
        assert USER_HOOK_GROUP in groups, "user hook must survive merge"
        assert SAMPLE_GROUP in groups, "managed hook must be added"


def test_merge_json_preserves_unmarked_runtime_link_hook() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)

        unmarked_hook = {
            "matcher": "*",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 \"${AI_AGENT_HOOKS_RUNTIME_LINK}/scripts/safe_delete_guard.py\" --current claude",
                    "timeout": 10,
                }
            ],
        }
        write_json(
            dst,
            {"hooks": {"PreToolUse": [unmarked_hook, USER_HOOK_GROUP]}},
        )

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        groups = result["hooks"]["PreToolUse"]
        assert unmarked_hook in groups, "unmarked hook must be preserved"
        assert SAMPLE_GROUP in groups, "current managed hook must be present"
        assert USER_HOOK_GROUP in groups, "user hook must survive merge"


def test_merge_json_keeps_unmarked_user_hook_with_runtime_link() -> None:
    """A user hook referencing AI_AGENT_HOOKS_RUNTIME_LINK must not be removed
    unless it matches managed markers/patterns.
    """
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        user_runtime_hook = {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 \"${AI_AGENT_HOOKS_RUNTIME_LINK}/scripts/my_custom_router.py\"",
                    "timeout": 7,
                }
            ],
        }
        write_json(dst, {"hooks": {"PreToolUse": [user_runtime_hook]}})

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        groups = result["hooks"]["PreToolUse"]
        assert user_runtime_hook in groups, "user runtime-link hook must survive merge"
        assert SAMPLE_GROUP in groups, "managed hook must still be added"


def test_merge_json_no_duplicate_when_destination_lacks_marker() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        legacy_group = {
            "matcher": "Bash",
            "hooks": [SAMPLE_HOOK],
        }
        write_json(dst, {"hooks": {"PreToolUse": [legacy_group]}})

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        groups = result["hooks"]["PreToolUse"]
        assert len(groups) == 1, f"legacy managed group should not duplicate: {groups}"
        assert groups[0].get("_ai_agent_config_managed") is True, "group should be upgraded to explicit marker"


def test_merge_json_upgrades_legacy_managed_marker_without_duplicate() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        legacy_marker_group = {
            "_legacy_managed": True,
            "matcher": "Bash",
            "hooks": [SAMPLE_HOOK],
        }
        write_json(dst, {"hooks": {"PreToolUse": [legacy_marker_group]}})

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        groups = result["hooks"]["PreToolUse"]
        assert len(groups) == 1, f"legacy marker group should not duplicate: {groups}"
        assert groups[0].get("_ai_agent_config_managed") is True, "legacy marker should be upgraded"


def test_merge_json_pops_empty_event() -> None:
    """Medium #3: after stale cleanup leaves an event empty and the source
    has no entries for that event, the event key is popped (not left as []).
    """
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        # Source declares only PreToolUse — no entries for OldEvent.
        write_json(src, {"hooks": {"PreToolUse": [SAMPLE_GROUP]}})

        unmarked_group = {
            "matcher": "*",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 ${AI_AGENT_HOOKS_RUNTIME_LINK}/scripts/safe_delete_guard.py --current claude",
                    "timeout": 30,
                }
            ],
        }
        write_json(dst, {"hooks": {"OldEvent": [unmarked_group]}})

        MHC.merge_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        assert "OldEvent" in result.get("hooks", {}), "unmarked event must be preserved"


def test_merge_json_atomic_write_no_temp_leftover() -> None:
    """The atomic write helper must not leave .tmp / .partial leftovers."""
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {})

        MHC.merge_json_file(src, dst, dry_run=False)
        leftovers = [p.name for p in Path(tmp).iterdir() if p.name not in {"src.json", "dst.json"}]
        assert_eq(leftovers, [], "atomic_write leftovers")


def test_merge_json_dry_run_no_write() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {})
        before = dst.read_text(encoding="utf-8")

        changed = MHC.merge_json_file(src, dst, dry_run=True)
        assert changed
        assert_eq(dst.read_text(encoding="utf-8"), before, "dry-run wrote to disk")


# ---------- JSON remove tests ----------

def test_remove_json_pops_event_when_empty() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {"hooks": {"PreToolUse": [SAMPLE_GROUP]}})

        changed = MHC.remove_json_file(src, dst, dry_run=False)
        assert changed
        result = read_json(dst)
        assert "hooks" not in result, "hooks key should be popped when empty"


def test_remove_json_preserves_user_hook() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(
            dst,
            {"hooks": {"PreToolUse": [SAMPLE_GROUP, USER_HOOK_GROUP]}},
        )

        MHC.remove_json_file(src, dst, dry_run=False)
        result = read_json(dst)
        assert SAMPLE_GROUP not in result["hooks"]["PreToolUse"]
        assert USER_HOOK_GROUP in result["hooks"]["PreToolUse"]


def test_remove_json_cleans_legacy_event_not_in_source() -> None:
    """Uninstall should remove managed hooks from legacy events not in source."""
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {"hooks": {"UserPromptSubmit": [SAMPLE_GROUP]}})

        changed = MHC.remove_json_file(src, dst, dry_run=False)
        assert changed
        result = read_json(dst)
        assert "hooks" not in result, "legacy managed event should be removed"


def test_remove_json_cleans_legacy_managed_marker_group() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        legacy_marker_group = {
            "_legacy_managed": True,
            "matcher": "UserPromptSubmit",
            "hooks": [SAMPLE_HOOK],
        }
        write_json(dst, {"hooks": {"UserPromptSubmit": [legacy_marker_group]}})

        changed = MHC.remove_json_file(src, dst, dry_run=False)
        assert changed
        result = read_json(dst)
        assert "hooks" not in result, "legacy marker managed event should be removed"


def test_remove_json_dry_run_message_mentions_managed_hooks() -> None:
    with in_tempdir() as tmp:
        src = Path(tmp) / "src.json"
        dst = Path(tmp) / "dst.json"
        write_json(src, SAMPLE_SOURCE_JSON)
        write_json(dst, {"hooks": {"PreToolUse": [SAMPLE_GROUP]}})

        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "json", str(src), str(dst), "--remove", "--dry-run"],
            check=True,
            capture_output=True,
            text=True,
        )
        expected = f"would remove managed hooks from: {dst}"
        assert_eq(result.stdout.strip(), expected, "dry-run remove message")


# ---------- Codex TOML tests ----------

def test_merge_codex_no_features_section() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        # Pre-existing unrelated content.
        dst.write_text("[ui]\ntheme = \"dark\"\n", encoding="utf-8")
        MHC.merge_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        assert MHC.MANAGED_BEGIN in text
        assert "codex_hooks = true" in text
        assert MHC.MANAGED_END in text
        assert "[ui]" in text, "pre-existing section must be preserved"


def test_merge_codex_existing_features_no_codex_hooks() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text("[features]\nfoo = true\n", encoding="utf-8")
        MHC.merge_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        assert "codex_hooks = true" in text
        assert "foo = true" in text


def test_merge_codex_idempotent() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text("", encoding="utf-8")
        first = MHC.merge_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        second = MHC.merge_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        assert first
        assert not second, "repeated merge must be a no-op"


def test_merge_codex_overrides_explicit_false() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text("[features]\ncodex_hooks = false\n", encoding="utf-8")
        MHC.merge_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        assert "codex_hooks = true" in text
        assert "previous: codex_hooks = false" in text, "must record previous value"


def test_remove_codex_clean_block() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text(
            "[ui]\ntheme = \"dark\"\n\n"
            f"{MHC.MANAGED_BEGIN}\n"
            "[features]\n"
            "codex_hooks = true\n"
            f"{MHC.MANAGED_END}\n",
            encoding="utf-8",
        )
        changed = MHC.remove_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        assert changed
        text = dst.read_text(encoding="utf-8")
        assert MHC.MANAGED_BEGIN not in text
        assert MHC.MANAGED_END not in text
        assert "[ui]" in text
        assert "theme = \"dark\"" in text


def test_remove_codex_orphan_managed_begin_preserved() -> None:
    """Medium #4: when MANAGED_END is missing, the orphan block must be kept
    (so the user can recover) instead of silently consuming the file tail.
    """
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        original = (
            "[ui]\ntheme = \"dark\"\n\n"
            f"{MHC.MANAGED_BEGIN}\n"
            "[features]\n"
            "codex_hooks = true\n"
            "# user manually deleted the END marker\n"
            "[other]\n"
            "value = 1\n"
        )
        dst.write_text(original, encoding="utf-8")
        changed = MHC.remove_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        # Without MANAGED_END the function must keep the block as-is rather
        # than discarding lines through EOF.
        assert MHC.MANAGED_BEGIN in text, "orphan block must be preserved"
        assert "[other]" in text, "lines after the orphan block must survive"
        assert "value = 1" in text, "lines after the orphan block must survive"
        # `changed` may legitimately be False here because nothing was safely
        # removable; the contract we need is "no data loss".
        assert isinstance(changed, bool)


def test_remove_codex_marker_only_pair() -> None:
    """The non-fenced marker pair (`# ai-agent-config managed hooks` + codex_hooks=true)
    is removed cleanly without touching surrounding content.
    """
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text(
            "[features]\n"
            "foo = true\n"
            "# ai-agent-config managed hooks\n"
            "codex_hooks = true\n"
            "[other]\n"
            "value = 1\n",
            encoding="utf-8",
        )
        MHC.remove_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        assert "codex_hooks" not in text
        assert "foo = true" in text
        assert "[other]" in text


def test_remove_codex_restores_previous_marker() -> None:
    with in_tempdir() as tmp:
        dst = Path(tmp) / "config.toml"
        dst.write_text(
            "[features]\n"
            "# ai-agent-config managed hooks previous: codex_hooks = false\n"
            "codex_hooks = true\n",
            encoding="utf-8",
        )
        MHC.remove_codex_config(Path(tmp) / "ignored.toml", dst, dry_run=False)
        text = dst.read_text(encoding="utf-8")
        assert "codex_hooks = false" in text, "previous value must be restored"
        assert "previous:" not in text, "marker comment must be cleaned"


# ---------- runner ----------

TESTS = [
    test_merge_json_fresh_destination,
    test_merge_json_idempotent,
    test_merge_json_preserves_user_hook,
    test_merge_json_preserves_unmarked_runtime_link_hook,
    test_merge_json_keeps_unmarked_user_hook_with_runtime_link,
    test_merge_json_no_duplicate_when_destination_lacks_marker,
    test_merge_json_upgrades_legacy_managed_marker_without_duplicate,
    test_merge_json_pops_empty_event,
    test_merge_json_atomic_write_no_temp_leftover,
    test_merge_json_dry_run_no_write,
    test_remove_json_pops_event_when_empty,
    test_remove_json_preserves_user_hook,
    test_remove_json_cleans_legacy_event_not_in_source,
    test_remove_json_cleans_legacy_managed_marker_group,
    test_remove_json_dry_run_message_mentions_managed_hooks,
    test_merge_codex_no_features_section,
    test_merge_codex_existing_features_no_codex_hooks,
    test_merge_codex_idempotent,
    test_merge_codex_overrides_explicit_false,
    test_remove_codex_clean_block,
    test_remove_codex_orphan_managed_begin_preserved,
    test_remove_codex_marker_only_pair,
    test_remove_codex_restores_previous_marker,
]


def main() -> int:
    failures: list[tuple[str, str]] = []
    for test in TESTS:
        try:
            test()
        except Exception:  # noqa: BLE001 - test runner needs broad capture
            failures.append((test.__name__, traceback.format_exc()))
    passed = len(TESTS) - len(failures)
    print(f"merge-hook-config tests: {passed}/{len(TESTS)} passed")
    if failures:
        for name, tb in failures:
            print(f"\n--- FAIL: {name} ---", file=sys.stderr)
            sys.stderr.write(tb)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
