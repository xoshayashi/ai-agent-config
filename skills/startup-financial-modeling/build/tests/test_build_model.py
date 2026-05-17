"""Smoke tests for the startup-financial-modeling xlsx orchestrator.

Run directly:
    PYTHONPYCACHEPREFIX=$(mktemp -d) python3 skills/startup-financial-modeling/build/tests/test_build_model.py
"""

from __future__ import annotations

import sys
import tempfile
import re
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter, range_boundaries

SKILL_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = SKILL_DIR.parents[1]
RUNTIME_DIR = SKILL_DIR / "build" / "runtime"
SCRIPTS_DIR = RUNTIME_DIR
sys.path.insert(0, str(RUNTIME_DIR))

import build_model  # noqa: E402
import cap_table_builder as cap_table  # noqa: E402
import economic_kernel as kernel  # noqa: E402
import ib_format as ib  # noqa: E402
import live_comps  # noqa: E402
import source_plan_builder as source_plan  # noqa: E402

FIRST_VALUE_COL = source_plan.START_PERIOD_COL
SECOND_VALUE_COL = FIRST_VALUE_COL + 1
FIRST_VALUE_LETTER = source_plan.get_column_letter(FIRST_VALUE_COL)
SECOND_VALUE_LETTER = source_plan.get_column_letter(SECOND_VALUE_COL)
UNIT_COL = source_plan.LAYOUT.unit_col


def _fake_public_comps(tickers: list[str], *, timeout: float = 8.0) -> live_comps.PublicCompsResult:
    comps = [
        live_comps.PublicComp(
            ticker=ticker.strip().upper(),
            name=f"{ticker.strip().upper()} Test Comparable",
            currency="USD",
            market_cap=100_000_000_000.0,
            enterprise_value=110_000_000_000.0,
            revenue_multiple=8.0 + idx,
            ebitda_multiple=20.0 + idx,
            source_url=f"https://example.test/{ticker.strip().upper()}",
            as_of_date="2026-05-17",
            status="current",
        )
        for idx, ticker in enumerate(tickers)
        if ticker.strip()
    ]
    return live_comps.PublicCompsResult(
        comps=comps,
        revenue_multiple_median=9.0 if comps else None,
        ebitda_multiple_median=21.0 if comps else None,
        source_url="https://example.test/live-comps",
        as_of_date="2026-05-17",
    )


build_model.lc.fetch_public_comps = _fake_public_comps


def _column_width(ws, column_letter: str) -> float:
    dimension = ws.column_dimensions.get(column_letter)
    return dimension.width if dimension and dimension.width is not None else 0


def test_skill_exposes_clean_build_route_only() -> None:
    scanned_paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "build" / "evals" / "evals.json",
        SKILL_DIR / "scripts" / "build_model.py",
    ]
    scanned_paths.extend((SKILL_DIR / "build" / "references").glob("*.md"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in scanned_paths if path.exists())
    forbidden = [
        "workbook_" + "quality_" + "review",
        "quality " + "review",
        "review " + "score",
        "hard_" + "failures",
    ]
    required_references = [
        "_generic_composition_protocol.md",
        "_ib_workbook_design_system.md",
        "_self_review_protocol.md",
        "_benchmark_protocol.md",
        "_kpi_analytics.md",
        "_scenario_sensitivity_playbook.md",
        "_valuation_and_return_logic.md",
        "_ic_memo_depth.md",
    ]

    assert not (SCRIPTS_DIR / ("workbook_" + "quality_" + "review.py")).exists()
    assert [(SKILL_DIR / "build" / "references" / name).exists() for name in required_references] == [True] * len(required_references)
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    assert [name for name in required_references if name not in invocation_text] == []
    assert [term for term in forbidden if term in text] == []


def test_skill_uses_generic_economic_kernel_not_stage_matrix() -> None:
    scanned_paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "build" / "evals" / "evals.json",
        SKILL_DIR / "scripts" / "build_model.py",
    ]
    scanned_paths.extend((SKILL_DIR / "build" / "references").glob("*.md"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in scanned_paths if path.exists())
    normalized = text.lower()
    forbidden = [
        "ステージ × 業態 × 資金調達目的",
        "stage × business",
        "stage x business",
        "stage applicability",
        "applicability matrix",
        "source-backed investor plan",
        "mode-based monthly template",
        "monthly template",
    ]
    required_files = [
        SKILL_DIR / "build" / "references" / "_modeling_kernel.md",
        SKILL_DIR / "build" / "references" / "_coverage_universe.md",
    ]
    required_terms = [
        "economic kernel",
        "model grain",
        "driver tree",
        "operating engine",
        "capital stack",
        "ownership",
        "scenario",
        "valuation",
        "seed to pre-ipo",
    ]

    assert [path for path in required_files if not path.exists()] == []
    assert [term for term in forbidden if term in normalized] == []
    assert [term for term in required_terms if term not in normalized] == []


def test_prompt_guidance_resists_fixed_template_routing() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    generic_text = (SKILL_DIR / "build" / "references" / "_generic_composition_protocol.md").read_text(encoding="utf-8")
    output_modes_text = (SKILL_DIR / "build" / "references" / "_output_modes.md").read_text(encoding="utf-8")
    kpi_text = (SKILL_DIR / "build" / "references" / "_kpi_analytics.md").read_text(encoding="utf-8")
    skill_flat = " ".join("\n".join([skill_text, invocation_text]).lower().split())
    generic_flat = " ".join(generic_text.split())

    assert "examples, maturity cues, sectors, and modes are prompts for reasoning, not templates" in skill_flat
    assert "Choose tabs, KPIs, scenarios, valuation methods, colors, and cell positions from the decision" in generic_flat
    assert "These are not mandatory bundles" in output_modes_text
    assert "Maturity and mechanics are signals for selecting metrics, not metric packs" in kpi_text


def test_sheet_quality_rubric_covers_every_generated_sheet() -> None:
    rubric_text = (SKILL_DIR / "build" / "references" / "_sheet_quality_rubric.md").read_text(encoding="utf-8")
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    output_modes_text = (SKILL_DIR / "build" / "references" / "_output_modes.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")
    combined_flat = " ".join(
        "\n".join([rubric_text, skill_text, invocation_text, output_modes_text, self_review_text, eval_text]).split()
    )
    for sheet_name in source_plan.SOURCE_PLAN_SHEETS:
        assert f"| {sheet_name} |" in rubric_text
    for phrase in [
        "a distinct purpose, source boundary, dependency flow, checks where errors would matter, and interpretation",
        "Do not create a sheet just because it belongs to a canonical full-workbook order",
        "sheet-specific quality gates for purpose, source boundary, dependency flow, checks, and interpretation",
        "Load `_sheet_quality_rubric.md` for every xlsx build or repair",
        "Every included sheet must satisfy `_sheet_quality_rubric.md`",
        "Guide and Kernel define the decision, evidence, mechanics, and scope",
    ]:
        assert phrase in combined_flat


def test_economic_kernel_is_separate_from_workbook_renderer() -> None:
    builder_text = (SCRIPTS_DIR / "source_plan_builder.py").read_text(encoding="utf-8")
    required_profile_keys = {
        "marketplace",
        "hardware_asset_heavy",
        "pre_revenue_milestone",
        "recurring_software",
        "fintech_balance_sheet",
        "generic",
    }

    assert {profile.key for profile in kernel.MECHANIC_PROFILES} == required_profile_keys
    assert kernel.SourceFacts.__module__ == "economic_kernel"
    assert "class SourceFacts" not in builder_text
    assert "def _detect_mechanics" not in builder_text
    assert "def _money_yen" not in builder_text
    assert "def assumption_decomposition_for" not in builder_text
    assert "assumption_decomposition_for(facts)" in builder_text
    assert "from economic_kernel import" in builder_text


def test_japanese_money_units_parse_at_correct_scale() -> None:
    assert kernel.money_yen([r"([0-9,.]+)\s*(万|億|兆)"], "900億円", 0) == 90_000_000_000
    assert kernel.money_yen([r"([0-9,.]+)\s*(万|億|兆)"], "1.2兆円", 0) == 1_200_000_000_000
    assert kernel.money_yen([r"([0-9,.]+)\s*(万|億|兆)"], "3200万円", 0) == 32_000_000
    assert kernel.money_yen([r"([0-9,.]+)\s*(m|bn|b)"], "12bn", 0) == 12_000_000_000


def test_seed_to_pre_ipo_horizon_is_not_truncated_to_two_years() -> None:
    assert kernel.extract_forecast_periods("5年のpre-IPO financial modelを月次で作る", "monthly") == 60
    assert kernel.extract_forecast_periods("36か月のシード資金計画", "monthly") == 36


def test_generated_workbook_contains_interpretive_analysis_surfaces() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")
        wb = load_workbook(out, data_only=False)

        assert wb["KPI"].cell(_row_for_label(wb, "KPI", "KPI interpretation register"), source_plan.LAYOUT.first_hierarchy_col).value == "KPI interpretation register"
        assert wb["Scenarios"].cell(_row_for_label(wb, "Scenarios", "Scenario interpretation"), source_plan.LAYOUT.first_hierarchy_col).value == "Scenario interpretation"
        assert wb["Sensitivity"].cell(_row_for_label(wb, "Sensitivity", "Sensitivity rationale"), source_plan.LAYOUT.first_hierarchy_col).value == "Sensitivity rationale"
        assert wb["Valuation"].cell(_row_for_label(wb, "Valuation", "Method credibility"), source_plan.LAYOUT.first_hierarchy_col).value == "Method credibility"
        assert wb["Benchmarks"]["B5"].value == "source_id"
        memo_row = _row_for_label(wb, "IC Memo", "KPI readout")
        assert wb["IC Memo"].cell(memo_row, source_plan.LAYOUT.first_hierarchy_col).value == "KPI readout"
        assert isinstance(wb["IC Memo"].cell(memo_row + 1, source_plan.LAYOUT.label_col).value, str)
        assert wb["IC Memo"].cell(memo_row + 1, source_plan.LAYOUT.label_col).value.startswith("=")

        formulas = [formula for _, _, formula in _formula_cells(wb)]
        assert not any("AVERAGE(" in formula and "'Valuation'" not in formula for formula in formulas)
        assert "Primary-method EV" in "\n".join(str(cell.value) for cell in wb["Valuation"]["C"] if cell.value)
        assert "PV of forecast FCF" in "\n".join(str(cell.value) for cell in wb["Valuation"]["C"] if cell.value)
        assert "Illustrative IRR" in "\n".join(str(cell.value) for cell in wb["Valuation"]["C"] if cell.value)


def test_mechanic_specific_kpi_and_scenario_axes_are_rendered() -> None:
    cases = [
        ("# Marketplace\nMarketplace with GMV, take rate, buyer and seller liquidity. Source: management memo.", "Take rate", "GMV / liquidity scale"),
        ("# Robotics\nHardware robot deployment with BOM, service, lease financing and utilization. Source: management memo.", "Asset payback", "Deployment capacity scale"),
        ("# Lending\nFintech lending model with origination, credit loss, warehouse line and collections. Source: management memo.", "Loss / collection quality", "Warehouse / debt headroom"),
    ]
    for source_text, expected_kpi, expected_driver in cases:
        tmp, wb = _sample_source_workbook(source_text)
        try:
            kpi_text = "\n".join(str(cell.value) for row in wb["KPI"].iter_rows() for cell in row if cell.value is not None)
            scenario_text = "\n".join(str(cell.value) for row in wb["Scenarios"].iter_rows() for cell in row if cell.value is not None)
            assert expected_kpi in kpi_text
            assert expected_driver in scenario_text
        finally:
            tmp.cleanup()


def test_ambiguous_mechanics_use_generic_kpis_and_scenario_axes() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA new startup with unclear revenue mechanics and weak evidence. Source: management memo."
    )
    try:
        kpi_text = "\n".join(str(cell.value) for row in wb["KPI"].iter_rows() for cell in row if cell.value is not None)
        scenario_text = "\n".join(str(cell.value) for row in wb["Scenarios"].iter_rows() for cell in row if cell.value is not None)
        assert "Economic unit clarity" in kpi_text
        assert "Demand evidence scale" in scenario_text
        assert "CAC payback" not in kpi_text
        assert "New logo / conversion scale" not in scenario_text
    finally:
        tmp.cleanup()


def test_cost_labeled_scenario_drivers_pressure_costs_not_revenue() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nPre-revenue prototype company with milestone, prototype, grant, and hiring risk. Source: management memo."
    )
    try:
        ws = wb["Scenarios"]
        scenario_row = _row_for_label(wb, "Scenarios", "Prototype / program cost factor")
        assert ws.cell(scenario_row, source_plan.LAYOUT.label_col).value == "Prototype / program cost factor"
        revenue_formula = _first_year_cell_for_label(wb, "Scenarios", "Revenue").value
        gross_profit_formula = _first_year_cell_for_label(wb, "Scenarios", "Gross profit").value
        assert f"{FIRST_VALUE_LETTER}${scenario_row}" not in revenue_formula
        assert f"{FIRST_VALUE_LETTER}${scenario_row}" in gross_profit_formula
        hiring_row = _row_for_label(wb, "Scenarios", "Hiring capacity scale")
        ebitda_formula = _first_year_cell_for_label(wb, "Scenarios", "EBITDA").value
        assert f"{FIRST_VALUE_LETTER}${hiring_row}" not in revenue_formula
        assert f"{FIRST_VALUE_LETTER}${hiring_row}" in ebitda_formula
    finally:
        tmp.cleanup()


def test_unclassified_scenario_drivers_default_to_opex_not_revenue() -> None:
    revenue_factor, cost_factor, opex_factor, financing_factor = source_plan._scenario_driver_formula_terms(
        FIRST_VALUE_LETTER,
        (SimpleNamespace(label="Regulatory clearance readiness"),),
    )
    assert revenue_factor == "1"
    assert cost_factor == "1"
    assert opex_factor == f"{FIRST_VALUE_LETTER}$7"
    assert financing_factor == "1"


def test_financing_driver_downside_widens_funding_gap() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nAsset-heavy deployment startup with lease financing, warehouse capacity, and deployment risk. Source: management memo."
    )
    try:
        formula = _first_year_cell_for_label(wb, "Scenarios", "Funding gap").value
        financing_row = _row_for_label(wb, "Scenarios", "Financing capacity scale")
        assert f"MAX(0.01,{FIRST_VALUE_LETTER}${financing_row})" in formula
        assert f"-{FIRST_VALUE_LETTER}17/MAX" in formula
        assert f"-{FIRST_VALUE_LETTER}17*{FIRST_VALUE_LETTER}${financing_row}" not in formula
    finally:
        tmp.cleanup()


def test_cost_build_does_not_double_count_detailed_service_costs_in_variable_cogs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")
        wb = load_workbook(out, data_only=False)

        formula = _first_year_cell_for_label(wb, "Cost Build", "Variable COGS").value
        assert formula == f"={FIRST_VALUE_LETTER}7*'Assumptions'!{FIRST_VALUE_LETTER}24"
        assert "SUM('Assumptions'!" not in formula


def test_orchestrator_routes_through_generic_source_plan_builder() -> None:
    orchestrator_text = (SCRIPTS_DIR / "build_model.py").read_text(encoding="utf-8")

    assert "three_statement_builder" not in orchestrator_text
    assert "SaaS Series A defaults" not in orchestrator_text
    assert "00_Cover" not in orchestrator_text
    assert build_model.resolve_bundle("full") == source_plan.SOURCE_PLAN_SHEETS


def test_focused_modes_use_generic_kernel_after_bundle_filter() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        for mode in ("unit_economics", "three_statement"):
            out = Path(tmp) / f"{mode}.xlsx"
            build_model.build_model(None, out, mode=mode)
            wb = load_workbook(out, data_only=False)
            all_text = "\n".join(
                str(cell.value)
                for ws in wb.worksheets
                for row in ws.iter_rows()
                for cell in row
                if cell.value is not None
            )

            assert wb.sheetnames == build_model.resolve_bundle(mode)
            assert "Guide" in wb.sheetnames
            assert "Kernel" in wb.sheetnames
            assert "12_SanityChecks" not in wb.sheetnames
            assert "Demo SaaS" not in all_text
            assert "SaaS Series A" not in all_text


