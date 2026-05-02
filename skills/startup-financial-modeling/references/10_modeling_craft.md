---
name: modeling_craft
description: モデラーの暗黙知・コツ・Wind-down framework の正本。仮置き / 調整 / 根拠化の craft、Founder 側 wind-down decision sequence。SKILL.md dispatch table の "Down round / wind-down" entry の第 1 reference として §19.1-19.7 で展開。
type: reference
priority: P1
related: [_terminology, 01a_modeling_standards, 01b_integrity_and_anti_patterns, 08_investment_thesis, _stress_framework]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: モデラー暗黙知 / Wind-down framework は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §A, §C`](_master_decision_tree.md) から「craft / wind-down」context のときに参照
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check を必ず実行
- **関連 reference**: `01a / 01b` (formal standards) / `08_investment_thesis` (kill criteria 連動) / `_stress_framework` (stress)

# 10. モデラーの暗黙知・コツ・Craft (Modeler's Tacit Knowledge & Craft)

> スコープ: スタートアップ財務モデリングにおける「**どう仮置きし、どう調整し、どう根拠化するか**」の craft を扱う。構造・規範・公式は `01a_modeling_standards.md` / `01b_integrity_and_anti_patterns.md` を、業務モデルは `02_saas_metrics.md` 〜 `08_investment_thesis.md` を参照。
>
> 対象読者: モデルを「壊さない」段階を超え、「シニアレビューに耐える」段階へ進みたいアナリスト / FP&A / 創業 CFO。
>
> 想定: Series Pre-Seed 〜 Pre-IPO。地域は日本市場メインだが SaaS / Marketplace / Hardware を想定。
>
> 引用源: McKinsey *Valuation* (Koller et al.)、Damodaran *Narrative and Numbers*、Mauboussin *Expectations Investing*、Mark Suster (Both Sides of the Table)、Bessemer Cloud Index / State of the Cloud、Tomasz Tunguz (Theory Ventures blog)、Bill Gurley (Above the Crowd)、Kahneman *Thinking, Fast and Slow*、Flyvbjerg "Reference Class Forecasting"。
>
> 本リファレンスは `scripts/build_model.py` および `sanity_checks.py` から「シニアレビュー視点」の正本として参照される。

---

## 目次

- [1. 変数の根拠主義 (Justification Discipline)](#1-変数の根拠主義-justification-discipline)
- [2. Benchmark Calibration (同業他社バランシング)](#2-benchmark-calibration-同業他社バランシング)
- [3. Hockey Stick / Optimism 検出](#3-hockey-stick--optimism-検出)
- [4. Sensitivity Analysis Discipline](#4-sensitivity-analysis-discipline)
- [5. Forecast 構築のコツ](#5-forecast-構築のコツ)
- [6. Cost Modeling のコツ](#6-cost-modeling-のコツ)
- [7. Cash / Runway モデリングのコツ](#7-cash--runway-モデリングのコツ)
- [8. シニアレビュー時の典型 pushback](#8-シニアレビュー時の典型-pushback)
- [9. Iteration の実務](#9-iteration-の実務)
- [10. 認知バイアス対策](#10-認知バイアス対策)
- [11. Stage-appropriate Modeling](#11-stage-appropriate-modeling)
- [12. Smell Test (直感的 sanity check)](#12-smell-test-直感的-sanity-check)
- [13. Documentation & Defendability](#13-documentation--defendability)
- [14. IB / VC / PE で実際に学ぶ tacit knowledge](#14-ib--vc--pe-で実際に学ぶ-tacit-knowledge)
- [15. ケーススタディ集](#15-ケーススタディ集)
- [16. モデラー成熟度モデル (Maturity Model)](#16-モデラー成熟度モデル-maturity-model)
- [17. 100 Maxims (一行格言集)](#17-100-maxims-一行格言集)
- [18. シニアレビュー想定問答 30 問](#18-シニアレビュー想定問答-30-問)

---

## 共通フォーマット

各 craft 項目は原則として次の構造で書く:

> **原則**: 1 行で言い切る命題。
> **悪い例**: 数値付きで具体に。
> **良い例**: 数値付きで具体に。
> **Rationale**: なぜそうなのか、何が壊れるか。

数値の前提は「Series A / B SaaS、ARR $1-10M、JP+US 顧客、2024-2026 環境」を base に置き、必要に応じてレンジを併記する。USD 表記は $、JPY は 円 / ¥ を使い分ける。

---

## 1. 変数の根拠主義 (Justification Discipline)

> 「**Why this number?** に 1 行で答えられない数字をモデルに残すな」が出発点。すべての入力セルは、**出典付きで防御可能 (defendable)** であるべきという思想。

### 1.1 全変数 4 段階分類 (Tier System)

| Tier | 名称 | 定義 | スタートアップでの典型 | 望ましい比率 |
|---|---|---|---|---|
| **Tier 1** | Hard | 一次データ。実績、契約、請求書、Stripe / NetSuite からの export。第三者が検証できる。 | 過去 12 ヶ月の MRR、署名済み LOI、確定発注 PO | Series B 以降は 30-50% を Tier 1 で固めたい |
| **Tier 2** | Benchmark | 同業他社・業界平均からの外挿。Bessemer State of the Cloud, OpenView SaaS Benchmarks, ICONIQ Growth Reports など。 | 「Series A SaaS の中央値 NRR 110%」「業界 Magic Number 0.7」 | Series A の S&M / 採用効率は大半 Tier 2 |
| **Tier 3** | Expert | CXO・顧問・既存投資家・業界 advisor へのヒアリング。最低 3 名の triangulation を取る。 | 「営業 1 名で月 ARR $30K のリストある」 (CRO 経験者ヒアリング) | Pre-revenue の GTM 仮置きはここに依存 |
| **Tier 4** | Speculation | 推測。ロジックや類推のみで根拠は薄い。**明示マーカー (`SPEC` / `??`) 必須**。 | 「3 年後にエンタープライズ tier を切る」想定の ASP | 全変数の 10% を超えたらモデルは「希望リスト」 |

**rationale**: Tier を明記しない変数はレビュアにとって等価値に見える。創業者の希望と CRO の経験ヒアリングと業界中央値が同じセルに並ぶと、シニアレビューは全変数を疑い直すコストを払う。Tier を入れると「Tier 4 のセルだけ詰める」という会話が成立し、レビュー時間が 1/3 になる。

#### 悪い例

```
Pricing  ¥5,000/seat/month
Growth   8% MoM
NRR      130%
CAC      ¥200,000
```

→ 全部「数字あり気の equally weighted」。Pricing は契約から (Tier 1) なのか希望 (Tier 4) なのか分からない。

#### 良い例

```
Pricing      ¥5,000/seat/mo   T1  既存 12 社契約中央値 (2026-04 時点)
Growth       8% MoM            T2  Bessemer Series A 中央値 7-10%
NRR          130%               T3  CRO Aさん, CSM Bさん ヒアリング (2026-03)
ASP Y3       ¥18,000/seat/mo   T4  ?? Enterprise tier 想定. validate 必要
```

**Rationale**: Tier 4 が 1 行あるだけで「ここが脆弱」とレビュアに即伝わる。シニアは Tier 4 にだけ刺さるので会話が速い。

### 1.2 Assumption Log の正しい書式

シニアレビューで「使える」Assumption Log には **8 列** が要る。1 列でも欠けると次の質問でモデラーが詰まる。

| 列 | 内容 | 例 |
|---|---|---|
| Variable | セル名 / 範囲名 | `NRR_base` |
| Current Value | 現在値 | 130% |
| Tier | T1-T4 | T3 |
| Source | URL / 文書名 / 人名 + 日付 | "CRO Aさん 2026-03-12 ヒアリング" |
| Date | 値を最後に更新した日 | 2026-04-15 |
| Confidence | High / Med / Low | Med |
| Sensitivity | Tornado での寄与 | -10% で Y3 ARR -¥420M |
| Owner | 値の維持責任者 | CFO 田中 |

**追加の "Why this number?" 1 行**: 各 row に最後 1 列で「Why this and not other?」を 1 行で書く。これが書けない数字はモデルに残す資格がない。

#### IB / PE での Assumption Book 構造

PE / LBO モデルでは Assumption Log は別シート ("Assumptions" or "Inputs Cover") として独立し、以下の階層で並ぶ:

1. **Macro / Market** (GDP, FX, interest rate, industry growth)
2. **Revenue drivers** (volume, price, mix, churn)
3. **Cost drivers** (COGS rate, S&M, R&D, G&A)
4. **Capital structure** (debt, equity, dividend)
5. **Tax / Other** (tax rate, depreciation method)

各 driver には「Base / Up / Down」の 3 列とシナリオ ID (`Scen_ID`) で切り替える。スタートアップ向けでも、この階層は流用可能。

### 1.3 「数字を出す前に出典を書く」原則

ハードコードした数値の隣にコメント (出典 + 日付) を書く。Excel/Sheets ともに `セル comment / Note` 機能を使い、数式バーには見えない場所に源泉を残す。

#### セル内 N (note) marker / footnote 番号

セルの右側 1 列を `Note` 列にし、`N1`, `N2`, ... を入れる。シート末尾に footnote ブロック `Notes` を作り、`N1: 2026-03 締結 X 社契約に基づく ¥5,000/seat`。

```
B12  ¥5,000        Pricing per seat        N1
B13  ¥4,500        Pricing per seat (low)  N2
...
B100 Notes
B101 N1   2026-03 締結 X 社 SaaS 契約 (5 年, 100 seat) より中央値
B102 N2   2025-Q4 失注 3 件で提示された competitor 価格平均
```

**Rationale**: 出典がセル内にあれば、半年後にモデルを引き継いだ後任者が「何を根拠に 5,000 にしたか」を 30 秒で確認できる。出典が壊れた (ヒアリング元が退職、URL が 404) 場合も、Notes ブロックを更新するだけで全 row に伝播する。

#### 「ハードコード = 即 footnote」のルール

数式内の constant は `=Sales*1.21` ではなく `=Sales*(1+VAT_rate)` で名前定義し、`VAT_rate` セルに footnote を貼る。これは `01a_modeling_standards.md` §1.2 の FAST 規範と同じだが、**craft 視点では「footnote のない constant はバグ」と扱う**のが規律。



## 2. Benchmark Calibration (同業他社バランシング)

> 「自分の数字を見る前に、隣の家の数字を見る」。Damodaran は *Narrative and Numbers* で「story を numbers で律し、numbers を story で説明する」と述べる。Benchmark は story の reality check に他ならない。

### 2.1 Triangulation 三角測量

良いモデルは 1 つの仮置きに対し **最低 3 つの独立データ点** で triangulate する:

1. 自社想定 (founder / CRO の主観 + 過去 trend)
2. 同業他社 5-10 社の実績 (公開 KPI / S-1 / 投資家資料)
3. Industry median / quartile (Bessemer State of the Cloud, OpenView, ICONIQ Growth, KeyBanc CapMkts SaaS Survey, SaaStr)

中央値だけ見るのではなく **分散** も見る。

| 指標 | Bottom 25% | Median | Top 25% | Top 5% |
|---|---|---|---|---|
| ARR Growth (Series A SaaS) | 80% | 150% | 250% | 350%+ |
| NRR | 95% | 110% | 125% | 140%+ |
| Gross Margin | 60% | 72% | 80% | 85%+ |
| CAC Payback (months) | 24 | 18 | 12 | 6 |
| Magic Number | 0.4 | 0.7 | 1.1 | 1.5+ |
| Burn Multiple | 3.0 | 1.5 | 0.8 | 0.5 |

(出典: Bessemer State of the Cloud + OpenView SaaS Benchmarks 各年版を統合した経験則レンジ。具体年版は cell footnote で要更新)

#### Comp set の選び方 (4 軸)

| 軸 | 揃えるべきか | 理由 |
|---|---|---|
| **Stage** (Series A/B/C, ARR scale) | 必須 | Magic Number / Burn は stage で大きく違う |
| **Business model** (SaaS / Marketplace / Hardware / Hybrid) | 必須 | Gross margin の構造が異なる |
| **ACV / Customer size** (SMB / Mid / Enterprise) | 強く推奨 | CAC Payback / Sales cycle の桁が変わる |
| **Geography** (US / JP / EU / Global) | 推奨 | NRR や採用コスト構造が異なる |

**5-10 社が ideal**。3 社未満は "n が小さい" と即 reject、20 社超は均一性が崩れて median が無意味化する。

### 2.2 「ありえない数値」の自動検出

Sanity check の 1st pass は機械的にできる。`sanity_checks.py` で実装する閾値群:

| ルール | 閾値 | アクション |
|---|---|---|
| Gross Margin > 業界 max | SaaS で > 90% | flag |
| Growth + 1 年で +1000bps 以上の加速 | YoY 成長率が前年比 +10pp | flag |
| CAC Payback < 業界 best in class | SaaS SMB で < 6mo, Enterprise で < 12mo | flag |
| NRR > 150% | エンタープライズ Net Adds 過剰外挿 | flag |
| S&M efficiency が同期間に 2x 改善 | Magic Number 0.5 → 1.0 を 12mo で | flag |
| ARR per Sales Rep > $2.5M | 上位 5% でのみ実現 | flag |
| Headcount per ARR $1M < 5 | 異常な lean を表示 | flag |
| Year 5 EBITDA Margin > 40% (SaaS) | 上場 SaaS の上位 5% | flag |

**Rationale**: これらは「物理的にあり得ない」のではなく「物理的に稀」。flag された時点で `Why this number?` ヒアリングが発動する。創業者バイアス (内部 cohort の good case を全社外挿) は大半ここで検出される。

#### 創業者バイアスの典型 5 つ

1. **Best cohort 外挿**: 社内 design partner 3 社の retention が 105% → 全社 NRR を 105% で置く (現実は 90% である)。
2. **Pilot pricing の永続化**: pilot で ¥3,000 を ¥10,000 に上げる前提を契約根拠なしに置く。
3. **Top sales の標準化**: 1 名のトップ営業の 2x 数字を全営業の base に。
4. **顧客 ICP の broadening**: Enterprise でうまくいったから SMB 10x 仮置きを top-down で乗せる。
5. **Marketing CPA の固定**: $50 CPA が channel saturation 後も維持される前提。

### 2.3 Best in class vs Realistic anchor

「業界 top 5% を base に置くのは無効」。Bessemer Cloud 100 や Public SaaS の top decile は **survivorship bias の塊** であり、初期 100 社のうち生き残った 1 社の数字。Series A の 80% は median 以下に着地する。

| Stage | Realistic anchor (NRR) | Aspirational (Top 25%) | Aspirational (Top 5%) |
|---|---|---|---|
| Pre-seed / Seed | n.a. (data 不足) | n.a. | n.a. |
| Series A | 100-110% | 120% | 135%+ |
| Series B | 110-120% | 130% | 140%+ |
| Series C | 115-125% | 130% | 145%+ |
| Pre-IPO | 115-125% | 130% | 140%+ |

**ルール**: モデルが Top 25% より上を base に置く場合、その理由を 3 行以上で説明できなければ Tier 4 (speculation) として明示する。

#### 悪い例

「Snowflake は NRR 178% だった。我々も同じ ICP を狙うので NRR 150% を base に」

→ Snowflake は data warehouse で usage-based、ICP は Fortune 500、PMF 後の現象。Series A の汎用 SaaS で 150% は top 1%。Tier 4 確定。

#### 良い例

「Series A SaaS の中央値 NRR 110% を base に置く。Upside は 120% (top 25%)、Downside は 100% (bottom quartile)。Snowflake 178% は industry exception として比較対象外。」

### 2.4 Maturity Curve 沿わせ

スタートアップの主要指標は「物理的な改善速度」を持つ。これに沿わない予測は要警戒。

#### Revenue ramp の典型カーブ (SaaS B2B)

| 月 / 年 | $ARR (典型) | YoY |
|---|---|---|
| 12 ヶ月 (Year 1 end) | $0.3-0.8M | n.a. |
| 24 ヶ月 (Year 2 end) | $1-3M | 200-400% |
| 36 ヶ月 (Year 3 end) | $3-10M | 200-300% |
| 48 ヶ月 (Year 4 end) | $8-25M | 150-200% |
| 60 ヶ月 (Year 5 end) | $20-60M | 100-150% |

(参考: Bessemer "Path to $100M ARR"、$100M ARR 到達の中央値は 84 ヶ月 / 7 年)

「Year 3 で $30M ARR 着地」は top 5% の世界 (T2D3 = Triple, Triple, Double, Double, Double を完遂する想定)。Series A モデルでこれを base に置いている時点で再校正必要。

#### Gross Margin expansion の現実速度

| 業態 | 年改善幅 (典型) | 上限 |
|---|---|---|
| SaaS (Pure software) | +100-300 bps/yr | 80-85% |
| SaaS (with services) | +200-500 bps/yr (services 比率減) | 70-78% |
| Marketplace (Take rate fixed) | +50-150 bps/yr | 30-40% (take rate type による) |
| Hardware | +50-150 bps/yr (scale + 部材交渉) | 50-60% |
| Hardware-as-a-Service | +150-300 bps/yr | 55-65% |

**ルール**: GM 改善が年 +500bps 超を 2 年連続で出す前提は Tier 4。理由 (e.g., infra 移行、AWS reserved instance、特定ベンダー切替) を文書化。

#### S&M efficiency 改善曲線

Magic Number / CAC Payback / LTV/CAC の改善は **段階的**:

- Year 1-2: PMF 後で magic number が 0.3 → 0.7 へ (大改善は可能)
- Year 3-4: 0.7 → 0.9 (中程度)
- Year 5+: 0.9 → 1.1 (限界)

「Year 5 で magic number 1.5」は、PLG + viral product でのみ実現する exception。



## 3. Hockey Stick / Optimism 検出

> 「Year 3 で曲がるグラフは大体ウソ」。Mark Suster が "The Hockey Stick Sale" で繰り返し書いている通り、創業者プレゼンに必ず現れるカーブで、シニアレビューでは即座に Pull-back の対象。

### 3.1 Hockey Stick Syndrome

**典型のパターン**: Year 1-2 で +50% / +80%、Year 3 で +200%、Year 4 で +250%、Year 5 で +200%。年率成長が「途中で加速する」前提。

#### 悪い例 (典型 hockey stick)

| Year | ARR (¥M) | YoY |
|---|---|---|
| Y1 | 50 | n.a. |
| Y2 | 90 | +80% |
| Y3 | 270 | +200% |
| Y4 | 700 | +160% |
| Y5 | 1,400 | +100% |

→ Y2→Y3 で成長率が +200% にジャンプする「具体的根拠」が見当たらない。同じ顧客 ICP で同じ ASP でなぜ Y3 から急激に売れる?

#### 良い例 (説明可能カーブ)

| Year | ARR (¥M) | YoY | 駆動要因 (年単位) |
|---|---|---|---|
| Y1 | 50 | n.a. | Founder-led sales 4 deals/qtr |
| Y2 | 130 | +160% | AE 2 名追加で 8 deals/qtr |
| Y3 | 280 | +115% | Mid-market segment へ拡張、AE 4 名 |
| Y4 | 540 | +93% | パートナーチャネル稼働、Enterprise 1 deals/Q |
| Y5 | 900 | +67% | Net retention が成長の半分を占める |

**Rationale**: 各 Y で「**何が増えて売れるのか**」が一文で答えられる。AE 数, channel, segment expansion など driver の追加が描けると、ホッケースティックではなく **物理的な階段関数** になる。

### 3.2 同時改善の二重カウント (Compounding fallacy)

楽観モデルの第二の罠は「**price + volume + margin が同時に拡大**」する想定。

| 仮置き | base | optimistic | 注意点 |
|---|---|---|---|
| Volume (顧客数) | +50% | +80% | OK 単独 |
| ASP (price/customer) | +5% | +15% | OK 単独 |
| Gross Margin | +200bps | +500bps | OK 単独 |
| NRR | 110% | 130% | OK 単独 |
| **複合効果** | revenue +60% | revenue +130% | **NG** — 全部 best が同時実現は確率 1-3% |

**Rationale**: 各 driver が独立 (independent) であるとき、4 つの best を同時実現する確率は `0.25^4 ≈ 1.5%`。しかも実務では「ASP を上げると volume が落ちる」など **負の相関** があるため、もっと低い。Best case を組む時は driver 間の相関を考えよ。

### 3.3 Optimism Bias の補正

#### Inside view vs Outside view (Kahneman, *Thinking, Fast and Slow*)

- **Inside view**: 「うちは特別、Roadmap が見えてる、x社にない強みがある」 → 楽観
- **Outside view**: 「同じ stage の同種会社がどう着地したか」 → 中央値に regress

**ルール**: Inside view を base case として置きたいなら、Outside view を downside / pessimistic として並列で置き、確率 50/50 で blend するのが最低限の規律。

#### Reference Class Forecasting (Bent Flyvbjerg)

公共インフラ予測で実証された手法。「自分のプロジェクトの予測」を信じず、**過去の類似プロジェクトの実績分布**から forecast する。

スタートアップへの適用:
1. Comp set 10 社の Y1-Y5 ARR ramp を実績で集める
2. 中央値 / 四分位を ramp curve として描く
3. 自社想定が Top 25% より上にある場合、`Top 25% に置く理由` を明文化
4. 説明できなければ Median に regress

「過去の自分」も reference class に入れる。前回の予算が外れた幅 (e.g., Y1 計画の 60% 着地) を Y2 の補正係数として適用するだけで精度が上がる。

#### "Plan for the worst case, sell the best case" の罠

VC pitch で best case を見せるのと、社内予算で worst case を運用するのは正しい。**しかし両者を同じファイルで管理しないとモデルが破綻する**。Pitch 用 base が社内 budget の base と一致してしまうと、計画未達時の説明責任 (accountability) が壊れる。

→ シナリオ ID を明示的に分け (`Pitch_Base`, `Internal_Plan`, `Bear`)、**Internal_Plan は Pitch_Base の 60-70% を base** に置くのが実務。

### 3.4 Conservatism 不足 — Worst Case が「楽観的 base」になっている誤り

「Worst case でも Y3 ARR ¥500M」というモデルの大半は、worst ではなく **mildly optimistic**。Series A の 70-80% は「計画どおりにいかない」(Mark Suster, "Why Most VCs Don't Hit Their Returns")。

#### 真の Worst Case の作り方

1. **Top 顧客 1 社の喪失** (集中リスクを反映)
2. **Funding window 12-18 ヶ月閉鎖** で bridge round しか取れない
3. **新規受注ペース 50% 減** が 4 quarter 続く
4. **Key engineer 2 名退職** で開発遅延 6 ヶ月
5. **Macro recession** で B2B SaaS 予算 -30%

これらの **2 つ以上** が同時に起きるシナリオが Worst case。1 つだけだと "Bear" レベル。

#### 悪い例

「Worst Case: 成長率を base から -30% に下げる」 → これは Bear ですらない、Mild Down case。

#### 良い例

「Worst Case: Top customer (revenue 18%) churn + 新規受注 4Q 連続 -50% + bridge round (薄い)。結果、Y3 末 ARR ¥180M、runway 7 ヶ月、解雇 25 名必要。」

**Rationale**: Worst case の役割は「会社が死ぬ条件」を可視化し、**経営者が早期に何を止めるかを事前合意**すること。マイルドな worst case はこの役割を果たさない。



## 4. Sensitivity Analysis Discipline

> 「全部の変数を ±10% で振っても意味がない」。Mauboussin *Expectations Investing* は「market expectations を逆算し、どの driver の前提が決定的か」を問う。Sensitivity の目的は **意思決定者にとって決定的な driver を浮き上がらせる** ことであり、装飾ではない。

### 4.1 何を flex するか (variable selection)

Top 5 drivers を Tornado analysis で識別する。寄与度 (contribution) は **`(高ケース output - 低ケース output) / 中央 output`** で測る。

#### Tornado analysis 手順

1. base case で全 driver を保持
2. 1 driver だけ low / high (e.g., ±25%) に振る
3. 終端 (Y5 ARR / EBITDA / Equity Value) の変動幅を記録
4. 全 driver で 2-3 を繰り返す
5. 変動幅で降順ソートしてバーチャートに描く

| Driver | -25% | +25% | レンジ (Y5 ARR ¥M) |
|---|---|---|---|
| New Logo Volume | 600 | 1,300 | 700 |
| NRR | 700 | 1,200 | 500 |
| ASP | 750 | 1,150 | 400 |
| Churn | 800 | 1,100 | 300 |
| AE Productivity | 850 | 1,070 | 220 |
| Pricing increase | 880 | 1,030 | 150 |

→ Top 3 (New Logo, NRR, ASP) で意思決定の 80% が決まる。これらだけを 2-D sensitivity で深掘り、残りは飾り。

#### High impact × High uncertainty を最優先

2x2 マトリクスで:

| | Low Uncertainty | High Uncertainty |
|---|---|---|
| **High Impact** | base に固定して動かさない | **最優先で sensitivity** |
| **Low Impact** | 動かす意味薄 | 動かす意味薄 |

「Impact 大 × 不確実性大」だけが flex の対象。Impact 小 × 不確実性大は worry zone (ノイズで気を散らす) なので削る。

### 4.2 Range の決め方

#### ±10% は「飾り」

成熟業界の DCF なら ±10% でも意味があるが、スタートアップでは driver の historical volatility が桁違い。Series A SaaS の Y3 ARR は base 想定の 0.4x - 2.5x の幅で着地するのが現実 (ICONIQ Growth, Bessemer 観測ベース)。

#### 業界 historical volatility に合わせる

| Driver | 推奨レンジ (Series A-B SaaS) | 根拠 |
|---|---|---|
| YoY Growth | -50%, +100% | 中央値 ±1σ |
| NRR | -15pp, +20pp | 中央値 ±1σ |
| Gross Margin | -500bps, +500bps | comp 分散 |
| CAC | -30%, +50% | channel saturation の非対称性 |
| Hiring (FTE) | -20%, +30% | 採用遅延の非対称性 |
| ASP | -20%, +30% | tier mix shift |

**rationale**: Range が小さすぎると tornado が「全部似たような長さ」になり差が見えない。実務 volatility に合わせると discriminating power が上がる。

#### 「物理的にあり得ない範囲」は外す

NRR を ±50% で振ると 60-180% の範囲を取るが、180% は単独 outlier 以外は無理。±20pp で十分。

### 4.3 Combination の罠

#### Best case 同時実現

revenue best × margin best × CAC best × NRR best を全部同時に実現する想定は、独立仮定でも確率 ~1-2%、相関を入れるとさらに低い。

#### 悪い例

`Best case = base * 1.5 * 1.2 * 1.1 * 1.15 = base * 2.28x` (4 driver を multiplicatively 重ねる)

#### 良い例

`Best case = base * 1.4` (4 driver の 1 σ 同時シフトを Cholesky 分解で相関調整。実質的には 1 driver only の +50%)

または、シナリオを driver bundle で組む:
- **Bull**: Volume +30%, ASP fixed, NRR +5pp, Margin fixed (volume 主導)
- **Base**: median
- **Bear**: Volume -20%, NRR -5pp (volume 落ちでも margin は fixed)

driver を bundle に纏めると、内部相関を経営者が議論できる。

### 4.4 Stress Test (tail scenario)

「**What kills this company?**」シナリオ。Sensitivity ではなく、Survivability test。

#### 必須 4 シナリオ

| シナリオ | 内容 | 数値仮定 |
|---|---|---|
| **Concentration loss** | Top 3 顧客が同時 churn | Revenue -25%, gross profit -40% |
| **Funding window 閉鎖** | 12-18 ヶ月新規エクイティ取れず | Cash burn を維持 → Y5 末 cash 0 |
| **Macro shock** | B2B IT 予算 -30% (recession) | New ARR -50%, churn +5pp が 6 quarter |
| **Regulatory shock** | 法改正 / 個情法強化 / 業界規制 | Compliance cost +¥50M/year, 一部 segment 失注 |

#### 各シナリオでの意思決定

| シナリオ | Trigger | Action |
|---|---|---|
| Concentration loss | Top 1 churn 兆候 (NPS<0, exec change) | New ARR 強化に S&M +30%、Concentration upper bound 25% に契約上設定 |
| Funding closed | bridge 必要 | RIF 25-40%、growth pause、`Default Alive` (PG) 状態に移行 |
| Macro shock | 業界 NPS / 受注速度 -30% | Spend freeze、cash preservation |
| Regulatory | 法施行 6 ヶ月前 | Compliance team setup、価格改定で吸収 |

**Rationale**: Stress test の役割は「死ぬ条件と死を避ける action」を事前に board と握ること。実際にイベントが来た時に panic ではなく playbook が動く。Paul Graham の「Default Alive vs Default Dead」(2015) と同じ思考。



## 5. Forecast 構築のコツ

### 5.1 "Drivers, then formulas, then numbers" 順序

新しいモデルを作る時の鉄則は **構築順序**:

1. **Driver tree を描く** (紙 or Miro / FigJam)
2. **依存関係を確認** (どの driver がどれを動かすか)
3. **数式に落とす** (input cell を空にして formula のみ実装)
4. **数値仮置き** (input cell に Tier 1-4 のいずれかで置く)

#### 悪い例

「とりあえず Excel を開いて Y1 から ¥50M、Y2 ¥100M、Y3 ¥250M を打ち、後で driver を遡って探す」

→ 「数字あり気の逆エンジニアリング」になり、driver 間の整合が壊れる。Y3 ¥250M を実現する CAC / AE / pipeline を後から逆算してもどこかが破綻する。

#### 良い例

```
Driver tree:
  ARR
   ├── New ARR
   │   ├── # of AE
   │   ├── ARR per AE per quarter (productivity)
   │   └── Ramp factor (新人は 0.3x で Y2 から 1.0x)
   └── Existing ARR
       ├── Beginning ARR
       ├── Expansion (NRR upside)
       └── Churn (gross churn)
