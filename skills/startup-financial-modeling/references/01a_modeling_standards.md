---
name: modeling_standards
description: 財務モデリングの規格・フォーマット規範の正本。命名規則 / row 構造 / driver 分離 / 期間軸 / IPO readiness 観点の formatting。SKILL.md dispatch から「IPO readiness」「三表突合」「sheet 構造」を聞かれた際に読まれる。
type: reference
priority: P1
related: [_terminology, 00_design_guidelines, 01b_integrity_and_anti_patterns, 06_three_statement, 14_ipo_readiness]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 用語・色・閾値は [`_terminology.md`](_terminology.md) を canonical とする (sheet name は `_terminology §3`)
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) の各 entry から「IPO readiness check」「modeling standards」が必要なときに参照される
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check を必ず実行
- **関連 reference**: `00_design_guidelines` (色・形式) / `01b_integrity_and_anti_patterns` (検証・anti-pattern) / `06_three_statement` (三表) / `14_ipo_readiness` (IPO 観点)

# 財務モデリング標準とフォーマット規範 (Modeling Standards & Formatting Conventions)

> スコープ: 本ドキュメントは「規格・フォーマット」のみを扱う。
> エラーチェック / sensitivity / anti-pattern は別エージェント (`01b_*`, `01c_*`) を参照。
>
> 対象: スタートアップ向け 3 表モデル / オペレーティングモデル / 投資家配布モデル。
> 想定読者: モデルを作る側 (アナリスト、CFO チーム、創業者) と、レビューする側 (投資家、監査)。

---

## 目次

