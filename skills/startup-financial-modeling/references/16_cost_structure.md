---
name: cost_structure
description: コスト側 (固定 / 変動 / SBC / 業態別 COGS-OpEx 標準形 / Headcount-driven 構築) の正本。SKILL.md dispatch table の "コスト構造 (固定/変動/SBC)" entry の第 1 reference として読まれる。02 / 03 (収益側) と対の構造。
type: reference
priority: P1
related: [_terminology, 02_saas_metrics, 03_business_models, 06_three_statement, 16_cost_structure]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: コスト分類 / Headcount driver / 業態別 COGS-OpEx 標準形は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) (構築) からコスト driver 入力時に第 1 reference として参照
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (固定 / 変動分類 / SBC 計上) を必ず実行
- **関連 reference**: `02 §5` (SaaS コスト) / `03_business_models` (業態別 COGS) / `06_three_statement` (OpEx schedule)

# 16. コスト構造 (Cost Structure) 徹底リファレンス

> 本ドキュメントはスタートアップ向け包括的財務モデリング Skill の reference であり、収益側 (02_saas_metrics, 03_business_models) と対をなす **コスト側の正本** である。固定/変動 (fixed/variable) の根本定義、業態別の COGS / OpEx 標準形、Headcount 駆動 (headcount-driven) の bottom-up 構築手順、ベンチマーク (中央値 / 良 / 優秀)、そして cost DD チェックリスト 50 項目までを扱う。
>
> 用語注: 本書では「Operating System / OS」を避け、「Operating model」「経営の仕組み」と表現する (個人ルール)。時系列の数値データは原則として表形式 (markdown table) に揃えている。
>
> 数値ベンチマークはすべて出典明示。複数ソースが矛盾する場合は両方併記し、レンジで提示する (平均化はしない)。

---

## 目次

