"""Generic economic-kernel startup financial-plan workbook builder.

The source Markdown route builds an editable investor-grade xlsx from a generic
startup finance kernel. It does not start from a sector template. Source text is
used to infer mechanics such as marketplace, recurring software, hardware /
asset-heavy operations, lending, or pre-revenue R&D, then the same workbook
architecture is composed from drivers, operating logic, capital stack,
ownership, scenarios, valuation, and memo surfaces.
"""

from __future__ import annotations

import sys
import re
from copy import copy
from pathlib import Path
from dataclasses import dataclass

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ib_format as ib  # noqa: E402
from economic_kernel import (  # noqa: E402
    SourceFacts,
    average_units as _average_units,
    assumption_decomposition_for,
    derive_source_facts,
    derive_source_facts_from_mapping,
    driver_surfaces_for,
    ending_units as _ending_units,
    extract_source_facts,
    kpi_definitions_for,
    scenario_drivers_for,
)


SOURCE_PLAN_SHEETS = [
    "Guide",
    "Kernel",
    "Assumptions",
    "Driver Tree",
    "Revenue Build",
    "Cost Build",
    "People Plan",
    "P&L",
    "BS",
    "CF",
    "Capital Stack",
    "Ownership",
    "Pricing",
    "Financing",
    "Exit Waterfall",
    "Segments",
    "KPI",
    "Scenarios",
    "Sensitivity",
    "Valuation",
    "Market Support",
    "Benchmarks",
    "IC Memo",
]

@dataclass(frozen=True)
class LayoutSpec:
    hierarchy_cols: int = 1
    hierarchy_width: float = ib.COL_HIERARCHY_WIDTH
    label_width: float = ib.COL_LABEL_WIDTH
    source_width: float = ib.COL_SOURCE_WIDTH
    unit_width: float = ib.COL_UNIT_WIDTH
    period_width: float = ib.COL_PERIOD_WIDTH
    note_width: float = ib.COL_NOTE_WIDTH

    @property
    def first_hierarchy_col(self) -> int:
        return 2

    @property
    def label_col(self) -> int:
        return self.first_hierarchy_col + self.hierarchy_cols

    @property
    def source_col(self) -> int:
        return self.label_col + 1

    @property
    def unit_col(self) -> int:
        return self.source_col + 1

    @property
    def first_value_col(self) -> int:
        return self.unit_col + 1


LAYOUT = LayoutSpec()
START_PERIOD_COL = LAYOUT.first_value_col
BENCHMARK_REGISTER_START_COL = 2
BENCHMARK_FRESHNESS_COL = BENCHMARK_REGISTER_START_COL + 5
BENCHMARK_VALUATION_SUPPORT_ROW = 9


def _start_period_col() -> int:
    return LAYOUT.first_value_col
TAB_COLORS = {
    "Guide": ib.BRAND_NAVY,
    "Kernel": ib.BRAND_PRIMARY_DEEP,
    "Assumptions": ib.BRAND_PRIMARY_DEEP,
    "Driver Tree": ib.BRAND_PRIMARY,
    "Revenue Build": ib.BRAND_PRIMARY,
    "Cost Build": ib.BRAND_PRIMARY,
    "People Plan": ib.BRAND_PRIMARY,
    "P&L": ib.BRAND_SLATE,
    "BS": ib.BRAND_SLATE,
    "CF": ib.BRAND_SLATE,
    "Capital Stack": ib.BRAND_WARNING,
    "Ownership": ib.BRAND_WARNING,
    "Pricing": ib.BRAND_PRIMARY,
    "Financing": ib.BRAND_WARNING,
    "Exit Waterfall": ib.BRAND_WARNING,
    "Segments": ib.BRAND_PRIMARY,
    "KPI": ib.BRAND_PRIMARY,
    "Scenarios": ib.BRAND_WARNING,
    "Sensitivity": ib.BRAND_WARNING,
    "Valuation": ib.BRAND_PRIMARY,
    "Market Support": ib.BRAND_SLATE,
    "Benchmarks": ib.BRAND_WARNING,
    "IC Memo": ib.BRAND_ACCENT,
}

YEN_INPUT_SCALES = {
    "JPY K": 1_000,
    "JPY M": 1_000_000,
    "JPY B": 1_000_000_000,
    "JPY T": 1_000_000_000_000,
}

DISPLAY_UNIT_BY_SCALE = {
    ("JPY", "actual"): "円",
    ("JPY", "thousand"): "千円",
    ("JPY", "million"): "百万円",
    ("JPY", "hundred_million"): "億円",
    ("JPY", "billion"): "十億円",
    ("JPY", "trillion"): "兆円",
    ("USD", "actual"): "$",
    ("USD", "thousand"): "$K",
    ("USD", "million"): "$M",
}

YEN_DISPLAY_UNITS = {
    "JPY": "円",
    "JPY K": "千円",
    "JPY M": "百万円",
    "JPY B": "十億円",
    "JPY T": "兆円",
}


def _display_unit(unit: str, fmt: str | None = None, currency: str = "JPY", scale: str = "million") -> str:
    if unit == "JPY":
        if fmt in {ib.FMT_JPY_YEN, ib.FMT_USD_DOLLAR}:
            return DISPLAY_UNIT_BY_SCALE.get((currency, "actual"), "円")
        if fmt in {ib.FMT_JPY_THOUSAND, ib.FMT_USD_THOUSAND}:
            return DISPLAY_UNIT_BY_SCALE.get((currency, "thousand"), "千円")
        if fmt == ib.FMT_JPY_HUNDRED_MILLION:
            return DISPLAY_UNIT_BY_SCALE.get((currency, "hundred_million"), "億円")
        if fmt in {ib.FMT_MONEY, ib.FMT_MONEY_DECIMAL, ib.FMT_JPY_MILLION, ib.FMT_USD_MILLION}:
            return DISPLAY_UNIT_BY_SCALE.get((currency, scale), DISPLAY_UNIT_BY_SCALE.get((currency, "million"), "百万円"))
        return DISPLAY_UNIT_BY_SCALE.get((currency, "actual"), YEN_DISPLAY_UNITS["JPY"])
    return YEN_DISPLAY_UNITS.get(unit, unit)


def _normalise_formula_scale(formula: str) -> str:
    return formula.replace("/1000000", "").replace("*1000000", "")


def _model_value(value: object, unit: str) -> object:
    if isinstance(value, str) and value.startswith("="):
        return _normalise_formula_scale(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        scale = YEN_INPUT_SCALES.get(unit)
        if scale:
            return int(value * scale) if float(value * scale).is_integer() else value * scale
    return value


def _money_format(facts: SourceFacts) -> str:
    return ib.fmt_for_currency(facts.currency, facts.display_scale)


def _money_unit(facts: SourceFacts) -> str:
    return _display_unit("JPY", _money_format(facts), facts.currency, facts.display_scale)


def _facts_for_sheet(ws: Worksheet, facts: SourceFacts | None = None) -> SourceFacts | None:
    if facts is not None:
        return facts
    return getattr(ws, "_startup_facts", None)


def _format_for_unit(unit: str, requested_fmt: str, facts: SourceFacts | None = None) -> str:
    if unit == "%" or unit.startswith("%"):
        return ib.FMT_PERCENT
    if unit == "x":
        return ib.FMT_MULTIPLE
    if unit in {"months", "count"}:
        return ib.FMT_NUM
    if unit in {"units", "customers", "FTE", "days"}:
        return ib.FMT_INTEGER
    if unit == "JPY":
        if facts is not None:
            if requested_fmt == ib.FMT_MONEY:
                return _money_format(facts)
            if requested_fmt == ib.FMT_JPY_YEN:
                return ib.fmt_for_currency(facts.currency, "actual")
            if requested_fmt == ib.FMT_JPY_THOUSAND:
                return ib.fmt_for_currency(facts.currency, "thousand")
        return requested_fmt
    return requested_fmt


FMT_KEY_MAP = {
    "money": ib.FMT_MONEY,
    "jpy_yen": ib.FMT_JPY_YEN,
    "integer": ib.FMT_INTEGER,
    "percent": ib.FMT_PERCENT,
    "multiple": ib.FMT_MULTIPLE,
    "num": ib.FMT_NUM,
    "text": ib.FMT_NUM,
}


def _apply_unit_cell(cell) -> None:
    cell.font = ib.FONT_COMMENT
    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)


def _disable_wrap_text(wb: Workbook) -> None:
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.alignment is not None and cell.alignment.wrap_text is True:
                    alignment = copy(cell.alignment)
                    alignment.wrap_text = False
                    cell.alignment = alignment


def _clear_blank_cell_styles(wb: Workbook) -> None:
    ib.clear_blank_cell_styles(wb)


def _last_value_bounds(ws: Worksheet) -> tuple[int, int]:
    return ib.last_value_bounds(ws)


def _rendered_bounds(ws: Worksheet) -> tuple[int, int]:
    return ib.rendered_bounds(ws)


def _trim_blank_canvas(wb: Workbook) -> None:
    ib.trim_blank_canvas(wb)


def _setup_sheet(
    ws: Worksheet,
    title: str,
    subtitle: str = "",
    period_sheet: bool = False,
    periods: int = 0,
) -> None:
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = None
    ws.column_dimensions["A"].width = 3
    for col in range(LAYOUT.first_hierarchy_col, LAYOUT.label_col):
        ws.column_dimensions[get_column_letter(col)].width = LAYOUT.hierarchy_width
    ws.column_dimensions[get_column_letter(LAYOUT.label_col)].width = LAYOUT.label_width
    ws.column_dimensions[get_column_letter(LAYOUT.source_col)].width = LAYOUT.source_width
    ws.column_dimensions[get_column_letter(LAYOUT.unit_col)].width = LAYOUT.unit_width
    if period_sheet:
        for col in range(_start_period_col(), _start_period_col() + max(periods, 1)):
            ws.column_dimensions[get_column_letter(col)].width = LAYOUT.period_width
        ws.column_dimensions[get_column_letter(_start_period_col() + max(periods, 1))].width = LAYOUT.note_width
    ws["B2"] = title
    ws["B2"].font = Font(name=ib.FONT_FAMILY, size=14, bold=True, color=ib.IB_INK)
    ws["B3"] = subtitle
    ws["B3"].font = ib.FONT_COMMENT
    ws["B3"].alignment = Alignment(wrap_text=False)
    ws.sheet_properties.tabColor = TAB_COLORS.get(ws.title, ib.BRAND_SLATE)


def _set_column_widths(ws: Worksheet, widths: dict[int | str, float]) -> None:
    role_min_widths = {
        LAYOUT.label_col: LAYOUT.label_width,
        LAYOUT.source_col: LAYOUT.source_width,
        LAYOUT.unit_col: LAYOUT.unit_width,
    }
    for col, width in widths.items():
        letter = col if isinstance(col, str) else get_column_letter(col)
        col_index = col if isinstance(col, int) else ws[letter + "1"].column
        floor = role_min_widths.get(col_index, 0)
        ws.column_dimensions[letter].width = max(width, floor)


def _period_cols(facts: SourceFacts) -> list[int]:
    return list(range(_start_period_col(), _start_period_col() + len(facts.period_labels)))


def _final_period_col(facts: SourceFacts) -> str:
    return get_column_letter(_period_cols(facts)[-1])


def _period_range_label(facts: SourceFacts) -> str:
    return f"{facts.period_labels[0]}-{facts.period_labels[-1]}"


def _period_display(facts: SourceFacts) -> str:
    return f"{facts.grain} {_period_range_label(facts)}"


def _write_period_header(ws: Worksheet, facts: SourceFacts, row: int = 5) -> None:
    for col in _period_cols(facts):
        ws.column_dimensions[get_column_letter(col)].width = LAYOUT.period_width
    ws.column_dimensions[get_column_letter(_start_period_col() + len(facts.period_labels))].width = LAYOUT.note_width
    ib.apply_semantic_fill_span(
        ws,
        row,
        LAYOUT.first_hierarchy_col,
        _start_period_col() + len(facts.period_labels) - 1,
        ib.BG_TABLE_HEADER,
        bottom=ib.THIN_LINE,
        border_start_col=_row_rule_start_col(ws),
    )
    for col, label in zip(_period_cols(facts), facts.period_labels):
        cell = ws.cell(row=row, column=col, value=label)
        ib.apply_year_header(cell, label)
    headers = [(LAYOUT.first_hierarchy_col, ""), (LAYOUT.label_col, "Line item"), (LAYOUT.source_col, "Source / driver"), (LAYOUT.unit_col, "Unit")]
    for col, label in headers:
        c = ws.cell(row=row, column=col, value=label if label else None)
        c.font = ib.FONT_BODY_BOLD
        c.alignment = Alignment(horizontal="left" if col in (LAYOUT.first_hierarchy_col, LAYOUT.label_col, LAYOUT.source_col) else "right", vertical="center", wrap_text=False)


def _apply_text_header(cell, label: str) -> None:
    cell.value = label
    cell.font = ib.FONT_BODY_BOLD
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
    ib.apply_semantic_fill_span(cell.parent, cell.row, cell.column, cell.column, ib.BG_TABLE_HEADER, bottom=ib.THIN_LINE)


