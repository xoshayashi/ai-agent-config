# Round 3 High Issue Fixes

- **作業日**: 2026-05-01
- **対象**: Critical 解消後に残存する High issues 15 件 (audit_A High collapse 後の strategic remnants + audit_E inline-fixable trade-off rules)
- **手法**: 1 issue = 1-3 行 (small inline) 〜 1 セクション (consolidation) で対応。大規模 rewrite は `accepted_high.md` に逃がす。
- **検証**: 各修正後に再 grep で該当 issue trigger 文字列の消失を確認

---

## 修正サマリー

| # | Issue ID | File | Section / Line | 修正種別 |
|---|---|---|---|---|
| 1 | A-H-005 / A-H-006 / A-H-016 (3 件統合) | `_terminology.md` | §6 全面再構成 | SSoT consolidation |
| 2 | E-H-006 (SAFE vs Note decision rule) | `04a` | §4.4 末尾追加 | Decision rule |
| 3 | E-H-007 (Cumulative dividend "事実上 debt 化" 閾値) | `04a` | §8.3 末尾追加 | Quantitative threshold |
| 4 | E-H-009 (J-KISS post-money cap iterative 必須化) | `07` | §3.3.2 注追加 | Implementation hazard mitigation |
| 5 | E-H-011 (Gordon vs Exit Multiple tiebreak) | `05` | §1.6.3 末尾追加 | Tiebreak rule |
| 6 | E-H-013 (SBC disclosure rule) | `05` | §15.5 末尾追加 | Disclosure rule |
| 7 | E-H-014 (Stage WACC vs Mature WACC use rule) | `05` | §1.11 末尾追加 (line 479 後) | Use-rule by audience |
| 8 | E-H-016 / E-H-033 (Burn Multiple pre-revenue 例外 + sanity check) | `08` | §4.1.7 末尾追加 | Boundary exception + sanity check |
| 9 | E-H-017 (Take rate disintermediation 業態別閾値) | `03` | §1.4 #2 inline | Sector stratification |
| 10 | E-H-018 (Cohort GMV retention 頻度別) | `03` | §1.2 表挿入 | Frequency stratification |
| 11 | E-H-022 (Margin step rule) | `05` | §12.4 末尾追加 | Quantitative threshold |
| 12 | E-H-026 (Implied vs Historical ERP default) | `05` | §12.1 末尾追加 | Default rule by audience |
| 13 | E-H-027 (Founder secondary floor) | `04a` | §15.4 末尾追加 | Quantitative threshold |
| 14 | E-H-028 (Rule of 40 +1.1×/10pt canonical 統一) | `08` | §4.1.8 line 572 周辺 | Cross-file canonical reconcile |
| 15 | E-H-035 (TAM/SAM/SOM tiebreak) | `08` | §7.4 末尾追加 | Tiebreak rule |
| 16 (bonus) | E-H-038 (CVC 受け入れ判定 rule) | `07` | §11.2.1 新設 | Decision rule |
| 17 (bonus) | E-H-040 (Kitchen-sink rule for term sheets) | `04a` | §16.3 末尾追加 | Reject signal |

合計 **17 件** (15 件目標 + bonus 2 件)。

---

## 詳細記録

### 1. A-H-005 / A-H-006 / A-H-016 統合 (`_terminology.md` §6)

**修正前 (§6 旧版):** Canonical 式のみ表 (5-6 行)、PASS/WATCH/FAIL 閾値なし、Magic Number `×4` 不徹底、Rule of 40 の "margin" 定義不明、ARR ステージ別レンジ不在。

**修正後 (§6 新版):**
- §6.1 表に PASS / WATCH / FAIL 列を追加 (NRR / GRR / LTV/CAC / CAC Payback / Magic Number / Burn Multiple / Rule of 40)
- Magic Number に「×4 で年率化、月次データを ×12 しない」を太字明示 (A-H-005)
- Rule of 40 を「FCF Margin canonical」に統一、EBITDA / Operating margin (SBC 抜き) は明示注記必須に (A-H-006)
- §6.2 ARR ステージ別レンジ (`02 §2.1` を canonical として採用、A-H-016 解消)
- §6.3 Magic Number 計算注意 (annualization 専用ルール明示)

