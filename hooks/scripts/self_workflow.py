#!/usr/bin/env python3
"""Compatibility shim for older managed hook configs.

Legacy Claude/Codex/Gemini/Copilot settings may still invoke
`hooks/scripts/self_workflow.py`. The current implementation lives in
`subprocess_check.py`, so this shim forwards execution there until the local
CLI settings are re-applied.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the script directory to Python path so subprocess_check can be imported
sys.path.insert(0, str(Path(__file__).parent))

from subprocess_check import main


if __name__ == "__main__":
    raise SystemExit(main())
