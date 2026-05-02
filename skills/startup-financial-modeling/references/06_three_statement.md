---
name: three_statement
description: P&L / BS / CFS 統合モデルの正本。三表突合 / SanityChecks / 監査ログ / 循環参照対処を構築順に展開。SKILL.md dispatch table の "三表突合 / SanityChecks" entry の第 1 reference として読まれる。
type: reference
priority: P1
related: [_terminology, 01a_modeling_standards, 01b_integrity_and_anti_patterns, 16_cost_structure, 12_tax_strategy]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 三表構築の式 / SanityChecks 構造は本書を canonical とする。色・sheet name は [`_terminology.md`](_terminology.md)
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) (構築) から「三表組む」場合に第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (BS = L+E / CFS ending = BS cash / NI → RE) を必ず実行
- **関連 reference**: `01a_modeling_standards` (formatting) / `01b_integrity_and_anti_patterns` (sensitivity / 監査) / `16_cost_structure` (OpEx 入力) / `12_tax_strategy` (Tax Schedule)

# 06. 3-Statement (P&L / BS / CF) 統合モデル — 構築実務リファレンス

> **対象**: スタートアップ向け包括的財務モデリング Claude Code skill。
> **目的**: 三表が完全に突合する IB 品質の integrated model を組むための仕様書。
> **想定アウトプット**: `xlsx` の `IS` / `BS` / `CFS` / `Schedules` / `SanityChecks` シートが本書の式・チェックを 1:1 で実装している状態。
> **会計基準**: US GAAP (ASC) と IFRS、および日本基準 (JGAAP・改正 ASBJ) の論点を併記する。

---

## 0. ドキュメント全体の使い方

- 本書は **構築順** に並んでいる。1→13 の順に読むと、空のワークブックから完成モデルまでビルドできる。
- 「式」は **A1 形式の Excel 数式** で記載する。`[セル]` は変数、`{シート名}` はシート参照。
- 「突合チェック」は §12 の表に統合する。すべての式は SanityChecks シートで `=` 0 になることを期待する (許容誤差 ±$1 = `0.0001` の四捨五入丸め誤差吸収)。
- 用語は IB / Wall Street Prep / Macabacus の慣習に従い、日本語訳を初出のみ括弧書きする。
- 大文字慣例: `D&A` (減価償却 & 償却), `WC` (運転資本), `CapEx` (設備投資), `SBC` (株式報酬), `NOL` (繰越欠損金), `RE` (利益剰余金), `APIC` (資本剰余金 / 払込資本超過額)。

---

## 1. 三表の連結ロジック (核となる結合点)

統合モデルは **8 本の連結線** で全期間が突合する。ここは **唯一の正解** が存在する世界。1 本でも切れていれば BS check が破綻する。

### 1.1 連結線一覧 (Master Linkage Table)

| # | 項目 | From | To | 方向と式の本質 |
|---|---|---|---|---|
| L1 | Net Income | IS 末尾 | CFS 冒頭 (CFO の出発点) / BS の RE 増加 | `RE_t = RE_{t-1} + NI_t − Dividends_t` |
| L2 | Depreciation & Amortization | IS の OpEx 内訳 (or COGS 内訳) | CFS add-back / BS の Accumulated Depreciation 増加 | `AccumDep_t = AccumDep_{t-1} + Dep_t − Disposal_{t-1→t}` |
| L3 | Stock-Based Compensation | IS 各 OpEx | CFS add-back (non-cash) / BS の APIC 増加 | `APIC_t = APIC_{t-1} + SBC_t + EquityIssuance_t − Buyback_t` |
| L4 | CapEx | BS の Gross PP&E 増加 | CFS の CFI (出金) | `GrossPPE_t = GrossPPE_{t-1} + CapEx_t − Disposal_t` |
| L5 | Working Capital | BS の AR / Inventory / AP / Accrued / Deferred Rev 増減 | CFS の CFO 内 ΔWC | `ΔAR = AR_t − AR_{t-1}`、CFS では `−ΔAR` (増加=現金流出) |
| L6 | Debt Issuance / Repayment | BS の LT Debt + Current Portion 増減 | CFS の CFF | `Debt_t = Debt_{t-1} + Issuance_t − Repayment_t` |
| L7 | Equity Issuance / Buyback / Dividends | BS の Common Stock / APIC / Treasury / RE | CFS の CFF | Buyback は Treasury 増加 + Cash 流出 |
| L8 | Cash | CFS ending = BS Cash | 全モデル唯一の **突合点** | `Cash_BS_t = Cash_BS_{t-1} + CFO_t + CFI_t + CFF_t + FX_t` |

### 1.2 BS plug の選択 (Cash か Revolver の片方のみ)

- **Plug の意味**: BS が常に balance するように、最後に残った差分を吸収するアカウント。
- **Plug にできる候補**: (a) Cash, (b) Revolver。**両方を plug にすると過剰自由度で balance しない**。
- **業界標準**: スタートアップ初期は Cash plug (revolver なし)、調達が進み信用枠ができたら Revolver plug に切り替え。
- **実装方針**: 本リファレンスでは **Revolver plug** を主、Cash floor (例: $500K の minimum operating cash) を維持する設計を採用する。`Cash_t = max(Min_Cash, Cash_t-1 + ΔCFO + ΔCFI + ΔCFF_excl_revolver) + Revolver_draw`。

### 1.3 連結線が切れる典型 5 パターン

| 症状 | 原因 | 修正 |
|---|---|---|
| BS が毎期 同額ずれる | `RE_t = RE_{t-1} + NI` で配当を引き忘れ | `−Dividends` を追加 |
| BS が増える期だけずれる | CapEx の符号 (CFI で正しく −、BS で正しく +) | CFS 側を負号に |
| WC 増減で BS が崩れる | AR 増 = CFO 流出 (−) なのに + で計上 | 「BS の Δ をそのまま CFO 引き算」がルール |
| Cash が ending CFS と BS で 1 円ずれる | 丸め誤差 / IFERROR でゼロ化 | 表示単位を揃え、`ROUND` を統一 |
| 期末から期初がずれる | 外部から手で BS 上書き | 「初期値以外は計算式で生成」のルールを徹底 |

---

## 2. 各シートの設計

### 2.1 Income Statement (P&L) — Full Row Layout

> **設計思想**: Revenue は driver-based で組み、COGS/OpEx は %-of-revenue または unit-based で展開。EBITDA / EBIT / Pre-tax / NI の 4 つのサブトータルを**必ず明示**する。

| Row | Label (Japanese / English) | 算式 (代表例) | 備考 |
|---|---|---|---|
| 1 | **Revenue Build** | | サブセクション header |
| 2 | Subscription Revenue (SaaS) | `Customers × ARPU × 12` | §10 driver と連動 |
| 3 | Services Revenue | `Hours × Rate` | プロサービ |
| 4 | Hardware Revenue | `Units × ASP` | hardware co. |
| 5 | Other Revenue | manual / driver | |
| 6 | **Total Revenue** | `SUM(2:5)` | サブトータル |
| 7 | Revenue Growth YoY % | `Rev_t/Rev_{t-1}−1` | 表示用 |
| 8 | | | |
| 9 | **COGS Build** | | |
| 10 | Variable COGS (Hosting/Cloud) | `Rev × COGS%_var` | SaaS では AWS/GCP |
| 11 | Variable COGS (Materials) | `Units × Unit Cost` | hardware |
| 12 | Variable COGS (Payment fees) | `Rev × fee%` | payments |
| 13 | Fixed COGS (Implementation team) | manual or headcount | |
| 14 | COGS — D&A allocation | from §3 PP&E schedule | non-cash |
| 15 | **Total COGS** | `SUM(10:14)` | |
| 16 | **Gross Profit** | `[6]−[15]` | サブトータル |
| 17 | Gross Margin % | `[16]/[6]` | |
| 18 | | | |
| 19 | **OpEx Build** | | |
| 20 | S&M — Headcount | `S&M_HC × Avg_Comp` | comp incl. SBC |
| 21 | S&M — Marketing programs | `Rev × M%` or budget | |
| 22 | S&M — Other | budget | |
| 23 | R&D — Headcount | `R&D_HC × Avg_Comp` | |
| 24 | R&D — Tools / cloud | budget | |
| 25 | R&D — Other | budget | |
| 26 | G&A — Headcount | `G&A_HC × Avg_Comp` | |
| 27 | G&A — Professional fees (legal/audit) | budget | |
| 28 | G&A — Office / IT | budget | |
| 29 | G&A — Insurance / D&O | budget | |
| 30 | OpEx — D&A allocation | from §3 PP&E schedule | non-cash |
| 31 | OpEx — SBC allocation | from §6 SBC schedule | non-cash |
| 32 | **Total OpEx** | `SUM(20:31)` | |
| 33 | | | |
| 34 | **EBITDA (excl. SBC)** | `[16]−SUM([20:29])` | non-GAAP, 投資家 KPI |
| 35 | **EBITDA (GAAP, incl. SBC)** | `[34]−[31]` | GAAP 整合性 |
| 36 | **EBIT (Operating Income)** | `[35]−[14]−[30]` | D&A を差し引く |
| 37 | EBIT Margin % | `[36]/[6]` | |
| 38 | | | |
| 39 | Interest Income | `Avg_Cash × YieldOnCash` | excess cash の運用 |
| 40 | Interest Expense — Term Loan | from §4 Debt schedule | |
| 41 | Interest Expense — Revolver | from §4 Debt schedule | iterative |
| 42 | Interest Expense — Lease | from §7 Lease schedule | finance lease |
| 43 | FX Gain/(Loss) | manual or ratio | non-functional ccy |
| 44 | Other Income/(Expense) | manual | |
| 45 | **Pre-tax Income (PBT)** | `[36]+[39]−[40]−[41]−[42]+[43]+[44]` | |
| 46 | Tax Provision (current + deferred) | from §5 Tax schedule | |
| 47 | **Net Income (NI)** | `[45]−[46]` | **L1 → CFS / RE** |
| 48 | NI Margin % | `[47]/[6]` | |
| 49 | | | |
| 50 | **Per-share data** | | |
| 51 | Weighted Avg. Basic Shares | from §6 cap table | |
| 52 | Weighted Avg. Diluted Shares | basic + TSM dilution | TSM = §6 |
| 53 | Basic EPS | `[47]/[51]` | |
| 54 | Diluted EPS | `[47]/[52]` | |

