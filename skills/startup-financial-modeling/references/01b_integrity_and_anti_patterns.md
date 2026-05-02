---
name: integrity_and_anti_patterns
description: 三表突合 / sensitivity / SanityChecks / 監査 / 避けるべき anti-pattern の正本。SKILL.md dispatch から「三表突合」「SanityChecks」「audit」を聞かれた際に第 2 reference として読まれる (第 1 は 06)。
type: reference
priority: P1
related: [_terminology, 01a_modeling_standards, 06_three_statement, _self_review_protocol]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 用語・色・閾値は [`_terminology.md`](_terminology.md) を canonical とする
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) §A 構築フェーズ + [`_self_review_protocol §2`](_self_review_protocol.md) の 6 軸監査の cross-domain coverage
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check を必ず実行
- **関連 reference**: `01a_modeling_standards` (formatting) / `06_three_statement §12` (SanityChecks 設計) / `_self_review_protocol` (6 軸監査)

# 01b. Integrity Layer・Sensitivity・ドキュメンテーション・Anti-pattern 徹底リファレンス

財務モデルの後半工程 — 検証 (integrity)、感応度分析 (sensitivity)、文書化 (documentation)、避けるべきパターン (anti-patterns)、監査 (auditing) — の実務リファレンス。フロント工程 (構造設計、ドライバー選定、三表構築) は `01_modeling_principles.md` および `06_three_statement.md` を参照。

> **対象**: スタートアップ CFO/FP&A、IB/PE/VC アナリスト、シードからレイトステージまでのモデル制作者。
> **想定環境**: Microsoft Excel (Windows / Mac)。Google Sheets で代替可能なものは併記。
> **準拠基準**: Wall Street Prep、Macabacus、EuSpRIG (European Spreadsheet Risks Interest Group)、FAST Standard、SSRB (Spreadsheet Standards Review Board)。

---

## 目次

