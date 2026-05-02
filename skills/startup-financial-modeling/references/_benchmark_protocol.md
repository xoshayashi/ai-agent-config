---
name: benchmark_protocol
description: メトリクス benchmark を skill 内に hard-code せず、build 時に research agent を dispatch して primary source (Pacific Crest / OpenView / KeyBanc / ChartMogul / 各社 IR) から fresh 値を取得する canonical protocol。陳腐化する事実 (benchmark / comp multiple / tax rate / WACC 構成要素) と不変な概念定義を分離する設計の正本
type: reference
priority: P0
related: [02_saas_metrics, 03_business_models, 18_customer_value_and_pricing, 19_ma_exit_for_founders, _self_review_protocol, _terminology, sanity_checks]
---

# Benchmark Protocol — On-Demand Research Dispatch

このドキュメントは、本 skill における **「陳腐化する数値事実」のガバナンス正本**である。

skill 構築チームが benchmark を skill 内に hard-code し続けると、(a) 1 年以内に値が陳腐化し、(b) 出典が曖昧になり、(c) 更新責任が不明になり、(d) IC memo の defensibility が毀損する。本 protocol は、陳腐化する benchmark を skill 内 SSoT に固めるのではなく、**build 時に毎回 research agent を dispatch して primary source から fresh data を取得**する手続きを canonical 化する。

> **対比メモ**: `_terminology.md` は不変な概念定義 (NRR の式、SAFE 転換式、IB 機能色) の SSoT。本 file は陳腐化する数値 (NRR median %、EV/Rev multiple、risk-free rate) の取得手続きの SSoT。両者は補完関係にあり、置換関係ではない。

---

## §1. 設計原則 — 事実と手続きの分離

### 1.1 「陳腐化する事実」と「不変な概念」の分離

financial modeling reference に登場する数値・事実は、**半減期 (half-life)** によって性質が大きく異なる。本 skill ではこれを 3 階層で管理する。

| 階層 | 半減期 | 例 | 管理場所 |
|---|---|---|---|
| Tier 0 (不変) | ∞ | NRR の式、SAFE 転換式、`#0000FF` = hard input、IFRS 8 segment 概念 | `_terminology.md` / 各 reference 本文 |
| Tier 1 (中期) | 5+ 年 | 業態構造の典型値、適格組織再編の要件、日本実効税率の "31.52%" 構成、WACC の理論式 | reference 本文に hard-code OK (改訂履歴必須) |
| Tier 2 (短命) | < 1 年 | Pacific Crest annual SaaS survey の median、公開 SaaS comp の EV/Rev、risk-free rate、industry beta、long-term GDP growth forecast | **本 protocol で都度取得 (skill 内 hard-code 禁止)** |

**rationale**:
- Tier 0 は 5 年経っても変わらない概念定義。skill 内の SSoT 化が defensibility を高める。
- Tier 1 は 5 年スパンで安定。reference 本文に hard-code し、改訂履歴で governance する。
- Tier 2 は **3-12 ヶ月で陳腐化**。skill メンテナのみが更新責任を持つ設計は scale しない。**agent dispatch なら "always fresh"**。

### 1.2 設計の rationale (なぜ skill 内に焼き込まないか)

1. **更新責任の分散**: skill maintainer が 50+ 数値を年次 update する負荷は持続不能。dispatch なら build 時に最新値が降ってくる。
2. **出典の defensibility**: skill 内 hard-code は出典 trace が劣化する (どの survey の何年版か)。dispatch なら snapshot に source URL + N + year が常に残る。
3. **rebuild の信頼性**: 同じ案件を 6 ヶ月後に re-evaluate する時、cache snapshot 比較で benchmark drift を可視化できる。
4. **multi-source triangulation**: 1 source の bias を avoid するため複数 source を median で集約する手続きが、build 時 dispatch なら自然に組み込める。

### 1.3 「protocol-as-canonical」の意味

本 file は「benchmark の値」を持たない。代わりに「**どう取得するか**」「**いつ取得するか**」「**どの source を信頼するか**」「**どう cache するか**」「**どう sanity_check と統合するか**」を canonical 化する。

> 値そのものが必要な build 時には、本 file の §3 prompt template を参照して research agent を dispatch する。本 file 自体は値を保有しない。

---

## §2. Trigger Condition — いつ Benchmark Agent を Dispatch するか

### 2.1 MUST trigger (dispatch 必須)

以下のシナリオでは、build orchestrator は **必ず** benchmark research agent を dispatch しなければならない。

| トリガー | 必要な benchmark | dispatch する prompt |
|---|---|---|
| `scripts/sanity_checks.py` の S1-S10 (旧 H1-H16 の soft 拡張) で quartile 判定が必要 | Magic Number / Burn Multiple / Rule of 40 / NRR / LTV/CAC の median + top quartile | §3.1 SaaS metric benchmark |
| IC memo §"Performance vs Industry Benchmark" 生成 | 案件業態 × stage に該当する 5-7 個の SaaS metric | §3.1 を 5-7 並列 |
| `11_KPI_Dashboard` シートの benchmark 列 populate | KPI に対応する quartile 値 | §3.1 を 5-10 並列 |
| `09_DCF` で WACC 計算 | risk-free rate / market premium / industry unlevered beta | §3.3 |
| `10_Comps` で公開 SaaS の median EV/Rev / EV/EBITDA 取得 | 業態 × growth × ARR 帯に合致する 5-10 社 sample | §3.2 |
| `09_DCF` の terminal growth 議論 | long-term real GDP growth (region 別) | §3.5 |
| `12_tax_strategy` で cross-border 構造の effective rate 検証 | 国別 corporate / capital gains / withholding / treaty | §3.4 |
| `19_ma_exit_for_founders §11` の earn-out probability (Bayesian) | 業態別 earn-out 達成率 base rate | §3.1 (custom: earn-out base rate metric) |
| `18_customer_value_and_pricing §3.2` の payback benchmark 比較 | 業態別 customer payback months median | §3.1 (custom: customer payback metric) |

### 2.2 SHOULD NOT trigger (固定値で済む)

以下は dispatch 不要。reference 内 hard-code 値または `_terminology.md` の SSoT を直接利用する。

| ケース | 固定値の所在 | 理由 |
|---|---|---|
| NRR の数式自体 (`(期初 ARR + Expansion - Contraction - Churn) / 期初 ARR`) | `_terminology §6.1` | Tier 0、不変 |
| SAFE 転換式 (`Conversion = Next Round × (1 − Discount)`) | `_terminology §4` | Tier 0、不変 |
| 法人実効税率 31.52% (日本大企業 2026 年度〜) | `_terminology §7` | Tier 1、構成は法令で 5+ 年安定 (年次変動は§7改訂履歴で管理) |
| sheet naming (`04_IS`, `05_BS`, `09_DCF`, ...) | `_terminology §3` | skill 規約、Tier 0 |
| IB 機能色 (`#0000FF` hard input 等) | `_terminology §1` | 業界標準、Tier 0 |
| Magic Number の `×4 で年率化` ルール | `_terminology §6.3` | 計算規則、Tier 0 |
| 7_japan_specifics の役員報酬の損金算入要件 | `07_japan_specifics §X` | 法令、Tier 1 |
| ARR ステージ別 entry 範囲 ($1-3M for Series A) | `_terminology §6.2` | Tier 1 (5 年スパンで安定) |

### 2.3 判断フローチャート