```

→ AE 数を変えると New ARR が動く、ramp で AE productivity が動く、という **依存関係が明示**。Y3 の数字は driver 設定の **結果** として出てくる。

### 5.2 Bottom-up + Top-down の二重突合

| 観点 | Bottom-up | Top-down |
|---|---|---|
| 出発点 | 営業 / pipeline / cohort 実績 | TAM × 取れる share × ARPU |
| 強み | 短期精度高 (12-18 mo) | 長期上限を担保 |
| 弱み | 長期で TAM 越え | 中期で driver 不在 |
| 用途 | 予算 / OKR | Strategic、VC pitch |

#### 突合の規律

**Y1-Y2 は Bottom-up、Y3-Y5 は両者を 5-10% 以内に収める**ように調整。

例:
- Bottom-up Y5 ARR = ¥1,200M
- Top-down (TAM ¥80B × 1.5% share) = ¥1,200M → OK
- Bottom-up Y5 ARR = ¥1,200M
- Top-down = ¥600M → Bottom-up が "売れすぎ" or TAM 推定が甘い → 再検討

#### 「Plug」を作らない

Bottom-up と Top-down が一致しない時に、差額を「ASP 上昇」「期末ボーナス契約」など **物理的根拠のない調整セル** で埋めるのは禁。差は議論の対象であって、隠す対象ではない。

### 5.3 月次 → 四半期 → 年次の整合

#### よくあるバグ

| バグ | 症状 | 原因 |
|---|---|---|
| Seasonality 消失 | 月次で見た季節変動が四半期で平準化 | 月次 → 四半期 集計時に average を使う |
| 年次合計不整合 | Σ(月次) ≠ 年次行 | 中間期に hardcode を上書き |
| Quarter end の旗が ずれる | Q1 末が 3/31 でなく 4/1 | flag 行 (Period_End) と date 行が不整合 |
| Day count 微差 | 月次で 30/31 day を考慮していない | revenue / interest accrual で誤差発生 |

#### 整合性の自動 check

```
Check_Annual!B5  =SUM(Monthly!B12:M12) - Annual!N12
                  → 0 でなければ NG
