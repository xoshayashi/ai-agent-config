# Setup Error Guide

Instruction-only 構成での代表的な確認ポイントです。

| Symptom | Meaning | Fix |
|---|---|---|
| `skipping existing path` | default の `skip` mode が既存ファイルを保持したため、対象 link は作られていません。 | `sh scripts/health-check.sh` で未リンク箇所を確認し、置き換えてよい場合は `AI_AGENT_CONFLICT_MODE=replace sh scripts/setup.sh` を使います。 |
| `path already exists` | `AI_AGENT_CONFLICT_MODE=fail` で、配置先に既存ファイルがあります。 | 既存ファイルを確認し、`skip` に変えるか、backup して置き換えるなら `replace` で再実行します。 |
| Terminal.app に `setup.sh:` で始まる window が開く | `displaylink` / `docker-desktop` / `google-drive` / `tailscale-app` / `zoom` / `pmset` など、管理者権限が必要な処理だけを通常の Terminal で実行しています。 | Terminal の `sudo` プロンプトに macOS のパスワードを入力し、完了まで待ちます。 |
| `move skill backup out of skill root` | `skills/` 直下に `*.backup-*` があり、CLI が backup を skill として読む可能性があります。 | `setup.sh` が `<cli-home>/skill-backups/`、または旧 `~/.agents/skill-backups/` へ移動します。移動後に CLI セッションを再起動します。 |
| `trash is required for uninstall` | `uninstall.sh` は安全な削除のため `trash` を要求します。 | macOS なら `brew install trash`、Linux なら `trash-cli` を導入してから再実行します。 |
| health が `warn` | instruction link、notification hook、skill runtime、または repository 状態に確認点があります。CLI コマンドの有無は表示しますが、未導入だけでは warn にしません。 | `AI_AGENT_HEALTH_REDACT=0 sh scripts/health-check.sh` で具体 path を見て、必要なら `sh scripts/setup.sh` を再実行します。 |
| command path error が出る | CLI の個人設定、または起動済みセッションが、この checkout に含まれない command path を保持している可能性があります。 | 該当 CLI の個人設定から存在しない command path を外し、CLI セッションを再起動します。 |
| skill が認識されない | `skills/<name>` が `~/.codex/skills/<name>`、`~/.claude/skills/<name>`、`~/.gemini/skills/<name>` に反映されていないか、CLI を再起動していません。 | `sh scripts/setup.sh` を再実行し、Codex / Claude / Gemini CLI を再起動します。 |
| `python3 not found; skip notification hook setup` | `python3` が無く、通知 hook の設定を skip しました。 | macOS には標準で `python3` があります。`xcode-select --install` 等で導入後、`sh scripts/setup.sh` を再実行します。 |
| 通知が出ない | hook は設定済みでも、CLI セッションが古いか、端末アプリに通知許可がありません。 | `sh scripts/health-check.sh` の `notifications:` 行で `ok` を確認し、各 CLI を再起動します。macOS の システム設定 → 通知 で、端末アプリ（Terminal / iTerm など）の通知を許可します。 |
| Claude Code で通知が二重に出る | Claude Code 本体のネイティブ通知と、本リポジトリの `Notification` hook が両方鳴っています。 | どちらか一方に絞ります。hook 側を止める場合は、`~/.claude/settings.json` の `hooks.Notification` から `notify.sh` を呼ぶエントリを外します。 |
| `python package openpyxl missing` | `startup-financial-modeling` の xlsx 生成に必要な `openpyxl` が入っていません。 | `pip3 install -r skills/startup-financial-modeling/scripts/requirements.txt` を実行します。 |
| `libreoffice/soffice not found` | LibreOffice が無く、xlsx の再計算検証とスライド PDF レンダリングは skip されます（任意の依存です）。 | 必要なら `brew install --cask libreoffice` を実行後、`sh scripts/setup.sh` を再実行します。 |
| skill 実行時に `libreoffice not found` で exit 1 | LibreOffice は `soffice` という名前で入っており、`libreoffice` の名前で見つかりません。 | `sh scripts/setup.sh` を実行すると、`soffice` と同じディレクトリに `libreoffice` 互換 symlink を作成します。 |
| `brew doctor` が `libreoffice` symlink を警告する | `setup.sh` が作る `libreoffice` 互換 symlink です。 | 意図的なものです。外す場合は `trash /opt/homebrew/bin/libreoffice` を使います。 |

## 確認手順

```sh
AI_AGENT_HEALTH_REDACT=0 sh scripts/health-check.sh
sh scripts/setup.sh
sh scripts/health-check.sh
```
