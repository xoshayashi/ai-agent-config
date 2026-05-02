# Audit F: Implementation Readiness

> 監査対象: `references/` 配下 14 ファイル (24,681 行)
> 評価軸: `scripts/build_model.py` / `ib_format.py` / `sanity_checks.py` / `cap_table_builder.py` / `valuation_builder.py` / `three_statement_builder.py` への直接利用可能性

## Summary
- Total implementation-relevant items audited: **128**
- Direct-use ready (copy-paste): **48** (38%)
- Needs minor adaptation: **53** (41%)
- Needs significant rewriting: **22** (17%)
- Missing entirely: **5** (4%)

総評: 各 reference は「IB 品質のモデルを書ける読者向けのリファレンス」として **記述粒度は十分** で、**業態判定 (03 §11)、Stage 判定 (08 §3.1)、IB constants (00 付録 B)、Sheet skeleton + Sanity rules (06 付録 A + §12) が機械可読に近い形で揃っている**。最大の未充足は **(a) ユーザー入力スキーマの正本不在、(b) Excel formula → openpyxl 変換規則、(c) SAFE round-trip 反復解の収束仕様、(d) Comp set 入力 schema**。当初想定より reference 充実度は高く、`ib_format.py` / `sanity_checks.py` / `three_statement_builder.py` (SaaS) は **build phase 即着手可**。`build_model.py` (orchestrator) のみ補強が必要。

---

## Per-script Readiness Score (0-10)

| Script | Score | Critical Gaps |
|--------|-------|---------------|
| `ib_format.py` | **9** | 00 付録 B が Python 定数として完全 export 済。Bank-specific brand 上書き機構のみ要設計 |
| `three_statement_builder.py` | **8** | 06 付録 A に sheet/named-range/cell formula が揃っている。ただし業態別 row 構成 (06 付録 B) は table 形式でしかなく、コードに落とすときの分岐が不明示 |
| `sanity_checks.py` | **8** | 06 §12.1/12.2 で H1-H15 / S1-S10 が列挙、threshold も明示。Excel 数式 → Python 1:1 変換可能。閾値の業態別変動 (S3 など) のみ要追加 |
| `cap_table_builder.py` | **6** | 04b §2.3 closed-form pool shuffle, §4.5 anti-dilution は実装可能。ただし `simulate_round` の戻り値型 `CapTablePostRound` が未定義、SAFE 連鎖 round-trip の擬似コードが narrative |
| `valuation_builder.py` | **6** | 05 §1.4 WACC, §1.6 TV, §4 VC method の数式は揃う。ただし comp set 入力データのスキーマ (会社名・FY end・ARR・margin) が未規定、DCF セル layout が未提供 |
| `build_model.py` (orchestrator) | **6** | 業態判定は **03 §11 にフローチャート + 早見表あり** (機械可読化が必要だが情報は揃う)。Stage 判定は **08 §3.1 にステージ別 ARR/評価額 table あり** (4 列マトリクス)。残課題はユーザー入力 schema の正本化 (F-C-004) と業態 → reference loading routing 表 (M-001) |

平均: **7.2 / 10** — `ib_format` / `sanity_checks` は build phase 即着手可、`three_statement_builder` (SaaS) も即着手可。`build_model.py` orchestrator は YAML 化作業が先行で必要だが情報は揃う。

---

## Critical Implementation Gaps

### F-C-001: 業態判定フローの YAML 化が未済 (Severity: **Medium → High**, 当初 Critical から下方修正)
- **Script affected**: `build_model.py`
- **Reference**: `03_business_models.md` §11 (l.1433-1502)
- **Status**: **decision flowchart は既存** (Q1→Q2→Q3→Q4 のテキスト表現 + hybrid 取扱、加えて「メトリクスセット早見表」が 10 業態分揃う)。
- **Gap**: 機械可読な構造化形式 (YAML / dict) ではなく **ASCII art + markdown table**。orchestrator から直接 import するには `_parse_03_flowchart()` のようなパーサが必要、または各業態 entry を別途 dict 化する手作業が必要。
- **Impact**: build_model.py に 30-50 行の routing dict をハードコピーする工数が発生。decision logic そのものは reference に正本があるため、動作は再現可能。
- **Recommendation**: 03 §11 末尾に以下を追加 (既存フローチャートの machine-readable 版):
  ```yaml
  business_model_routing:
    marketplace:
      Q1: intermediation
      Q2: [physical_goods, services, financial, digital]
    ecommerce_d2c:
      Q1: own_sales
      Q3: physical_consumer_brand
    fintech: { ... }
  hybrid_handling:
    - "hardware + sw_subscription": [hardware_primary, saas_metrics]
    - "marketplace + fintech": [marketplace, fintech]
  ```
