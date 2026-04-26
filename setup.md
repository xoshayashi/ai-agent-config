# Setup

Use this guide to install the shared AI agent instructions and skills on any Unix-like machine.

**For AI agents:** treat this file as an executable setup brief. Use Japanese as the default conversation language unless the user asks otherwise. Determine the intended target workspace first, set `AI_AGENT_TARGET_DIR` explicitly, run a dry run, summarize the planned changes, then run `scripts/setup.sh` and verify the links. Do not assume the config repository itself is the target unless the user says so.

**Recommended target:** propose the user's normal parent folder for LLM CLI work first. If the user is unsure, recommend `~/Documents/projects`. If the user already has a team-mandated workspace, a monorepo root, or a folder where they regularly start Claude Code, Codex, and Gemini CLI, prefer that instead.

## Prerequisites / 前提条件

Before running this repository's setup, make sure the user can open a terminal and use all supported LLM CLIs: Claude Code, Codex, and Gemini CLI.

For beginner-facing setup, guide the user through these steps first:

1. **ターミナルを起動する。** macOSなら「ターミナル」または「iTerm2」、Windowsなら「PowerShell」または「Windows Terminal」を開きます。
2. **Claude Code、Codex、Gemini CLIを全てインストールする。** The official setup pages are the source of truth because CLI install methods can change.
3. **3つ全てのLLM CLIにログインする。** Start each installed CLI, complete browser or account authentication, and confirm each interactive prompt opens.

| Tool | Official Setup | Login Check |
|---|---|---|
| **Claude Code** | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) | Run `claude`; if prompted, use `/login` and follow the browser/account flow. |
| **Codex** | [Codex CLI](https://developers.openai.com/codex/cli) | Run `codex`; on first launch, sign in with a ChatGPT account or API key. |
| **Gemini CLI** | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) | Run `gemini`; choose **Login with Google** when asked how to authenticate. |

If installation or login fails for any required CLI, stop setup and help the user resolve that tool-specific issue using the relevant official documentation before continuing.

## Natural-Language GitHub Checkout / 自然言語での取得手順

The intended beginner flow is conversational: the user should be able to start a LLM CLI, paste one natural-language request, and let the LLM CLI handle GitHub login checks, repository checkout or pull, and setup.

Give the active Claude Code, Codex, or Gemini CLI session this instruction:

```text
GitHubにログインできているか確認して。未ログインなら、初心者にも分かる日本語でログイン手順を案内して。
その後、次のリポジトリをこのPCに取得して。既に同じリポジトリがある場合は、最新のmainをpullして。

https://github.com/xoshayashi/ai-agent-config.git

取得できたら、そのリポジトリのREADME.mdとsetup.mdを読んで、このPCにAI Agent Configをセットアップして。
Claude Code、Codex、Gemini CLIの全てがインストール済みかつログイン済みか確認して、未完了のものがあれば先に案内して。
セットアップ先は、まず推奨として「普段LLM CLIで作業する親フォルダー」を示して。迷っている場合は `~/Documents/projects` を推奨し、既に使っている作業フォルダーや会社指定のworkspaceがあればそれを優先して。
初回セットアップでは必ずdry runで事前確認して、作成されるリンク、バックアップされる可能性があるファイル、設定される更新頻度を日本語で要約してから本実行して。
専門用語は日本語で説明して、更新頻度は推奨の1日1回を含めて選ばせて。
```

For AI agents executing this request:

- Prefer a standard GitHub authentication check such as the GitHub CLI when available, but keep the user-facing interaction in plain Japanese.
- If the repository already exists locally, update it with the latest `main`; otherwise clone `https://github.com/xoshayashi/ai-agent-config.git` into a sensible local config location such as the user's Documents folder.
- After checkout or pull succeeds, continue with this setup guide rather than making the user issue a second command.
- If setup, update, scheduling, or uninstall fails, use [docs/setup-error-guide.md](docs/setup-error-guide.md) to explain the error and choose the next safe step.

