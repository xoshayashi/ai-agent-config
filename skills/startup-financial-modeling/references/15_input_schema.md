---
name: input_schema
description: scripts/build_model.py がユーザー入力から xlsx を生成する際の正本入力スキーマ。YAML / JSON Schema / Pydantic 三本立てで定義。SKILL.md dispatch table の "業態 × stage で何を読むか" entry の補完 reference として §11.2 を、Mode 選択質問は §1 を参照。
type: reference
priority: P1
related: [_terminology, _master_decision_tree, 03_business_models, 06_three_statement, 16_cost_structure]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: build_model.py 入力 schema は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §0.1`](_master_decision_tree.md) (5 entry point) / SKILL.md basic workflow §1 (Mode 選択) から参照
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (schema validation 通過) を必ず実行
- **関連 reference**: `_master_decision_tree §E` (業態 routing) / `03_business_models` (業態別 metric) / `06_three_statement` (三表 driver) / `16_cost_structure` (コスト driver)

# 15. Input Schema 正本 (User Input Schema for build_model.py)

> 本ドキュメントは `scripts/build_model.py` および全 builder script (cap_table_builder / valuation_builder / three_statement_builder / debt_builder / consolidation_builder) が **ユーザー入力から xlsx を生成する際の正本入力スキーマ** を定義する。F-C-004 (audit F: 唯一の Critical) を解消するため、reference 群 (00-14) の field 定義を集約し、build phase 着手前に YAML / JSON Schema として固定する。
>
> 用語注: 本書では「Operating System」「OS」表記を避け、「Operating model」「経営の仕組み」と表現する (個人ルール、`MEMORY.md` 参照)。
>
> **正本主義 (SSoT)**: field 名・enum 値・default 値で他 reference (00-14) と矛盾する場合は **本書を canonical** とし、参照元 reference との対応を `source ref` 列に明示する。terminology / color / 命名規則は `_terminology.md` を上位 SSoT として尊重する。
>
> 数値 default はすべて出典明示。同一 field で複数ソースが矛盾する場合は両方併記し、推奨値は中央値ではなく **保守側 (悲観側)** を採用する。

---

## 目次

1. [前提と入力モード分類](#1-前提と入力モード分類)
2. [業態判定 (Business Model Detection)](#2-業態判定-business-model-detection)
3. [Stage 判定 (Funding Stage Detection)](#3-stage-判定-funding-stage-detection)
4. [共通 Input Field (全業態共通)](#4-共通-input-field-全業態共通)
5. [業態別 Input Field (主要 5 業態)](#5-業態別-input-field-主要-5-業態)
6. [Cap Table Input](#6-cap-table-input)
7. [Debt Input](#7-debt-input)
8. [Validation Rules](#8-validation-rules)
9. [Default 値テーブル (業態 × Stage)](#9-default-値テーブル-業態--stage)
10. [Schema 完全形 (YAML / JSON Schema / Pydantic)](#10-schema-完全形-yaml--json-schema--pydantic)
11. [Routing 表 (Input → Reference Loading)](#11-routing-表-input--reference-loading)
12. [Error Messages (i18n: 日本語)](#12-error-messages-i18n-日本語)
13. [Example Input Sets](#13-example-input-sets)
14. [Build_model.py 統合手順](#14-build_modelpy-統合手順)

---

## 1. 前提と入力モード分類

### 1.1 設計思想

`build_model.py` は **3 段階の入力深度** をサポートする。早期段階のスタートアップでは詳細データが揃わないため、Quick mode で **default 値 + 業態 × Stage benchmark から逆算** する経路を残す。逆に Series B 以降は Comprehensive mode で実数値中心に組む。

**3 段階の構成**:

| Mode | Field 数 | 想定読者 | xlsx 出力規模 | 完了所要時間 (ヒアリング込み) |
|---|---|---|---|---|
| Quick | 10-15 | Founder 自己診断、Pitch 前検算 | 6 sheet, ~200 行 | 15-30 分 |
| Standard | 30-50 | Seed-Series A、IM/CIM 用 | 10-12 sheet, ~600 行 | 1-2 時間 |
| Comprehensive | 100-200 | Series B 以降、IPO/M&A 準備 | 15-20 sheet, ~2,000 行 | 半日-1 日 |

> 出典: `01a §3.2` (Modeling discipline by stage)、`14 §2` (IPO 準備時のデータ深度)、`08 §3.1` (Stage 別 ARR table)。

### 1.2 Mode 選択ロジック

`build_model.py` 開始時に以下の 1 問をユーザーに提示し、回答に応じて Mode を自動決定する。明示的に Mode を指定された場合は優先する。

```yaml
mode_selection:
  question: "目的を 1 つ選択してください"
  options:
    - id: pitch_quick_check
      label: "ピッチ用の概算 (15 分)"
      mode: quick
    - id: ic_memo_seed_seriesA
      label: "Seed/Series A の IC memo / IM (1-2 時間)"
      mode: standard
    - id: ipo_ma_due_diligence
      label: "Series B 以降 / IPO・M&A 準備 (半日-1 日)"
      mode: comprehensive
  default: standard
```

Mode が決まると **必須 field 集合** と **optional field 集合** が確定する。Quick で省略された field は §9 の default 値テーブル (業態 × Stage) から自動充填する。

### 1.3 入力チャンネル

入力は以下の 3 経路をサポート:

| 経路 | 用途 | 形式 |
|---|---|---|
| 対話的 (CLI) | 単発実行、ヒアリング | Click prompt / Inquirer.py |
| YAML/JSON 一括 | 再現性、CI/CD | `inputs/{company}.yaml` |
| Excel template | 顧客自己入力 | `templates/input_template.xlsx` (Hard input cell only) |

**正本**: 内部表現は **YAML 1 経路に正規化** し、対話/Excel 入力は YAML に変換してから validate → builder に渡す。これにより validate / fixture / regression test が単一 schema で済む。

### 1.4 Field 命名規則

- **snake_case** に統一 (Python pydantic 互換)
- 通貨は **末尾 `_jpy` / `_usd` / `_local`** で明示 (例: `arr_jpy`, `cac_usd`)
- 比率は **末尾 `_pct`** (例: `gross_margin_pct`、0-100 の数値、0-1 ではない)
- 期間は **末尾 `_months` / `_years`** (例: `cac_payback_months`)
- Boolean は **`is_` / `has_` プレフィックス** (例: `is_consolidated`, `has_safe_outstanding`)
- 配列は **複数形** (例: `safe_notes`, `debt_facilities`)

> 出典: `_terminology.md §4` (命名規則)、`00 付録 A` (sheet naming)、`10 §2` (modeling craft 命名規則)。

---

## 2. 業態判定 (Business Model Detection)

### 2.1 Enum 定義

**Field**: `business_model`
**Type**: enum (string)
**Required**: yes (全 Mode で必須)

```yaml
business_model:
  enum:
    - saas               # B2B SaaS / Subscription software
    - marketplace        # Two-sided marketplace, GMV ベース
    - d2c_ecommerce      # D2C / EC, AOV × repeat ベース
    - fintech            # Lending / Payments / Insurance / Wealth
    - hardware_iot       # Hardware + recurring IoT subscription
    - bio_pharma         # 創薬 / 治験 / Royalty
    - media_content      # Ad-supported, Subscription content
    - b2b_services       # Consulting, BPO, Agency
    - manufacturing      # 製造業 (B2B 受注生産含む)
    - real_estate        # 不動産開発 / REIT / PropTech
    - ai_foundation_model  # 大規模 AI モデル開発 (Foundation 層)
```

> 出典: `03 §1` (業態 11 分類)、`03 §11` (業態判定フローチャート)、`08 §2.3` (業態別投資テーゼ)。

### 2.2 自動判定フローチャート (decision tree)

ユーザー入力が曖昧な場合、以下の 4 質問で判定する。`03 §11` のフローチャートを 1:1 で機械可読化したもの。

```yaml
business_model_decision_tree:
  - q1: "収益の主要源は?"
    options:
      subscription_recurring:
        - q2_subscription: "顧客は誰?"
          options:
            business: saas
            consumer: media_content   # 個人向け subscription (Netflix 型)
      transaction_fee:
        - q2_transaction: "自社が在庫を持つか?"
          options:
            no_inventory: marketplace        # GMV × take rate
            yes_inventory: d2c_ecommerce     # AOV × repeat
            financial_product: fintech       # NIM or take rate
      project_fee:
        b2b_services
      product_sale:
        - q2_product: "ハードウェアか?"
          options:
            yes_hw: hardware_iot
            no_software: saas      # one-time license は稀、ほぼ subscription に流れる
            pharma: bio_pharma
            heavy_industry: manufacturing
      ad_revenue:
        media_content
      rental_lease:
        real_estate
      compute_api_token:
        ai_foundation_model
```

**早見表 (簡易判定)**:

| 主要 KPI | 推奨 enum |
|---|---|
| ARR / MRR / NRR が中心 | `saas` |
| GMV / Take rate が中心 | `marketplace` |
| AOV / 購入頻度 / Cohort retention が中心 | `d2c_ecommerce` |
| TPV (Total Payment Volume) / NPL / Loss rate | `fintech` |
| BOM / Inventory turns / Margin が中心 | `hardware_iot` or `manufacturing` |
| Phase II/III 確率 / Royalty が中心 | `bio_pharma` |
| ARPU × MAU × Ad CPM | `media_content` (ad-supported) |
| Project margin / Utilization rate | `b2b_services` |
| Cap rate / NOI / LTV (Loan-to-value) | `real_estate` |
| Token throughput / Cost per training run | `ai_foundation_model` |

> 出典: `03 §11` 早見表、`08 §3.2` 業態別 KPI、`02 §2-§5` SaaS metrics。

### 2.3 Hybrid / 複数業態の処理

- 主業態 (`business_model`) + 副業態 (`secondary_business_model`, optional, enum) で表現
- **収益の 80% 以上を占める業態** を主業態とする
- 副業態が >20% の場合、`segment_revenue_split_pct` (各 segment の比率) を要求し、segment 別に売上を組む
- 例: SaaS + Services の Hybrid → `saas` 主、`b2b_services` 副、segment split 75/25

> 出典: `03 §10` (Hybrid モデル)、`13a §3` (segment 連結)。

### 2.4 業態が未確定 / Pre-revenue の場合

- 売上ゼロでも `business_model` は **必須** とする (今後の収益モデル仮説として固定)
- `is_pre_revenue: true` を別 field で立て、Stage 判定 (§3) で `pre_revenue` を強制する
- Default 値の参照先は「業態 × `pre_revenue` 行」(§9) を使う

---

## 3. Stage 判定 (Funding Stage Detection)

### 3.1 Enum 定義

**Field**: `funding_stage`
**Type**: enum (string)
**Required**: yes

```yaml
funding_stage:
  enum:
    - pre_revenue     # 売上ゼロ、Seed 前後
    - early_revenue   # 売上 0 < ARR < $1M、Seed-pre Series A
    - series_a        # ARR $1-5M、Series A
    - series_b        # ARR $5-20M、Series B
    - series_c        # ARR $20-50M、Series C / D
    - pre_ipo         # ARR $50M+、IPO 申請準備
    - public          # 上場後 (参考、本 Skill 範囲外だが TS 比較用に保持)
```

> 出典: `08 §3.1` Stage 別 ARR table (4 列マトリクス)、`14 §2` IPO 準備。

### 3.2 自動判定 logic (auto-judge)

`scripts/build_model.py` は以下を **優先順位** で判定:

```python
# Pseudocode (実装は build_model.py § stage_detection を参照)
def detect_stage(inputs: dict) -> str:
    # 1. ユーザー manual override が最優先
    if inputs.get("funding_stage_manual"):
        return inputs["funding_stage_manual"]

    arr = inputs.get("arr_jpy", 0)  # JPY 想定
    revenue = inputs.get("revenue_ttm_jpy", 0)
    employees = inputs.get("employees", 0)

    # 2. ARR 基準 (SaaS) または revenue 基準 (非 SaaS)
    metric = arr if inputs["business_model"] == "saas" else revenue
    metric_usd = metric / inputs.get("fx_jpy_per_usd", 150.0)

    # 3. しきい値 (USD ベース、08 §3.1 と同期)
    if metric_usd == 0:
        return "pre_revenue"
    elif metric_usd < 1_000_000:
        return "early_revenue"
    elif metric_usd < 5_000_000:
        return "series_a"
    elif metric_usd < 20_000_000:
        return "series_b"
    elif metric_usd < 50_000_000:
        return "series_c"
    else:
        return "pre_ipo"

    # 4. 矛盾検知: employees と ARR が不整合の場合 warn
    # 例: ARR $50M なのに employees < 30 → 異常 (warn)
    # 例: ARR $1M なのに employees > 200 → 異常 (warn)
