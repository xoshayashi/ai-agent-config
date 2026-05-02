# Codex Automation Daily Review

日次 LLM 履歴 instruction review の推奨スケジューラは Codex App
Automations です。古い macOS `launchd` installer は fallback として残しますが、
新規セットアップでは、定期実行の schedule、prompt、run history、sandbox mode、
model、findings を Codex app 側で一体管理します。

公式リファレンス: <https://developers.openai.com/codex/app/automations>

## `launchd` から移す理由

OS job は macOS background permission、shell environment、`launchd` からの
filesystem access に依存します。Codex App Automations に寄せると、定期実行の
管理面が Codex 側にまとまり、run の確認も Automations pane / Triage で扱えます。

この repository には既存 schedule を外すための `launchd` scripts も残します。
Codex automation が有効になった後で外してください。

```sh
./scripts/uninstall-daily-llm-history-instruction-review
```

## Codex Automation を作る

Codex app が起動しており、この project が disk 上で利用できる状態にします。
以下の `/path/to/ai-agent-config` は、この repository の local checkout path に
置き換えてください。

この repository を Codex app で開きます。

```sh
codex app /path/to/ai-agent-config
```

その app thread で、次の内容を Codex に依頼します。

```text
Create a standalone project automation.

Name: ai-agent-config daily LLM history instruction review
Project: /path/to/ai-agent-config
Schedule: daily at 00:00 local time.
Custom schedule if needed: 0 0 * * *
Execution environment: use a dedicated worktree if available; otherwise use the
local project and preserve user work.
Model and reasoning: default.

Prompt:
Use the `$daily-llm-history-instruction-review` skill.

If any repository changes are made, complete the GitHub closeout before ending:
create or continue a branch named
`daily-llm-history-instruction-review-YYYYMMDD`, commit only the intended
changes, push it, open a pull request against `main`, add `codex` and
`codex-automation` labels when available, monitor checks and review comments,
address actionable feedback, mark the PR ready when clean, squash merge it, and
delete the remote branch. If no repository files changed, do not open a PR.
```

別時刻にする場合は Codex app の schedule UI で調整します。custom cadence を使う
場合、公式 docs は cron syntax を指定すると説明しています。

## 初回 Run の確認

OS schedule を外す前に、最初の数回は Codex app の Automations pane で結果を確認します。
確認すること:

- recent Claude Code / Codex / Gemini CLI history sources を読めている
- repository edits が documented scope に収まっている
- edits がある場合に validation が通っている
- edits がある場合に PR が作成され、review feedback が解消され、clean な状態で
  merge まで完了している
- unreadable sources を raw logs としてコピーせず、要約で報告している

Codex automation が active になり、少なくとも 1 回よい run が完了したら、
legacy `launchd` schedule を外します。

```sh
./scripts/uninstall-daily-llm-history-instruction-review
```

## Fallback

その machine で Codex App Automations が使えない場合のみ、legacy installer で
macOS schedule を登録できます。

```sh
./scripts/install-daily-llm-history-instruction-review
```

fallback は trusted local environment でのみ使います。`launchd` logs に
`Operation not permitted` が出る場合は、macOS privacy settings で該当 app /
shell に project folder へのアクセス権を付与するか、Codex automation に移行します。
legacy `launchd` fallback は local review 用で、PR 作成や merge closeout は
Codex App Automation 側で行います。
