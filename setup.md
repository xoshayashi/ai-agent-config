# Setup

このリポジトリは、Claude Code / Codex / Gemini CLI のグローバル instruction files、共有 skill links、シェル設定 (`~/.zshrc`) を管理します。

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
| `~/.zshrc` | `shell/.zshrc` |

## 基本コマンド

```sh
sh scripts/setup.sh
sh scripts/health-check.sh
sh scripts/update.sh
sh scripts/uninstall.sh
```

`setup.sh` は Claude Code / Codex / Gemini CLI が未インストールでも止まりません。
CLI の導入状態は `sh scripts/health-check.sh` で確認します。

## macOS bootstrap

macOS では `setup.sh` が先に Command Line Tools と Homebrew を確認し、無ければ
インストールを開始します。その後、`.zshrc` が参照する次の Homebrew formula を
入れます。

- `zsh-autosuggestions`
- `fzf`
- `zoxide`
- `starship`
- `zsh-syntax-highlighting`
- `displayplacer`
- `git`
- `gh`
- `hf`
- `mas`
- `python`（`python3` / `pip3` / `pip`）
- `pipx`
- `gemini-cli`

`colab-cli` は Homebrew formula が無いため、`pipx` で Python CLI として入れます。
既に入っている場合は PyPI の最新 version と比較し、更新がある場合だけ
`pipx upgrade colab-cli` を実行します。

Codex CLI は公式推奨の standalone installer で入れます。既存の Homebrew
`codex` cask がある場合は外し、`~/.local/bin/codex` の launcher を使います。
Claude Code は公式推奨の Native Install で入れます。既存の Homebrew
`claude-code` / `claude-code@latest` cask がある場合は外し、`~/.local/bin/claude`
の launcher を使います。Gemini CLI は公式 README にある Homebrew formula
`gemini-cli` で入れます。

あわせて、次のアプリを cask で入れます。Dia は Homebrew の cask token が
`thebrowsercompany-dia` なので、この名前で管理します。

- `chatgpt`
- `claude`
- `displaylink`
- `gcloud-cli`
- `slack`
- `tailscale-app`
- `thebrowsercompany-dia`
- `google-chrome`
- `google-drive`
- `docker-desktop`
- `visual-studio-code`
- `libreoffice`
- `maccy`
- `ollama-app`
- `zoom`

Antigravity CLI は公式 installer で `agy` を入れ、既に入っている場合は
`agy update` で更新します。Perplexity は Mac App Store app のため、`mas` で
App Store 版（app id `1668000334`）を入れます。

`chatgpt`、`claude`、`codex`、`displaylink`、`docker-desktop`、`google-drive`、`tailscale-app`、`zoom` は installer や symlink
作成で管理者権限を要求します。
`setup.sh` が非対話セッションから実行されている場合は、該当コマンドだけを
Terminal.app で開き、通常のターミナル上の `sudo` プロンプトでパスワードを
入力できるようにします。完了するまで `setup.sh` は待機します。

既に Homebrew 管理下にある formula / cask は、`brew outdated` で更新がある場合
だけ `brew upgrade` を実行します。更新が無い場合は `ok` として通過します。

## Manual auth steps

`setup.sh` は `gh`、`gcloud`、`hf` のログイン状態を確認します。未ログインの場合、
認証そのものは自動実行せず、次のような手動コマンドを表示します。

```sh
gh auth login
gcloud auth login
hf auth login
```

認証チェックの表示を止める場合:

```sh
AI_AGENT_SHOW_AUTH_STEPS=0 sh scripts/setup.sh
```

bootstrap だけ止める場合:

```sh
AI_AGENT_SETUP_MACOS_BOOTSTRAP=0 sh scripts/setup.sh
```

## macOS system settings

`setup.sh` は、現在のマシンから取得した再適用可能な設定を `defaults`、`pmset`、
`displayplacer` で反映します。対象は `macos/defaults/*.plist` に保存した
GlobalDomain、キーボードショートカット、入力ソース、トラックパッド/マウス、Dock、
Finder、スクリーンショット、Window Manager、Control Center、Terminal などの基本設定、
電源設定、ディスプレイ配置です。

defaults snapshot を更新する場合は、対象 domain を `defaults export <domain>
macos/defaults/<domain>.plist` で保存し、`plutil -convert xml1` と `plutil -lint` で
検証してください。最近使った項目、履歴、analytics timestamp などの揮発情報は
保存対象から外します。

ディスプレイ配置は `macos/displays/current.sh` に保存しています。接続する
ディスプレイが変わった場合は、`displayplacer list` の末尾に出る現在配置コマンドで
このファイルを更新してください。