- **困りごと例**: orchestrator がユーザー回答 (「自社製品の販売、サブスク課金あり」→ Q1=own_sales, Q3=digital_subscription) を Q1/Q2/Q3/Q4 の 4 段階質問に変換する logic を、reference の自然言語フローから自前実装する必要。

### F-C-002: Stage 判定 matrix は存在、ただし軸が ARR + 評価額のみ (Severity: **Low → Medium**, 当初 Critical から下方修正)
- **Script affected**: `build_model.py`, `valuation_builder.py`
- **Reference**: `08_investment_thesis.md` §3.1 (l.384-393), `05_valuation_wacc.md` §1.4.5 (Stage IRR レンジ)
- **Status**: 08 §3.1 に **Stage × 米国 ARR × 日本評価額 × 主な評価軸** の 4 列 6 行 table が既存。05 §1.4.5 にも Stage 別 IRR (Seed 50-70%, Series A 40-60% ...) あり。組み合わせれば Stage 判定 + WACC 選定が完結する。
- **Gap**: 軸が ARR と評価額のみで、**Headcount / Runway / Last raise size 等の補助シグナル** は無い。境界ケース (ARR $1M = Seed と A の境界, ARR $5M = A と B の境界) で曖昧性が残る。また、判定の **優先順** (ARR 優先か直近ラウンド優先か) が未明示。
- **Impact**: orchestrator が「ARR $4M、シリーズ A 半年経過」を Series A と判定するか Series B 直前と判定するかの裁量が残る。実務影響は WACC が ±5pp 程度で valuation に ±10-20% 振れる。
- **Recommendation**: 08 §3.1 に補助列を 1 行で追加:
  - 「直近ラウンドでの調達名がそのまま Stage 判定の主要キー、ARR は補助検証」とルール明記
  - もしくは 05 §1.4.5 に「ARR が table 範囲に入っていてもラウンド名と矛盾する場合はラウンド名優先」を追記
- **困りごと例**: 「Seed 後 ARR $1.5M」のスタートアップを、Seed の WACC (50-70%) で割引くか Series A の WACC (40-60%) で割引くか scriptが決定不能。

### F-C-003: SAFE round-trip 連鎖の擬似コードが narrative
- **Script affected**: `cap_table_builder.py`
- **Reference**: `04b_cap_table_mechanics.md` §5.4
- **Gap**: 複数 SAFE 同時転換は narrative + 数値例 (約 120 行) であるが、**反復解法の収束条件 / iteration cap** が未指定。Pre-money SAFE と Post-money SAFE 混在時の処理順序も曖昧。
- **Impact**: `simulate_round()` の SAFE 転換ステップで、実装者が「順次 vs 同時」「iteration vs closed-form」を独自判断する。
- **Recommendation**: 04b §5.4 末尾に `### Implementation Pseudocode` を追加し、以下を明示:
  - 転換順序: post-money SAFE 群 → pre-money SAFE 群 → 新ラウンド (YC 標準)
  - 共通 PPS は `min(cap_pps, discount_pps, round_pps)` を SAFE 単位に評価
  - 収束: `max(|new_PPS - old_PPS|) < $0.0001` で抜ける
- **困りごと例**: cap $5M / discount 20% / round PPS $0.85、SAFE 投資 $500k が 3 件混在 → 各 SAFE の転換株数を順番依存なしに決められないと、結果が non-deterministic に。

### F-C-004: ユーザー入力最小集合 (input schema) の正本不在
- **Script affected**: `build_model.py` (全 script に伝播)
- **Reference**: なし (どの reference にも明示無し)
- **Gap**: 「xlsx を生成するために最低限ユーザーから取るべき入力」が単一表として定義されていない。各 reference は「この変数があるとよい」と局所的に述べる。
- **Impact**: orchestrator が「ユーザーへの最初の質問リスト」を組み立てられない。MVP scope が定義困難。
- **Recommendation**: `references/` に `12_input_schema.md` を新規作成、または `01a_modeling_standards.md` 末尾に追加。
  ```yaml
  required:
    - company_name: str
    - reporting_currency: enum[JPY, USD]
    - business_model: enum (F-C-001 参照)
    - stage: enum (F-C-002 参照)
    - forecast_periods_months: int (default 60)
    - last_actuals_date: date
  optional:
    - cap_table_csv_path: str  # 無ければ founders_only template
    - last_round_pre_money: float
    - target_runway_months: int
  ```
- **困りごと例**: 「MVP として必須入力は何か」を skill オーケストレーターが推論で埋めると、ユーザーごとに UI 体験が変わる。

### F-C-005: Comp set 入力データのスキーマ未定義
- **Script affected**: `valuation_builder.py`
- **Reference**: `05_valuation_wacc.md` §2.2-2.7
- **Gap**: Trading comps の選定基準 / calendarization は narrative。**csv ヘッダ仕様 / 必須列リスト**が無い。Damodaran industry beta / synthetic rating の参照もデータ取得手段未指定 (web 取得 or local cache?)。
- **Impact**: comp 入力をスクリプトに渡せない、WACC β を bottom-up で算出するコードを書けない。
- **Recommendation**: 05 末尾に `### Comp Set Schema` 追加 (必須列: ticker, fy_end, currency, revenue_ltm, revenue_ntm, ebitda_ltm, market_cap, net_debt, beta_5y_monthly)、加えて Damodaran data の手動 update プロセスを文書化。
- **困りごと例**: ユーザーが Bloomberg export を csv で渡しても、列名揺れで script が拒否。

### F-C-006: Excel 関数 → openpyxl 翻訳ガイド不在
- **Script affected**: `three_statement_builder.py`, `valuation_builder.py`
- **Reference**: `06_three_statement.md` 付録 A, `01a_modeling_standards.md`
- **Gap**: 数式は `=IF(...)`, `=MAX(...)`, `=SUMIF(...)` の Excel 表記。**openpyxl で書くときの quote / escape ルール** や、A1 vs R1C1 vs Named Range の使い分け規範が未明示。
- **Impact**: 実装時に「Named Range を使うか、絶対参照 `$A$5` を使うか」が script ごとに分かれる。
- **Recommendation**: `01a_modeling_standards.md` に `### Excel Formula Authoring Rules for Generators` を追加:
  - Named Range 優先 (cross-sheet ref は必ず named)
  - 同一 sheet 内は構造化参照 (`Table[Column]`) 不採用、A1 直接
  - Quote escape: openpyxl `Cell.value = '=IF(A1>0,"OK","BREAK")'` (二重 quote 不要)
- **困りごと例**: H1 sanity check `=Total_Assets - Total_LE` を named range で書こうとすると、各期の Total_Assets を期間別 named range にするか単一 named range + offset にするか実装者裁量で割れる。

### F-C-007: Cross-sheet reference 命名規則の不徹底
- **Script affected**: `three_statement_builder.py`
- **Reference**: `06_three_statement.md` 付録 A.2
- **Gap**: Named range は 7 個 (S_Switch, Min_Cash, Tax_Rate, DSO, DIO, DPO, Periods, StartDate) のみ列挙。**期間付き named range** (例: Revenue_Y1, Revenue_Y2) の命名 convention が未提示。
- **Impact**: `Sched_Debt!Revolver_change_t` のような時系列参照を Excel で書く方法が複数あり、生成コードが定まらない。
- **Recommendation**: 付録 A.2 に「期間別 named range は使わず、各シート内で row label を A 列 / 期間を行方向に展開し、ROW MATCH で参照する」を明記。または `OFFSET(Anchor, 0, period_idx)` パターンを正典化。
- **困りごと例**: BS の Cash 行が Cash_t と Cash_{t-1} を参照する数式を生成するとき、各期セル毎に named range を作るのか単一 anchor で済ますか実装者で割れる。

### F-C-008: 業態別 sheet template 差分が table のみ
- **Script affected**: `three_statement_builder.py`
- **Reference**: `06_three_statement.md` 付録 B
- **Gap**: SaaS / Hardware / Marketplace 別の差分は **9 行 × 3 列の table** で表現されるが、「Hardware の場合に IS の どの行を Inventory Cost に置き換えるか」「Marketplace の場合に Revenue 行は GMV を上に追加するか」の **構造的差分が記述粒度不足**。
- **Impact**: scripts は SaaS テンプレを base に書き、業態別の delta を hard-code するしかない (DRY 違反)。
- **Recommendation**: 付録 B を拡張、または各業態章 (`03_business_models.md`) に `### IS Row Layout`, `### BS Row Layout`, `### Drivers` の三表を追加。
- **困りごと例**: Marketplace モデルで Revenue 行を `GMV × take_rate` で書くか、`Net Revenue (after take rate)` だけにするか — IB 慣行は両方ある。

### F-C-009: Sanity check の業態別 threshold 変動
- **Script affected**: `sanity_checks.py`
- **Reference**: `06_three_statement.md` §12.2
- **Gap**: S3 (DSO < 90 for SaaS) のような閾値が、Hardware / Marketplace / Fintech では異なる。各業態ごとの上限 / 下限が単一表として揃っていない。
- **Impact**: sanity_checks.py が業態を引数に取れず、固定 threshold で誤検知。
- **Recommendation**: `06 §12.2` を拡張し、各 S 項目に業態別カラムを追加:
  ```
  | # | Check | SaaS | Hardware | Marketplace | Fintech |
  | S3 | DSO | <90 | <60 | <30 | n/a |
  ```
- **困りごと例**: Fintech (lending) は受取利息で AR 概念が独特、DSO check が意味をなさず偽陽性連発。

