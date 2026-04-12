"""
JETA_BrokerChain (or equivalent) Airtable field names — canonical snake_case.
Reads fall back to legacy Title Case where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JBC:
    """Canonical Airtable field names on IMFPA / broker chain rows (snake_case)."""

    deal_id = 'deal_id'
    broker_position = 'broker_position'
    broker_name = 'broker_name'
    broker_company = 'broker_company'
    broker_email = 'broker_email'
    broker_phone = 'broker_phone'
    broker_address = 'broker_address'
    chain_percentage = 'chain_percentage'
    jeta_introduced = 'jeta_introduced'
    verified = 'verified'
    ncnda_signed = 'ncnda_signed'
    imfpa_signed = 'imfpa_signed'
    payment_info = 'payment_info'
    notes = 'notes'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JBC.deal_id: ('Deal',),
    JBC.broker_position: ('Broker Position', 'Position'),
    JBC.broker_name: ('Broker Name', 'Name'),
    JBC.broker_company: ('Broker Company', 'Company'),
    JBC.broker_email: ('Broker Email', 'Email'),
    JBC.broker_phone: ('Broker Phone', 'Phone'),
    JBC.broker_address: ('Broker Address', 'Address'),
    JBC.chain_percentage: ('Chain Percentage', 'IMFPA %', 'IMFPA Percentage'),
    JBC.jeta_introduced: ('JETA Introduced',),
    JBC.verified: ('Verified',),
    JBC.ncnda_signed: ('NCNDA Signed',),
    JBC.imfpa_signed: ('IMFPA Signed',),
    JBC.payment_info: ('Payment Info',),
    JBC.notes: ('Notes',),
}


def _jbc_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jbc_get_raw(f: dict, canonical: str) -> Any:
    for k in _jbc_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jbc_get_str(f: dict, canonical: str) -> str:
    for k in _jbc_keys(canonical):
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


def jbc_get_float(f: dict, canonical: str) -> Optional[float]:
    for k in _jbc_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def jbc_get_int(f: dict, canonical: str) -> Optional[int]:
    x = jbc_get_float(f, canonical)
    if x is None:
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def jbc_get_bool(f: dict, canonical: str) -> Optional[bool]:
    for k in _jbc_keys(canonical):
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


def jbc_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jbc_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jbc_first_link_id(f: dict, canonical: str) -> str:
    ids = jbc_link_ids(f, canonical)
    return ids[0] if ids else ''
