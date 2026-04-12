"""
JETA fraud / compliance audit log — canonical fields per JETA COURTIÈRE Master (TABLE 11).
Reads fall back to legacy column names (older snake_case + Title Case).
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JFL:
    flagged_record_type = 'flagged_record_type'
    flagged_record_id = 'flagged_record_id'
    flag_level = 'flag_level'
    flag_type = 'flag_type'
    flag_detail = 'flag_detail'
    triggered_by = 'triggered_by'
    action_taken = 'action_taken'
    reviewed_by = 'reviewed_by'
    review_date = 'review_date'
    resolution_notes = 'resolution_notes'
    blacklisted = 'blacklisted'
    date_flagged = 'date_flagged'
    linked_deal = 'linked_deal'
    linked_buyer = 'linked_buyer'
    linked_seller = 'linked_seller'
    # Legacy-only (pre–Master doc); still read when present
    company_name = 'company_name'
    final_decision = 'final_decision'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JFL.flagged_record_type: ('record_type', 'Record Type', 'Flagged Record Type'),
    JFL.flagged_record_id: ('record_id', 'Record ID', 'Linked Record ID', 'Flagged Record ID'),
    JFL.flag_level: ('Flag Level',),
    JFL.flag_type: ('flags_triggered', 'Flags Triggered', 'Flag Type'),
    JFL.flag_detail: ('blacklist_terms', 'Blacklist Terms', 'Flag Detail'),
    JFL.triggered_by: ('Triggered By',),
    JFL.action_taken: ('Action Taken',),
    JFL.reviewed_by: ('Reviewed By',),
    JFL.review_date: ('Review Date',),
    JFL.resolution_notes: ('review_notes', 'Review Notes'),
    JFL.blacklisted: ('Blacklisted',),
    JFL.date_flagged: ('date_logged', 'Date Logged'),
    JFL.linked_deal: ('Linked Deal',),
    JFL.linked_buyer: ('Linked Buyer',),
    JFL.linked_seller: ('Linked Seller',),
    JFL.company_name: ('Company Name',),
    JFL.final_decision: ('Final Decision',),
}


def _jfl_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jfl_get_raw(f: dict, canonical: str) -> Any:
    for k in _jfl_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jfl_get_str(f: dict, canonical: str) -> str:
    for k in _jfl_keys(canonical):
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


def jfl_get_bool(f: dict, canonical: str) -> bool:
    raw = jfl_get_raw(f, canonical)
    if raw is True:
        return True
    if raw is False or raw is None or raw == '':
        return False
    if isinstance(raw, (int, float)):
        return bool(raw)
    s = str(raw).strip().lower()
    return s in ('true', 'yes', '1', 'checked', 'x')


def jfl_flag_type_list(f: dict) -> List[str]:
    raw = jfl_get_raw(f, JFL.flag_type)
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [x.strip() for x in raw.split(',') if x.strip()]
    return []


def jfl_format_date(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    return s[:10] if s else ''


def jfl_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jfl_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jfl_first_link_id(f: dict, canonical: str) -> str:
    ids = jfl_link_ids(f, canonical)
    return ids[0] if ids else ''


def jfl_flagged_record_id_display(f: dict) -> str:
    """Single-line text or legacy numeric/rec id."""
    return jfl_get_str(f, JFL.flagged_record_id)