### F-C-010: Iterative calc (循環参照) の Python 側収束ロジック未定義
- **Script affected**: `three_statement_builder.py`, `valuation_builder.py`
- **Reference**: `06_three_statement.md` §12.4
- **Gap**: Excel 側 iterative calc は max=100, change=0.001 と明記。しかし **xlsx を生成するときに iterative calc を有効化する openpyxl 側の API** や、**生成後に Excel で開いた時にユーザー設定が iterative OFF のままだと計算破綻** するリスクへの対処が未記述。
- **Impact**: Revolver / Tax NOL / WACC iterative の 3 箇所すべてで生成 xlsx が #REF や `0` を表示。
- **Recommendation**: `06 §12.4` に openpyxl 側の `wb.calculation.iterate=True; wb.calculation.iterateCount=100; wb.calculation.iterateDelta=0.001` を明記。
- **困りごと例**: 生成 xlsx を共有して相手 Excel で開くと、初期値で計算が止まる。

### F-C-011: ESLint 的「禁則」を機械可読化できる箇所が narrative
- **Script affected**: `sanity_checks.py` (拡張)
- **Reference**: `01b_integrity_and_anti_patterns.md`
- **Gap**: 86 個の generic code block が anti-pattern の実例を示すが、「このパターンが出たら BREAK」という machine-checkable rule に翻訳されていない。
- **Impact**: 生成後の自動レビュー (e.g., 「Hard-coded value detected in formula cell」) を script で書けない。
- **Recommendation**: 01b 末尾に `### Machine-Readable Rule Set` を追加し、各 anti-pattern を `(rule_id, sheet_pattern, cell_pattern, severity)` の dict 配列として export。
- **困りごと例**: 「数式に直接 0.30 (税率) が入っている」を検出するには cell.value を正規表現で走査必要。reference にその指針が無い。

### F-C-012: 11_debt_financing と 06 §4 の Term Loan / Revolver 数式重複 (Severity: **Resolved**, 当初 High から取り下げ)
- **Script affected**: `three_statement_builder.py`
- **Reference**: `11_debt_financing.md` l.16, `06_three_statement.md` §4
- **Status**: **既に解決済**。11 冒頭 (l.16) で「Revolver の plug 機能、利払の循環参照解消は `06_three_statement.md` §4 の前提を継承する。重複は避け、本書では debt 商品横断の追加論点に集中する。」と明示。**06 §4 が一次正本、11 が拡張**。
- **Residual Gap**: orchestrator が「どの債務種類は 06 で済み、どの債務種類は 11 を読み込むか」の対応表は無いが、これは scripts 側で `if has_term_loan_b: read_11(); else: read_06()` のような分岐で吸収可能。
- **Recommendation**: SKILL.md の loading order に「06 → 11 の順で読み込む。11 は 06 の前提を共有」を 1 行追加するだけで足りる (M-001 と統合)。
- **困りごと例**: 当初想定の重複問題は無かった。

---

## Constants Extractability

| Concept | File | Extractable as | Status | Notes |
|---------|------|----------------|--------|-------|
| IB Functional Color Palette | 00 付録 B | `dict[str, str]` (5 色) | Direct | コピペ可、`IB_HARD_INPUT="0000FF"` 等 |
| IB Brand Color Palette | 00 §3.2 + 付録 B | `dict[bank_id, dict[str, str]]` | Minor adapt | 付録 B は 5 銀行のみ、§3.2 に 10+ 銀行があるので統合必要 |
| Sheet Order (3-statement) | 06 付録 A.1 | `list[str]` 17 シート | Direct | 名前は固定、コピペ可 |
| Sheet Order (Cover→Outputs) | 06 付録 A.1 | `list[str]` | Direct | 同上 |
| Number Format Strings | 00 付録 B | `dict[str, str]` (6 種) | Direct | openpyxl `number_format` に直接代入可 |
| Font Tuples | 00 付録 B | `dict[str, tuple]` (6 種) | Direct | `Font(name=, size=, bold=)` に分解しやすい |
| Investment Thesis Thresholds | 08 全章 | `nested dict` | Needs rewrite | 数値が散在、単一 export point 無し |
| Industry WACC ranges | 05 §1.4.5 | `dict[stage, tuple]` (6 行) | Minor adapt | Stage 別のみ、業態別は無し (F-C-002 参照) |
| Sanity Check H1-H15 | 06 §12.1 | `list[CheckRule]` | Minor adapt | Excel 数式列を Python lambda に変換要 |
| Sanity Check S1-S10 | 06 §12.2 | `list[CheckRule]` | Minor adapt | 閾値が業態依存 (F-C-009) |
| Damodaran Implied ERP | 05 §1.4.1 | `float` (4.23%) + 出所 URL | Direct | snapshot 値、定期更新ノートあり |
| CRP (Japan, US, etc) | 05 §1.4.1 | `dict[country, float]` | Direct | 単一値、URL 出所付 |
| Stage IRR Ranges | 05 §1.4.5 | `dict[stage, tuple]` | Direct | 6 行表 |
| SaaS/Hardware/Marketplace 差分 | 06 付録 B | `dict[business_model, dict]` | Minor adapt | 9 項目 × 3 業態の table |
| Layout Constants (column width, row height) | 00 付録 B | `dict[str, float]` | Direct | コピペ可 |
| Print / Page Setup | 00 付録 B | `dict[str, str/float]` | Direct | コピペ可 |
| Vesting Schedule defaults | 04b §3.5 | `tuple(cliff_months, total_months)` | Direct | 12 / 48 を default に |
| ESOP Pool Size targets | 04b §3.6 | `dict[stage, float]` | Direct | Seed 10%, A 12-15% etc. |
| Logistic curve helper | 09 §6.7 (l.1245-1267) | `def logistic(K, r, t0)` + `@dataclass Segment` | Direct | Python コード block で完成形あり、コピペ可 |
| Monte Carlo template | 09 §6.5.3 (l.1217-1225) | numpy snippet | Direct | triangular / normal の使い分けあり |
| Anti-dilution variants | 04b §4.5 | `enum(FullRatchet, BroadWA, NarrowWA, PayToPlay)` | Direct | 数式付 |

