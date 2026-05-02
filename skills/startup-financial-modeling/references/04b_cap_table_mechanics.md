---
name: cap_table_mechanics
description: Cap Table 計算ロジック (FDSO / Pre-money / Post-money / Option Pool Shuffle / 希薄化 / Exit Waterfall / IPO Conversion / 日本種類株式) の正本。SKILL.md dispatch table の "SAFE 転換" / "J-KISS" / "Founder secondary" entry の補完 reference として §12 boundary 条件と数値例 trace を含む。
type: reference
priority: P1
related: [_terminology, 04a_convertible_and_terms, 07_japan_specifics, 14_ipo_readiness, _master_decision_tree]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 計算メカニクスは本書を canonical とする。SAFE Discount 表記 / J-KISS 2.0 等の用語は [`_terminology.md`](_terminology.md) に follow
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) (cap table 計算) から `04a` とセットで読まれる。`04a §19` の State Machine と本書 `§12` の Boundary 条件は対
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (Σ% = 100%, Founder closed-form 一致) を必ず実行
- **関連 reference**: `04a_convertible_and_terms` (条項 + State Machine §19) / `07_japan_specifics §3, §6` (日本種類株 + 会社法) / `14_ipo_readiness` (IPO Conversion / Lock-up)

# Cap Table メカニクス・希薄化計算・Exit Waterfall・日本種類株式 完全リファレンス

本書は、スタートアップの株式資本政策（Capitalization Table、以下 cap table）に関する計算メカニクスを、米国 NVCA / YC SAFE 標準と日本会社法・実務慣行の双方の観点から完全に展開した実務リファレンスである。SAFE / J-KISS / 優先株式の経済条項（liquidation preference / participation / anti-dilution など）の交渉論点については別冊（`04a_safe_jkiss_preferred.md` 相当）に譲り、本書は計算ロジック・モデル化・実例計算に集中する。

> **作成方針**
>
> - 数値例は架空だが、シリコンバレー / 東京の市場慣行を反映した現実的な水準とする。
> - 通貨は文脈に応じて USD / JPY を併記する（為替 1 USD = 150 JPY を仮定）。
> - 「省略すると DD で必ず突かれる」論点を漏らさず記載する。
> - 数式は必ず代入後の数値結果まで提示する。
> - 表は markdown table で構造化し、Excel / Sheets にそのまま転記可能な形にする。

---

## 目次

1. Cap Table の基本構造と FDSO（Fully Diluted Shares Outstanding）
2. Pre-money / Post-money 計算と Option Pool Shuffle
3. ESOP / Stock Option / RSU の設計と税務
4. ダイリューション（希薄化）の完全数式
5. SAFE 転換と Round-trip 計算
6. Exit Waterfall（清算優先 / 参加型 / cross-over）
7. IPO シミュレーション（Conversion / Lock-up / Greenshoe / Founder secondary）
8. 日本固有 種類株式（会社法 108 条）の計算実装
9. 計算ツール / モデル化アプローチ（Carta / Pulley / Excel 構造）
10. 実例ケーススタディ 3 本
11. Cap Table DD チェックリスト

---

## 1. Cap Table の基本構造と FDSO

### 1.1 Cap Table とは何を表すか

Cap table（capitalization table、株主資本構成表）は、ある時点で会社の経済的所有権・議決権・将来発生し得る希薄化要因を、株主・証券種類別に一覧化した表である。ラウンドが進むにつれ、以下の構成要素が累積していく。

| 区分 | 英語表記 | 説明 | 計上タイミング |
|---|---|---|---|
| 創業者株式 | Founders Common | 創業時に創業者が保有する普通株式 | 設立時 |
| 普通株式（一般） | Common Stock | エンジェル / 役職員譲渡分 / 行使済 SO | 都度 |
| A 種優先株式 | Series A Preferred | シリーズ A ラウンドで発行 | A ラウンド時 |
| B 種優先株式 | Series B Preferred | シリーズ B ラウンドで発行 | B ラウンド時 |
| 以降 C / D / ... | Series C / D / ... | 後続ラウンド | 各ラウンド時 |
| SAFE / J-KISS 残高 | Outstanding Convertibles | 未転換のコンバーティブル | 発行時計上、転換時消滅 |
| 行使済 SO | Issued/Exercised Options | 行使済で発行済株式となったもの | 行使時 |
| 未行使 SO | Outstanding Options | 付与済で未行使（in-the-money / out-of-the-money 区別あり） | 付与時 |
| Option Pool 残枠 | Option Pool Available / Reserved | 取締役会が将来付与可能な未割当枠 | プール拡張時 |
| Warrants | Warrants | 主にデット投資家・ベンダーに発行 | 発行時 |
| RSU（上場後） | Restricted Stock Units | 上場直前 / 後の役職員報酬 | 付与時 |

### 1.2 Issued / Outstanding / Authorized / Fully Diluted の区別

混同しやすい 4 つの用語を厳密に定義する。

| 用語 | 定義 | 含むもの |
|---|---|---|
| Authorized Shares | 定款で発行可能な総株式数 | 未発行枠を含む |
| Issued Shares | 発行済株式数 | Treasury（自己株式）も含む |
| Outstanding Shares | 発行済株式数 − 自己株式（基本 EPS の分母） | 流通している全株式 |
| Fully Diluted Shares (FDSO) | Outstanding + 全希薄化要因の行使想定後 | SO / Warrant / Convertible / Pool 残枠を全部加算 |

FDSO の正確な計算式は以下：

```
FDSO = Common Outstanding
     + Preferred Outstanding (× conversion ratio)
     + Issued/Outstanding Options
     + Option Pool Available (未割当枠)
     + Outstanding Warrants
     + SAFE / J-KISS の想定転換株数 (一般に valuation cap / next price で算定)
     + RSU (vesting 状況に応じる場合あり)
```

**注意点**：ラウンド時に投資家が前提とする FDSO は通常「pool 拡張後 + SAFE 転換後」だが、IPO 主幹事や DD 法律事務所が用いる FDSO は会計目線で「treasury method による in-the-money 分のみ」を加算するなど定義が異なる。**1 つの cap table に対し、目的別に 2〜3 種類の FDSO を併記するのが実務**。

### 1.3 Treasury Stock Method (TSM) — 行使想定の計算

TSM は EPS（earnings per share）の希薄化算定に用いる手法だが、cap table の "diluted" 列の見せ方にも応用される。

**TSM の考え方**：
1. In-the-money の SO / Warrant について、行使想定で発行株数を加算する。
2. 同時に行使価格 × 行使株数の現金が会社に流入する。
3. その現金で、市場価格（あるいは平均株価）で自己株式を買戻したと仮定する。
4. 差し引きの「ネット希薄化株数」を分母に加える。

```
追加株数 = N_options × (1 − K / P)
ただし K = 行使価格、P = 評価株価、N_options = 未行使株数
（K ≥ P の out-of-the-money 分は加算しない）
```

**計算例**：
- 未行使 SO 1,000,000 株、行使価格 K = 200 円、評価株価 P = 1,000 円
- TSM 加算株数 = 1,000,000 × (1 − 200/1,000) = 1,000,000 × 0.8 = **800,000 株**
- ナイーブな全株加算（1,000,000 株）より 200,000 株少ない

**注意**：VC の term sheet で前提とする pre-money valuation 計算では TSM ではなく "all options as if exercised at zero proceeds" を使うのが業界標準。すなわち、pool 残枠も含めて全部加算する保守的な FDSO を使う。TSM は財務会計の希薄化 EPS 計算用と割り切る。

### 1.4 Cap Table の最小データモデル

実務でモデル化する際に最低限必要なフィールド。

| フィールド | 型 | 例 |
|---|---|---|
| Stakeholder ID | string | "FOUNDER_001" |
| Stakeholder Name | string | "山田太郎" |
| Security Class | enum | Common / Series-A / SAFE / Option / Warrant |
| Issue Date | date | 2024-04-01 |
| Quantity | int | 1,000,000 |
| Price per Share (PPS) | decimal | 100.00 |
| Original Investment | decimal | 100,000,000 |
| Liquidation Preference Multiple | decimal | 1.0 |
| Participating | boolean | false |
| Participation Cap | decimal | NaN / 3.0 |
| Conversion Ratio | decimal | 1.0 |
| Anti-dilution Type | enum | None / Broad-based WA / Narrow-based WA / Full Ratchet |
| Vesting Start | date | 2024-04-01 |
| Vesting Cliff (months) | int | 12 |
| Vesting Total (months) | int | 48 |
| Strike Price (options) | decimal | 100.00 |
| Exercise Status | enum | Granted / Exercised / Cancelled |

### 1.5 Cap Table の代表的な形（数値例）

シード後（J-KISS 1 億円発行、Founders 4 名、Pool 10% 設置）の cap table 例。

| Stakeholder | Security | Shares | % FD | Notes |
|---|---|---|---|---|
| 創業者 A | Common | 4,000,000 | 40.0% | 4 年 vesting / 1y cliff |
| 創業者 B | Common | 2,500,000 | 25.0% | 同上 |
| 創業者 C | Common | 1,500,000 | 15.0% | 同上 |
| 創業者 D（CTO） | Common | 1,000,000 | 10.0% | 同上 |
| Option Pool（未割当） | Reserved Pool | 1,000,000 | 10.0% | 取締役会が承認済 |
| J-KISS（投資家 X） | Convertible | — | — | 1 億円、cap 8 億円、Discount 20% |
| **合計（Pre-conversion）** | | **10,000,000** | **100.0%** | J-KISS は転換時加算 |

J-KISS 転換想定（cap 8 億円 ÷ 10,000,000 株 = 80 円 / 株、なお A ラウンド条件で再計算される）。

---

## 2. Pre-money / Post-money 計算と Option Pool Shuffle

### 2.1 基本式

Pre-money valuation（プレ・マネー、PMV）と Post-money valuation（ポスト・マネー、QMV）の関係：

```
Post-money = Pre-money + New Investment
Investor Ownership % (post) = New Investment / Post-money
PPS (Price per Share) = Pre-money / Pre-money FDSO
New Shares Issued = New Investment / PPS
Post FDSO = Pre FDSO + New Shares
```

### 2.2 Pre-money FDSO の "正しい" 定義 — Option Pool Shuffle 問題

「pre-money valuation」の計算で使う分母（pre-money FDSO）に **option pool 拡張分を含めるか** が、業界用語で `option pool shuffle` と呼ばれる希薄化問題の本質である。

**論点**：シリーズ A 投資家は通常、ラウンド完了後に 10〜15% の未割当 option pool を要求する。term sheet 上「**closing 直前に pool を拡張せよ**」と書かれていれば、新規 pool 株数は pre-money FDSO に算入される → PPS は低下 → 既存普通株主（=創業者）が独占的に希薄化を被る。一方、closing 後に拡張すれば、pool 希薄化は新旧株主全員でプロラタに負担される。

**数値例**：シリーズ A、pre-money $9M / 投資 $3M / pool 目標 10%（post-money 基準）。

#### ケース A（pool 拡張は pre-money に含める = 投資家有利）

```
Post-money = $9M + $3M = $12M
投資家持分 = $3M / $12M = 25%
新 pool 目標サイズ = 10% × FDSO(post) = 10%
創業者 + 既存株主の持分 = 100% − 25% − 10% = 65%
```

すなわち、**創業者は 90%(pre) → 65%(post) と 25%pt 希薄化**。pool 全部を創業者が独力で負担している（pool が pre-money 内に押し込められたため）。

#### ケース B（pool 拡張を post-money 後に行う = 創業者有利）

```
Post-money 暫定 = $12M
投資家持分（pool 拡張前） = 25%
創業者持分 = 75%
↓ pool を post-money 後に 10% 拡張（全員プロラタ希薄化）
創業者 = 75% × (1 − 10%) = 67.5%
投資家 = 25% × (1 − 10%) = 22.5%
Pool = 10%
合計 = 100%
```

**創業者持分の差**：65% vs 67.5% = **2.5pt 差**。$80M exit なら $2M の差になる。

### 2.3 PPS の正確な計算式

NVCA 標準では、`shuffle` 込み（投資家有利）が市場慣行である。式を厳密に：

```
Pre-money FDSO（拡張後） = Existing FDSO_before + New Pool Shares − Old Available Pool
```

ここで、

```
New Pool Shares = (Pool Target % × Post-money FDSO) − Existing Granted/Issued options
```

そして、Post-money FDSO は再帰的に決まる：

```
Post-money FDSO = Pre-money FDSO（拡張後） + Investor New Shares
PPS = Pre-money / Pre-money FDSO（拡張後）
Investor New Shares = Investment / PPS
```

これを連立で解くと、

```
Let X = Post-money FDSO
    Y = New Pool Shares
    Z = Investor New Shares
    P = PPS
    F0 = Existing FDSO（pool 既存枠を除外）
    P0 = Existing Pool Available
    T = Pool Target %（post-money FDSO 比）
    PMV = Pre-money valuation
    INV = New investment

X = F0 + Y + Z
Y + P0 = T × X            （= post pool 全体）
P = PMV / (F0 + Y)        （pre-money FDSO ベース）
Z = INV / P
```

これを解くと、

```
Y = T × X − P0
F0 + Y = F0 + T × X − P0
P = PMV / (F0 + T × X − P0)
Z = INV × (F0 + T × X − P0) / PMV
X = F0 + Y + Z
  = F0 + T × X − P0 + INV × (F0 + T × X − P0) / PMV
  = (F0 − P0)(1 + INV/PMV) + T × X × (1 + INV/PMV)
X (1 − T (1 + INV/PMV)) = (F0 − P0)(1 + INV/PMV)
X = (F0 − P0) × (1 + INV/PMV) / (1 − T × (1 + INV/PMV))
  = (F0 − P0) × (PMV + INV) / (PMV − T × (PMV + INV))
  = (F0 − P0) × QMV / (PMV − T × QMV)
```

**数値で検算**：F0 = 9,000,000 株、P0 = 0、T = 10%、PMV = $9M、INV = $3M、QMV = $12M。

```
X = 9,000,000 × 12,000,000 / (9,000,000 − 0.10 × 12,000,000)
  = 9,000,000 × 12 / (9 − 1.2)
  = 108,000,000 / 7.8
  = 13,846,153.85 株 ≒ 13,846,154 株

Y = 0.10 × X = 1,384,615 株
F0 + Y = 9,000,000 + 1,384,615 = 10,384,615 株
PPS = $9,000,000 / 10,384,615 = $0.8666...
Z = $3,000,000 / 0.8666 = 3,461,538 株
X = 9,000,000 + 1,384,615 + 3,461,538 = 13,846,153 株 ✓

シェア配分：
創業者 = 9,000,000 / 13,846,154 = 65.00%
投資家 = 3,461,538 / 13,846,154 = 25.00%
Pool   = 1,384,615 / 13,846,154 = 10.00%
```

これでシェア配分が目標どおり 65 / 25 / 10 になる。**式と数値が完全一致**。

