#!/usr/bin/env python3
"""
VERTEX Medical Billing — claim scrub + timely-filing gate.

Runs BEFORE generate_claim() creates a VERTEX invoice. Blocks fatal claim
defects; returns warnings for soft issues.

Ironclad rules (Jul 2026):
- Timely filing per payer (Molina LTSS = 365 days from DOS)
- Required member/trip fields present
- NPI stamped
- Mileage sanity
- HCPCS present and payer-compatible where known
- No duplicate open claim for same member + DOS + HCPCS
- HAP eligibility must carry audit stamp (method + timestamp)
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Fallback when VERTEX_PAYER_PROFILES.json has no match
PAYER_TIMELY_FILING_DAYS: Dict[str, int] = {
    "molina": 365,
    "hap": 365,
    "caresource": 365,
    "priority": 365,
    "aetna": 365,
    "mclaren": 365,
    "blue cross": 365,
    "bcc": 365,
    "default": 365,
}

MAX_REASONABLE_LOADED_MILES = 300.0
MIN_REASONABLE_LOADED_MILES = 0.0


def _parse_date(value: Any) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%m/%d/%Y"):
        try:
            if "T" in s and fmt.startswith("%Y-%m-%dT"):
                return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
            if "T" not in s and "T" in fmt:
                continue
            return datetime.strptime(s[:10] if fmt == "%Y-%m-%d" else s, fmt if "T" not in fmt else "%Y-%m-%d").date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _payer_key(payer: Optional[str]) -> str:
    p = (payer or "").lower()
    if "molina" in p:
        return "molina"
    if "caresource" in p or p.startswith("hap"):
        return "hap"
    if "priority" in p:
        return "priority"
    if "aetna" in p:
        return "aetna"
    if "mclaren" in p:
        return "mclaren"
    if "blue cross" in p or "bcc" in p:
        return "blue cross"
    return "default"


def timely_filing_days_for_payer(payer: Optional[str]) -> int:
    try:
        from vertex_payer_profiles import timely_filing_days

        return timely_filing_days(payer, default=PAYER_TIMELY_FILING_DAYS["default"])
    except Exception:
        return PAYER_TIMELY_FILING_DAYS.get(_payer_key(payer), PAYER_TIMELY_FILING_DAYS["default"])


def check_timely_filing(
    *,
    payer: Optional[str],
    date_of_service: Any,
    as_of: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Returns {ok, days_from_dos, limit_days, days_remaining, error}.
    ok=False when past timely filing window.
    """
    as_of = as_of or date.today()
    dos = _parse_date(date_of_service)
    limit = timely_filing_days_for_payer(payer)
    if not dos:
        return {
            "ok": False,
            "days_from_dos": None,
            "limit_days": limit,
            "days_remaining": None,
            "error": "Date of service missing or unparseable — cannot verify timely filing",
        }
    days_from = (as_of - dos).days
    remaining = limit - days_from
    if days_from < 0:
        return {
            "ok": False,
            "days_from_dos": days_from,
            "limit_days": limit,
            "days_remaining": remaining,
            "error": f"Date of service {dos.isoformat()} is in the future",
        }
    if days_from > limit:
        return {
            "ok": False,
            "days_from_dos": days_from,
            "limit_days": limit,
            "days_remaining": remaining,
            "error": (
                f"Timely filing expired for {payer or 'payer'}: "
                f"{days_from} days since DOS {dos.isoformat()} (limit {limit} days)"
            ),
        }
    return {
        "ok": True,
        "days_from_dos": days_from,
        "limit_days": limit,
        "days_remaining": remaining,
        "error": None,
        "warning": (
            f"Timely filing window closing — {remaining} days left of {limit}"
            if remaining is not None and remaining <= 30
            else None
        ),
        "filing_deadline": (dos + timedelta(days=limit)).isoformat(),
    }


