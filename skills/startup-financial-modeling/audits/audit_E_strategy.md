# Audit E: Strategic Clarity

**Status**: COMPLETE (initial pass).
**Scope**: 14 reference files under `skills/startup-financial-modeling/references/` (24,681 lines total).
**Method**: Inspect each file for trade-off articulation, decision-framework completeness, dual-perspective coverage (founder vs investor / debt vs equity / US vs JP / conservative vs aggressive), rationale depth ("why"), unresolved conflicting recommendations, stakeholder clarity, business-strategy linkage, downside / risk surfacing, business-model fit, stage fit, JP-context integration, implementability, and failure-mode coverage.

Severity legend:
- **Critical (E-C)**: Strategic ambiguity that lets Claude give a directionally wrong recommendation (wrong instrument, wrong stage, wrong stakeholder advice).
- **High (E-H)**: Trade-off / rationale missing in a place where multiple legitimate answers exist; Claude likely to default to one without surfacing the alternative.
- **Medium (E-M)**: "Why" depth shallow but recommendation directionally safe; or stakeholder perspective implicit but inferable.
- **Low (E-L)**: Phrasing-level ambiguity, easily clarified with one sentence.

---

## Summary

- Total strategic recommendations audited: ~330 (sampled across 14 files; not exhaustive).
- Clearly articulated (rationale + trade-off + stakeholder split): ~170.
- Ambiguous (rationale or trade-off implicit / missing): ~110.
- Conflicting (two legitimate answers without resolution rule): ~50.
- Issues recorded below: 92 (5 Critical, 26 High, 41 Medium, 20 Low).

Severity distribution skews to High/Medium because the corpus is methodologically careful: most recommendations are directionally defensible, but the "why" / "when this fails" / "stakeholder perspective" layer is unevenly delivered. Critical issues cluster around cross-file silences (e.g., no global decision tree for choosing among the 14 files; no master rule for when convertible vs priced round vs venture debt; no single owner for "kill the company" thresholds).

---

## Critical Strategic Ambiguities (E-C-xxx)

### E-C-001: No master decision tree connecting `04a` (convertible) ↔ `05` (VC method) ↔ `08` (stage thesis) ↔ `11` (debt)
- **Files**: `04a_convertible_and_terms.md` §1.4 "転換型と優先株 (priced round) の境界線"; `08_investment_thesis.md` §3.1 ステージ別評価軸; `11_debt_financing.md` §1.0 商品横断比較; `05_valuation_wacc.md` §17.1 標準フロー.
- **Issue**: Each file gives a stage→instrument table, but they do not cross-reference. `04a` says "Seed = SAFE / J-KISS, Series A = priced." `11` says "Series A後 ARR ≥ $2M で venture debt 適用." `05` says "Pre-revenue は Berkus / Scorecard, Series A は VC method." There is **no single composite decision tree** that asks "given stage X, ARR Y, geography Z, capital need W, which instrument and which valuation method?"
- **Why it matters**: Claude given a Series A pre-revenue Japan startup may pick J-KISS (from 04a stage table) while simultaneously recommending venture debt (from 11) without realizing the latter requires ARR ≥ $2M. The two recommendations are individually defensible but jointly incoherent.
- **Claude misjudgment scenario**: User: "We're a 6-month-old Japanese AI startup, no revenue, raising bridge before Series A." Claude pulls "use J-KISS" from `04a` and "venture debt for runway extension" from `11` without surfacing that venture debt is unavailable pre-revenue.
- **Recommendation**: Add a top-level routing matrix in `00_design_guidelines.md` or a new `00b_decision_tree.md` keyed by (stage × revenue × business model × geography) → (which file is primary, which secondary, which inapplicable).

### E-C-002: Pre-money vs Post-money SAFE — recommendation appears neutral but is actually founder-hostile by default
- **File**: `04a_convertible_and_terms.md` §2.2.3 数値で比較; §2.7 投資家観点と創業者観点.
- **Issue**: §2.2.3 numerically demonstrates that post-money SAFE shifts dilution onto founders (8.20% vs 10.00% investor share). §2.7 then notes "post-money の方が投資家有利、pre-money の方が創業者有利". But the file states "**post-money SAFE (2018 〜 現行)**" as if it were the operative standard, without a recommendation rule for **when a founder should push back to pre-money** or **what discount premium justifies accepting post-money**.
- **Why it matters**: YC made post-money the de-facto standard, but a sophisticated founder representing themselves should know "I will accept post-money cap only if cap is N% higher than pre-money equivalent." The file lacks that conversion factor / pushback strategy.
- **Claude misjudgment scenario**: Founder user: "Investor offered post-money SAFE at $10M cap. Is this fair?" Claude says "yes, post-money SAFE is current YC standard" without pointing out the founder should ask for ~$11–12M post-money to economically equal $10M pre-money assuming typical option-pool top-up.
- **Recommendation**: Add §2.2.4 "Negotiation rule: post-money cap should be roughly (pre-money cap) × (1 + expected SAFE stack + ESOP top-up) to be founder-neutral. If investor refuses, the founder is taking ~2–4% additional dilution per $1M of subsequent SAFE issuance."

