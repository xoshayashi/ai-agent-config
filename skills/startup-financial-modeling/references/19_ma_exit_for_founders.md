---
name: ma_exit_for_founders
description: スタートアップ M&A exit における創業者・既存投資家視点の deal structure、税務、process、ファクトベースの判断ロジック正本。Cap table の exit waterfall を出発点に、earn-out / lock-up / WC adjustment / R&W insurance / タックスストラクチャ含めた sell-side 全般を網羅
type: reference
priority: P0
related: [04b_cap_table_mechanics, 05_valuation_wacc, 08_investment_thesis, 12_tax_strategy, 13a_consolidation_core, 18_customer_value_and_pricing, _terminology]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: スタートアップ M&A exit における **founder / 既存投資家視点** の sell-side mechanics — deal structure (cash / stock / earn-out / roll-over)、tax wedge (US QSBS / 日本適格組織再編)、process (NDA → LOI → DA)、戦略的買収候補 Comps、indemnification escrow、R&W insurance、founder-net analysis、Investor exit IRR — の方法論はすべて本書を canonical とする。`04b_cap_table_mechanics §6` (Exit Waterfall) はこの reference の出発点であり、本書はそれを **税後 founder net cash + stock の bridge** まで延長する。
- **Routing**: [`_master_decision_tree.md §A (構築)`](_master_decision_tree.md) の "exit thesis" / "M&A waterfall" / "founder net" / "earn-out" / "tax-free reorganization" / "適格株式交換" / "QSBS" 関連 entry の第 1 reference。`scripts/build_model.py` が `08_CapTable Exit Waterfall` を埋める際、および `13_IC_Memo` の "Exit Thesis" section を生成する際に参照される。
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §9`](_self_review_protocol.md) の追加 5 check (LP preference 漏れ / earn-out 100% 想定違反 / tax wedge flat 仮定違反 / lock-up 期間中 acquirer 株 mark-to-market 実装 / Headline = founder net 誤誘導) を実行。
- **関連 reference**: `04b_cap_table_mechanics §6` (Exit Waterfall — 本書 §6 の起点) / `05_valuation_wacc §7-9` (DCF からの exit value 推定、本書 §9 の WTP 上限と整合) / `08_investment_thesis §7-8` (IC memo "Exit Thesis" section 追加要件) / `12_tax_strategy §3-5` (Tax 詳細 — 本書 §5 はその使用ガイド) / `13a_consolidation_core §4` (適格組織再編の連結処理) / `18_customer_value_and_pricing §4` (pricing realization が exit value に影響) / `_terminology` (用語整合)。

> 用語注: 本書では「Operating System / OS」を避け、「価格決定の仕組み」「pricing 体系」「描画エンジン」「処理系」と表現する (個人ルール)。時系列の数値データは原則として表形式 (markdown table) に揃える。

> 出典規律: ベンチマーク (earn-out 実現率 / IRR / 平均 escrow 比率 / process timeline) は本文中に出典を明示し、複数ソースが矛盾する場合はレンジで提示する (平均化はしない)。

---

# 19. M&A Exit for Founders — 創業者視点の M&A exit 徹底リファレンス

> 本ドキュメントは、これまで `04b §6 Exit Waterfall` で扱っていた **liquidation preference の payout 計算** を起点に、その上下流の sell-side mechanics — buyer typology、consideration mix、tax structuring、process、indemnification、earn-out、R&W insurance、Investor exit IRR — を 1 冊にまとめた正本である。
>
> **対象読者**: Claude (xlsx exit waterfall / IC memo Exit Thesis 生成エージェント)、IC memo の Exit Thesis を書くアナリスト、それを review する人間バンカー / VC partner / founder。
>
> **Scope (INCLUDE)**: sell-side 全般、founder-net analysis、Investor exit IRR、deal structure 全種 (cash / stock / mix / earn-out / roll-over / reverse vesting)、tax wedge (US QSBS Section 1202 — pre-OBBBA / post-OBBBA / 日本適格組織再編)、process (NDA → CIM → IOI → LOI → DD → DA → Signing → Closing)、戦略的買収候補 Comps、indemnification escrow、R&W insurance、MAC clause。
>
> **Scope (EXCLUDE — 別 reference 候補)**: acquirer-side accretion/dilution 詳細、PPA (Purchase Price Allocation)、LBO debt schedule、buyer-side synergies modeling 詳細 (LBO model 自体は §3.2 で WTP 推定の文脈で簡略言及するに留める)。
>
> **数値の出典**: 出典は本文中に明示。Pitchbook / CB Insights / SRS Acquiom / Boston Consulting / IRS / 国税庁 / 経済産業省 / 公開 M&A press release。

---

## 目次

1. [なぜ founder 視点 M&A exit modeling が必須か](#1-なぜ-founder-視点-ma-exit-modeling-が必須か)
2. [Exit Pathway Tree](#2-exit-pathway-tree)
3. [Buyer Type 分析](#3-buyer-type-分析)
4. [Deal Structure — Consideration Mix](#4-deal-structure--consideration-mix)
5. [Tax Structuring](#5-tax-structuring)
6. [Founder-Net Analysis (Headline → Real Proceeds)](#6-founder-net-analysis-headline--real-proceeds)
7. [Investor Exit IRR](#7-investor-exit-irr)
8. [M&A vs IPO Decision Tree](#8-ma-vs-ipo-decision-tree)
9. [Strategic Comps for Buyer Selection](#9-strategic-comps-for-buyer-selection)
10. [NDA → LOI → DA Process](#10-nda--loi--da-process)
11. [Earn-out Mechanics 詳解](#11-earn-out-mechanics-詳解)
12. [R&W Insurance & Indemnification](#12-rw-insurance--indemnification)
13. [Mini Cases (Real-world)](#13-mini-cases-real-world)
14. [xlsx 統合 (skill との接続)](#14-xlsx-統合-skill-との接続)
15. [Anti-patterns](#15-anti-patterns)
16. [関連 reference との整合](#16-関連-reference-との整合)

---

## 1. なぜ founder 視点 M&A exit modeling が必須か

### 1.1 スタートアップ exit の構造的事実

Pitchbook / CB Insights の 2020–2024 データを横断的に集計すると、VC-backed startup の exit のうち **M&A が 90% 以上を占め、IPO は 10% を下回る** (年により 5–9%)。SPAC ブーム (2020 Q4–2021) を除外すれば IPO 比率はさらに下がる。Bio / Pharma / Hardware では IPO 比率がやや高くなるが、SaaS / Marketplace / D2C / FinTech では M&A が exit の事実上の唯一経路といってよい。

| Exit pathway | 件数比率 (2020–2024 平均) | 補足 |
|---|---|---|
| Strategic M&A | 65–75% | 既存事業の伸長を求めた事業会社による買収 |
| Financial M&A (PE / Roll-up) | 12–18% | LBO / Roll-up / Carve-out。SaaS で Vista / Thoma Bravo / KKR / Bain Capital が常連 |
| IPO / Direct Listing | 3–9% | SPAC を含めず。market window は 2021 Q4 を境に縮小 |
| Continue private (secondary / tender) | 5–10% | 部分流動化のみ。本書では §2.4 で軽く触れる |
| Wind-down / Acquihire (negligible price) | 5–10% | 投資家リターンは clawback level、founder retention のみ |

> 出典: Pitchbook NVCA Venture Monitor (2020–2024), CB Insights State of Venture Reports, Crunchbase Quarterly Funding Data。年により ±5% の振れ。

つまり、IC memo の "Exit Thesis" を「IPO で 8x revenue multiple」と書くのは大半の deal で **誤り**、もしくは「**起こらなかった場合のテール**」を語っているに等しい。Base case として M&A を据え、IPO は upside scenario として扱うのが標準である。

### 1.2 「Headline price ≠ Founder net」の溝

founder / 既存投資家が直面する最大の認知ギャップは、**プレスリリースに載る「買収額 (headline deal value)」と、founder の銀行口座に入る現金 (after-tax net cash) が大きく乖離する** という事実である。SRS Acquiom の M&A Deal Terms Study (2017–2023 観測) を踏まえると、headline → founder net の縮小は以下の累積で説明される。

| Bridge step | 縮小量 (中央値) | 主因 |
|---|---|---|
| LP preference holders (優先株) | 0–20% | 1x non-participating が標準。下方シナリオで participating preferred や 2x が効く |
| Bridge note / venture debt repayment | 1–5% | growth round で resolve。late-stage では SVB / Hercules / TriplePoint debt が常時 |
| Transaction expenses (banker / legal / DD) | 1.5–4% | sell-side banker 1–2%、legal $1–3M、QoE / commercial DD 別途 |
| Indemnification escrow holdback | 10–20% (12–24 か月凍結) | R&W insurance が普及して圧縮傾向 |
| WC adjustment (estimated → actual) | ±0–2% | normalized working capital が target を下回ると差額が purchase price から控除 |
| Earn-out unfunded (期待値 vs 実現) | 0–30% (max) × (1 − 実現率 35–55%) | empirical realization rate は中央値 50% 前後 |
| Tax (capital gains) | 20–40% | jurisdiction、holding period、QSBS / 適格再編 の有無による |

足し算すると、**headline の 50–70% が「実際に founder の手元に残る現金 + 流動性のある acquirer 株」** というのが多くの deal の現実である。とりわけ early stage で大量の preferred 資金を入れた company は、liquidation preference stack が厚く、**founder 持分が common である限り、headline → founder の縮小は更に大きい**。これを IC memo / cap table waterfall で defensible に表現できなければ、founder の意思決定を誤誘導する。

### 1.3 IC memo の Exit Thesis section に必要な要素

`08_investment_thesis §7` の IC memo template は、"Exit Thesis" section を以下のように構造化することを要求する。本 reference はこの section を埋めるための一次的な根拠ソースである。

| IC memo Exit Thesis 項目 | 本書の対応 § |
|---|---|
| Likely exit pathway (M&A / IPO / continue private) と probability weighting | §2 Exit Pathway Tree |
| Likely buyer shortlist (3–5 個 × buyer type × WTP 推定) | §3 Buyer Type 分析、§9 Strategic Comps |
| Likely consideration mix (cash / stock / earn-out 比率) と timing | §4 Deal Structure |
| Founder net at headline ¥XB と実額の bridge | §6 Founder-Net Analysis |
| Investor MOIC / IRR (base / upside / downside) | §7 Investor Exit IRR |
| Tax wedge assumption (US QSBS / 日本適格再編) と効果 | §5 Tax Structuring |
| Earn-out realization probability (35–55%) と PV 計算 | §11 Earn-out Mechanics |
| Process timeline 想定 (4–6 か月 standard) | §10 NDA → LOI → DA Process |
| Anti-patterns 自己確認 | §15 Anti-patterns |

### 1.4 VC fund exit IRR / DPI 計算には正確な net proceeds が必須

VC fund の LP は、TVPI / DPI / IRR を quarterly で更新し、Cambridge Associates や Burgiss の benchmark と比較する。fund GP が portfolio company の exit を realized 化する際、**headline price ではなく LP に分配可能な distribution (= net proceeds × fund 持分 × management fee / carry 控除後)** が IRR の分子になる。escrow に凍結された 15% は、**release されるまで「未実現」扱い**、earn-out は contingent consideration として discount factor を効かせる。modeling 段階で headline をそのまま distribution と見做せば、fund の DPI は系統的に過大表示され、LP との reporting で齟齬が生じる。

### 1.5 本書の使い方 — 3 つのレンズ

本書の章構成は、以下 3 つのレンズを縦串にして読む設計である。

1. **Founder lens**: §1, §2, §4, §5, §6, §11, §13, §15。自分の手取り、税、earn-out、anti-patterns を理解する。
2. **Investor lens**: §1, §2, §3, §6, §7, §8, §13。MOIC / IRR、liquidation preference の効き方、buyer 選定。
3. **Process / banker lens**: §3, §4, §9, §10, §12。Sell-side banker と work する際に founder / 投資家が抑える論点。

---

## 2. Exit Pathway Tree

### 2.1 4 大 Path の比較

スタートアップの流動性イベントは概ね以下 4 path に分かれる。各 path の典型レンジを示す (実例は §13 で詳述)。

| Path | 期間 (signing 起点) | EV / Revenue typical | Investor MOIC (top quartile) | Founder net % of headline (税後) | Liquidity 形態 | 投資独立性 (post-exit operational control) |
|---|---|---|---|---|---|---|
| **Strategic M&A** (§3.1) | 4–6 か月 | 5–15x (SaaS); 1–4x (D2C); 業態依存 | 3–10x MOIC | 30–60% | Cash + acquirer stock (lock-up) | 失う (acquirer に統合) |
| **Financial M&A (PE)** (§3.2) | 4–6 か月 | 8–12x EBITDA (PE は EBITDA multiple) | 3–5x MOIC | 25–45% (roll-over 控除後) | Cash + roll-over equity | 部分的に失う (PE governance) |
| **IPO / Direct Listing** (§8) | 12–18 か月 (準備含む) | 8–20x revenue | 5–15x MOIC | 50–70% (lock-up 6 か月後 mark-to-market) | 段階的 (lock-up 6 か月 + insider sales) | 維持 (ただし public market governance) |
| **Continue private + secondary** (§2.4) | continuous | n/a | per fund | 部分流動化 (10–30%) | Tender offer / direct secondary | 維持 |

> 注: 「Founder net % of headline」 は 税後 + escrow / earn-out 確率重み付け後の中央値。下位 quartile はさらに低い (acquihire は 10% を切ることがある)。

### 2.2 Path 選択基準 (Decision Tree)

founder / board が「どの path を pursue するか」を判断する際の 4-layer decision tree:

```
1. IPO 適格か？ (financial / regulatory)
   - ARR ≥ $200M (US) / ¥30B (JP) +
   - Growth ≥ 30% YoY +
   - Rule of 40 ≥ 40 +
   - Public market window が open +
   - Audit-grade financials + SOX-readiness
   ├─ YES → 2 へ進む (M&A optionality も保持)
   └─ NO  → M&A or continue private

2. Strategic acquirer の interest があるか？ (banker outreach で確認)
   - 過去 12–18 か月の inbound interest
   - banker が initial outreach で 3+ 社の serious response
   ├─ YES → M&A (auction process) を base case
   └─ NO  → IPO (適格なら) or continue private + secondary

3. Founder / board の preference は？
   - Legacy / mission 重視 → IPO or continue private (operational control 維持)
   - Liquidity 重視 → M&A (即時 cash)
   - Hybrid → Stock-heavy strategic M&A or IPO + secondary

4. Market timing は？
   - Public market: Renaissance IPO Index / VIX / SaaS comps multiple → IPO window 判定
   - Acquirer cash position: 大型 acquirer の M&A budget (公開 statement / share buyback 履歴)
   - 金利環境: 高金利 → PE LBO の hurdle rate 上昇で multiple 圧縮
```

詳細は §8 で再展開する。

### 2.3 Path 横断の hybrid 戦略

実際は単一 path ではなく以下のような hybrid が増えている。

- **Dual track (IPO + M&A)**: banker が S-1 を準備しつつ strategic outreach。IPO roadshow 直前で acquirer が premium 提示すれば switch (ex: 過去の SaaS 多数事例)。
- **Pre-IPO secondary**: IPO 直前に founder + early VC が tender で 5–20% を流動化。Founder の psychological burden を下げ、IPO に commit させる。
- **Crossover round + IPO**: T. Rowe / Fidelity / Coatue の crossover が直前 round に入り、IPO で anchor。

### 2.4 Continue private + Secondary

- **Tender offer (organized secondary)**: 既存 / 新規投資家が common stock を buy。founder + employee の partial liquidation。typical 5–20% 流動化、price は last round の 0.7–1.0x。
- **Direct secondary**: 投資家間の direct sale (e.g., Greylock → Sequoia)。preferred stock の transfer。
- **Continuation fund**: GP が既存 LP exit のために new SPV を組成し portfolio asset を transfer。late-stage で広がる手法。
- **Founder secondary at primary round**: primary round の中で founder が 5–10% を sell。Series B 以降で標準化 (`04a §3.4` で詳述)。

これらは「exit」ではなく「partial liquidity event」だが、IC memo の Exit Thesis では "interim liquidity option" として明記する価値がある。

### 2.5 Path probability weighting (IC memo での提示形)

IC memo に書くべき表現:

> Base case (60%): Strategic M&A in 5–7 yr, EV/Rev 8–12x, Salesforce / Microsoft / Adobe shortlist。
> Upside (20%): IPO in 7 yr, EV/Rev 15–20x, ARR $300M+ achieved。
> Downside (15%): Tuck-in M&A at 3–5x EV/Rev, headline $200M, founder net post-tax $80M。
> Tail (5%): Wind-down / acquihire, investor partial recovery only。

確率の根拠は `09_market_sizing` (TAM / penetration の上限) + `02_saas_metrics` (現状の growth rate) + `05_valuation_wacc` (comps multiple range) で defensible にする。

---

## 3. Buyer Type 分析

### 3.1 Strategic Acquirer (事業会社による戦略買収)

#### 3.1.1 動機

Strategic acquirer の M&A 動機は以下の 5 軸に分解できる:

1. **Revenue synergies (cross-sell, distribution)**: 既存顧客への sale-through、新地理 / 新 vertical への入口
2. **Cost synergies (G&A consolidation, procurement)**: HR / Finance / IT の重複削減、vendor leverage
3. **Talent acquisition / Acqui-hire**: 特定 engineering team / domain expert の獲得 (key engineer 単価で valued されるとほぼ acquihire)
4. **IP / Patent**: defensive moat, 訴訟回避
5. **Market entry / Geographical expansion**: local presence の即時獲得 (organic entry より速い)

複数軸が同時に効くほど buyer の WTP (Willingness To Pay) は上がる。Microsoft → LinkedIn (2016, $26.2B) は data + distribution + cross-sell が同時に効いた典型。Salesforce → Slack (2020, $27.7B) は distribution + product portfolio + Microsoft Teams 対抗の defensive 動機が混合。

#### 3.1.2 WTP 上限の推定

Strategic acquirer の WTP 上限は次式で表現される:

```
WTP_strategic = Standalone_EV
              + PV(Revenue synergies × P(realize)_revenue × time_phase_factor)
              + PV(Cost synergies × P(realize)_cost × time_phase_factor)
              − Integration_cost (one-time + ongoing)
              − Risk_discount (post-close performance variance)