### 2.2 Balance Sheet (BS) — Full Row Layout

> **設計思想**: 各行は **roll-forward 式** で書く (`期末 = 期初 + 増 − 減`)。直接入力するのは初期 BS のみ。

| Row | Label | 算式 | 連結先 |
|---|---|---|---|
| **Current Assets** | | | |
| 1 | Cash & Cash Equivalents | `=BS_{t-1}![Cash]+CFS!{Net Change in Cash}` | L8 |
| 2 | Short-term Investments (Marketable securities) | manual / FV roll | |
| 3 | Accounts Receivable (AR) | `=Revenue × DSO/365` | §3 WC |
| 4 | Inventory | `=COGS × DIO/365` | §3 WC |
| 5 | Prepaid Expenses | `=OpEx × Prepaid_days/365` | §3 WC |
| 6 | Contract Assets (ASC 606 unbilled) | from rev rec | §8 |
| 7 | Other Current Assets | manual | |
| 8 | **Total Current Assets** | `SUM(1:7)` | |
| **Non-current Assets** | | | |
| 9 | Gross PP&E | `=GrossPPE_{t-1}+CapEx_t−Disposals_t` | L4 |
| 10 | Accumulated Depreciation | `=AD_{t-1}−Dep_t+DisposalAccumDep_t` | L2, 表示は負値 |
| 11 | Net PP&E | `[9]+[10]` | |
| 12 | Right-of-Use Asset (ROU) — Operating | `=ROU_{t-1}+New_lease−Amort_t` | §7 |
| 13 | Right-of-Use Asset (ROU) — Finance | `=ROU_{t-1}+New_lease−Amort_t` | §7 |
| 14 | Intangibles, net | `=Intangibles_{t-1}+New−Amort` | |
| 15 | Goodwill | `=Goodwill_{t-1}+M&A_t−Impairment_t` | M&A only |
| 16 | Deferred Tax Asset (DTA), net | from §5 | §5 |
| 17 | Other Long-term Assets | manual | |
| 18 | **Total Non-current Assets** | `SUM(11:17)` | |
| 19 | **TOTAL ASSETS** | `[8]+[18]` | |
| **Current Liabilities** | | | |
| 20 | Accounts Payable (AP) | `=COGS × DPO/365` | §3 WC |
| 21 | Accrued Expenses | `=OpEx × Accr_days/365` | §3 WC |
| 22 | Deferred Revenue — Current | from §8 rev rec | §8 |
| 23 | Current Portion of LT Debt | from §4 amort schedule | §4 |
| 24 | Current Portion of Lease Liability | from §7 | §7 |
| 25 | Income Tax Payable | from §5 | |
| 26 | Other Current Liabilities | manual | |
| 27 | **Total Current Liabilities** | `SUM(20:26)` | |
| **Non-current Liabilities** | | | |
| 28 | Long-term Debt (excl. current) | `=LTD_{t-1}+Issuance−Repayment−reclass` | L6 |
| 29 | Revolver / Line of Credit | **plug** = §4 | iterative |
| 30 | Deferred Revenue — Long-term | from §8 | §8 |
| 31 | Lease Liability — Operating (LT) | from §7 | §7 |
| 32 | Lease Liability — Finance (LT) | from §7 | §7 |
| 33 | Deferred Tax Liability (DTL) | from §5 | §5 |
| 34 | Other Long-term Liabilities | manual | |
| 35 | **Total Non-current Liabilities** | `SUM(28:34)` | |
| 36 | **TOTAL LIABILITIES** | `[27]+[35]` | |
| **Equity** | | | |
| 37 | Preferred Stock (Series A/B/C, etc.) | `=Pref_{t-1}+New_round` | |
| 38 | Common Stock (par) | `=CS_{t-1}+New_par` | |
| 39 | Additional Paid-in Capital (APIC) | `=APIC_{t-1}+(Issuance−par)+SBC_t−Buyback_premium` | L3, L7 |
| 40 | Retained Earnings (RE) | `=RE_{t-1}+NI_t−Dividends_t` | L1 |
| 41 | Treasury Stock | `=Treasury_{t-1}−Buyback_t+Reissuance_t` | L7, 表示は負値 |
| 42 | Accumulated OCI (AOCI) | `=AOCI_{t-1}+OCI_t` | FX, 投資 unrealized |
| 43 | **Total Parent Equity** | `SUM(37:42)` | |
| 44 | Non-controlling Interest (NCI) | `=NCI_{t-1}+NCI%×Sub_NI` | §9 連結 |
| 45 | **TOTAL EQUITY** | `[43]+[44]` | |
| 46 | **TOTAL LIABILITIES + EQUITY** | `[36]+[45]` | |
| 47 | **BS CHECK** | `[19]−[46]` | **must = 0** |

### 2.3 Cash Flow Statement (CFS) — Indirect Method, Full Row Layout

> **設計思想**: Indirect method を主、direct method は補助 schedule で算出。
> **指針**: CFS の各行は「**BS の Δ から**」もしくは「**IS の non-cash add-back から**」しか来ない。**手入力ゼロ**を目指す。

| Row | Label | 算式 / 由来 | 符号 |
|---|---|---|---|
| **CFO (Operating)** | | | |
| 1 | Net Income | `IS![NI]` | + |
| 2 | (+) Depreciation & Amortization | `IS![COGS_DA]+IS![OpEx_DA]+§7 Lease ROU amort` | + |
| 3 | (+) Stock-Based Compensation | `IS![OpEx_SBC]+IS![COGS_SBC]` | + |
| 4 | (+) Deferred Tax Expense / (Benefit) | `Δ(DTL−DTA)` from §5 | ± |
| 5 | (+) Loss / (−) Gain on Disposal | from §3 PP&E | ± |
| 6 | (+) Non-cash Interest (PIK) | from §4 Debt schedule | + |
| 7 | (−) Increase in AR / (+) Decrease | `−(AR_t−AR_{t-1})` | sign-flip |
| 8 | (−) Increase in Inventory / (+) | `−(Inv_t−Inv_{t-1})` | sign-flip |
| 9 | (−) Increase in Prepaid / (+) | `−(Prep_t−Prep_{t-1})` | sign-flip |
| 10 | (+) Increase in AP / (−) | `+(AP_t−AP_{t-1})` | direct |
| 11 | (+) Increase in Accrued / (−) | `+(Accr_t−Accr_{t-1})` | direct |
| 12 | (+) Increase in Deferred Revenue / (−) | `+(DR_t−DR_{t-1})` | direct |
| 13 | (+) Other WC | balancing | |
| 14 | **Cash Flow from Operating (CFO)** | `SUM(1:13)` | |
| **CFI (Investing)** | | | |
| 15 | (−) CapEx | `−CapEx_t` from §3 | − |
| 16 | (+) Proceeds from Disposal | `+Sale_t` | + |
| 17 | (−) Acquisitions (M&A net of cash acquired) | `−M&A_cash_t` | − |
| 18 | (+) Divestitures | `+Divest_t` | + |
| 19 | (−) Purchase of Investments / (+) Sales | `±Investments` | ± |
| 20 | **Cash Flow from Investing (CFI)** | `SUM(15:19)` | |
| **CFF (Financing)** | | | |
| 21 | (+) Issuance of LT Debt | `+Issuance_t` | + |
| 22 | (−) Repayment of LT Debt | `−Repay_t (mandatory + voluntary)` | − |
| 23 | (+) Drawdown of Revolver | `+max(0, ΔRevolver)` | + |
| 24 | (−) Repayment of Revolver | `−max(0, −ΔRevolver)` | − |
| 25 | (−) Lease Liability Principal Payment | `−Principal_t` from §7 | − |
| 26 | (+) Issuance of Equity | `+Equity_round_t` | + |
| 27 | (−) Buyback of Common | `−Buyback_t` | − |
| 28 | (−) Dividends Paid | `−Div_t` | − |
| 29 | (−) Other Financing | manual | |
| 30 | **Cash Flow from Financing (CFF)** | `SUM(21:29)` | |
| 31 | (+) FX impact on Cash | `OCI_FX_t` | ± |
| 32 | **Net Change in Cash** | `[14]+[20]+[30]+[31]` | |
| 33 | Cash — Beginning of Period | `BS_{t-1}![Cash]` | |
| 34 | Cash — End of Period | `[32]+[33]` | |
| 35 | **CASH CHECK** | `[34]−BS_t![Cash]` | **must = 0** |

