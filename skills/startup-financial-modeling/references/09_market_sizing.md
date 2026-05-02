---
name: market_sizing
description: 市場規模 (TAM / SAM / SOM) と浸透率 (Penetration Rate) モデリングの正本。Top-down / Bottom-up / Triangulation の三方式、業態別 calibration、source citation。SKILL.md dispatch table の "Market sizing" entry の第 1 reference として読まれる。
type: reference
priority: P1
related: [_terminology, 03_business_models, 08_investment_thesis]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: TAM/SAM/SOM 定義 / Triangulation 手順は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §C`](_master_decision_tree.md) (投資判断 / TAM tiebreak) から第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (Top-down / Bottom-up triangulation gap < 50%) を必ず実行
- **関連 reference**: `03_business_models` (業態別 SAM 算出) / `08_investment_thesis §7.4` (TAM tiebreak)

# 09. 市場規模 (TAM / SAM / SOM) と浸透率 (Penetration Rate) モデリング リファレンス

> **役割**: スタートアップ向け包括的財務モデリング skill の **bottom-up revenue forecast 正本**。
> 市場規模 × 浸透率 × 単価 の三項モデルを正しく組むための参照資料。`scripts/build_model.py` の Revenue シート生成ロジックから直接参照される。
> 投資判断側 (judgment-side, 参照: `08_investment_thesis.md`) の TAM 検証 (§7) と組で機能する。

---

## 0. このリファレンスの使い方

### 0.1 三項モデルの基本式

bottom-up revenue forecast の最小骨格は以下:

$$
\text{Revenue}(t) = \underbrace{\text{TAM}(t)}_{\text{市場規模}} \times \underbrace{\text{SAM\%}(t)}_{\text{到達可能比率}} \times \underbrace{p(t)}_{\text{浸透率}} \times \underbrace{\text{ARPU}(t)}_{\text{単価}}
$$

または同値で

$$
\text{Revenue}(t) = N(t) \times \text{ARPU}(t),\quad N(t) = \text{SAM units}(t) \times p(t)
$$

ここで $N(t)$ は時点 $t$ の有料顧客数、$p(t)$ は SAM 内浸透率 (penetration rate, 0 ≤ p ≤ 1)。

### 0.2 build-side との接続

| モデル出力 | 本リファレンス節 | judgment-side (`08_investment_thesis.md`) |
|---|---|---|
| TAM / SAM / SOM 三層図 | §1, §10 | §7 TAM 健全性 |
| Top-down / Bottom-up / Value-based 計算 | §2 | §7 三角測定 |
| Logistic / Bass 浸透率モデル | §3 | §7 Penetration 健全性 |
| ARPU / pricing tier | §5 | §4.1 Unit Economics |
| Cohort × segment forecast | §6 | §4.1 NRR / Cohort |
| Sensitivity (TAM ±20% etc.) | §6.4 | §1.13 Sensitivity |
| 業態別 sizing パターン | §8 | §3 セクター閾値 |
| Anti-pattern 検出 | §9 | §7 落とし穴 |

### 0.3 用語の方針

- 「OS」は使わない。「土台」「基盤」「運営体系」「アプローチ」と書く (memory note 準拠)。
- 時系列の数値データはすべて表形式で揃える。
- 出典は `[出典: <Title>](<URL>)` を文末に付す。
- 通貨単位は文脈で明記 (¥、$、€)。為替前提は §9.5 参照。
- 数式は LaTeX 風 (`$...$`, `$$...$$`) で完全展開する。

### 0.4 章構成

1. TAM / SAM / SOM の正しい定義
2. 算出手法 3+1 法 (Top-down / Bottom-up / Value-based / Triangulation)
3. Penetration Rate Modeling (Logistic / Bass / Geographic / Vertical / Network Effects)
4. データソース (グローバル / 日本 / セクター固有)
5. ARPU / ASP / 客単価の決定方法
6. Forecast Construction (財務モデル化)
7. Sanity Check / 投資判断視点
8. 業態別 sizing パターン (SaaS / Marketplace / Fintech / D2C / Bio / Hardware)
9. Anti-patterns
10. 投資家プレゼン用 TAM スライド標準形
11. 数値例 (mini case 5 件)
12. ケーススタディ (a16z / Sequoia / YC / Bessemer)
13. 市場規模 DD チェックリスト
14. TAM プレゼン作成手順

---

## 1. TAM / SAM / SOM の正しい定義

### 1.1 三層の定義と関係

| 層 | 名称 | 定義 | 想定回答 |
|---|---|---|---|
| TAM | Total Addressable Market | 全世界 / 全業態で当該課題を持つ需要の総量。製品・地理・規制の制約を一切外したときの「上限」。 | 「もし全員に届いたら」 |
| SAM | Serviceable Addressable Market | 自社が技術 / 言語 / 規制 / チャネルで現実的に届く範囲。TAM の中で「自社が売れる対象」だけ。 | 「うちの製品で売れる対象」 |
| SOM | Serviceable Obtainable Market | 短期 (3-5 年) で実際に取得可能な範囲。競合・営業力・予算で制約。 | 「3-5 年で取れる分」 |

幾何的には TAM ⊃ SAM ⊃ SOM の入れ子構造。プレゼンでは同心円 (concentric circles) かピラミッド図で示す (§10.2)。

[出典: CB Insights - TAM, SAM and SOM: What do they mean & how do you calculate them?](https://www.cbinsights.com/research/report/tam-sam-som/)
[出典: Sequoia Capital - Writing a Business Plan (Market Size)](https://www.sequoiacap.com/article/writing-a-business-plan/)

### 1.2 論点別の切り方

#### 1.2.1 B2B / B2C

- B2B では **意思決定単位 (DMU, Decision-Making Unit)** で数える。
  - 例: SaaS なら「企業数 × 部署数」または「seat 数」。
  - "全社員 × ARPU" は誤り (実際の購買者単位は限定的)。
- B2C では **個人** で数える。
  - 例: コーヒー D2C なら「コーヒー飲用人口」。
  - 世帯単位 (HHs) で数えるべきものを個人で数えるのは誤り (家電など)。

#### 1.2.2 業態 (Vertical)

- 単一垂直 (vertical-specific) の場合、TAM は対象業界に限定。
  - 例: legal tech なら「全国法律事務所数」が母集団。
  - 「全企業」を母集団にすると過大評価。
- 横断 (horizontal) の場合、業界別に重み付け。

#### 1.2.3 地理 (Geography)

- TAM は一般にグローバル。SAM で地理を絞る。
- TAM をグローバルで出して SAM を国内に限るのが標準。
- 注意: グローバル TAM を出して、後段の bottom-up は国内のみ、というアンバランスは要避け。

### 1.3 TAM の典型 anti-pattern

| アンチパターン | 例 | なぜ誤りか |
|---|---|---|
| 世界 GDP を TAM と称する | 「世界 GDP $100T が TAM」 | GDP は付加価値の総和、対象市場ではない |
| 隣接市場を含む | 「広告 + マーケ + IT すべて」 | 自社製品が解決しない領域を含む |
| 顧客の総支出を TAM と称する | 「中小企業の総 IT 支出 = TAM」 | その支出のうち自社カテゴリに割ける割合は一部 |
| 1 社あたり ARPU を過大設定 | 「全社員 × $50/月」 | 実購買単位は seat 限定が多い |
| 古いデータ (>3 年) を使う | 2019 年 IDC レポート × 2026 年予測 | 市場は変動、特に IT は 2-3 年で別物 |
| 為替・インフレ未補正 | 旧 ¥/$ レートで現在比較 | 通貨換算で 20-30% ずれる |
| 重複カウント | 「メーカー TAM + 流通 TAM」両方計上 | サプライチェーン上重複 |

[出典: a16z - Sizing Markets That Don't Exist Yet](https://a16z.com/2014/02/27/16-more-startup-metrics/)

### 1.4 VC が見たい数値

| TAM レンジ | 意味 | 想定 VC スタンス |
|---|---|---|
| < $100M | Niche | "lifestyle business" 扱い、VC 対象外 |
| $100M - $1B | Small | Seed / Series A 上限、Tier 2 VC |
| $1B - $10B | Standard VC scale | Series A / B 中心、unicorn は厳しい |
| $10B - $100B | Large | Tier 1 VC ターゲット、unicorn 候補 |
| > $100B | Massive / category-defining | Sequoia / a16z が "going to be huge" と書ける水準 |

ただし TAM の "$1B / $10B / $100B" 閾値は **bottom-up で defensible** であることが前提。盛った数字は減点対象。

[出典: Sequoia - Elements of Enduring Companies](https://www.sequoiacap.com/article/elements-of-enduring-companies/)
[出典: Bessemer - State of the Cloud (annual)](https://www.bvp.com/atlas/state-of-the-cloud)

### 1.5 VC が unicorn (=>$1B exit) として成立を見る逆算

unicorn 級の retorn を期待する場合の TAM 必要規模を逆算する:

$$
\text{Required Exit Valuation} \approx \$1B
$$

$$
\text{Target ARR at exit} \approx \frac{\$1B}{\text{Revenue Multiple}}
$$

SaaS で 8-12x revenue multiple (steady state) なら ARR = $80M - $125M。

$$
\text{TAM} \times \text{Realistic Max Share (5-10\%)} \geq \text{Target ARR}
$$

$$
\therefore \text{TAM} \geq \frac{\$100M}{0.10} = \$1B \quad (\text{下限})
$$

逆に TAM が $500M しかなければ、5-10% シェアで $25-50M ARR、unicorn 化は厳しい。

### 1.6 SAM の絞り方 (チェックリスト)

- [ ] 対応言語 (例: 英語 + 日本語のみなら 80 か国 → 2 か国)
- [ ] 法規制 (例: 金融なら免許保有国のみ)
- [ ] 業界 (例: vertical SaaS なら対象業種のみ)
- [ ] 企業サイズ (SMB only なら従業員 1-50 人のみ)
- [ ] チャネル到達 (Direct sales のみなら Top 1000 まで等)
- [ ] 製品適合 (SKU が対応する範囲)

### 1.7 SOM の見積り (3 アプローチ)

#### 1.7.1 競合シェア類推

> 既存競合の市場シェアから、自社が 5 年で取り得るシェアを逆算

例: 競合 A 5%, B 3%, C 2% で計 10%。自社は 5 年で 1-3% (合理) - 5% (強気)。

#### 1.7.2 Sales capacity 制約

> 営業人員 × 平均 quota × 達成率

例: AE 20 人 × $500K quota × 80% achievement = $8M new ARR/年。5 年累積 $40M。これが SOM 上限。

#### 1.7.3 Penetration curve 起点

> 浸透率モデル (§3) で時系列に SOM 軌道を描く

例: Logistic curve で Year 5 浸透率 3% → SOM = SAM × 3%。

### 1.8 TAM の時間変動 (TAM Expansion)

TAM は静的ではない。複数の方向で拡張できる:

| 方向 | 例 |
|---|---|
| 製品ライン拡張 | Stripe: payments → invoicing → tax → capital |
| 地理拡張 | Shopify: Canada → US → global |
| 業界拡張 | Toast: 飲食 → 広く小売 |
| ユーザー層拡張 | LinkedIn: tech → 全業種 |
| 用途拡張 | Slack: tech team → enterprise-wide |

**注意**: TAM expansion を Year 5 で 10x にするのは非現実的が多い。Year 5 で 2-3x が現実的範囲 (§7.3 比較アンカー参照)。

### 1.9 三層を一括計算する例 (Vertical SaaS for 法律事務所)

| 層 | 計算 | 値 |
|---|---|---|
| TAM (全世界) | 全世界の法律事務所 ~150,000 × 平均 ARPU $5,000/年 | $750M |
| SAM (日本のみ) | 日本の法律事務所 17,000 × 平均 ARPU ¥500K/年 | ¥8.5B (~$57M) |
| SOM (5 年) | SAM × 浸透率 10% | ¥850M (~$5.7M) |

[出典: 日本弁護士連合会 - 弁護士白書](https://www.nichibenren.or.jp/library/ja/jfba_info/statistics/data/white_paper/2023/all.pdf)

### 1.10 三層図の標準形

```
        ┌────────────────────────┐
        │      TAM ($X B)        │  ← グローバル / 全規制 / 全製品ライン
        │  ┌──────────────────┐  │
        │  │   SAM ($Y B)     │  │  ← 自社対応地理 / 言語 / 規制
        │  │  ┌────────────┐  │  │
        │  │  │ SOM ($Z M) │  │  │  ← 3-5 年取得目標
        │  │  └────────────┘  │  │
        │  └──────────────────┘  │
        └────────────────────────┘
