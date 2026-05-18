"""Economic-kernel extraction and driver composition for startup models."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

DEFAULT_FORECAST_PERIODS = 5
MAX_FORECAST_PERIODS = 60


def forecast_years(start_year: int | None = None, periods: int = DEFAULT_FORECAST_PERIODS) -> list[int]:
    """Return the model forecast years without baking a calendar year into code."""
    base_year = start_year if start_year is not None else date.today().year
    return [base_year + idx for idx in range(periods)]


def forecast_axis(start_year: int | None = None, periods: int = DEFAULT_FORECAST_PERIODS, grain: str = "annual") -> tuple[list[int], list[str]]:
    """Return period years plus display labels for annual, quarterly, or monthly models."""
    base_year = start_year if start_year is not None else date.today().year
    normalized = grain.lower()
    if normalized.startswith("month"):
        years = [base_year + idx // 12 for idx in range(periods)]
        labels = [f"M{idx + 1}" for idx in range(periods)]
    elif normalized.startswith("quarter"):
        years = [base_year + idx // 4 for idx in range(periods)]
        labels = [f"Q{idx + 1}" for idx in range(periods)]
    else:
        years = forecast_years(base_year, periods)
        labels = [f"FY{year}" for year in years]
    return years, labels


@dataclass(frozen=True)
class KeywordSignal:
    term: str
    weight: int = 1


@dataclass(frozen=True)
class MechanicProfile:
    key: str
    label: str
    product: str
    primary_unit_name: str
    keywords: tuple[KeywordSignal, ...]
    default_target_units: int
    first_units: int
    customers: tuple[int, int, int, int, int]
    variable_cogs_pct: tuple[float, float, float, float, float]
    capex_per_unit_yen: tuple[int, int, int, int, int]
    tam_yen: int
    default_monthly_price_yen: int
    default_gmv_yen: int = 0


@dataclass(frozen=True)
class DriverSurface:
    layer: str
    driver: str
    workbook_owner: str
    decision_relevance: str
    source_status: str


@dataclass(frozen=True)
class AssumptionLine:
    label: str
    unit: str
    values: list[Any] | str | int | float
    source: str = ""
    kind: str = "input"
    fmt_key: str = "money"
    bold: bool = False
    note: str = ""


@dataclass(frozen=True)
class AssumptionGroup:
    title: str
    lines: tuple[AssumptionLine, ...]


@dataclass(frozen=True)
class ScenarioDriver:
    label: str
    unit: str
    downside: float
    base: float
    upside: float
    why: str
    output_pressured: str
    breakpoint: str
    decision_implication: str


@dataclass(frozen=True)
class KPIDefinition:
    name: str
    formula_driver: str
    applies_when: str
    source_context: str
    downside_trigger: str
    ic_implication: str


@dataclass(frozen=True)
class SourceFacts:
    years: list[int]
    period_labels: list[str]
    grain: str
    currency: str
    display_scale: str
    company: str
    product: str
    mechanics: str
    primary_unit_name: str
    source_summary: str
    source_names: list[str]
    source_urls: list[str]
    live_comps: list[dict[str, object]]
    market_lines: list[str]
    segments: list[str]
    source_unknowns: list[str]
    new_units: list[int]
    gmv_yen: list[int]
    # Monthly subscription price under `recurring`; the one-time per-unit
    # sale price under `revenue_mode == "unit_sale"` (see _period_subtotal_revenue).
    monthly_price_yen: list[int]
    take_rate: list[float]
    customers: list[int]
    variable_cogs_pct: list[float]
    delivery_cost_yen: list[int]
    cloud_cost_yen: list[int]
    support_cost_yen: list[int]
    capex_per_unit_yen: list[int]
    avg_comp_yen: list[int]
    equity_raise_yen: list[int]
    debt_raise_yen: list[int]
    debt_interest_rate: list[float]
    post_money_yen: list[int]
    founder_ownership: float
    option_pool: float
    existing_investors: float
    strategic_warrant: float
    option_pool_refresh: list[float]
    secondary_warrant_dilution: list[float]
    product_headcount: list[int]
    gtm_headcount: list[int]
    operations_headcount: list[int]
    ga_headcount: list[int]
    net_retention: list[float]
    utilization_conversion: list[float]
    other_revenue_share: list[float]
    deferred_revenue_share: list[float]
    revenue_productivity_factor: list[float]
    depreciation_life_months: list[int]
    other_capex_yen: list[int]
    ar_days: list[int]
    ap_days: list[int]
    tax_rate: list[float]
    beginning_cash_yen: int
    sm_pct_revenue: list[float]
    rd_program_per_product_fte_yen: list[int]
    rd_program_floor_yen: list[int]
    ga_pct_revenue: list[float]
    fixed_ga_yen: list[int]
    inventory_wip_pct_capex: list[float]
    grants_yen: list[int]
    convertibles_yen: list[int]
    lease_financing_yen: list[int]
    customer_advances_yen: list[int]
    secondary_yen: list[int]
    nol_yen: list[int]
    revenue_multiple: list[float]
    gross_profit_multiple: list[float]
    ebitda_multiple: list[float]
    discount_rate: float
    customer_roi_yen: int
    implementation_cost_yen: int
    sales_cycle_months: int
    churn_rate: float
    repeat_rate: float
    payment_fee_pct: float
    incentive_pct_gmv: float
    fraud_loss_pct_gmv: float
    value_capture_share: list[float]
    target_gross_margin: list[float]
    support_tickets_per_customer: list[int]
    minutes_per_support_ticket: list[int]
    support_fte_capacity_tickets: list[int]
    product_squad_size: list[int]
    target_min_runway_months: list[int]
    evidence_status: str
    tam_yen: int
    sam_yen: int
    som_yen: int
    revenue_mode: str = "recurring"


MECHANIC_PROFILES: tuple[MechanicProfile, ...] = (
    MechanicProfile(
        key="marketplace",
        label="Marketplace / transaction",
        product="Marketplace product",
        primary_unit_name="GMV",
        keywords=(
            KeywordSignal("marketplace", 4),
            KeywordSignal("gmv", 4),
            KeywordSignal("take rate", 4),
            KeywordSignal("buyer", 2),
            KeywordSignal("seller", 2),
            KeywordSignal("流通総額", 4),
        ),
        default_target_units=0,
        first_units=2_000,
        customers=(2_000, 4_500, 9_000, 16_000, 26_000),
        variable_cogs_pct=(0.30, 0.28, 0.25, 0.23, 0.22),
        capex_per_unit_yen=(0, 0, 0, 0, 0),
        tam_yen=1_000_000_000_000,
        default_monthly_price_yen=0,
        default_gmv_yen=10_000_000_000,
    ),
    MechanicProfile(
        key="fintech_balance_sheet",
        label="Fintech / balance-sheet",
        product="Fintech product",
        primary_unit_name="Loan book / accounts",
        keywords=(
            KeywordSignal("lending", 4),
            KeywordSignal("loan", 3),
            KeywordSignal("credit", 3),
            KeywordSignal("fintech", 3),
            KeywordSignal("貸金", 4),
            KeywordSignal("融資", 4),
        ),
        default_target_units=25_000,
        first_units=500,
        customers=(500, 1_500, 4_500, 11_000, 25_000),
        variable_cogs_pct=(0.42, 0.38, 0.34, 0.31, 0.30),
        capex_per_unit_yen=(500_000, 400_000, 320_000, 260_000, 220_000),
        tam_yen=2_000_000_000_000,
        default_monthly_price_yen=120_000,
    ),
    MechanicProfile(
        key="hardware_asset_heavy",
        label="Hardware / asset-heavy",
        product="Hardware / AI product",
        primary_unit_name="Deployed units",
        keywords=(
            KeywordSignal("hardware", 3),
            KeywordSignal("robot", 4),
            KeywordSignal("humanoid", 4),
            KeywordSignal("raas", 4),
            KeywordSignal("manufacturing", 3),
            KeywordSignal("フィジカルai", 4),
            KeywordSignal("ヒューマノイド", 4),
        ),
        default_target_units=25_000,
        first_units=50,
        customers=(25, 85, 250, 520, 900),
        variable_cogs_pct=(0.48, 0.42, 0.36, 0.31, 0.28),
        capex_per_unit_yen=(8_000_000, 6_400_000, 5_120_000, 4_096_000, 3_277_000),
        tam_yen=36_500_000_000_000,
        default_monthly_price_yen=300_000,
    ),
    MechanicProfile(
        key="pre_revenue_milestone",
        label="Pre-revenue / milestone",
        product="Deeptech product",
        primary_unit_name="Milestones",
        keywords=(
            KeywordSignal("no revenue", 3),
            KeywordSignal("pre-revenue", 4),
            KeywordSignal("poc", 2),
            KeywordSignal("deeptech", 3),
            KeywordSignal("研究開発", 4),
            KeywordSignal("助成金", 3),
        ),
        default_target_units=18,
        first_units=25,
        customers=(0, 1, 3, 8, 18),
        variable_cogs_pct=(0.15, 0.18, 0.24, 0.30, 0.35),
        capex_per_unit_yen=(30_000_000, 28_000_000, 24_000_000, 20_000_000, 18_000_000),
        tam_yen=1_500_000_000_000,
        default_monthly_price_yen=120_000,
    ),
    MechanicProfile(
        key="recurring_software",
        label="Recurring software",
        product="Recurring software product",
        primary_unit_name="Active accounts",
        keywords=(
            KeywordSignal("saas", 4),
            KeywordSignal("arr", 3),
            KeywordSignal("mrr", 3),
            KeywordSignal("subscription", 3),
            KeywordSignal("nrr", 2),
        ),
        default_target_units=5_000,
        first_units=100,
        customers=(80, 220, 520, 1_050, 1_900),
        variable_cogs_pct=(0.22, 0.20, 0.18, 0.17, 0.16),
        capex_per_unit_yen=(100_000, 90_000, 80_000, 75_000, 70_000),
        tam_yen=1_200_000_000_000,
        default_monthly_price_yen=120_000,
    ),
    MechanicProfile(
        key="generic",
        label="Generic startup",
        product="Startup product",
        primary_unit_name="Economic units",
        keywords=(),
        default_target_units=3_500,
        first_units=100,
        customers=(100, 300, 850, 1_800, 3_500),
        variable_cogs_pct=(0.40, 0.36, 0.32, 0.29, 0.27),
        capex_per_unit_yen=(1_000_000, 850_000, 720_000, 610_000, 520_000),
        tam_yen=1_000_000_000_000,
        default_monthly_price_yen=120_000,
    ),
)


def read_source(source_md: Path) -> str:
    return source_md.read_text(encoding="utf-8")


def score_mechanics(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for profile in MECHANIC_PROFILES:
        score = 0
        for signal in profile.keywords:
            if signal.term.lower() in lowered:
                score += signal.weight
        scores[profile.key] = score
    return scores


def profile_for_text(text: str) -> MechanicProfile:
    scores = score_mechanics(text)
    best = max(MECHANIC_PROFILES, key=lambda profile: scores[profile.key])
    if scores[best.key] <= 0:
        return _profile("generic")
    return best


def _profile(key: str) -> MechanicProfile:
    for profile in MECHANIC_PROFILES:
        if profile.key == key:
            return profile
    raise KeyError(key)


def extract_start_year(text: str) -> int:
    """Infer forecast start year only from explicit model/fiscal-year signals."""
    # `[^\n]{0,24}?` is non-greedy: it captures the first year after the cue,
    # so a hyphenated range ("(2026-2031)") yields the start year 2026, not
    # the end year 2031.
    patterns = [
        r"(?:model|forecast|plan|fiscal|FY|開始|初年度|計画)[^\n]{0,24}?(20\d{2})",
        r"(20\d{2})\s*(?:forecast|plan|model|年度開始|開始)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return date.today().year


def extract_model_grain(text: str) -> str:
    """Detect the requested period grain.

    Grain detection is deliberately conservative: bare words like "monthly
    burn" or "18-month runway" describe metrics, not a request for a
    month-by-month model. The forecast architecture is annual (revenue, cost,
    and comp formulas annualize per period), so only an explicit request for a
    monthly or quarterly *model* flips the grain.
    """
    lowered = text.lower()
    monthly_model = any(
        token in lowered
        for token in (
            "monthly model", "month-by-month model", "month by month model",
            "monthly financial model", "monthly p&l", "monthly forecast",
            "monthly build", "monthly cash model", "月次モデル",
            "月次財務モデル", "月次の財務モデル", "月次計画", "月次で作",
            "月次で構築", "月次で組",
        )
    )
    if monthly_model:
        return "monthly"
    quarterly_model = any(
        token in lowered
        for token in (
            "quarterly model", "quarter-by-quarter", "quarterly forecast",
            "quarterly p&l", "quarterly build", "四半期モデル",
            "四半期の財務モデル", "四半期で作",
        )
    )
    if quarterly_model:
        return "quarterly"
    return "annual"


def extract_forecast_periods(text: str, grain: str) -> int:
    lowered = text.lower()
    # The years pattern allows a hyphen ("6-year plan") as well as a space.
    # The `(?![\s-]olds?\b)` guard rejects a company-age adjective
    # ("6-year-old startup"), which is not a forecast horizon. Months /
    # quarters keep the spaced form only: a hyphenated "18-month runway" is
    # a metric phrase, not a request for an 18-period horizon.
    patterns = [
        r"([0-9]{1,2})\s*(?:months|month|か月|ヶ月)",
        r"([0-9]{1,2})\s*(?:quarters|quarter|四半期)",
        r"([0-9]{1,2})[\s-]*(?:years|year|年)(?![\s-]olds?\b)",
    ]
    for pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if "quarter" in pattern or "四半期" in pattern:
                return min(max(value, 1), MAX_FORECAST_PERIODS)
            if "month" in pattern or "か月" in pattern or "ヶ月" in pattern:
                return min(max(value, 1), MAX_FORECAST_PERIODS)
            if grain == "monthly":
                return min(max(value * 12, 1), MAX_FORECAST_PERIODS)
            if grain == "quarterly":
                return min(max(value * 4, 1), MAX_FORECAST_PERIODS)
            return min(max(value, 1), MAX_FORECAST_PERIODS)
    if grain == "monthly":
        return 24 if any(token in lowered for token in ("seed", "pre-revenue", "シード", "売上はありません", "まだ売上")) else 12
    if grain == "quarterly":
        return 12
    return DEFAULT_FORECAST_PERIODS


def _pad_series(values: Iterable[int | float], periods: int, default: int | float = 0) -> list:
    series = list(values)
    if not series:
        series = [default]
    while len(series) < periods:
        series.append(series[-1])
    return series[:periods]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _coerce_int_series(raw: Any, periods: int, default: list[int]) -> list[int]:
    values = []
    for item in _as_list(raw):
        if isinstance(item, str):
            parsed = money_yen([r"([0-9,.]+)\s*(兆|億|百万|万|t|T|bn|b|B|m|M)?"], item, 0)
            values.append(parsed)
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            values.append(int(item))
    if not values:
        values = list(default)
    return [int(v) for v in _pad_series(values, periods, default[-1] if default else 0)]


def _coerce_float_series(raw: Any, periods: int, default: list[float], percent: bool = False) -> list[float]:
    values = []
    for item in _as_list(raw):
        if isinstance(item, str):
            cleaned = item.strip().replace("%", "")
            try:
                number = float(cleaned)
                values.append(number / 100 if percent or "%" in item else number)
            except ValueError:
                continue
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            number = float(item)
            values.append(number / 100 if percent and number > 1 else number)
    if not values:
        values = list(default)
    return [float(v) for v in _pad_series(values, periods, default[-1] if default else 0.0)]


def _first_present(raw: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in raw:
            return raw[key]
    return None


def _round_to(value: float, unit: int) -> int:
    if value <= 0:
        return 0
    return int(round(value / unit) * unit)


def _curve(start: float, end: float, periods: int) -> list[float]:
    if periods <= 1:
        return [end]
    return [start + (end - start) * idx / (periods - 1) for idx in range(periods)]


def _price_series(price: int, periods: int) -> list[int]:
    return [int(price * (1.0 + 0.03 * idx)) for idx in range(periods)]


def _take_rate_series(take: float, periods: int) -> list[float]:
    return [min(take + 0.004 * idx, 0.25) for idx in range(periods)]


def extract_rd_headcount(text: str) -> int:
    """Stated current R&D / engineering / product team size, or 0.

    A narrative that states the team it already runs ("a 32-person R&D
    team") pins the people-cost base; the auto-derived ramp would size it
    from revenue / units and badly understate an R&D-heavy plan.
    """
    # Every pattern requires explicit "team" framing — a bare "N engineers"
    # is dropped, as it would match a hiring plan ("hire 15 engineers next
    # year") or an incidental count ("a network of 500 researchers").
    role = r"R&D|research|engineering|product|technical|dev(?:elopment)?"
    patterns = [
        rf"([0-9]{{1,4}})[-\s]person\s+(?:{role})\s+team",
        rf"(?:{role})\s+team\s+of\s+([0-9]{{1,4}})",
        rf"team\s+of\s+([0-9]{{1,4}})\s+(?:engineers|researchers|developers)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            count = int(match.group(1))
            if 0 < count < 10_000:
                return count
    return 0


def _headcount_plan(profile: MechanicProfile, revenue: list[int]) -> tuple[list[int], list[int], list[int], list[int]]:
    """Create editable staffing assumptions scaled to revenue, not a company
    example.

    Every function scales with revenue. Operations once carried a raw
    account-count term (`scale / ops_divisor`) that equated one customer to a
    fixed slice of operations staff regardless of price — a low-ARPU
    mass-market plan then drew hundreds of operations FTE and people cost ran
    past revenue. Headcount is funded by revenue, so revenue is the driver;
    the agent should override `*_headcount` in structured input when a plan's
    staffing is known.
    """
    asset_heavy = profile.key in {"hardware_asset_heavy", "fintech_balance_sheet"}
    marketplace = profile.key == "marketplace"
    product: list[int] = []
    gtm: list[int] = []
    operations: list[int] = []
    ga: list[int] = []
    for idx, revenue_yen in enumerate(revenue):
        revenue_b = max(revenue_yen / 1_000_000_000, 0)
        product_base = 4 + idx * 2 + revenue_b * (2.2 if asset_heavy else 1.2)
        gtm_base = 2 + revenue_b * (1.4 if marketplace else 1.8)
        ops_base = 1 + revenue_b * (0.7 if asset_heavy else 0.35)
        product.append(max(2, int(round(product_base))))
        gtm.append(max(1, int(round(gtm_base))))
        operations.append(max(1, int(round(ops_base))))
        ga.append(max(1, int(round((product[-1] + gtm[-1] + operations[-1]) * 0.16))))
    return product, gtm, operations, ga


def _operating_assumption_curves(profile: MechanicProfile, periods: int) -> dict[str, list]:
    asset_heavy = profile.key in {"hardware_asset_heavy", "fintech_balance_sheet"}
    marketplace = profile.key == "marketplace"
    return {
        "net_retention": _curve(1.00, 1.10 if not marketplace else 1.04, periods),
        "utilization_conversion": _curve(0.35, 0.72 if asset_heavy else 0.64, periods),
        "other_revenue_share": _curve(0.00, 0.10 if not marketplace else 0.06, periods),
        "deferred_revenue_share": _curve(0.08, 0.12 if not marketplace else 0.04, periods),
        "revenue_productivity_factor": _curve(0.45, 1.35 if not asset_heavy else 1.10, periods),
        "depreciation_life_months": [48 if asset_heavy else 60 for _ in range(periods)],
        "ar_days": [45 for _ in range(periods)],
        "ap_days": [45 + min(idx * 4, 15) for idx in range(periods)],
        "tax_rate": _curve(0.00, 0.30, periods),
        "sm_pct_revenue": _curve(0.18, 0.10 if marketplace else 0.14, periods),
        "ga_pct_revenue": _curve(0.10, 0.06, periods),
        "inventory_wip_pct_capex": [0.18 if asset_heavy else 0.04 if marketplace else 0.08 for _ in range(periods)],
        "debt_interest_rate": _curve(0.05, 0.06, periods),
        "option_pool_refresh": [0.00] + [0.02 for _ in range(max(0, periods - 1))],
        "secondary_warrant_dilution": [0.00] + [0.005 if asset_heavy else 0.00 for _ in range(max(0, periods - 1))],
    }


def _debt_plan(
    profile: MechanicProfile,
    new_units: list[int],
    capex_per_unit: list[int],
    other_capex: list[int],
    round_unit: int = 100_000_000,
) -> list[int]:
    """Asset-backed debt capacity per period (unchanged level heuristic)."""
    asset_debt_share = (
        0.35
        if profile.key == "hardware_asset_heavy"
        else 0.20
        if profile.key == "fintech_balance_sheet"
        else 0.05
    )
    debt: list[int] = []
    for idx in range(len(new_units)):
        growth_investment = max(0, new_units[idx] * capex_per_unit[idx]) + other_capex[idx]
        debt.append(_round_to(growth_investment * asset_debt_share, round_unit))
    return debt


def first_match_float(patterns: Iterable[str], text: str, default: float) -> float:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            continue
        raw = m.group(1).replace(",", "").replace("，", "")
        try:
            return float(raw)
        except ValueError:
            continue
    return default


def money_from_match(match: re.Match) -> int | None:
    """Parse a monetary regex match into an integer in the model currency.

    Number is group 1, optional scale unit (万/億/兆/m/b/t...) is group 2. The
    result is a raw amount; the caller decides the currency.
    """
    raw = match.group(1).replace(",", "").replace("，", "")
    unit_raw = match.group(2) if len(match.groups()) >= 2 else ""
    unit = (unit_raw or "").lower()
    try:
        value = float(raw)
    except ValueError:
        return None
    if unit in {"兆", "t", "tn", "trillion"}:
        return int(value * 1_000_000_000_000)
    if unit in {"億"}:
        return int(value * 100_000_000)
    if unit in {"b", "bn", "billion"}:
        return int(value * 1_000_000_000)
    if unit in {"百万", "m", "mn", "million"}:
        return int(value * 1_000_000)
    if unit in {"万"}:
        return int(value * 10_000)
    if unit in {"千", "k", "thousand"}:
        return int(value * 1_000)
    return int(value)


def money_yen(patterns: Iterable[str], text: str, default: int) -> int:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            continue
        scaled = money_from_match(m)
        if scaled is not None:
            return scaled
    return default


def extract_company(text: str) -> str:
    heading = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if heading:
        caps = re.search(r"\b([A-Z][A-Z0-9]{2,16})\b", heading.group(1))
        if caps:
            return caps.group(1)
        return heading.group(1).strip()[:32]
    caps = re.search(r"\b([A-Z][A-Z0-9]{2,16})\b", text)
    return caps.group(1) if caps else "Startup"


def extract_sources(text: str) -> tuple[list[str], list[str]]:
    names: list[str] = []
    for line in text.splitlines():
        source_match = re.search(r"(?:^|\b)source\s*[:：]\s*(.+)$", line, flags=re.IGNORECASE)
        if source_match:
            payload = source_match.group(1)
            for part in re.split(r"[;,、]", payload):
                cleaned = part.strip(" .")
                if cleaned and cleaned not in names:
                    names.append(cleaned)
    urls = []
    for url in re.findall(r"https?://[^\s)）]+", text):
        cleaned = url.rstrip("。.,)")
        if cleaned not in urls:
            urls.append(cleaned)
    return names[:16], urls[:12]


def extract_market_lines(text: str) -> list[str]:
    keywords = ("TAM", "SAM", "SOM", "market", "市場", "GMV", "ARR", "revenue", "売上", "資金")
    lines = []
    for line in text.splitlines():
        clean = line.strip(" -*|")
        has_metric = any(k in clean for k in keywords) or re.search(r"\b20\d{2}\b", clean)
        if 16 <= len(clean) <= 180 and has_metric:
            lines.append(clean)
        if len(lines) >= 10:
            break
    return lines


# Nominal JPY-per-USD rate. The economic kernel carries JPY-denominated default
# magnitudes (comp, capital floors, capex, G&A); for a USD model they are
# divided by this rate so a dollar plan reads in plausible dollar magnitudes.
DEFAULT_JPY_PER_USD = 150.0


def money_scale_for_currency(currency: str, jpy_per_usd: float = DEFAULT_JPY_PER_USD) -> float:
    """Factor that converts a JPY-denominated default into the model currency."""
    if currency == "USD" and jpy_per_usd > 0:
        return 1.0 / jpy_per_usd
    return 1.0


def extract_currency(text: str) -> str:
    """Detect the model currency from the narrative; default to JPY.

    The skill is JPY-primary, so this flips to USD only on a strong USD signal
    with no competing JPY signal — a JPY plan that merely cites a dollar-priced
    competitor or comparable stays JPY.
    """
    usd_figures = re.findall(r"\$\s?[0-9]", text)
    usd_word = bool(
        re.search(r"\bUSD\b|US\s?dollar|US-based|米ドル|ドル建", text, flags=re.IGNORECASE)
    )
    has_jpy = bool(
        re.search(
            r"[¥円]|\bJPY\b|\byen\b|月額|[0-9]\s*(?:万|億|百万|兆)",
            text,
            flags=re.IGNORECASE,
        )
    )
    # USD needs a strong signal — an explicit USD word or at least two dollar
    # figures. A lone "$NNN" (typically a competitor reference) is not enough.
    strong_usd = usd_word or len(usd_figures) >= 2
    if strong_usd and not has_jpy:
        return "USD"
    return "JPY"


# Single-letter Latin scale units must not bleed into a following word — the
# "b" of "but" once parsed as "billion" (cf. the same fix for GMV extraction).
_PRICE_UNIT = r"(万|億|百万|[mMbB](?![A-Za-z]))"

# Economic-unit nouns for the number-first "$X per <unit>" price pattern.
_UNIT_NOUN = r"unit|robot|device|machine|vehicle|drone|seat|user|customer|台"


# Markers that a stated price is annual, so it must be divided to a monthly
# figure. ACV (Annual Contract Value) is annual by definition.
_ANNUAL_PRICE_CUE = re.compile(
    r"per\s*year|/\s*year|per\s*annum|\bp\.a\.|annual(?:ly)?|年額|年間|/\s*年|年契約",
    flags=re.IGNORECASE,
)


def extract_price(text: str, profile: MechanicProfile, currency: str = "JPY") -> int:
    """Extract a monthly per-unit price; annual figures (ACV, "per year") /12.

    The model drives recurring revenue off a *monthly* price. A stated ACV or
    an explicitly annual price is divided to a monthly figure so a ¥7M/year
    contract is not modeled as ¥7M/month.
    """
    if profile.key == "marketplace":
        return 0
    # (pattern, always_annual) — `月額` is monthly; ACV is annual by definition;
    # the other patterns are annual only when annual cues sit next to them.
    # `sells/sold for|at` requires a currency mark, so a volume or duration
    # after the verb ("sold for 3 years") is not read as a price. The
    # number-first "$X per <unit-noun>" form covers phrasing no cue keyword
    # sits next to; its `s?\b` matches the plural and blocks a partial-word
    # match.
    month = (rf"月額\s*([0-9,.]+)\s*{_PRICE_UNIT}?\s*円?", False)
    sells = (
        rf"(?:sells?|sold)\s+(?:for|at)[^0-9¥$]{{0,16}}[¥$]\s*"
        rf"([0-9,.]+)\s*{_PRICE_UNIT}?",
        None,
    )
    keyword = (
        rf"(?:price|pricing|fee|subscription|lease|rental|unit price|"
        rf"単価|価格|利用料)"
        rf"[^0-9¥$]{{0,32}}[¥$]?\s*([0-9,.]+)\s*{_PRICE_UNIT}?",
        None,
    )
    per_unit = (
        rf"[¥$]\s*([0-9,.]+)\s*{_PRICE_UNIT}?\s*(?:per|/|あたり)\s*"
        rf"(?:{_UNIT_NOUN})s?\b",
        None,
    )
    # For hardware, the unit sale is the primary revenue: an explicit
    # "sells/sold for $X" outranks an incidental attach-revenue keyword
    # ("a support subscription at $X/year"). Every other profile keeps the
    # keyword cue first — its subscription / fee price is the primary one.
    candidates: list[tuple[str, bool | None]] = (
        [month, sells, keyword, per_unit]
        if profile.key == "hardware_asset_heavy"
        else [month, keyword, sells, per_unit]
    )
    if profile.key != "hardware_asset_heavy":
        candidates.append(
            (rf"ACV[^0-9¥$]{{0,24}}[¥$]?\s*([0-9,.]+)\s*{_PRICE_UNIT}?", True),
        )
    default_price = max(1, int(profile.default_monthly_price_yen * money_scale_for_currency(currency)))
    # The noise floor is currency-relative: a valid USD per-seat price ($80) is
    # far below any sane JPY price floor, but the floor must still reject a
    # near-zero spurious match — hence $10, not $1.
    floor = 10 if currency == "USD" else max(10_000, int(profile.default_monthly_price_yen * 0.05))
    price = default_price
    for pattern, always_annual in candidates:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        value = money_from_match(match)
        if value is None or value <= 0:
            continue
        is_annual = always_annual
        if is_annual is None:
            context = text[max(0, match.start() - 40): match.end() + 40]
            is_annual = bool(_ANNUAL_PRICE_CUE.search(context))
        # Apply the noise floor to the as-stated figure so a valid-but-small
        # annual contract (¥120k/year -> ¥10k/month) is not discarded after
        # the division; a sub-floor match is noise — keep searching.
        if value < floor * (12 if is_annual else 1):
            continue
        price = int(round(value / 12)) if is_annual else value
        break
    return price


# A narrative states a current / year-one figure before the maturity target
# ("currently 30 customers and target 1,200"; "ship 40 units ... target
# 2,500"). A target / maturity cue marks the figure the plan should ramp to,
# so the extractor must prefer it over a plain first match. The cue can sit
# on either side of the figure — it leads ("target 1,200") as often as it
# trails ("25,000 operating units at maturity") — so both sides are scanned.
# `までに` ("by / no later than") carries the temporal-target sense; bare
# `まで` is excluded because it is also a present-state particle (`今まで`,
# "until now").
_TARGET_CUE = re.compile(
    r"(target|reach(?:ing)?|grow(?:ing)?\s+to|scal(?:e|ing)\s+to|ramp\s+to|"
    r"by\s+year|by\s+(?:FY)?\s*20\d\d|at\s+maturity|maturity|"
    r"目標|までに|成熟)",
    flags=re.IGNORECASE,
)
# A prefix cue ("target", "grow to") points forward to a *later* figure; a
# postfix cue trails the figure it marks ("25,000 units at maturity"). Only
# this postfix subset may be matched in a figure's trailing window — a prefix
# cue found after a figure belongs to the next number, not this one.
_TRAILING_TARGET_CUE = re.compile(
    r"at\s+maturity|maturity|by\s+year|by\s+the\s+end|"
    r"成熟|目標|までに|最終年|時点",
    flags=re.IGNORECASE,
)


def _maturity_count(
    patterns: Iterable[tuple[str, int]], text: str, default: int
) -> int:
    """Pick the count tied to a maturity / target cue from all matches.

    A plain first match grabs the current or year-one figure stated before
    the target. This prefers a figure a target / maturity cue marks — on
    either side of the figure; failing that the largest match (a maturity
    target is almost always the larger number); failing that the default.

    Each pattern carries a unit multiplier so a scale word is normalised on
    the *selected* match (e.g. `万台` -> x10,000) — never document-wide.
    """
    cue_best: int | None = None
    any_best: int | None = None
    for pattern, unit in patterns:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            raw = m.group(1).replace(",", "").replace("，", "")
            try:
                value = int(float(raw)) * unit
            except ValueError:
                continue
            if value <= 0:
                continue
            any_best = value if any_best is None else max(any_best, value)
            lead = text[max(0, m.start() - 48): m.start()]
            # The trailing window is clipped at the first clause boundary or
            # digit, so a postfix cue that belongs to a *later* figure
            # ("10,000 units and we target 2,500 ... by year five") cannot
            # reach back to this one. The comma is a boundary on purpose — it
            # separates the common "current, target" figure pair — at the
            # cost of missing a cue a narrative states after a comma.
            trail = re.split(
                r"[.;,。；、，\n0-9]", text[m.end(): m.end() + 48], maxsplit=1
            )[0]
            if _TARGET_CUE.search(lead) or _TRAILING_TARGET_CUE.search(trail):
                cue_best = value if cue_best is None else max(cue_best, value)
    if cue_best is not None:
        return cue_best
    if any_best is not None:
        return any_best
    return default


def extract_target_units(text: str, profile: MechanicProfile) -> int:
    if profile.key == "marketplace":
        return 0
    return _maturity_count(
        [
            (r"([0-9,.]+)\s*万\s*台", 10_000),
            (r"([0-9,.]+)\s*台", 1),
            (r"([0-9,.]+)\s*operating", 1),
            (r"([0-9,.]+)\s*customers", 1),
            (r"([0-9,.]+)\s*units", 1),
        ],
        text,
        profile.default_target_units,
    )


# Scale words for a stated capital figure (raise size, post-money). A
# single Latin letter must not bleed into a following word — the `m` in
# "5 month" is not a "5M" magnitude — so it requires a non-letter boundary.
_CAPITAL_SCALE = r"(兆|億|百万|万|千|bn|[tTbBmMkK](?![A-Za-z]))"


def _capital_figure(matched: str, scale: str | None, currency: str) -> bool:
    """A stated capital figure must carry a magnitude marker — a currency
    symbol or a scale word — so a bare number ("5" from "5-year plan") is
    not read as a raise. A `$` figure belongs to a USD plan and a `¥` figure
    to a yen plan."""
    if "$" in matched and currency != "USD":
        return False
    if "¥" in matched and currency == "USD":
        return False
    return "$" in matched or "¥" in matched or bool(scale)


def _first_capital_figure(
    patterns: list[str], text: str, currency: str
) -> int:
    """First marker-bearing, currency-consistent capital figure, or 0."""
    for pattern in patterns:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            scale = m.group(2) if m.lastindex and m.lastindex >= 2 else None
            if not _capital_figure(m.group(0), scale, currency):
                continue
            value = money_from_match(m)
            if value and value > 0:
                return value
    return 0


def extract_raise_size(text: str, currency: str = "JPY") -> int:
    """Stated size of the first (seed / Series A-E) equity round, raw currency.

    Returns 0 when nothing is stated, when the figure carries no magnitude
    marker, or when its currency mark contradicts the model currency — in
    each case the funding plan falls back to auto-sizing the round.
    """
    round_cue = r"seed|pre-seed|series\s+[a-e]|round|equity|financing"
    return _first_capital_figure(
        [
            rf"rais\w*\s+(?:a\s+)?(?:[¥$]\s*)?([0-9,.]+)\s*{_CAPITAL_SCALE}?"
            rf"[^0-9.\n]{{0,20}}?(?:{round_cue})",
            rf"[¥$]\s*([0-9,.]+)\s*{_CAPITAL_SCALE}?\s*(?:{round_cue})\b",
            rf"(?:{round_cue})\s+(?:round\s+)?of\s+(?:[¥$]\s*)?"
            rf"([0-9,.]+)\s*{_CAPITAL_SCALE}?",
        ],
        text,
        currency,
    )


def extract_post_money(text: str, currency: str = "JPY") -> int:
    """Stated post-money valuation, raw currency; 0 when absent, unmarked, or
    when the figure's currency mark contradicts the model currency."""
    return _first_capital_figure(
        [
            rf"(?:[¥$]\s*)?([0-9,.]+)\s*{_CAPITAL_SCALE}?\s*post[- ]?money",
            rf"post[- ]?money[^0-9¥$\n]{{0,24}}?(?:[¥$]\s*)?([0-9,.]+)\s*"
            rf"{_CAPITAL_SCALE}?",
            rf"valu\w+\s+(?:at\s+)?(?:a\s+)?(?:[¥$]\s*)?([0-9,.]+)\s*"
            rf"{_CAPITAL_SCALE}?\s*(?:post[- ]?money|valuation)",
        ],
        text,
        currency,
    )


def extract_target_arr(text: str) -> int:
    """Extract a stated maturity ARR / recurring-revenue target, in raw yen."""
    return money_yen(
        [
            r"([0-9,.]+)\s*(兆|億|百万|万|t|T|bn|b|B|m|M)?\s*(?:の)?\s*ARR",
            r"ARR[^0-9¥$]{0,20}(?:of\s+)?¥?\s*([0-9,.]+)\s*(兆|億|百万|万|t|T|bn|b|B|m|M)?",
            r"(?:recurring revenue|年間経常収益)[^0-9¥$]{0,20}¥?\s*([0-9,.]+)\s*(兆|億|百万|万|t|T|bn|b|B|m|M)?",
        ],
        text,
        0,
    )


def extract_target_customers(text: str) -> int:
    """Extract a stated maturity customer / account count.

    Prefers the figure a target / maturity cue precedes — a narrative states
    the current count first ("currently 30 customers and target 1,200").
    """
    return _maturity_count(
        [
            (r"([0-9,]{1,9})\s*(?:paying\s+)?(?:customers|accounts|logos)", 1),
            (r"([0-9,]{1,9})\s*(?:社|アカウント|顧客)", 1),
            (r"顧客\s*(?:数)?\s*(?:約)?\s*([0-9,]{1,9})", 1),
        ],
        text,
        0,
    )


def retarget_demand_to_narrative(
    text: str,
    profile: MechanicProfile,
    new_units: list[int],
    monthly_price: int,
    periods: int,
) -> tuple[list[int], list[int]]:
    """Scale the demand ramp so the plan reaches the narrative's stated scale.

    Sector profiles carry default ramp shapes calibrated to a generic company.
    When the narrative states a maturity ARR or customer count, the plan must
    honor it — a model that lands an order of magnitude short of its own stated
    target is not investor-grade. This rescales the unit and customer ramps by
    single factors, preserving the profile's ramp *shape* while honoring the
    narrative's *level*. Hardware (unit-count driven) and marketplace (GMV
    driven) keep their own anchors and are left untouched.
    """
    units = list(new_units)
    customers = _pad_series(profile.customers, periods, 0)
    # Hardware is already anchored by extract_target_units (unit count) and
    # marketplace by gmv_ramp (GMV); both own their narrative anchor, so an
    # ARR/customer rescale here would double-count. This guard is what keeps a
    # hardware story's stated ARR from being applied to the unit ramp.
    if profile.key in {"hardware_asset_heavy", "marketplace"}:
        return units, customers

    ending = ending_units(units)
    mature_units = ending[-1] if ending else 0
    target_arr = extract_target_arr(text)
    unit_scale = 0.0
    if target_arr > 0 and monthly_price > 0 and mature_units > 0:
        target_units = target_arr / (monthly_price * 12)
        unit_scale = target_units / mature_units
        if unit_scale > 0:
            units = [max(0, int(round(value * unit_scale))) for value in units]

    target_customers = extract_target_customers(text)
    profile_mature = profile.customers[-1] if profile.customers else 0
    customer_scale = 0.0
    if target_customers > 0 and profile_mature > 0:
        customer_scale = target_customers / profile_mature
        customers = [max(0, int(round(value * customer_scale))) for value in customers]
    elif unit_scale > 0:
        customers = [max(0, int(round(value * unit_scale))) for value in customers]
    # The unit ramp drives revenue; for these profiles a "unit" and a
    # "customer" are the same economic entity. When the narrative pins the
    # customer count but states no ARR, scale the unit ramp by the customer
    # factor too — otherwise revenue is computed off the profile-default
    # unit ramp and diverges from the stated customer scale by orders of
    # magnitude. A stated ARR, when present, keeps priority for the units.
    if unit_scale == 0.0 and customer_scale > 0.0:
        units = [max(0, int(round(value * customer_scale))) for value in units]
    return units, customers


def ramp_to_target(target: int, first: int, periods: int = DEFAULT_FORECAST_PERIODS) -> list[int]:
    if periods <= 1:
        return [max(target, 0)]
    if target <= 0:
        return [0 for _ in range(periods)]
    early = [first, max(first * 5, int(target * 0.04)), int(target * 0.10), int(target * 0.25)]
    ramp = _pad_series(early, periods - 1, early[-1])[: periods - 1]
    ramp.append(0)
    ramp[-1] = max(0, target - sum(ramp[:-1]))
    return ramp


# Latin single-letter scale units must not bleed into a following word — a bare
# "t" in "targets" once parsed as "trillion". Require a non-letter boundary.
_GMV_UNIT = r"(兆|億|百万|万|trillion|billion|million|bn|tn|mn|[tTbBmM](?![A-Za-z]))"
_GMV_CJK_UNIT = r"(兆|億|百万|万)"
_GMV_PATTERNS = [
    # Keyword first: require an explicit currency mark so prose like
    # "GMV. Phase 1 targets" cannot be misread as a GMV figure.
    rf"GMV[^0-9¥$]{{0,24}}[¥$]\s*([0-9,.]+)\s*{_GMV_UNIT}?",
    rf"流通総額[^0-9¥$]{{0,24}}¥?\s*([0-9,.]+)\s*{_GMV_CJK_UNIT}",
    # Number first: a scale unit is mandatory so bare prose ("Q2 GMV review")
    # cannot match — the trailing keyword alone is not a strong enough anchor.
    rf"[¥$]?\s*([0-9,.]+)\s*{_GMV_UNIT}\s*(?:の)?\s*GMV",
    rf"[¥$]?\s*([0-9,.]+)\s*{_GMV_CJK_UNIT}\s*(?:の)?\s*流通総額",
]
_GMV_MATURITY_CUE = re.compile(
    r"maturity|at\s+(?:full\s+)?scale|"
    r"by\s*(?:FY)?\s*20\d\d|by\s+year|by\s+(?:the\s+)?end\s+of|"
    r"end\s+of\s+the\s+(?:plan|forecast|horizon|period|model)|final\s+year|"
    r"成熟|目標|までに|時点|最終年",
    flags=re.IGNORECASE,
)


def gmv_ramp(
    text: str,
    profile: MechanicProfile,
    periods: int = DEFAULT_FORECAST_PERIODS,
    money_scale: float = 1.0,
) -> list[int]:
    """Build the GMV ramp for marketplace-style plans.

    Extracts a stated GMV in either order ("GMV ¥10B" or "¥120億 GMV"). When
    the figure sits next to maturity language ("at maturity", "by FY2030"), it
    is treated as the final-period target and the ramp is scaled so the last
    period lands on it — a stated maturity GMV is a goal, not a period-0 base.
    A stated GMV is taken in the model currency as written; only the
    profile-default fallback is FX-scaled.
    """
    if periods <= 0:
        return []
    # A narrative may state both a period-0 base ("¥4B GMV today") and a
    # maturity target ("scaling to ¥120B by the end of the plan"). Scan every
    # GMV figure: one tied to a maturity cue is the final-period target and
    # wins; otherwise the first plain figure is the period-0 base.
    base_value = 0
    maturity_value = 0
    for pattern in _GMV_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            scaled = money_from_match(match)
            if scaled is None or scaled <= 0:
                continue
            context = text[max(0, match.start() - 60): match.end() + 60]
            if _GMV_MATURITY_CUE.search(context):
                maturity_value = max(maturity_value, scaled)
            elif base_value == 0:
                base_value = scaled
    if maturity_value > 0:
        value, is_maturity_figure = maturity_value, True
    elif base_value > 0:
        value, is_maturity_figure = base_value, False
    else:
        value, is_maturity_figure = int(profile.default_gmv_yen * money_scale), False
    if value <= 0:
        return [0 for _ in range(periods)]
    multipliers = _curve(1.0, 8.5, periods)
    if is_maturity_figure:
        final = multipliers[-1] or 1.0
        return [int(value * multiple / final) for multiple in multipliers]
    return [int(value * multiple) for multiple in multipliers]


def ending_units(new_units: list[int]) -> list[int]:
    ending: list[int] = []
    running = 0
    for idx, value in enumerate(new_units):
        churn = int(running * (0.02 + idx * 0.005))
        running = max(0, running + value - churn)
        ending.append(running)
    return ending


def average_units(ending: list[int]) -> list[int]:
    avg: list[int] = []
    prior = 0
    for value in ending:
        avg.append(int((prior + value) / 2))
        prior = value
    return avg


def driver_surfaces_for(facts: SourceFacts) -> tuple[DriverSurface, ...]:
    return (
        DriverSurface("Demand", facts.primary_unit_name, "Assumptions / Revenue Build", "Volume, pricing, capital need", "source + assumption"),
        DriverSurface("Monetization", "Price / take rate / other revenue", "Assumptions / Revenue Build", "Revenue and customer ROI", "source + assumption"),
        DriverSurface("Delivery", "Variable COGS and support load", "Cost Build", "Gross margin and payback", "assumption"),
        DriverSurface("Capacity", "People, capex, working capital", "People Plan / BS / CF", "Runway and operational bottlenecks", "assumption"),
        DriverSurface("Financing", "Equity, debt, cash, ownership", "Capital Stack / Ownership", "Dilution and survivability", "assumption"),
        DriverSurface("Risk", "Scenario and sensitivity", "Scenarios / Sensitivity", "Downside and decision pressure", "model"),
        DriverSurface("Value", "Exit, SOTP, investor return", "Valuation / IC Memo", "Investment judgment", "model"),
    )


def _mechanic_key(facts: SourceFacts) -> str:
    lowered = f"{facts.mechanics} {' '.join(facts.segments)}".lower()
    signals = {
        "marketplace": ("marketplace", "transaction", "gmv", "liquidity", "two-sided"),
        "hardware_asset_heavy": ("hardware", "asset", "equipment", "robot", "lease", "deployed"),
        "fintech_balance_sheet": ("fintech", "balance", "loan", "lending", "credit", "warehouse"),
        "pre_revenue_milestone": ("proof", "pre-revenue", "milestone", "prototype", "grant"),
        "recurring_software": ("software", "recurring", "saas", "subscription", "arr"),
    }
    scores = {key: sum(1 for token in tokens if token in lowered) for key, tokens in signals.items()}
    strongest = max(scores.values())
    if strongest <= 0:
        return "generic"
    winners = [key for key, score in scores.items() if score == strongest]
    if len(winners) > 1:
        return "generic"
    return winners[0]


def mechanic_key(facts: SourceFacts) -> str:
    """Public accessor for the detected business-mechanic key.

    Returns one of ``marketplace``, ``hardware_asset_heavy``,
    ``fintech_balance_sheet``, ``pre_revenue_milestone``,
    ``recurring_software``, or ``generic``. Renderers use it to gate
    profile-specific surfaces without reaching into a private helper.
    """
    return _mechanic_key(facts)


def scenario_drivers_for(facts: SourceFacts) -> tuple[ScenarioDriver, ...]:
    key = _mechanic_key(facts)
    registry = {
        "marketplace": (
            ScenarioDriver("GMV / liquidity scale", "x", 0.65, 1.00, 1.35, "buyer/seller liquidity evidence is weakest", "net revenue and contribution margin", "liquidity or repeat rate misses plan", "tighten wedge, incentives, or funding plan"),
            ScenarioDriver("Take-rate / pricing scale", "x", 0.85, 1.00, 1.12, "monetization may pressure marketplace liquidity", "net revenue and NRR quality", "take rate cannot hold without churn", "reprice, bundle, or change value capture"),
            ScenarioDriver("Incentive / loss factor", "x", 1.30, 1.00, 0.80, "incentives, payment fees, or fraud can absorb gross profit", "gross margin and burn", "contribution margin turns negative", "validate unit economics by cohort"),
            ScenarioDriver("Working-capital factor", "x", 1.20, 1.00, 0.85, "cash timing may diverge from GMV growth", "runway and funding gap", "cash conversion absorbs raise", "change settlement, advances, or debt plan"),
        ),
        "hardware_asset_heavy": (
            ScenarioDriver("Deployment capacity scale", "x", 0.65, 1.00, 1.30, "manufacturing or field deployment constrains growth", "revenue, capex, and runway", "units ship below milestone", "phase rollout or add capacity financing"),
            ScenarioDriver("Utilization / pricing scale", "x", 0.85, 1.00, 1.15, "asset ROI depends on utilization and price capture", "revenue and payback", "payback exceeds funding window", "validate customer ROI and pricing"),
            ScenarioDriver("BOM / service cost factor", "x", 1.25, 1.00, 0.85, "hardware/service cost evidence is often thin", "gross margin and capex intensity", "margin falls below target", "lock BOM, warranty, and service data"),
            ScenarioDriver("Lease/debt availability", "x", 0.70, 1.00, 1.25, "non-dilutive capacity may be unavailable in downside", "funding gap and dilution", "debt/lease headroom fails", "resize equity round or asset plan"),
        ),
        "fintech_balance_sheet": (
            ScenarioDriver("Origination scale", "x", 0.70, 1.00, 1.25, "demand and underwriting capacity may diverge", "revenue and capital need", "origination below cost base", "tighten ICP and credit box"),
            ScenarioDriver("Spread / pricing scale", "x", 0.85, 1.00, 1.10, "pricing may not offset funding cost", "gross profit and valuation", "spread compression", "reprice, hedge, or reduce growth"),
            ScenarioDriver("Loss / collection factor", "x", 1.35, 1.00, 0.80, "loss and collection evidence drives survivability", "cash, runway, and covenants", "losses breach headroom", "validate cohorts before scaling"),
            ScenarioDriver("Warehouse / debt headroom", "x", 0.70, 1.00, 1.20, "balance-sheet growth depends on committed funding", "funding gap and dilution", "warehouse capacity unavailable", "slow originations or raise equity"),
        ),
        "pre_revenue_milestone": (
            ScenarioDriver("Milestone timing scale", "x", 0.65, 1.00, 1.20, "proof points may slip before commercial revenue", "cash-out date and next round", "milestone slips beyond runway", "reduce scope or raise bridge"),
            ScenarioDriver("Prototype / program cost factor", "x", 1.30, 1.00, 0.85, "R&D and prototype cost evidence is thin", "burn and funding gap", "cost overrun consumes buffer", "add contingency and vendor proof"),
            ScenarioDriver("Grant / non-dilutive coverage", "x", 0.70, 1.00, 1.25, "non-dilutive funding may not arrive on time", "equity need and dilution", "coverage below target", "replace with bridge or equity"),
            ScenarioDriver("Hiring capacity scale", "x", 0.80, 1.00, 1.20, "execution depends on recruiting scarce talent", "milestone delivery and burn", "critical hires slip", "sequence hires to proof points"),
        ),
        "recurring_software": (
            ScenarioDriver("New logo / conversion scale", "x", 0.70, 1.00, 1.30, "pipeline conversion drives ARR", "ARR, burn multiple, and runway", "sales capacity misses plan", "revise GTM capacity or spend"),
            ScenarioDriver("ACV / expansion scale", "x", 0.85, 1.00, 1.15, "pricing and expansion quality drive NRR", "ARR and valuation quality", "expansion below benchmark", "validate packaging and customer ROI"),
            ScenarioDriver("Churn / retention factor", "x", 1.30, 1.00, 0.80, "retention is often the hardest evidence gap", "NRR, LTV, and valuation", "churn breaks payback", "cohort retention DD before scaling"),
            ScenarioDriver("CAC / sales capacity factor", "x", 1.20, 1.00, 0.85, "sales efficiency controls funding need", "burn multiple and payback", "payback exceeds cash window", "rebalance GTM mix"),
        ),
        "generic": (
            ScenarioDriver("Demand evidence scale", "x", 0.70, 1.00, 1.25, "demand proof is not yet tied to one mechanic", "revenue, burn, and runway", "demand evidence fails to support plan", "clarify economic unit before scaling spend"),
            ScenarioDriver("Value capture scale", "x", 0.85, 1.00, 1.15, "pricing or monetization route remains uncertain", "gross profit and valuation support", "value capture lacks customer proof", "validate willingness-to-pay or monetization path"),
            ScenarioDriver("Cost-to-serve factor", "x", 1.25, 1.00, 0.85, "delivery burden may be understated", "gross margin and burn", "unit economics fail under service load", "decompose cost stack and operating capacity"),
            ScenarioDriver("Financing capacity scale", "x", 0.75, 1.00, 1.20, "capital availability depends on unresolved proof points", "funding gap and dilution", "financing need exceeds credible capacity", "reset milestone scope or capital plan"),
        ),
    }
    return registry.get(key, registry["generic"])


def kpi_definitions_for(facts: SourceFacts) -> tuple[KPIDefinition, ...]:
    common = [
        KPIDefinition("Runway", "CF ending cash / burn", "cash survival matters", "cash forecast / financing terms", "below target runway", "round timing or burn reset"),
        KPIDefinition("Burn multiple", "net burn / net new revenue", "funding efficiency matters", "cash flow and revenue ramp", "burn not justified by growth", "capital efficiency and round size"),
        KPIDefinition("Funding coverage", "committed financing / cash need", "raise sizing is a decision", "capital stack and milestone plan", "coverage below target", "round size, bridge, or debt plan"),
        KPIDefinition("Evidence coverage", "support status across material drivers", "source quality is uneven", "benchmark/source register", "material driver remains unknown", "prioritize DD before circulation"),
    ]
    key = _mechanic_key(facts)
    registry = {
        "marketplace": (
            KPIDefinition("Take rate", "net revenue / GMV", "transaction monetization is central", "transaction and pricing proof", "take rate weakens liquidity", "pricing and incentive DD"),
            KPIDefinition("Contribution margin", "gross profit after incentives/losses", "subsidies or fraud matter", "payment, incentive, fraud evidence", "contribution margin negative", "cohort unit economics DD"),
            KPIDefinition("Repeat / liquidity quality", "repeat rate and GMV growth", "network health drives scale", "cohort behavior", "repeat behavior below threshold", "wedge or supply/demand focus"),
        ),
        "hardware_asset_heavy": (
            KPIDefinition("Deployment capacity", "units deployed / capacity", "physical rollout drives revenue", "manufacturing/deployment evidence", "capacity below unit plan", "capacity financing or phasing"),
            KPIDefinition("Asset payback", "capex per unit / unit gross profit", "assets consume cash", "BOM, service, utilization evidence", "payback beyond funding window", "lease/debt and pricing DD"),
            KPIDefinition("Service burden", "support workload / Ops-CS capacity", "service quality affects margins", "ticket and field-service evidence", "coverage below 1.0x", "support model or warranty DD"),
        ),
        "fintech_balance_sheet": (
            KPIDefinition("Loss / collection quality", "loss and collection assumptions", "credit risk drives value", "cohort loss evidence", "losses exceed spread", "credit and collections DD"),
            KPIDefinition("Funding spread", "yield minus funding cost", "warehouse funding drives economics", "debt terms and origination data", "spread compression", "funding partner or pricing DD"),
            KPIDefinition("Debt / warehouse headroom", "debt capacity / originations", "growth depends on balance sheet", "capital stack evidence", "capacity below plan", "slow growth or raise equity"),
        ),
        "pre_revenue_milestone": (
            KPIDefinition("Milestone runway", "cash runway vs proof-point timing", "revenue proof is ahead", "technical roadmap and burn", "runway ends before proof", "scope, bridge, or hiring reset"),
            KPIDefinition("Prototype cost variance", "selected cost vs implied cost", "R&D cost evidence is thin", "vendor and team estimates", "cost overrun consumes buffer", "contingency and vendor DD"),
            KPIDefinition("Non-dilutive coverage", "grants/advances / milestone spend", "funding mix changes dilution", "grant/customer advance status", "coverage slips", "replace with equity or convert"),
        ),
        "recurring_software": (
            KPIDefinition("Net retention", "opening ARR + expansion - churn", "recurring revenue quality matters", "cohort behavior", "NRR below target", "retention and expansion DD"),
            KPIDefinition("CAC payback", "CAC / gross profit from new ARR", "GTM spend drives burn", "sales cycle and CAC evidence", "payback beyond cash window", "GTM mix or pricing reset"),
            KPIDefinition("Sales efficiency", "new ARR / sales and marketing spend", "growth efficiency matters", "GTM capacity", "efficiency below benchmark", "quota and channel DD"),
        ),
        "generic": (
            KPIDefinition("Economic unit clarity", "selected unit and value flow", "mechanic is ambiguous", "driver tree and source facts", "unit cannot be traced to cash", "model design or DD before forecast"),
            KPIDefinition("Unit margin support", "price/value capture minus cost-to-serve", "unit economics must be credible", "pricing, cost, and support evidence", "margin depends on unsupported default", "decompose pricing and cost stack"),
            KPIDefinition("Proof-point coverage", "runway and funding vs required evidence", "funding should buy evidence", "milestone and capital plan", "proof point slips beyond runway", "resize scope, round, or validation plan"),
        ),
    }
    return tuple(common + list(registry.get(key, registry["generic"])))


def extract_target_gross_margin(text: str) -> float | None:
    """Extract a stated/target gross margin from the narrative, if present.

    Returns a fraction in (0, 1) or None when the narrative gives no figure.
    Recognises English ("gross margin ... 78%", "78% gross margin") and
    Japanese ("粗利率 78%", "売上総利益率 78%") phrasings.
    """
    # The gap windows are wide enough for a qualifying clause ("gross margin
    # on the subscription is about 82%"); `[^0-9%]` keeps any intervening
    # number out, so a wide window cannot capture an unrelated percentage.
    patterns = [
        r"gross\s*margin[^0-9%]{0,44}([0-9]{1,2}(?:\.[0-9])?)\s*%",
        r"([0-9]{1,2}(?:\.[0-9])?)\s*%[^0-9%]{0,32}gross\s*margin",
        r"粗利率?[^0-9%]{0,20}([0-9]{1,2}(?:\.[0-9])?)\s*%",
        r"売上総利益率[^0-9%]{0,20}([0-9]{1,2}(?:\.[0-9])?)\s*%",
    ]
    pct = first_match_float(patterns, text, -1.0)
    if 0.0 < pct < 100.0:
        return round(pct / 100.0, 4)
    return None


# Employee / workforce churn is an HR metric, not the customer-retention
# rate the model wants.
_HR_CHURN_CUE = re.compile(
    r"(?:employee|staff|workforce|team|talent|personnel)\s+"
    r"(?:churn|attrition|turnover)",
    flags=re.IGNORECASE,
)
# "monthly" only annualizes when it is syntactically tied to the churn
# phrase — "monthly churn", "churn ... per month" — not an unrelated
# "monthly price" sentence sitting near a churn figure.
_MONTHLY_CHURN_CUE = re.compile(
    r"(?:monthly|per[-\s]month|/\s*mo\b|月次|月間|毎月)\s*"
    r"(?:logo\s+|customer\s+|net\s+)?churn"
    r"|churn[^.\n]{0,20}?(?:per[-\s]month|monthly|/\s*mo\b)",
    flags=re.IGNORECASE,
)


def extract_churn_rate(text: str) -> float | None:
    """Stated customer / logo churn as an annual fraction.

    A monthly churn figure is annualized by compounding
    (1 - (1 - monthly)^12). An employee / workforce churn mention is
    skipped — it is not the customer-retention metric. Returns None when
    no customer-churn figure is stated.
    """
    for pattern in (
        r"churn[^0-9%\n]{0,24}?([0-9]{1,2}(?:\.[0-9])?)\s*%",
        r"([0-9]{1,2}(?:\.[0-9])?)\s*%[^0-9%.\n]{0,28}?churn",
    ):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            window = text[max(0, match.start() - 24): match.end() + 24]
            if _HR_CHURN_CUE.search(window):
                continue  # an employee-churn mention — not the retention rate
            try:
                pct = float(match.group(1)) / 100.0
            except ValueError:
                continue
            if not 0.0 < pct < 1.0:
                continue
            if _MONTHLY_CHURN_CUE.search(window):
                pct = 1.0 - (1.0 - pct) ** 12
            return round(pct, 4)
    return None


def _profile_target_gross_margin(profile: MechanicProfile, periods: int) -> list[float]:
    base = (
        0.55
        if profile.key == "hardware_asset_heavy"
        else 0.72
        if profile.key == "recurring_software"
        else 0.60
    )
    return [base for _ in range(periods)]


def resolve_target_gross_margin(
    text: str, profile: MechanicProfile, periods: int
) -> list[float]:
    """Resolve the target gross-margin series: stated narrative figure wins."""
    stated = extract_target_gross_margin(text)
    if stated is not None:
        clamped = min(max(stated, 0.05), 0.95)
        return [clamped for _ in range(periods)]
    return _profile_target_gross_margin(profile, periods)


def calibrate_cost_stack_to_gross_margin(
    target_gross_margin: list[float],
    new_units: list[int],
    gmv_yen: list[int],
    monthly_price_yen: list[int],
    take_rate: list[float],
    customers: list[int],
    other_revenue_share: list[float],
    variable_cogs_pct: list[float],
    delivery_cost_yen: list[int],
    cloud_cost_yen: list[int],
    support_cost_yen: list[int],
    revenue_mode: str = "recurring",
) -> tuple[list[float], list[int], list[int], list[int]]:
    """Gross-margin governor.

    The cost-to-serve drivers (variable COGS %, delivery, cloud, support) come
    from sector profiles and are calibrated for a specific price point. Applied
    unchanged to an out-of-profile price (e.g. a ¥90k/unit hardware delivery
    cost on a ¥12k SaaS seat) they produce nonsense gross margins.

    This governor rescales the four cost components by one per-period factor so
    that total COGS lands on (1 - target gross margin) x revenue, using the same
    revenue and COGS arithmetic as the workbook formulas. Scaling all four
    proportionally preserves the profile's intended cost *mix* while fixing its
    *level*; each component still reads as an honest decomposition of COGS.
    """
    ending = ending_units(new_units)
    average = average_units(ending)
    vc_out: list[float] = []
    delivery_out: list[int] = []
    cloud_out: list[int] = []
    support_out: list[int] = []
    for idx in range(len(target_gross_margin)):
        subtotal = _period_subtotal_revenue(
            idx, new_units, average, gmv_yen, monthly_price_yen,
            take_rate, revenue_mode,
        )
        revenue = subtotal * (1.0 + other_revenue_share[idx])
        variable = revenue * variable_cogs_pct[idx]
        # Field-service cost accrues on deployed units every period (post-sale
        # maintenance), independent of the revenue model.
        delivery = average[idx] * delivery_cost_yen[idx] * 12
        cloud = average[idx] * cloud_cost_yen[idx] * 12
        support = customers[idx] * support_cost_yen[idx] * 12
        base_cogs = variable + delivery + cloud + support
        gross_margin = min(max(target_gross_margin[idx], 0.05), 0.95)
        target_cogs = (1.0 - gross_margin) * revenue
        if revenue <= 0 or base_cogs <= 0:
            vc_out.append(variable_cogs_pct[idx])
            delivery_out.append(delivery_cost_yen[idx])
            cloud_out.append(cloud_cost_yen[idx])
            support_out.append(support_cost_yen[idx])
            continue
        scale = target_cogs / base_cogs
        vc_out.append(round(variable_cogs_pct[idx] * scale, 6))
        delivery_out.append(int(round(delivery_cost_yen[idx] * scale)))
        cloud_out.append(int(round(cloud_cost_yen[idx] * scale)))
        support_out.append(int(round(support_cost_yen[idx] * scale)))
    return vc_out, delivery_out, cloud_out, support_out


def _period_subtotal_revenue(
    idx: int,
    new_units: list[int],
    average: list[int],
    gmv_yen: list[int],
    monthly_price_yen: list[int],
    take_rate: list[float],
    revenue_mode: str,
) -> float:
    """Pre-`other revenue` subtotal for one period, by revenue model.

    `unit_sale` (hardware): the price is a one-time per-unit sale price, so
    revenue is new units shipped x price — no recurring billing on the
    installed base. `recurring` (default): transaction take + a monthly
    subscription billed on the installed base + a one-time onboarding fee.
    """
    if revenue_mode == "unit_sale":
        return new_units[idx] * monthly_price_yen[idx]
    transaction = gmv_yen[idx] * take_rate[idx]
    recurring = average[idx] * monthly_price_yen[idx] * 12
    one_time = new_units[idx] * monthly_price_yen[idx] * 3
    return transaction + recurring + one_time


def plan_revenue_series(
    new_units: list[int],
    gmv_yen: list[int],
    monthly_price_yen: list[int],
    take_rate: list[float],
    other_revenue_share: list[float],
    revenue_mode: str = "recurring",
) -> list[float]:
    """Per-period total revenue, mirroring the Revenue Build sheet formulas."""
    average = average_units(ending_units(new_units))
    revenue: list[float] = []
    for idx in range(len(new_units)):
        subtotal = _period_subtotal_revenue(
            idx, new_units, average, gmv_yen, monthly_price_yen,
            take_rate, revenue_mode,
        )
        revenue.append(subtotal * (1.0 + other_revenue_share[idx]))
    return revenue


def project_free_cash_flow(
    revenue: list[float],
    target_gross_margin: list[float],
    total_headcount: list[int],
    avg_comp_yen: list[int],
    product_headcount: list[int],
    sm_pct_revenue: list[float],
    rd_program_per_product_fte_yen: list[int],
    rd_program_floor_yen: list[int],
    ga_pct_revenue: list[float],
    fixed_ga_yen: list[int],
    capex_yen: list[int],
    depreciation_life_months: list[int],
    debt_raise_yen: list[int],
    debt_interest_rate: list[float],
    ar_days: list[int],
    ap_days: list[int],
    deferred_revenue_share: list[float],
    inventory_wip_pct_capex: list[float],
    tax_rate: list[float],
) -> list[dict]:
    """Project per-period free cash flow, mirroring the P&L / BS / CF sheets.

    Used to size the funding plan against real projected burn rather than a
    fixed heuristic. Equity financing is intentionally excluded — it does not
    feed operating cash flow (no interest-on-cash is modeled), which keeps
    round sizing a non-circular forward walk.

    Depreciation mirrors the workbook P&L formula: straight-line on the
    accumulated asset base — gross PP&E (cumulative CapEx) divided by the
    depreciation life — capped so accumulated depreciation never exceeds gross
    PP&E. It is cash-flow neutral here (D&A is added back in operating cash
    flow), so it does not change funding sizing; it sharpens EBIT, net income,
    accumulated depreciation, and net PP&E.
    """
    periods = len(revenue)
    out: list[dict] = []
    ar_prev = inventory_prev = ap_deferred_prev = 0.0
    debt_balance = 0.0
    cumulative_capex = accumulated_da = 0.0
    for idx in range(periods):
        cogs = revenue[idx] * (1.0 - target_gross_margin[idx])
        gross_profit = revenue[idx] - cogs
        people = total_headcount[idx] * avg_comp_yen[idx]
        sales_marketing = revenue[idx] * sm_pct_revenue[idx]
        rd = max(
            rd_program_floor_yen[idx],
            product_headcount[idx] * rd_program_per_product_fte_yen[idx],
        )
        ga = revenue[idx] * ga_pct_revenue[idx] + fixed_ga_yen[idx]
        opex = people + sales_marketing + rd + ga
        ebitda = gross_profit - opex
        life = depreciation_life_months[idx] or 60
        cumulative_capex += capex_yen[idx]
        depreciation = min(
            cumulative_capex * 12.0 / life, cumulative_capex - accumulated_da
        )
        accumulated_da += depreciation
        ebit = ebitda - depreciation
        debt_balance += debt_raise_yen[idx]
        interest = debt_balance * debt_interest_rate[idx]
        ebt = ebit - interest
        tax = max(0.0, ebt * tax_rate[idx])
        net_income = ebt - tax
        accounts_receivable = revenue[idx] * ar_days[idx] / 365
        inventory = capex_yen[idx] * inventory_wip_pct_capex[idx]
        ap_deferred = (
            cogs * ap_days[idx] / 365 + revenue[idx] * deferred_revenue_share[idx]
        )
        working_capital = (
            (ar_prev - accounts_receivable)
            + (inventory_prev - inventory)
            + (ap_deferred - ap_deferred_prev)
        )
        operating_cf = net_income + depreciation + working_capital
        free_cash_flow = operating_cf - capex_yen[idx]
        ar_prev, inventory_prev, ap_deferred_prev = (
            accounts_receivable,
            inventory,
            ap_deferred,
        )
        out.append(
            {
                "revenue": revenue[idx],
                "cogs": cogs,
                "gross_margin": gross_profit / revenue[idx] if revenue[idx] else 0.0,
                "ebitda": ebitda,
                "net_income": net_income,
                "depreciation": depreciation,
                "free_cash_flow": free_cash_flow,
                "capex": capex_yen[idx],
                "accounts_receivable": accounts_receivable,
                "inventory": inventory,
                "ap_deferred": ap_deferred,
            }
        )
    return out


def size_equity_rounds(
    beginning_cash_yen: int,
    free_cash_flow: list[float],
    debt_raise_yen: list[int],
    target_runway_months: int = 12,
    round_unit: int = 100_000_000,
    stated_first_round: int | None = None,
) -> list[int]:
    """Size each period's equity round so projected ending cash stays solvent.

    Walks the cash balance forward; whenever cash before equity would fall
    below a runway buffer (``target_runway_months`` of the period's own burn),
    the round is topped up — rounded up to ``round_unit`` — to clear it. The
    final period keeps a half-period cushion: there is no successor round to
    fund, but ending the horizon at exactly zero cash is not investor-grade.

    When the narrative states the first round's size, ``stated_first_round``
    is used for period 0 exactly as given — the user's fundraising terms are
    honored, not overridden. Follow-on rounds are still auto-sized; if the
    stated raise is too small the next period carries the shortfall, which is
    the honest outcome to surface.
    """
    periods = len(free_cash_flow)
    equity: list[int] = []
    cash = float(beginning_cash_yen)
    for idx in range(periods):
        cash_before_equity = cash + free_cash_flow[idx] + debt_raise_yen[idx]
        if idx == 0 and stated_first_round is not None:
            raised: int = int(stated_first_round)
        else:
            burn = max(0.0, -free_cash_flow[idx])
            runway_factor = (
                target_runway_months / 12.0 if idx < periods - 1 else 0.5
            )
            buffer = burn * runway_factor
            shortfall = buffer - cash_before_equity
            raised = (
                math.ceil(shortfall / round_unit) * round_unit
                if shortfall > 0 else 0
            )
        equity.append(int(raised))
        cash = cash_before_equity + raised
    return equity


def project_plan_free_cash_flow(facts: SourceFacts) -> list[dict]:
    """Project free cash flow and ending cash for a fully built plan.

    Mirrors the workbook P&L / BS / CF chain. Ending cash adds equity and
    debt financing to free cash flow; generic source plans carry no other
    financing instruments, so those terms are omitted.
    """
    revenue = plan_revenue_series(
        facts.new_units,
        facts.gmv_yen,
        facts.monthly_price_yen,
        facts.take_rate,
        facts.other_revenue_share,
        facts.revenue_mode,
    )
    total_headcount = [
        facts.product_headcount[i]
        + facts.gtm_headcount[i]
        + facts.operations_headcount[i]
        + facts.ga_headcount[i]
        for i in range(len(revenue))
    ]
    capex = [
        facts.new_units[i] * facts.capex_per_unit_yen[i] + facts.other_capex_yen[i]
        for i in range(len(revenue))
    ]
    projection = project_free_cash_flow(
        revenue,
        facts.target_gross_margin,
        total_headcount,
        facts.avg_comp_yen,
        facts.product_headcount,
        facts.sm_pct_revenue,
        facts.rd_program_per_product_fte_yen,
        facts.rd_program_floor_yen,
        facts.ga_pct_revenue,
        facts.fixed_ga_yen,
        capex,
        facts.depreciation_life_months,
        facts.debt_raise_yen,
        facts.debt_interest_rate,
        facts.ar_days,
        facts.ap_days,
        facts.deferred_revenue_share,
        facts.inventory_wip_pct_capex,
        facts.tax_rate,
    )
    cash = float(facts.beginning_cash_yen)
    for idx, period in enumerate(projection):
        cash += (
            period["free_cash_flow"]
            + facts.debt_raise_yen[idx]
            + facts.equity_raise_yen[idx]
        )
        period["ending_cash"] = cash
    return projection


def project_balance_sheet(facts: SourceFacts) -> list[dict]:
    """Project the per-period balance sheet and its A = L + E check.

    Mirrors the workbook BS sheet: cash and working capital roll forward from
    the same projection that drives free cash flow, PP&E and accumulated D&A
    accumulate capex and depreciation, paid-in capital accumulates equity, and
    retained earnings accumulate net income. `balance_check` is total assets
    minus total liabilities minus total equity; a coherent plan keeps it at
    zero every period.
    """
    projection = project_plan_free_cash_flow(facts)
    rows: list[dict] = []
    gross_ppe = accumulated_da = 0.0
    debt_balance = 0.0
    paid_in_capital = float(facts.beginning_cash_yen)
    retained_earnings = 0.0
    for idx, period in enumerate(projection):
        gross_ppe += period["capex"]
        accumulated_da += period["depreciation"]
        debt_balance += facts.debt_raise_yen[idx]
        paid_in_capital += facts.equity_raise_yen[idx]
        retained_earnings += period["net_income"]
        total_assets = (
            period["ending_cash"]
            + period["accounts_receivable"]
            + period["inventory"]
            + (gross_ppe - accumulated_da)
        )
        total_liabilities = period["ap_deferred"] + debt_balance
        total_equity = paid_in_capital + retained_earnings
        rows.append(
            {
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity,
                "balance_check": total_assets - total_liabilities - total_equity,
            }
        )
    return rows


def implied_gross_margin_series(facts: SourceFacts) -> list[float]:
    """Per-period gross margin implied by the calibrated cost drivers.

    Mirrors the workbook's Cost Build COGS (variable % plus per-unit delivery,
    cloud, and support) so a coherence check can verify the cost stack actually
    delivers the target margin — independently of the FCF projection, which
    takes `(1 - target margin)` as a shortcut.
    """
    revenue = plan_revenue_series(
        facts.new_units,
        facts.gmv_yen,
        facts.monthly_price_yen,
        facts.take_rate,
        facts.other_revenue_share,
        facts.revenue_mode,
    )
    ending = ending_units(facts.new_units)
    average = average_units(ending)
    margins: list[float] = []
    for idx in range(len(revenue)):
        rev = revenue[idx]
        if rev <= 0:
            margins.append(0.0)
            continue
        variable = rev * facts.variable_cogs_pct[idx]
        # Field-service cost accrues on deployed units every period (post-sale
        # maintenance), independent of the revenue model.
        delivery = average[idx] * facts.delivery_cost_yen[idx] * 12
        cloud = average[idx] * facts.cloud_cost_yen[idx] * 12
        support = facts.customers[idx] * facts.support_cost_yen[idx] * 12
        margins.append((rev - (variable + delivery + cloud + support)) / rev)
    return margins


def audit_economic_coherence(
    facts: SourceFacts, *, gross_margin_tolerance: float = 0.03
) -> list[str]:
    """Profile-agnostic economic-coherence audit for a generated plan.

    Structural workbook audits (omitted-sheet references, fonts, merged cells)
    do not catch a plan whose *economics* are broken — a -789% gross margin, a
    plan that runs cash-negative, a zero-revenue forecast. This generalizes
    that whole class of failure into one reusable gate that holds for any
    sector profile or output mode: it replays the kernel's own revenue, cost,
    and cash projection and returns human-readable violations. An empty list
    means the plan is economically coherent.
    """
    issues: list[str] = []
    labels = facts.period_labels
    revenue = plan_revenue_series(
        facts.new_units,
        facts.gmv_yen,
        facts.monthly_price_yen,
        facts.take_rate,
        facts.other_revenue_share,
        facts.revenue_mode,
    )
    gross_margin = implied_gross_margin_series(facts)
    projection = project_plan_free_cash_flow(facts)

    def _label(idx: int) -> str:
        return labels[idx] if idx < len(labels) else f"period {idx}"

    # Read the profile from `facts.mechanics`, which `derive_source_facts`
    # stamps from `profile.label` — the same profile object whose `.key`
    # drove the revenue-zeroing decision. Re-deriving via `_mechanic_key`
    # would traverse a separate keyword set that can diverge on edge cases.
    is_pre_revenue = facts.mechanics == _profile("pre_revenue_milestone").label
    for idx in range(len(revenue)):
        if revenue[idx] <= 0:
            # A pre-revenue / milestone plan legitimately carries zero product
            # revenue; for any other profile a non-positive period is a
            # coherence failure.
            if not is_pre_revenue:
                issues.append(
                    f"{_label(idx)}: non-positive revenue ({revenue[idx]:,.0f})"
                )
            continue
        target = (
            facts.target_gross_margin[idx]
            if idx < len(facts.target_gross_margin)
            else 0.0
        )
        if abs(gross_margin[idx] - target) > gross_margin_tolerance:
            detail = " (negative)" if gross_margin[idx] < 0 else ""
            issues.append(
                f"{_label(idx)}: cost stack implies gross margin "
                f"{gross_margin[idx]:.1%}{detail}, off target {target:.1%}"
            )

    for idx, period in enumerate(projection):
        if period["ending_cash"] < 0:
            issues.append(
                f"{_label(idx)}: projected insolvency "
                f"(ending cash {period['ending_cash']:,.0f})"
            )

    # Three-statement integrity: the balance sheet must balance every period.
    for idx, period in enumerate(project_balance_sheet(facts)):
        scale = max(1.0, abs(period["total_assets"]))
        if abs(period["balance_check"]) > 1e-4 * scale:
            issues.append(
                f"{_label(idx)}: balance sheet does not balance "
                f"(A - L - E = {period['balance_check']:,.0f})"
            )

    if not facts.equity_raise_yen or facts.equity_raise_yen[0] <= 0:
        issues.append(f"{_label(0)}: no funding round sized for the first period")
    return issues


def extract_source_facts(source_md: Path) -> SourceFacts:
    return derive_source_facts(read_source(source_md))


# Asset-heavy hardware spans two revenue models: outright unit sales and
# recurring leasing / robot-as-a-service.
#
# A strong sale cue names an unambiguous one-time sale ("sells for $X"); it
# establishes a unit-sale business on its own — a mention of attach revenue
# (a support subscription) does not override it. An ambiguous unit-price cue
# ("unit price") could be a monthly rate, so it yields unit_sale only when no
# recurring cue competes. A recurring cue (lease, RaaS, 月額, ARR, ...) is the
# default model.
# `sells/sold for` is an unambiguous one-time sale. `sold/sells at` is left
# out of the strong set — "sold at a monthly rate" is recurring — and lands
# in the ambiguous set, which defers to the recurring-cue check.
_STRONG_SALE_CUE = re.compile(
    r"(?:sells?|sold)\s+for|sale\s+price|販売価格",
    flags=re.IGNORECASE,
)
_UNIT_PRICE_CUE = re.compile(
    r"unit\s+price|price\s+per\s+"
    r"(?:unit|robot|device|machine|vehicle|drone)|per-unit\s+price|"
    r"(?:sells?|sold)\s+at|1\s*台\s*あたり",
    flags=re.IGNORECASE,
)
_RECURRING_CUE = re.compile(
    r"recurring|leas(?:e|ing)|subscription|RaaS|as\s+a\s+service|"
    r"monthly\s+(?:fee|charge|billing|subscription|price|rate|lease|rental)|"
    r"per\s+month|/\s*mo(?:nth)?\b|"
    r"\bARR\b|\bMRR\b|月額|リース|サブスク",
    flags=re.IGNORECASE,
)


def detect_revenue_mode(text: str, profile: MechanicProfile) -> str:
    """Revenue-recognition model for the plan.

    Asset-heavy hardware is sold outright in some plans and leased / offered
    as a service in others. A strong one-time sale cue makes it ``unit_sale``
    outright; an ambiguous unit-price cue makes it ``unit_sale`` only when no
    recurring cue competes. Every other plan stays ``recurring``.
    """
    if profile.key != "hardware_asset_heavy":
        return "recurring"
    if _STRONG_SALE_CUE.search(text):
        return "unit_sale"
    if _UNIT_PRICE_CUE.search(text) and not _RECURRING_CUE.search(text):
        return "unit_sale"
    return "recurring"


@dataclass
class SourcePrimitives:
    """The *primitive drivers* of a plan, before any quantity is derived.

    `derive_source_facts` once interleaved primitive extraction (regex parses
    of the narrative) with derivation (ramps, gmv, cost-stack calibration,
    funding sizing, ...). That made the structured `--input` path impossible
    to do cleanly: it could only shallow-merge YAML values onto an already
    fully-derived SourceFacts, leaving every derived quantity stale relative
    to the structured drivers.

    Splitting the two lets a structured input override the primitives *before*
    derivation runs, so gmv / take_rate / new_units / cost calibration /
    funding all see the structured drivers. `_extract_source_primitives`
    produces this from narrative text; `derive_source_facts_from_mapping`
    produces it from narrative text and then overrides it with the structured
    YAML values; `_derive_facts_from_primitives` turns either into a full
    SourceFacts.

    The mutable fields are exactly the drivers a structured input may state.
    `text` is retained because a few derivation steps (demand retargeting,
    R&D-headcount anchoring) still parse the narrative for *scale anchors*;
    when a structured input pins the demand ramp those anchors are bypassed.
    """

    text: str
    jpy_per_usd: float
    grain: str
    periods: int
    years: list[int]
    period_labels: list[str]
    profile: MechanicProfile
    revenue_mode: str
    company: str
    currency: str
    source_names: list[str]
    source_urls: list[str]
    market_lines: list[Any]
    segments: list[str]
    source_unknowns: list[str]
    # Demand / monetization drivers. The monetization quantities are carried
    # as full per-period series: a structured input that states an explicit
    # `monthly_price_yen` / `take_rate` series must land exactly, not be
    # re-ramped from a scalar.
    new_units: list[int]
    customers: list[int]
    price: int
    take: float
    gmv: list[int]
    monthly_price: list[int]
    take_rate: list[float]
    target_gross_margin: list[float]
    money_scale: float
    # Capital / people drivers that feed the free-cash-flow projection and
    # funding sizing. Carried as series so a structured input flows through.
    capex_per_unit: list[int]
    avg_comp: list[int]
    variable_cogs_pct: list[float]
    delivery_cost: list[int]
    cloud_cost: list[int]
    support_cost: list[int]
    beginning_cash: int | None = None
    # True when the demand ramp is pinned by a structured input, so the
    # narrative-scale retargeting step must not rescale it.
    demand_pinned: bool = False
    # Stated financing inputs honored as-is during derivation. ``None`` means
    # "derive it"; a value means "use this stated input".
    stated_first_round: int | None = None
    stated_post_money: int | None = None
    stated_churn: float | None = None
    stated_rd_headcount: int = 0


def _extract_source_primitives(
    text: str, *, jpy_per_usd: float = DEFAULT_JPY_PER_USD
) -> SourcePrimitives:
    """Parse the *primitive drivers* of a plan from narrative text.

    This is step (a) of derivation: only regex extraction, no derived
    quantities. `derive_source_facts` runs this then `_derive_facts_from_primitives`;
    the structured `--input` path runs this, overrides the primitives with the
    YAML values, then derives — so the structured drivers reach the pipeline.
    """
    grain = extract_model_grain(text)
    periods = extract_forecast_periods(text, grain)
    years, period_labels = forecast_axis(extract_start_year(text), periods, grain)
    periods = len(years)
    profile = profile_for_text(text)
    revenue_mode = detect_revenue_mode(text, profile)
    company = extract_company(text)
    source_names, source_urls = extract_sources(text)
    market_lines = extract_market_lines(text)
    segments = extract_segments(text)
    currency = extract_currency(text)
    money_scale = money_scale_for_currency(currency, jpy_per_usd)
    if profile.key == "hardware_asset_heavy":
        target_units = extract_target_units(text, profile)
        new_units = ramp_to_target(target_units, profile.first_units, periods)
    else:
        new_units = ramp_to_target(profile.customers[-1], max(25, profile.customers[0]), periods)
    customers = _pad_series(profile.customers, periods, 0)
    gmv = gmv_ramp(text, profile, periods, money_scale)
    price = extract_price(text, profile, currency)
    take = first_match_float(
        [r"take rate[^0-9]{0,12}([0-9.]+)%", r"手数料率[^0-9]{0,12}([0-9.]+)%"],
        text,
        12.0,
    ) / 100
    if profile.key != "marketplace":
        take = 0.0
    target_gross_margin = resolve_target_gross_margin(text, profile, periods)
    # Monetization and cost-stack base series. These act as the *default*
    # primitive drivers; a structured input overrides them before derivation.
    monthly_price = _price_series(price, periods)
    take_rate = _take_rate_series(take, periods)
    capex_per_unit = _pad_series(
        [int(value * money_scale) for value in profile.capex_per_unit_yen], periods, 0
    )
    avg_comp = [int(value * money_scale) for value in _curve(16_000_000, 14_500_000, periods)]
    variable_cogs_pct = _pad_series(profile.variable_cogs_pct, periods, 0.30)
    # The cost-to-serve drivers are not FX-scaled: calibrate_cost_stack_to_gross_margin
    # rescales all four COGS components to hit the target gross margin, so their
    # starting values act only as relative weights, not currency amounts.
    delivery_cost = [int(value) for value in _curve(90_000 if profile.key != "marketplace" else 0, 32_000 if profile.key != "marketplace" else 0, periods)]
    cloud_cost = [int(value) for value in _curve(18_000, 26_000, periods)]
    support_cost = [int(value) for value in _curve(24_000, 16_000, periods)]
    return SourcePrimitives(
        text=text,
        jpy_per_usd=jpy_per_usd,
        grain=grain,
        periods=periods,
        years=years,
        period_labels=period_labels,
        profile=profile,
        revenue_mode=revenue_mode,
        company=company,
        currency=currency,
        source_names=source_names,
        source_urls=source_urls,
        market_lines=market_lines,
        segments=segments,
        source_unknowns=extract_unknowns(text),
        new_units=new_units,
        customers=customers,
        price=price,
        take=take,
        gmv=gmv,
        monthly_price=monthly_price,
        take_rate=take_rate,
        target_gross_margin=target_gross_margin,
        money_scale=money_scale,
        capex_per_unit=capex_per_unit,
        avg_comp=avg_comp,
        variable_cogs_pct=variable_cogs_pct,
        delivery_cost=delivery_cost,
        cloud_cost=cloud_cost,
        support_cost=support_cost,
        beginning_cash=None,
        demand_pinned=False,
        stated_first_round=extract_raise_size(text, currency) or None,
        stated_post_money=extract_post_money(text, currency) or None,
        stated_churn=extract_churn_rate(text),
        stated_rd_headcount=extract_rd_headcount(text),
    )


def derive_source_facts(
    text: str, *, jpy_per_usd: float = DEFAULT_JPY_PER_USD
) -> SourceFacts:
    """Full SourceFacts from narrative text: extract primitives, then derive."""
    return _derive_facts_from_primitives(
        _extract_source_primitives(text, jpy_per_usd=jpy_per_usd)
    )


def _derive_facts_from_primitives(prims: SourcePrimitives) -> SourceFacts:
    """Step (b) of derivation: turn primitive drivers into a full SourceFacts.

    Computes ramps, gmv recomputation, demand retargeting, cost-stack
    calibration, capex, debt, the free-cash-flow projection, funding sizing,
    ownership, and TAM/SAM/SOM — all off the (possibly structured-overridden)
    primitive drivers, never a post-hoc shallow merge.
    """
    text = prims.text
    jpy_per_usd = prims.jpy_per_usd
    grain = prims.grain
    periods = prims.periods
    years = prims.years
    period_labels = prims.period_labels
    profile = prims.profile
    revenue_mode = prims.revenue_mode
    company = prims.company
    source_names = prims.source_names
    source_urls = prims.source_urls
    market_lines = prims.market_lines
    segments = prims.segments
    currency = prims.currency
    money_scale = prims.money_scale
    round_10m = max(1, int(10_000_000 * money_scale))
    round_100m = max(1, int(100_000_000 * money_scale))
    new_units = list(prims.new_units)
    gmv = list(prims.gmv)
    price = prims.price
    take = prims.take
    monthly_price = _pad_series(prims.monthly_price, periods, price)
    take_rate = _pad_series(prims.take_rate, periods, take)

    if prims.demand_pinned:
        # A structured input pinned the demand ramp; the narrative-scale
        # retargeting step would rescale it against stale narrative anchors.
        retargeted_customers = _pad_series(prims.customers, periods, 0)
    else:
        new_units, retargeted_customers = retarget_demand_to_narrative(
            text, profile, new_units, price, periods
        )

    if profile.key == "pre_revenue_milestone":
        # A pre-revenue / milestone plan has no product revenue by definition
        # — it is a milestone-driven burn and runway model. Zero the
        # monetization so revenue is 0 across the plan; R&D OpEx, prototype
        # capex, grants, and the equity round still drive the cash forecast.
        # Milestone units and customers are kept: they drive capex and cost.
        price = 0
        monthly_price = [0 for _ in range(periods)]

    new_units = _pad_series(new_units, periods, 0)
    ending = ending_units(new_units)
    if revenue_mode == "unit_sale":
        # Hardware: gmv tracks annual unit-sale revenue (new units shipped x
        # monthly price), so the downstream capex / headcount / R&D sizing
        # scales off real revenue, not a 12x recurring proxy.
        gmv = [units * monthly_price[idx] for idx, units in enumerate(new_units)]
    elif profile.key != "marketplace":
        gmv = [
            units * monthly_price[idx] * 12
            for idx, units in enumerate(ending_units(new_units))
        ]

    gmv = _pad_series(gmv, periods, 0)
    customers = _pad_series(retargeted_customers, periods, 0)
    variable_cogs_pct = _pad_series(prims.variable_cogs_pct, periods, 0.30)
    capex_per_unit = _pad_series(prims.capex_per_unit, periods, 0)
    tam_default = int(profile.tam_yen * money_scale)
    tam = max(tam_default, gmv[-1] * 10 if profile.key == "marketplace" else tam_default)
    sam = max(int(tam * 0.18), int(1_000_000_000 * money_scale))
    # Implied mature revenue: recurring billing on the installed base, or a
    # single unit-sale year. A unit-sale plan recognises only the final
    # year's shipments (new_units[-1]) x price, not the cumulative installed
    # base — that would inflate SOM as deployments accumulate.
    mature_units = (
        new_units[-1] if revenue_mode == "unit_sale"
        else ending_units(new_units)[-1]
    )
    implied_mature_revenue = mature_units * monthly_price[-1] * (
        1 if revenue_mode == "unit_sale" else 12
    )
    som = max(
        max(gmv[-1], implied_mature_revenue),
        int(1_000_000_000 * money_scale),
    )
    product_hc, gtm_hc, ops_hc, ga_hc = _headcount_plan(profile, gmv)
    # Honor a stated current R&D / engineering team size: scale the product
    # headcount ramp so period 0 lands on it, preserving the ramp shape. The
    # auto-derived ramp scales with revenue / units, which badly understates
    # an R&D-heavy plan (a 32-person team modeled as 4) and so understates
    # its people-cost burn.
    stated_rd_headcount = prims.stated_rd_headcount
    if stated_rd_headcount > 0 and product_hc and product_hc[0] > 0:
        factor = stated_rd_headcount / product_hc[0]
        product_hc = [max(1, int(round(value * factor))) for value in product_hc]
    total_hc = [a + b + c + d for a, b, c, d in zip(product_hc, gtm_hc, ops_hc, ga_hc)]
    curves = _operating_assumption_curves(profile, periods)
    avg_comp = _pad_series(prims.avg_comp, periods, int(15_000_000 * money_scale))
    delivery_cost = _pad_series(prims.delivery_cost, periods, 0)
    cloud_cost = _pad_series(prims.cloud_cost, periods, 0)
    support_cost = _pad_series(prims.support_cost, periods, 0)
    target_gross_margin = _pad_series(prims.target_gross_margin, periods, 0.78)
    variable_cogs_pct, delivery_cost, cloud_cost, support_cost = calibrate_cost_stack_to_gross_margin(
        target_gross_margin,
        new_units,
        gmv,
        monthly_price,
        take_rate,
        customers,
        [float(value) for value in curves["other_revenue_share"]],
        variable_cogs_pct,
        delivery_cost,
        cloud_cost,
        support_cost,
        revenue_mode,
    )
    if profile.key == "pre_revenue_milestone":
        # A pre-revenue plan sells nothing, so it has no cost of goods sold:
        # the cost-to-serve drivers are zeroed alongside the zeroed price
        # (the gross-margin calibration above no-ops on zero revenue and
        # would otherwise leave the raw profile defaults, making the Cost
        # Build sheet book COGS and a negative gross profit on zero
        # revenue). Prototype build cost stays in capex; R&D stays in OpEx.
        variable_cogs_pct = [0.0 for _ in range(periods)]
        delivery_cost = [0 for _ in range(periods)]
        cloud_cost = [0 for _ in range(periods)]
        support_cost = [0 for _ in range(periods)]
    other_capex = [
        _round_to(
            max(
                gmv[idx] * (0.025 if profile.key != "marketplace" else 0.010),
                total_hc[idx] * int(1_500_000 * money_scale),
            ),
            round_10m,
        )
        for idx in range(periods)
    ]
    rd_program_per_product_fte = [int(4_500_000 * money_scale) for _ in range(periods)]
    rd_program_floor = [
        _round_to(max(gmv[idx] * 0.015, int(60_000_000 * money_scale)), round_10m)
        for idx in range(periods)
    ]
    fixed_ga = [
        _round_to(
            max(total_hc[idx] * int(1_200_000 * money_scale), int(50_000_000 * money_scale)),
            round_10m,
        )
        for idx in range(periods)
    ]
    # A structured input may state the opening cash balance; it then feeds
    # the funding-round sizing directly. Otherwise size it from the people
    # base so the plan opens with a credible runway.
    if prims.beginning_cash is not None:
        beginning_cash = int(prims.beginning_cash)
    else:
        beginning_cash = _round_to(
            max(int(300_000_000 * money_scale), avg_comp[0] * max(total_hc[0], 1) * 0.50),
            round_100m,
        )
    capex_total = [
        new_units[idx] * capex_per_unit[idx] + other_capex[idx] for idx in range(periods)
    ]
    debt_raise = _debt_plan(profile, new_units, capex_per_unit, other_capex, round_100m)
    plan_revenue = plan_revenue_series(
        new_units,
        gmv,
        monthly_price,
        take_rate,
        [float(value) for value in curves["other_revenue_share"]],
        revenue_mode,
    )
    fcf_projection = project_free_cash_flow(
        plan_revenue,
        target_gross_margin,
        total_hc,
        avg_comp,
        product_hc,
        [float(value) for value in curves["sm_pct_revenue"]],
        rd_program_per_product_fte,
        rd_program_floor,
        [float(value) for value in curves["ga_pct_revenue"]],
        fixed_ga,
        capex_total,
        [int(value) for value in curves["depreciation_life_months"]],
        debt_raise,
        [float(value) for value in curves["debt_interest_rate"]],
        [int(value) for value in curves["ar_days"]],
        [int(value) for value in curves["ap_days"]],
        [float(value) for value in curves["deferred_revenue_share"]],
        [float(value) for value in curves["inventory_wip_pct_capex"]],
        [float(value) for value in curves["tax_rate"]],
    )
    free_cash_flow = [period["free_cash_flow"] for period in fcf_projection]
    # Honor a stated first-round size and post-money valuation; follow-on
    # rounds are still auto-sized to keep the plan solvent. A structured
    # input that states an explicit first-round equity raise reaches the
    # sizing here through `prims.stated_first_round`.
    stated_raise = prims.stated_first_round
    stated_post_money = prims.stated_post_money
    stated_churn = prims.stated_churn
    equity_raise = size_equity_rounds(
        beginning_cash, free_cash_flow, debt_raise, round_unit=round_100m,
        stated_first_round=stated_raise or None,
    )
    ownership_targets = _curve(0.22, 0.10, periods)
    post_money = [
        _round_to(equity_raise[idx] / ownership_targets[idx], round_100m)
        if equity_raise[idx]
        else 0
        for idx in range(periods)
    ]
    if stated_post_money and stated_post_money > 0:
        post_money[0] = stated_post_money
    currency_symbol = "$" if currency == "USD" else "¥"
    summary_bits = [
        profile.label,
        f"{profile.primary_unit_name}: {ending[-1]:,}",
        f"FY{years[-1]} revenue basis: {currency_symbol}{som:,.0f}",
    ]
    if price > 0:
        summary_bits.append(f"Monthly price: {currency_symbol}{price:,.0f}")

    return SourceFacts(
        years=years,
        period_labels=period_labels,
        grain=grain,
        currency=currency,
        display_scale="million",
        company=company,
        product=profile.product,
        mechanics=profile.label,
        primary_unit_name=profile.primary_unit_name,
        source_summary="; ".join(summary_bits),
        source_names=source_names,
        source_urls=source_urls,
        live_comps=[],
        market_lines=market_lines,
        segments=segments,
        source_unknowns=prims.source_unknowns,
        new_units=new_units,
        gmv_yen=gmv,
        monthly_price_yen=monthly_price,
        take_rate=take_rate,
        customers=customers,
        variable_cogs_pct=variable_cogs_pct,
        delivery_cost_yen=delivery_cost,
        cloud_cost_yen=cloud_cost,
        support_cost_yen=support_cost,
        capex_per_unit_yen=capex_per_unit,
        avg_comp_yen=avg_comp,
        equity_raise_yen=equity_raise,
        debt_raise_yen=debt_raise,
        debt_interest_rate=[float(value) for value in curves["debt_interest_rate"]],
        post_money_yen=post_money,
        founder_ownership=0.75,
        option_pool=0.15,
        existing_investors=0.10,
        strategic_warrant=0.00,
        option_pool_refresh=[float(value) for value in curves["option_pool_refresh"]],
        secondary_warrant_dilution=[float(value) for value in curves["secondary_warrant_dilution"]],
        product_headcount=product_hc,
        gtm_headcount=gtm_hc,
        operations_headcount=ops_hc,
        ga_headcount=ga_hc,
        net_retention=[float(value) for value in curves["net_retention"]],
        utilization_conversion=[float(value) for value in curves["utilization_conversion"]],
        other_revenue_share=[float(value) for value in curves["other_revenue_share"]],
        deferred_revenue_share=[float(value) for value in curves["deferred_revenue_share"]],
        revenue_productivity_factor=[float(value) for value in curves["revenue_productivity_factor"]],
        depreciation_life_months=[int(value) for value in curves["depreciation_life_months"]],
        other_capex_yen=other_capex,
        ar_days=[int(value) for value in curves["ar_days"]],
        ap_days=[int(value) for value in curves["ap_days"]],
        tax_rate=[float(value) for value in curves["tax_rate"]],
        beginning_cash_yen=beginning_cash,
        sm_pct_revenue=[float(value) for value in curves["sm_pct_revenue"]],
        rd_program_per_product_fte_yen=rd_program_per_product_fte,
        rd_program_floor_yen=rd_program_floor,
        ga_pct_revenue=[float(value) for value in curves["ga_pct_revenue"]],
        fixed_ga_yen=fixed_ga,
        inventory_wip_pct_capex=[float(value) for value in curves["inventory_wip_pct_capex"]],
        grants_yen=[0 for _ in range(periods)],
        convertibles_yen=[0 for _ in range(periods)],
        lease_financing_yen=[0 for _ in range(periods)],
        customer_advances_yen=[0 for _ in range(periods)],
        secondary_yen=[0 for _ in range(periods)],
        nol_yen=[0 for _ in range(periods)],
        revenue_multiple=[round(value, 1) for value in _curve(4, 12, periods)],
        gross_profit_multiple=[round(value, 1) for value in _curve(8, 16, periods)],
        ebitda_multiple=[round(value, 1) for value in _curve(12, 28, periods)],
        discount_rate=0.18,
        customer_roi_yen=max(price * 18, int(3_000_000 * money_scale)),
        implementation_cost_yen=max(price * 2, int(300_000 * money_scale)),
        sales_cycle_months=4 if profile.key in {"recurring_software", "marketplace"} else 6,
        churn_rate=(
            stated_churn
            if stated_churn is not None
            else (0.08 if profile.key != "marketplace" else 0.18)
        ),
        repeat_rate=0.40 if profile.key == "marketplace" else 0.75,
        payment_fee_pct=0.025 if profile.key == "marketplace" else 0.0,
        incentive_pct_gmv=0.025 if profile.key == "marketplace" else 0.0,
        fraud_loss_pct_gmv=0.004 if profile.key == "marketplace" else 0.0,
        value_capture_share=[0.18 if profile.key == "marketplace" else 0.25 for _ in range(periods)],
        target_gross_margin=target_gross_margin,
        support_tickets_per_customer=[18 if profile.key == "hardware_asset_heavy" else 12 for _ in range(periods)],
        minutes_per_support_ticket=[45 if profile.key == "hardware_asset_heavy" else 25 for _ in range(periods)],
        support_fte_capacity_tickets=[5_000 if profile.key == "hardware_asset_heavy" else 7_500 for _ in range(periods)],
        product_squad_size=[6 for _ in range(periods)],
        target_min_runway_months=[18 for _ in range(periods)],
        evidence_status="estimate / needs validation",
        tam_yen=tam,
        sam_yen=sam,
        som_yen=som,
        revenue_mode=revenue_mode,
    )


def extract_segments(text: str) -> list[str]:
    candidates: list[str] = []
    segment_line = re.search(r"(?:segments?|セグメント|事業)[：:\s]+(.+)", text, flags=re.IGNORECASE)
    if segment_line:
        for part in re.split(r"[,、/／;；]", segment_line.group(1)):
            cleaned = part.strip(" 。.")
            if 1 < len(cleaned) <= 40 and cleaned not in candidates:
                candidates.append(cleaned)
    keywords = [
        ("SaaS", ("saas", "arr", "subscription")),
        ("Marketplace", ("marketplace", "gmv", "take rate")),
        ("Hardware", ("hardware", "robot", "manufacturing", "humanoid", "raas")),
        ("Financial services", ("fintech", "loan", "lending", "credit")),
        ("Services", ("service", "implementation", "maintenance", "保守")),
    ]
    lowered = text.lower()
    for label, terms in keywords:
        if any(term in lowered for term in terms) and label not in candidates:
            candidates.append(label)
    return candidates[:8] or ["Core business"]


def assumption_decomposition_for(facts: SourceFacts) -> tuple[AssumptionGroup, ...]:
    """Return driver-decomposition patterns for the assumptions sheet.

    This registry owns assumption depth. The workbook renderer should only
    place rows and resolve row references; it should not decide which
    explanatory variables make an assumption credible.
    """
    periods = len(facts.period_labels)
    qualified_pool = [
        max(int(facts.new_units[idx] / max(facts.utilization_conversion[idx], 0.01)), facts.customers[idx])
        for idx in range(periods)
    ]
    committed_financing = [
        facts.equity_raise_yen[idx]
        + facts.debt_raise_yen[idx]
        + facts.grants_yen[idx]
        + facts.convertibles_yen[idx]
        + facts.lease_financing_yen[idx]
        + facts.customer_advances_yen[idx]
        for idx in range(periods)
    ]
    evidence = [facts.evidence_status for _ in range(periods)]
    pricing_source = "take-rate / liquidity proof" if "Marketplace" in facts.mechanics else "customer ROI and cost floor"
    cost_source = "BOM / service / support workload" if "Hardware" in facts.mechanics else "hosting / delivery / support workload"
    return (
        AssumptionGroup(
            "Demand support",
            (
                AssumptionLine("Qualified demand pool", "count", qualified_pool, "funnel / addressable accounts", fmt_key="integer", note="Use when source support for new units is thin."),
                AssumptionLine("Demand conversion to units", "%", facts.utilization_conversion, "conversion evidence", fmt_key="percent"),
                AssumptionLine("Implied new units from funnel", "units", "={c}{row:Qualified demand pool}*{c}{row:Demand conversion to units}", kind="formula", fmt_key="integer"),
                AssumptionLine("Selected new units", "units", "={c}{row:New primary units}", kind="formula", fmt_key="integer"),
                AssumptionLine("Demand support coverage", "x", "=IF({c}{row:Selected new units}=0,0,{c}{row:Implied new units from funnel}/{c}{row:Selected new units})", kind="formula", fmt_key="multiple", bold=True),
                AssumptionLine("Demand evidence status", "status", evidence, "source / management / estimate", fmt_key="text"),
            ),
        ),
        AssumptionGroup(
            "Pricing support",
            (
                AssumptionLine("Customer annual value / ROI", "JPY", [facts.customer_roi_yen for _ in range(periods)], "customer value proof", fmt_key="money"),
                AssumptionLine("Value capture share", "%", facts.value_capture_share, pricing_source, fmt_key="percent"),
                AssumptionLine("Value-based monthly price", "JPY", "={c}{row:Customer annual value / ROI}*{c}{row:Value capture share}/12", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Target gross margin", "%", facts.target_gross_margin, "margin policy / benchmark", fmt_key="percent"),
                AssumptionLine("Cost-plus monthly floor", "JPY", "=({c}{row:Delivery cost / primary unit}+{c}{row:Cloud / platform cost}+{c}{row:Support cost / customer})/(1-MAX(0.01,{c}{row:Target gross margin}))", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Selected monthly price", "JPY", "={c}{row:Monthly price / unit}", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Pricing support ratio", "x", "=IF(MAX({c}{row:Value-based monthly price},{c}{row:Cost-plus monthly floor})=0,0,{c}{row:Selected monthly price}/MAX({c}{row:Value-based monthly price},{c}{row:Cost-plus monthly floor}))", kind="formula", fmt_key="multiple", bold=True),
                AssumptionLine("Pricing evidence status", "status", evidence, "source / management / estimate", fmt_key="text"),
            ),
        ),
        AssumptionGroup(
            "Cost-to-serve support",
            (
                AssumptionLine("Direct delivery cost / unit", "JPY", "={c}{row:Delivery cost / primary unit}", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Cloud / platform cost / unit", "JPY", "={c}{row:Cloud / platform cost}", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Support tickets / customer / year", "count", facts.support_tickets_per_customer, cost_source, fmt_key="integer"),
                AssumptionLine("Minutes / support ticket", "count", facts.minutes_per_support_ticket, "support workload", fmt_key="integer"),
                AssumptionLine("Support FTE ticket capacity", "count", facts.support_fte_capacity_tickets, "support capacity", fmt_key="integer"),
                AssumptionLine("Cost / support ticket", "JPY", "=IF({c}{row:Support tickets / customer / year}=0,0,{c}{row:Support cost / customer}*12/{c}{row:Support tickets / customer / year})", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Implied annual service cost / customer", "JPY", "={c}{row:Direct delivery cost / unit}*12+{c}{row:Cloud / platform cost / unit}*12+{c}{row:Cost / support ticket}*{c}{row:Support tickets / customer / year}", kind="formula", fmt_key="money"),
                AssumptionLine("Implied variable COGS %", "%", "=IF({c}{row:Monthly price / unit}=0,0,{c}{row:Implied annual service cost / customer}/({c}{row:Monthly price / unit}*12))", kind="formula", fmt_key="percent"),
                AssumptionLine("Selected variable COGS %", "%", "={c}{row:Variable COGS}", kind="formula", fmt_key="percent"),
                AssumptionLine("COGS support ratio", "x", "=IF({c}{row:Selected variable COGS %}=0,0,{c}{row:Implied variable COGS %}/{c}{row:Selected variable COGS %})", kind="formula", fmt_key="multiple", bold=True),
                AssumptionLine("COGS evidence status", "status", evidence, "source / management / estimate", fmt_key="text"),
            ),
        ),
        AssumptionGroup(
            "People capacity support",
            (
                AssumptionLine("Product squad size", "FTE", facts.product_squad_size, "team design", fmt_key="integer"),
                AssumptionLine("Required product squads", "count", "=IF({c}{row:Product squad size}=0,0,{c}31/{c}{row:Product squad size})", kind="formula", fmt_key="num"),
                AssumptionLine("Revenue / GTM FTE", "JPY", "=IF({c}32=0,0,'Revenue Build'!{c}18/{c}32)", kind="formula", fmt_key="money"),
                AssumptionLine("Customers / Ops-CS FTE", "count", "=IF({c}33=0,0,{c}13/{c}33)", kind="formula", fmt_key="num"),
                AssumptionLine("Required Ops-CS FTE from ticket load", "FTE", "=IF({c}{row:Support FTE ticket capacity}=0,0,{c}13*{c}{row:Support tickets / customer / year}/{c}{row:Support FTE ticket capacity})", kind="formula", fmt_key="num"),
                AssumptionLine("Ops-CS capacity coverage", "x", "=IF({c}{row:Required Ops-CS FTE from ticket load}=0,0,{c}33/{c}{row:Required Ops-CS FTE from ticket load})", kind="formula", fmt_key="multiple", bold=True),
                AssumptionLine("People evidence status", "status", evidence, "source / management / estimate", fmt_key="text"),
            ),
        ),
        AssumptionGroup(
            "Capital and runway support",
            (
                AssumptionLine("CapEx / unit selected", "JPY", "={c}38", kind="formula", fmt_key="jpy_yen"),
                AssumptionLine("Other CapEx selected", "JPY", "={c}40", kind="formula", fmt_key="money"),
                AssumptionLine("CapEx intensity vs revenue", "%", "=IF('Revenue Build'!{c}18=0,0,'Cost Build'!{c}16/'Revenue Build'!{c}18)", kind="formula", fmt_key="percent"),
                AssumptionLine("Target minimum runway", "months", facts.target_min_runway_months, "financing policy", fmt_key="num"),
                AssumptionLine("Committed financing", "JPY", committed_financing, "equity / debt / grants / advances", fmt_key="money"),
                AssumptionLine("Cash need coverage by committed financing", "x", "=IF(ABS('CF'!{c}16)=0,0,{c}{row:Committed financing}/ABS('CF'!{c}16))", kind="formula", fmt_key="multiple"),
                AssumptionLine("Runway support coverage", "x", "=IF({c}{row:Target minimum runway}=0,0,'CF'!{c}32/{c}{row:Target minimum runway})", kind="formula", fmt_key="multiple", bold=True),
                AssumptionLine("Capital evidence status", "status", evidence, "source / management / estimate", fmt_key="text"),
            ),
        ),
    )


def extract_unknowns(text: str) -> list[str]:
    unknowns = []
    for label, terms in [
        ("pricing validation", ("price", "pricing", "価格", "料金")),
        ("customer ROI proof", ("roi", "payback", "導入効果")),
        ("cost-to-serve evidence", ("cogs", "gross margin", "原価")),
        ("financing terms", ("debt", "convertible", "safe", "jkiss", "借入", "転換")),
        ("market benchmark refresh", ("tam", "sam", "som", "market", "市場")),
    ]:
        if any(term in text.lower() for term in terms):
            unknowns.append(label)
    return unknowns or ["pricing validation", "cost-to-serve evidence", "financing terms"]


def _ending_to_new_units(customers: list[int]) -> list[int]:
    """Invert `ending_units`: back out the new-unit series from an ending series.

    A structured input commonly states `customers` as the *ending* installed
    base per period. `ending_units` rolls new units forward with churn
    (`churn = running * (0.02 + idx*0.005)`); this inverts that walk so the
    derived new-unit ramp reproduces the stated ending series — the demand
    primitive the rest of derivation consumes.
    """
    new_units: list[int] = []
    prior = 0
    for idx, ending in enumerate(customers):
        if idx == 0:
            value = max(0, int(ending))
        else:
            churn = int(prior * (0.02 + idx * 0.005))
            value = max(0, int(ending) - prior + churn)
        new_units.append(value)
        prior = max(0, int(ending))
    return new_units


def derive_source_facts_from_mapping(raw: dict[str, Any]) -> SourceFacts:
    """Build facts from a structured YAML mapping.

    The structured drivers flow through the full derivation pipeline: this
    extracts the primitive drivers from any narrative the mapping carries,
    *overrides* those primitives with the structured values, then derives the
    whole SourceFacts. So gmv, take rate, the demand ramp, cost-stack
    calibration, and funding sizing all see the structured drivers — never a
    post-hoc shallow merge that leaves derived quantities stale.

    Pure stated *outputs* (financing schedules, headcount, operating-curve
    overrides, multiples, market-size scalars, ...) — fields nothing
    downstream consumes — are applied as a final override on the derived
    facts. An explicitly-stated driver-level input (a first-round equity raise,
    an opening cash balance, ...) is honored as a stated input to derivation.
    """
    narrative = ""
    for key in ("source_text", "narrative", "story", "memo", "description"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            narrative = value
            break
    company = raw.get("company") or raw.get("company_name") or "Startup"
    mechanics = raw.get("mechanics") or raw.get("business_model") or raw.get("model_type") or "generic startup"
    if not narrative:
        narrative = f"# {company}\nGeneric financial model for a {mechanics}."

    fx_raw = raw.get("jpy_per_usd") or raw.get("fx_rate")
    jpy_per_usd = float(fx_raw) if fx_raw else DEFAULT_JPY_PER_USD

    # --- Step 1: primitive drivers from the narrative -----------------------
    prims = _extract_source_primitives(narrative, jpy_per_usd=jpy_per_usd)

    # --- Step 2: resolve the forecast axis from the structured input --------
    periods_raw = raw.get("periods") or raw.get("horizon_periods") or raw.get("horizon")
    grain = str(raw.get("grain") or raw.get("model_grain") or prims.grain).lower()
    if isinstance(periods_raw, str):
        period_match = re.search(r"([0-9]{1,2})", periods_raw)
        periods = int(period_match.group(1)) if period_match else len(prims.years)
        if "year" in periods_raw.lower() or "年" in periods_raw:
            periods = periods * (12 if grain.startswith("month") else 4 if grain.startswith("quarter") else 1)
    elif isinstance(periods_raw, (int, float)) and not isinstance(periods_raw, bool):
        periods = int(periods_raw)
    else:
        periods = len(prims.years)
    periods = min(max(periods, 1), MAX_FORECAST_PERIODS)
    start_year = int(raw.get("start_year") or raw.get("fiscal_year") or prims.years[0])
    years, labels = forecast_axis(start_year, periods, grain)
    currency = str(raw.get("currency") or "JPY").upper()

    prims.grain = grain
    prims.periods = periods
    prims.years = years
    prims.period_labels = _as_list(raw.get("period_labels"))[:periods] or labels
    prims.currency = currency
    prims.money_scale = money_scale_for_currency(currency, jpy_per_usd)
    prims.company = str(company)
    prims.segments = [str(v) for v in _as_list(raw.get("segments")) if str(v).strip()] or prims.segments
    prims.source_unknowns = [str(v) for v in _as_list(raw.get("unknowns")) if str(v).strip()] or prims.source_unknowns

    # --- Step 3: override the primitive drivers -----------------------------
    # Demand. A stated customer / new-unit series pins the ramp; the
    # narrative-scale retargeting step is then bypassed. When only the ending
    # `customers` series is stated, the new-unit ramp is inverted from it so
    # revenue (driven by the installed base) tracks the stated count.
    raw_new_units = _first_present(raw, ("new_units",))
    raw_customers = _first_present(raw, ("customers",))
    if raw_new_units is not None:
        prims.new_units = _coerce_int_series(raw_new_units, periods, prims.new_units)
        prims.demand_pinned = True
        if raw_customers is not None:
            prims.customers = _coerce_int_series(raw_customers, periods, prims.customers)
        else:
            prims.customers = ending_units(prims.new_units)
    elif raw_customers is not None:
        prims.customers = _coerce_int_series(raw_customers, periods, prims.customers)
        prims.new_units = _ending_to_new_units(prims.customers)
        prims.demand_pinned = True
    else:
        prims.new_units = _pad_series(prims.new_units, periods, 0)
        prims.customers = _pad_series(prims.customers, periods, 0)

    # Monetization drivers (carried as series).
    prims.monthly_price = _coerce_int_series(
        _first_present(raw, ("monthly_price_yen", "monthly_price")),
        periods, prims.monthly_price,
    )
    prims.price = prims.monthly_price[0] if prims.monthly_price else prims.price
    prims.gmv = _coerce_int_series(
        _first_present(raw, ("gmv_yen", "gmv")), periods, prims.gmv,
    )
    prims.take_rate = _coerce_float_series(
        _first_present(raw, ("take_rate", "take")), periods, prims.take_rate, percent=True,
    )
    prims.take = prims.take_rate[0] if prims.take_rate else prims.take
    prims.target_gross_margin = _coerce_float_series(
        _first_present(raw, ("target_gross_margin",)), periods, prims.target_gross_margin, percent=True,
    )
    # Cost-stack and capital drivers that feed calibration / FCF / funding.
    prims.variable_cogs_pct = _coerce_float_series(
        _first_present(raw, ("variable_cogs_pct", "variable_cogs")), periods, prims.variable_cogs_pct, percent=True,
    )
    prims.delivery_cost = _coerce_int_series(
        _first_present(raw, ("delivery_cost_yen", "delivery_cost")), periods, prims.delivery_cost,
    )
    prims.cloud_cost = _coerce_int_series(
        _first_present(raw, ("cloud_cost_yen", "cloud_cost")), periods, prims.cloud_cost,
    )
    prims.support_cost = _coerce_int_series(
        _first_present(raw, ("support_cost_yen", "support_cost")), periods, prims.support_cost,
    )
    prims.capex_per_unit = _coerce_int_series(
        _first_present(raw, ("capex_per_unit_yen", "capex_per_unit")), periods, prims.capex_per_unit,
    )
    prims.avg_comp = _coerce_int_series(
        _first_present(raw, ("avg_comp_yen", "avg_comp")), periods, prims.avg_comp,
    )
    # Stated driver-level financing inputs.
    beginning_cash_raw = _first_present(raw, ("beginning_cash_yen", "beginning_cash"))
    if beginning_cash_raw is not None:
        prims.beginning_cash = _coerce_int_series(beginning_cash_raw, 1, [prims.beginning_cash or 0])[0]
    # Only the first stated round is pinned; follow-on rounds always
    # auto-size for solvency. A multi-round YAML schedule is read as its
    # period-0 value — the funding plan owns the follow-on cadence.
    equity_raise_raw = _first_present(raw, ("equity_raise_yen", "equity_raise"))
    if equity_raise_raw is not None:
        first_round = _coerce_int_series(equity_raise_raw, 1, [0])[0]
        if first_round > 0:
            prims.stated_first_round = first_round
    post_money_raw = _first_present(raw, ("post_money_yen", "post_money"))
    if post_money_raw is not None:
        stated_pm = _coerce_int_series(post_money_raw, 1, [0])[0]
        if stated_pm > 0:
            prims.stated_post_money = stated_pm
    churn_raw = _first_present(raw, ("churn_rate", "churn"))
    if churn_raw is not None:
        prims.stated_churn = _coerce_float_series(churn_raw, 1, [prims.stated_churn or 0.0], percent=True)[0]

    # --- Step 4: derive the full SourceFacts from the structured drivers ----
    facts = _derive_facts_from_primitives(prims)

    # --- Step 5: apply stated outputs nothing downstream consumes -----------
    overrides: dict[str, Any] = dict(
        display_scale=str(raw.get("display_scale") or raw.get("scale") or "million").lower(),
        mechanics=str(mechanics),
        product=str(raw.get("product") or facts.product),
        primary_unit_name=str(raw.get("primary_unit_name") or raw.get("unit_name") or facts.primary_unit_name),
    )
    # Financing schedules and other stated output series — these do not feed
    # the derivation, so a direct override does not leave anything stale.
    output_money_series = (
        "debt_raise_yen", "grants_yen", "convertibles_yen", "lease_financing_yen",
        "customer_advances_yen", "secondary_yen", "nol_yen", "other_capex_yen",
        "fixed_ga_yen", "rd_program_floor_yen", "rd_program_per_product_fte_yen",
    )
    for field in output_money_series:
        raw_value = _first_present(raw, (field, field.replace("_yen", "")))
        if raw_value is not None:
            overrides[field] = _coerce_int_series(raw_value, periods, getattr(facts, field))
    output_unit_series = (
        "product_headcount", "gtm_headcount", "operations_headcount", "ga_headcount",
    )
    for field in output_unit_series:
        raw_value = _first_present(raw, (field,))
        if raw_value is not None:
            overrides[field] = _coerce_int_series(raw_value, periods, getattr(facts, field))
    output_pct_series = {
        "value_capture_share": True,
        "debt_interest_rate": True,
        "option_pool_refresh": True,
        "secondary_warrant_dilution": True,
        "net_retention": False,
        "utilization_conversion": True,
        "other_revenue_share": True,
        "deferred_revenue_share": True,
        "revenue_productivity_factor": False,
        "tax_rate": True,
        "sm_pct_revenue": True,
        "ga_pct_revenue": True,
        "inventory_wip_pct_capex": True,
        "revenue_multiple": False,
        "gross_profit_multiple": False,
        "ebitda_multiple": False,
    }
    for field, is_percent in output_pct_series.items():
        raw_value = _first_present(raw, (field, field.replace("_pct", ""), field.replace("_rate", "")))
        if raw_value is not None:
            overrides[field] = _coerce_float_series(raw_value, periods, getattr(facts, field), percent=is_percent)
    for field in ("depreciation_life_months", "ar_days", "ap_days",
                  "support_tickets_per_customer", "minutes_per_support_ticket",
                  "support_fte_capacity_tickets", "product_squad_size",
                  "target_min_runway_months"):
        if raw.get(field) is not None:
            overrides[field] = _coerce_int_series(raw.get(field), periods, getattr(facts, field))
    if raw.get("evidence_status") is not None:
        overrides["evidence_status"] = str(raw.get("evidence_status"))

    scalar_overrides = {
        "founder_ownership": "founder_ownership",
        "option_pool": "option_pool",
        "existing_investors": "existing_investors",
        "strategic_warrant": "strategic_warrant",
        "discount_rate": "discount_rate",
        "customer_roi_yen": "customer_roi",
        "implementation_cost_yen": "implementation_cost",
        "sales_cycle_months": "sales_cycle_months",
        "repeat_rate": "repeat_rate",
        "payment_fee_pct": "payment_fee_pct",
        "incentive_pct_gmv": "incentive_pct_gmv",
        "fraud_loss_pct_gmv": "fraud_loss_pct_gmv",
        "tam_yen": "tam",
        "sam_yen": "sam",
        "som_yen": "som",
    }
    for field, alt in scalar_overrides.items():
        value = _first_present(raw, (field, alt))
        if value is None:
            continue
        if field.endswith("_yen"):
            overrides[field] = _coerce_int_series(value, 1, [getattr(facts, field)])[0]
        elif field.endswith("_pct") or field in {"founder_ownership", "option_pool", "existing_investors", "strategic_warrant", "discount_rate", "repeat_rate"}:
            overrides[field] = _coerce_float_series(value, 1, [float(getattr(facts, field))], percent=True)[0]
        elif field == "sales_cycle_months":
            overrides[field] = int(float(value))
        else:
            overrides[field] = float(value)

    return SourceFacts(**{**facts.__dict__, **overrides})


__all__ = [
    "AssumptionGroup",
    "AssumptionLine",
    "DriverSurface",
    "DEFAULT_FORECAST_PERIODS",
    "MECHANIC_PROFILES",
    "MechanicProfile",
    "SourceFacts",
    "average_units",
    "derive_source_facts",
    "derive_source_facts_from_mapping",
    "driver_surfaces_for",
    "assumption_decomposition_for",
    "ending_units",
    "extract_forecast_periods",
    "extract_model_grain",
    "extract_start_year",
    "extract_source_facts",
    "forecast_years",
    "mechanic_key",
    "profile_for_text",
    "score_mechanics",
]
