# Wave 2 Quality Enhancement Log

- **作業日**: 2026-05-02
- **目的**: skill_creator_review.md §7 Wave 2 タスクを実行し、Maturity Score を 7.86/10 → 9.0+/10 へ引き上げる
- **前提**: Wave 1 (SKILL.md / evals/evals.json 新規作成) 完了済
- **方針**: 既存 corpus の **追記のみ**。本文・既存 TOC・既存 frontmatter は破壊しない

---

## 1. Wave 2 Task 一覧 (skill_creator_review §7)

| # | Task | 状態 | 補足 |
|---|---|---|---|
| 1 | 全 reference に frontmatter 追加 (24/24) | ✅ Done | 4 file (`_terminology` / `_master_decision_tree` / `_stress_framework` / `_self_review_protocol`) は既存、20 file 新規追加 |
| 2 | 大型 file (>1500 行) に TOC 追加 | ⚠️ Partial — TOC は **全 14 file に既存** のため新規追加不要。代わりに「TOC 存在確認」と「frontmatter 上部配置で TOC への routing 維持」で対応 | §3 参照 |
| 3 | 各 reference 冒頭に Back-reference block 追加 | ✅ Done | frontmatter 直後 / TOC の前に挿入 |
| 4 | SKILL.md dispatch table に section anchor を追加 | ✅ Done | sub-section anchor まで指定 (`§19.1 / §21.1 / §22 / §23` 等) |
| 5 | SKILL.md の Trade-off section を更新 | ✅ Done | Phase 6 着手準備完了状態に更新、`document-skills:xlsx` 併用パス明記 |
| 6 | evals/evals.json に assertions 追加 | ✅ Done | 各 case に 5-10 個の検証可能 assertion |
| 7 | trigger eval skeleton 作成 | ✅ Done | `audits/trigger_eval_skeleton.md` |

---

## 2. Frontmatter 追加対象 (20 file)

各 file に追加した frontmatter block の構造:

```yaml
---
name: <ファイル名から数字 prefix を除いたもの>
description: <1-2 文。何の正本か、SKILL.md からどの dispatch で読まれるか>
type: reference
priority: P1  # 全本文 reference は P1 (P0 は SSoT 4 file のみ)
related: [<相互参照する他 reference のリスト>]
---
```

| # | File | name | priority |
|---|---|---|---|
| 1 | `00_design_guidelines.md` | `design_guidelines` | P1 |
| 2 | `01a_modeling_standards.md` | `modeling_standards` | P1 |
| 3 | `01b_integrity_and_anti_patterns.md` | `integrity_and_anti_patterns` | P1 |
| 4 | `02_saas_metrics.md` | `saas_metrics` | P1 |
| 5 | `03_business_models.md` | `business_models` | P1 |
| 6 | `04a_convertible_and_terms.md` | `convertible_and_terms` | P1 |
| 7 | `04b_cap_table_mechanics.md` | `cap_table_mechanics` | P1 |
| 8 | `05_valuation_wacc.md` | `valuation_wacc` | P1 |
| 9 | `06_three_statement.md` | `three_statement` | P1 |
| 10 | `07_japan_specifics.md` | `japan_specifics` | P1 |
| 11 | `08_investment_thesis.md` | `investment_thesis` | P1 |
| 12 | `09_market_sizing.md` | `market_sizing` | P1 |
| 13 | `10_modeling_craft.md` | `modeling_craft` | P1 |
| 14 | `11_debt_financing.md` | `debt_financing` | P1 |
| 15 | `12_tax_strategy.md` | `tax_strategy` | P1 |
| 16 | `13a_consolidation_core.md` | `consolidation_core` | P1 |
| 17 | `13b_treasury_carveout.md` | `treasury_carveout` | P1 |
| 18 | `14_ipo_readiness.md` | `ipo_readiness` | P1 |
| 19 | `15_input_schema.md` | `input_schema` | P1 |
| 20 | `16_cost_structure.md` | `cost_structure` | P1 |

---

## 3. TOC Audit 結果 (Task 2 alteration)

skill_creator_review §3.3 で「>1,000 行 file (15 file) で TOC 確認 + 補完」推奨だったが、**Wave 2 着手時点で 14 大型 file (>1500 行) 全てに TOC が既存**:

| File | 行数 | 既存 TOC 位置 | 種別 |
|---|---|---|---|
| `00_design_guidelines.md` | 2,254 | line 13 | `## Table of Contents` |
| `02_saas_metrics.md` | 1,691 | line 11 | `## 目次` |
| `03_business_models.md` | 1,578 | line 7 | `## 目次` |
| `04a_convertible_and_terms.md` | 2,401 | line 15 | `## 目次` |
| `04b_cap_table_mechanics.md` | 2,384 | line 15 | `## 目次` |
| `05_valuation_wacc.md` | 2,440 | line 10 | `## 0. 本リファレンスの全体構成` |
| `07_japan_specifics.md` | 1,924 | line 22 | `## 目次` |
| `08_investment_thesis.md` | 2,001 | line 8 | `## 0. このリファレンスの使い方` (実質 TOC) |
| `09_market_sizing.md` | 2,399 | line 9 | `## 0. このリファレンスの使い方` (実質 TOC) |
| `11_debt_financing.md` | 2,602 | line 21 | `## 目次` (line 11 に `## 0. ドキュメントの使い方` も併存) |
| `12_tax_strategy.md` | 1,952 | line 17 | `## 目次` |
| `14_ipo_readiness.md` | 2,010 | line 38 | `## 目次` |
| `15_input_schema.md` | 2,603 | line 13 | `## 目次` |
| `16_cost_structure.md` | 1,906 | line 11 | `## 目次` |

