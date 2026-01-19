"""
Check what fields exist in VENDOR PORTAL table
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

print("="*70)
print("VENDOR PORTAL - CURRENT FIELDS")
print("="*70)

vp_table = base.table('VENDOR PORTAL')
records = vp_table.all(max_records=5)

if records:
    # Get all field names from the first few records
    all_fields = set()
    for record in records:
        all_fields.update(record['fields'].keys())
    
    print(f"\n✅ Fields found in VENDOR PORTAL table:\n")
    for i, field in enumerate(sorted(all_fields), 1):
        print(f"   {i}. '{field}'")
    
    print(f"\n📊 Total fields: {len(all_fields)}")
    
    # Check for the specific fields we need
    print("\n" + "="*70)
    print("CHECKING FOR REQUIRED FIELDS")
    print("="*70)
    
    required_fields = {
        'Portal URL': 'URL',
        'Portal Type': 'Single select',
        'Status': 'Single select'
    }
    
    for field_name, field_type in required_fields.items():
        if field_name in all_fields:
            print(f"✅ '{field_name}' - EXISTS")
        else:
            print(f"❌ '{field_name}' - MISSING")
    
    # Show sample data
    print("\n" + "="*70)
    print("SAMPLE RECORDS (first 3)")
    print("="*70)
    
    for i, record in enumerate(records[:3], 1):
        print(f"\n{i}. Portal Name: {record['fields'].get('Portal Name', 'N/A')}")
        print(f"   Portal URL: {record['fields'].get('Portal URL', 'N/A')}")
        print(f"   Portal Type: {record['fields'].get('Portal Type', 'N/A')}")
        print(f"   Status: {record['fields'].get('Status', 'N/A')}")

else:
    print("❌ No records found in VENDOR PORTAL table")

print("\n" + "="*70)
