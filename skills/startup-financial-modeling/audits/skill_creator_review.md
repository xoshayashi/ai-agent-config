# Skill Creator Framework Review

- **Reviewer**: skill-creator framework compliance audit (Claude Opus 4.7)
- **対象**: `skills/startup-financial-modeling/` 全配下
- **基準**: `~/.claude/plugins/cache/anthropic-agent-skills/document-skills/12ab35c2eb56/skills/skill-creator/SKILL.md`
- **作業日**: 2026-05-01
- **判定 mode**: 監査のみ (本 review では修正は実施しない)

---

## Executive Summary

**Overall assessment**: 24 reference の corpus 自体は IB / VC / PE 実務水準で強力 (38,041 行、reference depth 9/10) だが、**skill としての invocation 機構 (SKILL.md) が完全に欠落** しており、現状では Claude の skill router から **一切呼び出されない**。`audits/final_status.md` の「Phase 6 着手 OK」宣言は、Phase 4-5 の reference 整合性の終了条件のみを満たした判定であり、**skill-creator framework の Layer 1 (metadata) 要件を満たしていない**。Phase 6 (scripts/) を着手する前に、まず SKILL.md を作成して corpus を **invocable** にすることが最優先タスク。

### Top 3 Critical Gaps (P0)
1. **SKILL.md 不在** — 必須の YAML frontmatter (name / description) を持つ entrypoint file が存在しない。skill-creator framework の三層 progressive disclosure のうち最上層 (Metadata, always-loaded) が欠落しているため、Claude は本 corpus を skill として認識できない。
2. **evals/evals.json 不在** — triggering の精度検証手段が無く、description 最適化 (skill-creator §"Description Optimization") 着手不可。
3. **Skill 内部の dispatch logic が散在** — `_master_decision_tree.md` (499 行) が事実上の orchestrator として機能しているが、SKILL.md からの「最初に読むべき reference」明示と意図 → reference のルーティング表が存在しない。ユーザーの曖昧な質問 (例: "Series A model 作って") に対し、Claude が 24 file からどれを読み始めるかが決まらない。

### Top 3 Strengths
1. **Reference depth 9/10** — IB Color 規格、3 表突合、SAFE/J-KISS state machine、WACC≈g auto-fallback、業態 × Stage routing matrix まで踏み込んだ実務水準。numeric example の再計算も 7/7 一致。
2. **SSoT 設計が機能している** — `_terminology.md` を hub に IB Color / J-KISS 2.0 日付 / SaaS metric 閾値が canonical 化され、cross-file consistency が運用可能な状態。
3. **Self-review protocol が存在** — `_self_review_protocol.md` で 6 軸監査 + Wave 設計が明文化され、案件レベルでも品質保証が回せる構造。

### Recommended Next Actions (順番固定)
1. **SKILL.md ドラフト作成** (本 review §1.4 のテンプレートを使用、所要 1-2 時間)
2. **evals/evals.json 3 case 整備** (本 review §6 のテンプレート、所要 30 分)
3. **trigger eval 20 query** で skill-creator の `run_loop.py` で description 最適化 (1 day)
4. **Phase 6 (scripts/build_model.py) 着手** は SKILL.md がランドしてから

---

## 1. SKILL.md Assessment

### 1.1 結論: ❌ Critical — SKILL.md 不在

```
$ ls skills/startup-financial-modeling/SKILL.md
ls: No such file or directory
```

`audits/final_status.md` は「Phase 6 着手 OK」を宣言しているが、これは reference 群の内部整合性 (Critical = 0 / High ≤ 3 / SSoT 不整合 = 0) の達成宣言であり、**skill-creator framework の必須前提を満たしているという判定ではない**。skill-creator SKILL.md (`#anatomy-of-a-skill`) より:

> ```
> skill-name/
> ├── SKILL.md (required)
> │   ├── YAML frontmatter (name, description required)
> │   └── Markdown instructions
> └── Bundled Resources (optional)
> ```

SKILL.md が無い以上、Claude の skill router は本 skill を `available_skills` list に load できず、24 reference の存在自体が見えない。**Phase 6 (scripts/) を仮に組んだとしても、ユーザーから invocation が起きない**。これが本 review の最大の発見。

### 1.2 設計示唆 — 4 つの underscore-prefixed reference が de facto SKILL.md substrate

既存 reference のうち、以下 4 file は YAML frontmatter (name / description / type / priority) を持ち、skill 内部の構造を司っている:

| File | 役割 | 行数 |
|---|---|---|
| `_terminology.md` | SSoT (用語・色・閾値の正本) | 191 |
| `_master_decision_tree.md` | 意図 → reference routing | 499 |
| `_stress_framework.md` | Stress test / cross-domain logic | 861 |
| `_self_review_protocol.md` | 品質保証メタプロトコル | 132 |

これら 4 file は **SKILL.md の素材として既に揃っている**。SKILL.md 本体は corpus 内容を再記述する textbook であってはならず、**この 4 file への dispatcher** として書くべき。残 20 reference (00-16) は per-section anchor で参照する。

### 1.3 推奨 description (triggering 用 ドラフト)

skill-creator §"Write the SKILL.md" の "pushy" 指針を踏まえ、undertrigger を防ぐため少し強めに書く。重要キーワード (startup / 財務モデル / SaaS / valuation / cap table / IC memo / IB / xlsx) を明示:

```yaml
name: startup-financial-modeling
description: >
  Build IB-quality 17-sheet xlsx financial models, IC memos, cap tables, and
  valuation decks for startups (Pre-Seed → Pre-IPO). Covers SaaS / Marketplace /
  D2C / Fintech / Hardware / Bio / AI Foundation, US (Delaware C-corp) and Japan
  (株式会社 / J-KISS / 政策金融公庫). Use this skill whenever the user mentions
  building a financial model, three-statement model, cap table, dilution waterfall,
  SAFE / J-KISS conversion, founder secondary, valuation (DCF / WACC / Comps /
  Football field), IC memo, sensitivity analysis, Rule of 40, NRR, LTV/CAC,
  Burn Multiple, Runway, IPO readiness, debt covenant, or any structured xlsx
  output for fundraising or investment decisions — even if the user does not
  use the word "model" explicitly. Trigger especially when a startup's ARR /
  MRR / Stage / business model is given and the user wants quantitative output,
  not just analysis prose. Do NOT trigger for: pitch deck design (use
  document-skills:pptx instead unless the user explicitly asks for IB-style
  charts wired to the xlsx model), market analysis without numerical model,
  or general accounting questions.
```

文字数: ~140 words。skill-creator framework の "100 words ideal" よりやや長いが、業態 11 + stage 6 + geography 2 の cross-product を扱う複雑な skill のため triggering 精度を優先。

### 1.4 SKILL.md Body Skeleton (推奨)

300 行以下を目標に下記構造で書き起こす。corpus の中身を再記述せず、dispatch に徹する:

```markdown
---
name: startup-financial-modeling
description: <§1.3 のテキスト>
---

# Startup Financial Modeling

IB 品質の 17 sheet xlsx 財務モデル + IC memo を生成する skill。
Pre-Seed → Pre-IPO の各 stage、11 業態、US/Japan に対応。

## このスキルが解決する問題

- Founder: 「Series A 評価額の根拠を 17 sheet で正当化したい」
- VC/PE: 「IC memo + 三表突合付き sensitivity を半日で作りたい」
- CFO: 「J-KISS 転換後の希薄化を cap table で trace したい」
- アナリスト: 「業態 × stage の正しい metric を引いてモデリングしたい」

(計算・条項・数値は references/ に分散。本 SKILL.md は orchestration のみ)

## 基本ワークフロー (高位 5 steps)

1. **Mode 選択**: Quick / Standard / Comprehensive を `references/15_input_schema.md §1.2` の質問で確定
2. **Routing**: `references/_master_decision_tree.md §0.1` の 5 entry point から該当 § を read
3. **Generate**: 17 sheet xlsx + IC memo を build (Phase 6 で `scripts/build_model.py` がここを担当、現状は手動構成)
4. **Self-review**: `references/_self_review_protocol.md §8` の必須 5 check を実行
5. **Iterate**: SanityChecks シート全 row が ✅ になるまで修正

## Reference dispatch table (intent → which reference to read first)

| ユーザー発話の例 | 第 1 reference | 補完 reference |
|---|---|---|
| "Series A 評価額が知りたい" | `_master_decision_tree.md §B` | `05_valuation_wacc.md §1.6, §21` |
| "SAFE 転換シミュレーションを" | `04a_convertible_and_terms.md §2, §19` | `04b_cap_table_mechanics.md §12` |
| "J-KISS post-money cap" | `07_japan_specifics.md §3.1` | `04a §3, _terminology §5` |
| "SaaS metric の正しい定義" | `_terminology.md §6` | `02_saas_metrics.md` |
| "IC memo 雛形" | `08_investment_thesis.md §17` | `_master_decision_tree §C` |
| "IPO readiness check" | `14_ipo_readiness.md` | `01a_modeling_standards.md §3.2` |
| "業態 × stage で何を読むか" | `_master_decision_tree §E` | `15_input_schema §11.2` |
| "venture debt vs equity" | `_master_decision_tree §D` | `11_debt_financing.md §1.1, §18` |
| "WACC が g 以下になる" | `05_valuation_wacc.md §21.1` | `_terminology §6` |
| "下方 / wind-down シナリオ" | `10_modeling_craft.md §19` | `_stress_framework.md` |

## Critical SSoT 規約 (毎回確認)

- 用語・色・閾値: `references/_terminology.md` を canonical
- IB Color: Hard input = `#0000FF`、Cross-sheet link = `#008000`、External = `#FF0000`
- Sheet naming: `00_Cover ... 16_IC_Memo` (`_terminology §3`)
- J-KISS 2.0 = 2022-04 (`_terminology §5`)
- 出力前に `_self_review_protocol §8` の 5 check 必須

## 17 Sheet Layout (default)

`00_Cover / 01_Assumptions / 02_Drivers / 03_Revenue / 04_OpEx /
05_IS / 06_BS / 07_CFS / 08_WC / 09_Debt / 10_CapTable /
11_DCF / 12_Comps / 13_Sensitivity / 14_KPI_Dashboard /
15_SanityChecks / 16_IC_Memo`

(出典: `_terminology §3`)

## Trade-off と limitations

- Build phase 1 完成業態 = SaaS / Marketplace / Consumer Subscription /
  Hardware / Fintech のみ (`15_input_schema §11.2`)。残 6 業態 (Bio / Media /
  B2B Services / Manufacturing / Real Estate / AI Foundation) は warn 出力 +
  手動 schema 補完が必要 (`audits/accepted_high.md §A`)。
- 数値 example の re-verification は 7/55 sample 完了。残 sample は build phase 1
  の `tests/numeric_consistency_test.py` で拡大予定 (`accepted_high.md §D`)。

## 関連 skill との境界