### 2.4 Direct method との違い

| 項目 | Indirect | Direct |
|---|---|---|
| 出発点 | Net Income | Cash receipts from customers |
| 主な行 | NI + non-cash + ΔWC | Cash from customers, cash to suppliers, cash to employees |
| 普及度 | 上場企業の 99% | 数% |
| Pros | IS と直接連結、推定が容易 | 経済実態を直感的に表示 |
| Cons | ΔWC の理解が必要 | データ収集コスト高 |
| 適用場面 | スタートアップ全般、IB 標準 | 内部管理 / cash forecasting / 銀行融資審査 |
| **本リファレンス推奨** | **Indirect** (IS から自動連結) | 補助 schedule のみ |

---

## 3. Working Capital Schedule

### 3.1 Driver 定義

| 指標 | 略 | 公式 (基本) | 推奨計算 (期末 stock) |
|---|---|---|---|
| Days Sales Outstanding | DSO | `Avg AR / Revenue × 365` | `AR_t = Revenue_t × DSO_t / 365` |
| Days Inventory Outstanding | DIO | `Avg Inv / COGS × 365` | `Inv_t = COGS_t × DIO_t / 365` |
| Days Payable Outstanding | DPO | `Avg AP / COGS × 365` | `AP_t = COGS_t × DPO_t / 365` |
| Days Prepaid | — | `Prepaid / OpEx × 365` | `Prepaid_t = OpEx_t × Days/365` |
| Days Accrued | — | `Accrued / OpEx × 365` | `Accrued_t = OpEx_t × Days/365` |
| Deferred Revenue % | — | `DR / Annual Rev` | `DR_t = ARR_t × % billed in advance × remaining months/12` |

> **注 (Wall Street Prep / CFI)**: 期間粒度が monthly / quarterly のときは `× 365` を `× DaysInPeriod` に置換する。または **DaysInPeriod を直接モデル化**する (より一般的)。

### 3.2 Cash Conversion Cycle (CCC)

```
CCC = DSO + DIO − DPO
```

- **意味**: 1 円の現金が「在庫購入 → 売上 → 入金」と回って戻るまでの日数。
- **業界ベンチマーク**:
  - SaaS / 純デジタル: −60 〜 −180 日 (前払いで負の WC = キャッシュ生成)
  - 製造業: 30〜90 日
  - 小売 (回転速い): 5〜30 日

### 3.3 SaaS-specific WC

| 項目 | 性質 | モデリング |
|---|---|---|
| Deferred Revenue (年間前払い) | 負債 (現金は受領済) | `New ARR × % annual prepay × remaining months/12` |
| Contract Asset (ASC 606 unbilled) | 資産 | usage-based billing で発生 |
| AR (月次後払い) | 資産 | DSO で driver 化 |
| Sales Commission (deferred) | 資産 (capitalized per ASC 606) | amortize over contract life |

### 3.4 Working Capital schedule 例 (Excel layout)

```
        2024A   2025E   2026E   2027E
Revenue      10,000  15,000  22,500  31,500
COGS          3,000   4,500   6,750   9,450
OpEx          5,000   7,000   9,500  12,500
DSO (days)       45      45      45      45
DIO (days)        0       0       0       0
DPO (days)       30      30      30      30
Prepaid days      7       7       7       7
Accrued days     14      14      14      14

AR        =Revenue×DSO/365    1,233   1,849   2,774   3,884
Inventory                          0       0       0       0
Prepaid   =OpEx×Days/365          96     134     182     240
AP        =COGS×DPO/365          247     370     555     777
Accrued   =OpEx×Days/365         192     268     364     480

NWC = AR+Inv+Prep − AP−Accr      890   1,346   2,037   2,866
ΔNWC                                +456   +691   +830
ΔNWC → CFS (sign-flip → −CFO)      −456   −691   −830
```

### 3.5 突合チェック

| Check | 式 |
|---|---|
| AR roll-forward | `BS![AR_t]−BS![AR_{t-1}] = −CFS![ΔAR add-back]` |
| AP roll-forward | `BS![AP_t]−BS![AP_{t-1}] = +CFS![ΔAP add-back]` |
| Each WC item: BS Δ = CFS line |  |

---

## 4. Debt Schedule (Revolver Logic)

### 4.1 構造

スタートアップの典型的負債は (a) **Term Loan** (Venture Debt が代表), (b) **Revolver** (信用枠), (c) **Convertible Note / SAFE** (resolution 後は equity 扱い)。

### 4.2 Term Loan モデリング

| Row | Label | 式 |
|---|---|---|
| Beginning Balance | `Debt_{t-1}` | |
| (+) New Issuance | input | |
| (−) Mandatory Amortization | `−min(BeginBal, Mand_principal_t)` | |
| (−) Voluntary Repayment / Cash Sweep | `−min(remaining_FCF × sweep%, BeginBal)` | |
| Ending Balance | sum | |
| Avg Balance | `(Begin + End) / 2` | |
| Interest Expense | `Avg × Rate` | iterative ⚠ |

> **注 (BIWS / Macabacus)**: Avg balance は **iterative calculation** を起こす (Interest → NI → CFO → Cash → Debt repayment → Debt balance → Avg → Interest)。Excel で `Options → Formulas → Enable iterative calculation, max 100, change 0.001` を ON にする。代替として **Beginning balance のみで計算** (より conservative、circular ref なし)。

### 4.3 Revolver (信用枠) — Plug ロジック

```
Revolver_t = max(
  0,
  Revolver_{t-1}
  − (Cash_pre_revolver_t − Min_Cash)    -- excess cash で revolver 返済
  + (Min_Cash − Cash_pre_revolver_t)    -- shortfall を revolver で fill
)
```

シンプルな書き方:

```
Cash_pre_revolver = Cash_{t-1} + CFO + CFI + CFF_excl_revolver
If Cash_pre_revolver < Min_Cash:
    Draw = Min_Cash − Cash_pre_revolver
    Revolver_t = Revolver_{t-1} + Draw
    Cash_t = Min_Cash
Else:
    Pay = min(Revolver_{t-1}, Cash_pre_revolver − Min_Cash)
    Revolver_t = Revolver_{t-1} − Pay
    Cash_t = Cash_pre_revolver − Pay
```

Excel 1-line:

```
Revolver_t = MAX(0, Revolver_{t-1} + Min_Cash − (Cash_{t-1} + CFO + CFI + CFF_excl_revolver))
Cash_t = Cash_{t-1} + CFO + CFI + CFF_excl_revolver + (Revolver_t − Revolver_{t-1})
```

### 4.4 Interest expense (詳細式)

```
Interest_TermLoan_t = ((TermLoan_{t-1} + TermLoan_t)/2) × Rate_TermLoan
Interest_Revolver_t = ((Revolver_{t-1} + Revolver_t)/2) × Rate_Revolver + Unused_t × Commitment_fee
Interest_Lease_t    = OpenLeaseLiab_t × Rate_lease  (effective interest method)
Interest_Income_t   = ((Cash_{t-1} + Cash_t)/2) × Yield_on_Cash
Net_Interest        = Income − Expense
```

### 4.5 Begin/End reconciliation (debt walk)

各 debt instrument について:

```
Begin BoP   +Issuance   −Repayment   −Reclass to current   = End EoP
                                                              ↓
                                                          BS LT Debt
End EoP × Mandatory_in_next_year   = Current Portion (BS line)
```

### 4.6 突合チェック

| Check | 式 |
|---|---|
| Debt roll | `Begin + Issue − Repay = End` |
| BS LT Debt | `LTD_t = End − Current Portion_t` |
| CFS Debt lines tie | `CFF Issuance − CFF Repay = ΔTotal Debt` |
| Interest expense | `IS Interest = SUM of all debt instrument interests` |

---

## 5. Tax Schedule

### 5.1 Effective Tax Rate (ETR) vs Statutory

