"""Economic-quality regression tests for the startup financial modeling kernel.

These tests pin the economic *sanity* of generated plans, not just their
structure. They exist because the generator could previously emit a textbook
seed-SaaS plan with -789% gross margin (cost-to-serve drivers were unanchored
to the stated/target gross margin) while still passing every structural check.

Run directly:
    PYTHONPYCACHEPREFIX=$(mktemp -d) \\
      python3 skills/startup-financial-modeling/build/tests/test_economic_quality.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from openpyxl import load_workbook

SKILL_DIR = Path(__file__).resolve().parents[2]
RUNTIME_DIR = SKILL_DIR / "build" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import build_model  # noqa: E402
import economic_kernel as kernel  # noqa: E402
import source_plan_builder as source_plan  # noqa: E402

# --- Archetype source narratives -------------------------------------------

SAAS_STORY = """# Seed-stage B2B SaaS equity story

The company sells a workflow-automation SaaS to mid-market operations teams.
The model must support a seed fundraise: 5-year integrated plan, monthly burn,
runway, unit economics, and dilution.

Monetization is a per-seat subscription at 月額1.2万円 per seat, average 40 seats
per customer. Phase 1 targets 600 paying customers in three years, roughly
¥35億 ARR at maturity. Gross margin target is about 78%. Logo churn runs near
14% annually with modest net revenue expansion.

The plan needs market sizing, competitive funding benchmarks, hiring, scenario
analysis, sensitivity analysis, and an investor-use funding plan.

Source: customer discovery memo, market sizing memo, investor benchmark notes.
"""

MARKETPLACE_STORY = """# Series A marketplace equity story

The company runs a two-sided marketplace connecting local service providers
with consumers. Revenue is a take rate of 18% on gross merchandise value.
The model needs a 5-year integrated plan covering liquidity, contribution
margin, and the next fundraise.

Phase 1 targets ¥120億 GMV at maturity with repeat purchase behaviour.

Source: cohort analysis memo, marketplace benchmark notes.
"""

HARDWARE_STORY = """# Asset deployment equity story

The company is an asset-heavy startup deploying specialized field devices into
operational sites. The model combines recurring lease fees, services, and
software. Unit pricing is 月額32万円. Phase 1 targets cumulative deployments of
3,000 units in three years and about 25,000 operating units at maturity.
Hardware cost starts around ¥8m per unit and declines with scale.

Source: customer discovery memo, lender discussion notes.
"""

ARCHETYPES = {
    "saas": SAAS_STORY,
    "marketplace": MARKETPLACE_STORY,
    "hardware": HARDWARE_STORY,
}


def _implied(facts) -> list[dict]:
    """Replicate the workbook revenue / COGS / people formulas period by period.

    Mirrors Revenue Build, Cost Build, and People Plan so the test is an
    independent check on the driver values rather than trusting kernel
    internals.
    """
    ending = kernel.ending_units(facts.new_units)
    average = kernel.average_units(ending)
    rows: list[dict] = []
    for i in range(len(facts.years)):
        txn = facts.gmv_yen[i] * facts.take_rate[i]
        recurring = average[i] * facts.monthly_price_yen[i] * 12
        one_time = facts.new_units[i] * facts.monthly_price_yen[i] * 3
        subtotal = txn + recurring + one_time
        revenue = subtotal + subtotal * facts.other_revenue_share[i]
        variable = revenue * facts.variable_cogs_pct[i]
        delivery = average[i] * facts.delivery_cost_yen[i] * 12
        cloud = average[i] * facts.cloud_cost_yen[i] * 12
        support = facts.customers[i] * facts.support_cost_yen[i] * 12
        cogs = variable + delivery + cloud + support
        headcount = (
            facts.product_headcount[i]
            + facts.gtm_headcount[i]
            + facts.operations_headcount[i]
            + facts.ga_headcount[i]
        )
        people_cost = headcount * facts.avg_comp_yen[i]
        rows.append(
            {
                "revenue": revenue,
                "cogs": cogs,
                "gross_margin": (revenue - cogs) / revenue if revenue else 0.0,
                "people_cost": people_cost,
            }
        )
    return rows


def test_gross_margin_tracks_target_across_archetypes() -> None:
    """Every period's implied gross margin must sit within 3pp of its target."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        rows = _implied(facts)
        for i, row in enumerate(rows):
            assert row["revenue"] > 0, f"{name} period {i}: non-positive revenue"
            gap = abs(row["gross_margin"] - facts.target_gross_margin[i])
            assert gap <= 0.03, (
                f"{name} period {i}: gross margin {row['gross_margin']:.1%} "
                f"vs target {facts.target_gross_margin[i]:.1%} (gap {gap:.1%})"
            )
        assert rows[-1]["gross_margin"] > 0, f"{name}: negative mature gross margin"