```

### 3.3 Stage 早見表 (3.2 の table 表現)

| Stage | ARR (USD) | Revenue (USD, 非 SaaS) | 典型 Employees | 典型 Burn (USD/月) |
|---|---|---|---|---|
| `pre_revenue` | 0 | 0 | 1-10 | $50K-$200K |
| `early_revenue` | <$1M | <$1M | 5-20 | $100K-$400K |
| `series_a` | $1-5M | $1-5M | 15-50 | $300K-$1M |
| `series_b` | $5-20M | $5-30M | 40-150 | $800K-$3M |
| `series_c` | $20-50M | $30-100M | 120-400 | $2-8M |
| `pre_ipo` | $50M+ | $100M+ | 350+ | $5M-$20M |
| `public` | -- | -- | -- | -- |

> 出典: `08 §3.1` (ARR / 評価額 table)、`11 §3.2` (Burn benchmarks)、Bessemer Cloud Index 2024 の Stage 別中央値を保守側に丸めた。

### 3.4 Manual override

`funding_stage_manual` (optional, enum) を別 field として用意。ユーザーが auto-judge を上書きできる。Override 時は audit trail として `_meta.stage_override_reason` (string, 自由記述) を保存。

### 3.5 矛盾検知 (warning)

| 矛盾パターン | 警告 |
|---|---|
| ARR $5M 以上 & employees < 10 | "従業員数が ARR に対して少ない (異常値の可能性)" |
| ARR $1M 未満 & employees > 100 | "従業員数が ARR に対して多い (Pre-product or Hardware 初期の可能性)" |
| `funding_stage_manual = pre_ipo` & ARR < $30M | "Stage と ARR が乖離。ARR 補正または stage 再判定を推奨" |
| `is_pre_revenue = true` & ARR > 0 | "矛盾。pre_revenue フラグまたは ARR を修正" |

> 出典: §8 (Validation rules) の Soft warn。

---

## 4. 共通 Input Field (全業態共通)

### 4.1 Field 一覧 (最重要 30-40 個)

全業態共通の必須 / optional field を以下の table で定義。**type / 必須 / default / validation / source ref** の 5 列を備える。

#### 4.1.1 Company Profile

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `company_name` | string | Quick | -- | 1-120 chars | 06 §A.1 Cover sheet |
| `company_legal_form` | enum | Standard | `kk` | enum: kk, gk, llc, c_corp, foreign_other | 07 §3.1 |
| `founded_year` | int (YYYY) | Quick | -- | 1900 <= year <= 現在年 | 06 §A.1 |
| `headquarters_country` | enum (ISO 3166-1 alpha-2) | Quick | `JP` | 2 chars uppercase | 07 §1 |
| `reporting_currency` | enum | Quick | `JPY` | enum: JPY, USD, EUR, GBP, CNY, SGD, KRW, TWD | 06 §1.4 |
| `presentation_currency` | enum | Standard | = `reporting_currency` | 同上 | 13a §4 (multi-currency) |
| `fiscal_year_end` | string (MM-DD) | Quick | `03-31` | regex: `^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$` | 07 §2.1 |
| `accounting_basis` | enum | Standard | `jgaap` | enum: jgaap, ifrs, us_gaap | 07 §2, 06 §2 |
| `is_consolidated` | boolean | Standard | false | -- | 13a §1 |
| `parent_company_name` | string | optional | null | 1-120 chars (consolidated 時必須) | 13a §1 |

> **Default の根拠**: 国内スタートアップは `kk` (株式会社) が ~95%、`gk` (合同会社) が小規模に存在 (07 §3.1)。`fiscal_year_end` は `03-31` が日本企業の慣習で多数派 (07 §2.1)、欧米向けは `12-31` を推奨 default に切り替えてもよい (国別 default を §9 に列挙)。

#### 4.1.2 Forecast Configuration

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `forecast_period_years` | int | Quick | 5 | 1 <= n <= 10 | 01a §4.1, 06 §3 |
| `forecast_granularity` | enum | Standard | `monthly_36_then_annual` | enum: monthly, quarterly, annual, monthly_36_then_annual | 01a §4.2 |
| `historical_years_loaded` | int | Standard | 3 | 0 <= n <= 10 | 06 §3.2 |
| `model_start_date` | string (YYYY-MM) | Standard | 当月 | regex: `^\d{4}-(0[1-9]|1[0-2])$` | 06 §3 |
| `terminal_value_method` | enum | Standard | `gordon_growth` | enum: gordon_growth, exit_multiple, h_model, none | 05 §6 |
| `terminal_growth_rate_pct` | float | optional | 2.0 | -1.0 <= x <= 5.0 (%) | 05 §6.1 |
| `discount_rate_method` | enum | Standard | `wacc` | enum: wacc, hurdle_rate, manual | 05 §3 |
| `tax_rate_pct` | float | Standard | 30.6 | 0 <= x <= 50 (%) | 12 §1 (法定実効税率 ~30.6% in JP) |

> **Default の根拠**: `forecast_period_years=5` は VC モデル業界標準 (01a §4.1)。`monthly_36_then_annual` は IB 標準で 36 か月月次 + 残り年次 (01a §4.2)。`terminal_growth_rate_pct=2.0` は日米長期 GDP 成長率の保守側 (05 §6.1)。`tax_rate_pct=30.6` は 2024 年度日本法定実効税率 (12 §1)。

#### 4.1.3 Macro Assumption

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `fx_jpy_per_usd` | float | Standard | 150.0 | 50 <= x <= 300 | 13a §4 (multi-currency) |
| `inflation_rate_pct` | float | optional | 2.0 | -2.0 <= x <= 10.0 (%) | 05 §3.4 |
| `risk_free_rate_pct` | float | optional | 1.5 | 0 <= x <= 10.0 (%) | 05 §3.2 (日本 10y JGB ~1.5%) |
| `equity_risk_premium_pct` | float | optional | 6.0 | 3.0 <= x <= 10.0 (%) | 05 §3.3 |
| `country_risk_premium_pct` | float | optional | 0.0 | 0 <= x <= 15.0 (%) | 05 §3.5 (Damodaran) |

#### 4.1.4 Headcount and Compensation

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `employees` | int | Quick | -- | 1 <= n <= 10000 | 06 §6 (HR plan) |
| `headcount_split_pct` | object | Standard | `{eng: 50, sales: 25, gna: 15, other: 10}` | sum = 100 | 06 §6.2 |
| `avg_salary_jpy` | int | Standard | 8_000_000 | 3M <= x <= 30M | 07 §6 (賞与込み年収中央値) |
| `payroll_burden_pct` | float | Standard | 16.5 | 10.0 <= x <= 25.0 (%) | 07 §6.2 (社保会社負担 + 労災) |
| `hiring_plan_growth_pct_yoy` | float | Standard | 50.0 | -50 <= x <= 300 (%) | 06 §6.3 |
| `esop_pool_pct` | float | Standard | 10.0 | 0 <= x <= 30 (%) | 04b §3.1 (Pre-Series A typical 10%) |
| `esop_grant_velocity_pct_yoy` | float | optional | 1.5 | 0 <= x <= 5 (%) | 04b §3.3 (年間 grant ペース) |

#### 4.1.5 Founders / Cap Table Skeleton (詳細は §6)

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `founder_share_pct` | float | Quick | 75.0 | 1 <= x <= 100 (%, ESOP 込みの **post-money 比率**) | 04b §2 |
| `n_founders` | int | Standard | 2 | 1 <= n <= 10 | 04b §2.1 |
| `total_shares_outstanding` | int | Standard | 100_000 | 1 <= n <= 10^9 | 04b §1.2 |
| `par_value_jpy` | float | optional | 1.0 | 0 <= x <= 100_000 | 07 §3 |

#### 4.1.6 Cash and Working Capital (Pre-revenue でも必須)

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `cash_on_hand_jpy` | int | Quick | 0 | 0 <= x | 06 §B (BS Cash) |
| `monthly_burn_jpy` | int | Quick | -- | 0 <= x <= 1_000_000_000 | 11 §3.2 (burn rate) |
| `dso_days` | int | Standard | 60 | 0 <= n <= 180 | 06 §5.2 (AR days) |
| `dpo_days` | int | Standard | 45 | 0 <= n <= 180 | 06 §5.2 (AP days) |
| `dio_days` | int | optional | 30 | 0 <= n <= 365 (在庫業態のみ) | 06 §5.2 |

> **Default の根拠**: `dso_days=60` は B2B SaaS の中央値 (06 §5.2、Net 60 が標準)。`dpo_days=45` は SaaS / サービス業の中央値。在庫業態 (D2C / Hardware / Manufacturing) は `dio_days` 必須化、§5 で業態別 default を上書き。

#### 4.1.7 Capex and Asset

| Field | Type | Mode 必須 | Default | Validation | Source ref |
|---|---|---|---|---|---|
| `capex_pct_revenue` | float | Standard | 3.0 | 0 <= x <= 50 (%) | 06 §B (Capex line) |
| `depreciation_useful_life_years` | int | optional | 5 | 1 <= n <= 50 | 07 §4 (税法償却期間) |
| `intangibles_amortization_years` | int | optional | 5 | 1 <= n <= 20 | 07 §4 |

### 4.2 Field の Quick / Standard / Comprehensive 分布

- **Quick (10-15 field)**: §4.1.1 から `company_name, founded_year, headquarters_country, reporting_currency`、§4.1.2 から `forecast_period_years`、§4.1.4 から `employees`、§4.1.5 から `founder_share_pct`、§4.1.6 から `cash_on_hand_jpy, monthly_burn_jpy`、+ `business_model`, `funding_stage` (§2-§3)、+ 業態別の最重要 KPI 1-3 個 (§5、SaaS なら ARR / NRR / CAC payback)。合計 12-13 field。
- **Standard (30-50 field)**: 上記 + §4.1 の Standard 列すべて + 業態別 Standard field (§5) + Cap Table summary (§6 summary form) + Debt summary (§7 summary form)。合計 35-45 field。
- **Comprehensive (100-200 field)**: 上記 + 業態別 Comprehensive (segment 別、cohort 別、product line 別) + Cap Table の preferred/SAFE 全件 (§6 詳細) + Debt facility 全件 (§7 詳細) + Tax 詳細 (12 §) + Consolidation entity ツリー (13a §) + Treasury (13b §) + IPO 準備 (14 §)。合計 120-180 field。

### 4.3 Field 検証順序 (build_model.py 内で)

1. **Schema-level**: type, enum, regex, range (pydantic で機械的に検証)
2. **Cross-field consistency**: §8.2 の hard fail / soft warn (例: founder + investor + ESOP > 100%)
3. **Business model dependency**: §5 の業態別必須 field (例: `business_model=saas` なら `arr_jpy` / `nrr_pct` 必須)
4. **Stage dependency**: §3 の auto-judge と manual override の整合性
5. **Default fill**: 未入力 field を §9 (業態 × Stage default) で充填
6. **Final sanity**: §8.3 の最終チェック (cash < 0、growth > 1000% 等)

### 4.4 Pricing thesis section (Phase 6 拡張)

> 出典: `18_customer_value_and_pricing.md §3 (Quantification), §4 (Value-based pricing), §5 (Pricing model 選定)`。Mode 依存: Quick = `pricing_model` のみ、Standard = + `customer_roi_annual_pct` / `gainsharing_pct`、Comprehensive = 全 field。

```yaml
pricing:
  pricing_model: enum("subscription" | "usage_based" | "outcome_based" | "hybrid" | "tiered" | "freemium" | "perpetual_license")
  scale_currency: enum("JPY" | "USD" | "EUR")
  scale_display: enum("actual" | "thousand" | "million" | "hundred_million")
customer_value:
  customer_roi_annual_pct: float           # 中央値、例 0.30 = 30%。`18 §3.1` の Net Benefit / Customer Cost
  customer_roi_payback_months: int         # 例 12。Standard 以上で必須、Quick では default 18 で fill
  gainsharing_pct: float                   # vendor の取り分、例 0.30 = 30%。`18 §4.1` の boundary 20-30% 内
  wtp_estimate_money_m: float              # ¥M、Van Westendorp PSM の OPP 値 (`18 §3.4`)
  pricing_realization_pct: float           # = actual ARPU / list price、discount の概況 (1.0 = no discount)
  net_pricing_power_yoy: float             # 年率、ARPU growth - inflation。`18 §6.2` の YoY metric
```

| Field | Type | Mode | Default (業態別) | Validation | 出典 |
|---|---|---|---|---|---|
| `pricing_model` | enum (7 値) | All | SaaS=`subscription`, Marketplace=`usage_based`, D2C=`tiered`, Fintech=`outcome_based`, Hardware=`perpetual_license` | enum 列挙のみ | `18 §5.1` |
| `scale_currency` | enum | All | `reporting_currency` を継承 | -- | `_design_consistency_rules §2.1` |
| `scale_display` | enum (4 値) | All | `auto` (= ARR から判定) | -- | `_design_consistency_rules §2.2` |
| `customer_roi_annual_pct` | float | Standard | SaaS=0.30, Marketplace=0.20, D2C=0.15, Fintech=0.25, Hardware=0.40 | range [-0.5, 5.0]、warn if < 0 | `18 §3.1` |
| `customer_roi_payback_months` | int | Standard | 12 (SaaS), 18 (Hardware), 6 (D2C) | range [1, 60] | `18 §3.2` |
| `gainsharing_pct` | float | Standard | 0.25 | range [0, 1]、**warn if > 0.30 or < 0.20** (`18 §4.1` boundary) | `18 §4.1` |
| `wtp_estimate_money_m` | float | Comprehensive | -- (任意) | range [0, ∞)、PSM optional | `18 §3.4` |
| `pricing_realization_pct` | float | Comprehensive | 0.85 (B2B SaaS), 0.95 (D2C) | range [0.4, 1.2] | `18 §6.1` |
| `net_pricing_power_yoy` | float | Comprehensive | 0.03 (3%) | range [-0.20, 0.30] | `18 §6.2` |

> **Boundary check**: `gainsharing_pct` は customer ROI ÷ vendor share の比率制約 (`18 §4.1.3`)。`gainsharing_pct × customer_roi_annual_pct > 0.50` の場合 hard fail (over-extraction)、`< 0.05` の場合 soft warn (under-pricing)。

### 4.5 Exit thesis section (Phase 6 拡張)

> 出典: `19_ma_exit_for_founders.md §1 (Likely Buyers), §6 (Founder Net), §10 (Lock-up/Escrow), §11 (Earn-out), §13 (QSBS / OBBBA)`。Mode 依存: Quick = exit pathway probability + expected_exit_year のみ、Standard = + acquirer_shortlist (top 3) + consideration_mix、Comprehensive = 全 field。

```yaml
exit:
  expected_exit_year: int                  # 例 2030。`19 §2` で 5-7 年 default
  exit_pathway_probability:                # Σ = 1.0 (validation)
    strategic_ma: 0.6
    ipo: 0.2
    pe_recap: 0.15
    no_exit: 0.05
  acquirer_shortlist:                      # `19 §1.2` の Likely Buyer Map
    - name: str
      type: enum("strategic" | "financial" | "tuck_in")
      ev_multiple_estimate: float          # EV / Revenue or EV / EBITDA、業態依存
  founder_jurisdiction: enum("US_QSBS" | "US_NonQSBS" | "JP_Standard" | "JP_Reorg")
  qsbs_qualification_status: enum("legacy" | "post_obbba" | "non_qsbs" | "n/a")
                                           # OBBBA (One Big Beautiful Bill Act) 2025-07-04 区分
                                           # legacy = 2025-07-04 前 (旧 §1202、5y hold / $10M cap)
                                           # post_obbba = 2025-07-04 後 (3-yr 50% / 4-yr 75% / 5-yr 100%、$15M cap)
                                           # `19 §13.2` 参照
  expected_consideration_mix:              # Σ = 1.0 (validation)
    cash_pct: float
    stock_pct: float
    earn_out_pct: float
  expected_lockup_months: int              # 典型 6-24。`19 §10.1`
  expected_escrow_pct: float               # 典型 0.10-0.20。`19 §10.2`
  expected_escrow_period_months: int       # 典型 12-24。`19 §10.2`
