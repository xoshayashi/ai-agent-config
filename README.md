# AI Agent Config

Claude Code / Codex / Gemini CLI で共通の Instructions・Skills・Hooks を配布するためのリポジトリです。  
**現在はグローバル設定前提**で運用します。

## 何が設定されるか

### Instructions（グローバル）

| CLI | 配置先 |
|---|---|
| Codex | `~/.codex/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |

加えて各フォルダーに `AI_AGENT_INSTRUCTIONS.md` と `DESIGN.md` をリンクします。
加えて各フォルダーに `HOOKS.md` もリンクします。

> 注意: 旧方式で行っていた `.github/copilot-instructions.md` の自動配置は廃止しました。  
> Copilot の指示はリポジトリ単位で扱う前提のため、必要な場合は対象リポジトリ側で明示的に配置してください。

### Skills（共有）

- 既定: `~/.agents/skills`

### Hooks（グローバル）

| CLI | 設定先 |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Codex | `~/.codex/config.toml` と `~/.codex/hooks.json` |
| Gemini CLI | `~/.gemini/settings.json` |

Hook 本体はこのリポジトリで管理し、実行時は安定リンクを参照します。

```text
${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks} -> <this repo>/hooks
```

## 前提条件

1. ターミナルを起動できること
2. **Claude Code / Codex / Gemini CLI を全てインストール済み**であること
3. **3つ全てでログイン済み**であること
4. `git` と `python3` が使えること
5. `trash` コマンド（macOS は `brew install trash`、Linux は `trash-cli` パッケージ）

`scripts/setup.sh` は既定で 3 CLI の存在チェックを行います（`AI_AGENT_REQUIRE_LLM_CLIS=0` で無効化可能）。

`trash` がインストールされていない場合、`scripts/setup.sh` は対応するパッケージマネージャ（macOS: `brew`、Linux: `apt-get` / `dnf` / `pacman`）を検出して **インストールコマンドを提示し、y/N で確認**します（**Enter は「いいえ」**）。`AI_AGENT_ASSUME_YES=1` を付けると確認をスキップして即実行します。

| OS | 自動提案されるコマンド |
|---|---|
| macOS | `brew install trash` |
| Debian/Ubuntu | `sudo apt-get install -y trash-cli` |
| Fedora/RHEL | `sudo dnf install -y trash-cli` |
| Arch | `sudo pacman -S --noconfirm trash-cli` |

これらの環境以外では、`trash` を手動で導入してから setup を再実行してください。

| ツール | 公式手順 |
|---|---|
| Claude Code | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) |
| Codex | [Codex CLI](https://developers.openai.com/codex/cli) |
| Gemini CLI | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) |

## LLM CLI に貼るセットアップ依頼（自然言語）

```text
GitHubログイン状態を確認して。未ログインなら日本語で案内して。
次に https://github.com/xoshayashi/llm-config.git を ~/Documents/llm-config に取得して。既にあれば最新mainをpullして。
README.mdとsetup.mdを読んで、このPCにグローバル設定としてセットアップして。
Claude Code/Codex/Gemini CLIが全てインストール・ログイン済みか確認し、未完了があれば先に案内して。
初回はdry runして、作成リンク・追記対象・バックアップ候補を日本語で要約してから本実行して。
既存のsettings.jsonやconfig.tomlがある場合は置換せず、共有Hookだけappend/mergeして説明して。
更新頻度は推奨の1日1回を含めて選ばせて。
```

## 手動コマンド

### セットアップ

```sh
sh /path/to/llm-config/scripts/setup.sh
```

### 更新

```sh
sh /path/to/llm-config/scripts/update.sh
```

### 状態確認

```sh
sh /path/to/llm-config/scripts/health-check.sh
```

`health-check` は既定でパス/remote情報をマスク表示します（`AI_AGENT_HEALTH_REDACT=0` でフル表示）。

### 取り外し

```sh
sh /path/to/llm-config/scripts/uninstall.sh
```

## オプション: 3 CLI の auto-permission モードを既定化

> ⚠️ **これは安全側を下げる opt-in です。** 内容を理解した上で、自己責任で実行してください。
> 非エンジニアの方や、AI エージェントが自分のマシンで何をしうるか把握していない場合は **使わないでください**。

`shell/auto-permission.sh` には、Codex / Gemini CLI / Claude Code を **承認スキップ・auto モード**で起動する shell 用ラッパーが入っています。

| CLI | 適用される flag |
|---|---|
| `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `gemini` | `--yolo` |
| `claude` | `--permission-mode auto`（通常セッション時のみ。`auth` / `mcp` / `plugin` / `doctor` 等は素の挙動） |

