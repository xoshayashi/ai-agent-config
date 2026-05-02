---
name: saas_metrics
description: SaaS 業態のメトリクス正本 (ARR/MRR/NRR/GRR/LTV/CAC/Magic Number/Burn Multiple/Rule of 40)。SKILL.md dispatch table の "SaaS metric の正しい定義" entry から読まれる。canonical 値は _terminology §6 を参照。
type: reference
priority: P1
related: [_terminology, 03_business_models, 08_investment_thesis, 16_cost_structure, _stress_framework]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: SaaS metric の canonical 定義は [`_terminology.md §6`](_terminology.md) に集約。本書は計算式 / ベンチマーク / 落とし穴の詳細展開
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) §B (バリュエーション) / §C (投資判断) から SaaS の場合に第 2 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (特に Magic Number ×4 / Rule of 40 FCF margin) を必ず実行
- **関連 reference**: `_terminology §6` (canonical) / `03_business_models` (他業態との比較) / `08_investment_thesis §4` (kill criteria) / `16_cost_structure` (コスト側) / `_stress_framework §4.1` (applicability)

# 02. SaaS / Subscription メトリクス完全リファレンス

> 本ドキュメントはスタートアップ向け包括的財務モデリング Skill の reference であり、投資判断ロジックの dual verification (二重検証) を目的とする。各メトリクスについて、定義 → 計算式 → ベンチマーク (出典付) → 落とし穴 → 投資判断ロジックでの利用法、の順で構造化している。
>
> 用語注: 本書では「Operating System」「OS」表記を避け、「Operating model」「経営の仕組み」と表現する (個人ルール)。
>
> 数値はすべて出典明示。同一メトリクスで複数ソースが矛盾する場合は両方併記し、平均化はしない (レンジで提示)。

---

## 目次