- `document-skills:xlsx` — 一般 xlsx 操作。本 skill は財務モデル特化、xlsx は
  spreadsheet 一般操作。財務モデル生成では本 skill 優先、xlsx 一般は xlsx skill。
- `document-skills:pptx` — pitch deck / IC presentation 生成。本 skill は xlsx
  + IC memo (.md / .docx) を出力、pitch deck は pptx skill との合わせ技。
- `document-skills:docx` — IC memo を Word で出したい場合は docx skill 連携。
```

行数目算: ~250 行。skill-creator の "<500 lines ideal" を満たす。

### 1.5 SKILL.md 評価点 (作成後の予想スコア)

| 軸 | スコア (作成後 想定) | 備考 |
|---|---|---|
| YAML frontmatter | 10/10 | name + description 両方 |
| 本文 < 500 行 | 9/10 | 250 行で済む |
| Progressive disclosure | 8/10 | dispatch table が機能 |
| Pushy description | 7/10 | "even if the user does not use the word 'model'" がある |
| Trigger keyword 網羅 | 9/10 | startup / SaaS / cap table / valuation / IC memo / WACC / J-KISS / SAFE / NRR / Rule of 40 |

---

## 2. Description / Triggering Quality

### 2.1 現状評価: ❌ 不在

description が無いため triggering の議論ができない。skill-creator §"How skill triggering works" より:

> Skills appear in Claude's `available_skills` list with their name + description, and Claude decides whether to consult a skill based on that description.

description = "" の skill は **listed されない**。

### 2.2 推奨 description のキーワード分析

§1.3 の draft description の主要 keyword を skill-creator の "pushy" 指針と照合:

| キーワード | カバー | 備考 |
|---|---|---|
| 主要動詞 | "build", "model", "value", "size" | ✅ |
| 業態 | SaaS / Marketplace / D2C / Fintech / Hardware / Bio / AI | ✅ 11 のうち 7 列挙 |
| 出力形式 | xlsx / IC memo / cap table / valuation deck | ✅ |
| Stage | Pre-Seed → Pre-IPO | ✅ |
| Geo | US / Japan / J-KISS / 政策金融公庫 | ✅ |
| 専門 metric | SAFE / DCF / WACC / Football field / Rule of 40 / NRR / LTV/CAC / Burn Multiple | ✅ |
| 関連用語 (近接) | sensitivity / IPO readiness / debt covenant | ✅ |
| 否定条件 | pitch deck "unless ..." / market analysis without model | ✅ near-miss を排除 |

### 2.3 Triggering 検証用 20 query 提案

skill-creator §"Step 1: Generate trigger eval queries" に従い、現実的・具体的・abbreviation/typo 含む:

#### Should-trigger (10 queries)

```json
[
  { "query": "うちの SaaS、ARR がやっと ¥240M に届いた。Series A の調達額と評価額のレンジを 17 sheet モデルに落とし込みたい。MRR の月次成長 8%、NRR は 115%。希薄化込みでファウンダーの持分が何 % 残るかも cap table で見たい", "should_trigger": true },
  { "query": "J-KISS 2.0 で ¥150M 調達済み (cap ¥1.2B、disc 20%)、来年 Series A で pre ¥3B 想定。post-money cap iterative で converted shares 計算して、希薄化 waterfall を Excel で出して", "should_trigger": true },
  { "query": "VC のインベストメントメモを書きたい。投資先は B2B SaaS、ARR $5M、Rule of 40 = 38、Burn Multiple = 1.8。kill criteria 通ってるか、Football field で valuation 妥当性も併せて", "should_trigger": true },
  { "query": "boss から「Q4 SaaS forecast、3 年分」と振られた。データは Salesforce の export (cohort 別 ARR) と SaaSOptics 月次。三表 (PL / BS / CF) 突合せ + sensitivity も付けてって", "should_trigger": true },
  { "query": "Marketplace スタートアップの GMV $100M、take rate 12%、両側 retention は cohort 別。LTV/CAC は買い手 / 売り手 別に計算したい。IC memo と xlsx 一式を", "should_trigger": true },
  { "query": "うちのスタートアップ、来期から連結に乗る (子会社 持分 70%)。NCI と CTA の処理込みの三表モデルと、親会社 single の wind-down も並走で", "should_trigger": true },
  { "query": "DCF で WACC 計算したら g (terminal growth) より低くなった。Mid-stage SaaS なんだけど、これって Exit Multiple に切り替えるべき? boundary auto-fallback の判定基準ある?", "should_trigger": true },
  { "query": "founder secondary を Series B で 10% やりたい。tax 込みの net cash で投資家側にどう見えるか、cap table と税効果両方で trace したい。日本法人", "should_trigger": true },
  { "query": "venture debt の facility (¥500M, 4-year, JPY+1.8%) を組みたいんだけど、equity との trade-off と cross-default risk を IC memo に入れたい", "should_trigger": true },
  { "query": "fintech (lending) の起業準備中。CAC payback と loan loss provision のモデル合わせて 3 年 forecast 作りたい。日本 (貸金業登録前提)", "should_trigger": true }
]
```

#### Should-NOT-trigger (10 near-miss queries)

```json
[
  { "query": "競合 SaaS 上場企業 (例: Sansan) の直近決算を読んで、business model の解説してほしい。モデル作る必要はない、文章で良い", "should_trigger": false },
  { "query": "個人事業主 (フリーランス) の家計簿を Excel でまとめたい。月次の収支と確定申告用の経費仕訳", "should_trigger": false },
  { "query": "上場企業 (Snowflake) の 10-K から ARR と NRR を抽出して csv にまとめてほしい。財務モデル化はしない", "should_trigger": false },
  { "query": "Series A の term sheet 雛形が欲しい。NVCA model documents の文面そのままで、数値計算は不要", "should_trigger": false },
  { "query": "VC 向け pitch deck (10 slide) を作りたい。team / problem / solution / market / traction / model business / GTM / financials (1 slide だけ summary) / ask / appendix", "should_trigger": false },
  { "query": "TAM/SAM/SOM の市場規模算定だけ知りたい。Bottom-up で。財務モデルは別途作るので、market sizing 単体で良い", "should_trigger": false },
  { "query": "M&A の deal book / virtual data room を整理したい。財務モデル本体は target 側が持ってる。VDR の folder structure と DD checklist が欲しい", "should_trigger": false },
  { "query": "Cap table を入力する SaaS (Carta / Pulley) の比較してほしい。どっちが Founder 向きか、料金と機能で", "should_trigger": false },
  { "query": "会社設立の手続き (株式会社、資本金 ¥1M) を教えて。定款 / 公証役場 / 法務局 / 銀行口座開設の順番", "should_trigger": false },
  { "query": "Series A の調達がうまくいかない。VC への cold reach の文面を 5 つ書いて。LinkedIn DM 用、200 字以内", "should_trigger": false }
]
```

### 2.4 Near-miss の取り扱い (advisor 反映)

advisor からの指摘: `00_design_guidelines.md §0` に「IB 品質の財務モデル (xlsx) と **pitchbook (pptx)** を生成」と書かれているため「VC ピッチデッキ」を should-NOT-trigger にすると corpus と矛盾する。本 review §2.3 では:

- "VC 向け pitch deck (10 slide) を作りたい" を **should-NOT-trigger** に分類 (= pitch deck メイン作業は `document-skills:pptx`)
- ただし SKILL.md description の "Do NOT trigger for: pitch deck design (use `document-skills:pptx` instead **unless** the user explicitly asks for IB-style charts wired to the xlsx model)" で例外条件を明示

これにより corpus との整合性を保ちつつ、ピッチデッキ単体は競合 skill に譲る境界を確保。

---

## 3. Progressive Disclosure Design

### 3.1 三層構造の現状

| Layer | skill-creator 想定 | 現状 | 判定 |
|---|---|---|---|
| 1. Metadata | name + description (always loaded, ~100 words) | ❌ 不在 | Critical |
| 2. SKILL.md body | 本文 < 500 行 (skill triggers 時に load) | ❌ 不在 | Critical |
| 3. Bundled resources | references/ (as needed) | ✅ 24 file 38,041 行 | OK |

Layer 1-2 が無いまま Layer 3 だけが分厚い、いびつな構造。

### 3.2 推奨 dispatch logic

`_master_decision_tree.md §0.1` の 5 entry point は既に良い orchestrator だが、**SKILL.md の dispatch table に "1 sentence で intent を識別 → 最初に読む reference の section anchor まで指定"** する。本 review §1.4 の dispatch table を SKILL.md に置く形が標準。

#### Reference の自己完結性チェック

skill-creator §"Domain organization" より:

> Claude reads only the relevant reference file.

この観点で 24 file の独立性を確認:

| 軸 | 評価 | 詳細 |
|---|---|---|
| 1 file ≤ 1 domain | ✅ | `02_saas_metrics`, `03_business_models`, `07_japan_specifics` 等が綺麗に分離 |
| Cross-file 依存 | ⚠️ | `_terminology` 経由は OK だが、`04a` ↔ `04b` は state machine と cap table で密結合 (ただし design 上やむを得ない) |
| 独立 readable | ⚠️ | 各 file の冒頭に「本書の前提 / 上位 SSoT への back-reference」が散発的。`_stress_framework`, `_terminology`, `_master_decision_tree`, `_self_review_protocol`, `15_input_schema` には明示があるが、`00`, `01a/b`, `02-14` は無し |

### 3.3 大型 reference の section anchor 戦略 (advisor 反映)

`15_input_schema.md` (2,603 行 / 約 100KB) のような大型 file は **全文 load を避ける**。SKILL.md の dispatch table で "§11.2" や "§13.1 Example 1" まで指定する。これで Claude は necessary section だけ読める。

各 reference 冒頭に TOC があるか確認:

| File | 行数 | TOC 有無 |
|---|---|---|
| `00_design_guidelines.md` | 2,254 | ✅ (line 14-33) |
| `04a_convertible_and_terms.md` | 2,401 | ⚠️ (要 sampling) |
| `04b_cap_table_mechanics.md` | 2,384 | ⚠️ (要 sampling) |
| `05_valuation_wacc.md` | 2,440 | ⚠️ (要 sampling) |
| `11_debt_financing.md` | 2,602 | ⚠️ (要 sampling) |
| `15_input_schema.md` | 2,603 | ✅ (line 13-28) |

skill-creator §"Progressive Disclosure" より:

> For large reference files (>300 lines), include a table of contents

本 corpus は **全 24 file が >300 行** (最小 `_terminology` で 191 行、最大 `15_input_schema` で 2,603 行)。TOC 整備状況の網羅 audit は本 review 範囲外だが、Phase 6 着手前に **少なくとも >1,000 行 file (15 file)** で TOC 確認 + 補完を推奨。

---

## 4. Bundled Resources

### 4.1 references/ (24 file 38,041 行)

| 観点 | 評価 | 詳細 |
|---|---|---|
| 役割明確性 | ✅ 9/10 | underscore-prefix が SSoT 系、数字 prefix が domain 系で識別容易 |
| 命名一貫性 | ⚠️ 7/10 | `00`, `01a/b`, `02-16` の 2 桁 prefix は一貫。ただし `13a/b` は consolidation の `core` / `treasury_carveout` で意味的細分。`04a/b` は `convertible_and_terms` / `cap_table_mechanics` で並列分離 — Phase 6 で `15a/15b` 等を作る場合の規約を SKILL.md に明記推奨 |
| Frontmatter 一貫性 | ❌ 4/10 | 4/24 file (`_terminology`, `_master_decision_tree`, `_stress_framework`, `_self_review_protocol`) のみ frontmatter あり。残 20 file は冒頭が `# Title` 直書き。SKILL.md からの dispatch には影響しないため P2 だが、**reference 内部の "skill 内 SSoT 階層" 認識のために統一推奨** |
| 大型 file 比率 | ⚠️ | 2,000 行超え 6 file (`04a`, `04b`, `05`, `11`, `15`, `00`)、3,000-3,500 行が無いため最大級は 2,603 行 |