### E-C-003: Stage-appropriate discount rate vs survival probability — explicit warning, but no chosen default
- **File**: `05_valuation_wacc.md` §1.4.5; §15.8.
- **Issue**: §1.4.5 gives a stage discount table (Seed 50–70% IRR ... Mature 10–15% WACC). §15.8 explicitly warns "**stage-appropriate discount と probability-weighting を同時に使うのは原則 NG (バイアス重複)**". But neither section says **which one Claude should default to** when given a generic startup valuation request, nor under what circumstances each is preferred.
- **Why it matters**: This is the single most consequential modeling choice in startup valuation; getting it wrong produces 2–5x valuation errors.
- **Claude misjudgment scenario**: User asks Claude to value a Series B SaaS. Claude builds DCF with mature WACC 10% AND multiplies CF by survival probabilities (because it read both §1.4.5 and §15.8 but didn't pick one), producing ~50% understatement of value.
- **Recommendation**: Add a default rule: "Pre-revenue / Series A: use stage-appropriate discount (no survival weighting). Series B / C with PMF: use mature WACC + survival probability for tail. Late-stage / pre-IPO: mature WACC, no survival weighting."

### E-C-004: Liquidation preference treatment in valuation handed off but not concluded
- **Files**: `04a_convertible_and_terms.md` §7; `04b_cap_table_mechanics.md` (waterfall); `05_valuation_wacc.md` §13.2 PWERM/OPM/Hybrid; `08_investment_thesis.md` §1.10.
- **Issue**: `04a` thoroughly explains 1x non-participating vs participating vs capped participating. `05` says use OPM/PWERM/Hybrid for Level 3 fair value. But there is no **single normative rule for valuing common stock (founder/employee) when 3+ preferred series stack with different multiples and cap structures**. The hybrid method described in `05` §13.2 is one of three; the choice criterion ("near-IPO use PWERM, otherwise OPM") is hand-wavy.
- **Why it matters**: Founder secondary, 409A pricing, divorce settlements, and tax planning all hinge on this. Claude pulling the wrong allocation method can be off by 30–50% on common stock value.
- **Claude misjudgment scenario**: Series C company with 1x NP Series A, 1.5x participating Series B, 1x NP Series C asks for common-stock 409A. Claude does naive "post-money / fully diluted" without OPM, producing a strike price 2–3x higher than defensible.
- **Recommendation**: Add a worked Series-C example showing how OPM allocation diverges from naive pro-rata, and a hard rule: "If any preferred has participation, multiple preference, or 1.x ratchet, OPM/PWERM is required, not optional."

### E-C-005: Kill criteria scattered across files; no master "company is dead" threshold
- **Files**: `08_investment_thesis.md` §3.3, §10.3; `11_debt_financing.md` §1.1.7 typical failures; `02_saas_metrics.md` (implicit via Burn Multiple etc.); `09_market_sizing.md`.
- **Issue**: `08` §3.3 has stage-by-stage kill criteria for VCs ("NRR < 90%, growth < 50% at Series A"). `08` §10.3 has Lean Startup pivot/persevere/kill. But neither file integrates the founder's perspective: "from the founder's seat, when do I voluntarily kill?" The investor-side kill is "stop putting capital in"; the founder-side kill is "voluntarily liquidate before insolvency to preserve any reputation / chance of next attempt." These are different decisions with different thresholds.
- **Why it matters**: An advisor agent that conflates "VC kills the deal" with "founder should shut down" will give catastrophically wrong advice. A still-funded company with 9 months of runway and no PMF is not dead from the VC's sunk-cost view but should arguably be wound down.
- **Claude misjudgment scenario**: Founder asks "should I shut down? Runway = 5 months, no PMF, NRR = 70%." Claude pulls the VC kill criteria from `08` and says "yes, terminal." But the founder may have a strategic exit (acquihire) that VC kill thresholds don't capture.
- **Recommendation**: Add `08` §10.4 "Founder-side wind-down decision tree": (a) cash position vs trailing 6mo burn, (b) realistic acquihire valuation, (c) employee severance + retention runway, (d) post-shutdown reputational ceiling.

---

## High Issues (E-H-xxx)

### Trade-off / decision-framework gaps

#### E-H-006: SAFE vs Convertible Note — when is the "debt-vs-equity-like" distinction load-bearing?
- **File**: `04a_convertible_and_terms.md` §4.4 "SAFE との比較".
- **Issue**: Table compares the two on legal form, interest, maturity, accounting. But the practical decision rule "use Note when investor demands creditor protection in distressed scenarios; use SAFE when cap-table simplicity dominates" is implied, never stated.
- **Recommendation**: Add explicit "Decision rule: choose Note if (a) investor is risk-averse and demands maturity, (b) state/jurisdiction restricts SAFE enforceability, (c) you are in a structured down-round where seniority matters. Otherwise SAFE."

#### E-H-007: Cumulative dividend acceptance — when does it become a debt-killer?
- **File**: `04a_convertible_and_terms.md` §8.3.
- **Issue**: "創業者は Non-cumulative で柔軟性確保." But cumulative 8% over 5+ years compounds to a 1.4–1.5x liquidation overhang — material. The doc doesn't say at what dividend rate × hold period combination cumulative becomes "effectively a debt convert" and should be rejected.
- **Recommendation**: Add quantitative threshold: "Cumulative dividend > 6% combined with hold > 4 years approximates 1.3x liquidation overlay; founder should treat this as a 1.3x participating preferred for negotiation purposes."

#### E-H-008: Anti-dilution ratchet — Full Ratchet rejection rule lacks the "what if forced" branch
- **File**: `04a_convertible_and_terms.md` §9.3, §16.3.
- **Issue**: "Full Ratchet → 創業者は強く拒否" is correct but unhelpful when a distressed startup has only one investor offering Full Ratchet and refusing the term means the company dies. There is no fallback rule like "if Full Ratchet is non-negotiable, demand a sunset clause (e.g., expires at next $X round) and a carve-out for ESOP top-up of $Y."
- **Recommendation**: Add "Cannot-refuse" mitigation set: sunset, carve-outs, conversion to weighted-average after milestone.

#### E-H-009: J-KISS post-money cap iterative computation — implementation hazard not flagged
- **File**: `07_japan_specifics.md` §3.3.2 "post-money cap の正確な計算"; §14.4 reference Python.
- **Issue**: The note "post-money cap の場合は分母に転換後株式数を含むため反復計算" appears once; the worked example in §3.3.2 silently uses the pre-money formula. A non-expert Claude user will miss this and compute a wrong dilution by 5–20%.
- **Recommendation**: In every J-KISS worked example, render BOTH the simplified and iterative versions side-by-side, with a "Use iterative when N J-KISS overlap or when Cap is near Series A pre-money" rule.

#### E-H-010: Choice of valuation method by stage — rule is offered but not defended against alternatives
- **File**: `05_valuation_wacc.md` §17.1.
- **Issue**: "Pre-seed → Berkus / Scorecard / VC method." But the literature also supports "use VC method exclusively, and use Berkus only as a triangulation tool." The file recommends triangulation but doesn't pick a hierarchy of weight (e.g., "VC method 60%, Berkus 25%, Scorecard 15%"). Claude will treat all three equally and average them, which dilutes the most-defensible method.
- **Recommendation**: Add weight defaults per stage with rationale.

#### E-H-011: Terminal Value — Gordon vs Exit Multiple choice not resolved
- **File**: `05_valuation_wacc.md` §1.6, §1.11.
- **Issue**: §1.11 explicitly shows Gordon ($980) vs Exit Multiple ($2,232) diverging by 2.3x, then says "両者の中点 ≈ 1,600 または range." This is exactly the "It's complicated" pattern flagged in the audit prompt: the corpus surfaces the divergence but doesn't supply a tiebreaker. A user with no judgment will pick the average, which is not theoretically defensible.
- **Claude misjudgment scenario**: Claude reports an EV range of $448M–$1,000M+ to a CFO preparing a board package and the CFO has no basis to pick.
- **Recommendation**: Add "Tiebreak rule: if Y10 is genuinely steady-state, Gordon governs and Exit Multiple is sanity check. If Y10 still has visible >5%pt growth premium, extend forecast 5 years and re-test; do not average."

#### E-H-012: Comp set selection — geographic filter rule
- **File**: `05_valuation_wacc.md` §2.2.
- **Issue**: "Geography: 主要市場の重複" — but a Japanese SaaS with 100% domestic revenue has comp set including US-listed Snowflake/Datadog (the file's example for a Japan B2B SaaS). The implicit assumption is that SaaS is globally fungible; not stated.
- **Recommendation**: State explicitly: "For domestic-revenue companies in markets with thin local comparable depth (Japan, Brazil, India), use US public comps with a country-adjusted CRP discount, not raw multiples. Apply a 20–35% multiple discount for Japan."

#### E-H-013: Damodaran SBC treatment — recommended position not labeled "controversial"
- **File**: `05_valuation_wacc.md` §15.5.
- **Issue**: "Damodaran 主張 (推奨): SBC は真の希薄化コスト... 加算戻しはしない." But sell-side bankers and most public SaaS analysts add back SBC. The recommendation is correct but isolating; a user comparing Claude's valuation to a sell-side comp will see a 30–40% gap with no explanation.
- **Recommendation**: Add "**Disclosure rule**: when reporting valuation, always show both 'SBC-as-cost' and 'SBC-added-back' versions, and explain that the SBC-added-back version is the market convention but the SBC-as-cost version is the theoretically correct one."

#### E-H-014: WACC — stage-segmented vs constant choice
- **File**: `05_valuation_wacc.md` §1.11 "WACC 構築".
- **Issue**: Worked example uses three-stage WACC (15.4 → 12.5 → 10.4%), then notes "全 mature WACC 一定 (10.4%) に変えると EV ≈ $610M (+27%). 本ケースは stage premium 反映で保守的." But there's no rule for which choice is appropriate when. The 27% delta is huge.
- **Recommendation**: Add "Use stage-segmented WACC when modeling for pre-IPO IC. Use mature WACC when comparing against public-comp multiple. Never present both without explaining."

#### E-H-015: Net Revenue Retention threshold by segment — SMB vs Mid vs Enterprise — but not by business model
- **File**: `08_investment_thesis.md` §4.1.2.
- **Issue**: NRR thresholds are split by SMB / Mid / Ent, which is a customer-size cut. But NRR economics differ massively by business model (vertical SaaS vs horizontal SaaS vs PLG vs marketplace). PLG SaaS like Notion / Figma have radically different NRR mechanics than Salesforce-like Enterprise sales.
- **Recommendation**: Add a second cut (PLG / SLG / Hybrid) to the NRR table, or add a footnote: "PLG NRR is typically lower (best-in-class 110% vs 125% for Enterprise SLG) because expansion happens via seat sprawl rather than ARR upsell."

#### E-H-016: Burn Multiple thresholds — "OK at 1.5–2.0x" doesn't account for revenue stage
- **File**: `08_investment_thesis.md` §4.1.7.
- **Issue**: Stage-by-stage Burn Multiple thresholds are given (Seed < 3x, A < 2x, ...), but the underlying Sacks framework is `Net Burn / Net New ARR`. At pre-revenue, Net New ARR ≈ 0, making Burn Multiple infinite. The doc doesn't say "Burn Multiple is meaningless pre-revenue; use absolute burn × runway months instead."
- **Recommendation**: Add "Burn Multiple is undefined when ARR < $100K. Use 'absolute monthly burn / months to cash-out' for pre-revenue."

#### E-H-017: Marketplace take-rate — "高すぎれば disintermediation リスク" not quantified
- **File**: `03_business_models.md` §1.4 "投資判断ロジック観点".
- **Issue**: "高すぎれば disintermediation リスク" — but Bill Gurley's "rake too far" essay puts the ceiling at 15% for marketplaces. The file's own Take Rate table shows ride-hail at 22–28% gross. So either the threshold is wrong or the recommendation is wrong; the conflict is unresolved.
- **Recommendation**: Reconcile: "Gross take rate >25% combined with high-frequency relational transactions (homecare, tutoring) → disintermediation risk. Gross take rate >25% in low-frequency / long-tail / regulated markets (hotels, ride-hail) → defensible because the customer cannot easily reroute."

#### E-H-018: Cohort GMV retention — Year 2 100%+ benchmark not differentiated by frequency
- **File**: `03_business_models.md` §1.2.
- **Issue**: "Best-in-class: Year 2+ で 100% 超" applies to all marketplaces, but the bar should be much higher for high-frequency (Uber, DoorDash) than low-frequency (Airbnb 1–2 trips/year). 100% retention in low-frequency is excellent; 100% in food delivery is mediocre.
- **Recommendation**: Stratify by transaction frequency: "Frequency >12/year: Year 2 retention >120% required. Frequency 1–4/year: 100% is best-in-class."

#### E-H-019: Hardware razor-blade — "subscription churn に脆弱" but no churn threshold
- **File**: `03_business_models.md` §4.4.1.
- **Issue**: "ハードは赤字でサブスクで黒字化モデルは subscription churn に脆弱" — but no rule for which churn level breaks the model. Peloton survives at 1.5–2% monthly. At what churn does the unit economic case fall apart?
- **Recommendation**: Add "Razor-blade falls below break-even when Hardware GM loss × probability > Subscription monthly contribution × (1 / churn rate). Rule of thumb: hardware deficit per unit must be recovered in <(1/monthly churn × 0.7) months."

#### E-H-020: Bio rNPV — discount rate 10–13% conflicts with stage-appropriate IRR
- **Files**: `03_business_models.md` §5.1; `05_valuation_wacc.md` §1.4.5.
- **Issue**: `03` says "discount rate 10–13% が pharmaceutical 慣行" for rNPV. But `05` §1.4.5 says Seed-stage requires 50–70% IRR. A pre-clinical bio is functionally Seed-stage. So which discount rate? The PoS in rNPV already encodes failure probability, so 10–13% may be the right answer — but this is exactly the point that needs explicit explanation.
- **Recommendation**: Add to `03` §5.1: "rNPV uses 10–13% because PoS already absorbs failure risk. Do NOT compound stage-IRR on top of rNPV; that would double-count the bio failure rate." Cross-link to `05` §15.8.

#### E-H-021: Real Options for Bio — Decision Tree DCF gives -$24.6M, Real Options gives +$17.3M, no rule for which to use in IC
- **File**: `05_valuation_wacc.md` §8.5.
- **Issue**: The Bio mini-case shows Real Options flipping a "no-go" DCF to a "go." But Real Options is often academic; many IC committees won't accept the σ-driven option value as decision-relevant. The file doesn't say when Real Options *replaces* DCF vs when it's only a sanity check.
- **Recommendation**: Add rule: "Use Real Options as the primary number when (a) abandonment is structurally available (contract / regulatory), (b) σ has empirical basis (peer stock-vol or trial-outcome variance), (c) optionality is asymmetric. Otherwise treat as sensitivity."

#### E-H-022: Lifecycle valuation framework — stage transitions not flagged for discontinuity warning
- **File**: `05_valuation_wacc.md` §12.4.
- **Issue**: "Stage 越境点で valuation discontinuity (margin 急変) が発生しやすい" — but no test for whether the user's model has a smooth or jagged transition. A model jumping from -20% margin to +25% margin in a single year is a red flag, but the doc doesn't quantify "jagged."
- **Recommendation**: Add "Margin step rule: if year-over-year EBIT margin change exceeds ±5pp during transition, the model needs a 2-year smoothing layer or a justification (e.g., one-time cost cut, milestone IPO bonus)."

#### E-H-023: Japanese ESOP — 信託型 SO 2023 国税庁見解 — what's the migration path for existing companies?
- **File**: `07_japan_specifics.md` §2.7.4.
- **Issue**: "信託型 SO は事実上利用が困難に" with "既導入企業は税制適格 SO への切替・現金清算等の対応." But the migration path itself is not described. A startup with 200 employees on signal-trust SO from 2021 is left without operative guidance.
- **Recommendation**: Add a 4-step migration playbook: (a) snapshot current beneficiary list, (b) communicate the tax change, (c) issue replacement 適格 SO with equivalent value, (d) cash-settle for those over 1,200万円 limit.

#### E-H-024: Resource capital ratio — capital adequacy "規制下限 +200bps" but which regulator?
- **File**: `08_investment_thesis.md` §4.3.
- **Issue**: "Capital adequacy ratio: 規制下限 +200bps" applies for fintech lenders, but the regulator differs by jurisdiction (Basel III for banks, prudential supervisor for non-bank), and the threshold for "adequate" varies by the lender's product mix. The single threshold collapses too much.
- **Recommendation**: Stratify by lender type (bank charter / state-licensed lender / partner-bank arrangement) and reference the controlling regulator.

#### E-H-025: Country exposure (λ) for CRP — "sales 地理 で按分" — but for B2B SaaS with global customers?
- **File**: `05_valuation_wacc.md` §1.4.1.
- **Issue**: A B2B SaaS sells to a US-incorporated subsidiary of a German manufacturer that operates plants in Mexico — what is the country exposure? The doc says "sales 地理" but this metric is ambiguous for multi-national customers.
- **Recommendation**: Add rule: "Use the billing country of the contracting entity, not the operating country of the end-user. For risk-sensitive valuation, weight by where the cash settles, not where the value is consumed."

#### E-H-026: Implied ERP vs Historical ERP choice
- **File**: `05_valuation_wacc.md` §12.1.
- **Issue**: "Implied ERP を使う理由: Forward-looking, self-consistent" — clear rationale. But banker shops still use historical ERP. The doc doesn't tell Claude which to use when defending a model in a sell-side context vs an internal IC.
- **Recommendation**: Add "Default rule: use implied ERP for IC. Use historical ERP only when the audience explicitly demands it (some bank IBs, some regulators)."

#### E-H-027: Founder secondary timing — "Series B 以降" but no founder-equity floor
- **File**: `04a_convertible_and_terms.md` §15.4.
- **Issue**: "通常 $1〜5M 規模" — but the structural constraint is that founder equity post-secondary should be enough to maintain operating motivation. The doc doesn't say "after secondary, founder ownership must remain >X% to avoid governance dilution from cap table re-engineering."
- **Recommendation**: Add "Founder secondary floor: post-secondary, founder common+vested-options should remain ≥10% to preserve normal voting/governance and avoid signaling 'founder is checking out.'"

#### E-H-028: SaaS Rule of 40 — "discount tier" implies multiple penalty but no explicit number
- **Files**: `08_investment_thesis.md` §4.1.8; `05_valuation_wacc.md` §10.3.
- **Issue**: `05` §10.3 says "Each 10pt R40 improvement → +1.1× multiple"; `08` §4.1.8 says "Rule of 40 達成は valuation premium 約 +121%." But "+121%" and "+1.1×" appear independently with different methodologies; a user can't reconcile them.
- **Recommendation**: Standardize: pick one (the +1.1× per 10pt is more granular and Bessemer-source) and consistently use across the corpus.

#### E-H-029: Convertible Note vs SAFE — US state law variation
- **File**: `04a_convertible_and_terms.md` §4.1.
- **Issue**: "SAFE が使えない州法環境" — without specifying which states. California and Delaware are SAFE-friendly; some states have ambiguity. A founder advised to "use SAFE" without state context can hit unenforceability later.
- **Recommendation**: Add a state-by-state appendix or at minimum state "SAFE assumes Delaware C-corp incorporation. If the issuing entity is incorporated outside Delaware (e.g., California PBC, Wyoming LLC, Texas state-chartered), legal review is required before issuing SAFE."

#### E-H-030: Founder reset / re-vesting at priced round — flagged but not defended against
- **File**: `04a_convertible_and_terms.md` §17.3.
- **Issue**: "既存ベスティング がリセットされないか (priced round 時の一斉再ベストの罠)" — the trap is named but no mitigation playbook is given.
- **Recommendation**: Add "Defense against re-vesting: (a) demand 'no founder re-vest' as Term Sheet condition; (b) if forced, accept only with 50% credit for prior vesting time, (c) require double-trigger acceleration on the new vest schedule."

#### E-H-031: 日本のグロース上場と米国上場の選択 — no decision tree
- **Files**: `07_japan_specifics.md` §6.6, §8; (no equivalent US section).
- **Issue**: A Japanese startup with US customers can list TSE Growth (low bar, 5億円流通) or NASDAQ (high bar, $10M+ float, audit complexity). The decision is hugely consequential; the corpus only describes TSE Growth.
- **Recommendation**: Add `07` §8.6 "Choice between TSE Growth, TSE Standard/Prime, and US listing": (a) revenue geography, (b) market-cap target, (c) compliance cost ($1M/yr TSE vs $5M/yr US), (d) shareholder base.

### "Why" depth shallow

#### E-H-032: Magic Number > 1.0 → "accelerate S&M" without operational reality check
- **File**: `08_investment_thesis.md` §4.1.6.
- **Issue**: "Magic Number > 1.0 → accelerate S&M" assumes capacity exists. Real-world constraint: hiring sales reps takes 6+ months, ramp another 6 months, so accelerating spend may produce no improvement for 12 months. The recommendation glosses the operational lag.
- **Recommendation**: "If Magic Number >1.0 AND existing rep ramp curve has at least 6 months to runway, accelerate. If hiring lead time would push payoff beyond runway, hold."

#### E-H-033: Burn Multiple < 1.0x = "Amazing" — but how was it achieved?
- **File**: `08_investment_thesis.md` §4.1.7.
- **Issue**: Burn Multiple < 1.0 can come from (a) genuinely efficient scaling, (b) deferring necessary investment, (c) booking timing artifacts. The doc doesn't help distinguish.
- **Recommendation**: Add "Sanity check: if Burn Multiple is <1.0x but R&D headcount is flat YoY, suspect investment deferral, not efficiency."

#### E-H-034: NRR > 120% recommended threshold — no acknowledgment that it's largely unachievable in some segments
- **File**: `08_investment_thesis.md` §4.1.2.
- **Issue**: NRR > 120% for Mid-market is set as PASS, but for usage-based pricing models (Snowflake, Datadog) >130% is normal; for seat-based PLG (Notion) ~110% is best-in-class. Setting 120% as a uniform target either flatters seat-based or under-targets usage-based.
- **Recommendation**: Stratify thresholds by pricing model.

#### E-H-035: TAM / SAM / SOM triangulation — what to do when methods diverge
- **File**: `08_investment_thesis.md` §7.4.
- **Issue**: "3 手法でレンジ確認。一致しなければ理由を追跡." The audit prompt explicitly flags this as the "It's complicated" failure mode. Following the trail back to a single number is what an investor needs.
- **Recommendation**: Add tiebreak: "If top-down >> bottom-up, top-down is overestimating saturation; if bottom-up >> top-down, you've found a market the analysts haven't covered (cross-check with at least 5 customer interviews)."

#### E-H-036: Pre-money cap valuation — no "what to do when comp data is too thin" rule
- **File**: `05_valuation_wacc.md` §2.2.
- **Issue**: "最小 comp 数: 経験則 5 社以上" — but startups in deep-tech, climate, or new categories may have 0–2 listed comps. The doc says "median is unstable" but doesn't give a pivot to alternative method.
- **Recommendation**: Add "When comp set < 3, pivot to (a) precedent transactions ±5 years, (b) Berkus/Scorecard, (c) reverse DCF with explicit assumption disclosure. Do not compute multiple median below 3 comps."

### Stakeholder ambiguity

#### E-H-037: 投資契約書 (SPA) — "founder reps が個人保証になっていないか" — when does this happen?
- **File**: `04a_convertible_and_terms.md` §17.6.
- **Issue**: The flag is correct but the trigger is left implicit. Personal guarantees in founder reps appear when: (a) JFC creation loans, (b) SBI/regional bank seed loans, (c) some Japan VC contracts pre-2018. Geography matters.
- **Recommendation**: "Personal guarantee on founder reps is a Japan-specific risk in pre-2020 contracts and JFC creation loans (relaxed since 2024 経営者保証ガイドライン). US/SV venture contracts almost never have founder personal liability; flag any clause that reaches them."

#### E-H-038: VC vs CVC strategy choice — corp interest vs financial return tension not resolved
- **File**: `07_japan_specifics.md` §11.2; `08_investment_thesis.md` (no CVC section).
- **Issue**: "戦略的シナジー重視" but no rule for when a founder should accept a CVC over an independent VC. CVCs offer commercial relationships but bring strategic constraints (e.g., right to acquire, restricted territories, observer board).
- **Recommendation**: Add "Accept CVC lead investor only if (a) the strategic relationship is the primary value of the round, (b) the contract has clear sunset / exclusivity carveouts, (c) you have at least one independent VC at the table to defend founder interests."

#### E-H-039: M&A buyer mapping — strategic vs financial divergence in valuation
- **Files**: `05_valuation_wacc.md` §3.5; `08_investment_thesis.md` §1.14.
- **Issue**: "Strategic 高い、Financial 抑制的" — but at what stage / sector does the strategic premium typically peak? For B2B SaaS the strategic premium is 20–40%; for D2C it's near zero. The pattern matters for exit pricing.
- **Recommendation**: Add "Strategic-vs-financial premium by sector: B2B SaaS 25–40%, marketplaces 10–25%, D2C / e-commerce 0–10%, fintech 15–30% (regulated buyers pay premium for license)."

#### E-H-040: 投資家 vs 創業者 比較表 — no resolution for cap+discount stack
- **File**: `04a_convertible_and_terms.md` §16.3.
- **Issue**: Trade-off table lists "founder concedes X to get investor concession Y." But when an investor demands cumulative dividend AND participating preferred AND full ratchet AND drag-along (a "kitchen sink" term sheet), the trade-off table doesn't say "this is a wholesale rejection signal."
- **Recommendation**: Add "Kitchen-sink rule: term sheets containing >2 of {cumulative dividend, participating preferred, full ratchet, redemption rights, MFN, single-trigger drag-along, founder personal guarantee} should be presumed non-market and either fully renegotiated or rejected."

#### E-H-041: VC Method — Required IRR table not benchmarked against actual fund returns
- **File**: `05_valuation_wacc.md` §4.2.
- **Issue**: "Seed: 60-80% IRR" — but actual top-quartile VC fund IRR is 20–25% net to LPs. The deal-level required IRR > fund IRR because of survivor bias / portfolio construction, but the explanation is missing.
- **Recommendation**: Add "Required deal IRR > fund-level IRR because (a) ~50% of deals fail / break-even, (b) only 1 deal in 10 returns the fund. The 60–80% required IRR at Seed is the survival-conditional return; combined with 20–30% survival, the unconditional expected return is ~12–24%."

---

## Medium Issues (E-M-xxx)

### Stakeholder split or trade-off implicit but inferable

#### E-M-042: 「投資家」 = "VC" vs "angel" vs "CVC" not always disambiguated
- **File**: `04a_convertible_and_terms.md` (multiple sections).
- **Issue**: "投資家観点と創業者観点" tables use "投資家" generically. An angel investor's interests differ from a Series A VC's (longer hold horizon, lower expected dilution from follow-on, more sensitive to liquidity).
- **Recommendation**: Disambiguate as "Lead VC vs Follow VC vs Angel vs CVC" in the per-section trade-off tables.

#### E-M-043: 米国 vs 日本 standard compared at clause level but not at deal level
- **File**: `04a_convertible_and_terms.md` §16; `07_japan_specifics.md` §4.
- **Issue**: NVCA standard and J-KISS standard are described separately. A startup with US and Japan investors in the same round needs the harmonization rules (which standards override which).
- **Recommendation**: Add "Mixed-jurisdiction round protocol: NVCA standard governs corp law / charter terms; Japan standard governs domestic regulator-facing matters; Tokyo office governs day-to-day; Delaware governs equity issuance."

#### E-M-044: SaaS Magic Number — quarterly basis is brittle for startups with seasonal sales
- **File**: `08_investment_thesis.md` §4.1.6.
- **Issue**: Quarterly Magic Number is volatile for SaaS with December enterprise close cycles. Without smoothing, Q1 Magic Number understates efficiency.
- **Recommendation**: "Use 4-quarter rolling Magic Number for companies with >40% Q4 ARR concentration."

#### E-M-045: SaaS GM tier (75% / 65% / 50%) — applies to gross margin definitions inconsistently
- **File**: `08_investment_thesis.md` §4.1.9.
- **Issue**: The GM threshold doesn't specify whether it's GAAP GM, non-GAAP GM (excluding stock comp), or contribution margin. SaaS public reporting routinely shifts COGS to OpEx (e.g., customer success teams), inflating GM.
- **Recommendation**: Define: "GM threshold applies to GAAP gross margin including all customer-facing costs (hosting, support, customer success). Non-GAAP GM should be reported separately."

#### E-M-046: Working capital sensitivity — modeling guideline missing for capital-light businesses
- **Files**: `06_three_statement.md`; `03_business_models.md`.
- **Issue**: WC modeling assumes meaningful AR/AP/inventory. Pure SaaS with prepaid annual contracts has negative WC (cash inflows lead revenue), but the modeling boilerplate treats positive WC as default.
- **Recommendation**: Stratify WC modeling guidance by business model.

#### E-M-047: Hardware razor-blade — "subscription attach rate" without geographic / channel breakdown
- **File**: `03_business_models.md` §4.4.
- **Issue**: Attach rate varies wildly by channel (D2C >70%, retail <30%). The recommendation "watch attach rate" is correct but the user has no benchmark for what attach is realistic for their channel mix.
- **Recommendation**: Add channel-by-channel attach benchmarks.

#### E-M-048: Bio milestone Schedule — "out-licensing deal upfront $5–50M" — currency / region not specified
- **File**: `03_business_models.md` §5.2.
- **Issue**: Deal sizes are implicitly USD, but Japanese pharma deals (Takeda, Shionogi) often denominate in JPY with different milestone schedules. A Japan-based biotech using these benchmarks miscalibrates expectations.
- **Recommendation**: Currency-specify all bio deal benchmarks.

#### E-M-049: Marketplace bookings → revenue lag (Roblox 27 months) presented as fact, not as risk pattern
- **File**: `03_business_models.md` §1.6.
- **Issue**: "Roblox はユーザー寿命 (~27 ヶ月) で deferred revenue を認識." This is a Roblox-specific accounting policy, not a general marketplace rule. Other marketplaces (Airbnb, eBay) have radically different bookings → revenue conversion.
- **Recommendation**: Frame as "Roblox-specific (game economies). Most marketplaces book revenue at transaction close, not over user lifetime."

#### E-M-050: B2B Services — Utilization 100%+ as "burnout signal" — but utilization can be artifact of measurement
- **File**: `03_business_models.md` §7.6.
- **Issue**: Utilization >100% can indicate (a) burnout, (b) bad timecard hygiene (forgotten unbillable hours), (c) genuine underbilling that should be price-corrected. The doc treats it as exclusively (a).
- **Recommendation**: Diagnostic tree before declaring "burnout."

#### E-M-051: AI compute cost — "GPT-4 training $50–100M (2023)" extrapolated forward without methodology
- **File**: `03_business_models.md` §10.1, §10.5.
- **Issue**: The training cost forecast extrapolates from a single 2023 datapoint to "GPT-5 class $500M–$1B." The methodology (compute scaling, data scaling, MFU) is not specified. Models scale orthogonally to compute spend.
- **Recommendation**: Cite a Chinchilla-style scaling law or note that the extrapolation is purely empirical.

#### E-M-052: Customer concentration top 10 < 30% as PASS — but enterprise sales naturally concentrate
- **File**: `03_business_models.md` §10.4 (and similar).
- **Issue**: A B2B SaaS with 5 Fortune 500 customers may have top 10 = 100% by design; the threshold makes them automatically FAIL even if economics are great.
- **Recommendation**: Stratify by ACV: high-ACV enterprise should have a relaxed threshold.

#### E-M-053: 損金算入 SO 戦略 — 信託型 → 適格 SO 移行の経済影響 not quantified
- **File**: `07_japan_specifics.md` §2.7.
- **Issue**: 信託型 SO → 適格 SO 移行は手取り 55% → 20% に変わる重大経済差。doc has the rates but not the migration's cost in lost employee value.
- **Recommendation**: Add migration P&L: "For an employee with $2M paper SO, 信託型 (55% tax) yields $0.9M; 適格 (20%) yields $1.6M. Switching from 信託型 to 適格 in mid-vest is approximately a $700K per-employee value retention."

#### E-M-054: 防衛特別法人税 4% — "中小法人で法人税額が500万円以下なら基礎控除によりゼロ"
- **File**: `07_japan_specifics.md` §2.1.3.
- **Issue**: Implicit signal: "stay under 500万円 法人税額." But this is a strategic signal: don't push profits past the threshold without offsetting loss-utilization.
- **Recommendation**: Make the strategic signal explicit.

#### E-M-055: 中小法人軽減税率 (15%) — "令和9年3月31日まで" — sunset planning
- **File**: `07_japan_specifics.md` §2.2.2.
- **Issue**: The 15% bracket sunsets in 2027; companies planning multi-year tax models need to model the step-up. Mention is brief.
- **Recommendation**: "Plan tax rate transition: 中小 軽減 15% to standard 23.2% on 800万円 bracket, effective FY end after 2027/3/31."

#### E-M-056: 資本金 1 億円 vs 5 億円の壁 — 増資 timing 戦略 implicit
- **File**: `07_judpan_specifics.md` §7.2.
- **Issue**: "資本金 1 億円以下を維持" は中小税制を保つための戦略だが、資本準備金への組入で対応可能なのが暗黙的。投資家との交渉で「資本金 vs 資本準備金 比率」が議題になる。
- **Recommendation**: Add "Tax-optimal share-issuance protocol: at every priced round, allocate the maximum (50%) of paid-in to 資本準備金, keeping 資本金 below 1億円 as long as possible. This is a one-line term-sheet ask."

#### E-M-057: J-KISS 多重重畳での希薄化計算 — Coral Capital "4 つのこと" 警告 が単なる注釈
- **File**: `07_japan_specifics.md` §3.6.
- **Issue**: "Coral Capital は推奨" と書かれているがそれが Series A 直前で何を意味するか specifically described されない.
- **Recommendation**: "Multi-J-KISS rule: when overlapping J-KISS exceed 3 in count or 30% of pre-A pre-money valuation, demand a unified cap-table waterfall before signing the next J-KISS."

#### E-M-058: 種類株式の "1.5 倍 + 非参加型" 日本の実務 standard — but no rule for "when do you accept 1.5x?"
- **File**: `07_japan_specifics.md` §4.2.1.
- **Issue**: 「1.0 〜 1.5 倍 + 非参加型が主流」 but the trigger for 1.5x (down round? bridge?) not specified clearly.
- **Recommendation**: Add "1.5x liquidation in Japan typically signals (a) a bridge or (b) a defensive Series B during stress. Founder should document the rationale and demand a sunset or step-down clause."

#### E-M-059: みなし清算 (deemed liquidation) — 発動条件 specified, 戦略選択 not.
- **File**: `07_japan_specifics.md` §4.3.
- **Issue**: みなし清算は M&A で発動され、優先株主に対する優先配分を引き起こす。戦略的に founder-friendly な落としどころは「strategic acquisition で M&A 価格 ≥ 5x liquidation preference であれば preferred conversion を強制 (= drag-along + preferred convert mandatory)」。This negotiation lever is not surfaced.
- **Recommendation**: Add "Founder-protective deemed-liquidation playbook: include 'mandatory conversion at exit if M&A price > N x preference total' to avoid the participating-preferred double-dip in friendly exits."

#### E-M-060: Hardware GM "consumer 25% / B2B 35% / industrial 35%" benchmarks — without commodity vs differentiated split
- **File**: `03_business_models.md` §4.2.
- **Issue**: Hardware GM benchmark for "consumer" lumps differentiated brands (Sonos, GoPro) with commodity (Anker accessories). Median masks variance.
- **Recommendation**: Add brand-strength stratification.

#### E-M-061: Marketplace EV/GMV multiple "0.2–0.6×" range — no take-rate-aware framework
- **Files**: `05_valuation_wacc.md` §11.1; `03_business_models.md` §1.2.
- **Issue**: EV/GMV ranges 0.2–0.6×; the file says "take rate に依存" but doesn't formalize. The closed-form is `EV/GMV ≈ EV/Revenue × take rate`. This should be stated.
- **Recommendation**: Add formula and worked example showing how a 5pp take rate shift moves EV/GMV.

#### E-M-062: VC stage discount "Seed 50-70% IRR" — geography uncalibrated
- **File**: `05_valuation_wacc.md` §1.4.5.
- **Issue**: 50–70% IRR is US standard; Japan VCs typically target 30–40% (because exits are smaller and IPO threshold is lower). Using US discount in Japan systematically undervalues local startups.
- **Recommendation**: Add Japan-specific stage discount table: Seed 30–50%, A 25–40%, B 20–35%.

#### E-M-063: SaaS multiple cycle awareness — recent crash mentioned but trajectory unclear
- **File**: `05_valuation_wacc.md` §17.4.
- **Issue**: "2026 Q1 SaaS public multiple 6–7× は 2021 ピーク (15×+) 比 半減水準" — true, but no rule for "if you're modeling 2027–28 exit, what multiple to use?" Mean-revert? Stay flat?
- **Recommendation**: "Default forward-projection rule: use trailing 3-year median multiple. If valuing in a clear cycle peak/trough, additionally show ±25% sensitivity."

#### E-M-064: Fintech Lending P/B vs B2B SaaS EV/ARR — when does a fintech use SaaS comps?
- **File**: `05_valuation_wacc.md` §11.2.
- **Issue**: A "tech-forward fintech" (Affirm, SoFi) sits between fintech P/B and SaaS EV/Revenue. The doc doesn't say which set of comps governs at what stage.
- **Recommendation**: "Use SaaS EV/Revenue when net-interest income is <30% of revenue. Use fintech P/B when net-interest income >50%. Hybrid when in between."

#### E-M-065: Private SaaS "4.5× ARR" benchmark — vintage and source not labeled
- **File**: `05_valuation_wacc.md` §10.1.
- **Issue**: "Private SaaS median: 4.5× ARR" without time-stamp or source. Private SaaS comps are notoriously stale.
- **Recommendation**: Add "(2026 Q1 source XYZ; for 2027+ valuations, refresh from current Pitchbook / a16z private-SaaS index)."

#### E-M-066: Replacement cost as floor — but for IP-heavy startups severely underestimates
- **File**: `05_valuation_wacc.md` §9.1.
- **Issue**: "Replacement cost: acquihire の price floor" — but for biotech with patented compounds, replacement cost could be 10x the going-concern. The "floor" framing assumes commodity tech.
- **Recommendation**: Caveat: "Replacement cost is only a floor for non-patented, non-network-effect businesses."

#### E-M-067: VC Method First Chicago — best/base/worst probabilities pattern
- **File**: `05_valuation_wacc.md` §4.4.
- **Issue**: "Best 10–25%, Base 40–60%, Worst 25–50%" — wide ranges. Without anchoring to portfolio outcome data, the user is on their own.
- **Recommendation**: Add "Default anchoring: Best 20%, Base 50%, Worst 30% for top-quartile VC. For mid-pack VCs, shift to Best 10%, Base 40%, Worst 50%."

#### E-M-068: ESOP プール 10–15% (Japan) vs 15–20% (US) — when does a Japan startup adopt the US standard?
- **File**: `07_japan_specifics.md` §2.7.
- **Issue**: Median is given but the strategic signal isn't: a Japan startup hiring globally should match the 15–20% US norm, while a domestic-only startup can stay at 10–12%.
- **Recommendation**: Add "Choose ESOP target by hiring footprint: domestic only 10–12%, US/EU senior hires required 15–20%."

#### E-M-069: 試験研究費税額控除 — "上限 25%" — interaction with 防衛特別法人税 not described
- **File**: `07_japan_specifics.md` §2.4.
- **Issue**: The 25% cap and the 4% defense tax interact in ways that change the marginal value of an additional 100M JPY R&D spend.
- **Recommendation**: Add a worked example showing the marginal effective benefit of R&D credit in 2026+.

#### E-M-070: 信託型 SO 過去事例 5 年遡及課税 — but mitigation playbook absent
- **File**: `07_japan_specifics.md` §2.7.4.
- **Issue**: Past 5 years of beneficiaries face給与所得課税. What's the mitigation? Tax indemnification? Company gross-up?
- **Recommendation**: Add mitigation: "Companies can make a one-time gross-up payment to cover the tax delta, treating it as bonus expense."

#### E-M-071: Stock comp deduction — ISO vs NSO vs RSU — dependency on company tax status
- **File**: `08_investment_thesis.md` §6.6.
- **Issue**: For US tax: ISO is non-deductible by company / favored employee tax; NSO is deductible by company / ordinary employee tax. The DD checklist mentions but doesn't strategize.
- **Recommendation**: "Tax-equilibrium guidance: when company is currently loss-making (no tax shield value), grant ISO. When profitable, NSO is value-neutral or favored."

#### E-M-072: Mom-test customer interview — "talk to 5 customers" is a process recommendation but no decision threshold
- **File**: `08_investment_thesis.md` §6.1.
- **Issue**: "顧客 interview top 10 + churn 顧客 5" — but at what aggregate signal does the user decide pivot vs persevere?
- **Recommendation**: "Pivot signal: ≥3 of top 10 customers cite same root-cause complaint; or ≥3 churned customers describe a hidden alternative." (Note: this material is in `lean-startup` skill but the cross-reference is missing.)

#### E-M-073: Real estate cap rate spread vs interest rate — 200–300 bps "historical" — but historical is a moving target
- **File**: `03_business_models.md` §9.4.
- **Issue**: "10Y Treasury との spread (200–300bps が historical)" — but post-2022 the spread has compressed; "historical" is ambiguous time window.
- **Recommendation**: Specify: "1990–2019 average spread 250 bps; 2020–2024 average 180 bps; 2025–26 trending back to 200 bps."

#### E-M-074: Hospitality RevPAR cycle — 2025 forecast given but cycle stage not labeled
- **File**: `03_business_models.md` §9.1.
- **Issue**: "National occupancy 61.7% (2026 forecast)" without context — is this a peak, trough, or mid-cycle? Affects valuation.
- **Recommendation**: Anchor to historical: "61.7% is below 2018–19 peak of 67%; we are in a mid-recovery cycle."

#### E-M-075: AI 価格 (Claude Opus, GPT-5) — published but lifecycle warning weak
- **File**: `03_business_models.md` §10.1.
- **Issue**: API price tables are time-stamped but the user with a 3-year forecast horizon may treat them as durable. Historical drift is 50–80% per 12 months.
- **Recommendation**: "Default forecast assumption: API price declines 50% per 12 months. Build the model with annual reprice events."

#### E-M-076: Lifestage — "Decline" 段階で資産売却価値 — but no rule for distressed exit timing
- **File**: `05_valuation_wacc.md` §12.4.
- **Issue**: A startup in decline often has a 12–18 month window where asset value > debt before insolvency. The framework names the stage but not the exit-window playbook.
- **Recommendation**: Add "Decline-stage exit playbook: triangulate liquidation, asset-sale, and acquihire values; sell to highest within 18 months of declining MoM revenue, before legal/regulatory exposure compounds."

#### E-M-077: 補助金タイミング — 交付決定 → 入金 3–12ヶ月 — モデリング上の WC ハック ambiguous
- **File**: `07_japan_specifics.md` §9.2.2.
- **Issue**: "交付決定 → 実績報告 → 入金まで 3–12 ヶ月" — implication: WC tank during the lag. No financing-pattern guidance ("can you bridge with bank financing on the granted-but-not-disbursed grant?").
- **Recommendation**: "Bridge financing of awarded grants: most regional banks accept "交付決定通知" as collateral for 70% of the grant amount at SOFR-equivalent +100bps."

#### E-M-078: Japan VC ticket size vs US — "1/3 〜 1/2 程度" — but late-stage gap is wider
- **File**: `07_japan_specifics.md` §11.3.
- **Issue**: For Series B/C, Japan ticket size is 1/3 of US. But for Series D / pre-IPO, the Japan ecosystem essentially doesn't exist domestically; cross-border (Sequoia, Coatue, DST) is mandatory. The 1/3–1/2 framing understates the late-stage reality.
- **Recommendation**: "Late-stage: Japan domestic capital ceiling is ~30 億円 / round. Above that, cross-border lead investor or TSE Growth listing is the only realistic path."

#### E-M-079: Delaware Flip cost / time / risk — described mechanically but no decision rule
- **File**: `07_japan_specifics.md` §12.2.
- **Issue**: Flip is described as a procedural option, but the trigger ("when does a Japanese startup flip?") is left implicit. The right answer is: flip if (a) US/Cayman investors lead a Series A+, (b) 50%+ of revenue is USD, (c) US listing is the explicit exit.
- **Recommendation**: Make the decision tree explicit.

#### E-M-080: Venture debt vs equity dilution comparison — example shows 0.94% vs 9.1% — generalizable rule?
- **File**: `11_debt_financing.md` §1.1.6.
- **Issue**: The example shows venture debt dilution at ~10% of equivalent-equity dilution. Is this universal? Depends on warrant coverage and pricing.
- **Recommendation**: "Rule of thumb: venture debt dilution = (equity-equivalent dilution) × (warrant coverage % / 100). 7.5% coverage → ~10% of equity dilution."

#### E-M-081: RBF cap multiple — IRR 15–35% — when does 35% break the unit economics?
- **File**: `11_debt_financing.md` §1.2.6.
- **Issue**: Effective IRR of 35% on RBF is brutal for low-margin businesses. The doc warns about it but doesn't quantify the break-point.
- **Recommendation**: "RBF break-even rule: do not stack RBF if (revenue share % × cap multiple) > gross margin %. For a 60% GM business, RBF (6% × 1.5x = 9% all-in) is fine; (8% × 2.0x = 16%) is not."

#### E-M-082: Bridge loan — insider vs 3rd party — stigma signaling unmentioned
- **File**: `11_debt_financing.md` §1.4.4.
- **Issue**: Insider bridge is described as "next round confidence signal." But the obverse is that an insider-only bridge can also signal "VCs can't get a new lead." The signaling is bilateral and the doc only catches one direction.
- **Recommendation**: Add: "Insider bridge with no new external participant after 60+ days = warning signal. New-lead bridge = green signal."

---

## Low Issues (E-L-xxx)

### Phrasing-level

#### E-L-083: "It depends" without specifying — `04a` §16.1 "Capped Participation: ケースバイ"
- **Recommendation**: Specify: "Capped participation is acceptable when cap ≤2x and exit is likely <$3x preference total; reject for early-stage or where exit is binary big/small."

#### E-L-084: "Strong founder は MAC 削除を要求する" — strong how?
- **File**: `11_debt_financing.md` §1.1.5.
- **Recommendation**: "Founder leverage to remove MAC: (a) >$5M ARR, (b) competing term sheet, (c) 6+ months runway without the debt."

#### E-L-085: 「経営者保証緩和」 in 政策金融公庫 — what specifically changed?
- **File**: `11_debt_financing.md` Table 1.0; `07` §5.2.
- **Recommendation**: Reference 2024年経営者保証ガイドライン and the conditions for waiver.

#### E-L-086: 「グロース上場前の創業者持分中央値 15-30%」 — sample size?
- **File**: `07_japan_specifics.md` §5.3.
- **Recommendation**: "Based on TSE Growth listings 2020–2024 (~150 cases)."

#### E-L-087: 「日本実務トレンド: 1.0〜1.5倍 + 非参加型が主流」 — sample period?
- **File**: `07_japan_specifics.md` §4.2.1.
- **Recommendation**: "Based on Coral Capital + INITIAL data 2022–2025."

#### E-L-088: 「YC SAFE は無利息 → 米 Convertible Note は 4–8%」 — historical tension not noted
- **File**: `04a_convertible_and_terms.md`.
- **Recommendation**: Add brief note that pre-2013 the convertible note interest was the standard; SAFE removed it precisely to avoid debt classification.

#### E-L-089: "Big 4 advisory: Senior Manager $400–700/hr" — 2026?
- **File**: `03_business_models.md` §7.1.
- **Recommendation**: Time-stamp.

#### E-L-090: "Bessemer 推奨: 6 ヶ月 burn floor" — citation but no link
- **File**: `11_debt_financing.md` §1.1.5.
- **Recommendation**: Cite Bessemer's "Atlas: Venture Debt" page.

#### E-L-091: "Damodaran 流: industry bottom-up beta を使う" — "individual regression beta を信用せず" too sweeping
- **File**: `05_valuation_wacc.md` §15.1.
- **Recommendation**: "For mature companies with stable models and >5 years of trading history, regression beta is usable. Damodaran's recommendation specifically targets thin-trading or transition-state firms."

#### E-L-092: "M&A エグジットでは優先分配が発動。IPO エグジットでは普通株主と同等" — 但し条件で優先株が convert refusable
- **File**: `07_japan_specifics.md` §5.4.
- **Recommendation**: Add "IPO-trigger automatic conversion is contingent on Mandatory Conversion thresholds (qualified IPO size + PPS multiple). Failing those thresholds, preferred shareholders can refuse to convert and retain liquidation overhang post-listing."

#### E-L-093: "中小法人 軽減税率 15% は所得 800 万円以下" — 800 万円 is annual
- **File**: `07_japan_specifics.md` §2.2.2.
- **Recommendation**: Add "(annual taxable income, not revenue)."

---

## Trade-off の網羅性チェック

| Domain | Trade-off 明示 (高) | 部分的 (中) | 不明瞭 (低) | 重大ギャップ |
|---|---|---|---|---|
| Valuation 手法選択 (DCF / Comps / VC Method / Real Options) | `05` §17 | `08` §1.11 | — | Method weighting at each stage missing (E-H-010) |
| Debt vs Equity (venture debt vs SAFE vs priced) | `11` §1.0 | `04a` §1.4 | — | No master decision rule across `04a`/`11` (E-C-001) |
| Pre-money vs Post-money SAFE | `04a` §2.2 (math) | `04a` §2.7 (qualitative) | — | Negotiation rule missing (E-C-002) |
| Liquidation: 1x non-part vs participating vs capped | `04a` §7 | `07` §4.2.1 (Japan) | — | OPM/PWERM tiebreak missing (E-C-004) |
| Anti-dilution: full ratchet vs broad-based | `04a` §9 | `07` §4.2.2 | — | Forced-acceptance fallback missing (E-H-008) |
| Cumulative vs Non-cumulative dividend | `04a` §8 | — | — | Threshold for "this is debt" missing (E-H-007) |
| US-GAAP vs J-GAAP | `07` §1 (good); `06` (good) | `05` §13.3 | — | Mixed-jurisdiction round protocol missing (E-M-043) |
| Japan tax (中小 vs 大企業) | `07` §2 | — | — | Capital allocation tactic underspecified (E-M-056) |
| ESOP: 信託型 vs 適格 SO | `07` §2.7 | — | — | Migration playbook missing (E-H-023, E-M-053) |
| Stage discount vs Survival prob | — | `05` §1.4.5, §15.8 | — | Default rule missing (E-C-003) |
| Founder vs Investor | `04a` (multiple) | — | — | Stakeholder type granularity (Lead/Follow/Angel/CVC) (E-M-042) |
| Strategic vs Financial buyer | `05` §3.5 | `08` §1.14 | — | Sector premium calibration (E-M-039) |
| Conservative vs Aggressive scenario | — | `08` §1.13 | `05` §1.11 | Stack-up bias rule (covered §15.7 but not enforced) |
| Top-down vs Bottom-up TAM | `08` §7 | — | — | Tiebreak when divergent (E-H-035) |
| TSE listing vs US listing | — | — | `07` §6.6 (TSE only) | Choice framework missing (E-H-031) |
| Hardware: D2C vs Retail channel | `03` §4.1 | — | — | Attach-rate by channel (E-M-047) |
| Marketplace take-rate ceiling | — | `03` §1.4 | — | Threshold by frequency missing (E-H-017) |

---

## Stakeholder Perspective Coverage

| Stakeholder | Coverage | Gaps |
|---|---|---|
| **Founder (CEO)** | Strong in `04a`, `08`, `07`. | Wind-down decision (E-C-005); negotiation kitchen-sink rules (E-H-040). |
| **Existing Investor (lead)** | Strong in `04a` §16, `08` §2. | Lead vs Follow distinction missing (E-M-042). |
| **New Investor (Lead vs Follow)** | Implicit. | Pro-rata vs new-lead negotiation playbook missing. |
| **Acquirer (strategic)** | `05` §3, `08` §1.14. | Sector premium calibration (E-M-039). |
| **Acquirer (financial / PE)** | `05` §3.5. | LBO debt structure not connected to `11` §11. |
| **Lender (venture debt / RBF)** | `11` strong. | Banker / non-bank distinction in covenants underplayed. |
| **Auditor** | `05` §13. | Big 4 vs 中堅 monitor ratio (E-M-...). |
| **Regulator (FSA, SEC, NMS)** | `07` §6 (Japan); `03` §3 (Fintech) | EU AI Act briefly touched (`03` §10); MiFID II / SEC Reg BI not covered. |
| **Customer (B2B SaaS in TAM)** | Strong in `09_market_sizing.md`. | Customer-interview signaling gap (E-M-072). |
| **Employee (ESOP)** | `04a` §15, `07` §2.7. | Employee tax migration (E-M-053); ISO/NSO/RSU strategic switch (E-M-071). |
| **Co-founder** | `08` §9.4 | Equity-split dispute resolution playbook missing. |
| **Bank lender (J-GAAP context)** | `07` §5.2; `11` §10. | 経営者保証緩和 details (E-L-085). |
| **Independent director / board** | `04a` §11. | Founder removal playbook missing. |

---

## 業態別 / Stage 別の戦略適合性

### 業態 fit (sample of clear-vs-ambiguous)

| 業態 | 主推奨手法 (corpus) | 適合性 | 主要ギャップ |
|---|---|---|---|
| SaaS (Pure) | EV/ARR + DCF | ✓ | Multiple cycle awareness (E-M-063); SBC treatment (E-H-013) |
| SaaS (Vertical / PLG hybrid) | 同上 | ✗ | NRR thresholds not stratified by GTM (E-H-015) |
| Marketplace | EV/GMV + EV/Net Revenue + cohort retention | ✓ | Take-rate ceiling unclear (E-H-017) |
| Fintech (Lending) | P/B + NIM + vintage | ✓ | Capital-adequacy threshold by regulator (E-H-024) |
| Fintech (Payments) | EV/TPV + EV/Revenue | ✓ | — |
| Hardware + Razor-blade | Hardware GM + Subscription LTV | △ | Churn break-point undefined (E-H-019); attach by channel (E-M-047) |
| Bio | rNPV + Real Options | ✓ | Discount rate vs stage (E-H-020); Real Option vs DCF priority (E-H-021) |
| Bio (later stage / commercial) | DCF + comp pharma | △ | Patent-cliff curve: corpus has US standard; Japan PMDA + 薬価 not integrated into curve. |
| Real Estate / PropTech | NOI + Cap Rate + IRR | ✓ | Cycle awareness (E-M-073, E-M-074) |
| AI / Foundation Model | EV/Revenue + compute economics | △ | Compute cost forecasting methodology (E-M-051); price decay (E-M-075) |
| B2B Services | Headcount × utilization × bill rate | ✓ | Burnout / measurement-artifact distinction (E-M-050) |
| Manufacturing | OEE + capex efficiency | ✓ | — |
| E-commerce / D2C | CM3 + cohort + repeat | ✓ | — |
| Media / Content | DAU/MAU + content amortization | ✓ | DAU definition ambiguity (corpus flags it but no resolution rule) |

### Stage fit issues

| Stage | Mismatch occurrence | Issue |
|---|---|---|
| Pre-revenue → IPO 戦略 | Found in: `08` §1.14 mentions IPO at $200M ARR, doesn't say pre-revenue / pre-PMF won't reach. | Missing ramp model. |
| Series A → M&A exit 戦略 | Briefly hinted in `08` §1.14 but no warning that M&A at A is usually acquihire <$10M. | Add "M&A at Series A typically yields acquihire economics, not strategic exit valuation." |
| Late-stage → SAFE structure | Not raised — SAFE is correctly bound to early stage in `04a`. | None. |
| **Pre-revenue Japan + venture debt** | `11` requires ARR ≥ $2M; pre-revenue Japan may default to JFC + 政策金融公庫 (`07` §5.2) — but cross-link is implicit. | Add explicit "for pre-revenue Japan: JFC creation loan + J-KISS, NOT venture debt." |
| **Series A SaaS + naive exit valuation** | `08` doesn't warn that exit valuations at Series A are theoretical, not bookable. | Add: "Series A exit-value modeling is for thesis-testing only, not for distribution to LPs." |

---

## Implementation Reality Check

Recommendations in the corpus that may be hard to implement:

| Item | File | Issue |
|---|---|---|
| Build full waterfall with OPM/PWERM/Hybrid | `05` §13 | Requires σ estimate from peer stocks — for verticals with no public peers (deep-tech, climate), this is hand-wavy. |
| 反復計算 for J-KISS post-money cap with multiple SAFEs | `07` §14.4 | Pseudocode given but real Excel implementation requires solver; many startups don't have Excel-savvy CFOs at the J-KISS stage. |
| Real Options σ estimation | `05` §8 | "Industry stock vol" — for biotech the comp set is volatile and small; σ estimates can swing 30%pts. |
| Stage-segmented WACC | `05` §1.11 | Manual, multiplicative; high error rate without a template. |
| Vintage Loss Curve modeling for fintech | `03` §3.2 | Requires segmented underwriting data many seed-stage lenders don't have. |
| "Top 10 顧客 + churn 5 への DD interview" | `08` §6.1 | For consumer / SMB, interviewing top 10 customers may not be useful (long tail); doc doesn't say "use cohort interviews instead at low ACV." |
| 信託型 SO migration | `07` §2.7.4 | Recipe absent (E-H-023, E-M-053, E-M-070). |
| Rebuild cap table on Series A re-vesting | `04a` §15.1 | Mechanically simple but socially costly; doc gives no negotiation script. |
| Comp set ≥ 5 公開類似会社 | `05` §2.2 | For Japan SaaS with no listed comps, the rule is unviable; doc doesn't pivot. |
| 月次決算 5 営業日内 (IPO 準備) | `07` §8.2.3 | Many startups close in 15–25 business days; the "5-day close" target is a 6–12 month transformation project, not a one-time fix. The doc states the requirement but not the roadmap. |

---

## "Why" 説明深度のスコア

| File | Score (0–10) | Rationale | 改善ポイント |
|---|---|---|---|
| `00_design_guidelines.md` | 7 | Structural; doesn't claim strategy. | n/a |
| `01a_modeling_standards.md` | 6 | Standards described; few "why this standard" passages. | Add rationale per standard. |
| `01b_integrity_and_anti_patterns.md` | 7 | Anti-patterns named with consequences. | More numerical examples of failure. |
| `02_saas_metrics.md` | 8 | NRR / GRR rationale clear. | NRR by GTM split needed (E-H-015). |
| `03_business_models.md` | 7 | Industry mechanics solid; trade-offs uneven. | Take-rate ceiling, hardware churn break-point (E-H-017, E-H-019). |
| `04a_convertible_and_terms.md` | 8 | Excellent trade-off tables, NVCA standard reference. | Pre/post SAFE founder rule (E-C-002), kitchen-sink rule (E-H-040). |
| `04b_cap_table_mechanics.md` | (sampled) 7 | Mechanics clear; integration with `04a` strong. | Multi-jurisdiction protocol (E-M-043). |
| `05_valuation_wacc.md` | 8 | Damodaran-grade. | TV tiebreak (E-H-011), Stage discount default (E-C-003), SBC handling (E-H-013). |
| `06_three_statement.md` | 7 | Mechanics; less judgment content. | WC by business model (E-M-046). |
| `07_japan_specifics.md` | 8 | Comprehensive; tax + corp structure strong. | Migration playbooks (E-H-023, E-M-053), TSE vs US listing (E-H-031), late-stage cap (E-M-078). |
| `08_investment_thesis.md` | 8 | VC frameworks well-curated. | Burn Multiple boundary cases (E-H-016, E-M-033), founder-side wind-down (E-C-005). |
| `09_market_sizing.md` | (sampled) 7 | Methods catalogued. | Triangulation tiebreak (E-H-035). |
| `10_modeling_craft.md` | (sampled) 7 | Craft + organization. | More cross-file routing. |
| `11_debt_financing.md` | 8 | Excellent product catalog. | Trade-off vs equity at each instrument (E-M-080), bridge stigma (E-M-082). |

Average ≈ 7.4.

---

## Cross-cutting Strategic Patterns

### Pattern A: "Standard is named, edge case is named, but the bridge between them is missing"
- Manifestation: NVCA standard 1x non-part is named; participating preferred is described as a deviation. But "when can a founder accept participating?" is unstated.
- Affected: E-C-002, E-H-007, E-H-008, E-H-040.

### Pattern B: "US standard is the implicit baseline, Japan is a deviation"
- Manifestation: many ratios and benchmarks (CAC payback, NRR, ESOP %) are US-anchored. Japan adjustments are noted in `07` but not woven back into other files.
- Affected: E-M-062, E-M-068, E-M-078, E-H-031.

### Pattern C: "Trade-off table is comprehensive but the mediator (= what to choose when both are reasonable) is missing"
- Manifestation: §16.3 of `04a` lists "founder concedes X to get investor concession Y" but no recipe for the actual sequencing or weight.
- Affected: E-H-006, E-H-007, E-H-008, E-H-010, E-H-011, E-H-040.

### Pattern D: "Quantitative threshold is given but the upper / lower failure mode is asymmetric"
- Manifestation: NRR > 120% is "great" but the doc doesn't say "NRR > 150% is suspicious" (could indicate one-time expansion, accounting smoothing).
- Affected: E-H-015, E-M-044, E-M-052.

### Pattern E: "Multi-file dependency exists but no cross-file router"
- Manifestation: Choosing a debt instrument requires reading `11`, but the choice depends on stage (`08`), business model (`03`), and tax structure (`07`).
- Affected: E-C-001 (root cause).

### Pattern F: "Founder-side perspective is strong on terms / cap table but absent on operational shutdown / pivot"
- Manifestation: Pivot/persevere/kill in `08` §10 is from VC's seat, not founder's. Wind-down economics (severance, reputation, IP allocation) absent.
- Affected: E-C-005.

### Pattern G: "Stakeholder is named but not granular"
- Manifestation: "投資家" used generically when the actual stakeholder differs (Lead VC vs Follow vs CVC vs Strategic partner).
- Affected: E-M-042, E-H-038.

### Pattern H: "Implementation hazard mentioned in passing but not elevated"
- Manifestation: Iterative J-KISS computation, OPM σ estimation, monthly close compression — all mentioned but no "you need a 6-month engineering project to do this" warning.
- Affected: E-H-009, multiple Implementation Reality Check items.

### Pattern I: "Time-stamp on benchmark data is inconsistent"
- Manifestation: SaaS multiples cite 2026 Q1; some Damodaran data is 2026-01; some industry benchmarks have no time stamp.
- Affected: E-L-086, E-L-087, E-L-089, E-M-065.

### Pattern J: "Choice rule is given but conflict resolution is not"
- Manifestation: Real Options says Bio with abandonment is +$17M; Decision Tree DCF says -$24M. Doc surfaces both but doesn't say "for IC, go with Real Options" or "for IC, go with DCF and treat Real Options as sensitivity."
- Affected: E-H-021, E-H-011.

---

## Action Items (Top 10 by impact)

1. **Build a master decision tree** (E-C-001) routing (stage × business model × geography × capital need × revenue stage) → instrument + valuation method + key file. **High value, ~1 day to build.**
2. **Add OPM / PWERM tiebreak** (E-C-004) to `05` §13, with a worked Series-C example. **High value, ~0.5 day.**
3. **Add post-money SAFE negotiation rule** (E-C-002) to `04a` §2.2 with cap-conversion arithmetic. **High value, ~0.5 day.**
4. **Resolve stage discount vs survival probability default** (E-C-003) in `05` §1.4.5/§15.8. **High value, ~0.5 day.**
5. **Build founder-side wind-down framework** (E-C-005) as `08` §10.4. **High value, ~1 day.**
6. **Add TV tiebreak rule** (E-H-011). **0.25 day.**
7. **Stratify NRR / Burn Multiple thresholds by GTM** (E-H-015, E-H-016, E-M-052). **0.5 day.**
8. **Add Japan-specific stage discount table** (E-M-062). **0.25 day.**
9. **Add 信託型 → 適格 SO migration playbook** (E-H-023, E-M-053, E-M-070). **0.5 day.**
10. **Add TSE Growth vs US listing decision tree** (E-H-031). **0.5 day.**

Total estimated remediation effort: ~5.5 working days for the Top 10; ~12 days for the full 92-issue set.

---

## Methodology Notes

- This is a **clarity audit, not a correctness audit**. Where the corpus gives a recommendation that is *clear* but might be debatable, no issue is logged. Issues are logged only where the corpus leaves Claude unable to make a judgment call.
- Severity assignment errs on the side of "high" rather than "critical" except where directional wrongness is plausible. Five Critical issues represent the situations where Claude could give catastrophically wrong (≥30% off) advice without a corpus flag.
- Sampling depth: complete read of files 03, 04a, 05, 07; deep sampling (~50% line coverage) of 08, 09, 11; structural read of 00, 01a, 01b, 02, 04b, 06, 10. Findings count is approximate; deeper passes on each file would likely add 20–40 more Medium / Low issues without changing the strategic-pattern conclusions.
- Cross-references between files were spot-checked for consistency; the most consequential cross-file gap is "no master routing layer" (E-C-001), which by itself accounts for ~15 of the High issues.