1. [Integrity Layer (エラーチェック)](#1-integrity-layer)
   - 1.1 BS check (Assets = L + E)
   - 1.2 CF check (CFS ending cash = BS ending cash)
   - 1.3 三表突合 (Net Income IS→CFS→BS retained earnings)
   - 1.4 Sum check (横列合計 vs 縦列合計)
   - 1.5 Sign check (符号方向)
   - 1.6 循環参照と意図的 iterative calc (revolver)
   - 1.7 Master Check セルの実装
2. [Sensitivity Analysis](#2-sensitivity-analysis)
   - 2.1 Excel Data Table (1 変数 / 2 変数)
   - 2.2 Tornado Chart の作成手順
   - 2.3 Scenario Manager (Excel 標準機能)
   - 2.4 Input toggle pattern (CHOOSE / INDEX / SWITCH)
3. [Documentation Conventions](#3-documentation-conventions)
   - 3.1 Cover sheet 必須項目
   - 3.2 Version log
   - 3.3 Assumptions log
   - 3.4 Instructions sheet
   - 3.5 Comments の使い方 (cell comment vs notes column)
4. [Anti-patterns (避けるべきパターン)](#4-anti-patterns)
   - 4.1 ハードコード混在
   - 4.2 同一行内に複数の数式パターン
   - 4.3 不可視シート
   - 4.4 隠し列の濫用
   - 4.5 Named range の濫用
   - 4.6 OFFSET / INDIRECT (volatile)
   - 4.7 巨大 IF nest
   - 4.8 Merged cells で数式
   - 4.9 空白行による視覚的グルーピング
   - 4.10 旧バージョンのコピペ残存
5. [Spreadsheet 監査手順](#5-spreadsheet-auditing)
   - 5.1 F2 数式トレース
   - 5.2 Trace Precedents / Dependents
   - 5.3 Formula Auditing toolbar
   - 5.4 Watch Window
   - 5.5 Inquire add-in
   - 5.6 Spreadsheet Compare / 外部監査ツール
6. [IB 品質チェックリスト (60+ 項目)](#6-ib-quality-checklist)

---

## 1. Integrity Layer

財務モデルの「壊れていないこと」を機械的に保証する層。**人間がレビューする前に、モデル自身が自己検証を成立させる**ことが目標。IB の MD レビューでは、Master Check が緑であることが「席に座る権利」になる。

### 1.1 BS check (Assets = Liabilities + Equity)

会計恒等式 `Total Assets = Total Liabilities + Total Equity`。**1 円でも合わなければモデルは壊れている**。差額を許容する閾値は「ゼロ」(機械的に厳密) が推奨。`ROUND` で丸めると、丸め誤差で隠された別バグを取りこぼす。

#### 悪い例

```
B50  Total Assets       1,250
B51  Total Liab + Eq    1,248
B52  BS Check           OK    ← 目視で OK と書いている / 数式で検証していない
```

または、

```
B52  =IF(ABS(B50-B51)<10,"OK","NG")   ← 10 円までずれを許容
```

**なぜ問題か**:
- 「OK」が手書きで自動更新されない。
- 閾値 10 円は、別の符号バグを覆い隠す可能性がある (1,000 円のミスと 990 円のミスの差し引きで合計 10 円なら通ってしまう)。

#### 良い例

```
B50  Total Assets             =SUM(B30:B49)
B51  Total Liab + Equity      =SUM(B70:B99)
B52  BS Diff                  =B50-B51
B53  BS Check                 =IF(ROUND(B52,4)=0,"OK","CHECK")
```

- B52 で **差額そのものを表示** (デバッグ時に符号と桁が分かる)。
- B53 で OK/CHECK を出すが、判定は B52 を機械的に評価。
- `ROUND(_,4)` は浮動小数点の丸め誤差 (e.g., 1.0e-13) のみを吸収する目的で、業務的な許容ではない。

#### 期間ごとの BS check

すべての期間 (列) で個別にチェックし、**ワークシート末尾に行サマリー** (`=AND(C53:Z53="OK")`) を置く。

```
B53:Z53  各期 BS check        OK / CHECK
AA53     All Periods          =IF(COUNTIF(B53:Z53,"CHECK")=0,"OK","NG")
```

### 1.2 CF check (CFS ending cash = BS ending cash)

キャッシュフロー計算書 (CFS) の期末現金が、貸借対照表 (BS) の Cash & Equivalents 行と一致するか。**三表整合性の最も強力なチェック**。

#### 悪い例

CFS で期末現金を「BS から拾ってくる」: `CFS Ending Cash = BS!Cash` — これは check ではなく循環的に同じ数値を表示しているだけ。

#### 良い例

```
CFS!B40  Cash, Beginning of Period      =CFS!A40 (前期末) または BS!A_cash (前期)
CFS!B41  + Net Change in Cash           =SUM(B30:B39)   ← CFO+CFI+CFF
CFS!B42  Cash, End of Period            =B40+B41

BS!B25   Cash & Equivalents              (independently computed)

Check!B5 CFS End vs BS End               =CFS!B42-BS!B25
Check!B6 CF Check                        =IF(ROUND(B5,4)=0,"OK","CHECK")
```

ポイント: BS の Cash は **plug ではなく、独立に積み上がる** 構造であるべき。CFS の `期首+ΔCash` と BS の Cash が両方独立に計算されてはじめて、両者の一致が三表整合性の証拠になる。

### 1.3 三表突合 (Net Income → Retained Earnings)

`期末 RE = 期首 RE + Net Income - Dividends`。IS の Net Income が CFS の出発点として使われ、最終的に BS の Retained Earnings に到達するライン。

#### チェック式

```
IS!NetIncome           = X
CFS!NetIncome (top)    = =IS!NetIncome
BS!RE_end              = BS!RE_beg + IS!NetIncome - Dividends_paid

Check!NI Tie           = CFS!NetIncome - IS!NetIncome   → 0 であるべき
Check!RE Roll          = BS!RE_end - (BS!RE_beg + IS!NetIncome - Dividends)  → 0 であるべき
```

**スタートアップ特有の注意**: ストックオプション費用 (SBC) が IS で費用計上され、CFS で non-cash add-back され、BS で APIC に積み上がる。この三表ループも整合チェックの対象。

```
SBC!IS_expense          = $X
CFS!Add-back SBC        = +$X
BS!APIC end             = APIC beg + SBC + 新規株式発行に伴う APIC
```

### 1.4 Sum check (横列合計 vs 縦列合計)

**横方向の累計 (年次→累計)** と **縦方向の集計 (科目→小計)** が独立に計算されている場合、両者の合計が一致するか確認する。

#### 悪い例: 単一の合計セルに頼る

```
        Y1  Y2  Y3  Total
Rev     100 110 121  =SUM(B:D)
COGS    50  55  60   =SUM(B:D)
GP                   ← 計算していないか、Total 列だけで計算
```

**なぜ問題か**: GP の「期間別」と「累計」が別の数式パスで計算されないため、年次内訳のミスが集計だけで発見できない。

#### 良い例: 二重集計

```
              Y1   Y2   Y3   Total (横)
Rev           100  110  121  =SUM(B:D)
COGS          50   55   60   =SUM(B:D)
GP            =B-B =C-C =D-D =SUM(B:D)
GP (縦)       =B-B =C-C =D-D =SUM(B:D)  ← 別計算

Cross check: Total GP (横の最後) = Total GP (縦の最後)
```

#### Implementation: Cross-foot

```
Check!CrossFoot = SUM(横方向の Total) - SUM(縦方向の Total)   → 0
```

### 1.5 Sign check (符号方向)

費用は「正の数として入力 → 数式で減算」とするか、「負の数として入力 → 数式で加算」するかを **モデル全体で統一**。混在は最大のバグ温床。

#### 推奨ルール (Wall Street Prep / Macabacus 準拠)

- **IS**: 費用は **正の値** で入力し、数式で減算 (`Revenue - COGS - OpEx`)。表示は青文字 (input)。
- **CFS**: 投資 CF と財務 CF のキャッシュアウトは **負の値** で表示。CapEx は `-X`。
- **BS**: 資産・負債・資本いずれも **正の値**。負の含み (累積赤字 RE) のみ自然に負になる。

#### 悪い例

```
Revenue    1,000
COGS         400      ← 費用を正で入力
Gross Profit  =Rev + COGS  ← うっかり加算 → 1,400 になる
```

#### 良い例

```
Revenue    1,000
COGS         400      ← 費用を正で入力 (青文字 input)
Gross Profit  =Rev - COGS  ← 数式で減算 → 600
```

#### Sign check 数式

```
Check!Cost_signs  = IF(MIN(COGS_row)<0, "CHECK", "OK")
Check!CapEx_sign  = IF(MAX(CapEx_row)>0, "CHECK", "OK")    ← CFI で正値が出たら異常
Check!Rev_sign    = IF(MIN(Revenue_row)<0, "CHECK_NEGREV", "OK")  ← 売上マイナスは要確認
```

### 1.6 循環参照と意図的 iterative calc (revolver)

#### 循環参照 = 通常はバグ

`A1 = B1+1`, `B1 = A1+1` のような直接循環は、ステータスバーに `Circular references: A1` と表示される。**99% はバグ**。発見手順:

1. `Formulas → Error Checking → Circular References` でセル位置を取得。
2. F2 で precedents を辿る。
3. 大半は「Tax Expense が PBT を参照、PBT が Interest を参照、Interest が Net Debt を参照、Net Debt が Cash を参照、Cash が Net Income を参照、Net Income が Tax Expense を参照」というループ。

#### 意図的循環: Revolver / Cash Sweep

リボルビング・クレジットの期末残高は `期首残高 + 必要借入額` で、必要借入額は `最低現金維持後の不足額` で、不足額は `当期 CF` に依存し、当期 CF の利息費用は **当期平均借入残高に依存**。これは数学的に自然な循環。

##### 設定方法

```
File → Options → Formulas → Enable iterative calculation
  Maximum Iterations: 100
  Maximum Change: 0.001
```

##### 安全装置: Circuit Breaker

意図的循環でも、計算が発散したり、入力エラーで爆発することがある。**Circuit Breaker セルで強制的に切断できるトグル** を作る。

```
Inputs!CircuitBreaker      = 0   (0=normal, 1=cut interest)
Calc!Interest_on_Revolver  = IF(Inputs!CircuitBreaker=1, 0, AvgBalance * Rate)
```

問題発生時は CB=1 にして数値を一旦凍結 → 入力を直す → CB=0 に戻す。

##### Revolver の標準実装

```
Beg Revolver Balance       = prev period End Balance
Cash Available before Rev  = Beg Cash + CFO + CFI + CFF (excl. revolver)
Min Cash Required          = (input)
Cash Surplus / (Deficit)   = Cash Available - Min Cash
Revolver Drawdown          = MAX(0, -Cash Surplus)
Revolver Repayment         = MIN(Beg Revolver, MAX(0, Cash Surplus))
End Revolver Balance       = Beg Rev + Drawdown - Repayment
End Cash                   = Cash Available + Drawdown - Repayment
Avg Revolver Balance       = AVERAGE(Beg, End)
Interest Expense (Revolver)= Avg Balance * Interest Rate    ← ループポイント
```

#### Iterative Calc OFF を推奨する場合

監査者・投資家が読む最終モデルでは、**iterative calc を OFF にして開いても破綻しないモデル** が望ましい。手段:

- Revolver は `MAX(0, 前期末値ベース)` で近似し、当期 NI への影響は許容する (簡易型)。
- もしくは、Goal Seek スタイルで一度収束させた値を Paste Special Values でハードコードし、`= [hardcoded interest]` の形にする (`Live` セルと `Locked` セルを切り替え)。

### 1.7 Master Check セル

#### 設計原則

- モデルの **全シートの全 check** を 1 か所に集約。
- Cover sheet の右上または Footer に常に表示。
- 1 つでも CHECK があれば赤背景。すべて OK なら緑。
- **赤いまま提出された PDF** が IB アナリストの最大の恥。

#### 実装パターン

##### Pattern A: シンプルな AND 集約

```
Check!Sheet1_BS_OK    = COUNTIF(BS!Check_row, "CHECK")
Check!Sheet1_CF_OK    = COUNTIF(CFS!Check_row, "CHECK")
Check!Sheet1_NI_Tie   = ABS(Check!NI_diff) > 0.01
...
Master!B2  Total Errors  = SUM(Check!B:B)
Master!B3  Status         = IF(B2=0, "OK", "ERRORS: " & B2)
```

条件付き書式: `Status` セルが "OK" なら緑背景、それ以外は赤背景。

##### Pattern B: Named range で全 check を一覧化

`AllChecks` という名前付き範囲に全 check 行を含め、Cover sheet で:

```
=IF(COUNTIF(AllChecks,"CHECK")+COUNTIF(AllChecks,"NG")+COUNTIF(AllChecks,"#REF!")=0,
    "ALL CHECKS PASS", "REVIEW NEEDED")
```

##### Pattern C: ヘッダ常駐 (固定行)

Row 1 に Master Check を置き、`View → Freeze Panes → Freeze Top Row`。どのシート、どのセルにいても、画面上部で赤/緑が常に見える状態にする。

```
Row 1:  ▼ MASTER CHECK ▼  [OK]  Last calc: 2026-05-01 14:32  Version: v1.4
```

#### Check の最低構成 (推奨 8 項目)

| # | Check | 期待値 | 実装 |
|---|---|---|---|
| 1 | BS check | Assets = L+E (差 0) | 各期 + 合計 |
| 2 | CF tie | CFS End Cash = BS Cash | 各期 |
| 3 | NI tie | IS NI = CFS NI (top line) | 各期 |
| 4 | RE roll | RE end = RE beg + NI − Div | 各期 |
| 5 | Debt roll | Debt end = beg + draw − repay | 各期 |
| 6 | PP&E roll | PP&E end = beg + CapEx − Dep − disposal | 各期 |
| 7 | Cross-foot | 横合計 = 縦合計 | 主要小計 |
| 8 | Error cell | `#REF!`, `#DIV/0!`, `#VALUE!` 検出 | `COUNTIF(All, "#*")` |

#### エラー値の検出 (#REF! など)

```
Check!HasErrors  = SUMPRODUCT(--ISERROR(全モデル範囲))
Check!Status     = IF(HasErrors=0, "OK", "FORMULA ERRORS: " & HasErrors)
```

注: `SUMPRODUCT(--ISERROR(...))` は揮発関数を含まずに範囲全体のエラーを数えられる。`OFFSET` は使わない (4 章 anti-pattern 参照)。

---

## 2. Sensitivity Analysis

### 2.1 Excel Data Table (1 変数 / 2 変数)

`Data → What-If Analysis → Data Table` (Mac: `Data → What-If Analysis → Data Table`)。**入力を変えてアウトプットがどう変わるか** を 1 関数で一括計算する標準機能。

#### 1 変数 Data Table

##### レイアウト (列入力)

```
        B           C
3                  =Output_cell    ← formula を「左上に隣接した行/列」に置く
4    -10%          (auto)
5     -5%          (auto)
6      0%          (auto)
7     +5%          (auto)
8    +10%          (auto)
```

手順:
1. 出力したい結果セル (例: `IRR_cell`) を `C3` にリンク (`=IRR_cell`)。
2. `B4:B8` に変動させたい入力 (例: revenue growth) のシナリオ値を入力。
3. `B3:C8` を選択 → `Data → What-If → Data Table`。
4. **Column input cell** に「実際にモデルが参照している入力セル」(例: `Inputs!Rev_Growth`) を指定。
5. Excel が `B4:B8` の各値を一時的に column input cell に代入し、`C3` の式の結果を `C4:C8` に書き込む。

##### 行入力の場合

ヘッダ行に input 値を並べ、左下に `=Output_cell` を置き、`Row input cell` を指定。

#### 2 変数 Data Table

##### レイアウト

```
        B           C        D        E        F
3      =Output    -10%      -5%      0%       +5%       ← Row 入力
4     -10%       (auto)    (auto)   (auto)   (auto)
5      0%        (auto)    (auto)   (auto)   (auto)
6     +10%       (auto)    (auto)   (auto)   (auto)
                                    ↑ Column 入力
```

- **左上 (`B3`)** に `=Output_cell`。
- **B4:B6** に column 方向の変動値 (例: COGS rate)。
- **C3:F3** に row 方向の変動値 (例: revenue growth)。
- 全範囲 `B3:F6` を選択 → `Data → What-If → Data Table` → Row input と Column input の両方を指定。

#### Data Table の落とし穴

| 落とし穴 | なぜ問題か | 対策 |
|---|---|---|
| **同シート内に置くと再計算が極端に遅い** | Data Table は揮発関数扱い。F9 のたびに全テーブル再計算 | 別シート (`Sensitivity` sheet) に集約 |
| **Output cell との配置を間違う** | 1 変数: 左上の右隣に formula。2 変数: 左上に formula。位置が違うと無効 | 上記レイアウトを厳守 |
| **Input cell が `Sensitivity` シートと別シートでも OK** | (誤解されがち) | 入力セルは `Inputs!X` のような別シート参照可 |
| **計算オプションが Auto except Tables になっている** | Tables だけ手動再計算が必要 | `Formulas → Calculation Options → Automatic` |
| **Result 列を直接編集しても効かない** | Data Table は array formula。個別編集不可 | 全範囲を一度クリアしてやり直す |

#### 推奨表示

- 中央列・中央行を **base case** にし、太字で強調。
- 条件付き書式: 数値の高低で **2 色グラデーション** (例: green-red) を当てる。
- ハードルレート (例: IRR > 25%) を超えたセルだけ太字 + 緑背景。

### 2.2 Tornado Chart の作成手順

Tornado chart = **入力変数を 1 つずつ ±X% 動かしたとき、Output (例: NPV, IRR, EV) がどれだけ振れるか** を縦棒で並べた図。**最も影響度の高い変数** を視覚的に特定する。

#### 作成手順 (手動)

1. **Driver list** を作る: モデルで動かしたい入力 10–20 個 (Revenue growth, Churn, CAC, Gross margin, OpEx growth, Discount rate, Terminal growth, …)。
2. 各 driver について、**Low / Base / High** の 3 シナリオ値を決める (例: ±10%, ±20%)。
3. 各 driver を 1 つだけ Low に振り替えて Output を記録 → `Output_low`。同様に High → `Output_high`。**他の入力は固定**。
4. `Swing = |Output_high − Output_low|` で並び替え (大きい順)。
5. Stacked bar chart (centered): 中央 = Base output, 左 = Output_low との差, 右 = Output_high との差。

##### データ表

| Driver | Low value | High value | Output_low | Output_high | Swing | Sort order |
|---|---|---|---|---|---|---|
| Revenue growth | -10% | +10% | $80M | $140M | $60M | 1 |
| Gross margin | 60% | 75% | $90M | $130M | $40M | 2 |
| Churn | 8% | 3% | $95M | $125M | $30M | 3 |
| CAC | $1,200 | $800 | $100M | $120M | $20M | 4 |
| Discount rate | 12% | 8% | $105M | $115M | $10M | 5 |

#### 自動化のヒント

- `What-If` を手作業で 1 つずつ振るのは非効率。**Driver 列に Scenario toggle** (CHOOSE) を入れ、`= CHOOSE(Toggle, Low, Base, High)` で切り替え可能にし、VBA マクロでループする (大型モデル用)。
- 中規模モデルでは、各 driver につき 1 列分の Data Table を `Sensitivity` sheet に並べ、その中央列 (Base) を全体 base case にすればテーブルだけで完結。

#### 解釈

- **棒の長い順** が影響度ランキング。
- 影響度の小さい変数は **モデル簡素化** や **input 精度の優先度を下げる** 候補。
- **非対称性 (Low と High の swing が左右で異なる)** は非線形性の存在を示唆 (e.g., 借入カベナンツ近傍、税金の loss carry-forward)。

### 2.3 Scenario Manager (Excel 標準機能)

`Data → What-If Analysis → Scenario Manager`。**複数の input セルの値セット** に名前をつけて保存・切替できる。

#### 使い所

- Base / Bull / Bear の 3 シナリオを **正式に保存** したい場合。
- 入力数が 5–10 個程度の中規模モデル。
- **Summary レポート** として `Scenario Summary` を自動生成できる (各シナリオでの output 値の比較表)。

#### 手順

1. `Data → What-If → Scenario Manager → Add`。
2. **Scenario name**: "Base" など。
3. **Changing cells**: 動かす入力セルを Ctrl+click で複数指定 (最大 32 セル)。
4. シナリオごとに値を入力。
5. `Show` で値をシートに反映。`Summary` で比較表を別シートに出力。

#### Scenario Manager の限界

- 32 セルが上限。大規模モデルでは不足。
- **動的な切替がボタン 1 つで** できない (Show を毎回押す必要)。
- バージョン管理されない (誰がいつ Bull を更新したか追跡不可)。
- **CHOOSE / INDEX / SWITCH ベースの toggle pattern (2.4 節) のほうが** スケーラブルで明示的。実務では Scenario Manager より自前 toggle のほうが一般的。

### 2.4 Input toggle pattern (CHOOSE / INDEX / SWITCH)

シナリオ切替の本命。**1 つのトグルセルで全 input が一斉に切り替わる**。

#### Pattern A: CHOOSE (シナリオ数が固定で少数)

```
Inputs!B2  Scenario_ID    1    ← 1=Base, 2=Bull, 3=Bear (Data Validation で list)

       Base  Bull  Bear
Rev_Gr 10%   20%   5%      ← Inputs!C5:E5
COGS%  40%   38%   45%
Churn  5%    3%    8%

Inputs!B5  Active_Rev_Gr  =CHOOSE($B$2, C5, D5, E5)
Inputs!B6  Active_COGS    =CHOOSE($B$2, C6, D6, E6)
Inputs!B7  Active_Churn   =CHOOSE($B$2, C7, D7, E7)
```

**長所**: 直感的。シナリオ数が増えても `CHOOSE($B$2, C5, D5, E5, F5, ...)` で拡張。
**短所**: シナリオ数が 5 を超えると CHOOSE の引数列挙が冗長。

#### Pattern B: INDEX (シナリオ数が多い、シナリオが行/列で構造化)

```
       1=Base 2=Bull 3=Bear 4=Stress
Rev_Gr 10%    20%    5%     -5%
COGS%  40%    38%    45%    50%
Churn  5%     3%     8%     12%

Active_Rev_Gr   =INDEX(C5:F5, $B$2)
Active_COGS     =INDEX(C6:F6, $B$2)
Active_Churn    =INDEX(C7:F7, $B$2)
```

**長所**: シナリオを列追加するだけで拡張可能。
**短所**: Scenario_ID を整数で管理する必要 (Data Validation 推奨)。

##### INDEX/MATCH 化 (シナリオ名で参照)

```
Inputs!B2  Scenario_Name  "Base"   ← Data Validation: Base, Bull, Bear, Stress

Active_Rev_Gr   =INDEX(C5:F5, MATCH($B$2, $C$3:$F$3, 0))
```

これなら Scenario_Name に文字列を入れるだけで切替。Cover sheet で大きく表示すれば、誰が見ても **「いま Bull で計算している」** が一目で分かる。

#### Pattern C: SWITCH (Excel 2019+ / 365)

```
Active_Rev_Gr  =SWITCH($B$2, "Base", 10%, "Bull", 20%, "Bear", 5%, NA())
```

**長所**: 名前ベース。可読性が高い。`NA()` で未定義時に `#N/A` を出してエラー検知。
**短所**: 古い Excel 互換性なし。シナリオ追加時に全式を変更が必要。

#### Toggle と Cover sheet 表示

```
Cover!E5  Active Scenario   =Inputs!B2   "Base"  (大きいフォント、太字、Primary deep #004F49)
```

監査者が **Cover を見ただけで** 現在のシナリオが分かることが重要。PDF を印刷した瞬間「Bull で印刷した」が紛れる事故を防ぐ。

#### Toggle の単一性原則

- **トグルセルはモデル内に 1 つ**。複数のトグル (Sheet1 で Base, Sheet2 で Bull) を許すと整合性が崩壊。
- すべての input は `Active_X = CHOOSE/INDEX(toggle, ...)` の形を経由してから利用。**直接 input セルを参照しない**。

#### Snapshot 保存 (シナリオ結果の保存)

- 各シナリオで重要 output (NPV, IRR, EV, Burn) を Snapshot 表に Paste Special Values で記録する習慣。
- Snapshot 表はバージョン日と共にアーカイブ (`Snapshots!Y2026Q1_Base`, etc.)。

---

## 3. Documentation Conventions

モデルは **6 か月後の自分が読み返して 5 分で理解できる** ことが最低基準。投資家・監査人・新任 CFO がコールドリーディングできるレベルを目指す。

### 3.1 Cover sheet (必須項目)

`Cover` または `00_Cover` という名前で **必ず先頭シート** に配置。タブ色は Primary deep (`#004F49`) など固定色で目立たせる。

#### 必須項目 (12 項目)

| # | 項目 | 例 | 備考 |
|---|---|---|---|
| 1 | **Title** | "Acme SaaS Inc. — 5Y Operating Model" | プロジェクト名 + モデルの目的 |
| 2 | **Company / Entity** | "Acme SaaS Inc. (Delaware C-Corp)" | 法人格まで |
| 3 | **Version** | "v1.4 (2026-05-01)" | 後述 Version log と一致 |
| 4 | **Author** | "Shintaro Hayashi <s@xo-street.com>" | 連絡先必須 |
| 5 | **Last modified** | "2026-05-01 14:32 JST" | 自動更新でもよい (注: 揮発を避けるため `NOW()` は使わず手動更新を推奨) |
| 6 | **Currency unit** | "All figures in JPY million unless stated" | 単位混在を防ぐ |
| 7 | **Period** | "FY2025A → FY2030E (Annual)" | 実績/予測の境界明示 |
| 8 | **Active Scenario** | "Base" (大きく表示) | 2.4 の toggle と紐付け |
| 9 | **Master Check** | "OK" (緑) または "REVIEW" (赤) | 1.7 の集約セル |
| 10 | **Source documents** | "Audited FY2024 financials, FY2025 board pack, ARR snapshot 2026-04-30" | 入力の出所 |
| 11 | **Recipient** | "Series B Lead — Tier 1 VC" | 配布先で粒度・disclaimer が変わる |
| 12 | **Disclaimer** | "Confidential. Forecast figures are management estimates and not assured." | NDA / forward-looking statement |

#### Cover sheet レイアウト例

```
+------------------------------------------------------------------+
|                  ACME SaaS INC.                                  |
|                  5Y Operating Model                              |
|                                                                  |
|  Version:        v1.4                  Last modified: 2026-05-01 |
|  Author:         S. Hayashi            Currency:     JPY million |
|  Period:         FY25A - FY30E         Frequency:    Annual      |
|                                                                  |
|  Active Scenario:  [BASE]              Master Check: [OK]        |
|                                                                  |
|  Recipient:    Series B Lead VC                                  |
|  Source docs:  FY24 audit, FY25 board pack, ARR 2026-04-30       |
|                                                                  |
|  Disclaimer:   Confidential. Estimates not assured.              |
+------------------------------------------------------------------+
```

#### スタイル (Act design)

- 背景 Surface `#ECE9E1`、本文 Ink `#2D332E`、強調 Primary deep `#004F49`。
- 装飾色は 1 か所のみ (Active Scenario と Master Check のステータス)。
- 純黒・ネオン・グラデーションは使わない。

### 3.2 Version log

専用シート `VersionLog` または Cover の下半分に配置。**変更が起きるたびに追記**。

#### 推奨書式

| Version | Date | Author | Change | Files affected | Reviewed by |
|---|---|---|---|---|---|
| v1.0 | 2026-03-01 | S. Hayashi | Initial build | All | - |
| v1.1 | 2026-03-15 | S. Hayashi | Added revolver | CFS, BS, Debt sched | T. Sato |
| v1.2 | 2026-04-02 | S. Hayashi | Updated FY24 actuals from audit | IS, BS, Cover | T. Sato |
| v1.3 | 2026-04-20 | T. Sato | Added Bull/Bear scenarios | Inputs, Outputs | S. Hayashi |
| v1.4 | 2026-05-01 | S. Hayashi | Refined SBC schedule | IS, BS Equity | - |

#### 運用ルール

- **Minor change (typo, format)** = patch。Cover の version は更新しない。Log にも書かない (OS 側 git/Drive の version history で十分)。
- **Logic change** = minor (`v1.3 → v1.4`)。Log に必ず追記。
- **Structural change** (シート追加、入力フォーマット変更) = major (`v1.x → v2.0`)。**Old version をアーカイブして別名保存**。
- ファイル名にもバージョンを刻む: `Acme_Model_v1.4_2026-05-01.xlsx`。

#### Semantic versioning ライク

- `v1.0`: 初版完成。
- `v1.x`: 数値・前提・追加チェックなどの非破壊更新。
- `v2.0`: シート構成や入力体系の破壊的変更。

### 3.3 Assumptions log

主要前提と **その根拠** を一覧化したシート (`Assumptions` または `Notes`)。**「なぜこの数字なのか」** を 6 か月後の自分に伝える。

#### 推奨書式

| # | Category | Assumption | Value | Source / Rationale | Date | Owner |
|---|---|---|---|---|---|---|
| 1 | Revenue | New logo growth Y1 | +60% YoY | Last 4 quarters compounded | 2026-04-15 | Sales lead |
| 2 | Revenue | Gross retention | 92% | LTM cohort analysis | 2026-04-10 | CS lead |
| 3 | Revenue | Net retention | 115% | Top 20 customer ARR expansion | 2026-04-10 | CS lead |
| 4 | Cost | S&M as % rev | 45% Y1 → 30% Y5 | Public SaaS comp median (Bessemer Cloud Index) | 2026-04-12 | CFO |
| 5 | Cost | R&D headcount | +12 FY25 (8 eng, 2 PM, 2 design) | Board-approved hiring plan | 2026-03-25 | Hiring plan |
| 6 | Capital | Series B raise | $25M @ $150M post | LOI from Lead VC | 2026-04-20 | Term sheet |
| 7 | Tax | Effective tax rate | 30% | JP statutory + add-on | 2026-03-01 | CPA memo |
| 8 | Discount | WACC | 15% | Build-up: Rf 1.0% + ERP 6% × β 1.5 + size 4% + specific 1% | 2026-04-01 | CFO |

#### 運用

- **入力セル単位で Assumptions log の番号** を付与 (cell comment で `#3 (NRR 115%)` のように)。
- **Source なしの前提は禁止**。「直感」「うろ覚え」は記録しない。せめて「TBD - need data from Sales」と明記。
- 数値が更新されたら **過去の値も履歴として残す**:

| Date | Value | Note |
|---|---|---|
| 2026-03-01 | 110% | Initial estimate |
| 2026-04-10 | 115% | Updated based on cohort data |

### 3.4 Instructions sheet

`README` または `Instructions` シート。**初見の読者のためのナビゲーション**。

#### 推奨内容

```
1. Purpose
   This model projects Acme SaaS Inc.'s P&L, BS, and CFS
   for FY25E to FY30E, supporting the Series B fundraising.

2. How to use
   - Toggle scenarios at Inputs!B2 (1=Base, 2=Bull, 3=Bear)
   - All blue cells are inputs; do not edit black cells (formulas)
   - Outputs are summarized at Cover!E10:E20

3. Sheet map
   Cover         Project metadata, master check
   Instructions  This sheet
   VersionLog    Change history
   Assumptions   Key assumptions and sources
   Inputs        All driver inputs (one place)
   IS            Income Statement (annual)
   BS            Balance Sheet (annual)
   CFS           Cash Flow Statement (annual)
   Debt          Debt schedule with revolver
   PPE           PP&E and depreciation schedule
   WC            Working capital schedule
   Equity        Equity & SBC schedule
   Outputs       KPI dashboard, NPV, IRR
   Sensitivity   Data tables and tornado
   Snapshots     Saved scenarios

4. Color conventions
   Blue text     Hard-coded input  (#004F49 primary deep)
   Black text    Formula
   Green text    Reference to another sheet
   Red text      Caution / placeholder

5. Calculation settings
   Iterative calculation: ON (Max iter 100, Max change 0.001)
   Required for revolver. Circuit breaker at Inputs!CircuitBreaker.

6. Known limitations
   - Tax NOL carry-forward simplified (no expiration tracking)
   - Equity tranches: Series A and B only; further rounds require manual extension
   - FX assumed flat at FY25 spot
```

### 3.5 Comments の使い方 (cell comment vs notes column)

#### Cell comment (Excel) / Note (Sheets)

- 適しているケース: **特定のセル 1 つに付随する注釈** (e.g., 「この値は税理士確認待ち」「2026-04 board で承認済み」)。
- Excel では `Insert → Comment` (新仕様: スレッド型 = レビュー用) または `Insert → Note` (旧仕様: 単純メモ)。
- Mac/Win, Sheets で表示挙動が違うため、**重要なロジック説明は cell comment に頼らない**。

#### Notes column (隣接列に常時表示)

- 適しているケース: **行ごとの恒久的な説明** (e.g., 数式の意味、参照根拠、注意点)。
- レイアウト: 数式列の右に `Notes` 列を 1 列確保し、A4 印刷時にも見える位置に。

##### 例

```
        B (Y1)    C (Y2)    Notes
Rev     1,000     1,200     Bottoms-up: ARR end Y0 × NRR + new logo (#1, #3)
COGS    400       450       45% gross margin floor (long-term target)
SBC     50        60        Per board-approved option pool (#9)
```

#### 使い分け原則

| 種類 | 用途 | 寿命 |
|---|---|---|
| Cell comment | レビュー時の「ここどうなってる？」 | 一時的、解決後削除 |
| Note column | 数式の恒久的説明 | モデルの寿命と同じ |
| Assumptions log | 前提の根拠と日付 | モデルの寿命と同じ |
| Instructions sheet | 全体ナビ | モデルの寿命と同じ |

#### Anti-pattern (注釈)

- **Cell comment を恒久ドキュメントの場所として使う**: 印刷で消える、検索に弱い、レビューで誤って削除される。Notes 列に格上げすべき。
- **同じ説明を複数箇所に重複記載**: Single source of truth (Assumptions log) に集約し、行内では `(see #3)` のように番号参照。
- **コメントに「TODO」「FIXME」を書いたまま提出**: 提出前にレビューする。Notes 列に `TBD - source needed` のように **意図的なプレースホルダ** として残す場合は赤字で強調。

---

## 4. Anti-patterns

EuSpRIG (European Spreadsheet Risks Interest Group) の蓄積によると、業務スプレッドシートの大半に何らかの数式エラーがあると報告されている。以下は IB / Wall Street Prep / Macabacus / FAST Standard で **共通して禁止** されているパターン。

### 4.1 ハードコード混在 (number と formula を 1 セルに混ぜる)

##### 悪い例

```
B5  =Inputs!B5 * 1.05      ← 5% 成長を直接式に埋め込み
B6  =Inputs!B6 * 1.21      ← Y2 累積。なぜ 21% なのか不明
B7  =Inputs!B7 - 250000    ← 250,000 の意味が不明
```

##### 良い例

```
Inputs!B5  Growth rate Y1   5%       ← 入力 (青)
Inputs!B6  Growth rate Y2   5%
Inputs!B7  Fixed cost adj   250,000  ← 入力 (青)

Calc!B5    =Inputs!B5_prev * (1 + Inputs!Growth_Y1)
Calc!B7    =Inputs!B7_calc - Inputs!Fixed_cost_adj
```

##### なぜ問題か

- **トレースできない**: Sensitivity をかけたいが、入力セルに値がないため Data Table が機能しない。
- **更新ミス**: 1.05 が 10 か所、1.21 が別の 5 か所…という散在は、レートが変わったときの修正漏れを必ず生む。
- **監査拒否**: IB の MD レビューで一発リジェクト。「なぜこの倍率か」の根拠 (Assumptions log) を辿れない。

##### 例外

- **数学的定数** (12 month/year, 365 day/year, 100% conversion など): 式中に書いて構わない。むしろ `=B5/12` のほうが `=B5/Inputs!Months_per_year` より読みやすい。
- 会計的に固定の値。ただし税率は変動するため定数扱いしない。

### 4.2 同一行内に複数の数式パターン

「ある列までは式 A、その先は式 B」を **同じ行内** で混在させる。

##### 悪い例

```
        Y1A      Y2A      Y3E       Y4E       Y5E
Rev    1,000   1,200   =C*1.10   =D*1.10   =E*1.15   ← Y5 だけ +15%
```

##### なぜ問題か

- **横方向のフィル** が効かない。E から F に式をコピーしても F は `=E*1.10` になり、想定の +15% 適用ロジックが消える。
- レビュー時に「なぜ Y5 だけ違うのか」を見落としやすい。
- セル単位で式が違うと、列単位の自動チェック (例: 各列で `Total Asset = L+E`) が壊れる。

##### 良い例

```
        Y1A      Y2A      Y3E       Y4E       Y5E
Growth rate (input) -    -    10%   10%   15%      ← 入力行 (Y1-Y2 は実績で空欄/N/A)
Rev (calc)         1,000  1,200  =B*(1+rate3) =C*(1+rate4) =D*(1+rate5)
```

ロジックは **完全に同一**、変化は入力行に集約。

##### FAST 原則 (one row, one calculation)

FAST Standard の「Each line of calculations should perform one calculation only, and that calculation should be applied consistently across all columns」を遵守。

### 4.3 不可視シート (hidden sheets without index)

`右クリック → Hide` で隠したシートが、Cover や Instructions に **記載されていない**。

##### 悪い例

- 監査者が `Right-click → Unhide` で発見した hidden sheet に **古い数値** や **競合シナリオ** が残っており、Cover の Active Scenario と矛盾。
- **Very Hidden** (`xlSheetVeryHidden`、UI からは Unhide できない VBA 限定) の濫用。

##### なぜ問題か

- **隠した瞬間に「ない」と扱う読者** が多く、レビュー漏れを誘発。
- **意図的に隠した補助計算** と **削除し忘れ** の見分けがつかない。
- 監査では hidden sheet を全て unhide する手順が標準。隠す意味が薄い。

##### 良い例

- Hidden を許す場合: Cover sheet の Sheet map に `[hidden]` ラベル付きで列挙。
  ```
  CalcLookup    [hidden] Helper tables for INDEX/MATCH lookups
  Archive_v1.0  [hidden] Reference snapshot, do not edit
  ```
- 開発者がデバッグ用に隠した one-off シートは、提出前に **削除**。

### 4.4 隠し列の濫用

行の途中で hidden column を使い、画面上は隙間が空かないが Ctrl+→ で飛ぶと急に列番号が飛ぶ。

##### 悪い例

```
A   B   C   [D 隠し]   E   F
                         ↑ 重要計算が D に潜む
```

##### なぜ問題か

- **印刷で消える** (Page setup でも復元しない設定が多い)。
- レビューが目視で済まないため、ミスを見逃す。
- 列削除/挿入のたびに hidden 列がずれて、フォーマットが崩壊。

##### 良い例

- 補助計算は **専用シート (`CalcHelper` など)** に隔離。Cover に [hidden 化していてもよい] と明記。
- 表示したくない場合は、**Group (Outline)** を使う。Group は `+`/`−` ボタンで明示的に折りたたみ表示され、隠れていることが視覚的にわかる。

### 4.5 Named range の濫用

`Inputs!B5` を `WACC_Y1` のような名前で参照すること自体は良い。だが **過剰命名** はモデルを破壊する。

##### 悪い例

- 入力 1 つにつき名前を 1 つ、500 個の named range が登録されている。
- 同一名がスコープ違いで複数 (`Sheet1.Tax`, `Workbook.Tax`) に存在し、参照によって挙動が変わる。
- 範囲が `OFFSET` 関数で動的定義され、開いただけで volatile 計算が走る。

##### なぜ問題か

- **Find & Replace で名前が捕捉されない**: セル参照は動かせるが、named range の定義が古いまま残る。
- **Broken named ranges** (元のセルが削除されると `#REF!` が定義に残存)。Name Manager を開いても気づきにくい。
- **重複名・スコープ違い** で、同じ式でも異なる結果が出る。
- IB の慣習では **named range を使わず、直接セル参照** が主流 (Wall Street Prep, Macabacus)。トレースしやすさを優先。

##### 良い例 (named range を使う場合)

- 使用は **「workbook 全体に適用される定数」** に限定: `TaxRate_Statutory`, `WACC`, `TerminalGrowthRate` など、せいぜい 5–10 個。
- すべて **workbook scope**。sheet scope は混乱の元。
- Name Manager で一覧化し、Cover sheet の Sheet map に `Named ranges (5)` として記載。
- **#REF! を含む named range はゼロ** (Inquire add-in で自動チェック可能)。

### 4.6 OFFSET / INDIRECT (volatile)

##### Volatile functions とは

`OFFSET`, `INDIRECT`, `NOW`, `TODAY`, `RAND`, `RANDBETWEEN`, `INFO`, `CELL` (一部引数) は、**シートのどこかが変わるたびに再計算される**。100 個の OFFSET で表が組まれていると、1 セル変更で 100 個全部が再計算され、大型モデルで数十秒のラグが発生。

##### 悪い例

```
B5  =OFFSET(Inputs!$A$1, 0, MATCH(B$3, Inputs!$1:$1, 0)-1)
```

期間ヘッダで列を動的選択する常套手段だが、揮発性で遅い。

##### なぜ問題か

- **遅さ**: Volatile が連鎖すると O(n) の式追加で再計算回数が爆発的に増える。
- **トレースが効かない**: `INDIRECT("Sheet1!"&A1)` のような式は、Trace Precedents で precedent が表示されない。
- **検索が効かない**: `INDIRECT` が文字列でセル名を組み立てるため、Find & Replace で捕捉できない。

##### 良い例

```
B5  =INDEX(Inputs!$2:$2, MATCH(B$3, Inputs!$1:$1, 0))
```

`INDEX/MATCH` は非揮発。`OFFSET` でできることはほぼ全て `INDEX` で書ける。

`INDIRECT` の代替: 動的なシート切替が必要なら、**1 つのシートに集約 + シナリオ列で切り替え** にリファクタする。`INDIRECT` を生かしたままにすると、保守性で必ず破綻する。

### 4.7 巨大 IF nest

##### 悪い例

```
=IF(A1="Base", IF(B1>0, IF(C1<100, IF(D1="Yes", X*1.1, X*1.05),
    IF(D1="Yes", X*1.0, X*0.95)), IF(C1<100, X*0.9, X*0.85)),
    IF(A1="Bull", X*1.2, IF(A1="Bear", X*0.8, X)))
```

ネスト深さ 5–7。何が起きているか **数日後の自分でも分からない**。

##### なぜ問題か

- 可読性が低く、レビューで見逃される。
- 1 か所の typo で全体が壊れ、原因特定が難しい。
- Excel の IF ネスト上限 (Excel 2007+ で 64) 近くまで使うのは設計の失敗。

##### 良い例

###### Option A: ヘルパー列に分解

```
Helper!A  Scenario_factor  =CHOOSE(MATCH(A1,{"Base","Bull","Bear"},0), 1.0, 1.2, 0.8)
Helper!B  Volume_factor    =IF(B1>0, 1, 0)
Helper!C  Range_factor     =IF(C1<100, 1.1, 0.9)
Result    = X * Helper!A * Helper!B * Helper!C
```

###### Option B: SWITCH (Excel 2019+)

```
=SWITCH(A1, "Base", X*1.0, "Bull", X*1.2, "Bear", X*0.8, X)
```

###### Option C: Lookup table

```
ScenarioTable:
   Name   Factor
   Base   1.0
   Bull   1.2
   Bear   0.8

=X * VLOOKUP(A1, ScenarioTable, 2, FALSE)
```

##### 一般原則

- **IF のネストは最大 3 層**。それ以上は `CHOOSE`, `INDEX/MATCH`, `SWITCH`, `IFS` (Excel 2019+) または別行に分解。
- 同じ条件分岐が複数行で繰り返されるなら、**条件判定を 1 セルに集約** (`IsBullCase = (Scenario="Bull")`) して再利用。

### 4.8 Merged cells で数式

セル結合 (`Format → Merge cells`) されたセルに数式を入れる。

##### 悪い例

```
B5:D5 (merged)  =SUM(B10:D20)
```

##### なぜ問題か

- **`COPY` / `PASTE` が壊れる**: merged cell をコピーした先で結合解除、または範囲外参照になる。
- **行/列の挿入で破綻**: 結合範囲の中に行を挿入すると参照が崩れる。
- **VBA / 配列数式 / Data Table が動かない**: 多くの機能が merged cell をサポートしない。
- **AutoFilter / Sort が壊れる**: 結合された行をソートすると並び順がぐちゃぐちゃに。

##### 良い例

- **Center Across Selection** (`Format Cells → Alignment → Horizontal: Center Across Selection`) で見た目の中央揃えのみ実現。セルは結合されない。
- ヘッダの装飾は **Cell style (font, color, border)** で。Merge は使わない。

##### 例外

- **印刷用にタイトル行** を 1 行だけ merge する: 数式が入らないラベルなら許容。ただし、その上下に他の merge が連鎖しないこと。

### 4.9 空白行による「視覚的グルーピング」

##### 悪い例

```
Row 10  Revenue          1,000
Row 11  COGS               400
Row 12  Gross Profit       600
Row 13  (空白)
Row 14  OpEx               200
Row 15  Operating Income   400
Row 16  (空白)
Row 17  Total Revenue (集計)  =SUM(B10:B15)   ← 空白行を含めた SUM
```

##### なぜ問題か

- **行挿入で式が壊れる**: 誰かが Row 14 と 15 の間に行を挿入すると、空白だった Row 13 が新規行に置き換わり、SUM の意味が変わる。
- **Pivot Table / Filter / Sort が誤動作**: 空白行で「データ範囲」が切れたと判断され、後続のデータが拾われない。
- **Sheets の構造化参照** (Excel Table) が機能しない。

##### 良い例

- **行高さ** を使って視覚的余白を作る (`Row height: 24` をセクション末に)。
- **罫線 (Cell border)** で境界線を引く。
- **背景色 (Subtle fill)** でセクションを区切る。
- セクション見出しは **太字 + Surface 色** (`#ECE9E1` の少し濃い変種) で表現。

### 4.10 旧バージョンのコピペ残存

##### 悪い例

- `Sheet1`, `Sheet1 (2)`, `Sheet1_OLD`, `Sheet1_v0.5` といったコピーが残存。
- 数式が `='Sheet1 (2)'!B5` のように、古いシートを参照したまま。
- `Inputs_OLD` シートに前回の input が残っており、Find & Replace で書き換えたつもりの値が一部 OLD のまま。

##### なぜ問題か

- **どれが本物か分からない**。レビュアー、共同編集者、6 か月後の自分が必ず混乱する。
- 古いシートが新シートの数式に参照されていた場合、**意図せず古い数値で計算** している可能性。
- ファイルサイズの肥大化、計算速度の劣化。

##### 良い例

- **Archive ファイル** を `_archive/` フォルダに別保存し、現行ファイルから古いシートを **削除**。
- どうしてもファイル内に残したいときは:
  - シート名を `ARCHIVE_v1.0_DO_NOT_EDIT` のように明示。
  - タブ色を **#C04A4A (Danger)** にして区別。
  - **数式参照がないこと** を `Find: 'ARCHIVE` で確認。
  - Cover の Sheet map に `[archive]` と明記。
- Git/Drive のバージョン履歴に頼り、ファイル内では基本「最新だけ」を保つのが原則。

---

## 5. Spreadsheet Auditing

モデルを **受け取る側** (PE/VC/FP&A レビュアー) として、または **提出する側** が自分でかける最終チェックの手順。

### 5.1 F2 で数式トレース

最も基本かつ強力な操作。

- **F2** (Mac: Ctrl+U): セルを編集モードにし、数式が表示される。**すべての precedent セルに色付き枠線** が同時表示される。
- **Esc** で抜ける (Enter で確定すると意図せず変更される事故あり、Esc 推奨)。
- **F5 → Special → Formulas / Constants / Errors**: シート全体で「数式だけ」「ハードコード値だけ」「エラー値だけ」を選択 → 範囲を一覧確認。
- **Ctrl + ` (バッククォート)**: 数式表示モードに切替 (全セル一斉表示)。レイアウト崩れに注意。

### 5.2 Trace Precedents / Dependents

`Formulas → Trace Precedents` (Mac も同じ)。

- **Trace Precedents**: 選択セルが **どのセルから** 値を引いているか矢印表示。複数階層を辿るには複数回クリック。
- **Trace Dependents**: 選択セルが **どのセルに** 影響を及ぼしているか矢印表示。「この入力を変えるとどこが動くか」を瞬時に把握。
- **Remove Arrows**: 矢印クリア (`Formulas → Remove Arrows`)。
- 黒矢印 = 同シート、点線 + シートアイコン = 別シート参照。

##### 監査ワークフロー

1. Output (例: NPV) のセルを選択 → Trace Precedents を 5–10 階層辿る。
2. 「いま追っている数値が、最終的にどの input から来ているか」をマップ化。
3. 入力に到達したら Trace Dependents で逆向きに辿り、計算経路に **想定外のジャンプ** がないか確認。

### 5.3 Formula Auditing toolbar

`Formulas → Formula Auditing` グループの全機能:

| 機能 | 用途 |
|---|---|
| Trace Precedents | 上記 |
| Trace Dependents | 上記 |
| Remove Arrows | クリア |
| Show Formulas | 数式表示モード切替 (Ctrl + `) |
| Error Checking | `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`, `#NULL!` を順次表示 |
| Evaluate Formula | 複雑な数式を **1 ステップずつ評価** (デバッグの主役) |
| Watch Window | 別シートのセルを常時表示 (5.4 節) |

##### Evaluate Formula

`Formulas → Evaluate Formula` で、巨大な式の一部を選択して F9 で部分評価できる (Edit モード中)。

- セル編集モード (F2) で式の一部 (例: `IF(B5>0, X, Y)` の `B5>0`) を選択 → F9 → その部分式の評価結果が表示される。
- **Esc で必ず抜ける** (Enter すると評価結果がハードコードされる)。

### 5.4 Watch Window

`Formulas → Watch Window` で開く小ウィンドウ。指定セルを **どのシートにいても常時監視** できる。

##### 用途

- Master Check の状態を常に確認しながら他のシートを編集。
- Output (NPV, IRR) の動きを見ながら入力を変更 → 即座に impact が見える。
- **大規模モデルで再計算後の値を即確認** (画面遷移不要)。

##### 設定

1. `Formulas → Watch Window → Add Watch`。
2. 監視したいセルを選択 → OK。
3. ウィンドウに **Workbook / Sheet / Name / Cell / Value / Formula** が一覧表示される。

### 5.5 Inquire add-in (Excel)

Excel Pro Plus / Microsoft 365 で使える組み込みアドイン。`File → Options → Add-ins → COM Add-ins → Inquire` で有効化。

##### 主な機能

| 機能 | 効能 |
|---|---|
| **Workbook Analysis** | シート数、数式数、hidden objects、links、named ranges、warnings をレポート出力 |
| **Workbook Relationship Diagram** | ブック間の参照関係を図示 |
| **Worksheet Relationship Diagram** | シート間の参照関係を図示 |
| **Cell Relationship Diagram** | 1 セルの precedent/dependent ツリーを図示 |
| **Compare Files** | 2 つのブックを差分比較 (5.6 節) |
| **Clean Excess Cell Formatting** | 未使用セルの format を一括削除 (ファイル軽量化) |
| **Workbook Passwords** | パスワード保護されたシートの一覧 |

##### Inquire の Workbook Analysis 報告で必ずチェック

- **Volatile functions** の数 → 4.6 で削減対象。
- **External links** → 意図しない他ファイル参照を検出。
- **Errors** (#REF!, #VALUE! など) → 全て解消すべき。
- **Hidden sheets / Very hidden sheets** → 4.3 で全て index 化。
- **Named ranges with errors** → 4.5 で削除。
- **Circular references** → 1.6 で意図したものか確認。

### 5.6 Spreadsheet Compare / 外部監査ツール

##### Spreadsheet Compare (Microsoft 製)

- Office Pro Plus 同梱、独立アプリ (`Start → Office Tools → Spreadsheet Compare`)。
- 2 つのブックを比較し、**入力値変更 / 数式変更 / 書式変更 / シート構造変更** を色分けレポート。
- バージョン間の差分監査に必須 (例: v1.3 と v1.4 の違いを 1 分で把握)。

##### 外部監査ツール (有償)

| ツール | 提供 | 特徴 |
|---|---|---|
| **Spreadsheet Auditor** (Operis OAK 等) | Operis | IB/PE 業界標準。複雑な model のロジック追跡に強い |
| **Macabacus** | Macabacus LLC | IB アナリスト向け。fast formula 監査 + formatting (alt-shortcut で高速作業) |
| **PerfectXL** | Infotron | 自動チェック (volatile, hardcode mix 等) のレポート |
| **XLAudit / XLTest** | 各社 | リスク評価 + テスト自動化 |

##### 自分でやる「セルフ監査」のチェックポイント

1. **`Find: =` で全数式を確認** → 怪しい固定値混入を発見。
2. **`Ctrl+End`** で「最終セル」に飛ぶ → 想定外の遠い位置に残骸セル (空でも書式が残っているとファイル肥大化) を発見。
3. **`Find & Select → Constants`** で全ハードコード一覧 → 入力でないハードコードを洗い出す。
4. **`Find & Select → Data Validation`** → 入力検証セルの位置確認。
5. **`Find: !`** (シート参照) → 外部リンクや旧シート参照を検出。
6. **`Find: [` (角括弧)** → 別ファイル参照 (絶対パス) を検出。配布前に解消。
7. **行/列のグループ折りたたみを全展開** (Outline → Show All) で隠れ計算を可視化。

---

## 6. IB Quality Checklist

最終提出前に走らせる **60+ 項目** のチェックリスト。各カテゴリごとにペアレビュー (作成者 + 第三者) を推奨。

### A. 構造 (Structure) — 10 項目

| # | 項目 | OK基準 |
|---|---|---|
| A1 | Cover sheet が先頭にある | Yes |
| A2 | Instructions sheet がある | Yes |
| A3 | Inputs / Calc / Outputs が分離されている | 物理的にシート単位、または明示ブロック単位で分離 |
| A4 | シートの順序が読み手の動線に沿う | Cover → Instructions → VersionLog → Assumptions → Inputs → Calc → Outputs → Sensitivity |
| A5 | シート名が一貫した命名規則 | snake_case または PascalCase 統一、特殊文字なし |
| A6 | タブ色がカテゴリで意味づけされている | 例: Cover=Primary deep, Inputs=Navy, Output=Accent |
| A7 | Period (期間) ヘッダが全シートで一致 | 同じ列番号で同じ期 (例: 列 D = FY25E) |
| A8 | Actuals と Forecast の境界が視覚的に明示 | 列ヘッダの色変え、罫線、ラベル "A/E" |
| A9 | 単位が全シートで統一 | "JPY million" 等。混在なし |
| A10 | フォントが Geist Sans / Noto Sans JP 系で統一 | 1 ブック内 1–2 フォント以内 |

### B. 書式 (Formatting) — 10 項目

| # | 項目 | OK基準 |
|---|---|---|
| B1 | Input セルは青文字 (`#004F49` 等) | 全 input |
| B2 | Formula セルは黒文字 (Ink `#2D332E`) | 全 formula |
| B3 | 別シート参照は緑文字 | (任意。FAST 推奨) |
| B4 | 数値の符号方針が統一 | 1.5 節 sign check 通過 |
| B5 | Number format が用途別に統一 | 通貨 / %, decimal places 一貫 |
| B6 | Conditional formatting がチェックセル等の限定箇所のみ | 過剰使用なし |
| B7 | Merged cell が数式範囲で使われていない | 4.8 通過 |
| B8 | 空白行による grouping をしていない | 4.9 通過 |
| B9 | Print area が設定されている | A4 / Letter で意図通り収まる |
| B10 | グリッド線、枠線、背景が控えめ | Act design に整合。装飾色は 1 か所/画面 |

### C. 数式 (Formulas) — 12 項目

| # | 項目 | OK基準 |
|---|---|---|
| C1 | ハードコードと formula を 1 セルで混ぜていない | 4.1 通過 |
| C2 | 1 行 = 1 数式パターン | 4.2 通過 |
| C3 | IF nest が最大 3 層以下 | 4.7 通過 |
| C4 | OFFSET / INDIRECT を使っていない | 4.6 通過 (またはコメント付きで限定使用) |
| C5 | Volatile 関数の総数が低い | Inquire 報告で確認 |
| C6 | Named range は 5–10 個以内、すべて workbook scope | 4.5 通過 |
| C7 | Named range にエラーがない | Name Manager で `#REF!` ゼロ |
| C8 | 循環参照は意図的なもののみ | Revolver 等。Circuit breaker あり |
| C9 | 数値の丸めが意図的 | `ROUND` 使用箇所が文書化されている |
| C10 | `IFERROR` でエラーを隠蔽していない | エラーは表面化させる方針 (`IFERROR` は外部 API 等の限定箇所のみ) |
| C11 | `VLOOKUP` よりも `INDEX/MATCH` または `XLOOKUP` を使用 | 範囲挿入で壊れない構造 |
| C12 | 配列数式が意図的に使われている | CSE 配列の混入なし、または 365 動的配列に統一 |

### D. 参照 (References) — 8 項目

| # | 項目 | OK基準 |
|---|---|---|
| D1 | 外部ファイル参照 (`[file.xlsx]`) なし | Find: `[` でゼロ |
| D2 | 旧シート (`Sheet1 (2)`) への参照なし | 4.10 通過 |
| D3 | 絶対参照 / 相対参照が用途で正しく使い分け | ヘッダ参照は `$`、フィル方向は相対 |
| D4 | フィル方向に整合する | 行/列方向のコピーで意図通り展開 |
| D5 | Cross-sheet 参照が双方向ループしていない | 1.6 以外で循環なし |
| D6 | 三表間の参照が 1.3 で定義したラインのみ | NI: IS→CFS, RE: IS→BS, Cash: CFS→BS |
| D7 | 期間参照が統一 (前期 = 同行の左隣セル) | 例外あれば cell comment で明示 |
| D8 | 名前付き定数 (Tax, WACC) のセル位置がモデル先頭 (Inputs) に集約 | 散在なし |

### E. 監査 (Audit & Checks) — 12 項目

| # | 項目 | OK基準 |
|---|---|---|
| E1 | BS check (Assets = L+E) 全期間 OK | 1.1 通過 |
| E2 | CF check (CFS End = BS Cash) 全期間 OK | 1.2 通過 |
| E3 | NI tie (IS NI = CFS top) 全期間 OK | 1.3 通過 |
| E4 | RE roll forward 整合 全期間 OK | 1.3 通過 |
| E5 | Debt roll forward 整合 全期間 OK | beg+draw−repay |
| E6 | PP&E roll forward 整合 全期間 OK | beg+CapEx−Dep−disposal |
| E7 | Working Capital roll forward 整合 全期間 OK | AR/AP/Inventory roll |
| E8 | Equity roll forward 整合 全期間 OK | beg+Issue+SBC−Repurchase |
| E9 | Cross-foot (横合計 = 縦合計) OK | 1.4 通過 |
| E10 | Sign check 全 row OK | 1.5 通過 |
| E11 | エラーセル (`#REF!`, `#DIV/0!`, ...) ゼロ | `SUMPRODUCT(--ISERROR(...))=0` |
| E12 | Master Check が緑 / "OK" | 1.7 通過 |

### F. ドキュメンテーション (Documentation) — 12 項目

| # | 項目 | OK基準 |
|---|---|---|
| F1 | Cover sheet 12 必須項目すべて記載 | 3.1 通過 |
| F2 | Last modified が更新されている | 提出当日 |
| F3 | Version が VersionLog の最新と一致 | 3.2 通過 |
| F4 | Author に連絡先がある | email |
| F5 | Currency unit が明示 | "JPY million" 等 |
| F6 | Active Scenario が Cover に表示 | "Base" 等 |
| F7 | Source documents が列挙 | 監査済み FS、board pack など |
| F8 | Disclaimer がある | confidential / forward-looking |
| F9 | Assumptions log が全主要前提を網羅 | 3.3 通過 |
| F10 | 各前提に Source / Rationale 記載 | "TBD" は赤字で残し意図的に明示 |
| F11 | Notes 列が必要な行に記載 | 数式の意味を新人が読んで理解可能 |
| F12 | Instructions sheet がカラー規則・計算設定・既知の限界を記載 | 3.4 通過 |

### G. 操作性 (Operability) — 6 項目

| # | 項目 | OK基準 |
|---|---|---|
| G1 | Scenario toggle が 1 つのみ、Cover に大きく表示 | 2.4 通過 |
| G2 | Sensitivity sheet に Data Table と Tornado がある | 2.1, 2.2 通過 |
| G3 | Snapshot 表に主要 output が保存されている | 各シナリオ NPV, IRR, EV |
| G4 | 計算オプション (iterative on/off) が Instructions に記載 | 1.6 通過 |
| G5 | Circuit breaker (revolver 用) が設置 | 1.6 通過 |
| G6 | Print preview で Cover, Outputs, Sensitivity が A4 1 ページに収まる | 配布資料として完成 |

### 合計: 70 項目

#### 採点運用

- **Phase 1 (作成中)**: 各章ごとに章末の Master Check が緑であれば次工程。
- **Phase 2 (Self review)**: チェックリスト全 70 項目を自分でレビュー。NG は黄色マーク。
- **Phase 3 (Peer review)**: 第三者 (チームメンバ、CFO、外部 CPA) が同チェックリストを白紙から再レビュー。
- **Phase 4 (Final delivery)**: 70/70 OK で配布。Cover の Master Check は緑。バージョン確定。

#### NG が残ったまま提出するときの開示

- どうしても期限内に解消できない項目は、**Cover sheet の Known Limitations 欄に明記**。
  - 例: "G6 NG — Sensitivity sheet currently spans 2 pages; will fix in v1.5."
- 隠さない。提出後の信頼で大きな差がつく。

---

## 関連ドキュメント

- `01_modeling_principles.md` — モデリング全体の設計原則 (フロント工程)
- `06_three_statement.md` — 三表モデル構築の手順
- `02_saas_metrics.md` — SaaS 固有 KPI の定義と算式
- `05_valuation_wacc.md` — 評価手法と WACC build-up
- `08_investment_thesis.md` — 投資判断とアウトプット連携

## 参考文献

- **Wall Street Prep** (https://www.wallstreetprep.com) — IB modeling standards
- **Macabacus** (https://www.macabacus.com) — Best practices and shortcuts
- **EuSpRIG** (https://eusprig.org) — European Spreadsheet Risks Interest Group。スプレッドシートエラー研究の蓄積
- **FAST Standard** (https://www.fast-standard.org) — Flexible / Appropriate / Structured / Transparent モデル設計原則
- **SSRB** — Spreadsheet Standards Review Board