def _compact_status(value: object) -> object:
    if not isinstance(value, str):
        return value
    text = value.strip()
    normalized = text.lower()
    if normalized in {"estimate / needs validation", "estimate/needs validation"}:
        return "estimate"
    if "pipeline" in normalized and "estimate" in normalized:
        return "pipeline-backed"
    if "management target" in normalized:
        return "management target"
    if "placeholder" in normalized:
        return "placeholder"
    if "unknown" in normalized:
        return "unknown"
    return text


def _section_band_end_col(ws: Worksheet, explicit_end_col: int | None = None) -> int:
    if explicit_end_col is not None:
        return explicit_end_col
    note_col = getattr(ws, "_startup_note_col", None)
    facts = _facts_for_sheet(ws)
    if facts is not None:
        return max(
            LAYOUT.unit_col,
            _start_period_col() + len(facts.period_labels) - 1,
            note_col or 0,
        )
    return max(LAYOUT.unit_col, ws.max_column)


def _section(ws: Worksheet, row: int, label: str, end_col: int | None = None) -> None:
    band_end_col = _section_band_end_col(ws, end_col)
    cell = ws.cell(row=row, column=LAYOUT.first_hierarchy_col, value=label)
    cell.font = Font(name=ib.FONT_FAMILY, size=10, bold=True, color="FFFFFF")
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
    ib.apply_semantic_fill_span(
        ws,
        row,
        LAYOUT.first_hierarchy_col,
        band_end_col,
        ib.BG_HEADER_BAND,
        bottom=ib.THIN_LINE,
        border_start_col=_row_rule_start_col(ws),
    )
    ws.row_dimensions[row].height = ib.ROW_HEIGHT_RELAXED


def _note(ws: Worksheet, row: int, text: str) -> None:
    note_col = getattr(ws, "_startup_note_col", None)
    if note_col is None:
        note_col = max(ws.max_column + 1, 10)
        ws._startup_note_col = note_col
    ws.column_dimensions[get_column_letter(note_col)].width = LAYOUT.note_width
    cell = ws.cell(row=row, column=note_col, value=text)
    ib.apply_comment(cell, wrap_text=False)


def _label(
    ws: Worksheet,
    row: int,
    label: str,
    unit: str = "",
    source: str = "",
    note: str = "",
    bold: bool = False,
    fmt: str | None = None,
    facts: SourceFacts | None = None,
) -> None:
    facts = _facts_for_sheet(ws, facts)
    ws.cell(row=row, column=LAYOUT.label_col, value=label)
    ws.cell(row=row, column=LAYOUT.source_col, value=source)
    currency = facts.currency if facts is not None else "JPY"
    scale = facts.display_scale if facts is not None else "million"
    ws.cell(row=row, column=LAYOUT.unit_col, value=_display_unit(unit, fmt, currency, scale))
    ib.apply_label(ws.cell(row=row, column=LAYOUT.label_col), bold=bold)
    if source:
        ib.apply_comment(ws.cell(row=row, column=LAYOUT.source_col), wrap_text=False)
    _apply_unit_cell(ws.cell(row=row, column=LAYOUT.unit_col))
    if note:
        _note(ws, row, note)


def _highlight_row(ws: Worksheet, row: int, last_col: int | None = None) -> None:
    end_col = last_col if last_col is not None else max(ws.max_column, 9)
    facts = _facts_for_sheet(ws)
    period_end_col = _start_period_col() + len(facts.period_labels) - 1 if facts is not None else end_col
    border_end_col = min(end_col, period_end_col)
    ib.apply_semantic_fill_span(
        ws,
        row,
        LAYOUT.first_hierarchy_col,
        end_col,
        ib.BG_WORKING,
    )
    accent_cols = [LAYOUT.label_col, *range(_start_period_col(), border_end_col + 1)]
    for col in accent_cols:
        cell = ws.cell(row=row, column=col)
        cell.border = _merge_border(cell.border, top=ib.THIN_LINE, bottom=ib.THIN_LINE)


def _merge_border(existing: Border | None, *, top=None, bottom=None, left=None, right=None) -> Border:
    if existing is None:
        return Border(top=top, bottom=bottom, left=left, right=right)
    return Border(
        top=top if top is not None else existing.top,
        bottom=bottom if bottom is not None else existing.bottom,
        left=left if left is not None else existing.left,
        right=right if right is not None else existing.right,
    )


def _fill_rgb(cell) -> str | None:
    fill = cell.fill
    if fill is None or fill.fill_type != "solid":
        return None
    value = getattr(fill.fgColor, "rgb", None)
    return value[-6:].upper() if isinstance(value, str) else None


def _is_section_row(ws: Worksheet, row: int) -> bool:
    fill = ws.cell(row=row, column=LAYOUT.first_hierarchy_col).fill
    value = getattr(fill.fgColor, "rgb", None)
    if fill.fill_type == "solid" and isinstance(value, str) and value.endswith(ib.BG_HEADER_BAND):
        return True
    color = ws.cell(row=row, column=LAYOUT.first_hierarchy_col).font.color
    font_rgb = getattr(color, "rgb", None)
    return isinstance(font_rgb, str) and font_rgb.endswith(ib.BG_HEADER_BAND)


def _is_highlight_row(ws: Worksheet, row: int) -> bool:
    fill = ws.cell(row=row, column=LAYOUT.first_hierarchy_col).fill
    value = getattr(fill.fgColor, "rgb", None)
    return fill.fill_type == "solid" and isinstance(value, str) and value.endswith(ib.BG_WORKING)


def _uses_default_layout(ws: Worksheet) -> bool:
    hierarchy_values = [
        ws.cell(row=5, column=col).value
        for col in range(LAYOUT.first_hierarchy_col, LAYOUT.label_col)
    ]
    role_values = [
        ws.cell(row=5, column=LAYOUT.label_col).value,
        ws.cell(row=5, column=LAYOUT.source_col).value,
        ws.cell(row=5, column=LAYOUT.unit_col).value,
    ]
    return hierarchy_values == [None] * LAYOUT.hierarchy_cols and role_values == [
        "Line item",
        "Source / driver",
        "Unit",
    ]


def _is_hierarchy_spacer_col(ws: Worksheet, col: int) -> bool:
    width = ws.column_dimensions[get_column_letter(col)].width
    return width is not None and abs(float(width) - float(LAYOUT.hierarchy_width)) < 0.001


def _row_rule_start_col(ws: Worksheet) -> int:
    if LAYOUT.hierarchy_cols > 0:
        return LAYOUT.label_col
    return LAYOUT.label_col if _is_hierarchy_spacer_col(ws, LAYOUT.first_hierarchy_col) else LAYOUT.first_hierarchy_col


def _apply_design_surface(wb: Workbook) -> None:
    header_row_fill = PatternFill("solid", fgColor=ib.BG_TABLE_HEADER)
    for ws in wb.worksheets:
        uses_default_layout = _uses_default_layout(ws)
        max_col = max(ws.max_column, 9)
        max_row = max(ws.max_row, 5)
        ws.freeze_panes = None
        for row in range(1, max_row + 1):
            row_has_value = any(ws.cell(row=row, column=col).value is not None for col in range(1, max_col + 1))
            is_section = _is_section_row(ws, row)
            for col in range(1, max_col + 1):
                cell = ws.cell(row=row, column=col)
                if cell.value is None:
                    continue
                if is_section and col == LAYOUT.first_hierarchy_col:
                    if _fill_rgb(cell) == ib.BG_HEADER_BAND:
                        cell.font = Font(name=ib.FONT_FAMILY, size=10, bold=True, color="FFFFFF")
                    else:
                        cell.font = Font(name=ib.FONT_FAMILY, size=10, bold=True, color=ib.BG_HEADER_BAND)
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
                    continue
                if row == 5 and row_has_value and col >= LAYOUT.first_hierarchy_col and not is_section:
                    cell.fill = header_row_fill
                    if col >= LAYOUT.label_col:
                        cell.border = _merge_border(cell.border, bottom=ib.THIN_LINE)
                if uses_default_layout and col == LAYOUT.source_col and row != 5:
                    ib.apply_comment(cell, wrap_text=False)
                elif uses_default_layout and col == LAYOUT.unit_col and row != 5:
                    _apply_unit_cell(cell)
                elif uses_default_layout and col in (LAYOUT.first_hierarchy_col, LAYOUT.label_col) and row != 5:
                    ib.apply_label(cell, bold=cell.font.bold is True)

def _apply_value_style(cell, fmt: str) -> None:
    value = cell.value
    if isinstance(value, str) and value.startswith("="):
        if "!" in value:
            ib.apply_link_intra(cell, fmt)
        else:
            ib.apply_formula(cell, fmt)
    else:
        ib.apply_hard_input(cell, fmt)


def _write_values(
    ws: Worksheet,
    row: int,
    label: str,
    unit: str,
    values: list[object],
    *,
    source: str = "",
    note: str = "",
    kind: str = "input",
    fmt: str = ib.FMT_MONEY,
    bold: bool = False,
    facts: SourceFacts | None = None,
) -> None:
    facts = _facts_for_sheet(ws, facts)
    applied_fmt = _format_for_unit(unit, fmt, facts)
    _label(ws, row, label, unit, source, note, bold=bold, fmt=applied_fmt, facts=facts)
    period_cols = list(range(_start_period_col(), _start_period_col() + len(values)))
    for col, value in zip(period_cols, values):
        model_value = _model_value(value, unit)
        cell = ws.cell(row=row, column=col, value=model_value)
        if kind == "formula" and not (isinstance(model_value, str) and model_value.startswith("=")):
            ib.apply_formula(cell, applied_fmt)
        else:
            _apply_value_style(cell, applied_fmt)
    if bold:
        accent_cols = [LAYOUT.label_col, *period_cols]
        for col in accent_cols:
            cell = ws.cell(row=row, column=col)
            if cell.value is None:
                continue
            font = copy(cell.font)
            font.bold = True
            cell.font = font
            cell.border = ib.BORDER_SUBTOTAL


def _label_rows(ws: Worksheet, labels: tuple[str, ...], *, max_row: int | None = None) -> dict[str, int]:
    wanted = set(labels)
    found: dict[str, int] = {}
    scan_until = max_row or ws.max_row
    for row in range(1, scan_until + 1):
        value = ws.cell(row=row, column=LAYOUT.label_col).value
        if value in wanted:
            found[str(value)] = row
    missing = wanted - set(found)
    if missing:
        raise KeyError(f"Missing labels while building row references: {', '.join(sorted(missing))}")
    return found


def _resolve_row_refs(value: str, row_by_label: dict[str, int]) -> str:
    def repl(match: re.Match[str]) -> str:
        label = match.group(1)
        if label not in row_by_label:
            raise KeyError(f"Unknown assumption decomposition row reference: {label}")
        return str(row_by_label[label])

    return re.sub(r"\{row:([^}]+)\}", repl, value)


def _render_decomposition_values(values: object, cols: list[int], row_by_label: dict[str, int]) -> list[object]:
    if isinstance(values, list):
        raw_values = values
    else:
        raw_values = [values for _ in cols]
    rendered: list[object] = []
    for idx, col in enumerate(cols):
        value = raw_values[idx] if idx < len(raw_values) else raw_values[-1]
        if isinstance(value, str):
            text = _resolve_row_refs(value, row_by_label)
            text = text.format(c=get_column_letter(col))
            rendered.append(text)
        else:
            rendered.append(value)
    return rendered


def _write_decomposition_status(ws: Worksheet, row: int, label: str, values: list[object], source: str = "", note: str = "") -> None:
    _label(ws, row, label, "status", source=source, note=note)
    for col, value in zip(_period_cols(_facts_for_sheet(ws)), values):
        cell = ws.cell(row=row, column=col, value=_compact_status(value))
        ib.apply_comment(cell, wrap_text=False)


def _apply_print(wb: Workbook) -> None:
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 90
        last_row, last_col = _rendered_bounds(ws)
        ib.setup_print_layout(
            ws,
            orientation="landscape",
            fit_to_width=1,
            print_title_rows="1:5",
            print_title_cols=f"A:{get_column_letter(LAYOUT.unit_col)}",
            footer_right="&P / &N",
        )
        ws.print_area = f"A1:{get_column_letter(last_col)}{last_row}"
        for row in range(1, last_row + 1):
            if ws.row_dimensions[row].height is None:
                ws.row_dimensions[row].height = ib.ROW_HEIGHT_BASE
        ws.row_dimensions[2].height = 20
        ws.row_dimensions[3].height = 15
        ws.row_dimensions[5].height = 18


def _add_line_chart(ws: Worksheet, title: str, data_ref: Reference, cats_ref: Reference, anchor: str, y_axis_title: str = "") -> None:
    chart = LineChart()
    chart.title = title
    chart.y_axis.title = y_axis_title
    chart.height = 7
    chart.width = 14
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    ib.apply_chart_palette(chart, ib.IB_CHART_COLORS_LINE)
    ws.add_chart(chart, anchor)


def _add_bar_chart(ws: Worksheet, title: str, data_ref: Reference, cats_ref: Reference, anchor: str, y_axis_title: str = "") -> None:
    chart = BarChart()
    chart.title = title
    chart.y_axis.title = y_axis_title
    chart.height = 7
    chart.width = 14
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    ib.apply_chart_palette(chart, ib.IB_CHART_COLORS_BAR)
    ws.add_chart(chart, anchor)