| 概念 | 定義 |
|---|---|
| Statutory Rate | 法定税率。US 連邦 21% + 州 (合算 25-28%)、日本 23.2% (法人税) + 地方 (実効 30-35%) |
| Effective Tax Rate | `Tax provision / PBT`。永久差異・税額控除でブレる |
| Marginal Rate | 追加 1 円の所得に対する税率。Statutory に近い |

> **モデリング指針**: forecast では **実効税率 (ETR)** を assumption に置き、`Tax = PBT × ETR`。詳細モデルでは current vs deferred を分割。

### 5.2 Book-tax differences

| 種類 | 例 | 影響 |
|---|---|---|
| **Permanent** (永久差異) | 交際費損金不算入、罰金、税額控除 | ETR に永続的影響 |
| **Temporary** (一時差異) | D&A 償却年数差、SBC 認識タイミング、引当金 | DTA/DTL を生成、将来 reverse |

### 5.3 Deferred Tax Asset / Liability

```
DTA = (Future deductible amount) × Tax Rate
DTL = (Future taxable amount)    × Tax Rate
Book Tax Expense = Current Tax + Deferred Tax
                 = Current Tax + Δ(DTL − DTA)
```

| 一時差異 | 簿記 vs 税務 | DTA or DTL |
|---|---|---|
| Accelerated tax depreciation > book | 税務側で先に loss | DTL |
| SBC: expensed for book, deductible at exercise | 税務側で後で loss | DTA |
| Loss carryforward (NOL) | 税務側で将来控除 | DTA |
| Bad debt allowance (book only) | 税務側で後で loss | DTA |
| R&D capitalization (US 174) | 税務側で 5 年償却 | DTA (一時的) |

### 5.4 NOL Carryforward — 米国

- **TCJA (2017 以降の損失)**:
  - 繰越期間: **無期限**
  - 控除限度: 課税所得の **80%**
  - 繰戻し: **不可** (CARES Act の 5 年遡及は 2018-2020 損失のみ、終了)
- **モデル式**:

```
NOL_balance_t = NOL_balance_{t-1} − NOL_used_t + NOL_generated_t
NOL_used_t    = MIN(NOL_balance_{t-1}, 80% × Taxable_Income_pre_NOL_t)
Taxable_Income_t = Taxable_Income_pre_NOL_t − NOL_used_t
DTA_NOL_t     = NOL_balance_t × Tax_Rate
```

### 5.5 NOL 繰越控除 — 日本 (青色申告)

- **繰越期間**: **10 年** (2018/4/1 以降開始事業年度)
- **控除限度**:
  - **大法人** (資本金 5 億円以上): 課税所得の **50%**
  - **中小法人** (資本金 1 億円以下): 課税所得の **100%** (限度なし)
  - スタートアップで資本金 1 億超 5 億未満は 50% 適用となる事業年度あり (個別確認)
- **繰戻し還付**: 中小法人は 1 年繰戻し可能 (継続適用要件あり)

```
日本モデル式 (大法人):
損金算入額_t = MIN(繰越欠損金_{t-1}, 50% × 所得_控除前_t)
日本モデル式 (中小法人):
損金算入額_t = MIN(繰越欠損金_{t-1}, 所得_控除前_t)
```

### 5.6 Valuation Allowance (評価性引当)

- **ASC 740 (US GAAP) / IAS 12 (IFRS)**: DTA は「**more likely than not** (>50%)」回収できる金額のみ計上。残りは **valuation allowance** で相殺。
- **スタートアップ典型**: 累損段階では DTA 全額を VA で相殺 → 損益計算書には現れない。利益化が見えてきた段階で VA を取り崩し、巨額の **deferred tax benefit** を計上 → ETR が 1 期だけ大きくマイナスに。

### 5.7 R&D Tax Credit

| 国 | 制度 | 概要 |
|---|---|---|
| US | R&D Credit (Sec. 41) | qualified research expense の 6-14% |
| 日本 | 試験研究費税額控除 | 総額型 (試験研究費の 1-14%, 法人税額の 25%が上限) + オープンイノベーション型 (20-30%) |
| 日本 (中小) | 中小企業技術基盤強化税制 | 12-17% |

### 5.8 突合チェック

| Check | 式 |
|---|---|
| Tax Provision | `IS![Tax] = Current_Tax + Deferred_Tax` |
| DTA roll | `DTA_t = DTA_{t-1} + ΔDTA_originating − DTA_used + ΔVA` |
| NOL | `NOL_t = NOL_{t-1} − Used_t + Generated_t` (≥ 0) |
| BS DTA/DTL = §5 schedule end balance |  |

---

## 6. Stock-Based Compensation (SBC)

### 6.1 三表での扱い

| 表 | 動き |
|---|---|
| IS | 各 OpEx (S&M, R&D, G&A) と COGS にコンプポートフォリオ % で配分。**cash expense として計上** (P&L hit はある) |
| CFS | CFO 内で **add-back** (non-cash) |
| BS | APIC 増加 (equity 側)。Cash には影響なし。Vesting 時点で APIC に振替 |

### 6.2 仕訳イメージ

```
Dr.  R&D Expense (or COGS, S&M, G&A)   100
    Cr. APIC                                100
```

### 6.3 SaaS スタートアップでの実態

- **Morgan Stanley Counterpoint Global (Mauboussin)** 調査: 公開 SaaS 平均 SBC は revenue の **15-25%**、EBITDA の **20-40%** を占める。
- **問題**: 「Adjusted EBITDA ex-SBC」を主要 KPI とすると **真の経済性を過大評価**する。SBC は将来希薄化を通じて株主価値を毀損する。
- **投資家ベンチマーク**:
  - 健全: 年間 SBC 起因希薄化 < 2-3%
  - 高成長 (>30%) でも 4% 超は警戒、5% 超は危険信号
  - 1pp の超過で EV が 7-10% 毀損 (高成長), 5-7% (中成長) — Mauboussin

### 6.4 Diluted Share Count — Treasury Stock Method (TSM)

公開時の希薄化を計算するときは TSM を使う:

```
1. 行使価格 < 株価 (in-the-money) のオプション・RSU・ワラントを抽出
2. 仮想行使: 
     Gross Shares Issued = ITM_options
     Cash Received       = ITM_options × Avg_Strike
3. 仮想自社株買い: 
     Shares Bought Back = Cash Received / Stock Price
4. Net dilution = Gross Issued − Bought Back
5. Diluted Shares = Basic Shares + Net dilution
```

> RSU は strike price = 0 のオプションとみなし、cash received = 0 → 全数希薄化。

### 6.5 SBC schedule 例 (Excel)

```
                              Y1    Y2    Y3    Y4
Grant value (FV at grant)   2,000 3,000 4,000 5,000
Vesting schedule (4yr cliff/ratable)
  Y1 grant, Y1 vest         500
  Y1 grant, Y2 vest                500
  ...
SBC Expense (sum of vested)   500  1,250 2,250 3,500
   COGS allocation %           5%
   S&M allocation %           25%
   R&D allocation %           50%
   G&A allocation %           20%

APIC increase (= SBC Expense) → BS L3
CFS add-back (= SBC Expense)  → CFO L3
```

### 6.6 突合チェック

| Check | 式 |
|---|---|
| SBC IS = CFS add-back | `IS_SBC = CFS_SBC_add_back` |
| APIC roll | `APIC_t = APIC_{t-1} + SBC_t + Issuance_premium − Buyback_premium` |
| Diluted shares ≥ Basic |  |

---

## 7. Lease Accounting (ASC 842 / IFRS 16 / 日本基準改正)

### 7.1 基準別 概要

| 項目 | ASC 842 (US GAAP) | IFRS 16 | 日本 (改正 2027/4/1〜) |
|---|---|---|---|
| **モデル** | Dual model (Operating + Finance) | Single model (全て finance 風) | Single model (使用権モデル) |
| **BS 計上** | 両方とも ROU + Lease Liab | 全リース ROU + Liab | 全リース 使用権資産 + リース負債 |
| **IS** | Op: 単一 lease expense (定額); Fin: D&A + Interest | 全て D&A + Interest | 減価償却費 + 支払利息 |
| **CFS** | Op: 全 CFO; Fin: principal CFF, interest CFO | Principal CFF, Interest CFO/CFI/CFF (選択) | 概ね Principal CFF, Interest CFO |
| **適用開始** | 2019 (公開), 2022 (非公開) | 2019/1/1 | 2027/4/1 (早期 2025/4/1) |

### 7.2 共通の初期計上

```
Lease Liability_0 = PV(Lease Payments, IBR or implicit rate)
ROU Asset_0       = Lease Liability_0 + Prepayments + Initial direct costs − Lease incentives
```

`IBR` = incremental borrowing rate (借手の追加借入金利)

### 7.3 Operating Lease (ASC 842) の各期処理

```
Lease Expense (IS, 単一) = (Total payments − Total incentives) / Lease term  -- 定額化
Interest_t = OpenLiab_t × Rate
Principal_t = Payment_t − Interest_t
Liab_End = Liab_Begin − Principal_t
ROU_End  = ROU_Begin − (Lease Expense_t − Interest_t)  -- "balancing"
```

CFS:
- Lease Expense は CFO の中で `+D&A relief = ROU amort` と `−Cash payment` の差で吸収。
- 結果として Operating CF は cash payment 相当額が CFO outflow になる。

### 7.4 Finance Lease (ASC 842) / IFRS 16 全リース

```
ROU Amortization (IS) = ROU_0 / Lease term  -- 定額
Interest_t            = OpenLiab_t × Rate    -- 漸減
Principal_t           = Payment_t − Interest_t
Liab_End              = Liab_Begin − Principal_t
ROU_End               = ROU_Begin − Amortization
```

CFS:
- Interest → CFO
- Principal → CFF
- → **CFO が Operating Lease より良く見える** (IFRS 16 で広く議論された)

### 7.5 突合チェック

| Check | 式 |
|---|---|
| ROU roll | `ROU_t = ROU_{t-1} − Amort_t (+ New leases)` |
| Liab roll | `Liab_t = Liab_{t-1} − Principal_t (+ New leases)` |
| Interest = OpenLiab × Rate |  |
| Cash payment = Principal + Interest |  |
| BS Current Portion = next 12mo principal |  |

---

## 8. Revenue Recognition (ASC 606 / IFRS 15 / 日本基準)

### 8.1 5-step model (3 基準で共通フレーム)

| Step | 内容 (英) | 日本語 |
|---|---|---|
| 1 | Identify the contract with the customer | 顧客との契約の識別 |
| 2 | Identify the performance obligations | 履行義務の識別 |
| 3 | Determine the transaction price | 取引価格の算定 |
| 4 | Allocate the transaction price | 取引価格の履行義務への配分 |
| 5 | Recognize revenue when (or as) PO is satisfied | 履行義務の充足に応じた収益認識 |

### 8.2 業態別パターン

| 業態 | 認識タイミング | 例 |
|---|---|---|
| **SaaS subscription** | Over time (ratable, 月割) | $12,000 年契約 → 月 $1,000 認識 |
| **Implementation / setup** | One-time (delivery) or over contract life (もし distinct でない) | 切り分け判定が論点 |
| **Hardware** | Point-in-time (引渡し / 検収) | IoT デバイス |
| **Usage-based (API call等)** | Over time (使用量比例) | OpenAI API |
| **Multi-year prepay with discount** | Over the period | 3 年契約一括前払い |
| **Variable consideration (rebate)** | Constrained estimate | 達成型 rebate |

### 8.3 BS への影響

| 取引 | BS 計上 |
|---|---|
| 顧客が前払 (現金受領、サービス未提供) | Cash↑ + Deferred Revenue↑ (契約負債) |
| サービス提供 (Defer Rev → Rev に振替) | Deferred Revenue↓ + Revenue↑ |
| サービス先行 (請求未) | Contract Asset (Unbilled AR)↑ + Revenue↑ |
| 請求 (Billing) | AR↑ + Contract Asset↓ |

### 8.4 SaaS Deferred Revenue モデル例

```
ARR_t (Annual Recurring Revenue) = ARR_{t-1} + New ARR − Churn
Billing pattern: Annual upfront 60%, Monthly 40%
Avg deferred months on annual contracts = 6 (年中で平均 6 か月分残)

Deferred Revenue_t = ARR_t × 60% × (6/12) = ARR_t × 30%
```

### 8.5 日本基準 (収益認識に関する会計基準, 企業会計基準第 29 号)

- 適用: 2021/4/1 以降開始事業年度の上場企業必須。
- 「契約負債」「契約資産」「顧客との契約から生じた債権」など新勘定科目。
- 5-step は ASC 606 / IFRS 15 と整合。代替的取扱い (alternative treatment) で本邦商慣行を一部容認。

### 8.6 突合チェック

| Check | 式 |
|---|---|
| Deferred Rev roll | `DR_t = DR_{t-1} + Billings − Revenue` |
| AR roll | `AR_t = AR_{t-1} + Billings − Cash collections` |
| Cash = Billings 関数 |  |

---

## 9. 連結 (Consolidation)

### 9.1 持分比率と会計処理

| 持分 | 影響度 | 会計処理 | BS 計上 |
|---|---|---|---|
| **>50%** | 支配 (control) | **完全連結 (Full consolidation)** | 子会社の AS/L 100% を BS に。NCI 行に親非帰属分 |
| **20-50%** | 重要な影響力 (significant influence) | **持分法 (Equity method)** | "Investment in associate" 1 行で計上、Δは IS の "Equity in earnings" |
| **<20%** | 通常の投資 | **公正価値 (Fair value)** or **Cost** | 投資簿価、評価損益は OCI/IS |

### 9.2 完全連結のメカニクス

1. **資産・負債の合算**: 親 100% + 子 100%
2. **資本連結**: 子の資本を親の投資勘定と相殺
3. **のれん (Goodwill)** = 取得対価 − 取得純資産公正価値
4. **NCI (非支配持分)** = 子 純資産 × (1 − 親持分%)
5. **内部取引消去** (Intercompany sales/AR/AP)
6. **未実現利益消去** (Inventory, PP&E 親子間売買)

### 9.3 持分法

```
Investment_t = Investment_{t-1} 
             + Investor_share × Sub_NI 
             − Dividends_received
             − Impairment
```

IS 側: `Equity in earnings = Investor_share × Sub_NI` (1 行)。

### 9.4 為替換算

- **Functional currency** ≠ Reporting currency:
  - 資産・負債: 期末レート
  - 損益: 平均レート
  - 資本 (歴史的): 取引レート
  - 差額 → **CTA (Cumulative Translation Adjustment) in OCI/AOCI**

### 9.5 突合チェック

| Check | 式 |
|---|---|
| NCI 表示 | NCI は Equity 内の 別行 |
| Equity in earnings ↔ Investment 増 |  |
| Intercompany 消去 | 内部 AR + 内部 AP = 0 |

---

## 10. Forecast 構築アプローチ

### 10.1 3 アプローチ

| アプローチ | 手順 | 強み | 弱み |
|---|---|---|---|
| **Top-down** | TAM × 取込率 | 市場感応度を取込め、ストーリー説得力 | "5% を取れば $1B" 的な空想化リスク |
| **Bottom-up** | 各ドライバー (顧客数 × ARPU, leads × CVR) | 経済実態に直結、感度分析可 | 過度に細かいと予測精度↓ |
| **Hybrid** | Bottom-up を構築 → Top-down で sanity check | 実務標準、両者の弱みを相殺 | 構築工数大 |

> **本リファレンス推奨**: **Bottom-up を主**、最終年だけ TAM/SAM 比率で sanity check。

### 10.2 Bottom-up SaaS Revenue driver 例

```
Pipeline:
  Leads_t = Leads_{t-1} × (1 + Lead growth%)
  MQLs    = Leads × MQL conversion%
  SQLs    = MQLs × SQL conversion%
  Won     = SQLs × Win rate%
  New customers = Won
  Churned customers = Customers_{t-1} × Logo churn%
  
Customers_t = Customers_{t-1} + New − Churn
ARPU_t       = ARPU_{t-1} × (1 + Expansion%)
ARR_t        = Customers_t × ARPU_t
Revenue_t    = AVG(ARR_{t-1}, ARR_t)  -- 月次平均で粗計算
```

### 10.3 Seasonality

- 月次モデルでは monthly seasonality factor (sums to 12) を適用:
  - B2B SaaS: Q4 重い (予算消化), Q1 軽い
  - 小売: Q4 (holiday) が 35-45%
  - Travel: 夏休み + 年末年始

### 10.4 Soft launch / S-curve

```
Adoption_t = Plateau / (1 + EXP(−k × (t − t_midpoint)))
  Plateau = 想定ピーク値
  k       = ramp 急峻さ
  t_mid   = 半分到達時点
```

線形 ramp: `min(Plateau, t × Plateau / Ramp_months)`。

---

## 11. シナリオ管理

### 11.1 Switch (toggle) cell パターン

- セル `Inputs!B2 = 1` (1=Base / 2=Upside / 3=Downside)
- 名前付きセル: `S_Switch`
- `Data Validation > List > 1,2,3` (or 名前 list)

### 11.2 関数別の特徴

| 関数 | 例 | 備考 |
|---|---|---|
| **CHOOSE** | `=CHOOSE(S_Switch, Base!B5, Up!B5, Down!B5)` | 透明、IB 標準。引数最大 254 個 |
| **INDEX** | `=INDEX(Scenarios!B5:D5, S_Switch)` | 行 1 本に scenarios 横並びがハマる |
| **OFFSET** | `=OFFSET(Base!B5, 0, S_Switch−1)` | volatile (再計算負荷大), 非推奨 |
| **SWITCH (Excel 365)** | `=SWITCH(S_Switch,1,Base!B5,2,Up!B5,3,Down!B5)` | 一番読みやすい |

