"""
JETA industry events / conferences (Master doc TABLE 12) — canonical snake_case.
"""
from __future__ import annotations

from typing import Any, List, Tuple


class JE:
    event_name = 'event_name'
    organizer = 'organizer'
    event_type = 'event_type'
    location_city = 'location_city'
    location_state = 'location_state'
    virtual = 'virtual'
    start_date = 'start_date'
    end_date = 'end_date'
    registration_deadline = 'registration_deadline'
    registration_url = 'registration_url'
    cost = 'cost'
    attending = 'attending'
    registration_status = 'registration_status'
    contacts_met = 'contacts_met'
    follow_ups_needed = 'follow_ups_needed'
    linked_buyers = 'linked_buyers'
    linked_sellers = 'linked_sellers'
    notes = 'notes'
    date_added = 'date_added'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JE.event_name: ('Event Name',),
    JE.organizer: ('Organizer',),
    JE.event_type: ('Event Type',),
    JE.location_city: ('Location City',),
    JE.location_state: ('Location State',),
    JE.virtual: ('Virtual',),
    JE.start_date: ('Start Date',),
    JE.end_date: ('End Date',),
    JE.registration_deadline: ('Registration Deadline',),
    JE.registration_url: ('Registration URL',),
    JE.cost: ('Cost',),
    JE.attending: ('Attending',),
    JE.registration_status: ('Registration Status',),
    JE.contacts_met: ('Contacts Met',),
    JE.follow_ups_needed: ('Follow Ups Needed', 'Follow-ups Needed'),
    JE.linked_buyers: ('Linked Buyers',),
    JE.linked_sellers: ('Linked Sellers',),
    JE.notes: ('Notes',),
    JE.date_added: ('Date Added',),
}


def _je_keys(canonical: str) -> tuple:
    return (canonical,) + _LEGACY.get(canonical, ())


def je_get_raw(f: dict, canonical: str) -> Any:
    for k in _je_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def je_get_str(f: dict, canonical: str) -> str:
    for k in _je_keys(canonical):
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


def je_get_float(f: dict, canonical: str) -> float | None:
    for k in _je_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def je_get_bool(f: dict, canonical: str) -> bool:
    raw = je_get_raw(f, canonical)
    if raw is True:
        return True
    if raw is False or raw is None or raw == '':
        return False
    if isinstance(raw, (int, float)):
        return bool(raw)
    s = str(raw).strip().lower()
    return s in ('true', 'yes', '1', 'checked', 'x')


def je_format_date(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    return s[:10] if s else ''


def je_link_ids(f: dict, canonical: str) -> List[str]:
    raw = je_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []
