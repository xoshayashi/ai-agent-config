# AI Agent Config

Claude Code / Codex / Gemini CLI に共通の Instructions を配布するためのリポジトリです。

このリポジトリは、各 CLI のグローバル設定フォルダーへ instruction files をリンクします。

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

加えて、シェル設定 `shell/.zshrc` を `~/.zshrc` へリンクします。`.zshrc` の正本は
このリポジトリ側にあり、`~/.zshrc` はそのシンボリックリンクになります。

このリポジトリでは、CLI や `/init` 系コマンドがローカルに生成しうる root-level `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` は canonical ではありません。正本は `instructions/` 配下です。

## 通知 hook

`setup.sh` は、各 CLI がターンを終えたとき、および入力や承認を待つときにデスクトップ通知を出す hook も設定します。

| CLI | 通知のきっかけ | 設定先 |
|---|---|---|
| Claude Code | `Stop`（完了） / `Notification`（要対応） | `~/.claude/settings.json` の `hooks` |
| Codex | `Stop`（完了） / `PermissionRequest`（承認待ち） | `~/.codex/hooks.json` |
| Gemini CLI | `AfterAgent`（完了） / `Notification`（要対応） | `~/.gemini/settings.json` の `hooks` |

通知は共有スクリプト `notifications/notify.sh` が出します。macOS では `osascript` でバナーと音を出し、それ以外の OS では端末ベルにフォールバックします。

`~/.claude/settings.json` と `~/.gemini/settings.json` は通知以外の設定も持つため、symlink ではなく `scripts/install-notifications.py` が hook 部分だけを冪等にマージします。書き換え前にタイムスタンプ付き backup を作り、ユーザーが手で足した hook は残します。`~/.codex/hooks.json` は hook 専用ファイルとして生成します。除去は `uninstall.sh` が同じヘルパーで行います。

## 前提条件

1. `git` が使えること
2. macOS では `setup.sh` が Homebrew と Command Line Tools の導入を試みます
3. Perplexity の App Store 版を自動導入する場合は、Mac App Store にサインイン済みであること
4. `uninstall.sh` を使う場合は `trash` コマンドがあること

## セットアップ

```sh
sh /path/to/ai-agent-config/scripts/setup.sh
```

`setup.sh` は macOS の bootstrap（Homebrew、Command Line Tools、Codex /
Claude Code / Gemini CLI / Antigravity CLI、`python` / `pip`、zsh 補助ツール、
指定アプリの cask / App Store app）、現在の macOS 設定の再適用、instruction links、skill links、
シェル設定 link を実行します。既存ファイルがある場合は既定で skip します。置き換える場合は `AI_AGENT_CONFLICT_MODE=replace` を指定します。
置換時の skill backup は各 CLI home の `skill-backups/` に移し、`skills/`
直下には残しません。あわせて skill のランタイム依存（`python3`、`pip`、`openpyxl`、
LibreOffice）を確認し、`openpyxl` は不足時にユーザー site-packages へ導入します。詳細は `setup.md` の
「Skill runtime dependencies」を参照してください。

macOS の bootstrap やシステム設定反映を一時的に止める場合:

```sh
AI_AGENT_SETUP_MACOS_BOOTSTRAP=0 AI_AGENT_SETUP_MACOS_SETTINGS=0 sh scripts/setup.sh
```

既存の `~/.zshrc` を symlink へ切り替える初回は、`~/.zshrc` だけを対象に手動で
退避・リンクします（`AI_AGENT_CONFLICT_MODE=replace` は instruction / skill を
含む全 link に効く global フラグのため、この初回切り替えには使いません）。
具体的な手順は `setup.md` の「Shell 設定」を参照してください。

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

## 取り外し

```sh
sh /path/to/ai-agent-config/scripts/uninstall.sh
```

`uninstall.sh` は、このリポジトリが管理する symlink（instruction / skill / シェル設定）だけを `trash` へ移します。ユーザーが手で作った通常ファイルや別 target の symlink は触りません。

## 保守方針

- 構成は `instructions/`、`scripts/`、`notifications/`、`shell/`、必要に応じた `skills/`、最小 docs、CI validation、on-demand PR review workflow に絞ります。
- 初心者向けの coding support は `instructions/AI_AGENT_INSTRUCTIONS.md` の `Coding Collaboration Defaults` に集約し、長い個別プロンプト例を常時ロードしないようにします。
- Instruction の構造を変えたら、`README.md`、`setup.md`、`scripts/validate-repo.sh` も同じ変更で合わせます。
