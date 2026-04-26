# Setup

このガイドは、共有 Instructions / Skills / Hooks を **グローバル設定**として導入する手順です。  
対象 CLI は **Claude Code / Codex / Gemini CLI** です。

## AI エージェント向け実行ルール

- 既定の会話言語は日本語
- まず前提（3 CLI のインストール・ログイン、`git`、`python3`）を確認
- 初回は必ず dry run を実行して、変更予定を日本語で要約
- 既存の `settings.json` / `config.toml` がある場合は置換せず append/merge

## 前提条件

1. ターミナルを起動できる  
2. Claude Code / Codex / Gemini CLI が全てインストール済み  
3. 3つ全てでログイン済み  
4. `git` と `python3` が利用可能

| Tool | Official Setup |
|---|---|
| Claude Code | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) |
| Codex | [Codex CLI](https://developers.openai.com/codex/cli) |
| Gemini CLI | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) |

## 自然言語での取得とセットアップ

以下を Claude Code / Codex / Gemini CLI のどれかに貼り付けると、GitHub確認からセットアップまで会話で進められます。

```text
GitHubログイン状態を確認して。未ログインなら日本語で案内して。
次に https://github.com/xoshayashi/llm-config.git を ~/Documents/llm-config に取得して。既にあれば最新mainをpullして。
README.mdとsetup.mdを読んで、このPCにグローバル設定としてセットアップして。
Claude Code/Codex/Gemini CLIが全てインストール・ログイン済みか確認し、未完了があれば先に案内して。
初回はdry runして、作成リンク・追記対象・バックアップ候補を日本語で要約してから本実行して。
既存のsettings.jsonやconfig.tomlがある場合は置換せず、共有Hookだけappend/mergeして説明して。
更新頻度は推奨の1日1回を含めて選ばせて。
```

## Quick Start

### 1) Dry run（必須推奨）

```sh
AI_AGENT_DRY_RUN=1 sh /path/to/llm-config/scripts/setup.sh
```

### 2) 本実行

```sh
sh /path/to/llm-config/scripts/setup.sh
```

## 何がインストールされるか

### Instructions（グローバル）

| Link | Source |
|---|---|
| `~/.codex/AGENTS.md` | `instructions/AGENTS.md` |
| `~/.claude/CLAUDE.md` | `instructions/CLAUDE.md` |
| `~/.gemini/GEMINI.md` | `instructions/GEMINI.md` |
| `~/.codex/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.claude/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.gemini/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.codex/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.claude/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.gemini/DESIGN.md` | `instructions/DESIGN.md` |

> Note: `.github/copilot-instructions.md` の自動配置は行いません。  
> Copilot 向け設定は、利用する各リポジトリで個別に管理してください。

### Skills

| Link Location | Source |
|---|---|
| `$AI_AGENT_SKILLS_DIR/<skill-name>` | `skills/<skill-name>` |

既定の `$AI_AGENT_SKILLS_DIR` は `~/.agents/skills` です。

### Hooks（グローバル）

Hook スクリプト本体はリポジトリ管理し、CLI 側は安定リンク経由で参照します。

| Link Location | Source |
|---|---|
| `$AI_AGENT_HOOKS_RUNTIME_LINK` | `hooks/` |

既定の `$AI_AGENT_HOOKS_RUNTIME_LINK` は `~/.llm-config/hooks` です。

CLI 側設定先:

| CLI | Hook settings location |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Codex | `~/.codex/config.toml` と `~/.codex/hooks.json` |
| Gemini CLI | `~/.gemini/settings.json` |

## 既存個人設定の扱い

- 既存設定ファイルがある場合、`scripts/setup.sh` は **append/merge** を実行します
- `append:` ログが出た場合、既存設定を保持したまま managed Hook 部分のみ追加しています
- 競合時の既定は `backup` で、変更前ファイルは退避されます

## 環境変数

