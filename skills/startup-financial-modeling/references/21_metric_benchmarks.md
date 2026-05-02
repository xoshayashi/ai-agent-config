---
name: metric_benchmarks
description: 業態 × Stage × Quartile (top/median/bottom) の 3 次元 benchmark matrix 正本。SaaS / Marketplace / Fintech / D2C / Hardware / Bio / AI Foundation Model 等の各 metric について、Pacific Crest / OpenView / KeyBanc / ChartMogul / SaaSCapital 等の Tier 1 source から canonical 値を抽出。sanity_checks S 系の applicability + 閾値、IC memo の justification、_master_decision_tree §C の四段ゲート計算に使用される SSoT
type: reference
priority: P0
related: [02_saas_metrics, 03_business_models, 09_market_sizing, 14_ipo_readiness, 18_customer_value_and_pricing, _stress_framework, _master_decision_tree, _terminology]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 各業態 × stage × quartile の **3 次元 benchmark matrix** の canonical 値はすべて本書に集約。`02_saas_metrics §8` の SaaS benchmark / `03_business_models` の Marketplace / Fintech / D2C / Hardware / Bio / AI 横断 benchmark / `09_market_sizing §6` の TAM 現実性 benchmark / `14_ipo_readiness` の IPO 適格 benchmark は、すべて本書に **数値の正本** を持ち、各 reference 側は「定義 + 解釈」を担当する。
- **Routing**: [`_master_decision_tree.md §C (投資判断)`](_master_decision_tree.md) の四段ゲート計算で「median 比較」「top quartile 判定」をする際、必ず本書を引く。`scripts/sanity_checks.py` の S1-S10 判定の閾値はすべて本書 §13 の整合表を参照する。`13_IC_Memo` の "Performance vs Industry Benchmark" 表は §14 のテンプレを使用する。
- **Self-review**: 本書に記載される数値を引用する際は [`_self_review_protocol.md §8`](_self_review_protocol.md) の "Benchmark citation check" (Tier / sample size / vintage / cherry-picking 検査) を実行する。
- **関連 reference**: `02_saas_metrics` (定義) / `03_business_models` (業態 taxonomy) / `09_market_sizing §6` (TAM 現実性) / `14_ipo_readiness §3` (上場適格性 benchmark) / `18_customer_value_and_pricing §3.1` (pricing realization) / `19_ma_exit_for_founders §2, §7` (exit MOIC / IRR benchmark) / `_stress_framework §4` (applicability matrix) / `_master_decision_tree §C` (4 段ゲート) / `_terminology §6` (用語整合)。

> 用語注: 本書では「Operating System / OS」を避け、「価格決定の仕組み」「pricing 体系」「処理系」「経営の仕組み」と表現する (個人ルール)。時系列・量比較の数値データは原則として表形式 (markdown table) に揃える。

> 出典規律: 本書の全 benchmark には **Source name + version + N (sample size) + 取得年 + Tier** を付す。複数ソースが矛盾する場合は両方併記、平均化はしない。Tier 4 (anecdotal) の数値は **IC memo / 投資判断には使用しない**、内部推測の参考のみ。

---

# 21. Metric Benchmark Matrix — 業態 × Stage × Quartile 正本

> 本ドキュメントは、startup financial modeling skill の reference 群 (00-19) 横断で「benchmark とは何か」を 1 か所に集約した正本である。
>
> **対象読者**: Claude (xlsx KPI heatmap / IC memo "Performance vs Benchmark" section 生成エージェント)、investor、founder、それを review する人間 IC reviewer / VC partner。
>
> **Scope (INCLUDE)**: SaaS / Marketplace / Fintech / D2C / Hardware / Bio / AI Foundation Model の 7 業態 × Pre-Seed / Seed / Series A / Series B / Series C+ の 5 stage × Top quartile / Median / Bottom quartile の 3 quartile = 7 × 5 × 3 = 105 cell の数値正本、加えて市場サイジング・資本効率・exit MOIC・IPO 適格の cross-cut benchmark。
>
> **Scope (EXCLUDE — 別 reference 担当)**: metric の **定義** (定義は `02_saas_metrics §2-7` / `03_business_models` / `_terminology §6` を参照、本書は数値のみ)、IC memo の thesis 構成 (`08_investment_thesis`) 、xlsx 構築手順 (`scripts/build_model.py`)。
>
> **数値の出典**: 本文中に Tier (1-4) + Source name + version + N + year を明示。Pacific Crest 2024 / OpenView 2024 / KeyBanc 2024 / ChartMogul 2024 / SaaSCapital 2024 / Bessemer State of Cloud 2025 / a16z portfolio analysis / Pitchbook NVCA Venture Monitor / SRS Acquiom M&A Deal Terms / BIO Industry Report / 各社 IR 等。

---

## 目次

