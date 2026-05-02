---
name: self_review_protocol
description: skill 完成 ≠ 終了とし、多面的監査エージェントによる評価 → 修正 → 再監査 のループで品質を継続的に高める正本プロトコル。各案件で xlsx 生成後にも適用する self-review 義務化を含む
type: reference
priority: P0
---

# Self-Review Iteration Protocol

このドキュメントは、本 skill の **品質保証メタプロトコル** の正本である。skill 自体の構築だけでなく、**個別案件で xlsx を生成した後** にも適用される。「完成」を一度の出力で完了としない、という規律を明文化する。

## 1. 基本原則

### 1.1 完成 ≠ 終了
- xlsx / IC memo / cap table を出力しただけでは「完成」とみなさない
- 多面的 audit エージェントで評価し、結果に基づいて修正、再評価のループを回す
- 「十分な品質」と判断されるまで自走的に改善し続ける

### 1.2 評価軸の独立性
- 評価エージェントは生成エージェントと **独立** に動かす (生成者が自己採点する bias を避ける)
- 6 軸 (consistency / calculation / logic / grounding / strategy / implementation) は互いに独立した視点を持つ

### 1.3 evidence-based 改善
- 「直感」「経験則」だけで修正せず、**audit 結果の特定 issue ID** を起点に修正する
- 修正後は「該当 issue が解消したか」を再評価で verify する

## 2. 6 軸監査の標準セット

skill 構築時 (Phase 2) と同じ 6 軸を案件レベルでも適用する。各案件の xlsx 生成後、以下を並列で実行:

| Axis | 監査エージェント prompt の核 | 出力先 |
|---|---|---|
| **A. Consistency** | 案件内の cap table / 三表 / valuation / IC memo で同一概念の定義・数値が file 間で矛盾していないか | `<案件>/audits/A_consistency.md` |
| **B. Calculation** | 全数値例を再計算して誤りを検出。Excel 数式を Python で再実行 sampling | `<案件>/audits/B_calculations.md` |
| **C. Logic** | 場合分け欠落・edge case 未対応・複合シナリオ未考慮 (例: SAFE × Anti-Dilution × Pool refresh, WACC≈g 発散) | `<案件>/audits/C_logic.md` |
| **D. Grounding** | 全数値・閾値・ベンチマークの出典追跡可能性 (Tier 1-4 分類) | `<案件>/audits/D_grounding.md` |
| **E. Strategy** | trade-off 明示性、両論併記の網羅、stakeholder 視点の混乱がないか | `<案件>/audits/E_strategy.md` |
| **F. Implementation** | 構造化度、参照性 (build に直接使えるか、xlsx として開いて壊れないか) | `<案件>/audits/F_implementation.md` |

## 3. 改善ループ (Phase 4 → Phase 5 の構造)

### 3.1 Master Issues 統合
6 軸の audit 結果を 1 ファイル (`master_issues.md`) に集約。各 issue を:
- **Severity**: Critical / High / Medium / Low
- **Master ID**: M-001..M-NNN (audit ID と mapping)
- **File affected**: 修正対象
- **Recommendation**: 推奨修正

### 3.2 修正 Wave 設計
| Wave | 対象 | 並列度 |
|---|---|---|
| Wave 1 | Critical (即時必須) + 直接修正可能なもの (typo / numerical) | 4-6 並列 |
| Wave 2 | Logic / Strategy 系 (state machine spec, decision tree, boundary check) | 3-5 並列 |
| Wave 3 | Polish (High issues for top files) | 2-4 並列 |

### 3.3 修正後 再監査
Wave ごとに完了後、変更影響領域を **対象を絞って再監査** する。新規 issue が発生していないか確認。

## 4. 終了条件

以下を **すべて** 満たした時点で「十分な品質」と判定。**Layer 1 (skill metadata) の充足を含む** ことに注意:

