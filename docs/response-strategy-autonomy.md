# Response Strategy Hook Design (2026-04)

## 目的

Claude Code / Codex / Gemini CLI の回答確定タイミングで Hook を発火し、  
外部レビュー（Gemini / Codex / Ollama）から「次の一手」を生成して、  
必要時のみ自動でもう1ターン継続させる設計を検証した結果です。

狙いは **完全自律寄り** にしつつ、`needs_human` フラグで **Human-in-the-loop** を残すことです。

## 実現可能性（公式仕様ベース）

| CLI | 使うイベント | 入力の要点 | 継続制御 |
|---|---|---|---|
| Claude Code | `Stop` | `last_assistant_message` あり | `decision: "block"` + `reason` で停止を取り消して続行 |
| Codex | `Stop` | `last_assistant_message`, `stop_hook_active` あり | `decision: "block"` + `reason` で continuation prompt を生成 |
| Gemini CLI | `AfterAgent` | `prompt_response`, `stop_hook_active` あり | `decision: "deny"` + `reason` でリトライ |

結論として、3 CLI すべてで「回答後に判定し、必要時のみ再実行」は可能です。

## このリポジトリでの実装方針

`hooks/scripts/response_strategy_bridge.py` を追加し、以下を実装しました。

1. 回答後イベントで起動（Claude/Codex は `Stop`、Gemini は `AfterAgent`）
2. 最新回答 + redact済み transcript 末尾をレビュー用コンテキスト化
3. 非対話モードで peer LLM を呼び出し、JSON判定を受け取る
4. `action=continue` かつ `needs_human=false` のときだけ自動継続
5. それ以外は fail-open（`{}`）で通常終了

## ルーティング

既定（`AI_AGENT_RESPONSE_STRATEGY_PROVIDER=auto`）:

- Claude/Codex -> Gemini
- Gemini -> Codex

明示指定:

- `AI_AGENT_RESPONSE_STRATEGY_PROVIDER=gemini|codex|ollama`
- `ollama` を使う場合は `AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL` が必須

## デフォルト挙動

この Hook は **登録済みだが既定OFF** です。  
有効化時のみ判定処理が動きます。

```sh
export AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY=1
```

## 安全策

- 無限ループ抑止: `AI_AGENT_RESPONSE_STRATEGY_ACTIVE=1` をサブプロセスへ注入
- 連続再入抑止: `stop_hook_active=true` 時は既定スキップ
- 低価値レスポンス除外: 最小文字数しきい値（既定 `120`）
- タイムアウト・出力上限あり（fail-open）
- パース失敗・CLI未導入・外部LLM失敗時は `{}` を返して本体フロー継続

## 運用リスクと回避

| リスク | 回避策 |
|---|---|
| レイテンシ増加 | 既定OFF、必要時だけ有効化 |
| 過剰再試行ループ | `stop_hook_active` ガード + `needs_human` 分岐 |
| 機密混入 | transcriptは末尾のみ + key/token系を redaction |
| ツール未導入環境 | fail-open（通常終了） |

## さらにシンプルにしたい場合

最小構成は以下です。

1. Provider を `gemini` 固定（`ollama` / `codex` 分岐を使わない）
2. transcript共有をOFF
3. `action` を `continue|allow_stop` の2値だけ運用

これでデバッグ負荷と運用分岐をさらに下げられます。

## 参照（一次情報）

- Codex Hooks: <https://developers.openai.com/codex/hooks>
- Claude Code Hooks: <https://code.claude.com/docs/en/hooks>
- Gemini CLI Hooks index: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/hooks/index.md>
- Gemini CLI Hooks reference: <https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/hooks/reference.md>
- Ollama CLI/API docs: <https://docs.ollama.com/cli>, <https://docs.ollama.com/api/generate>
