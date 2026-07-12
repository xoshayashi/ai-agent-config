# business-model-unit-economics — 優位性のあるユニットエコノミクスから成り立つビジネスモデル

## 一本のストーリーへの接続(直前・直後の要素と「したがって」で繋がる書き方)

- 受け取るバトン(直前=プロダクト・トラクション要素から):「顧客が価値を感じ、使い続けている」。**したがって**この要素では「その価値は経済的に回収可能であり、1顧客あたりで再現的に儲かる」ことを示す。トラクションが「売れる」の証明、本要素は「売れるほど儲かる」の証明、と役割を明確に分離する。
- 渡すバトン(直後=成長戦略・資金使途要素へ):「1単位の経済が成立し、投下資本が予見可能な期間で回収される」。**したがって**「今回調達する資金は、この成立済みの経済にレバレッジをかける拡大投資である」と接続する。資金使途スライドの説得力は、本要素のCAC回収期間とバーンマルチプルの数値に全面的に依存する。
- 一文テスト:この要素の主張は「当社は◯◯(顧客)から◯◯(value metric)に応じて課金し、1顧客あたり獲得コストを◯ヶ月で回収、粗利ベースLTVはCACの◯倍。この経済は規模とともに◯◯の理由で改善する」という4文に圧縮できなければならない。圧縮できない時点で構成をやり直す。
- 赤字企業の場合の必須翻訳:「全社赤字=ユニット黒字×拡大投資額」に分解して直後の資金使途に橋渡しする。「成長投資を止めれば黒字化する」構造を数式(貢献利益合計−成長投資=営業損益)で見せる。

## ベスト構成(節立てレベルで具体)

### 節1: 収益モデル一枚図(How we make money)
- 一文で言えるモデル(YC基準: 投資家が一文で他人に説明できなければ複雑すぎる)を見出しに置く。例「予約成立ごとにGMVの◯%を受け取る」。
- 価値の流れ図を1枚で: 登場人物(顧客/供給者/自社/パートナー)を左右に配置し、①価値(モノ・サービス・データ)の流れ、②カネの流れ、③自社の課金ポイント(どの矢印の何%か・何円か)を色分けで示す。課金ポイントは1画面で最大でも2〜3個。
- 料金体系の設計論理を1ブロックで: 採用したvalue metric(シート/利用量/成果/GMV%)と、それが「顧客の得る価値に比例して伸びる」根拠を1行で述べる。usage/hybrid型はNRRが構造的に高く出る(usage型平均NRR120%+ vs サブスク型110%)ことを引用可能。マーケットプレイスのtake rateは摩擦(Gurley「A Rake Too Far」)とのトレードオフなので、「なぜこの%が長期均衡か」を代替手段・付加価値で正当化する。
- DocSend調査で、調達成功デッキはビジネスモデル節の閲覧時間が94%長い。この1枚に最も情報設計コストをかける。

### 節2: ユニットエコノミクスの現在値(単位定義→数値)
- 冒頭で「1単位」を宣言する(1顧客/1注文/1席/1店舗/1車両)。単位の選定理由(意思決定の最小単位であること)を1行。
- 標準指標を表で: paid CAC(blendedと併記、paidを主)、粗利ベースLTV、LTV/CAC、CAC回収期間(粗利ベース)、粗利率、NRRまたはリピート率、バーンマルチプル。定義(分子・分母・期間)を脚注で固定する。
- 各数値の隣にベンチマーク帯(下記チェックリスト参照)と自社の位置を並記。「業界水準表の中に自社をプロットした1枚」が最強の形式。

### 節3: 優位性の分解(なぜ自社のUEは構造的に良いか)
- 「良い数値」ではなく「良い数値を生む構造」を主張の単位にする。分解の型は3系統:
  1. **獲得効率の構造**: PLG/バイラル/供給側持ち込み需要などによりpaid依存度が低い(blended CACとpaid CACの差分と、organic比率の推移で立証)。
  2. **粗利構造**: 原価の構成(ソフトウェア比率、自動化率、AI推論原価)が競合類型より軽い。AIネイティブは推論原価込み粗利を明示し、原価低減ロードマップ(モデル小型化・キャッシュ・ルーティング)を添える。
  3. **維持・拡張構造**: value metricが顧客成長に連動しNRRが構造的に110%+になる、スイッチングコスト・データ蓄積で後期コホートほど残存が良い。
- 比較の作法: 上場類似企業・業界ベンチマーク(KeyBanc/Benchmarkit/Bessemer等の公表値)と同一定義で並べる。競合が非公開なら「業界中央値」との比較に留め、出典を必ず付す。定義をずらした比較は一発で信用を失う。