def _build_guide(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Guide"]
    _setup_sheet(ws, f"{facts.company} Financial Model Guide", "Generic economic-kernel workbook assembled from the source narrative.")
    _set_column_widths(ws, {2: 30, 3: 128})
    rows = [
        ("Purpose", "Investor-ready startup financial plan with traceable assumptions and editable formulas."),
        ("Source story signals", facts.source_summary),
        ("Model standard", f"{_period_display(facts)}, raw base-currency values, Excel number formats for display scale, direct formulas, no workbook names, no merged cells."),
        ("Workbook map", "Kernel -> Assumptions -> Driver Tree -> Revenue/Cost/People -> P&L/BS/CF -> Capital/Ownership -> KPI/Scenarios/Valuation -> Memo."),
        ("Color rule", "Blue = editable hard input; black = formula; green = cross-sheet link; gray italic = note/source."),
        ("Decision lens", "Use the smallest complete logic graph that supports pricing, runway, financing, ownership, valuation, and investor diligence."),
    ]
    for idx, (label, text) in enumerate(rows, start=7):
        ws.cell(idx, 2, label)
        ws.cell(idx, 3, text)
        ib.apply_label(ws.cell(idx, 2), bold=True)
        ib.apply_comment(ws.cell(idx, 3), wrap_text=False)
    _section(ws, 15, "Sheet-level acceptance criteria")
    criteria = [
        ("Kernel", "Decision, model grain, mechanics, source status, and unknowns are explicit."),
        ("Assumptions", "Every driver has unit, source/driver, and editable or formula status."),
        ("Driver Tree", "Economic dependencies are visible before financial statements."),
        ("Capital Stack / Ownership", "Cash, debt, equity, dilution, option pool, and investor ownership connect to the plan."),
        ("Scenarios / Valuation", "Key driver pressure is translated into cash, dilution, value, and IC questions."),
    ]
    for r, (sheet, text) in enumerate(criteria, start=16):
        ws.cell(r, 2, sheet)
        ws.cell(r, 3, text)
        ib.apply_label(ws.cell(r, 2), bold=True)
        ib.apply_comment(ws.cell(r, 3), wrap_text=False)


def _build_kernel(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Kernel"]
    _setup_sheet(ws, f"{facts.company} — Economic kernel", "Economic kernel before workbook tabs: decision, grain, mechanics, source status.")
    _set_column_widths(ws, {3: 32, 4: 92})
    _section(ws, 6, "Kernel definition")
    rows = [
        ("Decision", "Build a startup financial plan for fundraising, board, lender, or investor diligence decisions."),
        ("Model grain", _period_display(facts)),
        ("Mechanics", facts.mechanics),
        ("Primary unit", facts.primary_unit_name),
        ("Product", facts.product),
        ("Currency", facts.currency),
        ("Source status", "; ".join(facts.source_names) if facts.source_names else "No explicit external source listed"),
        ("Unknowns", "; ".join(facts.source_unknowns)),
    ]
    for r, (label, value) in enumerate(rows, start=7):
        ws.cell(r, 3, label)
        ws.cell(r, 4, value)
        ib.apply_label(ws.cell(r, 3), bold=True)
        ib.apply_comment(ws.cell(r, 4), wrap_text=False)
    _section(ws, 17, "Engine composition")
    engines = [
        ("Operating engine", "Primary units / GMV / customers -> revenue -> gross profit."),
        ("Cost engine", "Variable COGS, delivery cost, support load, cloud/platform cost, and headcount."),
        ("Asset engine", "CapEx, depreciation, inventory, and capacity-linked investment where relevant."),
        ("Working-capital engine", "AR, AP, deferred revenue, inventory, tax timing, and cash conversion."),
        ("Capital stack", "Equity, debt, option pool, dilution, cash runway, and investor return."),
        ("Scenario engine", "Base/downside/upside plus sensitivity around the decision-critical drivers."),
    ]
    for r, (engine, body) in enumerate(engines, start=18):
        ws.cell(r, 3, engine)
        ws.cell(r, 4, body)
        ib.apply_label(ws.cell(r, 3), bold=True)
        ib.apply_comment(ws.cell(r, 4), wrap_text=False)


def _build_assumptions(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Assumptions"]
    _setup_sheet(ws, f"{facts.company} — Assumptions", "Editable driver layer. Values are raw units / raw base-currency values; formats handle display scale.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    ending = _ending_units(facts.new_units)
    average = _average_units(ending)

    _section(ws, 6, "Volume and demand")
    _write_values(ws, 7, "New primary units", "units", facts.new_units, source="source / ramp", fmt=ib.FMT_INTEGER)
    _write_values(ws, 8, "Ending primary units", "units", ending, source="formula ramp", fmt=ib.FMT_INTEGER)
    _write_values(ws, 9, "Average primary units", "units", average, source="period average", fmt=ib.FMT_INTEGER)
    _write_values(ws, 10, "Gross merchandise value", "JPY", facts.gmv_yen, source="GMV / economic volume", fmt=ib.FMT_MONEY)
    _write_values(ws, 11, "Monthly price / unit", "JPY", facts.monthly_price_yen, source="pricing anchor", fmt=ib.FMT_JPY_YEN, note="For non-unit models this remains an optional recurring-price driver.")
    _write_values(ws, 12, "Take rate", "%", facts.take_rate, source="transaction monetization", fmt=ib.FMT_PERCENT)
    _write_values(ws, 13, "Total customers", "customers", facts.customers, source="customer / account count", fmt=ib.FMT_INTEGER)
    _write_values(ws, 14, "Net retention", "%", facts.net_retention, source="cohort behavior", fmt=ib.FMT_PERCENT)
    _write_values(ws, 15, "Utilization / conversion", "%", facts.utilization_conversion, source="operational leverage", fmt=ib.FMT_PERCENT)

    _section(ws, 18, "Revenue adjuncts")
    _write_values(ws, 19, "One-time revenue / new unit", "JPY", [f"={get_column_letter(c)}11*3" for c in cols], kind="formula", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 20, "Other revenue / total revenue", "%", facts.other_revenue_share, source="services / add-ons", fmt=ib.FMT_PERCENT)
    _write_values(ws, 21, "Deferred revenue share", "%", facts.deferred_revenue_share, source="billing timing", fmt=ib.FMT_PERCENT)

    _section(ws, 23, "Unit cost and delivery")
    _write_values(ws, 24, "Variable COGS", "%", facts.variable_cogs_pct, source="cost-to-serve curve", fmt=ib.FMT_PERCENT)
    _write_values(ws, 25, "Delivery cost / primary unit", "JPY", facts.delivery_cost_yen, source="implementation / service", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 26, "Cloud / platform cost", "JPY", facts.cloud_cost_yen, source="infrastructure", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 27, "Support cost / customer", "JPY", facts.support_cost_yen, source="support operations", fmt=ib.FMT_JPY_YEN)

    _section(ws, 30, "People and productivity")
    _write_values(ws, 31, "Product/R&D headcount", "FTE", facts.product_headcount, source="product roadmap", fmt=ib.FMT_INTEGER)
    _write_values(ws, 32, "GTM headcount", "FTE", facts.gtm_headcount, source="sales capacity", fmt=ib.FMT_INTEGER)
    _write_values(ws, 33, "Operations/CS headcount", "FTE", facts.operations_headcount, source="delivery / support", fmt=ib.FMT_INTEGER)
    _write_values(ws, 34, "G&A headcount", "FTE", facts.ga_headcount, source="company build", fmt=ib.FMT_INTEGER)
    _write_values(ws, 35, "Total headcount", "FTE", [f"=SUM({get_column_letter(c)}31:{get_column_letter(c)}34)" for c in cols], kind="formula", fmt=ib.FMT_INTEGER, bold=True)
    _write_values(ws, 36, "Avg loaded comp / FTE", "JPY", facts.avg_comp_yen, source="talent cost", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 37, "Revenue productivity factor", "x", facts.revenue_productivity_factor, source="operating leverage", fmt=ib.FMT_MULTIPLE)
    _write_values(ws, 38, "CapEx / primary unit", "JPY", facts.capex_per_unit_yen, source="asset / setup investment", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 39, "Depreciation life", "months", facts.depreciation_life_months, source="asset policy", fmt=ib.FMT_INTEGER)
    _write_values(ws, 40, "Other CapEx", "JPY", facts.other_capex_yen, source="labs / systems / tooling", fmt=ib.FMT_MONEY)

    _section(ws, 43, "Working capital and tax")
    _write_values(ws, 44, "AR days", "days", facts.ar_days, source="collection terms", fmt=ib.FMT_INTEGER)
    _write_values(ws, 45, "AP days", "days", facts.ap_days, source="supplier terms", fmt=ib.FMT_INTEGER)
    _write_values(ws, 46, "Tax rate", "%", facts.tax_rate, source="NOL / tax timing", fmt=ib.FMT_PERCENT)
    beginning_cash = [facts.beginning_cash_yen]
    for prior_col in cols[:-1]:
        prior = get_column_letter(prior_col)
        beginning_cash.append(f"={prior}47+'CF'!{prior}23")
    _write_values(ws, 47, "Beginning cash", "JPY", beginning_cash, source="cash roll-forward", kind="formula", fmt=ib.FMT_MONEY)
    ib.apply_hard_input(ws.cell(47, _start_period_col()), _money_format(facts))

    _section(ws, 50, "Operating policy")
    _write_values(ws, 51, "S&M / revenue", "%", facts.sm_pct_revenue, source="go-to-market spend policy", fmt=ib.FMT_PERCENT)
    _write_values(ws, 52, "R&D program / product FTE", "JPY", facts.rd_program_per_product_fte_yen, source="product roadmap spend", fmt=ib.FMT_JPY_YEN)
    _write_values(ws, 53, "R&D program floor", "JPY", facts.rd_program_floor_yen, source="minimum roadmap spend", fmt=ib.FMT_MONEY)
    _write_values(ws, 54, "G&A / revenue", "%", facts.ga_pct_revenue, source="company infrastructure", fmt=ib.FMT_PERCENT)
    _write_values(ws, 55, "Fixed G&A / systems", "JPY", facts.fixed_ga_yen, source="systems and admin base", fmt=ib.FMT_MONEY)
    _write_values(ws, 56, "Inventory / WIP share of CapEx", "%", facts.inventory_wip_pct_capex, source="working capital policy", fmt=ib.FMT_PERCENT)
    _write_values(ws, 57, "Opening equity / prior capital", "JPY", [facts.beginning_cash_yen] + [0 for _ in cols[1:]], source="opening balance", fmt=ib.FMT_MONEY)
    _write_values(ws, 58, "Payment fees / GMV", "%", [facts.payment_fee_pct for _ in cols], source="marketplace / payments", fmt=ib.FMT_PERCENT)
    _write_values(ws, 59, "Incentives / GMV", "%", [facts.incentive_pct_gmv for _ in cols], source="liquidity / promotion", fmt=ib.FMT_PERCENT)
    _write_values(ws, 60, "Fraud and loss / GMV", "%", [facts.fraud_loss_pct_gmv for _ in cols], source="risk loss", fmt=ib.FMT_PERCENT)

    groups = assumption_decomposition_for(facts)
    row_by_label = _label_rows(
        ws,
        (
            "New primary units",
            "Monthly price / unit",
            "Variable COGS",
            "Delivery cost / primary unit",
            "Cloud / platform cost",
            "Support cost / customer",
        ),
        max_row=62,
    )
    preview_row = 63
    for group in groups:
        preview_row += 1
        for line in group.lines:
            row_by_label[line.label] = preview_row
            preview_row += 1
        preview_row += 1

    row = 63
    for group in groups:
        _section(ws, row, group.title)
        row += 1
        for line in group.lines:
            rendered = _render_decomposition_values(line.values, cols, row_by_label)
            fmt = FMT_KEY_MAP.get(line.fmt_key, ib.FMT_MONEY)
            if line.fmt_key == "text" or line.unit == "status":
                _write_decomposition_status(ws, row, line.label, rendered, source=line.source, note=line.note)
            else:
                _write_values(ws, row, line.label, line.unit, rendered, source=line.source, note=line.note, kind=line.kind, fmt=fmt, bold=line.bold)
            row += 1
        row += 1


def _build_driver_tree(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Driver Tree"]
    _setup_sheet(ws, f"{facts.company} — Driver Tree", "The workbook is composed from economic dependencies, not category routing.")
    _set_column_widths(ws, {2: 22, 3: 44, 4: 30, 5: 42, 6: 22})
    headers = ["Layer", "Driver", "Workbook owner", "Decision relevance", "Source status"]
    for c, header in enumerate(headers, start=2):
        _apply_text_header(ws.cell(5, c), header)
    for r, surface in enumerate(driver_surfaces_for(facts), start=6):
        row = (
            surface.layer,
            surface.driver,
            surface.workbook_owner,
            surface.decision_relevance,
            surface.source_status,
        )
        for c, value in enumerate(row, start=2):
            ws.cell(r, c, value)
            ib.apply_comment(ws.cell(r, c), wrap_text=False)


def _build_revenue(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Revenue Build"]
    _setup_sheet(ws, f"{facts.company} — Revenue Build", "Driver tree: economic volume -> monetization -> total revenue.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    _section(ws, 6, "Revenue drivers")
    rows = [
        (7, "Gross merchandise value", "JPY", "='Assumptions'!{c}10", ib.FMT_MONEY),
        (8, "New primary units", "units", "='Assumptions'!{c}7", ib.FMT_INTEGER),
        (9, "Average primary units", "units", "='Assumptions'!{c}9", ib.FMT_INTEGER),
        (10, "Take rate", "%", "='Assumptions'!{c}12", ib.FMT_PERCENT),
        (11, "Monthly price / unit", "JPY", "='Assumptions'!{c}11", ib.FMT_JPY_YEN),
    ]
    for row, label, unit, formula, fmt in rows:
        _write_values(ws, row, label, unit, [formula.format(c=get_column_letter(c)) for c in cols], kind="formula", fmt=fmt)
    _section(ws, 13, "Revenue streams")
    for row, label, unit, formula in [
        (14, "Transaction revenue", "JPY", "={c}7*{c}10"),
        (15, "Recurring revenue", "JPY", "={c}9*{c}11*12"),
        (16, "One-time revenue", "JPY", "={c}8*'Assumptions'!{c}19"),
        (17, "Other revenue", "JPY", "=({c}14+{c}15+{c}16)*'Assumptions'!{c}20"),
        (18, "Total revenue", "JPY", "=SUM({c}14:{c}17)"),
        (19, "Revenue growth", "%", "=IF({prev}18=0,0,{c}18/{prev}18-1)"),
        (20, "Total customers", "count", "='Assumptions'!{c}13"),
        (21, "Revenue / customer", "JPY", "=IF({c}20=0,0,{c}18/{c}20)"),
    ]:
        vals = []
        for idx, col in enumerate(cols):
            c = get_column_letter(col)
            prev = get_column_letter(cols[idx - 1]) if idx else c
            vals.append(formula.format(c=c, prev=prev))
        fmt = ib.FMT_PERCENT if unit == "%" else ib.FMT_INTEGER if unit == "count" else ib.FMT_MONEY
        _write_values(ws, row, label, unit, vals, kind="formula", fmt=fmt, bold=row == 18)
    cats = Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=5)
    _add_bar_chart(ws, "Revenue mix", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=14, max_row=18), cats, "B27", _money_unit(facts))


def _build_cost(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Cost Build"]
    _setup_sheet(ws, f"{facts.company} — Cost Build", "Cost-to-serve, gross profit, capex, and delivery capacity.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    _section(ws, 6, "Gross profit bridge")
    rows = [
        (7, "Total revenue", "JPY", "='Revenue Build'!{c}18"),
        (8, "Variable COGS", "JPY", "={c}7*'Assumptions'!{c}24"),
        (9, "Delivery cost", "JPY", "='Revenue Build'!{c}9*'Assumptions'!{c}25*12"),
        (10, "Cloud / platform cost", "JPY", "='Revenue Build'!{c}9*'Assumptions'!{c}26*12"),
        (11, "Support cost", "JPY", "='Revenue Build'!{c}20*'Assumptions'!{c}27*12"),
        (12, "Total COGS", "JPY", "=SUM({c}8:{c}11)"),
        (13, "Gross profit", "JPY", "={c}7-{c}12"),
        (14, "Gross margin", "%", "=IF({c}7=0,0,{c}13/{c}7)"),
        (16, "CapEx", "JPY", "='Assumptions'!{c}7*'Assumptions'!{c}38+'Assumptions'!{c}40"),
        (17, "Capital intensity", "%", "=IF({c}7=0,0,{c}16/{c}7)"),
    ]
    for row, label, unit, formula in rows:
        fmt = ib.FMT_PERCENT if unit == "%" else ib.FMT_MONEY
        _write_values(ws, row, label, unit, [formula.format(c=get_column_letter(c)) for c in cols], kind="formula", fmt=fmt, bold=row in (12, 13, 16))


def _build_people(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["People Plan"]
    _setup_sheet(ws, f"{facts.company} — People Plan", "Headcount, compensation, and productivity.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Product/R&D headcount", "FTE", "='Assumptions'!{c}31", ib.FMT_INTEGER),
        (8, "GTM headcount", "FTE", "='Assumptions'!{c}32", ib.FMT_INTEGER),
        (9, "Operations/CS headcount", "FTE", "='Assumptions'!{c}33", ib.FMT_INTEGER),
        (10, "G&A headcount", "FTE", "='Assumptions'!{c}34", ib.FMT_INTEGER),
        (11, "Total headcount", "FTE", "='Assumptions'!{c}35", ib.FMT_INTEGER),
        (13, "Avg loaded comp / FTE", "JPY", "='Assumptions'!{c}36", ib.FMT_JPY_YEN),
        (14, "Total people cost", "JPY", "={c}11*{c}13", ib.FMT_MONEY),
        (15, "Revenue / FTE", "JPY", "=IF({c}11=0,0,'Revenue Build'!{c}18/{c}11)", ib.FMT_MONEY),
        (16, "Gross profit / FTE", "JPY", "=IF({c}11=0,0,'Cost Build'!{c}13/{c}11)", ib.FMT_MONEY),
    ]
    for row, label, unit, formula, fmt in rows:
        _write_values(ws, row, label, unit, [formula.format(c=get_column_letter(c)) for c in cols], kind="formula", fmt=fmt, bold=row in (11, 14))
    cats = Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=5)
    _add_bar_chart(ws, "Headcount by function", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=7, max_row=10), cats, "B22", "FTE")


def _build_pl(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["P&L"]
    _setup_sheet(ws, f"{facts.company} — Profit & Loss", f"{facts.grain.title()} P&L connected to operating and cost engines.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Total revenue", "JPY", "='Revenue Build'!{c}18"),
        (8, "Total COGS", "JPY", "='Cost Build'!{c}12"),
        (9, "Gross profit", "JPY", "='Cost Build'!{c}13"),
        (10, "Gross margin", "%", "='Cost Build'!{c}14"),
        (13, "People cost", "JPY", "='People Plan'!{c}14"),
        (14, "Sales & marketing", "JPY", "={c}7*'Assumptions'!{c}51"),
        (15, "R&D programs / pilots", "JPY", "=MAX('Assumptions'!{c}53,'People Plan'!{c}7*'Assumptions'!{c}52)"),
        (16, "G&A / systems", "JPY", "={c}7*'Assumptions'!{c}54+'Assumptions'!{c}55"),
        (17, "Total OpEx", "JPY", "=SUM({c}13:{c}16)"),
        (18, "EBITDA", "JPY", "={c}9-{c}17"),
        (19, "EBITDA margin", "%", "=IF({c}7=0,0,{c}18/{c}7)"),
        (21, "D&A", "JPY", "='Cost Build'!{c}16/'Assumptions'!{c}39*12"),
        (22, "EBIT", "JPY", "={c}18-{c}21"),
        (23, "Interest expense", "JPY", "='Capital Stack'!{c}8*'Capital Stack'!{c}9"),
        (24, "EBT", "JPY", "={c}22-{c}23"),
        (25, "Cash tax", "JPY", "=MAX(0,{c}24*'Assumptions'!{c}46)"),
        (26, "Net income", "JPY", "={c}24-{c}25"),
        (27, "Net margin", "%", "=IF({c}7=0,0,{c}26/{c}7)"),
    ]
    for row, label, unit, formula in rows:
        fmt = ib.FMT_PERCENT if unit == "%" else ib.FMT_MONEY
        _write_values(ws, row, label, unit, [formula.format(c=get_column_letter(c)) for c in cols], kind="formula", fmt=fmt, bold=row in (9, 17, 18, 22, 26))


def _build_bs(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["BS"]
    _setup_sheet(ws, f"{facts.company} — Balance Sheet", "Simplified balance sheet for cash, working capital, assets, debt, and equity.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    gross_ppe = []
    accumulated_da = []
    paid_in_capital = []
    retained_earnings = []
    for idx, col in enumerate(cols):
        c = get_column_letter(col)
        if idx == 0:
            gross_ppe.append(f"='Cost Build'!{c}16")
            accumulated_da.append(f"='P&L'!{c}21")
            paid_in_capital.append(f"='Assumptions'!{c}57+'Capital Stack'!{c}7+'Financing'!{c}7-'Financing'!{c}13")
            retained_earnings.append(f"='P&L'!{c}26")
        else:
            prior = get_column_letter(cols[idx - 1])
            gross_ppe.append(f"={prior}12+'Cost Build'!{c}16")
            accumulated_da.append(f"={prior}13+'P&L'!{c}21")
            paid_in_capital.append(f"={prior}23+'Capital Stack'!{c}7+'Financing'!{c}7-'Financing'!{c}13")
            retained_earnings.append(f"={prior}24+'P&L'!{c}26")
    rows = [
        (7, "Cash", "JPY", [f"='CF'!{get_column_letter(c)}31" for c in cols]),
        (8, "Accounts receivable", "JPY", [f"='Revenue Build'!{get_column_letter(c)}18*'Assumptions'!{get_column_letter(c)}44/365" for c in cols]),
        (9, "Inventory / WIP", "JPY", [f"='Cost Build'!{get_column_letter(c)}16*'Assumptions'!{get_column_letter(c)}56" for c in cols]),
        (10, "Total current assets", "JPY", [f"=SUM({get_column_letter(c)}7:{get_column_letter(c)}9)" for c in cols]),
        (12, "Gross PP&E", "JPY", gross_ppe),
        (13, "Accumulated D&A", "JPY", accumulated_da),
        (14, "Net PP&E", "JPY", [f"={get_column_letter(c)}12-{get_column_letter(c)}13" for c in cols]),
        (15, "Total assets", "JPY", [f"={get_column_letter(c)}10+{get_column_letter(c)}14" for c in cols]),
        (18, "Accounts payable", "JPY", [f"='Cost Build'!{get_column_letter(c)}12*'Assumptions'!{get_column_letter(c)}45/365" for c in cols]),
        (19, "Deferred revenue / customer advances", "JPY", [f"='Revenue Build'!{get_column_letter(c)}18*'Assumptions'!{get_column_letter(c)}21+'Financing'!{get_column_letter(c)}12" for c in cols]),
        (20, "Debt balance", "JPY", [f"='Capital Stack'!{get_column_letter(c)}8" for c in cols]),
        (21, "Total liabilities", "JPY", [f"=SUM({get_column_letter(c)}18:{get_column_letter(c)}20)" for c in cols]),
        (23, "Paid-in capital", "JPY", paid_in_capital),
        (24, "Retained earnings", "JPY", retained_earnings),
        (25, "Total equity", "JPY", [f"={get_column_letter(c)}23+{get_column_letter(c)}24" for c in cols]),
        (27, "Balance check", "JPY", [f"={get_column_letter(c)}15-{get_column_letter(c)}21-{get_column_letter(c)}25" for c in cols]),
    ]
    for row, label, unit, values in rows:
        _write_values(ws, row, label, unit, values, kind="formula", fmt=ib.FMT_MONEY, bold=row in (10, 15, 21, 25, 27))
    _highlight_row(ws, 27, _start_period_col() + len(cols) - 1)


def _build_cf(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["CF"]
    _setup_sheet(ws, f"{facts.company} — Cash Flow", "Operating cash, working capital, capex, financing, and runway.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    ar_increase = []
    inventory_increase = []
    ap_deferred_increase = []
    for idx, col in enumerate(cols):
        c = get_column_letter(col)
        if idx == 0:
            ar_increase.append(f"=-'BS'!{c}8")
            inventory_increase.append(f"=-'BS'!{c}9")
            ap_deferred_increase.append(f"='BS'!{c}18+'BS'!{c}19")
        else:
            prior = get_column_letter(cols[idx - 1])
            ar_increase.append(f"='BS'!{prior}8-'BS'!{c}8")
            inventory_increase.append(f"='BS'!{prior}9-'BS'!{c}9")
            ap_deferred_increase.append(f"='BS'!{c}18+'BS'!{c}19-'BS'!{prior}18-'BS'!{prior}19")
    rows = [
        (7, "Net income", "JPY", [f"='P&L'!{get_column_letter(c)}26" for c in cols]),
        (8, "D&A", "JPY", [f"='P&L'!{get_column_letter(c)}21" for c in cols]),
        (9, "AR increase", "JPY", ar_increase),
        (10, "Inventory increase", "JPY", inventory_increase),
        (11, "AP / deferred revenue increase", "JPY", ap_deferred_increase),
        (12, "Operating cash flow", "JPY", [f"=SUM({get_column_letter(c)}7:{get_column_letter(c)}11)" for c in cols]),
        (15, "CapEx", "JPY", [f"=-'Cost Build'!{get_column_letter(c)}16" for c in cols]),
        (16, "Free cash flow", "JPY", [f"={get_column_letter(c)}12+{get_column_letter(c)}15" for c in cols]),
        (19, "Equity financing", "JPY", [f"='Capital Stack'!{get_column_letter(c)}7" for c in cols]),
        (20, "Debt financing", "JPY", [f"='Capital Stack'!{get_column_letter(c)}10+'Financing'!{get_column_letter(c)}8+'Financing'!{get_column_letter(c)}11" for c in cols]),
        (21, "Customer advances / grants", "JPY", [f"='Financing'!{get_column_letter(c)}7+'Financing'!{get_column_letter(c)}12" for c in cols]),
        (22, "Secondary liquidity", "JPY", [f"=-'Financing'!{get_column_letter(c)}13" for c in cols]),
        (23, "Net cash flow", "JPY", [f"={get_column_letter(c)}16+SUM({get_column_letter(c)}19:{get_column_letter(c)}22)" for c in cols]),
        (30, "Beginning cash", "JPY", [f"='Assumptions'!{get_column_letter(c)}47" for c in cols]),
        (31, "Ending cash", "JPY", [f"={get_column_letter(c)}30+{get_column_letter(c)}23" for c in cols]),
        (32, "Runway months", "months", [f"=IF({get_column_letter(c)}16>=0,99,MAX(0,{get_column_letter(c)}31)/ABS({get_column_letter(c)}16/12))" for c in cols]),
    ]
    for row, label, unit, values in rows:
        fmt = ib.FMT_NUM if unit == "months" else ib.FMT_MONEY
        _write_values(ws, row, label, unit, values, kind="formula", fmt=fmt, bold=row in (12, 16, 21, 31))
    cats = Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=5)
    _add_line_chart(ws, "Ending cash", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=31, max_row=31), cats, "B38", _money_unit(facts))
    _add_line_chart(ws, "Runway months", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=32, max_row=32), cats, "J38", "months")


def _build_capital_stack(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Capital Stack"]
    _setup_sheet(ws, f"{facts.company} — Capital Stack", "Cash sources, runway, debt capacity, and round ownership.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    debt_balance = []
    for idx, col in enumerate(cols):
        c = get_column_letter(col)
        debt_inflow = f"{c}10+'Financing'!{c}8+'Financing'!{c}11"
        if idx == 0:
            debt_balance.append(f"={debt_inflow}")
        else:
            prior = get_column_letter(cols[idx - 1])
            debt_balance.append(f"={prior}8+{debt_inflow}")
    rows = [
        (7, "Equity financing", "JPY", facts.equity_raise_yen, "funding plan", "input", ib.FMT_MONEY),
        (8, "Debt balance", "JPY", debt_balance, "debt / lease / convert roll-forward", "formula", ib.FMT_MONEY),
        (9, "Debt interest rate", "%", facts.debt_interest_rate, "debt terms", "input", ib.FMT_PERCENT),
        (10, "Debt financing", "JPY", facts.debt_raise_yen, "debt / lease capacity", "input", ib.FMT_MONEY),
        (12, "Ending cash", "JPY", [f"='CF'!{get_column_letter(c)}31" for c in cols], "cash roll-forward", "formula", ib.FMT_MONEY),
        (13, "Runway", "months", [f"='CF'!{get_column_letter(c)}32" for c in cols], "cash runway", "formula", ib.FMT_NUM),
        (15, "Illustrative post-money", "JPY", facts.post_money_yen, "round strategy", "input", ib.FMT_MONEY),
        (16, "New investor ownership", "%", [f"=IF({get_column_letter(c)}15=0,0,{get_column_letter(c)}7/{get_column_letter(c)}15)" for c in cols], "dilution", "formula", ib.FMT_PERCENT),
        (17, "Debt / revenue", "%", [f"=IF('Revenue Build'!{get_column_letter(c)}18=0,0,{get_column_letter(c)}8/'Revenue Build'!{get_column_letter(c)}18)" for c in cols], "leverage", "formula", ib.FMT_PERCENT),
    ]
    for row, label, unit, values, source, kind, fmt in rows:
        _write_values(ws, row, label, unit, values, source=source, kind=kind, fmt=fmt, bold=row in (7, 12, 13, 16))


def _ownership_rollforward_values(period_cols: list[int], row: int, initial_value: float, inflow_row: int | None = None) -> list[object]:
    values: list[object] = [initial_value]
    for prior_col, current_col in zip(period_cols[:-1], period_cols[1:]):
        prior = get_column_letter(prior_col)
        current = get_column_letter(current_col)
        formula = f"={prior}{row}*(1-{current}12-{current}13-{current}14)"
        if inflow_row is not None:
            formula += f"+{current}{inflow_row}"
        values.append(formula)
    return values


def _build_ownership(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Ownership"]
    _setup_sheet(ws, f"{facts.company} — Ownership Waterfall", "Founder, employee, investor, debt warrant, and secondary-style dilution.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Founder ownership", "%", _ownership_rollforward_values(cols, 7, facts.founder_ownership), "cap table assumption", "input", ib.FMT_PERCENT),
        (8, "Employee / option pool", "%", _ownership_rollforward_values(cols, 8, facts.option_pool, 13), "talent plan", "input", ib.FMT_PERCENT),
        (9, "Existing investors", "%", _ownership_rollforward_values(cols, 9, facts.existing_investors, 12), "existing + new rounds", "input", ib.FMT_PERCENT),
        (10, "Debt warrant / strategic", "%", _ownership_rollforward_values(cols, 10, facts.strategic_warrant, 14), "debt / partner terms", "input", ib.FMT_PERCENT),
        (12, "New investor ownership", "%", [f"='Capital Stack'!{get_column_letter(c)}16" for c in cols], "round ownership", "formula", ib.FMT_PERCENT),
        (13, "Option pool refresh", "%", facts.option_pool_refresh, "hiring needs", "input", ib.FMT_PERCENT),
        (14, "Secondary / warrant dilution", "%", facts.secondary_warrant_dilution, "liquidity / debt", "input", ib.FMT_PERCENT),
        (16, "Ownership check", "%", [f"=SUM({get_column_letter(c)}7:{get_column_letter(c)}10)" for c in cols], "should approach 100%", "formula", ib.FMT_PERCENT),
    ]
    for row, label, unit, values, source, kind, fmt in rows:
        _write_values(ws, row, label, unit, values, source=source, kind=kind, fmt=fmt, bold=row == 16)
    _highlight_row(ws, 16, _start_period_col() + len(cols) - 1)


def _build_pricing(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Pricing"]
    _setup_sheet(ws, f"{facts.company} — Pricing and ROI", "Price, customer ROI, cost-to-serve, sales cycle, and willingness-to-pay checks.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Monthly price / unit", "JPY", [f"='Assumptions'!{get_column_letter(c)}11" for c in cols], "pricing anchor", "formula", ib.FMT_JPY_YEN),
        (8, "Customer ROI / year", "JPY", [facts.customer_roi_yen for _ in cols], "customer value estimate", "input", ib.FMT_MONEY),
        (9, "Implementation cost / customer", "JPY", [facts.implementation_cost_yen for _ in cols], "deployment burden", "input", ib.FMT_JPY_YEN),
        (10, "Monthly unit cost", "JPY", [f"=('Assumptions'!{get_column_letter(c)}25+'Assumptions'!{get_column_letter(c)}26+'Assumptions'!{get_column_letter(c)}27)" for c in cols], "cost-to-serve", "formula", ib.FMT_JPY_YEN),
        (11, "Gross margin", "%", [f"=IF({get_column_letter(c)}7=0,0,({get_column_letter(c)}7-{get_column_letter(c)}10)/{get_column_letter(c)}7)" for c in cols], "unit margin", "formula", ib.FMT_PERCENT),
        (12, "Customer payback", "months", [f"=IF({get_column_letter(c)}8=0,99,{get_column_letter(c)}9/({get_column_letter(c)}8/12))" for c in cols], "customer ROI", "formula", ib.FMT_NUM),
        (13, "Sales cycle", "months", [facts.sales_cycle_months for _ in cols], "commercial motion", "input", ib.FMT_NUM),
        (14, "Churn / non-renewal risk", "%", [facts.churn_rate for _ in cols], "cohort risk", "input", ib.FMT_PERCENT),
        (15, "Repeat / expansion rate", "%", [facts.repeat_rate for _ in cols], "cohort behavior", "input", ib.FMT_PERCENT),
        (16, "Suggested floor price", "JPY", [f"={get_column_letter(c)}10/(1-MAX(0.01,{get_column_letter(c)}11))" for c in cols], "cost-plus guardrail", "formula", ib.FMT_JPY_YEN),
        (17, "Suggested value price", "JPY", [f"={get_column_letter(c)}8/12*0.25" for c in cols], "ROI share", "formula", ib.FMT_JPY_YEN),
        (18, "Selected price support ratio", "x", [f"=IF({get_column_letter(c)}7=0,0,{get_column_letter(c)}17/{get_column_letter(c)}7)" for c in cols], "willingness-to-pay headroom", "formula", ib.FMT_MULTIPLE),
        (19, "Gross-profit payback", "months", [f"=IF(({get_column_letter(c)}7-{get_column_letter(c)}10)<=0,\"N/A\",{get_column_letter(c)}9/({get_column_letter(c)}7-{get_column_letter(c)}10))" for c in cols], "deployment recovery", "formula", ib.FMT_NUM),
        (20, "Validation hurdle", "x", [1.5 for _ in cols], "minimum WTP / selected price", "input", ib.FMT_MULTIPLE),
        (21, "Pricing IC gate", "pass / fail", [f"=IF(AND({get_column_letter(c)}18>={get_column_letter(c)}20,{get_column_letter(c)}11>=0.5,{get_column_letter(c)}19<=12),\"pass\",\"DD gate\")" for c in cols], "pricing decision gate", "formula", "General"),
    ]
    for row, label, unit, values, source, kind, fmt in rows:
        _write_values(ws, row, label, unit, values, source=source, kind=kind, fmt=fmt, bold=row in (7, 16, 17, 21))
    _highlight_row(ws, 21, _start_period_col() + len(cols) - 1)
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 34, start_col + 1: 28, start_col + 2: 18, start_col + 3: 32, start_col + 4: 68})
    _section(ws, 24, "Pricing validation plan", start_col + 4)
    headers = ["Test", "Evidence required", "Pass threshold", "Owner / source", "IC implication"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(25, col), header)
    validation_rows = [
        ("WTP interview / LOI", "named buyer pain, budget owner, procurement trigger", "support ratio >= 1.5x", "customer discovery / pipeline", "price can anchor value share"),
        ("Pilot conversion", "paid pilot or signed deployment scope", "gross-profit payback <= 12 months", "sales pipeline / contract", "implementation burden is financeable"),
        ("Packaging ladder", "entry, core, expansion, enterprise SKUs", "no cliff in expansion path", "pricing owner", "avoid under-monetizing high-ROI accounts"),
        ("Renewal risk", "cohort churn or renewal intent by segment", "churn below downside case", "CS / cohort export", "discount valuation if renewal evidence is weak"),
    ]
    for row, values in enumerate(validation_rows, start=26):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)


def _build_financing(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Financing"]
    _setup_sheet(ws, f"{facts.company} — Financing Instruments", "Equity, grants, converts, leases, customer advances, secondary, and runway pressure.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Grants / subsidies", "JPY", facts.grants_yen, "non-dilutive funding", "input", ib.FMT_MONEY),
        (8, "Convertible instruments", "JPY", facts.convertibles_yen, "SAFE / J-KISS / note", "input", ib.FMT_MONEY),
        (9, "Primary equity", "JPY", [f"='Capital Stack'!{get_column_letter(c)}7" for c in cols], "priced equity", "formula", ib.FMT_MONEY),
        (10, "Venture debt", "JPY", [f"='Capital Stack'!{get_column_letter(c)}10" for c in cols], "debt draw", "formula", ib.FMT_MONEY),
        (11, "Lease financing", "JPY", facts.lease_financing_yen, "asset financing", "input", ib.FMT_MONEY),
        (12, "Customer advances", "JPY", facts.customer_advances_yen, "working-capital offset", "input", ib.FMT_MONEY),
        (13, "Founder / investor secondary", "JPY", facts.secondary_yen, "liquidity use", "input", ib.FMT_MONEY),
        (15, "Financing cash inflow", "JPY", [f"=SUM({get_column_letter(c)}7:{get_column_letter(c)}12)-{get_column_letter(c)}13" for c in cols], "cash inflow", "formula", ib.FMT_MONEY),
        (16, "Downside funding gap", "JPY", [f"='Scenarios'!{get_column_letter(_start_period_col())}19" for _ in cols], "scenario pressure", "formula", ib.FMT_MONEY),
        (17, "NOL balance", "JPY", facts.nol_yen, "tax shield", "input", ib.FMT_MONEY),
    ]
    for row, label, unit, values, source, kind, fmt in rows:
        _write_values(ws, row, label, unit, values, source=source, kind=kind, fmt=fmt, bold=row in (15, 16))
    _highlight_row(ws, 16, _start_period_col() + len(cols) - 1)


def _build_exit_waterfall(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Exit Waterfall"]
    _setup_sheet(ws, f"{facts.company} — Exit Waterfall", "M&A / IPO proceeds, deal leakage, preference floor, and buyer-view value bridge.")
    _set_column_widths(ws, {2: 18, 3: 16, 4: 16, 5: 16, 6: 16, 7: 16, 8: 16, 9: 16, 10: 18, 11: 12, 12: 18, 13: 22})
    headers = [
        "Case", "Exit EV", "Net debt", "Txn costs / escrow", "Equity value",
        "Preference floor", "Common pool", "New investor ownership",
        "Investor proceeds", "MOIC", "Founder proceeds", "Walk-away signal",
    ]
    for col, header in enumerate(headers, start=2):
        _apply_text_header(ws.cell(5, col), header)
    cases = [
        ("Downside", f"='Scenarios'!{get_column_letter(_start_period_col())}18"),
        ("Base", f"='Valuation'!{_final_period_col(facts)}26"),
        ("Upside", f"='Scenarios'!{get_column_letter(_start_period_col() + 2)}18"),
    ]
    for row, (label, exit_ev) in enumerate(cases, start=6):
        ws.cell(row, 2, label)
        ws.cell(row, 3, exit_ev)
        ws.cell(row, 4, f"='Capital Stack'!{_final_period_col(facts)}8-'Capital Stack'!{_final_period_col(facts)}12")
        ws.cell(row, 5, f"=MAX(0,C{row}*3%)")
        ws.cell(row, 6, f"=MAX(0,C{row}-D{row}-E{row})")
        ws.cell(row, 7, f"=MAX('Capital Stack'!{_final_period_col(facts)}7,0)")
        ws.cell(row, 8, f"=MAX(0,F{row}-G{row})")
        ws.cell(row, 9, f"='Ownership'!{_final_period_col(facts)}9")
        ws.cell(row, 10, f"=MIN(F{row},G{row})+H{row}*I{row}")
        ws.cell(row, 11, f"=IF('Valuation'!{_final_period_col(facts)}31=\"-\",\"-\",J{row}/MAX(1,'Valuation'!{_final_period_col(facts)}29))")
        ws.cell(row, 12, f"=H{row}*'Ownership'!{_final_period_col(facts)}7")
        ws.cell(row, 13, f"=IF(OR(K{row}=\"-\",K{row}<2),\"reprice / reject\",IF(L{row}<J{row},\"terms protect investor\",\"committee case\"))")
        for col in range(2, 14):
            cell = ws.cell(row, col)
            if col == 2:
                ib.apply_label(cell, bold=col == 2)
                continue
            fmt = "General" if col == 13 else ib.FMT_PERCENT if col == 9 else ib.FMT_MULTIPLE if col == 11 else _money_format(facts)
            _apply_value_style(cell, fmt)
        if label == "Base":
            _highlight_row(ws, row, 13)
    _section(ws, 12, "Buyer-view M&A bridge", 12)
    bridge_headers = ["Bridge item", "Treatment", "Evidence required", "Risk to value"]
    for col, header in enumerate(bridge_headers, start=LAYOUT.label_col):
        _apply_text_header(ws.cell(13, col), header)
    bridge_rows = [
        ("Control premium / synergy", "do not add unless buyer-specific", "named buyer logic or comparable transaction", "unsupported premium inflates EV"),
        ("Debt-like items / NWC peg", "deduct before common proceeds", "debt schedule, leases, working-capital target", "equity value leakage"),
        ("Escrow / earnout / rollover", "separate certain from contingent proceeds", "SPA terms or precedent range", "MOIC timing and certainty"),
        ("Retention / transaction fees", "deduct from equity bridge", "advisor, legal, retention, tax estimate", "founder and investor proceeds overstatement"),
    ]
    for row, values in enumerate(bridge_rows, start=14):
        for col, value in enumerate(values, start=LAYOUT.label_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)


def _build_segments(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Segments"]
    _setup_sheet(ws, f"{facts.company} — Segment Lens", "Segment revenue, margin, capital intensity, and SOTP support.")
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 58, start_col + 1: 16, start_col + 2: 16, start_col + 3: 16, start_col + 4: 18, start_col + 5: 18, start_col + 6: 24, start_col + 7: 58})
    headers = ["Segment", "Revenue share", "Segment revenue", "Gross margin", "EBITDA proxy", "Segment multiple", "Segment EV", "Source status", "Decision implication"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(5, col), header)
    segment_count = max(len(facts.segments), 1)
    for idx, segment in enumerate(facts.segments, start=6):
        share = 1 / segment_count
        share_col = get_column_letter(start_col + 1)
        revenue_col = get_column_letter(start_col + 2)
        gp_col = get_column_letter(start_col + 3)
        ebitda_col = get_column_letter(start_col + 4)
        multiple_col = get_column_letter(start_col + 5)
        row = [
            segment,
            share,
            f"='Revenue Build'!{_final_period_col(facts)}18*{share_col}{idx}",
            f"='KPI'!{_final_period_col(facts)}16",
            f"='KPI'!{_final_period_col(facts)}17",
            f"='Valuation'!{get_column_letter(_start_period_col())}13*(1+{ebitda_col}{idx})",
            f"=MAX(0,{revenue_col}{idx}*{multiple_col}{idx})",
            "source / assumption",
            "Use distinct segment evidence before relying on SOTP as a primary method.",
        ]
        for col, value in enumerate(row, start=start_col):
            ws.cell(idx, col, value)
            if col == start_col + 1:
                ib.apply_hard_input(ws.cell(idx, col), ib.FMT_PERCENT)
            elif col in (start_col + 3, start_col + 4):
                _apply_value_style(ws.cell(idx, col), ib.FMT_PERCENT)
            elif col in (start_col + 2, start_col + 6):
                _apply_value_style(ws.cell(idx, col), _money_format(facts))
            elif col == start_col + 5:
                _apply_value_style(ws.cell(idx, col), ib.FMT_MULTIPLE)
            else:
                ib.apply_comment(ws.cell(idx, col), wrap_text=False)


def _build_kpi(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["KPI"]
    _setup_sheet(ws, f"{facts.company} — KPI Dashboard", "Decision metrics: scale, margin, runway, capital efficiency, ownership, and valuation.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    rows = [
        (7, "Monthly price / unit", "JPY", "='Assumptions'!{c}11", ib.FMT_JPY_YEN),
        (8, "Monthly unit cost", "JPY", "=('Assumptions'!{c}25+'Assumptions'!{c}26+'Assumptions'!{c}27)", ib.FMT_JPY_YEN),
        (9, "Monthly unit gross profit", "JPY", "={c}7-{c}8", ib.FMT_JPY_YEN),
        (10, "Unit gross margin", "%", "=IF({c}7=0,0,{c}9/{c}7)", ib.FMT_PERCENT),
        (11, "Unit payback", "months", "=IF({c}9<=0,\"N/A\",'Assumptions'!{c}38/{c}9)", ib.FMT_NUM),
        (13, "Ending primary units", "units", "='Assumptions'!{c}8", ib.FMT_INTEGER),
        (14, "GMV / economic volume", "JPY", "='Assumptions'!{c}10", ib.FMT_MONEY),
        (15, "Revenue", "JPY", "='Revenue Build'!{c}18", ib.FMT_MONEY),
        (16, "Gross margin", "%", "='P&L'!{c}10", ib.FMT_PERCENT),
        (17, "EBITDA margin", "%", "='P&L'!{c}19", ib.FMT_PERCENT),
        (18, "Burn multiple", "x", "=IF({c}15=0,0,ABS('CF'!{c}16)/MAX(1,{c}15-{prev}15))", ib.FMT_MULTIPLE),
        (19, "Revenue / FTE", "JPY", "='People Plan'!{c}15", ib.FMT_MONEY),
        (20, "Runway", "months", "='CF'!{c}32", ib.FMT_NUM),
        (21, "New investor ownership", "%", "='Capital Stack'!{c}16", ib.FMT_PERCENT),
        (22, "Founder ownership", "%", "='Ownership'!{c}7", ib.FMT_PERCENT),
    ]
    for row, label, unit, formula, fmt in rows:
        vals = []
        for idx, col in enumerate(cols):
            c = get_column_letter(col)
            prev = get_column_letter(cols[idx - 1]) if idx else c
            vals.append(formula.format(c=c, prev=prev))
        _write_values(ws, row, label, unit, vals, kind="formula", fmt=fmt, bold=row in (13, 15, 20))
    cats = Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=5)
    _add_line_chart(ws, "Operating scale", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=13, max_row=13), cats, "B28", "units")
    _add_line_chart(ws, "Economic value", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=14, max_row=15), cats, "J28", _money_unit(facts))
    _add_line_chart(ws, "Margin and ownership", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=16, max_row=22), cats, "B44", "%")
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 24, start_col + 1: 42, start_col + 2: 36, start_col + 3: 38, start_col + 4: 40, start_col + 5: 48})
    _section(ws, 62, "KPI interpretation register", start_col + 5)
    headers = ["KPI", "Formula / driver", "Applies when", "Source context", "Downside trigger", "IC implication"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(63, col), header)
    interpretation_rows = [
        (
            item.name,
            item.formula_driver,
            item.applies_when,
            item.source_context,
            item.downside_trigger,
            item.ic_implication,
        )
        for item in kpi_definitions_for(facts)
    ]
    for row, values in enumerate(interpretation_rows, start=64):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)