Check_Quarter!B5 =SUM(Monthly!B12:D12) - Quarterly!Q1_12
```

`01b_integrity_and_anti_patterns.md` の master check pattern を流用。

### 5.4 Ramp Curve のコツ

#### Linear ramp vs S-curve

新規 channel / product / segment の ARR ramp は **S-curve** が現実。Linear ramp (素人) は month-1 から full productivity を仮定するが、S-curve は:

| Month | % of full productivity | 累計 ARR |
|---|---|---|
| 1 | 10% | 10 |
| 3 | 30% | 60 |
| 6 | 60% | 250 |
| 9 | 90% | 530 |
| 12 | 100% | 850 |

(Logistic curve, midpoint ~6mo, k=0.5)

#### 業界別 ramp time

| 業態 | First $1M ARR | First $10M ARR |
|---|---|---|
| SMB SaaS (PLG) | 6-12mo | 24-36mo |
| Mid-market SaaS | 12-18mo | 30-42mo |
| Enterprise SaaS | 18-30mo | 36-60mo |
| Marketplace | 12-24mo (liquidity 後) | 36-48mo |
| Hardware/IoT | 18-36mo | 48-60mo |

(参考: Bessemer "State of the Cloud 2023", ICONIQ Growth "Topline Growth Benchmarks")

「Year 1 で $5M ARR」を仮置きする時、業界の First $1M に 6-12mo かかる事実と整合するか確認。

---

## 6. Cost Modeling のコツ

### 6.1 OpEx の原則

#### "Variable cost が固定費に化ける"

「Variable」と書いてあっても、契約や採用で 6-12mo lock-in しているコストは **実態として固定費**:

| 項目 | 名目 | 実態 |
|---|---|---|
| AWS / インフラ | usage-based | reserved instance / commit で 1-3 年固定 |
| 営業給与 | variable comp | base salary は固定、commission は売上の 10-25% |
| 業務委託 | hourly | 月次 retainer 化で固定費 |
| オフィス | scalable | 2-5 年契約 |
| Marketing | dial up/down | brand / SEO / partner は半固定 |

→ 「すぐに止められるコスト」は実は OpEx の 30-40% 程度。残り 60-70% は 6-12mo 視野での固定費と扱うのが現実。

#### Headcount-driven 固定費比率

スタートアップの OpEx の **70-85% は人件費**。Headcount × Fully Loaded Cost で大半が決まる。

```
Fully Loaded Cost (FLC) = 給与 × 1.3 〜 1.5
  (社会保険 ~14%, 法定福利 ~3%, 賞与, 設備費, ライセンス)