1. [Why benchmark matters](#1-why-benchmark-matters)
2. [Benchmark Source Authority Hierarchy](#2-benchmark-source-authority-hierarchy)
3. [Update Cadence](#3-update-cadence)
4. [SaaS Metric Benchmarks](#4-saas-metric-benchmarks)
5. [Marketplace Metric Benchmarks](#5-marketplace-metric-benchmarks)
6. [Fintech Metric Benchmarks](#6-fintech-metric-benchmarks)
7. [D2C Metric Benchmarks](#7-d2c-metric-benchmarks)
8. [Hardware Metric Benchmarks](#8-hardware-metric-benchmarks)
9. [Bio / Biotech Metric Benchmarks](#9-bio--biotech-metric-benchmarks)
10. [AI / Foundation Model Metric Benchmarks](#10-ai--foundation-model-metric-benchmarks)
11. [Market Sizing Benchmark Patterns](#11-market-sizing-benchmark-patterns)
12. [Capital Efficiency Benchmarks](#12-capital-efficiency-benchmarks)
13. [Sanity Check Integration](#13-sanity-check-integration)
14. [IC Memo Integration](#14-ic-memo-integration)
15. [11_KPI_Dashboard 拡張](#15-14_kpi_dashboard-拡張)
16. [Mini Cases (Real-world)](#16-mini-cases-real-world)
17. [関連 reference との整合](#17-関連-reference-との整合)
18. [Anti-patterns](#18-anti-patterns)

---

## 1. Why benchmark matters

### 1.1 「Good vs Bad」の判断は benchmark との比較で初めて成立する

NRR 110%、Burn Multiple 1.8、Magic Number 0.9、Rule of 40 = 35、LTV/CAC = 2.5。これらの数字を単体で見ても「いい」とも「悪い」とも言えない。文脈は **業態 (SaaS か Marketplace か)、Stage (Seed か Series C か)、Quartile (top か median か bottom か)** の 3 次元で初めて決まる。

たとえば NRR 110% は:

- **Series A SaaS** の文脈では: median 110%、すなわち **平均的**。良くも悪くもない。
- **Series C+ enterprise SaaS** の文脈では: bottom quartile 100%、すなわち **平均以下**。investor から「contraction が起きている可能性は」と問われる。
- **Series Seed PLG SaaS** の文脈では: top quartile 120% に近い、すなわち **良好**。「early adopter retain がよく効いている」と書ける。

同じ 110% が、3 つの文脈で「平均」「平均以下」「良好」と異なる解釈になる。`anchoring without source` (出典のない anchoring) は IC memo / DD report で defensibility を持たない — 「私たちは強い」と言うときに、何との比較で強いのかの canonical を欠くと、reviewer から即座に弾かれる。

### 1.2 VC / fund partner との会話は benchmark 言語で行われる

VC partner / fund LP / IB MD との investor meeting / deal review において、「我々の NRR は 125% です」と単に言うのではなく「我々の NRR は 125% で、Pacific Crest 2024 SaaS Survey (N=400, Series B median 115%) の **top quartile (135%) に近い水準** にあります」と言うのが標準である。後者は出典 + quartile rank + sample size の 3 点で defensibility を持つ。前者は単なる主張に留まる。

慣習的な benchmark 言語の例:

- 「Magic Number は **top quartile**」 (= > 1.0、SaaSCapital 2024)
- 「Burn Multiple は **best-in-class** zone」 (= < 1、Sacks framework)
- 「Rule of 40 は **80+ で premium tier**」 (= top quartile pre-IPO、Bessemer State of Cloud 2025)
- 「ARR Growth は **median を 1.5x 超え**」 (= Series B median 60% に対し 90%)
- 「NRR は **120% で above peer median**」

これらの語法は出典が共有された benchmark に立脚している前提で初めて機能する。skill の job は、その前提を一つの canonical document に集約することである。

### 1.3 Sanity check 閾値の「根拠」を benchmark に置く

`scripts/sanity_checks.py` の S1-S10 判定 (Magic Number > 0.75 / Burn Multiple < 2 / Rule of 40 > 40 / NRR > 110% / LTV/CAC > 3 / CAC Payback < 18 mo / GM% > 70% / TAM realism / TV/EV ratio / Founder dilution > 8%) はそれ自体は閾値の集合であり、各閾値の **根拠 (なぜ 0.75 か、なぜ 110% か)** は benchmark に置く必要がある。

本書 §13 で、S1-S10 の各閾値が本書のどの section の median/quartile に由来するかを明記する。閾値が任意設定 (cherry-picked) であるとの批判を払拭するために必須の整合である。

### 1.4 M&A buyer / IPO underwriter の DD で「benchmark deviation の説明力」が require される

M&A の sell-side process において、buyer の DD team は **必ず** target 企業の metric を業界 benchmark と比較する。同様に IPO underwriter (Goldman / MS / JPM 等の syndicate) は S-1 / 目論見書のドラフト段階で peer comp を作成する。Benchmark から大きく乖離している metric については、**乖離の理由を founder / management が説明できる必要がある** — できなければ valuation に discount が乗る、または deal が落ちる。

たとえば:

- **GM% 55% (median 75%)** : 「professional services 比率が 30% で revenue mix を引き下げている。recurring SaaS 単体では 78%」と説明できれば maintenance、できなければ「コスト構造に問題」として valuation discount。
- **NRR 95% (median 115%)** : 「主要顧客 1 社が contract restructure で一時的に downgrade、ARR 影響は ¥80M、Q4 で正常化」と説明できれば許容、できなければ "structural churn" 懸念で deal kill 可能性。
- **Magic Number 0.4 (median 0.8)** : 「過去 4 quarter は新市場開拓投資 phase、acquired customers の Q5 以降 expansion で recovery 想定」と説明 + 過去 cohort の recovery 実績を提示できれば可、できなければ S&M の wasteful spend として discount。

すなわち本書の役割は単に「数値を載せる」ことではなく、**乖離の説明責任を果たすための比較基準点を提供する** ことである。

### 1.5 Founder / Investor 双方の認知バイアス補正

founder は自社の metric を industry leader (Snowflake / Datadog / ServiceNow) と比較しがちで、過度に悲観的になる。逆に investor は seed / series A の company を mature listed company と比較してしまうと過度に厳しい判断になる。

本書は **stage stratification (Pre-Seed / Seed / Series A / Series B / Series C+ の 5 階層)** を提供することで、適切な peer group での比較を可能にする。Series A startup を Series C+ benchmark と比較するのは meaningless であり、IC memo を書くときには必ず stage を fit させる必要がある。

### 1.6 本書を使わなかった場合に起きる典型的な失敗

実例 (anonymized):

- **Case A**: Series A SaaS で NRR 105% を「強い」と memo に記載したが、Pacific Crest median = 110% であり median 以下。partner review で弾かれた。
- **Case B**: D2C で repeat rate 25% を「業界平均」と書いたが、出典が当社サイトの blog post (Tier 4) で Pacific Crest 同等の Tier 1 source と比較すると 30-50% が median。defensibility 欠落で IC memo 書き直し。
- **Case C**: Bio で Phase II → III 確率 50% を仮定したが、BIO Industry Report 2024 では 30-40% が median。誤った gating で valuation 過大評価、IC で deal kill。
- **Case D**: Marketplace で take rate 10% を「弱い」と判断したが、対象 vertical (B2B SaaS marketplace) では median 10%、すなわち平均的。誤った悲観で deal pass、後に他社が買収。

これら 4 ケースはすべて、本書のような **canonical benchmark database** が手元にあれば防げた失敗である。

---

## 2. Benchmark Source Authority Hierarchy

Benchmark の数値は、その出典の **権威性 (authority)** によって IC memo / 投資判断における **使用可否** を決める。本書では Tier 1-4 の 4 階層に分類する。

### 2.1 Tier 1 — 大規模 N の annual survey (使用最優先)

> Tier 1 は **N ≥ 200、年次以上の cadence、methodology 公開、median + quartile 提示** を満たす publicly available data sourceに限定する。IC memo / DD で第一に引くべき source。

| Source | Cadence | 典型 N | URL / Identifier | Coverage |
|---|---|---|---|---|
| **Pacific Crest SaaS Survey** | Annual (Q3) | 1,000+ | Sponsored by Pacific Crest / KeyBanc, partnered with SaaS Capital and OPEXEngine | comprehensive SaaS metrics, by ARR scale stratified |
| **OpenView Partners SaaS Benchmarks** | Annual + quarterly updates | 500+ | openviewpartners.com/expansion-saas-benchmarks/ | growth, retention, GTM efficiency |
| **KeyBanc Capital Markets SaaS Survey** | Annual (Q3) | 300-500 | key.com (KeyBanc Capital Markets) | growth, profitability, GTM |
| **ChartMogul SaaS Retention Report** | Annual + monthly trends | 2,500+ | chartmogul.com/reports/ | retention, churn, NRR/GRR |
| **SaaSCapital Survey** | Annual | 1,000+ | saas-capital.com/research-and-analysis/ | financial focus, capital efficiency |
| **Bessemer State of the Cloud Report** | Annual (Q1) | aggregated portfolio + public comp | bvp.com/atlas/state-of-the-cloud-2025 | cloud index, valuation multiples |
| **EMERGENCE Capital B2B Cloud Report** | Annual | aggregated portfolio | emcap.com | enterprise B2B SaaS |
| **NVCA / Pitchbook Venture Monitor** | Quarterly | full deal flow data | nvca.org / pitchbook.com | capital deployment, valuations |
| **SRS Acquiom M&A Deal Terms Study** | Annual | 1,500+ deals | srsacquiom.com | M&A consideration mix, escrow, earn-out |
| **BIO Industry Phase Success Rates** | Annual | 12,000+ trials | bio.org | clinical trial success rates by phase |
| **Pitchbook Quantitative Perspectives** | Quarterly | full universe | pitchbook.com/news/reports | venture, growth equity, buyout trends |

特徴:
- methodology section が公開されている
- N (sample size) が明示
- median + quartile 双方が提示される (ただし source ごとに quartile の定義が top 25% か top 10% か異なるため記載必須)
- year-over-year で同じ methodology を維持する (trend 比較可能)

### 2.2 Tier 2 — VC / PE 公開分析、citation 付 (使用可、但し source 検証)

> Tier 2 は **個別 VC partner / PE firm の publicly available analysis post で、原 data source への citation がある** もの。Tier 1 ほどの大規模 N ではないが、portfolio company aggregate / pattern 観察として有用。IC memo で使用可、但し原 source (= Tier 1) が併記できればなお良い。

| Source | URL / Identifier | Specialty |
|---|---|---|
| **a16z portfolio analysis** | a16z.com/category/portfolio-construction/ | growth, network effects, marketplace |
| **Sequoia Capital Insights** | sequoiacap.com/perspectives/ | broad industry, recent: AI, SaaS efficiency |
| **Bessemer "8 Laws of Cloud" / "Memos to Founders"** | bvp.com/atlas | cloud company building |
| **Iconiq Capital Growth Letters** | iconiqcapital.com (gated) | growth-stage SaaS |
| **Tomasz Tunguz analysis posts** | tomtunguz.com | granular SaaS pattern observation |
| **David Sacks (Craft Ventures / SaaStr)** | davidsacks.substack.com / craftventures.com | Burn Multiple framework, SaaS GTM |
| **Bain & Company industry reports** | bain.com/insights/ | industry deep-dive (Hardware, FinTech, Healthcare) |
| **Boston Consulting Group industry reports** | bcg.com/publications | industry, especially adjacent to traditional sectors |
| **McKinsey & Company Global Banking Reviews** | mckinsey.com/industries | FinTech / Banking / Insurance |
| **First Round Capital "State of Startups"** | firstround.com/review/ | early-stage operator survey |
| **Jason Lemkin (SaaStr)** | saastr.com | SaaS practitioner pattern observation |

注意点:
- Tier 2 の数字は portfolio aggregate (= 各 firm の survivor 集合) に偏る → "VC-backed only, growing only" の bias がある
- 個別 thesis post ほど narrative bias が混じる (= 自社 thesis を強化する数字を選ぶ傾向)
- **同じ数字が複数 Tier 2 source で繰り返される場合**、原典が Tier 1 であることを確認する (= chain citation の起点を辿る)

### 2.3 Tier 3 — 業界 analyst (Tier 1 がない領域で使用)

> Tier 3 は **業界 analyst firm (Gartner / Forrester / IDC / CB Insights / Crunchbase aggregated)** の有償・無償 report。IT spend / cloud spend / fintech transaction volume 等、Tier 1 が cover しない領域で使用。

| Source | Specialty |
|---|---|
| **Gartner** | IT spend forecast, Magic Quadrant (positioning), Hype Cycle |
| **Forrester** | tech adoption, Wave reports, customer experience |
| **IDC** | hardware shipment, cloud infrastructure spend |
| **Crunchbase aggregated** | funding rounds, founder demographics |
| **CB Insights** | startup landscape, exit data (often republished Pitchbook + own scraping) |
| **Pitchbook segment reports** | by-industry venture data |
| **Statista** | broad consumer / B2C market sizes (注意: secondary aggregator が多い) |
| **eMarketer / Insider Intelligence** | digital advertising, e-commerce |
| **Frost & Sullivan** | industrial, healthcare hardware |

注意点:
- Tier 3 は **methodology の透明度が Tier 1 より低い** ことがある (特に Statista は secondary citation 多用)
- 数字を引く時は、必ず report の発行年 + 対象期間を併記
- 業界全体 spend の絶対額は信頼できるが、「median/quartile of startup metric」は Tier 1 に劣る

### 2.4 Tier 4 — anecdotal、IC memo では使用回避

> Tier 4 は **citation のない LinkedIn post / Twitter (X) thread / Medium post / 個人 blog** 等。内部の brainstorming / 仮説生成では参考になるが、**IC memo / DD report の数字としては使用しない**。

該当例:
- LinkedIn post で「SaaS の median NRR は 110% です」と書かれているが、source 記載なし
- Twitter thread で「Series A の Burn Multiple median は 1.5」とあるが、N も year も不明
- Medium 記事で「marketplace take rate は普通 15%」とあるが、対象 vertical 不明

これらの数字は感覚的に近いことが多いが、IC reviewer / partner からは「source は」と必ず聞かれる。返答できないと defensibility が崩壊するため、IC memo の数字は **必ず Tier 1-3 に置き換える**。

### 2.5 Source 記載必須項目 (本書の citation 形式)

本書で benchmark を引く際、以下を必ず併記する:

| 項目 | 例 |
|---|---|
| Source name | Pacific Crest SaaS Survey |
| Version / year | 2024 (data collected H1 2024) |
| Sample size (N) | N=1,082 |
| URL / Identifier | (内部 working では URL、本書ではsource name + year で十分) |
| Tier | Tier 1 |

例: 「NRR median 115% (Pacific Crest 2024 SaaS Survey, N=1,082, Tier 1)」

### 2.6 Quartile 定義の不一致への注意

Source ごとに quartile の定義が異なる:

| Source | "Top quartile" 定義 | "Median" 定義 | "Bottom quartile" 定義 |
|---|---|---|---|
| Pacific Crest | top 25% (P75 cutoff) | P50 | bottom 25% (P25 cutoff) |
| OpenView | top 25% (P75 cutoff) | P50 | bottom 25% |
| Bessemer (Cloud Index) | top decile (P90) で "best-in-class" | P50 | bottom decile (P10) |
| ChartMogul | NPS-style score の top 25% | P50 | bottom 25% |
| David Sacks "Burn Multiple" | "best-in-class" = < 1 (閾値式、quartile ではない) | "OK" = 1-2 | "bad" = > 3 |

**本書では原則 P75 (= top 25% cutoff) を "Top quartile" と呼ぶ**。Bessemer の "best-in-class" (P90) は本書中で明示的に区別する。

---

## 3. Update Cadence

本書は **年 1 回 (Q4)** の通期 review + metric ごとの inline 更新を行う。各 source の最新版が出るタイミングを以下に整理する:

| Source | Cadence | 直近版 (本書執筆時点) | 更新月 (typical) |
|---|---|---|---|
| Pacific Crest SaaS Survey | Annual (Q3) | 2024 | September |
| OpenView SaaS Benchmarks | Annual + quarterly updates | 2024 | rolling |
| KeyBanc SaaS Survey | Annual (Q3) | 2024 | September |
| ChartMogul SaaS Retention Report | Annual + monthly trends | 2024 | December (annual) |
| SaaSCapital Survey | Annual | 2024 | June |
| Bessemer State of the Cloud | Annual (Q1) | 2025 | February-March |
| Bain industry reports | Various | 2023-2024 | rolling |
| BIO Industry Phase Success | Annual | 2023 (covering 2011-2020 trials) | December |
| SRS Acquiom M&A Deal Terms Study | Annual | 2024 | October |
| Pitchbook NVCA Venture Monitor | Quarterly | 2024 Q4 | quarterly |

> 本書の各 metric には引用年次 (e.g. "Pacific Crest 2024") を付し、年 1 回の review 時に最新版に置き換える。**本書が 1 年以上更新されていない場合は読者は Tier 1 source を直接参照する** ことを推奨。

特に変動の激しい領域 (= update 必須):

- **AI / Foundation Model cost** (token 単価、inference latency) → 6 か月で 50% 以上変動することがある
- **Cloud SaaS valuation multiple** → market regime で 2x 動く (2021 vs 2023)
- **Fintech NIM / Cost of risk** → 金利環境で動く
- **D2C ROAS** → platform algorithm 変更で動く

---

## 4. SaaS Metric Benchmarks

> **§4 の使用範囲**: 本 section の数値は B2B SaaS / B2C SaaS (subscription) を対象とする。Marketplace / Fintech / Hardware / Bio / AI Foundation の業態は §5-§10 を参照。
>
> **Stage definition**: Pre-Seed = ARR < $0.5M / Seed = ARR $0.5M-$2M / Series A = ARR $2M-$10M / Series B = ARR $10M-$30M / Series C+ = ARR $30M+。本書の各 stage column はこの ARR scale に紐づく (= round name ではなく ARR scale で stratify)。
>
> **Quartile definition**: Top = P75 (top 25% cutoff)、Median = P50、Bottom = P25 (bottom 25% cutoff)。Bessemer の "best-in-class" (P90) は別記。

### 4.1 ARR Growth Rate (YoY %)

ARR の前年同期比成長率。SaaS の最重要 single metric。

#### Benchmark matrix (ARR YoY growth %)

| Stage (ARR scale) | Top quartile (P75) | Median (P50) | Bottom quartile (P25) | Source / N | Tier |
|---|---|---|---|---|---|
| Pre-Seed (< $0.5M ARR) | 400% | 200% | 100% | First Round 2023 N=120 | 1 |
| Seed ($0.5-2M ARR) | 250% | 150% | 80% | KeyBanc 2024 N=180 | 1 |
| Series A ($2-10M ARR) | 200% | 120% | 60% | Pacific Crest 2024 N=350 | 1 |
| Series B ($10-30M ARR) | 100% | 60% | 30% | Pacific Crest 2024 N=400 | 1 |
| Series C+ ($30M+ ARR) | 50% | 30% | 15% | Bessemer State of Cloud 2025 (cloud index) | 1 |
| Public SaaS ($100M+) | 40% | 22% | 12% | Bessemer Cloud Index 2025 (Q1) | 1 |

#### 注釈

- Series A 以下では分母が小さいため YoY % が爆発的に大きく見える ("law of small numbers")。**4Q rolling growth** または **net new ARR per quarter** で見るのが安定。
- Series C+ で「30% YoY が median」というのは、$50M ARR から $65M ARR への成長を意味する。$30M の net new ARR ではなく $15M の net new ARR が median である点に注意。
- Bessemer の "Triple Triple Double Double Double" (T2D3) ルール: Series A → IPO までに 3x → 3x → 2x → 2x → 2x の 5 年で ~72x、これは **top quartile 路線** であり median ではない。
- 2022-2023 の market downturn 期は SaaS growth rate が 2 割程度 derate した (Bessemer Cloud Index)。本書の 2024 数値はその再加速 phase の median を反映。

### 4.2 NRR (Net Revenue Retention)

期初 cohort の ARR に対する期末同 cohort の ARR ratio。expansion + contraction + churn を含む。

#### Benchmark matrix (NRR %)

| Stage | Top quartile (P75) | Median (P50) | Bottom quartile (P25) | Best-in-class (P90) | Source / N | Tier |
|---|---|---|---|---|---|---|
| Seed | 120% | 100% | 80% | 130% | ChartMogul 2024 N=2,500+ | 1 |
| Series A | 130% | 110% | 95% | 140% | Pacific Crest 2024 N=350 | 1 |
| Series B | 135% | 115% | 100% | 150% | Pacific Crest 2024 N=400 | 1 |
| Series C+ | 140% | 120% | 100% | 160% | Bessemer 2025 + KeyBanc 2024 | 1 |
| Public best-in-class | 130-140% | 115% | 95% | 165%+ | Public IR (FY24) | 1 |

#### 公開企業 NRR 実例 (FY24 latest disclosed)

| Company | Latest NRR | Source |
|---|---|---|
| Snowflake | 131% (Q4 FY24) | Snowflake 10-K FY24 |
| Twilio | 102% (Q4 FY24) | Twilio 10-K FY24 |
| ServiceNow | 124% (Q4 CY24) | ServiceNow IR |
| Datadog | 115% (Q4 CY24) | Datadog 10-K FY24 |
| MongoDB | 118% (Q4 FY24, ARR-based proxy) | MongoDB IR |
| Cloudflare | 110% (Q4 CY24) | Cloudflare IR |
| HubSpot | 100% (Q4 CY24) | HubSpot IR (note: SMB-heavy customers, lower NRR baseline acceptable) |
| Atlassian | 117% (FY24) | Atlassian shareholder letter |
| Workday | 95% (recent disclosed proxy) | Workday IR (note: enterprise long-cycle, NRR formula differs) |

> 注: 公開企業の NRR 算出 methodology は微妙に異なる (cohort 基準、seat-based vs ARR-based、currency adjustment) ため、各社 IR の definition section を必ず参照。

#### 注釈

- Enterprise SaaS (ACV > $50K) の方が NRR は高くなる傾向 (median +5-10pp)。SMB SaaS は churn が高く NRR が低めに出る。
- **NRR 100% 未満は "contraction"**: 既存顧客 base の ARR が縮小しているため、新規獲得で必死に補わないと growth が出ない。Series B+ で NRR < 100% は kill criteria に近い (`08_investment_thesis §4` 参照)。
- 注意: **PLG (Product-Led Growth) SaaS は NRR の variance が大きい**。free → paid conversion + paid expansion の両方が NRR に乗るため、calculation の transparent disclosure が必要。
- **Snowflake の NRR が peak 158% (FY22) から 131% (FY24) に低下** したのは、(1) base 拡大による mathematical compression、(2) consumption-based pricing で AI workload growth 鈍化、の 2 因子。下降自体は構造的に避けられないが、131% でも依然 top quartile。

### 4.3 GRR (Gross Revenue Retention)

期初 cohort の ARR に対する期末同 cohort の **expansion 抜きの** ARR ratio。100% から下方への churn + downgrade のみを反映。

#### Benchmark matrix (GRR %)

| Stage | Top quartile (P75) | Median (P50) | Bottom quartile (P25) | Source / N | Tier |
|---|---|---|---|---|---|
| Seed | 92% | 85% | 75% | ChartMogul 2024 | 1 |
| Series A | 94% | 88% | 80% | Pacific Crest 2024 | 1 |
| Series B | 95% | 90% | 82% | Pacific Crest 2024 | 1 |
| Series C+ | 97% | 92% | 85% | Bessemer 2025 | 1 |
| Public enterprise SaaS | 97-98% | 93% | 88% | Public IR aggregate | 1 |

#### 注釈

- **GRR は NRR の "純粋な churn 力"** を示す指標。NRR が高くても GRR が低ければ、expansion で churn を埋めているだけ = 構造的に脆い。
- **"GRR と NRR の差 = 純 expansion 余地"**。GRR 90% / NRR 120% であれば、expansion contribution は 30pp。
- Enterprise SaaS は GRR 95%+ が標準。SMB SaaS では 85-90% が現実的。
- Vertical SaaS (例: 業界特化) は switching cost が高く GRR が高めに出る。
- "logo retention" (顧客数ベース) と "revenue retention" (金額ベース) は別物。**本書の GRR は revenue retention**。

### 4.4 Magic Number (×4 quarterly-annualized)

Net New ARR / S&M Spend (前 quarter)、4 倍して年率化したもの。1 USD の S&M 投資が何 USD の ARR を生むかを示す。

#### Benchmark

| Class | Magic Number value | Source | Tier |
|---|---|---|---|
| Top quartile | > 1.0 | SaaSCapital 2024 N=1,500 | 1 |
| Median (good) | 0.7-1.0 | SaaSCapital 2024 | 1 |
| Acceptable | 0.5-0.7 | SaaSCapital 2024 | 1 |
| Bottom quartile (concerning) | < 0.5 | SaaSCapital 2024 | 1 |
| Best-in-class (rare) | > 1.5 | KeyBanc 2024 + observation | 1 |

#### 注釈

- Magic Number は **Q4 → Q1 の S&M を Q1 net new ARR と対応** させる定式が canonical。lag を入れない式は誤り (`02_saas_metrics §5.1` 参照)。
- 1.0 を超える期間は "growth efficient" zone であり、investor は「もっと S&M 投下せよ (= burn 増やしてでも grow せよ)」と push する。
- 0.5 を下回る期間が 2 quarter 以上続く場合、**S&M efficiency 構造の見直し** が要求される (channel mix / segment focus / pricing 改定)。
- PLG companies の Magic Number は traditional sales-led よりも variance が大きく解釈に注意 (S&M に含めるべき marketing 範囲が広い)。

### 4.5 Burn Multiple (David Sacks)

Net Burn / Net New ARR。1 USD の ARR を生むのにいくらの cash を burn しているかを示す。

#### Benchmark

| Class | Burn Multiple | David Sacks 表現 | Source | Tier |
|---|---|---|---|---|
| Best-in-class | < 1 | "Amazing" | David Sacks 2020 framework | 2 |
| Top quartile | 1-1.5 | "Great" | Sacks framework | 2 |
| Median (good) | 1.5-2 | "OK" | Sacks framework | 2 |
| Acceptable | 2-3 | "Suspect" | Sacks framework | 2 |
| Bottom quartile | > 3 | "Bad" | Sacks framework | 2 |
| Critical | > 5 | "Time to panic" | Sacks framework | 2 |

#### Stage 別の現実的 baseline

| Stage | Top | Median | Bottom | 備考 |
|---|---|---|---|---|
| Seed | 1.5 | 2.5 | 4 | early は CAC が安く見えがち |
| Series A | 1.2 | 2.0 | 3.5 | mid stage、最も focus される段階 |
| Series B | 1.0 | 1.5 | 3.0 | growth 加速期、ratio は健全化方向 |
| Series C+ | 0.8 | 1.2 | 2.5 | scale 効くと改善 |
| Public approach | < 0.5 | 0.8 | 1.5 | FCF positive 前夜 |

#### 注釈

- Burn Multiple は **Magic Number の inverse "cousin"**: Magic Number が S&M 効率なら、Burn Multiple は **全社 burn 効率**。R&D / G&A 込みで見るため、Magic Number が高くても overhead が重ければ Burn Multiple は悪化する。
- 2022-2023 の "efficiency era" 以降、investor は **Burn Multiple を top-line growth より優先** する傾向 (= efficient growth narrative)。
- > 3 が 2 quarter 以上続くと bridge round / down round が選択肢になる stage。

### 4.6 Rule of 40

ARR YoY Growth % + FCF Margin %。Bessemer 起源、SaaS valuation の最頻 benchmark。

#### Benchmark matrix

| Stage | Top quartile (P75) | Median (P50) | Bottom quartile (P25) | Best-in-class (P90) | Source | Tier |
|---|---|---|---|---|---|---|
| Series A | 60+ | 30-40 | < 20 | 80+ | KeyBanc 2024 + Bessemer 2025 | 1 |
| Series B | 50+ | 25-35 | < 15 | 70+ | Pacific Crest 2024 | 1 |
| Series C+ | 50+ | 25-35 | < 10 | 80+ | Bessemer Cloud Index 2025 | 1 |
| Pre-IPO ($100M+ ARR) | 60+ | 35-45 | < 20 | 80+ | Bessemer 2025 | 1 |
| Public SaaS | 40+ | 25 | < 10 | 80+ | Bessemer Cloud Index Q1 2025 | 1 |

#### 公開企業 Rule of 40 実例 (FY24)

| Company | YoY Growth | FCF Margin | Rule of 40 | Source |
|---|---|---|---|---|
| Snowflake | 30% | 30% | 60 | Snowflake 10-K FY24 |
| Datadog | 26% | 29% | 55 | Datadog 10-K FY24 |
| ServiceNow | 22% | 32% | 54 | ServiceNow IR |
| CrowdStrike | 29% | 32% | 61 | CrowdStrike IR |
| Atlassian | 24% | 24% | 48 | Atlassian shareholder letter |
| HubSpot | 21% | 17% | 38 | HubSpot IR |
| Twilio | 7% | 16% | 23 | Twilio 10-K FY24 |
| MongoDB | 31% | 17% | 48 | MongoDB IR |

#### 注釈

- **FCF margin** に GAAP operating margin を代入するのは誤り (`02_saas_metrics §5.3` で詳述)。FCF = CFO - CapEx (capitalized SW dev 含む) で見る。
- **Rule of 40 は "valuation multiple" との correlation が高い** (Bessemer Cloud Index, R^2 ~0.5-0.6)。Rule of 40 が 10 上昇すると EV/Revenue multiple が ~1-2x 上昇するのが歴史平均。
- 「growth 70 + margin -25 = 45」の組み合わせが「growth 25 + margin 20 = 45」より valuation で premium が乗ることが多い (= growth weight が highly placed)。但しこれは market regime に依存。
- 2025 現在は **growth + 1.5x margin** という "Rule of 40 with growth premium" の議論もある (Bessemer)。

### 4.7 LTV/CAC

Lifetime Value / Customer Acquisition Cost。

#### Benchmark

| Class | LTV/CAC | Source | Tier |
|---|---|---|---|
| Top quartile (sustainable) | > 3.0 | Bessemer + KeyBanc 2024 | 1 |
| Median (acceptable) | 2.0-3.0 | KeyBanc 2024 | 1 |
| Bottom (concerning) | < 2.0 | KeyBanc 2024 | 1 |
| Enterprise (long sales cycle) | 5+ acceptable | EMERGENCE Capital | 2 |
| PLG (low CAC, high churn-risk) | 3-5 typical | OpenView 2024 | 1 |
| SMB SaaS | 1.5-3.0 typical | Pacific Crest 2024 | 1 |

#### 注釈

- LTV/CAC は **計算が "lossy"** (= lifetime の仮定、GM% の仮定、CAC の S&M scope 仮定で大きく変わる)。本書の数字は「LTV = ACV × GM% / Churn rate」「CAC = (S&M total) / new logos」の standard 定義に依拠。
- LTV/CAC > 5 は **"under-investing in growth"** のシグナルでもある。investor は「もっと S&M 投資せよ」と push する場面が多い。
- < 1.5 は **構造的に viable でない**: lifetime で CAC を回収できないモデル (= ARR を上げる degree of pricing power が必要)。

### 4.8 CAC Payback (months)

CAC を gross margin で回収するのに必要な月数。

#### Benchmark

| Class | CAC Payback | Source | Tier |
|---|---|---|---|
| Top quartile (best-in-class) | < 12 months | KeyBanc 2024 N=350 | 1 |
| Median | 12-18 months | KeyBanc 2024 | 1 |
| Acceptable (enterprise long cycle) | 18-24 months | KeyBanc 2024 | 1 |
| Concerning | > 24 months | KeyBanc 2024 | 1 |
| Critical | > 36 months | observation | 1 |

#### 注釈

- **GM-adjusted CAC payback** が canonical (= CAC / (ARR × GM%) で月数換算)。Naive な "CAC / ARR" 月数換算は誤り (`02_saas_metrics §5.4`)。
- Enterprise SaaS は CAC Payback 24 months でも acceptable とされることがある (lifetime が 7-10 years と長い前提)。
- **CAC Payback と Magic Number は inverse correlated**: Magic Number 1.0 ≒ CAC Payback ~ 12 months 相当 (ASP / contract length / GM% の組み合わせで変動)。
- Series A 以下では cohort 数が少なく CAC Payback の sample variance が大きいため、quarterly aggregate より trailing 12 months で見る。

### 4.9 Quick Ratio (Net New ARR / Net Burn)

Bessemer 提唱。Magic Number の inverse 派生だが net burn 全体ベース。

#### Benchmark

| Class | Quick Ratio | Source | Tier |
|---|---|---|---|
| Top quartile | > 4 | Bessemer "8 Laws" | 2 |
| Median (good) | 2-4 | Bessemer | 2 |
| Acceptable | 1-2 | Bessemer | 2 |
| Bottom (concerning) | < 1 | Bessemer | 2 |

#### 注釈

- Burn Multiple = 1 / Quick Ratio (近似)。Burn Multiple < 1 = Quick Ratio > 1。
- Quick Ratio はChurned ARR を分母に含めるバリアントもある: (New ARR + Expansion ARR) / (Churned ARR + Contracted ARR)。本書のここでは net burn ベースのみ採用。
- > 4 は scale phase に入ると徐々に低下するのが自然 (= base 拡大による分母圧迫)。

### 4.10 ARR per FTE (efficiency)

ARR / 全社 employee 数 (full-time equivalent)。

#### Benchmark

| Stage | Top | Median | Bottom | Source | Tier |
|---|---|---|---|---|---|
| Seed | $100K | $50K | $30K | observation + KeyBanc 2024 | 2 |
| Series A | $200K | $120K | $80K | KeyBanc 2024 | 1 |
| Series B | $300K | $200K | $130K | KeyBanc 2024 | 1 |
| Series C+ | $400K | $250K | $150K | KeyBanc 2024 + Pacific Crest 2024 | 1 |
| Pre-IPO ($100M+) | $500K | $300K | $200K | Bessemer 2025 | 1 |
| Public SaaS | $400K-$1M | $350K | $250K | Public IR aggregate | 1 |

#### 公開企業実例

| Company | ARR / FTE (FY24 approx) | 備考 |
|---|---|---|
| ServiceNow | $700K | enterprise mature |
| Datadog | $750K | observability category leader |
| Atlassian | $500K | self-serve heavy |
| Snowflake | $700K (FY24) | PLG + enterprise hybrid |
| HubSpot | $350K | SMB heavy |
| Twilio | $650K | API-first |

#### 注釈

- ARR per FTE は **会社の "system efficiency"** を示すマクロ指標。R&D heavy / GTM heavy で valuation が異なるため、絶対比較は注意。
- offshore / outsourced 比率の高い会社は ARR per FTE が overstate される (FTE count に offshore / contractor が含まれないことが多い)。

### 4.11 GM% (Gross Margin)

GAAP-defined gross margin (ASC 606 / IFRS 15 ベース)。

#### Benchmark matrix

| Stage / Type | Top quartile | Median | Bottom quartile | Source | Tier |
|---|---|---|---|---|---|
| Pure SaaS (subscription only) | 80%+ | 75% | 65% | Pacific Crest 2024 | 1 |
| SaaS + PS mix (PS < 30%) | 75% | 68% | 60% | Pacific Crest 2024 | 1 |
| SaaS + PS mix (PS > 30%) | 65% | 58% | 50% | Pacific Crest 2024 | 1 |
| Usage-based / Consumption | 70% | 62% | 55% | observation | 2 |
| Vertical SaaS (industry-specific) | 78% | 70% | 60% | Bessemer 2025 | 2 |
| Enterprise on-prem hybrid | 65% | 55% | 45% | observation | 2 |
| Embedded fintech revenue mix | 50% | 35% | 25% | a16z fintech 2024 | 2 |

#### 公開企業 GM% 実例 (FY24)

| Company | GM% (FY24) | Notes |
|---|---|---|
| Snowflake | 67% | consumption-based, COGS ~ cloud infra |
| Datadog | 80% | observability, hosted |
| ServiceNow | 79% | enterprise SaaS |
| MongoDB | 73% | database, hosted |
| Atlassian | 82% | self-serve heavy |
| HubSpot | 84% | SMB SaaS |

#### 注釈

- **Snowflake / MongoDB 等 consumption-based の GM%** は、cloud infra cost が直接 COGS に乗るため、subscription pure-play よりやや低めに出る (これは構造であり improve する余地は限定的)。
- Pure SaaS で GM% < 65% が継続する場合は **inflated COGS** (= professional services / hosting / support の按分問題)、もしくは pricing power 不足のシグナル。
- IFRS 15 / ASC 606 の deferred revenue 認識基準により、"non-GAAP gross margin" を bridging で見ることがある (本書の数字は GAAP base)。

### 4.12 R&D / Revenue

#### Benchmark matrix

| Stage | Top quartile (lean) | Median | Bottom quartile (heavy) | Source | Tier |
|---|---|---|---|---|---|
| Pre-Seed | 60% | 100% | 200%+ | First Round 2023 | 2 |
| Seed | 50% | 80% | 150%+ | KeyBanc 2024 | 1 |
| Series A | 30% | 50% | 80% | Pacific Crest 2024 | 1 |
| Series B | 25% | 40% | 60% | Pacific Crest 2024 | 1 |
| Series C+ | 20% | 30% | 45% | Bessemer 2025 | 1 |
| Public SaaS | 15% | 22% | 35% | Bessemer Cloud Index | 1 |

#### 注釈

- R&D 重 (= % of revenue が高い) こと自体は "bad" ではない: AI / Foundation Model / Vertical SaaS 等は R&D heavy が構造的に正常。
- **R&D / FTE** で見ると比較しやすい: $250K-$400K per R&D FTE が SaaS で典型。
- 一部 R&D を IFRS / GAAP で **capitalize** している会社では reported R&D が低く見える ⇒ FCF benchmark で吸収する。

### 4.13 S&M / Revenue

#### Benchmark matrix

| Stage | Top (lean) | Median | Bottom (heavy) | Source | Tier |
|---|---|---|---|---|---|
| Seed | 30% | 50% | 100%+ | KeyBanc 2024 | 1 |
| Series A | 40% | 60% | 100% | Pacific Crest 2024 | 1 |
| Series B | 40% | 55% | 80% | Pacific Crest 2024 | 1 |
| Series C+ | 35% | 50% | 70% | Bessemer 2025 | 1 |
| Pre-IPO | 30% | 45% | 60% | Bessemer 2025 | 1 |
| Public SaaS mature | 30% | 40% | 55% | Bessemer Cloud Index | 1 |

#### 注釈

- S&M / Revenue が **Series B で 50% を切る** のは "underinvest" のシグナル: growth 鈍化リスクとして investor が懸念。
- Enterprise SaaS は S&M heavy が常 (long sales cycle、CRO + AE + SE chain)。
- PLG model は S&M の中身が異なる (paid acquisition / community / events)。Reported S&M ratio が低いことが多いが、R&D に product-led growth 投資が紛れているケースもある。

### 4.14 G&A / Revenue

#### Benchmark matrix

| Stage | Top | Median | Bottom | Source | Tier |
|---|---|---|---|---|---|
| Seed | 8% | 15% | 25% | KeyBanc 2024 | 1 |
| Series A | 10% | 15% | 22% | Pacific Crest 2024 | 1 |
| Series B | 10% | 13% | 18% | Pacific Crest 2024 | 1 |
| Series C+ | 8% | 12% | 16% | Bessemer 2025 | 1 |
| Public SaaS | 7% | 10% | 14% | Bessemer Cloud Index | 1 |

#### 注釈

- G&A 比率は **stage が進むほど低下する** のが自然 (scale 効果)。Series C+ で G&A 20%+ は overhead 過剰。
- Public 化準備 phase で G&A が一時的に上昇する (audit / SOX / IR / legal 強化)。

### 4.15 ACV / ARPA Stratification

Average Contract Value / Average Revenue Per Account。

#### Benchmark range

| Type | Median ACV | Notes |
|---|---|---|
| SMB SaaS | $1K-$5K | high volume, transactional |
| Mid-market SaaS | $20K-$100K | inside sales |
| Enterprise SaaS | $100K-$1M | field sales, AE + SE |
| Strategic enterprise | $1M+ | C-suite sales |
| PLG starter | $500-$5K | self-serve, freemium upgrade |

ACV stratification は CAC 構造 / sales cycle / churn pattern を決定する。**ACV を 10x するためには GTM model を再設計** する必要があり、cross-segment の "linear extension" は失敗する典型。

---

## 5. Marketplace Metric Benchmarks

> **§5 の使用範囲**: Two-sided / multi-sided marketplace (consumer-to-consumer / business-to-consumer / business-to-business のすべて)。Pure SaaS / Subscription は §4 を参照。
>
> Marketplace 業態の特徴: liquidity (両サイドの厚み)、network effect (cross-side / same-side)、take rate (price extraction power)、frequency (LTV driver) の 4 軸で評価。本書では各軸の benchmark を業界 (vertical) 別に整理。

### 5.1 Take Rate (commission %)

GMV (Gross Merchandise Value) に対する revenue 比率。

#### Benchmark by vertical

| Vertical | Top quartile | Median | Bottom quartile | 公開企業 anchor | Source / Tier |
|---|---|---|---|---|---|
| Ride-hailing (driver-passenger) | 30% | 25% | 20% | Uber 27% (FY24)、Lyft 28% | Uber/Lyft IR / Tier 1 |
| Food delivery | 30% | 25% | 18% | DoorDash 14% (effective)、Uber Eats 22% | DoorDash IR / Tier 1 |
| Vacation rental | 18% | 15% | 12% | Airbnb 14.4% (FY24) | Airbnb 10-K / Tier 1 |
| E-commerce — generalist (eBay) | 13% | 11% | 9% | eBay 10.4% (FY24) | eBay IR / Tier 1 |
| E-commerce — handmade (Etsy) | 8% | 6.5% | 5% | Etsy 17.4% effective with ads (FY24) | Etsy 10-K / Tier 1 |
| Fashion resale (StockX, Vestiaire) | 15% | 12% | 9% | StockX ~10%、TheRealReal 30%+ (consignment) | press / Tier 2 |
| B2B SaaS marketplace | 15% | 10% | 5% | varies | a16z marketplace 100 / Tier 2 |
| Freelance services (Fiverr, Upwork) | 25% | 20% | 15% | Fiverr 27%、Upwork 17% | Fiverr/Upwork IR / Tier 1 |
| Real estate (Zillow lead-gen) | 5% | 3% | 2% | Zillow take rate ~ 1.5% on PropertyValue | Zillow IR / Tier 1 |
| Local services (Thumbtack, TaskRabbit) | 30% | 25% | 15% | various | a16z / Tier 2 |
| App store (App Store, Play) | 30% | 25% | 15% (post 2021 regulation) | Apple 30% → 15% (small dev) | Apple IR / Tier 1 |
| Online dating (Match Group) | n/a (subscription model) | n/a | n/a | Match ~ 70% GM% | Match IR |
| 生鮮 marketplace (日本) | 20% | 15% | 10% | 食べチョク等 (estimate) | press / Tier 3 |

#### 注釈

- Take rate の "natural ceiling" は **buyer の switching cost + seller の dependency** に依存。Uber は driver の switching cost が低いため take rate を 30%+ に上げると driver が他 platform へ流出。Etsy は seller の handmade brand investment が switching cost を作るため 17% でも維持できる。
- Take rate 上昇の上限を「市場が許容するか」を見るには、**price elasticity test** (= 上げた quarter の GMV growth deceleration) を観察。
- B2B marketplace では take rate を低く抑え (5-10%) volume を取り、ancillary services (SaaS subscription、payment processing、ads、insurance) で margin を取る "marketplace + SaaS" 戦略が増加 (Faire / Toast / ShipBob 等)。
- **regulatory ceiling**: EU Digital Markets Act / 韓国 App Store 規制等で App Store の take rate は徐々に圧縮中。

### 5.2 GMV Growth Rate (YoY %)

Marketplace の "top-line" 指標。

#### Benchmark matrix

| Stage (GMV scale) | Top | Median | Bottom | Source / Tier |
|---|---|---|---|---|
| Pre-Seed (< $1M GMV) | 500% | 200% | 80% | a16z marketplace post 2024 / Tier 2 |
| Seed ($1M-$10M GMV) | 300% | 150% | 60% | a16z / Tier 2 |
| Series A ($10M-$100M GMV) | 200% | 100% | 40% | a16z / Tier 2 |
| Series B ($100M-$1B GMV) | 100% | 50% | 25% | Pitchbook segment / Tier 1 |
| Series C+ ($1B+ GMV) | 50% | 30% | 15% | public marketplace IR aggregate / Tier 1 |
| Public marketplace | 30% | 18% | 8% | Uber/DoorDash/Airbnb/Etsy aggregate / Tier 1 |

#### 注釈

- GMV growth と take rate growth の **divergence** を見る: GMV growth 30%、revenue (= GMV × take rate) growth 50% であれば pricing power 強化中、逆なら take rate 圧縮中。
- 2022-2024 の e-commerce 市場は post-pandemic normalization で GMV growth が rebound からの hold pattern。

### 5.3 Cohort Retention (M3 / M6 / M12)

期初 acquired user の M+N 月後 active rate (購入 or 利用)。

#### Benchmark matrix (consumer marketplace)

| Vertical | M3 retention | M6 retention | M12 retention | Source / Tier |
|---|---|---|---|---|
| Ride-hailing | 70% | 60% | 50% | Uber DD docs / Tier 2 |
| Food delivery | 50% | 40% | 30% | DoorDash S-1 / Tier 1 |
| E-commerce generalist | 40% | 30% | 22% | a16z marketplace 100 / Tier 2 |
| Fashion resale | 35% | 25% | 18% | StockX prospectus / Tier 2 |
| Vacation rental | 50% (annual usage proxy) | 35% | 25% | Airbnb investor day / Tier 1 |
| Freelance services | 60% (project-based) | 45% | 35% | Upwork S-1 / Tier 1 |

#### Best-in-class anchor

- **Amazon Prime renewal rate**: 93%+ globally (Amazon 10-K 推定)
- **Uber active rider 90-day retention**: ~72% (S-1)
- **Airbnb host re-listing rate**: 70%+ (FY24 IR)

#### 注釈

- "M+12 retention 30%" は consumer marketplace では非常に良い水準。20% を下回ると acquisition 永続が必須となり LTV/CAC 構造が脆弱。
- B2B marketplace では retention が consumer より高い (60-80% M+12 が common)。

### 5.4 Buyer-Seller Liquidity

Marketplace の "両サイドの厚み":

| Metric | Definition | Top tier benchmark | Median |
|---|---|---|---|
| Buyer / seller ratio | Active buyers / Active sellers (per period) | depends on vertical | n/a |
| Listings per active seller (e-commerce) | Listings count avg per active seller | 50+ | 15-30 |
| Sessions per active buyer | Sessions / month per buyer | 10+ | 3-5 |
| Time to first transaction (new buyer) | Days from registration to first trade | < 7 days | 14-30 days |
| Time to second transaction (new buyer) | Days from first to second | < 30 days | 60-90 days |
| Search-to-fill rate (vacation rental) | Search resulting in booking % | 30%+ | 15-20% |
| Match rate (dating, services) | Matched / Initiated request | 70%+ | 40-60% |

#### 注釈

- **Liquidity threshold**: "search-to-fill rate" が 50%+ 安定化したら liquid market、20% 以下では illiquid (= cold start 状態)。Network effect の transition point。
- Buyer / seller ratio: ride-hailing は ~ 5-10 (passengers per driver)、handmade では ~ 50+ (buyers per seller)、freelance では ~ 1.5-3。Vertical の自然 ratio から大きく外れると imbalance signal。

### 5.5 Frequency (transactions per active user per period)

#### Benchmark by vertical

| Vertical | Median frequency | Top tier | 単位 |
|---|---|---|---|
| Ride-hailing | 4-6 | 15+ | rides / month per active rider |
| Food delivery | 3-5 | 8+ | orders / month per active customer |
| E-commerce generalist | 1-2 | 5+ | orders / month |
| Vacation rental | 0.5 | 1.5 | bookings / quarter |
| Fashion resale | 1-2 | 4 | trades / quarter |
| Freelance services | 0.5-1 | 3 | projects / month |
| App store transactions | 5-10 | 30+ | downloads + IAP / month |

### 5.6 AOV (Average Order Value) / GMV per transaction

| Vertical | Median | Top tier | 単位 |
|---|---|---|---|
| Ride-hailing | $12-$20 | $30+ | per ride |
| Food delivery | $30-$45 | $60+ | per order |
| E-commerce generalist | $60-$100 | $200+ | per order |
| Vacation rental | $500-$800 | $2,000+ | per booking |
| Fashion resale | $150-$300 | $1,000+ | per trade |
| Freelance services | $200-$1,000 | $5,000+ | per project |

### 5.7 Cross-side Network Effect Strength

Marketplace の moat 評価:

| Class | Definition | Indicator | Example |
|---|---|---|---|
| Strong cross-side | 一方が増えるほど他方の utility が指数的に増 | search-to-fill rate が user 数増に連動 | Uber、Airbnb |
| Weak cross-side | linear に utility 増 | time-to-fill が線形に短縮 | Etsy、Fiverr |
| Local network effect | 地理的 cluster でしか効かない | city-by-city liquidity 必要 | Local services、フードデリバリー |
| Same-side positive | 同サイド user 増で他 user が利益 | reviews / community | Yelp |
| Same-side negative | 同サイド user 増で他 user が不利益 (= 競合) | seller competition | App store の同カテゴリ過密 |

### 5.8 Marketplace Take Rate Trajectory (Stage 別 norm)

| Stage | Take rate norm | Reason |
|---|---|---|
| Pre-Seed | 0-3% (subsidize 期) |両サイド獲得を優先 |
| Seed | 3-8% | unit economics の片鱗を見る |
| Series A | 8-15% | take rate sustainability test 段階 |
| Series B | 12-20% | scale phase、margin 拡大 |
| Series C+ | 15-25% | mature phase、ancillary revenue 上乗せ |
| Public mature | 15-30% | platform power 完成 |

### 5.9 Marketplace M2C / B2B / C2C 別 base economics 早見

| 軸 | C2C (例: eBay early) | B2C (例: Amazon Marketplace) | B2B (例: Faire) |
|---|---|---|---|
| Take rate median | 8-15% | 10-20% | 5-10% (+ ancillary) |
| Repeat frequency | low | mid | mid-high |
| GMV/transaction | small ($30-$100) | medium ($60-$300) | large ($500-$10K) |
| Liquidity threshold | small population OK | large city scale | sector cluster |

---

## 6. Fintech Metric Benchmarks

> **§6 の使用範囲**: Lending、Payments、BaaS (Banking-as-a-Service)、Embedded finance、Insurtech、Wealthtech。
>
> Fintech 業態の特徴: NIM (Net Interest Margin) / cost of risk / regulatory capital / unit economics の 4 軸で SaaS とは別枠の benchmark が必要。

### 6.1 Lending (Consumer / SMB)

#### NIM (Net Interest Margin)

NIM = (Interest income - Interest expense) / Earning assets。

| Vertical | Top quartile NIM | Median | Bottom | Source / Tier |
|---|---|---|---|---|
| Consumer unsecured (BNPL) | 15-20% | 10-12% | 5% | a16z fintech 2024 / Tier 2 |
| Consumer credit card | 12-15% | 8-10% | 4% | Federal Reserve aggregated / Tier 1 |
| Consumer secured (auto, mortgage) | 4-6% | 2-3% | 1% | Fed bank aggregate / Tier 1 |
| SMB unsecured (working capital) | 18-25% | 12-15% | 6% | a16z fintech 2024 / Tier 2 |
| SMB asset-backed (invoice, factoring) | 8-12% | 5-7% | 2% | various / Tier 2 |
| Crypto lending | 10-30% (high variance) | n/a | n/a | Tier 4 |

#### Cost of Risk (NPL %, Default rate)

Charge-off rate = annual loan losses / outstanding portfolio.

| Vertical | Acceptable | Median | Concerning | Source / Tier |
|---|---|---|---|---|
| Consumer prime (FICO 700+) | < 1% | 1-2% | > 3% | Fed / Tier 1 |
| Consumer near-prime (FICO 600-700) | 3-5% | 5-8% | > 10% | Fed / Tier 1 |
| Consumer subprime (FICO < 600) | 8-12% | 12-18% | > 25% | Fed / Tier 1 |
| BNPL (Klarna, Affirm) | 2-3% | 4-5% | > 7% | Affirm 10-K / Klarna prospectus / Tier 1 |
| SMB working capital | 3-5% | 6-9% | > 15% | a16z fintech / Tier 2 |
| Auto loan (subprime) | 5-7% | 8-12% | > 15% | Fed / Tier 1 |
| Mortgage (prime) | < 0.5% | 0.5-1% | > 2% | Fed / Tier 1 |

#### 注釈

- **Cost of risk は credit cycle に強く依存**: 2022-2024 の expansion から 2024 後半は consumer credit normalization で charge-off 上昇 phase。本書 benchmark は 2023-2024 cycle 平均。
- **CECL (Current Expected Credit Loss) accounting** 下では loan loss provision が前倒しで計上される (US GAAP 基準) → P&L で reported provision の解釈に注意。
- Subprime lending startup の典型的 IC kill criteria: charge-off > 15% かつ NIM が cost of risk を 5pp 以上上回らない (= "negative real spread")。

#### Approval Rate

| Vertical | Median approval rate | 備考 |
|---|---|---|
| Consumer unsecured | 30-50% (online) | application funnel 後半 |
| Consumer prime card | 50-65% | 銀行系 |
| Consumer subprime | 60-80% (high approval, high risk) | fintech subprime |
| SMB working capital | 30-45% | underwriting deeper |
| BNPL | 70-85% | low-friction, instant |

#### Loan Origination Cost (CAC equivalent)

| Vertical | Cost per origination | 備考 |
|---|---|---|
| Consumer unsecured (online) | $50-$200 | mostly digital marketing |
| Consumer prime card | $100-$300 | 含む branch / partnership |
| SMB working capital | $300-$1,500 | longer underwriting |
| Mortgage | $2,000-$5,000 | regulatory + manual |

### 6.2 Payments

#### Take Rate

| Vertical | Top quartile | Median | Bottom | 公開企業 anchor | Source / Tier |
|---|---|---|---|---|---|
| Card processing (Stripe / Block) | 2.9% + $0.30 (US blended) | 2.5-3% | 2-2.3% | Stripe disclosed via reports / Adyen ~ 1% (large enterprise pricing) | press / Tier 2 |
| Payment gateway pure | 0.5-1.5% | 0.8% | 0.5% | smaller gateway / Tier 3 |
| Cross-border (Wise, Remitly) | 1-1.5% | 0.8-1.2% | 0.5% | Wise 10-K / Tier 1 |
| BNPL (Affirm / Klarna) | 6-7% (merchant-side) | 4-5% | 3% | Affirm 10-K / Tier 1 |
| Crypto payment | 1-2% | 0.5-1% | 0.1% | various / Tier 3 |
| ACH / wire (US) | flat fee | flat | flat | n/a |

#### Authorization Rate (auth rate)

card payment の credit card auth が成功する率。

| Class | Auth rate | 備考 |
|---|---|---|
| Best-in-class | 95%+ | ML fraud + smart routing |
| Median | 90-93% | typical processor |
| Concerning | < 88% | revenue leak |

Stripe / Adyen 等の auth rate 改善は merchant にとって直接的 revenue 改善 (1pp = revenue 1pp 増)。

#### TPV (Total Payment Volume) Growth

| Stage | Top YoY | Median | Bottom |
|---|---|---|---|
| Series A | 200% | 100% | 50% |
| Series B | 100% | 60% | 30% |
| Series C+ | 50% | 30% | 15% |
| Public payments | 25% | 15% | 8% |

### 6.3 Embedded Finance / BaaS

#### Per-user financial revenue

| Vertical | Median per-user financial revenue (annual) | 備考 |
|---|---|---|
| Banking app (Chime, Cash App) | $80-$150 | interchange + lending + sub |
| SMB embedded (Toast Capital, Square) | $300-$1,500 | working capital に乗せ |
| Vertical SaaS embedded (例: Vagaro 美容、ServiceTitan) | $500-$3,000 | payment + lending |

Embedded finance の典型 thesis: "vertical SaaS が payments で revenue を 2x、lending で 3x にする"。

### 6.4 Insurtech

| Metric | Top | Median | Bottom | 備考 |
|---|---|---|---|---|
| Loss ratio (claim payouts / premium) | < 60% | 65-75% | > 85% | Lemonade 89% (FY23) → 75% (FY24) recovery |
| Combined ratio (loss + expense) | < 95% (profitable) | 100-105% | > 115% | Lemonade still > 100% |
| Premium retention | 90%+ | 80-85% | < 75% |  |
| Distribution cost | 10-15% | 20-25% | 30%+ |  |

### 6.5 Wealthtech / Robo-advisor

| Metric | Top | Median | Bottom |
|---|---|---|---|
| AUM growth YoY | 80%+ | 40% | 15% |
| Revenue / AUM (bps) | 50bps | 25bps | 15bps |
| Customer LTV | $5K | $2K | $500 |

Robo-advisor の典型的 unit economics: LTV $2K、CAC $300、payback 18-24 months。

---

## 7. D2C Metric Benchmarks

> **§7 の使用範囲**: Direct-to-Consumer (Shopify ecosystem、physical product brands、subscription box、apparel、CPG 等)。

### 7.1 Customer Metrics

#### Repeat Rate (12-month)

| Category | Top quartile | Median | Bottom | Source / Tier |
|---|---|---|---|---|
| Subscription box | 60-70% | 40-50% | 25% | observation / Tier 2 |
| Beauty / skincare D2C | 50% | 35-40% | 20% | Glossier / Warby press / Tier 3 |
| Apparel D2C | 35% | 25-30% | 15% | various / Tier 3 |
| Home goods D2C | 30% | 18-22% | 10% | observation / Tier 3 |
| Food / CPG D2C | 50%+ (consumable) | 35% | 20% | observation / Tier 3 |
| Electronics D2C | 15% | 10% | 5% | low purchase frequency 構造 |

#### AOV (Average Order Value)

| Category | Median AOV |
|---|---|
| Beauty | $50-$80 |
| Apparel | $80-$150 |
| Home goods | $150-$400 |
| Food / CPG | $40-$80 |
| Electronics | $300-$1,500 |
| Furniture | $1,000-$5,000 |

#### LTV/CAC

| Category | Top | Median | Bottom |
|---|---|---|---|
| Subscription box | 4-5 | 2.5-3 | 1.5 |
| Beauty | 3-4 | 2-2.5 | 1.5 |
| Apparel | 2.5-3 | 1.8-2.2 | 1.2 |
| Food / CPG | 4-5 | 2.5-3 | 1.5 |

#### CAC Payback

| Category | Median CAC payback |
|---|---|
| Subscription box | 6-12 months |
| Beauty / skincare | 9-15 months |
| Apparel | 12-18 months |
| Food / CPG | 6-12 months |
| Electronics | 18+ months (high AOV/low frequency) |

### 7.2 Inventory & Operations

#### Inventory Turns (annual)

| Category | Top | Median | Bottom |
|---|---|---|---|
| Apparel | 8-12 | 5-7 | 3-4 |
| Beauty | 6-10 | 4-6 | 2-3 |
| Home goods | 5-8 | 3-5 | 2 |
| Food / CPG | 12-20 | 8-12 | 5 |
| Electronics | 6-10 | 4-6 | 2-3 |

#### Cash Conversion Cycle

CCC = DIO + DSO - DPO (days inventory outstanding + days sales outstanding - days payable outstanding)。

| Category | Top (cash-positive cycle) | Median | Bottom |
|---|---|---|---|
| Pure D2C (online) | -10 to +30 days | +30-60 | +60-120 |
| D2C + retail wholesale | +30 days | +60-90 | +120 days+ |
| Subscription box (prepaid) | -30 to -60 days | -10 to -30 | +30 |

#### GM% (after shipping)

| Category | Top | Median | Bottom |
|---|---|---|---|
| Beauty / skincare | 70-80% | 55-65% | 40% |
| Apparel | 55-65% | 45-55% | 35% |
| Home goods | 50-60% | 40-50% | 30% |
| Food / CPG | 35-45% | 25-35% | 15% |
| Electronics | 35-45% | 25-35% | 15% |

### 7.3 Marketing

#### ROAS (Return on Ad Spend) by channel

| Channel | Top ROAS | Median | Bottom |
|---|---|---|---|
| Meta (Facebook + Instagram) | 4-5x | 2.5-3x | 1.5x |
| TikTok ads | 3-4x | 2-2.5x | 1x |
| Google Search | 5-7x | 3-4x | 2x |
| Google Shopping | 4-5x | 2.5-3x | 1.5x |
| Email | 30-40x (organic) | 15-20x | 5x |
| Affiliate | 5-7x | 3-4x | 2x |

#### Brand vs Performance ratio

| Stage | Brand : Performance ratio (S&M spend) |
|---|---|
| Pre-Seed / Seed | 10:90 (mostly performance) |
| Series A | 20:80 |
| Series B | 30:70 |
| Series C+ | 40:60 |
| Mature D2C | 50:50 |

Allbirds / Casper / Warby Parker 等の brand-heavy D2C は早期から 30:70 に近づける戦略。

### 7.4 Channel Diversification

D2C の "Meta dependency" risk (Meta が CAC の 60%+) は kill criteria に近い (`08_investment_thesis §4`)。

| Diversification level | DTC channel mix | Risk profile |
|---|---|---|
| High concentration | 1 channel > 70% | High risk |
| Moderate | top channel 40-70% | Medium |
| Diversified | top channel < 40% | Low |

### 7.5 Wholesale / Retail expansion

D2C → omni-channel への evolution:

| Stage | Wholesale revenue % | 備考 |
|---|---|---|
| Pure DTC | 0% | online-only |
| Early omni | 5-15% | trial accounts |
| Hybrid | 30-50% | scaling distribution |
| Mature DTC + wholesale | 50-70% | brand mature |

DTC が wholesale へ移行する際 GM% は 10-20pp 低下 (wholesale は 50% off MSRP が標準)。

---

## 8. Hardware Metric Benchmarks

> **§8 の使用範囲**: Consumer hardware (DJI、Peloton、Sonos)、Enterprise hardware (network、server、storage)、Medical devices、IoT。

### 8.1 GM% (typical)

| Vertical | Top quartile GM% | Median | Bottom |
|---|---|---|---|
| Consumer hardware (DJI、GoPro、Bose) | 35-45% | 25-30% | 15-20% |
| Smartphone (Apple-class) | 45%+ | n/a | n/a |
| Smartphone (commodity Android) | 15-20% | 10% | 5% |
| Enterprise networking (Cisco-class) | 60-65% | 50-55% | 40% |
| Server / Storage | 40-50% | 30-40% | 20% |
| Medical devices (high-end) | 65-75% | 55-65% | 40% |
| IoT (sensor + cloud) | 45-55% | 30-40% | 20% |
| Consumer wearable (Fitbit, Garmin) | 35-45% | 25-30% | 15% |
| EV (Tesla) | 25-30% | 18-22% | 10-15% |

#### 注釈

- Hardware GM% は "production scale" に強く依存。pre-launch / pilot は GM% 10-20pp 低めで spike up at scale (Bill of Materials cost reduction、yield 改善)。
- "Razor-and-blade" モデル (printer-cartridge、Peloton-subscription) では hardware GM% を意図的に薄く (10-20%)、subscription / consumable で margin を取る。

### 8.2 Inventory Turns

| Vertical | Top | Median | Bottom |
|---|---|---|---|
| Consumer electronics | 8-12 | 5-7 | 3 |
| Enterprise hardware | 6-10 | 4-6 | 2-3 |
| Medical devices | 4-6 | 2-3 | 1.5 |
| Industrial IoT | 4-8 | 3-5 | 2 |

### 8.3 Service Revenue % over 5 years (recurring revenue tail)

Hardware company の SaaS-ification 度合い:

| Stage | Service revenue % | Example |
|---|---|---|
| Year 1 (launch) | 0-5% | hardware-only |
| Year 2-3 | 5-15% | warranty + basic subscription |
| Year 4-5 | 15-30% | maturing service tier |
| Mature (10+ years) | 30-50% | Apple Services-like |

Apple FY24: services 25% of revenue。Tesla autopilot subscription growth: pricing 増加。Peloton: 50%+ subscription revenue (post-restructure)。

### 8.4 Warranty Cost %

| Vertical | Median warranty cost % of revenue |
|---|---|
| Consumer electronics | 1.5-2.5% |
| Enterprise hardware | 2-4% |
| Medical devices | 2-3% |
| EV / automotive | 2-4% (early year) → 1.5% mature |

Warranty accrual の trend は product quality leading indicator: 上昇すれば quality decline。

### 8.5 Yield Rate (Manufacturing)

| Stage | Yield % |
|---|---|
| Prototype | 30-50% |
| Early production | 60-80% |
| Mature production | 95%+ |

Yield rate < 90% を mass production phase で出していると COGS が膨張する。

### 8.6 Hardware ASP (Average Selling Price) trajectory

| Vertical | ASP CAGR (5-year typical) |
|---|---|
| Consumer electronics | -5% to -10% (deflationary) |
| Smartphone (Apple class) | +2% (premium creep) |
| Smartphone (commodity) | -10%+ (commoditization) |
| Server (per unit) | -5% |
| Server (per FLOP / TB) | -20%+ (Moore's law) |
| Medical devices | +2-5% (regulatory moat) |

---

## 9. Bio / Biotech Metric Benchmarks

> **§9 の使用範囲**: Drug discovery / Pharma / Biotech / Diagnostic / Medical device with regulatory pathway。
>
> Bio 業態の特徴: phase 進行確率と R&D / pricing が中心、SaaS 系の monthly metric は適用されない。本書では FDA / PMDA approval pipeline、drug pricing、phase progression を中心に整理。

### 9.1 Phase Progression Probability (clinical trial success)

#### Aggregate (all therapeutic areas, all sponsor types)

| Transition | BIO 2023 (large N) | DiMasi 2016 | Recent peak (oncology) |
|---|---|---|---|
| Phase I → II | 52-65% | 63% | 60-65% |
| Phase II → III | 28-40% | 30% | 25-30% (oncology lower) |
| Phase III → BLA/NDA | 55-70% | 58% | 60-65% |
| BLA/NDA → FDA approval | 85-95% | 89% | 90% |
| Cumulative Phase I → approval | 7.9% (BIO 2023, all indications) | 9.6% | 5-10% (oncology lower) |

> 出典: BIO Industry Analysis 2023 (covering 2011-2020, ~12,000 trials), DiMasi 2016 Tufts CSDD, Wong/Siah/Lo 2018 (HBS)。
>
> **BIO 2023 が most-cited Tier 1**: aggregate cumulative Phase I → approval = 7.9%、これは "1 in 13" と慣例的に語られる確率。

#### By therapeutic area (Phase I → approval cumulative)

| Therapeutic area | P1 → approval | Source |
|---|---|---|
| Hematology (Heme) | 23% | BIO 2023 |
| Infectious disease | 25% | BIO 2023 |
| Ophthalmology | 17% | BIO 2023 |
| Metabolic / Endocrine | 13% | BIO 2023 |
| Cardiovascular | 12% | BIO 2023 |
| Respiratory | 7% | BIO 2023 |
| Neurology | 5-7% | BIO 2023 |
| Oncology (solid tumor) | 3-5% | BIO 2023 |
| Oncology (heme) | 8-15% | BIO 2023 |
| Psychiatry | 6-7% | BIO 2023 |

#### Modality 別 (recent trend)

| Modality | P1 → approval | 備考 |
|---|---|---|
| Small molecule (NCE) | 5-9% | traditional |
| Large molecule (biologic) | 11-14% | higher cumulative success |
| Vaccine | 16-20% | high success post-IND |
| Gene therapy | 10-15% (limited data) | newer modality |
| RNA therapeutics | 12-16% | post-COVID validated |
| Cell therapy (CAR-T) | 8-15% (rapid expansion phase) | |

### 9.2 Drug Pricing

#### List price (US, by category)

| Category | Median annual cost | Source / Tier |
|---|---|---|
| Specialty oncology | $150K-$300K | ICER reviews / Tier 1 |
| Rare disease (orphan) | $300K-$1M | NORD aggregated / Tier 1 |
| Gene therapy (one-time) | $1M-$3.5M (Zolgensma $2.1M) | press releases / Tier 1 |
| Common chronic (e.g. statin generic) | < $500 | n/a |
| Hospital biologic (oncology IV) | $100K-$200K | ICER / Tier 1 |
| Advanced specialty (rheumatoid, psoriasis) | $40K-$80K | ICER / Tier 1 |

#### Pricing thresholds (cost-effectiveness)

| Geography | Standard cost-effectiveness threshold | Source |
|---|---|---|
| US (ICER recommendation) | $50-150K / QALY | ICER Value Assessment Framework |
| UK (NICE) | £20-30K / QALY | NICE technology appraisals |
| Japan (HTA) | ¥5M / QALY (proposed) | Chuikyo proposal 2019 |
| Germany (G-BA) | benefit-based, no fixed threshold | G-BA AMNOG |

#### Net price haircut (US)

US の list price → net price (rebates / discounts) の haircut:

| Category | Median net : list ratio |
|---|---|
| Specialty without competitor | 80-90% |
| Specialty with 1-2 competitor | 60-70% |
| Crowded specialty (oncology IV with 5+) | 40-55% |
| Primary care (high-volume) | 30-50% |

### 9.3 R&D / Revenue (Pharma / Biotech)

| Stage | R&D / Revenue % | 備考 |
|---|---|---|
| Discovery / Pre-IND | ~∞ (no revenue) | full burn |
| Phase I-II | 80-100% (= R&D > revenue) | burn ratio |
| Phase III | 60-80% (if any commercial product exists) | |
| Marketed (single drug) | 25-35% | typical pharma |
| Marketed (multi-drug, large pharma) | 15-25% | scale 効果 |
| Pure biotech post-launch (1 drug) | 30-50% | early commercial |

公開企業実例:

| Company | R&D / Revenue (FY24) |
|---|---|
| Vertex | 35% |
| Regeneron | 25% |
| BioMarin | 35% |
| Alnylam | 80% (still loss-making) |
| Pfizer | 14% (mature large pharma) |

### 9.4 Cost per Phase (clinical trial)

| Phase | Median cost (USD) | Median duration | Source |
|---|---|---|---|
| Phase I | $4-15M | 1-2 years | DiMasi 2016 |
| Phase II | $15-40M | 2-3 years | DiMasi 2016 |
| Phase III | $40-300M (oncology high end $1B+) | 3-5 years | DiMasi 2016 |
| BLA/NDA filing → approval | $5-20M | 1-2 years | DiMasi 2016 |
| Cumulative Phase I → approval (capitalized cost) | $1-2.6B (DiMasi)、$985M-$2.8B (Tufts) | 8-12 years | DiMasi 2020 |

### 9.5 Patent Life & Commercial Window

| Metric | Median |
|---|---|
| Composition-of-matter patent term | 20 years from filing |
| Patent term remaining at approval | 10-13 years |
| Commercial window (launch → first generic / biosimilar) | 8-12 years (small molecule)、12-15 years (biologic) |
| Peak sales year (post-launch) | Year 5-7 |
| LOE (Loss of Exclusivity) revenue cliff | -50% to -80% in Year 1 post-LOE (small molecule) / -20-40% (biologic) |

### 9.6 Diagnostic / Medical Device

| Metric | Top | Median | Bottom |
|---|---|---|---|
| GM% (CGM, infusion pump) | 70-80% | 55-65% | 40% |
| Premium pricing vs predicate | +50-100% | +20-50% | flat |
| 510(k) clearance time (US) | 4-9 months | 6-9 months | 12+ months |
| PMA approval time | 1-2 years | 18-30 months | 3+ years |
| CE mark to MDR transition | varies | 1-2 years | longer |

### 9.7 Bio Investor IRR / MOIC anchors

(`19_ma_exit_for_founders §7` と整合)

| Class | IRR | MOIC |
|---|---|---|
| Top quartile bio fund | 25-35% | 3-5x |
| Median bio fund | 12-18% | 1.8-2.5x |
| Bottom | < 10% | < 1.5x |

Bio fund は "binary" outcome (Phase III 通過 or 失敗) で IRR distribution が SaaS より長尾化する。

---

## 10. AI / Foundation Model Metric Benchmarks

> **§10 の使用範囲**: Foundation model labs (OpenAI / Anthropic / Mistral / Cohere / etc.)、AI infrastructure (CoreWeave / Lambda Labs)、AI-native applications (Perplexity / Cursor / Glean)、AI-augmented vertical SaaS。
>
> AI 業態の特徴: token cost / inference cost / model performance benchmark / enterprise adoption rate / 人的 productivity uplift の組み合わせ。**変化が極めて速いため benchmark の vintage が短い (6 か月) 点に注意**。

### 10.1 Token Cost Evolution (USD per 1M tokens)

#### Frontier model API pricing (2020-2025)

| Model class / Year | Input ($ / 1M tokens) | Output ($ / 1M tokens) | Notes |
|---|---|---|---|
| GPT-3 (2020) | $20 | $20 | OpenAI initial pricing |
| GPT-3.5-turbo (Mar 2023) | $1.50 | $2.00 | major price drop |
| GPT-4 8K (Mar 2023) | $30 | $60 | flagship launch |
| GPT-4-turbo (Nov 2023) | $10 | $30 | -67%/-50% vs GPT-4 |
| GPT-4o (May 2024) | $5 | $15 | further reduction |
| GPT-4.1 / 4o-mini (2024) | $0.15 | $0.60 | small model commoditized |
| Claude 3 Opus (Mar 2024) | $15 | $75 | Anthropic flagship |
| Claude 3.5 Sonnet (June 2024) | $3 | $15 | mid-tier |
| Claude Haiku 3.5 (2024) | $1 | $5 | small model |
| Gemini 1.5 Pro (Q2 2024) | $7 | $21 | Google |
| Gemini 1.5 Flash (Q2 2024) | $0.075 | $0.30 | aggressive low-end |
| Llama 3.1 405B (Q3 2024, Together) | ~$3-5 | ~$3-5 | open-weight hosted |
| DeepSeek V3 (Dec 2024) | ~$0.27 | ~$1.10 | open-weight, low-cost |

#### 観察される pattern

- **Frontier model price は 12 か月で 50-70% 低下** (GPT-4 → GPT-4o)。Open-weight model は更に速く低下。
- **Inference の "intelligence per dollar"** は 2020 → 2025 で ~ 10,000x 改善 (a16z, "AI Stack" reports)。
- Pricing model は flat per-token から **batch / cached / context discount tier** へ多層化。

### 10.2 Inference Latency Benchmarks

| Tier | TTFT (Time-to-first-token) | Tokens/sec | Notes |
|---|---|---|---|
| Frontier model standard API | 200-800ms | 50-100 | GPT-4o, Claude Sonnet |
| Smaller model (Haiku, Mini) | 50-200ms | 100-300 | |
| Open-weight self-hosted (H100) | 10-50ms | 200-500 | |
| Specialized inference (Groq, Cerebras) | 5-20ms | 500-1500 | |
| Edge inference (small model) | 20-100ms | 50-200 | |

### 10.3 Per-task Cost vs Human (productivity uplift)

| Task category | Human cost (US) | AI cost | Multiple |
|---|---|---|---|
| Customer support email | $5-15 | $0.01-0.05 | 100-500x cheaper |
| Code review (junior eng) | $50-100 / hour | $0.50-2 / hour | 50-200x cheaper |
| Translation (1,000 words) | $50-100 | $0.10-1 | 50-1000x cheaper |
| Long document summary | $20-50 | $0.10-0.50 | 50-500x cheaper |
| Image generation (commercial) | $100-1,000 | $0.04-0.50 | 200-25,000x cheaper |

これらの ratio は **AI adoption の経済 incentive を示す anchor**: ROI > 100x の経済性が出る場合、enterprise adoption は需要側で driven する。

### 10.4 Enterprise AI Adoption Rate

| Metric | 2023 | 2024 | 2025 (projected) | Source |
|---|---|---|---|---|
| Fortune 500 with AI strategy | 60% | 80% | 90%+ | McKinsey AI survey 2024 / Tier 2 |
| % of employees using AI tools weekly | 10-20% | 30-45% | 50%+ | various surveys / Tier 3 |
| % of new code AI-assisted (developer) | 5-10% | 20-30% | 40%+ | GitHub Copilot reports / Tier 2 |
| AI spend as % of IT budget | 2-4% | 4-7% | 7-12% | Gartner / Tier 3 |

### 10.5 Foundation Model Lab Economics (estimate, public statements)

> ⚠️ Foundation model lab の数字は公式 disclosure が limited、本 section は **press / Information / leaked memos からの推定** に留まる (Tier 3-4)。IC memo では "estimate" と明示。

| Company | Reported Revenue | Reported Loss / FCF | Source / Year |
|---|---|---|---|
| OpenAI | $3.7B (2024 est, Information report) | ~ -$5B (2024) | The Information leaks 2024 |
| Anthropic | $1B (run-rate Oct 2024, FT) | est. negative material | FT Oct 2024 |
| xAI | est. $100M+ (2024) | n/a | press |
| Mistral | est. $100M+ (2024) | n/a | press |
| Cohere | est. $100M+ (2024) | n/a | press |

**Compute spend as % of revenue**: estimated 50-100%+ at frontier labs (= unsustainable without continued capital infusion)。

### 10.6 AI-native Application Metrics

#### Productivity SaaS (Cursor / Glean / Notion AI)

| Metric | Top quartile | Median |
|---|---|---|
| Activation rate (sign-up → 7-day retention) | 60%+ | 40% |
| ARR per FTE | $400K+ | $200K |
| Compute cost / Revenue | 15% | 25% |
| Token consumption growth (per active user) | 3-5x YoY | 2x YoY |

#### AI-augmented vertical SaaS (legal AI / medical AI)

| Metric | Top quartile | Median |
|---|---|---|
| Premium vs traditional vertical SaaS pricing | +50-100% | +20-50% |
| GM% | 70-75% (compute pass-through limited) | 60-65% |
| NRR | 130%+ | 115% |

### 10.7 AI Infrastructure (GPU-as-a-Service, Inference platforms)

| Metric | Top quartile | Median |
|---|---|---|
| GPU utilization rate | 80%+ | 60-70% |
| Revenue / GPU / month (H100) | $4-6K | $2-3K |
| Customer concentration (top 5) | < 50% | 60-80% |

### 10.8 AI Productivity Uplift Studies (research literature)

- **Brynjolfsson, Li, Raymond 2023 (NBER)**: 5,179 customer support agents で AI assistance による productivity +14% (novice agent +35%、experienced +0%)
- **Noy, Zhang 2023 (Science)**: writing task で ChatGPT 使用者 -40% time、+18% quality
- **Peng et al. 2023 (GitHub Copilot)**: developer task で +55.8% completion speed
- **Eloundou et al. 2023 (OpenAI)**: 80% of US workforce で 10%+ task が AI で affected、19% で 50%+ task affected

これらは market sizing の TAM scale で参照される。

---

## 11. Market Sizing Benchmark Patterns

> **§11 の使用範囲**: TAM / SAM / SOM の "現実性チェック" 用 benchmark。`09_market_sizing` の本論と整合。

### 11.1 Penetration Realistic Ranges by Stage

ある market (= 通常 TAM) に対して、startup が一定 stage で **現実的に取れる share の median range**:

| Stage | Penetration of TAM (median) | Penetration top quartile | Source / Tier |
|---|---|---|---|
| Pre-Seed | 0.0001-0.001% | 0.01% | a16z market sizing 2023 / Tier 2 |
| Seed | 0.001-0.01% | 0.1% | a16z / Tier 2 |
| Series A | 0.01-0.1% | 0.5% | a16z + observation / Tier 2 |
| Series B | 0.1-1% | 3% | observation / Tier 2 |
| Series C | 1-3% | 5-10% | observation / Tier 2 |
| Pre-IPO | 3-10% | 15-25% | Pitchbook segment / Tier 1 |
| Public mature | 10-30% | 40%+ | public IR aggregate / Tier 1 |

#### 注釈

- これらの "penetration of TAM" は **TAM の定義依存性が大きい** (TAM 100B vs 10B で penetration が 10x 異なる)。`09_market_sizing` の TAM 定義 (top-down vs bottom-up) を参照。
- 「Series B で TAM の 5%」を base case にしている model は **現実的に top quartile よりさらに上**。reviewer は "why are you above top quartile" を必ず質問する。

### 11.2 Geographic Split (Global IT Spend)

#### IT spend share (Gartner Global IT Spending Forecast 2024)

| Region | Share of Global IT Spend |
|---|---|
| North America (US + CA) | 35-40% |
| Western Europe | 22-26% |
| China | 13-17% |
| Asia-Pacific (ex-China, ex-Japan) | 8-12% |
| Japan | 6-8% |
| Latin America | 3-4% |
| MEA | 3-4% |

#### SaaS spend share (Gartner SaaS forecast 2024)

| Region | Share of Global SaaS Spend |
|---|---|
| US | 50-55% |
| Western Europe | 22-26% |
| Japan | 6-8% |
| China | 5-7% (regulatory headwind) |
| Other APAC | 8-10% |
| RoW | 3-5% |

#### Fintech revenue share (BCG Global Fintech 2024)

| Region | Share of Global Fintech Revenue |
|---|---|
| US | 40-45% |
| Asia-Pacific | 30-35% (China 15-20%) |
| Western Europe | 18-22% |
| Latin America + MEA | 5-8% |

### 11.3 Industry-specific TAM benchmarks (2024-2025 published forecasts)

| Industry / Segment | Global TAM 2024 | 5y CAGR forecast | Source |
|---|---|---|---|
| Global SaaS (Gartner) | $295B | 14% | Gartner 2024 |
| Cybersecurity (Gartner) | $215B | 12% | Gartner 2024 |
| Cloud infrastructure (Synergy Research) | $300B | 20% | Synergy 2024 |
| Global B2B Marketplace (a16z) | $5T GMV | 15% | a16z 2024 |
| Global Insurance Premium (Swiss Re) | $7T | 4-5% | Swiss Re Sigma 2024 |
| Global E-commerce (eMarketer) | $6T | 8-10% | eMarketer 2024 |
| AI-related software (Bloomberg Intelligence) | $135B | 40%+ | BI 2024 |
| Global Pharma (IQVIA) | $1.6T | 5-7% | IQVIA 2024 |
| Japan SaaS Market (Fuji Chimera) | ¥1.6T (~$11B) | 12-15% | Fuji Chimera 2024 |
| Japan Cloud Market (IDC Japan) | ¥6T (~$40B) | 15% | IDC Japan 2024 |

### 11.4 Penetration Curve Patterns (technology adoption)

S-curve から rough estimation:

| Adoption phase | Penetration of total addressable users | 期間 (typical) |
|---|---|---|
| Innovators (early adopters) | 0-2.5% | Year 1-3 |
| Early adopters | 2.5-16% | Year 3-7 |
| Early majority | 16-50% | Year 5-12 |
| Late majority | 50-84% | Year 10-20 |
| Laggards | 84-100% | Year 15-30+ |

(`strategy-growth:crossing-the-chasm` skill 参照)

「Series A で early adopter market を取りに行く」モデルでは、TAM × 2.5-16% を SAM に近い概念として使うのが現実的。

### 11.5 Bottom-up TAM vs Top-down 整合 check

`09_market_sizing §3` で詳述。本書では **bottom-up : top-down ratio が ±2x 以内に収まる** ことを benchmark とする。

| Ratio (bottom-up / top-down) | Acceptability |
|---|---|
| 0.5x - 2x | OK、両 method が整合 |
| 2-5x | yellow flag、説明必要 |
| > 5x または < 0.2x | red flag、一方の method が誤定義 |

---

## 12. Capital Efficiency Benchmarks

> **§12 の使用範囲**: 起業から exit までの capital efficiency。`19_ma_exit_for_founders` と integral に整合。

### 12.1 Founder Dilution at Exit

Founders の合計 ownership at exit (M&A or IPO):

| Quartile | Founders' retained ownership at exit | Source / Tier |
|---|---|---|
| Top quartile | 25%+ | Capshare / Carta 2023-2024 / Tier 2 |
| Median | 12-18% | Carta / Tier 2 |
| Bottom quartile | < 8% | Carta / Tier 2 |
| Worst case observed | 0-3% (founder removed / heavy dilution) | press cases |

#### 注釈

- Top quartile は (1) 少ない round 数、(2) 高い round-by-round multiple、(3) preferred equity 控えめな structure (= founder-friendly term sheet) の組み合わせで実現。
- "Founder dilution" は co-founder 数 / round 数 / option pool 拡大頻度に強く依存。Median 12-18% は co-founder 2-3 名、round 4-5 回前提。
- **Series Seed → A → B → C → D → IPO の 5 round で `(1 - 0.20)^5 = 33%`** が dilution 抜き retain、option pool 拡大 + 既存 anti-dilution 保護で実際は 12-18% に落ちる。

### 12.2 Investor MOIC by Fund Vintage

#### Fund-level MOIC (TVPI)

| Fund quartile | Vintage 2014-2018 (mature) | Vintage 2019-2022 (mid maturity) | Source |
|---|---|---|---|
| Top quartile | 4-5x+ | 2-3x (still maturing) | Cambridge Associates US Venture Index / Tier 1 |
| Median | 1.8-2.5x | 1.3-1.8x | Cambridge / Tier 1 |
| Bottom quartile | 0.8-1.3x | 0.7-1.1x | Cambridge / Tier 1 |

> 出典: Cambridge Associates US Venture Capital Benchmark 2024 Q3。Vintage 2019-2022 は mark-to-market 含むため markdown 影響受けやすい。

#### Deal-level MOIC by stage

(`19_ma_exit_for_founders §7` 整合)

| Stage of investment | Top quartile MOIC | Median | Bottom |
|---|---|---|---|
| Seed | 10x+ | 3x | 1x |
| Series A | 8x | 3x | 1x |
| Series B | 5x | 2.5x | 1x |
| Series C+ | 3x | 1.8x | 1x |
| Late stage growth | 2x | 1.4x | 1x |

#### IRR by stage

| Stage | Top quartile IRR | Median |
|---|---|---|
| Seed | 35%+ | 18% |
| Series A | 30% | 16% |
| Series B | 25% | 14% |
| Series C+ | 20% | 12% |
| Late growth | 15% | 10% |

### 12.3 Capital Raised / Revenue (capital efficiency)

Revenue 1 USD を作るのに何 USD の equity を投じたか。

| Class | Capital raised / ARR ratio |
|---|---|
| Top quartile (capital efficient) | < 1.0x ARR |
| Median | 1.0-2.0x ARR |
| Bottom (capital intensive) | 2.5-4x ARR |
| Worst observed | 5-10x ARR |

#### 公開企業実例 (capital raised pre-IPO / current ARR)

| Company | Capital raised pre-IPO | ARR at IPO | Ratio |
|---|---|---|---|
| Atlassian | ~$60M | ~$320M | 0.2x (極端に capital efficient、bootstrapped 期長) |
| Zoom | ~$160M | ~$330M | 0.5x |
| Slack | ~$1.4B | ~$400M (IPO 時) | 3.5x |
| WeWork (failed) | ~$13B | ~$3B (failed IPO 時) | 4.3x |
| Snowflake | ~$1.4B | ~$600M (IPO 時) | 2.3x |

**Capital raised / ARR > 3x は kill criteria に近い** (`08_investment_thesis §4`)。

### 12.4 Revenue per Investor Dollar Burned (lifetime)

`scripts/sanity_checks.py` での capital intensity check 用:

| Class | Lifetime revenue / Lifetime burn |
|---|---|
| Top | > 3x |
| Median | 1.5-2x |
| Bottom | < 1x (= raised more than ever generated) |

### 12.5 Bridge Round Frequency (efficiency proxy)

Series A → Series B 間に bridge round (extension / SAFE / convertible note) を追加した startup の比率: 2024 時点で ~ 35% (Pitchbook 2024)。

| Class | Bridge round count between primary rounds |
|---|---|
| Top | 0 |
| Median | 0-1 |
| Bottom | 2+ |

---

## 13. Sanity Check Integration

> 本 section は `scripts/sanity_checks.py` の S1-S10 判定の **閾値の根拠** を本書 benchmark に紐づける。各 S check は以下の 3 点を満たすこと: (a) applicability は `_stress_framework §4` 由来、(b) 閾値は本書 benchmark 由来、(c) recommendation field で本 reference の section を引用。

### 13.1 S1-S10 Threshold Mapping

| Sanity Check | Threshold | Source section in 21 | Benchmark basis |
|---|---|---|---|
| S1 Magic Number | > 0.75 | §4.4 | SaaSCapital 2024 median 0.7-1.0 の midpoint |
| S2 Burn Multiple | < 2 | §4.5 | Sacks framework "OK" zone 上限 |
| S3 Rule of 40 | > 40 | §4.6 | Bessemer median 25-35 を上回る "good" zone |
| S4 NRR | > 110% | §4.2 | Series A Pacific Crest median |
| S5 LTV/CAC | > 3 | §4.7 | KeyBanc top quartile cutoff |
| S6 CAC Payback | < 18 months | §4.8 | KeyBanc median 12-18 上限 |
| S7 GM% | > 70% (pure SaaS) | §4.11 | Pacific Crest median - 5pp |
| S8 TAM realism | bottom-up : top-down within 2x | §11.5 | a16z post + observation |
| S9 TV/EV ratio | < 75% | (別 ref `05_valuation_wacc §8`) | DCF discipline |
| S10 Founder dilution | > 8% retained | §12.1 | Carta bottom quartile cutoff |

### 13.2 Recommendation field 表記例

`sanity_checks.py` で issue が発見された場合の `recommendation` field の boilerplate:

```python
# S1 Magic Number 違反例
recommendation = (
    "Magic Number = {value:.2f} is below the threshold 0.75 "
    "(SaaSCapital 2024 SaaS Survey, N=1,500, median 0.7-1.0 per "
    "`21_metric_benchmarks §4.4`). "
    "Bottom quartile zone — review S&M efficiency before next round."
)

# S4 NRR 違反例
recommendation = (
    "NRR = {value:.1f}% is below the threshold 110% "
    "(Pacific Crest 2024 SaaS Survey, N=350, Series A median per "
    "`21_metric_benchmarks §4.2`). "
    "Above-median NRR is required for Series B+ thesis defensibility."
)
```

### 13.3 Stage-aware Threshold Override

S1-S10 の閾値は **stage-aware** に override されることがある。たとえば Pre-Seed で Magic Number > 0.75 を要求するのは厳しすぎる (data noise 大)。本書 §4 の各 stage column を参照して適切に loosen する:

| Sanity check | Pre-Seed threshold | Series A threshold | Series C+ threshold |
|---|---|---|---|
| S1 Magic Number | > 0.4 (loose) | > 0.75 (canonical) | > 0.6 (re-tight) |
| S2 Burn Multiple | < 4 | < 2 | < 1.5 |
| S3 Rule of 40 | > 0 (only growth side) | > 40 | > 50 |
| S4 NRR | > 95% | > 110% | > 120% |

`scripts/sanity_checks.py` 実装で、stage 入力から本表を引いて threshold を切り替える。

### 13.4 業態別 applicability matrix (`_stress_framework §4` 整合)

| Sanity check | SaaS | Marketplace | Fintech | D2C | Hardware | Bio | AI |
|---|---|---|---|---|---|---|---|
| S1 Magic Number | ○ | △ (CAC 定義注意) | △ | ○ | △ | × | ○ |
| S2 Burn Multiple | ○ | ○ | ○ | ○ | ○ | △ | ○ |
| S3 Rule of 40 | ○ | △ | △ | △ | △ | × | ○ |
| S4 NRR | ○ | △ (cohort 定義) | △ | × | × | × | ○ |
| S5 LTV/CAC | ○ | ○ | ○ | ○ | △ | × | ○ |
| S6 CAC Payback | ○ | ○ | ○ | ○ | △ | × | ○ |
| S7 GM% | ○ | ○ | △ | ○ | ○ (低 baseline) | △ | △ |
| S8 TAM realism | ○ | ○ | ○ | ○ | ○ | ○ (= addressable patient) | ○ |
| S9 TV/EV ratio | ○ | ○ | ○ | ○ | ○ | △ (binary outcome 故) | ○ |
| S10 Founder dilution | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

凡例: ○ = applicable canonical / △ = applicable with caveats / × = not applicable, skip the check。

---

## 14. IC Memo Integration

> 本 section は、`08_investment_thesis` の IC memo template に **"Performance vs Industry Benchmark"** sub-section を追加する canonical な書き方を定義する。

### 14.1 必須 sub-section: Performance vs Industry Benchmark

IC memo の 6 sub-section (Pricing Thesis / Growth Thesis / Unit Economics / Capital Plan / Exit Thesis / Risk) のうち、**Pricing / Unit Economics / Exit Thesis** の 3 sub-section に benchmark 比較表を埋め込む。

#### Template (canonical)

```markdown
## Performance vs Industry Benchmark

| Metric | Our value | Industry median | Top quartile | Quartile rank | Source |
|---|---|---|---|---|---|
| ARR Growth (Series B) | 90% | 60% | 100% | Above median | Pacific Crest 2024 (N=400) |
| NRR | 118% | 115% | 135% | Above median | Pacific Crest 2024 |
| Burn Multiple | 1.4 | 1.8 | 1.0 | Above median | Sacks framework |
| Rule of 40 | 50 | 30 | 60+ | Above median | Bessemer 2025 |
| LTV/CAC | 3.5 | 2.5 | 3.5 | At top quartile | KeyBanc 2024 |
| CAC Payback | 16 mo | 15 mo | 12 mo | Median | KeyBanc 2024 |
| GM% | 76% | 75% | 80% | At median | Pacific Crest 2024 |

> Industry benchmark source: 21_metric_benchmarks §4 (canonical SSoT)
> Quartile interpretation:
> - "Top quartile" = above P75 cutoff
> - "Above median" = between P50 and P75
> - "Median" = around P50 (±5pp tolerance)
> - "Below median" = between P25 and P50
> - "Bottom quartile" = below P25 — flag in risk section
```

### 14.2 Quartile rank の自動計算

`scripts/build_ic_memo.py` で xlsx KPI sheet から各 metric を抽出し、本書 §4-§10 の table を look up して quartile rank を判定する pseudo code:

```python
def quartile_rank(value, top, median, bottom):
    """Map a metric value to a quartile descriptor."""
    if value >= top:
        return "Top quartile"
    if value >= (median + top) / 2:
        return "Above median"
    if value >= (median + bottom) / 2:
        return "Median"
    if value >= bottom:
        return "Below median"
    return "Bottom quartile"

def benchmark_lookup(metric_name, stage, vertical):
    """Lookup canonical benchmark from 21_metric_benchmarks tables."""
    # Implementation reads the markdown tables and returns dict:
    # {top: ..., median: ..., bottom: ..., source: "..."}
    ...
```

### 14.3 IC memo "Risk" section の benchmark deviation 説明

bottom quartile に該当する metric が 1 つでもあれば、Risk section に **deviation 説明** を必ず追加:

```markdown
## Risk: Benchmark Deviation

### NRR (95% — Bottom Quartile)
Pacific Crest 2024 SaaS Survey の Series B median = 115% (per `21_metric_benchmarks §4.2`) に対し、当社 NRR は 95% で bottom quartile に位置。

**乖離の理由**:
- Q3 2024 に主要顧客 1 社 (ARR ¥80M、全体の 8%) が contract restructure で downgrade、これが ARR の一時減少要因
- Restructure 後の uplift commitment ¥120M (+50% expansion) を Q1 2025 で実装予定
- Restructure 抜きの "underlying NRR" は 112% (median 近接)

**Mitigation**:
- Customer concentration を Q1 2025 末までに top customer 8% → 5% に低減
- Q2 2025 までに NRR を 110% (median range) へ正常化
```

このように **deviation の "数値的 root cause" + "mitigation plan + timeline"** を明記しないと bottom quartile flag は IC で kill される。

### 14.4 Cherry-picking 検査

IC memo の benchmark comparison 表で **意図的に都合のいい metric だけ載せる** のは reviewer の信頼を損なう典型的失敗 (`§18.1` 参照)。本書では canonical metric set を vertical 別に列挙する:

| Vertical | Required benchmark metrics in IC memo |
|---|---|
| SaaS | ARR Growth, NRR, GRR, Burn Multiple, Rule of 40, LTV/CAC, CAC Payback, GM%, S&M / Revenue, R&D / Revenue |
| Marketplace | GMV Growth, Take Rate, NRR cohort, M+12 retention, Liquidity (search-to-fill), Frequency, AOV, Buyer/Seller ratio |
| Fintech (Lending) | NIM, Cost of risk (NPL), Approval rate, Charge-off, Capital adequacy, Cost-to-Income |
| Fintech (Payments) | TPV Growth, Take rate, Auth rate, GM%, Cost per transaction |
| D2C | Repeat rate, AOV, LTV/CAC, GM%, ROAS by channel, Inventory turns, Channel diversification |
| Hardware | GM%, Inventory turns, Service revenue %, Warranty cost %, Yield rate |
| Bio | Phase progression probabilities, R&D/Rev, Drug pricing, Patent life remaining |
| AI / Foundation Model | Token cost, Inference latency, Adoption rate, Compute / Revenue ratio |

これらはすべて IC memo template (`08_investment_thesis §6 Appendix A`) で **mandatory section** として埋める。

---

## 15. 11_KPI_Dashboard 拡張

> 本 section は xlsx 生成時に `11_KPI_Dashboard` sheet に benchmark heatmap を追加する specification。`scripts/build_model.py` の `_build_kpi_dashboard()` で実装。

### 15.1 KPI heatmap layout (xlsx sheet structure)

`11_KPI_Dashboard` sheet:

| Column | Content |
|---|---|
| A | Metric name (e.g. "NRR") |
| B | Our actual value (current period) |
| C | Industry median (from 21_metric_benchmarks lookup) |
| D | Top quartile (from 21 lookup) |
| E | Bottom quartile (from 21 lookup) |
| F | Quartile rank (formula: =IF(B>=D,"Top",IF(B>=median,"Above median",...))) |
| G | Source citation (e.g. "Pacific Crest 2024 N=400") |
| H | Vintage year (= source publication year) |
| I | Tier (1-4) |
| J | Notes / deviation explanation |

### 15.2 Conditional formatting

Column F (quartile rank) に 5-color scale を適用 (color は `_terminology §1` の機能色準拠):

| Rank | HEX (background) | Notes |
|---|---|---|
| Top quartile | `#3F8F5E` (Success) | 強い positive |
| Above median | `#D5E8DD` (Success light) | やや positive |
| Median | white | neutral |
| Below median | `#F4DCC4` (Warning light) | やや negative |
| Bottom quartile | `#C04A4A` (Danger) | flag for risk section |

### 15.3 Charts within dashboard

#### Chart 1: Radar / Spider chart

- 8-12 metric を radar chart で重ね合わせ
- Inner ring (red) = bottom quartile / Mid ring (yellow) = median / Outer ring (green) = top quartile
- 当社 actual line を solid line で重ね描く
- 直感的に "どの方向に lean" しているかを視覚化

#### Chart 2: Bar chart by metric

- 各 metric について bottom / median / top の bar + 当社 marker
- ascending order で並べると benchmark deviation の magnitude が見える

### 15.4 Update protocol

`11_KPI_Dashboard` sheet は month-end に actual を更新、benchmark は **年 1 回 (Q4)** に本書から再 lookup。Vintage year column が常に最新であることを担保する。

### 15.5 Source citation の統一

Column G は本書 §2.5 の "Source 記載必須項目" に準拠した format:

```
Pacific Crest 2024 SaaS Survey (N=350, Tier 1)
```

Excel 内では cell comment で URL / DOI を保持するのも可。

---

## 16. Mini Cases (Real-world)

> 本 section の case はすべて **公開 IR / S-1 / press release** に基づく。"推定" "estimate" 表記がある場合は Tier 3-4 の出典であることを示す。

### 16.1 Case 1: Snowflake at IPO (September 2020)

**Context**: 2020 年 9 月の Snowflake IPO は 2010 年代以降の SaaS / data infrastructure IPO で最大規模 ($3.4B raised、Day-1 valuation $70B)。各 metric を Pacific Crest 2020-2024 benchmark と対比。

| Metric | Snowflake IPO 時 | 業界 benchmark (Series C+ 標準) | Quartile rank | Notes |
|---|---|---|---|---|
| ARR (FY20 Q1) | $264M | $30M+ stage threshold | "Mega-deal" | scale |
| YoY ARR Growth | 174% | Series C+ median 30% | Top quartile (P99) | exceptional |
| NRR | 158% | median 120% | Top quartile (P95) | benchmark exceeding |
| Magic Number | ~1.5 (at IPO) | top quartile > 1.0 | Top quartile | |
| Rule of 40 | ~80 (174% growth - 100% FCF margin) | top quartile 60+ | Top quartile | growth heavy |
| GM% | 62% (at IPO) | median 75% | Below median | consumption-based 構造 |
| FCF margin | -100% | median -25% | Bottom quartile | high burn pre-IPO |

**Investment Thesis at IPO**:
- "Top quartile in growth + retention" が clear
- GM% は consumption COGS で structural、benchmark below は容認可能
- FCF margin negative は "growth efficient" zone (Magic Number 1.5+) で許容

**Outcome (FY24 update)**:
- NRR 131% (peak 158% → mathematical compression)
- GM% 67% (improvement)
- Rule of 40 = 60 (still top quartile)
- FCF margin +30% (FY24)
- IPO 時の thesis は **base case** で実現、AI workload 上振れで upside scenario 追加

> 出典: Snowflake S-1 (Aug 2020)、10-K FY24、各種 IR。

### 16.2 Case 2: WeWork failed IPO (2019) — Benchmark Deviation の典型

**Context**: 2019 年 8 月に S-1 提出、9 月 valuation 概念半減 ($47B → $20B)、10 月 IPO 撤退、2023 年 chapter 11 申請。Benchmark 比較で「red flag」が overwhelming だった典型例。

| Metric | WeWork S-1 時 | SaaS / 不動産 hybrid benchmark | Quartile | Notes |
|---|---|---|---|---|
| Revenue YoY Growth | 100%+ | Series C+ median 30% | Top quartile | growth は強い |
| Net loss / Revenue | -100%+ ($1.6B loss / $1.8B revenue) | bottom < -30% | Worst | loss intensity 異常 |
| Rule of 40 | ~ -10 (100% growth - 100%+ margin) | median 30 | Bottom quartile | deeply negative |
| Burn Multiple | > 5 (Net Burn / Net New revenue) | bottom > 3 | Worst | "time to panic" zone |
| Founder ownership at S-1 | Adam Neumann ~ 22% (super-voting) | median 12-18% | Top quartile (governance 危険) | 集中 |
| Capital raised / Revenue | ~ 4.3x ARR | bottom > 3x | Bottom quartile | capital inefficient |

**Why benchmark deviation 説明が機能しなかったか**:
- Lease liability $47B vs revenue $1.8B → "operating leverage" の説明が underwriter / investor を説得できず
- Real estate operating model (margin 5-10%) を SaaS-like multiple (15x revenue) で valued する thesis が破綻
- Governance: super-voting share + 関係者取引 (Neumann が個人で wework trademark licensed back)

**Lesson**: benchmark deviation は (1) 数値で deep red、(2) 説明が structural ではなく cosmetic、(3) governance も問題、の 3 重で kill criteria 該当。Series B+ 以降で **single benchmark deep below** ではなく **multiple benchmark の simultaneous deep below** が dealbreaker。

> 出典: WeWork S-1 (Aug 2019、後に withdrawn)、Vanity Fair / WSJ press。

### 16.3 Case 3: Notion (private) — 推定値 + Sequoia public letter による benchmark interpretation

**Context**: Notion は 2024 年 4 月時点で valuation $10B 超 (private)、2024 年 ARR ~$500M 推定 (The Information 報道)。公開 IR がないため Tier 3 推定。

| Metric | Notion 推定 (FY24) | SaaS Series C+ benchmark | Notes |
|---|---|---|---|
| ARR | ~$500M (Tier 3) | n/a | scale |
| YoY Growth | ~ 50% (Tier 3 estimate) | median 30% | Top quartile estimate |
| NRR | ~ 130% (Sequoia letter) | median 120% | Top quartile |
| Rule of 40 | "profitable" disclosed | median 30 | likely top quartile |
| GM% | ~ 80% (Tier 3) | median 75% | Top quartile |

**Caveat**: Tier 3 estimate のため IC memo に直接引用せず、"based on Sequoia public letter and The Information reporting" 等の attribution を明示。Investor から「Notion の正確な数字は」と問われたら "private、estimate per public statements only" と返答する規律。

> 出典: Sequoia Partner letters, The Information articles 2023-2024。

### 16.4 Case 4: 中堅 SaaS pre-IPO (¥10B ARR、Series C 想定)

**Context**: 仮想ケース。日本 SaaS pre-IPO 想定 (Sansan / freee 程度の規模)。Median pattern を benchmark で対比。

| Metric | 当社 actual | benchmark (Series C+ median) | Quartile rank | IC memo 表現 |
|---|---|---|---|---|
| ARR | ¥10B | n/a | n/a | scale |
| ARR YoY Growth | 35% | Bessemer 2025 median 30% | Median | "above median" |
| NRR | 112% | median 120% | Below median | "still below industry median, mitigation plan in slide 18" |
| Rule of 40 | 28 | median 30-35 | Median | "approaching median" |
| Burn Multiple | 1.6 | median 1.5 | Median | "in line" |
| LTV/CAC | 3.0 | median 2.5 | Above median | "above median, top quartile zone" |
| CAC Payback | 18 mo | median 15 mo | Below median | "extended payback due to enterprise mix shift" |
| GM% | 73% | median 75% | At median | "in line" |

**Thesis**: "Above median in growth + LTV/CAC、median in efficiency、below median in NRR (mitigation plan)、capital efficiency in line。Pre-IPO base case で **public peer comp の median multiple** で valuation thesis を justifiable に組成"

これが median company の benchmark interpretation の standard pattern。Top quartile / bottom quartile 双方を持たない balanced profile が pre-IPO の median deal で最も多い。

### 16.5 Case 5: 失敗 Marketplace — Liquidity benchmark below

**Context**: 仮想ケース (公開された fail patterns に基づく)。B2B service marketplace で Series B にて failed。

| Metric | 当社 actual at Series B | Marketplace benchmark | Quartile | Notes |
|---|---|---|---|---|
| GMV YoY Growth | 60% | median 50% (Series B) | Median | OK |
| Take Rate | 8% | median 10-15% | Below median | pricing power 不足 |
| Frequency (M+12) | 1.5x / quarter | median 3-5x | Bottom quartile | low repeat |
| Search-to-fill rate | 15% | median 20-30% | Bottom quartile | illiquid 状態 |
| M+12 cohort retention | 18% | median 30% | Bottom quartile | weak retention |
| Buyer/Seller ratio | 0.8 (= sellers > buyers) | depending on vertical, but typically 1.5+ | Bottom quartile | imbalance |

**Outcome**: Series C 調達失敗、acquihire 価格で売却 (capital raised $50M、acquihire ~$10M)。

**Lesson**: Marketplace の "fundamental liquidity metric" (search-to-fill / frequency / cohort retention) で 3 つ以上 bottom quartile に該当した時点で kill criteria。GMV growth が good でも liquidity がなければ scale しても unit economics が改善しない。

### 16.6 Case 6: AI startup — benchmark applicability の難しさ

**Context**: Anthropic / OpenAI 等 frontier model lab の estimate。IC memo で benchmark applying するのが極めて困難な業態。

| Metric | OpenAI 2024 estimate | 業界 benchmark (?) | Quartile | Notes |
|---|---|---|---|---|
| Revenue (run-rate) | $3.7B (The Information) | n/a (no peer) | n/a | unique scale |
| YoY Revenue Growth | ~3-4x | "AI-native" estimate | Top quartile | exceptional |
| Compute / Revenue | ~50%+ (Tier 4 estimate) | n/a | n/a | unsustainable absent capital infusion |
| GM% | est. 30-50% (post-compute) | SaaS median 75% | Bottom quartile | structural |
| NRR | n/a (rapid usage growth) | n/a | n/a | not measurable in standard SaaS def |

**Methodological note**: AI labs は (1) peer set がない、(2) compute cost が rapidly evolving、(3) revenue mix (API / Enterprise / Consumer) で economics が異なる。IC memo の benchmark comparison は "AI-native peer set" (Anthropic / xAI / Mistral 等) のみで行い、SaaS benchmark に強引に当てはめない。

**Lesson**: benchmark の applicability が limited な業態では、**custom benchmark frame** を IC memo で明示。e.g. "compared against AI-native peer set (Anthropic, xAI, Mistral) — note: peer N=3, Tier 3-4 estimates only"。

> 出典: The Information leaks 2024、FT Oct 2024。

### 16.7 Case 7: 日本 SaaS (Sansan / freee) 公開数字 vs Pacific Crest

**Context**: 日本上場 SaaS の代表 Sansan (2019 上場) / freee (2019 上場) の Series C 相当時点 (= IPO 時) の数字を Pacific Crest 2018-2019 と対比。

#### Sansan (FY2019 6 月期、東証マザーズ上場時)

| Metric | Sansan FY19 | Pacific Crest 2018-2019 (Series C+ median) | Quartile |
|---|---|---|---|
| Revenue YoY | 35% (¥10.2B → ¥13.8B) | median 30% | Median |
| GM% | 78% | median 75% | Above median |
| Operating margin | -25% | median -10% to 0% | Below median |
| Net dollar retention (NDR、open data 推定) | ~115% | median 110% | Above median |
| ARPU per customer (年契約) | ¥1.1M | n/a | n/a |

#### freee (FY2019 6 月期、東証マザーズ上場時)

| Metric | freee FY19 | Pacific Crest 2018-2019 (Series C+ median) | Quartile |
|---|---|---|---|
| Revenue YoY | 65% (¥3.7B → ¥6.1B) | median 30% | Top quartile |
| GM% | 82% | median 75% | Top quartile |
| Operating margin | -50% | median -10% | Bottom quartile |
| ARR growth | ~80% | median 30% | Top quartile |

**Lesson**: 日本 SaaS は revenue growth は global median 上回る場合多いが、operating margin が深く negative になる傾向 (= S&M heavy + scale-loss period 長い)。Rule of 40 では global benchmark 下回ることがある。**日本特有の post-IPO scale curve** を考慮した benchmark comparison が必要 (= "stage definition を ARR でなく国内市場 share で定義する" 等)。

> 出典: Sansan IR、freee IR、有価証券報告書 2019-2020。

---

## 17. 関連 reference との整合

### 17.1 02_saas_metrics

- **Division of labor**: `02` は metric の **定義 + 計算式 + 落とし穴**、本書は **業界 benchmark 数値**。
- **Cross-reference**: `02 §8` (業界ベンチマーク 出典別) は本書 §4 に migration 済 (重複削除予定)。`02 §8` は将来的に "本書を参照" の short-form に縮小。

### 17.2 03_business_models

- **Division of labor**: `03` は **業態 taxonomy + 構造比較**、本書は **業態別 benchmark 数値**。
- **Cross-reference**: `03` の各業態 section の末尾 "代表 benchmark" 部分は本書 §5-§10 へ link。

### 17.3 09_market_sizing

- **Division of labor**: `09` は **TAM 算出 method (top-down / bottom-up / value-based)**、本書 §11 は **TAM 現実性 benchmark**。
- **Cross-reference**: `09 §6` (TAM realism) は本書 §11.1, §11.5 と整合。

### 17.4 14_ipo_readiness

- **Division of labor**: `14` は **IPO process + listing 適格性 framework**、本書は **IPO 適格 benchmark の数値**。
- **Cross-reference**: `14 §3` (Quantitative readiness) の各 metric threshold は本書 §4 (Public approach column) を参照。

### 17.5 18_customer_value_and_pricing

- **Division of labor**: `18` は **pricing strategy + WTP framework**、本書は **pricing realization benchmark (NRR / Take rate / ARPU)**。
- **Cross-reference**: `18 §3.1` (Pricing realization rate) は本書 §4.2, §5.1 を参照。

### 17.6 19_ma_exit_for_founders

- **Division of labor**: `19` は **M&A process + tax + waterfall**、本書 §12 は **exit MOIC / IRR benchmark**。
- **Cross-reference**: `19 §7` (Investor exit IRR) は本書 §12.2 を参照。

### 17.7 _stress_framework

- **Division of labor**: `_stress_framework` は **applicability matrix の framework**、本書 §13 は **同 matrix の benchmark 数値**。
- **Cross-reference**: `_stress_framework §4` の applicability map に本書 §13.4 が integrate。

### 17.8 _master_decision_tree

- **Division of labor**: `_master_decision_tree §C` は **4 段ゲートの structure**、本書は **各ゲート閾値の benchmark 由来**。
- **Cross-reference**: `_master_decision_tree §C.1-C.4` の各閾値は本書 §13.1 と整合。

### 17.9 _terminology

- **Division of labor**: `_terminology §6` は **canonical metric definition**、本書は **同 metric の業界数値**。
- **Cross-reference**: `_terminology §6` の "industry typical" 例示 (1-2 行) は本書を参照する short-form に統一。

### 17.10 _self_review_protocol

- **追加 check (本書由来)**:
  - [ ] Benchmark citation に source name + version + N + Tier が併記されているか
  - [ ] Quartile rank が本書の P75/P50/P25 定義と一致しているか
  - [ ] 引用 vintage が 2 年以内か (年次 update 済か)
  - [ ] Cherry-picking していないか (canonical metric set §14.4 をすべて含むか)
  - [ ] Benchmark deviation (bottom quartile) について説明 + mitigation が記載されているか

これらは `_self_review_protocol §11 (Benchmark citation check)` として追加。

---

## 18. Anti-patterns

### 18.1 Cherry-picking benchmark

**症状**: 自社が strong な metric だけを benchmark 表示し、weak な metric を比較表から省く。
**害**: IC reviewer は省略を即座に検知 (= "the 4 metrics you didn't show are the ones that fail")、信頼を失う。
**修正**: §14.4 の vertical 別 mandatory metric set をすべて benchmark 表に含める。bottom quartile に該当する metric については §14.3 の deviation 説明を Risk section に書く。

### 18.2 Outdated benchmark

**症状**: 2018 年の Pacific Crest data を 2025 年の startup model に当てはめる。
**害**: 業界が大きく変化した領域 (AI cost、Cloud margin、Remote work、SaaS valuation multiple) で benchmark が現在の reality を反映しない。
**修正**: 本書 §3 (Update Cadence) を遵守。年 1 回 (Q4) review、各 metric の引用年を本文記載。**2 年以上の vintage は yellow flag**、3 年以上は red flag (stale data)。

特に注意の領域:
- **AI / Foundation Model cost**: 6 か月で 50% 変動
- **Cloud SaaS valuation multiple**: 2021 vs 2023 で 2x 変動 (ZIRP era → efficiency era)
- **Fintech NIM**: 金利環境で連動
- **D2C ROAS**: platform algorithm 変更 (iOS 14.5 ATT、Android privacy sandbox)

### 18.3 Wrong stratification

**症状**: Series A startup を Series C+ benchmark と比較、または Series C+ を Public mature と比較。
**害**: 当然 below median と出る → meaningless conclusion。reviewer は「stage が違う」と即指摘。
**修正**: 本書 §4-§10 の各 stage column を厳密に使用。stage definition (= ARR scale) を memo header に明示。

### 18.4 Survivor bias in benchmark

**症状**: Pacific Crest / OpenView survey の回答企業は **continued operation 企業** のみ → failed の 30%+ は除外されている。"median NRR 110%" は実は "median NRR among survivors"。
**害**: IC memo で "median per benchmark" と言うとき、暗黙に survivor 集合との比較。failed 含めると当社 metric の percentile が異なる可能性。
**修正**: IC memo に "benchmark per survivor cohort、failed 除外" の caveat を併記。Series A から Series B への survival rate (~35-50%) を separately 議論。

### 18.5 Self-citing chains

**症状**: 同じ benchmark 数字が a16z post → SaaStr article → LinkedIn post → 別の VC blog で繰り返され、原典に辿り着けない (= "circular citation")。
**害**: 数字の vintage / methodology / N が不明。最悪、初出が anecdotal (Tier 4) でも "everyone says 110%" 化する。
**修正**: 本書 §2.5 で source name + version + N + Tier を必須化。chain citation を見たら原典を探す。Tier 1 source に辿り着けない場合は IC memo で使用しない。

### 18.6 Misinterpreting "best-in-class"

**症状**: "Top quartile (P75)" を "Best-in-class (P90)" と混同して target に置く。Bessemer の "best-in-class" は P90 で本書の "Top quartile" (P75) より厳しい。
**害**: 達成不可能な target を model に置き、reviewer から「unreasonable assumptions」と弾かれる。
**修正**: 本書 §2.6 (Quartile 定義の不一致) を厳守。"Best-in-class" は明示的に P90 と区別、target に置くなら 1-2 metric のみ。

### 18.7 Benchmarking against "wrong vertical"

**症状**: Vertical SaaS company を generic SaaS benchmark と比較、または Marketplace を SaaS metric と比較。
**害**: vertical 特性 (例: vertical SaaS は switching cost 高 → NRR 高、Marketplace は recurring 構造が異なる) を無視した misalignment。
**修正**: 本書 §4-§10 の業態別 section を正しく選択。混合業態 (e.g. SaaS + Marketplace hybrid like Toast) は両方の benchmark を併記し weight を明示。

### 18.8 "Industry average" without quartile context

**症状**: "業界平均は 110%" としか書かない。median なのか mean なのか不明、quartile context もない。
**害**: 110% が median なら "above" は意味あるが、mean なら distribution が skew (top tier が引き上げ) で実は below median な可能性。
**修正**: 本書では mean ではなく **median (P50)** を canonical とする。"average" の語を避け "median" を使用。

### 18.9 Pre-Seed / Seed の noise を ignore

**症状**: Pre-Seed (ARR < $0.5M) startup の Magic Number / Burn Multiple を Series A benchmark と直接比較。
**害**: data noise が大きい stage で precision を装う。
**修正**: 本書 §4 の Pre-Seed / Seed column を正しく使う + early stage は **trend (4Q rolling)** で見る規律を memo に書く。

### 18.10 Benchmark を absolute target に置く

**症状**: "NRR を 120% にする" を target に置くが、それは median であり、top quartile (135%) を取るべき business model なのにそれが見えていない。
**害**: median = "good enough" の認知が形成され、ambition が縮む。investor expectation との misalignment。
**修正**: Stage 進行に伴い target を top quartile へ stretch するロードマップを明示。"Series A median を Series B で top quartile に move" を IC memo の Growth Thesis に書く。

### 18.11 Benchmark deviation の説明を skip

**症状**: bottom quartile の metric について、IC memo で "industry standard です" と書くだけで、root cause / mitigation を書かない。
**害**: reviewer 即座に「説明不足、kill」。
**修正**: §14.3 の deviation 説明 template を遵守。**root cause + magnitude + mitigation + timeline** の 4 要素を記載。

### 18.12 業態 boundary の crossing を ignore

**症状**: Hybrid business model (e.g. Marketplace + Embedded fintech) について、片方の benchmark のみで thesis を組み、もう片方の risk を見落とす。
**害**: 例: Toast (SaaS + Payment + Lending) の credit risk を SaaS benchmark で見ると Lending portion の charge-off risk が見えない。
**修正**: Hybrid business では segment 別 P&L を作り、各 segment に本書の対応する § benchmark を当てる。

---

## 付録 A. Quick Reference Card

> 「業態 × stage × metric」で **median / top quartile** を引きたい時の早見表。詳細は §4-§10 を参照。

### SaaS — Series A (ARR $2-10M)

| Metric | Median | Top quartile |
|---|---|---|
| ARR Growth | 120% | 200% |
| NRR | 110% | 130% |
| GRR | 88% | 94% |
| Magic Number | 0.7-1.0 | > 1.0 |
| Burn Multiple | 2.0 | 1.2 |
| Rule of 40 | 30-40 | 60+ |
| LTV/CAC | 2.5 | > 3.0 |
| CAC Payback | 15 mo | < 12 mo |
| GM% | 75% | 80%+ |

### SaaS — Series B (ARR $10-30M)

| Metric | Median | Top quartile |
|---|---|---|
| ARR Growth | 60% | 100% |
| NRR | 115% | 135% |
| GRR | 90% | 95% |
| Magic Number | 0.7-1.0 | > 1.0 |
| Burn Multiple | 1.5 | 1.0 |
| Rule of 40 | 25-35 | 50+ |
| LTV/CAC | 2.5-3.0 | > 3.5 |
| CAC Payback | 13-15 mo | < 12 mo |
| GM% | 75% | 80%+ |

### SaaS — Series C+ (ARR $30M+)

| Metric | Median | Top quartile |
|---|---|---|
| ARR Growth | 30% | 50% |
| NRR | 120% | 140% |
| GRR | 92% | 97% |
| Burn Multiple | 1.2 | 0.8 |
| Rule of 40 | 25-35 | 50+ |
| LTV/CAC | 3.0 | > 4.0 |

### Marketplace — Series B

| Metric | Median | Top |
|---|---|---|
| GMV Growth | 50% | 100% |
| Take Rate | vertical-specific (10-25%) | top of vertical range |
| Frequency / month | 3-5 (consumer) | 8+ |
| M+12 retention | 25-35% | 50%+ |
| Search-to-fill | 20% | 30%+ |

### Fintech (Lending) — Series B

| Metric | Median | Top |
|---|---|---|
| NIM | 10-12% | 15%+ |
| Cost of risk (NPL) | 5-8% | < 3% |
| Approval rate | 30-50% | balanced |
| Customer LTV | $500-$2K | $5K+ |

### D2C — Series B

| Metric | Median | Top |
|---|---|---|
| Repeat rate (12-mo) | 30-40% | 50%+ |
| LTV/CAC | 2-2.5 | 3.5+ |
| GM% | 50-60% | 70%+ |
| Inventory turns | 5-7 | 10+ |
| Channel concentration | 40-70% | < 40% |

### Hardware — Series C

| Metric | Median | Top |
|---|---|---|
| GM% (consumer) | 25-30% | 35-45% |
| Inventory turns | 5-7 | 10+ |
| Service revenue % (Year 5) | 15-25% | 30%+ |
| Yield rate | 90% | 95%+ |

### Bio — Phase II progression

| Metric | Median | Top |
|---|---|---|
| Phase II → III probability | 30-40% | 50%+ |
| Phase III → approval | 60-70% | 75%+ |
| Cumulative P1 → approval | 7.9% (BIO 2023 aggregate) | 15-25% (best therapeutic area) |

### AI / Foundation Model — Series A-C

| Metric | Trend |
|---|---|
| Frontier API price | -50-70% per year |
| Adoption (Fortune 500) | 60% (2023) → 80% (2024) → 90%+ (2025) |
| Compute / Revenue (frontier lab) | 50%+ (estimate, Tier 4) |
| Productivity uplift studies | +14% (CS), +56% (dev), +40% (writing) |

---

## 付録 B. Source Cheat Sheet

> 直接 URL を保存する場合の primary source list (Tier 1 中心)。

| Source | Web identifier | Update cadence |
|---|---|---|
| Pacific Crest SaaS Survey | (KeyBanc Capital Markets) | annual Q3 |
| OpenView SaaS Benchmarks | openviewpartners.com/expansion-saas-benchmarks/ | annual + quarterly |
| KeyBanc SaaS Survey | key.com (Capital Markets) | annual Q3 |
| ChartMogul SaaS Retention | chartmogul.com/reports/ | annual + monthly |
| SaaSCapital Survey | saas-capital.com/research-and-analysis/ | annual |
| Bessemer State of Cloud | bvp.com/atlas | annual Q1 |
| EMERGENCE B2B Cloud | emcap.com | annual |
| Pitchbook NVCA Venture Monitor | nvca.org / pitchbook.com | quarterly |
| SRS Acquiom M&A Deal Terms | srsacquiom.com | annual |
| BIO Industry Phase Success | bio.org | annual |
| Cambridge Associates US VC Index | cambridgeassociates.com | quarterly |
| a16z Marketplace 100 | a16z.com/marketplace-100 | annual |
| Bessemer Cloud Index | bvp.com/cloud-index | continuous |
| ICER Value Assessments | icer.org | rolling |

---

## 付録 C. Glossary 連動 (用語と benchmark の組み合わせ早見)

| 用語 (原語) | 定義 reference | 数値 reference |
|---|---|---|
| ARR / MRR | `02 §2.1` | §4.1 |
| NRR / NDR | `02 §3.2` / `_terminology §6` | §4.2 |
| GRR | `02 §3.2` | §4.3 |
| Magic Number | `02 §5.1` | §4.4 |
| Burn Multiple | `02 §5.2` | §4.5 |
| Rule of 40 | `02 §5.3` | §4.6 |
| LTV / CAC | `02 §4.1, §4.2` | §4.7 |
| CAC Payback | `02 §5.4` | §4.8 |
| Quick Ratio | `02 §5.5` | §4.9 |
| ARR per FTE | `02 §5.6` | §4.10 |
| GM% | `02 §2.4` / `06_three_statement` | §4.11 |
| Take Rate | `03 §3` | §5.1 |
| GMV | `03 §3` | §5.2 |
| NIM | `03 §5` (fintech) | §6.1 |
| MOIC / TVPI / DPI | `19 §7` / `_terminology §6` | §12.2 |
| Founder dilution | `04b §6` / `19 §6` | §12.1 |
| Phase progression probability | `03 §7` (bio) | §9.1 |
| Token cost | `03 §8` (AI) | §10.1 |

---

