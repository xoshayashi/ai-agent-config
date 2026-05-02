# Setup

このリポジトリは、Claude Code / Codex / Gemini CLI のグローバル instruction files と、Codex App Automations ベースの日次 instruction 改善レビューを管理します。

## インストール内容

| Destination | Source |
|---|---|
| `~/.codex/AGENTS.md` | `instructions/AGENTS.md` |
| `~/.codex/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.codex/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.codex/skills/<name>` | `skills/<name>` |
| `~/.claude/CLAUDE.md` | `instructions/CLAUDE.md` |
| `~/.claude/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.claude/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.claude/skills/<name>` | `skills/<name>` |
| `~/.gemini/GEMINI.md` | `instructions/GEMINI.md` |
| `~/.gemini/AI_AGENT_INSTRUCTIONS.md` | `instructions/AI_AGENT_INSTRUCTIONS.md` |
| `~/.gemini/DESIGN.md` | `instructions/DESIGN.md` |
| `~/.gemini/skills/<name>` | `skills/<name>` |

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

推奨ルートは Codex App Automations です。
`docs/codex-automation-daily-review.md` にある automation 作成リクエストを
Codex app で実行し、毎日 00:00 に
`$daily-llm-history-instruction-review` を呼び出す standalone project
automation を作ります。

実行内容:

- Claude Code / Codex / Gemini CLI の直近 2 日分を中心にした履歴を要約的に確認
- 非効率が反復している場合のみ `instructions/` を抽象的に更新
- `scripts/setup.sh`、`scripts/validate-repo.sh`、`git diff --check` を実行

既存の macOS `launchd` schedule を外す場合:

```sh
./scripts/uninstall-daily-llm-history-instruction-review
```

Codex App Automations が使えない環境では、legacy fallback として
`scripts/install-daily-llm-history-instruction-review` を使えます。これは macOS
`launchd` に `com.ai-agent-config.daily-llm-history-instruction-review` を登録し、
毎日 00:00 に `scripts/daily-llm-history-instruction-review` を直接実行します。

legacy fallback の `cron-log/` は git 管理外です。時刻は
`AI_AGENT_DAILY_REVIEW_HOUR` / `AI_AGENT_DAILY_REVIEW_MINUTE`、ログ保持数は
`AI_AGENT_DAILY_REVIEW_LOG_KEEP` で変更できます。
`AI_AGENT_DAILY_REVIEW_LOG_KEEP=0` はローテーション無効です。この fallback は
Claude Code を `instructions/` で起動し、履歴は一時 symlink set、日付で絞った
JSONL history、Gemini history の tail slice だけを参照します。`Edit` /
`MultiEdit` の実効範囲は Claude Code の cwd と `--add-dir` 境界に依存するため、
信頼済みローカル環境でのみ使います。

`setup.sh` の skill links は `skills/<name>` を `~/.codex/skills/<name>`、
`~/.claude/skills/<name>`、`~/.gemini/skills/<name>` にリンクします。skill が
見えない時は `sh scripts/setup.sh` を再実行し、各 CLI を再起動します。

日次 review の automation は `daily-llm-history-instruction-review` skill を使います。