```

| Field | Type | Mode | Default | Validation | 出典 |
|---|---|---|---|---|---|
| `expected_exit_year` | int | All | `founded_year + 7` | range [`current_year + 1`, `current_year + 15`] | `19 §2.1` |
| `exit_pathway_probability` | object | All | strategic_ma=0.6, ipo=0.2, pe_recap=0.15, no_exit=0.05 | **Σ = 1.0 ± 0.001** (hard fail) | `19 §2.2` |
| `acquirer_shortlist` | array | Standard | -- (任意、Standard 推奨 top 3) | maxItems=10 | `19 §1.2` |
| `founder_jurisdiction` | enum | All | `US_QSBS` if `headquarters_country=US`, `JP_Standard` if `JP` | -- | `19 §13.1`, `12 §3` |
| `qsbs_qualification_status` | enum | Comprehensive | `n/a` if not US, else `post_obbba` if `founded_year ≥ 2025` | US 以外で `legacy`/`post_obbba` の場合 hard fail | `19 §13.2` (OBBBA 2025-07-04) |
| `expected_consideration_mix` | object | Standard | cash=0.7, stock=0.2, earn_out=0.1 (strategic), cash=1.0 (PE) | **Σ = 1.0 ± 0.001** (hard fail) | `19 §6.3` |
| `expected_lockup_months` | int | Standard | 12 | range [0, 36]、warn if > 24 | `19 §10.1` |
| `expected_escrow_pct` | float | Standard | 0.15 | range [0, 0.30]、warn if > 0.20 | `19 §10.2` |
| `expected_escrow_period_months` | int | Standard | 18 | range [6, 36] | `19 §10.2` |

> **OBBBA boundary**: `qsbs_qualification_status=legacy` は **founded_year ≤ 2025-07-03** の取得株式に限定。`post_obbba` は 2025-07-04 以降取得分で、3-yr 50% / 4-yr 75% / 5-yr 100% 段階免除 + cap $15M (旧 $10M から拡大)。`19 §13.2` の OBBBA flowchart を参照。
>
> **Earn-out probability の整合**: `expected_consideration_mix.earn_out_pct > 0` の場合、`19 §11` の達成確率 (Bayesian conditional E[earn_out | revenue_run_rate]) を IC memo §Exit に記載すること。`_self_review_protocol §8.8` の M&A Exit thesis check で確認。

### 4.6 Design consistency section (Phase 6 拡張)

> 出典: `_design_consistency_rules.md §2 (単位 scale), §3 (font/IB color), §4 (chart 統一), §5 (sanity_checks D1-D12)`。**全 mode で必須** (default fill で auto-decide 可)。`scripts/ib_format.py` の `apply_*` helper が本 section を参照する。

```yaml
design:
  workbook_scale: enum("auto" | "thousand" | "million" | "hundred_million")
                                           # auto: ARR から判定 (`_design §2.2` table)
                                           #   ARR < ¥100M       → thousand (千)
                                           #   ¥100M ≤ ARR < 10B → million (百万)
                                           #   ARR ≥ ¥10B         → hundred_million (億)
  workbook_currency: enum("JPY" | "USD")
  named_range_strategy: enum("workbook_scoped" | "sheet_scoped" | "hybrid")
                                           # default hybrid (cross-sheet → workbook、sheet 内中間値 → sheet)
                                           # `_named_ranges §1.1` 判定ルール準拠
  font_family: "Calibri"                   # canonical (consistent with ib_format.FONT_HARD_INPUT 等)
  font_size_base: 11                       # default。header は +2pt、note は -1pt
  enable_charts: bool                      # default true。Chart 出力を 11_KPI_Dashboard / 09_DCF / 09_DCF § Sensitivity に追加
  enable_data_validation: bool             # default true。input cell に dropdown / range 制約を付与
  enable_zebra_stripes: bool               # default false。読みやすさ目的、IB 慣習では off
```

| Field | Type | Mode | Default | Validation | 出典 |
|---|---|---|---|---|---|
| `workbook_scale` | enum (4 値) | All | `auto` | enum のみ | `_design §2.2` |
| `workbook_currency` | enum | All | = `reporting_currency` (JPY/USD のみ) | -- | `_design §2.1` |
| `named_range_strategy` | enum (3 値) | All | `hybrid` | -- | `_named_ranges §1.1` |
| `font_family` | str | All | `"Calibri"` | enum {Calibri, Arial, Meiryo} (warn if その他) | `_design §3.1` |
| `font_size_base` | int | All | 11 | range [9, 14] | `_design §3.1` |
| `enable_charts` | bool | All | true | -- | `_design §4`, `17_chart_design.md` |
| `enable_data_validation` | bool | Standard | true | -- | `_design §5` |
| `enable_zebra_stripes` | bool | Comprehensive | false | -- | `_design §3.3` |

> **Auto-decide rules**:
> - `workbook_scale=auto` の場合、build 時に `arr_jpy` (or 業態の中核 metric) から `_design §2.2` の閾値で自動選択
> - `workbook_currency` が `reporting_currency` と異なる場合、`00_Cover` Notes に exchange rate 注記を自動付与 (`_design §2.1`)
> - `font_family != "Calibri"` の場合、`_self_review_protocol §8.10` の Design consistency check で warn 出力

> **Sanity check 連携**: 本 section の値は `12_SanityChecks` シートの D1-D12 row で検証される (`_design §5`)。D1 = font 統一、D2 = scale 一貫性、D3 = IB color 適用、…、D12 = named range coverage ≥ 80% (`_self_review_protocol §8.9`)。

---

## 5. 業態別 Input Field (主要 5 業態)

各業態の主要 input field を listing。**業態 11 種すべての全 field を網羅すると分量過多になるため、本章では出現頻度上位 5 業態 (SaaS / Marketplace / D2C / Fintech / Hardware) を完全定義** し、残り 6 業態 (Bio / Media / B2B Services / Manufacturing / Real Estate / AI Foundation) は §5.6 で要点のみ記述する (build phase 第 2 段階で拡充)。

### 5.1 SaaS / Subscription

> 出典: `02 §1-§7`、`03 §3 (SaaS)`、`08 §3.2.1`。

#### 5.1.1 必須 KPI (Quick mode 含む)

| Field | Type | Mode 必須 | Default (Series A) | Validation | Source ref |
|---|---|---|---|---|---|
| `arr_jpy` | int | Quick | -- | 0 <= x | 02 §2.1 |
| `mrr_jpy` | int | Standard | = `arr_jpy / 12` | 0 <= x | 02 §2.1 |
| `n_customers` | int | Standard | -- | 0 <= n | 02 §3.1 |
| `arpu_jpy_per_month` | int | Standard | -- (= MRR / customers) | 0 <= x | 02 §3.2 |
| `gross_margin_pct` | float | Quick | 75.0 | 0 <= x <= 95 | 02 §2.4 (SaaS 中央値 70-80%) |
| `nrr_pct` | float | Quick | 110.0 | 50 <= x <= 200 | 02 §3.4 (Best-in-class 120%+) |
| `grr_pct` | float | Standard | 90.0 | 50 <= x <= 100 | 02 §3.4 (= 100% - logo churn 換算) |
| `logo_churn_pct_annual` | float | Standard | 8.0 | 0 <= x <= 50 | 02 §3.5 |
| `revenue_churn_pct_annual` | float | Standard | 5.0 | -50 <= x <= 50 (上向き expansion で負も可) | 02 §3.5 |
| `cac_jpy` | int | Standard | -- | 0 <= x | 02 §4.1 |
| `cac_payback_months` | float | Quick | 18.0 | 0 <= x <= 60 | 02 §4.4 (Series A target <18) |
| `ltv_jpy` | int | Standard | -- (= ARPU * GM% / churn) | 0 <= x | 02 §4.2 |
| `ltv_cac_ratio` | float | Standard | 3.0 | 0 <= x <= 20 | 02 §4.5 (target >= 3) |
| `magic_number` | float | optional | 0.7 | 0 <= x <= 3 | 02 §5.2 |
| `burn_multiple` | float | optional | 1.5 | 0 <= x <= 10 | 02 §5.3 (target <1.5) |
| `rule_of_40` | float | optional | -- (= growth% + FCF margin%) | -100 <= x <= 200 | 02 §5.4 |

#### 5.1.2 Comprehensive 拡張

| Field | Type | Default | Note |
|---|---|---|---|
| `arr_by_cohort` | array of {cohort_month, arr_jpy} | -- | Cohort 分析 (02 §6) |
| `expansion_arr_pct_of_new` | float | 30 | Expansion / New ARR 比 (02 §3.6) |
| `pricing_tiers` | array of {tier_name, monthly_price_jpy, customer_count} | -- | Tier 別売上分解 |
| `usage_based_pct` | float | 0 | 従量課金比率 (02 §11) |
| `multi_year_contract_pct` | float | 30 | 複数年契約比率 (02 §10 ASC 606) |

### 5.2 Marketplace

> 出典: `03 §4 (Marketplace)`、`08 §3.2.2`。

| Field | Type | Mode 必須 | Default (Series A) | Validation | Source ref |
|---|---|---|---|---|---|
| `gmv_jpy_annual` | int | Quick | -- | 0 <= x | 03 §4.1 |
| `take_rate_pct` | float | Quick | 15.0 | 0 <= x <= 50 | 03 §4.2 (取引型 10-20%) |
| `n_transactions_annual` | int | Standard | -- | 0 <= n | 03 §4.3 |
| `aov_jpy` | int | Standard | -- (= GMV / transactions) | 0 <= x | 03 §4.3 |
| `n_buyers_active` | int | Standard | -- | 0 <= n | 03 §4.4 |
| `n_sellers_active` | int | Standard | -- | 0 <= n | 03 §4.4 |
| `liquidity_ratio` | float | optional | 0.3 | 0 <= x <= 1 | 03 §4.5 (1 sellers 当たり buyer match 率) |
| `repeat_purchase_rate_pct` | float | Standard | 35.0 | 0 <= x <= 100 | 03 §4.6 |
| `cac_jpy` | int | Standard | -- | 0 <= x | 03 §4.7 |
| `contribution_margin_pct` | float | Standard | 25.0 | -50 <= x <= 80 | 03 §4.8 (revenue ベースで計算) |
| `take_rate_volatility` | float | optional | 0.1 | 0 <= x <= 1 | 03 §4.2 (補助金後の実効 take rate 変動) |

### 5.3 D2C / E-commerce

> 出典: `03 §5 (D2C)`、`08 §3.2.3`。

| Field | Type | Mode 必須 | Default (Series A) | Validation | Source ref |
|---|---|---|---|---|---|
| `revenue_jpy_annual` | int | Quick | -- | 0 <= x | 03 §5.1 |
| `gross_margin_pct` | float | Quick | 50.0 | 10 <= x <= 80 | 03 §5.2 (D2C 中央値 40-55%) |
| `aov_jpy` | int | Quick | 8000 | 1000 <= x <= 100_000 | 03 §5.3 |
| `n_orders_annual` | int | Standard | -- | 0 <= n | 03 §5.3 |
| `repeat_purchase_rate_pct` | float | Quick | 30.0 | 0 <= x <= 100 | 03 §5.4 |
| `n_customers_active_annual` | int | Standard | -- | 0 <= n | 03 §5.5 |
| `cac_jpy` | int | Standard | -- | 0 <= x | 03 §5.6 |
| `cac_payback_months` | float | Standard | 12.0 | 0 <= x <= 36 | 03 §5.6 |
| `contribution_margin_pct` | float | Standard | 25.0 | -20 <= x <= 60 | 03 §5.7 (CM2: GM - shipping - returns) |
| `return_rate_pct` | float | Standard | 8.0 | 0 <= x <= 50 | 03 §5.8 |
| `inventory_turns_annual` | float | Standard | 6.0 | 1 <= x <= 30 | 03 §5.9 |
| `cohort_repeat_curve` | array of float (M1, M3, M6, M12) | optional | [0.6, 0.4, 0.3, 0.25] | 0 <= x <= 1 | 03 §5.10 |

### 5.4 Fintech (Lending / Payments)

> 出典: `03 §6 (Fintech)`、`08 §3.2.4`、`07 §9` (金融業特有税制)。

| Field | Type | Mode 必須 | Default (Series A) | Validation | Source ref |
|---|---|---|---|---|---|
| `fintech_subtype` | enum | Quick | `payments` | enum: payments, lending, neobank, wealth, insurtech, crypto | 03 §6.1 |
| `tpv_jpy_annual` | int | Quick | -- | 0 <= x | 03 §6.2 (Total Payment Volume) |
| `take_rate_pct` | float | Quick (payments) | 1.5 | 0 <= x <= 10 | 03 §6.3 (payments 中央値) |
| `nim_pct` | float | Quick (lending) | 8.0 | 0 <= x <= 30 | 03 §6.4 (Net Interest Margin) |
| `loan_book_outstanding_jpy` | int | Quick (lending) | -- | 0 <= x | 03 §6.5 |
| `npl_ratio_pct` | float | Standard (lending) | 3.0 | 0 <= x <= 30 | 03 §6.6 (Non-performing loan) |
| `loss_rate_pct_annual` | float | Standard | 2.0 | 0 <= x <= 30 | 03 §6.7 (charge-off rate) |
| `cac_jpy` | int | Standard | -- | 0 <= x | 03 §6.8 |
| `cohort_lifetime_months` | float | optional | 36 | 6 <= x <= 120 | 03 §6.9 |
| `regulatory_capital_pct` | float | optional (lending) | 8.0 | 0 <= x <= 30 | 07 §9 (BIS / 自己資本比率) |
| `funding_cost_pct` | float | optional (lending) | 2.0 | 0 <= x <= 15 | 03 §6.10 |
| `interchange_fee_pct` | float | optional (payments) | 1.0 | 0 <= x <= 3 | 03 §6.3 |

### 5.5 Hardware / IoT

> 出典: `03 §7 (Hardware)`、`08 §3.2.5`。

| Field | Type | Mode 必須 | Default (Series A) | Validation | Source ref |
|---|---|---|---|---|---|
| `hw_revenue_jpy_annual` | int | Quick | -- | 0 <= x | 03 §7.1 |
| `recurring_revenue_jpy_annual` | int | Standard | -- | 0 <= x | 03 §7.1 (sub の software/IoT 部分) |
| `gross_margin_pct_hw` | float | Quick | 30.0 | 5 <= x <= 60 | 03 §7.2 (HW 部分のみ) |
| `gross_margin_pct_recurring` | float | Standard | 70.0 | 30 <= x <= 90 | 03 §7.2 |
| `bom_cost_pct_revenue` | float | Standard | 50.0 | 10 <= x <= 90 | 03 §7.3 (Bill of Material) |
| `inventory_turns_annual` | float | Standard | 4.0 | 1 <= x <= 12 | 03 §7.4 |
| `attach_rate_pct` | float | Standard | 60.0 | 0 <= x <= 100 | 03 §7.5 (HW + recurring の attach 率) |
| `recurring_arpu_jpy_per_month` | float | Standard | 1500 | 100 <= x <= 100000 | 03 §7.6 |
| `recurring_churn_pct_annual` | float | Standard | 10.0 | 0 <= x <= 50 | 03 §7.7 |
| `warranty_cost_pct_revenue` | float | optional | 2.5 | 0 <= x <= 10 | 03 §7.8 |
| `manufacturing_lead_time_days` | int | optional | 60 | 7 <= x <= 365 | 03 §7.9 |
| `dio_days` | int | Standard | 90 | 30 <= x <= 365 | 06 §5.2 (HW は在庫が長い) |

### 5.6 残り 6 業態 (要点のみ、build phase 2 で拡充)

| 業態 | 必須 KPI (Quick) | 出典 |
|---|---|---|
| `bio_pharma` | `phase_stage` (enum: preclinical, phase1, phase2, phase3, approved), `target_indication`, `peak_sales_jpy_estimate`, `royalty_rate_pct`, `cogs_pct_post_approval` | 03 §8 |
| `media_content` | `mau`, `arpu_jpy_per_month`, `ad_revenue_pct`, `subscription_revenue_pct`, `content_amortization_years` | 03 §9 |
| `b2b_services` | `revenue_jpy_annual`, `utilization_rate_pct`, `bill_rate_jpy_per_hour`, `n_billable_consultants`, `gross_margin_pct` | 03 §10 |
| `manufacturing` | `revenue_jpy_annual`, `gross_margin_pct`, `bom_cost_pct`, `inventory_turns_annual`, `dio_days`, `capex_pct_revenue` (高め) | 03 §10 |
| `real_estate` | `gav_jpy` (Gross Asset Value), `noi_pct` (Net Operating Income), `cap_rate_pct`, `ltv_pct` (Loan-to-Value), `dscr` (Debt Service Coverage Ratio) | 03 §10 |
| `ai_foundation_model` | `revenue_jpy_annual`, `compute_cost_jpy_annual`, `training_run_cost_jpy`, `gpu_hours_consumed`, `gross_margin_pct` (低め -20%-30%), `model_release_cadence_months` | 03 §10 |

> 各業態の完全 schema は build phase 2 で本書に追記。Quick mode で書類化する場合は上記 5 KPI を必須化し、残りは §9 default を充填する。

---

## 6. Cap Table Input

> 出典: `04a` (Convertible / SAFE / J-KISS)、`04b` (Cap Table mechanics)、`07 §3` (株式関連の日本特殊事項)。

### 6.1 構造の二層化

Cap Table 入力は **summary form (Quick / Standard 用) と detail form (Comprehensive 用)** の二層に分ける。

#### 6.1.1 Summary form (Standard まで)

| Field | Type | Default | Validation | Source ref |
|---|---|---|---|---|
| `total_shares_outstanding` | int | 100_000 | 1 <= n <= 10^9 | 04b §1.2 |
| `founder_shares` | int | 75_000 | 0 <= n | 04b §2 |
| `common_pool_shares` | int | 0 | 0 <= n | 04b §1.3 |
| `esop_pool_shares_authorized` | int | 10_000 | 0 <= n | 04b §3.1 |
| `esop_pool_shares_issued` | int | 3_000 | 0 <= n <= esop_pool_shares_authorized | 04b §3.2 |
| `preferred_shares_total` | int | 12_000 | 0 <= n | 04b §4 |
| `safe_outstanding_count` | int | 0 | 0 <= n <= 50 | 04a §2.1 |
| `safe_total_principal_jpy` | int | 0 | 0 <= x | 04a §2.1 |

#### 6.1.2 Detail form (Comprehensive)

Comprehensive mode では preferred / SAFE / option grant を **配列** として全件展開する。

```yaml
preferred_rounds:
  type: array
  items:
    round_name:
      type: string
      enum: ["seed", "series_a", "series_b", "series_c", "series_d", "bridge", "extension"]
    closing_date:
      type: string  # YYYY-MM-DD
    shares_issued:
      type: int
    price_per_share_jpy:
      type: float
      validation: x > 0
    pre_money_jpy:
      type: int
    post_money_jpy:
      type: int
    liquidation_preference_multiple:
      type: float
      default: 1.0
      validation: 1.0 <= x <= 3.0
      source: 04a §3.3
    participation:
      type: enum
      enum: ["non_participating", "full_participating", "capped_participating"]
      default: "non_participating"
      source: 04a §3.4
    participation_cap_multiple:
      type: float
      default: 3.0
      validation: 1.0 <= x <= 5.0  # capped 時のみ
    dividend_pct:
      type: float
      default: 0.0
      validation: 0.0 <= x <= 15.0
      source: 04a §3.5
    dividend_cumulative:
      type: bool
      default: false
    anti_dilution:
      type: enum
      enum: ["none", "full_ratchet", "broad_based_weighted_average", "narrow_based_weighted_average"]
      default: "broad_based_weighted_average"
      source: 04a §3.6
    voting_rights:
      type: enum
      enum: ["one_per_share", "as_converted", "special_class_voting"]
      default: "as_converted"
    pay_to_play:
      type: bool
      default: false
      source: 04a §3.7
    redemption_right:
      type: bool
      default: false
      source: 04a §3.8
