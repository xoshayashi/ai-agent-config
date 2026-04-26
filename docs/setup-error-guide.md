# Setup Error Guide

Use this guide when setup, update, scheduling, or uninstall fails. Explain errors in plain Japanese first, then suggest the smallest safe next step.

## Common Errors

| Error Signal | Plain Japanese Explanation | Safe Next Step |
|---|---|---|
| `command not found: git` | GitHubから設定ファイルを取得するためのGitが入っていません。 | Gitをインストールしてから、同じ自然言語セットアップ依頼をもう一度実行します。 |
| GitHub authentication failed | GitHubにログインできていないか、private repositoryを読む権限がありません。 | GitHub CLIやブラウザ認証でログインし、対象リポジトリへアクセスできるか確認します。 |
| `target exists but is not a git repository` | 設定リポジトリを置こうとした場所に、Git管理ではない別フォルダーがあります。 | 別の保存先を使うか、そのフォルダーの中身を確認してから安全に退避します。 |
| `path already exists` | リンクを作りたい場所に同名のファイルやフォルダーがあります。 | 標準ではバックアップ先へ退避します。上書きせず、何が退避されるか説明します。 |
| `permission denied` / `operation not permitted` | 選んだフォルダーに書き込む権限がない、またはOSの保護が効いています。 | `~/Documents/projects` などユーザー所有の作業フォルダーを推奨します。OS権限が必要な場所へのセットアップは避けます。 |
| `could not apply delete protection` | macOSの削除防止設定をリンクに付けられませんでした。リンク作成自体は成功している場合があります。 | まずリンクが読めるか確認します。削除防止が必須でなければ継続できます。 |
| `trash is required for safe uninstall` | 安全に元へ戻すための `trash` コマンドが見つかりません。 | 完全削除はせず、`trash` をインストールするか、手動でゴミ箱へ移す方法を案内します。 |
| `config repository has local changes` | 設定リポジトリに未保存の変更があり、更新すると作業を壊す可能性があります。 | 変更内容を確認し、必要ならコミットまたは退避してから更新します。 |
| `not a git repository` | 更新対象がGitリポジトリではありません。 | 正しい `ai-agent-config` の場所を探すか、GitHubから再取得します。 |
| `AI_AGENT_TARGET_DIR is not set` | どの作業フォルダーへリンクを置くか決まっていません。 | 推奨は `~/Documents/projects`。既存の作業フォルダーや会社指定workspaceがあればそちらを選びます。 |
| `launchctl` or `systemctl` scheduling failed | 自動更新のスケジュール登録に失敗しました。設定本体は使える場合があります。 | まず手動更新コマンドを案内します。自動更新はOS別に再確認します。 |
| `health: warn` | 基本動作は確認できましたが、未ログイン、未インストール、リンク未設定、リポジトリ未保存変更など確認が必要な項目があります。 | `scripts/health-check.sh` の各行を見て、最も小さい修正だけを提案します。 |
| `health: fail` | Gitや設定リポジトリなど、更新や診断に必要な前提が見つかりません。 | リポジトリの場所、Gitの有無、GitHubからの再取得が必要かを確認します。 |

## Response Pattern

1. **何が起きたか**を1から2文で説明する。
2. **ユーザーのファイルが失われていないか**を確認する。
3. **安全な次の一手**を1つ提示する。
4. 迷う場合は `AI_AGENT_DRY_RUN=1` で再確認する。

## Safety Rules

- Do not suggest permanent deletion.
- Use `trash` for cleanup and uninstall.
- Prefer user-owned folders such as `~/Documents/projects` over system or application directories.
- If a command failed because knowledge may be outdated, check the official CLI or GitHub documentation before retrying.