合計 **20 概念**: Direct=12, Minor adapt=6, Needs rewrite=2

---

## Formula → Code Mapping

| Formula | File | Implementable | Notes |
|---------|------|---------------|-------|
| WACC (CAPM 完全形) | 05 §1.4.1 | Direct | 6 項目加算、各項定義あり |
| β unlever / relever | 05 §1.4.2 | Direct | Hamada formula |
| Cost of Debt (synthetic rating) | 05 §1.4.3 | Minor | Damodaran ratings.xls を local cache で持つ必要 |
| FCFF | 05 §1.2 | Direct | EBIT(1-t) + D&A - CapEx - ΔNWC |
| FCFE | 05 §1.3 | Direct | NI + D&A - CapEx - ΔNWC + ΔNet Debt |
| Gordon TV | 05 §1.6 | Direct | FCFF_(n+1) / (WACC - g) |
| Exit Multiple TV | 05 §1.6 | Direct | EBITDA_n × Multiple |
| Mid-year convention | 05 §1.7 | Direct | (1+WACC)^(t-0.5) |
| VC Method backsolve | 05 §4.3 | Direct | 直近ラウンド逆算 |
| First Chicago 加重 | 05 §4.4 | Direct | p_success × Value 3 シナリオ |
| Pool Shuffle (closed-form) | 04b §2.3 | Direct | X = (F0-P0) × QMV / (PMV - T×QMV) |
| Anti-dilution Full Ratchet | 04b §4.5.1 | Direct | conversion_price = new_round_pps |
| Anti-dilution Broad-based WA | 04b §4.5.2 | Direct | (A+B)/(A+C) × old_price |
| Anti-dilution Narrow-based WA | 04b §4.5.3 | Direct | A の定義変更のみ |
| SAFE Pre-money 転換 | 04b §5.2 | Direct | min(cap_pps, discount_pps) |
| SAFE Post-money 転換 | 04b §5.3 | Direct | YC 2018 standard |
| SAFE Round-trip (multi) | 04b §5.4 | Needs spec | F-C-003 参照 |
| MFN 連鎖 | 04b §5.5 | Minor | iteration 必要、数式は明記 |
| Liquidation Waterfall | 04b §6.1-6.3 | Direct | Multi-class 計算ステップあり |
| TSM Diluted Shares | 04b §1.3, 06 §6.4 | Direct | `Options - (Options × Strike / VWAP)` |
| Logistic Curve | 09 (要確認) | Direct | sigmoid + parameters |
| Bass Diffusion | 09 (要確認) | Direct | p,q,m parameters |
| Working Capital Days | 06 §3 | Direct | DSO, DIO, DPO |
| Cash Conversion Cycle | 06 §3.2 | Direct | DSO + DIO - DPO |
| NOL Carryforward (US) | 06 §5.4 | Direct | 80% NOL limitation post-2017 |
| NOL Carryforward (JP) | 06 §5.5 | Direct | 9 年 (青色申告) + 50%/65% 上限 |
| DTA / DTL recognition | 06 §5.3 | Direct | 一時差異 × tax rate |
| SBC TSM dilution | 06 §6.4 | Direct | 既述 |
| Lease (ASC 842 / IFRS 16) | 06 §7 | Minor | 初期計上 + amortization、数値例で補足要 |
| Term Loan amortization | 11 / 06 §4.2 | Direct | mortgage / equal-principal 両方 |
| Revolver plug logic | 11 / 06 §4.3 | Direct | iterative |
| Interest expense (avg balance) | 06 §4.4 | Direct | 数式明記 |
| Berkus / Scorecard / RFS | 05 §5,6,7 | Direct | 加点表ベース、シンプル |
| Real Options (Black-Scholes) | 05 §8.2 | Direct | scipy.stats.norm.cdf 標準 |