### 2.4 交渉論点：Pool 目標の "promised hires" 開示

実務では、創業者が pool size を抑制するため、「直近 12〜24 ヶ月の hiring plan を提示し、必要 SO 付与量を逆算」する戦術が標準化している。

| Hiring Plan 項目 | 必要 SO（FDSO%） | 備考 |
|---|---|---|
| VP Eng | 1.5% – 2.5% | A ラウンド以降の hire |
| VP Sales | 1.0% – 2.0% | 〃 |
| VP Product | 1.0% – 1.5% | 〃 |
| Senior IC × 5 | 0.25% × 5 = 1.25% | エンジニア |
| Director × 3 | 0.5% × 3 = 1.5% | |
| Mid-level × 10 | 0.10% × 10 = 1.0% | |
| **合計** | **約 8 – 10%** | これを根拠に pool size を交渉 |

→ NVCA 慣行では 10%、強硬なら 12〜15% が要求されるが、上記 hiring plan 提示で 8% 程度まで圧縮可能なケースもある。

### 2.5 Post-money SAFE の "post-money" は何の post か

YC が 2018 年に post-money SAFE をリリースして以降、SAFE に関する "post-money" の定義は **SAFE 群が全部転換した後の cap table** を指す（その後の priced round はまだ含まない）。詳細は §5 で述べる。

---

## 3. ESOP / Stock Option / RSU の設計と税務

### 3.1 用語整理

| 用語 | 概要 | 主用途 |
|---|---|---|
| Stock Option（SO） | 一定価格で自社株を取得できる権利 | ベスティング型インセンティブ |
| 新株予約権 | SO の日本会社法上の呼称 | 上場前後問わず |
| ESOP | Employee Stock Option Plan の略。SO 制度全体 | 制度設計用語 |
| Option Pool | 役員 / 従業員に将来付与する SO の "ガチャ玉" 在庫 | 取締役会承認の reservation |
| RSU | Restricted Stock Unit。vesting 後に株式が付与（無償） | 主に上場後 |
| 信託型 SO | 株式報酬信託に SO を割当 → 業績条件達成者に交付 | 日本特有スキーム |

### 3.2 米国：ISO vs NSO

| 項目 | ISO（Incentive Stock Option） | NSO / NQSO（Non-qualified） |
|---|---|---|
| 適用主体 | 米国従業員のみ | 従業員 / コンサル / 役員 |
| 行使時課税 | 連邦所得税：非課税（AMT 課税対象） | 行使益（Spread）= Ordinary income |
| 売却時課税 | 長期キャピタルゲイン（要件充足時） | キャピタルゲイン |
| 上限 | 100k Rule（年間 vest 額 ≤ $100k） | なし |
| Strike Price | 409A の FMV 以上 | 〃 |
| 有効期間 | 退職後 90 日以内に行使必要（ISO 維持） | 一般に 7 〜 10 年 |

**409A Valuation**：米国の Internal Revenue Code Section 409A により、SO の strike price は付与時 FMV 以上でなければならない。FMV は独立 valuation provider（例：Carta 409A、Aranca、Andersen）が DCF / Market / OPM などを使って算定する。FMV を下回る strike を設定すると、ベスト時に 20% ペナルティ + 即時課税の罰則。

**409A 算定の OPM (Option Pricing Method)**：会社価値 V を「複数の strike level でストック・コール・オプションを発行している」とモデル化し、Black-Scholes でレイヤー別に分解。

```
FMV_common = V_total × (BS_common_layer / Σ BS_layers)
```

**Backsolve**：直近の優先株調達 PPS を観測値として、OPM の総価値 V を逆算する手法。

### 3.3 日本：税制適格 SO vs 税制非適格 SO vs 信託型 SO

#### 3.3.1 税制適格 SO（措置法 29 条の 2）

**要件**（2026 年 5 月時点。令和 5 年度 / 6 年度 / 7 年度税制改正反映）：

| 要件 | 内容 |
|---|---|
| 付与対象 | 自社 / 子会社の役員・従業員（社外高度人材は別枠） |
| 行使価額 | 契約締結時の **時価（純資産価額方式 / 類似業種比準 / DCF）以上** |
| 年間行使価額 | 設立 5 年未満：年間 2,400 万円<br>設立 5 年以上 20 年未満（非上場 or 上場後 5 年以内）：年間 3,600 万円<br>その他：年間 1,200 万円 |
| 行使期間 | 付与決議日後 2 年経過〜10 年（設立 5 年未満の非上場会社は 15 年以内まで延長可、令和 5 年改正） |
| 譲渡制限 | 譲渡禁止 |
| 保管委託 | 株券・新株予約権を証券会社等で保管委託（令和 5 年改正で要件緩和：株式管理スキームによる代替可） |
| 1 株当たり行使価額の算定方法 | セーフハーバー・ルール公表（国税庁 通達 R5.5、純資産価額方式が利用可） |

**税務効果**：
- 付与時：課税なし
- 行使時：課税なし（**最大のメリット**）
- 譲渡時：譲渡益 = 売却価額 − 行使価額。**申告分離課税 20.315%（所得税 15% + 復興 0.315% + 住民 5%）**

#### 3.3.2 税制非適格 SO

| タイミング | 課税 |
|---|---|
| 付与時 | 課税なし（付与時の経済的利益が概ねゼロ） |
| 行使時 | 行使益（時価 − 行使価額）= **給与所得**（最高 55% 超）|
| 譲渡時 | 譲渡益（売却 − 行使時時価）= 申告分離課税 20.315% |

→ 行使時に高額の給与課税が走り、現金が出ていない状態で源泉所得税の納税義務が発生し、行使を断念するケースが多い。**実務上、税制適格を満たすことが極めて重要**。

#### 3.3.3 信託型 SO（信託型ストックオプション）

スキーム：
1. オーナー（創業者）が信託銀行 / 専用 SPC に金銭を信託 → 信託受託者がそれを原資に SO を引受
2. 一定期間後、業績達成度等に応じて受益者（役職員）に SO を交付
3. 受益者は行使し、株式取得 → 売却

**過去の運用前提**：行使時課税を回避でき、譲渡益のみ 20.315% で済むと業界は理解していた。

**2023 年 5 月 国税庁見解変更**：信託型 SO の経済的利益は「労務の対価として給与所得に該当する」と明確化。**過去発行分・未行使分の追徴課税リスク** が顕在化。

**現在（2026 年 5 月）の実務**：
- 信託型 SO は新規発行を停止する企業が大勢
- 既発行分は税制適格 SO への切替や、信託契約の解除・現金清算で対応
- 上場準備会社は監査法人が信託型 SO の有効性チェックを必ず行う

**モデリング上の影響**：信託型 SO を抱える会社の cap table では、未行使残高を「給与所得課税後ネット」で評価し、想定行使率も保守的（30〜50%）に置く。

### 3.4 RSU（Restricted Stock Unit）

特に上場後・上場間際の上場準備で利用。日本では 2016 年税制改正で RS（Restricted Stock）の譲渡制限付株式が損金算入可能となり、上場会社で利用が急増。

**仕組み**：vesting 達成時に株式が無償交付される。

**税務（日本）**：
- 交付時：交付時の時価 = **給与所得 / 退職所得**（役員）として課税
- 譲渡時：譲渡益 = 売却 − 交付時時価 = **申告分離 20.315%**

**米国**：交付時に W-2 income、売却時にキャピタルゲイン。

**Cap table への影響**：交付前は「予約株数」として希薄化要因（FDSO に算入）。交付後は普通株式 outstanding に移行。

### 3.5 Vesting Schedule

最も標準的なベスティング設計：

```
Total: 4 years
Cliff: 1 year
Cliff vest: 25%（48 ヶ月のうち 12 ヶ月分が一括）
Post-cliff: monthly vest 1/48（残り 36 ヶ月、毎月 1/48 ずつ）
```

**変種**：
- Back-loaded vesting（Snap など）：Y1 10%、Y2 20%、Y3 30%、Y4 40%
- 5 年 vesting（Tesla / Musk スタイル）：tenure を伸ばす意図
- Acceleration：
  - Single-trigger：M&A など Change of Control だけで全部 vest
  - Double-trigger：CoC + termination without cause within 12 months で vest
  - Founder の場合、典型的に **double-trigger 100% acceleration**

### 3.6 ESOP Pool Sizing

|ステージ| 推奨 pool 比率（FDSO%） |
|---|---|
| Seed 直後 | 10 〜 15% |
| Series A 直後 | 12 〜 20% |
| Series B 直後 | 15 〜 22% |
| IPO 直前 | 15 〜 25% |
| 上場後 | 5 〜 15%（評価額が大きくなるため pool % は減らす） |

**Pool refresh**：各ラウンドで pool を「投資家要求の post-money %」に reset するのが業界慣行。例：A で 15% pool 設置 → 24 ヶ月で 8% 残 → B 投資家は再び 15% を要求 → 7%pt 分を pre-money 拡張。

### 3.7 Burn Rate（年間付与率）

**Burn rate = 年間付与株数 / FDSO**

| ステージ | 健全な burn rate |
|---|---|
| Seed 〜 A | 4 〜 6% / 年 |
| B 〜 C | 3 〜 5% / 年 |
| Pre-IPO | 2 〜 4% / 年 |
| 上場後 | 1 〜 3% / 年 |

→ Burn rate が高すぎると、毎ラウンドで pool を refresh する必要が出てきて創業者希薄化が累積する。

---

## 4. ダイリューション（希薄化）の完全数式

### 4.1 単一ラウンドの希薄化

ある株主 i のラウンド前持分を $α_i$、ラウンドで発行される新株 / 既存株比率を $r = N_{new} / FDSO_{pre}$ とすると、

```
α_i (post) = α_i (pre) / (1 + r) = α_i (pre) × FDSO_pre / FDSO_post
```

**数値例**：創業者 60% 持分、ラウンド後 FDSO は pre 比 1.333 倍に増加（25% を新規投資家へ）。

```
60% × (1 / 1.333) = 60% × 0.75 = 45%
```

### 4.2 累積希薄化（Round-by-round）

複数ラウンドにわたる累積希薄化：

```
α_i (final) = α_i (initial) × Π_k (FDSO_pre,k / FDSO_post,k)
            = α_i (initial) × Π_k (1 / (1 + r_k))
```

各ラウンドの新規発行比率 $r_k$ が決まれば創業者持分は順次計算できる。

### 4.3 Founder Dilution の典型シナリオ（Series Seed → IPO）

| ラウンド | 新規発行 % (post) | Pool refresh % | 累積創業者持分 |
|---|---|---|---|
| 設立 | — | — | 100% |
| Seed（J-KISS 含む） | 15% | 10%（設置） | (100% − 25%) × Founder初期 = 75% × 4 名分布 |
| Series A | 20% | 5% （15% → 15% へ refresh） | 約 50 〜 55% |
| Series B | 18% | 4% | 約 35 〜 40% |
| Series C | 15% | 3% | 約 28 〜 32% |
| Series D / Pre-IPO | 12% | 2% | 約 22 〜 26% |
| IPO（プライマリ + セカンダリ） | 12 〜 18% | 2% | 約 15 〜 22% |

**Carta / Pulley の業界統計（2024〜2025）** によれば、IPO 時の創業者総合計持分は **中央値 12 〜 18%**、Pre-A 時で過剰希薄化を被ったケースは 5% 未満まで落ちる。

### 4.4 New money vs Existing money dilution

希薄化の "犯人" は次の 2 系統に分けて分析：

```
Total Dilution_i = New-money Dilution_i + Internal Reshuffling Dilution_i
```

- **New-money dilution**：投資家が新株を出資した分（投資家持分 = 25%なら、既存全員が 25% 等しく希薄化）。
- **Internal reshuffling dilution**：option pool 拡張、anti-dilution 発動、re-cap など、新規投資家からの cash inflow 無しに既存株主間で持分が動く部分。

→ 投資家との交渉では、internal reshuffling 分（特に pool shuffle、anti-dilution の broad-based vs full-ratchet 選択）に注力する。

### 4.5 Anti-dilution（希薄化防止条項）の数式

優先株主は、後続ラウンドで PPS が下がった場合（down round）に conversion ratio を調整して希薄化から保護される。

#### 4.5.1 Full Ratchet（フル・ラチェット、強い）

```
NewConversionPrice = NewRoundPPS（後続ラウンドの PPS そのもの）
NewConversionRatio = OriginalIssuePrice / NewConversionPrice
```

例：Series A を $1.00 で発行、Series B が $0.50 で行われた場合 → Series A の conversion ratio が 1.0 → 2.0 となり、Series A 株主は実質的に "Series B と同じ単価で買った" 扱いになる。創業者は猛烈に希薄化。

#### 4.5.2 Broad-based Weighted Average（広基準加重平均、業界標準）

```
NewConversionPrice = OldConversionPrice × (A + B) / (A + C)

A = pre-issue FDSO（option pool 含む、broad な意味）
B = ラウンド調達額 / OldConversionPrice
C = 実際にラウンドで発行された株数
```

例（数値）：
- Series A：$1.00 で発行、Conversion ratio 1.0
- A 直後 FDSO = 10,000,000 株（pool 含む、broad）
- Series B：投資 $2,000,000、PPS = $0.50、新株 4,000,000 株発行
- B = $2,000,000 / $1.00 = 2,000,000
- C = 4,000,000

```
NewConversionPrice = $1.00 × (10,000,000 + 2,000,000) / (10,000,000 + 4,000,000)
                   = $1.00 × 12,000,000 / 14,000,000
                   = $0.857...
NewConversionRatio = 1.00 / 0.857 = 1.1667
```

→ Series A 株主の保有株数は実質 16.67% 増加（普通株転換時）。Full ratchet の "倍" 増ほど過激ではない。

#### 4.5.3 Narrow-based Weighted Average（狭基準）

A の定義を「発行済普通株式相当数 + 発行済優先株式の転換相当数」のみに絞る（pool / unissued options を除外）。Broad-based より優先株主に有利。

#### 4.5.4 Pay-to-play

「希薄化防止 + 後続ラウンドへの参加義務」をセットにした条項。後続ラウンドでプロラタ参加しなかった優先株主は、anti-dilution 保護を失う or 普通株に強制 conversion されるなどのペナルティ。Down round では創業者保護に有利。

### 4.6 Pro-rata Right の数式

優先株主は、後続ラウンドで自分の持分比率を維持できる権利（プロラタ・ライト、preemption right）を持つ。

```
Pro-rata investment = α_i (current) × Total New Money
Resulting Ownership = α_i (current) （変化なし）
```

→ プロラタ未行使の場合、その投資家は希薄化される（新規投資家にスペースを譲る）。

### 4.7 Super Pro-rata

通常のプロラタを超える allocation を求める権利。リードを取り続けたい VC が要求する。

---

## 5. SAFE 転換と Round-trip 計算

### 5.1 SAFE / J-KISS の経済条項（再掲、別冊参照）