def test_stated_gross_margin_is_extracted_from_narrative() -> None:
    """A narrative gross-margin target overrides the profile default."""
    facts = kernel.derive_source_facts(SAAS_STORY)
    assert abs(facts.target_gross_margin[-1] - 0.78) <= 0.01, (
        f"stated 78% gross margin not extracted: {facts.target_gross_margin[-1]}"
    )


def test_annual_pricing_is_converted_to_a_monthly_figure() -> None:
    """An ACV or explicitly annual price must be divided to a monthly price.

    The model drives recurring revenue off a monthly price; a ¥7M/year ACV
    read as ¥7M/month overstates revenue twelvefold.
    """
    acv = kernel.derive_source_facts(
        "# SaaS plan\nB2B SaaS. ACV is ¥7,200,000 per customer per year.\n"
        "Source: memo.\n"
    )
    assert acv.monthly_price_yen[0] == 600_000, (
        f"ACV not converted to a monthly price: {acv.monthly_price_yen[0]}"
    )
    annual = kernel.derive_source_facts(
        "# SaaS plan\nB2B SaaS. The subscription price is ¥1,200,000 per year.\n"
        "Source: memo.\n"
    )
    assert annual.monthly_price_yen[0] == 100_000, (
        f"annual price not converted: {annual.monthly_price_yen[0]}"
    )
    # Japanese annual cue (年額).
    jp = kernel.derive_source_facts(
        "# SaaS計画\nB2B SaaS。利用料は年額240万円。\nSource: メモ。\n"
    )
    assert jp.monthly_price_yen[0] == 200_000, (
        f"年額 price not converted: {jp.monthly_price_yen[0]}"
    )
    # A monthly price stays monthly, and an explicit 月額 wins over a later
    # ACV mention in the same document.
    monthly = kernel.derive_source_facts(SAAS_STORY)
    assert monthly.monthly_price_yen[0] == 12_000
    both = kernel.derive_source_facts(
        "# SaaS plan\nB2B SaaS priced at 月額50,000円. ACV is ¥1,200,000.\n"
        "Source: memo.\n"
    )
    assert both.monthly_price_yen[0] == 50_000, (
        f"月額 should win over ACV: {both.monthly_price_yen[0]}"
    )


def test_monthly_burn_phrasing_does_not_flip_model_grain() -> None:
    """'monthly burn' is a metric, not a request for a month-by-month model."""
    assert kernel.extract_model_grain(SAAS_STORY) == "annual"
    facts = kernel.derive_source_facts(SAAS_STORY)
    assert facts.grain == "annual"


def test_explicit_monthly_model_request_is_still_detected() -> None:
    """An explicit monthly-model request must still produce a monthly grain."""
    assert kernel.extract_model_grain("Build a monthly model for the seed plan.") == "monthly"
    assert kernel.extract_model_grain("月次モデルでシード計画を作る") == "monthly"


def test_demand_ramp_reaches_stated_arr() -> None:
    """A narrative ARR target must anchor the demand ramp, not be ignored.

    The SaaS story states roughly ¥35億 ARR at maturity. A plan that lands an
    order of magnitude short of its own stated target is not investor-grade.
    """
    facts = kernel.derive_source_facts(SAAS_STORY)
    rows = _implied(facts)
    mature_revenue = rows[-1]["revenue"]
    target_arr = 3_500_000_000
    assert 0.6 * target_arr <= mature_revenue <= 1.6 * target_arr, (
        f"mature revenue ¥{mature_revenue:,.0f} is far from stated "
        f"¥{target_arr:,.0f} ARR target"
    )


def test_customer_count_reaches_stated_target() -> None:
    """A stated customer count ('600 paying customers') must be honored."""
    facts = kernel.derive_source_facts(SAAS_STORY)
    assert abs(facts.customers[-1] - 600) <= 30, (
        f"mature customer count {facts.customers[-1]} vs stated 600"
    )


def test_marketplace_gmv_honors_stated_maturity_target() -> None:
    """A marketplace story's stated maturity GMV must anchor the GMV ramp.

    The marketplace narrative states ¥120億 GMV at maturity. The ramp must land
    on that figure, not treat it as a period-0 base (which inflated it ~700x).
    """
    facts = kernel.derive_source_facts(MARKETPLACE_STORY)
    target = 12_000_000_000
    mature_gmv = facts.gmv_yen[-1]
    assert 0.7 * target <= mature_gmv <= 1.5 * target, (
        f"mature GMV ¥{mature_gmv:,.0f} is far from stated ¥{target:,.0f} target"
    )


