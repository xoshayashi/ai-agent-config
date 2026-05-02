---
name: startup-financial-modeling
description: "Build IB-quality 14-sheet xlsx startup financial models, cap tables, valuation outputs, pricing theses, and IC memos across Pre-Seed to Pre-IPO for US/Japan startups. Trigger for quantitative startup-finance work (three-statement models, SAFE/J-KISS, DCF/comps, Rule of 40, NRR, LTV/CAC, Burn Multiple, runway, venture debt, M&A waterfall, TAM/SAM/SOM, WTP) and skip pitch-deck design, prose-only market analysis, or scripting tasks."
---

# Startup Financial Modeling

IB 品質の **14 sheet xlsx 財務モデル** + IC memo + cap table を生成する skill。Pre-Seed → Pre-IPO の各 stage、11 業態、US / Japan に対応。

## このスキルが解決する問題

- **Founder**: Series A/B 評価額の根拠を 14 sheet で正当化したい / J-KISS 転換後の希薄化を trace したい
- **VC/PE**: IC memo + 三表突合付き sensitivity を半日で作りたい / kill criteria に通っているか定量判定したい
- **CFO**: 三表モデル + Cap Table + 監査整合 (J-SOX / SOX 404) を IPO 準備期に整えたい
- **アナリスト**: 業態 × stage の正しいメトリクスを引いてモデリングしたい

> 計算式・条項・数値・閾値は `references/` 配下に分散。本 SKILL.md は **orchestration (dispatch) のみ** を担う。Reference の本文を再記述しない。

## 基本ワークフロー (5 steps)

1. **Mode 選択**: Quick / Standard / Comprehensive を `references/15_input_schema.md §1` の質問で確定
2. **業態 × Stage 判定**: `references/15_input_schema.md §2-3` の enum + auto-judge
3. **Routing**: 下記 dispatch table と `references/_master_decision_tree.md §A-E` で読むべき reference を確定
4. **Generate**: 14 sheet xlsx + IC memo を build (Phase 6 で `scripts/build_model.py` がここを担当、現状は手動構成)
5. **Self-review**: `references/_self_review_protocol.md §8` の必須 5 check を実行 → 不合格なら修正 loop

## Reference Dispatch Table (intent → 第 1 reference + section anchor)

| ユーザー発話の例 | 第 1 reference (sub-section anchor 指定) | 補完 reference |
|---|---|---|
| "Series A 評価額を知りたい" | `_master_decision_tree.md §B` | `05 §1.6.3 (Gordon vs Exit), §21.1 (WACC≈g 発散), §22 (Stage Discount Default), §23 (Liquidation Method 選定)` |
| "SAFE 転換シミュレーションを" | `04a §2 (SAFE)`, `§19.1 (Round Event 順序)`, `§19.2 (Triple-trigger Flow)` | `04b §12.1-12.4 (Boundary 条件 + 三重組合せ down round trace)`, `19_ma §6 (Founder Net) 派生` |
| "J-KISS post-money cap で converted shares" | `07 §3.1-3.3 (J-KISS 標準条項 + 転換計算)` | `04a §3.4 (iterative solver), _terminology §5` |
| "SaaS metric の正しい定義" | `_terminology §6 (canonical)` | `02_saas_metrics.md` 該当 § |
| "IC memo 雛形" | `08 §17.1 (Executive Summary), §17.2 (詳細版)` | `_master_decision_tree §C (4 段ゲート)` |
| "IPO readiness check" | `14_ipo_readiness.md` | `01a §3.2`, `13b (carve-out 観点)` |
| "業態 × stage で何を読むか" | `_master_decision_tree §E` | `15_input_schema §11.2` |
| "venture debt vs equity" | `_master_decision_tree §D` | `11 §1.1 (Venture Debt), §18.1-18.6 (Cross-default mechanics)` |
| "WACC が g 以下になった" | `05 §21.1 (WACC≈g 発散 + Exit Multiple auto-fallback)` | `_terminology §6` |
| "Down round / wind-down シナリオ" | `10 §19.1 (Trigger), §19.2 (Path 比較), §19.4 (Decision Sequence), §19.7 (Kill Criteria 対応)` | `_stress_framework §2` |
| "三表突合 / SanityChecks" | `06 §12.1 (Hard checks), §12.2 (Soft checks), §12.3 (Sheet 例)` | `01b §6` |
| "Tax 戦略 (M&A / Delaware Flip / Pillar 2)" | `12_tax_strategy.md` | `07 §2 (日本 compliance)` |
| "Holdco / 連結 / Carve-out" | `13a_consolidation_core.md` (連結手続 / NCI / PPA) | `13b_treasury_carveout.md` (Treasury / IPO carve-out) |
| "Market sizing (TAM/SAM/SOM)" | `09_market_sizing.md` | `08 §7.4` |
| "コスト構造 (固定/変動/SBC)" | `16_cost_structure.md` | `02 §5` |
| "業態別 unit economics" | `03_business_models.md` (該当業態 §) | (業態別 §) |
| "pricing thesis / WTP / 顧客 ROI / value-based pricing" | `18_customer_value_and_pricing.md §3 (Quantification), §4 (Value-based pricing)` | `02_saas_metrics §6 (LTV/CAC), 16_cost_structure` |
| "M&A exit / 株式交換 / earn-out / lock-up / liquidation pref / founder net" | `19_ma_exit_for_founders.md §6 (Founder Net), §11 (Earn-out)` | `04b §10 (Exit Waterfall), 12_tax_strategy, 08_ic_memo` |
| "chart 設計 / IB chart / waterfall / sensitivity heatmap" | `17_chart_design.md` | `00_design_guidelines, 14_kpi_dashboard` |