1. [前提と用語整理](#1-前提と用語整理)
2. [収益メトリクス](#2-収益メトリクス)
3. [顧客メトリクス](#3-顧客メトリクス)
4. [ユニットエコノミクス](#4-ユニットエコノミクス)
5. [効率性メトリクス](#5-効率性メトリクス)
6. [コホート分析](#6-コホート分析)
7. [マルチプルとバリュエーション](#7-マルチプルとバリュエーション)
8. [業界ベンチマーク (出典別)](#8-業界ベンチマーク-出典別)
9. [典型的な落とし穴と誤用](#9-典型的な落とし穴と誤用)
10. [GAAP vs SaaS Metrics: ASC 606 / IFRS 15](#10-gaap-vs-saas-metrics-asc-606--ifrs-15)
11. [Vertical SaaS / Usage-based pricing 特殊事項](#11-vertical-saas--usage-based-pricing-特殊事項)
12. [SaaS デューデリジェンス チェックリスト](#12-saas-デューデリジェンス-チェックリスト)
13. [メトリクス改ざん検知チェックリスト](#13-メトリクス改ざん検知チェックリスト)
14. [出典一覧 (URL)](#14-出典一覧-url)

---

## 1. 前提と用語整理

### 1.1 Recurring Revenue の定義条件

「Recurring」と称してよい収益は以下を満たすものに限る:

- **契約期間中の繰り返し性**: 月次または年次で継続的に発生
- **解約可能性**: 顧客側に契約解除権があるが、維持される蓋然性が高い
- **同質性**: One-time fee (実装費、トレーニング費、PS = Professional Services) を含まない
- **契約裏付け**: 口頭ベースや「見込み」ではなく契約書/PO で確認可能

### 1.2 Committed vs Reported の差

| 区分 | 内容 | 用途 |
|------|------|------|
| Committed ARR | 契約上将来確実に発生する ARR (cancellation 権利を控除済) | 内部経営計画 |
| Reported ARR | 期末時点の MRR × 12、または ACV ベース合計 | 外部報告 |
| Implied ARR | 直近四半期 GAAP 売上 × 4 (使用量型企業向けアナリスト推定) | 上場企業の外部評価 |

Implied ARR は本来の ARR 定義から外れる近似値であり、消費型 (Snowflake 型) では実態を歪めることに注意 (出典: Ordway Labs 2024)。

### 1.3 GAAP vs Non-GAAP の差

GAAP 売上は ASC 606 (米) または IFRS 15 (国際) の 5-step model に従う認識基準。SaaS Metrics (ARR/MRR) はあくまで operating metric であり、GAAP 売上の代替ではない (Datadog 10-Q 注記)。

---

## 2. 収益メトリクス

### 2.1 ARR (Annual Recurring Revenue) / MRR (Monthly Recurring Revenue)

#### 定義

ある時点 t において、契約上継続発生する recurring revenue を年率/月率換算したもの。

#### 計算式

$$
\text{ARR}_t = \sum_{i \in \text{Active}_t} \text{ContractValue}_i \times \frac{12}{\text{ContractMonths}_i}
$$

または:

$$
\text{ARR}_t = \text{MRR}_t \times 12
$$

ただし MRR は per-customer 月次正規化値の合計:

$$
\text{MRR}_t = \sum_{i \in \text{Active}_t} \frac{\text{ContractValue}_i}{\text{ContractMonths}_i}
$$

#### ベンチマーク

| ステージ | 中央値 ARR | 出典 |
|---------|-----------|------|
| Pre-Seed / Seed | $0 - $1M | OpenView 2023 |
| Series A | $1.0M - $3.0M | Tunguz 2018-2022, OpenView 2023 |
| Series B | $5M - $10M (中央値 $5M 帯) | Tunguz / KeyBanc 2024 |
| Series C | $15M - $30M | OpenView 2023 |
| KeyBanc 2024 サンプル中央値 | $26M ARR | KeyBanc/Sapphire 2024 |

(注: Tunguz 2018 の Series A 中央値 $1.8M ARR / 250% 成長は当時値。マクロ環境で 2023-2025 は減速し、Series A 中央値 $1.0-1.5M ARR レンジに低下したと OpenView 2023 が示唆)

#### 落とし穴

- **One-time fee の混入**: 実装費 / PS / セットアップ費は ARR に含めない。混ぜると multiple が歪む
- **割引の処理**: 初年度割引を gross で計上すると次年度に「自動 expansion」が見えるが実態は単に割引剥がれ。Net (= 割引後実額) で計上すべき
- **multi-year discount の年率化**: 3 年契約 $300K (実質 1 年 $120K + 2 年 $90K + 3 年 $90K) を $100K/年と均すか、契約値で均すかで cohort が変わる
- **試用期間中の顧客**: trial / freemium ユーザーを ARR に入れない

#### 投資判断ロジックでの利用法

- ARR 絶対額 → ステージ判定 (Series A/B/C)
- ARR 成長率 (YoY, MoM 年率換算) → 多くのバリュエーションモデルの主因
- ARR/従業員数 → 効率性指標 (後述 Revenue per Employee)

---

### 2.2 ARR Waterfall (New / Expansion / Contraction / Churn / Reactivation)

#### 定義

ある期間における ARR の増減を 5 種類の動きに分解する仕組み:

$$
\text{ARR}_{\text{end}} = \text{ARR}_{\text{start}} + \text{New ARR} + \text{Expansion ARR} + \text{Reactivation ARR} - \text{Contraction ARR} - \text{Churn ARR}
$$

#### 各コンポーネント定義

| 項目 | 定義 | カウント単位 |
|------|------|-------------|
| New ARR | 新規ロゴ獲得による ARR | 新規顧客のみ |
| Expansion ARR | 既存顧客のアップセル / クロスセル / シート増 | 既存顧客 |
| Contraction ARR | 既存顧客のダウンセル / シート減 / 値引き | 既存顧客 |
| Churn ARR | 完全解約による ARR 喪失 | 既存顧客 |
| Reactivation ARR | 過去 churn 顧客の再契約による ARR | 元 churn 顧客 |

#### Net New ARR

$$
\text{Net New ARR} = \text{New} + \text{Expansion} + \text{Reactivation} - \text{Contraction} - \text{Churn}
$$

これが Magic Number / Burn Multiple の分母として登場する。

#### ベンチマーク

| 段階 | New : Expansion 比率の目安 | 出典 |
|------|--------------------------|------|
| Series A 初期 | 80 : 20 | OpenView 2023 |
| Series B-C スケール期 | 60 : 40 | OpenView 2023 |
| 成熟期 (NRR>120%) | 40 : 60 以下 | Bessemer State of the Cloud 2024 |

Expansion 比率が時間とともに上昇するのが健全 (= Land & Expand が機能している証拠)。

#### 落とし穴

- **Reactivation を New に混ぜる**: 真の新規獲得力を過大評価する
- **Contraction を Churn に混ぜる**: GRR 計算が変わるため要分離
- **Logo 単位と Revenue 単位の混同**: 1 顧客が部署単位で expansion + contraction を同時に起こすケース

#### 投資判断ロジックでの利用法

- Net New ARR の trailing 4 quarter sum → Magic Number / Burn Multiple の分子
- Expansion ARR / Total Net New ARR > 30% → Net Negative Churn の前兆
- Reactivation ARR の規模 → 過去 churn の質 (avoidable churn の割合) を示唆

---

### 2.3 Bookings vs Billings vs Revenue

#### 定義の階層

```
Bookings  ≧  Billings  ≧  Revenue
(契約値)    (請求値)     (認識値)
```

| 項目 | 定義 | タイミング |
|------|------|----------|
| Bookings | 顧客と署名した契約の総額 (TCV ベースが一般的) | 契約署名時 |
| Billings | 顧客に発行した invoice 額 | 請求発行時 |
| Revenue | ASC 606 / IFRS 15 に従い認識した金額 | サービス提供進行時 |

#### 計算式 (Billings の推定)

四半期 Billings の近似 (公開情報のみで推定する場合):

$$
\text{Billings}_q = \text{Revenue}_q + (\text{Deferred Revenue}_q - \text{Deferred Revenue}_{q-1})
$$

これは「当期に GAAP 認識した売上 + 当期に増えた前受金 = 当期に請求した額」という考え方。

#### 例: 3 年契約 $360K, 年次前払

- Q1 Bookings: $360K (契約 3 年分)
- Q1 Billings: $120K (1 年分前払請求)
- Q1 Revenue: $30K ($120K / 4 quarters)
- Q1 末 Deferred Revenue: $90K (まだ未認識の年内分)

#### 落とし穴

- **Bookings = ARR ではない**: TCV (3 年 $360K) は ARR ($120K) と別物
- **Multi-year billing upfront の歪み**: Billings が一時的に膨らむが ARR は変わらない
- **PS / one-time の混入**: Bookings に PS 込みで報告すると recurring 性が薄まる
- **Reported "Bookings" の定義差**: 企業ごとに「sales accepted bookings」「ACV bookings」「TCV bookings」と定義が異なる。投資判断時は注記参照必須

#### 投資判断ロジックでの利用法

- Billings 成長率 > Revenue 成長率 → 前受金が増加 = forward visibility 改善
- Bookings ÷ Revenue の比率 → backlog の厚み
- 多年契約比率 (TCV/ACV) → 顧客 lock-in の強度

(出典: Kellblog 2018, OPEXEngine, NetSuite)

---

### 2.4 RPO (Remaining Performance Obligation) / cRPO

#### 定義

ASC 606-10-50-13 の開示要件。契約上将来発生確実な未認識収益。

$$
\text{RPO} = \text{Deferred Revenue} + \text{Non-cancellable Backlog}
$$

| 項目 | 内容 |
|------|------|
| Deferred Revenue | すでに請求/入金済だが未認識の金額 (BS の負債) |
| Backlog | 契約済だが未請求かつ未認識の金額 (BS には載らない) |
| RPO | 上記合計 (10-K / 10-Q で開示) |
| cRPO (current RPO) | RPO のうち今後 12 ヶ月以内に認識見込みの分 |

#### ASC 606 が RPO に含めることを許す範囲

- 契約期間が定まり、解約不可 (non-cancellable) な分のみ
- Month-to-month 契約、termination for convenience 条項付契約は除外
- 使用量最低保証 (commitment) のない consumption 契約は除外
- パイプライン / 更新見込みは除外

#### ベンチマーク (公開企業)

| 企業 | cRPO 成長率 | 直近期 |
|------|-----------|--------|
| Salesforce | +10% YoY | FY25 Q3 (cRPO $26.4B) |
| Datadog | mid-teens% | FY24 |
| Snowflake | +20%超 | FY25 |

(出典: 各社 10-K / 10-Q)

#### 落とし穴

- **RPO の伸びが ARR の伸びを下回る**: 多年契約が減り、月次/年次への転換 = lock-in 弱体化のサイン
- **cRPO 比率の急変**: cRPO/RPO 比率が下がる = より長期契約偏重 (一時的に short-term visibility が薄まる)
- **Deferred Revenue 単独で見ると billing cycle 変更で歪む**: 必ず RPO と並べる

#### 投資判断ロジックでの利用法

- cRPO 成長率 → 12 ヶ月先 forward revenue の visibility
- RPO ÷ Revenue (LTM) → backlog 倍率 (高いほど予見性高)
- Salesforce $14.1B Deferred Revenue / 売上 = 3-4 ヶ月分 → 標準的な年次前払モデル

(出典: SaaS CFO, Salesforce 10-K, RightRev, FLG Partners)

---

### 2.5 Backlog

#### 定義

契約済かつ未請求かつ未認識の金額。BS には載らないが RPO 開示の構成要素。Long-term software 契約 (Oracle, SAP の社内オンプレ含む) では特に重要。

#### 計算

$$
\text{Backlog} = \text{RPO} - \text{Deferred Revenue}
$$

#### 落とし穴

- 公開企業以外は開示義務がない → DD で個別取得必要
- 「契約済」の解釈が曖昧 (LOI 含むか? PO 受領前は?)

---

## 3. 顧客メトリクス

### 3.1 Logo Retention vs Revenue Retention

#### Logo Retention (顧客数ベース)

$$
\text{Logo Retention} = \frac{\text{期末時点で存続している期初顧客数}}{\text{期初顧客数}}
$$

#### Logo Churn

$$
\text{Logo Churn Rate} = 1 - \text{Logo Retention}
$$

両者とも分母は「期初時点の顧客」のみ (期中新規は含めない)。

---

### 3.2 GRR (Gross Revenue Retention)

#### 定義

既存顧客からの収益を、Expansion を除外して計算した「下方リスクのみ」の retention。

#### 計算式

$$
\text{GRR} = \frac{\text{Starting MRR} - \text{Churn MRR} - \text{Contraction MRR}}{\text{Starting MRR}}
$$

GRR は 100% が天井。

#### ベンチマーク

| 区分 | GRR 中央値 | 出典 |
|------|----------|------|
| Best-in-class B2B SaaS | 90%+ | KeyBanc 2024 |
| Median private SaaS | 90% | KeyBanc 2024 |
| SMB SaaS | 80-85% | OpenView 2023 |
| Enterprise SaaS | 90-95% | Bessemer 2024 |

(出典: KeyBanc 2024, OpenView 2023)

#### 落とし穴

- Expansion を引いていない数字を「GRR」と称する誤用が多い
- Down-sell (シート減) を contraction でなく expansion 控除に分類する例がある → 定義要確認

---

### 3.3 NRR / NDR (Net Revenue Retention / Net Dollar Retention)

#### 定義

NRR と NDR は同義。Expansion を含めた retention (>100% も可能)。

#### 計算式

$$
\text{NRR} = \frac{\text{Starting MRR} + \text{Expansion MRR} - \text{Contraction MRR} - \text{Churn MRR}}{\text{Starting MRR}}
$$

#### ベンチマーク

| 企業 / カテゴリ | NRR | 出典 / 時期 |
|----------------|-----|-------------|
| Snowflake | 131% (FY24), 127% (FY25 Q2) | Snowflake 10-Q |
| Datadog | mid-110% | Datadog 10-Q FY24 |
| Bill.com | 131% | 公開時 |
| GitLab | 129% | 公開時 |
| KeyBanc 2024 中央値 | 101% | KeyBanc/Sapphire 2024 |
| OpenView 2023 上位四分位 (expansion stage) | 119% → 107% (低下) | OpenView 2023 |
| Bessemer Cloud Index 中央値 | 110-115% | Bessemer 2024 |
| 「Top performer」目安 | 115-125% | KeyBanc 2024 |

#### 解釈基準

| NRR | 評価 |
|-----|------|
| < 90% | Warning: churn / contraction が expansion を超過 |
| 90-100% | Flat: 既存顧客から新規収益増えていない |
| 100-110% | Healthy: net negative churn 達成 |
| 110-130% | Top quartile |
| > 130% | Elite (consumption 型に多い) |

#### 落とし穴

- **計算期間の差**: 12 ヶ月 trailing と quarterly annualized で値が異なる
- **Cohort 定義**: 「12 ヶ月前の顧客」とするか「期初時点」とするかで値が変わる
- **新規 logo を分母に混入**: 結果が常に >100% になる構造ミス
- **Logo NRR vs Dollar NRR**: 大口 1 社の expansion で全体 NRR が膨らむ → median 補正必要

#### 投資判断ロジックでの利用法

- NRR > 110% → "Net Negative Churn" 達成 → LTV モデルが分母負になり実質無限大に発散 (要修正)
- NRR と GRR の差 = 純 expansion 寄与
- NRR 上昇トレンド → 製品の defensibility (vendor lock-in)
- NRR 急落 (>10pt YoY 下げ) → セグメント mix shift か、SMB churn 急増の可能性

(出典: ChartMogul, Wall Street Prep, ChurnZero, Salesforce, KeyBanc 2024)

---

### 3.4 Logo Churn vs Revenue Churn

#### 計算式の違い

$$
\text{Logo Churn} = \frac{\text{解約顧客数}}{\text{期初顧客数}}
$$

$$
\text{Revenue Churn (gross)} = \frac{\text{解約 MRR + Contraction MRR}}{\text{Starting MRR}}
$$

#### Logo Churn と Revenue Churn が乖離する理由

- 大口顧客が長く残り、SMB の churn が高い → Logo Churn 高 / Revenue Churn 低
- 逆 (大口の 1 社解約) → Revenue Churn だけ跳ね上がる

#### 月次 → 年次変換 (重要)

**間違い (linear approx)**:
$$
\text{Annual Churn} \approx \text{Monthly Churn} \times 12 \quad \text{(誤)}
$$

**正しい (compound)**:
$$
\text{Annual Churn} = 1 - (1 - \text{Monthly Churn})^{12}
$$

#### 月次 → 年次の誤差テーブル

| 月次 Churn | 線形 ×12 (誤) | 複利正解 | 誤差 (pt) |
|-----------|--------------|----------|----------|
| 1.0% | 12.0% | 11.4% | -0.6 |
| 2.0% | 24.0% | 21.5% | -2.5 |
| 3.0% | 36.0% | 30.6% | -5.4 |
| 4.0% | 48.0% | 38.7% | -9.3 |
| 5.0% | 60.0% | 46.0% | -14.0 |

> 月次 5% を超えると線形近似は実態と 14pt 以上ずれる。Board Deck で「Annual Churn = Monthly × 12」と書いてあれば即チェック。

(出典: Wall Street Prep, Optifai, Vena Solutions)

#### 落とし穴

- **Cohort 起点の不一致**: 期初 cohort で計算するか、各月の cohort weighted で計算するか
- **「解約申し出」と「契約終了」のタイミング差**: 通知ベースで churn を早期計上する企業もある
- **Reactivation を考慮しない gross 値とネット値**

#### 投資判断ロジックでの利用法

- Annual Logo Churn < 5% → enterprise 帯として優秀
- Annual Logo Churn > 20% → SMB / freemium 帯では allowed、Enterprise では赤旗
- Monthly Logo Churn × 12 を「年率」と称する pitch deck → 数値読み替え必要

---

### 3.5 Customer Concentration

#### 計算

$$
\text{Top-N Concentration} = \frac{\sum_{i=1}^{N} \text{ARR}_i}{\text{Total ARR}}
$$

通常 N = 1, 5, 10 を見る。

#### ベンチマーク

| 集中度 | 評価 (M&A / IPO 観点) | 出典 |
|--------|---------------------|------|
| Top 1 < 5% | 質問されない | Wall Street Prep |
| Top 1 5-10% | 詳細 DD 入る | Livmo, Morgan & Westfield |
| Top 1 10-20% | 価格条項付き | 業界実務 |
| Top 1 20-30% | Yellow flag, valuation 10-20% 圧縮 | 業界実務 |
| Top 1 > 30% | 多くの PE / SBA lender が pass | 業界実務 |

| 区分 | Top 10 目安 |
|------|-----------|
| SMB / Mid-market SaaS | < 10-15% |
| Enterprise / Large ACV SaaS | < 40-50% (許容) |
| Series B+ ($10M ARR+) | Top 1 < 10%, Top 5 < 30% が望ましい |
| IPO 準備 | Top 1 < 10%, Top 5 < 20% が institutional investor 標準 |

#### 落とし穴

- **親会社単位での名寄せ漏れ**: 部署別契約を別ロゴと数えると集中度を過小評価
- **Channel partner 経由**: reseller 1 社経由で実 end customer が 100 社いる場合の評価
- **Logo 集中 vs Revenue 集中 vs ACV 集中**: 異なる切り口

#### 投資判断ロジックでの利用法

- Top 1 > 20% → 即 valuation discount モデル発動
- Top 5 が 2 年連続で同じ顔ぶれ → renewal 依存度の警告
- Logo retention は良いが Revenue 集中度高 → 1 社失墜で IPO 計画破綻

---

## 4. ユニットエコノミクス

### 4.1 CAC (Customer Acquisition Cost)

#### 種類

| 種類 | 内容 | 計算式概要 |
|------|------|-----------|
| Blended CAC | 全 S&M 費用 ÷ 全新規顧客数 | 平均値 |
| Paid CAC | 有料チャネル分のみ | 有料 S&M ÷ 有料経由新規 |
| Organic CAC | オーガニック分 | (CS / Marketing 一部) ÷ オーガニック新規 |
| Marketing-only CAC | Sales 人件費を除く | Marketing 費 ÷ 新規 |
| Fully-loaded CAC | Sales + Marketing 全人件費込 | (Sales 人件費 + Marketing 人件費 + tools + ad) ÷ 新規 |

#### 推奨計算式 (Fully-loaded)

$$
\text{CAC}_{\text{fully-loaded}} = \frac{\text{S\&M 費用 (人件費・ツール・広告) }_{t-1}}{\text{New Customers}_t}
$$

期ずらし (前期費用 → 当期成果) するのは sales cycle を反映するため。

#### ベンチマーク

| 区分 | CAC 中央値 | 出典 |
|------|----------|------|
| SMB SaaS (ACV $1-10K) | $500 - $5,000 | OpenView 2023 |
| Mid-market (ACV $10-50K) | $5,000 - $30,000 | KeyBanc 2024 |
| Enterprise (ACV $50K+) | $30,000 - $200,000+ | KeyBanc 2024 |

#### 落とし穴

- **新規ロゴ獲得コストと expansion コストを混ぜる**: CS 人件費の按分が不明瞭になる
- **PS / 実装費の controb. を CAC 控除しない**: PS で marg loss しているのに CAC で正味回収できているように見える
- **Brand / awareness 投資の扱い**: 数年遅れで効くため当期 CAC に全額入れると過大評価
- **株式報酬 (SBC) 抜き計算**: GAAP 的には費用だが SBC 抜き CAC は実態より良く見える

#### 投資判断ロジックでの利用法

- Blended CAC の急落 → channel mix が viral 寄りに変化、または measurement 変更
- Blended と Paid の乖離 → organic dependency / brand strength
- CAC YoY 推移 → channel saturation の兆候

(出典: David Skok / Kellblog, OpenView 2023, KeyBanc 2024)

---

### 4.2 LTV (Lifetime Value)

#### 3 つの計算法

##### Method A: Simple LTV (定常状態仮定)

$$
\text{LTV}_{\text{simple}} = \frac{\text{ARPA} \times \text{Gross Margin \%}}{\text{Revenue Churn Rate}}
$$

最も普及。ただし churn が 0 (NRR > 100%) で発散する欠点あり。

##### Method B: Cohort-based LTV

各 cohort の累積 (gross profit 累積) を経時で加算:

$$
\text{LTV}_{\text{cohort}} = \sum_{t=1}^{T} \text{Revenue per cohort customer}_t \times \text{Gross Margin \%}_t
$$

T は実観測期間 (3-5 年が現実的)。発散しない。

##### Method C: DCF-based LTV (NRR > 100% にも対応)

$$
\text{LTV}_{\text{DCF}} = \sum_{t=1}^{\infty} \frac{\text{ARPA} \times \text{Gross Margin \%} \times \text{NRR}^{t-1}}{(1+r)^{t-1}}
$$

割引率 r > NRR成長率 でないと発散。例: NRR=110%, r=15% → 等比級数で

$$
\text{LTV}_{\text{DCF}} = \frac{\text{ARPA} \times \text{GM\%}}{1 - \frac{\text{NRR}}{1+r}} = \frac{\text{ARPA} \times \text{GM\%}}{1 - \frac{1.10}{1.15}}
$$

#### Gross Margin 補正の必要性

LTV は revenue でなく gross profit で測るのが正しい。Gross margin を外すと cost of goods sold (hosting, support) を無視することになる。

#### ベンチマーク (LTV/CAC)

| 区分 | LTV/CAC 目安 | 出典 |
|------|-------------|------|
| 健全 (Skok 原典) | ≥ 3.0x | David Skok 2010 |
| Best-in-class | 5x+ | OpenView 2023 |
| Warning | < 1.5x | 業界実務 |

#### 落とし穴

- **Churn = 0 で発散**: NRR>100% で計算すると LTV = ∞ になる → DCF or finite-horizon に切り替え
- **Multi-product / cross-sell の二重カウント**: cross-sell 後の ARPA で計算すると 過大評価
- **Gross margin が hosting だけ含む**: customer success / R&D 一部も gross margin 控除すべき派あり (出典: Kellblog)
- **Discount rate の扱い**: 付けない LTV と DCF LTV を比較すると後者が過小評価される
- **新規 cohort の LTV を 5 年運用 cohort に外挿**: 早期 churn が高い cohort の特性を無視

#### 投資判断ロジックでの利用法

- LTV/CAC ≥ 3 を「pass / fail」基準にしない (Skok 原典の前提条件 = 安定 churn, 12ヶ月 payback, 多年観測)
- 同じ会社で 3 通り計算し、レンジで判定するのが望ましい
- Cohort-based を真値、Simple を上限、DCF を実用値、と使い分ける

(出典: David Skok 2010, Kellblog 2014, Marketing Case Bootcamp, Standard Ledger)

---

### 4.3 CAC Payback Period

#### 定義

CAC を gross profit で回収するのに要する月数。

#### 計算式 (gross margin 調整済)

$$
\text{CAC Payback (months)} = \frac{\text{CAC}}{\text{ARPA}_{\text{monthly}} \times \text{Gross Margin \%}}
$$

#### Gross margin 補正の重要性

GM 補正なしで計算すると、payback を約 28% 過小評価する (出典: Drivetrain)。

例: CAC $12,000, monthly ARPA $1,000, GM 75%
- 誤 (GM なし): $12,000 / $1,000 = 12 ヶ月
- 正 (GM あり): $12,000 / ($1,000 × 0.75) = 16 ヶ月

#### ベンチマーク

| 区分 | CAC Payback 中央値 | 出典 |
|------|-------------------|------|
| Best-in-class | < 12 ヶ月 | 業界共通 |
| Good | 12-18 ヶ月 | OpenView 2023 |
| Concerning | 18-24 ヶ月 | OpenView 2023 |
| Critical | > 24 ヶ月 | 業界共通 |
| OpenView 2023 (低 ARR 帯) | 約 10 ヶ月 | OpenView 2023 |
| OpenView 2023 (高 ARR 帯) | 約 15 ヶ月 | OpenView 2023 |
| KeyBanc 2024 中央値 | 20 ヶ月 (悪化) | KeyBanc 2024 |
| B2B SaaS 一般 | 15-16 ヶ月 | 業界実務 |

ソース間の食い違い: KeyBanc (中央値 20 ヶ月) vs OpenView/Drivetrain (15-16 ヶ月) は調査対象企業と算出ロジックの差。投資判断ではレンジ提示推奨。

| セグメント別 | CAC Payback |
|-------------|-------------|
| SMB | 8-12 ヶ月 |
| Mid-market | 14-18 ヶ月 |
| Enterprise | 18-24 ヶ月 |

#### 落とし穴

- Gross margin で割らない計算は過小評価
- ARPA を contract 値の 1/12 ではなく net billed で計算すると discount 効果が混じる
- Sales cycle が長い enterprise で CAC を月次計上すると tail が見えない

#### 投資判断ロジックでの利用法

- CAC Payback × Burn Multiple で「投下資金がどれだけ早く回収されるか」を立体評価
- 24 ヶ月超 → growth efficient でない → Series B 以降 fundraise 厳しい

(出典: Drivetrain, OpenView 2023, KeyBanc 2024, Wall Street Prep, SaaS CFO)

---

### 4.4 ARPU / ARPA / ACV / TCV

| 用語 | 定義 |
|------|------|
| ARPU (Average Revenue Per User) | seat / user 単位の月次平均収益 |
| ARPA (Average Revenue Per Account) | logo / アカウント単位の月次または年次平均 |
| ACV (Annual Contract Value) | 1 顧客 1 年あたり契約額 |
| TCV (Total Contract Value) | 1 顧客全契約期間合計 |

#### 計算

$$
\text{ARPA}_{\text{annual}} = \frac{\text{Total ARR}}{\text{Active Customer Count}} = \text{ACV (average)}
$$

$$
\text{TCV} = \text{ACV} \times \text{Contract Length (years)} + \text{One-time fee}
$$

#### ベンチマーク (ACV 帯別の SaaS 類型)

| ACV 帯 | 顧客タイプ | 例 |
|--------|----------|-----|
| < $1K | Self-serve / freemium | Notion, Figma 個人 |
| $1K - $10K | SMB | HubSpot Starter |
| $10K - $100K | Mid-market | Asana Enterprise |
| $100K - $1M | Enterprise | Salesforce, Workday |
| > $1M | Strategic / Lighthouse | 大手金融機関向け SaaS |

#### 落とし穴

- ARPU と ARPA の混同 (seat と account)
- ACV vs TCV: pitch で TCV だけ強調する企業 → 多年契約による短期の見栄え操作
- "Average" が中央値か平均か: 大口 1 社で平均が跳ねる

#### 投資判断ロジックでの利用法

- ACV 上昇トレンド → upmarket movement (down-market move なら逆)
- ACV 上昇と CAC 上昇の比 → 効率成長の判定
- TCV/ACV 比率 → 平均契約年数 (lock-in 強度)

---

## 5. 効率性メトリクス

### 5.1 Magic Number (SaaS Magic Number)

#### 起源

Scale Venture Partners の Rory O'Driscoll が Omniture の分析中に「$1 投資で初年度 $2 戻ってくる、It's Magic!」と発したことが起源 (出典: Scale VP)。

#### 計算式

$$
\text{Magic Number} = \frac{(\text{GAAP Revenue}_q - \text{GAAP Revenue}_{q-1}) \times 4}{\text{S\&M Spend}_{q-1}}
$$

ARR ベース変形版:

$$
\text{Magic Number}_{\text{ARR}} = \frac{\text{Net New ARR}_q \times 4}{\text{S\&M}_{q-1}}
$$

(分母が前期の S&M なのは、当期の ARR 増は前期投資の成果という前提)

#### ベンチマーク

| 値 | 解釈 | アクション |
|-----|------|----------|
| > 1.0 | Strong, scale up | 投資加速 |
| 0.75 - 1.0 | Healthy | 緑信号 |
| 0.5 - 0.75 | Working but unoptimized | 慎重に投資 |
| < 0.5 | Fundamental issues | スケール停止 |

| 出典 | 中央値 |
|------|-------|
| Scale VP 10 年中央値 | 0.7x |
| KeyBanc 2024 | 0.90 |
| OpenView 2023 上位四分位 | > 1.0 |

#### 落とし穴

- **GAAP Revenue 版と ARR 版の混同**: 前者は usage-based でも使えるが ratable subscription 以外で歪む
- **PS や one-time の含み**: Revenue 版を使う場合は注意
- **季節性**: Q4 押し込み → Q1 dip で Magic Number が乱高下
- **S&M 期ずらし**: 前期 vs 当期で計算方針が割れる

#### 投資判断ロジックでの利用法

- Magic Number と Burn Multiple を併用して「効率成長」評価
- Magic Number > 1 かつ Burn Multiple < 1.5 → top quartile efficient growth

(出典: Scale Venture Partners, Kellblog, Wall Street Prep, Klipfolio)

---

### 5.2 Burn Multiple (David Sacks / Craft Ventures)

#### 起源

Craft Ventures の David Sacks が 2020 年頃に提唱。資本効率の核心指標。

#### 計算式

$$
\text{Burn Multiple} = \frac{\text{Net Burn}}{\text{Net New ARR}}
$$

Net Burn = (Operating cash outflow) - (Operating cash inflow)
Net New ARR は前述の waterfall の合計。

#### ベンチマーク (David Sacks)

| Burn Multiple | 評価 |
|---------------|------|
| < 1x | Amazing |
| 1 - 1.5x | Great |
| 1.5 - 2x | Good |
| 2 - 3x | Suspect |
| > 3x | Bad |

#### ステージ別目安

| ステージ | 健全レンジ | 出典 |
|---------|-----------|------|
| ARR $0-$10M | < 1.1x | a16z |
| ARR $10-$50M | < 1.0x | Bessemer 2024 |
| ARR $50M+ | < 0.5x or negative (cash positive) | Bessemer 2024 |
| 「ideal」公開可能像 | 100% growth × 1.2x burn multiple | Bessemer |

#### 落とし穴

- **Net Burn の定義差**: SBC を含めるか, working capital 変動を入れるか
- **One-time event の含み**: 本社移転費, M&A 関連費の扱い
- **ARR 計算法の影響**: Implied ARR を分母に使うと burn multiple が動く
- **マイナス Net New ARR 期**: 計算不能 (定義上意味を成さない)

#### 投資判断ロジックでの利用法

- Burn Multiple が 4 四半期連続 < 1.5 → Series C+ で安定して fundraise 可能
- 急上昇 (1 → 3) → product-market fit 後退の警告
- Magic Number と組み合わせて「効率の質」評価

(出典: Sacks "The Burn Multiple" Substack, Wall Street Prep, Drivetrain)

---

### 5.3 Rule of 40

#### 定義

成長率と FCF margin の合計が 40% 以上であるべき (Brad Feld 2015 が初出, Bessemer 普及)。

#### 計算式

$$
\text{Rule of 40} = \text{Revenue Growth \%}_{\text{YoY}} + \text{FCF Margin \%}
$$

または:

$$
\text{Rule of 40} = \text{ARR Growth \%}_{\text{YoY}} + \text{Operating Margin \%}
$$

(Operating margin 派は SBC 抜きで)

#### ベンチマーク

| 値 | 評価 |
|-----|------|
| > 40 | Healthy |
| > 60 | Top quartile |
| > 80 | Elite (Snowflake, Datadog 一時) |
| < 30 | Concerning |

#### 落とし穴

- **margin の定義**: FCF, EBITDA, Operating margin を混在
- **Growth の定義**: GAAP revenue / ARR / Billings で値が変わる
- **小規模時の過大評価**: ARR 成長 200% × FCF -100% = R40 = 100 だが燃焼激しいと評価が歪む

#### 投資判断ロジックでの利用法

- Public SaaS valuation との相関高 (Meritech, Bessemer の散布図参照)
- Rule of 40 単独でなく Rule of X (後述) と併用推奨

(出典: Brad Feld 2015, Bessemer State of the Cloud, Meritech)

---

### 5.4 Rule of X (Bessemer 拡張)

#### 定義

Rule of 40 が成長と利益を同等扱いするのを補正。成長を 2-3 倍 weighting して将来 NPV と整合させる。

#### 計算式

$$
\text{Rule of X} = X \times \text{Revenue Growth \%} + \text{FCF Margin \%}
$$

| ステージ | X (推奨係数) | 出典 |
|---------|------------|------|
| Late-stage private | ~2x | Bessemer |
| Public (low cost of capital) | ~2-3x | Bessemer |
| Hyper-growth (Snowflake 型) | ~3x | Bessemer |

#### 比較例

| 企業 | Growth | FCF Margin | Rule of 40 | Rule of X (X=2) |
|------|--------|-----------|-----------|----------------|
| A 社 | 30% | 15% | 45 | 75 |
| B 社 | 15% | 30% | 45 | 60 |

Rule of 40 では同等だが、A 社のほうが NPV 大 (= Bessemer 主張)。

#### 投資判断ロジックでの利用法

- Rule of X の R² (EV/Revenue 説明力) は Rule of 40 比 ~1.5x (Bessemer)
- Late-stage SaaS valuation の最有力指標 (公開市場で実証)
- 1 つの数字で評価せず、growth 質 (NRR), efficiency (Burn Multiple) を並列確認

(出典: Bessemer "The Rule of X", TechCrunch 2023, Clouded Judgement, OnlyCFO)

---

### 5.5 SaaS Quick Ratio

#### 起源

Mamoon Hamid (現 Kleiner Perkins, 当時 Social Capital) が SaaStr Annual で提唱。

#### 計算式

$$
\text{Quick Ratio} = \frac{\text{New MRR} + \text{Expansion MRR}}{\text{Churned MRR} + \text{Contraction MRR}}
$$

#### ベンチマーク

| 値 | Hamid の評価 |
|-----|-------------|
| > 4 | Good (Hamid の投資基準) |
| 2 - 4 | OK |
| < 2 | 投資見送り |

#### 落とし穴

- 分母が小さいと膨らみすぎる (early-stage で意味薄)
- Reactivation の扱いが流派により異なる
- 月次/四半期/年次で値が変わる

#### 投資判断ロジックでの利用法

- Series A-B の効率成長スクリーニング
- 4 期連続 > 4 → growth quality の signal
- Magic Number / Burn Multiple との併用で立体把握

(出典: SaaStr, Tunguz, The SaaS CFO)

---

### 5.6 Bessemer Efficiency Score

#### 計算式

$$
\text{Efficiency Score} = \frac{\text{Net New ARR}}{\text{Net Burn}}
$$

Burn Multiple の逆数。Bessemer 推奨。

#### ベンチマーク

| ARR 段階 | Efficiency Score 目安 |
|---------|---------------------|
| $25-$50M | 70%+ |
| $100M+ | 50%+ |

(出典: Bessemer State of the Cloud)

---

### 5.7 Revenue per Employee

#### 計算

$$
\text{Revenue per Employee} = \frac{\text{ARR}}{\text{Headcount}}
$$

#### ベンチマーク

| 段階 | Revenue/HC 目安 |
|------|---------------|
| Series A | $100K - $200K |
| Series B | $150K - $250K |
| Series C+ | $200K - $400K |
| Best-in-class public (efficient) | $400K - $1M+ |

(出典: KeyBanc 2024, Bessemer 2024)

#### 落とし穴

- Contractor 含むか、SBC 含むかで値が変わる
- AI 時代に急上昇傾向 → 過去比較は注意

---

## 6. コホート分析

### 6.1 Revenue Cohort Retention Curves

#### 概念

ある月 (cohort 起点) に獲得した顧客群の、起点を 100% としたその後の revenue 推移を時系列でプロットする。

#### 解釈

| パターン | 意味 |
|---------|------|
| 単調減少 (90% → 70% → 60%) | 通常の churn |
| 急減後フラット | 早期 churn 後に core users が定着 |
| 単調増加 (Smile curve) | NRR > 100%, expansion 効いている |
| U字 (Smile curve 下半身) | churn 後に reactivation が来る |

#### 落とし穴

- **Cohort sample size の違い**: 古い cohort は size 小さく noise 大
- **平均化による歪み**: 月次 cohort を年次で集計すると粒度落ちる

---

### 6.2 Layer Cake Chart

#### 定義

各 cohort を別色で積み上げグラフにし、ARR/MRR の累積を可視化。

#### 解釈

- 各層が時間とともに薄くなる → churn (= 縮小)
- 各層が時間とともに厚くなる → expansion (= NRR>100%)
- 新層 (上に積まれる) が大きい → New ARR が活発

#### 投資判断ロジックでの利用法

- 上位 cohort が時間とともに分厚くなっていれば NRR が公称値通り (改ざんチェック)
- 新層が縮小傾向 → New ARR 鈍化
- 古い cohort が突然消える → 一括解約 (顧客集中リスク)

---

### 6.3 Smile Curve

#### 定義

Cohort retention curve が当初下がった後で再上昇する形状。

#### 出現条件

- 強い network effect (Slack, Airbnb)
- Per-seat / consumption pricing で組織内拡散
- Reactivation が活発

#### 投資判断ロジックでの利用法

- Smile curve の存在 → defensibility の強い signal
- 業界内で Smile を出している企業は valuation premium 取れる

(出典: Userpilot, Stripe, Mosaic)

---

### 6.4 Cohort Gross Margin の経時変化

新規 cohort は実装コストや一時的サポート費が嵩むため gross margin が低い。Mature cohort は GM が改善する。

#### 投資判断ロジックでの利用法

- Cohort GM が経時改善 = 「scale economics」の証拠
- 改善しない or 悪化 → product cost 構造に問題 (hosting cost 制御不能等)

---

### 6.5 Stack Loss Problem (Cohort 計算の罠)

連続四半期でデータを集計すると、各 cohort の損失が複合し、表面上の retention が実態より高く見える「stack loss」が発生。

#### 対策

- 各 cohort 単独で曲線を引き、平均化しない
- Triangulation: cohort 起点別に複数年見る

---

## 7. マルチプルとバリュエーション

### 7.1 EV / NTM ARR

#### 定義

$$
\text{EV/NTM ARR} = \frac{\text{Enterprise Value}}{\text{Next Twelve Months Forward ARR}}
$$

NTM ARR は forward 12 ヶ月予測の年率化 ARR。

---

### 7.2 EV / NTM Revenue

#### 定義

$$
\text{EV/NTM Revenue} = \frac{\text{Enterprise Value}}{\text{NTM Revenue (analyst consensus)}}
$$

#### ベンチマーク (公開 SaaS)

| 期間 | EV/NTM Revenue 中央値 | 出典 |
|------|----------------------|------|
| 2021 ピーク | 15-20x+ | Meritech, Bessemer |
| 2023 後半 | 5-7x | Aventis Advisors |
| 2024 中央値 | 6-8x | Aventis Advisors |
| 2025 Q3 | 6-9x (BVP EMCLOUD) | Bessemer Cloud Index |
| 2026 Q1 推定 | 8-9x (EMCLOUD) | Bessemer Cloud Index |
| 全 SaaS 中央値 (2026 年初) | ~4.0x (157 社) | SaaS Valuation Multiple |

#### セクター別 (2025 Oct)

| セクター | EV/NTM Revenue |
|---------|---------------|
| Data infrastructure | 6.2x |
| DevOps | 5.7x |
| Sales/Marketing automation | 1.9x |

(出典: Multiples.vc 2025 Oct)

---

### 7.3 Growth-adjusted Multiple

#### 計算

$$
\text{Growth-adjusted Multiple} = \frac{\text{EV/Revenue}}{\text{Revenue Growth \%}}
$$

成長率による割安/割高補正。1.0 を中立とする見方が一般的。

---

### 7.4 参照ソース

| ソース | 内容 | URL |
|-------|------|-----|
| Bessemer Cloud Index (BVP Nasdaq Emerging Cloud Index) | 公開 SaaS の指数 | cloudindex.bvp.com |
| Meritech Comp Tables | 公開 SaaS 個別 multiple | meritechcapital.com |
| Aventis Advisors | 2015-現在の四半期データ | aventis-advisors.com |
| SaaS Capital Index | 公開 SaaS 指数 | saas-capital.com |
| Clouded Judgement (Jamin Ball) | 週次 SaaS 公開市場分析 | cloudedjudgement.substack.com |
| Public Comps | 公開比較データ | publiccomps.com |

---

### 7.5 落とし穴

- **NTM 予測の信頼性**: アナリスト consensus が当たらない時期 (2022-2023) はマルチプルが歪む
- **GAAP Revenue ベースか Implied ARR ベースか**: Snowflake/Datadog 型は両者で差が出る
- **Stock-based compensation の扱い**: GAAP では費用、Non-GAAP では除外 → EV 算定で議論
- **Take-private 案件**: 公開比較で見積もると 20-30% プレミアム/ディスカウント

#### 投資判断ロジックでの利用法

- Median Multiple × 自社 NTM ARR で Lower-bound valuation
- Rule of X 値の散布図上の自社プロット → comp 群対比
- セクター別中央値で「妥当レンジ」設定

---

## 8. 業界ベンチマーク (出典別)

### 8.1 OpenView SaaS Benchmarks (2023 / 2025 共著: High Alpha)

- **2023 サンプル**: 710 operators (2023/7/26 - 9/1)
- **2025**: OpenView × High Alpha 共同 (Kyle Poyar 関与)

主要数値 (2023):

| 指標 | 中央値 |
|------|-------|
| NRR (top quartile expansion stage) | 119% → 107% (低下) |
| CAC payback (低 ARR 帯) | 約 10 ヶ月 |
| CAC payback (高 ARR 帯) | 約 15 ヶ月 |

(出典: openviewpartners.com/2023-saas-benchmarks-report)

---

### 8.2 KeyBanc Capital Markets × Sapphire Ventures SaaS Survey

- **2024 サンプル**: 100+ 社 private SaaS (中央値 $26M ARR)
- 公表: info.sapphireventures.com

主要数値 (2024):

| 指標 | 中央値 |
|------|-------|
| Net retention | ~101% |
| Gross retention | ~90% |
| CAC payback | 20 ヶ月 |
| Magic Number | 0.90 |
| Top performers NRR | 115-125% |

---

### 8.3 Bessemer State of the Cloud

毎年 Bessemer Venture Partners が発表。2024 年版は AI integration が主軸。

主要 framework:

- Rule of X (年間更新)
- Bessemer Efficiency Score 目標
- Cloud Index ($EMCLOUD) 中央値推移

(出典: bvp.com/atlas)

---

### 8.4 SaaStr / Tomasz Tunguz データ

- Tunguz (Theory Ventures, ex-Redpoint) が tomtunguz.com で継続公開
- SaaStr Annual カンファレンスで Mamoon Hamid (Quick Ratio), David Sacks (Burn Multiple) などが原典提唱

主要数値 (Tunguz, 過去):

| Year | Series A 中央値 ARR | 成長率 |
|------|-------------------|-------|
| 2018 | $1.8M | 250% |
| 2019 | $1.0-1.5M (信頼区間 ~$1.7M) | - |
| 2022-2024 | 一部 $30K-$50K まで低下 | macroenv 影響 |

(数値は近似、出典 tomtunguz.com)

---

### 8.5 Kyle Poyar (OpenView → Tremont) のフレームワーク

- Growth Unhinged (newsletter)
- Product-Influenced Revenue (PIR) の提唱

PIR ベンチマーク:

| 採用モデル | Good | Great |
|----------|------|-------|
| Sales-led | 5% | 35%+ |
| Self-serve free trial | 70% | 95%+ |
| Freemium | 90% | 100% |

(出典: growthunhinged.com)

---

### 8.6 ChartMogul SaaS Retention Report

- 2023 年版: SMB / Mid / Enterprise 別 retention 中央値
- データソース: ChartMogul 顧客 (~2,000 社)

(出典: chartmogul.com/reports/saas-retention-report)

---

### 8.7 Ray Rike "SaaS Barometer"

- 公開市場+ private SaaS 横断
- LinkedIn / Substack で継続発信

---

## 9. 典型的な落とし穴と誤用

### 9.1 "Implied ARR" の誤用

#### 問題

- Snowflake, Twilio, AWS の様な consumption 型は ARR を公式報告しない
- アナリストは "Implied ARR = 直近 quarter GAAP Revenue × 4" を代用
- これは「契約された継続性」と異なる単なる売上年率化

#### 誤用パターン

- Implied ARR 成長率 ≠ 真の Net New ARR 成長率
- Implied ARR を NRR や Burn Multiple の分母に流用 → 数値が歪む
- 過剰請求 (multi-year billing upfront 比率増) で Implied ARR が実態より膨らむ

#### 正しい扱い

- Snowflake / Datadog 型 → ARR は MRR×12 を独立に開示し、Implied ARR とは別物として扱う (Datadog の例)
- 評価時は両方並べて読む

(出典: Ordway Labs 2024, Datadog 10-Q)

---

### 9.2 One-time Revenue (PS) を ARR に混ぜる

#### 問題

実装費、トレーニング費、PS (Professional Services) は recurring でない。

#### 影響

- ARR が一時的に膨らむ
- NRR が次年度に「自動低下」(PS が翌年消える) → 実態は単に PS 落ち
- LTV/CAC が過大評価

#### 検知

- 顧客リストの 1st year と 2nd year ARR を比較し、systematic な低下があれば PS 混入を疑う
- "Subscription Revenue" と "Services Revenue" が 10-K で別開示されているか

---

### 9.3 Discount を Gross / Net どちらで計上するか

#### 問題

初年度割引 50% を「契約定価で ARR 計上 + 別途割引引当」(gross) するか、「割引後実額」(net) にするか。

#### 影響

- Gross 計上 → 翌年に「expansion」が発生 (実態は割引剥がれ)
- Net 計上 → 翌年同額継続なら NRR=100%

#### 業界標準

- ASC 606 / IFRS 15 では transaction price = 割引後 net で認識
- ただし「ARR」は GAAP 外なので企業裁量
- 開示文言で確認 (例: "ARR is based on contractual subscription revenue, net of discounts")

---

### 9.4 月次 Churn から年次への変換誤差

§ 3.4 の表参照。3% 月次で 5.4pt 過大評価。Pitch deck の「Annual churn 12%」が「Monthly churn 1%」由来かどうか必ず確認。

---

### 9.5 Cohort 計算の Stack Loss

§ 6.5 参照。集計レベルが粗いと cohort 単位の loss が見えなくなる。

---

### 9.6 Logo Retention で Revenue を語る

10 顧客中 9 顧客が retain (Logo Retention 90%) でも、最大顧客 1 社が抜けて Revenue Retention 50% という事態は起こりうる。両方並べる。

---

### 9.7 NRR の「12 ヶ月前 cohort」基準のずれ

NRR 計算で「12 ヶ月前 ARR」と「期初 ARR」をどう取るかで値が変わる。

- 公式 A: $\text{NRR} = \frac{\text{ARR from same cohort today}}{\text{ARR from same cohort 12 mo ago}}$
- 公式 B: $\text{NRR} = \frac{\text{Starting ARR + Expansion - Contraction - Churn}}{\text{Starting ARR}}$

前者は cohort 厳密、後者は期間 flow ベース。混用注意。

---

### 9.8 Cohort 起点の選定 bias

特殊月 (大型契約成立月) を cohort とすると不自然に強い retention が見える。月次 cohort を 12 ヶ月平均で見るのが安全。

---

### 9.9 Stock-Based Compensation の扱い

GAAP では費用、Non-GAAP / "adjusted" では除外。Burn Multiple や FCF margin の比較時にどちらかを統一。

---

### 9.10 Mark-to-Market 為替の歪み

USD 建報告だが顧客契約が複数通貨の場合、為替変動で "Expansion / Contraction" に見える金額が発生。FX-neutral NRR を別途出すのが best practice。

---

## 10. GAAP vs SaaS Metrics: ASC 606 / IFRS 15

### 10.1 5-Step Model (ASC 606 / IFRS 15 共通)

1. **Identify the contract**: 契約の特定
2. **Identify performance obligations**: 履行義務の特定
3. **Determine transaction price**: 取引価格の決定
4. **Allocate transaction price**: 履行義務への割当
5. **Recognize revenue**: 履行義務の充足時に認識

両基準で 5-step は同一。違いは細部。

### 10.2 ASC 606 (US GAAP) と IFRS 15 の差

| 論点 | ASC 606 | IFRS 15 |
|------|---------|---------|
| Collectibility threshold | "Probable" = 75-80% | "More likely than not" = >50% |
| Contract cost capitalization | ASC 340-40 で営業 commission / 実装費を資産化可能 | より厳格、多くは即時費用化 |
| Cloud implementation cost | 状況による (顧客ソフトウェア管理権の有無) | 2019 IFRIC 解釈で原則即時費用化 |
| Renewal accounting | 更新期間開始まで認識繰延 | おおむね同様 |
| 開示要件 (RPO) | 詳細 (ASC 606-10-50-13) | やや簡素 |

(出典: PwC IFRS 15 Guide, DualEntry, FinanSys)

### 10.3 SaaS の典型的な認識パターン

- **Pure subscription (月額)**: 契約期間にわたり ratable に認識
- **Annual prepay**: 入金時点で deferred revenue 計上 → 月次に按分認識
- **Multi-year prepay**: 全額 deferred revenue → 期間按分
- **Usage-based**: 使用実績に応じて認識 (Snowflake, AWS)
- **Hybrid (commitment + usage)**: commitment は ratable, overage は usage

### 10.4 SaaS Metrics (ARR/MRR) と GAAP Revenue のズレが発生する場面

- Multi-year prepay で billings >> revenue
- Usage-based の peak / trough
- Year-end push (Bookings 急増) で deferred revenue が膨らむ
- Discount / refund / credit memo

#### 投資判断ロジックでの利用法

- ARR と GAAP Revenue を並べ、年度内の deferred revenue 推移を見る
- Implied ARR と reported ARR の差 = ratable subscription 比率の指標

---

## 11. Vertical SaaS / Usage-based Pricing 特殊事項

### 11.1 Usage-based / Consumption Model の特性

#### 例

- Snowflake: コンピュート / ストレージ使用量に応じた課金
- Datadog: ホスト数 + ログ量 + APM 等の組み合わせ
- AWS / Twilio: 純粋 consumption
- MongoDB: capacity + usage hybrid

#### Recurring Revenue 定義の難しさ

- 契約上の commitment (= floor) と実 usage が乖離
- ARR 報告は (a) commitment ベース (b) trailing usage 年率化 (c) MRR×12 の 3 流派

(出典: Ordway Labs 2024)

### 11.2 NRR が異常に高くなる構造

- 既存顧客の usage 増 (= expansion) が大きく出やすい
- New logo 獲得が遅くても、既存からの expansion で全体成長確保
- 結果、Snowflake は一時 NRR 150%+ (2022 年時点ピーク; canonical 値は `_terminology.md §6` の FY24 Q4 = 131%, FY25 Q2 = 127%), Datadog mid-110%

### 11.3 Vertical SaaS の特殊論点

- 業界固有の seasonality (税務 SaaS の Q1, 小売 SaaS の Q4)
- Long sales cycle (12-18 ヶ月) → CAC payback が見かけ長い
- Embedded fintech revenue (payments, lending) は recurring の定義から外れがち

### 11.4 Non-recurring 部分の扱い

| 項目 | 扱い |
|------|------|
| 実装費 / Onboarding | Services Revenue (別開示) |
| Marketplace 手数料 | Recurring に近いが usage-based |
| Payments take rate | Hybrid (volume × rate) |
| Hardware (POS 等) | One-time、ARR から除外 |
| Float income | Other income 扱い |

#### 投資判断ロジックでの利用法

- "Subscription Revenue / Total Revenue" 比率 → SaaS 純度
- Vertical SaaS で 60%+ recurring → SaaS multiple 適用妥当
- 30-50% recurring → Hybrid (SaaS と Services の中間 multiple)

---

## 12. SaaS デューデリジェンス チェックリスト

### 12.1 収益の質

- [ ] ARR の定義書 (定義文書) を入手
- [ ] ARR と GAAP Revenue の reconciliation テーブル
- [ ] One-time / PS Revenue の比率
- [ ] Multi-year contract 比率 (ARR vs TCV)
- [ ] Annual prepay / monthly billing の比率
- [ ] Implied ARR と Reported ARR の乖離 (consumption 型)
- [ ] Currency 別 ARR breakdown
- [ ] Discount 計上方針 (gross / net)

### 12.2 顧客と Retention

- [ ] 過去 12-24 ヶ月の cohort retention 表 (revenue / logo 別)
- [ ] NRR / GRR の trailing 12 ヶ月推移
- [ ] Top 10 顧客の ARR 占有率 (3 年分)
- [ ] Top 10 顧客の renewal 履歴
- [ ] 親会社単位での名寄せ
- [ ] Logo churn / Revenue churn の差
- [ ] Reactivation 顧客比率

### 12.3 ユニットエコノミクス

- [ ] CAC の定義 (blended / paid / fully-loaded)
- [ ] CAC Payback (gross margin 補正済) の trailing 推移
- [ ] LTV 3 通り計算 (simple, cohort, DCF) と乖離分析
- [ ] LTV/CAC trailing 12 ヶ月推移
- [ ] Channel 別 CAC (organic / paid / partner)
- [ ] Sales rep の ramp time とquota attainment

### 12.4 効率性

- [ ] Magic Number 4 quarter trend
- [ ] Burn Multiple 4 quarter trend
- [ ] Rule of 40 / Rule of X (X=2)
- [ ] SaaS Quick Ratio
- [ ] Revenue per Employee
- [ ] Headcount mix (R&D / S&M / G&A)

### 12.5 会計と GAAP

- [ ] ASC 606 / IFRS 15 監査済財務諸表
- [ ] Deferred Revenue / RPO / cRPO 開示
- [ ] Bookings vs Billings vs Revenue reconciliation
- [ ] SBC 額と扱い
- [ ] Auditor 名 (Big 4 か否か)

### 12.6 製品とプロダクトマーケットフィット

- [ ] DAU / MAU / WAU と stickiness ratio
- [ ] Product-Influenced Revenue 比率 (PLG 系)
- [ ] Feature adoption 表
- [ ] NPS / CSAT の trailing trend

### 12.7 競合と市場

- [ ] TAM / SAM / SOM の根拠ソース
- [ ] 直接競合の comp table (multiple, NRR, growth)
- [ ] Win/loss 分析

### 12.8 リスク

- [ ] Customer concentration (Top 1, 5, 10)
- [ ] Geographic concentration
- [ ] Technology dependency (AWS, OpenAI 等の vendor risk)
- [ ] Key-person dependency
- [ ] Pending litigation
- [ ] Compliance (SOC 2, ISO 27001, GDPR, HIPAA)

---

## 13. メトリクス改ざん検知チェックリスト

### 13.1 数値整合性

- [ ] ARR と GAAP Revenue の比率 (subscription 純度) が四半期で大きく揺らぐ → 定義変更の可能性
- [ ] NRR が報告値とコホート計算で 5pt 以上ズレる → 計算式変更
- [ ] Magic Number と Rule of 40 が同時に劇的改善 → S&M reclassification の疑い
- [ ] CAC が前期比 30%+ 低下 → channel 再分類または期ずらし変更

### 13.2 用語のすり替え

- [ ] "Bookings" を "Revenue" として表示 (multi-year 込みで膨らませる)
- [ ] "TCV" を "ARR" と称する (年率化していない)
- [ ] "ARR" に PS / 実装費を混入
- [ ] "MRR" を月次最高値で固定し平均値と称する
- [ ] "Adjusted EBITDA" の調整項目に SBC + 訴訟費 + restructuring を全部入れる

### 13.3 タイミング操作

- [ ] 四半期末駆け込み Bookings (channel stuffing) → 翌期 Bookings 急減
- [ ] Annual prepay を期末に集中 → Billings 跳ねるが ARR は変化薄
- [ ] 解約申込日と契約終了日の差を悪用 (申込済を残ARR にカウント)
- [ ] Reactivation を当月 New ARR に二重計上

### 13.4 Cohort / Sample 操作

- [ ] 公開する cohort を都合の良い月に限定
- [ ] 大口 1 社で NRR 全体が膨らむ → median NRR を併記しない
- [ ] 「Top 25% of customers」NRR だけ強調し全体 NRR を伏せる
- [ ] Churn cohort の expansion を別 cohort で計上

### 13.5 一回性収益の混入

- [ ] PS が ARR に組み込まれている兆候 (前述)
- [ ] Hardware 売上を SaaS と合算
- [ ] Setup fee を 12 ヶ月按分して MRR に混ぜる
- [ ] One-time discount を 12 ヶ月按分

### 13.6 Discount / Credit 操作

- [ ] Credit memo を頻発し ARR を維持 (実質 churn を隠蔽)
- [ ] Free month 大量配布で contract value を維持
- [ ] Discount を expansion 控除に分類

### 13.7 関係者取引

- [ ] Investor / Board members の会社が顧客になっている (related-party revenue)
- [ ] Founder の knapsack 会社が PS revenue 提供
- [ ] Sister company 間の循環取引

### 13.8 監査と統制

- [ ] Auditor が頻繁に交代
- [ ] CFO が直近 2 年で複数交代
- [ ] Material weakness の開示
- [ ] Restatement (修正再表示) 履歴

### 13.9 Public Filing 整合性

- [ ] 10-K の Subscription Revenue と Investor Deck の ARR が整合
- [ ] RPO / cRPO 推移が Bookings 推移と整合
- [ ] Deferred Revenue 推移が billing pattern と整合

### 13.10 数字の「鋭さ」

- [ ] ARR がきれいに $10.0M, $25.0M で揃う (rounding 過剰)
- [ ] 連続四半期で全指標が一斉改善 (operating reality と乖離)
- [ ] NRR が 4 期連続で 130%+ (特殊事情なくは異例)

---

## 14. 出典一覧 (URL)

### 主要レポートとブログ

- OpenView 2023 SaaS Benchmarks Report — https://openviewpartners.com/2023-saas-benchmarks-report/
- 2024 KeyBanc Capital Markets & Sapphire Ventures SaaS Survey — https://info.sapphireventures.com/2024-keybanc-capital-markets-and-sapphire-ventures-saas-survey
- Bessemer State of the Cloud 2024 — https://www.bvp.com/atlas/state-of-the-cloud-2024
- Bessemer The Rule of X — https://www.bvp.com/atlas/the-rule-of-x
- BVP Nasdaq Emerging Cloud Index — https://cloudindex.bvp.com/
- David Sacks "The Burn Multiple" — https://medium.com/craft-ventures/the-burn-multiple-51a7e43cb200
- Scale Venture Partners "A History of the Magic Number" — https://www.scalevp.com/insights/saas-metrics-a-history-of-the-magic-number/
- David Skok / Kellblog "The Ultimate SaaS Metric: LTV/CAC" — https://kellblog.com/2014/07/30/the-ultimate-saas-metric-ltv-cac/
- Tomasz Tunguz Benchmarks — https://tomtunguz.com/categories/benchmarks
- Kyle Poyar "Growth Unhinged" — https://www.growthunhinged.com/
- ChartMogul SaaS Retention Report — https://chartmogul.com/reports/saas-retention-report/
- Ray Rike "SaaS Barometer" — https://thesaasbarometer.substack.com/

### 計算式と用語解説 (一次/二次)

- Wall Street Prep Burn Multiple — https://www.wallstreetprep.com/knowledge/burn-multiple/
- Wall Street Prep NRR — https://www.wallstreetprep.com/knowledge/net-revenue-retention-nrr/
- Wall Street Prep CAC Payback — https://www.wallstreetprep.com/knowledge/cac-payback-period/
- Wall Street Prep Magic Number — https://www.wallstreetprep.com/knowledge/saas-magic-number/
- Wall Street Prep Customer Concentration — https://www.wallstreetprep.com/knowledge/customer-concentration/
- Wall Street Prep Bookings vs Billings — https://www.wallstreetprep.com/knowledge/bookings/
- Wall Street Prep Churn Rate — https://www.wallstreetprep.com/knowledge/churn-rate/
- The SaaS CFO RPO — https://www.thesaascfo.com/understanding-remaining-performance-obligations-in-saas/
- The SaaS CFO Magic Number — https://www.thesaascfo.com/calculate-saas-magic-number/
- The SaaS CFO Quick Ratio — https://www.thesaascfo.com/saas-quick-ratio/
- The SaaS CFO LTV/CAC — https://www.thesaascfo.com/ltv-to-cac-ratio-of-three/
- Drivetrain CAC Payback — https://www.drivetrain.ai/strategic-finance-glossary/cac-payback-period-formula-benchmarks-and-how-to-reduce-it
- Drivetrain Burn Multiple — https://www.drivetrain.ai/strategic-finance-glossary/what-is-burn-multiple-formula
- Drivetrain RPO — https://www.drivetrain.ai/strategic-finance-glossary/rpo-for-saas
- ChartMogul NRR — https://chartmogul.com/saas-metrics/nrr/
- ChurnZero NRR — https://churnzero.com/churnopedia/net-revenue-retention/

### 会計基準 (ASC 606 / IFRS 15)

- PwC IFRS 15 Guide for Software & SaaS — https://viewpoint.pwc.com/content/dam/pwc-madison/ditaroot/gx/en/pwc/industry/software/revenue-recognition-an-ifrs-15-guide-for-software-and-saas-sellers/assets/Revenue_Recognition_An_IFRS_15_Guide_for_Software_and_SaaS_sellers_2022.pdf
- PwC ASC 606 Q&A Software/SaaS — https://viewpoint.pwc.com/content/dam/pwc-madison/ditaroot/us/en/pwc/accounting_guides/software-saas/assets/pwcrevrecguisoftsaas.pdf
- DualEntry ASC 606 vs IFRS 15 — https://www.dualentry.com/blog/revenue-recognition-methods
- Maxio ASC 606 SaaS Guide — https://www.maxio.com/blog/saas-revenue-recognition-asc-606
- FinanSys ASC 606 / IFRS 15 — https://finansys.com/blog/asc-606-ifrs-15-compliance-for-saas-businesses/

### Cohort / Layer Cake / Smile Curve

- Userpilot Retention Curve — https://userpilot.com/blog/retention-curve/
- Stripe SaaS Cohort Analysis — https://stripe.com/resources/more/saas-cohort-analysis
- Mosaic Customer Cohorts — https://www.mosaic.tech/financial-metrics/customer-cohorts
- Churnkey Retention Curves — https://churnkey.co/blog/retention-curves/

### Multiples / Valuation

- Aventis Advisors SaaS Valuation Multiples — https://aventis-advisors.com/saas-valuation-multiples/
- Multiples.vc — https://multiples.vc/reports/software-saas-valuation-multiples
- Public SaaS Companies — https://publicsaascompanies.com/saas-multiples/
- Clouded Judgement (Jamin Ball) — https://cloudedjudgement.substack.com/

### Implied ARR / Usage-based

- Ordway Labs "Cloud Usage-based Pricing Report ARR" — https://ordwaylabs.com/blog/cloud-usage-based-pricing-report-arr/
- Ordway Labs RPO — https://ordwaylabs.com/blog/metrics-blog/remaining-performance-obligations/
- Datadog Investor Relations — https://investors.datadoghq.com/

### Concentration / DD

- Livmo Customer Concentration — https://livmo.com/blog/why-customer-concentration-kills-deals-and-how-to-diversify-fast/
- Morgan & Westfield Concentration — https://morganandwestfield.com/knowledge/reducing-concentrations-of-risk-before-selling-your-business/

### その他 (用語と概念)

- SaaStr Mamoon Hamid Numbers That Matter — https://www.saastr.com/mamoon-hamid-social-capital-numbers-actually-matter-founders-video-transcript/
- Kellblog Bookings vs Billings — https://kellblog.com/2018/05/10/bookings-vs-billings-in-a-saas-company/
- OPEXEngine Bookings/Billings/Revenue — https://www.opexengine.com/post/what-the-heck-is-the-difference-between-bookings-billings-and-recognized-revenue-for-saas-companies

---

## 付録 A: 投資判断ロジック簡易フロー (dual verification)

1. **Stage 判定**: ARR 絶対額 → Series A/B/C
2. **Growth quality**: ARR 成長率 + NRR + Magic Number でスクリーニング
3. **Capital efficiency**: Burn Multiple + Rule of X + CAC Payback で 3 軸チェック
4. **Customer base health**: GRR + Logo Churn + Top10 Concentration
5. **Forward visibility**: cRPO 成長率 + Billings/Revenue 比率
6. **Multiple 妥当性**: EV/NTM Revenue を Bessemer Cloud Index 中央値・Rule of X 散布図と照合
7. **Red flag check**: § 13 改ざん検知チェックリストで full pass
8. **GAAP 整合性**: ASC 606 / IFRS 15 認識と SaaS metric の差を分解

各ステップで複数指標による cross-check を行い、単一指標で判断しない。

---

## 付録 B: 用語英和対応表

| 英語 | 和訳 |
|------|------|
| Recurring | 繰り返し性のある (継続的) |
| Bookings | 受注 / 契約署名額 |
| Billings | 請求額 |
| Deferred Revenue | 前受収益 |
| Backlog | 受注残 / 契約残高 |
| Performance Obligation | 履行義務 |
| Cohort | コホート (同期間集団) |
| Stickiness | 定着性 / 粘着性 |
| Take Rate | 手数料率 |
| Net Negative Churn | 純解約マイナス (NRR>100%) |
| Land & Expand | 初期小規模獲得後の拡張戦略 |

---

> **本書の使い方**: skill 内の他リファレンス (収益モデル、コホート分析、バリュエーション) と併読する。投資判断に用いる際は、§ 12 と § 13 の二つのチェックリストを必ず通すこと。一次資料の最新版は § 14 のリンクから入手し、ベンチマーク数値は四半期ごとに更新を推奨する。