これを有効化すると、これら 3 CLI から起動した AI エージェントは **ファイル削除・コマンド実行・shell 操作などをユーザに毎回確認せずに行えます**。

### 有効化

`scripts/setup.sh` には**意図的に組み込まれていません**。明示的に opt-in する場合のみ、専用スクリプトを実行してください。

```sh
sh /path/to/llm-config/scripts/enable-auto-permission.sh
```

実行すると、変更内容（追加されるシンボリックリンクと shell rc に追記される marker block）を表示してから、`y/N` で確認します。**Enter キーは「いいえ」**。

非インタラクティブな環境で確認をスキップしたい場合（CI 等）：

```sh
AI_AGENT_ASSUME_YES=1 sh /path/to/llm-config/scripts/enable-auto-permission.sh
```

### 無効化

```sh
sh /path/to/llm-config/scripts/disable-auto-permission.sh
```

shell rc から marker block を削除し、シンボリックリンクを `trash` に送ります。冪等です。

## 自然言語トリガー（運用）

- 「**急ぎ対応したいんだけど**」→ `scripts/update.sh`
- 「**設定が壊れていないか確認して**」→ `scripts/health-check.sh`
- 「**最近のログからSkill改善点を見て**」→ `python3 scripts/skill-improvement-bot.py scan`

## Hooks アーキテクチャの簡素化方針

- 管理レイヤーは **ユーザーグローバル1層**に統一（`~/.claude`, `~/.codex`, `~/.gemini`）
- プロジェクト層への自動 Hook 配布は廃止
- 安全性重視 Hook（`safe_delete_guard.py`）は既定ON
- 共通 Hook（`self_workflow.py`）は **Codex / Claude Code / Gemini CLI の managed event に登録済み**
- `self_workflow.py` は qualifying-task 判定に通ったときだけ spec -> implementation -> verification の自己継続 loop を起動
- 入力前プロンプト改善と phase boundary の brief 引き締めは **Skill（`refinment`）で運用**
- `refinment` は self-contained。現在の CLI が必要と判断したときだけ brief を整え、必要なら `Refined prompt:` を表示してから作業を始める
- 外部 reviewer を使う multi-LLM orchestration / response-strategy の main path は廃止

これにより、ローカル負荷と多層 Hook 重複による挙動競合を抑えつつ、同じ CLI が自分のタスクを最後まで完了しやすくします。

## 補足

- compatibility マトリクス運用は廃止済みです
- 詳細手順は [setup.md](setup.md)
- `CLAUDE.md` / `GEMINI.md` の `@` import は、CLIの解決仕様に合わせて絶対パスで管理しています。別のPCや別パスに clone した場合は、その clone 先から `scripts/setup.sh` を再実行して各CLI設定を作り直してください
- エラー時は [docs/setup-error-guide.md](docs/setup-error-guide.md)
- Skill 改善自動化は [docs/skill-improvement-automation.md](docs/skill-improvement-automation.md)
- Hooks 設計検証は [docs/hooks-architecture-review.md](docs/hooks-architecture-review.md)
- 現行の共通自己完結フローは [docs/self-workflow-hooks.md](docs/self-workflow-hooks.md)
