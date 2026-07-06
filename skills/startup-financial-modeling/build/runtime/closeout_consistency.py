"""Closeout consistency checks for SFM self-improvement edits."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
COUNT_RE = re.compile(
    r"<!--\s*sfm-closeout-count\s+name=\"(?P<name>[^\"]+)\"\s+"
    r"expected=\"(?P<expected>\d+)\"\s+glob=\"(?P<glob>[^\"]+)\"\s*-->"
)


def _is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def _strip_anchor(target: str) -> str:
    return target.split("#", 1)[0]


def check_markdown_file(path: Path) -> list[str]:
    """Return dangling local links and declared-count drift for one file."""
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    base = path.parent

    for match in LINK_RE.finditer(text):
        target = _strip_anchor(match.group(1).strip())
        if not target or _is_external(target):
            continue
        if target.startswith("/"):
            candidate = Path(target)
        else:
            candidate = (base / target).resolve()
        if not candidate.exists():
            errors.append(f"dangling_ref:{path.name}->{target}")

    for match in COUNT_RE.finditer(text):
        name = match.group("name")
        expected = int(match.group("expected"))
        glob = match.group("glob")
        found = len([item for item in base.glob(glob) if item.is_file()])
        if found != expected:
            errors.append(f"count_drift:{path.name}:{name}:expected={expected}:found={found}:glob={glob}")

    return errors


def check_closeout_consistency(paths: list[Path]) -> list[str]:
    """Return deterministic closeout errors across markdown protocol files."""
    errors: list[str] = []
    for path in paths:
        if path.suffix.lower() == ".md" and path.exists():
            errors.extend(check_markdown_file(path))
        elif not path.exists():
            errors.append(f"missing_path:{path}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Markdown files to check")
    args = parser.parse_args()
    errors = check_closeout_consistency([Path(p) for p in args.paths])
    print(json.dumps({"errors": errors, "ok": not errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
