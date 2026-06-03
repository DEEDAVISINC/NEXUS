#!/usr/bin/env python3
"""
PRISM Intake — Airtable PRISM Orders Setup
==========================================
Creates or patches the PRISM Orders table in the NEXUS Command Center base
(AIRTABLE_BASE_ID) with fields required for client intake + ops.

Run once:
  python3 setup_prism_intake_airtable.py

Requires AIRTABLE_API_KEY with schema.bases:read and schema.bases:write scopes.
"""
from __future__ import annotations

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

API_KEY = os.environ.get('AIRTABLE_API_KEY', '')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')
TABLE_NAME = 'PRISM Orders'

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}


def txt(name):
    return {'name': name, 'type': 'singleLineText'}


def mltext(name):
    return {'name': name, 'type': 'multilineText'}


def email_f(name):
    return {'name': name, 'type': 'email'}


def phone_f(name):
    return {'name': name, 'type': 'phoneNumber'}


def date_f(name):
    return {'name': name, 'type': 'date', 'options': {'dateFormat': {'name': 'us'}}}


def currency_f(name):
    return {'name': name, 'type': 'currency', 'options': {'precision': 2, 'symbol': '$'}}


def select(name, choices):
    return {
        'name': name,
        'type': 'singleSelect',
        'options': {'choices': [{'name': c} for c in choices]},
    }


STATUS_CHOICES = [
    'New', 'Assigned', 'Confirmed', 'In Progress', 'Completed',
    'Scanned Back', 'Under Review', 'Errors Found', 'Correction Requested',
    'Re-scanned', 'Verified', 'Closed', 'Cancelled',
]

PRIORITY_CHOICES = ['Standard', 'Rush', 'Emergency']

SERVICE_TYPE_CHOICES = [
    'Drug Test (DOT)', 'Drug Test (Non-DOT)', 'DNA Collection', 'Fingerprinting/EFT',
    'NEMT', 'Courier/Runner', 'Notary', 'Notary (RON)', 'Apostille', 'Background Check',
    'Process Serving', 'Occupational Health', 'Lead Screening', 'Medical Credentialing',
    'Workforce Compliance',
]

INTAKE_SOURCE_CHOICES = ['Client Portal', 'Manual', 'Phone', 'Email', 'NEXUS API']

# Fields to ensure exist (compatible with prism_compliance_api.py + intake)
REQUIRED_FIELDS = [
    txt('Order Number'),
    select('Status', STATUS_CHOICES),
    select('Service Type', SERVICE_TYPE_CHOICES),
    select('Priority', PRIORITY_CHOICES),
    txt('Client'),
    txt('Agent'),
    email_f('Requestor Email'),
    txt('Requestor Contact'),
    phone_f('Requestor Phone'),
    txt('Signer Name'),
    phone_f('Signer Phone'),
    txt('Subject ID'),
    date_f('Appointment Date'),
    txt('Appointment Time'),
    mltext('Appointment Address'),
    mltext('Special Instructions'),
    email_f('Routing Email'),
    select('Intake Source', INTAKE_SOURCE_CHOICES),
    txt('Service Key'),
    currency_f('Order Total'),
    txt('Payment Method'),
    date_f('Scanback Upload Date'),
]


def get_base_tables(base_id: str) -> list:
    url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    r = requests.get(url, headers=HEADERS, timeout=30)
    if not r.ok:
        print(f'ERROR reading base schema: {r.status_code} {r.text[:500]}')
        sys.exit(1)
    return r.json().get('tables', [])


def create_table(base_id: str) -> str:
    payload = {
        'name': TABLE_NAME,
        'description': 'PRISM service orders — intake portal, ops queue, QC, billing.',
        'fields': REQUIRED_FIELDS,
    }
    url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    r = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    if not r.ok:
        print(f'ERROR creating table: {r.status_code} {r.text[:800]}')
        sys.exit(1)
    table_id = r.json().get('id')
    print(f'  ✓ Created table {TABLE_NAME} → {table_id}')
    return table_id


def add_field(base_id: str, table_id: str, field: dict) -> bool:
    url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields'
    r = requests.post(url, headers=HEADERS, json=field, timeout=30)
    if r.ok:
        print(f'  ✓ Added field: {field["name"]}')
        return True
    if 'DUPLICATE' in r.text or 'already exists' in r.text.lower():
        print(f'  – Field exists: {field["name"]}')
        return True
    print(f'  ✗ Field {field["name"]}: {r.status_code} {r.text[:300]}')
    return False


def patch_table(base_id: str, table: dict) -> None:
    table_id = table['id']
    existing_names = {f['name'] for f in table.get('fields', [])}
    print(f'  Table {TABLE_NAME} found ({table_id}) — {len(existing_names)} existing fields')

    missing = [f for f in REQUIRED_FIELDS if f['name'] not in existing_names]
    if not missing:
        print('  ✓ All intake fields already present')
        return

    print(f'  Adding {len(missing)} missing field(s) …')
    for field in missing:
        add_field(base_id, table_id, field)
        time.sleep(0.35)


def main() -> None:
    if not API_KEY:
        print('✗ AIRTABLE_API_KEY not set in .env')
        sys.exit(1)
    if not BASE_ID:
        print('✗ AIRTABLE_BASE_ID not set in .env')
        sys.exit(1)

    print('\n══════════════════════════════════════════════════════')
    print('  PRISM Intake — Airtable PRISM Orders Setup')
    print(f'  Base: {BASE_ID}')
    print('══════════════════════════════════════════════════════\n')

    tables = get_base_tables(BASE_ID)
    prism_table = next((t for t in tables if t.get('name') == TABLE_NAME), None)

    if prism_table:
        print(f'Patching existing {TABLE_NAME} …')
        patch_table(BASE_ID, prism_table)
    else:
        print(f'Creating {TABLE_NAME} …')
        create_table(BASE_ID)

    print('\n══════════════════════════════════════════════════════')
    print('  DONE.')
    print('\n  Recommended Airtable views (create manually in UI — one table, all services):')
    print('    • All Orders — Calendar — Calendar on Appointment Date')
    print('    • New Intake — Filter Status = New')
    print('    • By Service Type — Group by Service Type (NEMT, Notary, Drug Test, …)')
    print('    • Optional lane views — Filter Service Type = [one type] for each ops inbox')
    print('      (e.g. NEMT, Notary, Drug Test — same table, different filtered views)')
    print('\n  Next: deploy API with prism_airtable_intake sync enabled.')
    print('══════════════════════════════════════════════════════\n')


if __name__ == '__main__':
    main()