```

academic studies (KPMG / Bain Global M&A Reports 2018–2023) では:

- Revenue synergies の realization rate ≈ 30–50% (中央値 40%)
- Cost synergies の realization rate ≈ 60–80% (中央値 70%)
- Integration cost: 取引額の 5–15%
- Phasing: synergies は year 1: 25%, year 2: 60%, year 3: 100% で立ち上がるのが standard

これを founder 側の bid 評価で使うと、acquirer ごとの WTP 上限を 3–5 個並列推定できる (§9 で table 化)。

#### 3.1.3 特徴

- **Stock 比率が高い**: 自社株を currency にして cash-out なしに買える。Acquirer の P/E が高いほど stock currency は valuable。
- **Earn-out は控えめ**: 大手 strategic ほど earn-out 嫌い (integration の妨げ、accounting complexity)。中堅以下は earn-out 多用。
- **Long-term integration**: 3–5 年で完全統合、founder は通常 1–3 年で離脱。
- **DA negotiation で R&W が厚い**: acquirer 法務が standard form を厚く要求。

#### 3.1.4 業界別 strategic buyer typical pattern

| Vertical | 主要 strategic buyer | 典型 deal pattern |
|---|---|---|
| SaaS (horizontal) | Salesforce, Microsoft, Oracle, Adobe, ServiceNow, SAP | Stock-heavy ($1B+ deal は stock 50%+)、premium 30–50% |
| SaaS (vertical) | Veeva (Bio), Tyler Tech (Gov), Procore (Construction), Toast (F&B) | Cash-heavy、tuck-in 多い |
| FinTech | Visa, Mastercard, JPMorgan, Stripe (acquirer 化), Block, FIS, Fiserv | Mixed、regulatory approval 重い |
| D2C | Amazon, Procter & Gamble, Unilever, Estée Lauder, L'Oréal | Cash-heavy、earn-out 多用 (brand 売上連動) |
| Bio / Pharma | Pfizer, Merck, J&J, Roche, Novartis, AstraZeneca | Milestone-based earn-out が大半 (clinical trial 進捗連動) |
| Hardware / IoT | Apple, Cisco, Samsung, Nvidia | Acquihire 多い、IP 中心 |
| AI / ML Infra | Google, Microsoft, Amazon, Nvidia, Meta | Talent + GPU compute footprint 中心、acquihire 寄り |
| Cyber | Palo Alto Networks, CrowdStrike, Cisco, Microsoft | Stock-heavy、premium 高め (60–80%) |
| Marketplace | Uber, DoorDash, Airbnb, Booking | 横断少ない、地理拡大目的の tuck-in |

### 3.2 Financial (PE) Acquirer

#### 3.2.1 動機

PE buyer の動機は単一: **5–7 年 hold で IRR 20%+** (LP commitment の hurdle rate)。実現経路は:

- **Multiple expansion**: entry multiple 8x → exit 12x など (Vista の Marketo case が好例 — §13 Case 6)
- **Operational improvement**: SaaS の場合 unit economics 改善 (CAC 効率化、price uplift、retention 改善)、cost cutting (R&D / S&M trim)
- **Bolt-on acquisitions (roll-up)**: platform asset に複数 add-on を bolt-on し scale で multiple expansion
- **Leverage**: 3–6x EBITDA debt を入れて equity IRR を上げる

#### 3.2.2 WTP 上限の推定 (LBO model 簡略)

```
PE WTP = Entry_EV that yields 20%+ IRR over 5 yr hold given:
  - Exit_EV = Exit_EBITDA × Exit_multiple (assumption)
  - Debt structure: 50–60% LTV at entry
  - Operational uplift: EBITDA growth 10–15% CAGR
  - Multiple expansion: 0.5–1.5x increase or flat