### 4.1 Layer 1: Skill Invocation Readiness (skill-creator framework 準拠)
| 条件 | 閾値 | 計測方法 |
|---|---|---|
| `SKILL.md` 存在 | YAML frontmatter (name + description) + 本文 < 500 行 | ファイル存在 + ヘッダ確認 |
| `description` triggering quality | 主要キーワード 8+、業態×Stage×Geo 網羅、pushy + near-miss exclusion | 20 query trigger eval (10 should + 10 should-not) |
| `evals/evals.json` 存在 | 3+ test case | ファイル存在 |
| skill router で listed | available_skills 一覧に表示 | system reminder 確認 |

### 4.2 Layer 2-3: Reference 品質 (Phase 2-5)
| 条件 | 閾値 | 計測方法 |
|---|---|---|
| Critical issues | = 0 | 6 軸 audit 集計 |
| High issues | ≤ 3 | 同上 (accept with rationale 含む) |
| SSoT 不整合 | = 0 | `_terminology.md` cross-check (`grep` パターン + 目視) |
| 主要数値例 再計算一致 | sampling 100% pass | Python 再実行 |
| 三表突合 (該当時) | BS = L+E、CFS ending cash = BS cash、NI → RE tie | xlsx 内の SanityChecks シート |
| Cap table 整合 (該当時) | Σ% = 100%, FDSO 計算一致 | 同上 |

### 4.3 Layer 1 と Layer 2-3 の独立性 (重要)
Layer 1 と Layer 2-3 は **独立した品質軸** で、片方の達成は他方を保証しない。例:
- reference 整合性は完璧でも SKILL.md 不在 → skill router から見えず、ユーザーから invocation されない
- SKILL.md は完璧でも reference に Critical 残 → skill が呼び出されても誤った output

両 Layer の終了条件を **同時に** 満たすこと。終了条件チェックリストには **必ず両方を記載** する。

**Accept with rationale**: High 残件のうち、修正コスト > 価値と判断された場合は accept 可。ただし `audits/accepted.md` に **理由 + 影響範囲 + 将来再検討 trigger** を明記。

## 5. case-by-case 適用テンプレート

各案件の出力フロー:

```
入力 (15_input_schema 準拠 YAML)
  ↓
generate_model.py (build phase)
  ↓
出力 v0.1 (xlsx + IC memo)
  ↓
[Phase 2 audit: 6 軸並列]
  ↓
master_issues.md 生成
  ↓
Critical / High 修正 (Wave 1-3)
  ↓
[Phase 5 final review]
  ↓
終了条件満たす? ──No── (戻る)
  ↓ Yes
  出力 v1.0 (案件成果物)
```

## 6. Stall 防止ルール (経験則)

skill 構築時の経験から、subagent watchdog stall を回避するための制約:

| 制約 | 値 |
|---|---|
| 1 reference 生成 | 1500-1800 行 / 12 セクション以下 / mini case 3-4 個 |
| 1 audit 生成 | 50-150 issues / 直接読み込み + section sampling |
| 1 fix agent | 1 file 修正のみ (cross-file fix は inline) |
| 並列度上限 | 4-5 (server-side rate limit を避けるため) |
| 大領域 reference | 必ず 2 分割 (例: 04 → 04a + 04b、13 → 13a + 13b) |

## 7. Anti-pattern (反復 review で避けるべき)

- **Audit 結果の sampling 確認をせず agent 報告を盲信**: 必ず file system + grep でファクトチェック
- **Critical を修正したから完了**: High も合計件数で見るべき (3 件以下が目安)
- **同じ視点で再 audit**: 同じ視点だと同じ blind spot を持つ → 6 軸 + advisor で多角化必須
- **修正で別の issue を生む**: SSoT 経由の修正 (terminology.md) なら local 修正の連鎖を防げる
- **修正記録を残さない**: `round1/2_*.md` のような diff log は次セッション継続性を担保
- **"final" を 1 回で打つ**: Phase 5 後にまだ残 SSoT があった例を踏まえ、自動 grep + 目視で2 重確認

