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

### 取り外し

```sh
sh /path/to/llm-config/scripts/uninstall.sh
```

## 自然言語トリガー（運用）

- 「**急ぎ対応したいんだけど**」→ `scripts/update.sh`
- 「**設定が壊れていないか確認して**」→ `scripts/health-check.sh`
- 「**最近のログからSkill改善点を見て**」→ `python3 scripts/skill-improvement-bot.py scan`

## Hooks アーキテクチャの簡素化方針

- 管理レイヤーは **ユーザーグローバル1層**に統一（`~/.claude`, `~/.codex`, `~/.gemini`）
- プロジェクト層への自動 Hook 配布は廃止
- デフォルト Hook は安全性重視（`safe_delete_guard.py`）のみ
- `peer_prompt_refinement.py` は同梱するが、デフォルトでは配線しない（必要時のみ手動拡張）

これにより、ローカル負荷と多層 Hook 重複による挙動競合を抑えます。

## 補足

- compatibility マトリクス運用は廃止済みです
- 詳細手順は [setup.md](setup.md)
- エラー時は [docs/setup-error-guide.md](docs/setup-error-guide.md)
- Skill 改善自動化は [docs/skill-improvement-automation.md](docs/skill-improvement-automation.md)
- Hooks 設計検証は [docs/hooks-architecture-review.md](docs/hooks-architecture-review.md)