def _build_scenarios(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Scenarios"]
    _setup_sheet(ws, f"{facts.company} — Scenario Engine", "Downside / base / upside cases expressed as coherent driver sets.")
    scenario_cols = list(range(_start_period_col(), _start_period_col() + 3))
    for col, label in zip(scenario_cols, ["Downside", "Base", "Upside"]):
        ws.cell(5, col, label)
        ib.apply_year_header(ws.cell(5, col), label)
    _section(ws, 6, "Driver settings")
    drivers = scenario_drivers_for(facts)
    for r, driver in enumerate(drivers, start=7):
        label, unit, down, base, up = driver.label, driver.unit, driver.downside, driver.base, driver.upside
        _label(ws, r, label, unit)
        for col, value in zip(scenario_cols, [down, base, up]):
            ws.cell(r, col, value)
            ib.apply_hard_input(ws.cell(r, col), ib.FMT_MULTIPLE)
    _section(ws, 13, f"{facts.period_labels[-1]} output")
    outputs = [
        ("Revenue", "JPY"),
        ("Gross profit", "JPY"),
        ("EBITDA", "JPY"),
        ("Ending cash", "JPY"),
        ("Exit EV", "JPY"),
        ("Funding gap", "JPY"),
        ("Founder ownership", "%"),
    ]
    for r, (label, unit) in enumerate(outputs, start=14):
        _label(ws, r, label, unit, fmt=ib.FMT_PERCENT if unit == "%" else ib.FMT_MONEY)
        for col in scenario_cols:
            c = get_column_letter(col)
            ws.cell(r, col, _scenario_output_formula(facts, label, c, drivers))
            _apply_value_style(ws.cell(r, col), ib.FMT_PERCENT if unit == "%" else _money_format(facts))
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 24, start_col + 1: 40, start_col + 2: 98, start_col + 3: 46, start_col + 4: 64})
    _section(ws, 23, "Scenario interpretation", start_col + 4)
    headers = ["Case", "Cause", "Linked driver changes", "Breakpoint", "DD action"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(24, col), header)
    driver_summary = "; ".join(driver.label for driver in drivers[:4])
    scenario_notes = [
        ("Downside", drivers[0].why, driver_summary, drivers[0].breakpoint, drivers[0].decision_implication),
        ("Base", "selected operating plan", "selected assumptions reconcile to support checks", "support ratios stay credible", "refresh stale sources before circulation"),
        ("Upside", drivers[-1].why, driver_summary, drivers[-1].breakpoint, drivers[-1].decision_implication),
    ]
    for row, values in enumerate(scenario_notes, start=25):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)
    _add_bar_chart(ws, "Scenario EBITDA", Reference(ws, min_col=scenario_cols[0], max_col=scenario_cols[-1], min_row=16, max_row=16), Reference(ws, min_col=scenario_cols[0], max_col=scenario_cols[-1], min_row=5), "B33", _money_unit(facts))