```
benchmark 値が build 中に必要になった
  ↓
Q1: 値そのもの (median %, multiple, rate) か、概念定義 (式・規則) か?
  ├── 概念定義 → _terminology.md 参照 (dispatch 不要)
  └── 値そのもの →
        Q2: 半減期は?
          ├── ≥ 5 年 (構造的) → reference 本文 hard-code (dispatch 不要)
          └── < 1 年 (市場依存) →
                Q3: cache TTL 内 (§4.1) で同条件 entry 存在?
                  ├── Yes & IC memo 用途でない → cache 利用
                  └── No or IC memo 用途 → §3 prompt template で dispatch
```

### 2.4 例外: dispatch 失敗時の fallback

WebSearch rate limit / source paywall / 完全 fail 時は §10.2 の fallback chain (Tier 1 fail → Tier 2 → expired cache → "benchmark unavailable" status を sanity_check に記録) に従う。**hard-code 値への暗黙 fallback は禁止** (defensibility 毀損)。

---

## §3. Dispatch Prompt Template

build orchestrator から research agent を起動する際の **完成形 prompt template** を 5 種類定義する。各 template は (a) 必要 input、(b) 出力 JSON スキーマ、(c) source tier 指示、(d) tool budget を明示する。

### 3.1 SaaS Metric Benchmark Prompt

最も頻度高い template。NRR / Magic Number / Burn Multiple / Rule of 40 / LTV/CAC / Gross Margin / Sales Efficiency / Payback / Net New ARR Growth に対応。

```
あなたは VC fund analyst です。次の SaaS metric の {YYYY} 年最新 benchmark を調査してください。

【調査対象】
Metric: {metric_name}            (例: Net Revenue Retention / Burn Multiple / Magic Number / Rule of 40 / LTV/CAC / Gross Margin / CAC Payback)
Business model: {business_model} (例: B2B SaaS / Vertical SaaS / SMB SaaS / Enterprise SaaS / PLG / Marketplace / Fintech)
Stage: {stage}                   (例: Pre-Seed / Seed / Series A / Series B / Series C+ / Growth / Pre-IPO)
Region: {region}                 (例: US / Japan / Europe / Global)
ARR band (任意): {arr_band}      (例: $1-5M / $5-20M / $20-50M / $50M+)

【要求】
1. **3 値必須**: Top quartile (75 percentile) / Median (50 percentile) / Bottom quartile (25 percentile)。N 不明な場合は明示
2. **Source は Tier 1 を優先**:
   - Tier 1 (一次): Pacific Crest / OpenView / KeyBanc SaaS Survey / ChartMogul / Bessemer State of Cloud / SaaS Capital / Scale Studio / Gainsight / a16z (data report のみ)
   - Tier 2 (二次): Tomasz Tunguz blog (data-driven post)、Battery Ventures、Insight Partners report、Carta benchmarks
   - Tier 3 (三次): 中堅 VC / Angel blog のうち data 引用元が明示されているもの
   - Tier 4 (回避): Twitter post / 個人 anecdote / podcast 引用のみ → 採用禁止
3. **メタデータ必須**: Sample size N、data collection year、survey published year、business model split 有無、stage split 有無
4. **Source URL / DOI**: 全 source に対して必ず URL を記録 (paywall でも URL 記録)
5. **複数 source 一致時**: 最新かつ N 大の source を primary、他を triangulation として記録。値が乖離する場合 (top quartile の差 > 30%) は両方記録 + caveats
6. **Year currency**: 直近 12 ヶ月以内の data を優先、24 ヶ月超は "stale" として flag

【出力 format (JSON、strict)】
{
  "metric": "{metric_name}",
  "business_model": "{business_model}",
  "stage": "{stage}",
  "region": "{region}",
  "arr_band": "{arr_band or null}",
  "year_data_collected": 2025,
  "year_published": 2025,
  "top_quartile": 1.5,
  "median": 1.0,
  "bottom_quartile": 0.5,
  "n": 350,
  "source_tier": 1,
  "source_name": "Pacific Crest 2025 SaaS Survey",
  "source_url": "https://...",
  "secondary_sources": [
    {"name": "ChartMogul SaaS Trends 2025", "url": "https://...", "median": 1.05, "n": 800}
  ],
  "caveats": "Survivor bias / opt-in survey / Series A 以下は N=42 と少ない",
  "fetched_at": "2026-05-02T10:30:00Z",
  "agent_version": "v1.0"
}

【tool budget】
- WebSearch: 5-8 query 以内
- WebFetch: 3-5 page 以内
- 1 metric につき 5 分以内に完了
- 深追い禁止 (median が出たら止まる)
```

### 3.2 Comp Multiple Prompt (10_Comps 用)

```
{date} (例: 2026-05-02) 時点の公開 SaaS company で、以下条件を満たす peer 5-10 社の EV/Revenue / EV/EBITDA / EV/ARR multiple を取得してください。

【絞り込み条件】
- Region: {region}                       (例: US / Japan / Global)
- Listing: 公開市場 (Nasdaq / NYSE / TSE Prime / TSE Growth 等)
- Revenue growth (latest YoY): {growth_min}% 以上 (例: 30%)
- Revenue scale: {revenue_min} ≤ TTM Revenue ≤ {revenue_max} (例: $50M-$2B)
- Business model: {business_model}        (例: Vertical SaaS / B2B Horizontal SaaS / Marketplace)
- 上場期間: 直近 IPO (12 ヶ月以内) は除外可 (post-IPO volatility 排除)

【要求】
1. 各社 ticker / market cap / TTM revenue / TTM ARR (推定可) / latest YoY growth / Rule of 40 / EV / EV/Rev / EV/EBITDA
2. Median / 75 percentile / 25 percentile を計算 (peer 5 社未満の場合は計算せず "insufficient_n" flag)
3. EV は market cap + total debt − cash (= net debt + equity) で算出
4. 出典は IR / 10-K / 10-Q / Yahoo Finance / Capital IQ priority、推定値 (consensus 等) は flag
5. 競合除外時は理由明示 (例: "Adobe は scale 違いで除外")
6. 業態 mismatch (例: Vertical SaaS 案件で Horizontal Saas 引用) は除外、または比較注記必須

【出力 format (markdown table + JSON summary)】
| Ticker | Company | Region | TTM Rev ($M) | YoY Growth | Rule of 40 | EV ($M) | EV/Rev | EV/EBITDA |
|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ...% | ... | ... | ...x | ...x |

JSON summary:
{
  "comp_set_size": 7,
  "median_ev_revenue": 9.2,
  "p75_ev_revenue": 13.5,
  "p25_ev_revenue": 6.0,
  "median_ev_ebitda": 32,
  "filter_criteria": {...},
  "fetched_at": "2026-05-02T10:30:00Z",
  "excluded_with_reason": [{"ticker": "ADBE", "reason": "scale mismatch (>$10B revenue)"}],
  "data_source": "Yahoo Finance + 10-K filings",
  "fetched_at_macro_event": null  // 例: "post-SVB crash" 等の macro 文脈
}

【tool budget】
- WebSearch: 8-12 query
- WebFetch: 5-7 page (各社 IR)
- 7 分以内
```

### 3.3 Risk-Free Rate / Market Premium / Beta Prompt (DCF WACC 用)