> **Section anchor 戦略**: 大型 reference (`15_input_schema.md` 2,603 行、`09_market_sizing.md` 2,399 行 等) は全文 load せず、anchor (例: `§11.2`, `§13.1 Example 1`) で必要 section のみ参照する。
>
> **Cross-reference**: `04b §6 (Exit Waterfall)` は `19_ma_exit §6 (Founder Net)` の cap-table 機構を提供する派生関係。M&A 案件では `19_ma_exit` を上位 reference として読み、Waterfall 計算詳細を `04b` で参照する。`18_customer_value` は `02_saas_metrics §6 (LTV/CAC)` の WTP 上限を quantify する役割。

## SSoT 規約 (毎回確認)

`references/_terminology.md` を **canonical**。他 reference と矛盾する場合は terminology を優先:

- **IB Color**: Hard input = `#0000FF` / Formula = `#000000` / Cross-sheet link = `#008000` / External = `#FF0000`
- **Sheet naming**: `00_Cover ... 13_IC_Memo` (詳細は `_terminology.md §3`)
- **J-KISS 2.0**: 公開時期 = **2022-04** (post-money cap, `_terminology §5`)
- **SAFE Discount**: 0.20 = 20% off (multiply by 0.80 to get conversion price, `_terminology §4`)
- **Magic Number**: ×4 で quarterly-annualized (×12 で月次 annualize は不可、`_terminology §6.3`)
- **Rule of 40**: Revenue Growth % + **FCF margin** % (canonical / EBITDA margin は明示注記必須、`_terminology §6.1`)
- **Snowflake NRR**: FY24 Q4 = 131% / FY25 Q2 = 127% (canonical、`_terminology §6.4`)
- **法人実効税率 (日本大企業 2026~)**: 31.52% (`_terminology §7`)

## 14 Sheet Layout (default)

```
00_Cover            01_Assumptions      02_Revenue
03_OpEx             04_IS               05_BS
06_CFS              07_Debt             08_CapTable
09_DCF              10_Comps            11_KPI_Dashboard
12_SanityChecks     13_IC_Memo
```

各 sheet の row 構成・名前付きレンジ・cell 数式は `references/06_three_statement.md §2` および `references/01a_modeling_standards.md §5` を参照。

## 必須 Self-Review (xlsx 生成後)

`references/_self_review_protocol.md §8` の 10 check (Phase 5 base 5 + Phase 6 拡張 5) を毎回実行:

1. `12_SanityChecks` シートの全 row が ✅ か (BS check / CF tie / 三表突合 / Σ check / Sign check)
2. `_master_decision_tree.md §C 4 段ゲート` の量的閾値通過確認
3. `_stress_framework.md §4` applicability matrix で誤適用メトリクスがないか (Pre-revenue で LTV/CAC NG 等)
4. `_terminology.md` canonical 値と xlsx 数値が一致するか sampling 5 点
5. accept with rationale な逸脱があれば `00_Cover` Notes 欄に記録
6. **Customer ROI thesis** (`18 §3.1`): 中央値 ROI > 0、payback < 業態 benchmark
7. **WTP boundary** (`18 §4.1`): `0.20 ≤ gainsharing_pct ≤ 0.30`
8. **M&A Exit thesis** (`19 §1`): IC memo §Exit に likely buyers + founder net + earn-out probability の 3 要素
9. **Named range coverage** (`_named_ranges`): cross-sheet 参照の 80% 以上が named range 経由 (D12 row PASS)
10. **Design consistency** (`_design_consistency_rules`): 単位 scale / Calibri 11pt / IB Color が D1-D12 全 PASS

