# AI Agent Config

AIツール向けの共通InstructionsとSkillsを配布・更新するための設定リポジトリです。

## Claude Codeに渡す言葉

初回セットアップでは、Claude Codeに次のように伝えてください。

```text
README.mdとsetup.mdを読んで、このPCにAI Agent Configをセットアップして。
専門用語は日本語で説明して、更新頻度は推奨の1日1回を含めて選ばせて。
```

急ぎで最新化したい時は、次のように伝えてください。

```text
急ぎ対応したいんだけど、READMEの臨時更新手順で今すぐ最新にして。
```

Claude Codeは `scripts/update.sh` を実行して、共有InstructionsとSkillsをすぐ最新化します。ここでの **LLM** は、Claude CodeやCodexのように会話しながら作業を進めるAIエージェントを指します。

## 何が入るか

- `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` などのAIツール用入口ファイル
- 共通ルール本体の `AI_AGENT_INSTRUCTIONS.md`
- 再利用可能なSkill
- 更新用スクリプト

## 更新頻度

セットアップ時に、LLMはユーザーへ更新頻度を聞きます。推奨は **1日1回** です。

| 選択肢 | 設定 | 向いている場面 |
|---|---|---|
| **1日1回（推奨）** | `AI_AGENT_UPDATE_CADENCE=daily` | ほとんどの従業員向け |
| **12時間ごと** | `AI_AGENT_UPDATE_CADENCE=twice-daily` | ルールやSkillが頻繁に変わる時期 |
| **1週間ごと** | `AI_AGENT_UPDATE_CADENCE=weekly` | 安定運用で更新頻度を抑えたい場合 |
| **自動更新なし** | `AI_AGENT_UPDATE_CADENCE=manual` | 既存の自動更新を止め、必要な時だけ手動更新したい場合 |
| **カスタム** | `AI_AGENT_UPDATE_CADENCE=custom AI_AGENT_UPDATE_INTERVAL_SECONDS=<seconds>` | 管理者や特殊な運用向け |

## 臨時更新 / 手動更新

自動更新を待たずに今すぐ反映したい場合は、次を実行します。

```sh
sh /path/to/ai-agent-config/scripts/update.sh
```

LLMには「急ぎ対応したいんだけど」と伝えれば、この手順で進めるように案内しています。

## 詳細

詳しいセットアップ手順、環境変数、検証方法は [setup.md](setup.md) を参照してください。