### 11.3 推奨レイアウト (Inputs シート)

```
Driver               Base    Upside   Downside   Active (=CHOOSE)
Revenue growth %     20%     35%      5%         =CHOOSE(S_Switch, ...)
Gross margin %       70%     75%      60%        =CHOOSE(...)
S&M as % of Rev      40%     35%      50%        ...
```

すべての IS / BS / CFS は **Active 列のみ参照**。

### 11.4 Excel Scenario Manager (補助)

- `Data → What-If Analysis → Scenario Manager`
- ベースには使わず、**社内議論用の "What-if 比較レポート"** 生成用。レポート tab に summary を吐き出して PDF 化に向く。

---

## 12. 監査ログ / Sanity Checks (SanityChecks シート設計)

### 12.1 Hard checks (== 0 でないと error)

| # | Check | 式 | 意味 |
|---|---|---|---|
| H1 | **BS Balance** | `Total Assets − Total L&E` | 全期 = 0 |
| H2 | **Cash tie** | `CFS Ending Cash − BS Cash_t` | CFS と BS の現金一致 |
| H3 | **RE roll** | `(BS RE_t − BS RE_{t-1}) − (IS NI_t − Dividends_t)` | RE 連結 |
| H4 | **PP&E roll** | `(BS GrossPPE_t − BS GrossPPE_{t-1}) − (CapEx_t − Disposal_t)` | PP&E 連結 |
| H5 | **Accum Dep roll** | `(BS AD_{t-1} − BS AD_t) − (Dep_t − DisposalAD_t)` | 累計減価償却 |
| H6 | **Debt roll** | `(BS Debt_t − BS Debt_{t-1}) − (CFF Issue_t − CFF Repay_t)` | Debt 連結 |
| H7 | **APIC roll** | `(BS APIC_t − BS APIC_{t-1}) − (SBC_t + EquityIss_t − BuybackPremium_t)` | APIC 連結 |
| H8 | **Lease ROU roll** | `(BS ROU_t − BS ROU_{t-1}) − (NewLease_t − Amort_t)` | リース |
| H9 | **Lease Liab roll** | `(BS Liab_t − BS Liab_{t-1}) − (NewLease_t − Principal_t)` | リース |
| H10 | **Deferred Rev roll** | `(BS DR_t − BS DR_{t-1}) − (Billings_t − Revenue_t)` | RevRec |
| H11 | **NOL roll** | `NOL_t − NOL_{t-1} − Generated_t + Used_t` | NOL ≥ 0 |
| H12 | **DTA roll** | `DTA_t − DTA_{t-1} − ΔDTA_originating + DTA_used + ΔVA` | 税効果 |
| H13 | **CFS internal sum** | `CFO + CFI + CFF + FX − Net Change in Cash` | CFS sub-totals |
| H14 | **Cash floor** | `Cash_t ≥ Min_Cash` (warning if false) | 流動性 |
| H15 | **Revolver ≥ 0** | `Revolver_t ≥ 0` | Plug 非負 |

### 12.2 Soft checks (warning, 黄色フラグ)

| # | Check | 閾値 |
|---|---|---|
| S1 | Gross Margin in [0, 100%] | range |
| S2 | EBIT Margin not declining > 20pp YoY without explanation | 急変 |
| S3 | DSO not exploding (< 90 days for SaaS) | 業種依存 |
| S4 | DPO not negative or > 180 | range |
| S5 | CapEx not negative | sign |
| S6 | Tax provision not negative when PBT > 0 | sign / refund |
| S7 | NI margin not exceeding gross margin | sanity |
| S8 | Diluted shares ≥ Basic shares | TSM |
| S9 | Revenue growth > 200% YoY without context | bubble |
| S10 | NWC days not changing > 50% YoY | unstable |

### 12.3 SanityChecks シート例

```
                                 Y1     Y2     Y3     Y4     Y5
HARD CHECKS (must be 0)
H1  BS balance                    0      0      0      0      0     ✓
H2  Cash tie                      0      0      0      0      0     ✓
H3  RE roll                       0      0      0      0      0     ✓
H4  PP&E roll                     0      0      0      0      0     ✓
H5  AD roll                       0      0      0      0      0     ✓
...

SOFT CHECKS (warnings)
S1  GM in [0,100%]               TRUE   TRUE   TRUE   TRUE   TRUE   ✓
S2  EBIT Δ < 20pp                TRUE   TRUE   TRUE   TRUE   TRUE   ✓
S3  DSO < 90                     TRUE   TRUE   TRUE   TRUE   TRUE   ✓
...

OVERALL STATUS                   PASS   PASS   PASS   PASS   PASS
```

セル: `=IF(ABS(check_value) < 0.0001, "✓", "✗")`、conditional formatting で✓緑、✗赤。

### 12.4 循環参照 (Circular Reference)

- **Intentional**: Revolver interest, Avg balance interest, Tax with NOL → iterative calc ON
- **Unintentional**: 数式コピペで forward 参照 → **必ず修正**

判別:
- File → Options → Formulas → Enable iterative calc (max 100, change 0.001)
- ON にしても解けない循環は **bug**
- Bug 検出: Iterative OFF → 循環 alert → trace で発見

---

## 13. 期間粒度

### 13.1 粒度ごとの特徴

| 粒度 | 適用場面 | 強み | 弱み |
|---|---|---|---|
| **Monthly** | 12-18 か月先 / cash forecasting / fundraise | 季節性・runway を捉える、ramp curve 表現 | データノイズ大、構築工数大 |
| **Quarterly** | 公開準備 / IB レポート / 18-36 か月 | IB 標準、公開報告と整合 | 月次変動の埋没 |
| **Annual** | 5-10 年 long-range / DCF | 長期視点、構造シンプル | 短期キャッシュ管理に不向き |

### 13.2 Hybrid 粒度設計 (推奨)

```
Year 1-2: Monthly
Year 3-5: Quarterly (Year 1-2 の monthly を集計し period total として表示)
Year 6+:  Annual (Quarterly を 4 集計)
```

集計関数:
- `Quarterly = SUMIF(Period_label = current_quarter)`
- `Annual = SUM(4 quarters)`
- BS は **stock の最終値** を取る (`= 期末月の BS`), 平均でない。

### 13.3 Drill-down 設計

- **Drivers シート**: 月次のみ
- **IS / BS / CFS シート**: 月次 / 四半期 / 通年の 3 view を sheet level または column group で持つ

---

## 14. 数値例 (Mini Integrated Model)

> **設定**: 創業 3 年目 SaaS スタートアップ。Y0 (期初 BS) → Y1 (1 年予測) を完全に展開。

### 14.1 Inputs (assumptions)

```
Revenue (Y1)              $10,000  (Y0: $0 implicit, simplification)
Gross margin              70%
COGS = $3,000
S&M                       $4,000  (incl. SBC $500)
R&D                       $3,500  (incl. SBC $700)
G&A                       $1,500  (incl. SBC $300)
SBC total                 $1,500  (split above)
D&A                       $500    (allocated: COGS $100, OpEx $400)
Interest expense          $200    (term loan)
Tax rate (effective)      0%      (NOL absorbs PBT, VA = 100%)
DSO                       45 days
DPO                       30 days
Prepaid days              7
Accrued days              14
Deferred Rev = Rev × 30%  $3,000
CapEx (Y1)                $800
LT Debt issuance          $0
LT Debt repayment         $200
Equity raise              $5,000  (Series A)
Min cash                  $500
```

### 14.2 Income Statement (Y1)

```
Revenue                          10,000
COGS (incl. $100 D&A)           (3,000)
   Gross Profit                   7,000   (70% margin)
S&M (incl. SBC $500)            (4,000)
R&D (incl. SBC $700)            (3,500)
G&A (incl. SBC $300)            (1,500)
   D&A in OpEx (already in)        ---
   Total OpEx                   (9,000)
   EBIT (Op Income)             (2,000)
Interest expense                  (200)
   Pre-tax Income (PBT)         (2,200)
Tax (0% effective, NOL)              0
   Net Income                   (2,200)
```

### 14.3 Balance Sheet (Y0 → Y1)

