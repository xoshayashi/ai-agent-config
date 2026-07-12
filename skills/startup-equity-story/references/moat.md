# Moat — 圧倒的な防御可能性の立証

対象: 「なぜ勝ち続けられるのか」を、名指しされたPowerと観測可能な証拠で立証する要素。
基礎式(Helmer): 企業価値 = 市場規模 × Power、Power = 長期シェア × 長期差分マージン。Moat節は財務計画のマージン・シェア前提を裏書きする「担保」であり、飾りではない。

## 一本のストーリーへの接続(「したがって」で繋ぐ)

- 直前(Why now / トラクション)から: 「窓は開いた(Why now)。窓は競合にも開いている。**したがって**、窓の期間中に先に入った者だけが積める資産Xを、我々はすでにx%積んだ」。Moatの冒頭1文は必ず「窓は皆に開く」ことを自認してから始める。ここを飛ばすとWhy nowと時間軸が矛盾する。
- トラクションから: トラクション節の数字(NRR、オーガニック比率、密度別単位経済)は、Moat節で「Powerの証拠」として再登場させる。同じ数字を2つの意味で使う(勢いの証明→構造の証明)。
- 直後(市場規模・財務計画)へ: 「この障壁が持続する。**したがって**、計画上の粗利率xx%・シェアxx%は、競争圧力下でも維持できる前提として妥当」。Moatなしの高マージン計画は投資家に即座に矛盾として検出される。
- Why not Google への回答はこの節が担う。競争環境スライドに逃がさない。

## ベスト構成(節立て)

### 1. Power宣言(1〜2個を名指し)
- 7 Powersのうち**主たるPower 1つ+補助1つまで**を名指しする。3つ以上の主張は「どれも弱い」という自白として読まれる。
- 各Powerを「便益(コスト優位 or 価格プレミアム)」+「障壁(競合が模倣しない/できない理由)」の2文で書く。便益だけ(=良い製品)はPowerではない。
- AI領域では a16z型の4分類(data flywheel / workflow embedding / distribution / network effect)のどれかへのマッピングも併記する。「proprietary AI」単体は減点対象。

### 2. メカニズム(フライホイール図)
- ループは3〜5辺。例: 利用↑ → データ↑ → 精度↑ → 転換率・継続率↑ → 利用↑。
- **各辺に実測値を置く**。最低1辺は実測相関(コホート比較・地域比較・相関係数)、残りはSeedなら計画値でも可。ただし矢印にラベルだけの概念図は禁止。
- 「この一周が回るたびに何が蓄積し、後発が同じ一周を回すのに何年・何億円かかるか」を1文で明示する。

### 3. 証拠(Power別・観測可能指標)
Powerごとに使う指標を固定する。数字は必ず競合または業界水準との比較で示す。

| Power | 観測可能な証拠指標 |
|---|---|
| 規模の経済 | 規模別コホートの単位コスト低下カーブ、固定費の対売上比率低下、競合対比の粗利差(pt) |
| ネットワーク効果 | 密度と単位経済の相関(密度上位市場のCAC・マッチ率・充足時間 vs 下位市場)、オーガニック流入比率の上昇、CAC低下トレンド、マルチテナンシー率(併用率)の低下 |
| カウンターポジショニング | 大手が模倣した場合の**既存収益の共食い額を試算して提示**(incumbentのセグメント別収益構造から)。「模倣しない合理的理由」を金額で示す |
| スイッチングコスト | GRR(>90%)・NRR(B2Bで>110〜120%)、解約時の移行コスト実測(データ移行工数・再学習時間・API/ワークフロー統合本数)、解約ヒアリングでの「移行断念」事例 |
| ブランド | 同等機能比の価格プレミアム(+x%)、指名検索・オーガニック比率、値上げ後の解約率、対競合でマーケ費率が低いのに成長率が同等以上、価格/ミックス主導の成長 |
| コーナードリソース | 排他性の法的裏付け(独占契約・特許の請求項・規制ライセンス)、代替調達の推定コストと年数 |
| プロセスパワー | 歩留まり・リードタイム・品質指標の競合差と、その運用が模倣に要する年数の根拠(組織・暗黙知の蓄積過程) |

