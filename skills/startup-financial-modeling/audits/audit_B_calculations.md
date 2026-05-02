# Audit B: Calculation Accuracy

## Summary

- Files prioritized & checked: 04b, 04a, 02, 06, 05, 11, 09, 08 (8 of 14 files; remaining 00, 01a, 01b, 03, 07, 10 are mostly conceptual / standards / qualitative content with little numerical density)
- Total numerical examples checked: ~45 substantive worked examples across the priority files
- Calculation errors detected: **6 substantive** (1 High, 4 Medium, 1 Low)
- Internal-formula calculations (closed-form OPS, anti-dilution, waterfall, DCF main path, Bass peak time, comps, VC method, working-capital schedule, debt-cost worksheets, J-KISS conversion, TSM): VERIFIED CORRECT
- Errors concentrated in *narrative-style* worked examples (story cases) — §10 of 04b, §11.3 of 09, §17.2.8 of 08 — rather than in core formulas

Severity legend:
- Critical: result wrong by >5%, sign/direction wrong, propagates to recommendations
- High: wrong by 1-5% / arithmetic error in a worked example that propagates
- Medium: wrong by <1% (rounding inconsistency), labeling/unit mismatch without numerical impact, or value mismatch in a sensitivity table that the reader would notice
- Low: typo not affecting numerical conclusion

---

## Critical Calculation Errors

(none found in priority-checked sections; the core formulas are clean)

---

## High Calculation Errors

### B-H-001: §10.3.5 Founder Net Cash sensitivity table — multiple internal inconsistencies

- **File**: `04b_cap_table_mechanics.md`, §10.3.5, lines 1627-1635
- **Original table** (Founder Net Cash by Exit Value):

  | Exit (¥M) | Founder Net Cash (¥M) | Take Ratio (doc) |
  |-----------|----------------------|------------------|
  | 3,800 | 0 | 0.0% |
  | 5,000 | 624.0 | 12.5% |
  | 6,000 | 1,262.6 | 21.0% |
  | 10,000 | 3,242.7 | 32.4% |
  | 11,442 | (B cross-over) | 35.4% |
  | 20,000 | 7,460.4 | 37.3% |
  | 50,000 | 18,649.4 | 37.3% (asymp) |

- **Recomputation** (using identical Cap-table input from §10.3.1; SO ITM → exercise + cash inflow ¥225M as in §10.3.2 line 1500):

  | Exit (¥M) | Cash Pool (¥M) | LP Stack | Residual | Founder | Ratio |
  |-----------|----------------|----------|----------|---------|-------|
  | 3,800 | 3,800 (SO OTM, strike ¥150 > ExitPPS ¥146) | 3,800 | 0 | 0 | 0.0% ✓ |
  | 5,000 | 5,225 | 3,800 | 1,425 | **741.9** | 14.84% |
  | 6,000 | 6,225 | 3,800 | 2,425 | **1,262.6** ✓ | 21.04% ✓ |
  | 10,000 | 10,225 | 3,800 | 6,425 | **3,344.9** | 33.45% |
  | 20,000 | 20,225 | 800 (B converts) | 19,425 | **7,460.7** ≈ ✓ | **36.89%** (doc says 36.95%) |
  | 50,000 | 50,225 | 800 | 49,425 | **18,983.1** | 37.97% |

- **Discrepancy summary**:
  - ¥5B row: doc 624.0M / 12.5% — wrong; correct **741.9M / 14.84%** if SO inflow included (consistent with §10.3.2 method). 624M only matches a "no-SO-inflow" model, making the table internally inconsistent with the §10.3.2 worked detail.
  - ¥10B row: doc 3,242.7M (32.4%) — wrong; correct **3,344.9M (33.45%)**.
  - ¥20B row: doc 7,460.4M is essentially right (rounds from 7,460.7M), but stated take-ratio 36.95% is wrong; correct **36.89%**. (See B-M-002 below.)
  - ¥50B row: doc 18,649.4M — wrong; correct **18,983.1M** (with SO inflow). Without SO inflow it would be 18,896.7M; doc value matches neither.
  - ¥11,442M cross-over ratio "35.4%" cannot be reproduced under either model.

- **Likely cause**: The author used at least two inconsistent assumption sets across the table rows (some rows with SO cash inflow, some without; some with rounding errors).
- **Recommendation**: Recompute the entire table with one consistent rule (recommended: SO ITM → exercise + cash inflow added to pool, matching §10.3.2). Replace stated values with the corrected column above.
- **Severity**: High (multi-row error in a flagship sensitivity analysis; up to ~17pt take-ratio error at low exit; numbers will be quoted by users).

