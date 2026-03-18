#!/usr/bin/env python3
"""
ADD LAUREN ELKINS (DDC) TO NEXUS CONTACTS
Lauren Elkins - Collection Network Supervisor, DNA Diagnostics Center
DDI/DBA Depointe DNA - DDC collection partner

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
    print("🧬 ADDING LAUREN ELKINS (DDC) TO NEXUS CONTACTS")
    print("="*80 + "\n")

    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return

    contact = {
        'Name': 'Lauren Elkins',
        'Email': 'lelkins@dnacenter.com',
        'Title': 'Collection Network Supervisor',
        'Organization': 'DNA Diagnostics Center (DDC)',
        'Role Category': 'Partner',
        'Notes': '''DDC Collection Network Supervisor. Direct: 513.881.4003. Fax: 513.881.4042. www.dnacenter.com.
Government Contracts: 800.310.9868. Government Emergency: 513.668.4744.
DDI/DBA Depointe DNA – DDC collection partner.
Key contact for Kentucky Child Support Genetic Testing RFP 040 2600000321 (collection sub discussions).
Added Feb 26, 2026.'''
    }

    add_contact(contact)

    print("\n" + "="*80)
    print("✅ LAUREN ELKINS ADDED TO NEXUS CONTACTS")
    print("="*80)
    print("📋 DNA Diagnostics Center - Collection Network Supervisor")
    print("🤝 Partner contact for DDI/DBA Depointe DNA")
    print("\n💡 TIP: Search for 'DDC' or 'Lauren' in GPSS CONTACTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