```

founder / 投資家視点では、PE が strategic より高い price を出すケースは limited (synergies がない分 standalone uplift だけで IRR を達成しないと駄目)。SaaS で revenue ≥ $50M、EBITDA margin ≥ 20%、growth ≥ 30% 程度の condition だと PE と strategic が WTP で拮抗しうる。

#### 3.2.3 特徴

- **Leverage 多用**: 3–6x EBITDA の Term Loan B / unitranche / 2nd lien を入れる。Margin が薄い business は PE deal にならない。
- **Management roll-over**: founder + key exec が 5–25% を rollover equity として再投資。"2nd bite of apple" を約束する形 (§4.6 で詳述)。
- **Aggressive cost cutting**: post-close 12–18 か月で OpEx 15–25% reduction を平気で課す (R&D / S&M / G&A 横断)。
- **Operational playbook**: Vista Equity / Thoma Bravo は標準化された SaaS playbook を持ち、price uplift と churn reduction を systematic に実行。

#### 3.2.4 主要 PE buyer の特徴

| PE | 専門領域 | 標準 hold | 典型 leverage | Operational playbook |
|---|---|---|---|---|
| Vista Equity Partners | SaaS | 5–7 yr | 5–6x EBITDA | Pricing optimization、go-to-market 再構築、bolt-on acquisitions |
| Thoma Bravo | SaaS, Cyber | 4–6 yr | 5–7x EBITDA | Aggressive cost cutting、margin expansion |
| Silver Lake | Tech (large cap) | 3–5 yr | 3–4x EBITDA | Strategic repositioning、carve-out |
| KKR | Diversified | 5–7 yr | 4–6x EBITDA | Diversified playbook |
| Bain Capital | Tech, Consumer | 5–7 yr | 4–6x EBITDA | Operational improvement consultancy |
| Hellman & Friedman | Software, FinTech | 5–7 yr | 4–5x EBITDA | Long-term value creation |
| Insight Partners (PE arm) | SaaS Late-stage | 4–6 yr | 3–5x EBITDA | Onsite operational team |
| Stone Point | Insurance, FinTech | 5–7 yr | 3–5x EBITDA | Sector specialist |

### 3.3 Tuck-in (小規模戦略買収)

- **対象**: 早期 startup (Pre-Seed–Series A 前後)、$10–100M 規模
- **目的**: 機能追加 / talent acquisition / IP 補強 / 地理拡大の小ピース
- **deal structure**: cash 70%+ stock 0–30%、1–2 年 earn-out (revenue or milestone)
- **Founder の処遇**: acquirer に join、key engineering position で 12–24 か月 retention package
- **典型例**: Stripe による多数の tuck-in、Salesforce による Heroku ($212M, 2010)、Twitter による Vine ($30M, 2012, acquihire 寄り)

### 3.4 Acquihire (人材獲得買収)

- **対象**: pre-revenue / 失敗気味 / pivot 失敗の startup
- **目的**: engineering team 獲得 (founder + key engineers の 5–20 名)
- **deal structure**: 投資家には clawback 級の minimal return (元本回収未満が多い)、founder / team に retention package (RSU 4 年 vest が中心)
- **headline 価格は誤解を招く**: PR 発表上は "$50M acquisition" でも、内訳は $10M consideration + $40M retention RSU で実質 acquihire 寄り
- **投資家の損益**: 1x liquidation preference 未達の deal が多く、common holders には distribution ゼロも普通
- **典型例**: Yahoo の Tumblr (initially $1.1B 2013、後日 ほぼ全額 write-down)、Yahoo の度重なる acquihire (Genevieve Bell の言う "acquihire spiral")
- **見分け方**: deal 発表時の "purchase price allocation" で goodwill ではなく "compensation expense" 比率が高ければ acquihire 寄り。

### 3.5 業界別 buyer typical pattern (consolidator map)

スタートアップの業界別に「常連 acquirer」を把握しておくと、§9 の WTP 推定で買い手 shortlist が defensible になる。

| Vertical | Strategic consolidator | PE consolidator |
|---|---|---|
| SaaS | Salesforce, Microsoft, Oracle, Adobe, ServiceNow, SAP, Workday | Vista, Thoma Bravo, Insight, Hellman & Friedman |
| FinTech | Visa, Mastercard, FIS, Fiserv, Stripe, Block, JPM | TPG, Stone Point, Warburg Pincus |
| D2C / Consumer | Amazon, Unilever, P&G, L'Oréal, Estée Lauder, Nestlé | L Catterton, Berkshire Partners |
| Bio / Pharma | Pfizer, Merck, J&J, Roche, Novartis, AstraZeneca, Gilead, Bristol Myers | Avista Capital, Gilde Healthcare |
| Hardware / IoT | Apple, Cisco, Samsung, Nvidia, Bosch | Carlyle, KKR |
| AI / ML | Google, Microsoft, Amazon, Nvidia, Meta, Apple | Silver Lake, Vista (AI-adjacent) |
| Cyber | Palo Alto, CrowdStrike, Cisco, Microsoft, Fortinet | Thoma Bravo (cyber playbook 強) |
| Marketplace | Uber, DoorDash, Airbnb, Booking, Expedia | Apollo, Silver Lake |
| Logistics / SCM | C.H. Robinson, Maersk, FedEx, UPS, DSV | Apollo, KKR |
| EdTech | Pearson, McGraw Hill, Cengage, Chegg | KKR, Vista |
| HealthTech | UnitedHealth (Optum), CVS Health, Walgreens, Cigna | TPG, Bain Capital |

> 出典: 各社 IR 開示、Pitchbook M&A Database (2018–2024)。日本では Mercari、楽天、リクルート、SMBC グループ、KDDI、NTT グループが横断 acquirer。

---

## 4. Deal Structure — Consideration Mix

Consideration mix (買収対価の内訳) は founder net と investor IRR の決定要因として最も大きく効く。実務では以下の 6 形態を組み合わせて構成される。

### 4.1 Cash 100%

#### 4.1.1 Pros (founder)

- **確実性最大**: closing 時点で headline = real cash value (escrow 除く)。
- **税務シンプル**: capital gains を closing 年に realize、計算明瞭。
- **投資独立**: acquirer 株の volatility を背負わない。
- **Liquidity 即時**: lock-up なし (escrow 部分以外)。

#### 4.1.2 Cons (founder)

- **Tax 即時発生**: capital gains を closing 年に full payment。Stock-for-stock の繰延べ benefit を放棄。
- **Acquirer 株値上りの upside 喪失**: post-close で acquirer が 50% 上がっても founder は享受できない。
- **Reinvestment risk**: cash を新たに投資するときの tax-inefficient な選択 (treasury / index fund 等で再投資すると再度 long-term capital gains)。

#### 4.1.3 典型 pattern

- 小規模 / 中堅 deal ($10–500M)
- PE buyer による LBO (PE は cash-out が standard)
- Acquirer の stock currency が魅力的でないとき (低 P/E / 流動性不足)
- D2C / FMCG (P&G, Unilever 等) は cash-heavy
- 例: LinkedIn → Microsoft (2016, $26.2B all-cash)

### 4.2 Stock 100%

#### 4.2.1 Pros (founder)

- **Tax-free reorganization 可能** (qualifying な場合): capital gains を rollover、acquirer 株の cost basis に carry over。
- **Acquirer 上昇 upside の享受**: post-close で acquirer が rally すれば founder も享受。
- **Dilution なしの merger**: acquirer cash を温存。

#### 4.2.2 Cons (founder)

- **Lock-up 中 acquirer 下落 risk**: 6–12 か月 lock-up 中に acquirer が drop すれば founder net も同じだけ下がる。
- **Conversion ratio fluctuation**: signing と closing の間で acquirer 株が動くと founder の effective consideration が変動 (fixed exchange ratio vs floating exchange ratio で扱いが違う)。
- **Liquidity 制限**: lock-up + insider trading 規制 (10b5-1 plan が必要)。

#### 4.2.3 Tax-free reorganization 要件 (US: IRS Section 368)

| Type | 形態 | 主要要件 |
|---|---|---|
| **Type A** | Statutory merger / consolidation | 州法に基づく法定 merger。少なくとも 40% を acquirer 株で支払う必要 (continuity of interest test)。Boot (cash) は taxable。 |
| **Type B** | Stock-for-stock | Solely voting stock で 80%+ を取得。Boot は permitted されない (含めると entire deal が taxable に転落)。 |
| **Type C** | Stock-for-assets | Solely voting stock で substantially all assets を取得。Boot は 20% まで許容。 |
| **Type D** | Acquisitive D | Target's shareholders が acquirer corp を control する形態 (small で大手を買う divisive D / acquisitive D)。 |

Founder 側の tax 効果: 受領した acquirer 株の cost basis = 譲渡した target stock の adjusted basis。**売却するまで gain は realize しない (繰延べ)**。

#### 4.2.4 Tax-free reorganization 要件 (日本: 法人税法 第2条第12号の17 / 第62条の9)

日本では「**適格株式交換 / 適格株式移転**」として規定されている (法人税法 第2条第12号の17 で適格株式交換を定義、第62条の9 で課税の特例を規定)。主要要件:

| 区分 | 要件 |
|---|---|
| **完全支配関係グループ内** | 株式交換前後 100% 完全支配関係 |
| **支配関係グループ内** (50%超) | (i) 対価が完全親法人株式のみ + (ii) 株式交換後も支配関係継続 + (iii) 主要事業が引き続き営まれる + (iv) 従業員 80%+ が引き続き雇用 + (v) 主要資産・負債が完全子法人で引き続き保有 |
| **共同事業要件** (グループ外との交換) | 上記 + 事業関連性 + 規模要件 (5 倍以内) or 経営参画要件 + 株式継続保有要件 (個人株主 80%+) |

Founder 側の効果: 株式譲渡損益が**繰延べ** (法人税法第61条の2第10項 / 所得税法第57条の4)、acquirer 株の取得価額 = 旧株の取得価額。**繰延べた損益は acquirer 株を売却した時に realize**。

> Cross-reference: より詳細な実務処理 (連結処理、簿価引継ぎ、個別株主 vs 法人株主) は `13a_consolidation_core §4` および `12_tax_strategy §4` を参照。本書は founder lens で「適格 vs 非適格で何が変わるか」に絞る。

#### 4.2.5 典型 pattern

- 大型 public-to-public deal
- Acquirer の stock currency が魅力的 (high P/E、流動性十分、業績 stable)
- Founder の long-term commitment を求める deal (post-close での integration commitment)
- 例: Slack → Salesforce (2020, $27.7B、stock 中心 + cash 部分 — §13 Case 1)

### 4.3 Cash + Stock Mix (50/50, 70/30 等)

#### 4.3.1 Pros

- **Tax と upside の bridge**: cash 部分で immediate liquidity、stock 部分で upside 享受。
- **Acquirer cash 制約 + founder の commitment 両立**: acquirer の cash 流出を抑えつつ founder を retention。
- **負担分散**: founder 全員が同一比率である必要はなく、founder の preference に応じて individual structure 可能。

#### 4.3.2 Cons

- **Complex tax treatment**: "Boot rule" (Section 368(a)(1) の文脈) — 受領した cash 部分は taxable、stock 部分は tax-free。Cost basis allocation が複雑。

#### 4.3.3 Boot Rule (US) の数値例

- 受領: $100 cash + $400 acquirer stock (合計 $500)
- 譲渡 target stock の adjusted basis: $50
- Realized gain: $500 − $50 = $450
- Recognized gain (boot rule): min($100, $450) = $100 が taxable
- 残り $350 gain は acquirer 株 cost basis に carry over (i.e., acquirer 株 cost basis = $400 − $350 = $50)

#### 4.3.4 典型 pattern

- 中堅〜大型 deal の majority pattern
- 例: WhatsApp → Facebook (2014, $19B; cash $4B + stock $12B + RSU $3B — §13 Case 2)

### 4.4 Earn-out (Contingent Consideration)

#### 4.4.1 概要

Earn-out は **post-close で合意条件を満たした場合に追加支払いされる contingent consideration**。Acquirer-founder 間の valuation gap (founder が believe する future growth と acquirer の skeptical assumption の溝) を bridge する手段。

#### 4.4.2 Trigger metric

| Metric | 利点 | 欠点 |
|---|---|---|
| **Revenue (ARR / MRR)** | 客観的、game しにくい | top-line に focus されると acquirer の cost discipline が崩れる |
| **EBITDA / Operating income** | profitability も縛れる | cost allocation 紛争が発生 (acquirer が integration cost を target に押し付ける) |
| **Customer KPI** (logos, retention, NRR) | 戦略意図と整合 | gameable (key customer の retention only に集中) |
| **Product milestone** (launch, regulatory approval) | binary, clear | scope 紛争 (何を以て "launch" とするか) |
| **Bookings / Pipeline** | leading indicator | 先延ばし可能、reverse engineering されやすい |

#### 4.4.3 Cap (上限金額)

実務では total deal value の **10–30% が earn-out**。残り 70–90% は upfront (cash + stock + escrow)。Earn-out が 50%+ の deal は founder にとって highly risky で、原則避けるべき。

#### 4.4.4 期間

- 1 年: 不安定で gameable、避ける
- 2 年: standard
- 3 年: 大型 deal で見られる、買収側が integration を急がない場合
- 4 年+: vesting RSU 形式に近づく (§4.5 reverse vesting と境界が曖昧)

#### 4.4.5 Realization rate (empirical)

- **SRS Acquiom 2017–2023 study**: earn-out 含む deal の中央値で **earn-out の 50% が支払われる** (full realization は 35% 程度)。
- **Bain & Company 2018–2022 M&A Reports**: 30%+ の earn-out で litigation または formal dispute が発生。
- **Boston Consulting Group**: 業界別に realization rate が異なる。Bio / Pharma の milestone-based earn-out は trigger 達成 / 不達成が binary な分、平均 25% (技術的成功確率と相関)。SaaS の revenue-based は中央値 60%。

> 結論: founder / 投資家が earn-out を modeling する際、**100% 実現を前提にしてはいけない**。Empirical 中央値 35–55% を probability として discount し、PV 計算に反映する (§11.4 で計算式)。

#### 4.4.6 Pitfalls

- **KPI gameable**: revenue earn-out なら期末で discount 投げ売り、EBITDA earn-out なら R&D 削減で短期 boost。
- **Buyer 側の operational control**: post-close で acquirer が headcount / marketing / pricing を縛れば KPI 達成は困難。
- **Common cause vs interpretation dispute**: 経済環境変動 (景気後退、為替) で KPI 未達 → どちらに帰責?
- **Litigation の頻度**: 30%+ の earn-out が紛争化 (Bain study)。

#### 4.4.7 Best practice (founder protection)

1. **Simple objective metric**: Revenue (ARR or recognized revenue) one metric only。EBITDA / multi-metric は避ける。
2. **Founder operational autonomy 期間**: 12–18 か月、acquirer は budget / headcount / pricing を一方的に変更しない (DA schedule に明記)。
3. **Earn-out plan を DA schedule に明記**: 計算式、accounting policy、dispute resolution mechanism (third-party arbitrator) を全文書面化。
4. **Acceleration triggers**: founder termination without cause / acquirer breach / business sale 時に earn-out が full pay。
5. **Reporting transparency**: monthly KPI report 義務、independent auditor right。

### 4.5 Reverse Vesting (Founder Retention 用)

#### 4.5.1 概要

Acquirer が founder の post-close commitment を確保するために、既存 founder 株式の一部 (10–50%) を **acquirer 側で再 vest**。離脱したら forfeiture。Earn-out との違いは "performance 連動ではなく service 連動" (時間で vest)。

#### 4.5.2 標準 schedule

- 12–24 か月 cliff、その後 24–36 か月 monthly vest
- 合計期間 4 年 (acquirer の standard new-hire grant と整合)

#### 4.5.3 Double trigger acceleration

- Single trigger: termination without cause → 即 vest
- Double trigger: (acquisition + termination without cause) または (acquisition + good reason resignation) → 即 vest

実務では double trigger が主流 (acquirer が retention のために強制 vesting を避ける)。

#### 4.5.4 Tax 取り扱い

- **US**: Section 83(b) election をしないと、vesting 時点で FMV と purchase price の差額が ordinary income。多くの founder は 83(b) を打って (signing 時に基底 FMV で taxable に固定) future appreciation を capital gains にする。
- **日本**: 個人の譲渡所得 (上場株式は 20.315%)。reverse vesting で再 vesting されるたびに譲渡所得課税ではなく給与所得課税に転じる場合がある (個別判定)。

### 4.6 Roll-over Equity (PE deal)

#### 4.6.1 概要

PE buyer が management roll-over を要求するパターン。Founder + key exec が deal proceed の一部を **新 HoldCo (PE-controlled) 株式に再投資** し、5–25% を保持。"2nd bite of apple" — PE の exit (typically 5–7 yr 後) で再度 founder return を享受。

#### 4.6.2 構造例

- Pre-deal: Target Co、founder 30% / VC 60% / employee pool 10%
- Deal: PE が $500M で Target Co を取得 (LBO with $300M debt + $200M PE equity)
- Roll-over: founder の deal proceed $150M のうち $50M (33%) を新 HoldCo equity に再投資 (rest $100M は cash + tax)
- Post-deal: NewCo、PE 75% / founder 20% / management options pool 5%
- Exit (5 yr 後): NewCo $1.5B、founder 20% × $1.5B (leverage 控除後) = $200M

#### 4.6.3 Tax: Section 351 contribution

US では founder の roll-over equity 部分は **Section 351 で tax-free contribution** にできる (founder + PE の合計が NewCo control を構成すれば)。Section 368 と並んで founder の tax 繰延べ手段。

#### 4.6.4 留意点

- **PE governance**: board control を失う、operational autonomy 制限。
- **Aggressive cost cutting**: PE の標準 playbook に founder が抵抗すると friction。
- **Exit timing**: PE が 5 yr で exit しない場合 founder の liquidity がさらに先送り。
- **Drag-along / Tag-along**: PE は drag-along を多用、founder は tag-along で minority protection。

### 4.7 Consideration mix の比較 summary

| Mix | Founder net 期待値 (税後) | Risk | Typical use |
|---|---|---|---|
| Cash 100% | Headline × (1 − tax_rate) | Low (escrow のみ) | PE deal, mid-size strategic |
| Stock 100% | Headline × (1 − stock_volatility × lock-up) − tax (繰延べ) | Med (acquirer 株 risk) | Large public-to-public |
| 50/50 mix | Hybrid | Med | Majority pattern (大半の deal) |
| Cash + earn-out (70/30) | Cash 部分 (1 − tax) + earn-out × P(realize) × discount | High | 中堅 strategic, PE, valuation gap bridge |
| Cash + roll-over | Cash 部分 (1 − tax) + roll-over equity (NewCo PV) | Med-High | PE LBO |
| Acquihire (cash + retention RSU) | Cash 小 + RSU vesting × continued employment | High (attrition risk) | Failed startup |

---

## 5. Tax Structuring

> 本 § は **founder lens の使用ガイド**。詳細な税務処理 (実効税率の計算式、源泉徴収手続き、cross-border の anti-abuse rules、適格組織再編の正確な要件 step) は `12_tax_strategy §3-5` を参照する。本書は exit deal structure と tax の関係を理解するための要点に絞る。

### 5.1 米国 (Delaware C-corp founder)

#### 5.1.1 QSBS (Qualified Small Business Stock) — Section 1202

QSBS は US 創業者の M&A exit における最大の tax 武器。**発行時の会社が C-corp で gross assets ≤ $50M ($75M post-OBBBA)、5 年保有、active business test を満たす** stock の譲渡益を一定額まで federal tax から除外する。

**重要: 2025 年 7 月 4 日 (OBBBA = One Big Beautiful Bill Act) で大幅改訂された。Stock の発行日で適用ルールが分岐する。**

| 発行日 | Asset 上限 | Per-issuer 控除上限 | Holding period | Exclusion 率 | 適用税率 (除外外部分) |
|---|---|---|---|---|---|
| **2025-07-04 以前** (Legacy) | $50M (issuance 時点) | $10M または adjusted basis × 10x のいずれか大 | 5 年 (固定) | 100% (post-2010 取得) | 残部分 N/A (full exclusion) |
| **2025-07-04 以降** (Post-OBBBA) | $75M (issuance 時点、2027 から CPI 連動) | $15M または adjusted basis × 10x のいずれか大、2027 から CPI 連動 | 3 年 / 4 年 / 5 年 (tiered) | 50% / 75% / 100% | 3-4 yr の non-excluded 部分は 28% (preferential 15/20% を適用しない) |

> 出典: IRS Section 1202 (改正前)、One Big Beautiful Bill Act (2025-07-04 enacted)、The Tax Adviser (AICPA) "QSBS gets a makeover" (2025-11)、Mintz "QSBS Benefits Expanded Under OBBBA" (2025-07-09)。

##### 適格要件 (両 regime 共通)

1. **Domestic C-corp** (S-corp / LLC / partnership は NG)
2. **Issuance 時点で gross assets ≤ 上限** ($50M / $75M)
3. **Original issuance**: founder / VC / employee が会社から **直接** 取得した stock (secondary purchase は NG)
4. **Active business test**: assets の 80%+ を qualified active business で使用 (財務 / hospitality / banking / real estate は disqualified)
5. **Holding period**: 5 年 (legacy) / 3-4-5 yr tiered (post-OBBBA)

##### 例: Founder の 5B exit

- US founder (legacy QSBS, 5+ year hold, exit 2025-06): $50M sale → cost basis $1K → realized gain $49.99M → exclusion = min($10M, $1K × 10) = $10M → taxable gain $39.99M → effective tax (federal LTCG 20% + NIIT 3.8% + state CA 13.3%) ≈ $14.8M → after-tax $35.2M (retention 70.4%)。複数 stockholders がいれば各人 $10M 控除可。
- US founder (post-OBBBA, stock issued 2025-08, 5+ year hold, exit 2030+): per-issuer $15M cap → $50M sale, basis $1K → exclusion $15M → taxable $35M → effective tax ≈ $13M → after-tax $37M (74%)。
- US founder (post-OBBBA, 3 year hold, exit 2028): 50% exclusion → taxable $25M → 28% rate → $7M tax → after-tax $43M (86%)、ただし 3-yr early exit は通常 strategic urgency があるケース。

##### 重要な tactical points

- **Stock issued ≤ 2025-07-04**: legacy rule のまま。例外なく 5 yr hold を要求、$10M cap、ただし 100% exclusion。
- **Stock issued ≥ 2025-07-05**: tiered + $15M cap。早期 exit 可能になったが residual 28% が痛い。
- **Mixed lot (2025-07 を跨ぐ)**: lot ごとに rule 適用、accounting で lot tracking が必要。
- **Spousal exemption**: married filing jointly でも単一 stockholder 扱い (cap doubling は不可、ただし gift to non-spouse family で stockholder 数を増やすことは合法 — 1202(h) gift transfer rule)。
- **State conformity**: California は QSBS exclusion を認めない (state tax full)。Texas / Florida / Washington は no state income tax で QSBS 効果最大。
- **Section 1045 rollover**: 5 yr 未満で sell する場合、proceeds を 60 日以内に別 QSBS に再投資すれば holding period を carry over。

#### 5.1.2 Tax-free Reorganization (Section 368)

§4.2.3 で deal type を整理した。Founder 視点で重要な点:

- **Type A merger**: minimum 40% acquirer stock requirement。Boot (cash) は taxable。M&A の majority pattern。
- **Type B (B reorganization)**: 100% voting stock。Boot 一切不可。**Boot 含めると entire deal が taxable に転落** (catastrophic risk)。
- **Type C**: stock-for-assets。Boot 20% まで OK。

##### Reverse triangular merger

実務で最も多用される M&A 形態。Acquirer が Merger Sub (delaware shell) を組成し、target に merge。Sub が消滅、target が surviving entity に。Acquirer が target shareholders に stock + cash を交付。Type A 要件を満たせば tax-free 部分 + boot taxable。

#### 5.1.3 Section 351 Contribution (PE roll-over)

Founder が roll-over equity に再投資する PE deal で活用。Founder + PE が NewCo を組成し、founder が target stock + cash を NewCo に拠出 (control 80%+ を満たす場合 tax-free)。Roll-over 部分は basis 引継ぎ、cash 取得部分は boot で taxable。

#### 5.1.4 State Tax

| 州 | Capital gains tax (top bracket) | M&A への影響 |
|---|---|---|
| Delaware | 6.6% | 標準 |
| California | 13.3% | 高い、QSBS exclusion 認めず |
| New York | 10.9% | 高い、QSBS は federal だけ |
| Texas | 0% | Founder 移住で大型節税 |
| Washington | 7% (2022 から導入) | 移住前に確認 |
| Florida | 0% | Founder 移住で節税 |
| Wyoming | 0% | LLC で migrate するケース |

> 注意: 移住は exit の 2-3 年前から planning しないと "California exit tax" や "183-day rule" で disputed になる。

### 5.2 日本 (株式会社 founder)

#### 5.2.1 適格株式交換 (法人税法 第2条第12号の17 / 第62条の9)

§4.2.4 で要件を整理した。Founder 視点での実務:

- **個人株主 (founder personal)**: 株式譲渡損益が**繰延べ**される (所得税法 第57条の4)。Acquirer 株の取得価額 = 旧株の取得価額 + 適格判定後の調整。Acquirer 株を将来 sell した時に realize。
- **法人株主 (founder の SPC / 投資家 LP)**: 法人税法 第61条の2第10項。Acquirer 株の帳簿価額を旧株式と同額で計上。

##### 適格要件 (グループ外との交換 — 共同事業要件)

1. 完全親法人と完全子法人が共同で事業を営む
2. 事業関連性
3. 規模要件 (5 倍以内) または経営参画要件
4. 株式継続保有要件 — 個人株主 80%+ が支配関係期間中継続保有
5. 主要事業継続要件
6. 従業員引継ぎ 80%+
7. 対価が完全親法人株式のみ (金銭等不可)

> 出典: 法人税法 第2条第12号の17 (定義)、第62条の9 (課税の特例)、所得税法 第57条の4 (個人株主の繰延べ)。

#### 5.2.2 譲渡所得税 (founder が個人で sell する場合)

| 区分 | 税率 (合計) | 内訳 |
|---|---|---|
| **上場株式・公募株式** | **20.315%** | 所得税 15% + 復興特別所得税 0.315% + 住民税 5% |
| **非上場株式** | **20.315%** | 同上、申告分離課税 |
| **総合課税の譲渡所得** (一定要件) | 累進 | rare、適用要件厳しい |

> M&A exit における founder の譲渡益は基本的に 20.315% フラット。

#### 5.2.3 創業者間贈与 (親族で持分移動時)

Pre-exit に founder 持分を spouse / 子に贈与する場合、**贈与税** が発生する (累進 10–55%)。Exit 直前の駆け込み贈与は税務リスクが高く、**3-5 年前から計画的に分散** する pattern が standard。事業承継税制 (相続税 / 贈与税の納税猶予) も検討対象。

#### 5.2.4 エンジェル税制 (投資家 incentive)

Founder ではなく **投資家** 側の制度だが、cap table の理解に必要。

- **Type A**: 寄附金控除類似 (総所得から控除)
- **Type B**: 株式譲渡損益から控除
- Exit 時の譲渡所得計算では、エンジェル税制で受けた控除分が basis 調整される

#### 5.2.5 ストックオプション税制

- **税制適格 SO**: 行使時に課税なし、譲渡時に譲渡所得 20.315%
- **税制非適格 SO**: 行使時に給与所得 (累進、最大 55%)、譲渡時に譲渡所得 20.315%
- M&A exit では SO は通常 acquirer 株 / cash で買収される (cash-out が標準)。買収 cash は **行使益 + 譲渡益** に分解、税務処理が分岐 (詳細は `07_japan_specifics §6` 参照)。

### 5.3 Cross-border (US-JP)

#### 5.3.1 日米租税条約 (Tax Treaty)

| 所得種類 | 源泉地国課税 (default) | Treaty rate |
|---|---|---|
| Dividends (一般) | 30% | 10% |
| Dividends (持分 10%+) | 30% | 5% |
| Interest | 30% | 0–10% |
| Royalties | 30% | 0% |
| **株式譲渡益** | 通常 source country で非課税 (residence country で課税) | source country で原則 0%、ただし real estate-rich entity は例外 |

> 出典: 日米租税条約 (2003 改定、2019 議定書)。実務では IRS Form W-8BEN / 8233、日本側は租税条約届出書を提出。

#### 5.3.2 PE (Permanent Establishment) Risk

US founder が日本 startup に経営参画している場合、日本国内に PE を構成すると認定されると、日本側課税が発生する可能性。**遠隔リモート業務だけなら通常 PE 構成しない** が、長期出張・営業拠点・倉庫があると要注意。

#### 5.3.3 Inversion / Migration

- **Pre-IPO migration**: US-listed shell parent (Delaware) + JP subsidiary は典型 structure。Founder の effective tax は jurisdiction によって変わる。
- **Founder migration**: US founder が exit 直前に Puerto Rico や Singapore に移住する pattern (Act 60 / Singapore tax incentives)。移住タイミングと residency 認定を厳格に検討、anti-abuse rule に抵触しないこと。

### 5.4 Tax Wedge mini case (Headline ¥6B → 税後)

| Founder 属性 | Headline | LP / debt 控除後 cash | Tax | After-tax | 実効 retention |
|---|---|---|---|---|---|
| **US founder, QSBS legacy ($10M cap × 5 holders), 5+ yr hold, Florida resident** | $50M | $50M | $0 federal + $0 state (Florida) = $0 | $50M | **100%** |
| **US founder, QSBS post-OBBBA ($15M cap, single holder), 5+ yr hold, CA resident** | $50M | $50M | (50−15) × (20% + 13.3%) = $11.7M | $38.3M | 76.6% |
| **US founder, NON-QSBS, 5+ yr hold, CA resident** | $50M | $50M | $50M × (20% + 13.3% + 3.8% NIIT) = $18.55M | $31.45M | 62.9% |
| **日本 founder, 適格組織再編なし, 上場株式譲渡** | ¥6B | ¥6B | ¥6B × 20.315% = ¥1.22B | ¥4.78B | **79.7%** |
| **日本 founder, 適格株式交換 (繰延べ)** | ¥6B | acquirer 株 ¥6B 受領 | ¥0 (繰延べ) | acquirer 株 ¥6B (含み益繰延) | **100% nominal** (将来売却時に課税) |
| **日本 founder, 非適格株式交換** | ¥6B | ¥6B | ¥6B × 20.315% = ¥1.22B + みなし配当課税 risk | ¥4.78B 以下 | < 79.7% |

> 観察: jurisdiction × QSBS 適用 × 適格再編 で **62%–100%** の retention レンジ。**flat 20% 仮定で modeling するのは不適切** (anti-pattern §15.4)。

---

## 6. Founder-Net Analysis (Headline → Real Proceeds)

### 6.1 Bridge Components — 全 step 図

§1.2 で大枠を示した。本 § で各 step を計算式に落とす。

```
Step 0: Headline Deal Value (HDV)
        ↓
