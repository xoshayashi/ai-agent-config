---
name: named_ranges
description: 14-sheet xlsx モデル全体で使用する named range の canonical 命名規約。line item 単位の cross-sheet 参照を行/列追加耐性のある名前ベース参照で実装する正本。Phase 6 refactor (Wave 1 — Option A) の SSoT
type: reference
priority: P0
related: [_terminology, 00_design_guidelines, 06_three_statement, 04b_cap_table_mechanics, 05_valuation_wacc, 17_chart_design]
---

# Named Ranges — Canonical 命名規約 (Phase 6 Refactor Wave 1)

このドキュメントは 14-sheet xlsx 財務モデル全体 (Phase 6 Stage A 後 canonical layout) の **named range (定義された名前) 命名規約** の正本である。`three_statement_builder.py` / `cap_table_builder.py` / `valuation_builder.py` の 3 builder で **絶対 cell anchor** (`='02_Revenue'!$C$5`) を hard-code していた cross-sheet 参照を、**named range** ベース (`=Rev_Total`) に refactor するための SSoT。

## このドキュメントの位置づけ

- **正本 (SSoT)**: 全 named range の名前・scope・対応 cell の対応表は本書を canonical とする。色・sheet name の SSoT は [`_terminology.md`](_terminology.md) §1-3
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) (構築) で「cross-sheet 参照を書く」場面に達したら、まず本書 §2 の table を引き、cell anchor 直書きでなく named range で書く
- **Self-review 連携**: 本書を適用した builder 出力は、[`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check に「行挿入耐性 self-test」を 6 番目として追加 (本書 §4 mini case を template に使用)
- **関連 reference**:
  - `_terminology.md §3` — sheet 名 (`00_Cover` ... `13_IC_Memo`) を正本として使用
  - `00_design_guidelines.md` — 機能色 (#0000FF / #008000) と独立 (named range は名前のみ、表示色は別軸)
  - `06_three_statement.md §2` — 各 sheet の row 構成 (Revenue B5 / IS Revenue D5 等) と本書 §2 の対応表は **相互整合**
  - `04b_cap_table_mechanics.md` — Cap_FDSO 等の named range が DCF / Valuation で使われる
  - `05_valuation_wacc.md` — DCF_FCFF / DCF_PV_TV / DCF_EV を valuation builder で使用
  - `17_chart_design.md` — KPI Dashboard / Football field のチャートが KPI_RuleOf40 / DCF_PerShare 等を name 経由で参照

---

## 0. なぜ named range か (TL;DR)

現状 (Phase 5 まで) は cross-sheet 参照が **絶対 cell anchor** で hard-code されている:

```python
# scripts/three_statement_builder.py (現状)
ws_is["D5"] = f"='02_Revenue'!$D$5"   # IS の Revenue 行 = 02_Revenue の D5
```

この設計には 2 つの致命的脆弱性がある:

1. **行挿入で意味が壊れる**: ユーザーが Excel で「Hardware revenue 行を B5 と B6 の間に追加」しても、`'02_Revenue'!$D$5` の参照は **動かない** (`$` 固定)。新しく挿入された行を指すか、元の意味 (Subscription Revenue) を指すかは Excel の挿入挙動次第で、特に **同じ sheet 内** ならば cell anchor は auto-shift するが、**他 sheet からの絶対参照は shift しない** (実装依存)。
2. **列追加で破綻する**: period 列が D-G (Y1-Y4) から D-H (Y1-Y5) に変わったとき、forecast 列の各 row 末尾の formula が古い列範囲のまま残る。

**named range** にすると Excel/openpyxl が **自動的に shift** する (sheet-scoped name の場合 row/col insertion 時に reference cell が auto-adjust)。さらに副次的利点:

- formula が **意味的に読める** (`=Rev_Total` は意図が自明、`='02_Revenue'!$D$5` は cell coord を覚える必要がある)
- sheet rename しても name は不変 (sheet 名 hard-code を 0 に削減)
- builder の Python code に sheet-cell の物理座標が **散らばらず**、本書 §2 table 1 か所で集約管理できる

---

## 1. 設計原則

### 1.1 Sheet-scoped vs Workbook-scoped の選定基準

| 項目 | Sheet-scoped | Workbook-scoped |
|---|---|---|
| 衝突許容 | 同名を別 sheet で使用可 | 全 workbook 一意 |
| 参照記法 | 同 sheet 内: `=Rev_Subscription` / 他 sheet から: `='02_Revenue'!Rev_Subscription` | どこからでも `=Rev_Total` |
| 用途 | sheet 内部で閉じる中間値 (例: 02_Revenue の Subscription/Services 内訳) | 14 sheet で共通参照される基幹値 (例: Total Revenue, Net Income) |
| 行/列 insertion | 同 sheet 内 row/col 挿入で auto-shift | 同左 (定義 cell の shift は同じ) |
| 推奨 default | **Sheet-scoped** を default | cross-sheet aggregator のみ workbook-scoped |

**判定ルール (canonical)**:
- 1 sheet 内でしか参照されない → **Sheet-scoped**
- 2+ sheet から参照される → **Workbook-scoped**
- 迷ったら sheet-scoped (後から workbook に昇格は安全、逆は衝突 risk)

### 1.2 Insertion Robustness (本書の中核価値)

Excel の named range は、定義 cell を含む **行/列が挿入・削除された場合に reference cell が auto-shift する**。これは cell anchor (`$C$5`) でも sheet 内部では同様だが、**他 sheet からの絶対参照** では Excel の version / 設定により挙動が安定しない。named range なら全 reference 元が自動追従。

| 操作 | 名前ベース ref の挙動 | cell anchor ref の挙動 |
|---|---|---|
| 同 sheet 内で行挿入 (B5-B6 間に新行) | ✅ auto-shift | ✅ auto-shift (同 sheet) |
| 他 sheet から absolute ref で行挿入 | ✅ auto-shift | ⚠️ Excel version 依存 |
| 行削除 (定義 cell を削除) | ❌ `#REF!` | ❌ `#REF!` |
| sheet rename | ✅ 不変 | ✅ 自動更新 (Excel が認識) |
| sheet 削除 | ❌ name が orphan | ❌ `#REF!` |
| 列挿入 (D 列の前に新列) | ✅ auto-shift | ⚠️ Excel が auto-adjust する場合とそうでない場合あり (絶対参照の挙動差) |
| 期数追加 (Y4 → Y5 列追加) | ✅ Year_Headers 更新で全連動 | ❌ 各 builder の hard-code 列範囲を全て手修正 |

### 1.3 Naming Convention

**Canonical 形式**: `<Section>_<LineItem>` の **PascalCase + Underscore separator**

```
✅ Rev_Total            (Section=Rev, LineItem=Total)
✅ ARR_NetNew           (Section=ARR, LineItem=NetNew)
✅ Cap_PPS_PostMoney    (Section=Cap, SubSection=PPS, Variant=PostMoney — 多段 underscore OK)
✅ KPI_LTV_CAC          (compound term — 多段 underscore OK)
❌ rev_total            (snake_case 禁止 — case 区別なしだが視認性のため)
❌ RevTotal             (区切りなし — Section と LineItem の境界が読めない)
❌ Rev-Total            (hyphen 禁止 — Excel で識別子として不可)
❌ Rev Total            (空白禁止 — Excel 仕様)
```

**Section prefix の canonical 一覧** (本書 §2 で全件列挙):

| Section | 用途 | 例 |
|---|---|---|
| `Rev_` | 02_Revenue の line items | `Rev_Total`, `Rev_Subscription` |
| `ARR_` | ARR / 顧客指標 (02_Revenue 内部) | `ARR_New`, `ARR_EOY` |
| `Cust_` | 顧客 count / ACV | `Cust_Count_EOY`, `ACV` |
| `NRR_` / `GRR_` | retention rate (単独で意味確定) | `NRR_Rate`, `GRR_Rate` |
| `Cost_` | COGS / Personnel | `Cost_COGS`, `Cost_Personnel` |
| `Profit_` | Gross Profit | `Profit_Gross` |
| `OpEx_` | OpEx (S&M / R&D / G&A) | `OpEx_SM`, `OpEx_Total` |
| `FTE_` | Headcount | `FTE_Sales`, `FTE_Total` |
| `Salary_` | 給与 | `Salary_Avg` |
| `IS_` | Income Statement の line items | `IS_Revenue`, `IS_NI` |
| `BS_` | Balance Sheet の line items | `BS_Cash`, `BS_TotalAssets` |
| `CF_` | Cash Flow Statement | `CF_Operating`, `CF_EndCash` |
| `WC_` | Working Capital (05_BS § Working Capital) | `WC_DSO`, `WC_Net` |
| `Debt_` | 借入 (07_Debt) | `Debt_Drawdown`, `Debt_Ending` |
| `Cap_` | Cap table (08_CapTable) | `Cap_FDSO`, `Cap_PPS_PostMoney` |
| `DCF_` | DCF 評価 (09_DCF) | `DCF_FCFF`, `DCF_EV` |
| `Comps_` | 比較分析 (10_Comps) | `Comps_Median_EVRev` |
| `Sens_` | 感度分析 (09_DCF § Sensitivity) | `Sens_WACC_Range` |
| `KPI_` | KPI ダッシュボード (11_KPI_Dashboard) | `KPI_RuleOf40`, `KPI_LTV_CAC` |
| (workbook 共通) | 期ヘッダ / 通貨 / scale | `Year_Headers`, `Currency_Code`, `Scale_Display`, `Period_Count` |

### 1.4 NG パターン

#### 1.4.1 Excel の予約名 (絶対禁止)

| 名前 | 理由 |
|---|---|
| `Print_Area` | Excel が印刷範囲指定に予約 |
| `Print_Titles` | Excel が印刷タイトル行に予約 |
| `Auto_Open` | Excel 起動時マクロ自動実行用 |
| `Auto_Close` | Excel 終了時マクロ自動実行用 |
| `Auto_Activate` | sheet 切替時マクロ自動実行用 |
| `Auto_Deactivate` | 同上 |
| `Database` | Excel の DB 連携機能予約 |
| `Criteria` | Excel フィルター予約 |
| `Extract` | Excel 抽出機能予約 |
| `Consolidate_Area` | Excel 統合機能予約 |
| `Sheet_Title` | LibreOffice で予約 (互換性のため避ける) |

#### 1.4.2 Cell address 衝突パターン (Excel が name vs cell ref を取り違える)

| NG | 衝突 | 代替 |
|---|---|---|
| `Q1` | 列 Q × 行 1 の cell ref と区別不能 | `Period_Q1` |
| `FY24` | 列 FY × 行 24 の cell ref | `FY_2024` or `Year_FY24` |
| `R1C1` | R1C1 reference style と競合 | `Row1Col1` |
| `A1`, `B5`, ..., `XFD16384` | 全 cell coord と衝突 | prefix 付与 (`Cell_A1`) |
| `IRR1` | 列 IRR (4096 列目) × 行 1 | `IRR_Y1` |

**Rule**: **数字始まり禁止** + **2 文字列+1 文字以上の数字** という pattern (例: `AB12`) は cell ref と衝突する可能性が高いので避ける。常に section prefix (`Rev_`, `ARR_` 等) を付ければこの class の衝突は自動回避される。

#### 1.4.3 単一語 (Section prefix なし) — 衝突リスクが高いため禁止

| NG | 理由 | 代替 |
|---|---|---|
| `Total` | どの total か不明 + 他名と衝突しやすい | `Rev_Total` / `OpEx_Total` |
| `Revenue` | 02_Revenue の合計か IS の合計か不明 | `Rev_Total` / `IS_Revenue` |
| `Cash` | BS の Cash か CFS の ending か不明 | `BS_Cash` / `CF_EndCash` |
| `ARR` | New / Expansion / Churn / EOY のどれか不明 | `ARR_EOY` 等明示 |
| `WACC` | 単独使用は OK と感じるが、検索 hit 多発 | `Val_WACC` (将来 valuation の WACC が複数になる場合に備える) |

#### 1.4.4 Underscore の位置

| NG | 理由 | 代替 |
|---|---|---|
| `_Var` | underscore 始まり = Excel が hidden name として扱う | `Var_X` |
| `Rev_` | underscore 終わり = parser が混乱 | `Rev_Total` |
| `Rev__Total` | 連続 underscore = typo の温床 | `Rev_Total` |

但し **途中の underscore** は OK (例: `Year_Headers`, `Cap_PPS_PostMoney`)。

### 1.5 文字数制限

| 制限 | 値 | 出典 |
|---|---|---|
| Excel 公式上限 | 255 文字 | Microsoft 公式 |
| 慣習推奨上限 | 30 文字以内 | IB 業界慣習 (Wall Street Prep / Macabacus) |
| 本 skill 推奨 | **25 文字以内** | 本書では 25 字以内を厳守 |

本書 §2 の全 named range は **25 字以内** に収まる設計。`KPI_CAC_Payback_Months` (22 字) のような長名でも問題なし。

### 1.6 大文字小文字非区別 (Excel 仕様)

Excel は named range 解決時に case を **無視する**。`Rev_Total` と `rev_total` は同一 name と扱う。よって:

- **PascalCase + underscore** に統一して **可読性のため** 揃える (Excel の挙動は同じだが、人間が読むときの一貫性のため)
- Python builder 側で `name="Rev_Total"` と指定しても、Excel UI では `Rev_Total` で表示 (登録時の case がそのまま保存)

### 1.7 重複時の振る舞い

同名で **workbook-scoped と sheet-scoped が併存可能**。優先順位:

1. ある sheet 内で `=Rev_Total` と書くと、まず **その sheet の sheet-scoped name** を探す
2. なければ **workbook-scoped name** にフォールバック
3. なければ `#NAME?` エラー

**実用ルール**: 本 skill では 同名併存を **避ける**。同名の sheet-scoped と workbook-scoped が混在すると保守時の混乱の元 (どちらを参照しているか目視で判別困難)。

---

## 2. 命名規約 Canonical Table (本 reference の中核)

各 sheet × line item を **完全列挙**。実装時はこの表を **唯一の正本** として参照する。

### 2.1 02_Revenue (Sheet 02)

| Sheet line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| Revenue (total) — B5 | `$D$5:$AA$5` | `Rev_Total` | **Workbook** | 04_IS, 09_DCF, 09_DCF § Sensitivity, 14_KPI |
| Subscription Revenue | `$D$6:$AA$6` | `Rev_Subscription` | Sheet | 03 内部、11_KPI_Dashboard |
| Services / Pro-services Revenue | `$D$7:$AA$7` | `Rev_Services` | Sheet | 03 内部 |
| Initial / Setup Fee Revenue | `$D$8:$AA$8` | `Rev_Initial` | Sheet | 03 内部 |
| Usage / Consumption Revenue | `$D$9:$AA$9` | `Rev_Usage` | Sheet | 03 内部 |
| Hardware Revenue | `$D$10:$AA$10` | `Rev_Hardware` | Sheet | 03 内部 (hardware co. のみ) |
| Other Revenue | `$D$11:$AA$11` | `Rev_Other` | Sheet | 03 内部 |
| Revenue YoY Growth % | `$D$12:$AA$12` | `Rev_GrowthYoY` | Sheet | 14_KPI |
| | | | | |
| **ARR Build** (sub-section) | | | | |
| Beginning ARR (BoP) | `$D$15:$AA$15` | `ARR_BoP` | Sheet | 11_KPI_Dashboard |
| New ARR | `$D$16:$AA$16` | `ARR_New` | Sheet | 02, 14_KPI |
| Expansion ARR | `$D$17:$AA$17` | `ARR_Expansion` | Sheet | 02, 14 |
| Contraction ARR | `$D$18:$AA$18` | `ARR_Contraction` | Sheet | 02, 14 |
| Churn ARR | `$D$19:$AA$19` | `ARR_Churn` | Sheet | 02, 14 |
| Ending ARR (EoP / EOY) | `$D$20:$AA$20` | `ARR_EOY` | **Workbook** | 14_KPI, 09_DCF |
| Net New ARR | `$D$21:$AA$21` | `ARR_NetNew` | Sheet | 14 (Magic Number 算出) |
| | | | | |
| **Customer Metrics** (sub-section) | | | | |
| Customer Count BoP | `$D$24:$AA$24` | `Cust_Count_BoP` | Sheet | 02 |
| New Customers | `$D$25:$AA$25` | `Cust_New` | Sheet | 02 |
| Churned Customers | `$D$26:$AA$26` | `Cust_Churned` | Sheet | 02 |
| Customer Count EOY | `$D$27:$AA$27` | `Cust_Count_EOY` | Sheet | 02, 14 |
| ACV (Average Contract Value) | `$D$28:$AA$28` | `ACV` | Sheet | 02, 14 |
| | | | | |
| **Retention Rates** (sub-section) | | | | |
| NRR (Net Revenue Retention) | `$D$31:$AA$31` | `NRR_Rate` | Sheet | 02, 14 |
| GRR (Gross Revenue Retention) | `$D$32:$AA$32` | `GRR_Rate` | Sheet | 02, 14 |
| Logo Retention | `$D$33:$AA$33` | `LogoRetention_Rate` | Sheet | 14 |

### 2.2 03_OpEx (Sheet 03)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| **COGS Build** | | | | |
| Variable COGS — Hosting/Cloud | `$D$5:$AA$5` | `Cost_COGS_Hosting` | Sheet | 04 内部 |
| Variable COGS — Materials | `$D$6:$AA$6` | `Cost_COGS_Materials` | Sheet | 04 内部 |
| Variable COGS — Payment Fees | `$D$7:$AA$7` | `Cost_COGS_Payment` | Sheet | 04 内部 |
| Fixed COGS — Implementation | `$D$8:$AA$8` | `Cost_COGS_Impl` | Sheet | 04 内部 |
| COGS — D&A allocation | `$D$9:$AA$9` | `Cost_COGS_DA` | Sheet | 04 内部 |
| **Total COGS** | `$D$10:$AA$10` | `Cost_COGS` | **Workbook** | 03_Rev, 04_IS |
| Gross Profit | `$D$12:$AA$12` | `Profit_Gross` | **Workbook** | 04_IS, 14_KPI |
| Gross Margin % | `$D$13:$AA$13` | `Profit_GM_Pct` | Sheet | 14_KPI |
| | | | | |
| **OpEx Build** | | | | |
| S&M — Total | `$D$16:$AA$16` | `OpEx_SM` | **Workbook** | 04_IS, 14 (Magic Number) |
| S&M — Headcount Cost | `$D$17:$AA$17` | `OpEx_SM_HC` | Sheet | 04 内部 |
| S&M — Marketing Programs | `$D$18:$AA$18` | `OpEx_SM_Marketing` | Sheet | 04 内部 |
| R&D — Total | `$D$19:$AA$19` | `OpEx_RD` | **Workbook** | 04_IS |
| R&D — Headcount Cost | `$D$20:$AA$20` | `OpEx_RD_HC` | Sheet | 04 内部 |
| G&A — Total | `$D$21:$AA$21` | `OpEx_GA` | **Workbook** | 04_IS |
| G&A — Headcount Cost | `$D$22:$AA$22` | `OpEx_GA_HC` | Sheet | 04 内部 |
| **Total OpEx** | `$D$23:$AA$23` | `OpEx_Total` | **Workbook** | 04_IS, 14 |
| | | | | |
| **Headcount** (FTE) | | | | |
| FTE — Sales | `$D$26:$AA$26` | `FTE_Sales` | Sheet | 02, 04 内部 |
| FTE — Marketing | `$D$27:$AA$27` | `FTE_Marketing` | Sheet | 04 内部 |
| FTE — Engineering | `$D$28:$AA$28` | `FTE_Eng` | Sheet | 02, 04 内部 |
| FTE — Product | `$D$29:$AA$29` | `FTE_Product` | Sheet | 04 内部 |
| FTE — G&A | `$D$30:$AA$30` | `FTE_GA` | Sheet | 04 内部 |
| FTE — Other | `$D$31:$AA$31` | `FTE_Other` | Sheet | 04 内部 |
| **FTE Total** | `$D$32:$AA$32` | `FTE_Total` | **Workbook** | 14_KPI |
| Average Salary (Annual) | `$D$33:$AA$33` | `Salary_Avg` | Sheet | 04 内部 |
| Personnel Cost (Total) | `$D$34:$AA$34` | `Cost_Personnel` | Sheet | 04 内部 |
| | | | | |
| **D&A / SBC** | | | | |
| D&A (Depreciation & Amortization) | `$D$37:$AA$37` | `Cost_DA` | **Workbook** | 04_IS, 06_CFS |
| SBC (Stock-Based Compensation) | `$D$38:$AA$38` | `Cost_SBC` | **Workbook** | 04_IS, 06_CFS, 05_BS (APIC) |

### 2.3 04_IS (Income Statement)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| Revenue (link from 03) | `$D$5:$AA$5` | `IS_Revenue` | **Workbook** | 09_DCF, 09_DCF § Sensitivity, 14_KPI |
| COGS (link from 04) | `$D$6:$AA$6` | `IS_COGS` | Workbook | 14_KPI |
| **Gross Profit** | `$D$7:$AA$7` | `IS_GrossProfit` | **Workbook** | 09_DCF, 14_KPI |
| S&M | `$D$9:$AA$9` | `IS_SM` | Sheet | 14_KPI (LTV/CAC) |
| R&D | `$D$10:$AA$10` | `IS_RD` | Sheet | 14_KPI |
| G&A | `$D$11:$AA$11` | `IS_GA` | Sheet | 14_KPI |
| Total OpEx | `$D$12:$AA$12` | `IS_OpEx` | Sheet | 14_KPI |
| **EBITDA** | `$D$14:$AA$14` | `IS_EBITDA` | **Workbook** | 09_DCF, 10_Comps, 09_DCF § Sensitivity, 14_KPI |
| EBITDA Margin % | `$D$15:$AA$15` | `IS_EBITDA_Pct` | Sheet | 14_KPI |
| D&A | `$D$16:$AA$16` | `IS_DA` | Sheet | 06_CFS |
| **EBIT** | `$D$17:$AA$17` | `IS_EBIT` | **Workbook** | 09_DCF (NOPAT 算出), 14_KPI |
| Interest Income | `$D$18:$AA$18` | `IS_InterestIncome` | Sheet | 05 内部 |
| Interest Expense | `$D$19:$AA$19` | `IS_Interest` | **Workbook** | 07_Debt, 14 (ICR) |
| Other Income / Expense | `$D$20:$AA$20` | `IS_OtherIE` | Sheet | 05 内部 |
| **PBT (Pre-Tax Income)** | `$D$21:$AA$21` | `IS_PBT` | **Workbook** | 12_Tax, 09_DCF |
| Tax Expense | `$D$22:$AA$22` | `IS_Tax` | **Workbook** | 09_DCF, 12_Tax |
| Effective Tax Rate % | `$D$23:$AA$23` | `IS_TaxRate` | Sheet | 09_DCF, 12_Tax |
| **Net Income** | `$D$24:$AA$24` | `IS_NI` | **Workbook** | 05_BS (RE), 06_CFS, 14_KPI |
| Net Income Margin % | `$D$25:$AA$25` | `IS_NI_Pct` | Sheet | 14_KPI |
| EPS (basic) | `$D$26:$AA$26` | `IS_EPS_Basic` | Sheet | 14_KPI |
| EPS (diluted) | `$D$27:$AA$27` | `IS_EPS_Diluted` | Sheet | 14_KPI |

### 2.4 05_BS (Balance Sheet)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| **Assets — Current** | | | | |
| Cash & Equivalents | `$D$5:$AA$5` | `BS_Cash` | **Workbook** | 06_CFS, 09_DCF, 14_KPI |
| Short-term Investments | `$D$6:$AA$6` | `BS_STInvest` | Sheet | 06 内部 |
| Accounts Receivable | `$D$7:$AA$7` | `BS_AR` | **Workbook** | 06_CFS (ΔWC), 05_BS § Working Capital |
| Inventory | `$D$8:$AA$8` | `BS_Inventory` | Sheet | 06_CFS, 05_BS § Working Capital |
| Prepaid Expenses | `$D$9:$AA$9` | `BS_Prepaid` | Sheet | 06_CFS |
| Other Current Assets | `$D$10:$AA$10` | `BS_OtherCA` | Sheet | 06_CFS |
| **Total Current Assets** | `$D$11:$AA$11` | `BS_CurrentAssets` | **Workbook** | 14_KPI |
| | | | | |
| **Assets — Non-current** | | | | |
| PP&E (Gross) | `$D$13:$AA$13` | `BS_PPE_Gross` | Sheet | 06 内部 |
| Accumulated Depreciation | `$D$14:$AA$14` | `BS_AccumDep` | Sheet | 06 内部 |
| **PP&E (Net)** | `$D$15:$AA$15` | `BS_PPE_Net` | **Workbook** | 09_DCF, 14_KPI |
| Intangible Assets | `$D$16:$AA$16` | `BS_Intangibles` | Sheet | 06 内部 |
| Goodwill | `$D$17:$AA$17` | `BS_Goodwill` | Sheet | 06 内部 |
| Right-of-Use Assets (lease) | `$D$18:$AA$18` | `BS_ROU` | Sheet | 06 内部, 07_Debt |
| Deferred Tax Asset | `$D$19:$AA$19` | `BS_DTA` | Sheet | 12_Tax |
| Other Non-current Assets | `$D$20:$AA$20` | `BS_OtherNCA` | Sheet | 06 内部 |
| **Total Non-current Assets** | `$D$21:$AA$21` | `BS_NonCurrentAssets` | Sheet | 06 内部 |
| | | | | |
| **Total Assets** | `$D$22:$AA$22` | `BS_TotalAssets` | **Workbook** | 14_KPI, 12_SanityChecks |
| | | | | |
| **Liabilities — Current** | | | | |
| Accounts Payable | `$D$25:$AA$25` | `BS_AP` | **Workbook** | 06_CFS, 05_BS § Working Capital |
| Accrued Expenses | `$D$26:$AA$26` | `BS_Accrued` | Sheet | 06_CFS, 05_BS § Working Capital |
| Deferred Revenue (current) | `$D$27:$AA$27` | `BS_DefRev_Current` | Sheet | 06_CFS, 05_BS § Working Capital |
| Short-term Debt | `$D$28:$AA$28` | `BS_STDebt` | Sheet | 07_Debt |
| Current Portion of LT Debt | `$D$29:$AA$29` | `BS_CurrentLTD` | Sheet | 07_Debt |
| Other Current Liabilities | `$D$30:$AA$30` | `BS_OtherCL` | Sheet | 06 内部 |
| **Total Current Liabilities** | `$D$31:$AA$31` | `BS_CurrentLiab` | **Workbook** | 14_KPI |
| | | | | |
| **Liabilities — Non-current** | | | | |
| Long-term Debt | `$D$33:$AA$33` | `BS_LTDebt` | **Workbook** | 07_Debt, 09_DCF, 14_KPI |
| Deferred Revenue (non-current) | `$D$34:$AA$34` | `BS_DefRev_NC` | Sheet | 06 内部 |
| Lease Liabilities | `$D$35:$AA$35` | `BS_LeaseLiab` | Sheet | 07_Debt |
| Deferred Tax Liability | `$D$36:$AA$36` | `BS_DTL` | Sheet | 12_Tax |
| Other Non-current Liabilities | `$D$37:$AA$37` | `BS_OtherNCL` | Sheet | 06 内部 |
| **Total Non-current Liabilities** | `$D$38:$AA$38` | `BS_NonCurrentLiab` | Sheet | 06 内部 |
| | | | | |
| **Total Liabilities** | `$D$39:$AA$39` | `BS_TotalLiab` | **Workbook** | 09_DCF (Net Debt), 14_KPI, 12_SanityChecks |
| | | | | |
| **Equity** | | | | |
| Common Stock | `$D$42:$AA$42` | `BS_CommonStock` | Sheet | 08_CapTable |
| APIC (Additional Paid-in Capital) | `$D$43:$AA$43` | `BS_APIC` | Sheet | 08_CapTable |
| Treasury Stock | `$D$44:$AA$44` | `BS_Treasury` | Sheet | 08_CapTable |
| Retained Earnings | `$D$45:$AA$45` | `BS_RE` | **Workbook** | 06_CFS, 12_SanityChecks |
| AOCI (累積為替換算 等) | `$D$46:$AA$46` | `BS_AOCI` | Sheet | 13a_consolidation |
| Non-controlling Interest | `$D$47:$AA$47` | `BS_NCI` | Sheet | 13a_consolidation |
| **Total Equity** | `$D$48:$AA$48` | `BS_TotalEquity` | **Workbook** | 09_DCF (Net Debt), 14_KPI, 12_SanityChecks |
| | | | | |
| **Total L + E** | `$D$49:$AA$49` | `BS_LE_Total` | Sheet | 12_SanityChecks (BS = L+E check) |

### 2.5 06_CFS (Cash Flow Statement)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| **CF from Operations** | | | | |
| Net Income (link from 05) | `$D$5:$AA$5` | `CF_NI` | Sheet | 07 内部 |
| D&A add-back | `$D$6:$AA$6` | `CF_DA` | Sheet | 07 内部 |
| SBC add-back | `$D$7:$AA$7` | `CF_SBC` | Sheet | 07 内部 |
| ΔAR (Working Capital) | `$D$8:$AA$8` | `CF_dAR` | Sheet | 07 内部 |
| ΔInventory | `$D$9:$AA$9` | `CF_dInventory` | Sheet | 07 内部 |
| ΔAP | `$D$10:$AA$10` | `CF_dAP` | Sheet | 07 内部 |
| ΔAccrued | `$D$11:$AA$11` | `CF_dAccrued` | Sheet | 07 内部 |
| ΔDeferred Revenue | `$D$12:$AA$12` | `CF_dDefRev` | Sheet | 07 内部 |
| Other Operating | `$D$13:$AA$13` | `CF_OtherOps` | Sheet | 07 内部 |
| **CF from Operations** | `$D$14:$AA$14` | `CF_Operating` | **Workbook** | 09_DCF, 14_KPI (Burn Multiple) |
| | | | | |
| **CF from Investing** | | | | |
| CapEx | `$D$17:$AA$17` | `CF_CapEx` | **Workbook** | 09_DCF (FCFF) |
| Acquisitions | `$D$18:$AA$18` | `CF_Acquisitions` | Sheet | 07 内部 |
| Investments | `$D$19:$AA$19` | `CF_Investments` | Sheet | 07 内部 |
| Other Investing | `$D$20:$AA$20` | `CF_OtherInv` | Sheet | 07 内部 |
| **CF from Investing** | `$D$21:$AA$21` | `CF_Investing` | **Workbook** | 09_DCF, 14_KPI |
| | | | | |
| **CF from Financing** | | | | |
| Debt Issuance | `$D$24:$AA$24` | `CF_DebtIssue` | Sheet | 07_Debt |
| Debt Repayment | `$D$25:$AA$25` | `CF_DebtRepay` | Sheet | 07_Debt |
| Equity Issuance | `$D$26:$AA$26` | `CF_EquityIssue` | Sheet | 08_CapTable |
| Buyback / Dividends | `$D$27:$AA$27` | `CF_Buyback` | Sheet | 08_CapTable |
| Other Financing | `$D$28:$AA$28` | `CF_OtherFin` | Sheet | 07 内部 |
| **CF from Financing** | `$D$29:$AA$29` | `CF_Financing` | **Workbook** | 14_KPI |
| | | | | |
| **Cash Reconciliation** | | | | |
| Net Cash Change | `$D$32:$AA$32` | `CF_NetChange` | Sheet | 07 内部 |
| FX Translation | `$D$33:$AA$33` | `CF_FX` | Sheet | 13a_consolidation |
| Beginning Cash | `$D$34:$AA$34` | `CF_BeginCash` | Sheet | 07 内部 |
| **Ending Cash** | `$D$35:$AA$35` | `CF_EndCash` | **Workbook** | 05_BS (Cash check), 12_SanityChecks |
| | | | | |
| Free Cash Flow (FCF) | `$D$37:$AA$37` | `CF_FCF` | **Workbook** | 09_DCF, 14_KPI |

### 2.6 05_BS § Working Capital Schedule (sub-section, rows 56-69)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| DSO (Days Sales Outstanding) | `$D$5:$AA$5` | `WC_DSO` | Sheet | 05_BS (AR projection) |
| DIO (Days Inventory Outstanding) | `$D$6:$AA$6` | `WC_DIO` | Sheet | 05_BS (Inventory) |
| DPO (Days Payable Outstanding) | `$D$7:$AA$7` | `WC_DPO` | Sheet | 05_BS (AP) |
| Deferred Revenue Days | `$D$8:$AA$8` | `WC_DefRev_Days` | Sheet | 05_BS (DefRev) |
| Cash Conversion Cycle (CCC) | `$D$9:$AA$9` | `WC_CCC` | Sheet | 14_KPI |
| Net Working Capital | `$D$10:$AA$10` | `WC_Net` | Sheet | 09_DCF (ΔWC) |
| ΔWC (period-over-period) | `$D$11:$AA$11` | `WC_dNet` | Sheet | 09_DCF |

### 2.7 07_Debt (Debt Schedule)

| Line item | 推定 cell (anchor) | Named range | Scope | Used by |
|---|---|---|---|---|
| Beginning Debt Balance | `$D$5:$AA$5` | `Debt_Beginning` | Sheet | 09 内部 |
| Drawdown | `$D$6:$AA$6` | `Debt_Drawdown` | Sheet | 06_CFS |
| Scheduled Repayment | `$D$7:$AA$7` | `Debt_Repayment` | Sheet | 06_CFS |
| Mandatory Amortization | `$D$8:$AA$8` | `Debt_Amortization` | Sheet | 09 内部 |
| Optional Prepayment | `$D$9:$AA$9` | `Debt_Prepayment` | Sheet | 09 内部 |
| **Ending Debt Balance** | `$D$10:$AA$10` | `Debt_Ending` | **Workbook** | 05_BS, 09_DCF (Net Debt), 14_KPI |
| Average Debt Balance | `$D$11:$AA$11` | `Debt_AvgBalance` | Sheet | 09 内部 (interest 計算) |
| Interest Rate (effective) | `$D$12:$AA$12` | `Debt_InterestRate` | Sheet | 09 内部 |
| **Interest Expense** | `$D$13:$AA$13` | `Debt_InterestExpense` | **Workbook** | 04_IS |
| Debt Capacity (covenant) | `$D$14:$AA$14` | `Debt_Capacity` | Sheet | 14_KPI (covenant check) |
| Leverage (Debt/EBITDA) | `$D$15:$AA$15` | `Debt_Leverage` | Sheet | 14_KPI |
| ICR (Interest Coverage) | `$D$16:$AA$16` | `Debt_ICR` | Sheet | 14_KPI |
| FCCR | `$D$17:$AA$17` | `Debt_FCCR` | Sheet | 14_KPI |
| DSCR | `$D$18:$AA$18` | `Debt_DSCR` | Sheet | 14_KPI |

### 2.8 08_CapTable

| Line item | 推定 cell | Named range | Scope | Used by |
|---|---|---|---|---|
| **Pre-money Cap Table** | | | | |
| FDSO (Fully Diluted Shares Outstanding) | `$D$5` (single cell) | `Cap_FDSO` | **Workbook** | 09_DCF (Per Share), 14_KPI (EPS) |
| FDSO — Common (Founders) | `$D$6` | `Cap_FDSO_Founders` | Workbook | 14_KPI (Founder %) |
| FDSO — Preferred (Investors) | `$D$7` | `Cap_FDSO_Preferred` | Workbook | 09_DCF |
| FDSO — Options Pool (Issued) | `$D$8` | `Cap_FDSO_Pool_Issued` | Workbook | 14_KPI |
| FDSO — Options Pool (Available) | `$D$9` | `Cap_FDSO_Pool_Avail` | Workbook | 14_KPI |
| FDSO — SAFE / Convertibles | `$D$10` | `Cap_FDSO_SAFE` | Workbook | 09_DCF |
| | | | | |
| **Pricing** | | | | |
| Pre-Money Valuation | `$D$13` | `Cap_PreMoney` | **Workbook** | 09_DCF |
| Post-Money Valuation | `$D$14` | `Cap_PostMoney` | **Workbook** | 09_DCF, 14_KPI |
| New Money | `$D$15` | `Cap_NewMoney` | Workbook | 14_KPI |
| **PPS Pre-Money** | `$D$16` | `Cap_PPS_PreMoney` | **Workbook** | 09_DCF |
| **PPS Post-Money** | `$D$17` | `Cap_PPS_PostMoney` | **Workbook** | 09_DCF (Per Share), 14_KPI |
| | | | | |
| **Ownership %** | | | | |
| Founder % | `$D$20` | `Cap_Founder_Pct` | **Workbook** | 14_KPI |
| Investor % | `$D$21` | `Cap_Investor_Pct` | Workbook | 14_KPI |
| Pool Total % | `$D$22` | `Cap_Pool_Pct` | Workbook | 14_KPI |
| Pool Total (shares) | `$D$23` | `Cap_Pool_Total` | **Workbook** | 14_KPI |
| Pool Available (post-issuance) | `$D$24` | `Cap_Pool_Available` | Workbook | 14_KPI |
| Pool Issued | `$D$25` | `Cap_Pool_Issued` | Workbook | 14_KPI |
| | | | | |
| **Liquidation Preference** | | | | |
| Total Pref Stack | `$D$28` | `Cap_PrefStack` | Sheet | 09_DCF (waterfall) |
| Common Pool (after pref) | `$D$29` | `Cap_CommonPool` | Sheet | 09_DCF |
| | | | | |
| **Per-share Outputs (DCF link)** | | | | |
| Equity Value per Share | `$D$32` | `Cap_EquityPerShare` | Workbook | 14_KPI |
| MOIC (cumulative) | `$D$33` | `Cap_MOIC` | Sheet | 14_KPI |
| IRR (cumulative) | `$D$34` | `Cap_IRR` | Sheet | 14_KPI |

### 2.9 09_DCF (DCF Valuation)

| Line item | 推定 cell | Named range | Scope | Used by |
|---|---|---|---|---|
| **NOPAT Build** | | | | |
| EBIT | `$D$5:$AA$5` | `DCF_EBIT` | Sheet | 11 内部 |
| Tax on EBIT | `$D$6:$AA$6` | `DCF_TaxEBIT` | Sheet | 11 内部 |
| **NOPAT** | `$D$7:$AA$7` | `DCF_NOPAT` | Sheet | 11 内部 |
| | | | | |
| **FCFF Build** | | | | |
| + D&A | `$D$8:$AA$8` | `DCF_DA` | Sheet | 11 内部 |
| − CapEx | `$D$9:$AA$9` | `DCF_CapEx` | Sheet | 11 内部 |
| − ΔWC | `$D$10:$AA$10` | `DCF_dWC` | Sheet | 11 内部 |
| **FCFF (Free Cash Flow to Firm)** | `$D$11:$AA$11` | `DCF_FCFF` | **Workbook** | 10_Comps, 09_DCF § Sensitivity |
| | | | | |
| **WACC** | | | | |
| Risk-free Rate | `$D$14` | `DCF_RiskFree` | Sheet | 11 内部 |
| Equity Risk Premium | `$D$15` | `DCF_ERP` | Sheet | 11 内部 |
| Beta (unlevered) | `$D$16` | `DCF_Beta_Unlev` | Sheet | 11 内部 |
| Beta (relevered) | `$D$17` | `DCF_Beta_Relev` | Sheet | 11 内部 |
| Cost of Equity | `$D$18` | `DCF_CostEquity` | Sheet | 11 内部 |
| Cost of Debt (pre-tax) | `$D$19` | `DCF_CostDebt_Pre` | Sheet | 11 内部 |
| Cost of Debt (after-tax) | `$D$20` | `DCF_CostDebt_AT` | Sheet | 11 内部 |
| Debt / EV ratio | `$D$21` | `DCF_DebtEV` | Sheet | 11 内部 |
| Equity / EV ratio | `$D$22` | `DCF_EquityEV` | Sheet | 11 内部 |
| **WACC** | `$D$23` | `DCF_WACC` | **Workbook** | 09_DCF § Sensitivity |
| | | | | |
| **Terminal Value** | | | | |
| Terminal Year FCFF | `$D$26` | `DCF_TerminalFCFF` | Sheet | 11 内部 |
| Perpetual Growth Rate (g) | `$D$27` | `DCF_g` | **Workbook** | 09_DCF § Sensitivity |
| Terminal Value (Gordon Growth) | `$D$28` | `DCF_TV_GG` | Sheet | 11 内部 |
| Exit Multiple (EV/EBITDA) | `$D$29` | `DCF_TV_Exit_Mult` | Sheet | 11 内部 |
| Terminal Value (Exit Multiple) | `$D$30` | `DCF_TV_Exit` | Sheet | 11 内部 |
| Terminal Value (used) | `$D$31` | `DCF_TV` | Sheet | 11 内部 |
| | | | | |
| **PV / EV / Equity Value** | | | | |
| Discount Factor | `$D$34:$AA$34` | `DCF_DiscountFactor` | Sheet | 11 内部 |
| PV of FCFF | `$D$35:$AA$35` | `DCF_PV_FCFF` | Sheet | 11 内部 |
| PV of Terminal Value | `$D$36` | `DCF_PV_TV` | Sheet | 11 内部 |
| **Enterprise Value (EV)** | `$D$37` | `DCF_EV` | **Workbook** | 10_Comps, 09_DCF § Sensitivity, 14_KPI, 13_IC |
| − Net Debt | `$D$38` | `DCF_NetDebt` | Sheet | 11 内部 |
| **Equity Value** | `$D$39` | `DCF_Equity` | **Workbook** | 14_KPI, 13_IC |
| ÷ FDSO | `$D$40` | `DCF_FDSO_Used` | Sheet | 11 内部 |
| **Equity per Share** | `$D$41` | `DCF_PerShare` | **Workbook** | 14_KPI, 13_IC |

### 2.10 10_Comps (Trading / Transaction Comps)

| Line item | 推定 cell | Named range | Scope | Used by |
|---|---|---|---|---|
| **Trading Comps** | | | | |
| EV/Revenue — Min | `$D$5` | `Comps_Min_EVRev` | Sheet | 09_DCF § Sensitivity (football field) |
| EV/Revenue — 25%ile | `$D$6` | `Comps_25pct_EVRev` | Sheet | 09_DCF § Sensitivity |
| EV/Revenue — Median | `$D$7` | `Comps_Median_EVRev` | Sheet | 09_DCF § Sensitivity |
| EV/Revenue — 75%ile | `$D$8` | `Comps_75pct_EVRev` | Sheet | 09_DCF § Sensitivity |
| EV/Revenue — Max | `$D$9` | `Comps_Max_EVRev` | Sheet | 09_DCF § Sensitivity |
| EV/EBITDA — Min | `$D$10` | `Comps_Min_EVEBITDA` | Sheet | 09_DCF § Sensitivity |
| EV/EBITDA — Median | `$D$11` | `Comps_Median_EVEBITDA` | Sheet | 09_DCF § Sensitivity |
| EV/EBITDA — 75%ile | `$D$12` | `Comps_75pct_EVEBITDA` | Sheet | 09_DCF § Sensitivity |
| EV/EBITDA — Max | `$D$13` | `Comps_Max_EVEBITDA` | Sheet | 09_DCF § Sensitivity |
| ARR Multiple — Median | `$D$14` | `Comps_Median_ARRMult` | Sheet | 09_DCF § Sensitivity |
| Rule of 40 — Median (peers) | `$D$15` | `Comps_Median_R40` | Sheet | 14_KPI (compare) |
| | | | | |
| **Transaction Comps** | | | | |
| Tx EV/Revenue — Median | `$D$18` | `Comps_Tx_Median_EVRev` | Sheet | 09_DCF § Sensitivity |
| Tx EV/EBITDA — Median | `$D$19` | `Comps_Tx_Median_EVEBITDA` | Sheet | 09_DCF § Sensitivity |

### 2.11 09_DCF § Sensitivity & Stress (sub-section)

| Line item | 推定 cell | Named range | Scope | Used by |
|---|---|---|---|---|
| WACC Range Low | `$D$5` | `Sens_WACC_Low` | Sheet | 13 内部 |
| WACC Range Mid | `$D$6` | `Sens_WACC_Mid` | Sheet | 13 内部 |
| WACC Range High | `$D$7` | `Sens_WACC_High` | Sheet | 13 内部 |
| WACC Range (array) | `$D$5:$D$7` | `Sens_WACC_Range` | Sheet | 13 内部 |
| g Range Low | `$D$8` | `Sens_g_Low` | Sheet | 13 内部 |
| g Range Mid | `$D$9` | `Sens_g_Mid` | Sheet | 13 内部 |
| g Range High | `$D$10` | `Sens_g_High` | Sheet | 13 内部 |
| g Range (array) | `$D$8:$D$10` | `Sens_g_Range` | Sheet | 13 内部 |
| EV Matrix (WACC × g) | `$E$5:$G$7` | `Sens_EV_Matrix` | Sheet | 17_chart (Football field) |
| Equity Matrix | `$E$10:$G$12` | `Sens_Equity_Matrix` | Sheet | 17_chart |
| PerShare Matrix | `$E$15:$G$17` | `Sens_PerShare_Matrix` | Sheet | 17_chart |
| Football Field — Low band | `$D$20` | `Sens_FF_Low` | Sheet | 17_chart |
| Football Field — Mid band | `$D$21` | `Sens_FF_Mid` | Sheet | 17_chart |
| Football Field — High band | `$D$22` | `Sens_FF_High` | Sheet | 17_chart |

### 2.12 11_KPI_Dashboard

| KPI | 推定 cell | Named range | Scope | Used by |
|---|---|---|---|---|
| **Growth & Profitability** | | | | |
| Revenue Growth YoY | `$D$5:$AA$5` | `KPI_RevGrowth` | Sheet | 17_chart |
| Rule of 40 | `$D$6:$AA$6` | `KPI_RuleOf40` | **Workbook** | 13_IC |
| Gross Margin | `$D$7:$AA$7` | `KPI_GM` | Sheet | 17_chart |
| EBITDA Margin | `$D$8:$AA$8` | `KPI_EBITDA_Margin` | Sheet | 17_chart |
| FCF Margin | `$D$9:$AA$9` | `KPI_FCF_Margin` | Sheet | 17_chart |
| | | | | |
| **SaaS / Retention** | | | | |
| NRR | `$D$12:$AA$12` | `KPI_NRR` | **Workbook** | 13_IC, 17_chart |
| GRR | `$D$13:$AA$13` | `KPI_GRR` | Sheet | 17_chart |
| ARR Growth | `$D$14:$AA$14` | `KPI_ARR_Growth` | Sheet | 17_chart |
| Magic Number | `$D$15:$AA$15` | `KPI_Magic_Number` | **Workbook** | 13_IC |
| | | | | |
| **Efficiency** | | | | |
| LTV (Method B, cohort) | `$D$18:$AA$18` | `KPI_LTV` | Sheet | 14 内部 |
| CAC (fully loaded) | `$D$19:$AA$19` | `KPI_CAC` | Sheet | 14 内部 |
| **LTV / CAC** | `$D$20:$AA$20` | `KPI_LTV_CAC` | **Workbook** | 13_IC |
| **CAC Payback (months)** | `$D$21:$AA$21` | `KPI_CAC_Payback` | **Workbook** | 13_IC |
| | | | | |
| **Burn / Runway** | | | | |
| Net Burn | `$D$24:$AA$24` | `KPI_NetBurn` | Sheet | 14 内部 |
| **Burn Multiple** | `$D$25:$AA$25` | `KPI_BurnMultiple` | **Workbook** | 13_IC |
| Runway (months) | `$D$26:$AA$26` | `KPI_Runway` | **Workbook** | 13_IC |
| | | | | |
| **Capital Efficiency** | | | | |
| Burn Multiple Cumulative | `$D$29:$AA$29` | `KPI_BurnMult_Cum` | Sheet | 14 内部 |
| Capital Consumed | `$D$30:$AA$30` | `KPI_CapitalConsumed` | Sheet | 14 内部 |
| Total Capital Raised | `$D$31:$AA$31` | `KPI_CapitalRaised` | Sheet | 14 内部 |

### 2.13 Cross-sheet Aggregator (Workbook-scoped Constants)

| 名前 | 用途 | 推定定義 cell | Scope | Used by |
|---|---|---|---|---|
| `Year_Headers` | 年ヘッダ row への ref (D2:AA2 等) | `'01_Assumptions'!$D$2:$AA$2` | **Workbook** | 全 sheet (header row 描画時) |
| `Period_Count` | 期数定数 (例: 60 = 5y monthly, 20 = 5y quarterly) | `'01_Assumptions'!$D$3` | **Workbook** | 全 builder (loop 上限) |
| `Period_Start` | 期開始 (Date 値、例: 2026-01-01) | `'01_Assumptions'!$D$4` | **Workbook** | header 描画 |
| `Period_Frequency` | "monthly" / "quarterly" / "annual" | `'01_Assumptions'!$D$5` | **Workbook** | 全 builder |
| `Currency_Code` | "JPY" / "USD" | `'01_Assumptions'!$C$6` | **Workbook** | format 切替 |
| `Currency_Symbol` | "¥" / "$" | `'01_Assumptions'!$C$7` | **Workbook** | format 切替 |
| `Scale_Display` | "actual" / "thousand" / "million" | `'01_Assumptions'!$C$8` | **Workbook** | format 切替 |
| `Co_Name` | 会社名 (Cover / Footer) | `'00_Cover'!$B$2` | **Workbook** | header / footer |
| `Model_Version` | モデルバージョン (例: "v1.0.0") | `'00_Cover'!$B$3` | **Workbook** | Footer |
| `Model_Date` | モデル日付 | `'00_Cover'!$B$4` | **Workbook** | Footer |
| `Tax_Rate_Effective` | 法人実効税率 (例: 0.3152 for 大企業) | `'01_Assumptions'!$C$10` | **Workbook** | 09_DCF, 12_Tax |
| `Discount_Rate_DCF` | DCF 用 WACC (alias of DCF_WACC) | (alias) | **Workbook** | 09_DCF § Sensitivity |

### 2.14 Total 件数

| Section | Workbook-scoped | Sheet-scoped | 合計 |
|---|---|---|---|
| 02_Revenue | 2 | 23 | 25 |
| 03_OpEx | 7 | 16 | 23 |
| 04_IS | 9 | 15 | 24 |
| 05_BS | 9 | 28 | 37 |
| 06_CFS | 4 | 20 | 24 |
| 05_BS § Working Capital | 0 | 7 | 7 |
| 07_Debt | 2 | 12 | 14 |
| 08_CapTable | 9 | 11 | 20 |
| 09_DCF | 7 | 22 | 29 |
| 10_Comps | 0 | 12 | 12 |
| 09_DCF § Sensitivity | 0 | 13 | 13 |
| 11_KPI_Dashboard | 8 | 14 | 22 |
| Cross-sheet aggregator | 12 | 0 | 12 |
| **合計** | **69** | **193** | **262** |

(注: これは canonical な完全列挙であり、業態別バリエーション (例: hardware の `Rev_Hardware`, marketplace の `GMV_Total`) で項目が増減する場合は本表から派生定義する。`_Total` 行が同 sheet 内で 1 つしか出ない line item は workbook-scoped にしている。)

---

## 3. NG パターン総覧 (避けるべき名前)

§1.4 で原則を述べた。ここでは具体的な反例集を列挙する。

### 3.1 Excel 予約名 (再掲、絶対禁止)

```
Print_Area, Print_Titles, Auto_Open, Auto_Close, Auto_Activate,
Auto_Deactivate, Database, Criteria, Extract, Consolidate_Area
```

これらを名前として登録すると Excel は **登録は受け付ける** が、印刷範囲やマクロ機能と挙動が混線する。発見が困難な bug の温床。

### 3.2 Cell address 衝突 (再掲)

```
Q1, Q2, Q3, Q4, FY24, FY25, R1C1, A1, B5, ZZ100, XFD16384
```

特に **四半期表記 `Q1` / `Q2`** は実務で書きたくなるパターンだが Excel と衝突する。`Period_Q1` / `Period_FY24` の prefix を必ず付与する。

### 3.3 単一語 (Section prefix なし) — 強い衝突リスク

| NG | 何と衝突するか |
|---|---|
| `Total` | 全 sheet の `Total *` 行と概念衝突 |
| `Revenue` | 02_Revenue の合計 vs 04_IS の Revenue (link) |
| `Cash` | 05_BS の Cash vs 06_CFS の Beginning/Ending Cash |
| `Debt` | 05_BS の LTDebt vs 07_Debt の Beginning/Ending |
| `Tax` | IS の Tax vs Tax Schedule の Tax |
| `WACC` | 09_DCF の WACC vs 09_DCF § Sensitivity の WACC range mid |
| `Pool` | Cap Table の Issued vs Available vs Total |
| `EV` | 09_DCF vs 10_Comps の derived EV |

**Rule**: section prefix を **必ず** 付ける。1 文字の例外も認めない。

### 3.4 Underscore 異常パターン

```
NG: _Var      (underscore 始まり = Excel hidden)
NG: Var_      (underscore 終わり)
NG: Rev__Total (連続 underscore)
NG: __Init    (二重 underscore 始まり)
```

### 3.5 文字数オーバー

25 字超の名前は **可読性低下 + Name Box 画面で省略表示** され検索性が下がる。例:

```
NG: Cap_PostMoney_Valuation_Including_Pool_Refresh   (47 字)
OK: Cap_PostMoney_PoolRefresh                        (24 字)
```

### 3.6 言語混在

```
NG: 売上_Total      (日本語 + 英語、Excel は受け付けるが grep / VBA で詰まる)
OK: Rev_Total       (英語統一)
```

label 表記 (cell の B 列) は日本語 OK だが **named range 名は英語のみ** に統一。

---

## 4. 行/列 Insertion 耐性の検証パターン (Mini Cases)

### 4.1 Mini Case 1 — Hardware 売上 line を挿入 (行追加)

#### Before (Phase 5 — cell anchor)

`02_Revenue` シートの初期状態:

```
Row 5: Revenue (total)        =SUM(B6:B11)        [B5]
Row 6: Subscription Revenue   2,400               [B6]  ← ユーザー hard input
Row 7: Services Revenue         300               [B7]
Row 8: Initial Fee               100              [B8]
Row 9: Usage Revenue             500              [B9]
Row 10: Other Revenue              0              [B10]
Row 11: Hardware Revenue           0              [B11]
```

`04_IS` シートの Revenue 行:

```
Row 5: Revenue                =02_Revenue!$B$5    ← cell anchor 直書き
```

ユーザーが `02_Revenue` で **「Hardware 売上の前に SaaS Add-on Revenue を 1 行挿入したい」** として、行 11 と 12 の間に空行を挿入:

#### After (cell anchor — broken)

```
Row 5: Revenue (total)        =SUM(B6:B11)   ← ⚠️ Excel が =SUM(B6:B12) に拡張する場合と
                                                 そうでない場合あり (range vs anchor 違い)
Row 6-11: 既存行                                
Row 12: SaaS Add-on Revenue   (空)               ← 新行
```

`04_IS` の `=02_Revenue!$B$5` は **依然 B5 を指す** が、もし `Total` が SUM 拡張されない場合 Add-on Revenue が抜け落ちる。

#### After (named range — robust)

`02_Revenue` で `Rev_Total` が `'02_Revenue'!$B$5` で workbook-scoped に登録されている。行挿入で B5 自体は **動かない** (B5 は依然 Total) が、**SUM(B6:B11) の B11 部分が auto-shift して SUM(B6:B12) になる** (named range と無関係に Excel の SUM 範囲挙動として正しい)。

`04_IS` の formula:

```
Row 5: Revenue                =Rev_Total
```

これは **常に正しい Total を指し続ける**。`Rev_Total` の定義 cell (`$B$5`) も不変。

**判定**: named range は `=SUM(...)` の挙動とは独立に「`Rev_Total` 名 = B5」のひも付けだけを管理し、B5 の中身が SUM(B6:B12) になっていれば結果は正しい。**cross-sheet からの参照が一切壊れない** のが named range の核価値。

### 4.2 Mini Case 2 — Y6 forecast 列を追加 (列追加)

#### Before

```
Headers: A    B          C   D    E    F    G
                Y0       Y1   Y2   Y3   Y4   Y5
02_Revenue B5: Total     1000 1200 1500 1800 2200
04_IS  D5:    =02_Revenue!$D$5    (cell anchor: D5 を指す)
```

ユーザーが Y4 と Y5 の間に **Y4.5 (中間期)** を挿入したいとする。`02_Revenue` で F 列の前に新列を挿入:

#### After (cell anchor)

```
Headers: D    E    F    G    H
        Y1   Y2   Y3   Y4   Y4.5  Y5  ← 新列 = G になる
03_Rev:  1000 1200 1500 1800 (空)  2200
04_IS  D5: =02_Revenue!$D$5  ← Y1 (動かず正しい)
04_IS  E5: =02_Revenue!$E$5  ← Y2 (動かず正しい)
...
04_IS  H5: =02_Revenue!$G$5  ← ⚠️ ここで Excel auto-shift が動くか動かないか?
```

実際の挙動: 列挿入は **Excel が auto-adjust する** (cell anchor でも shift する) が、`'02_Revenue'!` のような cross-sheet absolute ref は version によっては shift しないバグ事例あり。さらに 04_IS 側で Y4.5 列を新規に作る場合、対応する formula は **手書きで追加** が必要。

#### After (named range — `Year_Headers` driven)

`Year_Headers` を `'01_Assumptions'!$D$2:$H$2` で登録し、各 sheet の period header はこの name から describe する。 列挿入時:

1. `01_Assumptions` で D-H の D-I に変更 (1 列拡張)
2. `Year_Headers` の定義範囲が auto-shift で `$D$2:$I$2` になる
3. 各 sheet で `Period_Count` を 5 → 6 に変更
4. 全 sheet が再 calculate して、Y4.5 列が空欄 (新 input 待ち) で 一貫表示

`Rev_Total` 自体は range ではなく point name (例えば `$B$5` 単独) なので影響なし。**range 系の name (`Year_Headers` 等) は auto-shift され、point 系の name (`Rev_Total` 単点) は不変**。

**判定**: 列追加 robustness は `Year_Headers` のような **range 系 named range で一括管理** することで、各 builder の hard-code を不要にする。

### 4.3 Mini Case 3 — Sheet rename (`02_Revenue` → `03_Rev`)

#### Before (cell anchor)

```python
# three_statement_builder.py
ws_is["D5"] = f"='02_Revenue'!$D$5"
```

ユーザーが Excel で `02_Revenue` を `03_Rev` にリネームすると、**Excel は内部参照を全て自動更新** する (Excel の優秀機能)。よって `04_IS` の D5 cell は `='03_Rev'!$D$5` に書き換わる。

ただし **Python builder 側の hard-coded 文字列** は古いまま:

```python
ws_is["D5"] = f"='02_Revenue'!$D$5"   # ← 次回 build 時に再現できない
```

→ **再 generate すると `'02_Revenue'!` を探して `#REF!`** (sheet 名が変わったため)。

#### After (named range)

```python
# three_statement_builder.py (refactored)
ws_is["D5"] = "=Rev_Total"
```

Excel で sheet を rename しても `Rev_Total` の **scope と定義 cell は不変** (workbook-scoped name は sheet 名に依存しない)。Python builder 側も sheet 名 hard-code が **0 になる**。

**判定**: named range は **sheet rename を完全に吸収** する。Phase 6 refactor の副次効果として、builder の sheet 名 dependency が消える。

### 4.4 Mini Case 4 — 行削除で `#REF!`

#### Before / After 共通

ユーザーが `02_Revenue` の B5 (Revenue Total 行) を **誤って削除** すると、cell anchor も named range も **どちらも `#REF!`** になる。

named range の挙動:

```
=Rev_Total   →   #REF!
```

しかし **Name Manager で `Rev_Total` の定義を見ると `'02_Revenue'!#REF!`** と表示される。これは「どこかで Rev_Total が必要だが定義 cell が消えた」と即視認できる **diagnostic 価値** がある。cell anchor 直書きの場合は `'02_Revenue'!#REF!` が直接 cell に表示されるが、**どの name が壊れたか追跡が困難**。

**判定**: 行削除自体はどちらの方式でも壊れる (= データロス)。但し named range の方が **Name Manager で破損 location が一覧化される** 利点あり。

### 4.5 Mini Case 5 — LibreOffice / Numbers 互換性 (scope 解釈差)

xlsx を **LibreOffice Calc** で開いた場合:

- workbook-scoped name: ✅ 完全互換
- sheet-scoped name: ✅ 互換 (LibreOffice 5.0+)
- name with special chars (例: `Rev_$Total`): ⚠️ LibreOffice が拒否する場合あり (本書では特殊文字を全 NG にしているので影響なし)

**Apple Numbers** で開いた場合:

- workbook-scoped name: ⚠️ Numbers は workbook-scoped に変換し直すが、**保存し直すと Excel-scope 情報が失われる**
- sheet-scoped name: ❌ Numbers は sheet-scoped を **workbook-scoped に強制変換** → 保存後 Excel に戻すと **同名衝突** 発生

**Google Sheets** で開いた場合:

- workbook-scoped name: ✅ 互換 (Named ranges 機能)
- sheet-scoped name: ⚠️ Google Sheets は sheet-scoped を **サポートしない** (全 named range が workbook-scoped 扱い) → 同名衝突する場合あり

**判定**: 本 skill の出力 xlsx は **Excel での編集を主想定**。LibreOffice は OK、Numbers / Google Sheets は **named range 互換 rendering で開けるが、再保存後の Excel 戻しは保証しない** ことを `00_Cover` の Notes 欄で明記する。

#### Before / After 比較表 (mini case 1-5 まとめ)

| Mini Case | Cell anchor 直書き | Named range |
|---|---|---|
| 1. 行挿入 | ⚠️ Excel version 依存で壊れる | ✅ 不変 |
| 2. 列追加 | ⚠️ 各 builder hard-code 全修正 | ✅ Year_Headers + Period_Count 更新で連動 |
| 3. Sheet rename | ✅ Excel が自動更新するが builder code が古い | ✅ 完全に sheet 名独立 |
| 4. 行削除 | ❌ `#REF!` (追跡困難) | ❌ `#REF!` (Name Manager で diagnose 容易) |
| 5. 他 app 互換 | ✅ どこでも開ける | ⚠️ Numbers は scope 変換、Google Sheets は workbook-only |

---

## 5. openpyxl 実装規約 (3.1.x Verified)

> **Verified against**: openpyxl 3.1.5 (`openpyxl.workbook.defined_name` module、empirical round-trip test 2026-05-02 by Phase 6 Wave 1 実装)。`scripts/ib_format.py` lines 1030-1262 が canonical 実装、本書はその実装を反映する **正本** である。重要事実:
>
> - `DefinedName(name=..., attr_text=...)` がコンストラクタの正規呼び出し。`value=...` は `attr_text` の **alias** (`value = Alias("attr_text")`) なので可換だが本書は `attr_text` を canonical とする
> - **scope は `localSheetId` 属性で決まる**:
>   - `localSheetId=None` (default) → workbook-scoped (`wb.defined_names` に格納)
>   - `localSheetId=<ws_index>` → sheet-scoped (`ws.defined_names` に格納、該当 sheet のみで bare name 解決)
> - **openpyxl 3.1.x では `wb.defined_names` / `ws.defined_names` は `DefinedNameDict` (dict subclass)**。`.append()` メソッドは持たず、`AttributeError: 'DefinedNameDict' object has no attribute 'append'` を empirical に raise する。canonical な登録パターンは **dict-style assignment**:
>   - workbook-scoped: `wb.defined_names[name] = DefinedName(name=name, attr_text=...)`
>   - sheet-scoped: `ws.defined_names[name] = DefinedName(name=name, attr_text=..., localSheetId=<idx>)`
> - 旧 `DefinedNameList` (Sequence) で使っていた `.append()` / `.definedName` 内部アクセスは 3.1.x では使えない。本書 v1.1 (2026-05-02) で `.append()` ベースの記述を全面修正した
> - 上書き (同名再登録) は **同 key への単純代入** で OK。専用 helper は不要
> - 削除は `del wb.defined_names[name]` / `del ws.defined_names[name]`

### 5.1 Workbook-scoped name の登録

```python
from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName


def register_workbook_name(
    wb: Workbook,
    name: str,
    sheet_title: str,
    cell_ref: str,
) -> DefinedName:
    """Register `name` as workbook-scoped pointing to '<sheet>'!<cell_ref>.

    canonical API (openpyxl 3.1.x):
        wb.defined_names[name] = DefinedName(name=name, attr_text=...)

    Example:
        register_workbook_name(wb, "Rev_Total", "02_Revenue", "$B$5")
        # → '=Rev_Total' で workbook 内の任意 cell から参照可

    Args:
        wb: openpyxl Workbook
        name: 名前 (canonical = §2 table から)
        sheet_title: 定義 cell のあるシート名
        cell_ref: 絶対参照表記 ($B$5 / $D$5:$AA$5 など)

    Returns:
        登録された DefinedName
    """
    full_ref = f"'{sheet_title}'!{cell_ref}"
    dn = DefinedName(name=name, attr_text=full_ref)
    # localSheetId=None (default) で workbook-scoped。dict-like 代入で登録
    wb.defined_names[name] = dn
    return dn
```

### 5.2 Sheet-scoped name の登録

```python
def register_sheet_name(
    ws,                  # openpyxl Worksheet
    name: str,
    cell_ref: str,
) -> DefinedName:
    """Register `name` as scoped to worksheet `ws`.

    Sheet-scoped name は同 sheet 内では bare name (=Rev_Subscription) で参照可、
    他 sheet からは '02_Revenue'!Rev_Subscription で qualified ref が必要。

    canonical API (openpyxl 3.1.x):
        ws.defined_names[name] = DefinedName(
            name=name, attr_text=..., localSheetId=ws_index
        )

    Args:
        ws: openpyxl Worksheet (定義先 sheet)
        name: 名前
        cell_ref: 絶対参照表記

    Returns:
        登録された DefinedName

    Note: localSheetId は in-memory inspection の整合性のために明示する。
    save 時に openpyxl が ws 位置から自動付与もするが、明示することで
    load 後との一貫性が取れる。登録先は **必ず `ws.defined_names`** (DefinedNameDict)。
    """
    wb = ws.parent
    full_ref = f"'{ws.title}'!{cell_ref}"
    sheet_id = wb.index(ws)
    dn = DefinedName(
        name=name,
        attr_text=full_ref,
        localSheetId=sheet_id,  # ← この属性で sheet-scoped と判別
    )
    ws.defined_names[name] = dn
    return dn
```

### 5.2.1 Sheet-scoped + Range の組合せ (`Rev_Subscription` D6:AA6 等)

```python
def register_sheet_range_name(
    ws,                  # openpyxl Worksheet
    name: str,
    range_ref: str,
) -> DefinedName:
    """Sheet-scoped name で range (例: $D$6:$AA$6) を登録。

    用法は §5.2 と同じだが range_ref を渡す点のみ異なる。実装は同一なので
    呼び出し側の意図を明示するための名前付き wrapper。

    Example:
        register_sheet_range_name(ws_rev, "Rev_Subscription", "$D$6:$AA$6")
    """
    wb = ws.parent
    full_ref = f"'{ws.title}'!{range_ref}"
    sheet_id = wb.index(ws)
    dn = DefinedName(
        name=name,
        attr_text=full_ref,
        localSheetId=sheet_id,
    )
    ws.defined_names[name] = dn
    return dn
```

### 5.3 利便 wrapper (推奨 API)

3 builder で共通利用するため `ib_format.py` に薄い wrapper を追加 (Phase 6 Wave 1 実装済、`scripts/ib_format.py` § `register_named_range`):

```python
# scripts/ib_format.py (Phase 6 Wave 1 — 実装済)

from typing import Literal
from openpyxl.cell.cell import Cell
from openpyxl.workbook.defined_name import DefinedName


def register_named_range(
    cell: Cell,
    name: str,
    *,
    scope: Literal["workbook", "sheet"] = "workbook",
) -> DefinedName:
    """openpyxl cell から named range を登録する thin wrapper。

    Phase 6 Wave 1 で導入。scope=workbook を default にしている理由:
    cross-sheet で参照される line item の方が圧倒的に多く、sheet-scoped は
    sheet 内中間値に限定 (本書 §1.1 判定ルール)。

    内部では `register_workbook_name` / `register_sheet_name` に delegate し、
    どちらも canonical な dict-style assignment (§5.1, §5.2) を行う。

    Args:
        cell: openpyxl Cell オブジェクト (= ws['B5'] 等)
        name: §2 canonical table から取った名前
        scope: "workbook" or "sheet"

    Example:
        c = ws.cell(row=5, column=2)
        c.value = "=SUM(B6:B11)"
        register_named_range(c, "Rev_Total", scope="workbook")
    """
    if scope == "workbook":
        return register_workbook_name(
            cell=cell, wb=cell.parent.parent, name=name
        )
    elif scope == "sheet":
        return register_sheet_name(ws=cell.parent, name=name, cell=cell)
    else:
        raise ValueError(
            f"Invalid scope: {scope!r} (expected 'workbook' or 'sheet')"
        )
```

> 実装の `register_workbook_name` / `register_sheet_name` は cell 引数 + sheet_title/cell_ref 引数の overload を取り、内部で `_abs_coord()` を使って未絶対化形式 (`B5`) を自動で `$B$5` に変換する。詳細は `scripts/ib_format.py` を参照。

### 5.4 Range 系 named range の登録 (`Year_Headers` 等)

range (D2:AA2) を name に bind する場合は `register_range_name` を使う:

```python
def register_range_name(
    ws,                  # openpyxl Worksheet
    name: str,
    range_str: str,
    *,
    scope: Literal["workbook", "sheet"] = "workbook",
) -> DefinedName:
    """範囲 (multi-cell range) を name に bind して登録。

    Year_Headers / Rev_Total (range 形式) / DCF_FCFF (D11:AA11) 等に使う。

    Args:
        ws: openpyxl Worksheet (定義先 sheet)
        name: §2 canonical table から取った name
        range_str: 絶対参照表記 ($D$5:$AA$5 等) — caller が完全な absolute ref を用意
        scope: "workbook" (default) / "sheet"

    Example:
        register_range_name(ws_assump, "Year_Headers", "$D$2:$AA$2",
                            scope="workbook")
    """
    wb = ws.parent
    full_ref = f"'{ws.title}'!{range_str}"
    if scope == "workbook":
        dn = DefinedName(name=name, attr_text=full_ref)
        wb.defined_names[name] = dn
    elif scope == "sheet":
        sheet_id = wb.index(ws)
        dn = DefinedName(name=name, attr_text=full_ref, localSheetId=sheet_id)
        ws.defined_names[name] = dn
    else:
        raise ValueError(f"Invalid scope: {scope!r}")
    return dn
```

### 5.5 既存 name の上書き / 削除

`DefinedNameDict` (dict subclass) なので **同 key への単純代入で上書き可**。専用 helper は不要:

```python
# 上書き (= 同名再登録)
wb.defined_names["Rev_Total"] = DefinedName(name="Rev_Total", attr_text=new_ref)

# Sheet-scoped name の上書き (登録先は ws.defined_names)
sheet_id = wb.index(ws)
ws.defined_names["Rev_Subscription"] = DefinedName(
    name="Rev_Subscription", attr_text=new_ref, localSheetId=sheet_id
)

# 削除 (workbook-scoped)
del wb.defined_names["Rev_Total"]

# 削除 (sheet-scoped) — 該当 ws の dict から
del ws.defined_names["Rev_Subscription"]

# 存在チェック
if "Rev_Total" in wb.defined_names:
    ...
```

> 旧 `DefinedNameList` 時代の `_remove_name_if_exists` ヘルパー (sequence の filter rebuild) は不要。3.0+ の dict subclass では `del` / `__setitem__` の atomic 操作で十分。

### 5.6 全 name の列挙 (debug 用)

openpyxl 3.1.x では workbook-scoped と sheet-scoped が **別々の DefinedNameDict** に格納されるため、両方を walk する。`DefinedNameList.by_sheet()` は本 version では存在しない (旧 API、deprecated)。canonical な列挙パターン (`scripts/ib_format.py` § `list_workbook_names` と同じ):

```python
def list_all_names(wb: Workbook) -> list[tuple[str, str, str]]:
    """全 named range を (name, scope_label, ref) の tuple list で返す。

    Returns:
        sorted list. scope_label は "workbook" or "sheet[<idx>]:<title>"。
    """
    out: list[tuple[str, str, str]] = []
    # workbook-scoped: wb.defined_names を直接 iterate
    for nm, dn in wb.defined_names.items():
        out.append((nm, "workbook", dn.attr_text or ""))
    # sheet-scoped: 各 ws.defined_names を iterate
    for idx, ws in enumerate(wb.worksheets):
        for nm, dn in ws.defined_names.items():
            out.append((nm, f"sheet[{idx}]:{ws.title}", dn.attr_text or ""))
    return sorted(out)
```

> 本実装は `scripts/ib_format.py` § `list_workbook_names` (line 1246-1262) と同一パターン。D12 sanity check (named range coverage 計測) もこの walker を使用。

### 5.7 openpyxl version 互換性メモ

| openpyxl version | API 挙動 |
|---|---|
| 2.6.x | `wb.defined_names` は `DefinedNameList` (Sequence)。`.append(DefinedName(...))` のみ。`wb.defined_names[name] = ...` は **未対応** |
| 3.0.x | `wb.defined_names` が `DefinedNameDict` (dict subclass) に変更。dict-like 代入が canonical に。`.append()` は **削除** され `AttributeError` を raise |
| 3.1.x | **本書の前提 version**。`attr_text` parameter が canonical (`value` は alias)。empirical 検証で `wb.defined_names[name] = DefinedName(...)` round-trip OK |
| 3.2+ | API 変化なし (継続互換) |

**本書は dict-style assignment (`wb.defined_names[name] = ...` / `ws.defined_names[name] = ...`) を canonical method として採用** (3.0+ の `DefinedNameDict` 互換)。`.append()` ベースの古い記述は v1.1 (2026-05-02) で削除済。本 skill の `requirements.txt` は **openpyxl 3.1.x 以上** を前提とする。

---

## 6. ib_format.py 拡張提案 (apply_*  signature)

`apply_hard_input` / `apply_formula` / `apply_link_intra` の signature を拡張し、`named_range` 引数で自動 register できるようにする:

### 6.1 拡張前 (Phase 5)

```python
def apply_hard_input(cell, fmt: str = FMT_JPY_MILLION) -> None:
    cell.font = FONT_HARD_INPUT
    cell.number_format = fmt
    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)
```

### 6.2 拡張後 (Phase 6 Wave 1) — 選択肢 A canonical

`fmt` を positional 互換のため `cell` 直後に維持し、`named_range` / `scope` を keyword-only にする (§6.3 で詳述):

```python
def apply_hard_input(
    cell,
    fmt: str = FMT_JPY_MILLION,
    *,
    named_range: str | None = None,
    scope: Literal["sheet", "workbook"] = "workbook",
) -> None:
    """Hard input セルに IB blue + 数値書式を適用 (wrap_text=False).

    Phase 6 Wave 1 拡張: `named_range` 引数を渡すと自動で workbook (or sheet)
    scoped named range を登録する。canonical 命名は references/_named_ranges.md §2。

    Args:
        cell: openpyxl Cell
        fmt: number_format (positional 互換 — 既存 caller の互換性のため)
        named_range: §2 canonical table の名前 (None ならスキップ、kwarg only)
        scope: "workbook" (default) / "sheet" (kwarg only)

    Example:
        # 02_Revenue B5 = Revenue (total)
        c = ws.cell(row=5, column=2)
        c.value = 2400  # ユーザー入力 hard
        apply_hard_input(c, named_range="Rev_Total", scope="workbook")

        # 既存 positional caller は無修正で動く:
        apply_hard_input(c, FMT_USD_MILLION)
    """
    cell.font = FONT_HARD_INPUT
    cell.number_format = fmt
    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)
    if named_range is not None:
        register_named_range(cell, named_range, scope=scope)


def apply_formula(
    cell,
    fmt: str = FMT_JPY_MILLION,
    *,
    named_range: str | None = None,
    scope: Literal["sheet", "workbook"] = "workbook",
) -> None:
    cell.font = FONT_FORMULA
    cell.number_format = fmt
    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)
    if named_range is not None:
        register_named_range(cell, named_range, scope=scope)


def apply_link_intra(
    cell,
    fmt: str = FMT_JPY_MILLION,
    *,
    named_range: str | None = None,
    scope: Literal["sheet", "workbook"] = "workbook",
) -> None:
    cell.font = FONT_LINK_INTRA
    cell.number_format = fmt
    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)
    if named_range is not None:
        register_named_range(cell, named_range, scope=scope)
```

### 6.3 後方互換性 (重要: 既存 caller の確認必須)

新シグネチャは `named_range` 等を **キーワード引数 (after `*`)** にしているので、`apply_hard_input(cell)` のような単純な positional 呼び出しは無修正で動く。

**ただし**、現状 (Phase 5) の builder には `apply_formula(c, ib.FMT_PERCENT_BPS)` のような **`fmt` を positional 第 2 引数で渡す** caller が `valuation_builder.py` (40+ 箇所) と `three_statement_builder.py` 等に存在する。本書 signature 案では `*` を `cell` の **直後** に置いているため、これらの呼び出しは **TypeError** で破綻する。

**選択肢 A (推奨)**: `*` の位置を変えて `fmt` を positional でも渡せるようにする:

```python
def apply_hard_input(
    cell,
    fmt: str = FMT_JPY_MILLION,         # ← positional 互換のため後ろに置かない
    *,
    named_range: str | None = None,
    scope: Literal["sheet", "workbook"] = "workbook",
) -> None:
    ...
```

これなら既存 `apply_formula(c, ib.FMT_PERCENT_BPS)` (positional) は **無修正で動く**。新規 caller は `apply_hard_input(c, named_range="Rev_Total")` (kwarg) で OK。

**選択肢 B**: 全 既存 caller を一括 grep + sed で `apply_formula(c, fmt=ib.FMT_X)` に書換 (= explicit kwarg 化)。Wave 1 のスコープがやや膨らむが、long-term の signature 一貫性は高い。

**本書の canonical 推奨は 選択肢 A** (Wave 1 のスコープ最小化のため)。`fmt` を positional 互換にしたうえで、`named_range` / `scope` を keyword-only にする。

### 6.4 既存 caller 一括検査 (Wave 1.0 pre-check)

Wave 1 着手前に必ず実行:

```bash
# positional fmt を使っている caller の数を確認
grep -rn 'apply_\(formula\|hard_input\|link_intra\|link_external\)(' \
  scripts/*.py \
  | grep -vE 'def apply_|fmt=' \
  | wc -l
```

期待: 該当数 = 選択肢 A の互換性で吸収される件数。 該当 0 件なら選択肢 B も無コストで採用可。

### 6.4 テスト方針

`apply_hard_input(cell, named_range="Rev_Total", scope="workbook")` の単体テスト:

```python
# tests/test_ib_format_named_ranges.py
def test_apply_hard_input_with_named_range():
    wb = Workbook()
    ws = wb.active
    ws.title = "02_Revenue"
    cell = ws.cell(row=5, column=2)
    cell.value = 2400
    apply_hard_input(cell, named_range="Rev_Total", scope="workbook")

    # name が登録されているか
    assert "Rev_Total" in wb.defined_names
    dn = wb.defined_names["Rev_Total"]
    assert "02_Revenue" in dn.attr_text
    assert "$B$5" in dn.attr_text or "B5" in dn.attr_text

    # font が hard input
    assert cell.font.color.rgb.endswith("0000FF")
```

---

## 7. Builder 適用パターン (3 builder 共通)

### 7.1 Bad (Phase 5 cell anchor) → Good (Phase 6 named range)

#### `_build_is` の Revenue link (Before)

```python
def _build_is(ws, inp):
    # ...
    for m in range(num_periods):
        c = ws.cell(row=5, column=col_for_period(m))
        c.value = f"={sref('02_Revenue', period_cell(m, 5))}"
        apply_link_intra(c)
```

#### After (named range)

```python
def _build_is(ws, inp):
    # ...
    for m in range(num_periods):
        c = ws.cell(row=5, column=col_for_period(m))
        # 各期 cell が IS_Revenue の単一 element を指す
        # IS_Revenue が range 系 named range なら =INDEX(IS_Revenue, m+1) で個別期取得
        # 但し row 単位の name は cross-sheet 単純 alias でいいので:
        c.value = f"=Rev_Total"  # ← 同列の Rev_Total を引く
        # 但し列方向に shift が必要な場合は INDEX/OFFSET と組み合わせ
```

実用パターン (各期セル単位での参照):

```python
# 02_Revenue で Rev_Total を range として登録 ($D$5:$AA$5)
register_workbook_range_name(wb, "Rev_Total", "02_Revenue", "$D$5:$AA$5")

# 04_IS の D5 セルから個別期参照
def _build_is(ws_is, inp, num_periods=24, start_col=4):
    for m in range(num_periods):
        c = ws_is.cell(row=5, column=start_col + m)
        # INDEX で m+1 期目を取る (1-indexed)
        c.value = f"=INDEX(Rev_Total, {m + 1})"
        apply_link_intra(c)
```

または **単一 cell name で各期を別々に登録** する場合 (より素朴):

```python
# 02_Revenue の D5, E5, F5 ... を Rev_Total_Y1, Rev_Total_Y2, ... と個別登録
for m in range(num_periods):
    period_idx = m + 1
    cell = ws_rev.cell(row=5, column=start_col + m)
    register_named_range(cell, f"Rev_Total_Y{period_idx}", scope="workbook")

# 04_IS で各期を引く
for m in range(num_periods):
    c = ws_is.cell(row=5, column=start_col + m)
    c.value = f"=Rev_Total_Y{m + 1}"
```

**判定**: range 系 name + INDEX を使うパターンが **scalable** (期数追加で個別 name 増加なし)。但し可読性は単一 cell name の方が高い。**本 skill では range 系 + INDEX を canonical** とする (期数追加耐性を優先)。

### 7.2 Mini Case: `_build_is` Revenue link

実装の完全形 (Phase 6):

```python
def _build_is(ws_is: Worksheet, inp: ModelInput) -> None:
    """04_IS を build。Revenue / COGS / OpEx を 03/04 から named range で link。"""
    ib.apply_section_header(ws_is.cell(row=1, column=2), "05 — Income Statement")
    ws_is.cell(row=2, column=2).value = "(JPY M)"

    # Year headers (workbook-scoped Year_Headers から)
    for m in range(inp.num_periods):
        c = ws_is.cell(row=3, column=4 + m)
        c.value = f"=INDEX(Year_Headers, {m + 1})"
        apply_link_intra(c, fmt=FMT_DATE_YM)

    # Row 5: Revenue
    ws_is.cell(row=5, column=2).value = "Revenue"
    for m in range(inp.num_periods):
        c = ws_is.cell(row=5, column=4 + m)
        c.value = f"=INDEX(Rev_Total, {m + 1})"
        apply_link_intra(c, named_range=None)  # IS_Revenue は別途 range 登録

    # IS_Revenue range の登録
    register_workbook_range_name(
        wb=ws_is.parent,
        name="IS_Revenue",
        sheet_title=ws_is.title,
        range_ref=f"$D$5:${get_column_letter(3 + inp.num_periods)}$5",
    )

    # Row 6: COGS (link from 03_OpEx Cost_COGS)
    ws_is.cell(row=6, column=2).value = "COGS"
    for m in range(inp.num_periods):
        c = ws_is.cell(row=6, column=4 + m)
        c.value = f"=-INDEX(Cost_COGS, {m + 1})"  # 符号注意 (IS で表示 negative)
        apply_link_intra(c)

    # Row 7: Gross Profit
    ws_is.cell(row=7, column=2).value = "Gross Profit"
    for m in range(inp.num_periods):
        c = ws_is.cell(row=7, column=4 + m)
        c.value = f"=INDEX(IS_Revenue, {m + 1})+INDEX(IS_COGS, {m + 1})"
        apply_formula(c)

    # IS_GrossProfit range 登録
    register_workbook_range_name(
        wb=ws_is.parent,
        name="IS_GrossProfit",
        sheet_title=ws_is.title,
        range_ref=f"$D$7:${get_column_letter(3 + inp.num_periods)}$7",
    )

    # ... 続いて OpEx, EBITDA, EBIT, NI まで
```

---

## 8. マイグレーション手順 (3 builder 適用ガイド)

### 8.1 全体方針

各 builder で以下を **wave** で適用:

0. **Wave 1.0 (pre-check)**: 既存 caller の signature 互換性確認 (§6.4 の grep)、openpyxl version 確認 (`pip show openpyxl` で 3.1.x 以上)、現状の cross-sheet ref 件数 baseline 計測
1. **Wave 1.1**: `register_workbook_name` / `register_sheet_name` / `register_workbook_range_name` / `register_sheet_range_name` / `register_named_range` を `ib_format.py` に追加 (§5.1-5.4 全 helper)
2. **Wave 1.2**: `apply_hard_input` / `apply_formula` / `apply_link_intra` の signature 拡張 (selection 肢 A: `fmt` positional 互換 + `named_range` / `scope` kwarg only — §6.2 / §6.3)
3. **Wave 1.3**: 各 builder で `_register_names(wb)` 関数を実装、build 開始時に全 named range を一括登録 (本書 §A.2 snippet を参考)
4. **Wave 1.4**: cross-sheet 参照箇所を `=INDEX(<Name>, period_idx)` に書換
5. **Wave 1.5**: sanity_checks.py に **D12: Named Range Coverage** check を追加 (§9)
6. **Wave 1.6**: 行挿入テスト (mini case 1) を `tests/` に追加し CI で fail 検出
7. **Wave 1.7**: `_self_review_protocol.md §8` に 6 番目の check (行/列 insertion robustness self-test) を追加

### 8.2 Step-by-step (three_statement_builder.py の例)

#### Step 1: 全 named range を一括登録する関数を追加

```python
def _register_names(wb: Workbook, inp: ModelInput) -> None:
    """Phase 6 Wave 1: 全 cross-sheet 参照を named range で集約管理。

    canonical naming: references/_named_ranges.md §2
    """
    last_col = get_column_letter(3 + inp.num_periods)

    # ----- Cross-sheet aggregator -----
    register_workbook_range_name(
        wb, "Year_Headers", "01_Assumptions", f"$D$2:${last_col}$2"
    )
    register_workbook_name(wb, "Period_Count", "01_Assumptions", "$D$3")
    register_workbook_name(wb, "Currency_Code", "01_Assumptions", "$C$6")
    register_workbook_name(wb, "Scale_Display", "01_Assumptions", "$C$8")
    register_workbook_name(wb, "Tax_Rate_Effective", "01_Assumptions", "$C$10")

    # ----- 02_Revenue -----
    register_workbook_range_name(wb, "Rev_Total", "02_Revenue", f"$D$5:${last_col}$5")
    rev_idx = wb.index(wb["02_Revenue"])  # sheet-scoped name に必要な index
    register_sheet_range_name(
        wb, rev_idx, "Rev_Subscription",
        "02_Revenue", f"$D$6:${last_col}$6",
    )
    register_sheet_range_name(
        wb, rev_idx, "Rev_Services",
        "02_Revenue", f"$D$7:${last_col}$7",
    )
    # ... §2 の table を全 entry 登録 (sheet-scoped は同じ ws_index を使い回す)

    # ----- 03_OpEx -----
    register_workbook_range_name(wb, "Cost_COGS", "03_OpEx", f"$D$10:${last_col}$10")
    register_workbook_range_name(wb, "Profit_Gross", "03_OpEx", f"$D$12:${last_col}$12")
    register_workbook_range_name(wb, "OpEx_SM", "03_OpEx", f"$D$16:${last_col}$16")
    register_workbook_range_name(wb, "OpEx_RD", "03_OpEx", f"$D$19:${last_col}$19")
    register_workbook_range_name(wb, "OpEx_GA", "03_OpEx", f"$D$21:${last_col}$21")
    register_workbook_range_name(wb, "OpEx_Total", "03_OpEx", f"$D$23:${last_col}$23")
    # ...

    # ----- 04_IS -----
    register_workbook_range_name(wb, "IS_Revenue", "04_IS", f"$D$5:${last_col}$5")
    register_workbook_range_name(wb, "IS_GrossProfit", "04_IS", f"$D$7:${last_col}$7")
    register_workbook_range_name(wb, "IS_EBITDA", "04_IS", f"$D$14:${last_col}$14")
    register_workbook_range_name(wb, "IS_EBIT", "04_IS", f"$D$17:${last_col}$17")
    register_workbook_range_name(wb, "IS_NI", "04_IS", f"$D$24:${last_col}$24")
    # ...
```

#### Step 2: build flow に register 呼び出しを追加

```python
def build_three_statement(inp: ModelInput, output_path: Path) -> None:
    wb = Workbook()
    sheets = _create_sheets(wb)

    # ★ Phase 6 Wave 1: 全 named range を build より先に登録
    _register_names(wb, inp)

    # 既存 build 呼び出し
    _build_assumptions(sheets["01_Assumptions"], inp)
    _build_drivers(sheets["11_KPI_Dashboard"], inp)
    _build_revenue(sheets["02_Revenue"], inp)
    _build_opex(sheets["03_OpEx"], inp)
    _build_is(sheets["04_IS"], inp)
    _build_bs(sheets["05_BS"], inp)
    _build_cfs(sheets["06_CFS"], inp)
    # ...

    wb.save(output_path)
```

#### Step 3: 各 _build_* 内の cross-sheet 参照を named range に書換

Diff 例:

```diff
 def _build_is(ws_is, inp):
     for m in range(inp.num_periods):
         c = ws_is.cell(row=5, column=4 + m)
-        c.value = f"={sref('02_Revenue', period_cell(m, 5))}"
+        c.value = f"=INDEX(Rev_Total, {m + 1})"
         apply_link_intra(c)
```

#### Step 4: sanity_checks.py に D12 check を追加 (§9 参照)

#### Step 5: 行挿入 self-test を実装

```python
# tests/test_named_range_robustness.py

def test_row_insertion_does_not_break_is_link():
    """Mini case 1: 02_Revenue で行挿入しても 04_IS の Revenue が壊れないこと"""
    wb = build_test_workbook()  # 上記 _register_names 適用済

    # 02_Revenue の B6 と B7 の間に新行を挿入 (シミュレーション)
    ws_rev = wb["02_Revenue"]
    ws_rev.insert_rows(idx=7)

    # 再 save / 再 load
    wb.save("/tmp/test_named_ranges.xlsx")
    wb2 = openpyxl.load_workbook("/tmp/test_named_ranges.xlsx")

    # Rev_Total の名前が依然 正しい cell を指しているか
    rev_total = wb2.defined_names["Rev_Total"]
    assert "$B$5" in rev_total.attr_text or "$D$5" in rev_total.attr_text  # 元の B5 維持
    # または auto-shift で $B$5 のまま (Total 行は B5 のまま)
```

### 8.3 Wave 1 の完了条件

- [ ] `ib_format.py` に register_named_range / register_workbook_range_name 追加
- [ ] `apply_hard_input` / `apply_formula` / `apply_link_intra` に named_range kwarg 追加
- [ ] three_statement_builder.py で `_register_names` 実装、§2 §2.1-2.7 全 entry 登録
- [ ] cap_table_builder.py で §2.8 全 entry 登録
- [ ] valuation_builder.py で §2.9-2.13 全 entry 登録
- [ ] sanity_checks.py に D12 (Named Range Coverage) 追加
- [ ] tests/test_named_range_robustness.py に mini case 1-3 を実装
- [ ] 1 案件サンプル build → ファクトチェック (Excel で開いて Name Manager 確認)

### 8.4 想定リスクと対処

| リスク | 兆候 | 対処 |
|---|---|---|
| Name Manager に 100+ name で UI 重い | Excel UI が遅い | 重要度低い sheet-scoped を削減、本書 §2 で **sheet-scoped に分類した item から優先削除** |
| INDEX(Range, idx) で循環参照 | 三表突合が壊れる | INDEX の対象 range が同 sheet 内かどうか確認、cross-sheet INDEX のみに限定 |
| INDEX 内の row 番号 mismatch | period 軸が 1 ずれて表示 | `m + 1` (1-indexed) を全て統一、test で 5 期分 check |
| openpyxl 古 version で `wb.defined_names[name] = ...` 動かず | Build error | requirements.txt で openpyxl 3.1+ 固定 |
| LibreOffice で開いて scope 変換 | 互換性 issue | `00_Cover` Notes に「Excel 想定、再保存後の他 app 互換は保証しない」明記 |

---

## 9. Sanity Check 連携 (D12: Named Range Coverage)

`scripts/sanity_checks.py` に新規 check D12 を追加する仕様:

### 9.1 Check Specification

| 項目 | 内容 |
|---|---|
| ID | D12 |
| Name | Named Range Coverage |
| Severity | **soft_warn** (cell anchor が完全 NG ではない、但し refactor 推奨) |
| 期待 | 全 cross-sheet reference が named range 経由 |
| 検出 | workbook 内の formula で `'<sheet>'!$X$Y` 形式を grep、named range 由来でないものを抽出 |

### 9.2 Implementation

```python
import re
from openpyxl import load_workbook


def check_d12_named_range_coverage(wb_path: Path) -> dict:
    """D12: Named Range Coverage check.

    全 cross-sheet ref が named range 経由か検査。`'<sheet>'!$cell` パターンを
    detect し、それが named range の attr_text にも含まれない (= bare cell anchor
    直書き) なら WARN。

    Returns:
        {
            "passed": bool,
            "warns": list[dict] (cell location + raw formula),
            "summary": str,
        }
    """
    wb = load_workbook(wb_path, data_only=False)

    # 全 named range の attr_text を集めて、name で reference できる cell を集合化
    name_refs = set()
    for name, dn in wb.defined_names.items():
        name_refs.add(dn.attr_text)
    for ws in wb.worksheets:
        for name, dn in ws.defined_names.items():
            name_refs.add(dn.attr_text)

    # 各 cell の formula を走査
    pattern = re.compile(r"'([^']+)'!(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)")

    warns = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None or not isinstance(cell.value, str):
                    continue
                if not cell.value.startswith("="):
                    continue
                # cross-sheet ref を抽出
                for m in pattern.finditer(cell.value):
                    sheet_ref = m.group(1)
                    cell_ref = m.group(2)
                    full_ref = f"'{sheet_ref}'!{cell_ref}"
                    if full_ref not in name_refs:
                        # named range からの曝露でない bare cross-sheet ref
                        warns.append({
                            "sheet": ws.title,
                            "cell": cell.coordinate,
                            "formula": cell.value,
                            "bare_ref": full_ref,
                        })

    return {
        "passed": len(warns) == 0,
        "warns": warns,
        "summary": (
            f"D12 Named Range Coverage: {len(warns)} bare cross-sheet refs found"
            if warns else "D12 Named Range Coverage: PASS"
        ),
    }
```

### 9.3 Mini Case (D12 grep 出力例)

build した xlsx を D12 で走査、結果:

```
D12 Named Range Coverage: 3 bare cross-sheet refs found
  ⚠️  '05_BS'!D5: ='06_CFS'!$D$35     (raw cross-sheet, expected: =CF_EndCash)
  ⚠️  '05_BS'!D7: ='05_BS § Working Capital'!$D$5*'04_IS'!$D$5/365  (DSO 計算, expected: WC_DSO/IS_Revenue)
  ⚠️  '14_KPI'!D6: =('04_IS'!$D$5-'04_IS'!$C$5)/'04_IS'!$C$5  (YoY %, expected: KPI_RevGrowth)
```

→ developer は build script の該当箇所を修正し、re-run で `D12: PASS` になるまで loop。

### 9.4 D12 を 12_SanityChecks シートに表示

12_SanityChecks シートの末尾に row 追加:

```
D11: BS = L+E check                            ✅ PASS
D12: Named Range Coverage                      ⚠️ 3 warnings (see audit log)
D13: Σ check                                   ✅ PASS
```

→ Cover sheet の Notes 欄に「D12 残 warning 3 件、Phase 6 Wave 2 で解消予定」等と注記。

---

## 10. 関連 reference との整合

### 10.1 _terminology.md との関係

`_terminology.md §3` (Sheet naming canonical) で定義された 14 sheet 名 (`00_Cover` ... `13_IC_Memo`) を本書 §2 の "<sheet>'!" 部分で使用する。**sheet 名が変わったら本書 §2 も同期更新が必要**。

逆に、本書 §2 の named range の **prefix (Rev_, ARR_, IS_ など)** は `_terminology.md` には登場しない (本書独自の命名規約)。同名衝突回避のため `_terminology.md` 改訂時に「prefix を予約済として list する」項目を新設することが望ましい (将来 enhancement)。

### 10.2 00_design_guidelines.md との関係

`00_design_guidelines.md` の機能色 (`#0000FF` hard input / `#008000` cross-sheet link) と **本書は独立軸**。named range は **名前のみ** を canonical 化し、**表示色** は別軸 (link 色 = #008000 のまま、name で参照していても色は cross-sheet link green を適用)。

実装上の duty:
- `apply_link_intra(c, named_range="Rev_Total")` → cell の色は green (機能色 `#008000`) で、formula は `=INDEX(Rev_Total, ...)` で書く

### 10.3 06_three_statement.md との関係

`06_three_statement.md §2` の各 sheet row 構成 (Revenue B5 / IS Revenue D5 等) と本書 §2 は **相互参照**。`06` 改訂で row 構成が変わったら、本書 §2 の "推定 cell (anchor)" 列を同期更新。逆に本書で named range を追加したら `06` で言及されるべき item に整合する。

具体的な対応:

| `06_three_statement.md §2` 記述 | 本書 §2 該当 |
|---|---|
| §2.1 IS Revenue row | §2.3 IS_Revenue |
| §2.2 BS Cash row | §2.4 BS_Cash |
| §2.3 CFS L1 (Net Income → RE) | §2.5 CF_NI / §2.4 BS_RE |
| §2.4 BS plug (Cash or Revolver) | §2.4 BS_Cash + §2.7 Debt_Ending |

### 10.4 04b_cap_table_mechanics.md との関係

`04b §1.3` Diluted Share Count (TSM) で算出される FDSO は本書 §2.8 `Cap_FDSO` (workbook-scoped) として canonical 化。`04b` 改訂で TSM 計算式が変わっても **name 自体は不変**。

### 10.5 05_valuation_wacc.md との関係

`05` の DCF 計算は本書 §2.9 `DCF_FCFF` / `DCF_WACC` / `DCF_EV` を使用。`05` の WACC 計算式 (§3) と本書 §2.9 の row 構成 (NOPAT → FCFF → PV → EV) は **構造一致** すべき。

### 10.6 17_chart_design.md との関係

KPI Dashboard / Football Field のチャート source data は本書 §2.12 `KPI_*` および §2.11 `Sens_FF_*` を name 経由で参照。`17` の chart 描画コードは:

```python
# 17_chart_design.md (refactored)
chart.add_data(
    Reference(ws=wb["09_DCF § Sensitivity"], range_string="Sens_FF_Low,Sens_FF_Mid,Sens_FF_High"),
)
```

(openpyxl の `Reference` は文字列指定の named range もサポートする)

### 10.7 _self_review_protocol.md §8 との連携

`_self_review_protocol.md §8` (案件レベル Self-Review 義務化) の **5 check** に、本書適用後は **6 番目** として追加:

> 6. **行/列 insertion robustness self-test**: build した xlsx で `02_Revenue` に 1 行挿入、`04_IS` の Revenue 行が依然正しい値を返すか目視確認 (mini case 1 の手順に従う)。

---

## 11. Limitations / 既知の落とし穴

### 11.1 openpyxl API 関連

- **dict-like assignment**: `wb.defined_names[name] = DefinedName(...)` は openpyxl 3.0+ で動作。3.0 未満は `wb.defined_names.append(...)` 形式 (本 skill では 3.1+ 固定)
- **sheet-scoped scope**: `localSheetId` parameter は `DefinedName` constructor で渡す **+** `ws.defined_names[name] = ...` の両方が必要。片方だけだと scope が正しく保存されない
- **`attr_text` vs `value`**: openpyxl 3.2 で `value` parameter alias が追加されたが、`attr_text` も継続サポート。本書は `attr_text` を canonical とする (3.1 互換性のため)
- **Builder script 内の private API**: `wb._sheets` (アンダースコア付き) は public API ではない。本書では `wb.worksheets[ws_index]` を canonical とする
- **save / load 後の挙動**: openpyxl で save した後、別プロセスで load_workbook すると `defined_names` が iterable になる。dict-like access (`wb.defined_names[name]`) は load 後も動く

### 11.2 Excel UI 関連

- **Name Box 重さ**: 100+ named range で Name Box (左上の name dropdown) が重くなる。本 skill の §2 は **262 entry** だが、内 sheet-scoped 193 個は workbook の Name Box には表示されないので実害なし
- **Name Manager 検索**: Ctrl+F3 で Name Manager を開き name で filter 可。section prefix (Rev_, ARR_) で filter すると目的の name に素早くたどり着ける
- **GoTo (F5)**: F5 → name 入力で該当 cell に jump 可。debug で便利

### 11.3 他アプリ互換性

- **Apple Numbers**: sheet-scoped name を **強制 workbook-scoped 変換**。Numbers → Excel 戻しで同名衝突する
- **Google Sheets**: sheet-scoped 非サポート、全 name が workbook-scoped 扱い
- **LibreOffice Calc 5.x+**: workbook + sheet 両 scope 互換 (実用 OK)
- **Excel Online**: 全 scope 互換
- **対処**: `00_Cover` Notes 欄で「Excel desktop 推奨。他 app 互換は保証しない」と明記

### 11.4 名前 parsing 関連

- **数式内の name 解決**: `=Rev_Total + Rev_Total2` で `Rev_Total2` が未登録だと `#NAME?`。但し Excel UI の formula bar で typo を highlight しないので注意
- **大文字小文字**: Excel は case insensitive で name を解決するが、保存される文字列は **登録時の case のまま**。Python builder で必ず canonical PascalCase で書く

### 11.5 INDEX 内 row 番号

- **1-indexed**: `INDEX(Rev_Total, 1)` は range の 1 番目。Python の `m=0` で `INDEX(Rev_Total, m+1)` と書く (本書 §7 全 sample 同パターン)
- **2D range の場合**: `INDEX(Sens_EV_Matrix, row, col)` で 2 引数。1 引数だと row 全体 or col 全体を返す (Excel version 依存)

### 11.6 行/列 insertion の Excel 挙動境界

| 操作 | 名前 cell が含まれる | 挙動 |
|---|---|---|
| 行挿入 (name 行の上) | yes | name の row が +1 shift |
| 行挿入 (name 行の下) | no | name は不変 |
| 行削除 (name 行) | yes | name attr_text が `#REF!` |
| 行削除 (name 行の隣接行) | no | name は不変 |
| 列挿入 (name 列の左) | yes | name の col が +1 shift |
| 列削除 (name 列) | yes | name attr_text が `#REF!` |
| シート削除 | yes | workbook-scoped name は orphan、sheet-scoped name は同時削除 |

### 11.7 循環参照リスク

- INDEX(Rev_Total, ...) を 02_Revenue 自身が参照すると循環参照
- Cross-sheet INDEX のみに限定する rule を builder code で確立
- 同 sheet 内は cell 直接参照 (`=B5`) で OK (named range は overhead)

---

## 付録 A: Quick Reference (Phase 6 Wave 1 実装者向け)

### A.1 「cross-sheet 参照を書く」最短手順

1. 本書 §2 で対象 line item の **named range 名** を引く
2. cell formula を `=INDEX(<name>, <period_idx + 1>)` で書く
3. `apply_link_intra(cell)` で green color 適用 (named_range kwarg は不要、name は §A.2 の bulk register 関数で別途登録)

### A.2 Bulk Register Snippet

```python
# Builder の最初に呼ぶ。本書 §2 全 entry をここに集約。
def _register_all_names(wb: Workbook, num_periods: int) -> None:
    last_col = get_column_letter(3 + num_periods)

    # Cross-sheet aggregator
    register_workbook_range_name(wb, "Year_Headers", "01_Assumptions", f"$D$2:${last_col}$2")
    register_workbook_name(wb, "Period_Count", "01_Assumptions", "$D$3")
    register_workbook_name(wb, "Tax_Rate_Effective", "01_Assumptions", "$C$10")

    # 02_Revenue
    register_workbook_range_name(wb, "Rev_Total", "02_Revenue", f"$D$5:${last_col}$5")
    register_workbook_range_name(wb, "ARR_EOY", "02_Revenue", f"$D$20:${last_col}$20")

    # 03_OpEx
    register_workbook_range_name(wb, "Cost_COGS", "03_OpEx", f"$D$10:${last_col}$10")
    register_workbook_range_name(wb, "Profit_Gross", "03_OpEx", f"$D$12:${last_col}$12")
    register_workbook_range_name(wb, "OpEx_SM", "03_OpEx", f"$D$16:${last_col}$16")
    register_workbook_range_name(wb, "OpEx_RD", "03_OpEx", f"$D$19:${last_col}$19")
    register_workbook_range_name(wb, "OpEx_GA", "03_OpEx", f"$D$21:${last_col}$21")
    register_workbook_range_name(wb, "OpEx_Total", "03_OpEx", f"$D$23:${last_col}$23")
    register_workbook_range_name(wb, "FTE_Total", "03_OpEx", f"$D$32:${last_col}$32")
    register_workbook_range_name(wb, "Cost_DA", "03_OpEx", f"$D$37:${last_col}$37")
    register_workbook_range_name(wb, "Cost_SBC", "03_OpEx", f"$D$38:${last_col}$38")

    # 04_IS
    register_workbook_range_name(wb, "IS_Revenue", "04_IS", f"$D$5:${last_col}$5")
    register_workbook_range_name(wb, "IS_COGS", "04_IS", f"$D$6:${last_col}$6")
    register_workbook_range_name(wb, "IS_GrossProfit", "04_IS", f"$D$7:${last_col}$7")
    register_workbook_range_name(wb, "IS_EBITDA", "04_IS", f"$D$14:${last_col}$14")
    register_workbook_range_name(wb, "IS_EBIT", "04_IS", f"$D$17:${last_col}$17")
    register_workbook_range_name(wb, "IS_Interest", "04_IS", f"$D$19:${last_col}$19")
    register_workbook_range_name(wb, "IS_PBT", "04_IS", f"$D$21:${last_col}$21")
    register_workbook_range_name(wb, "IS_Tax", "04_IS", f"$D$22:${last_col}$22")
    register_workbook_range_name(wb, "IS_NI", "04_IS", f"$D$24:${last_col}$24")

    # 05_BS
    register_workbook_range_name(wb, "BS_Cash", "05_BS", f"$D$5:${last_col}$5")
    register_workbook_range_name(wb, "BS_AR", "05_BS", f"$D$7:${last_col}$7")
    register_workbook_range_name(wb, "BS_CurrentAssets", "05_BS", f"$D$11:${last_col}$11")
    register_workbook_range_name(wb, "BS_PPE_Net", "05_BS", f"$D$15:${last_col}$15")
    register_workbook_range_name(wb, "BS_TotalAssets", "05_BS", f"$D$22:${last_col}$22")
    register_workbook_range_name(wb, "BS_AP", "05_BS", f"$D$25:${last_col}$25")
    register_workbook_range_name(wb, "BS_CurrentLiab", "05_BS", f"$D$31:${last_col}$31")
    register_workbook_range_name(wb, "BS_LTDebt", "05_BS", f"$D$33:${last_col}$33")
    register_workbook_range_name(wb, "BS_TotalLiab", "05_BS", f"$D$39:${last_col}$39")
    register_workbook_range_name(wb, "BS_RE", "05_BS", f"$D$45:${last_col}$45")
    register_workbook_range_name(wb, "BS_TotalEquity", "05_BS", f"$D$48:${last_col}$48")

    # 06_CFS
    register_workbook_range_name(wb, "CF_Operating", "06_CFS", f"$D$14:${last_col}$14")
    register_workbook_range_name(wb, "CF_CapEx", "06_CFS", f"$D$17:${last_col}$17")
    register_workbook_range_name(wb, "CF_Investing", "06_CFS", f"$D$21:${last_col}$21")
    register_workbook_range_name(wb, "CF_Financing", "06_CFS", f"$D$29:${last_col}$29")
    register_workbook_range_name(wb, "CF_EndCash", "06_CFS", f"$D$35:${last_col}$35")
    register_workbook_range_name(wb, "CF_FCF", "06_CFS", f"$D$37:${last_col}$37")

    # 07_Debt (excerpts)
    register_workbook_range_name(wb, "Debt_Ending", "07_Debt", f"$D$10:${last_col}$10")
    register_workbook_range_name(wb, "Debt_InterestExpense", "07_Debt", f"$D$13:${last_col}$13")

    # 08_CapTable
    register_workbook_name(wb, "Cap_FDSO", "08_CapTable", "$D$5")
    register_workbook_name(wb, "Cap_PreMoney", "08_CapTable", "$D$13")
    register_workbook_name(wb, "Cap_PostMoney", "08_CapTable", "$D$14")
    register_workbook_name(wb, "Cap_PPS_PreMoney", "08_CapTable", "$D$16")
    register_workbook_name(wb, "Cap_PPS_PostMoney", "08_CapTable", "$D$17")
    register_workbook_name(wb, "Cap_Founder_Pct", "08_CapTable", "$D$20")

    # 09_DCF
    register_workbook_range_name(wb, "DCF_FCFF", "09_DCF", f"$D$11:${last_col}$11")
    register_workbook_name(wb, "DCF_WACC", "09_DCF", "$D$23")
    register_workbook_name(wb, "DCF_g", "09_DCF", "$D$27")
    register_workbook_name(wb, "DCF_EV", "09_DCF", "$D$37")
    register_workbook_name(wb, "DCF_Equity", "09_DCF", "$D$39")
    register_workbook_name(wb, "DCF_PerShare", "09_DCF", "$D$41")

    # 11_KPI_Dashboard
    register_workbook_range_name(wb, "KPI_RuleOf40", "11_KPI_Dashboard", f"$D$6:${last_col}$6")
    register_workbook_range_name(wb, "KPI_NRR", "11_KPI_Dashboard", f"$D$12:${last_col}$12")
    register_workbook_range_name(wb, "KPI_Magic_Number", "11_KPI_Dashboard", f"$D$15:${last_col}$15")
    register_workbook_range_name(wb, "KPI_LTV_CAC", "11_KPI_Dashboard", f"$D$20:${last_col}$20")
    register_workbook_range_name(wb, "KPI_CAC_Payback", "11_KPI_Dashboard", f"$D$21:${last_col}$21")
    register_workbook_range_name(wb, "KPI_BurnMultiple", "11_KPI_Dashboard", f"$D$25:${last_col}$25")
    register_workbook_range_name(wb, "KPI_Runway", "11_KPI_Dashboard", f"$D$26:${last_col}$26")
```

### A.3 Phase 6 Wave 1 完了の verify

```bash
# 1. Build sample
python scripts/three_statement_builder.py --inp tests/sample_input.yaml --out /tmp/test.xlsx

# 2. D12 check
python scripts/sanity_checks.py --check D12 --xlsx /tmp/test.xlsx
# Expected: "D12 Named Range Coverage: PASS" or warns < 5

# 3. Excel で開く → Ctrl+F3 で Name Manager 確認
# Expected: 60+ workbook-scoped names が一覧化されている

# 4. 行挿入 self-test
# Excel で 02_Revenue B5-B6 間に行挿入 → 04_IS の Revenue 行が依然正しい値か確認
```