- [0. 規範の階層 (Hierarchy of Standards)](#0-規範の階層-hierarchy-of-standards)
- [1. FAST Standard (公式仕様)](#1-fast-standard-公式仕様)
  - [1.1 概要と発行元](#11-概要と発行元)
  - [1.2 F = Flexible](#12-f--flexible)
  - [1.3 A = Appropriate](#13-a--appropriate)
  - [1.4 S = Structured](#14-s--structured)
  - [1.5 T = Transparent](#15-t--transparent)
  - [1.6 FAST 適用チェックリスト](#16-fast-適用チェックリスト)
- [2. ICAEW Twenty Principles of Good Spreadsheet Practice](#2-icaew-twenty-principles-of-good-spreadsheet-practice)
- [3. SMART Standard (Spreadsheet Modeling Audit Review Toolkit)](#3-smart-standard-spreadsheet-modeling-audit-review-toolkit)
- [4. IB の色・フォント・書式規範](#4-ib-の色フォント書式規範)
  - [4.1 Color coding (色分け)](#41-color-coding-色分け)
  - [4.2 Font](#42-font)
  - [4.3 Number formatting](#43-number-formatting)
  - [4.4 Sign convention (符号規約)](#44-sign-convention-符号規約)
  - [4.5 Italic / Bold / Underline 使い分け](#45-italic--bold--underline-使い分け)
  - [4.6 行高・列幅・borders](#46-行高列幅borders)
- [5. Sheet 命名・ordering](#5-sheet-命名ordering)
- [6. Freeze panes / Print area / Page setup](#6-freeze-panes--print-area--page-setup)
- [7. 数式 discipline](#7-数式-discipline)
- [8. 学派の違い (House Styles)](#8-学派の違い-house-styles)
- [9. 統合チェックリスト](#9-統合チェックリスト)
- [10. 参考文献](#10-参考文献)

---

## 0. 規範の階層 (Hierarchy of Standards)

実務で参照される「モデリング標準」は複数あり、対象範囲が一部重なる。整理すると:

| 規格 | 主管 | カバー範囲 | 対象モデル | 強制力 |
|---|---|---|---|---|
| **FAST Standard** | F1F (旧 FAST Standard Organisation) → 2020 以降 FAST Modelling Alliance | レイアウト + 数式 + 命名 + ガバナンス | プロジェクトファイナンス、コーポレートモデル全般 | 任意 (採用は任意契約) |
| **ICAEW Twenty Principles** | ICAEW IT Faculty | ライフサイクル全般 (設計〜廃棄) の原則 | あらゆる業務スプレッドシート | 任意 (英国会計士界では事実上必須) |
| **SMART** | Operis (英) ほか | 監査観点のチェックリスト | 既存モデルのレビュー | 任意 |
| **IB House Style** | 各バンク (GS / MS / JPM / Lazard 等) | フォーマット中心 | M&A / LBO / valuation | バンク内では強制 |
| **Macabacus / Wall Street Prep / Training The Street** | 教育ベンダー | 上記の事実上の翻訳・教育版 | 教育目的 | 任意 |

**rationale**:
- FAST は「数式設計まで踏み込んだ」唯一公開された標準。複雑モデルでは FAST を骨格に据えるのが堅い。
- ICAEW 20 原則は「原則」レベルで、FAST より上位。FAST を採用するか否かに関わらず守るべき汎用ガバナンス。
- SMART は監査用。完成モデルを第三者レビューする際の評価軸。
- IB ハウススタイルはレイアウト/見栄え中心。上記 3 つと衝突する場合は数式 discipline (FAST) を優先し、見栄えのみ IB 流に寄せる、というハイブリッド運用が一般的。

---

## 1. FAST Standard (公式仕様)

### 1.1 概要と発行元

**FAST** は財務モデルの構築標準。"Flexible, Appropriate, Structured, Transparent" の頭字語。

| 項目 | 内容 |
|---|---|
| 発行元 (現在) | **FAST Modelling Alliance** (FMA, Australia / 旧 F1F の流れ) |
| 旧発行元 | FAST Standard Organisation (CIC, UK, ~2018) |
| 主要起草者 | Kenny Whitelaw-Jones, Andrew Berkley, Morten Siersted ほか |
| 入手 | `fast-standard.org` (旧) / `fastalliance.org` (現) からフリーダウンロード |
| ライセンス | Creative Commons (BY-SA 系)。営利でも自由配布可、改変は同条件で開示 |
| バージョン | B2 系列が長く使われたあと、FMA が改訂継続中 (B2.02、B2.03 系) |

**rationale**:
複数アナリストが入れ替わってもメンテ可能なモデル、レビュアが短時間で監査できるモデルを再現可能に作るための「業界共通文法」を提供する。M&A、PE、PF (project finance) で広く採用。

### 1.2 F = Flexible

**定義**: モデルは、想定される改修・拡張・期間延長・シナリオ追加に対し、構造を壊さずに対応できること。

#### 1.2.1 行 (rules) と原則

| ルール | 実装 | rationale |
|---|---|---|
| **時間軸は単一の master timeline で全シートに供給** | `Time` シートの 1 行 (period number, period start, period end, flag rows) を、全シートが横方向に直接参照 | 期間延長 / 周期変更時に 1 か所で済む |
| **期間長は変数化** | `Periods per year` を入力にして DCF / 償却 / interest accrual を全部スケール | 月次→四半期→年次の切替を 1 セルで |
| **シナリオは選択スイッチで切替** | `CHOOSE(scenario_id, base, upside, downside)` 行を入力ブロック側で受ける | アウトプット側を書き換えずに切替可能 |
| **ハードコード禁止 (数式内)** | 数式内の定数は `=Sales*1.21` ではなく `=Sales*(1+VAT_rate)` | 税率変更等が 1 か所で済む |
| **行追加に強い構造** | input block は「定数」「成長率」「ベース」「結果」を上下に積む決まった順序 | 後で driver 行を増やしても下位ブロックが壊れない |

#### 1.2.2 NG 例 / OK 例

NG (timeline 直書き):
```
B5: =SUM('P&L'!C10:N10)        ← 12 か月の前提が固定
```

OK (timeline 経由):
```
B5: =SUMIFS('P&L'!10:10, Time!10:10, ">="&FY_start, Time!10:10, "<="&FY_end)
```

NG (シナリオ直書き):
```
B7: =100 * 1.10                ← 10% 成長を直書き
```

OK (シナリオ駆動):
```
B7: =B6 * (1 + Growth_selected)
Growth_selected: =CHOOSE(Scen_ID, Growth_Base, Growth_Up, Growth_Down)
```

### 1.3 A = Appropriate

**定義**: モデルの精度・粒度・複雑性を、意思決定の必要性に「ちょうど」一致させる。
過剰精度 (false precision) も過小精度も両方避ける。

#### 1.3.1 原則

1. **目的を文書化** — Cover sheet に "purpose" を 1 行で書き、その目的に必要な範囲だけ作る。
2. **粒度の決定基準** — 粒度を上げて意思決定が変わるなら詳細化、変わらないなら集約。
3. **過剰モデリングの抑制** — 「Excel に載せたから美しく見える」を排除。スプレッドシートの仮定が誤差より大きいなら粒度を上げる意味はない。
4. **重要性閾値** — モデル合計の 1% 未満の項目はラインまとめて 1 行に集約。
5. **single source of truth** — 同じ前提を 2 か所に書かない。すべて参照。

#### 1.3.2 例: SaaS スタートアップでの粒度判断

| 項目 | 判断 | 理由 |
|---|---|---|
| 顧客数 (cohort 別) | 月次 cohort | LTV/CAC のドライバ。意思決定影響大 |
| AWS 費用 | 単一行 (% of revenue) | 5 期目以降は当たらない予測。集約で十分 |
| 旅費交通費 | 単一行 | 重要性閾値以下 |
| ストックオプション SBC | 個別 grant 単位 | 希薄化計算と税効果のため必要 |
| 為替レート | 1 通貨ペアにつき 1 行 (年次) | 月次変動を入れても予測精度は上がらない |

### 1.4 S = Structured

**定義**: モデルは予測可能な構造を持ち、行・列・シートの位置から内容が推測できる。

#### 1.4.1 縦横ルール

- **計算は左から右** (時間が右へ進む)
- **依存は上から下** (上の行を下の行が参照、その逆は不可)
- **シート内の column アンカー固定** — 例えば Column F を「期初」、列 G から先を時間軸、として全シートで揃える
- **同じ性質の行は同じ位置** (例: input block の "growth rate" は常に block の 2 行目)

#### 1.4.2 column 構成 (FAST 標準的レイアウト)

| Col | 内容 |
|---|---|
| A | 章番号 / セクションフラグ (任意) |
| B | row label (主) |
| C | sub-label / detail |
| D | unit ($, %, x, days, count) |
| E | 注記 / source 参照 |
| F | (任意) opening balance 列 / 合計列 / aggregation |
| G〜 | 時間軸 (period 1, period 2, ...) |

> **rationale**: F 列を「時間外の値 (前期末 / 合計 / 年計)」、G 列以降を「時間軸内」と二分することで、SUMIFS や時間ループ計算の式を統一できる。F 列は学派により hardcode 解禁・絶対参照アンカー・OB (opening balance) 専用などバリエーションあり。

#### 1.4.3 sheet 構成 (FAST 推奨パターン)

```
Cover  →  Control  →  Time  →  Inputs (assumptions)  →
Workings (calc)  →  Outputs (financials)  →  Checks  →  Glossary
```

- 1 sheet 1 機能の原則 (機能を混ぜない)
- 計算ブロックは原則 1 ブロック 1 アウトプット (block = label / inputs / calc / output)
- 「input と calc を混ぜない」が最重要 (FAST B5 ルール)

#### 1.4.4 block (FAST のもっとも特徴的な単位)

FAST における **block** は計算の最小単位で、以下の 5 行構造が基本:

```
[1] Block heading        (太字、underline、行種別 = "header")
[2] (空行)
[3] Input row(s)         (青文字、unit 列に単位)
[4] Working row(s)       (黒文字、計算過程)
[5] Output row           (太字 underline、block の最終結果。次の block で参照される)
[6] (空行)
```

block と block の間は必ず 1 行空ける。block の output 行は名前付きセル化 or 視覚的に強調する。

### 1.5 T = Transparent

**定義**: モデルを初見の第三者が、説明なしで構造・前提・計算を理解できる。

#### 1.5.1 数式 transparency 原則

1. **short formulas** — 1 cell に 1 計算ステップ。`SUM(IF(IF...))` のネストは禁止
2. **single formula per row** — 同じ行内で複数の異なる式が混在しない
3. **avoid hidden complexity** — マクロ・volatile 関数 (OFFSET, INDIRECT, INDEX 動的) を可能な限り避ける
4. **avoid mega-formulas** — 1 cell 80 文字超の式は分解
5. **explicit is better than implicit** — `IFERROR(.., 0)` ではなく、エラー条件を明示し flag check で扱う

#### 1.5.2 NG → OK 変換例

NG (mega-formula):
```
=IF(AND(Date>=Start,Date<=End),IF(Type="Fixed",Amount,Amount*Multiplier),IF(Date>End,0,IF(Type="Fixed",0,Pre_amount)))
```

OK (FAST 流に分解):
```
[Row 10] In_period_flag       =IF(AND(Date>=Start, Date<=End), 1, 0)
[Row 11] Pre_period_flag      =IF(Date<Start, 1, 0)
[Row 12] Post_period_flag     =IF(Date>End, 1, 0)
[Row 13] Amount_in_period     =IF(Type="Fixed", Amount, Amount*Multiplier) * In_period_flag
[Row 14] Amount_pre           =IF(Type="Fixed", 0, Pre_amount) * Pre_period_flag
[Row 15] Total                =Row13 + Row14
```

> **rationale**: 各行の意味と中間値が画面で見える。バグも特定行で隔離される。

#### 1.5.3 命名・ラベル

- **labels are unique** — 同じ label を 2 行で使わない (`Revenue` が 3 行あるなら `Revenue - Product`, `Revenue - Service`, `Revenue - Total`)
- **units in their own column** — `$m`, `%`, `x`, `days`, `units`, `FTE` を Col D に明示
- **named ranges 控えめに** — FAST B2 系では「named range は使うが過剰使用しない」立場。input switch / global 定数のみ命名し、time series セルには使わない
- **switch values の意味を脇に表示** — `Scenario_ID = 2` の右に `(2 = Upside)` を出す

### 1.6 FAST 適用チェックリスト

| カテゴリ | チェック項目 | Pass 条件 |
|---|---|---|
| Flexible | timeline は 1 シートに集約 | Time シート以外で日付の hardcode なし |
| Flexible | scenario switch | CHOOSE/INDEX で 1 セル切替可能 |
| Flexible | 数式に定数 hardcode なし | constants は input block 経由 |
| Appropriate | cover に purpose 記載 | "what / for whom / decision" の 3 点 |
| Appropriate | 重要性閾値 | 1% 未満項目は集約 |
| Structured | F 列 = 時間外、G〜 = 時間軸 | 全 sheet で統一 |
| Structured | input と calc が別 sheet | mixing なし |
| Structured | 1 block = label + input + calc + output | 空行で区切り |
| Transparent | 1 row = 1 formula | row 内で複数式の混在なし |
| Transparent | volatile 関数 | OFFSET / INDIRECT 不使用 (代替 INDEX/MATCH) |
| Transparent | mega-formula | 80 文字超 / IF nest > 3 を flag |
| Transparent | named range | switch / global 定数のみ |

---

## 2. ICAEW Twenty Principles of Good Spreadsheet Practice

ICAEW (Institute of Chartered Accountants in England and Wales) IT Faculty が 2014 年に発行 (`Twenty principles for good spreadsheet practice`)、以後改訂継続。**4 つのカテゴリ × 20 原則** で、スプレッドシートのライフサイクル全体をカバーする。

| カテゴリ | 原則 # |
|---|---|
| A. Spreadsheet の役割 (lifecycle) | 1〜5 |
| B. 設計 (design) | 6〜11 |
| C. 構築 (build) | 12〜17 |
| D. 運用 / レビュー (live, archive, audit) | 18〜20 |

### A. Lifecycle

#### 原則 1. Determine what role spreadsheets play in your business, and plan accordingly.

| 項目 | 内容 |
|---|---|
| 実装 | スプレッドシートを「使い捨て分析」「中核プロセス」「監査対象」に分類し、各々で要求水準を変える |
| rationale | 中核プロセスは外部システム化を検討、使い捨ては過剰投資を避ける。Excel は万能ではない |
| スタートアップ運用例 | 「投資家配布モデル」と「経営会議用ローリング予算」を分け、後者だけ TCO 視点で運用 |

#### 原則 2. Adopt a standard for your organisation and stick to it.

| 項目 | 内容 |
|---|---|
| 実装 | FAST / SMART / 自社規程のいずれかを選び、社内テンプレで強制 |
| rationale | 同じ会社で 3 種類の流儀が混在すると、レビュー・引継・監査の全コストが激増 |
| 注意 | 標準は wiki に書き、新人入社時に 30 分で読める量に圧縮 |

#### 原則 3. Ensure that everyone involved in the creation or use of spreadsheets has an appropriate level of knowledge and competence.

| 項目 | 内容 |
|---|---|
| 実装 | Excel スキルマトリクス、認定 (FMI、Wall Street Prep など) |
| rationale | リスクは関係者の最低スキルに律速される |

#### 原則 4. Work collaboratively, share ownership, peer review.

| 項目 | 内容 |
|---|---|
| 実装 | git / SharePoint で版管理、変更ログを別 sheet に残す |
| rationale | 単独保守は属人化と監査不能を招く |

#### 原則 5. Before starting, satisfy yourself that a spreadsheet is the appropriate tool for the job.

| 項目 | 内容 |
|---|---|
| 実装 | 行数 > 50k、同時編集 > 3 名、トランザクション処理が中心、なら DB / BI ツールを検討 |
| rationale | Excel の構造的限界 (行制限、同時編集、性能、テスト容易性) を超える要件で無理して使わない |

### B. Design

#### 原則 6. Identify the audience.

| 項目 | 内容 |
|---|---|
| 実装 | Cover に "audience" 行を設置、想定読者の財務リテラシ水準と粒度を明示 |
| rationale | 投資家配布モデルと社内 ops モデルでは粒度が違う |

#### 原則 7. Include an "About" or "Welcome" sheet to document the spreadsheet.

必須項目:
- Purpose
- Author / version / date
- Inputs と outputs の所在
- Assumption の主要 list
- Change log
- Caveats / known limitations

#### 原則 8. Design for longevity.

| 項目 | 内容 |
|---|---|
| 実装 | 期間延長、行追加、シナリオ追加に耐える構造 (= FAST の Flexible) |
| rationale | 多くのモデルは "1 回きり" の想定で作られ、3 か月後に流用される |

#### 原則 9. Focus on the required outputs.

「必要なアウトプットから逆算」して計算と input を決める。中間計算が冗長なまま残らないようにする。

#### 原則 10. Separate and clearly identify inputs, workings and outputs.

| ゾーン | 配置 | 表記 |
|---|---|---|
| Inputs | 専用 sheet または block 上部 | 青文字、淡い背景色、外枠 |
| Workings | 専用 sheet または block 中央 | 黒文字、背景なし |
| Outputs | 専用 sheet または block 下部 | 黒文字、太字 underline、必要なら強調背景 |

> **rationale**: レビュアが「ここを変えたら何が動くか」を 5 秒で判別可能にする。3 ゾーンの分離は ICAEW・FAST・SMART いずれにも共通。

#### 原則 11. Be consistent in structure.

| 項目 | 内容 |
|---|---|
| 実装 | sheet 間で column アンカー一致、row label の用語統一、計算ロジック統一 |
| rationale | 規則性があれば、目視レビューで「何かおかしい」が見つかる |

### C. Build

#### 原則 12. Be consistent in formulas used.

行内・行間・シート間で同じロジックは同じ式で表現する。`=A*B` と `=B*A` を混在させない。

#### 原則 13. Keep formulas short and simple.

| 実装 | 1 cell 80 文字以内、IF nest ≤ 3、変数は中間行に切り出し |
| rationale | 短い式 + 多い行 > 長い式 + 少ない行 (デバッグ可能性) |

#### 原則 14. Never embed in a formula anything that might change or need changing.

定数 (税率、為替、割引率) は input セル化。`=Sales * 0.21` は禁止、`=Sales * VAT_rate` にする。

#### 原則 15. Perform a calculation once and refer back to that calculation.

`=Revenue * Margin` を別シートで再計算しない。1 か所で計算→他は参照。

#### 原則 16. Refer to source data only once, then refer back to that single point.

外部データ (rate, market data) は import sheet に 1 回だけ取り込み、他は参照。

#### 原則 17. Avoid using offset cells, particularly with hard-coded references.

| 項目 | 内容 |
|---|---|
| 実装 | `OFFSET`, `INDIRECT`, 動的 `INDEX` 多用は避ける |
| 代替 | 固定範囲、テーブル (Excel Table)、INDEX/MATCH (静的) |
| rationale | volatile 関数は再計算負荷が大きく、参照先の挙動が見えづらい (transparency 違反) |

### D. Live / archive / audit

#### 原則 18. Have a system of backup and version control.

git (Excel-friendly: `git lfs` + `xltrail` の検討) または SharePoint バージョン管理。バージョン名は `MODEL_v1.3.4_2026-05-01_KW.xlsx` のように `<name>_<semver>_<date>_<author>` で統一。

#### 原則 19. Rigorously test the workbook.

| 項目 | 内容 |
|---|---|
| 実装 | 既知の (toy) input でアウトプットを手計算と突合、極端値で破綻チェック、checks シートで balance / sum / sign 自動検査 |
| rationale | テストなき公開は監査不能 |

#### 原則 20. Build in checks, controls and alerts.

| 項目 | 内容 |
|---|---|
| 実装 | 専用 `Checks` シートに集約。BS balance, IS-CF tie, period count, scenario flag valid, etc. 1 行 1 check で `OK` / `ERR` を表示し、cover でも色付き表示 |
| rationale | レビュアと next user に "壊れた" を通知する |

---

## 3. SMART Standard (Spreadsheet Modeling Audit Review Toolkit)

> 注意: SMART は出版社により呼称が揺れる。Operis は同社の `Operis Analysis Kit` (OAK) と組み合わせた監査メソッドとして "SMART" を使用。BPM (Business Performance Management) Council 系の Spreadsheet Standards Review Board (SSRB) が公開したものは `Best Practice Spreadsheet Modeling Standards`。本章では「監査観点」として両者の共通項を整理。

### 3.1 監査の 5 つの問い

監査者がモデルに対して問う基本軸:

| # | 問い | チェック対象 |
|---|---|---|
| 1 | 数式は意図したとおりに計算しているか (`Mathematical correctness`) | 全 cell |
| 2 | 同じ前提から同じ結果が出るか (`Deterministic`) | volatile / random / iter |
| 3 | 想定外の input でも安全に振る舞うか (`Robust`) | edge case, error trap |
| 4 | レビュアが構造を理解できるか (`Auditable`) | layout, naming, color |
| 5 | 公開前提と実際が一致しているか (`Consistent with documentation`) | cover, glossary |

### 3.2 SMART チェック項目 (実務 70 項目相当を圧縮)

#### A. 構造系

- [ ] sheet 名が意味を表す (`Sheet1` 等が残っていない)
- [ ] sheet ordering が flow と一致 (cover → input → calc → output → checks)
- [ ] hidden sheet がない、または明示文書化
- [ ] tab color が分類規則 (assumption / output / check) に準拠
- [ ] freeze panes が全 sheet で一貫
- [ ] gridline OFF / 罫線で代替

#### B. Input 系

- [ ] input は青文字 + 専用 sheet (or block)
- [ ] hardcoded value が calc 内にない (formula audit で `=数値*数値` ゼロ件)
- [ ] data validation が必要 input にかかっている (範囲制限、list)
- [ ] units 列が全 input で埋まっている
- [ ] source 列で出典が辿れる

#### C. Formula 系

- [ ] 1 row 1 formula (row 内で式が変化しない、`F2` で確認)
- [ ] IF nest が ≤ 3 (4 段以上は CHOOSE / IFS / lookup に書き換え)
- [ ] 80 文字超 formula のリスト = 0 (or 文書化された例外のみ)
- [ ] volatile 関数 (`OFFSET`, `INDIRECT`, `NOW`, `TODAY`, `RAND`, `RANDBETWEEN`) 使用箇所が監査済
- [ ] 循環参照ゼロ (iter 必須箇所は明示 ON、それ以外は OFF)
- [ ] external link なし (or import sheet 経由のみ)
- [ ] R1C1 と A1 の混在なし
- [ ] array formula / dynamic array 使用箇所の挙動確認

#### D. Output / 整合性

- [ ] BS 平衡 (`Total Assets = Total L&E`) が全期間で 0
- [ ] CF 期末現預金 = BS 現預金
- [ ] PL 純利益 = 利益剰余金変動 - 配当
- [ ] sub-total = SUM(items) が全 sub-total で成立 (FAST flag check)
- [ ] sign convention が統一されている (cost が常に正 or 常に負、混在なし)

#### E. Documentation / governance

- [ ] cover sheet に purpose / version / author / date / scope
- [ ] change log
- [ ] glossary
- [ ] check sheet で現在状態が PASS / FAIL 一目瞭然
- [ ] file 名 = `<name>_v<semver>_<YYYYMMDD>_<initials>.xlsx`

### 3.3 監査ツール

| ツール | 提供 | 用途 |
|---|---|---|
| Operis Analysis Kit (OAK) | Operis | formula consistency / map / audit trail |
| Spreadsheet Inquire (Excel built-in) | Microsoft | workbook analyze, cell relationship |
| Spreadsheet Compare (Excel built-in) | Microsoft | バージョン差分 |
| Macabacus | Macabacus | format / check / audit (IB 寄り) |
| F1F Modeller | F1F | FAST 準拠チェック |
| ClusterSeven / Mirage | risk control | enterprise spreadsheet risk monitoring |
| PerfectXL | PerfectXL | risk audit, formula complexity scoring |

> **rationale**: 人間レビューは漏れる。formula consistency や circular ref のような機械的検査はツールで自動化し、人間は意味論的な validation に集中する。

---

## 4. IB の色・フォント・書式規範

### 4.1 Color coding (色分け)

IB (investment banking) で世代を超えて生き残った色分けルール。Macabacus / Wall Street Prep / Training The Street がほぼ同一規則を教えている。

| 色 | RGB | HEX | Excel theme | 用途 | 例 |
|---|---|---|---|---|---|
| **青** | (0, 0, 255) | `#0000FF` | Standard Blue | **ハードコード input** (定数、手入力数値) | revenue 開始値、tax rate、growth rate |
| **黒** | (0, 0, 0) | `#000000` | Black | **同シート内の数式** | `=B5*B6` |
| **緑** | (0, 128, 0) | `#008000` | Green | **同 workbook 内のシート間リンク** | `=Assumptions!B5` |
| **赤** | (255, 0, 0) | `#FF0000` | Red | **外部 workbook へのリンク** | `=[Other.xlsx]Sheet1!B5` |
| 紫 (任意) | (128, 0, 128) | `#800080` | Purple | named range / 関数値 (FAST 派) | `=VAT_rate` |
| 灰 (任意) | (128, 128, 128) | `#808080` | Gray | コメント / メモ / 非表示計算の補助行 | "see note" |
| オレンジ (任意) | (255, 102, 0) | `#FF6600` | Orange | 一時的なオーバーライド (`scenario lock`) | scenario flag |

#### 使用境界 (どの色がどこまで)

| 状況 | 色 |
|---|---|
| `=42` (数値直書き) | 青 |
| `="Acme Inc"` (文字列直書き) | 青 |
| `=B5+B6` (同シート参照) | 黒 |
| `=Inputs!B5` (シート間) | 緑 |
| `=Inputs!B5 + Inputs!B6` (シート間 + 算術) | 緑 (シート間リンクが含まれているため) |
| `=Inputs!B5 + 0.05` (シート間 + ハードコード混在) | NG → ハードコード `0.05` を input に切り出し、緑に統一 |
| `=[Other.xlsx]Sheet!B5` | 赤 |
| `=VAT_rate` (named range) | 黒 (Macabacus 系) または紫 (FAST B2 派) |

> **rationale**:
> - 青のハードコードを目で追えば「これを変えると何が起きるか」がすぐ分かる。
> - 緑を見れば「他シートを開かないと辿れない」を即認識できる。
> - 赤は `#REF!` 化リスクが高いので、レビュアがファイル受領時に必ず確認すべき場所として警告。
> - 数式内に複数色種別が混在する場合は、最も「重い」(外部 > シート間 > ハードコード) リンクの色に揃える、というのが Macabacus のデフォルト。

#### 適用ツール

| ショートカット | 動作 |
|---|---|
| Macabacus `Ctrl + Alt + 1` | 数式内容を解析して自動着色 |
| 手動 | 範囲選択 → フォント色 |
| ホーム → 数値の右下「セルのスタイル」 | "Input" "Calculation" "Linked Cell" "Output" の組込スタイルを使う代替案もあるが、IB 流ではフォント色の方が支配的 |

### 4.2 Font

#### IB ハウススタイル (典型)

| 用途 | font | size | weight | color |
|---|---|---|---|---|
| body (data) | Arial | 10 pt | regular | per color rule |
| section header | Arial | 11 pt | bold | black |
| sheet title | Arial | 14 pt | bold | black |
| year header | Arial | 10 pt | bold + italic | black (or per rule) |
| total row | Arial | 10 pt | bold | black |
| sub-total row | Arial | 10 pt | regular + top border | black |
| footnote | Arial | 8 pt | italic | gray |

#### Arial vs Calibri

| 項目 | Arial 10 | Calibri 11 |
|---|---|---|
| 標準 | IB 旧来 (Office 2003 以前のデフォルト) | Office 2007 以降のデフォルト |
| 印刷時の密度 | 高い (1 page により多く載る) | やや低い |
| 数字の判読性 | 高い (タビュラ的) | 高い (ヒンタが効く) |
| Excel new file default | 過去はあった | 現在 (Calibri 11) |
| LBO / M&A 銀行内モデル | Arial 10 が圧倒的多数 | 少数派 |
| 企業内 FP&A | 半々 | 半々 |
| FAST 推奨 | 規定なし (sans-serif 推奨) | 規定なし |

> **rationale**: Arial 10 を選ぶ実務上の理由は「縦に行をたくさん載せられる + 過去資料との一貫性」。Calibri 11 は新規プロジェクトで違和感を生まないが、PDF 化したとき微妙に文字数が減る。**選ぶことより、選んだものを workbook 全体で一貫させる方がはるかに重要**。

#### 数字フォント選定の細部

- 通貨記号 `$`, `¥`, `€` の前のスペース有無は number format で揃える
- 全角ロケール (日本) の場合、英数字部分は半角に強制 (`@` 表示書式は使わない)
- 中国語 / 日本語の混在モデルでは、英数字 = Arial、和文 = `MS Pゴシック` or `Yu Gothic` を `フォント` 設定で別指定

### 4.3 Number formatting

#### 基本書式 (IB 標準)

| 種別 | format string | 表示例 (input 1234.5) | 表示例 (input -1234.5) | 表示例 (input 0) |
|---|---|---|---|---|
| 通貨 (1 桁千区切) | `#,##0;(#,##0);-` | `1,235` | `(1,235)` | `-` |
| 通貨 (小数 1 桁) | `#,##0.0;(#,##0.0);-` | `1,234.5` | `(1,234.5)` | `-` |
| 通貨 (小数 2 桁) | `#,##0.00;(#,##0.00);-` | `1,234.50` | `(1,234.50)` | `-` |
| 百分率 (1 桁) | `0.0%;(0.0%);-` | `123,450.0%` ※ | `(123,450.0%)` | `-` |
| 倍率 | `0.0"x"` | `1234.5x` | `-1234.5x` | `0.0x` |
| 倍率 (括弧負号) | `0.0"x";(0.0"x");-` | `1234.5x` | `(1234.5x)` | `-` |
| 日付 (年月) | `mmm-yy` | `May-26` | n/a | n/a |
| 日付 (会計四半期) | `\Q0 yy` | `Q2 26` | n/a | n/a |
| 日付 (会計年度) | `"FY"yy` | `FY26` | n/a | n/a |
| count | `#,##0;(#,##0);-` | `1,235` | `(1,235)` | `-` |
| bps | `0" bps"` | `1234 bps` | `-1234 bps` | `0 bps` |
| dollars in millions (suffix) | `#,##0.0,,"M";(#,##0.0,,"M");-` | (input 1,234,500,000 → `1,234.5M`) | | |
| dollars in thousands (suffix) | `#,##0.0,"K";(#,##0.0,"K");-` | | | |

※ 百分率は input 自体を 0.123 (= 12.3%) とすること。本表の例は「数値 1234.5 を百分率 format に当てたとき」。実務では input は 0.123 で `0.0%;(0.0%);-` で表示。

#### units row (単位行) と format の関係

- 各 block の input section の最上段に **units row** を配置 (col D の "unit" 列にユニット略号、行ヘッダ近くに `($m)` `(%)` `(x)` 等)
- 同 units row 配下の row は同じ number format を使う
- units row が異なる場合 (例えば "metric" と "%" が混在) は section を分ける

#### 千 / 百万 / 十億 単位 (scaling)

| 表示単位 | format | 注意 |
|---|---|---|
| そのまま | `#,##0` | input scale = display scale |
| 千 | `#,##0,` (末尾カンマ 1 つ) | input は 1,234,567 のまま、表示 1,235 |
| 百万 | `#,##0,,` (末尾カンマ 2 つ) | input 1,234,500,000 → 1,235 |
| 十億 | `#,##0,,,` (末尾カンマ 3 つ) | input 1,234,500,000,000 → 1,235 |
| 千 + suffix | `#,##0,"K"` | 1,234,567 → 1,235K |
| 百万 + suffix | `#,##0.0,,"M"` | 1,234,500,000 → 1,234.5M |

> **rationale**: 末尾カンマを使った scaling は、計算は raw 数で行いつつ表示だけスケールするため、丸め誤差を発生させない。input 側で `/1000` するのは禁止 (誤差と再利用性の問題)。

#### スタートアップの金額単位選択

| ARR 規模 | 推奨 display 単位 |
|---|---|
| ARR < $1M | 1 (raw, 千の位カンマ) |
| ARR $1M - $100M | $K (千) |
| ARR $100M - $10B | $M (百万) |
| ARR > $10B | $B (十億) |

**規則**: モデル内で 1 種類に統一、cover 行に `($ in thousands except per share data)` のようなラベル必須。

### 4.4 Sign convention (符号規約)

#### 学派比較

| 学派 | cost / expense の符号 | revenue の符号 | 例 |
|---|---|---|---|
| **正符号派 (positive numbers)** | + (正) | + (正) | OpEx = 100 と表示、PL は `Revenue - OpEx = NI` で式側が引き算 |
| **負符号派 (signed numbers)** | - (負) | + (正) | OpEx = -100 と表示、PL は `=SUM(Revenue:OpEx)` で集計 |
| **混合派 (FAST 流)** | 機能別: cash flow は in (+) / out (-)、PL は all positive | + | FAST B2 では section ごとに統一 |

| 学派 | 採用例 | pros | cons |
|---|---|---|---|
| 正符号派 | M&A バンク (GS / JPM 等)、Macabacus デフォルト | 紙の決算書と同じ見た目、株主向け readable | 集計時に +/- を式側で書き分け、ミス余地あり |
| 負符号派 | PE / LBO、Operis、FAST 一部 | `=SUM(...)` で何も考えず合算可、CF と整合的 | 紙のレポートと印象が逆 |
| 混合派 | FAST 標準 | section 内で一貫、レビューしやすい | section 跨ぎで mental model 切替が必要 |

#### スタートアップ実務の推奨

- **PL は正符号派** (経営陣・投資家向けに紙の決算書イメージで見せる)
- **CF は in/out で符号を持たせる** (営業 CF +、投資 CF -、FCF = 営業 + 投資 (- が引かれる))
- **schedule は負符号派** (depreciation, amortization, capex などは calc 上 negative にして集計を簡単に)
- **section に units row + sign hint** (`($m, costs as +ve)` などをラベルに明示)

#### 一貫性 check

```
[Checks sheet]
Sign_consistency_OpEx     = IF(MIN(OpEx_range)<0, "MIXED", "OK")
Sign_consistency_Revenue  = IF(MIN(Revenue_range)<0, "MIXED", "OK")
```

> **rationale**: モデル内で sign が混在すると、レビュアが各 block で +/- を解読し直すコストが累積する。section ごとに 1 つの規約 + cover で宣言、を守ればよい。

### 4.5 Italic / Bold / Underline 使い分け

| 装飾 | 用途 | 適用箇所 |
|---|---|---|
| **Bold** | 強調 / 結果 | section header, total row, output row, year header |
| _Italic_ | 区分 / 単位 / 引用 | year header (実績 vs 予想区分)、units `($m)`、footnote、参照 source |
| Underline | 集計線 | sub-total の上線 (top border 1px が一般的)、total row の上下二重線 |
| Bold + Italic | 強い区分 | scenario header、case name |
| Strikethrough | 廃止 | 旧仮定を残す場合の hashout (deletion ではなく見え消し) |

#### typical pattern

```
[Year]                  [italic, bold]   FY25  FY26  FY27  FY28  FY29
                                          A     A     E     E     E      <- Actual / Estimate
[Revenue]               [regular]         100   120   144   173   207
[COGS]                  [regular]        (40)  (48)  (58)  (69)  (83)
[Gross Profit]          [bold + top]      60    72    86   104   124
[OpEx]                  [regular]        (30)  (35)  (42)  (51)  (61)
[EBITDA]                [bold + top]      30    37    44    53    63
```

> **rationale**:
> - input 行は太字にしない (太字は「結果」のサイン)
> - year header は italic で「これは時間軸ヘッダ」と認識させる
> - total row は bold + top single border、grand total は bold + top single + bottom double border

### 4.6 行高・列幅・borders

| 項目 | 推奨 | rationale |
|---|---|---|
| 行高 | 14.4pt (12pt の 1.2 倍) または 15pt | Arial 10 で 1.2 倍が読みやすい |
| 標準列幅 (時間軸列) | 10〜12 | `(1,234.5)` が ぴったり収まる |
| label 列 (B) | 30〜40 | 一般的な日本語 / 英文 label が省略なく入る |
| unit 列 (D) | 6〜8 | `$m`, `%`, `x` が入る最小幅 |
| gridline | OFF | 見栄え |
| border | 必要最小: total 行の上線、grand total の上下、表外周 | 過剰罫線は読みにくい |
| section 間 | 空行 1 行 | 視覚的に区切る |
| 列幅統一 | 時間軸列は全 sheet で同じ幅 | コピー&ペーストで体裁が崩れない |

#### borders のパターン

```
              Top    Bottom
Sub-total:    single    -
Total:        single    single
Grand total:  single    double
Block header: double    -        (任意、太字下線で代替も可)
```

---

## 4. IB の色・フォント・書式規範

> _本章は次のコミットで追記_

---

## 5. Sheet 命名・ordering

### 5.1 標準順序 (FAST + IB ハイブリッド)

スタートアップ向け推奨順序 (左→右):

| # | sheet | prefix | 内容 | tab color |
|---|---|---|---|---|
| 0 | Cover | `00_` | purpose / version / author / change log / disclaimer | 黒 |
| 1 | Control | `01_` | scenario switch、global flags、unit toggle | 紺 (Navy) |
| 2 | Time | `02_` | period number / start / end / FY / Q / month flags | 紺 |
| 3 | Assumptions | `03_` | 価格、コスト原単位、税率、為替、人件費、growth rate などすべての input | 青 |
| 4 | Drivers | `04_` | 顧客数 cohort、headcount、capex schedule、stock comp grant、convertible terms | 青 |
| 5 | Revenue Build | `05_` | 売上を Driver から build | 灰 |
| 6 | OpEx Build | `06_` | OpEx を Driver から build | 灰 |
| 7 | Working Capital | `07_` | A/R, A/P, Inventory, Deferred Rev | 灰 |
| 8 | PP&E / Capex | `08_` | capex schedule, depreciation waterfall | 灰 |
| 9 | Debt / Equity | `09_` | borrowings, repayment, SAFE / convertible, equity rounds | 灰 |
| 10 | Tax | `10_` | NOL, current tax, deferred tax | 灰 |
| 11 | PL | `11_` | 損益計算書 (output) | 緑 |
| 12 | BS | `12_` | 貸借対照表 (output) | 緑 |
| 13 | CF | `13_` | キャッシュフロー (output) | 緑 |
| 14 | KPI / Cap Table | `14_` | ARR, MRR, churn, LTV/CAC, fully-diluted shares, runway | 緑 |
| 15 | Valuation | `15_` | DCF / multiples / cap table waterfall | 緑 |
| 16 | Scenario / Sensitivity | `16_` | data table, tornado, scenario summary | 緑 |
| 17 | Charts | `17_` | output 用 charts | 緑 |
| 18 | Checks | `98_` | model integrity checks | 黄 (warning 用赤) |
| 19 | Glossary | `99_` | 用語、略号、source | 灰 |

### 5.2 命名規則

| ルール | 例 OK | 例 NG |
|---|---|---|
| 数字 prefix で順序固定 | `03_Assumptions` | `Assumptions` (順序が崩れる) |
| 単語間は `_` 1 つ | `05_Revenue_Build` | `05 Revenue Build`, `05-revenue-build` |
| 全角文字 / 絵文字なし | `04_IS` | `11_損益計算書`, `📊PL` |
| ASCII 31 文字以内 (Excel 制限) | `15_Valuation_DCF` | (長すぎ) |
| 予約名・記号 (`History`, `'`, `[]`, `*`, `?`, `:`, `\`, `/`) 不使用 | | |

> **rationale**: ファイルシステム / VBA / 外部ツール (PerfectXL 等) との互換性、git diff のしやすさ、ASCII で何も壊れない、を優先。

### 5.3 Tab color のルール

| 色 | 用途 |
|---|---|
| **Primary deep `#004F49`** | Cover (Act ブランド色、`_terminology.md` §2 canonical) |
| **紺 (Navy)** | Control / Time (system 系) |
| **青 (Blue)** | Assumptions / Drivers (input 系) |
| **灰 (Gray)** | Workings / Build (中間計算) |
| **緑 (Green)** | Outputs (PL / BS / CF / KPI / Valuation) |
| **黄 (Yellow)** | Checks (注意・警告) |
| **赤** | エラーが現在ある checks (運用中の状態色、平常時は黄) |

> **rationale**: tab color を見れば「ここは入力 / ここは出力 / ここはチェック」が瞬時に判別。色覚特性配慮として、色 + prefix 数字の二重符号化で意味を伝える。

### 5.4 hidden sheet / very hidden sheet

| 状態 | 用途 |
|---|---|
| visible | 通常運用 |
| hidden | 補助計算・debug sheet。読者にも切替可能 |
| very hidden | 開発者のみ。VBA 経由で表示。本番モデルでは原則使わない |

ICAEW / SMART は「hidden は明示文書化、very hidden は原則禁止」が立場。

### 5.5 テンプレート例 (cover sheet 構造)

```
[A1]    [Project name / Model name]                    (24pt bold)
[A3]    Purpose:        <one sentence>
[A4]    Audience:       <intended reader>
[A5]    Decision:       <what decision this informs>
[A7]    Author:         <name>
[A8]    Version:        v1.3.4
[A9]    Date:           2026-05-01
[A10]   Currency:       USD ($ in thousands)
[A11]   Time scale:     Monthly, FY Apr-Mar
[A12]   Scenario:       Base (cf. Control sheet)

[A14]   Change Log
[A15]   v1.3.4  2026-05-01  KW   Add SAFE round 2 schedule
[A16]   v1.3.3  2026-04-12  KW   Fix tax NOL carryforward bug
...

[A20]   Caveats / Known Limitations
[A21]   - FX assumed flat from FY27
[A22]   - SBC accounting follows IFRS 2, not US GAAP
...

[A30]   Checks Summary  (linked from 12_SanityChecks)
[A31]   BS balance:     OK
[A32]   CF tie:         OK
[A33]   Sign convention: OK
```

---

## 6. Freeze panes / Print area / Page setup

### 6.1 Freeze panes

#### 標準: `View → Freeze Panes → Freeze (selected cell の左上交差点)`

| sheet 種別 | freeze 位置 | rationale |
|---|---|---|
| Time / Assumptions / Drivers (input 系) | Cell `G6` (label 列 + header 行を固定) | 横スクロールでも label が見える、縦スクロールでも year header が見える |
| Workings / Build | Cell `G6` | 同上 |
| PL / BS / CF (output) | Cell `G6` | 同上 |
| Cover / Glossary | freeze なし | 画面に収まる前提 |
| Checks | Cell `G3` | header 1 行のみ固定 |

> **規則**: freeze は全 sheet で同じ列位置 (G) に揃える。これは §1.4.2 の「F 列までは時間外」「G 列以降は時間軸」と整合。

### 6.2 Print area

| 項目 | 推奨 |
|---|---|
| Print area | 各 sheet で `Page Layout → Print Area → Set Print Area` を明示設定 |
| Page orientation | Landscape (時間軸が長い) |
| Paper size | A4 または Letter (組織の規定に従う) |
| Scaling | `Fit All Columns on One Page` (横方向は 1 ページに圧縮) |
| Margins | Narrow (上下 1.91cm、左右 0.64cm) |

### 6.3 Page setup の標準

| 設定 | 推奨値 | rationale |
|---|---|---|
| Header (left) | `&[File]` | ファイル名印字 |
| Header (center) | `&[Sheet name]` | シート名印字 |
| Header (right) | `&[Date] / &[Time]` | 印刷日時 |
| Footer (left) | `Confidential` または案件名 | 機密区分の明示 |
| Footer (center) | `Page &[Page] of &[Pages]` | ページ番号 |
| Footer (right) | author initials, version | 出所追跡 |
| Print titles - Rows to repeat at top | `$1:$5` (sheet header 行) | 縦に長い表でも header 維持 |
| Print titles - Columns to repeat at left | `$A:$F` (label 列) | 横に長い表でも label 維持 |
| Gridlines (print) | OFF | |
| Black and white | OFF (ただし紺/緑が判読可能か確認) | |
| Print quality | 600dpi | |
| Comments / notes | At end of sheet | コメントを最終ページにまとめる |

#### Excel の便利 Tips

- `Page Break Preview` で改ページ位置を視認、不自然な位置に来たら手動調整
- `Custom Views` を使って「投資家向け印刷版」「フル詳細版」「monitoring 版」を保存
- PDF 出力時は `Quality: Standard` ではなく `Quality: High` を選択 (フォントぼけ防止)

---

## 7. 数式 discipline

### 7.1 計算方向のルール

| ルール | 内容 |
|---|---|
| **左→右** | 時間軸は列方向、左 (古) → 右 (新) |
| **上→下** | 依存方向は行方向、上 (前提) → 下 (結果) |
| 逆参照禁止 | 下行が上行を参照する。上行が下行を参照しない |
| シート間も同方向 | input シート (左) → calc シート (中) → output シート (右) |

> **rationale**: 計算グラフが DAG (有向非巡回) になる。循環参照リスクが構造的に減る。レビュアの目線移動が予測可能。

### 7.2 single formula per row

各行内で式は同一 (時間軸方向に同じパターンを繰り返す):

```
[Row 5]  Revenue   =B5    [G5: hardcode/link]   =H5*(1+growth)   =I5*(1+growth)   ...
                                                  ↑ G6 以降は同じパターン
```

NG パターン:
```
G10 = =F10*1.10
H10 = =G10+5            ← 違うロジック
I10 = =H10*1.15         ← また違うロジック
```

OK パターン:
```
[Row 9]  Growth_rate    10%   10%   15%   15%   ...    <- input 行
[Row 10] Revenue        100  =F10*(1+G9)  =G10*(1+H9)  =H10*(1+I9)  ...
                              ↑ 全列同一ロジック
```

> **rationale**: 1 行に 1 ロジック。式が変わるなら別行にする。F2 で式を見ても列を移動して同じ式が並んでいることを期待でき、機械的検査が容易。

### 7.3 no hardcodes inside formulas

#### 検出ルール

| パターン | 判定 | 直し方 |
|---|---|---|
| `=B5*0.21` | NG | tax rate を input に切り出し |
| `=B5*1.10` | NG | growth_rate input に分離 |
| `=B5+1000000` | NG | one-time fee を input |
| `=B5*12` (月→年換算) | △ | timing コンスタントは `Periods_per_year` 経由 |
| `=B5*(B5>0)` | △ | flag を上行に持たせて参照 |
| `=B5+B6+B7` (集計) | OK | ただし行範囲は SUM() を推奨 |

#### 例外

- `0`, `1`, `-1` は OK (`IF(flag, X, 0)` の中の 0、`SUM(X) * -1` の -1 など)
- 単位係数 (`/1000000` 等) は ❌ → number format で scaling
- `100` (= 100% の表示用) は ❌ → input

> **rationale**: モデルが業界標準値を「上書き」したくなる場面 (税率改正、為替変動) で 1 か所修正すれば伝搬する。hardcode が散在するモデルは grep ベースのメンテで漏れる。

### 7.4 IF nesting

| nest 数 | 判定 | 推奨代替 |
|---|---|---|
| 1〜2 | OK | |
| 3 | △ (ぎりぎり可) | flag 行への分解を検討 |
| 4 以上 | NG | `IFS`, `CHOOSE`, `INDEX/MATCH`, lookup table 化 |

#### 変換例

NG (4-deep IF):
```
=IF(stage="Seed", 0.10, IF(stage="Series A", 0.15, IF(stage="Series B", 0.20, IF(stage="Series C", 0.25, 0.30))))
```

OK (lookup table):
```
[Lookup table on Drivers sheet]
A20: stage         B20: rate
A21: Seed          B21: 10%
A22: Series A      B22: 15%
A23: Series B      B23: 20%
A24: Series C      B24: 25%
A25: Growth        B25: 30%

[Formula]
=VLOOKUP(stage, A21:B25, 2, FALSE)
or
=INDEX(B21:B25, MATCH(stage, A21:A25, 0))
```

OK (CHOOSE for ordinal):
```
=CHOOSE(scenario_id, base, upside, downside)
```

OK (IFS, Excel 2019+):
```
=IFS(stage="Seed",10%, stage="Series A",15%, stage="Series B",20%, stage="Series C",25%, TRUE,30%)
```

### 7.5 Avoid volatile / opaque functions

#### Volatile (再計算ごとに値変化 / 計算負荷大)

| 関数 | 推奨度 | 代替 |
|---|---|---|
| `OFFSET` | 避ける | INDEX (静的) |
| `INDIRECT` | 避ける | named range, 構造化参照 |
| `NOW()`, `TODAY()` | 避ける | input セルに固定日付 |
| `RAND()`, `RANDBETWEEN()` | 避ける (本番モデル) | 事前生成し paste values |
| `CELL()` (一部引数) | 避ける | |
| `INFO()` | 避ける | |

#### 推奨される lookup

| 関数 | 用途 | 注意 |
|---|---|---|
| `INDEX` + `MATCH` | 縦横どちらも | 古いが堅い |
| `XLOOKUP` (Excel 365) | 縦横どちらも、戻り値・default 対応 | 互換性確認 |
| `VLOOKUP` | 縦のみ | 列挿入で壊れやすい (`MATCH` で col 取得を併用) |
| `HLOOKUP` | 横のみ | INDEX/MATCH 推奨 |
| `XMATCH` (Excel 365) | MATCH 強化版 | |
| `FILTER` (Excel 365) | 条件抽出 | dynamic array |
| `SUMIFS` / `COUNTIFS` / `AVERAGEIFS` | 条件付集計 | 推奨 |

> **rationale**: volatile 関数は workbook 全体の再計算を毎回トリガする。100 個の OFFSET を含む大規模モデルで再計算が分単位になる事例が実在。INDEX / SUMIFS は volatile ではない。

### 7.6 named ranges の運用

| 派 | 立場 |
|---|---|
| FAST | switch / global 定数のみ命名 (`Scenario_ID`, `VAT_rate`, `Discount_rate`)、time series セルは命名しない |
| Macabacus / IB | 原則 named range なし、相対参照 + 絶対参照のみ |
| ICAEW | 「使うなら一貫させる」 (中立) |
| Project Finance / FAST B5 | 各 block の output 行を命名 (`Revenue_Total`, `EBITDA_Total`) |

#### 推奨運用 (スタートアップ)

- **必ず命名**: scenario switch, global 定数 (tax rate、discount rate、currency)
- **任意**: PL / BS / CF の主要 output 行 (DCF 計算で参照する `EBITDA`, `FCF`, `Net_Debt`)
- **命名しない**: 中間計算行、time series 全体

#### 命名規則

```
PascalCase + アンダースコア区切り、または snake_case
✓ Tax_Rate, Scenario_ID, Discount_Rate, FCF_Y1
✗ TR, t, x1
```

### 7.7 absolute / relative reference

| 場面 | 表記 |
|---|---|
| 同行内で右にコピー | 列固定 `$B5` |
| 同列内で下にコピー | 行固定 `B$5` |
| 全方向に同セルを参照 | `$B$5` (named range 推奨) |
| time series 内の通常参照 | 相対 `B5` |
| anchor row (例: scenario switch 行) を参照 | `B$5` |

> **rationale**: drag コピーの挙動を予測可能にする。`F4` キーで `$` 切替を覚える。

### 7.8 array / dynamic array (Excel 365)

- `SUMPRODUCT` の array 計算は OK (古来の汎用)
- `=A1:A10*B1:B10` のような動的 array は Excel 365 限定。互換性が必要なら使わない
- `LET()` 関数 (中間変数) は 365 限定だが、複雑式の可読性向上に有効

#### LET の例

```
=LET(
    revenue, A5,
    cogs, A6,
    gp, revenue - cogs,
    gp_margin, gp / revenue,
    gp_margin
)
```

> **rationale**: スタートアップで `Excel for Microsoft 365` 利用を前提にできるなら LET を活用、配布先が古い Excel ならば従来式に戻す。互換性を cover sheet に明記。

### 7.9 数式長と複雑性メトリクス

| 指標 | しきい値 |
|---|---|
| 1 cell の式長 | ≤ 80 文字 |
| 1 cell の関数数 (nest を含む) | ≤ 5 |
| 1 cell の参照セル数 | ≤ 7 |
| IF nest 段数 | ≤ 3 |
| 複式 (`+`,`-`,`*`,`/`) の混在数 | ≤ 4 |

これを超える式は警告対象。PerfectXL や Macabacus が自動検出可能。

---

## 6. Freeze panes / Print area / Page setup

> _本章は次のコミットで追記_

---

## 7. 数式 discipline

> _本章は次のコミットで追記_

---

## 8. 学派の違い (House Styles)

### 8.1 主要 figures と教義

| 派 / 流派 | 中心人物 | 起源 | 特徴 |
|---|---|---|---|
| **FAST (Project Finance 系)** | Kenny Whitelaw-Jones, Andrew Berkley, Morten Siersted, Dominic Robertson | UK, 2000s | block 設計、time line、column anchor、flag rows、column F sentinel |
| **Pierre Bernardeau / SMART (BPM)** | Pierre Bernardeau (BPM, France/UK) | 1990s-2000s | 監査観点強化、auditor 寄り |
| **Operis** | Operis (UK) | 1990s | OAK + SMART メソッド、PF / 大型インフラ案件 |
| **Mazars / PwC / Big4 advisory** | (機関各社) | 1990s〜 | クライアントワーク中心、house style は各々あるが ICAEW + FAST のハイブリッド |
| **Wall Street Prep / Training The Street / Macabacus** | Tim Vipond, Hamilton Lin, Macabacus team | 米国、教育 | IB style 教育、format 中心 |
| **Goldman Sachs / Morgan Stanley / JPM** | (各 IB) | 米国、IB house | LBO / M&A モデル、内部 template、format 重視 |
| **Lazard / Evercore / Centerview** | (boutique IB) | 米国、IB house | M&A advisory model、PF + IB のハイブリッド |
| **CFA / NYU Stern Damodaran** | Aswath Damodaran | 米国、academic | valuation 寄り、書式は緩い |

### 8.2 観点別比較表

| 観点 | FAST | IB (Macabacus 系) | Operis / SMART | スタートアップ実務 |
|---|---|---|---|---|
| layout | sheet 多分割 (cover/control/time/inputs/...) | sheet 中分割 (assumptions / model / output) | FAST 寄り | 中分割で十分 |
| input/calc 分離 | 必須 (sheet レベル) | 任意 (block レベル) | 必須 | 必須 (block レベル) |
| color coding | 採用 | 必須 (Macabacus 6 色) | 採用 | 必須 (4 色: 青黒緑赤) |
| named ranges | 限定的 (switch のみ) | 原則使わない | switch + output | switch + output |
| sign convention | section ごとに統一 (混合) | 全 positive (PL) | 全 positive | PL: positive、CF: signed |
| time line | 単一 master timeline | sheet ごとの year header | 単一 master | 単一 master |
| sheet 数 | 多 (10〜30) | 中 (5〜15) | 多 | 中 (10〜15) |
| flag rows | 多用 | 中程度 | 多用 | 中程度 |
| volatile fn | 厳格に禁止 | 控えめ | 禁止 | 禁止 |
| LBO / M&A 専用機能 | 弱 | 強 (sources/uses, ability to pay 等) | 中 | 不要 |
| project finance 機能 | 強 (debt sculpting, DSCR) | 弱 | 強 | 不要 |
| documentation 量 | 多 (cover, glossary, methods) | 中 | 多 | 中で十分 |

### 8.3 IB バンク別テンプレ傾向

> 注意: 公開資料 / リーク資料 / 外部教材 (Macabacus, M&I, Investment Banking 教科書) ベースの一般的傾向。実物 template は内部資料。

| バンク | 傾向 |
|---|---|
| **Goldman Sachs (GS)** | Arial 10、青/黒/緑/赤の標準 4 色、Sources & Uses / Pro Forma の見せ方が定型、ロゴ/フッタが厳格、PDF 出力前提でレイアウト調整 |
| **Morgan Stanley (MS)** | Arial 10、output sheet を front に置く (cover の次)、merger model は accretion/dilution テンプレが固有 |
| **JP Morgan (JPM)** | Arial 10、CF schedule の見せ方が独特 (working capital を専用 block 化)、LBO は IRR ladder 必須 |
| **Lazard / Evercore / Centerview** | Calibri 10〜11 派が多い、boutique 故に template 自由度高め、M&A 事例ごとにカスタム |
| **Houlihan Lokey** | restructuring 案件多数、liquidation analysis / waterfall が標準 |
| **UBS / CS** | 欧州寄り、CHF / EUR / GBP マルチ通貨設計が標準、IFRS 表示 |
| **野村 / 大和 / みずほ** | IFRS / J-GAAP 切替、円表示 (`百万円` 単位)、月末日基準の period 切り、社内承認スタンプの欄 |

### 8.4 スタートアップが採用すべきハイブリッド

スタートアップの財務モデルは「投資家配布」と「経営会議」の両用途が一般的。FAST の規律 + IB の見栄え + ICAEW の governance を組み合わせる:

| 要素 | 採用 | 出典 |
|---|---|---|
| Cover / Control / Time / Inputs / Workings / Outputs / Checks の sheet 分割 | 採用 | FAST |
| 青/黒/緑/赤 color coding | 採用 | IB (Macabacus) |
| number format (`#,##0;(#,##0);-`, `0.0%`, `0.0x`) | 採用 | IB |
| Arial 10pt + bold header | 採用 | IB |
| sign: PL positive, CF signed | 採用 | IB / FAST 混合 |
| named range は switch / global のみ | 採用 | FAST |
| flag rows for time period | 採用 | FAST |
| volatile 禁止 | 採用 | FAST / SMART |
| BS balance / CF tie / sub-total checks | 採用 | ICAEW / SMART |
| change log + glossary + cover | 採用 | ICAEW |
| audience / decision を cover に書く | 採用 | ICAEW |

---

## 9. 統合チェックリスト

ローンチ前に通すべき 50 項目チェックリスト。Pass = ✓、Fail = ✗、N/A = - で記録。

### 9.1 構造 (Structure)

- [ ] Sheet 順が `00_Cover` → `01_Control` → `02_Time` → `03_Assumptions` → `04_Drivers` → ... → `12_SanityChecks` → `99_Glossary`
- [ ] Tab color が分類規則 (黒/紺/青/灰/緑/黄) に準拠
- [ ] Cover sheet に purpose / audience / decision / version / author / date / currency / time scale / scenario の 9 項目
- [ ] Change log に少なくとも初版エントリ
- [ ] Glossary に略語 / 用語定義
- [ ] Hidden sheet なし (またはコメントで存在を明示)
- [ ] All sheets freeze pane 位置統一 (G6)
- [ ] All sheets gridline OFF
- [ ] All sheets で時間軸列が同列 (G〜) から開始

### 9.2 Input / Time

- [ ] Time シートが単一の master timeline を提供
- [ ] All inputs が `03_Assumptions` または `04_Drivers` に集約
- [ ] All inputs 青文字
- [ ] All inputs に units 列に単位明示
- [ ] All inputs に source / 注記
- [ ] data validation がかかっている (% 範囲 0〜1、年範囲 妥当)
- [ ] No hardcoded date inside calc sheets

### 9.3 数式 (Formula)

- [ ] No hardcoded constants in formulas (grep `*0.\d`, `*1.\d` のような pattern が 0 件)
- [ ] No `#REF!`, `#NAME?`, `#VALUE!`, `#DIV/0!` (`Find & Replace` で 0 件)
- [ ] No volatile functions (`OFFSET`, `INDIRECT`, `NOW`, `TODAY`, `RAND`, `RANDBETWEEN`)
- [ ] No external links (or import sheet 経由のみ)
- [ ] IF nest ≤ 3 across all formulas
- [ ] Each row uses single formula pattern (F2 で右に進んで同じ式)
- [ ] No mega-formulas (> 80 文字)
- [ ] Named ranges only for switch / global constants
- [ ] Consistent absolute / relative reference style

### 9.4 Format

- [ ] Font: Arial 10pt body, Arial 11pt bold header (or 規定通り)
- [ ] Color: 青 input / 黒 calc / 緑 cross-sheet / 赤 external のみ
- [ ] Number format: 通貨 `#,##0;(#,##0);-`, 百分率 `0.0%;(0.0%);-`, 倍率 `0.0"x"`
- [ ] Year header: italic + bold
- [ ] Total row: bold + top single border
- [ ] Grand total: bold + top single + bottom double border
- [ ] Sign convention 文書化 (cover sheet) と全 sheet で一致

### 9.5 Output / Integrity

- [ ] BS balance check = 0 全期間
- [ ] CF 期末現預金 = BS 現預金 全期間
- [ ] PL 純利益 = 利益剰余金変動 - 配当 全期間
- [ ] sub-total = SUM(items) 全箇所
- [ ] Outputs に bold + top border (合計線)
- [ ] Checks sheet に summary、cover にも反映

### 9.6 Print / Distribution

- [ ] Print area set on each output sheet
- [ ] Print orientation: landscape
- [ ] Print scaling: fit columns on one page
- [ ] Header / footer: filename, sheet name, page #, version, date
- [ ] PDF 出力サンプルを目視確認
- [ ] File 名: `<Project>_<Model>_v<semver>_<YYYYMMDD>_<initials>.xlsx`

---

## 10. 参考文献

### 10.1 公式 / 主要規格

- **FAST Standard (B2 系)** — `https://www.fast-standard.org/` (旧)、`https://fastalliance.org/` (現 FAST Modelling Alliance)
- **ICAEW IT Faculty — Twenty Principles for Good Spreadsheet Practice** — `https://www.icaew.com/technical/technology/excel/twenty-principles`
- **EuSpRIG (European Spreadsheet Risks Interest Group)** — `https://eusprig.org/` (リスク統計、事故事例)
- **IFAC / IIA / SOX** スプレッドシートコントロール関連ガイダンス (organizational governance)

### 10.2 教育 / IB house style

- **Macabacus** — `https://macabacus.com/learn/financial-modeling-best-practices` (color coding、shortcut、style guide)
- **Wall Street Prep** — `https://www.wallstreetprep.com/knowledge/` (model standards、bank style)
- **Training The Street** — IB 内研修ベンダー、外部公開教材は限定的
- **Corporate Finance Institute (CFI)** — `https://corporatefinanceinstitute.com/resources/financial-modeling/` (basics + standards)
- **Mergers & Inquisitions / Breaking Into Wall Street (BIWS)** — Brian DeChesare、formatting / LBO / M&A モデル教材

### 10.3 書籍

- *Financial Modeling in Excel For Dummies* — Danielle Stein Fairhurst
- *Using Excel for Business and Financial Modelling* — Danielle Stein Fairhurst
- *Principles of Financial Modelling* — Michael Rees (Wiley) — model design + risk
- *The Financial Modeler's Manifesto* — Paul Wilmott, Emanuel Derman
- *Building Financial Models* — John Tjia (McGraw-Hill)
- *Financial Modeling and Valuation* — Paul Pignataro (Wiley)
- *Investment Banking* — Joshua Rosenbaum & Joshua Pearl (Wiley) — IB house style 教科書
- *Project Finance in Theory and Practice* — Stefano Gatti — PF モデル

### 10.4 ツール / 監査

- **Operis Analysis Kit (OAK)** — `https://www.operisanalysiskit.com/`
- **Macabacus add-in** — `https://macabacus.com/`
- **Spreadsheet Inquire** (Excel built-in、Office Pro Plus / 365)
- **Spreadsheet Compare** (Excel built-in)
- **PerfectXL** — `https://www.perfectxl.com/` (formula complexity, audit)
- **xltrail** — `https://www.xltrail.com/` (Excel git diff)
- **F1F Modeller** — `https://www.f1f.com/` (FAST 準拠チェック)
- **ClusterSeven / Mirage** — enterprise spreadsheet risk

### 10.5 関連リソース

- **EuSpRIG Horror Stories** — `https://eusprig.org/research-info/horror-stories/` (実例集、各種事故)
- **Reinhart-Rogoff Excel error** (2013) — 学術モデルの SUM 範囲ミス事例
- **JP Morgan London Whale** (2012) — Excel コピーペーストエラー、$6B loss
- **Olympics 2012 ticketing** — 数式エラーで席数 over-sold

---

> _本文書は §1 FAST、§2 ICAEW、§3 SMART、§4 IB format、§5 sheet 命名、§6 freeze/print、§7 数式 discipline、§8 学派、§9 統合チェック、§10 参考文献の 10 章で構成。エラーチェックの自動化、感度分析の手法、anti-pattern カタログは別ファイル (`01b_*`, `01c_*`) を参照。_

---

## 9. 統合チェックリスト

> _本章は次のコミットで追記_

---

## 10. 参考文献

> _本章は次のコミットで追記_
