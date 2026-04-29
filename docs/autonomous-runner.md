# Autonomous Runtime

このドキュメントは、**Hook を主オーケストレーターにせず**、非対話 CLI を使って
タスク全体をできるだけ自律的に進める optional runtime を説明します。

## 位置づけ

- shared Hook は引き続き thin guardrail のままです
- 主役は `scripts/autonomous_runner.py` です
- state は会話履歴ではなく外部 JSON に保存します
- 真実は verification step、外部 readback、review thread、check status、必要時の `git` に置きます

この runtime は固定の core phase を回します。

- `work`: LLM worker がタスク本体を進める
- `verify`: typed verification step で検証する
- `sync`: delivery backend に従って成果物を届ける
- `followup`: backend adapter が追加の同期 loop を必要とする時だけ使う

## 一つの抽象化

この runtime の中心は backend 名そのものではなく、各 run で解決される
**delivery capability** です。

delivery capability は次の情報を 1 つにまとめます。

- git が必要か
- work branch が必要か
- local commit までか
- remote push までか
- PR までか
- review fix loop を許すか
- completion を許すか

つまり `workspace`、`branch`、`github_pr` は個別 workflow ではなく、
**同じ core phase に渡す capability の違い**として扱います。

## Core Layer

### 1. Core phase

- `work`
- `verify`
- `sync`
- `followup`

### 2. Delivery plan

`delivery.backend` と `delivery.backends.<name>` から、1 回の run に必要な
delivery capability を解決します。

### 3. Verification registry

verification は `verification.steps` で定義します。step type ごとの execute と
failure rendering は registry に寄せます。

## 対応 CLI

- Codex: `codex exec`
- Claude Code: `claude -p`
- Gemini CLI: `gemini -p`

provider ごとの実行コマンドは config で差し替えられます。

## Security Considerations

- `claude` の既定テンプレートは `--permission-mode bypassPermissions` を含みます。headless self-automation を優先するための明示的な tradeoff なので、使う scope と前提を理解した上で有効化してください。
- `commit_all` は `git add -A` を使います。automation が所有している worktree を前提にしており、未追跡の一時ファイルや secrets を混ぜたくない場合は、worktree を分けるか commit/push をしない backend を使ってください。
- verification の `shell` step は `/bin/sh -c` で実行します。login shell 固有の環境に依存しない、短い check を想定しています。
- `provider_timeout_seconds` を設定すると、provider の無限待ちを避けられます。重い調査で無制限に待ちたい場合だけ `null` のままにしてください。

## v1 の範囲

v1 は optional utility です。

- `setup.sh` には統合しません
- `health-check.sh` にも載せません
- shared Hook の managed layer は増やしません

まずは local repo または local workspace から、手動または scheduler 経由で呼ぶ前提です。

## Config

既定の config path:

```text
~/.ai-agent-config/autonomous-runner.json
```

example:

```json
{
  "version": 4,
  "provider": "codex",
  "base_branch": "main",
  "state_dir": "~/.ai-agent-config/runner",
  "runtime": {
    "branch_prefix": "auto/",
    "max_verification_retries": 2,
    "max_followup_retries": 2,
    "poll_interval_seconds": 20,
    "max_pending_polls": 15,
    "provider_timeout_seconds": null
  },
  "delivery": {
    "backend": "workspace",
    "backends": {
      "workspace": {},
      "branch": {
        "push_branch": false,
        "commit_message_prefix": "Autonomous runtime:"
      },
      "github_pr": {
        "push_branch": true,
        "allow_followup_fixes": false,
        "allow_completion": false,
        "commit_message_prefix": "Autonomous runtime:",
        "pr_title_prefix": "[auto]",
        "completion_method": "squash",
        "review_policy": {
          "require_zero_unresolved_threads": true,
          "required_checks_only": true,
          "min_required_checks": 0
        }
      }
    }
  },
  "verification": {
    "steps": [
      {"type": "shell", "command": "sh scripts/validate-repo.sh"}
    ]
  },
  "providers": {
    "codex": ["codex", "exec", "--cd", "{repo}", "--full-auto", "{prompt}"],
    "claude": ["claude", "-p", "{prompt}", "--permission-mode", "bypassPermissions"],
    "gemini": ["gemini", "-p", "{prompt}", "--approval-mode", "yolo", "--skip-trust"]
  }
}
```

repo にも example を置いてあります。  
[docs/examples/autonomous-runner.example.json](docs/examples/autonomous-runner.example.json)

Markdown 内の JSON も、この example file と同じ shape を保つ前提です。
旧 `workflow` / `validation` 形式や旧 `delivery.*` 直書き形式は、この runtime では明示的に拒否します。

## Delivery Backend

### `workspace`

- verified local work で止まります
- branch 作成、commit、push、PR は runtime が行いません
- non-git directory でも動きます
- Docs / Drive / Notion / Slack / ローカルファイル生成など、repo 外の task に自然です

### `branch`

- verified local work を branch に届けます
- local commit までは共通です
- `delivery.backends.branch.push_branch=false` なら local branch まで
- `delivery.backends.branch.push_branch=true` なら remote branch まで

### `github_pr`

- branch を push して PR を作ります
- 必要なら review fix loop と completion まで進みます
- GitHub は whole-task automation の 1 backend であって、runtime の中心ではありません

## Verification Step

### `shell`

```json
{"type": "shell", "command": "sh scripts/validate-repo.sh"}
```

短い shell check だけなら、string shorthand も使えます。

```json
"sh scripts/validate-repo.sh"
```

### `path_exists`

```json
{"type": "path_exists", "path": "dist/report.md"}
```

relative path は `--repo` で渡した working directory 基準です。

## Provider Env Contract

worker CLI には phase ごとに次の env を渡します。