```
{date} 時点の {region} (US / JP / EU / Other) における以下 3 値を取得してください。

【調査対象】
1. **Risk-free rate (Rf)**: 10-year government bond yield (US: Treasury / JP: 国債 / EU: Bund 等)
   - 直近 1 週間平均、現在値、過去 12 ヶ月レンジを記録
2. **Equity risk premium (ERP)**:
   - **Historical**: 1928-current の long-run average (Damodaran NYU Stern data 推奨)
   - **Implied**: current implied ERP (Damodaran monthly update)
   - 両方記録 (DCF では implied を primary、historical を sanity check)
3. **Industry beta (unlevered)**: 公開 SaaS sample で計算
   - {business_model} (B2B SaaS / Vertical SaaS / Fintech / etc.) の peer 10-20 社
   - Unlevered beta = levered beta / (1 + (1-tax) × (D/E))
   - Median を採用、range も記録

【source priority】
- Tier 1: FRED (US Treasury data / 米国 macro), 日銀 (日本国債), ECB (Bund), Damodaran NYU Stern data, Bloomberg consensus
- Tier 2: Yahoo Finance, Investing.com, 各国 central bank 公式サイト
- Tier 3: 経済紙 (WSJ / Nikkei) の引用値

【出力 format (JSON)】
{
  "region": "{region}",
  "as_of_date": "2026-05-02",
  "risk_free_rate": {
    "ticker": "US10Y",
    "current": 0.0420,
    "trailing_12m_low": 0.0380,
    "trailing_12m_high": 0.0480,
    "source": "FRED DGS10",
    "url": "https://fred.stlouisfed.org/series/DGS10"
  },
  "equity_risk_premium": {
    "historical_avg": 0.0535,
    "historical_period": "1928-2025",
    "historical_source": "Damodaran",
    "implied_current": 0.0510,
    "implied_source": "Damodaran monthly update May 2026"
  },
  "industry_beta": {
    "business_model": "B2B SaaS",
    "peer_count": 18,
    "unlevered_beta_median": 1.30,
    "unlevered_beta_range": [0.95, 1.65],
    "tax_rate_assumed": 0.21,
    "source": "Damodaran industry data + custom calc"
  },
  "fetched_at": "2026-05-02T10:30:00Z"
}

【tool budget】WebSearch 6-8、WebFetch 4-5、6 分以内
```

### 3.4 Tax Rate / Treaty Prompt (12_tax_strategy 用)

```
{country} の {entity_type} (法人 / 個人 / pass-through) に対する {YYYY} 年の以下 rate を取得してください。

【調査対象】
1. Corporate tax (国法人税) — 大企業 / 中小企業 区分
2. Local tax (地方税 / 州税)
3. Effective combined rate (国 + 地方 + 復興/防衛等 surcharge)
4. Capital gains tax — 個人 / 法人 / 長短期区分
5. Dividend withholding (cross-border) — domestic / treaty rate
6. Treaty rate (cross-border specific): {country_A} ↔ {country_B} (例: JP-US, US-DE)
7. R&D tax credit / startup incentive (該当時のみ): 制度名 + 上限 + 適用要件 概要

【source priority】
- Tier 1: 国税庁 (NTA), IRS, HMRC, BMF (DE), Bundesfinanzhof, OECD treaty database, 各国財務省一次資料
- Tier 2: Big 4 (PwC / EY / KPMG / Deloitte) Worldwide Tax Summary、IBFD database
- Tier 3: 各国大手会計事務所の解説記事

【出力 format (JSON)】
{
  "country": "{country}",
  "entity_type": "{entity_type}",
  "tax_year": 2026,
  "corporate_tax": {
    "national_rate": 0.232,
    "local_rate": 0.0680,
    "surcharge_rate": 0.005,
    "effective_combined": 0.3152,
    "components_note": "法人税 23.2% + 地方法人税 1.52% + 法人住民税 1.62% + 法人事業税 5.18% + 防衛特別法人税 (2026.4〜)"
  },
  "small_business_rate": 0.21,
  "small_business_threshold": "年所得 800万円以下部分",
  "capital_gains": {
    "individual_long_term": 0.20315,
    "individual_short_term": 0.20315,
    "corporate": 0.3152,
    "note": "日本では長短期区分なし、上場 vs 非上場で扱い相違"
  },
  "dividend_withholding": {
    "domestic": 0.20315,
    "treaty_rates": {
      "US": 0.10,
      "DE": 0.15,
      "SG": 0.05
    }
  },
  "rd_credit": {
    "name": "総額型 + オープンイノベ型",
    "max_credit_rate_of_corporate_tax": 0.40,
    "qualification": "..."
  },
  "fetched_at": "2026-05-02T10:30:00Z",
  "primary_source_url": "https://www.nta.go.jp/..."
}

【tool budget】WebSearch 5-8、WebFetch 3-5、6 分以内
【caveat】 Treaty rate は protocol 種別 (BEPS MLI 適用後) を必ず明示
```

### 3.5 Long-Term GDP Growth Prompt (DCF terminal growth 用)

```
{region} の long-term real GDP growth (DCF terminal growth proxy) を取得してください。

【調査対象】
1. Historical long-run average: 直近 10 年 / 20 年 / 30 年 各レンジ
2. Forecast: IMF WEO / World Bank GEP / OECD Outlook の 5 年 forward + 10 年 forward
3. Inflation: same period の CPI / GDP deflator (real → nominal 変換用)
4. Caveats: demographic decline (Japan 等)、productivity slowdown、structural shift

【source priority】
- Tier 1: IMF WEO (World Economic Outlook), World Bank GEP (Global Economic Prospects), OECD Economic Outlook, BIS, 各国中央銀行 forecast
- Tier 2: Eurostat / BEA / 内閣府 / 統計局
- Tier 3: 主要金融機関の長期予測 (Goldman / JP Morgan / Nomura research)

【出力 format (JSON)】
{
  "region": "{region}",
  "as_of_date": "2026-05-02",
  "historical_real_gdp_growth": {
    "trailing_10y": 0.018,
    "trailing_20y": 0.020,
    "trailing_30y": 0.022,
    "data_source": "World Bank WDI"
  },
  "forecast_real_gdp_growth": {
    "next_5y_avg": 0.017,
    "next_10y_avg": 0.015,
    "long_run_potential": 0.012,
    "data_source": "IMF WEO Apr 2026"
  },
  "inflation_assumption": {
    "trailing_10y_cpi": 0.0220,
    "central_bank_target": 0.0200,
    "data_source": "BLS / 日銀 / ECB"
  },
  "terminal_growth_recommendation": {
    "for_dcf": 0.020,
    "rationale": "long-run nominal (real 1.5% + inflation 2.0%) を上限。WACC との spread が 200bp 以上必要 (`05 §1.6`)"
  },
  "caveats": [
    "Japan: demographic decline で real growth は 0.5-1.0% 予測、nominal 1.5-2.0%",
    "US: AI productivity boost で +0.5-1.0% upside scenario あり (Goldman 2025 report)"
  ],
  "fetched_at": "2026-05-02T10:30:00Z"
}

【tool budget】WebSearch 5、WebFetch 3、5 分以内
```

---

## §4. Caching Strategy

### 4.1 Cache Validity Period (TTL Table)

dispatched benchmark には用途別の TTL (time-to-live) を設定する。TTL 内であれば cache 値を再利用、超過時は **必ず re-dispatch**。

| Data type | Cache TTL | Re-dispatch trigger |
|---|---|---|
| Pacific Crest annual SaaS survey (NRR / Burn / Magic / Rule of 40 quartile) | 12 mo | Q3 each year (annual survey release) |
| OpenView / KeyBanc SaaS Survey | 12 mo | Q2-Q3 release |
| ChartMogul / Scale Studio public benchmark | 6 mo | quarterly update |
| Risk-free rate (US10Y / JP10Y) | 1 wk | macro event (FOMC / 日銀 / ECB 決定) |
| Equity risk premium (Damodaran implied) | 1 mo | monthly update by Damodaran |
| Industry beta | 3 mo | quarterly recalc |
| Comp multiple (個別企業) | 1 mo | major M&A / earnings release |
| Comp set median (5-10 社) | 2 wk | broad market correction (>10% within 2 wk) |
| Tax rate (national + local) | 12 mo | budget / tax legislation passage |
| Treaty rate | 24 mo | MLI / BEPS update |
| GDP growth forecast (IMF WEO) | 6 mo | IMF WEO update (Apr / Oct) |
| GDP growth forecast (World Bank GEP) | 6 mo | GEP update (Jan / Jun) |
| R&D tax credit (rate / cap) | 12 mo | budget cycle |
| Earn-out base rate (M&A) | 12 mo | annual deal study release (PitchBook / SRS Acquiom) |
| Customer payback months (業態別) | 6 mo | semi-annual SaaS benchmark refresh |

