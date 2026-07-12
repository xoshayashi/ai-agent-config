# product-strategy — イメージの湧くプロダクト戦略・ソリューション提示・プロダクトロードマップ

## 一本のストーリーへの接続

- 直前(課題/Why Now)から:「この変化と痛みが放置されている。**したがって**、まず最も痛い一点(楔)をこの製品で解く」。課題スライドで描いた具体的な人物・ワークフローを、そのままソリューション節の主語として再登場させる。人物・場面・固有名詞を変えない。
- 直後(市場規模/GTM/財務)へ:「楔で得た顧客・データ・ワークフロー支配が拡張の権利になる。**したがって**、TAMは"今の製品の市場"でなく"拡張後に取れる市場"として読める」。ロードマップの各段が市場規模スライドのセグメント分解、および財務計画の売上ドライバーと1対1で対応していること。
- 約束の地(Promised Land)との関係:製品は主役ではなく「顧客を約束の地へ運ぶ魔法の贈り物」(Raskin)。ソリューション節の冒頭は製品名でなく「顧客の新しい状態」の再提示から始め、製品はその実現手段として2番目に出す。
- アナロジー(「◯◯業界の△△」等)は課題〜ロードマップ〜市場規模まで全節で同一のものを使う。節ごとに違う比喩を出さない。

## ベスト構成(節立てレベル)

### 節1. ソリューション提示 — Before/After(スライド1枚)

1. 左に Before:実在顧客の現行ワークフローを工程・時間・関与者数で描く(例:「経理の田中さんは月初3日間、5システムから手作業で突合」)。抽象語(効率化・DX・シームレス)は禁止。固有名詞・数字・情景に置換する(Heath「知の呪い」対策)。
2. 右に After:同じ人物の新しい1日。削減された工程と生まれた時間の使い道まで書く。
3. 差分を1つの数字で締める(「3日→20分」「エラー率2.1%→0.05%」)。数字は実顧客の実測値。推定なら推定と明記。

### 節2. プロダクトの実体 — 10秒で伝わるビジュアル(スライド1枚)

- 実物のスクリーンショット1枚を大きく。中核ワークフローの「価値が見える画面」(ダッシュボード、成果物、判定結果)を選ぶ。設定画面・管理画面は出さない。
- ライブなら30秒デモ、資料ならGIF/動画リンクまたは3コマの画面遷移。「説明」より「実物」(Bloomberg Beta: "One is a description of a thing; the other is the thing itself")。
- キャプションはJTBD言語で1行:「◯◯(顧客)が△△(状況)のとき、□□(進歩)できる」。機能名の羅列は書かない。

### 節3. プロダクト戦略 — 楔→拡張→プラットフォームの3幕(スライド1〜2枚)

- **第1幕(楔)**:単一ユースケース・単一バイヤー・実測KPIで語る(Harvey=M&A文書レビュー、Moveworks=ITチケット削減率)。楔の合格条件は「導入が容易(行動変容が小さい)」×「小規模チームでも供給可能」(Every)。
- **第2幕(拡張)**:楔で得た「支配点(control point)」を明示し、そこからの拡張パターンを1つ選んで宣言する(Tidemark)——(a) ワークフロー隣接(ServiceNow型)、(b) 金流追随(決済・与信へ、Toast/Coupa型)、(c) 単一の真実源=System of Record化(Salesforce型)、(d) データ×データの掛け合わせ。次モジュールは「最も野心的」でなく「データ・バイヤー・GTMの重複が最大」のものを選んだと説明する。
- **第3幕(compounding/プラットフォーム)**:製品同士が売上・データで相互強化するループを1枚の因果図で描く(Amazon flywheel: 品揃え→体験→トラフィック→出品者→品揃え。自社版は矢印4〜6本に制限)。Figma型の実証数値(複数製品利用率76%、NDR132%)のように「拡張が既に起きている証拠」を添える。
- 各幕の遷移条件(「NDR120%到達で第2幕へ」等)を書き、幕の順序を飛ばさない。プラットフォーム宣言は楔の証明後(通常Series B以降)。

### 節4. ロードマップ — 機能リストでなく市場獲得の物語(スライド1枚)

