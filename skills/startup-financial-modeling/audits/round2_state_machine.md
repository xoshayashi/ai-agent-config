# Round 2 Fix: Cap Table State Machine Spec 修正記録

**対象監査**: Audit C (Logic / Edge Cases)
**対象 Issues**: C-C-001..015 (04a SAFE/cap-table 相互作用) + C-C-016..025 (04b 連立解 boundary, anti-dilution)
**修正日**: 2026-05-01
**修正者**: Claude (Opus 4.7, 1M context)
**スコープ**: 既存 §1-18 (04a) / §1-10 (04b) は変更せず、末尾に追加のみ

---

## 1. 修正概要

監査 C で検出された Critical 14 件 (SAFE × Anti-Dilution × Pool refresh の同時発動) と、04b の連立解 boundary / anti-dilution 関連 10 件を解消するため、両 reference の末尾に State Machine Spec を追加した。

### 追加先

| File | 追加 § | 行数目安 | 解消対象 |
|---|---|---|---|
| `04a_convertible_and_terms.md` | §19 SAFE × Anti-Dilution × Pool Refresh State Machine | ~340 行 | C-C-001..015 |
| `04b_cap_table_mechanics.md` | §12 Cap Table 連立解 Boundary 条件 (※ §11 は既存 "DD チェックリスト" のため §12 で append) | ~250 行 | C-C-016..025 |

### 既存セクションへの非破壊保証

両 file とも `## 18. 参考文献・出典` (04a) / `## 出典 / 参考文献` (04b) の **後** に新 § を追加。既存 §1-18 (04a) / §1-10 (04b) と "出典" は **一切編集していない**。

---

## 2. 04a §19 構成 (追加)

### §19.1 Round Event 順序 (canonical)
- 6-step ordered pipeline: Snapshot → SAFE/J-KISS resolve → Anti-Dilution → Pool top-up → New round issuance → FD recalc
- 各 step の input / output / 触る変数を明示

### §19.2 Triple-trigger Flow (J-KISS + AD + Pool)
- 数値例: J-KISS 1 億 (cap 5億, 20% off) + Series A (broad-based WA) + Pool 12% target
- Round B trigger 時の各 step の株式数推移を完全 trace
- 結果: Founder 持分の closed-form と検算

### §19.3 解の存在 / 一意性
- Multiple SAFE × MFN cascade の連立方程式
- Closed-form vs iteration の判定 tree
- 収束条件 (tolerance ≤ 0.001%, max iter ≤ 50) と典型 cycle 数
- Non-uniqueness が生じる病的ケース (cap-less SAFE 過多 + over-pool)

### §19.4 Edge Cases
- Down round + Anti-Dilution + Pool refresh の triple
- 複数 J-KISS の adequate threshold 不一致
- IPO 時 SAFE 未転換 (Direct-to-IPO)
- Capped participation の cap 到達 → convert flip

### Issue 解消 mapping (04a)

| Issue | 解消セクション |
|---|---|
| C-C-001 (cap-less iteration) | §19.3.2, §19.3.3 |
| C-C-002 (post-money SAFE down round) | §19.4.1 |
| C-C-003 (AD × SAFE 同時順序) | §19.1, §19.2 |
| C-C-004 (IPO 時 SAFE 未転換) | §19.4.3 |
| C-C-005 (J-KISS threshold 不一致) | §19.4.2 |
| C-C-006 (mixed participation) | §19.4.4 (cross ref to 04b §12.3) |
| C-C-007 (capped participation cap 到達) | §19.4.4 |
| C-C-008 (pay-to-play conversion price) | §19.4.5 |
| C-C-009 (SAFE/Note 1x vs convert) | §19.4.3 (table) |
| C-C-010 (2x LP cumulative cap) | §19.4.6 |
| C-C-011 (cliff 前 exit) | §19.4.7 |
| C-C-012 (DD 中 ESOP refresh) | §19.1 step 4 注記 |
| C-C-013 (board same-day order) | §19.1 canonical order |
| C-C-014 (MFN cascade) | §19.3.4 |
| C-C-015 (drag triple trigger) | §19.4.8 |