### 4.2 scripts/ (空)

| 観点 | 評価 |
|---|---|
| 不在の妥当性 | ✅ Phase 6 未着手として正当。`audits/final_status.md §5` で「SaaS Series A 向け `scripts/build_model.py` の scaffold 着手可能」と明記 |
| 影響 | SKILL.md ができるまで scripts 着手は無意味 (skill 自体が trigger しない) |

### 4.3 assets/ (空)

| 観点 | 評価 |
|---|---|
| 不在の影響 | ⚠️ 本 skill は 17 sheet の xlsx template を生成するため、`assets/templates/input_template.xlsx` (Hard input cell only) と `assets/templates/output_template.xlsx` (色 / 罫線 / 17 sheet 骨格付き) が build phase で必要。`15_input_schema §1.3` に Excel template 経路の言及あり |
| 推奨 | Phase 6.0 で `xlsxwriter` で programmatic 生成する設計の場合 assets 不要、`openpyxl` で template を起点に生成する設計の場合 assets が必須。設計判断は SKILL.md の "Build phase strategy" section で declare |

### 4.4 evals/ (空)

| 観点 | 評価 |
|---|---|
| 不在の影響 | ❌ skill-creator §"Test Cases" より「Skills with objectively verifiable outputs ... benefit from test cases」。本 skill は xlsx の数値整合性が verifiable なので test case が **特に有効** |
| 影響度 | High — triggering 検証 / 出力品質検証ともに測定不能 |
| 推奨 | §6 で 3 case のテンプレート提案 |