---

## Medium Calculation Errors

### B-M-001: §10.1.3 T3 Series B post-money FDSO — arithmetic typo

- **File**: `04b_cap_table_mechanics.md`, §10.1.3, line 1335
- **Original calculation** as stated:
  ```
  19,208,333 × 13,000 / 8,440 = 29,587,479
  ```
- **Recomputation**: numerator (line 1334) is correct at 249,708,329,000; 249,708,329,000 / 8,440 = **29,586,294.91**.
- **Discrepancy**: stated 29,587,479 vs correct **29,586,295** — diff ≈ 1,184 shares (~0.004%). The error then echoes in lines 1336, 1342, 1359, 1361, 1374, 1382, 1436, but the percentages around it round-mask the error.
- **Likely cause**: manual division typo.
- **Recommendation**: Replace `29,587,479` with `29,586,295` in lines 1335, 1361, 1374, 1382, 1436.
- **Severity**: Medium (small absolute error, but the worked example is meant to "tie out exactly").

### B-M-002: §10.3.3 Founder take-ratio at ¥20B exit

- **File**: `04b_cap_table_mechanics.md`, §10.3.3 final paragraph, line 1609
- **Original**: "Founder の感覚: 38.41% 株式 → **36.95%** net cash (¥7,460.4M / ¥20,225M)"
- **Recomputation**: 7,460.4 / 20,225 = **0.36889 = 36.89%**, not 36.95%.
- **Recommendation**: Change "36.95%" to "36.89%".
- **Severity**: Medium.

### B-M-003: §3.4 monthly→annual churn table — rounding inconsistency at 4.0% row

