---
name: customer_value_and_pricing
description: 顧客 ROI / 費用対効果の定量化と value-based pricing の正本。Bain B2B Elements of Value、Forrester TEI、Van Westendorp PSM、Conjoint analysis 等の手法を体系化し、業態別の customer value 算出 template とプライシング決定ロジックを提供
type: reference
priority: P0
related: [02_saas_metrics, 03_business_models, 09_market_sizing, 16_cost_structure, 08_investment_thesis, 15_input_schema, _terminology]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 顧客 ROI / WTP (Willingness To Pay) / value-based pricing / Tier design / outcome-based pricing の方法論はすべて本書を canonical とする。`02_saas_metrics.md` (LTV / CAC) や `03_business_models.md` (revenue 構造) で扱う pricing は、**根拠としての customer value** を本書に委ねる。
- **Routing**: [`_master_decision_tree.md §A (構築)`](_master_decision_tree.md) の "pricing thesis" / "顧客 ROI" / "value-based pricing" / "WTP 推定" 関連 entry の第 1 reference。`scripts/build_model.py` が `02_Revenue` / `11_KPI_Dashboard` / `13_IC_Memo` を埋める際、price 決定根拠として参照される。
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の追加 5 check (顧客 ROI 中央値 / WTP boundary / Pricing realization / 双方向 double counting / Hidden cost 計上) を実行。
- **関連 reference**: `02_saas_metrics §5-6` (LTV) / `03_business_models §1-7` (業態別 revenue) / `09_market_sizing §3-4` (TAM penetration) / `16_cost_structure §3-5` (vendor 側 COGS) / `08_investment_thesis §7` (IC memo "Pricing Thesis" section) / `15_input_schema §2` (input schema に customer_roi / wtp_estimate field) / `_terminology §6` (canonical metric 定義)。

> 用語注: 本書では「Operating System / OS」を避け、「価格決定の仕組み」「pricing 体系」と表現する (個人ルール)。時系列の数値データは原則として表形式 (markdown table) に揃える。

---

# 18. Customer Value and Pricing (顧客価値と価値ベース・プライシング) 徹底リファレンス

> 本ドキュメントは、これまで `02 / 03 / 09 / 16` のいずれにも収まらなかった「**顧客にとっての便益 (customer value)**」軸を独立 reference として体系化したものである。Value-based pricing (価値ベース・プライシング) の根拠として、顧客 ROI を定量化し、WTP (Willingness To Pay) 上限を推定し、それを vendor 側の price と照合するまでの一連の手順を 1 冊にまとめる。
>
> **対象読者**: Claude (xlsx pricing 入力エージェント)、IC memo の "Pricing Thesis" を書くアナリスト、それを review する人間バンカー / VC partner。
>
> **Scope**: 顧客 ROI 計算手法、WTP 推定 (PSM / Conjoint / Stated / Revealed)、pricing model 選定 (Subscription / Usage / Outcome / Hybrid / Tier / Freemium)、業態別 template、IC memo / xlsx への組み込み。各論の **計算ロジックは本書を canonical とし**、関連 reference は補完として参照する。
>
> **数値の出典**: ベンチマーク (NRR / take rate / ICER 閾値 / SaaS pricing) は本文中に出典を明示し、複数ソースが矛盾する場合はレンジで提示する (平均化はしない)。

---

## 目次