- 縦軸=獲得する顧客セグメント/解くジョブ、横軸=Now/Next/Later(日付でなく確度)。セルには機能名でなく「誰に何ができるようになるか」を書く。
- Now:今回調達資金で完成させるもの。スコープ確定済みのみ載せる(粒度が粗いとここで信頼を失う)。Next:方向性のみ、日付なし。Later:選択肢として提示。確度の傾斜で約束しすぎを防ぐ(Now Next Later法)。
- 資金との接続:Nowの各項目に「達成マイルストーン=次ラウンドの証明事項」を対応させる(Seedの終着点がSeries Aの審査項目になる設計)。使途とマイルストーンが対応しないロードマップは書かない。

### 節5. 技術優位の翻訳(該当する場合、スライド1枚)

- 3行変換を必ず通す:①技術事実(「独自アルゴリズムで40倍高速」)→②顧客価値(「創薬ターゲット同定18ヶ月→6週間」)→③経済性(「臨床入りが1年早まる=パートナーのNPVが◯◯増、当社粗利◯%」)。①だけで終わる技術説明は削除。
- 経済性の語彙は粗利率・処理単価・速度・精度・導入リードタイムに限定。投資家の問い(コスト削減か/新ワークフロー解放か/意味ある性能差か/防御性か)に1つ以上明答する。

### 節6. AIプロダクトの追加問答(AI企業のみ、スライド0.5〜1枚)

- モデル依存リスクへの答えを先回りで明記する。有効な答えは3系統のみ:(a) 独自データ(顧客利用で生まれ複製不能なもの)、(b) ワークフロー統合の深さ(スイッチングコスト)、(c) 自社モデル/モデル非依存アーキテクチャ。資金調達に成功したAI企業のデックはほぼ全てこれを明示的に扱う。
- データフライホイールは主張でなく実証で語る:「データ量→精度→利用→データ」のループを、実測の精度改善カーブ(例:「顧客100社時点で誤検知率が半減」)で裏づける。数値のないフライホイール図は載せない。
- 「基盤モデルが進化したら不要になるか」への答えを1行用意する(進化はコスト低下として自社に取り込まれる構造か、を示す)。

## 合格基準チェックリスト

- [ ] ソリューション節の第1文が製品名でなく「顧客の新しい状態」で始まる
- [ ] Before/Afterが同一人物・同一ワークフローで、差分が実測数字1つで締まる
- [ ] 抽象語(効率化/シームレス/DX/次世代)がソリューション節にゼロ
- [ ] 実物スクリーンショットが1枚あり、初見者が10秒で「何をする製品か」を言える(第三者テスト)
- [ ] 楔が単一ユースケース・単一バイヤー・実測KPIで定義されている
- [ ] 拡張の根拠が「支配点」(データ/金流/ワークフロー/真実源)として名指しされている
- [ ] フライホイール図の矢印が6本以下で、少なくとも1辺に実測値がある
- [ ] ロードマップの行が顧客セグメント/ジョブで、機能名の行がない
- [ ] Now項目の全てが今回調達の使途・マイルストーンと対応し、次ラウンドの証明事項に接続している
- [ ] Next/Laterに日付が書かれていない
- [ ] 技術主張の全てが「技術→顧客価値→経済性」の3行変換を通過している
- [ ] (AIの場合)モデル依存リスクへの答えが(a)(b)(c)いずれかで明記され、フライホイールに実測値がある
- [ ] アナロジーが資料全体で1つに統一されている
- [ ] ロードマップ各段が市場規模スライドのセグメントと財務モデルの売上ドライバーに対応している

## 致命的失敗パターン

1. **楔の証明前のプラットフォーム宣言**:「私たちは◯◯のOSです」から始める。楔のKPIが出るまでプラットフォーム語は封印(実例上、宣言はSeries B/C以降)。
2. **機能リスト型ロードマップ**:Q別に機能名を並べる。→ 日付は確約と読まれ、未達が次回調達時の負債になる。市場・セグメント獲得の物語に書き換える。
3. **知の呪い**:創業者にだけ見えている価値を抽象語で書く(「業務を最適化」)。→ 初見者テストで「誰の何が変わるか」を言えなければ書き直し。
4. **Before/Afterの人物すり替え**:Beforeは現場担当、Afterは経営者視点など、主語が変わって変化が追えない。
5. **数字なしフライホイール**:矢印だけの循環図。ループが回っている実測値が1つもないと「願望図」と読まれる。
6. **技術自慢の翻訳放棄**:「40倍高速」「特許◯件」で止まり、粗利・速度・精度への換算がない。
7. **拡張の飛び石**:楔と第2製品の間にデータ・バイヤー・GTMの重複がない(重複80%目安を大きく割る)拡張を描く。
8. **AIリスク問答の回避**:モデル依存・コモディティ化の問いをデックで扱わない。→ 質疑で初出になると準備不足と評価される。
9. **デモ/スクショの不在または管理画面の提示**:文章だけの製品説明、または価値の見えない画面を載せる。

