"""
Check all fields in GPSS SUBCONTRACTORS table - including exact spelling
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("🔍 CHECKING ALL FIELDS IN GPSS SUBCONTRACTORS\n")

# Get table schema by looking at records
try:
    all_records = subs_table.all()
    
    if all_records:
        print(f"Found {len(all_records)} existing records\n")
        print("ALL FIELDS IN TABLE:")
        
        # Collect all unique field names from all records
        all_fields = set()
        for record in all_records:
            for field_name in record['fields'].keys():
                all_fields.add(field_name)
        
        for field_name in sorted(all_fields):
            print(f"  ✅ '{field_name}'")
        
        # Show first record as example
        print(f"\n📋 FIRST RECORD EXAMPLE:")
        print(f"Record ID: {all_records[0]['id']}")
        for field_name, value in all_records[0]['fields'].items():
            print(f"  {field_name}: {value}")
    else:
        print("⚠️  Table is empty - no records found")
        print("\nCannot determine field names from empty table.")
        print("Trying to create a test record to see required fields...")

except Exception as e:
    print(f"❌ ERROR: {e}")
