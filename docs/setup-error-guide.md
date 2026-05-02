# Setup Error Guide

Instruction-only 構成での代表的な確認ポイントです。

| Symptom | Meaning | Fix |
|---|---|---|
| `missing required LLM CLI(s)` | `setup.sh` が Claude Code / Codex / Gemini CLI の存在を確認し、未導入の CLI を見つけました。 | CLI を導入するか、link 作成だけ先に行うなら `AI_AGENT_REQUIRE_LLM_CLIS=0 sh scripts/setup.sh` を使います。 |
| `skipping existing path` | default の `skip` mode が既存ファイルを保持したため、対象 link は作られていません。 | `sh scripts/health-check.sh` で未リンク箇所を確認し、置き換えてよい場合は `AI_AGENT_CONFLICT_MODE=replace sh scripts/setup.sh` を使います。 |
| `path already exists` | `AI_AGENT_CONFLICT_MODE=fail` で、配置先に既存ファイルがあります。 | 既存ファイルを確認し、`skip` に変えるか、backup して置き換えるなら `replace` で再実行します。 |
| `trash is required for uninstall` | `uninstall.sh` は安全な削除のため `trash` を要求します。 | macOS なら `brew install trash`、Linux なら `trash-cli` を導入してから再実行します。 |
| health が `warn` | instruction link、CLI コマンド、または repository 状態に確認点があります。 | `AI_AGENT_HEALTH_REDACT=0 sh scripts/health-check.sh` で具体 path を見て、必要なら `sh scripts/setup.sh` を再実行します。 |
| command path error が出る | CLI の個人設定、または起動済みセッションが、この checkout に含まれない command path を保持している可能性があります。 | 該当 CLI の個人設定から存在しない command path を外し、CLI セッションを再起動します。 |
| legacy daily review が `Operation not permitted` で落ちる | macOS `launchd` から project folder や CLI home へのアクセスが TCC / privacy 設定で拒否されています。 | 推奨は `docs/codex-automation-daily-review.md` に従って Codex App Automations へ移行することです。fallback を続ける場合は macOS privacy settings で該当 app / shell にアクセス権を付与します。 |
| skill が認識されない | `skills/<name>` が `~/.codex/skills/<name>`、`~/.claude/skills/<name>`、`~/.gemini/skills/<name>` に反映されていないか、CLI を再起動していません。 | `sh scripts/setup.sh` を再実行し、Codex / Claude / Gemini CLI を再起動します。 |

## 確認手順

```sh
AI_AGENT_HEALTH_REDACT=0 sh scripts/health-check.sh
sh scripts/setup.sh
sh scripts/health-check.sh
```