```

```yaml
safe_notes:
  type: array
  items:
    note_id:
      type: string
    instrument_type:
      type: enum
      enum: ["safe_pre_money", "safe_post_money", "j_kiss", "convertible_note"]
      default: "j_kiss"
      source: 04a §1, §2
    closing_date:
      type: string  # YYYY-MM-DD
    principal_jpy:
      type: int
      validation: x >= 1
    cap_jpy:
      type: int  # null 許容 (uncapped)
      validation: x >= principal_jpy
      source: 04a §2.3
    discount_pct:
      type: float
      default: 20.0
      validation: 0.0 <= x <= 50.0
      source: 04a §2.4
    mfn_clause:
      type: bool
      default: false
      source: 04a §2.5  # Most Favored Nation
    interest_rate_pct:
      type: float
      default: 0.0  # SAFE は 0、convertible note は通常 4-8%
      validation: 0.0 <= x <= 15.0
    maturity_date:
      type: string  # YYYY-MM-DD (null 許容、SAFE は通常 null)
    conversion_trigger:
      type: enum
      enum: ["next_qualified_round", "ipo", "change_of_control", "maturity"]
      default: "next_qualified_round"
    conversion_minimum_round_size_jpy:
      type: int
      default: 100_000_000  # qualified round の最低額
    pro_rata_right:
      type: bool
      default: false
      source: 04a §2.6
```

```yaml
option_grants:
  type: array  # ESOP 詳細 (04b §3)
  items:
    grant_id:
      type: string
    grantee_role:
      type: enum
      enum: ["executive", "engineer", "sales", "advisor", "other"]
    shares_granted:
      type: int
    grant_date:
      type: string
    exercise_price_jpy:
      type: float
    vesting_years:
      type: int
      default: 4
    cliff_months:
      type: int
      default: 12
    vesting_schedule:
      type: enum
      enum: ["monthly", "quarterly", "annual"]
      default: "monthly"
    is_iso:  # 税制適格 SO
      type: bool
      default: true
      source: 07 §3.5 (税制適格 SO 要件)
    early_exercise:
      type: bool
      default: false
```

### 6.2 Anti-dilution の指定方法

`anti_dilution` enum は preferred 各 round で個別に指定可能。空欄の場合は `broad_based_weighted_average` を default とする。Down round 発生時の new conversion ratio は `04a §3.6` の式で計算する (build_model.py の cap_table_builder が自動再計算)。

### 6.3 ESOP の表現

- `esop_pool_pct` (Quick / Standard): post-money fully-diluted ベースの ESOP authorize 比率
- `esop_pool_shares_authorized` / `_issued` (Standard): 株数ベース
- `option_grants` 配列 (Comprehensive): grant 単位の詳細

3 経路は **fully-diluted post-money 比率で必ず一致** すること。一致しない場合は build_model.py が hard fail する (§8.2)。

### 6.4 Round-trip / SAFE conversion 反復解

SAFE / convertible note の next round 転換は **fixed-point iteration** で解く (詳細仕様は cap_table_builder.py で実装、reference は `04a §4` 参照)。本 schema 段階では入力 field のみ定義し、計算 logic は本書 scope 外。

### 6.5 Cap Table 入力の Mode 依存

| Mode | 必須 |
|---|---|
| Quick | `founder_share_pct`, `esop_pool_pct` のみ |
| Standard | summary form (§6.1.1) 全 field + 主要 round (`series_a` 1 件) |
| Comprehensive | detail form (§6.1.2) 全 field、複数 round + SAFE 全件 + option grant 全件 |

---

## 7. Debt Input

> 出典: `11` (Debt financing 全章)、`07 §7` (政策金融公庫 / JFC)、`12 §6` (税務上の debt 取扱)。

### 7.1 Facility 配列

```yaml
debt_facilities:
  type: array
  items:
    facility_id:
      type: string
    facility_type:
      type: enum
      enum:
        - term_loan        # 期間貸付
        - revolving_credit # RCF (回転信用枠)
        - venture_debt     # ベンチャーデット
        - rbf              # Revenue-based financing
        - jfc              # 政策金融公庫
        - convertible_debt # CB (転換社債、別途 §6 でも扱える)
        - mezzanine        # メザニン
        - shogun_bond      # 私募債 / 少人数私募
      source: 11 §1, §2
    lender_name:
      type: string
    lender_type:
      type: enum
      enum: ["megabank", "regional_bank", "credit_union", "jfc", "vc_debt_fund", "specialty_lender", "investor_individual"]
      source: 11 §3.1
    closing_date:
      type: string  # YYYY-MM-DD
    principal_jpy:
      type: int
      validation: x > 0
    interest_rate_pct:
      type: float
      validation: 0.0 <= x <= 25.0
      source: 11 §4.1
    interest_rate_type:
      type: enum
      enum: ["fixed", "floating_tibor_plus", "floating_libor_plus", "floating_sofr_plus"]
      default: "fixed"
    floating_spread_pct:
      type: float
      default: 0.0  # floating 時のみ
      validation: 0.0 <= x <= 10.0
    maturity_months:
      type: int
      validation: 1 <= n <= 120
    grace_period_months:
      type: int
      default: 0
      validation: 0 <= n <= 36
      source: 11 §4.2 (元本据置)
    amortization_method:
      type: enum
      enum: ["bullet", "equal_principal", "equal_payment", "step_up", "balloon"]
      default: "equal_principal"
      source: 11 §4.3
    balloon_pct:
      type: float
      default: 0.0  # balloon 時のみ
      validation: 0.0 <= x <= 100.0
    secured:
      type: bool
      default: false
    collateral_description:
      type: string
      validation: required if secured = true
    personal_guarantee:
      type: bool
      default: false
      source: 07 §7.2 (経営者保証)
    covenants:
      type: array of {covenant_type, threshold, frequency}
      default: []
      source: 11 §5
    warrant_attached:
      type: bool
      default: false  # venture debt で典型
    warrant_coverage_pct:
      type: float
      default: 0.0
      validation: 0.0 <= x <= 30.0
      source: 11 §6.1
    upfront_fee_pct:
      type: float
      default: 0.0
      validation: 0.0 <= x <= 5.0
      source: 11 §4.4
    rbf_revenue_share_pct:  # RBF 専用
      type: float
      default: 0.0
      validation: 0.0 <= x <= 20.0
      source: 11 §7
    rbf_cap_multiple:
      type: float
      default: 1.4
      validation: 1.0 <= x <= 3.0
      source: 11 §7.2
```

### 7.2 Covenant の表現

```yaml
covenants:
  type: array
  items:
    covenant_type:
      type: enum
      enum:
        - dscr_minimum            # Debt Service Coverage Ratio
        - leverage_maximum        # Debt / EBITDA 上限
        - liquidity_minimum_jpy   # 最低現預金
        - revenue_minimum_jpy     # 最低売上
        - tangible_net_worth_minimum
        - capex_maximum
      source: 11 §5.1
    threshold:
      type: float  # 単位は covenant_type に依存
    frequency:
      type: enum
      enum: ["monthly", "quarterly", "semi_annual", "annual"]
      default: "quarterly"
    cure_period_days:
      type: int
      default: 30
      validation: 0 <= n <= 90
