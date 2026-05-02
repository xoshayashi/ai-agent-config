---
name: business_models
description: SaaS 以外の主要 10 業態 (Marketplace / D2C / Fintech / Hardware / Bio / Media / B2B Services / Manufacturing / Real Estate / AI Foundation) のメトリクス・モデリング論点・落とし穴の正本。SKILL.md dispatch table の "業態別 unit economics" entry から読まれる。
type: reference
priority: P1
related: [_terminology, 02_saas_metrics, 09_market_sizing, 16_cost_structure, _master_decision_tree]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 業態判定 / 共通用語 (GMV / take rate / TPV 等) は本書を canonical とする。色・sheet name 等は [`_terminology.md`](_terminology.md)
- **Routing**: [`_master_decision_tree.md §E`](_master_decision_tree.md) (業態 × stage) から該当業態 § を直接 dispatch
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (特に `_stress_framework §4.1` の applicability) を必ず実行
- **関連 reference**: `02_saas_metrics` (SaaS 業態) / `09_market_sizing` (TAM/SAM/SOM) / `16_cost_structure` (業態別 COGS/OpEx) / `_master_decision_tree §E` (業態 routing)

# 03. ビジネスモデル別 重要メトリクスと財務モデリング論点

スタートアップ向け包括的財務モデリングのリファレンス。SaaS 以外の主要 10 業態について、メトリクス定義、ベンチマーク、モデリング上の落とし穴、IPO/開示の典型を体系化する。

---

## 目次

1. [Marketplace / Platform](#1-marketplace--platform)
2. [E-commerce / D2C](#2-e-commerce--d2c)
3. [Fintech (Lending / Neobank / Payments)](#3-fintech-lending--neobank--payments)
4. [Hardware / IoT / Robotics](#4-hardware--iot--robotics)
5. [Bio / Pharma / MedTech](#5-bio--pharma--medtech)
6. [Media / Content / Creator](#6-media--content--creator)
7. [B2B Services / Consulting](#7-b2b-services--consulting)
8. [Manufacturing / Industrial](#8-manufacturing--industrial)
9. [Real Estate / PropTech](#9-real-estate--proptech)
10. [AI / Foundation Model](#10-ai--foundation-model)
11. [業態判定フローチャート](#業態判定フローチャート)

---

## 共通の原則

- **Bookings と Revenue は別物**: GMV / TPV / Bookings はトップオブザファネルの取引総額。GAAP/IFRS の Net Revenue とは認識基準が異なる。混同すると評価倍率が壊れる。
- **Gross と Net の言い換えに注意**: Net Revenue 開示企業 (Etsy, eBay) と Gross Revenue 開示企業 (Amazon 1P, Mercari) の倍率比較は無効。
- **Cohort で見る**: Aggregate retention は新規流入で薄まる。必ずコホート (取得月別) で reten / repeat / GMV per cohort を見る。
- **Unit Economics は contribution margin ベース**: Gross Margin だけで CAC payback を計算するとマーケ・物流・返品・決済を取りこぼす。
- **Working capital を独立 driver に**: 在庫・売掛・買掛・前受金は P/L には現れないが、現金繰りを支配する。

---

# 1. Marketplace / Platform

## 1.1 主要メトリクス

### GMV (Gross Merchandise Value) / GBV / GOV / TPV

```
GMV = Σ (取引完了金額)  // 税・手数料・チップを含めるかは要件定義
```

業態別の慣行的な開示単位。

| 業態 | 開示用語 | 対象企業 |
|---|---|---|
| Lodging | Gross Booking Value (GBV) | Airbnb, Booking |
| Ride / Delivery | Gross Bookings | Uber |
| Food Delivery | Marketplace GOV | DoorDash |
| Resale C2C | GMV / 流通額 | Mercari, eBay |
| Fintech 決済 | TPV (Total Payment Volume) | Square, Adyen |

### Take Rate

```
Take Rate = Net Revenue / GMV
        または Gross Revenue / GMV
```

- Airbnb: 通常 13–14% (Service fee guest 5–15% + host 3% 等が原資)
- DoorDash: 12–14% レンジ (Marketplace GOV ベース)
- Uber Mobility: 25–30% (gross take rate)、Driver incentive 控除後 net take rate は数 pt 低い
- Mercari Japan: 販売手数料 10% (2024 に一部撤廃)
- Etsy: 7–8% レンジ (transaction + payment + listing)

> **モデリング論点**: Take rate は事業の値付け力と pricing power を反映。Driver incentive、coupons、refund を Net out しているか必ず確認。これらは contra-revenue として控除されるか、S&M / Operations コストとして計上されるかで Net Revenue が大きく変わる (例: Uber は driver incentive のうち超過分を Sales & Marketing に計上)。

### Liquidity (流動性)

最も本質的な marketplace 健全性指標。Liquidity が無ければ marketplace は価値を生まない。

主な計測メトリクス:

```
Search-to-Fill Ratio = 取引成立件数 / 検索件数
Match Rate          = マッチ成立件数 / マッチ要求件数
Time to First Match = (リスト掲載または検索開始から) 最初のマッチまでの時間
Utilization Rate    = 実取引化された supply / 全 supply
Days on Market      = リスト掲載から成約までの日数
```

業態別に好まれる指標が異なる:

| 業態 | 主指標 | Good benchmark |
|---|---|---|
| Ride hail | Pickup ETA, Time to dispatch | < 5 分 |
| Food delivery | Time to dispatch + delivery | < 30 分 |
| Lodging | Search-to-book conversion | 1–3% |
| Job marketplace | Time to first response | < 24h |
| Resale | Days to sell | < 30 日 |

### Network Effects 計測

Bill Gurley の XY フレームワーク (横軸: 浸透率、縦軸: nth user/supplier に対する価値):
- 真の network effect: 浸透率と value が単調増加。
- 多くの labor marketplace は 5% 程度で頭打ち (incremental supply の価値が減衰)。

実務で使う近似指標:
- **Cross-side retention**: supply 増加 → demand retention 上昇の弾力性
- **Localization**: 地域・カテゴリ別 density (例: 都市別 active driver 数 / active rider 数)
- **Multi-tenanting**: ドライバーや出店者が他プラットフォームと併用しているか (高ければ network effect は弱い)

### Concentration Risk

```
Top X% Supply Concentration = Top X% supplier の GMV シェア
Top X% Demand Concentration = Top X% buyer の GMV シェア
```

- Top 10% supplier に 50% 超の GMV が集中している場合、bargaining power がプラットフォーム側に限定的。
- DoorDash S-1: top merchant への依存度開示。
- Etsy: top sellers の churn が GMV に大きく影響。

### Cohort Retention (両サイド)

Marketplace は **GMV retention** でコホートを見る (a16z 推奨)。

```
GMV Retention (Year N) = Cohort C の Year N 内 GMV / Cohort C の Year 1 GMV
```

**頻度別 best-in-class 閾値 (E-H-018 解消):**

| 取引頻度 | Year 2 GMV retention 目標 | 例 |
|---|---|---|
| 高頻度 (>12 回/年) | **>120% 必要** | Uber, DoorDash, 日次 SaaS |
| 中頻度 (4-12 回/年) | 100-120% で良好 | Etsy, Mercari |
| 低頻度 (1-4 回/年) | **100% で best-in-class** | Airbnb, 不動産マーケットプレイス |
| 単発 (<1 回/年) | 50-80% でも許容 | 結婚式関連、葬儀 |

「Year 2+ で 100% 超」は中〜低頻度カテゴリーの目標値。**food delivery で 100% は mediocre**、低頻度宿泊で 100% は excellent と解釈は逆転する。
- Median: Year 2 で 60–70%
- Weak: Year 2 で < 50% (一回きり利用が多い、再来訪インセンティブが弱い)

両サイド (supply / demand 両方) で計測する。Supply 側の churn は提供量を減らし、demand 側の retention を毀損する。

### Bookings vs Net Revenue 認識

**Principal vs Agent (ASC 606 / IFRS 15)** の判定が会計を支配する:

- **Principal (Gross 認識)**: 在庫リスク・価格決定権・履行責任を負う → 取引総額を Revenue に計上。
- **Agent (Net 認識)**: 仲介のみ → 手数料 (commission / take) のみを Revenue に計上。

代表例:
- Airbnb: Agent → Net Revenue (service fee 部分のみ)
- eBay: Agent → Net (transaction fee のみ)
- Amazon 1P (Retail): Principal → Gross
- Amazon 3P (Marketplace): Agent → Net (commission のみ)
- Uber Mobility: 大部分 Net (driver は independent contractor)、ただし英国など一部地域では Principal 認識
- DoorDash: 主に Principal (delivery service fee 全額計上 + 配達員費用を COGS)

> **落とし穴**: 同じ「marketplace」と呼ばれる企業同士でも、Principal/Agent の違いで Revenue 倍率が 5–10x 乖離する。比較時は **Net Revenue / Take ベース** に揃える。

## 1.2 ベンチマーク値

Take Rate (median / good / great):

| Vertical | Median | Good | Great | 出典 |
|---|---|---|---|---|
| Horizontal C2C resale | 8–10% | 12% | 15%+ | a16z marketplace 100 |
| Vertical labor (gig) | 10–15% | 20% | 25%+ | USV / Gurley |
| Lodging | 12–14% | 15% | 17%+ | Airbnb 開示 |
| Food delivery | 12–14% | 14% | 16%+ | DoorDash 10-K |
| Ride hail (gross) | 22–28% | 28% | 30%+ | Uber 10-K |
| Vertical SaaS-enabled marketplace | 15–25% | 25% | 30%+ | a16z |

GMV Retention (Year 2):

| Tier | Range |
|---|---|
| Great | 110%+ (net expansion) |
| Good | 80–100% |
| Median | 60–80% |
| Weak | < 60% |

## 1.3 モデリング上の注意

- **Supply / Demand を別々にモデル化**: 単一の「ユーザー数」では駆動しない。Active sellers, Active buyers, Listings, Search queries, Transactions の 5 layer で組む。
- **Cohort GMV retention** を driver にして将来 GMV を bridge: Year-on-Year で Existing cohort GMV + New cohort GMV (acquisition × first-year GMV per cohort) に分解。
- **Take rate は静的ではない**: コーホート成熟・mix shift・新サービス (広告、決済、物流) で経時変化。
- **Refund / Cancellation を control account に**: GMV ベースの bookings から実現 Revenue にブリッジするとき、cancel 率が大きい業態 (lodging, food) では数 % の差が決定的。
- **Incentive と Discount の表示**: Driver bonus, host promotion, consumer discount を contra-revenue にすると Net Revenue が下がる (Uber 方式)。S&M に計上すると見かけ Net Revenue が高くなる (一部後発)。両方並べて mix-adjusted に評価。
- **Working capital**: ユーザーから前受 → サプライヤーへ後払いのモデル (Airbnb, Booking) では負の working capital が cash 源泉。 GMV 急成長期は free cash flow が会計利益を上回る。

## 1.4 投資判断ロジック観点

1. **Liquidity に到達したか**: マッチ率・search-to-fill が改善トレンドか。地域・カテゴリ別で十分な density があるか。
2. **Take rate を上げる余地**: 現在の rake が「fair」レンジ (Gurley の 10–15%) より低ければ pricing power up の余地。逆に高すぎれば disintermediation リスク。**ただし「高すぎ」の閾値は業態で異なる (E-H-017 解消):** (a) 高頻度・関係構築型 (家庭教師、ハウスクリーナー、ペットケア) で >25% は disintermediation リスク高、(b) 低頻度・長尾・規制下市場 (ride-hail 22-28%、宿泊、医療) で >25% でも defensible — 顧客が直接取引にルーティングできない構造があるため。Gurley の 15% 閾値は中央値で、構造で上下する。
3. **Cohort GMV retention が 100% を超えているか**: 真に sticky か、新規流入で見せかけ成長か。
4. **両サイドの concentration**: 大口 supplier・大口 buyer 依存はリスク。
5. **Cross-side network effects**: supply 拡張が demand を呼ぶ弾力性。Take rate を維持しながら GMV が伸びているか。
6. **Disintermediation リスク**: 高頻度・高単価・関係構築型 (家庭教師、ハウスクリーナー) は marketplace を経由しない直接取引に流れやすい。

## 1.5 IPO / 10-K / 有報 開示の典型

- **Cover Pages の Operating metrics**: GMV / GBV / GOV、Number of transactions, Active buyers, Active sellers (Airbnb は Nights and Experiences Booked)。
- **MD&A の Non-GAAP**: Adjusted EBITDA, Free Cash Flow を Marketplace mix で説明。
- **Cohort 開示**: Airbnb, DoorDash は cohort 性能を S-1 に詳述。
- **Concentration 開示**: 「No single customer accounts for more than 10% of revenue」が無い場合、依存リスクを Risk Factors で明示。
- **Take rate の言葉を避ける**: SEC では「Revenue as a percentage of GMV」と表記する企業が多い。

## 1.6 落とし穴

- **GMV 成長 != 利益成長**: 高 take rate 低 GMV と低 take rate 高 GMV を時系列で混ぜると Revenue 成長が歪む。
- **Refund と Cancellation の遅延認識**: 旅行系では予約取消が後の四半期に効くため、bookings と revenue がタイムラグで動く。
- **Bookings → Revenue 認識まで複数四半期**: Roblox はユーザー寿命 (~27 ヶ月) で deferred revenue を認識。Bookings = revenue とは別物。
- **Multi-tenanting**: 競合プラットフォームを併用する supply は LTV を過大評価しがち。
- **「First-time discount で水増し」**: 新規顧客向けクーポンを Net Revenue で控除しないモデルは新規 cohort の経済性を過大評価する。

## 1.7 開示例 (要点抜粋)

- **Airbnb (10-K 2024 / S-1 2020)**: GBV、Nights and Experiences Booked、Average Daily Rate (ADR) を開示。Net Revenue / GBV ≈ take rate を投資家が逆算。Cancel 率は明示しないが、MD&A で言及。
- **Uber (10-K)**: Mobility / Delivery / Freight の 3 セグメント。Gross Bookings、Trips、MAPCs (Monthly Active Platform Consumers)、Take Rate を Mobility と Delivery 別に開示。Adjusted EBITDA / Gross Bookings が「margin on bookings」として注目される (Q4 2025 で 4.6%)。
- **DoorDash (10-K)**: Marketplace GOV、Total Orders、Take Rate (Q1 2021 で 10.9%、その後上昇)。DashPass 会員数や Logistics の専有性を MD&A で説明。2024 年 GOV は $80.2B、初の年次黒字 $123M。
- **Mercari (有報)**: 流通総額 (GMV) と Net Sales を分けて開示。販売手数料 10% を 2024 に「販売手数料 0 円」キャンペーンで一部撤廃 (USA 事業)。日本 GMV は ~JPY 1.1 trillion。

---

# 2. E-commerce / D2C

## 2.1 主要メトリクス

### AOV (Average Order Value)

```
AOV = Gross Sales / Order Count
```

カテゴリ別の典型 (USD):
- アパレル: $50–150
- 靴 (例: Allbirds): $100–150
- アイウェア (Warby Parker): $100–200
- 食品 D2C: $30–80
- 家具 (Wayfair): $300–500

### Conversion Rate

```
CVR = Orders / Sessions
```

- D2C 平均: 1.5–3%
- Top quartile: 3–5%
- 大手 marketplace (Amazon Prime cohort): 13%+

Mobile/Desktop で大きく異なるので分けて見る。Add-to-cart rate, Checkout completion rate も必ずファネルで分解。

### Repeat Rate / Cohort Repeat

```
Repeat Rate = 2 回以上購入した顧客数 / 全顧客数 (期間内)
```

- Allbirds (S-1): 2020 売上の ~53% が repeat customer から。
- 平均的 D2C: 20–35% (12 ヶ月内)
- 高頻度カテゴリ (消耗品 CPG): 50%+

### CAC Payback (Months)

```
CAC Payback = CAC / (AOV × 購買頻度 × Contribution Margin %)
```

- Best-in-class D2C: < 6 ヶ月
- Acceptable: 12–18 ヶ月
- 18 ヶ月超は赤信号 (paid traffic 依存度が高すぎる)

### Contribution Margin (Tier 1 / 2 / 3)

D2C では gross margin だけでは経済性を語れない。3 段階に分解する:

```
Net Revenue
  − COGS (Tier 1)                       → Gross Margin
  − Variable fulfillment + payment + returns (Tier 2)  → CM2
  − Variable marketing (paid CAC)       → CM3 (Contribution Margin)
```

- **CM1 (Gross Margin)**: 製品原価のみ。D2C アパレルで 50–60%、消耗品で 60–70%。
- **CM2**: フルフィルメント (Pick & Pack)、配送、決済手数料、返品 reverse logistics、想定 return rate を引いた後。アパレルでは return rate が 20–40% に達するため CM1 から 10–20pt 落ちる。
- **CM3 (Contribution Margin)**: Variable marketing を控除。新規顧客を含む blended の CM3 はマイナスもありうる。

ベンチマーク (Saras, RetentionX 2022):
- Median CM (Tier 3 ベース): 15–30%
- Health & wellness: 47%+
- アパレル: 10–25%

### Returns / Refund 影響

```
Return Rate      = 返品個数 / 出荷個数
Net Revenue      = Gross Sales − Returns × refund − Restocking fees
Effective Margin = Gross Margin − Return Rate × (Margin loss + Reverse logistics cost)
```

- アパレル: 20–40% return
- フットウェア: 15–25%
- 化粧品: 5–10%
- 家電: 10–15%

### Inventory Turns / DIO

```
Inventory Turns = COGS / Average Inventory
DIO            = 365 / Inventory Turns
```

- アパレル D2C 平均: 3–5 turns/year (DIO 70–120 日)
- 食品: 12+ turns (DIO < 30 日)
- 家具: 2–4 turns

過剰在庫は markdown を強制し、Gross Margin を毀損する。Quarter 末の inventory aging を必ず確認。

### Cohort Revenue Retention

D2C では time-to-second-purchase と Year 2 cohort spend が決定的。

```
Cohort Year N Revenue = (Cohort 顧客の Year N 累積購買額 / Year 1 購買額)
```

ベンチマーク (Theta, RetentionX):
- Best-in-class アパレル: Year 2 cohort retention 80–120%
- Median: 40–60%
- 「Top 25% of customers acquired 2016–2019 spent $446 by 2020」(Allbirds S-1 開示の cumulative pattern)

## 2.2 ベンチマーク

| Metric | Median | Good | Great | 出典 |
|---|---|---|---|---|
| Gross Margin | 45% | 55% | 60%+ | Bainbridge / Allbirds (54.1%) |
| Contribution Margin (CM3) | 10% | 20% | 30%+ | RetentionX |
| AOV uplift YoY | 0–3% | 5% | 10%+ | Drivepoint |
| Repeat Rate (12mo) | 25% | 35% | 50%+ | Statista DTC |
| Return Rate (apparel) | 30% | 25% | <20% | NRF |
| CAC Payback | 12mo | 8mo | < 6mo | a16z DTC |

## 2.3 モデリング上の注意

- **Discount cadence を陽に**: Black Friday / EOSS の sale 頻度と depth を別 line に。Gross Sales → Net Sales への transition を必ず明示。
- **Returns を独立 driver**: SKU 別 return rate と markdown 時の rebate を計算。
- **Channel mix**: Shopify direct vs Amazon vs Wholesale で margin が大きく異なる (wholesale は 40–50% off retail)。
- **Inventory モデリング**: 発注 lead time + safety stock × 在庫保管費 + 廃棄/markdown を明示。
- **Repeat purchase intervals**: 商品ライフサイクルに応じた buying interval (アイウェア 2–3 年、シャンプー 2 ヶ月) を base に LTV を計算。
- **CAC blended vs new-customer**: 「マーケ費用 / アクティブ顧客」(Warby Parker S-1 が採用) は CAC を希釈する。「マーケ費用 / 新規取得顧客」が正攻法。
- **Free shipping threshold**: Free shipping の break-even を計算。送料負担の Net Revenue 計上か COGS 計上かで margin が変わる。

## 2.4 投資判断ロジック観点

1. **CM3 がプラスになる cohort age**: 新規取得時 CM3 がマイナスでも、6–12 ヶ月以内にプラスに転じるか。
2. **Repeat 比率の年次推移**: 50% 超が安定的に repeat であれば「ブランド資産」が形成されている。
3. **Return rate トレンド**: フィット改善 / サイジング工夫で改善できているか。
4. **在庫健全性**: aging buckets (0–30, 31–60, 61–90, 90+ days) と markdown 履歴。
5. **Channel distribution**: D2C 比率の変化。Wholesale 比率上昇は margin 圧迫。
6. **Brand pricing power**: 値上げを実施しても CVR / repeat が落ちないか。

## 2.5 開示例

- **Allbirds (S-1 2021)**: FY2020 Net Revenue $219M、Gross Margin 51.4%、Repeat 53%、Top 25% customers $446 cumulative spend を開示。Store と D2C のチャネル比率も提示。
- **Warby Parker (S-1 2021)**: 2020 CAC $40 (2019 $27 から 48% 上昇)、active customers 数、retail store + e-comm の比率。CAC 定義が「Marketing / Active customers」と異常に緩く批判された (Theta CLV 分析)。
- **Glossier, Casper, Stitch Fix**: いずれも Cohort spend curve を S-1 に図示。

## 2.6 落とし穴

- **AOV を Discount で水増し**: Gross AOV と Net AOV (after discount) を区別しない開示は要警戒。
- **Returns を control account から外す**: 返品処理が翌期に渡る場合、見せかけの margin になる。
- **Inventory write-down の遅延**: 売れ残り SKU を簿価維持して Gross Margin を温存している場合、後で爆発する (Allbirds 2022 の inventory 問題)。
- **CAC が paid のみ**: Organic / referral / brand を含めない Pure paid CAC は実態より低く見える。Blended CAC で比較すべき。
- **Wholesale 「stuffing」**: 流通在庫を期末に押し込んで売上計上する手法。Sell-through (顧客に売れた量) ではなく Sell-in (卸に売った量) を見ている可能性。

---

# 3. Fintech (Lending / Neobank / Payments)

## 3.1 サブカテゴリと主要メトリクスの違い

3 つのサブカテゴリでメトリクスがかなり異なるため分けて整理する。

### 3.1.1 Payments / Money movement (Stripe, Square, Adyen, Affirm)

```
TPV (Total Payment Volume) = Σ (処理した取引金額)
Take Rate                  = Net Revenue / TPV
Net Revenue                = Transaction fees − Interchange − Network fees − Processor cost
                             + Interest income (BNPL) + Float income
```

- Affirm: GMV(同社用語) baseの take rate は 8–10% レンジ。Split Pay (BNPL 4 回払) では merchant fee ~5%、長期 installment では merchant fee + interest income。
- Square (Block): take rate ~3% on TPV (Cash App / Seller 別)。
- Stripe: take rate ~2.7% (公開数値ではないが推定)。

### 3.1.2 Lending (Affirm 長期ローン部分, SoFi, OnDeck)

主要メトリクス:

```
Loan Origination Volume     = 期内新規貸出額
Loan Portfolio (avg)        = 平均ローン残高
Yield on Loans              = 利息収入 / Avg Loan Portfolio
Cost of Funds               = 借入費用 / Avg Funding Liabilities
NIM (Net Interest Margin)   = (利息収入 − Cost of funds) / Avg Earning Assets
NPL (Non-Performing Loans)  = 90日延滞以上のローン残高 / 全ローン残高
Net Charge-off Rate         = (Charge-offs − Recoveries) / Avg Loan Portfolio
CECL Provision %            = Allowance for credit losses / Loan Portfolio
LTV (Customer LTV)          = NIM × Avg loan size × tenure − loss − cost-to-serve
```

ベンチマーク:
- Prime consumer 個人ローン: NIM 6–10%, NCO 2–4%
- Subprime / near-prime: NIM 12–20%, NCO 8–15%
- BNPL (Affirm): NIM proxy で 5–8%、NCO 4–8%
- SMB lending (OnDeck, Kabbage): NIM 15–25%、NCO 8–15%
- Mortgage origination: NIM 1–2% but volume large

### 3.1.3 Neobank (Nubank, Chime, Revolut, Monzo)

```
ARPAC (Avg Revenue per Active Customer) = Monthly revenue / Avg Active Customers
Cost-to-Serve per Active Customer        = OpEx (excl. credit losses) / Active customers / month
Activation Rate                         = Active customers / Total registered
Cross-sell ratio                        = Avg products held per customer
Funding Cost / Deposit Yield mix
NIM, NCO (Lending あり Neobank の場合)
```

ベンチマーク:
- Nubank: ARPAC $12–13/month (Q2-Q3 2025), Cost-to-Serve ~$0.80/month で安定
- 米 Neobank (Chime): ARPAC $5–8/month
- LATAM 既存銀行 cost-to-income 45–50%, 米 Chime < 35%
- Active rate: Nubank 83% (2023), 起ち上げ期は 50–65%

## 3.2 Vintage Analysis (CECL 対応)

Vintage analysis は CECL 下で fintech lender の必須開示・必須モデリング。

```
Vintage Cohort = 同一期間 (月 / 四半期 / 年) に origination された loan のグループ
各 vintage の Loss curve = Cumulative loss / Original principal を MOB (Months on Book) でプロット
```

実務:
1. Origination 時に FICO band, DTI, vintage, channel ごとに segment 化。
2. 各 segment の historical loss curve を bootstrap。
3. Macro overlay (失業率、GDP) を multiplier で乗せる。
4. Lifetime expected credit loss (ECL) を計算 → CECL 引当 (Allowance for Credit Losses)。

> **CECL 下の落とし穴**: Day 1 で全 lifetime 損失を引当 → 高成長期は origination が増えるほど引当が PL を圧迫。Net income が見かけ赤字でも、Run-off ベースで見ると黒字構造の場合がある。

## 3.3 規制資本 (Banking license / 銀行免許保有 fintech)

```
CET1 Ratio       = Common Equity Tier 1 / Risk-Weighted Assets
Tier 1 Ratio     = Tier 1 Capital / RWA
Total Capital    = (Tier 1 + Tier 2) / RWA
Leverage Ratio   = Tier 1 / Total Assets
Liquidity Coverage Ratio (LCR)  = HQLA / Net cash outflow over 30d
```

ベンチマーク (バーゼル III):
- CET1 minimum: 4.5% + 2.5% buffer = 7%
- Tier 1: 6%
- Total: 8% + 2.5% = 10.5%
- Well-capitalized banks: CET1 12%+, Total 14%+

Charter を持たない fintech (Affirm 等) は banking partner 経由で origination するため自社規制資本は不要だが、warehouse facility の covenant で実質的に制約される。

## 3.4 ベンチマーク表

| Metric | Median | Good | Great |
|---|---|---|---|
| Take Rate (payments) | 2.5% | 3.0% | 3.5%+ |
| NIM (consumer prime) | 6% | 8% | 10%+ |
| NCO (consumer prime) | 4% | 3% | < 2% |
| NPL ratio (90+ DPD) | 3% | 2% | < 1.5% |
| ARPAC neobank | $5/mo | $10/mo | $15+/mo |
| Cost-to-serve neobank | $3/mo | $1.5/mo | < $1/mo |
| CAC payback (lending) | 18mo | 12mo | < 9mo |
| LCR | 110% | 130% | 150%+ |

## 3.5 モデリング上の注意

- **Origination volume × yield × loss を vintage で**: 全体 NIM は new origination mix に強く依存。Vintage cohort で expected loss を組み、origination 計画と組み合わせて P&L を bridge。
- **Cost of funds の mix**: Deposit funding (cheapest) vs Warehouse funding vs Securitization vs Equity の混合比率と各 cost rate を別 line に。Fed funds rate との相関を sensitivity に。
- **Loan loss reserve の Day 1 認識**: CECL では origination 時に lifetime loss を引当。高成長期はこれが「成長税」として PL を圧迫。
- **Float / Float income**: 顧客資金の interest を稼ぐビジネス (PayPal, Coinbase の cash holdings)。利上げ局面で大きく寄与。
- **Interchange revenue (Debit / Credit)**: Durbin amendment 対象 (asset $10B 超は規制 cap) かどうかで economics が激変。
- **Cross-sell economics**: SoFi の Financial Services Productivity Loop。1 顧客 1 product → 2 product で LTV 倍増の打ち出し。Cross-buy 比率を driver に。
- **Regulatory capital constraints**: 急成長で RWA が増えれば CET1 比率が下がり追加調達が必要。Bank charter 取得の Pros/Cons (cost of funds 低下 vs 規制負担) を明示。
- **Stress testing**: 失業率 +3pt, GDP -2% シナリオで NCO がどこまで上振れするかを必ず stress test。

## 3.6 投資判断ロジック観点

1. **Unit economics: per-loan or per-customer**: Origination 1 件あたりの lifetime contribution、cost-to-serve、損失見込みを reconcile。
2. **Vintage curves の安定性**: 直近 vintage が過去 vintage より loss が大きい (curve が上方シフト) なら underwriting 緩和または環境悪化。
3. **Cost of funds trajectory**: Cheap funding (deposit) を増やせるか。
4. **Cross-sell によるエンゲージメント**: ARPAC が経時的に上がっているか。
5. **Regulatory tailrisk**: Durbin 抵触、State usury cap、CFPB 規制動向。
6. **Leverage**: Equity / Loan portfolio 比率が低すぎる場合、loss 吸収力が不足。

## 3.7 開示例

- **Affirm (S-1 2020 / 10-K)**: GMV、Active consumers、Active merchants、Transactions per active consumer、Revenue Less Transaction Costs (RLTC)、RLTC / GMV を開示。Vintage の Cumulative Net Charge-Off curve を Risk Factors / MD&A で図示。Merchant concentration (Peloton 依存) を S-1 リスクで明示。
- **SoFi (10-K, 8-K)**: Members, Total products, Cross-buy rate (Q1 2026 で 43%)、ARPU at members and per-product。Lending segment、Tech Platform (Galileo)、Financial Services の 3 セグメント。
- **Nubank (20-F)**: Customers, Activity rate, ARPAC, Cost-to-serve per customer, NPL 15–90 days と 90+ days、Loan portfolio breakdown by product。Q3 2025 ARPAC $13.4、Cost-to-serve $0.80。

## 3.8 落とし穴

- **「Origination growth = Revenue growth」と見る**: Origination 多くても spread が薄ければ NIM 低下。
- **Loss provision を年度ごとに smoothing**: CECL の Day-1 認識は本来 lumpy。Adjusted EBITDA で hide すると経済実態が見えにくい。
- **Loan sale gain を Recurring 扱い**: 一部 lender は loan を warehouse に売って gain on sale を計上。これは originate-to-distribute モデル特有で、投資家視点では持続性低い。
- **Regulatory arbitrage 依存**: Bank partner との rent-a-charter モデルが規制で塞がれるリスク。
- **Concentration**: Affirm の Peloton 依存、Stripe の特定大口加盟店依存などは S-1 で開示される。

---

# 4. Hardware / IoT / Robotics

## 4.1 主要メトリクス

### Bill of Materials (BOM) と Gross Margin

```
BOM Cost      = Σ (component_i × qty_i)
Manufacturing = Direct labor + Yield loss + Overhead allocation
Landed COGS   = BOM + Manufacturing + Inbound freight + Duties + Tariffs
Gross Margin  = (ASP − Landed COGS) / ASP
```

実務上の追加考慮:
- **Yield rate**: 90% yield なら投入 BOM の 11% 余分が必要。
- **Scrap / Rework rate**: 品質不適合の再加工費用。
- **Tooling / NRE**: 金型・治具は capex として別途、unit cost には含めない or 償却で乗せる。
- **Manufacturing overhead allocation**: 工場固定費の単位配賦。

### Inventory aging と Working capital

```
Inventory Turns = COGS / Avg Inventory
DIO            = 365 / Inventory Turns
CCC = DIO + DSO − DPO
```

ベンチマーク (Hardware-heavy):
- Apple: Inventory turns 50+ (Tim Cook 流の supply chain magic)、DIO < 10 日
- Tesla: Turns 6–8、DIO 45–60 日
- 一般 hardware startup: Turns 3–5、DIO 75–120 日
- US 大手 non-financial median CCC: 37 日 (Hackett 2024)

> **モデリング論点**: Hardware は inventory が cash flow を支配する。10% growth in revenue でも inventory 投資が同じか先行して必要。在庫モデルを売上モデルと連動させて WC 必要額を算出。

### Razor-Blade Model (Hardware + Recurring Software)

```
Lifetime Value = Hardware Margin (one-time) + Recurring Margin × Subscription tenure
Payback (incl. recurring) = (Hardware loss + CAC) / Monthly recurring contribution
```

例:
- Peloton: Bike price $1,495、Connected Fitness Subscription $44/month。Hardware GM 13–17% (FY25), Subscription GM 60%+。Subscription が真の経済性を生む。
- HP Printers: ink subscription
- Keurig: pod
- Fitbit: device + premium

### Warranty Reserve / RMA

```
Warranty Reserve %         = 想定 warranty cost / Net Sales
RMA (Return Material Authorization) Rate = 返品・交換ユニット数 / 出荷ユニット数
```

ベンチマーク:
- 良質な consumer electronics: Warranty 1–3% of revenue, RMA 1–4%
- 平均: 3–5%, 5–8%
- 品質問題発生時: 10%+

### Channel mix

| Channel | GM impact |
|---|---|
| Direct (D2C web, brand store) | Highest GM (定価販売) |
| Retail wholesale (Best Buy, 量販店) | 30–40% margin to retailer → seller GM 圧迫 |
| Distributor (B2B) | 15–25% margin to distributor |
| OEM / Private label | Lowest margin、ボリューム勝負 |

Hardware startup は D2C 比率を高めて margin を確保しつつ、retail で reach を取る balanced strategy が一般的。

### Working Capital Cycle (CCC)

```
CCC = DIO + DSO − DPO
```

- Negative CCC 例: Apple, Dell (BTO 時代), Costco — supplier より顧客先払いが早い。
- Positive 大: 在庫を抱える hardware startup は CCC 100+ 日。Working capital 需要 = (CCC / 365) × Annual Revenue × COGS 比率。

## 4.2 ベンチマーク

| Metric | Median | Good | Great |
|---|---|---|---|
| Hardware GM (consumer) | 25% | 35% | 45%+ |
| Hardware GM (B2B / industrial) | 35% | 45% | 55%+ |
| Recurring SW GM (attached) | 70% | 80% | 85%+ |
| Inventory Turns | 4 | 8 | 12+ |
| DIO (days) | 90 | 45 | < 30 |
| RMA / Warranty | 5% | 3% | < 2% |
| CCC (days) | 90 | 45 | < 30 (or negative) |

## 4.3 モデリング上の注意

- **Unit economics by SKU**: SKU 別の BOM、ASP、GM、ライフサイクル (技術陳腐化、後継機投入) を別々にモデル。
- **Inventory モデル**: Forecast → 発注 lead time + safety stock + 季節性 → 月次在庫残高 → 期末在庫の aging 想定。
- **Tariff / Duty sensitivity**: 関税変動 (Section 301、追加関税) で Landed COGS が 10%+ 動く。
- **NRE 費用 (Non-Recurring Engineering)**: 金型、認証 (FCC, CE, PSE)、テスト治具は preflight cost。Unit margin に乗せず capex / OpEx で別管理。
- **後継機 cannibalization**: 新機種投入時の旧機種 markdown を計画に組み込む。
- **Recurring attach rate**: ハードウェア出荷の何 % が recurring service に attach するか。Peloton では 1 hardware に 1 subscription が紐づくが、HP printer ink では家庭購買率は限定的。
- **FX exposure**: 中国生産・USD 価格設定なら CNY/USD で BOM が変動。Hedging 政策を明示。
- **Capex schedule**: Tooling、テストライン、自社製造設備は減価償却を別 line。
- **Channel mix shift**: 上場後 retail 比率を上げると margin 低下、見かけの GM トレンドが悪化。

## 4.4 投資判断ロジック観点

1. **Hardware GM 単独で利益が出るか**: 「ハードは赤字でサブスクで黒字化」モデルは subscription churn に脆弱。
2. **Recurring attach + retention**: Connected fitness, IoT サービスでの subscription retention。Peloton の Subs Churn (~1.5–2% monthly) は良好だが hardware demand 失速で全体は苦戦。
3. **在庫健全性**: Aging buckets、E&O (Excess & Obsolete) reserve、後継機リリース時の旧機種残量。
4. **Supplier 依存度**: 単一サプライヤー依存 (例: 半導体特定品)、地政学リスク。
5. **Yield 改善曲線**: 量産立ち上げ期は yield 60–70% で start し、80%+ への改善が経済性決定。
6. **Capex efficiency**: Capex / Revenue が時間とともに低下するか (operating leverage)。

## 4.5 開示例

- **Peloton (10-K, S-1 2019)**: Connected Fitness Products GM、Subscription GM、Connected Fitness Subscriptions (paid subs 数)、Average Net Monthly Connected Fitness Churn を別個に開示。FY25 で Hardware GM 13.6% (+870bps YoY)、Subscription GM 60%+。
- **GoPro (10-K)**: Channel mix (Direct vs Retail) を明示。Subscription business (GoPro Subscription) を切り出し開示開始 (recurring の比率上昇を訴求)。
- **iRobot, Sonos, Fitbit**: Inventory metrics、Warranty reserve、Retail concentration (Best Buy, Amazon 依存) をリスクで開示。
- **Tesla**: Vehicle Deliveries, ASP, Auto GM excl. credits、Energy / Service segment 開示。Inventory days を明示。

## 4.6 落とし穴

- **Hardware「赤字でも将来 SW で取り戻す」**: SW take rate 仮定が楽観的。Subscription churn と ARPU 仮定を厳密に。
- **在庫の markdown 遅延**: 期末在庫を簿価で持ち越し → 翌期に大きな write-down (Allbirds, Peloton 過去事例)。
- **Capex を OpEx に流して GM を膨らます**: 設備投資を期間費用で処理せず資産化して減価償却の遅延 → 営業利益が見かけ良好。
- **Tooling NRE の capitalization**: 量産前 NRE を全額 capitalize すると単位 GM が高く見える。
- **Pre-order を Revenue 計上**: 配送前予約を Revenue で先取り計上は ASC 606 に抵触するが、bookings として別開示する企業もある。
- **チャネル詰め込み (Channel stuffing)**: 期末に retail へ卸を膨らませて売上計上 → 翌期 Sell-in が落ちる。
- **Tariff / FX を "one-time"扱い**: 構造的なコスト要因を non-recurring 扱いして adjusted GM を膨らます。

---

# 5. Bio / Pharma / MedTech

## 5.1 valuation の基本: rNPV (Risk-Adjusted NPV)

開発段階パイプラインの公正価値は **risk-adjusted NPV** (rNPV) で評価するのが gold standard。

```
rNPV = Σ_t [ PoS_t × CF_t / (1 + r)^t ]
```

- PoS_t: 当該時点までの累積成功確率
- CF_t: その時点でのキャッシュフロー (R&D 投資、milestone 受領、上市後売上、royalty 等)
- r: discount rate (10–13% が pharmaceutical 慣行)

### Phase 別 PoS (Probability of Success) ベンチマーク

BIO「Clinical Development Success Rates 2011–2020」(医薬全体):

| Transition | 全体 | Oncology | Hematology | Cardio | Rare disease |
|---|---|---|---|---|---|
| Phase I → II | 52% | 49% | 70% | 50% | 67% |
| Phase II → III | 29% | 25% | 35% | 22% | 32% |
| Phase III → NDA/BLA | 58% | 55% | 70% | 55% | 78% |
| NDA/BLA → Approval | 90% | 89% | 95% | 90% | 95% |
| **Phase I → Approval (cumulative)** | **7.9%** | **5.3%** | **16.4%** | **5.4%** | **15.9%** |

(値は近似、最新版 BIO レポートで都度更新する)

> **Biomarker 効果**: Patient stratification を biomarker で行うと oncology の overall PoS が ~5.5% → 10.3% に倍増 (medRxiv 2025 / 各種研究)。

### Phase typical Timeline と Cost

| Phase | 期間 | Cost (USD) | 主目的 |
|---|---|---|---|
| Preclinical | 1–3 年 | $1–10M | 動物・PK/PD・safety |
| Phase I | 1–2 年 | $5–30M | Healthy volunteers, safety, dose finding |
| Phase II | 2–3 年 | $20–100M | Patients, efficacy signal, dose optimization |
| Phase III | 3–5 年 | $100M–$1B+ | Pivotal efficacy, registration |
| Regulatory | 0.5–1.5 年 | $10–30M | NDA/BLA review |

合計開発コスト (発見 → 上市) は Tufts CSDD 推定で平均 $2.6B、Risk-adjusted で $1.3B (2014 推計)。

## 5.2 Royalty / Milestone 構造

Out-licensing deal の典型構造:

```
Upfront Payment    : Deal 締結時 一時金
Development Milestones : Phase II, III, Filing 等で支払い
Regulatory Milestones  : 各国承認時
Sales Milestones    : Net sales が threshold (例: $500M, $1B) 突破時
Royalty             : Net sales の % (mid-single to mid-teens %)
```

ベンチマーク (典型 deal):
- Preclinical asset out-license: Upfront $5–50M, Total milestones $100–500M, Royalty 5–10%
- Phase II asset: Upfront $50–300M, Milestones $300M–$1B, Royalty 8–15%
- Phase III asset: Upfront $300M–$1B, Milestones $500M–$2B, Royalty 10–20%

> **モデリング論点**: rNPV では各 milestone の支払いを「Phase 通過時 PoS で discount」する。Sales milestones は upside option として別途評価することも。

## 5.3 Regulatory Pathway

各国の承認経路と平均審査期間:

| Region | 主規制 | 標準審査 | Priority |
|---|---|---|---|
| US | FDA (CDER/CBER) | 10ヶ月 | 6ヶ月 (Priority Review) |
| EU | EMA (CHMP) | ~210 日 | Accelerated Assessment 150 日 |
| Japan | PMDA | 12ヶ月 | Sakigake (先駆け) 6ヶ月 |
| China | NMPA | 200 営業日 | 急用例外あり |

Special designation:
- **Breakthrough Therapy (FDA)**: 治療効果が著しい疾患で expedited
- **Fast Track**: serious condition で unmet need、開発初期から指定
- **Orphan Drug**: 希少疾患、市場独占権 7 年 (US) / 10 年 (EU) + 開発インセンティブ
- **Pediatric Exclusivity**: +6 ヶ月 market exclusivity
- **Priority Review Voucher**: pediatric rare / tropical disease で取得、譲渡可能 (公表取引で $80–350M)

### 日本 PMDA / 薬価特有

- 薬価収載: 申請から ~60–90 日で中医協で薬価収載
- 薬価改定: 2 年に 1 度 (現在は毎年改定移行)、原則的引下げ
- 新薬創出加算: 革新性高い新薬は薬価維持、ジェネリック参入後は引下げ
- 費用対効果評価 (HTA): 高額医薬品で QALY ベース評価導入

## 5.4 Patent Cliff / LOE (Loss of Exclusivity)

```
Patent Expiry → Generic / Biosimilar 参入
- 小分子薬: 1 年で 60–80% 売上減
- バイオ薬 (biosimilar): 3 年で 30–50% 減 (interchangeable 取得タイミングによる)
```

モデリングでは LOE 後の sales erosion curve を以下のテンプレで:
- Year 1 post-LOE: -50% (small molecule), -15% (biologic)
- Year 2: -75%, -30%
- Year 3+: -85%, -50%

## 5.5 Reimbursement / 償還

販売数量と価格を決定する最重要因子。

- **米国**: PBM (CVS Caremark, Express Scripts), Medicare Part D coverage、Formulary placement、Rebate (典型 list price から 20–50% rebate)
- **欧州**: 各国で HTA (NICE 英、IQWiG 独、HAS 仏)、参照価格制度
- **日本**: 中医協で算定方式 (類似薬効比較方式 or 原価計算方式)、外国平均価格調整

> **Net Price vs List Price**: 米国では list price と net price (after rebate) の乖離が極端。Net price で経済性を評価。

## 5.6 ベンチマーク

| Metric | Range |
|---|---|
| Phase I→Approval (overall) | 8% |
| Phase I→Approval (oncology) | 5% |
| Discount rate | 10–13% |
| GM (small molecule branded) | 80–90% |
| GM (biologics branded) | 70–85% |
| GM (generic) | 30–50% |
| R&D / revenue (Big Pharma) | 15–20% |
| SG&A / revenue (Big Pharma) | 25–30% |
| Peak sales / first year | 5–15x |
| Time to peak from launch | 4–7 年 |

## 5.7 モデリング上の注意

- **Cash flow waterfall を Phase 別**: R&D investment, Milestone receipts, COGS post-launch, S&M ramp を別 line。
- **Peak sales curve**: Launch → ramp → peak → LOE decline の 4 フェーズで型を作る。Analog drugs (similar disease, similar efficacy) を proxy にする。
- **Probability tree**: 各 Phase で「成功 / 失敗」分岐を明示し、scenario probability を documenting。
- **Scenario analysis**: Bull (faster approval, higher peak), Base, Bear (delay, lower peak) で rNPV レンジを提示。
- **Multi-indication**: 単一化合物が複数 indication で開発される場合、各 indication で別 rNPV → 統合。
- **Royalty waterfall**: 売上 tier 別 royalty step-up (例: $500M まで 8%、$500–1B で 12%、$1B 超 15%)。
- **Capital需要**: Phase III は cash-burn が最大。Cash runway モデルで「次の milestone まで何ヶ月」を必ず明示。

## 5.8 投資判断ロジック観点

1. **PoS 仮定の plausibility**: Sponsor R&D strength、Phase II データ品質、biomarker 有無で PoS を adjust。
2. **Peak sales 仮定**: Patient population × Treatment penetration × Treatment duration × Net price で bottoms-up に積み上げ。Top-down (analog drug の peak) と reconcile。
3. **Patent runway**: 上市から LOE までの effective exclusivity 期間。
4. **Regulatory tail risk**: BLA/NDA reject、CRL (Complete Response Letter) のシナリオ。
5. **Competitive landscape**: 同 MoA (Mechanism of Action) で先行・後続。First-in-class vs Best-in-class。
6. **Cash runway**: 次の Milestone (data readout) まで cash があるか。
7. **Out-licensing deal の構造**: Royalty step-up、territory split、rights reversion。

## 5.9 開示例

- **Moderna, BioNTech, CRISPR**: pipeline graphic で indication × Phase × milestone を提示。
- **大手 pharma (Merck, Pfizer)**: 個別品目別 net sales を開示、LOE 影響を guidance で言及。
- **Bio バイオベンチャー (S-1)**: lead candidate の Phase 進捗、milestone schedule、cash runway (months)、operating cash burn rate (per quarter) を Risk Factors に明示。
- **MedTech (Intuitive Surgical, Edwards)**: Installed base (devices placed), Procedures volume, Recurring (instrument & accessories) revenue per device を開示。
- **Diagnostics (Guardant, Exact Sciences)**: Test volume、ASP per test、Reimbursement coverage の地理進捗。

## 5.10 落とし穴

- **PoS 自前推計の楽観バイアス**: Sponsor 自身は historical industry average より高 PoS を主張する傾向。BIO 業界平均で sanity check。
- **Peak sales を analog drug の最大値で**: Comparable analog の median/mean を使うべき。
- **List price で revenue 計算**: 米国では Net price (rebate 後) を使う。Gross-to-net adjustment 30–40% を見込む。
- **Generic erosion curve を緩く**: 多くの biotech モデルが LOE 後の decay を過小評価。
- **R&D 全額即時費用化 vs Capitalize**: GAAP は基本即時費用化 (development の一部 conditions を満たせば capitalize 可)、IFRS は development phase の一部要件下で capitalization 可。倍率比較で揃える。
- **Milestone 受領を Recurring 扱い**: Lump-sum milestone は不規則。Run-rate 評価から除外。

---

# 6. Media / Content / Creator

## 6.1 主要メトリクス

### Engagement: DAU / MAU / Stickiness

```
DAU             = Daily Active Users (24h period)
MAU             = Monthly Active Users (30d period)
Stickiness      = DAU / MAU
Time spent      = Σ user time / DAU or MAU
```

ベンチマーク:
- Stickiness: top consumer (Facebook, Instagram) 60–70%, mid 30–50%, low 15–25%
- Roblox: DAU 132M (Q1 2026), Hours engaged per DAU per day ≈ 7.8h (31B hours / 132M DAU / 30 days × 通常 30 日換算で月次合計)
- Spotify: MAU 761M (Q1 2026), active subscriber 263M (Q4 2024)

### ARPU 系

```
ARPU       = Total revenue / Avg users (期間)
ARPU split = ARPU(Subscription) + ARPU(Advertising) + ARPU(Other)
```

サブスクと広告の両建ての場合:

```
ARPU(subscription) = Subscription revenue / Avg paying subscribers
ARPU(ad)            = Ad revenue / Avg ad-supported users (or MAU)
```

例:
- Spotify Premium ARPU: €4.76 (Q1 2026, ほぼ flat YoY)
- Spotify Ad-supported revenue per ad MAU: 算出 (€385M / 483M MAU / 3 months) ≈ €0.27 / month
- Netflix ARPU (US): $17–18/month (2024)

### 広告系メトリクス

```
CPM (Cost per Mille)        = Ad cost / Impressions × 1,000
CPC (Cost per Click)         = Ad cost / Clicks
CPA (Cost per Action)        = Ad cost / Conversions
eCPM                         = Total ad revenue / Impressions × 1,000 (publisher 視点)
Fill rate                    = Filled impressions / Total impressions
```

ベンチマーク (USD CPM):
- Connected TV: $20–40
- Premium video web: $15–30
- Mobile in-app video: $5–15
- Mobile in-app banner: $0.5–2
- Programmatic display: $1–5
- Native ad: $3–10

### Content 投資の会計

```
Content Asset (BS) = Capitalized content cost
Content Amortization = Method による (straight-line, accelerated, individual title)
```

Netflix モデル:
- Licensed content: 契約 fee を全額 capitalize、契約期間 or 推定使用期間 (max 10 年) で償却
- Produced content: 制作費を capitalize、初回放映から推定使用期間で償却 (主に accelerated curve、 first 2 years が前倒し)

Disney / Netflix の 10-K 比較:
- Netflix: 2024 年 content amortization $21B、+6% YoY
- Content investment が cash 先行で発生、PL での amortization は遅行 → Cash from operations が乏しく FCF が遅れて改善

### Subscriber Acquisition Funnel

```
Free trial  → Conversion → Paid → Retention → Churn
```

- Free trial conversion: 50–70% (best Netflix-style), 20–40% (mid)
- Monthly churn: Streaming 4–7%, Music 1–3%, News 2–5%

### Content Library Health

- **Total titles / minutes available**
- **Catalog depth by genre** (rights expiration)
- **Recently added (engagement weighting)**
- **Originals vs Licensed mix**: Original 投資は capex 重いが longer-term margin 有利

## 6.2 ベンチマーク

| Metric | Median | Good | Great |
|---|---|---|---|
| Stickiness (DAU/MAU) | 25% | 40% | 60%+ |
| Subscription monthly churn | 5% | 3% | < 2% |
| Ad fill rate | 70% | 85% | 95%+ |
| ARPU growth YoY | 0% | 3% | 8%+ |
| Content amort / Revenue (streaming) | 50% | 40% | < 35% |
| GM | 30% | 45% | 60%+ |

## 6.3 モデリング上の注意

- **Subscription と Ad は別事業**: P&L を双方向に分離。Cross-subsidy (ad-supported tier → premium upgrade) を別途モデル。
- **Content investment と Amortization の cash gap**: Content P/L 影響と Cash flow 影響を区別。Cash flow モデルでは「Content investment」を独立 line として capex 的に扱い、PL では amortization で expense する。
- **Originals vs Licensed の Margin**: Originals は marginal cost 低 (成功すれば re-watching の incremental cost ~0)。Licensed は契約更新で cost 跳ね上がる。
- **Subscriber lifetime**: Roblox は paying user lifetime ~27 ヶ月で deferred revenue を認識。LTV モデルで lifetime と churn を crosscheck。
- **DAU の定義**: Roblox は「アカウント単位」と注記 (一人で複数アカウント使用)。Active definition が緩い企業は DAU が水増し。
- **Ad load tradeoff**: Ad load 増 → 短期 Revenue 増だが engagement 低下 → 長期 LTV 毀損。
- **Creator economy 配分**: YouTube 55%, Roblox developer payout (Q1 2026 で revenue の 29%, bookings の 24%) を control。配分率変更は両サイドの supply に影響。

## 6.4 投資判断ロジック観点

1. **エンゲージメント depth**: Time spent per DAU が経時的に伸びているか。
2. **Subscription churn が低位安定**: 価格上げ余地。
3. **Content efficiency**: Content investment / hours watched、 originals の hit rate。
4. **広告 CPM trend**: Premium video CPM の業界比較。Programmatic vs direct sales の比率。
5. **Creator/supply 健全性**: payout 配分率、top creator concentration。
6. **Bookings vs Revenue gap**: deferred revenue trend で先行指標を把握。

## 6.5 開示例

- **Netflix (10-K)**: Paid memberships by region, ARM (Average Revenue per Membership), Content amortization, Cash content spend, Streaming content obligations。Free cash flow を guidance。
- **Spotify (20-F, Quarterly)**: Premium MAU, Ad-supported MAU, Premium ARPU, Gross Margin (Premium vs Ad-supported)。Q1 2026: MAU 761M (+10M)、Premium ARPU €4.76、Ad-supported revenue €385M。
- **Roblox (10-K)**: DAU, Hours engaged, Bookings, Average Bookings per DAU, Estimated average lifetime of paying user (~27 ヶ月)、Developer Exchange Fees (Q1 2026 で revenue の 29%, bookings の 24%)。Bookings は initial で deferred revenue として計上。
- **Disney+, Warner Bros Discovery**: Subscribers, Monthly ARPU、Content cash spend を segment 別開示。
- **NYT (digital media)**: Digital-only subscribers, ARPU per subscriber、Bundled vs single-product 比率。

## 6.6 落とし穴

- **DAU の定義inflation**: Multi-account, bot, shared login が含まれる定義は実態より多い。
- **Content amortization の loaded curve**: Accelerated curve で early loss、後続 quarter で margin 改善に見える。Curve assumption を必ず確認。
- **Subscription「Free / Promo」を Paid 扱い**: Promo 期間中の subscriber を paid で開示する企業がある。Net adds の見せ方に注意。
- **MAU と paying subscriber の混同**: Spotify は両方開示、混同しない。
- **広告 fill rate を高く保つために CPM を下げる**: 広告 revenue の質低下。
- **Creator payout の改定**: payout share の上下は creator supply に直接効く。事前 disclosure と historical changes を確認。

---

# 7. B2B Services / Consulting

## 7.1 主要メトリクス

### Utilization Rate

```
Utilization Rate = Billable Hours / Total Available Hours
```

職階別の典型 target:
- Junior consultant / Analyst: 65–75%
- Mid-level / Manager: 75–85%
- Senior / Partner: 30–60% (営業・組織運営に時間)

業界 (2025 SPI ベンチマーク):
- Professional services overall: 66.4% (2024 68.9%)
- Management consulting: 67.4% (2024)
- Optimal threshold: 75%

### Average Billable Rate

```
ABR = Total Billings / Billable Hours
Blended ABR = Σ (Hours_role × Rate_role) / Total billable hours
```

ベンチマーク (USD/hr):
- Big 4 advisory: Senior Manager $400–700, Partner $800–1,500
- MBB (McKinsey, Bain, BCG): Associate $300–500, Partner $1,200–3,000
- Boutique strategy: $200–800
- Mid-market consulting: $150–400
- Implementation / IT: $100–300

### Project Margin

```
Project Margin = (Project Revenue − Project Direct Cost) / Project Revenue
Direct Cost    = Consultant cost (billable + non-billable allocated) + T&E + Subcontractor
```

ベンチマーク:
- Strategy consulting: 50–70% project margin
- Implementation: 30–45%
- Staff augmentation / body shop: 20–35%

### Pipeline Coverage / Win Rate

```
Pipeline Coverage = Open pipeline value / Quota (期間)
Win Rate          = Won deals / Total decided deals
```

- Pipeline coverage: target 3–4x の Quota
- Win rate by stage: top of funnel < 20%, mid 30–50%, late stage 60–80%

### Headcount-Driven Revenue Model

人月モデルの基本式:

```
Revenue = Σ (Headcount_role × Utilization × Hours_per_year × Billable Rate)
EBITDA = Revenue − Direct Comp − S&M − G&A
```

- Direct Comp: 給与 + ベネフィット (40–60% of revenue が consulting の典型)
- Bench cost: Non-utilized 人員も給与発生
- Compensation leverage: Senior 1 名 / Junior 5–8 名の pyramid で margin を確保

### DSO, Project WIP

```
DSO = Average AR / (Annual Revenue / 365)
WIP = Unbilled work performed but not yet invoiced
```

- 大手 consulting DSO: 60–90 日
- Project WIP: progress milestone まで未請求の time × rate
- Long collection cycles → 受注急増局面で WC 圧迫

## 7.2 ベンチマーク

| Metric | Median | Good | Great |
|---|---|---|---|
| Utilization (consultants) | 65% | 75% | 85%+ |
| Bench % | 30% | 20% | < 15% |
| Project margin (strategy) | 50% | 60% | 70%+ |
| EBITDA margin | 15% | 20% | 30%+ |
| DSO | 75 | 60 | < 45 |
| Pipeline coverage | 2.5x | 3.5x | 4x+ |
| Win rate (qualified) | 30% | 45% | 60%+ |
| Revenue per consultant | $250k | $400k | $600k+ |

## 7.3 モデリング上の注意

- **Headcount を主要 driver に**: Consultant FTE × Utilization × Bill rate × Annual hours = Revenue。 SaaS の ARR モデルではない。
- **Hiring / Ramp**: 新規入社 6 ヶ月程度は productivity 低い。Ramp curve (10/30/60/90% by 月) を入れる。
- **Pyramid mix**: Senior/Mid/Junior の比率と各 rate × utilization → blended economics。
- **Bench cost**: 利用されない時間も給与発生。Hiring を需要の少し後に置く政策で管理。
- **Project mix**: Time & Material (T&M, 固定 rate × hours) と Fixed Price (FP, 成果物 fixed) で margin リスクが異なる。FP では over-run が margin 喰い。
- **Subcontractor leverage**: 外注委託で marginal capacity を確保、margin は 5–15pt 低い。
- **Geographic mix**: US/EU vs インド・東欧 offshore で rate と labor cost が大きく異なる。
- **Currency exposure**: Cross-border project は FX hedge ポリシーを明示。
- **DSO sensitivity**: 受注急増時 DSO 悪化は WC 圧迫。Factoring / 前受で緩和可能か。

## 7.4 投資判断ロジック観点

1. **Utilization の安定性**: 75% を超えて維持できているか。下落トレンドはバックログ枯渇の先行指標。
2. **Bill rate 上昇余地**: Industry standard まで余地があるか、過去の値上げ実績。
3. **Project type mix**: T&M 比率高 (低リスク低 margin) vs FP 高 (高リスク高 margin)。
4. **Repeat business / Account expansion**: Top 10 client の年次再受注率。LTV proxy。
5. **Pyramid leverage**: Senior 1 人あたり junior 何人で運営できているか。
6. **Talent retention**: voluntary turnover が業界 (15–20%) より低いか。
7. **Productized service / IP-based**: 純粋 hours billing より productized (固定パッケージ) 化された比率。Recurring 収益化の進捗。

## 7.5 開示例

- **Accenture, Booz Allen Hamilton, EPAM**: Bookings (新規受注), Utilization, Headcount, Revenue per employee を IR で開示。
- **PE 保有 boutique**: Utilization と Bill rate trajectory を Mgmt presentation で開示。
- **Tech consulting (Slalom, Infosys)**: Onsite/Offshore mix、 Vertical 別 revenue を 10-K に。
- **Japan SI**: 工数単価 (人月単価) ベースで開示、案件 backlog (受注残) を IR 説明会で示す。

## 7.6 落とし穴

- **Utilization 100% 超**: Burnout を意味する。長期持続不可能、turnover 上昇の前兆。
- **新規受注 (Bookings) と Revenue の混同**: Revenue は per-period の確定実現額。
- **Project over-run の隠蔽**: FP project で予算超過しても WIP に積み上げて margin を一時的に守る → 後で write-down。
- **Headcount 増 = 成長と単純評価**: Productivity per head が下がっていれば成長は希薄。
- **Off-balance subcontractor 依存**: 外注比率を抑えていない場合、需要急増で margin 急落。
- **Repeat business の inflation**: 同一クライアントの follow-on を「new deal」として扱う集計ミス。

---

# 8. Manufacturing / Industrial

## 8.1 主要メトリクス

### Capacity Utilization と OEE

```
Capacity Utilization = Actual Output / Maximum Possible Output
OEE = Availability × Performance × Quality
  Availability = Run Time / Planned Production Time
  Performance  = (Total Count × Ideal Cycle Time) / Run Time
  Quality      = Good Count / Total Count
```

ベンチマーク:
- 製造平均 OEE: 60%
- 業界平均 (一般的に「acceptable」): 65–75%
- World-class: 85%+ (Availability 90%, Performance 95%, Quality 99.9%)
- 半導体・電子: top quartile 80%+

### Operating Leverage

```
Operating Leverage = % Change in EBIT / % Change in Revenue
                   ≈ (Revenue − Variable Cost) / EBIT
```

- 高 capex / 高 fixed cost manufacturer (鉄鋼、化学、半導体): Operating leverage 3–5x
- Light asset (組立中心): 1.5–2x
- 利上げ / 不況局面で revenue 10% 減 → EBIT 30–50% 減のシナリオを stress test

### Backlog & Book-to-Bill

```
Backlog        = 受注残 (受注済・未出荷)
Book-to-Bill   = New Bookings (期間内受注) / Billings (期間内出荷)
```

- 1.0 が需要・供給の equilibrium。
- 1.0 超 = 受注が出荷を上回る (バックログ増、需要強)。
- 1.0 未満 = 在庫消化フェーズ (需要弱)。
- 半導体装置 (Lam, Applied Materials): 1.2–1.5 の局面で投資家強気。
- 米国半導体 SIA は月次で Book-to-Bill 公表 (現在は IDM ベースで限定的)。

### Inventory Cycle と Raw Material Exposure

```
Raw Material days = (Raw Material Inventory / Material COGS) × 365
WIP days          = (Work-in-Process / Total COGS) × 365
Finished Goods days = (FG / COGS) × 365
Total inventory days = Sum
```

- Just-in-Time (Toyota): Total inventory < 30 日
- Process industry (chemical): 60–90 日
- Heavy equipment: 90–150 日

Raw material price exposure:
- Hedging policy (futures, fixed-price contracts) を明示。
- Pass-through ability (顧客への原料費転嫁能力)。

## 8.2 ベンチマーク

| Metric | Median | Good | Great |
|---|---|---|---|
| OEE | 60% | 75% | 85%+ |
| Capacity utilization | 70% | 85% | 90%+ |
| Inventory turns | 6 | 10 | 15+ |
| Gross margin (asset-heavy) | 20% | 30% | 40%+ |
| Gross margin (asset-light assembly) | 15% | 25% | 35%+ |
| EBITDA margin | 10% | 18% | 25%+ |
| Book-to-Bill | 0.95 | 1.10 | 1.20+ |
| Capex / Revenue | 8% | 5% | < 4% |

## 8.3 モデリング上の注意

- **Capacity モデリング**: Plant-level theoretical capacity × OEE × ramp curve = practical output。
- **Capex schedule**: 大規模設備投資 (新工場 $100M+) は減価償却 (15–25 年) で margin に重力。
- **Variable vs Fixed Cost**: 直接材 (variable) と 直接労務 + 間接費 (mixed) の分解。Operating leverage の根幹。
- **Pricing pass-through**: 原料急騰時、価格転嫁の lag (3–6 ヶ月) を margin モデルに反映。
- **Forex translation**: 海外工場 (中国、ベトナム、メキシコ) の cost 通貨と販売通貨の mismatch。
- **Yield 改善曲線**: 新工場立ち上げ初期は 70–80% yield、 12–18 ヶ月で 90%+ への ramp。
- **Maintenance capex vs Growth capex**: Maintenance は recurring、Growth は discretionary。FCF 議論で必ず分離。
- **Working capital scaling**: Revenue 1.5x growth で WC 1.3–1.5x が必要 (DIO + DSO 比例)。

## 8.4 投資判断ロジック観点

1. **OEE trajectory**: Continuous improvement で 1–2pt/year の改善が一般的目標。
2. **Capacity utilization が 90% 接近**: 増設タイミング、capex sizing。
3. **Book-to-Bill > 1.0 持続**: 需要強含み。
4. **Operating leverage の上下振り**: Cycle peak / trough での EBIT 振れ幅。
5. **Pricing power**: 原料 pass-through %、過去サイクルの margin volatility。
6. **Capex efficiency**: Asset turnover (Revenue / Net PPE) が業界 median を超えるか。
7. **Cycle position**: 業界 cycle (構造的需要 vs 在庫調整) のどこにいるか。

## 8.5 開示例

- **Caterpillar, Komatsu, Deere**: Backlog (受注残)、Dealer inventory、Sales by region・product family、Operating margin by segment。
- **半導体装置 (Applied, Lam, KLA)**: System backlog、Service revenue (recurring 性高い)、Geographic sales、Memory/Logic mix。
- **Auto OEM (Toyota, GM)**: Production volume、Wholesale vs Retail、Days of supply、Incentive per vehicle。
- **化学・素材**: Volume × Price decomposition、Capacity utilization、Feedstock cost trends。

## 8.6 落とし穴

- **Backlog の質**: 一部「ソフト LOI」「キャンセル可能オーダー」を hard backlog に含める企業がある。Coverage 期間 (backlog / quarterly revenue) も併用。
- **Inventory build-up を「受注対応」と説明**: 過剰在庫が cycle 終盤に markdown を強制。
- **Capex の lumpiness を smoothing**: 一時的な軽量化は持続性無し。
- **Energy / 原料 cost を non-recurring 扱い**: 構造的 cost を adjusted EBITDA で hide する。
- **Plant idle cost を COGS から OpEx へ振替**: GM が見かけ改善するが実態変化なし。
- **Sale-leaseback で見かけ ROIC 改善**: BS から asset を消すが本質的経済性は変わらない。

---

# 9. Real Estate / PropTech

## 9.1 主要メトリクス

### NOI (Net Operating Income) と Cap Rate

```
NOI = Effective Gross Income − Operating Expenses (excl. mortgage, capex, depreciation)
Cap Rate = NOI / Property Value
Implied Property Value = NOI / Cap Rate
```

- Cap Rate は逆 yield: 5% cap rate ⇔ 20x NOI。低 cap rate = 高評価。

ベンチマーク (US 2025):
- Multifamily (apartment): 5.0–5.5% cap
- Industrial / Logistics: 5.0–6.0%
- Office (Class A): 7.5–9.0% (post-COVID 上昇)
- Retail (grocery anchored): 6.5–7.5%
- Hotel (full-service): 7.5–9.5%
- Hotel (luxury): 6.0–7.5%

### IRR と Equity Multiple

```
IRR = Discount Rate at which NPV(cash flows) = 0
Equity Multiple = Total Distributions / Equity Invested
DCF Period      = Hold period (典型 5–10 年)
Exit Cap Rate   = 売却時 cap (典型 entry cap + 25–75bps)
```

ベンチマーク (PE real estate):
- Core: IRR 7–10%, Equity Multiple 1.5x
- Core-plus: IRR 10–13%, EM 1.7x
- Value-add: IRR 13–18%, EM 2.0x
- Opportunistic: IRR 18%+, EM 2.5x+

### Hospitality: RevPAR / ADR / Occupancy

```
ADR (Average Daily Rate)   = Room Revenue / Rooms Sold
Occupancy                  = Rooms Sold / Available Rooms
RevPAR (Revenue per Available Room) = Room Revenue / Available Rooms
                                    = ADR × Occupancy
TRevPAR                    = Total Revenue per Available Room (room + F&B + その他)
```

ベンチマーク (US 2025–2026):
- National occupancy: 61.7% (2026 forecast)
- Luxury: 67–75% occupancy, RevPAR $210–450
- Mid-scale / Economy: 55%, RevPAR $50–80
- Upper-upscale (Marriott Marquis 等): 70%+, RevPAR $150–250

### 開発パイプライン Cash Flow

```
Year 0: Land acquisition (equity + debt)
Year 1–2: Construction (capex draws against construction loan)
Year 2–3: Lease-up / Stabilization
Year 3–10: Operations (NOI generation)
Year 10: Exit (refi or sale at exit cap)
```

主要 metric:
- **Yield on Cost** = Stabilized NOI / Total Development Cost (target 6–8%, vs market cap 5–6% で 100–200bps spread)
- **Lease-up timeline**: Class A multifamily 12–18 ヶ月で 90% occupancy 達成想定
- **Construction cost / unit** や / SF: 地域市況依存
- **Pre-leasing %**: Office, retail で 開業前にどの程度 lease 確保か

## 9.2 ベンチマーク

| Metric | Multifamily | Industrial | Office | Hotel |
|---|---|---|---|---|
| Cap rate | 5.0–5.5% | 5.0–6.0% | 7.5–9.0% | 7.5–9.5% |
| Stabilized occupancy | 93–96% | 95–97% | 80–90% | 60–75% |
| OpEx / Revenue | 35–45% | 25–35% | 35–45% | 65–75% |
| Capex / Revenue (recurring) | 5–8% | 3–5% | 8–12% | 6–10% |
| Yield on cost premium | +75bps | +75bps | +100bps | +100–150bps |

## 9.3 モデリング上の注意

- **Lease structure を陽に**: Multifamily は 1 年 lease (短期 reset)、 Office/Retail は 5–10 年 lease (CPI 連動 escalation)。Lease roll schedule と market rent gap を明示。
- **Occupancy ramp**: 新規 lease-up 期は physical vs economic occupancy を区別。Free rent / TI (tenant improvement) concession の cash 影響。
- **OpEx pass-through**: NNN (Triple Net) lease は OpEx を tenant 負担。Gross lease は landlord 負担で margin が圧縮。
- **Refinancing assumptions**: Stabilization 後の cash-out refi で equity を引き戻す前提を明示。Interest rate sensitivity 必須。
- **Debt structure**: LTV (Loan-to-Value), LTC (Loan-to-Cost), DSCR (Debt Service Coverage Ratio = NOI / Debt service)。Bank covenants の詳細。
- **Hospitality は capex 重い**: 客室・F&B のリノベが 7–10 年サイクル。Capex を OpEx と分離して FCF を計算。
- **Cap rate は exit に最も sensitive**: Sensitivity table で entry cap ± 50bps, exit cap ± 50bps を必ず提示。

## 9.4 投資判断ロジック観点

1. **NOI growth trajectory**: Same-property NOI growth 2–4%/year が市況 normal。
2. **Lease roll**: Mark-to-market opportunity (現行 lease rate vs market rate ギャップ)。
3. **Occupancy sustainability**: Submarket vacancy trend。
4. **Cap rate spread vs interest rate**: 10Y Treasury との spread (200–300bps が historical)。スプレッド縮小は warning。
5. **Hospitality cycle**: RevPAR トレンド、segment mix (luxury 強、 economy 弱)。
6. **Debt maturities**: Refi wall (2–3 年内に大量の debt が満期) は流動性 risk。
7. **Property-level vs Fund-level returns**: Sponsor fee (acquisition, asset management, disposition) を控除した investor net IRR。

## 9.5 開示例

- **REITs (10-K)**: Same-store NOI growth, Occupancy, Average rent, Capex, FFO (Funds from Operations), AFFO (Adjusted FFO)。
- **PropTech Marketplaces (Zillow, Redfin, Opendoor)**: Listings, Transactions, Take rate, Inventory days (iBuyer)。
- **Hotel REITs (Host, Park)**: RevPAR, ADR, Occupancy by segment、CapEx schedule。
- **PE Real Estate**: 投資家報告で property-level IRR/EM、Fund-level net IRR/EM を分離開示。

## 9.6 落とし穴

- **Cap rate は forward-looking**: Trailing NOI / current price だと評価。Forward NOI で should-be 評価。
- **NOI に capex を含めない**: 厳密 NOI には capex 除外。Recurring capex を引いた AFFO/cash NOI で評価。
- **Concession 込み face rent**: Effective rent (concession 控除後) を使う。
- **iBuyer の inventory mark-to-market**: Opendoor は inventory holding period の市場下落リスクを抱える。Inventory mark-to-fair-value の頻度。
- **Hospitality「stabilized」前の運営年データ**: Lease-up 期の数字を stabilized 扱いすると過大評価。
- **Development overruns**: Construction cost +10–20% の overrun は scenario に必ず。

---

# 10. AI / Foundation Model

## 10.1 主要メトリクス

### Compute Cost as % of Revenue

```
Compute Cost = Training Compute + Inference Compute + Data Storage + Networking
COGS         = Compute Cost + Personnel (research) + Hosting overhead
Gross Margin = (Revenue − COGS) / Revenue
```

公開シグナル (2025–2026):
- OpenAI compute margin: ~35% (Jan 2024) → ~70% (Oct 2025) と急改善 (Information / SaaStr 報道)
- Anthropic GM target: 2025 で 50%, 2028 で 77% (内部資料報道)
- 多くの「AI app」スタートアップは underlying API cost で 30–50% GM 止まり (B2B SaaS の 70–80% に劣る)

### Training Run Amortization

```
Training Run Cost   = GPU/TPU hours × Hourly rate + Data prep + Researcher time
Useful Life of Model = 6–12 ヶ月 (前線モデル)、12–24 ヶ月 (後方モデル、open-weight)
Monthly Amortization = Training Cost / Useful Life
```

GPT-4 class training: 推定 $50–100M (2023 当時)。GPT-5 class: $500M–$1B 以上の推定 (2024–25)。
Frontier モデルのライフは継続短縮 → Capex/OpEx 議論の論点。

### Inference Cost per Request / per Token

```
Cost per request = (Input tokens × cost_in/M) + (Output tokens × cost_out/M)
Effective margin per request = (Price − Cost) / Price
```

API 価格 (2026 5月時点参考、 各社継続変動):
- Claude Opus 4.6: $5.00 / $25.00 per M tokens (input/output)
- Claude Sonnet 4.6: $3.00 / $15.00
- Claude Haiku 4.5: $1.00 / $5.00
- GPT-5.4: $2.50 / $15.00 (相対比較で Opus 比 40–50% 安価)

Internal compute cost (報道推定):
- Output token compute ~$0.50–3.00 per M (極めて変動)、Input は output の 1/100–1/1000 (KV cache 等で再利用効率高)
- 結果として API 売上の対 compute cost 比率は 5–20x → API は software 級 margin、消費者向け subscription はチャット集中で marginal cost が嵩み margin 低い

> **Asymmetry**: Input vs Output compute cost の極端な非対称性 (output ~1000x cost)。Input-heavy use case (large context retrieval) は profit が出やすい。

### Model Lifecycle (減価償却 analog)

実会計上の取扱い (現行慣行):
- 訓練コスト R&D 即時費用化が一般 (US GAAP)
- 一部企業 (Google, Microsoft) は cloud datacenter capex に GPU を含めて減価償却 (3–6 年)
- Frontier モデルの effective economic life は 12 ヶ月 ± なので会計と経済実態に乖離

簡易 economic depreciation:
```
Economic Depreciation per quarter = Training Cost / 4 quarters of useful life
```

### Token Economics (顧客側)

エンドユーザーのコスト式:
```
User cost = (Avg Input Tokens × Price_in) + (Avg Output Tokens × Price_out) + Caching Discount
Effective margin for vendor = User Price − Compute Cost − Hosting overhead
```

- Prompt caching (Anthropic): cached input tokens は 0.1x の cost。Multi-turn conversation では cache hit 率 50–80% で cost 大幅削減。
- Batch API: 50% off で 24h 内処理保証
- Provisioned Throughput: 一定容量を月額 commit で割引

### Gross Margin Curve over Scale

スケール別 GM パターン:
- Sub-$10M ARR: GM 30–50% (compute fixed cost が重い、reserved instance のスケールメリットなし)
- $10–100M ARR: GM 50–65% (reserved capacity 効率化、prompt cache 適用)
- $100M+ ARR: GM 65–80% (custom silicon 、distillation、自社推論最適化)
- Frontier vendor (OpenAI, Anthropic): 70–80% に向け改善中

## 10.2 ベンチマーク

| Metric | Median | Good | Great |
|---|---|---|---|
| Inference GM (LLM API) | 50% | 65% | 80%+ |
| Inference GM (consumer subscription) | 30% | 50% | 70%+ |
| Compute / Revenue (early stage) | 40% | 25% | < 15% |
| Active developer / month | 1k | 100k | 1M+ |
| Tokens processed / month | 1B | 1T | 100T+ |
| Customer concentration (top 10) | 60%+ | 30% | < 20% |

## 10.3 モデリング上の注意

- **Compute capacity を独立 driver に**: GPU/TPU hours × hourly rate (cloud) または amortized capex per hour (own datacenter)。Reserved vs spot mix。
- **Training と Inference を分離**: Training は capex 性、Inference は OpEx (revenue scaling)。
- **Generation lifecycle**: モデル世代 (G3, G4, G5) ごとに training cost + lifetime revenue を NPV で評価。
- **Customer concentration**: API ビジネスでは top 10 顧客で 50–80% revenue が頻繁。Major customer 失注は壊滅的。
- **Data licensing cost**: Training data licensing (Reuters, Stack Overflow, Reddit) のミニマム + variable。
- **Safety / Eval / Red teaming cost**: 上場前は OpEx に算入されるが、規制強化で増加リスク。
- **Custom silicon roadmap**: Trainium, TPU, MI300, Maia 等の自社 / commit 比率で長期 cost trajectory が変わる。
- **Output token mix**: Reasoning models (extended thinking) は output tokens が 5–20x 多い → margin 圧迫または premium pricing 必要。
- **Subscription vs API**: Consumer subscription は heavy user の集中で marginal cost が膨らむ。Tiered limits, usage-based throttling が必要。

## 10.4 投資判断ロジック観点

1. **Training capex / Frontier R&D の disciplined allocation**: 次世代モデル投資の必要性 vs Cost-out のトレードオフ。
2. **Inference Margin curve**: スケール経済が出ているか。
3. **Customer concentration**: Top 10 < 30% が望ましい。特定大口 (例: Microsoft への OpenAI 依存、Anthropic への AWS 依存) は両刃。
4. **Token-economics moat**: Lower-cost variant (distilled / quantized model) で同等品質の提供能力。
5. **Defensibility**: 真に diff な capability (推論深度、tool use、specific verticals) があるか、コモディティ化していないか。
6. **Compute access**: GPU 確保 (HW supply) が制約条件。Reserved capacity の長期契約。
7. **Energy / 環境負荷**: Power, cooling、規制 (EU AI Act, data center moratorium)。
8. **Open-source pressure**: Open-weight モデル (Llama, Mistral, DeepSeek) が closed model 価格を圧迫。

## 10.5 開示例

- **OpenAI**: Private、定期的に内部資料が報道される (Information, NYT)。Annualized run-rate revenue, operating loss/burn を断片的に開示。
- **Anthropic**: Private、Claude API revenue、CEO 発言で scaling laws、investment plan を発信。
- **Public proxies**: NVIDIA (datacenter revenue, GPU sales) は AI infrastructure demand の代理指標。Microsoft (Azure AI services growth) も公開シグナル。
- **AI-native public (将来 IPO)**: Token volume processed, Active developers, % API vs subscription, Compute cost / Revenue を S-1 で開示する見込み。

## 10.6 落とし穴

- **Training Run を「One-time」扱い**: Frontier 競争では 6–12 ヶ月毎に新世代を training。Recurring capex として扱う必要。
- **API price を「safe」と仮定**: 価格は 12 ヶ月で 50–80% 下落の歴史 (例: GPT-3.5 → 4o → 4o-mini)。Input / Output で別軌跡。
- **Compute cost 予測の楽観**: Moore's Law 単純適用では誤算。GPU supply タイト、 Power 制約で cost reduction が頭打ちの可能性。
- **Customer LTV 仮定**: API 顧客は乗り換え容易 (AWS Bedrock, Azure OpenAI Service で multi-vendor 化)。Multi-vendor 比率を retention で考慮。
- **Subscription unit economics**: Power user の compute consumption が極端 (95th percentile が平均の 50x も)。Heavy user で margin が極小 / 赤字になりうる。
- **Open-source による floor pricing**: Llama / Mistral / DeepSeek が「good enough」品質を $0 で提供 → closed model premium pricing は high-end use case 限定。
- **AI Act / 規制 capex**: EU AI Act compliance、 model card、 audit、 safety eval が今後 OpEx を増加。
- **Capacity build-ahead**: Reserved GPU / datacenter commit が demand に先行 → 一時的な fixed cost 過剰。

---

# 業態判定フローチャート

財務モデリングを始める前に、対象企業の主要メトリクスセットを判定するためのフローチャート。

```
START
  |
  ├─[Q1] 主要収益は「自社製品の販売」か「他者間の取引仲介」か？
  |     ├─ 仲介 (commission) → [Q2 Marketplace]
  |     └─ 自社販売 → [Q3 物販 / サービス判定]
  |
  ├─[Q2 Marketplace] 取引対象は何か？
  |     ├─ 物理財 (中古、新品) → 1. Marketplace (C2C/B2C resale)
  |     ├─ サービス (ride, delivery, lodging, labor) → 1. Marketplace (gig/service)
  |     ├─ 金融商品 (loan, insurance) → 3. Fintech (Marketplace lender)
  |     └─ デジタル財 (ad inventory, virtual goods) → 6. Media + Marketplace hybrid
  |
  ├─[Q3 物販 / サービス判定] 主要収益形態は？
  |     ├─ 物理製品の販売 → [Q4 Hardware/Ecommerce/Manufacturing 判定]
  |     ├─ デジタルコンテンツ (subscription / ad) → 6. Media / Content
  |     ├─ 工数/専門役務 (B2B) → 7. B2B Services / Consulting
  |     ├─ 金融サービス (deposit, lending, payments) → 3. Fintech
  |     ├─ 不動産 (rent, sale, hospitality) → 9. Real Estate
  |     ├─ AI モデルへの API/subscription → 10. AI / Foundation Model
  |     └─ 医薬・医療機器 → 5. Bio/Pharma/MedTech
  |
  ├─[Q4 Hardware/Ecommerce/Manufacturing] 顧客と販売形態は？
  |     ├─ 個人消費者向け、自社ブランド → 2. E-commerce / D2C
  |     ├─ 個人消費者向け、ハードウェア + 継続課金あり → 4. Hardware/IoT (razor-blade)
  |     ├─ B2B (工業製品、装置、部品) → 8. Manufacturing / Industrial
  |     └─ ハードウェア単発 (consumer / B2B 混在) → 4. Hardware/IoT
  |
  └─[Special considerations] 業態 hybrid のケース:
        ├─ Hardware + Software subscription (Peloton, Tesla) → 4. Hardware を主とし、 SaaS 的 subscription metric を併用
        ├─ Marketplace + Fintech (BNPL, Square): → 1. Marketplace + 3. Fintech 両方
        ├─ Media + Commerce (Twitch, TikTok Shop): → 6. Media + 1. Marketplace
        ├─ Bio + Diagnostic platform: → 5. Bio + 4. Hardware (instrument-installed-base)
        └─ AI + SaaS (vertical AI app): → 10. AI 経済性 + SaaS metric (ARR, NRR)
```

## メトリクスセット早見表

| 業態 | 必須トップ 5 メトリクス |
|---|---|
| 1. Marketplace | GMV, Take Rate, Liquidity, Cohort GMV Retention, Concentration |
| 2. E-commerce / D2C | AOV, Repeat Rate, CM3, Return Rate, CAC Payback |
| 3. Fintech (Lending) | Origination Volume, NIM, NCO/NPL, Vintage Loss Curve, CECL Reserve |
| 3. Fintech (Neobank) | ARPAC, Cost-to-Serve, Active Rate, Cross-buy, Funding Cost |
| 3. Fintech (Payments) | TPV, Take Rate, Authorization Rate, Net Revenue per Transaction, Float |
| 4. Hardware | Hardware GM, Subscription Attach, Inventory Turns, Warranty %, CCC |
| 5. Bio / Pharma | rNPV, PoS by Phase, Peak Sales, Patent Runway, Cash Runway |
| 6. Media | DAU/MAU/Stickiness, ARPU, Content Amort/Revenue, Churn, Ad eCPM |
| 7. B2B Services | Utilization, Bill Rate, Project Margin, Pipeline Coverage, DSO |
| 8. Manufacturing | OEE, Capacity Utilization, Book-to-Bill, Backlog, Operating Leverage |
| 9. Real Estate | NOI, Cap Rate, Occupancy, RevPAR (hotel), DSCR |
| 10. AI Foundation Model | Inference GM, Compute/Revenue, Training Cost Amort, Token Volume, Customer Concentration |

## 共通の財務 sanity check

業態に関わらず、最低限以下を全モデルで確認する。

1. **Cash runway**: 現金 + Available debt − Quarterly burn × 18 ヶ月分 が確保されているか。
2. **Working capital**: Revenue 1.5x growth 想定で WC 必要額が確保できるか。
3. **Customer concentration**: Top 10 顧客で revenue の 50% 超は警告。
4. **Geographic concentration**: 単一地域 70% 超は政治・規制リスク。
5. **Supplier / Compute concentration**: 単一供給元依存 (Hardware の半導体、AI の GPU、Marketplace の決済処理) を Risk Factors に明記。
6. **Currency exposure**: 売上通貨と費用通貨の mismatch、hedging policy。
7. **Capex / FCF Bridge**: Net Income → CFO → FCF への bridge。Maintenance vs Growth capex の分離。

---

## 参考文献 / 出典 (主要)

### Marketplace
- a16z, "13 Metrics for Marketplace Companies" (Andreessen Horowitz)
- a16z, "GMV Retention: The Marketplace Metric Most Ignore"
- a16z, "The Marketplace Glossary"
- Bill Gurley, "A Rake Too Far: Optimal Platform Pricing Strategy" (Above the Crowd)
- Andrew Chen, "Required reading for marketplace startups"
- Airbnb 10-K (2024) / S-1 (2020) [SEC EDGAR]
- Uber 10-K (2024)
- DoorDash 10-K (2024) — Marketplace GOV $80.2B, 初の年次黒字 $123M
- Mercari 有報 / 決算説明会資料

### E-commerce / D2C
- Allbirds S-1 (2021) — FY2020 Net Revenue $219M, Repeat 53%, Top 25% $446 cumulative
- Warby Parker S-1 (2021) — CAC $40 (2020)、Active Customer ベース
- Theta CLV / RetentionX D2C Benchmarks 2022
- Bainbridge DTC index
- Drivepoint, "DTC Business Breakdown: Allbirds"

### Fintech
- Affirm S-1 (2020) / 10-K — GMV、RLTC、Vintage NCO curve
- Nubank 20-F / Quarterly — ARPAC $13.4 (Q3'25), Cost-to-Serve $0.80, NPL by tenor
- SoFi 10-K / 投資家プレゼン — Members, Products, Cross-buy 43% (Q1'26), FSPL
- BIS / Basel III 規制資本枠組み
- FASB ASC 326 (CECL)
- Wipfli, Withum 等 CECL methodology guides

### Hardware / IoT
- Peloton 10-K / S-1 (2019) — Connected Fitness GM, Subscription Churn
- Tesla 10-K
- Apple 10-K (CCC negative の参照ケース)
- Hackett Group "Working Capital Survey 2024" — US 大企業 median CCC 37 日
- J.P. Morgan Working Capital Index 2024

### Bio / Pharma
- BIO, "Clinical Development Success Rates 2011–2020"
- Tufts CSDD Drug Development Cost study
- Alacrita, "Valuing Pharmaceutical Assets: NPV vs rNPV"
- DiMasi et al., 各種 NPV / rNPV academic papers
- FDA, EMA, PMDA review timeline standards
- 中医協 薬価制度参考資料

### Media / Content
- Netflix 10-K (2024) — Content amortization $21B, accounting policy
- Spotify Q1 2026 報告 — MAU 761M, Premium ARPU €4.76
- Roblox 10-K (2024) / Q1 2026 — DAU 132M, Bookings, Developer Exchange Fee 24% of bookings
- IAB CPM benchmarks

### B2B Services
- Service Performance Insight (SPI) "Professional Services Maturity Benchmark 2025" — Average utilization 66.4%
- Accenture 10-K
- Booz Allen, Slalom 等 consulting firm filing

### Manufacturing
- LNS Research OEE Benchmark Data by Industry
- Lean Production OEE Standards (World-class 85%)
- SIA Book-to-Bill (historical)
- Caterpillar, Komatsu, Applied Materials 10-K

### Real Estate
- CBRE Cap Rate Survey 2025
- STR / TakeUp AI RevPAR Benchmarks 2025
- mmcginvest "U.S. Hotel Cap Rates in 2025"
- NAREIT FFO/AFFO definitions

### AI Foundation Model
- Anthropic, OpenAI 公開 pricing pages (2026 5月時点)
- SaaStr / The Information OpenAI compute margin reporting
- Martin Alderson, "Are OpenAI and Anthropic Really Losing Money on Inference?"
- Vantage / Finout LLM API pricing comparisons

---

(終)