### 4.2 Cache Location

#### 4.2.1 案件単位 cache snapshot
- 各案件の `<project_root>/audits/benchmark_cache_{YYYYMMDD}.json` に保存
- model build 完了時に自動 snapshot
- 案件固有のため skill 内には保存しない (cross-project leakage 回避)

#### 4.2.2 Skill 内には保存しない原則
- skill `references/` 配下に benchmark 値を保存することは **禁止**
- 例外: `21_metric_benchmarks.md` (もし既存) は **starter cache / fallback** 扱いで保管可。ただし IC memo build 時は本 protocol で fresh 取得が **primary**、starter cache は dispatch fail 時の last-resort fallback (§10.2)。

#### 4.2.3 Cache JSON schema
```json
{
  "schema_version": "1.0",
  "project_id": "saas_acme_seriesB_20260502",
  "build_timestamp": "2026-05-02T10:30:00Z",
  "benchmarks": [
    {
      "benchmark_id": "saas_metric/nrr/series_b/us",
      "metric": "NRR",
      "context": {"business_model": "B2B SaaS", "stage": "Series B", "region": "US"},
      "values": {"top_quartile": 1.30, "median": 1.15, "bottom_quartile": 1.05, "n": 280},
      "source": {"tier": 1, "name": "Pacific Crest 2025 SaaS Survey", "url": "https://..."},
      "fetched_at": "2026-05-02T10:31:00Z",
      "ttl_until": "2027-05-02T10:31:00Z",
      "agent_version": "v1.0"
    }
  ]
}
```

### 4.3 Re-Dispatch Rule

| 用途 | cache 利用可否 |
|---|---|
| **IC memo 作成 / final 出力** | **必ず full fresh dispatch** (cache 利用不可)。IC committee / LP 説明 / 投資家提示の場面では最新 data 必須、defensibility が最重要 |
| internal modeling iteration (driver 調整、scenario test) | TTL 内なら cache OK |
| "what-if" sensitivity analysis | cache OK (相対的差異が target、絶対値ではない) |
| portfolio re-eval (既存投資の四半期 review) | quarterly 単位で fresh dispatch、ただし full re-dispatch ではなく前回 snapshot の delta dispatch 可 |
| crisis re-evaluation (macro event 発生時) | **必ず fresh dispatch** (前回 cache の前提が破綻している可能性) |

### 4.4 Cache Hit / Miss Logic

```python
def get_benchmark(metric_id, context, *, force_fresh=False, ic_memo_mode=False):
    """
    Returns benchmark dict, dispatching only if cache miss or stale.
    """
    if ic_memo_mode or force_fresh:
        return dispatch_benchmark(metric_id, context)  # always fresh
    cached = load_cache(metric_id, context)
    if cached and not is_stale(cached, ttl_table[metric_id]):
        return cached
    return dispatch_benchmark(metric_id, context)
```

---

## §5. Integration with sanity_checks.py

### 5.1 既存実装の確認

`scripts/sanity_checks.py` の `_check_soft_all` (line 1209-) では Magic Number / Burn Multiple / Rule of 40 / NRR / LTV/CAC の各 soft check で threshold が **hard-code** されている (例: `Magic Number: threshold=0.4 below`)。

これは `_terminology §6.1` で同期された PASS/WATCH/FAIL 閾値と一致しているが、**top quartile 値** や **業態別 stage 別 quartile** は反映されていない。本 protocol との統合では、top quartile + median を runtime に injection する API に拡張する。

### 5.2 改修例: Before / After

#### 5.2.1 Before (現行)

```python
def _check_soft_all(wb, vwb, report):
    _soft_check_threshold(
        report=report,
        check_id="S1", section="Magic Number",
        label="Magic Number", threshold=0.4, direction="below",
        rationale="< 0.4 = poor S&M efficiency",
    )
```

#### 5.2.2 After (benchmark injection 対応)

```python
def _check_soft_all(
    wb,
    vwb,
    report,
    *,
    benchmarks: dict[str, dict] | None = None,
):
    """
    benchmarks: § 3.1 prompt template の出力 JSON を metric_id (例: "magic_number")
    で索引化した dict。build_model.py がここに inject する。
    None の場合は absolute threshold のみで check (legacy 動作)。
    """
    benchmarks = benchmarks or {}

    # Magic Number — quartile-aware check
    mn_bench = benchmarks.get("magic_number")
    _soft_check_with_benchmark(
        report=report,
        check_id="S1", section="Magic Number",
        label="Magic Number",
        absolute_threshold=0.4,           # ← _terminology §6.1 PASS/FAIL 境界 (Tier 0、固定)
        absolute_direction="below",
        benchmark=mn_bench,                # ← runtime injection、Tier 2
        rationale=(
            "absolute: < 0.4 = poor S&M efficiency。benchmark 提供時は "
            "top_quartile / median 比較も追加"
        ),
    )

    # 同様に Burn Multiple / Rule of 40 / NRR / LTV/CAC...
```

### 5.3 Helper Function (新設)

```python
def _soft_check_with_benchmark(
    *,
    report,
    check_id: str,
    section: str,
    label: str,
    absolute_threshold: float,
    absolute_direction: str,
    benchmark: dict | None,
    rationale: str,
):
    """
    1. Always: absolute threshold check (Tier 0 安全網)
    2. If benchmark provided: top_quartile / median との比較を追加 finding として report
    3. Benchmark 出典 (source_name + N + year) を recommendation に埋め込む
    """
    val = _read_kpi_value(_soft_check_with_benchmark._wb, label)
    if val is None:
        report.add(CheckResult(
            check_id=check_id, status="info", section=section,
            message=f"{label} not found in workbook (skip benchmark compare)"
        ))
        return

    # Step 1: absolute check (Tier 0 hard threshold)
    if absolute_direction == "below" and val < absolute_threshold:
        absolute_status = "fail"
    elif absolute_direction == "above" and val > absolute_threshold:
        absolute_status = "fail"
    else:
        absolute_status = "pass"

    # Step 2: benchmark compare (if provided)
    if benchmark is None:
        report.add(CheckResult(
            check_id=check_id,
            status=absolute_status,
            section=section,
            actual=val, expected=absolute_threshold,
            message=f"{label} = {val:.2f} (absolute check only; benchmark not provided)",
            recommendation=(
                "Pass --benchmark JSON to enable quartile-aware check. "
                "See `_benchmark_protocol §6` for build_model.py integration."
            ),
        ))
        return

    top = benchmark["top_quartile"]
    median = benchmark["median"]
    bottom = benchmark["bottom_quartile"]
    src = benchmark["source_name"]
    n = benchmark["n"]
    year = benchmark.get("year_data_collected", "n/a")

    if val >= top:
        quartile_label = "Top quartile"
        bench_status = "pass"
    elif val >= median:
        quartile_label = "Above median"
        bench_status = "pass"
    elif val >= bottom:
        quartile_label = "Below median"
        bench_status = "warn"
    else:
        quartile_label = "Bottom quartile"
        bench_status = "fail"

    # 最も厳しい status を採用
    final_status = max([absolute_status, bench_status], key=lambda s: _status_severity(s))

    report.add(CheckResult(
        check_id=check_id,
        status=final_status,
        section=section,
        actual=val,
        expected=median,
        diff=val - median,
        message=(
            f"{label} = {val:.2f} ({quartile_label} vs benchmark median {median:.2f}; "
            f"top quartile {top:.2f}, bottom {bottom:.2f})"
        ),
        recommendation=(
            f"Source: {src} (N={n}, data year {year}). "
            f"Top quartile threshold = {top:.2f}. "
            f"absolute hard threshold = {absolute_threshold} ({rationale})."
        ),
    ))


def _status_severity(s: str) -> int:
    return {"pass": 0, "info": 1, "warn": 2, "fail": 3}.get(s, 0)
```