**判定**: 重複 TOC を作ると drift する (clutter / 二重メンテ) ため、**新規 TOC 追加は実施せず**。Frontmatter と back-reference block のみ TOC の **直前** に配置する。

「§<number>」level の anchor は SKILL.md dispatch table 側で `§19.1` / `§22.5` 等まで掘り下げて指定 (Task 4) し、Claude が必要 section だけ load する流れで progressive disclosure を達成。

---

## 4. Back-Reference Block の構造

各 reference の frontmatter 直下、TOC 直前に以下を挿入:

```markdown
## このドキュメントの位置づけ

- **正本 (SSoT)**: 用語・色・閾値は [`_terminology.md`](_terminology.md) を canonical とする
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) §<該当 §> から本書 §<該当 §> へ dispatch される
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check を必ず実行
- **関連 reference**: <related list>
```

各 file の routing 先 (`_master_decision_tree §A〜E`) は file の役割に応じて指定。

---

## 5. SKILL.md dispatch table 改訂 (Task 4)

Before / After 抜粋:

| ユーザー発話の例 | Before | After |
|---|---|---|
| "Series A 評価額" | `05_valuation_wacc.md §1.6, §21-23` | `05 §1.6.3 (Gordon vs Exit Multiple), §21.1 (WACC≈g 発散), §22 (Stage Discount Default), §23 (Liquidation Method 選定)` |
| "SAFE 転換" | `04a §2, §19` | `04a §2 (SAFE), §19.1 (Round Event 順序), §19.2 (Triple-trigger Flow)` |
| "WACC が g 以下" | `05 §21.1` | `05 §21.1 (WACC≈g 発散 + Exit Multiple auto-fallback)` |
| "下方シナリオ" | `10 §19` | `10 §19.1-19.7 (Wind-Down framework full)` |

**確認済 anchor** (Wave 2 で grep verification):
- `04a §19` 配下: §19.1 (line 1822), §19.2 (1963), §19.3 (2096), §19.4 (2220), §19.5 (2415)
- `05 §21-23` 配下: §21.1 (1809), §22 (2184), §23 (2328)
- `04b §12` 配下: §12.1 (1777), §12.2 (1903), §12.3 (2007), §12.4 (2195)
- `08 §17` 配下: §17.1 (1474), §17.2 (1553)
- `11 §1.1` (line 65), §18.1-18.6 (2256-2523)
- `10 §19.1-§19.7` (line 1494-1642)

---

## 6. Trade-off Section 更新 (Task 5)

Before:
> **Phase 6 build 未完了**: `scripts/build_model.py` はまだ存在せず、xlsx は Claude が手動で構成。完成までは **`document-skills:xlsx` skill 併用** で生成する

After (Phase 6 着手準備完了状態 + interim path 明示):
> **Phase 6 着手準備完了 / build_model.py 着手前**: `audits/final_status.md §5` の通り Critical = 0 / High ≤ 3 / SSoT = 0 で着手判定通過。`scripts/build_model.py` の scaffold は SaaS Series A から開始予定。完成までの **interim path**: `document-skills:xlsx` skill を併用 + 24 reference の section anchor 経由で手動構成 (`SKILL.md` dispatch table の anchor 通り)。

---

## 7. evals.json assertions 追加 (Task 6)

case 1 (`saas_series_a_3yr_model`): 10 assertions
case 2 (`jkiss_to_series_a_conversion`): 8 assertions
case 3 (`existing_xlsx_sanity_audit`): 8 assertions

各 assertion に `id`, `text`, `type` (`structural` / `calculation` / `metric` / `design` / `logic`) を付与。

---

## 8. Maturity Score Δ (見込み)

| 軸 | Wave 1 後 | Wave 2 後 (見込み) | Δ |
|---|---|---|---|
| Reference depth | 9/10 | 9/10 | ±0 |
| SKILL.md / Orchestrator | 8/10 | 9/10 | +1 (dispatch table sub-anchor 化、trade-off 更新) |
| Triggering | 8/10 | 9/10 | +1 (sub-anchor 化で precision UP、Phase 7 run_loop で更に最適化想定) |
| Progressive disclosure | 8/10 | 9/10 | +1 (frontmatter 24/24 + back-reference 24/24) |
| Test coverage | 6/10 | 7/10 | +1 (assertions 追加) |
| Documentation | 8/10 | 8/10 | ±0 |
| Implementation readiness | 6/10 | 6/10 | ±0 (scripts/ は Phase 6) |
| **平均** | **7.57/10** | **8.14/10** | **+0.57** |

skill_creator_review §1.5 / §9.1 で predicted の "post Wave 1 = 7.7/10" は実数値 7.86/10 (Phase 5 final_status.md 通り) で、Wave 2 で **8.14/10** を目指す。

---

## 9. 改訂履歴

| Date | Action |
|---|---|
| 2026-05-02 | Wave 2 着手。20 reference に frontmatter + back-reference block 追加、SKILL.md dispatch refine、evals/assertions 追加 |