```

### 7.3 政策金融公庫 (JFC) の特殊

- `lender_type: jfc`、`facility_type: jfc` で識別
- `interest_rate_pct` は **基準金利 1.5-2.5%** を default 範囲とする (07 §7.1、2024 年中小事業の特利水準)
- `personal_guarantee` は近年の経営者保証ガイドラインで **default false** (07 §7.2)
- `grace_period_months` は通常 12-24 が default (07 §7.3)

### 7.4 Mode 依存

| Mode | 必須 |
|---|---|
| Quick | debt なしを default。あれば `debt_facilities` に 1 件のみ summary 形式で受ける |
| Standard | facility 全件、ただし covenants は配列必須化しない |
| Comprehensive | facility + covenants 配列 + warrant + RBF 詳細 |

---

## 8. Validation Rules

> 出典: `01b §10` (Anti-pattern)、`06 §12` (Sanity rules)、`02 §13` (メトリクス改ざん検知)。

### 8.1 検証層の構造

3 段階で検証する:

1. **Schema-level (pydantic 自動)**: type / enum / regex / range
2. **Cross-field (本章 §8.2 - §8.3)**: hard fail / soft warn の意味的検証
3. **Business sanity (build_model.py 後段)**: 計算結果の最終 sanity (例: cash 残高が forecast 期間中に正)

### 8.2 Hard fail rules (build を停止する条件)

```yaml
hard_fails:
  - id: HF-001
    rule: "founder_share_pct + investor_share_pct + esop_pool_pct > 100"
    message: "Cap Table 合計が 100% を超過。各 share の比率を再確認してください。"
    source: "04b §1.4"

  - id: HF-002
    rule: "cash_on_hand_jpy < 0"
    message: "現預金が負値。BS の cash 計上を確認してください。"
    source: "06 §B"

  - id: HF-003
    rule: "tax_rate_pct < 0 or tax_rate_pct > 50"
    message: "実効税率が範囲外 (0-50%)。日本法定実効税率は 30.6% (2024)。"
    source: "12 §1"

  - id: HF-004
    rule: "any forecast year revenue growth_pct > 1000"
    message: "年次成長率が 1000% を超過。Pre-revenue→ early_revenue 移行期を除き、入力ミスの可能性。"
    source: "01b §10.3"

  - id: HF-005
    rule: "gross_margin_pct < -100 or gross_margin_pct > 100"
    message: "粗利率が範囲外 (-100% ~ 100%)。"
    source: "01b §10.1"

  - id: HF-006
    rule: "esop_pool_shares_issued > esop_pool_shares_authorized"
    message: "ESOP 発行済株数が authorize 数を超過。"
    source: "04b §3.2"

  - id: HF-007
    rule: "any preferred_rounds[].liquidation_preference_multiple > 3.0"
    message: "Liquidation preference が 3x を超過。市場標準 (1x) を大きく逸脱。"
    source: "04a §3.3"

  - id: HF-008
    rule: "any debt_facilities[].interest_rate_pct > 25"
    message: "金利が 25% を超過。利息制限法 (~20%) を確認してください。"
    source: "11 §4.1, 07 §7.4"

  - id: HF-009
    rule: "fiscal_year_end regex mismatch"
    message: "fiscal_year_end は MM-DD 形式 (例: 03-31) で指定してください。"
    source: "07 §2.1"

  - id: HF-010
    rule: "is_consolidated = true and parent_company_name is null"
    message: "連結の場合、親会社名が必須。"
    source: "13a §1"

  - id: HF-011
    rule: "business_model = 'saas' and arr_jpy is null and is_pre_revenue = false"
    message: "SaaS では ARR が必須 (Pre-revenue を除く)。"
    source: "02 §2"

  - id: HF-012
    rule: "model_start_date > 当月"
    message: "モデル開始月が未来。実数値開始を確認。"
    source: "06 §3"

  - id: HF-013
    rule: "headcount_split_pct sum != 100 (tolerance ±0.5)"
    message: "Headcount split の合計が 100% でない。"
    source: "06 §6.2"
```

### 8.3 Soft warn rules (警告のみ、build は継続)

```yaml
soft_warns:
  - id: SW-001
    rule: "ltv_cac_ratio < 1.0"
    message: "LTV/CAC < 1.0。Unit economics が成立していません。投資判断には致命的。"
    source: "02 §4.5"

  - id: SW-002
    rule: "burn_multiple > 3.0"
    message: "Burn multiple > 3.0。資本効率が低い (target <1.5)。"
    source: "02 §5.3"

  - id: SW-003
    rule: "magic_number < 0.5"
    message: "Magic Number < 0.5。営業効率が低い (target >0.7)。"
    source: "02 §5.2"

  - id: SW-004
    rule: "nrr_pct < 90"
    message: "NRR < 90%。Best-in-class は 120%+、Series A 期待値は 100%+。"
    source: "02 §3.4"

  - id: SW-005
    rule: "cac_payback_months > 24"
    message: "CAC payback > 24 か月。Series A 標準 <18 か月を超過。"
    source: "02 §4.4"

  - id: SW-006
    rule: "rule_of_40 < 0"
    message: "Rule of 40 が負。成長と収益性の和がマイナス。"
    source: "02 §5.4"

  - id: SW-007
    rule: "gross_margin_pct < 50 and business_model = 'saas'"
    message: "SaaS で粗利率 50% 未満。サービス比率が高い可能性 (Hybrid 検討)。"
    source: "02 §2.4, 03 §10"

  - id: SW-008
    rule: "ARR と employees の整合性 (§3.5 参照)"
    message: "ARR と従業員数が乖離。"
    source: "08 §3.1"

  - id: SW-009
    rule: "founder_share_pct < 30 at series_a"
    message: "Series A 時点で創業者比率 30% 未満は希薄化が進行しています。"
    source: "04b §2.3"

  - id: SW-010
    rule: "esop_pool_pct > 20"
    message: "ESOP プール 20% 超は通常 Series B 以降の水準。"
    source: "04b §3.1"

  - id: SW-011
    rule: "any safe_notes[].cap_jpy is null"
    message: "Uncapped SAFE が含まれます。希薄化計算で投資家有利になります。"
    source: "04a §2.3"

  - id: SW-012
    rule: "any debt_facilities[].interest_rate_pct > 15 and lender_type != 'specialty_lender'"
    message: "金利 15% 超は典型的な銀行レートではありません。lender type を確認。"
    source: "11 §4.1"

  - id: SW-013
    rule: "dscr_minimum covenant exists and forecast DSCR < 1.2"
    message: "DSCR forecast が covenant 下限 (1.2) を割る恐れがあります。"
    source: "11 §5.2"

  - id: SW-014
    rule: "is_pre_revenue = true and monthly_burn_jpy = 0"
    message: "Pre-revenue で burn が 0 は稀。Burn を確認してください。"
    source: "11 §3.2"
```

### 8.4 検証エラー出力形式

build_model.py は以下の JSON で結果を返す。CLI では同内容を日本語表で表示 (§12)。

```yaml
validation_result:
  status: enum [pass, warn, fail]
  hard_fails: list of {id, message, field_path, value}
  soft_warns: list of {id, message, field_path, value}
  filled_defaults: list of {field_path, default_value, source}
  meta:
    business_model: string
    funding_stage: string
    mode: string
    timestamp: ISO8601