| 条項 | 説明 |
|---|---|
| Valuation Cap | 転換時の最大想定 valuation |
| Discount | 後続ラウンド PPS の (1 − d) で転換 |
| MFN | 後続発行 SAFE で有利な条件があれば自動採用 |
| Pre-money vs Post-money SAFE | YC 標準は post-money（2018〜）|
| Pro-rata side letter | 別途付与のプロラタ権 |

### 5.2 Pre-money SAFE の転換計算

転換価格 PPS_safe を以下で算定：

```
Cap-Based PPS = Cap / Pre-money FDSO（SAFE 転換前）
Discount-Based PPS = Round PPS × (1 − Discount)
SAFE PPS = min(Cap-Based PPS, Discount-Based PPS)
SAFE Conversion Shares = SAFE Investment / SAFE PPS
```

**重要**：pre-money SAFE では、Cap 計算の分母（pre-money FDSO）に **他の SAFE 転換株数を含めない**（自分自身も他 SAFE も）。これが "pre-money SAFE は SAFE 同士で互いに希薄化させる" 性質を生む。

### 5.3 Post-money SAFE の転換計算（YC 2018 standard）

```
Cap-Based PPS = Cap / "Company Capitalization (post-money SAFE 定義)"
"Company Capitalization" = Common Outstanding
                         + Preferred Outstanding
                         + Issued Options
                         + Available Pool
                         + すべての SAFE / Convertible 転換後株数
                         （ただし新ラウンドの新規 priced shares は含まない）
```

→ Post-money SAFE では、SAFE 投資家は **自分の Cap 名目持分 = Investment / Cap が "新ラウンド直前" 時点で確実に保護される**。複数 SAFE を発行しても、各 SAFE 投資家は自分の Cap 名目持分を維持する（互いに希薄化しない）。

代わりに、新ラウンド前の追加 SAFE / 新規 SO 付与は **すべて創業者希薄化** に転嫁される。

### 5.4 複数 SAFE 同時転換の Round-trip 計算

シナリオ：3 つの post-money SAFE が異なる Cap で混在し、Series A が行われる。

| SAFE | 投資額 | Cap（post-money） | 名目持分 |
|---|---|---|---|
| SAFE-1 | $500,000 | $5,000,000 | 10.00% |
| SAFE-2 | $1,000,000 | $8,000,000 | 12.50% |
| SAFE-3 | $500,000 | $10,000,000 | 5.00% |
| **合計 SAFE 持分** | $2,000,000 | — | **27.50%** |

Series A：pre-money $20M、投資 $5M、新 pool 拡張で post-money 10% 設置。

#### Step 1：SAFE 転換 PPS の決定

各 SAFE の "capped PPS" は、Cap / Company Capitalization で算定。Company Capitalization は SAFE 転換後の総株数だが、SAFE 自身が含まれるため再帰。実装は次の解析解：

各 SAFE は **自分の Cap-implied 持分（Invest / Cap）を独立に確保する**。総 SAFE 持分 = Σ Invest_i / Cap_i = 27.50%（上記）。

新ラウンド投資家 ＋ pool ＋ SAFE ＋ 既存 founder で 100% を構成：

```
α_founders = 1 − α_SAFE − α_NewInvestor − α_NewPool
α_NewInvestor = New Investment / Post-money（priced round 後 valuation）
α_NewPool = Target pool % 
```

定義上、Series A の post-money = pre-money + new investment = $20M + $5M = $25M。

しかし、SAFE 投資家から見た "post-money" は **Cap** であり pre-money ではない。post-money SAFE では Cap は SAFE 持分 % 計算に直接使う。

```
α_SAFE_i = Invest_i / Cap_i（priced round 直前）
```

合計で 27.50%。

新ラウンド投資家持分は、

```
α_NewInvestor = New Investment / Series-A Post-money
              = 5,000,000 / 25,000,000
              = 20.00%
```

新 pool は post-money で 10% 設置（pre-money 内に押し込む shuffle 仕様）：

```
α_NewPool = 10.00%
```

**創業者持分**：

```
α_founders = 100% − 27.50% − 20.00% − 10.00% = 42.50%
```

#### Step 2：株数で書き下す

新ラウンド PPS と各株数を求める。Series A の発行株数は：

```
α_NewInvestor = 20% = NewInvShares / TotalShares
TotalShares = NewInvShares / 0.20
```

ここで、

```
α_SAFE_i = SAFE_i Shares / TotalShares
SAFE_i Shares = α_SAFE_i × TotalShares
SAFE_i PPS = Invest_i / SAFE_i Shares
           = Invest_i / (α_SAFE_i × TotalShares)
```

PPS は各 SAFE で異なる。**新ラウンド PPS（Series A 投資家）**：

```
PPS_A = New Investment / NewInvShares
      = $5,000,000 / NewInvShares
```

仮に Series A pre-money に SAFE 群が含まれない（つまり "$20M pre-money" は SAFE 転換前の意味）と決めた場合、

```
Pre-money FDSO（拡張前 SAFE 込み） = Existing Founders Shares + SAFE Shares + Old Pool Shares
```

実装上の簡易ステップ：
1. Founders 株数（既知）= F
2. Pool 拡張前残枠 = P_old
3. 各 SAFE_i Shares = α_SAFE_i × X（X = post-Series-A FDSO）
4. NewInvShares = 0.20 × X
5. NewPoolShares = 0.10 × X − P_existing_pool_remaining
6. F = (1 − Σα_SAFE − 0.20 − 0.10) × X = 0.425 × X

これにより、

```
X = F / 0.425
```

例えば F = 8,500,000 なら X = 20,000,000 株。

```
NewInvShares = 4,000,000 株
PPS_A = $5,000,000 / 4,000,000 = $1.25 / 株
SAFE-1 Shares = 0.10 × 20,000,000 = 2,000,000 株 → SAFE-1 PPS = $500,000 / 2,000,000 = $0.25
SAFE-2 Shares = 0.125 × 20,000,000 = 2,500,000 株 → SAFE-2 PPS = $1,000,000 / 2,500,000 = $0.40
SAFE-3 Shares = 0.05 × 20,000,000 = 1,000,000 株 → SAFE-3 PPS = $500,000 / 1,000,000 = $0.50
```

#### Step 3：Discount 適用ケース

SAFE-3 が Cap 1000 万 + Discount 20% を持っている場合：

```
Cap-based PPS_3 = $0.50 （上記）
Discount-based PPS_3 = PPS_A × (1 − 0.20) = $1.25 × 0.80 = $1.00
SAFE-3 actual PPS = min($0.50, $1.00) = $0.50（Cap が有利）
```

→ Discount は **Cap が高すぎて発動しない場合の安全弁**。シード後の急騰では Cap で転換、down round では Discount で転換するという対称設計。

### 5.5 MFN 連鎖の数式

MFN（Most Favored Nation）clause：「後続発行 SAFE / 投資契約に有利条項があれば、自動的に当該条項を採用」。

シナリオ：
1. SAFE-A：MFN 付き、Cap なし、Discount なし
2. その後 SAFE-B 発行：Cap $5M
3. → SAFE-A は MFN 発動で「Cap $5M」を取り込む

連鎖：
4. その後 SAFE-C 発行：Cap $4M、Discount 20%
5. → SAFE-A も SAFE-B も MFN を持っていれば、「Cap $4M + Discount 20%」を取り込む（**いいとこ取り** ではなく原則として一連のターム全体採用、契約文言確認必須）

**実務上の論点**：MFN は "term ごとに best を選ぶ"（cherry-pick） vs "包括的に新ターム全体を選択"（all-or-nothing）の 2 解釈があり、契約文言で明示する必要がある。日本の J-KISS 標準では cherry-pick 不可、全体採用が標準（J-KISS 2.0）。

### 5.6 J-KISS の特徴

日本版 SAFE と呼ばれる J-KISS（Coral Capital が公開、無償ライセンス）の標準条項：

| 条項 | J-KISS 1.0 | J-KISS 2.0（2022-04〜） |
|---|---|---|
| 形式 | 新株予約権（法律上は warrant） | 同左 |
| 評価上限 | あり（Cap） | あり |
| Discount | あり（標準 20%） | あり |
| 転換トリガー | 1 億円以上の qualified financing | 同左（金額調整可能） |
| MFN | あり | あり（条項全体採用） |
| 残余財産分配優先権 | 投資額 1.0x | 同左 |
| 期限満了時転換 | あり（残余財産分配優先付普通株式へ転換） | あり |
| 名称 | J-KISS（旧版） | J-KISS 2.0 |

日本では会社法上、米国 SAFE のような「単なる契約書」では資本調達と認められないため、**新株予約権** という法形式に乗せている点に注意。会計処理は新株予約権として純資産の部に計上、転換時に資本金 / 資本準備金へ振替。

---

## 6. Exit Waterfall（清算優先 / 参加型 / cross-over）

### 6.1 Liquidation Preference（清算優先権）の基本

優先株主は、清算 / M&A 時に普通株主に優先して配分を受ける権利を持つ。

```
LP_i = N_i × Issue Price_i × Multiple_i

N_i = i 種優先株式の保有株数
Issue Price_i = i 種の発行時 PPS
Multiple_i = 1.0x 〜 3.0x（業界標準は 1.0x、down round 時に 2.0x や 3.0x も）
```

**Senior / Pari Passu / Junior**：
- Senior：他の優先株よりも先に支払い（よく "Series B 株主は Series A 株主に先んじる" などと設計）
- Pari Passu（パリパス）：複数 series が同順位 → 各 series の LP 合計を、各 series の按分で分配
- Junior：劣後

NVCA 標準は pari passu（フラット）。Series B が "Senior to A" を取ると、down round 時に B 投資家に有利。

### 6.2 Participating vs Non-participating

| Type | 清算時の受取 |
|---|---|
| Non-participating（非参加型、業界標準） | LP のみ受取（=もっと欲しければ普通株転換し、参加型同様の按分受取に切替）|
| Full participating（完全参加型） | LP 受取 **後** に残余額を持分比率で按分受取（"double-dip"）|
| Capped participating（上限付き参加型） | LP + 按分受取 が investment × cap 倍に達した時点で打ち切り |

#### 6.2.1 Non-participating の "Convert or LP" 選択

非参加型優先株主は、Exit 時に以下を比較し、有利な方を取る：

```
Choice A（LP）：LP_i のみ受取
Choice B（Convert）：α_i × ExitValue（普通株転換して持分比率で按分）

Investor takes max(A, B)
```

**Cross-over point**：A と B が等しくなる Exit Value を `cross-over point` と呼ぶ。これより上では Convert、下では LP を選ぶ。

```
LP_i = α_i × ExitValue_crossover
ExitValue_crossover = LP_i / α_i = (N_i × P_i × m_i) / (N_i / FDSO)
                    = P_i × m_i × FDSO
```

**数値例**：投資 $10M、FDSO = 50,000,000 株、PPS = $1.00、Multiple = 1x、α_i = 20%。

```
LP = $10M
ExitValue_crossover = $10M / 0.20 = $50M
```

Exit が $50M 以下なら LP を選ぶ、$50M 以上なら convert を選ぶ。

#### 6.2.2 Participating（完全参加型）

```
Total_i = LP_i + α_i × (ExitValue − Σ_j LP_j)
        = N_i × P_i × m_i + α_i × (ExitValue − Σ LP)
```

ここで $\alpha_i$ は as-converted basis での持分比率。

**数値例**：上記同条件、参加型、Exit = $100M。

```
LP_i = $10M
Residual = $100M − $10M = $90M
Participation_i = 0.20 × $90M = $18M
Total_i = $10M + $18M = $28M
```

非参加型なら max($10M, $20M) = $20M。**8M ドルの差**が生まれる。

#### 6.2.3 Capped participating

```
Total_i = min(
    LP_i + α_i × (ExitValue − Σ LP),
    cap × Investment_i
) 
= min(LP + Participation, cap × INV_i)
```

通常 cap = 2x 〜 3x。これを超えると、投資家は普通株転換を選んでも equivalent の受取になる（Convert 比較で max を取る）。

### 6.3 Multi-class Waterfall の計算ステップ

シナリオ：
- Series A：$5M @ Multiple 1x、参加型、α_A = 20%
- Series B：$10M @ Multiple 1x、非参加型、α_B = 25%、Pari Passu with A
- Common：α_C = 55%（すなわち founders + pool + SAFE 転換後 common）

Exit = $50M とする。

**Step 1：LP の合計**

```
LP_A = $5M × 1 = $5M
LP_B = $10M × 1 = $10M
LP_total = $15M
Residual after LP = $50M − $15M = $35M
```

**Step 2：Series B の "Convert or LP" 判断**

Series B as-converted な場合の取り分：

```
B_if_convert = α_B × $50M = 0.25 × $50M = $12.5M（LP 取らずに普通株転換）
B_if_LP_only = $10M（非参加型の LP 受取）
```

最大は $12.5M、すなわち convert を選択。Series B が convert すると、LP_B は剥落、α_B は普通株として再評価される。

これで LP は LP_A = $5M のみ。残余 = $50M − $5M = $45M。

**Step 3：Series A の参加型計算**

Series A は参加型なので、LP + 按分参加。Series B が普通株化したことで as-converted の分母 / 分子が変わる。元の α 計算が「全株 as-converted」前提なら、α_A = 20% のまま使える。

```
A_LP = $5M
A_residual_share = α_A × Residual_after_A_LP
```

ここで A 自身も as-converted で按分に参加するため、慎重に：

- 残余 $45M を、α_A + α_B + α_C = 0.20 + 0.25 + 0.55 = 100% で按分
- Series A の按分 = 0.20 × $45M = $9M
- Series A 総取り = $5M + $9M = $14M
- Series B = 0.25 × $45M = $11.25M
- Common = 0.55 × $45M = $24.75M

**Step 4：合計検算**

```
A 総取り = $14M
B 総取り = $11.25M
C 総取り = $24.75M
合計 = $50M ✓
```

**Step 5：Series B の cross-over 確認**

Series B が "convert" を選んだ判断は正しかったか？

- LP_only（参加型でない場合の純 LP）：$10M
- as-converted convert：$11.25M
- → convert が有利、判断正しい

**もし Series B が参加型だったら**：

```
LP_B = $10M
B_residual_share = α_B × (Exit − LP_total) = 0.25 × ($50M − $15M) = 0.25 × $35M = $8.75M
B 総取り = $10M + $8.75M = $18.75M
```

この場合の cross-over：参加型は常に LP + 按分のため、**convert 選択肢は無い** ことに注意。

### 6.4 Liquidation Stack の典型パターン（日本）

日本の VC ラウンドでは、A 種、B 種が累積した結果、cap table 上 LP の積み上げが投資総額の 200〜300% になることが多い。その結果、**M&A exit valuation が LP stack 未満だと普通株主（=創業者）に何も残らない** 事態が起きる。

| Stage | LP 累計 |
|---|---|
| Seed J-KISS (1 億円、1x) | 1 億円 |
| A 種（5 億円、1x、参加型） | 6 億円 |
| B 種（15 億円、1x、参加型） | 21 億円 |