### 5.4 sanity_checks.py CLI 拡張

```python
# scripts/sanity_checks.py main()

import argparse, json, sys

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", required=True)
    p.add_argument("--benchmarks", help="Path to benchmark JSON (from build_model.py dispatch)")
    p.add_argument("--check", help="Single check id to run (e.g. D12)")
    args = p.parse_args(argv)

    benchmarks = {}
    if args.benchmarks:
        with open(args.benchmarks) as f:
            data = json.load(f)
        # Index by metric_id for fast lookup
        for entry in data["benchmarks"]:
            benchmarks[entry["metric"].lower().replace(" ", "_")] = entry["values"] | {
                "source_name": entry["source"]["name"],
                "n": entry["values"].get("n"),
                "year_data_collected": entry.get("fetched_at", "n/a")[:4],
            }

    wb = load_workbook(args.xlsx, data_only=False)
    vwb = load_workbook(args.xlsx, data_only=True)
    report = CheckReport()
    _check_soft_all(wb, vwb, report, benchmarks=benchmarks)
    # ... 他 check 群
    report.write_to_workbook(wb)
    wb.save(args.xlsx)
    return 0 if report.is_clean() else 1
```

### 5.5 Backward compatibility

`benchmarks=None` で呼び出すと従来動作 (absolute threshold のみ)。既存の自動テスト / CI は影響なし。

---

## §6. Integration with build_model.py Orchestrator

### 6.1 高位フロー

```
build_model.py 実行フロー:

Step 1: Input parsing                  (15_input_schema 準拠 YAML を schema 検証 + load)
   ↓
Step 2: Sheet generation               (three_statement_builder / cap_table_builder /
                                        valuation_builder で 17 シート生成)
   ↓
Step 3: ★ Benchmark research dispatch ★  (NEW; § 3 prompt template を 5-10 並列で agent dispatch)
   ↓
Step 4: Sanity check with benchmarks    (sanity_checks.py に benchmarks JSON を inject)
   ↓
Step 5: IC memo generation              (13_IC_Memo に fresh benchmark を埋め込み、
                                        11_KPI_Dashboard の benchmark 列も populate)
   ↓
Step 6: Cache snapshot save             (audits/benchmark_cache_{date}.json に保存)
   ↓
Step 7: xlsx 保存 + audit log          (build_log.csv に dispatch 履歴 + cost 記録)
```

### 6.2 Parallel Dispatch Pattern

1 案件で必要となる benchmark 数は典型的に **5-10 個**:

| # | benchmark | template |
|---|---|---|
| 1 | NRR (業態 × stage) | §3.1 |
| 2 | Burn Multiple (stage) | §3.1 |
| 3 | Magic Number (stage) | §3.1 |
| 4 | Rule of 40 (stage) | §3.1 |
| 5 | LTV/CAC (業態) | §3.1 |
| 6 | Comp set (業態 × growth × ARR) | §3.2 |
| 7 | Risk-free rate (region) | §3.3 |
| 8 | Industry beta (業態) | §3.3 |
| 9 | Tax rate (country × entity) | §3.4 |
| 10 | Long-term GDP growth (region) | §3.5 |

**parallel dispatch** で 5-10 並列、各 5-7 分以内に完了 → total 5-10 分。

sequential dispatch だと 30-50 分かかるため、**parallel が canonical**。

### 6.3 Implementation Sketch (build_model.py 抜粋)

```python
import asyncio
from research_dispatcher import dispatch_benchmark

async def fetch_all_benchmarks(project_config):
    """
    project_config から必要な benchmark を抽出 → 並列 dispatch。
    """
    business_model = project_config["business_model"]
    stage = project_config["stage"]
    region = project_config["region"]
    arr_band = project_config.get("arr_band")
    country = project_config.get("country", region)

    # § 3 template に対応する dispatch task 群
    tasks = [
        # SaaS metrics (§3.1)
        dispatch_benchmark("saas_metric", template="3.1", context={
            "metric_name": m, "business_model": business_model,
            "stage": stage, "region": region, "arr_band": arr_band,
        })
        for m in ["NRR", "Burn Multiple", "Magic Number", "Rule of 40", "LTV/CAC"]
    ]
    # Comp set (§3.2)
    tasks.append(dispatch_benchmark("comp_multiple", template="3.2", context={
        "region": region, "growth_min": 30, "revenue_min": "$50M",
        "revenue_max": "$2B", "business_model": business_model,
    }))
    # WACC components (§3.3)
    tasks.append(dispatch_benchmark("wacc_components", template="3.3", context={
        "region": region, "business_model": business_model,
    }))
    # Tax (§3.4)
    tasks.append(dispatch_benchmark("tax_rate", template="3.4", context={
        "country": country, "entity_type": "corporate", "tax_year": 2026,
    }))
    # GDP growth (§3.5)
    tasks.append(dispatch_benchmark("gdp_growth", template="3.5", context={
        "region": region,
    }))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return _consolidate_benchmark_results(results)


def main():
    cfg = load_input_yaml(args.input)
    wb = build_sheets(cfg)                              # Step 1-2
    benchmarks = asyncio.run(fetch_all_benchmarks(cfg)) # Step 3
    save_cache(benchmarks, project_id=cfg["project_id"])
    run_sanity_checks(wb, benchmarks=benchmarks)        # Step 4 (§5 で改修済)
    write_ic_memo(wb, cfg, benchmarks)                  # Step 5
    save_xlsx(wb, args.output)                          # Step 7
```

### 6.4 Failure Mode Handling

並列 dispatch のうち 1-2 個 fail しても build は止めない (degraded mode で継続)。fail 詳細は `build_log.csv` に記録 + IC memo に "benchmark unavailable" status を可視化 (§7.2)。

---

## §7. IC Memo Template Update

### 7.1 「Performance vs Industry Benchmark」 Section

`13_IC_Memo` に以下 section を **必ず含める** (Phase 6 拡張)。

```markdown
## Performance vs Industry Benchmark

| Metric | Our value | Industry median | Quartile rank | Source |
|---|---|---|---|---|
| ARR YoY Growth | 180% | 120% | Top quartile | Pacific Crest 2025 (N=350, B2B SaaS Series B, US) |
| NRR | 115% | 110% | Above median | Pacific Crest 2025 (N=350) |
| Burn Multiple | 1.2x | 1.5x | Top quartile (lower better) | Pacific Crest 2025 (N=350) |
| Magic Number | 0.85 | 0.70 | Above median | Pacific Crest 2025 (N=350) |
| Rule of 40 | 45 | 25 | Top quartile | Pacific Crest 2025 (N=350) |
| LTV/CAC | 4.2x | 3.0x | Top quartile | Pacific Crest 2025 (N=350) |
| EV/Revenue (peers) | n/a (private) | 9.2x | (peer median) | Custom comp set (N=7, US listed B2B SaaS, growth>30%, $50M-$2B revenue) |

*All benchmark values fetched at build time {build_timestamp} via on-demand research agent dispatch.
Cache TTL per `_benchmark_protocol §4.1`. Source URLs in `audits/benchmark_cache_{YYYYMMDD}.json`.*
```