ネットワーク効果を主張する場合の追加規律:
- **種類を特定する**(NFX 16分類: direct系5種+Hub-and-Spoke / 2-sided 3種 / data / tech performance / expertise / social系4種)。「ネットワーク効果があります」は不合格。
- 強度順(Physical > Protocol > Personal Utility > … > Bandwagon)を踏まえ、自分の型の限界を自認する。漸近型マーケットプレイス(配車の「待ち4分」以降は価値逓減)なら、閾値到達後の防御は別のPowerで補うと明記。
- データNW効果は「量」でなく「**幅と鮮度**」で語る。蓄積データが精度→転換率に効いた実測(モデル改善ログ×事業KPI)を1点は置く。

### 4. 敵対的テスト(反証質問と回答)
以下を自問し、少なくとも2つへの回答を本文に組み込む。
1. 資金無制限の競合が2年で我々の資産を複製できるか。できないなら、複製に**時間そのもの**が必要な要素はどれか(データ蓄積・埋め込み・供給網・規制)。
2. 大手が同機能を無料配布したら顧客は移るか。→ カウンターポジショニング(共食い試算)か、埋め込み(移行コスト実測)で答える。
3. 基盤モデルの次リリースで表層機能が複製されたら何が残るか。→ 4分類のどれが残るかを名指し。
4. 顧客が明日解約すると何を失うか。金額・工数に換算する。
5. 「先行者利益・技術力・チームの実行力・特許出願中」しか答えが出ないなら、この節はまだ書けない。プロダクト設計に戻る。

### 5. Why nowとの整合(時限的な窓 × 蓄積型資産)
- 定型: 「窓は20XX〜20XX年に開いている(Why nowの根拠)。窓の期間中にしか積めない資産はXである。我々はT年分・x%をすでに積んだ。窓が閉じた後、Xが後発への障壁になる」。
- Moatが窓と無関係な静的資産(特許のみ等)だと、Why nowと接続せず「なぜ今なのか」が崩れる。逆にWhy nowだけ強くMoatが無いと「窓に皆が殺到して価格競争」で終わる。両方を同じ資産Xで貫くこと。

### 6. 深化予測(動的Moat)
- Moatは静的でない。「顧客+1、データ+1のたびに堀が深くなる」構造を、次ラウンドまでに証明する指標と目標値で締める(例: 「Series Aまでに密度2倍市場でCAC▲30%を実証する」)。一度きりの技は複製される。複利のループだけが差を戻させない。

## 合格基準チェックリスト(検証可能)

- [ ] 7 Powersの1〜2個が名指しされ、各々に便益と障壁が1文ずつある
- [ ] 主張するPowerごとに、上表の観測指標のうち最低1つの実数がある(Seedは初期シグナル1点+測定計画で可)
- [ ] 数字に比較対象(競合・業界水準・自社の低密度市場)が付いている
- [ ] ネットワーク効果を主張する場合、16分類のどれかが特定され、臨界質量の閾値仮説がある
- [ ] フライホイール図の全辺にラベル+数字(実測 or 計画と明記)があり、概念図で終わっていない
- [ ] 「資金無制限の競合が2年で複製できるか」への回答が本文に含まれ、時間依存の要素が特定されている
- [ ] 大手参入シナリオに、カウンターポジショニング(共食い試算)か移行コスト実測のどちらかで答えている
- [ ] Why nowの「窓」とMoatの「蓄積資産」が同じ資産Xで貫かれている
- [ ] 財務計画の粗利率・シェア前提と、この節の主張が矛盾していない
- [ ] 「先行者利益」「技術力」「実行力」「情熱」がMoatとして単独主張されていない

## 致命的失敗パターン

1. **非Moatの主張**: 先行者利益・技術力・実行力・スピード・特許出願中を堀と呼ぶ。いずれも急速に劣化する優位であり、投資家は即座に減点する。
2. **全部盛り**: 7 Powersを4つ以上主張。強い会社ほど1つを深く証明する。
3. **概念フライホイール**: 矢印とラベルだけで数字がないループ図。「回っている証拠」がない自己言及。
4. **時間矛盾**: Why nowで「窓が今開いた」と言い、Moatで「すでに堀が深い」と言う。開いたばかりの窓に深い堀は掘れない。「積み始めた資産の速度」で語るのが正。
5. **種類不明のネットワーク効果**: 型・臨界質量・測定値のないNW効果主張。
6. **proprietary AI/独自アルゴリズム**: 基盤モデルの次リリースで消える表層をMoatと呼ぶ。データ・ワークフロー・流通・NWのどれに還元されるかを言えない場合は主張しない。
7. **便益のみ**: 「製品が優れている」はPowerの半分でしかない。障壁(模倣しない/できない理由)が欠落。
8. **裸の数字**: NRR125%等を比較水準なしに提示。文脈のない数字は検証不能として扱われる。

