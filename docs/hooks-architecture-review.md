# Hooks Architecture Review (2026-04)

## 結論

共有 Hook は **最小・決定的・低遅延** に保ち、自己進行の主役は
instructions と現在の CLI 本体に戻すのが、このリポジトリの標準構成です。

- **配布先はグローバルのみ**（`~/.claude`, `~/.codex`, `~/.gemini`）
- **managed Hook は safety/policy 系だけ**（既定では `safe_delete_guard.py`）
- **仕様整理・実装・検証・セルフレビューは Hook ではなく main session が担当**
- **brief の引き締めは必要時だけ `skills/refinment` を使う**

## なぜこの形にしたか

1. **CLI 共通化を保つため**
   Hook event や継続制御は CLI ごとの差が大きく、薄い guardrail の方が共通 repo に向く。
2. **遅延とデバッグ負荷を減らすため**
   Hook-driven orchestration は便利そうに見えて、状態管理と失敗原因の切り分けを重くしやすい。
3. **責任の所在を明確にするため**
   実装と検証の責任は、作業中の CLI がそのまま持つ方が説明も挙動も素直になる。

## 現行構成

- `safe_delete_guard.py`: 永続削除の防止
- `instructions/HOOKS.md`: minimal Hook policy
- `skills/refinment`: 曖昧な brief の整理

## 非目標

- Hook-driven phase machine
- completion keyword によるタスク進行管理
- managed Hook からの routine な peer-LLM orchestration
