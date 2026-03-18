#!/usr/bin/env python3
"""
ADD MICHIGAN DTMB BUYERS TO NEXUS CONTACTS
Sarah Oumedian - NEMT Brokerage (MA190000000912)
Emily Massa - Medical Specimen Courier (RFP-171-220000002433-2)
Jordana Sager - Category Analyst, Commodities

Part of NEXUS Backend - Dee Davis Inc
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CONTACTS_TABLE = 'GPSS CONTACTS'

api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)


def check_duplicate(email: str):
    """Check if contact already exists"""
    try:
        formula = f"{{Email}} = '{email}'"
        existing = table.all(formula=formula, max_records=1)
        return existing[0] if existing else None
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return None


def add_contact(contact_data):
    """Add or update contact in NEXUS"""
    email = contact_data['Email']
    name = contact_data['Name']
    existing = check_duplicate(email)
    try:
        if existing:
            table.update(existing['id'], contact_data)
            print(f"✅ UPDATED: {name} ({email})")
            return existing['id']
        else:
            record = table.create(contact_data)
            print(f"✅ ADDED: {name} ({email})")
            return record['id']
    except Exception as e:
        print(f"❌ ERROR adding {name}: {e}")
        return None


def main():
    print("\n" + "="*80)
    print("📇 ADDING MICHIGAN DTMB BUYERS TO NEXUS CONTACTS")
    print("="*80 + "\n")

    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return

    contacts = [
        {
            'Name': 'Sarah Oumedian',
            'Email': 'OumedianS@michigan.gov',
            'Title': 'Buyer',
            'Organization': 'State of Michigan / DTMB / MDHHS',
            'Role Category': 'Buyer',
            'Notes': '''Buyer for NEMT Brokerage contract MA190000000912.
Medicaid NEMT Broker for Wayne, Oakland, Macomb Counties. Awarded 7/1/2019, expires 7/31/2026.
Phone: 517-335-1969.
Department 171. Key contact for NEMT brokerage re-compete.
Added Feb 27, 2026.'''
        },
        {
            'Name': 'Emily Massa',
            'Email': 'MassaE@michigan.gov',
            'Title': 'Buyer',
            'Organization': 'State of Michigan / DTMB / Department 171',
            'Role Category': 'Buyer',
            'Notes': '''Buyer for Medical Specimen Courier Services.
RFP-171-220000002433-2 - Medical Specimen Courier Services. Awarded 9/27/2022.
Phone: 517-897-7321.
Department 171. Re-compete opportunity for DDI courier services.
Added Feb 27, 2026.'''
        },
        {
            'Name': 'Jordana Sager',
            'Email': 'SagerJ2@michigan.gov',
            'Title': 'Category Analyst, Commodities',
            'Organization': 'State of Michigan / DTMB - Central Procurement Services, Enterprise Sourcing',
            'Role Category': 'Procurement',
            'Notes': '''Category Analyst, Commodities. Central Procurement Services.
Phone: 517-896-1903.
NOT buyer on NEMT (MA190000000912) - referred to SIGMA for buyer info.
SIGMA: AdvantageVSS (michigan.gov). Contract Connect: michigan.gov/dtmb/procurement/contractconnect.
Added Feb 27, 2026.'''
        }
    ]

    for contact in contacts:
        add_contact(contact)

    print("\n" + "="*80)
    print("✅ MICHIGAN DTMB CONTACTS ADDED TO NEXUS")
    print("="*80)
    print("📋 Sarah Oumedian - NEMT Brokerage buyer (MA190000000912)")
    print("📋 Emily Massa - Medical Specimen Courier buyer (RFP-171)")
    print("📋 Jordana Sager - Category Analyst, Commodities")
    print("\n💡 TIP: Search for 'Michigan' or 'DTMB' in GPSS CONTACTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