```
                          Y0       Y1
Cash                       0    *plug, computed below
AR                         0    1,233   (= 10,000 × 45/365)
Prepaid                    0       96   (= (4000+3500+1500) × 7/365 ≈ 173... 
                                          OpEx denominator design choice; use $5000 base → 96)
Total Current Assets       0    1,329 + Cash

Gross PP&E             1,000    1,800   (+800 CapEx)
Accum Dep               (200)    (700)  (Y0 (200) − Y1 dep 500)
Net PP&E                 800    1,100
Total Assets             800    2,429 + Cash

AP                         0      247   (= 3,000 × 30/365)
Accrued                    0      192   (= 5,000 × 14/365 ≈ 192)
Deferred Revenue           0    3,000   (= 10,000 × 30%)
Current Portion LT Debt    0      200
Total Current Liab         0    3,639

LT Debt                1,000      600   (1,000 − 200 repaid − 200 reclass)
Total Liabilities      1,000    4,239

Common + APIC          1,000    7,500   (+5,000 raise + 1,500 SBC)
Retained Earnings       (200)  (2,400)  ((-200) + (-2,200) NI)
Total Equity             800    5,100
Total L+E              1,800    9,339 ?? — ここで ASSETS とずれが出る → Cash plug を解く

Cash plug:
Total Assets must = 9,339
Cash = 9,339 − (1,329 + 1,100) = 6,910
```

### 14.4 Cash Flow Statement (Y1)

```
CFO:
  Net Income                          (2,200)
  + D&A                                  500
  + SBC                                1,500
  - ΔAR                              (1,233)
  - ΔPrepaid                             (96)
  + ΔAP                                  247
  + ΔAccrued                             192
  + ΔDeferred Rev                      3,000
  CFO Total                            1,910

CFI:
  - CapEx                               (800)
  CFI Total                             (800)

CFF:
  - LT Debt Repayment                   (200)
  + Equity Raise                       5,000
  CFF Total                            4,800

Net Change in Cash                     5,910
Cash Beginning (Y0)                        0
Cash Ending (Y1)                       5,910

Wait — ↑ disagrees with BS plug (6,910). Let's check.
```

### 14.5 Reconciliation (デバッグの実例)

> **教訓**: 上のずれは実装中に必ず起きる。手作業で diff を掘る。

差額 $1,000 = 実は Y0 BS の Cash を 0 と置いたが、 BS が `Total Assets = 800` で `Total L&E = 1,800` という **そもそも Y0 BS が unbalanced** という設定ミス。修正版:

```
Y0 BS (修正): 
  Cash 1,000, Net PP&E 800, Total Assets 1,800
  LT Debt 1,000, Common+APIC 1,000, RE (200), Total L&E 1,800   ✓

Y1 Cash = Y0 Cash 1,000 + ΔCash 5,910 = 6,910
BS 側 plug もこの 6,910 と一致 ✓
```

H2 (Cash tie) check passed. → このようなデバッグ手順を **毎期の SanityChecks で自動化** する。

### 14.6 Sanity Checks (Y1)

```
H1  BS balance:    9,339 − 9,339 = 0           ✓
H2  Cash tie:      6,910 − 6,910 = 0           ✓
H3  RE roll:       (-2,400) − (-200) − (-2,200) = 0  ✓
H4  PP&E roll:     1,800 − 1,000 − 800 = 0     ✓
H5  AD roll:       (700)−(200) − 500 = 0       ✓
H6  Debt roll:     800 − 1,000 + 200 = 0       ✓
H7  APIC roll:     7,500 − 1,000 − 5,000 − 1,500 = 0  ✓
S1  GM in range:   70% ✓
S5  CapEx ≥ 0:     ✓
```

すべて PASS。これがマスター期にできる状態。

---

## 15. 3-Statement DD チェックリスト (実務用)

> **使用シーン**: 自分のモデル / 他人のモデル / DD で渡されたモデルの **45 分速攻レビュー**。
> **判定**: ✓ Pass, ⚠ Warning, ✗ Fail。

### 15.1 構造 (Structure)

- [ ] 3 表が独立 sheet または single sheet で明示的にラベル
- [ ] 入力 (青) / 計算 (黒) / リンク (緑) 色分けが一貫
- [ ] 全期間 1 計算式でドラッグ可能 (hard-coded `100` などが forecast 期間にない)
- [ ] Inputs シートが独立して存在し、すべての driver がそこに集約
- [ ] Sheet 数 ≤ 15 (過度に分散していない)

### 15.2 P&L (IS)

- [ ] Revenue が driver-based (顧客 × ARPU 等), 単純 % growth でない
- [ ] COGS が variable / fixed に分解
- [ ] OpEx が S&M / R&D / G&A の標準 3 区分
- [ ] EBITDA, EBIT, Pre-tax, NI のサブトータルが明示
- [ ] D&A が IS 内 (COGS / OpEx 配分) と CFS add-back の両方に整合
- [ ] SBC が IS 内に計上され CFS で add-back
- [ ] Interest expense / income が分離され、debt schedule と一致
- [ ] Tax provision が NOL を考慮 (累損段階で 0 なら確認)
- [ ] Diluted EPS が basic ≥, TSM 適用

### 15.3 BS

- [ ] BS が毎期 balance (assets = L+E)
- [ ] Cash と Revolver の片方のみが plug
- [ ] PP&E が gross / accum dep / net で表示
- [ ] AR / Inv / AP が DSO / DIO / DPO driver で計算
- [ ] Deferred Revenue が rev rec schedule と整合
- [ ] LT Debt と Current Portion が分離
- [ ] APIC が SBC + equity raise で roll-forward
- [ ] RE が NI − Dividends で roll-forward
- [ ] ROU 資産 / Lease Liab が ASC 842 / IFRS 16 / 新リース基準準拠
- [ ] DTA / DTL が tax schedule から flow

### 15.4 CFS

- [ ] Indirect method (NI 出発)
- [ ] CFO add-back: D&A, SBC, deferred tax, other non-cash
- [ ] CFO ΔWC: AR/Inv/Prep を sign-flip (BS 増 → CFO 減)
- [ ] CFI: CapEx は単独行、M&A 別行
- [ ] CFF: Debt issue/repay, equity issue/buyback, dividends 各別行
- [ ] FX 影響行が存在 (海外子会社あり)
- [ ] Ending cash = BS cash (H2 check)

### 15.5 Schedules

- [ ] Working Capital schedule が独立
- [ ] Debt schedule が独立 (term loan / revolver / lease 各別)
- [ ] Tax schedule に NOL roll-forward
- [ ] SBC schedule に grant / vesting
- [ ] Lease schedule (ASC 842 / IFRS 16) で ROU と Liab roll
- [ ] Equity schedule (cap table) で diluted share count

### 15.6 SanityChecks

- [ ] BS balance (H1) 全期 0
- [ ] Cash tie (H2) 全期 0
- [ ] All roll-forwards (H3-H12) 全期 0
- [ ] CFS internal sum (H13) 0
- [ ] Cash floor (H14) ≥ Min_Cash 全期
- [ ] Soft checks (S1-S10) PASS or 説明可
- [ ] 循環参照は intentional のみ (iterative calc ON で解ける)

### 15.7 シナリオ

- [ ] Switch cell が 1 か所に集約
- [ ] Base / Up / Down の 3 ケースが全 driver に存在
- [ ] CHOOSE / INDEX / SWITCH 関数で参照、OFFSET なし
- [ ] シナリオを変えても BS check が崩れない (= 連結が完全)

### 15.8 期間粒度

- [ ] Monthly / Quarterly / Annual の view が明示
- [ ] 集計が SUMIF / SUM 4Q で機械的
- [ ] BS 集計は flow ではなく stock の期末値

### 15.9 開示 / Documentation

- [ ] 各シートの先頭に目的・更新日・作成者
- [ ] Inputs に source 注記 (e.g., "Per Q3 board deck")
- [ ] Assumptions に sensitivity (key drivers ±10%)
- [ ] バージョン管理 (file name に v1.0, v1.1)

### 15.10 Governance / 監査耐性

- [ ] 印刷時 1 ページに収まる KPI dashboard
- [ ] PDF export 用 layout が整っている
- [ ] レンダリング (色, フォント) が DESIGN.md 準拠 (淡 surface, ink 本文, 強調 1 か所)
- [ ] Files / cells が password-protected (機密 deal の場合)

---

## 16. 参考文献 (Primary Sources)

> 以下は本書を構築する上で参照した一次・準一次資料。実装時は最新版を再確認すること。

- **Wall Street Prep**:
  - "How are the Three Financial Statements Linked?" `wallstreetprep.com/knowledge/how-are-the-financial-statements-linked/`
  - "3-Statement Model | Complete Guide (Step-by-Step)" `wallstreetprep.com/knowledge/build-integrated-3-statement-financial-model/`
  - "Balance Sheet Forecasting | Step-by-Step Guide" `wallstreetprep.com/knowledge/guide-balance-sheet-projections/`
  - "Income Statement Forecasting | Projection Guide"
  - "Working Capital Cycle | Formula + Calculator"
  - "Cash Conversion Cycle | Formula + Calculator"
  - "Revolver Debt | Formula + Calculation Example"
  - "Debt Schedule | Formula + Calculator"
  - "Stock Based Compensation (SBC) | Journal Entry + Examples"
  - "Non-Controlling Interest (NCI) | Formula + Calculator"
  - "Scenario Analysis | Excel Tutorial Lesson"