## Recommended Target Workspace / 推奨セットアップ先

`AI_AGENT_TARGET_DIR` is the folder where the entrypoint links such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` will be placed. It should usually be the parent folder where the user starts LLM CLI work, not this config repository.

For beginners, recommend one target first instead of asking an open-ended question:

| Priority | Recommended Target | Use When |
|---|---|---|
| **1** | Existing team workspace | The company or team already has a standard workspace folder. |
| **2** | Existing daily work parent folder | The user already opens Claude Code, Codex, or Gemini CLI from a folder such as `~/Documents/projects`, `~/Workspace`, or a monorepo root. |
| **3** | `~/Documents/projects` | The user is unsure. This is the default recommendation for a clean personal setup. |
| **4** | `~/Downloads` | Temporary evaluation only. Avoid this for long-term work unless the user intentionally works there. |
| **Avoid** | This config repository root | Only use it when the user is developing this config repository itself. |

Suggested Japanese wording:

```text
セットアップ先は、普段LLM CLIで作業を始める親フォルダーにするのがおすすめです。
迷っている場合は `~/Documents/projects` を推奨します。
会社指定のworkspaceや、いつも使っている作業フォルダーがあればそちらを優先します。どれにしますか？
```

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

After all three LLM CLIs are installed and logged in, give the Claude Code, Codex, or Gemini CLI session that will perform setup this instruction:

> Read `setup.md`, explain any technical terms in plain Japanese, recommend a target workspace before asking me to choose, set `AI_AGENT_TARGET_DIR` to that project or workspace directory, ask me what update frequency I want with daily as the recommended option, run a dry run first and summarize the planned changes in Japanese, then run `scripts/setup.sh`, configure or disable updates according to my choice, and verify the resulting links.

If the user has not installed or logged in to all of Claude Code, Codex, and Gemini CLI yet, start from **Prerequisites / 前提条件** before running setup commands.

If the LLM CLI is opened inside this config repository, tell it the target directory explicitly:

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
| **GitHub** | Gitで管理されたファイルをインターネット上で保存・共有するサービスです。 |
| **Repository** | Gitで管理されているフォルダーです。多くの場合、GitHubからダウンロードします。 |
| **Clone** | GitHub上のリポジトリを、このPCへ初めて取得することです。 |
| **Pull** | 既にPCにあるリポジトリを、GitHub上の最新版に更新することです。 |
| **Workspace** | AIツールにこの共通ルールを読ませたい作業フォルダーです。 |
| **Symbolic link / symlink** | 実体ファイルへの近道のようなファイルです。コピーではなく、元ファイルを指し示します。 |
| **Environment variable** | コマンドに渡す一時的な設定です。たとえば、どのフォルダーをセットアップするかを指定します。 |
| **Skill** | AIツールに特定の作業手順を教える、再利用できる説明書パッケージです。 |
| **Backup** | 変更前に存在していたファイルを安全に残しておく退避先です。 |
| **Dry run** | 実際には変更せず、何が起きるかだけを確認する予行演習モードです。 |

For non-technical users, prefer this interaction pattern:

1. **GitHubログインを確認する。** 未ログインなら、ブラウザ認証など必要な操作だけを日本語で案内します。
2. **このリポジトリを取得または更新する。** PC上に無ければ取得し、既にあれば最新版の `main` に更新します。
3. **推奨セットアップ先を示して選んでもらう。** まず `~/Documents/projects`、既存の作業フォルダー、会社指定workspaceの順で提案します。例: "`~/Documents/projects` に設定するのがおすすめです。ここで開いたAIツールが共通ルールを読めるようになります。"
4. **実行前に短く説明する。** ユーザーが詳しい説明を求めない限り、日本語で2から3文に収めます。
5. **dry runで事前確認する。** `AI_AGENT_DRY_RUN=1` と `AI_AGENT_TARGET_DIR` を指定して予行演習し、作成予定のリンク、バックアップ候補、Skillリンク、状態ファイルを日本語で要約します。
6. **要約後に本実行する。** ユーザーが明示的に止めない限り、同じ `AI_AGENT_TARGET_DIR` で本実行します。
7. **更新頻度を選んでもらう。** 推奨は「1日1回」です。選択肢は「1日1回」「12時間ごと」「1週間ごと」「自動更新なし」「カスタム秒数」くらいに絞ります。
8. **更新設定を反映する。** 選んだ頻度に合わせて `AI_AGENT_UPDATE_CADENCE` または `AI_AGENT_UPDATE_INTERVAL_SECONDS` を指定し、`scripts/schedule-update.sh` で自動更新を設定または停止します。
9. **結果を確認して翻訳する。** `readlink` は「近道ファイルがどの本体ファイルを指しているか確認するコマンド」だと説明します。
10. **最後に簡単にまとめる。** 何を設定したか、バックアップが作られたか、更新頻度は何か、急ぎの時に何を頼めばよいかを短く伝えます。

## Dry-Run Approval / 事前確認

First-time setup should use dry run as a standard safety step.

```sh
AI_AGENT_DRY_RUN=1 AI_AGENT_TARGET_DIR="/path/to/workspace" sh /path/to/ai-agent-config/scripts/setup.sh
```

After dry run, summarize in Japanese:

- **リンク作成予定:** Which entrypoint files and skill directories would be linked.
- **既存ファイルの扱い:** Whether any existing files would be backed up.
- **状態ファイル:** Where setup state would be written for future updates.
- **次の実行:** The exact target workspace and update cadence that will be used for the real run.

Then proceed with the real setup unless the user stops or changes the target.

## Uninstall / 元に戻す

The uninstall flow removes only links and state files that this repository manages. It skips ordinary files and unmanaged links.

Preview first:

```sh
AI_AGENT_DRY_RUN=1 sh /path/to/ai-agent-config/scripts/uninstall.sh
```

Then run the actual cleanup:

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

For beginner-facing LLM CLI sessions, use this Japanese interaction:

```text
まずdry runで、どのリンクと設定ファイルを片付ける予定か確認します。
通常のファイルや、別の設定が作ったリンクは触りません。
問題なければ、実際の片付けでは対象をゴミ箱へ移します。
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

