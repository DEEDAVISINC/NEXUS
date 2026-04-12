"""
JETA_MarketData Airtable field names — canonical snake_case (IATA weekly snapshot).
Reads fall back to legacy Title Case where older bases still use them.

Manual / dashboard context (add in Airtable alongside IATA sync fields):
  - geopolitical_risk_level — Single select: Low, Elevated, High, Critical
  - active_conflict_regions — Multi: Middle East, Eastern Europe, Asia Pacific,
      North Africa, West Africa, South China Sea, Other
  - hormuz_status, suez_status, bosphorus_status, south_china_sea_status —
      Single select each: Open, Restricted, Closed, Monitoring
      (legacy field names chokepoint_hormuz etc. still read)
  - supply_disruption_alert — Checkbox → dashboard warning banner
  - price_driver — Multi: Crude Oil Rise/Drop, Refinery Outage, Chokepoint Threat,
      Seasonal Demand, Currency Movement, Geopolitical Event, SAF Supply Shift,
      Hurricane/Weather, OPEC Decision, Other
  - crude_oil_price_bbl, jet_crack_spread, war_premium_estimated — Currency ($/bbl)
  - price_trend — Single: Rising, Falling, Stable, Volatile
  - 30_day_forecast — Single: Expect Higher, Expect Lower, Expect Stable, Uncertain
  - escalation_clause_triggered — Checkbox → dashboard prompts fee agreement review
  - market_notes — Long text; analyst_source — Single line (Dee / NEXUS AI / External)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

# Primary key data_id is Auto Number in Airtable — not written by API.


class JMD:
    price_per_barrel = 'price_per_barrel'
    price_per_gallon = 'price_per_gallon'
    week_of = 'week_of'
    prior_week_price = 'prior_week_price'
    week_over_week_change = 'week_over_week_change'
    week_over_week_dir = 'week_over_week_dir'
    source = 'source'
    ytd_average = 'ytd_average'
    # Airtable field names (leading digit — use constants, not invalid Python identifiers)
    f52_week_high = '52_week_high'
    f52_week_low = '52_week_low'
    market_note = 'market_note'
    date_fetched = 'date_fetched'
    # Manual / ops context (edit in Airtable; surfaced on JETA dashboard)
    geopolitical_risk_level = 'geopolitical_risk_level'
    active_conflict_regions = 'active_conflict_regions'
    hormuz_status = 'hormuz_status'
    suez_status = 'suez_status'
    bosphorus_status = 'bosphorus_status'
    south_china_sea_status = 'south_china_sea_status'
    supply_disruption_alert = 'supply_disruption_alert'
    price_driver = 'price_driver'
    crude_oil_price_bbl = 'crude_oil_price_bbl'
    jet_crack_spread = 'jet_crack_spread'
    price_trend = 'price_trend'
    # Airtable field name starts with digit — use constant for API key forecast_30_day
    forecast_30_day = '30_day_forecast'
    war_premium_estimated = 'war_premium_estimated'
    escalation_clause_triggered = 'escalation_clause_triggered'
    market_notes = 'market_notes'
    analyst_source = 'analyst_source'


_LEGACY = {
    JMD.price_per_barrel: ('Price Per Barrel',),
    JMD.price_per_gallon: ('Price Per Gallon',),
    JMD.week_of: ('Week Of', 'Price Date', 'price_date'),
    JMD.prior_week_price: ('Prior Week Price',),
    JMD.week_over_week_change: ('Week Over Week Change', 'WoW Change'),
    JMD.week_over_week_dir: ('Week Over Week Dir', 'WoW Direction'),
    JMD.source: ('Source',),
    JMD.ytd_average: ('YTD Average',),
    JMD.f52_week_high: ('52 Week High',),
    JMD.f52_week_low: ('52 Week Low',),
    JMD.market_note: ('Market Note',),
    JMD.date_fetched: ('Date Fetched',),
    JMD.geopolitical_risk_level: ('Geopolitical Risk Level',),
    JMD.active_conflict_regions: ('Active Conflict Regions',),
    JMD.hormuz_status: ('chokepoint_hormuz', 'Chokepoint Hormuz', 'Hormuz Status'),
    JMD.suez_status: ('chokepoint_suez', 'Chokepoint Suez', 'Suez Status'),
    JMD.bosphorus_status: ('chokepoint_bosphorus', 'Chokepoint Bosphorus', 'Bosphorus Status'),
    JMD.south_china_sea_status: ('South China Sea Status',),
    JMD.supply_disruption_alert: ('Supply Disruption Alert',),
    JMD.price_driver: ('Price Driver', 'price_drivers'),
    JMD.crude_oil_price_bbl: ('Crude Oil Price Bbl', 'Crude Oil Price ($/bbl)'),
    JMD.jet_crack_spread: ('Jet Crack Spread',),
    JMD.price_trend: ('Price Trend',),
    JMD.forecast_30_day: ('30 Day Forecast', 'Forecast 30 Day'),
    JMD.war_premium_estimated: ('War Premium Estimated',),
    JMD.escalation_clause_triggered: ('Escalation Clause Triggered',),
    JMD.market_notes: ('Market Notes',),
    JMD.analyst_source: ('Analyst Source',),
}


def _jmd_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jmd_get_raw(f: dict, canonical: str) -> Any:
    for k in _jmd_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jmd_get_str(f: dict, canonical: str) -> str:
    for k in _jmd_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is None:
            continue
        if isinstance(v, (int, float)):
            s = str(int(v) if isinstance(v, float) and v == int(v) else v)
        else:
            s = str(v).strip()
        if s == '':
            continue
        return s
    return ''


def jmd_get_float(f: dict, canonical: str) -> Optional[float]:
    for k in _jmd_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def jmd_get_bool(f: dict, canonical: str) -> Optional[bool]:
    """Airtable checkbox: True when checked; missing/empty treated as unset (caller may treat as False)."""
    for k in _jmd_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is True or v is False:
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            lo = v.strip().lower()
            if lo in ('true', 'yes', '1', 'on', 'checked'):
                return True
            if lo in ('false', 'no', '0', 'off'):
                return False
    return None


def jmd_get_list(f: dict, canonical: str) -> list:
    """Multi-select or comma-separated text → list of non-empty strings."""
    for k in _jmd_keys(canonical):
        if k not in f or f[k] is None:
            continue
        v = f[k]
        if isinstance(v, list):
            out = []
            for x in v:
                if x is None:
                    continue
                s = str(x).strip()
                if s:
                    out.append(s)
            return out
        s = str(v).strip()
        if not s:
            continue
        if ',' in s:
            return [p.strip() for p in s.split(',') if p.strip()]
        return [s]
    return []


def jmd_format_date_val(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    if 'T' in s:
        return s[:10]
    return s[:10] if s else ''


def jmd_week_sort_key(f: dict) -> str:
    """ISO date string for sorting rows (prefer week_of Monday, then legacy Price Date)."""
    wo = jmd_get_raw(f, JMD.week_of)
    if wo is not None and str(wo).strip():
        return jmd_format_date_val(wo)
    pd = f.get('price_date') or f.get('Price Date')
    return jmd_format_date_val(pd)


def monday_iso_for_date_str(iso_date: str) -> str:
    """Monday (week_of) for the calendar week containing iso_date (YYYY-MM-DD)."""
    try:
        d = datetime.strptime(iso_date[:10], '%Y-%m-%d').date()
    except ValueError:
        return iso_date[:10]
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()


def wow_direction_from_pct(pct: Optional[float]) -> str:
    if pct is None:
        return 'Flat'
    if abs(float(pct)) < 0.0005:
        return 'Flat'
    return 'Up' if float(pct) > 0 else 'Down'


def compute_wow_vs_prior(
    current_ppg: float,
    prior_ppg: Optional[float],
) -> Tuple[Optional[float], str]:
    if prior_ppg is None or prior_ppg == 0:
        return None, 'Flat'
    pct = (float(current_ppg) - float(prior_ppg)) / float(prior_ppg) * 100.0
    return round(pct, 4), wow_direction_from_pct(pct)
