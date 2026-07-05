---
name: act-structured-slide-generation
description: "Generate native, editable 16:9 .pptx decks from a prompt — banker-grade structured slides in the Act design language (action titles, IBCS-style actual/forecast styling, native charts/tables, waterfalls, KPI dashboards, TAM/SAM/SOM, guidance progress). Use whenever the user asks for a deck, slides, a presentation, or any 資料 meant to be presented or shared as pages: 決算説明資料, IR資料, 提案書, 営業資料, 会社説明資料, 経営会議資料, 登壇・セミナー資料, ピッチ資料, 事業計画資料, or a .pptx deliverable — even without the word 'slide' or 'pptx' (e.g. 「資料を作って」「◯◯をまとめて役員に説明したい」). Not for AI-image slides (act-slide-image-generation), ATOM-brand slides (atom-slide-image-generation), narrative-only equity stories (equity-story), or xlsx financial models (startup-financial-modeling)."
---

# Act Structured Slide Generation

プロンプトから、投資銀行 Deck / 上場テック企業 IR 資料水準の**編集可能な 16:9 pptx** を生成する。
責務分離が品質の要: **LLM はコンテンツ(deck.json)だけを書き、座標・色・フォントは
build_deck.py が決定論的に処理する**。LLM が座標や色コードを発明した瞬間に再現性が壊れる。

## パイプライン

```
要件整理 → アウトライン承認 → deck.json → validate_spec(+--outline でタイトル通読)
→ build → verify → render → lint_render → 視覚レビュー → (必要なら)ルーブリック審査
→ 修正ループ(再レンダーは --baseline で回帰検知) → 完了報告
```

### 0. 環境(初回のみ)

```sh
python3 -c "import pptx, PIL, fontTools"     # 無ければ: pip3 install -r scripts/requirements.txt
python3 scripts/setup_fonts.py --check       # フォント欠落なら --check なしで導入
```

レンダリング検証には soffice(LibreOffice)と pdftoppm(poppler)が必要。無い環境では
その旨を報告し、ユーザーに pptx を開いての確認を明示的に依頼する。

### 1. 要件整理とアウトライン

- 聴衆・意思決定・言語・枚数感を確認する(不明なら 1 度だけ質問、以後は推論して明記)。
- 既存のコンテキスト資産(会社概要・KPI 定義・過去デッキの deck.json / outline.md・ブランド資料)
  があれば**先に読む** — 毎回ゼロから事実を再導出すると数字とトーンがブレる。使った資産は
  outline.md に出所として記録する。入力資料が大量のときは読み込みをサブエージェントに
  分担させ、要点だけを outline.md に落とす(本体のコンテキストを温存する)。
- governing thought(デッキ全体の主張)を 1 文で決め、各スライドのアクションタイトルを
  先に列挙する。**タイトルだけの通読で議論が完結する**(ゴーストデッキテスト)ことを
  確認してから中身を書く — 後からの構成修正は全工程やり直しになるため。deck.json 完成後は
  `python3 scripts/validate_spec.py deck.json --outline` でタイトル列を機械的に読み戻して再確認する。
- 数字は入力・リサーチに実在するもののみ。出典のない数字を作らない。**入力の数字が薄い
  ままアウトラインを書かない** — 主張を数字で立てられないときは、先にリサーチ工程を挟んで
  実数と出典を確保する(プレースホルダー数字で骨組みを作ると、後から全数値を差し替える
  羽目になる)。
- アウトラインは `outline.md`(governing thought / アクションタイトル列+パターン / 主要数字と
  出所)として出力ディレクトリに保存する。ユーザーが対話中なら**ビルド前に提示して承認を得る**。
  構成に迷いどころがあるときは 2-3 案を併記して 1 回の選択で決めてもらう(逐次の好み探りは
  往復が増えるだけ)。無人実行時は提示のみで先へ進む。以後の構成変更は outline.md → deck.json の順で反映する
  (中断・別セッションからの再開点になる)。
- **主張・構成・数字の確定はこの段階で終える。** レンダー後に許されるのは §4 の修理メニュー
  (表現とレイアウトの修理)だけ — それを超える変更が必要になったらアウトラインに戻る。
  スライドにしてから中身を直すのは全工程で最も高くつく。
- 用途で検証の重点を変える: **決算・IR・投資家向け**は出典・脚注・期間整合を最重視し §5 の
  ルーブリック審査をデフォルトで実施。**提案・ピッチ**はゴーストデッキテストと「図表がタイトルの
  主張を証明しているか」。**社内・経営会議資料**は速度優先で §5 は求められた場合のみ。