def test_focused_modes_are_formula_complete_without_compact_placeholders() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        for mode in build_model.VALID_MODES:
            out = Path(tmp) / f"{mode}.xlsx"
            build_model.build_model(None, out, mode=mode)
            wb = load_workbook(out, data_only=False)
            assert wb.sheetnames == build_model.resolve_bundle(mode)
            workbook_text = "\n".join(
                str(cell.value)
                for ws in wb.worksheets
                for row in ws.iter_rows()
                for cell in row
                if cell.value is not None
            )
            assert "compact mode placeholder" not in workbook_text
            assert "Original formula omitted from focused bundle" not in workbook_text
            assert build_model.audit_workbook(wb) == []


def test_integrated_model_has_ib_decision_gates_not_just_readouts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")
        wb = load_workbook(out, data_only=False)

        sotp_formula = _first_year_cell_for_label(wb, "Valuation", "SOTP EV").value
        selected_formula = _first_year_cell_for_label(wb, "Valuation", "Selected EV midpoint").value
        recommendation_formula = wb["IC Memo"].cell(
            _row_for_label(wb, "IC Memo", "Recommendation") + 1,
            source_plan.LAYOUT.label_col,
        ).value
        exit_headers = [
            wb["Exit Waterfall"].cell(5, col).value
            for col in range(2, 14)
        ]

        assert "Segments" in sotp_formula and "SUM" in sotp_formula
        assert "MEDIAN" in selected_formula and "Supportability" not in selected_formula
        assert isinstance(recommendation_formula, str) and "Proceed subject to DD gates" in recommendation_formula
        assert "Txn costs / escrow" in exit_headers
        assert "Preference floor" in exit_headers
        assert "Walk-away signal" in exit_headers
        assert _row_for_label(wb, "Valuation", "Valuation committee gates")
        assert _row_for_label(wb, "Pricing", "Pricing validation plan")
        assert build_model.audit_workbook(wb) == []


def test_comparable_evidence_loads_public_peers_by_default_and_overrides_multiples() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "live_comps.xlsx"
        build_model.build_model(None, out, mode="full")
        wb = load_workbook(out, data_only=False)
        benchmark_text = "\n".join(str(cell.value) for row in wb["Benchmarks"].iter_rows() for cell in row if cell.value is not None)

        assert _first_year_cell_for_label(wb, "Valuation", "Revenue multiple").value == 9.0
        assert _first_year_cell_for_label(wb, "Valuation", "EBITDA multiple").value == 21.0
        assert "Comparable evidence" in benchmark_text
        assert "public market data" in benchmark_text
        assert "current" in benchmark_text
        assert wb["Benchmarks"]["G9"].value == "current"


def test_default_live_comps_match_mechanic_labels_and_cli_overrides_yaml() -> None:
    recurring = kernel.derive_source_facts("# PLAN\nA recurring software startup with ARR.")
    marketplace = kernel.derive_source_facts("# PLAN\nMarketplace with GMV and take rate.")
    hardware = kernel.derive_source_facts("# PLAN\nHardware robot deployment with capex.")
    fintech = kernel.derive_source_facts("# PLAN\nFintech lending balance sheet with loans.")
    deeptech = kernel.derive_source_facts("# PLAN\nPre-revenue R&D milestone platform.")

    assert build_model._default_live_comps_for_facts(recurring) == ["CRM", "NOW", "DDOG"]
    assert build_model._default_live_comps_for_facts(marketplace) == ["UBER", "DASH", "ETSY"]
    assert build_model._default_live_comps_for_facts(hardware) == ["ISRG", "ROK", "TSLA"]
    assert build_model._default_live_comps_for_facts(fintech) == ["PYPL", "SOFI", "AFRM"]
    assert build_model._default_live_comps_for_facts(deeptech) == ["ISRG", "ROK", "TSLA"]

    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "comps.yaml"
        out = Path(tmp) / "override.xlsx"
        input_path.write_text("live_comps: [BAD1, BAD2]\n", encoding="utf-8")
        build_model.build_model(input_path, out, mode="full", live_comps=["CRM"])
        wb = load_workbook(out, data_only=False)
        text = "\n".join(str(cell.value) for row in wb["Benchmarks"].iter_rows() for cell in row if cell.value is not None)
        assert "CRM Test Comparable" in text
        assert "BAD1" not in text


def test_private_and_transaction_comps_are_included_in_comparable_evidence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "private_comps.yaml"
        out = Path(tmp) / "private_comps.xlsx"
        input_path.write_text(
            "\n".join([
                "private_comps:",
                "  - name: PrivateAI",
                "    company_type: private",
                "    source_type: funding round / press release",
                "    stage: Series B",
                "    geography: Japan",
                "    post_money: 12000000000",
                "    arr: 1000000000",
                "    currency: JPY",
                "    source_url: https://example.test/privateai-series-b",
                "    as_of_date: 2026-04-30",
                "    applicability_limits: ARR reported by company; verify security terms",
                "transaction_comps:",
                "  - name: Strategic SaaS acquisition",
                "    company_type: transaction",
                "    source_type: M&A announcement",
                "    enterprise_value: 50000000000",
                "    revenue: 5000000000",
                "    ebitda: 2000000000",
                "    as_of_date: 2025-12-15",
                "    source_url: https://example.test/ma-announcement",
            ]),
            encoding="utf-8",
        )
        build_model.build_model(input_path, out, mode="full")
        wb = load_workbook(out, data_only=False)
        text = "\n".join(str(cell.value) for row in wb["Benchmarks"].iter_rows() for cell in row if cell.value is not None)

        assert "PrivateAI" in text
        assert "private" in text
        assert "Strategic SaaS acquisition" in text
        assert "transaction" in text
        assert "ARR reported by company" in text
        assert _first_year_cell_for_label(wb, "Valuation", "Revenue multiple").value == 10.0


def test_incomplete_provided_comps_are_registered_but_not_used_for_medians() -> None:
    comps = live_comps.provided_comps_from_raw([
        {"name": "Undated PrivateCo", "post_money": 100_000_000, "arr": 10_000_000},
        {"name": "Dated PrivateCo", "post_money": 120_000_000, "arr": 10_000_000, "as_of_date": "2026-01-01"},
    ])
    result = live_comps.summarize_comps(comps)

    assert comps[0].status == "needs review"
    assert "missing source date" in comps[0].error
    assert comps[1].status == "provided"
    assert result.revenue_multiple_median == 12.0


def test_sec_ticker_lookup_is_cached_and_errors_are_compact() -> None:
    original_json_url = live_comps._json_url
    original_cache = live_comps._SEC_TICKER_LOOKUP_CACHE
    calls: list[str] = []

    def fake_json_url(url: str, *, timeout: float) -> dict:
        calls.append(url)
        return {
            "0": {"ticker": "CRM", "cik_str": 1108524, "title": "Salesforce, Inc."},
            "1": {"ticker": "NOW", "cik_str": 1373715, "title": "ServiceNow, Inc."},
        }

    try:
        live_comps._SEC_TICKER_LOOKUP_CACHE = None
        live_comps._json_url = fake_json_url
        assert live_comps._sec_cik_for_ticker("CRM", timeout=1.0) == ("0001108524", "Salesforce, Inc.")
        assert live_comps._sec_cik_for_ticker("NOW", timeout=1.0) == ("0001373715", "ServiceNow, Inc.")
        assert len(calls) == 1
        assert len(live_comps._compact_error("line one\n" + ("x" * 500), limit=80)) == 80
    finally:
        live_comps._json_url = original_json_url
        live_comps._SEC_TICKER_LOOKUP_CACHE = original_cache


def test_failed_live_comps_do_not_pollute_company_specific_sources_or_mark_live_multiples() -> None:
    def fake_failed_comps(tickers: list[str], *, timeout: float = 8.0) -> live_comps.PublicCompsResult:
        comps = [
            live_comps.PublicComp(
                ticker=ticker,
                name="",
                currency="",
                market_cap=None,
                enterprise_value=None,
                revenue_multiple=None,
                ebitda_multiple=None,
                source_url=f"https://example.test/{ticker}",
                as_of_date="2026-05-17",
                status="failed",
                error="HTTP Error 401: Unauthorized",
            )
            for ticker in tickers
        ]
        return live_comps.PublicCompsResult(
            comps=comps,
            revenue_multiple_median=None,
            ebitda_multiple_median=None,
            source_url="https://example.test/live-comps",
            as_of_date="2026-05-17",
        )

    original_fetch = build_model.lc.fetch_public_comps
    try:
        build_model.lc.fetch_public_comps = fake_failed_comps
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "failed.xlsx"
            build_model.build_model(None, out, mode="full")
            wb = load_workbook(out, data_only=False)
            assert _first_year_cell_for_label(wb, "Valuation", "Revenue multiple").value == 4
            assert wb["Valuation"].cell(_row_for_label(wb, "Valuation", "Revenue multiple"), source_plan.LAYOUT.source_col).value == "benchmark / refresh required"
            assert wb["Benchmarks"]["G9"].value == "needs refresh"
            assert wb["Benchmarks"]["E6"].value == "unknown"
            bench_text = "\n".join(str(cell.value) for row in wb["Benchmarks"].iter_rows() for cell in row if cell.value is not None)
            assert "HTTP Error 401" in bench_text
    finally:
        build_model.lc.fetch_public_comps = original_fetch


def _formula_cells(wb) -> list[tuple[str, str, str]]:
    formulas: list[tuple[str, str, str]] = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    formulas.append((ws.title, cell.coordinate, cell.value))
    return formulas


def _formula_error_cells(wb) -> list[str]:
    errors: list[str] = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("#"):
                    errors.append(f"{ws.title}!{cell.coordinate}={cell.value}")
    return errors


def _defined_name_count(wb) -> int:
    count = len(wb.defined_names)
    for ws in wb.worksheets:
        count += len(ws.defined_names)
    return count


def _font_rgb(cell) -> str | None:
    color = cell.font.color
    if color is None or getattr(color, "type", None) != "rgb":
        return None
    value = getattr(color, "rgb", None) or getattr(color, "value", None)
    if not isinstance(value, str):
        return None
    return value[-6:].upper()


def _chart_axis_title_text(chart) -> str:
    title = getattr(getattr(chart, "y_axis", None), "title", None)
    if title is None:
        return ""
    try:
        paragraphs = title.tx.rich.p
        return "".join(run.t for paragraph in paragraphs for run in (paragraph.r or []) if run.t)
    except AttributeError:
        return str(title)


def _tab_rgb(ws) -> str | None:
    color = ws.sheet_properties.tabColor
    if color is None or getattr(color, "type", None) != "rgb":
        return None
    value = getattr(color, "rgb", None)
    return value[-6:].upper() if isinstance(value, str) else None


def _sample_source_workbook(source_text: str):
    tmp = tempfile.TemporaryDirectory()
    source_md = Path(tmp.name) / "source.md"
    out = Path(tmp.name) / "source_plan.xlsx"
    source_md.write_text(source_text, encoding="utf-8")
    source_plan.build_source_plan_workbook(source_md, out)
    return tmp, load_workbook(out, data_only=False)


def test_full_model_uses_direct_formula_refs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")

        wb = load_workbook(out, data_only=False)
        assert wb.sheetnames == build_model.resolve_bundle("full")
        assert _defined_name_count(wb) == 0

        alias_formulas = [
            f"{sheet}!{cell}: {formula}"
            for sheet, cell, formula in _formula_cells(wb)
            if "INDEX(" in formula
        ]
        assert alias_formulas == []


def test_intra_sheet_formula_cells_are_black() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")

        wb = load_workbook(out, data_only=False)
        violations = [
            f"{sheet}!{cell}: {formula} color={color}"
            for sheet, cell, formula in _formula_cells(wb)
            if "!" not in formula
            for color in [_font_rgb(wb[sheet][cell])]
            if color is not None and color != ib.IB_FORMULA
        ]
        assert violations == []


def test_ic_memo_dependency_closure_matches_live_formula_readouts() -> None:
    bundle = build_model.resolve_bundle("market_sizing", additional_sheets=["IC Memo"])

    assert "IC Memo" in bundle
    assert "Kernel" in bundle
    assert "KPI" in bundle
    assert "Scenarios" in bundle
    assert "Capital Stack" in bundle
    assert "Ownership" in bundle
    assert "Valuation" in bundle


def test_cash_flow_runway_formula_floors_negative_cash_at_zero() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")

        wb = load_workbook(out, data_only=False)
        formula = _first_year_cell_for_label(wb, "CF", "Runway months").value

        assert formula == f"=IF({FIRST_VALUE_LETTER}16>=0,99,MAX(0,{FIRST_VALUE_LETTER}31)/ABS({FIRST_VALUE_LETTER}16/12))"


def test_cross_sheet_formula_cells_are_green() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")

        wb = load_workbook(out, data_only=False)
        violations = [
            f"{sheet}!{cell}: {formula} color={color}"
            for sheet, cell, formula in _formula_cells(wb)
            if "!" in formula
            for color in [_font_rgb(wb[sheet][cell])]
            if color != ib.IB_LINK_INTRA
        ]
        assert violations == []


def test_pricing_bundle_is_formula_complete() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pricing.xlsx"
        build_model.build_model(None, out, mode="pricing")

        wb = load_workbook(out, data_only=False)
        assert wb.sheetnames == build_model.resolve_bundle("pricing")
        assert "Pricing" in wb.sheetnames
        assert "Assumptions" in wb.sheetnames
        assert "CF" in wb.sheetnames
        assert "Valuation" in wb.sheetnames
        all_text = "\n".join(str(cell.value) for ws in wb.worksheets for row in ws.iter_rows() for cell in row if cell.value is not None)
        assert "compact mode placeholder" not in all_text
        assert build_model.audit_workbook(wb) == []
        assert _defined_name_count(wb) == 0


def test_cap_table_mode_uses_state_machine_not_full_workbook() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "cap_table.xlsx"
        build_model.build_model(None, out, mode="cap_table")

        wb = load_workbook(out, data_only=False)
        assert wb.sheetnames == ["Guide", "Kernel", "Ownership"]
        assert {"P&L", "BS", "CF", "Capital Stack", "Valuation", "IC Memo"}.isdisjoint(wb.sheetnames)
        ownership_text = "\n".join(
            str(cell.value)
            for row in wb["Ownership"].iter_rows()
            for cell in row
            if cell.value is not None
        )
        assert "Round Event State Machine" in ownership_text
        assert "SAFE / J-KISS Conversions" in ownership_text
        assert "Exit Waterfall" in ownership_text


def test_all_modes_produce_expected_bundles() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        for mode in build_model.VALID_MODES:
            out = Path(tmp) / f"{mode}.xlsx"
            build_model.build_model(None, out, mode=mode)

            wb = load_workbook(out, data_only=False)
            assert wb.sheetnames == build_model.resolve_bundle(mode)
            assert _defined_name_count(wb) == 0
            assert _merged_count(wb) == 0
            assert _wrapped_cells(wb) == []
            assert _manual_line_break_violations(wb) == []
            assert _styled_blank_cells(wb) == []
            assert _font_design_violations(wb) == []
            assert _semantic_alignment_violations(wb) == []
            for ws in wb.worksheets:
                assert ws.freeze_panes is None


def test_generated_modes_do_not_reference_removed_sheets() -> None:
    sheet_ref = re.compile(r"'([^']+)'!")
    with tempfile.TemporaryDirectory() as tmp:
        for mode in build_model.VALID_MODES:
            out = Path(tmp) / f"{mode}.xlsx"
            build_model.build_model(None, out, mode=mode)
            wb = load_workbook(out, data_only=False)
            missing_refs = []
            neutralized_cells = []
            for sheet, cell, formula in _formula_cells(wb):
                for target in sheet_ref.findall(formula):
                    if target not in wb.sheetnames:
                        missing_refs.append(f"{mode}:{sheet}!{cell}->{target}")
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value == "not in bundle":
                            neutralized_cells.append(f"{mode}:{ws.title}!{cell.coordinate}")
            assert missing_refs == []
            assert neutralized_cells == []


def test_structured_yaml_controls_grain_periods_and_drivers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "model.yaml"
        out = Path(tmp) / "structured.xlsx"
        input_path.write_text(
            "\n".join(
                [
                    "company: KernelCo",
                    "grain: monthly",
                    "periods: 6",
                    "start_year: 2026",
                    "segments: [Japan SaaS, Hardware]",
                    "new_units: [10, 20, 30, 40, 50, 60]",
                    "monthly_price_yen: [100000, 110000, 120000, 130000, 140000, 150000]",
                    "value_capture_share: [30%, 30%, 28%, 28%, 25%, 25%]",
                    "target_gross_margin: [65%, 65%, 68%, 68%, 70%, 70%]",
                    "support_tickets_per_customer: [10, 9, 8, 7, 6, 5]",
                    "evidence_status: pipeline-backed estimate",
                    "grants_yen: [10000000, 0, 0, 0, 0, 0]",
                    "convertibles_yen: [0, 50000000, 0, 0, 0, 0]",
                ]
            ),
            encoding="utf-8",
        )
        build_model.build_model(input_path, out, mode="full")
        wb = load_workbook(out, data_only=False)

        first_col = FIRST_VALUE_COL
        assert [wb["Assumptions"].cell(5, c).value for c in range(first_col, first_col + 6)] == ["M1", "M2", "M3", "M4", "M5", "M6"]
        assert wb["Guide"]["B7"].value == "Purpose"
        assert wb["Assumptions"].cell(7, first_col).value == 10
        assert wb["Assumptions"].cell(11, first_col + 5).value == 150000
        assert wb["Financing"].cell(7, first_col).value == 10000000
        assert wb["Financing"].cell(8, first_col + 1).value == 50000000
        assert wb["Segments"].cell(6, source_plan.LAYOUT.label_col).value == "Japan SaaS"
        assert wb["Assumptions"].cell(_row_for_label(wb, "Assumptions", "Value capture share"), first_col).value == 0.30
        assert wb["Assumptions"].cell(_row_for_label(wb, "Assumptions", "Target gross margin"), first_col).value == 0.65
        assert wb["Assumptions"].cell(_row_for_label(wb, "Assumptions", "Support tickets / customer / year"), first_col).value == 10
        assert wb["Assumptions"].cell(_row_for_label(wb, "Assumptions", "Pricing evidence status"), first_col).value == "pipeline-backed"


def test_balance_sheet_has_opening_capital_counterpart() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "full.xlsx"
        build_model.build_model(None, out, mode="full")
        wb = load_workbook(out, data_only=False)

        first_col = FIRST_VALUE_COL
        first_letter = FIRST_VALUE_LETTER
        assert wb["Assumptions"].cell(57, source_plan.LAYOUT.label_col).value == "Opening equity / prior capital"
        assert wb["BS"].cell(23, first_col).value == f"='Assumptions'!{first_letter}57+'Capital Stack'!{first_letter}7+'Financing'!{first_letter}7-'Financing'!{first_letter}13"
        assert wb["BS"].cell(27, first_col).value == f"={first_letter}15-{first_letter}21-{first_letter}25"


def test_mfn_applied_only_for_changed_safe_terms() -> None:
    inp = cap_table.CapTableInput(
        company_name="MFN Test",
        safes=[
            cap_table.SAFEInstrument(
                name="Best terms SAFE",
                type="j_kiss_v2",
                principal_money_m=20,
                cap_money_m=1_000,
                discount=0.20,
                mfn=True,
            ),
            cap_table.SAFEInstrument(
                name="Changed SAFE",
                type="j_kiss_v2",
                principal_money_m=20,
                cap_money_m=1_400,
                discount=0.10,
                mfn=True,
            ),
        ],
        round_pre_money_money_m=2_000,
        round_investment_money_m=500,
        round_target_pool_pct=0.10,
    )

    result = cap_table.run_round_state_machine(inp)
    mfn_flags = {safe.name: safe.mfn_applied for safe in result.safe_conversions}

    assert mfn_flags == {
        "Best terms SAFE": False,
        "Changed SAFE": True,
    }


def test_cap_table_rebuild_clears_prior_sheet_fills() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Ownership"
    ws["A1"].fill = PatternFill(fill_type="solid", fgColor="FFFF00")

    cap_table.build_cap_table_sheet(wb, cap_table.CapTableInput(company_name="Fill Test"))

    assert wb["Ownership"]["A1"].fill.fill_type in (None, "none")


def test_cap_table_rebuild_clears_legacy_layout_state() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Ownership"
    ws.freeze_panes = "C8"
    ws.merge_cells("B2:C2")
    ws["B1"] = "legacy"
    ws["B1"].alignment = Alignment(wrap_text=True, indent=2)

    cap_table.build_cap_table_sheet(wb, cap_table.CapTableInput(company_name="Layout State Test"))
    ws = wb["Ownership"]

    assert _merged_count(wb) == 0
    assert ws.freeze_panes is None
    assert ws.column_dimensions["A"].width == ib.COL_MARGIN_WIDTH
    assert ws.column_dimensions["B"].width == ib.COL_HIERARCHY_WIDTH
    assert ws["C1"].value == "Layout State Test — Cap Table"
    assert _wrapped_cells(wb) == []
    assert _leading_space_labels(wb) == []
    assert [
        f"{cell.coordinate}: {cell.alignment.indent}"
        for row in ws.iter_rows()
        for cell in row
        if getattr(cell.alignment, "indent", 0)
    ] == []


def test_cap_table_sheet_uses_canonical_design_surface() -> None:
    inp = cap_table.CapTableInput(
        company_name="Design Surface Test",
        safes=[
            cap_table.SAFEInstrument(
                name="Seed SAFE",
                type="j_kiss_v2",
                principal_money_m=20,
                cap_money_m=1_000,
                discount=0.20,
            )
        ],
        round_pre_money_money_m=2_000,
        round_investment_money_m=500,
        round_target_pool_pct=0.10,
    )
    round_result = cap_table.run_round_state_machine(inp)
    waterfall = [
        (
            3_000.0,
            cap_table.compute_exit_waterfall(inp=inp, exit_value_money_m=3_000.0),
        )
    ]
    wb = Workbook()
    ws = cap_table.build_cap_table_sheet(
        wb,
        inp,
        round_result=round_result,
        waterfall_scenarios=waterfall,
    )

    assert wb.sheetnames == ["Ownership"]
    assert _merged_count(wb) == 0
    assert ws.freeze_panes is None
    assert ws.sheet_view.showGridLines is False
    assert ws.print_area
    assert ws.page_setup.orientation == "landscape"
    assert ws.page_setup.fitToWidth == 1
    assert ws.print_title_rows in {"1:3", "$1:$3"}
    assert ws.print_title_cols in {"A:C", "$A:$C"}
    assert _column_width(ws, "A") == ib.COL_MARGIN_WIDTH
    assert _column_width(ws, "B") == ib.COL_HIERARCHY_WIDTH
    assert _column_width(ws, "C") >= ib.COL_LABEL_WIDTH
    assert _column_width(ws, "G") >= ib.COL_SOURCE_WIDTH
    assert _wrapped_cells(wb) == []
    assert _manual_line_break_violations(wb) == []
    assert _styled_blank_cells(wb) == []
    assert _design_band_span_violations(wb) == []
    assert _repeated_semantic_fill_rows(wb) == []
    assert _unknown_fill_color_violations(wb) == []
    assert _repeated_prominent_border_rows(wb) == []
    assert _hierarchy_spacer_border_violations(wb) == []
    assert _font_design_violations(wb) == []
    assert _border_density_violations(wb) == []
    assert _memo_note_border_violations(wb) == []
    assert _border_style_violations(wb) == []
    assert _border_color_violations(wb) == []
    assert _row_height_violations(wb) == []
    for row in (5, 25, 50, 70):
        assert [_fill_rgb(ws.cell(row=row, column=col)) for col in range(2, 8)] == [
            ib.BG_HEADER_BAND
        ] * 6


def _chart_count(wb) -> int:
    return sum(len(getattr(ws, "_charts", [])) for ws in wb.worksheets)


def _merged_count(wb) -> int:
    return sum(len(ws.merged_cells.ranges) for ws in wb.worksheets)


def _formula_count(wb) -> int:
    return len(_formula_cells(wb))


def _wrapped_cells(wb) -> list[str]:
    return [
        f"{ws.title}!{cell.coordinate}"
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for cell in row
        if cell.alignment is not None and cell.alignment.wrap_text is True
    ]


def test_ib_helpers_reject_wrap_text_true() -> None:
    wb = Workbook()
    ws = wb.active

    for apply_func in (ib.apply_label, ib.apply_comment):
        try:
            apply_func(ws["A1"], wrap_text=True)
        except ValueError as exc:
            assert "forbids wrap_text=True" in str(exc)
        else:
            raise AssertionError(f"{apply_func.__name__} accepted wrap_text=True")

    ib.apply_label(ws["A2"])
    ib.apply_comment(ws["A3"])
    assert ws["A2"].alignment.wrap_text is False
    assert ws["A3"].alignment.wrap_text is False
    assert ib.wrapped_text_row_height(3) == ib.ROW_HEIGHT_PER_WRAPPED_LINE * 3
    assert ib.wrapped_text_row_height(0) == ib.ROW_HEIGHT_PER_WRAPPED_LINE
    assert ib.visible_text_line_count("one\ntwo", "single") == 2
    ib.set_wrapped_exception_row_height(ws, 4, ib.visible_text_line_count("one\ntwo\nthree"))
    assert ws.row_dimensions[4].height == ib.ROW_HEIGHT_PER_WRAPPED_LINE * 3

    ws["A5"] = "bounded\nprose"
    try:
        ib.apply_wrapped_exception(
            ws["A5"],
            user_approved=False,
            bounded_prose=True,
            adjacent_cells_carry_meaning=True,
        )
    except ValueError as exc:
        assert "explicit user approval" in str(exc)
    else:
        raise AssertionError("apply_wrapped_exception accepted missing approval")

    try:
        ib.apply_wrapped_exception(
            ws["A5"],
            user_approved=True,
            bounded_prose=False,
            adjacent_cells_carry_meaning=True,
        )
    except ValueError as exc:
        assert "bounded table prose" in str(exc)
    else:
        raise AssertionError("apply_wrapped_exception accepted horizontal-read text")

    try:
        ib.apply_wrapped_exception(
            ws["A5"],
            user_approved=True,
            bounded_prose=True,
            adjacent_cells_carry_meaning=False,
        )
    except ValueError as exc:
        assert "adjacent table cells carry meaningful" in str(exc)
    else:
        raise AssertionError("apply_wrapped_exception accepted blank overflow text")

    ib.apply_wrapped_exception(
        ws["A5"],
        user_approved=True,
        bounded_prose=True,
        adjacent_cells_carry_meaning=True,
    )
    assert ws["A5"].alignment.wrap_text is True
    assert ws.row_dimensions[5].height == ib.wrapped_text_row_height(2)
    ws["A6"] = "bounded\nprose"
    ib.apply_wrapped_exception(
        ws["A6"],
        user_approved=True,
        bounded_prose=True,
        adjacent_cells_carry_meaning=True,
        line_count=0,
    )
    assert ws.row_dimensions[6].height == ib.wrapped_text_row_height(1)


def test_runtime_builders_do_not_use_wrap_or_merge_layout_shortcuts() -> None:
    runtime_files = [
        SCRIPTS_DIR / "build_model.py",
        SCRIPTS_DIR / "source_plan_builder.py",
        SCRIPTS_DIR / "cap_table_builder.py",
    ]
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        assert "wrap_text=True" not in text
        assert "apply_wrapped_exception(" not in text
        text_without_unmerge = text.replace("unmerge_cells(", "")
        assert ".merge_cells(" not in text_without_unmerge
        assert "merge_cells(" not in text_without_unmerge

    ib_text = (SCRIPTS_DIR / "ib_format.py").read_text(encoding="utf-8")
    ib_text_without_unmerge = ib_text.replace("unmerge_cells(", "")
    assert ".merge_cells(" not in ib_text_without_unmerge
    assert "merge_cells(" not in ib_text_without_unmerge
    assert "blank unstyled overflow cells without merging" in ib.WRAP_TEXT_ERROR
    assert "use_user_approved_bounded_prose_wrap_only" in ib.WRAP_DECISION_LADDER
    assert "final print/render column" in ib.WRAP_BEST_PRACTICE


def test_skill_guidance_makes_no_wrap_rule_explicit() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    layout_text = (SKILL_DIR / "build" / "references" / "_layout_canonical.md").read_text(encoding="utf-8")
    design_text = (SKILL_DIR / "build" / "references" / "_ib_workbook_design_system.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")
    ib_text = (SCRIPTS_DIR / "ib_format.py").read_text(encoding="utf-8")
    skill_full = "\n".join([skill_text, invocation_text])
    skill_flat = " ".join(skill_full.split())
    layout_flat = " ".join(layout_text.split())
    design_flat = " ".join(design_text.split())

    combined = "\n".join([skill_text, invocation_text, layout_text, design_text, self_review_text, eval_text, ib_text])
    assert "No-Wrap Rule" in combined
    assert "Treat text wrapping as prohibited" in skill_full
    assert "no merged cells" in skill_flat
    assert "blank unmerged unstyled overflow cells" in skill_flat
    assert "reject `wrap_text=True`" in design_text
    assert "Do not use merged cells as the repair" in design_flat
    assert "明示的に wrap_text=True" not in ib_text
    assert "set row height to the exact rendered visible line count" in skill_flat
    assert "clipped text, auto-height guesses, or oversized padded rows are design defects" in layout_flat
    assert "No-Merge Rule" in layout_text
    assert "let the text read horizontally through those blank cells without merging" in layout_flat
    assert "exact rendered visible line count" in design_flat
    assert "wrapped_text_row_height" in ib_text
    assert "set_wrapped_exception_row_height" in ib_text
    assert "row height matched exactly to the rendered visible line count" in eval_text
    assert "visible wrap/tall-text rows are audited by role" in eval_text
    assert "no unnecessary wrapping on horizontal-read" in eval_text
    assert "IB wrap decision ladder" in design_text
    assert "Use the IB wrap decision ladder" in skill_full
    assert "Horizontal-read rows must also have visual runway" in design_text
    assert "Manual line breaks are treated as wrapped exceptions" in design_text
    assert "blank unstyled overflow cells" in combined
    assert "user-approved prose or table cells" not in combined
    assert "blank overflow space" not in combined
    assert "bounded-prose" not in combined
    assert "bounded table prose" in combined
    assert "print/render boundary" in combined
    assert "XLSX_WRAP_DISCIPLINE" in eval_text


def test_skill_guidance_requires_fix_and_rerun_iteration() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")
    skill_flat = " ".join("\n".join([skill_text, invocation_text]).split())
    self_review_flat = " ".join(self_review_text.split())
    eval_flat = " ".join(eval_text.split())

    assert "fix the concrete failed items and rerun the same checks" in skill_flat
    assert "Do not treat model construction as completion" in skill_flat
    assert "command checks and rendered-output inspection for both finance logic and sheet design" in skill_flat
    assert "Keep iterating until the model logic and the visible sheet design are both sufficient" in skill_flat
    assert "command-based workbook checks and rendered-output inspection" in self_review_flat
    assert "Apply both to the finance model itself and to sheet design" in self_review_flat
    assert "Passing commands do not excuse a visibly poor sheet" in self_review_flat
    assert "a good-looking render does not excuse broken formulas" in self_review_flat
    assert "fix the concrete failed item, rerun the same check" in self_review_flat
    assert "Do not replace failed verification with a narrative explanation" in self_review_flat
    assert "Model creation is not completion" in eval_flat
    assert "verify both model logic and sheet design with command-based workbook checks plus rendered-output inspection" in eval_flat


