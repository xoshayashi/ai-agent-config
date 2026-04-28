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
5. `trash` コマンド（無い場合は `scripts/setup.sh` 実行時に確認の上で自動インストール）

| Tool | Official Setup |
|---|---|
| Claude Code | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) |
| Codex | [Codex CLI](https://developers.openai.com/codex/cli) |
| Gemini CLI | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) |
| trash (macOS) | `brew install trash` |
| trash-cli (Linux) | `sudo apt-get install -y trash-cli` 等 |

`trash` はこのリポジトリの `scripts/uninstall.sh` と `scripts/disable-auto-permission.sh` が安全に削除を行うために必須です（`rm` は使いません）。`scripts/setup.sh` は `trash` が無ければインストールコマンドを提示して y/N 確認します（**Enter は「いいえ」**、`AI_AGENT_ASSUME_YES=1` で確認スキップ）。

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
| `~/.codex/HOOKS.md` | `instructions/HOOKS.md` |
| `~/.claude/HOOKS.md` | `instructions/HOOKS.md` |
| `~/.gemini/HOOKS.md` | `instructions/HOOKS.md` |

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

### 回答後自律継続 Hook（任意）

`response_strategy_bridge.py` は設定に登録済みですが、既定では無効です。  
有効化する場合のみ、シェル設定に次を追加します。

```sh
export AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY=1
```

追加で provider を固定する場合:

```sh
export AI_AGENT_RESPONSE_STRATEGY_PROVIDER=gemini   # gemini / codex / ollama
```

`ollama` を使う場合はモデル指定が必須です。

```sh
export AI_AGENT_RESPONSE_STRATEGY_PROVIDER=ollama
export AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL=qwen2.5:latest
```

### Codex中心マルチLLMオーケストレーション Hook（任意）

`multillm_orchestrator.py` は Codex Hook 設定に登録済みで、既定では無効です。  
有効化すると、Codexをハブとして次を実行します。

1. `UserPromptSubmit`: Codexに仕様起草ブリーフを注入
2. `Stop` で `[[SPEC_DONE]]` が出たら Claude が仕様レビュー
3. Claude が未完成と判断したら、Codexへ仕様修正プロンプトを返す
4. Claude が確定と判断したら、そのまま実装に進める
5. 実装中は Claude が次ステップ提案、Gemini が定期レビュー

有効化したい場合:

```sh
export AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=1
```

Geminiレビュー頻度（実装ターン数ベース）:

```sh
export AI_AGENT_ORCHESTRATOR_GEMINI_REVIEW_EVERY=3
```

peer CLI 内部待機時間を延ばしたい場合:

```sh
export AI_AGENT_ORCHESTRATOR_TIMEOUT_SECONDS=45
```

注記:

- orchestration を有効化しても、実際には **重い設計 / 実装 / レビュー系 prompt を中心に起動** させる前提です
- Codex の `Stop` では、Gemini critique と Claude guidance が同じターンで順に走ることがあるため、**外側 Hook timeout は内部 timeout の 2 倍弱を見込む** のが安全です

Claude spec review / implementation guidance の thinking 深さを調整したい場合:

```sh
export AI_AGENT_ORCHESTRATOR_CLAUDE_SIMPLE_EFFORT=low
export AI_AGENT_ORCHESTRATOR_CLAUDE_COMPLEX_EFFORT=high
```

完了キーワードと終了条件は `instructions/HOOKS.md` を参照します。

### 入力前プロンプト改善

入力前のプロンプト改善は、グローバル Hook ではなく **Skill
`peer-prompt-refinement`** で運用します。  
そのため、`scripts/setup.sh` は prompt refinement 用 Hook を各 CLI 設定に登録しません。

### 3 CLI の auto-permission モード（任意・別コマンド）

> ⚠️ **既定の安全側を下げる opt-in です。** 内容を理解した上で実行してください。

`shell/auto-permission.sh` には Codex / Gemini CLI / Claude Code を承認スキップ・auto モードで起動する shell ラッパーが定義されています。`scripts/setup.sh` には**意図的に組み込まれていません**。明示 opt-in したい場合のみ、専用スクリプトを実行します。