def scrub_nemt_trip_for_claim(
    trip: Dict[str, Any],
    *,
    existing_trips: Optional[Dict[str, Dict[str, Any]]] = None,
    as_of: Optional[date] = None,
    require_hap_portal_confirm: bool = True,
) -> Dict[str, Any]:
    """
    Full pre-claim scrub. Raises nothing — returns structured result.

    result = {
      ok: bool,
      blocking: [str],
      warnings: [str],
      timely_filing: {...},
      checks: {...},
    }
    """
    blocking: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, str] = {}

    payer = trip.get("payer")
    try:
        from vertex_payer_profiles import claim_clocks_for_payer, require_hap_portal_confirm as _prof_hap

        # Profile drives HAP portal rule when env not forcing off
        if os.environ.get("VERTEX_HAP_REQUIRE_PORTAL_CONFIRM", "1") == "0":
            require_hap_portal_confirm = False
        else:
            require_hap_portal_confirm = _prof_hap(payer, env_default=require_hap_portal_confirm)
        payer_clocks = claim_clocks_for_payer(payer)
    except Exception:
        payer_clocks = {
            "profile_key": None,
            "timely_filing_days": timely_filing_days_for_payer(payer),
            "dispute_days": None,
            "appeal_days": None,
            "clearinghouse": {},
        }

    medicaid_id = (trip.get("member_medicaid_id") or "").strip()
    if not medicaid_id:
        blocking.append("Member Medicaid ID missing")
        checks["member_medicaid_id"] = "FAIL"
    else:
        checks["member_medicaid_id"] = "PASS"

    for field, label in (
        ("pickup_address", "Pickup address"),
        ("dropoff_address", "Dropoff address"),
        ("hcpcs_code", "HCPCS code"),
    ):
        if not str(trip.get(field) or "").strip():
            blocking.append(f"{label} missing")
            checks[field] = "FAIL"
        else:
            checks[field] = "PASS"

    npi = str(trip.get("provider_npi") or trip.get("npi") or "").strip()
    if npi and npi != "1538939111":
        warnings.append(f"Provider NPI on trip is {npi} — expected 1538939111 (DDI)")
        checks["npi"] = "WARN"
    elif not npi:
        # generate_claim stamps company NPI on invoice; warn only
        warnings.append("Trip missing provider_npi — invoice will stamp company NPI 1538939111")
        checks["npi"] = "WARN"
    else:
        checks["npi"] = "PASS"

    # Mileage
    try:
        miles = float(trip.get("mileage") or 0)
    except (TypeError, ValueError):
        miles = -1
        blocking.append("Mileage is not a number")
        checks["mileage"] = "FAIL"
    else:
        if miles < MIN_REASONABLE_LOADED_MILES:
            blocking.append("Mileage cannot be negative")
            checks["mileage"] = "FAIL"
        elif miles > MAX_REASONABLE_LOADED_MILES:
            blocking.append(
                f"Mileage {miles} exceeds sanity max {MAX_REASONABLE_LOADED_MILES} — verify before billing"
            )
            checks["mileage"] = "FAIL"
        elif miles == 0:
            warnings.append("Mileage is 0 — confirm base-only trip has no loaded miles")
            checks["mileage"] = "WARN"
        else:
            checks["mileage"] = "PASS"

    # DOS / pickup time
    dos_raw = trip.get("date_of_service") or trip.get("pickup_time") or trip.get("service_date")
    filing = check_timely_filing(payer=payer, date_of_service=dos_raw, as_of=as_of)
    if not filing["ok"]:
        blocking.append(filing["error"])
        checks["timely_filing"] = "FAIL"
    else:
        checks["timely_filing"] = "PASS"
        if filing.get("warning"):
            warnings.append(filing["warning"])

    # HAP eligibility audit
    pk = _payer_key(payer)
    if pk == "hap":
        method = (trip.get("eligibility_verification_method") or "").strip()
        verified_at = trip.get("eligibility_verified_at")
        portal_ok = bool(trip.get("eligibility_portal_confirmed"))
        if require_hap_portal_confirm and not portal_ok:
            if not method or not verified_at:
                blocking.append(
                    "HAP eligibility missing audit stamp "
                    "(eligibility_verification_method + eligibility_verified_at). "
                    "Confirm in CareSource/Availity portal and set eligibility_portal_confirmed=True before claim."
                )
                checks["hap_eligibility_audit"] = "FAIL"
            else:
                warnings.append(
                    "HAP eligibility has intake stamp but eligibility_portal_confirmed is False — "
                    "confirm in portal before payer submit"
                )
                checks["hap_eligibility_audit"] = "WARN"
        else:
            checks["hap_eligibility_audit"] = "PASS"

    # Molina hard gates mirrored at claim (defense in depth)
    if pk == "molina":
        try:
            from nemt_billing import (
                MOLINA_LTSS_ATTESTATION_ON_FILE,
                MOLINA_LTSS_AVAILITY_ACTIVE,
            )

            if not MOLINA_LTSS_ATTESTATION_ON_FILE:
                blocking.append("Molina LTSS attestation not on file — cannot generate claim")
                checks["molina_attestation"] = "FAIL"
            else:
                checks["molina_attestation"] = "PASS"
            if not MOLINA_LTSS_AVAILITY_ACTIVE:
                blocking.append("Molina Availity not active — cannot generate claim")
                checks["molina_availity"] = "FAIL"
            else:
                checks["molina_availity"] = "PASS"
        except ImportError:
            warnings.append("Could not import Molina gates for scrub")

    # Duplicate open claim: same member + DOS + HCPCS already invoiced
    if existing_trips and medicaid_id and dos_raw:
        dos = _parse_date(dos_raw)
        hcpcs = str(trip.get("hcpcs_code") or "").strip().upper()
        trip_id = trip.get("trip_id")
        for other_id, other in existing_trips.items():
            if other_id == trip_id:
                continue
            if not other.get("invoice_id"):
                continue
            if (other.get("member_medicaid_id") or "").strip() != medicaid_id:
                continue
            other_dos = _parse_date(
                other.get("date_of_service") or other.get("pickup_time") or other.get("service_date")
            )
            if dos and other_dos and dos == other_dos:
                other_h = str(other.get("hcpcs_code") or "").strip().upper()
                if other_h == hcpcs:
                    blocking.append(
                        f"Duplicate claim risk — trip {other_id} already invoiced "
                        f"for same member + DOS {dos.isoformat()} + HCPCS {hcpcs}"
                    )
                    checks["duplicate"] = "FAIL"
                    break
        else:
            if checks.get("duplicate") != "FAIL":
                checks["duplicate"] = "PASS"

    # Payer-specific HCPCS hints
    hcpcs = str(trip.get("hcpcs_code") or "").strip().upper()
    if pk == "hap" and hcpcs and hcpcs not in ("T2002", "A0130", "T2003", "A0425"):
        warnings.append(f"HCPCS {hcpcs} unusual for HAP CareSource NEMT — verify contract coding")
    if pk == "molina" and hcpcs and hcpcs not in ("T2003", "A0130", "S0215", "S0209", "T1028", "T2038"):
        warnings.append(f"HCPCS {hcpcs} unusual for Molina LTSS NMT/CTS — verify Attachment B coding")

    ok = len(blocking) == 0
    return {
        "ok": ok,
        "blocking": blocking,
        "warnings": warnings,
        "timely_filing": filing,
        "payer_clocks": payer_clocks,
        "checks": checks,
        "scrubbed_at": datetime.utcnow().isoformat() + "Z",
    }


def assert_claim_scrub_pass(trip: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
    """Raise ValueError if scrub fails; return result if pass."""
    existing = kwargs.pop("existing_trips", None)
    result = scrub_nemt_trip_for_claim(trip, existing_trips=existing, **kwargs)
    if not result["ok"]:
        raise ValueError(
            "VERTEX claim scrub FAILED — "
            + "; ".join(result["blocking"])
        )
    return result
