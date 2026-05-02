# Codex Automation Daily Review

日次 LLM 履歴 instruction review のスケジューラは Codex App Automations です。
定期実行の schedule、prompt、run history、sandbox mode、model、findings を
Codex app 側で一体管理します。

公式リファレンス: <https://developers.openai.com/codex/app/automations>

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

最初の数回は Codex app の Automations pane で結果を確認します。
確認すること:

- recent Claude Code / Codex / Gemini CLI history sources を読めている
- repository edits が documented scope に収まっている
- edits がある場合に validation が通っている
- edits がある場合に PR が作成され、review feedback が解消され、clean な状態で
  merge まで完了している
- unreadable sources を raw logs としてコピーせず、要約で報告している