```

---

## 9. Default 値テーブル (業態 × Stage)

> 出典: 各 reference のベンチマーク表。本表は **未入力 field の自動充填用** で、ユーザーが入力した値は常に優先される。値はいずれも **保守側 (悲観側)** を採用している。

### 9.1 SaaS (主要 KPI default)

| Field | pre_revenue | early_revenue | series_a | series_b | series_c | pre_ipo | Source ref |
|---|---|---|---|---|---|---|---|
| `gross_margin_pct` | 70 | 72 | 75 | 78 | 78 | 80 | 02 §2.4 |
| `nrr_pct` | -- | 100 | 110 | 115 | 120 | 120 | 02 §3.4 |
| `grr_pct` | -- | 85 | 90 | 92 | 92 | 93 | 02 §3.4 |
| `logo_churn_pct_annual` | -- | 15 | 8 | 6 | 5 | 4 | 02 §3.5 |
| `cac_payback_months` | -- | 24 | 18 | 15 | 12 | 12 | 02 §4.4 |
| `ltv_cac_ratio` | -- | 2.0 | 3.0 | 3.5 | 4.0 | 4.0 | 02 §4.5 |
| `magic_number` | -- | 0.4 | 0.7 | 0.9 | 0.9 | 1.0 | 02 §5.2 |
| `burn_multiple` | -- | 3.0 | 1.5 | 1.2 | 1.0 | 0.8 | 02 §5.3 |
| `growth_rate_pct_yoy` | -- | 200 | 100 | 80 | 60 | 40 | 02 §5.4, T2D3 |
| `s_and_m_pct_revenue` | -- | 60 | 50 | 45 | 40 | 35 | 02 §5.1 |
| `r_and_d_pct_revenue` | -- | 40 | 35 | 30 | 25 | 20 | 02 §5.1 |
| `g_and_a_pct_revenue` | -- | 25 | 20 | 17 | 15 | 12 | 02 §5.1 |

### 9.2 Marketplace (主要 KPI default)

| Field | early_revenue | series_a | series_b | series_c | Source ref |
|---|---|---|---|---|---|
| `take_rate_pct` | 12 | 15 | 17 | 18 | 03 §4.2 |
| `repeat_purchase_rate_pct` | 25 | 35 | 45 | 55 | 03 §4.6 |
| `liquidity_ratio` | 0.15 | 0.30 | 0.45 | 0.55 | 03 §4.5 |
| `gmv_growth_pct_yoy` | 200 | 120 | 80 | 50 | 03 §4.10 |
| `contribution_margin_pct` | 10 | 25 | 35 | 40 | 03 §4.8 |

### 9.3 D2C / E-commerce

| Field | early_revenue | series_a | series_b | series_c | Source ref |
|---|---|---|---|---|---|
| `gross_margin_pct` | 40 | 50 | 55 | 58 | 03 §5.2 |
| `aov_jpy` | 6000 | 8000 | 10000 | 12000 | 03 §5.3 |
| `repeat_purchase_rate_pct` | 20 | 30 | 40 | 50 | 03 §5.4 |
| `cac_payback_months` | 18 | 12 | 9 | 6 | 03 §5.6 |
| `contribution_margin_pct` | 10 | 25 | 32 | 38 | 03 §5.7 |
| `return_rate_pct` | 12 | 8 | 6 | 5 | 03 §5.8 |
| `inventory_turns_annual` | 4 | 6 | 8 | 10 | 03 §5.9 |

### 9.4 Fintech (Lending)

| Field | early_revenue | series_a | series_b | series_c | Source ref |
|---|---|---|---|---|---|
| `nim_pct` | 6 | 8 | 10 | 11 | 03 §6.4 |
| `npl_ratio_pct` | 5 | 3 | 2.5 | 2 | 03 §6.6 |
| `loss_rate_pct_annual` | 4 | 2 | 1.5 | 1.2 | 03 §6.7 |
| `cohort_lifetime_months` | 24 | 36 | 48 | 60 | 03 §6.9 |
| `regulatory_capital_pct` | 8 | 8 | 10 | 12 | 07 §9 |

### 9.5 Hardware / IoT

| Field | early_revenue | series_a | series_b | series_c | Source ref |
|---|---|---|---|---|---|
| `gross_margin_pct_hw` | 20 | 30 | 35 | 40 | 03 §7.2 |
| `gross_margin_pct_recurring` | 60 | 70 | 75 | 78 | 03 §7.2 |
| `bom_cost_pct_revenue` | 60 | 50 | 45 | 40 | 03 §7.3 |
| `inventory_turns_annual` | 3 | 4 | 5 | 6 | 03 §7.4 |
| `attach_rate_pct` | 30 | 60 | 75 | 85 | 03 §7.5 |
| `dio_days` | 120 | 90 | 75 | 60 | 06 §5.2 |

### 9.6 共通 default (全業態)

| Field | pre_revenue | early_revenue | series_a | series_b | series_c | pre_ipo | Source ref |
|---|---|---|---|---|---|---|---|
| `tax_rate_pct` | 0 (繰越欠損) | 0 (繰越欠損) | 30.6 | 30.6 | 30.6 | 30.6 | 12 §1, §3 |
| `dso_days` | 30 | 45 | 60 | 60 | 60 | 60 | 06 §5.2 |
| `dpo_days` | 30 | 30 | 45 | 45 | 50 | 50 | 06 §5.2 |
| `capex_pct_revenue` | 5 | 4 | 3 | 3 | 4 | 5 | 06 §B |
| `esop_pool_pct` | 10 | 10 | 12 | 15 | 18 | 18 | 04b §3.1 |
| `founder_share_pct` | 95 | 80 | 60 | 40 | 25 | 20 | 04b §2.3 |
| `headquarters_country` | JP | JP | JP | JP | JP | JP | -- |
| `fiscal_year_end` | 03-31 | 03-31 | 03-31 | 03-31 | 03-31 | 03-31 | 07 §2.1 |

### 9.7 Default 適用順序

1. ユーザー明示入力 (highest priority)
2. 業態 × Stage 表 (§9.1-§9.5) の値
3. 共通 default (§9.6) の値
4. Schema-level の field default (§4-§7 の `Default` 列)
5. Hard fallback (型ごとの空値: 0 / "" / [])

各 field に対して **どこから default を引いたか** は `validation_result.filled_defaults[].source` に記録される (§8.4)。

---

## 10. Schema 完全形 (YAML / JSON Schema / Pydantic)

### 10.1 Top-level YAML schema

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
title: "Startup Financial Model Input Schema (v1.0)"
type: object
required:
  - mode
  - business_model
  - funding_stage
  - company_name
  - founded_year
  - reporting_currency
properties:
  mode:
    type: string
    enum: [quick, standard, comprehensive]
  business_model:
    type: string
    enum: [saas, marketplace, d2c_ecommerce, fintech, hardware_iot, bio_pharma, media_content, b2b_services, manufacturing, real_estate, ai_foundation_model]
  secondary_business_model:
    type: [string, "null"]
    enum: [saas, marketplace, d2c_ecommerce, fintech, hardware_iot, bio_pharma, media_content, b2b_services, manufacturing, real_estate, ai_foundation_model, null]
  segment_revenue_split_pct:
    type: object
    additionalProperties:
      type: number
      minimum: 0
      maximum: 100
  funding_stage:
    type: string
    enum: [pre_revenue, early_revenue, series_a, series_b, series_c, pre_ipo, public]
  funding_stage_manual:
    type: [string, "null"]
  is_pre_revenue:
    type: boolean
    default: false
  company_profile:
    $ref: "#/$defs/CompanyProfile"
  forecast_config:
    $ref: "#/$defs/ForecastConfig"
  macro_assumptions:
    $ref: "#/$defs/MacroAssumptions"
  headcount:
    $ref: "#/$defs/Headcount"
  cap_table:
    $ref: "#/$defs/CapTable"
  debt_facilities:
    type: array
    items:
      $ref: "#/$defs/DebtFacility"
  business_metrics:
    $ref: "#/$defs/BusinessMetrics"
  cash_position:
    $ref: "#/$defs/CashPosition"
  # Phase 6 拡張 (§4.4-§4.6 参照)
  pricing:
    $ref: "#/$defs/Pricing"
  customer_value:
    $ref: "#/$defs/CustomerValue"
  exit:
    $ref: "#/$defs/Exit"
  design:
    $ref: "#/$defs/Design"
  meta:
    $ref: "#/$defs/Meta"
$defs:
  CompanyProfile:
    type: object
    required: [company_name, founded_year, headquarters_country, reporting_currency, fiscal_year_end]
    properties:
      company_name:
        type: string
        minLength: 1
        maxLength: 120
      company_legal_form:
        type: string
        enum: [kk, gk, llc, c_corp, foreign_other]
        default: kk
      founded_year:
        type: integer
        minimum: 1900
      headquarters_country:
        type: string
        pattern: "^[A-Z]{2}$"
        default: "JP"
      reporting_currency:
        type: string
        enum: [JPY, USD, EUR, GBP, CNY, SGD, KRW, TWD]
        default: JPY
      presentation_currency:
        type: string
        enum: [JPY, USD, EUR, GBP, CNY, SGD, KRW, TWD]
      fiscal_year_end:
        type: string
        pattern: "^(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$"
        default: "03-31"
      accounting_basis:
        type: string
        enum: [jgaap, ifrs, us_gaap]
        default: jgaap
      is_consolidated:
        type: boolean
        default: false
      parent_company_name:
        type: [string, "null"]

  ForecastConfig:
    type: object
    properties:
      forecast_period_years:
        type: integer
        minimum: 1
        maximum: 10
        default: 5
      forecast_granularity:
        type: string
        enum: [monthly, quarterly, annual, monthly_36_then_annual]
        default: monthly_36_then_annual
      historical_years_loaded:
        type: integer
        minimum: 0
        maximum: 10
        default: 3
      model_start_date:
        type: string
        pattern: "^\\d{4}-(0[1-9]|1[0-2])$"
      terminal_value_method:
        type: string
        enum: [gordon_growth, exit_multiple, h_model, none]
        default: gordon_growth
      terminal_growth_rate_pct:
        type: number
        minimum: -1.0
        maximum: 5.0
        default: 2.0
      discount_rate_method:
        type: string
        enum: [wacc, hurdle_rate, manual]
        default: wacc
      tax_rate_pct:
        type: number
        minimum: 0
        maximum: 50
        default: 30.6

  MacroAssumptions:
    type: object
    properties:
      fx_jpy_per_usd:
        type: number
        minimum: 50
        maximum: 300
        default: 150.0
      inflation_rate_pct:
        type: number
        minimum: -2.0
        maximum: 10.0
        default: 2.0
      risk_free_rate_pct:
        type: number
        minimum: 0
        maximum: 10.0
        default: 1.5
      equity_risk_premium_pct:
        type: number
        minimum: 3.0
        maximum: 10.0
        default: 6.0
      country_risk_premium_pct:
        type: number
        minimum: 0
        maximum: 15.0
        default: 0.0

  Headcount:
    type: object
    required: [employees]
    properties:
      employees:
        type: integer
        minimum: 1
        maximum: 10000
      headcount_split_pct:
        type: object
        properties:
          eng: {type: number}
          sales: {type: number}
          gna: {type: number}
          other: {type: number}
        required: [eng, sales, gna, other]
      avg_salary_jpy:
        type: integer
        minimum: 3000000
        maximum: 30000000
        default: 8000000
      payroll_burden_pct:
        type: number
        minimum: 10.0
        maximum: 25.0
        default: 16.5
      hiring_plan_growth_pct_yoy:
        type: number
        minimum: -50
        maximum: 300
        default: 50
      esop_pool_pct:
        type: number
        minimum: 0
        maximum: 30
        default: 10
      esop_grant_velocity_pct_yoy:
        type: number
        minimum: 0
        maximum: 5
        default: 1.5

  CapTable:
    type: object
    properties:
      total_shares_outstanding:
        type: integer
        minimum: 1
      founder_shares:
        type: integer
        minimum: 0
      common_pool_shares:
        type: integer
        minimum: 0
        default: 0
      esop_pool_shares_authorized:
        type: integer
        minimum: 0
      esop_pool_shares_issued:
        type: integer
        minimum: 0
      preferred_shares_total:
        type: integer
        minimum: 0
      n_founders:
        type: integer
        minimum: 1
        maximum: 10
        default: 2
      founder_share_pct:
        type: number
        minimum: 1
        maximum: 100
      par_value_jpy:
        type: number
        minimum: 0
        default: 1.0
      preferred_rounds:
        type: array
        items:
          $ref: "#/$defs/PreferredRound"
      safe_notes:
        type: array
        items:
          $ref: "#/$defs/SAFENote"
      option_grants:
        type: array
        items:
          $ref: "#/$defs/OptionGrant"

  PreferredRound:
    type: object
    required: [round_name, closing_date, shares_issued, price_per_share_jpy]
    properties:
      round_name:
        type: string
        enum: [seed, series_a, series_b, series_c, series_d, bridge, extension]
      closing_date:
        type: string
        format: date
      shares_issued:
        type: integer
        minimum: 1
      price_per_share_jpy:
        type: number
        exclusiveMinimum: 0
      pre_money_jpy:
        type: integer
      post_money_jpy:
        type: integer
      liquidation_preference_multiple:
        type: number
        minimum: 1.0
        maximum: 3.0
        default: 1.0
      participation:
        type: string
        enum: [non_participating, full_participating, capped_participating]
        default: non_participating
      participation_cap_multiple:
        type: number
        minimum: 1.0
        maximum: 5.0
      dividend_pct:
        type: number
        minimum: 0
        maximum: 15
        default: 0
      dividend_cumulative:
        type: boolean
        default: false
      anti_dilution:
        type: string
        enum: [none, full_ratchet, broad_based_weighted_average, narrow_based_weighted_average]
        default: broad_based_weighted_average
      voting_rights:
        type: string
        enum: [one_per_share, as_converted, special_class_voting]
        default: as_converted
      pay_to_play:
        type: boolean
        default: false
      redemption_right:
        type: boolean
        default: false

  SAFENote:
    type: object
    required: [note_id, instrument_type, principal_jpy]
    properties:
      note_id: {type: string}
      instrument_type:
        type: string
        enum: [safe_pre_money, safe_post_money, j_kiss, convertible_note]
      closing_date:
        type: string
        format: date
      principal_jpy:
        type: integer
        minimum: 1
      cap_jpy:
        type: [integer, "null"]
      discount_pct:
        type: number
        minimum: 0
        maximum: 50
        default: 20
      mfn_clause:
        type: boolean
        default: false
      interest_rate_pct:
        type: number
        minimum: 0
        maximum: 15
        default: 0
      maturity_date:
        type: [string, "null"]
        format: date
      conversion_trigger:
        type: string
        enum: [next_qualified_round, ipo, change_of_control, maturity]
        default: next_qualified_round
      conversion_minimum_round_size_jpy:
        type: integer
        default: 100000000
      pro_rata_right:
        type: boolean
        default: false

  OptionGrant:
    type: object
    required: [grant_id, shares_granted, grant_date, exercise_price_jpy]
    properties:
      grant_id: {type: string}
      grantee_role:
        type: string
        enum: [executive, engineer, sales, advisor, other]
      shares_granted:
        type: integer
        minimum: 1
      grant_date:
        type: string
        format: date
      exercise_price_jpy:
        type: number
        exclusiveMinimum: 0
      vesting_years:
        type: integer
        minimum: 1
        maximum: 10
        default: 4
      cliff_months:
        type: integer
        minimum: 0
        maximum: 36
        default: 12
      vesting_schedule:
        type: string
        enum: [monthly, quarterly, annual]
        default: monthly
      is_iso:
        type: boolean
        default: true
      early_exercise:
        type: boolean
        default: false

  DebtFacility:
    type: object
    required: [facility_id, facility_type, principal_jpy, interest_rate_pct, maturity_months]
    properties:
      facility_id: {type: string}
      facility_type:
        type: string
        enum: [term_loan, revolving_credit, venture_debt, rbf, jfc, convertible_debt, mezzanine, shogun_bond]
      lender_name: {type: string}
      lender_type:
        type: string
        enum: [megabank, regional_bank, credit_union, jfc, vc_debt_fund, specialty_lender, investor_individual]
      closing_date:
        type: string
        format: date
      principal_jpy:
        type: integer
        exclusiveMinimum: 0
      interest_rate_pct:
        type: number
        minimum: 0
        maximum: 25
      interest_rate_type:
        type: string
        enum: [fixed, floating_tibor_plus, floating_libor_plus, floating_sofr_plus]
        default: fixed
      floating_spread_pct:
        type: number
        minimum: 0
        maximum: 10
        default: 0
      maturity_months:
        type: integer
        minimum: 1
        maximum: 120
      grace_period_months:
        type: integer
        minimum: 0
        maximum: 36
        default: 0
      amortization_method:
        type: string
        enum: [bullet, equal_principal, equal_payment, step_up, balloon]
        default: equal_principal
      balloon_pct:
        type: number
        minimum: 0
        maximum: 100
        default: 0
      secured:
        type: boolean
        default: false
      collateral_description: {type: string}
      personal_guarantee:
        type: boolean
        default: false
      covenants:
        type: array
        items:
          $ref: "#/$defs/Covenant"
      warrant_attached:
        type: boolean
        default: false
      warrant_coverage_pct:
        type: number
        minimum: 0
        maximum: 30
        default: 0
      upfront_fee_pct:
        type: number
        minimum: 0
        maximum: 5
        default: 0
      rbf_revenue_share_pct:
        type: number
        minimum: 0
        maximum: 20
        default: 0
      rbf_cap_multiple:
        type: number
        minimum: 1.0
        maximum: 3.0
        default: 1.4

  Covenant:
    type: object
    required: [covenant_type, threshold]
    properties:
      covenant_type:
        type: string
        enum: [dscr_minimum, leverage_maximum, liquidity_minimum_jpy, revenue_minimum_jpy, tangible_net_worth_minimum, capex_maximum]
      threshold:
        type: number
      frequency:
        type: string
        enum: [monthly, quarterly, semi_annual, annual]
        default: quarterly
      cure_period_days:
        type: integer
        minimum: 0
        maximum: 90
        default: 30

  BusinessMetrics:
    type: object
    description: "業態に応じて schema-level で枝分かれ。pydantic discriminated union で実装。"
    oneOf:
      - $ref: "#/$defs/SaaSMetrics"
      - $ref: "#/$defs/MarketplaceMetrics"
      - $ref: "#/$defs/D2CMetrics"
      - $ref: "#/$defs/FintechMetrics"
      - $ref: "#/$defs/HardwareMetrics"

  SaaSMetrics:
    type: object
    properties:
      arr_jpy: {type: integer, minimum: 0}
      mrr_jpy: {type: integer, minimum: 0}
      n_customers: {type: integer, minimum: 0}
      arpu_jpy_per_month: {type: integer, minimum: 0}
      gross_margin_pct: {type: number, minimum: 0, maximum: 95}
      nrr_pct: {type: number, minimum: 50, maximum: 200}
      grr_pct: {type: number, minimum: 50, maximum: 100}
      logo_churn_pct_annual: {type: number, minimum: 0, maximum: 50}
      revenue_churn_pct_annual: {type: number, minimum: -50, maximum: 50}
      cac_jpy: {type: integer, minimum: 0}
      cac_payback_months: {type: number, minimum: 0, maximum: 60}
      ltv_jpy: {type: integer, minimum: 0}
      ltv_cac_ratio: {type: number, minimum: 0, maximum: 20}
      magic_number: {type: number, minimum: 0, maximum: 3}
      burn_multiple: {type: number, minimum: 0, maximum: 10}
      rule_of_40: {type: number, minimum: -100, maximum: 200}
      arr_by_cohort:
        type: array
        items:
          type: object
          properties:
            cohort_month: {type: string}
            arr_jpy: {type: integer}
      expansion_arr_pct_of_new: {type: number, minimum: 0, maximum: 200}
      pricing_tiers:
        type: array
        items:
          type: object
          properties:
            tier_name: {type: string}
            monthly_price_jpy: {type: integer}
            customer_count: {type: integer}
      usage_based_pct: {type: number, minimum: 0, maximum: 100}
      multi_year_contract_pct: {type: number, minimum: 0, maximum: 100}

  MarketplaceMetrics:
    type: object
    properties:
      gmv_jpy_annual: {type: integer, minimum: 0}
      take_rate_pct: {type: number, minimum: 0, maximum: 50}
      n_transactions_annual: {type: integer, minimum: 0}
      aov_jpy: {type: integer, minimum: 0}
      n_buyers_active: {type: integer, minimum: 0}
      n_sellers_active: {type: integer, minimum: 0}
      liquidity_ratio: {type: number, minimum: 0, maximum: 1}
      repeat_purchase_rate_pct: {type: number, minimum: 0, maximum: 100}
      cac_jpy: {type: integer, minimum: 0}
      contribution_margin_pct: {type: number, minimum: -50, maximum: 80}
      take_rate_volatility: {type: number, minimum: 0, maximum: 1}

  D2CMetrics:
    type: object
    properties:
      revenue_jpy_annual: {type: integer, minimum: 0}
      gross_margin_pct: {type: number, minimum: 10, maximum: 80}
      aov_jpy: {type: integer, minimum: 1000, maximum: 100000}
      n_orders_annual: {type: integer, minimum: 0}
      repeat_purchase_rate_pct: {type: number, minimum: 0, maximum: 100}
      n_customers_active_annual: {type: integer, minimum: 0}
      cac_jpy: {type: integer, minimum: 0}
      cac_payback_months: {type: number, minimum: 0, maximum: 36}
      contribution_margin_pct: {type: number, minimum: -20, maximum: 60}
      return_rate_pct: {type: number, minimum: 0, maximum: 50}
      inventory_turns_annual: {type: number, minimum: 1, maximum: 30}
      cohort_repeat_curve:
        type: array
        items:
          type: number
          minimum: 0
          maximum: 1

  FintechMetrics:
    type: object
    properties:
      fintech_subtype:
        type: string
        enum: [payments, lending, neobank, wealth, insurtech, crypto]
      tpv_jpy_annual: {type: integer, minimum: 0}
      take_rate_pct: {type: number, minimum: 0, maximum: 10}
      nim_pct: {type: number, minimum: 0, maximum: 30}
      loan_book_outstanding_jpy: {type: integer, minimum: 0}
      npl_ratio_pct: {type: number, minimum: 0, maximum: 30}
      loss_rate_pct_annual: {type: number, minimum: 0, maximum: 30}
      cac_jpy: {type: integer, minimum: 0}
      cohort_lifetime_months: {type: number, minimum: 6, maximum: 120}
      regulatory_capital_pct: {type: number, minimum: 0, maximum: 30}
      funding_cost_pct: {type: number, minimum: 0, maximum: 15}
      interchange_fee_pct: {type: number, minimum: 0, maximum: 3}

  HardwareMetrics:
    type: object
    properties:
      hw_revenue_jpy_annual: {type: integer, minimum: 0}
      recurring_revenue_jpy_annual: {type: integer, minimum: 0}
      gross_margin_pct_hw: {type: number, minimum: 5, maximum: 60}
      gross_margin_pct_recurring: {type: number, minimum: 30, maximum: 90}
      bom_cost_pct_revenue: {type: number, minimum: 10, maximum: 90}
      inventory_turns_annual: {type: number, minimum: 1, maximum: 12}
      attach_rate_pct: {type: number, minimum: 0, maximum: 100}
      recurring_arpu_jpy_per_month: {type: number, minimum: 100, maximum: 100000}
      recurring_churn_pct_annual: {type: number, minimum: 0, maximum: 50}
      warranty_cost_pct_revenue: {type: number, minimum: 0, maximum: 10}
      manufacturing_lead_time_days: {type: integer, minimum: 7, maximum: 365}
      dio_days: {type: integer, minimum: 30, maximum: 365}

  CashPosition:
    type: object
    required: [cash_on_hand_jpy, monthly_burn_jpy]
    properties:
      cash_on_hand_jpy: {type: integer, minimum: 0}
      monthly_burn_jpy: {type: integer, minimum: 0, maximum: 1000000000}
      dso_days: {type: integer, minimum: 0, maximum: 180, default: 60}
      dpo_days: {type: integer, minimum: 0, maximum: 180, default: 45}
      dio_days: {type: integer, minimum: 0, maximum: 365}
      capex_pct_revenue: {type: number, minimum: 0, maximum: 50, default: 3}
      depreciation_useful_life_years: {type: integer, minimum: 1, maximum: 50, default: 5}
      intangibles_amortization_years: {type: integer, minimum: 1, maximum: 20, default: 5}

  # Phase 6 拡張 (§4.4-§4.6 の binding contract)
  Pricing:
    type: object
    properties:
      pricing_model:
        type: string
        enum: [subscription, usage_based, outcome_based, hybrid, tiered, freemium, perpetual_license]
      scale_currency:
        type: string
        enum: [JPY, USD, EUR]
      scale_display:
        type: string
        enum: [actual, thousand, million, hundred_million]
        default: actual

  CustomerValue:
    type: object
    properties:
      customer_roi_annual_pct: {type: number, minimum: -0.5, maximum: 5.0}
      customer_roi_payback_months: {type: integer, minimum: 1, maximum: 60}
      gainsharing_pct: {type: number, minimum: 0, maximum: 1, default: 0.25}
      wtp_estimate_money_m: {type: number, minimum: 0}
      pricing_realization_pct: {type: number, minimum: 0.4, maximum: 1.2, default: 0.85}
      net_pricing_power_yoy: {type: number, minimum: -0.20, maximum: 0.30, default: 0.03}

  Exit:
    type: object
    properties:
      expected_exit_year: {type: integer, minimum: 2026, maximum: 2045}
      exit_pathway_probability:
        type: object
        properties:
          strategic_ma: {type: number, minimum: 0, maximum: 1, default: 0.6}
          ipo: {type: number, minimum: 0, maximum: 1, default: 0.2}
          pe_recap: {type: number, minimum: 0, maximum: 1, default: 0.15}
          no_exit: {type: number, minimum: 0, maximum: 1, default: 0.05}
        required: [strategic_ma, ipo, pe_recap, no_exit]
        # Validation: Σ = 1.0 ± 0.001 (§4.5 hard fail)
      acquirer_shortlist:
        type: array
        maxItems: 10
        items:
          type: object
          required: [name, type]
          properties:
            name: {type: string, minLength: 1, maxLength: 120}
            type:
              type: string
              enum: [strategic, financial, tuck_in]
            ev_multiple_estimate: {type: number, minimum: 0}
      founder_jurisdiction:
        type: string
        enum: [US_QSBS, US_NonQSBS, JP_Standard, JP_Reorg]
      qsbs_qualification_status:
        type: string
        enum: [legacy, post_obbba, non_qsbs, "n/a"]
        default: "n/a"
        # OBBBA (One Big Beautiful Bill Act) 2025-07-04 区分、`19 §13.2`
      expected_consideration_mix:
        type: object
        properties:
          cash_pct: {type: number, minimum: 0, maximum: 1}
          stock_pct: {type: number, minimum: 0, maximum: 1}
          earn_out_pct: {type: number, minimum: 0, maximum: 1}
        required: [cash_pct, stock_pct, earn_out_pct]
        # Validation: Σ = 1.0 ± 0.001 (§4.5 hard fail)
      expected_lockup_months: {type: integer, minimum: 0, maximum: 36, default: 12}
      expected_escrow_pct: {type: number, minimum: 0, maximum: 0.30, default: 0.15}
      expected_escrow_period_months: {type: integer, minimum: 6, maximum: 36, default: 18}

  Design:
    type: object
    properties:
      workbook_scale:
        type: string
        enum: [auto, thousand, million, hundred_million]
        default: auto
      workbook_currency:
        type: string
        enum: [JPY, USD]
      named_range_strategy:
        type: string
        enum: [workbook_scoped, sheet_scoped, hybrid]
        default: hybrid
      font_family: {type: string, default: "Calibri"}
      font_size_base: {type: integer, minimum: 9, maximum: 14, default: 11}
      enable_charts: {type: boolean, default: true}
      enable_data_validation: {type: boolean, default: true}
      enable_zebra_stripes: {type: boolean, default: false}

  Meta:
    type: object
    properties:
      stage_override_reason: {type: string}
      schema_version: {type: string, default: "1.0"}
      created_at: {type: string, format: date-time}
      created_by: {type: string}
```

### 10.2 Pydantic class skeleton

```python
# scripts/input_models.py — build_model.py が import する正本 schema
from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict


class Mode(str, Enum):
    quick = "quick"
    standard = "standard"
    comprehensive = "comprehensive"


class BusinessModel(str, Enum):
    saas = "saas"
    marketplace = "marketplace"
    d2c_ecommerce = "d2c_ecommerce"
    fintech = "fintech"
    hardware_iot = "hardware_iot"
    bio_pharma = "bio_pharma"
    media_content = "media_content"
    b2b_services = "b2b_services"
    manufacturing = "manufacturing"
    real_estate = "real_estate"
    ai_foundation_model = "ai_foundation_model"


class FundingStage(str, Enum):
    pre_revenue = "pre_revenue"
    early_revenue = "early_revenue"
    series_a = "series_a"
    series_b = "series_b"
    series_c = "series_c"
    pre_ipo = "pre_ipo"
    public = "public"


class CompanyProfile(BaseModel):
    company_name: str = Field(min_length=1, max_length=120)
    company_legal_form: Literal["kk", "gk", "llc", "c_corp", "foreign_other"] = "kk"
    founded_year: int = Field(ge=1900)
    headquarters_country: str = Field(default="JP", pattern=r"^[A-Z]{2}$")
    reporting_currency: Literal["JPY", "USD", "EUR", "GBP", "CNY", "SGD", "KRW", "TWD"] = "JPY"
    presentation_currency: Optional[Literal["JPY", "USD", "EUR", "GBP", "CNY", "SGD", "KRW", "TWD"]] = None
    fiscal_year_end: str = Field(default="03-31", pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    accounting_basis: Literal["jgaap", "ifrs", "us_gaap"] = "jgaap"
    is_consolidated: bool = False
    parent_company_name: Optional[str] = None


class SaaSMetrics(BaseModel):
    model_config = ConfigDict(extra="allow")
    arr_jpy: Optional[int] = Field(default=None, ge=0)
    mrr_jpy: Optional[int] = Field(default=None, ge=0)
    n_customers: Optional[int] = Field(default=None, ge=0)
    arpu_jpy_per_month: Optional[int] = Field(default=None, ge=0)
    gross_margin_pct: float = Field(default=75.0, ge=0, le=95)
    nrr_pct: float = Field(default=110.0, ge=50, le=200)
    grr_pct: float = Field(default=90.0, ge=50, le=100)
    logo_churn_pct_annual: float = Field(default=8.0, ge=0, le=50)
    revenue_churn_pct_annual: float = Field(default=5.0, ge=-50, le=50)
    cac_jpy: Optional[int] = Field(default=None, ge=0)
    cac_payback_months: float = Field(default=18.0, ge=0, le=60)
    ltv_jpy: Optional[int] = Field(default=None, ge=0)
    ltv_cac_ratio: float = Field(default=3.0, ge=0, le=20)
    magic_number: float = Field(default=0.7, ge=0, le=3)
    burn_multiple: float = Field(default=1.5, ge=0, le=10)
    rule_of_40: Optional[float] = Field(default=None, ge=-100, le=200)


# その他の Metrics class、CapTable / DebtFacility / Covenant / etc. も同様に定義。
# 全 class 定義は scripts/input_models.py に格納し、本書では skeleton のみ。

class StartupModelInput(BaseModel):
    """Top-level input. build_model.py のエントリポイント。"""
    mode: Mode
    business_model: BusinessModel
    secondary_business_model: Optional[BusinessModel] = None
    segment_revenue_split_pct: Optional[dict[str, float]] = None
    funding_stage: FundingStage
    funding_stage_manual: Optional[FundingStage] = None
    is_pre_revenue: bool = False
    company_profile: CompanyProfile
    # forecast_config, macro_assumptions, headcount, cap_table, debt_facilities,
    # business_metrics, cash_position, meta はそれぞれの class を参照
    # ...

    @model_validator(mode="after")
    def cross_field_checks(self):
        # §8.2 / §8.3 の rule をここで実装
        # 例: founder + investor + ESOP > 100% は HardFailError を raise
        # SaaS で arr_jpy is None かつ is_pre_revenue False なら HF-011
        return self
```

### 10.3 JSON Schema 配布形式

`scripts/schema/input_schema.v1.json` として上記 §10.1 の YAML を JSON 化したものを配布。`build_model.py` は `pydantic` 経由で同等検証をかけるが、外部利用 (CI / Excel template / 他言語) のために JSON Schema も維持する。

---

## 11. Routing 表 (Input → Reference Loading)

> 出典: 各 reference の自己宣言 + audit F の routing ニーズ (M-001)。

### 11.1 業態 × Stage の reference dispatch

`build_model.py` は `(business_model, funding_stage)` の組合せから **どの reference を sub-agent 経由で読み込むか** を以下の table で決定する。すべての case で共通必須とする reference は太字。

凡例:
- **00**: design guidelines
- **01a**: modeling standards
- **01b**: integrity / anti-patterns
- **02**: SaaS metrics
- **03**: business models
- **04a**: convertible / SAFE
- **04b**: cap table mechanics
- **05**: valuation / WACC
- **06**: three-statement
- **07**: Japan specifics
- **08**: investment thesis
- **09**: market sizing
- **10**: modeling craft
- **11**: debt financing
- **12**: tax strategy
- **13a**: consolidation core
- **13b**: treasury / carveout
- **14**: IPO readiness
- **15**: input schema (本書)

#### 11.1.1 SaaS

| Stage | 必読 references |
|---|---|
| pre_revenue | **00, 01a, 01b, 06, 09, 10**, 02, 04b |
| early_revenue | **00, 01a, 01b, 06, 09, 10**, 02, 04a, 04b, 08 |
| series_a | **00, 01a, 01b, 06, 09, 10**, 02, 03 §3, 04a, 04b, 05, 07, 08 |
| series_b | 上記 + 12 |
| series_c | 上記 + 11, 13a |
| pre_ipo | 上記 + 13b, 14 |

#### 11.1.2 Marketplace

| Stage | 必読 references |
|---|---|
| early_revenue | **00, 01a, 01b, 06, 09, 10**, 03 §4, 04a, 04b, 08 |
| series_a | 上記 + 02 §4-§5 (一部 metric 共通)、05, 07 |
| series_b/c | 上記 + 11, 12, 13a |
| pre_ipo | 上記 + 13b, 14 |

#### 11.1.3 D2C / E-commerce

| Stage | 必読 references |
|---|---|
| early_revenue | **00, 01a, 01b, 06, 09, 10**, 03 §5, 04b |
| series_a | 上記 + 04a, 05, 07, 08 |
| series_b/c | 上記 + 11 (在庫融資), 12 |
| pre_ipo | 上記 + 13a, 13b, 14 |

#### 11.1.4 Fintech

| Stage | 必読 references |
|---|---|
| early_revenue | **00, 01a, 01b, 06, 09, 10**, 03 §6, 04b, 07 §9 (金融業特有) |
| series_a | 上記 + 04a, 05, 08 |
| series_b/c | 上記 + 11, 12, 13a |
| pre_ipo | 上記 + 13b, 14 |

#### 11.1.5 Hardware / IoT

| Stage | 必読 references |
|---|---|
| early_revenue | **00, 01a, 01b, 06, 09, 10**, 03 §7, 04b |
| series_a | 上記 + 02 (recurring 部分のみ), 04a, 05, 07, 08 |
| series_b/c | 上記 + 11 (設備融資), 12 |
| pre_ipo | 上記 + 13a, 13b, 14 |

### 11.2 機械可読 dispatch dict (build_model.py 内に直接埋め込む)