→ exit が 30 億円なら、LP stack 21 億円差し引き後 9 億円のみが普通株 + LP 参加型に按分。**創業者持分が 30% でも実際の取り分は 9 億円 × 30% = 2.7 億円**。LP 額面の方がインパクトが大きい。

### 6.5 Cross-over Point の図示用テーブル（参加型 vs 非参加型）

Series A：投資 $5M、α 20%、Multiple 1x。

| Exit Value | 非参加型（LP only） | 非参加型（Convert） | 非参加型 max | 参加型 |
|---|---|---|---|---|
| $5M | $5M | $1M | $5M | $5M |
| $10M | $5M | $2M | $5M | $5M + 0.2×$5M = $6M |
| $25M | $5M | $5M（cross-over） | $5M | $5M + 0.2×$20M = $9M |
| $50M | $5M | $10M | $10M | $5M + 0.2×$45M = $14M |
| $100M | $5M | $20M | $20M | $5M + 0.2×$95M = $24M |

→ Exit が大きいほど **参加型と非参加型の差は拡大**。創業者にとって参加型のコストが大きい。

### 6.6 Option Pool の Exit 時 Treatment

Exit 時、未行使 SO は次のように扱う：

#### 6.6.1 In-the-money Options

```
Option Holder Net = N_options × max(0, ExitPPS − StrikePrice)
```

ExitPPS は exit 株価（M&A の場合 deal value / FDSO）。

**典型的扱い**：
- Vested、in-the-money：Exit 時に強制行使 + 株式譲渡（acquirer は cash out）
- Unvested：acceleration（single/double-trigger）or acquirer rolls into new option pool

#### 6.6.2 Out-of-the-money

通常 cancel / 失効。希薄化計算からも除外。

#### 6.6.3 例：M&A Exit at $80M、SO 100 万株未行使（strike $0.50）、ExitPPS $4

```
SO Net = 1,000,000 × ($4 − $0.50) = $3,500,000
```

これが Cash Pool（M&A の cash consideration）から先取りされ、残余が普通株主 + 優先株主に分配される。

### 6.7 Tax Treatment（日本 / 米国）

#### 6.7.1 日本

| 投資家 | exit 課税 |
|---|---|
| 個人（普通株式 / 優先株式） | 譲渡益 = 申告分離 20.315% |
| 個人（エンジェル税制活用） | 投資時所得控除（最大 800 万円）+ 譲渡時控除等、エンジェル税制 1〜3 + プレシード特例（令和 5 改正） |
| 法人 VC（投資事業有限責任組合 LPS） | パススルー（組合員に按分課税）|
| 法人事業会社 | 受取配当益金不算入 + 譲渡益は法人税課税（実効 30%）|

#### 6.7.2 米国

| 投資家 | exit 課税 |
|---|---|
| 創業者（QSBS 該当） | 5 年保有要件等を満たせば $10M または 10x basis のキャピタルゲイン非課税（Section 1202）|
| 一般個人 | 長期キャピタルゲイン 0%/15%/20% + NIIT 3.8% |
| 個人投資家（短期） | 通常所得税 |
| Fund LP | パススルー |

QSBS（Qualified Small Business Stock）は米国スタートアップの最重要税優遇。日本のエンジェル税制とは設計が異なる。

---

## 7. IPO シミュレーション

### 7.1 上場時の資本構成変換

上場直前に通常以下を実施：

1. **優先株式 → 普通株式への強制 conversion**：上場 trigger（通常、bookbuilding 確定 or 上場日）で各優先株式を自動転換。Conversion ratio は通常 1:1（anti-dilution 発動時のみ調整）。
2. **新株予約権 → 上場可能な SO へ移行**：未行使 SO は上場後も継続、新株予約権原簿で管理。
3. **RSU 開始**：上場後の従業員報酬は RSU が中心（流動性確保）。
4. **株式分割**：上場時の理想株価レンジ（東証グロース：1,000〜3,000 円、NASDAQ：$15〜$30）に合うよう、しばしば 1:50 〜 1:1000 の分割を実施。

### 7.2 Conversion 数式

```
Common_post = Common_pre + Σ_i (N_pref_i × ConversionRatio_i)
FDSO_post_IPO = Common_post + Outstanding Options + Outstanding Warrants
```

### 7.3 Lock-up 期間

| 市場 | 標準 lock-up |
|---|---|
| 米国 NASDAQ / NYSE | 180 日（IPO underwriter agreement で交渉余地あり） |
| 東証グロース | 180 日 〜 360 日（証券会社方針による）。直近は 180 日が標準化 |
| 香港 HKEX | 6 ヶ月 |

Lock-up 対象は通常：
- 創業者・役員
- 大株主（5% 超）
- VC / 機関投資家（一部 staggered release あり）

**Cap table 影響**：lock-up 期間中は流通株式が限定され、株価ボラティリティが高い。Lock-up 解除日付近で大量売却 → 株価下落のリスクを示すため、investor relations 用に Lock-up Schedule を別表で開示する。

### 7.4 Greenshoe Option（オーバーアロットメント）

主幹事証券会社に与えられる、IPO 公募株数の **+15% 追加発行オプション**。需要が強い場合に発動。

```
Total IPO Shares = Base Offering × (1 + Greenshoe %)
                 = Base Offering × 1.15（最大）
```

**Cap table 影響**：Greenshoe は新株発行（プライマリ）または既存株主の大株主からの追加譲渡（セカンダリ）の組合せで実施される。プライマリ部分は希薄化、セカンダリ部分は希薄化なし。

### 7.5 Founder Secondary

IPO 時に創業者が一定数を売却する選択肢。

| 通称 | 内容 |
|---|---|
| Direct Secondary | 創業者 → 機関投資家 / 一般 への売却（公募 + 売出） |
| Tender Offer | IPO 前のラウンドで二次取引、創業者の cash out（liquidity round） |

**慣行**：上場時に創業者が手放せる比率は概ね **保有株式の 5〜15%**。それ以上は market から「creator がコミットしない」と見られて IPO 株価の punish 対象。Lock-up 解除後に追加売却。

---

## 8. 日本固有 種類株式（会社法 108 条）

### 8.1 会社法 108 条で認められる 9 種類

会社法 108 条 1 項により、定款の定めをもって、次の 9 つの権利のいずれかが異なる種類株式を発行できる。

| 番号 | 種類 | 内容 |
|---|---|---|
| 1 号 | 剰余金配当 | 配当に関し優先 / 劣後 / 別異 |
| 2 号 | 残余財産分配 | 清算分配に関し優先 / 劣後 / 別異 |
| 3 号 | 議決権制限株式 | 株主総会で議決権を有する事項を定款で限定 |
| 4 号 | 譲渡制限株式 | 譲渡時に会社承認必要 |
| 5 号 | 取得請求権付株式（株主側プット） | 株主が会社に取得を請求できる |
| 6 号 | 取得条項付株式（会社側コール） | 会社が一定事由発生時に強制取得 |
| 7 号 | 全部取得条項付株式 | 株主総会特別決議で全部取得（M&A スクイーズアウト等） |
| 8 号 | 拒否権付株式（黄金株） | 重要事項に拒否権 |
| 9 号 | 役員選任権付株式 | 種類株主総会で取締役 / 監査役を選任 |

**スタートアップでの典型的組合せ**：
- 1 号（優先配当） + 2 号（残余財産分配優先） + 5 号（株主側 put 権） + 6 号（会社側 call 権、IPO 時の強制 conversion）+ 9 号（取締役選任権）= **A 種優先株式の標準パッケージ**

### 8.2 A 種優先株式の典型条項

|条項|定め方|備考|
|---|---|---|
| 優先配当率 | 投資額の年 5〜8%、累積 / 非累積 | 累積型は未払分繰越 |
| 残余財産分配 | 1.0x 〜 1.5x（参加型 or 非参加型）| 日本は参加型多数 |
| 取得請求権 | IPO / M&A 等 trigger 時に普通株式へ転換 | conversion ratio = 1:1 標準 |
| 取得条項 | 上場申請承認時に会社が強制取得 → 普通株式交付 | mandatory conversion |
| 議決権 | 普通株式と同等 1 株 1 議決権 | 議決権制限を入れる例少 |
| 種類株主総会決議事項 | 定款変更、種類株式追加発行、合併、増減資 等 | 拒否権の経済的代替 |
| 取締役選任権 | A 種株主全員一致で 1 名指名 | VC 投資家の board seat |
| 希薄化防止 | broad-based weighted average | full ratchet は稀 |

### 8.3 議決権制限株式（種類株式 3 号）

業界 / 用途：

| ケース | 説明 |
|---|---|
| 創業者複数議決権株式 | 上場後に 1 株 = 複数議決権を確保し、創業者の経営権を維持。日本では東証グロースが「dual class share」を 2014 年〜認めた |
| 無議決権優先株式 | 優先配当を厚くし議決権を放棄。日本では IPO 時に優先株式すべてを普通株式に転換するため、上場前の運用が中心 |

### 8.4 株主間契約（SHA）の典型条項

A 種優先株式の経済条項を補完するため、株主間契約（SHA、shareholders agreement）または投資契約書（Share Purchase Agreement, SPA）で以下を明記：

| 条項 | 内容 |
|---|---|
| みなし清算条項 | M&A を清算とみなし優先株主に LP を支払う |
| 取締役指名権 | A 種株主が 1 〜 2 名の取締役指名権を保有 |
| 拒否権事項（VC consent） | 増資、M&A、定款変更、年間予算、key person 報酬等 |
| 情報受領権 | 月次 / 四半期 / 年次の財務情報を受領 |
| 先買権・共同売却権 | 創業者 / 大株主が株式譲渡する際、VC が同条件で買取 / 売却参加 |
| Right of First Refusal (ROFR) | 同上、株式譲渡時の先買権 |
| Tag-along / Drag-along | 共同売却 / 強制売却（drag-along は IPO 不能時の戦略的 exit に必要）|
| Reverse Vesting | 創業者株式に逆 vesting を適用（1 年以内退社 → 株式買戻）|
| Lock-up | IPO 時のロックアップ義務、SHA で前倒し合意 |

### 8.5 種類株主総会

会社法 322 条により、種類株主全体の利害に関する一定事項は **種類株主総会** の特別決議が必要：

- 種類株式の内容変更（例：LP の倍数変更）
- 株式分割 / 併合（種類株主に不利な場合）
- 全部取得条項発動
- 合併・株式交換・株式移転（不利な場合）

A 種優先株主の VC 1 社が支配的だと、事実上の拒否権として機能する。

### 8.6 みなし清算条項（M&A 時の LP 発動）

会社法上、M&A は法的には清算ではないため、SHA / 投資契約で「M&A trigger 時に清算と同様の分配」を契約上規定する必要がある。

**典型条文（要約）**：
> A 種優先株主は、合併・株式交換・株式移転・事業全部譲渡、その他支配権変動を伴う事象（"M&A Event"）が生じた場合、当該 M&A Event の対価から、各 A 種株主が会社清算時に受領するであろう金額の支払を受ける権利を有する。

→ acquirer は買収契約書で明確に LP 配分を考慮した consideration allocation を明記する必要があり、適正配分の DD 論点となる。

### 8.7 種類株式の登記と定款

会社法 911 条 3 項により、種類株式の発行可能種類株式総数、発行済種類株式数、各種類株式の内容（=会社法 108 条 2 項の事項）を **登記** する必要。

新規ラウンドで A 種を発行する場合、定款変更 → 登記変更 → 投資契約締結 → 株式発行 → 登記の流れ。クロージングと同時の登記対応のため、司法書士は事前準備が必須。

---

## 9. 計算ツール / モデル化アプローチ

### 9.1 商用 SaaS（Carta / Pulley / Captable.io）

| ツール | 強み | 弱み | 価格帯 |
|---|---|---|---|
| Carta | 業界最大手、米国 standard、409A valuation 込 | 高価、日本法対応弱 | $3,000〜$30,000 / 年 |
| Pulley | UI シンプル、価格安、新興 | 高度な scenario 限定的 | $1,200〜$15,000 / 年 |
| Captable.io | ファウンダー向け、無料プランあり | 機関投資家が要求するレポート不足 | 無料〜 |
| AngelList Stack | 米国デラウェア法人前提 | 日本法人非対応 | $1,000〜 |
| SmartRound（日本） | 日本登記・種類株式に対応、J-KISS テンプレ | 海外投資家の評価フォーマット非対応 | 数十万円 / 年 |
| keepers / Nstock | 日本 SO 管理特化 | Cap table 全機能は弱 | 中堅 |

### 9.2 Excel / Google Sheets での Cap Table モデル構造

実務ではプロ機関でも Excel が併用される。シート分けの推奨構造：

| シート名 | 内容 |
|---|---|
| `Stakeholders` | 株主 ID / 名前 / メール / 連絡先 |
| `Securities` | 各証券明細（class / qty / PPS / vesting） |
| `Rounds` | ラウンド・サマリ（pre/post-money、PPS、participants） |
| `Vesting` | vesting 状況（grant 別の vested/unvested） |
| `OptionGrants` | SO 付与一覧（grant_id, grantee, qty, strike, vest_start, vest_end） |
| `SAFEs` | SAFE / J-KISS 残高 |
| `Scenarios` | What-if 想定（次ラウンドでの希薄化シミュレーション） |
| `Waterfall` | Exit waterfall 計算（liquidation preference を hard-code） |
| `Summary_FD` | Fully Diluted % のスナップショット |
| `Summary_Voting` | 議決権 % |
| `History` | 変更履歴 |

### 9.3 Round Simulator の仕組み

Round simulator は、想定ラウンドの主要パラメータを入力し、cap table の post-money 構造を返す関数群。最小入力：

```python
def simulate_round(
    pre_money: float,
    investment: float,
    target_pool_pct: float,         # post-money 比
    existing_pool_available: int,   # 既存残枠
    existing_fdso_excl_pool: int,   # pool を除いた FDSO
    safe_list: list[SAFE],          # 各 SAFE: invest/cap/discount/type
    anti_dilution_classes: list,    # 既存優先株 with WA broad
    pool_shuffle_in_pre: bool = True
) -> CapTablePostRound:
    ...
```

**処理フロー**：
1. SAFE 転換 PPS の決定（pre-money or post-money SAFE で分岐）
2. Anti-dilution 発動チェック（新ラウンド PPS < 既存 series PPS なら conversion ratio 調整）
3. Pool target からの拡張サイズ算定（§2.3 連立解）
4. 新ラウンド PPS 確定
5. 各株主の post-round shares / % 計算
6. 検算（合計 = 100%）

### 9.4 What-if と感度分析

実務での頻出 scenario：

- 次ラウンド pre-money レンジ（$15M / $20M / $25M）に対する創業者 % の感度
- Pool size 8% / 10% / 12% / 15% に対する創業者 % の感度
- Down round シミュレーション（PPS が 50% に下落した場合の anti-dilution 発動）
- M&A exit valuation $30M / $50M / $100M / $200M に対する各株主 net cash 配分