1. [前提とコスト分類の根本](#1-前提とコスト分類の根本)
2. [P/L コスト構造の標準形](#2-pl-コスト構造の標準形)
3. [業態別 COGS 構造の解剖](#3-業態別-cogs-構造の解剖)
4. [OpEx 三大区分 (S&M / R&D / G&A)](#4-opex-三大区分-sm--rd--ga)
5. [業態別ベンチマーク表 (中央値 / 良 / 優秀)](#5-業態別ベンチマーク表-中央値--良--優秀)
6. [Headcount 駆動 cost modeling](#6-headcount-駆動-cost-modeling)
7. [Variable cost と Unit Economics](#7-variable-cost-と-unit-economics)
8. [Operating Leverage と Break-even](#8-operating-leverage-と-break-even)
9. [Cost Curve / Scale 効果](#9-cost-curve--scale-効果)
10. [SBC (Stock-Based Compensation) の取扱い](#10-sbc-stock-based-compensation-の取扱い)
11. [R&D Capitalization (ASC 350-40 / IAS 38 / J-GAAP)](#11-rd-capitalization-asc-350-40--ias-38--j-gaap)
12. [Stage 別 Cost Reduction 戦略](#12-stage-別-cost-reduction-戦略)
13. [Anti-patterns と落とし穴](#13-anti-patterns-と落とし穴)
14. [Bottom-up Cost Forecast 構築 6 ステップ](#14-bottom-up-cost-forecast-構築-6-ステップ)
15. [Per-customer / Per-transaction cost](#15-per-customer--per-transaction-cost)
16. [AI / Compute cost 構造](#16-ai--compute-cost-構造)
17. [数値例 5 ケース](#17-数値例-5-ケース)
18. [Cost DD チェックリスト 50 項目](#18-cost-dd-チェックリスト-50-項目)
19. [出典一覧](#19-出典一覧)

---

## 1. 前提とコスト分類の根本

コスト分析は「どの軸で分類するか」で結論が変わるため、最初に分類軸を厳密に定義する。実務で使う軸は以下の 5 つ。

### 1.1 軸 A: 固定費 (Fixed) vs 変動費 (Variable) vs 半変動費 (Semi-variable)

| 区分 | 定義 | 数式での扱い | 例 |
|---|---|---|---|
| Fixed cost | 短期 (1 年以内) において **operating volume の変化に対し変動しない** コスト | $C_F = \text{const}$ | オフィス賃料、正社員給与、減価償却、SaaS ライセンス (固定数ユーザ分) |
| Variable cost | Operating volume に **比例** して変動するコスト | $C_V = v \times Q$ ($v$: 単価, $Q$: 数量) | 原材料、パッケージング、決済手数料、従量課金型 hosting |
| Semi-variable | 一定までは固定、閾値超で変動 (step function 含む) | $C_{SV} = C_0 + v \times \max(0, Q - Q_0)$ | カスタマーサポート (一定人数までは固定、超過で増員)、AWS Reserved Instance + on-demand |

**重要な落とし穴**: 「変動費」と呼んでいても実態は半変動なケースが多い。代表例:
- **Marketing**: 「売上の X%」と仮定しがちだが、実際は契約単位 (年契約のメディアバイ) や headcount (社内チーム) で半固定。short-term には変動できない。
- **Customer Success (CS)**: 「契約 → CS allocation」と単純比例させがちだが、実態は CS 1 人あたり担当 ARR がレンジで存在し step function。
- **Compute (AWS / GCP)**: Reserved + Savings Plans 部分は固定、残りは変動。AI training のように burst 的に発生する場合は予算管理上 fixed として扱う方が誤差が少ない。

固定/変動の判定は **時間軸** に依存する。短期 (1Q 以内) では固定だが、中期 (1-2 年) では変動可能なものは「中期変動費」として別管理する。

### 1.2 軸 B: 直接費 (Direct) vs 間接費 (Indirect) — COGS vs OpEx 境界

GAAP / IFRS 上、COGS (Cost of Goods Sold = 売上原価) には **revenue 獲得に直接紐づくコスト** のみを計上する。境界判断は業態により幅があるが、以下が標準。

| 業態 | COGS に含めるべき | OpEx (含めない) |
|---|---|---|
| SaaS | Hosting, 3rd party API (Twilio/Stripe など仕入れ型), 1st-line support, customer success の一部, データセンター減価償却 | Sales rep, Marketing, R&D, G&A |
| D2C / EC | BOM (Bill of Materials), packaging, fulfillment, payment processing, returns provision | Marketing (CAC), HQ headcount |
| Marketplace | Payment processing, fraud, ops support to facilitate transactions | Marketing, R&D |
| Hardware | BOM, manufacturing labor, yield loss, freight in, warranty provision | R&D, S&M, G&A |
| Fintech (lending) | Cost of funds (利息費用), loan losses (CECL/ECL), KYC, fraud loss, interchange | Marketing, G&A |
| Bio (上市後) | API (Active Pharmaceutical Ingredient), CMO 製造費, packaging, royalty | R&D, S&M, G&A |
| AI 製品 | Inference compute, human reviewer (RLHF inference 段階), data labeling (オン going) | Training compute (一部 capitalize 議論あり), R&D |

**Customer Success (CS) の分類**: 業態と機能で分かれる。
- Onboarding / 1st-line support → COGS
- Renewal / Expansion 営業要素 → S&M
- Strategic Account Management (戦略的顧客対応) → S&M
- Pure G&A 計上は誤り (CS を G&A に入れる SaaS 企業は要再分類)

出典: KeyBanc Capital Markets "SaaS Survey" 2023 / 2024 で定義整理。

### 1.3 軸 C: Cash cost vs Non-cash cost

| 区分 | 内容 | 三表での流れ |
|---|---|---|
| Cash cost | 当期キャッシュアウト発生 | P/L 費用 = CF 流出 |
| Non-cash cost | キャッシュアウトを伴わない | P/L 費用 → CF で add-back |

代表的な non-cash cost:
- **D&A (Depreciation & Amortization)**: 過去の capex を期間配分
- **SBC (Stock-Based Compensation)**: 株式付与費用 (fair value)。CF add-back し、BS では APIC (Additional Paid-In Capital) を増加
- **Asset write-off / impairment**: 資産簿価切り下げ
- **CECL / ECL provision**: 期待信用損失引当 (引当時 non-cash、貸倒実現時 cash)
- **Inventory write-down**: 棚卸資産評価減

**SBC を non-cash と扱う論争**: GAAP 上 P/L に費用計上、CF 計算書で add-back されるが、**希薄化 (dilution) は実質的なキャッシュコスト** であるため "Adjusted EBITDA ex-SBC" を主指標とする企業評価には批判が多い (詳細は §10)。

### 1.4 軸 D: Capitalize vs Expense

ある支出を **資産計上 (capitalize)** するか **費用処理 (expense)** するかは、損益と現金繰りに大きく影響する。

| ケース | US-GAAP | IFRS | J-GAAP |
|---|---|---|---|
| 内部開発ソフトウェア (販売目的) | ASC 985-20: Technological feasibility 達成後 capitalize | IAS 38: 開発費要件満たせば capitalize | 研究開発費等会計基準: 原則費用、市場販売目的ソフトは一定要件で資産計上 |
| 内部利用ソフトウェア | ASC 350-40: Application development 段階 capitalize | IAS 38: 同様 | 自社利用ソフト: 将来便益確実なら資産計上 |
| 研究費 (Research) | 即時費用 | 即時費用 | 即時費用 |
| 開発費 (Development) | 上記分類による | IAS 38 要件満たせば capitalize | 原則費用 (一部例外) |
| Customer acquisition cost (commission) | ASC 606 / 340-40: 1 年超契約は capitalize & 償却 | IFRS 15: 同様 | 同等 |

詳細は §11 で展開。

### 1.5 軸 E: Activity-based costing (ABC) vs Functional costing

| 手法 | 内容 | 用途 |
|---|---|---|
| Functional costing | コストを機能 (S&M/R&D/G&A) で分類 | 外部報告、IPO 開示、業界比較 |
| Activity-based costing (ABC) | コストを「活動 (activity)」単位に再配賦 | 価格決定、製品/顧客別 profitability、process improvement |

スタートアップ初期は functional で十分。Series C 以降、複数製品・複数顧客セグメントになると ABC を導入し「製品別貢献利益」「顧客セグメント別 fully loaded margin」を出す。

---

## 2. P/L コスト構造の標準形

### 2.1 標準 P/L レイアウト (SaaS 例)

```
Revenue                        100.0%
  - COGS                       -22.0%
= Gross Profit                  78.0%       Gross Margin
  - S&M                        -35.0%
  - R&D                        -22.0%
  - G&A                        -10.0%
= Operating Income              11.0%       Operating Margin
  - Net interest                -0.5%
  - Tax                         -2.5%
= Net Income                     8.0%       Net Margin
```

### 2.2 各層の式

$$
\text{Gross Profit} = \text{Revenue} - \text{COGS}
$$

$$
\text{Gross Margin} = \frac{\text{Gross Profit}}{\text{Revenue}}
$$

$$
\text{OpEx} = \text{S\&M} + \text{R\&D} + \text{G\&A}
$$

$$
\text{Operating Income (EBIT)} = \text{Gross Profit} - \text{OpEx}
$$

$$
\text{EBITDA} = \text{EBIT} + \text{D\&A}
$$

$$
\text{Adj. EBITDA} = \text{EBITDA} + \text{SBC} + \text{One-time items}
$$

(Adj. EBITDA の SBC 加算は批判含み。§10 参照。)

### 2.3 業態別の項目修正

| 業態 | 標準形からの修正点 |
|---|---|
| SaaS | 上記そのまま |
| Marketplace | Revenue は Net (= GMV - take rate share) で記載するのが標準。GMV は Operating metric として注記 |
| D2C | Marketing を S&M から切り出して "Marketing" として独立表示することが多い |
| Hardware | COGS の細分化 (BOM, mfg, freight, warranty) を 10-K 注記で開示 |
| Fintech (lending) | Net Interest Income (Interest revenue - Interest expense) を gross profit 相当として表示 |
| Bio | 売上前は R&D が支配的、上市後は COGS, S&M が拡大 |

### 2.4 SaaS の S&M 細分化 (Sub-classification)

S&M を「新規取得」と「既存拡大」に分けるのは、unit economics 評価で必須。

| 区分 | 内容 | 担当 ARR | コスト分母 |
|---|---|---|---|
| New ARR S&M | 新規顧客獲得 | New ARR | New CAC = 新規 S&M / New ARR |
| Expansion S&M | 既存顧客の追加販売 | Expansion ARR | Expansion CAC = Expansion S&M / Expansion ARR |
| Renewal S&M | 既存顧客の維持 (CSM 含む) | Renewal ARR (NRR の維持寄与) | Renewal cost = Renewal S&M / Retained ARR |
| Brand / Demand gen | 中長期需要喚起 | 全体に按分 | (按分) |

ベンチマーク (Bessemer State of the Cloud / OpenView):
- New ARR の獲得 CAC payback: 12-24 ヶ月 (median 18)
- Expansion ARR の CAC payback: 6-12 ヶ月 (median 9)

### 2.5 会計分類と財務分析分類の差

外部開示 (10-K, 有報) の R&D / S&M / G&A は会計上の機能分類だが、内部分析では以下のように再構成することが多い:

| 内部分析区分 | 含めるもの |
|---|---|
| Customer-facing variable cost | COGS + S&M variable (commission, ad spend) |
| Customer-facing fixed cost | S&M fixed (rep base salary), CS fixed |
| Product cost | R&D 全額 |
| Corporate cost | G&A |

これは Bessemer の "Cloud Index" のセグメンテーションに近い。

---

## 3. 業態別 COGS 構造の解剖

### 3.1 SaaS の COGS

| サブ項目 | 中央値 (% of revenue) | 説明 |
|---|---|---|
| Hosting / cloud infra | 5-10% | AWS / GCP / Azure。Reserved + on-demand |
| 3rd party API | 1-5% | Twilio, Stripe (lossless pass-through 部分は注意), email API |
| 1st-line support | 2-4% | Tier 1 ticket 対応 |
| Customer Success (COGS 部分) | 3-6% | Onboarding, technical CSM の一部 |
| Data infra / analytics | 1-2% | Snowflake, Datadog, Segment 等 |
| Hosting amortization (capex 償却) | 0-1% | Self-hosted の場合 |
| **合計 COGS** | **15-25%** | Gross margin 75-85% |

出典: KeyBanc Capital Markets SaaS Survey 2024。なお Vertical SaaS で実装 (Implementation) を recurring に組み込んでいる場合は COGS が 5-10pt 高い。

### 3.2 D2C / EC の COGS

| サブ項目 | 中央値 (% of revenue) | 説明 |
|---|---|---|
| BOM (Bill of Materials / 商品原価) | 25-40% | 商材依存。アパレル 25-30%、化粧品 15-20%、CPG 35-45% |
| Packaging | 2-5% | 一次包装 + 二次包装 (ギフト含む) |
| Inbound freight | 1-3% | 工場 → 倉庫 |
| Outbound fulfillment | 5-10% | 倉庫 → 顧客 (ピック・梱包・配送) |
| Payment processing | 2-3% | 2.5-3.0% (国内 Stripe / Square)、海外 1.8-2.9% |
| Returns provision | 1-5% | アパレル 10-30%、化粧品 2-5%、食品 < 1% |
| Customer service (CS) | 1-2% | コール / チャット対応 |
| **合計 COGS** | **35-60%** | Gross margin 40-65% |

### 3.3 Marketplace の COGS

Marketplace は **Net Revenue (= take rate × GMV)** ベースで損益を作る。

| サブ項目 | 中央値 (% of net revenue) | 説明 |
|---|---|---|
| Payment processing | 10-15% | GMV ベース 2-3% を net revenue で割り戻すと 10-15% |
| Fraud / chargeback | 2-5% | クレカ不正、なりすまし |
| Customer support / disputes | 5-15% | 取引仲裁、買い手売り手両方の問い合わせ |
| Trust & safety | 1-3% | KYC, content moderation |
| **合計 COGS** | **18-40%** | Gross margin 60-82% |

注意: GMV を revenue として計上する誤りは ASC 606 (principal vs agent) の論点で 2018-2020 に多くの上場 marketplace が再分類を受けた。Net 計上が大半。

### 3.4 Hardware の COGS

| サブ項目 | 中央値 (% of revenue) | 説明 |
|---|---|---|
| BOM (部品原価) | 35-55% | 設計依存 |
| Manufacturing labor | 3-8% | OEM/ODM 委託の場合は manufacturing fee に含まれる |
| Yield loss (歩留損) | 2-10% | 立ち上げ初期 10%+、成熟後 2-3% |
| Inbound + outbound freight | 3-7% | 海外生産は inbound 費が嵩む |
| Warranty provision | 1-5% | 1 年保証で 1-3%、長期保証で 5%+ |
| Tooling 償却 | 1-3% | 金型・治具 |
| **合計 COGS** | **50-75%** | Gross margin 25-50% |

Apple のようなプレミアム機器は 38-44% gross margin を維持 (10-K)。コモディティ家電は 15-25%。

### 3.5 Fintech (Lending) の COGS

Lending 系は P/L が銀行型に近く、**Net Interest Income (NII)** を gross profit 相当として扱う。

```
Interest revenue              100.0
- Interest expense (cost of funds)   -35.0
= Net Interest Income           65.0
- Loan losses (CECL provision) -15.0
= NII after provisions          50.0
- Non-interest income items    +5.0  (interchange, late fee, etc)
- OpEx                         -40.0
= Pretax income                 15.0
```

| サブ項目 | 範囲 (% of interest revenue) | 説明 |
|---|---|---|
| Cost of funds | 25-50% | 調達金利。VC 株式 → 低、warehouse facility → SOFR + 200-500bp、deposit funded → 低 |
| Loan losses (CECL) | 10-30% | Prime 2-5%、subprime 10%+。Vintage 別管理が必須 |
| Fraud loss | 1-3% | KYC 強度に依存 |
| KYC / AML compliance | 1-3% | 1 件あたり ¥100-500 |
| Servicing | 2-5% | Bookkeeping, collection |

CECL (Current Expected Credit Loss, ASC 326) は 2020 年から US 上場企業に適用。ライフタイムの期待損失を貸付実行時に引当てるため、growth 段階の lender は P/L が大幅マイナスになる (Affirm 2021 の例)。

### 3.6 Bio / 製薬の COGS

Pre-revenue 段階では COGS は実質ゼロ。R&D が支配的。上市後:

| サブ項目 | 範囲 (% of revenue) | 説明 |
|---|---|---|
| API / 原薬 | 5-15% | 化合物の製造原価。Biologics は高い (15-30%) |
| CMO 製造費 | 5-15% | Contract Manufacturing Organization 委託費 |
| Packaging / 検査 | 2-5% | GMP 管理含む |
| Royalty (in-licensing) | 5-25% | ライセンス契約により大幅変動 |
| Distribution | 2-5% | 卸 (Cardinal Health 等) のマージン |
| **合計 COGS** | **20-60%** | Gross margin 40-80%。Biologics は 80%+ |

R&D の取扱い: §11 capitalize 議論参照。Bio は概ね expense される (clinical 不確実性が高いため)。

### 3.7 AI スタートアップの COGS

新興分野で会計実務が固まりきっていない領域。論点が多い。

| サブ項目 | 範囲 (% of revenue) | 説明 |
|---|---|---|
| Inference compute | 30-70% | Foundation model API call (OpenAI/Anthropic), or self-hosted GPU |
| Training compute | (capitalize 議論) | §11 / §16 参照。期間費用処理が多数 |
| Data labeling (継続分) | 5-15% | Scale AI, Surge, in-house annotator |
| Human reviewer (RLHF / safety) | 3-10% | コンテンツモデレーション、応答品質チェック |
| Hosting (non-AI part) | 3-8% | 通常の web infra |
| **合計 COGS (生成 AI スタートアップ)** | **40-90%** | Gross margin 10-60% (variability 極大) |

代表的 disclosure (推定): OpenAI 2023 GP margin 推定 30-50% (compute 負担)、Anthropic 同様レンジ。Vertical AI (Harvey, Hippocratic) は 40-70% を狙う。

「AI gross margin の構造的低さ」は 2024-2025 年の重要論点。詳細は §16 で。

---

## 4. OpEx 三大区分 (S&M / R&D / G&A)

### 4.1 S&M (Sales & Marketing)

#### 4.1.1 構成

| サブ項目 | 内容 | 固定/変動 |
|---|---|---|
| Account Executive (AE) | 商談クローズ担当営業の base + benefit | 固定 (短期) |
| AE commission | 売上連動報酬 | 変動 |
| SDR (Sales Development Rep) | リード作成・初期接点担当 | 固定 |
| Sales engineer / Solutions architect | 技術営業 | 固定 |
| Marketing programs | デジタル広告、コンテンツ、SEO | 半変動 (予算枠 + 出稿変動) |
| Events / sponsorship | カンファレンス、イベント | 固定 (年初予算) |
| Brand / PR | ブランド広告、広報 | 固定 |
| Partner / channel | チャネル営業、パートナー報酬 | 変動 |
| Sales operations | RevOps, Salesforce admin, deal desk | 固定 |
| Marketing operations | MA tool admin, Hubspot/Marketo | 固定 |

#### 4.1.2 Magic Number / Sales Efficiency

$$
\text{Magic Number} = \frac{\Delta \text{ARR}_{Q} \times 4}{\text{S\&M}_{Q-1}}
$$

ベンチマーク (Bessemer):
- < 0.5: 非効率 (要見直し)
- 0.5-1.0: 標準
- 1.0-1.5: 効率的
- 1.5+: アクセル踏むべき

#### 4.1.3 CAC Payback Period

$$
\text{CAC Payback} = \frac{\text{CAC}}{\text{ARPU} \times \text{Gross Margin}}
$$

(月数で表示)

ベンチマーク (OpenView SaaS Benchmarks 2024):
- SMB SaaS: 6-12 ヶ月
- Mid-market: 12-18 ヶ月
- Enterprise: 18-30 ヶ月

### 4.2 R&D (Research & Development)

#### 4.2.1 構成

| サブ項目 | 内容 |
|---|---|
| Engineering (SWE) | フロント/バック/SRE/プラットフォーム |
| Product Management | PdM, PMM の一部 |
| Design (UI/UX) | デザイナー |
| QA / Test engineering | テスト自動化、品質保証 |
| Data / ML engineering | データ基盤、ML/AI チーム |
| Security engineering | アプリ/インフラセキュリティ |
| Dev tools / SaaS | GitHub, CI/CD, Linear, Figma 等 |
| Cloud spend (R&D 用) | Dev/staging 環境 (本番は COGS) |
| R&D facility allocation | オフィスの R&D 占有部分 |

#### 4.2.2 R&D 効率指標

$$
\text{R\&D as \% of revenue} = \frac{\text{R\&D expense}}{\text{Revenue}}
$$

成熟段階別ベンチマーク (Bessemer):
- Series A-B: 40-70% (revenue 規模小)
- Series C-D: 25-40%
- Pre-IPO: 18-25%
- Public mature: 12-20%

注意: capitalize 部分 (ASC 350-40) は P/L の R&D に乗らないため、capitalize 比率が高い企業は見かけ上 R&D% が低い (§11 参照)。

### 4.3 G&A (General & Administrative)

#### 4.3.1 構成

| サブ項目 | 内容 |
|---|---|
| Finance / Accounting | CFO, controller, FP&A, AP/AR, 経理 |
| Legal | GC, contracts, compliance |
| HR / People ops | recruiting, HRBP, L&D |
| IT / Internal systems | corp IT, identity, MDM |
| Facilities | オフィス賃料、設備 |
| Executive | CEO, COO, exec staff |
| External professional fees | Audit, legal counsel, consultant |
| Insurance | D&O, cyber, etc. |
| Public company readiness | SOX, IR, audit fee 増分 (Pre-IPO) |

#### 4.3.2 G&A 効率指標

$$
\text{G\&A as \% of revenue} = \frac{\text{G\&A expense}}{\text{Revenue}}
$$

成熟段階別 (KeyBanc 2024):
- Series A-B: 20-30% (revenue 小、固定費的)
- Series C-D: 12-18%
- Pre-IPO: 10-14% (audit/SOX 増)
- Public mature: 7-10%

公開企業で G&A 7% 以下を持続できる企業は希少 (Adobe, Microsoft クラス)。

### 4.4 OpEx 全体の Rule of 40 連動

$$
\text{Rule of 40} = \text{Growth rate (\%)} + \text{FCF margin (\%)} \geq 40\%
$$

OpEx 比率は Growth と Margin の両方に直結する。例えば S&M 50%、R&D 30%、G&A 15% で OpEx 95%、GM 75% なら Operating margin = -20%。Growth が +60% でないと Rule of 40 を満たさない。

---

## 5. 業態別ベンチマーク表 (中央値 / 良 / 優秀)

すべて **% of revenue** ベース。出典は §19 参照。

### 5.1 SaaS (B2B、ARR ≥ $10M)

| 区分 | 中央値 | 良 (Top quartile) | 優秀 (Top decile) |
|---|---|---|---|
| Gross Margin | 70% | 75% | 80%+ |
| S&M | 40% | 30% | 20% |
| R&D | 25% | 20% | 15% |
| G&A | 15% | 10% | 7% |
| Operating Margin | -10% | +10% | +30% |
| FCF Margin | -5% | +15% | +35% |
| SBC % of revenue | 25% | 18% | 12% |

出典: Bessemer State of the Cloud 2024, KeyBanc SaaS Survey 2024, Meritech Public Comp dashboard。

### 5.2 Marketplace (B2C / B2B、Net Revenue ベース)

| 区分 | 中央値 | 良 | 優秀 |
|---|---|---|---|
| Take rate | 15-20% | 20-25% | 25%+ (Etsy, Airbnb) |
| Net Gross Margin | 65% | 75% | 80%+ |
| S&M (% of net revenue) | 35% | 25% | 18% |
| R&D | 18% | 14% | 10% |
| G&A | 12% | 9% | 7% |
| Operating Margin | -5% | +15% | +30% |
| Payment processing (% of GMV) | 2.7% | 2.4% | 2.0% |

出典: a16z Marketplace 100 / a16z Marketplace metrics, Andreessen Horowitz 2023。

### 5.3 D2C / EC (DTC)

| 区分 | 中央値 | 良 | 優秀 |
|---|---|---|---|
| Gross Margin | 50% | 60% | 70% (高ブランド) |
| Marketing (% of revenue) | 35% | 25% | 15% |
| Operations (CS/fulfillment OpEx 部分) | 12% | 9% | 7% |
| G&A | 12% | 9% | 7% |
| Operating Margin | -10% | +5% | +15% |
| Returns rate (アパレル) | 25% | 15% | 8% |
| Returns rate (化粧品) | 5% | 3% | 1% |

出典: Modern Retail Benchmarks 2023, eMarketer DTC Survey 2024, Shopify Plus Benchmarks。

### 5.4 Hardware

| 区分 | 中央値 | 良 | 優秀 |
|---|---|---|---|
| Gross Margin | 30% | 40% | 50% (premium) |
| S&M | 15% | 12% | 9% |
| R&D | 12% | 10% | 8% |
| G&A | 8% | 6% | 5% |
| Operating Margin | -5% | +12% | +25% |
| Inventory carrying | 7% | 5% | 3% |
| Warranty provision | 3% | 2% | 1% |

出典: Bessemer Hardware Index, NDR Hardware peers, Apple/HP/Dell 10-K 比較。

### 5.5 Fintech (Lending)

| 区分 | 中央値 | 良 | 優秀 |
|---|---|---|---|
| Net Interest Margin (NIM) | 8% | 12% | 15% |
| Loan loss rate (% of avg loan book) | 4% | 2.5% | 1.5% |
| CAC payback (months) | 18 | 12 | 9 |
| Cost-to-income ratio | 70% | 55% | 45% |
| Operating Margin | -10% | +10% | +25% |

出典: NDR Fintech, MoffettNathanson Fintech, S&P Capital IQ。

### 5.6 Bio / Biotech (Pre-commercial)

Revenue 前のため "% of revenue" ではなく **資金消費 (cash burn) ベース**。

| 区分 | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| 累計 R&D 投資 (USD M) | 5-15 | 30-100 | 150-500 |
| 月次 burn (USD M) | 0.5-1.5 | 1.5-5 | 5-15 |
| 試験参加患者数 | 20-100 | 100-500 | 500-3,000+ |
| 期間 | 1-2 年 | 2-3 年 | 3-5 年 |

出典: Tufts CSDD, BIO Industry Analysis, EvaluatePharma。

### 5.7 AI 製品 (Pure-play / Vertical)

| 区分 | 中央値 | 良 | 優秀 (将来目標) |
|---|---|---|---|
| Gross Margin | 40% | 60% | 75% |
| Compute (% of revenue) | 50% | 30% | 15% |
| S&M | 35% | 25% | 18% |
| R&D | 35% | 25% | 18% |
| G&A | 12% | 9% | 7% |
| Operating Margin | -50% | -10% | +20% |

注意: 業態としての benchmark が固まり切っていない (2024-2025 年時点)。代表企業データ点で構成。出典: a16z "The Cost of Compute" 2024, Sequoia "AI's $200B Question" 2023。

---

## 6. Headcount 駆動 cost modeling

スタートアップのコストの **60-80% は人件費起点** (給与 + 関連 cost)。Headcount plan を起点にコストモデルを組むのが標準。

### 6.1 Fully Loaded Cost (FLC) の式

$$
\text{FLC} = \text{Base Salary} \times \text{Loading factor} + \text{Equipment} + \text{Allocations}
$$

Loading factor の構成:

| 要素 | US 一般 | JP 一般 | India |
|---|---|---|---|
| 社会保険・税 (employer side) | 8-12% | 14-16% | 12-15% |
| ボーナス (annual incentive) | 10-25% | 5-20% | 10-20% |
| Benefits (医療、生命保険、退職金) | 15-25% | 5-10% | 5-10% |
| Office space allocation | 5-10% | 5-10% | 3-5% |
| IT / SaaS tools | 3-7% | 3-7% | 3-7% |
| L&D / training | 1-3% | 1-3% | 1-3% |
| **Loading factor 合計** | **40-80%** | **30-65%** | **35-60%** |

実務的には **base × 1.3-1.5** を使うのが簡便法。詳細モデルでは上記内訳を個別に計算。

### 6.2 国別エンジニア FLC 比較 (2024-2025 推定)

| Role | US (Bay Area) | US (Remote) | JP (東京) | India (Bangalore) | EU (Berlin) | LATAM |
|---|---|---|---|---|---|---|
| Junior SWE | $150K-200K | $120K-160K | ¥6-9M | $25-40K | €60-80K | $40-60K |
| Mid SWE | $200K-280K | $160K-220K | ¥9-14M | $40-70K | €80-110K | $60-90K |
| Senior SWE | $280K-400K | $220K-320K | ¥14-22M | $70-120K | €110-150K | $90-130K |
| Staff/Principal SWE | $400K-650K | $320K-500K | ¥20-35M | $120-200K | €150-220K | $130-200K |
| Eng Manager | $300K-450K | $250K-380K | ¥15-25M | $80-150K | €120-170K | $100-150K |
| FLC = 1.4x base (目安) | $210K-560K | $170K-450K | ¥8-30M | $35-280K | €85-310K | $55-280K |

注: 数値は base salary (cash) 中央値レンジ、FLC は ×1.4 換算。Levels.fyi, Glassdoor, Pave 2024 データに基づく推定。

### 6.3 Onboarding Lag (立ち上がり遅延)

新規採用は即戦力ではない。

| Role | Ramp 期間 | 期間中 productivity |
|---|---|---|
| AE (Sales) | 6-9 ヶ月 | Month 1: 0%, Month 3: 30%, Month 6: 70%, Month 9: 100% |
| SDR | 3-4 ヶ月 | Month 1: 0%, Month 2: 50%, Month 4: 100% |
| Engineer | 3-6 ヶ月 | Month 1: 20%, Month 3: 60%, Month 6: 100% |
| Product Manager | 4-6 ヶ月 | 同上 |
| CSM | 3-4 ヶ月 | 同上 |
| GM / Exec | 6-12 ヶ月 | 段階的 |

#### モデルへの組込み式

$$
\text{Productive HC}_t = \sum_{i \in \text{HC}_t} \text{Ramp}_i(t - \text{HireDate}_i)
$$

Sales productivity (closed ARR/AE) は productive HC ベースで計算する。固定コストは total HC ベース。この差が Series B-C で重要 (採用が前倒しで FLC が先行発生する)。

### 6.4 Attrition (離職率)

| Role | 年間 attrition (中央値) |
|---|---|
| Engineering | 12-18% |
| Product / Design | 10-15% |
| Sales (AE) | 25-35% |
| SDR | 40-60% (短期 churn 高い) |
| Customer Success | 15-20% |
| G&A (Finance/HR/Legal) | 10-15% |
| Executive | 5-10% |

出典: LinkedIn Talent Insights 2024, Lattice People Strategy Report 2023。

Attrition のコストモデル影響:
- Productive HC < Total HC (常に欠員あり)
- 採用コスト (recruiter fee, agency 20-30% of base) が継続発生
- Knowledge loss → 残留メンバーの productivity drop

### 6.5 Equity Compensation の HC 比率

| Role / Stage | Equity (% of company, fully diluted) |
|---|---|
| Engineer (個人貢献者) Junior | 0.02-0.05% |
| Engineer Senior | 0.05-0.15% |
| Engineer Staff | 0.15-0.40% |
| Eng Manager | 0.10-0.30% |
| Director / Sr Director | 0.30-0.80% |
| VP | 0.50-1.50% |
| C-level (non-founder) | 0.75-3.00% |
| CTO / 最初の 10 人 | 0.50-2.00% |

出典: Carta Equity Reports 2024, Pave Tech Compensation Survey。

注意: Series 進行に伴い % は希薄化、ドル建ては増加する。Cliff (1 年) と vesting schedule (4 年) は標準。

---

## 7. Variable cost と Unit Economics

### 7.1 Unit Margin

$$
\text{Unit Margin} = \text{ASP} - \text{Direct Variable Cost}
$$

ここで Direct Variable Cost は **その 1 単位を生み出すために発生する変動費のみ** を含む。固定費 allocation は含めない。

### 7.2 Contribution Margin Tier (D2C 標準)

D2C / EC では下記 3 階層で margin を見る:

| Tier | 定義 | 数式 |
|---|---|---|
| CM1 (Tier 1) | 商品単位の粗利 | $\text{ASP} - \text{BOM} - \text{Packaging} - \text{Inbound freight}$ |
| CM2 (Tier 2) | CM1 から物流・決済を控除 | $\text{CM1} - \text{Outbound fulfillment} - \text{Payment processing} - \text{Returns provision}$ |
| CM3 (Tier 3) | CM2 から marketing 控除 | $\text{CM2} - \text{Variable marketing (CAC)}$ |

CM3 がプラスでないと「広告打つほど赤字が拡大」する状態。

#### 数値例
- ASP ¥10,000
- BOM ¥3,000、Packaging ¥500、Inbound ¥200 → CM1 = ¥6,300 (63%)
- Fulfillment ¥800、Payment ¥250、Returns ¥300 → CM2 = ¥4,950 (49.5%)
- Variable marketing (CAC of new customer / repeat purchase rate normalized) ¥3,000 → CM3 = ¥1,950 (19.5%)

### 7.3 Marginal cost vs Average cost

$$
MC = \frac{dTC}{dQ}, \quad AC = \frac{TC}{Q}
$$

スケール初期は MC < AC (固定費が分散) → AC 低下、利益率改善。
ある点を超えると MC > AC → AC 上昇 (capacity 制約、coordination 増)。

### 7.4 Capacity bottleneck と TOC (制約理論)

Eliyahu M. Goldratt "The Goal" の theory of constraints。

最も律速な工程 (bottleneck) のスループットが全体のスループットを決める。
- SaaS: Sales rep 数 (年間 quota × rep 数)
- Hardware: Production line capacity
- Marketplace: Supply side (driver, host, seller) inventory
- Bio: Clinical site capacity (患者リクルート速度)

コスト最適化は bottleneck 周辺に集中投資、非 bottleneck は積極的に放置するのが原理 (大半のスタートアップは ALL 工程に均等投資して非効率)。

### 7.5 LTV / CAC との接続

$$
\text{LTV} = \frac{\text{ARPU} \times \text{Gross Margin}}{\text{Churn rate}}
$$

$$
\frac{\text{LTV}}{\text{CAC}} \geq 3
$$

これを Variable cost 視点で再構成すると:

$$
\frac{\text{LTV}}{\text{CAC}} = \frac{(P - VC) / (1 - r)}{C_{acq}}
$$

- $P$: ARPU、$VC$: Variable cost per customer per period、$r$: retention rate (= 1 - churn)、$C_{acq}$: CAC

VC が増える (compute、CS allocation) と LTV が圧迫される。AI 製品でこの構造が顕著 (§16)。

---

## 8. Operating Leverage と Break-even

### 8.1 Operating Leverage (経営レバレッジ)

$$
\text{Operating Leverage} = \frac{\% \Delta \text{EBIT}}{\% \Delta \text{Revenue}}
$$

または contribution margin ベース:

$$
\text{DOL (Degree of Operating Leverage)} = \frac{\text{Contribution Margin}}{\text{EBIT}}
$$

固定費比率が高いほど DOL は大きい。

#### 業態別 DOL 典型値

| 業態 | DOL レンジ | コメント |
|---|---|---|
| SaaS (Pure software) | 3-6 | 限界コスト極小、固定 R&D 大 |
| Marketplace | 2-4 | Variable processing あり |
| Hardware | 1.5-3 | Variable BOM 大 |
| D2C | 1.3-2 | Variable BOM/物流大 |
| Service / Consulting | 1-1.5 | ほぼ全変動費 |
| Bio (上市後) | 4-8 | 固定 R&D, S&M 大 |

### 8.2 Break-even Analysis

#### 単純 Break-even

$$
\text{Break-even Revenue} = \frac{\text{Fixed Cost}}{\text{Contribution Margin Ratio}}
$$

Contribution Margin Ratio = $(P - VC) / P$

#### Multi-product break-even

複数製品の場合は **加重平均 contribution margin** で計算:

$$
\bar{CM} = \sum_i w_i \times CM_i
$$

ここで $w_i$ は製品 $i$ の revenue mix。

### 8.3 Cash Break-even vs Accounting Break-even

| 区分 | 数式 | 意味 |
|---|---|---|
| Accounting break-even | EBIT = 0 | P/L ベース、D&A 含む |
| Cash break-even | EBITDA = 0 (D&A 除外) | 当期キャッシュアウト = キャッシュイン |
| Free cash flow break-even | FCF = 0 (D&A, capex, WC 考慮) | 真の自己資金充足 |

スタートアップ評価では **FCF break-even** を最重要視する (Adj. EBITDA が黒字でも capex/WC 負担で resort to fundraise が継続するケースが多い)。

### 8.4 数値例: SaaS Series B の Break-even

```
Revenue (ARR run rate)         $20.0M
Gross Margin                   75%  → Gross Profit $15.0M
S&M                            $9.0M  (45%, 主に AE 給与+commission)
  内: Variable S&M             $2.5M  (commission のみ)
  内: Fixed S&M                $6.5M
R&D                            $7.0M  (35%, 主に engineer FLC)
G&A                            $3.0M  (15%, finance/legal)

Total Fixed cost (除く COGS変動)  = $6.5M (S&M fixed) + $7.0M (R&D) + $3.0M (G&A) = $16.5M
Variable cost ratio (COGS + variable S&M) = 25% + 12.5% = 37.5%
Contribution margin ratio = 62.5%

Break-even Revenue = $16.5M / 0.625 = $26.4M ARR
```

つまり ARR を $20M → $26.4M (+32%) 成長させれば break-even。

---

## 9. Cost Curve / Scale 効果

### 9.1 Experience Curve (BCG)

Bruce Henderson (BCG, 1968) の提唱。

> Cumulative production が doubling するごとに、unit cost が 15-30% 低下する。

数式:

$$
C_n = C_1 \times n^{-b}, \quad b = -\log_2(1 - \text{learning rate})
$$

例: learning rate 20% (slope 80%) なら $b = \log_2(1.25) \approx 0.322$。
- 累積 1 万台時 unit cost ¥10,000
- 累積 10 万台時 (10x = $\log_2 10 \approx 3.32$ doublings) → $\$10000 \times 0.8^{3.32} \approx \$5,120$
- 累積 100 万台時 → ¥2,621

業態別 learning rate (代表値):
- 半導体: 25-30% (Moore 効果含む)
- 太陽光パネル: 22-25%
- LCD パネル: 25%
- 自動車: 12-15%
- 航空機: 15-20%
- ソフトウェア: 5-15% (限界コスト極小だが maintenance 増)

### 9.2 Economies of Scale

| メカニズム | 説明 | 例 |
|---|---|---|
| Bulk discount | 仕入数量増で単価下落 | 半導体 wafer、AWS Reserved |
| Fixed cost dilution | 固定費 / 売上比率が低下 | R&D, G&A の % of revenue |
| Negotiated pricing | 規模で sourcing 力強化 | enterprise SaaS の volume discount |
| Learning curve | §9.1 |
| Specialization | 専門化で生産性向上 | Eng team の機能別細分化 |

### 9.3 Diseconomies of Scale (規模の不経済)

逆向きの効果。一定規模を超えると発生。

| メカニズム | 説明 |
|---|---|
| Coordination cost | チーム間の調整コスト増 (Brooks's law: "Adding manpower to a late software project makes it later") |
| Bureaucracy | 承認プロセス、報告階層 |
| Communication overhead | n^2 の組み合わせ問題 |
| Dilution of culture | 採用基準低下、企業文化希薄 |
| Innovator's dilemma | 既存事業優先で破壊的革新を見落とす |

### 9.4 Network Economics (デジタル限界コスト)

ソフトウェア/デジタル財は限界コストが極小:

$$
MC \approx 0
$$

しかしこれは naive な近似。実際には:
- Compute MC > 0 (AI スタートアップで顕在化)
- Customer success MC > 0 (顧客増 → サポート要員増)
- 認証 / coordination MC > 0

「MC = 0」と仮定すると AI 製品で gross margin を過大評価する誤りを犯す。

### 9.5 Step Function (階段状) コスト

実態のコストは線形ではなく階段状。

例:
- Office: 50 人まで現オフィス、51 人で move
- AWS Reserved Instance: 100 unit 単位で contract
- AE: 1 rep が ARR $1.5M を担当、超えたら 2 人目

モデル化:

$$
C(Q) = C_0 \times \lceil Q / Q_0 \rceil
$$

Step が大きいと予算編成のリスク (1 ステップで cost が突然 +30% など)。

---

## 10. SBC (Stock-Based Compensation) の取扱い

### 10.1 三表での流れ

| 項目 | 影響 |
|---|---|
| P/L | Operating expense (S&M / R&D / G&A 各項目に按分) |
| BS | APIC (Additional Paid-In Capital) 増加、Equity 増加 |
| CF | Operating CF で add-back (non-cash) |
| 希薄化 | Share count 増加 → EPS 計算で希薄化反映 |

### 10.2 計算 (ASC 718 / IFRS 2)

Fair value で測定。RSU (Restricted Stock Unit) と Stock Option で異なる。

#### RSU
$$
\text{SBC expense} = \text{Grant date FV} \times \text{Vested shares}
$$

Grant date FV = 株価。Vesting period にわたり straight-line で expense (4 年 vesting なら毎年 25%)。

#### Stock Option
Black-Scholes か Lattice model で fair value を算定。

$$
C = S_0 N(d_1) - K e^{-rT} N(d_2)
$$

- $S_0$: 現在株価、$K$: 行使価格、$T$: 満期、$r$: 無リスク金利、$N$: 累積標準正規分布
- $d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2) T}{\sigma \sqrt{T}}$, $d_2 = d_1 - \sigma\sqrt{T}$
- $\sigma$: volatility

### 10.3 業態別 SBC % of revenue

| 業態 | 中央値 | 良 (低) | 悪 (高) |
|---|---|---|---|
| SaaS (public) | 22% | 14% | 35%+ (Snowflake, Datadog) |
| Marketplace | 15% | 10% | 25% |
| D2C | 8% | 5% | 12% |
| Hardware | 10% | 6% | 18% |
| Bio (Pre-revenue) | n/a (revenue 小) | n/a | n/a |
| AI スタートアップ | 30%+ | 20% | 50% |

出典: Meritech Public Comp 2024, Bessemer Cloud Index。

### 10.4 Adj. EBITDA ex-SBC への批判

代表批判 (Damodaran 2023, "Stock-based Compensation: Time to End the Charade"):

1. **希薄化は実質コスト**: シェア発行 = 既存株主への課税 (= キャッシュ流出と等価)
2. **Add-back は経営者の都合**: SBC を含めた "real EBITDA" でも Rule of 40 を満たせる企業のみが本物
3. **DCF の二重カウント**: WACC で equity cost を計上しつつ SBC add-back すると重複
4. **比較性低下**: SBC ratio が違う企業同士を Adj. EBITDA で比較すると過大/過小評価

実務的な落としどころ:
- DCF: SBC は P/L に残し、Equity value から SBC dilution を控除
- マルチプル: EV/Sales、Rule of 40 では SBC を含む値も併記

### 10.5 IPO 後の SBC burn-down

IPO 直後は historical grant の vesting で SBC 比率がピーク。3-5 年で正常化。

```
Year 0 (IPO): SBC % = 30%
Year 1: 28%
Year 2: 24%
Year 3: 20%
Year 4: 17%
Year 5+: 15% (maintenance level)
```

例: Snowflake 2020 IPO 時 SBC % > 50% → 2024 年 ~30%。

---

## 11. R&D Capitalization (ASC 350-40 / IAS 38 / J-GAAP)

### 11.1 ASC 350-40 (US-GAAP, 内部利用ソフト)

3 段階で扱いが変わる:

| Stage | 内容 | 処理 |
|---|---|---|
| Preliminary project | 概念設計、評価 | Expense |
| Application development | Coding, testing | **Capitalize** |
| Post-implementation | 運用、保守 | Expense |

Capitalize された無形資産は使用可能になった時点から **3-5 年** で straight-line 償却。

#### Capitalize の実務影響

例: 年間 R&D $100M、内 60% (=$60M) が application development 段階。

```
P/L impact:
  Without capitalize: R&D expense $100M
  With capitalize:    R&D expense $40M + 償却 ($60M / 4年 = $15M)
                    = $55M

Operating margin への影響: +$45M (revenue $1B なら +4.5pt)

CF への影響: なし (capex として CFI で計上)
```

つまり capitalize 比率が高い企業は **見かけ上 operating margin が高い** が、本質的なキャッシュ収益力は変わらない。比較時は調整必要。

### 11.2 ASC 985-20 (US-GAAP, 販売目的ソフト)

"Technological feasibility" 達成後 capitalize。実務的には "feasibility 達成" のタイミング判断が経営判断であり、SaaS 企業で discretion が大きい論点。

### 11.3 IAS 38 (IFRS)

Research expense、Development capitalize (要件満たせば)。要件:
- Technical feasibility
- Intent to complete
- Ability to use or sell
- Probable future economic benefits
- Adequate resources to complete
- Reliably measurable expenditure

US-GAAP より capitalize 範囲が広い。EU 系 SaaS で operating margin が高めに出るのはこれが一因。

### 11.4 J-GAAP

「研究開発費等に係る会計基準」(企業会計審議会 1998):
- 研究費: 即時費用
- 開発費: 原則費用 (US-GAAP より厳格)
- 例外: 自社利用ソフトで将来便益確実な場合 + 市場販売目的ソフトで製品マスター完成後

J-GAAP 採用企業は P/L に R&D が乗りやすい (見かけ operating margin 低)。

### 11.5 Tax R&D Credit (試験研究費控除 / R&D Tax Credit)

会計の capitalize/expense とは独立した税務優遇。

#### 日本 (法人税法 42 条)
- 総額型: 試験研究費の 6-14% を法人税額から控除 (上限あり)
- 中小企業は 12-17%
- オープンイノベーション型 (大学/中小との共同) で割増

#### US (IRC Section 41)
- Regular Research Credit: Qualified research expense (QRE) に対し 20% credit
- Alternative Simplified Credit: 14%
- 2022 年 TCJA で R&D は 5 年または 15 年で amortize 義務 (旧: expense 即時) → 多くの SaaS の short-term tax 負担増

### 11.6 Capitalize 戦略の判断基準

| 状況 | Capitalize 推奨 | Expense 推奨 |
|---|---|---|
| SOX 対応で margin 改善が市場評価に重要 | ◎ | |
| 早期 IPO 準備 | ◎ | |
| 内部経営判断重視、Cash 視点 | | ◎ |
| 監査負担最小化 | | ◎ (判断不要) |
| 投資家コミュニケーションで Adj 指標重視 | ◎ | |
| 比較可能性 (peer が expense している) | | ◎ |

---

## 12. Stage 別 Cost Reduction 戦略

### 12.1 Pre-revenue (Pre-Seed / Seed)

優先度: cash runway 延長 > scale。

| 領域 | 戦略 |
|---|---|
| Headcount | 10-15 名以内に抑える、co-founder + 早期 eng + 1-2 PMM |
| Office | Co-working / 自宅 |
| Cloud | AWS Activate / GCP for Startups の credit ($10K-100K) を最大活用 |
| Tooling | Free tier (GitHub, Notion, Linear) |
| Outsource | デザイン / マーケティング外注、社内固定費 fix しない |
| Marketing | Earned media (PR、SNS、コミュニティ) 中心、paid 最小 |
| Legal | テンプレート活用 (YC SAFE、J-KISS) |

数値目標: 月次 burn ¥10-30M、runway 18-24 ヶ月。

### 12.2 Early Revenue (Series A)

優先度: PMF 検証 + scale 準備。

| 領域 | 戦略 |
|---|---|
| Headcount | Engineer 主導、Sales 1-2 名、CS 1 名 |
| CAC 効率化 | Paid → Organic シフト (SEO、コミュニティ、Referral) |
| Tooling consolidation | 重複 SaaS 削減 (Notion か Confluence か、片方) |
| Cloud spend | Cost monitoring (Vantage, Cloudability) を導入、無駄を可視化 |
| Office | Small office (10-30 名想定) |

数値目標: ARR $1-5M、burn multiple 1.5-3x。

### 12.3 Growth (Series B-C)

優先度: efficient growth (scale + unit econ 維持)。

| 領域 | 戦略 |
|---|---|
| Vendor pricing | Renegotiate with volume (AWS EDP、Salesforce、Stripe) |
| Offshore engineering | Senior + offshore (Vietnam, Poland, India) blend |
| Marketing automation | MA tool (Marketo, Hubspot) で人件費効率化 |
| Sales playbook | Repeatable playbook を文書化、Onboarding 期間短縮 |
| BPO | Tier 1 support, AR/AP, expense process を BPO 化 |

数値目標: ARR $10-50M、Rule of 40 達成、Magic Number 0.7+。

### 12.4 Scale (Series D / Late stage)

優先度: efficient operation + IPO readiness。

| 領域 | 戦略 |
|---|---|
| Bulk procurement | Strategic sourcing 導入、3 年契約で割引獲得 |
| Real estate | Hub-and-spoke モデル、tier 2 city 拠点 |
| Process automation | RPA, AI 内部活用、low-code 導入 |
| HR efficiency | HR tech stack 統合 (HRIS, ATS, perf mgmt) |
| Compute optimization | Multi-cloud arbitrage、Reserved + Savings Plan 最大化 |

数値目標: ARR $50-200M、Operating margin > 0、FCF 黒字化視野。

### 12.5 Pre-IPO (S-1 提出 12 ヶ月前)

優先度: regulatory readiness + cost discipline 公開。

| 領域 | 戦略 |
|---|---|
| Tax optimization | Transfer pricing、IP holding、netting |
| Treasury efficiency | Cash management (T-bills, money market)、forex hedge |
| Compliance cost ramp | SOX (Section 404)、internal audit、Board structure |
| Audit | Big 4 監査人、PCAOB 対応 |
| IR / external comms | IRO 採用、guidance 整備 |

S-1 で公開する直近 3 年の P/L が evaluator 評価の基礎。Cost discipline ストーリーが必須。

---

## 13. Anti-patterns と落とし穴

### 13.1 Anti-pattern 1: Headcount 削減 = Cost Cut の単純思考

「コスト削減 = レイオフ」という短絡思考は ROI が低い。
- レイオフ → severance ($10-50K/人)、recruitment redo cost、knowledge loss
- 真の cost savings は **process 効率化 + tool consolidation + vendor renegotiation** で 20-30% 取れる
- レイオフ前にこれらを尽くすべき

### 13.2 Anti-pattern 2: SBC を Cash Cost と認識せず希薄化過大

Adj. EBITDA ex-SBC を主指標にしている経営は SBC を「見えないコスト」として運用しがち。
- 結果: Engineer 1 人を $200K cash + $200K SBC で雇う → "P/L 上は cash 部分のみ" として運用
- 5 年後の希薄化が過大、既存株主の return が毀損
- 監査: SBC を含めた **dilution-adjusted cost per FTE** で比較

### 13.3 Anti-pattern 3: Marketing を「変動費」と仮定

「売上の X%」モデルは forecast には便利だが実態を反映しない。
- 代理店契約は 6 ヶ月-1 年契約で半固定
- 社内 marketer の人件費は 100% 固定
- Brand campaign は年度予算で固定
- 真の variable は performance ad 部分 (全 marketing の 30-50%)

→ Marketing は「Fixed brand + Variable performance」の二層構造でモデル化。

### 13.4 Anti-pattern 4: Customer Success を G&A と誤分類

CS を G&A に入れる SaaS は分類エラー。
- Onboarding/Support → COGS
- Renewal/Expansion → S&M
- いずれも G&A ではない
- Mistake は KeyBanc Survey の比較で 20% 程度の企業に発見される

### 13.5 Anti-pattern 5: R&D Capitalize で Operating Margin ガス爆発

ASC 350-40 capitalize 比率を不自然に高めると:
- P/L Operating margin: 見かけ +5-10pt
- BS: Intangibles 急増
- CF: 変わらず (CFI で capex として出る)
- 監査リスク: feasibility 判定の根拠が薄いと再分類リスク

実務: peer comp での capitalize 比率 (10-K notes) を確認、極端に外れる場合は要警戒。

### 13.6 Anti-pattern 6: Compute Cost を線形と仮定

AI スタートアップの forecast で頻発:
- 「次の 1000 ユーザは現状の compute / ユーザで線形に増える」と仮定
- 実態: Inference は usage の偏り (Pareto 80/20)、burst で peak compute が突発
- LLM API 価格が変動 (OpenAI が 2024 年に値下げ)
- Self-hosted の場合は GPU lead time (B100 は 6 ヶ月待ち)

→ Compute は **percentile (P50, P95) ベース + scenario** でモデル化。

### 13.7 Anti-pattern 7: Headcount Plan に Attrition を入れ忘れる

Hiring plan = Net hires のつもりが、実態は gross hires (= net + attrition)。
- 例: 年初 100 名、年末目標 130 名
- Gross hires = 30 (net) + 100 × 15% (attrition) = 45
- Recruitment コストが 50% 過小

### 13.8 Anti-pattern 8: Allocation 漏れ

Department 別 P/L で **オフィス賃料、IT、Finance** が allocation されず、特定部門 (例: R&D) に全額計上されている。
- True department margin が見えない
- 投資判断 (どこを伸ばすか) を誤る

### 13.9 Anti-pattern 9: One-time vs Recurring の混在

"One-time" 名目で実態は recurring な費用 (例: 毎四半期 reorg cost)。
- Adj. EBITDA を not so adjusted にする
- 監査・投資家の信頼喪失

### 13.10 Anti-pattern 10: International Expansion Cost を Underestimate

海外進出で本社経費の 1.5-2x の cost を見落とす。
- Localization (UI, content, legal docs)
- Compliance (GDPR, CCPA, 各国 tax)
- Hiring (recruiter cost、relocation)
- Forex risk

US → Europe で revenue per HC が 60-70% に低下 (初年度) は典型。

---

## 14. Bottom-up Cost Forecast 構築 6 ステップ

### Step 1: Headcount Plan の確定

Role × Stage × Geography の 3 軸で展開。

| Role | Q1 | Q2 | Q3 | Q4 | 配置 |
|---|---|---|---|---|---|
| Engineer Senior | 8 | 10 | 13 | 15 | US 60%, India 40% |
| AE | 4 | 6 | 8 | 10 | US 100% |
| SDR | 4 | 6 | 8 | 10 | US 50%, LATAM 50% |
| CSM | 3 | 4 | 5 | 6 | US 80%, JP 20% |
| Finance | 3 | 3 | 4 | 4 | US 100% |

各 Role について Hire date を月次で記載 (Onboarding lag のために必要)。

### Step 2: FLC × Headcount

各 hire の FLC = Base × Loading factor。

```python
flc_per_role = {
    "Eng Senior US": 250000 * 1.4,    # = $350K
    "Eng Senior India": 90000 * 1.35, # = $121.5K
    "AE US": 130000 * 1.5,            # = $195K (commission 込)
    ...
}
```

月次コスト = $\sum_i \text{FLC}_i \times \text{Days}_i / 365$ (按分)。

### Step 3: Per-employee Programs

| 項目 | 単位 | 単価/年 |
|---|---|---|
| Tools (SaaS) | per HC | $3-7K |
| T&E (Travel & Entertainment) | per HC | $2-10K (役職依存) |
| Learning & Development | per HC | $1-3K |
| Office allocation | per HC | $5-15K (geography 依存) |

合計 per HC で年 $10-30K。

### Step 4: Direct Activity Cost

| 活動 | 費目 | Driver |
|---|---|---|
| Marketing programs | Paid ads, content, events | Revenue or CAC target |
| Hosting | AWS / GCP | Active users / queries / storage |
| 3rd party API | Twilio, Stripe | Transactions |
| Logistics | Shipping, fulfillment | Orders × per-order rate |
| Sales travel | T&E for AE | AE count × $5-15K |

各活動について **driver-based** にモデル化。

### Step 5: Allocations

| 項目 | 配賦先 | 配賦キー |
|---|---|---|
| Rent | All departments | HC ratio |
| IT | All departments | HC ratio |
| Finance/Legal | All departments | Revenue ratio or HC ratio |
| Internal events | All departments | HC ratio |

Department P/L 作成時のみ実施。Total P/L には不要。

### Step 6: Sanity vs Comparable

最後に business model peer (§5) と比較し、各項目の % of revenue が許容範囲か確認。
- 大幅外れ (例: G&A 20% で peer は 10-12%) は要根拠説明
- 経営計画として外れる場合は narrative (「先行投資」「IPO 準備」) を明記

---

## 15. Per-customer / Per-transaction cost

### 15.1 SaaS: COGS per Customer

$$
\text{COGS per customer} = \frac{\text{Total COGS}}{\text{Average active customers}}
$$

または customer segment 別:

$$
\text{COGS per Enterprise customer} = \text{Hosting}_E + \text{Support}_E + \text{CSM}_E + \text{Implementation}_E
$$

ベンチマーク (推定):
- SMB SaaS: $50-200/year/customer
- Mid-market: $500-3,000
- Enterprise: $5,000-50,000+

### 15.2 D2C: Cost per Order

$$
\text{Cost per Order} = \text{Pick & Pack} + \text{Outbound shipping} + \text{Returns share} + \text{CS share}
$$

ベンチマーク:
- Apparel: $8-20
- Beauty: $5-12
- CPG (subscription): $4-10
- Heavy / Furniture: $30-100

### 15.3 Fintech: Cost to Serve

$$
\text{Cost to Serve} = \text{KYC} + \text{Servicing} + \text{Fraud} + \text{Compliance share}
$$

| Customer type | Cost to Serve / year |
|---|---|
| Consumer banking | $30-80 |
| Lending (consumer) | $100-300 |
| SMB banking | $200-600 |
| Wealth (mass affluent) | $500-2,000 |
| Wealth (HNW) | $5,000-30,000 |

### 15.4 AI: Inference Cost per Request

$$
\text{Cost per request} = \text{Input tokens} \times P_{in} + \text{Output tokens} \times P_{out}
$$

(API 経由の場合)

または self-hosted:

$$
\text{Cost per request} = \text{GPU-seconds used} \times \text{GPU cost / hour} / 3600
$$

代表値 (2024 Q4):
- GPT-4o: input $2.50/1M tokens, output $10/1M tokens
- Claude 3.5 Sonnet: input $3/1M, output $15/1M
- Llama 3.1 70B (self-hosted, H100): input $0.15/1M, output $0.60/1M

1 リクエスト = avg 1,000 input + 500 output tokens 想定:
- GPT-4o: $0.0025 + $0.005 = $0.0075
- 1 ユーザ月 100 リクエスト → $0.75/月
- ARPU $20/月の SaaS なら compute = 3.75% (allowable)

### 15.5 Scale で逓減するか?

Per-customer/transaction cost は理論的に scale で逓減 (固定費分散) するが、実際は:
- SaaS: 逓減する (COGS の 70% が hosting で variable だが scale 効果あり)
- D2C: 物流の規模化で per-order cost は -20-40% 削減可能 (FBA 自動化、cluster warehouses)
- Fintech: KYC 自動化で per-customer servicing が逓減
- AI: モデル improvement で逓減 (GPT-4 → GPT-4o で 50% 値下げ)、ただし用途多様化で per-user requests 増加で相殺

---

## 16. AI / Compute cost 構造

### 16.1 Training cost vs Inference cost

| 区分 | 性質 | 会計処理 (現状) |
|---|---|---|
| Training cost | 一時的、大規模 | Expense or Capitalize 議論あり (実務は expense 多数) |
| Fine-tuning cost | Per-customer (or per-product) | COGS or R&D |
| Inference cost | Continuous, usage 比例 | COGS |

#### Training cost の例 (推定)
- GPT-4 training: ~$100M
- Claude 3 Opus: 数十-100M USD レンジ (推定)
- Llama 3 70B: ~$20-30M
- 中小 fine-tune: $10K-1M

会計処理 (FASB 議論中、2024-2025):
- 即時 expense (現行多数): R&D 計上
- Capitalize + amortize (Useful life 1-3 年): 一部企業が試行
- 最終ガイダンスは 2025-2026 に出る見込み

### 16.2 Inference cost の構造

$$
\text{Inference cost / month} = \text{Active users} \times \text{Requests/user} \times \text{Tokens/request} \times \text{Token price}
$$

#### 主要モデル価格 (per 1M tokens, 2024 Q4)

| Model | Input | Output | 用途 |
|---|---|---|---|
| GPT-4o | $2.50 | $10.00 | 汎用、高品質 |
| GPT-4o-mini | $0.15 | $0.60 | 軽量タスク |
| Claude 3.5 Sonnet | $3.00 | $15.00 | コード、分析 |
| Claude 3.5 Haiku | $0.80 | $4.00 | 軽量・高速 |
| Gemini 1.5 Pro | $1.25 | $5.00 | 長コンテキスト |
| Llama 3.1 405B (Together) | $5.00 | $5.00 | Open weight |
| Llama 3.1 70B (Together) | $0.88 | $0.88 | Open weight 軽量 |
| DeepSeek V3 | $0.27 | $1.10 | 低価格 |

### 16.3 GPU pricing (Hardware)

| GPU | 価格 (USD) | レンタル ($/hour) | 用途 |
|---|---|---|---|
| H100 80GB SXM5 | $30K-40K | $2-4 (cloud) | Training, large inference |
| H200 | $35K-45K | $3-5 | Training, large inference |
| B100 / B200 | $40K-50K | (限定供給) | 次世代 |
| A100 80GB | $15K-20K | $1.5-2.5 | Training (旧)、inference |
| L40S | $8-10K | $0.8-1.5 | Inference |
| RTX 4090 | $1.6-2K | $0.4-0.6 | Lab, light inference |

GPU 調達 lead time (2024-2025): H100 3-6 ヶ月、B100 12+ ヶ月。

### 16.4 LLM Cost-to-Serve の数式展開

例: Vertical AI SaaS (法律向け)

```
ARPU                     $200/月
Active queries/user/月    300 queries
Avg input tokens/query    3,000 (RAG context)
Avg output tokens/query    600

Token consumption:
  Input: 300 × 3,000 = 900K tokens/month
  Output: 300 × 600 = 180K tokens/month

API cost (Claude 3.5 Sonnet):
  Input: 900K × $3/1M = $2.70
  Output: 180K × $15/1M = $2.70
  Total: $5.40/user/month

Compute cost as % of ARPU = $5.40 / $200 = 2.7%
```

これは healthy。しかし RAG context が 30K tokens、queries が 1,000/user の場合:
```
Input: 1,000 × 30,000 = 30M tokens
Output: 1,000 × 1,500 = 1.5M tokens
Cost: 30 × $3 + 1.5 × $15 = $90 + $22.5 = $112.5/user/month
% of ARPU: 56% (危険水準)
```

### 16.5 Margin Compression 環境 (API 価格戦争)

2023-2024 の price war:
- GPT-4 ($30/1M input) → GPT-4 Turbo ($10) → GPT-4o ($2.50) で **12 ヶ月で -92%**
- Claude 3 Opus ($15/1M) → Claude 3.5 Sonnet ($3) で **6 ヶ月で -80%**
- DeepSeek V3 (2024 Q4) で $0.27/1M (Anthropic Sonnet の 11 倍安い)

含意:
- AI SaaS の compute COGS は **時間が味方** (Gross margin 改善)
- ただし vendor lock-in リスク (OpenAI/Anthropic/Google 三つ巴)
- Self-hosted (Llama, DeepSeek) で arbitrage 戦略は有効だが、運用コスト + 性能差を考慮

### 16.6 AI Gross Margin の構造的低さ — 解消シナリオ

a16z "The Cost of Compute" 2024 の主張: 
- 短期 (12-24 ヶ月): AI スタートアップの GM は 30-50% で SaaS 標準 (75-80%) より低い
- 中期 (3-5 年): モデル価格低下で GM 60-70% 達成可能
- 長期: GM 75-80% に収斂 (SaaS と同等)

逆論 (Sequoia "AI's $200B Question" 2023):
- Compute 投資 ($200B+ in 2023-2024) と AI 売上 ($30-50B 推定) のギャップ
- 一部スタートアップは margin 改善の前にキャッシュ枯渇するリスク

実務: 2024-2025 時点では **2 シナリオ (Compute 価格半減 / 横這い) でモデル化**、bear case で runway 検証。

---

## 17. 数値例 5 ケース

### 17.1 Case 1: SaaS Series B コスト構造分解

**前提**:
- ARR $10.0M (年初 $7.5M、年末 $12.5M、avg $10M)
- New ARR $4.0M、Expansion ARR $1.5M、Churn $1.0M
- Gross margin 78% (COGS $2.2M)
- S&M 35% of revenue ($3.5M)

**コスト分解 (annual, $M)**:

| 項目 | 金額 | % of revenue | 内訳 |
|---|---|---|---|
| Revenue | 10.0 | 100% | |
| **COGS** | **2.2** | **22%** | |
| Hosting (AWS) | 0.7 | 7% | EC2 + S3 + RDS |
| 3rd party API | 0.3 | 3% | Twilio, Sendgrid, Auth0 |
| 1st-line support | 0.5 | 5% | 4 名 × $90K + tooling |
| CSM (COGS portion) | 0.7 | 7% | 5 名 × $130K (40% allocation) |
| **Gross Profit** | **7.8** | **78%** | |
| **S&M** | **3.5** | **35%** | |
| AE (5 人 × $200K FLC) | 1.0 | 10% | $130K base + commission + benefit |
| SDR (4 人 × $90K FLC) | 0.36 | 3.6% | |
| Sales engineer (1 人) | 0.18 | 1.8% | |
| Marketing programs | 0.85 | 8.5% | Paid + content |
| Events | 0.30 | 3.0% | Conference 出展 3 回 |
| Marketing HC (4 人) | 0.50 | 5.0% | |
| Sales ops + tooling | 0.31 | 3.1% | Salesforce, Outreach, etc. |
| **R&D** | **2.5** | **25%** | |
| Engineer (12 人 × FLC avg $200K) | 2.4 | 24% | |
| Tooling (GitHub, AWS dev) | 0.10 | 1% | |
| **G&A** | **1.5** | **15%** | |
| Finance (CFO + 2) | 0.45 | 4.5% | |
| Legal (GC contractor) | 0.15 | 1.5% | |
| HR (1 人 + tooling) | 0.18 | 1.8% | |
| Office (NYC 30 名 capacity) | 0.45 | 4.5% | |
| Insurance, audit, etc. | 0.27 | 2.7% | |
| **Operating Income** | **0.3** | **3%** | |

**評価**:
- Gross margin 78% — top quartile
- S&M 35% — median (新規獲得急拡大中)
- R&D 25% — median
- G&A 15% — high (Series B 段階で良くある)
- Operating margin +3% — Bessemer median (-10%) より優秀
- Magic Number = ($5.5M new+expansion - 0) / $3.5M = 1.57 — efficient

**改善提案**:
- G&A は Series C で 12% を目指す (規模効果)
- S&M efficiency 改善 (CAC payback 短縮) で Operating margin +5pt
- Engineering の India offshore 比率を 20% → 35% で R&D の絶対額抑制

---

### 17.2 Case 2: D2C ¥5B 売上の Tier 1/2/3 contribution margin

**前提 (アパレル D2C)**:
- 年商 ¥5,000M (= $33M)
- 年間注文数 500,000 件
- 平均注文額 ¥10,000 (1 注文 1 商品)

**Contribution Margin 分解 (¥ per order, 全社平均)**:

| 項目 | 金額 (¥) | % | 説明 |
|---|---|---|---|
| ASP | 10,000 | 100% | |
| BOM (商品原価) | 2,800 | 28% | アパレル 28%、自社製造工場 |
| Packaging | 350 | 3.5% | 一次 + ギフト |
| Inbound freight | 150 | 1.5% | 工場 → 国内倉庫 |
| **CM1 (Tier 1)** | **6,700** | **67%** | |
| Outbound fulfillment | 800 | 8.0% | ピック + 梱包 + 配送 |
| Payment processing | 280 | 2.8% | クレカ + コンビニ |
| Returns provision | 1,500 | 15.0% | 返品率 25%、戻り商品の半分は再販可能 |
| **CM2 (Tier 2)** | **4,120** | **41.2%** | |
| Variable marketing (CAC normalized) | 2,500 | 25% | New + repeat blend |
| **CM3 (Tier 3)** | **1,620** | **16.2%** | |
| Fixed OpEx allocation (per order) | 1,200 | 12% | HC, office, IT, etc. |
| **Order-level Operating Profit** | **420** | **4.2%** | |

**P/L 全社換算**:

| 項目 | ¥M | % of revenue |
|---|---|---|
| Revenue | 5,000 | 100% |
| COGS (BOM + Pack + Inbound) | 1,650 | 33% |
| **Gross Profit** | **3,350** | **67%** |
| Logistics + Returns | 1,150 | 23% |
| Payment processing | 140 | 2.8% |
| **CM2 P/L** | **2,060** | **41.2%** |
| Marketing | 1,250 | 25% |
| **CM3 P/L** | **810** | **16.2%** |
| Fixed OpEx | 600 | 12% |
| **Operating Income** | **210** | **4.2%** |

**評価**:
- Gross margin 67% — D2C 良
- 返品率 25% → CM2 で 15pt 食う (改善余地大)
- Variable marketing 25% — D2C 中央値
- CM3 16% — 健全 (新規広告打ってもプラス)
- Operating margin 4.2% — D2C median 0% よりも上

**改善提案**:
- 返品率を AI フィッティング技術で 25% → 18% に → ¥350M (7%) の利益増
- Repeat purchase 促進で CAC blended 25% → 20% → ¥250M 増
- Operating margin 目標 10%+ (D2C 良-優秀ライン)

---

### 17.3 Case 3: Hardware の BOM 構造 (¥30K BOM / ¥80K ASP / 12% yield loss)

**前提 (IoT デバイス スタートアップ)**:
- ASP ¥80,000 (B2C、家電量販店経由)
- 製造ロット 50,000 台/年
- BOM 設計値 ¥30,000

**Yield loss を考慮した実質 BOM**:

$$
\text{Effective BOM} = \frac{\text{Designed BOM}}{1 - \text{Yield loss rate}}
$$

$$
= \frac{30,000}{1 - 0.12} = \frac{30,000}{0.88} = 34,091
$$

**COGS 分解 (per unit)**:

| 項目 | 金額 (¥) | % of ASP | 説明 |
|---|---|---|---|
| ASP (sell-in to retailer) | 80,000 | 100% | (retailer は ¥110K で販売、margin ¥30K) |
| Effective BOM | 34,091 | 42.6% | Yield loss 込み |
| Manufacturing labor (OEM) | 5,000 | 6.3% | 中国 OEM、人件費 |
| Inbound freight (Shenzhen → 横浜) | 2,500 | 3.1% | 海上輸送 |
| Packaging | 1,200 | 1.5% | リテールパッケージ |
| Outbound freight (DC → retailer) | 1,800 | 2.3% | 国内物流 |
| Tooling 償却 (¥30M / 50K units / 3年) | 200 | 0.3% | 金型 |
| Warranty provision (1 年保証、不良率 3%) | 1,500 | 1.9% | |
| **Total COGS** | **46,291** | **57.9%** | |
| **Gross Profit** | **33,709** | **42.1%** | |

**P/L 全社換算 (年商 ¥4B = 50K × ¥80K)**:

| 項目 | ¥M | % |
|---|---|---|
| Revenue | 4,000 | 100% |
| COGS | 2,315 | 57.9% |
| **Gross Profit** | **1,685** | **42.1%** |
| S&M | 600 | 15% |
| R&D | 480 | 12% |
| G&A | 320 | 8% |
| **Operating Income** | **285** | **7.1%** |

**評価**:
- Gross margin 42% — Hardware 良 (中央値 30%)
- Yield 12% は scale 初期の典型値 (成熟後 3-5% を目指す)
- Operating margin 7% — Hardware 中央値 -5% より上

**Yield 改善シナリオ**:

| Yield loss | Effective BOM | GM | Operating margin |
|---|---|---|---|
| 12% (現状) | ¥34,091 | 42.1% | 7.1% |
| 8% (1 年後) | ¥32,609 | 44.2% | 9.2% |
| 5% (2 年後) | ¥31,579 | 45.5% | 10.5% |
| 3% (成熟) | ¥30,928 | 46.4% | 11.4% |

Yield 改善で Operating margin +4.3pt の余地。

---

### 17.4 Case 4: Fintech CECL Provisioning (Loan book ¥10B / 3% expected loss / vintage)

**前提 (消費者向け融資 fintech)**:
- 期末 Loan book 残高 ¥10,000M
- 全体期待損失率 (lifetime ECL) 3%
- 平均融資期間 24 ヶ月
- Vintage 別 (origination 月別) 管理

**CECL 引当の式**:

$$
\text{ECL Reserve} = \sum_{v \in \text{Vintages}} \text{Outstanding}_v \times \text{Lifetime PD}_v \times \text{LGD}_v \times (1 - \text{Recovery rate})
$$

**Vintage 別データ (簡略)**:

| Origination Vintage | Outstanding (¥M) | Maturity (months) | Lifetime PD | LGD | ECL (¥M) |
|---|---|---|---|---|---|
| 2023 H1 | 1,500 | 6 残 | 4% | 80% | 48 |
| 2023 H2 | 2,000 | 12 残 | 3.5% | 80% | 56 |
| 2024 H1 | 2,500 | 18 残 | 3% | 80% | 60 |
| 2024 H2 | 4,000 | 24 残 | 2.8% | 80% | 90 |
| **合計** | **10,000** | | | | **254** |

ECL Reserve / Loan book = 2.54%

**P/L impact (年間)**:

| 項目 | ¥M | 説明 |
|---|---|---|
| Interest revenue (avg book ¥9B × 18% APR) | 1,620 | |
| Interest expense (Cost of funds ¥9B × 5%) | -450 | |
| **Net Interest Income** | **1,170** | |
| Loan loss provision (期中の change in ECL) | -300 | New origination + book aging |
| **NII after provisions** | **870** | |
| Fee income (late fee, etc.) | 80 | |
| Operating expense (S&M, R&D, G&A) | -650 | |
| **Pretax income** | **300** | |

**シナリオ分析 (景気悪化で PD 2x)**:

| シナリオ | Lifetime PD | ECL Reserve | NII after prov | Pretax |
|---|---|---|---|---|
| Base (現状) | 3% | 254 | 870 | 300 |
| Mild downturn | 4.5% | 381 | 743 | 173 |
| Severe (Subprime) | 7% | 593 | 531 | -39 |
| Catastrophic (COVID-like) | 12% | 1,016 | 108 | -462 |

**Vintage 管理の重要性**: 2024 H2 origination の credit quality は前 vintage より良いか悪いか? Underwriting tightening の効果はあるか? Vintage cohort で見ないと分からない。

---

### 17.5 Case 5: AI スタートアップ Compute Cost (50% → 20% scale)

**前提 (Vertical AI、法律向け SaaS)**:
- ARPU $500/月 (mid-market law firm 用、3-10 ユーザの seat)
- Active users 1,000 → 10,000 (10x scale)
- LLM API 価格は時間とともに低下

**Year 1 (1,000 users)**:

```
Active queries/user/月    400
Avg input tokens/query    8,000 (RAG context with case law)
Avg output tokens/query   1,500

Per-user monthly:
  Input: 400 × 8,000 = 3.2M tokens
  Output: 400 × 1,500 = 0.6M tokens

API cost (Claude 3.5 Sonnet, 2024 Q1 pricing):
  Input: 3.2M × $3/1M = $9.60
  Output: 0.6M × $15/1M = $9.00
  Total: $18.60/user/month

Compute cost (1,000 users) = $18,600/月 = $223,200/年

Revenue (1,000 users × $500 × 12) = $6,000,000
Compute as % of revenue = 3.7%
```

これは healthy だが、ARPU が低い場合は危険:
```
ARPU $50/月 の場合:
  Compute / ARPU = $18.60 / $50 = 37% (危険)
```

**Year 3 (10,000 users) — Optimistic scenario**:

```
モデル: Haiku に shift + prompt optimization で input tokens -40%
Avg input tokens/query    4,800 (caching + tighter RAG)
Avg output tokens/query   1,200

API cost (Claude 3.5 Haiku, 2026 推定 $0.50/1M input, $2.50/1M output):
  Per-user monthly:
    Input: 400 × 4,800 = 1.92M tokens
    Output: 400 × 1,200 = 0.48M tokens
  Cost:
    Input: 1.92M × $0.50/1M = $0.96
    Output: 0.48M × $2.50/1M = $1.20
    Total: $2.16/user/month

Compute cost (10,000 users) = $21,600/月 = $259,200/年
Revenue (10,000 × $500 × 12) = $60,000,000
Compute as % of revenue = 0.43%
```

Compute % of revenue は 3.7% → 0.43% へ **8.6 倍効率化**。これがモデル価格低下 + scale + optimization の合成効果。

**Year 3 (10,000 users) — Pessimistic scenario**:

```
モデル価格は横這い、input tokens 増 (より複雑な query):
  Input tokens/query: 12,000
  Output tokens/query: 2,500
  
Cost (Claude 3.5 Sonnet 価格据え置き):
  Input: 4.8M × $3/1M = $14.40
  Output: 1.0M × $15/1M = $15.00
  Total: $29.40/user/month

Compute cost (10,000 users) = $294,000/月 = $3,528,000/年
Revenue ($60M)
Compute as % of revenue = 5.9%
```

依然 manageable だが、ARPU が下がっていればさらに危険。

**結論**: AI スタートアップは以下 3 戦略の組合せで margin 確保:
1. Model arbitrage (Haiku/Mini への切替)
2. Prompt optimization (caching, tighter RAG)
3. ARPU 上昇 (機能追加、enterprise tier)

---

## 18. Cost DD チェックリスト 50 項目

DD (Due Diligence) で必ず確認すべき項目。投資家向け / アクワイヤラー向け / 監査向けで使用。

### A. コスト分類の正確性 (10 項目)

1. □ COGS と OpEx の境界が GAAP / IFRS / J-GAAP に従っているか
2. □ Customer Success が COGS / S&M / G&A の正しい区分に置かれているか
3. □ Hosting cost が COGS に計上されているか (R&D ではないか)
4. □ Implementation/PS revenue に対応する cost が COGS にあるか
5. □ Capitalize した R&D の amortization が適切に R&D にカウントされているか
6. □ SBC が S&M / R&D / G&A 各項目に按分されているか (一括処理ではないか)
7. □ Allocation キー (HC ratio / revenue ratio) が文書化されているか
8. □ Restructuring / one-time cost と recurring cost が分離されているか
9. □ Foreign exchange impact がコスト分析で adjusted されているか
10. □ Discontinued operations が separate に表示されているか

### B. 固定費 vs 変動費 (5 項目)

11. □ Marketing が真に variable な部分と fixed な部分に分解されているか
12. □ Step function コスト (office, AWS RI など) が認識されているか
13. □ Headcount の固定費的性格が forecast に反映されているか
14. □ Commission 等真の variable cost の式が明確か
15. □ DOL (Degree of Operating Leverage) が計算されているか

### C. Headcount (10 項目)

16. □ Hiring plan が role × stage × geography で展開されているか
17. □ FLC (Fully Loaded Cost) の loading factor が業界標準内か
18. □ Onboarding ramp が productivity 計算に反映されているか
19. □ Attrition (年率) が hiring plan に gross-up されているか
20. □ Recruiter / agency fee が含まれているか
21. □ Equity compensation の cash equivalent が監視されているか
22. □ Offshore vs onshore の compensation gap が妥当か
23. □ Span of control (manager 比率) が業界標準か
24. □ Sales rep の quota attainment 仮定が realistic か (50-70% が現実)
25. □ Engineer per PM, Designer per Engineer 比率が機能しているか

### D. Vendor / Software cost (5 項目)

26. □ Top 10 vendor がリストされ年間 spend が把握されているか
27. □ Auto-renewal 契約の Identification ができているか
28. □ Multi-year discount が活用されているか
29. □ SaaS tooling の重複 (Notion + Confluence など) がないか
30. □ Vendor contract の termination clause が把握されているか

### E. Cloud / Compute (5 項目)

31. □ Cloud spend (AWS/GCP/Azure) が monthly で監視されているか
32. □ Reserved Instance / Savings Plan の活用率が分かるか
33. □ Cost per active user / per query が time series で取れているか
34. □ AI training / inference cost が分離されているか
35. □ Multi-cloud arbitrage の検討余地が評価されているか

### F. Customer-level economics (5 項目)

36. □ COGS per customer (segment 別) が計算されているか
37. □ CAC, LTV, LTV/CAC が定義通りに計算されているか
38. □ Cohort-based gross margin が安定しているか
39. □ Top 10 customer の concentration risk が把握されているか
40. □ Loss-leader 顧客 (negative gross margin) がいないか

### G. Capitalize / Tax (5 項目)

41. □ R&D capitalize 比率が peer 比で妥当か
42. □ Capitalize 判定の internal control が文書化されているか
43. □ R&D Tax Credit (試験研究費控除) が claim されているか
44. □ Transfer pricing (海外子会社) が arm's length か
45. □ Deferred tax asset の realizability が評価されているか

### H. SBC / Equity (5 項目)

46. □ SBC % of revenue が業界 peer 比で妥当か
47. □ Vesting schedule が standard (4 年 + 1 年 cliff) か
48. □ Net dilution rate (年率) が長期投資家視点で許容範囲か
49. □ Top 10 SBC recipients (executive) の grant が disclosed か
50. □ Performance-based vesting (PSU) があれば KPI が明確か

---

## 19. 出典一覧

### Bessemer Venture Partners
- "State of the Cloud 2024" — https://www.bvp.com/atlas/state-of-the-cloud-2024
- "Cloud Index" (公開企業ベンチマーク) — https://cloudindex.bvp.com/
- "Hardware Index" — https://www.bvp.com/

### OpenView Partners (現 G2)
- "SaaS Benchmarks 2024" — https://www.openviewpartners.com/saas-benchmarks/
- "SaaS Pricing Strategy"

### KeyBanc Capital Markets
- "Annual SaaS Survey 2024" (Public + private SaaS のコスト構造)
- 100+ pages、毎年 9 月発行

### a16z (Andreessen Horowitz)
- "Marketplace 100" — https://a16z.com/marketplace-100/
- "The Cost of Compute" 2024 — https://a16z.com/the-cost-of-compute-a-7-trillion-dollar-race/
- "16 Metrics for Marketplaces"
- "16 More Metrics" series

### Sequoia Capital
- "AI's $200B Question" 2023 — David Cahn
- "Generative AI's Act Two" 2023

### Aswath Damodaran (NYU Stern)
- Cost of capital database (国別 / 業界別) — http://pages.stern.nyu.edu/~adamodar/
- "Stock-based Compensation: Time to End the Charade" 2023
- Operating margin database (業界別、年次更新)

### McKinsey & Company
- "The State of Operations" annual
- "Cost Excellence" practice publications

### BCG (Boston Consulting Group)
- "Experience Curves" Bruce Henderson 1968 (オリジナル)
- Sourcing & Operations practice

### KPMG / PwC / EY / Deloitte
- "SaaS Industry Survey"
- "Tech Industry Outlook"

### 個別企業 10-K / 有価証券報告書
- Snowflake 10-K (SBC)
- Datadog 10-K (gross margin)
- Affirm 10-K (CECL)
- Apple 10-K (Hardware GM)

### 補助データソース
- Levels.fyi (Compensation)
- Pave Tech Compensation Survey
- Carta Equity Reports
- LinkedIn Talent Insights
- Glassdoor

### 学術 / 標準
- ASC 350-40 (FASB) — 内部利用ソフトウェア
- ASC 985-20 (FASB) — 販売目的ソフトウェア
- ASC 326 (FASB) — CECL
- ASC 718 (FASB) — Stock Compensation
- IAS 38 (IFRS) — Intangible Assets
- IFRS 2 — Share-based Payment
- IFRS 9 — Financial Instruments (ECL)
- 企業会計審議会「研究開発費等に係る会計基準」(J-GAAP)
- 法人税法 42 条 (試験研究費控除)
- IRC Section 41 (US R&D Tax Credit)

### 書籍
- Eliyahu M. Goldratt "The Goal" — TOC (制約理論)
- Geoffrey Moore "Crossing the Chasm" — Cost ramp by stage
- Frederick Brooks "The Mythical Man-Month" — Diseconomies of scale
- Tom Tunguz, David Sacks ら SaaS thought leaders blog

---

(本ドキュメント終わり。改訂は references の他章 (02 SaaS metrics, 03 business models, 06 three statement) と相互参照しながら行う。)