## ステージ差

### Seed
- 要求水準: **path to defensibility**。堀の完成ではなく設計図+初期シグナル。
- 書くべきもの: (a) Powerの名指しとメカニズム(プロダクト/GTMが資産を積む構造になっている設計上の証拠)、(b) 初期シグナル1点(初期コホートのオーガニック比率、データ蓄積速度、初期顧客の埋め込み深度)、(c) 「何をいつまでに測って証明するか」の宣言。
- この段階の実際の優位はドメイン知識とスピード(=劣化する優位)であることを自認し、それを「劣化する前に蓄積型資産へ転換する計画」として書くと誠実かつ強い。

### Series A〜Growth
- 要求水準: **定量実証の開始**。堀が「効き始めている」計測データ。
- 目安: NRR 110〜120%以上・GRR 90%以上(B2B)、粗利70%以上(SaaS)、密度上位市場と下位市場の単位経済の差、CACの低下トレンド、オーガニック比率の上昇、フライホイールの最低1辺の実測相関。
- Growth期はusage/dataループが審査の中心。コホートの経年深化(古いコホートほど良い単位経済)を示せると最強。

### IPO・IR
- 要求水準: **持続の実績**。機関投資家の語彙(Morningstar型: 無形資産/スイッチングコスト/ネットワーク効果/コスト優位/効率的規模)に自社のPowerを翻訳する。
- 証拠: 5〜10年スパンの粗利率の維持・拡大、シェアの安定(±2%以内)または拡大、価格/ミックス主導の成長実績(値上げしても解約率が動かない)、NRRの複数年持続、ROIC>WACCの継続。
- 目論見書・IR資料では「堀の主張」より「堀が生んだ財務実績→今後も続く理由」の順に語る。将来の堀ではなく過去の実証が主語になる。

## 出典(URL)

- Hamilton Helmer, 7 Powers(まとめ): https://blas.com/7-powers/ / https://jacobwallenberg.com/posts/notes-on-7-powers
- Acquired: 7 Powers with Hamilton Helmer: https://www.acquired.fm/episodes/7-powers-with-hamilton-helmer
- NFX, The Network Effects Manual(16分類・強度順・臨界質量): https://www.nfx.com/post/network-effects-manual
- NFX, The Network Effects Bible(4大防御性の比較): https://www.nfx.com/post/network-effects-bible
- Jerry Chen (Greylock), The New Moats / The New New Moats: https://news.greylock.com/the-new-moats-53f61aeac2d9 / https://greylock.com/greymatter/the-new-new-moats/
- Euclid Ventures, Dude, Where's My Moat?(ステージ別要求水準): https://insights.euclid.vc/p/dude-wheres-my-moat
- CRV, What Is a Moat?: https://www.crv.com/content/moat-meaning
- Chris Neumann, "What if Google Builds It?" is No Longer a Bullshit Question: https://chrisneumann.com/archives/what-if-google-builds-it-is-no-longer-a-bullshit-question
- Morningstar/VanEck, What Makes a Moat?(IPO・IR側の語彙と財務証拠): https://www.vaneck.com/us/en/investments/morningstar-wide-moat-etf-moat/what-makes-a-moat-white-paper.pdf
- VanEck, An Investor's Guide to Switching Costs: https://www.vaneck.com/blogs/moat-investing/switching-costs-build-moats/
- TIKR, How to Analyze a Company's Competitive Position and Moat(粗利・シェア安定の閾値): https://www.tikr.com/blog/how-to-analyze-a-companys-competitive-position-and-moat
- a16z 16 Startup Metrics 解説(NRR等の水準): https://easyvc.ai/blog/comprehensive-guide-to-a16z-startup-metrics-template/
- DECKO, Anthropic's Round Changes What Moat Means on Your Slide(AI時代のmoatスライド審査): https://www.getdecko.com/blog/anthropics-35b-round-changes-what-moat-means-on-your-slide
- Waveup, How to Build Your Competitive Moat(compounding moat): https://waveup.com/blog/how-to-build-your-competitive-moat/
- UiPath Series A deck 分析(フライホイール実例): https://qubit.capital/blog/lessons-from-top-ai-pitch-decks
