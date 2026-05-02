---
name: terminology
description: SSoT (Single Source of Truth) for cross-file consistency. Resolves audit Critical issues A-C-001..006 + D-C-001. All other references defer here for terminology, color, naming conventions.
type: reference
priority: P0
---

# Terminology & SSoT (Single Source of Truth)

このドキュメントは reference 群 横断の **正本**。用語・色・名称・数値で 2 file 以上に同概念が現れる場合、この file の定義を **canonical** とする。

## 1. IB Functional Color (機能色) — A-C-001 解消

| 役割 | HEX | 適用範囲 |
|---|---|---|
| Hard input | `#0000FF` | ユーザー入力セル (canonical) |
| Formula | `#000000` | 数式セル |
| Cross-sheet link | `#008000` | シート間参照 |
| External link | `#FF0000` | 外部 file 参照 |
| Comment | `#666666` | 注記 (italic) |

**rationale**: IB 業界標準。`01b §6 / §A.6` の「hard input = `#004F49`」記述は誤り、`#0000FF` に統一。`#004F49` (Act Primary deep) は **branding 用途のみ** (Cover sheet header band 等) に限定。

## 2. Brand Color (Act ブランド) — A-C-002 解消

| 役割 | HEX | 適用範囲 |
|---|---|---|
| Surface (背景) | `#ECE9E1` | 限定 (Cover sheet 背景のみ) |
| Ink (主テキスト) | `#2D332E` | Cover sheet タイトル |
| Primary | `#008A80` | Cover sheet 強調 1 か所 |
| Primary deep | `#004F49` | Cover sheet タブ色 + 限定強調 |
| Accent | `#ECC85A` | 1 sheet 1 か所まで |

**rationale**: Cover タブ色は Primary deep `#004F49` に統一 (`01a §5.1` の「黒」を上書き)。他 tab は Excel 既定色 (no fill)。

## 3. Sheet Naming Convention — A-C-006 解消

**Canonical sheet 順** (Phase 6 Stage A 後、14-sheet layout):

```
00_Cover            (モデル概要)
01_Assumptions      (ハードインプット)
02_Revenue          (収益モデル)
03_OpEx             (費用モデル)
04_IS               (損益計算書 = Income Statement)
05_BS               (貸借対照表 = Balance Sheet — 旧 08_WC を Working Capital Schedule sub-section として吸収)
06_CFS              (キャッシュフロー計算書 = Cash Flow Statement)
07_Debt             (借入スケジュール)
08_CapTable         (資本政策)
09_DCF              (DCF バリュエーション — 旧 13_Sensitivity を Sensitivity & Stress sub-section として吸収)
10_Comps            (比較分析)
11_KPI_Dashboard    (KPI 可視化 — 旧 02_Drivers の driver display 機能を代替)
12_SanityChecks     (整合性監査)
13_IC_Memo          (投資判断サマリ)
99_Glossary         (用語集 — optional)
```

**rationale**: `01a` の旧仕様 (`11_PL`, `12_BS`, `98_Checks`) と `06/11` の (`IS, BS, CFS, SanityChecks, DebtSchedule`) を統合。Phase 6 Stage A で 17 sheet → 14 sheet に集約 (`02_Drivers` `08_WC` `13_Sensitivity` を吸収)。**ファイル全体でこれを参照すべし**。canonical SSoT は `scripts/ib_format._OLD_TO_NEW_SHEET_MAP`。

## 4. SAFE Discount Rate — A-C-003 解消

`Discount Rate` = **割引率の絶対値** として記述。

| 表現 | 意味 |
|---|---|
| Discount = 0.20 | 20% off (multiply by 0.80 to get conversion price) |
| Discount = 20% | 同上 |
| Discount Factor | 0.80 (= 1 − Discount) を指す場合は明示 |

**SAFE 転換式 (canonical)**:
```
Conversion Price = Next Round Price × (1 − Discount)
                 = Next Round Price × 0.80   (Discount = 20% の場合)
```

**rationale**: `04a` で `0.20` と `0.80` が混在し SAFE 株式数が 4倍ズレ得る。本 file で「Discount = 割引率絶対値」に統一。Discount Factor を使う場合は別変数 `DF = 1 - Discount` と明示。

## 5. J-KISS バージョン — D-C-001 解消

| バージョン | 公開時期 | 主要変更 |
|---|---|---|
| v1.0 | 2016-04 | 初版、利息条項あり (年 1%)、pre-money cap |
| v1.1 | 2017 | 軽微な文言修正 |
| **v2.0** | **2022-04** | **post-money cap、利息条項削除、Series A 経済条件整合** |
| v2 派生 | 2023〜 | bridge / cap only / discount only バリエーション |

**rationale**: `04a §1.2 (line 52)` 旧記述「2020 (v2.0)」を 2022-04 に修正済。`07 §3.1` と整合。

## 6. SaaS メトリクス定義 — A-C-005 解消 (A-H-005/006/016 統合)

### 6.1 Canonical 式と PASS/WATCH/FAIL 閾値