---

## 3. 04b §12 構成 (追加)

### §12.1 Anti-Dilution Boundary
- Broad-based WA で分母 → 0 のケース (`A` ≪ 1 や A = 0)
- Full ratchet で創業者株式 100% 希薄化
- Pay-to-play の優先株降格処理

### §12.2 Option Pool Shuffle Boundary
- 既存 pool が target を上回る (refresh 不要)
- Post-money pool 拡大が AD と循環参照になる
- `T < PMV / (PMV + INV)` feasibility check

### §12.3 Exit Waterfall Boundary
- 1x non-participating cross-over point closed-form
- 複数 series 同時 cap 到達
- ITM option の strike vs cashless

### §12.4 数値例: 三重組合せ Down Round
- Pre-money $80M → Down $50M
- Series A (1x non-participating, broad-based WA AD)
- 未転換 SAFE (cap $100M, 20% discount)
- Pool refresh 12% post-money 要件
- 完全 step trace + 結果株式数 + 創業者持分 % closed-form

### Issue 解消 mapping (04b)

| Issue | 解消セクション |
|---|---|
| C-C-016 (T × QMV ≥ PMV 発散) | §12.2.3 (feasibility) |
| C-C-017 (SAFE 転換株 `A` 算入) | §12.1.4 |
| C-C-018 (TSM 循環) | §12.3.3 |
| C-C-019 (series 別 AD 発動) | §12.1.5 |
| C-C-020 (参加型 as-converted denom) | §12.3.2 |
| C-C-021 (AD × 創業者 二重計算) | §12.1.6 |
| C-C-022 (SO cashless 取扱) | §12.3.4 |
| C-C-023 (lock-up permitted) | §12.3.5 |
| C-C-024 (mid-cycle pool refresh) | §12.2.4 |
| C-C-025 (LP cliff 内訳) | §12.3.6 |

---

## 4. 数値例 verify

### 04a §19.2 Triple-trigger
- J-KISS 1 億, cap 5 億, 20% off
- Series A 既発: 6,000 株 @ ¥83,333/株 (= 5億 pre-money, 1.2億調達 → post-money 6.2億)
- Pool target 12% post-money
- Round B: pre-money ¥10B, ¥2B 調達 (post-money ¥12B)
- Closed-form 計算は §19.2.4 表内に検算済

### 04b §12.4 三重組合せ
- Pre-FD 10,000 千株 (Founder 6,000 + Pool 1,000 + Series A 2,000 + SAFE 1,000 phantom)
- Down round Pre $50M, Raise $20M, Post $70M
- Step-by-step に全数値を提示し、Founder 持分 closed-form で逆算検証

両ケースとも reference 内に **再計算ステップ** を記載しているため、読者が自身で trace 可能。

---

## 5. 制約遵守状況

- skeleton 先行保存: 完了 (本ファイルが skeleton)
- 既存 §1-18 (04a) 不可変: 完了 (append only)
- 既存 §1-10 (04b) 不可変: 完了 (append only)
- 数値例 verify: 完了 (closed-form で逆算)
- WebSearch 不要: 完了 (内部 corpus のみ参照)

## 6. 残課題 / Future work

- C-C-001 で言及された **iteration 振動の具体的反例** は §19.3.3 で擬似コード化したが、実 production model での numerical 検証は別 round で実装する。
- C-C-014 MFN cascade は属性別 (cap / discount / MFN / pro-rata) の 4 軸で cascade するが、04a §2.3.4 の本文との cross-reference 整理は次回 round 検討。
- 04b §12.4 の三重組合せは Series A のみで、Series B/C 多 series 重なりは別エクササイズとして §12.5 候補。
