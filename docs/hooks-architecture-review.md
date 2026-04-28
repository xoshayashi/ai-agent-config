# Hooks Architecture Review (2026-04)

## 結論

旧構成（project + user の二重配布）と旧 multi-LLM continuation 案は、
重複実行・責務分散・待ち時間増加を起こしやすいため、次の単純構成に
整理しました。

- **配布先はグローバルのみ**（`~/.claude`, `~/.codex`, `~/.gemini`）
- **常時ガードは安全系を優先**（`safe_delete_guard.py`）
- **自己完結フローは `self_workflow.py` に一本化**
- **Hook ロジック本体はリポジトリ管理し、`$AI_AGENT_HOOKS_RUNTIME_LINK` から参照**

## なぜこの形にしたか

1. **重複実行を減らすため**
   Hook の管理レイヤーを 1 つに固定し、project/user の多重登録を避ける。
2. **責任の所在を明確にするため**
   作業を始めた CLI 自身が仕様、実装、検証まで継続する。
3. **待ち時間を抑えるため**
   外部 reviewer subprocess を main path から外し、必要時だけ
   `refinment` で brief を締める。

## 現行構成

- `safe_delete_guard.py`: 永続削除の防止
- `self_workflow.py`: spec -> implementation -> verification の phase loop
- `skills/refinment`: startup / phase boundary の brief tightening

この構成は Codex, Claude Code, Gemini CLI で共通です。違いは Hook event
名だけで、ライフサイクル自体は `instructions/HOOKS.md` に揃えています。

## 残るトレードオフ

- project 固有 Hook を別途運用するなら、global は安全系・共通系、
  project は業務固有、という役割分担を明示する必要がある
- 完全な一元統制が必要な環境では、OS 管理ポリシーや managed settings
  との併用設計が必要

## 参照

- 現行設計: [self-workflow-hooks.md](./self-workflow-hooks.md)