def test_skill_guidance_uses_meaningful_sparse_fills_and_borders() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    layout_text = (SKILL_DIR / "build" / "references" / "_layout_canonical.md").read_text(encoding="utf-8")
    design_text = (SKILL_DIR / "build" / "references" / "_ib_workbook_design_system.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")

    skill_full = "\n".join([skill_text, invocation_text])
    combined = "\n".join([skill_full, layout_text, design_text, self_review_text, eval_text])
    combined_flat = " ".join(combined.split()).lower()
    assert "same non-heatmap fill" in combined_flat
    assert "background fills are selective accents for major semantic moments only" in combined_flat
    assert "avoid rainbow palettes" in combined_flat
    assert "role-based sparse fill palette" in eval_text
    assert "no rainbow or decorative background fills" in eval_text
    assert "ordinary calculation rows should stay white" in combined_flat
    assert "workbook tokens" in combined_flat
    assert "arial 10pt" in combined_flat
    assert "header / label row" in combined_flat
    assert "use one rectangular span per filled row component" in combined_flat
    assert "do not choose the end column only from cells that happen to contain text" in combined_flat
    assert "do not stop a fill because a cell is blank" in " ".join(skill_full.split()).lower()
    assert "for every filled row, name its role and inspect the start column, end column" in " ".join(self_review_text.split()).lower()
    assert "semantic row-span helper in\n`ib_format.py` for fill/border row components" in design_text
    assert "rectangular column-consistent fill and border spans chosen from the attached table/block" in eval_text
    assert "heavy border pattern or ragged populated-cell-only rule" in combined_flat
    assert "prominent borders follow the same meaning-first rule as fills" in combined_flat
    assert "do not stop a border because a cell is blank" in " ".join(skill_full.split()).lower()
    assert "draw the rule across that full span, including blank cells inside the component" in combined_flat
    assert "a blank cell inside the table/header/check width still receives the border" in combined_flat
    assert "check border span with the same positive rule as fill span" in combined_flat
    assert "dedicated hierarchy / indent columns stay borderless" in " ".join(skill_full.split()).lower()
    assert "b stays borderless and row rules begin at c" in combined_flat
    assert "confirm hierarchy / indent columns are not carrying row rules" in combined_flat
    assert "avoid repeating the same prominent top/bottom rule across adjacent rows" in " ".join(skill_full.split()).lower()
    assert "the same prominent border should not repeat on adjacent rows by default" in combined_flat
    assert "check border rhythm exactly as you check color rhythm" in combined_flat
    assert "no adjacent repeated prominent border rows" in eval_text
    assert "borders are not row-by-row decoration" in " ".join(skill_full.split()).lower()
    assert "memo, source, note, and interpretation cells are usually borderless" in combined_flat
    assert "three border styles by meaning" in combined_flat
    assert "border colors are black by default" in combined_flat
    assert "border color is black by default" in combined_flat
    assert "normal dotted for soft/provisional separations" in combined_flat
    assert "no per-row gridline borders" in eval_text
    assert "borderless memo/source/note cells" in eval_text
    assert "black border colors by default" in eval_text


def test_skill_guidance_enforces_ib_text_positioning() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    design_text = (SKILL_DIR / "build" / "references" / "_ib_workbook_design_system.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")
    ib_text = (RUNTIME_DIR / "ib_format.py").read_text(encoding="utf-8")
    combined_flat = " ".join("\n".join([skill_text, invocation_text, design_text, self_review_text, eval_text, ib_text]).split())

    for phrase in [
        "Investment-banking model alignment is functional, not decorative",
        "labels, sources, notes, titles, memos, and interpretation text are left-aligned",
        "numeric values, formulas, money, percentages, multiples, counts, and unit labels are right-aligned",
        "only period headers, scenario/matrix headers, and short column headers are centered",
        "Do not center long prose or labels",
        "Hierarchy is expressed with dedicated hierarchy/indent columns",
        "role-based left/right/center text alignment",
        "ALIGNMENT_BEST_PRACTICE",
    ]:
        assert phrase in combined_flat


