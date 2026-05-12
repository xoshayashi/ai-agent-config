"""Build startup-financial-modeling xlsx outputs.

Primary route:
    python build_model.py --source-md equity_story.md --output plan.xlsx

That route generates a generic economic-kernel startup plan. The mode path is a
focused-module convenience for narrow requests such as pricing, cap table,
runway, valuation, market sizing, or three-statement mechanics. Every mode now
starts from the same economic-kernel workbook and only filters sheets.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml  # type: ignore
except ImportError:
    _yaml = None  # YAML loader is optional; defaults work without it.

import ib_format as ibf  # noqa: E402
import source_plan_builder as spb  # noqa: E402

# ============================================================================
# Mode -> seed sheet bundle for focused module outputs.
# ============================================================================

MODE_BUNDLE_SEEDS: dict[str, list[str]] = {
    "full": [
        "Guide", "Kernel", "Assumptions", "Driver Tree", "Revenue Build",
        "Cost Build", "People Plan", "P&L", "BS", "CF", "Capital Stack",
        "Ownership", "Pricing", "Financing", "Exit Waterfall", "Segments",
        "KPI", "Scenarios", "Sensitivity", "Valuation", "Market Support",
        "Benchmarks", "IC Memo",
    ],
    "pricing": [
        "Guide", "Kernel", "Assumptions", "Driver Tree", "Pricing", "IC Memo",
    ],
    "unit_economics": [
        "Guide", "Kernel", "Assumptions", "Driver Tree", "KPI", "Scenarios",
    ],
    "cap_table": [
        "Guide", "Kernel", "Capital Stack", "Ownership", "Financing",
        "Exit Waterfall", "IC Memo",
    ],
    "ma_exit": [
        "Guide", "Kernel", "Exit Waterfall", "Scenarios", "Sensitivity",
        "Valuation", "IC Memo",
    ],
    "dcf_only": [
        "Guide", "Kernel", "Valuation", "Sensitivity",
    ],
    "burn_runway": [
        "Guide", "Kernel", "CF", "Capital Stack", "Financing", "KPI",
    ],
    "three_statement": [
        "Guide", "Kernel", "P&L", "BS", "CF",
    ],
    "market_sizing": [
        "Guide", "Kernel", "Driver Tree", "Market Support", "Benchmarks",
    ],
    "comps_only": [
        "Guide", "Kernel", "Valuation", "Market Support", "Benchmarks", "IC Memo",
    ],
}

SHEET_DEPENDENCIES: dict[str, list[str]] = {
    "Driver Tree": ["Kernel"],
    "Revenue Build": ["Assumptions"],
    "Cost Build": ["Assumptions", "Revenue Build"],
    "People Plan": ["Assumptions", "Revenue Build", "Cost Build"],
    "P&L": ["Assumptions", "Revenue Build", "Cost Build", "People Plan", "Capital Stack"],
    "BS": ["Assumptions", "Revenue Build", "Cost Build", "P&L", "CF", "Capital Stack", "Financing"],
    "CF": ["Assumptions", "Cost Build", "P&L", "BS", "Capital Stack", "Financing"],
    "Capital Stack": ["CF", "Revenue Build", "Financing"],
    "Ownership": ["Capital Stack"],
    "Pricing": ["Assumptions", "KPI"],
    "Financing": ["Capital Stack", "Scenarios"],
    "Exit Waterfall": ["Capital Stack", "Ownership", "Scenarios", "Valuation"],
    "Segments": ["KPI"],
    "KPI": ["Assumptions", "Revenue Build", "Cost Build", "People Plan", "P&L", "CF", "Capital Stack", "Ownership"],
    "Scenarios": ["Revenue Build", "Cost Build", "P&L", "CF", "Valuation", "Ownership"],
    "Sensitivity": ["Revenue Build", "Cost Build", "P&L", "Capital Stack", "Ownership"],
    "Valuation": ["Revenue Build", "Cost Build", "P&L", "CF", "Capital Stack", "Segments"],
    "Market Support": ["Kernel"],
    "Benchmarks": ["Kernel"],
    "IC Memo": ["Kernel", "KPI", "Scenarios", "Valuation"],
}

VALID_MODES: list[str] = list(MODE_BUNDLE_SEEDS.keys())
VALID_SHEETS: set[str] = set(spb.SOURCE_PLAN_SHEETS)


def _validate_sheet_names(sheet_names: list[str], *, arg_name: str) -> None:
    unknown = [sheet for sheet in sheet_names if sheet not in VALID_SHEETS]
    if unknown:
        raise ValueError(f"Unknown sheet name(s) in {arg_name}: {unknown}. Valid: {spb.SOURCE_PLAN_SHEETS}")


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
) -> list[str]:
    """Return the exact sheet bundle generated for a mode plus overrides."""
    if mode not in MODE_BUNDLE_SEEDS:
        raise ValueError(f"Unknown mode {mode!r}. Valid: {VALID_MODES}")
    if additional_sheets:
        _validate_sheet_names(additional_sheets, arg_name="additional_sheets")
    if excluded_sheets:
        _validate_sheet_names(excluded_sheets, arg_name="excluded_sheets")

    bundle: list[str] = []
    pending = list(MODE_BUNDLE_SEEDS[mode])
    while pending:
        sheet = pending.pop(0)
        if sheet in bundle:
            continue
        bundle.append(sheet)
        pending.extend(SHEET_DEPENDENCIES.get(sheet, []))
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
    canonical_order = {sheet: idx for idx, sheet in enumerate(spb.SOURCE_PLAN_SHEETS)}
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


# ============================================================================
# Build pipeline
# ============================================================================


def build_model(
    input_path: Path | None,
    output_path: Path,
    mode: str = "full",
    additional_sheets: list[str] | None = None,
    excluded_sheets: list[str] | None = None,
    source_md: Path | None = None,
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
    bundle = resolve_bundle(mode, additional_sheets, excluded_sheets)

    raw: dict[str, Any] = load_yaml(input_path) if input_path else {}
    if source_md is not None:
        facts = spb.extract_source_facts(source_md)
    elif raw:
        facts = spb.derive_source_facts_from_mapping(raw)
    else:
        facts = spb.derive_source_facts(_default_source_text())
    wb = spb.build_source_plan_workbook_from_facts(facts)

    # Bundle filter (drop sheets outside selected mode).
    for ws_name in list(wb.sheetnames):
        if ws_name not in bundle:
            wb.remove(wb[ws_name])

    # Sanity: at least 1 sheet must remain (openpyxl requires it).
    if not wb.sheetnames:
        raise RuntimeError(
            f"Empty workbook after bundle filter (mode={mode}). "
            f"Check additional_sheets/excluded_sheets overrides."
        )

    # Font enforcement (Arial 10pt = Google Sheets default + IB std)
    # Two-stage:
    #   (a) Sweep existing cells whose font fell through to openpyxl-default
    #       Calibri 11 → Arial 10 (preserves explicit non-default fonts).
    #   (b) Override the persistent xlsx default (font index 0 + Normal style)
    #       so that rows added by the user AFTER save also inherit Arial 10.
    ibf.normalize_workbook_fonts(wb)
    ibf.set_workbook_default_font(wb)
    _clear_defined_names(wb)

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
        help="Sheet names to add to the mode bundle (e.g. Market Support).",
    )
    ap.add_argument(
        "--excluded-sheets", nargs="*", default=[], metavar="SHEET",
        help="Sheet IDs to drop from the mode bundle.",
    )
    args = ap.parse_args(argv)

    output = build_model(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        additional_sheets=args.additional_sheets,
        excluded_sheets=args.excluded_sheets,
        source_md=args.source_md,
    )
    bundle = resolve_bundle(args.mode, args.additional_sheets, args.excluded_sheets)
    print(f"[ok] xlsx generated: {output}")
    print(f"     mode = {args.mode!r}, sheets = {len(bundle)} ({', '.join(bundle)})")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