- **File**: `02_saas_metrics.md`, §3.4, lines 416-422
- **Stated row**: 4.0% / 48.0% / **39.0%** / **-9.0pt**
- **Recomputation**: 1−(1−0.04)^12 = **0.38729 = 38.7290%**. Linear-vs-compound delta = **−9.27pt**, not −9.0pt.
- **Other rows**: 1.0/2.0/3.0/5.0% rows are within 0.05pt of stated values; only the 4.0% row is rounded inconsistently (rounded up to nearest whole instead of one decimal like the rest).
- **Recommendation**: Change 4.0% row to compound 38.7%, err -9.3pt.
- **Severity**: Medium (the section's whole point is that linear×12 is wrong; the corrected number must itself be tight).

### B-M-004: §11.3 Bass-model mini case — numbers don't match stated parameters

- **File**: `09_market_sizing.md`, §11.3, lines 1848-1856 (Bass mini case for AI writing tool)
- **Stated parameters**: p = 0.04, q = 0.5, m = 60,000 SMB customers
- **Stated table**:

  | Year | N(t) | Inc | Revenue ¥B |
  |------|------|-----|------------|
  | 1 | 2,400 | 2,400 | 0.26 |
  | 2 | 6,800 | 4,400 | 0.74 |
  | 3 | 16,200 | 9,400 | 1.75 |
  | 4 | 30,500 | 14,300 | 3.30 |
  | 5 | 45,800 | 15,300 | 4.95 |

- **Recomputation** with the closed-form Bass curve N(t) = m · (1−exp(−(p+q)t)) / (1 + (q/p)·exp(−(p+q)t)):

  | Year | N(t) (correct) | Inc (correct) |
  |------|----------------|---------------|
  | 1 | 3,022 | 3,022 |
  | 2 | 7,555 | 4,533 |
  | 3 | 13,854 | 6,300 |
  | 4 | 21,740 | 7,886 |
  | 5 | 30,416 | 8,676 |

- **Discrepancy**: All five rows are wrong with the stated p, q, m. At Year 5, stated 45,800 vs correct **30,416** — error of **+50.6%**. Backsolving from the stated values: no single (p, q) pair with m = 60,000 reproduces the table. The table appears to be hand-fabricated (or computed with different unstated parameters).
- **Adjacent issue** (line 1845): SAM = "1.2M × ¥36K (avg 3 seats) = 130B". The stated arithmetic 1.2M × ¥36K = ¥43.2B, not ¥130B. The "(avg 3 seats)" parenthetical is doing implicit work — the actual computation must be 1.2M × (¥36K × 3) = ¥129.6B ≈ 130B. Notation is ambiguous; rewrite as `1.2M × (¥36K × 3 seats) = 130B` or `1.2M × ¥108K = 130B`.
- **Recommendation**: Either (a) keep p=0.04, q=0.5, m=60,000 and replace the table with the corrected N(t) values above (and recompute Revenue × ARPU); or (b) state the actual parameters used (likely something like p≈0.07, q≈0.6 or m=80,000+ to reach 45,800 at Y5). Also fix the SAM formula notation.
- **Severity**: Medium (primary teaching example for Bass; visible error of >50% at Y5 will be quoted by users; rev impact propagates to ¥4.95B vs corrected ~¥3.28B).

### B-M-005: §17.2.8 IRR/MOIC sensitivity table — internally inconsistent

- **File**: `08_investment_thesis.md`, §17.2.8, lines 1706-1710
- **Stated rows**:
  - Worst: MOIC 1.6x / IRR 12%
  - Base: MOIC 11x / IRR 45%
  - Best: MOIC 25x / IRR 70%
- **Recomputation** (5-year holding period; pure MOIC↔IRR identity IRR = MOIC^(1/5) − 1):
  - 1.6x → IRR = **9.86%** (doc 12%)
  - 11x → IRR = **61.54%** (doc 45%)
  - 25x → IRR = **90.37%** (doc 70%)
  - Conversely: IRR 12% → MOIC = **1.76x** (doc 1.6x); IRR 45% → MOIC = **6.41x** (doc 11x); IRR 70% → MOIC = **14.20x** (doc 25x)
- **Discrepancy**: All three rows are internally inconsistent on the simple MOIC/IRR identity. The bias is: stated MOIC implies *higher* IRR than stated IRR (or stated IRR implies *lower* MOIC).
- **Possible explanations** (all undocumented in the case):
  - Future dilution rounds reduce realized share at exit → real MOIC < headline MOIC. Author may have privately discounted but not stated the assumption.
  - 7-year hold (per §17.2.11 line 1740 "5-7 年") rather than 5: at 7 years, 1.6x → 6.97% IRR (still not 12%); 11x → 41.7% IRR (close-ish to 45%); 25x → 57.5% IRR (close-ish to 70%). 7-year base case partially fits but not perfectly.
- **Recommendation**: Either (a) state the dilution path / hold period explicitly, or (b) recompute with consistent inputs. Preferred fix: state hold = 7 years and use the 7y formula (1.6x→7%, 11x→42%, 25x→57.5%) and adjust the other column; or redo MOIC values from a stated post-dilution stake.
- **Severity**: Medium (it's a recommendation-grade sensitivity table; users quoting either column will be off).

---

## Low Calculation Errors / Typos

### B-L-001: §10.1.3 line 1342 — "新 Pool 追加" arithmetic typo

- **File**: `04b_cap_table_mechanics.md`, §10.1.3, line 1342
- **Stated**: "新 Pool 追加 = 3,550,497 − 1,625,000 = 1,925,497 株"
- **Recomputation**: With B-M-001 fix, the correct values are 3,550,355 − 1,625,000 = **1,925,355**. The exact off-by-1,184 (or 142 once you allow proper rounding) follows from B-M-001 and is not a separate error per se, but the computation also assumes a specific rounding stage.
- **Severity**: Low (downstream of B-M-001).

---

# Calculations Verified Correct (priority sample)

## File 04b_cap_table_mechanics.md

- §1.3 TSM example (line 92-95): 1,000,000 × (1 − 200/1,000) = 800,000 ✓
- §2.3 Option Pool Shuffle closed-form (lines 246-264): F0=9M, T=10%, PMV=$9M, INV=$3M ⇒ X=13,846,154; Y=1,384,615; PPS=$0.8667; Z=3,461,538; founder/investor/pool = 65/25/10% ✓
- §4.5.2 Broad-based WA anti-dilution (lines 510-522): NewConvPrice = $1.00 × 12M/14M = $0.857; ratio = 1.1667 ✓
- §6.2.1 cross-over (lines 798-803): $10M / 0.20 = $50M ✓
- §6.2.2 participating Total at $100M exit (lines 818-823): $10M LP + 0.20×$90M = $28M ✓
- §6.3 multi-class waterfall at $50M exit, A participating + B converts (lines 848-893): A=$14M, B=$11.25M, C=$24.75M, sum=$50M ✓
- §6.5 cross-over table (lines 930-936): all five rows ✓
- §6.6.3 SO Net at $80M exit (lines 962-964): 1M × ($4-$0.50) = $3.5M ✓
- §10.1.2 T2 Series A (lines 1271-1305): X=20,833,333; new pool=3,125,000; PPS=¥115.2; A new=5,208,333; pcts 48/12/25/15 ✓
- §10.3.2 ¥6B exit waterfall (lines 1491-1551): ExitPPS=¥230.4; SO Net=¥120.6M; B chooses LP at ¥3B; LP-stack=¥3,800M; residual=¥2,425M; founder=¥1,262.6M; ratio=21.0% ✓
- §10.3.3 ¥20B exit (lines 1553-1607): cash pool=¥20,225M; B converts at ¥5,303M > ¥3,000M LP; founder=¥7,460.4M ✓ (only the 36.95% take-ratio = B-M-002 is an issue)
- §10.3.4 cross-over for B at ¥11,442M: 3000/0.2622 = 11,440 ✓ (within rounding)

## File 04a_convertible_and_terms.md

- §2.6 Step 3 SAFE2 sub-calc (lines 308-313): Series A PPS=$1.50 (T=10M), SAFE2 conv=$1.20, SAFE2=250,000 sh, x_2=2.5%; founder pct=55% ✓
  - Note: line 317 then shows T=10.91M and PPS=$1.375 once founder count is held at 6M — internally consistent with the "T=Founder/0.55" identity.
- §3.6 J-KISS example (lines 432-468): pre-FD=900K; PPS_A=¥888.89; cap-based=¥555.56 < discount-based=¥711.11 ⇒ ¥555.56 used; J-KISS=90,000 sh; A=225,000 sh ✓

## File 02_saas_metrics.md

- §3.4 churn table 1.0 / 2.0 / 3.0 / 5.0% rows ✓ (only 4.0% row is rounded inconsistently — see B-M-003)
- §4.3 CAC Payback example (lines 610-612): w/o GM 12mo, w/ GM 16mo ✓

## File 06_three_statement.md

- §3.4 Working Capital schedule (lines 274-296): AR/Prep/AP/Accr/NWC values match (rounding ±1) ✓; ΔNWC +456 / +691 / +830 ✓ (Y2 ΔNWC = 1346−890 = 456, Y3 = 2037−1346 = 691, Y4 = 2867−2037 = 830 — all tie)

## File 05_valuation_wacc.md

- §1.11 DCF mini-case (lines 319-475):
  - Re_mature = 4.0% + 1.10×4.23% + 0.2% + 1.5% = **10.35%** → 10.4% ✓
  - All segmented mid-year DFs (Y1=0.9308 to Y10=0.3303, TV DF=0.3144) reproduce ✓
  - PV(FCFF) sum = 140.40 ✓; TV(Gordon) = 80.7 × 1.02 / (10.4%−2.0%) = 979.93 ≈ 980 ✓; EV = 448.65 ≈ 448.5 ✓; Equity = 478.65 ≈ 478.5 ✓
- §2.10 Comps mini-case (lines 600-641):
  - EV/NTM Rev median 2.45 ✓, mean 2.6 ✓
  - EV/NTM GMV median 0.335 → rounded to 0.34 ✓
  - NTM Rev = 6.4 × 1.40 = 8.96 ≈ 9.0 ✓; NTM GMV = 80 × 1.35 = 108 ✓
  - EV(Rev) = 2.45 × 9.0 = 22.05 ≈ 22.0 ✓; EV(GMV) = 0.34 × 108 = 36.72 ≈ 36.7 ✓
  - Take-rate-adj GMV mult = 0.34 × (8/11) = 0.2473 → 0.25 ✓; EV = 0.25 × 108 = 27 ✓
- §4.5 First Chicago VC method backsolve (lines 790-814):
  - E[Exit] = 0.20×30 + 0.50×10 + 0.30×1 = 11.3 ✓
  - PV at IRR 50% = 11.3/(1.5^5) = 1.488 ≈ 1.49 ✓
  - Pre-money = 1.49 − 0.50 = 0.99 ≈ 1.0 ✓
  - 500/1490 = 33.56 ≈ 33.6% ✓
  - Sensitivity: PV at IRR 40% = 11.3/(1.4^5) = 2.10 ✓; Best=30% E[Exit] = 14.2 → PV = 1.87 ✓; Best exit ¥40B → E[Exit] = 13.3 → PV = 1.75 ✓

## File 11_debt_financing.md

- §2.4.2 Warrant value (lines 540-541): 750K/8 = 93,750 sh; × $5.55 = $520,312 ≈ $520K; 5.2% of $10M facility ✓
- §2.4.3 Effective cost (line 555): 8.80% + (520K/10M/4y) = 8.80% + 1.30% = **10.10%** all-in ✓
- §2.6 PIK example (lines 587-595): $30M × 1.12^5 = $52.87M ≈ $52.9M; 76.2% increase ✓
- §2.7 Worksheet (lines 614-621): SOFR 4.30 + Spread 7.50 + OID 0.25 + Closing 0.25 + Backend 0.75 + Warrant 1.13 = **14.18%** ✓; after-tax 9.22% (= 14.175 × 0.65 = 9.21, rounds to 9.22) ✓
- Case 1 §1-C effective cost (lines 1553-1557): coupon 11.80 + 0.33 + 0.67 + 1.60 = **14.40%** ✓; after-tax 28% = 10.37% ✓
- Case 2 §2-B Borrowing Base (lines 1597-1600): 2.5×0.95×0.85 + 4×0.80×0.50 = 2.0188 + 1.6 = **3.62M**, capped at 3M ✓
- Case 2 §2-C interest (lines 1610-1612): Y1 2.0 × 8.30% = $166K ✓; Y1 unused 1.0 × 0.50% = $5K ✓; Y2 2.5 × 8.30% = $207.5K → $208K ✓; Y3 2.8 × 8.30% = $232.4K → $232K ✓
- Case 2 §2-D FCCR (line 1617-1618): (2.0 − 0.3) / (0.171 + 0 + 0.05) = 1.7 / 0.221 = **7.69x** ✓

## File 09_market_sizing.md

- §3.2.4 Bass peak time (line 591): with p=0.03, q=0.4, t* = (1/0.43)·ln(13.33) = **6.024 years ≈ 6.0** ✓; q/p = 13.33 ✓; analytic check N(t*)/m = (q-p)/(2q) = 0.4625 ✓

## File 08_investment_thesis.md

- (Investment thesis is mostly qualitative; only one quantitative sensitivity table in §17.2.8 was checked — see B-M-005.)

---

# Ambiguous Cases (前提が不明で再計算困難)

- §2.6 (04a) full SAFE/Series A connected solve: doc shows partial step but skips the actual closed-form. It uses "T=10M assumed" then later "T≈10.909M" once founder shares are pinned at 6M. Both representations are individually consistent but the worked example doesn't continue with the corrected T=10.909M to redo SAFE 2 conversion at the new PPS. This is pedagogical simplification rather than an error — flagged for the reader's awareness.
- §17.2.8 (08) MOIC↔IRR mismatch (B-M-005): could be explained by a stated dilution path or longer hold period, neither of which is present in the case body. Marked as Medium error pending the author clarifying the intended assumption.
- §11.3 (09) Bass parameters → table values: cannot back-solve to a clean (p, q, m) triple matching the stated table; treated as an arithmetic/parameter mismatch rather than ambiguity.
- §10.1.2 cap table %s (04b, line 1305): doc states "100%" sum but rounded to 0.01% it is 100.00% only with the corrected X=29,586,295 (B-M-001). With the stated X=29,587,479 the column sum is 100.0040%. Minor.

---

# Files NOT covered in this audit pass

- **00_design_guidelines.md** (2,254 lines): mostly typography / color tokens / no calculations
- **01a_modeling_standards.md** / **01b_integrity_and_anti_patterns.md**: standards & checklists, few worked numbers
- **03_business_models.md**: mostly typology / qualitative
- **07_japan_specifics.md**: tax/legal narrative
- **10_modeling_craft.md**: best-practice prose; some pseudo-code

If full coverage of these is required, expect ~10-20 additional minor checks (mostly statutory rates, threshold tables, formula presentation).

---

# Aggregate observations

1. **Core formulas are clean.** The closed-form Option Pool Shuffle, broad-based WA anti-dilution, basic waterfall, segmented mid-year DCF, Bass peak, working-capital schedule, J-KISS conversion, comps medians, PIK compound, debt effective-cost decomposition, FCCR — all reproduce to the digit (modulo standard rounding).
2. **Errors cluster in story-style "case studies".** Specifically: 04b §10.3.5, 09 §11.3, 08 §17.2.8. These appear to be hand-computed without a model file behind them, then transcribed. They do not match the formulas printed elsewhere in the same documents.
3. **No critical errors.** No formula reversal, sign error, or fundamental conceptual mistake was detected in priority sections.
4. **Typical pattern**: small typos (B-M-001 ~0.004% off, B-M-002 ~0.06pt off) that propagate through a long story; mild rounding inconsistencies (B-M-003); unmatched parametric mini-cases (B-M-004, B-M-005).
5. **Recommended fix order**: B-H-001 (largest user-visible impact) → B-M-004 (Bass case is a high-traffic teaching example) → B-M-005 (recommendation-grade IRR/MOIC) → B-M-001/002/003 (small typos, fast fixes).
