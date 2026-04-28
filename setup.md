# Setup

このガイドは、共有 Instructions / Skills / Hooks を **グローバル設定**として導入する手順です。  
グローバル導入の対象 CLI は **Claude Code / Codex / Gemini CLI / GitHub Copilot CLI** です。

> やさしい導線から入りたい場合は、先に [docs/getting-started.md](docs/getting-started.md) を読んでください。

## AI エージェント向け実行ルール

- 既定の会話言語は日本語
- まず前提（4 CLI のインストール・ログイン、`git`、`python3`）を確認
- 初回は必ず dry run を実行して、変更予定を日本語で要約
- 既存の `settings.json` / `config.toml` がある場合は置換せず append/merge
- Copilot CLI も通常の導入対象。必要なら、この repo の tracked `.github/copilot-instructions.md` も確認

## 前提条件

1. ターミナルを起動できる  
2. Claude Code / Codex / Gemini CLI / GitHub Copilot CLI が全てインストール済み
3. 4つ全てでログイン済み
4. `git` と `python3` が利用可能
5. `trash` コマンド（無い場合は `scripts/setup.sh` 実行時に確認の上で自動インストール）

| Tool | Official Setup |
|---|---|
| Claude Code | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) |
| Codex | [Codex CLI](https://developers.openai.com/codex/cli) |
| Gemini CLI | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) |
| GitHub Copilot CLI | [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) |
| trash (macOS) | `brew install trash` |
| trash-cli (Linux) | `sudo apt-get install -y trash-cli` 等 |

`trash` はこのリポジトリの `scripts/uninstall.sh` と `scripts/disable-auto-permission.sh` が安全に削除を行うために必須です（`rm` は使いません）。`scripts/setup.sh` は `trash` が無ければインストールコマンドを提示して y/N 確認します（**Enter は「いいえ」**、`AI_AGENT_ASSUME_YES=1` で確認スキップ）。

## 自然言語での取得とセットアップ

以下を Claude Code / Codex / Gemini CLI / Copilot CLI のどれかに貼り付けると、GitHub確認からセットアップまで会話で進められます。

```text
GitHubログイン状態を確認して。未ログインなら日本語で案内して。
次に https://github.com/xoshayashi/ai-agent-config.git を ~/Documents/ai-agent-config に取得して。既にあれば最新mainをpullして。
README.mdとsetup.mdを読んで、このPCにグローバル設定としてセットアップして。
Claude Code/Codex/Gemini CLI/Copilot CLIが全てインストール・ログイン済みか確認し、未完了があれば先に案内して。
初回はdry runして、作成リンク・追記対象・バックアップ候補を日本語で要約してから本実行して。
既存のsettings.jsonやconfig.tomlがある場合は置換せず、共有Hookだけappend/mergeして説明して。
GitHub Copilot CLI には `~/.copilot` 側の global config を入れ、この repo では tracked な `.github/copilot-instructions.md` も確認して。
更新頻度は推奨の1日1回を含めて選ばせて。
```

## Quick Start

### 1) Dry run（必須推奨）

```sh
AI_AGENT_DRY_RUN=1 sh /path/to/ai-agent-config/scripts/setup.sh
```

### 2) 本実行

