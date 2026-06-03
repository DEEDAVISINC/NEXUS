"""
PRISM Client Intake ↔ Airtable PRISM Orders
============================================
Sync intake submissions to Airtable and read order history by Requestor Email.
Table name: PRISM Orders (NEXUS Command Center base — AIRTABLE_BASE_ID)
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

TABLE_NAME = 'PRISM Orders'

SERVICE_KEY_TO_ORDER_TYPE = {
    'testing-drug': 'Drug Test (DOT)',
    'testing-occhealth': 'Occupational Health',
    'testing-lead': 'Lead Screening',
    'fingerprint': 'Fingerprinting/EFT',
    'background': 'Background Check',
    'dna': 'DNA Collection',
    'nemt': 'NEMT',
    'arena': 'ARENA',
    'event-mobility': 'ARENA',
    'transport': 'NEMT',
    'notary': 'Notary',
    'notary-law-firm': 'Notary',
    'apostille': 'Apostille',
    'process': 'Process Serving',
    'courier': 'Courier/Runner',
    'credentialing': 'Medical Credentialing',
    'workforce': 'Workforce Compliance',
}

PRIORITY_TO_AIRTABLE = {
    'Standard': 'Standard',
    'STAT': 'Emergency',
    'Same Day': 'Rush',
}


def _get_airtable_client():
    try:
        from nexus_backend import AirtableClient
        client = AirtableClient()
        if not client.base_id or not os.environ.get('AIRTABLE_API_KEY'):
            return None
        return client
    except Exception:
        return None


def _escape_formula_string(value: str) -> str:
    return (value or '').replace("'", "\\'")


def parse_date_for_airtable(raw: str) -> Optional[str]:
    """Return YYYY-MM-DD for Airtable date fields."""
    if not raw or raw.strip() in ('', '—'):
        return None
    raw = raw.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}', raw):
        return raw[:10]
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', raw)
    if m:
        month, day, year = m.group(1), m.group(2), m.group(3)
        return f'{year}-{month.zfill(2)}-{day.zfill(2)}'
    try:
        return datetime.fromisoformat(raw.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def format_date_for_portal(raw) -> str:
    """Normalize Airtable or JSON dates to MM/DD/YYYY for portal display."""
    if not raw:
        return ''
    if isinstance(raw, str) and re.match(r'^\d{4}-\d{2}-\d{2}', raw):
        try:
            d = datetime.strptime(raw[:10], '%Y-%m-%d')
            return d.strftime('%m/%d/%Y')
        except ValueError:
            return raw
    return str(raw)


def _details_to_text(details: dict) -> str:
    if not details:
        return ''
    lines = []
    for key, value in details.items():
        if value and str(value).strip() not in ('', '—'):
            label = key.replace('_', ' ').title()
            lines.append(f'{label}: {value}')
    return '\n'.join(lines)


def intake_order_to_airtable_fields(order: dict, intake_payload: Optional[dict] = None) -> Dict[str, Any]:
    """Map NEXUS intake order dict → Airtable PRISM Orders field names."""
    intake_payload = intake_payload or {}
    svc_key = order.get('service_key') or intake_payload.get('service_key', '')
    details = order.get('details') or intake_payload.get('details') or {}
    mobility_lane = (details.get('mobility_lane') or '').upper()
    courier_lane = (details.get('courier_lane') or '').upper()
    if svc_key in ('arena', 'event-mobility') or mobility_lane == 'ARENA':
        service_type = 'ARENA — Event Navigation Administration'
    elif svc_key == 'nemt' and mobility_lane == 'MOB-A':
        service_type = 'NEMT (Medicaid/Plan)'
    elif svc_key == 'nemt' and mobility_lane == 'NEMT':
        service_type = 'NEMT (Medical Mobility)'
    elif svc_key == 'courier' and courier_lane == 'LEGAL':
        service_type = 'Legal Courier / Documents'
    elif svc_key == 'courier' and courier_lane == 'MEDICAL':
        service_type = 'Medical / Pharma Courier'
    else:
        service_type = SERVICE_KEY_TO_ORDER_TYPE.get(
            svc_key,
            order.get('service_label') or svc_key or 'Notary',
        )
    priority = PRIORITY_TO_AIRTABLE.get(order.get('priority', 'Standard'), 'Standard')
    appt_date = parse_date_for_airtable(order.get('date') or intake_payload.get('sched_date', ''))

    details_text = _details_to_text(details)
    notes_parts = [order.get('notes', '')]
    if details_text:
        notes_parts.append('--- Service Details ---\n' + details_text)
    special_instructions = '\n'.join(p for p in notes_parts if p and p.strip())

    billing = order.get('billing') or {}
    fields: Dict[str, Any] = {
        'Order Number': order.get('id', ''),
        'Status': order.get('status', 'New'),
        'Service Type': service_type,
        'Priority': priority,
        'Client': order.get('client', ''),
        'Requestor Email': (order.get('client_email') or '').strip().lower(),
        'Requestor Contact': order.get('client_contact', ''),
        'Requestor Phone': order.get('client_phone', ''),
        'Signer Name': order.get('signer', ''),
        'Signer Phone': order.get('subject_phone', ''),
        'Subject ID': order.get('subject_id', ''),
        'Appointment Time': order.get('time', ''),
        'Appointment Address': order.get('collection_site') or order.get('address', ''),
        'Special Instructions': special_instructions,
        'Routing Email': order.get('routing_email', ''),
        'Intake Source': 'Client Portal',
        'Service Key': svc_key,
        'Payment Method': billing.get('payment_method', intake_payload.get('payment_method', '')),
    }

    if appt_date:
        fields['Appointment Date'] = appt_date

    order_total = billing.get('order_total') or intake_payload.get('order_total')
    if order_total:
        try:
            fields['Order Total'] = float(order_total)
        except (TypeError, ValueError):
            pass

    return {k: v for k, v in fields.items() if v not in (None, '')}


def sync_intake_order_to_airtable(order: dict, intake_payload: Optional[dict] = None) -> Optional[str]:
    """
    Create or update PRISM Orders row. Returns Airtable record id or None.
    Updates existing row when Order Number matches.
    """
    client = _get_airtable_client()
    if not client:
        print('PRISM Airtable: not configured (AIRTABLE_API_KEY / AIRTABLE_BASE_ID)')
        return None

    fields = intake_order_to_airtable_fields(order, intake_payload)
    order_number = fields.get('Order Number')
    if not order_number:
        return None

    try:
        formula = f"{{Order Number}} = '{_escape_formula_string(order_number)}'"
        existing = client.search_records(TABLE_NAME, formula)
        if existing:
            record_id = existing[0]['id']
            client.update_record(TABLE_NAME, record_id, fields)
            print(f'PRISM Airtable: Updated {TABLE_NAME} {order_number} → {record_id}')
            return record_id

        created = client.create_record(TABLE_NAME, fields)
        record_id = created.get('id') if isinstance(created, dict) else None
        print(f'PRISM Airtable: Created {TABLE_NAME} {order_number} → {record_id}')
        return record_id
    except Exception as e:
        print(f'PRISM Airtable sync failed: {e}')
        return None


def airtable_record_to_portal_view(record: dict) -> dict:
    """Map Airtable PRISM Orders record → client portal order shape."""
    f = record.get('fields') or {}
    status = f.get('Status', 'New')
    appt = f.get('Appointment Date', '')
    return {
        'id': f.get('Order Number', record.get('id', '')),
        'type': f.get('Service Key') or f.get('Service Type', ''),
        'service_key': f.get('Service Key', ''),
        'service_label': f.get('Service Type', ''),
        'subject': f.get('Signer Name', '') or '—',
        'date': format_date_for_portal(appt),
        'time': f.get('Appointment Time', ''),
        'timezone': '',
        'location': f.get('Appointment Address', ''),
        'status': _portal_status_from_airtable(status),
        'priority': f.get('Priority', 'Standard'),
        'result': f.get('Result', '') or f.get('Inspection Status', ''),
        'created_at': f.get('Created Date', '') or record.get('createdTime', ''),
        'airtable_record_id': record.get('id'),
    }


def _portal_status_from_airtable(status: str) -> str:
    s = (status or 'New').lower().replace(' ', '_')
    if s in ('complete', 'completed', 'closed', 'verified', 'documentation', 'scanned_back'):
        return 'completed'
    if s in ('in_progress', 'assigned'):
        return 'in_progress'
    if s in ('confirmed', 'scheduled'):
        return 'scheduled'
    return 'pending'


def fetch_portal_orders_by_email(email: str) -> List[dict]:
    """Query PRISM Orders by Requestor Email for client portal."""
    client = _get_airtable_client()
    if not client:
        return []

    email = email.strip().lower()
    if not email or '@' not in email:
        return []

    try:
        formula = f"LOWER({{Requestor Email}}) = '{_escape_formula_string(email)}'"
        records = client.search_records(TABLE_NAME, formula)
        portal = [airtable_record_to_portal_view(r) for r in records]
        portal.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
        return portal
    except Exception as e:
        print(f'PRISM Airtable fetch by email failed: {e}')
        return []


def merge_portal_orders(*order_lists: List[dict]) -> List[dict]:
    """Dedupe portal orders by confirmation / order id."""
    seen = {}
    for lst in order_lists:
        for o in lst or []:
            oid = o.get('id')
            if oid:
                seen[oid] = o
    merged = list(seen.values())
    merged.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
    return merged
