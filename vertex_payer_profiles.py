#!/usr/bin/env python3
"""
VERTEX payer profile loader — reads VERTEX_PAYER_PROFILES.json.

Used by claim scrub (timely filing / dispute / appeal clocks) and claim status
machine (clearinghouse IDs stamped on each claim).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional

_BASE = os.path.dirname(os.path.abspath(__file__))
_PROFILES_PATH = os.path.join(_BASE, "VERTEX_PAYER_PROFILES.json")

# Map free-text payer labels → profile keys
_PAYER_ALIASES: Dict[str, str] = {
    "hap caresource": "hap_caresource",
    "hap": "hap_caresource",
    "caresource": "hap_caresource",
    "health alliance plan": "hap_caresource",
    "molina healthcare michigan": "molina_mi_ltss",
    "molina": "molina_mi_ltss",
    "molina healthcare of michigan": "molina_mi_ltss",
}


@lru_cache(maxsize=1)
def load_payer_profiles() -> Dict[str, Any]:
    if not os.path.isfile(_PROFILES_PATH):
        return {"version": None, "payers": {}}
    with open(_PROFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def reload_payer_profiles() -> Dict[str, Any]:
    load_payer_profiles.cache_clear()
    return load_payer_profiles()


def resolve_profile_key(payer: Optional[str]) -> Optional[str]:
    if not payer:
        return None
    p = payer.strip().lower()
    if p in _PAYER_ALIASES:
        return _PAYER_ALIASES[p]
    for alias, key in _PAYER_ALIASES.items():
        if alias in p or p in alias:
            return key
    # Match nexus_code_key from JSON
    data = load_payer_profiles()
    for key, prof in (data.get("payers") or {}).items():
        code = (prof.get("nexus_code_key") or "").strip().lower()
        if code and (code == p or code in p or p in code):
            return key
    return None


def get_payer_profile(payer: Optional[str]) -> Optional[Dict[str, Any]]:
    key = resolve_profile_key(payer)
    if not key:
        return None
    prof = (load_payer_profiles().get("payers") or {}).get(key)
    if not prof:
        return None
    out = dict(prof)
    out["profile_key"] = key
    return out


def timely_filing_days(payer: Optional[str], default: int = 365) -> int:
    prof = get_payer_profile(payer)
    if not prof:
        return default
    val = prof.get("timely_filing_days")
    try:
        return int(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def dispute_days(payer: Optional[str]) -> Optional[int]:
    prof = get_payer_profile(payer)
    if not prof:
        return None
    val = prof.get("dispute_days")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def appeal_days(payer: Optional[str]) -> Optional[int]:
    prof = get_payer_profile(payer)
    if not prof:
        return None
    val = prof.get("appeal_days")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def clearinghouse_snapshot(payer: Optional[str]) -> Dict[str, Any]:
    """IDs to stamp on a claim for 837 / Availity submit."""
    prof = get_payer_profile(payer)
    if not prof:
        return {"clearinghouse": None, "payer_ids": {}, "profile_key": None}
    ch = prof.get("clearinghouse") or {}
    return {
        "profile_key": prof.get("profile_key"),
        "clearinghouse": ch.get("name"),
        "payer_ids": dict(ch.get("payer_ids") or {}),
        "vendor_id": prof.get("vendor_id"),
        "npi": prof.get("npi"),
    }


def require_hap_portal_confirm(payer: Optional[str], env_default: bool = True) -> bool:
    """Profile eligibility flag for HAP; others False unless env forces."""
    key = resolve_profile_key(payer)
    if key != "hap_caresource":
        return False
    prof = get_payer_profile(payer) or {}
    elig = prof.get("eligibility") or {}
    if "require_portal_confirm_before_claim" in elig:
        return bool(elig["require_portal_confirm_before_claim"])
    return env_default


def claim_clocks_for_payer(payer: Optional[str]) -> Dict[str, Any]:
    return {
        "profile_key": resolve_profile_key(payer),
        "timely_filing_days": timely_filing_days(payer),
        "dispute_days": dispute_days(payer),
        "appeal_days": appeal_days(payer),
        "clearinghouse": clearinghouse_snapshot(payer),
    }