### 4.5 audits/ (15 file)

skill-creator framework には audits/ という規定 directory 名はないが、本 skill では **品質保証ログ** として機能している:

| File | 役割 |
|---|---|
| `audit_A〜F_*.md` (6 file) | Phase 2 の 6 軸監査 raw 出力 |
| `round2_*.md` (4 file) | Phase 4 の Wave 別 fix log |
| `round3_high_fixes.md` | Round 3 の High 17 件 inline 解消 |
| `final_review.md` | Phase 5 final 監査 |
| `accepted_high.md` | Phase 6 backlog 56 件 rationale |
| `final_status.md` | 終了宣言 |

**評価**: 内部品質保証として優秀だが、**ユーザーが skill を invoke する経路には関係しない**。Phase 6 で `tests/` を作る際は `audits/` とは別 directory にすること。

---

## 5. Writing Style & Anatomy

### 5.1 Principle of Lack of Surprise (✅ 7/10)

`startup-financial-modeling` という skill 名から想定される範囲 (財務モデル / cap table / valuation / IC memo / 業態別 metric / 日本特有 J-KISS / debt) はすべて corpus 内に存在。**意外性は無い** (= 良い意味で skill 名通りの中身)。

ただし `13a_consolidation_core.md` (連結会計) と `14_ipo_readiness.md` (IPO readiness) は startup-modeling の枠を **やや超える** 可能性あり (= series D 以降専用)。skill 名から想定される「early-stage 財務モデル」と整合させるため、SKILL.md description で「Pre-Seed → Pre-IPO」と stage range を明示することで surprise を避ける (§1.3 で対応済)。

### 5.2 Writing Style — Imperative の使用 (✅ 8/10)

`_terminology.md` / `_master_decision_tree.md` / `_self_review_protocol.md` の 3 file は imperative + theory of mind 両立で書かれている。例 (`_self_review_protocol §1.1`):

> 「完成 ≠ 終了」: xlsx / IC memo / cap table を出力しただけでは「完成」とみなさない

理由付き imperative で skill-creator §"Writing Style" に整合。

### 5.3 ALWAYS / NEVER の濫用チェック

`_terminology.md` 全文を grep で検査した範囲:
- "必ず" (= ALWAYS): 4 箇所 — いずれも rationale 併記済 ✅
- "してはいけない" / "use ... only" (= NEVER): 3 箇所 — rationale 併記済 ✅

ただし 2,000 行超え reference (`05`, `11` 等) は本 review で全文確認していない。Phase 6 着手前に sampling audit 推奨。

### 5.4 Examples Pattern

skill-creator §"Examples pattern" より:

> ```markdown
> ## Commit message format
> **Example 1:**
> Input: Added user authentication with JWT tokens
> Output: feat(auth): implement JWT-based authentication
> ```