### 節4: コホートで示す改善トレンド(時系列の証明)
- 四半期または月次コホートで、①CAC回収曲線(横軸:経過月、縦軸:累積粗利/CAC、100%線を明示)、②残存・拡張曲線(flattenする=LTVが計算可能になる)を重ね描きし、新しいコホートほど曲線が上/左に来ることを示す。
- 改善の因果を1行ずつ添える(例「23Q4コホート以降の回収短縮は、オンボーディング自動化によるS&M人件費/顧客の低下による」)。数値の改善だけ見せて理由を言わないのは弱い。
- 平均でなくコホート別に見せること自体が「悪化を平均で隠していない」というシグナルになる。悪いコホートがあるなら先に自分から開示し、学習内容を添える。

### 節5: スケールとUEの関係(改善する構造/悪化する圧力の両面開示)
- 改善側: 規模の経済(固定費按分・仕入交渉力)、ネットワーク効果(流動性向上→マッチ率・fill rate改善)、データ蓄積(与信・レコメンド精度→転換率/粗利改善)のうち、自社に実在するものだけを、既に観測された証拠(密度の高い地域ほどUEが良い、等のスケール断面データ)付きで主張する。
- 悪化側を自ら開示: チャネル飽和によるCAC逓増、後期セグメントのLTV劣化(AOV低下・リピート低下)、enterprise移行によるセールスコスト増。原則は「CAC上昇はLTVが同時に上昇していれば持続可能、LTV横ばいでのCAC上昇は罠」。次セグメントのUE仮説と検証計画を添えることで、リスク開示を実行計画に変換する。
- この節の結論が「したがって追加資本のリターンは予見可能」となり、資金使途要素へ接続する。

## 合格基準チェックリスト(検証可能な形)

- [ ] 収益モデルが一文で書かれており、その一文に課金主体・課金トリガー・料率(または単価)が全部入っている
- [ ] 価値とカネの流れ図が1枚に収まり、課金ポイントが視覚的に特定できる
- [ ] value metricの選択理由(顧客価値との比例性)が明文化されている
- [ ] 「1単位」の定義が宣言され、全指標が同じ単位で計算されている
- [ ] CACはpaid CACを主、blendedを従として両方開示している(a16z基準)
- [ ] LTVは粗利ベースで計算され、粗利率・チャーン(またはリピート率)の前提が脚注にある
- [ ] LTV/CAC 3x+(SaaS/消費者の目安帯。5x超は成長投資不足の可能性も言及できる)
- [ ] CAC回収: SaaSはBessemer帯(0-6ヶ月best/6-12better/12-18good/18-24懸念)に対する自社位置を明示。ACV・セグメント別基準(SMB<12ヶ月、mid<18、enterprise<24)で評価している
- [ ] 粗利率: SaaS 70-80%(業界中央値77%)、AIネイティブは推論原価込みで50-60%帯が現実(a16z/ICONIQ)であることを踏まえ、乖離の説明と改善ロードマップがある
- [ ] NRR: 中央値101%・上位111%+(Benchmarkit 2025)に対する自社位置。マーケットプレイスはGMVリテンション、D2Cはコホート別リピート率(6ヶ月40%+が強い水準)で代替
- [ ] マーケットプレイス: GMVと純収益を混同していない。take rateの水準根拠(Gurleyの摩擦論)、流動性指標(fill rate/マッチ時間/市場深度)を提示
- [ ] D2C: 貢献利益率(健全帯目安20-45%、20%未満は要説明。中央値は2021年35%→2025年22%へ圧縮)を全変動費控除後で提示
- [ ] バーンマルチプル: <1x amazing / <2x good(Sacks)。悪い場合は改善トレンドで補う
- [ ] Rule of 40(成長率+利益率≧40%)はGrowth以降で言及。未達なら到達パスを示す
- [ ] コホートチャートが最低2枚(回収曲線・残存曲線)あり、直近コホートが改善している。悪化コホートを隠していない
- [ ] 全社赤字の場合、「貢献利益合計−成長投資=営業損益」の分解表がある
- [ ] スケールでUEが改善する根拠が、願望でなく既観測データ(地域別・密度別・コホート別の断面)で示されている
- [ ] CAC逓増・セグメント劣化リスクを自ら開示し、次セグメントのUE仮説を添えている
- [ ] すべてのベンチマーク数値に出典が付いている

## 致命的失敗パターン

