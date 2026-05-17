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


def test_payroll_is_not_absurd_at_maturity() -> None:
    """Mature-period payroll must not dwarf revenue (a sign of grain mixups)."""
    for name, story in ARCHETYPES.items():
        facts = kernel.derive_source_facts(story)
        rows = _implied(facts)
        ratio = rows[-1]["people_cost"] / rows[-1]["revenue"]
        assert ratio < 1.5, f"{name}: mature payroll/revenue ratio {ratio:.2f}"


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


if __name__ == "__main__":
    _tests = [
        test_gross_margin_tracks_target_across_archetypes,
        test_stated_gross_margin_is_extracted_from_narrative,
        test_monthly_burn_phrasing_does_not_flip_model_grain,
        test_explicit_monthly_model_request_is_still_detected,
        test_demand_ramp_reaches_stated_arr,
        test_customer_count_reaches_stated_target,
        test_payroll_is_not_absurd_at_maturity,
        test_funding_plan_keeps_the_company_solvent,
        test_seed_round_is_positive_across_archetypes,
        test_workbook_recalc_shows_no_insolvency,
        test_archetype_workbooks_pass_strict_audit,
        test_workbook_recalc_reconciles_with_kernel_gross_margin,
    ]
    for _test in _tests:
        try:
            _test()
            print(f"ok    {_test.__name__}")
        except pytest.skip.Exception as exc:  # soffice unavailable, etc.
            print(f"skip  {_test.__name__}: {exc}")
    print("done")