```

各層に bottom-up 内訳と出典を付すのが必須 (§10)。

---

## 2. 算出手法 (3 + 1 法)

### 2.1 Top-down 法

#### 2.1.1 概要

外部の業界レポートから出発し、対象セグメントの比率で絞り込む。

$$
\text{TAM}_{\text{top-down}} = \text{業界全体規模} \times \prod_{i} \text{セグメント比率}_i
$$

例:
$$
\text{TAM}_{SaaS} = \$200B \text{ (世界 SaaS)} \times 30\% \text{ (B2B mid-market)} \times 5\% \text{ (legal tech)} = \$3B
$$

#### 2.1.2 主要レポートソース

| レポート | カバレッジ | 特徴 | 出典 |
|---|---|---|---|
| Gartner | 技術全般 (IT spending, magic quadrant) | カテゴリ定義の業界標準 | [gartner.com](https://www.gartner.com/) |
| IDC | IT (semi, infra, software) | 細かいユニット単位の数値 | [idc.com](https://www.idc.com/) |
| Forrester | CX, marketing tech, enterprise | Wave レポートでベンダー比較 | [forrester.com](https://www.forrester.com/) |
| Statista | 横断 (consumer / industry) | 1-2 page summary 多数、無料も | [statista.com](https://www.statista.com/) |
| MarketsandMarkets | B2B niche | カテゴリは細かいが粒度バラつき | [marketsandmarkets.com](https://www.marketsandmarkets.com/) |
| Grand View Research | 横断 | 安価、グローバル断面 | [grandviewresearch.com](https://www.grandviewresearch.com/) |
| McKinsey Global Institute | マクロ (productivity, AI 影響) | 大きいテーマで信頼性高い | [mckinsey.com/mgi](https://www.mckinsey.com/mgi) |
| BCG | 業界別 strategy report | コンサル系で深い | [bcg.com](https://www.bcg.com/) |

#### 2.1.3 セグメント階層の絞り方

階層的に絞り込む際は重複に注意:

```
Total IT spend ($5T)
 └ Software ($800B)
    └ SaaS ($300B)
       └ Vertical SaaS ($60B)
          └ Vertical SaaS for SMB ($15B)
             └ Vertical SaaS for legal SMB ($1.5B)
                └ JP only ($100M)
