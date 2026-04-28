# Self-Workflow Hooks (2026-04)

## このドキュメントの位置付け

- **読者:** Claude Code / Codex / Gemini CLI で AI エージェントに「仕様 → 実装 → 検証」と段階的に作業させたい人。プログラミング経験は問いません。
- **前提:** [hooks-architecture-review.md](./hooks-architecture-review.md) の結論（Hook = CLI が自動実行する小さなスクリプト、配布先はグローバルのみ）を読んだ前提で、その自己継続フローの中身を説明します。
- **読み終えて分かること:** どの CLI でどのイベント名で動くか、どの完了キーワードで段階が切り替わるか、暴走を防ぐための安全装置として何が用意されているか。

## Goal

Use Hooks so the current LLM CLI can finish its own work without handing the
main path to another model.

> 補足: 別のモデルにバトンを渡さず、作業を始めた **その CLI 自身が最後まで責任を持つ** ための仕組みです。

This runtime currently covers Codex, Claude Code, and Gemini CLI. GitHub
Copilot shares the same canonical instructions source, but it is not part of
the managed Hook or self-workflow runtime path.

The shared pattern is:

1. the user sends a task to Codex, Claude Code, or Gemini CLI
2. the startup hook injects a specification-first brief（最初に「仕様書から書け」と指示を差し込む）
3. the CLI optionally uses `refinment` when the prompt or phase brief really
   needs tightening（指示文を整える Skill。必要なときだけ呼ぶ）
4. completion hooks decide whether to stop or auto-continue that **same CLI**（完了タイミングの Hook が、止めるか同じ CLI を再起動するかを決める）
5. the loop ends only after verification evidence is present（検証の証拠が揃って初めてループ終了）

The runtime uses a generic intent split: answer-only turns usually stay
outside this loop, while artifact/execution turns can enter it when they need
bounded multi-step work.
If a loop is already active, non-follow-up turns outside that path should end
the active loop state so stale continuations do not fire on the next stop
event.

> 補足: 単に質問に答えるだけのターン（answer-only）は通常このループに乗りません。何かを作ったりコマンドを実行したりするターン（artifact/execution）だけが、必要に応じてループに入ります。

## Active Runtime

- Hook script: `hooks/scripts/self_workflow.py`
- Supporting skill: `skills/refinment/`
- State root: `~/.llm-config/self-workflow`（セッションごとの状態を保存する場所）
- Shared lifecycle rules: `instructions/HOOKS.md`

This is the current main path. External reviewer subprocesses are not part of
the default flow.

## Event Mapping

| CLI | Startup event（開始合図） | Completion event（完了合図） |
|---|---|---|
| Codex | `UserPromptSubmit` / `SessionStart` | `Stop` |
| Claude Code | `UserPromptSubmit` | `Stop`, `SubagentStop` |
| Gemini CLI | `BeforeAgent` | `AfterAgent` |

The hook injects context on startup and returns a continuation prompt on
completion when more work is needed.

> 補足: 開始合図で「次に何をすべきか」を CLI に伝え、完了合図で「まだ続きが必要か」を判定して継続プロンプトを返します。

## Phase Flow

1. **Specification authoring**（仕様書を書くフェーズ）
   The CLI drafts the spec itself. `refinment` is optional and should stay
   sparse.
2. **Specification review gate**（仕様レビューのゲート）
   `[[SPEC_DONE]]` or a structured fallback draft moves the task into a tighter
   spec pass.
3. **Implementation**（実装フェーズ）
   The CLI continues step by step and uses `refinment` only when the next step
   or verification-readiness decision is unclear.
4. **Verification**（検証フェーズ）
   `[[IMPLEMENTATION_DONE]]` is only a handoff into verification, not final
   completion. If verification finds only a narrow omission, respond with the
   correction delta instead of restating the full earlier answer. Plain
   "updated files" status text should not trigger that stricter delta mode.
5. **Done**（完了）
   Completion requires `[[VERIFICATION_DONE]]` plus `[[TASK_DONE]]`, or a
   structured `phase_signal="task_complete"` packet with real evidence.

> 補足: `[[SPEC_DONE]]` などの二重角括弧キーワードは、CLI 出力の中で「ここでフェーズが切り替わる」と Hook 側に明示的に伝えるための合図です。

## Safety Design

- recursion guard: `AI_AGENT_SELF_WORKFLOW_ACTIVE=1`（再帰ループ防止のフラグ）
- bounded continuation count and repeated-prompt caps（自動継続の回数と、同じプロンプト連発の上限）
- bounded verification-turn caps（検証フェーズが永遠に続くのを防ぐ上限）
- session-scoped local state（セッションごとに分離されたローカル状態）
- fail-open behavior for unsupported or non-qualifying turns（対象外のターンは Hook を素通りさせる）

## Design Intent

- keep execution ownership inside the current CLI
- keep prompt tightening visible to the user
- avoid routine cross-LLM reviewer latency
- reuse one lifecycle across Codex, Claude Code, and Gemini CLI

## Related Docs

- Current architecture summary: [hooks-architecture-review.md](./hooks-architecture-review.md)
