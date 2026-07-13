# story-spine — 統率命題・投資テーゼ・アーク設計・接続技術・焦点

役割: 全12要素を貫く「赤い糸」を設計する元締めリファレンス。個別要素を書く前に本書で統率命題とアークを確定し、書いた後に本書の検証テストで一本通っているかを判定する。

## 一本のストーリーへの接続

### 12要素接続マップ(各要素が前から受け取るもの→次へ渡すもの)

| # | 要素 | 前から受け取る | 次へ渡す |
|---|------|--------------|---------|
| 1 | story-spine | 生素材一式 | 統率命題1文+believe list+アーク型+ドライバーシート |
| 2 | vision-problem-whynow | 統率命題の「因果」側 | 開いた市場の窓・課題の深刻度 |
| 3 | product-strategy | 課題と窓 | 約束の地(顧客の新状態)への道筋 |
| 4 | market-positioning | 窓とプロダクト | 戦う土俵の定義・勝者敗者の線引き |
| 5 | tam-sam-som | 土俵の定義 | 顧客数×単価の母数(ドライバーシート起点) |
| 6 | gtm | SOMのICP | 獲得の再現手順とCAC |
| 7 | business-model-unit-economics | GTMの獲得数・CAC | LTV/CAC・粗利構造 |
| 8 | moat | Why nowの窓+UEの蓄積資産 | 「窓が閉まった後も勝ち続ける理由」 |
| 9 | traction-team | believe list | 各believeへの証拠割当 |
| 10 | financial-ask | ドライバーシート+証拠の空白 | 資金使途=次に証明するbelieve、マイルストーン |
| 11 | qa-risk | 全要素の弱点 | 反論への構造化回答・ベアケース |
| 12 | japan-ipo | 完成したスパイン | 制度枠(成長可能性資料等)への写像 |

### 「したがって」チェーン模範例(架空B2B SaaS)

1. 規制改正Xで全社が業務Yのデジタル記録を義務化された(変化)。**しかし** 既存手段は現場が使えず形骸化している(課題)。**したがって** 現場が使える記録手段を最初に握った者が業務データの蓄積で勝つ(統率命題の因果)。**したがって** 当社は現場特化UIで記録点有率を取りにいく(プロダクト)。**したがって** 戦う土俵は「基幹システム」でなく「現場入力レイヤー」(ポジショニング)。**したがって** 母数は対象事業所N万×単価P(SOM)。**しかし** 現場への販売は営業効率が課題。**したがって** 業界団体経由のGTMでCACを抑える(GTM)。**したがって** LTV/CAC=4xが成立(UE)。**したがって** 蓄積データが switching cost と精度優位になり窓が閉まっても残る(Moat)。**したがって** 導入200社・継続率97%が上記を裏づけ(証拠)。**したがって** 今回のY億円でGTM再現性を証明しシリーズBへ(Ask)。

判定: 各ビートが「そして」でしか繋がらないなら、その要素は接続不全(後述テスト2)。

## ベスト構成(このリファレンスの手順)

### 手順1: 素材インベントリ
- 会社情報を事実カードに分解し `[fact]/[derived]/[estimate]/[assumption]/[open]` を付す。
- 「最強カード」を1枚選ぶ: 投資家が最も驚き、かつ検証可能な事実(トラクション、独自データ、インサイト、変化の目撃者性のいずれか)。

### 手順2: 統率命題1文の導出
McKee型「価値+因果」で書く: **「(因果: 何が起きた/何を知っているから)、(価値: 誰がどれだけ大きな価値をどう独占するか)」の1文**。
1. 候補を3〜5本生成。各候補は (a)1文 (b)接続詞1個以内 (c)固有名詞・数値を最低1つ含む。
2. 絞り込み判定基準(全候補を5項目で採点、最高得点を採用):
   - **反証可能性**: 賢い投資家が「その前提には同意しない」と言える具体性があるか(VC投資委員会メモの基準)。
   - **競合代入テスト**: 主語を主要競合に置換して文が嘘になるか。生き残るなら固有性不足。
   - **3P位置**(Damodaran): possible/plausible/probable のどこに立つ命題か。ステージ相応か(Seed=plausible上等、IPO=probable必須)。
   - **派生力**: この1文から believe list 3〜8個が機械的に展開できるか。
   - **30秒再現性**: 聞いた投資家が同僚に一言で転送できるか。
3. **悪い統率命題の判別**(1つでも該当なら書き直し):
   - 形容詞・副詞で支えられている(Hoffman「be wary of adjectives and especially adverbs」)。
   - カテゴリ自己紹介文(「〜向けSaaSです」)で因果がない。
   - 「かつ」で2つの物語が接合されている(焦点分裂)。
   - 価値(リターン)側の欠落: 社会的意義のみで独占の理屈がない。
   - 因果側の欠落: 結論(大きくなる)だけで理由がない。

### 手順3: believe list 展開(Hoffman)
- 統率命題を **3〜8個の「投資家が信じるべき命題」** に分解。冒頭スライドに置き、以降の全章はこのリストの確度を上げるためだけに存在させる。
- 最低カバレッジ: 「市場が十分大きくなる理由」「持続優位の理由」「このチームが実行できる理由」を各1個以上。
- 各believeに5属性を持たせる: **現在の確度(3P: possible/plausible/probable)/現有証拠/反証条件/未証明なら検証マイルストーン/本編での表現区分(実証済み・仮説・調達後に証明)**。「現有証拠 or 今回調達で検証」のどちらかを必ず割り当てる(空白のまま放置禁止)。
- 未証明のbelieveを本編で確定事項の顔で書かない(表現区分に従う)。IPO・IRでは「未証明believeを資金使途送りにすれば合格」は不可 — probable未満のbelieveは投資ハイライトに置かない。

### 手順4: アーク型の選択(判定木)
上から順に判定し、最初にYesの型を採る:
- **Q1 変化起点(Raskin)**: 外部の undeniable な変化に名前を付けられ、勝者と敗者を具体的に言えるか? その変化が最強カードか? → カテゴリ創造・市場再定義・concept-driven ピッチ向き。構成: 変化命名→勝敗のstakes→約束の地→障害を越えるgifts=プロダクト→実現できる証拠。
- **Q2 インサイト起点(Dunford)**: 市場は既知だが「市場の見方」が競合と違い、その洞察が最強カードか? → 競合密集市場・既存カテゴリ内差別化向き。構成: 市場インサイト→代替案の長短→完璧な解の合意→差別化価値→証明。
- **Q3 問題起点(Sequoia)**: 課題が自明かつ深刻で、解と実績が直球で強い(data-driven)か? → デフォルト。迷ったらこれ。構成: 一文の会社目的→課題→解→Why now→市場→競合→プロダクト→BM→チーム→財務。
- 補正: concept-driven(現データより将来仮説が主)は Q1/Q2 寄り、data-driven は Q3+数字前倒し(Hoffmanの区分を先に自己判定)。日本IPOは制度順(ビジネスモデル→市場環境→競争力の源泉→事業計画→リスク)を骨格にQ3ベースで写像。
- どの型でも Duarte の what is⇔what could be の往復をリズムとして重ね、終点は new bliss(顧客と投資家の新状態)で閉じる。

### 手順5: ドライバーシート先行作成
- 章を書く前に、顧客数・単価・獲得数・CAC・継続率・売上を1枚の数値対応表(ドライバーシート)に確定し、TAM/GTM/UE/財務の各章は**この表から引用**する。各章で数字を独立に作ることを禁止する(継ぎ目破綻の根絶策)。
- 変数の分離定義: **CACは paid / blended / fully-loaded の3種を別行で持つ**(UE章はpaid主・blended従、財務との継ぎ目検算はfully-loadedのみ、と用途が違うため単一「CAC」では衝突する)。**単価は楔ACVと拡張後ACV(またはNRR係数)を分離**できる行を持ち、land-and-expand型の単価上昇を各章がその場で捏造しない構造にする。
- 「確定」の定義: 値そのものが未確定でも、**変数名・定義・単位・期間・タグ(`[fact]`等)・値の範囲・検証方法**を固定することを指す。実測がないステージ(Seed等)では、ターゲット値・類推に基づく仮説値を `[assumption]`/`[estimate]` タグ付きで入力してよく、全章はその同一仮説値を引用する。禁止は**無タグの数値発明**。仮説すら立てられない変数のみ `[open]` を維持し、その変数に依存する章は範囲と検証計画で語る。

