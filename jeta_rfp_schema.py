"""
JETA RFP tracking table — canonical snake_case (see workspace schema).
Reads fall back to legacy Title Case where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JR:
    """Canonical Airtable field names for JETA RFP rows (snake_case)."""

    rfp_title = 'rfp_title'
    issuing_entity = 'issuing_entity'
    entity_type = 'entity_type'
    state = 'state'
    country = 'country'
    fuel_type_required = 'fuel_type_required'
    estimated_volume = 'estimated_volume'
    contract_term = 'contract_term'
    rfp_number = 'rfp_number'
    issue_date = 'issue_date'
    questions_due = 'questions_due'
    submission_deadline = 'submission_deadline'
    award_date = 'award_date'
    submission_method = 'submission_method'
    portal_link = 'portal_link'
    rfp_document_link = 'rfp_document_link'
    status = 'status'
    bid_decision = 'bid_decision'
    no_bid_reason = 'no_bid_reason'
    incumbent = 'incumbent'
    competitors_known = 'competitors_known'
    our_ppg_proposed = 'our_ppg_proposed'
    estimated_fee = 'estimated_fee'
    linked_buyer = 'linked_buyer'
    source = 'source'
    notes = 'notes'
    date_added = 'date_added'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JR.rfp_title: ('RFP Title', 'Title'),
    JR.issuing_entity: ('Issuing Entity',),
    JR.entity_type: ('Entity Type',),
    JR.state: ('State',),
    JR.country: ('Country',),
    JR.fuel_type_required: ('Fuel Type Required', 'Fuel Types'),
    JR.estimated_volume: ('Estimated Volume',),
    JR.contract_term: ('Contract Term',),
    JR.rfp_number: ('RFP Number',),
    JR.issue_date: ('Issue Date',),
    JR.questions_due: ('Questions Due',),
    JR.submission_deadline: ('Submission Deadline',),
    JR.award_date: ('Award Date',),
    JR.submission_method: ('Submission Method',),
    JR.portal_link: ('Portal Link',),
    JR.rfp_document_link: ('RFP Document Link',),
    JR.status: ('Status',),
    JR.bid_decision: ('Bid Decision',),
    JR.no_bid_reason: ('No Bid Reason',),
    JR.incumbent: ('Incumbent',),
    JR.competitors_known: ('Competitors Known',),
    JR.our_ppg_proposed: ('Our PPG Proposed',),
    JR.estimated_fee: ('Estimated Fee',),
    JR.linked_buyer: ('Linked Buyer', 'Buyer'),
    JR.source: ('Source',),
    JR.notes: ('Notes',),
    JR.date_added: ('Date Added',),
}


def _jr_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jr_get_raw(f: dict, canonical: str) -> Any:
    for k in _jr_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jr_get_str(f: dict, canonical: str) -> str:
    for k in _jr_keys(canonical):
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


def jr_get_float(f: dict, canonical: str) -> Optional[float]:
    for k in _jr_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def jr_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jr_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jr_first_link_id(f: dict, canonical: str) -> str:
    ids = jr_link_ids(f, canonical)
    return ids[0] if ids else ''


def jr_fuel_types_list(f: dict) -> List[str]:
    """Multiple select: list of strings, or legacy comma-separated text."""
    raw = jr_get_raw(f, JR.fuel_type_required)
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [x.strip() for x in raw.split(',') if x.strip()]
    return []


def jr_format_date_val(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    return s[:10] if s else ''
