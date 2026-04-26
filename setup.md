# Setup

Use this guide to install the shared AI agent instructions and skills on any Unix-like machine.

**For AI agents:** treat this file as an executable setup brief. Determine the intended target workspace first, set `AI_AGENT_TARGET_DIR` explicitly, run `scripts/setup.sh`, then verify the links. Do not assume the config repository itself is the target unless the user says so.

## Quick Start

From the directory where the instruction files should appear, run:

```sh
AI_AGENT_TARGET_DIR="$PWD" sh /path/to/ai-agent-config/scripts/setup.sh
```

If you are running from the config repository root, set the target explicitly:

```sh
AI_AGENT_TARGET_DIR="/path/to/workspace" sh scripts/setup.sh
```

## Claude Code Setup Prompt

Give Claude Code this instruction:

> Read `setup.md`, set `AI_AGENT_TARGET_DIR` to the project or workspace directory that should receive the instruction entrypoints, then run `scripts/setup.sh` and verify the resulting links.

If Claude Code is opened inside this config repository, tell it the target directory explicitly:

```text
Read setup.md and set up my workspace at /path/to/workspace.
```

## What The Script Installs

The script creates symbolic links for these instruction entrypoints:

| Link Location | Source |
|---|---|
| `$AI_AGENT_TARGET_DIR/AGENTS.md` | `instructions/AGENTS.md` |
| `$AI_AGENT_TARGET_DIR/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `$AI_AGENT_TARGET_DIR/CLAUDE.md` | `instructions/CLAUDE.md` |
| `$AI_AGENT_TARGET_DIR/GEMINI.md` | `instructions/GEMINI.md` |
| `$AI_AGENT_TARGET_DIR/.github/copilot-instructions.md` | `instructions/.github/copilot-instructions.md` |

It also links every skill under `skills/*/SKILL.md` into the shared skills directory:

```text
$AI_AGENT_SKILLS_DIR
```

By default, that directory is:

```text
$HOME/.agents/skills
```

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `AI_AGENT_CONFIG_HOME` | Repository root inferred from `scripts/setup.sh` | Location of this config repository. |
| `AI_AGENT_TARGET_DIR` | Current working directory | Directory that receives `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and related entrypoints. |
| `AI_AGENT_SKILLS_DIR` | `$HOME/.agents/skills` | Shared skill directory used as the canonical cross-LLM skill location. |
| `AI_AGENT_EXTRA_SKILLS_DIRS` | Empty | Optional colon-separated list of additional skill directories to link into. |
| `AI_AGENT_INSTALL_INSTRUCTIONS` | `1` | Set to `0` to skip instruction entrypoint links. |
| `AI_AGENT_INSTALL_SKILLS` | `1` | Set to `0` to skip skill links. |
| `AI_AGENT_CONFLICT_MODE` | `backup` | `backup`, `skip`, or `fail` when a destination path already exists. |
| `AI_AGENT_BACKUP_DIR` | `$AI_AGENT_TARGET_DIR/.ai-agent-config-backups/<timestamp>` | Where existing conflicting files are moved when conflict mode is `backup`. |
| `AI_AGENT_PROTECT_LINKS` | `auto` | On macOS, applies `everyone deny delete` to created links. Set to `0` to disable. |
| `AI_AGENT_DRY_RUN` | `0` | Set to `1` to preview actions without changing files. |

## Examples

Install instructions into the current project and skills into the shared directory:

```sh
AI_AGENT_TARGET_DIR="$PWD" sh /path/to/ai-agent-config/scripts/setup.sh
```

Install into a specific workspace:

```sh
AI_AGENT_TARGET_DIR="$HOME/Downloads" sh "$HOME/Documents/ai-agent-config/scripts/setup.sh"
```

Install skills into both the shared directory and a Codex-specific directory:

```sh
AI_AGENT_EXTRA_SKILLS_DIRS="$HOME/.codex/skills" \
AI_AGENT_TARGET_DIR="$PWD" \
sh /path/to/ai-agent-config/scripts/setup.sh
```

Preview without making changes:

```sh
AI_AGENT_DRY_RUN=1 AI_AGENT_TARGET_DIR="$PWD" sh /path/to/ai-agent-config/scripts/setup.sh
```

## Conflict Handling

The default behavior is conservative:

- Existing correct links are kept.
- Existing conflicting files or links are moved into a timestamped backup directory.
- No file is permanently deleted.
- The script does not use `rm`.

Use `AI_AGENT_CONFLICT_MODE=fail` when you want the setup to stop instead of moving conflicts aside.

## Verification

After setup, verify:

```sh
readlink "$AI_AGENT_TARGET_DIR/AI_AGENT_INSTRUCTIONS.md"
readlink "$AI_AGENT_TARGET_DIR/CLAUDE.md"
find "${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}" -maxdepth 2 -name SKILL.md
```

Claude Code should be able to read `CLAUDE.md`, follow it to `AI_AGENT_INSTRUCTIONS.md`, and use linked skills from the shared skills directory.