### 手順6: 焦点の絞り込み(本編/Appendix判定)
以下に1つでも該当する章・スライドはAppendixへ「降格」(削除ではなく正典に温存):
- believe list対応表(後述テスト4)で空列=どのbelieveも支持しない。
- 削っても believe の確信度が下がらない。
- 第2ビジネスモデル・第2プロダクト(Hoffman「one business model drives the business」)。
- 想定反論のうち先回りすべき主要3つ以外(構造化回答としてAppendix待機。Hoffman流に質問が出るまで見せない)。
- 分量規律: 主張は7要素以内・1章1主張(Paul Graham: 狭く具体的に、simple/focused/groundedはDamodaranの物語3則とも一致)。送付版10〜15枚、口頭20±5枚、Appendix無制限。

### 手順7: 継ぎ目防衛(設計段階で仕込む)
- **Why now⇔Moat**: 「いま窓が開いた」と「他社は入れない」は放置すると矛盾する。Why nowは「窓が開いた理由」、Moatは「窓が開いている間に蓄積する資産と、窓が閉まった後もそれが残る理由」として時系列で分業させる。統率命題自体に両方を内包させる(模範: 「Xで市場が開き、最初にYを蓄積した者が構造的に勝つ。当社が最初にYを持つ」)。
- **TAM⇔GTM⇔UE⇔財務計画**: ドライバーシート経由で相互検算。(a) 財務計画最終年度売上 ≦ SOM(超えたら即棄却、SOM比が高すぎる場合は根拠明記) (b) GTMの**fully-loaded CAC×年間新規獲得数 ≒ 財務計画の新規獲得対応S&M費**(継ぎ目検算はfully-loaded CACのみに固定。paid CACはUE開示用の指標でありこの検算には使わない — CAC定義の混用が最頻の偽陽性/偽陰性) (c) UEの継続率・単価前提 = 財務計画のコホート前提。許容幅は差異10%以内。超過時は定義差・期間差を明記して説明できる場合のみ通す。
- **トラクション⇔financial-ask**: 証拠の空白があるbelieveは、資金使途とマイルストーンがその検証を明示的に引き受ける(空白を資金使途が埋める構造)。askは「次に証明すべきbelieve」からの逆算で正当化。

## 合格基準チェックリスト(検証テスト集・実行手順つき)

1. **章タイトル通読テスト**: 全章タイトルのみ抽出して縦に並べる → 各行が主張文か(体言止め・ラベルは不合格)→ 上から読むだけで議論が進行するか(Hoffman: タイトル列だけで論旨が伝わること)。
2. **接続詞テスト**: 隣接章の間に「したがって」または「しかし」を挿入して音読。「そして」しか入らない箇所は接続不全 → 並べ替え・降格・ブリッジ命題追加(Parker/Stone の but/therefore 規則)。
3. **1文再現テスト**: 資料だけを読んだ第三者(別LLM可)に「この会社に投資すべき理由を1文で」と要約させ、統率命題と価値・因果が一致するか判定。ズレた場合はどの章が焦点を流出させたか特定。
4. **believe list対応表**: 行=believe(3〜8)、列=章。各セルに支持証拠を記入。空行(支持なしのbelieve)は証拠追加か資金使途送り、空列(何も支持しない章)はAppendix降格。
5. **競合代入テスト**: 統率命題と各章タイトルの主語を主要競合名に置換。成立してしまう文は固有性不足として書き直し。
6. **数字往復テスト**(Damodaran): 「すべての数字に物語、すべての物語に数字」。統率命題→ドライバー→財務数値の対応表が埋まるか。手順7の検算式(a)(b)(c)が全て通るか。
7. **3P自己判定**: 統率命題と各believeを possible/plausible/probable に分類し、ステージ要求水準を満たすか。
8. **媒体密度テスト**: 統率命題+believe listのみの3分送付版が自立して読めるか。30分口頭版と矛盾がないか。
9. **正典化**: 上記を通過した統率命題・believe list・ドライバーシートを1つの正典ドキュメントに固定し、全派生物(デッキ・メモ・想定問答)がそこから引用しているか。

