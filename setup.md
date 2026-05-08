# Setup

このリポジトリは、Claude Code / Codex / Gemini CLI のグローバル instruction files と共有 skill links を管理します。

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
| `replace` | 既存 path を backup folder へ移してから link 作成。skill は `~/.codex/skill-backups/`、`~/.claude/skill-backups/`、`~/.gemini/skill-backups/` に逃がし、`skills/` 直下には置きません。 |

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

## Skill Links

`setup.sh` の skill links は `skills/<name>` を `~/.codex/skills/<name>`、
`~/.claude/skills/<name>`、`~/.gemini/skills/<name>` にリンクします。skill が
見えない時は `sh scripts/setup.sh` を再実行し、各 CLI を再起動します。
廃止済みの管理対象 skill symlink は、`setup.sh` または `uninstall.sh` の実行時に
通常ファイルや別 target の symlink と区別して片付けます。
既存の `*.backup-*` skill が `skills/` 直下にある場合も、setup 時に各 home の
`skill-backups/` へ移動し、バックアップが skill として読み込まれないようにします。
旧 skill root として残っている `~/.agents/skills/*.backup-*` も同じく
`~/.agents/skill-backups/` へ移動します。