1. **blended CACでの化粧**: organic込みの安いCACでLTV/CACを計算。投資家はpaid CACで再計算し、その瞬間に他の数値も疑われる。
2. **売上ベースLTV**: 粗利を掛けないLTVはSaaSで1.3〜1.4倍、低粗利業態で3倍以上過大になる。定義脚注がない時点で減点。
3. **GMVを売上のように語る**(マーケットプレイス/フィンテック): take rate後の純収益と粗利で語れないと、モデル理解が浅いと判定される。
4. **UE未成立でスケール資金を要求**: 「まだ1単位で赤字だが広告費で伸ばす」はステージ不一致。UE成立前はUE成立のための資金、成立後に拡大資金、の順序を崩さない。
5. **平均値でコホート悪化を隠す**: 古い良質コホートが平均を支え、新規コホートが劣化しているケースは必ずDDで発覚する。先に開示しない場合、悪化そのものより「隠した」ことが致命傷になる。
6. **AI原価の外出し**: 推論コストをR&D計上して粗利80%を演出する。上場水準の会計精査で崩れるうえ、原価構造の理解不足と見なされる。
7. **料金体系の論理欠落**: 「競合がこの価格だから」だけのpricing。value metricと顧客価値の比例関係を語れないと、NRR・拡張の将来性を主張できなくなる。
8. **スケール改善の無根拠な宣言**: 「規模の経済で改善します」を断面データなしで言う。ネットワーク効果・データ効果は「既に観測された勾配」として示せない限り主張しない。
9. **複雑すぎる収益モデル**: 課金ポイントが5個以上、一文で説明不能。YC基準では投資家が一文で説明できないモデルは通らない。主収益源1つに絞って語り、副収益は「将来のレバー」に格下げする。

## ステージ差(Seed / SeriesA〜Growth / IPO・IR)

- **Seed**: 実測UEは不要な場合が多い。求められるのは①一文の収益モデル、②value metricの設計論理、③初期顧客の単価・粗利の「点」の証拠、④「どのUE指標を次ラウンドまでに成立させるか」の宣言。ベンチマーク表は「目指す帯」として使う。捏造めいた精緻なLTV計算(顧客10社で60ヶ月LTV等)はむしろ減点。
- **SeriesA〜Growth**: 本要素が最重量になるステージ。実測コホート必須。paid CAC・粗利ベースLTV・CAC回収・NRR・バーンマルチプルをベンチマーク帯と並記し、節3(構造優位の分解)と節4(コホート改善)を厚くする。Growth後半はRule of 40、セグメント別UE(SMB/mid/enterprise別のCAC回収)、次セグメントのUE仮説まで要求される。
- **IPO・IR**: 監査済み会計との整合が最優先。非GAAP指標(LTV/CAC等)は定義を目論見書・決算説明で固定し毎期同一定義で開示。UEは「単位あたり経済」から「セグメント別の限界利益率と中期マージン目標」への翻訳が必要。スケール改善ストーリーは中期経営計画のマージンブリッジ(粗利改善×S&M効率化×固定費レバレッジの寄与分解)として提示する。悪化圧力(CAC逓増等)はリスク情報として先回り開示し、対応策とセットで語る。

## 出典(URL)

- a16z, 16 Startup Metrics(paid vs blended CAC、LTV定義): https://a16z.com/16-startup-metrics/
- a16z, Why Do Investors Care So Much About LTV:CAC?(3x目安・5年以内): https://a16z.com/why-do-investors-care-so-much-about-ltvcac/
- a16z, 13 Metrics for Marketplace Companies(GMV/take rate/流動性): https://a16z.com/13-metrics-for-marketplace-companies/
- a16z, GMV Retention: https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/
- a16z, The New Business of AI(AI粗利50-60%帯): https://a16z.com/the-new-business-of-ai-and-how-its-different-from-traditional-software/
- Bill Gurley, A Rake Too Far(take rateと摩擦): https://abovethecrowd.com/2013/04/18/a-rake-too-far-optimal-platformpricing-strategy/
- David Sacks, The Burn Multiple(<1x amazing/<2x good): https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200
- Bessemer, Cloud Computing Metrics(CAC回収 good/better/best帯): https://www.bvp.com/atlas/cloud-computing-metrics
- Benchmarkit, 2025 SaaS Performance Metrics(粗利中央値77%、NRR中央値101%/上位111%+): https://www.benchmarkit.ai/2025benchmarks
- Brad Feld / Rule of 40(定義と由来): https://en.wikipedia.org/wiki/Rule_of_40
- OpenView, SaaS Pricing Insights(value metric・usage型NRR差): https://openviewpartners.com/blog/saas-pricing-insights/
- Y Combinator, How to Build Your Seed Round Pitch Deck(一文モデル・Business Modelスライド): https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
- DocSend / Dropbox, Pitch Deck Research(調達成功デッキはビジネスモデル節の閲覧+94%): https://www.dropbox.com/resources/docsend-pitch-deck-research
- Christoph Janz (Point Nine), CAC Payback Time の計測作法: https://medium.com/point-nine-news/the-art-and-science-of-figuring-out-your-cac-payback-time-c7d20808d51b
- Tribe Capital, Unit Economics and the Pursuit of Scale Invariance(スケールとUEの関係): https://tribecap.co/unit-economics-and-the-pursuit-of-scale-invariance/
- Fairview, D2C Unit Economics(貢献利益・リピート率帯): https://getfairview.com/blog/d2c-unit-economics
- Jordan Glickman, The CAC Trap(チャネル飽和・後期コホート劣化): https://www.jordanglickman.com/writing/cac-trap-scaling-ad-spend
