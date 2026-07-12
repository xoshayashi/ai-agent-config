# シート構築プレイブック②：人員計画・費用計画

対象: B2B SaaS/プラットフォーム（固定＋従量課金＋導入フィー、AI推論COGS重め）の
年次IB型7シートモデル。出典はWeb調査（2026-07）。

## 人員計画（Headcount）

### 役割と設計原則
- 人件費はスタートアップ支出の最大項目。Kruze分析ではフル装備人件費が総支出の約68%（[Kruze](https://kruzeconsulting.com/blog/startup-payroll-costs/)）。VCが最初にストレステストするシート。人員計画→費用計画→PLの一方向参照にし、費用側で人件費を二重入力しない。
- 粒度はステージで切替: 〜50名はポジション単位、それ以降は職能×レベルのドライバー型（[Mosaic](https://www.mosaic.tech/post/mosaics-guide-to-headcount-planning)）。
- Gross hires（採用数）とNet adds（純増）を区別。50名超のモデルでは離職率行（年10〜15%）＋バックフィル行を持つ（[Metapraxis](https://metapraxis.com/blog/workforce-headcount-planning-guide)）。年次簡易モデルで純増のみとする場合は備考に明記。

### 必須ブロック
1. **FTE by function**: 最低4分類（Sales・Marketing / CS・導入Delivery / Engineering・Product / Corp）。各職能のPL配賦先（COGS/S&M/R&D/G&A）を備考で明記。
2. **採用数・純増**: 採用リードタイム（オファー→入社2〜3ヶ月）を月次モデルでは反映。
3. **Loaded cost**: 基本給×(1+バーデン率)。日本の法定福利費は給与の約15%（令和5年度平均15.2%、[Edenred](https://edenred.jp/article/employee-benefits/244/)）で、諸手当込みでベース×1.18〜1.25が実務レンジ（推定・仮定として明示）。昇給率行（年2〜3%）は複数年モデルで検討。
4. **PL配賦**: サポート・定着型CS→COGS、Sales+Marketing+拡販型CS→S&M、Eng/Product→R&D、Corp→G&A（[SaaS Capital](https://www.saas-capital.com/blog-posts/what-should-be-included-in-cogs-for-my-saas-business/)）。
5. **生産性メトリクス**: Revenue per FTE — ARR $1M未満で中央値$42K、$1-5Mで$90K、私企業SaaS全体中央値$130K（[SaaS Capital](https://www.saas-capital.com/blog-posts/revenue-per-employee-benchmarks-for-private-saas-companies/)）。AE1人あたり年間新規ARR: Seed $250-400K → Series B+ $600K-1M（[Prospeo](https://prospeo.io/s/sales-rep-quota)）。日本のエンタープライズはこの0.5〜0.7掛けが現実的（推定）。開発は1スクワッド6〜8名単位。

### 品質チェックリスト
- Revenue/FTEがステージバンド内か（$5M ARR超で<$80Kは人員過剰、>$250KはAI-native以外で未達リスク）
- 採用ペース実現性: リクルーター1人あたり月3〜4名（[Pinpoint](https://trends.pinpointhq.com/hires-per-recruiter)）。急拡大年はTA人員・採用費が整合しているか
- Span of control: マネージャー1人あたり直属5〜8名
- 営業キャパ整合: 必要AE数＝新規ARR目標÷（クォータ×達成率60〜80%）、ランプ控除（[Lative](https://lative.ai/blog/sales-capacity-planning-for-saas/)）

### よくある失敗
- 人員が売上に永久比例（Revenue/FTE改善なし＝スケールメリット不在）
- バーデン抜きの基本給のみ計上（日本で約18〜25%の過小評価）
- 採用費・リードタイム無視（日本の中途採用単価は約100〜130万円/人、[レバテック](https://levtech.jp/partner/guide/article/detail/319/)）
- 離職ゼロ・期初一括入社前提の歪み（採らない場合は仮定を備考に明示）

## 費用計画（COGS & Opex）

### 役割と設計原則
- 物理ドライバーがある費目は必ずドライバー型（数量×単価）。%売上比は「ドライバー不明の残余費目」に限定（[Mosaic](https://www.mosaic.tech/financial-model)）。
- COGS/Opexの線引き:「現在の顧客へのプロダクト提供に直接必要か」。Yes→COGS（[SaaS Capital](https://www.saas-capital.com/blog-posts/what-should-be-included-in-cogs-for-my-saas-business/)）。

### COGS必須ブロック
1. **推論・従量原価**: 利用量×単価。単価はアーキテクチャフェーズ別の階段型で持ち、各段の根拠（モデル小型化・キャッシュ・エッジ化）を明記。LLM推論単価は同性能比で年約10倍下落の観測（[a16z LLMflation](https://a16z.com/llmflation-llm-inference-cost/), [Epoch AI](https://epoch.ai/data-insights/llm-inference-price-trends)）だが、計画では保守的に年3〜5倍下落＋消費量リッチ化の相殺を置く。コストダウンは時間経過でなく「実装フェーズ達成」に紐づける。
2. **ホスティング/プラットフォーム**: 顧客数or利用量ドライバー。成熟SaaSで売上の8〜12%が上限目安（[humanr](https://www.humanr.ai/intelligence/saas-cost-of-revenue-breakdown-hosting-support-professional-services-benchmarks)）。
3. **Support/CS人件費**: 人員計画から参照（定着・サポート型のみ）。売上の8〜10%目安。
4. **導入原価 vs 導入フィー**: 対で置きサービス粗利率を明示。プロフェッショナルサービス粗利はBE〜+30%が標準、初期はマイナスも普通（[CFO Pro Analytics](https://cfoproanalytics.com/cfo-wiki/saas/gross-margin-targets-for-saas-companies/)）。サブスク粗利と分離表示。
5. **COGSに入れないもの**: 営業コミッション、R&D、マーケ、全社間接費（[SoftwareEquity](https://softwareequity.com/blog/cogs-in-saas/)）。
- **粗利ベンチマーク**: サブスクGM中央値〜79%、Total GM中央値71%（KeyBanc 2024）。AI-nativeは当初40〜60%（[SoftwareSeni](https://www.softwareseni.com/why-ai-gross-margins-are-so-much-lower-than-saas-and-what-that-means-for-your-business/)）。「初期50〜60%→フェーズ達成で70%台〜」の軌道と各段の根拠を置く。

### Opex必須ブロック
1. **S&M**: 広告宣伝（%売上 or CAC×新規数。実データがあればCAC連動優先）＋営業マーケ人件費＋コミッション（新規ARR×〜10%）。ステージ目安: 早期40〜50%超→成長期中央値37%（[SaaS Capital](https://www.saas-capital.com/blog-posts/spending-benchmarks-for-private-b2b-saas-companies/), [Parsa Saljoughian](https://medium.com/parsa-vc/operating-expense-benchmarks-for-saas-startups-e49697abf3ed)）。
2. **R&D**: 人件費＋GPU・データ・外部委託のプログラム費を別行で明示（AI企業は通常SaaSより重い）。私企業SaaS中央値は売上の27%。早期は50〜100%超でも正常、縮小軌道を示す。
3. **G&A**: オフィス＝FTE×単価、士業・監査、採用費＝採用数×単価、ツール＝FTE×単価。売上比15〜25%→規模拡大で10%前後へ低下。

### 品質チェックリスト
- 粗利軌道が主張フェーズと整合（フェーズ移行年に段差、それ以外なだらか）
- S&M・R&D・G&Aの%売上をステージ別ベンチマークと突合
- Rule of 40スメルテスト: 終盤年に「成長率60%＋EBITDA 40%」の両取りは過大バラ色のサイン
- 支出合計の妥当性: エクイティ調達企業の総支出中央値はARRの約101%。終盤にOpexが売上の40%未満へ急落するモデルは要説明
- 人件費の二重計上ゼロ（費用計画の人件費行がすべて人員計画参照）

### よくある失敗
- 全費目%売上比の「ゴムひもモデル」（感応度分析が無意味化）
- 推論コストダウンの無根拠な直線外挿／利用量リッチ化を無視した片側バイアス
- 導入フィーの100%粗利計上（Delivery人件費を他区分に隠す）
- コミッションのCOGS混入・CS配賦の歪み
- G&Aが売上比一定のまま（規模の経済不在）、採用費等「成長に必ず付随する費用」の欠落