システム設定反映だけ止める場合:

```sh
AI_AGENT_SETUP_MACOS_SETTINGS=0 sh scripts/setup.sh
```

## Conflict Handling

既存ファイルがある場合、`AI_AGENT_CONFLICT_MODE` で挙動を変えられます。

| Value | Behavior |
|---|---|
| `skip` | 既存 path を残して skip |
| `fail` | 既存 path があれば失敗 |
| `replace` | 既存 path を backup folder へ移してから link 作成。skill は `~/.codex/skill-backups/`、`~/.claude/skill-backups/`、`~/.gemini/skill-backups/`、旧 `~/.agents/skill-backups/` に逃がし、`skills/` 直下には置きません。 |

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

## Skill runtime dependencies

一部の skill はスクリプト実行用に外部ランタイムを使います。`setup.sh` は
これらの存在を確認します。macOS bootstrap が有効な場合、`openpyxl` は
`python3 -m pip install --user --break-system-packages` でユーザー site-packages へ
自動インストールし、LibreOffice は cask として自動インストール対象です。状態は
`sh scripts/health-check.sh` の
`skill dependencies:` 行でも確認できます。

| 依存 | 区分 | 用途 | 不足時の対応 |
|---|---|---|---|
| `python3` / `pip` / `pip3` | 必須 | skill スクリプト（財務モデリング、スライド packaging）の実行と Python package 導入 | macOS は `brew install python` |
| `openpyxl` | 必須 | `startup-financial-modeling` の xlsx 生成 | `setup.sh` がユーザー site-packages へ導入 |
| LibreOffice (`soffice`) | 任意 | xlsx の再計算検証、スライドの PDF レンダリング | `brew install --cask libreoffice` |
| ImageMagick (`convert`)・画像生成 API | 任意 | スライド画像 skill の個別処理 | 各 skill の手順に従って個別に用意 |

LibreOffice は macOS Homebrew では `soffice` という名前で入りますが、skill は
`libreoffice` という名前で探します。`setup.sh` は `soffice` が見つかり
`libreoffice` が無い場合、`soffice` と同じディレクトリに `libreoffice` の
互換 symlink を作成します。このため `brew doctor` が unexpected symlink として
警告することがありますが、これは意図的なものです。互換 symlink を手動で外す
場合は `trash /opt/homebrew/bin/libreoffice` を使います。

## Shell 設定

`setup.sh` は `shell/.zshrc` を `~/.zshrc` にリンクします。`.zshrc` の正本は
このリポジトリにあり、編集はリポジトリ側で行います。

既存の `~/.zshrc` が通常ファイルとして残っていると、既定 (`skip`) では
リンクが作られません。`AI_AGENT_CONFLICT_MODE=replace` は instruction や
skill を含む全 link 対象に効く global フラグなので、`~/.zshrc` だけを初めて
切り替えるときは、対象を絞って手動で退避・リンクします。

```sh
cd /path/to/ai-agent-config
mv ~/.zshrc ~/.zshrc.backup-$(date +%Y%m%d-%H%M%S)
ln -s "$(pwd)/shell/.zshrc" ~/.zshrc
```

以降は `sh scripts/setup.sh`（既定の `skip` モード）が、正しい symlink に
なった `~/.zshrc` をそのまま検出します。`sh scripts/health-check.sh` の
`shell: zshrc=ok` で状態を確認できます。

## 通知 hook

`setup.sh` は通知 hook も設定します。各 CLI がターンを終えたとき、入力や承認を
待つときに、共有スクリプト `notifications/notify.sh` がデスクトップ通知（macOS）
または端末ベル（その他 OS）を出します。

| CLI | 設定ファイル | イベント |
|---|---|---|
| Claude Code | `~/.claude/settings.json` | `Stop` / `Notification` |
| Codex | `~/.codex/hooks.json` | `Stop` / `PermissionRequest` |
| Gemini CLI | `~/.gemini/settings.json` | `AfterAgent` / `Notification` |

`~/.claude/settings.json` と `~/.gemini/settings.json` は通知以外の設定も持つため、
`scripts/install-notifications.py` が hook 部分だけを冪等にマージします（書き換え前に
`*.bak-<timestamp>` を作成）。`~/.codex/hooks.json` は hook 専用ファイルとして
生成します。`python3` が無い環境では、この処理は skip されます。

除去は `uninstall.sh` が同じヘルパーで行い、このリポジトリが入れた hook だけを
外します。`AI_AGENT_DRY_RUN=1` を付けると、設定を書き換えずにマージ差分を表示します。