### 7.2 Benchmark Unavailable 表示

dispatch fail / cache miss / source paywall 等で benchmark 取得できなかった場合:

```markdown
| Metric | Our value | Industry median | Quartile rank | Source |
|---|---|---|---|---|
| Burn Multiple | 1.2x | n/a | n/a | **benchmark unavailable** (dispatch fail at {timestamp}; see audits/benchmark_log.csv) |
```

### 7.3 Stale Cache 表示

TTL 超過した cache を allowed-fallback で使用した場合 (§10.2 fallback chain 経由):

```markdown
| Metric | Our value | Industry median | Quartile rank | Source |
|---|---|---|---|---|
| NRR | 115% | 110% (stale) | Above median | Pacific Crest 2024 Survey (cached 14 mo, TTL 12 mo, **stale flag**) |
```

### 7.4 Source Date 必須

各 benchmark cell に source date が **必ず記載**されることで、IC committee や LP に対する defensibility を担保する。

---

## §8. Anti-Patterns

### 8.1 Skill 内 Hard-Code

```
NG: NRR median = 110% を skill 内 reference (例: 02_saas_metrics.md) に書き込む
理由: 1 年で陳腐化、source 出典が剥落する、年次 update 責任不明、複数 reference に分散すると同期コスト増
OK: protocol を skill に固め (本 file)、value は build 時取得。reference 本文には数式と PASS/WATCH/FAIL 区分のみ書く
```

### 8.2 Cache の Stale 利用 (silent stale)

```
NG: 14 ヶ月前の Pacific Crest 2024 survey を IC memo で「最新」と表示 (TTL 12 mo 超過)
理由: 投資家は最新 data 期待。stale 開示なしは defensibility 毀損 + 場合により misrepresentation
OK: TTL ルール (§4.1) を守り、IC memo build 時は fresh dispatch 強制 (§4.3)。
    やむを得ず stale cache を使う場合は IC memo に "(stale flag)" を必ず明示 (§7.3)
```

### 8.3 Single Source Bias

```
NG: 1 source (例: a16z blog) のみ参照
理由: bias リスク、誤情報の amplification、data N 不明な blog 引用が IC memo に滲む
OK: 2-3 source triangulation、median 採用。乖離が大きい場合は両方記録 + caveats
    (§3.1 prompt template の "secondary_sources" 配列で強制)
```

### 8.4 Source Tier の揉み消し

```
NG: Twitter post を Tier 2 と区分け、podcast 引用を Tier 1 と扱う
理由: Tier 4 (anecdotal) は IC memo 不適合。bias / cherry-picking / 出典遡及不能リスク
OK: Tier 4 は internal exploration のみ、Tier 1-2 を IC memo。Tier 3 は caveats 付きで IC 利用可
    (§3.1 prompt template の "source_tier": 1-4 を strict 区分)
```

### 8.5 Hard-Code への暗黙 Fallback

```
NG: dispatch fail 時に skill 内に隠してある「NRR median = 110%」を黙って使う
理由: source トレース不能、stale 隠蔽、defensibility 毀損
OK: dispatch fail 時は (a) 上位 source tier に fallback、(b) expired cache を "stale" 明示で使う、
    (c) 完全 fail なら "benchmark unavailable" を IC memo + sanity_check に明示 (§10.2)
```

### 8.6 Quartile を「median のみ」に省略

```
NG: IC memo benchmark 表で median 列だけ書き、top/bottom quartile を省く
理由: 「中央値超え」だけでは defensibility 不十分。VC は top quartile か above median かを区別する
OK: top quartile / median / bottom quartile の 3 値を必ず併記 (§7.1)
```

### 8.7 "About 2x" のような曖昧表記

```
NG: "EV/Rev は SaaS で約 9-10x が相場" と IC memo に書く
理由: 出典 N、対象期間、業態 split が不明
OK: 必ず具体値 + N + source URL + as_of_date を併記 (§7.1 のテンプレに従う)
```

### 8.8 Macro Event 後の Cache 継続利用

```
NG: 2026-03 の SVB 級 banking crisis 直後に、2026-01 取得の comp multiple を「TTL 内 (1 mo)」と継続利用
理由: macro event は cache 前提を破壊する。TTL は通常時 governance であり、structural break 発生時は無効
OK: macro event detect 時は §4.3 "crisis re-evaluation" で全 benchmark を強制 fresh dispatch
```

---

## §9. Mini Cases — 5 例

### Case 1: Series A SaaS の Sanity Check (S1 Magic Number)

#### 状況
- 業態: B2B Vertical SaaS (HR Tech)、Stage: Series A、Region: US、ARR $4M
- model build 中、`scripts/sanity_checks.py` が S1 (Magic Number) 判定で benchmark 必要

#### 適用フロー
1. build_model.py が §3.1 prompt を Magic Number / B2B Vertical SaaS / Series A / US で dispatch
2. 5 分後、agent が以下を返す:
   ```json
   {
     "metric": "Magic Number",
     "top_quartile": 1.0, "median": 0.7, "bottom_quartile": 0.4,
     "n": 350, "source_name": "Pacific Crest 2025 SaaS Survey",
     "fetched_at": "2026-05-02T10:30:00Z"
   }
   ```
3. sanity_checks.py の `_soft_check_with_benchmark` がこれを受け取り、xlsx の Magic Number = 0.85 と比較
4. 結果: "Above median (0.85 vs median 0.7; top quartile 1.0; Pacific Crest 2025 N=350)"
5. SanityChecks シートに ✅ + recommendation 行を populate

#### 採用 reference
- `_terminology §6.1` (Magic Number 計算式 = canonical)
- `_terminology §6.3` (×4 で年率化ルール)
- 本 file §3.1 (prompt) + §5.3 (helper function)

### Case 2: IC Memo の Comp Section (10_Comps + 13_IC_Memo)

#### 状況
- 案件: B2B Horizontal SaaS、Series B、ARR $15M、growth 120% YoY、地域 US
- IC memo 最終段で `10_Comps` シートに peer multiple 必要

#### 適用フロー
1. §3.2 prompt を以下 input で dispatch:
   - region: US
   - growth_min: 30
   - revenue_min: "$50M", revenue_max: "$1B"
   - business_model: "B2B Horizontal SaaS"
2. 7 分後、agent が peer 7 社 (例: HubSpot / Asana / Monday / etc.) の table を返す:
   ```
   median EV/Rev = 9.2x、p75 = 13.5x、p25 = 6.0x、N=7
   data source: Yahoo Finance + 10-K, fetched 2026-05-02
   ```
3. `10_Comps` シートに table を populate、median を `13_IC_Memo §Valuation` で参照
4. IC memo: "Trading comp median 9.2x → applied to forward $25M ARR → $230M EV (peer-median basis)"

#### 採用 reference
- `05_valuation_wacc §10` (comp methodology)
- 本 file §3.2 (prompt template)

### Case 3: DCF WACC Components (09_DCF)

#### 状況
- 案件: Late-stage SaaS、DCF model 構築、WACC 計算が必要
- region: US、業態: B2B SaaS

#### 適用フロー
1. §3.3 prompt を dispatch (region=US, business_model=B2B SaaS)
2. 6 分後、agent が以下を返す:
   - risk-free rate: 4.20% (FRED DGS10, 2026-05-02)
   - implied ERP: 5.10% (Damodaran May 2026)
   - industry beta (B2B SaaS, unlevered): 1.30 (Damodaran industry data, N=18)
3. `09_DCF` で WACC 計算:
   - Cost of Equity = 4.20% + 1.30 × 5.10% = **10.83%**
   - (D/V = 0 で Cost of Debt 寄与なし、SaaS 想定)
