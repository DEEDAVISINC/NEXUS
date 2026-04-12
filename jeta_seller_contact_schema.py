"""
JETA seller contact rows (per JETA_Sellers) — canonical snake_case.
Reads fall back to legacy Title Case where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JSC:
    seller_id = 'seller_id'
    contact_name = 'contact_name'
    contact_title = 'contact_title'
    contact_email = 'contact_email'
    contact_phone = 'contact_phone'
    contact_linkedin = 'contact_linkedin'
    department = 'department'
    decision_authority = 'decision_authority'
    relationship_status = 'relationship_status'
    last_contact_date = 'last_contact_date'
    next_contact_date = 'next_contact_date'
    outreach_notes = 'outreach_notes'
    loa_signatory = 'loa_signatory'
    notes = 'notes'


_LEGACY = {
    JSC.seller_id: ('Seller', 'JETA Seller'),
    JSC.contact_name: ('Contact Name', 'Name'),
    JSC.contact_title: ('Contact Title', 'Title'),
    JSC.contact_email: ('Contact Email', 'Email'),
    JSC.contact_phone: ('Contact Phone', 'Phone'),
    JSC.contact_linkedin: ('Contact LinkedIn', 'LinkedIn', 'LinkedIn URL'),
    JSC.department: ('Department',),
    JSC.decision_authority: ('Decision Authority',),
    JSC.relationship_status: ('Relationship Status',),
    JSC.last_contact_date: ('Last Contact Date',),
    JSC.next_contact_date: ('Next Contact Date',),
    JSC.outreach_notes: ('Outreach Notes',),
    JSC.loa_signatory: ('LOA Signatory',),
    JSC.notes: ('Notes',),
}


def _jsc_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jsc_get_raw(f: dict, canonical: str) -> Any:
    for k in _jsc_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jsc_get_str(f: dict, canonical: str) -> str:
    for k in _jsc_keys(canonical):
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


def jsc_get_bool(f: dict, canonical: str) -> Optional[bool]:
    for k in _jsc_keys(canonical):
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


def jsc_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jsc_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jsc_first_link_id(f: dict, canonical: str) -> str:
    ids = jsc_link_ids(f, canonical)
    return ids[0] if ids else ''


def jsc_format_date(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    return s[:10] if s else ''