def test_marketplace_present_value_gmv_stays_period_zero_base() -> None:
    """A present-value GMV ("GMV is ¥10B") must seed the base, not the maturity.

    Guards against a maturity-cue false positive silently scaling a stated
    current GMV down to a small period-0 figure.
    """
    facts = kernel.derive_source_facts(
        "# Marketplace plan\nThe company is a marketplace startup. GMV is ¥10B "
        "today, take rate is 12%.\nSource: management memo.\n"
    )
    assert facts.gmv_yen[0] >= 9_000_000_000, (
        f"present-value GMV scaled down to period-0 ¥{facts.gmv_yen[0]:,.0f}"
    )


USD_STORY = """# Seed B2B SaaS equity story (USD)

A US-based B2B SaaS company. The model must support a seed fundraise: 5-year
integrated plan, runway, unit economics, and dilution. Pricing is a per-seat
subscription at $80 per seat per month. Phase 1 targets $12M ARR at maturity.
Gross margin target is about 80%.

Source: customer discovery memo, investor benchmark notes.
"""


def test_usd_narrative_produces_a_coherent_usd_plan() -> None:
    """A USD narrative is modeled in USD, at the stated scale, with USD-scale costs."""
    facts = kernel.derive_source_facts(USD_STORY)
    assert facts.currency == "USD", f"currency not detected as USD: {facts.currency}"
    assert facts.monthly_price_yen[0] == 80, (
        f"per-seat price '$80' not extracted: {facts.monthly_price_yen[0]}"
    )
    # JPY default magnitudes must be FX-scaled — a USD plan cannot carry a
    # ¥16M loaded comp read as $16M, nor a ¥300M cash floor read as $300M.
    assert facts.avg_comp_yen[0] < 1_000_000, (
        f"loaded comp not FX-scaled for USD: {facts.avg_comp_yen[0]}"
    )
    assert facts.beginning_cash_yen < 50_000_000, (
        f"beginning cash not FX-scaled for USD: {facts.beginning_cash_yen}"
    )
    assert kernel.audit_economic_coherence(facts) == [], (
        "USD plan is not economically coherent"
    )


def test_jpy_narratives_are_not_misdetected_as_usd() -> None:
    """JPY stories — including ones citing a dollar-priced competitor — stay JPY."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        assert facts.currency == "JPY", f"{name} misdetected as {facts.currency}"
        # JPY magnitudes are unchanged (no FX scaling).
        assert facts.avg_comp_yen[0] >= 10_000_000, f"{name}: JPY comp was scaled"
    mixed = "# 計画\n月額1.2万円のSaaS。競合は $499/月。Source: メモ。"
    assert kernel.extract_currency(mixed) == "JPY"


def test_yaml_can_override_the_fx_rate() -> None:
    """The JPY-per-USD rate is overridable for USD plans via structured input."""
    facts = kernel.derive_source_facts(USD_STORY, jpy_per_usd=100.0)
    other = kernel.derive_source_facts(USD_STORY, jpy_per_usd=200.0)
    # A smaller divisor leaves larger USD magnitudes.
    assert facts.avg_comp_yen[0] > other.avg_comp_yen[0]


def test_payroll_is_not_absurd_at_maturity() -> None:
    """Mature-period payroll must not dwarf revenue (a sign of grain mixups)."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        rows = _implied(facts)
        ratio = rows[-1]["people_cost"] / rows[-1]["revenue"]
        assert ratio < 1.5, f"{name}: mature payroll/revenue ratio {ratio:.2f}"


def test_economic_audit_passes_for_healthy_archetypes() -> None:
    """The economic-coherence audit must clear a sound plan, every archetype."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        issues = kernel.audit_economic_coherence(facts)
        assert issues == [], f"{name}: unexpected economic-audit issues {issues}"


def test_economic_audit_catches_a_broken_cost_stack() -> None:
    """Inflating the cost drivers must surface a gross-margin violation."""
    from dataclasses import replace

    facts = kernel.derive_source_facts(SAAS_STORY)
    broken = replace(
        facts, delivery_cost_yen=[cost * 60 for cost in facts.delivery_cost_yen]
    )
    issues = kernel.audit_economic_coherence(broken)
    assert any("gross margin" in issue for issue in issues), issues


def test_economic_audit_catches_insolvency() -> None:
    """A plan stripped of its funding must be flagged insolvent and round-less."""
    from dataclasses import replace

    facts = kernel.derive_source_facts(SAAS_STORY)
    broken = replace(facts, equity_raise_yen=[0 for _ in facts.equity_raise_yen])
    issues = kernel.audit_economic_coherence(broken)
    assert any("insolven" in issue for issue in issues), issues
    assert any("funding round" in issue for issue in issues), issues


def test_economic_audit_catches_non_positive_revenue() -> None:
    """A period with no economic volume must be flagged as non-positive revenue."""
    from dataclasses import replace

    facts = kernel.derive_source_facts(SAAS_STORY)
    broken = replace(
        facts,
        new_units=[0 for _ in facts.new_units],
        gmv_yen=[0 for _ in facts.gmv_yen],
    )
    issues = kernel.audit_economic_coherence(broken)
    assert any("non-positive revenue" in issue for issue in issues), issues


def test_balance_sheet_balances_in_the_kernel_projection() -> None:
    """The projected balance sheet must satisfy A = L + E every period."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        for idx, period in enumerate(kernel.project_balance_sheet(facts)):
            tolerance = 1e-4 * max(1.0, abs(period["total_assets"]))
            assert abs(period["balance_check"]) <= tolerance, (
                f"{name} period {idx}: balance sheet off by "
                f"{period['balance_check']:,.0f}"
            )


