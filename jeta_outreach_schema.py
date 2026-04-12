"""
JETA_Outreach Airtable field names — canonical snake_case (see workspace schema).
Reads fall back to legacy Title Case where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JO:
    """Canonical Airtable field names on JETA_Outreach (snake_case)."""

    buyer_id = 'buyer_id'
    deal_id = 'deal_id'
    touch_number = 'touch_number'
    channel = 'channel'
    outreach_date = 'outreach_date'
    outreach_time = 'outreach_time'
    subject_line = 'subject_line'
    message_summary = 'message_summary'
    ai_drafted = 'ai_drafted'
    response_received = 'response_received'
    response_date = 'response_date'
    response_type = 'response_type'
    response_notes = 'response_notes'
    next_touch_number = 'next_touch_number'
    next_touch_date = 'next_touch_date'
    next_touch_channel = 'next_touch_channel'
    next_touch_notes = 'next_touch_notes'
    sent_by = 'sent_by'
    follow_up_complete = 'follow_up_complete'
    notes = 'notes'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JO.buyer_id: ('Buyer',),
    JO.deal_id: ('Deal',),
    JO.touch_number: ('Touch Number',),
    JO.channel: ('Channel',),
    JO.outreach_date: ('Touch Date',),
    JO.outreach_time: ('Outreach Time', 'Touch Time'),
    JO.subject_line: ('Subject', 'Subject Line'),
    JO.message_summary: ('Message', 'Message Summary'),
    JO.ai_drafted: ('AI Drafted',),
    JO.response_received: ('Response Received',),
    JO.response_date: ('Response Date',),
    JO.response_type: ('Response Status',),
    JO.response_notes: ('Response Notes',),
    JO.next_touch_number: ('Next Touch Number',),
    JO.next_touch_date: ('Next Touch Date',),
    JO.next_touch_channel: ('Next Touch Channel',),
    JO.next_touch_notes: ('Next Touch Notes',),
    JO.sent_by: ('Sent By',),
    JO.follow_up_complete: ('Follow Up Complete',),
    JO.notes: ('Notes',),
}


def _jo_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jo_get_raw(f: dict, canonical: str) -> Any:
    for k in _jo_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jo_get_str(f: dict, canonical: str) -> str:
    for k in _jo_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is None:
            continue
        if isinstance(v, bool):
            s = 'Yes' if v else ''
        elif isinstance(v, (int, float)):
            s = str(int(v) if isinstance(v, float) and v == int(v) else v)
        else:
            s = str(v).strip()
        if s == '':
            continue
        return s
    return ''


def jo_get_bool(f: dict, canonical: str) -> Optional[bool]:
    for k in _jo_keys(canonical):
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


def jo_get_int(f: dict, canonical: str) -> Optional[int]:
    for k in _jo_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return int(float(f[k]))
        except (TypeError, ValueError):
            continue
    return None


def jo_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jo_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jo_first_link_id(f: dict, canonical: str) -> str:
    ids = jo_link_ids(f, canonical)
    return ids[0] if ids else ''


def jo_response_received_display_string(f: dict) -> str:
    """
    Legacy API used responseReceived as a string (free text).
    Prefer response_notes / message_summary; if checkbox True, non-empty summary or 'Yes'.
    """
    notes = jo_get_str(f, JO.response_notes)
    if notes:
        return notes
    leg_txt = f.get('Response Received')
    if isinstance(leg_txt, str) and leg_txt.strip():
        return leg_txt.strip()
    b = jo_get_bool(f, JO.response_received)
    if b is True:
        return 'Yes'
    if leg_txt is True:
        return 'Yes'
    return ''
