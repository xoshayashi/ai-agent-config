"""Build startup-financial-modeling xlsx outputs.

Primary route:
    python build_model.py --source-md equity_story.md --output plan.xlsx

That route generates a generic economic-kernel startup plan. The mode path is a
focused-module convenience for narrow requests such as pricing, cap table,
runway, valuation, market sizing, or three-statement mechanics. Focused modes
start from the same kernel but keep an explicit visible-surface contract.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml  # type: ignore
except ImportError:
    _yaml = None  # YAML loader is optional; defaults work without it.

import ib_format as ibf  # noqa: E402
import source_plan_builder as spb  # noqa: E402
import cap_table_builder as ctb  # noqa: E402
import economic_kernel as ek  # noqa: E402
import live_comps as lc  # noqa: E402

# ============================================================================
# Mode -> seed sheet bundle for focused module outputs.
# ============================================================================

# S3-2: every route builds the v2 12-sheet architecture. Mode bundles are
# CLOSED lists (BLUEPRINT_S3 MODE_BUNDLE_SEEDS(新)) — no transitive dependency
# expansion. Builders are bundle-aware: a sheet whose engine dependency is
# outside the bundle computes a compact in-sheet block instead of referencing
# a missing sheet. The --source-md narrative route uses the same v2 full
# bundle (annual grain by default).
MODE_BUNDLE_SEEDS: dict[str, list[str]] = {
    "full": list(spb.SOURCE_PLAN_SHEETS_V2),
    "pricing": ["Guide", "Assumptions", "Pricing", "Summary"],
    "unit_economics": ["Guide", "Assumptions", "Unit Economics", "Summary"],
    "burn_runway": ["Guide", "Assumptions", "CF", "Financing", "Summary"],
    "cap_table": list(spb.CAP_TABLE_MODE_SHEETS),
    "three_statement": ["Guide", "Assumptions", "P&L", "BS", "CF", "Summary"],
    "ma_exit": ["Guide", "Assumptions", "Valuation & Exit", "Evidence", "IC Memo"],
    "dcf_only": ["Guide", "Assumptions", "Valuation & Exit", "Evidence"],
    "market_sizing": ["Guide", "Evidence"],
    "comps_only": ["Guide", "Evidence", "Valuation & Exit", "IC Memo"],
}

# HARD build dependencies only (a builder unconditionally references the
# target sheet). Weak dependencies (engine sheets, Summary roll-ups) resolve
# inside the builders and are deliberately NOT listed — that is what removed
# the transitive bundle explosion. Used for excluded_sheets validation and
# for --additional-sheets closure.
SHEET_DEPENDENCIES: dict[str, list[str]] = {
    "Guide": [],
    "Summary": [],
    "Assumptions": [],
    "Revenue Build": ["Assumptions"],
    "Cost Build": ["Assumptions", "Revenue Build"],
    "People Plan": ["Assumptions", "Revenue Build"],
    "P&L": ["Assumptions"],
    "BS": ["Assumptions", "P&L", "CF"],
    "CF": ["Assumptions"],
    "Financing": ["Assumptions", "CF"],
    "Cap Table": ["Assumptions"],
    "Evidence": [],
    "Valuation & Exit": [],
    "IC Memo": ["Valuation & Exit"],
    "Pricing": ["Assumptions"],
    "Unit Economics": ["Assumptions"],
    "Segments": [],
    "Kernel": [],
    "Ownership": [],
}

VALID_MODES: list[str] = list(MODE_BUNDLE_SEEDS.keys())
VALID_SHEETS: set[str] = (
    set(spb.SOURCE_PLAN_SHEETS_V2)
    | set(spb.CONDITIONAL_SHEETS_V2)
    | set(spb.CAP_TABLE_MODE_SHEETS)
)
_CANONICAL_SHEET_ORDER: list[str] = list(dict.fromkeys([
    *spb.SOURCE_PLAN_SHEETS_V2,
    *spb.CONDITIONAL_SHEETS_V2,
    *spb.CAP_TABLE_MODE_SHEETS,
]))
DEFAULT_PUBLIC_COMP_TICKERS: dict[str, list[str]] = {
    "Recurring software": ["CRM", "NOW", "DDOG"],
    "Marketplace / transaction": ["UBER", "DASH", "ETSY"],
    "Hardware / asset-heavy": ["ISRG", "ROK", "TSLA"],
    "Fintech / balance-sheet": ["PYPL", "SOFI", "AFRM"],
    # Public-market data is only a fallback for pre-revenue companies; users
    # should add private milestone, funding-round, or transaction evidence.
    "Pre-revenue / milestone": ["ISRG", "ROK", "TSLA"],
    "Generic startup": ["CRM", "NOW", "DDOG"],
}


def _validate_sheet_names(sheet_names: list[str], *, arg_name: str) -> None:
    unknown = [sheet for sheet in sheet_names if sheet not in VALID_SHEETS]
    if unknown:
        raise ValueError(
            f"Unknown sheet name(s) in {arg_name}: {unknown}. "
            f"Valid: {sorted(VALID_SHEETS)}"
        )


def _missing_dependencies(bundle: list[str]) -> list[str]:
    selected = set(bundle)
    missing: list[str] = []
    for sheet in bundle:
        for dependency in SHEET_DEPENDENCIES.get(sheet, []):
            if dependency not in selected:
                missing.append(f"{sheet} requires {dependency}")
    return missing


def resolve_bundle(
    mode: str,
    additional_sheets: list[str] | None = None,
    excluded_sheets: list[str] | None = None,
    *,
    source_route: bool = False,
    facts: Any | None = None,
) -> list[str]:
    """Return the exact sheet bundle generated for a mode plus overrides.

    Mode seeds are closed bundles (no transitive expansion). Only
    --additional-sheets pull their hard dependencies in. When `facts` is
    given, the full bundle drops BS if its balance-sheet drivers are
    immaterial (BLUEPRINT_S3 条件付き). `source_route` is accepted for CLI
    symmetry — the narrative route builds the same v2 bundle."""
    if mode not in MODE_BUNDLE_SEEDS:
        raise ValueError(f"Unknown mode {mode!r}. Valid: {VALID_MODES}")
    if additional_sheets:
        _validate_sheet_names(additional_sheets, arg_name="additional_sheets")
    if excluded_sheets:
        _validate_sheet_names(excluded_sheets, arg_name="excluded_sheets")

    bundle: list[str] = list(MODE_BUNDLE_SEEDS[mode])
    if mode == "full" and facts is not None:
        bundle = spb.full_bundle_for_facts(facts, bundle)
    if additional_sheets:
        pending = [s for s in additional_sheets if s not in bundle]
        while pending:
            sheet = pending.pop(0)
            if sheet in bundle:
                continue
            bundle.append(sheet)
            pending.extend(SHEET_DEPENDENCIES.get(sheet, []))
    if excluded_sheets:
        bundle = [s for s in bundle if s not in excluded_sheets]
        missing = _missing_dependencies(bundle)
        if missing:
            raise ValueError(
                "excluded_sheets would create broken workbook references. "
                "Also exclude dependent sheets or choose a focused mode. "
                f"Missing dependencies: {missing}"
            )
    canonical_order = {sheet: idx for idx, sheet in enumerate(_CANONICAL_SHEET_ORDER)}
    return sorted(bundle, key=lambda sheet: canonical_order.get(sheet, len(canonical_order)))


# ============================================================================
# Input loading
# ============================================================================


def load_yaml(path: Path) -> dict[str, Any]:
    """Load optional YAML input for focused module outputs."""
    if _yaml is None:
        raise RuntimeError(
            "PyYAML not installed. Run: pip install pyyaml "
            "(or omit --input to use generic economic-kernel defaults)."
        )
    with path.open(encoding="utf-8") as f:
        data = _yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping, got {type(data).__name__}")
    return data


def _clear_defined_names(wb: Any) -> None:
    """Remove workbook and sheet-scoped names from generated models."""
    wb.defined_names.clear()
    for ws in wb.worksheets:
        ws.defined_names.clear()


_SHEET_REF_RE = re.compile(r"'([^']+)'!")


# v2 sheet-quality markers (BLUEPRINT_S3 マーカー): every generated sheet must
# carry these labels or the strict audit fails. Kernel / Ownership belong to
# the cap_table state-machine bundle (Ownership is pure data — no markers).
REQUIRED_SHEET_MARKERS: dict[str, list[str]] = {
    "Guide": ["Formatting key", "Model qualifications"],
    "Summary": ["Master check", "Scenario comparison", "Cross-check", "KPI"],
    "Assumptions": ["Scenario toggle", "Driver map", "Evidence status"],
    "Revenue Build": ["Total revenue", "Demand support", "Price support"],
    "Cost Build": ["Total COGS", "Gross profit", "Cost-to-serve"],
    "People Plan": ["Total headcount", "People cost", "Capacity"],
    "P&L": ["Total revenue", "EBITDA", "Net income"],
    "BS": ["Total assets", "Balance check"],
    "CF": ["Ending cash", "Runway months", "Cash shortfall check"],
    "Financing": ["Sources", "Uses", "Runway after raise", "Downside funding gap"],
    "Cap Table": ["Pre-money", "Post-money", "Fully diluted shares", "Ownership check"],
    "Evidence": ["Comparable evidence", "Benchmark register", "Market sanity"],
    "Valuation & Exit": ["Method matrix", "Selected EV range", "Investor return", "Exit waterfall"],
    "IC Memo": ["Recommendation", "Ranked DD gates", "Walk-away conditions"],
    "Pricing": ["Selected price", "Pricing validation plan"],
    "Unit Economics": ["Unit economics", "LTV / CAC", "CAC payback"],
    "Segments": ["Segment register", "Consolidation bridge check"],
    "Kernel": ["Decision", "Model grain", "Mechanics", "Unknowns"],
    # Ownership is the cap_table state-machine sheet — pure data, no prose markers.
    "Ownership": [],
}


def _missing_sheet_markers(title: str, sheet_values: set[str]) -> list[str]:
    markers = REQUIRED_SHEET_MARKERS.get(title, [])
    return [marker for marker in markers if marker not in sheet_values]


def _v2_period_anchor_col(ws: Any) -> int | None:
    """First v2 period column (freeze anchor). Delegates to the canonical
    detector in ib_format so the shipped audit and the ib_format helper/tests
    share ONE definition of a period column (row-5 months ruler + row-6
    header). Legacy sheets carry string row-5 values and stay exempt."""
    return ibf.period_axis_anchor_col(ws)


def _defined_name_count(wb: Any) -> int:
    count = len(wb.defined_names)
    for ws in wb.worksheets:
        count += len(ws.defined_names)
    return count


# ============================================================================
# S5 promoted audits (BLUEPRINT_S3 監査 1/2/3/5/6 — ported from the
# quality_gates.py scoring harness into the shipping strict-audit gate).
# ============================================================================

# R18 hardcoded-constant whitelist: structural constants only. Everything
# else must come from an Assumptions (or register) cell reference.
NUMERIC_FORMULA_WHITELIST = {"0", "1", "-1", "2", "3", "12", "24", "100", "365", "1000"}


def _v2_period_cols(ws: Any) -> list[int]:
    """Period columns per the canonical ib_format detector (row-5 months ruler
    under a row-6 period header). Single source of truth shared with the
    ib_format audit/tests so the two cannot drift."""
    return ibf.period_axis_columns(ws)


def _audit_period_column_widths(wb: Any) -> list[str]:
    """監査1: every period column on every period-axis sheet carries the one
    canonical width (COL_PERIOD_WIDTH_V2 = 11.5)."""
    from openpyxl.utils import get_column_letter

    expected = float(ibf.COL_PERIOD_WIDTH_V2)
    issues: list[str] = []
    for ws in wb.worksheets:
        for col in _v2_period_cols(ws):
            letter = get_column_letter(col)
            dim = ws.column_dimensions.get(letter)
            width = dim.width if dim is not None else None
            if width is None or round(float(width), 2) != expected:
                issues.append(
                    f"{ws.title}!{letter} period column width {width} != {expected}"
                )
    return issues


# Unit label -> acceptable number formats (監査2). Money labels must match
# the canonical scale format EXACTLY (a mismatched comma scale misstates the
# numbers); unscaled counts accept integer / 1-decimal display variants.
def _unit_format_rules() -> dict[str, tuple[str, ...]]:
    jp = {unit: (ibf.FMT_JP_BY_SCALE[scale],) for scale, unit in ibf.JP_UNIT_BY_SCALE.items()}
    usd = {unit: (ibf.FMT_USD_BY_SCALE[scale],) for scale, unit in ibf.USD_UNIT_BY_SCALE.items()}
    count_like = (spb.FMT_COUNT_V2, "0", "0.0")
    return {
        **jp,
        **usd,
        "x": (ibf.FMT_MULTIPLE, ibf.FMT_FACTOR),
        "months": (ibf.FMT_MONTHS_1DP, *count_like),
        "FTE": count_like,
        "units": count_like,
        "customers": count_like,
        "count": count_like,
        "check": (spb.FMT_CHECK_V2,),
    }


def _audit_unit_format_agreement(wb: Any) -> list[str]:
    """監査2: the unit label (column E) and the row's number format agree.

    Probes the first numeric or formula cell from the first period column
    onward — plain-text cells (notes, status prose) carry no scale and are
    not probed. Dedicated-column sheets (Valuation & Exit method matrix)
    keep their values left of column F and are exempt by construction."""
    rules = _unit_format_rules()
    issues: list[str] = []
    for ws in wb.worksheets:
        for row in range(8, ws.max_row + 1):
            unit = ws.cell(row=row, column=5).value
            if not isinstance(unit, str):
                continue
            probe = None
            for col in range(6, ws.max_column + 1):
                cell = ws.cell(row=row, column=col)
                value = cell.value
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    probe = cell
                    break
                if isinstance(value, str) and value.startswith("="):
                    probe = cell
                    break
            if probe is None:
                continue
            fmt = probe.number_format or ""
            ok = True
            if unit in rules:
                ok = fmt in rules[unit]
            elif unit == "%":
                ok = "%" in fmt
            if not ok:
                issues.append(
                    f"{ws.title}!{probe.coordinate} unit label {unit!r} disagrees "
                    f"with number format {fmt!r}"
                )
    return issues


def _audit_check_rows(wb: Any) -> list[str]:
    """監査3: P&L / BS / CF / Cap Table / Summary (when present) each carry at
    least one registered check row (numeric-delta cell with the OK/ERROR
    format), and Summary carries the master check."""
    issues: list[str] = []
    for name in ("P&L", "BS", "CF", "Cap Table", "Summary"):
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        has_check = any(
            cell.number_format == spb.FMT_CHECK_V2
            for row in ws.iter_rows()
            for cell in row
            if cell.value is not None
        )
        if not has_check:
            issues.append(f"{name} has no check row (OK/ERROR-format numeric delta)")
    if "Summary" in wb.sheetnames:
        labels = {
            str(cell.value)
            for row in wb["Summary"].iter_rows(min_col=3, max_col=3)
            for cell in row
            if cell.value
        }
        if "Master check" not in labels:
            issues.append("Summary has no master check row")
    return issues


def _audit_hardcoded_constants(wb: Any) -> list[str]:
    """監査5: numeric literals in formulas outside the structural whitelist
    ({0,1,-1,2,3,12,24,100,365,1000}, 0.5, and 0<x<1 tolerances/rates)."""
    issues: list[str] = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if not (isinstance(value, str) and value.startswith("=")):
                    continue
                body = re.sub(r'"[^"]*"', "", value)
                body = re.sub(r"'[^']*'!", "", body)
                body = re.sub(r"\$?[A-Z]{1,3}\$?\d+(:\$?[A-Z]{1,3}\$?\d+)?", "", body)
                for literal in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", body):
                    number = float(literal)
                    if literal in NUMERIC_FORMULA_WHITELIST or number == 0.5:
                        continue
                    if 0 < number < 1:  # tolerances / rates
                        continue
                    issues.append(
                        f"{ws.title}!{cell.coordinate} hardcoded constant {literal} "
                        f"outside the whitelist"
                    )
    return issues


def _normalize_r1c1(formula: str, col_idx: int) -> str:
    """Normalize relative column references to a column-offset form so one
    row formula compares copy-identical across period columns (R17)."""
    from openpyxl.utils import column_index_from_string

    def repl(match: re.Match) -> str:
        dollar_col, letters, dollar_row, digits = match.groups()
        if dollar_col == "$":
            return match.group(0)
        offset = column_index_from_string(letters) - col_idx
        return f"C[{offset}]{dollar_row}{digits}"

    return re.sub(r"(\$?)([A-Z]{1,3})(\$?)(\d+)", repl, formula)


def _audit_row_formula_consistency(wb: Any) -> list[str]:
    """監査6 (R17): within one row, every period-column formula must be the
    same formula in R1C1 terms — including across the monthly/annual grain
    boundary (grain awareness lives in the months-ruler reference, not in
    per-column formula edits)."""
    from openpyxl.utils import get_column_letter

    issues: list[str] = []
    for ws in wb.worksheets:
        cols = _v2_period_cols(ws)
        if len(cols) < 2:
            continue
        for row in range(8, ws.max_row + 1):
            forms: dict[int, str] = {}
            for col in cols:
                cell = ws.cell(row=row, column=col)
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    forms[col] = _normalize_r1c1(cell.value, col)
            if len(forms) >= 2 and len(set(forms.values())) > 1:
                variants = sorted(set(forms.values()))
                first_col = min(forms)
                issues.append(
                    f"{ws.title}!{get_column_letter(first_col)}{row} row formula "
                    f"varies across period columns ({len(variants)} variants)"
                )
    return issues


def _font_rgb(cell: Any) -> str | None:
    color = cell.font.color
    if color is None:
        return None
    rgb = getattr(color, "rgb", None)
    return rgb[-6:].upper() if isinstance(rgb, str) else None


def _sheet_values(ws: Any) -> set[str]:
    return {
        str(cell.value)
        for row in ws.iter_rows()
        for cell in row
        if cell.value not in (None, "")
    }


def _audit_font_design(wb: Any) -> list[str]:
    issues: list[str] = []
    allowed_sizes = {float(size) for size in ibf.FONT_SIZE_ALLOWED_CELLS}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                if cell.font.name is not None and cell.font.name != ibf.FONT_FAMILY:
                    issues.append(f"{ws.title}!{cell.coordinate} uses non-standard font {cell.font.name}")
                if cell.font.sz is not None and float(cell.font.sz) not in allowed_sizes:
                    issues.append(f"{ws.title}!{cell.coordinate} uses non-standard font size {cell.font.sz}")
    return issues


def _audit_semantic_alignment(wb: Any) -> list[str]:
    issues: list[str] = []
    header_rows = {4, 5, ibf.HEADER_PERIOD_ROW}
    for ws in wb.worksheets:
        if not spb.uses_default_layout(ws):
            continue
        period_cols = set(_v2_period_cols(ws))
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                alignment = cell.alignment
                horizontal = alignment.horizontal
                indent = getattr(alignment, "indent", 0)
                if (
                    cell.row in {4, ibf.HEADER_PERIOD_ROW}
                    and cell.column in period_cols
                    and horizontal not in (None, "center")
                ):
                    issues.append(f"{ws.title}!{cell.coordinate} period/header cell is {horizontal}, expected center")
                elif (
                    cell.row == 5
                    and cell.column in period_cols
                    and horizontal not in (None, "right", "center")
                ):
                    issues.append(f"{ws.title}!{cell.coordinate} months-ruler cell is {horizontal}, expected right/center")
                elif cell.row not in header_rows and cell.column == spb.LAYOUT.source_col:
                    rgb = _font_rgb(cell)
                    if horizontal not in (None, "left") or not cell.font.italic or (rgb is not None and rgb != ibf.IB_COMMENT):
                        issues.append(f"{ws.title}!{cell.coordinate} source cell alignment/font is non-standard")
                elif cell.row not in header_rows and cell.column == spb.LAYOUT.unit_col:
                    rgb = _font_rgb(cell)
                    if horizontal not in (None, "right") or (rgb is not None and rgb != ibf.IB_COMMENT):
                        issues.append(f"{ws.title}!{cell.coordinate} unit cell alignment/font is non-standard")
                elif cell.row not in header_rows and cell.column in (spb.LAYOUT.first_hierarchy_col, spb.LAYOUT.label_col):
                    if horizontal not in (None, "left") or indent:
                        issues.append(f"{ws.title}!{cell.coordinate} label cell is {horizontal} indent={indent}, expected left/no indent")
                elif cell.row not in header_rows and cell.column >= spb.LAYOUT.first_value_col:
                    value = cell.value
                    if isinstance(value, (int, float)) or (isinstance(value, str) and value.startswith("=")):
                        if horizontal not in (None, "right"):
                            issues.append(f"{ws.title}!{cell.coordinate} numeric/formula cell is {horizontal}, expected right")
    return issues


def audit_workbook(wb: Any) -> list[str]:
    """Return generation issues that should block an investor-ready handoff."""
    issues: list[str] = []
    available = set(wb.sheetnames)
    if _defined_name_count(wb):
        issues.append("workbook must not contain workbook-scoped or sheet-scoped defined names")
    for ws in wb.worksheets:
        # Freeze-pane polarity (S3): period-axis v2 sheets MUST freeze at
        # (first period col, row 7); non-period sheets are exempt (the old
        # blanket "no frozen panes" rule is retired).
        anchor_col = _v2_period_anchor_col(ws)
        if anchor_col is not None:
            expected_anchor = ws.cell(row=7, column=anchor_col).coordinate
            if ws.freeze_panes != expected_anchor:
                issues.append(
                    f"{ws.title} period-axis sheet must freeze at {expected_anchor} "
                    f"(found {ws.freeze_panes})"
                )
        if ws.merged_cells.ranges:
            issues.append(f"{ws.title} has merged cell range(s): {', '.join(str(rng) for rng in ws.merged_cells.ranges)}")
        sheet_values = _sheet_values(ws)
        missing_markers = _missing_sheet_markers(ws.title, sheet_values)
        if missing_markers:
            issues.append(f"{ws.title} is missing sheet-quality marker(s): {', '.join(missing_markers)}")
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if cell.alignment is not None and cell.alignment.wrap_text is True:
                    issues.append(f"{ws.title}!{cell.coordinate} has wrap_text enabled")
                if isinstance(value, str) and "\n" in value:
                    issues.append(f"{ws.title}!{cell.coordinate} contains a manual line break")
                if isinstance(value, str) and value.startswith("="):
                    missing = sorted(set(_SHEET_REF_RE.findall(value)) - available)
                    if missing:
                        issues.append(f"{ws.title}!{cell.coordinate} references omitted sheet(s): {', '.join(missing)}")
                if isinstance(value, str) and "#REF!" in value:
                    issues.append(f"{ws.title}!{cell.coordinate} contains #REF!")
    issues.extend(_audit_font_design(wb))
    issues.extend(_audit_semantic_alignment(wb))
    # S5 promoted audits (formerly quality_gates-only): width uniformity,
    # unit/format agreement, check-row presence, hardcode scan, R17.
    issues.extend(_audit_period_column_widths(wb))
    issues.extend(_audit_unit_format_agreement(wb))
    issues.extend(_audit_check_rows(wb))
    issues.extend(_audit_hardcoded_constants(wb))
    issues.extend(_audit_row_formula_consistency(wb))
    return issues


def _default_source_text() -> str:
    return (
        "# Startup financial plan\n"
        "Generic startup model for pricing, runway, financing, ownership, "
        "valuation, scenarios, and investor diligence. No explicit external "
        "source is listed."
    )


def _source_text_from_yaml(raw: dict[str, Any]) -> str:
    for key in ("source_text", "narrative", "story", "memo"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value
    company = raw.get("company") or raw.get("company_name") or "Startup"
    mechanics = raw.get("mechanics") or raw.get("business_model") or "generic startup"
    return f"# {company}\nGeneric financial model for a {mechanics}."


def _first_number(values: Any, default: float) -> float:
    """Return the first numeric scalar from a scalar/list-like YAML value."""
    if isinstance(values, (int, float)):
        return float(values)
    if isinstance(values, list):
        for value in values:
            if isinstance(value, (int, float)):
                return float(value)
    return default


def _money_m_from_yen(value: float, default_money_m: float) -> float:
    """Convert raw yen to reporting-currency millions for cap-table helpers."""
    if not value:
        return default_money_m
    return max(value / 1_000_000, 1.0)


def _cap_table_input_from_facts(facts: Any) -> ctb.CapTableInput:
    """Build a user-facing cap-table input from extracted model facts."""
    base = ctb.get_default_input()
    post_money = _money_m_from_yen(
        _first_number(getattr(facts, "post_money_yen", None), 0.0),
        base.round_pre_money_money_m + base.round_investment_money_m,
    )
    investment = _money_m_from_yen(
        _first_number(getattr(facts, "equity_raise_yen", None), 0.0),
        base.round_investment_money_m or 800.0,
    )
    pre_money = max(post_money - investment, investment)
    return ctb.CapTableInput(
        company_name=getattr(facts, "company", None) or base.company_name,
        reporting_currency=getattr(facts, "currency", None) or base.reporting_currency,
        as_of_date=base.as_of_date,
        founder_shares=base.founder_shares,
        common_pool_issued=base.common_pool_issued,
        common_pool_available=base.common_pool_available,
        safes=base.safes,
        preferred=base.preferred,
        round_pre_money_money_m=pre_money,
        round_investment_money_m=investment,
        round_target_pool_pct=base.round_target_pool_pct,
        round_anti_dilution_default=base.round_anti_dilution_default,
        round_label=base.round_label,
    )


def _serialize_live_comp(comp: lc.PublicComp) -> dict[str, object]:
    return {
        "ticker": comp.ticker,
        "name": comp.name,
        "company_type": comp.company_type,
        "source_type": comp.source_type,
        "stage": comp.stage,
        "geography": comp.geography,
        "applicability_limits": comp.applicability_limits,
        "currency": comp.currency,
        "market_cap": comp.market_cap,
        "enterprise_value": comp.enterprise_value,
        "revenue_multiple": comp.revenue_multiple,
        "ebitda_multiple": comp.ebitda_multiple,
        "gross_margin": comp.gross_margin,
        "ebitda_margin": comp.ebitda_margin,
        "source_url": comp.source_url,
        "as_of_date": comp.as_of_date,
        "status": comp.status,
        "error": comp.error,
    }


def _ticker_list_from_raw(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        return []
    return [str(item).strip().upper() for item in value if not isinstance(item, dict) and str(item).strip()]


def _provided_comps_from_raw_mapping(raw: dict[str, Any]) -> list[lc.PublicComp]:
    comps: list[lc.PublicComp] = []
    for key in ("live_comps", "public_comps", "private_comps", "transaction_comps", "benchmark_sources"):
        comps.extend(lc.provided_comps_from_raw(raw.get(key)))
    return comps


def _apply_live_comps_to_facts(
    facts: Any,
    tickers: list[str],
    *,
    timeout: float,
    provided_comps: list[lc.PublicComp] | None = None,
) -> Any:
    """Refresh public comps, merge provided private/transaction evidence, and apply valid medians."""
    if not tickers and not provided_comps:
        return facts
    fetched = lc.fetch_public_comps(tickers, timeout=timeout) if tickers else lc.summarize_comps([])
    result = lc.summarize_comps([*fetched.comps, *(provided_comps or [])], source_url="mixed comparable evidence")
    periods = len(getattr(facts, "period_labels", []) or [])
    overrides: dict[str, Any] = {
        "live_comps": [_serialize_live_comp(comp) for comp in result.comps],
    }
    if result.revenue_multiple_median and periods:
        overrides["revenue_multiple"] = [round(float(result.revenue_multiple_median), 1) for _ in range(periods)]
    if result.ebitda_multiple_median and periods:
        overrides["ebitda_multiple"] = [round(float(result.ebitda_multiple_median), 1) for _ in range(periods)]
    return replace(facts, **overrides)


def _default_live_comps_for_facts(facts: Any) -> list[str]:
    mechanics = str(getattr(facts, "mechanics", "") or "")
    return DEFAULT_PUBLIC_COMP_TICKERS.get(mechanics, DEFAULT_PUBLIC_COMP_TICKERS["Generic startup"])


# ============================================================================
# Build pipeline
# ============================================================================


def _facts_for_inputs(
    input_path: Path | None, source_md: Path | None
) -> tuple[Any, dict[str, Any]]:
    """Derive SourceFacts (and the raw YAML mapping) from CLI inputs.

    Single source of truth so the build path and the strict-audit economic
    coherence check operate on identical facts.
    """
    raw: dict[str, Any] = load_yaml(input_path) if input_path else {}
    if source_md is not None:
        return spb.extract_source_facts(source_md), raw
    if raw:
        return spb.derive_source_facts_from_mapping(raw), raw
    return spb.derive_source_facts(_default_source_text()), raw


def _facts_with_mode_defaults(
    facts: Any, mode: str, raw: dict[str, Any], source_md: Path | None
) -> Any:
    """Apply mode-level facts defaults (single source for build + CLI audit).

    burn_runway defaults to a monthly-first surface: when the input does not
    state a grain, promote the annual-canonical facts to the hybrid axis
    (24 monthly columns + annual tail) and re-anchor an unstated start year
    to the fiscal year in progress. An explicit `grain:` wins.
    """
    if mode == "burn_runway" and not raw.get("grain") and source_md is None:
        facts = replace(facts, grain="hybrid")
        facts = ek.anchor_facts_first_fiscal_year(facts)
    return facts


def build_model(
    input_path: Path | None,
    output_path: Path,
    mode: str = "full",
    additional_sheets: list[str] | None = None,
    excluded_sheets: list[str] | None = None,
    source_md: Path | None = None,
    live_comps: list[str] | None = None,
    live_comps_timeout: float = 8.0,
    auto_live_comps: bool = True,
) -> Path:
    """Build a startup finance xlsx model and save to `output_path`.

    Args:
        input_path: YAML input for focused mode outputs (None = defaults).
        output_path: Where to save the xlsx.
        mode: One of `VALID_MODES`.
        additional_sheets: Extra sheet IDs to add to the bundle.
        excluded_sheets: Sheet IDs to drop from the bundle.
        source_md: Narrative source markdown. When present, route to the
            generic economic-kernel workbook builder instead of focused mode.

    Returns:
        The output_path (for chaining). Use `resolve_bundle()` when callers also
        need the final generated sheet list.

    Raises:
        ValueError: Unknown mode.
    """
    source_route = source_md is not None
    facts, raw = _facts_for_inputs(input_path, source_md)
    facts = _facts_with_mode_defaults(facts, mode, raw, source_md)
    bundle = resolve_bundle(
        mode, additional_sheets, excluded_sheets,
        source_route=source_route, facts=facts,
    )
    raw_live_comps = raw.get("live_comps") or raw.get("public_comps") or []
    cli_live_comps = [str(item) for item in (live_comps or []) if str(item).strip()]
    yaml_live_comps = _ticker_list_from_raw(raw_live_comps)
    requested_live_comps = (
        cli_live_comps or yaml_live_comps or
        (_default_live_comps_for_facts(facts) if auto_live_comps else [])
    )
    facts = _apply_live_comps_to_facts(
        facts,
        requested_live_comps,
        timeout=live_comps_timeout,
        provided_comps=_provided_comps_from_raw_mapping(raw),
    )
    wb = spb.build_plan_workbook_v2(facts, bundle)

    if mode == "cap_table":
        ctb.build_cap_table_for_workbook(
            wb,
            _cap_table_input_from_facts(facts),
            exit_scenarios_money_m=[
                _money_m_from_yen(
                    _first_number(getattr(facts, "exit_value_yen", None), 0.0),
                    6_000.0,
                ),
                _money_m_from_yen(
                    _first_number(getattr(facts, "exit_value_yen", None), 0.0) * 1.5,
                    12_000.0,
                ),
            ],
        )

    # Safety net: the builder already creates exactly the bundle.
    for ws_name in list(wb.sheetnames):
        if ws_name not in bundle:
            wb.remove(wb[ws_name])
    if not wb.sheetnames:
        raise RuntimeError(
            f"Empty workbook after bundle filter (mode={mode}). "
            f"Check additional_sheets/excluded_sheets overrides."
        )

    # Font enforcement (Arial 10pt = Google Sheets default + IB std).
    ibf.normalize_workbook_fonts(wb)
    ibf.set_workbook_default_font(wb)
    _clear_defined_names(wb)
    spb._apply_print(wb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


# ============================================================================
# CLI
# ============================================================================


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="build_model.py",
        description=(
            "Builds startup financial-modeling xlsx outputs. Use --source-md "
            "for generic economic-kernel plans; use --mode for narrow "
            "focused finance modules."
        ),
    )
    ap.add_argument(
        "--input", "-i", type=Path, default=None,
        help="YAML input for focused mode output (omit for defaults).",
    )
    ap.add_argument(
        "--output", "-o", type=Path, default=Path("model_output.xlsx"),
        help="Output xlsx path (default: model_output.xlsx).",
    )
    ap.add_argument(
        "--source-md", type=Path, default=None,
        help=(
            "Narrative source markdown for a generic economic-kernel startup "
            "financial plan. Use for equity-story-to-model requests."
        ),
    )
    ap.add_argument(
        "--mode", "-m", choices=VALID_MODES, default="full",
        help="Output mode (default: full).",
    )
    ap.add_argument(
        "--additional-sheets", nargs="*", default=[], metavar="SHEET",
        help="Sheet names to add to the mode bundle (e.g. Valuation & Exit).",
    )
    ap.add_argument(
        "--excluded-sheets", nargs="*", default=[], metavar="SHEET",
        help="Sheet IDs to drop from the mode bundle.",
    )
    ap.add_argument(
        "--strict-audit", action="store_true",
        help=(
            "Reopen the generated workbook and fail on broken references, "
            "missing sheet-quality markers, or IB workbook design violations."
        ),
    )
    ap.add_argument(
        "--live-comps", nargs="*", default=[], metavar="TICKER",
        help="Override the auto-selected public ticker peers; private/transaction comps come from YAML evidence fields.",
    )
    ap.add_argument(
        "--live-comps-timeout", type=float, default=8.0,
        help="Timeout in seconds per live public-market comparable request.",
    )
    ap.add_argument(
        "--no-live-comps", action="store_true",
        help=(
            "Disable auto-selected public comparable refresh. YAML-provided "
            "private/transaction/benchmark evidence is still included."
        ),
    )
    args = ap.parse_args(argv)

    output = build_model(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        additional_sheets=args.additional_sheets,
        excluded_sheets=args.excluded_sheets,
        source_md=args.source_md,
        live_comps=args.live_comps,
        live_comps_timeout=args.live_comps_timeout,
        auto_live_comps=not args.no_live_comps,
    )
    bundle_facts, _bundle_raw = _facts_for_inputs(args.input, args.source_md)
    bundle_facts = _facts_with_mode_defaults(bundle_facts, args.mode, _bundle_raw, args.source_md)
    bundle = resolve_bundle(
        args.mode, args.additional_sheets, args.excluded_sheets,
        source_route=args.source_md is not None, facts=bundle_facts,
    )
    if args.strict_audit:
        from openpyxl import load_workbook

        audit_issues = audit_workbook(load_workbook(output, data_only=False))
        # Structural audit cannot see broken economics; the economic-coherence
        # audit replays the kernel projection and is profile/mode independent.
        audit_facts = bundle_facts
        audit_issues += [
            f"economic: {issue}" for issue in ek.audit_economic_coherence(audit_facts)
        ]
        if audit_issues:
            for issue in audit_issues:
                print(f"[audit] {issue}", file=sys.stderr)
            return 2
        # Task 3.4 (H): non-blocking transparency notes — K8 clamps and K6
        # revenue-provenance flags are printed, never fail the build.
        for warning in ek.audit_economic_warnings(audit_facts):
            print(f"[warn] {warning}", file=sys.stderr)
    print(f"[ok] xlsx generated: {output}")
    print(f"     mode = {args.mode!r}, sheets = {len(bundle)} ({', '.join(bundle)})")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