## ステージ差

- **Seed**:第1幕(楔)に紙面の8割。Before/Afterは1社の実話(デザインパートナーで可)。フライホイールは「設計図+初期兆候」でよいが、その旨を明記。ロードマップはNow(12〜18ヶ月)中心、Later は1行。ナラティブ型ピッチ(Kwok)として「なぜこの楔が正しい入口か」の secret を語る。
- **Series A〜Growth**:楔の実証数値(KPI、NDR、複数製品利用率)を主役に、第2幕=拡張の初期証拠(2製品目のアタッチ率、クロスセル実績)を示す。支配点→拡張パターンの明示が必須。ロードマップはNow/Next2段を厚くし、各段を調達使途・次ラウンド証明事項に接続。データフライホイールは実測カーブで裏づけ。
- **IPO・IR**:第3幕(compounding)が主役。Figma S-1型に「複数製品利用率」「NDR」「新製品の売上寄与率」で拡張の再現性を定量開示。ロードマップは個別機能でなく「成長レバー」(新製品・新セグメント・新地域・単価)として語り、ガイダンスと矛盾しない粒度に落とす。未確定の製品計画は開示しない(選択的開示・過剰約束リスク)。多製品企業の評価プレミアム(単一製品比)を比較会社選定の論拠に使える。

## 出典(URL)

- Andy Raskin, The Greatest Sales Deck I've Ever Seen — https://medium.com/the-mission/the-greatest-sales-deck-ive-ever-seen-4f4ef3391ba0
- Andy Raskin, Pitch the Promised Land — https://medium.com/firm-narrative/pitch-like-moses-87540a85b236
- Every, The Product Wedge: A Complete Guide — https://every.to/divinations/product-wedges-a-complete-guide
- Every, The Market Wedge — https://every.to/divinations/the-market-wedge-how-to-pick-your-initial-market
- NFX, 12 Killer Wedges — https://www.nfx.com/post/finding-your-killer-wedge
- Kevin Kwok, kwokchain(narrative/inflection/traction pitch)— https://kwokchain.com/
- Tidemark, Platforms of Compounding Greatness(control points・拡張4パターン)— https://www.tidemarkcap.com/post/platforms-of-compounding-greatness
- Figma S-1 — https://www.sec.gov/Archives/edgar/data/1579878/000162828025033742/figma-sx1.htm
- Tanay Jaipuria, Figma S-1 Breakdown — https://www.tanayj.com/p/figma-s-1-breakdown
- Sequoia Capital Pitch Deck Template 解説 — https://vcbeast.com/sequoia-capital-pitch-deck-template
- OpenVC, Product Slide Best Practices — https://www.openvc.app/blog/product-slide
- OpenVC, Roadmap Slide Best Practices — https://www.openvc.app/blog/roadmap-slide
- Screenhance, Pitch Deck Screenshot Guide — https://screenhance.com/blog/pitch-deck-screenshot-guide
- Aakash Gupta, Now Next Later Roadmap — https://www.aakashg.com/now-next-later-roadmap/
- Capwave, Milestone Mapping — https://capwave.ai/blog/milestone-mapping-a-founders-guide-to-traction-before-the-round
- Viktori, Deep Tech Pitch Strategy — https://viktori.co/deep-tech-pitch-strategy/
- Tran.vc, How to Pitch Deep Tech Without Oversimplifying — https://www.tran.vc/how-to-pitch-deep-tech-without-oversimplifying/
- Startups.com, AI Moat / Data Flywheel — https://www.startups.com/lexicon/ai-moat / https://www.startups.com/lexicon/data-flywheel
- AI Funding Tracker, Best AI Startup Pitch Decks — https://aifundingtracker.com/best-ai-startup-pitch-decks/
- 100founders, Narrow Before You Scale(楔→プラットフォーム宣言の時期)— https://www.100founders.ai/p/narrow-before-you-scale-the-wedge