不合格なら `_self_review_protocol.md §3 修正 Wave` で修正 → 再 review。check 6-10 は Phase 6 統合後の新規モデル必須、既存 Phase 5 モデルは accept with rationale で skip 可。

## 業態 × Stage 早見

| 業態 | Pre-rev | Early Rev | Series A | Series B-C | Pre-IPO |
|---|---|---|---|---|---|
| SaaS | `04a + 09` | `+ 02 + 03` | `+ 04b + 05` | `+ 06 + 11` | `+ 13 + 14` |
| Marketplace | `04a + 09` | `+ 03 §1` | `+ 04b + 05 §11` | `+ 06 + 11` | `+ 13 + 14` |
| Fintech | `04a + 09` | `+ 03 §3` | `+ 04b + 05 §11` | `+ 06 + 11 §10` | `+ 12 + 13 + 14` |
| Bio | `04a + 09` | `+ 03 §5` | `+ 04b + 05 §8` | `+ 06 + 11` | `+ 12 + 13 + 14` |

> 詳細は `references/_master_decision_tree.md §E` および `references/15_input_schema.md §11`。

## Trade-off と limitations

- **Build phase 1 完成業態** (推奨利用): SaaS / Marketplace / D2C / Fintech / Hardware
- **Phase 2 backlog**: Bio / Media / B2B Services / Manufacturing / Real Estate / AI Foundation Model — schema は `15_input_schema §5` の主要 5 業態を流用 + 手動補完が必要 (`audits/accepted_high.md §A`)
- **Phase 6 着手準備完了 / `scripts/build_model.py` 着手前**: `audits/final_status.md §5` の通り Critical = 0 / High ≤ 3 / SSoT 不整合 = 0 / Numeric ✅ で着手判定通過。SaaS Series A 向け scaffold から開始予定。完成までの **interim path**: `document-skills:xlsx` skill を併用しつつ、本 SKILL.md dispatch table の sub-section anchor (例: `04a §19.1` / `05 §22`) 通りに 24 reference を section 単位で読み、Claude が手動で 14 sheet xlsx + IC memo を構成する
- **数値再検証**: 7/55 sample 完了 (Phase 5)。残 sample は build phase 1 の `tests/numeric_consistency_test.py` で拡大予定 (`accepted_high.md §D`)
- **Description 最適化未実施**: trigger eval 20 query は `evals/evals.json` に整備済、Phase 7 で `run_loop.py` を 5 iteration 回して description 精度を実測する設計。skeleton は `audits/trigger_eval_skeleton.md` を参照

## 関連 skill との境界

| 状況 | 推奨 skill | 理由 |
|---|---|---|
| 一般 xlsx 操作 (家計簿、データ整形) | `document-skills:xlsx` | 財務モデル特化ではない |
| Pitch deck (slides) | `document-skills:pptx` | xlsx でなく pptx |
| IC memo を Word で出したい | `document-skills:docx` | docx 出力 |
| 一般 PDF 操作 | `document-skills:pdf` | |
| 市場分析の文章のみ | (skill 不要、直接回答) | quantitative output 不要 |
| **財務モデル + xlsx + IC memo** | **本 skill** | corpus 適合 |

## Quality assurance

本 skill は Phase 1-5 を完走済 (`audits/final_status.md`):
- 24 reference / ~38,000 行 (Phase 6 で +5 reference: 17/18/19 + `_named_ranges` + `_design_consistency_rules`、計 29 reference / ~50,000 行)
- Critical issues = 0 (旧 31 件解消)
- High issues ≤ 3 (旧 ~115 件のうち 17 件 inline 修正 / 56 件 backlog accept)
- SSoT 不整合 = 0 (`_terminology.md` 経由)
- 数値再計算 sampling 7/7 一致

詳細は `audits/skill_creator_review.md` および `audits/final_status.md` を参照。
