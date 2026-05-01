# Setup

このリポジトリは、Claude Code / Codex / Gemini CLI のグローバル instruction files と、日次の instruction 改善レビューを管理します。

## インストール内容

| Destination | Source |
|---|---|
| `~/.codex/AGENTS.md` | `instructions/AGENTS.md` |
| `~/.codex/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.codex/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.claude/CLAUDE.md` | `instructions/CLAUDE.md` |
| `~/.claude/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.claude/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.gemini/GEMINI.md` | `instructions/GEMINI.md` |
| `~/.gemini/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.gemini/DESIGN.md` | `instructions/DESIGN.md` |

## 基本コマンド

```sh
sh scripts/setup.sh
sh scripts/health-check.sh
sh scripts/update.sh
sh scripts/uninstall.sh
./scripts/install-daily-llm-history-instruction-review
./scripts/uninstall-daily-llm-history-instruction-review
```

`setup.sh` は既定で Claude Code / Codex / Gemini CLI のコマンド存在を確認します。まだ入れていない CLI がある状態で link だけ作りたい場合は、次のように実行します。

```sh
AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh
```

## Conflict Handling

既存ファイルがある場合、`AI_AGENT_CONFLICT_MODE` で挙動を変えられます。

| Value | Behavior |
|---|---|
| `skip` | 既存 path を残して skip |
| `fail` | 既存 path があれば失敗 |
| `replace` | 既存 path を同じ directory の `<name>.backup-<timestamp>` へ移してから link 作成 |

例:

```sh
AI_AGENT_CONFLICT_MODE=fail sh scripts/setup.sh
```

## Validation

変更前後の確認には次を使います。

```sh
sh scripts/validate-repo.sh
```

この validation は、必要なファイルの存在、repository surface、任意の `skills/` 構造、entrypoint 参照、health-check と setup dry-run を確認します。

## Daily Review

`scripts/install-daily-llm-history-instruction-review` は macOS `launchd` に `com.ai-agent-config.daily-llm-history-instruction-review` を登録し、毎日 00:00 に `scripts/daily-llm-history-instruction-review` を直接実行します。

実行内容:

- Claude Code / Codex / Gemini CLI の直近 2 日分を中心にした履歴を要約的に確認
- 非効率が反復している場合のみ `instructions/` を抽象的に更新
- `scripts/setup.sh`、`scripts/validate-repo.sh`、`git diff --check` を実行
- `cron-log/` に Markdown 要約を保存

`cron-log/` は git 管理外です。時刻は `AI_AGENT_DAILY_REVIEW_HOUR` / `AI_AGENT_DAILY_REVIEW_MINUTE`、ログ保持数は `AI_AGENT_DAILY_REVIEW_LOG_KEEP` で変更できます。`AI_AGENT_DAILY_REVIEW_LOG_KEEP=0` はローテーション無効です。Claude Code は `instructions/` を作業ディレクトリにし、履歴は一時 symlink set、日付で絞った JSONL history、Gemini history の tail slice だけを参照します。`Edit` / `MultiEdit` の実効範囲は Claude Code の cwd と `--add-dir` 境界に依存するため、この日次処理は信頼済みローカル環境でのみ使います。