## Contributing And Validation / みんなで育てるために

When adding or changing shared instructions, setup behavior, skills, or agent workflows, keep portability and activation quality visible.

- **互換性を確認する:** Use [docs/compatibility.md](docs/compatibility.md) and [compatibility/llm-cli-matrix.yml](compatibility/llm-cli-matrix.yml) when a change may affect Claude Code, Codex, or Gemini CLI differently.
- **Skillはテンプレートから始める:** Start new skills from `skills/template/SKILL.md.template`, then fill in activation tests under `tests/`.
- **根拠を分離する:** Keep `SKILL.md` lean and put source notes, benchmarks, official references, or academic background in `references/`.
- **検証を実行する:** Before a pull request or distribution update, run:

```sh
sh scripts/validate-repo.sh
```

If validation fails, explain the error in Japanese, fix the smallest relevant issue, and run validation again.

## Examples

Install instructions into the current project and skills into the shared directory:

```sh
AI_AGENT_TARGET_DIR="$PWD" sh /path/to/ai-agent-config/scripts/setup.sh
```

Install into a specific workspace:

```sh
AI_AGENT_TARGET_DIR="$HOME/Documents/projects" sh "$HOME/Documents/ai-agent-config/scripts/setup.sh"
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

Preview uninstall without changing files:

```sh
AI_AGENT_DRY_RUN=1 sh /path/to/ai-agent-config/scripts/uninstall.sh
```

Undo setup by moving managed links and saved setup state to the trash:

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

If the user says **"全部元に戻して"** or **"AI Agent Configを外して"**, explain what will be moved to the trash, run the dry-run uninstall first, summarize it in Japanese, then run `scripts/uninstall.sh` unless the user changes course.

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
