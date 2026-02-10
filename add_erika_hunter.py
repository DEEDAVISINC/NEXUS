#!/usr/bin/env python3
"""
ADD ERIKA HUNTER (WAYNE COUNTY) TO NEXUS
Quick contact add script

Part of NEXUS Backend - Dee Davis Inc
"""

import os
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


def main():
    """Add Erika Hunter contact"""
    
    print("\n" + "="*80)
    print("🏛️ ADDING ERIKA HUNTER (WAYNE COUNTY) TO NEXUS")
    print("="*80 + "\n")
    
    # Check environment
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        return
    
    # Contact data
    contact = {
        'Name': 'Erika Hunter',
        'Email': 'ehunter@waynecounty.com',
        'Title': 'Procurement Officer - Phone: 313-224-2310',
        'Organization': 'Wayne County',
        'Role Category': 'Buyer',
        'Notes': 'Wayne County procurement officer. Local Michigan county government. Contact: 313-224-2310. Added Jan 31, 2026.'
    }
    
    # Check for duplicate
    existing = check_duplicate(contact['Email'])
    
    try:
        if existing:
            # Update existing
            record_id = existing['id']
            table.update(record_id, contact)
            print(f"✅ UPDATED: {contact['Name']} ({contact['Email']})")
        else:
            # Add new
            record = table.create(contact)
            print(f"✅ ADDED: {contact['Name']} ({contact['Email']})")
    except Exception as e:
        print(f"❌ ERROR adding contact: {e}")
        return
    
    print("\n" + "="*80)
    print("✅ WAYNE COUNTY CONTACT ADDED TO NEXUS")
    print("="*80)
    print("📋 Erika Hunter - ehunter@waynecounty.com")
    print("📞 313-224-2310")
    print("🏛️ Wayne County - Michigan county government")
    print("\n💡 TIP: Search for 'Wayne County' or 'Erika Hunter' in NEXUS CONTACTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
