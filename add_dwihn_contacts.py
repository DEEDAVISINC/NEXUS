#!/usr/bin/env python3
"""
ADD DWIHN CONTACTS TO NEXUS
Adds Jean Mira and Antonio Ziegler from Detroit Wayne Integrated Health Network

Part of NEXUS Backend - Dee Davis Inc
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CONTACTS_TABLE = 'GPSS CONTACTS'

# Initialize Airtable
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
    
    # Check for duplicate
    existing = check_duplicate(email)
    
    try:
        if existing:
            # Update existing
            record_id = existing['id']
            table.update(record_id, contact_data)
            print(f"✅ UPDATED: {name} ({email})")
            return record_id
        else:
            # Add new
            record = table.create(contact_data)
            print(f"✅ ADDED: {name} ({email})")
            return record['id']
    except Exception as e:
        print(f"❌ ERROR adding {name}: {e}")
        return None


def main():
    """Add DWIHN contacts"""
    
    print("\n" + "="*80)
    print("🏥 ADDING DWIHN CONTACTS TO NEXUS")
    print("="*80 + "\n")
    
    # Check environment
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return
    
    # DWIHN Contacts
    contacts = [
        {
            'Name': 'Jean Mira',
            'Email': 'jmira1@dwihn.org',
            'Title': 'Procurement Officer - Phone: 313-344-9099 ext. 3705',
            'Organization': 'Detroit Wayne Integrated Health Network (DWIHN)',
            'Role Category': 'Buyer',
            'Notes': 'Detroit Wayne Integrated Health Network - Regional behavioral health authority serving Detroit and Wayne County. Healthcare procurement. Contact: 313-344-9099 ext. 3705. Added Jan 31, 2026.'
        },
        {
            'Name': 'Antonio Ziegler',
            'Email': 'aziegler@dwihn.org',
            'Title': 'Procurement Officer - Phone: 313-344-9099 ext. 3761',
            'Organization': 'Detroit Wayne Integrated Health Network (DWIHN)',
            'Role Category': 'Buyer',
            'Notes': 'Detroit Wayne Integrated Health Network - Regional behavioral health authority serving Detroit and Wayne County. Healthcare procurement. Contact: 313-344-9099 ext. 3761. Added Jan 31, 2026.'
        }
    ]
    
    # Add both contacts
    for contact in contacts:
        add_contact(contact)
    
    print("\n" + "="*80)
    print("✅ DWIHN CONTACTS ADDED TO NEXUS")
    print("="*80)
    print("📋 Added 2 contacts from Detroit Wayne Integrated Health Network")
    print("🏥 Organization: Regional behavioral health authority")
    print("📍 Location: Detroit/Wayne County, Michigan")
    print("\n💡 TIP: Search for 'DWIHN' in NEXUS CONTACTS to view these contacts")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
