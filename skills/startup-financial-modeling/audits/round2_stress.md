# Round 2 Fix: Multi-Covenant + Stress Scenarios

- 対象: 監査 C (Logic) Critical 17 件
- 解消対象 finding: C-C-051..056 (Multi-covenant cross-default), C-C-067..078 (Stress / Cross-domain logic gap)
- 状態: skeleton 保存済 → 段階的に追記 → 完了

## 解消マッピング

### Multi-Covenant 系 (C-C-051..056) → `11_debt_financing.md` §18 追記

| Finding | 概要 | 修正対象 file | 対応 section |
|---|---|---|---|
| C-C-051 | Multi-covenant 同時 breach 時の優先順位ロジック不在 | `references/11_debt_financing.md` | §18.1 |
| C-C-052 | Cross-default vs Cross-acceleration の区別不在 | `references/11_debt_financing.md` | §18.2 |
| C-C-053 | Equity cure 上限到達ロジック (回数 / amount cap) 不在 | `references/11_debt_financing.md` | §18.3 |
| C-C-054 | PIK toggle (利率連動 PIK 切替) ロジック不在 | `references/11_debt_financing.md` | §18.4 |
| C-C-055 | Refinance 失敗 → bankruptcy timeline 不在 | `references/11_debt_financing.md` | §18.5 |
| C-C-056 | 経営者保証 effective cost 差の数値化不在 | `references/11_debt_financing.md` | §18.6 |

### Stress / Cross-domain 系 (C-C-067..078) → 新規 `_stress_framework.md`

| Finding | 概要 | 対応 section |
|---|---|---|
| C-C-067 | Equity round 後の Debt covenant 影響 (cross-domain) 不在 | `_stress_framework.md` §1.1 |
| C-C-068 | Down round → Anti-dilution → Pool 拡大 cascade 不在 | `_stress_framework.md` §1.2 |
| C-C-069 | Tax loss carryforward × M&A (Section 382 / 適格組織再編) 不在 | `_stress_framework.md` §1.3 |
| C-C-070 | IPO 時 SO acceleration + Lock-up + Greenshoe の連鎖 不在 | `_stress_framework.md` §1.4 |
| C-C-071 | Bankruptcy claim priority (各 claim 順位) 不在 | `_stress_framework.md` §1.5 |
| C-C-072 | 業態別 metric mismatch (Pre-revenue で LTV/CAC 等) 防止策不在 | `_stress_framework.md` §4.1 |
| C-C-073 | Profitable 企業に Burn Multiple 当てはめる誤謬 防止策不在 | `_stress_framework.md` §4.1 |
| C-C-074 | Post-IPO 企業に SAFE 残高考慮の誤謬 防止策不在 | `_stress_framework.md` §4.1 |
| C-C-075 | Recession scenario 仕様不在 (-30% revenue 等の数値定義) | `_stress_framework.md` §2.1 |
| C-C-076 | Customer concentration loss シナリオ不在 | `_stress_framework.md` §2.2 |
| C-C-077 | Regulatory shock シナリオ (Fintech / Bio / 国際) 不在 | `_stress_framework.md` §2.3 |
| C-C-078 | Black Swan / Macro stress 仕様不在 | `_stress_framework.md` §2.4-2.5 |

## 番号付け方針 (advisor 指摘への対応)

- 当初 spec は `11_debt_financing.md` §16 末尾追加と記述。
- しかし現状の `11_debt_financing.md` は §17 (Term Sheet レビュー チェックリスト) で終了済 (§16 は Debt DD チェックリスト)。
- 既存番号を破壊しないため、新規追加 block は **§18 Multi-Covenant Cross-Default Mechanics** として §17 の後に追加。
- 内部下位番号 (18.1..18.6) は spec の 16.1..16.6 と 1:1 対応を維持。
- audit_C 解消マッピング上は「§18」で統一参照。

## 修正ログ

- step1: skeleton 3 file 保存 (本 file を含む)
  - `references/11_debt_financing.md` §18 skeleton 追記
  - `references/_stress_framework.md` skeleton 作成
  - `audits/round2_stress.md` (本 file) 作成
- step2: `_stress_framework.md` frontmatter + §1 (Cross-domain) 本体
- step3: `_stress_framework.md` §2 (Stress / Tail シナリオ) 本体
- step4: `_stress_framework.md` §3 (Stress Test 実装)
- step5: `_stress_framework.md` §4 (業態別 / Stage 別 applicability)
- step6: `_stress_framework.md` §5 (数値例 mini case)
- step7: `11_debt_financing.md` §18 本体追記
- step8: 本 file 修正ログ最終化

## Cross-reference 方針 (advisor 指摘への対応)

- `_stress_framework.md` §1 は本 file が SSoT として cross-domain 論理を集約。各論の mechanics 詳細は以下に back-reference:
  - §1.1 Equity round → Debt covenant: `11_debt_financing.md` §3 (covenant 定義), `04b_cap_table_mechanics.md` §3
  - §1.2 Down round cascade: `04a_convertible_and_terms.md` §3 (Anti-dilution), `04b_cap_table_mechanics.md` §5 (Option Pool refresh)
  - §1.3 Tax × M&A: `12_tax_strategy.md` §6-§7 (NOL, 組織再編)
  - §1.4 IPO acceleration: `14_ipo_readiness.md` §4 (SO), §5 (Lock-up)
  - §1.5 Bankruptcy priority: `11_debt_financing.md` §8 (デフォルト処理)
- `11_debt_financing.md` §18 は新規追記 (multi-covenant の `11` 内部完結ロジック)。

## 完了条件

- [x] `audits/round2_stress.md` skeleton (本 file) 作成
- [x] `references/11_debt_financing.md` §18 skeleton 追記
- [x] `references/_stress_framework.md` skeleton 作成
- [x] `_stress_framework.md` §1 本体 (Cross-domain)
- [x] `_stress_framework.md` §2 本体 (Stress / Tail)
- [x] `_stress_framework.md` §3 本体 (Stress Test 実装)
- [x] `_stress_framework.md` §4 本体 (業態別 / Stage 別)
- [x] `_stress_framework.md` §5 本体 (数値例 mini case)
- [x] `11_debt_financing.md` §18 本体追記 (200-400 行)
- [x] 本 file 修正ログ最終更新
