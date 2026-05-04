# AI Agent Config

Claude Code / Codex / Gemini CLI に共通の Instructions を配布するためのリポジトリです。

このリポジトリは、各 CLI のグローバル設定フォルダーへ instruction files をリンクします。必要に応じて、履歴にもとづく instruction 改善レビューを手動で実行します。

## 配置されるもの

| CLI | Entry point |
|---|---|
| Codex | `~/.codex/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |

加えて、各 CLI の設定フォルダーに次の共有ファイルをリンクします。

- `AI_AGENT_INSTRUCTIONS.md`
- `DESIGN.md`

さらに、`skills/` 配下の共有 skill も各 CLI のグローバル `skills/`
フォルダーへリンクします。

このリポジトリでは、CLI や `/init` 系コマンドがローカルに生成しうる root-level `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` は canonical ではありません。正本は `instructions/` 配下です。

## 前提条件

1. `git` が使えること
2. Claude Code / Codex / Gemini CLI を使う場合は、それぞれインストール済みであること
3. `uninstall.sh` を使う場合は `trash` コマンドがあること

## セットアップ

```sh
sh /path/to/ai-agent-config/scripts/setup.sh
```

`setup.sh` は instruction links と skill links を作成します。既存ファイルがある場合は既定で skip します。置き換える場合は `AI_AGENT_CONFLICT_MODE=replace` を指定します。

CLI の存在チェックを省く場合:

```sh
AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh
```

## 更新

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

`update.sh` は対象ブランチを fast-forward し、その後 `setup.sh` を再実行して instruction links を更新します。

## 状態確認

```sh
sh /path/to/ai-agent-config/scripts/health-check.sh
```

パスをマスクせず確認する場合:

```sh
AI_AGENT_HEALTH_REDACT=0 sh scripts/health-check.sh
```

## LLM 履歴 Instruction レビュー

`$daily-llm-history-instruction-review` は、Claude Code / Codex / Gemini CLI
の最近の履歴を要約的に確認し、反復的な非効率があれば `instructions/` を
抽象的に更新する on-demand skill です。定期実行は既定では使いません。

特に「続けて」「進捗は？」「やり直した方がいい？」のようなユーザーの反復
プロンプトは、その文言への反応ではなく、次回そのプロンプトを減らす agent
behavior として instruction 化します。詳しくは
`docs/llm-history-instruction-review.md` を参照してください。

## 取り外し

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

`uninstall.sh` は、このリポジトリが管理する instruction symlink だけを `trash` へ移します。ユーザーが手で作った通常ファイルや別 target の symlink は触りません。

## 保守方針

- 構成は `instructions/`、`scripts/`、必要に応じた `skills/`、最小 docs、CI validation、on-demand PR review workflow、on-demand の履歴 instruction レビューに絞ります。
- Instruction の構造を変えたら、`README.md`、`setup.md`、`scripts/validate-repo.sh` も同じ変更で合わせます。
- 履歴レビューで Instruction を変える場合は、既存文言に有機的に統合し、単なる追記を避けます。
