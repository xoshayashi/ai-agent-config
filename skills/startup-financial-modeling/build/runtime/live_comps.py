"""Comparable-evidence retrieval for startup financial-modeling.

The module intentionally uses only the Python standard library so the skill can
ship without a data-vendor SDK. It treats live public data and user-provided
private/transaction evidence as benchmark support, not as audited truth.
"""

from __future__ import annotations

import json
import statistics
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class PublicComp:
    ticker: str
    name: str
    currency: str
    market_cap: float | None
    enterprise_value: float | None
    revenue_multiple: float | None
    ebitda_multiple: float | None
    source_url: str
    as_of_date: str
    status: str
    error: str = ""
    company_type: str = "public"
    source_type: str = "public market data"
    stage: str = ""
    geography: str = ""
    applicability_limits: str = ""


@dataclass(frozen=True)
class PublicCompsResult:
    comps: list[PublicComp]
    revenue_multiple_median: float | None
    ebitda_multiple_median: float | None
    source_url: str
    as_of_date: str


_RESULT_CACHE: dict[tuple[tuple[str, ...], float], PublicCompsResult] = {}
_SEC_TICKER_LOOKUP_CACHE: dict[str, tuple[str, str]] | None = None


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        raw = value.get("raw")
        if isinstance(raw, (int, float)):
            return float(raw)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("x", "")
        if cleaned.endswith("%"):
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _first_float(raw: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = _to_float(raw.get(key))
        if value is not None:
            return value
    return None


def _first_text(raw: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def provided_comp_from_mapping(raw: dict[str, Any]) -> PublicComp:
    """Normalize private, transaction, report, or manually supplied comps.

    This deliberately accepts a broad set of field aliases so users can bring
    PitchBook/Crunchbase exports, press-release notes, transaction comps, or
    internal benchmark tables without reshaping every column first.
    """
    company_type = _first_text(raw, ["company_type", "type", "comp_type"], "private")
    source_type = _first_text(raw, ["source_type", "source_category"], f"user-provided {company_type} comparable")
    valuation = _first_float(raw, ["enterprise_value", "ev", "valuation", "post_money", "post_money_valuation", "market_cap"])
    revenue = _first_float(raw, ["revenue", "arr", "run_rate_revenue", "gmv_net_revenue"])
    ebitda = _first_float(raw, ["ebitda", "adjusted_ebitda"])
    revenue_multiple = _first_float(raw, ["revenue_multiple", "ev_revenue", "ev_to_revenue", "ev/revenue"])
    ebitda_multiple = _first_float(raw, ["ebitda_multiple", "ev_ebitda", "ev_to_ebitda", "ev/ebitda"])
    if revenue_multiple is None and valuation and revenue and revenue > 0:
        revenue_multiple = valuation / revenue
    if ebitda_multiple is None and valuation and ebitda and ebitda > 0:
        ebitda_multiple = valuation / ebitda

    source_url = _first_text(raw, ["source_url", "url", "source", "file", "owner"], "user-provided comparable")
    as_of_date = _first_text(raw, ["as_of_date", "date", "period"], "")
    error = _first_text(raw, ["error", "caveat", "note"], "")
    has_usable_multiple = bool(revenue_multiple or ebitda_multiple)
    if not as_of_date:
        error = (error + "; " if error else "") + "missing source date"
    if not has_usable_multiple:
        error = (error + "; " if error else "") + "missing usable valuation multiple"
    status = _first_text(raw, ["status"], "provided" if as_of_date and has_usable_multiple else "needs review")
    return PublicComp(
        ticker=_first_text(raw, ["ticker", "symbol"], ""),
        name=_first_text(raw, ["name", "company", "target", "comparable"], "Unspecified comparable"),
        currency=_first_text(raw, ["currency"], ""),
        market_cap=_first_float(raw, ["market_cap"]),
        enterprise_value=_first_float(raw, ["enterprise_value", "ev"]),
        revenue_multiple=revenue_multiple,
        ebitda_multiple=ebitda_multiple,
        source_url=source_url,
        as_of_date=as_of_date,
        status=status,
        error=error,
        company_type=company_type,
        source_type=source_type,
        stage=_first_text(raw, ["stage", "round", "maturity"], ""),
        geography=_first_text(raw, ["geography", "region", "country"], ""),
        applicability_limits=_first_text(raw, ["applicability_limits", "limits", "comparability", "rationale"], ""),
    )


def provided_comps_from_raw(value: Any) -> list[PublicComp]:
    """Return normalized non-ticker comparable evidence from YAML-like input."""
    if isinstance(value, dict):
        items: list[Any] = [value]
    elif isinstance(value, list):
        items = value
    else:
        return []
    comps: list[PublicComp] = []
    for item in items:
        if isinstance(item, dict):
            comps.append(provided_comp_from_mapping(item))
    return comps


def summarize_comps(comps: list[PublicComp], *, source_url: str = "mixed comparable evidence") -> PublicCompsResult:
    today = date.today().isoformat()
    usable_statuses = {"current", "provided"}
    revenue_values = [
        comp.revenue_multiple
        for comp in comps
        if comp.revenue_multiple and comp.revenue_multiple > 0 and comp.status in usable_statuses
    ]
    ebitda_values = [
        comp.ebitda_multiple
        for comp in comps
        if comp.ebitda_multiple and comp.ebitda_multiple > 0 and comp.status in usable_statuses
    ]
    return PublicCompsResult(
        comps=comps,
        revenue_multiple_median=statistics.median(revenue_values) if revenue_values else None,
        ebitda_multiple_median=statistics.median(ebitda_values) if ebitda_values else None,
        source_url=source_url,
        as_of_date=today,
    )


def _quote_summary_url(ticker: str) -> str:
    modules = "price,summaryDetail,defaultKeyStatistics,financialData"
    return (
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
        f"{urllib.parse.quote(ticker)}?modules={modules}"
    )


def _json_url(url: str, *, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "startup-financial-modeling contact@example.com"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _compact_error(value: Any, *, limit: int = 220) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _yahoo_chart_url(ticker: str) -> str:
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?range=1d&interval=1d"


def _latest_fact_value(payload: dict[str, Any], namespace: str, tag: str, unit: str, *, annual_only: bool = False) -> float | None:
    units = payload.get("facts", {}).get(namespace, {}).get(tag, {}).get("units", {})
    facts = units.get(unit, [])
    if not isinstance(facts, list):
        return None
    candidates = [
        item for item in facts
        if isinstance(item, dict)
        and isinstance(item.get("val"), (int, float))
        and (not annual_only or item.get("fp") == "FY" or item.get("form") == "10-K")
    ]
    if not candidates:
        return None
    latest = max(candidates, key=lambda item: str(item.get("end") or item.get("filed") or ""))
    return float(latest["val"])


def _sec_ticker_lookup(*, timeout: float) -> dict[str, tuple[str, str]]:
    global _SEC_TICKER_LOOKUP_CACHE
    if _SEC_TICKER_LOOKUP_CACHE is not None:
        return _SEC_TICKER_LOOKUP_CACHE
    payload = _json_url("https://www.sec.gov/files/company_tickers.json", timeout=timeout)
    lookup: dict[str, tuple[str, str]] = {}
    for item in payload.values():
        if isinstance(item, dict) and item.get("ticker") and item.get("cik_str") is not None:
            normalized = str(item.get("ticker")).upper()
            lookup[normalized] = (f"{int(item['cik_str']):010d}", str(item.get("title") or normalized))
    _SEC_TICKER_LOOKUP_CACHE = lookup
    return lookup


def _sec_cik_for_ticker(ticker: str, *, timeout: float) -> tuple[str, str] | None:
    return _sec_ticker_lookup(timeout=timeout).get(ticker.upper())


def _fetch_market_cap_revenue_proxy(ticker: str, *, timeout: float, prior_error: str) -> PublicComp:
    as_of = date.today().isoformat()
    chart_url = _yahoo_chart_url(ticker)
    compact_prior_error = _compact_error(prior_error)
    try:
        chart = _json_url(chart_url, timeout=timeout)
        result = chart.get("chart", {}).get("result", [{}])[0]
        meta = result.get("meta", {})
        price = _to_float(meta.get("regularMarketPrice"))
        currency = str(meta.get("currency") or "")
        name = str(meta.get("longName") or meta.get("shortName") or ticker)
        cik_name = _sec_cik_for_ticker(ticker, timeout=timeout)
        if cik_name is None:
            return PublicComp(ticker, name, currency, None, None, None, None, chart_url, as_of, "failed", f"{compact_prior_error}; SEC CIK not found")
        cik, sec_name = cik_name
        sec_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        sec_payload = _json_url(sec_url, timeout=timeout)
        revenue = (
            _latest_fact_value(sec_payload, "us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD", annual_only=True)
            or _latest_fact_value(sec_payload, "us-gaap", "Revenues", "USD", annual_only=True)
        )
        shares = _latest_fact_value(sec_payload, "dei", "EntityCommonStockSharesOutstanding", "shares")
        if not (price and shares and revenue and revenue > 0):
            return PublicComp(ticker, sec_name or name, currency, None, None, None, None, sec_url, as_of, "failed", f"{compact_prior_error}; SEC/Yahoo proxy missing price, shares, or revenue")
        market_cap = price * shares
        return PublicComp(
            ticker=ticker,
            name=sec_name or name,
            currency=currency or "USD",
            market_cap=market_cap,
            enterprise_value=None,
            revenue_multiple=market_cap / revenue,
            ebitda_multiple=None,
            source_url=f"{chart_url}; {sec_url}",
            as_of_date=as_of,
            status="current",
            error="market-cap/revenue proxy; EV and EBITDA unavailable from fallback",
        )
    except Exception as exc:  # noqa: BLE001 - fallback failures should be visible in the workbook.
        return PublicComp(ticker, "", "", None, None, None, None, chart_url, as_of, "failed", f"{compact_prior_error}; fallback failed: {_compact_error(exc)}")


def _extract_result(payload: dict[str, Any]) -> dict[str, Any] | None:
    result = payload.get("quoteSummary", {}).get("result")
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, dict):
            return item
    return None


def fetch_public_comp(ticker: str, *, timeout: float = 8.0) -> PublicComp:
    """Fetch one public comparable from Yahoo Finance quoteSummary."""
    normalized = ticker.strip().upper()
    as_of = date.today().isoformat()
    url = _quote_summary_url(normalized)
    if not normalized:
        return PublicComp("", "", "", None, None, None, None, url, as_of, "failed", "blank ticker")
    try:
        payload = _json_url(url, timeout=timeout)
        item = _extract_result(payload)
        if item is None:
            return PublicComp(normalized, "", "", None, None, None, None, url, as_of, "failed", "empty quoteSummary result")
        price = item.get("price", {})
        stats = item.get("defaultKeyStatistics", {})
        financial = item.get("financialData", {})
        name = str(price.get("shortName") or price.get("longName") or normalized)
        currency = str(price.get("currency") or financial.get("financialCurrency") or "")
        return PublicComp(
            ticker=normalized,
            name=name,
            currency=currency,
            market_cap=_to_float(price.get("marketCap")),
            enterprise_value=_to_float(stats.get("enterpriseValue")),
            revenue_multiple=_to_float(stats.get("enterpriseToRevenue")),
            ebitda_multiple=_to_float(stats.get("enterpriseToEbitda")),
            source_url=url,
            as_of_date=as_of,
            status="current",
        )
    except Exception as exc:  # noqa: BLE001 - data retrieval failures must be surfaced, not fatal by default.
        return _fetch_market_cap_revenue_proxy(normalized, timeout=timeout, prior_error=str(exc))


def fetch_public_comps(tickers: list[str], *, timeout: float = 8.0) -> PublicCompsResult:
    normalized = tuple(dict.fromkeys(ticker.strip().upper() for ticker in tickers if ticker.strip()))
    cache_key = (normalized, timeout)
    today = date.today().isoformat()
    cached = _RESULT_CACHE.get(cache_key)
    if cached is not None and cached.as_of_date == today:
        return cached
    comps = [fetch_public_comp(ticker, timeout=timeout) for ticker in normalized]
    source_url = "https://query2.finance.yahoo.com/v10/finance/quoteSummary"
    result = summarize_comps(comps, source_url=source_url)
    _RESULT_CACHE[cache_key] = result
    return result