```

JP 大手都市:
- Senior Engineer: 給与 ¥10M → FLC ¥13-15M
- Senior AE: 給与 ¥9M (base) + ¥6M (OTE commission) → FLC ¥18-22M
- Junior Marketer: 給与 ¥6M → FLC ¥7.8-9M

US (Bay Area):
- Senior Engineer: $180K + equity → FLC $230-260K
- Senior AE: $130K base + $130K OTE → FLC $290-340K

### 6.2 採用計画の現実

#### Lag を入れないモデルは破綻

```
Plan: "Q1 に Senior Engineer 3 名採用"
Reality:
  Sourcing開始 W1
  Offer出る W8-12
  Acceptance W12-14 (offer accept rate 60-70%)
  Onboarding W14-22 (4-8w で 50% productivity)
  Full productivity W22-36 (営業は 6-9mo)
```

#### モデル化の最小規律

| Stage | Time (week) | Productivity |
|---|---|---|
| Hire decision → Offer | 0-8 | 0% |
| Offer → Start | 8-14 | 0% |
| Start → Ramped | 14-26 (Eng), 14-40 (Sales) | 0-100% linear |
| Full | 26+ (Eng), 40+ (Sales) | 100% |

採用 1 名のフル稼働まで Eng 6mo / Sales 9-12mo として ARR ramp model に組み込む。

#### Attrition (離職)

Series A-B SaaS の年間 attrition は **15-25%** が中央値 (US tech は 20%、JP tech は 12-18%)。10% 未満の前提は楽観。

```
Net Hiring = Gross Hiring - Attrition
  Y3 末 Headcount = Y2末 + Hiring - Attrition
  Attrition = Y2末 Headcount × 18%
```

Attrition を入れないと「Y3 末 50 名 + Y4 で 30 採用 = 80 名」の楽観モデルになるが、現実は `80 - 50*0.18 = 71` 名 + 採用ロス。

### 6.3 Margin Expansion 期待値

| Margin | Year 1 | Year 3 | Year 5 (SaaS realistic) | Y5 楽観 (top quartile) |
|---|---|---|---|---|
| Gross Margin | 65% | 72% | 78% | 82% |
| Operating Margin | -120% | -30% | +5% | +20% |
| EBITDA Margin | -110% | -25% | +10% | +25% |
| FCF Margin | -130% | -35% | -5% | +15% |

(SaaS Series A-B 想定。出典: Bessemer Cloud 100, KeyBanc SaaS Survey)

「Y5 で Operating Margin +30%」は上位 5%。`Rule of 40` (Growth + Profit Margin) を 40 で抑える設計が標準的。



## 7. Cash / Runway モデリングのコツ

> 「**Cash is reality, P&L is opinion**」(IB の格言)。スタートアップにとって P&L Loss と Cash Burn は別物。runway を読み違えると倒産する。

### 7.1 Burn の本当の数値

#### Net Burn ≠ P&L Loss

| 項目 | P&L Loss に含まれる | Cash Burn に含まれる |
|---|---|---|
| 営業損失 | Yes | Yes |
| 減価償却 | Yes (cost) | No (non-cash) |
| 在庫増加 | No | Yes (cash out) |
| 売掛金増加 | No | Yes (cash 未回収) |
| 買掛金増加 | No | -Yes (cash temporarily preserved) |
| Capex (PP&E) | No (期間外) | Yes (cash out) |
| 前受金増加 (年契約) | No | -Yes (cash temporarily +) |

→ Net Burn は **Cash Flow Statement (CFS) の CFO + CFI** で見るのが正解。P&L Operating Loss を Burn と呼ぶのは誤り。

#### 数式

```
Net Burn = Beginning Cash - Ending Cash + Net Equity Raised - Net Debt Drawn
```

または:

```
Net Burn = - (CFO + CFI) [+ ストック ベース報酬 (SBC) は non-cash で除く]
```

#### Quarterly burn の振れ幅

四半期 burn は seasonality で 1.3-1.5x 振れる。年契約 invoice (Q1 集中) があると Q1 は burn が下がり、Q2-Q4 で burn が増える。**月次 burn を季節性無視で year/12 と近似すると runway 計算が壊れる**。

#### Cash conversion lag

- 受注 → 請求書発行: 0-30 days
- 請求書 → 入金: 30-60 days (NET 30, 大手 NET 60)
- 失注 → 既存契約解約反映: 30-90 days

→ ARR が Q1 に +¥100M 増えても、cash 着金は Q2-Q3。Burn 軽減は遅れて現れる。

### 7.2 Runway 計算の罠

#### Static burn 仮定の誤り

```
Naive: Runway = Current Cash / Monthly Burn
       = ¥800M / ¥40M = 20 ヶ月
