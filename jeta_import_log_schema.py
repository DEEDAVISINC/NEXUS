"""
JETA airport / facility import batch log — canonical snake_case.
Reads fall back to legacy Title Case where older bases still use them.
"""
from __future__ import annotations

import json
from typing import Any, Optional, Tuple


class JIL:
    import_source = 'import_source'
    import_date = 'import_date'
    file_name = 'file_name'
    total_processed = 'total_processed'
    total_imported = 'total_imported'
    total_skipped = 'total_skipped'
    total_filtered = 'total_filtered'
    breakdown_by_state = 'breakdown_by_state'
    breakdown_by_type = 'breakdown_by_type'
    errors = 'errors'
    imported_by = 'imported_by'
    notes = 'notes'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JIL.import_source: ('Import Source',),
    JIL.import_date: ('Import Date',),
    JIL.file_name: ('File Name',),
    JIL.total_processed: ('Total Processed',),
    JIL.total_imported: ('Total Imported',),
    JIL.total_skipped: ('Total Skipped',),
    JIL.total_filtered: ('Total Filtered',),
    JIL.breakdown_by_state: ('Breakdown By State', 'Breakdown by State'),
    JIL.breakdown_by_type: ('Breakdown By Type', 'Breakdown by Type'),
    JIL.errors: ('Errors',),
    JIL.imported_by: ('Imported By',),
    JIL.notes: ('Notes',),
}


def _jil_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jil_get_raw(f: dict, canonical: str) -> Any:
    for k in _jil_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jil_get_str(f: dict, canonical: str) -> str:
    for k in _jil_keys(canonical):
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


def jil_get_int(f: dict, canonical: str) -> Optional[int]:
    for k in _jil_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return int(float(f[k]))
        except (TypeError, ValueError):
            continue
    return None


def jil_format_date(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    return s[:10] if s else ''


def jil_long_text_as_json_str(val: Any) -> str:
    """Normalize long-text JSON fields: accept dict/list or JSON string."""
    if val is None:
        return ''
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False, separators=(',', ':'))
    s = str(val).strip()
    return s