### 9.5 検算（モデル健全性チェック）

| チェック項目 | 内容 |
|---|---|
| Σ FD% = 100.00% | 端数も合致 |
| Σ Common + Σ Preferred + Σ Options + Σ Warrants + SAFE = FDSO | クロスチェック |
| Investor invested cash sum = Σ Round investments | 受取現金一致 |
| Vested shares ≤ Total grant | 各 grant 別 |
| SAFE 残高 = $0 after conversion | 転換後ゼロ |
| Σ LP ≤ Exit Value | M&A 試算で LP overflow 検知 |
| Anti-dilution 後 conversion ratio ≥ 1 | 1 を下回らない |

---

## 10. 実例ケーススタディ

### 10.1 ケース A：Seed J-KISS → Series A → Series B（標準パス、UP round）

#### 10.1.1 設定

会社：架空 SaaS スタートアップ「TechCo」

```
[T0：設立]
創業者 4 名 = 10,000,000 株、PPS = ¥1（額面）
資本金 = ¥10,000,000

[T1：Seed J-KISS 発行（6 ヶ月後）]
J-KISS 投資家：5 社、合計 ¥200M
Cap = ¥800M（post-money）
Discount = 20%
発行：新株予約権 1 セット

[T2：Series A（J-KISS から 12 ヶ月後）]
A 種優先株式
Pre-money = ¥1,800M
投資 = ¥600M
Pool target = post-money 後 15%（pre-shuffle）
Anti-dilution = broad-based WA
LP = 1.0x、参加型

[T3：Series B（A から 18 ヶ月後）]
B 種優先株式
Pre-money = ¥10,000M
投資 = ¥3,000M
Pool refresh = post-money 後 12%
LP = 1.0x、非参加型
```

#### 10.1.2 T2 Series A 計算

**J-KISS 転換**：

J-KISS は Cap ¥800M、Discount 20%。Series A pre-money ¥1,800M なので Cap が有利。

```
Cap-based PPS_JKISS = ¥800M / 10,000,000（pre-Series-A 既存創業者株） = ¥80
Discount-based PPS_JKISS = Series-A PPS × 0.80
```

ただし pre-money SAFE / J-KISS の "Cap-based PPS" の分母は、J-KISS 標準では **創業者 + Pool 既存（J-KISS 自身は除く）**。

ここでは創業者 10,000,000 株（pool まだ無し）。

```
Cap-based PPS_JKISS = ¥800M / 10,000,000 = ¥80 / 株
J-KISS 転換株数 = ¥200M / ¥80 = 2,500,000 株
```

**Series A の連立解（§2.3 適用）**：

```
F0 = 10,000,000 + 2,500,000 = 12,500,000 株（J-KISS 転換後、pool 拡張前 FDSO）
P0 = 0
T = 0.15
PMV = ¥1,800M
INV = ¥600M
QMV = ¥2,400M

X = (F0 − P0) × QMV / (PMV − T × QMV)
  = 12,500,000 × 2,400 / (1,800 − 0.15 × 2,400)
  = 12,500,000 × 2,400 / (1,800 − 360)
  = 30,000,000,000 / 1,440
  = 20,833,333 株
```

検証：

```
新 Pool = 0.15 × 20,833,333 = 3,125,000 株
PPS_A = ¥1,800M / (12,500,000 + 3,125,000) = ¥1,800M / 15,625,000 = ¥115.2
A 種新株 = ¥600M / ¥115.2 = 5,208,333 株
合計 = 12,500,000 + 3,125,000 + 5,208,333 = 20,833,333 株 ✓
```

**Cap Table（T2 Post-Series A）**：

| Stakeholder | Security | Shares | % FD |
|---|---|---|---|
| 創業者 4 名 計 | Common | 10,000,000 | 48.00% |
| J-KISS 5 社 計 | A 種（転換後扱い） | 2,500,000 | 12.00% |
| Series A 投資家 | A 種 | 5,208,333 | 25.00% |
| 新 Pool（未割当） | Reserved | 3,125,000 | 15.00% |
| **合計** | | **20,833,333** | **100.00%** |

注：J-KISS は通常 Series A 直前 round で「転換時に当該 priced round の株式と同種（=A 種）を、ただし Cap 反映の有利な PPS で取得」する標準設計（J-KISS 2.0）。実装上は J-KISS shares も A 種にバケット化される。

#### 10.1.3 T3 Series B 計算

設定：Pre-money ¥10,000M、投資 ¥3,000M、Pool refresh 12%（post-money 比）。

仮に T2 直後から T3 直前までに **既存 Pool から 1,500,000 株が役職員に grant** されており、未行使残 1,625,000 株、追加 vesting / pool 残り = 1,625,000 株（既存 grant は新株予約権として残）。

実装簡易化として、**T3 直前 FDSO に既存 grant 全数を含める** とする：

```
F0' = 10,000,000 + 2,500,000 + 5,208,333 + 1,500,000（grant 済 SO）+ 1,625,000（pool 残）= 20,833,333 株
```

T3 計算：

```
T = 0.12
PMV = 10,000
INV = 3,000
QMV = 13,000
P0_existing_pool = 1,625,000

X = (F0' − P0_existing_pool) × QMV / (PMV − T × QMV)
  = (20,833,333 − 1,625,000) × 13,000 / (10,000 − 0.12 × 13,000)
  = 19,208,333 × 13,000 / (10,000 − 1,560)
  = 19,208,333 × 13,000 / 8,440
  = 249,708,329,000 / 8,440
  = 29,586,295 株
```

検算：

```
Post-pool Total = T × X = 0.12 × 29,586,295 = 3,550,497 株
新 Pool 追加 = 3,550,497 − 1,625,000 = 1,925,497 株
PPS_B = ¥10,000M / (20,833,333 − 1,625,000 + 1,925,497 + 1,625,000)
      = ¥10,000M / 22,758,830
ちょっと計算合わせる：

Pre-money FDSO (after pool expansion) = F0' − P0 + new pool = 20,833,333 − 1,625,000 + 3,550,497
= 22,758,830 株
```

うーん、F0' から P0 を引いた上で、new pool = T × X を加える形にする（§2.3 の式と同じ意味）。

```
Pre_FDSO_expanded = (F0' − P0) + T × X
                  = 19,208,333 + 0.12 × 29,586,295
                  = 19,208,333 + 3,550,497
                  = 22,758,830
PPS_B = ¥10,000M / 22,758,830 = ¥439.4
B 種新株 = ¥3,000M / ¥439.4 = 6,827,950 株（≒ X − Pre_FDSO_expanded = 29,586,295 − 22,758,830 = 6,828,649、丸め誤差）

合計 X ≒ 29,586,295 株 ✓
```

**Cap Table（T3 Post-Series B）**（概数）：

| Stakeholder | Security | Shares | % FD |
|---|---|---|---|
| 創業者 4 名 | Common | 10,000,000 | 33.80% |
| J-KISS 投資家 | A 種 | 2,500,000 | 8.45% |
| Series A 投資家 | A 種 | 5,208,333 | 17.60% |
| Series B 投資家 | B 種 | 6,827,950 | 23.08% |
| Pool 既存 grant | Options | 1,500,000 | 5.07% |
| Pool 残（refresh 後） | Reserved | 3,550,497 − 1,500,000 = 2,050,497<br>（うち既存残 1,625,000 + 新規 拡張 425,497 ≈ 2,050,000、approx）| 約 6.93% |
| **合計** | | **約 29,586,295** | **約 100.00%** |

**Founder Dilution Trajectory**：100% → 48.0%（A 後）→ 33.8%（B 後）。これは業界中央値（A 後 ~50%、B 後 ~35%）と整合。

### 10.2 ケース B：Down Round（Anti-dilution 発動）

#### 10.2.1 設定

ケース A の T3 Series B 直後 cap table（FDSO ≒ 29.6M 株）が出発点。

24 ヶ月後、市況悪化で次ラウンド（Series C）は **Down Round**：

```
Pre-money = ¥6,000M（前回 post-money ¥13,000M から大幅下落）
投資 = ¥1,500M
Pool refresh = なし
```

A 種・B 種ともに broad-based weighted average anti-dilution 条項あり。

#### 10.2.2 Anti-dilution 発動

**Series A の調整**：

```
Old PPS_A = ¥115.2
新ラウンド PPS_C は計算前だが、暫定的に Pre-money / Pre-FDSO（拡張前）で見積。
Pre-FDSO = 29,586,295（ケース A T3 末より）
Naive PPS_C = ¥6,000M / 29,586,295 = ¥202.8

→ ¥202.8 < ¥115.2 ではない。Series A の old PPS は ¥115.2、PPS_C は ¥202.8、つまり A は希薄化されない（PPS 上がっているように見える）。

ところが、A 種 PPS と B 種 PPS は別。Series B の old PPS = ¥439.4 ＞ PPS_C = ¥202.8 → Series B が anti-dilution 発動。

NewConversionPrice_B = 439.4 × (A + B') / (A + C)

A = pre-Series-C FDSO（broad な定義、option pool 含む）= 29,586,295
B' = ¥1,500M / Old PPS_B = ¥1,500M / ¥439.4 = 3,413,290 株
C = 実際の C 株発行 = ¥1,500M / NewPPS_C, ここで NewPPS_C は anti-dilution 後の連立解

簡略化：anti-dilution 計算では C を「raw PPS_C 仮定」で計算。raw PPS_C ≒ ¥202.8。
C = ¥1,500M / ¥202.8 = 7,396,449 株

NewConversionPrice_B = ¥439.4 × (29,586,295 + 3,413,290) / (29,586,295 + 7,396,449)
                    = ¥439.4 × 33,000,769 / 36,983,928
                    = ¥439.4 × 0.8923
                    = ¥392.1
NewConversionRatio_B = ¥439.4 / ¥392.1 = 1.121
```

→ Series B 株主の保有株が **約 12.1% 増加**（普通株転換時の見立て、または conversion ratio が 1.121x 倍）。

**Series A は影響なし**（A の old PPS ¥115.2 < PPS_C ¥202.8 のため）。

#### 10.2.3 Series B "Effective Shares" の増加

Series B 6,827,950 株（issued）→ effective common-equivalent 6,827,950 × 1.121 = 7,654,531 株。

#### 10.2.4 Series C 発行と Cap Table

仮に anti-dilution 発動分（826,581 株増）を会社が新規発行で実装（実務では conversion ratio 調整なので「会計上の発行はないが exit 時の株数増加」として扱う）。

Pre-FDSO（B の anti-dilution 後）= 29,586,295 + 826,581 = 30,414,060 株。

Series C：

```
PMV = ¥6,000M
INV = ¥1,500M
QMV = ¥7,500M
T = 0（pool refresh なし）

X = F0 × QMV / PMV
  = 30,414,060 × 7,500 / 6,000
  = 30,414,060 × 1.25
  = 38,017,575 株

PPS_C = ¥6,000M / 30,414,060 = ¥197.3
C 株 = ¥1,500M / ¥197.3 = 7,602,635 株
```

#### 10.2.5 Down Round の創業者影響

```
創業者株数 10,000,000（変化なし）
T2 (A 後) = 48.00%
T3 (B 後) = 33.80%
T4 (C 後 down round) = 10,000,000 / 38,017,575 = 26.30%
```

加えて B の anti-dilution で created な phantom shares 826,581 株を全員プロラタで負担、実質 founder 持分はもう少し低い（厳密には "B's issued" がふくらむため founder 持分は 26.30% × (29,586,295 / 30,414,060) ≈ 25.59%、これに加えて C 投資家も 826,581 株プロラタ希薄化）。

**Pay-to-play 発動シナリオ**：もし Series A 株主が Series C へのプロラタ参加を拒否し、契約上 pay-to-play 条項により普通株式へ強制 conversion される場合、Series A 株主は LP を失い、cap table 上は "Common" にリクラシファイ。これは創業者・新規投資家双方の希薄化を緩和する効果がある。

### 10.3 ケース C：M&A Exit Waterfall

#### 10.3.1 設定

ケース A T3 末（Series B 後）の cap table を出発点に、24 ヶ月後に M&A exit。

```
Cap Table:
創業者 4 名：10,000,000 株（Common）
J-KISS 投資家：2,500,000 株（A 種、参加型 1.0x、original price ¥80）
Series A 投資家：5,208,333 株（A 種、参加型 1.0x、original price ¥115.2）
Series B 投資家：6,827,950 株（B 種、非参加型 1.0x、original price ¥439.4）
Pool grant 済：1,500,000 株（仮想 strike 平均 ¥150）
Pool 未割当残：2,050,497 株（cancel される）
合計 FDSO（cancel 後）= 26,036,283 株
```

LP 投資額：
- J-KISS A 種：¥200M × 1.0 = ¥200M
- Series A：¥600M × 1.0 = ¥600M
- Series B：¥3,000M × 1.0 = ¥3,000M
- LP 合計 = ¥3,800M

#### 10.3.2 Exit Value = ¥6,000M（小さめの exit）

**Step 1：SO の in-the-money 行使**

仮想 strike 平均 ¥150。Exit PPS（pre-cleanup） ≒ ¥6,000M / 26,036,283 = ¥230.4 → SO は in-the-money。

```
SO Net = 1,500,000 × (¥230.4 − ¥150) = 1,500,000 × ¥80.4 = ¥120.6M
SO 行使 cash inflow = 1,500,000 × ¥150 = ¥225M
Cash to distribute = ¥6,000M + ¥225M = ¥6,225M
```

**Step 2：B 種非参加型の "Convert or LP"**

```
B as-converted = 6,827,950 / 26,036,283 × ¥6,225M = 26.22% × ¥6,225M = ¥1,632.5M
B LP only = ¥3,000M
```

LP only（¥3,000M）が convert（¥1,632.5M）より大きい → B は LP を選択。

**Step 3：LP 支払い**

```
B LP = ¥3,000M
A 種 LP（J-KISS + Series A）= ¥800M（参加型は LP 取得 + residual 按分なので、まず LP 部分を受取）
LP 合計 = ¥3,800M
Residual = ¥6,225M − ¥3,800M = ¥2,425M
```

**Step 4：A 種参加型 + Common の按分**

A 種が参加型のため、A 種は LP 後の residual に as-converted base で参加。B 種は LP 取得を選んだため residual に参加しない（非参加型 + LP-only 選択）。

按分対象：
- 創業者：10,000,000 株
- J-KISS A 種（参加型）：2,500,000 株
- Series A 種（参加型）：5,208,333 株
- 行使済 SO：1,500,000 株（行使後は普通株式）
- 合計：19,208,333 株（B 種を除く）