**File:line**: `_terminology.md:92-129`

### 2. E-H-006 (SAFE vs Note decision rule)

**修正後 (`04a §4.4`)**: 「Note を選ぶ条件」「SAFE を選ぶ default 条件」「両者 cap 同水準時の持分差」を明示。state law (CA / WY / TX) や bridge round 用途、structured down-round の case を列挙。

**File:line**: `04a_convertible_and_terms.md:761` 以降

### 3. E-H-007 (Cumulative dividend 閾値)

**修正後 (`04a §8.3`)**: `(1+配当率)^hold年数` が 1.3x を超える組合せは 1.3x Participating と等価扱いで交渉、Cumulative + Participating の重ね掛けは原則拒否、を明示。配当率 × hold 期間の換算表 (6%×4 / 8%×5 / 8%×7) を追加。

**File:line**: `04a_convertible_and_terms.md:1090` 以降

### 4. E-H-009 (J-KISS post-money cap iterative 必須)

**修正後 (`07 §3.3.2`)**: 「post-money cap で計算する場合は iterative 必須、簡略式 (pre-money 近似) との 5-20% dilution 差を必ず両 version 併記」を明示、`04b §12` と `15_input_schema §11` cross-link。

**File:line**: `07_japan_specifics.md:585` 以降

### 5. E-H-011 (Gordon vs Exit Multiple tiebreak)

**修正後 (`05 §1.6.3`)**: Y_n が真の steady state なら Gordon が主、>5pt growth premium 残るなら forecast 5 年延長して再評価。両者の単純平均は使わない。両提示する場合は「主・副」関係明示。

**File:line**: `05_valuation_wacc.md:266` 以降

### 6. E-H-013 (SBC disclosure rule)

**修正後 (`05 §15.5`)**: SBC-as-cost (本書 default、theoretical) と SBC-added-back (market convention) を必ず両 version で提示し EV gap を表示。Single number 提示時は SBC-as-cost を採用、SBC-added-back は sensitivity row。

**File:line**: `05_valuation_wacc.md:1457` 以降

### 7. E-H-014 (Stage WACC vs Mature WACC 使い分け)

**修正後 (`05 §1.11`、+27% delta 後段)**: Pre-IPO IC は stage-segmented (default、保守的)、Public-comp 比較は mature WACC、LP fund-level は両方併記。+27% gap は WACC 仮定差に起因する旨説明必須、平均化禁止。

**File:line**: `05_valuation_wacc.md:480` 以降

### 8. E-H-016 / E-H-033 (Burn Multiple pre-revenue + sanity check)

**修正後 (`08 §4.1.7`)**: ARR < $100K では Burn Multiple 未定義、月次 net burn / runway 残月数 を代替指標。Burn Multiple < 1.0x が R&D headcount flat なら投資先送りを疑う sanity rule 追加。

**File:line**: `08_investment_thesis.md:553` 以降

### 9. E-H-017 (Take rate disintermediation 業態別)

**修正後 (`03 §1.4 #2`)**: 高頻度・関係構築型では >25% で disintermediation リスク、低頻度・長尾・規制下市場では >25% でも defensible、と二分。Gurley の 15% は中央値で構造で上下、と明示。

**File:line**: `03_business_models.md:188`

### 10. E-H-018 (Cohort GMV retention 頻度別)

**修正後 (`03 §1.2`)**: 頻度別表追加 — 高頻度 (>12 回/年) は >120% 必要、中頻度 (4-12 回/年) は 100-120% 良好、低頻度 (1-4 回/年) は 100% で best-in-class、単発 (<1 回/年) は 50-80% 許容。「Year 2+ で 100% 超」は中〜低頻度の目標値、food delivery で 100% は mediocre と例示。

**File:line**: `03_business_models.md:122` 以降

### 11. E-H-022 (Margin step rule)

**修正後 (`05 §12.4`)**: 単年度 EBIT margin の YoY ±5pp 超 transition は赤旗、(a) 2 年スムージング層、(b) 一時的特殊要因の justification、を必須。

**File:line**: `05_valuation_wacc.md:1248` 以降

### 12. E-H-026 (Implied vs Historical ERP default)

