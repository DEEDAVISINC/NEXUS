"""
JETA_Buyers Airtable field names — canonical snake_case (see workspace schema).
Reads fall back to legacy Title Case fields where older bases still use them.
"""
from __future__ import annotations

import json
import re
from typing import Any, List, Optional


class JB:
    """Canonical Airtable field names on JETA_Buyers (snake_case)."""

    company_name = 'company_name'
    contact_name = 'contact_name'
    contact_title = 'contact_title'
    contact_email = 'contact_email'
    contact_phone = 'contact_phone'
    airport_name = 'airport_name'
    airport_icao = 'airport_icao'
    airport_faa_code = 'airport_faa_code'
    city = 'city'
    state = 'state'
    country = 'country'
    province = 'province'
    zip_code = 'zip_code'
    buyer_type = 'buyer_type'
    based_aircraft = 'based_aircraft'
    fuel_type = 'fuel_type'
    supplier_status = 'supplier_status'
    current_supplier = 'current_supplier'
    current_ppg = 'current_ppg'
    monthly_volume_gal = 'monthly_volume_gal'
    pipeline_stage = 'pipeline_stage'
    priority_score = 'priority_score'
    score_breakdown = 'score_breakdown'
    tags = 'tags'
    supply_adjacent = 'supply_adjacent'
    canada = 'canada'
    source = 'source'
    contract_status = 'contract_status'
    contract_expiry = 'contract_expiry'
    decision_maker_confirmed = 'decision_maker_confirmed'
    purchasing_authority = 'purchasing_authority'
    last_contact_date = 'last_contact_date'
    next_contact_date = 'next_contact_date'
    next_action = 'next_action'
    outreach_touch = 'outreach_touch'
    response_received = 'response_received'
    response_notes = 'response_notes'
    deal_id = 'deal_id'
    notes = 'notes'
    date_added = 'date_added'
    added_by = 'added_by'
    last_updated = 'last_updated'
    fraud_score = 'fraud_score'
    fraud_flags = 'fraud_flags'
    verified = 'verified'


# Legacy Airtable names (pre–snake_case migration), in try order after canonical.
_LEGACY = {
    JB.company_name: ('Company Name',),
    JB.contact_name: ('Contact Name',),
    JB.contact_title: ('Decision Maker Title',),  # closest legacy
    JB.contact_email: ('Email',),
    JB.contact_phone: ('Phone',),
    JB.airport_name: ('Airport',),
    JB.airport_icao: ('ICAO Code',),
    JB.airport_faa_code: ('FAA Registration',),
    JB.city: ('City',),
    JB.state: ('State',),
    JB.country: ('Country',),
    JB.province: ('Province',),
    JB.zip_code: ('Zip Code', 'ZIP'),
    JB.buyer_type: ('Buyer Type',),
    JB.based_aircraft: ('Based Aircraft Total',),
    JB.fuel_type: ('Fuel Type',),
    JB.supplier_status: ('Supplier Status',),
    JB.current_supplier: ('Seller Product Description',),  # weak legacy
    JB.pipeline_stage: ('Pipeline Stage',),
    JB.priority_score: ('Priority Score',),
    JB.score_breakdown: ('Score Breakdown',),
    JB.tags: ('Priority Tags',),
    JB.supply_adjacent: ('Supply Adjacent',),
    JB.canada: ('Canada',),
    JB.source: ('Source',),
    JB.contract_status: ('Contract Status',),
    JB.purchasing_authority: ('Decision Maker Name',),
    JB.last_contact_date: ('Last Contact Date',),
    JB.next_contact_date: ('Next Touch Date',),
    JB.next_action: ('Next Action',),
    JB.notes: ('Notes',),
    JB.date_added: ('Date Added',),
}


def _jb_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jb_get_raw(f: dict, canonical: str) -> Any:
    """First existing key among canonical + legacy (may be None)."""
    for k in _jb_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jb_get_str(f: dict, canonical: str) -> str:
    """Non-empty string from canonical or legacy."""
    for k in _jb_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is None:
            continue
        s = str(v).strip() if not isinstance(v, (int, float)) else str(int(v) if isinstance(v, float) and v == int(v) else v)
        if s == '':
            continue
        return s
    return ''


def jb_get_float(f: dict, canonical: str) -> Optional[float]:
    for k in _jb_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def jb_geo_state_raw(f: dict) -> str:
    """US state or CA province for geography scoring."""
    s = jb_get_str(f, JB.state)
    if s:
        return s
    return jb_get_str(f, JB.province)


def jb_get_email(f: dict) -> str:
    return jb_get_str(f, JB.contact_email)


def jb_tags_as_list(f: dict) -> list:
    """tags: Multiple Select (list) or legacy Priority Tags JSON string."""
    raw = jb_get_raw(f, JB.tags)
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        t = raw.strip()
        if t.startswith('['):
            try:
                arr = json.loads(t)
                if isinstance(arr, list):
                    return [str(x).strip() for x in arr if str(x).strip()]
            except json.JSONDecodeError:
                pass
        return [t] if t else []
    return []


def jb_pipeline_stage_option(stage_1_to_9: int, stage_labels: list) -> str:
    """Single-select value e.g. 1-Identified … 9-Closed."""
    s = max(1, min(9, int(stage_1_to_9)))
    lab = stage_labels[s - 1] if 1 <= s <= len(stage_labels) else stage_labels[0]
    return f'{s}-{lab}'


def jb_parse_pipeline_stage_int(fields: dict, stage_labels: list) -> int:
    """Read pipeline_stage select or legacy number/label → 1–9."""
    ps = jb_get_raw(fields, JB.pipeline_stage)
    if ps is None or ps == '':
        ps = fields.get('Pipeline Stage')
    if ps is None or ps == '':
        return 1
    if isinstance(ps, (int, float)):
        return max(1, min(9, int(ps)))
    s = str(ps).strip()
    m = re.match(r'^(\d+)', s)
    if m:
        return max(1, min(9, int(m.group(1))))
    for i, lab in enumerate(stage_labels, start=1):
        if lab.lower() in s.lower():
            return i
    return 1


def jb_priority_write_payloads(
    pkg: dict,
    *,
    json_dumps_score: str,
) -> List[dict]:
    """
    Try canonical snake_case first; fallback legacy field names for older bases.
    tags: list for Multiple Select; legacy long text stores JSON array string.
    """
    canonical = {
        JB.priority_score: pkg['priority_score'],
        JB.score_breakdown: json_dumps_score,
        JB.tags: pkg['tags'],
        JB.supply_adjacent: pkg['supply_adjacent'],
        JB.canada: pkg['canada'],
    }
    legacy = {
        'Priority Score': pkg['priority_score'],
        'Score Breakdown': json_dumps_score,
        'Priority Tags': json.dumps(pkg['tags'], separators=(',', ':')),
        'Supply Adjacent': pkg['supply_adjacent'],
        'Canada': pkg['canada'],
    }
    alt_tags_json = {
        JB.priority_score: pkg['priority_score'],
        JB.score_breakdown: json_dumps_score,
        JB.tags: json.dumps(pkg['tags'], separators=(',', ':')),
        JB.supply_adjacent: pkg['supply_adjacent'],
        JB.canada: pkg['canada'],
    }
    return [canonical, legacy, alt_tags_json]
