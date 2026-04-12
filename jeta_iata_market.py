"""
JETA — IATA Jet Fuel Price Monitor (https://www.iata.org/en/publications/economics/fuel-monitor/).

Parses the global average jet fuel $/bbl from the public HTML page.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import requests

from jeta_market_data_schema import (
    JMD,
    jmd_format_date_val,
    jmd_get_bool,
    jmd_get_float,
    jmd_get_list,
    jmd_get_raw,
    jmd_get_str,
)

IATA_FUEL_MONITOR_URL = "https://www.iata.org/en/publications/economics/fuel-monitor/"
SOURCE_IATA_FUEL_MONITOR = "IATA Fuel Price Monitor"

# Browser-like UA — some CDNs block generic Python clients
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) "
        "Gecko/20100101 Firefox/128.0"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def parse_jet_fuel_usd_per_bbl_from_html(html: str) -> Optional[float]:
    """
    Extract the headline global average from the Fuel Price Analysis section when possible;
    otherwise the first $.../bbl on the page.
    """
    if not html or not html.strip():
        return None
    lower = html.lower()
    anchor = lower.find("fuel price analysis")
    segment = html[anchor : anchor + 6000] if anchor >= 0 else html
    pat = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*/\s*bbl", re.IGNORECASE)
    m = pat.search(segment)
    if not m:
        m = pat.search(html)
    if not m:
        return None
    raw = m.group(1).replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def fetch_iata_jet_fuel_price_usd_per_bbl(
    *,
    timeout: int = 45,
    session: Optional[requests.Session] = None,
) -> Tuple[Optional[float], str]:
    """
    Download the IATA Fuel Monitor page and parse USD/bbl.
    Returns (price_or_none, error_message).
    """
    sess = session or requests.Session()
    try:
        r = sess.get(IATA_FUEL_MONITOR_URL, headers=_DEFAULT_HEADERS, timeout=timeout)
        r.raise_for_status()
        html = r.text or ""
    except Exception as e:
        return None, str(e)
    price = parse_jet_fuel_usd_per_bbl_from_html(html)
    if price is None:
        return None, "Could not parse $/bbl from IATA Fuel Price Monitor HTML."
    return price, ""


def price_date_today_utc() -> str:
    """ISO date string for Airtable Date fields (YYYY-MM-DD)."""
    return datetime.now(timezone.utc).date().isoformat()


def serialize_market_row(record: Dict[str, Any]) -> Dict[str, Any]:
    """Map Airtable JETA_MarketData record to API camelCase (canonical + legacy fields)."""
    f = record.get("fields") or {}
    ppb_f = jmd_get_float(f, JMD.price_per_barrel)
    ppg_f = jmd_get_float(f, JMD.price_per_gallon)
    if ppg_f is None and ppb_f is not None:
        ppg_f = round(float(ppb_f) / 42.0, 6)

    week_of = jmd_format_date_val(jmd_get_raw(f, JMD.week_of))
    date_fetched = jmd_format_date_val(jmd_get_raw(f, JMD.date_fetched))
    legacy_pd = f.get("price_date") or f.get("Price Date")
    legacy_pd_s = jmd_format_date_val(legacy_pd)
    price_date_display = date_fetched or week_of or legacy_pd_s

    src = jmd_get_str(f, JMD.source) or SOURCE_IATA_FUEL_MONITOR
    wow = jmd_get_float(f, JMD.week_over_week_change)
    wow_dir = jmd_get_str(f, JMD.week_over_week_dir)
    prior = jmd_get_float(f, JMD.prior_week_price)

    geo = jmd_get_str(f, JMD.geopolitical_risk_level)
    regions = jmd_get_list(f, JMD.active_conflict_regions)
    ch_h = jmd_get_str(f, JMD.hormuz_status)
    ch_s = jmd_get_str(f, JMD.suez_status)
    ch_b = jmd_get_str(f, JMD.bosphorus_status)
    ch_scs = jmd_get_str(f, JMD.south_china_sea_status)
    price_drivers = jmd_get_list(f, JMD.price_driver)
    crude_bbl = jmd_get_float(f, JMD.crude_oil_price_bbl)
    jet_crack = jmd_get_float(f, JMD.jet_crack_spread)
    trend = jmd_get_str(f, JMD.price_trend)
    forecast_30 = jmd_get_str(f, JMD.forecast_30_day)
    war_prem = jmd_get_float(f, JMD.war_premium_estimated)
    alert_raw = jmd_get_bool(f, JMD.supply_disruption_alert)
    supply_alert = bool(alert_raw) if alert_raw is not None else False
    esc_raw = jmd_get_bool(f, JMD.escalation_clause_triggered)
    escalation_clause = bool(esc_raw) if esc_raw is not None else False
    notes_long = jmd_get_str(f, JMD.market_notes)
    analyst = jmd_get_str(f, JMD.analyst_source)

    return {
        "id": record.get("id"),
        "pricePerBarrel": ppb_f,
        "pricePerGallon": ppg_f,
        "weekOf": week_of,
        "priorWeekPrice": prior,
        "weekOverWeekChange": wow,
        "weekOverWeekDir": wow_dir,
        "source": src or SOURCE_IATA_FUEL_MONITOR,
        "ytdAverage": jmd_get_float(f, JMD.ytd_average),
        "week52High": jmd_get_float(f, JMD.f52_week_high),
        "week52Low": jmd_get_float(f, JMD.f52_week_low),
        "marketNote": jmd_get_str(f, JMD.market_note),
        "dateFetched": date_fetched,
        "priceDate": price_date_display,
        "geopoliticalRiskLevel": geo or None,
        "activeConflictRegions": regions,
        "chokepointStatus": {
            "hormuz": ch_h or None,
            "suez": ch_s or None,
            "bosphorus": ch_b or None,
            "southChinaSea": ch_scs or None,
        },
        "priceDrivers": price_drivers,
        "crudeOilPriceBbl": crude_bbl,
        "jetCrackSpread": jet_crack,
        "priceTrend": trend or None,
        "forecast30Day": forecast_30 or None,
        "warPremiumEstimated": war_prem,
        "supplyDisruptionAlert": supply_alert,
        "escalationClauseTriggered": escalation_clause,
        "marketNotes": notes_long or None,
        "analystSource": analyst or None,
    }