def _scenario_driver_bucket(driver: ScenarioDriver) -> str:
    label = driver.label.lower()
    if any(token in label for token in ("financing", "debt", "lease", "grant", "warehouse", "working-capital")):
        return "financing"
    if any(token in label for token in ("cost", "loss", "incentive", "bom", "service", "prototype", "program")):
        return "cost"
    if any(token in label for token in ("cac", "sales capacity", "hiring", "headcount", "fte", "talent")):
        return "opex"
    if any(token in label for token in ("demand", "gmv", "liquidity", "take-rate", "pricing", "value capture", "utilization", "origination", "spread", "new logo", "conversion", "acv", "expansion", "retention", "churn", "deployment capacity")):
        return "revenue"
    return "opex"


def _scenario_driver_formula_terms(col: str, drivers: tuple[ScenarioDriver, ...]) -> tuple[str, str, str, str]:
    revenue_rows: list[str] = []
    cost_rows: list[str] = []
    opex_rows: list[str] = []
    financing_rows: list[str] = []
    for offset, driver in enumerate(drivers[:4], start=7):
        row_ref = f"{col}${offset}"
        bucket = _scenario_driver_bucket(driver)
        if bucket == "cost":
            cost_rows.append(row_ref)
        elif bucket == "opex":
            opex_rows.append(row_ref)
        elif bucket == "financing":
            financing_rows.append(row_ref)
        elif bucket == "revenue":
            revenue_rows.append(row_ref)
        else:
            opex_rows.append(row_ref)
    return (
        "*".join(revenue_rows) if revenue_rows else "1",
        "*".join(cost_rows) if cost_rows else "1",
        "*".join(opex_rows) if opex_rows else "1",
        "*".join(financing_rows) if financing_rows else "1",
    )


