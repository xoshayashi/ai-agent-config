"""Thin CLI wrapper for the startup financial modeling runtime."""

from __future__ import annotations

import sys
from pathlib import Path


def _runtime_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "build" / "runtime"


def main(argv: list[str] | None = None) -> int:
    runtime_dir = _runtime_dir()
    sys.path.insert(0, str(runtime_dir))
    from build_model import _main  # noqa: PLC0415

    return _main(argv)


if __name__ == "__main__":
    sys.exit(main())
