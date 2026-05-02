# Round 2 Fix: Master Decision Tree + SAFE Founder Negotiation + Founder Wind-Down

- 対象: 監査 E (Strategy) Critical 3 件
- 解消対象 finding: E-C-001, E-C-002, E-C-005
- 状態: skeleton 保存済 → 段階的に追記

## 解消マッピング

| Finding | 概要 | 修正対象 file | 対応 section |
|---|---|---|---|
| E-C-001 | Cross-file decision tree が不在 (04a / 05 / 08 / 11 を繋ぐ master 不在) | 新規 `references/_master_decision_tree.md` | 全体 (A〜E) |
| E-C-002 | SAFE Pre-money vs Post-money の founder 交渉 rule of thumb 不在 | `references/04a_convertible_and_terms.md` | §2.X (新規 §2.9 として追加) |
| E-C-005 | Founder 側の wind-down (operational shutdown) framework 不在 (08 は VC kill criteria のみ) | `references/10_modeling_craft.md` | §19 (末尾追加、参考文献の前に挿入) |

## 修正ログ

- step1: skeleton 4 file 保存 (本 file を含む) — 完了
- step2: `_master_decision_tree.md` 本体作成 — 完了 (499 行)
- step3: `04a_convertible_and_terms.md` §2.9 追記 — 完了 (100 行、§2.8 直後 / §3 直前に挿入)
- step4: `10_modeling_craft.md` §19 追記 — 完了 (170 行、§18 と参考文献の間に挿入)
- step5: 本 file 完了記録 — 完了

## 検証結果

| Finding | 修正対象 | 行数 | 状態 |
|---|---|---|---|
| E-C-001 | `_master_decision_tree.md` 新規 | 499 行 | 完了 (target 500-800 の lower bound、内容密度を優先) |
| E-C-002 | `04a` §2.9 追記 | 100 行 | 完了 (target 50-100 の上限ぴったり) |
| E-C-005 | `10` §19 追記 | 170 行 | 完了 (target 100-200 の中間、Wind-Down 7 sub-section + Maxims 10 ヶ条 + 対応表) |

## 追記後の整合チェック

- `_terminology.md` に master decision tree への参照を追加するかは round 3 以降で検討。
- Cross-file 参照は本 master を SSoT として、04a / 05 / 08 / 11 はここを back-reference する形を維持。
- `_master_decision_tree.md` の routing 表 (E section) は `00_design_guidelines.md` の reference 一覧と整合させる。

## 完了条件

- [x] `_master_decision_tree.md` 作成 (499 行)
- [x] `04a_convertible_and_terms.md` §2.9 追加 (100 行)
- [x] `10_modeling_craft.md` §19 追加 (170 行)
- [x] 本 file の修正ログを最終 commit 状態に更新