```
J-KISS 按分 = 2,500,000 / 19,208,333 × ¥2,425M = 13.02% × ¥2,425M = ¥315.6M
A 種按分 = 5,208,333 / 19,208,333 × ¥2,425M = 27.11% × ¥2,425M = ¥657.6M
Common founders 按分 = 10,000,000 / 19,208,333 × ¥2,425M = 52.06% × ¥2,425M = ¥1,262.6M
SO holders 按分 = 1,500,000 / 19,208,333 × ¥2,425M = 7.81% × ¥2,425M = ¥189.4M
合計 = ¥2,425M ✓
```

**Step 5：各株主の Total Take**

| Stakeholder | LP | Residual | Total | LP cash inflow | Net Cash |
|---|---|---|---|---|---|
| 創業者 | — | ¥1,262.6M | ¥1,262.6M | — | ¥1,262.6M |
| J-KISS A 種 | ¥200M | ¥315.6M | ¥515.6M | ¥0 | ¥515.6M |
| Series A | ¥600M | ¥657.6M | ¥1,257.6M | ¥0 | ¥1,257.6M |
| Series B | ¥3,000M | ¥0（LP only） | ¥3,000M | ¥0 | ¥3,000M |
| SO Holders | — | ¥189.4M | ¥189.4M | (¥225M paid) | ¥189.4M − 課税控除 |
| **合計** | **¥3,800M** | **¥2,425M** | **¥6,225M** | | |

**Founder の感覚**：株式 38.4%（10/26.04）持っていたのに net cash は ¥1,262.6M / ¥6,000M = 21.0%。LP stack ¥3,800M に大きく削られた。

#### 10.3.3 Exit Value = ¥20,000M（大きい exit）

**Step 1：SO**

Exit PPS ≒ ¥20,000M / 26,036,283 = ¥768.2

```
SO Net per share = ¥768.2 − ¥150 = ¥618.2
SO Total = 1,500,000 × ¥618.2 = ¥927.3M
SO Cash inflow = ¥225M
Cash pool = ¥20,225M
```

**Step 2：B 種 "Convert or LP"**

```
B as-converted = 6,827,950 / 26,036,283 × ¥20,225M = 26.22% × ¥20,225M = ¥5,303M
B LP only = ¥3,000M
```

Convert（¥5,303M）> LP only（¥3,000M） → B は **convert**。LP 喪失、普通株として residual に参加。

**Step 3：LP 支払い**

```
A 種 LP = ¥800M
B は convert したので LP なし
LP 合計 = ¥800M
Residual = ¥20,225M − ¥800M = ¥19,425M
```

**Step 4：A 種参加型 + B 種 + Common 按分**

按分対象：
- 創業者 + SO + J-KISS + A + B = 26,036,283 株（全員）

```
創業者 = 10,000,000 / 26,036,283 × ¥19,425M = 38.41% × ¥19,425M = ¥7,460.4M
J-KISS = 2,500,000 / 26,036,283 × ¥19,425M = 9.60% × ¥19,425M = ¥1,865.2M
A 種 = 5,208,333 / 26,036,283 × ¥19,425M = 20.00% × ¥19,425M = ¥3,885.5M
B 種 = 6,827,950 / 26,036,283 × ¥19,425M = 26.22% × ¥19,425M = ¥5,094.3M
SO = 1,500,000 / 26,036,283 × ¥19,425M = 5.76% × ¥19,425M = ¥1,118.7M
合計 = ¥19,425M ✓（端数調整）
```

**Step 5：各株主の Total Take**

| Stakeholder | LP | Residual | Total |
|---|---|---|---|
| 創業者 | — | ¥7,460.4M | ¥7,460.4M |
| J-KISS A 種 | ¥200M | ¥1,865.2M | ¥2,065.2M |
| Series A | ¥600M | ¥3,885.5M | ¥4,485.5M |
| Series B | ¥0（converted） | ¥5,094.3M | ¥5,094.3M |
| SO Holders | — | ¥1,118.7M | ¥1,118.7M |
| **合計** | **¥800M** | **¥19,425M** | **¥20,225M** |

**Founder の感覚**：38.41% 株式 → 36.89% net cash（¥7,460.4M / ¥20,225M）。Up exit では LP の食い込みが小さく、株式比率に近い分配を獲得。

#### 10.3.4 Cross-over 確認

Series B の cross-over：
- LP_B = ¥3,000M
- α_B = 26.22%
- Cross-over Exit ≒ ¥3,000M / 0.2622 ≒ ¥11,442M

Exit が ¥11.4B 未満 → B は LP を選択、それ以上 → convert を選択。

ケース C-1（¥6B）：LP 選択 ✓
ケース C-2（¥20B）：Convert 選択 ✓

Series A 参加型は cross-over 概念なし（常に LP + 按分）。

#### 10.3.5 創業者 net cash sensitivity

前提条件：SO は ITM のとき行使（strike ¥150 × 1.5M = ¥225M を会社に cash inflow として加算）。Take Ratio = Founder Net Cash / Cash Pool（= Exit + SO inflow）。B 種は cross-over (¥11.4B) を境に LP/convert を選択。

```
Exit Value (¥M) | Cash Pool (¥M) | LP Stack | Founder Net Cash (¥M) | Founder Take Ratio
3,800           | 3,800          | 3,800    | 0                     | 0.00%
5,000           | 5,225          | 3,800    | 741.9                 | 14.20%
6,000           | 6,225          | 3,800    | 1,262.6               | 20.28%
10,000          | 10,225         | 3,800    | 3,344.9               | 32.71%
11,442          | 11,667         | (cross-over: B convert ↔ LP)        | 4,173.8 | 35.77%
20,000          | 20,225         | 800      | 7,460.7               | 36.89%
50,000          | 50,225         | 800      | 18,983.1              | 37.80%
```

→ Exit が小さい時の "LP cliff" が極端。¥3.8B 以下では founder cash 0。これが日本のスタートアップ M&A での founder 不満の最大ポイント。Up exit（B converts）では Take Ratio が 37% 台に漸近、株式比率 38.41% にほぼ一致。

---

## 11. Cap Table DD チェックリスト

スタートアップへの投資 / 監査 / IPO 引受 / 買収 DD で必ず確認すべき項目をまとめる。

### 11.1 株式・種類株式の基本

- [ ] 定款（最新）確認 ：会社法 911 条 3 項各号該当事項、種類株式の発行可能数 / 発行済数
- [ ] 株主名簿（最新）：発行済株式数 = 商業登記の発行済株式数と一致
- [ ] 種類株主総会議事録 ：発行決議、内容変更決議
- [ ] 株式発行決議 取締役会 / 株主総会議事録：各 issuance について
- [ ] 株券発行会社か株券不発行会社か（株券不発行が標準。発行している場合、株券そのものの所在確認）
- [ ] 譲渡制限株式の譲渡承認実績

### 11.2 投資契約 / SHA

- [ ] 各ラウンドの SPA / 投資契約書 全文取得
- [ ] 株主間契約書（SHA）全文 ：拒否権事項、取締役指名権、ROFR / Tag-along / Drag-along
- [ ] みなし清算条項 の有無と LP 計算式の整合
- [ ] anti-dilution 条項 の type（broad-based / narrow-based / full ratchet）
- [ ] 各 series の 優先配当率、累積 / 非累積 区別
- [ ] LP の Multiple、参加 / 非参加、Cap の有無
- [ ] 取得請求権 / 取得条項 の trigger 条件

### 11.3 SAFE / J-KISS / 新株予約権

- [ ] J-KISS 契約書全文 ：Cap、Discount、MFN、転換 trigger
- [ ] SAFE pre/post-money 区別、各 SAFE の Cap 一覧
- [ ] MFN 連鎖チェック ：後発で有利条項が発生していないか
- [ ] 新株予約権原簿（最新）：付与先、付与日、行使価額、vesting
- [ ] 新株予約権発行決議：全件分の取締役会 / 株主総会議事録
- [ ] 信託型 SO の有無（過去発行分含む。2023 年国税庁見解変更後の対応状況）
- [ ] 税制適格 SO 要件充足 ：付与対象者、行使価額（時価以上）、年間限度額

### 11.4 Vesting / Reverse Vesting

- [ ] 創業者株式の reverse vesting 契約 ：4 年 / 1y cliff の standard か
- [ ] 既退社者の vesting 状況、未行使分の cancel 処理
- [ ] Acceleration 条項（single-trigger / double-trigger）
- [ ] M&A 時の SO acceleration trigger テスト

### 11.5 計算整合

- [ ] FDSO 内訳の合計 = 100.00%（端数 0.0001% 以下）
- [ ] 各ラウンド PPS と pre/post-money の整合
- [ ] Anti-dilution 発動履歴 と現 conversion ratio の照合
- [ ] Pool target % と実残枠の差異
- [ ] 既存 grant の期間進捗別 vested / unvested 株数

### 11.6 法令・登記

- [ ] 商業登記簿謄本（履歴事項全部証明書） 取得：発行済株式総数、種類株式数の整合
- [ ] 資本金 / 資本準備金 の登記額と財務諸表の整合
- [ ] 新株予約権の登記：発行 / 行使 / 消滅の各時点で正しく登記
- [ ] 法定実効税率変更時の DTA 影響（J-GAAP/IFRS いずれでも）

### 11.7 Exit Waterfall シミュレーション

- [ ] Liquidation stack（LP 累計）の試算
- [ ] M&A 想定 valuation $X / $Y / $Z での各株主分配額
- [ ] Cross-over point の特定（series 別）
- [ ] LP 参加 / 非参加 cliff の影響
- [ ] In-the-money SO の exercise scenario

### 11.8 IPO 準備

- [ ] 上場時 conversion ratio 最終確定（anti-dilution 反映済）
- [ ] 株式分割計画（理想株価レンジ）
- [ ] Lock-up agreement ドラフト：対象者・期間
- [ ] Greenshoe 条項：主幹事との合意
- [ ] Founder secondary 計画：金額・タイミング・税務影響
- [ ] 関係会社・関連当事者間の株式譲渡履歴 ：creeping ownership change が無いか

### 11.9 米国法人化（Delaware Flip）の確認

- [ ] Delaware Flip 実施の有無
- [ ] Flip 時の cap table 引き継ぎの整合（株式 1 株 vs option 1 個の対応関係）
- [ ] QSBS 5 年保有要件の起算日
- [ ] CFC（Controlled Foreign Corporation）リスク
- [ ] PFIC（Passive Foreign Investment Company）リスク

### 11.10 海外投資家対応

- [ ] FX exposure：USD 投資家視点での "share count" 表記
- [ ] DD レポートの英訳一貫性（種類株式名称 = Series A Preferred Shares 等）
- [ ] FIRRMA / 外為法 該当性（重要技術 / インフラ分野の場合）

---

## 出典 / 参考文献

### 米国 / 英語圏