def _scenario_output_formula(facts: SourceFacts, label: str, col: str, drivers: tuple[ScenarioDriver, ...]) -> str:
    final_col = _final_period_col(facts)
    revenue_factor, cost_factor, opex_factor, financing_factor = _scenario_driver_formula_terms(col, drivers)
    formulas = {
        "Revenue": f"='Revenue Build'!{final_col}18*{revenue_factor}",
        "Gross profit": f"={col}14-('Cost Build'!{final_col}12*{cost_factor})",
        "EBITDA": f"={col}15-('P&L'!{final_col}17*{opex_factor})",
        "Ending cash": f"='CF'!{final_col}31+{col}16-'P&L'!{final_col}18",
        "Exit EV": f"=MAX(0,{col}16*'Valuation'!{final_col}15)",
        "Funding gap": f"=MAX(0,-{col}17/MAX(0.01,{financing_factor}))",
        "Founder ownership": f"='Ownership'!{final_col}7/({col}$7^0.15)",
    }
    return formulas[label]


def _build_sensitivity(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Sensitivity"]
    _setup_sheet(ws, f"{facts.company} — Sensitivity", "Two-variable sensitivity around the decision-critical drivers.")
    _set_column_widths(ws, {_start_period_col() - 1: LAYOUT.period_width})
    final_col = _final_period_col(facts)
    drivers = scenario_drivers_for(facts)
    x_axis = drivers[0]
    y_axis = drivers[1]
    _section(ws, 5, f"{facts.period_labels[-1]} EBITDA — {x_axis.label} x {y_axis.label}")
    scales = [0.60, 0.80, 1.00, 1.20, 1.40]
    prices = [0.80, 0.90, 1.00, 1.10, 1.20]
    matrix_cols = list(range(_start_period_col(), _start_period_col() + len(scales)))
    row_axis_col = get_column_letter(_start_period_col() - 1)
    _label(ws, 7, x_axis.label, x_axis.unit)
    _label(ws, 8, y_axis.label, y_axis.unit)
    x_bucket = _scenario_driver_bucket(x_axis)
    y_bucket = _scenario_driver_bucket(y_axis)
    for idx, scale in zip(matrix_cols, scales):
        ws.cell(7, idx, scale)
        ib.apply_hard_input(ws.cell(7, idx), ib.FMT_MULTIPLE)
    for r, price in enumerate(prices, start=8):
        ws.cell(r, _start_period_col() - 1, price)
        ib.apply_hard_input(ws.cell(r, _start_period_col() - 1), ib.FMT_MULTIPLE)
        for c in matrix_cols:
            col = get_column_letter(c)
            revenue_term = "1"
            cost_term = "1"
            opex_term = "1"
            if x_bucket == "cost":
                cost_term = f"{col}$7"
            elif x_bucket == "opex":
                opex_term = f"{col}$7"
            elif x_bucket == "revenue":
                revenue_term = f"{col}$7"
            if y_bucket == "cost":
                cost_term = f"{cost_term}*${row_axis_col}{r}"
            elif y_bucket == "opex":
                opex_term = f"{opex_term}*${row_axis_col}{r}"
            elif y_bucket == "revenue":
                revenue_term = f"{revenue_term}*${row_axis_col}{r}"
            ws.cell(r, c, f"=('Revenue Build'!{final_col}18*{revenue_term})-('Cost Build'!{final_col}12*{cost_term})-('P&L'!{final_col}17*{opex_term})")
            _apply_value_style(ws.cell(r, c), _money_format(facts))
    ib.apply_heatmap_3color(ws, f"{get_column_letter(matrix_cols[0])}8:{get_column_letter(matrix_cols[-1])}12")
    _section(ws, 15, "Founder ownership — valuation x round size")
    values = [0.70, 0.85, 1.00, 1.20, 1.45]
    rounds = [0.75, 0.90, 1.00, 1.15, 1.35]
    _label(ws, 17, "Valuation scale", "x")
    _label(ws, 18, "Round size scale", "x")
    for idx, value in zip(matrix_cols, values):
        ws.cell(17, idx, value)
        ib.apply_hard_input(ws.cell(17, idx), ib.FMT_MULTIPLE)
    for r, round_size in enumerate(rounds, start=18):
        ws.cell(r, _start_period_col() - 1, round_size)
        ib.apply_hard_input(ws.cell(r, _start_period_col() - 1), ib.FMT_MULTIPLE)
        for c in matrix_cols:
            col = get_column_letter(c)
            ws.cell(r, c, f"='Ownership'!{final_col}7*(1-('Capital Stack'!{final_col}7*${row_axis_col}{r})/('Capital Stack'!{final_col}15*{col}$17))")
            _apply_value_style(ws.cell(r, c), ib.FMT_PERCENT)
    ib.apply_heatmap_3color(ws, f"{get_column_letter(matrix_cols[0])}18:{get_column_letter(matrix_cols[-1])}22")
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 24, start_col + 1: 100, start_col + 2: 34, start_col + 3: 34, start_col + 4: 64})
    _section(ws, 25, "Sensitivity rationale", start_col + 4)
    headers = ["Matrix", "Why selected", "Output pressured", "Breakpoint", "Decision implication"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(26, col), header)
    rationale_rows = [
        ("Operating economics", f"selected from weak-evidence drivers: {x_axis.label} and {y_axis.label}", "EBITDA and cash capacity", "EBITDA or runway turns negative", "pricing, cost, or growth plan must change"),
        ("Financing terms", "use when dilution is decision-critical", "founder ownership and investor return", "ownership falls below tolerance", "round size, valuation, or instrument mix must change"),
    ]
    for row, values in enumerate(rationale_rows, start=27):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)


