#!/usr/bin/env python3
"""
ADD REMAINING MA190000000912 CONTACTS TO NEXUS
Nate McQueen, Jason Harbitz, Adam Shiffman, Amy Mattson, Williams E. (Chris Echols)

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
    try:
        formula = f"{{Email}} = '{email}'"
        existing = table.all(formula=formula, max_records=1)
        return existing[0] if existing else None
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return None


def add_contact(contact_data):
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
    print("📇 ADDING REMAINING MA190000000912 CONTACTS TO NEXUS")
    print("="*80 + "\n")

    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return

    contacts = [
        {
            'Name': 'Nate McQueen',
            'Email': 'McQueenN@michigan.gov',
            'Title': 'Program Manager',
            'Organization': 'Michigan Department of Health and Human Services (MDHHS)',
            'Role Category': 'Procurement',
            'Notes': '''MDHHS Program Manager for MA190000000912 (earlier change notices).
Medicaid NEMT Broker Wayne/Oakland/Macomb.
Phone: 248-210-0672.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Jason Harbitz',
            'Email': 'Jason.Harbitz@modivcare.com',
            'Title': 'Program Manager',
            'Organization': 'ModivCare Solutions, LLC',
            'Role Category': 'Partner',
            'Notes': '''ModivCare Program Manager for MA190000000912.
Phone: 517-488-9242.
Incumbent NEMT broker - key contact for DDI sub/partnership discussions.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Adam Shiffman',
            'Email': 'Adam.shiffman@modivcare.com',
            'Title': 'Program Manager',
            'Organization': 'ModivCare Solutions, LLC',
            'Role Category': 'Partner',
            'Notes': '''ModivCare Program Manager for MA190000000912.
Incumbent NEMT broker - key contact for DDI sub/partnership discussions.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Amy Mattson',
            'Email': 'Amy.Mattson@modivcare.com',
            'Title': 'Program Manager',
            'Organization': 'ModivCare Solutions, LLC',
            'Role Category': 'Partner',
            'Notes': '''ModivCare Program Manager for MA190000000912.
Phone: 612-416-5566.
Incumbent NEMT broker - key contact for DDI sub/partnership discussions.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Williams E. (formerly Chris Echols)',
            'Email': 'williame@modivcare.com',
            'Title': 'Contractor Contact',
            'Organization': 'ModivCare Solutions, LLC (formerly LogistiCare)',
            'Role Category': 'Partner',
            'Notes': '''ModivCare Contractor Contact for MA190000000912.
Originally listed as Chris Echols (williame@logisticare.com), updated to williame@modivcare.com when LogistiCare became ModivCare.
Main line: 800-486-7647 ext. 2459.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        }
    ]

    for contact in contacts:
        add_contact(contact)

    print("\n" + "="*80)
    print("✅ REMAINING MA190000000912 CONTACTS ADDED TO NEXUS")
    print("="*80)
    print("📋 Nate McQueen - MDHHS Program Manager")
    print("📋 Jason Harbitz - ModivCare Program Manager")
    print("📋 Adam Shiffman - ModivCare Program Manager")
    print("📋 Amy Mattson - ModivCare Program Manager")
    print("📋 Williams E. - ModivCare Contractor Contact")
    print("\n💡 TIP: Search for 'ModivCare' or 'NEMT' in GPSS CONTACTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
