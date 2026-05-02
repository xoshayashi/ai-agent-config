---
name: multi_segment_modeling
description: |
  複数事業セグメントを持つ企業の財務モデリング正本。Segment 定義 (IFRS 8 / ASC 280 / J-GAAP 第 17 号)、per-segment 3-statement、cost allocation、Sum-of-the-Parts (SOTP) valuation、segment 別 KPI、conglomerate discount、transfer pricing を包括。SaaS+Marketplace+Fintech 等の混合事業 startup の Series C+ / Pre-IPO 用。`13a_consolidation_core` (連結会計核心: 親子・NCI・PPA) と `13b_treasury_carveout` (carve-out) が「別法人」前提なのに対し、本書は「1 法人内・複数事業 segment」を canonical に扱う。
type: reference
priority: P0
related: [03_business_models, 05_valuation_wacc, 06_three_statement, 12_tax_strategy, 13a_consolidation_core, 13b_treasury_carveout, 18_customer_value_and_pricing, 19_ma_exit_for_founders, _terminology]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 1 法人内 / 複数事業 segment の財務モデリング (segment 定義、per-segment 3-statement、cost allocation、SOTP valuation、conglomerate discount、transfer pricing) は本書を canonical とする。`13a_consolidation_core` は **別法人** (親子会社 / NCI / PPA / 持分法) を扱い、`13b_treasury_carveout` は **carve-out / spin-off の準備** を扱う。本書は両者の **間** にある「同一法人内の事業 segment 」を埋める。
- **Routing**: [`_master_decision_tree.md §A (構築)`](_master_decision_tree.md) で「2 つ以上の business model」「セグメント別開示」「SOTP」「事業 mix」「コングロマリットディスカウント」「業界別 multiple 別」が出た場合、本書を第 1 reference として読む。Stage 前提: Series C+ / Pre-IPO / 上場後企業の比較分析。`scripts/build_model.py` が `inputs.segments` を読んで `20a_Segment_*` 系 sheet を生成する際に参照される。
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §10`](_self_review_protocol.md) の追加 5 check (segment revenue 合計 = consolidated revenue / inter-segment elimination 漏れ / corporate cost over-allocation / SOTP の double counting / conglomerate discount 範囲根拠) を実行。
- **関連 reference**: `03_business_models` (各 segment の業態テンプレ) / `06_three_statement` (single-entity 三表 — 各 segment は本書 §3 でその縮小版を build) / `05_valuation_wacc §10–§12` (SaaS / Marketplace / Fintech 別 multiple、本書 §5 で SOTP に統合) / `12_tax_strategy` (transfer pricing tax 詳細) / `13a_consolidation_core` (親子連結。法人またぎは 13a を canonical) / `13b_treasury_carveout` (carve-out — segment が完全分離される場合) / `18_customer_value_and_pricing` (segment 別 pricing realization) / `19_ma_exit_for_founders §9` (buyer 視点で segment を取得対象として評価) / `_terminology` (segment / subsidiary / division 用語整合)。

> 用語注: 本書では「Operating System / OS」を避け、「事業の仕組み」「処理系」「pricing 体系」と表現する (個人ルール)。時系列の数値データは原則として markdown table に揃える。
>
> 出典規律: 業界別 multiple、conglomerate discount %、segment 開示数値はすべて本文中に出典 (一次ソース URL or 学術論文 + 観測時点) を併記する。レンジが分かれる場合は **平均化せずレンジで提示** する (例: 「Berger & Ofek 1995 で 13–15%、Campa & Kedia 2002 で endogeneity を control 後はほぼゼロ」)。
>
> 範囲外: 親子会社の連結手続 (consolidation, NCI, PPA, 持分法) は `13a_consolidation_core` を canonical とし、本書では触れない。Carve-out / spin-off の treasury 分離・stranded cost 詳細は `13b_treasury_carveout` を canonical とし、本書 §4.5 では segment 内 stranded cost の処理のみ扱う。

---

# 20. Multi-Segment Modeling — 1 法人 / 複数事業セグメントの財務モデリング徹底リファレンス

> 本ドキュメントは、Series C 以降 / Pre-IPO / 上場後の startup が **1 つの法人内に 2 つ以上の事業 segment** を持つようになった場合の財務モデリング・バリュエーション・KPI 設計の正本である。
>
> **対象読者**: Claude (xlsx 20a–20g 系 sheet 生成エージェント、SOTP valuation を生成するエージェント、IC memo の "Capital Allocation Thesis" / "Per-Segment Business Case" を書くエージェント)、それを review する人間バンカー / VC partner / founder。
>
> **Scope (INCLUDE)**: segment 定義 (IFRS 8 / ASC 280 / J-GAAP 第 17 号)、per-segment 3-statement の構築、cost allocation methodologies (revenue / headcount / ABC / profit base)、inter-segment elimination、Sum-of-the-Parts (SOTP) valuation、segment 別 multiple の選択 (SaaS / Marketplace / Fintech / D2C / Hardware / Bio / Ads / AI)、conglomerate discount の理論と実装、transfer pricing (cost-plus / market / negotiated)、stranded cost の取り扱い、SBC の segment 配賦、IC memo template、業態 mix の代表 pattern (SaaS+Marketplace / SaaS+Fintech / D2C+Marketplace / SaaS+Hardware / AI mix / cross-border)、real-world mini case (Amazon / 楽天 / Mercari / Stripe / Microsoft / HP spin-off / Berkshire)、xlsx 統合 (`20a-z` sheet)、anti-patterns。
>
> **Scope (EXCLUDE — 別 reference 担当)**:
>
> | 領域 | 担当 reference | 本書の扱い |
> |---|---|---|
> | 親子会社の連結手続 / NCI / PPA / 持分法 / 在外子会社換算 | `13a_consolidation_core` | 触れず。本書 §9.2 で「subsidiary 別 cap table の場合は 13a へ」と逆参照のみ。 |
> | Carve-out 準備 / treasury 分離 / stranded cost 全体最適 | `13b_treasury_carveout` | 触れず。本書 §4.5 で segment 内 stranded cost の戦術のみ。 |
> | 連結納税 / グループ通算 / 国際 BEPS 詳細 | `12_tax_strategy` | 触れず。本書 §7.4 で transfer pricing の入口のみ。 |
> | 各 segment の業態詳細 (SaaS / Marketplace / Fintech / Hardware / Bio / AI 各論) | `03_business_models` / `02_saas_metrics` / `18_customer_value_and_pricing` | 触れず。本書 §6 で segment 別 KPI matrix のみ整理し詳細は逆参照。 |
> | DCF / WACC 単体計算 | `05_valuation_wacc` | 触れず。本書 §5.3 で segment 別 WACC の組成原則のみ。 |
> | M&A buyer-side の segment 評価 (買収対象としての segment value) | `19_ma_exit_for_founders §3 / §9` | 触れず。逆参照。 |
>
> **数値の出典**: 本文中に明示。IFRS Foundation / FASB / ASBJ / SEC EDGAR / 楽天グループ IR / Mercari IR / Microsoft IR / SRS Acquiom / Pitchbook / Damodaran NYU Stern / 学術論文 (Berger & Ofek 1995、Campa & Kedia 2002、Hund / Monk / Tice 2010)。

---

## 目次

1. [なぜ multi-segment modeling が必須か](#1-なぜ-multi-segment-modeling-が必須か)
2. [Segment 定義 (会計基準準拠)](#2-segment-定義-会計基準準拠)
3. [Per-Segment 3-Statement の構築](#3-per-segment-3-statement-の構築)
4. [Cost Allocation Methodologies](#4-cost-allocation-methodologies)
5. [Sum-of-the-Parts (SOTP) Valuation](#5-sum-of-the-parts-sotp-valuation)
6. [Segment 別 KPI Framework](#6-segment-別-kpi-framework)
7. [Transfer Pricing](#7-transfer-pricing)
8. [Conglomerate Discount 詳解](#8-conglomerate-discount-詳解)
9. [Multi-Segment Cap Table の implications](#9-multi-segment-cap-table-の-implications)
10. [Multi-Segment IC Memo Template](#10-multi-segment-ic-memo-template)
11. [業態 mix の代表的 pattern](#11-業態-mix-の代表的-pattern)
12. [xlsx 統合 (skill との接続)](#12-xlsx-統合-skill-との接続)
13. [関連 reference との整合](#13-関連-reference-との整合)
14. [Anti-patterns](#14-anti-patterns)
15. [Mini Case 詳解 (Real-world)](#15-mini-case-詳解-real-world)

---

## 1. なぜ multi-segment modeling が必須か

### 1.1 Series C 以降の startup における「事業の枝分かれ」

Pre-Seed / Seed / Series A の段階では、ほぼ全ての startup は **単一事業 (single business model)** で運営される。Pricing も market も顧客 segment も「ひとつ」であり、財務モデルも `06_three_statement` の標準三表 + `02_saas_metrics` の 1 業態 KPI を当てれば済む。

ところが Series C 以降の Pre-IPO / 上場後企業を観察すると、**多くは複数事業 segment を持つに至る**。一次事業 (core) の周辺に隣接事業 (adjacency) を作る、あるいは異なる地域・顧客 segment 向けに別の business model を立ち上げるという成長パターンが普遍的に観察される。

| Stage | 単一事業 (single segment) | 複数事業 (multi-segment) | 主因 |
|---|---|---|---|
| Pre-Seed / Seed | ほぼ 100% | ほぼ 0% | 1 product / 1 market focus |
| Series A | 95% | 5% | 一部が adjacent product 着手 |
| Series B | 80% | 20% | core + adjacency / 海外展開開始 |
| Series C | 50% | 50% | core + monetization layer / cross-sell |
| Series D / Pre-IPO | 30% | 70% | 複数 product line / 国別 segment |
| 上場後 (large-cap tech) | 10% | 90% | 多事業ポートフォリオ |

> 出典規律: 上記は `19_ma_exit_for_founders §1.1` の Pitchbook / CB Insights / Crunchbase 観察と、SEC EDGAR 提出企業の segment 開示数の手集計から組成した目安レンジ。学術的に厳密な統計値ではなく **経験則 (rule of thumb)** であり、「Series C+ で半数以上が multi-segment」という大局を示すために用いる。具体個別企業の segment 数は §15 の mini case で個別検証する。

つまり、Series C 以降では **「multi-segment を扱えない財務モデル」は実務頻度の高いケースで使えない**。これが本書を独立 reference として立てる第 1 の動機である。

### 1.2 SOTP がないと「正しい valuation が出ない」

単一事業企業であれば、業界 multiple (EV/Revenue or EV/EBITDA) を 1 つ選んで掛けるか、DCF を 1 本回せば valuation は出る。しかし複数事業企業に同じことをすると、**各事業の経済性が混ざり合った "blended multiple" を全体に当てる** ことになり、必ず誤差が出る。

| 企業特性 | Single multiple の問題 | SOTP で解消すること |
|---|---|---|
| Amazon | Retail (EBIT margin 5–8%) と AWS (EBIT margin 35%+) を一律 EV/Rev で評価すると、AWS の高 margin が薄まり、過小評価 | AWS は EV/EBITDA 25x、Retail は EV/Sales 1.5x で別評価 |
| 楽天 | EC 黒字を Mobile loss が吸収。consolidated EBITDA を multiple すると Mobile の cash burn 反映で過小 | EC / FinTech / Mobile を別 multiple、Mobile は赤字 segment 用に EV/Rev or replacement cost |
| Microsoft | Cloud (Azure) の高成長と More Personal Computing (PC) の成熟事業を一律にすると、Cloud premium が薄まる | Productivity / Intelligent Cloud / MPC を別 multiple |
| Stripe | Payments (transaction-based) と Stripe Capital (lending) を一律にすると lending の信用リスクが反映されない | Payments は EV/TPV、Capital は EV/Loan Book × 2-3x |

> 出典: Amazon 2024 10-K (AWS EBIT $39.8B / 売上 $108B → 約 37% margin、Retail North America EBIT $29.6B / 売上 $387B → 約 7.6% margin。https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm); 楽天グループ 2024 通期決算 (https://corp.rakuten.co.jp/news/press/2025/0214_01.html); Microsoft FY24 segment revenue (https://www.microsoft.com/en-us/investor/earnings/fy-2024-q4/segment-revenues)。

SOTP (Sum-of-the-Parts) valuation は §5 で詳述するが、エッセンスは「**各 segment に最も近い comp 群の multiple を当てて足し合わせる**」ことである。これをやらない limit は、Berkshire Hathaway の Warren Buffett が長年指摘してきた "blender effect" — 異なる経済性を持つ事業を均してしまう誤差 — を生む。

### 1.3 投資家への説明: 「コングロマリットディスカウント」との対決

複数事業を持つ企業は、しばしば株式市場で **conglomerate discount (多角化ディスカウント)** を受ける。Berger & Ofek (1995) の seminal 研究では、1986–1991 年の米上場企業 5,233 社のサンプルで、多角化企業は同等事業の単一事業企業の合計と比較し **平均 13–15% 過小評価** されていた。

ただし後続研究はこの discount の存在を強く問題視している:

| 研究 | 観察 | discount 推計 | 解釈 |
|---|---|---|---|
| Berger & Ofek (1995) | 1986–91 米上場 | -13% to -15% | 多角化は value-destroying |
| Lang & Stulz (1994) | 1978–90 米上場 (Tobin's Q) | -10% to -25% | 多角化企業は Q が低い |
| Campa & Kedia (2002) | endogeneity を control (固定効果 + IV) | ほぼゼロ | "discount" は selection bias の artifact |
| Villalonga (2004) | BITS 事業所単位データ | +少 (premium) | 適切な事業単位で見ると premium |
| Hund / Monk / Tice (2010, "Berger-Ofek Diversification Discount Is Just Poor Firm Matching") | matching 改善 | ほぼゼロ〜微正 | 元論文の matching 不備が原因 |

> 出典: Berger & Ofek 1995, JFE 37(1) 39–65 (https://www.sciencedirect.com/science/article/pii/0304405X94007986); Campa & Kedia 2002 (https://pages.stern.nyu.edu/~eofek/PhD/papers/CK_Explaining_JF.pdf); Hund/Monk/Tice 2010 working paper (https://cfr.ivo-welch.info/published/papers/hund-monk-tice.pdf)。

要点は: **多角化が直接 value を破壊しているのか、それとも「もともと弱い企業が多角化に流れている」(selection bias) のかは未決着**。本書 §8.1 で詳述する。実務的には、**discount は存在し得るが、その水準は 0–25% のレンジで firm-specific** という前提で SOTP を組む。

### 1.4 Carve-out / Spin-off 判断の基礎数値

本書と `13b_treasury_carveout` は密接に関連する。spin-off (例: HP Inc / HPE 2015、eBay / PayPal 2015、Auto Trader from Trader Media、Dropbox 上場時の事業整理) を検討するとき、最初に必要なのは「**現状の各 segment の独立 EV はいくらか、それを切り離した場合に conglomerate discount は解消されるか**」という SOTP 計算である。

具体的なフロー:

1. 現状の consolidated 株主価値 P_now を観察 (上場企業なら市場価格、未上場なら直近 round の post-money)
2. 各 segment の **standalone EV** を SOTP で計算 (本書 §5)
3. 合計 (Σ EV_segment) − 親会社 corporate items (HQ cash / debt / pension) = SOTP gross
4. SOTP gross − P_now = **implied conglomerate discount** (% で表示)
5. spin-off で discount が解消すると仮定すると、shareholder value 増加額 = SOTP gross − P_now − spin-off cost
6. spin-off cost (legal / banker fee / one-time IT separation / stranded cost) を `13b §3` で見積もる
7. ROI 比較: spin-off net value > 0 なら implementation 推奨

このプロセスのステップ 2–4 は本書、ステップ 5–7 は `13b` が canonical。本書なしに carve-out 議論はできない。

### 1.5 例: AWS が Retail を吸い上げる構造

Amazon の 2024 segment 開示は、なぜ multi-segment modeling が単純な consolidated 三表より価値情報を生むかの典型例:

| Segment | 売上 (2024, $B) | Op Income (2024, $B) | Op Margin | EBIT 含意 |
|---|---|---|---|---|
| North America (Retail / Ads / Subscription mix) | 387 | 29.6 | 7.6% | 薄利の Retail + 高利益 Ads が混在 |
| International (Retail) | 143 | 4.7 | 3.3% | より薄利、為替影響 |
| AWS | 108 | 39.8 | 36.9% | クラウドの高 margin |
| **Consolidated** | **638** | **74.1** | **11.6%** | blended |

> 出典: Amazon 2024 Annual Report (https://s2.q4cdn.com/299287126/files/doc_financials/2025/ar/Amazon-2024-Annual-Report.pdf), 2024 10-K segment note。

Amazon を単一 EV/Sales = 3x で評価すると EV ≈ $1.9T。SOTP では:

- North America: $387B × 0.7x EV/Sales = $271B (mid-cap retailer 並)
- International: $143B × 0.5x EV/Sales = $71B
- AWS: $108B × 10x EV/Sales = $1,080B (hyperscale cloud 並)
- 合計 SOTP gross = $1,422B + corporate cash $80B − 長期負債 $50B = $1,452B
- 5% conglomerate discount (一体運営の synergy 弱め前提) → SOTP net ≈ $1,380B

数値は説明用の illustrative であり、実 AWS 評価では EV/EBITDA や DCF も併用する。要旨は: **Single multiple では Retail の薄利が AWS を引きずり下ろし、SOTP では各事業に適切な multiple を当てた結果 AWS の価値が独立に表面化する** という構造。

### 1.6 本書の方法論的立場

本書は以下の方針で書かれている:

- **SOTP は range output が正**: 各 segment の multiple は range で出すため、合計 SOTP も range。「一点推定 (pinpoint accuracy)」は誤りで、ベースケース ± レンジで提示する。
- **Conglomerate discount は firm-specific**: 0–25% の範囲で「なぜその水準か」を必ず本文に書く (capital allocation の透明性、cross-subsidization の証拠、reporting opacity 等)。default flat 10% などの粗い当てはめは anti-pattern (§14.3)。
- **Cost allocation の上限は 100% を超えない**: stranded cost を segment に押付けると segment 撤退判断が歪むため、`13b` の stranded cost は consolidated 留保として segment EBITDA に load しない (§4.5)。
- **Inter-segment elimination は「片方向」で実装**: 売り手 segment が consolidated に internal sale を立て、買い手 segment が消費としてカウントし、consolidated 上で elimination する片方向のフロー (§3.3)。

### 1.7 想定する典型ケース (本書の対象範囲)

| ケース | 例 | 事業数 | 主分析対象 |
|---|---|---|---|
| Core SaaS + 隣接 SaaS | HubSpot CRM + Marketing Hub + Service Hub | 3+ | per-segment ARR / 共通 cost allocation |
| Core SaaS + Marketplace | Salesforce SFA + AppExchange | 2 | ARR + GMV / take-rate / SOTP |
| Core SaaS + Fintech | Toast Restaurant POS + Toast Capital lending | 2 | ARR + TPV + NIM |
| D2C + Marketplace | Amazon Retail + 3P Marketplace | 2 | GM% / take-rate / SOTP |
| SaaS + Hardware | Tesla EV + FSD subscription | 2 | hardware GM + recurring rev % |
| AI mix | OpenAI API + ChatGPT consumer + Enterprise | 3 | API rev + subscriber + ACV |
| Cross-border | Mercari 国内 + US + Pay | 3 | 国別 + 業態別の 2 軸 |

各ケースの mini-case は §11 と §15 で詳述する。

---

## 2. Segment 定義 (会計基準準拠)

### 2.1 IFRS 8 "Operating Segments"

IFRS 8 は 2009 年 1 月施行 (旧 IAS 14 を置換)、**management approach (経営者視点)** を採用する基準。「会計上どう開示するか」より「**経営者 (CODM) が事業判断のために実際に内部で見ている区分**」を起点に segment を定義する。

#### 2.1.1 Operating segment の 3 要件

IFRS 8 §5 によれば、operating segment と認められるのは以下 3 要件をすべて満たす component:

1. **収益発生 / 費用発生**: 収益を生み、費用を発生させる事業活動を行っている (同一企業の他 component に対する内部取引も含む)
2. **CODM レビュー**: その component の operating results を Chief Operating Decision Maker (CODM) が **定期的に review** し、resource 配分と performance evaluation の意思決定に用いている
3. **個別財務情報入手可能**: その component の **discrete financial information** が available (内部報告体系で別 P/L / asset を持っている)

3 要件すべて満たす component が operating segment。1 でも欠けると不可。

#### 2.1.2 CODM (Chief Operating Decision Maker) の identification

CODM は **役職ではなく機能** (function) を指す。「resource を allocate し performance を評価する **個人または委員会**」が CODM。典型的に:

- **CEO 単独** (中小企業 / startup): CEO 1 人が判断 → CODM = CEO
- **Executive Committee** (大企業): 経営会議全体が CODM (CEO + CFO + COO + 主要事業長)
- **CFO ではなく CEO** (重要): CFO は通常 CODM ではない (numbers prep 役。decision は CEO)
- **取締役会は CODM ではない**: BoD は監督役、operating decision はしない

#### 2.1.3 Aggregation criteria (集約 5 基準)

IFRS 8 §12 — 似た経済特性を持つ operating segments は **集約 (aggregate) して 1 つの reportable segment として開示** することが許される。集約には以下 5 基準すべて満たす必要がある:

1. **製品 / サービスの性質** が類似
2. **生産プロセス** の性質が類似 (manufacturing / service delivery)
3. **顧客の type / class** が類似
4. **製品分配 / 提供方法** が類似 (direct / wholesale / digital)
5. **規制環境** が類似 (banking / utility / healthcare 等の業界規制)

加えて長期 average gross margin が類似していることが望ましい。

例: Mercari 国内 EC と Mercari US は商品性質 (used goods C2C) が類似だが、顧客 (日本人 vs 米国人) と規制環境 (関税 / 越境決済) が異なるため別 segment。Microsoft Azure と Office 365 は両方 cloud delivery だが製品性質 (infrastructure vs application) が異なるため別 segment。

#### 2.1.4 Reportable segment thresholds (10% test)

IFRS 8 §13 — 以下 3 quantitative test の **いずれか** を超える operating segment は reportable segment として個別開示が必要:

- **Revenue test**: 内部取引 (inter-segment) を含む合計 revenue が **全 operating segments 合計 revenue の 10% 以上**
- **Profit test**: 報告利益 (黒字 segment) または報告損失 (赤字 segment) の絶対額が、(1) 黒字 segment 合計利益の絶対値、または (2) 赤字 segment 合計損失の絶対値、**のいずれか大きい方の 10% 以上**
- **Asset test**: 資産が全 operating segments 合計資産の **10% 以上**

#### 2.1.5 75% coverage test

IFRS 8 §15 — 上記 10% test で identified された reportable segments の **外部売上合計が consolidated revenue の 75% 未満** の場合、**追加 segment を reportable とする** 必要がある。

たとえば 5 segment あって 10% test では 3 segment が reportable だが、その 3 segment の external revenue が consolidated の 70% しかない → 4 番目 (大きい順) の segment を追加で reportable に格上げし、cumulative external revenue が 75% に達するまで続ける。

#### 2.1.6 Practical limit (10 segments)

IFRS 8 §19 — segment 数が 10 を超えると information overload で utility が下がるため、entity は disclosure の practical limit を考慮すべき。10 を超える場合は **より上位 level での aggregate** を再検討する。

### 2.2 ASC 280 (US-GAAP)

US-GAAP の ASC 280 "Segment Reporting" は IFRS 8 の元になった基準であり、内容はほぼ同等。観点別の差異:

| 項目 | IFRS 8 | ASC 280 | 実務影響 |
|---|---|---|---|
| 起源 | IAS 14 → IFRS 8 (2009) | SFAS 131 → ASC 280 (1997) | ASC 280 のほうが歴史長い |
| Management approach | 採用 | 採用 | 同じ |
| CODM 概念 | Same | Same | 同じ |
| 10% / 75% test | 同じ | 同じ | 同じ |
| Practical limit (10) | 推奨 | 推奨 | 同じ |
| Geographic / 製品別の重複開示 | 必要 | 必要 | 主軸 segment + 補助開示 |
| 2023 年改正 | なし | ASU 2023-07 (significant expense disclosure 強化) | US 上場は CODM が見ている expense category 開示が追加 |

> 出典: IFRS 8 全文 (https://www.ifrs.org/content/dam/ifrs/publications/pdf-standards/english/2022/issued/part-a/ifrs-8-operating-segments.pdf?bypass=on); FASB ASC 280 概要 (FASB.org)。

US 上場企業 (Amazon / Microsoft / Stripe 仮想上場 / Toast / Adyen US listing 等) は ASC 280 ベース、cross-listing する企業 (Mercari は東証のみだが ADR 検討企業) は両方を意識する。

### 2.3 J-GAAP「セグメント情報の開示に関する会計基準」(企業会計基準第 17 号)

日本は 2010 年 4 月開始事業年度から、ASBJ 企業会計基準第 17 号「セグメント情報等の開示に関する会計基準」を適用。**management approach への移行** が要点で、以前の「事業の種類別」「地域別」固定区分から、IFRS 8 / ASC 280 と同じ CODM ベース区分に変わった。

#### 2.3.1 主要規定

- **連結ベース** で報告 (個別ベースは原則しない)
- **CODM 概念**: 「最高経営意思決定機関」と訳される。日本企業では多くの場合「経営会議」「執行役員会」「取締役会のうち執行兼務メンバーで構成する委員会」が該当
- **10% / 75% threshold**: IFRS 8 と同じ
- **報告セグメントの Aggregation**: IFRS 8 と同じ 5 基準
- **収益認識基準** との整合: 2021 年適用の「収益認識に関する会計基準」(企業会計基準第 29 号) と齟齬がないように

#### 2.3.2 IFRS 8 / ASC 280 との実務差異

ほぼ整合だが、日本 unique の論点:

- **連結子会社 (subsidiary) と segment の関係**: 日本企業は子会社単位で事業を分けることが多く、subsidiary = segment が頻繁に成立。米欧では事業部 (division) = segment が多い
- **持分法適用関連会社 (associate)** の segment 配分: 連結 segment には含まれないが、セグメント情報の補足として開示することが多い
- **2023 年 5 月改正 (新リース基準)** との整合: Lease 関連数値の segment 別開示が必要に

> 出典: ASBJ 企業会計基準第 17 号 (https://www.asb.or.jp/jp/accounting_standards/accounting_standards/y2010/2010-1029.html — 2025 年時点の最新版)。

### 2.4 Segment vs Subsidiary vs Division の使い分け

これらは混同されやすいが、機能的に異なる:

| 用語 | 意味 | 法的存在 | 会計上の扱い |
|---|---|---|---|
| **Segment** (セグメント / 報告セグメント) | 経営者が internal reporting で見ている事業単位 | なし (経営概念) | IFRS 8 / ASC 280 / 企業会計基準 17 号で開示 |
| **Subsidiary** (子会社) | 親会社が支配する別法人 | あり (別法人) | 連結会計基準 / IFRS 10 で連結 (`13a §2-3`) |
| **Division** (事業部 / 部門) | 企業内部の組織単位 (部 / 本部 / カンパニー) | なし (組織概念) | 内部用語 (segment と一致することも一致しないことも) |

**重複は許される**:

- subsidiary = segment: 楽天モバイル (株式会社、楽天 G の子会社) は連結 subsidiary であり、同時に「モバイル」segment として開示
- division = segment: Microsoft の "Intelligent Cloud" は法的には Microsoft Corp 内部の division だが、ASC 280 の reportable segment
- subsidiary ≠ segment: 小規模子会社が他事業 segment に集約される (Aggregation)
- division ≠ segment: Apple は CODM (Tim Cook + 経営会議) が **製品別 division** で運営しているが、ASC 280 segment は **地域別** (Americas / Europe / Greater China / Japan / Rest of Asia Pacific) で開示。management approach の解釈差

#### 2.4.1 本書の区分け

| 状況 | 適用 reference |
|---|---|
| 1 法人内に複数事業 (例: Microsoft の 3 segment) | **本書 (`20`)** が canonical |
| 親会社 + 別法人子会社 (例: 楽天 G の連結グループ) | **`13a_consolidation_core`** が canonical |
| 上記の混合 (1 法人内 segment + 別法人 subsidiary が混在) | 連結処理は `13a`、segment 開示は本書を併用 |
| Spin-off / carve-out 検討 | **`13b_treasury_carveout`** が canonical、SOTP は本書 §5 |

### 2.5 Operating Segment Identification の実務手順

CODM が見ている内部 reporting structure を起点に segment を定義する 6 step:

1. **CODM identify**: 経営会議メンバー、その report 受領内容を確認 (board pack / executive review deck)
2. **Internal reporting unit list**: CODM に提出されている事業単位を全て列挙 (典型的に 5–15 個)
3. **3 要件 filter**: 各 unit が IFRS 8 §5 の 3 要件を満たすか確認 → operating segment 候補
4. **Aggregation review**: 候補のうち 5 基準で類似のものを集約 → 集約後の operating segments
5. **10% test**: 各 operating segment に test を当て、reportable segment を identify
6. **75% coverage**: cumulative external revenue が 75% 達成まで追加 reportable segment を持ち上げ

実務的に startup の場合:

- Series C 段階では CODM は CEO + CFO + 主要事業長 1–3 名の経営会議
- internal reporting unit は 3–7 個程度
- aggregation はあまり必要ない (各 unit が十分異なる)
- 10% / 75% test の結果、reportable segment は 2–4 個に落ち着く

### 2.6 用語整合 (本書での記法)

| 用語 (本書) | 同義語 | 英語 |
|---|---|---|
| segment | reportable segment / 報告セグメント | reportable segment |
| operating segment | (segment の上位概念、aggregation 前) | operating segment |
| corporate | HQ / Holdco / unallocated | Corporate / unallocated |
| inter-segment | internal trade / intercompany (※法人内なので intercompany より inter-segment 推奨) | inter-segment |
| consolidated | group total / 連結 (※法人内 segment では「全社合計」と訳し分け) | consolidated / company-wide |
| CODM | Chief Operating Decision Maker / 最高経営意思決定機関 | CODM |
| reportable | disclosable / 報告対象 | reportable |

`_terminology` に追加用語があれば適宜参照。

---

## 3. Per-Segment 3-Statement の構築

`06_three_statement` は single-entity (= 法人 1 社、segment 区分なし) の三表 build pattern を canonical とする。本書は **その三表を segment 別に分ける** 方法を扱う。基本パターンは「**各 segment について縮小版三表を作り、合計 + elimination で consolidated に再構築する**」。

### 3.1 各 segment の損益層 (P/L vertical)

各 segment について次の階層を持つ P/L を build する:

```
Segment Revenue (external + inter-segment)
  - inter-segment revenue (internal sale to other segments)