合計 **34 数式**: Direct=29, Minor=4, Needs spec=1

---

## Sanity Check Rule Set Implementability

| ID | Rule | Excel | Python 1:1 | Threshold 業態依存 |
|----|------|-------|------------|---------------------|
| H1 | BS = L + E | `Total_Assets - Total_LE` | 直 | No |
| H2 | Cash tie | `CFS_End - BS_Cash` | 直 | No |
| H3 | RE roll | `(RE_t-RE_{t-1}) - (NI_t-Div_t)` | 直 | No |
| H4 | PP&E roll | 数式 | 直 | No |
| H5 | AD roll | 数式 | 直 | No |
| H6 | Debt roll | 数式 | 直 | No |
| H7 | APIC roll | 数式 | 直 | No |
| H8 | Lease ROU roll | 数式 | 直 | No |
| H9 | Lease Liab roll | 数式 | 直 | No |
| H10 | Deferred Rev roll | 数式 | 直 | Yes (SaaS only) |
| H11 | NOL roll | NOL≥0 | 直 | Yes (国別) |
| H12 | DTA roll | 数式 | 直 | No |
| H13 | CFS internal sum | CFO+CFI+CFF+FX = ΔCash | 直 | No |
| H14 | Cash floor | Cash_t ≥ Min_Cash | 直 | No (Min_Cash はユーザー入力) |
| H15 | Revolver ≥ 0 | 直 | 直 | No |
| S1 | GM ∈ [0,100%] | range | 直 | No |
| S2 | EBIT ΔY/Y < 20pp | abs delta | 直 | Yes (業態) |
| S3 | DSO < 90 | range | 直 | **Yes (F-C-009)** |
| S4 | DPO ∈ [0, 180] | range | 直 | Yes |
| S5 | CapEx ≥ 0 | sign | 直 | No |
| S6 | Tax ≥ 0 if PBT > 0 | sign | 直 | No (例外: refund) |
| S7 | NI margin ≤ GM | sanity | 直 | No |
| S8 | Diluted ≥ Basic | TSM | 直 | No |
| S9 | Rev growth < 200% Y/Y | bubble | 直 | Yes (Stage) |
| S10 | NWC days Δ < 50% | unstable | 直 | Yes |

H1-H15 は **完全実装可**, S1-S10 は **業態 / Stage 依存** で sanity_checks.py に context arg 必要。

---

## Per-Reference Implementation Coverage

| File | Lines | Implementation-readable score | Best parts | Worst parts |
|------|-------|-------------------------------|-----------|-------------|
| 00_design_guidelines.md | 2254 | **9/10** | 付録 B (Implementation Constants) | 銀行別 brand 詳述が export 形式に未統合 |
| 01a_modeling_standards.md | 1243 | 6/10 | Excel formula 7 個明示、modeling 7 原則 | Generator 向け formula authoring rule (F-C-006) が無い |
| 01b_integrity_and_anti_patterns.md | 1288 | 4/10 | 86 個の anti-pattern 実例 | Machine-readable rule set 未提供 (F-C-011) |
| 02_saas_metrics.md | 1691 | 7/10 | NRR/GRR/Magic#/Rule of 40 全式 | コード block ほぼ無、Python 換算は読者任せ |
| 03_business_models.md | 1578 | 5/10 | 6 業態 × 各 KPI / driver 詳細 | **業態判定 routing 未定義 (F-C-001)**、SaaS テンプレからの delta 不明 (F-C-008) |
| 04a_convertible_and_terms.md | 1679 | 7/10 | SAFE / J-KISS の term sheet 詳細 | 数式は narrative、計算 pseudocode 不足 |
| 04b_cap_table_mechanics.md | 1763 | 8/10 | 付録: closed-form pool shuffle, anti-dilution 数式群 | `simulate_round` 戻り値型未定義、SAFE chain spec (F-C-003) |
| 05_valuation_wacc.md | 1767 | 7/10 | WACC 完全展開、Stage IRR 表、ミニケース 5 個 | comp set csv schema (F-C-005) 不在 |
| 06_three_statement.md | 1330 | 9/10 | 付録 A (sheet/named range/cell formulas), §12 sanity | 業態別 row 構成 (F-C-008)、iterative calc API (F-C-010) |
| 07_japan_specifics.md | 1924 | 6/10 | 税制適格 SO 表、JGAAP 差異、消費税処理 | 国際展開時の locale switching ロジック未定義 |
| 08_investment_thesis.md | 2001 | 6/10 | 投資判定 thesis 700 行のテーブル | thresholds が散在、Stage 判定 (F-C-002) 不在 |
| 09_market_sizing.md | 2399 | 7/10 | TAM/SAM/SOM、Logistic, Bass 数式・Python | Python block の関数名・引数・戻り値が文書化不足 |
| 10_modeling_craft.md | 1510 | 5/10 | Modeling 哲学 + craft tip 多数 | scripts への直接 input 性は低い、メタ的 |
| 11_debt_financing.md | 2254 | 7/10 | Debt 完全 (Term/Revolver/Lease/Convertible) | 06 §4 と重複、正本不明 (F-C-012) |