4. `_terminology §X` (WACC 計算式正本) に従って sanity check (WACC ≥ terminal growth + 200bp 確認)

#### 採用 reference
- `05_valuation_wacc §1.6` (WACC 計算正本)
- 本 file §3.3 (prompt template) + §3.5 (terminal growth 整合)

### Case 4: Multi-Year IC Memo の Benchmark Drift 比較

#### 状況
- 2024-05 に投資した SaaS portfolio 企業の re-evaluation を 2026-05 に実施
- 「benchmark がこの 2 年でどう動いたか」を IC committee に説明したい

#### 適用フロー
1. 2024-05 build 時の cache snapshot (`audits/benchmark_cache_20240520.json`) を load
2. 2026-05 で fresh dispatch (§3.1 を 5 並列、IC memo mode で TTL 無視)
3. 比較表を IC memo に挿入:
   ```
   Metric                     2024-05 median   2026-05 median   Drift
   NRR (Series B B2B SaaS)    115%             110%             -5pp
   Burn Multiple              1.4x             1.5x             +0.1x
   EV/Revenue (peer median)   12.5x            9.2x             -3.3x
   Risk-free rate (US10Y)     4.55%            4.20%            -35bp
   ```
4. 「Multiple compression -26% は exit valuation 前提の見直し必要」と IC memo に記載

#### 採用 reference
- 本 file §4.2 (cache snapshot 設計) + §7 (IC memo benchmark section)
- `19_ma_exit_for_founders` (exit valuation 再見積もり)

### Case 5: Crisis Re-Dispatch (Macro Event)

#### 状況
- 2026-03 に banking crisis 級 macro event 発生 (架空シナリオ)
- 既に保有する 5 model の benchmark を全 re-dispatch する必要

#### 適用フロー
1. portfolio orchestrator が `force_fresh=True` で全 benchmark を re-dispatch (§4.4)
2. 並列 dispatch (5 model × 各 7 benchmark = 35 並列、または model 単位 sequential で 5 model)
3. 各 model の `audits/benchmark_cache_{date}.json` を更新、前回 cache と diff 計算
4. crisis 影響が顕著な指標 (comp multiple、risk-free rate) を IC re-discussion 用に整形:
   ```
   Pre-crisis (2026-02-15)   Post-crisis (2026-03-20)
   risk-free 4.20%           5.10%   (+90bp panic)
   EV/Rev median 9.2x        6.5x    (-29%)
   ```
5. 「WACC 上昇 + multiple compression で全 portfolio の implied IRR が 2-3pp 低下」と IC report に記載

#### 採用 reference
- 本 file §4.3 ("crisis re-evaluation") + §8.8 (Macro event 後の cache 利用禁止)

---

## §10. Operational Notes

### 10.1 Cost / Latency Budget

| 項目 | 値 |
|---|---|
| 1 案件あたり benchmark 数 | 5-10 個 |
| 1 dispatch あたり token 消費 | 100-500K (input + output 合算、WebSearch / WebFetch 含む) |
| 1 案件 total token | 1-5M |
| Latency (parallel) | 5-10 分 |
| Latency (sequential、参考) | 30-50 分 |
| API cost (1 案件) | $5-25 (Claude API rate に依存) |
| Cache hit 率 (実運用想定) | 40-60% (IC memo 以外なら) |

案件 1 件あたりの追加コストは IB 報酬比で十分に許容範囲。LP / 投資家への defensibility 価値が API cost を大きく上回る。

### 10.2 Failure Mode と Fallback Chain

dispatch 失敗 (rate limit / paywall / timeout / 完全 fail) が発生した時の fallback 順序:

```
Step 1: Tier 1 source dispatch
  ↓ (fail)
Step 2: Tier 2 source dispatch
  ↓ (fail)
Step 3: Cache (TTL 超過でも) を "stale" flag 付きで利用
  ↓ (cache 不在)
Step 4: Skill 内 starter cache (例: 21_metric_benchmarks.md があれば) を "fallback" flag 付きで利用
  ↓ (なし)
Step 5: "benchmark unavailable" を sanity_check + IC memo に明示記録
```

各段階で **silently 進めない**。何 fallback を踏んだか必ず audit log + IC memo に明示する。

### 10.3 Observability

`<project_root>/audits/benchmark_log.csv` に以下を記録:

| 列 | 内容 |
|---|---|
| timestamp | dispatch 時刻 (ISO 8601) |
| project_id | 案件 ID |
| metric_id | benchmark の識別子 (例: `saas_metric/nrr/series_b/us`) |
| template_used | §3.1 / §3.2 / §3.3 / §3.4 / §3.5 |
| status | success / cache_hit / fallback_tier2 / fallback_cache / fail |
| source_tier | 1 / 2 / 3 / 4 |
| source_name | Pacific Crest 2025 など |
| n | sample size |
| year_data | 2025 など |
| latency_sec | dispatch 所要秒 |
| token_cost | input + output token |
| api_cost_usd | 概算 USD |
| caveats | flag (stale / single_source / etc.) |

月次 review でこの log を見て:
- (a) どの benchmark が cache miss 多いか → TTL 見直し
- (b) どの source が fail しがちか → primary source 切り替え
- (c) cost 異常 outlier → prompt 最適化

### 10.4 Privacy / Data Handling

- benchmark research は **公開 source 限定**。proprietary data (顧客 internal data, NDA-bound research) は混ぜない
- 案件 ID + cache snapshot は internal storage 限定 (S3 / 社内 NAS 等)、外部 API には送出しない
- IC memo に benchmark 値を含める際、source URL を必ず併記し reproducibility を担保

### 10.5 Versioning / Backward Compatibility

- 本 protocol は `agent_version` field を持つ (§3.1 出力 JSON)
- prompt template / output schema 改訂時はバージョン bump
- 既存案件の benchmark cache は古い version でも読める (forward compatibility 維持)

---

## §11. 関連 Reference との整合

| 関連 reference | 関係 |
|---|---|
| `_terminology` | 不変概念 (定義式 / PASS/WATCH/FAIL 区分 / 計算規則) はここ。**benchmark の median % / 数値は本 protocol 経由**。両者は補完 |
| `02_saas_metrics` | metric の概念説明・計算式・stage 別 ARR レンジはここ。**median / quartile 数値は本 protocol 経由** |
| `05_valuation_wacc` | WACC 計算式正本。risk-free / ERP / beta の **値** は本 protocol §3.3 経由 |
| `_self_review_protocol` | §8 案件 self-review check 6 (Customer ROI thesis) / 7 (WTP boundary) / 10 (Design consistency) で benchmark 比較する場面は本 protocol 経由 |
| `_master_decision_tree §C` | 4 段ゲートで使う数値 threshold は本 protocol 経由 |

---

## §11a. Migration Plan — 既存 Reference からの Hard-Code 移行

本 protocol を新設しても、既存 reference (00-19) には Tier 2 hard-code 値が残存する可能性が高い。Phase 6 Wave 2-3 の修正対象として、以下手順で migrate する。

### 11a.1 Audit Step (発見)

```bash
# 既存 reference の Tier 2 候補を grep で抽出
cd skills/startup-financial-modeling/references/
grep -nE "median|p50|p75|p25|top quartile|bottom quartile" *.md | grep -v "_benchmark_protocol\|_terminology" > /tmp/tier2_candidates.txt

# 数値パターン抽出 (% / x multiple / bp / mo)
grep -nE "[0-9]+(\.[0-9]+)?%|[0-9]+(\.[0-9]+)?x|[0-9]+ ?bp|[0-9]+ ?mo " *.md > /tmp/numeric_candidates.txt
```