```

各段階で「なぜこの比率か」を出典付きで根拠を残す。

#### 2.1.4 適用条件 / 強み / 弱み

- **適用条件**: カテゴリが既存で業界レポートが存在すること。
- **強み**: 短時間で defensible な数値が出る、VC が見慣れた粒度。
- **弱み**: 「自社が本当に届く範囲」を反映しないため過大評価しがち、新カテゴリでは数値が無い。
- **典型的失敗**:
  - レポート 1 本だけ引用 (層別検証なし)
  - 古いレポート (>3 年) 使用
  - セグメント比率を恣意的に決定 (出典なし)
  - 通貨換算ミス
  - 重複領域カウント (例: SaaS とクラウドインフラ両方)

#### 2.1.5 落とし穴: geography overlap

「グローバル SaaS = 各国 SaaS の単純合計」と仮定すると以下で重複する:

- 多国籍企業 (e.g. Salesforce US 売上に日本支社売上が含まれる場合)
- マーケットプレイス GMV (買い手国 vs 売り手国)

対策: レポートに従う。北米 / EMEA / APAC の 3 ブロック分割が標準。

### 2.2 Bottom-up 法 (推奨)

#### 2.2.1 概要

> ユニット数 × ARPU を積み上げる。VC が最も信頼する手法。

$$
\text{TAM}_{\text{bottom-up}} = \sum_{s \in \text{Segments}} N_s \times \text{ARPU}_s
$$

ここで $N_s$ はセグメント $s$ のユニット数、$\text{ARPU}_s$ は平均単価 (年額)。

[出典: a16z - 16 More Startup Metrics](https://a16z.com/2014/02/27/16-more-startup-metrics/)

#### 2.2.2 セグメント別積み上げ (SMB / Mid-market / Enterprise)

例: 全国法律事務所 17,000 を弁護士数で 3 階層に分け、それぞれの ARPU を設定:

| セグメント | 弁護士数 | 事務所数 | ARPU/年 | 小計 |
|---|---|---|---|---|
| Solo | 1 | 9,500 | ¥120,000 | ¥1,140M |
| SMB | 2-10 | 6,800 | ¥600,000 | ¥4,080M |
| Mid | 11-50 | 600 | ¥3,000,000 | ¥1,800M |
| Large | 51+ | 100 | ¥12,000,000 | ¥1,200M |
| **合計** | - | **17,000** | - | **¥8,220M** |

これが SAM。SOM は浸透率を掛ける (§3)。

#### 2.2.3 検証: 顧客数 × 取引頻度 × 単価

ECサイトや決済ビジネスでは 3 因子分解が有効:

$$
\text{Revenue} = \underbrace{\text{Customers}}_{\text{取得}} \times \underbrace{\text{Frequency}}_{\text{利用頻度}} \times \underbrace{\text{ASP}}_{\text{単価}}
$$

例: D2C コーヒー
$$
\text{Revenue} = 50,000 \text{ 顧客} \times 6 \text{ 回購入/年} \times ¥3,000 = ¥900M/\text{年}
$$

#### 2.2.4 三角測量での top-down 整合確認

bottom-up と top-down を独立に算出し、レンジ一致を確認:

| 手法 | 結果 | 備考 |
|---|---|---|
| Top-down (Gartner Legal Tech 25 年) | ¥7-9B | 海外比率推定 |
| Bottom-up (法律事務所 × ARPU) | ¥8.2B | §2.2.2 |
| Value-based (1 事務所あたり時間削減 × 時給) | ¥9-11B | §2.3 |

→ レンジ ¥7-11B、中央値 ¥8-9B で defensible。

#### 2.2.5 適用条件 / 強み / 弱み

- **適用条件**: 顧客の母集団とユニット ARPU が推定可能なこと。
- **強み**: 自社製品の adressability を直接反映、VC が defensible と評価する基本形。
- **弱み**: ARPU 仮定が外れると全体ずれる、segmentation 設計のセンスが要る。
- **典型的失敗**:
  - 単一 ARPU で全 segment を計算
  - 母集団に商品が刺さらない層を含めたまま
  - "全社員 × ARPU" 計算 (実際は seat 限定)
  - 公表データ (e.g. 帝国データバンクの企業数) の最新性確認漏れ

### 2.3 Value-based 法

#### 2.3.1 概要

> 顧客が解消する Pain (痛み) の金額換算 × Willingness to Pay (WTP) で算出。
> Cost displacement: 既存代替手段のコストを置換する分

$$
\text{TAM}_{\text{value}} = \sum_{s} N_s \times V_s \times \alpha_s
$$

- $V_s$: セグメント $s$ における顧客 1 ユニットあたりの value (年額)
- $\alpha_s$: WTP 比率 (典型 10-30%、value の何割を価格にできるか)

#### 2.3.2 例: Toast (POS for restaurants)

> 「1 店舗あたり年間決済手数料節約額」 × 全店舗数

| 項目 | 値 |
|---|---|
| 全米飲食店舗数 | ~660,000 |
| 1 店舗 平均年間売上 | $1.0M |
| 既存決済手数料率 | 2.6% |
| Toast 削減幅 | 0.6 ppts |
| 1 店舗節約額/年 | $6,000 |
| Total cost displacement | ~$4.0B |
| WTP 比率 (30%) | $1.2B (Toast 関連 TAM) |

[出典: Toast S-1, 2021](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001650164)

#### 2.3.3 Value chain 分解

業務プロセスを step に分解し、step ごとの cost displacement を算出:

例: 与信業務 (Fintech)

| Step | 既存コスト/件 | 自社削減幅 | 比率 |
|---|---|---|---|
| 申込書類処理 | ¥2,000 | ¥1,500 | 75% |
| 審査ロジック | ¥3,000 | ¥2,000 | 67% |
| 承認/与信判定 | ¥1,500 | ¥500 | 33% |
| **合計** | **¥6,500** | **¥4,000** | 62% |

× 年間与信件数 100M 件 = ¥400B cost displacement (理論値)。
WTP 20% → TAM ¥80B。

#### 2.3.4 WTP の決め方

§5.2 で詳述するが、以下が代表的:

- Van Westendorp PSM (Price Sensitivity Meter) 4 質問サーベイ
- Conjoint analysis (機能 × 価格の組合せ評価)
- Competitive pricing benchmark (代替の 50-150% レンジ)
- ROI 計算 (annual savings の 20-40%)

#### 2.3.5 適用条件 / 強み / 弱み

- **適用条件**: 顧客課題が定量可能 (時間 / コスト / 機会損失) であること。
- **強み**: 新カテゴリ (既存市場無し) で唯一使える、creates new TAM の主張が可能。
- **弱み**: WTP 推定の不確実性大、実証が薄いと "wishful thinking" 扱い。
- **典型的失敗**:
  - Cost displacement = TAM と置く (WTP 比率を無視)
  - 顧客が認識していない value を計上 (実購買は付かない)
  - α (WTP 比率) を 50%+ に置く (現実 10-30%)

### 2.4 Triangulation (3 手法でレンジ確認)

#### 2.4.1 手順

1. Top-down で算出 → $T$
2. Bottom-up で算出 → $B$
3. Value-based で算出 → $V$
4. レンジ $[\min(T,B,V), \max(T,B,V)]$ で示す
5. 中央値 (median) を base case とする

#### 2.4.2 一致しない場合の解釈

| パターン | 解釈 |
|---|---|
| $T \gg B$ | レポート定義が広すぎる。SAM 絞り込み不足の可能性。 |
| $B \gg T$ | 単価仮定が高すぎる。WTP 過大評価。 |
| $V \gg T, B$ | 既存市場が未成熟、新カテゴリの可能性。創造的破壊あり得るが要検証。 |
| $T \approx B \approx V$ | defensible、自信を持って提示可能。 |

#### 2.4.3 信頼性での重み付け

3 手法を信頼性で加重平均する:

$$
\text{TAM}_{\text{final}} = w_T T + w_B B + w_V V,\quad \sum w_i = 1
$$

典型重み:

| 状況 | $w_T$ | $w_B$ | $w_V$ |
|---|---|---|---|
| 既存カテゴリ | 0.3 | 0.5 | 0.2 |
| 新カテゴリ | 0.1 | 0.4 | 0.5 |
| Vertical SaaS | 0.2 | 0.6 | 0.2 |
| Marketplace | 0.3 | 0.4 | 0.3 |

### 2.5 三手法の比較表

| 手法 | データ源 | 精度 | 工数 | VC 信頼度 |
|---|---|---|---|---|
| Top-down | 業界レポート | 中 | 低 | 中 (補助のみ) |
| Bottom-up | 母集団 + ARPU | 高 | 中 | 高 (中心) |
| Value-based | 顧客課題 + WTP | 中-低 | 高 | 中 (新市場で必須) |
| Triangulation | 3 手法統合 | 最高 | 高 | 最高 |

---

## 3. Penetration Rate Modeling

浸透率 $p(t) \in [0, 1]$ は SAM 内で何割の顧客が自社製品を採用しているかを示す関数。財務モデルの長期 forecast はこの曲線で決まる。

### 3.1 Logistic Curve (S 字曲線)

#### 3.1.1 数式

$$
p(t) = \frac{K}{1 + e^{-r(t - t_0)}}
$$

- $K$: saturation level (上限浸透率、典型 0 < K ≤ 1)
- $r$: growth rate (内的増加率、年率)
- $t_0$: inflection point (浸透率が $K/2$ に達する時刻)

導関数 (年次浸透増加率):

$$
\frac{dp}{dt} = r \cdot p(t) \cdot \left(1 - \frac{p(t)}{K}\right)
$$

ピーク採用速度は $t = t_0$、$p = K/2$ で生じる。

#### 3.1.2 パラメータ推定

過去 3+ 年の実績 $\{(t_i, p_i)\}$ がある場合、線形変換で推定:

$$
\ln\left(\frac{p}{K - p}\right) = r(t - t_0)
$$

→ $K$ を仮定して左辺を計算、$t$ で線形回帰し $r$ と $t_0$ を得る。

#### 3.1.3 業界別 $K$ (saturation) の典型値

| 領域 | $K$ レンジ | 根拠 |
|---|---|---|
| B2B SaaS (horizontal) | 0.30 - 0.50 | CRM, HR でも 50% 超は稀 |
| B2B SaaS (vertical) | 0.40 - 0.60 | 業界特化で深く浸透 |
| Consumer subscription | 0.05 - 0.15 | Netflix US 60% は例外 |
| Consumer mobile app | 0.10 - 0.30 | super app は 50%+ |
| Hardware (smartphones) | 0.70 - 0.90 | 必需品化 |
| Marketplace (買い手) | 0.10 - 0.40 | カテゴリ依存 |
| Marketplace (売り手) | 0.30 - 0.70 | 供給側は集中しやすい |

[出典: Bessemer - State of the Cloud Report (Penetration in Cloud)](https://www.bvp.com/atlas/state-of-the-cloud)

#### 3.1.4 Excel 実装

セル設計:

| セル | 内容 | 数式 |
|---|---|---|
| B1 | K (saturation) | 0.40 |
| B2 | r (growth rate) | 0.6 |
| B3 | t0 (inflection year) | 4 |
| A6:A20 | year (1, 2, ..., 15) | - |
| B6 | p(t) | `=$B$1/(1+EXP(-$B$2*(A6-$B$3)))` |

これを下方向にコピーすれば S 字曲線完成。

#### 3.1.5 適用条件 / 強み / 弱み

- **適用条件**: 単一カテゴリ、需要側に明確な飽和点があるとき。
- **強み**: シンプル、パラメータ 3 個で defensible、Excel 実装容易。
- **弱み**: 競合反応や product launch の不連続を表現できない。
- **典型的失敗**: $K = 1.0$ (100% 浸透) 設定、$r$ を実績無しに楽観設定。

### 3.2 Bass Diffusion Model

#### 3.2.1 数式

Frank Bass (1969) の新製品浸透モデル。Innovation (外部影響) と Imitation (口コミ) を分離:

$$
\frac{dN(t)}{dt} = \left( p + q \cdot \frac{N(t)}{m} \right) \left( m - N(t) \right)
$$

積分形 (累積採用者数):

$$
N(t) = m \cdot \frac{1 - e^{-(p+q)t}}{1 + \frac{q}{p} e^{-(p+q)t}}
$$

- $p$: innovation coefficient (外部広告等、典型 0.01 - 0.05)
- $q$: imitation coefficient (口コミ、典型 0.30 - 0.50)
- $m$: ultimate market potential (究極採用者総数)
- $N(t)$: 時刻 $t$ までの累積採用者数

[出典: Bass, F. M. (1969). A new product growth for model consumer durables. Management Science, 15(5), 215-227.](https://www.bassbasement.org/F/N/FMB/Pubs/Bass%201969%20A%20New%20Prod%20Growth%20for%20Model%20Consumer%20Durables.pdf)

#### 3.2.2 業界別パラメータ (Sultan et al meta-analysis)

| 製品カテゴリ | $p$ | $q$ | 備考 |
|---|---|---|---|
| 平均 (Bass 1969) | 0.030 | 0.380 | 数十製品のメタ |
| 家電耐久財 | 0.025 | 0.420 | 冷蔵庫、TV 等 |
| 産業財 | 0.014 | 0.300 | やや遅い |
| ICT 製品 | 0.040 | 0.450 | 普及速い |
| 医薬品 | 0.005 | 0.400 | innovation 低、口コミ重要 |
| Web2 SaaS (推定) | 0.030 | 0.500 | viral loop あり |

[出典: Sultan, F., Farley, J. U., & Lehmann, D. R. (1990). A meta-analysis of applications of diffusion models. Journal of Marketing Research, 27(1), 70-77.](https://journals.sagepub.com/doi/10.1177/002224379002700107)

#### 3.2.3 適用条件 / 強み / 弱み

- **適用条件**: 新製品、過去 1-2 年の実績で $p, q$ がフィットできる。
- **強み**: viral loop / network effect を直接モデリング、teaser launch 計画にも使える。
- **弱み**: $m$ (ultimate market) を別途決める必要、推定が難しい。
- **典型的失敗**: $p = 0$ (initial seed なし) 設定、$m$ を TAM と等値 (実際 SOM 程度)。

#### 3.2.4 ピーク採用時刻

$$
t^* = \frac{1}{p+q} \ln\left(\frac{q}{p}\right)
$$

例: $p=0.03, q=0.4$ なら $t^* = \frac{1}{0.43}\ln(13.3) \approx 6.0$ 年。

#### 3.2.5 Logistic vs Bass の使い分け

| 状況 | 推奨モデル |
|---|---|
| 既に普及中、単純な S 字 | Logistic |
| 新製品、口コミ駆動 | Bass |
| 1 製品 1 カテゴリ | どちらでも |
| 複数製品 cannibalization | Multi-generation Bass (Norton-Bass 1987) |
| 短期 (3 年) forecast | Logistic |
| 長期 (10 年+) forecast | Bass |

### 3.3 Geographic Rollout

地理別に staggered launch する場合、各地域の浸透曲線を別個に設定し合算する:

$$
N_{\text{global}}(t) = \sum_{c \in \text{Countries}} N_c(t - \tau_c) \cdot \mathbb{1}[t \geq \tau_c]
$$

- $\tau_c$: 国 $c$ の launch year (基準国を 0 とする offset)
- $\mathbb{1}[\cdot]$: indicator (launch 前は 0)

例 (SaaS):

| 国 | launch year | $m_c$ | $p_c$ | $q_c$ |
|---|---|---|---|---|
| US | 0 | 100,000 | 0.03 | 0.40 |
| UK | +2 | 30,000 | 0.04 | 0.45 |
| JP | +3 | 50,000 | 0.02 | 0.35 |
| DE | +3 | 40,000 | 0.03 | 0.40 |

地理拡大の lessons:

- 後続国は先行国を見て採用が早まる傾向 ($p$ 上振れ)
- 言語 / 文化障壁が高い国は $p$ 下振れ (日本など)
- B2B では現地法人有無で $q$ が大きく変わる

### 3.4 Vertical Expansion

Single vertical ("beachhead") から横展開する場合のモデリング。Geoffrey Moore "Crossing the Chasm" の bowling pin strategy が理論基盤。

[出典: Geoffrey Moore - Crossing the Chasm](https://www.harpercollins.com/products/crossing-the-chasm-3rd-edition-geoffrey-a-moore)

#### 3.4.1 Beachhead 戦略

1. **第 1 vertical**: 早期顧客のうち最も pain が深いセグメント (例: Toast → restaurant)
2. **第 2-3 vertical**: 第 1 と顧客特性が近い隣接領域 (例: bar / cafe)
3. **第 4+ vertical**: 製品の core が抽象化され横展開可能 (例: retail へ)

#### 3.4.2 横展開の typical timing

| Stage | Year | Vertical 数 | 主な動機 |
|---|---|---|---|
| Beachhead | 0-2 | 1 | PMF 確立 |
| Adjacent | 2-4 | 2-3 | revenue diversification |
| Horizontal | 4-7 | 5-10 | TAM 拡張 |
| Platform | 7+ | 10+ | M&A 含む |

#### 3.4.3 多 vertical Bass

各 vertical で別々の Bass パラメータを置き合算する形になるが、vertical 間で migration がある場合は cross-vertical interaction term を入れる:

$$
\frac{dN_v(t)}{dt} = \left( p_v + q_v \frac{N_v}{m_v} + \sum_{u \neq v} q_{uv} \frac{N_u}{m_u} \right)(m_v - N_v)
$$

### 3.5 Network Effects 加速

Network effect が効く場合、value が利用者数の関数として非線形に増加し、浸透率と revenue の関係が乖離する。

#### 3.5.1 Metcalfe's Law

ネットワークの value はノード数の二乗に比例:

$$
V_{\text{Metcalfe}} \propto n^2
$$

例: 10x の users で 100x の value。Telecom, social network, marketplace 適用。

#### 3.5.2 Reed's Law

サブグループ形成可能なネットワーク (Slack channels, Facebook groups) では value がノード数の指数関数:

$$
V_{\text{Reed}} \propto 2^n
$$

実際は飽和項を入れた現実形:

$$
V_{\text{Reed-realistic}} \propto 2^n - n - 1
$$

#### 3.5.3 Sarnoff's Law (broadcast)

放送型ネットワーク (TV, ニュースサイト) では value が線形:

$$
V_{\text{Sarnoff}} \propto n
$$

#### 3.5.4 浸透率 × value の非線形関係

ARPU が user 数依存する場合、財務モデルでは revenue は浸透率の二乗オーダーで増える:

$$
\text{Revenue}(t) \propto N(t) \cdot \text{ARPU}(N(t))
$$

例 (Metcalfe 仮定):
$$
\text{ARPU}(N) = \text{ARPU}_{\text{base}} \cdot \left(\frac{N}{N_{\text{ref}}}\right)^{0.5}
$$
→ revenue は $N^{1.5}$ オーダー。

#### 3.5.5 Network effect 強度の判別

| タイプ | 例 | Revenue scaling |
|---|---|---|
| 強 (direct) | 通信、マーケットプレイス | $\sim n^2$ |
| 中 (indirect) | OS + apps | $\sim n^{1.5}$ |
| 弱 (data) | 広告 ML、検索 | $\sim n^{1.2}$ |
| 無 (linear) | 通常 SaaS | $\sim n$ |

[出典: NfX - The Network Effects Manual](https://www.nfx.com/post/network-effects-manual)

### 3.6 Penetration ceiling (飽和上限) の業界別ガイド

| カテゴリ | 浸透率 ceiling (%) | 到達期間 |
|---|---|---|
| B2B SaaS (must-have) | 30-50% | 7-10 年 |
| B2B SaaS (nice-to-have) | 5-15% | 5-10 年 |
| Consumer subscription | 5-15% | 5-10 年 |
| Mobile messaging (national) | 60-90% | 5-7 年 |
| E-commerce (国別) | 15-25% | 10+ 年 |
| 専門 vertical SaaS | 20-40% | 7-10 年 |
| Hardware (consumer) | 50-90% | 5-15 年 |

このレンジを超える forecast は要根拠。

### 3.7 浸透率 milestone のチェック

| milestone | 達成までの典型期間 |
|---|---|
| 1% (early adopters) | 1-3 年 |
| 10% (chasm 直前) | 3-7 年 |
| 25% (early majority 入り) | 5-10 年 |
| 50% (mainstream) | 7-15 年 (達するなら) |

これを超えるスピードを forecast する場合は同業比較で根拠提示。

### 3.8 Competitive density による ceiling 補正

競合存在下では理論上限から市場分割を考慮:

$$
p_{\text{your}}(\infty) = K \cdot s_{\text{your}}
$$

- $K$: カテゴリ全体の浸透 ceiling
- $s_{\text{your}}$: 自社シェア (long-run)

典型 $s$:

| 競合構造 | 自社シェア $s$ |
|---|---|
| Winner-take-all (e.g. SNS) | 0.6-0.9 (winner) / 0.05-0.15 (others) |
| Oligopoly (3-5 社) | 0.15-0.35 |
| Fragmented | 0.02-0.10 |

---

## 4. データソース (徹底列挙)

### 4.1 グローバル

#### 4.1.1 業界レポート (有料中心)

| ソース | カテゴリ | 価格帯 | URL |
|---|---|---|---|
| Gartner | 技術全般 (IT spending, magic quadrant) | $$$$ | [gartner.com](https://www.gartner.com/) |
| IDC | IT (semi, infra, software) | $$$$ | [idc.com](https://www.idc.com/) |
| Forrester | CX/marketing tech, enterprise | $$$$ | [forrester.com](https://www.forrester.com/) |
| Statista | 横断 | $-$$ | [statista.com](https://www.statista.com/) |
| MarketsandMarkets | B2B niche | $$$ | [marketsandmarkets.com](https://www.marketsandmarkets.com/) |
| Grand View Research | 横断 | $$ | [grandviewresearch.com](https://www.grandviewresearch.com/) |
| Mordor Intelligence | 業界別 | $$ | [mordorintelligence.com](https://www.mordorintelligence.com/) |
| Frost & Sullivan | 産業 / B2B | $$$ | [frost.com](https://www.frost.com/) |

#### 4.1.2 Consulting / Research (一部無料)

| ソース | カテゴリ | URL |
|---|---|---|
| McKinsey Global Institute | マクロ | [mckinsey.com/mgi](https://www.mckinsey.com/mgi) |
| BCG Henderson Institute | strategy | [bcg.com](https://www.bcg.com/) |
| Bain | PE / strategy | [bain.com](https://www.bain.com/) |
| Deloitte Insights | 産業横断 | [deloitte.com/insights](https://www2.deloitte.com/us/en/insights.html) |
| PwC | 産業 / 規制 | [pwc.com/research](https://www.pwc.com/) |
| KPMG | 産業 / DD | [kpmg.com](https://kpmg.com/) |
| EY | 産業 / トレンド | [ey.com](https://www.ey.com/) |

#### 4.1.3 マクロ (無料)

| ソース | カテゴリ | URL |
|---|---|---|
| World Bank Open Data | 国別マクロ、GDP、人口 | [data.worldbank.org](https://data.worldbank.org/) |
| IMF Data | 通貨、為替、GDP | [imf.org/data](https://www.imf.org/en/Data) |
| OECD Statistics | 先進国、ICT、教育 | [stats.oecd.org](https://stats.oecd.org/) |
| UN Comtrade | 貿易データ | [comtrade.un.org](https://comtrade.un.org/) |
| US Census Bureau | 米国人口、business | [census.gov](https://www.census.gov/) |
| Eurostat | EU 統計 | [ec.europa.eu/eurostat](https://ec.europa.eu/eurostat) |

#### 4.1.4 Private market (有料)

| ソース | カテゴリ | URL |
|---|---|---|
| Crunchbase | startup funding | [crunchbase.com](https://www.crunchbase.com/) |
| PitchBook | private equity / VC | [pitchbook.com](https://pitchbook.com/) |
| CB Insights | tech market intel | [cbinsights.com](https://www.cbinsights.com/) |
| Tracxn | startup database | [tracxn.com](https://tracxn.com/) |
| Dealroom | EU startup data | [dealroom.co](https://dealroom.co/) |

### 4.2 日本

#### 4.2.1 民間調査会社

| ソース | 強み | URL |
|---|---|---|
| 矢野経済研究所 | 業界別、消費財 〜 産業財 | [yano.co.jp](https://www.yano.co.jp/) |
| 富士経済グループ | 化学、エネルギー、IT | [fuji-keizai.co.jp](https://www.fuji-keizai.co.jp/) |
| 富士キメラ総研 | エレクトロニクス、医療 | [fcr.co.jp](https://www.fcr.co.jp/) |
| MM 総研 | 通信、ICT | [m2ri.jp](https://www.m2ri.jp/) |
| ICT 総研 | クラウド、SaaS、通信 | [ictr.co.jp](https://ictr.co.jp/) |
| 帝国データバンク | 企業情報、倒産 | [tdb.co.jp](https://www.tdb.co.jp/) |
| 東京商工リサーチ (TSR) | 企業情報、与信 | [tsr-net.co.jp](https://www.tsr-net.co.jp/) |
| 日経 BP | 業界誌、白書 | [nikkeibp.co.jp](https://www.nikkeibp.co.jp/) |

#### 4.2.2 政府統計 (無料)

| ソース | カテゴリ | URL |
|---|---|---|
| 経済産業省 (経産省) | 商業動態、特定サービス、IT | [meti.go.jp/statistics](https://www.meti.go.jp/statistics/) |
| 総務省統計局 | 国勢調査、家計調査、産業連関表 | [stat.go.jp](https://www.stat.go.jp/) |
| 内閣府 | GDP、経済財政白書、国民経済計算 | [esri.cao.go.jp](https://www.esri.cao.go.jp/) |
| 日本銀行 | 金融経済統計、消費活動指数 | [boj.or.jp/statistics](https://www.boj.or.jp/statistics/index.htm) |
| 財務省 | 法人企業統計、貿易統計 | [mof.go.jp/policy/financial_system](https://www.mof.go.jp/policy/financial_system/) |
| 厚生労働省 | 雇用、医療、介護 | [mhlw.go.jp/toukei](https://www.mhlw.go.jp/toukei/) |
| 国土交通省 | 不動産、交通、建設 | [mlit.go.jp/statistics](https://www.mlit.go.jp/statistics/) |
| 農林水産省 | 農林水産業 | [maff.go.jp/j/tokei](https://www.maff.go.jp/j/tokei/) |
| 中小企業庁 | 中小企業白書 | [chusho.meti.go.jp](https://www.chusho.meti.go.jp/) |
| e-Stat | 政府統計ポータル | [e-stat.go.jp](https://www.e-stat.go.jp/) |
| RESAS | 地域経済分析 | [resas.go.jp](https://resas.go.jp/) |

#### 4.2.3 海外進出 / 国際比較

| ソース | カテゴリ | URL |
|---|---|---|
| JETRO (日本貿易振興機構) | 海外市場、貿易統計、国別レポート | [jetro.go.jp](https://www.jetro.go.jp/) |
| 国際協力銀行 (JBIC) | 海外投資環境 | [jbic.go.jp](https://www.jbic.go.jp/) |
| ジェトロ・アジア経済研究所 | 開発経済 | [ide.go.jp](https://www.ide.go.jp/) |

#### 4.2.4 スタートアップ系

| ソース | カテゴリ | URL |
|---|---|---|
| INITIAL | スタートアップ調達情報 | [initial.inc](https://initial.inc/) |
| STARTUP DB | 国内スタートアップ DB | [startup-db.com](https://startup-db.com/) |
| ENTRPRD | プレシード〜シード | [entreprd.com](https://www.entreprd.com/) |
| Forbes JAPAN STARTUP | スタートアップ記事 | [forbesjapan.com](https://forbesjapan.com/) |

#### 4.2.5 業界団体・白書

| 団体 | 領域 | URL |
|---|---|---|
| 一般社団法人ソフトウェア協会 (SAJ) | ソフトウェア | [saj.or.jp](https://www.saj.or.jp/) |
| 電子情報技術産業協会 (JEITA) | エレクトロニクス、IT | [jeita.or.jp](https://www.jeita.or.jp/) |
| ベンチャーエンタープライズセンター (VEC) | VC 投資動向 | [vec.or.jp](https://www.vec.or.jp/) |
| 日本ベンチャーキャピタル協会 (JVCA) | VC | [jvca.jp](https://jvca.jp/) |
| 一般社団法人 Fintech 協会 | フィンテック | [fintechjapan.org](https://fintechjapan.org/) |
| 日本セキュリティ協会 (JASA) | セキュリティ | [jasa.jp](https://www.jasa.jp/) |
| 日本通信販売協会 (JADMA) | 通販、EC | [jadma.or.jp](https://www.jadma.or.jp/) |

主要白書:

- 中小企業白書 (中小企業庁、年次)
- 通商白書 (経産省)
- 情報通信白書 (総務省)
- 厚生労働白書
- 経済財政白書 (内閣府)
- ものづくり白書 (経産省)

### 4.3 セクター固有

#### 4.3.1 SaaS / Cloud

| ソース | カテゴリ | URL |
|---|---|---|
| Bessemer State of the Cloud | SaaS 動向 (annual) | [bvp.com/atlas/state-of-the-cloud](https://www.bvp.com/atlas/state-of-the-cloud) |
| OpenView SaaS Benchmarks | SaaS metrics | [openviewpartners.com](https://openviewpartners.com/) |
| KeyBanc SaaS Survey | SaaS 経営指標 | [key.com](https://www.key.com/) |
| Capterra | software reviews / pricing | [capterra.com](https://www.capterra.com/) |
| G2 | software reviews | [g2.com](https://www.g2.com/) |
| ICONIQ Growth | growth metrics | [iconiqcapital.com](https://www.iconiqcapital.com/) |

#### 4.3.2 Fintech

| ソース | カテゴリ | URL |
|---|---|---|
| CB Insights State of Fintech | 動向 | [cbinsights.com](https://www.cbinsights.com/) |
| Statista Digital Markets - Fintech | 横断 | [statista.com](https://www.statista.com/outlook/dmo/fintech) |
| Coingecko / CoinMarketCap | crypto | [coingecko.com](https://www.coingecko.com/) |
| Chainalysis | crypto on-chain | [chainalysis.com](https://www.chainalysis.com/) |
| BIS | 中央銀行統計 | [bis.org](https://www.bis.org/) |
| Bank of Japan | 国内決済 | [boj.or.jp](https://www.boj.or.jp/) |

#### 4.3.3 Bio / Pharma

| ソース | カテゴリ | URL |
|---|---|---|
| EvaluatePharma | 医薬市場 | [evaluate.com](https://www.evaluate.com/) |
| Citeline (Pharma Intelligence) | 臨床試験、規制 | [pharmaintelligence.informa.com](https://pharmaintelligence.informa.com/) |
| IQVIA | リアルワールドデータ | [iqvia.com](https://www.iqvia.com/) |
| GlobalData Pharma | 製品パイプライン | [globaldata.com](https://www.globaldata.com/) |
| FDA Drug Approvals | 米国承認 | [fda.gov](https://www.fda.gov/) |
| PMDA | 日本医薬品 | [pmda.go.jp](https://www.pmda.go.jp/) |

#### 4.3.4 Real Estate / PropTech

| ソース | カテゴリ | URL |
|---|---|---|
| CBRE | 商業不動産 | [cbre.com](https://www.cbre.com/) |
| JLL | 商業不動産 | [jll.com](https://www.jll.com/) |
| Colliers | 商業不動産 | [colliers.com](https://www.colliers.com/) |
| Real Capital Analytics (RCA) | 取引データ | [rcanalytics.com](https://www.rcanalytics.com/) |
| Costar | 米国不動産 | [costar.com](https://www.costar.com/) |
| 不動産研究所 (国内) | 国内不動産 | [reinet.or.jp](https://www.reinet.or.jp/) |

#### 4.3.5 Auto / Mobility

| ソース | カテゴリ | URL |
|---|---|---|
| S&P Global Mobility (旧 IHS Markit) | 自動車生産・販売 | [spglobal.com/mobility](https://www.spglobal.com/mobility/) |
| LMC Automotive | 自動車予測 | [lmc-auto.com](https://www.lmc-auto.com/) |
| 自動車工業会 (JAMA) | 国内自動車 | [jama.or.jp](https://www.jama.or.jp/) |
| EV-Volumes | 電気自動車 | [ev-volumes.com](https://www.ev-volumes.com/) |

#### 4.3.6 Energy / Climate

| ソース | カテゴリ | URL |
|---|---|---|
| BloombergNEF | エネルギー、気候 | [about.bnef.com](https://about.bnef.com/) |
| Wood Mackenzie | エネルギー | [woodmac.com](https://www.woodmac.com/) |
| IEA (国際エネルギー機関) | エネルギー統計 | [iea.org](https://www.iea.org/) |
| EIA (米国) | 米国エネルギー | [eia.gov](https://www.eia.gov/) |
| 資源エネルギー庁 (国内) | 国内エネルギー | [enecho.meti.go.jp](https://www.enecho.meti.go.jp/) |

#### 4.3.7 Retail / E-commerce

| ソース | カテゴリ | URL |
|---|---|---|
| eMarketer (Insider Intelligence) | 米国 / グローバル EC | [insiderintelligence.com](https://www.insiderintelligence.com/) |
| Euromonitor | 消費財 | [euromonitor.com](https://www.euromonitor.com/) |
| Nielsen | 消費者購買 | [nielsen.com](https://www.nielsen.com/) |
| 経産省 商取引動態統計 (国内 EC) | 国内 EC 規模 | [meti.go.jp](https://www.meti.go.jp/policy/it_policy/statistics/outlook/) |
| 経産省 電子商取引市場調査 | 年次 EC レポート | [meti.go.jp](https://www.meti.go.jp/) |

#### 4.3.8 HR / Workforce

| ソース | カテゴリ | URL |
|---|---|---|
| LinkedIn Economic Graph | 労働市場 | [economicgraph.linkedin.com](https://economicgraph.linkedin.com/) |
| BLS (米国労働統計) | 米国労働 | [bls.gov](https://www.bls.gov/) |
| 厚労省 雇用動向調査 | 国内雇用 | [mhlw.go.jp](https://www.mhlw.go.jp/) |
| リクルートワークス研究所 | 国内労働 | [works-i.com](https://www.works-i.com/) |

### 4.4 データソース選定の優先順位

1. **一次データ (政府統計、企業 IR)** - 最優先、無料・高信頼
2. **業界団体データ** - 中信頼、対象業界の文脈が正確
3. **コンサルティング系 (McKinsey/BCG/Deloitte)** - フレームと数値整合性が高い
4. **調査会社 (Gartner/IDC/矢野経済)** - 標準粒度、有料前提
5. **3rd party (Statista, Grand View)** - サマリ用、深度は浅い
6. **メディア記事** - 補助、必ず一次出典確認

---

## 5. ARPU / ASP / 客単価の決定方法

### 5.1 用語整理

| 用語 | 定義 | 単位 |
|---|---|---|
| ARPU | Average Revenue Per User | 通貨/user/期間 |
| ARPA | Average Revenue Per Account | 通貨/account/期間 (B2B) |
| ASP | Average Selling Price | 通貨/sale (1 回限り) |
| AOV | Average Order Value | 通貨/order (EC) |
| LTV | Customer Lifetime Value | 通貨 (累積) |
| TCV | Total Contract Value | 通貨 (契約全期間) |
| ACV | Annual Contract Value | 通貨/年 (B2B SaaS) |

[出典: ChartMogul - SaaS Metrics Glossary](https://chartmogul.com/saas-metrics/)

### 5.2 Pricing tier 設計

代表的 3-tier:

| Tier | 想定顧客 | 特徴 | 比率 (B2B SaaS 典型) |
|---|---|---|---|
| Free / Starter | Individual / SMB | 機能制限 / seat 数限 | 60-80% |
| Pro / Team | Mid-market | 主機能 + integration | 15-30% |
| Enterprise | 大企業 | SSO, audit log, SLA | 5-15% |

ARPU は加重平均で計算:

$$
\text{ARPU} = \frac{\sum_t N_t \cdot p_t}{\sum_t N_t}
$$

### 5.3 WTP 推定: Van Westendorp PSM

#### 5.3.1 4 質問

1. この製品が **高すぎて買わない** 価格はいくら?
2. **高いが買う** 価格はいくら?
3. **安くて魅力的** な価格はいくら?
4. **安すぎて品質を疑う** 価格はいくら?

#### 5.3.2 4 線の交点で価格帯を推定

| 交点 | 名称 | 解釈 |
|---|---|---|
| Q1 ∩ Q3 | Point of Marginal Cheapness (PMC) | 下限 |
| Q2 ∩ Q4 | Point of Marginal Expensiveness (PME) | 上限 |
| Q1 ∩ Q4 | Optimal Price Point (OPP) | 最適価格 |
| Q2 ∩ Q3 | Indifference Price Point (IPP) | 中立点 |

[出典: Van Westendorp PSM](https://en.wikipedia.org/wiki/Van_Westendorp%27s_Price_Sensitivity_Meter)

### 5.4 WTP 推定: Conjoint Analysis

機能と価格の組合せを評価させ、各属性の効用 (utility) を推定。

| 属性 | レベル例 |
|---|---|
| 機能 | A / A+B / A+B+C |
| 価格 | $10 / $20 / $50 / $100 |
| サポート | Email / 24x7 |

→ ベイズ MNL モデルで属性別効用と価格弾性を推定。Sawtooth Software, Qualtrics CoreXM が標準ツール。

### 5.5 Competitive pricing benchmark

| 戦略 | 価格設定 | 適用 |
|---|---|---|
| Penetration pricing | 競合の 50-70% | シェア優先 (新参入) |
| Price parity | 競合と同等 | 機能差別化重視 |
| Premium pricing | 競合の 130-200% | ブランド / 機能優位 |
| Value-based | 顧客 ROI の 20-30% | 新カテゴリ |

### 5.6 Segment 別 ARPU の重み付け

セグメント別 ARPU を顧客数で加重平均:

$$
\text{ARPU}_{\text{blend}} = \frac{\sum_s N_s \cdot \text{ARPU}_s}{\sum_s N_s}
$$

例:

| Segment | $N$ | ARPU | $N \cdot$ARPU |
|---|---|---|---|
| SMB | 800 | $200/月 | $160K |
| Mid | 150 | $1,500/月 | $225K |
| Ent | 50 | $8,000/月 | $400K |
| **計** | **1,000** | - | **$785K** |

ARPU_blend = $785/月 (顧客 1 社あたり)。

### 5.7 Price elasticity

価格弾性 $\epsilon$:

$$
\epsilon = \frac{\Delta Q / Q}{\Delta P / P}
$$

典型値:

| 製品タイプ | $|\epsilon|$ |
|---|---|
| Necessity (食品、ガソリン) | 0.1 - 0.5 |
| 一般 SaaS | 0.5 - 1.5 |
| Discretionary (luxury) | 1.5 - 3.0 |
| Substitutable (commodity) | 2.0 - 5.0 |

価格弾性を考慮した revenue 最適化:

$$
P^* = \frac{|\epsilon|}{|\epsilon| - 1} \cdot MC
$$

ここで $MC$ は marginal cost。SaaS では $MC \approx 0$ なので価格は WTP で決まる。

### 5.8 ARPU 時間変動

長期 forecast では ARPU が変動:

| 要因 | 方向 | 典型 |
|---|---|---|
| Land-and-expand | ↑ | NRR 110-130% |
| Mix shift (Ent 比率 ↑) | ↑ | 年 5-10% UP |
| Cohort 旧化 (旧プラン残存) | ↓ | 年 2-5% DOWN |
| 競合価格圧力 | ↓ | 年 3-7% DOWN |
| インフレ調整 | ↑ | 年 2-3% UP (US) |

→ Net effect は B2B SaaS で年 5-8% UP が典型。

---

## 6. Forecast Construction (財務モデル化)

### 6.1 単純式 (single-segment)

最小モデル:

$$
\text{Revenue}(t) = \text{TAM}(t) \times \text{SAM\%}(t) \times p(t) \times \text{ARPU}(t)
$$

例: SaaS 5 年予測

| Year | TAM (¥B) | SAM% | $p$ | ARPU (¥/年) | 顧客数 | Revenue (¥M) |
|---|---|---|---|---|---|---|
| 1 | 100 | 20% | 0.5% | 600,000 | 167 | 100 |
| 2 | 105 | 22% | 1.5% | 620,000 | 559 | 347 |
| 3 | 110 | 24% | 4.0% | 640,000 | 1,320 | 845 |
| 4 | 115 | 26% | 8.0% | 660,000 | 2,392 | 1,579 |
| 5 | 120 | 28% | 14.0% | 680,000 | 3,763 | 2,559 |

(顧客数 = TAM × SAM% × p / ARPU、Revenue = 顧客数 × ARPU)

### 6.2 拡張: Cohort 化

各年取得 cohort の retention curve を分けて積み上げる:

$$
\text{Revenue}(t) = \sum_{c \leq t} A_c \cdot R(t - c) \cdot \text{ARPU}_c \cdot (1 + g)^{t-c}
$$

- $A_c$: cohort $c$ の取得顧客数
- $R(\tau)$: $\tau$ 期経過後の retention 率 ($R(0) = 1$)
- $\text{ARPU}_c$: cohort $c$ の取得時 ARPU
- $g$: cohort 内 NRR (net revenue retention) 上振れ率

例:

| Cohort | 取得時 (Yr) | 取得数 $A_c$ | $R(1)$ | $R(2)$ | $R(3)$ |
|---|---|---|---|---|---|
| 2024 | 0 | 100 | 0.85 | 0.75 | 0.70 |
| 2025 | 1 | 200 | 0.85 | 0.75 | - |
| 2026 | 2 | 350 | 0.85 | - | - |
| 2027 | 3 | 500 | - | - | - |

→ Year 3 末のアクティブ顧客 = 500 + 350×0.85 + 200×0.75 + 100×0.70 = 500+298+150+70 = 1,018

### 6.3 拡張: Multi-segment

セグメント別 (SMB / Mid / Ent) に独立 forecast し合算:

$$
\text{Revenue}(t) = \sum_{s} N_s(t) \cdot \text{ARPU}_s(t)
$$

各 segment は独立に:
- TAM_s
- SAM%_s (絞り込み)
- p_s(t) (Logistic / Bass)
- ARPU_s(t)

例:

| Segment | $N$ Yr 5 | ARPU | Revenue |
|---|---|---|---|
| SMB | 5,000 | $300/月 | $18M/年 |
| Mid | 800 | $1,500/月 | $14.4M/年 |
| Ent | 80 | $10,000/月 | $9.6M/年 |
| **計** | - | - | **$42M/年** |

### 6.4 Sales motion 別 / Channel 別

Sales motion で取得効率と CAC が異なる:

| Motion | CAC (Mid SaaS) | Sales cycle | Win rate |
|---|---|---|---|
| PLG (self-serve) | $500-2,000 | 1-7 日 | N/A (signup) |
| Inbound (MQL → SQL) | $5,000-15,000 | 30-90 日 | 15-25% |
| Outbound (cold) | $20,000-50,000 | 60-180 日 | 5-10% |
| Partner / channel | $10,000-20,000 | 60-120 日 | 20-30% |

各 motion の量 × 単価で revenue 構成を分解する。

### 6.5 Sensitivity 設計

#### 6.5.1 1 因子感度

| 変数 | -20% | -10% | base | +10% | +20% |
|---|---|---|---|---|---|
| TAM | 80M | 90M | 100M | 110M | 120M |
| Penetration ramp | × 0.5 | × 0.75 | × 1.0 | × 1.25 | × 1.5 |
| ARPU | -15% | -7.5% | base | +7.5% | +15% |

各 1 因子だけ動かして revenue 出力をプロット。

#### 6.5.2 Tornado chart

各因子の感度幅 (vary range で revenue が動く幅) を棒で並べる。視覚的に「どの仮定が一番効くか」を示す。

[出典: Tornado Diagram - Wikipedia](https://en.wikipedia.org/wiki/Tornado_diagram)

#### 6.5.3 Monte Carlo

3-5 因子に対して分布 (正規 / 三角) を仮定し 10,000 回シミュレーション:

```python
import numpy as np
N = 10000
TAM = np.random.triangular(80, 100, 130, N)         # M$
SAM_pct = np.random.triangular(0.15, 0.22, 0.28, N)
p_yr5 = np.random.triangular(0.05, 0.10, 0.20, N)
ARPU = np.random.normal(600, 60, N)                  # $
revenue = TAM * SAM_pct * p_yr5 * 1e6 * ARPU
```

→ p10 / p50 / p90 で revenue レンジを示す。

### 6.6 Excel 実装パターン

| シート | 内容 |
|---|---|
| Inputs | TAM, SAM%, ARPU, p の base / sensitivity 入力 |
| Population | 母集団 (顧客数等) の年次推移 |
| Penetration | $p(t)$ の Logistic / Bass 計算 |
| Cohorts | 取得 cohort × retention 表 |
| Revenue | 統合 revenue forecast |
| Scenarios | best / base / worst |
| Sensitivity | tornado / 2D heat map |

色分けは `00_design_guidelines.md` 準拠 (Inputs = blue, Calc = black, Output = navy)。

### 6.7 Python 実装パターン (`scripts/build_model.py` 参照)

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Segment:
    name: str
    population: Callable[[int], float]   # year -> N
    sam_pct: Callable[[int], float]
    arpu: Callable[[int], float]
    penetration: Callable[[int], float]  # year -> p

def revenue(seg: Segment, t: int) -> float:
    return seg.population(t) * seg.sam_pct(t) * seg.penetration(t) * seg.arpu(t)

def total_revenue(segs: list[Segment], t: int) -> float:
    return sum(revenue(s, t) for s in segs)

# Logistic helper
def logistic(K: float, r: float, t0: float):
    import math
    return lambda t: K / (1 + math.exp(-r * (t - t0)))
```