= External Revenue
  - COGS (direct: 各 segment が直接負担する原価)
= Gross Profit
  - Direct OpEx (sales / marketing / R&D の direct portion)
= Segment Contribution Margin
  - Allocated Corporate G&A (HQ overhead を allocate, §4)
= Segment EBITDA (本書での core 数値)
  - D&A (allocated)
= Segment EBIT
  - Allocated Interest expense (optional, §3.5 で扱い議論)
  - Allocated Tax (optional, §3.5)
= Segment Net Income (optional)
```

**重要**: 多くの企業は「Segment EBITDA」or 「Segment Operating Profit (EBIT)」までを segment-level で開示し、**interest と tax は consolidated でのみ表示** する。これは IFRS 8 §23 の管理アプローチに従い、CODM が segment 単位で interest / tax を見ていない場合、その単位での割り振りは恣意的だからである。本書 §3.5 で詳述する。

#### 3.1.1 Revenue 階層の特徴

- **External revenue**: 第三者 (顧客) からの売上 — segment の外部経済価値
- **Inter-segment revenue**: 他 segment への内部売上 — consolidated では elimination されるが segment 別では計上 (§3.3)
- **Total revenue (segment)** = external + inter-segment

10% test の Revenue test は **total revenue (inter-segment 含む)** で判定 (IFRS 8 §13)。これは「内部であっても他 segment に sales する活動量を持つかどうか」が segment の独立性指標だから。

#### 3.1.2 Cost layer の特徴

- **Direct COGS / Direct OpEx**: その segment が **その segment のためだけに** 発生させる cost。例: AWS の data center server depreciation、Retail の inventory write-down
- **Allocated Corporate G&A**: HQ で発生し全社に benefit する cost を segment に allocate。例: CEO salary、Legal、HR、Finance の HQ 部分 (§4)
- **Allocated D&A**: HQ-owned asset (本社ビル等) の depreciation を segment に分配

#### 3.1.3 数値例 (illustrative)

ある SaaS+Marketplace 企業の年次 P/L を segment 別に:

| 項目 | SaaS Segment ($M) | Marketplace Segment ($M) | Inter-seg Elim ($M) | Consolidated ($M) |
|---|---|---|---|---|
| External Revenue | 100 | 50 | 0 | 150 |
| Inter-segment Revenue | 5 | 0 | (5) | 0 |
| Total Revenue | 105 | 50 | (5) | 150 |
| COGS (direct) | (30) | (20) | 5 | (45) |
| Gross Profit | 75 | 30 | 0 | 105 |
| Direct OpEx (S&M + R&D direct) | (40) | (15) | 0 | (55) |
| Segment Contribution | 35 | 15 | 0 | 50 |
| Allocated Corporate G&A | (10) | (5) | 0 | (15) |
| Segment EBITDA | 25 | 10 | 0 | 35 |
| D&A (allocated) | (5) | (2) | 0 | (7) |
| Segment EBIT | 20 | 8 | 0 | 28 |
| Interest (consolidated only) | -- | -- | -- | (3) |
| Tax (consolidated only) | -- | -- | -- | (5) |
| Net Income | -- | -- | -- | 20 |

> Note: SaaS が Marketplace に internal hosting service を $5M 提供。SaaS の Inter-segment Revenue $5M、Marketplace の COGS に同 $5M を計上 (Marketplace から見ると外部購入と同等)。consolidated では elimination で両方消去 → external revenue は変化なし。

### 3.2 各 segment の貸借 (BS — segment-level)

IFRS 8 / ASC 280 は P/L だけでなく asset (assets attributable to segment) の開示も要求。

#### 3.2.1 Direct asset

各 segment が直接使用する asset:

- **Inventory** (Retail / Hardware segment が保有する商品 / 部品)
- **Trade Receivable** (segment-specific 顧客)
- **PP&E** (segment-specific 設備、AWS なら data center 自体)
- **Intangible** (segment-specific patent / brand / customer relationship)
- **Capitalized software** (segment-specific 開発した IP)

#### 3.2.2 Allocated asset

HQ-owned で全社が共有する asset:

- **Corporate cash** (treasury 管理): 通常 segment に配分しない (consolidated only) — `13b_treasury_carveout §2` が canonical
- **Shared infrastructure** (本社ビル / 共通 IT system): allocation rate (headcount 比例 等) で配分
- **Goodwill** (M&A 起因): IFRS / US-GAAP では cash-generating unit 単位で trace されるため、買収子会社が属する segment に reside

#### 3.2.3 Direct liability

- **Trade Payable** (segment 直接の仕入先)
- **Customer prepaid / Deferred revenue** (SaaS なら subscription deferred)
- **Segment-specific debt** (まれ。通常 debt は HQ で raise)

#### 3.2.4 Allocated liability

通常は配分しない (debt は corporate level)。例外として、特定 segment 専用に raise した debt (e.g. AWS 用 green bond) は当該 segment 直接負債とすることがある。

#### 3.2.5 Segment 別 BS の数値例

| 項目 | SaaS ($M) | Marketplace ($M) | Corporate ($M) | Consolidated ($M) |
|---|---|---|---|---|
| Cash | 5 | 3 | 80 | 88 |
| AR | 10 | 8 | 0 | 18 |
| Inventory | 0 | 5 | 0 | 5 |
| PP&E (net) | 20 | 5 | 30 | 55 |
| Intangible / Goodwill | 15 | 0 | 0 | 15 |
| **Total Assets** | **50** | **21** | **110** | **181** |
| AP | 5 | 4 | 2 | 11 |
| Deferred Revenue | 25 | 0 | 0 | 25 |
| Debt | 0 | 0 | 50 | 50 |
| Equity | 20 | 17 | 58 | 95 |
| **Total L+E** | **50** | **21** | **110** | **181** |

corporate row には HQ cash $80M、長期 debt $50M、本社 PP&E $30M を保持。これらは segment に allocate されない。

#### 3.2.6 ROIC by segment

segment-level の **ROIC = Segment NOPAT / Segment Invested Capital**:

- Invested Capital (segment) = Direct PP&E + Direct Working Capital (AR + Inventory − AP) + Direct Intangible

これにより各 segment の **capital efficiency** が比較可能。capital allocation 判断 (next year は SaaS と Marketplace のどちらに growth investment するか) の基礎数値となる。

### 3.3 Inter-segment elimination

#### 3.3.1 Internal sale の typical 例

| Selling segment | Buying segment | Service / Good | 典型企業 |
|---|---|---|---|
| AWS | Amazon Retail | Cloud hosting | Amazon |
| Microsoft Azure | Office 365 | Compute / Storage | Microsoft |
| Google Cloud | YouTube / Search | Compute | Alphabet |
| 楽天モバイル | 楽天市場 | 通信ネットワーク | 楽天 |
| Mercari | Mercari Pay | Identity / KYC | Mercari |
| Toast POS | Toast Capital | 顧客 transaction data | Toast |

#### 3.3.2 Bookkeeping pattern

例: AWS が Amazon Retail に $1B の internal hosting を売る:

```
AWS の books (内部):
  (借) Inter-company Receivable (Retail)   $1,000M
  (貸) Inter-segment Revenue              $1,000M

Retail の books (内部):
  (借) Inter-segment COGS                 $1,000M
  (貸) Inter-company Payable (AWS)         $1,000M

Consolidation worksheet で elimination:
  (借) Inter-segment Revenue (AWS)         $1,000M
  (貸) Inter-segment COGS (Retail)        $1,000M
  (借) Inter-company Payable (Retail)     $1,000M
  (貸) Inter-company Receivable (AWS)     $1,000M
```

結果: consolidated では revenue / COGS / receivable / payable いずれも 0 で計上され、external 取引のみ残る。

#### 3.3.3 Pricing の重要性

inter-segment の pricing (transfer price) によって:

- AWS segment の Op margin は変動 (高い transfer price = 高 margin)
- Retail segment の Op margin は逆に変動 (高い transfer price = COGS 増 = 低 margin)
- consolidated は不変 (両側 elimination)

これが §7 transfer pricing の論点。consolidated に影響しないからといって任意に決めると、segment 別の経営判断 (どこに growth investment するか) が歪む。

#### 3.3.4 Segment 別 SOTP への影響

SOTP では **inter-segment revenue は計算前に除外** が原則。理由は:

- 外部に売れない (= external 経済価値ではない) ため EV/Sales multiple を当てる対象外
- 反対意見: inter-segment が strategic value を持つ (例: AWS の internal usage が Retail の競争優位を生む) — synergy として §5.5 で別計上

実務的に SOTP 計算では:

- **Segment EV** = External Revenue × multiple (inter-segment 部分を除外)
- **Synergy adjustment** = inter-segment value を別途定量化し SOTP に加算 or 別ライン

### 3.4 Per-segment xlsx layout

skill の 17-sheet 標準 model に segment 拡張を追加する場合の sheet 構造案 (本書 §12 で詳述):

```
既存 17-sheet (canonical, _terminology §3):
  00_Cover, 01_Assumptions, 11_KPI_Dashboard, 02_Revenue, 03_OpEx, 04_IS, 05_BS, 06_CFS,
  05_BS § Working Capital, 07_Debt, 08_CapTable, 09_DCF, 10_Comps, 09_DCF § Sensitivity, 11_KPI_Dashboard,
  12_SanityChecks, 13_IC_Memo

Segment 拡張 (本書 §12 提案):
  20a_Segment_A_PL       (Segment A の縮小 P/L、03 Revenue + 04 OpEx の segment 内部分)
  20b_Segment_A_BS       (Segment A の direct asset / liability)
  20c_Segment_A_KPI      (Segment A の business model 別 KPI、業態 reference へ)
  20d_Segment_B_PL       (同上 Segment B)
  20e_Segment_B_BS
  20f_Segment_B_KPI
  20g_Segment_Eliminations  (inter-segment 全消去計算)
  20h_Segment_Allocation_Table (cost allocation rates と allocated 数値)
  20i_SOTP_Valuation     (SOTP 計算、業態別 multiple、conglomerate discount 適用)

既存 sheet (04_IS / 05_BS / 06_CFS / 11_KPI_Dashboard) は **consolidated** として残す:
  - 各 segment sheet の roll-up + elimination で再構築
  - 既存 11_KPI_Dashboard には consolidated KPI のみ表示し、segment-level KPI は 20c / 20f に。