## 致命的失敗パターン

- **「そして」デッキ**: 章が事実の羅列で因果連結がない(テスト2で全滅)。最頻の死因。
- **二兎の統率命題**: 「かつ」接合で2ストーリー並走。投資家は弱い方を突く。
- **形容詞テーゼ**: 「圧倒的」「唯一」で支える命題。Hoffmanの禁則、証拠に置換できなければ削除。
- **Why nowとMoatの自殺点**: 「巨大な追い風」を語った直後に「参入障壁は高い」と言い、なぜ追い風が競合を呼ばないか説明しない。
- **章ごとに別人の数字**: TAM章・GTM章・財務章で顧客数や単価が食い違う。ドライバーシート不在の兆候。
- **Appendix恐怖症**: 削れず全部本編に載せ、believe listと無関係な章が焦点を薄める。逆に、削除で正典から消して質疑で答えられなくなるのも失敗。
- **命題の無断変更**(IR): ラウンドや四半期ごとに統率命題が入れ替わり、投資家の学習が毎回リセットされる。

## ステージ差

- **Seed**: concept-driven前提(Hoffman)。統率命題は変化/インサイトの因果に比重、3Pはplausibleで可。believe 4〜6個、チームと洞察の証拠比重が高い。証拠の空白は許容されるが、全空白に検証パス必須。アークはQ1/Q2が多い。類推(ピッチ・バイ・アナロジー)は有効だが「悪い類推なら無い方がまし」。
- **Series A〜Growth**: concept→dataの移行点。統率命題に再現性の因果(UE成立・GTM再現)を組み込み、believeごとに実データを割当。数字往復テスト(6)とドライバーシート検算が必須ゲート。アークはQ3+データ前倒しへ寄る。
- **IPO・IR**: 統率命題=中期の一貫命題として正典化し、四半期開示は同じ命題のKPI更新として書く(命題変更時は理由を開示)。3Pはprobable必須、believe listは「投資家が織り込む前提」として自ら開示し、ベアケース・リスクを併記。アークは成長可能性資料の制度順に写像し、Why nowは「市場環境」、Moatは「競争力の源泉」、ドライバーシートは「事業計画とKPI」に対応させる。

## 出典(URL)

- Reid Hoffman, LinkedIn's Series B Pitch to Greylock: https://www.reidhoffman.org/linkedin-pitch-to-greylock/
- Paul Graham, How to Convince Investors: https://paulgraham.com/convince.html
- Sequoia Capital, Writing a Business Plan: https://sequoiacap.com/article/writing-a-business-plan/
- Andy Raskin, The Greatest Sales Deck I've Ever Seen: https://medium.com/the-mission/the-greatest-sales-deck-ive-ever-seen-4f4ef3391ba0
- Andy Raskin, The Making of a Great Strategic Narrative: https://medium.com/the-mission/the-making-of-a-great-sales-narrative-978938b3926
- April Dunford, How to build a killer sales pitch(Lenny's Newsletter): https://www.lennysnewsletter.com/p/how-to-build-a-killer-sales-pitch
- Aswath Damodaran, Narrative and Numbers(blog): https://aswathdamodaran.blogspot.com/2017/01/narrative-and-numbers-how-number.html
- Aswath Damodaran, Narrative and Numbers: Valuation as a Bridge(講義PDF): https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/narrativeandnumbers.pdf
- Robert McKee の controlling idea(value+cause)解説: https://www.shortform.com/blog/what-is-a-controlling-idea/
- Parker/Stone の but/therefore 規則: https://perell.com/note/but-therefore-rule/
- Nancy Duarte, 3-Act Structure / sparkline: https://www.duarte.com/blog/business-communication-demands-3-act-story-structure/
- VC投資委員会メモの「何を信じる必要があるか」基準: https://thevcfactory.com/investment-committee-memos/
- Barbara Minto『The Pyramid Principle』(書籍、SCQAと章タイトル主張文化の原典)
