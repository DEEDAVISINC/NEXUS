#!/usr/bin/env python3
"""
ADD ALL CONTACTS FROM CONTRACT MA190000000912 (190000000912.pdf)
Extracted from BIDS:RESOURCES/190000000912.pdf - Contract Change Notices

Contacts from document:
- DTMB Contract Administrators: Kyle London, Marissa Gove, Jillian Yeates
- MDHHS Program Managers: Spring McKeever, Ashlee Diaz
- ModivCare (Contractor): Larry Smith

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
    print("📇 ADDING MA190000000912 CONTACTS TO NEXUS (from 190000000912.pdf)")
    print("="*80 + "\n")

    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return

    contacts = [
        {
            'Name': 'Kyle London',
            'Email': 'londonk1@michigan.gov',
            'Title': 'Contract Administrator',
            'Organization': 'State of Michigan / DTMB',
            'Role Category': 'Procurement',
            'Notes': '''DTMB Contract Administrator for MA190000000912.
Contract Change Notice 7 (Feb 2025). Medicaid NEMT Broker Wayne/Oakland/Macomb.
Phone: 517-614-3616.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Marissa Gove',
            'Email': 'govem1@michigan.gov',
            'Title': 'Contract Administrator',
            'Organization': 'State of Michigan / DTMB',
            'Role Category': 'Procurement',
            'Notes': '''DTMB Contract Administrator for MA190000000912.
Contract Change Notices 5, 6, 7. Medicaid NEMT Broker Wayne/Oakland/Macomb.
Phone: 517-449-8952.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Jillian Yeates',
            'Email': 'yeatesj@michigan.gov',
            'Title': 'Contract Administrator',
            'Organization': 'State of Michigan / DTMB',
            'Role Category': 'Procurement',
            'Notes': '''DTMB Contract Administrator for MA190000000912.
Original RFP 190000000198 Solicitation Manager. Contract Change Notice 3 (June 2021).
Phone: 517-275-1131.
Source: BIDS:RESOURCES/190000000912.pdf, RFP 190000000198. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Spring McKeever',
            'Email': 'Mckeevers1@michigan.gov',
            'Title': 'Program Manager',
            'Organization': 'Michigan Department of Health and Human Services (MDHHS)',
            'Role Category': 'Procurement',
            'Notes': '''MDHHS Program Manager for Multi-Agency and Statewide Contracts.
MA190000000912 - Medicaid NEMT Broker Wayne/Oakland/Macomb.
Phone: 517-335-5198.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Ashlee Diaz',
            'Email': 'DiazA8@michigan.gov',
            'Title': 'Program Manager',
            'Organization': 'Michigan Department of Health and Human Services (MDHHS)',
            'Role Category': 'Procurement',
            'Notes': '''MDHHS Program Manager for Multi-Agency and Statewide Contracts.
MA190000000912 - Medicaid NEMT Broker Wayne/Oakland/Macomb.
Phone: 517-241-4056.
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        },
        {
            'Name': 'Larry Smith',
            'Email': 'larry.smith@modivcare.com',
            'Title': 'Sr. Director / Contractor Representative',
            'Organization': 'ModivCare Solutions, LLC (formerly LogistiCare)',
            'Role Category': 'Partner',
            'Notes': '''ModivCare Sr. Director - Contractor Representative for MA190000000912.
Overall responsibility for MDHHS NEMT contract. Michigan-based contact.
Phone: 248-395-5101.
Key contact for DDI to sign up as NEMT transportation provider (sub to ModivCare).
Source: BIDS:RESOURCES/190000000912.pdf. Added Feb 27, 2026.'''
        }
    ]

    for contact in contacts:
        add_contact(contact)

    print("\n" + "="*80)
    print("✅ MA190000000912 CONTACTS ADDED TO NEXUS")
    print("="*80)
    print("📋 Kyle London - DTMB Contract Administrator (CN7)")
    print("📋 Marissa Gove - DTMB Contract Administrator")
    print("📋 Jillian Yeates - DTMB Contract Administrator (original RFP)")
    print("📋 Spring McKeever - MDHHS Program Manager")
    print("📋 Ashlee Diaz - MDHHS Program Manager")
    print("📋 Larry Smith - ModivCare Sr. Director (Contractor)")
    print("\n💡 TIP: Search for 'NEMT' or '190000000912' in GPSS CONTACTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
