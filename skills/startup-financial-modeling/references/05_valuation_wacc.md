---
name: valuation_wacc
description: バリュエーション手法 (DCF / Comps / Precedent / VC Method / Berkus / Scorecard / RFS / Real Options) と WACC / 資本コストの正本。SKILL.md dispatch table の "Series A 評価額" / "WACC が g 以下" / "Football field" entry の第 1 reference として読まれる。§21.1 で WACC≈g auto-fallback、§22 で Stage Discount Default。
type: reference
priority: P1
related: [_terminology, 02_saas_metrics, 03_business_models, 08_investment_thesis, _stress_framework, _master_decision_tree]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: バリュエーション手法と WACC は本書を canonical とする。canonical 値 (Stage Discount Default 等) は本書 §22、SaaS metric 閾値は [`_terminology.md §6`](_terminology.md)
- **Routing**: [`_master_decision_tree.md §B`](_master_decision_tree.md) (バリュエーション) から第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (DCF と Comps の overlap、WACC≈g auto-fallback) を必ず実行
- **関連 reference**: `02_saas_metrics §7` (SaaS multiple) / `03_business_models` (業態別) / `08_investment_thesis §4-7` (kill criteria + thesis 定量) / `_stress_framework §2` (stress) / `_master_decision_tree §B`

# 05. バリュエーション手法と資本コスト (Valuation & WACC) — スタートアップ向け徹底リファレンス

> **位置づけ:** スタートアップ・成長企業を対象とした包括的バリュエーション・リファレンス。理論 (theory)、計算手順 (calculation steps)、適用条件 (applicability)、典型的失敗 (common pitfalls)、データソース、ミニケース、DD チェックリスト、トライアンギュレーション (triangulation) 手順を一冊にまとめる。
> **想定読者:** Claude Code skill 内で投資判断ロジックの dual verification を実行するエージェント、および LP/IC/PMF 検討に関わる人間アナリスト。
> **更新方針:** 数値ベンチマーク (Damodaran ERP, country risk, SaaS multiples, VC stage discount) は時点依存であるため、本文中で常に「YYYY-MM 時点」を明記し、一次ソース URL を添える。理論部分はモデル独立。
> **本ドキュメント内の cross-reference 表記:** 「§1.4 参照」のように章節番号で示す。

---

## 0. 本リファレンスの全体構成

| 章 | 内容 | 主用途 |
|---|---|---|
| §1 | DCF (Discounted Cash Flow) 完全展開 | Intrinsic value, IC 用主モデル |
| §2 | 上場類似会社比較法 (Trading Comps) | Market-implied valuation |
| §3 | 類似取引比較法 (Precedent Transactions) | M&A exit price, control premium |
| §4 | VC Method / First Chicago Method | Pre-money / Post-money 算定 |
| §5 | Berkus Method | Idea / pre-revenue stage |
| §6 | Scorecard Method | Pre-revenue, regional benchmark |
| §7 | Risk Factor Summation Method | Pre-revenue, リスク棚卸 |
| §8 | Real Options Valuation | R&D / biotech / staged investment |
| §9 | Replacement Cost / Asset-based | 清算価値 / fallback |
| §10 | Cloud / SaaS 特有 | EV/ARR, Rule of 40, Bessemer |
| §11 | Marketplace / Fintech 特有 | GMV, TPV, take rate, P/B |
| §12 | Damodaran 流派 (NYU Stern) | Implied ERP, CRP, lifecycle |
| §13 | 公正価値 (PPA / 409A / 監査) | ASC 820, IFRS 13, 日本税務評価 |
| §14 | ベンチマーク値とデータソース | 一次ソース URL、頻度、ライセンス |
| §15 | 落とし穴 (cross-cutting pitfalls) | 全手法横断的なバイアス |
| §16 | バリュエーション DD チェックリスト | 投資意思決定前の確認 |
| §17 | トライアンギュレーション手順 | Dual verification の標準フロー |

---

## 1. DCF (Discounted Cash Flow)

### 1.1 DCF の理論的位置づけと2つの流派

DCF は「企業価値 = 将来キャッシュフローの現在価値」という intrinsic valuation (本源的価値評価) の最も基本的な定式化である。スタートアップであっても、最終的に「現金を稼ぐ事業」になるという仮説を置く以上、DCF からは逃げられない。ただしスタートアップ特有の論点 (long horizon、negative FCF、stage discount) がある。

DCF には大きく2系統ある:

- **FCFF (Free Cash Flow to Firm) DCF / Enterprise DCF:** 企業全体に帰属する CF を WACC (加重平均資本コスト) で割引いて Enterprise Value (EV) を算出。そこから Net Debt を控除して Equity Value を得る。
- **FCFE (Free Cash Flow to Equity) DCF / Equity DCF:** 株主に帰属する CF を Cost of Equity (Re) で割引いて Equity Value を直接算出。

| 観点 | FCFF | FCFE |
|---|---|---|
| 割引率 | WACC | Cost of Equity (Re) |
| 出力 | Enterprise Value → Equity Value (EV − Net Debt) | Equity Value 直接 |
| Capital structure 変動 | 反映容易 (WACC で吸収) | 困難 (Re が変動) |
| 銀行 / 保険 / レバレッジ事業 | 不適 (運転資金 ≠ 借入の区別困難) | 適 |
| スタートアップ標準 | **これが標準** | 補助的 |

**実務原則 (rule of thumb):** スタートアップ・成長企業は FCFF を主、FCFE を補助とする。資本構成が頻繁に変動 (down round, convertible, SAFE conversion) するため、WACC で吸収する FCFF の方が運用しやすい。

### 1.2 FCFF (Free Cash Flow to Firm) の計算

完全展開した式:

```
FCFF = EBIT × (1 − t)
       + D&A
       − CapEx
       − ∆NWC
       (− SBC を費用として認識する場合の調整、§15.5 参照)
```

| 変数 | 定義 | 典型値・注意点 |
|---|---|---|
| EBIT | 営業利益 (Earnings Before Interest and Taxes) | スタートアップでは赤字 (negative) も普通。GAAP / IFRS の non-recurring items を normalize する |
| t | 限界実効税率 (marginal effective tax rate) | 日本: 約 30% (法人実効税率)。米: 連邦+州で 21–28%。NOL がある場合は期間中ゼロ→将来 normalize の段階移行 |
| D&A | 減価償却費 + 償却費 (Depreciation & Amortization) | キャッシュアウトを伴わない費用なので加算戻し |
| CapEx | 設備投資額 (Capital Expenditure) | 維持 CapEx と成長 CapEx を分けて議論できると望ましい |
| ∆NWC | 運転資本増加額 (Change in Net Working Capital) | NWC = (売掛+棚卸+前払) − (買掛+前受+未払)。「営業に必要な」短期項目に限定 |

**Stock-Based Compensation (SBC) の扱い (§15.5 で詳細):** GAAP/IFRS 上 EBIT に費用計上されているが、キャッシュフロー計算書では非現金項目として加算戻しされる。**ただし DCF では SBC を真の希薄化コストと見なし、加算戻しをしない (= 現金費用として扱う)** のが Damodaran 流。これを怠ると SaaS の valuation が 2-3 割過大になりがち。

### 1.3 FCFE (Free Cash Flow to Equity) の計算

```
FCFE = Net Income
       + D&A
       − CapEx
       − ∆NWC
       + Net Borrowing (= 新規借入 − 既存借入返済)
```

または:

```
FCFE = FCFF − Interest × (1 − t) + Net Borrowing
```

レバレッジ変動を明示的に扱える反面、Net Borrowing 予測が必要で、スタートアップでは将来の資本構成が不確定なため不安定。

### 1.4 WACC (加重平均資本コスト) — 完全展開

```
WACC = (E / V) × Re + (D / V) × Rd × (1 − t)
```

| 変数 | 定義 |
|---|---|
| E | 株主資本の市場価値 (Market Value of Equity) |
| D | 有利子負債の市場価値 (Market Value of Debt)。簿価で代替する場合の留意は §1.4.4 |
| V | E + D |
| Re | Cost of Equity (株主資本コスト) |
| Rd | Cost of Debt (負債コスト, pre-tax) |
| t | 限界実効税率 |

#### 1.4.1 Cost of Equity (CAPM ベース完全形)

スタートアップ用の拡張 CAPM (modified CAPM, Damodaran 流):

```
Re = Rf
   + β_levered × ERP_mature_market
   + CRP × λ          (country risk premium と country exposure)
   + SP                (size premium, small cap discount)
   + ILP               (illiquidity / marketability discount)
   [+ key person / specific risk premium があれば追加]
```

| 変数 | 内容 | 典型値・注意点 |
|---|---|---|
| Rf | リスクフリーレート | 評価通貨の長期国債利回り。USD 評価なら 10Y UST、JPY 評価なら 10Y JGB。**評価通貨と一致させる** (§1.10 参照) |
| β_levered | レバレッジド・ベータ | 公開類似会社のアンレバード・ベータ平均を、自社 D/E でリレバーした値 (§1.4.2) |
| ERP | 株式リスクプレミアム (Equity Risk Premium) | Damodaran implied ERP (US) が 2026年1月時点で約 4.23% (出所: aswathdamodaran.substack.com Data Update 2 for 2026)。Historical ERP は約 4–6% |
| CRP | カントリーリスクプレミアム | Damodaran ctryprem.xlsx 参照。**日本 (Moody's A1): CRP = 0.91%、Total ERP = 5.14% (2026-01-05 更新)** (出所: pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)。米国 mature ERP は 4.23%、これに 0.91% 加算で日本 ERP となる |
| λ | 当該企業の country exposure (0–1+) | 売上の地理的内訳で按分。グローバル企業は 1.0 未満も可。新興国エクスポージャがあれば加算 |
| SP | サイズプレミアム | Duff & Phelps (Kroll) の size premia tables 参照。Decile-based で micro-cap だと +3〜+5% 程度 |
| ILP | 非流動性ディスカウント (実装は「ディスカウントを Re に加算」する方式と「結果の Equity Value から控除」する方式の2系統) | スタートアップで +2〜+5% が一般的。Restricted Stock Studies 由来 |

#### 1.4.2 Beta の推定 — スタートアップでの実務

スタートアップ自身の株価は存在しないため、Bottom-up beta (Damodaran) を使う:

```
1. 公開類似会社 (comp set) を 5〜10 社選定
2. 各社の levered beta (regression beta) を取得 (Bloomberg / Capital IQ / Yahoo Finance)
3. アンレバード化:  β_unlevered = β_levered / [ 1 + (1 − t) × (D/E) ]
4. 平均または中央値を取る
5. 自社の目標 D/E でリレバー: β_levered_self = β_unlevered_avg × [ 1 + (1 − t_self) × (D/E_self) ]
```

スタートアップは現状 D/E ≈ 0 でも、**長期目標 capital structure (mature D/E)** でリレバーするのが McKinsey / Damodaran 流。終局的に WACC が一定になる前提を整合させる。

**Beta 推定の落とし穴 (§15.1 で詳細):**
- 流動性が低い類似会社の regression beta は thin trading でバイアス (Scholes-Williams, Dimson 修正で対応)
- 5年 monthly が標準だが、ビジネスモデル激変期は 2年 weekly でも可
- 業界 beta (Damodaran industry betas) を使うとサンプル数が確保できる

#### 1.4.3 Cost of Debt の推定

```
Rd_pre_tax = Rf + Default Spread (synthetic rating ベース)
Rd_after_tax = Rd_pre_tax × (1 − t)
```

スタートアップが debt facility を持たない / 持っていても off-market な金利の場合、Damodaran の **synthetic rating** を使う:

```
1. Interest Coverage Ratio = EBIT / Interest Expense を計算
2. Damodaran ratings.xls の閾値表で synthetic rating を求める
   (例: ICR > 8.5 → AAA, 6.5–8.5 → AA, ..., < 0.5 → D, 等)
3. その rating の default spread を加算
```

**スタートアップで EBIT が負の場合:** ICR が定義不能 / 負。Damodaran は「revenue size でプロキシする small firm rating table」を提案 (smallrating.htm)。または同業 mature 企業の rating を当てて感度分析。

(出所: pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ratings.html)

#### 1.4.4 ウェイトは Market Value 基準で

E と D は **市場価値 (market value)** で測る。簿価ではない。Equity の market value がない (private) 場合は、最新ラウンド post-money、または DCF/comp の self-consistent な値を使う iterative solve。

#### 1.4.5 スタートアップ向けステージ別ディスカウントレート

CAPM-WACC は mature firm 向けに最適化されている。Pre-revenue / Series A/B では VC が要求する IRR を反映した stage-appropriate discount rate を使うのが実務 (§4 参照)。Damodaran も "Valuing Young Firms" で言及:

| ステージ | 期待 IRR レンジ (年率) | 主な根拠 |
|---|---|---|
| Seed / Idea | 50–70% | 失敗確率 60–70%, モデル不確実性極大 |
| Series A | 40–60% | PMF 仮説検証フェーズ |
| Series B | 30–50% | スケール初期 |
| Series C | 25–40% | スケール中期 |
| Bridge / Pre-IPO | 20–30% | ほぼ unit economics 確定 |
| Mature | 10–15% | 標準 WACC レンジ |

(出所: Damodaran "Valuing Young, Start-up and Growth Companies"; 数値はレンジ目安、当該案件の risk factor で調整)

**Survival probability adjustment (Damodaran):** 高 IRR の代わりに、**期待 CF 自体を survival probability で確率加重**する方式もある。`E[Value] = p_success × Value_success + (1 − p_success) × Liquidation Value` の形。これだと割引率は mature WACC が使え、二重カウントを防げる。**stage-appropriate discount と probability-weighting を同時に使うのは原則 NG** (バイアス重複)。

### 1.5 予測期間 (Forecast Period)

- **5年 (短期):** mature 業界、CF が安定。トラッカブルな経営計画と整合させやすい。
- **10年 (標準):** 成長企業のデフォルト。Mature 状態への遷移を明示的に描ける。
- **15–20年 (長期):** R&D pipeline、インフラ、SaaS で TAM が大きく long-tailed な場合。Terminal value 比率の暴走を抑える効果。

判定基準: 「予測期間末で当該企業が steady state (定常状態) に入っているか」。Steady state とは:
- 売上成長率 ≤ 経済成長率
- ROIC ≈ WACC または安定的な spread
- 再投資率 (reinvestment rate) が CF 成長と整合

これを満たさないなら期間延長。**Terminal value が EV の 75% 超** (§15.2) なら期間延長を検討する黄信号。

### 1.6 Terminal Value (継続価値)

#### 1.6.1 Gordon Growth Model (永続成長モデル)

```
TV_n = FCFF_(n+1) / (WACC − g)
     = FCFF_n × (1 + g) / (WACC − g)
```

| 変数 | 説明 |
|---|---|
| g | 永続成長率 (perpetual growth rate) |
| FCFF_(n+1) | 予測期間翌年 (steady state 1年目) の FCFF |

**g の選び方 (硬性制約):**
- `g ≤ 評価通貨の long-term GDP growth rate`
- USD 名目: 概ね **2.0–2.5%** 上限
- JPY 名目: 概ね **0.5–1.5%** 上限
- `g ≤ Rf` (リスクフリーレート、Damodaran 厳格ルール)
- 保守的には **2% 前後**を上限とする

**Reinvestment rate の整合:**
```
g = ROIC × Reinvestment Rate
Reinvestment Rate = (CapEx + ∆NWC − D&A) / [EBIT × (1 − t)]
```

g を高く置くなら、その分 Reinvestment Rate を上げ、TV の分子 FCFF を下げる必要がある。「成長率だけ高く、CF も多い」は不整合 (§15.7 stack-up bias)。

#### 1.6.2 Exit Multiple Method

```
TV_n = Metric_n × Exit Multiple
```

- Metric: EBITDA, Revenue, ARR, EBIT 等
- Exit Multiple: comparable trading / transaction multiples のレンジ

スタートアップでは **EV/Revenue, EV/ARR** が主流 (EBITDA がまだ意味を持たないため)。

**Implied growth rate のクロスチェック (必須):**
Exit multiple から Gordon を逆算し、g_implied を出して妥当性を検証:

```
Exit Multiple = (1 − Reinvestment Rate) / (WACC − g_implied)
→ g_implied = WACC − (1 − Reinv) / Exit Multiple
```

g_implied が GDP 成長率を超えていたら exit multiple が過大 (= TV 過大)。

#### 1.6.3 両手法のクロスチェック原則

| 観点 | Gordon | Exit Multiple |
|---|---|---|
| 強み | 長期 growth に直接連動、理論整合 | Market-grounded、現実感 |
| 弱み | g 感度が大きい、永続前提 | Multiple cycle に左右される |
| 実務 | 主要 (理論的) | クロスチェック (market sanity) |

**dual verification ルール:** Gordon と Exit Multiple の両方で TV を計算し、両者が ±20% 以内に収まることを確認。乖離が大きければ `g`、`WACC`、`exit multiple` のどれかを再検討。

**Tiebreak (乖離 >20% 時のルール、E-H-011 解消):**
- Y_n が真の steady state (margin 横ばい、growth ≤ g、reinvestment = g/ROIC で整合) なら **Gordon を主、Exit Multiple は sanity check** とする (理論整合優先)。
- Y_n に >5pt の growth premium が残っているなら、forecast 期間を 5 年延長して Y_{n+5} で再評価。**両者の単純平均は使わない** (理論的に defensible でない)。
- Gordon と Exit Multiple をどちらも提示する場合は、必ず「主、副」の関係を明示し、平均値は出さない。

### 1.7 Mid-year convention (中間期間規約)

標準 DCF は year-end (期末一括 CF) を仮定。実際は CF が年間を通じて発生するため、**0.5年分前倒し** の方が現実的:

```
PV (year n, mid-year) = CF_n / (1 + WACC)^(n − 0.5)
```

または同等に: `PV_year-end × (1 + WACC)^0.5`

実務インパクト: WACC 10% で約 5% の valuation アップ。Sell-side、特に banker model で標準。Buy-side でも明示すべき。

### 1.8 Stub period adjustment (端数期間調整)

評価日が会計年度の途中 (例: 11/15) の場合、当該年度の残り期間 (stub) を別建てで割引く:

```
Stub fraction = 残日数 / 365 (例: 11/15 評価、12/31 期末 → 46 / 365 ≈ 0.126)
PV (stub CF) = CF_full_year × stub fraction / (1 + WACC)^(stub fraction / 2) (mid-stub 規約)
```

その後、翌年以降の full year CF を t = stub fraction + 0.5, 1.5, ... で割引く (mid-year + stub)。

### 1.9 通貨・インフレ整合性 (Real vs Nominal)

**鉄則:** 同じ DCF の中では、CF と割引率 (WACC) を **同じ通貨・同じインフレ前提** で揃える。

| パターン | CF 単位 | WACC | 用途 |
|---|---|---|---|
| Nominal (標準) | 名目 (インフレ込み) | 名目 (Rf に名目国債) | デフォルト |
| Real | 実質 (インフレ控除済み) | 実質 (Rf に実質金利、TIPS など) | 高インフレ国、長期インフラ |

**多通貨企業のクロスボーダー DCF:**
- 売上が複数通貨に跨る場合、各通貨で別 DCF を組み、それぞれの WACC で割引いてから現在通貨へ FX で換算
- 単一通貨に強引に集約するなら、forward FX で予測 CF を換算 (interest rate parity 整合)

### 1.10 Reverse DCF (逆 DCF)

現在の市場価格が前提とする growth/margin の暗示値を逆算する手法。投資判断の sanity check に有用:

```
1. 現在の Equity Value (= Market Cap、private なら直近ラウンド post-money)
2. WACC を確定
3. Forecast period & terminal year を仮定
4. 既知のパラメータ (現状 EBIT margin, 再投資率) を入れる
5. 残りの未知 (revenue growth rate, terminal margin) を Goal Seek
6. その implied 値が「達成可能か」を比較分析、業界ベンチマークと照合
```

例: 直近ラウンドで $1B post の SaaS スタートアップが、reverse DCF で「今後 7年間 CAGR 80% かつ terminal EBITDA margin 35% を要求している」と判明 → 実現可能性を critically review。

---

### 1.11 ミニケース 1: Series B SaaS の DCF + WACC 完全構築

**設定:**
- 日本本社・北米拡大中の B2B SaaS
- 評価通貨: USD (調達も売上も USD 比率高)
- 直近 LTM ARR: $25M、YoY 80%
- Gross margin 78%、現状 EBIT margin: −20%
- Net cash position $30M (no debt)、D/E 目標 = 0 で運営見込み (equity-financed)
- 評価日: 2026-01-31

**前提構築:**
- 予測期間: 10年 (Y1–Y10)、その後 terminal
- ARR growth path: Y1 80%, Y2 65%, Y3 50%, Y4 38%, Y5 28%, Y6 22%, Y7 17%, Y8 13%, Y9 10%, Y10 7%
- EBIT margin path: Y1 −15%, Y2 −5%, Y3 5%, Y4 12%, Y5 18%, Y6 22%, Y7 25%, Y8 27%, Y9 28%, Y10 28%
- Terminal: g = 2.0% (USD 名目 GDP 上限近傍)、terminal EBIT margin = 28%、terminal reinvestment rate = g / ROIC (ROIC を mature SaaS の 25% と仮定 → reinvest = 8%)
- Tax rate 25% (米連邦+州ブレンド)
- D&A: 売上の 4%、CapEx: 売上の 3%、∆NWC: 売上増の 5%
- SBC: 売上の 12% (Y1) → 6% (Y10)、§15.5 ルールにより EBIT から戻し入れず費用扱い

**WACC 構築 (Y10 時点 mature 状態):**
- Rf (USD 10Y UST、2026-01 時点目安): 4.0%
- ERP (Damodaran implied, 2026-01): 4.23%
- Bottom-up β: 公開 SaaS comp (Snowflake, Datadog, MongoDB, HubSpot, Zscaler, CrowdStrike) の unlevered β 平均 ≈ 1.10
- 目標 D/E 0% → levered β = 1.10
- Size premium (small-mid SaaS, Kroll Decile): +1.5% (mature 後は不要かもだが保守的に残す)
- Illiquidity premium: 段階的 (early: +3%, mature: 0%)
- Country exposure: US 70% / Japan 20% / EU 10%、CRP 加重 ≈ 0.2%

**Cost of Equity (mature):**
```
Re_mature = 4.0% + 1.10 × 4.23% + 0.2% + 1.5% + 0% ≈ 10.4%
```

D = 0 想定なので WACC_mature ≈ Re_mature ≈ 10.4%

**Stage adjustment (predictive period 中):**
- Y1–Y3: Seed/A 残滓を考慮し +5% premium → 約 15.4%
- Y4–Y6: Series B 標準 → 12.5%
- Y7–Y10: Mature 移行 → 10.4%

または **VC method 的に Y1–Y3 は 30%、それ以降 mature 10.4% という二段ロケット** も実務的。本ケースでは段階的低減 (15.4 → 12.5 → 10.4) を採用。

**FCFF 抜粋 (USD M):**

| Year | Revenue | EBIT | EBIT × (1−t) | + D&A | − CapEx | − ∆NWC | FCFF |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Y1 | 45 | −6.8 | −5.1 | 1.8 | 1.4 | 1.0 | −5.7 |
| Y2 | 74 | −3.7 | −2.8 | 3.0 | 2.2 | 1.5 | −3.5 |
| Y3 | 111 | 5.6 | 4.2 | 4.4 | 3.3 | 1.9 | 3.4 |
| Y4 | 153 | 18.4 | 13.8 | 6.1 | 4.6 | 2.1 | 13.2 |
| Y5 | 196 | 35.3 | 26.5 | 7.8 | 5.9 | 2.2 | 26.2 |
| Y6 | 239 | 52.6 | 39.5 | 9.6 | 7.2 | 2.2 | 39.7 |
| Y7 | 280 | 70.0 | 52.5 | 11.2 | 8.4 | 2.1 | 53.2 |
| Y8 | 316 | 85.3 | 64.0 | 12.6 | 9.5 | 1.8 | 65.3 |
| Y9 | 348 | 97.4 | 73.1 | 13.9 | 10.4 | 1.6 | 75.0 |
| Y10 | 372 | 104.2 | 78.2 | 14.9 | 11.2 | 1.2 | 80.7 |

**Terminal Value (Gordon):**
```
FCFF_(Y11) = 80.7 × 1.02 = 82.3
TV_(Y10)  = 82.3 / (10.4% − 2.0%) = 82.3 / 8.4% ≈ 980
```

**Terminal Value (Exit Multiple) クロスチェック:**
- Y10 ARR 372、SaaS mature multiple EV/ARR ≈ 6× (2026 Q1 公開 SaaS median: 6.4×, 出所: SaaS Capital Index) → TV ≈ 2,232
- これは Gordon の 980 の **約 2.3 倍** で大きく乖離。**乖離原因の解釈:**
  - Gordon の 8.4% denominator が thin (g を 2.5% に上げると 980 → 1,250 と動く)
  - Exit multiple は market が織り込む growth premium を含む (Y11 以降も成長と織り込んでいる)
  - 本ケースでは Y10 で「成熟」と置きすぎた可能性。**予測期間を 12 年に延長して Y11–Y12 の高成長を明示**するか、Gordon の g を 3.0% (上限超過要注意) にする選択
- 実務判断: 両者の **中点 ≈ 1,600** または「TV range 980–2,232」として TV uncertainty を価格レンジで表現

**現在価値計算 (Mid-year convention 適用、段階別 WACC):**

段階別の WACC: Y1–Y3 = 15.4%、Y4–Y6 = 12.5%、Y7–Y10 = 10.4%。Mid-year convention により、Y_n の CF は t = n − 0.5 で割引く。**ただし WACC が段階別なので、累積割引ファクタは段階を渡って合成する必要がある**。

**Cumulative Discount Factor (mid-year, segmented WACC) の構築:**

Y1 (t=0.5): DF₁ = 1 / (1.154)^0.5 = 1 / 1.0744 = 0.9308
Y2 (t=1.5): DF₂ = 1 / (1.154)^1.5 = 1 / 1.2398 = 0.8066
Y3 (t=2.5): DF₃ = 1 / (1.154)^2.5 = 1 / 1.4307 = 0.6989
(Y3 末時点の cumulative WACC factor = 1.154^3 = 1.5358)

Y4 (t=3.5): DF₄ = 0.6989 / (1.125)^1.0 × (1.125)^0.5 = ... より厳密には:
- Y3 末から Y4 mid-year までの追加期間 = 0.5 年 + 0.5 年 = 1.0 年 (Y4 mid-year)
- DF₄ = 1 / [1.154^3 × 1.125^(0.5+0.5)] = 1 / [1.5358 × 1.125^1.0] = 1 / 1.7278 = 0.5788
- 検算: Y3 mid → Y4 mid 間隔 1.0年で WACC 12.5% 適用、つまり DF₄ = DF₃ / 1.125^1 を期待→ 0.6989/1.125 = 0.6212 ≠ 0.5788

実用的には **段階間で累積 factor を receipt-by-receipt に積み上げる** のがクリーン。以下、各 Y のキャッシュ受領時点 (mid-year) の累積 discount factor を整数ステップで構築:

| Year | t (mid) | 当期間 WACC | 累積 DF (mid-year) | 計算根拠 |
|---:|---:|---:|---:|---|
| Y1 | 0.5 | 15.4% | 0.9308 | 1 / 1.154^0.5 |
| Y2 | 1.5 | 15.4% | 0.8066 | 1 / 1.154^1.5 |
| Y3 | 2.5 | 15.4% | 0.6989 | 1 / 1.154^2.5 |
| Y4 | 3.5 | 12.5% (Y4) | 0.6212 | 0.6989 / 1.125 |
| Y5 | 4.5 | 12.5% (Y5) | 0.5522 | 0.6212 / 1.125 |
| Y6 | 5.5 | 12.5% (Y6) | 0.4908 | 0.5522 / 1.125 |
| Y7 | 6.5 | 10.4% (Y7) | 0.4445 | 0.4908 / 1.104 |
| Y8 | 7.5 | 10.4% | 0.4027 | 0.4445 / 1.104 |
| Y9 | 8.5 | 10.4% | 0.3647 | 0.4027 / 1.104 |
| Y10 | 9.5 | 10.4% | 0.3303 | 0.3647 / 1.104 |
| TV @ Y10 | 10.0 | 10.4% | 0.3144 | 0.3303 / 1.104^0.5 (TV を Y10 期末で受領と仮定) |

**PV 計算 (USD M):**

| Year | FCFF | DF | PV |
|---:|---:|---:|---:|
| Y1 | −5.7 | 0.9308 | −5.31 |
| Y2 | −3.5 | 0.8066 | −2.82 |
| Y3 | 3.4 | 0.6989 | 2.38 |
| Y4 | 13.2 | 0.6212 | 8.20 |
| Y5 | 26.2 | 0.5522 | 14.47 |
| Y6 | 39.7 | 0.4908 | 19.49 |
| Y7 | 53.2 | 0.4445 | 23.65 |
| Y8 | 65.3 | 0.4027 | 26.30 |
| Y9 | 75.0 | 0.3647 | 27.35 |
| Y10 | 80.7 | 0.3303 | 26.66 |
| **PV(FCFF) sum** |  |  | **140.4** |
| TV (Gordon) | 980 | 0.3144 | 308.1 |
| **Enterprise Value** |  |  | **448.5** |

**Equity Value:** EV + Cash − Debt = 448.5 + 30 − 0 = **$478.5M**

**Sanity check:**
- 現在 ARR $25M に対し Equity / ARR = 478.5 / 25 = 19.1× → 公開 SaaS premium tier (Rule of 40 高位、growth 80% × margin −20% = 60 → 50 超で premium tier、出所: SaaS Capital, Rule of 40 多寡で multiple ±1.1×/10pt)
- TV / EV 比率 = 308 / 448.5 ≈ 69% → §15.2 警戒値 (75% 未満だが高め)。期間延長 or TV 二刀流提示で risk-flagging
- 同 EV を Y10 ARR ($372M) で割ると implied EV/Y10 ARR = 448.5 / 372 = 1.2×、TV 単独で = 980 / 372 = 2.6× → これが Y10 時点での implied EV/ARR = 980/372 と整合し、SaaS mature multiple 6× より大幅に低い → Gordon の保守的さを反映

**Sensitivity Table 1: Mature WACC × Terminal g (TV と Equity Value の感度)**

| Mature WACC \ g | g = 1.0% | g = 2.0% (base) | g = 3.0% |
|---:|---:|---:|---:|
| WACC = 8.4%  | 1,124 / 562 | 1,288 / 614 | 1,506 / 683 |
| WACC = 10.4% (base) | 838 / 412 | **980 / 478.5** | 1,153 / 533 |
| WACC = 12.4% | 663 / 327 | 754 / 365 | 859 / 408 |

(各セル: TV / Equity Value、USD M)

**観察:**
- WACC ±2pt で Equity Value ±15–20%、g ±1pt で ±10%。両者で +30% / −25% の幅
- Equity Value range $327M(下限) – $683M(上限)、ターゲットレンジ centered on $478M
- WACC は β、ERP、CRP すべて連動するため、WACC を 1pt 動かすには CAPM 構成要素を再走するべき

**Sensitivity Table 2: Y10 EBIT margin × Terminal Reinvestment Rate**

| Margin \ Reinv | Reinv = 5% | Reinv = 8% (base) | Reinv = 12% |
|---:|---:|---:|---:|
| 23% (low) | 401 | 388 | 372 |
| 28% (base) | **496** | **478.5** | **456** |
| 33% (high) | 590 | 568 | 540 |

(各セル: Equity Value、USD M)

**インサイト:**
- TV が EV の 69% を占める時点で、本 DCF は実質的に「Terminal multiple モデル + 短期 CF」。Reverse DCF で「市場が織り込む暗黙の Y10–Y20 growth」を可視化する追加分析が必要
- WACC 段階別の取り扱い (15.4 → 12.5 → 10.4%) を全 mature WACC 一定 (10.4%) に変えると EV ≈ $610M (+27%)。本ケースは stage premium 反映で保守的

**Stage-segmented vs Mature WACC — 使い分けルール (E-H-014 解消、+27% delta は意思決定 critical):**

| Audience / 用途 | 推奨 | 理由 |
|---|---|---|
| Pre-IPO IC pitch | **Stage-segmented (default)** | early stage の execution risk を反映、保守的 base case |
| Public-comp 比較 / Sell-side comp set | Mature WACC 一定 | comp set 自体が mature multiple なので整合 |
| Founder 内部の go/no-go | Stage-segmented | 楽観バイアス排除 |
| LP / Fund-level Reporting | 両方併記 | range で示す (audit defensibility) |

**両方を提示する場合は必ず「+27% gap が WACC 仮定差に起因」と説明**する。説明なしの平均値提示 (= $1,600M / $610M を averaging) は理論的に defensible でないため避ける。

---

## 2. Comparable Company Analysis (Trading Comps)

### 2.1 理論的位置づけ

「市場が、似た会社をどう値付けしているか」を観察し、それを当該企業に適用する手法。**Market-implied valuation** であり、絶対的な intrinsic value とは異なる (相対値)。

**強み:** 市場参加者の集合知反映、計算高速、IC で広く受容される
**弱み:** 市場全体のバブル / クラッシュ局面では誤誘導 (2021 SaaS multiple bubble → 2022 半減、等)、適切な comp 集合の選定が困難

### 2.2 Comp Set 選定基準

以下を満たす公開会社 5–15 社が望ましい:

| 軸 | 基準 |
|---|---|
| Business model | 同一カテゴリ (SaaS / marketplace / fintech / hardware-enabled SaaS 等) |
| Size | 売上 / 時価 1/3〜3倍 程度に収まる (収まらないなら size premium で調整) |
| Growth profile | YoY revenue growth ±10%pt 以内が理想 |
| Profitability | 同 stage (赤字 vs 黒字、Rule of 40 帯) |
| Geography | 主要市場の重複 (US, JP, EU, APAC) |
| Capital structure | レバレッジ水準が大きく異なるなら EV 系 multiple で吸収 |
| Liquidity | Daily trading volume / float が一定 ($10M 日次以上が望ましい) |

**最小 comp 数:** 経験則 5 社以上。3 社以下なら multiple の median が不安定。

### 2.3 LTM vs NTM vs CY+1 — 時点の整合

| 表記 | 意味 |
|---|---|
| LTM (Last Twelve Months) | 直近 4 四半期合計 (trailing) |
| NTM (Next Twelve Months) | 今後 12 か月予想 (forward) |
| CY+0, CY+1, CY+2 | 暦年単位の Year 0 (現年), +1, +2 |
| FY+1 | 会計年度ベースの翌期 |

**鉄則:** Comp set 内で **同じ時点定義**を使う。LTM と NTM を混ぜない。**MIX すると 20–40% のバイアス**を生む可能性 (高成長 SaaS で NTM 利用すると multiple は LTM の 60–70% に縮む)。

実務標準:
- 高成長 SaaS / startup: NTM Revenue または NTM ARR
- Mature: LTM EBITDA, LTM EBIT
- 二刀流 (両方計算しレンジ提示)

### 2.4 主要マルチプル — 計算式と適用条件

| マルチプル | 計算 | 主用途 | 留意 |
|---|---|---|---|
| EV / Revenue | EV / Revenue | High growth (negative EBITDA) | Margin 構造を無視するため要レンジ感 |
| EV / ARR | EV / ARR (SaaS) | SaaS / subscription | Backlog/RPO の扱いを統一 |
| EV / EBITDA | EV / EBITDA | Mature | SBC を費用扱いした調整 EBITDA で |
| EV / EBIT | EV / EBIT | D&A intensity 差を調整したい時 | |
| EV / GMV | EV / GMV | Marketplace | take rate 差で multiple が大きく変動 |
| P / E | Price / EPS | Mature equity-only | Capital structure 影響残る |
| PEG | P/E / Growth (%) | Growth comparable | Growth の単位 (%, %pt) 注意 |
| P / B | Price / Book | Banking, financial | テック事業には不適 |
| EV / FCF | EV / FCF | Capital-light mature | 一過性 CF に注意 |

### 2.5 Calendarization (会計年度の調整)

複数の comp が異なる FY (例: 12月決算と3月決算が混在) を持つ場合、すべて同じ calendar period (例: CY2026E) に揃える:

```
Calendarized FY+1 = (残月数 / 12) × 自社 FY+1 + (経過月数 / 12) × 自社 FY+2
```

例: 評価日 2026-04-30、3月決算企業 → CY2026E = 8/12 × FY2027 + 4/12 × FY2026

これを怠ると、3 月決算 / 12 月決算 / 6 月決算が混在した comp set で `EV / FY+1 Revenue` が比較不能になる。

### 2.6 Diluted Share Count — Treasury Stock Method

EV の Equity 部分で使う share count は **diluted (希薄化後)**。Treasury Stock Method:

```
1. ITM (in-the-money) options/warrants/RSU の数を集計
2. 行使価格 × 数量 = "exercise proceeds" を会社が受け取る
3. その proceeds で株を買い戻す (treasury) と仮定
4. Net 増加株数 = ITM 数 − 買い戻し株数
   = ITM 数 − (ITM × strike) / current stock price
   = ITM × (1 − strike / current price)
5. Diluted shares = Basic + Net dilution
```

転換社債 (CB) は **if-converted method** で、ITM な転換価格なら株式に置換し利息を加算戻し。

### 2.7 Net Debt の計算 (細部の罠)

```
Net Debt = Total Debt
         − Cash & Equivalents
         + Preferred Stock (if mandatorily redeemable, debt-like)
         + Minority Interest (Non-Controlling Interest)
         + Underfunded Pension Liabilities
         + Operating Lease (IFRS 16 / ASC 842 reclass)
         − Investments in associates (if non-operating)
```

スタートアップ特有:
- **SAFE / Convertible note:** 未転換段階では実質 equity-like だが、IFRS では負債計上されることがある。Discount/Cap 込みで dilution の TSM に含めるのが実務
- **Preferred stock with liquidation preference:** participating / non-participating で扱い変動。OPM/PWERM (§13) でアロケーション

### 2.8 Outlier 除外と Median vs Mean

- **Outlier 検出:** 中央値 ± 2σ、または IQR (Interquartile Range) × 1.5 を超える値
- **Median を主に使う** (mean はスター企業に引っ張られる)
- ただし comp 数が 5–7 と少ない場合、median と mean の両方を提示

### 2.9 Football Field Chart (バリュエーションレンジ可視化)

横軸: Equity Value (または EV)、縦軸: 手法・マルチプル種別。各手法の min/max を bar で描画し、**重なる帯**を target valuation range とする。

サンプル構成:
```
DCF (Bear / Base / Bull)               |======|
DCF Sensitivity (WACC 8–13%, g 1–3%)  |==========|
Trading Comps EV/NTM Revenue (5–9×)    |========|
Trading Comps EV/NTM EBITDA (15–25×)   |======|
Precedent Transactions (M&A 25–40 prem)    |======|
52-Week High/Low (公開なら)               |==|
直近ラウンド post-money                       |=|
```

中央付近で複数手法が重なるレンジ → IC の推奨価格帯。

### 2.10 ミニケース 2: Marketplace スタートアップの Trading Comps + Calendarization

**設定:**
- 日本の B2C marketplace (中古品)
- LTM GMV ¥80B、Take rate 8%、LTM Revenue ¥6.4B、LTM EBITDA ¥0.6B (margin 9%)
- 直近 12M growth: GMV +35%、Revenue +40%、Adjusted EBITDA +60%
- 評価日 2026-04-30、評価通貨 JPY、3月決算 → CY2026E = 9/12 × FY2027 + 3/12 × FY2026

**Comp set:**

| 会社 | FY 末 | LTM Revenue | NTM Revenue | EV (M) | LTM Take Rate | EV/NTM Rev | EV/NTM GMV |
|---|---|---:|---:|---:|---:|---:|---:|
| eBay | 12月 | $10.2B | $10.8B | $26B | ~12% | 2.4× | 0.29× |
| Etsy | 12月 | $2.8B | $3.0B | $7.5B | ~22% | 2.5× | 0.55× |
| Mercari (JP) | 6月 | ¥190B | ¥210B | ¥350B | ~10% | 1.7× | 0.17× |
| Allegro (PL) | 12月 | PLN 11.5B | PLN 13.0B | PLN 50B | ~10% | 3.8× | 0.38× |
| Coupang (incl 1P) | 12月 | $30B | $35B | $50B | mixed | 1.4× | n/a |
| Vinted (private) | n/a | non-public | n/a | n/a | n/a | n/a | n/a |

**Calendarization:** Mercari (6月決算) を CY2026E に直す:
```
CY2026E Revenue = (8 / 12) × FY2027(Jul'26–Jun'27) + (4 / 12) × FY2026(Jul'25–Jun'26)
```

**Outlier 除外と median:**
- Coupang は 1P 在庫モデル混在で除外
- eBay, Etsy, Mercari, Allegro の 4 社で集計
- EV/NTM Revenue median = (2.4 + 2.5 + 1.7 + 3.8) / 4 → median ≈ 2.45×、mean ≈ 2.6×
- EV/NTM GMV median = (0.29 + 0.55 + 0.17 + 0.38) → median ≈ 0.34×

**自社評価:**
- 自社 NTM Revenue ≈ ¥6.4B × (1 + 0.40) ≈ ¥9.0B (CY2026E 計算上、概算)
- 自社 NTM GMV ≈ ¥80B × 1.35 ≈ ¥108B
- EV (Revenue base) = 2.45× × ¥9.0B = **¥22.0B**
- EV (GMV base) = 0.34× × ¥108B = **¥36.7B**

**乖離の解釈:**
- Take rate が 8% と comp 中央値 (10–12%) より低い → GMV multiple は割引が必要
- 補正: 8% / 11% (median take rate) = 0.73 倍を GMV multiple に適用 → 0.34× × 0.73 = 0.25× → EV ≈ ¥27B
- Revenue base ¥22B と Take-rate 補正 GMV base ¥27B → range ¥22–27B

**Football Field 提示用レンジ:** ¥20–30B (DCF クロスチェック後の central は別途算出)

**典型的失敗:**
- LTM と NTM を混ぜて 1 社 LTM、3 社 NTM で multiple を計算 → 自動 +20% バイアス
- 1P/3P 混在企業を入れる (本ケースでは Coupang 除外で対処)
- Take rate を均一 と仮定 (本来は GMV multiple を take rate で調整必要)

---

## 3. Precedent Transactions Analysis (類似取引比較法)

### 3.1 概要

**過去の M&A 取引価格** から multiple を抽出し、自社へ適用する手法。Trading Comps が「市場の毎日の評価」なのに対し、Precedent は「**control を含めた支配権 transaction の評価**」。

### 3.2 案件選定基準

| 軸 | 基準 |
|---|---|
| Industry | 同一サブセクター |
| Time | 直近 3–5年 (multiple cycle に注意) |
| Deal size | 同サイズ感 |
| Buyer type | Strategic vs Financial (PE) を区別 |
| Geography | 同一/類似市場 |
| Strategic rationale | 公開された rationale (synergy, market entry, talent acq.) |

### 3.3 Control Premium

公開会社買収では市場価格に対し **25–40%** の premium が支払われるのが典型 (米国実証研究: Mergerstat, BVR データ)。Strategic synergy が大きい案件ほど premium 高い。

```
Implied EV (control) = Market EV × (1 + Control Premium)
```

スタートアップ M&A では「公開価格」が存在しないため、最終ラウンド post-money に対する premium という形で議論される。

### 3.4 Synergy 控除

買収者は synergies を価値の一部として支払う。**自社 standalone valuation には synergy 分を含めない**:

```
Standalone Value = Transaction Value − PV(Synergies) − Control Premium
```

ただし synergies は買い手特有 (buyer-specific) のため、自社 valuation 適用時は除外。

### 3.5 Strategic vs Financial Buyer

| 軸 | Strategic | Financial (PE/VC) |
|---|---|---|
| 価格 | 高い (synergy 反映) | 抑制的 (IRR 制約) |
| Multiple | 高め | やや低め |
| Time horizon | 永続 | 5–7年 exit |
| Synergy | あり (cost / revenue) | 限定的 (operational improvements) |

スタートアップの potential acquirer 想定で multiple ベンチを使い分け。

### 3.6 データソース

| ソース | 強み | 弱み |
|---|---|---|
| S&P Capital IQ | 全業種カバー、調整済財務 | 高額、要契約 |
| Refinitiv (旧 Thomson) | M&A データ深い | UI 古い、要契約 |
| MergerMarket | M&A 専門、rumor 含む | 価格情報限定的 |
| Pitchbook | VC/PE / startup 取引 | 発表ベース、未確認多い |
| Crunchbase | スタートアップ取引、無料 tier あり | 確度・正確性に幅 |
| INITIAL (Japan) | 国内スタートアップ取引 | 国内中心 |
| 公開 8-K / S-4 / 有報 | 一次資料、infaltable | 個別案件のみ |
| KPMG / EY VC pulse | 集計データ、四半期更新 | 個別案件は粗い |

### 3.7 案件 Staleness の調整

3年以上前の取引は market regime が異なる (e.g., 2021 SaaS 取引 multiple は 2024–2025 に半減)。**Time-weighted median** や public market multiple change を当てて再調整:

```
Adjusted Past Multiple = Past Multiple × (Current Public Multiple Median / Past Public Multiple Median at Deal Date)
```

---

## 4. VC Method / First Chicago Method

### 4.1 VC Method 標準形

**Pre-money / Post-money** の関係:

```
Post-money = Pre-money + Investment Amount
% Ownership (new investor) = Investment / Post-money
```

VC の意思決定式:

```
Required Post-money (today) = Exit Value at Year n / (1 + Required IRR)^n
Pre-money = Required Post-money − Investment
```

または **Probability-weighted exit:**

```
Post-money = E[Exit Value] / (1 + Required IRR)^n
E[Exit Value] = Σ p_i × Exit_i (各シナリオ)
```

### 4.2 Required IRR (年率) — Stage 別

(出所: Damodaran "Valuing Young, Start-up and Growth Companies"; Sahlman HBS framework)

| Stage | 期待 IRR (年率) | Multiple over 5–7yr (concept) |
|---|---|---|
| Seed | 60–80%+ | 10× over 5y |
| Series A | 40–60% | 7–10× |
| Series B | 30–50% | 5–7× |
| Series C | 25–40% | 4–5× |
| Pre-IPO / Bridge | 20–30% | 2–3× |
| Mature / Buyout (PE) | 20–25% | 2.5× |

これらは「VC ファンド全体の目標 IRR (top-quartile 25%+) と、各個別 deal の **survival-weighted required IRR** の差」を反映している。Damodaran 流の **survival probability** で割り戻す方式と等価。

### 4.3 Backsolve (直近ラウンドからの逆算)

直近 priced round が手元にある場合、その post-money を **anchor** として使う:

```
Backsolve Equity Value = Latest Post-money
↓ (OPM/PWERM で各 share class へ allocation)
Common Stock FMV (= 409A 評価額)
```

(§13 で詳細)

### 4.4 First Chicago Method (3 シナリオ加重)

Best / Base / Worst の 3 シナリオを設定し、各シナリオで:

```
Scenario Value = Exit Value × p_scenario / (1 + r)^n
Final Pre-money = Σ Scenario Value − Investment
```

| Scenario | Probability (typical) | Exit Multiple | 用途 |
|---|---|---|---|
| Best (home run) | 10–25% | 20× | IPO 大成功 |
| Base | 40–60% | 5× | 標準成長後 strategic exit |
| Worst | 25–50% | 0.5× | Down round / 清算 |

**Bias 注意:** 確率合計 = 1.0 を保つこと。確率を 100% 超で best 寄りに置くと自動的に過大評価。

### 4.5 ミニケース 3: Series A の VC Method backsolve

**設定:**
- 日本のヘルスケア SaaS、Series A 募集中
- 調達額 ¥500M
- 5年後 exit 想定 (IPO or M&A)
- 3 シナリオ:
  - Best (確率 20%): Exit value ¥30B (5y CAGR 業界 multiple top tier)
  - Base (確率 50%): Exit value ¥10B
  - Worst (確率 30%): Exit value ¥1B (acquihire)
- Required IRR (Series A): 50%

**計算:**
```
E[Exit] = 0.20 × 30 + 0.50 × 10 + 0.30 × 1 = 6.0 + 5.0 + 0.3 = ¥11.3B
PV = 11.3 / (1.50)^5 = 11.3 / 7.59 = ¥1.49B
Post-money (today) = ¥1.49B
Pre-money = 1.49 − 0.50 = ¥0.99B  ≈ ¥1.0B
新規投資家持分 = 500 / 1,490 = 33.6%
```

**感度:**
- IRR 40% に下げると post-money = 11.3 / 5.38 = ¥2.10B (+41%)
- Best 確率を 30% に上げると E[Exit] = 0.30×30 + 0.50×10 + 0.20×1 = 14.2 → post-money = ¥1.87B
- Best シナリオ exit を ¥40B に上げると E[Exit] = 0.20×40 + ... = 13.3 → post-money = ¥1.75B

**典型的失敗:**
- Required IRR と probability-weight を二重に保守 (IRR 60% に置きながら confidence 最低の expected value も使う) → 過小評価バイアス
- Best シナリオの確率を直感で「30%」と置く (公開比較データを参照すべき。VC ファンドの DPI 分布から、Series A 投資の 20% が 5× 以上 return という Correlation Ventures 等のデータあり)
- Liquidation preference 構造を無視。**Worst case で清算優先株が effective return を変える**

---

## 5. Berkus Method (idea-stage)

Pre-revenue, pre-product startup 用の qualitative pricing モデル (Dave Berkus, 1990s)。**最大 $2.5M (or 該当通貨換算)** の上限。

| 評価軸 | 上限値 |
|---|---|
| Sound idea (basic value) | $0.5M |
| Prototype (technology risk reduction) | $0.5M |
| Quality management team (execution risk reduction) | $0.5M |
| Strategic relationships (market risk reduction) | $0.5M |
| Product rollout / sales (production risk reduction) | $0.5M |
| **合計上限** | **$2.5M** |

**強み:** 数値根拠ゼロのアイデア段階で defensible な pre-money を設定可能
**弱み:** 上限が硬い、地域・市場で実勢に合わない (シリコンバレーは $5–10M に拡張運用が普通)
**適用条件:** Idea–Pre-seed のみ。Series A 以降では使わない

---

## 6. Scorecard Method (Bill Payne)

地域 / 業界の median pre-money を anchor とし、案件特性で乗数調整:

| 軸 | Weight | 評価コメント |
|---|---|---|
| Strength of management team | 0–30% | 重要度高 |
| Size of opportunity | 0–25% | TAM |
| Product / Technology | 0–15% | 差別化 |
| Competitive environment | 0–10% | Moat |
| Marketing / Sales / Partnerships | 0–10% | GTM |
| Need for additional investment | 0–5% | Capital efficiency |
| Other | 0–5% | Misc |

**計算:**
```
Adjustment Factor = Σ (weight_i × score_i)  (score_i は 50%–200% など)
Pre-money = Median Regional Pre-money × Adjustment Factor
```

例: median ¥250M、Adjustment 1.20 → Pre-money ¥300M

**強み:** 地域実勢 anchor で sanity 高い
**弱み:** Median の取得に苦労、weight の主観性
**適用条件:** Pre-revenue / Seed〜Series A 早期

---

## 7. Risk Factor Summation Method

12 項目のリスクを ±0.5 ステップで評価し、**1 段階あたり地域中央値の ±$250–500K** を pre-money に加減算:

| Risk Factor |
|---|
| Management |
| Stage of business |
| Legislation / Political |
| Manufacturing |
| Sales and marketing |
| Funding / Capital raising |
| Competition |
| Technology |
| Litigation |
| International |
| Reputation |
| Potential lucrative exit |

各因子を `++` (very positive, +$500K) 〜 `−−` (very negative, −$500K) で評価し、median pre-money に加算。

**強み:** リスクの網羅性、議論の構造化
**弱み:** 12 項目 × 5 段階 = 60 通りの主観決定、再現性低い
**適用条件:** Berkus / Scorecard と組み合わせて triangulate

---

## 8. Real Options Valuation (リアルオプション評価)

### 8.1 概要

R&D pipeline、staged investment (e.g., biotech 第I相→第II相→第III相)、TAM 拡張オプションなど、**「将来の意思決定柔軟性に価値がある」状況** で DCF が過小評価する分を、ブラック-ショールズ等のオプション理論で価値化。

### 8.2 Black-Scholes 適用 (real option として)

```
C = S × N(d1) − K × e^(−r×T) × N(d2)
d1 = [ln(S/K) + (r + σ^2/2) × T] / (σ × √T)
d2 = d1 − σ × √T
```

| 変数 | 真の経済意味 (real option として) |
|---|---|
| S | 後続フェーズで開発する事業の **PV (現在の DCF 価値)** |
| K | 後続フェーズへの追加投資額 (executive cost) |
| T | 意思決定までの期間 (年) |
| r | リスクフリーレート |
| σ | 事業価値のボラティリティ (年率) — 推定が肝 |

### 8.3 Binomial / Decision Tree との併用

3 段階 (Phase I → II → III) のバイオは **Decision Tree + 各段階での real option** が標準:

```
Value = Σ p(reach phase) × [PV(launch) − Σ PV(stage costs)] − Σ PV(unconditional costs)
```

各段階の **abandonment option** (失敗時の損切り権) も明示的に評価。

### 8.4 適用条件

- 将来意思決定の柔軟性が **真に存在** (契約上 / 構造的に)
- σ が信頼できる (公開類似企業 stock vol、業界 vol benchmark)
- 段階移行の milestones が明確

**強み:** 段階的 R&D の価値化、TAM 拡張の価値化、abandonment の価値化
**弱み:** σ 推定が最大の未知数。±20%pt の誤差で valuation ±50% 動く
**典型的失敗:** σ を低く置き option value を過小評価 / 高く置きすぎて DCF を圧倒する

### 8.5 ミニケース 4: Biotech 第II相 中の real options

**設定:**
- バイオベンチャー、第I相完了、第II相を計画中
- 第III相 + 上市時の事業 PV (DCF)= $500M
- 第II相費用 = $40M (今後 2年で支出)
- 第III相費用 = $200M (第II相成功後、3年後に支出)
- 第II相成功確率 = 40%
- 第III相成功確率 (条件付き) = 60%
- σ (業界 small biotech 株価ボラ) = 60%
- r = 4.0%

**段階1: Decision Tree ベースの DCF:**
```
P(reach launch) = 0.40 × 0.60 = 0.24
E[Launch Value] = 0.24 × $500M = $120M
PV (5y discount @ WACC 12%): 120 / 1.12^5 ≈ $68M
PV(Phase II cost) = 40 / 1.12^1 ≈ 35.7   (簡略)
PV(Phase III cost) = 0.40 × 200 / 1.12^3 ≈ 56.9
Naive DCF = 68 − 35.7 − 56.9 = -24.6  → 投資不能
```

**段階2: Real option として (abandonment 権利を価値化):**
- 第II相段階で「失敗 (60%) なら第III相投資をしない」abandonment option がある
- これは「第II相成功時にのみ第III相 $200M を行使する call option」
- 第II相成功時の value: $500M × 0.60 (第III相成功確率) = $300M, K = $200M, T = 3y, σ = 0.6
- d1 = [ln(300/200) + (0.04 + 0.36/2) × 3] / (0.6 × √3) = [0.405 + 0.66] / 1.039 ≈ 1.025
- d2 = 1.025 − 1.039 ≈ −0.014
- N(d1) ≈ 0.847, N(d2) ≈ 0.494
- C = 300 × 0.847 − 200 × e^(−0.12) × 0.494 = 254 − 87.8 ≈ $166M
- これが「第II相成功時点での option 価値」
- 期待 option 価値 (today) = 0.40 × 166 / 1.12^2 ≈ 53.0
- PV(Phase II cost) = 35.7
- Real Option Value = 53.0 − 35.7 = +$17.3M → **投資可** (vs naive DCF −24.6)

**インサイト:**
- DCF だけで切り捨てる案件のうち、abandonment option を持つものは real option で覆る可能性
- σ を 50% に下げると C ≈ $145M、option value 落ちて −値 → σ 感度極大
- 第II相 / 第III相成功確率は industry benchmark (BIO/BioMedTracker, Wong-Siah-Lo 2019 paper) 必須

---

## 9. Replacement Cost / Asset-based Valuation

### 9.1 Replacement Cost

「同等の事業を一から作るのに何を買い、何を採用しなければならないか」を積み上げる:

- 開発済 IP / コードの再構築費用 (engineer-year × cost)
- 取得済顧客リストの CAC × N
- 取得済データセットの市場価格
- 知財登録費用、ブランド構築投資
- 営業組織立ち上げ費用

**適用:** acquihire の price floor、 distressed assets、技術買収の floor。

**弱み:** 上限論にしかならない、ネットワーク効果や暗黙知を捕捉できない。

### 9.2 Asset-based (純資産価額方式)

財務諸表の純資産 (Equity book value) を基礎に、含み損益を時価評価:

```
Adjusted Net Asset Value
  = Tangible Assets (時価) + Intangible Assets (時価)
  − Total Liabilities (時価)
```

**適用:** 清算価値、PPA (§13)、日本の税務評価 (§13.3)、ホールディングカンパニーの NAV。
**弱み:** ゴーイングコンサーン価値を捕捉できない、SaaS / IP 重視事業で大きく過小。

---

## 10. Cloud / SaaS 特有の評価

### 10.1 EV / NTM ARR (主軸 multiple)

```
EV = NTM ARR × Multiple
```

**Rule of thumb:**
- Public SaaS median (2026 Q1): 6–7× NTM Revenue (出所: SaaS Capital, BVP Cloud Index)
- Private SaaS median: 4.5× ARR
- Top tier (Rule of 40 ≥ 50, NRR ≥ 120%): 7–9× ARR (private)

### 10.2 Bessemer Cloud Index (BVP) の使い方

- Index 構成: 公開 SaaS 60–80 社、market-cap weighted
- 月次 / 四半期で multiple 推移を追う
- **Multiple は growth と強く相関する** ことが BVP/Meritech 定期レポートで実証
- 自社 valuation の market-cycle adjustment に必須

### 10.3 Rule of 40 と Multiple

```
Rule of 40 = Revenue Growth (%) + EBITDA / FCF margin (%)
```

- 40 超: 健全
- 50 超: premium tier、multiple +1〜2× 上振れ
- 60 超: top decile

**Empirical:** 各 10pt 改善で EV/Revenue multiple +1.1× (2024–2025 SaaS Capital data)

### 10.4 NRR / GRR 連動

- NRR (Net Revenue Retention): existing cohort revenue の前年比 (拡張 - 解約)
- GRR (Gross Revenue Retention): 解約のみ
- NRR ≥ 120% は SaaS top tier の定石

EV/ARR multiple の規定式 (Meritech 流):
```
EV/ARR ≈ f(Growth, NRR, FCF margin, TAM)
```

### 10.5 LTV / CAC, Payback Period, Magic Number

- LTV/CAC ≥ 3: 健全
- CAC Payback ≤ 12 か月: 効率高
- Magic Number = (Revenue 増分 × 4) / S&M 支出 ≥ 0.75

これらは multiple そのものを決めないが、**comp set 内での discount/premium 判断**に使う。

---

## 11. Marketplace / Fintech 特有

### 11.1 Marketplace

#### GMV Multiple
```
EV = GMV × Multiple_GMV
```
- 0.2–0.6× 程度 (take rate に依存)
- High-take (Etsy 22%): 0.5× 以上
- Low-take (eBay 12%, Mercari 10%): 0.2–0.3×

#### Revenue (Take rate × GMV) Multiple
```
EV = (GMV × take rate) × Multiple_Rev
```
GMV multiple よりも take-rate を normalize した evaluation。

#### Liquidity, GMV per active buyer, GMV growth
- Liquidity (出品の成約率) が long-term margin の先行指標
- GMV / active buyer、Cohort GMV retention で health check

### 11.2 Fintech 特有

- **Lending:** P/B (Price-to-Book), P/PPP (Pre-Provision Profit)、ROA、ROE、loan loss reserve coverage
- **Payment:** TPV (Total Payment Volume), take rate, EV/TPV, EV/Revenue
- **Insurtech:** Combined ratio, expense ratio, P/EVE (Embedded Value)
- **Wealthtech:** AUM × take rate × multiple、または EV/Net Revenue

#### Take Rate × Multiple 分解

EV/TPV を構成要素分解で sanity check:
```
EV/TPV = (EV/Revenue) × (Revenue/TPV) = Revenue Multiple × Take Rate
```

- Square (Block): EV/TPV 0.05–0.10×, Revenue multiple 3–4×, take rate ≈ 1.7%
- PayPal: EV/TPV 0.05×, take rate ≈ 2.0%

### 11.3 ミニケース 5: Fintech (融資) の P/B + ROE で valuation

**設定:**
- 中小企業向けレンディングフィンテック
- 自己資本 ¥10B、貸出残高 ¥80B、年間 PPP ¥3.5B、ROE 直近 25%、貸倒引当 cover 1.5%
- 評価日 2026-02

**Comp:**
- 米 SoFi: P/B 1.7×, ROE 8% (依然成長期)
- 韓 Kakao Bank: P/B 1.4×, ROE 5%
- ブラジル Nubank: P/B 5.5×, ROE 28%

**Justified P/B (Gordon-Growth):**
```
Justified P/B = (ROE − g) / (Re − g)
ROE = 25%、Re = 14%、g = 3% (mature converge)
Justified P/B = (0.25 − 0.03) / (0.14 − 0.03) = 0.22 / 0.11 = 2.0×
Equity Value = 2.0 × ¥10B = ¥20B
```

**Comp 中央 (Nubank-like) の adjusted P/B = 3.0× 採用:**
- Equity = 3.0 × ¥10B = ¥30B
- ただし Nubank は ROE 28%, growth 高、貸倒覆 vs 当該より厚い → 1.5–2.0× への割引が妥当

**Range:** ¥20–25B (Justified + Comp blend)

**Sensitivity Table 3: ROE × Re で Justified P/B が動く感度**

| ROE \ Re | Re = 11% | Re = 14% (base) | Re = 17% |
|---:|---:|---:|---:|
| ROE = 18% | (0.18−0.03)/(0.11−0.03) = 1.88× | (0.18−0.03)/(0.14−0.03) = 1.36× | 1.07× |
| ROE = 25% (base) | (0.25−0.03)/(0.11−0.03) = 2.75× | **2.00×** (base) | (0.25−0.03)/(0.17−0.03) = 1.57× |
| ROE = 30% | 3.38× | 2.45× | 1.93× |

各 Equity Value (¥B) = P/B × ¥10B Equity:
| ROE \ Re | 11% | 14% | 17% |
|---:|---:|---:|---:|
| 18% | 18.8 | 13.6 | 10.7 |
| 25% | 27.5 | **20.0** | 15.7 |
| 30% | 33.8 | 24.5 | 19.3 |

**インサイト:**
- ROE 持続性 (mature 期に何 % で収束するか) が valuation の最大 driver
- Re ±3pt は β の 0.5pt 動き相当だが、サブプライム後 emerging fintech は high β (1.3–1.6) なので注意
- 貸倒覆 (loan loss reserve) を厚くすると ROE 圧縮 → 将来 ROE の保守見積もりが必要

---

## 12. Damodaran 流派 (NYU Stern) の重要要素

### 12.1 Implied ERP (現在価値ベース)

過去ヒストリカル (Ibbotson 流の 1928〜 average) ではなく、**現在の S&P 500 価格 + アナリスト consensus 配当成長 + Buyback yield** から逆算した IRR − Rf:

```
Implied ERP = IRR(S&P 500) − Rf
```

(出所: pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histimpl.html、月次更新)

2026年1月時点 implied ERP ≈ **4.23%** (出所: aswathdamodaran.substack.com Data Update 2 for 2026)。Historical 平均 (1960–2025) とほぼ一致だが、post-2008 平均よりは低位。

**Implied ERP を使う理由:**
- Forward-looking
- 現在の市場 valuation と self-consistent
- Historical の sample-period dependency 回避

**Implied vs Historical ERP — 使い分け default ルール (E-H-026 解消):**

| 用途 | 推奨 ERP | 理由 |
|---|---|---|
| 内部 IC 用 valuation | **Implied (default)** | Forward-looking、現市場の self-consistent |
| Sell-side / 投資銀行モデル | Implied (主) + Historical (副) | Bank IB は historical 1928〜 を併記する慣習が残るため両論併記 |
| 規制当局・rate-making (公益事業等) | Historical | Regulator が historical を mandate する場合あり |
| 学術 / academic | Historical (long-run) | 一貫性・比較可能性を優先 |

**default は Implied**。Historical を使う場合は audience 要件 (sell-side bank、regulator) を明記し、Implied と併記する。両方を提示する場合は「主 = Implied、副 = Historical (sanity check)」を明示。

### 12.2 Country Risk Premium (CRP)

```
CRP = Sovereign Default Spread × (σ_equity / σ_bond)
```

- Sovereign Default Spread: Moody's local-currency rating → Damodaran rating-spread table
- σ ratio: equity index volatility / sovereign bond volatility (Damodaran の経験則 1.0–1.5)

(出所: pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)

**日本 (2026-01-05 Damodaran 更新時点):** Moody's A1、Adjusted Default Spread = 0.60%、CRP = **0.91%**、Total Equity Risk Premium = **5.14%** (= US mature ERP 4.23% + 0.91%)。最新値は ctryprem.xlsx で要再確認。

**Country exposure (λ) で按分:**
```
Effective CRP = Σ (revenue_share_country_i × CRP_i)
```

または location of operations base、または listing 地。Damodaran は **revenue exposure 推奨**。

### 12.3 Synthetic Credit Rating

スタートアップは外部格付なし。Damodaran は ICR (Interest Coverage Ratio) → synthetic rating → default spread の table を提供 (`ratings.xls`)。

サンプル閾値 (large firm):

| ICR レンジ | Synthetic Rating | Default Spread (例) |
|---|---|---|
| > 8.5 | AAA | 0.6% |
| 6.5–8.5 | AA | 0.8% |
| 5.5–6.5 | A+ | 1.0% |
| 4.25–5.5 | A | 1.1% |
| 3–4.25 | A− | 1.25% |
| 2.5–3 | BBB | 1.5% |
| 2.25–2.5 | BB+ | 2.0% |
| 2–2.25 | BB | 2.5% |
| 1.75–2 | B+ | 3.5% |
| 1.5–1.75 | B | 5.0% |
| 1.25–1.5 | B− | 6.0% |
| 0.8–1.25 | CCC | 8.0% |
| 0.65–0.8 | CC | 10.0% |
| 0.2–0.65 | C | 12.0% |
| < 0.2 | D | 15.0% |

(数値はレンジ目安。最新の正確な閾値・spread は ratings.xls 要確認)

スタートアップ (赤字 = ICR 負) は **smallrating.htm** の "small firm" table または同業 mature 企業 rating proxy。

### 12.4 Lifecycle Valuation Framework

Damodaran は企業を **Idea → Young Growth → High Growth → Mature Growth → Mature Stable → Decline** の 6 段階に分け、各段階で:

| Stage | Revenue 成長 | Margin | 主要 driver | 推奨手法 |
|---|---|---|---|---|
| Idea | n/a | -∞ | TAM / story | Berkus, Scorecard, VC Method |
| Young Growth | 100%+ | 大幅赤字 | TAM × penetration | VC method, Real option, DCF (if visible) |
| High Growth | 30–80% | 黒字化過渡期 | Unit economics, NRR | DCF + Comps |
| Mature Growth | 10–30% | 成長 + margin | ROIC > WACC | DCF (主), Comps |
| Mature Stable | 2–10% | 安定 | FCF, capital return | DCF, P/E, EV/EBITDA |
| Decline | 負 | margin 収縮 | 資産売却価値 | Liquidation, Asset-based |

各段階で **適切な discount rate と FCF 設計**が異なる。Stage 越境点で valuation discontinuity (margin 急変) が発生しやすい。

**Margin step rule (E-H-022 解消):** 単年度 EBIT margin の YoY 変動幅が **±5pp を超える transition** は赤旗 (red flag)。-20% margin → +25% margin の単年 jump 等は (a) 2 年スムージング層を挟むか、(b) 一時的 cost cut / IPO milestone bonus 等の特殊要因を脚注で justification する。Justification なしの jagged transition は審査差し戻し対象。

---

## 13. 公正価値 (PPA / 409A / 監査対応)

### 13.1 ASC 820 / IFRS 13 — Fair Value Hierarchy

| Level | 定義 | 例 |
|---|---|---|
| Level 1 | Active market quoted price | 公開株 |
| Level 2 | Observable inputs (market data, quoted prices similar instruments) | 同業公開 comps、yield curve |
| Level 3 | Unobservable inputs (model-based) | Private startup, complex preferred stock |

スタートアップは Level 3。OPM / PWERM / Hybrid model + sensitivity disclosure 必須。

### 13.2 409A Valuation (米国 ESOP の strike price)

米国 IRC §409A は、**common stock の Fair Market Value (FMV)** を独立した評価 (independent valuation) で決定し、その FMV 以上で stock options の strike を設定することを要求。

#### 主要 3 手法 (出所: Sofer Advisors, J.P. Morgan, txncapitalllc 等)

**(a) Option Pricing Method (OPM)**
- Black-Scholes ベースで、企業価値全体を call option pool として preferred / common / option / warrant に allocate
- 入力: 企業価値 (V)、各 share class の breakpoint (liquidation preference, conversion ratio)、σ、T (expected exit time)、r
- 強み: capital structure の preference を厳密に反映
- 弱み: σ と T の推定、近 IPO で誤差大
- 適用: Series A〜C 中期、exit が時期不明

**(b) Probability-Weighted Expected Return Method (PWERM)**
- 2–4 個の discrete scenario (IPO, M&A, Continued operation, Dissolution) を設定
- 各シナリオで equity allocation を計算し、確率加重
- 強み: 直感的、stakeholder への説明容易
- 弱み: シナリオ確率の主観性
- 適用: Pre-IPO、近 exit が見えるレイトステージ

**(c) Hybrid Method**
- 近期高確率シナリオ (例: IPO in 12mo) は PWERM で詳細モデル
- 遠期 / unclear シナリオは OPM で allocate
- 適用: Pre-IPO 最終局面、現在の業界標準

#### 409A の実務フロー

```
1. Independent valuation firm 起用 (or AICPA Practice Aid 準拠の internal model)
2. Enterprise Value 推定 (DCF / Comps / Backsolve from latest round)
3. Equity Value = EV − Net Debt
4. Allocate to share classes (OPM/PWERM/Hybrid)
5. Common stock per share FMV を算出
6. Marketability discount (DLOM, 15–30%) 適用
7. Strike price ≥ FMV で option grant
8. Annual reset または triggering event (調達, M&A, 急成長) で再評価
```

### 13.3 日本の税務評価

#### 純資産価額方式
- 1株当たり相続税評価額 = (時価純資産 − 法人税等相当額 37%) / 発行済株式数
- 含み益のある資産は時価評価 (土地、有価証券、暗号資産)

#### 類似業種比準方式
```
評価額 = A × [(B'/B + C'/C + D'/D) / 3] × 0.7 (中会社) or 0.5/0.6/0.7
```

| 記号 | 意味 |
|---|---|
| A | 類似業種 (国税庁公表) の平均株価 |
| B, C, D | 類似業種の 1株当たり配当, 利益, 純資産 |
| B', C', D' | 当社の 1株当たり配当, 利益, 純資産 |

(0.7 / 0.6 / 0.5 は会社規模区分、大会社 0.7、中 0.6、小 0.5)

#### 配当還元方式
少数株主向け簡易方式: `(年配当額 / 10%) × 1株額面 / 50円`

#### スタートアップ実務上の論点

**(a) ストックオプション (新株予約権) の税制適格要件:**
租税特別措置法 29条の2 の税制適格 SO は、付与時点の権利行使価額が **「時価以上」** であることを要件とする。「時価」の定義は:
- 公認会計士等による評価書 (DCF / 類似業種比準など) で算定された価額
- または、**直近の第三者割当増資価額** を anchor とする
- 直近 6 か月以内の調達があれば、その price-per-share が原則 fair value とみなされる慣行

行使価額が時価未満で付与すると、**(i) 給与所得課税 (累進、最高 55%)** が発生し税制適格性を喪失。米 409A の下方違反 (FMV 未満 strike) と同様、後発的に税務当局の更正対象となるため、慎重な評価が必要。

**(b) 直近の第三者割当増資価額の参照:**
評価日から **概ね 6 か月** 以内のラウンドが anchor として尊重される。ただし以下の場合は anchor からの調整が必要:
- 普通株 vs 種類株 (preferred): preferred liquidation preference を控除した普通株 FMV を別途算定 (OPM/PWERM 適用)
- ラウンド間で大きな業績変動 (例: PMF 達成、主要顧客失注) があれば再評価
- ダウンラウンド時は普通株 FMV も連動して下方修正

**(c) 評価通達 (純資産価額・類似業種比準) と公正価値の乖離調整:**
税務評価 (相続税・贈与税ベース) は、**公正価値 (ASC 820 / IFRS 13)** とは必ずしも一致しない:
- 純資産価額方式は「時価純資産 − 含み益への 37% 法人税相当」を控除 → 公正価値より **15–25% 低位**
- 類似業種比準方式 × 0.6 (中会社) のディスカウントが入る → 公正価値より **30–40% 低位**
- 国税庁が認める「特定評価会社」(株式保有特定会社、土地保有特定会社等) では純資産価額方式に強制移行

**(d) M&A・第三者割当時の実務:**
- M&A デューデリジェンス: DCF + 類似会社比較 + 直近ラウンド anchor の triangulate
- 第三者割当: 会社法上「特に有利な発行価額」(時価の概ね 90% 未満) は株主総会特別決議が必要
- 役員に対する付与 (有償ストックオプション、信託 SO) は別途評価書必須

**(e) 監査・税務調査での主要論点:**
- 評価書の独立性 (利害関係なき第三者)
- 評価日と取引日の一致
- 評価仮定 (WACC, growth, multiple) の合理性説明
- DCF の感度分析、複数手法 triangulation の実施

参考: 日本公認会計士協会「企業価値評価ガイドライン」(経営研究調査会研究報告 第32号)、国税庁「財産評価基本通達」、租税特別措置法 29条の2、会社法 199条 (有利発行)

### 13.4 PPA (Purchase Price Allocation, ASC 805 / IFRS 3)

M&A 後、買収対価を識別可能資産・負債に時価配分:
- 識別可能無形資産: 顧客関係 (excess earnings method)、技術 (relief from royalty)、商標 (relief from royalty)
- Goodwill: 残差 = 対価 − 識別可能 net assets

スタートアップ買収では **顧客関係と開発技術** が無形資産の中心。Excess earnings method:
```
Customer Relationship Value
  = Σ (Existing Customer Revenue × Profit Margin × Attrition curve − Contributory Asset Charges)
    discounted at WACC + customer-specific risk premium
```

---

## 14. ベンチマーク値とデータソース (実務リファレンス)

### 14.1 月次 / 四半期更新が要るデータ

| データ | ソース | 更新頻度 | URL / 備考 |
|---|---|---|---|
| Implied ERP (US) | Damodaran | 月次 | pages.stern.nyu.edu/~adamodar/New_Home_Page/dataarchived.html |
| Country Risk Premiums | Damodaran | 年1〜2回 | ctryprem.xlsx |
| Industry Beta (sectors) | Damodaran | 年次 (1月) | betas.xls |
| Synthetic Rating spreads | Damodaran | 年次 | ratings.xls |
| WACC by industry | Damodaran | 年次 | wacc.xls |
| Public SaaS multiples | SaaS Capital, BVP Cloud Index, Meritech | 月〜四半期 | cloudindex.bvp.com / saascapital.com |
| Rule of 40 distribution | Bessemer Cloud 100 / SaaS Capital | 年次 | bvp.com/atlas |
| VC Pulse (deal activity, valuations) | KPMG / EY / Pitchbook | 四半期 | KPMG Venture Pulse, EY VC Trends |
| Japan startup data | INITIAL, STARTUP DB | 月〜四半期 | initial.inc / startup-db.com |

### 14.2 Sector-Specific 主要マルチプル (2026 Q1 概況)

(以下は時点感をつかむための approximate range。**個別案件では最新ソースで再確認**)

| Sector | Median EV/NTM Revenue | Median EV/NTM EBITDA | Notes |
|---|---:|---:|---|
| Public SaaS (BVP Cloud Index) | 6–8× | 25–35× | Rule of 40 gating |
| Public marketplace | 1.5–3× | 15–25× | Take-rate 依存 |
| Fintech (payment) | 3–5× | 15–20× | TPV growth 連動 |
| Fintech (lending) | n/a | n/a | P/B 1–3× が標準 |
| E-commerce (1P-heavy) | 0.5–1.5× | 10–15× | margin 薄 |
| AI infra (training) | 8–15× | n/a | 2026 強気局面 |
| AI application (vertical) | 5–10× | 30–40× | growth 第一 |
| Bio (pre-revenue, in pipeline) | n/a | n/a | Real options + risk-adjusted NPV |
| Climate tech | 3–6× | 20–30× | subsidy dependence varies |

**重要免責:** 数値は 2026 Q1 周辺の傾向で、月単位で動く。Damodaran 公式 update / SaaS Capital monthly update / BVP Cloud Index dashboard をモデル日付直前に再取得すること。

### 14.3 VC ファンド向けの benchmark

- DPI (Distributions to Paid-In): 5y で 0.5–1.0×, 10y で 1.5–3.0× が top quartile
- TVPI (Total Value to Paid-In): 10y で 2.5–4.0× が top quartile
- IRR: gross 20%+, net 15%+ が top quartile (Cambridge Associates / Preqin benchmark)

---

## 15. 落とし穴 (cross-cutting pitfalls)

### 15.1 Beta 推定の不安定性

- 流動性が低い comp の regression beta は、stale price 問題で **下方バイアス**
- 対策: Scholes-Williams beta、Dimson lag-correction、業界 beta + bottom-up
- 5y monthly が標準だが、ビジネスモデル激変期 (e.g., COVID 2020) は 2y weekly や excluded period も検討
- **Damodaran 流: 個別 regression beta を信用せず、industry bottom-up beta を使う**

### 15.2 Terminal Value が EV の 75% 超 → 黄信号

意味: 「予測期間中の CF」がほとんど評価に効いていない。実質的に exit multiple モデルと同じ。

対策:
- 予測期間延長 (10y → 15y / 20y)
- 二段階成長モデル (high-growth phase + transition phase + steady state)
- Reverse DCF で TV-implied growth を可視化
- TV を Gordon と Exit Multiple の **両方で計算しレンジ表示**

### 15.3 WACC と g の循環参照

WACC と g は両方が valuation を大きく動かす。実務:
- **WACC > g + 200bp** を硬性制約 (denominator が thin だと TV が爆発)
- Sensitivity table 必須 (WACC ±2%, g ±1%)
- Cross-check: g_implied from exit multiple と Gordon g を一致させない

### 15.4 Comp 多重カウント

- LTM と NTM、または同一会社の subsidiaries を別カウント
- 持ち合い (e.g., Alibaba × Ant) で valuation 重複
- Spin-off 前後の同一会社を別計上

### 15.5 Stock-Based Compensation (SBC) の扱い

**問題:** GAAP/IFRS で EBIT に費用計上だが、CF 計算書で加算戻し → "Adjusted EBITDA" "Free Cash Flow" として SBC を除外する慣行が広がる → SaaS 等で valuation が **過大化**。

**Damodaran 主張 (推奨):** SBC は **真の希薄化コスト**。FCFF 計算で「EBIT は SBC 控除済のまま使う」「加算戻しはしない」。または、加算戻すなら share count を将来希薄化込みの diluted で見るか、**TSM の dilution** を保守的に取る。

**実務影響例:**
- ある SaaS で SBC が売上の 20% → naive Adjusted EBITDA で +20%pt margin 過大
- Equity value が naive base 比 30–40% 下がるケースもあり、**特にレイトステージ SaaS で critical**

**Disclosure rule (E-H-013 解消):** Sell-side IB と多くの公開 SaaS analyst は SBC を **加算戻しする慣習** が現存する。本書は Damodaran 流の「加算戻しなし」を **理論的 base case (主)** として推奨するが、外部 audience (sell-side comp、investor pitch deck) に提示する場合は **両 version 併記** を必須とする:

1. **SBC-as-cost (本書 default、theoretically correct)**: FCFF = EBIT(SBC 控除後) × (1 − t) + D&A − CapEx − ΔNWC
2. **SBC-added-back (market convention)**: 上記に SBC を加算 (Adjusted FCF)

両者の EV gap を表に明記し、「市場慣行 vs 理論」の差として説明すること。Single number で出す場合は SBC-as-cost を採用し、SBC-added-back は sensitivity row として下に置く。

### 15.6 マルチプル時点不整合 (LTM vs NTM ミックス)

- Comp set 内で LTM と NTM を混ぜない (§2.3)
- 自社にも同じ期間定義の数字を当てる
- Calendarization で fiscal year を揃える (§2.5)

### 15.7 Stack-up bias (Best Case の積み上げ)

- Revenue growth (best case) × Margin (best case) × NWC (best case) × CapEx (best case) を全項目 best で積み上げる → 実現確率は項目数 N に対し p^N (各 50% でも 5 項目で 3%)
- 対策: モンテカルロ、確率連動、または "Worst case 入れた sensitivity table"

### 15.8 Survival probability と High discount rate の二重カウント

- Stage-appropriate discount rate (60% IRR) は **survival 失敗を織り込み済**
- これに更に E[CF] (= success CF × survival prob) を掛けると二重控除
- 整合: 「(a) Mature WACC + survival probability adjusted CF」 OR 「(b) Stage-appropriate high IRR + unconditional success CF」のどちらか一方

### 15.9 Net Debt 計算漏れ

- Operating lease (IFRS 16/ASC 842) → 負債計上漏れで EV 過小
- Underfunded pension → 隠れ負債
- Earn-out / contingent consideration → 取得時 fair value 計上必要
- SAFE / Convertible note → equity-like だが IFRS で負債分類されることがある

### 15.10 Currency / Inflation 不整合

- Nominal CF + Real WACC、または逆 → 系統的バイアス
- 通貨混在 (USD revenue + JPY cost) で WACC を JPY 単一にする → forward FX 整合性破綻

### 15.11 Liquidation preference の無視

- Series A/B/C で 1× non-participating, 1× participating, 2× participating with cap などが混在
- Common stock 価値に大きく影響 (down-round で wipeout も)
- OPM / PWERM (§13) で必ずモデル

### 15.12 直近ラウンド post-money の参照点バイアス

- 直近ラウンド post-money は valuation の "anchor" として使われがちだが、**market cycle dependent**
- 2021 round は 2024–2025 では 30–50% overvalued の可能性
- Time-adjusted, public-multiple-rebased で再評価

### 15.13 PEG Ratio の誤用

- PEG = (P/E) / Growth%、Growth% の単位 (例: 30 か 0.30 か) で 100 倍違う
- Growth が 0% に近いと PEG が爆発
- Negative growth では使用不能

### 15.14 Forecast の hockey stick

- 最初の 1–2 年は赤字 / 横ばい、3 年目以降急上昇 → "hockey stick"
- ベンチマーク化: top-quartile growth を超える前提なら根拠提示
- Cohort analysis で current cohort の trajectory を bottom-up で示す

---

## 16. バリュエーション DD チェックリスト

投資意思決定の最終局面で、以下をすべて埋める:

### 16.1 全手法横断

- [ ] Intrinsic (DCF) + Relative (Comps) + Absolute (Precedent or VC method) の 3 系統を triangulate (§17)
- [ ] 各手法の central, low, high が ±20% 以内に収束しているか
- [ ] 乖離が大きい場合、その原因を 1〜3 文で説明できるか
- [ ] Football field chart で重なる帯を target range として提示

### 16.2 DCF

- [ ] FCFF / FCFE のどちらを主にしたか明示
- [ ] WACC 構築の各 component (Rf, β, ERP, CRP, SP, ILP) と出所明記
- [ ] Beta は bottom-up (industry / peer unlevered + relevered) か、独立 regression か
- [ ] Cost of Debt を synthetic rating で導出した場合、ICR 計算と rating proxy の妥当性
- [ ] Terminal value: Gordon × Exit Multiple の両方で計算
- [ ] g ≤ Rf, g ≤ long-term GDP の硬性制約満たすか
- [ ] TV / EV 比率が 75% 超か (黄信号)
- [ ] Mid-year convention 明示
- [ ] Currency / inflation 整合
- [ ] SBC の treatment (加算戻ししないか、希薄化に取り込むか)
- [ ] Stage-appropriate discount rate を使っているか、または survival probability で adjust か (二重カウントなし)
- [ ] Sensitivity table (WACC ±2%, g ±1%, terminal margin ±5%pt) 添付
- [ ] Reverse DCF で implied growth/margin の妥当性チェック

### 16.3 Comps

- [ ] Comp set 5 社以上、business model / size / growth / geography で justify
- [ ] LTM vs NTM が comp set 全体で統一されているか
- [ ] Calendarization 実施済 (異なる FY 末を揃えた)
- [ ] Diluted share count は TSM 適用済か
- [ ] Net Debt に operating lease, pension, preferred, NCI, SAFE 等を含めたか
- [ ] Outlier 除外の根拠
- [ ] Median と mean 両方を提示
- [ ] EV/Revenue, EV/EBITDA, EV/ARR など複数 multiple で cross-check
- [ ] Take-rate / margin 差分を multiple で調整したか (marketplace の場合)

### 16.4 Precedent

- [ ] 直近 3〜5年の同セクター取引
- [ ] Strategic vs Financial buyer 区別
- [ ] Synergy 控除済の standalone valuation
- [ ] Control premium (25–40%) の妥当性
- [ ] Staleness 調整 (古い deal は public multiple 推移で rebase)

### 16.5 VC Method / First Chicago

- [ ] Required IRR が stage と整合
- [ ] Best/Base/Worst の確率合計 = 1.0
- [ ] Liquidation preference が分配に反映
- [ ] Backsolve の場合、anchor のラウンド時期と現在の market regime ギャップを意識

### 16.6 Stage-specific

- [ ] Idea/pre-seed: Berkus + Scorecard + Risk Factor の 3 法 triangulation
- [ ] Bio/R&D: Real option (abandonment) を必ず併用
- [ ] SaaS: Rule of 40 / NRR / GRR / payback / magic number で multiple 補正
- [ ] Marketplace: Take rate 調整、liquidity 指標
- [ ] Fintech: P/B 系と EV 系の両方

### 16.7 公正価値 / 監査

- [ ] 直近 409A FMV と DCF/Comps の乖離が説明可能
- [ ] Liquidation preference 込みの common stock allocation (OPM/PWERM/Hybrid)
- [ ] DLOM / DLOC 設定の根拠
- [ ] Level 3 disclosure が監査要件を満たすか

### 16.8 データの一次性

- [ ] Damodaran の ERP / CRP / Beta は最新月のデータか
- [ ] SaaS multiple は SaaS Capital / BVP の direct 数字か (要約・転載でなく)
- [ ] 経営計画は management の "approved" 版か (sales pitch ではなく)

### 16.9 Documentation

- [ ] モデルの assumption sheet が独立しているか
- [ ] Hard-code を排除した formula linkage か
- [ ] 計算 trace (drilldown) が IC で示せるか
- [ ] Model audit (third-party / senior reviewer) を経たか

---

## 17. トライアンギュレーション (Triangulation) 手順

### 17.1 標準フロー

投資判断 / valuation 確定の **dual verification** プロセス:

```
Step 1: 主手法の選定 (stage-dependent)
         Idea/Pre-seed → Berkus, Scorecard, VC method
         Series A/B    → VC method (主), DCF (補助), Comps (補助)
         Series C+     → DCF (主), Comps (主), VC method (補助), Precedent (補助)
         Mature        → DCF (主), Comps (主), Precedent (補助)

Step 2: 各手法で central / low / high を出す
         DCF: Bear / Base / Bull (assumption の variation)
         Comps: 25th / median / 75th percentile multiple
         Precedent: deal-by-deal range
         VC method: Required IRR ±10pt sensitivity

Step 3: Football field chart
         縦軸: 手法、横軸: Equity Value
         各手法の min/max を bar で描画
         複数手法の overlap zone = target range

Step 4: 収束判定
         (max(centrals) − min(centrals)) / median(centrals) ≤ 20%
         → 収束、target range 採用
         > 20%
         → 乖離原因を特定し、再計算 or 明示的 disclosure

Step 5: 乖離原因 typology
         (a) Comp set 不適切 (business model 違い) → comp set 再選定
         (b) WACC 過大 / 過小 → β, ERP, stage discount を再考
         (c) Terminal value 暴走 → 期間延長 or g 下方修正
         (d) Multiple cycle (市場高すぎ/低すぎ) → time-rebase
         (e) Liquidation preference 未反映 → OPM/PWERM 適用

Step 6: 最終 valuation の提示
         Range (low – high), central
         Investor recommendation: 提示価格 vs target range
```

### 17.2 Dual Verification Test (Claude Code skill 用)

Claude が valuation 出力する際、**自動的に以下 2 点を確認**:

1. **手法独立性チェック:** 主手法 + 補助手法の 2 系統以上、central が ±20% 内収束
2. **数値整合性チェック:** WACC > g, TV/EV ≤ 75%, Comp set ≥ 5, LTM/NTM 統一, share count diluted, Net Debt 完全

満たさない場合は **明示的に flag** を立て、ユーザーに「乖離 / 違反」を報告。

### 17.3 ミニケース (本リファレンス内の 5 案件) 横断 triangulation 例

|案件 (mini-case) | 主手法 | 補助 | central converge? |
|---|---|---|---|
| §1.11 Series B SaaS DCF | DCF (10y + Gordon/Exit) | Comps (EV/ARR 6× private + 7× public) | TV uncertainty 大、レンジ提示 |
| §2.10 Marketplace Comps | Trading comps (EV/Rev, EV/GMV) | Precedent (M&A) | Take-rate 補正で 20% 収束 |
| §4.5 Series A VC method | VC (3 シナリオ) | Pre/Post bridge to next round | Required IRR 感度 ±40% |
| §8.5 Bio Real Options | Decision tree DCF + Real option | Comp (peer pre-clinical bio) | σ 感度 ±50% |
| §11.3 Fintech P/B | Justified P/B (Gordon) | Comp P/B | ROE 持続性 critical |

### 17.4 投資判断時の最終確認

- **市場 multiple cycle の認識:** 2026 Q1 SaaS public multiple 6–7× は 2021 ピーク (15×+) 比 半減水準。投資 thesis が "再拡張" 前提なら明示的に書く。
- **下方リスクのストレステスト:** Bear case で IRR < 0% の確率、time-to-fund-life-end までの cash burn、down round シナリオでの dilution
- **キーマンリスク:** Founder departure scenario の valuation discount
- **規制・地政学:** Country specific overlay (regulatory shift, FX, sanction)

---

## 18. 付録: 数式レファレンス (まとめ)

### 18.1 DCF
```
EV = Σ FCFF_t / (1 + WACC)^t  +  TV / (1 + WACC)^n

FCFF = EBIT × (1 − t) + D&A − CapEx − ∆NWC

FCFE = NI + D&A − CapEx − ∆NWC + Net Borrowing
     = FCFF − Interest × (1 − t) + Net Borrowing

WACC = (E/V) × Re + (D/V) × Rd × (1 − t)

Re = Rf + β × ERP + λ × CRP + SP + ILP

β_levered = β_unlevered × [1 + (1 − t) × (D/E)]

TV_Gordon = FCFF_(n+1) / (WACC − g)

TV_Exit  = Metric_n × Multiple
```

### 18.2 Comps
```
EV = (Market Cap + Net Debt + Preferred + NCI − Investments)

Diluted Shares = Basic + Σ_ITM (#opt × (1 − strike / price))

Calendarized FY = (m/12) × FY+1 + ((12−m)/12) × FY+2
```

### 18.3 VC Method
```
Required Post-money = Exit Value / (1 + IRR)^n
Pre-money = Required Post-money − Investment
% Ownership = Investment / Post-money

E[Exit] = Σ p_i × Exit_i  (First Chicago)
```

### 18.4 Real Option
```
C = S × N(d1) − K × e^(−rT) × N(d2)
d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d2 = d1 − σ√T
```

### 18.5 Justified P/B (Banking)
```
Justified P/B = (ROE − g) / (Re − g)
```

### 18.6 Rule of 40
```
Rule of 40 = Revenue Growth (%) + EBITDA margin (%)
```

### 18.7 LTV / CAC
```
LTV = ARPU × Gross Margin / Churn Rate
CAC = S&M Spend / New Customers Acquired
LTV / CAC ≥ 3 が健全
```

---

## 19. 参考文献・一次ソース

### 19.1 Damodaran (NYU Stern) — モデル独立の標準資料

- Damodaran, A. *Investment Valuation* (3rd ed., Wiley, 2012)
- Damodaran, A. *The Dark Side of Valuation* (3rd ed., FT Press, 2018) — 特にスタートアップ・新興国・サイクリカル
- Damodaran "Valuing Young, Start-up and Growth Companies: Estimation Issues" (working paper, pages.stern.nyu.edu/~adamodar/pdfiles/papers/younggrowth.pdf)
- Damodaran "Equity Risk Premiums (ERP): Determinants, Estimation, and Implications — 2026 Edition" (SSRN abstract_id=6361419)
- Damodaran data updates (月次 substack): aswathdamodaran.substack.com
- Damodaran data files: pages.stern.nyu.edu/~adamodar/

### 19.2 McKinsey & 主要教科書

- Koller, Goedhart, Wessels *Valuation: Measuring and Managing the Value of Companies* (McKinsey, 7th ed., 2020)
- Rosenbaum, Pearl *Investment Banking: Valuation, LBOs, M&A* (3rd ed., Wiley, 2020)
- Pignataro *Financial Modeling and Valuation* (2nd ed., Wiley, 2022)

### 19.3 Startup-specific

- Sahlman "A Method for Valuing High-Risk Long-Term Investments" (HBS 9-288-006)
- Berkus, Dave "The Berkus Method" (berkonomics.com)
- Payne, Bill "Scorecard Valuation Methodology" (billpayne.com)
- Wong, Siah, Lo "Estimation of clinical trial success rates" (Biostatistics, 2019) — Real option σ / probability 入力
- AICPA "Valuation of Privately-Held-Company Equity Securities Issued as Compensation" (Practice Aid)

### 19.4 SaaS / Marketplace / Fintech 業界データ

- BVP Cloud Index (cloudindex.bvp.com)
- SaaS Capital Index (saascapital.com/research)
- Meritech Capital Public SaaS comps (publiccomps.com)
- KPMG Venture Pulse (Q1 2026 等四半期報告)
- EY Venture Capital Insights
- Pitchbook (購読)
- Crunchbase
- INITIAL (initial.inc) — 国内スタートアップ
- STARTUP DB (startup-db.com)

### 19.5 公正価値 / 監査

- ASC 820 / IFRS 13 — Fair Value Measurement
- AICPA Practice Aid (PE/VC investment companies)
- 国税庁「財産評価基本通達」
- 日本公認会計士協会 経営研究調査会研究報告 第32号「企業価値評価ガイドライン」

---

## 21. Boundary Conditions (境界条件・例外処理)

### 21.1 WACC ≈ g 発散 (Gordon Growth の境界)

**問題の所在.** Terminal Value (TV) を Gordon Growth Model で算定するとき:

```
TV = FCF_(n+1) / (WACC - g)
```

ここで `WACC - g → 0` になると TV は無限大に発散し、`WACC < g` では TV が**負の値**になり、経済的に意味を失う。スタートアップの DCF では成長率 g を強気に置きがちで、また WACC を CAPM ベースで再計算する過程で WACC を低く見積もる誤りが重なり、両者が接近・逆転するケースが頻発する。

**3 段階の境界判定 (実装ロジック).**

```
spread = WACC - g

if spread <= 0:
    raise ValuationError("WACC ≤ g: Gordon Growth invalid; switch to Exit Multiple Method")
elif spread < 0.01:           # 1pt 未満
    warn("Spread < 1pt: TV is hyper-sensitive; sensitivity table required, recommend Exit Multiple cross-check")
elif spread < 0.02:           # 2pt 未満
    info("Spread < 2pt: high sensitivity; report TV elasticity to spread")
else:
    pass
```

**閾値の根拠.**
- `spread = 0` (発散点) は数学的境界。
- `spread = 1%` 未満で TV/FCF 比率が **100x を超え**、g の 0.1pt の誤差が TV を 10%以上動かす (`d(TV)/TV = -d(spread)/spread`)。
- `spread = 2%` 未満で TV/FCF 比率が 50x を超え、市場 multiple との乖離が顕著になる (上場 SaaS の EV/Revenue 中央値 6-10x、つまり TV/FCF 50x 以上は warning ライン)。

**自動切替フロー (WACC ≤ g 時).**

```
1. Gordon Growth の TV 計算を停止
2. Exit Multiple Method に切替:
   TV = EBITDA_(n+1) × Exit Multiple (industry median)
3. ログに切替理由を記録 (ユーザーが後で再現できるよう)
4. Sensitivity table を 2 軸 (Multiple, EBITDA) で出力
5. (optional) H-Model や 2 段階 DCF も推奨候補として提示
```

**Exit Multiple の選定 (切替先).**

| 業態 | 推奨 Exit Multiple | 中央値レンジ (2024-2025) | 出典 |
|---|---|---|---|
| SaaS (Rule of 40+) | EV/ARR | 6-10x | BVP Cloud Index, Meritech |
| SaaS (mature) | EV/EBITDA | 18-28x | Damodaran "multiples" |
| Marketplace | EV/GMV (take-rate × 8-15x) | — | Pitchbook |
| Fintech (lending) | P/Loan book × ROE | 1.0-1.8x | Damodaran "fin services" |
| Consumer / D2C | EV/Revenue | 1.5-3.5x | Damodaran |
| Hardware / IoT | EV/EBITDA | 8-12x | Damodaran |

**g (永続成長率) の妥当性チェック.**
- g ≤ long-term GDP nominal growth が実務的な上限 (Damodaran 推奨)。
  - 米国: 名目 GDP 4-4.5% (≒ 実質 2% + 期待 inflation 2-2.5%)
  - 日本: 名目 GDP 1-2% (実質 0.5% + 期待 inflation 0.5-1.5%)
  - グローバル mix の場合は加重平均
- `g > risk-free rate` は理論的に矛盾 (riskless growth が riskless rate を超えることはない)。これも警告対象。
- スタートアップの「高成長期」は予測期間 (5-10 年) で表現し、TV の g には**長期定常状態の成長率**のみ使うこと。

**実装テスト (擬似コード).**

```python
def test_wacc_g_boundary():
    fcf = 100
    # Case 1: invalid (WACC < g)
    assert switch_to_exit_multiple(wacc=0.10, g=0.12)
    # Case 2: warning (spread < 1pt)
    tv = gordon_tv(fcf, wacc=0.105, g=0.10)
    assert warning_emitted("spread < 1pt")
    # Case 3: normal
    tv = gordon_tv(fcf, wacc=0.10, g=0.03)
    assert tv == pytest.approx(100/0.07, rel=1e-3)
```

**反例 (アンチパターン).** WACC 9%, g 8% で TV を計算 → TV/FCF = 100x。市場 multiple 18-28x との乖離が 4-5 倍。これは「数字が滑った」サインで、内部整合性の崩壊を示す。スプレッドが小さい時は Exit Multiple との triangulation を必須化する。

### 21.2 Stage Transition での discount rate 切替 (経路依存性の処理)

**問題の所在.** Stage discount rate を Pre-revenue 50-70%、Early revenue 40-60% のように段階別の表で運用する場合、ある会計年度に「Pre-revenue → Early revenue」と区分が切り替わると、その年だけ割引率が **15-20pt 一気にジャンプ**する。これは:

1. PV の連続性が失われる (前年の DCF と当年の DCF の整合性が崩壊)
2. 同じキャッシュフローが「stage 切替の前後どちらに属するか」で評価額が 30-50% 変動
3. 経路依存性 (path dependency): 同じ将来 CF でも、stage transition のタイミング次第で結果が変わる

**Smoothing アプローチ (3 種類).**

**(a) Linear ramp (推奨デフォルト).** Stage transition の予定年から N 年かけて線形に補間。

```
discount_rate(t) =
  r_old + (r_new - r_old) × min(1, (t - t_transition_start) / N)
```

- N の標準: **2-3 年** (early/A, A/B のような 1 段階移動)
- 大幅な stage 跨ぎ (例: Pre-revenue → Series B) の場合は N=4-5 年も可
- 出典: Damodaran "Investment Valuation" 3rd ed. Ch.23 (Young & Start-up Firms) で 2-stage 構造の transition を線形 / convex で扱う議論あり

**(b) Convex decay (実態反映型).**

```
discount_rate(t) = r_new + (r_old - r_new) × exp(-λ × (t - t_transition_start))
```

- λ の目安: 0.4-0.6 (半減期 1.2-1.7 年相当)
- 早期に大きく下がり、後で緩やかに収束 → リスク解消の実態 (Series A 直後の survival jump) に近い

**(c) Probabilistic (Monte Carlo).** 各 stage の survival 確率と transition 時期を確率分布で扱い、シミュレーション平均で評価。重要案件のみ。

**経路依存性の警告ロジック.**

```
if abs(r_new - r_old) > 0.10:    # 10pt 以上のジャンプ
    warn("Stage transition spans > 10pt; smoothing required")
    require_smoothing(method="linear", N=2-3)

if r_old < r_new:                # 逆行 (Down round 等)
    warn("Reverse stage transition detected (risk increased)")
    record_reason()              # reset の理由を必ず記録
```

**Down round / 逆 transition の扱い.** 業績不振や市場収縮で discount rate を再上方修正するケース:
- 評価日時点の最新 information set で discount rate を更新するのが正攻法
- ただし「過去の DCF 推計を**遡及して**書き換える」のは誤り。過去推計は記録として保持し、再評価は当期以降のみ
- 監査では「いつ、どの information で stage 認識を変えたか」のログを必須化

**実装例 (3 段階モデル).**

```python
def stage_discount_rate(year, stages):
    """
    stages = [
        {"name": "pre_rev", "rate": 0.60, "until_year": 2},
        {"name": "early_rev", "rate": 0.50, "until_year": 4},
        {"name": "series_a", "rate": 0.40, "until_year": 999},
    ]
    transition_years = 2  # linear ramp window
    """
    for i, s in enumerate(stages):
        if year <= s["until_year"]:
            if i == 0:
                return s["rate"]
            prev = stages[i-1]
            ramp_start = prev["until_year"]
            t = year - ramp_start
            if t < transition_years:
                return prev["rate"] + (s["rate"] - prev["rate"]) * t / transition_years
            return s["rate"]
    return stages[-1]["rate"]
```

**Cross-check.** Smoothing 適用後の累積 PV が、smoothing なし (step function) の PV と何 % 違うかを必ず report。差が 10% 以上なら smoothing 仮定の sensitivity を別添する。

**反例.** Pre-revenue 60% → Series A 30% を 1 年で切替 → 切替前年の最終 CF を 60% で割引、切替後は 30%。同じキャッシュフロー水準でも PV 比が 2 倍弱になり、IRR / NPV ベースの意思決定が大きく歪む。Linear ramp 3 年でこの歪みは半分以下に縮小する。

### 21.3 Currency Mismatch (通貨不一致と DCF)

**問題の所在.** 多くのスタートアップ DCF が次の不整合を抱える:

- 売上は USD (海外顧客中心) / 費用は JPY (日本拠点 OPEX) / Discount rate は USD ベース CAPM だが TV を JPY で計算
- インフレ率を「実質 (real)」で組んでいるのに名目 (nominal) discount rate を当てている
- Country risk premium (CRP) を加味するか否かで通貨プレミアムを二重計上している

これは結果として **valuation を 20-50% 歪める**。

**対処原則 (Damodaran 推奨).**

1. **キャッシュフローと割引率の通貨を一致させる** (currency consistency)。同じモデル内で USD CF を JPY rate で割引するなどは不可。
2. **名目 vs 実質も一致** (nominal-real consistency)。Nominal CF は nominal rate、real CF は real rate。
3. **CF を片方の通貨に統一して計算後、forward レートで換算する**のが正攻法。

**3 つの実装パターン.**

**(A) 単一通貨統合 (推奨デフォルト).**

すべての CF をプライマリ通貨 (例: 親会社報告通貨 JPY) に揃え、その通貨ベースの WACC で割引。

```
JPY_revenue(t) = USD_revenue(t) × FX_forward(USD/JPY, t)
JPY_cost(t)    = JPY_cost(t)        # native
JPY_FCF(t)     = JPY_revenue(t) - JPY_cost(t) - tax
PV             = sum( JPY_FCF(t) / (1 + WACC_JPY)^t )
```

Forward FX には interest rate parity (IRP) を使う:

```
FX_forward(t) = FX_spot × ((1 + i_JPY)^t / (1 + i_USD)^t)
```

ここで `i_JPY`, `i_USD` は同年限の risk-free rate。

**(B) 二重通貨並列 (sensitivity 用).**

USD CF を USD WACC で、JPY CF を JPY WACC で別々に PV 化し、最後に spot で合算。これは輸出企業の sensitivity check として補助的に。

**(C) PPP (購買力平価) ベース real model.**

ハイパーインフレ国 (例: トルコ、アルゼンチン) のスタートアップ評価で、nominal モデルが破綻する場合に使用。Real CF + real discount rate (= nominal - expected inflation) で構築。

**通貨タグ付けのデータ構造.**

```python
@dataclass
class CashFlow:
    period: int
    amount: float
    currency: Literal["USD", "JPY", "EUR", "..."]
    nominal_or_real: Literal["nominal", "real"]
    inflation_assumption: float | None   # real のとき必須
    fx_source: str                       # "spot 2026-04-30 BoJ" 等

def validate_consistency(cfs: list[CashFlow], discount_rate_currency: str, discount_rate_type: str):
    for cf in cfs:
        assert cf.currency == discount_rate_currency, "currency mismatch"
        assert cf.nominal_or_real == discount_rate_type, "nominal/real mismatch"
```

**Forward FX 簡易版 (年限 5-10 年).**

| 通貨ペア | 2026-04 spot | 期待インフレ差 (年率) | 5 年 forward (近似) |
|---|---|---|---|
| USD/JPY | 152 (illustrative) | US 2.3% - JP 1.8% = 0.5% | 152 × 1.005^5 ≈ 156 |
| EUR/JPY | 165 | EU 2.0% - JP 1.8% = 0.2% | 165 × 1.002^5 ≈ 166 |
| USD/EUR | 0.92 | 0.3% | 0.92 × 1.003^5 ≈ 0.93 |

注: 上記は説明用の概数で、最新の primary source (Bloomberg, Reuters, 中銀公表データ) で必ず再確認。

**為替リスクの hedging を割引率に折り込むか.**
- 自然ヘッジ (現地調達 + 現地販売) の比率を明示し、未ヘッジ部分のみ FX risk premium を加える方式が理論的にクリーン
- FX premium 目安: 主要通貨間で 0.5-1.5% / 新興国通貨で 2-5% (Damodaran "Country Risk")

**反例.** USD revenue を spot レートで JPY に換算 → 全期間同レート → JPY WACC 7% で割引。これは forward が無視されており、長期になるほど USD 高 / JPY 安バイアスが積み上がる (実際の forward は IRP により乖離する)。長期 DCF では forward 必須。

### 21.4 Negative EBITDA で multiple (赤字企業の評価)

**問題の所在.** スタートアップの大半は EBITDA が赤字。EV/EBITDA は分母が負だと:

- 計算結果が**負の倍率**になる (経済的に解釈不能)
- 分母 0 近傍では発散
- 「Multiple は使えない」と諦めて DCF だけに依存すると triangulation が失われる

**自動 fallback フロー.**

```
def select_multiple(financials, industry):
    if financials.ebitda > 0 and financials.ebitda > 0.05 * financials.revenue:
        return ("EV/EBITDA", multiples[industry]["ev_ebitda"])

    if industry == "saas":
        if financials.arr > 0:
            return ("EV/ARR", multiples["saas"]["ev_arr"])
        return ("EV/Revenue", multiples["saas"]["ev_revenue"])
    elif industry == "marketplace":
        return ("EV/GMV (× take_rate)", multiples["marketplace"]["ev_gmv"])
    elif industry == "fintech_lending":
        return ("P/Loan Book", multiples["fintech"]["p_loanbook"])
    elif industry == "fintech_payments":
        return ("EV/Net Revenue (= TPV × take_rate)", multiples["fintech"]["ev_netrev"])
    elif industry == "consumer_d2c":
        return ("EV/Revenue", multiples["consumer"]["ev_revenue"])
    elif industry == "biotech_preclinical":
        return ("rNPV (risk-adjusted NPV)", None)
    elif industry == "hardware":
        return ("EV/Revenue (or EV/Gross Profit)", multiples["hardware"]["ev_revenue"])
    return ("EV/Revenue", multiples["default"]["ev_revenue"])
```

**業態別 fallback metric 表 (EBITDA 不能時).**

| 業態 | 第 1 候補 (EBITDA+) | EBITDA 赤字時 fallback | 中央値レンジ |
|---|---|---|---|
| SaaS | EV/EBITDA | EV/ARR | 6-10x (Rule-of-40 達成は 8-15x) |
| SaaS (very early) | — | EV/Forward Revenue | 3-6x |
| Marketplace (asset-light) | EV/EBITDA | EV/GMV (= EV/Revenue × (1/take rate)) | take-rate 換算で EV/Revenue 4-12x |
| Fintech (lending) | P/E | P/Loan Book | 1.0-1.8x (ROE 連動) |
| Fintech (payments) | EV/EBITDA | EV/Net Revenue (= TPV × take rate) | 5-15x |
| Consumer / D2C | EV/EBITDA | EV/Revenue + LTV/CAC > 3 を条件 | 1.5-3.5x |
| Biotech (preclinical) | — | rNPV (per program) | 確率調整 |
| Biotech (Ph2-3) | — | EV/R&D pipeline | per-asset NPV |
| Hardware / IoT | EV/EBITDA | EV/Gross Profit | 12-25x (gross profit) |
| Crypto / Web3 | — | EV/Protocol Revenue, EV/TVL | DeFi で TVL 0.1-1.0x |
| Media / Content | EV/EBITDA | EV/Subscriber, EV/MAU | per-MAU $5-50 |
| Adtech | EV/EBITDA | EV/Net Revenue | 3-8x |

**Negative EBITDA を許容する条件 (EV/EBITDA を使い続ける条件).**

EBITDA が一時的赤字でも次のいずれかを満たす場合は、**Forward EV/EBITDA** (12-24 ヶ月先の予測 EBITDA を使う) で対応可能:

- Magic Number / Burn Multiple が改善トレンド
- EBITDA margin が直近 6 ヶ月で +5pt 以上改善
- LTV/CAC > 3 かつ payback < 18M
- Rule of 40 ≧ 40 (Growth + EBITDA Margin)

**重要な注意.**
- EV/Revenue を使うときも **growth-adjusted** で議論する。同じ EV/Revenue 5x でも、growth 50% と growth 10% では意味が違う。Bessemer の "Cloud Index" の Growth-adjusted multiple (EV/Revenue ÷ growth%) などの cross-check を必須化。
- ARR ≠ Revenue の場合 (SaaS で ASR や PSR を含むなど) は ARR の定義を必ず明記。
- Rule of 40 (Growth% + EBITDA margin% ≧ 40) との組み合わせで EV/ARR の見方を変えるのが現代的アプローチ。

**反例.** EBITDA -$10M で売上 $50M の SaaS。EV/EBITDA を機械的に計算すると EV = -$200M (multiple 20x) で意味不明。EV/ARR fallback で ARR $40M × 8x = EV $320M、Rule of 40 が 35 (growth 60% + margin -25%) なら multiple を 6x に落とすなどの adjustment が妥当。

### 21.5 Reverse DCF の Boundary (逆算成長率の妥当性)

**Reverse DCF とは.** 観測されている市場時価 (上場株価 / 直近ラウンドの post-money 等) を所与として、その評価額を正当化する **implied long-term growth rate** を逆算する手法。「市場はいくらの成長を織り込んでいるか」を可視化し、その期待が現実的かを評価する。

```
Market_Value = sum_(t=1..n) FCF(t) × g_implied^(t-1) / (1+WACC)^t
                + TV(g_implied) / (1+WACC)^n

→ g_implied について解く (numerical solver)
```

**Boundary 警告条件.**

| 警告レベル | 条件 | 推奨アクション |
|---|---|---|
| Critical | g_implied > GDP × 100 (倍率非現実) | 市場過熱 / モデル誤り疑い |
| Critical | g_implied > 50% (永続) | 永続成長としては数学的に近似 GDP 上限を破る |
| High | g_implied > GDP nominal × 3 (3 倍) | 業界 leading の高成長企業相当 |
| High | g_implied > risk-free rate × 5 | 高すぎる reinvestment 仮定 |
| Medium | g_implied > 一次予測期間の業界平均 growth × 1.5 | comp との乖離を要説明 |
| Low | g_implied < 0% | distressed / 縮小局面、survival 確率の検証必須 |

**実装ロジック.**

```python
def reverse_dcf_validate(market_value, fcf_forecast, wacc, horizon_years):
    g_implied = solve_for_growth(market_value, fcf_forecast, wacc, horizon_years)

    gdp_nominal = lookup_gdp_nominal_growth(country="us")  # e.g. 0.04
    rf = lookup_risk_free_rate(currency="usd", years=horizon_years)

    if g_implied > 0.50:
        raise ValuationError(f"g_implied={g_implied:.2%} > 50% — physically infeasible as terminal growth")
    if g_implied > gdp_nominal * 100:
        raise ValuationError("Implied growth > 100x GDP — sanity check failed")
    if g_implied > gdp_nominal * 3:
        warn(f"g_implied={g_implied:.2%} > 3x GDP ({gdp_nominal:.2%}); requires industry leadership thesis")
    if g_implied > rf * 5:
        warn(f"g_implied > 5x risk-free rate ({rf:.2%}); reinvestment assumption aggressive")
    if g_implied < 0:
        warn(f"g_implied={g_implied:.2%} negative — review survival probability and shrinkage scenario")

    return g_implied
```

**物理的上限の根拠 (Damodaran 推奨).**

- 永続的に GDP 成長を上回る企業は存在し得ない (上回り続ければ最終的に当該国 GDP を超える)
- スタートアップの予測期間 5-10 年では年 30-60% も可だが、その後の TV では必ず GDP nominal 以下に収束させる
- "Even Apple cannot grow at 20% forever" (Damodaran 2014 論考)

**Reverse DCF を使う場面.**

1. 上場株式の overvaluation/undervaluation 検証 (sanity check)
2. 直近ラウンド bridging round の妥当性検証
3. M&A bid 価格の implied growth を可視化
4. Comparable company の同質性確認 (peer 5 社の implied growth が大差ないかを比較)

**逆算 g の解釈フレーム.**

```
g_implied = base_case_g + risk_premium_implied + market_sentiment_premium
```

- `base_case_g` (内部予測): 業績計画ベース
- `risk_premium_implied`: 投資家が要求する追加成長
- `market_sentiment`: 市場心理 / ナラティブ要因

3 者を分解できれば、市場価格のうちどれだけが「期待の上振れ」かを見積もれる。

**反例.** 上場 SaaS 株価から逆算した g_implied = 35% (永続)。GDP 名目 4% に対して 8.75 倍 → critical 警告。実態は「予測 5 年 × 50% 成長 → TV g = 3% への減衰モデル」を暗黙に織り込んでいるはずで、単純 Gordon Growth で逆算すると過大に出る。Reverse DCF は **2 段階モデル** で行うのが正攻法 (高成長期 + perpetual TV)。

---

## 22. Stage Discount Rate Default (推奨デフォルト)

### 22.1 全体方針

スタートアップに **stage-only discount rate** を適用するのは「投資家の期待 IRR」と「事業内在の不確実性」を一本化するため簡便だが、**survival 確率の不連続性**を反映できないため誤差が大きい。本節では:

1. Stage × WACC range の表
2. Survival probability の表
3. **Risk-adjusted method を default とする** 推奨と reason
4. Stage-only を legacy として残す位置づけ

を整理する。

### 22.2 Stage × WACC × Survival の対応表

| Stage | WACC range | Default (中央値) | Survival probability | 主要 risk source |
|---|---|---|---|---|
| Pre-revenue (Idea / PoC) | 50-70% | **60%** | 10-30% | 製品仮説検証、PMF 未確認 |
| Early Revenue (Seed) | 40-60% | **50%** | 30-50% | 顧客獲得、retention 未検証 |
| Series A | 30-50% | **40%** | 50-70% | スケーラビリティ、unit economics |
| Series B | 25-40% | **32%** | 70-85% | 市場規模、competition |
| Series C | 20-30% | **25%** | 85-95% | execution、scale efficiency |
| Pre-IPO (Series D+) | 15-25% | **20%** | 95% | exit timing、market sentiment |
| Public (post-IPO) | 10-15% | **12%** | 100% | 通常の市場リスクのみ |

**根拠.** Damodaran "Valuing Young Firms" (Stern, 2009-2025 各年改訂) で示される VC implied IRR レンジを基準に、最近の VC リターン data (Cambridge Associates, NVCA Yearbook 2024-2025) で確認した経験値レンジ。Survival probability は CB Insights "Startup Failure Post-Mortem"、Wilbank-Boomtown "Startup Genome" のサバイバル統計を参照。**いずれも時点依存のため、最新データで再確認**。

### 22.3 Risk-Adjusted Method (推奨デフォルト)

**定義.** Stage discount rate を survival probability で「上乗せ調整」せずに、**base WACC ÷ survival probability** で expected value を割り戻すアプローチ。

```
Adjusted_Value = sum_t [ E(FCF_t) × Survival(t) ] / (1 + WACC_base)^t

# あるいは
WACC_effective = WACC_base / Survival(stage)   # 大雑把な近似
```

**正確な定式化 (Damodaran "Valuing Young Firms" §7).**

```
PV = (Probability of Survival × Going-concern Value) + (Probability of Failure × Distress Value)
   = p × DCF(success) + (1-p) × Liquidation_or_FireSale_Value
```

ここで:
- `DCF(success)` は通常の base WACC (10-15% 程度) で割引した going-concern PV
- `(1-p)` の失敗 scenario では distress value (典型的には 0 もしくは IP 売却額)
- `p` は stage 別 survival probability

**例: Pre-revenue (p = 0.20) の場合.**

```
PV = 0.20 × DCF_at_12pct + 0.80 × 0
   = 0.20 × DCF_at_12pct
```

これは「stage-only で WACC = 60% で割引した PV」と数学的にほぼ等価ではない (時点別の survival 割引が指数関数的に効くため)。

### 22.4 Stage-only と Risk-adjusted の差分 (重要)

**本書の主張.** 単一 discount rate で済ますなら **risk-adjusted method を default**。Stage-only は legacy として降格。

**Reason (定量比較).**

ある exit value V のシナリオ:

| 条件 | Stage-only (60% 割引) | Risk-adjusted (12% × p=0.5) |
|---|---|---|
| Exit value V (ベース) | V / 1.6^5 ≈ 0.10V | 0.5 × V/1.12^5 ≈ 0.28V |
| Exit value 0.5V (半減) | 0.5V / 1.6^5 ≈ 0.05V | 0.5 × 0.5V/1.12^5 ≈ 0.14V |
| 比率 (半減 / ベース) | **50% (0.05/0.10)** | **50% (0.14/0.28)** |

ここまでは同じ。**しかし survival 確率が変動した場合**:

| 条件 | Stage-only (60% 割引) | Risk-adjusted (12% × p=0.25) |
|---|---|---|
| Survival 50% → 25% に低下 | 反映できない (固定) | 0.25 × V/1.12^5 ≈ 0.14V |
| 価値変化 | 0% (反映なし) | **-50%** |

**結論.** Stage-only では **exit value の感度** (50% 半減 → -50%) は捉えられるが、**survival の感度** は割引率を変えない限り反映できない。Risk-adjusted は両方を直接モデル化する。

ある exit が 1/2 になっても survival 50% の前提で済ませると、実際 survival 25% への悪化は **追加で 50% の overvaluation** を生む。Stage-only だと「discount rate 60% で大丈夫」とブラックボックス化してしまう。

### 22.5 Risk-adjusted method 実装ガイド

```python
def risk_adjusted_value(
    fcf_forecast: list[float],          # going-concern FCF
    wacc_base: float,                   # mature company WACC, e.g. 0.12
    survival_prob: dict[int, float],    # year → cumulative survival prob
    distress_value: float = 0.0,
):
    pv_success = sum(
        fcf * survival_prob[t] / (1 + wacc_base)**t
        for t, fcf in enumerate(fcf_forecast, start=1)
    )
    # 単純化: distress は t=0 で評価
    pv_distress = distress_value * (1 - survival_prob[1])
    return pv_success + pv_distress
```

**Survival curve の組み立て (cumulative).**

| Year | Pre-rev start | Early-rev start | Series A start |
|---|---|---|---|
| 1 | 0.70 | 0.85 | 0.92 |
| 2 | 0.50 | 0.72 | 0.85 |
| 3 | 0.35 | 0.62 | 0.79 |
| 4 | 0.25 | 0.55 | 0.74 |
| 5 | 0.20 | 0.50 | 0.70 |

注: 各 stage の年率 hazard rate ≈ 1 - (5 年生存率)^(1/5)。Pre-rev 5 年生存 20% → 年 hazard 約 27%。

### 22.6 Stage-only を使い続けてよい状況 (legacy 容認条件)

- Term Sheet ネゴシエーション初期で「投資家側の希望 IRR」を簡易表現
- 比較用 (mature company の 12% との対比で stage premium を可視化)
- 監査レポートでの 2nd opinion 補強 (ただし risk-adjusted を main result とする)

**禁止条件.**
- 規制対応の 409A 評価書 (OPM/PWERM ベースが必須)
- 監査ファイル (auditable) に提出する formal valuation
- 異 stage transition を含む長期 DCF (path dependency が捉えられない)

### 22.7 信頼性タグ付け

各 default 値には以下を必ず付記:

```yaml
discount_rate:
  value: 0.40         # 40%
  source: "Damodaran 2024 Young Firms"
  vintage: "2024-Q1"
  industry_adjusted: true       # 業界 multiple での cross-check 済か
  survival_basis: "CB Insights startup failure 2024"
  confidence: "medium"          # high/medium/low
  override_reason: null         # 手動上書き時の理由
```

これにより監査時に「なぜこの数字を使ったか」が再現可能。

---

## 23. Liquidation Preference 評価手法選定基準

### 23.1 背景

優先株 (Preferred Stock) と普通株 (Common Stock) が混在する cap table で、各クラスの公正価値を分配するには、単純な per-share プロラタでは正しくない。Liquidation preference (LP)、participating right、conversion option、anti-dilution 等の付帯条件が経済的に効くため、以下のいずれかの専門手法を使う:

- **OPM (Option Pricing Method)**: 各 class を Black-Scholes 型 option として評価
- **PWERM (Probability-Weighted Expected Return Method)**: 複数の exit scenario に確率を付与して加重平均
- **Hybrid**: OPM ベースに PWERM scenario を上乗せ
- **Current Value Method (CVM)**: 即時清算価値ベース (限定用途のみ)

主要原典:
- AICPA "Valuation of Privately-Held-Company Equity Securities Issued as Compensation" Practice Aid (Aug 2013、改訂継続)
- ASC 718 / IRC §409A 関連の評価実務ガイド

### 23.2 手法選定 Decision Tree

| 状況 | 推奨手法 | 根拠 |
|---|---|---|
| Pre-Series B、exit scenario 多様で確率付与困難 | **OPM** | Black-Scholes ベースで連続的に全 scenario を表現。確率分布を仮定不要 (volatility にまとめて反映) |
| Pre-IPO、IPO/M&A の確率明確、業績予測信頼性高 | **PWERM** | 各 scenario に payoff × probability を直接指定でき、cap table 詳細を反映 |
| Series B-C、両特性が混在 | **Hybrid** | OPM で baseline、PWERM で IPO scenario を上書き / 上乗せ |
| Down round 直後、scenario が極めて狭く volatility 上昇 | **OPM** | volatility 反映、不確実性をパラメトリックに表現 |
| Public comp 豊富 / multiple 明確 / exit timing 確定的 | **PWERM** | exit value を直接 forecast 可能、市場 multiple との triangulation 容易 |
| 即時清算 / 解散決議直後 | **CVM** | 短期 horizon、option time value 無視可 |
| 重大な戦略変更直後で不確実性極大 | **OPM (with high vol)** | scenario 列挙が現実的に困難 |

### 23.3 意思決定の優先順位フロー

```
[Step 1] IPO 確率は明確に推定できるか?
  Yes → [Step 2] 業績 forecast の信頼性は?
    High  → PWERM (確率 × payoff)
    Low   → Hybrid (OPM baseline + PWERM IPO scenario)
  No  → [Step 3] Exit scenario が 2-3 に絞れるか?
    Yes → PWERM (シンプル分岐)
    No  → OPM (連続的に表現)

[Step 4] Down round / 大幅な評価変動が直近にあった?
  Yes → OPM 強推奨 (volatility が観測可)
  No  → 上記の選定継続

[Step 5] 監査 / 409A 提出用?
  Yes → 必ず Hybrid を考慮 (AICPA Practice Aid 推奨)
  No  → 内部用途は単一手法でも可
```

### 23.4 各手法の長所・短所

#### OPM (Option Pricing Method)

**前提.** Total equity value V を underlying asset、各 class の payoff threshold を strike price として、Black-Scholes で各 class の present value を算出。

**入力.**
- Total equity value V (前回ラウンド post-money 等)
- Volatility σ (上場 comp の equity volatility, 50-90% が標準レンジ)
- Time to liquidity T (typically 1-5 years)
- Risk-free rate r
- Cap table の breakpoints (各 class が payoff を受け始める閾値)

**長所.**
- Scenario 確率を陽に置かなくてよい (σ にすべて吸収)
- 業績 forecast 不要、既存資本構成のみで動く
- Down round / volatility 高い場面で堅牢

**短所.**
- σ の選定が結果を支配 (sensitivity 高い)
- IPO 特殊事情 (anti-dilution、IPO ratchet 等) を素直に反映しにくい
- Common stock の DLOM (Discount for Lack of Marketability) を別建てで考慮要

**Volatility 推定.** 上場 SaaS comp 5-10 社の 1-2 年 daily return から計算した equity vol を、leverage adjust (`σ_asset = σ_equity × E/(E+D)`) してから使うのが王道。新興企業はベース σ を 60-80% で出発し、業界・stage で調整。

#### PWERM (Probability-Weighted Expected Return Method)

**前提.** 主要 exit scenario (IPO / strategic M&A / financial M&A / dissolution) を列挙し、それぞれの payoff を per-class 計算後、確率で加重平均。

**入力.**
- 各 scenario の time horizon、exit value、確率
- 各 scenario における cap table の payout waterfall

**長所.**
- 直感的で経営陣に説明しやすい
- 各 scenario の cap table 効果を陽に表示できる
- Exit 確率を投資家・経営陣の合意で変えやすい

**短所.**
- Scenario 確率に大きな主観が入る (auditable 性で課題)
- Volatility / option value を捉えづらい (一律確率の sum に潰れる)
- Scenario 数が増えると計算負荷とエラーが増える

#### Hybrid

OPM (baseline) + PWERM (IPO scenario の上書き / 上乗せ)。AICPA Practice Aid が「非上場企業価値評価で広く採用される実務的妥協」と位置づける手法。

**典型的な適用.**
- IPO scenario (確率 30-50%) を PWERM で詳細にモデリング
- それ以外の scenario (M&A, dissolution 等) を OPM で連続的に評価
- 加重和を最終 fair value とする

**長所.** 主観 (IPO) と客観 (OPM) のバランス、auditable 性高
**短所.** モデル複雑化、二重カウントの監査ポイントあり

#### CVM (Current Value Method)

即時清算前提で、現時点の equity value を waterfall でそのまま分配。

**適用条件.**
- 解散・清算が確定 / 高確度
- 短期 (< 6M) liquidation event
- Option value が無視できる (deep ITM / OTM のいずれか)

それ以外は使わない (歴史的 default だが現代では推奨されない)。

### 23.5 観点別 (創業者 vs 投資家) の選好

**創業者観点.**
- **PWERM 選好**: capped participation の上限が common stock の取り分を増やす効果を陽に反映
- 高 IPO scenario のもとで common stock の payoff を最大化する argument
- ただし 409A purposes では PWERM のみだと過小評価リスクあり

**投資家観点.**
- **OPM 選好**: 下落 protection (LP) の option value を full reflect
- Volatility が大きい局面で preferred の floor 効果を価値化できる
- Down round 時の re-pricing で OPM の re-run が定着

**監査人 / 409A 評価人観点.**
- Hybrid 強推奨 (AICPA Practice Aid 準拠)
- 単一手法は exception report 必須

### 23.6 実装 / 報告における注意点

1. **Breakpoint 計算の transparency**: cap table breakpoints は手計算 / Excel 監査ログを必ず保存。OPM の各 tranche payoff が再現可能であること。
2. **Volatility 出典**: comp 選定基準と数値計算ログを残す。
3. **Scenario 確率 (PWERM)**: 経営陣 + 取締役会 の合意プロセスを記録。investor side / common side の両方の同意を得るのが理想。
4. **DLOM**: OPM 結果に対して別建てで 10-30% を割り引く実務が一般的 (Empirical Studies: 国内非上場 30%、海外 SaaS 20% 前後)。AICPA Practice Aid §11 参照。
5. **時点感度**: 評価日と次回ラウンドの間隔が 6M を超えると stale。再評価必須。

### 23.7 監査済 sample な選定例

| ケース | 業態 / Stage | 選定 | 理由 |
|---|---|---|---|
| (a) Series A SaaS、PMF 確認、Public SaaS comp あり | OPM (σ = 65%, T = 4y) | Public comp で σ 推定可、scenario 多様 |
| (b) Pre-IPO Fintech、IPO 12M 以内 | Hybrid | IPO scenario 確率 60% を PWERM、残り 40% を OPM |
| (c) Down round 直後 marketplace | OPM (σ = 80%, T = 3y) | 評価変動大、scenario 困難 |
| (d) M&A 入札進行中 (LOI 受領済) | PWERM (M&A 70% / IPO 10% / failure 20%) | scenario 限定、確率明確 |
| (e) Series B Biotech (Ph2 待ち) | Hybrid + rNPV cross-check | 試験成功確率を rNPV、市場価値を OPM |

---