Step 1: − LP holders preferred (per liquidation preference stack)
        ↓
Step 2: − Bridge note / venture debt repayment
        ↓
Step 3: − Transaction expenses (banker fee 1-2% / legal $1-3M / DD)
        ↓
Step 4: ⇒ Cash pool available to common holders
        ↓
Step 5: × Founder pro-rata share of common
        ↓
Step 6: − Indemnification escrow (10-20% × 12-24 mo holdback)
        ↓
Step 7: − WC adjustment (estimated → actual)
        ↓
Step 8: ⇒ Closing cash + stock to founder
        ↓
Step 9: − Tax (capital gains × jurisdiction × QSBS / 適格 status)
        ↓
Step 10: ⇒ Founder closing after-tax proceeds
        ↓
Step 11: + Earn-out realized × probability × discount factor
        ↓
Step 12: + Escrow released × probability × discount factor
        ↓
Step 13: + Stock appreciation during lock-up (mark-to-market or implied)
        ↓
Step 14: ⇒ Total founder economics (5-7 yr horizon, post-exit)
```

### 6.2 Liquidation Preference の影響 (extends from `04b §6`)

`04b_cap_table_mechanics §6` で扱った liquidation waterfall を、**税後 founder net** に延長するのが本書の役割。要点を再掲:

#### 6.2.1 Standard cases

- **1x non-participating**: preferred holder は max(1x preference, as-converted common) を取る。標準。
- **1x participating**: preferred holder は 1x preference + as-converted common を両方取る (double-dip)。Down-round や late-stage で稀に。
- **1x participating with cap (3x cap など)**: cap までは double-dip、cap 到達後は as-converted。
- **2x non-participating**: down-round 後の new money で見られる。Founder への dilution が厚い。
- **Multiple-class waterfall**: Series A / B / C で異なる terms が stack。Latest → earliest の順 (typical seniority) で payout。

#### 6.2.2 Down-side scenario の影響 (cliff effect)

低 exit value で **founder net = 0** になる "cliff"。例:

| Exit value | LP stack ($50M, 1x non-part) | Founder net (10% common) |
|---|---|---|
| $40M | $40M (preferred) | $0 |
| $50M | $50M (preferred) | $0 (break-even) |
| $60M | $50M + $10M as-converted ($1M to common after pref) | $1M × 10% = $100K |
| $100M | $50M + $50M as-converted (45% to common) | $4.5M |
| $200M | $50M + $150M as-converted (75% to common) | $15M |

> Founder の break-even は LP stack の天井。Down-round や bridge を増やすほど break-even が高くなり、founder の "wipe-out" risk が増す。

#### 6.2.3 Participation cap の特殊解

Series B が 1x participating with 3x cap、Series A が 1x non-participating の場合、exit value に応じて Series B が participating mode と non-participating mode を switch する。breakeven 計算は as-converted threshold で行う:

```
Threshold = 3 × Series B preference / (Series B as-converted % of total)
```

Threshold を超えたら Series B holder は as-converted を選んで participation を放棄するのが rational。

### 6.3 Founder-Net Calculator (Python 実装)

以下は本 reference の中核となる計算 function。`scripts/build_model.py` から呼び出される想定。

```python
from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class LiquidationClass:
    """1 つの preferred class (Series A / B / C 等) の terms."""
    name: str
    shares: int
    invested: float           # 出資総額
    pref_multiplier: float    # 1.0 (standard), 2.0 (down-round)
    pref_type: Literal["non_participating", "participating", "participating_capped"]
    cap_multiplier: float = 0.0  # participating_capped のみ
    seniority: int = 0        # 0 = senior, 大きいほど junior


@dataclass
class TaxParams:
    jurisdiction: Literal["US_QSBS_legacy", "US_QSBS_post_obbba",
                          "US_NonQSBS", "JP_Standard", "JP_Reorg_Qualified"]
    federal_ltcg_rate: float = 0.20   # US LTCG top bracket
    niit_rate: float = 0.038          # US Net Investment Income Tax
    state_rate: float = 0.0           # State, default 0
    qsbs_cap: float = 10_000_000      # legacy default
    qsbs_basis: float = 0             # founder の cost basis
    qsbs_exclusion_pct: float = 1.0   # 100% (legacy 5+yr) / 0.5 / 0.75
    jp_rate: float = 0.20315


def waterfall_payout(
    headline_deal_value: float,
    classes: list[LiquidationClass],
    common_shares: int,
) -> dict:
    """Liquidation preference waterfall を計算し、各 class の payout を返す.
    
    classes は seniority 順 (senior が先) で渡される前提.
    Returns: {'preferred_payouts': {class_name: amount}, 'common_pool': amount}
    """
    remaining = headline_deal_value
    preferred_payouts = {}
    
    # Sort by seniority (smaller = more senior)
    sorted_classes = sorted(classes, key=lambda c: c.seniority)
    
    # Step 1: preferred 全額の min(pref, as-converted) を seniority 順で
    # まず "all non-participating" 仮定で as-converted distribution を試算
    as_converted_pool = headline_deal_value
    total_shares_for_as_conv = common_shares + sum(c.shares for c in sorted_classes)
    as_converted_per_share = (
        as_converted_pool / total_shares_for_as_conv if total_shares_for_as_conv > 0 else 0
    )
    
    # Step 2: 各 preferred class が pref vs as-converted のうち高い方を選ぶ
    # (non-participating)、participating は両方取る
    for cls in sorted_classes:
        pref_amount = cls.invested * cls.pref_multiplier
        as_conv_amount = cls.shares * as_converted_per_share
        
        if cls.pref_type == "non_participating":
            payout = max(pref_amount, as_conv_amount)
            # ただし remaining より大きい場合は remaining cap
            payout = min(payout, remaining)
        elif cls.pref_type == "participating":
            # First take pref, then participate in residual as common
            payout_pref = min(pref_amount, remaining)
            # 残額からの common participation は後段で計算
            payout = payout_pref  # 暫定。participation 部分は次 loop で再計算が必要
        elif cls.pref_type == "participating_capped":
            cap_amount = cls.invested * cls.cap_multiplier
            payout_pref = min(pref_amount, remaining)
            # cap 超過判定は as_converted との比較で
            if as_conv_amount >= cap_amount:
                payout = min(as_conv_amount, remaining)  # convert to common
            else:
                payout = payout_pref
        
        preferred_payouts[cls.name] = payout
        remaining -= payout
    
    # Step 3: 残額が common pool
    common_pool = max(0.0, remaining)
    
    # Step 4: participating preferred の participation 部分を common と合算分配
    participating_classes = [c for c in sorted_classes if c.pref_type == "participating"]
    if participating_classes and common_pool > 0:
        participating_shares = sum(c.shares for c in participating_classes)
        total_participating_shares = common_shares + participating_shares
        per_share = common_pool / total_participating_shares
        for cls in participating_classes:
            extra = cls.shares * per_share
            preferred_payouts[cls.name] += extra
        common_pool = common_shares * per_share
    
    return {
        "preferred_payouts": preferred_payouts,
        "common_pool": common_pool,
    }


def apply_tax(
    pre_tax_proceeds: float,
    tax_params: TaxParams,
    holding_years: float = 5.0,
) -> dict:
    """Apply jurisdiction-specific tax. Returns {'tax_owed', 'after_tax'}."""
    j = tax_params.jurisdiction
    p = tax_params
    
    if j == "US_QSBS_legacy":
        # 100% exclusion up to cap if 5+ yr hold
        if holding_years >= 5.0:
            excludable = min(p.qsbs_cap, max(p.qsbs_basis * 10, p.qsbs_cap))
            taxable = max(0.0, pre_tax_proceeds - excludable)
            tax = taxable * (p.federal_ltcg_rate + p.niit_rate + p.state_rate)
        else:
            # Use Section 1045 rollover or full LTCG
            tax = pre_tax_proceeds * (p.federal_ltcg_rate + p.niit_rate + p.state_rate)
    
    elif j == "US_QSBS_post_obbba":
        # Tiered exclusion based on holding years
        if holding_years >= 5.0:
            exclusion_pct = 1.00
        elif holding_years >= 4.0:
            exclusion_pct = 0.75
        elif holding_years >= 3.0:
            exclusion_pct = 0.50
        else:
            exclusion_pct = 0.0
        
        cap = max(15_000_000, p.qsbs_basis * 10)
        eligible_for_exclusion = min(pre_tax_proceeds, cap)
        excluded = eligible_for_exclusion * exclusion_pct
        # 残部分の税率: 5 yr で 0% (full excl)、3-4 yr で 28% rate on non-excluded portion
        residual_taxable = pre_tax_proceeds - excluded
        if holding_years >= 5.0:
            residual_rate = p.federal_ltcg_rate + p.niit_rate + p.state_rate
        else:
            residual_rate = 0.28 + p.niit_rate + p.state_rate  # 28% for 3-4 yr
        tax = residual_taxable * residual_rate
    
    elif j == "US_NonQSBS":
        tax = pre_tax_proceeds * (p.federal_ltcg_rate + p.niit_rate + p.state_rate)
    
    elif j == "JP_Standard":
        tax = pre_tax_proceeds * p.jp_rate
    
    elif j == "JP_Reorg_Qualified":
        # Tax-deferred. Tax owed at this step = 0
        tax = 0.0
    
    else:
        raise ValueError(f"Unknown jurisdiction: {j}")
    
    return {
        "tax_owed": tax,
        "after_tax": pre_tax_proceeds - tax,
    }


def earn_out_present_value(
    max_amount: float,
    realization_probability: float,
    payout_year: float,
    discount_rate: float = 0.15,
) -> float:
    """Earn-out の確率重み付き PV.
    
    realization_probability: empirical 中央値 0.50 (35-55% range).
    discount_rate: founder の uncertainty discount。15-20% が standard.
    """
    expected = max_amount * realization_probability
    return expected / ((1.0 + discount_rate) ** payout_year)


def escrow_present_value(
    escrow_amount: float,
    release_probability: float,
    release_year: float,
    discount_rate: float = 0.05,  # 通常 escrow は claim 起こる確率が低く discount 緩い
) -> float:
    expected = escrow_amount * release_probability
    return expected / ((1.0 + discount_rate) ** release_year)


def founder_net_analysis(
    headline_deal_value: float,
    classes: list[LiquidationClass],
    common_shares: int,
    founder_common_shares: int,
    cash_pct: float = 1.0,
    stock_pct: float = 0.0,
    earn_out_max: float = 0.0,
    earn_out_probability: float = 0.50,
    earn_out_payout_year: float = 2.0,
    earn_out_discount_rate: float = 0.15,
    escrow_pct: float = 0.15,
    escrow_release_probability: float = 0.85,
    escrow_release_year: float = 1.5,
    escrow_discount_rate: float = 0.05,
    tx_expenses_pct: float = 0.025,  # banker 1.5% + legal/DD 1%
    debt_repay: float = 0.0,
    wc_adjustment: float = 0.0,  # negative if WC short
    tax_params: Optional[TaxParams] = None,
    holding_years: float = 5.0,
    acquirer_stock_lockup_years: float = 0.5,
    acquirer_implied_appreciation: float = 0.0,
) -> dict:
    """Sell-side proceeds の comprehensive bridge.
    
    Returns dict with all bridge steps and total founder economics.
    """
    if tax_params is None:
        tax_params = TaxParams(jurisdiction="JP_Standard")
    
    # Step 1: LP / common waterfall
    waterfall = waterfall_payout(headline_deal_value, classes, common_shares)
    common_pool = waterfall["common_pool"]
    lp_total = sum(waterfall["preferred_payouts"].values())
    
    # Step 2: Founder pro-rata share of common
    founder_share_pct = (
        founder_common_shares / common_shares if common_shares > 0 else 0
    )
    founder_pre_tx = common_pool * founder_share_pct
    
    # Step 3: Transaction expenses (founder shares pro-rata)
    tx_expense_total = headline_deal_value * tx_expenses_pct
    founder_tx_expense = tx_expense_total * founder_share_pct
    
    # Step 4: Debt repayment (founder shares pro-rata via reduced common pool)
    founder_debt_share = debt_repay * founder_share_pct
    
    # Step 5: WC adjustment (typically purchase price reduction)
    founder_wc = wc_adjustment * founder_share_pct
    
    # Step 6: Net cash + stock at closing (pre-tax, pre-escrow)
    closing_gross = founder_pre_tx - founder_tx_expense - founder_debt_share + founder_wc
    
    # Step 7: Escrow holdback
    escrow_held = closing_gross * escrow_pct
    closing_after_escrow = closing_gross - escrow_held
    
    # Step 8: Cash / stock split
    closing_cash = closing_after_escrow * cash_pct
    closing_stock = closing_after_escrow * stock_pct
    
    # Step 9: Tax on closing (cash 部分は immediate、stock 部分は tax-free reorg なら 繰延べ)
    if tax_params.jurisdiction in ("JP_Reorg_Qualified",):
        # Cash 部分のみ taxable (boot rule)
        taxable_now = closing_cash
    else:
        # Cash + stock 両方が realize 扱い (non-tax-free reorg)、または all cash deal
        taxable_now = closing_cash + closing_stock
    
    tax_result = apply_tax(taxable_now, tax_params, holding_years=holding_years)
    
    closing_after_tax = closing_after_escrow - tax_result["tax_owed"]
    
    # Step 10: Earn-out PV
    earn_out_pv = earn_out_present_value(
        earn_out_max * founder_share_pct,
        earn_out_probability,
        earn_out_payout_year,
        earn_out_discount_rate,
    )
    
    # Step 11: Escrow PV (release後)
    escrow_pv = escrow_present_value(
        escrow_held,
        escrow_release_probability,
        escrow_release_year,
        escrow_discount_rate,
    )
    
    # Step 12: Stock appreciation during lock-up (implied)
    stock_appreciation_value = closing_stock * (
        (1.0 + acquirer_implied_appreciation) ** acquirer_stock_lockup_years - 1.0
    )
    
    total_founder_pv = (
        closing_after_tax
        + earn_out_pv
        + escrow_pv
        + stock_appreciation_value
    )
    
    return {
        "headline_deal_value": headline_deal_value,
        "lp_payments": lp_total,
        "tx_expenses_total": tx_expense_total,
        "common_pool": common_pool,
        "founder_share_pct": founder_share_pct,
        "founder_pre_tx_proceeds": founder_pre_tx,
        "founder_closing_gross": closing_gross,
        "escrow_held": escrow_held,
        "closing_cash": closing_cash,
        "closing_stock_market_value": closing_stock,
        "taxable_now": taxable_now,
        "tax_owed": tax_result["tax_owed"],
        "closing_after_tax": closing_after_tax,
        "earn_out_pv": earn_out_pv,
        "escrow_pv": escrow_pv,
        "stock_appreciation_value": stock_appreciation_value,
        "total_founder_pv": total_founder_pv,
        "effective_retention_pct": (
            total_founder_pv / (headline_deal_value * founder_share_pct)
            if founder_share_pct > 0 else 0
        ),
    }
