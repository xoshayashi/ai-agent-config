# Hooks Architecture Review (2026-04)

## 結論

旧構成（project + user の二重配布）は、重複実行と設定競合を起こしやすいため、次の単純構成に変更しました。

- **配布先はグローバルのみ**（`~/.claude`, `~/.codex`, `~/.gemini`）
- **常時ガードは安全系を優先し、Codex orchestration は qualifying-task 判定で制御**（`safe_delete_guard.py`, `multillm_orchestrator.py`）
- Hook ロジック本体はリポジトリ管理し、`$AI_AGENT_HOOKS_RUNTIME_LINK` から参照

## 旧構成の主なリスク

1. **重複実行リスク（Codex）**  
   Codex は複数ソースの Hook を併用するため、project と user の両方に同種 Hook があると二重実行される。

2. **遅延リスク（Gemini CLI）**  
   Hook は同期実行で、マッチした Hook の完了待ちが発生するため、頻繁イベントへの重い Hook は対話速度を落とす。

3. **運用競合リスク（全 CLI）**  
   プロジェクト配下の設定ファイルはチーム差分・ブランチ差分の影響を受けやすく、PRコンフリクト要因になる。

## 新構成での回避策

- 管理対象をユーザーグローバル設定に限定して、管理レイヤーを1つに固定
- 既存 `settings.json` / `config.toml` は置換せず managed 部分のみ append/merge
- 重い外部 reviewer call は main path から外しつつ、Codex の `UserPromptSubmit` では必要時だけ self-contained な `refinment` を使う

## 残るトレードオフ

- プロジェクト固有 Hook を別途運用する場合、手動で役割分担（global は安全系、project は業務固有）を明確化する必要がある
- 完全な一元統制が必要な組織では、OS 管理ポリシーや managed settings との併用設計が必要

## 追補（2026-04 Response Strategy）

回答完了タイミングの自律継続検証として、以下を追加しました。

- `multillm_orchestrator.py`（Codex `SessionStart` / `UserPromptSubmit` / `Stop`）
- `codex_hook_gate.py`（Codex Hook の単一ルーター）
- Claude/Codex: `Stop` イベントで発火
- Gemini: `AfterAgent` イベントで発火
- `AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY=0` は既定維持
- Codex orchestration 自体は常時 routed だが、実際の loop 起動は qualifying-task 判定と phase state によって決まる

現行の `multillm_orchestrator.py` は、旧来の `Claude -> Gemini -> Claude` 仕様ループではなく、**Codex が先に仕様を書き、必要時だけ self-contained な `refinment` で brief を締め、Hook 本体は state machine に専念する** 形へ寄せています。

設計詳細は [docs/codex-hub-orchestration.md](./codex-hub-orchestration.md) と [docs/response-strategy-autonomy.md](./response-strategy-autonomy.md) を参照してください。