平均: **6.6 / 10**

---

## Missing Integration Points

### M-001: SKILL.md オーケストレーターの reference 読み込み順
- 各 reference 同士の依存関係 (00 → 01a/01b → 業態 → 06 → 05 → 04 → 11) が明示されていない。
- 推奨: SKILL.md に loading order と「stage-by-script reference matrix」を追加。

### M-002: 数値例 (mini case) の test fixture 化
- 04b §10 ケース A/B/C, 05 §1.11 ミニケース 1, 06 §14 などに **完全な数値例** あり。
- これらは `scripts/tests/fixtures/*.json` 化の素材として最適だが、**現時点では markdown 表形式のため自動抽出不可**。
- 推奨: 各ミニケースに `<!-- fixture:case_a_seed_to_b -->` 等のマーカーを入れて parser で抽出。

### M-003: Bank-mode 切り替え (Banker / VC / PE / Strategy)
- 00 §11 で 4 mode を定義、各 mode で sheet 構成・色・フォントが異なる。
- ただし script 入力としての `mode` パラメータ仕様が無い。
- 推奨: `ib_format.py` に `apply_mode(mode: Literal["banker","vc","pe","strategy"])` を入れる前提で 00 付録 B に mode-specific override 表を追加。

### M-004: 日本固有処理の locale switch
- 07 全章で日本特有の税制 / 会社法 / 開示が解説。米国・グローバル案件との切り替え API が未定義。
- 推奨: 各 script に `locale: Literal["JP","US","GLOBAL"]` 引数、reference に locale-specific routing 表追加。

### M-005: chart 生成と xlsx の連携
- 00 §6 で 7 種のチャート規約。openpyxl Chart object のマッピングが reference 内に無い。
- 推奨: 00 §6 末尾に `### Chart Generation Recipe` を追加 (`from openpyxl.chart import LineChart, BarChart3D, ...`)。

### M-006: pptx 連携 (00 §12 と pptx skill 連携)
- 00 §12 で「Excel → PowerPoint linked table」を解説。`document-skills:pptx` skill との連携 contract が未定義。
- 推奨: `references/12_pptx_integration.md` 新設 or 00 §12 を拡張。

---

## Build Phase Effort Estimate

| Script | LOC estimate | Difficulty | Reference Coverage | Notes |
|--------|--------------|------------|--------------------|-------|
| `ib_format.py` | 250-400 | Easy | **95%** | 00 付録 B コピペ + Font / Border 関数化、Mode 切替で +50 LOC |
| `three_statement_builder.py` | 1,200-1,800 | Hard | 75% | 06 付録 A 再現 + 業態別 delta + iterative calc 設定。最長 |
| `sanity_checks.py` | 400-600 | Medium | 90% | H1-H15/S1-S10 の openpyxl 数式 string 化 + cond formatting |
| `cap_table_builder.py` | 700-1,000 | Hard | 70% | 04b §2.3, §4.5, §5.x の閉じた式 + SAFE round-trip iteration |
| `valuation_builder.py` | 800-1,200 | Medium-Hard | 65% | DCF + Comps + VC Method + Football Field chart。comp 入力 schema 必要 |
| `build_model.py` (orchestrator) | 500-800 | Medium | **45%** | 業態判定 + Stage 判定 + ユーザー入力収集 + 各 builder 呼び出し |
| 合計 | 3,850-5,800 LOC | - | 70% avg | 約 2-3 週間 (1 名フルタイム想定) |

### 着手推奨順序
1. `ib_format.py` (依存なし、確実、テスト容易)
2. `sanity_checks.py` (06 §12 直接、test fixture 容易)
3. `three_statement_builder.py` (06 付録 A 直接、ただし業態別差分は SaaS のみ先行)
4. `cap_table_builder.py` (04b 中心、SAFE round-trip は最後)
5. `valuation_builder.py` (05 中心、Damodaran data 取得が外部依存)
6. `build_model.py` (上記 5 つが揃ってから orchestrator)

