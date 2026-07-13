---
name: startup-equity-story
description: >-
  Use when the user needs an equity story, fundraising narrative, investment
  thesis, pitch narrative, IPO/IR story, roadshow message, growth-potential
  disclosure (成長可能性に関する説明資料), investor Q&A (想定問答), "why invest
  in us", moat, positioning, TAM/SAM/SOM, GTM story, unit-economics narrative,
  "なぜ勝てるのか", or "エクイティストーリー" for VC, IPO, public-market,
  Japan, or US investors.
---

# Equity Story(エクイティストーリー設計)

エクイティストーリー = 「なぜこの会社に、この価格で、いま投資すべきか」。
要素の寄せ集めではなく、統率命題1文(価値+因果)が全要素を「したがって」で
貫く一本のストーリーとして設計する。全要素は統率命題の証明としてだけ存在させる。

## ルート

- テーゼ・競争土俵・主要Moat仮説のいずれかが**選べない**(候補すら立たない):
  診断モードのみ実行して止める — 競合マップ、Moat仮説2〜3個、反証シグナル、
  正直な選択肢、検証アクション(基準は `references/market-positioning.md` と
  `references/moat.md`)。
- 上記を**仮説としてなら選べる**: `[assumption]` タグと反証条件を付けて
  ストーリーモード(以下のワークフロー)へ進む。仮説段階のMoatはSeedでは正常。
- ユーザーが診断のみを求めた場合はストーリー本体を作らない。
- 質問は、ステージ・読者・バリュエーション・法的文脈・成果物の形が結果を変える
  場合のみ。それ以外は仮定を明示して進める。

## ワークフロー

1. **素材収集** — 会社/プロダクト、ステージ/地域、証拠、読者、調達額/バリュエーション、
   マイルストーンを集め、全数値に `[fact]/[derived]/[estimate]/[assumption]/[open]`
   タグを付す。数値の発明は禁止。弱い主張はリサーチで補強する。
2. **スパイン設計(執筆前に必ず)** — `references/story-spine.md` の手順で:
   統率命題1文の導出と採点 → believe list 3〜8個 → アーク型判定(変化起点/
   インサイト起点/問題起点)→ ドライバーシート先行作成(顧客数・単価・獲得数・
   CAC・継続率・売上を1枚に確定し、各章はこの表から引用のみ。独立に数字を作らない。
   実測がない変数は `[assumption]`/`[estimate]` タグ付きの仮説値で埋めてよく、
   各章はその同一仮説値を引用する。禁止は無タグの数値発明。仮説すら立たない変数のみ
   定義・単位・検証方法を固定して `[open]` を維持する)。
3. **要素執筆** — 各要素は対応リファレンスの「ベスト構成」と合格基準に従い、
   直前の要素を「したがって/しかし」で受けてから書く:

   | 要素 | リファレンス |
   |---|---|
   | ビジョン・課題の大きさ・Why Now | `references/vision-problem-whynow.md` |
   | プロダクト戦略(楔→拡張→compounding) | `references/product-strategy.md` |
   | 市場構造・競合・ポジショニング | `references/market-positioning.md` |
   | TAM(トップダウン)/SAM(構造減算)/SOM(ボトムアップ) | `references/tam-sam-som.md` |
   | ICP・GTM・市場浸透 | `references/gtm.md` |
   | ビジネスモデル・ユニットエコノミクス | `references/business-model-unit-economics.md` |
   | Moat(7 Powers・動的堀・Why not Google) | `references/moat.md` |
   | トラクション・チーム・ソーシャルプルーフ | `references/traction-team.md` |
   | 財務計画・調達額・資金使途・資本政策 | `references/financial-ask.md` |

4. **継ぎ目検算** — Why now⇔Moat は「時限的な窓 × 蓄積型資産」を同じ資産で貫く。
   TAM⇔GTM⇔UE⇔財務計画はドライバーシート経由で検算: (a) 最終年売上 ≦ SOM、
   (b) fully-loaded CAC×年間新規獲得数 ≒ 新規獲得対応S&M費(差異10%以内、
   超過は定義差・期間差を説明)、(c) UEの継続率・単価前提 = 財務計画のコホート前提。
   財務モデルが要るときは `references/financial-ask.md` §5 のドライバー8項目を
   埋めてから `startup-financial-modeling` スキルに渡す。
5. **反証耐性** — `references/qa-risk.md`: 最重要反論1個は本編序盤に先回りで組み込む。
   想定問答10カテゴリ(回答は「結論(数字)→根拠1つ→反証条件」)、リスク2〜4個+
   緩和策/検証マイルストーン(資金使途と1対1対応)、falsification trigger つき
   ベアケース、「What would change our mind」。
6. **日本IPO・IR(該当時のみの条件分岐)** — 日本IPO・東証開示・国内IRの場合のみ
   実行し、それ以外の調達ではスキップする。成果物の言語は読者に合わせる(日本IPO・
   IRは日本語標準)。`references/japan-ipo.md` で同じストーリーを成長可能性資料の
   制度項目・KPI契約(採用理由/実績/目標/算定方法)・引受審査・FDルール下の
   想定問答・継続開示に写像する。
7. **出力ゲート(通るまで反復、行き詰まったら明示)** — `references/story-spine.md`
   の検証テスト9本(章タイトル通読・接続詞・1文再現・believe対応表・競合代入・
   数字往復・3P・媒体密度・正典化)+ 使用した各リファレンスの合格基準チェックリスト。
   まず**コアゲート5項目**を厳密に通す: (1) 1文再現テスト(第三者/別LLMで統率命題が
   再現される) (2) 接続詞テスト(全章が「したがって/しかし」で繋がる) (3) 数字検算
   3式(最終年売上≦SOM・CAC×獲得数≒S&M費・コホート前提一致) (4) believe対応表に
   空行・空列なし (5) 主要主張に falsification trigger がある。
   その後、使用リファレンスのチェック項目を Pass / N/A / Open に分類する: N/A は
   各リファレンスの「ステージ差」に明示された免除がある場合のみ。Open は検証
   マイルストーン・期限つきの場合のみ通過可(IPO・IRでは Open 原則不可)。
   煽り語・根拠なき最上級・全部✓比較表・累積グラフはゼロ。

## 出力形式

- 日本IPO・IR用途では本章順に代えて `references/japan-ipo.md` の9章構成
  (投資ハイライト→ミッション/課題→市場環境→サービス→ビジネスモデル→KPI→
  競争力の源泉→成長戦略→利益計画・リスク)を最優先で適用する。
- 標準の章順(アーク型・最強カードに応じて並べ替え可): 統率命題/投資ハイライト →
  Why now・課題・ビジョン → プロダクト → 市場構造・ポジショニング → TAM/SAM/SOM →
  GTM → ビジネスモデル・UE → Moat → トラクション → チーム → 財務計画・調達・
  マイルストーン → リスク・ベアケース → ビジョン再掲。想定問答と詳細データは Appendix。
- 診断モードのゲート: 反証可能なMoat仮説、正直な選択肢、検証アクションが揃うこと。
- デッキ化する場合はスライド見出し+1行メッセージのアウトラインを付け、
  スライド生成はスライド系スキルに委ねる。