def test_depreciation_uses_the_accumulated_asset_base() -> None:
    """D&A depreciates the accumulated asset base, capped at gross PP&E.

    The prior model charged only the current period's CapEx; mature-period D&A
    must now exceed that, and accumulated D&A may never exceed gross PP&E.
    """
    facts = kernel.derive_source_facts(HARDWARE_STORY)
    projection = kernel.project_plan_free_cash_flow(facts)
    cumulative_capex = accumulated_da = 0.0
    for idx, period in enumerate(projection):
        cumulative_capex += period["capex"]
        accumulated_da += period["depreciation"]
        assert accumulated_da <= cumulative_capex + 1.0, (
            f"period {idx}: accumulated D&A exceeds gross PP&E"
        )
    # Accumulated-base depreciation charges materially more over the horizon
    # than the old single-period model (each period's CapEx / life), which
    # would total cumulative-CapEx / life.
    life = facts.depreciation_life_months[-1] or 60
    single_period_total = cumulative_capex * 12.0 / life
    assert accumulated_da > single_period_total, (
        "D&A does not reflect the accumulated asset base"
    )


def test_economic_audit_flags_an_unbalanced_sheet() -> None:
    """The audit must surface a balance sheet that does not balance."""
    facts = kernel.derive_source_facts(SAAS_STORY)
    original = kernel.project_balance_sheet
    kernel.project_balance_sheet = lambda f: [
        {
            "total_assets": 1_000_000_000.0,
            "total_liabilities": 0.0,
            "total_equity": 0.0,
            "balance_check": 1_000_000_000.0,
        }
    ]
    try:
        issues = kernel.audit_economic_coherence(facts)
    finally:
        kernel.project_balance_sheet = original
    assert any("does not balance" in issue for issue in issues), issues


def test_workbook_balance_sheet_balances_when_recalculated() -> None:
    """The recalculated workbook BS must balance — A = L + E, every period."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        (Path(tmp) / "recalc").mkdir()
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        ws = wb["BS"]
        row = next(
            (cell.row for r in ws.iter_rows() for cell in r
             if cell.value == "Balance check"),
            None,
        )
        assert row is not None, "BS sheet missing 'Balance check' row"
        first_col = source_plan.START_PERIOD_COL
        facts = kernel.derive_source_facts(SAAS_STORY)
        for idx in range(len(facts.years)):
            check = ws.cell(row, first_col + idx).value
            assert check is not None and abs(float(check)) <= 1.0, (
                f"period {idx}: workbook balance sheet is off by {check}"
            )


def test_strict_audit_fails_on_economic_incoherence() -> None:
    """An economically incoherent plan must fail the strict-audit gate (rc 2)."""
    original = build_model.ek.audit_economic_coherence
    build_model.ek.audit_economic_coherence = lambda facts: ["forced economic issue"]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "m.xlsx"
            rc = build_model._main(["--output", str(out), "--strict-audit"])
            assert rc == 2, f"strict audit did not fail on an economic issue (rc={rc})"
    finally:
        build_model.ek.audit_economic_coherence = original


def test_cap_table_exit_waterfall_uses_post_round_cap_table() -> None:
    """The exit waterfall must distribute proceeds over the post-round FDSO.

    Running it on the pre-round input (empty preferred — converted SAFEs and the
    new priced round absent) over-credited founders: ~95% of proceeds against a
    post-round founder FDSO near 54%.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "cap.xlsx"
        build_model.build_model(None, out, mode="cap_table")
        wb = load_workbook(out, data_only=True)
        ws = wb["Ownership"]
        header = next(
            (cell for r in ws.iter_rows() for cell in r if cell.value == "Founder %"),
            None,
        )
        assert header is not None, "Exit Waterfall 'Founder %' column not found"
        # Collect contiguous scenario rows below the header until the column ends.
        founder_pcts = []
        for row in range(header.row + 1, ws.max_row + 1):
            value = ws.cell(row, header.column).value
            if not isinstance(value, (int, float)):
                break
            founder_pcts.append(value)
        assert founder_pcts, "no exit-waterfall founder-% scenarios found"
        # Post-round founders hold ~54-60% of the exit-relevant FDSO; a value
        # near 95% means the waterfall ran on the pre-round cap table.
        for pct in founder_pcts:
            assert 0.40 <= pct <= 0.70, (
                f"exit-waterfall founder % {pct:.3f} is inconsistent with the "
                f"post-round cap table"
            )


