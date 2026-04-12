"""
JETA fee agreement — escalation clause selection, populated text, and monitoring helpers.

Version mapping (product rule):
  Spot → Version B (market price adjustment)
  term_length <= 90 days → Version A (fuel price escalation)
  term_length > 90 days → Version C (multi-year provision)
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# --- Term parsing ---------------------------------------------------------------------------

_DAYS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*days?", re.I)
_MONTHS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*months?", re.I)
_WEEKS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*weeks?", re.I)
_YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*years?", re.I)


def parse_term_days(term_length: Optional[str]) -> Optional[int]:
    """Best-effort days from Airtable text like '90 days', '6 months', '1 year'."""
    if term_length is None:
        return None
    s = str(term_length).strip()
    if not s:
        return None
    m = _DAYS_RE.search(s)
    if m:
        return int(round(float(m.group(1))))
    m = _WEEKS_RE.search(s)
    if m:
        return int(round(float(m.group(1)) * 7))
    m = _MONTHS_RE.search(s)
    if m:
        return int(round(float(m.group(1)) * 30.4375))
    m = _YEARS_RE.search(s)
    if m:
        return int(round(float(m.group(1)) * 365.25))
    # Plain number → treat as days
    if s.isdigit():
        return int(s)
    return None


def select_escalation_clause_version(deal_type: Optional[str], term_days: Optional[int]) -> str:
    """
    Returns 'Version A' | 'Version B' | 'Version C'.
    Spot overrides term. Missing term defaults to Version A (short-term-style).
    """
    dt = (deal_type or "").strip().lower()
    if dt == "spot":
        return "Version B"
    if term_days is None:
        return "Version A"
    return "Version C" if term_days > 90 else "Version A"


# --- Populated clause bodies (placeholders filled) ----------------------------------------

def build_version_a_clause(
    *,
    base_fee_per_gallon: float,
    base_benchmark_bbl: float,
    agreement_date: str,
    party_1_line: str,
    party_2_line: str,
) -> str:
    xf = f"{float(base_fee_per_gallon):.4f}"
    xb = f"{float(base_benchmark_bbl):.2f}"
    return f"""FUEL PRICE ESCALATION CLAUSE

Base JETA COURTIÈRE fee of ${xf} per gallon is established at an IATA jet fuel benchmark price of ${xb} per barrel (the "Base Benchmark") as of {agreement_date}.

Party 1: {party_1_line}
Party 2: {party_2_line}

In the event the weekly IATA Jet Fuel Price Monitor benchmark exceeds the Base Benchmark by more than twenty-five dollars ($25.00) per barrel for two (2) consecutive weeks, the JETA COURTIÈRE per-gallon fee shall automatically increase as follows:

  $25.01 - $50.00 above Base:
  Fee increases by $0.005/gallon

  $50.01 - $75.00 above Base:
  Fee increases by $0.010/gallon

  $75.01 - $100.00 above Base:
  Fee increases by $0.015/gallon

  Above $100.00 above Base:
  Parties agree to renegotiate within 5 business days

Fee adjustments are calculated on the first business day following the second consecutive week of threshold breach and applied to all gallons delivered thereafter.

JETA COURTIÈRE shall provide written notice to all parties within 48 hours of any fee adjustment trigger.

Fee reductions shall apply symmetrically if the IATA benchmark falls more than $25.00/bbl below the Base Benchmark for two consecutive weeks."""


def build_version_b_clause(
    *,
    base_benchmark_bbl: float,
    agreement_date: str,
    party_1_line: str,
    party_2_line: str,
) -> str:
    xb = f"{float(base_benchmark_bbl):.2f}"
    return f"""MARKET PRICE ADJUSTMENT

This fee agreement is established at current IATA benchmark pricing of ${xb}/bbl as of {agreement_date}.

Party 1: {party_1_line}
Party 2: {party_2_line}

For spot transactions, JETA COURTIÈRE reserves the right to adjust the agreed fee if the IATA benchmark moves more than 15% from the date of this agreement to the date of fuel delivery. Adjusted fee will be communicated in writing prior to delivery confirmation.

Buyer/Seller acknowledges that jet fuel pricing is subject to global market conditions including geopolitical events, supply disruptions, and currency fluctuations beyond the control of any party."""


def build_version_c_clause(
    *,
    base_fee_per_gallon: float,
    base_benchmark_bbl: float,
    agreement_date: str,
    party_1_line: str,
    party_2_line: str,
) -> str:
    xf = f"{float(base_fee_per_gallon):.4f}"
    xb = f"{float(base_benchmark_bbl):.2f}"
    return f"""MULTI-YEAR PRICE ESCALATION PROVISION

For term agreements exceeding ninety (90) days, the following escalation structure applies. This Agreement is dated {agreement_date} with reference IATA benchmark ${xb}/bbl and base broker fee ${xf}/gallon.

Party 1: {party_1_line}
Party 2: {party_2_line}

ANNUAL REVIEW
On each anniversary of this Agreement, JETA COURTIÈRE fee shall be reviewed against the trailing 52-week average IATA benchmark. If the annual average has increased more than 10% from the prior year average, JETA COURTIÈRE fee shall increase proportionally, not to exceed $0.02/gallon per annual adjustment.

FORCE MAJEURE PRICING EVENT
A Force Majeure Pricing Event is declared when:
  (a) Any major oil transit chokepoint (Strait of Hormuz, Suez Canal, Strait of Bosphorus) is officially closed or restricted by governmental or military action, OR
  (b) IATA benchmark exceeds the Base Benchmark (${xb}/bbl) by more than $75.00/bbl for any period exceeding 14 days