```

### 6.4 Worked Example: Series B SaaS founder の $500M exit

#### 6.4.1 Setup

- Company: SaaS, Series B, Delaware C-corp
- Cap table:
  - Series A: 1.0M shares, $5M invested, 1x non-participating
  - Series B: 2.0M shares, $20M invested, 1x non-participating
  - Common: 7.0M shares (founder 5.0M = 71% of common, employee pool 2.0M)
- Headline deal: $500M (cash 70% + stock 30%)
- Earn-out: max $50M, year 2, probability 50%, discount 15%
- Escrow: 15% × 18 mo, release prob 85%, discount 5%
- Tx expenses: 2.5%
- Debt: $0 (no venture debt)
- WC adjustment: $0
- Tax: US_NonQSBS, federal 20% + NIIT 3.8% + CA state 13.3%, 5-yr hold

#### 6.4.2 Bridge

| Step | 計算 | Amount |
|---|---|---|
| Headline | | $500.0M |
| Series A pref | min($5M, as-converted $5M × 1M / 10M = $50M) → max = $50M as-converted | rationale: as-converted > pref → take as-conv |
| Series B pref | $20M × 1 = $20M, as-converted = $500M × 2M / 10M = $100M → max = $100M as-converted | take as-conv |
| Common pool | $500M − $50M − $100M = $350M | $350M |
| Founder share (71% of common) | $350M × 71% = $248.5M | $248.5M |
| Tx expenses (founder pro-rata) | $500M × 2.5% × 71% × 7M/10M = $6.2M | −$6.2M |
| Closing gross | | $242.3M |
| Escrow (15%) | $242.3M × 15% = $36.3M | −$36.3M |
| Closing after escrow | $242.3M − $36.3M = $206.0M | $206.0M |
| Cash (70%) | $206M × 70% = $144.2M | |
| Stock (30%) | $206M × 30% = $61.8M | |
| Tax (cash + stock both realize, 37.1% effective) | $206M × 37.1% = $76.4M | −$76.4M |
| Closing after-tax | $206M − $76.4M = $129.6M | **$129.6M** |
| Earn-out PV | $50M × 71% × 50% × 1/1.15² = $13.4M | +$13.4M |
| Escrow PV | $36.3M × 85% × 1/1.05^1.5 = $28.6M | +$28.6M |
| Stock appreciation (assume 0%) | $0 | $0 |
| **Total founder PV** | | **$171.6M** |
| Headline founder share | $500M × 71% × 70% (common pool / headline) = $248.5M | |
| **Effective retention** | $171.6M / $248.5M | **69%** |

#### 6.4.3 Counterfactual: Same exit with QSBS legacy

- Tax: $10M exclusion + remaining $196M × 37.1% = $72.7M
- Closing after-tax: $206M − $72.7M = $133.3M
- Total PV: $133.3M + $13.4M + $28.6M = $175.3M
- Retention: $175.3M / $248.5M = **70.5%**

QSBS の効果は ~1.5% 改善 (founder の cost basis が低く $10M cap が full に効くケース)。Multiple stockholders で QSBS を spread すれば もっと効く。

### 6.5 Founder net 計算で見落としがちな調整項目

| 項目 | 影響 | 出典 / 注意 |
|---|---|---|
| **Net Working Capital (NWC) target** | DA 締結時に target NWC を合意、closing 時に actual と比較し差額を purchase price から控除 / 加算 | DA negotiation で target を低めに合意できれば founder 有利 |
| **Cash-free / debt-free adjustment** | M&A は cash-free / debt-free が standard、closing balance sheet で precise adjustment | DD で確認 |
| **Transaction bonus / change-of-control bonus** | Key exec への closing bonus、purchase price から控除 (purchase agreement で seller が負担) | $1M-$5M 級 |
| **Founder's tax gross-up** | Founder の tax を acquirer が gross-up して負担する deal も rare に存在 | 高 leverage negotiation 時 |
| **Indemnification cap and basket** | Cap = total deal の 10-20%、basket (deductible) $X 以下は claim できない | DA schedule |
| **Seller representation insurance premium** | Buyer-side R&W policy の premium を seller が負担する場合あり | §12 で詳述 |
| **Withholding tax** | Cross-border deal で source country が源泉徴収 | §5.3.1 treaty rate |

### 6.6 Sensitivity (Founder net の感応度)

Worked example のパラメータを動かす:

| パラメータ | Base | −1σ | +1σ | Founder net Δ |
|---|---|---|---|---|
| Headline deal value | $500M | $400M | $600M | ±$30M |
| Earn-out probability | 50% | 30% | 70% | ±$5M |
| Escrow release probability | 85% | 70% | 95% | ±$5M |
| Tax rate (jurisdiction) | 37% | 20% (Florida) | 50% (NY) | ±$30M |
| Acquirer stock lockup volatility | 0% | -20% | +20% | ±$12M |

> 結論: Headline と tax rate が dominant。Earn-out / escrow は marginal。Modeling では tax rate と headline を sensitivity 1st priority に置く。

---

## 7. Investor Exit IRR

### 7.1 Cash-on-Cash MOIC (Multiple of Invested Capital)

最もシンプルな指標。

```
MOIC = Total proceeds (cumulative distributions) / Total capital invested
```

##### Benchmark (Cambridge Associates / Pitchbook 2018-2023, vintage 2010-2017 fund)

| Quartile | MOIC | DPI (5 yr) | TVPI (10 yr) |
|---|---|---|---|
| Top quartile | 3.5x+ | 1.5x+ | 4.0x+ |
| Median | 1.7-2.2x | 0.5-0.8x | 1.8-2.5x |
| Bottom quartile | < 1.0x | < 0.3x | < 1.0x |

Fund GPs LP に "carry" を返すには TVPI ≥ 1.0x、DPI で realized 部分を実証する。

### 7.2 IRR (Internal Rate of Return)

複数 round の cash flow stream で discount rate を逆算。

```
0 = Σ_t (CF_t) / (1 + IRR)^t
```

Standard methodology: scipy.optimize.newton or Excel XIRR。

#### 7.2.1 IRR vs MOIC の trade-off

- **MOIC 高 + IRR 低**: 長期 hold で大きく増えた (10 yr で 3x → IRR 12%)
- **MOIC 低 + IRR 高**: 短期で 1.8x (3 yr で 1.8x → IRR 22%)
- VC LP は **両方** を評価する。一律 hurdle はない。

#### 7.2.2 Investor IRR 計算 (Python)

```python
import numpy as np
from scipy.optimize import brentq


def fund_irr(cash_flows: list[tuple[float, float]]) -> float:
    """cash_flows = [(t_year, amount), ...]
    
    投資 = negative, 分配 = positive.
    """
    def npv(rate):
        return sum(amt / (1.0 + rate) ** t for t, amt in cash_flows)
    
    return brentq(npv, -0.99, 10.0)
```

例: Series A VC が $5M 投資 (year 0)、$20M 受領 (year 6) → IRR = (20/5)^(1/6) − 1 ≈ 26.0%。

### 7.3 DPI / TVPI / RVPI

| Metric | 定義 | 解釈 |
|---|---|---|
| **DPI (Distributions to Paid-In)** | Cumulative distributions / Paid-in capital | Realized cash-on-cash。"Did I get my money back?" |
| **TVPI (Total Value to Paid-In)** | (Distributions + NAV) / Paid-in | Total value accumulation |
| **RVPI (Residual Value to Paid-In)** | NAV / Paid-in | Unrealized portfolio value |

> DPI = TVPI − RVPI。Fund late-stage (year 8+) で DPI が TVPI に追いつくかが評価軸。

### 7.4 J-Curve (VC Fund の典型 cash flow パターン)

| Year | Capital deployed (cumulative) | Realized distributions | TVPI | DPI |
|---|---|---|---|---|
| 1 | 25% | 0 | 0.95x | 0 |
| 2 | 50% | 0 | 0.85x | 0 |
| 3 | 75% | 0% | 0.95x | 0 |
| 4 | 90% | 0.1x (early secondary) | 1.10x | 0.10x |
| 5 | 95% | 0.3x (some exits) | 1.40x | 0.40x |
| 6 | 95% | 0.6x | 1.70x | 0.65x |
| 7 | 95% | 1.0x | 2.00x | 1.10x |
| 8 | 95% | 1.5x | 2.30x | 1.55x |
| 10 | 95% | 2.5x | 3.00x | 2.55x |

> 出典: Cambridge Associates U.S. Venture Capital Index, 2010-2018 vintage 平均 J-curve。

最初の 2-3 年は management fee + early write-down で TVPI < 1.0x、その後 mark-up と realization で curve が回復。

### 7.5 Carry / Distribution Waterfall (LP / GP 間)

Founder net とは別に、VC fund の LP / GP 間にも distribution waterfall が存在する。

```
Step 1: LP への 1.0x preferred return (full return of capital)
Step 2: LP への 8% preferred return (hurdle rate)
Step 3: GP catch-up (typical 100% to GP まで GP の % が 20% 相当に達するまで)
Step 4: 80/20 split (LP 80%, GP 20% carry)
```

GP の carry は portfolio level (whole fund), deal-by-deal, または European waterfall (whole fund first) など fund document で定義。

### 7.6 IC memo での提示形

IC memo の Investor Returns section では以下の table を提示する:

| Scenario | Exit value | Investor MOIC | Investor IRR | DPI uplift |
|---|---|---|---|---|
| Base (M&A 5 yr, $500M EV) | $500M | 5.0x | 38% | +2.5x to fund DPI |
| Upside (IPO 7 yr, $2B EV) | $2.0B | 20.0x | 50% | +10x to fund DPI |
| Downside (M&A 4 yr, $100M EV) | $100M | 1.2x | 5% | +0.6x |
| Tail (Wind-down) | $20M | 0.2x | -25% | partial loss |

---

## 8. M&A vs IPO Decision Tree

### 8.1 Quantitative Gate (適格判定)

#### 8.1.1 ARR / Revenue threshold

| 市場 | IPO 適格 ARR / Revenue | Comment |
|---|---|---|
| US (NYSE / Nasdaq) | $200M+ ARR (SaaS), $300M+ revenue (other) | 過去 3 年 audited financials 必須 |
| 日本 (TSE Prime) | ¥10B+ revenue (SaaS は ¥3B+ ARR で容認) | growth + 黒字 / 黒字目処 |
| 日本 (TSE Growth) | ¥1B+ revenue, growth 30%+ | 早期 IPO 路線 |
| LSE (London) | £50M+ revenue | EU regulatory 要件 |

#### 8.1.2 Growth rate

- IPO 候補: YoY growth ≥ 30% (SaaS), ≥ 20% (mature)
- M&A 候補: YoY growth ≥ 10% でも OK (multiple は下がるが exit 可能)

#### 8.1.3 Profitability path (Rule of 40)

- IPO: Rule of 40 (Growth + EBITDA margin) ≥ 40
- M&A: Rule of 40 ≥ 30 でも buyer 興味あり

#### 8.1.4 Public market environment

- IPO window indicator: Renaissance IPO Index (US), Nikkei Mothers Index (JP)
- VIX < 20: IPO friendly
- 過去 3 か月の同業 IPO の price action: +20% post-IPO で window open、−10% で closed
- 金利環境: 10-yr Treasury 上昇 → growth multiple 圧縮 → IPO 不利

### 8.2 Qualitative Judgment

#### 8.2.1 Founder operational appetite

- "M&A は exit, IPO は引き続き運営" — founder が post-exit に何年 work したいか
- M&A で acquirer に integrate される vs IPO で CEO 継続
- 多くの founder は 5-7 yr で burnout、M&A を選ぶ

#### 8.2.2 Strategic acquirer interest 存在

- Banker outreach で 3+ serious acquirer の indication
- Inbound interest (M&A team から direct contact) の積み上げ
- Strategic acquirer の cash position と M&A appetite (recent M&A history)

#### 8.2.3 Regulatory complexity

- Bio / Pharma: clinical trial の途中で IPO 困難 → M&A pathway
- Heavily regulated (banking, telecom, healthcare): IPO で disclosure 重い
- Defense / national security: CFIUS 規制で acquirer 限定

#### 8.2.4 Governance readiness

- IPO で必要: SOX 404 readiness, audit committee, indep board, IFRS / US GAAP audited financials, 20+ pages of risk factors
- M&A: less rigorous, ただし R&W で financial accuracy を保証する

### 8.3 4-Layer Decision Tree (Detailed)

```
LAYER 1: Quantitative IPO eligibility
  - ARR ≥ $200M (US) or ¥10B (JP Prime) or ¥1B (JP Growth)
  - Growth ≥ 25% YoY
  - Rule of 40 ≥ 40
  - Public market window open (VIX < 25, recent IPO traction +)
  - Audit-grade financials (3 yr history)
  ├─ ALL YES → Layer 2 へ進む
  └─ Any NO  → M&A track only

LAYER 2: Strategic acquirer interest
  - Banker pre-outreach (10-20 候補) で 3+ serious response
  - Past 12 mo inbound interest from named acquirers
  - Relevant comparable deal in past 18 mo (price discovery)
  ├─ YES (M&A も IPO もどちらも possible) → Layer 3
  └─ NO → IPO base case (M&A は backup)

LAYER 3: Founder / Board preference
  - Legacy / mission 重視 → IPO
  - Liquidity 重視 / burnout → M&A
  - Hybrid → Stock-heavy strategic M&A or IPO + secondary
  ├─ Strong M&A preference → M&A
  ├─ Strong IPO preference → IPO
  └─ Indifferent → Layer 4 (market timing で決定)

LAYER 4: Market timing
  - Public market: window open + comparable IPO multiple > pre-deal valuation × 1.2 → IPO
  - Acquirer cash position: 主要 acquirer が active M&A mode → M&A
  - Interest rate trajectory: 上昇 → IPO multiple 圧縮 → M&A 有利
```

### 8.4 Dual-Track Process (M&A + IPO 同時進行)

実務では dual-track が増えている。

#### 8.4.1 Mechanics

- Banker が S-1 を準備 (DRS = Draft Registration Statement, EDGAR で confidential filing) しつつ、parallel に M&A outreach (5-10 strategic + 3-5 PE)
- IPO roadshow 1 週間前まで M&A bid を accept できる "no-shop release" が DA に含まれる構造
- M&A deal closure → IPO 撤回 (S-1 withdraw)
- IPO 完了 → M&A track 終了

#### 8.4.2 Pros / Cons

- **Pros**: price discovery 最大化、competitive tension で premium 引き出す
- **Cons**: cost が高い (banker fee 両 track 分)、organizational distraction、information leakage risk
- 実例: Slack は dual-track で IPO (2019 direct listing) を選択、後に Salesforce 買収 (2020)。LinkedIn の S-1 filing 後に Microsoft の M&A announcement というケースは少ない (LinkedIn は直接 IPO → 5年後 Microsoft 買収)。

### 8.5 IPO ↔ M&A の price comparison

| Metric | IPO | Strategic M&A |
|---|---|---|
| Headline multiple | 10-25x revenue (top quartile SaaS) | 5-15x revenue (with synergies) |
| Premium over last private round | 30-100% | 30-50% |
| Liquidity timing | Lock-up 6 mo + insider gradual | Closing immediate (cash) or lock-up 6-12 mo (stock) |
| Tax implication | Founder LTCG (20% federal + state) | Founder LTCG, 適格 reorg なら 繰延べ |
| Operational continuity | 維持 (CEO continues) | 失う (typically 1-3 yr transition) |
| Public market scrutiny | Quarterly earnings, SOX, analyst | None (private after closing) |

### 8.6 IPO 撤回 / Pulled IPO

実例: 2022-2023 で多くの IPO が pull された (market window closed)。

- Pulled IPO 後の選択肢:
  - 6-12 mo 後に re-file (window 再開待ち)
  - Strategic M&A pivot (banker が relationship 活用)
  - Continue private + secondary (insider liquidity)
  - SPAC merger (de-SPAC 経由 listing、ただし 2020-2021 の peak は終了)

---

## 9. Strategic Comps for Buyer Selection

§3 で buyer typology を整理した。本 § ではその buyer ごとに **WTP 上限** を quantitative に推定する手順を示す。`05_valuation_wacc §6 (Comparable Transactions)` が "industry-wide M&A multiple" の正本だが、本書はそれを **buyer-specific** に分解する。

### 9.1 Buyer-specific Premium Analysis

#### 9.1.1 Standalone EV から WTP_upper への bridge

```
Standalone EV (DCF or Comps based)
  + PV(Revenue synergies × P_realize × time_phase)
  + PV(Cost synergies × P_realize × time_phase)
  − Integration cost (one-time)
  − Risk adjustment (post-close performance variance)
  = WTP_upper for this buyer