def test_dcf_forecast_fcf_is_not_floored_at_zero() -> None:
    """The explicit-period FCF sum must reflect real burn, not be floored at 0.

    Flooring `SUM(forecast FCF)` at zero discarded the cash a startup actually
    burns and, with a near-zero terminal value, drove DCF enterprise value to 0.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dcf.xlsx"
        build_model.build_model(None, out, mode="dcf_only")
        wb = load_workbook(out, data_only=False)
        ws = wb["Valuation"]
        row = next(
            (cell.row for r in ws.iter_rows() for cell in r
             if cell.value == "PV of forecast FCF"),
            None,
        )
        assert row is not None, "Valuation sheet missing 'PV of forecast FCF' row"
        first_col = source_plan.START_PERIOD_COL
        formulas = [
            ws.cell(row, c).value
            for c in range(first_col, ws.max_column + 1)
            if isinstance(ws.cell(row, c).value, str) and ws.cell(row, c).value.startswith("=")
        ]
        assert formulas, "no forecast-FCF formulas found"
        assert not any("MAX(0" in f for f in formulas), (
            "forecast FCF is still floored at zero"
        )


def test_dcf_enterprise_value_is_positive_and_method_consistent() -> None:
    """DCF EV must be a positive, method-consistent figure, not ~0."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dcf.xlsx"
        build_model.build_model(None, out, mode="dcf_only")
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "dcf.xlsx", data_only=True)
        ws = wb["Valuation"]

        # Derive the last period column from the period header row (row 5).
        final_col = max(
            cell.column
            for cell in ws[5]
            if cell.column >= source_plan.START_PERIOD_COL and cell.value
        )

        def final_value(label: str) -> float:
            row = next(
                (cell.row for r in ws.iter_rows() for cell in r
                 if cell.value == label),
                None,
            )
            assert row is not None, f"Valuation sheet missing '{label}' row"
            return float(ws.cell(row, final_col).value)

        dcf_ev = final_value("DCF EV")
        primary_ev = final_value("Primary-method EV")
        assert dcf_ev > 0, f"DCF EV is non-positive: {dcf_ev}"
        # An exit-multiple DCF should be the same order of magnitude as the
        # multiple-based EV — not collapsed near zero.
        assert dcf_ev >= 0.1 * primary_ev, (
            f"DCF EV {dcf_ev:,.0f} is implausibly small vs primary-method EV "
            f"{primary_ev:,.0f}"
        )


def test_funding_plan_keeps_the_company_solvent() -> None:
    """The sized funding plan must keep projected ending cash non-negative.

    A generated fundraise plan whose own cash goes negative is not
    investor-grade: the equity rounds must be sized against the projected
    free cash flow, not a fixed heuristic.
    """
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        projection = kernel.project_plan_free_cash_flow(facts)
        for i, period in enumerate(projection):
            assert period["ending_cash"] >= 0, (
                f"{name} period {i}: insolvent, ending cash "
                f"¥{period['ending_cash']:,.0f}"
            )


def test_seed_round_is_positive_across_archetypes() -> None:
    """Period 0 must always carry a positive round (the current raise)."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        assert facts.equity_raise_yen[0] > 0, f"{name}: no period-0 round"


def test_workbook_recalc_shows_no_insolvency() -> None:
    """The recalculated workbook must not go cash-negative in any period."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        ws = wb["CF"]
        first_col = source_plan.START_PERIOD_COL
        facts = kernel.derive_source_facts(SAAS_STORY)
        cash_row = next(
            (cell.row for row in ws.iter_rows() for cell in row
             if cell.value == "Ending cash"),
            None,
        )
        assert cash_row is not None, "CF sheet missing 'Ending cash' row"
        # Allow a small tolerance for kernel/workbook working-capital timing
        # rounding; reject genuine insolvency.
        tolerance = 0.02 * 3_500_000_000
        for idx in range(len(facts.years)):
            cash = ws.cell(cash_row, first_col + idx).value
            assert cash is not None and float(cash) >= -tolerance, (
                f"period {idx}: workbook ending cash ¥{cash:,.0f} is insolvent"
            )