| Metric | Canonical 式 | PASS | WATCH | FAIL | 注 |
|---|---|---|---|---|---|
| ARR | Committed ARR (契約時点) | — | — | — | Reported ARR と区別 |
| MRR | ARR / 12 (subscription only) | — | — | — | usage 含めない |
| NRR / NDR | (期初 ARR + Expansion - Contraction - Churn) / 期初 ARR | > 120% (Mid) / > 110% (PLG) | 100-120% | < 100% | Method A (期初 cohort) を canonical |
| GRR | (期初 ARR - Contraction - Churn) / 期初 ARR | > 90% | 85-90% | < 85% | expansion 除外 |
| LTV | Method B (cohort, T=5y) を canonical | — | — | — | Method A (simple) は NRR < 100% でのみ valid |
| CAC | (S&M 全額 fully loaded) / (新規顧客数) | — | — | — | blended vs paid 区別 |
| LTV/CAC | 上記 LTV / CAC | > 3x | 1-3x | < 1x | method = cohort with T=5y |
| CAC Payback | CAC / (ARPU × Gross Margin / 12) ヶ月 | < 12 mo | 12-18 mo | > 24 mo | enterprise は緩和可 |
| **Magic Number** | **(Net New ARR × 4) / S&M (前 quarter)**  ← 必ず ×4 で年率化 | > 1.0 | 0.4-1.0 | < 0.4 | quarterly-annualized 値、月次データに ×12 はしない |
| Burn Multiple | Net Burn / Net New ARR | < 1.5x | 1.5-2x | > 2x | ARR < $100K では未定義 (`08 §4.1.7` 参照) |
| **Rule of 40** | **Revenue Growth % + FCF Margin %** ← canonical (FCF margin、SBC 含む) | > 40 | 20-40 | < 20 | EBITDA margin / Operating margin (SBC 抜き) を使う場合は明示注記必須 |

### 6.2 ARR ステージ別レンジ (A-H-016 解消、`02 §2.1` を canonical)

| Stage | ARR レンジ (canonical) |
|---|---|
| Series A 入口 | $1.0 - 3.0M |
| Series A → B 移行 | $5 - 10M |
| Series B → C 移行 | $15 - 30M |
| Late stage | $50M+ |

出典: OpenView / Tunguz / KeyBanc。`08 §3.1`、`10 §2.4` / §11.3 はこのレンジを参照する (file 内独自値を持たない)。Stage は ARR 単独で決まらず、調達履歴・成長率も補助シグナル。

### 6.3 Magic Number 計算注意 (A-H-005 解消)

`Magic Number` は **quarterly-annualized 値で計算する**。式: `(Rev_q − Rev_{q-1}) × 4 / S&M_{q-1}`、または ARR ベースで `Net New ARR / S&M_{q-1}` (年率 ARR は既に annualized)。**月次データを `×12` で annualize して計算しない**。`10 §2.1` の quartile 表 (Bottom 25% 0.4 / Median 0.7 / Top 25% 1.1 / Top 5% 1.5+) は `02 §5.1` の式で算出した値に対応。

### 6.4 Snowflake NRR 例 (canonical 数値)

FY24 Q4 = **131%**、FY25 Q2 = 127%。各 file で「150%」「178%」表記は **2022 年時点** のものとして「(2022)」注記必須、または削除。

## 7. 法人実効税率 (日本)

| 区分 | 実効税率 | 内訳 |
|---|---|---|
| 大企業 (2026 年度〜) | **31.52%** | 法人税 23.2% + 地方法人税 1.52% + 法人住民税 1.62% + 法人事業税 5.18% + 防衛特別法人税 |
| 中小企業 (年所得 800万円以下部分) | 約 21% | 軽減税率 15% + 地方 |

**rationale**: 2026.4 開始の防衛特別法人税を反映。`07 §2.1` を canonical。

## 8. 日米英会計用語

| 日本語 | 英語 | 略 |
|---|---|---|
| 損益計算書 | Income Statement | IS / P&L |
| 貸借対照表 | Balance Sheet | BS |
| キャッシュフロー計算書 | Cash Flow Statement | CFS / CF |
| 営業利益 | Operating Income | OI |
| 当期純利益 | Net Income | NI |
| 売上総利益 | Gross Profit | GP |
| 自己資本 | Shareholders' Equity | SE |
| 純資産 | Net Assets / Total Equity | TE |
| 内部留保 | Retained Earnings | RE |
| 非支配持分 | Non-Controlling Interest | NCI |
| 累積為替換算調整 | Cumulative Translation Adjustment | CTA |
| のれん | Goodwill | GW |
| 繰延税金資産 | Deferred Tax Asset | DTA |
| 繰延税金負債 | Deferred Tax Liability | DTL |

## 9. 借入指標

| 指標 | 式 | 典型値 |
|---|---|---|
| Leverage | Total Debt / EBITDA | < 4-6x |
| Net Debt | Total Debt - Cash & equivalents | |
| ICR | EBITDA / Interest | > 2-3x |
| FCCR | (EBITDA - CapEx) / (Interest + Principal + Lease) | > 1.0-1.2x |
| DSCR | CFADS / Debt Service | > 1.2x |

**rationale**: `06 §4` と `11 §4` で異なる式が並走するのを統一。

## 10. Diluted Share Count

**Treasury Stock Method (TSM)**:
- ITM (in-the-money) options のみ
- Strike × N_options を市場価格で買い戻し相当株数控除
- Restricted Stock は full count
- Convertible 全部 if-converted

`04b §1.3` を canonical。

---

## 適用ルール

1. 他 reference は本 file の定義を **直接引用** または **本 file を参照する明示** すること
2. 本 file と矛盾する記述を見つけた場合、修正は本 file 定義に合わせる (本 file 自体を修正する場合は理由を本 file の History に記載)
3. 新規 reference 追加時、新規用語は本 file に登録 → 他 reference で利用
