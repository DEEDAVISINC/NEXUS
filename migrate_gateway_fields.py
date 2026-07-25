#!/usr/bin/env python3
"""
One-off migration: add GATEWAY (self-service portal) fields to the
'NEXUS HR ONBOARDING' Airtable table.

Adds:
  EMAIL                 (singleLineText)  — portal login lookup key
  DOCUMENTS              (multipleAttachments) — uploaded doc files
  DOCUMENTS_JSON         (multilineText)   — metadata mirror (local-fallback source of truth)
  ACKNOWLEDGMENTS_JSON   (multilineText)   — typed-name e-sign log
  PORTAL_ACTIVITY_JSON   (multilineText)   — last login / visit count / IP from gateway.deedavis.biz

Safe to re-run — skips fields that already exist.
"""
import os
import sys

try:
    from pyairtable import Api
except ImportError:
    print("pyairtable not installed — run: pip install pyairtable")
    sys.exit(1)

API_KEY = os.environ.get('AIRTABLE_API_KEY', '')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')
TABLE_NAME = 'NEXUS HR ONBOARDING'

if not API_KEY or not BASE_ID:
    # Try loading from .env manually if not already in the environment
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('AIRTABLE_API_KEY='):
                    API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                elif line.startswith('AIRTABLE_BASE_ID='):
                    BASE_ID = line.split('=', 1)[1].strip().strip('"').strip("'")

if not API_KEY or not BASE_ID:
    print("Missing AIRTABLE_API_KEY / AIRTABLE_BASE_ID (checked env + .env)")
    sys.exit(1)

api = Api(API_KEY)
base = api.base(BASE_ID)

# Find the table schema by name (for reading existing field names + table ID —
# the fields-creation endpoint 404s on table NAME, needs table ID).
tables = base.schema().tables
table_schema = next((t for t in tables if t.name == TABLE_NAME), None)
if not table_schema:
    print(f'Table "{TABLE_NAME}" not found in base. Nothing to migrate — GATEWAY will run in local-JSON fallback mode.')
    sys.exit(0)

table = api.table(BASE_ID, table_schema.id)
existing_field_names = {f.name for f in table_schema.fields}
print(f'Existing fields on "{TABLE_NAME}": {sorted(existing_field_names)}')

to_add = [
    ('EMAIL', 'singleLineText', None),
    ('DOCUMENTS', 'multipleAttachments', None),
    ('DOCUMENTS_JSON', 'multilineText', None),
    ('ACKNOWLEDGMENTS_JSON', 'multilineText', None),
    ('PORTAL_ACTIVITY_JSON', 'multilineText', None),
]

for field_name, field_type, options in to_add:
    if field_name in existing_field_names:
        print(f'  [skip] {field_name} already exists')
        continue
    try:
        table.create_field(name=field_name, field_type=field_type, options=options)
        print(f'  [added] {field_name} ({field_type})')
    except Exception as e:
        print(f'  [ERROR] could not add {field_name}: {e}')

print('Done.')