def _build_valuation(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Valuation"]
    _setup_sheet(ws, f"{facts.company} — Valuation", "Valuation committee view: method supportability, SOTP, selected range, and investor return logic.")
    _write_period_header(ws, facts)
    cols = _period_cols(facts)
    final_col = _final_period_col(facts)
    _section(ws, 6, "Operating basis")
    rows = [
        (7, f"{facts.period_labels[-1]} revenue", "JPY", f"='Revenue Build'!{final_col}18"),
        (8, f"{facts.period_labels[-1]} gross profit", "JPY", f"='Cost Build'!{final_col}13"),
        (9, f"{facts.period_labels[-1]} EBITDA", "JPY", f"='P&L'!{final_col}18"),
        (10, "Discount rate", "%", facts.discount_rate),
        (11, "Terminal growth", "%", facts.terminal_growth_rate),
    ]
    for row, label, unit, formula in rows:
        _label(ws, row, label, unit, fmt=ib.FMT_PERCENT if unit == "%" else ib.FMT_MONEY)
        ws.cell(row, _start_period_col(), formula)
        if isinstance(formula, str) and formula.startswith("="):
            _apply_value_style(ws.cell(row, _start_period_col()), _money_format(facts))
        else:
            ib.apply_hard_input(ws.cell(row, _start_period_col()), ib.FMT_PERCENT)
    _section(ws, 12, "Multiple range")
    live_comps = [comp for comp in (getattr(facts, "live_comps", []) or []) if isinstance(comp, dict)]
    usable_statuses = {"current", "provided"}
    has_comparable_revenue_multiple = any(comp.get("status") in usable_statuses and comp.get("revenue_multiple") for comp in live_comps)
    has_comparable_ebitda_multiple = any(comp.get("status") in usable_statuses and comp.get("ebitda_multiple") for comp in live_comps)
    revenue_source = "comparable evidence" if has_comparable_revenue_multiple else "benchmark / refresh required"
    ebitda_source = "comparable evidence" if has_comparable_ebitda_multiple else "benchmark / refresh required"
    gp_source = "derived proxy / refresh required"
    _write_values(ws, 13, "Revenue multiple", "x", facts.revenue_multiple, source=revenue_source, fmt=ib.FMT_MULTIPLE)
    _write_values(ws, 14, "Gross profit multiple", "x", facts.gross_profit_multiple, source=gp_source, fmt=ib.FMT_MULTIPLE)
    _write_values(ws, 15, "EBITDA multiple", "x", facts.ebitda_multiple, source=ebitda_source, fmt=ib.FMT_MULTIPLE)
    basis_col = get_column_letter(_start_period_col())
    _write_values(ws, 16, "Revenue-implied EV", "JPY", [f"=${basis_col}$7*{get_column_letter(c)}13" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 17, "GP-implied EV", "JPY", [f"=${basis_col}$8*{get_column_letter(c)}14" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 18, "EBITDA-implied EV", "JPY", [f"=${basis_col}$9*{get_column_letter(c)}15" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 19, "Primary-method EV", "JPY", [f"=IF(${basis_col}$9>0,{get_column_letter(c)}18,IF(${basis_col}$8>0,{get_column_letter(c)}17,{get_column_letter(c)}16))" for c in cols], kind="formula", fmt=ib.FMT_MONEY, bold=True)
    pv_forecast = []
    pv_terminal = []
    for idx, col in enumerate(cols, start=1):
        terms = [f"'CF'!{get_column_letter(c)}16/(1+${basis_col}$10)^{offset}" for offset, c in enumerate(cols[:idx], start=1)]
        pv_forecast.append(f"=MAX(0,SUM({','.join(terms)}))")
        pv_terminal.append(f"=MAX(0,'CF'!{get_column_letter(col)}16*(1+${basis_col}$11)/MAX(0.01,${basis_col}$10-${basis_col}$11)/(1+${basis_col}$10)^{idx})")
    _write_values(ws, 20, "PV of forecast FCF", "JPY", pv_forecast, kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 21, "PV of terminal value", "JPY", pv_terminal, kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 22, "DCF EV", "JPY", [f"={get_column_letter(c)}20+{get_column_letter(c)}21" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    segment_last_row = 5 + max(len(facts.segments), 1)
    segment_ev_col = get_column_letter(LAYOUT.label_col + 6)
    _write_values(ws, 23, "SOTP EV", "JPY", [f"=SUM('Segments'!${segment_ev_col}$6:${segment_ev_col}${segment_last_row})" for _ in cols], kind="formula", fmt=ib.FMT_MONEY)
    benchmark_freshness_cell = f"'Benchmarks'!${get_column_letter(BENCHMARK_FRESHNESS_COL)}${BENCHMARK_VALUATION_SUPPORT_ROW}"
    _write_values(ws, 24, "Supportability score", "x", [f"=MIN(1.5,MAX(0.5,0.35+IF({get_column_letter(c)}16>0,0.25,0)+IF({get_column_letter(c)}22>0,0.20,0)+IF({get_column_letter(c)}23>0,0.20,0)+IF({benchmark_freshness_cell}=\"current\",0.20,0)))" for c in cols], kind="formula", fmt=ib.FMT_MULTIPLE)
    _write_values(ws, 25, "Selected EV low", "JPY", [f"=MAX(0,MIN({get_column_letter(c)}19,{get_column_letter(c)}22,{get_column_letter(c)}23)*0.9)" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 26, "Selected EV midpoint", "JPY", [f"=IF({get_column_letter(c)}24<0.9,MEDIAN({get_column_letter(c)}19,{get_column_letter(c)}22,{get_column_letter(c)}23)*0.85,MEDIAN({get_column_letter(c)}19,{get_column_letter(c)}22,{get_column_letter(c)}23))" for c in cols], kind="formula", fmt=ib.FMT_MONEY, bold=True)
    _write_values(ws, 27, "Selected EV high", "JPY", [f"=MAX({get_column_letter(c)}19,{get_column_letter(c)}22,{get_column_letter(c)}23)*IF({get_column_letter(c)}24>=1,1.1,1.0)" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _highlight_row(ws, 26, _start_period_col() + len(cols) - 1)
    start_col = LAYOUT.label_col
    _set_column_widths(ws, {start_col: 24, start_col + 1: 42, start_col + 2: 34, start_col + 3: 42, start_col + 4: 26})
    _section(ws, 35, "Method credibility", start_col + 4)
    headers = ["Method", "Role", "Use when", "Exclusion / caution", "Linked driver"]
    for col, header in enumerate(headers, start=start_col):
        _apply_text_header(ws.cell(36, col), header)
    method_rows = [
        ("Revenue multiple", "primary if revenue quality is central", "recurring or high-quality growth", "weak margin or non-recurring revenue", "growth / retention"),
        ("GP multiple", "support if cost-to-serve matters", "gross margin is well-defined", "COGS definition is unstable", "gross margin"),
        ("EBITDA multiple", "primary if profitability is visible", "profitability is credible", "growth investment distorts EBITDA", "EBITDA margin"),
        ("DCF", "support or cross-check", "cash flows are explainable", "terminal value dominates", "cash flow / discount rate"),
        ("SOTP", "support if segments differ", "segments have distinct economics", "segment allocation is arbitrary", "segment mix"),
    ]
    for row, values in enumerate(method_rows, start=37):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            ib.apply_comment(ws.cell(row, col), wrap_text=False)
    _section(ws, 28, "Investor return")
    _write_values(ws, 29, "Equity invested", "JPY", [f"='Capital Stack'!{get_column_letter(c)}7" for c in cols], kind="formula", fmt=ib.FMT_MONEY)
    _write_values(ws, 30, "New investor ownership", "%", [f"='Capital Stack'!{get_column_letter(c)}16" for c in cols], kind="formula", fmt=ib.FMT_PERCENT)
    _write_values(ws, 31, "MOIC at selected EV", "x", [f"=IF({get_column_letter(c)}29=0,\"-\",{get_column_letter(c)}26*{get_column_letter(c)}30/{get_column_letter(c)}29)" for c in cols], kind="formula", fmt=ib.FMT_MULTIPLE)
    _write_values(ws, 32, "Illustrative IRR", "%", [f"=IF({get_column_letter(c)}31=\"-\",\"-\",{get_column_letter(c)}31^(1/{max(idx, 1)})-1)" for idx, c in enumerate(cols, start=1)], kind="formula", fmt=ib.FMT_PERCENT)
    _highlight_row(ws, 31, _start_period_col() + len(cols) - 1)
    _section(ws, 45, "Valuation committee gates", start_col + 4)
    gate_headers = ["Gate", "Threshold", "Current read", "Decision use", "If failed"]
    for col, header in enumerate(gate_headers, start=start_col):
        _apply_text_header(ws.cell(46, col), header)
    gate_rows = [
        ("Benchmark freshness", "current/provided with limits", "see Benchmarks freshness", "decide whether comps can support price", "refresh or verify comps before external use"),
        ("Supportability score", ">= 0.9x", f"see {final_col}24", "decide whether midpoint is usable", "haircut selected EV or use downside"),
        ("Return hurdle", ">= 2.0x MOIC", f"see {final_col}31", "decide price / ownership acceptability", "reprice, resize, or reject"),
        ("SOTP credibility", "segment evidence not arbitrary", "see Segments source status", "decide if SOTP is primary or support", "keep SOTP as cross-check only"),
    ]
    for row, values in enumerate(gate_rows, start=47):
        for col, value in enumerate(values, start=start_col):
            ws.cell(row, col, value)
            if isinstance(value, str) and value.startswith("="):
                _apply_value_style(ws.cell(row, col), ib.FMT_MULTIPLE if row in (48, 49) else "General")
            else:
                ib.apply_comment(ws.cell(row, col), wrap_text=False)
    cats = Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=13)
    _add_bar_chart(ws, "Exit EV range", Reference(ws, min_col=cols[0], max_col=cols[-1], min_row=16, max_row=27), cats, "B54", _money_unit(facts))


def _build_market_support(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Market Support"]
    _setup_sheet(ws, f"{facts.company} — Market Support", "Traceable market, customer, and benchmark support from the provided source.")
    _section(ws, 6, "Source anchors")
    ws["B8"] = "Source anchors: " + ("; ".join(facts.source_names) if facts.source_names else "No explicit external source listed")
    ib.apply_comment(ws["B8"], wrap_text=False)
    for r, line in enumerate(facts.market_lines[:8], start=9):
        ws.cell(r, 2, line)
        ib.apply_comment(ws.cell(r, 2), wrap_text=False)
    ws._startup_note_col = 11
    _section(ws, 19, "TAM / SAM / SOM bridge", 11)
    rows = [
        ("TAM", "top-down opportunity", facts.tam_yen, "category-wide opportunity"),
        ("SAM", "serviceable market", facts.sam_yen, "reachable wedge given geography/channel/product readiness"),
        ("SOM", "plan case", facts.som_yen, "model-implied reachable revenue or GMV basis"),
    ]
    for r, (label, source, value, note) in enumerate(rows, start=20):
        _label(ws, r, label, "JPY", source=source, note=note, bold=label == "SOM", fmt=ib.FMT_MONEY)
        ws.cell(r, _start_period_col(), value)
        ib.apply_hard_input(ws.cell(r, _start_period_col()), _money_format(facts))
        if label == "SOM":
            _highlight_row(ws, r, _start_period_col())
    if facts.source_urls:
        _section(ws, 26, "URLs captured from source")
        for r, url in enumerate(facts.source_urls[:8], start=27):
            ws.cell(r, 2, url)
            ib.apply_link_external(ws.cell(r, 2))


def _build_benchmarks(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["Benchmarks"]
    _setup_sheet(ws, f"{facts.company} — Benchmarks", "Traceable benchmark and source register for material assumptions.")
    _set_column_widths(ws, {2: 14, 3: 24, 4: 18, 5: 42, 6: 42, 7: 22, 8: 28, 9: 18, 10: 20, 11: 20, 12: 28})
    headers = ["source_id", "Source type", "Date / period", "URL / file / owner", "Applicability limits", "Freshness status", "Linked assumption", "Refresh needed"]
    for col, header in enumerate(headers, start=BENCHMARK_REGISTER_START_COL):
        _apply_text_header(ws.cell(5, col), header)
    source_anchor = "; ".join(facts.source_names or facts.source_urls) if (facts.source_names or facts.source_urls) else "unknown"
    live_comps = list(getattr(facts, "live_comps", []) or [])
    current_revenue_multiple = any(comp.get("status") == "current" and comp.get("revenue_multiple") for comp in live_comps if isinstance(comp, dict))
    current_ebitda_multiple = any(comp.get("status") == "current" and comp.get("ebitda_multiple") for comp in live_comps if isinstance(comp, dict))
    provided_multiple = any(comp.get("status") == "provided" and (comp.get("revenue_multiple") or comp.get("ebitda_multiple")) for comp in live_comps if isinstance(comp, dict))
    live_freshness = (
        "current"
        if current_revenue_multiple and current_ebitda_multiple
        else "provided / verify"
        if provided_multiple
        else "partial refresh"
        if current_revenue_multiple or current_ebitda_multiple
        else "needs refresh"
    )
    rows = [
        ("SRC-01", facts.evidence_status, "source period", source_anchor, "company-specific evidence", "needs refresh", "pricing / demand", "yes"),
        ("SRC-02", "estimate", "model date", "modeler estimate", "replace with actual or benchmark", "not externally sourced", "cost-to-serve", "yes"),
        ("SRC-03", "management target", "plan period", "management plan", "depends on execution capacity", "not externally sourced", "headcount / capacity", "yes"),
        ("SRC-04", "benchmark", "comparable refresh" if live_freshness != "needs refresh" else "needs refresh", "comparable evidence register" if live_freshness != "needs refresh" else "unresolved external benchmark", "public/private comps; validate fit", live_freshness, "valuation support", "no" if live_freshness == "current" else "yes"),
        ("SRC-05", "unknown", "unknown", "unresolved evidence", "do not treat as fact", "needs evidence", "financing terms", "yes"),
    ]
    for r, row in enumerate(rows, start=6):
        for c, value in enumerate(row, start=BENCHMARK_REGISTER_START_COL):
            ws.cell(r, c, value)
            ib.apply_comment(ws.cell(r, c), wrap_text=False)
    if live_comps:
        _section(ws, 13, "Comparable evidence", 12)
        comp_headers = ["Ticker", "Company", "Type", "Source type", "Stage / geography", "EV / Revenue", "EV / EBITDA", "As of", "Status", "Applicability", "Source / error"]
        for col, header in enumerate(comp_headers, start=LAYOUT.label_col):
            _apply_text_header(ws.cell(14, col), header)
        for row_idx, comp in enumerate(live_comps, start=15):
            source_or_error = comp.get("source_url") if comp.get("status") in {"current", "provided"} else comp.get("error")
            values = [
                comp.get("ticker"),
                comp.get("name"),
                comp.get("company_type") or "public",
                comp.get("source_type") or "benchmark",
                " / ".join(str(part) for part in (comp.get("stage"), comp.get("geography")) if part),
                comp.get("revenue_multiple"),
                comp.get("ebitda_multiple"),
                comp.get("as_of_date"),
                comp.get("status"),
                comp.get("applicability_limits") or comp.get("error"),
                source_or_error,
            ]
            for col, value in enumerate(values, start=LAYOUT.label_col):
                ws.cell(row_idx, col, value)
                if col in (LAYOUT.label_col + 5, LAYOUT.label_col + 6):
                    _apply_value_style(ws.cell(row_idx, col), ib.FMT_MULTIPLE)
                elif col == LAYOUT.label_col + 10 and comp.get("status") in {"current", "provided"}:
                    ib.apply_link_external(ws.cell(row_idx, col))
                else:
                    ib.apply_comment(ws.cell(row_idx, col), wrap_text=False)


def _build_ic_memo(wb: Workbook, facts: SourceFacts) -> None:
    ws = wb["IC Memo"]
    _setup_sheet(ws, f"{facts.company} — IC Decision Memo", "Investment committee recommendation, valuation stance, risks, and diligence gates generated from the model.")
    final_col = _final_period_col(facts)
    sections = [
        ("Recommendation", f"=IF(AND('Valuation'!{final_col}31>=2,'Valuation'!{final_col}24>=0.9,'Pricing'!{final_col}21=\"pass\"),\"Proceed subject to DD gates\",\"Do not circulate externally until valuation, pricing, and evidence gates are cleared\")"),
        ("Investment thesis", f"{facts.company} is modeled through an economic kernel described as {facts.mechanics}; use this as a driver composition, not a sector template."),
        ("KPI readout", f"=\"Final runway: \"&TEXT('KPI'!{final_col}20,\"0.0\")&\" months; burn multiple: \"&TEXT('KPI'!{final_col}18,\"0.0x\")&\"; gross margin: \"&TEXT('KPI'!{final_col}16,\"0%\")"),
        ("Funding and dilution", f"=\"Final funding gap: JPY \"&ROUND('Scenarios'!{get_column_letter(_start_period_col())}19/10^6,0)&\"M; new investor ownership: \"&TEXT('Capital Stack'!{final_col}16,\"0%\")&\"; founder ownership: \"&TEXT('Ownership'!{final_col}7,\"0%\")"),
        ("Valuation and return", f"=\"Selected EV midpoint: JPY \"&ROUND('Valuation'!{final_col}26/10^6,0)&\"M; supportability: \"&TEXT('Valuation'!{final_col}24,\"0.0x\")&\"; MOIC: \"&TEXT('Valuation'!{final_col}31,\"0.0x\")&\"; IRR: \"&TEXT('Valuation'!{final_col}32,\"0%\")"),
        ("Price / terms stance", f"=\"Target price range: JPY \"&ROUND('Valuation'!{final_col}25/10^6,0)&\"M-\"&ROUND('Valuation'!{final_col}27/10^6,0)&\"M EV; pricing gate: \"&'Pricing'!{final_col}21&\"; exit signal: \"&'Exit Waterfall'!M7"),
        ("What must be true", "Demand, pricing, cost-to-serve, capacity, financing, segment economics, cap-table terms, and valuation support must reconcile to explicit evidence status before external circulation."),
        ("Scenario breakpoint", "Downside is decision-relevant when it creates a funding gap, runway breach, covenant issue, unacceptable dilution, preference-stack leakage, or valuation support break."),
        ("Ranked DD gates", "1) benchmark freshness and comps; 2) customer ROI/WTP proof; 3) cohort retention and CAC; 4) cost-to-serve and deployment capacity; 5) financing terms, preference stack, tax/debt constraints, and buyer-view exit support."),
        ("Walk-away conditions", "Reject or reprice if MOIC stays below hurdle, supportability remains below gate, pricing validation fails, benchmark support is unresolved, or downside financing requires unacceptable dilution."),
        ("Source boundary", "Source fields should contain traceable evidence or evidence status only; refresh material benchmarks before external circulation."),
    ]
    row = 6
    for title, body in sections:
        _section(ws, row, title)
        body_cell = ws.cell(row + 1, LAYOUT.label_col, body)
        if isinstance(body, str) and body.startswith("="):
            _apply_value_style(body_cell, "General")
        else:
            ib.apply_comment(body_cell, wrap_text=False)
        ws.row_dimensions[row + 1].height = ib.ROW_HEIGHT_BASE
        row += 4
    for label, body in [
        ("Decision owner", "Assign banker / investor owner before external circulation."),
        ("Next action", "Refresh sources, rerun strict audit, and update recommendation after DD gates clear."),
        ("Evidence package", "Attach source register, cohort export, pricing validation, cap-table terms, and buyer-view exit support."),
    ]:
        ws.cell(row, LAYOUT.label_col, label)
        ws.cell(row, LAYOUT.source_col, body)
        ib.apply_label(ws.cell(row, LAYOUT.label_col))
        ib.apply_comment(ws.cell(row, LAYOUT.source_col), wrap_text=False)
        row += 1


def build_source_plan_workbook_from_facts(facts: SourceFacts) -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)
    for name in SOURCE_PLAN_SHEETS:
        ws = wb.create_sheet(name)
        ws._startup_facts = facts

    _build_guide(wb, facts)
    _build_kernel(wb, facts)
    _build_assumptions(wb, facts)
    _build_driver_tree(wb, facts)
    _build_revenue(wb, facts)
    _build_cost(wb, facts)
    _build_people(wb, facts)
    _build_capital_stack(wb, facts)
    _build_ownership(wb, facts)
    _build_pricing(wb, facts)
    _build_financing(wb, facts)
    _build_segments(wb, facts)
    _build_pl(wb, facts)
    _build_cf(wb, facts)
    _build_bs(wb, facts)
    _build_kpi(wb, facts)
    _build_scenarios(wb, facts)
    _build_sensitivity(wb, facts)
    _build_valuation(wb, facts)
    _build_exit_waterfall(wb, facts)
    _build_market_support(wb, facts)
    _build_benchmarks(wb, facts)
    _build_ic_memo(wb, facts)

    _apply_design_surface(wb)
    ib.normalize_workbook_fonts(wb)
    ib.set_workbook_default_font(wb)
    _disable_wrap_text(wb)
    _clear_blank_cell_styles(wb)
    _trim_blank_canvas(wb)
    _apply_print(wb)
    wb.defined_names.clear()
    for ws in wb.worksheets:
        ws.defined_names.clear()
    return wb


def build_source_plan_workbook_from_text(text: str, output_path: Path) -> Path:
    facts = derive_source_facts(text)
    wb = build_source_plan_workbook_from_facts(facts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


def build_source_plan_workbook(source_md: Path, output_path: Path) -> Path:
    wb = build_source_plan_workbook_from_facts(extract_source_facts(source_md))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build generic economic-kernel startup financial plan xlsx.")
    ap.add_argument("--source-md", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    build_source_plan_workbook(args.source_md, args.output)
    print(f"[ok] generic financial plan generated: {args.output}")