### 2. deck.json を書く

`build/references/deck-spec.md` を読み、パターン 19 種から構成する(表紙・目次・扉・
サマリー・KPI・チャート・市場規模・比較表・2x2・財務・waterfall・ロードマップ・2 案比較・
フロー・ステートメント・決算ハイライト・数値サマリ行・ドライバー分解・ガイダンス進捗)。
定石構成とデザイン判断は `build/references/design-principles.md`、完全な実例は
`examples/sample-deck.json`(提案書・市場参入)と `examples/sample-earnings-deck.json`
(決算説明・パターン 16-19 の使い方)。

書き上げたら `build/references/humanize.md` でセルフレビューし、AI 常套句・均一な 3 項目・
ヘッジの重なり・幽霊出典を **1 回のまとめ修正**で除去する(逐次直しは均一化を招く)。

### 3. 検証とビルド(全て通ること)

```sh
python3 scripts/validate_spec.py deck.json          # 予算・パレット・整合の事前検証
python3 scripts/build_deck.py deck.json -o deck.pptx
python3 scripts/verify_deck.py deck.pptx            # 色/フォント/<a:ea>/オーバーフロー/重なり
sh scripts/render_deck.sh deck.pptx render/
python3 scripts/lint_render.py render/ --spec deck.json  # 端見切れ+readback 検証
```

validate_spec のエラーは deck.json 側を直す。機械検証は視覚品質を保証しない — 次工程が本体。

### 4. 視覚レビュー(スキップ禁止)

3 段階で見る。まず `render/contact-sheet.png`(render_deck.sh が自動生成)を Read して
デッキ全体を一望し、**デッキ単位でしか見えない問題**を探す: トーン・密度の偏り、レイアウト
リズムの単調さ、Accent 黄の使用頻度、スライド間の視覚的な揺れ。次に `render/header-strip.png`
(全ヘッダー帯の縦積み、同時生成)で**ヘッダーの統一**を確認する — タイトル行数・サブタイトル
有無・バー高の揺れは、積み上げて見ると一目で分かる。最後に render/ の**全 PNG を
Read で個別に精読する**。「問題は必ずある。見つけるのが仕事」の前提で探す — 初見で指摘ゼロ
なら見方が甘い。各スライドは deck.json 上の意図(パターン・主張)を思い出してから見ると
「期待と実物の差」として欠陥が浮く:

- テキストのはみ出し・重なり・見切れ、要素衝突、0.3in 未満の窮屈な隙間
- 大きな空白、カードの器と中身の不釣り合い、上下どちらかへの偏り
- タイトルの主張と図表の不一致(図表が証明できない期間・数値をタイトルが語っていないか)
- 単位・桁・符号(+/△)・期間表記のスライド間の揺れ、実績と予想の描き分け漏れ
- ヘッダーの揺れ: タイトル行数・文体・サブタイトル有無の混在、kicker の乱用(header-strip で確認)
- 日本語組版: 行頭の句読点・閉じ括弧(禁則)、不自然な位置での折返し、フォント化け
- source/ページ番号の欠落、Accent 黄の複数使用

同一デッキのレビューが 2 周目以降で惰性化してきたら、レビューだけをサブエージェントに
出して新しい目で見させる(自分が作った物は「あるはずの物」が見えてしまう)。その際は
各スライドの意図(パターンと主張)を添え、上のチェックリストで「欠陥を探せ」と依頼し、
指摘の形式を**スライド番号+箇所+観察事実+修理メニューのどれで直すか**に固定する —
場所と直し方を特定しない指摘(「全体的に余白が気になる」)は修正に使えず 1 往復無駄になる。

修正は**修理メニューに限定**する: 文章の短縮 / スライド分割 / 詳細の speaker_notes 送り /
パターン切替 / 項目の削除・統合 / insight の削除。deck.json を直して再ビルドし(pptx 手編集
禁止)、**最低 1 周の fix-and-verify を回すまで完了を宣言しない**。再ビルドはトークンを
消費しない決定論処理なので、遠慮なく全量再ビルドしてよい。再レンダー後は前回レンダーを
`--baseline` に渡して差分を確認する:

```sh
sh scripts/render_deck.sh deck.pptx render-v2/
python3 scripts/lint_render.py render-v2/ --spec deck.json --baseline render/
```