def test_skill_guidance_enforces_ib_font_size_discipline() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    design_text = (SKILL_DIR / "build" / "references" / "_ib_workbook_design_system.md").read_text(encoding="utf-8")
    self_review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    eval_text = (SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8")
    ib_text = (RUNTIME_DIR / "ib_format.py").read_text(encoding="utf-8")
    combined_flat = " ".join("\n".join([skill_text, invocation_text, design_text, self_review_text, eval_text, ib_text]).split())

    for phrase in [
        "Font size discipline is equally strict",
        "Investment-banking models should look dense, legible, and standardized",
        "Use Arial 10pt for ordinary body cells",
        "Use Arial 9pt italic gray for supporting source, note, unit-helper, footnote",
        "Use 10-11pt bold for section labels and compact header rows",
        "Use Arial 14pt bold for sheet titles and cover/title surfaces only",
        "Keep the generated cell-size set intentionally small: 9, 10, 11, and 14pt",
        "Do not use 8pt cell text to squeeze content",
        "constrained 9/10/11/14pt cell-size palette",
        "FONT_SIZE_ALLOWED_CELLS",
        "FONT_SIZE_BEST_PRACTICE",
    ]:
        assert phrase in combined_flat


def test_xlsx_evals_load_full_design_reference_stack() -> None:
    evals = json.loads((SKILL_DIR / "build" / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    required = {"_layout_canonical", "_ib_workbook_design_system", "_self_review_protocol", "_sheet_quality_rubric"}
    missing = []
    for item in evals:
        refs = set(item.get("applicable_references", []))
        if not required <= refs:
            missing.append(f"{item['id']}:{item['name']} missing {sorted(required - refs)}")
        assertions = item.get("assertions", [])
        if not any(assertion.get("id") == "XLSX_DESIGN" for assertion in assertions):
            missing.append(f"{item['id']}:{item['name']} missing XLSX_DESIGN assertion")
        if not any(assertion.get("id") == "XLSX_SHEET_QUALITY" for assertion in assertions):
            missing.append(f"{item['id']}:{item['name']} missing XLSX_SHEET_QUALITY assertion")
        if not any(assertion.get("id") == "XLSX_WRAP_DISCIPLINE" for assertion in assertions):
            missing.append(f"{item['id']}:{item['name']} missing XLSX_WRAP_DISCIPLINE assertion")
        if not any(assertion.get("id") == "XLSX_FONT_HIERARCHY" for assertion in assertions):
            missing.append(f"{item['id']}:{item['name']} missing XLSX_FONT_HIERARCHY assertion")
        for assertion in assertions:
            if assertion.get("id") == "XLSX_DESIGN":
                text = assertion.get("text", "")
                if "rectangular semantic fill and border spans including member blank cells" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing semantic border span guidance")
                if "no rainbow or decorative background fills" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing restrained fill palette guidance")
                if "role-based sparse fill palette" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing role-based fill palette guidance")
                if "table-width row rules" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing table-width row rule guidance")
                if "start after hierarchy spacer columns" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing hierarchy-border start guidance")
                if "no adjacent repeated prominent border rows" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing border rhythm guidance")
                if "no per-row gridline borders" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing no-gridline border guidance")
                if "borderless memo/source/note cells" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing memo borderless guidance")
                if "three semantic border styles" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing border style guidance")
                if "black border colors by default" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing black border color guidance")
                if "sheet-specific quality gates for purpose, source boundary, dependency flow, checks, and interpretation" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing sheet-specific quality guidance")
                if "IB-style text positioning" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing IB text positioning guidance")
                if "left-aligned labels/sources/notes" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing left text alignment guidance")
                if "right-aligned values/formulas/units" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing right value alignment guidance")
                if "centered period/scenario/matrix headers only" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing centered-header-only guidance")
                if "IB-style font-size discipline" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing IB font-size guidance")
                if "9/10/11/14pt generated cell palette" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing constrained font-size palette guidance")
                if "no 8pt squeezed cell text or 16pt+ presentation headings" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing font-size anti-pattern guidance")
            if assertion.get("id") == "XLSX_SHEET_QUALITY":
                text = assertion.get("text", "")
                if "sheet-specific purpose, traceable source/evidence boundary" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing sheet purpose/evidence quality guidance")
                if "Focused tasks include only sheets needed for the decision" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing focused-sheet restraint guidance")
            if assertion.get("id") == "XLSX_WRAP_DISCIPLINE":
                text = assertion.get("text", "")
                if "generated cells keep wrap_text off by default" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing no-wrap default assertion")
                if "blank unmerged unstyled overflow cells" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing blank overflow assertion")
                if "final print/render column" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing print/render boundary assertion")
                if "manual line breaks appear only for user-approved bounded table prose" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing manual-line-break assertion")
                if "exact rendered visible-line-count row height" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing rendered-visible row-height assertion")
            if assertion.get("id") == "XLSX_FONT_HIERARCHY":
                text = assertion.get("text", "")
                if "constrained IB hierarchy" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing constrained font hierarchy assertion")
                if "9pt italic gray supporting source/note/unit-helper cells" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing 9pt support-cell assertion")
                if "10-11pt bold compact section/header cells" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing compact section/header assertion")
                if "8pt squeezed text" not in text or "16pt+ presentation headings" not in text:
                    missing.append(f"{item['id']}:{item['name']} missing font-size anti-pattern assertion")
    assert missing == []


def test_semantic_fill_helper_uses_rectangular_span_including_blanks() -> None:
    wb = Workbook()
    ws = wb.active
    ws.cell(3, 2, "Section")
    ws.cell(3, 5, "Last populated")

    ib.apply_semantic_fill_span(ws, 3, 2, 6, ib.BG_HEADER_BAND, bottom=ib.THIN_LINE)

    for col in range(2, 7):
        assert _fill_rgb(ws.cell(3, col)) == ib.BG_HEADER_BAND
        assert ws.cell(3, col).border.bottom.style == "thin"
    assert ws.cell(3, 7).fill.fill_type in (None, "none")
    assert ws.cell(3, 7).border.bottom.style is None

    ib.apply_semantic_fill_span(
        ws, 4, 2, 6, ib.BG_HEADER_BAND, bottom=ib.THIN_LINE, border_start_col=3
    )
    assert _fill_rgb(ws.cell(4, 2)) == ib.BG_HEADER_BAND
    assert ws.cell(4, 2).border.bottom.style is None
    for col in range(3, 7):
        assert ws.cell(4, col).border.bottom.style == "thin"
    try:
        ib.apply_semantic_fill_span(
            ws, 5, 2, 6, ib.BG_HEADER_BAND, bottom=ib.THIN_LINE, border_start_col=7
        )
        raise AssertionError("border_start_col beyond the span should fail")
    except ValueError as exc:
        assert "must be within span 2:6" in str(exc)

    ib.apply_box_border(ws, "B7:D9", inner_dotted=True)
    assert ws["C8"].border.top.style == "dotted"
    assert ws["C8"].border.left.style == "dotted"

    source_plan._section(ws, 11, "Section before layout setup", end_col=6)
    assert _fill_rgb(ws.cell(11, source_plan.LAYOUT.first_hierarchy_col)) == ib.BG_HEADER_BAND
    assert ws.cell(11, source_plan.LAYOUT.first_hierarchy_col).border.bottom.style is None
    for col in range(source_plan.LAYOUT.label_col, 7):
        assert ws.cell(11, col).border.bottom.style == "thin"

    ws.cell(13, source_plan.LAYOUT.label_col, "Selected output")
    ws.cell(13, source_plan.LAYOUT.source_col, "source note")
    ws.cell(13, source_plan.LAYOUT.unit_col, "JPY")
    ws.cell(13, FIRST_VALUE_COL, 1)
    source_plan._highlight_row(ws, 13, FIRST_VALUE_COL)
    assert ws.cell(13, source_plan.LAYOUT.label_col).border.top.style == "thin"
    assert ws.cell(13, source_plan.LAYOUT.source_col).border.top.style is None
    assert ws.cell(13, source_plan.LAYOUT.unit_col).border.top.style is None
    assert ws.cell(13, FIRST_VALUE_COL).border.top.style == "thin"


def _unit_label_violations(wb) -> list[str]:
    bad_fragments = ("単位:", "単位：", "Unit:", "JPY M", "JPY B")
    return [
        f"{ws.title}!{cell.coordinate}: {cell.value}"
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and any(fragment in cell.value for fragment in bad_fragments)
    ]


def _raw_money_scale_formula_violations(wb) -> list[str]:
    money_units = {"円", "千円", "百万円", "億円", "$", "$K", "$M"}
    violations = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            unit = ws.cell(row=row[0].row, column=UNIT_COL).value
            if unit not in money_units:
                continue
            for cell in row:
                if (
                    isinstance(cell.value, str)
                    and cell.value.startswith("=")
                    and ("/1000000" in cell.value or "*1000000" in cell.value)
                ):
                    violations.append(f"{ws.title}!{cell.coordinate}: {cell.value}")
    return violations


def _numbered_section_labels(wb) -> list[str]:
    import re

    pattern = re.compile(r"^\d+\.\s+\D")
    return [
        f"{ws.title}!{cell.coordinate}: {cell.value}"
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and pattern.match(cell.value.strip())
    ]


def _leading_space_labels(wb) -> list[str]:
    return [
        f"{ws.title}!{cell.coordinate}: {cell.value!r}"
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and cell.value.startswith((" ", "\t"))
    ]


def _missing_section_band_fills(wb) -> list[str]:
    missing = []
    for ws in wb.worksheets:
        for row_idx in range(1, ws.max_row + 1):
            label = ws.cell(row_idx, source_plan.LAYOUT.first_hierarchy_col)
            if not isinstance(label.value, str):
                continue
            label_fill = label.fill
            is_section = (
                label_fill.fill_type == "solid"
                and isinstance(label_fill.fgColor.rgb, str)
                and label_fill.fgColor.rgb.endswith(ib.BG_HEADER_BAND)
            )
            if not is_section:
                continue
            font = label.font
            label_has_white_text = font.color is not None and str(font.color.rgb).endswith("FFFFFF")
            band_cells = []
            for col in range(source_plan.LAYOUT.first_hierarchy_col, ws.max_column + 1):
                cell = ws.cell(row_idx, col)
                if _fill_rgb(cell) == ib.BG_HEADER_BAND:
                    band_cells.append(cell)
            band_is_contiguous = band_cells and [cell.column for cell in band_cells] == list(range(band_cells[0].column, band_cells[-1].column + 1))
            following_cols = [
                cell.column
                for next_row in range(row_idx + 1, min(ws.max_row, row_idx + 3) + 1)
                for cell in ws[next_row]
                if cell.value is not None
            ]
            attached_width_col = max([source_plan.LAYOUT.label_col, *following_cols])
            if not (label_has_white_text and band_is_contiguous and band_cells[-1].column >= attached_width_col):
                missing.append(f"{ws.title}!{label.coordinate}")
    return missing


def _styled_blank_cells(wb) -> list[str]:
    bad = []
    semantic_fill_colors = {
        ib.BG_TABLE_HEADER,
        ib.BG_TOTAL_BAND,
        ib.BG_HEADER_BAND,
        ib.BG_WORKING,
    }
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value not in (None, "") or cell.style_id == 0:
                    continue
                color = _fill_rgb(cell)
                if color in semantic_fill_colors:
                    same_fill_run = []
                    col = cell.column
                    while col >= 1 and _fill_rgb(ws.cell(cell.row, col)) == color:
                        same_fill_run.append(ws.cell(cell.row, col))
                        col -= 1
                    col = cell.column + 1
                    while col <= ws.max_column and _fill_rgb(ws.cell(cell.row, col)) == color:
                        same_fill_run.append(ws.cell(cell.row, col))
                        col += 1
                    if any(run_cell.value not in (None, "") for run_cell in same_fill_run):
                        continue
                bad.append(f"{ws.title}!{cell.coordinate}: style_id={cell.style_id}")
    return bad


def _manual_line_break_violations(wb) -> list[str]:
    violations = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if not (isinstance(cell.value, str) and "\n" in cell.value):
                    continue
                if cell.alignment is None or cell.alignment.wrap_text is not True:
                    violations.append(f"{ws.title}!{cell.coordinate}: manual line break without wrapped exception")
                    continue
                expected = ib.wrapped_text_row_height(ib.visible_text_line_count(cell.value))
                actual = ws.row_dimensions[cell.row].height
                if actual != expected:
                    violations.append(
                        f"{ws.title}!{cell.coordinate}: height={actual} expected={expected}"
                    )
    return violations


def _design_band_span_violations(wb) -> list[str]:
    violations = []
    band_colors = {ib.BG_TABLE_HEADER, ib.BG_WORKING}
    for ws in wb.worksheets:
        max_col = max(ws.max_column, 9)
        for row_idx in range(1, ws.max_row + 1):
            row = [ws.cell(row=row_idx, column=col) for col in range(2, max_col + 1)]
            populated = [cell for cell in row if cell.value is not None]
            colors = [_fill_rgb(cell) for cell in populated]
            row_band = next((color for color in colors if color in band_colors), None)
            if row_band is None:
                continue
            if row_band == ib.BG_WORKING:
                # Working highlights may intentionally stop before note columns.
                last = max(cell.column for cell in populated if _fill_rgb(cell) == row_band)
                check_cells = [ws.cell(row=row_idx, column=col) for col in range(2, last + 1)]
            else:
                first = min(cell.column for cell in populated if _fill_rgb(cell) == row_band)
                last = max(cell.column for cell in populated if _fill_rgb(cell) == row_band)
                check_cells = [ws.cell(row=row_idx, column=col) for col in range(first, last + 1)]
            for cell in check_cells:
                if _fill_rgb(cell) != row_band:
                    violations.append(f"{ws.title}!{cell.coordinate}: expected row band {row_band}")
    return violations


def _repeated_semantic_fill_rows(wb) -> list[str]:
    violations = []
    semantic_fill_colors = {
        ib.BG_TABLE_HEADER,
        ib.BG_TOTAL_BAND,
        ib.BG_HEADER_BAND,
        ib.BG_WORKING,
    }
    for ws in wb.worksheets:
        previous_color = None
        previous_row = None
        for row_idx in range(1, ws.max_row + 1):
            colors = [
                _fill_rgb(ws.cell(row=row_idx, column=col))
                for col in range(1, ws.max_column + 1)
            ]
            row_colors = [color for color in colors if color in semantic_fill_colors]
            row_color = max(set(row_colors), key=row_colors.count) if row_colors else None
            if row_color is not None and row_color == previous_color:
                violations.append(f"{ws.title}!{previous_row}:{row_idx}: repeated semantic fill {row_color}")
            previous_color = row_color
            previous_row = row_idx if row_color is not None else None
    return violations


def _unknown_fill_color_violations(wb) -> list[str]:
    allowed = {
        ib.BG_CANVAS,
        ib.BG_TABLE_HEADER,
        ib.BG_TOTAL_BAND,
        ib.BG_HEADER_BAND,
        ib.BG_WORKING,
    }
    violations = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                color = _fill_rgb(cell)
                if color is not None and color not in allowed:
                    violations.append(f"{ws.title}!{cell.coordinate}: unexpected fill {color}")
    return violations


def _repeated_prominent_border_rows(wb) -> list[str]:
    violations = []
    prominent_styles = {"medium", "thick", "double"}
    for ws in wb.worksheets:
        previous_signature = None
        previous_row = None
        for row_idx in range(1, ws.max_row + 1):
            counts = {}
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col)
                for side_name in ("top", "bottom"):
                    style = getattr(getattr(cell.border, side_name), "style", None)
                    if style in prominent_styles:
                        key = (side_name, style)
                        counts[key] = counts.get(key, 0) + 1
            signature = max(counts, key=counts.get) if counts and max(counts.values()) >= 2 else None
            if signature is not None and signature == previous_signature:
                violations.append(
                    f"{ws.title}!{previous_row}:{row_idx}: repeated prominent border {signature[0]}={signature[1]}"
                )
            previous_signature = signature
            previous_row = row_idx if signature is not None else None
    return violations


def _hierarchy_spacer_border_violations(wb) -> list[str]:
    violations = []
    for ws in wb.worksheets:
        hierarchy_cols = [
            idx
            for idx in range(1, ws.max_column + 1)
            if abs(float(ws.column_dimensions[get_column_letter(idx)].width or 0) - float(ib.COL_HIERARCHY_WIDTH)) < 0.001
        ]
        for row in range(1, ws.max_row + 1):
            for col in hierarchy_cols:
                cell = ws.cell(row=row, column=col)
                if any(
                    getattr(getattr(cell.border, side_name), "style", None)
                    for side_name in ("top", "bottom", "left", "right")
                ):
                    violations.append(f"{ws.title}!{cell.coordinate}: hierarchy spacer carries border")
    return violations


def _border_density_violations(wb) -> list[str]:
    violations = []
    for ws in wb.worksheets:
        bordered_rows = 0
        populated_rows = 0
        for row_idx in range(1, ws.max_row + 1):
            row_has_value = any(ws.cell(row=row_idx, column=col).value not in (None, "") for col in range(1, ws.max_column + 1))
            if not row_has_value:
                continue
            populated_rows += 1
            has_border = any(
                getattr(getattr(ws.cell(row=row_idx, column=col).border, side_name), "style", None)
                for col in range(1, ws.max_column + 1)
                for side_name in ("top", "bottom", "left", "right")
            )
            if has_border:
                bordered_rows += 1
        if populated_rows and bordered_rows / populated_rows > 0.45:
            violations.append(f"{ws.title}: bordered_rows={bordered_rows} populated_rows={populated_rows}")
    return violations


def _memo_note_border_violations(wb) -> list[str]:
    note_header_labels = {"source / driver", "source", "note", "notes", "memo", "interpretation"}
    violations = []
    for ws in wb.worksheets:
        note_cols = set()
        startup_note_col = getattr(ws, "_startup_note_col", None)
        if isinstance(startup_note_col, int):
            note_cols.add(startup_note_col)
        for row in ws.iter_rows():
            for cell in row:
                value = str(cell.value or "").strip().lower()
                if value in note_header_labels:
                    note_cols.add(cell.column)
        for col in note_cols:
            for cell in ws[get_column_letter(col)]:
                if cell.value in (None, ""):
                    continue
                value = str(cell.value or "").strip().lower()
                if value in note_header_labels:
                    continue
                if _fill_rgb(cell) in {ib.BG_TABLE_HEADER, ib.BG_HEADER_BAND}:
                    continue
                if any(
                    getattr(getattr(cell.border, side_name), "style", None)
                    for side_name in ("top", "bottom", "left", "right")
                ):
                    violations.append(f"{ws.title}!{cell.coordinate}: memo/source/note cell carries border")
    return violations


def _border_style_violations(wb) -> list[str]:
    allowed = {"thin", "medium", "dotted"}
    violations = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                for side_name in ("top", "bottom", "left", "right"):
                    style = getattr(getattr(cell.border, side_name), "style", None)
                    if style is not None and style not in allowed:
                        violations.append(f"{ws.title}!{cell.coordinate}: {side_name}={style}")
    return violations


def _border_color_violations(wb) -> list[str]:
    violations = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                for side_name in ("top", "bottom", "left", "right"):
                    side = getattr(cell.border, side_name)
                    if getattr(side, "style", None) is None:
                        continue
                    rgb = getattr(getattr(side, "color", None), "rgb", None)
                    if isinstance(rgb, str) and rgb[-6:].upper() == ib.IB_FORMULA:
                        continue
                    violations.append(f"{ws.title}!{cell.coordinate}: {side_name} border color={rgb}")
    return violations


def _font_design_violations(wb) -> list[str]:
    violations = []
    allowed_sizes = {float(size) for size in ib.FONT_SIZE_ALLOWED_CELLS}
    default_font = wb._fonts[0]
    if default_font.name != ib.FONT_FAMILY or float(default_font.sz) != float(ib.FONT_SIZE_BASE):
        violations.append(f"workbook default font={default_font.name} size={default_font.sz}")
    normal_font = wb._named_styles["Normal"].font
    if normal_font.name != ib.FONT_FAMILY or float(normal_font.sz) != float(ib.FONT_SIZE_BASE):
        violations.append(f"Normal style font={normal_font.name} size={normal_font.sz}")
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                if cell.font.name != ib.FONT_FAMILY:
                    violations.append(f"{ws.title}!{cell.coordinate}: font={cell.font.name}")
                if cell.font.sz is not None:
                    size = float(cell.font.sz)
                    if size not in allowed_sizes:
                        violations.append(f"{ws.title}!{cell.coordinate}: size={cell.font.sz}")
                    if size == float(ib.FONT_SIZE_TINY):
                        violations.append(f"{ws.title}!{cell.coordinate}: tiny cell font={cell.font.sz}")
    return violations


def _semantic_alignment_violations(wb) -> list[str]:
    violations = []
    for ws in wb.worksheets:
        if not source_plan._uses_default_layout(ws):
            continue
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                alignment = cell.alignment
                horizontal = alignment.horizontal
                indent = getattr(alignment, "indent", 0)
                if cell.row == 5 and cell.column >= FIRST_VALUE_COL and horizontal != "center":
                    violations.append(f"{ws.title}!{cell.coordinate}: period header horizontal={horizontal}")
                elif cell.row != 5 and cell.column == source_plan.LAYOUT.source_col:
                    if horizontal != "left" or not cell.font.italic or _font_rgb(cell) != ib.IB_COMMENT:
                        violations.append(f"{ws.title}!{cell.coordinate}: source alignment/font")
                elif cell.row != 5 and cell.column == source_plan.LAYOUT.unit_col:
                    if horizontal != "right" or _font_rgb(cell) != ib.IB_COMMENT:
                        violations.append(f"{ws.title}!{cell.coordinate}: unit alignment/font")
                elif cell.row != 5 and cell.column in (source_plan.LAYOUT.first_hierarchy_col, source_plan.LAYOUT.label_col):
                    if horizontal != "left" or indent:
                        violations.append(f"{ws.title}!{cell.coordinate}: label horizontal={horizontal} indent={indent}")
                elif cell.row != 5 and cell.column >= FIRST_VALUE_COL:
                    if isinstance(cell.value, (int, float)) or (isinstance(cell.value, str) and cell.value.startswith("=")):
                        if horizontal != "right":
                            violations.append(f"{ws.title}!{cell.coordinate}: value horizontal={horizontal}")
    return violations


def _money_unit_format_mismatches(wb) -> list[str]:
    expected = {
        "円": {ib.FMT_JPY_YEN},
        "千円": {ib.FMT_JPY_THOUSAND},
        "百万円": {ib.FMT_MONEY, ib.FMT_MONEY_DECIMAL, ib.FMT_JPY_MILLION},
        "億円": {ib.FMT_JPY_HUNDRED_MILLION},
        "$": {ib.FMT_USD_DOLLAR},
        "$K": {ib.FMT_USD_THOUSAND},
        "$M": {ib.FMT_USD_MILLION},
    }
    mismatches = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            unit = ws.cell(row=row[0].row, column=UNIT_COL).value
            if unit not in expected:
                continue
            for cell in row[FIRST_VALUE_COL - 1:]:
                if cell.value is None:
                    continue
                if not (
                    isinstance(cell.value, (int, float))
                    or (isinstance(cell.value, str) and cell.value.startswith("="))
                ):
                    continue
                if cell.number_format not in expected[unit]:
                    mismatches.append(
                        f"{ws.title}!{cell.coordinate}: unit={unit} fmt={cell.number_format}"
                    )
    return mismatches


def _semantic_unit_format_mismatches(wb) -> list[str]:
    expected = {
        "%": {
            ib.FMT_PERCENT,
            ib.FMT_PERCENT_BPS,
            ib.FMT_PCT_0,
            ib.FMT_PCT_1,
            ib.FMT_PCT_2,
        },
        "x": {ib.FMT_MULTIPLE, ib.FMT_MULTIPLE_1, ib.FMT_MULTIPLE_2},
        "FTE": {ib.FMT_INTEGER, ib.FMT_NUM},
        "units": {ib.FMT_INTEGER, ib.FMT_NUM},
        "customers": {ib.FMT_INTEGER, ib.FMT_NUM},
        "count": {ib.FMT_INTEGER, ib.FMT_NUM},
        "months": {ib.FMT_NUM, ib.FMT_INTEGER},
        "days": {ib.FMT_NUM, ib.FMT_INTEGER},
    }
    mismatches = []
    for ws in wb.worksheets:
        if ws.max_column < FIRST_VALUE_COL:
            continue
        for row in ws.iter_rows():
            unit = ws.cell(row=row[0].row, column=UNIT_COL).value
            if unit not in expected:
                continue
            for cell in row[FIRST_VALUE_COL - 1:]:
                if cell.value is None:
                    continue
                if not (
                    isinstance(cell.value, (int, float))
                    or (isinstance(cell.value, str) and cell.value.startswith("="))
                ):
                    continue
                if cell.number_format not in expected[unit]:
                    mismatches.append(
                        f"{ws.title}!{cell.coordinate}: unit={unit} fmt={cell.number_format}"
                    )
    return mismatches


def _row_height_violations(wb) -> list[str]:
    allowed = {
        ib.ROW_HEIGHT_TIGHT,
        ib.ROW_HEIGHT_BASE,
        ib.ROW_HEIGHT_STANDARD,
        ib.ROW_HEIGHT_MEDIUM,
        ib.ROW_HEIGHT_RELAXED,
        ib.ROW_HEIGHT_HERO,
        ib.ROW_HEIGHT_COVER_TITLE,
    }
    violations = []
    for ws in wb.worksheets:
        for idx, dimension in ws.row_dimensions.items():
            if dimension.height is None:
                continue
            actual = float(dimension.height)
            if actual in allowed:
                continue
            wrapped_exception_heights = {
                ib.wrapped_text_row_height(ib.visible_text_line_count(cell.value))
                for cell in ws[idx]
                if isinstance(cell.value, str)
                and "\n" in cell.value
                and cell.alignment.wrap_text is True
            }
            if actual not in wrapped_exception_heights:
                violations.append(f"{ws.title}!{idx}: height={dimension.height}")
    return violations


def _fill_rgb(cell) -> str | None:
    fill = cell.fill
    if fill is None or fill.fill_type != "solid":
        return None
    value = getattr(fill.fgColor, "rgb", None)
    return value[-6:].upper() if isinstance(value, str) else None


def _row_for_label(wb, sheet_name: str, label: str) -> int:
    ws = wb[sheet_name]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value == label:
                return cell.row
    raise AssertionError(f"{sheet_name}: label not found: {label}")


def _unit_for_label(wb, sheet_name: str, label: str) -> object:
    return wb[sheet_name].cell(_row_for_label(wb, sheet_name, label), UNIT_COL).value


def _first_year_cell_for_label(wb, sheet_name: str, label: str):
    return wb[sheet_name].cell(_row_for_label(wb, sheet_name, label), FIRST_VALUE_COL)


def test_source_backed_plan_reaches_generic_kernel_shape() -> None:
    source_text = """# Asset deployment equity story

The company is an asset-heavy AI startup deploying specialized field devices
into operational sites. The model combines recurring lease fees, services, and
software. Unit pricing is 月額32万円. Phase 1 targets cumulative deployments of
3,000 units in three years and about 25,000 operating units at maturity, equal
to roughly ¥900億 ARR. Hardware cost starts around ¥8m per unit and declines with scale. The story
requires market sizing, competitive funding benchmarks, hiring, lease strategy,
scenario analysis, sensitivity analysis, and an investor-use funding plan.
Source: customer discovery memo, market sizing memo, lender discussion notes.
"""
    with tempfile.TemporaryDirectory() as tmp:
        source_md = Path(tmp) / "asset_deployment_story.md"
        out = Path(tmp) / "source_plan.xlsx"
        source_md.write_text(source_text, encoding="utf-8")

        source_plan.build_source_plan_workbook(source_md, out)
        wb = load_workbook(out, data_only=False)

        assert wb.sheetnames == source_plan.SOURCE_PLAN_SHEETS
        for sheet_name in [
            "Kernel",
            "Driver Tree",
            "Cost Build",
            "People Plan",
            "Capital Stack",
            "Ownership",
            "Market Support",
        ]:
            assert sheet_name in wb.sheetnames
        assert _defined_name_count(wb) == 0
        assert _merged_count(wb) == 0
        assert _formula_count(wb) >= 600
        assert _chart_count(wb) >= 5
        years = kernel.forecast_years(kernel.extract_start_year(source_text))
        assert wb["Assumptions"].cell(5, FIRST_VALUE_COL).value == f"FY{years[0]}"
        assert wb["Assumptions"].cell(5, FIRST_VALUE_COL + len(years) - 1).value == f"FY{years[-1]}"
        assert "Economic kernel" in str(wb["Kernel"]["B2"].value)
        assert "Monthly price" in str(wb["Guide"]["C8"].value)
        assert "customer discovery memo" in str(wb["Market Support"]["B8"].value)
        assert _wrapped_cells(wb) == []
        assert _manual_line_break_violations(wb) == []
        assert _unit_label_violations(wb) == []
        assert _raw_money_scale_formula_violations(wb) == []
        assert _numbered_section_labels(wb) == []
        assert _leading_space_labels(wb) == []
        assert _missing_section_band_fills(wb) == []
        assert _styled_blank_cells(wb) == []
        assert _design_band_span_violations(wb) == []
        assert _repeated_semantic_fill_rows(wb) == []
        assert _unknown_fill_color_violations(wb) == []
        assert _repeated_prominent_border_rows(wb) == []
        assert _hierarchy_spacer_border_violations(wb) == []
        assert _font_design_violations(wb) == []
        assert _semantic_alignment_violations(wb) == []
        assert _border_density_violations(wb) == []
        assert _memo_note_border_violations(wb) == []
        assert _border_style_violations(wb) == []
        assert _border_color_violations(wb) == []
        assert _money_unit_format_mismatches(wb) == []
        assert _unit_for_label(wb, "Assumptions", "New primary units") == "units"
        assert _unit_for_label(wb, "Assumptions", "Ending primary units") == "units"
        assert _unit_for_label(wb, "Assumptions", "Total customers") == "customers"
        assert _unit_for_label(wb, "Assumptions", "Monthly price / unit") == "円"
        assert _unit_for_label(wb, "Assumptions", "CapEx / primary unit") == "円"
        assert _unit_for_label(wb, "Assumptions", "Total headcount") == "FTE"
        assert _unit_for_label(wb, "Assumptions", "Avg loaded comp / FTE") == "円"
        assert source_plan._display_unit("JPY") == "円"
        assert source_plan._display_unit("JPY", ib.FMT_MONEY) == "百万円"
        assert source_plan._display_unit("JPY", ib.FMT_JPY_THOUSAND) == "千円"
        assert source_plan._display_unit("JPY K") == "千円"
        assert _unit_for_label(wb, "Capital Stack", "Equity financing") == "百万円"
        assert _unit_for_label(wb, "Ownership", "Founder ownership") == "%"
        assert _unit_for_label(wb, "Revenue Build", "Total customers") == "count"
        assert _unit_for_label(wb, "KPI", "Ending primary units") == "units"
        assert _unit_for_label(wb, "KPI", "Runway") == "months"
        assert _unit_for_label(wb, "People Plan", "Total headcount") == "FTE"
        assert _unit_for_label(wb, "Market Support", "TAM") == "百万円"
        for label in [
            "Demand support coverage",
            "Pricing support ratio",
            "COGS support ratio",
            "Ops-CS capacity coverage",
            "Runway support coverage",
        ]:
            assert _unit_for_label(wb, "Assumptions", label) == "x"
        for label in [
            "Demand evidence status",
            "Pricing evidence status",
            "COGS evidence status",
            "People evidence status",
            "Capital evidence status",
        ]:
            assert _unit_for_label(wb, "Assumptions", label) == "status"
            assert _first_year_cell_for_label(wb, "Assumptions", label).value == "estimate"
        assert _first_year_cell_for_label(wb, "Assumptions", "Implied variable COGS %").value == f"=IF({FIRST_VALUE_LETTER}11=0,0,{FIRST_VALUE_LETTER}88/({FIRST_VALUE_LETTER}11*12))"
        assert _first_year_cell_for_label(wb, "Assumptions", "Required Ops-CS FTE from ticket load").value == f"=IF({FIRST_VALUE_LETTER}86=0,0,{FIRST_VALUE_LETTER}13*{FIRST_VALUE_LETTER}84/{FIRST_VALUE_LETTER}86)"
        assert _first_year_cell_for_label(wb, "Assumptions", "New primary units").value > 0
        assert _first_year_cell_for_label(wb, "Assumptions", "New primary units").number_format == ib.FMT_INTEGER
        assert _first_year_cell_for_label(wb, "Assumptions", "CapEx / primary unit").value > 0
        assert _first_year_cell_for_label(wb, "Assumptions", "Avg loaded comp / FTE").value > 0
        assert _first_year_cell_for_label(wb, "Capital Stack", "Equity financing").value > 0
        assert _first_year_cell_for_label(wb, "KPI", "Runway").number_format == ib.FMT_NUM
        assert _first_year_cell_for_label(wb, "Market Support", "TAM").value >= 1_000_000_000_000
        assert _first_year_cell_for_label(wb, "Revenue Build", "Recurring revenue").value == f"={FIRST_VALUE_LETTER}9*{FIRST_VALUE_LETTER}11*12"
        assert _first_year_cell_for_label(wb, "KPI", "Unit payback").value == f'=IF({FIRST_VALUE_LETTER}9<=0,"N/A",\'Assumptions\'!{FIRST_VALUE_LETTER}38/{FIRST_VALUE_LETTER}9)'
        assert _fill_rgb(wb["BS"].cell(_row_for_label(wb, "BS", "Balance check"), FIRST_VALUE_COL)) == ib.BG_WORKING
        assert _fill_rgb(wb["Ownership"].cell(_row_for_label(wb, "Ownership", "Ownership check"), FIRST_VALUE_COL)) == ib.BG_WORKING
        assert _fill_rgb(wb["Valuation"].cell(_row_for_label(wb, "Valuation", "Selected EV midpoint"), FIRST_VALUE_COL)) == ib.BG_WORKING


def test_generated_workbook_has_sheet_specific_quality_markers() -> None:
    source_text = """# Asset deployment equity story

AI device deployment with 月額32万円 pricing, capex, financing, ownership,
valuation, market sizing, benchmark refresh, and DD needs.
Source: management memo, customer discovery memo.
"""
    expected_markers = {
        "Guide": ["Sheet-level acceptance criteria", "Workbook map"],
        "Kernel": ["Economic kernel", "Mechanics", "Engine composition"],
        "Assumptions": ["Source / driver", "Support ratio"],
        "Driver Tree": ["Decision relevance", "Workbook owner"],
        "Revenue Build": ["Revenue drivers", "Total revenue"],
        "Cost Build": ["Gross profit bridge", "Gross margin"],
        "People Plan": ["Total headcount", "Avg loaded comp / FTE"],
        "P&L": ["Gross profit", "EBITDA"],
        "BS": ["Balance check", "Total assets"],
        "CF": ["Operating cash flow", "Ending cash", "Runway"],
        "Capital Stack": ["Runway", "Illustrative post-money"],
        "Ownership": ["Ownership check", "Founder ownership"],
        "Pricing": ["Customer ROI", "Suggested floor price"],
        "Financing": ["Funding gap", "Financing cash inflow"],
        "Exit Waterfall": ["Investor proceeds", "Founder proceeds"],
        "Segments": ["Decision implication", "Source status"],
        "KPI": ["KPI interpretation register", "IC implication"],
        "Scenarios": ["Scenario interpretation", "Funding gap"],
        "Sensitivity": ["Sensitivity rationale", "Decision implication"],
        "Valuation": ["Method credibility", "Selected EV midpoint", "Valuation committee gates"],
        "Market Support": ["TAM / SAM / SOM bridge", "Source anchors"],
        "Benchmarks": ["source_id", "Applicability limits", "Refresh needed"],
        "IC Memo": ["Recommendation", "What must be true", "Ranked DD gates", "Walk-away conditions", "Source boundary"],
    }
    with tempfile.TemporaryDirectory() as tmp:
        source_md = Path(tmp) / "asset_deployment_story.md"
        out = Path(tmp) / "source_plan.xlsx"
        source_md.write_text(source_text, encoding="utf-8")

        source_plan.build_source_plan_workbook(source_md, out)
        wb = load_workbook(out, data_only=False)

        for sheet_name, markers in expected_markers.items():
            sheet_text = " ".join(
                str(cell.value)
                for row in wb[sheet_name].iter_rows()
                for cell in row
                if cell.value is not None
            )
            sheet_text_lower = sheet_text.lower()
            missing = [marker for marker in markers if marker.lower() not in sheet_text_lower]
            assert missing == [], f"{sheet_name}: missing {missing}"


def test_structured_yaml_currency_and_display_scale_are_generic() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "model.yaml"
        out = Path(tmp) / "usd_thousand.xlsx"
        input_path.write_text(
            "\n".join(
                [
                    "company: CurrencyCo",
                    "currency: USD",
                    "display_scale: thousand",
                    "periods: 3",
                    "new_units: [1, 2, 3]",
                    "gmv_yen: [1000000, 2000000, 3000000]",
                    "monthly_price_yen: [10000, 12000, 14000]",
                ]
            ),
            encoding="utf-8",
        )

        build_model.build_model(input_path, out, mode="full")
        wb = load_workbook(out, data_only=False)

        assert _unit_for_label(wb, "Assumptions", "Gross merchandise value") == "$K"
        assert _first_year_cell_for_label(wb, "Assumptions", "Gross merchandise value").number_format == ib.FMT_USD_THOUSAND
        assert _unit_for_label(wb, "Assumptions", "Monthly price / unit") == "$"
        assert _first_year_cell_for_label(wb, "Assumptions", "Monthly price / unit").number_format == ib.FMT_USD_DOLLAR
        assert _unit_for_label(wb, "Assumptions", "New primary units") == "units"
        assert _unit_for_label(wb, "People Plan", "Total headcount") == "FTE"
        assert _money_unit_format_mismatches(wb) == []
        assert _semantic_unit_format_mismatches(wb) == []


def test_money_units_are_raw_values_with_number_formats_not_scaled_values() -> None:
    source_text = """# Unit formatting plan

Asset-heavy startup with monthly price 月額32万円, target deployment of 3,000
units, and hardware cost around ¥8m per unit. Source: management memo.
"""
    tmp, wb = _sample_source_workbook(source_text)
    try:
        price_cell = _first_year_cell_for_label(wb, "Assumptions", "Monthly price / unit")
        revenue_cell = _first_year_cell_for_label(wb, "Revenue Build", "Recurring revenue")
        total_revenue_cell = _first_year_cell_for_label(wb, "Revenue Build", "Total revenue")
        capital_stack_cell = _first_year_cell_for_label(wb, "Capital Stack", "Ending cash")

        assert price_cell.value == 320000
        assert price_cell.number_format == ib.FMT_JPY_YEN
        assert _unit_for_label(wb, "Assumptions", "Monthly price / unit") == "円"
        assert isinstance(revenue_cell.value, str) and "/1000000" not in revenue_cell.value
        assert isinstance(total_revenue_cell.value, str) and "/1000000" not in total_revenue_cell.value
        assert total_revenue_cell.number_format == ib.FMT_MONEY
        assert _unit_for_label(wb, "Revenue Build", "Total revenue") == "百万円"
        assert capital_stack_cell.number_format == ib.FMT_MONEY
        assert _unit_for_label(wb, "Capital Stack", "Ending cash") == "百万円"
        assert _raw_money_scale_formula_violations(wb) == []
        assert _semantic_unit_format_mismatches(wb) == []
    finally:
        tmp.cleanup()


def test_non_money_units_keep_their_own_formats_and_formulas() -> None:
    assert source_plan._model_value("=A1/1000000", "units") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "customers") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "FTE") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "%") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "x") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "months") == "=A1/1000000"
    assert source_plan._model_value("=A1/1000000", "JPY") == "=A1"
    assert source_plan._model_value("=A1/1000000", "USD") == "=A1"
    assert source_plan._model_value(12, "units") == 12
    assert source_plan._model_value(12, "customers") == 12
    assert source_plan._model_value(12, "JPY M") == 12_000_000
    assert source_plan._model_value(12, "USD M") == 12_000_000
    assert source_plan._display_unit("USD") == "$"
    assert source_plan._display_unit("USD K") == "$K"
    assert source_plan._display_unit("USD M") == "$M"
    assert source_plan._format_for_unit("units", ib.FMT_MONEY) == ib.FMT_INTEGER
    assert source_plan._format_for_unit("customers", ib.FMT_MONEY) == ib.FMT_INTEGER
    assert source_plan._format_for_unit("FTE", ib.FMT_MONEY) == ib.FMT_INTEGER
    assert source_plan._format_for_unit("months", ib.FMT_MONEY) == ib.FMT_NUM
    assert source_plan._format_for_unit("%", ib.FMT_MONEY) == ib.FMT_PERCENT
    assert source_plan._format_for_unit("x", ib.FMT_MONEY) == ib.FMT_MULTIPLE
    assert source_plan._format_for_unit("USD", ib.FMT_MONEY) == ib.FMT_USD_MILLION
    assert source_plan._format_for_unit("USD K", ib.FMT_MONEY) == ib.FMT_USD_THOUSAND
    assert source_plan._format_for_unit("USD M", ib.FMT_MONEY) == ib.FMT_USD_MILLION


