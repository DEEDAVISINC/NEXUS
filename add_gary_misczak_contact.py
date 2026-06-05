#!/usr/bin/env python3
"""
Add Gary Misczak (retired Sonesta Michigan Operations Manager) to GPSS CONTACTS.
Met at Signature Xcel / Grand Strand signing 2026-06-03.
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CONTACTS_TABLE = 'GPSS CONTACTS'

NAME = 'Gary Misczak'

contact_data = {
    'Name': NAME,
    'Title': 'Retired Operations Manager — Sonesta Michigan',
    'Organization': 'Sonesta (Michigan)',
    'Role Category': 'Networking',
    'Notes': '''WARM CONTACT — HAVEN / Sonesta Michigan intro path

Phone (cell): 586-709-1964
Phone (alt — verify): 586-216-4136
Email: UNKNOWN — not on signing order; obtain on follow-up
Location: Warren, MI
Address: 4446 Buchanan Ave, Warren, MI 48092

HOW WE KNOW HIM:
- 3D Ink notary signing 2026-06-03 — routine closing (SIGX-122388)
- Retired Sonesta Michigan Operations Manager — HAVEN warm path only

STRATEGIC VALUE:
- Retired Sonesta Michigan Operations Manager
- Warm intro path vs cold GSO outreach
- File: HAVEN/OUTREACH/SONESTA_MICHIGAN_WARM_CONTACT_MISCZAK.md

RELATIONSHIP: Engaged (in-person)
PRIORITY: Medium — relationship first; no HAVEN pitch on first touch''',
}


def main():
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print('Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID in .env — contact saved in markdown only.')
        print('Files: VENDOR_CLIENT_CONTACTS.md, HAVEN/OUTREACH/SONESTA_MICHIGAN_WARM_CONTACT_MISCZAK.md')
        return

    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)

    formula = f"{{Name}} = '{NAME}'"
    existing = table.all(formula=formula, max_records=1)

    if existing:
        record_id = existing[0]['id']
        table.update(record_id, contact_data)
        print(f'UPDATED GPSS CONTACTS: {NAME} ({record_id})')
    else:
        record = table.create(contact_data)
        print(f'ADDED GPSS CONTACTS: {NAME} ({record["id"]})')

    print('Phone: 586-709-1964 | Email: unknown | Sonesta Michigan retired Ops Manager')


if __name__ == '__main__':
    main()
