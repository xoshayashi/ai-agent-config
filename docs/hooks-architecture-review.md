# Hooks Architecture Review (2026-04)

## このドキュメントの位置付け

- **読者:** AI エージェントツール（Claude Code / Codex / Gemini CLI）の挙動を変えたい人。プログラミング経験は問いません。
- **前提:** このリポジトリで配布している Hook（CLI が特定のタイミングで自動実行する小さなスクリプト）の構成が、なぜ今の形になっているかを知りたい人向け。
- **読み終えて分かること:** 旧構成と現行構成の違い、現行構成を選んだ理由、現行構成で動いている部品の名前と役割。
- **関連:** 実装の手順詳細は [self-workflow-hooks.md](./self-workflow-hooks.md)。

## 結論

旧構成（project + user の二重配布、つまり「リポジトリ単位」と「PC 全体」の両方に Hook を入れる方式）と、旧 multi-LLM continuation 案（複数の LLM を経由して作業を続ける方式）は、重複実行・責務分散・待ち時間増加を起こしやすいため、次の単純構成に整理しました。

- **配布先はグローバルのみ**（PC 全体の設定。`~/.claude`, `~/.codex`, `~/.gemini`）
- **常時ガードは安全系を優先**（`safe_delete_guard.py` = `rm` を `trash` に置き換える保護 Hook）
- **自己完結フローは `self_workflow.py` に一本化**（同じ CLI が仕様 → 実装 → 検証まで責任を持つ）
- **Hook ロジック本体はリポジトリ管理し、`$AI_AGENT_HOOKS_RUNTIME_LINK` から参照**（CLI 設定は安定リンク経由で本体を呼び出す）

## なぜこの形にしたか

1. **重複実行を減らすため**
   Hook の管理レイヤー（Hook をどこに置くか）を 1 つに固定し、project/user の多重登録（同じ Hook が2回走る状況）を避ける。
2. **責任の所在を明確にするため**
   作業を始めた CLI 自身が仕様、実装、検証まで継続する。
3. **待ち時間を抑えるため**
   外部 reviewer subprocess（別プロセスで動くレビュー LLM）を main path から外し、必要時だけ
   `refinment`（指示文を引き締めるための Skill）で brief を締める。

## 現行構成

- `safe_delete_guard.py`: 永続削除の防止（`rm -rf` などをブロックして `trash` に誘導）
- `self_workflow.py`: spec -> implementation -> verification の phase loop（仕様→実装→検証の自己継続ループ）
- `skills/refinment`: startup / phase boundary の brief tightening（開始時や段階の切れ目で指示文を整える Skill）
- `instructions/.github/copilot-instructions.md`: Copilot 向け canonical instructions（GitHub Copilot 用の正本。**repo-local 運用、Hook runtime なし** = リポジトリ単位で配置するだけで、自動 Hook の対象には入れない）

この構成は Codex, Claude Code, Gemini CLI で共通です。違いは Hook event
名（CLI ごとに通知タイミングの呼び方が違う点）だけで、ライフサイクル自体は `instructions/HOOKS.md` に揃えています。

GitHub Copilot はこの Hook runtime 構成には入りません。現行実装で共有して
いるのは instructions の source of truth（指示文の正本）だけです。

## 残るトレードオフ

- project 固有 Hook を別途運用するなら、global は安全系・共通系、
  project は業務固有、という役割分担を明示する必要がある
- 完全な一元統制が必要な環境では、OS 管理ポリシーや managed settings
  （企業管理の設定配布機構）との併用設計が必要

## 参照

- 現行設計: [self-workflow-hooks.md](./self-workflow-hooks.md)
