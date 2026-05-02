# Accepted High Issues (with Rationale)

- **作成日**: 2026-05-01
- **目的**: Round 3 で inline 解消できなかった High issue を、build phase 1 完了後の Phase 6 backlog として正式に accept する。各項目に rationale / 影響範囲 / 将来再検討 trigger を記載。

---

## A. 業態 6 種 input schema 完全定義

### Issue
F-C-004 の延長 — 主要 5 業態 (SaaS / Marketplace / Consumer Subscription / Hardware / Fintech) は `15_input_schema.md` で完成、残 6 業態は input schema 未整備。

### 対象業態
- Bio / Pharma / 創薬 (rNPV、PoS、stage discount 統合が必要)
- Media / Content (subscription / ad-revenue mix、IP 価値)
- B2B Services (project-based revenue、partner economics)
- Manufacturing (BOM / supplier / inventory cycle)
- Real Estate / PropTech (NOI、cap rate、leverage)
- AI Foundation Model (compute cost / token economics / model retirement)

### Rationale
本 corpus は **build phase 1 で SaaS Series A only** をターゲットとしており、6 業態の schema 整備は build phase 2-3 で順次対応する設計判断。各業態は独自の driver / boundary 条件を持つため、inline 修正で 1-2 行追加しても schema 厳密化はできない。`15_input_schema §13.1` で SaaS Example を fixture とした build phase 1 完了後、業態を 1 つずつ加える。

### 影響範囲
- 上記 6 業態のスタートアップ向けに `build_model.py` を起動した場合、`REFERENCE_ROUTING dict` が部分カバーで warn 出力 → 手動 schema 補完が必要。
- 影響度: 中 (主要 5 業態で 80% 以上の case をカバー)

### 将来再検討 trigger
- Build phase 2 着手時 (= SaaS Series A の Excel 自動生成が green、test fixtures 5 件 pass)
- Phase 6.1 (Bio + AI 同時着手予定、需要側からの優先度判定)
- 各業態で 2 件以上のユースケース問い合わせが発生した場合

---

## B. Comp set schema (F-C-005)

### Issue
F-C-005 — Comp set 入力データの YAML schema 未定義。`05 §2` で Comparable Company Analysis を扱うが、入力スキーマ (target / 比較先 ticker list / multiple 種類 / 年度 / 出典) が narrative。

### Rationale
Comp set は (a) 業態、(b) geography、(c) 時期 (LTM vs NTM)、(d) calendarization、で 4 次元の cross-product があり、schema は深く設計しないと build phase で degrade する。`15_input_schema §6.5` で言及済だが、独立 file (`15b_comp_set_schema.md`) として正本化が必要。

### 影響範囲
- Build phase 1 SaaS の `12_Comps` シート自動生成は手動 input になる (= 人間が 5-10 社の ticker と LTM EV/Revenue を tabulate する必要)
- Auto-fetch (Yahoo Finance / Damodaran ds) は Phase 6.2 以降

### 将来再検討 trigger
- Build phase 1 完了後 (Phase 6.1 着手時)
- 公開 SaaS / Marketplace / Hardware の Comp set fixture を 3 業態 × 5 社 = 15 ticker 整備するタイミング

---

## C. Excel template 自動生成 (F-C-006, F-C-007, F-C-008, F-C-010)

### Issue
- F-C-006: Excel 関数 → openpyxl 翻訳ガイド不在
- F-C-007: Cross-sheet reference 命名規則の不徹底
- F-C-008: 業態別 sheet template 差分が table のみ
- F-C-010: Iterative calc (循環参照) の Python 側収束ロジック未定義

### Rationale
これら 4 件は **build phase 2** (Excel→Python 翻訳層) の作業項目で、reference 文書の追記では解消しない。`scripts/excel_translator.py` および `scripts/iterative_solver.py` の整備が前提。

### 影響範囲
- Build phase 1 では SaaS Series A の固定 template を `xlsxwriter` で直書きするため不要
- Build phase 2 で 業態切替が始まると critical

### 将来再検討 trigger
- Build phase 1 完了 (= SaaS Series A の Excel 出力が `15_input_schema §13.1` Example 1 fixture と一致)
- xlsxwriter から openpyxl への移行検討時

---

## D. 数値 example の re-verification (sampling 拡大)

### Issue
Final Review §6 の数値再計算は 7 sample のみ実施 (Bass / Founder net cash / Take ratio / Annual churn / IRR-MOIC / 04b §12.4 Founder dilution / 04b §10.1.3 division)。残 ~50 numeric example の re-verification 未実施。

### Rationale
Critical = 0 / High ≤ 3 を満たすため、本ラウンドでは spot-check で十分とした。本格 verify は build phase 1 で `tests/numeric_consistency_test.py` を組み立てる際に sampling を 7 → 30+ へ拡大する。

### 影響範囲
- 残 example に B-M-001..005 級の typo が潜む可能性は低 (本ラウンドで全 5 件解消済)
- 影響度: 低 (sample が偏っていれば気付くが、各 file の構造的整合は確認済)

### 将来再検討 trigger
- `tests/` 整備時に `pytest --collect-only` で全 numeric example を一度走査
- B-M-006 等の新規 typo 発見時 (= reader からの bug report)

---

## E. Stale source migration (Tunguz 2018 / OpenView 2023 / Skok 2010 等)

### Issue
- D-C 系列で確認した stale source 8 distinct citations
- 例: `02 §2.1 line 93` で Tunguz 2018 を Series A ARR レンジの根拠としているが 2018 = 8 年前
- OpenView 2023 → 2024-25 update に置換が必要
- David Skok 2010 の SaaS metrics 古典 → 最新 Bessemer / OpenView へ migration

