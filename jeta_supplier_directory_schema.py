"""
JETA_SupplierDirectory Airtable field names — canonical snake_case (see workspace schema).
Used for dual-read/write with legacy Title Case where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional


class JSD:
    """Canonical Airtable field names on JETA_SupplierDirectory (snake_case)."""

    icao_code = 'icao_code'
    airport_name = 'airport_name'
    city = 'city'
    state = 'state'
    country = 'country'
    supplier_name = 'supplier_name'
    supplier_type = 'supplier_type'
    fuel_types_offered = 'fuel_types_offered'
    branded_program = 'branded_program'
    open_to_broker = 'open_to_broker'
    date_looked_up = 'date_looked_up'
    source = 'source'
    buyer_id = 'buyer_id'
    notes = 'notes'


_LEGACY = {
    JSD.icao_code: ('ICAO Code',),
    JSD.airport_name: ('Airport Name',),
    JSD.city: ('City',),
    JSD.state: ('State',),
    JSD.country: ('Country',),
    JSD.supplier_name: ('Supplier Name',),
    JSD.supplier_type: ('Supplier Type',),
    JSD.fuel_types_offered: ('Fuel Types Offered',),
    JSD.branded_program: ('Branded Program',),
    JSD.open_to_broker: ('Open To Broker',),
    JSD.date_looked_up: ('Date Looked Up',),
    JSD.source: ('Source',),
    JSD.buyer_id: ('Buyer',),
    JSD.notes: ('Notes',),
}


def jsd_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jsd_get_raw(f: dict, canonical: str) -> Any:
    for k in jsd_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jsd_get_str(f: dict, canonical: str) -> str:
    for k in jsd_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is None:
            continue
        s = str(v).strip() if not isinstance(v, (int, float)) else str(v)
        if s:
            return s
    return ''