```

→ 実際は売上拡大に S&M / Hiring を投入するので burn は増える。Static burn は最も楽観のシナリオ。

#### 動的 runway

```
Month 1: Cash 800, Burn 40, End 760
Month 2: Cash 760, Burn 42 (+2 hire), End 718
...
Month n: Cash 0
```

Plan 通りに hiring すると burn は徐々に増加し、runway は naive 計算より **短くなる**。

#### "Months of cash" vs "Months of zero revenue cash"

| 指標 | 定義 | 用途 |
|---|---|---|
| Months of cash | Current Cash / Net Burn | 通常運転 |
| Months of zero-revenue cash | Current Cash / Gross Burn (revenue 全 0 想定) | Tail risk / pandemic |
| Default Alive months | 計画 12mo 以内に CF break-even に到達できる cash | Paul Graham (2015) |

VC は最低 18-24mo の runway を求める。12mo を切ると bridge round 検討 (条件は base round より厳しい)。

### 7.3 Funding Gap の見積もり

#### Next round までの proof point

| Stage | 次ラウンドで求められる ARR / KPI | 必要 runway |
|---|---|---|
| Seed → Series A | ARR $1-3M, growth 200%+ | 18-24mo |
| Series A → Series B | ARR $5-15M, NRR 110%+, magic 0.7+ | 18-24mo |
| Series B → Series C | ARR $15-40M, NRR 115%+, path to profitability | 18-24mo |
| Series C → Pre-IPO | ARR $80M+, gross margin 75%+, Rule of 40 | 24-36mo |

(参考: ICONIQ Growth "Topline Growth Benchmarks", Bessemer "Path to $100M ARR")

#### Dry powder 残量

「Cash on hand × 0.7」を実質 dry powder とする (急場の使い切れない buffer 30% を除く)。Term sheet 締結から着金まで 6-10 週間かかるので、cash 0 ヶ月前には bridge を始めないと間に合わない。

#### Bridge round の現実

- 既存 VC が lead するか伴走するかで条件が決まる
- 大半は SAFE / Convertible Note (`04a_convertible_and_terms.md` 参照)
- valuation cap は前ラウンドの 0.7-1.0x が一般的 (down round に近い)
- Bridge を取るほど equity は希釈する。最初から 24mo runway を引くのが理想。



## 8. シニアレビュー時の典型 pushback

VC partner / PE MD / 監査 senior が必ず聞いてくる質問パターン。事前に「**1 文で答え**」を準備していないモデルは、ミーティング 5 分で穴が空く。

### 8.1 "Where did this number come from?"

最も基本かつ最も致命的な質問。Source unclear → 即 reject。

#### 悪い例

「業界平均だと思います / どこかで見ました」 → 終了。

#### 良い例

「Bessemer State of the Cloud 2024、Series A SaaS の中央値 110% NRR を base に置いています。Comp set は X, Y, Z 5 社、median 112%、range 95-130%。」

#### Average の隠れ仮定

| 落とし穴 | 例 |
|---|---|
| Mean vs Median | 「業界平均 NRR 130%」 → これは mean。Snowflake 等 outlier に引っ張られる。Median は 110% |
| GAAP vs non-GAAP | 「EBITDA Margin 25%」が SBC を除いた non-GAAP なのか、GAAP かで全く違う |
| Net vs Gross (churn) | 「Churn 5%」が gross か net かで意味が逆転する |
| LTV 算出方法 | LTV = ARPU/churn か ARPU × Gross Margin / churn かで 2x 違う |

シニアは「**どの定義で?**」を必ず聞く。1 行で答えられないと、その時点でモデル全体の信頼度が落ちる。

### 8.2 "Why is this different from comp X?"

#### 悪い例

「我々の方が強いから / プロダクトが優れている」 → 主観。

#### 良い例

「Comp X は SMB 中心 (ACV $5K)、当社は Mid-Market (ACV $25K)、ACV 5x で CAC payback が逆に 1.5x 改善する。これは Y 社 (Mid-Market 同類) の data point と整合。」

#### Specific moat / Why Now

「Why us, why now」を **3 文で説明**:
1. 自社の構造的優位 (technical, distribution, data, regulatory) — 1 文
2. 業界の構造変化が今起きている理由 — 1 文
3. 競合がこの優位を取れない理由 — 1 文

(参考: Bill Gurley "All Markets Are Not Created Equal", a16z investment memo template)

### 8.3 "What would have to be true?"

VC の典型質問。Bezos の Working Backwards に通じる **逆算思考**。

「Y5 ARR ¥3B」を成立させるためには:
- Y5 末 顧客数 = 1,500 社 × ACV ¥2M
- → AE 30 名で年 50 deals/AE × 5 years
- → AE per quarter 12 deals = 月 4 deals
- → pipeline 4-5x なので月 16-20 deals 入口必要
- → MQL 20 → SQL 5 → Closed 1 (5% conv) で月 SQL 16-20 = MQL 200/mo

→ MQL 200/mo を Marketing が出せる前提が現実か? ここが破綻すれば全シナリオが破綻。

### 8.4 "How does this break?"

全提案には **3 つの脆弱点** がある。自覚していないモデルは未熟。

#### 必須 self-question

| 質問 | 例 |
|---|---|
| "What kills this?" 単一要因 | Top customer churn (revenue 25%), founding eng 退職 |
| "Slowly bleeds" 2 要因 | NRR 95% に低下 + new logo -30%, channel が 1 つに依存 |
| "Black Swan" tail | 規制変更、競合の disruptive entry、macro recession |

各シナリオで「いつ気づくか」「何 trigger で action を取るか」を 1 行で書く。

---

## 9. Iteration の実務

### 9.1 v0 → v4 の進化

| Version | 期間 | 内容 | レビュアー |
|---|---|---|---|
| v0 | 1 day | 数値ハードコード、形だけ | self |
| v1 | 1 week | driver tree + formula 化 | CFO |
| v2 | 1 week | sensitivity / 3 scenario 追加 | CFO + advisor |
| v3 | 1 week | comp benchmark 反映、stress test | Lead VC |
| v4 | 継続 | stakeholder review、quarterly re-forecast | Board |

### 9.2 "Model in a day" rule

**1 日で end-to-end の数字が出る状態**を作る。完璧主義者は 1 sheet に 1 週間かけて、最後まで全体が見えない。

#### Day 1 の到達点

- 月次 60 ヶ月の P&L (revenue / COGS / OpEx / EBITDA)
- 簡易 BS (cash, debt, equity)
- 簡易 CFS (CFO, CFI, CFF)
- Cash balance / Runway 自動計算
- BS check, CF check は green

#### 後日 refine する箇所

- Driver tree の精緻化
- Cohort 分析
- Sensitivity / Scenario
- Comp benchmark
- 各セルの footnote

### 9.3 Stakeholder review の組み立て

| Review | 目的 | 観点 | 想定質問例 |
|---|---|---|---|
| Founder review | 現実性 | 顧客 / pipeline / hiring 実感 | 「来期 3 人採用、本当に集まる?」 |
| CFO/Finance | 会計整合 | 三表整合、税、為替 | 「J-GAAP / IFRS どちらで作っている?」 |
| VC/Board | 投資ロジック | runway, milestone, returns | 「次ラウンドのインパクトは?」 |
| Auditor | 基準準拠 | 監査法人 / J-SOX | 「収益認識の根拠は?」 |

各 review の前に「想定質問 5 問 + 1 行回答」を準備。これは Q&A Prep (§13.4) と統合できる。

---

## 10. 認知バイアス対策

> Kahneman, Tversky 系の cognitive bias は startup financial modeling で頻発する。**バイアスは消せないが、自覚と process で軽減できる**。

| バイアス | 症状 | 対策 |
|---|---|---|
| **Confirmation bias** | 都合の良いデータだけ集める | 反証データを 3 つ自分で挙げる |
| **Anchoring** | 初期数値が後の判断を縛る | Driver tree 設計を **数値の前に** 行う |
| **Optimism bias** | founder dynamic で過剰楽観 | Outside view (reference class forecasting) を強制 |
| **Survivorship bias** | 上場企業 comp ばかり見る | private failure cases も comp に入れる (e.g., Quibi, WeWork down) |
| **Sunk cost fallacy** | "これだけモデル作ったから..." | "今ゼロから作るならどう?" を月 1 回問う |
| **Overconfidence** | sensitivity range が狭すぎ | base ±50% を最低レンジに |
| **Status quo bias** | margin expand しない warning を軽視 | Y5 expand 0bps シナリオを必ず作る |
| **Hindsight bias** | "前回もこの曲線で当たった" | Pre-mortem を四半期ごと実施 (Klein, 2007) |
| **Availability heuristic** | 最近見た comp に引っ張られる | Comp set を最初に固定し以後変えない |
| **Recency bias** | 直近 3mo trend を 5 年外挿 | 12-24mo の trailing window で trend 取る |
| **Halo effect** | 1 指標が良いと全体を良く見積もる | 各 KPI を独立に評価 |
| **Planning fallacy** | スケジュール / コスト過小 | 過去自分の予算未達分を補正係数に |

---

## 11. Stage-appropriate Modeling

> モデルの粒度・期間・指標は stage で大きく変わる。「全 stage で同じテンプレート」は inappropriate。

### 11.1 Pre-revenue / Pre-product (Pre-Seed, Seed)

| 観点 | 内容 |
|---|---|
| 主要モデル | Bottom-up driver model (TAM × % share + 新規 cohort 想定) |
| 期間 | 24-36 ヶ月 (5 年予測は信頼性が逆に低い) |
| 焦点 | Cash burn, runway, MVP までのマイルストーン |
| 不要 | DCF, multi-year EBITDA, Comp valuation |
| KPI | MAU, paid pilot, design partner 数 |

「5 年予測 < 3 年予測の方が信頼性高い」 — Pre-revenue で 5 年先を出すと「fiction」と扱われる。

### 11.2 Early Revenue ($0-1M ARR) (Seed, Pre-Series A)

| 観点 | 内容 |
|---|---|
| 主要モデル | Cohort + bottom-up |
| 期間 | 3-5 年 |
| 焦点 | CAC payback、cohort retention、PMF 検証 |
| KPI | Logo retention, ARR retention, NPS, magic number (粗) |
| 注意 | Range で示す (median ± 50%)、point estimate は noisy |

### 11.3 Growth ($1-10M ARR) (Series A, B)

| 観点 | 内容 |
|---|---|
| 主要モデル | Bottom-up + Top-down 突合、segment 別 P&L |
| 期間 | 3-5 年 |
| 焦点 | Magic Number, Burn Multiple, Rule of 40, NRR |
| KPI | ARR growth, NRR, gross margin, S&M efficiency |
| 注意 | Comp benchmarking が機能し始める。中央値以下なら投資判断厳しい |

### 11.4 Scale ($10M+ ARR) (Series C)

| 観点 | 内容 |
|---|---|
| 主要モデル | IB-style integrated 3-statement model |
| 期間 | 5 年 + DCF terminal value |
| 焦点 | Path to profitability, Rule of 40, expansion economics |
| KPI | GM, OpEx leverage, FCF margin, ROIC |
| 注意 | Quarterly forecasting / re-forecasting cycle 必須 |

### 11.5 Pre-IPO

| 観点 | 内容 |
|---|---|
| 主要モデル | GAAP / IFRS 厳密準拠 (J-GAAP も並列で `07_japan_specifics.md`) |
| 期間 | 5 年 + DCF |
| 焦点 | Internal control, J-SOX 整合、quarterly KPI dashboard |
| KPI | 監査準拠の財務指標、IR 想定問答 |
| 注意 | revenue 認識基準 (ASC 606 / IFRS 15)、SBC 開示、segment reporting |



## 12. Smell Test (直感的 sanity check)

> 「数式が合っていても、現実感がない数字はモデラーが負ける」。**直感は数式が見落とす矛盾を捉える**。3 つの smell test を最終 review 前に必ず通す。

### 12.1 「経営者の食卓テスト」

これらの数字を creator の家族 / non-finance な友人に説明できるか。

#### 例

「Y3 で月 ¥100M 売上」を、不動産業界の友人に「うちのマンション 50 戸を毎月売る感じ」と翻訳できるか。
「Y5 で 200 名採用」を「中規模学校 1 つ作る感じ」と翻訳できるか。

→ 数字の桁感が「**普通の人にとって極端ではない**」かを確認する手段。極端なら理由を説明できないと、シニアにも刺さる。

### 12.2 「3 年後の世界の絵」

仮置きが成立した時の世界の解像度。

#### 質問 5 連

1. その時の **顧客リスト** トップ 10 を 30 秒で挙げられるか
2. 競合は **何をしているか** (静観 / 対抗 / 撤退)
3. **採用市場** で何が変わっているか (給料 / 競合 / リモート)
4. **macro** で何が前提か (金利 / 為替 / regulation)
5. **自社プロダクト** が何を新たにできているか (feature roadmap)

→ 5 つを描けないなら、それは数字の話ではなく fiction。

### 12.3 「If you're right, who loses?」

自社の成功は誰の market を奪うか。ゼロサムでないなら TAM expansion 仮定が必要。

#### 例

| シナリオ | Loser | 検証 |
|---|---|---|
| Salesforce competitor | Salesforce, HubSpot | これらが市場対応せず席を譲る前提? |
| 業界初 (no incumbent) | manual workflow / Excel / paper | TAM expansion (新需要) を量で示す |
| Marketplace 新規 | 既存 fragmented players | network effect が局地で出る理由 |

「Loser がいない」は market が無い signal。「Loser が大手 1 社」は対抗速度が脅威。

---

## 13. Documentation & Defendability

> モデルの 30% 程度は documentation。**3 ヶ月後の自分が読んで意図を再現できる**ことが基準。

### 13.1 Assumption Log の必須項目

§1.2 で定義した 8 列 (Variable, Current Value, Tier, Source, Date, Confidence, Sensitivity, Owner) に加え、以下 2 列も推奨:

- **Last Validated Date**: 最後に source 元と照合した日
- **Validation Method**: 「電話確認」「URL fetch」「契約書 PDF 確認」など

### 13.2 Decision Log

数式や構造選択の **why** を記録。

```
2026-04-10  Q vs M periodicity      → 月次採用 (理由: hiring lag が月次で意味)
2026-04-12  CHOOSE vs SWITCH        → CHOOSE 採用 (Excel 古い版互換)
2026-04-15  GP 算出 (with/without service)  → GP は software のみ。service は別 row
2026-04-20  CAC 算出に SDR 給与含める? → 含める (Bessemer 定義に合わせる)
```

意思決定 1 件あたり 1 行で十分。半年後の引継ぎで「なぜこう決めた?」の議論を 5 分で終わらせる。

### 13.3 Version Log

```
v1.0  2026-04-15  first draft, base only
v1.1  2026-04-22  Bessemer 2024 benchmarks 反映
v1.2  2026-05-02  CRO Aさんヒアリング後の AE productivity 修正
v1.3  2026-05-10  Lead VC review 反映 (CAC payback 厳格化)
v2.0  2026-06-01  Series A close 後の actual 反映 + Y3 forecast extend
```

各バージョンで `git tag` のように **不可逆な保存版** を Drive / Notion に残す。

### 13.4 Q&A Prep (30 問)

シニアレビュー / Board / DD で必ず聞かれる質問は 30 問程度。1 文 (時に数字付きで 2 文) で答えを準備する。§18 で 30 問を提供する。

---

## 14. IB / VC / PE で実際に学ぶ tacit knowledge

各業界で 1 年目アナリストが叩き込まれる craft。スタートアップ CFO / FP&A はこれらの ~半分を流用できる。

### 14.1 IB Analyst が 1 年目で叩き込まれる

| 規律 | 内容 |
|---|---|
| **Color coding 規律** | Blue = hardcoded input, Black = formula, Green = link to other sheet, Red = error/check (Macabacus 標準) |
| **Footnote discipline** | 全 hardcode / source-derived 数値に footnote 番号 |
| **Comp scrub** | 異常値の除外 (e.g., M&A directly affected EV/Sales が outlier) |
| **Tear sheet 作成** | 1 ページに圧縮した会社 1 ページ summary (revenue, EBITDA, margin, multiple, comp range) |
| **Print check** | A3 / A4 で印刷した時に 1 row が 1 page に収まるかチェック |
| **MD review prep** | "Senior partner が 5 分で見抜く" 想定で穴を潰す |

### 14.2 VC Associate が 1 年目で学ぶ

| 規律 | 内容 |
|---|---|
| **TAM 健全性検査** | TAM = (target customers × ASP × penetration) で 3 通り計算、近い値か |
| **"1% of TAM" 思考の罠** | 「1% 取れる」は何の根拠もない。share gain の物理的メカニズム必要 |
| **Founder reference check** | 信頼性は人 × 過去実績 × 自社 narrative の triangulation |
| **Investment memo 構造** | Why now? / Team / Market / Product / Traction / Financials / Risks (Sequoia / Bessemer 共通) |
| **"Pre-mortem"** | "5 年後この投資が失敗していたら、何が原因だったか" を上場前に書く |

### 14.3 PE Analyst が 1 年目で学ぶ

| 規律 | 内容 |
|---|---|
| **LBO model integrity** | Debt schedule、interest accrual、revolver、PIK の循環参照管理 |
| **Debt covenant check** | DSCR, ICR, Total Leverage が covenant 内か全期間で機械チェック |
| **Operating model bridge** | Bottom-up operating model と Top-down LBO model の差分 reconciliation |
| **Returns table の triangulation** | IRR, MoIC, equity check が 3 通り計算で一致するか |
| **Sources & Uses 整合** | Funding sources = total uses が 1 円単位で一致 |



## 15. ケーススタディ集

### Case 1: Series A SaaS の hockey stick を sniff out する

**状況**: Series A 投資検討中。Founder pitch deck の forecast:

| Year | ARR ($M) | YoY |
|---|---|---|
| Y1 (実績) | 1.0 | n.a. |
| Y2 (来期) | 3.0 | +200% |
| Y3 | 9.0 | +200% |
| Y4 | 22.0 | +144% |
| Y5 | 45.0 | +105% |

**Sniff out 手順**:

1. **Y1 → Y5 で 45x。Bessemer T2D3 model (Triple, Triple, Double, Double, Double = 144x の理想) と比較**: T2D3 の Double phase は通常 Y4-Y5 で起きる。Y2 から triple は早すぎる
2. **Y2 で +200% = $3M ARR** を実現する driver を確認: Y1 末 $1M に対し net new $2M。AE 何名で?
3. **AE productivity** を質問: Year 1 AE 1 名で $1M 売ったとして、Y2 で $3M 売るには AE 3-4 名必要。Y1 末から Y2 末までに hire できる?
4. **Sales cycle**: B2B SaaS で 6mo 想定なら、Y2 上半期に $2M pipeline closed が必要 = $10M+ pipeline 必要
5. **Marketing demand gen**: $10M pipeline = 200-400 SQL = MQL 2,000-4,000

**結論**: Y2 +200% を実現する driver が pipeline / hiring / demand-gen 全てで stretched。Y2 は base $1.8-2.2M (+80-120%) が現実的、後段も全部 30-50% 下方修正。Down-revised Y5 ARR = $20-25M。

### Case 2: Marketplace の take rate 拡大シナリオが過剰楽観な理由

**状況**: GMV $100M の Marketplace が take rate 5% → 12% に Y3 で上げる前提

**問題点**:
1. **Take rate は競争で抑えられる**: Etsy ~6.5%, eBay ~10-13%, StubHub ~25% (chasm)。事業モデル / ロックイン度合で上限が決まる
2. **Take rate を上げると seller が逃げる**: Amazon Marketplace の seller revolt が好例
3. **Take rate +700bps は $7M の seller transferred value**: これは seller側でも交渉対象になる
4. **Comp data**: Mercari, Coupang, Doordash 等の take rate trajectory は 1-3 年で +100-200bps が現実

**Reframe**: Y3 take rate 6.5-7.5% (中央値 +200bps が limit)、それ以上は **add-on revenue** (advertising, fulfillment, financing) で上乗せ。Build separate revenue line。

### Case 3: Bottom-up と top-down が 30% 乖離した時の reconciliation

**状況**:
- Bottom-up Y5 ARR: $25M (segment × ASP × penetration の積み上げ)
- Top-down Y5 ARR: $18M (TAM $1.2B × 1.5% share)

**Reconciliation 手順**:
1. Bottom-up の segment 別 ASP / 顧客数を確認
2. Top-down の TAM 推定が **3 通り** ある (top-down macroeconomic, sum-of-segments, customer count × ASP) — どの推定か確認
3. 差は何で生まれているか:
   - Bottom-up が ICP を broaden しすぎ (本来 SMB のみが Mid + Enterprise も含めている)
   - Top-down が ICP を narrow しすぎ (Enterprise のみ counted、Mid 除外)
4. ICP 定義を共通化して再計算
5. Bottom-up $25M → $20M に下方、Top-down $18M → $19M に上方 = $20M で合意

**Rule**: 5-10% 以内が docking、それ以上は driver tree の論理整合を再点検。

### Case 4: Comp 5 社中 1 社が outlier の時の処理

**状況**: SaaS Comp 5 社の NRR
- A: 110%
- B: 115%
- C: 108%
- D: 175% (outlier — Snowflake-like)
- E: 112%

**処理オプション**:
| Option | NRR Median | Comment |
|---|---|---|
| Median (5 社含む) | 112% | OK だが outlier 効果薄い (median は robust) |
| Mean (5 社) | 124% | NG (D に引っ張られる) |
| Median (D 除外) | 111% | より合理的 |
| Median + footnote D | 112% (D は別建てで参考) | Best practice |

**Rule**: Outlier は除外ではなく **別建てで参考表示**。除外理由 (data warehouse usage-based の特異性) を明記する。

### Case 5: Founder が「業界平均の 2x で hire できる」と主張した時の対応

**状況**: 「我々のブランドで $200K AE が $150K で取れる」と founder。

**Pushback 手順**:
1. **過去実績で検証**: 過去 12mo の hire 実績を見る。$150K で取った AE は何名? その後 retention は?
2. **市場調査**: Glassdoor, levels.fyi, payscale で AE comp distribution 確認 ($150K は P25 帯か)
3. **Quality risk**: 安く取れる = 経験浅い / 競合 offer ない、retention や productivity に出る
4. **Modeling treatment**: Base case は $200K (市場中央値)、Founder claim ($150K) は upside scenario (T4) で並列表示
5. **Stress test**: $150K hire の attrition Y1 で 30%+ になる確率は 40%、そのコストを mode化

**Rule**: Founder の subjective view は否定せず **並列 scenario で扱う**。否定するとモデル提供拒否、並列表示すると会話が成立する。

---

## 16. モデラー成熟度モデル (Maturity Model)

### Lv1: 数式が壊れない

| 指標 | Lv1 |
|---|---|
| BS check | green |
| CF check | green |
| 三表整合 | retain earnings が IS → BS で整合 |
| sum check | 全 row の Σ が consistent |
| 循環参照 | 意図的なもの以外なし |

→ 「壊れていない」モデル。レビューに耐える条件。

### Lv2: 三表が整合する

| 指標 | Lv2 |
|---|---|
| Lv1 | + |
| 月→Q→Y aggregation | 完全整合 |
| Working capital | DSO, DPO, inventory days で driver-based |
| Capex / Depreciation | schedule化、逆計算可能 |
| Tax | NOL carryforward / DTA 反映 |
| Equity / Debt | round-by-round で建てられる |

→ 「会計基準準拠」のモデル。CFO レビュー OK。

### Lv3: Sensitivity / Scenario が組める

| 指標 | Lv3 |
|---|---|
| Lv2 | + |
| Tornado analysis | top 5 driver 識別 |
| Scenario manager | base / up / down 切替 (CHOOSE / SWITCH) |
| 1D / 2D data table | 主要 driver で実装 |
| Stress test | 2 シナリオ以上 |

→ 「意思決定支援」のモデル。Board / Lead VC レビュー OK。

### Lv4: Comp benchmark で calibrate できる

| 指標 | Lv4 |
|---|---|
| Lv3 | + |
| Comp set | 5-10 社、quartile 表示 |
| Maturity curve | 沿わせ確認 |
| Tier 4 明示 | speculation セルが明確に分離 |
| Outside view | reference class forecasting 適用 |

→ 「プロのアナリスト」レベル。VC partner レビュー OK。

### Lv5: Stress test で kill scenarios を提示できる

| 指標 | Lv5 |
|---|---|
| Lv4 | + |
| Pre-mortem | "5 年後失敗していたら" を文書化 |
| Default Alive analysis | Paul Graham 流の break-even path |
| Tail scenarios | 4 つ (concentration, funding closure, macro, regulatory) |
| Q&A 30 問 | 全問 1 文回答準備 |
| Decision triggers | 各 scenario で何 trigger で何 action |

→ 「シニアパートナー / 監査」レベル。最終的な防御可能性を持つ。



## 17. 100 Maxims (一行格言集)

> モデラーが手元に置く格言集。`scripts/build_model.py` / `sanity_checks.py` の review prompt から参照される。

### A. 根拠主義 (Justification, 1-15)

1. 数字を仮置きする前に driver tree を描け。
2. 同業の中央値を見ずに数字を出すな。
3. Tier 1 (実績) を 30%、Tier 4 (推測) を 10% 未満に保て。
4. 「なぜこの数字?」に 1 行で答えられないセルは消せ。
5. 出典のない constant はバグである。
6. Average の前に Median を見よ、Mean は外れ値で歪む。
7. GAAP / non-GAAP / pro-forma を混ぜるな。
8. 「業界平均」と書く時は、何社の median か明記せよ。
9. Comp set は 5-10 社で固定し、後から増減するな。
10. 1 つの仮置きには 3 つの独立データ点を取れ。
11. 「Top-quartile を base に」は反証可能性なき argument だ。
12. Speculation は明示マーカー (SPEC / ??) で隔離せよ。
13. Founder の希望は否定せず upside シナリオに別建てせよ。
14. ヒアリング ベースの仮置きは「誰、いつ、何を」を残せ。
15. 出典 URL は dated archive を残せ (リンク切れに備えて)。

### B. ベンチマーク (Benchmark, 16-30)

16. Snowflake の NRR 178% を base に置くな。
17. Series A の 80% は中央値以下に着地する。
18. Best-in-class は exception、median が rule。
19. 業界の **量子化** (median, P25, P75, P5/P95) を持ち歩け。
20. SaaS pure software の GM 上限は 85% と心得よ。
21. CAC payback < 6mo は SMB でのみ成立する。
22. Magic Number 1.5 は viral PLG でのみ実現する。
23. NRR 150% は usage-based で熱狂的 expansion 局面のみ。
24. Comp の outlier は除外ではなく **別建て参考表示** せよ。
25. Geography (JP / US / EU) で comp を分けよ、混ぜるな。
26. ICP (SMB / Mid / Ent) を揃えずに comp を語るな。
27. Pre-IPO の S-1 は **直近 8 quarter** だけ見ろ、それ以前は noise。
28. Bessemer / OpenView / ICONIQ の最新 release を四半期ごと更新せよ。
29. KeyBanc SaaS Survey の Q&A 詳細は driver 単位で integrate せよ。
30. 自社実績 12mo を持つなら、それを最優先 reference にせよ。

### C. Forecast / 楽観バイアス (Forecast & Optimism, 31-50)

31. Year 3 で 10x を信じるな。
32. Hockey stick は driver の理由なく曲がるグラフだ、即疑え。
33. Volume × Price × Margin × NRR の同時 best は確率 ~1-2%。
34. Inside view (自社特殊) より Outside view (comp) を優先せよ。
35. Kahneman の Reference Class Forecasting を実行せよ。
36. Worst case は 2 つ以上の同時 negative event を想定せよ。
37. "Plan for the worst, sell the best" は同じファイルで管理するな。
38. Pitch Base ≠ Internal Plan、後者は前者の 60-70% を base に。
39. T2D3 (Bessemer 理想) は 10% の SaaS でしか実現しない。
40. Bottom-up と Top-down の差を 5-10% 以内に。Plug を作るな。
41. Linear ramp は素人、S-curve が現実。
42. First $1M ARR には 6-30mo かかる、業態次第。
43. 月次 → Q → Y の集計で seasonality を消すな。
44. 「将来コストが下がる」は具体的な vendor / contract を示せ。
45. ASP 上昇と Volume 拡大の同時実現は negative correlation を考慮せよ。
46. Pipeline 4-5x が closed 1x、conversion を rev で表すな。
47. 5 年予測 vs 3 年予測、後者の方が信頼性高いことを忘れるな。
48. "Proof by adjective" を許すな (e.g., "robust pipeline" の数値化要求)。
49. Win rate を 30%+ で 5 年維持する仮置きは要 reality check。
50. Pricing increase は契約更改タイミングのみ機能、契約年数を確認せよ。

### D. Cost / Hire (51-65)

51. Variable cost の 60-70% は実態として固定費だ。
52. OpEx の 70-85% は人件費、Headcount × FLC で決まる。
53. Fully Loaded Cost = 給与 × 1.3 〜 1.5 (JP)、× 1.4 〜 1.6 (US)。
54. Job posting → Hire の lag 2-4mo を入れずに採用計画を立てるな。
55. Offer accept rate 60-70% を base に置け。
56. 営業 ramp は 6-9mo、それ以下は楽観。
57. Engineer ramp は 3-6mo。
58. Annual attrition 15-25% は SaaS の中央値、10% 未満は楽観。
59. 「業界平均の 2x で hire できる」は upside scenario 扱いせよ。
60. CRO / VPM hire の lag は 6-9mo、計画から外すな。
61. Salary range の P25-P75 を持って comp data を見ろ。
62. Equity grant は希釈効果を Cap Table で必ず映せ。
63. Onboarding ramp は **業務関数別** に違う、一括 100% にするな。
64. Hiring の geographic distribution (リモート / オフィス) で給与構造変わる。
65. JP の社会保険料率 ~14% を給与に上乗せせよ。

### E. Cash / Runway (66-75)

66. Cash is reality, P&L is opinion.
67. Net Burn ≠ Operating Loss。CFO + CFI を見ろ。
68. SBC は cash burn から除外せよ (non-cash)。
69. Working capital 変動は burn の 5-15% を占めうる。
70. Capex を OpEx と分離し、CFI に正しく置け。
71. 前受金 (deferred revenue) は cash positive、P&L には現れない。
72. Static burn 仮定の runway 計算は楽観の極み。
73. Runway 12mo を切ったら bridge round を検討せよ。
74. Term sheet → 着金まで 6-10 週、cash 0 月前に始めるな。
75. Default Alive (Paul Graham) で 12mo 以内に CF break-even の path を持て。

### F. Sensitivity / Scenario (76-85)

76. ±10% sensitivity は飾り、±30-50% で意味あり。
77. Tornado top 5 driver で意思決定 80% が決まる。
78. High Impact × High Uncertainty だけ flex せよ。
79. Best case 同時実現の probability を計算せよ。
80. Stress test は 4 種 (concentration / funding / macro / regulatory) を必須に。
81. 各 scenario に「いつ気づくか」「何 trigger」を 1 行で書け。
82. Driver 間の correlation を Cholesky で扱え (本格 PE 案件)。
83. Bear ≠ Worst, Worst は 2 negative events 同時。
84. 1D / 2D Data Table は input cell が separated で同 sheet にあること。
85. シナリオ ID (`Scen_ID`) は CHOOSE / SWITCH で集中管理せよ。

### G. Documentation / Process (86-95)

86. 3 ヶ月後の自分が読んで再現できるかを基準に書け。
87. Color coding (Blue input, Black formula, Green link) を厳守せよ。
88. Footnote のない hardcode はバグである。
89. v0 は 1 day で end-to-end が出る状態を作れ。
90. Decision Log を 1 行ずつ残せ、半年後の引継ぎが速くなる。
91. Version Log で v1.0, v1.1, v2.0 を不可逆に保存せよ。
92. Q&A Prep 30 問に 1 文回答を用意せよ。
93. Stakeholder review は 4 種 (Founder / CFO / VC / Auditor) で角度を変えて。
94. Pre-mortem を四半期ごと、自分で実施せよ。
95. シナリオ切替後に master check が green であることを確認せよ。

### H. Cognitive / Smell test (96-100)

96. Confirmation bias 対策に反証データ 3 つを自分で挙げよ。
97. 経営者の食卓テスト (家族に説明できるか) で桁感を確認せよ。
98. "If you're right, who loses?" を 3 名挙げよ。
99. 「3 年後の世界の絵」を 5 質問で描けない数字は fiction だ。
100. 完璧主義者の罠 — 1 sheet に 1 週間かけるな、全体 1 day で動かせ。

---

## 18. シニアレビュー想定問答 30 問

> VC partner / PE MD / 監査 senior / Board が 5 分で聞いてくる質問を 30 問。各問に **1 文 (時に 2 文 + 数字)** で答える準備が「シニアレビューに耐える」モデルの defining trait。

### A. 数字の出所 (1-6)

**Q1. これらの数字の出所は?**
A. ARR と churn は当社 12mo 実績、NRR / Magic Number / GM は Bessemer 2024 中央値、CAC payback は CRO Aさんヒアリング (2026-03)。Tier 表で隔離。

**Q2. 業界 comp は何社 / どこから?**
A. SaaS Mid-Market 5 社 (X, Y, Z, A, B) を S-1 / Q-10 / Bessemer dataset から。Outlier 1 社 (Snowflake-like) は別建て参考表示。

**Q3. NRR 130% の根拠は?**
A. 中央値 110% (Bessemer) より高めだが、当社は usage-based pricing で comp Y 社 (NRR 132%) と構造類似。期待 NRR は **Tier 3 (CRO ヒアリング)** 由来で confidence Medium。

**Q4. Median と Mean を区別しているか?**
A. はい。本モデルは median 採用、mean は outlier (top quartile) で歪むので除外。差は脚注 N8 に記載。

**Q5. GAAP / non-GAAP どちら?**
A. GAAP base、Adj. EBITDA は SBC を除く non-GAAP で並記。SBC は revenue の 8-12% (公開 SaaS 中央値)。

**Q6. 為替前提は?**
A. USD/JPY ¥150 (2026-04 spot)、Sensitivity で ¥130-170 で振っている。USD 売上は 30% 比率なので EBITDA 影響は ±¥20M/year。

### B. 成長前提 (7-13)

**Q7. Year 3 で +200% growth の driver は?**
A. AE 4→8 名追加 + Mid-Market segment 開拓 (ACV 5x)。Pipeline 容量 / hiring lag は別 sheet に展開済。

**Q8. なぜ comp X より高い growth?**
A. 当社は ICP が Enterprise (ACV $25K vs comp X $5K)、initial 6 deals が 30% revenue を occupy。一定の lumpy growth が想定。

**Q9. Hockey stick じゃないか?**
A. Y2 で +160%、Y3 で +115%、Y4 で +90% の **decelerating curve**。各 Y で driver (AE / channel / segment) を 1 文で説明可能。

**Q10. NRR 110% を 130% に上げる根拠は?**
A. Y3 から Enterprise tier (ACV $50K+) を 30% mix に上げる前提。3 年の cohort で expansion 200% が前提なら NRR 122%、保守的に 130% で計算。

**Q11. Churn が 5% から 3% に下がる根拠は?**
A. Customer Success team の hire (Y2 末 5 名)、product 機能 X が retention に寄与。Comp Y 社が同期間で 4% → 2% を実現した。

**Q12. ASP +20% を 3 年連続できるのか?**
A. Y1-Y2 は契約更改で +5% (existing)、Y3 は新規 enterprise tier introduction で **新規 mix shift** での見かけ上 ASP 上昇 (既存 customer の price hike ではない)。

**Q13. Y5 ARR $100M を 7 年で達成できる probability は?**
A. Bessemer "Path to $100M" の中央値は 84mo (= 7 年)、当社 trajectory は中央値 ±10% に位置。確率推定 30-40%。

### C. コスト / 収益性 (14-20)

**Q14. GM が 70% から 78% に Y3 で expand する根拠は?**
A. AWS reserved instance への移行 (Y2 末) と support service 比率削減 (10% → 5%)、年 +200-300bps の改善は SaaS pure-software median と整合。

**Q15. S&M efficiency は誰の数字?**
A. Bessemer "Magic Number 0.7" を base、当社実績 0.5 → 0.7 へ Y3 で改善。CMO Bさん前職での channel 立ち上げ実績を参考。

**Q16. Headcount cost の前提は?**
A. JP 給与 × 1.4 (FLC、社保 14% + 設備 + 賞与含む)、US 給与 × 1.5。Senior Engineer FLC ¥14M、Senior AE FLC ¥21M (OTE 含む)。

**Q17. なぜ Y3 で profitability に近づく?**
A. Rule of 40 を達成 (Growth 30% + Op Margin +10% = 40%)、scale で OpEx leverage が出る。S&M 比率 Y1 70% → Y3 40%、R&D は 30% → 20%。

**Q18. 採用 lag を入れているか?**
A. 入れている。Job posting → onboarding 4mo、ramp 6-9mo (営業)。Y2 末に 30 名計画なら Y2 Q1 末から募集開始の前提。

**Q19. Attrition は何 % で置いているか?**
A. 年率 18% (SaaS JP 中央値)。Y3 末 50 名計画なら net hire = gross hire - 9 名 (attrition) を反映済。

**Q20. CAC payback はどう計算している?**
A. 月次 New ARR / 月次 S&M で逆算した平均値。GM 後ベース、CAC = Sales + Marketing fully loaded、payback months = CAC / (ARR × GM / 12)。

### D. Cash / Funding (21-25)

**Q21. Runway はいくつ?**
A. 22 ヶ月 (現在 cash ¥800M / 月平均 net burn ¥36M)。Burn は hiring に伴い Y2 で ¥45M に上昇する dynamic 計算。

**Q22. Funding gap は?**
A. Y3 Q4 で cash 8mo runway を切る計算、Series B (~¥2-3B) を Y3 Q1 にクローズしないと bridge 必要。

**Q23. Bridge round の前提は?**
A. Base ケースに含めず。Bear ケースで $5M SAFE (cap = pre-money $80M)、Y3 末まで 8mo 延命。

**Q24. Burn Multiple は?**
A. Y2 で 1.5 (中央値帯)、Y3 で 1.0 へ改善。Bessemer の Burn Multiple framework に整合。

**Q25. P&L Loss と Cash Burn の差は?**
A. SBC ~¥30M/year (non-cash)、Capex ¥20M/year (cash out, P&L 外)、working capital ~¥10M (cash 一時的に貯まる)。差し引き Cash Burn は P&L Loss + ¥0M、ほぼ neutral。

### E. Risk / Stress (26-30)

**Q26. 何がこの会社を kill する?**
A. (1) Top customer (revenue 18%) churn + 新規 -50% 4Q、(2) Funding window 12mo closure。各々 single trigger では 6mo 延命可能、両者同時で 4mo で cash 0。

**Q27. Worst case を見せて。**
A. Top 顧客 churn + 新規 -50% + bridge を取れず。Y3 末 ARR ¥180M、runway 7mo、25 名解雇必要。Plan B は cost reduction 40% 即実施、profitability priority に切替。

**Q28. Concentration risk は?**
A. Top 5 が revenue 45%、Top 1 が 18%。Y2 内に Top 1 比率を 12% 以下にする target (新規 enterprise 4 deals で実現可能)。

**Q29. Macro recession の影響は?**
A. B2B SaaS budget -30% シナリオで new ARR -50%、churn +5pp が 6Q 続く前提。Y3 末 ARR ¥250M (vs base ¥420M)、runway 14mo、Series B raise が delay。

**Q30. このモデルの 3 つの脆弱点は?**
A. (1) NRR 130% 前提 (現実 110-115% に着地する確率 50%)、(2) AE productivity ramp 6mo 前提 (実績 9-12mo の可能性)、(3) Y3 Enterprise tier 開発 / sales-readiness の遅延リスク。3 つ全て発現で Y5 ARR は base の 60% に着地。

---

## 19. Founder 側 Wind-Down Framework — E-C-005 解消

監査 E (Strategy) finding **E-C-005** 解消: 08 章は VC 側の "kill criteria" (投資先を切る判断) を扱うが、創業者側の **operational shutdown (会社を畳む) framework** が corpus 内に不在だった。本節がそれを補完する。

> 関連: `_master_decision_tree.md §F.4` (wind-down シナリオの routing) / `07_japan_specifics.md §6.4` (日本での経営者保証ガイドライン) / `12 §7` (清算所得課税)。

### 19.1 Wind-Down Trigger (どの時点で会社畳みを検討するか)

以下のいずれか単独で「検討開始」、複数該当で「実行可能性が高い」 と判断する。

```
A. Cash runway < 3 ヶ月、かつ次回 funding 見込みなし
B. Founder の燃え尽き / health issue が継続
C. 主要顧客 1 社で revenue 50% 超を喪失 (concentration の clip)
D. 経営者保証付き debt の covenant breach が不可避
E. Co-founder 紛争が解消不可能 (信頼関係の崩壊)
F. Product-market fit が 3 年経っても見えない (10 §15 Case 1 参照)
G. Regulator action / 訴訟敗訴で事業継続が困難
```

「runway < 3 ヶ月」 は trigger としては最も遅い指標。早期 trigger (B〜G) のほうが founder の選択肢が広い段階で検討できる。

### 19.2 Wind-Down Path 比較

| Path | 期間 | 直接コスト | Founder 影響 | 投資家分配 | Use case |
|---|---|---|---|---|---|
| 解散 (清算) | 6-12 ヶ月 | ¥1-3M | 経営者保証ありなら個人弁済義務 | 残余財産から優先株 → 普通株 | 黒字解散・債務超過なし |
| 民事再生 | 12-18 ヶ月 | ¥10-30M | DIP financing で再建可能 | 再生計画に従う | 事業継続に価値あり、債権者と合意可能 |
| 破産 (法人) | 6-9 ヶ月 | ¥0.5-2M | 信用喪失、再起 5-7 年 | 通常ゼロ | 債務超過、再建不能 |
| 個人破産 (founder) | 6-12 ヶ月 | ¥0.5-1M | Credit 履歴 5-10 年 cripple | — | 経営者保証発動後の最終手段 |
| Acqui-hire | 3-6 ヶ月 | 取得側負担 | Founder は買い手で雇用継続 | 通常 founder 取り分あり | チームに value、product に value 限定 |
| Asset Sale | 3-6 ヶ月 | ¥3-10M | IP / 顧客リスト売却後に解散 | 売却収入を分配 | 資産に value あり、事業は continuation せず |
| Ramen Profitable Pivot | 継続 | ¥0 | Growth 諦め、自走 | 投資家には IRR 期待値はゼロ | revenue は自走可能、growth funding 不可 |
| Wind-down (no formal) | 3-6 ヶ月 | ¥0.5-1M | 信用に軽微 | 残余 cash を返還 | 債務なし、株主全員合意 |

### 19.3 Wind-Down 時の財務責任 (founder が負うもの)

#### 19.3.1 経営者保証 (日本特有)

- JFC / 制度融資 / 銀行プロパー融資の多くで founder の **連帯保証** を要求される。
- 2023 改定 「**経営者保証ガイドライン**」 — 一定要件下で経営者責任を限定可能:
  - 法人と個人の資産分離が透明
  - 法人単独で返済可能性を示せる財務基盤の整備努力があった
  - 適時開示など lender との情報非対称が小さい
  - 弁護士 / 会計士の助言を受けて手続きを進めている
- Wind-down を決める前に必ずこのガイドライン適用判断を専門家と。`07 §6.4` 参照。

#### 19.3.2 投資家からの seek redress リスク

- 投資家代表訴訟 (株主代表訴訟): 取締役の任務懈怠を主張される可能性。
  - 但し「事業判断の原則 (business judgment rule)」 で守られる範囲が広い。
- 重要事項の隠蔽 / 虚偽表示があれば fraud 訴訟リスク。
- Wind-down 過程の **stakeholder 通知順** (§19.4 step 5) を守ることが防御に直結。

#### 19.3.3 従業員退職金 (法定 + 慣行)

- 法定: 「労働基準法上の解雇予告手当」 = 30 日分賃金 (即時解雇の場合)。
- 慣行: 退職金規程があれば従う。規程なしでも数ヶ月分支給が一般的 (会社の信義則)。
- 未払賃金は **租税債権・抵当権付債権に次ぐ優先弁済債権** (民法 + 労働債権)。
- 雇用調整助成金 / 求職者給付の手続支援も founder 責任の一部。

#### 19.3.4 ベンダー支払 priority

```
優先順位 (倒産・清算時):
1. 担保権付債権 (e.g. 不動産抵当)
2. 公租公課 (税・社保)
3. 労働債権 (給与・退職金)
4. 一般債権 (ベンダー / 取引先)
5. 株主 (優先株 → 普通株)
```

破産・民事再生では裁判所主導でこれが厳格に守られる。
任意清算・解散の場合でも順序を逸脱すると後で「偏頗弁済」 として取消される。

### 19.4 Wind-Down Decision Sequence (実行手順)

```
Step 1: Runway projection を厳密化 (本 file §7 cash modeling)
        - 13-week cash flow を週次で更新
        - 「Default Alive / Dead」 (Paul Graham) の判定
        - Liquidation value (固定資産 + AR - AP) を算定

Step 2: Bridge funding の最後の試行 (3 ヶ月以内に実行可否判定)
        - 既存投資家への bridge 提案 (04a §1.4)
        - SAFE による短期 cash 補強 (但し dilutive)
        - JFC 制度融資など短期 debt (但し経営者保証注意)

Step 3: Acqui-hire / Asset sale を並行探索
        - Strategic acquirer (顧客・ベンダー・競合) への打診
        - Talent acquirer (FAANG 等の technical hire 目的)
        - 期間: 3 ヶ月以内に signed term sheet が無ければ次へ

Step 4: Wind-down 形態の決定
        - §19.2 表で当てはめ (債務超過 → 破産 / 民事再生)
        - 弁護士 (倒産・破産専門) と公認会計士を起用
        - 取締役会決議 / 株主総会特別決議の議題確定

Step 5: Stakeholder 通知 (順序を守る)
        ① 取締役会 → 議事録残す
        ② 主要投資家 (board observer 含む) → 個別 call で説明
        ③ 従業員 → 全員集会、退職条件提示、Q&A
        ④ 主要ベンダー → 支払予定説明、契約終了通知
        ⑤ 主要顧客 → サービス継続 / migration plan 説明
        ⑥ 残ベンダー / 一般 stakeholder → 書面通知

        この順序を逆転させると「Founder が従業員より先にベンダーに通知した」 等で
        信頼を失い、後で投資家・従業員から訴訟リスクを引き起こす。