| CLI | 適用される flag |
|---|---|
| `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `gemini` | `--yolo` |
| `claude` | `--permission-mode auto`（通常セッション時のみ。`auth` / `mcp` / `plugin` / `doctor` 等は素の挙動） |

#### 有効化

```sh
sh /path/to/llm-config/scripts/enable-auto-permission.sh
```

実行内容（追加されるシンボリックリンクと shell rc に追記される marker block）を表示してから `y/N` で確認します。**Enter キーは「いいえ」** が既定です。CI 等で確認をスキップしたい場合は `AI_AGENT_ASSUME_YES=1` を併用します。

shell rc は次の marker block に挟まれて 1 行 source されるだけです。

```sh
# >>> ai-agent-config managed shell wrappers >>>
# Managed by scripts/enable-auto-permission.sh in ai-agent-config.
# Reverse with scripts/disable-auto-permission.sh.
[ -r "$HOME/.llm-config/auto-permission.sh" ] && . "$HOME/.llm-config/auto-permission.sh"
# <<< ai-agent-config managed shell wrappers <<<
```

#### 無効化

```sh
sh /path/to/llm-config/scripts/disable-auto-permission.sh
```

shell rc から marker block を削除し、シンボリックリンクを `trash` に送ります。冪等。

#### サポートされる shell

`SHELL` 環境変数を見て、`zsh` なら `~/.zshrc`、`bash` なら `~/.bash_profile`（macOS 想定）または `~/.bashrc` を対象にします。それ以外の shell の場合は `enable` が中断します（必要に応じて手動でスニペットを source してください）。

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
| `AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION` | `0` | `1` でCodex中心マルチLLMオーケストレーションHookを有効化 |
| `AI_AGENT_ORCHESTRATOR_TIMEOUT_SECONDS` | `45` | orchestration 内の Claude/Gemini 呼び出しの内部待機秒数 |
| `AI_AGENT_ORCHESTRATOR_CLAUDE_SIMPLE_EFFORT` | `low` | 簡単な Claude 非対話レビュー時の effort |
| `AI_AGENT_ORCHESTRATOR_CLAUDE_COMPLEX_EFFORT` | `high` | 複雑な Claude 非対話レビュー時の effort |
| `AI_AGENT_ORCHESTRATOR_GEMINI_REVIEW_EVERY` | `3` | 実装何ターンごとにGeminiレビューを挟むか |
| `AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY` | `0` | `1` で回答後の peer レビュー継続 Hook を有効化 |
| `AI_AGENT_RESPONSE_STRATEGY_PROVIDER` | `auto` | `auto` / `gemini` / `codex` / `ollama` |
| `AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL` | Empty | `provider=ollama` 時に使うモデル名 |
| `AI_AGENT_CONFLICT_MODE` | `backup` | `backup` / `skip` / `fail` |
| `AI_AGENT_BACKUP_DIR` | `$AI_AGENT_STATE_DIR/backups/<timestamp>` | 競合時の退避先 |
| `AI_AGENT_STATE_DIR` | `~/.llm-config` | `config.env` などの状態ファイル保存先 |
| `AI_AGENT_PERSIST_CONFIG` | `1` | `0` で状態ファイルを書かない |
| `AI_AGENT_REQUIRE_LLM_CLIS` | `1` | `1` で `claude` / `codex` / `gemini` の存在を事前チェック（不足時は失敗） |
| `AI_AGENT_DRY_RUN` | `0` | `1` で予行演習 |

## 更新

## 絶対パス import について

- `instructions/CLAUDE.md` と `instructions/GEMINI.md` の `@...` import は、各CLIの実際の読み込み挙動に合わせて **絶対パス** で管理しています。
- このリポジトリを別のPCや別パスに clone した場合は、`scripts/setup.sh` をその clone 先から実行して、各CLIのグローバル設定に張られるエントリーポイントをその環境向けに作り直してください。
- 手で `instructions/*.md` を別の場所へコピーした場合は、`@/absolute/path/...` の参照先もその環境に合わせて更新が必要です。

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

既定ではパス/remote情報はマスク表示です。フル表示が必要な時のみ:

```sh
AI_AGENT_HEALTH_REDACT=0 sh /path/to/llm-config/scripts/health-check.sh --json
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
