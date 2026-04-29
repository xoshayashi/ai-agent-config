# AI Agent Config

Claude Code / Codex / Gemini CLI で共通の Instructions・Skills・Hooks を配布するためのリポジトリです。
**現在は 3 CLI のグローバル設定**という形で運用します。

## 何が設定されるか

### Instructions（グローバル）

| CLI | 配置先 |
|---|---|
| Codex | `~/.codex/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |

加えて各フォルダーに `AI_AGENT_INSTRUCTIONS.md` と `DESIGN.md` をリンクします。
加えて各フォルダーに `HOOKS.md` もリンクします。

> 注意: `scripts/setup.sh` が自動配置するのは **Claude Code / Codex / Gemini CLI のグローバル設定**だけです。  
> このリポジトリでは、CLI や `/init` 系コマンドがローカルに生成しうる `/AGENTS.md`、`/CLAUDE.md`、`/GEMINI.md` は **canonical ではありません**。正本は `instructions/` 配下にあり、これらのローカル生成物は `.gitignore` で無視します。

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
${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.ai-agent-config/hooks} -> <this repo>/hooks
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
次に https://github.com/xoshayashi/ai-agent-config.git を ~/Documents/ai-agent-config に取得して。既にあれば最新mainをpullして。
README.mdとsetup.mdを読んで、このPCにグローバル設定としてセットアップして。
Claude Code/Codex/Gemini CLIが全てインストール・ログイン済みか確認し、未完了があれば先に案内して。
初回はdry runして、作成リンク・追記対象・バックアップ候補を日本語で要約してから本実行して。
既存のsettings.jsonやconfig.tomlがある場合は置換せず、共有Hookだけappend/mergeして説明して。
更新頻度は推奨の1日1回を含めて選ばせて。
```

## 手動コマンド

### セットアップ

```sh
sh /path/to/ai-agent-config/scripts/setup.sh
```

### 更新

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

### 状態確認

```sh
sh /path/to/ai-agent-config/scripts/health-check.sh
```

`health-check` は既定でパス/remote情報をマスク表示します（`AI_AGENT_HEALTH_REDACT=0` でフル表示）。

`setup.sh` は既定で **update** と **skill-improvement** の scheduler も登録します。
`update` scheduler は、作業中の branch 違いまたは未コミット変更がある場合は上書きせず `skip` して止まります。

### 取り外し

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

## 自然言語トリガー（運用）

- 「**急ぎ対応したいんだけど**」→ `scripts/update.sh`
- 「**設定が壊れていないか確認して**」→ `scripts/health-check.sh`
- 「**最近のログからSkill改善点を見て**」→ `python3 scripts/skill-improvement-bot.py scan`

## Hooks アーキテクチャの簡素化方針

- 管理レイヤーは **ユーザーグローバル1層**に統一（`~/.claude`, `~/.codex`, `~/.gemini`）
- プロジェクト層への自動 Hook 配布は廃止
- 安全性重視 Hook（`safe_delete_guard.py`）は既定ON
- managed Hook は **deterministic な safety/policy check だけ** に絞る
- 仕様整理・実装・検証・セルフレビューの主導権は、Hook ではなく現在の CLI 本体に持たせる
- 入力前の brief 整理が本当に必要なときだけ **Skill（`refinment`）** を使う
- `refinment` は self-contained。現在の CLI が必要と判断したときだけ brief を整え、必要なら `Refined prompt:` を表示してから作業を始める
- Hook-driven orchestration、phase state、completion keyword の main path は持たない

これにより、ローカル負荷と多層 Hook 重複による挙動競合を抑えつつ、同じ CLI が自分のタスクを最後まで完了しやすくします。

## 補足

- compatibility マトリクス運用は廃止済みです
- 詳細手順は [setup.md](setup.md)
- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` の entrypoint ファイルは、各 CLI の実際の読み込み挙動に合わせて管理しています。別のPCや別パスに clone した場合は、その clone 先から `scripts/setup.sh` を再実行して各CLI設定を作り直してください
- エラー時は [docs/setup-error-guide.md](docs/setup-error-guide.md)
- Skill 改善自動化は [docs/skill-improvement-automation.md](docs/skill-improvement-automation.md)
- Hooks 設計検証は [docs/hooks-architecture-review.md](docs/hooks-architecture-review.md)