Step 6: 法的手続実行
        - 任意清算: 解散決議 → 清算人選任 → 残余財産分配 → 清算結了登記
        - 民事再生: 裁判所申立 → 監督委員選任 → 再生計画案 → 認可 → 履行
        - 破産: 裁判所申立 → 破産管財人選任 → 換価 → 配当 → 終結
        - 期間中は founder は協力義務、特に書類・口座情報の開示

Step 7: Founder の fresh start
        - 経営者保証残債の整理 (ガイドライン適用申請)
        - 個人破産 を回避できれば次の startup へ
        - Network で「整然と畳んだ」評価を得ることが re-up に直結
        - Lessons learned は次社の investor pitch でも legal liability にならない範囲で開示
```

### 19.5 Wind-Down と財務モデリングの接点

本 skill (財務モデリング) として wind-down に直接関わる作業:

| 作業 | 該当 file 章 |
|---|---|
| Runway 厳密化 | 本 file §7, 06 §3 (CFS) |
| Liquidation value 算定 | 13a §4 (carve-out valuation) |
| Acqui-hire の founder 取り分計算 | 04b §3 (waterfall), 04a §6 (preferred preference) |
| 民事再生 計画案の財務モデル | 06 §1-§3 全章 (3 statement re-build) |
| 経営者保証残債のシミュレーション | 11 §6, 07 §6.4 |
| 清算所得課税 / 欠損金引継ぎ | 12 §7 |
| 投資家分配 waterfall | 04b §3 |

VC 側 kill criteria (08 §4) と founder 側 wind-down trigger (本節 §19.1) は **同じ事実から異なる方向の判断** をする 2 layer。
モデラーは両方を理解した上でモデルを「PASS / WATCH / FAIL」 と「Bridge / Acqui-hire / Wind-down」 の 2 軸で読む必要がある。

### 19.6 Wind-Down Maxims (10 ヶ条)

```
M1. 「畳む決断」は早ければ早いほど founder の選択肢が多い。
M2. Default Dead を Default Alive に偽装するな。Cash 表を毎週更新せよ。
M3. Bridge は「次の bridge を呼ぶ」だけになりがち。3 ヶ月で結論を出せ。
M4. Acqui-hire は失敗ではない。Talent に value がある証明である。
M5. 経営者保証は debt 取得時に弁護士に確認、wind-down 時に再確認。
M6. Stakeholder 通知の順序を守れ。法務的にも倫理的にも。
M7. 従業員に対しては「最低 2 ヶ月分の給与 + 推薦状」 を準備せよ。
M8. Wind-down 経験は次社の investor から「リスク管理」として評価される場合が多い。
M9. 「畳まずに Ramen Profitable」 は時に最強の選択肢。Growth は諦めても会社は残る。
M10. Founder 個人破産は最終手段。経営者保証ガイドラインを必ず先に検討せよ。
```

### 19.7 Founder Wind-Down と VC Kill Criteria の対応表

| 状況 | VC 側判断 (08 §4) | Founder 側判断 (本 §19.1) | 推奨 path |
|---|---|---|---|
| Burn multiple > 3, NRR < 90% | KILL (write-off) | Wind-down trigger A | 民事再生 / Acqui-hire |
| Founder + key engineer 同時離脱 | KILL | trigger B + E | Acqui-hire 一択 |
| TAM 過大判明、SAM 縮小 | WATCH → KILL | trigger F | Pivot or Asset sale |
| 主要顧客 1 社 50% loss | WATCH | trigger C | Bridge → 黒字解散 or pivot |
| Covenant breach (債務超過接近) | KILL | trigger D | 破産 / 民事再生 |
| 訴訟敗訴 (例: 特許侵害) | KILL | trigger G | 破産 / Asset sale (IP 除外) |

両者の判断が同方向の場合 (KILL ⇔ wind-down trigger 該当) は、founder は **wind-down を機械的に進めて構わない**。
両者がズレる場合 (例: VC は「KILL」 だが founder は「continue」) は、retention call を board で先に行い、合意形成を優先する。

---

## 参考文献 (Selected References)

- McKinsey & Company, *Valuation: Measuring and Managing the Value of Companies* (Tim Koller, Marc Goedhart, David Wessels)
- Aswath Damodaran, *Narrative and Numbers: The Value of Stories in Business*
- Michael J. Mauboussin & Alfred Rappaport, *Expectations Investing*
- Daniel Kahneman, *Thinking, Fast and Slow* (Inside view / Outside view)
- Bent Flyvbjerg, "Reference Class Forecasting" (Harvard Business Review)
- Mark Suster (Both Sides of the Table) — startup forecasting / VC pitch
- Bill Gurley (Above the Crowd) — marketplace economics, take rate
- Tomasz Tunguz (Theory Ventures) — SaaS metrics, board decks
- Bessemer Venture Partners — *State of the Cloud*, *Path to $100M ARR*, Cloud 100
- ICONIQ Growth — *Topline Growth Benchmarks*, *Sales Efficiency Benchmarks*
- OpenView Partners — *SaaS Benchmarks Report*
- KeyBanc Capital Markets — *SaaS Survey* (annual)
- Paul Graham, "Default Alive or Default Dead?" (essay, 2015)
- Gary Klein — "Pre-mortem" technique
- a16z / Sequoia Capital / Bessemer — investment memo templates (公開 sample)
- FAST Modelling Alliance — *FAST Standard* (構造規範は `01a_modeling_standards.md`)

---

> このリファレンスは **craft (技芸) の正本**。`01a` (規範)、`01b` (検証 / sensitivity)、`02-08` (業務モデル)、`07_japan_specifics.md` (日本特殊) と併読することで、モデルが「数字を作る」段階から「シニアレビューに耐える」段階に進む。

