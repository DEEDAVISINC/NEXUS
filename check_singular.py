"""
Check for VENDOR PORTAL (singular) variations
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Try singular variations
variations = [
    'VENDOR PORTAL',
    'Vendor Portal',
    'vendor portal',
    'VendorPortal',
]

print("🔍 Checking for VENDOR PORTAL (singular)...\n")

found = False
for name in variations:
    try:
        table = base.table(name)
        records = table.all(max_records=5)
        record_count = len(table.all())
        
        print(f"✅ FOUND IT!!! '{name}' ({record_count} records)")
        
        # Show what fields it has
        if record_count > 0:
            print(f"\n📋 Fields in '{name}':")
            sample_fields = list(records[0]['fields'].keys())
            for field in sample_fields:
                print(f"   - {field}")
            
            print(f"\n📄 Sample data:")
            for i, record in enumerate(records[:3], 1):
                portal_name = record['fields'].get('Portal Name', record['fields'].get('Name', 'Unknown'))
                print(f"   {i}. {portal_name}")
        else:
            print(f"   (Table is empty)")
        
        found = True
        break
        
    except Exception as e:
        if '404' in str(e) or 'NOT_FOUND' in str(e):
            print(f"❌ Not found: '{name}'")
        else:
            print(f"⚠️  Error: '{name}': {str(e)[:80]}")

if found:
    print("\n" + "="*60)
    print("✅ THE TABLE EXISTS!")
    print("="*60)
    print("\n💡 YOU DON'T NEED TO CREATE ANYTHING!")
    print("   The table is already there.")
    print("   Just run the populate script to add portal data.")
else:
    print("\n❌ Still not found. Can you copy the EXACT name from Airtable?")
