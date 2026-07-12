# シート構築プレイブック①：前提条件・売上計画

各シートの中身を作り込むためのベストプラクティス。出典はWeb調査
（2026-07、4ソース以上でクロスチェック）。生成時はこのプレイブックの
必須ブロックを満たし、品質チェックリストで自己検査すること。

## 前提条件（Assumptions）

### 役割と設計原則
- モデル内の全ハードコード入力を一元集約し、「どこを触れば計画が変わるか」を1シートで示す。入力と計算の分離はFAST標準・IB実務の共通原則（FAST Standard: https://fast-standard.org/the-fast-standard/, Wall Street Prep: https://www.wallstreetprep.com/knowledge/financial-modeling/）。
- 1ドライバー=1セル。同じ前提を2箇所に置かない。計算シート側にハードコードを一切残さない。
- 入力は青字。ラベルに必ず単位を含める（「解約率（年, %）」「単価（円/分）」）。全期間共通値も全期間列に同値を複製して埋め、下流は同列参照とする（年次で変えたくなったらそのセルだけ上書きできる）。
- 全入力に根拠タグ: `実績`＞`記載`（ソース資料に記載）＞`仮置き`（ベンチマーク/推定）。仮置きには出典か理由を備考列に書く。
- モデル全体の**決定準備度**を免責注記で明示する: 実績財務・実契約に接続する前は「検討用（screen-grade）」であり、意思決定利用には仮置き入力の差し替えが前提である旨をサマリーまたは前提条件の冒頭注記に置く。
- シナリオを持つ場合はBase/Upside/Downsideを列で並べ、単一スイッチセルでCHOOSE参照する。ケースごとにシートを複製しない。

### 必須ブロック
1. **需要**: セグメント別の新規獲得数または期末稼働数（年次）、解約率、（あれば）アップセル率。Janzモデルの主要ドライバー構成に準拠（Christoph Janz SaaS Financial Plan 2.0: http://christophjanz.blogspot.com/2016/03/saas-financial-plan-20.html）。
   - 解約率ベンチマーク: Enterprise 年5–10%、Mid-Market 月1–2%、SMB 月3–5%（年30%前後）、Consumerはさらに高い（Optifai: https://optif.ai/learn/questions/b2b-saas-churn-rate-benchmark/, CRV: https://www.crv.com/content/saas-churn-rate）。GRR中央値92%、NRR中央値106%（Enterprise 118% / SMB 97%）。
2. **価格**: セグメント別に固定料金（円/社/月）、従量単価（円/分・円/件）、従量利用料または利用量、導入フィー（円/件）。固定+従量+一時金の3系統を必ず分離。値引・改定率は別行。
3. **原価ドライバー**: 単位原価（円/分）、インフラ費率、決済手数料率、レベニューシェア率。
4. **人員**: 職種×年の人数と平均年収。法定福利費率は給与の約15–16%が日本の実務目安（経理プラス: https://keiriplus.jp/tips/houteifukurihi_keisan/）。採用単価も単価×人数で。
5. **OpEx率**: 家賃（円/人）、広告宣伝費（売上比% or CAC×新規数）、その他。費目ごとに最も因果的なドライバーを選ぶ（売上比%一辺倒を避ける）。
6. **CapEx・税・運転資本**: 償却年数、実効税率（日本は約30–34%）、繰越欠損金、回収・支払サイト。日本の売上債権回転期間は全業種平均約62日（Scalebase: https://scalebase.com/blog/billing-management/days-sales-outstanding）。B2B SaaSは回収1.5–2ヶ月・支払1ヶ月が無難なデフォルト。
7. **資金調達**: 期初現金、ラウンド（時期・金額・種別）。
8. **ソース照合値（Tie-out）**: ソース資料の主要数値を転記した参照ブロックを置き、モデル出力と突合する。TAM/SAM/SOMが記載されている場合は市場規模も転記し、サマリーで「売上÷SAM・売上÷TAM」のトップダウン浸透率検証行に接続する（浸透率の妥当域はSOM/SAMで数%台が説明しやすい。市場規模の再推計はモデルの役割外で、ソース資料側の責務）。記載値が2桁丸めの場合は照合許容誤差を±5%程度に緩め、その理由を注記する。

### 品質チェックリスト
1. 計算シートにハードコードがゼロ（構造定数12/365を除く）
2. 全入力行に単位・根拠タグがある。仮置きに出典または理由が付く
3. 解約率・NRR・成長率がセグメント別ベンチマークの妥当域か、逸脱に説明があるか
4. 率の上に率を重ねていない（実数ドライバーに分解されている）
5. 法定福利費・税率・サイト等の日本固有値がUS値の直輸入になっていない
6. Tie-outブロックとモデル値が一致する

