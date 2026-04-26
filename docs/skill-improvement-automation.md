# Skill Improvement Automation

この自動化は、Claude Code、Codex、Gemini CLIの利用ログから **Skillで吸収すべき改善点** を見つけ、改善提案、PR作成、Claudeレビュー対応、条件付き自動マージまでをつなぐためのローカル運用です。

## Feasibility / 実現可能性

| 領域 | 判定 | 理由 |
|---|---:|---|
| **CLIログの定期チェック** | 可能 | ログは各ユーザーPCのローカル領域にあるため、`launchd` または `systemd` のユーザータイマーで定期実行できます。 |
| **GitHub Actionsだけでのログ収集** | 不可 | GitHub-hosted runnerはユーザーPC上のClaude Code、Codex、Gemini CLIログへアクセスできません。GitHub Actionsの `schedule` は既定ブランチ上で定時実行できますが、対象はGitHub側の環境です。 |
| **改善提案PRの作成** | 可能 | `gh pr create` はタイトル、本文、base/head指定に対応しており、非対話のPR作成に使えます。 |
| **Claudeレビュー後の自動改善** | 条件付きで可能 | ローカルの `claude -p` と `gh` が使え、対象PRブランチをチェックアウトできる場合に実行できます。 |
| **自動マージ** | 条件付きで可能 | `gh pr merge --auto --match-head-commit <SHA>` により、要件が満たされた時だけマージ予約できます。未解決レビュー、失敗チェック、Draft、競合がある場合は止めます。 |

**結論:** 生ログをGitHubへ集めるのではなく、**各ユーザーPCでローカルに抽出・匿名化し、改善提案だけをPR化する** 方式が現実的で安全です。

## Architecture / 全体像

```text
Local LLM CLI logs
  -> scripts/skill-improvement-bot.py scan
  -> redacted skill-improvement report
  -> optional LLM patch pass
  -> scripts/validate-repo.sh
  -> gh pr create
  -> Claude Code Review workflow
  -> skill-improvement-bot.py review-open-prs
  -> optional Claude feedback pass
  -> gh pr merge --auto --match-head-commit
```

## Safety Defaults / 安全設計

- **生ログはコミットしない:** PRに入るのは `reports/skill-improvement/*.md` の匿名化済み要約だけです。
- **秘密情報は伏せる:** API key、GitHub token、メールアドレス、長いハッシュ、ユーザーホームパスは redaction の対象です。
- **スニペットは高プライバシーモードでPR化しない:** `AI_AGENT_IMPROVEMENT_INCLUDE_SNIPPETS=1` はローカル確認向けです。既定の `AI_AGENT_IMPROVEMENT_PRIVACY_MODE=high` では、スニペット入りレポートをPR化しようとすると停止します。
- **外部LLMへの送信は任意:** Skill本文を自動修正する処理は `AI_AGENT_IMPROVEMENT_LLM` を指定した時だけ動きます。
- **PR作成も任意:** `AI_AGENT_IMPROVEMENT_CREATE_PR=1` を設定しない限り、定期実行はローカルレポート生成に留まります。
- **自動マージはさらに任意:** `AI_AGENT_IMPROVEMENT_AUTO_MERGE=1` を設定した場合のみ、信頼済みレビュー作者、チェック、未解決スレッド、Draft、競合を確認してからマージ予約します。

## Manual Commands / 手動実行

ログから改善候補を確認します。

```sh
python3 scripts/skill-improvement-bot.py scan
```

JSONで確認します。

```sh
python3 scripts/skill-improvement-bot.py scan --json
```

レポートを作成します。

```sh
python3 scripts/skill-improvement-bot.py run
```

`reports/` は通常のgit状態には出さないため `.gitignore` に入っています。PR作成時は、botがその実行で作った対象レポートだけを明示的にstageします。

改善提案をPRにします。

```sh
AI_AGENT_IMPROVEMENT_CREATE_PR=1 \
python3 scripts/skill-improvement-bot.py run
```

PRレビュー状態を確認します。

```sh
python3 scripts/skill-improvement-bot.py review-pr <PR_NUMBER>
```

Claudeレビュー対応と自動マージまで有効にします。

```sh
AI_AGENT_IMPROVEMENT_APPLY_REVIEW=1 \
AI_AGENT_IMPROVEMENT_AUTO_MERGE=1 \
python3 scripts/skill-improvement-bot.py review-open-prs
```

## Scheduling / 定期実行

推奨は **1日1回** です。頻度はセットアップ時の対話で決められます。

| 選択肢 | 設定 | 用途 |
|---|---|---|
| **1日1回（推奨）** | `AI_AGENT_IMPROVEMENT_CADENCE=daily` | 通常運用 |
| **1週間ごと** | `AI_AGENT_IMPROVEMENT_CADENCE=weekly` | 改善PRの頻度を抑えたい場合 |
| **手動のみ** | `AI_AGENT_IMPROVEMENT_CADENCE=manual` | 自動スキャンを止める場合 |
| **カスタム** | `AI_AGENT_IMPROVEMENT_CADENCE=custom AI_AGENT_IMPROVEMENT_INTERVAL_SECONDS=<seconds>` | 管理者向け |

dry-runで予定内容を確認します。

```sh
AI_AGENT_DRY_RUN=1 sh scripts/schedule-skill-improvement.sh
```

1日1回で設定します。

```sh
AI_AGENT_IMPROVEMENT_CADENCE=daily sh scripts/schedule-skill-improvement.sh
```

PR作成まで自動化する場合は、`gh auth status` が成功する状態で次を設定します。

```sh
AI_AGENT_IMPROVEMENT_CREATE_PR=1 \
AI_AGENT_IMPROVEMENT_LLM=claude \
AI_AGENT_IMPROVEMENT_CADENCE=daily \
sh scripts/schedule-skill-improvement.sh
```

レビュー対応とマージ予約まで有効にする場合だけ、次を追加します。

```sh
AI_AGENT_IMPROVEMENT_APPLY_REVIEW=1 \
AI_AGENT_IMPROVEMENT_AUTO_MERGE=1 \
AI_AGENT_IMPROVEMENT_CREATE_PR=1 \
AI_AGENT_IMPROVEMENT_LLM=claude \
AI_AGENT_IMPROVEMENT_CADENCE=daily \
sh scripts/schedule-skill-improvement.sh
```

## Environment Variables / 環境変数

| 変数 | 既定値 | 意味 |
|---|---|---|
| `AI_AGENT_LOG_DAYS` | `14` | 何日前までのログを見るか |
| `AI_AGENT_LOG_MAX_FILES` | `300` | 1回で読む最大ファイル数 |
| `AI_AGENT_LOG_MAX_BYTES` | `120000` | 各ログファイル末尾から読む最大バイト数 |
| `AI_AGENT_LOG_ROOTS` | 空 | 追加ログルート。複数はOSのパス区切りで指定 |
| `AI_AGENT_LOG_ROOTS_ONLY` | `0` | `1` で既定ログルートを読まず、`AI_AGENT_LOG_ROOTS` だけを対象にする |
| `AI_AGENT_IMPROVEMENT_INCLUDE_SNIPPETS` | `0` | `1` でローカルレポートに短いredacted snippetを含める |
| `AI_AGENT_IMPROVEMENT_PRIVACY_MODE` | `high` | `high` ではsnippet入りレポートのPR化を止める |
| `AI_AGENT_IMPROVEMENT_CREATE_PR` | `0` | `1` で改善提案PRを作成 |
| `AI_AGENT_IMPROVEMENT_LLM` | 空 | `claude`、`codex`、`gemini` のいずれかで改善パッチを自動生成 |
| `AI_AGENT_IMPROVEMENT_APPLY_REVIEW` | `0` | `1` でClaudeレビューの指摘対応を試みる |
| `AI_AGENT_IMPROVEMENT_AUTO_MERGE` | `0` | `1` で条件成立時に自動マージ予約 |
| `AI_AGENT_TRUSTED_REVIEW_AUTHORS` | `claude,claude-code` | 自動レビュー対応・自動マージで信頼するGitHub loginの完全一致リスト |
| `AI_AGENT_IMPROVEMENT_ALLOW_DIRTY` | `0` | `1` でclean worktreeガードを解除。自動化が現在の変更を全て所有している時だけ使う |
| `AI_AGENT_IMPROVEMENT_CADENCE` | `daily` | 定期実行の頻度 |

## Health Check / 状態確認

`scripts/health-check.sh` は、Skill改善スケジューラが `active`、`installed`、`missing`、`unsupported` のどれかを出します。

```sh
sh scripts/health-check.sh
```

Windowsではこのリポジトリのスケジューラは未対応です。PowerShell運用では手動実行、またはWSL上で `scripts/schedule-skill-improvement.sh` を使ってください。

## What Counts As A Signal / 改善シグナル

改善候補は、次のような流れを見た時だけ抽出します。

1. 会話ログ中で対象Skill名やSkillパスに近い表現が出る。
2. その後に「修正」「漏れ」「足りない」「もう一回」「did you」「missing」「fix」など、Skill実行後の追加修正らしい発話が続く。
3. その内容を `activation`、`evidence`、`search`、`delegation`、`formatting`、`validation`、`privacy`、`pr-review` などへ分類する。
4. 生の発話ではなく、抽象化した改善提案としてレポート化する。

これは完全な自動評価ではありません。**誤検知を前提に、PRレビューと検証を必ず通す設計** です。

## Source Notes / 参照

- GitHub CLIの `gh pr create` は非対話PR作成に必要な `--title`、`--body`、`--base`、`--head` を持ちます: <https://cli.github.com/manual/gh_pr_create>
- GitHub CLIの `gh pr merge` は `--auto` と `--match-head-commit` を持ち、条件成立後のマージ予約とhead SHA固定に使えます: <https://cli.github.com/manual/gh_pr_merge>
- GitHub Actionsの `schedule` はGitHub側の既定ブランチで走るため、ユーザーPCのローカルログ収集には向きません: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule>
- Gemini CLIは `--prompt` / `-p` によるheadless modeを持ち、スクリプト実行に使えます: <https://google-gemini.github.io/gemini-cli/docs/cli/headless.html>
- Claude Codeは `claude -p`、`--output-format`、`--permission-mode` を持ち、非対話処理と権限モード指定に使えます: <https://code.claude.com/docs/en/cli-usage>