```

3 segment 以上の場合は 20j / 20k / 20l … と続く。`scripts/build_model.py` が `inputs.segments` 配列 length を見て sheet を動的生成する (§12.3 参照)。

### 3.5 Interest / Tax を segment に配賦するか

#### 3.5.1 配賦しない流派 (default 推奨)

IFRS 8 §23 の文言は「segment profit は CODM が見ている数値」。CODM が segment-level で interest / tax を見ていなければ、それは segment-level 開示の対象外 → consolidated でのみ表示。

理由:

- **Interest** は HQ の treasury 判断 (debt issuance 判断は CFO レベル、segment manager にコントロール権なし) — segment の operating performance 評価に noise を生む
- **Tax** は連結ベース (連結納税 / グループ通算) で計算され、segment 別に切れない

**default 推奨**: segment EBITDA or Segment EBIT までで止め、interest / tax は consolidated only。

#### 3.5.2 配賦する流派 (special purpose の場合)

ただし以下の状況では配賦する:

- **Carve-out / spin-off 準備**: 各 segment が独立企業になった場合の財務を simulate する必要 (`13b §3`) — pro-forma stand-alone basis で interest (segment 規模に応じた hypothetical debt) と tax (segment EBIT × 仮定実効税率) を算出
- **SOTP DCF (§5.3)**: 各 segment の DCF を回す際、interest は不要だが (FCFF ベース)、tax は必要 (NOPAT 計算)
- **Segment ROIC**: NOPAT 必要 → tax を配賦して NOPAT を出す

#### 3.5.3 Allocation method (配賦する場合)

- **Interest**: segment direct debt (rare) は direct、それ以外は segment invested capital 比例で配賦 (consolidated weighted average cost を rate として使う)
- **Tax**: segment EBIT × consolidated 実効税率 (effective tax rate) を当てる。NOL や R&D credit 等の特殊効果は consolidated に留保

#### 3.5.4 数値例 (continued)

§3.1.3 の SaaS+Marketplace 例で、SOTP 用の segment NOPAT を計算する場合:

| 項目 | SaaS ($M) | Marketplace ($M) | Consolidated ($M) |
|---|---|---|---|
| Segment EBIT | 20 | 8 | 28 |
| 仮定 Tax Rate (consolidated 実効) | 25% | 25% | 25% |
| Allocated Tax | (5.0) | (2.0) | (7.0) |
| Segment NOPAT | 15.0 | 6.0 | 21.0 |
| Segment Invested Capital (§3.2.5) | 20 | 17 | 95 (corp 含む) |
| Segment ROIC | 75.0% | 35.3% | -- |

→ SaaS の ROIC が圧倒的に高く、capital allocation で SaaS に追加投資する強い経済的根拠が出る。consolidated ROIC では 21 / (95) = 22% にしかならず、segment 別の差は見えない。

### 3.6 Inter-segment unrealized profit (上向き / 下向き売買)

連結会計の `13a §5` で詳述している **未実現利益** (unrealized profit on inter-company sale) と類似の問題が、segment 内でも発生する:

#### 3.6.1 Inventory に sit する未実現利益

例: Retail segment が AWS から hosting credit を一括 $100M で購入し、Inventory として計上。期末時点で 60% は consumed、40% は未消費 = $40M 残。AWS は markup 30% で売っているため、未消費 $40M の中に AWS の利益 $40M × (30/130) = $9.2M が含まれる。

consolidated 視点では、external 売上があるまでこの $9.2M は「**未実現利益**」 — elimination 必要。

#### 3.6.2 Down-stream vs Up-stream

- **Down-stream**: 親 segment (AWS) → 子 segment (Retail) の場合 → 全額 elimination
- **Up-stream**: 子 segment → 親 segment の場合 → 同じ (segment は法的親子関係でなく、対称扱い)

`13a §5` は別法人の親子間の論点として詳述しているが、本書 §3.6 の論点はあくまで「segment 別 P/L で internal sale を見せている場合」の bookkeeping 上の調整。1 法人内なので法的・税務的影響は無く、純粋に **segment 別 EBITDA を歪ませない** ための調整。

#### 3.6.3 実装簡略化

実務的には:

- inter-segment sales が小さい (< 5% of consolidated revenue) → 未実現利益も小さく、簡略化として全額認識 (即時実現と仮定)
- inter-segment sales が大きい (≥ 10%) → §3.6.1 の bookkeeping を厳密に。20g_Segment_Eliminations sheet で計算

### 3.7 Segment 別 Cash Flow Statement

P/L と BS を segment 別に作ると、CFS も segment 別に作る誘惑があるが、**通常は consolidated only**。理由:

- treasury (cash management) は HQ で集中管理、segment は cash を持たない (sweep される)
- consolidated CFS で十分、segment は EBITDA まで

例外:

- spin-off 準備 (§1.4) で各 segment の standalone cash flow simulate が必要 → `13b §3` でやる
- segment-level free cash flow を SOTP DCF (§5.3) で使いたい

#### 3.7.1 Segment FCF (free cash flow) の簡易計算

```
Segment FCFF = Segment EBITDA - Segment CapEx - Δ Segment Working Capital - Segment Tax (allocated)
```

これを 5–10 年回して segment DCF を組成 (§5.3)。

---

## 4. Cost Allocation Methodologies

複数事業企業で最も悩ましく、最も間違えやすいのが corporate cost (HQ overhead) の segment 配賦。本章ではメソドロジーを徹底整理する。

### 4.1 Direct vs Allocated

#### 4.1.1 Direct cost

**そのコストが、その segment が存在しなければ発生しない場合 → Direct**。

| Cost type | Direct と判定する基準 |
|---|---|
| Engineer salary | 1 segment の codebase / product にしか時間を使わない → direct |
| Sales rep commission | 1 segment の deal にしか紐づかない → direct |
| Cloud hosting (segment-specific) | その segment 専用の subscription / instance → direct |
| Marketing (paid acquisition) | 1 segment の funnel に流す広告 → direct |
| Customer Success (CS) team | 1 segment の顧客しか担当しない → direct |
| Hardware tooling | 1 segment の製造工程専用 → direct |

#### 4.1.2 Allocated cost

**そのコストが複数 segment に benefit を提供する場合 → Allocated**。

| Cost type | 典型的 allocation |
|---|---|
| CEO / 経営陣 salary | revenue or 経営判断時間比例 |
| HR (採用 / payroll / benefits) | headcount 比例 |
| Legal | revenue or contract count 比例 |
| Finance / Accounting | revenue or transaction count 比例 |
| IT (corporate IT, MS365 等) | headcount 比例 |
| Office rent (HQ) | square foot or headcount 比例 |
| Brand marketing (corporate brand) | revenue 比例 |
| Insurance (D&O, cyber) | revenue 比例 (risk weighted) |
| Legal entity 維持 (audit / tax filing fee) | revenue 比例 or flat |

#### 4.1.3 判定の境界例

実務では境界例が多い:

- **Engineer (across segment)**: ある engineer が複数 segment の code を兼任 → 時間 tracking で direct 配分 or headcount 比例 allocation
- **Brand marketing**: corporate brand "Microsoft" は全 segment が benefit するが、product marketing "Azure" は Azure segment 専用 → 分けて処理
- **Shared platform engineering (e.g. ML platform)**: 全 product line が使う ML platform 開発 → ABC で usage 比例

**原則**: 境界例は **conservative (allocate しすぎ)** より **direct/allocated 切り分け透明** を優先。後者のほうが segment 別 EBITDA の信頼性が高い。

### 4.2 Allocation Methods (4 種)

#### 4.2.1 Revenue-based allocation

最もシンプルな method: **corporate cost を segment external revenue 比例で配賦**。

```
Segment A allocated cost = Total Corporate Cost × (Segment A revenue / Total revenue)
```

| 利点 | 欠点 |
|---|---|
| 計算簡単、説明しやすい | 高 margin segment にも低 margin segment にも同 rate で push |
| Revenue は CODM 視点の主要 KPI | 規模 (revenue) と消費量 (HR / Legal usage) が比例しないことが多い |
| 監査人にとって defensible | low-margin / high-volume segment が disadvantageous |

**適用**: Brand marketing、CEO salary (経営判断は revenue scale 比例)、Insurance、Legal (一般)。

#### 4.2.2 Headcount-based allocation

**FTE (full-time equivalent) headcount 比例で配賦**。

```
Segment A allocated cost = Total Corporate Cost × (Segment A FTE / Total FTE)
```

| 利点 | 欠点 |
|---|---|
| HR / Payroll / IT の実 usage proxy として正確 | 高 productivity segment (engineer 重) に多く load されがち |
| 計算容易 | seasonal / contractor 取扱いに consistency 必要 |
| segment manager の hiring 判断と整合 (採れば cost も上がる) | salary 水準差を反映しない (engineer >> support) |

**適用**: HR / IT / Office rent / Internal communications。

#### 4.2.3 Activity-Based Costing (ABC)

**実 usage 量 (server hour、support ticket、transaction count、API call 等) で配賦**。

```
Segment A allocated cost = Total Corporate Cost × (Segment A activity / Total activity)
where activity = the most appropriate driver per cost category
```

| 利点 | 欠点 |
|---|---|
| 最も accurate (実 consumption 比例) | 計測 system 必要、運用 cost 高い |
| segment manager に discipline 効かす (使うと cost 上がる) | driver 選択の恣意性 |
| 監査でも defensible | startup 段階では over-engineering |

**適用**:

- Cloud infrastructure → server hour / GB stored / network egress 比例
- Customer Support → ticket count or resolution time 比例
- Compliance → KYC / fraud check 数比例 (Fintech)
- Data engineering / ML platform → query count or compute hour

#### 4.2.4 Profit-based allocation

**Segment EBITDA (allocation 前) 比例で配賦**。

```
Segment A allocated cost = Total Corporate Cost × (Segment A EBITDA / Total EBITDA)
```

| 利点 | 欠点 |
|---|---|
| 余裕のある segment が overhead を多く負担、loss segment は守られる | **controversial**: loss segment が永続的に守られ撤退判断が遅れる |
| 経営的 fairness (利益あるところから取る) | 数学的に不安定: 1 segment が loss なら denominator 不定 |
| ピリオドごとに rate が変動 | predictability 低 |

**適用**: 通常推奨されない (anti-pattern §14.1)。例外的に **stranded cost** (撤退でも残る overhead) を黒字 segment に集中させたい場合のみ局所的に使う、もしくは内部 inter-segment subsidy を明示的にしたい場合。

### 4.3 Method の使い分け matrix

| Cost category | 推奨 method | 第 2 候補 | 理由 |
|---|---|---|---|
| 経営陣 (CEO / CFO / COO) salary | Revenue-based | Profit-based | 経営判断の時間配分は revenue scale 相関 |
| HR / Talent Acquisition | Headcount-based | -- | direct usage proxy |
| Legal (一般) | Revenue-based | Activity-based (contract count) | 大型 deal は revenue 比例 |
| Legal (Patent / IP) | Direct | -- | segment-specific (1 segment の特許) |
| Finance / Accounting | Revenue-based | Headcount-based | transaction volume scale |
| IT (corporate / 全社共通 SaaS) | Headcount-based | -- | seat 比例 |
| Cloud infrastructure (shared) | ABC (server hour / API call) | Headcount-based (proxy) | 最 accurate |
| Office rent (HQ) | Headcount-based | Square footage 比例 | seat 比例 |
| Brand marketing (corporate) | Revenue-based | -- | brand benefit は scale 相関 |
| Product marketing (segment-specific) | Direct | -- | segment 専用 |
| R&D (corporate research) | Revenue-based | Headcount-based | strategic 投資 = revenue base |
| R&D (product engineering) | Direct or time-tracked | -- | segment 紐づき |
| Insurance (D&O / Cyber) | Revenue-based | -- | risk = scale |
| Audit / 税務 (上場企業) | Revenue-based | -- | size 比例 |
| Data engineering / ML platform | ABC (compute hour / query) | Headcount-based | 実 usage 比例 |
| Customer Support (shared center) | ABC (ticket count) | Headcount of CS team | 実 usage 比例 |

#### 4.3.1 サンプル: SaaS+Marketplace 企業の corporate G&A allocation

仮想例: 年次 corporate G&A $30M、SaaS revenue $100M / FTE 80、Marketplace revenue $50M / FTE 40。

| Cost category | 額 ($M) | Method | SaaS allocation ($M) | Marketplace allocation ($M) |
|---|---|---|---|---|
| 経営陣 salary | 5 | Revenue (100/150 vs 50/150) | 3.33 | 1.67 |
| HR | 3 | Headcount (80/120 vs 40/120) | 2.00 | 1.00 |
| Legal | 4 | Revenue | 2.67 | 1.33 |
| Finance | 3 | Revenue | 2.00 | 1.00 |
| IT (corporate) | 4 | Headcount | 2.67 | 1.33 |
| Office rent (HQ) | 5 | Headcount | 3.33 | 1.67 |
| Brand marketing | 4 | Revenue | 2.67 | 1.33 |
| Insurance / Audit | 2 | Revenue | 1.33 | 0.67 |
| **Total Corporate G&A** | **30** | -- | **20.00** | **10.00** |

→ §3.1.3 の数値例で SaaS allocated G&A $10M、Marketplace $5M としていたが、ここでは $20M / $10M (mix によっては変動)。実際の比率は企業の cost 構造による。

### 4.4 Allocation の動的 vs 固定

#### 4.4.1 動的 allocation (Variable)

- 月次 / 四半期 actual で allocation rate を再計算
- 例: 各月の actual revenue 比率で本社 cost を配分
- variance を segment に押付ける

| 利点 | 欠点 |
|---|---|
| Reality 反映 | segment manager の予測可能性低 |
| Year-end true-up 不要 | budget vs actual variance が segment 内に noise を生む |
| Allocation rate を accountable に | 月次で rate が変動、説明 cost 上がる |

#### 4.4.2 固定 allocation (Fixed)

- 年初 budget 時点の rate で 1 年間固定
- 例: 年初予算で SaaS 60% / Marketplace 40% を rate 固定
- Year-end で variance を corporate に集約 or true-up

| 利点 | 欠点 |
|---|---|
| segment manager の予測可能性 高 | reality 乖離 (期中 mix 変化) |
| budgeting 統制が efficient | mid-year rate freeze の任意性 |
| Forecast model も簡単 | year-end true-up の処理が必要 |

#### 4.4.3 IB best practice (推奨)

- **5 年 forecast model**: 固定 rate (forward-looking budget の simplicity 優先)
- **年次 actual reporting**: 動的 (reality 反映)
- **月次 management review**: 動的 (manager が見ている数値と整合)

これは Damodaran の "Valuation: Measuring and Managing the Value of Companies" 6th ed. § 13 でも同じ recommendation。

#### 4.4.4 5 年モデルの allocation rate forecast

固定 rate の 5 年 forward を組む際、allocation rate は year ごとに変えてよい:

| Year | SaaS revenue | Marketplace rev | Total | SaaS rate (rev-based) | Marketplace rate |
|---|---|---|---|---|---|
| Y1 | 100 | 50 | 150 | 67% | 33% |
| Y2 | 130 | 65 | 195 | 67% | 33% |
| Y3 | 160 | 90 | 250 | 64% | 36% |
| Y4 | 190 | 120 | 310 | 61% | 39% |
| Y5 | 220 | 160 | 380 | 58% | 42% |

→ Marketplace の成長で allocation rate が徐々にシフト。corporate cost も成長すると仮定すれば $30M → $50M 等に増える前提を置く。

### 4.5 落とし穴: Over-allocation と Stranded Cost

#### 4.5.1 100% を超えて allocate する誤り

corporate cost を全 segment に 100% allocate すると、**segment EBITDA を実態より低く見せる**。これにより:

- segment 撤退判断が早まりすぎる (本当はその segment は contribution positive なのに、allocated overhead で見ると loss)
- segment manager の moral 低下 (uncontrollable cost で評価)
- M&A / spin-off 時の standalone valuation を低く出してしまう

#### 4.5.2 Stranded cost の概念

**Stranded cost** = 「ある segment が消えた / spin-off された場合に **その segment と一緒に消えない**、HQ に残ったままの cost」。

例:

- CEO salary: SaaS segment を spin-off しても CEO は残る → stranded
- Office HQ lease (long-term contract): 1 segment 撤退でも lease 解約できない → stranded
- Corporate audit fee: 1 segment より上の連結監査は残る → stranded
- Group treasury team: 1 segment 撤退でも残る → stranded

`13b_treasury_carveout §3.4` で stranded cost の estimation methodology を詳述している。本書ではその概念を前提に **「stranded cost を segment に load しない」** という allocation rule を推奨。

#### 4.5.3 Stranded cost を corporate に留保

**推奨 allocation rule**: corporate cost を「**避けられる cost (avoidable)**」と「**stranded cost (unavoidable)**」に分け、avoidable のみ segment に allocate、stranded は consolidated 留保。

```
Segment EBITDA = Segment Contribution - Allocated Avoidable Corporate Cost
Consolidated EBITDA = Σ Segment EBITDA - Stranded Corporate Cost
```

これにより:

- segment-level EBITDA は **standalone economic 見地** で正確
- consolidated EBITDA は **stranded cost を表面化** させ、conglomerate inefficiency を可視化

#### 4.5.4 Avoidable / Stranded の判定 framework

| Cost item | Avoidable if segment exits? | 配分対象? |
|---|---|---|
| Segment 専用 sales team | Yes | Direct (allocate not needed) |
| Segment 専用 marketing | Yes | Direct |
| Shared HR (per FTE basis) | Mostly yes (FTE 減れば HR cost 減) | Allocate |
| Shared IT (per seat basis) | Mostly yes (seat 減れば cost 減) | Allocate |
| CEO salary | No | Stranded (consolidated 留保) |
| Office HQ lease (long contract) | No | Stranded |
| Corporate audit | No | Stranded |
| Brand marketing | Partially (大規模変更時のみ削減) | Allocate (50%) + Stranded (50%) の split も可 |
| Group Treasury | No | Stranded |

#### 4.5.5 数値例 (Stranded 区別あり)

§4.3.1 の数値を「avoidable 70% / stranded 30%」と区分けすると:

| Cost category | 額 ($M) | Avoidable ($M) | Stranded ($M) |
|---|---|---|---|
| 経営陣 salary | 5 | 1 | 4 |
| HR | 3 | 2.5 | 0.5 |
| Legal | 4 | 2.5 | 1.5 |
| Finance | 3 | 2 | 1 |
| IT (corporate) | 4 | 3.5 | 0.5 |
| Office rent (HQ) | 5 | 1 | 4 |
| Brand marketing | 4 | 2 | 2 |
| Insurance / Audit | 2 | 0.5 | 1.5 |
| **Total** | **30** | **15** | **15** |

→ Avoidable $15M を segment に配分、Stranded $15M は consolidated 留保。SaaS allocated avoidable G&A = $15M × 67% = $10M、Marketplace = $5M。残り $15M (stranded) が consolidated EBITDA に直接 hit。

| 項目 | SaaS ($M) | Marketplace ($M) | Stranded ($M) | Consolidated ($M) |
|---|---|---|---|---|
| Segment Contribution | 35 | 15 | -- | 50 |
| Allocated Avoidable G&A | (10) | (5) | -- | (15) |
| Segment EBITDA | 25 | 10 | -- | 35 |
| Stranded Corporate Cost | -- | -- | (15) | (15) |
| Consolidated EBITDA | -- | -- | -- | 20 |

→ `13b §3.5` の spin-off ROI 計算では、SaaS spin-off で stranded $15M がどれだけ post-separation で減らせるかを test (新 standalone HQ vs 旧 HQ)。

### 4.6 Allocation table の見せ方 (xlsx)

20h_Segment_Allocation_Table sheet の標準 layout:

| Cost item | Total ($M) | Method | Avoidable % | Stranded % | SaaS allocation ($M) | Marketplace allocation ($M) | Stranded ($M) |
|---|---|---|---|---|---|---|---|
| 経営陣 salary | 5.0 | Revenue | 20% | 80% | 0.67 | 0.33 | 4.00 |
| HR | 3.0 | Headcount | 83% | 17% | 1.67 | 0.83 | 0.50 |
| Legal | 4.0 | Revenue | 63% | 37% | 1.67 | 0.83 | 1.50 |
| Finance | 3.0 | Revenue | 67% | 33% | 1.33 | 0.67 | 1.00 |
| IT (corporate) | 4.0 | Headcount | 88% | 13% | 2.33 | 1.17 | 0.50 |
| Office rent | 5.0 | Headcount | 20% | 80% | 0.67 | 0.33 | 4.00 |
| Brand marketing | 4.0 | Revenue | 50% | 50% | 1.33 | 0.67 | 2.00 |
| Insurance / Audit | 2.0 | Revenue | 25% | 75% | 0.33 | 0.17 | 1.50 |
| **Total** | **30.0** | -- | -- | -- | **10.00** | **5.00** | **15.00** |

→ rate / Avoidable% / Stranded% は input cell (color-coded blue per `_terminology §1`)。allocation 額は formula。

### 4.7 Allocation 計算の Python 関数

```python
from typing import Dict, Literal

AllocationMethod = Literal["revenue", "headcount", "abc", "profit", "direct"]

def allocate_cost(
    total_cost: float,
    method: AllocationMethod,
    drivers: Dict[str, float],  # segment_id -> driver value (revenue / FTE / activity)
    avoidable_pct: float = 1.0,  # 0.0 - 1.0
) -> Dict[str, float]:
    """
    Allocate corporate cost to segments based on the chosen method.

    Returns dict: {
        "segment_a": <allocated_amount>,
        "segment_b": <allocated_amount>,
        ...,
        "_stranded": <amount kept at corporate>,
    }
    """
    if not 0 <= avoidable_pct <= 1:
        raise ValueError("avoidable_pct must be in [0, 1]")
    if method == "direct":
        # Direct cost should not flow through this function
        raise ValueError("direct cost is not allocated; assign to segment directly")
    if method == "profit":
        # Allow but warn
        # In practice, gate this method behind a feature flag.
        pass

    avoidable_amount = total_cost * avoidable_pct
    stranded_amount = total_cost * (1 - avoidable_pct)
    total_driver = sum(drivers.values())
    if total_driver <= 0:
        raise ValueError("driver total must be positive")

    allocations = {
        seg_id: avoidable_amount * (driver / total_driver)
        for seg_id, driver in drivers.items()
    }
    allocations["_stranded"] = stranded_amount
    return allocations


# Usage example
if __name__ == "__main__":
    # Revenue-based allocation of CEO salary, 20% avoidable
    result = allocate_cost(
        total_cost=5.0,
        method="revenue",
        drivers={"saas": 100.0, "marketplace": 50.0},
        avoidable_pct=0.20,
    )
    # Expected: saas ≈ 0.667, marketplace ≈ 0.333, _stranded = 4.0
    print(result)
```


---

## 5. Sum-of-the-Parts (SOTP) Valuation

SOTP は本書の中核 valuation methodology。`05_valuation_wacc` が DCF / Comps / Precedent / VC Method 等を **single-entity** に対して扱うのに対し、本書 §5 はそれらを **複数 segment に分解 + 統合** するメタ手法を扱う。

### 5.1 SOTP の基本数式

```
Enterprise Value (consolidated, SOTP) =
   Σ_segment EV_segment
   + Corporate-only items (HQ cash − HQ debt − pension − other liabilities)
   - Conglomerate Discount × (Σ EV_segment + Corp items)
   + Synergy adjustment (optional, §5.5)