### 6.8 Build-side 検証チェック

| チェック | 数式 | OK 条件 |
|---|---|---|
| 浸透率 ≤ 1 | $p(t) \leq 1$ | 全年 |
| 浸透率 monotone (短中期) | $p(t+1) \geq p(t)$ | 競合 churn 無しモデルで |
| 顧客数 = N(t) × p(t) | - | revenue = N × p × ARPU と整合 |
| TAM ≥ SAM ≥ SOM | - | 三層関係 |
| ARPU > 0 | - | 全 segment |
| Multi-segment 合計 | $R = \sum_s R_s$ | 集計と各 segment 合致 |
| Cohort retention | $R(\tau+1) \leq R(\tau)$ | 単調減少 (NRR 含むなら別計算) |

---

## 7. Sanity Check / 投資判断視点

### 7.1 TAM 健全性チェック

#### 7.1.1 必要規模成立

$$
\text{TAM} \times \text{Realistic Max Share (5-10\%)} \geq \text{Target ARR at exit}
$$

不成立なら unicorn 不可。Series A 時点で要 reset。

#### 7.1.2 "If we get 1% of $1B" 思考の罠

「市場 $1B のうち 1% 取れば $10M」的アプローチは VC で減点。理由:

1. **1% も非自明**: Series A までで 0.01-0.1% 程度が現実
2. **どのように取るか不在**: GTM の説明欠落
3. **逆転発想**: 「$10M ARR を作るには何 logo / ARPU 必要?」のほうが defensible

