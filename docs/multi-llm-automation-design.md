# 設計書: マルチLLMによる開発タスク自動化（Historical Note）

この文書は、外部 reviewer を main path に組み込む旧 multi-LLM automation
案の履歴メモです。現行の実装本流はこの設計ではありません。

## 現行の結論

- `multillm_orchestrator.py` は現役ではなく、`self_workflow.py` に置き換え済み
- `response_strategy_bridge.py` は active path から外れている
- startup / phase boundary の brief 引き締めは `refinment` Skill が担う
- 同じ CLI が spec -> implementation -> verification を完了する

## なぜ畳んだか

- 外部 reviewer subprocess を main path に置くと、待ち時間と責務分散が増えやすい
- completion event ごとの cross-LLM continuation は、状態追跡と再入ガードが複雑になりやすい
- 同一 CLI 内で完結する方が、実装責任と完了条件を整理しやすい

## 現在参照すべき文書

- 現行フロー: [self-workflow-hooks.md](./self-workflow-hooks.md)
- 配布と安全設計: [hooks-architecture-review.md](./hooks-architecture-review.md)
- 旧 Codex-hub 移行メモ: [codex-hub-orchestration.md](./codex-hub-orchestration.md)
- 旧 response-strategy 移行メモ: [response-strategy-autonomy.md](./response-strategy-autonomy.md)