Upon declaration of a Force Majeure Pricing Event, all parties agree to renegotiate fee terms within 10 business days. JETA COURTIÈRE fee during renegotiation period shall default to the Version A escalation schedule (Fuel Price Escalation Clause) referenced herein.

WAR SURCHARGE
In the event of declared armed conflict directly impacting petroleum production or transport in any OPEC member nation, JETA COURTIÈRE may apply a war surcharge not to exceed $0.02/gallon for the duration of the conflict impact period, with 5 business days written notice to all parties."""


def build_fee_schedule_block(
    *,
    fee_per_gallon: Optional[float],
    volume_gallons: Optional[float],
    base_benchmark_bbl: float,
    agreement_date: str,
) -> str:
    fee_s = f"${float(fee_per_gallon):.4f}" if fee_per_gallon is not None else "$[not specified]"
    vol_s = f"{float(volume_gallons):,.0f}" if volume_gallons is not None else "[not specified]"
    bench_s = f"{float(base_benchmark_bbl):.2f}"
    return f"""FEE SCHEDULE

Broker fee: {fee_s} per U.S. gallon (JETA COURTIÈRE).
Estimated volume (illustrative): {vol_s} gallons, subject to actual delivery confirmations.
IATA Jet Fuel Price Monitor benchmark (reference): ${bench_s} per barrel as of {agreement_date}.

This fee schedule is subject to the Price Escalation provisions below."""


# --- Monitoring ---------------------------------------------------------------------------

CLOSED_STAGES = frozenset({"closed won", "closed lost"})


def _deal_fields(rec: dict) -> dict:
    return rec.get("fields") or {}


def deal_is_active_monitoring(stage: str) -> bool:
    s = (stage or "").strip().lower()
    return s not in CLOSED_STAGES


def iata_bbl_from_market_fields(fields: dict) -> Optional[float]:
    """Read price_per_barrel from raw JETA_MarketData fields."""
    from jeta_market_data_schema import JMD, jmd_get_float

    f = fields or {}
    v = jmd_get_float(f, JMD.price_per_barrel)
    if v is not None:
        return float(v)
    # legacy
    for k in ("Price Per Barrel", "price_per_barrel"):
        if k in f and f[k] not in (None, ""):
            try:
                return float(f[k])
            except (TypeError, ValueError):
                continue
    return None


def escalation_threshold_breached_two_weeks(
    *,
    version: str,
    base_bbl: float,
    week0_bbl: Optional[float],
    week1_bbl: Optional[float],
) -> bool:
    """
    Two consecutive weekly IATA snapshots vs per-deal base benchmark.
    Version A/C: > $25/bbl above base both weeks.
    Version B: >15% move from base both weeks (absolute).
    """
    if week0_bbl is None or week1_bbl is None or base_bbl is None:
        return False
    v = (version or "").strip()
    if v == "Version B":
        def pct_ok(w: float) -> bool:
            if base_bbl == 0:
                return False
            return abs(w - base_bbl) / abs(base_bbl) > 0.15

        return pct_ok(week0_bbl) and pct_ok(week1_bbl)
    # Version A / C / default
    thresh = float(base_bbl) + 25.0
    return float(week0_bbl) > thresh and float(week1_bbl) > thresh


def compute_escalation_price_alert(
    *,
    market_records_newest_first: List[dict],
    deal_records: List[dict],
) -> Dict[str, Any]:
    """
    Returns { triggered: bool, affected_count: int, affected_deals: [...], message: str }.
    """
    from jeta_deal_schema import JD, jd_get_float, jd_get_str

    if len(market_records_newest_first) < 2:
        return {
            "triggered": False,
            "affected_count": 0,
            "affected_deals": [],
            "message": "",
        }
    w0 = iata_bbl_from_market_fields(_deal_fields(market_records_newest_first[0]))
    w1 = iata_bbl_from_market_fields(_deal_fields(market_records_newest_first[1]))
    if w0 is None or w1 is None:
        return {
            "triggered": False,
            "affected_count": 0,
            "affected_deals": [],
            "message": "",
        }

    affected: List[Dict[str, str]] = []
    for rec in deal_records:
        f = _deal_fields(rec)
        stage = jd_get_str(f, JD.deal_stage) or str(f.get("Deal Stage") or "").strip()
        if not deal_is_active_monitoring(stage):
            continue
        base = jd_get_float(f, JD.escalation_base_benchmark_bbl)
        if base is None:
            continue
        ver = (jd_get_str(f, JD.escalation_clause_version) or "").strip()
        if ver.lower() in ("none", ""):
            ver = "Version A"
        if not escalation_threshold_breached_two_weeks(
            version=ver,
            base_bbl=float(base),
            week0_bbl=w0,
            week1_bbl=w1,
        ):
            continue
        did = rec.get("id") or ""
        dname = jd_get_str(f, JD.deal_name) or str(f.get("Deal Name") or "").strip()
        affected.append(
            {
                "deal_id": did,
                "deal_name": dname or did,
                "clause_version": ver,
            }
        )

    n = len(affected)
    triggered = n > 0
    msg = ""
    if triggered:
        msg = (
            f"PRICE ALERT: Escalation clause triggered on {n} active deal(s). "
            "Review and notify counterparties within 48 hours."
        )
    return {
        "triggered": triggered,
        "affected_count": n,
        "affected_deals": affected,
        "message": msg,
    }