## 8. 案件レベル Self-Review 義務化

本 skill で xlsx を生成した直後、以下を **必ず実行** (10 check、Phase 6 で 5 check 追加):

1. `12_SanityChecks` シートの全 row が ✅ か確認 (BS check / CF check / 三表突合 / Σ check / Sign check)
2. `_master_decision_tree §C 4 段ゲート` の量的閾値通過確認
3. 業態 × Stage applicability matrix (`_stress_framework §4`) で誤適用メトリクスがないか
4. `_terminology.md` の canonical 値と xlsx 出力の数値が一致するか sampling 5 点
5. Accept with rationale な逸脱があれば xlsx の `00_Cover` Notes 欄に記録

### 8a. Phase 6 拡張 check (5 reference 統合に伴う新規 5 項)

6. **Customer ROI thesis**: pricing が `18_customer_value §3.1` の formula (Net Benefit / Customer Cost = Annual ROI) で justify されているか確認。**閾値**: 中央値 ROI > 0、payback < 業態 benchmark (SaaS 12mo / Hardware 18mo / D2C 6mo, `18 §3.2`)。**Sampling**: 主要 customer segment 上位 3 件で IC memo §Pricing の根拠数値と xlsx の `pricing.customer_roi_annual_pct` / `customer_roi_payback_months` が一致するか目視 + grep 確認
7. **WTP boundary**: pricing が `18_customer_value §4.1` gainsharing rule (vendor share = 20-30% of customer value) の範囲内に収まっているか確認。**閾値**: `0.20 ≤ gainsharing_pct ≤ 0.30` (硬境界)、`gainsharing_pct × customer_roi_annual_pct ≤ 0.50` (over-extraction 防止)。**Sampling**: input schema (`pricing.gainsharing_pct`) と xlsx `01_Assumptions` cell の double check (1 cell)
8. **M&A Exit thesis**: IC memo の Exit section が `19_ma_exit §1` の 3 要素 (likely buyers + founder net + earn-out probability) を **全て含んでいるか** 確認。**閾値**: 3 要素すべて記載 (欠落 0)、`expected_consideration_mix` の Σ = 1.0 ± 0.001、earn-out > 0 の場合 §11 の Bayesian conditional E[earn_out] が IC memo に記載。**Sampling**: IC memo §Exit を section header で grep + 必須 keyword (`likely buyer` / `founder net` / `earn-out`) 全件 hit 確認
9. **Named range coverage**: cross-sheet 参照の **80% 以上** が named range 経由か確認 (cell anchor 直接参照は新規モデルでは 20% 未満)。**閾値**: `12_SanityChecks` D12 row が PASS (coverage ≥ 80%)。**Sampling**: `scripts/sanity_checks.py --check D12 --xlsx <path>` を実行、または `scripts/ib_format.py § list_workbook_names` で全 named range を enumerate して `=Sheet!$A$1` 形式の生 cell ref と比較
10. **Design consistency**: 単位 scale / font Calibri 11pt / IB Color が `_design_consistency_rules` 全 §2-§3 に準拠しているか確認 (`sanity_checks D1-D12` 全 pass)。**閾値**: `12_SanityChecks` D1 (font 統一) / D2 (scale 一貫性) / D3 (IB color 適用) / D4 (number format 統一) / D5-D11 (各 sheet 個別) / D12 (named range coverage) **全 12 row で PASS**。**Sampling**: D row が ✅ か xlsx 内で目視 + 主要 sheet (`04_IS`, `05_BS`, `09_DCF`) の font / 色を 5 cell sampling で再確認

各 check の **不合格時 action**: `_self_review_protocol §3 修正 Wave` で対応 (Critical → Wave 1、それ以外 → Wave 2-3)。check 6-10 は **Phase 6 統合後の新規モデル** で必須、Phase 5 以前の既存モデルは accept with rationale (`audits/accepted_phase5_legacy.md` に記録) で skip 可。