def test_summarize_comps_aggregates_live_peer_margins() -> None:
    """Peer operating-margin bands are derived from the live fetch, not constants."""
    import live_comps as lc

    comps = [
        lc.PublicComp(
            ticker=ticker, name=ticker, currency="USD", market_cap=1e11,
            enterprise_value=1e11, revenue_multiple=8.0, ebitda_multiple=20.0,
            source_url="x", as_of_date="2026-05-17", status="current",
            gross_margin=gross, ebitda_margin=ebitda,
        )
        for ticker, gross, ebitda in [("A", 0.80, 0.25), ("B", 0.75, 0.20), ("C", 0.84, 0.30)]
    ]
    result = lc.summarize_comps(comps)
    assert result.gross_margin_median == 0.80
    assert result.gross_margin_low == 0.75
    assert result.gross_margin_high == 0.84
    assert result.ebitda_margin_median == 0.25


def _saas_facts_with_peer_comps():
    from dataclasses import replace

    facts = kernel.derive_source_facts(SAAS_STORY)
    return replace(
        facts,
        live_comps=[
            {"ticker": "CRM", "name": "Salesforce", "status": "current",
             "gross_margin": 0.77, "ebitda_margin": 0.30, "as_of_date": "2026-05-17",
             "revenue_multiple": 6.0, "ebitda_multiple": 18.0, "company_type": "public",
             "source_type": "public market data"},
            {"ticker": "NOW", "name": "ServiceNow", "status": "current",
             "gross_margin": 0.81, "ebitda_margin": 0.34, "as_of_date": "2026-05-17",
             "revenue_multiple": 12.0, "ebitda_multiple": 28.0, "company_type": "public",
             "source_type": "public market data"},
        ],
    )


def test_kpi_sheet_compares_plan_kpis_to_live_peers() -> None:
    """The KPI sheet juxtaposes plan KPIs with live-fetched peer margins."""
    wb = source_plan.build_source_plan_workbook_from_facts(_saas_facts_with_peer_comps())
    ws = wb["KPI"]
    texts = [c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str)]
    assert any("live public peers" in t for t in texts), "peer comparison section missing"
    # The peer median for the injected SaaS comps (0.77, 0.81) must appear live,
    # not a hard-coded band.
    numbers = [c.value for row in ws.iter_rows() for c in row if isinstance(c.value, (int, float))]
    assert any(abs(n - 0.79) < 1e-6 for n in numbers), "live peer median not written"
    # No cross-sheet reference: the block must survive focused-bundle pruning.
    section_rows = [
        c.row for row in ws.iter_rows() for c in row
        if isinstance(c.value, str) and "live public peers" in c.value
    ]
    formulas = [
        c.value for row in ws.iter_rows() for c in row
        if c.row > section_rows[0] and isinstance(c.value, str) and c.value.startswith("=")
    ]
    assert formulas, "peer comparison has no live formula"
    assert all("!" not in f for f in formulas), "peer block leaks a cross-sheet reference"


def test_peer_comparison_status_recalculates_without_error() -> None:
    """The plan-vs-peer status formula must resolve cleanly when recalculated."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "peers.xlsx"
        source_plan.build_source_plan_workbook_from_facts(_saas_facts_with_peer_comps()).save(out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "peers.xlsx", data_only=True)
        ws = wb["KPI"]
        statuses = {"below", "above", "within"}
        found = [
            c.value for row in ws.iter_rows() for c in row
            if isinstance(c.value, str) and c.value in statuses
        ]
        assert found, "no resolved plan-vs-peer status found on the KPI sheet"


def test_archetype_workbooks_pass_strict_audit() -> None:
    """Each archetype builds end to end and clears the strict audit gate."""
    with tempfile.TemporaryDirectory() as tmp:
        for name, story in ARCHETYPES.items():
            src = Path(tmp) / f"{name}.md"
            out = Path(tmp) / f"{name}.xlsx"
            src.write_text(story, encoding="utf-8")
            rc = build_model._main(
                ["--source-md", str(src), "--output", str(out), "--strict-audit"]
            )
            assert rc == 0, f"{name}: strict audit failed (rc={rc})"


def test_workbook_recalc_reconciles_with_kernel_gross_margin() -> None:
    """The recalculated workbook gross margin must match the kernel's intent."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        ws = wb["Cost Build"]
        gm_row = next(
            (cell.row for row in ws.iter_rows() for cell in row
             if cell.value == "Gross margin"),
            None,
        )
        assert gm_row is not None, "Cost Build sheet missing 'Gross margin' row"
        first_col = source_plan.START_PERIOD_COL
        facts = kernel.derive_source_facts(SAAS_STORY)
        for idx in range(len(facts.years)):
            recalced = ws.cell(gm_row, first_col + idx).value
            assert recalced is not None, f"period {idx}: gross margin not recalculated"
            assert abs(float(recalced) - facts.target_gross_margin[idx]) <= 0.04, (
                f"period {idx}: workbook GM {recalced} vs target "
                f"{facts.target_gross_margin[idx]}"
            )