```

- Standalone EV は target の独立 valuation (DCF / Public Comps / Precedent Transactions)。
- Synergies はその buyer に固有 (Salesforce が見える synergy と Microsoft が見える synergy は違う)。
- Integration cost は acquirer 側 OpEx の 5–15%。
- Risk adjustment は post-close で実現しなかった場合の loss を確率 × 期待値で控除。

#### 9.1.2 Premium の典型レンジ

| Buyer type | Premium over standalone (%) | 主因 |
|---|---|---|
| Strategic, high synergies | 50–100% | Revenue + Cost synergies 両方 |
| Strategic, defensive | 30–60% | 競合への流出阻止 |
| Strategic, low synergies | 20–40% | "fair price" with limited uplift |
| PE, financial only | 0–20% | Synergies なし、operational uplift のみ |
| Tuck-in / acquihire | n/a (price discovery 困難) | 戦略的価値 individual |

> 出典: Goldman Sachs / Morgan Stanley Sell-side M&A Decks (公開), Bain Global M&A Reports (2018-2023)。

### 9.2 Synergies Decomposition

#### 9.2.1 Revenue synergies

| Source | Mechanism | Typical quantum |
|---|---|---|
| Cross-sell | Acquirer の existing customers に target product を sell | 1–3% of acquirer revenue × 3–5 yr discounted |
| Up-sell / bundling | Acquirer の existing product に target を bundle | 0.5–1% of combined revenue |
| New geography | Target の地理 presence で acquirer の export | 5–10% expansion in 5 yr |
| New vertical | Target の vertical で acquirer の category 拡張 | Variable, depends on TAM |
| Pricing power | Combined dominance で price uplift | 1–3% blended price increase |

> 実現確率: revenue synergies は 30–50% (中央値 40%) — academic studies (KPMG, Bain)。

#### 9.2.2 Cost synergies

| Source | Mechanism | Typical quantum |
|---|---|---|
| G&A consolidation | HR / Finance / Legal / IT を統合 | 2–5% of combined OpEx |
| Procurement leverage | Combined volume で vendor terms 改善 | 1–3% of combined COGS |
| R&D consolidation | Duplicate research を集約 | 5–10% of target R&D |
| Real estate | Office consolidation | 0.5–1% of OpEx |
| Sales / Marketing | Channel duplication 削減 | 3–8% of combined S&M |

> 実現確率: cost synergies は 60–80% (中央値 70%) — 同上 academic studies。

#### 9.2.3 Phasing (time profile of synergy realization)

| Year post-close | Revenue synergy realized | Cost synergy realized |
|---|---|---|
| 1 | 15% | 30% |
| 2 | 50% | 70% |
| 3 | 80% | 100% |
| 4 | 100% | 100% |
| 5 | 100% | 100% |

#### 9.2.4 Integration cost

- One-time (year 0-1): 5–10% of combined OpEx
- Severance, IT migration, brand migration, customer transition

### 9.3 Buyer's WTP Table (Worked Example)

Target: SaaS startup, ARR $50M, growth 50%, EBITDA margin 10%, standalone EV ¥10B (8x revenue with growth premium)。

| Buyer | Standalone EV | Revenue Syn (PV) | Cost Syn (PV) | Integration Cost | Risk discount | WTP upper | Premium over standalone |
|---|---|---|---|---|---|---|---|
| Salesforce | ¥10B | ¥3B (cross-sell to large CRM base) | ¥1B (G&A) | −¥0.5B | −¥1B | **¥12.5B** | +25% |
| Microsoft | ¥10B | ¥1B (smaller cross-sell vs Slack overlap) | ¥0.5B | −¥0.3B | −¥0.7B | **¥10.5B** | +5% |
| Oracle | ¥10B | ¥0.5B (limited overlap) | ¥1.5B (synergy-heavy playbook) | −¥0.5B | −¥0.5B | **¥11B** | +10% |
| Adobe | ¥10B | ¥2B (marketing cross-sell) | ¥0.5B | −¥0.4B | −¥0.6B | **¥11.5B** | +15% |
| ServiceNow | ¥10B | ¥1.5B (workflow cross-sell) | ¥0.3B | −¥0.3B | −¥0.5B | **¥11B** | +10% |
| Vista Equity (PE) | ¥10B | ¥0 | ¥1B (PE playbook cost cuts) | 0 | −¥0.5B | **¥10.5B** | +5% (only operational uplift) |
| Thoma Bravo (PE) | ¥10B | ¥0 | ¥1.2B (aggressive cuts) | 0 | −¥0.5B | **¥10.7B** | +7% |

> 観察: Salesforce が最高 WTP (+25%)、Microsoft / PE は competitive。Founder / banker は Salesforce を **anchor buyer** として auction を構築する戦略。

### 9.4 Auction strategy implication

- Anchor (Salesforce) を最後まで残し、他 (Adobe, ServiceNow) と price discovery 競争させる
- PE は floor を設定する役割 (Salesforce が backout したときの fall-back)
- Microsoft は info-leak risk が高い (target を deeper acquire で knowledge appropriation)、carefully manage

### 9.5 Defensive premium の特殊ケース

時に acquirer は **synergies なしでも defensive 動機で premium** を払う。

- 競合 acquirer の市場参入を阻止 (Microsoft → LinkedIn は Salesforce 阻止と読む見方)
- Disruptor の脅威排除 (Facebook → Instagram、$1B at $0 revenue は WTP much higher than synergies justify)
- 規制対応の preemptive (例: 個人情報保護で data assets が strategic に貴重に)

このカテゴリは standard WTP 計算の枠外、case-by-case で premium が +50-200% に跳ねる。

### 9.6 Comps method の限界

- Buyer-specific synergies は acquirer's IR / 10-K analysis で粗い推定しか出ない
- Realized synergies の post-close disclosure は limited (公開する acquirer は少ない)
- Sensitivity analysis で WTP に ±30% の uncertainty を抱えた状態が standard
- IC memo では "**WTP range** for each buyer" と表記 (point estimate 出すと defensive で苦しくなる)

---

## 10. NDA → LOI → DA Process

スタートアップの sell-side process は以下 stages を 4–6 か月で run する。Founder / 投資家が抑えるべき milestone と deliverable を整理する。

### 10.1 Process Timeline (4-6 month standard)

| Phase | Duration | 主要 activities | Founder の deliverable | Risk |
|---|---|---|---|---|
| **Pre-launch** | 1–2 mo | Banker selection, CIM 準備, buyer list 構築, data room 整備 | Banker engagement letter signing, CIM 内容承認 | 過早 launch で valuation 圧縮 |
| **Outreach** | 2–4 wk | NDA 締結, teaser distribution, CIM 配布 | NDA list 承認, CIM signing | Information leakage |
| **Round 1 bids (IOI)** | 2–3 wk | Indicative offer, 5–10 buyers が IOI 提出 | IOI 評価 (price + structure + buyer fit) | Lowball IOI 多数 |
| **Round 2 (LOI)** | 4–6 wk | Detailed data room, mgmt presentations, focused 2–3 buyers, LOI (Letter of Intent) | LOI selection, exclusivity grant | Lock-out risk (LOI 1 社 exclusivity で他社失う) |
| **DA negotiation** | 4–6 wk | Definitive Agreement 交渉, schedules 作成, R&W 詳細 | DA review and signing | Re-trade risk (price adjustment by buyer) |
| **Signing → Closing** | 1–3 mo | Regulatory approval, financing, closing conditions | MAC clause monitoring, working capital settlement | Deal break 5–10% (Bain study) |

> 合計: 4–6 か月 (signing 起点)、closing まで 5–9 か月。Bio / regulated industry は longer (6–12 mo)。

### 10.2 NDA (Non-Disclosure Agreement)

#### 10.2.1 NDA の役割

- Buyer が CIM / data room を read する前の confidentiality 担保
- Standstill provision (buyer が unsolicited bid を出さない約束、12-24 mo)
- Non-solicitation (key employee 引き抜き禁止)

#### 10.2.2 Founder protection points

- Strict NDA で IP / pricing / customer list の漏洩防止
- Limited use clause (買収目的のみ使用、competing product 開発に転用禁止)
- Term: 2–5 年 (standard)
- Mutual NDA を要求する buyer (大手 strategic) と one-way NDA で済む buyer (PE) に分かれる

### 10.3 CIM (Confidential Information Memorandum)

#### 10.3.1 CIM の構成 (50-100 ページ)

1. Executive Summary (3-5 ページ): Highlights, financial summary, transaction rationale
2. Company Overview: History, founders, product, business model
3. Industry Overview: TAM, growth, competitive landscape
4. Products / Technology: Architecture (描画エンジン / 処理系含む), IP, roadmap
5. Customers: Logo list, segmentation, retention, NRR
6. Sales / Marketing: GTM, channels, sales productivity
7. Operations: HR, locations, infrastructure
8. Financials: 3-yr historical, projections, KPIs (ARR, churn, gross margin, S&M efficiency)
9. Management Team: Bio, equity, retention plan
10. Investment Highlights: 5-7 key reasons to acquire

#### 10.3.2 CIM の dos and don'ts

- **Do**: Conservative projections (founder は 30% growth と思っていても CIM では 20-25% で書く、後で beat-and-raise が好印象)
- **Do**: Quantify customer concentration、retention metrics、unit economics
- **Don't**: Customer 名を full disclose (logo は出すが contract value は anonymized)
- **Don't**: Overpromise synergies (buyer 側で計算する)
- **Don't**: Pre-negotiate price in CIM (banker が separate process で discovery)

### 10.4 Auction vs Negotiated

#### 10.4.1 Broad Auction (5-10 buyers)

- Pros: Price discovery 最大化, competitive tension で premium 引き出す
- Cons: Process 長期化, leak risk 高、buyer の commitment 浅い (window shopping)
- Use: Mature target with multiple potential buyers

#### 10.4.2 Targeted Auction (2-3 strategic buyers)

- Pros: Bilateral pacing で deal certainty 高、leak risk 低
- Cons: Price discovery 限定的
- Use: Niche target where only 2-3 buyers logically fit

#### 10.4.3 Single-buyer Negotiated

- Pros: Speed, certainty, relationship preserved
- Cons: No price discovery, buyer leverage 強い
- Use: Pre-existing strategic relationship, time-sensitive deal, market 不景気

### 10.5 Investment Banker Selection

#### 10.5.1 Bulge Bracket vs Mid-Market vs Boutique

| Tier | 例 (US) | 例 (JP) | Sweet spot deal size | Fee | 特徴 |
|---|---|---|---|---|---|
| Bulge bracket | Goldman Sachs, Morgan Stanley, JP Morgan, Citi, BofA | 野村, 大和, SMBC日興 | $1B+ | 1–2% | Brand, broad relationship, public deal |
| Mid-market | Lazard, Jefferies, Houlihan Lokey, William Blair | みずほ, 三菱UFJ M&A | $200M-$1B | 1.5–3% | Sector specialty, hands-on |
| Boutique | Qatalyst, Allen & Co, Centerview, FT Partners (FinTech) | GCA (Houlihan 傘下), M&Aキャピタルパートナーズ | $50M-$2B | 2–4% | Strong sector expertise, founder-friendly |
| Founder-friendly boutique | Code Advisors, Paul, Weiss & Cooley advisory | フロンティア・マネジメント | < $300M | 3–5% | Sell-side specialty, founder advocacy |

#### 10.5.2 Engagement Letter

- Retainer: $50K–$500K (deal size 連動、refundable from success fee)
- Success fee: 1–3% of deal value (sliding scale common — 上振れ tier で incentive 増)
- Tail provision: engagement 終了後 12–18 mo に banker 紹介 buyer から offer 来た場合も fee
- Conflicts disclosure: banker が buyer の advisor 経験あり → conflict of interest disclosure 必須

#### 10.5.3 Banker selection criteria

- Sector expertise (recent comparable deals)
- Buyer relationships (specific names)
- Process management capability
- Fee structure (success-based を厚く)
- Founder rapport (long process なので chemistry 重要)

### 10.6 Data Room

#### 10.6.1 Tier 構造

- **Tier 1 (Round 1)**: Financial statements, customer summary (anonymized), top-level metrics, org chart
- **Tier 2 (Round 2, focused buyers)**: Detailed customer contracts, IP, engineering details, sensitive HR
- **Tier 3 (Final 1 buyer)**: Customer names, salary by employee, M&A history

#### 10.6.2 Access permissioning

- Each buyer has separate access level
- Watermark + audit log (誰が何を view したか)
- Print / download permission を制御
- Q&A は data room 経由で all buyers に同等回答 (fair process)

#### 10.6.3 Recommended platforms

- Intralinks (incumbent)
- Datasite (Merrill Datasite)
- Box / Dropbox (lighter deals)
- iDeals / Firmex (mid-market)

### 10.7 Diligence Types

#### 10.7.1 Commercial DD (CDD)

- 第三者 management consultancy が市場 / 競合 / customer 分析
- 担い手: McKinsey, Bain, BCG (top tier), OC&C, LEK, Roland Berger (sector), 国内では NRI / DIR / Frontier
- Output: 100–200 ページ report, customer interview 結果, market growth proof points
- Cost: $200K–$1M (deal size 連動)
- Founder への hit: customer 紹介依頼 multiple times

#### 10.7.2 Technical DD (Tech DD)

- CTO advisor or boutique (e.g., Crosslake, Bain TQC) が technology stack / scalability / security 評価
- Code review, architecture review (描画エンジン / 処理系の選定理由含む), DevOps assessment
- Cost: $100K–$500K
- Output: green/yellow/red rating per area

#### 10.7.3 Financial DD (FDD / Quality of Earnings — QoE)

- Big 4 (Deloitte / EY / KPMG / PwC) or boutique (Alvarez & Marsal, RSM, FTI Consulting, BDO)
- 3 年 historical financials の audit-grade review
- Add-back analysis (one-time items, GAAP adjustments)
- Working capital normalization
- Cost: $200K–$1M

#### 10.7.4 Legal DD

- BigLaw (target side: Cooley, Wilson Sonsini, Latham; buyer side: Skadden, Sullivan & Cromwell)
- Corporate, IP, regulatory, employment, litigation, contracts
- Cost: $500K–$3M

#### 10.7.5 Tax DD

- Big 4 or specialty boutique
- Historical tax compliance, exposure (uncertain tax positions), structuring optimization
- Cost: $100K–$500K

#### 10.7.6 HR DD

- Key employee retention analysis (who will leave?)
- Compensation benchmark, equity dilution
- Compliance (payroll, benefits)
- Cost: $50K–$300K

#### 10.7.7 ESG DD (post-2020 increasing)

- Environmental impact, social practices, governance
- Material for European / US large strategic buyers
- Often integrated into commercial DD

#### 10.7.8 Cyber DD (post-2020)

- Penetration testing, breach history, security posture
- Especially material for SaaS / FinTech / healthcare
- Cost: $50K–$500K

### 10.8 LOI (Letter of Intent)

#### 10.8.1 LOI の主要条項

- **Purchase price**: 範囲 ($X–$Y) or specific number
- **Consideration mix**: Cash / stock / earn-out 比率
- **Exclusivity**: 30–90 days、buyer に対する no-shop の commit
- **Confidentiality**: NDA 既存 + LOI-specific
- **Condition precedent**: DD 完了, board approval, regulatory approval
- **Termination**: Mutual termination, drop-dead date

#### 10.8.2 LOI の大半は non-binding (price-related portions)

- Price は **non-binding** (final DA で改定可能)
- Exclusivity は **binding**
- Founder side で気をつけるべきは "exclusivity granted で他社 outreach 停止" → buyer の re-trade leverage が強化

#### 10.8.3 Re-trade risk

- LOI 後、DD で issue 発見 → buyer が price 引き下げ要求
- Empirical: signed LOI deal の 20–30% で re-trade (price 5–15% 下方修正、Mergermarket 2018-2022 stats)
- Founder 側 mitigants: short exclusivity (30 days), strict re-trade trigger conditions, multiple LOI received before exclusivity grant

### 10.9 DA (Definitive Agreement)

#### 10.9.1 DA の主要章

1. **Purchase Price and Consideration**: cash, stock, earn-out details
2. **Closing Mechanics**: working capital adjustment, closing balance sheet
3. **Representations and Warranties (R&W)**: target / buyer 両方の statements
4. **Covenants**: pre-closing operating restrictions, post-closing obligations
5. **Closing Conditions**: regulatory, MAC, financing, board approval
6. **Indemnification**: cap, basket, survival, escrow
7. **Termination**: mutual, drop-dead, MAC walkaway

#### 10.9.2 DA Schedules

- Schedule of exceptions (R&W に対する disclosure)
- Earn-out plan (KPI definition, calculation methodology)
- Employee retention list
- Customer list (closing condition: top X customers signed renewal)

### 10.10 Signing → Closing Gap (1-3 か月)

#### 10.10.1 Regulatory approval

- **HSR (Hart-Scott-Rodino) US**: 取引額 ≥ $111.4M (2024 threshold) で antitrust filing 必須。30-day waiting period (extendable to 60+ days if Second Request)。
- **JFTC (公正取引委員会) 日本**: 国内売上 ¥20B+ (取得側) and ¥5B+ (target) で届出。30-day waiting period。
- **EC (European Commission)**: EU-wide turnover ≥ €5B (combined) で merger control filing。
- **CFIUS (Committee on Foreign Investment in the United States)**: foreign acquirer + US national security → CFIUS review。取引によっては 6-12 か月 review。
- **業種別**: 銀行 (FRB, OCC), 通信 (FCC), 防衛 (DoD), 保険 (state insurance commissioners), 医療 (FDA), 公益事業 (state PUCs)。

#### 10.10.2 MAC (Material Adverse Change) Clause

Buyer の walkaway right。

- **Standard MAC carve-outs**: 業界全体への影響 (recession, war, pandemic)、market-wide events
- **Target-specific MAC**: revenue ≥ X% drop, key customer loss, key employee departure
- **Disproportionate effect rule**: target が市場全体より大きく影響受けたら MAC 認定可能
- 実例: COVID-19 で 一部 deal が MAC 主張で walkaway (Tiffany & Co / LVMH 2020 が有名、後に再交渉で価格下方修正)

#### 10.10.3 Financing Contingency (PE only)

- PE deal は debt financing 確定が closing condition
- Strategic deal は通常 financing contingency なし (acquirer cash / stock currency)
- Reverse termination fee (RTF): financing 失敗時に PE が target に支払う fee (typical 5–8% of deal value)

#### 10.10.4 Stockholder Approval

- Public target: proxy statement → stockholder vote (50–80 days timeline)
- Private target: written consent of majority/supermajority (drag-along で minority も bind)
- 90%+ consent achieved if drag-along + voting agreement coverage

---

## 11. Earn-out Mechanics 詳解

§4.4 で structure overview を整理した。本 § で details を deep dive する。

### 11.1 Common Structures

#### 11.1.1 Revenue-based earn-out

- Trigger: ARR > $X by year 1, OR cumulative revenue > $Y by year 2
- Payout: linear or tier (e.g., 0% if < target, 50% if 80%, 100% if 100%, 150% if 120%)
- Pros: 客観的、accounting で gameable 度低い
- Cons: founder が profit margin を犠牲に top-line を作る誘惑

#### 11.1.2 EBITDA-based earn-out

- Trigger: EBITDA > $X by year 2
- Pros: profitability も縛れる
- Cons: cost allocation 紛争多い (acquirer が parent allocations を target に push)
- 紛争多発のため founder は EBITDA-based を可能な限り回避

#### 11.1.3 Milestone-based earn-out (Bio / Pharma 多用)

- Trigger: Phase 2 trial readout positive, FDA approval, EMA approval
- Payout: discrete amount per milestone ($50M for Phase 2, $100M for FDA approval)
- Pros: binary, clear
- Cons: scope 紛争 ("Phase 2 success" 定義), 失敗時に full forfeiture

#### 11.1.4 Time-based RSU (Vesting based, less "earn-out")

- 4 year service period
- Performance-conditional acceleration 含む
- Founder retention の名目だが effectively earn-out 寄り

#### 11.1.5 Product launch / customer milestone

- New product launch by year 1
- Top 10 customer renewal at year 1
- Subscriber 100K achieved by year 2

### 11.2 Pitfalls (再列挙、深掘り)

#### 11.2.1 KPI Gameable

- Revenue earn-out: 期末で discount 投げ売り → KPI 達成、後に refund や churn で acquirer 側に loss
- EBITDA earn-out: R&D / S&M を年末 cut → 短期 EBITDA boost、長期 growth 毀損
- Subscriber earn-out: 無料 trial で subscriber 数稼ぎ、retention 死

#### 11.2.2 Buyer's Operational Control

- Post-close で acquirer が:
  - Pricing 強制変更 (price up で churn → KPI failure)
  - Headcount cap (sales 採用拒否 → revenue growth 遅延)
  - Marketing budget cut (lead gen 不足 → pipeline 縮小)
  - Cross-sell mandate (target が acquirer product に集中 → standalone ARR 鈍化)
- Founder の earn-out failure を意図的に誘導するケース、訴訟原因 #1

#### 11.2.3 Common Cause vs Specific Cause Disputes

- Macro economic recession: KPI 未達はどちら側の責任?
- Industry shock (e.g., COVID-19): force majeure
- Acquirer の corporate event (parent's restructuring): どちら?

### 11.3 Earn-out Litigation Statistics

| Source | Statistic |
|---|---|
| Bain 2018-2022 M&A Reports | 30%+ の earn-out で formal dispute |
| SRS Acquiom 2017-2023 study | 中央値 50% 実現、25% は zero realization |
| BCG (Bio/Pharma) | Milestone earn-out の 25-30% が full pay-out |
| Delaware Chancery Court | Earn-out litigation は M&A 訴訟の上位 3 位 |

### 11.4 Earn-out PV 計算

```python
def earn_out_pv_full(
    max_amount: float,
    realization_probability: float = 0.50,
    payout_year: float = 2.0,
    discount_rate: float = 0.15,
    litigation_probability: float = 0.30,
    litigation_haircut: float = 0.30,  # litigation 起こると 30% haircut
) -> dict:
    """Earn-out の expected PV with litigation adjustment.
    
    Returns: {
        'expected_payout': realized amount before discount,
        'pv_no_litigation': PV ignoring litigation,
        'litigation_adjusted_pv': PV with litigation expected loss,
    }
    """
    expected_payout = max_amount * realization_probability
    pv_no_litigation = expected_payout / ((1 + discount_rate) ** payout_year)
    
    # Litigation expected loss
    litigation_loss = pv_no_litigation * litigation_probability * litigation_haircut
    litigation_adjusted_pv = pv_no_litigation - litigation_loss
    
    return {
        "expected_payout": expected_payout,
        "pv_no_litigation": pv_no_litigation,
        "litigation_adjusted_pv": litigation_adjusted_pv,
    }