- `AI_AGENT_STATE_FILE`
- `AI_AGENT_RUNTIME_PHASE`
- `AI_AGENT_DELIVERY_BACKEND`
- `AI_AGENT_WORKDIR`

provider wrapper は prompt 文面ではなく、この env を見て phase-aware に振る舞えます。

## State Shape

state には backend-specific な値を namespaced に保持します。

```json
{
  "delivery_backend": "github_pr",
  "artifacts": {
    "delivery": {
      "github_pr": {
        "name": "auto/20260429-120000",
        "pushed": true,
        "pull_request": {
          "number": 123,
          "url": "https://example.invalid/pr/123"
        }
      }
    }
  },
  "backend_state": {
    "github_pr": {
      "pr_ref": "123",
      "followup_retries": 1,
      "pending_polls": 0
    }
  }
}
```

これにより delivery output も backend runtime state も、backend ごとの schema に閉じ込めます。

## Safe Default

- built-in default は **`workspace`** です
- config が無い状態でも GitHub publication は始まりません
- `branch` や `github_pr` は明示 opt-in です

## Preflight

最初に次を確認してください。

- `workspace` 以外を使うなら、対象が clean worktree であること  
  dirty な repo で使うなら、その変更をこの automation が所有している場合だけ `--allow-dirty` を使います
- provider CLI が実際に使えること  
  Codex / Claude Code / Gemini CLI のうち chosen provider が install 済みで login 済みであること
- `github_pr` backend を使うなら `gh auth status` が通ること
- completion を使うなら branch protection や required checks が整っていること

## よくある設定例

workspace で全体作業を自動化:

```json
{
  "delivery": {
    "backend": "workspace"
  },
  "verification": {
    "steps": [{"type": "shell", "command": "sh scripts/validate-repo.sh"}]
  }
}
```

branch まで届ける:

```json
{
  "delivery": {
    "backend": "branch",
    "backends": {
      "branch": {
        "push_branch": true
      }
    }
  }
}
```

GitHub PR まで届ける:

```json
{
  "delivery": {
    "backend": "github_pr",
    "backends": {
      "github_pr": {
        "allow_followup_fixes": true,
        "allow_completion": false
      }
    }
  }
}
```

completion まで使う場合:

```json
{
  "delivery": {
    "backend": "github_pr",
    "backends": {
      "github_pr": {
        "allow_followup_fixes": true,
        "allow_completion": true,
        "review_policy": {
          "min_required_checks": 1
        }
      }
    }
  }
}
```

## 基本実行

```sh
python3 scripts/autonomous_runner.py run \
  --repo /path/to/workdir \
  --task "必要な判断は自分で行い、実装・検証・必要な外部サービス操作まで自律的に進めて"
```

state file を固定したい場合:

```sh
python3 scripts/autonomous_runner.py run \
  --repo /path/to/workdir \
  --state-file ~/.ai-agent-config/runner/my-run.json \
  --task-file /path/to/task.txt
```

dry run:

```sh
python3 scripts/autonomous_runner.py run \
  --repo /path/to/workdir \
  --task "..." \
  --dry-run
```

JSONL trace:

```sh
python3 scripts/autonomous_runner.py run \
  --repo /path/to/workdir \
  --task "..." \
  --trace-json ~/.ai-agent-config/runner/trace.jsonl
```

resume:

```sh
python3 scripts/autonomous_runner.py run \
  --repo /path/to/workdir \
  --state-file ~/.ai-agent-config/runner/my-run.json
```

## 動作原則

- core phase は fixed に保つ
- backend 名ではなく resolved delivery capability を主語にする
- verification step は registry で増やす
- backend-specific state は namespaced に保つ
- 各 phase は idempotent に近づける
- phase 開始時に毎回 truth を再取得する
- pending check は bounded poll する
- worker は task を進めるが、delivery backend が引き受ける publication は runtime が持つ

## Resume と Exit Code

| 状態 | 挙動 |
|---|---|
| 新規 run (`--state-file` が無い) | 新しい state を作る |
| 既存 `--state-file` を再指定 | その state から resume する |
| repo / provider / base branch / task が食い違う | 既定では拒否する。意図的な時だけ `--force-resume` |
| blocked state を再実行 | 同じ phase から resume し直す |
| terminal state の state file を再実行 | その terminal result を返すだけで再開しない |
| `version != 4` や未知 phase の state file | 旧 schema とみなして拒否する |

| Exit code | 意味 |
|---|---|
| `0` | completed |
| `1` | failed |
| `2` | blocked |

## いつ止まるか

この runtime は、「本当に外部情報が足りないか」「policy で止まるか」「retry budget を使い切ったか」
のときだけ block/failed に寄せます。

provider が返す代表的な blocker class:

- `missing_credentials`
- `ambiguous_target`
- `policy_block`

runtime 自身が返す代表的な blocker class:

- `validation_failure`
- `pending_checks`
- `review_fix_exhausted`
- `review_truth_unavailable`
- `merge_pending`
- `no_changes`
- `missing_pr`
- `review_fix_disabled`
- `non_actionable_merge_blocker`
- `delivery_adapter_missing`

runtime が `failed` として記録する代表 class:

- `provider_error`
- `runtime_error`
- `unknown_phase`

## 注意

- `delivery.backends.github_pr.allow_completion=true` は opt-in にしてください
- 一時 override として `--allow-completion` / `--no-completion` を使うと、その run だけ completion policy を上書きできます
- completion だけでは CI gate になりません。branch protection または `review_policy.min_required_checks` を併用してください
- Claude の `bypassPermissions` や Gemini の `yolo` は strong autonomy 用です。信頼できる repo / 環境だけで使ってください
- Hook はこの runtime の主制御面ではありません
- 長い session 継続ではなく fresh headless call を前提にしています