def test_burn_multiple_does_not_explode_in_period_zero() -> None:
    """Period-0 burn multiple uses the full period-0 revenue as net-new
    revenue, not a zero year-over-year difference that forces the
    denominator and explodes the ratio to hundreds of millions."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        ws = wb["KPI"]
        first_col = source_plan.START_PERIOD_COL
        burn_row = next(
            (cell.row for row in ws.iter_rows() for cell in row
             if cell.value == "Burn multiple"),
            None,
        )
        assert burn_row is not None, "KPI sheet missing 'Burn multiple' row"
        facts = kernel.derive_source_facts(SAAS_STORY)
        for idx in range(len(facts.years)):
            val = ws.cell(burn_row, first_col + idx).value
            if isinstance(val, str):  # "N/A" — no revenue growth to fund
                continue
            # A deliberately loose regression bound: it must reliably catch
            # the ~415,000,000x denominator-collapse explosion. A tighter
            # business band (burn multiple is "good" below ~2x) is not
            # asserted here because an early-stage period can legitimately
            # carry a high ratio; that judgement belongs to the audit, not
            # this guard.
            assert val is not None and abs(float(val)) < 50.0, (
                f"period {idx}: burn multiple {val} is not a sane ratio"
            )


def _row_for_label(ws, label: str) -> int:
    """Return the row index whose first labelled cell matches `label`."""
    row = next(
        (cell.row for r in ws.iter_rows() for cell in r if cell.value == label),
        None,
    )
    assert row is not None, f"{ws.title} sheet missing '{label}' row"
    return row


def test_runway_months_is_capped_at_99() -> None:
    """A near-zero-negative free cash flow against a large cash balance must
    not blow runway to thousands of months — the formula caps it at 99."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "runway.xlsx"
        facts = kernel.derive_source_facts(SAAS_STORY)
        wb = source_plan.build_source_plan_workbook_from_facts(facts)
        ws = wb["CF"]
        first_col = source_plan.START_PERIOD_COL
        # Force a tiny-negative free cash flow against a large cash balance:
        # the uncapped ratio would yield tens of millions of months. Rows are
        # resolved by label so a CF layout shift cannot silently mis-target.
        fcf_row = _row_for_label(ws, "Free cash flow")
        cash_row = _row_for_label(ws, "Ending cash")
        ws.cell(fcf_row, first_col).value = -1000
        ws.cell(cash_row, first_col).value = 5_000_000_000
        wb.save(out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb2 = load_workbook(Path(tmp) / "recalc" / "runway.xlsx", data_only=True)
        ws2 = wb2["CF"]
        runway_row = _row_for_label(ws2, "Runway months")
        # The MIN(99,...) cap is applied uniformly, so verify every period.
        for idx in range(len(facts.years)):
            runway = ws2.cell(runway_row, first_col + idx).value
            assert runway is not None and float(runway) <= 99.0, (
                f"period {idx}: runway {runway} months is not capped at 99"
            )


def test_kpi_dashboard_carries_vc_decision_metrics() -> None:
    """The KPI dashboard computes the core VC capital-efficiency and
    retention metrics as live cells that recalculate without error."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        ws = wb["KPI"]
        first_col = source_plan.START_PERIOD_COL
        facts = kernel.derive_source_facts(SAAS_STORY)
        assert any(
            c.value == "VC decision metrics"
            for row in ws.iter_rows() for c in row
        ), "KPI sheet missing the 'VC decision metrics' section"
        metrics = [
            "Rule of 40", "Net revenue retention",
            "Customer acquisition cost", "CAC payback", "Magic number",
        ]
        for label in metrics:
            row = _row_for_label(ws, label)
            for idx in range(len(facts.years)):
                val = ws.cell(row, first_col + idx).value
                assert val is not None, f"{label} period {idx} did not resolve"
                if isinstance(val, str):
                    assert val == "N/A", (
                        f"{label} period {idx}: unexpected text {val!r}"
                    )
                else:
                    float(val)  # numeric, finite


def test_rule_of_40_is_growth_plus_ebitda_margin() -> None:
    """Rule of 40 on the KPI sheet equals revenue growth plus EBITDA margin
    — it is composed from the live model cells, not a free-standing input."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        pytest.skip("soffice/libreoffice not available")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "saas.md"
        out = Path(tmp) / "saas.xlsx"
        src.write_text(SAAS_STORY, encoding="utf-8")
        source_plan.build_source_plan_workbook(src, out)
        subprocess.run(
            [soffice, "--headless", "--calc", "--convert-to", "xlsx",
             "--outdir", str(Path(tmp) / "recalc"), str(out)],
            check=True, capture_output=True, timeout=120,
        )
        wb = load_workbook(Path(tmp) / "recalc" / "saas.xlsx", data_only=True)
        kpi, rb, pl = wb["KPI"], wb["Revenue Build"], wb["P&L"]
        first_col = source_plan.START_PERIOD_COL
        r40 = _row_for_label(kpi, "Rule of 40")
        growth = _row_for_label(rb, "Revenue growth")
        ebitda_margin = _row_for_label(pl, "EBITDA margin")
        facts = kernel.derive_source_facts(SAAS_STORY)
        for idx in range(len(facts.years)):
            got = kpi.cell(r40, first_col + idx).value
            expected = (
                float(rb.cell(growth, first_col + idx).value)
                + float(pl.cell(ebitda_margin, first_col + idx).value)
            )
            assert abs(float(got) - expected) < 1e-6, (
                f"period {idx}: Rule of 40 {got} != growth + EBITDA margin "
                f"{expected}"
            )


def test_kpi_dashboard_omits_vc_block_for_an_ambiguous_mechanic() -> None:
    """The VC metrics block is gated: an ambiguous-mechanic plan gets the
    generic KPI set and keeps the original (unshifted) dashboard layout."""
    story = (
        "# Ambiguous plan\n\nA new venture with unclear revenue mechanics "
        "and weak evidence. 5-year plan, seed round. Source: management memo."
    )
    facts = kernel.derive_source_facts(story)
    assert kernel.mechanic_key(facts) == "generic"
    ws = source_plan.build_source_plan_workbook_from_facts(facts)["KPI"]
    labels = [
        c.value for row in ws.iter_rows() for c in row
        if isinstance(c.value, str)
    ]
    assert "VC decision metrics" not in labels, (
        "VC metrics section leaked into an ambiguous-mechanic plan"
    )
    for metric in ("Rule of 40", "Customer acquisition cost", "Magic number"):
        assert metric not in labels, (
            f"{metric} leaked into an ambiguous-mechanic plan"
        )
    # The layout is unshifted: the interpretation register stays at its base.
    assert any(
        c.value == "KPI interpretation register" and c.row == 62
        for row in ws.iter_rows() for c in row
    ), "ambiguous-mechanic KPI layout should not shift"


if __name__ == "__main__":
    _tests = [
        test_gross_margin_tracks_target_across_archetypes,
        test_stated_gross_margin_is_extracted_from_narrative,
        test_annual_pricing_is_converted_to_a_monthly_figure,
        test_monthly_burn_phrasing_does_not_flip_model_grain,
        test_explicit_monthly_model_request_is_still_detected,
        test_demand_ramp_reaches_stated_arr,
        test_customer_count_reaches_stated_target,
        test_marketplace_gmv_honors_stated_maturity_target,
        test_marketplace_present_value_gmv_stays_period_zero_base,
        test_usd_narrative_produces_a_coherent_usd_plan,
        test_jpy_narratives_are_not_misdetected_as_usd,
        test_yaml_can_override_the_fx_rate,
        test_payroll_is_not_absurd_at_maturity,
        test_economic_audit_passes_for_healthy_archetypes,
        test_economic_audit_catches_a_broken_cost_stack,
        test_economic_audit_catches_insolvency,
        test_economic_audit_catches_non_positive_revenue,
        test_balance_sheet_balances_in_the_kernel_projection,
        test_depreciation_uses_the_accumulated_asset_base,
        test_economic_audit_flags_an_unbalanced_sheet,
        test_workbook_balance_sheet_balances_when_recalculated,
        test_strict_audit_fails_on_economic_incoherence,
        test_cap_table_exit_waterfall_uses_post_round_cap_table,
        test_dcf_forecast_fcf_is_not_floored_at_zero,
        test_dcf_enterprise_value_is_positive_and_method_consistent,
        test_funding_plan_keeps_the_company_solvent,
        test_seed_round_is_positive_across_archetypes,
        test_workbook_recalc_shows_no_insolvency,
        test_summarize_comps_aggregates_live_peer_margins,
        test_kpi_sheet_compares_plan_kpis_to_live_peers,
        test_peer_comparison_status_recalculates_without_error,
        test_archetype_workbooks_pass_strict_audit,
        test_workbook_recalc_reconciles_with_kernel_gross_margin,
        test_burn_multiple_does_not_explode_in_period_zero,
        test_runway_months_is_capped_at_99,
        test_kpi_dashboard_carries_vc_decision_metrics,
        test_rule_of_40_is_growth_plus_ebitda_margin,
        test_kpi_dashboard_omits_vc_block_for_an_ambiguous_mechanic,
    ]
    for _test in _tests:
        try:
            _test()
            print(f"ok    {_test.__name__}")
        except pytest.skip.Exception as exc:  # soffice unavailable, etc.
            print(f"skip  {_test.__name__}: {exc}")
    print("done")