def test_skill_guidance_requires_reading_workbook_formatting_for_units() -> None:
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    design_text = (SKILL_DIR / "build" / "references" / "_ib_workbook_design_system.md").read_text(encoding="utf-8")
    review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    rubric_text = (SKILL_DIR / "build" / "references" / "_sheet_quality_rubric.md").read_text(encoding="utf-8")
    combined = "\n".join([invocation_text, design_text, review_text, rubric_text])

    for phrase in [
        "Store base-currency values and use Excel",
        "Do not infer units only from visible text",
        "Inspect units through formatting as well as values",
        "visible unit labels must match those formats",
        "This is a money-unit rule, not a blanket numeric rule",
        "units, customers, count, FTE, days, months, percentages, and multiples",
    ]:
        assert phrase in combined


def test_benchmark_guidance_covers_material_evidence_lenses() -> None:
    benchmark_text = (SKILL_DIR / "build" / "references" / "_benchmark_protocol.md").read_text(encoding="utf-8")
    invocation_text = (SKILL_DIR / "build" / "references" / "_skill_invocation_protocol.md").read_text(encoding="utf-8")
    review_text = (SKILL_DIR / "build" / "references" / "_self_review_protocol.md").read_text(encoding="utf-8")
    rubric_text = (SKILL_DIR / "build" / "references" / "_sheet_quality_rubric.md").read_text(encoding="utf-8")
    combined = "\n".join([benchmark_text, invocation_text, review_text, rubric_text])

    for phrase in [
        "Material Evidence Lenses",
        "Labor / HR comps",
        "Venture equity / funding comps",
        "Venture debt / non-dilutive capacity",
        "Pricing / customer ROI comps",
        "Market / competitive benchmarks",
        "The gate is not the sheet name",
    ]:
        assert phrase in combined


def test_marketplace_source_does_not_emit_unrelated_asset_heavy_template() -> None:
    source_text = """# Marketplace plan

The company is a marketplace startup. GMV is ¥10B, take rate is 12%, buyer and
seller cohorts are tracked separately, and the plan needs pricing, working
capital, funding need, ownership, scenario, sensitivity, valuation, and IC memo.
Source: management memo.
"""
    with tempfile.TemporaryDirectory() as tmp:
        source_md = Path(tmp) / "marketplace.md"
        out = Path(tmp) / "marketplace_plan.xlsx"
        source_md.write_text(source_text, encoding="utf-8")

        source_plan.build_source_plan_workbook(source_md, out)
        wb = load_workbook(out, data_only=False)
        all_text = "\n".join(
            str(cell.value)
            for ws in wb.worksheets
            for row in ws.iter_rows()
            for cell in row
            if cell.value is not None
        )

        assert wb["Kernel"]["D9"].value == "Marketplace / transaction"
        assert _unit_for_label(wb, "Assumptions", "Gross merchandise value") == "百万円"
        assert _unit_for_label(wb, "Assumptions", "Take rate") == "%"
        assert _first_year_cell_for_label(wb, "Revenue Build", "Transaction revenue").value == f"={FIRST_VALUE_LETTER}7*{FIRST_VALUE_LETTER}10"
        assert [term for term in ["fleet", "hardware", "field devices"] if term.lower() in all_text.lower()] == []