```sh
sh /path/to/ai-agent-config/scripts/setup.sh
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
| `~/.copilot/copilot-instructions.md` | `instructions/COPILOT.md` |
| `~/.copilot/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.copilot/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.copilot/HOOKS.md` | `instructions/HOOKS.md` |

この repo 自体では [.github/copilot-instructions.md](.github/copilot-instructions.md) を tracked file として持ちます。
別のリポジトリで同じ repo-level instructions を使いたい場合は、`instructions/.github/copilot-instructions.md` をベースに配置してください。

### Copilot（repo-level, tracked in this repo）

| Target | Canonical Source |
|---|---|
| `.github/copilot-instructions.md` | `instructions/.github/copilot-instructions.md` |

`scripts/setup.sh` と `scripts/health-check.sh` の主対象は `~/.copilot` の global config です。
repo-level の `.github/copilot-instructions.md` は、この repo 自体で Copilot を使うための tracked file です。

### Skills

| Link Location | Source |
|---|---|
| `$AI_AGENT_SKILLS_DIR/<skill-name>` | `skills/<skill-name>` |
| `~/.copilot/skills/<skill-name>` | `skills/<skill-name>` |

既定の `$AI_AGENT_SKILLS_DIR` は `~/.agents/skills` です。
Copilot CLI 用には同じ Skill を `~/.copilot/skills` にも配置します。

### Hooks（グローバル）

Hook スクリプト本体はリポジトリ管理し、各 CLI 側の `hooks/` リンクから参照します。

| Link Location | Source |
|---|---|
| `~/.claude/hooks` | `hooks/` |
| `~/.codex/hooks` | `hooks/` |
| `~/.gemini/hooks` | `hooks/` |
| `~/.copilot/hooks` | `hooks/` |

共有 state や backup の保存先は既定で `~/.ai-agent-config` です。
shared state や backup の正本は `~/.ai-agent-config` です。

CLI 側設定先:

| CLI | Hook settings location |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Codex | `~/.codex/config.toml` と `~/.codex/hooks.json` |
| Gemini CLI | `~/.gemini/settings.json` |
| GitHub Copilot CLI | `~/.copilot/settings.json` |

### Same-LLM Subprocess Check Hook

`subprocess_check.py` は Claude Code / Codex / Gemini CLI / GitHub Copilot CLI の Hook 設定に登録済みで、**managed event で常時 routed** です。
Hook 境界で同じ CLI を非対話サブプロセスとして 1 回呼び、次の具体的な 1 手か `STATUS: complete` を返させます。
旧 `self_workflow.py` は、既存のローカル設定が残っている環境向けの互換 shim として同梱しています。

1. startup event (`UserPromptSubmit` / `SessionStart` または `BeforeAgent`) で、最初の具体的な 1 手を相談する
2. Stop 系 event では、短い返答や answer-only の返答を軽量 gate で弾く
3. 実質的な作業が続いているときだけ、同じ CLI に「次に何をするか」を聞く
4. サブプロセスが `STATUS: complete` を返したら、そのタスクの継続を止める

注記:

- subprocess-check Hook は常時 routed ですが、軽量 gate が no-op 判定を返すこともあります
- 入力前の brief 改善は **Skill `refinment`** 側の判断に委ねます
- 完了シグナルと停止条件の正本は `instructions/HOOKS.md` です
- 外部 reviewer を呼ぶ `response strategy` / `multi-LLM orchestration` は現行 main path では使いません

### 入力前プロンプト改善

入力前のプロンプト改善は、グローバル Hook ではなく **Skill
`refinment`** で運用します。  
そのため、`scripts/setup.sh` は refinment 専用 Hook を各 CLI 設定に登録しません。

### 3 CLI の auto-permission モード（任意・別コマンド）

> ⚠️ **既定の安全側を下げる opt-in です。** 内容を理解した上で実行してください。

`shell/auto-permission.sh` には Codex / Gemini CLI / Claude Code を承認スキップ・auto モードで起動する shell ラッパーが定義されています。`scripts/setup.sh` には**意図的に組み込まれていません**。明示 opt-in したい場合のみ、専用スクリプトを実行します。

Copilot CLI の `--allow-all` / `--yolo` は、このラッパーでは管理していません。

| CLI | 適用される flag |
|---|---|
| `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `gemini` | `--yolo` |
| `claude` | `--permission-mode auto`（通常セッション時のみ。`auth` / `mcp` / `plugin` / `doctor` 等は素の挙動） |

#### 有効化

```sh
sh /path/to/ai-agent-config/scripts/enable-auto-permission.sh
```

実行内容（追加されるシンボリックリンクと shell rc に追記される marker block）を表示してから `y/N` で確認します。**Enter キーは「いいえ」** が既定です。CI 等で確認をスキップしたい場合は `AI_AGENT_ASSUME_YES=1` を併用します。

shell rc は次の marker block に挟まれて 1 行 source されるだけです。