# Example
result = earn_out_pv_full(
    max_amount=50_000_000,
    realization_probability=0.50,
    payout_year=2.0,
    discount_rate=0.15,
    litigation_probability=0.30,
    litigation_haircut=0.30,
)
# expected_payout: $25M
# pv_no_litigation: $18.9M
# litigation_adjusted_pv: $17.2M
```

### 11.5 Best Practice Summary (Founder Protection)

1. **Simple objective metric** (revenue, single number)
2. **Founder operational autonomy 期間** (12-18 か月、acquirer は budget / headcount / pricing を一方的に変更しない)
3. **Earn-out plan を DA schedule に明記** (計算式、accounting policy、dispute resolution)
4. **Acceleration triggers** (founder termination without cause, acquirer breach, business sale → full pay)
5. **Reporting transparency** (monthly KPI report, independent auditor right)
6. **Cap at 30% of total deal max** (40%+ は reject)
7. **Period ≤ 2 yr** (3 yr 以上は long-term commitment burden)
8. **Anti-game clauses**: acquirer は reasonable best efforts to operate target in normal course of business
9. **Negotiate explicit allocations**: corporate overhead allocation methodology, transfer pricing for cross-sell
10. **Independent arbitrator** for earn-out calculation disputes (default to Big 4 accounting firm)

### 11.6 Earn-out Negotiation Tips for Founders

| Negotiation point | Founder asks | Acquirer asks | Compromise |
|---|---|---|---|
| Period | 1 year | 3 years | 2 years |
| Metric | Revenue | EBITDA | Revenue (with margin guardrail) |
| Cap | 50% of deal | 10% of deal | 25% of deal |
| Operational autonomy | Full | None | Defined budget envelope, hiring up to plan |
| Acceleration | Any termination | Only "for cause" termination | Without cause + good reason |
| Audit right | Annual | None | Quarterly review by founder + independent auditor |

---

## 12. R&W Insurance & Indemnification

### 12.1 Indemnification Escrow (古典 mechanism)

#### 12.1.1 Standard terms

- **Holdback**: 10–20% of deal value (中央値 15%)
- **Period**: 12–24 か月 (中央値 18 か月)
- **Cap (per breach)**: 5–15% of deal value、または unlimited for fraud / fundamental reps
- **Survival**: General reps 12-18 か月、tax reps 3-7 yr (statute of limitations), fundamental reps perpetual

#### 12.1.2 Basket / Deductible

- **Tipping basket**: $X 以下の claims は no claim、X 超過時に first dollar から claim 可
- **True deductible**: $X 以下は no claim、$X 超過分のみ claim
- **De minimis threshold**: 1 claim $50K-$100K 以下は basket からも除外 (nuisance claim 排除)

#### 12.1.3 Survival Period

| Rep type | Standard survival | 例 |
|---|---|---|
| General reps | 12–18 mo | Most R&W |
| Tax reps | 3–7 yr | Statute of limitations |
| Fundamental reps | Perpetual | Authority, capitalization, ownership |
| Special indemnities | Negotiated | Specific known issues |

### 12.2 R&W (Representations & Warranties) Insurance

#### 12.2.1 概要

Buyer が insurance company から R&W policy を購入し、target's R&W breach に対する claims を policy で carve out。Post-2015 で急速に普及 (US で 25%+ の M&A が R&W coverage 利用)。

#### 12.2.2 Mechanics

- **Policy limit**: 10–20% of deal value (中央値 10%)
- **Retention (deductible)**: 0.75-1.0% of deal value (12 か月後 0.5% に drop)
- **Premium**: 2–4% of policy limit, paid one-time
- **Term**: 6-7 years (general reps), 6-7 years (tax reps)
- **Underwriter**: AIG, Chubb, Beazley, Allianz, Tokio Marine HCC, Liberty GTS

#### 12.2.3 Pros / Cons

**Pros (founder)**:
- Escrow を minimize (e.g., 0.5% でなく 15%)
- Founder の post-close exposure 限定
- Speed (acquirer が confident with insurance backstop)

**Pros (acquirer)**:
- Coverage が 6-7 yr 続く (escrow より長い)
- Underwriter の DD で added scrutiny

**Cons**:
- Premium cost (typically split 50/50 or seller-paid)
- Exclusions (known issues, environmental, ERISA pension underfunding, FCPA — these stay in escrow / specific indemnities)
- Process burden (additional underwriter DD calls)

#### 12.2.4 Worked example

- Deal: $500M, R&W policy limit $50M (10% of deal)
- Premium: $50M × 3% = $1.5M (typically seller pays or shared)
- Retention: 0.75% × $500M = $3.75M (escrow holds this for 12 mo)
- After 12 mo: Retention drops to 0.5% × $500M = $2.5M
- Founder net escrow holdback: $3.75M (vs $75M without R&W policy = 5% of deal)

### 12.3 Specific Indemnities (Known Issues)

R&W coverage 外で、known issues は specific indemnity で seller liability が retained:

- Pending litigation (with cap of estimated exposure)
- Tax exposure (uncertain tax position from prior audit)
- Environmental remediation
- Pre-closing customer dispute
- Pre-closing IP infringement claim

### 12.4 Indemnification の Founder Protection Tactics

1. **Cap at 10-15%** of deal value (above this 拒否)
2. **R&W insurance** で escrow を 0.5% に圧縮
3. **De minimis $100K, basket $1M** で nuisance 排除
4. **Survival 12 mo for general reps** (18 か月 max)
5. **Pro-rata indemnification** (founder + investors が pro-rata に責任分担、joint and several は拒否)
6. **Sole and exclusive remedy** clause (escrow / R&W policy が唯一の救済、common law claims を waive)
7. **Knowledge qualifiers** ("to the knowledge of seller" を厚く plant in reps)
8. **Materiality scrape** に注意 (acquirer が "all material" を "any" に scrape する技、founder は反対)
9. **Anti-sandbagging clause**: buyer が DD 中に発見した issue で post-close claim できないようにする
10. **Tail insurance**: D&O policy の 6 yr tail を pre-closing で確保 (officer / director の personal liability)

---

## 13. Mini Cases (Real-world)

> 各 case は public press release / IR / S-1 / 10-K filings から構成。Founder net 計算は public information 範囲での **推定**、actual numbers は当事者しか knows。Reference 用途を超えた使用は推奨しない。

### Case 1: Slack → Salesforce ($27.7B, 2020)

#### 1.1 Deal facts

- **Announcement**: 2020-12-01。Closing 2021-07-21。
- **Headline value**: $27.7B (公開時点の Salesforce 株価ベース)
- **Consideration mix**: ~50% cash + ~50% Salesforce stock
  - Per Slack share: $26.79 cash + 0.0776 Salesforce share
  - Salesforce stock @ closing: ~$245 → $19 stock value per share
- **Premium over Slack pre-announcement price**: ~55%
- **Tax structure**: Reverse triangular merger (Type A reorganization)、cash 部分は boot taxable

#### 1.2 Founder Stewart Butterfield の net 推定

- Stewart Butterfield は IPO 時点 (2019) で約 8.6% (~50M shares post-IPO equivalent)
- Closing 時点では IPO 以降の sales / dilution を経て ~5.3% (~30M shares)
- Per-share consideration: $26.79 cash + 0.0776 × $245 = $45.81 total
- Headline founder share: 30M × $45.81 ≈ $1.37B
- Cash 部分: 30M × $26.79 ≈ $804M (taxable boot)
- Stock 部分: 30M × 0.0776 = 2.33M Salesforce shares (~$571M at closing)
- Tax (assumes Canadian resident, Canada-US deal, 26.76% federal + provincial top combined): ~$215M
- **Closing after-tax net**: ~$1.155B
- Lock-up: 6 か月 (typical) → Salesforce 株が closing から 1 年で −20% drop → mark-to-market loss ~$114M
- **Total founder net (post lock-up)**: ~$1.04B (76% of headline)

#### 1.3 Lessons

- Stock-heavy deal の **lock-up risk** が顕在化 (Salesforce が 2021-2022 で −30% drop)
- Boot rule で cash 部分のみ taxable、stock 部分は cost basis carry over
- Founder の operational role: Butterfield は Slack CEO として 2 年 transition、その後 退任 (2023)

### Case 2: WhatsApp → Facebook ($19B, 2014)

#### 2.1 Deal facts

- **Announcement**: 2014-02-19。Closing 2014-10-06。
- **Headline value**: $19B
  - Cash: $4B
  - Facebook stock: ~$12B (at closing date)
  - Restricted Stock Units (RSU) for retention: ~$3B (4 yr vest)
- **Premium**: WhatsApp は private、premium 計算は last raise (2013 Series C ~$1.5B) と比較で ~13x

#### 2.2 Founder Jan Koum の net 推定

- Jan Koum は約 45% (Sequoia 主要 LP の counter pattern)
- Cash 部分: $4B × 45% = $1.8B (taxable @ federal LTCG 20% + state CA 13.3% + NIIT 3.8% = 37.1%)
- Cash after-tax: $1.8B × (1 − 0.371) = $1.13B
- Facebook stock: $12B × 45% = $5.4B (tax-deferred via stock-for-stock, basis carry)
- RSU: $3B × Koum allocation (uncertain, ~$1B?), 4 yr vest, ordinary income at vesting
- **Closing after-tax (cash + stock)**: ~$6.5B headline value、cash $1.13B realized
- Lock-up: 12 か月 sale restrictions
- Facebook stock from $69 (closing) to $130 (1 yr later) → ~+88% appreciation
- Stock value at lock-up release: $5.4B × 1.88 = $10.15B
- **Total Koum economics (5 yr post-deal)**: ~$11B+ (headline value × 1.4x due to Facebook rally)

#### 2.3 Lessons

- Stock-heavy deal の **upside scenario** (acquirer rally で headline 超え)
- Tax-deferred reorganization で immediate tax 圧縮、long-term Facebook holding が wise (Koum は 2018 まで hold)
- RSU retention package — 100% vesting 前に Koum 退社 (2018) → partial forfeiture
- 後悔事例: Koum が WhatsApp の advertising 戦略で Zuckerberg と clash、4 年で離脱、$850M unvested RSU 放棄

### Case 3: LinkedIn → Microsoft ($26.2B, 2016)

#### 3.1 Deal facts

- **Announcement**: 2016-06-13。Closing 2016-12-08。
- **Headline value**: $26.2B
- **Consideration**: 100% cash ($196 per share)
- **Premium over LinkedIn pre-announcement price**: ~50% ($131 → $196)
- **Tax structure**: All-cash merger、stock is fully taxable
- **Earn-out**: なし

#### 3.2 Founder Reid Hoffman の net 推定

- Hoffman は約 11% (大株主、LinkedIn co-founder)
- Headline founder share: $26.2B × 11% = $2.88B
- All cash → fully taxable @ federal 20% + state CA 13.3% + NIIT 3.8% = 37.1%
- Tax: $2.88B × 37.1% = $1.07B
- **Closing after-tax**: $1.81B (63% of headline)
- No lock-up (cash deal)
- No earn-out

#### 3.3 Lessons

- All-cash deal の **founder net retention は jurisdiction (state tax) が dominant**
- Hoffman は CA resident で full state tax を被った
- Microsoft 側 motivation: data + distribution synergies、defensive vs Salesforce
- LinkedIn は IPO 後 5 年で M&A → IPO + M&A の両方を経験するパターン

### Case 4: Mercari M&A active acquirer (例: 中堅日本 startup の買収パターン)

#### 4.1 Pattern overview

メルカリは複数の startup acquisition を実施。代表例として **Origami (キャッシュレス決済) の事業承継 (2020)**、Echodyne (米国) 等。中堅日本 startup の典型 cash + stock pattern を例示する架空 case (real-world Mercari deal の一般化)。

- Target: 国内 SaaS startup, ARR ¥3B, growth 40%, Series B
- Acquirer: メルカリ (上場、TSE Prime)
- **Headline**: ¥10B
- **Consideration**: 70% cash + 30% Mercari stock
- **Tax structure**: 適格株式交換 (法人税法 第2条第12号の17 / 第62条の9 要件満たす)
- **Earn-out**: ¥2B (revenue ¥5B by year 2 trigger)

#### 4.2 Founder net 推定

- Founder ownership: 25%
- Headline founder share: ¥10B × 25% = ¥2.5B
- Cash 部分: ¥1.75B
- Stock 部分: ¥0.75B (Mercari 株 受領、適格交換で繰延べ)
- Cash の譲渡所得税: ¥1.75B × 20.315% = ¥356M
- **Closing after-tax**: ¥1.75B − ¥356M = ¥1.39B + ¥0.75B (Mercari stock, deferred) = **¥2.14B nominal**
- Earn-out PV: ¥2B × 25% × 50% × 1/1.15² = ¥189M
- **Total founder PV**: ¥2.14B + ¥189M = ¥2.33B (vs ¥2.5B headline → 93% retention nominal、ただし stock 売却時に追加課税)

#### 4.3 Lessons

- 適格株式交換で **stock 部分の課税繰延べ** → nominal retention 90%+
- 但し将来 Mercari 株を sell する時に譲渡所得課税が発生 → real net は売却タイミング依存
- 日本 founder の標準 pattern: 適格再編 + earn-out 抑制 (¥2B / ¥10B = 20%)
- 米国比で earn-out の litigation 頻度が低い (日本は和解 culture)

### Case 5: Acquihire example (small Bay Area startup)

#### 5.1 Pattern overview (representative composite)

実例多数 (Yahoo の度重なる acquihire 等)。架空 case で典型 mechanics を示す。

- Target: pre-revenue AI startup, 12 員 engineering team, total raised $10M (Seed + Series A)
- Cap table: founders 50% common, employees 20% common (vested), Seed VC 15% pref ($3M @ 1x), Series A VC 15% pref ($7M @ 1x)
- **Headline**: $30M (PR 上の表記)
- **実 consideration breakdown**:
  - Upfront cash: $10M (LP repayment + transaction expenses)
  - Retention RSU: $20M (4 yr vest, double trigger)
- **Tax structure**: 一部 Section 351 contribution (acquihire 寄り deal は acquirer 側で goodwill とせず compensation expense)

#### 5.2 投資家の損益

- Series A VC (15% pref, $7M @ 1x): 1x preference を取れず → preference $7M を $10M cash pool から優先 → $7M 回収 (元本回収のみ、IRR ≈ 0%)
- Seed VC (15% pref, $3M @ 1x): 残り $3M cash pool から $3M (元本のみ)
- Common holders (founders + employees, 70% combined): cash pool の残額 $0M → distribution ゼロ

#### 5.3 Founder の retention

- Founder 2 名: $20M retention RSU を 50:50 split、各 $10M
- 4 年 vest = $2.5M / yr、継続在籍 condition
- Effective founder net (4 yr post-deal, assuming full vesting): $10M × 2 founder = total $20M
- Headline $30M に対して実際 founder economics は retention RSU vesting 依存
- 訴え: 投資家から見て M&A は failure (1x preference 回収のみ)、founder には retention package で nominal "win"

#### 5.4 Lessons

- Acquihire の **headline price は misleading**: 実 consideration の大半は retention package
- 投資家 IRR ≈ 0%、founder は 4 yr 引き続き acquirer に縛られる
- Press release で "$30M acquisition" を読んだ founder candidate が誤解しないよう、IC memo / IPO comparable analysis では除外する pattern

### Case 6: Vista Equity → Marketo → Adobe (PE LBO の好例)

#### 6.1 Deal sequence

- **Step 1**: Vista Equity Partners が Marketo を取得 (2016-08, $1.79B, all-cash LBO)
  - Marketo は当時 Nasdaq 上場、株価低迷中 (Salesforce / Oracle 競合圧迫で uncertainty)
  - Vista の Take-private deal、premium ~64% over closing price
- **Step 2**: Vista の operational improvement (2016-2018, ~2 年)
  - Pricing optimization (price uplift)
  - Sales productivity 向上
  - Bolt-on acquisitions (no major)
  - Cost discipline (S&M efficiency 改善)
  - ARR が成長
- **Step 3**: Adobe が Marketo を Vista から取得 (2018-09 announcement, 2018-11 closing, $4.75B all-cash)
  - Premium over Vista's purchase: 2.65x in ~2 years
  - Adobe の最大級 acquisition (当時)、Marketing Cloud 強化目的

#### 6.2 Vista の financial outcome

- Initial investment: ~$1.79B (debt + Vista equity)
- LBO structure (estimated): ~50% debt ($900M Term Loan B / unitranche), ~50% equity ($890M Vista equity)
- Exit proceeds: $4.75B
- After debt repayment (~$900M): ~$3.85B equity returned
- Vista equity MOIC: $3.85B / $890M ≈ 4.3x in 2 yr
- Vista IRR: 4.3x^(1/2) − 1 ≈ 107% IRR (gross of fees)
- Profit (gross): ~$3B
- Buyouts Insider awarded "Deal of the Year"

#### 6.3 Management の roll-over

- 一部 Marketo executives は Vista deal で roll-over equity (5-15% rough estimate)
- Roll-over founders/execs は Adobe exit で **2nd bite of apple** を享受
- 4-5 名の key executives が collectively ~$50-100M の roll-over return (estimated)

#### 6.4 Lessons

- PE の **operational uplift + multiple expansion** で 2 年 2.65x exit
- Founder ではなく Vista が dominant beneficiary、ただし management roll-over は real wealth creation
- 注意: spec に "6 months later" とあるが正確には **2 年** (2016 Q3 → 2018 Q3-Q4)
- Source: Adobe 10-K (FY2018), Vista Equity Partners IR releases, Buyouts Insider DOY 2018

### Case 7: Earn-out litigation (Salesforce / Demandware-type dispute)

#### 7.1 Pattern (representative composite from Delaware Chancery Court cases)

実例多数 (Salesforce-Demandware の earn-out portion 紛争、Akorn-Fresenius の MAC walkaway、Genuine Parts-Essendant earn-out 訴訟等)。架空 case で典型紛争 mechanics を示す。

- Target: Marketing automation SaaS, ARR $40M
- Acquirer: 大手 SaaS 上場企業
- **Headline deal**: $400M
  - Upfront: $300M (cash $200M + acquirer stock $100M)
  - Earn-out: $100M (revenue $80M ARR by year 2 trigger)
- **Closing**: 2020 Q1
- **Earn-out evaluation**: 2022 Q1

#### 7.2 紛争の内容

- Year 1 post-close: acquirer が target の sales team を own field force と統合
- Year 1 ARR growth が低下 (target 単独で 40% growth → 統合後 20% growth)
- Year 2 ARR: $50M (vs $80M target) → earn-out trigger 不達
- Founder 主張: acquirer が sales merger で commitment 違反、common cause で earn-out should pay
- Acquirer 主張: revenue accounting に target customer lost、normal course of business

#### 7.3 Litigation outcome

- Delaware Chancery Court で 2 年 litigation
- Discovery で acquirer の internal email exposes integration mandate
- 和解 (settlement): $100M earn-out のうち $50M (50%) を支払い
- Legal fees: founder 側 $5M, acquirer 側 $8M (両方とも recoverable but settlement で walk-away)

#### 7.4 Lessons

- Earn-out の **litigation 頻度** (Bain 30%) を modeling で probability discount
- DA schedule に **operational autonomy clauses** を厚く plant しないと acquirer integration mandate に勝てない
- "Reasonable best efforts to operate target in normal course" clause が key
- IC memo の earn-out PV 計算で **litigation expected loss** を control variable として入れる (本書 §11.4 参照)
- Empirical: 中央値 50% realization、25% は zero、最頻値 0% or 100% (binary outcome)

---

## 14. xlsx 統合 (skill との接続)

### 14.1 既存 sheet 拡張

#### 14.1.1 `08_CapTable Exit Waterfall` の拡張

`04b_cap_table_mechanics §6` で扱う Exit Waterfall sheet を、本書 §6 の Founder-net Bridge まで延長する。具体的には:

- **既存**: liquidation pref → as-converted → common pool までを表示
- **追加**:
  - Bridge to founder net (税後): tx expenses, escrow holdback, WC adjustment, tax wedge, earn-out PV, escrow PV
  - Multiple jurisdiction / tax regime sensitivity (US_QSBS_legacy / post_obbba / NonQSBS / JP_Standard / JP_Reorg_Qualified)
  - Effective retention pct を最終行に表示
- 計算 logic は `scripts/build_model.py` の `build_exit_waterfall_sheet()` で `founder_net_analysis()` (§6.3) を呼び出す形で実装

#### 14.1.2 `13_IC_Memo` に "Exit Thesis" section 追加

IC memo template に以下 sub-sections を追加:

1. **Likely Exit Pathway** (M&A / IPO / continue private) と probability weighting (§2)
2. **Likely Buyer Shortlist**: 3-5 個 × buyer type × WTP 推定 (§9 の WTP table)
3. **Likely Consideration Mix**: cash / stock / earn-out 比率 (§4)
4. **Founder Net Analysis**: headline ¥XB → 税後 founder net の bridge (§6)
5. **Investor Returns**: MOIC / IRR (base / upside / downside, §7)
6. **Tax Wedge Assumption**: jurisdiction × QSBS / 適格再編 status (§5)
7. **Earn-out Realization**: probability 35-55% × discounted PV (§11)
8. **Exit Timeline**: 4-7 yr horizon (§10 process)
9. **Anti-pattern Self-check**: §15 list

### 14.2 New sheet 追加候補 (optional layer)

#### 14.2.1 `17_MA_Exit_Analysis` (architectural decision: 17 sheet 数増を許容するか)

> 既存 17 sheet 構成 (`_named_ranges.md` で固定済) と緊張がある。new sheet 追加は optional layer として扱い、`scripts/build_model.py --include-exit-analysis` flag で opt-in する。

Sheet structure:

| Section | Content |
|---|---|
| **Header** | Inputs (founder_jurisdiction, exit_year, acquirer_shortlist) |
| **Multi-scenario M&A** | 6 scenarios × founder net × investor IRR × probability |
| - Strategic Best (premium 100%) | EV = standalone × 2.0, founder net per §6 |
| - Strategic Mid (premium 50%) | EV = standalone × 1.5 |
| - Strategic Low (premium 25%) | EV = standalone × 1.25 |
| - PE deal (10x EBITDA) | EV = EBITDA × 10, roll-over 15% |
| - Acquihire (talent only) | EV = $30M, retention RSU 70% |
| - No-exit / wind-down | EV ≈ $0, partial recovery |
| **Probability-weighted founder net** | Σ (prob × founder net) by scenario |
| **Probability-weighted investor IRR** | Σ (prob × IRR) by scenario |
| **Sensitivity** | Tornado chart for top drivers (headline, tax, earn-out prob) |

### 14.3 `15_input_schema` の拡張

`15_input_schema.md` に new fields を追加:

```yaml
exit_thesis:
  expected_exit_year: 5  # 4-7 typical range
  exit_pathway_probability:
    strategic_ma: 0.60
    ipo: 0.20
    pe_ma: 0.15
    no_exit: 0.05
  acquirer_shortlist:
    - name: "Salesforce"
      type: "strategic"
      ev_revenue_multiple_estimate: 12.0
      premium_estimate: 0.4  # 40% over standalone
      synergies_pv_estimate: 30000  # in million local currency
    - name: "Microsoft"
      type: "strategic"
      ev_revenue_multiple_estimate: 10.0
      premium_estimate: 0.2
      synergies_pv_estimate: 15000
    - name: "Vista Equity"
      type: "pe"
      ev_ebitda_multiple_estimate: 10.0
      premium_estimate: 0.05
      synergies_pv_estimate: 0  # PE has no synergies
  founder_jurisdiction: "JP_Reorg_Qualified"  # or "US_QSBS_legacy" / "US_QSBS_post_obbba" / "US_NonQSBS" / "JP_Standard"
  founder_holding_period_years: 5.0  # for QSBS qualification
  expected_consideration_mix:
    cash_pct: 0.60
    stock_pct: 0.30
    earn_out_pct: 0.10
  earn_out_terms:
    period_years: 2.0
    realization_probability: 0.50  # empirical median
    discount_rate: 0.15
  escrow_terms:
    pct: 0.15
    period_months: 18
    release_probability: 0.85
  rw_insurance_used: true
