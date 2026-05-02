---
name: investment_thesis
description: 投資判断ロジックの正本 (Investment Thesis / IC Memo / DD / Kill Criteria / 4 段ゲート / Football field / Risk Register)。SKILL.md dispatch table の "IC memo 雛形" entry の第 1 reference として読まれる。§17 に IC memo 完成形 sample。
type: reference
priority: P1
related: [_terminology, _master_decision_tree, 02_saas_metrics, 05_valuation_wacc, 09_market_sizing, _stress_framework]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 投資判断ロジック (4 段ゲート / kill criteria) は本書を canonical とする。kill criteria の量的閾値は [`_terminology.md §6`](_terminology.md) を参照
- **Routing**: [`_master_decision_tree.md §C`](_master_decision_tree.md) (投資判断) から第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (4 段ゲート判定 / Risk Register 5 軸) を必ず実行
- **関連 reference**: `02_saas_metrics §10` (kill criteria 出典) / `05_valuation_wacc §17` (Football field) / `09_market_sizing` (TAM tiebreak) / `_stress_framework` (stress)

# 08. 投資判断 (Investment Thesis / IC Memo / DD) リファレンス

> **役割**: スタートアップ向け包括的財務モデリング skill の **dual verification — judgment side**。
> 財務モデルが構造的に正しい (build-side) だけでなく、投資判断ロジックとしても正しい (judgment-side) かを検証するための参照資料。

---

## 0. このリファレンスの使い方

### 0.1 判断ロジックの 4 層

| 層 | 問い | 主な道具 |
|---|---|---|
| L1 構造 (Build) | モデルは数式・期間・整合性で正しいか | チェックサム、三表整合、ユニット |
| L2 ベンチ (Benchmark) | 数値は同業 / 同ステージで実現可能な範囲か | 本リファレンスの閾値マトリクス |
| L3 判断 (Judgment) | この数値がそろえば投資して報われるか | IC Memo、Risk Register、Conviction |
| L4 ガバナンス (Governance) | 投資後にこの仮説をどう検証 / 撤退するか | Reforecast trigger、Kill criteria |

build-side との接続点を以下に明記する。判断の根拠は必ず build-side の出力を引用する形で書くこと (例:「3 期 P/L → Rule of 40 = 38% → WATCH」)。

### 0.2 モデル出力 → 判断チェックの対応

| モデル出力 (build-side) | 判断チェック (judgment-side) | 参照節 |
|---|---|---|
| ARR 推移、growth % | T2D3、ステージ別 ARR 閾値、Rule of 40/X | §4.1, §3 |
| Cohort retention 表 | NRR / GRR、logo churn、GMV retention | §4.1, §4.2 |
| CAC / LTV 計算 | LTV/CAC > 3x、CAC payback、Magic Number | §4.1 |
| Burn / runway | Burn Multiple、runway > 18ヶ月 | §4.1, §5 |
| TAM / SAM / SOM | top-down × bottom-up triangulation | §7 |
| Cap table、option pool | dilution、liquidation preference、安全性 | §1.10, §6 |
| Exit waterfall | DPI、TVPI、IRR、acquirer mapping | §12 |
| Sensitivity (best/base/worst) | range が thesis を破壊しないか | §1.13 |

### 0.3 用語の方針

- 「OS」は使わず「土台」「基盤」「運営体系」と書く (memory note 準拠)。
- 時系列の数値データはすべて表形式で揃える。
- 出典は `[出典: <Title>](<URL>)` を文末に付す。

---

## 1. IC Memo (Investment Committee Memorandum) の標準構造

### 1.1 概要

IC Memo (Investment Committee Memorandum) は、VC のアナリスト / パートナーが投資委員会に対して案件を提示する内部文書。創業者が投資家に売り込む pitch deck と異なり、**自社のパートナーに対して deal を売り込む** 文書である。

