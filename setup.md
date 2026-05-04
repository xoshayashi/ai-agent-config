# Setup

このリポジトリは、Claude Code / Codex / Gemini CLI のグローバル instruction files と、on-demand の履歴ベース instruction 改善レビューを管理します。

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

## LLM History Review

`$daily-llm-history-instruction-review` は必要なときに手動で呼び出します。
定期実行は既定では使いません。詳しくは
`docs/llm-history-instruction-review.md` を参照してください。

実行内容:

- Claude Code / Codex / Gemini CLI の直近 2 日分を中心にした履歴を要約的に確認
- 非効率が反復している場合のみ `instructions/` を抽象的に更新
- ユーザーの反復プロンプトを、そのプロンプトを減らす agent behavior に翻訳
- `scripts/setup.sh`、`scripts/validate-repo.sh`、`git diff --check` を実行

`setup.sh` の skill links は `skills/<name>` を `~/.codex/skills/<name>`、
`~/.claude/skills/<name>`、`~/.gemini/skills/<name>` にリンクします。skill が
見えない時は `sh scripts/setup.sh` を再実行し、各 CLI を再起動します。

履歴 review は `daily-llm-history-instruction-review` skill を使います。