### よくある失敗
- Rates-on-rates（成長率×シェア×転換率の連鎖）— 監査不能。顧客数×単価に分解する
- 数式内の隠れハードコード（`*1.1`等）
- 月次前提の12倍し忘れ、千円/円の混在 — ラベル単位で防ぐ
- タグなし前提 — 「仮置き」と明示すれば議論の土台になる
- 使わない前提行のノイズ（FASTの"Appropriate"原則）

## 売上計画（Revenue Build）

### 役割と設計原則
- 顧客数ロールフォワード×ARPUのボトムアップ。「TAM×シェア%」のトップダウンは不可（EY: https://www.ey.com/en_nl/services/finance-navigator/the-ultimate-guide-to-financial-modeling-for-startups, CFI: https://corporatefinanceinstitute.com/resources/financial-modeling/bottom-up-forecasting/）。TAM比は検算として脚注のみ。
- 獲得→顧客数→MRR/ARR→認識売上の順に流す（Janz 2.0）。
- セグメントごとに同一の行構成のブロックを複製し、最後に合算する。

### 必須ブロック
1. **顧客数ロールフォワード**（セグメント別）: 期首 / 新規（gross adds） / 解約（▲） / 期末。純増を入力にしない。認識基準が期中平均なら平均稼働行も持つ。
2. **拡張/NRR行**: アップセルが実績または価格設計上明確な場合のみ追加。gross churnとexpansionを混ぜた開示は不可（a16z 16 Startup Metrics: https://a16z.com/16-startup-metrics/）。
3. **ARPU分解**: 固定料金＋従量（利用量×単価）。コミット分とオンデマンド超過分の行分割はSnowflake型に対応（Snowflake SEC開示, Ordway: https://ordwaylabs.com/blog/rpos-for-usage-based-pricing/）。
4. **一時収益**: 導入売上＝新規×導入フィー。継続売上と必ず行を分ける（投資家はサービス売上を低く評価。a16z同上）。独立の価値がなければサブスク期間按分になる点に注意（Maxio ASC606: https://www.maxio.com/blog/saas-revenue-recognition-asc-606）。
5. **集計**: セグメント小計→全社売上→YoY成長率→ミックス（継続/一時、セグメント構成比）。
6. **ARR vs 認識売上**: 期末ARR（ランレート）と認識売上を区別する。期末基盤で売上を立てると高成長期は過大計上（Maxio: https://www.maxio.com/blog/fundamentals-of-saas-arr-and-revenue-forecasting）。ソースの算式が期末基盤なら従いつつ、期中平均ベースの参考行を必ず添える。ARRに一時フィーを含めない。
7. **感応度参考行**: 主要ドライバー±の参考行、または認識基準の感応度行。

### Usage-based特有の論点
- 利用量は実数で定義（分/社/月）。金額から逆算する場合は「従量料÷単価」の導出を備考で明示する。
- 新規顧客の利用率ランプ（初年度は定常の50–70%）を月次モデルでは考慮（Mostly Metrics: https://www.mostlymetrics.com/p/how-snowflake-forecasts-consumption-based-revenue）。
- 従量売上の成長は利用量成長と単価改定に分解して見せる。
- レベニューシェア/分配控除: 代理人ならネット計上、本人ならグロス計上＋分配は原価（RevenueHub ASC606: https://www.revenuehub.org/article/principalagent-considerations-gross-vs-net）。どちらをP/L売上とするか注記する。

### 品質チェックリスト
1. ロールフォワード閉合: 期首+新規−解約=期末が全セグメント・全年度で成立。翌期首=当期末
2. Tie-out: ソース記載値（Y5目標等）とモデル値の照合が±1%以内
3. ARPU検算: モデルARPUが定価と乖離しすぎない（値引考慮後±20%以内）
4. 成長率スメルテスト: T2D3（3x,3x,2x,2x,2x）を大幅に超えるなら根拠必須（Battery Ventures: https://www.battery.com/blog/a-mantra-for-saas-success-triple-triple-double-double-double/）
5. 解約と獲得の整合（解約率ゼロの根拠、ベンチマーク域内か）
6. 一時売上比率が年々低下するミックスか

### よくある失敗
- 期末×フル単価の過大計上（認識基準の未開示）
- 解約を純増に埋め込みgross addsを見せない → CACが壊れDDで指摘される
- 従量売上を「前年×成長率%」で伸ばす（体裁だけのボトムアップ）
- 新規顧客に初年度からフル従量（ランプ無視）
- ARRと売上の混同・未注記。導入フィーをARRに含める
- レベニューシェア控除をOpExに置いて粗利率を過大表示