```

### 14.4 `_master_decision_tree.md` への routing 追加

`_master_decision_tree.md` の §A に以下 entry を追加:

| Trigger keyword | First reference | Secondary |
|---|---|---|
| "exit thesis" | `19_ma_exit_for_founders §1.3, §2` | `08_investment_thesis §7-8` |
| "M&A waterfall" | `04b_cap_table_mechanics §6` + `19 §6` | `12_tax_strategy §5` |
| "founder net" | `19 §6 (founder_net_analysis)` | `04b §6` |
| "earn-out" | `19 §4.4, §11` | `04a §4` |
| "QSBS" | `19 §5.1.1` | `12_tax_strategy §3` |
| "適格株式交換" | `19 §5.2.1` | `12_tax_strategy §4` + `13a_consolidation_core §4` |
| "tax-free reorganization" | `19 §4.2.3-4, §5.1.2-3` | `12_tax_strategy §3-4` |
| "R&W insurance" | `19 §12.2` | `12_tax_strategy §6` |
| "MAC clause" | `19 §10.10.2` | n/a |
| "lock-up" | `19 §4.2, §13 Case 1-2` | `04b §7` |
| "investor IRR" | `19 §7` | `04b §6` |
| "M&A vs IPO" | `19 §8` | `14_ipo_readiness §1-3` |
| "buyer WTP" | `19 §3, §9` | `05_valuation_wacc §6` |
| "indemnification escrow" | `19 §12.1` | n/a |

---

## 15. Anti-patterns (避けるべき)

### 15.1 Headline price = founder net 誤解

- **症状**: IC memo / cap table の Exit Thesis section で headline ¥XB をそのまま founder の "expected exit" と書く
- **何が間違いか**: §1.2 で示した通り、LP / debt / tax / escrow / earn-out unfunded で乗算的に減額され headline の 50-70% に縮む
- **正しい approach**: §6.1 の bridge を完全に通し、最終行に "effective retention %" を表示

### 15.2 Earn-out as "guaranteed upside"

- **症状**: earn-out max を 100% で IC memo に計上
- **何が間違いか**: empirical 35-55% realization rate (SRS Acquiom)、30% は litigation
- **正しい approach**: §11.4 の `earn_out_pv_full()` で probability + discount + litigation adjustment

### 15.3 Stock consideration without buyer DD

- **症状**: acquirer 株を headline value 通り founder net に計上、lock-up 中の volatility / liquidity / regulatory risk を無視
- **何が間違いか**: Yahoo $5B Tumblr → write-down 全額の事例、Salesforce post-Slack で −30% drop
- **正しい approach**: acquirer 株の β / 30-day historical volatility / 6-mo lock-up implied loss を計算 (§6.6 sensitivity)

### 15.4 Ignoring tax wedge (jurisdiction agnostic 仮定)

- **症状**: 全 deal を flat 20% capital gains で modeling
- **何が間違いか**: US founder の non-QSBS (37%) と日本 founder 適格再編 (0% 繰延べ) で **30%+ 差**
- **正しい approach**: §5 の jurisdiction × QSBS regime × 適格 status を sensitivity input で扱う

### 15.5 Auction over-confidence

- **症状**: 10 buyer 全員が serious bidder と仮定、competitive premium を high で見積もる
- **何が間違いか**: 実際は IOI 5-10 のうち serious LOI 2-3、final bid 1-2。Pricing tension は限定的
- **正しい approach**: IOI から LOI への絞り込み rate を historical 30-40% で probability discount

### 15.6 Liquidation preference の seniority 無視

- **症状**: 全 preferred を 1x non-participating 仮定で flat に処理
- **何が間違いか**: Series B が 1x participating の場合 Series A holder より先に取り分が減り、common holder への trickle が更に縮小。Down-round で 2x preference が混じると waterfall が大きく変わる
- **正しい approach**: §6.2 の class-by-class waterfall を `waterfall_payout()` で逐次 simulate

### 15.7 Process timeline の楽観論

- **症状**: "3 か月で M&A close する" と仮定して funding plan を組む
- **何が間違いか**: §10.1 standard 4-6 か月 (signing)、closing まで 5-9 か月。Regulatory approval や MAC で更に伸長
- **正しい approach**: signing → closing の gap を 3 か月 buffer で plan、HSR / antitrust filing risk を考慮

### 15.8 Acquihire の headline 価格信仰

- **症状**: PR の "$30M acquisition" を IC memo の comparable analysis に使う
- **何が間違いか**: 内訳 70%+ が retention RSU、real consideration は $10M 以下
- **正しい approach**: deal の "consideration breakdown" が disclosed されない場合、acquihire 寄りと推定し comparable から除外

### 15.9 Cross-border tax の単純化

- **症状**: US-JP deal で federal LTCG だけを引く
- **何が間違いか**: Treaty rate, withholding, PE risk, state/prefectural tax で実効税率が複雑
- **正しい approach**: §5.3 の cross-border treatment を tax advisor と confirm、conservative estimate

### 15.10 Founder ego trap

- **症状**: founder が自身の ownership pct で "headline × 個人 持分%" を expected と思い込む
- **何が間違いか**: liquidation preference stack で common holder に trickle する金額は disproportionate に薄い
- **正しい approach**: §6 の bridge を**毎 round** founder に説明、down-round / bridge note の影響を visualize

---

## 16. 関連 reference との整合

| Reference | 本書の対応 § | 整合性 check |
|---|---|---|
| `04b_cap_table_mechanics §6` (Exit Waterfall) | 本書 §6 | 本書は §6 の起点として liquidation preference を再掲、その後 founder net まで延長 |
| `05_valuation_wacc §6-9` (Comps, DCF, WACC) | 本書 §9 (WTP), §3.2 (PE LBO) | Standalone EV を本書が引き受け、buyer-specific synergies を加算 |
| `08_investment_thesis §7-8` (IC memo) | 本書 §1.3, §14.1.2 | IC memo の Exit Thesis section の正本は本書 §14.1.2 |
| `12_tax_strategy §3-5` (Tax) | 本書 §5 | 本書は **使用ガイド**、詳細処理は `12` を参照 |
| `13a_consolidation_core §4` (適格組織再編) | 本書 §4.2.4, §5.2.1 | 連結会計処理は `13a`、deal 構造は本書 |
| `18_customer_value_and_pricing §4` | 本書 §6.5 | Pricing realization が customer LTV に影響 → exit value driver |
| `_terminology` | 本書 全体 | QSBS / Section 368 / 適格株式交換 / earn-out / R&W insurance / MAC 等の用語整合 |
| `_master_decision_tree` | 本書 §14.4 | Routing entry を §14.4 で定義 |
| `_self_review_protocol §9` | 本書 §15 | Anti-patterns を self-review check として運用 |

---
