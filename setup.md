# Setup

Use this guide to install the shared AI agent instructions and skills on any Unix-like machine.

**For AI agents:** treat this file as an executable setup brief. Use Japanese as the default conversation language unless the user asks otherwise. Determine the intended target workspace first, set `AI_AGENT_TARGET_DIR` explicitly, run `scripts/setup.sh`, then verify the links. Do not assume the config repository itself is the target unless the user says so.

## Quick Start

From the directory where the instruction files should appear, run:

```sh
AI_AGENT_TARGET_DIR="$PWD" sh /path/to/ai-agent-config/scripts/setup.sh
```

If you are running from the config repository root, set the target explicitly:

```sh
AI_AGENT_TARGET_DIR="/path/to/workspace" sh scripts/setup.sh
```

If you are using the installer script from a downloaded release or checked-out copy, it can clone or update the config repository for you:

```sh
AI_AGENT_TARGET_DIR="/path/to/workspace" sh /path/to/ai-agent-config/scripts/install.sh
```

## Claude Code / Codex / Gemini CLI Setup Prompt

Give Claude Code, Codex, or Gemini CLI this instruction:

> Read `setup.md`, explain any technical terms in plain Japanese, set `AI_AGENT_TARGET_DIR` to the project or workspace directory that should receive the instruction entrypoints, ask me what update frequency I want with daily as the recommended option, then run `scripts/setup.sh`, configure or disable updates according to my choice, and verify the resulting links.

If the AI CLI is opened inside this config repository, tell it the target directory explicitly:

```text
Read setup.md and set up my workspace at /path/to/workspace.
```

## Beginner-Friendly Interaction / 初心者にもやさしい対話

This setup may be used by every employee type, including people who are new to terminals, Git, Claude Code, Codex, Gemini CLI, or AI agent configuration. When an AI agent helps with setup, it should make the process understandable without turning the session into a lecture. The default employee-facing conversation should be in Japanese.

Before running commands, the agent should briefly explain in Japanese:

- **何が変わるか:** 選んだ作業フォルダーに、AIツールが共通ルールを見つけるための小さな案内ファイルを置きます。
- **どこが変わるか:** `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` などが置かれるフォルダーが対象です。
- **なぜリンクを使うか:** 共通ルールの本体は1か所で管理しつつ、各AIツールが期待する場所から読めるようにするためです。
- **既存ファイルの扱い:** 同じ名前のファイルがある場合、標準では削除せずバックアップフォルダーへ退避します。
- **成功状態:** 対象フォルダーに案内ファイルのリンクができ、共有Skillも設定済みのSkillフォルダーから使える状態です。

Use plain Japanese explanations for technical terms the first time they appear. Keep command names, file names, and environment variable names in their original spelling, then explain what they mean.

| Term | Plain Japanese Explanation |
|---|---|
| **Repository** | Gitで管理されているフォルダーです。多くの場合、GitHubからダウンロードします。 |
| **Workspace** | AIツールにこの共通ルールを読ませたい作業フォルダーです。 |
| **Symbolic link / symlink** | 実体ファイルへの近道のようなファイルです。コピーではなく、元ファイルを指し示します。 |
| **Environment variable** | コマンドに渡す一時的な設定です。たとえば、どのフォルダーをセットアップするかを指定します。 |
| **Skill** | AIツールに特定の作業手順を教える、再利用できる説明書パッケージです。 |
| **Backup** | 変更前に存在していたファイルを安全に残しておく退避先です。 |
| **Dry run** | 実際には変更せず、何が起きるかだけを確認する予行演習モードです。 |

For non-technical users, prefer this interaction pattern:

1. **対象フォルダーを人間の言葉で伝える。** 例: "Downloadsフォルダーに設定します。ここで開いたAIツールが共通ルールを読めるようになります。" 対象が不明な場合だけ、平易な質問を1つして確認します。
2. **実行前に短く説明する。** ユーザーが詳しい説明を求めない限り、日本語で2から3文に収めます。
3. **セットアップを実行する。** 現在のフォルダーに依存しないよう、`AI_AGENT_TARGET_DIR` を明示して実行します。
4. **更新頻度を選んでもらう。** 推奨は「1日1回」です。選択肢は「1日1回」「12時間ごと」「1週間ごと」「自動更新なし」「カスタム秒数」くらいに絞ります。
5. **更新設定を反映する。** 選んだ頻度に合わせて `AI_AGENT_UPDATE_CADENCE` または `AI_AGENT_UPDATE_INTERVAL_SECONDS` を指定し、`scripts/schedule-update.sh` で自動更新を設定または停止します。
6. **結果を確認して翻訳する。** `readlink` は「近道ファイルがどの本体ファイルを指しているか確認するコマンド」だと説明します。
7. **最後に簡単にまとめる。** 何を設定したか、バックアップが作られたか、更新頻度は何か、急ぎの時に何を頼めばよいかを短く伝えます。

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
| `AI_AGENT_REPO_URL` | `https://github.com/xoshayashi/ai-agent-config.git` | Repository URL used by `scripts/install.sh` when cloning. |
| `AI_AGENT_TARGET_DIR` | Current working directory | Directory that receives `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and related entrypoints. |
| `AI_AGENT_SKILLS_DIR` | `$HOME/.agents/skills` | Shared skill directory used as the canonical cross-LLM skill location. |
| `AI_AGENT_EXTRA_SKILLS_DIRS` | Empty | Optional colon-separated list of additional skill directories to link into. |
| `AI_AGENT_STATE_DIR` | `$HOME/.ai-agent-config` | Stores setup state used by future updates. |
| `AI_AGENT_INSTALL_INSTRUCTIONS` | `1` | Set to `0` to skip instruction entrypoint links. |
| `AI_AGENT_INSTALL_SKILLS` | `1` | Set to `0` to skip skill links. |
| `AI_AGENT_CONFLICT_MODE` | `backup` | `backup`, `skip`, or `fail` when a destination path already exists. |
| `AI_AGENT_BACKUP_DIR` | `$AI_AGENT_TARGET_DIR/.ai-agent-config-backups/<timestamp>` | Where existing conflicting files are moved when conflict mode is `backup`. |
| `AI_AGENT_PROTECT_LINKS` | `auto` | On macOS, applies `everyone deny delete` to created links. Set to `0` to disable. |
| `AI_AGENT_PERSIST_CONFIG` | `1` | Set to `0` to avoid writing setup state for `scripts/update.sh`. |
| `AI_AGENT_DRY_RUN` | `0` | Set to `1` to preview actions without changing files. |

## Keeping Config Updated

The instruction files and skills are linked from this repository. That means updates become available after this repository itself is updated.

After the first setup, run:

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

`scripts/update.sh` does three things:

1. Pulls the latest `main` from GitHub using a fast-forward-only Git update.
2. Reads the saved setup state from `$HOME/.ai-agent-config/config.env`.
3. Runs `scripts/setup.sh` again so links and skills stay aligned with the latest repository contents.

For automatic updates, schedule the updater with the recommended daily cadence:

```sh
AI_AGENT_UPDATE_CADENCE=daily sh /path/to/ai-agent-config/scripts/schedule-update.sh
```

This uses `launchd` on macOS and a user `systemd` timer on Linux when available. If neither is available, the script prints the manual update command.

Update-related variables:

| Variable | Default | Purpose |
|---|---|---|
| `AI_AGENT_UPDATE_REMOTE` | `origin` | Git remote to fetch from. |
| `AI_AGENT_UPDATE_BRANCH` | `main` | Branch to update from. |
| `AI_AGENT_UPDATE_CADENCE` | Empty | Friendly schedule name: `recommended`, `daily`, `twice-daily`, `weekly`, `manual`, or `custom`. |
| `AI_AGENT_UPDATE_RERUN_SETUP` | `1` | Set to `0` to pull updates without re-running setup. |
| `AI_AGENT_UPDATE_ALLOW_DIRTY` | `0` | Set to `1` to allow updates when the config repository has local changes. |
| `AI_AGENT_UPDATE_INTERVAL_SECONDS` | `86400` | Auto-update interval used by `schedule-update.sh`; required when `AI_AGENT_UPDATE_CADENCE=custom`. |

Recommended choices:

| User Choice | Command Setting | Meaning |
|---|---|---|
| **1日1回（推奨）** | `AI_AGENT_UPDATE_CADENCE=daily` | Balanced default for most employees. |
| **12時間ごと** | `AI_AGENT_UPDATE_CADENCE=twice-daily` | Useful while instructions are changing quickly. |
| **1週間ごと** | `AI_AGENT_UPDATE_CADENCE=weekly` | Lower-noise option for stable environments. |
| **自動更新なし** | `AI_AGENT_UPDATE_CADENCE=manual` | Stops any existing automatic updater; the user updates manually when needed. |
| **カスタム** | `AI_AGENT_UPDATE_CADENCE=custom AI_AGENT_UPDATE_INTERVAL_SECONDS=<seconds>` | Advanced option for admins or special cases. |

## Urgent Manual Updates

If the user says something like **"急ぎ対応したいんだけど"**, **"今すぐ最新にして"**, or **"最新のルールを反映して"**, the agent should run a one-time update instead of waiting for the next scheduled run:

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

Explain in Japanese that this pulls the latest shared instructions immediately and re-applies the saved setup. If the update stops because the config repository has local changes, explain that the script stopped to avoid overwriting local edits.

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

Schedule daily updates, the recommended cadence:

```sh
AI_AGENT_UPDATE_CADENCE=daily sh /path/to/ai-agent-config/scripts/schedule-update.sh
```

Run an urgent one-time update:

```sh
sh /path/to/ai-agent-config/scripts/update.sh
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

Claude Code, Codex, and Gemini CLI should be able to read their entrypoint files, follow them to `AI_AGENT_INSTRUCTIONS.md`, and use linked skills from the shared skills directory.