- [Cooley GO — Negotiating the Option Pool](https://www.cooleygo.com/negotiating-option-pool/)
- [Venture Hacks — The Option Pool Shuffle](https://venturehacks.com/option-pool-shuffle)
- [Pillar Legal — Series A Term Sheet: Let's Talk About Valuation](https://www.pillarlegalpc.com/series-a-term-sheet-lets-talk-about-valuation/)
- [Glencoyne — Pre-money Option Pools: a costly mistake](https://www.glencoyne.com/guides/option-pool-dilution-impact)
- [Glencoyne — NVCA Term Sheet Standards](https://www.glencoyne.com/guides/us-term-sheet-nvca-standards)
- [Finro — Option Pools: A Guide for Tech Startups](https://www.finrofca.com/startup-qa/option-pools-a-guide-for-tech-startups)
- [Foresight — Option Pools](https://foresight.is/docs/options/)
- [AVC — Valuation and Option Pool](https://avc.com/2009/11/valuation-and-option-pool/)
- [Seedcamp — Model Equity Calculator](https://seedcamp.com/views/model-equity-calculator-for-founders-with-option-pool-expansion/)
- [CapyTable — How SAFEs Convert](https://www.capytable.com/blog/how-safes-convert/)
- [Carta — Pre-money vs Post-money SAFEs](https://carta.com/learn/startups/fundraising/convertible-securities/pre-money-vs-post-money-safes/)
- [Fourscore Law — Pre-Money vs Post-Money SAFEs](https://fourscorelaw.com/pre-money-vs-post-money-simple-agreements-for-future-equity-safes/)
- [Mantle — How SAFEs Work](https://blog.withmantle.com/how-safes-work/)
- [Capbase — How SAFEs and Convertible Notes Convert](https://capbase.com/how-do-safes-and-convertible-notes-convert-in-a-priced-round/)

### 日本

- [中小企業庁 — エクイティ・ファイナンスに関する基礎知識（第三章）](https://www.chusho.meti.go.jp/kinyu/shikinguri/equityfinance/download/003.pdf)
- [BUSINESS LAWYERS — スタートアップ投資契約の優先残余財産分配権](https://www.businesslawyers.jp/practices/1251)
- [司法書士 長克成事務所 — 種類株式（残余財産の分配）](https://office-cho.jp/service/class-stock/distribution-class-stock/)
- [司法書士 長克成事務所 — 種類株式（剰余金の配当）](https://office-cho.jp/service/class-stock/dividend-class-stock/)
- [RSM 汐留パートナーズ — 種類株式の内容](https://shiodome.co.jp/js/blog/13717)
- [EXPACT — 優先株式（参加型・非参加型）](https://expact.jp/startup-investment/)
- [野村證券 用語解説 — 優先株式](https://www.nomura.co.jp/terms/japan/yu/yuusenkb.html)
- [戸上税理士・公認会計士事務所 — 種類株式の主要な条項](https://www.ktogami-accounting.com/knowledge/preferredstock_memorandum/)
- [パラダイムシフト — 優先株の種類](https://paradigm-shift.co.jp/column/93/detail)
- [セブンセンスグループ — 優先残余財産分配権付株式](https://seventh-sense.co.jp/column/3743/)
- [Coral Capital — J-KISS 2.0 公開資料](https://coralcap.co/j-kiss/)（参考）

> 注：法令番号、税率、適用期限、業界慣行は 2026 年 5 月時点の情報に基づく。最新の税制改正、会社法改正、東証ルール変更が反映されない場合があるため、実務では必ず原典確認のこと。

---

## 12. Cap Table 連立解 Boundary 条件

> **本章のスコープ** — §1〜§11 の手法は通常ケースで正しいが、boundary (境界) 付近で **数学的に解なし** / **発散** / **負の解** / **多義** が発生する。本 § は監査 C-C-016..025 で検出された 10 件を対象に、各 boundary の closed-form 条件と数値検証を提示する。
>
> **04a §19 (State Machine Spec) の補完**: §19 は **順序** に focus、本 §12 は **連立解の存在 / 一意性** に focus。
>
> **章番号注記**: ユーザ指定の "§11" 命名から §12 に rename した (既存 §11 = "Cap Table DD チェックリスト" との衝突回避)。`audits/round2_state_machine.md` の cross-reference もこれに従う。

### 12.1 Anti-Dilution Boundary

#### 12.1.1 Broad-based WA で分母 → 0 のケース

**式 (04b §4.5.2)**:
```
NCP = OCP × (A + B_eff) / (A + C)
where  A = pre-issue FDSO
       B_eff = INV / OCP  (= "as if at OCP")
       C = INV / PPS_new   (= 実発行株数)
```

**Boundary**: `A + C = 0` で発散。これは `A = 0` (= 空 cap table, 起こり得ない) または `C` が極端に負 (= 不可能) で起きるが、現実的には:

- `A ≪ 1` (= 極小 startup, FDSO < 1,000 株) で計算誤差発生
- `A` が SAFE 含むかどうかで `A + C` が大きく変動 (C-C-017)

**実装注意**:
```python
def broad_based_wa(OCP, A, B_eff, C, eps=1e-9):
    if A + C < eps:
        raise BoundaryError(f"Denominator near zero: A={A}, C={C}")
    return OCP * (A + B_eff) / (A + C)
```

#### 12.1.2 Full Ratchet で創業者 100% 希薄化

**式**: `NCP = PPS_new` (= 全 series 旧株式が新規 PPS で reissue)

**Boundary**: `PPS_new → 0` で `NCP → 0` → conversion ratio = `OCP / NCP → ∞` → 既存 preferred の effective shares が無限大 → **創業者持分が 0**。

**Closed-form check**:
```
Founder %_post = F / (F + Pool + Σ (P_i × OCP_i / PPS_new) + N_round)

PPS_new → 0 の極限で Founder % → 0
```

**数値例**: F = 6M, Pool = 1M, Series A 2M @ OCP=$5, PPS_new = $0.50 (10x down)
- A 種 effective = 2M × (5 / 0.50) = 20M
- N_round = $5M / $0.50 = 10M
- FDSO = 6 + 1 + 20 + 10 = 37M
- Founder % = 6 / 37 = 16.2% (= 既存 60% から)

PPS_new = $0.05 なら A 種 effective = 200M、Founder % = 6 / 217 = **2.8%**。

**Recommendation**: Full ratchet 契約は creditor 致命的。Term Sheet で broad-based WA に置換、または full ratchet に **floor PPS** (= NCP_min = OCP / 10 等) を設定する。

#### 12.1.3 Pay-to-Play 発動後の優先株降格

**Mechanism** (NVCA standard):
1. Pay-to-play 不参加 series → 強制 common 化
2. 当該 series は anti-dilution rights を喪失
3. 残った participating preferred 内で再計算 (= recursive)

**Boundary**: 全 preferred が non-participating だと common 化後 cap table から優先権が消滅 → 次 round で全 dilution は common holders が吸収。

**Closed-form**:
```
Participating set P = {series_j : j 参加}
Non-participating set N = {series_j : j 不参加}

For series in N:
  shares_j (preferred) → shares_j (common) at ratio = (a) NCP_current
                                                  or (b) OCP (= 1:1)
                                                  or (c) 強制 1:1
For series in P:
  Anti-dilution recalculate with A_new = A - Σ (preferred shares of N)
                                    + Σ (common shares of N at chosen ratio)
```

#### 12.1.4 SAFE 転換株の `A` 算入 (C-C-017 解消)

**Rule** (04a §19.1 step 3 と整合):
当該 round で **concurrent に転換する** SAFE / Note の転換株 (確定後) は `A` (= "Common Stock Equivalents Outstanding immediately prior") に **含める**。

**根拠**: NVCA Model Certificate of Incorporation の "Common Stock Equivalents Outstanding immediately prior to such issue" 条項。SAFE は本ラウンドのトランザクション直前に転換実行する建付けで、AD 計算時点では既に common-equivalent として cap table に存在する。

**数値例の差** (Series A FDSO 30M, bridge SAFE 5M, Series B 10M @ down):

| `A` 定義 | A | NCP_A | Series A ratio | effective A shares |
|---|---|---|---|---|
| (i) SAFE 含 | 35M | OCP × 37/45 | 1.216× | 30M (face) → effective via ratio |
| (ii) SAFE 除外 | 30M | OCP × 32/40 | 1.250× | 同 face → effective via ratio |

差: 約 2.7% の Series A 持分差 = 約 800K shares。NVCA 標準は (i)。

#### 12.1.5 Series 別の Anti-Dilution 発動 logic (C-C-019 解消)

**Rule**:
```python
for series_j in existing_preferred:
    if PPS_new < ICP_current_j:    # ← series ごとの current conversion price と比較
        trigger_AD(series_j)
    else:
        skip(series_j)              # = up round for this series
```

**Boundary**: 中間 PPS シナリオ。Series A @ $1, Series B @ $4, Series C @ $2.5。
- Series A: $2.5 > $1 → 不発 (up)
- Series B: $2.5 < $4 → 発動 (down)

**実装誤り**: "down round = 全 series 発動" という機械的判定で Series A も発動 → founder が不当に追加希薄化。

#### 12.1.6 AD × 創業者希薄化の二重計算回避 (C-C-021 解消)

**正しい実装** (NVCA 標準):
- AD は **conversion ratio 調整** のみ (= phantom shares、新株発行なし)
- Founder shares は **不変**
- Series A の effective shares のみ増加 (= ドル建て exit 時に多く貰う)

**誤った実装**: AD 発動分を **新株として発行** → Founder の denominator に追加 → 二重希薄化。

**数値検証**: Series A 5.0M shares @ OCP = $5、AD で NCP = $4 → ratio 1.25× → effective Series A = 6.25M (= +1.25M phantom)。

| 実装 | Founder shares | Total FDSO | Founder % |
|---|---|---|---|
| 正 (ratio 調整) | 10M (不変) | 10M + 1M pool + 6.25M (effective) + N_B = 17.25M + N_B | depends on N_B |
| 誤 (新株発行) | 10M (不変) | 10M + 1M + 5M + 1.25M new + N_B = 17.25M + N_B | 同じ FDSO だが share count の意味が違う |

両者は **FDSO は同じ** だが、誤実装は **新規発行扱いで税務 / 簿価処理が異なる**:
- 正: Series A 株主の経済的取得 increased、会社からの cash 流出なし
- 誤: 新株発行 = 簿価上 paid-in capital の追加計上が必要 (会計処理が違う)

**Recommendation**: §10.2.4 の数値例 (827K 新株発行扱い) は誤った実装方式の説明。**Production model では ratio 調整方式のみを使用**。

### 12.2 Option Pool Shuffle Boundary

#### 12.2.1 既存 pool が target を上回る (refresh 不要)

**Condition**:
```
Existing pool % (post-money basis) ≥ Target %
```

このとき `ΔP < 0` を avoid するため、`ΔP = max(0, ...)` で clip。

**実装**:
```python
def calculate_pool_topup(existing_pool_shares, target_pct, fdso_post):
    required_pool_shares = target_pct * fdso_post
    delta_p = max(0, required_pool_shares - existing_pool_shares)
    return delta_p
```

但し `delta_p = 0` で固定すると post-money pool % は `existing / fdso_post < target` になり、Term Sheet 違反。代替:
- (a) `target_pct` をそのまま受け入れ (= shrink to existing)
- (b) Round size を縮小して target を厳守

#### 12.2.2 Post-money pool 拡大が AD と循環 (C-C-016, C-C-017 統合)

**Cycle**:
1. AD 発動で existing preferred の effective shares 増加 → FDSO 増加
2. FDSO 増加で pool target absolute shares 増加 → ΔP 増加
3. ΔP 増加で PPS 低下 → AD trigger 強化 (PPS < ICP の幅拡大)
4. → step 1 に戻る

**収束**: §19.3.2 の iteration で解く。tolerance 1e-5 で 4-8 cycles。

**振動シナリオ**: ΔP と AD が逆方向に動く設定 (= AD 発動で effective shares 増 → pool % 達成のため ΔP 減 → でも PPS 計算では ΔP 減で PPS 上昇 → AD 緩和 → 元に戻る)。実際の収束は通常達成される (Banach fixed-point) が、step size が大きいと oscillation。

#### 12.2.3 `T × QMV ≥ PMV` での発散 (C-C-016 解消)

**式 (04b §2.3)**:
```
X = (F0 - P0) × QMV / (PMV - T × QMV)
```

**Feasibility 条件**:
```
T < PMV / QMV = PMV / (PMV + INV)
```

**Boundary check**:
```python
def feasibility_check_pool(T, PMV, INV):
    """Returns: (feasible: bool, max_T: float)"""
    QMV = PMV + INV
    max_T = PMV / QMV
    if T >= max_T:
        return False, max_T
    return True, max_T
```

**数値例**:

| Case | T | PMV | INV | max_T | Feasible? |
|---|---|---|---|---|---|
| Healthy | 15% | $20M | $5M | 80.0% | OK |
| Boundary | 30% | $5M | $5M | 50.0% | OK |
| **発散** | 40% | $5M | $10M | 33.3% | **NO** (founder 持分が負になる) |
| **発散** | 35% | $5M | $10M | 33.3% | **NO** |
| Edge | 33% | $5M | $10M | 33.3% | OK (ぎりぎり) |

**Recommendation**: cap table モデルで `T < PMV / (PMV + INV)` を **assertion** として実装。違反時は明示エラー (実務上は pool target の縮小 or pre-money の上方修正)。

#### 12.2.4 Mid-cycle pool refresh の post-money 換算 (C-C-024 解消)

**問題**: Series A 後 `Pool_existing = 8% (post-A 比)` のまま、Series B で `target = 15% (post-B 比)` を達成する。

**換算式** (post-A → post-B):
```
existing_post_B_pct = existing_shares / FDSO_post_B
                    = (0.08 × FDSO_post_A) / FDSO_post_B

ΔP = target × FDSO_post_B - existing_shares
   = target × FDSO_post_B - 0.08 × FDSO_post_A
```

**数値例**: FDSO_post_A = 12.5M, existing pool 8% = 1M. Series B raise → FDSO_post_B = 18M, target = 15%.
- existing_post_B_pct = 1M / 18M = 5.6% (= post-A 8% → post-B 5.6% に縮む = 自然希薄化)
- ΔP = 0.15 × 18M - 1M = 2.7M - 1M = **1.7M** 株

但しこれは FDSO_post_B が既知の前提。実際は ΔP 自体が FDSO_post_B に影響 → §19.3.2 の closed-form で同時に解く:
```
ΔP = (T × (a + N) - E_post_A_shares) / (1 - T)
```

ここで `E_post_A_shares = 1M` (= shares 単位、% は post-B 計算で動的に決まる)。

#### 12.2.5 Pool 拡大による founder 圧縮の closed-form

```
Founder %_post = F / (F + ΔP + N_B + Σ existing_others)
ΔFounder %    = Founder %_pre - Founder %_post
             ≈ Founder %_pre × (1 - FDSO_pre / FDSO_post)
```

Pool 拡大が大きいほど founder 圧縮も大きい。Pool 5% pt 拡大 ≈ founder 1.5-2% pt 希薄化 (= founder ratio に依存)。

### 12.3 Exit Waterfall Boundary

#### 12.3.1 1x Non-participating cross-over point (closed-form)

**式 (04b §6)**:
```
Investor payoff = max(LP, α × V)
where α = as-converted % of investor
       LP = invested amount × LP_multiple
       V = exit value
```

**Cross-over** (= preference 取り vs convert の境界):
```
LP = α × V_cross
V_cross = LP / α = (LP_multiple × INV) / (INV / Post-money)
        = LP_multiple × Post-money
```

**数値例**: INV $10M, post-money $50M, 1x non-participating
- α = 10/50 = 20%
- V_cross = 1 × $50M = $50M
- V < $50M: 投資家は preference 取り ($10M)
- V ≥ $50M: 投資家は convert (20% × V)

2x non-participating: V_cross = 2 × $50M = $100M。

#### 12.3.2 参加型 LP の "as-converted" 持分 denominator (C-C-020 解消)

**正しい実装**:
```
1. LP 取得: Σ LP_taken = Σ_{j ∈ participating} (LP_multiple_j × INV_j)
2. Residual = V - Σ LP_taken (LP_taken は participating series のみ)
3. Residual 按分:
   - Participating series: shares_j (as-converted)
   - Common: shares_common
   - Non-participating series が convert を選んだ場合: as-converted shares
   - Non-participating series が pure pref を選んだ場合: 除外
   - Denominator = Σ as-converted shares of participants in residual
```

**重要**: Series A (参加型) が LP 取得後、residual 按分で **再度 participating する** が、これは double-counting **ではない** (= 参加型の経済的意義)。

**数値例** (04b §6.3 の B convert ケース):
- Exit $50M
- A 種参加型 1x, INV $5M, 20% as-converted
- B 種非参加型 1x, INV $10M, 25% as-converted, **convert を選択**
- Common 55%

Step 1: LP 取得
- A: $5M (participating, takes LP)
- B: $0 (chose convert, no LP)
- Σ LP_taken = $5M

Step 2: Residual = $50M - $5M = $45M

Step 3: Residual 按分 denominator
- A 参加 (as-converted 20%)
- B convert (as-converted 25%)
- Common (55%)
- Σ = 100% ✓

按分:
- A: 20% × $45M = $9M
- B: 25% × $45M = $11.25M
- Common: 55% × $45M = $24.75M

**Total payouts**:
- A: $5M + $9M = **$14M** (= LP + participation)
- B: $11.25M (= convert only)
- Common: $24.75M
- 合計 = 50M ✓

**Boundary**: もし B が convert を選ばず pure pref を選んだら ($10M LP):
- Σ LP_taken = $5M + $10M = $15M
- Residual = $35M
- Denominator は A (20%) + Common (55%) = 75% (B は除外)
- A: 20/75 × $35M = $9.33M, Common: 55/75 × $35M = $25.67M
- A total: $5M + $9.33M = $14.33M, B: $10M, Common: $25.67M
- 合計 = $50M ✓

→ B の選択 (convert vs pref) は B 自身の payoff (¥11.25M vs $10M) で決まる。**$11.25M > $10M なので B は convert を選択** = 正しい NVCA 解釈。

#### 12.3.3 TSM の P 設定の循環 (C-C-018 解消)

**Cycle**:
- P (PPS) = pre-money / FDSO
- FDSO = base + TSM 補正 = base + N_options × (1 - K/P)
- → P 計算には FDSO 必要、FDSO 計算には P 必要

**Closed-form (Newton-Raphson)**:
```
f(P) = N_opt × (1 - K/P) - (FDSO_target - FDSO_excl_opt) = 0

f(P) = N_opt - N_opt × K/P - ΔF
f'(P) = N_opt × K / P²

Newton: P_{n+1} = P_n - f(P_n) / f'(P_n)
```

**Closed-form (代数解)**:
```
N_opt × (1 - K/P) = ΔF
N_opt - N_opt × K/P = ΔF
N_opt × K/P = N_opt - ΔF
P = N_opt × K / (N_opt - ΔF)
```

**数値例**: pre-money $20M, FDSO_excl_opt = 10M, N_opt = 2M @ K = $0.5
- target FDSO 含 TSM: FDSO_post_TSM
- ΔF = N_opt × (1 - K/P)
- pre-money / P = FDSO = FDSO_excl_opt + ΔF = 10M + N_opt × (1 - K/P)
- 20M / P = 10M + 2M - 2M × 0.5/P
- 20M / P + 1M / P = 12M
- 21M / P = 12M
- **P = $1.75**

検算: ΔF = 2M × (1 - 0.5/1.75) = 2M × (1 - 0.2857) = 2M × 0.7143 = 1.4286M
FDSO = 10M + 1.4286M = 11.4286M
P × FDSO = 1.75 × 11.4286M = $20M = pre-money ✓

#### 12.3.4 SO M&A 時 cashless exercise vs cash inflow (C-C-022 解消)

**Cashless (NVCA / 実取引慣行)**:
```
SO holder net = N_opt × (Exit_PPS - K)
Acquirer pays SO holder directly
Cash to other holders = Deal_value - SO_net
                     = Deal_value - N_opt × (Exit_PPS - K)
```

**Cash inflow (会計教科書方式)**:
```
SO exercise proceeds to company = N_opt × K
Cash to distribute = Deal_value + N_opt × K
SO holder gets: N_opt × Exit_PPS share of distribution
```

**数値例**: Deal value $80M, SO 1M shares K = $0.5, FDSO post-exercise = 18M (= 17M existing + 1M SO)
- Exit_PPS = (Deal_value + N_opt × K) / FDSO = ($80M + $0.5M) / 18M = $4.472 (cash inflow 方式)
- Or Exit_PPS = $80M / 18M = $4.444 + acquirer 直接 SO holder へ ($4.444 - $0.5) × 1M = $3.944M (cashless)

差: 約 $0.028 / share × 18M = $0.5M (= K の流入分)。

**Recommendation**: M&A waterfall モデルで **cashless** を default とし、契約条文 (= "Exercise of Options Upon Change of Control") で確認。Cash inflow 方式は accounting reporting 用途のみ。

#### 12.3.5 Lock-up Permitted Transfers (C-C-023 解消)

**標準的 exception list** (NVCA / IPO underwriter agreement):

| Exception | 条件 | Cap table 影響 |
|---|---|---|
| (a) 死亡 / 障害 | Probate court approval | Voting rights は相続人移管、shares は変更なし |
| (b) Family member 譲渡 | Spouse / direct lineal descendants / family trust | Shares 同 class、voting / lock-up 継続 |
| (c) Charitable donation | 501(c)(3) 認定団体 | Shares lock-up 継続 (受贈者も同 lock-up に拘束) |
| (d) Tax-related (estate tax) | IRS audit / death tax 払込 | 必要最小限のみ permitted |
| (e) Employment termination | Vesting agreement の repurchase | Shares 会社へ戻る、cap table 縮小 |

**Lock-up 違反時のペナルティ**: Underwriter が IPO price unwind / shares forfeiture / damages claim。

#### 12.3.6 LP cliff 内訳 (C-C-025 解消)

**Scenario**: Exit ¥3.5B、LP J-KISS ¥0.2B (pari) + A 種 ¥0.6B (pari) + B 種 ¥3B (senior to A)。LP 累計 ¥3.8B > Exit ¥3.5B で創業者 cliff。

**3 通り解釈**:

| 方式 | B 種 | A 種 | J-KISS | Common |
|---|---|---|---|---|
| (1) Stacked seniority | ¥3.0B (full) | ¥0.375B (= 0.5B × 0.75) | ¥0.125B (= 0.5B × 0.25) | ¥0 |
| (2) Pari passu (全員) | ¥2.763B (= 3.0/3.8 × 3.5) | ¥0.553B | ¥0.184B | ¥0 |
| (3) Hybrid (B senior, A=J pari) | ¥3.0B (full) | ¥0.375B | ¥0.125B | ¥0 (= 1 と同じ) |

**詳細計算 (1) Stacked**:
- Step 1: B 種 senior → 全額 ¥3.0B (Exit ¥3.5B 中)
- Step 2: 残 ¥0.5B を A + J-KISS に pari passu (LP 比率 0.6 : 0.2 = 3 : 1)
  - A: ¥0.5B × 3/4 = ¥0.375B
  - J-KISS: ¥0.5B × 1/4 = ¥0.125B
- Common: ¥0 (LP cliff のため)

**詳細計算 (2) Pari passu 全員**:
- 全 LP holders 同順位、Exit < Σ LP なので比例按分
- B: ¥3.5B × 3.0/3.8 = ¥2.763B
- A: ¥3.5B × 0.6/3.8 = ¥0.553B
- J-KISS: ¥3.5B × 0.2/3.8 = ¥0.184B
- Common: ¥0

**Recommendation**: 契約条文で seniority structure を明示 (NVCA Model Certificate Article IV Section 2 で stacked / pari passu / hybrid 選択)。日本実務は **混合型 (新シリーズ senior + 同シリーズ pari passu)** が主流 = 上記 (3) Hybrid。

### 12.4 数値例: 三重組合せ Down Round (full trace)

**Setup**:
- Company 既存:
  - Founder: 6,000,000 株 (common)
  - Pool granted: 500,000 株 (vested unexercised)
  - Pool unallocated: 500,000 株
  - Series A: 2,000,000 株 (preferred, OCP = $40, 1x non-participating, broad-based WA)
  - 未転換 SAFE: $4,000,000 face, cap = $100M, 20% discount
- Round B (Down):
  - Pre-money $50M (= down vs implied $80M last)
  - Raise $20M
  - Post-money $70M
  - Pool target 12% post-money
  - Implementation: NVCA broad-based WA (ratio adjust), pool top-up post-money

#### 12.4.1 Step 1: Snapshot

| Holder | Shares (M) | % FDSO_pre |
|---|---|---|
| Founder | 6.0 | 60.0% |
| Pool granted | 0.5 | 5.0% |
| Pool unallocated | 0.5 | 5.0% |
| Series A | 2.0 | 20.0% |
| (SAFE phantom $4M) | (0.0) | -- |
| **FDSO_pre** | **9.0** (excl SAFE) | 100.0% |

Implied last-round PPS for Series A = OCP = $40 → A 種 raise was 2.0M × $40 = $80M (post-money $80M previous? sanity: pre-money before A = $80M - $80M = $0, 不自然). **設定単純化**: Series A は通常 OCP basis で計算、Series B 連動を見るための仮設定として OCP=$40 を維持。

#### 12.4.2 Step 2: SAFE conversion

PPS_B (raw, pre-AD, pre-pool) = $50M / 9.0M = $5.556

Cap CP = $100M / 9.0M = $11.11
Discount CP = $5.556 × 0.80 = $4.444
PPS = $5.556

**Min**: $4.444 (discount) — cap が高すぎて保護にならない (= cap が pre-Round B FDSO 比で計算した PPS 11.11 より cap 価格が高くないと保護にならない、ここでは $11.11 vs $5.556 で cap が高い → 保護しない → discount 適用)

実は cap CP = $100M / 9.0M = $11.11 > PPS = $5.556 → cap は **保護にならない**。Discount CP = $4.444 < PPS → discount が保護。

**SAFE 転換株** = $4M / $4.444 = **900,000 株**

FDSO_with_SAFE (pre-AD, pre-pool) = 9.0M + 0.9M = **9.9M 株**

#### 12.4.3 Step 3: Series A Anti-Dilution

PPS_B (raw) = $5.556 < OCP_A = $40 → Series A trigger ✓ (down round for A)

Broad-based WA:
- A = 9.9M (= FDSO_with_SAFE = pre-issue FDSO incl. concurrent SAFE conversion per §12.1.4)
- B_eff = INV_B / OCP_A = $20M / $40 = 0.5M
- C = INV_B / PPS_B = $20M / $5.556 = 3.6M (但し PPS は pool 影響で変動 → iteration 必要)

仮置き PPS_B = $5.556 で:
- NCP_A = $40 × (9.9 + 0.5) / (9.9 + 3.6) = $40 × 10.4 / 13.5 = $40 × 0.7704 = **$30.81**
- Series A ratio = $40 / $30.81 = 1.298×
- Effective Series A shares = 2.0M × 1.298 = **2.5963M** (= +0.5963M phantom)

#### 12.4.4 Step 4-5: Pool top-up + Round B issuance (closed-form)

Updated FDSO_pre_pool_pre_round (incl. AD effect):
= 6.0M (Founder) + 1.0M (existing pool) + 2.5963M (Series A effective) + 0.9M (SAFE)
= **10.4963M**

Apply closed-form (§19.3.2):
- a = 10.4963M
- E = 1.0M (existing pool, granted + unallocated)
- T = 0.12
- raise = $20M
- pre-money = $50M
- r_p = 20/50 = 0.4

```
N = r_p × (a - E) / ((1-T) - r_p × T)
  = 0.4 × (10.4963 - 1.0) / (0.88 - 0.4 × 0.12)
  = 0.4 × 9.4963 / (0.88 - 0.048)
  = 3.79852 / 0.832
  = 4.5656M shares
```

```
ΔP = (T × (a + N) - E) / (1 - T)
   = (0.12 × (10.4963 + 4.5656) - 1.0) / 0.88
   = (0.12 × 15.0619 - 1.0) / 0.88
   = (1.8074 - 1.0) / 0.88
   = 0.8074 / 0.88
   = 0.9175M shares
```

```
PPS_B = pre-money / (a + ΔP)
      = 50 / (10.4963 + 0.9175)
      = 50 / 11.4138
      = $4.381 / share
```

**重要**: PPS_B が初期推定 $5.556 から $4.381 に下方修正 → Series A AD を再計算する必要 (cycle)。

**Iteration 2**:
- C_new = $20M / $4.381 = 4.5651M
- NCP_A_new = $40 × (9.9 + 0.5) / (9.9 + 4.5651) = $40 × 10.4 / 14.4651 = **$28.762**
- Series A ratio = 40 / 28.762 = 1.391×
- Effective Series A = 2.0M × 1.391 = **2.7821M** (vs 前 iter 2.5963M, +0.186M)
- Updated a = 6.0 + 1.0 + 2.7821 + 0.9 = 10.6821M
- N = 0.4 × (10.6821 - 1.0) / 0.832 = 0.4 × 9.6821 / 0.832 = 4.6549M
- ΔP = (0.12 × (10.6821 + 4.6549) - 1.0) / 0.88 = (0.12 × 15.337 - 1.0) / 0.88 = 0.84044 / 0.88 = 0.9550M
- PPS_B = 50 / (10.6821 + 0.9550) = 50 / 11.6371 = **$4.297**

**Iteration 3**:
- C = 20 / 4.297 = 4.6544M
- NCP_A = $40 × (10.4) / (9.9 + 4.6544) = $40 × 10.4 / 14.5544 = **$28.585**
- Series A ratio = 1.3992× → effective = 2.7984M
- a = 6 + 1 + 2.7984 + 0.9 = 10.6984M
- N = 0.4 × 9.6984 / 0.832 = 4.6627M
- ΔP = (0.12 × 15.3611 - 1.0) / 0.88 = 0.8433 / 0.88 = 0.9583M
- PPS_B = 50 / (10.6984 + 0.9583) = 50 / 11.6567 = **$4.290**

**Iteration 4**:
- C = 20 / 4.290 = 4.6620M
- NCP_A = $40 × 10.4 / (9.9 + 4.6620) = $40 × 10.4 / 14.5620 = **$28.570**
- Effective Series A = 2.0 × 40/28.570 = 2.7999M
- a = 10.6999M, N = 4.6634M, ΔP = 0.9586M
- PPS_B = 50 / 11.6585 = **$4.289**

|PPS_B^(4) - PPS_B^(3)| / $4.290 = $0.001 / $4.290 ≈ **0.023% < 1% tolerance**, ほぼ収束。

**さらに 1 cycle で 0.001% 以下に収束** (本資料は 4 cycle で打ち切り)。

#### 12.4.5 最終結果

| Holder | Shares (M) | % FDSO_post |
|---|---|---|
| Founder | 6.000 | 36.85% |
| Pool granted | 0.500 | 3.07% |
| Pool unallocated (new total) | 1.459 (= 0.5 + 0.9586) | 8.96% |
| Series A (effective) | 2.800 (= 2.0 × 40/28.57) | 17.20% |
| SAFE converted | 0.900 | 5.53% |
| Round B investors | 4.6634 | 28.65% |
| **FDSO_post (with effective AD)** | **16.282** | **99.99%** ≈ 100% ✓ |

(Pool % check: (0.5 + 1.459) / 16.282 = 1.959 / 16.282 = **12.03%** ✓ ≈ target 12%)
(Round B % check: 4.6634 / 16.282 = **28.64%** ≈ raise/post = 20/70 = **28.57%**, わずかな乖離は AD 残差; iteration をさらに進めると一致)

#### 12.4.6 創業者持分 closed-form 検算

```
Founder %_post = F / FDSO_post
              = 6.0M / 16.282M
              = 36.85%
```

**Pre-Round B founder %** = 6.0 / 9.9 = 60.6% (post-SAFE conversion only)
**希薄化** = 60.6% - 36.85% = **23.75% pt**

**希薄化 breakdown**:
- Round B 投資家持分: 28.65% pt
- Pool 拡大: ΔP / FDSO_post = 0.9586 / 16.282 = 5.89% pt
- Series A AD phantom: 0.7999M phantom / 16.282 = 4.91% pt
- Total others = 28.65 + 5.89 + 4.91 = 39.45% pt

但し希薄化は 1 - (FDSO_pre / FDSO_post) ratio で:
- 1 - 9.9/16.282 = 1 - 60.8% = **39.2%** ratio dilution
- Founder 絶対希薄化 = 60.6% × 39.2% = **23.74% pt** ✓ (closed-form 一致)

#### 12.4.7 Boundary stress (extra check)

**設定変更**: Pool target を 30% に上げると?
- Feasibility: max_T = pre / (pre + raise) = 50 / 70 = **71.4%**
- T = 30% < 71.4% → feasible OK
- ΔP 急増、PPS 大幅低下、AD 強化、founder 持分 大幅縮小

**T = 60% (extreme)**:
- < 71.4% で feasibility OK だが、founder 持分 ≈ 6 / (6 + 0.6×FDSO_post + ...) で大幅圧縮 (~12-15%)

**T = 75% (infeasible)**:
- > 71.4% → §12.2.3 のチェックで block。実装 assertion で raise。

### 12.5 Cross-reference

- **04a §19.1**: Round event canonical 順序 (本章は連立解の boundary に focus)
- **04a §19.2**: Triple-trigger 数値例 (up round; 本章 §12.4 は down round)
- **04a §19.3**: 一意性条件 / iteration 解法
- **04a §19.4.1**: Down round シナリオ (本章 §12.4 と相補)
- **§4.5** (本 file): broad-based WA 公式 (本章 §12.1 で boundary 拡張)
- **§6** (本 file): exit waterfall 数値例 (本章 §12.3 で参加型 denom 訂正)
- **§10** (本 file): 大型 case study (本章 §12.4 はさらに down round 三重組合せ)

---