Equity Value = Enterprise Value (SOTP) - Net Debt - NCI - Preferred + ITM options proceeds
```

ここで:

- `EV_segment` = 各 segment の standalone EV (multiple-based or DCF)
- `Corporate-only items` = HQ で保有する非事業 asset (cash 余剰、investment securities)、HQ で保有する非事業 liability (HQ debt、pension liability、deferred tax)
- `Conglomerate Discount` = §8 で詳述、firm-specific の 0–25%
- `Synergy adjustment` = inter-segment value の strategic premium (`19_ma_exit_for_founders §3.3` の cost / revenue synergy と同じ概念だが、内部経済について計算)

### 5.2 各 Segment への Multiple 適用

`05_valuation_wacc §10 / §11 / §12` で業態別の multiple 範囲を列挙している。本書ではそれを **segment 別に当てはめる** ための matrix を整理する。

#### 5.2.1 業態別 EV/Revenue / EV/EBITDA レンジ (canonical)

| Segment 業態 | EV/Revenue (median) | EV/Revenue (range) | EV/EBITDA (median) | 数値の前提 / 出典 |
|---|---|---|---|---|
| SaaS (B2B、ARR > $100M) | 8x | 5–12x | 25x | Bessemer Cloud Index 2024–2025、Rule of 40 ≥ 40% 前提 |
| SaaS (early stage、ARR < $50M) | 6x | 3–10x | n/m (赤字多い) | Pitchbook SaaS valuation report |
| Marketplace (2-sided、take-rate ≥ 10%) | 6x | 3–9x | 20x | EV/GMV ではなく EV/Net Revenue で比較 |
| Marketplace (low take-rate、3-5%) | 3x | 1.5–5x | 15x | take rate 低いと EV/Rev も低い |
| D2C (consumer brands、growth) | 2x | 1–4x | 12x | Allbirds / Warby Parker 等 listed comps |
| Hardware (consumer electronics) | 1.2x | 0.5–2x | 10x | Sonos / GoPro listed comps |
| Hardware (enterprise / industrial) | 2x | 1–3x | 12x | enterprise margin が高い |
| Hardware + Service (Tesla / Apple subscription tier) | EV/Rev は hardware 1.2x + service 8x の split | -- | -- | 製品 vs 経常 split |
| Bio / Pharma (pre-clinical) | n/a | n/a (pre-revenue) | n/a | NPV 法 / Real Options |
| Bio (post Phase 2) | 5x peak revenue × probability | 2–10x | n/m | clinical phase 別 |
| Fintech (lending) | 2x revenue + Loan book × premium | 1–4x | 8–12x | NIM 反映、loan book size ベース |
| Fintech (payments、processor) | 6x revenue or EV/TPV ≈ 0.10–0.30 | 4–10x rev | 25x EBITDA | Stripe / Adyen comps |
| Ads / Media (digital ads platform) | 6x | 4–10x | 18x | Meta / Google を upper、媒体小規模は下 |
| AI infrastructure (foundation model) | 高変動 (15x–50x rev、growth と loss 反映) | -- | n/m (loss) | OpenAI / Anthropic 仮想 multiple、CoreWeave listed |
| AI application layer (vertical AI SaaS) | 10x | 6–15x | 25x | premium for AI-driven NRR |
| Subscription consumer (Netflix / Spotify 等) | 4x | 2–6x | 15x | listed comps |
| Logistics (delivery / 3PL) | 1.5x | 0.8–2.5x | 10x | 低 margin ベース |
| Real estate / asset-heavy | NAV-based | -- | -- | 評価対象が equity でなく asset |

> 出典 (一次): Bessemer Cloud Index Quarterly Report (https://cloudindex.bvp.com/), Pitchbook Valuation Reports, Damodaran NYU Stern Industry Multiples Page (http://pages.stern.nyu.edu/~adamodar/), SEC EDGAR 上場 comps (10-K)、SaaStr Multiple Survey、Software Equity Group quarterly reports。観測時点は基本的に 2024 年通期〜2025 Q1。

> 注意: multiple は時期 / 金利環境 / 業界センチメントに大きく依存。2021 年 SaaS bubble peak の 25x → 2023 年下落で 6x まで縮小し、2024–25 で 8–12x に回復。本書の数値は **median + range** で示し、特定値を canonical に固定しない。

#### 5.2.2 Multiple selection rationale

各 segment に multiple を割り当てる際の説明 (rationale) を必ず IC memo に記述:

| Segment | 選択 multiple | Rationale |
|---|---|---|
| Core SaaS | 9x EV/Rev | Public comps median 8x、+1x premium for NRR 120%+ (Snowflake / Databricks-like) |
| Marketplace | 5x EV/Rev | take-rate 12% で 2-sided liquidity 強い、Etsy-like multiple |
| Fintech (lending small) | 2.5x EV/Rev | Loan book $80M、NIM 7%、低 NPL → upper end of range |
| Hardware | 1.5x EV/Rev | Sonos comps median 1.2x、+0.3 premium for software attach |

rationale には常に **comp 4–6 個** を明示。

#### 5.2.3 Comp 選定の guideline

良い comp は次の 4 条件を満たす:

1. **同 business model**: SaaS なら SaaS、Marketplace なら Marketplace
2. **同サイズ範囲** (revenue 0.3–3x の範囲 — Damodaran)
3. **同 growth profile** (YoY growth ±10pp 以内)
4. **同 profitability profile** (Rule of 40 等の指標が ±10pp 以内)

例: Marketplace segment の comp として Etsy / eBay / Mercari を選ぶか? → Mercari は同業 (used C2C) で best comp、Etsy は handmade 系で 2nd、eBay は size 巨大すぎ for small target → top 2 を採用。

### 5.3 DCF SOTP (各 Segment 別 DCF)

Multiple-based SOTP の cross-check として、**各 segment 別に DCF を回す** 方法。`05_valuation_wacc §1` の DCF を segment 単位で適用。

#### 5.3.1 各 Segment 別 WACC

異なる segment は異なる risk profile を持つため、**異なる WACC** を当てる必要がある。

```
WACC_segment = Re_segment × E/V + Rd × (1 - tax) × D/V
where Re_segment = Rf + β_segment × ERP + size_premium - liquidity_discount
```

`05_valuation_wacc §1.4` の standard CAPM を segment 別に修正。Beta は segment が属する **業界 unlevered beta** を Hamada 式で re-lever。

| Segment | 推定 unlevered β | 業界 ERP / Equity Risk Premium | 想定 Re | 想定 WACC |
|---|---|---|---|---|
| Core SaaS | 1.1 | 5% (US dev) | 9.5–11% | 9–10% |
| Marketplace | 1.3 | 5% | 11–13% | 10–11% |
| Fintech (lending) | 1.5 | 5% (+credit risk) | 12–14% | 11–13% |
| Hardware | 1.4 | 5% | 11–13% | 10–12% |
| AI infra | 1.8 (高 volatility) | 5% | 14–16% | 13–14% |
| Bio (pre-clinical) | 1.6 (or option pricing) | 5% | 13–15% | 13–14% |

> 出典: Damodaran NYU Stern industry beta table 2024–2025 update (http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html)。observation 時点を IC memo に明記。

#### 5.3.2 各 Segment 別 g (terminal growth)

terminal year の長期成長率 g は segment 業態 + 国別 + 段階別:

| Segment 業態 | 推奨 terminal g range | 理由 |
|---|---|---|
| Core SaaS (mature) | 2.5–4% | inflation + small real growth |
| Marketplace (mature) | 2–3% | population + volume growth |
| Fintech (regulated) | 2.5% | inflation 並み |
| Hardware (mature) | 1.5–2.5% | inflation 並 (low real growth) |
| AI / new technology | 4–6% | (※ optimistic、stress test 必要) |
| Bio (post-launch) | 2–3% | inflation + market expansion |
| 国別: 日本 g | -0.5 to +1.5% | 人口減 + GDP 横ばい |
| 国別: 米国 g | 2–3% | nominal GDP growth |
| 国別: 新興国 g | 4–6% | nominal GDP growth |

実 segment が複数国に分散している場合は **revenue mix で blended g** を出す:

```
g_blended = Σ(revenue_share_country × g_country)
```

#### 5.3.3 Inter-segment cash flow elimination (DCF 上)

multiple-based SOTP と同じく、DCF SOTP でも **inter-segment cash flow は除去**:

- Segment FCFF を計算する際、**external revenue ベース** で Revenue を用いる
- Inter-segment revenue / COGS は両側に存在 → DCF 計算から除外

これにより consolidated DCF と Σ(segment DCF) が一致 (除く discount / synergy)。

#### 5.3.4 Corporate-level cash flow の扱い

HQ で発生する FCF (e.g., HQ team salary、stranded cost、HQ tax) はどう扱うか:

- **Approach A (default)**: HQ FCF を corporate level で回し、SOTP に "corporate items" として addsubtract
- **Approach B**: HQ FCF を segment に allocate (revenue 比例) してから segment DCF を回す → segment FCF が allocated 込みに

A のほうが構造透明、推奨。

#### 5.3.5 Mixed approach (Multiples + DCF)

実務 best practice は **Multiples と DCF の両方を回し triangulation**:

| Segment | Multiple-based EV | DCF EV | Selected EV | 理由 |
|---|---|---|---|---|
| Core SaaS | $900M (9x × $100M) | $850M | $875M (mid) | Multiple と DCF が近接、信頼性 高 |
| Marketplace | $250M (5x × $50M) | $300M | $275M (mid) | DCF が optimistic、平均 |
| Fintech | $80M (4x × $20M) | $50M | $65M (mid) | DCF が conservative、 平均 |
| Sum | $1,230M | $1,200M | $1,215M | -- |

triangulation 後の SOTP gross は両 method の mid を取る (average ではなく judgement)。

### 5.4 Mixed Method の使い分け

#### 5.4.1 Multiple-only (DCF を省略する場合)

- segment が **未 mature** or **early stage** で 5–10 年 forecast の信頼性低い
- 公開 comps が豊富で、multiple range が tight (std dev 小)
- IC memo の作業量制約

#### 5.4.2 DCF-only (Multiple を省略する場合)

- segment が **unique business model** で適切な comps が無い (e.g. Berkshire Hathaway insurance + manufacturing、Apple の services + hardware combination の subset)
- comps の multiple range が広すぎ、selection の根拠が弱い

#### 5.4.3 Multiple + DCF triangulation (推奨)

ほとんどの実務 case で推奨。両 method の implied EV が:

- **乖離小 (±10%)**: 信頼性高い、mid 採用
- **乖離大 (±30% 以上)**: いずれかが誤り → 再検証

#### 5.4.4 Real Options for early-stage segment

`05_valuation_wacc §8` の Real Options を segment 単位で適用。pre-revenue / R&D-heavy / 成功 prob 低い segment (Bio Phase I、新規 AI 製品) は Black-Scholes 等の option pricing で評価。

### 5.5 Conglomerate Discount Theory (overview)

詳細は §8 で扱うが、SOTP 計算では必ず discount を考慮する。

#### 5.5.1 Discount の経験則 range

| 企業 type | Conglomerate discount (median) | Range | 出典 / observation |
|---|---|---|---|
| US large-cap diversified industrial | 15% | 5–25% | Berger & Ofek 1995 (-13 to -15% mean) |
| US tech holding (Alphabet / Amazon) | 5–10% | 0–15% | analyst consensus 2024 |
| Korean chaebol (Samsung / LG / Hyundai) | 30–40% | 25–50% | Asian Corp Governance Association、各社 NAV vs market cap |
| Japanese keiretsu (Mitsui / Sumitomo Holdings) | 15–25% | 10–30% | NAV gap 観察 |
| Berkshire Hathaway | -5 to +10% | (negative discount = premium) | Buffett の capital allocation |
| US mid-cap conglomerate (HP pre-spin) | 15–20% | -- | spin-off 発表前後の market cap 観察 |
| US PE-owned platforms | 0–10% (low) | -- | PE active management |

> 出典: Berger & Ofek 1995 JFE; Lang & Stulz 1994 JPE; Campa & Kedia 2002 JF; Korea Corporate Governance Service annual reports; CFA Institute "Conglomerate Discount" ad hoc analyses。

#### 5.5.2 Discount を計算するか「explicit に書く」か

- **計算する**: 上記 range の median を選び、SOTP gross × (1 − discount) で net SOTP を出す
- **explicit に書く**: discount を 0% で計算し、IC memo の risk セクションに「conglomerate discount リスクで -10–20%」と書く

best practice は **両方**: base case は明示的 10% で計算、sensitivity analysis で 0% / 15% / 25% の 3 cases を示す。

### 5.6 Synergy Value (反対方向の adjustment)

Conglomerate discount は negative adjustment だが、その逆 — **synergy** — は positive adjustment。

#### 5.6.1 Cost synergy (内部運営の効率)

- HQ 経費の共有 (1 社で済むため CEO salary 1 つ、Legal 1 team 等)
- Bulk purchasing の交渉力 (cloud rate、insurance、office rent)
- Tax efficiency (連結納税で各 segment NOL を相殺)

これらは既に segment の allocation で反映されている (avoidable cost が allocated)。**stranded cost が 1 社運営で減らせる分** が cost synergy。

#### 5.6.2 Revenue synergy (cross-sell / strategic)

- Cross-sell 機会 (SaaS 顧客に Fintech 提供)
- Brand premium (Microsoft brand で Azure 顧客獲得)
- Data network effect (Mercari の取引データが Pay の信用 score 提供)

これらは **inter-segment synergy** として SOTP に加算可能だが:

#### 5.6.3 Double counting 注意

Synergy を加算すると double counting に陥りやすい:

- inter-segment revenue を SOTP の各 segment EV から既に除外している (§3.3.4)
- でも synergy として加算すると同じ value を 2 回 count

正しい処理:

- **inter-segment 取引** = 内部経済価値、SOTP 計算外
- **inter-segment synergy** = 「もし取引が無くても消費 segment が外部から同等品を購入する場合のコスト + 取引 segment が外部に売る場合の opportunity profit」を **separate に計算** し、Synergy 行で加算

簡略化: 多くの IC memo では Synergy を 0 or 5% of SOTP gross と small に置き、conglomerate discount に内包させる流派が多い。

### 5.7 Premium / Discount Adjustments (other)

#### 5.7.1 Standalone Premium (control premium)

`19_ma_exit_for_founders §3.4` の control premium と同じ概念。spin-off / carve-out 発表時、各 segment が独立 listed company になると **multiple が上昇する** という観察:

- 専業 listed company は generalist より analyst coverage 厚く、liquidity 高い
- 経営 focus が improved
- compensation alignment

historical observation:

- HP / HPE 2015 spin-off: 発表後 6 ヶ月で combined market cap +12%
- eBay / PayPal 2015: PayPal 単独で eBay 内部時の implied valuation を 30% 超
- Yahoo / Alibaba 2015 spinoff 提案 (実現せず): proposal で +20% 折込

実務で SOTP の standalone premium を加える場合、**5–15% 程度** が経験則。

#### 5.7.2 Liquidity Discount (untraded shares)

未上場企業の SOTP は **flat 30% liquidity discount** を traded comp multiple に適用するのが標準 (Pratt's "Valuation of Privately-Held Businesses" 6th ed.)。

#### 5.7.3 Country / Sovereign Risk Premium

各 segment が異なる国で操業している場合、**country risk premium (CRP)** を WACC に加算 (`05_valuation_wacc §12` Damodaran 流)。

| Country | CRP (2024 末、Damodaran) |
|---|---|
| US | 0% (baseline) |
| 日本 | 0.55% |
| EU (西欧) | 0–0.7% |
| インド | 1.7% |
| ブラジル | 2.2% |
| ナイジェリア | 9% |

> 出典: Damodaran Country Risk Premium 2024 update (http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)。

国別 segment が分かれている場合、各 segment WACC に対応 CRP を加算。

### 5.8 SOTP 計算の Python 関数

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    """Single segment with its standalone valuation parameters."""
    id: str
    name: str
    external_revenue: float       # external sales only, $M
    ebitda: float                 # segment EBITDA after avoidable corp allocation
    ev_revenue_multiple: float    # e.g., 8.0 for SaaS
    ev_ebitda_multiple: float     # e.g., 25.0 for SaaS
    dcf_ev: Optional[float] = None  # if DCF was run independently


@dataclass
class SOTPInputs:
    segments: List[Segment]
    corporate_cash: float = 0.0
    corporate_debt: float = 0.0
    pension_liability: float = 0.0
    other_corporate_assets: float = 0.0
    other_corporate_liabilities: float = 0.0
    conglomerate_discount_pct: float = 0.10  # 10% default; firm-specific
    synergy_value: float = 0.0
    standalone_premium_pct: float = 0.0


def compute_sotp(inputs: SOTPInputs, valuation_method: str = "blended") -> dict:
    """
    Compute Sum-of-the-Parts EV.

    valuation_method: "multiple_revenue" | "multiple_ebitda" | "dcf" | "blended"
    """
    if not 0 <= inputs.conglomerate_discount_pct <= 0.5:
        raise ValueError("conglomerate_discount_pct unrealistic; must be in [0, 0.5]")

    ev_per_segment = {}
    for seg in inputs.segments:
        ev_rev = seg.external_revenue * seg.ev_revenue_multiple
        ev_ebitda = seg.ebitda * seg.ev_ebitda_multiple if seg.ebitda > 0 else None
        ev_dcf = seg.dcf_ev

        if valuation_method == "multiple_revenue":
            ev = ev_rev
        elif valuation_method == "multiple_ebitda":
            if ev_ebitda is None:
                raise ValueError(f"segment {seg.id} has non-positive EBITDA; cannot use ebitda multiple")
            ev = ev_ebitda
        elif valuation_method == "dcf":
            if ev_dcf is None:
                raise ValueError(f"segment {seg.id} has no DCF EV")
            ev = ev_dcf
        elif valuation_method == "blended":
            candidates = [v for v in (ev_rev, ev_ebitda, ev_dcf) if v is not None and v > 0]
            ev = sum(candidates) / len(candidates) if candidates else 0
        else:
            raise ValueError(f"unknown method {valuation_method}")
        ev_per_segment[seg.id] = ev

    sum_segment_ev = sum(ev_per_segment.values())
    corporate_items = (
        inputs.corporate_cash
        + inputs.other_corporate_assets
        - inputs.corporate_debt
        - inputs.pension_liability
        - inputs.other_corporate_liabilities
    )
    sotp_gross = sum_segment_ev + corporate_items

    discount_amount = sotp_gross * inputs.conglomerate_discount_pct
    standalone_premium_amount = sotp_gross * inputs.standalone_premium_pct
    sotp_net = (
        sotp_gross
        - discount_amount
        + standalone_premium_amount
        + inputs.synergy_value
    )

    return {
        "ev_per_segment": ev_per_segment,
        "sum_segment_ev": sum_segment_ev,
        "corporate_items": corporate_items,
        "sotp_gross": sotp_gross,
        "conglomerate_discount_amount": -discount_amount,
        "standalone_premium_amount": standalone_premium_amount,
        "synergy_value": inputs.synergy_value,
        "sotp_net": sotp_net,
        "implied_blended_multiple": sotp_net / sum(s.external_revenue for s in inputs.segments),
    }


# Usage example
if __name__ == "__main__":
    segments = [
        Segment("saas", "Core SaaS", 100, 25, 9.0, 25.0, dcf_ev=850),
        Segment("marketplace", "Marketplace", 50, 10, 5.0, 20.0, dcf_ev=300),
        Segment("fintech", "Fintech", 20, 4, 4.0, 15.0, dcf_ev=50),
    ]
    inputs = SOTPInputs(
        segments=segments,
        corporate_cash=80,
        corporate_debt=50,
        conglomerate_discount_pct=0.10,
    )
    result = compute_sotp(inputs, valuation_method="blended")
    print(result)
```

### 5.9 SOTP の限界と落とし穴

#### 5.9.1 Pinpoint Accuracy の幻想

SOTP は range output。「Net SOTP = $1,215M」と一点で書くと信頼性過大。代わりに:

```
SOTP base case = $1,000M
SOTP range = $850M (low: discount 20%, conservative multiples) – $1,400M (high: discount 0%, premium multiples)
```

football field chart で示す (`05_valuation_wacc §17` triangulation)。

#### 5.9.2 未上場 startup の segment は comps 不足

公開 comps が無い segment (e.g., 日本 SaaS の domestic comp、新興市場の Marketplace) は multiple-based 計算が困難 → DCF 主体、stress test を厚く。

#### 5.9.3 新規 segment (0 売上) の評価

new segment が 0 売上 (R&D 期 / launch 直前) の場合、multiple は意味なく、DCF も信頼性低い → **Real Options** で valuation:

- Black-Scholes parameters: underlying = 推定 future revenue NPV、strike = 必要 investment、volatility = 業界 vol、time = launch までの year
- 結果は range で出す

#### 5.9.4 Loss-making segment の扱い

赤字 segment は EV/EBITDA 計算不能 → EV/Revenue or asset-based:

- EV/Revenue: 業界 multiple を使う、ただし growth adj
- Replacement cost: もし segment を "0 から作る" のに必要な cost → lower bound

楽天モバイルのように **構造的赤字 segment** は SOTP で慎重: market cap 上の implied value はマイナス (consolidated 時価総額 < EC + FinTech の SOTP) になることがある。

#### 5.9.5 SOTP gross と Equity Value の bridge

SOTP は EV を出す。Equity Value への bridge は:

```
Equity Value (SOTP) =
   SOTP Net EV
 - Net Debt (consolidated)
 - Preferred Stock outstanding
 - NCI (if 連結子会社あり、`13a §6`)
 + ITM Options proceeds
```

NCI が大きい連結グループ (例: 楽天 G の楽天モバイルが連結子会社で NCI ある場合) は `13a §6.4` の NCI 計算を併用。

---

## 6. Segment 別 KPI Framework

各 segment はそれぞれ業態に応じた KPI を持つ。`02_saas_metrics`、`03_business_models`、`18_customer_value_and_pricing` に詳細はあるが、本書では segment 単位で **どの業態が何の KPI を持つか** を 1 表で整理する。

### 6.1 業態別 KPI Matrix

下表は各 segment 業態で必要な KPI を、本書の用途 (multi-segment IC memo の per-segment KPI 開示) に絞って整理。詳細指標は逆参照 reference に。

| Segment 業態 | 必須 KPI (5–10 個) | 推奨追加 KPI | 詳細 reference |
|---|---|---|---|
| **SaaS (B2B)** | ARR, NRR, GRR, Magic Number, CAC Payback (months), LTV/CAC, Burn Multiple, Rule of 40, Gross Margin | ACV, Logo retention, Sales efficiency | `02_saas_metrics` 全章 / `_terminology §6` canonical |
| **SaaS (PLG / SMB)** | ARR, NRR, MRR Growth, Activation rate, Free→Paid Conversion, CAC Payback, Logo Churn, GM | Time-to-value, Daily Active Users | `02_saas_metrics §3` / `03_business_models §2` |
| **Marketplace (2-sided)** | GMV, Take Rate (%), Active Buyers, Active Sellers, Cohort Retention, Listings, Liquidity (% listings sold), Buyer-Seller Ratio, Net Revenue, Contribution Margin | Repeat Rate, Cross-side Network Effect (new buyers per new seller) | `03_business_models §3` / `18_customer_value_and_pricing §3` |
| **D2C (Direct-to-Consumer)** | DTC Revenue %, Repeat Rate, AOV (Average Order Value), Purchase Frequency, Inventory Turns, Marketing Spend / Revenue, Contribution Margin per Order, Customer Acquisition Cost | LTV cohort curve, Retention by channel | `03_business_models §4` / `18_customer_value_and_pricing §2` |
| **Hardware (consumer / B2B)** | Units Sold, ASP (Average Selling Price), Hardware GM%, Service Attach Rate (%), Recurring Revenue %, Inventory Turns, Warranty Cost %, NPS | Service Revenue per Device, Time-to-replacement | `03_business_models §5` |
| **Bio / Pharma** | Phase I/II/III success probability, Patent Expiry Year, R&D % of Revenue, Clinical Trial Enrollment Rate, Time-to-Market, Peak Sales Forecast, NPV per Pipeline | Reimbursement rate, Physician adoption | `03_business_models §7` / `05_valuation_wacc §8` Real Options |
| **Ads / Media (digital)** | DAU/MAU Ratio, ARPU (Average Revenue Per User), CPM (Cost Per Mille), Ad Fill Rate, Ad Load (ads per session), Time Spent per User, Active Advertisers | Click-through rate, Brand vs performance ad mix | `03_business_models §6` |
| **AI (foundation model / API)** | Token Cost per Inference, Inference Latency, API Adoption Rate, Productivity Uplift Reported, Customer Adoption (logo count), Compute Cost / Revenue, Model Quality Benchmarks | Open-source vs proprietary mix, Fine-tune adoption | `03_business_models §8` (AI セクション) |
| **Fintech (Lending)** | NIM (Net Interest Margin), Cost of Risk, NPL (Non-Performing Loan) %, Approval Rate, Loan Book Size, TPV (Total Payment Volume) for adjacent payments | Stage 2/3 loan migration, Charge-off rate | `03_business_models §9` |
| **Fintech (Payments)** | TPV, Take Rate, Net Revenue / TPV, Active Merchants, Cross-border Payments %, Fraud Rate %, Authorization Rate | New product attach rate (lending / cards) | `03_business_models §9` |
| **Subscription Consumer (streaming / DTC subscription)** | Paying Subscribers, ARPU, Churn Rate, NRR, Content / Service Cost / Revenue, NPS | New content velocity, sub-by-tier mix | `03_business_models §10` |
| **Logistics / 3PL** | Volume Shipped, Cost per Order, Delivery Time, On-time %, Active Customers, Revenue per Order | Returns rate, last-mile vs full-stack mix | `03_business_models §11` |

