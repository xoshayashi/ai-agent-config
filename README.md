# AI Agent Config

AIツール向けの共通InstructionsとSkillsを配布・更新するための設定リポジトリです。

## 最初に準備すること

このセットアップは、**ターミナルでClaude Code、Codex、Gemini CLIの全てにログインできている状態**から進めます。まだの場合は、先に次を済ませてください。

1. **ターミナルを開く。**
   macOSなら「ターミナル」または「iTerm2」、Windowsなら「PowerShell」または「Windows Terminal」を使います。
2. **Claude Code、Codex、Gemini CLIを全てインストールする。**
   この設定は、3つ全てのLLM CLIで同じ共有InstructionsとSkillsを使える状態を前提にします。
3. **3つ全てのLLM CLIにログインする。**
   それぞれ起動して、ログイン画面やブラウザ認証が出たら画面の案内に従います。

| ツール | 公式手順 | ログイン確認の目安 |
|---|---|---|
| **Claude Code** | [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) | `claude` を起動し、必要なら `/login` でログインします。 |
| **Codex** | [Codex CLI](https://developers.openai.com/codex/cli) | `codex` を起動し、初回表示の案内に従ってChatGPTアカウントまたはAPI keyでログインします。 |
| **Gemini CLI** | [Gemini CLI Get Started](https://google-gemini.github.io/gemini-cli/docs/get-started/) | `gemini` を起動し、認証方法で「Login with Google」を選びます。 |

## LLM CLIで完結するセットアップ依頼

Claude Code、Codex、Gemini CLIのどれかを起動したら、次の文章をそのまま貼ってください。GitHubログイン確認、リポジトリ取得、セットアップまでLLM CLIとの会話で進めます。

```text
GitHubにログインできているか確認して。未ログインなら、初心者にも分かる日本語でログイン手順を案内して。
その後、次のリポジトリをこのPCに取得して。既に同じリポジトリがある場合は、最新のmainをpullして。

https://github.com/xoshayashi/ai-agent-config.git

取得できたら、そのリポジトリのREADME.mdとsetup.mdを読んで、このPCにAI Agent Configをセットアップして。
Claude Code、Codex、Gemini CLIの全てがインストール済みかつログイン済みか確認して、未完了のものがあれば先に案内して。
セットアップ先は、まず推奨として「普段LLM CLIで作業する親フォルダー」を示して。迷っている場合は `~/Documents/projects` を推奨し、既に使っている作業フォルダーや会社指定のworkspaceがあればそれを優先して。
初回セットアップでは必ずdry runで事前確認して、作成されるリンク、バックアップされる可能性があるファイル、設定される更新頻度を日本語で要約してから本実行して。
専門用語は日本語で説明して、更新頻度は推奨の1日1回を含めて選ばせて。
```

## 取得済みリポジトリでセットアップする時の言葉

このリポジトリが既にPC上にある場合は、実際にセットアップを進めるClaude Code、Codex、またはGemini CLIに次のように伝えてください。

```text
README.mdとsetup.mdを読んで、このPCにAI Agent Configをセットアップして。
まだClaude Code、Codex、Gemini CLIの全てのインストールやログインが済んでいなければ、最初にそこから案内して。
セットアップ先は、まず推奨として「普段LLM CLIで作業する親フォルダー」を示して。迷っている場合は `~/Documents/projects` を推奨し、既に使っている作業フォルダーや会社指定のworkspaceがあればそれを優先して。
初回セットアップでは必ずdry runで事前確認して、作成されるリンク、バックアップされる可能性があるファイル、設定される更新頻度を日本語で要約してから本実行して。
専門用語は日本語で説明して、更新頻度は推奨の1日1回を含めて選ばせて。
```

## 自然言語での保守・運用

急ぎで最新化したい時は、次のように伝えてください。これは **`scripts/update.sh` をすぐ実行するための合図** です。

```text
急ぎ対応したいんだけど、READMEの臨時更新手順で今すぐ最新にして。
```

Claude Code、Codex、Gemini CLIは `scripts/update.sh` を実行して、共有InstructionsとSkillsをすぐ最新化します。ここでの **LLM** は、Claude Code、Codex、Gemini CLIのように会話しながら作業を進めるAIエージェントを指します。

状態確認だけしたい時は、次のように伝えてください。これは **`scripts/health-check.sh` を実行するための合図** です。

```text
設定が壊れていないか確認して。README.mdとsetup.mdを読んで、health-checkを実行し、結果を日本語で短く説明して。
```

## 何が入るか

- `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` などのAIツール用入口ファイル
- 共通ルール本体の `AI_AGENT_INSTRUCTIONS.md`
- 再利用可能なSkill
- 更新用・状態確認用スクリプト

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

## 元に戻したい時

設定を外したい場合は、LLM CLIに次のように伝えてください。

```text
AI Agent Configのセットアップを元に戻して。README.mdとsetup.mdを読んで、uninstall手順でリンクと保存済み設定を安全に片付けて。
削除が必要なものは完全削除せず、ゴミ箱に移して。実行前に何を片付けるか日本語で説明して。
```

## みんなで育てる時

このリポジトリを複数人で更新する場合は、変更前に [docs/compatibility.md](docs/compatibility.md) を確認してください。新しいSkillは `skills/template/` から作り、PR前に次を実行します。

```sh
sh scripts/validate-repo.sh
```

## 詳細

詳しいセットアップ手順、環境変数、検証方法は [setup.md](setup.md) を参照してください。
