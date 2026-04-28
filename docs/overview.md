# このリポジトリは何か（概要）

## このドキュメントの位置付け

- **読者:** これからこのリポジトリを使うかもしれない人。プログラミング経験は問いません。
- **前提:** AI のチャットアシスタント（ChatGPT のようなもの）をターミナル（黒い画面のコマンド入力ツール）から使う「CLI（コマンドラインインターフェース）」というツール群があることだけ知っていれば十分です。
- **読み終えて分かること:** このリポジトリが何のためのものか、誰が使うのか、自分の PC を `setup.sh` で初期化すると何が起きるのか。

技術的な詳細を読みたい場合は [README.md](../README.md) と [setup.md](../setup.md) を参照してください。

## 一言で

**3種類の AI エージェント CLI（Claude Code / Codex / Gemini CLI）に「同じ指示書・同じ便利スキル・同じ安全装置」を入れて回すための、共通の設定リポジトリ**です。

PC を変えてもチームを変えても、同じルールで AI が動くようにする「設定の元本」を1箇所にまとめておく、という発想です。

## 誰のためのものか

- Claude Code / Codex / Gemini CLI のうち **少なくとも1つ** を自分の PC で使っている人
- 個人で複数 CLI を併用している人。CLI ごとに違うルールを書き分けるのが嫌な人
- 小さなチームで「AI への指示」を揃えたい人。GitHub 経由で共有・更新したい人
- GitHub Copilot 用の指示書（`.github/copilot-instructions.md`）も同じ源から作りたい人

逆に、**AI エージェント CLI を使っていない人には不要**です。ブラウザ版 ChatGPT や Claude しか使わない場合、このリポジトリの設定は何も呼び出されません。

## このリポジトリが配るもの 3 種類

| 種類 | 何か | 例 |
|---|---|---|
| **Instructions（指示書）** | AI に「こう振る舞ってほしい」を書いた Markdown ファイル | 「削除は `rm` ではなく `trash` を使う」「日本語で返す」など |
| **Skills（スキル）** | 再利用可能な手順書フォルダ。AI が必要なときに自分で呼び出す | 「指示文を整える `refinment`」「Skill 自体を改善する `skill-design-research`」 |
| **Hooks（フック）** | CLI が特定のタイミング（開始・停止など）に自動実行する小さなスクリプト | 「`rm` を見つけたら `trash` に置き換える」「仕様 → 実装 → 検証の流れを自動で回す」 |

正本（書き換える元のファイル）は `instructions/` フォルダの中だけにあります。各 CLI の設定はこの正本を **シンボリックリンク**（短く言うと「ショートカット」）で参照する仕組みです。元を編集すれば全ての CLI に反映されます。

## `scripts/setup.sh` を実行すると、自分の PC で何が起きるか

`setup.sh` は、PC 上の **3 つの決まった場所** にだけ手を入れます。それ以外のファイルは触りません。

| 場所 | 何が置かれるか |
|---|---|
| `~/.claude/` | Claude Code 用のグローバル指示書とフック設定 |
| `~/.codex/` | Codex 用のグローバル指示書とフック設定 |
| `~/.gemini/` | Gemini CLI 用のグローバル指示書とフック設定 |

加えて、リポジトリ本体への安定リンクが `~/.llm-config/hooks` に作られます。これがあるおかげで、リポジトリを別の場所に移しても CLI 設定は壊れません。

### 大事なルール（既存ファイルを壊さない設計）

- **既に `settings.json` や `config.toml` がある場合、上書きしません**。共通フックの記述だけを既存ファイルに **追記（マージ）** します。衝突する内容があれば自動でバックアップフォルダに退避します。
- **削除は `trash`（ゴミ箱に送る）だけ使います**。`rm` のような不可逆な削除は実行しません。
- **`AI_AGENT_DRY_RUN=1` を頭に付けて実行すれば、何も変更せずに「何が起きるはずか」だけを表示できます**。初回はこれで様子を見るのが安全です。

### GitHub Copilot は対象が違う

Copilot は VS Code の拡張機能であり、この自動配置の対象には入っていません。代わりに、Copilot に読ませたいリポジトリで `instructions/.github/copilot-instructions.md` を正本として `.github/copilot-instructions.md` に手動配置します。詳細は [README.md](../README.md) と [setup.md](../setup.md) を見てください。

## 後から外したくなったら

`scripts/uninstall.sh` を実行すると、このリポジトリが作ったリンクとフック追記だけを外して、元の状態に戻します。あなたが自分で書いた `settings.json` の中身は残ります。

## ここから先

- 実際の設定手順: [setup.md](../setup.md)
- 失敗したとき: [setup-error-guide.md](./setup-error-guide.md)
- 仕組みの設計判断: [hooks-architecture-review.md](./hooks-architecture-review.md)
- 自己完結フローの中身: [self-workflow-hooks.md](./self-workflow-hooks.md)
- ログから Skill 改善案を作る自動化: [skill-improvement-automation.md](./skill-improvement-automation.md)
