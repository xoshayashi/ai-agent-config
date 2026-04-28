#!/usr/bin/env python3
"""Legacy compatibility entrypoint for stale hook sessions.

The active workflow hook is ``self_workflow.py``. Some already-running CLI
sessions may still hold the previous hook command path in memory and try to
execute ``multillm_orchestrator.py``. Keep this thin shim so those sessions
continue to work until they restart and reload the current config.
"""

from __future__ import annotations

from self_workflow import main


if __name__ == "__main__":
    raise SystemExit(main())