```sh
# >>> ai-agent-config managed shell wrappers >>>
# Managed by scripts/enable-auto-permission.sh in ai-agent-config.
# Reverse with scripts/disable-auto-permission.sh.
[ -r "$HOME/.ai-agent-config/auto-permission.sh" ] && . "$HOME/.ai-agent-config/auto-permission.sh"
# <<< ai-agent-config managed shell wrappers <<<
```

#### 無効化

```sh
sh /path/to/ai-agent-config/scripts/disable-auto-permission.sh
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
| `AI_AGENT_COPILOT_HOME` | `~/.copilot` | GitHub Copilot CLI グローバル設定フォルダー |
| `AI_AGENT_SKILLS_DIR` | `~/.agents/skills` | 共有 Skill 配置先 |
| `AI_AGENT_EXTRA_SKILLS_DIRS` | Empty | 追加 Skill 配置先（`:` 区切り） |
| `AI_AGENT_INSTALL_INSTRUCTIONS` | `1` | `0` で Instructions のリンク作成をスキップ |
| `AI_AGENT_INSTALL_SKILLS` | `1` | `0` で Skills のリンク作成をスキップ |
| `AI_AGENT_INSTALL_HOOKS` | `1` | `0` で Hook 設定導入をスキップ |
| `AI_AGENT_CONFLICT_MODE` | `backup` | `backup` / `skip` / `fail` |
| `AI_AGENT_BACKUP_DIR` | `$AI_AGENT_STATE_DIR/backups/<timestamp>` | 競合時の退避先 |
| `AI_AGENT_STATE_DIR` | `~/.ai-agent-config` | `config.env`、backup、scheduler log などの状態ファイル保存先 |
| `AI_AGENT_PERSIST_CONFIG` | `1` | `0` で状態ファイルを書かない |
| `AI_AGENT_REQUIRE_LLM_CLIS` | `1` | `1` で `claude` / `codex` / `gemini` / `copilot` の存在を事前チェック（不足時は失敗） |
| `AI_AGENT_SELF_WORKFLOW_MAX_CONTINUATIONS_PER_TASK` | `5` | 自動継続の上限回数 |
| `AI_AGENT_SELF_WORKFLOW_MAX_SAME_PROMPT` | `2` | 同じ継続プロンプトを繰り返せる上限 |
| `AI_AGENT_SELF_WORKFLOW_MAX_VERIFICATION_TURNS` | `3` | verification 自動継続の上限回数 |
| `AI_AGENT_DRY_RUN` | `0` | `1` で予行演習 |

## 更新

## 絶対パス import について

- `instructions/CLAUDE.md` と `instructions/GEMINI.md` の `@...` import は、各CLIの実際の読み込み挙動に合わせて **絶対パス** で管理しています。
- このリポジトリを別のPCや別パスに clone した場合は、`scripts/setup.sh` をその clone 先から実行して、各CLIのグローバル設定に張られるエントリーポイントをその環境向けに作り直してください。
- 手で `instructions/*.md` を別の場所へコピーした場合は、`@/absolute/path/...` の参照先もその環境に合わせて更新が必要です。
- Copilot の `instructions/.github/copilot-instructions.md` は repo-level template です。別のリポジトリ側へ置くときは、そのリポジトリの運用に合わせて反映してください。

### 手動更新

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

### 自動更新（推奨: 1日1回）

```sh
AI_AGENT_UPDATE_CADENCE=daily sh /path/to/ai-agent-config/scripts/schedule-update.sh
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
sh /path/to/ai-agent-config/scripts/health-check.sh
```

JSON 出力:

```sh
sh /path/to/ai-agent-config/scripts/health-check.sh --json
```

既定ではパス/remote情報はマスク表示です。フル表示が必要な時のみ:

```sh
AI_AGENT_HEALTH_REDACT=0 sh /path/to/ai-agent-config/scripts/health-check.sh --json
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
AI_AGENT_DRY_RUN=1 sh /path/to/ai-agent-config/scripts/uninstall.sh
```

本実行:

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

`uninstall.sh` は managed link と managed Hook 設定のみを外します。  
削除操作は完全削除ではなく `trash` を使います。