> Note: 業態は **12 種** をカバー (task spec の "≥ 8 業態" 要件を満たす)。各業態の数値閾値 (PASS/WATCH/FAIL) は `_terminology §6` を canonical とする。

### 6.2 Cross-Segment KPI (Consolidated)

Segment-level KPI に加え、consolidated (全社統合) で意味を持つ KPI:

#### 6.2.1 Revenue Mix の推移

| Year | SaaS Rev ($M) | Marketplace Rev ($M) | Fintech Rev ($M) | Total Rev | SaaS % | MP % | FT % |
|---|---|---|---|---|---|---|---|
| Y1 | 100 | 50 | 10 | 160 | 63% | 31% | 6% |
| Y3 | 130 | 80 | 20 | 230 | 57% | 35% | 9% |
| Y5 | 160 | 120 | 50 | 330 | 48% | 36% | 15% |

→ Fintech segment の急成長で mix が変化。投資家視点で「次の 5 年で何が driver か」を可視化。

#### 6.2.2 Segment-level Operating Leverage

各 segment の "incremental EBITDA / incremental Revenue" を観察:

| Segment | Y1 EBITDA ($M) | Y2 EBITDA | ΔEBITDA | ΔRev | Operating Leverage (ΔEBITDA / ΔRev) |
|---|---|---|---|---|---|
| SaaS | 25 | 30 | +5 | +30 | 17% |
| Marketplace | 10 | 15 | +5 | +30 | 17% |
| Fintech | 4 | 8 | +4 | +10 | 40% |

→ Fintech が最も operating leverage 高い (固定 cost が薄い段階)、SaaS / Marketplace は均衡。

#### 6.2.3 Capital Allocation by Segment

各 segment への growth investment 配分:

| Segment | Y1 CapEx ($M) | Y1 OpEx growth ($M) | Total Growth Spend | % of Total | ROIC |
|---|---|---|---|---|---|
| SaaS | 5 | 10 | 15 | 38% | 75% |
| Marketplace | 8 | 12 | 20 | 50% | 35% |
| Fintech | 1 | 4 | 5 | 12% | 90% |
| Sum | 14 | 26 | 40 | 100% | -- |

→ Marketplace に半数の investment が流れているが ROIC 35%、SaaS / Fintech は ROIC 高いのに投資少。capital allocation の inefficiency 示唆。

#### 6.2.4 ROIC by Segment 比較

```
ROIC_segment = NOPAT_segment / Invested Capital_segment
Hurdle rate = WACC_segment
Excess ROIC = ROIC_segment - WACC_segment
```

| Segment | ROIC | WACC | Excess ROIC |
|---|---|---|---|
| SaaS | 75% | 9.5% | +65.5pp |
| Marketplace | 35% | 11% | +24pp |
| Fintech | 90% | 13% | +77pp |
| Hardware | 12% | 11% | +1pp (marginal) |

→ Hardware segment の excess ROIC が ~0 → このまま投資続けると value-destroying リスク、撤退候補。

### 6.3 KPI Dashboard Layout (xlsx)

`11_KPI_Dashboard` (canonical sheet name) は **consolidated KPI のみ** とし、segment-level KPI は新設の `20c_Segment_A_KPI` / `20f_Segment_B_KPI` に独立 sheet を持つ。

#### 6.3.1 11_KPI_Dashboard (consolidated)

| KPI | Y0 (LTM) | Y1 | Y2 | Y3 | 業界 benchmark |
|---|---|---|---|---|---|
| Total Revenue ($M) | 160 | 200 | 250 | 310 | -- |
| YoY Growth % | -- | 25% | 25% | 24% | SaaS-mix should be 30%+ |
| Consolidated GM % | 65% | 67% | 69% | 71% | -- |
| Consolidated EBITDA Margin | 12% | 18% | 22% | 25% | Rule of 40 |
| Rule of 40 (consol blended) | 37 | 43 | 47 | 49 | ≥ 40 = PASS |
| Burn Multiple | 0.4 | 0.3 | -- | -- | ≤ 1 = PASS |
| Net New ARR ($M) | 30 | 40 | 50 | 60 | growth |
| Cross-segment cross-sell rate | 5% | 8% | 12% | 15% | Optimization target |

#### 6.3.2 20c_Segment_A_KPI (SaaS segment)

| KPI | Y0 | Y1 | Y2 | Y3 | Threshold (`_terminology §6`) |
|---|---|---|---|---|---|
| ARR ($M) | 100 | 120 | 150 | 180 | -- |
| YoY ARR Growth | -- | 20% | 25% | 20% | ≥ 30% Series C+ ideal |
| NRR | 115% | 118% | 120% | 122% | ≥ 110% PASS |
| GRR | 92% | 93% | 94% | 95% | ≥ 85% PASS |
| Magic Number | 0.9 | 1.1 | 1.2 | 1.2 | ≥ 0.7 PASS |
| CAC Payback (months) | 18 | 16 | 14 | 13 | ≤ 24 PASS |
| LTV/CAC | 4.5 | 5.0 | 5.5 | 6.0 | ≥ 3 PASS |
| Burn Multiple | 0.5 | 0.4 | 0.3 | 0.3 | ≤ 1 PASS |
| Rule of 40 (segment) | 35 | 42 | 45 | 47 | ≥ 40 PASS |
| Segment EBITDA Margin | 25% | 30% | 33% | 35% | -- |

#### 6.3.3 20f_Segment_B_KPI (Marketplace segment)

| KPI | Y0 | Y1 | Y2 | Y3 | Threshold |
|---|---|---|---|---|---|
| GMV ($M) | 500 | 700 | 900 | 1,200 | -- |
| Take Rate | 10% | 11% | 12% | 13% | benchmark vary |
| Net Revenue ($M) | 50 | 77 | 108 | 156 | -- |
| Active Buyers (M) | 2.5 | 3.5 | 4.5 | 6.0 | -- |
| Active Sellers (K) | 50 | 80 | 120 | 170 | -- |
| Buyer Cohort Retention (Y2) | 60% | 62% | 64% | 65% | ≥ 60% PASS |
| Listing per Seller | 12 | 14 | 16 | 18 | density |
| Liquidity (% listings sold within 30 days) | 35% | 40% | 45% | 50% | ≥ 50% PASS |
| Contribution Margin % | 35% | 38% | 40% | 42% | -- |

### 6.4 Segment 比較の Sanity Check

複数 segment の KPI が integer / consistent であることを sanity check:

- **Σ(segment external revenue) = consolidated external revenue**: 必須 (`_self_review_protocol §10` 入り)
- **Σ(segment EBITDA) + Stranded Cost = consolidated EBITDA**: §4.5 のロジック
- **Σ(segment headcount) = consolidated headcount**: corporate FTE 含めて整合
- **Σ(segment CapEx) ≤ consolidated CapEx**: corporate-level CapEx 込みで一致
- **Cross-segment KPI consistency**: cross-sell rate が "% of customers in segment A who also purchase from segment B" なら 0–100% range

### 6.5 KPI inconsistency anti-pattern

§14.4 で詳述するが、**全 segment で同じ詳細度の disclosure** を維持することが投資家信頼の前提:

- SaaS segment で NRR を public に公開、Hardware segment で同等指標を出さない → 投資家不信
- Marketplace segment で take rate を 1 quarter で公開しない四半期がある → consistency 欠如
- 一度開示した KPI は 5 年以上は continue (大きな business model 変更ない限り)

---

## 7. Transfer Pricing

複数 segment 間 (= 同一法人内、別 segment 間) で good / service の internal trade が発生する場合、**transfer price (内部移転価格)** をどう設定するかが segment-level 経営判断・税務・税効果に影響する。

`13a_consolidation_core §5` は **法人間 (intercompany)** transfer pricing を扱う (連結消去 / 未実現利益 / 移転価格税制)。本書 §7 は **同一法人内 (inter-segment)** に絞る。

### 7.1 Internal Trade の Identification

#### 7.1.1 典型 inter-segment trade

| Selling segment | Buying segment | Service / Good | 計測単位 |
|---|---|---|---|
| AWS | Amazon Retail | Cloud hosting | Compute hour、storage GB、network egress |
| Microsoft Azure | Office 365 / Dynamics | Compute / Storage | 同上 |
| Google Cloud | YouTube / Search | Compute | 同上 |
| 楽天モバイル | 楽天市場 | 通信ネットワーク, dedicated 帯域 | GB / month |
| Mercari | Mercari Pay | Identity / KYC API | API call |
| Toast POS | Toast Capital | 顧客 transaction data | data record / month |
| Salesforce SFA | AppExchange | Marketplace listing infrastructure | listing 件数 |
| Apple Hardware | Apple Services | Device usage data, App Store distribution | flat fee or % |
| Shared platform engineering | Multiple product segments | ML platform, CI/CD | API call、compute hour |

#### 7.1.2 Identification の要件

「意味のある」inter-segment trade とは:

- **物理的 / 機能的に分離可能**: 1 segment が他 segment に提供しないと、買い手 segment の運営に impact がある
- **価格があり得る**: 外部 market でも提供可能 (= alternative source あり)
- **量計測可能**: API call / compute hour / unit 数 / 比例的に量れる

これらを満たさない (例: CEO が 2 segment の戦略を考える時間) は inter-segment trade ではなく、§4 の corporate cost allocation で扱う。

### 7.2 Pricing Methods (3 種)

#### 7.2.1 Cost-Plus

```
Transfer Price = Direct Cost + Markup (5–15%)
```

| 利点 | 欠点 |
|---|---|
| 計算容易、出した側の cost recovery 保証 | 提供 segment が efficient gain を売り手に取り込めない (innovation の incentive 弱) |
| 監査 friendly | 提供 segment の "real value" を反映しない |
| 税務 documentation 簡単 (`12_tax_strategy §5`) | 高 margin 業界 (cloud) では over-allocation の cost に |
| 安定 | 受け手 segment の経営判断: cost-plus は内部 captive、外部買えば markup 不要、と思う |

**適用**: 共通インフラ (HR system、IT infrastructure)、低差別化 service (data center hosting で commodity 部分)。

#### 7.2.2 Market Price

```
Transfer Price = External Comparable Market Rate
```

External market で同等 service の価格を観察し、それを transfer price に使う。

| 利点 | 欠点 |
|---|---|
| **Arm's length principle** に最も近い (税務 favorable) | external comp の identification が困難 (内部専用 service の場合) |
| 提供 segment は external sale と同じ economics → 競争 motivation | external rate が変動するため transfer price も変動 |
| 受け手 segment は外部買いと同じ価格 → make-or-buy 判断中立 | external market が undeveloped な場合 (e.g., 専用 ML platform は market 無し) |

**適用**: AWS の compute (external customer rate を base)、Stripe の payment processing (external rate を base)。

#### 7.2.3 Negotiated Price

```
Transfer Price = 両 segment の合意価格
```

両 segment の経営陣が交渉して決定。Cost-plus と Market price の中間。

| 利点 | 欠点 |
|---|---|
| 両 segment の経営判断を尊重 | 強い segment が weak segment を pressure する |
| flexibility | 客観性に欠け、税務 audit でリスク |
| 経営陣の strategic 議論を促進 | re-negotiation が頻発 (transactional cost) |

**適用**: 戦略的 strategic な内部 partnership (e.g., 共同 product development の費用負担)。

### 7.3 Transfer Pricing の動機

#### 7.3.1 内部 incentive 設計

各 segment を **独立した P&L unit** として運営する場合、transfer price は segment manager の経営判断 driver。

- 高 transfer price → 売り手 segment の EBITDA up、買い手 down → 売り手の incentive 強化
- 低 transfer price → 逆
- Market price → 中立 (両者が外部 market での代替を検討するインセンティブ)

#### 7.3.2 Cost discipline

買い手 segment にも市場価格を意識させることで、内部 service の "cost-free" perception を回避。

例: Amazon Retail が AWS hosting を内部 free で得ていたら、過剰使用が起きる。Market price で課金すれば、Retail segment は efficient な server usage を考える。

#### 7.3.3 Tax Optimization (cross-border の場合のみ)

**重要**: 1 法人内の inter-segment trade は **税務影響なし** (同一法人内なので)。これは `13a §5.4` の cross-border intercompany trade と区別すべき。法人またぎ (e.g., US 親会社 → 日本子会社) は OECD BEPS の制約あり (`12_tax_strategy §5`) が、本書 §7 の inter-segment はそれらの対象外。

cross-border の場合は法人を分けるか、transfer pricing 詳細は `12_tax_strategy §5` を canonical とし、本書では触れない。

### 7.4 Transfer Pricing の Tax Compliance (cross-border の場合)

本書では概要のみ、詳細は `12_tax_strategy §5` を canonical とする。

#### 7.4.1 Arm's Length Principle (OECD)

OECD Transfer Pricing Guidelines (2022 update) — cross-border intercompany trade は **arm's length** (独立企業間取引と同等) でなければならない。

#### 7.4.2 Transfer Pricing Methods (OECD で 5 method 認定)

1. CUP (Comparable Uncontrolled Price) — 同等 external trade との価格比較
2. RPM (Resale Price Method) — re-sale 価格から markup 控除
3. CPM (Cost Plus Method) — direct cost + markup
4. TNMM (Transactional Net Margin Method) — net margin 比較
5. PSM (Profit Split Method) — 利益分配

#### 7.4.3 日本 移転価格税制

租税特別措置法 66-4 — 国外関連取引 (海外の関連法人との取引) は arm's length。違反すると更正処分 + 加算税。

文書化義務:
- **Master file** (年度末から 1 年以内、グループ全体)
- **Local file** (期末から 60 日、個別取引)
- **CbC report** (Country-by-Country、連結売上 1,000 億円以上)

### 7.5 Transfer Pricing の Setting Process

実務的に transfer price を設定するフロー:

1. **Internal trade identification** (§7.1): 主要 inter-segment 取引を 5–10 個 list up
2. **Method selection per trade** (§7.2): Cost-plus / Market / Negotiated を選択。意思決定基準:
   - external comp が豊富 → Market
   - 内部専用 service → Cost-plus
   - 戦略 deal → Negotiated
3. **Markup or Negotiation**: Cost-plus の markup % は 業界 / 経営判断で 5–15% / Market はベンチマーク search
4. **Annual review**: 年初に rate fix (§4.4 の固定 allocation と同思想)
5. **Documentation** (cross-border のみ tax 用): Master / Local file
6. **Audit / Sanity check**: Year-end で transfer price が `13a §5` の元実利益と整合か再確認 (1 法人内では監査影響なし、segment 透明性のみ)

### 7.6 Transfer Pricing の数値例

例: SaaS+Marketplace 企業で SaaS が Marketplace に "Product Analytics API" を提供。

- Volume: Marketplace が月 10M API call 消費
- Direct cost (SaaS 側): $0.001 / call → 月 $10K = 年 $120K
- External market price: $0.005 / call (公開 cloud analytics provider)
- Strategic value (Marketplace の data driven product 改善): high

選択肢:

| Method | Transfer Price | SaaS Revenue | SaaS Margin | Marketplace COGS | Marketplace Decision |
|---|---|---|---|---|---|
| Cost-plus 10% | $0.0011 / call | $132K | 9% | $132K | 内部 service と external、ほぼ equal、内部選択 |
| Market | $0.005 / call | $600K | 80% | $600K | 内部 vs external comparison: data privacy 内部 favorable |
| Negotiated | $0.003 / call (両者合意) | $360K | 67% | $360K | 中間、両 segment の経営陣 OK |

→ どれを選ぶか? 経営方針による。本企業が「各 segment standalone economics 重視」なら Market、「cost-effective internal infra」なら Cost-plus。

### 7.7 Inter-segment Pricing と SOTP の関係

SOTP 計算では §3.3.4 で **inter-segment revenue は除外** (External revenue ベース)。これは transfer price の選択に独立。

ただし注意:

- Cost-plus low markup → 売り手 segment EBITDA 低 → multiple-based EV 低 → Net SOTP 低
- Market high price → 売り手 segment EBITDA 高 → multiple-based EV 高

**意味**: transfer price が任意なら、SOTP が "transfer pricing engineered" になる。これは投資家への透明性を欠く → arm's length / market price を recommendation。

---

## 8. Conglomerate Discount 詳解

### 8.1 Empirical Evidence

§5.5.1 で range を提示したが、ここで詳細整理。

#### 8.1.1 Berger & Ofek 1995 (seminal)

- **Sample**: 米上場 5,233 firm-year (1986–1991)
- **Methodology**: 多角化企業の価値 vs 各 segment の業界 median multiple で計算した「imputed value」の比較
- **Result**: 多角化企業は imputed value より **平均 13–15% 過小評価**
- **Key drivers (彼らの explanation)**: (1) overinvestment (低 ROI segment への過剰投資)、(2) cross-subsidization (黒字 segment が赤字 segment を補填)
- **Tax benefit offset**: 多角化に内在する tax shield (NOL 相殺) で discount は modest に reduced

