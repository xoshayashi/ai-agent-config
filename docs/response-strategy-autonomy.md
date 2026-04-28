# Response Strategy Hook Design (Historical Note)

This file is kept only as historical context for an earlier design that
considered calling another LLM after each completion event.

That design is no longer the active path in this repository.

Current status:

- `response_strategy_bridge.py` is removed from the active codebase
- external reviewer continuation is not part of the default workflow
- the supported path is the same-LLM self-workflow in
  [self-workflow-hooks.md](./self-workflow-hooks.md)

Keep this file only as a record of why the repository moved away from
post-response multi-LLM continuation.