```python
REFERENCE_ROUTING: dict[tuple[str, str], list[str]] = {
    ("saas", "pre_revenue"): ["00", "01a", "01b", "02", "04b", "06", "09", "10"],
    ("saas", "early_revenue"): ["00", "01a", "01b", "02", "04a", "04b", "06", "08", "09", "10"],
    ("saas", "series_a"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10"],
    ("saas", "series_b"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "12"],
    ("saas", "series_c"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a"],
    ("saas", "pre_ipo"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a", "13b", "14"],
    ("marketplace", "early_revenue"): ["00", "01a", "01b", "03", "04a", "04b", "06", "08", "09", "10"],
    ("marketplace", "series_a"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10"],
    ("marketplace", "series_b"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a"],
    ("marketplace", "pre_ipo"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a", "13b", "14"],
    ("d2c_ecommerce", "early_revenue"): ["00", "01a", "01b", "03", "04b", "06", "09", "10"],
    ("d2c_ecommerce", "series_a"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10"],
    ("d2c_ecommerce", "series_b"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12"],
    ("d2c_ecommerce", "pre_ipo"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a", "13b", "14"],
    ("fintech", "early_revenue"): ["00", "01a", "01b", "03", "04b", "06", "07", "09", "10"],
    ("fintech", "series_a"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10"],
    ("fintech", "series_b"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a"],
    ("fintech", "pre_ipo"): ["00", "01a", "01b", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a", "13b", "14"],
    ("hardware_iot", "early_revenue"): ["00", "01a", "01b", "03", "04b", "06", "09", "10"],
    ("hardware_iot", "series_a"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10"],
    ("hardware_iot", "series_b"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12"],
    ("hardware_iot", "pre_ipo"): ["00", "01a", "01b", "02", "03", "04a", "04b", "05", "06", "07", "08", "09", "10", "11", "12", "13a", "13b", "14"],
}

# 残り 6 業態は build phase 2 で拡充。Fallback として未定義組合せは
# ["00", "01a", "01b", "03", "06", "09", "10"] + (stage に応じて 04b, 05, 11, 12) を返す。
```

### 11.3 Skill loading 順序

`build_model.py` は上記 dispatch の結果を以下の順で読み込む:

1. `_terminology.md` (常時)
2. `15_input_schema.md` (本書、常時)
3. `00_design_guidelines.md` (常時)
4. `01a` / `01b` (常時)
5. その他 dispatch 結果の reference (順序は番号昇順)

> 順序は 00 (design) → 01 (standards) → 02-13 (domain) → 14 (IPO) → 15 (schema) としているため、上記 dispatch dict は **順序保存 (insertion-ordered list)** で扱う。

---

## 13. Example Input Sets

実装時の reference / fixture 用に、3 業態 × 3 Mode の代表例を提示する。すべて YAML 形式。`build_model.py` がこのまま受け取って xlsx を生成できるべき正本 sample。

### 13.1 Example 1: SaaS Series A (Quick mode)

```yaml
mode: quick
business_model: saas
funding_stage: series_a   # auto-judge から確定
is_pre_revenue: false

company_profile:
  company_name: "Acme SaaS 株式会社"
  founded_year: 2022
  headquarters_country: JP
  reporting_currency: JPY
  fiscal_year_end: "03-31"

forecast_config:
  forecast_period_years: 5

headcount:
  employees: 35
  esop_pool_pct: 12.0

cap_table:
  founder_share_pct: 55.0

cash_position:
  cash_on_hand_jpy: 350_000_000
  monthly_burn_jpy: 25_000_000

business_metrics:
  arr_jpy: 720_000_000        # ARR ~$4.8M (Series A レンジ)
  nrr_pct: 115.0
  cac_payback_months: 16
```

> 14 field のみ。残りは §9 の SaaS × series_a default で自動充填される (gross_margin_pct=75, magic_number=0.7, burn_multiple=1.5, etc.)。

### 13.2 Example 2: Marketplace Series B (Standard mode)

```yaml
mode: standard
business_model: marketplace
funding_stage: series_b
is_pre_revenue: false

company_profile:
  company_name: "BridgeHub 株式会社"
  company_legal_form: kk
  founded_year: 2019
  headquarters_country: JP
  reporting_currency: JPY
  presentation_currency: JPY
  fiscal_year_end: "12-31"
  accounting_basis: jgaap
  is_consolidated: false

forecast_config:
  forecast_period_years: 5
  forecast_granularity: monthly_36_then_annual
  historical_years_loaded: 3
  model_start_date: "2026-05"
  terminal_value_method: gordon_growth
  terminal_growth_rate_pct: 2.0
  discount_rate_method: wacc
  tax_rate_pct: 30.6

macro_assumptions:
  fx_jpy_per_usd: 150.0
  inflation_rate_pct: 2.0
  risk_free_rate_pct: 1.5
  equity_risk_premium_pct: 6.0

headcount:
  employees: 110
  headcount_split_pct: {eng: 45, sales: 30, gna: 15, other: 10}
  avg_salary_jpy: 8_500_000
  payroll_burden_pct: 16.5
  hiring_plan_growth_pct_yoy: 40
  esop_pool_pct: 15.0

cap_table:
  total_shares_outstanding: 1_500_000
  founder_shares: 600_000
  esop_pool_shares_authorized: 225_000
  esop_pool_shares_issued: 110_000
  preferred_shares_total: 565_000
  founder_share_pct: 40.0
  n_founders: 2
  preferred_rounds:
    - round_name: seed
      closing_date: "2020-06-15"
      shares_issued: 150_000
      price_per_share_jpy: 800.0
      pre_money_jpy: 800_000_000
      post_money_jpy: 920_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_a
      closing_date: "2022-09-30"
      shares_issued: 200_000
      price_per_share_jpy: 4_500.0
      pre_money_jpy: 5_400_000_000
      post_money_jpy: 6_300_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_b
      closing_date: "2024-11-20"
      shares_issued: 215_000
      price_per_share_jpy: 16_000.0
      pre_money_jpy: 20_000_000_000
      post_money_jpy: 23_440_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average

debt_facilities:
  - facility_id: jfc-2023
    facility_type: jfc
    lender_name: "日本政策金融公庫"
    lender_type: jfc
    closing_date: "2023-04-01"
    principal_jpy: 100_000_000
    interest_rate_pct: 1.8
    interest_rate_type: fixed
    maturity_months: 84
    grace_period_months: 12
    amortization_method: equal_principal
    secured: false
    personal_guarantee: false

business_metrics:
  gmv_jpy_annual: 18_000_000_000
  take_rate_pct: 17.0
  n_transactions_annual: 2_400_000
  aov_jpy: 7_500
  n_buyers_active: 380_000
  n_sellers_active: 12_500
  liquidity_ratio: 0.42
  repeat_purchase_rate_pct: 48.0
  cac_jpy: 1_800
  contribution_margin_pct: 32.0

cash_position:
  cash_on_hand_jpy: 5_200_000_000
  monthly_burn_jpy: 180_000_000
  dso_days: 30           # marketplace は支払 sweep が早い
  dpo_days: 45
  capex_pct_revenue: 2.0

meta:
  schema_version: "1.0"
  created_at: "2026-05-01T09:00:00+09:00"
  created_by: "shayashi@xo-street.com"
```

### 13.3 Example 3: Fintech Pre-IPO with Holdco (Comprehensive mode)

```yaml
mode: comprehensive
business_model: fintech
secondary_business_model: saas       # SaaS API 提供も持つ Hybrid
segment_revenue_split_pct:
  fintech: 78.0
  saas: 22.0
funding_stage: pre_ipo
is_pre_revenue: false

company_profile:
  company_name: "FinForge ホールディングス株式会社"
  company_legal_form: kk
  founded_year: 2016
  headquarters_country: JP
  reporting_currency: JPY
  presentation_currency: JPY
  fiscal_year_end: "03-31"
  accounting_basis: ifrs              # IPO 申請に向け IFRS 採用
  is_consolidated: true
  parent_company_name: "FinForge ホールディングス株式会社"

forecast_config:
  forecast_period_years: 7            # IPO + 上場後 2 期
  forecast_granularity: monthly_36_then_annual
  historical_years_loaded: 5
  model_start_date: "2026-05"
  terminal_value_method: exit_multiple
  discount_rate_method: wacc
  tax_rate_pct: 30.6

macro_assumptions:
  fx_jpy_per_usd: 150.0
  inflation_rate_pct: 2.0
  risk_free_rate_pct: 1.5
  equity_risk_premium_pct: 6.0
  country_risk_premium_pct: 0.0

headcount:
  employees: 480
  headcount_split_pct: {eng: 40, sales: 25, gna: 25, other: 10}
  avg_salary_jpy: 9_500_000
  payroll_burden_pct: 16.5
  hiring_plan_growth_pct_yoy: 25
  esop_pool_pct: 18.0
  esop_grant_velocity_pct_yoy: 1.5

cap_table:
  total_shares_outstanding: 50_000_000
  founder_shares: 12_500_000
  esop_pool_shares_authorized: 9_000_000
  esop_pool_shares_issued: 6_200_000
  preferred_shares_total: 28_500_000
  founder_share_pct: 25.0
  n_founders: 3
  preferred_rounds:
    - round_name: seed
      closing_date: "2017-01-15"
      shares_issued: 5_000_000
      price_per_share_jpy: 200.0
      pre_money_jpy: 1_000_000_000
      post_money_jpy: 2_000_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_a
      closing_date: "2019-06-01"
      shares_issued: 6_000_000
      price_per_share_jpy: 800.0
      pre_money_jpy: 8_000_000_000
      post_money_jpy: 12_800_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_b
      closing_date: "2021-09-01"
      shares_issued: 7_500_000
      price_per_share_jpy: 4_000.0
      pre_money_jpy: 50_000_000_000
      post_money_jpy: 80_000_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_c
      closing_date: "2023-11-01"
      shares_issued: 8_000_000
      price_per_share_jpy: 12_500.0
      pre_money_jpy: 200_000_000_000
      post_money_jpy: 300_000_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
    - round_name: series_d
      closing_date: "2025-08-01"
      shares_issued: 2_000_000
      price_per_share_jpy: 25_000.0
      pre_money_jpy: 480_000_000_000
      post_money_jpy: 530_000_000_000
      liquidation_preference_multiple: 1.0
      participation: non_participating
      anti_dilution: broad_based_weighted_average
  safe_notes: []   # Series A 以降は preferred のみ
  option_grants: []  # 別 file (option_grants.csv) で 200+ 件管理

debt_facilities:
  - facility_id: rcf-megabank-2024
    facility_type: revolving_credit
    lender_name: "三井住友銀行"
    lender_type: megabank
    closing_date: "2024-04-01"
    principal_jpy: 5_000_000_000
    interest_rate_pct: 1.5
    interest_rate_type: floating_tibor_plus
    floating_spread_pct: 0.8
    maturity_months: 36
    grace_period_months: 0
    amortization_method: bullet
    secured: true
    collateral_description: "売掛債権・特定預金"
    personal_guarantee: false
    covenants:
      - covenant_type: dscr_minimum
        threshold: 1.5
        frequency: quarterly
        cure_period_days: 30
      - covenant_type: leverage_maximum
        threshold: 3.0
        frequency: quarterly
  - facility_id: term-loan-megabank-2025
    facility_type: term_loan
    lender_name: "三菱 UFJ 銀行"
    lender_type: megabank
    closing_date: "2025-02-15"
    principal_jpy: 8_000_000_000
    interest_rate_pct: 1.9
    interest_rate_type: fixed
    maturity_months: 60
    grace_period_months: 6
    amortization_method: equal_principal
    secured: false
    personal_guarantee: false

business_metrics:
  fintech_subtype: payments
  tpv_jpy_annual: 850_000_000_000
  take_rate_pct: 1.4
  nim_pct: 0.0                # payments 主体
  loan_book_outstanding_jpy: 0
  npl_ratio_pct: 0.0
  loss_rate_pct_annual: 0.3   # chargeback / fraud
  cac_jpy: 4_500
  cohort_lifetime_months: 60
  regulatory_capital_pct: 8.0
  funding_cost_pct: 1.8
  interchange_fee_pct: 1.0

cash_position:
  cash_on_hand_jpy: 35_000_000_000
  monthly_burn_jpy: 0          # FCF positive
  dso_days: 5                  # payment processor は売掛回収早い
  dpo_days: 30
  dio_days: 0
  capex_pct_revenue: 4.0
  depreciation_useful_life_years: 5
  intangibles_amortization_years: 5

meta:
  stage_override_reason: "ARR は SaaS segment のみ $80M、payment volume 連結で pre_ipo 妥当"
  schema_version: "1.0"
  created_at: "2026-05-01T10:30:00+09:00"
  created_by: "shayashi@xo-street.com"
```

### 13.4 Fixture としての利用

これら 3 example は `tests/fixtures/input/` に配置し、`build_model.py` の regression test に利用する:

```
tests/fixtures/input/
  example_01_saas_series_a_quick.yaml
  example_02_marketplace_series_b_standard.yaml
  example_03_fintech_pre_ipo_comprehensive.yaml
```

各 fixture は **schema validation pass** + **builder スクリプトが xlsx を生成成功** + **生成された xlsx の sanity check pass** の 3 条件を満たすこと。

---

## 付録: Cross-reference matrix

本書と他 reference の対応関係を簡易 matrix で示す。本書を読む際の navigation 用。

| 本書 §  | 主たる対応 reference | 役割 |
|---|---|---|
| §1 (Mode) | 01a §3.2 / §4 | 入力深度の段階分け |
| §2 (Business model) | 03 §1, §11 | 11 業態の enum と判定フロー |
| §3 (Stage) | 08 §3.1 | Stage 判定の ARR/評価額 table |
| §4 (Common fields) | 01a, 06, 07, 12 | 全業態共通の forecast / company / tax |
| §5.1 (SaaS) | 02 §1-§7 | SaaS 全 KPI |
| §5.2 (Marketplace) | 03 §4 | GMV / Take rate |
| §5.3 (D2C) | 03 §5 | AOV / Repeat |
| §5.4 (Fintech) | 03 §6, 07 §9 | TPV / NIM / NPL |
| §5.5 (Hardware) | 03 §7 | BOM / Inventory |
| §6 (Cap Table) | 04a, 04b | SAFE / Preferred / ESOP |
| §7 (Debt) | 11 全章, 07 §7 | Term loan / RCF / VD / RBF / JFC |
| §8 (Validation) | 01b §10, 06 §12, 02 §13 | Anti-pattern / Sanity / 改ざん検知 |
| §9 (Defaults) | 各 reference のベンチマーク | 業態 × Stage default |
| §10 (Schema) | -- | 本書独自 (pydantic + JSON Schema) |
| §11 (Routing) | 各 reference 全体 | Sub-agent 経由の reference loading 表 |
| §12 (i18n) | -- | 本書独自 (日本語 error message) |
| §13 (Examples) | -- | 本書独自 (fixture sample) |
| §14 (Integration) | -- | 本書独自 (build_model.py 統合手順) |

---

**End of 15_input_schema.md (v1.0).**