| Variable | Default | Purpose |
|---|---|---|
| `AI_AGENT_CONFIG_HOME` | `scripts/setup.sh` から推定 | この設定リポジトリの場所 |
| `AI_AGENT_CODEX_HOME` | `~/.codex` | Codex グローバル設定フォルダー |
| `AI_AGENT_CLAUDE_HOME` | `~/.claude` | Claude Code グローバル設定フォルダー |
| `AI_AGENT_GEMINI_HOME` | `~/.gemini` | Gemini CLI グローバル設定フォルダー |
| `AI_AGENT_SKILLS_DIR` | `~/.agents/skills` | 共有 Skill 配置先 |
| `AI_AGENT_EXTRA_SKILLS_DIRS` | Empty | 追加 Skill 配置先（`:` 区切り） |
| `AI_AGENT_INSTALL_INSTRUCTIONS` | `1` | `0` で Instructions のリンク作成をスキップ |
| `AI_AGENT_INSTALL_SKILLS` | `1` | `0` で Skills のリンク作成をスキップ |
| `AI_AGENT_INSTALL_HOOKS` | `1` | `0` で Hook 設定導入をスキップ |
| `AI_AGENT_HOOKS_RUNTIME_LINK` | `~/.llm-config/hooks` | Hook スクリプト参照用の安定リンク |
| `AI_AGENT_CONFLICT_MODE` | `backup` | `backup` / `skip` / `fail` |
| `AI_AGENT_BACKUP_DIR` | `$AI_AGENT_STATE_DIR/backups/<timestamp>` | 競合時の退避先 |
| `AI_AGENT_PROTECT_LINKS` | `auto` | macOS で `everyone deny delete` を付与 |
| `AI_AGENT_STATE_DIR` | `~/.llm-config` | `config.env` などの状態ファイル保存先 |
| `AI_AGENT_PERSIST_CONFIG` | `1` | `0` で状態ファイルを書かない |
| `AI_AGENT_DRY_RUN` | `0` | `1` で予行演習 |

## 更新

### 手動更新

```sh
sh /path/to/llm-config/scripts/update.sh
```

### 自動更新（推奨: 1日1回）

```sh
AI_AGENT_UPDATE_CADENCE=daily sh /path/to/llm-config/scripts/schedule-update.sh
```

| 選択肢 | 設定 |
|---|---|
| 1日1回（推奨） | `AI_AGENT_UPDATE_CADENCE=daily` |
| 12時間ごと | `AI_AGENT_UPDATE_CADENCE=twice-daily` |
| 1週間ごと | `AI_AGENT_UPDATE_CADENCE=weekly` |
| 自動更新なし | `AI_AGENT_UPDATE_CADENCE=manual` |
| カスタム | `AI_AGENT_UPDATE_CADENCE=custom AI_AGENT_UPDATE_INTERVAL_SECONDS=<seconds>` |

## Health Check

```sh
sh /path/to/llm-config/scripts/health-check.sh
```

JSON 出力:

```sh
sh /path/to/llm-config/scripts/health-check.sh --json
```

## Skill 改善自動化

改善候補スキャン:

```sh
python3 scripts/skill-improvement-bot.py scan
```

定期実行設定:

```sh
AI_AGENT_IMPROVEMENT_CADENCE=daily sh scripts/schedule-skill-improvement.sh
```

`schedule-skill-improvement.sh` はローカルログをスキャンし、明示 opt-in 変数がある時のみ PR 作成・レビュー対応・自動マージに進みます。  
詳細は [docs/skill-improvement-automation.md](docs/skill-improvement-automation.md) を参照してください。

## 自然言語の運用トリガー

| Phrase | Script |
|---|---|
| 「急ぎ対応したいんだけど」 | `scripts/update.sh` |
| 「今すぐ最新にして」 | `scripts/update.sh` |
| 「設定が壊れていないか確認して」 | `scripts/health-check.sh` |
| 「最近のログからSkill改善点を見て」 | `scripts/skill-improvement-bot.py scan` |

## Uninstall

まず dry run:

```sh
AI_AGENT_DRY_RUN=1 sh /path/to/llm-config/scripts/uninstall.sh
```

本実行:

```sh
sh /path/to/llm-config/scripts/uninstall.sh
```

`uninstall.sh` は managed link と managed Hook 設定のみを外します。  
削除操作は完全削除ではなく `trash` を使います。