### 11a.2 Classification Step (分類)

各 hit を 3 区分に分類:
- (a) Tier 0 (定義式の一部) → そのまま reference 内残置
- (b) Tier 1 (5+ 年安定構造値) → reference 内残置 + 改訂履歴に記録
- (c) Tier 2 (短命 benchmark) → 本 protocol へ移行 + reference 内では「`_benchmark_protocol §3.1` 経由」と参照記述に変更

### 11a.3 Refactor Step (移行)

reference 内 hard-code を以下 pattern に書き換える:

#### Before (hard-code)
```markdown
NRR の Series B 時点 median は 110%、top quartile は 130% (Pacific Crest 2024)。
```

#### After (protocol 経由)
```markdown
NRR の Series B 時点 median / top quartile は **build 時に `_benchmark_protocol §3.1` で fresh 取得**。
本 file は計算式 (期初 ARR + Expansion - Contraction - Churn / 期初 ARR) と PASS/WATCH/FAIL 区分のみ canonical 化する (`_terminology §6.1` 参照)。
```

### 11a.4 Self-Review Protocol との連携

`_self_review_protocol §3.2 Wave 2` (Logic / Strategy 系) で本 migration を扱う。`audits/master_issues.md` に M-XXX で記録、Phase 6 patch の終了条件に「Tier 2 hard-code 残存件数 = 0」を追加。

---

## §11b. Test / Validation Strategy

### 11b.1 Schema Validation

dispatched benchmark JSON は §3 の各 template の出力 schema に準拠する必要がある。`scripts/validate_benchmark.py` (新設想定) で以下を check:

```python
import json
import jsonschema

SAAS_METRIC_SCHEMA = {
    "type": "object",
    "required": ["metric", "business_model", "stage", "region",
                "year_data_collected", "top_quartile", "median",
                "bottom_quartile", "n", "source_tier", "source_name",
                "source_url", "fetched_at"],
    "properties": {
        "metric": {"type": "string"},
        "top_quartile": {"type": "number"},
        "median": {"type": "number"},
        "bottom_quartile": {"type": "number"},
        "n": {"type": "integer", "minimum": 1},
        "source_tier": {"type": "integer", "minimum": 1, "maximum": 4},
        # ...
    },
}

def validate_benchmark(payload: dict, template: str) -> None:
    schema = SCHEMAS[template]
    jsonschema.validate(payload, schema)
    # 追加 sanity:
    assert payload["bottom_quartile"] <= payload["median"] <= payload["top_quartile"], \
        "Quartile order violation"
    assert payload["source_tier"] in [1, 2], \
        f"IC memo 用途には Tier 1-2 のみ許容、got Tier {payload['source_tier']}"
```

### 11b.2 Integration Test

`tests/test_benchmark_integration.py` で以下シナリオを mock dispatch + assert:

1. **Happy path**: dispatch → cache → sanity_check injection → IC memo populate
2. **Cache hit**: 2 回目の build で cache 利用、dispatch されない
3. **TTL expire**: TTL 超過後の build で fresh dispatch される
4. **Dispatch fail**: Tier 1 fail → Tier 2 dispatch → cache fallback の chain 実行
5. **IC memo mode**: `force_fresh=True` で cache 無視

### 11b.3 Regression Guard

毎月、過去 6 ヶ月の cache snapshot を sample 抽出し、現時点 fresh dispatch との drift を計測。`audits/benchmark_drift_report_{YYYYMM}.md` に記録。

| Metric | 6 mo ago median | Now median | Drift | Action |
|---|---|---|---|---|
| NRR (Series B B2B SaaS) | 115% | 110% | -5pp | None (within typical noise) |
| EV/Rev (peer median) | 9.5x | 9.2x | -3% | None |
| Risk-free (US10Y) | 4.50% | 4.20% | -30bp | None (TTL 1wk 適切) |
| Burn Multiple median | 1.5x | 1.7x | +13% | TTL 検討 (12 mo → 6 mo) |

drift が typical band を超える metric は TTL を短縮する候補。

---

## §11c. Edge Cases

### 11c.1 業態 mismatch (segment 境界)

「Vertical SaaS」案件で「B2B Horizontal SaaS」 benchmark を流用するのは不適切。dispatch context は具体的 segment まで指定し、agent 側で「該当 N が < 30 の場合は近接 segment で triangulate」を許容する。

```
case: dispatch context = "Vertical SaaS / HR Tech / Series B / US"
  → Pacific Crest 2025 の N=42 (HR Tech split) で適切
  → ただし N < 30 の細分化なら、周辺 vertical (FinTech / HealthTech) を triangulate
```

### 11c.2 Stage 跨ぎ (Series A → B 移行期)

ARR $4M / growth 200% の案件は Series A 末期と Series B 初期の境界。dispatch を 2 回行い両方の median を取得、IC memo に「Series A late / B early の境界 case」と注釈。

### 11c.3 Region mismatch

日本案件で US benchmark を流用すると WTP / churn 構造が違う。日本に特化した source (Off Topic, FastGrow, 経済産業省 IT survey) を Tier 2 として dispatch context に明記。N が小さい場合は US benchmark + Japan adjustment を IC memo に記載。

### 11c.4 Pre-revenue / Pre-product

ARR が無い stage では SaaS metric benchmark は意味を成さない。dispatch を skip し、IC memo benchmark section は「pre-revenue stage、benchmark 未適用」と明示。代わりに `08_investment_thesis §3 Pre-Seed criteria` の qualitative gate を IC memo で参照。

### 11c.5 Hardware / Bio など SaaS 以外

§3.1 prompt template は SaaS metric 専用。Hardware (gross margin / inventory turn) や Bio (R&D burn / Phase progression) は別 template が必要。本 protocol は v1.0 で SaaS / Marketplace に特化しており、Hardware / Bio 専用 template は v1.1 以降で追加予定 (Phase 7 候補)。

### 11c.6 IC committee の preferred source

特定 IC committee が「Pacific Crest を normative」と要求している場合、dispatch prompt に source priority を明示する:

```
prompt 修正例 (§3.1 内):
  Source priority override: Pacific Crest を primary、他は triangulation のみ
```

---

## §11d. Mini Case 6: Crisis Re-Dispatch + Cache Drift Visualization

### 状況
- 2026-09 に AI bubble correction 級 macro event 発生 (架空)
- 6 model の portfolio review、IC committee に「benchmark drift」を可視化したい

### 適用フロー

1. Portfolio orchestrator が `force_fresh=True` で 6 model × 7 benchmark = 42 並列 dispatch (ただし API rate limit 対策で 6 並列 × 7 wave = 60 分弱)
2. 各 model の前回 cache (2026-04 build 時) と新 dispatch を delta 計算
3. 集約レポート (`portfolio_benchmark_drift_2026Q3.md`) を生成:
   ```
   Pre-correction (2026-04)    Post-correction (2026-09)   Drift
   Risk-free (US10Y) 4.20%     5.50%                        +130bp
   ERP implied 5.10%            6.50%                        +140bp
   EV/Rev median 9.2x           5.8x                         -37%
   NRR median (B2B SaaS) 110%   105%                         -5pp
   Burn Multiple median 1.5x    1.8x                         +20%
   ```
4. 6 model の implied IRR を再計算、IC committee に「全 portfolio で平均 IRR -4pp、3 model は kill criteria 抵触」と報告
5. kill criteria 該当 model は `_master_decision_tree §C` で再ゲート判定

### 採用 reference
- 本 file §4.3 (crisis re-evaluation) + §4.4 (cache hit / miss logic) + §11b.3 (drift report)
- `08_investment_thesis §4` (kill criteria threshold)
- `_master_decision_tree §C` (4 段ゲート)