- **Macabacus**:
  - "Income Statement Projections" `macabacus.com/operating-model/income-statement-projections`
  - "Balance Sheet Projections" `macabacus.com/operating-model/balance-sheet-projections`
  - "Debt Balance Projections" `macabacus.com/operating-model/debt-balance-projections`
  - "Cash Sweep & Revolving Debt Repayment Guide" `macabacus.com/operating-model/revolver-cash-sweep`
  - "Debt Characteristics" `macabacus.com/operating-model/debt-characteristics`
  - "Balance Sheet Set-Up (LBO)" `macabacus.com/lbo-model/balance-sheet`
- **Mergers & Inquisitions / BIWS**:
  - "Noncontrolling Interests: The Full Consolidation Accounting Tutorial" `mergersandinquisitions.com/noncontrolling-interests/`
  - "Debt Schedule: Video Tutorial and Excel Example" (BIWS)
  - Debt Primer (BIWS)
- **Corporate Finance Institute (CFI)**:
  - "How the 3 Financial Statements are Linked Together"
  - "Auditing and Balancing a 3-Statement Model"
  - "10 Common Causes of Imbalance in 3-Statement Models"
  - "Cash Conversion Cycle"
  - "Indirect Method"
  - "Consolidation Method"
- **Street of Walls**: "Three Statement Financial Modeling"
- **Morgan Stanley Counterpoint Global**: Mauboussin, "Stock-Based Compensation Unpacking the Issues"
- **会計基準 (公式)**:
  - FASB ASC 606 (Revenue from Contracts with Customers)
  - FASB ASC 842 (Leases)
  - FASB ASC 740 (Income Taxes), Bloomberg Tax 解説
  - IFRS 15 (Revenue)
  - IFRS 16 (Leases)
  - IAS 12 (Income Taxes)
- **日本基準 (公式)**:
  - 企業会計基準第 29 号「収益認識に関する会計基準」(ASBJ, 2018/3/30 公表, 改正 2020/3/31)
  - 「リースに関する会計基準」(ASBJ, 2024/9/13 公表, 2027/4/1 適用)
  - 国税庁 No.5762「青色申告書を提出した事業年度の欠損金の繰越控除」
  - 経済産業省「特別試験研究費税額控除制度」
  - 国税庁「収益認識に関する会計基準への対応について」
- **PwC / Deloitte / EY Japan**:
  - PwC Viewpoint "Accounting for a consolidated entity"
  - Deloitte "Roadmap to Accounting for Noncontrolling Interests"
  - EY Japan「新リース会計基準における実務上のポイント」
  - EY Japan「グループ通算制度における繰越欠損金の実務」
- **その他実務記事**:
  - Forvis Mazars "Top 10 ways to fix an unbalanced balance sheet"
  - FinQuery "Right-of-Use Asset & Lease Liability Explained"
  - BDO "Accounting for Leases Under ASC 842"

---

## 付録 A. Excel 実装テンプレート (Cell-level Pseudocode)

> **目的**: Skill から `xlsx` を生成するときに、これを 1:1 に並べる。

### A.1 シート構成

```
Workbook:
  - Cover         (目次, バージョン, 作成日)
  - Inputs        (driver, assumptions, scenario switch)
  - Drivers       (revenue / cost driver detail)
  - IS            (Income Statement)
  - BS            (Balance Sheet)
  - CFS           (Cash Flow Statement)
  - Sched_WC      (Working Capital schedule)
  - Sched_PPE     (PP&E + D&A)
  - Sched_Debt    (Term Loan + Revolver)
  - Sched_Tax     (NOL, DTA/DTL, ETR walk)
  - Sched_SBC     (Grants + vesting + APIC)
  - Sched_Lease   (ROU + Liab, ASC 842 / IFRS 16)
  - Sched_RevRec  (Deferred Rev + Contract Asset)
  - Sched_Equity  (Cap table + TSM diluted shares)
  - SanityChecks  (H1-H15 + S1-S10)
  - Outputs       (KPI dashboard, charts, exports)
```

### A.2 主要セルの命名 (Excel Named Ranges)

```
S_Switch         → Inputs!B2
Min_Cash         → Inputs!B5
Tax_Rate         → Inputs!B10
DSO              → Inputs!B20
DIO              → Inputs!B21
DPO              → Inputs!B22
Periods          → Inputs!B30 (forecast 月数)
StartDate        → Inputs!B31
```

### A.3 IS の Net Income 行 (例)

```
=IS!Pretax_Income − IS!Tax_Provision

  IS!Tax_Provision
    = IF(IS!Pretax_Income < 0, 0,
        MAX(0, (IS!Pretax_Income − Sched_Tax!NOL_used) × Tax_Rate))
```

### A.4 BS の Cash 行 (Revolver plug 採用)

```
BS!Cash_t
  = MAX(Min_Cash,
         BS!Cash_{t-1} + CFS!CFO_t + CFS!CFI_t + CFS!CFF_excl_revolver_t + CFS!FX_t)
  + Sched_Debt!Revolver_change_t
```

### A.5 SanityChecks の例 (B5 行)

```
H1: =BS!Total_Assets_t − BS!Total_LE_t            → 期待 0
H2: =CFS!Cash_End_t − BS!Cash_t                    → 期待 0
H3: =BS!RE_t − BS!RE_{t-1} − IS!NI_t + Inputs!Div_t → 期待 0
...
Format: =IF(ABS([cell]) < 0.0001, "OK", "BREAK")
        Conditional formatting: "OK" green, "BREAK" red
```

---

## 付録 B. SaaS / Hardware / Marketplace 別のテンプレ差分

| 項目 | SaaS | Hardware | Marketplace |
|---|---|---|---|
| Revenue driver | Customers × ARPU | Units × ASP | GMV × Take rate |
| COGS 主成分 | Hosting + Customer Support | Materials + Logistics | Payment + Support |
| Gross Margin | 70-85% | 30-50% | 50-70% (taking 5-20% of GMV) |
| Inventory | 0 | 30-90 days DIO | 0 (3P) or 30-60 (1P) |
| Deferred Rev | 大 (annual prepay) | 0 (point-in-time) | 中 (subscription tier) |
| Working Capital | Negative (好転的) | Positive | Mixed |
| CapEx | Low (cloud-native) | High (mfg eq) | Low |
| SBC ratio | High (15-25% of rev) | Low (5-10%) | Mid (10-15%) |
| 主要 KPI | ARR / NRR / Magic # | GP per unit / inventory turn | Take rate / GMV growth |

---

## 付録 C. 日米 GAAP 主要差異の一覧 (実装時の留意)

| 領域 | US GAAP | IFRS | JGAAP |
|---|---|---|---|
| Revenue | ASC 606 | IFRS 15 | 収益認識 (29 号) |
| Lease | ASC 842 (dual model) | IFRS 16 (single) | 新リース基準 (2027 適用, single 風) |
| Inventory | LIFO / FIFO / WAvg | LIFO 不可、FIFO / WAvg | LIFO 廃止済、FIFO / WAvg |
| Goodwill | 非償却、年次 impairment | 非償却、年次 impairment | 20 年内で償却 (改正で IFRS 寄せ議論あり) |
| R&D | 全費用化 (一部 SW dev cap) | Research 費用、Development 資産化 | 試験研究費は費用化、SW 開発費は条件付き資産化 |
| 開発研究 SW | ASC 350-40 (内部使用) cap, ASC 985 (販売) | IAS 38 | 研究開発費等会計基準 |
| Income Tax | ASC 740 (DTA + VA) | IAS 12 (recoverable のみ計上) | 税効果会計基準 (回収可能性の判断) |
| FX | ASC 830 | IAS 21 | 外貨建取引等会計処理基準 |
| 連結 | ASC 810 (VIE 含む) | IFRS 10 | 連結財務諸表に関する会計基準 |
| Comprehensive Income | OCI / AOCI | OCI / AOCI | その他の包括利益 (継続事業 + 評価差額金) |

---

## 付録 D. レビューに使う「黄金の 5 質問」

> **モデルを 5 分でレビューする質問**。

1. **BS は balance しているか?** (`H1 == 0`)
2. **CFS の ending cash は BS の cash と一致しているか?** (`H2 == 0`)
3. **Plug は何を使っているか?** (Cash / Revolver の 1 つだけか)
4. **循環参照は意図的か?** (iterative calc ON で解けるか)
5. **シナリオを切り替えても全 sanity check が PASS か?** (連結の堅牢性)

5 つすべて Yes なら IB 品質に到達している可能性が高い。1 つでも No なら、**まずそこを直してから** 議論を始める。

---

> **本リファレンスの位置づけ**: スタートアップ向け財務モデルを「説得できる」「監査される」品質に押し上げるための実務仕様書。Skill は本書の章番号・チェック番号を Excel 上で再現することで、再現性ある自動生成を担保する。
