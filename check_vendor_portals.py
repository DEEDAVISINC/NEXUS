"""
Check if Vendor Portals table exists with various name variations
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Try all possible variations
variations = [
    'VENDOR PORTALS',
    'Vendor Portals',
    'vendor portals',
    'VendorPortals',
    'Vendor_Portals',
    'VENDOR_PORTALS'
]

print("🔍 Checking for Vendor Portals table...\n")

found = False
for name in variations:
    try:
        table = base.table(name)
        records = table.all(max_records=1)
        record_count = len(table.all())
        
        print(f"✅ FOUND: '{name}' ({record_count} records)")
        
        # Show what fields it has
        if record_count > 0:
            print(f"\n📋 Sample fields in '{name}':")
            sample_fields = list(records[0]['fields'].keys())
            for field in sample_fields[:10]:  # Show first 10 fields
                print(f"   - {field}")
        else:
            print(f"   (Table is empty, can't show fields)")
        
        found = True
        break
        
    except Exception as e:
        if '404' in str(e) or 'NOT_FOUND' in str(e):
            print(f"❌ Not found: '{name}'")
        else:
            print(f"⚠️  Error checking '{name}': {str(e)[:50]}")

if not found:
    print("\n❌ NO VENDOR PORTALS TABLE FOUND")
    print("\n💡 You need to create it!")
else:
    print("\n✅ Vendor Portals table EXISTS!")
    print("   You don't need to create it from scratch.")