def test_hardware_source_ignores_low_usd_competitor_price_noise() -> None:
    source_text = """# Asset-heavy plan

The company is a hardware startup. The source includes competitor context:
consumer device monthly rental $499, but the company has not finalized its own
yen price. The plan should still use a local hardware default rather than
treating the competitor USD number as the company's price.
"""
    with tempfile.TemporaryDirectory() as tmp:
        source_md = Path(tmp) / "hardware.md"
        source_md.write_text(source_text, encoding="utf-8")
        facts = source_plan.extract_source_facts(source_md)

        assert facts.mechanics == "Hardware / asset-heavy"
        assert facts.monthly_price_yen[0] == 300_000


def test_source_plan_starting_cash_is_hard_input_blue() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        beginning_cash_row = _row_for_label(wb, "Assumptions", "Beginning cash")
        assert _font_rgb(wb["Assumptions"].cell(beginning_cash_row, FIRST_VALUE_COL)) == ib.IB_HARD_INPUT
        assert _font_rgb(wb["Assumptions"].cell(beginning_cash_row, SECOND_VALUE_COL)) == ib.IB_LINK_INTRA
    finally:
        tmp.cleanup()


def test_source_plan_ownership_waterfall_dilutes_prior_holders_symmetrically() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        ws = wb["Ownership"]
        f = FIRST_VALUE_LETTER
        g = SECOND_VALUE_LETTER
        h = source_plan.get_column_letter(FIRST_VALUE_COL + 2)
        i = source_plan.get_column_letter(FIRST_VALUE_COL + 3)
        for row in (7, 8, 9, 10, 13, 14):
            assert _font_rgb(ws.cell(row, FIRST_VALUE_COL)) == ib.IB_HARD_INPUT
        for row in (7, 8, 9, 10):
            assert _font_rgb(ws.cell(row, SECOND_VALUE_COL)) == ib.IB_FORMULA
        assert ws[f"{g}8"].value == f"={f}8*(1-{g}12-{g}13-{g}14)+{g}13"
        assert ws[f"{h}8"].value == f"={g}8*(1-{h}12-{h}13-{h}14)+{h}13"
        assert ws[f"{i}8"].value == f"={h}8*(1-{i}12-{i}13-{i}14)+{i}13"
        assert ws[f"{g}9"].value == f"={f}9*(1-{g}12-{g}13-{g}14)+{g}12"
        assert ws[f"{h}9"].value == f"={g}9*(1-{h}12-{h}13-{h}14)+{h}12"
        assert ws[f"{i}9"].value == f"={h}9*(1-{i}12-{i}13-{i}14)+{i}12"
        assert ws[f"{g}10"].value == f"={f}10*(1-{g}12-{g}13-{g}14)+{g}14"
        assert ws[f"{h}10"].value == f"={g}10*(1-{h}12-{h}13-{h}14)+{h}14"
        assert ws[f"{i}10"].value == f"={h}10*(1-{i}12-{i}13-{i}14)+{i}14"
    finally:
        tmp.cleanup()


def test_source_plan_bold_rows_preserve_ib_cell_colors() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        assert _font_rgb(_first_year_cell_for_label(wb, "Capital Stack", "Equity financing")) == ib.IB_HARD_INPUT
        assert _font_rgb(_first_year_cell_for_label(wb, "Capital Stack", "Ending cash")) == ib.IB_LINK_INTRA
        assert _font_rgb(_first_year_cell_for_label(wb, "Capital Stack", "Runway")) == ib.IB_LINK_INTRA
        assert _font_rgb(wb["Cost Build"].cell(16, FIRST_VALUE_COL)) == ib.IB_LINK_INTRA
        assert _font_rgb(wb["People Plan"].cell(11, FIRST_VALUE_COL)) == ib.IB_LINK_INTRA
    finally:
        tmp.cleanup()


def test_source_plan_uses_column_based_hierarchy_layout() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        ws = wb["Assumptions"]
        layout = source_plan.LAYOUT
        assert source_plan.START_PERIOD_COL == layout.unit_col + 1
        assert ws.column_dimensions["A"].width == ib.COL_MARGIN_WIDTH
        assert ws.column_dimensions["B"].width == layout.hierarchy_width
        assert ws.column_dimensions["C"].width == layout.label_width
        assert ws.column_dimensions["D"].width == layout.source_width
        assert ws.column_dimensions["E"].width == layout.unit_width
        assert ws.column_dimensions[FIRST_VALUE_LETTER].width == layout.period_width
        assert ws.freeze_panes is None
        assert [ws.cell(5, c).value for c in range(2, FIRST_VALUE_COL + 1)] == [
            None,
            "Line item",
            "Source / driver",
            "Unit",
            "FY2026",
        ]
        assert ws["B6"].value == "Volume and demand"
        assert ws["C6"].value is None
        assert ws["C7"].value == "New primary units"
        assert ws["B7"].value is None
        assert wb["Guide"]["B8"].value == "Source story signals"
        assert ws["E7"].value == "units"
        assert ws["F7"].value is not None
        assert ws["C7"].alignment.horizontal == "left"
        assert ws["D7"].alignment.horizontal == "left"
        assert ws["E7"].alignment.horizontal == "right"
        assert ws["F7"].alignment.horizontal == "right"
    finally:
        tmp.cleanup()


def test_source_plan_chart_axes_and_tabs_follow_currency_and_semantic_roles() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "usd.yaml"
        out = Path(tmp) / "usd.xlsx"
        input_path.write_text(
            "\n".join(
                [
                    "company: Generic USD Co",
                    "currency: USD",
                    "display_scale: thousand",
                    "grain: monthly",
                    "periods: 6",
                    "start_year: 2027",
                    "new_units: [10, 15, 20, 25, 30, 35]",
                    "monthly_price_yen: [20000, 20000, 21000, 21000, 22000, 22000]",
                    "equity_raise_yen: [1000000, 0, 0, 0, 0, 0]",
                ]
            ),
            encoding="utf-8",
        )
        build_model.build_model(input_path, out, mode="full")
        wb = load_workbook(out, data_only=False)

        axis_titles = [
            _chart_axis_title_text(chart)
            for ws in wb.worksheets
            for chart in getattr(ws, "_charts", [])
        ]
        assert "円" not in " ".join(axis_titles)
        assert "$K" in axis_titles
        assert "months" in axis_titles
        assert "$K / months" not in axis_titles
        assert "units" in axis_titles
        assert "units / $K" not in axis_titles
        assert ib.validate_sheet_naming(source_plan.SOURCE_PLAN_SHEETS) == []
        assert [name for name in source_plan.SOURCE_PLAN_SHEETS if name not in ib.SHEET_ROLE_MAPPING] == []
        assert _tab_rgb(wb["Market Support"]) == ib.BRAND_SLATE
        assert _tab_rgb(wb["Benchmarks"]) == ib.BRAND_WARNING
        assert _tab_rgb(wb["IC Memo"]) == ib.BRAND_ACCENT


def test_segment_lens_handles_long_generic_segment_names_without_clipping() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "long_segments.yaml"
        out = Path(tmp) / "long_segments.xlsx"
        input_path.write_text(
            "\n".join(
                [
                    "company: Generic Segment Co",
                    "segments:",
                    "  - Enterprise expansion segment with regulated deployment partners",
                    "  - Embedded platform segment with long-cycle integration partners",
                    "  - International distributor segment with multi-entity reporting",
                ]
            ),
            encoding="utf-8",
        )
        build_model.build_model(input_path, out, mode="full")
        wb = load_workbook(out, data_only=False)
        ws = wb["Segments"]
        segment_col = source_plan.get_column_letter(source_plan.LAYOUT.label_col)
        width = ws.column_dimensions[segment_col].width or 0
        clipped = [
            f"{cell.coordinate}: width={width} value={cell.value}"
            for cell in ws[segment_col]
            if isinstance(cell.value, str)
            and cell.row >= 6
            and len(cell.value) > width * 1.15
        ]

        assert clipped == []


def test_source_plan_tables_do_not_overlap_metadata_columns() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        assert [wb["Scenarios"].cell(7, c).value for c in range(FIRST_VALUE_COL, FIRST_VALUE_COL + 3)] == [0.70, 1.00, 1.30]
        assert wb["Scenarios"].cell(7, source_plan.LAYOUT.label_col).value == "New logo / conversion scale"
        assert wb["Scenarios"].cell(7, source_plan.LAYOUT.unit_col).value == "x"
        assert wb["Financing"].cell(16, FIRST_VALUE_COL).value == f"='Scenarios'!{FIRST_VALUE_LETTER}19"
        assert [wb["Sensitivity"].cell(7, c).value for c in range(FIRST_VALUE_COL, FIRST_VALUE_COL + 5)] == [0.60, 0.80, 1.00, 1.20, 1.40]
        assert wb["Sensitivity"].cell(8, FIRST_VALUE_COL - 1).value == 0.80
        assert wb["Sensitivity"].cell(8, FIRST_VALUE_COL).value == f"=('Revenue Build'!J18*{FIRST_VALUE_LETTER}$7*$E8)-('Cost Build'!J12*1)-('P&L'!J17*1)"
    finally:
        tmp.cleanup()


def test_source_plan_design_surface_uses_generic_blue_palette() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        allowed = {ib.BG_CANVAS, ib.BG_TABLE_HEADER, ib.BG_TOTAL_BAND, ib.BG_HEADER_BAND, ib.BG_WORKING}
        observed = {
            _fill_rgb(cell)
            for ws in wb.worksheets
            for row in ws.iter_rows()
            for cell in row
            if _fill_rgb(cell) is not None
        }
        assert observed <= allowed
        assert ib.BG_TABLE_HEADER in observed
        assert _styled_blank_cells(wb) == []
        assert _repeated_semantic_fill_rows(wb) == []
        assert _repeated_prominent_border_rows(wb) == []
        assert _hierarchy_spacer_border_violations(wb) == []
        assert _font_design_violations(wb) == []
        assert _semantic_alignment_violations(wb) == []
        total_populated = sum(
            1
            for ws in wb.worksheets
            for row in ws.iter_rows()
            for cell in row
            if cell.value is not None
        )
        highlighted = sum(
            1
            for ws in wb.worksheets
            for row in ws.iter_rows()
            for cell in row
            if cell.value is not None and _fill_rgb(cell) == ib.BG_WORKING
        )
        assert highlighted / total_populated < 0.08
    finally:
        tmp.cleanup()


def test_source_plan_has_no_excel_indent_or_clipped_role_columns() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        indent_violations = []
        clipped = []
        role_cols = (source_plan.LAYOUT.label_col, source_plan.LAYOUT.source_col)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if getattr(cell.alignment, "indent", 0):
                        indent_violations.append(f"{ws.title}!{cell.coordinate}")
            for col in role_cols:
                width = ws.column_dimensions[source_plan.get_column_letter(col)].width or 0
                for row_idx in range(5, ws.max_row + 1):
                    cell = ws.cell(row_idx, col)
                    if not isinstance(cell.value, str):
                        continue
                    if cell.value.startswith("="):
                        continue
                    if ws.cell(row_idx, col + 1).value is None:
                        continue
                    if len(cell.value) > width * 1.15:
                        clipped.append(f"{ws.title}!{cell.coordinate}: width={width} value={cell.value}")
        assert indent_violations == []
        assert clipped == []
    finally:
        tmp.cleanup()


def test_source_plan_has_no_long_centered_prose_headers() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        centered = []
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if (
                        isinstance(cell.value, str)
                        and len(cell.value) > 18
                        and cell.alignment.horizontal == "center"
                    ):
                        centered.append(f"{ws.title}!{cell.coordinate}: {cell.value}")
        assert centered == []
    finally:
        tmp.cleanup()


def test_source_plan_ib_design_rhythm_and_visibility() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        kernel = wb["Kernel"]
        assert kernel["B7"].value is None
        assert kernel["C7"].value == "Decision"
        assert kernel["D7"].value
        assert _column_width(kernel, "B") == ib.COL_HIERARCHY_WIDTH
        assert _column_width(kernel, "C") >= 32
        assert _column_width(kernel, "D") >= 92
        for ws in wb.worksheets:
            assert ws.sheet_view.showGridLines is False
            assert ws.sheet_view.zoomScale == 90
            assert ws.page_setup.orientation == "landscape"
            assert ws.page_setup.fitToWidth == 1
            assert ws.print_title_rows in {"1:5", "$1:$5"}
            expected_title_cols = f"A:{source_plan.get_column_letter(source_plan.LAYOUT.unit_col)}"
            expected_title_cols_abs = f"$A:${source_plan.get_column_letter(source_plan.LAYOUT.unit_col)}"
            assert ws.print_title_cols in {expected_title_cols, expected_title_cols_abs}
            assert _column_width(ws, "A") == ib.COL_MARGIN_WIDTH
            for col in range(source_plan.LAYOUT.first_hierarchy_col, source_plan.LAYOUT.label_col):
                if ws.max_column >= col:
                    assert _column_width(ws, source_plan.get_column_letter(col)) >= ib.COL_HIERARCHY_WIDTH
            if ws.max_column >= source_plan.LAYOUT.label_col:
                assert _column_width(ws, source_plan.get_column_letter(source_plan.LAYOUT.label_col)) >= ib.COL_LABEL_WIDTH
            if ws.max_column >= source_plan.LAYOUT.source_col:
                assert _column_width(ws, source_plan.get_column_letter(source_plan.LAYOUT.source_col)) >= ib.COL_SOURCE_WIDTH
            if ws.max_column >= source_plan.LAYOUT.unit_col:
                assert _column_width(ws, source_plan.get_column_letter(source_plan.LAYOUT.unit_col)) >= ib.COL_UNIT_WIDTH
            assert (ws.row_dimensions[2].height or 0) <= 20
            assert (ws.row_dimensions[5].height or 0) <= 18
            assert ws.freeze_panes is None
        assert _column_width(wb["Assumptions"], "C") >= 54
        assert _column_width(wb["Assumptions"], "D") >= 54
    finally:
        tmp.cleanup()


def _print_area_bounds(ws) -> tuple[int, int, int, int]:
    area = str(ws.print_area).replace("'", "").replace("$", "")
    if "!" in area:
        area = area.split("!", 1)[1]
    return range_boundaries(area)


def test_all_generated_modes_pass_visual_design_invariants() -> None:
    for mode in build_model.VALID_MODES:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / f"{mode}.xlsx"
            build_model.build_model(None, out, mode=mode)
            wb = load_workbook(out, data_only=False)

            assert _defined_name_count(wb) == 0
            assert _merged_count(wb) == 0
            assert _wrapped_cells(wb) == []
            assert _manual_line_break_violations(wb) == []
            assert _leading_space_labels(wb) == []
            assert _styled_blank_cells(wb) == []
            assert _design_band_span_violations(wb) == []
            assert _repeated_semantic_fill_rows(wb) == []
            assert _unknown_fill_color_violations(wb) == []
            assert _repeated_prominent_border_rows(wb) == []
            assert _hierarchy_spacer_border_violations(wb) == []
            assert _font_design_violations(wb) == []
            assert _semantic_alignment_violations(wb) == []
            assert _border_density_violations(wb) == []
            assert _memo_note_border_violations(wb) == []
            assert _border_style_violations(wb) == []
            assert _border_color_violations(wb) == []
            assert _money_unit_format_mismatches(wb) == []
            assert _semantic_unit_format_mismatches(wb) == []
            assert _row_height_violations(wb) == []
            for ws in wb.worksheets:
                assert ws.freeze_panes is None
                assert ws.sheet_view.showGridLines is False
                assert ws.print_area
                rendered_row, rendered_col = ib.rendered_bounds(ws)
                min_col, min_row, max_col, max_row = _print_area_bounds(ws)
                assert (min_row, min_col) == (1, 1)
                assert max_row >= rendered_row
                assert max_col >= rendered_col


def test_source_plan_print_canvas_includes_rendered_used_range() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        assert _styled_blank_cells(wb) == []
        for ws in wb.worksheets:
            rendered_row, rendered_col = ib.rendered_bounds(ws)
            min_col, min_row, max_col, max_row = _print_area_bounds(ws)
            assert (min_row, min_col) == (1, 1)
            assert max_row >= rendered_row
            assert max_col >= rendered_col
            assert ws.max_row <= rendered_row
            assert ws.max_column <= rendered_col
            stray_dimensions = [
                key
                for key in ws.column_dimensions
                if range_boundaries(f"{key}1:{key}1")[0] > rendered_col
            ]
            assert stray_dimensions == []

        for ws in wb.worksheets:
            ws.insert_rows(ws.max_row + 1)
            assert ws.cell(ws.max_row, 1).style_id == 0
    finally:
        tmp.cleanup()