1. [なぜ顧客価値 (customer value) を定量化するか](#1-なぜ顧客価値-customer-value-を定量化するか)
2. [Customer Value の構造分解 — Value Driver Tree](#2-customer-value-の構造分解--value-driver-tree)
3. [Quantification Frameworks (定量化手法カタログ)](#3-quantification-frameworks-定量化手法カタログ)
4. [Value-Based Pricing — 価値ベース・プライシングの実装](#4-value-based-pricing--価値ベースプライシングの実装)
5. [WTP 推定の実証手法 (PSM / Conjoint / Stated / Revealed)](#5-wtp-推定の実証手法-psm--conjoint--stated--revealed)
6. [業態別 Customer Value 計算 Template (7 業態 × 4 stage)](#6-業態別-customer-value-計算-template-7-業態--4-stage)
7. [Modeling 反映方法 — 17 sheet xlsx への組み込み](#7-modeling-反映方法--17-sheet-xlsx-への組み込み)
8. [Qualitative Effects の定量化](#8-qualitative-effects-の定量化)
9. [Anti-patterns (落とし穴 7 連発)](#9-anti-patterns-落とし穴-7-連発)
10. [Mini Case 詳解 (7 例)](#10-mini-case-詳解-7-例)
11. [References / Sources (出典)](#11-references--sources-出典)
12. [関連 reference との整合](#12-関連-reference-との整合)

---

## 1. なぜ顧客価値 (customer value) を定量化するか

### 1.1 価格決定の根本ロジック

**価格は「顧客が得る便益」の関数である。** Cost-plus pricing (原価 + マージン) や Competition-based pricing (競合 ± α) は「価格の下限と参照点」を提供するに過ぎず、**価格の上限 (天井) は常に customer value で決まる**。Hermann Simon が『Confessions of the Pricing Man』で繰り返し主張するように、企業が値決めで取りこぼしている利益のうち、最大の機会は「customer value を客観的に推定し、それに比例した price を設定する」ことに尽きる。

| Pricing 哲学 | 何が決める価格 | 弱点 |
|---|---|---|
| Cost-plus | 原価 + 一定 margin | 顧客が支払うかどうかと無関係。費用構造が変わらない限り price も動かない |
| Competition-based | 競合の price に追随 | 自社の差別化 (機能 / ブランド / SLA) を価格に反映できない。Race-to-bottom リスク |
| Value-based | 顧客 ROI の関数 | データが必要 (顧客分析 / WTP 調査 / TEI study)。短期で立てづらい |

> 本書は **Value-based pricing を canonical 哲学** として採用する。Cost-plus / Competition-based は「次善 (fallback)」として §4.2 で扱う。

### 1.2 WTP (Willingness To Pay) の上限定義

WTP とは、顧客がその製品 / サービスに対して支払ってもよいと考える **最大金額**である。経済学的には「indifference point」であり、価格 = WTP のとき顧客は無差別、価格 > WTP のとき購入を見送る。**WTP は customer ROI の上限を超えない** という制約は本書の最重要原理である。

```
顧客 ROI > 0 ↔ 購入する経済合理性あり (WTP > 0)
顧客 ROI ≤ 0 ↔ 購入しない (WTP = 0)
WTP の上限 ≈ 顧客 ROI の正値範囲
```

実務ではさらに **gainsharing rule of thumb** (§4.1) を掛けて、vendor が顧客 ROI のうち取り切る割合 (典型 20-30%) を決める。100% 取り切る pricing は理論上可能でも実際には顧客が買わない。これは「顧客が利益を残してこそリピート / 推奨が生まれる」という長期視点による。

### 1.3 IC memo の Pricing Thesis を支える

IC (Investment Committee) memo (詳細は `08_investment_thesis.md` 参照) で「ARR ¥X が realistic」と主張するとき、その根拠の核心は pricing thesis である。本 reference §7.3 で示す通り、pricing thesis は:

1. Customer ROI 中央値の数値 (§3.1 / §3.3 の手順で計算)
2. WTP boundary の推定 (§5 の手法のいずれか)
3. 自社 take の比率 (§4.1 gainsharing)
4. Pricing model の選定根拠 (§4.2)
5. Tier design / land-and-expand path (§4.3 / §4.5)
6. Expansion path (NRR target、land price → expand price)

の 6 要素から成る。これらが揃って初めて「ARR ¥X」が defensible になる。

### 1.4 TAM 計算の reality check

`09_market_sizing.md` で扱う TAM / SAM / SOM は「市場 × penetration」の積で書かれるが、**penetration の上限は WTP × adoption で制約される**:

```
SOM (SaM = Serviceable Obtainable Market)
  = Market × (% of customers with ROI > 0)
        × (adoption rate within ROI-positive segment)
        × (realistic share within adopters)
```

例えば「WTP-positive 70% × adoption 50% × share 20% = 7%」のように、TAM の 7% に realistic な天井が決まる。`09_market_sizing.md` で penetration を入力するときは、**本 reference §7.5 の手順で derived value を確認**することを必須とする。

### 1.5 業態別ピボット判断

Pricing model を変更する (e.g. subscription → usage、usage → outcome) ことは、**customer value 構造の変化に紐づく**。

- **Subscription → Usage**: 顧客 ROI が usage に比例する場合に有効 (例: AWS、Stripe、Twilio)。固定費と感じる顧客の心理的抵抗を軽減
- **Usage → Outcome**: 顧客 ROI が単一 KPI に集中している場合に有効 (例: 売上増の % を vendor が取る)。adoption リスクを vendor 側が負う
- **Subscription → Hybrid**: subscription の予測可能性 + usage の上振れ捕捉 (例: Snowflake = compute + storage)

この移行を判断するときも、本 reference の §4.2 / §6 の業態別 template に立ち返ることになる。

### 1.6 競合分析の core lens

競合の WTP / take rate を見ると、「顧客 ROI を vendor が何 % 取らせているか」が分かる。

| 業態 | 典型 take rate | 解釈 |
|---|---|---|
| 決済 (Stripe) | 取扱高の 2.9% + ¥30 / 件 | 取扱高の 3% が vendor take。残り 97% が顧客手元 |
| Marketplace (Etsy) | 売主取引額の 6.5% + 広告 | 売主が買主 access の対価として 7% を vendor に |
| Ride hailing (Uber 等) | 取扱高の 25-30% | driver の機会費用 + matching value の対価 |
| SaaS (Salesforce SFA) | 顧客 labor saving の 5-10% 程度 | 顧客 ROI 大きいが pricing は控えめ → expansion 余地 |

競合の take rate を観察すれば、自社の pricing が「下に振れすぎ (under-priced) / 上に振れすぎ (over-priced)」かを評価できる。

### 1.7 本章のまとめ

| 視点 | 本書での位置 | 関連 § |
|---|---|---|
| 価格決定根拠 | Value-based pricing が canonical | §4 |
| WTP 上限の定義 | 顧客 ROI の正値範囲 | §1.2 / §3 / §5 |
| IC memo 連動 | Pricing thesis 6 要素 | §7.3 |
| TAM reality check | penetration ceiling を WTP × adoption で計算 | §7.5 |
| Pricing model pivot | customer value 構造の変化に紐づく | §4.2 / §6 |
| 競合 lens | take rate ratio で判定 | §1.6 / §6 |

---

## 2. Customer Value の構造分解 — Value Driver Tree

Customer value を「定性的なスローガン (e.g. 業務効率化)」のレベルに留めず、**金額換算可能な driver tree** に分解することが、本章のゴールである。本書は (a) 4 軸の自社流分類 → (b) Bain "Elements of Value" → (c) Forrester TEI の 3 層で driver tree を組み立てる。

### 2.1 4 軸の Value Driver

実務で使い回しやすい 4 軸 (本書の canonical 分類):

| Category | 定義 | B2B SaaS の例 | D2C consumer の例 | 金額換算難度 |
|---|---|---|---|---|
| **Cost reduction** | 既存コストの削減 | 人件費 (FTE × 時間 × 時給) / SaaS 費 / inf 費 削減 | 月額固定費削減、買い替え不要化 | 低 (直接) |
| **Revenue uplift** | 売上の増加 | conversion 改善、retention 改善、cross-sell | 顧客離脱抑制、LTV 向上 | 中 (因果分離が要) |
| **Risk reduction** | 損失期待値の低減 | downtime 削減、compliance 違反回避、不正検知 | 故障保証、保険的価値 | 高 (probability × magnitude) |
| **Time-to-value / Strategic** | 立ち上げ早期化、戦略的便益 | 立ち上げ早期化、talent retention、ブランド | 体験的便益、社会的承認 | 高 (代理指標) |

**金額換算難度** は、その軸の便益を ¥ 単位で defensible に表現するハードルの高さ。Cost reduction が最も直接的、Time-to-value / Strategic は代理指標 (proxy indicator) を介する。

#### 2.1.1 Cost reduction の標準形

```
Annual cost reduction
  = Σ_(saved item) {baseline cost × % reduction × adoption rate}
```

- 例: 営業 100 人 × 週 5 時間 × ¥5,000/hr × 50 週 × 70% adoption = ¥87.5M / 年 (Salesforce SFA case、§6.1 / §10 case 1 で詳細展開)

#### 2.1.2 Revenue uplift の標準形

```
Annual revenue uplift
  = Σ_(KPI) {baseline KPI × Δ% × duration × adoption × realization}
```

- 例: ¥10B baseline × +2% conversion × 通年 × 100% adoption × 50% realization = ¥100M / 年
- **realization rate** (実現率) を必ず discount すべき。理論値で計算すると OBL (Over-Bullish Logic, §9.1) に落ちる

#### 2.1.3 Risk reduction の標準形

```
Annual risk reduction
  = Σ_(risk event) {probability × magnitude × % reduction}
```

- 例: downtime 確率 5%/年 × 損失 ¥100M/event × 60% reduction = ¥3M / 年
- 「probability-weighted」が要諦。確率 × 影響額 の積で計算

#### 2.1.4 Time-to-value / Strategic の標準形

直接金額換算ができないため、代理指標 (proxy) を介する:

| Strategic 便益 | 代理指標 | 金額換算 |
|---|---|---|
| ブランド向上 | NPS、search volume、share-of-voice | NPS +12 → revenue +1% (Bain 研究) |
| Talent retention | 離職率 ↓ | 1 人離職 = ¥1.5M (採用 + onboarding) |
| Time-to-market 短縮 | 製品リリース月数 | 1 ヶ月早期 = month 1 の revenue ¥X 余分に取れる |
| Strategic optionality | M&A target value | 階段関数で評価 (§8.3 参照) |

### 2.2 Bain "Elements of Value" (B2B 40 + B2C 30)

Bain & Co の Almquist, Senior, Bloch の研究 (HBR 2018 "The B2B Elements of Value", HBR 2016 "The Elements of Value") が、customer value を **40 要素 (B2B) / 30 要素 (B2C)** に分解した。本書はこれを driver tree の **chess piece** として使う。

#### 2.2.1 B2B 40 elements (5 layer Pyramid)

Bain の B2B モデルは 5 層 ピラミッドで構成される。下層ほど客観的・機能的、上層ほど主観的・感情的。

```
┌─────────────────────────────────┐
│ Layer 5: Inspirational (4)       │ ← Purpose / Vision / Hope / Social responsibility
├─────────────────────────────────┤
│ Layer 4: Individual (7)          │ ← Career / Personal (Network expansion / Marketability / Reputational assurance / Design & aesthetics / Growth & development / Reduced anxiety / Fun & perks)
├─────────────────────────────────┤
│ Layer 3: Ease of doing biz (19)  │ ← Productivity (5) / Access (3) / Relationship (4) / Operational (4) / Strategic (3)
├─────────────────────────────────┤
│ Layer 2: Functional (5)          │ ← Economic (Improved top line / Cost reduction) / Performance (Product quality / Scalability / Innovation)
├─────────────────────────────────┤
│ Layer 1: Table stakes (4)        │ ← Meeting specifications / Acceptable price / Regulatory compliance / Ethical standards
└─────────────────────────────────┘
```

(出典: Almquist, Senior, Cleghorn "The B2B Elements of Value" HBR Mar 2018)

各 element の**定量化アプローチ**:

| Layer | 例 | 定量化方法 | 難度 |
|---|---|---|---|
| Functional - Economic | Cost reduction | FTE × hour × rate × % saving | 低 |
| Functional - Performance | Scalability | infrastructure cost / load | 中 |
| Ease of doing biz - Productivity | Time savings | hour saved × rate | 低 |
| Ease of doing biz - Access | Information | search cost saved | 中 |
| Individual - Career | Career advancement | 昇進率の差、retention | 高 (proxy) |
| Individual - Personal | Reduced anxiety | stress index、employee NPS | 高 (proxy) |
| Inspirational - Purpose | Vision | brand survey、NPS | 高 (proxy) |

> Bain の研究で、**6 つ以上の elements で高得点を取った企業の NPS は 60% 高い**。このため pricing の根拠としてだけでなく、customer success / 製品ロードマップの優先順位付けにも使える。

#### 2.2.2 B2C 30 elements (4 layer Pyramid)

B2C は 4 層 ピラミッド (出典: Almquist, Senior, Bloch HBR Sep 2016 "The Elements of Value")

```
┌─────────────────────────────────┐
│ Social Impact (1)                │ ← Self-transcendence
├─────────────────────────────────┤
│ Life Changing (5)                │ ← Provides hope / Self-actualization / Motivation / Heirloom / Affiliation & belonging
├─────────────────────────────────┤
│ Emotional (10)                   │ ← Reduces anxiety / Rewards me / Nostalgia / Design / Badge value / Wellness / Therapeutic value / Fun / Attractiveness / Provides access
├─────────────────────────────────┤
│ Functional (14)                  │ ← Saves time / Simplifies / Makes money / Reduces risk / Organizes / Integrates / Connects / Reduces effort / Avoids hassles / Reduces cost / Quality / Variety / Sensory appeal / Informs
└─────────────────────────────────┘
```

#### 2.2.3 B2B / B2C の使い分け

| 軸 | B2B (40 elements) | B2C (30 elements) |
|---|---|---|
| 意思決定者 | 複数 (committee buying) | 単一 (個人) |
| 評価期間 | 長期 (3-5 年 ROI) | 短期 (即時 emotional) |
| Layer 重要度 | Functional + Ease of doing biz が中心 | Functional + Emotional が中心 |
| 定量化方法 | TEI / NPV / payback | Conjoint / WTP survey |

### 2.3 Forrester TEI (Total Economic Impact) framework

Forrester Research の TEI は、ベンダー commission の "TEI study" の方法論として広く使われる。**4 軸**の構造:

| 軸 | 定義 | 例 |
|---|---|---|
| **Benefits** | 投資が生む価値 (productivity / cost reduction / customer satisfaction) | 営業 productivity 25% 向上 = ¥XM / year |
| **Costs** | 投資に必要な総費用 (license / implementation / training / ongoing operational) | License ¥XM + 実装 ¥YM |
| **Flexibility** | 将来の柔軟性 / 拡張可能性 (scalability / integration / customization) | 新ユースケース対応で +¥ZM optionality |
| **Risk** | 投資リスク (実装失敗 / セキュリティ / vendor lock-in) | 実装遅延の 確率 × 損失額 |

(出典: Forrester "The Total Economic Impact Methodology" / TEI policies)

#### 2.3.1 TEI の NPV 計算手順

1. **Customer profile** を確定 (業界 / 規模 / 業務領域)
2. **Investment** (year 0): license + implementation + training + integration cost
3. **Benefits** (year 1-3): probability-weighted (low / likely / high)
4. **Costs** (year 1-3): ongoing maintenance / support / additional license
5. **Flexibility**: optionality 価値を別途加算
6. **Risk adjustment**: 各 benefit を probability で discount
7. **NPV**: 3 年 discount (typical 10%)
8. **Payback months**: cumulative cash flow > 0 の月

#### 2.3.2 TEI report の典型構成 (本書の §10 mini case で再現)

```
1. Executive Summary
2. The Forrester TEI methodology
3. Customer Journey
   - Interviewed organizations
   - Composite organization profile
   - Investment objectives
4. Analysis of Benefits (probability-weighted)
   - Benefit 1: ... (Year 1-3 cash flow + risk-adjusted PV)
   - Benefit 2: ...
   - Total benefits PV
5. Analysis of Costs
   - Cost 1: License
   - Cost 2: Implementation
   - ...
6. Flexibility
7. Risks
8. Financial Summary (NPV / IRR / Payback / ROI)
```

#### 2.3.3 Risk adjustment の典型値

| 便益カテゴリ | Low (downside) | Likely (base) | High (upside) | Risk-adjusted |
|---|---|---|---|---|
| Hard cost reduction | 70% | 100% | 110% | base × 0.85 |
| Productivity uplift | 50% | 100% | 130% | base × 0.75 |
| Revenue uplift | 30% | 100% | 150% | base × 0.65 |
| Strategic optionality | 0% | 100% | 200% | base × 0.50 |

Risk-adjusted = (Low + 4 × Likely + High) / 6 (PERT 分布の期待値)、ただし Forrester の実務では各社が定数を持つ。

### 2.4 Driver Tree の組み立て手順 (本書 canonical)

実際に customer value を金額化するときの 6 ステップ:

1. **顧客プロファイルを固定** (業界 / 規模 / 役割)。複数 segment ある場合は segment 別に tree を組む
2. **4 軸 (§2.1) で大分類**: Cost reduction / Revenue uplift / Risk reduction / Strategic
3. **Bain elements (§2.2) で sub-driver を網羅** (B2B なら 40 / B2C なら 30 から該当を pick)
4. **TEI 4 軸 (§2.3) で Benefit / Cost / Flexibility / Risk を分けて計算**
5. **Driver ごとに probability + adoption + realization を掛けて effective 金額に**
6. **NPV / IRR / Payback (§3.4) で時系列に集約**

```
[顧客プロファイル]
    ↓
[4 軸大分類] ← §2.1
    ↓
[Bain elements で sub-driver 抽出] ← §2.2
    ↓
[TEI 4 軸で Benefit/Cost/Flexibility/Risk 分離] ← §2.3
    ↓
[各 driver の effective value (× adoption × realization)] ← §3.3
    ↓
[NPV / IRR / Payback] ← §3.4
    ↓
[WTP boundary 推定] ← §4.1
    ↓
[Pricing 決定] ← §4.2-4.5
```

---

## 3. Quantification Frameworks (定量化手法カタログ)

### 3.1 Hard ROI (直接金額換算)

直接 ¥ 単位で計算可能な便益。誤差が小さく、IC memo で defensible。

#### 3.1.1 Labor saving (人件費削減)

```
Labor saving (¥/year)
  = ΔHours × hourly rate × FTE × adoption rate × realization rate

ΔHours       : 1 人 1 週あたり削減される時間 (hr / week)
hourly rate  : 全社平均給与 / 年間労働時間 (例: ¥10M / 2,000hr = ¥5,000/hr)
FTE          : Full-Time Equivalent (人数)
adoption rate: 実際にツールを使う人の比率 (典型 50-80%)
realization  : 削減時間が実現する率 (典型 50-70%)
```

例 1: 営業 100 人 × 週 5 時間 × ¥5,000/hr × 50 週 × 70% adoption × 60% realization = **¥52.5M / year**

> **重要**: hourly rate に **fully-loaded cost** (給与 + 賞与 + 社保 + 福利厚生) を使うべきか、給与のみを使うべきかは IC memo で必ず明示する。fully-loaded cost は給与の 1.25-1.4 倍が典型。日本企業では法定福利費 + 通勤手当等で 1.15-1.2 倍が中央値。

#### 3.1.2 Revenue uplift (売上増)

```
Revenue uplift (¥/year)
  = baseline revenue × Δ(conversion or retention or cross-sell %) × period
    × adoption rate × realization rate × attribution rate
```

- **attribution rate** (寄与率): その施策単独でその revenue uplift が起きたかを示す (典型 40-70%)。複数施策が同時並行で動く場合、単独 attribution は 50% 以下に discount する

例 2: ¥10B baseline × 2%p conversion uplift × 100% period × 80% adoption × 60% realization × 60% attribution = **¥57.6M / year**

#### 3.1.3 Tool consolidation (ツール統合)

```
Tool consolidation saving (¥/year)
  = Σ (replaced tool annual cost) - new tool annual cost - migration one-time cost / N (years)
```

例 3: SaaS 統合
- 旧: Asana ¥5M + Slack ¥3M + Notion ¥2M + Confluence ¥4M = ¥14M / year
- 新: 統合プラットフォーム ¥8M / year + 移行費 ¥3M (一回限り、3 年で按分 = ¥1M / year)
- Net saving = ¥14M - ¥8M - ¥1M = **¥5M / year**

#### 3.1.4 Inventory / Working Capital reduction

```
Inventory reduction (¥)
  = ΔDIO (days) × COGS / 365

ΔDIO: Days Inventory Outstanding の減少日数
COGS: 年間売上原価
```

例 4: 製造業の在庫管理 SaaS
- 旧 DIO 60 日 → 新 DIO 50 日、Δ = -10 日
- COGS ¥10B / year
- Inventory reduction = 10 × ¥10B / 365 = **¥274M cash unlock** (一時的)
- 機会費用 (WACC 8%) = ¥22M / year (継続)

#### 3.1.5 Infrastructure cost (オンプレ → クラウド)

```
Inf cost saving (¥/year)
  = TCO_(on-premise) - TCO_(cloud) - migration cost / N
```

例 5: AWS migration
- On-premise: HW ¥30M (5 年償却 = ¥6M/year) + 運用 ¥40M + 電力 ¥10M + DC 賃貸 ¥20M = ¥76M / year
- AWS: ¥48M / year (Reserved Instance)
- Migration: ¥30M (3 年按分 = ¥10M/year)
- Net saving = ¥76M - ¥48M - ¥10M = **¥18M / year**

詳細は §10 Case 2 で再現。

### 3.2 Soft ROI (代理指標経由)

直接金額換算できないが、proxy 指標を介して金額化可能な便益。誤差大きく、IC memo では「assumption明示 + sensitivity」必須。

#### 3.2.1 NPS uplift と retention

Bain の研究 (Reichheld) で、**NPS が 12 ポイント上がると revenue が 1% 増加** する相関が観測される (業界平均)。これを使って NPS uplift を金額化:

```
Revenue uplift (¥/year, NPS 経由)
  = baseline revenue × ΔNPS / 12
```

例: NPS +24 → revenue +2% → ¥10B × 2% = ¥200M / year (理論値)

ただし NPS と revenue の causal relationship は弱いため、attribution rate を 40-60% で discount すべき。

#### 3.2.2 Employee engagement と productivity

Gallup の研究で、engagement 上位四分位の chamber は productivity が 18%、profitability が 23% 高い。これを使って engagement 改善を金額化:

```
Productivity uplift (¥/year, engagement 経由)
  = labor cost × 0.18 × Δengagement quartile (4 段階で +1)
```

例: 労働費 ¥1B × 0.18 × 1 quartile = ¥180M / year (理論値、causal は弱いため × 30-50%)

#### 3.2.3 Brand awareness と CAC 削減

Brand awareness が 上がると organic / referral 比率が上がり、paid CAC が下がる:

```
CAC saving (¥/year)
  = paid acquisition customers × Δ(% paid → organic) × paid CAC
```

例: 月間 1,000 顧客取得のうち paid 80% → 70%、paid CAC ¥50K
- 削減 paid 顧客 = 12,000 × 10% = 1,200 / year
- Saving = 1,200 × ¥50K = ¥60M / year

### 3.3 Probability-weighted ROI (実現率調整)

理論値に **adoption rate** (実際に使う %) と **realization rate** (理論値の何 % が実現するか) を掛けて effective 金額にする。本書の最重要原理の 1 つ。

```
Effective benefit
  = Theoretical benefit × adoption rate × realization rate

Theoretical: 100% の人が 100% 使い切ったときの便益
adoption  : 実際にどれだけの人がツールを使うか (典型 50-80%)
realization: 使ってもどれだけ理論値が実現するか (典型 50-70%)
```

例: 理論 labor saving 20% × adoption 70% × realization 60% = effective **8.4%**

#### 3.3.1 Adoption rate の典型値

| 業態 / 用途 | Adoption rate | 出典 / 理由 |
|---|---|---|
| 強制 (会計、CRM 必須運用) | 90-100% | 全社 mandate 運用 |
| 営業 SFA / CRM | 60-80% | 入力面倒で半数が形骸化 |
| 業務 SaaS (Asana / Notion 等) | 50-70% | チーム差が大きい |
| ナレッジ系 (Confluence 等) | 30-60% | passive 利用が多い |
| 学習 / トレーニング | 20-40% | 完了率が低い |
| AI assistant (Copilot 等) | 40-70% | 使う人と使わない人で二極化 |

#### 3.3.2 Realization rate の典型値

| 便益タイプ | Realization rate | 理由 |
|---|---|---|
| Hard cost saving (license 解約等) | 90-100% | 削減が明示的 |
| Time saving (自動化) | 50-70% | 削減した時間が他に流用される (Parkinson's law) |
| Productivity uplift | 40-60% | 因果分離が難しい |
| Revenue uplift | 30-50% | 複数施策 cluttering |
| Strategic optionality | 20-40% | 不確実性大 |

#### 3.3.3 IC memo での明示 (テンプレート)

```
[Benefit] = Theoretical ¥X × adoption Y% × realization Z% = Effective ¥W

例: Salesforce labor saving
= ¥125M (theoretical) × 70% adoption × 60% realization
= ¥52.5M / year (effective)

Sensitivity:
- Pessimistic: 50% × 50% = ¥31M
- Base:        70% × 60% = ¥52.5M
- Optimistic:  85% × 75% = ¥80M
```

### 3.4 NPV / IRR / Payback の計算 (Python)

時系列の cash flow を NPV / IRR / Payback で集約する。

```python
def customer_roi(
    annual_benefit: float,           # 年間便益 (¥)
    annual_cost: float,              # 年間 vendor pricing (¥)
    initial_implementation: float,   # 初期費用 (年 0、¥)
    years: int = 3,
    discount_rate: float = 0.10,
) -> dict:
    """3 年 horizon の NPV / IRR / Payback months 算出.

    Returns:
        {
          "npv": float,              # NPV (¥)
          "irr": float | None,       # IRR (年率)、計算不能なら None
          "payback_months": float,   # Payback months (interpolated)
          "roi_pct_total": float,    # 累計 ROI %
        }
    """
    # ----- Cash flows -----
    cf = [-initial_implementation]  # year 0
    for _ in range(1, years + 1):
        cf.append(annual_benefit - annual_cost)

    # ----- NPV -----
    npv = sum(c / (1 + discount_rate) ** t for t, c in enumerate(cf))

    # ----- IRR (Newton-Raphson, bracketed) -----
    def npv_at(r):
        return sum(c / (1 + r) ** t for t, c in enumerate(cf))

    irr = None
    lo, hi = -0.99, 10.0
    if npv_at(lo) * npv_at(hi) < 0:
        for _ in range(100):
            mid = (lo + hi) / 2
            v = npv_at(mid)
            if abs(v) < 1e-6:
                break
            if v * npv_at(lo) < 0:
                hi = mid
            else:
                lo = mid
        irr = (lo + hi) / 2

    # ----- Payback months (interpolated within year) -----
    cum = cf[0]
    payback_months = None
    for t in range(1, len(cf)):
        prev_cum = cum
        cum += cf[t]
        if prev_cum < 0 <= cum:
            # interpolate within year t
            frac = -prev_cum / cf[t]
            payback_months = (t - 1 + frac) * 12
            break

    # ----- ROI total -----
    total_in = -cf[0]
    total_out = sum(cf[1:])
    roi_pct_total = (total_out - total_in) / total_in * 100 if total_in else None

    return {
        "npv": npv,
        "irr": irr,
        "payback_months": payback_months,
        "roi_pct_total": roi_pct_total,
    }


# ----- Sample -----
if __name__ == "__main__":
    result = customer_roi(
        annual_benefit=80_000_000,        # ¥80M / year
        annual_cost=18_000_000,           # ¥18M / year (vendor price)
        initial_implementation=15_000_000,  # ¥15M one-time
        years=3,
        discount_rate=0.10,
    )
    print(result)
    # 期待値:
    # npv ≈ ¥139M
    # irr ≈ 4.0+ (極端に高い、benefit が大きいケース)
    # payback_months ≈ 3 ヶ月程度
    # roi_pct_total ≈ 1140%
```

#### 3.4.1 Discount rate の選び方

| 顧客タイプ | Discount rate (typical) |
|---|---|
| 大企業 (Investment-grade) | 7-9% (WACC) |
| 中堅企業 | 9-12% |
| スタートアップ (顧客側) | 12-20% |
| 上場 PE 保有 | 9-11% |

vendor 側で TEI を作るときは「顧客の WACC」を使う。一律 10% を使う Forrester study が多いが、本書では顧客タイプ別を推奨。

#### 3.4.2 Payback の合格ライン

| Stage / Sales motion | Payback target |
|---|---|
| SMB SaaS (PLG) | 6 ヶ月以内 |
| Mid-market SaaS | 12 ヶ月以内 |
| Enterprise SaaS | 18-24 ヶ月以内 |
| Hardware (耐久財) | 24-36 ヶ月以内 |
| Bio (製薬) | 5-7 年 |

Payback が target を超える場合、IC memo の "Pricing Thesis" で **追加根拠** (non-financial benefit / strategic value) を明示する必要がある。

#### 3.4.3 IRR の解釈

IRR は「NPV = 0 となる discount rate」、つまり「投資の年率リターン」。WACC を上回ればプロジェクトは acceptable。

| IRR | 評価 |
|---|---|
| < WACC | 不採用 |
| WACC - 1.5×WACC | Marginal、戦略的価値で補完すべき |
| 1.5×WACC - 3×WACC | 採用 |
| > 3×WACC | 強い採用 (典型的な SaaS 投資) |

ただし IRR は「再投資仮定」で歪むため、複数プロジェクト比較では **NPV を canonical** とし、IRR は補助指標として使う。

### 3.5 計算 worked example (Salesforce SFA case)

§10 Case 1 の 簡易版を本節で示す:

```
[Customer profile]
営業 100 人組織、ARR baseline ¥10B、現在 SFA なし

[Theoretical benefits]
1. Labor saving:
   100 人 × 5hr/week × ¥5,000/hr × 50 週 = ¥125M / year (theoretical)
   × adoption 70% × realization 60% = ¥52.5M / year (effective)

2. Revenue uplift:
   ¥10B × 2%p conversion = ¥200M / year (theoretical)
   × adoption 70% × realization 50% × attribution 60% = ¥42M / year (effective)

3. Risk reduction (商談紛失抑制):
   失注 ¥50M × 50% reduction × 80% probability = ¥20M / year

[Total effective benefit]
¥52.5M + ¥42M + ¥20M = ¥114.5M / year

[Costs]
- License: ¥18,000/seat/year × 100 = ¥1.8M / year (Sales Cloud Enterprise)
- 実装: ¥15M (one-time)
- Training: ¥5M (year 1)

[NPV calculation (3 yr, discount 10%)]
Year 0: -¥15M
Year 1: ¥114.5M - ¥1.8M - ¥5M = ¥107.7M
Year 2: ¥114.5M - ¥1.8M = ¥112.7M
Year 3: ¥114.5M - ¥1.8M = ¥112.7M

NPV = -15 + 107.7/1.1 + 112.7/1.21 + 112.7/1.331
    = -15 + 97.9 + 93.1 + 84.7
    = ¥260.7M

[Payback: 約 2 ヶ月]
[IRR: 700%+]
[ROI total: 1900%+]

[WTP upper boundary (gainsharing 30%)]
¥114.5M × 30% = ¥34.4M / year

[現状 Salesforce price]
¥1.8M / year
→ vendor take = 1.8/114.5 = 1.6% of customer ROI
→ 大幅 under-priced (expansion 余地大)
```

この例は **vendor 価格 ¥1.8M に対して顧客 ROI ¥114.5M** という極端なケースで、vendor 側の expansion (additional seat / module / Premium tier) で 5-10× の price 引き上げが可能な状態。実務でも Salesforce が CPQ / Marketing Cloud 等の cross-sell で expansion している背景はこの構造にある。

---

## 4. Value-Based Pricing — 価値ベース・プライシングの実装

### 4.1 WTP の理論と Gainsharing rule

#### 4.1.1 WTP の定義 (再掲)

WTP (Willingness To Pay) = 顧客が支払う最大金額。経済学的には indifference price。

```
WTP_upper = Customer ROI (positive range only)
WTP_lower = 0 (顧客 ROI が 0 以下なら買わない)
```

#### 4.1.2 Gainsharing rule of thumb

vendor が customer ROI を 100% 取り切ることは現実的でない。Reed Holden & Mark Burton『Pricing with Confidence』、Thomas Nagle & Georg Müller『The Strategy and Tactics of Pricing』の経験則として、

- **vendor take の典型レンジ: customer ROI の 20-30%**
- **顧客手元: 70-80% を残すことで再購入 / 推奨が生まれる**

ただしこれは **rule of thumb (経験則)** であり、業態 / 顧客 segment / 競合状況によって変わる:

| 状況 | Vendor take 比率 | 解釈 |
|---|---|---|
| 競合多数、commodity 化 | 5-15% | 価格競争で押し下げ |
| 標準的 B2B SaaS | 15-30% | gainsharing rule の中央値 |
| Sole-source / 特許 / 強い差別化 | 30-50% | プレミアム pricing |
| Mission-critical / lock-in 強い | 40-60% | 例: Bloomberg Terminal、ERP |
| 独占 / インフラ | 60-80% | 規制 (公益事業)、natural monopoly |

> **本書での扱い**: 一律 20-30% を base case とし、上記レンジを sensitivity range とする。IC memo では必ず「vendor take = X%」と明示する。

#### 4.1.3 Optimal Price = min(WTP, Competition × 1.2)

価格決定式 (本書 canonical):

```
Optimal price (¥/year)
  = min(
      WTP_upper,                       # 顧客 ROI × gainsharing %
      Competition_anchor × 1.2,        # 競合 + 20% premium 上限
      Cost × (1 + target_margin)       # 最低限の cost-plus floor
    )
```

3 つの上限のいちばん低いものが optimal price。これは「value > competition > cost」の優先順位を価格に反映させる。

### 4.2 Pricing Model 選定

8 つの典型 pricing model を比較:

| Model | 構造 | 適合条件 | 例 | 顧客の心理 |
|---|---|---|---|---|
| **Subscription (定額)** | 月 / 年で固定 ¥ | ROI 安定、月次予算化したい | Salesforce、Notion | 予測しやすい |
| **Usage-based** | 使用量 × 単価 | ROI が usage 比例 | AWS、Stripe、Twilio | スタート低リスク、成長で増 |
| **Outcome-based** | 結果 × % | ROI が 1 KPI に集中 | TikTok creator fund、Bloomberg trade | adoption リスク vendor 持ち |
| **Hybrid (base + usage)** | 固定 + 従量 | 両方の良さ | Snowflake (compute + storage)、Datadog | 安定 + 上振れ |
| **Per seat** | ユーザー数 × 単価 | 個人生産性向上 | Slack、Asana、Office 365 | 利用者数で透明 |
| **Per transaction** | 取引数 × 単価 | 取引価値ベース | PayPal、Visa、Wise | 1 件あたりが見える |
| **Tiered (Good/Better/Best)** | 段階的 feature | 顧客 segment が広い | Hubspot、Zoom | 選択肢で commit |
| **Freemium** | 無料 + 有料 tier | viral growth、 後の expansion | Dropbox、Slack 旧 | 無料で試せる |

#### 4.2.1 Subscription pricing の設計

```
Subscription price (¥/month/seat)
  = (Customer ROI / 12 / FTE) × gainsharing_pct
```

特徴:
- **予測可能性**: vendor 側 MRR / ARR forecast が立てやすい
- **Lock-in 効果**: 解約しない限り課金継続
- **限界**: 利用量が少ない顧客は割高に感じ、churn リスク

実装ポイント:
- Annual contract に discount (-10 to -20%) で long-term commitment を引き出す
- 月払 vs 年払で キャッシュフロー / churn risk のトレードオフ
- 自動更新条項 (auto-renewal) を契約に明記

#### 4.2.2 Usage-based pricing の設計

```
Total bill (¥/period)
  = Σ_(metric) {usage × unit_price}

例: AWS EC2
  = (running hours × hourly rate) + (storage GB-month × $/GB-month) + (data egress × $/GB)
```

特徴:
- **顧客側の land 容易**: 初期コストゼロでスタートできる
- **ROI 比例**: 成功するほど課金、 失敗時に課金少
- **Vendor 側の予測難**: forecast 立てづらい (usage の variance 大)
- **Cost-plus floor**: usage に対して vendor 側 cost も比例するため最低単価がある

実装ポイント:
- 「消費される metric」を 1-3 つに絞る (多すぎると顧客が混乱)
- Volume discount (§4.4) を tier 化
- Cost reserved 価格 (Reserved Instance) で予測可能性を顧客側に提供

#### 4.2.3 Outcome-based pricing の設計

vendor が「結果」に対して課金する。例:

| 例 | 結果指標 | Vendor take |
|---|---|---|
| Stripe Radar (不正検知) | 防いだ不正取引額 | 5-10% |
| Outreach (sales engagement) | 増えた商談数 | 一部 outcome-based pilot |
| AppLovin (mobile growth) | LTV uplift | 30-50% revshare |
| ICEYE (衛星 SAR insights) | 実 sense data delivery | per-image |

特徴:
- **顧客の心理的抵抗が低い**: 結果が出ないとお金を払わない
- **Vendor の adoption リスク大**: 結果が出ない期間は revenue ゼロ
- **Measurement infrastructure が必須**: 何を「結果」とするか、どう測るかが定義可能

実装条件 (3 つすべて満たす必要):
1. ROI が 1 KPI で測定可能
2. Attribution が clear (vendor 単独貢献が分離可能)
3. Measurement infra が顧客側に既に整っている (or vendor が提供)

> **失敗例**: 「広告の効果」を outcome-based で課金した DSP が、attribution 紛争で大量訴訟を抱えたケース (2010 年代後半に多発)

#### 4.2.4 Hybrid (base + usage) pricing の設計

```
Bill (¥/period)
  = Base subscription
    + Σ_(metric) {usage × unit_price (after included quota)}
```

例: Snowflake
- Base: edition price (Standard / Enterprise / Business Critical)
- Usage: compute (credit × $/credit) + storage ($/TB-month)
- 大半の B2B SaaS の expansion 構造に該当

特徴:
- 予測可能性 + 上振れ捕捉
- 顧客 size に対する均一性 (小口は base で割高、大口は usage で按分)

設計のコツ:
- Base に「典型 usage の 50-70%」を含める (overage で expansion)
- Overage 単価は base 単価より 1.5-2× 高くしない (心理的抵抗)

#### 4.2.5 Per seat pricing の落とし穴

「seat 数 × 単価」は単純で分かりやすいが、AI 時代に **崩れつつある** model:

- AI tool が 1 seat で複数人の仕事をこなす → vendor 側 take が減る
- 例: Github Copilot は 1 seat $19/月、ChatGPT Enterprise も seat 課金だが、heavy user と light user で realized value が 100× 違う
- Adobe / Salesforce は per seat を **per outcome** や **API call 課金** に部分移行中 (2024-)

代替案:
- Seat + usage hybrid (heavy user から overage を取る)
- Usage 単独 (API 課金)

### 4.3 Tier design (Good/Better/Best)

#### 4.3.1 3 tier の心理学 (Decoy effect)

3 つの選択肢を出すと、人は **真ん中**を選びやすい (decoy effect、Dan Ariely『Predictably Irrational』)。

```
| Tier   | Price       | Features              | 想定 % |
|--------|-------------|-----------------------|--------|
| Good   | ¥3K/seat/mo | Basic features        | 25%    |
| Better | ¥10K        | + Advanced + API      | 60%    | ← anchor 効果で誘導
| Best   | ¥30K        | + Enterprise + SSO    | 15%    |
```

設計のポイント:
- **Better tier に最も訴求する顧客 segment** を狙う (mid-market)
- Best tier は **anchor** (高さの基準点)。実際は売れなくても価値がある
- Good tier は「安い代替」を防ぐためのエントリー (downsell 阻止)

#### 4.3.2 Feature gating vs Limit gating

| Gating type | 例 | 特徴 |
|---|---|---|
| **Feature gating** | API access、SSO、Audit log、Priority support | 機能が tier 間で異なる、明確な差別化 |
| **Limit gating** | User 数 / API 呼び出し数 / Storage GB | 量の差別化、organic growth → upsell |

Best practice:
- Feature gating で **明確な segmentation** (Enterprise 機能 ≠ SMB)
- Limit gating で **organic upsell** (使うほど次の tier へ自然移行)
- 両者の組み合わせ:
  - Good: 5 user 限定 + Basic feature
  - Better: 50 user + Advanced feature
  - Best: 無制限 user + Enterprise feature

#### 4.3.3 Tier 間 WTP の segmentation

各 tier の WTP boundary を customer segment 別に推定 (§5.1 PSM 等で):

| Segment | WTP range (¥/seat/mo) | 推奨 tier |
|---|---|---|
| SMB (1-50 人) | ¥1K-5K | Good |
| Mid-market (50-500 人) | ¥5K-20K | Better |
| Enterprise (500+ 人) | ¥20K-100K+ | Best |

tier 間で **kinked demand curve** (折れ曲がった需要曲線) が観測される。各 segment が「適切な tier」を選んでいる証。

#### 4.3.4 Tier 移行率 (NRR への影響)

```
NRR_(driven by tier upgrade)
  = (% of customers who upgrade tier annually) × (avg uplift in ¥)
```

例: 年間 20% の customer が Good → Better へ upgrade、平均 uplift ¥7K/seat/mo
- 全 customer base の 20% × ¥7K × 12 = ¥16.8K/seat/year additional ARR
- これが NRR の core driver

### 4.4 Volume discount の数学的根拠

「数量 N 倍 → 価格 N 倍」は vendor 側の **marginal cost 低下分**を顧客に還元できない。一般則:

```
Discount % = log(volume_ratio) × elasticity_param

Volume ratio: 1 (基準) → 10 (10×) → 100 (100×)
Elasticity_param: 業態依存 (典型 5-15)
```

例 (elasticity = 10):
| Volume | Discount % | Effective unit price |
|---|---|---|
| 1× | 0% | ¥10K/seat |
| 5× | 16% (= log(5)×10) | ¥8.4K |
| 10× | 23% | ¥7.7K |
| 50× | 39% | ¥6.1K |
| 100× | 46% | ¥5.4K |

実務では **tier-based discount** で透明化:

```
| Volume     | Discount |
|------------|----------|
| 1-49 seats | 0%       |
| 50-99      | 10%      |
| 100-499    | 20%      |
| 500-999    | 30%      |
| 1,000+     | Custom   |
```

> **注意**: 平均化すると小口顧客が不公平 (小口だけで shouldering する構造) → tier 化で全顧客が予測可能

### 4.5 Land & Expand pattern

SaaS の standard motion。

```
[Year 1: Land]
- Initial price = WTP の 30-50% に設定
- 1 module / 1 team で start
- Time to first value < 30 日が target

[Year 2-3: Expand]
- Seat ↑、module ↑ で expansion
- Price/seat はあまり上げない (churn 主因のため)
- NRR 110-120% (中央値)、 130%+ (top quartile)
```

#### 4.5.1 Expansion の typical lever

| Expansion lever | 例 | 典型 uplift |
|---|---|---|
| Seat 追加 | 50 → 100 seat | 2× ARR |
| Module 追加 (cross-sell) | Sales Cloud → Service Cloud | +50-100% ARR |
| Tier upgrade | Better → Best | +50-200% per seat |
| Usage 増加 | API 100K → 1M calls | usage-based pricing で連動 |
| Geo / Subsidiary 拡大 | 1 国 → 多国 | 段階的 |

#### 4.5.2 NRR target (canonical)

公開 SaaS の NRR ベンチマーク (出典: ChartMogul SaaS Retention Report 2024-2025、Benchmarkit 2025、SaaS Capital):

| 評価 | NRR range |
|---|---|
| Concerning | < 100% |
| Median (B2B SaaS) | 100-110% |
| Good | 110-120% |
| Top quartile | 120-130% |
| Best-in-class | > 130% (Snowflake-class) |

> 過去の「NRR 130% が中央値」というのは誤解で、実際は **top decile クラス**。中央値は 105-115% (出典: ChartMogul N=2,100 venture-backed B2B SaaS、 2024)。`_terminology §6.4` の Snowflake NRR (FY24 Q4 = 131%、FY25 Q2 = 127%) はこの best-in-class カテゴリー。

#### 4.5.3 Price ↑ vs Seat ↑ の選択

価格上げは churn 主因。Expansion は **seat / module** で行うのが基本則:

| 戦略 | Churn 影響 | NRR 寄与 |
|---|---|---|
| Price 据置 + seat 増 | 低 (organic growth) | 高 |
| Price 微増 (+5-10%) + seat 増 | 中 | 中 |
| Price 大幅増 (+20%+) | 高 (renegotiation で離脱) | 短期高、中長期低 |

例: Salesforce は price を ほぼ据置にして、seat / cloud (Sales/Service/Marketing/Commerce) の cross-sell で expansion。

### 4.6 Outcome-based pricing の adoption リスクと条件

#### 4.6.1 失敗パターン

- **Attribution 紛争**: vendor 単独で「結果」が起きたか証明できない (例: AI sales tool で売上増、 でも market 自体が好調)
- **Adoption ゼロ**: 顧客が tool を使わない → outcome ゼロ → vendor revenue ゼロ
- **Gaming**: 顧客が結果指標を恣意的に低く報告 (e.g., 不正検知 saving を過少申告)

#### 4.6.2 Outcome-based pricing の成功条件

1. **Outcome の定義が客観的** (vendor / 顧客が一致して測定)
2. **Attribution が clean** (vendor 単独貢献が分離可能)
3. **Measurement infrastructure** が稼働 (vendor が提供 or 第三者証明)
4. **Vendor 側に runway** (revenue ゼロ期間を耐える資金力)

#### 4.6.3 部分 outcome-based (Hybrid)

100% outcome-based はリスク大すぎ → **base + outcome bonus** がより現実的:

```
Total bill = base subscription (¥X) + outcome bonus (¥Y × KPI uplift)
```

例: ある AI sales tool
- Base: $1K / seat / month (基本 SaaS)
- Outcome bonus: $5K per closed deal exceeding 10% over baseline forecast
- 基本 ARR 確保 + 上振れ捕捉

---

## 5. WTP 推定の実証手法 (PSM / Conjoint / Stated / Revealed)

### 5.1 Van Westendorp PSM (Price Sensitivity Meter)

Peter van Westendorp が 1976 年に提示した**4 質問法**。SaaS / consumer product の WTP 推定で世界的に使われる。

#### 5.1.1 4 つの質問

| 質問 | 内容 | Direction |
|---|---|---|
| Q1: Too cheap | 「いくらだと安すぎて品質が心配ですか？」 | 下限の下限 |
| Q2: Cheap (Bargain) | 「いくらだと安くてお買い得ですか？」 | 心地よい下限 |
| Q3: Expensive | 「いくらだと高いと感じますか？」 | 心地よい上限 |
| Q4: Too expensive | 「いくらだと高すぎて買いませんか？」 | 上限の上限 |

#### 5.1.2 Cumulative curve の作成

各質問の回答を **cumulative distribution** にプロット。X 軸 = 価格、Y 軸 = 累積 % of respondents:

- Q1 (Too cheap): 「この価格 **以下** で too cheap と回答」 の累積 % → **降順** で plot (高価格で 0%、低価格で 100%)
- Q2 (Cheap): 「この価格 **以下** で cheap と回答」 → **降順**
- Q3 (Expensive): 「この価格 **以上** で expensive と回答」 → **昇順**
- Q4 (Too expensive): 「この価格 **以上** で too expensive と回答」 → **昇順**

> 標準 PSM では Too cheap / Cheap の 2 曲線を invert (1 - cumulative) して表示。これで 4 曲線が交差する。

#### 5.1.3 4 つの key price points

4 曲線の交点が WTP の重要 price points:

| Point | 定義 | 解釈 |
|---|---|---|
| **PMC (Point of Marginal Cheapness)** | Too cheap × Expensive の交点 | 下限 (これ以下で品質懸念が expensive 懸念を上回る) |
| **PME (Point of Marginal Expensiveness)** | Too expensive × Cheap の交点 | 上限 (これ以上で価格懸念が bargain 印象を上回る) |
| **OPP (Optimal Price Point)** | Too cheap × Too expensive の交点 | 最適価格 (rejection が両側で等しい) |
| **IPP (Indifference Price Point)** | Cheap × Expensive の交点 | 心地よい価格 (cheap と expensive が等しい) |

```
Acceptable price range = PMC ~ PME
Optimal price          = OPP (中央値的な点)
Median price (felt)    = IPP (顧客の心理的中央値)
```

#### 5.1.4 PSM mini case (B2B SaaS)

仮想 N=200 の SaaS pricing 調査:

| Price (¥/seat/mo) | Too cheap % | Cheap % | Expensive % | Too expensive % |
|---|---|---|---|---|
| 1,000 | 65% | 90% | 5% | 1% |
| 3,000 | 30% | 70% | 15% | 5% |
| 5,000 | 10% | 50% | 35% | 12% |
| 7,000 | 3% | 30% | 55% | 25% |
| 10,000 | 1% | 12% | 75% | 50% |
| 15,000 | 0% | 5% | 90% | 75% |
| 20,000 | 0% | 1% | 95% | 90% |

交点の概算 (curve 交差から):
- PMC ≈ ¥3,000 (Too cheap × Expensive 交点)
- PME ≈ ¥10,000 (Too expensive × Cheap 交点)
- OPP ≈ ¥6,500 (Too cheap × Too expensive 交点)
- IPP ≈ ¥5,500 (Cheap × Expensive 交点)

**結論**: Acceptable range ¥3K-¥10K、optimal ¥5.5K-¥6.5K。実際の price を ¥7K に設定すれば「やや高め」だが acceptable。¥10K 超で 50% が too expensive と判定 → 上限。

#### 5.1.5 PSM の限界と補強

**限界**:
- Stated preference (申告ベース) のため bias あり (実際の購入行動とずれる)
- 高 ASP (¥1M+) の B2B では「価格感覚」が掴みにくく precision 落ちる
- New category (前例ない製品) は anchor がなく、回答が広く散らばる

**補強策**:
- Newton Miller-Smith extension: 「この価格で買うか？」を追加聴取し、purchase probability curve も併記
- Conjoint (§5.2) と併用して triangulate
- A/B test (§5.4) で実購入で検証

#### 5.1.6 PSM の実装 Tips

- N≥150 推奨 (segment 別 cut で statistical power 確保のため)
- 質問順序: Too expensive → Expensive → Cheap → Too cheap (anchor 順)
- 開放回答 (numeric input) > 選択肢 (price tier 提示は anchoring bias 強い)
- 業態 / segment 別に cut し、それぞれで curve を引く

### 5.2 Conjoint Analysis (コンジョイント分析)

#### 5.2.1 概念

Conjoint = "considered jointly"。複数機能 × 複数価格の **profile cards** を顧客に提示し、相対的選好を取得。回帰分析で各 attribute の **partial utility** (=寄与度) を分解。

#### 5.2.2 設計手順

1. **Attribute 選定**: 価格 + 重要 feature 5-10 個 (例: API access、SSO、SLA、Storage GB)
2. **Level 設定**: 各 attribute の選択肢 (例: 価格 ¥5K / ¥10K / ¥20K / ¥40K)
3. **Profile card 作成**: 直交設計 (orthogonal design) で全組合せから effective subset を抽出
4. **Survey**: 顧客に「どちらを選びますか？」(choice-based) または rank/rate
5. **Regression**: Logit / Probit / Hierarchical Bayes (HB) で partial utility 推定
6. **Output**: feature 別 WTP

#### 5.2.3 Output: Feature 別 WTP

```
WTP for Feature X = Partial utility of Feature X / Partial utility of $1 of price
```

例 (B2B SaaS):
| Feature | Partial utility | WTP (¥/month/seat) |
|---|---|---|
| API access | +0.8 | ¥3,200 |
| SSO | +0.6 | ¥2,400 |
| 99.9% SLA | +0.5 | ¥2,000 |
| Audit log | +0.3 | ¥1,200 |
| Priority support | +0.2 | ¥800 |

これで **Best tier に SSO + API + SLA + Audit + Priority を入れる** justify となり、価格 ¥10K の合計 WTP ≒ ¥9.6K で正当化。

#### 5.2.4 Conjoint の業界標準

- **Sawtooth Software** (米): 業界標準ツール、HB 推定実装
- **Qualtrics**: Conjoint module を統合提供
- **N≥200** 推奨 (segment 別 cut のため N=400+ が望ましい)

#### 5.2.5 Conjoint の限界

- **Cognitive load**: 質問者が card 8-15 個比較で判断疲れ → trade-off の精度落ちる
- **Attribute 過多**: 7+ attribute で精度落ちる → 重要 5-7 attribute に絞る
- **Hypothetical bias**: 申告と実購入のずれ (Stated vs Revealed)

### 5.3 Stated preference (直接インタビュー)

#### 5.3.1 単純な直接質問

「この機能でいくら払いますか？」型のインタビュー。

**Bias 要因**:
- **Social desirability**: 高めに答える (見栄)
- **Anchoring**: 調査者が示した数字に引きずられる
- **Strategic answer**: 安く答えたら安くなると期待
- **Hypothetical bias**: 仮想シナリオで高めに見積もる

#### 5.3.2 改善された stated preference

「Mom Test」(`product-strategy:mom-test` skill 参照) の原則を適用:

- 「将来買いますか」ではなく「**過去 1 年で類似製品にいくら払いましたか**」を問う
- 開放回答で先に anchor をもらう (「いくらが妥当と思いますか」を先)
- 後で「この価格 (¥X) なら払いますか」型 (Yes/No) で検証

#### 5.3.3 Survey design の checklist

- [ ] 複数 segment を cut (size / industry / role)
- [ ] N≥100 per segment (statistical power)
- [ ] Open question (numeric input) を中心、選択肢は補助
- [ ] Anchoring を避ける (調査者が前提値を出さない)
- [ ] 結果を Conjoint / PSM / Revealed で triangulate

### 5.4 Revealed preference (実取引データ)

過去取引から price elasticity (価格弾力性) を測定する。最も bias なし、最強の手法。

#### 5.4.1 Price elasticity の定義

```
ε = (ΔQ / Q) / (ΔP / P)

ε > 1: elastic (値下げで売上増)
ε < 1: inelastic (値上げで売上増、ただし absolute Q は減る)
ε = 1: unit elastic (revenue 一定)
```

#### 5.4.2 業態別の price elasticity (典型値)

| 業態 / 製品 | Elasticity | 解釈 |
|---|---|---|
| 必需品 (食品、医薬品) | 0.2-0.5 | 強 inelastic、値上げ余地 |
| 標準 SaaS | 0.5-1.5 | 中位、価格 / 量 trade-off |
| Luxury 製品 | 1.5-3 | 強 elastic、値上げで売上減 |
| Commodity (汎用品) | 3+ | 競合 substitute 多、価格競争 |

#### 5.4.3 A/B test で elasticity 測定

最も clean な手法:

1. 全 customer を random に 50/50 で split (control / treatment)
2. Treatment group に新価格を提示 (例: +10%)
3. 一定期間 (3-6 月) の conversion / churn / ARPU を比較
4. Elasticity を回帰

**Legal 注意**: Same customer に **異なる価格を提示する**ことは差別禁止法 (米 / EU / 日本 競争法) に触れる場合あり。実装は:
- New customer のみ A/B (既存顧客を変更しない)
- A/B test 期間限定の promotional pricing として明示
- 法務確認必須 (特に B2B Enterprise contract で先例化リスク)

#### 5.4.4 自然実験 (Natural experiment) からの推定

A/B test できない場合の代替:

- **競合 price 変更時**: 自社 churn / new logo の変化を測る
- **市場 shock**: 為替 / 規制で価格が外的に変わったとき
- **Geo experiment**: 地域差 (e.g. 米 vs EU pricing) で elasticity 推定

### 5.5 4 手法の triangulation

実務では **複数手法を併用** して WTP を triangulate する:

| 手法 | 強み | 弱み | コスト |
|---|---|---|---|
| **PSM** | 簡便、N=150-300 で実施可能 | Stated bias、新カテゴリ弱い | 低 (¥1-3M) |
| **Conjoint** | Feature 別 WTP 分解 | Cognitive load、attribute 数限界 | 中 (¥5-15M) |
| **Stated direct** | 質的 insight | Bias 大 | 低 (¥0.5-2M) |
| **Revealed (A/B)** | 最も accurate | 既存顧客必要、legal risk | 中-高 (data infra 必要) |

**推奨手順**:
1. Stated direct で **rough range** (¥X-Y) を取る (10-20 件 interview)
2. PSM で **distribution** を取る (N=200 survey)
3. Conjoint で **feature 別 partial utility** を取る (N=300+ survey)
4. Revealed (A/B) で **実価格弾性** を測定
5. 4 手法の結果を triangulate → final WTP boundary

---

## 6. 業態別 Customer Value 計算 Template (7 業態 × 4 stage)

本章は **7 業態** (SaaS B2B / Marketplace / Fintech / D2C consumer / Hardware / Bio / AI Foundation) × **4 stage** (Pre-Seed / Seed-Series A / Series B-C / Pre-IPO+) の合計 28 cell に対する customer value template。

### 6.1 SaaS (B2B)

#### 6.1.1 Customer Value 計算式

```
Customer Value (¥/year, B2B SaaS)
  = Σ_segment {
      Labor saving       (FTE × ΔHours × HourlyRate × adoption × realization)
      + Revenue uplift   (baseline × ΔConversion × period × adoption × realization × attribution)
      + Risk reduction   (downtime_cost × ΔAvailability + compliance_violation_avoidance)
      + Tool consolidation (Σ replaced tool cost - new license cost)
    } - implementation_cost - training_cost - switching_cost - ongoing_admin_cost

WTP_upper      = Customer Value × 0.20-0.30 (gainsharing)
Optimal_price  = min(WTP_upper, competition_anchor × 1.2)
```

#### 6.1.2 Stage 別 WTP / Pricing 推奨

| Stage | Customer profile | Pricing model | WTP capture | NRR target |
|---|---|---|---|---|
| **Pre-Seed** | Early adopter (10-50 logo) | Subscription (Annual contract -20%) | 5-10% (under-priced で land) | N/A (logo 重視) |
| **Seed-Series A** | SMB / Mid (50-500 logo) | Subscription + per-seat | 10-15% | 100-110% |
| **Series B-C** | Mid + Enterprise mix | Hybrid (base + usage) + Tier | 15-25% (gainsharing 中央値) | 110-120% |
| **Pre-IPO+** | Enterprise 中心 (100+ Fortune 500) | Enterprise contract + Outcome bonus | 25-35% (premium pricing) | 120-130% (best-in-class) |

#### 6.1.3 Mini case (Salesforce SFA、§3.5 / §10 Case 1 で詳細)

- 営業 100 人組織、ARR baseline ¥10B
- Theoretical labor saving: ¥125M / year → effective ¥52.5M / year
- Theoretical revenue uplift: ¥200M / year → effective ¥42M / year
- Total effective benefit: ¥114.5M / year
- WTP upper (gainsharing 30%): ¥34.4M / year
- 現状 Salesforce list price: ¥1.8M / year → significant under-pricing
- Expansion 余地: 5-10× via additional seat / Service Cloud cross-sell

### 6.2 Marketplace (B2C / B2B 両側)

#### 6.2.1 Customer Value (両側別 / Take rate ceiling)

Marketplace は **buyer / seller の double-sided** で、それぞれの value を計算:

```
Seller value (¥/year)
  = Revenue from marketplace × marketplace_premium_factor
    - alternative cost (own e-commerce / direct sales channel)
    + Demand access value (買い手リーチ拡大)

Buyer value (¥/year)
  = Time saving + Selection value + Trust value (rating / dispute resolution)
    - Direct alternative の cost (1:1 negotiation)

Take rate ceiling (% of GMV)
  = (Seller value + Buyer value) / GMV × gainsharing_ratio
```

#### 6.2.2 業界 take rate benchmarks

| Marketplace | Take rate | 解釈 |
|---|---|---|
| Etsy | 6.5% + transaction fees | 売主低 friction、自由出店 |
| eBay | 10-13% (final value fee) | 中間、auction 機能 |
| Amazon (3P seller) | 8-15% (referral) + FBA fees | 高、fulfillment 込み |
| Airbnb | host 3% + guest 14% (≒ 17% total) | 中、guest が多く負担 |
| Uber / Lyft | 25-30% (driver から) | 高、matching + dynamic pricing |
| App Store / Play Store | 15-30% | 最高、 platform lock-in |
| StockX / GOAT | 9.5-12% (seller) | 中、authentication value |
| Mercari | 10% (seller) | 中央値的 |

#### 6.2.3 Stage 別 Pricing 推奨

| Stage | Take rate strategy | Subsidy direction |
|---|---|---|
| Pre-Seed (chicken-and-egg) | Take rate 0-5% (bootstrap supply / demand) | 両側 subsidize |
| Seed-Series A | 5-10% (片側 subsidize 継続) | 弱い側 subsidize |
| Series B-C | 10-20% (sustainable economics へ) | 規模で eliminate |
| Pre-IPO+ | 15-25% (mature take rate) | 不要 |

> Marketplace は **early stage で take rate 0** から始まる場合が多い (a16z "Marketplace 100" 研究)。GMV 達成後に段階的に take rate を上げる。

#### 6.2.4 Mini case: B2B Marketplace (建設資材)

- 建設会社 (buyer) の従来購買 cost: 担当者 1 人 × ¥6M/year + 紙の RFQ process
- Marketplace 経由で: 担当者 0.5 人化 + RFQ 自動化 + 価格透明性で原価 5% 低下
- Seller value: 営業所マージン縮減を flat take rate で
- Take rate landed: GMV の 8% (buyer + seller 合算)

### 6.3 Fintech (Lending)

#### 6.3.1 Customer Value (NIM の合理性)

```
Borrower value (¥/year) [SMB lending case]
  = Speed value (即日承認 vs bank 30 日)
    × time-to-cash criticality factor
  + Access value (bank 与信通らない顧客のみ)
    × credit access criticality
  + Convenience value (オンライン申請、書類不要)
  - Interest rate premium over alternative
```

```
NIM ceiling (lending rate spread)
  = Σ above / Loan principal × gainsharing
```

#### 6.3.2 業界 lending rate / NIM benchmarks

| Lender type | Rate (USD market) | NIM (over funding cost) |
|---|---|---|
| Bank prime SMB loan | Prime + 1-3% (~ 6-9%) | 2-3% |
| SBA-backed loan | Prime + 1-2% | 2-2.5% |
| Online SMB lending (Bluevine, Kabbage) | 12-25% APR | 5-10% |
| Merchant cash advance | 30-100% APR | 15-30% |
| BNPL (Klarna, Affirm) | 0-30% APR | 4-15% (merchant fee 込み) |

#### 6.3.3 Stage 別 Pricing 推奨

| Stage | Underwriting source | NIM target |
|---|---|---|
| Pre-Seed | Manual + 100% balance sheet 自社負担 | 高 (15%+) for risk premium |
| Seed-Series A | ML model α version + warehouse line | 8-12% |
| Series B-C | ML model + securitization + ABS | 5-8% |
| Pre-IPO+ | Diversified funding + bank partnership | 3-5% (mature) |

#### 6.3.4 Mini case: SMB lending (¥10M loan)

- Borrower (SMB 飲食店、bank 与信通らず): 即時資金で月商 ¥1M → ¥3M (cash flow 改善)
- 12 ヶ月で利益 +¥10M
- 競合 cost (private lender): rate 30%
- 自社 fintech rate: 18%
- Borrower 残便益: ¥10M - ¥1.8M (interest) = ¥8.2M
- Vendor take = 18%、他社 30% を考えると、 12% が「速度 + 与信 access」の対価

### 6.4 D2C consumer

#### 6.4.1 Customer Value (BPI / Brand premium)

D2C は B2C なので、便益が **emotional + functional** の混合。Bain B2C 30 elements (§2.2.2) を flexibly 適用。

```
WTP (D2C consumer)
  = Competitive anchor (alternative product price)
    + Functional delta (機能の差) × WTP_per_attribute
    + Emotional delta (ブランド / デザイン)
    + Convenience (DTC delivery、subscription 自動化)
    - Switching cost (慣れ親しんだ既存商品から)
```

#### 6.4.2 Brand premium の典型

| Category | Brand premium over generic | 例 |
|---|---|---|
| Apparel (commodity) | 50-200% | Patagonia、 Lululemon |
| Apparel (luxury) | 500-2000% | Hermès、Prada |
| Electronics | 30-100% | Apple、Tesla、Dyson |
| Food / Beverage | 20-100% | Whole Foods、craft beer |
| Beauty / Personal care | 100-500% | Glossier、Drunk Elephant |
| Furniture | 50-200% | Herman Miller、Casper |

#### 6.4.3 Stage 別 Pricing 推奨

| Stage | Customer | Pricing strategy |
|---|---|---|
| Pre-Seed | Early adopter / cult fan | Premium pricing (early signal of quality) |
| Seed-Series A | Lookalike audience | Premium 維持、subscription option 追加 |
| Series B-C | Mainstream pivot | 段階的 SKU diversification (Good/Better/Best) |
| Pre-IPO+ | Mass market | Mass + Premium 二層化 |

#### 6.4.4 Mini case: Premium 寝具ブランド

- Mattress competitor (IKEA generic): ¥30K
- D2C premium mattress: ¥150K
- Brand premium = ¥120K (= 5×)
- 内訳: Functional (memory foam quality) ¥30K + Emotional (sleep quality narrative) ¥40K + Convenience (100 day trial、free shipping) ¥30K + Brand (Casper-class 認知) ¥20K
- WTP estimation: PSM survey で IPP ≈ ¥140K、OPP ≈ ¥160K → ¥150K は acceptable range の中央

### 6.5 Hardware (TCO comparison)

#### 6.5.1 Customer Value (TCO 比較)

Hardware (耐久財) は **5-7 年 TCO** で比較するのが基本。

```
TCO_(years N) = Initial cost
              + Σ_year {Maintenance + Operating + Energy + Downtime cost}
              + Upgrade / Replacement cost
              - Resale value at year N

WTP_upper (Hardware) = TCO_(alternative) - TCO_(this product)
```

#### 6.5.2 Stage 別 Pricing 推奨

| Stage | Customer | Pricing strategy |
|---|---|---|
| Pre-Seed | Beta / lighthouse customer | Cost-plus + 戦略 discount |
| Seed-Series A | Early commercial logo | Value-based on TCO comparison、bundled service |
| Series B-C | Mainstream | Tier (Good/Better/Best) + Service contract |
| Pre-IPO+ | Diversified verticals | Premium + Service + Software hybrid (e.g., HaaS) |

#### 6.5.3 Mini case: 工作機械

- 競合 (国内中堅) 工作機械: ¥150M、メンテ年 ¥10M、故障 downtime 年 1 週間
- 自社新型: ¥200M、メンテ年 ¥6M、故障 downtime 年 2 日
- 5 年 TCO 比較:
  - 競合: 150 + 50 + 5 × ¥5M (生産 loss / week) = ¥225M
  - 自社: 200 + 30 + 5 × ¥1.4M = ¥237M
- WTP boundary: ¥225M (competitor TCO)
- 自社価格 ¥200M は acceptable、ただし 5 年で ¥12M extra (¥237 - ¥225)
- Justify には maintenance ¥4M/year × 5 年 = ¥20M discount を offer or service contract で flatten

### 6.6 Bio (Drug / Medical Device)

#### 6.6.1 Customer Value (QALY / ICER)

医療では便益を **QALY** (Quality-Adjusted Life Year) で表現する。

```
QALY = Years of life × Quality factor (0 = death, 1 = perfect health)

ICER (Incremental Cost-Effectiveness Ratio)
  = (Cost_(new drug) - Cost_(comparator)) / (QALY_(new) - QALY_(comparator))

WTP_(payer ceiling) = ICER threshold (¥/QALY)
```

#### 6.6.2 ICER threshold (国別)

| 国 / 機関 | Threshold (¥/QALY equivalent) | 注意 |
|---|---|---|
| UK NICE | £20K-30K (≒ ¥3.7M-5.5M) | 厳格 (cost-effectiveness 評価) |
| US ICER (institute) | $100K-150K (≒ ¥15M-22.5M) | Reference ベンチマーク、決定権なし |
| 日本 C2H (HTA pilot) | ¥5M (基準)、¥7.5M (重症)、¥10M (希少疾患) | 2019- 公的価格調整に運用 |
| 豪 PBS | A$45-75K | 厳格 |
| カナダ CADTH | C$50K-100K | Province 差あり |

> これらは **approximate / jurisdiction-dependent** であり、年次で変動する (出典: ICER, NICE, C2H 各機関 2024-2025 公開資料)。希少疾患 / orphan drug では threshold 緩和される。

#### 6.6.3 Stage 別 Pricing 推奨

| Stage | Phase | Pricing strategy |
|---|---|---|
| Pre-Seed (preclinical) | Research only | N/A |
| Seed-Series A (Phase 1) | Safety study | N/A、 lock licensing terms with payer |
| Series B-C (Phase 2-3) | Efficacy data | ICER simulation で WTP ceiling 推定、 pricing strategy 確立 |
| Pre-IPO+ (approved / commercial) | Launch | Country-specific pricing、 patient access program、 risk-sharing |

#### 6.6.4 Mini case: 抗がん剤

- 新薬: ¥300M / patient / year
- Comparator (既存 chemo): ¥50M / patient / year
- QALY uplift: 1.2 / year (生存期間延長 1 年 + QoL 改善)
- ICER = (300 - 50) / 1.2 = **¥208M / QALY**
- 日本 C2H threshold ¥5M (希少疾患 ¥10M でも) を大幅超過 → pricing 引下げ要因
- 引下げ後価格: 通常 30-50% reduction、または risk-sharing scheme (応答した患者のみ課金)
- Recalculation: ¥150M / patient × 60% real-world response rate = effective ¥90M
- Recalculated ICER = (90 - 50) / 1.2 = ¥33M / QALY → 希少疾患 threshold 範囲内

### 6.7 AI / Foundation Model

#### 6.7.1 Customer Value (Token / Compute monetization)

AI / Foundation model API は**消費単位** (token、compute hour、image など) で課金。

```
Customer Value (¥/year) [LLM API]
  = labor cost saved × productivity uplift × adoption × realization
  - API consumption cost

Per-token WTP
  = (labor cost / token consumed at standard usage) × gainsharing %
```

#### 6.7.2 LLM API pricing benchmark (2025 中央値)

| Provider / Model | Input ($/1M tokens) | Output ($/1M tokens) | 用途 |
|---|---|---|---|
| Anthropic Claude Opus 4.7 | ~$15 | ~$75 | Premium |
| Anthropic Claude Sonnet | ~$3 | ~$15 | Mid |
| OpenAI GPT-4o | ~$2.5 | ~$10 | Standard |
| OpenAI GPT-4o mini | ~$0.15 | ~$0.60 | Light |
| Google Gemini Pro | ~$1.25 | ~$5 | Mid |
| Open source (Llama via fireworks) | ~$0.20 | ~$0.20 | Cost-sensitive |

(各社 公開 価格、2025-04 時点。実値は変動、本書では trend value として提示。)

#### 6.7.3 Stage 別 Pricing 推奨

| Stage | Strategy |
|---|---|
| Pre-Seed | Open API、free tier、 land 重視 |
| Seed-Series A | API + base subscription tier、batch API discount |
| Series B-C | Enterprise contract、 volume discount、 fine-tuning option |
| Pre-IPO+ | 完全 enterprise (private deployment、SLA、custom model) |

#### 6.7.4 Mini case: AI sales tool (white collar productivity)

- 顧客: 1,000 名の営業組織
- 1 人あたり saved time: 1 hr/day (調査 / メール作成 / proposal draft)
- Hourly rate (fully-loaded): ¥4,000
- Annual saving (theoretical): 1,000 × 1 × 200 work days × ¥4,000 = ¥800M / year
- adoption 60% × realization 70% = effective **¥336M / year**
- WTP upper (gainsharing 30%): ¥100M / year
- 現状 SaaS list price: ¥50K/seat/year × 1,000 = ¥50M / year → significant under-pricing
- Expansion 余地: tier upgrade or AI-specific add-on で ¥80-100M target

### 6.8 業態 × Stage 別 Quick Reference Matrix

| 業態 \ Stage | Pre-Seed | Seed-Series A | Series B-C | Pre-IPO+ |
|---|---|---|---|---|
| **SaaS B2B** | Subscription, 5-10% take | Subscription/Seat, 10-15% take | Hybrid+Tier, 15-25% take | Enterprise, 25-35% take |
| **Marketplace** | Take rate 0-5% | 5-10% | 10-20% | 15-25% |
| **Fintech** | Manual UW, NIM 15%+ | ML α + warehouse, NIM 8-12% | ML + ABS, NIM 5-8% | Diversified, NIM 3-5% |
| **D2C** | Premium pricing | Premium + subscription | Tier (Good/Better/Best) | Mass + Premium 二層 |
| **Hardware** | Cost-plus + 戦略 discount | TCO-based + service | Tier + Service contract | Premium + HaaS |
| **Bio** | N/A (preclinical) | N/A (Phase 1) | ICER simulation | Country-specific + risk-sharing |
| **AI Foundation** | Free tier + API | API + base sub, batch discount | Enterprise + volume | Private deployment + custom |

---

## 7. Modeling 反映方法 — 17 sheet xlsx への組み込み

### 7.1 02_Revenue sheet への price 入力

`02_Revenue` の price field (= 単価部分) には、本 reference の WTP analysis を **Note (cell comment)** で記録する。

#### 7.1.1 Cell comment の構造 (canonical)

```
Cell B5 (Subscription price = ¥10,000/月/seat) の Note:

[Pricing Thesis - per 18_customer_value_and_pricing.md]
- Customer ROI median (effective): ¥80M/year (per 100-FTE org)
- WTP analysis (PSM, N=200):
    PMC = ¥3,000, IPP = ¥9,000, OPP = ¥11,000, PME = ¥15,000
- Gainsharing target: 25% of customer ROI = ¥20M = ¥17K/seat/mo
- Competition anchor (Salesforce, Hubspot): ¥8K-12K/seat/mo
- Current price ¥10K/seat/mo: within optimal range (IPP-OPP)
- Expansion path: Year 1 ¥10K → Year 3 ¥15K via tier upgrade
- Source: PSM survey 2025-Q1, conjoint Sawtooth N=300
```

#### 7.1.2 Driver の追加 row

`11_KPI_Dashboard` に以下の input row を追加 (`15_input_schema.md §2` で formal definition):

| Field | Type | 例 | 説明 |
|---|---|---|---|
| `customer_roi_annual` | ¥/year | 80,000,000 | 1 customer / 1 year の effective ROI |
| `gainsharing_pct` | % | 0.25 | vendor take % of customer ROI |
| `wtp_psm_opp` | ¥ | 11,000 | PSM の OPP (price/seat/mo or per unit) |
| `wtp_psm_pme` | ¥ | 15,000 | PSM の PME (上限) |
| `competition_anchor` | ¥ | 10,000 | 競合中央値 |
| `tier_better_uplift` | % | 2.5 | Better tier の Good 比 uplift |

これらの input から `02_Revenue` の price field を formula で計算:

```
Price (B5) = MIN(
   customer_roi_annual / 12 / FTE × gainsharing_pct,   ← WTP ceiling
   competition_anchor × 1.2,                            ← Competition + 20% premium
   wtp_psm_pme                                          ← PSM upper bound
)
```

### 7.2 11_KPI_Dashboard への新 KPI

`11_KPI_Dashboard` に以下の KPI を追加:

| KPI | 計算式 | 合格ライン | 出典 reference |
|---|---|---|---|
| **Avg Customer ROI %** | (customer_value - vendor_price) / vendor_price × 100 | 200%+ | §3 |
| **Avg Payback (months)** | NPV-positive crossover months | < 12 (B2B SaaS) | §3.4.2 |
| **Pricing realization** | Actual ARPU / List price × 100 | > 80% | §7.1 |
| **Net Pricing Power** | ARPU growth (YoY) / inflation rate | > 1 | §4.5 |
| **WTP capture %** | Actual price / WTP_upper × 100 | 60-80% | §4.1.2 |
| **Vendor take of customer ROI** | Vendor price / Customer ROI × 100 | 15-30% | §4.1.2 |

### 7.3 13_IC_Memo への "Pricing Thesis" section

IC memo の標準構成 (`08_investment_thesis.md §17` ベース) に **新 section** を追加:

```
[Section X. Pricing Thesis] (新設)

X.1 Customer Value 中央値
- Per typical customer (segment: Mid-market 100-500 FTE)
- Cost reduction: ¥XM / year (FTE × hour × rate × adoption × realization)
- Revenue uplift: ¥YM / year
- Risk reduction: ¥ZM / year
- Total effective: ¥WM / year

X.2 WTP Boundary
- Method: PSM (N=200) + Conjoint (N=300) + Direct interview (N=20)
- PMC / IPP / OPP / PME: ¥A / B / C / D
- Triangulated WTP upper: ¥E / customer / year

X.3 Our Take
- Our list price: ¥F / customer / year
- Realized ARPU: ¥G (= F × pricing_realization)
- vendor take % of customer ROI: G/W = H% (target 15-30%)

X.4 Pricing Model 選定 Rationale
- Subscription / Usage / Hybrid / Outcome から: [選択]
- 選定理由: [reference §4.2 から]

X.5 Tier Design
- Good (¥X1, target SMB): [feature list]
- Better (¥X2, target Mid): [feature list, anchor]
- Best (¥X3, target Enterprise): [feature list]
- 想定 mix: 25% / 60% / 15%

X.6 Land & Expand Path
- Year 1 land price: ¥L (= WTP × 30-50% で friction 低)
- Year 3 expansion: ¥E (= ¥L × 2-3× via seat / module / tier upgrade)
- NRR target: 110-120% (B2B SaaS top quartile)

X.7 Sensitivity Range
- Pessimistic (WTP -20%): pricing -10%, ARR -X%
- Base: 上記
- Optimistic (WTP +20%): pricing +10%, ARR +X%
```

### 7.4 09_DCF § Sensitivity への WTP 軸追加

`09_DCF § Sensitivity` の matrix に **WTP boundary** を変数として追加:

```
[既存] Sensitivity 1: Revenue growth × Margin
[新規] Sensitivity 2: WTP × Pricing realization

         WTP -20%  -10%   Base   +10%  +20%
Pricing
-10%    [X1, ARR]  ...   ...    ...    ...
-5%      ...       ...   ...    ...    ...
Base     ...       ...   [Base] ...    ...
+5%      ...       ...   ...    ...    ...
+10%     ...       ...   ...    ...    ...
```

このマトリックスから「Adoption 率の sensitivity」を別途計算:

```
[新規] Sensitivity 3: Adoption rate × Realization rate

           Realization 40%  50%  60%  70%  80%
Adoption
50%        [LTV1]
60%        ...
70%        ...
80%        ...
90%        ...
```

### 7.5 09_Market_sizing への影響

`09_market_sizing.md` で扱う TAM penetration ceiling を本 reference の WTP 概念で **reality check**:

```
Realistic SOM
  = Market size                                ← TAM
    × WTP_positive_segment_pct (% with ROI > 0) ← § 1.4 (本 reference)
    × adoption_rate (実際に買う %)
    × realistic_share (vs 競合 share)
```

例: B2B SaaS の SOM 算出
- TAM = ¥500B (全業界対象)
- WTP-positive segment = 30% (300人以上の企業のみ ROI 正)
- TAM × 30% = ¥150B (= SAM)
- Adoption rate = 50% (5 年で realistic)
- Realistic share within adopters = 20%
- SOM = ¥150B × 50% × 20% = **¥15B**

> このフローで TAM の 3% に SOM が落ちる。これが 「penetration ceiling 30%」「share 20%」と sloppy に書かれた IC memo より defensible。

---

## 8. Qualitative Effects の定量化

定性的便益 (qualitative effects) を「金額化できないので諦める」ではなく、proxy / option value で **概算金額化**する技法を集める。

### 8.1 ブランド / Strategic 価値

#### 8.1.1 Brand value の代理指標

| 指標 | 単位 | 金額化 |
|---|---|---|
| Net Promoter Score (NPS) | 0-10 score | NPS +12 → revenue +1% (Bain) |
| Brand awareness | % aware of brand | aware → 購入確率 ×1.5-2× |
| Search volume | Google Trends index | search ↑ → organic traffic / CAC saving |
| Share-of-voice | % of social mentions vs competitors | SoV ↑ → 1 年遅れで market share ↑ |
| Sentiment score | -1 to +1 | positive sentiment → repurchase ↑ |

#### 8.1.2 NPS-to-revenue causal の前提

Bain の研究 (Reichheld 2003) は **NPS leader が業界平均より 2.5× 売上成長** という相関を示すが、causal は弱い。

実装: NPS +12 → revenue +1% を base case とし、attribution を 30-50% で discount。

```
Brand value (¥/year, NPS 経由)
  = baseline revenue × (ΔNPS / 12) × 1% × attribution_pct (30-50%)
```

### 8.2 Talent retention の金額化

#### 8.2.1 1 名離職の cost

```
Cost per voluntary turnover
  = 採用 cost (recruiter fee + sign-on bonus + interview labor)
  + 空席期間 cost (生産性 loss × 平均空席月数)
  + Onboarding cost (新人月給 × 6 ヶ月 + onboarding 担当 labor)
  + Knowledge loss (vague、proxy: 退職者 yearly salary × 0.3-0.5)
```

例: ¥10M/year salary engineer 1 名離職:
- 採用: ¥1.5M (15% recruiter fee)
- 空席: 3 月 × ¥1.5M productivity loss = ¥4.5M
- Onboarding: 6 ヶ月 × ¥0.8M = ¥4.8M
- Knowledge: ¥10M × 30% = ¥3M
- **Total: ¥13.8M / 名**

#### 8.2.2 Retention 改善の金額化

ツール導入で離職率 5% → 4% (Δ-1pp)、組織 100 名:
- 削減離職 = 100 × 1% = 1 名 / year
- Saving = ¥13.8M / year

### 8.3 Optionality (オプション価値)

ある投資が将来の **戦略的選択肢** を生む場合、その option value を概算評価する。Black-Scholes の正確な計算は実務で過剰なため、**階段関数で代替**:

```
Option value (階段関数)
  = Σ_(future_scenario) {probability × payoff}

例: AI 統合 platform への先行投資
- 30% prob × M&A target value ¥500M = ¥150M
- 50% prob × 自社製品強化 value ¥200M = ¥100M
- 20% prob × ゼロ payoff = ¥0
- Option value = ¥250M
```

#### 8.3.1 Optionality を IC memo で扱う Tips

- **Probability の根拠** を明示 (基準: business plan / market analysis / management track record)
- **Payoff の保守的見積もり** (upside cap)
- **Time horizon の明示** (3 年 vs 5 年 vs 10 年)
- 複数 option を **independent** で計算しない (1 option 実現すると他 option 消える)

### 8.4 Compliance / Regulatory

#### 8.4.1 違反 fine の期待値

```
Compliance value (¥/year)
  = Σ_(violation_type) {probability × fine_magnitude × 1 - prevention_rate}
```

例: GDPR 違反防止
- 違反確率 (年): 5%
- Fine magnitude: 売上 4% (max ¥X M)
- 既存処理での prevention: 50%
- ツール導入後 prevention: 90%
- Δ prevention: +40%
- Saving = 5% × ¥XM × 40% = expected reduction

#### 8.4.2 Lawsuit avoidance value

訴訟回避:
- 弁護士 fee ¥XM
- 和解 / 判決額 ¥YM
- Reputation cost ¥ZM (long-term revenue loss)

### 8.5 Network effects

#### 8.5.1 Metcalfe's law / Reed's law

| 法則 | Value formula | 適合 |
|---|---|---|
| **Metcalfe's law** | $V \propto N^2$ (pairs) | Communication network (電話、Slack DM) |
| **Reed's law** | $V \propto 2^N$ (subgroups) | Group-forming network (Facebook groups、Discord) |
| **Sarnoff's law** | $V \propto N$ (broadcast) | TV、radio (顧客は受動的) |

#### 8.5.2 WTP の network size 依存

各 user の WTP は **network size の関数** で増加する:

```
WTP_i (個人 i の WTP) = base_WTP + α × log(N)
```

例: ある SNS で N = 1M → WTP $5/month、N = 100M → WTP $5 + α×log(100) = $5 + α×4.6
- α = $1 のとき、N=100M で WTP $9.6
- 大規模化で価格を上げる正当化となる

#### 8.5.3 N 増加と pricing strategy

- Pre-network (N < critical mass): WTP 低、 free または subsidy 推奨
- Post-network (N > critical mass): WTP 高、 monetization 開始
- Mature network: 段階的 price increase (slow)

---

## 9. Anti-patterns (落とし穴 7 連発)

Customer value 計算と pricing で陥る 7 つの落とし穴。

### 9.1 OBL (Over-Bullish Logic)

100% adoption / 0 churn / 100% realization の理論値を effective として使う。

**症状**:
- 「全社員が full-time で使う」想定で labor saving 計算
- 「churn rate 0%」で LTV 計算
- 「即日導入」で立ち上げ cost 無視

**対策**:
- §3.3 の adoption rate / realization rate を必ず discount
- §3.3.1, §3.3.2 の typical 値を base case に
- IC memo で「pessimistic / base / optimistic」3 シナリオ提示

### 9.2 Double counting (二重計上)

Labor saving と revenue uplift を同じ KPI で重複計算。

**症状**:
- 営業時間 saving と「営業時間が増えたことで売上増」を独立に金額化
- Customer support 効率化と「support 時間が delivery に回って revenue 増」を独立計算

**対策**:
- Driver tree (§2.4) で **どの時間 / どの cost が** どこに流用されるかを明示
- 重複計上の risk を「mutually exclusive vs additive」で議論
- 数学的に: 同じ lever を 2 つの benefit で使う場合、2 つの sum は double count

### 9.3 Time horizon mismatch

5 年 NPV を 1 年 ROI で比較する、または逆。

**症状**:
- Vendor の TEI study (5 yr NPV) を顧客の 1 年予算と直接比較
- Hardware (10 yr 償却) を SaaS (annual subscription) と同 horizon で比較

**対策**:
- B2B SaaS は **3 年 horizon** が業界標準 (本書 canonical)
- Hardware は **5-7 年** TCO
- Bio (drug) は **5-10 年** patent life
- 比較時は同 horizon に揃える、 または annualize する

### 9.4 Hidden cost (隠れた cost の見落とし)

| Hidden cost | 例 | 典型値 |
|---|---|---|
| Switching cost | Legacy migration | License の 30-60% |
| Data migration | データ変換 / 整合性確保 | ¥X-XXM (規模依存) |
| Training | Employee education | License の 20-40% |
| Integration | 既存 system との API 接続 | ¥XM-XXM |
| Internal process change | SOP 改訂、 onboarding 改訂 | Hidden、 6-12 月分の 部分労務 |
| Opportunity cost | Migration 期間の生産性低下 | 3-6 月、 既存 baseline の 15-30% loss |
| Ongoing maintenance | Vendor management | License の 10-15%、 vendor 多いほど大 |
| Support cost | チケット対応 / Q&A | License の 15-25% |
| Compliance cost | SOC2 / GDPR / J-SOX 適合 | One-time + annual |

> 実際の TCO = License × 1.4-2.0× が経験則。「License 単価 ÷ 1.4-2.0」を hidden cost ratio として確保。

### 9.5 Counterfactual issue

「何もしなかった場合」の baseline をどう取るか。

**症状**:
- 「導入後 売上 +10%」と主張するが、 baseline 自体が +8% growth していた (Δ=+2% のみが正しい)
- 「ツール導入で離職率改善」だが、 経済 cycle で離職率全体が下降していた

**対策**:
- Baseline drift (技術進歩 / 市場 cycle) を控除
- Counterfactual control group を立てる (A/B で half not adopted)
- 業界 benchmark で baseline を validate

### 9.6 Survivor bias (生存者バイアス)

既存顧客のみで ROI 計算 → churn した顧客の negative ROI が反映されない。

**症状**:
- TEI study で「顧客 5 社の ROI 中央値 250%」だが、 churn した 3 社を除いている
- Customer success team の case study が成功例のみ

**対策**:
- Cohort analysis で **全顧客** (churn 含む) の median ROI
- Churn cohort の reason を別 segment 化
- IC memo で「sample size N、 churn excluded N'」を明示

### 9.7 Halo effect (ハロー効果)

1 顧客の成功事例で全顧客の ROI を一般化する。

**症状**:
- "We helped Microsoft save $50M/year" → 全顧客で同様の saving を仮定
- 1 件の Tier-1 顧客の ICER で全 patient 集団の cost-effectiveness を主張

**対策**:
- Segment 別の **median + IQR** (interquartile range) を提示
- Top decile (best case) と median と bottom decile (worst case) の 3 点提示
- Single-customer case study は「example」と明記、 generalize しない

### 9.8 (補足) Pricing-specific anti-patterns

- **Cost-plus 妄想**: 「原価の 30% margin が業界標準」← 顧客 ROI 無視
- **Competition mirroring**: 「競合と同価格」← 自社の差別化を反映できない
- **Anchor を高く設定するため Best tier を非現実的に高く**: 顧客信頼喪失
- **Discount を恒常化**: List price が空気 化、 pricing power 喪失
- **Contract 長期化で過大 discount**: NRR への影響、 期中値上げ困難

---

## 10. Mini Case 詳解 (7 例)

各 case は **顧客 profile → driver tree → effective ¥ 計算 → WTP → vendor pricing** の流れを再現。

### Case 1: Salesforce SFA × Series A SaaS (詳細版)

**Customer profile**:
- 業界: B2B SaaS (Series B 段階)
- 規模: 営業 100 名、ARR baseline ¥10B
- 現状: SFA なし (Excel + メール運用)

**Driver Tree**:

#### Cost reduction (labor)
- ΔHours: 5 hr/week × 50 週 = 250 hr/year/seat (調査時間 / 入力時間 / レポート作成)
- Hourly rate (fully-loaded): ¥10M / 2,000 hr × 1.25 = ¥6,250/hr
- Theoretical: 100 × 250 × ¥6,250 = ¥156.25M / year
- × adoption 70% × realization 60% = **¥65.6M / year (effective)**

#### Revenue uplift (conversion)
- baseline ¥10B × 2pp conversion uplift (実績ベース、 Salesforce study)
- = ¥200M / year (theoretical)
- × adoption 70% × realization 50% × attribution 60% = **¥42M / year (effective)**

#### Risk reduction (商談紛失抑制)
- Annual lost deal value: ¥50M
- Reduction by SFA: 50%
- Probability of any year having lost deal: 80%
- = ¥50M × 50% × 80% = **¥20M / year (effective)**

#### Tool consolidation
- 旧: HubSpot Marketing ¥3M + Mailchimp ¥1M + Notion ¥1M = ¥5M / year
- 新: Salesforce 統合化で削減 = ¥3M / year
- = **¥3M / year (effective)**

**Total effective benefit: ¥65.6 + ¥42 + ¥20 + ¥3 = ¥130.6M / year**

#### Cost (Vendor pricing + Implementation)
- Salesforce Sales Cloud Enterprise: ¥18,000 / seat / month × 100 = ¥21.6M / year (Note: 世間 list は $165/seat/mo ≒ ¥24K、 enterprise discount で ¥18K)
- Implementation (システム統合 + データ移行): ¥30M (one-time)
- Training: ¥8M (year 1)

#### NPV (3 yr, discount 10%)
- Year 0: -¥30M
- Year 1: ¥130.6 - ¥21.6 - ¥8 = ¥101M
- Year 2: ¥130.6 - ¥21.6 = ¥109M
- Year 3: ¥130.6 - ¥21.6 = ¥109M
- NPV = -30 + 101/1.1 + 109/1.21 + 109/1.331 = **¥230.6M**
- Payback: ~ 4 ヶ月
- IRR: ~340%
- ROI total (year 3 cumulative): (319 - 30) / 30 = **963%**

#### WTP boundary
- Customer ROI ¥130.6M × 30% gainsharing = **¥39.2M / year**
- Salesforce price ¥21.6M / year → vendor take = 21.6 / 130.6 = **16.5% of customer ROI**
- Acceptable range (gainsharing 20-30%): ¥26-39M
- 現価格は under-priced。 cross-sell / tier upgrade で ¥30M target が realistic

#### Pricing thesis 結論
- Year 1 pricing ¥21.6M (現状) を維持し、land を確実に
- Year 2-3 で Service Cloud + Marketing Cloud cross-sell で ARR ¥35-40M target
- NRR target: 130%+

---

### Case 2: AWS migration × 中堅企業

**Customer profile**:
- 業界: 中堅 EC 企業 (year 売上 ¥50B)
- 現状: オンプレデータセンター (HW 250 台、DC 1 拠点)

**Driver Tree**:

#### TCO breakdown (5 year)
| Item | On-premise | AWS | Saving |
|---|---|---|---|
| HW capex (5 yr 償却) | ¥30M / year | ¥0 | +¥30M |
| 運用 / 保守人件費 (4 名) | ¥40M / year | ¥18M (AWS スキル者 2 名) | +¥22M |
| 電力 + 冷却 | ¥10M / year | ¥0 | +¥10M |
| DC 賃貸 | ¥20M / year | ¥0 | +¥20M |
| AWS subscription | ¥0 | ¥48M / year (Reserved Instance + S3 + RDS) | -¥48M |
| **Net annual saving** | | | **¥34M / year** |

#### Migration cost (one-time)
- Re-architecture: ¥15M
- Data migration: ¥10M
- Cutover + rollback plan: ¥5M
- Total: ¥30M (3 yr 按分 = ¥10M / year)

#### Strategic optionality (qualitative)
- Auto-scaling で trafic spike 耐性 (Black Friday の inventory loss 回避)
- Global expansion 容易 (multi-region deploy)
- Probability-weighted: ¥20M optionality value (year 3+)

**Total effective benefit (year 1)**: ¥34M - ¥10M = **¥24M / year**
**Total (year 3+)**: ¥34M (migration cost depreciated) + 強い optionality

#### NPV (5 yr, discount 8%)
- Year 0: -¥30M
- Year 1-5: ¥34M / year (after migration cost amortization)
- NPV ≈ -30 + 34 × 3.99 (annuity factor 5yr 8%) = -30 + ¥135.7M = **¥105.7M**
- Payback: ~14 ヶ月
- ROI total: 380% (over 5 years)

#### Vendor (AWS) take
- ¥48M / year revenue from this customer
- Customer ROI = ¥34M / year
- AWS take of customer ROI: 48 / (48 + 34) = 58% (broad sense include cost替代)
  → AWS は cost-replacement model で 58% は妥当 (顧客は ¥34M/yr 残す)

詳細は §3.1.5 で標準形を参照。

---

### Case 3: Stripe 決済 × D2C 急成長

**Customer profile**:
- 業界: D2C consumer (D2C apparel)
- 規模: 取扱高 ¥1B / year (急成長中)
- 現状: 旧 PSP (内製決済 + 銀行 connector)

**Driver Tree**:

#### Cost reduction (transaction fee)
- 旧 PSP fee: 4.0% of GMV = ¥40M / year
- Stripe fee: 2.9% + ¥30/件 (taverage transaction ¥3,000) ≒ 3.0% of GMV = ¥30M / year
- **Saving: ¥10M / year**

#### Risk reduction (不正検知)
- 不正取引推定: ¥5M / year (chargeback 含む)
- Stripe Radar による reduction: 60%
- **Saving: ¥3M / year**

#### Productivity (dev 工数)
- 旧 PSP: 自社 engineer 月 5 日 dev / maintain
- Stripe: 月 1 日 dev / maintain
- Saving: 4 日 × 12 月 × ¥50K/day = **¥2.4M / year**

#### Tool consolidation
- 旧: Subscription billing 自社実装 ¥2M maintenance / year
- Stripe Billing で代替: ¥0.5M maintenance
- **Saving: ¥1.5M / year**

#### Strategic optionality
- 海外決済対応 (USD / EUR) 容易: market 拡大 optionality
- Probability-weighted ¥5M optionality (year 2+)

**Total effective benefit: ¥10 + ¥3 + ¥2.4 + ¥1.5 = ¥16.9M / year**

#### Vendor (Stripe) take
- Customer payment to Stripe: ¥30M / year
- Customer ROI: ¥16.9M / year
- Vendor take of net ROI: 30 / (30 + 16.9) = 64% (≈ broad sense)
  → 高い take rate だが、 cost replacement (旧 ¥40M → ¥30M) があるため acceptable

#### Stage 別 expansion path
- Year 1 (¥1B GMV): pure transaction fee
- Year 3 (¥10B GMV): + Subscription Billing + Connect (marketplace) + Atlas (incorporation) で expand
- Stripe 顧客の typical NRR: 130%+ (a16z 2023 SaaS report)

---

### Case 4: 医療機器 (高額耐久財) × Hospital

**Customer profile**:
- 病院: 中堅総合病院 (300 床)
- 製品: MRI 装置
- 現状: 既存 MRI (10 年経過、 維持費高)

**Driver Tree (5 year TCO comparison)**:

#### Existing MRI TCO (5 year)
| Item | ¥M / year | 5 yr total |
|---|---|---|
| Maintenance | 15 | 75 |
| Energy | 8 | 40 |
| Downtime cost (年 1 週間) | 5 | 25 |
| Replacement parts | 4 | 20 |
| Operator labor | 12 | 60 |
| **Total** | **44** | **220** |

#### New MRI TCO (5 year)
| Item | ¥M / year | 5 yr total |
|---|---|---|
| Initial purchase | (200, 一括) | 200 |
| Maintenance | 8 | 40 |
| Energy | 5 | 25 |
| Downtime cost (年 2 日) | 1.4 | 7 |
| Replacement parts | 2 | 10 |
| Operator labor (efficiency) | 9 | 45 |
| **Total** | **+25.4 / year (年次)** | **327** |

**5 年 TCO 比較**:
- Existing: ¥220M
- New: ¥327M
- Δ = +¥107M (新型が高い)

#### しかし...
- New MRI で 撮影効率 30% UP → patient throughput 増加
- Δ revenue (5 年): ¥150M (患者 1 人 ¥30K × 増加患者 1,000 人/year × 5 年)
- 早期発見性能向上 → 紹介病院シェア (qualitative + ¥30M / 5yr)

**Total benefit including revenue: ¥150 + ¥30 - ¥107 = ¥73M (5yr NPV positive)**

#### WTP boundary
- Manufacturer 視点: existing TCO ¥220M を超えない範囲で TCO total
- 現状価格 ¥200M は acceptable、 ただし maintenance contract の bundling で attractive さ↑

#### Manufacturer take (gainsharing)
- Hospital surplus value over alternative: ~¥70M / 5yr = ¥14M / year
- Manufacturer take: ¥200M ÷ 5 = ¥40M / year (≒ 装置 + maintenance)
- これは alternative よりは高いが、 revenue uplift も含めれば justify

---

### Case 5: SaaS Tier design (Good/Better/Best)

**Customer profile**:
- B2B SaaS provider (営業 SaaS)
- 顧客 segment: SMB (1-50 seat) / Mid (50-500) / Enterprise (500+)

**3-Tier 構造**:

| Tier | Price (¥/seat/mo) | Features | Limit | Target segment | 想定 % |
|---|---|---|---|---|---|
| **Good** | ¥3,000 | Basic CRM、 contact mgmt、 mobile app | 5 user | SMB (early) | 25% |
| **Better** | ¥10,000 | + API、 reporting、 automation、 integrations | 100 user | Mid-market | 60% |
| **Best** | ¥30,000 | + SSO、 audit log、 priority support、 sandbox | unlimited | Enterprise | 15% |

#### Tier WTP (PSM analysis)

| Segment | IPP (¥/seat/mo) | OPP | 推奨 tier |
|---|---|---|---|
| SMB | ¥2,500 | ¥3,500 | Good (¥3K) |
| Mid | ¥9,000 | ¥11,000 | Better (¥10K) |
| Enterprise | ¥25,000 | ¥35,000 | Best (¥30K) |

各 tier の price は IPP-OPP range の中央。

#### Decoy effect の使い方
- Best (¥30K) は anchor、 実売れる顧客は少ない (15%)
- Better (¥10K) を「お得感」で誘導 (¥30K に比べ 1/3)
- Good (¥3K) は SMB と「downsell 阻止」用

#### Tier 移行率 (NRR への影響)
- Good → Better: 年 20% (5 user 制限を超えるとき)
- Better → Best: 年 10% (SSO 必要となる Enterprise 移行時)
- 平均 ARPU uplift via tier upgrade: ¥3K/seat/mo

#### Best practice
- Better tier に **70-80% feature** を入れる (most attractive)
- Good tier の limit gating を「organic upsell」に設計 (5 user → 6 人で upgrade)
- Best tier の差別化 feature は **明確** (SSO / Audit / SLA など Enterprise unique)

---

### Case 6: Bio drug × ICER 実例

**Drug profile**:
- 適応: HER2陽性早期乳がん補助療法
- 価格: ¥3M / year / patient (1 年治療コース)
- Comparator: ハーセプチン (既存 standard therapy) ¥300K / year

**Effectiveness data (Phase 3)**:
- Recurrence reduction: 40% relative risk reduction
- Survival extension (5 yr OS): +2.5%
- Per patient QALY gain: 1.2 QALY (5-year horizon, discounted)

**ICER calculation**:
- Cost difference: ¥3M - ¥0.3M = ¥2.7M
- QALY gain: 1.2
- ICER = ¥2.7M / 1.2 = **¥2.25M / QALY**

**Threshold check (Japan C2H)**:
- Standard threshold: ¥5M / QALY
- Severe disease (cancer): ¥7.5M
- ICER ¥2.25M < ¥5M → **Cost-effective、価格 acceptable**

**Compare with US ICER threshold**:
- US ICER value-based price (intermediate): $100K-150K / QALY ≒ ¥15-22.5M / QALY
- ¥2.25M / QALY < $100K → 米でも高度に cost-effective

#### Pricing thesis
- 製薬会社 価格 ¥3M / patient / year は justified
- Probabilistic sensitivity analysis (PSA) で 80%+ 確率で cost-effective
- 早期承認 + 適応拡大 (HER2陽性 advanced で expansion) でブロックバスター化

#### 反対 case: Threshold 超過の場合
- 仮に薬剤価格 ¥10M / year のとき:
- ICER = (10 - 0.3) / 1.2 = ¥8.1M / QALY
- 標準 threshold ¥5M を超過、 severe ¥7.5M も微越え
- Pricing 対応:
  - 価格引下げ (国別 negotiation で 30-50% reduction が定石)
  - Risk-sharing scheme (response 率に応じた refund)
  - Patient access program (低所得層 free or discount)

---

### Case 7: AI tool × white collar productivity

**Customer profile**:
- 業界: 大手金融機関
- 規模: 営業 / アナリスト合計 1,000 名
- 現状: 手動 research、メール作成、 proposal draft

**Driver Tree**:

#### Cost reduction (labor saving)
- ΔHours: 1 hr / day saved per worker (research 30 min + memo 30 min)
- Hourly rate (fully-loaded、 金融): ¥8,000/hr
- 200 work days / year
- Theoretical: 1,000 × 1 × 200 × ¥8,000 = ¥1.6B / year
- × adoption 60% × realization 70% = **¥672M / year (effective)**

#### Revenue uplift (商談数増)
- Saved time → 商談数 +10% (実績ベース)
- Annual revenue base ¥50B × 商談数寄与 50% × +10% × adoption × realization × attribution
- ¥50B × 0.5 × 0.1 × 0.6 × 0.5 × 0.4 = **¥300M / year (effective)**

#### Risk reduction (compliance)
- AI による double-check で compliance violation 確率 ↓
- Annual fine 期待値: ¥10M × 50% reduction = **¥5M / year**

**Total effective benefit: ¥672 + ¥300 + ¥5 = ¥977M / year**

#### Cost (Vendor pricing + Implementation)
- AI tool subscription: ¥50K / seat / year × 1,000 = ¥50M / year (current)
- Implementation + integration: ¥30M (one-time)
- Training: ¥10M (year 1)

#### NPV (3 yr, discount 10%)
- Year 0: -¥30M
- Year 1: 977 - 50 - 10 = ¥917M
- Year 2: 977 - 50 = ¥927M
- Year 3: 927M
- NPV = -30 + 833 + 766 + 697 = **¥2,266M (約 ¥2.3B)**

#### WTP boundary
- Customer ROI ¥977M × 30% gainsharing = **¥293M / year**
- Vendor take (¥50M) = 5.1% of customer ROI → **大幅 under-pricing**
- Acceptable range: ¥150-300M / year
- 現状価格は 1/5 ~ 1/6 程度

#### Pricing 改善 path
- Tier upgrade: enterprise tier ¥150K / seat / year に → ¥150M / year (3× current)
- Outcome bonus: KPI 達成額の 5-10% を bonus (¥30-50M / year additional)
- Total target ARR per customer: ¥200M / year (gainsharing 20% を target)

#### 業界 implication
- AI tool は white collar productivity の **巨大 ROI** を生む
- 多くの AI 製品は under-priced 状態 (vendor が customer value を取りきれていない)
- 2025-2026 で価格 2-5× 引上げが期待される (Anthropic / OpenAI 等の Enterprise pricing 動向)

---

## 11. References / Sources (出典)

### 11.1 一次資料 (Academic / Industry Authoritative)

#### Bain "Elements of Value"
- Almquist, E., Senior, J., & Cleghorn, J. (2018). "The B2B Elements of Value." *Harvard Business Review*, March-April 2018. [https://hbr.org/2018/03/the-b2b-elements-of-value](https://hbr.org/2018/03/the-b2b-elements-of-value)
- Almquist, E., Senior, J., & Bloch, N. (2016). "The Elements of Value." *Harvard Business Review*, September 2016.
- Bain & Co interactive: [https://www.bain.com/insights/explore-the-b2b-elements-of-value-interactive/](https://www.bain.com/insights/explore-the-b2b-elements-of-value-interactive/)
- B2B = 40 elements (5 layers: Table stakes / Functional / Ease of doing biz / Individual / Inspirational)
- B2C = 30 elements (4 layers: Functional / Emotional / Life-changing / Social Impact)

#### Forrester TEI (Total Economic Impact)
- Forrester Research, Inc. "The Total Economic Impact™ Methodology." Forrester white paper.
- Forrester TEI policies: [https://www.forrester.com/policies/tei/](https://www.forrester.com/policies/tei/)
- 4 軸: Benefits / Costs / Flexibility / Risk
- Risk-adjusted, NPV-based, 3 年 horizon が標準

#### Van Westendorp PSM
- van Westendorp, P. (1976). "NSS-Price Sensitivity Meter (PSM) — A new approach to study consumer perception of price." *Proceedings of the ESOMAR Congress*, pp.139-167.
- Wikipedia: [https://en.wikipedia.org/wiki/Van_Westendorp's_Price_Sensitivity_Meter](https://en.wikipedia.org/wiki/Van_Westendorp's_Price_Sensitivity_Meter)
- 4 質問: Too cheap / Cheap / Expensive / Too expensive
- 4 交点: PMC / IPP / OPP / PME

#### Conjoint Analysis
- Sawtooth Software. "Conjoint Analysis: A Step by Step Guide." Sawtooth Software white paper.
- Green, P. E., & Srinivasan, V. (1990). "Conjoint Analysis in Marketing: New Developments with Implications for Research and Practice." *Journal of Marketing*, 54(4), 3-19.

### 11.2 書籍 (Pricing Theory)

- Ramanujam, M., & Tacke, G. (2016). *Monetizing Innovation: How Smart Companies Design the Product Around the Price*. Wiley.
- Holden, R., & Burton, M. (2008). *Pricing with Confidence: 10 Ways to Stop Leaving Money on the Table*. Wiley.
- Nagle, T. T., Hogan, J., & Zale, J. (2016). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Simon, H. (2015). *Confessions of the Pricing Man: How Price Affects Everything*. Copernicus.
- Smith, T. J. (2012). *Pricing Done Right: The Pricing Framework Proven Successful by the World's Most Profitable Companies*. Wiley.

### 11.3 SaaS pricing benchmarks

- ChartMogul. "The SaaS Retention Report: The New Normal For SaaS." 2024-2025. [https://chartmogul.com/reports/saas-retention-the-new-normal/](https://chartmogul.com/reports/saas-retention-the-new-normal/)
- Benchmarkit. "2025 SaaS Performance Metrics." [https://www.benchmarkit.ai/2025benchmarks](https://www.benchmarkit.ai/2025benchmarks)
- SaaS Capital. "2025 Private B2B SaaS Company Growth Rate Benchmarks." [https://www.saas-capital.com/research/private-saas-company-growth-rate-benchmarks/](https://www.saas-capital.com/research/private-saas-company-growth-rate-benchmarks/)
- OpenView Partners. "SaaS Benchmarks Report" (annual).
- Pacific Crest / KeyBanc Capital Markets. "Annual SaaS Survey."
- a16z. "Marketplace 100" (annual marketplace benchmarks).

### 11.4 Healthcare / Bio pricing

- ICER (Institute for Clinical and Economic Review, US). "Value Assessment Framework." [https://icer.org/our-approach/methods-process/](https://icer.org/our-approach/methods-process/)
- NICE (UK National Institute for Health and Care Excellence). "Guide to the methods of technology appraisal."
- C2H (Center for Outcomes Research and Economic Evaluation for Health, Japan). "費用対効果評価制度."
- Drummond, M. F., Sculpher, M. J., Claxton, K., Stoddart, G. L., & Torrance, G. W. (2015). *Methods for the Economic Evaluation of Health Care Programmes* (4th ed.). Oxford.

### 11.5 NPS / Customer satisfaction

- Reichheld, F. F. (2003). "The One Number You Need to Grow." *Harvard Business Review*, December 2003.
- Reichheld, F. F., & Markey, R. (2011). *The Ultimate Question 2.0: How Net Promoter Companies Thrive in a Customer-Driven World*. HBR Press.

### 11.6 Customer ROI methodology

- Christensen, C. M., Hall, T., Dillon, K., & Duncan, D. S. (2016). *Competing Against Luck: The Story of Innovation and Customer Choice*. HarperBusiness.
- Anderson, J. C., Kumar, N., & Narus, J. A. (2007). *Value Merchants: Demonstrating and Documenting Superior Value in Business Markets*. HBS Press.

### 11.7 関連 reference (本 skill 内)

- `02_saas_metrics.md` (LTV / CAC, NRR canonical)
- `03_business_models.md` (業態別 revenue 構造)
- `09_market_sizing.md` (TAM / SAM / SOM)
- `16_cost_structure.md` (vendor 側コスト)
- `08_investment_thesis.md` (IC memo 雛形)
- `15_input_schema.md` (input field 定義)
- `_terminology.md` (NRR、 Magic Number 等の canonical 数値)

---

## 12. 関連 reference との整合

### 12.1 02_saas_metrics.md (LTV / CAC) との関係

`02_saas_metrics.md` で扱う LTV / CAC は **vendor 視点の経済性**。本 reference は **顧客視点の ROI**。両者は対の関係:

```
LTV (vendor) = ARPU × (1 / churn_rate) × gross_margin
LTV (customer) = Σ_year {benefit - cost} discounted

LTV (vendor) は LTV (customer) × gainsharing_pct (15-30%) が WTP 上限
```

`02 §5.3.x` (LTV 計算式) を読むときは、本 reference §3-§4 の WTP / gainsharing で「LTV 上限の根拠」を補強する。

### 12.2 03_business_models.md (業態別 revenue) との関係

`03_business_models.md` で各業態の **revenue 構造** (subscription / take rate / NIM) を扱うが、その **price level 決定** は本 reference §6 の業態 template を参照する。

| 業態 | `03` 担当 | `18` (本書) 担当 |
|---|---|---|
| SaaS | revenue model 構造 | price level / tier design |
| Marketplace | take rate 構造 | take rate ceiling / WTP |
| Fintech | NIM 構造 | NIM ceiling / borrower value |

### 12.3 09_market_sizing.md (TAM / SAM / SOM) との関係

`09_market_sizing.md` で扱う TAM penetration の **reality check** は本 reference §7.5 で行う:

```
SOM = TAM × (WTP-positive segment %) × (adoption %) × (realistic share %)
```

`09 §3-§4` (TAM 計算) を埋めるときは、本 reference §7.5 の手順で derived value を validate する。

### 12.4 16_cost_structure.md (vendor side cost) との関係

`16_cost_structure.md` は **vendor 側のコスト**を扱う。本 reference §9.4 (Hidden cost) は **顧客側のコスト**を扱い、両者を混同しないこと。重複しないように:

- `16` = vendor が支払う COGS / OpEx
- `18` (本書) = 顧客が ROI 計算で控除する hidden cost (License 以外)

### 12.5 08_investment_thesis.md (IC memo) との関係

IC memo の "Pricing Thesis" section (本 reference §7.3) は `08_investment_thesis.md §17` の標準構成に **新 section** として追加される。`08` は memo の overall structure を定義し、 `18` は pricing 関連 section の中身を定義する。

### 12.6 15_input_schema.md (input fields) との関係

本 reference §7.1.2 で提案した新 input field (customer_roi_annual / gainsharing_pct / wtp_psm_opp 等) は `15_input_schema.md §2` に formal definition を追加する。本 reference 提案 → `15` で正式 schema 化、 という flow。

### 12.7 _terminology.md (canonical metric) との関係

本 reference で使う metric (NRR / LTV / CAC / Magic Number) は **すべて `_terminology.md` の canonical 定義** に従う。本 reference は重複 definition を作らない。

特に NRR の中央値については、本 reference §4.5.2 の table が最新の業界 benchmark を反映しており、 `_terminology §6.4` の Snowflake 個別データと整合する。

---