Reference 群は数値例 + worked example が豊富 (`04b §10.3.5` Founder Net Cash 表、`04b §12.4` Anti-dilution 4-iteration trace、`05 §22` Stage Discount default 表 等)。**Example pattern の質は高い** (final_review.md §6 で 7/7 numeric verification 一致)。

### 5.5 Domain organization (✅ 9/10)

skill-creator §"Domain organization" の cloud-deploy 例 (aws / gcp / azure) のように、本 skill は:

- **業態軸**: `02 (SaaS)`, `03 (general)`, `07 (Japan)`
- **stage 軸**: `_master_decision_tree §A〜E` でルーティング
- **Function 軸**: `04a/b (cap table)`, `05 (valuation)`, `06 (3 statement)`, `08 (thesis)`, `11 (debt)`

domain × function × stage の 3 軸 routing が `_master_decision_tree` で集約され、skill-creator の "domain organization" 推奨形を上回る複雑さを綺麗に整理している。

---

## 6. Test Cases Recommendation

### 6.1 推奨 3 case

skill-creator §"Test Cases" より「2-3 realistic test prompts — the kind of thing a real user would actually say」。本 skill の verifiable output (xlsx 数値整合 / IC memo 構造 / cap table %) を活かし、各 case で objectively check できる assertion を組める設計に:

#### Case 1: SaaS Series A 3 年モデル (greenfield)

- **Persona**: founder 自己診断 / VC IM 用
- **Input**: SaaS, ARR ¥240M ($1.6M), MRR growth 8% / mo, NRR 115%, GM 75%, S&M ratio 50%, 想定 stage = Series A
- **Expected output**: 17 sheet xlsx (`00_Cover ... 16_IC_Memo`) + IC memo (.md or .docx)
- **検証可能 assertion**:
  - `15_SanityChecks` 全 row が ✅ (BS L+E / CF ending = BS cash / NI→RE tie / Σ% = 100%)
  - 17 sheet 全て存在 (`_terminology §3` の sheet name と一致)
  - Hard input cell 色 = `#0000FF` (`_terminology §1`)
  - DCF (`11_DCF`) と Comps (`12_Comps`) の valuation range が overlap > 50%
  - IC memo に 5 必須 section (Investment Thesis / Market / Business / Financials / Risk) 存在

#### Case 2: J-KISS 2.0 → Series A 転換 (cap table 中心)

- **Persona**: CFO / 創業者 / VC
- **Input**: J-KISS 2.0 ¥150M (cap ¥1.2B post-money / discount 20% / 2024-04 発行), Series A pre ¥3B / lead ¥600M, ESOP refresh +10% post-money
- **Expected output**: 10_CapTable シート (pre / post / fully diluted) + 希薄化 waterfall + Founder net % trace
- **検証可能 assertion**:
  - post-money cap iterative 解 (`04a §3.4`, `_terminology §5`) の 4-step iteration が trace 出力されている
  - Founder absolute % 計算が closed-form と一致 (`04b §12.4` 方式)
  - Σ% = 100.00% (rounding tolerance ±0.01%)
  - SAFE Discount は `_terminology §4` の `Discount = 0.20` 表記 (Discount Factor = 0.80 を mix していない)

#### Case 3: 既存 xlsx の sanity 監査 (audit mode)

- **Persona**: VC associate / IB analyst が target の model を受領、6 軸 audit
- **Input**: ユーザーが既存の SaaS 3 年 model xlsx を提示、「sanity audit を 30 分で」
- **Expected output**: `audit_report.md` (B Calculation + A Consistency 中心)、修正提案リスト、`_self_review_protocol §2` の 6 軸スコア
- **検証可能 assertion**:
  - 6 軸 (consistency / calculation / logic / grounding / strategy / implementation) のうち最低 4 軸でコメント生成
  - 数値再計算 sampling が最低 5 cell で実施され、誤りがあれば location 明示
  - `_terminology` SSoT 違反を grep 検出 (例: hard input が `#0000FF` 以外、sheet name 旧仕様)
  - Critical / High / Medium / Low の 4 段階で issue を分類

### 6.2 evals/evals.json テンプレート

skill-creator §"Test Cases" の schema に従い:

```json
{
  "skill_name": "startup-financial-modeling",
  "evals": [
    {
      "id": 1,
      "name": "saas-series-a-3yr-greenfield",
      "prompt": "B2B SaaS スタートアップで ARR ¥240M ($1.6M)、MRR 月次成長 8%、NRR 115%、GM 75%、S&M 比率 50%、Series A 想定。3 年 forecast の 17 sheet xlsx と IC memo を作って。日本法人、JPY ベース。",
      "expected_output": "17 sheet xlsx (`_terminology §3` 順) + IC memo (.md)。`15_SanityChecks` 全 row ✅、Hard input = `#0000FF`、DCF と Comps の valuation overlap > 50%、IC memo に 5 必須 section",
      "files": [],
      "assertions": [
        { "text": "Output xlsx contains all 17 sheets named per `_terminology §3`", "type": "structural" },
        { "text": "All cells in `15_SanityChecks` evaluate to ✅", "type": "numeric" },
        { "text": "Hard input cells are colored `#0000FF`", "type": "visual" },
        { "text": "DCF valuation range and Comps range overlap > 50%", "type": "numeric" },
        { "text": "IC memo has Investment Thesis / Market / Business / Financials / Risk sections", "type": "structural" }
      ]
    },
    {
      "id": 2,
      "name": "jkiss-to-series-a-conversion",
      "prompt": "J-KISS 2.0 で ¥150M 調達済み (post-money cap ¥1.2B、discount 20%、2024-04 発行)。来年 Series A、pre ¥3B / lead ¥600M、ESOP refresh +10% post-money。希薄化 waterfall と cap table を組んで、Founder の net % を trace。",
      "expected_output": "10_CapTable シート (pre / post / FDSO) + 希薄化 waterfall + Founder net % trace。post-money cap iterative の 4-step iteration 付き。",
      "files": [],
      "assertions": [
        { "text": "Iterative solver shows 4-step trace per `04a §3.4`", "type": "structural" },
        { "text": "Founder absolute % matches closed-form per `04b §12.4`", "type": "numeric" },
        { "text": "Σ% across all shareholders = 100.00 ± 0.01%", "type": "numeric" },
        { "text": "SAFE Discount expressed as `0.20` (not mixed with `0.80` Discount Factor)", "type": "consistency" }
      ]
    },
    {
      "id": 3,
      "name": "existing-xlsx-sanity-audit",
      "prompt": "投資先 (SaaS、Series B) からモデル xlsx を受領した。30 分で sanity audit を回したい。`_self_review_protocol` の 6 軸でレビューして、Critical / High / Medium で issue 分類して。",
      "expected_output": "audit_report.md (6 軸スコア + issue list)。Numerical sampling 最低 5 cell、`_terminology` SSoT 違反を grep 検出。",
      "files": ["sample_saas_model.xlsx"],
      "assertions": [
        { "text": "Audit report covers at least 4 of the 6 axes (A-F)", "type": "structural" },
        { "text": "Numeric re-verification done on >=5 cells with location/value cited", "type": "numeric" },
        { "text": "SSoT violations (e.g. hard input != #0000FF) flagged", "type": "consistency" },
        { "text": "Issues classified into Critical / High / Medium / Low with severity rationale", "type": "structural" }
      ]
    }
  ]
}
```

### 6.3 Test case の運用方針

skill-creator §"Running and evaluating test cases" の workflow:

1. with-skill / without-skill (baseline) を **同一 turn で並列 spawn**
2. timing.json で `total_tokens` / `duration_ms` を記録
3. grader subagent で `grading.json` を生成
4. `aggregate_benchmark` で `benchmark.json` / `benchmark.md`
5. `eval-viewer/generate_review.py` で HTML viewer 起動

Phase 6 着手 **直前** に 3 case 全てを 1 iteration 回すことで、**SKILL.md の triggering と reference の dispatch logic が機能しているか** を検証。

---

## 7. Improvement Priority Ranking (Top 10)

| Rank | P | Issue | Recommendation | Estimated effort |
|---|---|---|---|---|
| 1 | **P0** | SKILL.md 不在 — skill が router に listed されない | §1.4 のテンプレートで `skills/startup-financial-modeling/SKILL.md` を新規作成。description は §1.3 の 140 word draft を採用 | **1-2h** |
| 2 | **P0** | evals/evals.json 不在 | §6.2 の 3 case テンプレートで作成、prompt 部分のみ user に確認後コミット | **30 min** |
| 3 | **P0** | Trigger eval 検証未実施 | §2.3 の 20 query を `eval_review.html` で user 確認 → `run_loop.py --max-iterations 5` で description 最適化 | **1 day (+ background)** |
| 4 | **P1** | Reference 20 file の frontmatter 不在 | 残 20 file (00, 01a/b, 02-16) に `--- name / type / priority ---` を追加 (内容は変えず) | **2h** |
| 5 | **P1** | 大型 reference (>1,000 行) の TOC 整備未確認 | 15 file の冒頭に TOC があるか sampling audit、無い file は補完 | **3-4h** |
| 6 | **P1** | assets/ Excel template 不在 | `xlsxwriter` 純 programmatic 路線か `openpyxl` template 路線かを SKILL.md の "Build phase strategy" で declare、必要なら `assets/templates/input_template.xlsx` 作成 | **半日 (decide)** + 1 day (template) |
| 7 | **P1** | Reference の独立 readability (上位 SSoT への back-reference 散発) | 20 file 冒頭に「本書の前提 / 上位 SSoT への back-reference」block を 5-10 行で追加 | **2-3h** |
| 8 | **P2** | `13a / 14` の startup-modeling 枠超え | SKILL.md description に "Pre-Seed → Pre-IPO" と stage range 明示 + `13a / 14` の冒頭に「Series D 以降 / IPO 準備で参照」と前提明示 | **30 min** |
| 9 | **P2** | Skill 名 `startup-financial-modeling` の長さ | 短縮 (`startup-modeling`) も検討対象だが、過去 commit / cross-link 影響あり、今回は維持推奨 | **decision only** |
| 10 | **P2** | `audits/` directory が `tests/` と区別されない | Phase 6 で `tests/` 新設時に「`audits/` = 品質保証ログ / `tests/` = TDD test fixture」と SKILL.md で明示 | **15 min** (declaration) |

### 7.1 Priority key

- **P0**: skill-creator framework 必須要件 (SKILL.md / evals / triggering 検証)。これらが揃わないと Phase 6 着手は無意味
- **P1**: 品質保証 / scaling 上重要だが、Phase 6 を **始める** 障害ではない
- **P2**: nice-to-have

---

## 8. Action Plan

### Wave 1 (Immediate — Phase 6 着手前必須)

| # | Task | 所要 | 担当 reference |
|---|---|---|---|
| 1.1 | SKILL.md draft 作成 (§1.4 テンプレート) | 1.5h | (新規) |
| 1.2 | `evals/evals.json` 作成 (§6.2 テンプレート) | 30 min | (新規) |
| 1.3 | `final_review.md §3.2` の SSoT 違反 5 件を inline fix | 30 min | `04b:735`, `01a §5.3`, `01a:728/782/1121`, `02:1411` |
| 1.4 | trigger eval 20 query の user 確認 → `run_loop.py` で description 最適化 | 1 day (background) | (`/tmp/trigger_eval.json`) |

**Wave 1 完了条件**: `SKILL.md` が listed され、20 query で trigger 率 >80% (should-trigger), <10% (should-not-trigger)。

### Wave 2 (Phase 6 開始前 — quality 強化)

| # | Task | 所要 |
|---|---|---|
| 2.1 | 残 20 reference に frontmatter 追加 | 2h |
| 2.2 | 15 大型 reference の TOC 整備 sampling audit + 補完 | 3-4h |
| 2.3 | Reference 冒頭の back-reference block 追加 | 2-3h |
| 2.4 | `13a / 14` の stage 前提明示 | 30 min |
| 2.5 | Build phase 戦略 (xlsxwriter vs openpyxl + template) declaration | 半日 |

### Wave 3 (Build phase 中)

| # | Task | 所要 |
|---|---|---|
| 3.1 | `scripts/build_model.py` scaffold (SaaS Series A only) | 1 week |
| 3.2 | `scripts/cap_table_builder.py` (J-KISS / SAFE state machine) | 1 week |
| 3.3 | `scripts/valuation_builder.py` (DCF + Comps + Football field) | 1 week |
| 3.4 | `tests/numeric_consistency_test.py` (sampling 7 → 30+) | 3 day |
| 3.5 | 案件レベル self-review iteration を `_self_review_protocol §5` に従い回す | 3-5 案件 |

---

## 9. Skill Maturity Score (10 pt)

| 軸 | スコア | 根拠 |
|---|---|---|
| **Reference depth** | **9/10** | 24 file 38,041 行、IB Color / 17 sheet / SAFE state machine / WACC≈g auto-fallback / 業態 11 routing。Phase 6 backlog 56 件は文書化済 |
| **SKILL.md / Orchestrator** | **2/10** | 不在。`_master_decision_tree.md` が事実上の orchestrator として機能しているが、router からは見えない |
| **Triggering** | **2/10** | description が無いため `available_skills` に listed されない。ゼロ trigger |
| **Progressive disclosure** | **5/10** | Layer 3 (resources) は強力、Layer 1-2 が空。3 層中 1 層しか機能していない |
| **Test coverage** | **3/10** | `_self_review_protocol §8` で案件レベル self-review は明文化、ただし `evals/` 不在で triggering 検証 + 出力品質検証は未実施。Phase 5 で numeric 7/55 sample 一致 |
| **Documentation** | **8/10** | `audits/final_status.md`, `final_review.md`, `accepted_high.md` で履歴 / 終了条件 / backlog が文書化、Phase 5 監査品質高い |
| **Implementation readiness** | **6/10** | reference 側の "実装可能 spec" は完成 (15 input schema YAML+JSON Schema+Pydantic 三本立て、05 §21.1 pseudo-test付き)、ただし scripts/ 空 |
| **平均** | **5.0/10** | SKILL.md / Triggering の 2 軸が大幅に足を引っ張っている。SKILL.md ランド後の予想平均 = 7.4/10 |

### 9.1 SKILL.md ランド後の予想スコア (Wave 1 完了後)

| 軸 | スコア | Δ |
|---|---|---|
| Reference depth | 9/10 | ±0 |
| SKILL.md / Orchestrator | 8/10 | +6 |
| Triggering | 8/10 | +6 (eval 20 query で >80% accuracy 想定) |
| Progressive disclosure | 9/10 | +4 |
| Test coverage | 6/10 | +3 (evals/evals.json 3 case) |
| Documentation | 8/10 | ±0 |
| Implementation readiness | 6/10 | ±0 (scripts/ は wave 3) |
| **平均** | **7.7/10** | **+2.7** |

---

## 10. Recommendation

### 10.1 Phase 6 (scripts/) 着手 OK か?

**❌ 現状では NO** — SKILL.md が無いと Claude は本 skill を呼び出せず、`scripts/build_model.py` を組んでも誰も invocation しない。

**✅ Wave 1 完了後 (1-2 hour) は YES** — SKILL.md + evals/evals.json が揃えば、`audits/final_status.md` の Phase 6 着手判定 (Critical = 0 / High ≤ 3 / SSoT = 0 / Numeric ✅) と組み合わせて build phase 1 (SaaS Series A) の scaffold を始められる。

### 10.2 ユーザーが invocation できる状態か?

**❌ 現状では NO** — `available_skills` list に "startup-financial-modeling" が現れない (description = "" のため)。

**✅ Wave 1 完了後 YES** — §1.3 の description が設定されれば、ユーザーが「Series A の SaaS モデル作って」と言ったときに skill が trigger される。

### 10.3 1 文 verdict

> **24 reference の corpus は IB / VC 実務水準で完成度が高いが、SKILL.md が無いため "skill" として機能していない**。Phase 6 着手前の **唯一の真のブロッカー** は SKILL.md (1-2 時間で解消可能)。残りの reference 整合性は `audits/final_status.md` 通り合格水準。

---

## 改訂履歴

| Date | Action |
|---|---|
| 2026-05-01 | 初版作成。skill-creator framework 全 10 評価軸で監査、SKILL.md 不在を P0 ブロッカーとして指摘、SKILL.md draft / evals テンプレート / 20 query trigger eval を提案 |