def test_representative_workbook_pdf_render_smoke_when_available() -> None:
    soffice = shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        return
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source_md = tmp_path / "render_source.md"
        out = tmp_path / "render_source.xlsx"
        source_md.write_text(
            "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo.",
            encoding="utf-8",
        )
        source_plan.build_source_plan_workbook(source_md, out)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(out)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        pdf = tmp_path / "render_source.pdf"
        assert pdf.exists()
        assert pdf.stat().st_size > 50_000
        subprocess.run(
            [pdftoppm, "-png", "-r", "80", "-f", "1", "-l", "2", str(pdf), str(tmp_path / "page")],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        pages = sorted(tmp_path.glob("page-*.png"))
        assert len(pages) >= 2
        assert all(page.stat().st_size > 10_000 for page in pages)


def test_representative_workbook_recalculates_without_formula_errors_when_available() -> None:
    soffice = shutil.which("soffice")
    if not soffice:
        return
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out = tmp_path / "formula_check.xlsx"
        recalc_dir = tmp_path / "recalc"
        recalc_dir.mkdir()
        build_model.build_model(None, out, mode="full")
        subprocess.run(
            [soffice, "--headless", "--convert-to", "xlsx", "--outdir", str(recalc_dir), str(out)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        recalculated = recalc_dir / out.name
        assert recalculated.exists()
        wb = load_workbook(recalculated, data_only=True)
        assert _formula_error_cells(wb) == []


def test_source_plan_custom_tables_keep_text_columns_readable() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA recurring software startup with ARR and subscription pricing. Source: management memo."
    )
    try:
        clipped = []
        for sheet_name in ["KPI", "Scenarios", "Sensitivity", "Valuation", "Benchmarks", "IC Memo"]:
            ws = wb[sheet_name]
            for row in ws.iter_rows():
                for cell in row:
                    if not isinstance(cell.value, str) or cell.value.startswith("="):
                        continue
                    width = ws.column_dimensions[source_plan.get_column_letter(cell.column)].width or 0
                    if ws.cell(cell.row, cell.column + 1).value is not None and len(cell.value) > width * 1.15:
                        clipped.append(f"{ws.title}!{cell.coordinate}: width={width} value={cell.value}")
        assert clipped == []
    finally:
        tmp.cleanup()


def test_excluded_sheets_cannot_create_broken_references() -> None:
    for excluded in (["Valuation"], ["Assumptions"], ["CF"]):
        try:
            build_model.resolve_bundle("full", excluded_sheets=excluded)
        except ValueError as exc:
            assert "broken workbook references" in str(exc)
        else:
            raise AssertionError(f"excluded_sheets accepted unsafe bundle: {excluded}")


def test_ib_helpers_do_not_use_native_indent_for_hierarchy() -> None:
    wb = Workbook()
    ws = wb.active
    ib.apply_label(ws["B2"])
    ib.write_hierarchical_line_item(ws, 3, 2, "Child line")

    assert ws["B2"].alignment.indent == 0
    assert ws["D3"].alignment.indent == 0


def test_ib_helpers_encode_role_based_alignment_tokens() -> None:
    wb = Workbook()
    ws = wb.active

    ib.apply_label(ws["B2"])
    ib.apply_comment(ws["C2"])
    ib.apply_unit_label(ws["D2"])
    ib.apply_year_header(ws["E2"], "FY2027")
    ib.apply_hard_input(ws["F2"])

    assert ib.ALIGN_LABEL == "left"
    assert ib.ALIGN_SOURCE_NOTE == "left"
    assert ib.ALIGN_UNIT == "right"
    assert ib.ALIGN_VALUE == "right"
    assert ib.ALIGN_PERIOD_HEADER == "center"
    assert "labels, sources, notes, titles, memos, and interpretation text are left-aligned" in ib.ALIGNMENT_BEST_PRACTICE
    assert ws["B2"].alignment.horizontal == ib.ALIGN_LABEL
    assert ws["C2"].alignment.horizontal == ib.ALIGN_SOURCE_NOTE
    assert ws["D2"].alignment.horizontal == ib.ALIGN_UNIT
    assert ws["E2"].alignment.horizontal == ib.ALIGN_PERIOD_HEADER
    assert ws["F2"].alignment.horizontal == ib.ALIGN_VALUE


def test_ib_helpers_encode_role_based_font_size_tokens() -> None:
    wb = Workbook()
    ws = wb.active

    ib.apply_label(ws["B2"])
    ib.apply_comment(ws["C2"])
    ib.apply_unit_label(ws["D2"])
    ib.apply_year_header(ws["E2"], "FY2027")
    ib.apply_section_header(ws["B4"], "Section")
    ib.write_cover(ws, title="Cover", subtitle="Subtitle", confidential=True)

    assert ib.FONT_SIZE_ALLOWED_CELLS == (
        ib.FONT_SIZE_SMALL,
        ib.FONT_SIZE_BASE,
        ib.FONT_SIZE_LARGE,
        ib.FONT_SIZE_TITLE,
    )
    assert ib.FONT_SIZE_TINY not in ib.FONT_SIZE_ALLOWED_CELLS
    assert ib.FONT_SECTION == ib.FONT_SECTION_HEADER
    assert ib.FONT_COMMENT.color.rgb[-6:] == ib.IB_COMMENT
    assert ib.IB_COMMENT == "666666"
    assert "constrained font-size palette" in ib.FONT_SIZE_BEST_PRACTICE
    assert float(ws["B2"].font.sz) == float(ib.FONT_SIZE_BASE)
    assert float(ws["C2"].font.sz) == float(ib.FONT_SIZE_SMALL)
    assert float(ws["D2"].font.sz) == float(ib.FONT_SIZE_SMALL)
    assert float(ws["E2"].font.sz) == float(ib.FONT_SIZE_BASE)
    assert float(ws["B4"].font.sz) == float(ib.FONT_SIZE_LARGE)
    assert float(ws["B6"].font.sz) == float(ib.FONT_SIZE_TITLE)
    assert float(ws["B8"].font.sz) == float(ib.FONT_SIZE_TITLE)
    assert float(ws["F2"].font.sz) == float(ib.FONT_SIZE_SMALL)


def test_font_design_audit_rejects_tiny_fractional_and_presentation_sizes() -> None:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Tiny"
    ws["A1"].font = Font(name=ib.FONT_FAMILY, size=8)
    ws["A2"] = "Fractional"
    ws["A2"].font = Font(name=ib.FONT_FAMILY, size=10.5)
    ws["A3"] = "Presentation"
    ws["A3"].font = Font(name=ib.FONT_FAMILY, size=16)
    ws["A4"] = "Wrong family"
    ws["A4"].font = Font(name="Times New Roman", size=10)
    ib.set_workbook_default_font(wb)

    violations = _font_design_violations(wb)
    assert any("A1" in item and "size=8" in item for item in violations)
    assert any("A1" in item and "tiny cell font=8" in item for item in violations)
    assert any("A2" in item and "size=10.5" in item for item in violations)
    assert any("A3" in item and "size=16" in item for item in violations)
    assert any("A4" in item and "font=Times New Roman" in item for item in violations)


def test_added_hierarchy_columns_use_google_sheets_20px_width() -> None:
    wb = Workbook()
    ws = wb.active
    original_layout = source_plan.LAYOUT
    try:
        source_plan.LAYOUT = source_plan.LayoutSpec(hierarchy_cols=3)
        facts = kernel.derive_source_facts("# PLAN\nSource: management memo.")
        ws._startup_facts = facts
        source_plan._setup_sheet(ws, "Hierarchy width check")
        source_plan._write_period_header(ws, facts)

        assert ws.column_dimensions["B"].width == ib.COL_HIERARCHY_WIDTH
        assert ws.column_dimensions["C"].width == ib.COL_HIERARCHY_WIDTH
        assert ws.column_dimensions["D"].width == ib.COL_HIERARCHY_WIDTH
        assert ib.COL_HIERARCHY_WIDTH == 2.14
        assert ws.column_dimensions["E"].width == ib.COL_LABEL_WIDTH
        assert ws.column_dimensions["F"].width == ib.COL_SOURCE_WIDTH
        assert ws.column_dimensions["G"].width == ib.COL_UNIT_WIDTH
        assert ws.cell(5, source_plan.LAYOUT.label_col).value == "Line item"
        assert ws.cell(5, source_plan.LAYOUT.source_col).value == "Source / driver"
        assert ws.cell(5, source_plan.LAYOUT.unit_col).value == "Unit"
        assert ws.cell(5, source_plan.LAYOUT.first_value_col).value == facts.period_labels[0]
        assert source_plan._uses_default_layout(ws) is True
        assert ws.freeze_panes is None
    finally:
        source_plan.LAYOUT = original_layout


def test_generic_kernel_does_not_promote_domain_specific_mentions_to_sources() -> None:
    facts = kernel.derive_source_facts(
        "# Marketplace\nThe plan mentions a public company only as a comparison. Source: management memo."
    )

    assert facts.source_names == ["management memo"]


def test_benchmark_register_uses_evidence_status_not_fake_source_placeholders() -> None:
    tmp, wb = _sample_source_workbook(
        "# PLAN\nA generic startup plan. Source: management memo."
    )
    try:
        text = "\n".join(str(cell.value) for row in wb["Benchmarks"].iter_rows() for cell in row if cell.value is not None)
        forbidden = ["provided source / owner", "external benchmark TBD", "TBD"]
        assert [term for term in forbidden if term in text] == []
        assert "management memo" in text
        assert "unresolved evidence" in text
    finally:
        tmp.cleanup()


def test_scenario_formulas_are_not_built_with_fragile_substring_replacement() -> None:
    builder_text = (SCRIPTS_DIR / "source_plan_builder.py").read_text(encoding="utf-8")

    assert ".replace(\"C14\"" not in builder_text
    assert ".replace(\"C15\"" not in builder_text
    assert ".replace(\"C16\"" not in builder_text


def test_build_model_routes_source_markdown_to_source_plan() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        source_md = Path(tmp) / "story.md"
        out = Path(tmp) / "routed.xlsx"
        source_md.write_text(
            "Asset-heavy deployment company with 月額32万円 pricing and 25,000 operating units at maturity.",
            encoding="utf-8",
        )

        build_model.build_model(None, out, source_md=source_md)
        wb = load_workbook(out, data_only=False)

        assert wb.sheetnames == source_plan.SOURCE_PLAN_SHEETS
        assert _chart_count(wb) >= 4


if __name__ == "__main__":
    test_skill_exposes_clean_build_route_only()
    test_skill_uses_generic_economic_kernel_not_stage_matrix()
    test_prompt_guidance_resists_fixed_template_routing()
    test_sheet_quality_rubric_covers_every_generated_sheet()
    test_economic_kernel_is_separate_from_workbook_renderer()
    test_japanese_money_units_parse_at_correct_scale()
    test_seed_to_pre_ipo_horizon_is_not_truncated_to_two_years()
    test_generated_workbook_contains_interpretive_analysis_surfaces()
    test_mechanic_specific_kpi_and_scenario_axes_are_rendered()
    test_ambiguous_mechanics_use_generic_kpis_and_scenario_axes()
    test_cost_labeled_scenario_drivers_pressure_costs_not_revenue()
    test_unclassified_scenario_drivers_default_to_opex_not_revenue()
    test_financing_driver_downside_widens_funding_gap()
    test_cost_build_does_not_double_count_detailed_service_costs_in_variable_cogs()
    test_orchestrator_routes_through_generic_source_plan_builder()
    test_focused_modes_use_generic_kernel_after_bundle_filter()
    test_focused_modes_are_formula_complete_without_compact_placeholders()
    test_integrated_model_has_ib_decision_gates_not_just_readouts()
    test_comparable_evidence_loads_public_peers_by_default_and_overrides_multiples()
    test_default_live_comps_match_mechanic_labels_and_cli_overrides_yaml()
    test_private_and_transaction_comps_are_included_in_comparable_evidence()
    test_incomplete_provided_comps_are_registered_but_not_used_for_medians()
    test_sec_ticker_lookup_is_cached_and_errors_are_compact()
    test_failed_live_comps_do_not_pollute_company_specific_sources_or_mark_live_multiples()
    test_full_model_uses_direct_formula_refs()
    test_intra_sheet_formula_cells_are_black()
    test_ic_memo_dependency_closure_matches_live_formula_readouts()
    test_cash_flow_runway_formula_floors_negative_cash_at_zero()
    test_cross_sheet_formula_cells_are_green()
    test_pricing_bundle_is_formula_complete()
    test_cap_table_mode_uses_state_machine_not_full_workbook()
    test_all_modes_produce_expected_bundles()
    test_generated_modes_do_not_reference_removed_sheets()
    test_structured_yaml_controls_grain_periods_and_drivers()
    test_balance_sheet_has_opening_capital_counterpart()
    test_mfn_applied_only_for_changed_safe_terms()
    test_cap_table_rebuild_clears_prior_sheet_fills()
    test_cap_table_rebuild_clears_legacy_layout_state()
    test_cap_table_sheet_uses_canonical_design_surface()
    test_ib_helpers_reject_wrap_text_true()
    test_runtime_builders_do_not_use_wrap_or_merge_layout_shortcuts()
    test_skill_guidance_makes_no_wrap_rule_explicit()
    test_skill_guidance_requires_fix_and_rerun_iteration()
    test_skill_guidance_uses_meaningful_sparse_fills_and_borders()
    test_skill_guidance_enforces_ib_text_positioning()
    test_skill_guidance_enforces_ib_font_size_discipline()
    test_xlsx_evals_load_full_design_reference_stack()
    test_semantic_fill_helper_uses_rectangular_span_including_blanks()
    test_source_backed_plan_reaches_generic_kernel_shape()
    test_generated_workbook_has_sheet_specific_quality_markers()
    test_structured_yaml_currency_and_display_scale_are_generic()
    test_money_units_are_raw_values_with_number_formats_not_scaled_values()
    test_non_money_units_keep_their_own_formats_and_formulas()
    test_skill_guidance_requires_reading_workbook_formatting_for_units()
    test_benchmark_guidance_covers_material_evidence_lenses()
    test_marketplace_source_does_not_emit_unrelated_asset_heavy_template()
    test_hardware_source_ignores_low_usd_competitor_price_noise()
    test_source_plan_starting_cash_is_hard_input_blue()
    test_source_plan_ownership_waterfall_dilutes_prior_holders_symmetrically()
    test_source_plan_bold_rows_preserve_ib_cell_colors()
    test_source_plan_uses_column_based_hierarchy_layout()
    test_source_plan_chart_axes_and_tabs_follow_currency_and_semantic_roles()
    test_segment_lens_handles_long_generic_segment_names_without_clipping()
    test_source_plan_tables_do_not_overlap_metadata_columns()
    test_source_plan_design_surface_uses_generic_blue_palette()
    test_source_plan_has_no_excel_indent_or_clipped_role_columns()
    test_source_plan_has_no_long_centered_prose_headers()
    test_source_plan_ib_design_rhythm_and_visibility()
    test_all_generated_modes_pass_visual_design_invariants()
    test_source_plan_print_canvas_includes_rendered_used_range()
    test_representative_workbook_pdf_render_smoke_when_available()
    test_representative_workbook_recalculates_without_formula_errors_when_available()
    test_source_plan_custom_tables_keep_text_columns_readable()
    test_excluded_sheets_cannot_create_broken_references()
    test_ib_helpers_do_not_use_native_indent_for_hierarchy()
    test_ib_helpers_encode_role_based_alignment_tokens()
    test_ib_helpers_encode_role_based_font_size_tokens()
    test_font_design_audit_rejects_tiny_fractional_and_presentation_sizes()
    test_added_hierarchy_columns_use_google_sheets_20px_width()
    test_generic_kernel_does_not_promote_domain_specific_mentions_to_sources()
    test_benchmark_register_uses_evidence_status_not_fake_source_placeholders()
    test_scenario_formulas_are_not_built_with_fragile_substring_replacement()
    test_build_model_routes_source_markdown_to_source_plan()