DIFF 出力が「直したつもりのスライド」と一致していれば修正は閉じている。触っていない
スライドが変化していたら回帰 — 原因を特定してから進む。修正の再確認は変化したスライドの
PNG だけ Read すればよい。エンジン側の欠陥は build_deck.py を直して全量再ビルドする
(スライド単位の場当たり座標調整をしない)。

### 5. ルーブリック審査(品質保証が求められるとき)

採点基準は `build/evals/rubric.json`(6 カテゴリ・チェックリスト減点法・95 点合格線)で
固定し、審査者は次の順で選ぶ:

1. **Advisor 審査(既定)**: §4 で全スライド PNG を Read 済みの会話状態で rubric.json を
   読み込み、Advisor に「rubric のカテゴリ別に、観察した欠陥の列挙と減点採点」を諮る
   (Advisor は画像を含む会話全体を見る)。Advisor 未設定の環境では `/advisor` での設定を
   ユーザーに案内するか、2 に切り替える。
2. **外部 CLI 審査(代替)**: `python3 scripts/eval_deck.py render/ --judge codex --anchor
   "<スライド1の一意な語句>"`(codex / gemini)。--anchor は幻覚審査の破棄に必須。

どの審査者でも、**指摘は render の実画像で真偽を確認してから**修理メニューで潰す —
審査者は実在しない重なりや表記を指摘することがあり、幻覚指摘に従った修正は品質を下げる。
どの審査者も使えない環境では本工程をスキップし、§4 の視覚レビュー結果を品質根拠として
完了報告に明記する(審査を捏造しない)。

### 6. 完了報告

出力ディレクトリには `outline.md` / `deck.json` / `deck.pptx` / `render/`(スライド PNG と
共有用 PDF — render_deck.sh の副産物)を揃えたまま残す。中間成果物は削除しない — 後修正は
deck.json から再開する。その上で、出力パス、枚数、各検証の結果、視覚レビューで直した点、
残リスク(フォント未導入環境での見え方など)を報告する。

納品後にユーザーが手直しした pptx が戻ってきたら、生成版との差分(文言・削除・並べ替え)を
読み取り、繰り返し直されている点を deck.json の書き方・参照ドキュメント・エンジンの改善に
還元する — 人の修正は最も信頼できる品質フィードバックで、放置すると毎回同じ手直しをさせる。

## 禁止事項(それぞれ理由がある)

- 座標・サイズ・色 hex を deck.json に書かない(チャート系列 color のパレット内指定のみ例外)
  — 見た目の一貫性はエンジンの一元処理で保たれており、spec 側の直指定は再現性とテーマを両方壊す。
- ダミー数字・プレースホルダー出典を書かない(「Act分析」は実際に分析した場合のみ)
  — 意思決定資料は 1 つの捏造数字で全体の信頼を失う。
- insight バーを常用しない(非自明な判断がある 2-4 枚のみ)。体言止め・トピックラベルの
  タイトルを書かない — 毎枚強調すると強調が消え、主張のないタイトルはゴーストデッキテストを壊す。
- 自動フォント縮小で詰め込まない — 縮小は「読めない資料」を機械検証エラーなしで通してしまう。
  溢れたら文章を短くするかスライドを分割する。
- build_deck.py を経由した pptx 生成だけを使う(手編集・スライドの画像貼り付け化をしない)
  — 手編集は次の再ビルドで消え、画像化は納品先での編集可能性(このスキルの存在意義)を奪う。

## ファイル構成(いつ何を読むか)

| ファイル | 読むとき |
|---|---|
| `build/references/deck-spec.md` | deck.json を書く前(必読。パターン仕様+執筆規律) |
| `build/references/design-principles.md` | 構成・強調・チャート表現の判断に迷ったとき |
| `build/references/humanize.md` | deck.json 執筆後のセルフレビュー(必須) |
| `build/references/tokens.json` | デザイントークンの確認・変更(色/タイポ/グリッドの単一情報源) |
| `build/references/pptx-pitfalls.md` | build_deck.py を改修するときのみ |
| `build/evals/` | ルーブリック・評価シナリオ(審査を回すとき) |
| `examples/sample-deck.json` | パターンの使い方の実例が欲しいとき(提案書・市場参入の 16 枚) |
| `examples/sample-earnings-deck.json` | 決算系パターン 16-19 の実例が欲しいとき |

`scripts/` は安定 CLI(build/scripts への symlink)。テストは
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest build/tests -p no:cacheprovider` で実行する
(素の pytest は `__pycache__` / `.pytest_cache` を残し、リポジトリの validate-repo.sh が落ちる)。