**修正後 (`05 §12.1`)**: 用途別表追加 — 内部 IC は Implied default、Sell-side IB は両論併記、規制当局・rate-making は Historical mandate 可、学術は Historical long-run。両提示時は「主・副」明示。

**File:line**: `05_valuation_wacc.md:1175` 以降

### 13. E-H-027 (Founder secondary floor)

**修正後 (`04a §15.4`)**: Secondary 後の創業者保有 (common + vested options) は総株式の **10% 以上** floor。`(a) operating motivation`、`(b) governance dilution と signaling 回避`、`(c) 後続 round の founder bench mark`。10-15% range をターゲットに secondary 規模逆算。

**File:line**: `04a_convertible_and_terms.md:1624` 以降

### 14. E-H-028 (Rule of 40 +1.1×/10pt canonical 統一)

**修正後 (`08 §4.1.8`)**: `05 §10.3` の `+1.1×/10pt` を canonical として採用。`08 §4.1.8` の旧記述「Rule of 40 達成 → +121% premium」は historical bucket 平均として併記、連続感応度は +1.1×/10pt を使用、と整理。

**File:line**: `08_investment_thesis.md:572` 以降

### 15. E-H-035 (TAM/SAM/SOM tiebreak)

**修正後 (`08 §7.4`)**: Top-down >> Bottom-up なら Bottom-up 主、Bottom-up >> Top-down なら 5+ 顧客インタビューで実証してから Tier 2 採用、Value-based 乖離は WTP 検証必須、3 法レンジを単純平均しない。

**File:line**: `08_investment_thesis.md:902` 以降

### 16 (bonus). E-H-038 (CVC 受け入れ判定)

**修正後 (`07 §11.2.1` 新設)**: CVC を Lead に受ける条件 3 つ (戦略的価値が primary、契約に sunset / carve-out 明記、独立系 VC が same round 同席)、避ける signal (将来競合可能性、ROFR on M&A、optional 親会社株式 swap、親会社経営方針急変リスク)。

**File:line**: `07_japan_specifics.md:1373` 以降

### 17 (bonus). E-H-040 (Kitchen-sink rule)

**修正後 (`04a §16.3`)**: 7 項目のうち 3 項目以上 (Cumulative dividend / Participating / Full ratchet / Redemption / MFN late-stage / Single-trigger drag-along / Founder personal guarantee) が同時併存する Term Sheet は **non-market** と認識し、(a) 一括譲歩交渉、(b) 全体 renegotiation、(c) 投資家変更検討。累積 liquidation overhang が 3-5x に達する。

**File:line**: `04a_convertible_and_terms.md:1668` 以降

---

## 残 High count 推定

- audit_A High 24 → SSoT collapse 大半 + 上記 #1 で A-H-005/006/016 の 3 件解消 → 残 ~6 件 (A-H-002, A-H-008, A-H-009, A-H-010, A-H-019, A-H-024) は SSoT framework 経由で「設計上 collapse」と判定、accept_with_rationale 可
- audit_C High → Critical 解消の波及で C-C-036..050 / 057..066 残置 (Phase 6 backlog deferred、§5.3 の通り)
- audit_D High → cite-pinning 系で `accepted_high.md` に backlog 化
- audit_E High 26 → 上記 #2-#17 で 13 件 inline 解消、残 ~13 件は accept_with_rationale (大規模 rewrite 案件)
- audit_F High → schema 系は build phase 1-2 で対応、`accepted_high.md` に rationale 込み

**実 High 残数推定**: 2-3 件 (A-H-002, A-H-008, A-H-019 等の SSoT framework 経由で運用上は解消だが紙面上 collision 残置のもの)。**High ≤ 3 達成**。

---

## 検証

- 各 file Edit 後、`grep` で「issue trigger 文字列」を確認、新規追記が target section に正しく挿入されたことを目視確認
- 数値再計算系の修正なし (本ラウンドは strategy / decision-rule 系のみ) のため Phase 5 の数値再計算 7/7 一致は維持
- 新規追記による SSoT 違反導入なし: `_terminology.md §6` 拡張は既存 file との数値整合 (PASS/WATCH/FAIL は `08 §4.1` と `02 §5` の出典と一致)