**ボトルネック**: `build_model.py` の business_model / stage 判定が reference 補強 (F-C-001, F-C-002, F-C-004) 待ち。これを先に潰さないと build phase 後半で混乱。

---

## Recommended Reference Additions (順序付き優先度)

| Priority | Add to | Section | Rationale |
|----------|--------|---------|-----------|
| P0 | `01a` or new `12_input_schema.md` | Required/Optional input schema (YAML) | F-C-004 (唯一の真の Critical) |
| P1 | `03_business_models.md` | §11 末尾に YAML 形式の routing dict | F-C-001 (情報あり、形式変換のみ) |
| P1 | `04b` | §5.4 末尾に SAFE round-trip pseudocode | F-C-003 |
| P1 | `05` | §2 末尾に Comp Set Schema | F-C-005 |
| P1 | `01a` | `### Excel Formula Authoring for openpyxl` | F-C-006, F-C-007 |
| P1 | `06` | 付録 B 拡張 (業態別 row 構成) | F-C-008 |
| P2 | `08 §3.1` | Stage 判定の優先順 1 行追記 | F-C-002 |
| P2 | `06 §12.2` | Sanity threshold 業態別カラム | F-C-009 |
| P2 | `06 §12.4` | openpyxl iterative calc API | F-C-010 |
| P2 | `01b` | Machine-readable rule set | F-C-011 |
| ~~P2~~ | ~~`11`~~ | ~~06 §4 との正本宣言~~ | F-C-012 (既に解決済) |
| P3 | SKILL.md | reference loading matrix | M-001 |
| P3 | 各 reference | mini case に fixture マーカー | M-002 |

P0=1, P1=5, P2=4, P3=2 → **追加で約 800-1,500 行** の reference 補強が必要 (現状 24,681 行に対し +3-6%)。**当初想定の半分以下**。

---

## Final Verdict

`scripts/` の build phase は **`ib_format.py` / `sanity_checks.py` / `three_statement_builder.py` (SaaS) の 3 本から即着手可能**。corpus 全体の implementation readiness は当初想定より高く、**業態判定 (03 §11)、Stage 判定 (08 §3.1)、IB 定数 (00 付録 B)、Sheet skeleton (06 付録 A)、Sanity rules (06 §12)** が reference 内に既に揃っている。

**Build phase の効率化提案 (改訂版)**:
1. **P0 は F-C-004 (input schema 正本) のみ真の Critical**。build_model.py 着手前に 50-100 行の YAML schema を 01a 末尾 or 新規 `12_input_schema.md` に追加する。
2. `ib_format.py` を最初に完成 (250-400 LOC, 1-2 日)。CI で「生成 xlsx を openpyxl で再 load → 全シート / 全 named range / 全 cond format が読める」を担保。
3. `sanity_checks.py` の test fixture を 06 §14 mini case から手作業でも先に作る (1 日)。他 script の回帰テストでも再利用可能。
4. `three_statement_builder.py` は **SaaS 専用版を先に完成** (1,200-1,500 LOC, 5-7 日) → 動作確認後に `business_model.py` factory pattern で他業態を hard-code 拡張 (各業態 +200-400 LOC)。
5. `cap_table_builder.py` は §2.3 closed-form pool shuffle と §4.5 anti-dilution は即実装可、SAFE round-trip (F-C-003) のみ実装者が反復解の詳細を decide してコード化。
6. `valuation_builder.py` は WACC + DCF を SaaS 1 件分だけ先行実装、Comp Set 拡張は次期スプリント (F-C-005 解消後)。
7. `build_model.py` orchestrator は最後に組む。03 §11 のフローチャートを 30-50 行の dict に手動翻訳 (F-C-001) し、08 §3.1 をそのまま `STAGE_TABLE` 定数として import。

総じて **80% は reference に準拠した実装可、20% は実装段階の判断 or reference 側の軽微な補強** で対応可能。当初評価より corpus 充実度が高い。

---

## Audit Revision Notes (執筆過程での補正)

監査初版では F-C-001 / F-C-002 / F-C-012 を Critical として書き出したが、reference 中盤以降 (03 §11, 08 §3.1, 11 l.16) を確認した結果:
- **F-C-001 (業態判定)**: 03 §11 にフローチャート + 早見表が完備。**形式変換のみ必要、Severity 下方修正**。
- **F-C-002 (Stage 判定)**: 08 §3.1 に Stage × ARR × 評価額 table 完備。**境界ケースの優先順のみ補強要、Severity 下方修正**。
- **F-C-012 (Debt 重複)**: 11 l.16 で「06 §4 を継承」と明示済。**実質解決済**。

この補正により真の Critical は **F-C-004 (input schema)** に絞られた。 build phase 着手 1 日前に schema YAML を書けば残りは reference 直接 import で進む。