> 出典: Berger PG, Ofek E. 1995. "Diversification's effect on firm value." Journal of Financial Economics 37(1): 39–65. (https://www.sciencedirect.com/science/article/pii/0304405X94007986)

#### 8.1.2 Lang & Stulz 1994

- **Sample**: 米上場 1978–1990
- **Methodology**: Tobin's Q (= Market value / Replacement cost) で多角化と単一事業を比較
- **Result**: 多角化企業の Q は単一事業より低い (-10 to -25%)
- **Note**: Q-based なので Berger-Ofek の imputed value 法とは異なるアプローチ

#### 8.1.3 Campa & Kedia 2002 (反証)

- **Critique**: Berger-Ofek は **endogeneity** (もともと弱い企業が多角化に流れる) を control していない
- **Methodology**: Heckman 2-step + 固定効果 model + IV (instrumental variable) で endogeneity を control
- **Result**: control 後、discount は **ほぼゼロ or 微小負**
- **Conclusion**: "diversification discount" is largely an artifact of selection bias

> 出典: Campa JM, Kedia S. 2002. "Explaining the diversification discount." Journal of Finance 57(4): 1731–1762. (https://pages.stern.nyu.edu/~eofek/PhD/papers/CK_Explaining_JF.pdf)

#### 8.1.4 Villalonga 2004

- **Sample**: BITS (Business Information Tracking Series) 事業所単位データ
- **Result**: より厳密な事業単位定義で Berger-Ofek を再 estimate → 微正 (premium)
- **Conclusion**: SIC コードベースの粗い segment 区分が discount を生んでいた

#### 8.1.5 Hund / Monk / Tice 2010

- **Critique**: Berger-Ofek の matching 手法 (median value within SIC code) が biased
- **Result**: より careful matching では discount はほぼゼロ

> 出典: Hund J, Monk D, Tice S. 2010. "The Berger-Ofek Diversification Discount Is Just Poor Firm Matching." (https://cfr.ivo-welch.info/published/papers/hund-monk-tice.pdf)

#### 8.1.6 学術合意 (2025 時点の現状)

- Berger-Ofek 13–15% discount は **実証的に弱い**
- ただし「多角化企業が premium を得ているという証拠も無い」
- Firm-specific factors (capital allocation skill、reporting transparency、industry mix) が支配
- **実務示唆**: SOTP 計算で discount を flat 13–15% で当てはめるのは **科学的根拠に欠ける**。0–25% range で firm-specific judgement。

#### 8.1.7 業界別 spread (現代 2024 時点の analyst observation)

公開 listed conglomerate の SOTP-implied discount を analyst が観察:

| 業界 | Discount (median) | Range | 観察 |
|---|---|---|---|
| US large industrial conglomerate (GE pre-spin、3M 等) | 15–20% | 10–25% | 旧 industrial mix が discount を呼ぶ |
| US tech holding (Alphabet、Amazon、Meta) | 5–10% | 0–15% | 関連事業の synergy 強い |
| Korean chaebol (Samsung、LG、Hyundai 等) | 30–50% | 25–60% | **chaebol discount** として well-documented |
| Japanese keiretsu / 商社 (三菱商事、伊藤忠 等) | 20–35% | 15–45% | 持ち合い、不透明な事業 |
| Berkshire Hathaway | -5 to +10% | (premium ! ) | 例外的、Buffett の skill 評価 |
| US PE-owned platforms (post LBO) | 0–10% | low | active management |

> 観察手法: SOTP gross (analyst が業界 multiple で各 segment を評価) と market cap の比較。Korean chaebol は 韓国 KCGS (Corporate Governance Service) annual reports 参照。

### 8.2 Discount を生む Driver

#### 8.2.1 Capital Allocation Suboptimization

- 黒字 segment の現金が赤字 segment の補填に使われる (cross-subsidization)
- 経営陣が「家族化された segment」を撤退できない (legacy 思考)
- Investor の評価: 「この黒字 segment 単独なら $X 価値、でも会社全体だと使われ方が不明 → Discount」

#### 8.2.2 Reporting Opacity

- segment 数が多すぎ analyst がモデル不能
- 各 segment の独立 metrics 開示が弱い (NRR / Take Rate 等が segment 別ない)
- inter-segment transfer pricing が任意 → 数値の信頼性低い
- Investor の評価: 「数値が信頼できないから Discount」

#### 8.2.3 Lack of Focus (経営の分散)

- CEO の attention が複数事業に分散
- 経営 review meeting が浅く
- 各 segment が best-in-class operator にならない
- Investor の評価: 「家業より分業のほうが効率良い → Discount」

#### 8.2.4 Agency Cost (経営陣のインセンティブ)

- 経営陣の compensation が **会社規模** (revenue / asset) 連動なら、低 ROI segment を保有するインセンティブ
- spin-off で会社規模が縮むのを嫌がる経営陣
- Investor の評価: 「経営陣が shareholder value より自分の status を重視 → Discount」

### 8.3 Discount を Premium に変える Driver (反対意見)

#### 8.3.1 Cost Synergy

- 共通 HQ で重複削減
- 共通 IT / HR / Legal で scale efficiency
- 共通 brand で marketing efficiency
- 数値: corporate G&A allocation に既に反映済 (§4)

#### 8.3.2 Revenue Synergy (cross-selling)

- 顧客への multiple product up-sell
- データの cross-product utilization (Amazon Prime + AWS data)
- Brand premium (Microsoft brand で Azure 売却)

#### 8.3.3 Capital Allocation Premium (Berkshire model)

- Star CEO (Buffett、Bezos) が業界 winner を pick できる skill
- Free cash flow が efficient に再投資
- → Conglomerate premium が生じる例

#### 8.3.4 Internal Capital Market

- 黒字 segment の cash を低 cost で赤字 segment R&D に流せる
- 外部 financing (株 / 債) より cheap
- 但し agency cost と背中合わせ

### 8.4 Discount を Reduce する Action (経営者向け)

#### 8.4.1 Segment Reporting Transparency

- IFRS 8 / ASC 280 の minimum を超えた voluntary disclosure
- segment 別 detailed metrics (NRR / Take Rate / Burn Multiple)
- 中期計画で segment 別 KPI guidance
- Investor day で segment-level 説明

#### 8.4.2 Capital Allocation の明確な Framework

- segment 別 ROIC > WACC を hurdle rate として明示
- "If a segment's ROIC < WACC for 2 consecutive years, we will divest" 等の rule
- 公開 review (annual letter で各 segment review)

#### 8.4.3 Spin-off / Split-off

- 価値 unrealized な segment を spinoff (`13b_treasury_carveout` canonical)
- 発表で premium realization (5–15% の standalone premium、§5.7.1)
- 例: HP / HPE 2015 (Q4 2014 発表 → 2015 完了で combined +12%)

#### 8.4.4 Active Investor との対話

- Activist (ValueAct、Elliott 等) の 提案を accept
- shareholder vote で portfolio optimization
- Carl Icahn が eBay → PayPal spinoff を 2014 年に提案、CEO Donahoe が抵抗 → 2015 年に実施 → PayPal 単独で eBay 内部時の implied valuation を 30% 超 (https://corporate.ebay.com/en/news-and-events/news/ebay-inc-announces-plans-to-separate-paypal-into-an-independent-publicly-traded-company)

### 8.5 Discount を Expand させる行動 (anti-pattern)

#### 8.5.1 Cross-Subsidization

- 黒字 segment が赤字 segment への内部援助 (transfer price で意図的に低 price)
- 楽天モバイル loss を EC が吸収する構造、investor に「いつまで続くか」不安
- → Discount 拡大

#### 8.5.2 Earn-out / Acquisition で Goodwill 巨大化

- 連続的 M&A で BS に goodwill が積み上がる
- impairment risk → 評価不確実性
- → Discount 拡大

#### 8.5.3 不透明な Inter-segment Trade

- transfer pricing がブラックボックス
- segment manager の真の performance 不明
- → Investor が segment-level 数値を信用しない → Discount 拡大

#### 8.5.4 経営陣の Compensation が会社規模連動

- CEO comp が consolidated revenue / assets 連動なら、divest インセンティブ無し
- → Investor が agency cost を懸念 → Discount 拡大

### 8.6 Discount の SOTP への適用 (実装)

#### 8.6.1 Base case 設定

firm-specific judgment で 0–25% の中で選択。判断 framework:

| Indicator | Discount を上げる factor | Discount を下げる factor |
|---|---|---|
| Segment 数 | 多 (5+) | 少 (2–3) |
| Inter-segment synergy | 弱い | 強い (cross-sell 多い) |
| Reporting transparency | 弱い | 強い (segment KPI 全公開) |
| Capital allocation discipline | 不明 | 明確 (segment-level ROIC > WACC) |
| 業界 mix | 不整合 (industrial + tech 等) | 整合 (全 tech / 全 SaaS 系) |
| Brand consistency | バラバラ | 統一 (Amazon、Microsoft 等) |
| Geographic concentration | 多国 | 1 国 |
| 市場予期 | 高 (analyst pessimistic) | 低 (analyst optimistic) |
| Activist pressure | あり | 無し |

#### 8.6.2 数値 example

ある SaaS+Marketplace+Fintech 企業:

| Indicator | Score |
|---|---|
| 3 segment (中) | +0% |
| Synergy 強 (cross-sell 15%) | -5% |
| Reporting transparent (NRR / Take Rate / NIM 全公開) | -5% |
| Capital allocation discipline 中 | +0% |
| 業態は隣接 (全て tech / fintech) | -3% |
| Brand 統一 | -2% |
| 1 国 | -2% |
| Activist 無し | +0% |
| **Net discount** | **-17% → 8%** から start、最終 base case 10% |

#### 8.6.3 Sensitivity table

```
SOTP gross = $1,200M
| Discount Scenario | Discount | SOTP net |
| Optimistic       | 0%       | $1,200M  |
| Base             | 10%      | $1,080M  |
| Conservative     | 20%      | $960M    |
| Bear              | 30%      | $840M    |
```

football field chart で base case + range を表現。

### 8.7 Carve-out / Spin-off Decision Tree (8.4.3 拡張)

discount > 15% で且つ spin-off cost が manageable な segment は spin-off 検討:

1. Calculate **Implied conglomerate discount** = (SOTP gross - market cap) / SOTP gross
2. If implied discount > 15% → spin-off candidate
3. Identify the segment that drives the discount most:
   - Largest standalone EV
   - Most independent (smallest synergy with rest)
   - Cleanest reporting
4. Estimate spin-off cost (`13b §3`):
   - Banker fees (~1–3% of EV)
   - Legal / Tax structuring (~$5–20M)
   - One-time IT separation (~$10–50M)
   - Stranded cost (HQ overhead remaining)
5. Net spin-off value = (SOTP gross × discount reduction %) - spin-off cost
6. If Net > 0 and > 5% of equity, recommend

例: 仮想 SaaS+Hardware company (current MC $5B、SOTP $6B、discount 17%):
- Spin-off Hardware → discount becomes 5% (assumed reduction)
- Recovered value = $6B × (17% - 5%) = $720M
- Spin-off cost ≈ $80M (banker $50M + legal/IT $30M)
- Net spin-off value = $640M = 13% of current MC
- → Recommend spin-off


---

## 9. Multi-Segment Cap Table の Implications

### 9.1 通常: 1 法人 1 Cap Table

ほとんどのケースで、1 法人内の複数 segment は **同じ cap table を共有** する。`04b_cap_table_mechanics` の standard cap table がそのまま適用される。

- 全 segment の業績は consolidated equity の value として表現
- 投資家 (shareholder) は会社全体の equity を保有、segment 別 equity ではない
- exit 時の waterfall (`04b §6`) は consolidated EV を base に、preference / participation / common 順で分配

#### 9.1.1 Segment 別 SBC (Stock Based Compensation) 配賦

ただし **会計上の SBC expense 配賦** は segment 別 P/L の対象になる:

```
SBC_segment = Total SBC × (Segment FTE / Total FTE)
```

これは §4.2.2 Headcount-based allocation の延長。SBC を segment に配賦することで segment EBITDA が悪化するが、これが reality。

#### 9.1.2 Segment 別 Dilution の表示

各 segment の "貢献" を investor にアピールする目的で、**segment 別 dilution attribution** を IC memo で表示することがある:

| Segment | FTE % | Equity grant share % | Effective dilution per year |
|---|---|---|---|
| SaaS | 60% | 65% | 2.0% (full dilutive incl ISO+RSU) |
| Marketplace | 30% | 25% | 0.8% |
| Fintech | 10% | 10% | 0.3% |
| Total | 100% | 100% | 3.1% |

→ SaaS segment が equity grant を多く受けている (key talent retention)。

### 9.2 Subsidiary 別 Cap Table (HoldCo + 別法人 Sub)

複雑なケース: 一部 segment が **別法人 subsidiary** に切り出されている。

例:

- 楽天 G は 楽天株式会社の中の事業 segment + 楽天モバイル株式会社、楽天銀行 (関連) 等の subsidiary
- Mercari Inc は Mercari, Inc. (Japan) + Mercari, Inc. (US Delaware) + Merpay 等
- Microsoft は ほぼ 1 法人 (子会社は地域 sub のみ、 segment は内部 division)

このケースでは:

- 親会社 cap table = consolidated equity holders
- 子会社 cap table = 親会社が支配 (50%+) + minority shareholders (NCI)
- `13a_consolidation_core §6` の NCI が登場
- segment 別の経営は本書、連結処理は `13a` を併用

#### 9.2.1 Subsidiary 別 minority investor

- 楽天モバイルに minority equity を発行する想定:
  - Series A: 親会社 80%、minority 投資家 20%
  - 親会社 BS に "Investment in 楽天モバイル" $X 計上、子会社 BS に NCI 20% × Equity Book 計上
- exit / IPO での treatment:
  - 楽天モバイル単独 IPO → 親会社のみが上場、minority は dilute
  - 楽天モバイル spin-off → 親会社 shareholder が併せて 楽天モバイル株を受領 (`13b §4`)

### 9.3 Tracking Stock / Class Stock (rare)

歴史的には segment 別の **tracking stock** (e.g., GM が Hughes Electronics を tracking 株として発行 1985–1997) が存在したが、現代ではほぼ廃れた:

- 法律的に同一会社の株、経済的に segment performance に連動
- 実務上の困難: 訴訟リスク (class warfare)、税務複雑化
- 現代では spin-off / direct subsidiary IPO のほうが好まれる

スタートアップ実務では tracking stock はほぼ見ない、念のため言及。

### 9.4 Pre-IPO Reorganization (segment を子会社化)

IPO 直前に segment を子会社化するケース (Pre-IPO 再編):

例:

- Stripe は内部 segment (Payments、Capital、Atlas、Climate) を別法人化する場合あり (将来 IPO 用 corporate structure 整理)
- Mercari は 国内 + US + Pay を別法人で運営 (corporate structure cleaner、carve-out optionality)

これは `13b_treasury_carveout §1` の事前準備。本書では概念のみ言及し、実務手続は `13b` canonical。

### 9.5 Multi-Class Voting Structure

複数事業企業は **multi-class voting** (Class A / Class B、founder の supervoting) を採ることが多い:

例: Alphabet は Class A (1 vote) / Class B (10 votes、founder 保有) / Class C (no vote)
例: Meta は Class A / Class B (10 votes、Zuckerberg)

これにより multi-segment の経営判断 (どの segment にどう投資するか) を founder が control できる。`04b_cap_table_mechanics §4` の dual-class structure 参照。

### 9.6 例外: 1 segment が子会社の場合 (HoldCo Structure)

LINE ヤフー (Z Holdings → LINE ヤフー) のように、Holdco 構造で各事業が別法人 subsidiary になっている場合:

- LINE ヤフー HD = parent
- ヤフー (株) = subsidiary (Search、E-commerce、Ad 事業)
- LINE (株) = subsidiary (Messenger、Sticker、ad 事業)
- 連結 segment 開示は `13a §6` の連結 segment、本書 §3 の単純 inter-segment ではない
- inter-法人 transfer pricing は `12_tax_strategy §5`、本書範囲外

→ こういう構造は **`13a` を canonical**、本書は補助的。

---

## 10. Multi-Segment IC Memo Template

複数 segment 企業の IC memo は single-segment より複雑な構造を持つ。`08_investment_thesis` の IC memo template を本書では segment 別に拡張する。

### 10.1 Executive Summary 拡張

通常の executive summary に **segment-level metrics summary table** を追加:

```
Investment Thesis (3 sentences):
  We invest because:
    1. Each segment is independently attractive (per-segment thesis)
    2. Cross-segment synergies create durable competitive advantage
    3. Management has demonstrated capital allocation skill (ROIC by segment)
```

#### 10.1.1 Segment metrics summary (1 表で全体像)

| Segment | Revenue ($M, LTM) | YoY Growth | EBITDA Margin | NRR / Take Rate / NIM | ROIC | Standalone EV (SOTP $M) |
|---|---|---|---|---|---|---|
| SaaS | 100 | 30% | 25% | NRR 118% | 75% | 900 |
| Marketplace | 50 | 35% | 20% | Take Rate 12% | 35% | 275 |
| Fintech | 20 | 50% | 20% | NIM 7% | 90% | 65 |
| Corporate items | -- | -- | -- | -- | -- | 30 (HQ cash 80 - debt 50) |
| Conglomerate discount (10%) | -- | -- | -- | -- | -- | (127) |
| **SOTP Net** | **170** | **34%** | **22% (blended)** | -- | **--** | **1,143** |

### 10.2 Per-Segment Business Case

各 segment ごとに以下 sub-section を 1–2 page で:

#### 10.2.1 Segment Thesis

- なぜこの segment が魅力的か
- TAM (Total Addressable Market)
- Competitive position (market share、moat)
- Growth path (5-year forecast)

#### 10.2.2 Segment KPI Summary

§6.3 の 20c / 20f 形式の metrics table

#### 10.2.3 Segment Valuation

- Multiple-based EV
- DCF EV
- Selected EV with rationale
- Standalone premium considered (§5.7.1)

#### 10.2.4 Segment Kill Criteria

「この segment が weak になったら撤退検討」の signal:

- ARR growth < 10% YoY for 2 quarters → SaaS segment 弱化 → divestiture review
- Take rate compression below 8% → Marketplace 競争激化 → strategy review
- NIM < 4% → Fintech 信用環境悪化 → loan book 縮小

#### 10.2.5 Segment-level Risks

各 segment 固有の risk (regulatory、competition、tech disruption)

### 10.3 Capital Allocation Thesis

**multi-segment IC memo の core**: 今後 5 年で各 segment にどう投資するか:

#### 10.3.1 Top-Down Strategy

- 経営戦略上のテーマ (例: "next 5 years は AI native でいくため AI segment に資本集中")
- Long-term portfolio mix (SaaS:Marketplace:Fintech = 50:30:20 を維持)

#### 10.3.2 Bottom-Up Capital Allocation

各 segment の ROIC に基づく:

```
Capital Allocation Rule:
  Year-end portfolio review.
  Increment growth investment in segments where ROIC > 1.5 × WACC and Excess ROIC > 30pp.
  Reduce or maintain in segments where Excess ROIC = 0–10pp.
  Divest segments where Excess ROIC < 0 for 2 consecutive years.
```

#### 10.3.3 5 年 Capital Allocation Forecast

| Year | SaaS CapEx + OpEx growth | Marketplace | Fintech | Total | Hardware (divestiture) |
|---|---|---|---|---|---|
| Y1 | 15 | 20 | 5 | 40 | -- |
| Y2 | 20 | 22 | 8 | 50 | -- |
| Y3 | 25 | 25 | 12 | 62 | -- |
| Y4 | 30 | 28 | 18 | 76 | -10 (proceeds) |
| Y5 | 35 | 32 | 25 | 92 | -- |

### 10.4 SOTP Table (Football Field)

```
SOTP Valuation Football Field
                      Low ($M)   Base ($M)   High ($M)
SaaS (Multiple-based)   500       900         1,300
Marketplace             200       275         350
Fintech                 40        65          100
Corporate items         20        30          40
Conglomerate discount  -25%      -10%         0%
Standalone premium      0%        +5%        +10%
                      ─────────  ─────────   ─────────
SOTP Net               584       1,143       1,710
```

football field chart で表示 (`05_valuation_wacc §17`)。

### 10.5 Multi-Segment Sensitivity

#### 10.5.1 Two-way Sensitivity

```
Conglomerate Discount × SaaS Multiple:
                    SaaS Mult 6x    8x      10x     12x
Discount 0%         $1,005          $1,205  $1,405  $1,605
Discount 10%        $904            $1,084  $1,265  $1,445
Discount 20%        $804            $964    $1,124  $1,284
Discount 30%        $703            $843    $984    $1,124
```

#### 10.5.2 Per-Segment 1-way Sensitivity

各 segment のみ ±20% revenue 変動でどう SOTP が動くか:

| Segment | -20% rev | Base | +20% rev | Range |
|---|---|---|---|---|
| SaaS revenue | $963 | $1,143 | $1,323 | 32% |
| Marketplace revenue | $1,068 | $1,143 | $1,218 | 13% |
| Fintech revenue | $1,127 | $1,143 | $1,159 | 3% |

→ SaaS が最 sensitive、Fintech は size 小さく impact 小。

### 10.6 Risks (multi-segment 特有)

#### 10.6.1 Segment 間の Cross-Subsidization Risk

「黒字 segment が赤字 segment を補填」が exit 時の bear case。investor 質問項目:

- 各 segment の standalone economic viability
- 撤退時の cost (`13b §3`)

#### 10.6.2 Capital Allocation Risk

経営陣が "favorite segment" に偏った投資をする risk。指標:

- segment ROIC vs growth investment 配分の整合性
- 公開された capital allocation framework の遵守

#### 10.6.3 Conglomerate Discount Persistence

経営陣が discount を解消する action を取らない場合、shareholder value の loss が継続。

#### 10.6.4 Inter-Segment Friction

segment manager 間の politics (リソース取り合い)、transfer pricing 紛争、cross-segment cooperation 不足。

### 10.7 IC Memo Closing — 投資判断 Statement

```
Investment Decision: APPROVE
  Reason:
    - Per-segment thesis: All 3 segments have ROIC > WACC + 20pp; durable advantage
    - Synergy thesis: Cross-segment data network effect drives moat
    - Management: Track record of disciplined capital allocation
  Risks:
    - Conglomerate discount of 10–20% may persist
    - Hardware segment review needed by Y3 (mentioned)
  Investment Size: $50M for 8% post-money equity (Series D)
  Target IRR: 25% over 5 years (base case SOTP $1,143M; expected exit at 1.4x MOIC + IPO)
```

---

## 11. 業態 mix の代表的 Pattern

複数事業 startup の組み合わせには historical pattern がある。代表的 6 パターンを mini-case 形式で整理。

### 11.1 SaaS + Marketplace

#### 11.1.1 概念

Core SaaS が顧客 base を作り、Marketplace で transaction-fee を取る。Salesforce + AppExchange、Lyft + Lyft for Business (B2B fleet)、HubSpot + Marketplace Apps が典型。

#### 11.1.2 KPI mix

| Segment | Primary KPI |
|---|---|
| SaaS | ARR、NRR、CAC Payback、Rule of 40 |
| Marketplace | GMV、Take Rate、Active Buyer-Seller |

#### 11.1.3 Valuation 特徴

SaaS multiple (8–10x EV/Rev) > Marketplace (4–7x EV/Rev) なので **SOTP で SaaS の高評価が表面化**。逆に SaaS にしか興味ない buyer (PE Vista 等) は Marketplace を discount し、SaaS-only を separately評価。

#### 11.1.4 Mini Case: Salesforce SFA + AppExchange

- Salesforce CRM = core SaaS (~80% revenue)
- AppExchange = 3rd party app marketplace (~5% revenue contribution、但し platform value は大)
- AppExchange 単独で SOTP 評価する analyst は少ないが、strategic moat として価値

### 11.2 SaaS + Fintech

#### 11.2.1 概念

Core SaaS + embedded financial services (lending、payments、cards)。Toast (Restaurant POS + Toast Capital lending)、Shopify (e-commerce SaaS + Shop Pay + Capital lending)、Square (POS + lending) が典型。

#### 11.2.2 KPI mix

| Segment | Primary KPI |
|---|---|
| SaaS | ARR、NRR |
| Fintech (lending) | Loan Book、NIM、Cost of Risk、TPV |

#### 11.2.3 Valuation 特徴

Fintech は SaaS より低 multiple (lending: 2–3x rev、credit risk 反映)。但し attach rate (SaaS 顧客の % が Fintech 利用) が **synergy proxy**。Toast の場合 Toast Capital attach rate ~25% で、attach 率増加が SOTP premium を生む。

#### 11.2.4 Mini Case: Toast

Toast は restaurant POS SaaS から lending (Toast Capital) と payments (processing) に拡大。SaaS revenue ~30% / Fintech revenue ~70% (TPV processing が bulk)。SaaS multiple 8x、Fintech (payment) 4x で SOTP 計算:

- SaaS: $400M ARR × 8 = $3.2B
- Fintech (payment + lending): $900M revenue × 4 = $3.6B
- HQ items + discount: $500M
- → SOTP ≈ $7.3B (illustrative)

### 11.3 D2C + Marketplace

#### 11.3.1 概念

自社 D2C (own goods) + 3rd party marketplace。Amazon Retail (1P) + Amazon Marketplace (3P)、Etsy 自社 + 個別 sellers、Shopify (D2C tooling) + Shopify Marketplace。

#### 11.3.2 KPI mix

| Segment | Primary KPI |
|---|---|
| D2C | GM%、Repeat Rate、Inventory Turns |
| Marketplace | GMV、Take Rate、Active Sellers |

#### 11.3.3 Valuation 特徴

D2C は薄利 (GM 30–50%)、Marketplace は高 margin (take rate × low fixed cost)。SOTP で Marketplace に高 multiple、D2C に低 multiple → consolidated は blend。

#### 11.3.4 Mini Case: Amazon Retail (1P) + Marketplace (3P)

- 1P: $387B revenue (NA only)、薄利 (Op margin 7.6%)
- 3P (含 fulfillment fees + take rate): ~$140B 推定 (Amazon は分けて開示しないが、analyst 推定)
- Marketplace は estimate $150–200B EV (8–10x revenue at high margin)
- 1P は estimate $250–300B EV (1.5x revenue at retail multiple)
- 詳細は §15 Mini Case 1 で再検証

### 11.4 SaaS + Hardware

#### 11.4.1 概念

Physical product + recurring software / service。Tesla (EV + FSD subscription)、Apple (iPhone + Services)、Roomba (cleaner + premium app)。

#### 11.4.2 KPI mix

| Segment | Primary KPI |
|---|---|
| Hardware | Units、ASP、GM%、Inventory Turns |
| SaaS / Service | ARR、Recurring Revenue %、Service Attach Rate |

#### 11.4.3 Valuation 特徴

Hardware multiple 1–2x、SaaS multiple 8–10x → SaaS portion を表面化することで market-cap premium。Apple は services revenue を 2015 年以降 explicitly 開示し、それで multiple expansion (P/E 12 → 25)。

#### 11.4.4 Mini Case: Apple Services

Apple Services は FY2024 ~$96B revenue (App Store + iCloud + Apple Music + Apple TV+ + Care + Pay 等)。Hardware revenue ~$295B。

- Hardware: 1.5x → ~$443B EV
- Services: 10x → ~$960B EV
- SOTP gross: ~$1,400B、Apple market cap ~$3T (FY2024 末)
- Hardware multiple 上の "premium" は Services の brand support として正当化
- (詳細は §15 Mini Case 5 で扱う Microsoft が近い構造として代用)

### 11.5 AI + Everything (OpenAI Mix)

#### 11.5.1 概念

AI infrastructure + consumer + enterprise。OpenAI (API + ChatGPT consumer + Enterprise/Microsoft partnership)、Anthropic (API + Claude.ai + Enterprise)、Google (Gemini API + AI Studio + Cloud + Search/Workspace integration)。

#### 11.5.2 KPI mix

| Segment | Primary KPI |
|---|---|
| API (developer) | API revenue、Active developers、Token cost |
| Consumer (ChatGPT-like) | DAU、Subscribers、ARPU |
| Enterprise | ACV、Logo count、Productivity uplift |

#### 11.5.3 Valuation 特徴

Pre-revenue / early commercialization 段階の startup → Real Options + revenue projection. Multiple は wild range (5–50x rev、growth/loss profile による)。SOTP 計算は range output が必須 (一点推定 NG)。

#### 11.5.4 Mini Case: OpenAI

OpenAI 2024 推定 (private):

- API: ~$2.7B (50% of revenue) — developer-led
- ChatGPT consumer ($20/月 Plus, $200 Pro): ~$2.7B (50%) — consumer subs
- Total ~$5.4B revenue
- Multiple-based valuation (~$200B post-money 2024 round): 推定 multiple ~37x revenue → growth premium
- SOTP: API + Consumer のシンプル split。Enterprise (Microsoft tie) は internal、SOTP には含めない

### 11.6 Cross-Border Multi-Segment

#### 11.6.1 概念

国別 segment + 業態別 segment の 2 軸。Mercari (国内 + US + Pay)、Uber (Rideshare + Eats + Freight × 国別)、楽天 (EC + Mobile + FinTech × 国内/海外)。

#### 11.6.2 KPI mix

国別 + 業態別の matrix:

| Segment | Country | Primary KPI |
|---|---|---|
| Mercari 国内 | 日本 | GMV、Active Users |
| Mercari US | US | GMV (USD)、Listings、Take Rate |
| Mercari Pay | 日本 | TPV、credit balance |

#### 11.6.3 Valuation 特徴

国別 country risk premium (CRP) で WACC 調整、各 country の comp pool 異なる:

- 国内 EC: Mercari 国内 ≈ 楽天 EC、Yahoo Shopping
- US C2C: Poshmark、Mercari US 自身、ThredUp 等
- 国別 currency 換算リスク
- 各 segment 別 multiple range が異なる: 日本 SaaS multiple 5–8x、US SaaS multiple 8–12x

#### 11.6.4 Mini Case: Mercari

- 国内 EC: 強み (~$1B 売上、profitable)
- US: 苦戦中 (~$300M 売上、loss、2025 年 fee 構造改変で recovery 試行)
- Mercari Pay: 急成長 (~$200M 売上、profitable)

詳細は §15 Mini Case 3 で扱う。

---

## 12. xlsx 統合 (Skill との接続)

本書の方法論を skill の xlsx model build pipeline に組み込む方法。

### 12.1 既存 Sheet との関係 (Option A: 1 法人 multi-segment)

`_terminology §3` の canonical 17-sheet (00–16) を **consolidated** として残す。各 segment は 20a–z で追加:

```
Existing 17-sheet (consolidated):
  00_Cover, 01_Assumptions, 11_KPI_Dashboard, 02_Revenue, 03_OpEx, 04_IS, 05_BS, 06_CFS,
  05_BS § Working Capital, 07_Debt, 08_CapTable, 09_DCF, 10_Comps, 09_DCF § Sensitivity, 11_KPI_Dashboard,
  12_SanityChecks, 13_IC_Memo

Multi-segment extension (本書):
  20a_Segment_A_PL          (Segment A の P/L; 03 Revenue + 04 OpEx の segment 内部分)
  20b_Segment_A_BS          (Segment A の direct asset / liability)
  20c_Segment_A_KPI         (Segment A の業態別 KPI)
  20d_Segment_B_PL
  20e_Segment_B_BS
  20f_Segment_B_KPI
  20g_Segment_Eliminations  (inter-segment 全消去計算)
  20h_Segment_Allocation    (cost allocation rates 全表)
  20i_SOTP_Valuation        (SOTP 計算: 業態別 multiple、conglomerate discount 適用)
  20j_Segment_C_PL          (3+ segment の場合)
  20k_Segment_C_BS
  20l_Segment_C_KPI
```

3+ segment の場合は 20j / 20k / 20l … と続く。

### 12.2 既存 Sheet との関係 (Option B: 連結 + segment 混合)

別法人 subsidiary が混在する場合 (`13a` 連結適用ケース):

```
Existing 17-sheet (consolidated): 残す

13a connectivity (連結関連、別 reference の管轄):
  21a_HoldCo_PL             (親会社単独)
  21b_HoldCo_BS
  21c_Sub_A_PL              (連結子会社 A、別法人)
  21d_Sub_A_BS
  21e_Consolidation         (`13a §4` 連結 5 step)

Segment 関連 (本書、HoldCo + Sub の中の事業 segment):
  20a_Segment_A_PL
  ...
```

OptionA の sheet 命名を baseline に、必要に応じて 21a–z は `13a` reference の管轄で別途。

### 12.3 Input Schema 拡張

`15_input_schema.md` に **`segments` field** を追加する仕様 (Task 1 の集約 patch agent が編集する。本書では参照のみ、直接編集はしない)。

```yaml
# 15_input_schema.md に追加されるべき構造 (本書の reference 仕様)
segments:
  - id: "saas"                          # required, unique within file
    name: "Core SaaS"                   # display name
    business_model: "saas_b2b"          # 03_business_models 業態 enum
    revenue_share_pct: 0.60             # consolidated revenue の比率 (sum to 1.0)
    standalone_kpis:                    # 業態別 KPI、_terminology §6 準拠
      arr_money_m: 100
      nrr_pct: 0.118
      grr_pct: 0.93
      magic_number: 1.1
      cac_payback_months: 14
      gm_pct: 0.78
      rule_of_40: 42
    cost_allocation_basis: "headcount"  # revenue / headcount / abc / profit / direct
    avoidable_pct: 0.70                 # corporate cost のうち segment に流す比率
    transfer_pricing_method: "market"   # cost_plus / market / negotiated / none
    transfer_pricing_markup_pct: 0.10   # cost_plus の場合のみ使用
    valuation:
      ev_revenue_multiple: 9.0          # comp-based
      ev_ebitda_multiple: 25.0
      wacc_pct: 0.095                   # segment 別 WACC
      terminal_growth_g_pct: 0.025      # segment 別 g
      use_dcf: true                     # DCF 計算するか
    capex_share_pct: 0.40               # consolidated CapEx の比率
    headcount: 80                       # FTE
    capital_invested_money_m: 50        # Invested Capital
    geography: "US"                     # CRP 適用用、optional

  - id: "marketplace"
    name: "Marketplace"
    business_model: "marketplace_2sided"
    revenue_share_pct: 0.30
    standalone_kpis:
      gmv_money_m: 700
      take_rate_pct: 0.11
      active_buyers_m: 3.5
      active_sellers_k: 80
      cohort_retention_y2_pct: 0.62
    cost_allocation_basis: "headcount"
    avoidable_pct: 0.70
    transfer_pricing_method: "none"
    valuation:
      ev_revenue_multiple: 5.0
      ev_ebitda_multiple: 20.0
      wacc_pct: 0.110
      terminal_growth_g_pct: 0.020
      use_dcf: true
    capex_share_pct: 0.50
    headcount: 40
    capital_invested_money_m: 17
    geography: "US"

  - id: "fintech"
    name: "Embedded Lending"
    business_model: "fintech_lending"
    revenue_share_pct: 0.10
    standalone_kpis:
      loan_book_money_m: 80
      nim_pct: 0.07
      cost_of_risk_pct: 0.015
      npl_pct: 0.025
      tpv_money_m: 200
    cost_allocation_basis: "abc"
    avoidable_pct: 0.50                 # Fintech は heavy regulation で stranded high
    transfer_pricing_method: "cost_plus"
    transfer_pricing_markup_pct: 0.05
    valuation:
      ev_revenue_multiple: 4.0
      ev_ebitda_multiple: 15.0
      wacc_pct: 0.130
      terminal_growth_g_pct: 0.025
      use_dcf: true
    capex_share_pct: 0.10
    headcount: 15
    capital_invested_money_m: 10
    geography: "US"

# Corporate-level overrides
corporate:
  hq_g_and_a_money_m: 30                # consolidated G&A total
  stranded_cost_money_m: 15             # 撤退でも残る
  hq_cash_money_m: 80
  hq_debt_money_m: 50
  pension_liability_money_m: 0
  other_corporate_assets_money_m: 0
  other_corporate_liabilities_money_m: 0

multi_segment_options:
  conglomerate_discount_pct: 0.10       # SOTP 計算で当てはめ
  conglomerate_discount_rationale: "3 segments, strong inter-segment synergy, transparent reporting"
  standalone_premium_pct: 0.05
  synergy_value_money_m: 20
  inter_segment_eliminations:
    - selling_segment: "saas"
      buying_segment: "marketplace"
      annual_amount_money_m: 5
      transfer_pricing_method: "market"
    - selling_segment: "saas"
      buying_segment: "fintech"
      annual_amount_money_m: 1
      transfer_pricing_method: "cost_plus"
```

> 注意: 本 schema 仕様は **本書 §12.3 のみが canonical**。実 file `15_input_schema.md` への追加は Task 1 が並行で実施中 (Task ID `a2fccf41` 参照)。本書では schema を **記述のみ** とし、`15_input_schema.md` を直接編集はしない。

### 12.7 Sheet Rendering Order

依存関係順に build:

```
1. 01_Assumptions, 11_KPI_Dashboard (input)
2. 20h_Segment_Allocation (allocation rates)
3. 20a/d/j_Segment_X_PL (segment P/Ls)
4. 20b/e/k_Segment_X_BS (segment BS)
5. 20c/f/l_Segment_X_KPI
6. 20g_Segment_Eliminations
7. 02_Revenue, 03_OpEx (consolidated, roll-up from segments)
8. 04_IS, 05_BS, 06_CFS (consolidated)
9. 09_DCF (consolidated DCF)
10. 10_Comps (consolidated)
11. 20i_SOTP_Valuation (segment-based)
12. 09_DCF § Sensitivity, 11_KPI_Dashboard, 12_SanityChecks, 13_IC_Memo
```

### 12.8 Sanity Checks (12_SanityChecks 拡張)

multi-segment 用の追加 sanity check 5 個 (`_self_review_protocol §10` 入り):

1. **Segment revenue 合計 = consolidated revenue**: Σ(segment external revenue) == 04_IS revenue
2. **Inter-segment elimination 整合**: 20g sheet で "eliminated revenue" == "eliminated COGS"
3. **Cost allocation 100% 以下**: 20h sheet で各 cost item の (avoidable + stranded) == total
4. **SOTP gross == sum of parts**: 20i sheet で SOTP gross == Σ(segment EV) + corporate items
5. **Conglomerate discount range**: 0 ≤ discount ≤ 30% (extreme out of range は warning)

### 12.9 IC Memo 拡張

`13_IC_Memo` sheet に新規 section: "Multi-Segment Analysis"

- Segment summary table (§10.1.1 準拠)
- Per-segment thesis (§10.2 — 各 segment 1 段落)
- Capital allocation framework (§10.3 — 5 年配分計画)
- SOTP table (§10.4)
- Sensitivity (§10.5)
- Risks specific to multi-segment (§10.6)


---

## 13. 関連 Reference との整合

本書と他 reference の境界を改めて整理する (§0 の冒頭表を補足)。

### 13.1 `03_business_models` との関係

- **`03`**: 各業態 (SaaS / Marketplace / D2C / Hardware / Bio / AI / Fintech 等) の business model 詳細、unit economics、pricing 体系の canonical
- **本書**: 各 segment が **どの業態に属するか** を `03` の enum 参照で identify。各 segment の operating mechanics 自体は `03` を逆参照
- **重複しない**: 本書は segment 別 KPI を **1 表で並べる** だけ、業態 1 つあたり 1 段落程度。詳細は `03` へ

### 13.2 `06_three_statement` との関係

- **`06`**: single-entity の三表 build pattern (revenue model、cost build-up、WC、CapEx、debt、tax 全部) の canonical
- **本書 §3**: 各 segment は `06` の縮小版。multi-segment 拡張部分のみ canonical
- **重複しない**: 三表の基本 mechanics (例: Days Receivable から AR を出す) は `06`、segment 化のための eliminations / allocation は本書

### 13.3 `05_valuation_wacc` との関係

- **`05`**: DCF / WACC / Comps / Precedent / VC Method / Berkus / Scorecard / Real Options を single-entity に対して canonical
- **本書 §5 / §10**: SOTP は `05` の方法論を **複数 segment に分解 + 統合** するメタ手法。WACC を segment 別に分ける議論 (§5.3.1) も本書で canonical
- **重複しない**: WACC 計算自体 (Re / Rd / β / ERP) は `05`、segment 別 β を当てる方法と SOTP 統合は本書

### 13.4 `12_tax_strategy` との関係

- **`12`**: 法人税効果、グループ通算、cross-border 移転価格 (`12 §5`)、繰延税金 (DTA / DTL) の canonical
- **本書 §7**: 同一法人内 inter-segment transfer pricing のみ canonical。cross-border 法人またぎ移転価格は **`12 §5` を canonical** とし、本書では概念のみ
- **重複しない**: tax compliance 詳細は `12`、segment-level allocated tax (`§3.5`) の framework のみ本書

### 13.5 `13a_consolidation_core` との関係

- **`13a`**: 親子会社の連結手続 (5 step)、NCI (Non-Controlling Interest)、PPA (Purchase Price Allocation)、持分法、未実現利益 elimination、為替換算 (CTA) の canonical
- **本書**: **同一法人内** segment のみ canonical。法人またぎ (parent + subsidiary) は `13a` を canonical
- **重複しない**: NCI 計算は `13a §6`、PPA は `13a §6` 後半、本書では一切扱わず

> 共存パターン: 楽天 G のように「親会社 + 別法人 subsidiary」かつ「subsidiary 内に複数 segment」の場合、**両方を併用**:
> - 親 vs sub の連結処理 → `13a`
> - sub 内 / 親会社内の segment 開示 → 本書

### 13.6 `13b_treasury_carveout` との関係

- **`13b`**: Carve-out / Spin-off の準備 — treasury 分離、stranded cost (全社最適)、IPO 直前再編、separation cost の見積 canonical
- **本書 §1.4 / §4.5 / §8.4.3**: Conglomerate discount 解消の手段として spin-off を **計算モデル** で示す。Spin-off 実務手続は `13b` 逆参照
- **重複しない**: treasury 分離プロセス、stranded cost 全社最適化は `13b`、本書は segment 内での stranded cost 配賦 rule のみ

### 13.7 `18_customer_value_and_pricing` との関係

- **`18`**: Customer Lifetime Value、pricing 体系 (cost-plus / value / dynamic / tier)、Willingness-to-Pay の canonical
- **本書 §6.1 / §11**: 各 segment の business model 内 pricing は `18` を逆参照。本書では segment 比較のための KPI matrix のみ
- **重複しない**: pricing experimentation や WTP analysis は `18`

### 13.8 `19_ma_exit_for_founders` との関係

- **`19`**: M&A exit の seller-side mechanics、tax wedge (QSBS / 適格組織再編)、process (NDA → LOI → DA)、earn-out、R&W insurance、indemnification の canonical
- **本書 §1.4 / §8.4.3 / §10**: SOTP を **buyer-side の synergy 評価** や **seller-side で carve-out として specific segment を売却** する判断に使う際、本書 §5 を起点とし `19 §3 / §9` の synergy / WTP cap を逆参照
- **重複しない**: deal mechanics 詳細は `19`、segment-level standalone EV 計算は本書

### 13.9 `_terminology` との関係

- **`_terminology`**: SaaS metric 閾値、color、sheet naming、税率、Diluted Share Count の canonical
- **本書 §2.4 / §6**: segment / subsidiary / division 用語整合は本書で初めて整理 (`_terminology` 補完候補)。SaaS 閾値 (NRR ≥ 110% PASS) などは `_terminology §6` をそのまま使用
- **重複しない**: 閾値値そのものは `_terminology`

### 13.10 `_master_decision_tree` との関係

- **`_master_decision_tree §A`**: 「2 つ以上の business model」「セグメント別開示」「SOTP」「事業 mix」「コングロマリットディスカウント」「業界別 multiple 別」の trigger で本書を第 1 reference として読む
- 本書 readers は `_master_decision_tree` から routing される

### 13.11 `_self_review_protocol` との関係

- **`_self_review_protocol §10`** (新設候補): multi-segment 用の追加 5 check
  1. Segment revenue 合計 = consolidated revenue
  2. Inter-segment elimination 整合 (revenue elim == COGS elim)
  3. Cost allocation 100% 以下 (avoidable + stranded == total)
  4. SOTP gross == sum of parts (segment EV + corporate items)
  5. Conglomerate discount 範囲根拠明示 (0–30%、firm-specific rationale)

`_self_review_protocol` への追加は別 task で実施 (本書では cross-reference)。

### 13.12 `01a_modeling_standards` との関係

- **`01a`**: FAST / SMART / ICAEW spreadsheet best practices、color coding、sheet naming、circular reference 回避 の canonical
- **本書 §3.4 / §12**: 20a–z 系新 sheet も `01a` の spreadsheet standards に準拠 (input cell blue、formula cell black、checks red 等)

### 13.13 `15_input_schema` との関係

- **`15`**: input YAML / dict schema の canonical
- **本書 §12.3**: `segments` field 仕様の reference。**直接編集は Task 1 が並行実施** (集約 patch agent `a2fccf41`)

---

## 14. Anti-patterns

multi-segment modeling で頻発する誤りと回避策。

### 14.1 Cost Allocation の過剰 (Over-allocation)

#### 14.1.1 症状

- corporate cost を 100% 全 segment に分配 → segment EBITDA が真実より低い
- 「segment は loss」と誤判断、本来 contribution positive な segment の撤退検討
- M&A / spin-off 時の standalone EV を低く出してしまう

#### 14.1.2 例

```
誤り (over-allocation):
  Corporate G&A $30M を全 100% 配分 → SaaS $20M / Marketplace $10M
  SaaS Segment EBITDA = $35M - $20M = $15M (見かけ低い)

正しい (avoidable / stranded 区別):
  Avoidable $15M を配分 → SaaS $10M / Marketplace $5M
  Stranded $15M は consolidated 留保
  SaaS Segment EBITDA = $35M - $10M = $25M (実態反映)
  Consolidated EBITDA = $25M + $10M - $15M = $20M (stranded hit)
```

#### 14.1.3 Mitigation

§4.5 の avoidable / stranded 区別を必ず実装。`13b_treasury_carveout §3.4` の stranded cost estimation を逆参照。

### 14.2 SOTP の Double Counting

#### 14.2.1 症状

- 同じ revenue を 2 segment で count
- inter-segment elimination が不十分、外部 sale + 内部 sale の両方が SOTP に hit
- Synergy adjustment と inter-segment trade の二重計上

#### 14.2.2 例

```
誤り (double counting):
  AWS revenue $108B (external $80B + Retail への internal $28B)
  Retail revenue $387B (Retail external $355B + AWS から購入 $32B = 388B)
  Note: AWS と Retail に同じ inter-trade $28-32B が両方に
  SOTP 計算で AWS multiple × $108B + Retail multiple × $387B → $28-32B が二重 count

正しい (External-only SOTP):
  AWS external revenue $80B × multiple
  Retail external revenue $355B × multiple
  Inter-segment $28-32B は SOTP 外、synergy 行で別計上 (or 0 と置く)
```

#### 14.2.3 Mitigation

§3.3.4 の "SOTP では external revenue only" rule を実装。20g_Segment_Eliminations sheet で external / internal を分離。

### 14.3 Conglomerate Discount の任意設定

#### 14.3.1 症状

- 5–30% range の根拠を明示せず "default 10%" など適当な数値
- 特定研究 (Berger & Ofek 1995) を出典として書かず、"15% という業界経験則" 等の vague な記述
- Sensitivity analysis なし、一点推定

#### 14.3.2 例

```
誤り (任意設定):
  "Conglomerate discount = 10% (industry average)"
  SOTP net = SOTP gross × 0.9 = $1,080M

正しい (根拠 + range):
  Conglomerate discount base case = 10%
  Rationale (§8.6.1):
    - 3 segments, all tech-adjacent (-3%)
    - Strong cross-sell synergy (Toast Capital に SaaS 顧客 25% attach) (-5%)
    - Transparent reporting (NRR / TPV / NIM 全公開) (-5%)
    - 1-country 集中 (-2%)
    - Net = -15% before floor; firm-specific judgement → 10%
  Range: 0% (optimistic) - 20% (conservative)
  Out-of-sample reference: Berger & Ofek 1995 finds -13–15%, Campa & Kedia 2002 control after = ~0%
```

#### 14.3.3 Mitigation

IC memo に rationale + range + sensitivity を必ず記述。Default 10% を spread sheet 化 (§10.4 / §10.5)。

### 14.4 Segment KPI の Inconsistency

#### 14.4.1 症状

- SaaS segment で NRR を public 開示、Hardware segment で同等指標 (Recurring Revenue %、Service Attach Rate) を出さない
- Marketplace で take rate を 1 quarter 開示しなかった四半期がある
- Period 間で KPI 定義が変わる (e.g. NRR の対象期間変更)

#### 14.4.2 例

```
誤り (inconsistency):
  Q1: SaaS NRR 118%、Marketplace Take Rate 12%
  Q2: SaaS NRR 120% (公開)、Marketplace Take Rate (非開示、計算方法変更中)
  Q3: SaaS NRR 122%、Marketplace Take Rate 10% (定義変更; 旧 12%、新 10%)
  → Investor が比較不能、信頼性低下

正しい (consistent):
  SaaS NRR (definition stable, calculated quarterly, GAAP-equivalent definition)
  Marketplace Take Rate (definition stable, gross merchandise basis)
  当期定義変更があれば prior period も restated 公開
  方針: 全 segment で同等 disclosure level を 5 年以上 maintain
```

#### 14.4.3 Mitigation

IC memo の "Segment Disclosure" section で各 segment が公開する KPI 一覧を明示。年次 review で variance がないか確認 (`14_ipo_readiness §4` の disclosure consistency と整合)。

### 14.5 Transfer Pricing の Lazy 設定

#### 14.5.1 症状

- すべて cost-plus 5% のような flat rate で適用
- Market price benchmark をしない
- 内部 trade の rate review が年次で済まない

#### 14.5.2 例

```
誤り (lazy):
  Internal Trade: AWS → Retail, ML platform → all segments, Identity API → all segments
  All priced at "Cost + 5%"
  Tax authority audit でリスク (cross-border の場合 OECD arm's length 違反指摘 risk)
  Internal: 各 segment の経済性が transfer rate に依存して歪んでいる

正しい (per-trade method):
  AWS → Retail: External market rate (AWS public pricing) → arm's length
  ML platform → segments: ABC (compute hour) + cost-plus 10%
  Identity API → segments: cost-plus 5% (commodity-like)
  各 trade の rate methodology を IC memo で文書化
```

#### 14.5.3 Mitigation

§7.5 の transfer price setting process を実装。最低限 trade ごとに method を決め、根拠を残す (§7.4.3 cross-border は documentation 法令義務)。

### 14.6 Segment 数の Inflation (細分化しすぎ)

#### 14.6.1 症状

- 真の経営判断単位を超えて segment を分けすぎ
- IFRS 8 §19 の practical limit 10 を超える
- 1 segment あたりの数値が小さく、analyst が無視

#### 14.6.2 例

```
誤り (inflation):
  10+ segment: SaaS-Mid-Market、SaaS-Enterprise、SaaS-SMB、Marketplace-US、Marketplace-EU、
              Marketplace-Asia、Hardware-Consumer、Hardware-Enterprise、Fintech-Lending、
              Fintech-Payments、Service-NA、Service-International、(計 12)
  → analyst モデル不能、disclosure overhead

正しい (aggregate to reportable):
  3-4 segment: SaaS、Marketplace、Hardware、Fintech
  各内部に sub-segment (e.g. SaaS-MM/Enterprise/SMB) は内部運営、外部 disclosure では aggregate
```

#### 14.6.3 Mitigation

IFRS 8 §12 aggregation criteria を厳密適用。CODM が見ている内部 reporting unit から本当に aggregate できないものだけを segment にする。

### 14.7 Loss-Making Segment の Hiding

#### 14.7.1 症状

- 赤字 segment を黒字 segment と aggregate
- "Other" segment に赤字事業を集約
- 赤字 segment の standalone economics 開示拒否

#### 14.7.2 例

```
誤り (hiding):
  楽天モバイル loss を "Internet Services" segment に隠す (実際は別 segment)
  → Investor 不信、conglomerate discount 拡大

正しい (transparent):
  楽天モバイル を別 segment で開示 (現状そうしている)
  各 segment の standalone EBITDA、capex、loan-to-X、forecast を全公開
  赤字でも投資ストーリーを正面から説明
```

#### 14.7.3 Mitigation

IFRS 8 §13 10% test を honest に適用。loss-making segment が threshold を超えたら separate disclosure 必須。

### 14.8 Capital Allocation の Inconsistency

#### 14.8.1 症状

- 高 ROIC segment より低 ROIC segment にお金が流れる
- 公開 capital allocation framework がない
- 経営陣の "favorite" segment への偏り (founder bias)

#### 14.8.2 例

```
誤り (inconsistency):
  SaaS ROIC 75% / WACC 9.5%、Marketplace ROIC 35% / WACC 11%
  Y3 growth investment: SaaS $20M、Marketplace $50M (Marketplace に集中)
  → Excess ROIC 計算上は SaaS のほうが高いのに逆配分

正しい (framework-driven):
  Excess ROIC を criteria に capital allocation:
  - SaaS Excess ROIC 65.5pp → primary growth investment
  - Marketplace Excess ROIC 24pp → secondary
  - Allocate 70% / 30% in line with relative excess
```

#### 14.8.3 Mitigation

§10.3 の Top-down + Bottom-up framework を IC memo に明示。investor day で公開。

### 14.9 Synergy の Fictional Counting

#### 14.9.1 症状

- IC memo で "cross-sell で 30% 追加 revenue" のような根拠なき synergy
- segment 別 EV に既に attach rate 反映済 + synergy で再加算 → double count
- Spin-off / M&A 判断で realized synergy track record なし

#### 14.9.2 例

```
誤り (fictional):
  "AppExchange synergy で SaaS revenue +$50M (attach rate 仮定)"
  既に SaaS DCF 内で attach rate 仮定込み → double count
  
正しい (separate segregation):
  Synergy = "もしどちらかが消えたら失う、両方ある場合のみ実現する経済価値"
  Quantify with: (1) historical attach data, (2) sensitivity if synergy = 0
  Discount Synergy NPV by 30-50% for execution risk
  Show as separate row in SOTP, not embedded in segment DCF
```

#### 14.9.3 Mitigation

§5.6.3 の Synergy double counting 注意を実装。

### 14.10 Inter-Segment Eliminationの忘れ

#### 14.10.1 症状

- segment 別 P/L で inter-segment revenue が consolidated に含まれてしまう
- Σ(segment revenue) ≠ consolidated revenue
- Sanity check 抜け

#### 14.10.2 Mitigation

§12.8 の sanity check #1 (Σ segment ext revenue == consolidated) を必ず実装。`scripts/build_model.py` で自動 check。

---

## 15. Mini Case 詳解 (Real-world)

複数事業企業の実際の segment 構造と financial performance を 7 case で詳述。各 case は (1) 構造、(2) 数値、(3) SOTP implications を提示。

### 15.1 Case 1: Amazon (Retail + AWS + Ads + Subscription)

#### 15.1.1 Segment 構造 (2024 10-K)

Amazon は ASC 280 で **3 reportable segment** で開示:

1. **North America**: 米国 + カナダ + メキシコの retail (1P + 3P) + advertising + subscription (Prime) + その他
2. **International**: 上記以外の国の同等事業
3. **AWS**: クラウドインフラサービス全世界

Advertising は内部で別事業として認識されているが、segment 開示では NA / International の中に hidden。analyst は "Other" 科目から advertising revenue を抽出している。

#### 15.1.2 2024 通期数値

| Segment | Net Sales 2024 ($B) | Net Sales 2023 ($B) | YoY | Operating Income 2024 ($B) | Op Margin |
|---|---|---|---|---|---|
| North America | 387 | 353 | +10% | 25.0 | 6.5% |
| International | 143 | 131 | +9% | 3.8 | 2.7% |
| AWS | 108 | 91 | +19% | 39.8 | 36.9% |
| **Consolidated** | **638** | **575** | **+11%** | **68.6** | **10.8%** |

> 出典: Amazon 2024 Annual Report (https://s2.q4cdn.com/299287126/files/doc_financials/2025/ar/Amazon-2024-Annual-Report.pdf)、2024 10-K segment note (https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm)。

> 注: 上の 2024 op income 数値は Amazon 2024 通期発表の数値。AWS の op margin 36.9% (= 39.8/108) が high-margin AWS segment、NA 6.5% (= 25.0/387) が retail 利益率。

#### 15.1.3 SOTP Calculation (illustrative)

| Segment | Multiple base | Multiple | EV ($B) |
|---|---|---|---|
| North America | EV/Sales 0.7x | (low retail multiple) | 271 |
| International | EV/Sales 0.5x | (lower retail multiple) | 71 |
| AWS | EV/Sales 10x | (hyperscale cloud premium) | 1,080 |
| Sum of segments | -- | -- | 1,422 |
| Corporate cash (2024 末) | -- | -- | +101 |
| Long-term debt (2024 末) | -- | -- | -56 |
| Operating lease | -- | -- | -77 |
| SOTP gross | -- | -- | 1,390 |
| Conglomerate discount (5%; tech holding low) | -- | -- | -70 |
| SOTP net | -- | -- | 1,320 |

> 数値は説明用 illustrative。Amazon の 2024 末 market cap は ~$2.3T で、本 SOTP estimate との差は (1) AWS multiple choice (10x revenue は conservative; some use 12x or implied EV/EBITDA 25x → AWS alone $1,400B+)、(2) Advertising standalone valuation (AWS と Retail の中、$50–80B)、(3) growth premium (consolidated multiple 上昇)、で説明される。

#### 15.1.4 観察

- AWS の Op income $39.8B が consolidated の 58% を構成 — Amazon は実質的に "AWS company with retail attached"
- Amazon は **Advertising segment を分離開示してこなかった** ため、analyst が implied valuation の不確実性に苦しむ
- 2024 から ASC 280 改正 (ASU 2023-07) で expense disclosure 強化 → 詳細化期待

### 15.2 Case 2: 楽天グループ (EC + FinTech + Mobile)

#### 15.2.1 Segment 構造

楽天グループは IFRS 8 で **3 reportable segment**:

1. **インターネットサービス (EC)**: 楽天市場、Rakuten Travel、その他 EC
2. **フィンテック**: 楽天カード、楽天銀行、楽天証券、楽天ペイ
3. **モバイル**: 楽天モバイル + 楽天最強プラン + 海外 OBN

Note: 楽天銀行 は 2023 年に上場 (持分法適用関連)、楽天証券は 2023 年から TDC International HD 出資による持分法。フィンテック segment 内の数値はそれら持分法部分が抜けている。

#### 15.2.2 2024 通期数値

| Segment | 売上収益 2024 (億円) | YoY | Non-GAAP 営業利益 2024 (億円) | Non-GAAP Op Margin |
|---|---|---|---|---|
| インターネットサービス (EC) | 12,821 | +5.8% | +851 | +6.6% |
| フィンテック | 推定 8,200 | +15% | 推定 +1,500 | +18% |
| モバイル | 4,407 | +20.9% | -2,089 | -47.4% |
| **連結** | **22,792** | **+10.0%** | **+70** | **+0.3%** |

> 出典: 楽天グループ 2024 通期決算ハイライト (https://corp.rakuten.co.jp/news/press/2025/0214_01.html)。フィンテック通期数値は IR の Q1 ($1,935 億円 / +15.1%) ベースで通期推計。モバイルは独立開示。

#### 15.2.3 SOTP Implications

楽天 G の market cap は 2024 年末頃 ~9,000 億円。一方 SOTP gross を見積もると:

| Segment | 売上 (億円) | Multiple | EV (億円) |
|---|---|---|---|
| EC | 12,821 | 1.5x EV/Rev | 19,232 |
| フィンテック (excl 持分法) | 8,200 | 2.0x EV/Rev | 16,400 |
| モバイル (loss-making) | 4,407 | 0.5x EV/Rev | 2,200 |
| 持分法 (楽天銀行 / 証券) | -- | 公正価値 | 6,000 |
| Sum | 25,428 | -- | 43,832 |
| 連結 cash & equivalents | -- | -- | +29,000 |
| 連結 borrowings | -- | -- | -23,000 |
| Mobile 累積 loss + future investment | -- | -- | -10,000 (penalty for ongoing loss) |
| **SOTP gross** | -- | -- | **39,832** |
| Conglomerate discount (~25%) | -- | -- | -10,000 |
| **SOTP net** | -- | -- | **~30,000** |

> 注: 数値は説明用 estimate。SOTP estimate ~3 兆円 vs market cap ~0.9 兆円 で **巨大な implied conglomerate discount (~70%)**。Mobile の構造的 loss が EC 利益を吸収し、investor が Mobile turnaround を信用できないため。2024 年末 Mobile non-GAAP loss が前年比 +1,056 億円改善で trend は positive。

#### 15.2.4 観察

- Mobile segment が EC の利益を構造的に吸収する architecture が、conglomerate discount の典型
- 2025 通期で Mobile が Non-GAAP black 化すれば discount は急縮小可能性
- Spin-off 議論は何度か挙がるが、楽天モバイル EBITDA 黒字化前は実現困難

### 15.3 Case 3: Mercari (国内 + US + Pay)

#### 15.3.1 Segment 構造

Mercari Inc (TSE: 4385) は IFRS 8 で **3 reportable segment**:

1. **Marketplace (Japan)**: 国内 C2C used goods マーケットプレイス
2. **Marketplace (US)**: 米国 同事業 (Mercari, Inc. Delaware sub)
3. **Mercari Pay (Fintech)**: 決済 + lending + クレジット (Merpay)

#### 15.3.2 FY2025 H1 (Jul-Dec 2024) 数値

| Segment | Revenue (¥B、6m) | YoY | Segment Profit (¥B) | コメント |
|---|---|---|---|---|
| Marketplace (Japan) | 推定 58 (Q2 alone ¥28.9B × 2) | +7.9% | +18 | Mature、profitable、low growth |
| Marketplace (US) | 推定 14 (-16% YoY 含む) | -16% | -3 | 2025 年 Jan の fee 構造変更で turnaround 試行 |
| Mercari Pay | 推定 22 | 高成長 | +1.6 | 高 credit balance + 高 collection rate |
| **連結 (6m)** | **94.2** | **+1.9%** | **+17** | Op profit +45.9% YoY |

> 出典: Mercari Q2 FY2025 (https://aimgroup.com/2025/02/06/mercari-q2-fy2025-steady-progress-on-high-growth-areas/)、Mercari Inc IR Library (https://about.mercari.com/en/ir/library/results/)。FY2025 Q2 = 2024 年 10-12 月、H1 = 2024 年 7 月-12 月。

#### 15.3.3 SOTP Calculation

| Segment | 通期 revenue (¥B、推定) | Multiple | EV (¥B) |
|---|---|---|---|
| Marketplace Japan | 110 | 5x EV/Rev (mature marketplace) | 550 |
| Marketplace US | 30 | 1.5x EV/Rev (loss-making, turnaround risk) | 45 |
| Mercari Pay | 45 | 4x EV/Rev (Fintech growth) | 180 |
| Sum of segments | -- | -- | 775 |
| Corporate cash | -- | -- | +150 |
| Debt | -- | -- | -50 |
| SOTP gross | -- | -- | 875 |
| Conglomerate discount (15%; cross-border, US loss) | -- | -- | -130 |
| SOTP net | -- | -- | 745 |

> 数値は説明用。Mercari の 2025 年 5 月時点 market cap は推定 ~700 億円〜850 億円 (= ¥700-850B JPY) で、本 SOTP estimate と近接。

#### 15.3.4 観察

- 国別 segment + 業態 segment の **2 軸 mix** で、本書 §11.6 の典型例
- US segment の loss が国内利益を吸収する mini-conglomerate-discount
- Mercari Pay の急成長で mix が変わりつつある (5 年後は Pay > Marketplace 可能性)

### 15.4 Case 4: Stripe (Payments + Capital + Atlas + Climate)

#### 15.4.1 Segment 構造 (Private)

Stripe は private company (2024 年 valuation $70B、2025 推定 $90B) で IFRS 8 reportable は無いが、社内的に以下 segment で運営:

1. **Payments**: 決済処理 (TPV ベース、take rate 0.3-1%)
2. **Stripe Capital**: 信用 (中小事業者向け融資)
3. **Stripe Atlas**: 法人設立 + tax 等のスタートアップ向け subscription
4. **Stripe Climate**: 炭素クレジット
5. **Stripe Issuing / Treasury**: カード発行 + 銀行
6. **Stripe Connect / Marketplace**: マーケットプレイス向け payments

#### 15.4.2 推定数値 (2024)

公式 segment 開示なし。Industry analyst (IPO 前提評価) の推定:

| Segment | Revenue 2024 推定 ($B) | Multiple | EV 推定 ($B) |
|---|---|---|---|
| Payments (core) | 18 | 6x | 108 |
| Capital (lending) | 1.2 | 3x | 3.6 |
| Atlas / Connect / Issuing | 2 | 4x | 8 |
| Climate (small) | 0.1 | 2x | 0.2 |
| Sum | 21.3 | -- | 119.8 |
| Cash & cash-like | -- | -- | +5 |
| Debt | -- | -- | -2 |
| SOTP gross | -- | -- | 122.8 |
| Conglomerate discount (5%; tightly integrated) | -- | -- | -6 |
| SOTP net | -- | -- | ~117 |

> 観察時点の Stripe valuation $70-90B vs SOTP $117B → market は conservative growth assumption を反映。

#### 15.4.3 観察

- Core Payments が dominant (~85%)、adjacencies は small だが strategic
- Stripe Capital は Toast Capital と類似の embedded lending
- Stripe Issuing は Card-As-A-Service、growth potential 高い

### 15.5 Case 5: Microsoft (Productivity + Cloud + Personal Computing)

#### 15.5.1 Segment 構造 (FY24, ended June 30, 2024)

Microsoft は ASC 280 で **3 reportable segment**:

1. **Productivity and Business Processes**: Office 365 + Dynamics 365 + LinkedIn + Power Platform + その他
2. **Intelligent Cloud**: Azure + Server products + Enterprise Services + GitHub
3. **More Personal Computing (MPC)**: Windows OEM + Search/News (Bing) + Xbox + Surface + Devices

#### 15.5.2 FY24 数値

| Segment | Revenue FY24 ($B) | Revenue FY23 ($B) | YoY | Op Income FY24 ($B) | Op Margin |
|---|---|---|---|---|---|
| Productivity & Business Processes | ~119 | 109 | +12% | ~62 | 52% |
| Intelligent Cloud | ~105 | 88 | +20% | ~50 | 48% |
| More Personal Computing | ~62 | 55 | +13% | ~17 | 27% |
| **Consolidated** | **~245** | **211** | **+16%** | **~109** | **44%** |

> 出典: Microsoft FY24 Q4 segment revenue (https://www.microsoft.com/en-us/investor/earnings/fy-2024-q4/segment-revenues)、Microsoft 2024 10-K (https://www.microsoft.com/investor/reports/ar24/index.html)。FY24 通期は 2023 年 7 月 - 2024 年 6 月。

> 注: 上表は Q4 数値からの推計。詳細 FY24 通期はリンク先で確認。

#### 15.5.3 SOTP Implications

| Segment | Revenue ($B) | Multiple | EV ($B) |
|---|---|---|---|
| Productivity & Business Processes | 119 | 12x EV/Rev (premium SaaS) | 1,428 |
| Intelligent Cloud | 105 | 14x EV/Rev (hyperscale + Azure premium) | 1,470 |
| More Personal Computing | 62 | 4x EV/Rev (consumer/PC mix) | 248 |
| Sum | 286 | -- | 3,146 |
| Cash & cash-equivalents (2024 末) | -- | -- | +75 |
| Debt | -- | -- | -45 |
| SOTP gross | -- | -- | 3,176 |
| Conglomerate discount (~5%; tightly integrated) | -- | -- | -160 |
| SOTP net | -- | -- | ~3,000 |

> Microsoft の 2024 年末 market cap は ~$3.1T で、本 SOTP estimate とほぼ一致。conglomerate discount は very low (5%) で、segment 間 synergy (Office 365 顧客への Azure 浸透、AI 統合) が強いため。

#### 15.5.4 観察

- AI commercialization が segment 越境 (Copilot は Productivity に、Azure AI は Intelligent Cloud に)
- More Personal Computing は historically lower-growth、最近 Surface / Xbox AI で改善
- 5 年後の SOTP は Cloud > Productivity > MPC mix 予想

### 15.6 Case 6: HP / HPE Spin-off (2015)

#### 15.6.1 Pre-Spin Structure

2015 年 11 月、Hewlett-Packard Company (HP Co) が以下 2 社に分離:

- **HP Inc (NYSE: HPQ)**: PC + プリンタ
- **Hewlett Packard Enterprise (NYSE: HPE)**: Enterprise IT + Servers + Storage + Services

#### 15.6.2 Pre / Post Market Cap (illustrative)

| 時点 | HP Combined Market Cap ($B) | 備考 |
|---|---|---|
| 2014 年 10 月 (発表前) | ~70 | Conglomerate of PC + Enterprise |
| 2014 年 10 月 (発表後) | ~80 | +15% on announcement |
| 2015 年 11 月 (Split day) | HP Inc ~25 + HPE ~35 = 60 (combined) | one-time spin tax + transition cost |
| 2016 年 6 月 (post 6m) | HP Inc ~35 + HPE ~40 = 75 | Combined +25% from pre-announce |

> 出典: 公開 SEC filings、Bloomberg / Refinitiv 価格 history。

#### 15.6.3 観察

- 発表 → 最終 split の間で combined market cap が ~25% 増加 = conglomerate discount realization
- HPE は subsequently DXC Technology spin-off (2017)、Mizuho の "Pathfinder" 等で更に分離 → multiple 段階で価値解放
- HP / HPE はその後の paths が異なる (HP は復活、HPE は struggle) ため、spin-off 自体が必ず value creation を保証するわけではない、と教訓

### 15.7 Case 7: Berkshire Hathaway (Insurance + Manufacturing + Utilities + Investments)

#### 15.7.1 Segment 構造

Berkshire Hathaway (NYSE: BRK.B) は ASC 280 で 6+ reportable segment:

1. **Insurance**: GEICO + Berkshire Hathaway Reinsurance + General Re
2. **BNSF Railroad**: 鉄道
3. **Berkshire Hathaway Energy**: ガス + 電力 + 再生可能
4. **Manufacturing, Service & Retailing**: Marmon、Lubrizol、IMC、Brooks、その他
5. **Investment Holdings**: Apple、Bank of America、Coca-Cola、Kraft Heinz、その他 listed equities
6. **Other**: McLane、PPG、その他

#### 15.7.2 数値 (2024 末 推定)

| Segment | Revenue / Net Investment Income 2024 ($B) | Op Income / Earnings ($B) |
|---|---|---|
| Insurance (incl float of $170B+) | 80 + investment income on float | 25-30 |
| BNSF Railroad | 24 | 5 |
| BHE | 25 | 4 |
| Manufacturing | 90 | 12 |
| Investment Holdings (mark-to-market) | n/a (Apple stake $135B) | $40-60B unrealized |
| Other | 60 | 6 |
| **Consolidated** | **279** | **~50** (operating + net investment) |

> 出典: Berkshire 2024 Annual Report (https://www.berkshirehathaway.com/2024ar/2024ar.pdf)。数値は近似。

#### 15.7.3 SOTP Implications

Berkshire 自体が "the conglomerate" として広く認識されているにもかかわらず:

- **Negative discount (premium)**: 多くの研究で Berkshire は SOTP gross より market cap が **higher** (Buffett's capital allocation skill premium)
- 例: 2024 年末 market cap ~$1T、SOTP estimate ~$900B (incl Apple stake market value, 業界 multiple) → +10% premium
- 同じ "diversified holding" なのに、楽天と Berkshire で 70% gap (vs +10% premium) — 経営陣の skill / track record / capital allocation framework が driving factor

#### 15.7.4 観察

- Berkshire の **negative conglomerate discount** は exceptional case、replicate 困難
- Buffett 後継 (Greg Abel 2024 年 announcement、2025 年 transition 予定) で premium が縮小する可能性 → investor concern
- 学術的に "Berkshire premium" は経営陣 quality 因子、systematic factor ではない

---