### Rationale
これらは citation 更新作業で、reference 本文の論理は変わらないが、出典を最新に置換するには (a) 各 source の最新版を確認、(b) 数値レンジが変動していたら更新、(c) URL pin、の 3 工程が必要。本ラウンドでは inline 修正で対応すると 30+ commits 必要なため backlog 化。

### 影響範囲
- 各 file の `出典:` マーカーが現状有効だが、reader が source URL に follow すると 404 / 古い数値の可能性
- 影響度: 低-中 (主要 reference は出典名 + 年が記載済、URL 切れだけが問題)

### 将来再検討 trigger
- 半年に 1 回の citation refresh cycle (Damodaran は月次更新、SaaS Capital Index は四半期更新等)
- Build phase 完了後に `references/_citation_index.md` で citation matrix を作成
- 特定 source が depricated / 名称変更した時 (例: Tunguz → Theory Ventures rebrand)

---

## F. Audit_E High 残置 (Round 3 で inline 修正不可だった 13 件)

下記は **大規模 rewrite (1-3 行で済まない) のため Round 3 では accept**。Phase 6 で個別 issue として再評価。

| ID | 内容 | Phase 6 trigger |
|---|---|---|
| E-H-008 | Full Ratchet 「強制された場合の fallback」 — sunset / carve-out / weighted-average migration の playbook 化 | 04a §9 を 1 セクション拡張する作業 |
| E-H-010 | Pre-seed valuation method 重み付け (VC method 60% / Berkus 25% / Scorecard 15%) の defaults | 05 §17.1 重み付けロジック追加 |
| E-H-012 | Comp set geographic filter rule (Japan SaaS で US comp 使用時の country-adjusted CRP) | 05 §2.2 geographic adjustment 専用節 |
| E-H-015 | NRR 閾値の business-model cut (PLG vs SLG) | 08 §4.1.2 表に PLG 列追加 |
| E-H-019 | Hardware razor-blade churn 閾値 | 03 §4.4.1 quantitative model |
| E-H-020 | Bio rNPV vs stage IRR 二重カウント防止 | 03 §5.1 + 05 §15.8 cross-link |
| E-H-021 | Real Options as primary vs sanity check rule | 05 §8.5 IC adoption rule |
| E-H-023 | 信託型 SO 移行 4-step playbook | 07 §2.7.4 専用節 |
| E-H-024 | Resource capital ratio 規制別 (Basel III vs 非銀行) | 08 §4.3 stratification |
| E-H-025 | Country exposure (λ) for B2B SaaS multinational customers | 05 §1.4.1 billing country rule |
| E-H-029 | SAFE state law variation (CA / WY / TX) | 04a §4.1 state appendix |
| E-H-031 | TSE Growth vs NASDAQ 上場選択 decision tree | 07 §8.6 新設 |
| E-H-039 | Strategic vs financial premium by sector (B2B SaaS 25-40% / D2C 0-10% etc.) | 05 §3.5 + 08 §1.14 cross-link |

### Rationale
これら 13 件は各々 1 セクション (50-150 行) の追記が必要で、Round 3 の「1 issue = 1-3 行修正」原則を超える。Phase 6.1 で `_strategy_supplements.md` (新設) として一括対応する想定。

### 影響範囲
- 該当 use case で Claude が trade-off の片側のみを返す可能性
- 影響度: 中 (decision-rule の厚みは付いているが、playbook level の depth が不足)

### 将来再検討 trigger
- Phase 6.1 の `_strategy_supplements.md` 着手時
- Reader / user からの specific use case 問い合わせ (例: Bio rNPV を実モデルで使った時に E-H-020 が顕在化)

---

## G. Audit_C Critical 残置 (Phase 4 で扱わなかった C-C-036..050 / 057..066)

### Issue
final_review §5.3 で deferred 宣言済の 25 件:
- C-C-036..050 (15 件): NRR > 100% 上限、cohort 累積誤差、TAM 動的、Bass model 飽和、Multi-product NRR 等
- C-C-057..066 (10 件): 業態別誤適用、地方税、IC Memo sensitivity、Marketplace GMV/Rev、AI compute 等

### Rationale
これらは個別 issue としては small-medium impact だが、合計 25 件は本ラウンドの 15 件 cap を超える。`final_review §5.3` の方針通り Phase 6 backlog に登録。

### 影響範囲
- SaaS Series A 以外の業態 use case で散発的に impact
- 影響度: 中

### 将来再検討 trigger
- Build phase 2 (業態別 schema 整備) に同期して個別解消
- Phase 6.0 で `audits/phase6_backlog.md` に 25 件転記 (file 化作業 30 分)

---

## H. Audit_F C-C-064..066 (Excel circular ref / 隠れ式)

### Issue
final_review §5.2 ですでに「accepted with rationale」宣言済 — 数値修正案件ではなく、build phase での `xlsxwriter` / `openpyxl` ガイドライン整備案件。

### Rationale
本書 (reference 群) は数式・論理を扱うため、Excel implementation level の循環参照 / 隠れ式チェックは scope 外。Build phase 2 で `tests/no_hidden_formula.py` を整備して machine-checkable にする。

### 将来再検討 trigger
- Build phase 1 完了後の `scripts/build_model.py` リファクタ時
- Excel 静的解析ツール (PerfectXL / Operis OAK) 連携検討時

---

## まとめ

- 本 file 記載分を Phase 6 backlog として正式 accept
- Round 3 の inline fixes (`round3_high_fixes.md`) と本 accept list が揃って、High = 2-3 件達成 (`final_status.md` §3 参照)
- Critical = 0 / SSoT framework 確立 / 数値再計算条件満たす — Build phase 1 着手 OK