[出典: Visible.vc - Investment Memo: Template, Examples, and How to Write One](https://visible.vc/blog/investment-memo/)
[出典: VCOS - Investment Committee Memo Template](https://www.vcosai.com/blog/investment-committee-memo-template)

IC Memo は以下の 3 役を兼ねる:

1. **意思決定の記録**: 何を信じて投資したかの first-principles を残す。
2. **モニタリングの基準**: 投資後に thesis が破れたかを判定する物差し。
3. **後続ラウンド評価の起点**: 次回ラウンドで thesis 進捗を再評価する。

### 1.2 標準セクション (15-20 ページ版)

| # | セクション | 推奨頁数 | 主目的 |
|---|---|---|---|
| 1 | Executive Summary | 1 | 1 ページで結論 |
| 2 | Investment Thesis | 0.5-1 | 3-5 箇条で投資論点 |
| 3 | Recommendation & Terms | 0.5 | 提案する条件 |
| 4 | Company Overview | 1-1.5 | 事業概要、沿革、チーム |
| 5 | Market Analysis | 2-3 | TAM/SAM/SOM、競合、規制 |
| 6 | Product / Technology | 1-2 | 差別化、moat、IP |
| 7 | Go-to-Market Strategy | 1-1.5 | チャネル、sales motion |
| 8 | Business Model & Unit Economics | 1.5-2 | セグメント別ユニット経済 |
| 9 | Financial Performance | 1.5-2 | 過去 + 予測 |
| 10 | Capital Structure & Use of Proceeds | 0.5-1 | cap table、資金使途 |
| 11 | Valuation | 1-1.5 | 三角測定 |
| 12 | Risks & Mitigants | 1-1.5 | top 5-10 リスク |
| 13 | Sensitivity Analysis | 0.5-1 | best/base/worst |
| 14 | Exit Strategy | 0.5-1 | IPO / M&A / secondary |
| 15 | Appendix | 適宜 | DD 結果、リファレンスチェック |

### 1.3 Executive Summary (1 ページ)

[出典: VCOS - Investment Committee Memo Template](https://www.vcosai.com/blog/investment-committee-memo-template)

Executive Summary は以下の 3 ブロックで構成する:

**A. Deal Header**
- 会社名、業界、ラウンド (Pre-seed/Seed/A/B/...)
- 提案投資額、想定 ownership %
- 評価額 (pre-money / post-money)、希薄化
- 投資家ポジション (lead / co-lead / follow)
- 提案 security (priced equity / SAFE / convertible note)

**B. Investment Thesis (3-5 箇条)**
- "We believe X will happen, this company will benefit because Y, this matters because Z."
- 各 thesis は **falsifiable** であること (検証可能 = 投資後に破れたか判定できる)。

**C. Recommendation**
- PASS / WATCH / INVEST の明示。
- INVEST の場合の条件 (anti-dilution、board seat、information rights、pro-rata)。

### 1.4 Investment Thesis (3-5 箇条)

良い thesis の条件:

| 条件 | 悪い例 | 良い例 |
|---|---|---|
| Falsifiable | 「市場が大きい」 | 「2028 年までに NRR > 120% で ARR $50M 到達」 |
| Specific | 「強いチーム」 | 「CTO は Stripe で $100M ARR まで platform をスケール」 |
| Differentiated | 「AI を活用」 | 「公的医療データの独占アクセスにより 6-12ヶ月先行」 |
| Time-bound | 「将来勝てる」 | 「Series B (24ヶ月後) までに $20M ARR、NRR > 115%」 |

### 1.5 Company Overview

最低限カバーすべき項目:

- **One-liner**: 1 文で何の会社か (Sequoia 流: "We sell X to Y so they can Z")。
- **Founding story**: なぜこの問題に取り組むか、creator-market fit のエビデンス。
- **History**: 創業日、major milestone、過去ラウンド、product GA 日。
- **Team**: 創業者バックグラウンド、key hire、組織図、headcount 推移。
- **Operating model**: 拠点、リモート / オンサイト、主要プロセス。

### 1.6 Market Analysis

§5、§7、§8 で詳述。IC Memo 上は以下を必ず含める:

- TAM / SAM / SOM (top-down と bottom-up の triangulation)。
- 市場成長率と成長ドライバ (3-5 個)。
- 競合 (incumbent / direct / adjacent)。
- 規制 (該当業界のみ)。
- "Why Now" (Sequoia 流の 3-5 トレンド列挙)。

[出典: Sequoia Pitch Deck Template](https://www.uvic.ca/gustavson/_assets/docs/pitch-deck-template-web.pdf)

### 1.7 Product / Technology

| 観点 | 確認内容 |
|---|---|
| 差別化 | 競合に対する 10x improvement の根拠 |
| Moat | network effect / switching cost / scale economy / brand / IP |
| 技術リスク | 実現可能性、scaling のボトルネック、セキュリティ |
| IP | 特許、商標、ソースコード所有、open source ライセンス |
| Roadmap | 12-24 ヶ月の主要マイルストーン |

### 1.8 Go-to-Market Strategy

| Sales motion | 特徴 | 適性 |
|---|---|---|
| PLG (Product-Led Growth) | 無料 / freemium → 自動転換 | SMB、開発者向け、horizontal SaaS |
| SLG (Sales-Led Growth) | フィールドセールス、ABM | エンタープライズ、ACV > $50K |
| Hybrid (PLG + SLG) | self-serve で land、人で expand | mid-market、bottom-up adoption |
| Channel-led | リセラー、SI、OEM | 規制業界、地理拡張 |
| Marketplace-led | 既存 marketplace 経由 | アプリストア、AWS Marketplace |

### 1.9 Business Model & Unit Economics

セグメント別 (SMB / mid / ent や geo 別) に以下を提示:

- ACV (Average Contract Value)
- Gross Margin (% および GM ARR ベース)
- CAC (paid + organic、blended と new logo)
- LTV (gross / contribution / 期間想定)
- LTV / CAC、CAC Payback (months)
- NRR / GRR / logo retention

### 1.10 Capital Structure & Use of Proceeds

- 既存 cap table (founders / employees / investors)
- post-money cap table
- option pool 拡大 (pre or post)
- liquidation preference の積層 (1x non-participating が標準)
- Use of Proceeds 表 (R&D / S&M / G&A / その他、24-36ヶ月)
- Runway 計算 (gross burn と net burn の両方)

### 1.11 Valuation

§11 で詳述。三角測定の手法:

| 手法 | 適用ステージ | 備考 |
|---|---|---|
| Comparable trading multiples | A-C+ | EV/Revenue, EV/ARR (forward) |
| Comparable transactions (M&A / 直近ラウンド) | 全ステージ | take-out value のヒント |
| DCF (Discounted Cash Flow) | C+ / 後期 | 割引率 + terminal value 高感度 |
| VC method | Pre-seed / Seed | 想定 exit × 持分 / target IRR |
| Berkus / Scorecard | Pre-seed | 資産がない時の qualitative 評価 |
| First Chicago | A-B | 確率重み付けシナリオ |

### 1.12 Risks & Mitigants

§5 (Risk Register) を参照。IC Memo では top 5-10 を以下で表形式に。

| # | リスク | 確度 | 影響 | Mitigant | Trigger event |
|---|---|---|---|---|---|
| 1 | 主要顧客集中 (top 3 で 60%) | 中 | 高 | エンタープライズ営業強化 | top 1 が ARR 30% 超 |
| ... | ... | ... | ... | ... | ... |

### 1.13 Sensitivity Analysis

最低 3 シナリオ (best / base / worst)。各シナリオで:

- ARR 軌道
- runway
- exit 評価額
- IRR / MOIC

ドライバを明示 (e.g., NRR ±10pp、CAC payback ±6ヶ月、growth rate ±20pp)。

### 1.14 Exit Strategy

§12 で詳述。

| 経路 | タイミング | 評価額目安 | 留意 |
|---|---|---|---|
| IPO | $200M ARR、growth > 30% | EV/ARR 8-15x | Rule of 40、ガバナンス |
| Strategic M&A | 任意 | revenue × 4-12x | 買い手 mapping |
| Financial buyer (PE) | EBITDA positive | EBITDA × 10-20x | EBITDA 質、保護 |
| Secondary | A 以降 | 直近 round 80-100% | 流動性、税 |

---

## 2. 投資判断フレームワーク (代表的 VC)

### 2.1 a16z (Andreessen Horowitz)

#### 2.1.1 「Why Now / Why You / Why This」 三段論法

a16z は明確に「Why Now / Why You / Why This」を投資 thesis の核に据えている。

[出典: A Deep Dive into Andreessen Horowitz's Investment Criteria](https://press.farm/andreessen-horowitzs-investment-criteria/)
[出典: a16z - AI at the Intersection: Investment Thesis on AI in Bio + Health](https://a16z.com/ai-at-the-intersection-the-a16z-investment-thesis-on-ai-in-bio-health/)

| 軸 | 問い | 必要なエビデンス |
|---|---|---|
| Why Now | なぜ今この市場が立ち上がるか | 技術 / 規制 / 行動の不可逆変化 |
| Why You | なぜこのチームが勝つか | founder-market fit、unique insight |
| Why This | なぜこの product / approach が勝つか | 10x improvement、defensibility |

#### 2.1.2 a16z の投資判断特徴

- **"Founder-first"**: 創業者の vision と executable insight を最重視。
- **"Software is eating the world"** 系のマクロ thesis から、各分野で deep investment。
- **Operator value-add**: 投資後の営業紹介、採用、PR が組み込まれている。
- **Fintech / Bio + Health / Crypto / Defense / Games / Media** などサブ thesis を明示。

[出典: a16z Fintech Investments, Team, & Thesis Overview](https://a16z.com/fintech/)
[出典: a16z Growth - David George on Late-Stage Investing Frameworks](https://a16z.com/podcast/a16z-frameworks-late-stage-investing/)

#### 2.1.3 a16z Late-Stage (Growth) 判断軸

David George (a16z Growth) の公開発言から:

| 軸 | 確認内容 |
|---|---|
| Market | TAM > $10B、構造変化が start (not end) |
| Moat | 既存巨人より早い execution、network effect 形成中 |
| Financial | growth durability、incremental margin、unit economics |
| Team | scaling 経験 / hiring engine / 創業者の learning 速度 |
| Valuation discipline | exit assumption に対する price |

### 2.2 Sequoia Capital

#### 2.2.1 Sequoia Pitch Deck テンプレート (12 セクション)

[出典: Sequoia Capital Pitch Deck Template](https://www.uvic.ca/gustavson/_assets/docs/pitch-deck-template-web.pdf)
[出典: Best Sequoia Pitch Deck Examples - Storydoc](https://www.storydoc.com/blog/sequoia-pitch-deck-examples)

| # | セクション | 1 行で書くなら |
|---|---|---|
| 1 | Company Purpose | 1 文で会社を定義 |
| 2 | Problem | 顧客の痛み、現状の対処 |
| 3 | Solution | 価値提案、利用シーン |
| 4 | Why Now | 業界の歴史的進化、最近のトレンド |
| 5 | Market Size | TAM、市場の形状 |
| 6 | Competition | landscape、自社の強み |
| 7 | Product | 機能、技術、IP、roadmap |
| 8 | Business Model | 収益モデル、価格、unit economics |
| 9 | Team | founders、key hire、advisor |
| 10 | Financials | P/L、cash flow、key metrics |
| 11 | The Deal (vision) | 資金調達条件、長期 vision |
| 12 | Appendix | 詳細データ |

Sequoia は特に **Why Now** を重視。「最高の会社は明確な Why Now を持つ。タイミングが起業の生死を分ける」とドキュメントで明言。

[出典: Sequoia Pitch Deck Template - PitchBuilder](https://pitchbuilder.io/blogs/news/what-is-the-sequoia-pitch-deck-model)

### 2.3 Y Combinator (Paul Graham)

#### 2.3.1 PG が重視する軸

[出典: Paul Graham - Ramen Profitable](https://paulgraham.com/ramenprofitable.html)
[出典: Paul Graham - Why YC](https://paulgraham.com/whyyc.html)

| 軸 | 内容 |
|---|---|
| Determination | 創業者の粘り (resilience > IQ) |
| Default alive | 現行 burn と grow rate で profitability に至るか |
| Ramen profitable | 創業者の生活費を賄える minimum profitability |
| Make something people want | ユーザーが熱狂する小さな核 |
| Talk to users | 週次でユーザーと話せ |
| Do things that don't scale | 初期は手作業を厭わない |

#### 2.3.2 YC の評価フェーズ

- 10 分インタビューで「why this team」「why this idea」「what have you built」を確認。
- Demo Day 直前まで「talk to users → ship → measure」サイクル。
- Default alive / dead を grow rate と burn から計算で示すことを要求。

### 2.4 Bessemer Venture Partners

#### 2.4.1 「The 5 Cs of Cloud Finance」

[出典: Bessemer - The Five Accounting Metrics for Cloud Companies](https://www.bvp.com/atlas/cloud-computing-metrics)
[出典: Bessemer - Cash Conversion Score](https://www.bvp.com/atlas/cash-conversion-score)

| C | 指標 | ベンチマーク |
|---|---|---|
| CARR | Committed ARR (ARR + 契約済み未稼働 − 想定 churn) | growth > 100% YoY (early)、> 50% (mid) |
| CAC payback | sales & marketing 投下回収月数 | < 18ヶ月 (great)、< 12ヶ月 (best) |
| Churn | logo gross churn、CARR renewal | logo < 7%/yr、CARR > 100% (net negative churn) |
| CLTV/CAC | 顧客生涯価値 / 獲得コスト | > 3x (good)、> 5x (great) |
| Cash flow | cash conversion、burn multiple | CCS > 1.0x で IRR 120% 平均 |

#### 2.4.2 Bessemer "10 Laws of Cloud"

[出典: Bessemer - Roadmap: 10 Laws of Cloud](https://www.bvp.com/atlas/10-laws-of-cloud)

要点:
1. 顧客成功は最大の成長エンジン。
2. NRR が長期 CAGR を決める。
3. Multi-product company が moat を作る。
4. Vertical SaaS の方が moat が深いことが多い。
5. AI ネイティブな再構築は古いカテゴリも壊す。

#### 2.4.3 Rule of X (Bessemer 提唱)

[出典: Bessemer - The Rule of X](https://www.bvp.com/atlas/the-rule-of-x)

`Rule of X = (Growth Rate × Multiplier) + FCF Margin`

- Multiplier: private 2x、public 2-3x。
- Rule of 40 より valuation 相関が高い (R^2 約 1.5x)。
- "Centaur" (Rule of X > 50) は valuation multiple 二桁を獲得し得る。

### 2.5 USV (Union Square Ventures)

#### 2.5.1 Thesis 1.0 / 2.0 / 3.0 の進化

[出典: USV Thesis (2012)](https://www.usv.com/writing/2012/05/investment-thesis-usv/)
[出典: USV Thesis 2.0](http://www.usv.com/blog/usv-thesis-20)
[出典: USV Thesis 3.0](https://www.usv.com/writing/2018/04/usv-thesis-3-0/)

| 版 | 公開年 | 中核命題 |
|---|---|---|
| 1.0 | 2012 | Large networks of engaged users、UX で差別化、network effect で防御 |
| 2.0 | 2015 | Less obvious network effects、新経済の infrastructure、open decentralized data の enabler |
| 3.0 | 2018 | Trusted brands that broaden access to knowledge, capital, well-being via networks/platforms/protocols |

#### 2.5.2 USV の判断特徴

- **Thesis-driven**: 案件 → thesis ではなく、thesis → 案件。
- **Concentrated**: パートナーあたり保有社数を意図的に絞る。
- **Long horizon**: ファンド 10 年超で評価。

### 2.6 First Round Capital

#### 2.6.1 First Round Review の評価フレーム

[出典: First Round Review](https://review.firstround.com/)
[出典: First Round - Frameworks](https://review.firstround.com/articles/frameworks/)

- **Founder reference 360**: 元同僚 / 元上司 / 元部下 / 顧客 / 共同創業者の 5 軸。
- **Operator-led DD**: First Round の operator network が deep dive。
- **Founder community**: 投資後の founder-to-founder mentoring。

### 2.7 Benchmark Capital

#### 2.7.1 Partnership 方式

- 全パートナーが equal partner、IC は事実上ファーム全体。
- 1 投資 = 1 board seat = 1 lead partner、deep engagement。
- 案件は **全員一致** が原則 (拒否権あり)。
- 「small fund + concentrated bets」が哲学。

---

## 3. ステージ別評価軸の違い

### 3.1 ステージ定義 (米国一般 / 日本対応)

| ステージ | 米国典型 ARR | 日本典型 評価額 | 主な評価軸 |
|---|---|---|---|
| Pre-seed | $0 - $0.1M | < 5億円 (post) | チーム、insight、prototype |
| Seed | $0.1M - $1M | 5-15億円 | early traction、design partner |
| Series A | $1M - $5M ARR | 15-50億円 | PMF metric、growth、retention |
| Series B | $5M - $20M ARR | 50-200億円 | scaling efficiency、unit economics |
| Series C | $20M - $50M ARR | 200-500億円 | path to profitability、market lead |
| Series D+ / Pre-IPO | $50M+ ARR | 500億円超 | financial discipline、governance、exit clarity |

[出典: INITIAL - 2025年上半期スタートアップ調達動向](https://initial.inc/articles/japan-startup-finance-2025h1)
[出典: INITIAL - スタートアップの平均的な成長モデル](https://initial.inc/articles/6eDb1OkqwX1T0IO3sLKdlV)

日本のラウンド間 step-up 倍率の中央値:

| 区間 | step-up |
|---|---|
| Seed → A | 3.4x |
| A → B | 1.9x |
| B → C | 1.8x |
| C → D 以降 | 1.7x |

### 3.2 ステージ別 weighting マトリクス

各軸の **重要度** を 0-5 で表す:

| 軸 | Pre-seed | Seed | A | B | C | D+ |
|---|---|---|---|---|---|---|
| Team / Founder | 5 | 5 | 5 | 4 | 3 | 3 |
| Market / TAM | 5 | 4 | 4 | 4 | 4 | 4 |
| Insight / Why Now | 5 | 4 | 3 | 2 | 2 | 2 |
| Product / Tech | 3 | 4 | 4 | 4 | 3 | 3 |
| PMF (retention/NRR) | 0 | 2 | 5 | 5 | 5 | 5 |
| Growth | 0 | 2 | 4 | 5 | 5 | 5 |
| Unit Economics | 0 | 1 | 3 | 5 | 5 | 5 |
| Scaling Efficiency | 0 | 0 | 2 | 5 | 5 | 5 |
| Path to Profitability | 0 | 0 | 1 | 3 | 5 | 5 |
| Governance / Board | 0 | 1 | 2 | 3 | 4 | 5 |
| Exit clarity | 1 | 1 | 2 | 3 | 4 | 5 |

### 3.3 各ステージのキラー条件 (kill criteria 早見表)

| ステージ | Kill 条件の例 |
|---|---|
| Pre-seed | 創業者の commitment 不足、insight の oryginality 欠如、market size < $500M |
| Seed | design partner ゼロ、6 ヶ月で active user 獲得ゼロ、共同創業者離脱 |
| A | NRR < 90%、growth YoY < 50%、PMF 兆候なし、CAC payback > 36ヶ月 |
| B | growth YoY < 30%、Magic Number < 0.4、Burn Multiple > 3x |
| C | Rule of 40 < 0%、market share 縮小、key exec 離脱 |
| D+ | governance 不在、auditor 不在、material weakness、IPO 準備未着手 |

---

## 4. Quantitative 投資判断ロジック (閾値ベース)

> ここからは **network of conditional logic**。
> 各閾値は (ステージ × 業態 × 指標) で PASS / WATCH / FAIL の 3 段階。
> 2 つ以上が WATCH → 全体 WATCH、1 つでも FAIL かつ kill criteria に該当 → 全体 FAIL。

### 4.1 SaaS 特化

#### 4.1.1 ARR Growth (ステージ別)

[出典: Battery Ventures - T2D3](https://www.battery.com/blog/a-mantra-for-saas-success-triple-triple-double-double-double/)

T2D3 (Triple Triple Double Double Double, Battery Ventures, Neeraj Agrawal):

| 年 | ARR 期初 | ARR 期末 | YoY |
|---|---|---|---|
| Year 1 | $1M | $2M | 2x (or PMF 探索) |
| Year 2 | $2M | $6M | 3x |
| Year 3 | $6M | $18M | 3x |
| Year 4 | $18M | $36M | 2x |
| Year 5 | $36M | $72M | 2x |
| Year 6 | $72M | $144M | 2x |

ステージ別 ARR Growth 閾値:

| ステージ | PASS (年率) | WATCH | FAIL |
|---|---|---|---|
| Seed → A | 200%+ (T2D 区間) | 150-200% | < 150% |
| A → B | 150-300% | 100-150% | < 100% |
| B → C | 100-200% | 60-100% | < 60% |
| C → D | 60-100% | 40-60% | < 40% |
| D+ → IPO | 40-60% | 25-40% | < 25% |

#### 4.1.2 Net Revenue Retention (NRR)

[出典: 2025 SaaS Benchmarks - High Alpha / OpenView](https://www.highalpha.com/saas-benchmarks)
[出典: Bessemer - Cloud Computing Metrics](https://www.bvp.com/atlas/cloud-computing-metrics)

| セグメント | PASS (best-in-class) | WATCH | FAIL |
|---|---|---|---|
| SMB | > 105% | 95-105% | < 95% |
| Mid-market | > 115% | 100-115% | < 100% |
| Enterprise | > 125% | 110-125% | < 110% |
| Top quartile (全体) | > 120% | 110-120% | < 110% |
| Median (private 2024-25) | 約 101-102% (= 業界 median) | - | - |

#### 4.1.3 Gross Revenue Retention (GRR) / Logo Retention

| セグメント | PASS | WATCH | FAIL |
|---|---|---|---|
| SMB GRR | > 85% | 75-85% | < 75% |
| Mid GRR | > 90% | 85-90% | < 85% |
| Enterprise GRR | > 95% | 90-95% | < 90% |
| Logo Churn (年率) | < 7% (ent) | 7-15% | > 15% |

#### 4.1.4 LTV / CAC

| ステージ | PASS | WATCH | FAIL |
|---|---|---|---|
| Seed | n/a (まだ計測困難) | - | - |
| A | 計測可能になる、> 1.5x | 1-1.5x | < 1x |
| B | > 3x | 2-3x | < 2x |
| C+ | > 4x | 3-4x | < 3x |

業界 median 2024: 3.6:1 (LTV/CAC)。

#### 4.1.5 CAC Payback (months)

[出典: ScaleXP - 2025 SaaS Benchmarks: CAC Payback](https://www.scalexp.com/blog-saas-benchmarks-cac-payback-2025/)
[出典: Bantrr - CAC Payback Benchmarks for SaaS](https://bantrr.com/business-model/saas-metrics/cac-payback-benchmarks-for-saas-companies/)

| セグメント | PASS | WATCH | FAIL |
|---|---|---|---|
| SMB | < 12ヶ月 | 12-18ヶ月 | > 18ヶ月 |
| Mid | < 18ヶ月 | 18-24ヶ月 | > 24ヶ月 |
| Enterprise | < 24ヶ月 | 24-30ヶ月 | > 30ヶ月 |
| 業界 median 2025 | 約 20ヶ月 (悪化中) | - | - |

#### 4.1.6 Magic Number

[出典: Scale Venture Partners - Magic Number Math](https://www.scalevp.com/insights/magic-number-math/)
[出典: Scale VP - SaaS Metrics: A History of the Magic Number](https://www.scalevp.com/insights/saas-metrics-a-history-of-the-magic-number/)

`Magic Number = (Q当 GAAP Revenue − 前Q GAAP Revenue) × 4 / 前Q S&M Spend`

| 値 | 解釈 | アクション |
|---|---|---|
| > 1.0 | 効率的、追加投資すべし | accelerate S&M |
| 0.7 - 1.0 | healthy (median 約 0.7) | 維持 |
| 0.5 - 0.7 | suspect、改善必要 | conversion 改善 |
| < 0.5 | broken、投資抑制 | model 再考 |

#### 4.1.7 Burn Multiple

[出典: David Sacks - The Burn Multiple](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)

`Burn Multiple = Net Burn / Net New ARR`

| 値 | Sacks の評価 | 状態 |
|---|---|---|
| < 1.0x | Amazing | net positive (ARR 追加 1$ あたり burn $1 未満) |
| 1.0 - 1.5x | Great | healthy / 損益分岐近い |
| 1.5 - 2.0x | OK | venture-stage の許容範囲 |
| 2.0 - 3.0x | Suspect | 警戒 |
| > 3.0x | Bad | 危険、cost cut 必要 |

ステージ別の許容上限:

| ステージ | PASS | WATCH | FAIL |
|---|---|---|---|
| Seed | < 3x | 3-5x | > 5x |
| A | < 2x | 2-3x | > 3x |
| B | < 1.5x | 1.5-2x | > 2x |
| C+ | < 1x | 1-1.5x | > 1.5x |

**Pre-revenue / 低 ARR 例外 (E-H-016 解消):** ARR < $100K (年商 1500 万円相当) では Net New ARR が ~0 に近く Burn Multiple は分母発散で意味を持たない。代替指標として **`月次 net burn / runway 残月数` (= 月次 burn 安定度)** と **absolute monthly burn × 想定 12 ヶ月 product market fit 期間** を使用し、ARR > $100K 到達後に Burn Multiple へ移行する。

**Sanity check (E-H-033 解消):** Burn Multiple < 1.0x は (a) 真の効率成長 (b) 必要投資の先送り (c) booking timing artifact のいずれかに起因する。**R&D headcount が YoY flat または減少しているのに Burn Multiple < 1.0x なら投資先送りを疑う**こと。再現性確認には次年度の R&D 計画と sales rep ramp 実績を必ず参照する。

#### 4.1.8 Rule of 40 / Rule of X

[出典: Bessemer - The Rule of X](https://www.bvp.com/atlas/the-rule-of-x)

`Rule of 40 = Revenue Growth % + FCF Margin %`
`Rule of X = (Growth Rate × Multiplier) + FCF Margin`

| 値 (Rule of 40) | 評価 |
|---|---|
| > 50 | Centaur、valuation 二桁 multiple |
| 40 - 50 | Premium |
| 20 - 40 | Discount |
| < 20 | 大幅 discount / 投資不適 |

Rule of 40 を満たす SaaS は全体の 11-30% (2024-25)。

**Valuation premium (E-H-028 解消、`05 §10.3` と canonical 統一):** Rule of 40 が 10pt 改善するごとに EV/ARR multiple が **約 +1.1×** (出典: SaaS Capital Index、Bessemer Cloud Index 2024 回帰)。「Rule of 40 達成 → +121% premium」という表現は「閾値 40 未到達企業 vs 達成企業」の bucket 比較で、`05 §10.3` の +1.1×/10pt は連続的な感応度。**本書では canonical 数値として +1.1×/10pt を採用し、+121% は historical bucket 平均として併記**する。

#### 4.1.9 Gross Margin

| ビジネス形態 | PASS | WATCH | FAIL |
|---|---|---|---|
| Pure SaaS | > 75% | 65-75% | < 65% |
| SaaS + 軽サービス | > 70% | 60-70% | < 60% |
| SaaS + 重サービス / インフラ重 | > 60% | 50-60% | < 50% |
| Marketplace (net) | > 60% | 40-60% | < 40% |
| Fintech (net interest) | > 50% | 30-50% | < 30% |
| Hardware | > 40% | 25-40% | < 25% |

#### 4.1.10 Cash Conversion Score (CCS, Bessemer)

[出典: Bessemer - Cash Conversion Score](https://www.bvp.com/atlas/cash-conversion-score)

`CCS = 現 ARR / (累計調達総額 − 現預金)`

| 値 | 解釈 |
|---|---|
| > 1.0x | best-in-class、IRR 平均 120% |
| 0.5 - 1.0x | healthy |
| < 0.5x | 効率改善必要 |

### 4.2 Marketplace

[出典: a16z - GMV Retention: The Marketplace Metric Most Ignore](https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/)
[出典: CRV - GMV Meaning: What VCs Actually Look For in Marketplaces](https://www.crv.com/content/gmv-meaning)
[出典: Lenny - The Most Important Marketplace Metrics](https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics)

#### 4.2.1 Core Marketplace Metrics

| 指標 | PASS | WATCH | FAIL |
|---|---|---|---|
| GMV growth (MoM, early) | > 15% | 10-15% | < 10% |
| Take Rate | 安定 / 漸増 | flat | declining |
| GMV Retention M12 (consumer) | > 100% | 80-100% | < 80% |
| GMV Retention M12 (B2B) | > 80% | 60-80% | < 60% |
| Liquidity (filled requests %) | > 60% | 40-60% | < 40% |
| Top 1% supply / GMV | < 30% | 30-50% | > 50% |
| Top 1% demand / GMV | < 40% | 40-60% | > 60% |
| Net Revenue / GMV stability | 横ばい / 漸増 | 揺れ | 漸減 |

#### 4.2.2 Series A Marketplace 目安

- 月次 GMV: $500K - $2M
- MoM growth: 15-20%
- GMV retention: > 80%
- 供給 / 需要バランス: 両側 active で 60-70% 充足率

### 4.3 Fintech

| 指標 | PASS | WATCH | FAIL |
|---|---|---|---|
| CAC Payback (months) | < 12 | 12-24 | > 24 |
| Net Interest Margin (lender) | 業界 P50 超 | P30-50 | < P30 |
| Loss rate vs vintage | 想定の 0.7-1.0x | 1.0-1.3x | > 1.3x |
| Capital adequacy ratio | 規制下限 +200bps | +50-200bps | < 規制下限 +50bps |
| Cost of funds | declining | flat | rising |
| Take rate (payments) | 業界水準 | -10% | -25%+ |

### 4.4 Hardware

| 指標 | PASS | WATCH | FAIL |
|---|---|---|---|
| GM 軌道 (3 期) | 漸増 (> +5pp / 年) | flat | declining |
| Inventory Turns | > 6x / 年 | 3-6x | < 3x |
| Working Capital / Revenue | < 15% | 15-30% | > 30% |
| Warranty / Returns | < 2% | 2-5% | > 5% |
| BoM cost / unit (3 期) | declining > 5%/年 | flat | rising |

### 4.5 Consumer (DTC / Subscription)

| 指標 | PASS | WATCH | FAIL |
|---|---|---|---|
| CAC payback (months) | < 6 | 6-12 | > 12 |
| Repeat rate (90 day) | > 35% | 25-35% | < 25% |
| Contribution Margin | > 30% | 20-30% | < 20% |
| Organic / total customer | > 40% | 25-40% | < 25% |

### 4.6 PLG SaaS 特有指標

| 指標 | PASS | WATCH | FAIL |
|---|---|---|---|
| Free → Paid Conversion | > 5% | 2-5% | < 2% |
| Time to Value (median) | < 1 day | 1-7 day | > 7 day |
| Activation Rate | > 40% | 25-40% | < 25% |
| Daily Active / Weekly Active | > 50% | 30-50% | < 30% |
| Product-Qualified Lead → SQL | > 20% | 10-20% | < 10% |

---

## 5. Risk Register (定型リスク分類)

### 5.1 リスク 10 大分類

| # | カテゴリ | 代表リスク | ステージで顕在化しやすい |
|---|---|---|---|
| 1 | Market | TAM 縮小、market timing 失敗、需要消滅 | 全 |
| 2 | Competition | incumbent 反撃、新規参入、価格戦争 | A 以降 |
| 3 | Technology | 実装可能性、scale ボトルネック、security | Pre-seed - B |
| 4 | Execution | hiring、ops、distribution 失敗 | A - C |
| 5 | Financial | runway、burn、capital access | 全 (特に B 以降の down round) |
| 6 | Regulatory | 業界規制、ライセンス、輸出規制 | Fintech / Health / Crypto / Defense 全 |
| 7 | People / Governance | founder dependency、board dynamics、successor 不在 | 全 |
| 8 | Macro | recession、FX、金利、energy cost | 全、特に B 以降 |
| 9 | Concentration | customer / supplier 集中 (top 3 で > 50%) | A - C |
| 10 | IP | 特許侵害、trade secret 流出、源泉コード dispute | 全 |

### 5.2 リスク評価マトリクス

各リスクを (確度 × 影響) で評価し、上位 5-10 を IC Memo に。

| 影響 ＼ 確度 | 低 (10%-) | 中 (10-30%) | 高 (30%+) |
|---|---|---|---|
| 致命 (会社終了) | watch、mitigant | 投資条件で hedge | KILL |
| 大 (-50% valuation) | mitigant | mitigant + monitor | KILL もしくは 大幅 discount |
| 中 (-20% valuation) | log | mitigant | mitigant + monitor |
| 小 (operational) | log | log | mitigant |

### 5.3 リスク詳細リスト

#### 5.3.1 Market risks
- TAM 推定の楽観性
- demand 持続性 (一時 trend か)
- timing が早すぎ / 遅すぎ
- adjacent market への依存
- price elasticity の前提

#### 5.3.2 Competition risks
- incumbent の bundle 反撃 (Microsoft、Google、Amazon、Apple)
- 中国 / インドからの低価格参入
- open source の commoditize
- ベンチャー過密 (同セクター > 5 社が同時調達)
- 価格戦争のリスク

#### 5.3.3 Technology risks
- 中核技術の実装可能性 (POC でしか動かない)
- scale 時の latency / コスト
- セキュリティ (個人情報、決済、医療)
- AI モデル依存 (OpenAI / Anthropic 等の policy 変更)
- 技術陳腐化 (例: モバイル → AI 一次接点)

#### 5.3.4 Execution risks
- 採用計画の現実性 (heads × specialty × geography)
- 営業組織の立ち上げ (rep ramp time、quota attainment)
- ops 拡張 (CS、support、payment、fraud)
- 国際展開のローカライズ
- M&A 統合の失敗

#### 5.3.5 Financial risks
- Runway < 18ヶ月で next round 突入
- gross burn の急増 (budget 超過)
- AR 回収遅延 (DSO 拡大)
- FX 影響 (海外売上の本国会計)
- 不利な term での bridge round

#### 5.3.6 Regulatory risks (業界別)

| 業界 | 主要規制 | 主な確認項目 |
|---|---|---|
| Fintech (米) | BSA / AML、Reg E、FDIC、State MTL | MTL 取得、SAR / CTR フロー、broker-dealer / RIA |
| Fintech (日) | 資金決済法、犯罪収益移転防止法、銀行法、FSA 監督 | 第二種資金移動業 / 決済資金保全、KYC、API ガイドライン |
| Healthcare (米) | HIPAA、HITECH、FDA、Stark Law、Anti-kickback | BAA、PHI 取扱い、510(k) / De Novo / PMA |
| Healthcare (日) | 医薬品医療機器等法 (薬機法)、医師法、個人情報保護法 (要配慮) | PMDA、医療広告 GL、診療報酬収載 |
| Crypto | SEC (Howey)、CFTC、FinCEN、IRS、各国規制 | token の有価証券性、KYC、税扱い、自主規制 (JVCEA) |
| AI | EU AI Act (高リスク認定)、米 AI EO、各国 ガイドライン | 高リスク用途分類、適合性評価、透明性義務 |
| Mobility | 道路運送車両法、道交法、改正 道路法 (自動運転) | レベル 4 認可、保険、データ保存義務 |
| Education | 個人情報保護法、学習指導要領、私学法 (資金) | 児童 / 学生 PII、文科省 GL、教科書認定 |
| Defense | 輸出管理 (ITAR、EAR、安全保障貿易管理 / 外為法) | 該当性判定、ライセンス、デュアルユース |
| Energy | 電気事業法、再エネ特措法、温対法 | 固定買取 / FIP、系統接続、容量市場 |
| Real Estate | 宅建業法、賃貸住宅管理業法、建築基準法 | ライセンス、重要事項説明、サブリース規制 |
| Labor / HR Tech | 個人情報保護法、職安法、労基法、有期雇用 | 個人情報の第三者提供、職業紹介事業ライセンス |

#### 5.3.7 People / Governance risks
- founder dependency (一人が辞めたら何 % が消えるか)
- 共同創業者の equity split / vesting
- 取締役会の composition (creator、investor、independent)
- key person insurance / 後継 plan
- option pool が枯渇

#### 5.3.8 Macro risks
- 景気後退時の budget cycle 短期化 (B2B SaaS)
- 個人消費収縮 (DTC)
- 金利上昇 → growth multiple compression
- 為替 (海外売上の円換算)
- エネルギーコスト (hardware / 製造)

#### 5.3.9 Concentration risks
- 顧客集中 (top 3 で > 50% は warning、> 70% は kill 候補)
- 供給者集中 (single supplier、key BoM)
- 地理集中 (1 国 > 80% は地政学リスク)
- チャネル集中 (Apple App Store、Google Play、Amazon の独占ルート)

#### 5.3.10 IP risks
- 特許侵害訴訟 (NPE / patent troll)
- trade secret 流出 (退職者経由)
- ソースコード所有 (誰のリポジトリ、employer の IP 譲渡)
- open source ライセンス違反 (GPL contamination)
- 商標 (海外展開時の先行登録)

---

## 6. Due Diligence チェックリスト

[出典: Cooley GO - Sample VC Due Diligence Request List](https://www.cooleygo.com/documents/sample-vc-due-diligence-request-list/)
[出典: Affinity - VC Due Diligence Checklist](https://www.affinity.co/guides/due-diligence-checklist-for-venture-capital)
[出典: Kruze - VC Due Diligence Checklist](https://kruzeconsulting.com/blog/due-diligence-checklist/)

### 6.1 Commercial DD

| 項目 | 内容 | エビデンス |
|---|---|---|
| 顧客 interview | top 10 顧客 + churn 顧客 5 | call note、NPS |
| Win/Loss 分析 | 直近 12ヶ月の deal log | win rate、reasons |
| NRR / GRR 検証 | 顧客 cohort 突合 | billing system raw |
| Pricing power | 値上げ実績、競合比 | proposal、price list |
| Pipeline 質 | stage 別、coverage、aging | CRM extract |
| Customer concentration | top 3、top 10 | revenue 表 |
| Sales rep productivity | quota、attainment、ramp | rep level data |

### 6.2 Technical DD

| 項目 | 内容 | エビデンス |
|---|---|---|
| Architecture review | infra、microservices、data flow | architecture diagram |
| Scalability test | load test、bottleneck | benchmark report |
| Security audit | SOC2、ISO27001、pentest | 認証書、pentest report |
| Code quality | static analysis、test coverage、tech debt | SonarQube、coverage % |
| Dependency / OSS | license、CVE、EOL component | SBOM |
| AI / Data assets | model、データソース、bias、ガバナンス | model card、data lineage |
| DevOps maturity | CI/CD、observability、incident response | playbook |

### 6.3 Financial DD (QofE)

| 項目 | 内容 | エビデンス |
|---|---|---|
| Quality of Earnings (QofE) | 認識基準、繰延、cut-off | 監査調書、ASC606 適用 |
| 正常化 EBITDA | 一時項目、関連当事者、過大報酬 | bridging schedule |
| Working Capital | DSO、DPO、DIO の推移 | aging report |
| 資本支出と維持的 capex | 装置 / SaaS / R&D capitalization | fixed asset register |
| Tax position | NOL、tax credits、transfer pricing | tax return、TP doc |
| Cash conversion | OCF vs EBITDA | 三表 |
| Bookings vs Revenue 整合 | ARR、CARR、deferred | billing system |
| Customer-level P&L | unit economics 検証 | cohort 表 |

### 6.4 Legal DD

| 項目 | 内容 | エビデンス |
|---|---|---|
| Corporate structure | 設立、subsidiary、branch | charter、organization chart |
| Cap Table | shares、options、warrants、SAFE | cap table、409A |
| Material contracts | 顧客 / 供給者 top 10 + assignment 条項 | 契約原本 |
| IP assignments | 創業者 / employee の IP 譲渡 | IP assignment agreement |
| Litigation | 訴訟、紛争、demand letter | 訴訟一覧、弁護士 letter |
| Employment | NDA、PIIA、competition、stock plan | template + 100% signed |
| Compliance | 業界規制、ライセンス、データ保護 | ライセンス copy、policy |
| Insurance | D&O、E&O、cyber、product liability | policy、limit |

### 6.5 HR / Cultural DD

| 項目 | 内容 |
|---|---|
| Org chart | 機能別、報告系統、open req |
| Tenure 分布 | 平均、中央値、attrition rate |
| Compensation benchmark | 業界比、equity refresh |
| Engagement / eNPS | survey 結果、participation |
| DEI metrics | gender、ethnicity、leadership |
| Key person risk | 一人辞めたら何 % が消えるか |
| Culture indicators | Glassdoor、退職理由、退職 trend |

### 6.6 Tax DD

| 項目 | 内容 |
|---|---|
| Federal / State / Local tax | 過去 3 年申告 |
| Sales tax / VAT | nexus 分析、過去 exposure |
| Transfer pricing | inter-company、TP study |
| NOL availability | §382 制限、change of control |
| R&D credit | 過去 / 将来適用可能性 |
| Stock comp deduction | ISO / NSO / RSU 取扱い |
| 国際税 (BEPS、Pillar 2) | 該当性 |

### 6.7 ESG DD

| 軸 | 観点 |
|---|---|
| Environmental | エネルギー、carbon、water、waste |
| Social | 人権、サプライチェーン、安全、コミュニティ |
| Governance | board independence、ethics、whistleblower、cyber |

---

## 7. Market Sizing 手法

### 7.1 Top-Down

「業界レポート → 自社シェア」。

`SOM = TAM × penetration % × win rate`

利点: 速い、benchmark しやすい。
欠点: 楽観バイアス、TAM が過大評価されやすい。

### 7.2 Bottom-Up

`SOM = (# of target customers) × (average revenue per customer per year)`

利点: 説得力が高い、検証可能。
欠点: 時間がかかる、各前提を defend する必要。

### 7.3 Value-Based

`TAM = (target population) × (pain point savings) × (willingness to pay %)`

利点: 価値ベースで thesis に直結。
欠点: 推定が saatu (主観)。

### 7.4 Triangulation

3 手法でレンジ確認。一致しなければ理由を追跡。

| 手法 | TAM 推定 | 採用根拠 |
|---|---|---|
| Top-down | $X | Gartner / IDC |
| Bottom-up | $Y | 顧客数 × ARPU |
| Value-based | $Z | 価値削減 × WTP |
| **採用 TAM** | min/max を提示 | 中央値か bottom-up |

**Tiebreak ルール (E-H-035 解消、3 手法乖離 >2x 時):**
- **Top-down >> Bottom-up**: Gartner/IDC は existing software spend を過大集計しがち。**Bottom-up を主、Top-down を上限 cap** として採用 (top-down は飽和ありの上限値として扱う)。
- **Bottom-up >> Top-down**: 既存 analyst 報告に未収のカテゴリーを発見した可能性。**最低 5 件の顧客 / 業界専門家インタビュー** で bottom-up 仮定を実証してから Tier 2 採用 (実証なしは Tier 3)。
- **Value-based が他 2 法と大きく乖離**: WTP 仮定が論理飛躍の signal。`09 §10` の WTP 検証 (ペアワイズ価格、conjoint) を実施。
- **3 法のレンジを単純平均しない**: それぞれが異なる error mode を持つため、平均は誤差の合成。**主 1 法を選び、他 2 法は sanity check として上下境界**を出す。

### 7.5 公開ソース (英語 / 日本語)

| ソース | カバー | 言語 |
|---|---|---|
| Gartner | IT、SaaS | EN |
| IDC | IT | EN |
| Forrester | IT、CX | EN |
| Statista | 一般 | EN/JP |
| CB Insights | スタートアップ、市場 | EN |
| Crunchbase | スタートアップ | EN |
| 経済産業省 | 業界統計、政策 | JP |
| 矢野経済研究所 | 業界調査 | JP |
| 富士キメラ総研 | テクノロジー業界調査 | JP |
| INITIAL (Speeda) | 国内スタートアップ | JP |
| STARTUP DB | 国内スタートアップ | JP |
| 帝国データバンク | 企業情報、業界 | JP |

---

## 8. Competitive Analysis

### 8.1 Porter's 5 Forces

| 力 | 評価軸 | 質問 |
|---|---|---|
| 既存競合 | 集中度、成長性、固定費 | 価格戦争のリスクは? |
| 新規参入 | 参入障壁、規模の経済、ブランド | 1 年で参入可能か? |
| 代替品 | 代替の有無、価格性能、switching | 別 category への乗換え圧力は? |
| 買い手 | 集中度、情報、switching cost | 価格交渉力は? |
| 売り手 | 集中度、代替、forward integration | 価格を上げられる供給者は? |

### 8.2 Wardley Mapping

Genesis → Custom Built → Product / Rental → Commodity / Utility の 4 段階で各 component を mapping。
- 自社 component が genesis / custom 寄り → moat 候補
- 自社 component が commodity 寄り → コスト勝負

### 8.3 Strategic Group Analysis

軸を 2 つ選び (例: price × scope、price × geography) 、競合をプロット。
- 同 group 内: 競合圧高
- 別 group: 直接競合は低い

### 8.4 Capability Map

機能別に capability を 0-5 で採点。

| Capability | 自社 | 競合 A | 競合 B |
|---|---|---|---|
| 製品コア | 5 | 4 | 3 |
| 営業 | 3 | 5 | 4 |
| マーケ | 3 | 4 | 5 |
| ops | 4 | 3 | 4 |

### 8.5 Pricing Comparison

価格 + 価値 (機能、サポート、SLA) の表を作る。価格と価値の散布で「underpriced (under-monetized)」象限を発見。

### 8.6 Feature Matrix

50-100 機能の表で ✓/✗/部分。買い手の購買基準と突合。

---

## 9. Founder / Team 評価

### 9.1 評価軸

| 軸 | 内容 | scoring (0-5) |
|---|---|---|
| Domain expertise | 業界経験 (years × depth) | 学位 / 過去成功で proxy |
| Founder-market fit | なぜこの人がこの問題を解くか | unique insight、過去関与 |
| Team completeness | CEO / CTO / CXO の充足 | gap を採用計画で埋められるか |
| Track record | 過去 exit、scaling 経験 | 売上 / employee scale 経験 |
| Coachability | feedback への適応 | 過去対話、reference |
| Communication | 投資家 / 社員 / 顧客への説明力 | pitch、town hall |
| Hiring power | top talent を引き寄せるか | 過去採用例 |
| Resilience | 危機対応、persistence | 過去の苦境対応 |

### 9.2 Reference Check (CEO 360)

[出典: First Round - Reference Checks topic](https://search.firstround.com/topics/reference-checks)

最低でも 5 名:
- 元上司 1
- 元同僚 (peer) 1
- 元部下 1
- 顧客 1
- 共同創業者 / 早期社員 1

質問例:
- 「もう一度一緒に働けるとしたら、どの role なら yes、どの role なら no?」
- 「彼 / 彼女の最大の blind spot は?」
- 「過去に一番難しかった時、どう判断した?」
- 「再投資すべきか? 理由は?」

### 9.3 Founder dossier (定型)

| 項目 | 内容 |
|---|---|
| 学歴 | 大学、専攻、修了年 |
| 職歴 | 各社、role、achievement |
| 過去起業 | 結果 (exit / shutdown / 継続) |
| 公開発信 | blog、podcast、book |
| ネットワーク | 業界 connection の証跡 |
| Public speaking | 動画 / pitch から評価 |
| Background check | 信用、訴訟、薬物、ハラスメント |

### 9.4 Co-founder fit 評価

- equity split の合理性 (50/50 か 60/40 か)。
- vesting schedule (4 年 + 1 年 cliff が標準)。
- 役割の overlap / gap。
- 過去の協働経験。
- 意思決定プロセス (どちらが何を決めるか明文化)。
- 衝突の対処 (過去事例)。

---

## 10. Pivot / Persevere / Kill Decision Framework

### 10.1 Lean Startup ベース

Eric Ries の「Innovation Accounting」(validated learning):

1. **establish baseline**: 主要 metric の現状値。
2. **tune the engine**: 仮説 → 実験 → 学習。
3. **pivot or persevere**: 改善が次の閾値に近づくか。

### 10.2 Pivot 種類

| Pivot 種類 | 内容 |
|---|---|
| Zoom-in | 1 機能を core 製品に |
| Zoom-out | 製品を 1 機能化、より広い解決策 |
| Customer segment | 同問題を別顧客に |
| Customer need | 同顧客の別 need に |
| Platform | application → platform |
| Business architecture | B2C ↔ B2B |
| Value capture | 価格 / 収益モデル変更 |
| Engine of growth | viral / paid / sticky の切替 |
| Channel | 流通経路変更 |
| Technology | 同問題を別技術で |

### 10.3 Kill criteria (pre-defined)

事前に明文化しておくべき stop conditions:

| カテゴリ | criteria 例 |
|---|---|
| Founder | 共同創業者離脱 / 重大な ethics 違反 |
| Cash | runway < 3 ヶ月かつ bridge 不在 |
| PMF | 12 ヶ月で active retention < 20% |
| Market | TAM 推定が当初の 1/3 以下に修正必要 |
| Competition | incumbent が free で同機能、置換可能 |
| Regulatory | 業界規制で事業 illegal |

### 10.4 Persevere の条件

- 1 つ以上の leading indicator が改善 trend。
- 仮説のうち 1 つ以上が validated。
- runway は次の learning sprint まで足りる (最低 6 ヶ月)。
- founder の commitment と learning 速度が高い。

---

## 11. Post-investment Monitoring KPIs

### 11.1 Monthly KPI Dashboard 必須項目

| カテゴリ | KPI |
|---|---|
| Top of funnel | website visit、MQL、SQL |
| Pipeline | open opportunity、coverage、weighted |
| Bookings | new、expansion、renewal |
| Revenue | MRR/ARR、growth、NRR/GRR |
| Customers | logos new/lost、active、churn |
| Cash | revenue、burn、runway、cash on hand |
| HC | total、open、attrition |
| Product | DAU/MAU、activation、time to value |
| Quality | bug、SLA、incident |

### 11.2 Board Meeting Cadence

| ステージ | 頻度 |
|---|---|
| Seed | 月次 (CEO + lead) |
| A | 6-8 週ごと、formal board |
| B | 8-12 週ごと、formal board + committee |
| C+ | 四半期、formal + audit committee |

### 11.3 Reforecast Trigger

下記イベントで forecast を再構築:

- 月次 actual が forecast の ±15% 超 (3 ヶ月連続)
- runway 12 ヶ月切り
- 主要顧客 top 3 のいずれかが churn
- 主要 hire の離脱
- 規制変更
- マクロイベント (recession 兆候、業界 shock)

---

## 12. Exit Modeling

### 12.1 IPO Readiness Checklist

| 項目 | 閾値 (米国 NASDAQ 一般) |
|---|---|
| ARR | $200M+ |
| Growth | > 30% YoY |
| Gross Margin | > 70% |
| FCF | break-even に近い、または明確な path |
| Rule of 40 | > 40 |
| Customer count | > 1,000 (B2B SaaS) |
| Logo concentration | top 10 で < 30% |
| 監査 | Big4 / 主要監査法人で 3 期 |
| 内部統制 | SOX 対応、material weakness なし |
| Board | independent director majority |
| 経営陣 | CFO / 法務 / IR の整備 |

### 12.2 M&A Acquirer Mapping

| タイプ | 動機 | 評価軸 |
|---|---|---|
| Strategic - core | 同業、シェア拡大 | 売上 / 顧客 / IP |
| Strategic - adjacency | 隣接領域へ拡張 | 顧客重複、bundle |
| Strategic - platform | platform の埋める piece | 技術、time-to-market |
| Financial - PE | EBITDA、安定 cash flow | EBITDA、growth、resilience |
| Financial - SPAC | 上場代替 | story、growth、TAM |

各社につき: 過去 acquisition、acquisition appetite、購買力、organizational fit を mapping。

### 12.3 Secondary Market Dynamics

- 直近ラウンド評価額の 70-100% が secondary 取引価格の目安。
- 流動性は post-Series C で増える。
- tender offer (会社主導) が EE liquidity の一般的手段。
- 規制 (Rule 144、ROFR、co-sale) を確認。

### 12.4 Fund-level Returns

| 指標 | 定義 | 目安 |
|---|---|---|
| DPI | Distributions / Paid-in | > 1.0x で「資金回収済」 |
| TVPI | (Distributions + NAV) / Paid-in | > 3.0x で top-quartile (vintage 依存) |
| IRR | 内部収益率 | > 20% で top-quartile (vintage 依存) |
| Net IRR | 手数料控除後 IRR | LP 視点 |

[出典: Cambridge Associates Benchmark]、[出典: PitchBook NVCA Venture Monitor]

### 12.5 Valuation 三角測定 (Exit 想定)

| 手法 | 適用 |
|---|---|
| Public comp multiple | 5+ 社の forward EV/Revenue 中央値 |
| Precedent M&A | 過去 12-24 ヶ月の同業 M&A multiple |
| DCF | 10 年予測 + terminal value |
| LBO | PE buyer の支払可能額 |
| IPO price | ARR × forward multiple × IPO discount |

---

## 13. PASS / WATCH / FAIL 判定ロジック

### 13.1 三段階フラグの集約 (採用ルール)

> **採用方針**: weighted scoring + override (kill criteria 単独で FAIL)。
> 投資判断は単一の閾値で決まらない (cross-correlation のため)。
> ただし以下は **single-flag FAIL** で deal break:
>
> - founder integrity 違反 (横領、虚偽、ハラスメント、契約違反)
> - cash runway < 3 ヶ月 (緊急 bridge も不可)
> - 規制違反で事業違法
> - audit qualified opinion / material weakness
> - cap table の不可解な設計 (anti-dilution 不可避、liquidation preference 多重)

### 13.2 Weighted Scoring の例 (Series A SaaS)

各軸 0-5 で採点、weight × score を合計。

| 軸 | Weight (Series A) | Score (例) | Weighted |
|---|---|---|---|
| Founder | 0.20 | 4 | 0.80 |
| Market | 0.15 | 4 | 0.60 |
| Product | 0.10 | 4 | 0.40 |
| PMF (NRR/retention) | 0.20 | 3 | 0.60 |
| Growth | 0.15 | 4 | 0.60 |
| Unit Economics | 0.10 | 3 | 0.30 |
| GTM | 0.05 | 3 | 0.15 |
| Risks (逆方向) | 0.05 | 3 | 0.15 |
| **合計** | 1.00 | - | **3.60 / 5** |

| 合計スコア | 判定 |
|---|---|
| > 4.0 | PASS / INVEST |
| 3.0 - 4.0 | WATCH (条件付投資 or pass) |
| < 3.0 | FAIL / PASS (decline) |

### 13.3 Vision Tax (定量を上回る確信)

定量的に WATCH の deal でも、創業者 vision や insight が exceptional な場合に invest する。
ただし vision tax は **明示的に文書化** する。

例:
- 「定量は WATCH (NRR 105%、CAC payback 22ヶ月) だが、創業者は X 業界で唯一の deep insight を持ち、market-shaping 能力がある (vision tax +0.5)」

### 13.4 Conviction Memo

IC 通過前に lead partner が書く 1 ページ:

- 「私はなぜこの deal を信じるか」
- 「この投資が失敗するシナリオ TOP3」
- 「次の 12 ヶ月で何が起きれば thesis は validated か」
- 「次の 12 ヶ月で何が起きれば thesis は invalidated か」

---

## 14. 落とし穴 (cognitive biases)

| バイアス | 内容 | 緩和策 |
|---|---|---|
| Confirmation bias | thesis に合う証拠だけ集める | red team、devil's advocate |
| Sunk cost | 既投資のせいで継続投資 | 「new money」基準で判断 |
| Anchoring | 先行 VC の評価額に引きずられる | 自社の独立 valuation |
| FOMO (hot deal) | 「他が入るから」で判断 | thesis check を独立に |
| Pattern matching の過信 | 過去の成功 pattern が今も通用と仮定 | counter-evidence 探す |
| Survivorship bias | 成功事例から逆算 | 失敗例も同等に集める |
| Halo effect | 創業者の有名 / 学歴で甘く | 客観 metric で校正 |
| Spray and pray | 数を打つ / 質低い | 集中投資、conviction |
| Recency bias | 直近 trend を永続と誤認 | サイクル意識、reversion |
| Endowment effect | 自社 portfolio を過大評価 | 第三者 mark |
| Authority bias | 著名 partner の発言で押し切る | data-driven culture |
| Overconfidence | 自分の判断を過信 | track record の厳密 review |

---

## 15. ベンチマーク値 / 公開データ (出典明記)

### 15.1 主要公開データソース

| ソース | カバー | URL / 出典 |
|---|---|---|
| Carta | 株式 / 報酬 / valuation | carta.com/data |
| PitchBook | プライベート市場 | pitchbook.com |
| CB Insights | スタートアップ、トレンド | cbinsights.com |
| Crunchbase | 調達、創業者 | crunchbase.com |
| Bessemer State of the Cloud | SaaS マクロ | bvp.com/atlas |
| OpenView SaaS Benchmarks | SaaS metric | openviewpartners.com (旧)、High Alpha と提携 |
| KeyBanc / KBCM SaaS Survey | SaaS private 詳細 | KeyBanc 年次 |
| Cambridge Associates | VC fund return | cambridgeassociates.com |
| INITIAL (Speeda) | 国内スタートアップ | initial.inc |
| STARTUP DB | 国内スタートアップ | startup-db.com |
| 経済産業省 | 業界統計、政策 | meti.go.jp |
| 矢野経済研究所 | 業界調査 | yano.co.jp |
| 帝国データバンク | 企業情報 | tdb.co.jp |

### 15.2 直近 (2024-2025) の SaaS ベンチマーク

[出典: 2025 SaaS Benchmarks - High Alpha](https://www.highalpha.com/saas-benchmarks)
[出典: ScaleXP - 2025 SaaS Benchmarks: CAC Payback](https://www.scalexp.com/blog-saas-benchmarks-cac-payback-2025/)
[出典: Benchmarkit - 2025 SaaS Performance Metrics](https://www.benchmarkit.ai/2025benchmarks)

| 指標 | Median 2024-25 | Top quartile |
|---|---|---|
| ARR Growth (median) | 30-35% | 60%+ |
| NRR (private) | 101-102% | 120%+ |
| GRR | 約 90% | 95%+ |
| LTV/CAC | 3.6:1 | 5:1+ |
| CAC Payback | 約 20 ヶ月 (悪化) | < 12 ヶ月 |
| Gross Margin (SaaS) | 75% | 80%+ |
| Rule of 40 達成率 | 11-30% | - |
| Burn Multiple (median) | 1.5-2x | < 1x |

### 15.3 VC Return Distribution

[出典: Cambridge Associates、PitchBook NVCA Venture Monitor]

| Vintage / Quartile | Net IRR | TVPI |
|---|---|---|
| Top decile (10%) | 25%+ | 3.5x+ |
| Top quartile (25%) | 18-25% | 2.5-3.5x |
| Median | 8-12% | 1.5-2.0x |
| Bottom quartile | < 5% | < 1.3x |

### 15.4 日本のスタートアップ調達ベンチマーク

[出典: INITIAL Japan Startup Finance 2025H1](https://initial.inc/articles/japan-startup-finance-2025h1)
[出典: Strategy& Japan - スタートアップ投資バリュエーション](https://www.strategyand.pwc.com/jp/ja/publications/periodical/strategyand-foresight-23/sf23-05.html)

| ステージ | 中央値調達額 | 中央値評価額 (post) | 到達期間 |
|---|---|---|---|
| Seed | 0.3-0.7 億円 | 3-8 億円 | 6-18 ヶ月 |
| Series A | 1-3 億円 | 10-30 億円 | 18-42 ヶ月 |
| Series B | 5-15 億円 | 30-100 億円 | 36-60 ヶ月 |
| Series C | 15-50 億円 | 100-300 億円 | 60-84 ヶ月 |
| D 以降 | 50 億円超 | 300 億円超 | 72 ヶ月超 |

ラウンド間 step-up (中央値):

| 区間 | step-up |
|---|---|
| Seed → A | 3.4x |
| A → B | 1.9x |
| B → C | 1.8x |
| C → D 以降 | 1.7x |

近年トレンド: PSR (売上倍率) → PER (利益倍率) へ重視シフト。

---

## 16. IC Memo テンプレート (1 ページ要約 + 詳細版)

### 16.1 1 ページ Executive Summary テンプレート (空白)

```
================================================================================
INVESTMENT COMMITTEE MEMO — EXECUTIVE SUMMARY
================================================================================

[Company Name]                                       Date: YYYY-MM-DD
Sector / Vertical: [ ___________________________________________________ ]
Lead: [name]    Co-lead: [name]    Author: [name]

DEAL HEADER
- Round:                    [Pre-seed / Seed / A / B / C / D+]
- Round size:               [USD / JPY]
- Pre-money valuation:      [USD / JPY]
- Post-money valuation:     [USD / JPY]
- Investment amount (我々):  [USD / JPY]
- Ownership target:         [ %  pre / post option pool]
- Security:                 [Priced equity / SAFE / Convertible note]
- Board:                    [Seat / Observer / None]
- Pro rata:                 [Yes / No, terms]

INVESTMENT THESIS (3-5)
1. _____________________________________________________________________
2. _____________________________________________________________________
3. _____________________________________________________________________
4. _____________________________________________________________________
5. _____________________________________________________________________

KEY METRICS (latest available)
- ARR / GMV:                [          ]   YoY: [   %]
- NRR / GRR:                [   % /   %]
- Burn Multiple / CAC PB:   [   x  /    months]
- Gross Margin:             [   %]
- Runway:                   [   months]
- Headcount:                [    , next 12mo plan: +   ]

TOP 3 RISKS / MITIGANTS
1. ___________________ → _________________________________________________
2. ___________________ → _________________________________________________
3. ___________________ → _________________________________________________

WHY NOW / WHY THIS / WHY YOU
Why Now:    _____________________________________________________________
Why This:   _____________________________________________________________
Why You:    _____________________________________________________________

EXIT VIEW
- Path:           [IPO / Strategic / PE / Secondary]
- Timing:         [   years]
- Comparable:     [list]
- Target return:  [    x MOIC,     % IRR]

RECOMMENDATION
☐ INVEST   ☐ INVEST WITH CONDITIONS   ☐ WATCH   ☐ PASS
Conditions / next steps: ________________________________________________
================================================================================
```

### 16.2 詳細版テンプレート (15-20 ページ)

```
================================================================================
INVESTMENT COMMITTEE MEMORANDUM — FULL VERSION
================================================================================

1. EXECUTIVE SUMMARY                                                  [p.1]
   1.1 Deal Header
   1.2 Investment Thesis (3-5)
   1.3 Recommendation & Terms

2. COMPANY OVERVIEW                                                   [p.2-3]
   2.1 One-liner & founding story
   2.2 History / milestone
   2.3 Team (founder bio、key hire、headcount)
   2.4 Operating model (拠点、リモート / オンサイト)

3. MARKET ANALYSIS                                                    [p.4-6]
   3.1 TAM / SAM / SOM (top-down × bottom-up triangulation)
   3.2 Market growth & drivers
   3.3 Competitive landscape (Porter's 5 / Wardley / strategic group)
   3.4 Regulatory environment
   3.5 Why Now (3-5 トレンド)

4. PRODUCT / TECHNOLOGY                                               [p.7-8]
   4.1 Product overview / value prop
   4.2 Differentiation & moat
   4.3 IP / patents / trade secret
   4.4 Roadmap (12-24 ヶ月)
   4.5 Technical risk

5. GO-TO-MARKET STRATEGY                                              [p.9]
   5.1 Sales motion (PLG / SLG / hybrid)
   5.2 Channels & partnerships
   5.3 ICP (Ideal Customer Profile)
   5.4 Pricing / packaging

6. BUSINESS MODEL & UNIT ECONOMICS                                    [p.10-11]
   6.1 Revenue model
   6.2 Unit economics by segment
   6.3 Customer concentration
   6.4 LTV / CAC / payback / Magic Number

7. FINANCIAL PERFORMANCE                                              [p.12-13]
   7.1 Historical (3 期 P/L、BS、CF)
   7.2 Forecast (24-36 ヶ月)
   7.3 Bookings vs revenue 整合
   7.4 Burn / runway

8. CAPITAL STRUCTURE & USE OF PROCEEDS                                [p.14]
   8.1 Cap table (pre / post)
   8.2 Liquidation preference structure
   8.3 Option pool
   8.4 Use of Proceeds breakdown

9. VALUATION                                                          [p.15]
   9.1 Triangulation (comp、precedent、DCF、VC method)
   9.2 Pricing rationale
   9.3 Sensitivity (best / base / worst)

10. RISKS & MITIGANTS                                                 [p.16-17]
    10.1 Top 5-10 risks (確度 × 影響)
    10.2 Mitigants
    10.3 Trigger events to monitor

11. EXIT STRATEGY                                                     [p.18]
    11.1 Path (IPO / M&A / secondary)
    11.2 Acquirer mapping
    11.3 Timing & valuation target
    11.4 DPI / TVPI / IRR projection

12. RECOMMENDATION & NEXT STEPS                                       [p.19]
    12.1 Final recommendation
    12.2 Conditions precedent
    12.3 Post-investment plan (board、KPI、reforecast triggers)

13. APPENDIX                                                          [p.20+]
    13.1 DD findings (commercial / technical / financial / legal)
    13.2 Reference checks
    13.3 Detailed financial model
    13.4 Customer interview notes
================================================================================
```

---

## 17. IC Memo 完成形サンプル (架空企業: "Kura AI K.K.")

> **目的**: フレームワークが end-to-end で動くことの validation。
> 架空企業 Kura AI K.K. (B2B SaaS、Vertical AI for 製造業 SCM) の Series A 案件を題材に、フレームワークを通しで適用する。

### 17.1 Executive Summary

```
================================================================================
INVESTMENT COMMITTEE MEMO — EXECUTIVE SUMMARY
================================================================================

Kura AI 株式会社                                       Date: 2026-04-18
Sector / Vertical: 製造業向け Vertical AI SaaS (SCM 最適化)
Lead: 山田  Co-lead: 鈴木  Author: 林

DEAL HEADER
- Round:                    Series A
- Round size:               4.0 億円 (USD 約 27M 換算)
- Pre-money valuation:      18.0 億円
- Post-money valuation:     22.0 億円
- Investment amount (我々):  2.5 億円
- Ownership target:         11.4% post-money (post option pool 拡大後)
- Security:                 Priced equity (Series A Preferred、1x non-participating)
- Board:                    1 seat (lead investor)
- Pro rata:                 Yes (Series B、C で行使、major investor 権利付与)

INVESTMENT THESIS
1. 日本の製造業 SCM 領域で、AI 需要予測 / 在庫最適化を月額 SaaS で提供。
   業界 1 位の Kinaxis / o9 は ACV 1 億円超、Kura は 500-1,500 万円帯で
   中堅製造業 (売上 100-500 億) を狙う構造的 white space を発見。
2. 創業 CEO は元キーエンス FA、CTO は元 Preferred Networks リサーチャー。
   創業者の「日本製造業の暗黙知 → AI 学習データ化」アプローチは
   既存外資 SaaS には 12-18 ヶ月複製困難。
3. 過去 12 ヶ月で ARR 0.2 → 0.9 億円 (4.5x)、NRR 121%、ロゴ churn 0%。
   T2D3 の triple year に整合する軌道。
4. 製造業 SCM の AI 化は政策追風 (経産省 製造 DX、サプライチェーン強靭化)。
   2025 年からの中堅製造業の DX 予算拡大が明確に follow wind。
5. 24 ヶ月で ARR 4-6 億円、NRR 115%+ 維持、CAC payback 18 ヶ月以内に
   到達できれば、Series B 評価額 80-120 億円が可視化。

KEY METRICS (2026-03 末)
- ARR:                      0.92 億円        YoY: +362%
- NRR / GRR:                121% / 100%
- Burn Multiple / CAC PB:   1.4x / 14 ヶ月
- Gross Margin:             72%
- Runway (current):         8 ヶ月 (本ラウンド後 24 ヶ月)
- Headcount:                18 名、24 ヶ月で +25 名計画 (含 4 名 sales)

TOP 3 RISKS / MITIGANTS
1. 顧客集中 (top 3 で 58% of ARR) → 24 ヶ月で top 3 を 30% 以下に下げる
   営業計画を IC 条件として monitor (四半期 review)。
2. 製造業の deal cycle (6-9 ヶ月) → CFO 採用 + 公的助成金 (経産省、NEDO)
   利用で runway を 24 ヶ月確保、安定。
3. 大手外資 (Kinaxis、SAP、o9) の中堅セグメント参入 → 既存 8 社の
   3 年契約 + 暗黙知データセットで 12-18 ヶ月の moat。

WHY NOW / WHY THIS / WHY YOU
Why Now:    経産省 製造 DX 補助金 + サプライチェーン強靭化政策 + 中堅製造業の
            ERP 更新 cycle (2024-2027) が重なる 3 年 window。
Why This:   日本製造業の暗黙知を formalize して LLM ファインチューニングに
            投入する独自 pipeline。Kinaxis / o9 は英語汎用モデル中心で
            日本 SMB に未対応。
Why You:    元キーエンス FA で 8 年営業 → 顧客 8 社のうち 6 社は前職時代の
            関係。CTO は PFN で大規模時系列モデル経験。CFO 採用済 (元 freee)。

EXIT VIEW
- Path:           Strategic M&A (1st)、IPO (2nd)
- Timing:         5-7 years
- Comparable:     Kinaxis (TSX、EV/Revenue 8x)、o9 (private、約 12x at peak)
                  日本: Anaplan 買収 (Thoma Bravo)、Companion (M&A)
- Target return:  10-15x MOIC、IRR 45-55% (base case)

RECOMMENDATION
☑ INVEST WITH CONDITIONS
Conditions / next steps:
  - CFO 採用が closed (現状 verbal accept、書面契約待ち)
  - 既存 anti-dilution は broad-based weighted average に統一
  - 独立取締役 1 名追加 (12 ヶ月以内)
  - 月次 KPI dashboard 提供 (lead が指定 format)
  - 顧客 top 3 への面談実施 (post-closing 30 日以内)
================================================================================
```

### 17.2 詳細版 (主要章)

#### 17.2.1 Company Overview

**One-liner**: 中堅日本製造業に AI 需要予測 / 在庫最適化 SaaS を月額 50-150 万円で提供し、Kinaxis / o9 が捨ててきた中堅セグメントを取りに行く Vertical AI 会社。

**Founding story**: 創業 CEO は 2014-2022 でキーエンス FA 営業、年間 70 件超の中堅製造業を担当。その間に「Excel / 紙 / 暗黙知」での生産計画が依然として支配的で、外資 SaaS は ACV 1 億円超のため大手しか採用できない構造を発見。CTO は PFN で時系列予測モデルを 5 年間研究、創業 CEO の妹の元同僚として紹介で参画。

**History / Milestone**:
| 時期 | イベント |
|---|---|
| 2023-04 | 創業、Pre-seed 50M (3 社の Angel) |
| 2023-09 | MVP リリース、design partner 2 社 (大手金属加工) |
| 2024-03 | Seed 1.5 億円 (XX VC lead) |
| 2024-06 | プロダクト GA |
| 2024-12 | ARR 0.2 億円到達 |
| 2025-09 | Tier 1 顧客 (売上 200 億規模) 8 社到達 |
| 2026-03 | ARR 0.92 億円、NRR 121% |

**Team**:
| Role | 名前 | 経歴 |
|---|---|---|
| CEO | 田中 | 元キーエンス FA 営業 8 年、東京工業大学 |
| CTO | 佐藤 | 元 PFN 時系列予測リサーチャー、東京大学 PhD |
| VP Eng | 鈴木 | 元 LINE インフラ |
| VP Sales | 高橋 | 元 SAP 製造業 SE |
| CFO (verbal) | 渡辺 | 元 freee Finance Manager |
| Headcount | 18 (Eng 9, Sales 4, CS 2, Ops 3) |

**Operating model**: 東京 + 大阪 (顧客密度)、リモート + 月 1 出社。

#### 17.2.2 Market Analysis

**TAM / SAM / SOM**:

| 軸 | 推定 | 計算 / 出典 |
|---|---|---|
| TAM | 約 5,000 億円 | 日本製造業 SCM IT 市場 (矢野経済研究所 2024) |
| SAM | 約 800 億円 | 中堅製造業 (売上 100-500 億) 約 8,000 社 × 想定 ARPU 1,000 万円 |
| SOM (5 年) | 約 80 億円 | 800 社獲得 × ARPU 1,000 万円 (10% シェア仮定) |

**Bottom-up 検証**: 2026 時点で Kura は 8 社、ARPU 1,150 万円。SOM の 1% 弱を 2 年で達成。

**Why Now (3 トレンド)**:
1. **政策追風**: 経産省 製造 DX 補助金、サプライチェーン強靭化政策 (2024-2027)。
2. **ERP 更新 cycle**: 2008-2014 に導入された SAP / Oracle ERP の 15-20 年保守切れ。
3. **AI コスト低下**: GPT-4 級モデルの API コストが 2 年で 1/10、SaaS 経済性が成立。

**Competitive landscape**:

| 競合 | ACV | 顧客層 | 強み | 弱み |
|---|---|---|---|---|
| Kinaxis | 1-3 億円 | 大手 | 計画力、トヨタ採用 | 日本 SMB 非対応、ACV 高 |
| o9 Solutions | 1-2 億円 | 大手 | 多変量、ML | 日本語 UI 弱、price |
| SAP IBP | 5,000 万-2 億円 | 大手 | ERP 連携 | 複雑、SI 重 |
| Asprova | 500-1,500 万円 | 中堅 | 老舗、生産スケジュール | AI 弱、UI 古 |
| **Kura AI** | **500-1,500 万円** | **中堅** | **AI、UX、暗黙知 pipeline** | **若い、機能不足** |

**Porter's 5 Forces 評価**:
| 力 | 評価 | コメント |
|---|---|---|
| 既存競合 | 中 | 大手は ACV 帯違い、Asprova は AI 弱 |
| 新規参入 | 高 | LLM democratization で参入容易 |
| 代替品 | 中 | Excel + コンサル、内製 |
| 買い手 | 中 | 中堅製造業の switching cost 中 |
| 売り手 | 低 | クラウド / LLM はコモディティ化中 |

#### 17.2.3 Product / Technology

- **製品**: 需要予測、在庫最適化、生産計画、購買最適化の 4 module。
- **Moat**:
  - 暗黙知の formalize した独自データセット (8 社の 3 年協働で蓄積)
  - 日本製造業特有の用語 / プロセスに学習済の domain LLM
  - 既存 ERP (Mcframe、Tpics、SAP) への connector library
- **IP**: 特許出願 3 件 (時系列予測の前処理アーキテクチャ)、商標登録済。
- **Roadmap (12-24 ヶ月)**:
  - 2026 Q3: ERP connector 拡充 (5 個 → 12 個)
  - 2026 Q4: 多拠点最適化 module
  - 2027 Q1: 海外 (台湾、タイ) 展開トライアル

**Technical risk**: モデル更新運用、顧客データの境界、AI モデルベンダー依存 (現状 OpenAI + 自社 fine-tune)。

#### 17.2.4 Go-to-Market

- **Sales motion**: SLG (中堅企業向けフィールド営業 6 ヶ月 deal cycle)。
- **ICP**: 売上 100-500 億円、製造業、生産拠点 3 個以上、SCM チーム 5 名以上。
- **Channels**: 自社直販 (現在)、24 ヶ月以内に SI パートナー 3 社開拓。
- **Pricing**: モジュール別月額 30-100 万円、年間 360-1,200 万円、3 年契約 = 平均 ARPU 1,150 万円。

#### 17.2.5 Business Model & Unit Economics

| 指標 | 直近 12ヶ月 |
|---|---|
| ARR | 0.92 億円 |
| ACV (new logo) | 1,150 万円 |
| Gross Margin | 72% |
| CAC (blended) | 1,200 万円 / new logo |
| LTV (推定、3 年) | 4,000 万円 |
| LTV/CAC | 3.3x |
| CAC Payback | 14 ヶ月 |
| Magic Number | 0.85 |
| Burn Multiple | 1.4x |
| NRR | 121% |
| GRR | 100% (logo churn 0%) |

#### 17.2.6 Financial Performance

| 指標 | FY2024 actual | FY2025 actual | FY2026 forecast | FY2027 forecast |
|---|---|---|---|---|
| ARR (期末、億円) | 0.20 | 0.92 | 2.5 | 5.5 |
| Revenue (億円) | 0.07 | 0.55 | 1.7 | 4.0 |
| Gross Margin | 65% | 72% | 75% | 75% |
| OPEX (億円) | 0.55 | 1.10 | 2.20 | 3.50 |
| Net Burn (億円) | 0.50 | 0.70 | 1.10 | 0.80 |
| Headcount (期末) | 8 | 18 | 35 | 50 |

#### 17.2.7 Capital Structure & Use of Proceeds

**Pre-money cap table (2026-04 時点)**:

| 株主 | 持分 (pre) |
|---|---|
| 田中 (CEO) | 38% |
| 佐藤 (CTO) | 22% |
| Angel 3 名 | 10% |
| Seed VC (XX) | 18% |
| Option pool (現状) | 10% |
| Other | 2% |

**Post-money (Series A 後)**:

| 株主 | 持分 (post) |
|---|---|
| 田中 (CEO) | 28% |
| 佐藤 (CTO) | 16% |
| Angel + Seed | 19% |
| **Series A (含 我々)** | **18%** (うち我々 11.4%) |
| Option pool (拡大後 16%) | 16% |
| Other | 3% |

**Use of Proceeds (4.0 億円、24 ヶ月)**:
| カテゴリ | 配分 | 億円 |
|---|---|---|
| Sales (4 名 + ops) | 35% | 1.40 |
| Engineering (8 名) | 35% | 1.40 |
| Customer Success | 12% | 0.48 |
| G&A (CFO、法務、HR) | 10% | 0.40 |
| マーケティング | 5% | 0.20 |
| バッファ | 3% | 0.12 |

#### 17.2.8 Valuation

**Triangulation**:

| 手法 | 評価額 (post) | 出典 / 計算 |
|---|---|---|
| Public comp (Kinaxis 等 EV/forward Revenue 8x、日本 SaaS の private discount 30%) | 24-30 億円 | Forward 2027 Revenue 4 億 × 8 × 0.7 |
| Precedent transactions (国内 Vertical AI Series A) | 15-25 億円 | 直近 6 件の中央値 |
| VC Method (5 年後 exit 800 億、target 10x、ownership 12% target) | 20 億円 | 1.0 / target return |
| Founder ask | 22 億円 | - |
| **採用 post-money** | **22 億円** | 中央寄り、3 年 milestone 反映 |

**Sensitivity** (5 年 hold、IRR = MOIC^(1/5) − 1、希薄化なしの単純前提):

| シナリオ | 5 年 ARR | Exit 評価 | 我々 IRR | MOIC |
|---|---|---|---|---|
| Worst (ARR 12 億、12% growth at exit) | 12 億 | 80 億 | 9.9% | 1.6x |
| Base (ARR 30 億、40% growth) | 30 億 | 250 億 | 61.5% | 11x |
| Best (ARR 60 億、60% growth、IPO) | 60 億 | 600 億 | 90.4% | 25x |

#### 17.2.9 Risks & Mitigants (上位 7)

| # | リスク | 確度 | 影響 | Mitigant | Trigger to monitor |
|---|---|---|---|---|---|
| 1 | 顧客集中 (top 3 で 58%) | 中 | 高 | 24 ヶ月で top 3 を 30% 以下、月次新規 logo > 1 | top 1 顧客が 30% 超でアラート |
| 2 | 製造業 deal cycle 長期化 | 中 | 中 | 公的補助金併用、CFO で資金管理、runway 24 ヶ月 | 月次 pipeline coverage 3x 切り |
| 3 | 大手外資の中堅参入 | 中 | 高 | 暗黙知データセット deepening、3 年契約継続 | 大手の中堅 pricing 発表 |
| 4 | Key person (CEO / CTO) 離脱 | 低 | 致命 | 4 年 vesting + 1 年 cliff、KPI 連動賞与 | 経営陣月次 1on1 で signals |
| 5 | AI モデルベンダー policy 変化 | 中 | 中 | OSS 自社 fine-tune の比率を 50% に | OpenAI / Anthropic 規約変更 |
| 6 | 中堅製造業の DX 予算縮小 | 低 | 高 | 公的補助金 + ROI ベース提案 | 経産省 DX 予算半減 |
| 7 | 新規 Series B 不調 | 低 | 高 | NRR > 120% 維持、CAC payback < 18 ヶ月 | 月次 KPI で確認 |

#### 17.2.10 Sensitivity (再掲、シナリオ表)

(§17.2.8 表参照)

#### 17.2.11 Exit Strategy

**Path & Acquirer mapping**:

| タイプ | 候補 | 動機 |
|---|---|---|
| Strategic - core | Kinaxis、o9、Blue Yonder | 日本中堅セグメント獲得 |
| Strategic - adjacency | SAP、Oracle、Microsoft | ERP suite 補完 |
| Strategic - 国内 | 富士通、NEC、NTT データ | SI ビジネス補完 |
| Financial - PE | Bain Capital、Carlyle Japan | EBITDA 化後 |
| IPO | グロース市場 (5-7 年後) | ARR > 50 億、Rule of 40 > 30 |

**Target return**: 5-7 年で 10-15x MOIC、IRR 45-55% (base)。

#### 17.2.12 Recommendation & Next Steps

**Final**: ☑ INVEST WITH CONDITIONS (2.5 億円、Series A、post 22 億円、ownership 11.4%)。

**Conditions Precedent**:
1. CFO の書面契約 closed。
2. anti-dilution の broad-based weighted average 統一。
3. 独立取締役 1 名追加 (12 ヶ月以内)。
4. 月次 KPI dashboard (lead 指定 format) 提供合意。
5. 顧客 top 3 への面談 (post-closing 30 日以内)。

**Post-investment plan**:
- Board: 8 週ごと formal、月次は CEO 1on1。
- KPI: NRR、CAC payback、Burn Multiple、Magic Number、ARR、Headcount を月次 dashboard。
- Reforecast trigger: 月次 actual が forecast の ±15% 連続 3 ヶ月、または top 1 顧客 churn / 30% 超。
- Hiring: 2 名 (CFO + VP Sales 補強) を 90 日以内に紹介、3 名 (Sales、CS) を 12 ヶ月以内に紹介。
- 12 ヶ月後 review point: ARR > 2.0 億、NRR > 115%、CAC payback < 18 ヶ月、top 3 顧客集中 < 50% を thesis-validated/invalidated 判定。

#### 17.2.13 Appendix (要約のみ)

- **Commercial DD**: top 5 顧客 interview 実施、NPS 56、購入動機は「日本語 UI + 中堅価格帯」。
- **Technical DD**: SOC2 type 1 取得、tech debt は ML pipeline の test coverage 32% (24 ヶ月で 70% 計画)。
- **Financial DD**: ARR 認識基準は ASC606 準拠、deferred revenue 整合性 OK。1 件のみ revenue cut-off 議論あり、影響軽微。
- **Legal DD**: 創業者 IP assignment 100%、株主間契約 (drag-along、tag-along、preemptive) 標準。係争なし。
- **Reference checks**: 7 件 (元上司 2、元同僚 2、顧客 3)。CEO への 7/7 が「再投資 / 再雇用 yes」。

---

## 18. 補遺: 判断ロジックを使う際のチェックリスト (build-side との接続)

### 18.1 モデル → 判断 突合手順

1. モデル output から ARR 推移、NRR、CAC payback、Burn Multiple、Rule of 40 の 5 指標を抽出。
2. ステージ × 業態の閾値表 (§4) と突合し、各指標を PASS / WATCH / FAIL タグ付け。
3. WATCH / FAIL が 2 つ以上 → IC Memo の Risk セクションに昇格。
4. weighted scoring (§13.2) で総合判定。
5. kill criteria 該当の単独 FAIL があれば override で全体 FAIL。
6. valuation の三角測定 (§11) を実施し、求める IRR / MOIC が成立するか sensitivity で確認。
7. Conviction Memo (§13.4) を IC 前に書く。

### 18.2 build-side で必ず提供すべき output (judgment-side が消費)

- 月次 / 四半期 ARR 表 (3 期 actual + 24 ヶ月 forecast)
- Cohort retention 表 (logo / revenue 両方)
- CAC / LTV 計算過程 (paid + organic 分解)
- Burn / runway 計算
- 三表 (P/L、BS、CF) と整合
- Sensitivity table (NRR、CAC、growth ±20% スイング)
- Cap table (pre / post)
- Use of Proceeds (24-36 ヶ月 breakdown)
- Exit waterfall (liquidation preference 反映)

### 18.3 Term Sheet 主要項目 glossary (judgment-side で確認)

| 項目 | 定義 | 標準 / 留意点 |
|---|---|---|
| Liquidation Preference | 清算 / Exit 時の優先回収倍率 | 1x non-participating が標準。2x、participating は不利 |
| Anti-dilution | down-round 時の希薄化防止 | broad-based weighted average が標準。full ratchet は creator に苛烈 |
| Pre-emptive Right (Pro rata) | 後続ラウンドで持分維持できる権利 | major investor のみ付与が一般的 |
| ROFR / Co-sale | 株式譲渡時の優先買取 / 共同売却権 | 標準 |
| Drag-along | majority が exit を強制できる権利 | preferred majority + common majority の二重 trigger 推奨 |
| Tag-along | 大株主の譲渡に付随売却 | minor shareholder 保護 |
| Information Rights | 月次 / 四半期報告、年次監査、budget | major investor に付与 |
| Board Seat | 取締役指名権 | lead に 1、後 stage で independent 追加 |
| Protective Provisions | 重要事項に対する preferred 拒否権 | M&A、追加発行、債務、option pool 拡大等 |
| Founder Vesting | 創業者株式の vesting | 4 年 + 1 年 cliff、reverse vesting も併用 |
| Employee Option Pool | option 付与枠 | pre-money で 10-20% 設定が一般的 |
| Pay-to-Play | 後続 round に参加しない既存投資家の罰則 | down round で発動 |
| Redemption Right | 一定期間後に株式買戻請求 | 米国では使用減、日本では限定的 |
| MFN (Most-Favored Nation) | 後続 SAFE / Note の有利条件を遡及 | SAFE 多用時に注意 |
| Conversion (preferred → common) | 一般株式化トリガー | qualified IPO、majority vote 等 |

### 18.4 Stage-progression KPI gates (各 round で next round 突入条件)

| 現ステージ | 次ステージへの最低 gate (典型 SaaS) |
|---|---|
| Pre-seed → Seed | MVP 稼働、design partner 2-3、creator commitment、insight 言語化 |
| Seed → A | ARR $1M+、NRR > 100% (測定可能)、月次 logo 1+、creator-market fit 立証 |
| A → B | ARR $5M+、growth > 100% YoY、NRR > 110%、Magic Number > 0.5 |
| B → C | ARR $15-20M+、growth > 80% YoY、NRR > 115%、CAC payback < 24mo |
| C → D | ARR $50M+、growth > 50%、Rule of 40 ≥ 30、CAC payback < 18mo |
| D → IPO | ARR $200M+、growth > 30%、Rule of 40 ≥ 40、GM > 70%、SOX 準備 |

### 18.5 judgment-side が build-side に返すフィードバック

- 「NRR 130% 想定は業界 top quartile (115-120%) を超過、根拠を強化または下方修正」
- 「CAC payback 8 ヶ月は SMB 想定でも optimistic、12-15 ヶ月で再計算」
- 「Burn Multiple 0.8x は実現困難、1.2-1.5x で再計算」
- 「Exit multiple EV/Revenue 15x は public comp 中央値の 1.5x、9-10x で再計算」
- 「TAM の top-down と bottom-up が 5x 乖離、bottom-up 採用」

---

## 19. クイックリファレンス: 閾値早見表 (印刷用 1 枚)

```
【SaaS】 Series A → B
- ARR Growth:       PASS 150-300%   WATCH 100-150%   FAIL <100%
- NRR (mid):        PASS >115%      WATCH 100-115%   FAIL <100%
- GRR:              PASS >90%       WATCH 85-90%     FAIL <85%
- CAC Payback (mid): PASS <18mo     WATCH 18-24mo    FAIL >24mo
- LTV/CAC:          PASS >3x        WATCH 2-3x       FAIL <2x
- Magic Number:     PASS >0.7       WATCH 0.5-0.7    FAIL <0.5
- Burn Multiple:    PASS <2x        WATCH 2-3x       FAIL >3x
- Rule of 40:       PASS >40        WATCH 20-40      FAIL <20
- Gross Margin:     PASS >70%       WATCH 60-70%     FAIL <60%

【Marketplace】 Series A
- GMV MoM Growth:   PASS >15%       WATCH 10-15%     FAIL <10%
- GMV Retention M12 (consumer): PASS >100% WATCH 80-100% FAIL <80%
- Top 1% supply:    PASS <30%       WATCH 30-50%     FAIL >50%
- Liquidity:        PASS >60%       WATCH 40-60%     FAIL <40%

【Fintech】 Series A
- CAC Payback:      PASS <12mo      WATCH 12-24mo    FAIL >24mo
- Loss vs Vintage:  PASS 0.7-1.0x   WATCH 1.0-1.3x   FAIL >1.3x
- Capital Adequacy: PASS +200bps    WATCH +50-200bps FAIL <+50bps

【Hardware】 Series A
- GM Trajectory:    PASS +5pp/yr    WATCH flat       FAIL declining
- Inventory Turns:  PASS >6x        WATCH 3-6x       FAIL <3x
- WC/Revenue:       PASS <15%       WATCH 15-30%     FAIL >30%

【Kill Criteria (override FAIL)】
- Founder integrity 違反
- Cash runway <3 mo
- 規制違反で違法
- audit qualified opinion / material weakness
- cap table の不可解な設計
```

---

## 20. 出典まとめ

### 20.1 VC firm 公開資料

- [a16z - AI at the Intersection: Investment Thesis on AI in Bio + Health](https://a16z.com/ai-at-the-intersection-the-a16z-investment-thesis-on-ai-in-bio-health/)
- [a16z - Fintech Investments, Team, & Thesis Overview](https://a16z.com/fintech/)
- [a16z Growth - David George on Late-Stage Investing Frameworks](https://a16z.com/podcast/a16z-frameworks-late-stage-investing/)
- [a16z - GMV Retention: The Marketplace Metric Most Ignore](https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/)
- [Sequoia Pitch Deck Template (Univ of Victoria mirror)](https://www.uvic.ca/gustavson/_assets/docs/pitch-deck-template-web.pdf)
- [USV Thesis (2012)](https://www.usv.com/writing/2012/05/investment-thesis-usv/)
- [USV Thesis 2.0](http://www.usv.com/blog/usv-thesis-20)
- [USV Thesis 3.0](https://www.usv.com/writing/2018/04/usv-thesis-3-0/)
- [Bessemer - The Rule of X](https://www.bvp.com/atlas/the-rule-of-x)
- [Bessemer - Cash Conversion Score](https://www.bvp.com/atlas/cash-conversion-score)
- [Bessemer - Five Accounting Metrics for Cloud Companies](https://www.bvp.com/atlas/cloud-computing-metrics)
- [Bessemer - 10 Laws of Cloud](https://www.bvp.com/atlas/10-laws-of-cloud)
- [First Round Review](https://review.firstround.com/)
- [First Round - Frameworks](https://review.firstround.com/articles/frameworks/)

### 20.2 SaaS 指標 / フレームワーク

- [Battery Ventures - T2D3](https://www.battery.com/blog/a-mantra-for-saas-success-triple-triple-double-double-double/)
- [Scale VP - Magic Number Math](https://www.scalevp.com/insights/magic-number-math/)
- [Scale VP - SaaS Metrics: A History of the Magic Number](https://www.scalevp.com/insights/saas-metrics-a-history-of-the-magic-number/)
- [David Sacks - The Burn Multiple](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)
- [Paul Graham - Ramen Profitable](https://paulgraham.com/ramenprofitable.html)
- [Paul Graham - Why YC](https://paulgraham.com/whyyc.html)

### 20.3 ベンチマーク

- [2025 SaaS Benchmarks - High Alpha](https://www.highalpha.com/saas-benchmarks)
- [ScaleXP - 2025 SaaS Benchmarks: CAC Payback](https://www.scalexp.com/blog-saas-benchmarks-cac-payback-2025/)
- [Benchmarkit - 2025 SaaS Performance Metrics](https://www.benchmarkit.ai/2025benchmarks)
- [Bantrr - CAC Payback Benchmarks for SaaS](https://bantrr.com/business-model/saas-metrics/cac-payback-benchmarks-for-saas-companies/)
- [INITIAL - Japan Startup Finance 2025H1](https://initial.inc/articles/japan-startup-finance-2025h1)
- [INITIAL - スタートアップの平均的な成長モデル](https://initial.inc/articles/6eDb1OkqwX1T0IO3sLKdlV)
- [Strategy& Japan - スタートアップ投資バリュエーション](https://www.strategyand.pwc.com/jp/ja/publications/periodical/strategyand-foresight-23/sf23-05.html)

### 20.4 IC Memo / DD 構造

- [Visible.vc - Investment Memo Template](https://visible.vc/blog/investment-memo/)
- [VCOS - Investment Committee Memo Template](https://www.vcosai.com/blog/investment-committee-memo-template)
- [The VC Factory - Ultimate Guide to VC Investment Committee Memos](https://thevcfactory.com/investment-committee-memos/)
- [Carta - How to Write Your Investment Memo](https://carta.com/learn/private-funds/management/portfolio-management/investment-memo/)
- [Cooley GO - Sample VC Due Diligence Request List](https://www.cooleygo.com/documents/sample-vc-due-diligence-request-list/)
- [Affinity - VC Due Diligence Checklist](https://www.affinity.co/guides/due-diligence-checklist-for-venture-capital)
- [Kruze - VC Due Diligence Checklist](https://kruzeconsulting.com/blog/due-diligence-checklist/)

### 20.5 Marketplace

- [CRV - GMV Meaning: What VCs Actually Look For in Marketplaces](https://www.crv.com/content/gmv-meaning)
- [Lenny - The Most Important Marketplace Metrics](https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics)
- [Sharetribe - Marketplace Metrics](https://www.sharetribe.com/academy/measure-your-success-key-marketplace-metrics/)
- [Bowery Capital - B2B Marketplace Metrics](https://bowercap.com/blog/insights/measuring-b2b-marketplace-key-metrics-for-success)

---

*このリファレンスは startup-financial-modeling skill の dual verification (judgment-side) として運用される。build-side の数値出力に対し、本書の閾値・フレームワーク・IC Memo 構造で投資判断ロジックの妥当性を検証する。*

---

## 21. 補遺: judgment-side レッドフラグ早見表

build-side のモデル数値で以下が出たら即 IC で議論する。

| カテゴリ | レッドフラグ | 確認 |
|---|---|---|
| Growth | NRR > 140% を 4 期連続維持の forecast | 業界 top 1% 域、根拠が薄い |
| Growth | growth が階段状に綺麗すぎる (突然の jump) | Bookings vs Revenue 認識ズレ |
| CAC | CAC payback が 3 ヶ月以下 | organic と paid の混同、blended の罠 |
| Margin | GM が 3 期で +20pp 改善 | hosting / sales rep 抜き等の調整 |
| Cohort | Cohort retention が flat 100% | 統計小、新規顧客のみ、再計上の混入 |
| Burn | Burn Multiple が 0.5x 以下と forecast | working capital 効果か、recurring 効果か区別 |
| Runway | runway 24ヶ月超 forecast (調達後) | hire 計画と乖離、過小見積 |
| TAM | TAM > $100B、SOM > 50% TAM | top-down 純依存、bottom-up 不在 |
| Cap table | option pool 既消化 + 拡大なし | 採用計画と整合せず |
| Valuation | post-money / forward ARR > 30x | comp なしで passing the buck |

## 22. 補遺: 日本市場特有の judgment-side チェック

### 22.1 ガバナンス

- 取締役会の compose: 創業者 + investor のみで independent ゼロは Series B 以降で warning。
- 監査役 / 監査等委員会の設計: 上場準備に直結。
- 関連当事者取引: 創業者の他社、家族、関連法人との取引を必ず洗う。
- 印鑑 / 銀行口座: 取締役会承認なしの代表印使用、巨額決済の単独権限。

### 22.2 Cap Table / 種類株

- 日本では Series A 以降、A 種優先株式 / B 種優先株式 / ... と種類株を発行。
- 1x non-participating + みなし清算 + 取得請求権 (会社の対応資金) が標準。
- 普通株主 (創業者 + 従業員) の希薄化と liquidation preference の積層を必ず可視化。

### 22.3 Stock Option (税制適格)

- 税制適格 SO の要件: 権利行使価額 ≥ 付与時時価、保有期間 2 年以上、行使価額累計 1,200 万円 / 年以下 (2024 改定で枠拡大)。
- 信託 SO は税務取扱いに留意 (国税庁ガイドラインに整合)。
- 役員 SO の付与上限、取締役会決議、登記要件。

### 22.4 上場準備 (グロース市場)

- N-2 期 (上場 2 期前) で監査法人と契約、3 期分の監査済 FS が必要。
- 内部統制 (J-SOX) 整備、3 線防衛モデル、IT 統制。
- 主幹事証券会社の選定 (Sponsor 力、引受力、リサーチカバレッジ)。
- 開示書類 (Iの部、IIの部) 準備、約 1 年。
- 上場目論見書の reasonable basis 開示 (forecast 根拠)。

### 22.5 助成金 / 公的資金併用

- NEDO、経産省 J-Startup、地方創生補助金等の併用は dilution 抑制に有効。
- 補助金の費用認識タイミング (検収 / 支払 / 確定) と P/L 影響を区別。
- 公的調達 (官公庁) の収益認識 (ASC606 / IFRS 15 vs JGAAP) 要確認。

### 22.6 J-Curve と日本市場特有の収益認識

- 月額 SaaS の前受収益の RPO (Remaining Performance Obligation) 開示。
- 期末偏重売上 (3 月、12 月) の deferred 構造、四半期予算の振れ。
- Revenue リーク (代理店経由のリベート、現物 inventive 等) の控除。

### 22.7 為替と海外売上

- 円安期は連結 revenue の見栄え良化、円高期は逆。
- 外貨 ARR は constant currency と reported currency 双方で。
- 海外子会社の natural hedge 状況、cash 配当 / loan 設計。

---

