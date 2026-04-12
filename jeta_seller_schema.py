"""
JETA_Sellers Airtable field names — canonical snake_case (see workspace schema).
Reads fall back to legacy Title Case fields where older bases still use them.
"""
from __future__ import annotations

import re
from typing import Any, Optional, Set


class JS:
    """Canonical Airtable field names on JETA_Sellers (snake_case)."""

    company_name = 'company_name'
    contact_name = 'contact_name'
    contact_title = 'contact_title'
    contact_email = 'contact_email'
    contact_phone = 'contact_phone'
    company_website = 'company_website'
    company_address = 'company_address'
    city = 'city'
    state = 'state'
    country = 'country'
    seller_type = 'seller_type'
    fuel_products = 'fuel_products'
    storage_location = 'storage_location'
    icao_airports_served = 'icao_airports_served'
    supply_capacity_gal = 'supply_capacity_gal'
    price_per_gallon = 'price_per_gallon'
    price_date = 'price_date'
    loa_on_file = 'loa_on_file'
    loa_expiry = 'loa_expiry'
    supply_docs_uploaded = 'supply_docs_uploaded'
    verification_status = 'verification_status'
    verification_notes = 'verification_notes'
    fraud_score = 'fraud_score'
    fraud_flags = 'fraud_flags'
    blacklist_terms_found = 'blacklist_terms_found'
    relationship_status = 'relationship_status'
    deal_id = 'deal_id'
    padd_region = 'padd_region'
    near_gulf_coast = 'near_gulf_coast'
    notes = 'notes'
    date_added = 'date_added'
    last_updated = 'last_updated'
    source = 'source'


_LEGACY = {
    JS.company_name: ('Company Name',),
    JS.contact_name: ('Contact Name',),
    JS.contact_title: ('Contact Title', 'Title'),
    JS.contact_email: ('Email',),
    JS.contact_phone: ('Phone',),
    JS.company_website: ('Website',),
    JS.company_address: ('Address', 'Company Address'),
    JS.city: ('City',),
    JS.state: ('State',),
    JS.country: ('Country',),
    JS.seller_type: ('Type',),
    JS.fuel_products: ('Fuel Products',),
    JS.storage_location: ('Storage Location',),
    JS.icao_airports_served: ('ICAO Code', 'Airports Served', 'ICAO Airports Served'),
    JS.supply_capacity_gal: ('Supply Capacity', 'Supply Capacity Gal'),
    JS.price_per_gallon: ('Price Per Gallon',),
    JS.price_date: ('Price Date',),
    JS.loa_on_file: ('LOA On File',),
    JS.loa_expiry: ('LOA Expiry',),
    JS.supply_docs_uploaded: ('Supply Docs Uploaded', 'Terminal Storage Docs Uploaded'),
    JS.verification_status: ('Status', 'Verification Status'),
    JS.verification_notes: ('Verification Notes',),
    JS.fraud_score: ('Fraud Score',),
    JS.fraud_flags: ('Fraud Flags',),
    JS.blacklist_terms_found: ('Blacklist Terms Found',),
    JS.relationship_status: ('Relationship Status',),
    JS.deal_id: ('Deal ID',),
    JS.padd_region: ('PADD Region',),
    JS.near_gulf_coast: ('Near Gulf Coast', 'PADD 3 proximity'),
    JS.notes: ('Notes',),
    JS.date_added: ('Date Added',),
    JS.last_updated: ('Last Updated',),
    JS.source: ('Source',),
}


def _js_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def js_get_raw(f: dict, canonical: str) -> Any:
    for k in _js_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def js_get_str(f: dict, canonical: str) -> str:
    for k in _js_keys(canonical):
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


def js_get_bool(f: dict, canonical: str) -> Optional[bool]:
    for k in _js_keys(canonical):
        if k not in f or f[k] is None:
            continue
        v = f[k]
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        s = str(v).strip().lower()
        if s in ('yes', 'true', '1', 'y'):
            return True
        if s in ('no', 'false', '0', 'n'):
            return False
    return None


_ICAO_TOKEN_RE = re.compile(
    r'\b([A-Z][A-Z0-9]{2,3})\b',
    re.IGNORECASE,
)


def js_icao_tokens_from_text(text: str) -> Set[str]:
    """Extract likely ICAO location codes from free text (comma/newline separated, embedded)."""
    if not text or not str(text).strip():
        return set()
    s = str(text).strip().upper()
    out: Set[str] = set()
    if re.fullmatch(r'[A-Z0-9]{3,4}', s):
        out.add(s)
    for m in _ICAO_TOKEN_RE.finditer(s):
        code = m.group(1).upper()
        if len(code) >= 3:
            out.add(code)
    return out


def js_icao_tokens_from_fields(f: dict) -> Set[str]:
    """All ICAO-like codes from icao_airports_served and legacy ICAO fields."""
    combined: Set[str] = set()
    raw = js_get_raw(f, JS.icao_airports_served)
    if raw is not None:
        combined |= js_icao_tokens_from_text(str(raw))
    # Legacy single-code column
    leg = f.get('ICAO Code')
    if leg is not None and str(leg).strip():
        combined |= js_icao_tokens_from_text(str(leg))
    raw_air = f.get('Airport')  # sometimes stores code
    if raw_air is not None and str(raw_air).strip():
        combined |= js_icao_tokens_from_text(str(raw_air))
    return combined


def js_fields_match_icao(f: dict, icao: str) -> bool:
    """True if seller row corresponds to the given ICAO (dedupe)."""
    u = str(icao).strip().upper()
    if len(u) < 3:
        return False
    tokens = js_icao_tokens_from_fields(f)
    return u in tokens