[出典: a16z - The 1% Pitch is the Worst Pitch](https://a16z.com/)

#### 7.1.3 矛盾検出

- TAM > 対象国 GDP → 誤算
- TAM > カテゴリ全体支出 → 誤算
- TAM expansion 5 年 10x → 過大、3x 上限が現実的

### 7.2 Penetration 健全性

#### 7.2.1 Ceiling

§3.6 の業界別 ceiling を超える forecast は要根拠 (同業比較)。

#### 7.2.2 Time to milestone

| milestone | 5 年で到達なら? | 7 年で到達なら? | 10 年で到達なら? |
|---|---|---|---|
| 1% | 普通 | 遅い | 失敗 |
| 10% | 強気 | 普通 | 遅い |
| 25% | 非常に強気 | 強気 | 普通 |
| 50% | 過剰 (PMF 異常) | 過剰 | 強気 |

#### 7.2.3 Competitive density 補正

$$
p_{\text{your}}^{\text{realistic}} = p_{\text{cat}}^{\text{ceiling}} \times s_{\text{your}}
$$

競合 5 社の市場で自社シェア 30% 取得は通常困難。10-20% で見るのが defensible。

### 7.3 Comparison Anchor (歴史的類似)

ベンチマーク企業の penetration curve を比較対象として並べる。

| 企業 | カテゴリ | 起点〜10% | 10% → 25% | 25% → 飽和 |
|---|---|---|---|---|
| Salesforce | CRM (US 大企業) | 4 年 | 5 年 | 飽和 ~50% |
| Shopify | E-commerce platform | 5 年 | 4 年 | 継続中 ~30% |
| Zoom | Video conferencing | 3 年 | 2 年 (COVID 加速) | ~70% |
| Slack | Team chat (tech) | 2 年 | 3 年 | 業界 50%+ |
| Stripe | Online payment | 6 年 | 5 年 | 継続 |
| Uber (US) | Rideshare | 3 年 | 4 年 | 飽和 ~70% (urban) |

#### 7.3.1 "TAM realized" 比

現在の market leader の market cap / TAM 比から、TAM の現実度を評価:

$$
\text{TAM Realized Ratio} = \frac{\text{Top 3 player の合計 market cap}}{\text{TAM}}
$$

- < 5%: 未成熟、参入余地大
- 5-20%: 標準
- 20-50%: 成熟、新規参入は差別化必須
- > 50%: 飽和、M&A target 化が現実

### 7.4 Bessemer "10x penetration" stress test

> 現在の penetration を 10 倍した世界が想像できるか?

- Yes → カテゴリの max が見える、安心
- No → カテゴリが既に飽和、TAM 水増しの可能性

例: vertical SaaS for X、現在 1% → 10% を想定すると 1,700 → 17,000 顧客、現実的。

### 7.5 投資判断側との接続 (`08_investment_thesis.md` §7)

| build-side (本リファレンス) | judgment-side (`08_investment_thesis.md`) |
|---|---|
| §1 TAM/SAM/SOM 三層 | §7.1 TAM 健全性 |
| §2.4 Triangulation | §7.2 三角測定 |
| §3.6 Penetration ceiling | §7.3 Penetration realistic ceiling |
| §7.3 Comparison anchor | §7.4 類似企業 anchor |

---

## 8. 業態別 sizing パターン

### 8.1 SaaS B2B

#### 8.1.1 基本式

$$
\text{TAM}_{\text{SaaS}} = \sum_s N_s^{\text{companies}} \times \text{seats}_s \times \text{price/seat/年}
$$

または ACV ベース:

$$
\text{TAM}_{\text{SaaS}} = \sum_s N_s^{\text{companies}} \times \text{ACV}_s
$$

#### 8.1.2 Vertical-specific

例: legal tech

- 母集団: 全国法律事務所数 (日弁連発表)
- 1 事務所あたり弁護士数 → seat 数
- seat 単価: $30-200/月

#### 8.1.3 TAM 拡張パス

| パス | 例 | 効果 |
|---|---|---|
| Geo expansion | JP → APAC → Global | x3-10 |
| Up-market (SMB → Ent) | 価格 5x で同顧客数 | x2-5 |
| Cross-product | CRM → marketing → service | x2-3 |
| New persona | sales → marketing → CS | x2 |

### 8.2 Marketplace

#### 8.2.1 GMV TAM

$$
\text{GMV}_{\text{TAM}} = \text{Transactions/年} \times \text{AOV}
$$

または

$$
\text{GMV}_{\text{TAM}} = \text{Active buyers} \times \text{Frequency} \times \text{AOV}
$$

#### 8.2.2 Net revenue TAM

$$
\text{Revenue}_{\text{TAM}} = \text{GMV}_{\text{TAM}} \times \text{Take Rate}
$$

Take rate 典型値:

| Marketplace タイプ | Take rate |
|---|---|
| Generic e-commerce (Amazon style) | 8-15% |
| Travel (Booking) | 10-20% |
| Food delivery | 15-30% |
| Rideshare | 20-30% |
| Vertical professional (Toptal 等) | 20-40% |
| 中古品 (Mercari) | 5-10% |

[出典: a16z - All Marketplaces are Not Created Equal](https://a16z.com/)

#### 8.2.3 双方の sizing

- Supply side TAM: 売り手の総供給量
- Demand side TAM: 買い手の総需要

両者の min が現実的 GMV 上限。

### 8.3 Fintech

#### 8.3.1 Payment / Wallet

$$
\text{Revenue}_{\text{TAM}} = \text{TPV (Total Payment Volume)} \times \text{Take Rate}
$$

Take rate: 0.5-3% (国・カード類別)。

#### 8.3.2 Lending

$$
\text{Revenue}_{\text{TAM}} = \text{Loan Book Outstanding} \times \text{NIM (Net Interest Margin)}
$$

NIM 典型: 3-8% (スタートアップは 5-10%)。

#### 8.3.3 SaaS-Fintech (banking-as-a-service)

$$
\text{Revenue} = N_{\text{accounts}} \times \text{Subscription} + \text{TPV} \times \text{Take Rate}
$$

ハイブリッド計算。

#### 8.3.4 Wealth / Asset management

$$
\text{Revenue}_{\text{TAM}} = \text{AUM} \times \text{Management Fee} (0.25-1.5\%)
$$

### 8.4 D2C / E-commerce

#### 8.4.1 既存カテゴリベース

$$
\text{TAM} = \text{カテゴリ売上 (例: コーヒー国内)} \times \text{オンライン比率} \times \text{自社 SKU 適合率}
$$

#### 8.4.2 LTV ベース

$$
\text{TAM} = N_{\text{target customers}} \times \text{LTV}
$$

LTV = AOV × Frequency × Retention 期間。

#### 8.4.3 Wallet share

$$
\text{Revenue per customer} = \text{Annual category spend} \times \text{Wallet share (5-30\%)}
$$

例: コーヒー D2C → 月 ¥3,000 × 12 月 × wallet share 25% = ¥9,000/年。

### 8.5 Bio / Pharma

#### 8.5.1 Patient-based

$$
\text{TAM} = \text{Disease prevalence} \times N_{\text{population}} \times \text{Diagnosis rate} \times \text{Treatment rate} \times \text{Annual cost} \times \text{Adherence}
$$

例: 糖尿病薬 (US)

| 因子 | 値 |
|---|---|
| US 人口 | 330M |
| Prevalence | 11% |
| Diagnosed | 75% |
| Treated | 90% |
| Annual drug cost | $4,000 |
| Adherence | 60% |
| TAM | 330 × 0.11 × 0.75 × 0.90 × 4,000 × 0.60 = $58.8B |

#### 8.5.2 Reimbursement 補正

$$
\text{Net TAM} = \text{Gross TAM} \times \text{Reimbursement rate} \times (1 - \text{Rebate})
$$

US で reimbursement 70-90%、rebate 30-50% (PBM)。

### 8.6 Hardware

#### 8.6.1 New device

$$
\text{TAM} = N_{\text{target users}} \times \text{ASP} \times \frac{1}{\text{Replacement cycle (年)}}
$$

例: スマホ
$$
\text{Annual TAM (US)} = 250M \text{ users} \times \$800 / 3 \text{ 年} = \$66.7B/年
$$

#### 8.6.2 Software attach

$$
\text{Total TAM} = \text{HW TAM} + N_{\text{installed base}} \times \text{Software ARPU}
$$

iPhone のように HW + services 両方計上。

#### 8.6.3 Replacement cycle

| カテゴリ | 平均 cycle (年) |
|---|---|
| Smartphone | 2-3 |
| PC | 4-6 |
| Car | 7-12 |
| Refrigerator | 10-15 |
| 産業機械 | 7-15 |

### 8.7 Subscription consumer (D2C, media)

#### 8.7.1 ARPU × subscriber

$$
\text{TAM} = \text{Subscriber TAM} \times \text{ARPU/月} \times 12
$$

例: 動画配信 (US)
$$
\text{TAM} = 130M \text{ HHs} \times \$10/月 \times 12 = \$15.6B/年
$$

#### 8.7.2 Ad-supported tier

両収益源を加算:

$$
\text{Total Revenue} = N_{\text{paid}} \times \text{Sub ARPU} + N_{\text{ad-tier}} \times \text{Ad ARPU}
$$

### 8.8 EdTech

$$
\text{TAM} = N_{\text{learners}} \times \text{Annual tuition / course fee} \times \text{Online conversion rate}
$$

国内例: 学習塾市場 ¥1.0 trillion → オンライン 15% → ¥150B (online tuition TAM)。

### 8.9 Insurance / InsurTech

$$
\text{TAM} = \text{Premium Pool} \times \text{Online distribution share} \times \text{自社 segment 比率}
$$

または GWP (Gross Written Premium) ベース:
$$
\text{Revenue} = \text{GWP} \times \text{Commission rate (10-30\%)}
$$

### 8.10 Cybersecurity

$$
\text{TAM} = N_{\text{enterprises}} \times \text{Security budget per company}
$$

参考: 大企業のセキュリティ予算は年商の 0.5-2% 程度。

---

## 9. Anti-patterns (典型的な誤り)

### 9.1 概念レベル

| # | アンチパターン | 症状 | 修正 |
|---|---|---|---|
| A1 | "If we get 1% of $1B" 思考 | 「市場 $1B のうち 1% で $10M」と pitch | bottom-up 顧客数 × ARPU で説明 |
| A2 | Top-down 単独 | 業界レポートだけで TAM 提示 | bottom-up と value-based を triangulate |
| A3 | 単一データソース依存 | Statista 1 本のみ引用 | 3+ ソースで cross-check |
| A4 | 古いデータ (>3 年) | 2019 年レポートで 2026 年予測 | 直近 12-24 ヶ月のソース |
| A5 | 為替・インフレ未補正 | 旧レート $1=¥100 で現在 ¥150 比較 | 現在レートで再換算 |
| A6 | 地理重複 | 「グローバル + US + APAC」三重計上 | 階層的に絞る |
| A7 | 顧客単位の誤り | "全社員 × ARPU" 計算 | 実購買単位 (DMU, seat) で計算 |
| A8 | 業界 outsider の見立て | 「肌感」で TAM 設定 | 実顧客 / 業界専門家 ヒアリング |

### 9.2 Forecast レベル

| # | アンチパターン | 症状 | 修正 |
|---|---|---|---|
| F1 | TAM expansion 過剰 | Year 5 で 10x TAM | 2-3x 上限 |
| F2 | Penetration 100% 仮定 | $K = 1.0$ in Logistic | 業界 ceiling (§3.6) を反映 |
| F3 | 競合反応無視 | 自社のみシェア 50% | competitive density 補正 (§3.8) |
| F4 | Regulatory headwind 無視 | 規制コストゼロ前提 | 規制適合コスト織り込み |
| F5 | Static ARPU | 5 年同 ARPU | mix shift / NRR / インフレを反映 |
| F6 | Penetration linear | 線形の浸透率増加 | S 字 / Bass で実態を反映 |
| F7 | Sensitivity 欠落 | Best case のみ提示 | best/base/worst を必須化 |
| F8 | 仮定の出典なし | 「業界平均」とだけ書く | 出典 URL 必須 |

### 9.3 投資家プレゼンレベル

| # | アンチパターン | 修正 |
|---|---|---|
| P1 | TAM のみ示し SAM/SOM 無し | 三層必須 |
| P2 | 競合の存在を見せない | 競合マップ + シェア前提を明示 |
| P3 | "We're the first" 主張 | 既存代替手段を必ず認識 |
| P4 | Take rate / Margin の説明欠落 | revenue model を明示 |
| P5 | Team capacity と整合しない target | sales capacity 制約を併記 (§1.7.2) |

### 9.4 数値の現実性レンジ (黄信号)

| 指標 | 現実的 | 要再考 | 危険 |
|---|---|---|---|
| TAM 成長率 (年) | 8-15% | 20-30% | >40% |
| 5 年浸透率到達 | 1-10% | 10-25% | >25% |
| ARPU 成長率 (年) | 3-8% | 10-15% | >20% |
| Win rate (B2B) | 15-30% | 30-50% | >50% |
| Sales rep quota 達成率 | 60-80% | 80-100% | >100% (sustained) |

### 9.5 為替・通貨換算の注意

| 用途 | 推奨レート |
|---|---|
| Historical comparison | 当時の年平均レート |
| 現在価値比較 | 直近 12 ヶ月平均 |
| 5 年 forecast | フォワードカーブ (CME) または PPP |
| Sensitivity | ±10-15% を base case 周辺 |

PPP (Purchasing Power Parity) と nominal rate の使い分け:

- nominal: 国際送金、輸出入、IR 開示
- PPP: 生活水準比較、新興国市場の購買力

[出典: World Bank ICP - PPP Data](https://www.worldbank.org/en/programs/icp)

---

## 10. 投資家プレゼン用 TAM スライド標準形

### 10.1 必須要素 7 点

1. TAM / SAM / SOM の数値 (currency 明示)
2. 三層図 (concentric circles or pyramid)
3. Bottom-up 内訳 (segment × ARPU)
4. 出典明記 (3+ ソース)
5. 算出年 (timestamp)
6. "Why now" のタイミング論
7. TAM expansion ロードマップ

### 10.2 三層図のテンプレ

#### 同心円 (concentric circles) 型

```
        TAM ¥150B
       (Global SaaS for legal)
       ┌────────────────────┐
       │   SAM ¥8.5B        │
       │  (JP, 17K firms)   │
       │   ┌──────────┐     │
       │   │ SOM ¥850M│     │
       │   │ (5 yr,   │     │
       │   │  10% pen)│     │
       │   └──────────┘     │
       └────────────────────┘
```

#### ピラミッド型

```
       ┌────────────────────┐
       │       TAM          │  ¥150B
       │  Global / All      │
       └────────┬───────────┘
                │
        ┌───────┴────────┐
        │      SAM       │  ¥8.5B
        │ JP, 17K firms  │
        └───────┬────────┘
                │
        ┌───────┴───┐
        │    SOM    │  ¥850M
        │  5y / 10% │
        └───────────┘
```

### 10.3 Bottom-up 内訳の標準テーブル

| Segment | 母集団 | ARPU/年 | 5yr ペネトレ | Revenue/年 (Yr 5) |
|---|---|---|---|---|
| Solo lawyer | 9,500 | ¥120K | 8% | ¥91M |
| SMB firm (2-10) | 6,800 | ¥600K | 12% | ¥489M |
| Mid firm (11-50) | 600 | ¥3M | 15% | ¥270M |
| Large firm (51+) | 100 | ¥12M | 20% | ¥240M |
| **合計** | **17,000** | - | - | **¥1,090M** |

### 10.4 出典の書き方

スライド最下部 (footer 8pt):

> Sources: 日弁連 弁護士白書 2024 / 矢野経済 リーガルテック市場 2025 / 自社顧客ヒアリング (n=42, 2025/Q1)

### 10.5 "Why now" の標準 4 軸

1. **技術** (例: GenAI コスト 1/10 化)
2. **規制** (例: 2025 年改正民法施行)
3. **行動変化** (例: コロナ後のリモートワーク定着)
4. **経済** (例: 弁護士報酬の透明化義務)

これらが過去 12-24 ヶ月で同時発生していると "now" 主張が defensible。

### 10.6 競合との位置取りスライド

2x2 マトリクス (例: 価格軸 × 機能網羅性軸) または機能比較表で示す。

### 10.7 TAM expansion ロードマップ

| Phase | Year | TAM 増分 | 累積 TAM | 動作 |
|---|---|---|---|---|
| Beachhead | 0-2 | ¥8.5B | ¥8.5B | JP 法律事務所 |
| Adjacent | 2-4 | +¥3B | ¥11.5B | 弁理士、司法書士 |
| Geography | 3-5 | +¥30B | ¥41.5B | 韓国、台湾 |
| Horizontal | 5-7 | +¥50B | ¥91.5B | 会計士、コンサル |

### 10.8 Act デザイン適用

- 配色: Surface ¥ECE9E1, Ink ¥2D332E, Primary ¥008A80, Accent ¥ECC85A
- 強調は 1 画面 1 か所 (Accent は SOM 数字のみ)
- 角丸 4-12px、Pill は数値ハイライトのみ
- フォント: Geist Sans (英)、Noto Sans JP (和) - 400/600/700 のみ
- ドロップシャドウ・グラデーションは使わない

---

## 11. 数値例 (mini case 5 件)

### 11.1 Vertical SaaS for 法律事務所 (国内)

#### 設定

- 全国法律事務所: 17,000 (日弁連 2024 年データ、登録弁護士 ~45,000 人)
- 製品: 案件管理 + AI 要約 + 請求

#### TAM/SAM/SOM (年額 ARPU ベース)

| 層 | 計算 | 値 |
|---|---|---|
| TAM (Global legal SaaS) | Gartner Legal Tech 2025 → ¥1.5T | ¥1.5T |
| SAM (JP only) | 17,000 firms × 加重 ARPU ¥500K | ¥8.5B |
| SOM (5 yr, 10% pen) | SAM × 10% | ¥850M |

#### 5 年 forecast (Logistic K=0.20, r=0.7, t0=4)

| Year | $p$ | 顧客数 | ARPU | Revenue (¥M) |
|---|---|---|---|---|
| 1 | 0.5% | 85 | 480K | 41 |
| 2 | 1.5% | 255 | 500K | 128 |
| 3 | 4.0% | 680 | 520K | 354 |
| 4 | 9.0% | 1,530 | 540K | 826 |
| 5 | 17.0% | 2,890 | 560K | 1,618 |

[出典: 日本弁護士連合会 - 弁護士白書](https://www.nichibenren.or.jp/library/ja/jfba_info/statistics/data/white_paper/)

### 11.2 D2C コーヒー (国内)

#### 設定

- 国内コーヒー消費市場 ¥3.0T (全日本コーヒー協会、レギュラー + インスタント + 缶)
- 自社 SKU: スペシャルティ豆 (国内 ¥150B 推定)
- オンライン比率: 25%

#### TAM/SAM/SOM

| 層 | 計算 | 値 |
|---|---|---|
| TAM (国内コーヒー全体) | カテゴリ全体 | ¥3.0T |
| SAM (オンラインスペシャルティ) | ¥150B × 25% online | ¥37.5B |
| SOM (5 yr, 3% share) | SAM × 3% | ¥1.13B |

#### Bottom-up 検証

50,000 顧客 × 6 回購入/年 × ¥3,000 = ¥900M/年 (3% シェアと整合)

[出典: 全日本コーヒー協会](https://coffee.ajca.or.jp/)

### 11.3 AI 文書作成ツール (SMB 向け)

#### 設定

- 国内 SMB: 4.2M 社 (中小企業庁、個人事業除く 2.0M 社)
- 対象: 文書作成業務がある SMB, 推定 60% = 1.2M 社
- 価格: ¥3,000/月/seat (¥36,000/年)

#### TAM/SAM/SOM

| 層 | 計算 | 値 |
|---|---|---|
| TAM (Global AI writing) | Gartner GenAI for productivity ¥10T | ¥10T |
| SAM (JP SMB) | 1.2M × ¥108K (= ¥36K/seat × 3 seats) = ¥130B | ¥130B |
| SOM (5 yr, S 字 5%) | SAM × 5% | ¥6.5B |

#### Bass モデル (p=0.04, q=0.5, m=60,000 SMB customers, ARPU ¥108K/年)

$N(t) = m \cdot \frac{1 - e^{-(p+q)t}}{1 + (q/p) \cdot e^{-(p+q)t}}$ で計算。

| Year | $N(t)$ | 増分 | Revenue (¥B) |
|---|---|---|---|
| 1 | 3,022 | 3,022 | 0.33 |
| 2 | 7,555 | 4,533 | 0.82 |
| 3 | 13,854 | 6,300 | 1.50 |
| 4 | 21,740 | 7,886 | 2.35 |
| 5 | 30,416 | 8,676 | 3.28 |

[出典: 中小企業庁 - 中小企業実態基本調査 / 中小企業白書](https://www.chusho.meti.go.jp/koukai/chousa/)

### 11.4 ハンドメイド Marketplace (国内)

#### 設定

- 国内ハンドメイド購入市場: ¥1,200B (内閣府推計、2023)
- オンライン比率: 35%
- Take rate: 8%

#### TAM/SAM/SOM (Net revenue base)

| 層 | 計算 | 値 |
|---|---|---|
| GMV TAM | 国内全体 | ¥1.2T |
| GMV SAM | × 35% online | ¥420B |
| Net Revenue SAM | × 8% take | ¥33.6B |
| Net Revenue SOM (5 yr, 5% share) | × 5% | ¥1.68B |

#### 双方検証

- Supply: 国内手作り作家 ~300,000 人 × 平均 GMV ¥1.2M/年 = ¥360B (一致しない、整合再確認要)
- Demand: 国内オンライン消費者 50M × 年 ¥7,000 = ¥350B (近似一致)

### 11.5 Fintech 与信 (中小企業向け)

#### 設定

- 国内中小企業数: 3.8M 社 (中企庁、2024)
- 借入経験: 65% → 2.47M 社
- 平均借入額: ¥30M/社 → 借入残高 ~¥75T
- NIM 自社想定: 3.5%

#### TAM/SAM/SOM

| 層 | 計算 | 値 |
|---|---|---|
| TAM (国内法人融資) | 借入残高 × NIM 平均 2.0% | ¥1.5T |
| SAM (デジタル融資、自社対象 SMB) | 借入残高 ¥30T × 3.5% NIM | ¥1.05T |
| SOM (5 yr, 0.5% share of SAM) | × 0.5% | ¥5.25B |

#### Bottom-up 検証

15,000 社 × 平均借入残高 ¥30M × 3.5% NIM = ¥15.75B (上方乖離、シェア仮定再考要 → 0.15-0.3% にする)

[出典: 中小企業庁 / 日本銀行 - 貸出金利動向](https://www.boj.or.jp/statistics/dl/loan/prime/index.htm)

---

## 12. ケーススタディ (公開データから読み取る)

### 12.1 a16z の TAM 評価方法

a16z (Andreessen Horowitz) は portfolio memo 公開で知られ、以下のフレームを使う:

#### 12.1.1 "Sizing Markets That Don't Exist Yet"

新カテゴリで TAM が無い場合、3 つの問いで近似:

1. **既存予算の displacement** どこから予算が来るか?
2. **新需要創出** 既存にない予算を作るか?
3. **行動変化** 行動変容で量が変わるか?

[出典: a16z - 16 More Startup Metrics](https://a16z.com/2014/02/27/16-more-startup-metrics/)

#### 12.1.2 a16z TAM Stress test

- "If we 100% won, what would our revenue be?"
- "What is the monopoly value?"
- "How does this compare to the largest companies in the category?"

### 12.2 Sequoia の "going to be huge" criteria

Sequoia Capital の "Elements of Enduring Companies" framework:

1. **Clarity of purpose**: 創業者が問題を明文化できる
2. **Markets > Teams > Products**: 市場の大きさが最重要
3. **Step function moments**: TAM が拡張する不連続イベント

#### 12.2.1 TAM の評価軸

| 観点 | criteria |
|---|---|
| Size | $10B+ で "going to be huge" |
| Growth | 年 15%+ で "secular growth" |
| Concentration | top 5 で 50% 未満なら fragmented (新規参入余地) |
| Adoption stage | early majority 入り直前が peak |

[出典: Sequoia - Writing a Business Plan / Pitch Deck Template](https://www.sequoiacap.com/article/writing-a-business-plan/)
[出典: Sequoia - Elements of Enduring Companies](https://articles.sequoiacap.com/company-design)

### 12.3 Y Combinator の Day 1 評価

YC の partner は 10-min ビデオ評価で TAM を見る。基準:

1. **Median outcome > $100M**: average ではなく中央値
2. **Win condition**: 何ができれば勝ち?
3. **Failure mode**: 何ができないと負け?

YC が嫌う pitch:
- "$10B market" だけで根拠なし
- "We'll capture 5%" → どうやって?
- TAM > GDP 規模 → 即減点

[出典: Paul Graham - Startup = Growth](http://paulgraham.com/growth.html)
[出典: YC - How to Pitch your Startup](https://www.ycombinator.com/library/6q-how-to-pitch-your-startup)

### 12.4 Bessemer の "stress test"

Bessemer Venture Partners は cloud SaaS 投資の標準で以下の "10x penetration" thinking を奨励:

> "What does the world look like if 10x more customers used this product?"

- それでも TAM が有限なら: 真の TAM 上限が見える
- それで TAM が突然非現実的: 既に飽和している証拠

[出典: Bessemer - State of the Cloud Report](https://www.bvp.com/atlas/state-of-the-cloud)

### 12.5 Damodaran の market sizing

Aswath Damodaran (NYU Stern) はバリュエーション分野で TAM 推定の academic フレームを公開:

#### 12.5.1 "Story to Numbers" framework

1. Story: 競合と異なる物語
2. Cap on potential market: 現実的上限
3. Market share trajectory: 年次シェア推移
4. Operating margins at scale: 飽和時 EBITDA マージン
5. Reinvestment needs: CAPEX/OPEX のドライバー
6. Risk: WACC

#### 12.5.2 Uber バリュエーション (公開 2014)

- 当時 TAM: 全タクシー市場 $100B
- Damodaran 評価: $5.9B (車利用 displacement 含めず)
- 後の見直し: $50B+ (rideshare で car ownership displacement 含む)
- 教訓: TAM の定義によって 10x 変動する

[出典: Aswath Damodaran - Uber Valuation, 2014](https://aswathdamodaran.blogspot.com/2014/06/possible-probable-plausible-and.html)
[出典: Aswath Damodaran - Narrative and Numbers](http://pages.stern.nyu.edu/~adamodar/)

### 12.6 経産省 / 矢野経済研究所の使い方

#### 12.6.1 経産省 IT 関連市場調査

経産省「特定サービス産業実態調査」「情報通信業基本調査」「電子商取引市場調査」を主に使う:

- 電子商取引市場規模 (BtoB / BtoC / CtoC) - 年次
- 業種別 IT 投資 (大企業中心)

#### 12.6.2 矢野経済研究所のレポート活用

- 業界動向 / 主要プレーヤーシェア / 中期予測
- 50-200 ページ、¥150K-500K/レポート
- 公開サマリ (~10%) は無料、競合把握に有用

ポイント: bottom-up を組んだ後の cross-check 用。出発点としては top-down 過大評価のリスクあり。

[出典: 経産省 - 電子商取引に関する市場調査](https://www.meti.go.jp/policy/it_policy/statistics/outlook/ie_outlook.html)
[出典: 矢野経済研究所 - プレスリリース](https://www.yano.co.jp/press-release/)

---

## 13. 市場規模 DD チェックリスト

投資家側 (judgment-side) と経営側 (build-side) 双方で使える DD チェック。`08_investment_thesis.md` §7 と組合せて使用。

### 13.1 TAM 定義の妥当性

- [ ] TAM の定義文が 2 行以内で書けるか
- [ ] 母集団 (companies / users / households) が明示されているか
- [ ] 単位 (currency, time period) が明示されているか
- [ ] TAM > 自社対象国 GDP の矛盾がないか
- [ ] TAM > カテゴリ全体支出 の矛盾がないか
- [ ] 隣接市場の重複計上がないか (例: SaaS + クラウドインフラ)
- [ ] グローバル / 地域別の geography overlap がないか

### 13.2 データソースの質

- [ ] 3+ の独立ソースを cross-check したか
- [ ] 直近 12-24 ヶ月のデータか
- [ ] 公的統計 (政府 / 国際機関) を 1+ 含むか
- [ ] 業界団体データを 1+ 含むか
- [ ] 為替 / インフレ補正済か
- [ ] 出典 URL が明記されているか
- [ ] 各セグメント比率の根拠が出典付きか

### 13.3 SAM の絞り込み

- [ ] 言語制約 (対応言語数) を反映済か
- [ ] 地理制約 (規制 / 営業拠点) を反映済か
- [ ] 業界制約 (vertical) を反映済か
- [ ] 企業サイズ制約 (SMB only 等) を反映済か
- [ ] 製品 SKU 適合範囲を反映済か
- [ ] チャネル到達制約を反映済か

### 13.4 SOM の現実性

- [ ] 5 年 SOM が SAM の 1-15% 以内か
- [ ] 競合シェアと整合するか
- [ ] Sales capacity 制約と整合するか
- [ ] CAC × Customers の総額が funding と整合するか
- [ ] Penetration milestone (1%/10%/25%) timing が業界 typical 内か

### 13.5 算出手法の triangulation

- [ ] Top-down 法で算出した値があるか
- [ ] Bottom-up 法で算出した値があるか
- [ ] Value-based 法 (新カテゴリの場合) で算出したか
- [ ] 3 手法のレンジが ±50% 内に収まるか
- [ ] レンジ不一致の場合、解釈を明示しているか

### 13.6 Penetration モデル

- [ ] 浸透率モデル (Logistic / Bass / Geographic) を明示しているか
- [ ] パラメータ (K, r, t0 / p, q, m) の根拠を明示しているか
- [ ] 業界 ceiling (§3.6) を超えていないか
- [ ] Competitive density 補正済か
- [ ] Network effect の有無を明示しているか

### 13.7 ARPU / 単価

- [ ] ARPU の通貨と期間 (月/年) を明示しているか
- [ ] Segment 別 ARPU を分解しているか
- [ ] Pricing tier (Free / Pro / Ent) と比率を示しているか
- [ ] WTP 推定の根拠 (PSM / Conjoint / 競合) があるか
- [ ] 時間変動 (NRR / mix shift / インフレ) を反映しているか

### 13.8 Forecast の構造

- [ ] Cohort 別計算をしているか (B2B SaaS / D2C で必須)
- [ ] Multi-segment 別計算をしているか
- [ ] Sales motion / Channel 別の分解があるか
- [ ] Sensitivity (±20% / ±15% etc.) を提示しているか
- [ ] Best / Base / Worst の 3 シナリオを示しているか
- [ ] Tornado chart (Sensitivity) を作成しているか

### 13.9 Sanity check

- [ ] "If 100% win" で revenue が unicorn 規模か
- [ ] "10x penetration" で TAM が見える上限か
- [ ] Realistic max share × TAM ≥ Target ARR が成立するか
- [ ] 類似企業 (Salesforce / Shopify / Zoom) の penetration curve と比較したか
- [ ] TAM realized ratio (top 3 / TAM) を確認したか

### 13.10 Anti-pattern 検出

- [ ] "If we get 1% of $XB" 思考になっていないか
- [ ] Top-down 単独になっていないか
- [ ] 全社員 × ARPU の誤計算がないか
- [ ] TAM expansion 5 年 10x になっていないか
- [ ] Penetration 100% 仮定がないか
- [ ] 競合反応無視がないか

### 13.11 投資家プレゼン整合性

- [ ] 三層図 (concentric / pyramid) を提示しているか
- [ ] Bottom-up 内訳テーブルを示しているか
- [ ] "Why now" 4 軸を提示しているか
- [ ] TAM expansion ロードマップを示しているか
- [ ] 競合との位置取りを示しているか

---

## 14. TAM プレゼン作成手順

### 14.1 全体フロー (8 ステップ)

| Step | アクション | 産出物 | 工数目安 |
|---|---|---|---|
| 1 | カテゴリ定義 | 1 行の market 定義 | 1h |
| 2 | データ収集 (一次 / 二次) | URL リスト、PDF | 4-8h |
| 3 | Top-down 算出 | TAM_T 数値 + 計算 | 2h |
| 4 | Bottom-up 算出 | TAM_B 数値 + segment 表 | 4-8h |
| 5 | Value-based 算出 (任意) | TAM_V 数値 | 2-4h |
| 6 | Triangulation | レンジと中央値 | 1h |
| 7 | Penetration / forecast 構築 | 5 年 revenue 表 | 4-8h |
| 8 | スライド化 | 3-5 ページ完成 | 2-4h |

合計: 20-37h (1-2 週間で完成可能)

### 14.2 Step 1: カテゴリ定義 (1 行)

> "We are the [product type] for [target persona] solving [problem]"

例:
- "Vertical SaaS for JP law firms solving case management"
- "AI doc-creation tool for SMB-level marketing teams"
- "Online marketplace for handmade goods buyers"

定義が曖昧なら TAM 計算も曖昧になる。

### 14.3 Step 2: データ収集チェックリスト

- [ ] Gartner / IDC / Forrester いずれか 1 本 (グローバル)
- [ ] 国内調査会社 (矢野 / 富士経済 / MM 総研) 1 本
- [ ] 政府統計 (経産省 / 総務省 / e-Stat) 1 本
- [ ] 業界団体データ 1 本
- [ ] 公開 IR (上場競合 3 社の S-1 / 決算)
- [ ] 顧客ヒアリング (n=10+ の primary research)

### 14.4 Step 3: Top-down のテンプレ計算

```
Total category market (出典 A): $X
× セグメント比率 (出典 B): Y%
× 地理比率 (出典 C): Z%
= TAM_T = $X × Y × Z
```

各掛け算に出典必須。

### 14.5 Step 4: Bottom-up のテンプレ計算

| Segment | 母集団 (出典) | ARPU | 小計 |
|---|---|---|---|
| Segment A | N_A (出典 X) | ARPU_A | N_A × ARPU_A |
| Segment B | N_B (出典 Y) | ARPU_B | N_B × ARPU_B |
| ... | ... | ... | ... |
| **計** | - | - | TAM_B |

母集団は政府統計 / 業界団体 / 一次データから取る。ARPU は自社 pricing + 競合 benchmark。

### 14.6 Step 5: Value-based 計算 (新カテゴリ向け)

```
1 顧客あたり year value (出典 + 推計):
  - 削減できる時間: X 時間/年 × ¥Y/時間 = ¥Z
  - 削減できるコスト: ¥W/年
  - Total value V = ¥(Z + W)/年

× WTP 比率 (典型 20-30%): α
× 全顧客数 N
= TAM_V = N × V × α
```

### 14.7 Step 6: Triangulation の提示形

```
TAM レンジ:
  Top-down (T):     ¥7-9B
  Bottom-up (B):    ¥8.2B  ← 推奨 base case
  Value-based (V):  ¥9-11B
  
中央値: ¥8-9B
信頼幅: ±30%
```

### 14.8 Step 7: Forecast 構築の最小手順

1. SAM% を決定 (TAM のうち自社対応範囲)
2. Penetration 関数を選択 (Logistic or Bass)
3. パラメータ (K/r/t0) を仮置き、3-5 案検討
4. Cohort × ARPU で revenue 表生成
5. Sensitivity (±20% TAM / ±50% penetration / ±15% ARPU)
6. Best/Base/Worst の 3 シナリオ作成

### 14.9 Step 8: スライド化テンプレ (3-5 枚)

#### Slide 1: Market Size Headline
- ヘッドライン数値 (TAM ¥XB / SAM ¥YB / SOM ¥ZM)
- 三層図 (concentric / pyramid)
- 出典 footer

#### Slide 2: Bottom-up 内訳
- Segment × ARPU テーブル
- 計算式と仮定の前提

#### Slide 3: Penetration & Growth
- S 字カーブ図
- 業界 typical との比較
- Year 5 の目標

#### Slide 4: Competition & Positioning
- 競合マップ (2x2 or 比較表)
- 自社 share trajectory

#### Slide 5: Why Now & Expansion Roadmap
- "Why now" 4 軸 (技術 / 規制 / 行動 / 経済)
- TAM expansion roadmap

### 14.10 レビューチェック (最終版前)

- [ ] §13 DD チェックリスト全項目に対応している
- [ ] 数値が 3 桁ごとカンマで揃っている
- [ ] 通貨・期間が全 slide で一貫している
- [ ] 出典 URL が working link
- [ ] フォントが 400/600/700 のみ
- [ ] 角丸 0/4/8/12/Pill のみ
- [ ] Accent カラー (¥ECC85A) は 1 画面 1 か所
- [ ] ドロップシャドウ・ガラス効果なし

### 14.11 Pitch 質疑想定 Q&A

| Q | 想定 A |
|---|---|
| TAM の根拠は? | 3 手法 triangulation で ¥X-Y、中央値 ¥Z |
| 1% 取れば $10M ですよね? | 1% も自明ではない、bottom-up で N 顧客 × ARPU の絵を書いている |
| 競合 X が既に 30% シェアでは? | Vertical Y では gap がある、自社は Z で差別化 |
| 浸透率の根拠は? | 類似 (Salesforce / Shopify) で同段階 N 年で M% 達成、自社は同等 ramp |
| TAM expansion はいつ? | Year 3 から adjacent vertical、Year 5 から geo expansion |

---

## 付録 A: 数式まとめ

### A.1 三項モデル

$$
\text{Revenue}(t) = \text{TAM}(t) \times \text{SAM\%}(t) \times p(t) \times \text{ARPU}(t)
$$

### A.2 Logistic curve

$$
p(t) = \frac{K}{1 + e^{-r(t - t_0)}}
$$

### A.3 Bass diffusion

$$
\frac{dN(t)}{dt} = \left( p + q \cdot \frac{N(t)}{m} \right) \left( m - N(t) \right)
$$

積分形:

$$
N(t) = m \cdot \frac{1 - e^{-(p+q)t}}{1 + \frac{q}{p} e^{-(p+q)t}}
$$

### A.4 Multi-segment forecast

$$
\text{Revenue}(t) = \sum_{s} N_s(t) \cdot \text{ARPU}_s(t)
$$

### A.5 Cohort 化

$$
\text{Revenue}(t) = \sum_{c \leq t} A_c \cdot R(t - c) \cdot \text{ARPU}_c \cdot (1 + g)^{t-c}
$$

### A.6 Triangulation 加重平均

$$
\text{TAM}_{\text{final}} = w_T T + w_B B + w_V V,\quad \sum w_i = 1
$$

### A.7 Network effect scaling

| Law | $V \propto$ |
|---|---|
| Sarnoff | $n$ |
| Metcalfe | $n^2$ |
| Reed | $2^n$ |

### A.8 Price elasticity

$$
\epsilon = \frac{\Delta Q / Q}{\Delta P / P},\quad P^* = \frac{|\epsilon|}{|\epsilon| - 1} \cdot MC
$$

### A.9 Required TAM for unicorn

$$
\text{TAM} \geq \frac{\text{Target ARR at exit}}{\text{Realistic Max Share (5-10\%)}}
$$

---

## 付録 B: 主要パラメータ早見表

### B.1 Bass パラメータ (業界別)

| 製品カテゴリ | $p$ | $q$ |
|---|---|---|
| 平均 (Bass 1969) | 0.030 | 0.380 |
| 家電耐久財 | 0.025 | 0.420 |
| 産業財 | 0.014 | 0.300 |
| ICT 製品 | 0.040 | 0.450 |
| 医薬品 | 0.005 | 0.400 |
| Web2 SaaS (推定) | 0.030 | 0.500 |

### B.2 Penetration ceiling (業界別)

| カテゴリ | ceiling | 期間 |
|---|---|---|
| B2B SaaS (must-have) | 30-50% | 7-10 年 |
| B2B SaaS (nice-to-have) | 5-15% | 5-10 年 |
| Consumer subscription | 5-15% | 5-10 年 |
| Mobile messaging (national) | 60-90% | 5-7 年 |
| E-commerce (国別) | 15-25% | 10+ 年 |
| Vertical SaaS | 20-40% | 7-10 年 |
| Hardware (consumer) | 50-90% | 5-15 年 |

### B.3 Marketplace take rate

| Marketplace タイプ | Take rate |
|---|---|
| Generic e-commerce | 8-15% |
| Travel | 10-20% |
| Food delivery | 15-30% |
| Rideshare | 20-30% |
| Vertical professional | 20-40% |
| Used goods (Mercari 等) | 5-10% |

### B.4 Replacement cycle (Hardware)

| カテゴリ | 平均 cycle (年) |
|---|---|
| Smartphone | 2-3 |
| PC | 4-6 |
| Car | 7-12 |
| Refrigerator | 10-15 |
| 産業機械 | 7-15 |

### B.5 Price elasticity 典型値

| 製品タイプ | $|\epsilon|$ |
|---|---|
| Necessity | 0.1 - 0.5 |
| 一般 SaaS | 0.5 - 1.5 |
| Discretionary | 1.5 - 3.0 |
| Substitutable | 2.0 - 5.0 |

---

## 付録 C: 関連ドキュメント

- `00_design_guidelines.md`: モデル全般のデザイン方針 (色・フォント等)
- `01a_modeling_standards.md`: Excel / Python モデルの構造
- `01b_integrity_and_anti_patterns.md`: 数値整合と整合性チェック
- `02_saas_metrics.md`: SaaS 指標 (ARR, NRR, LTV, CAC)
- `03_business_models.md`: 業態別のモデル構造
- `06_three_statement.md`: 三表モデル統合
- `07_japan_specifics.md`: 日本固有 (税制, GAAP, 為替)
- `08_investment_thesis.md`: 投資判断側 (IC memo, DD)

---

**Last updated**: 2026-05-01
**Next review**: TAM データソース最新化 (年次)、Bass パラメータ更新 (重要新カテゴリ登場時)
