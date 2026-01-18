"""
Show the EXACT field names that exist in both tables
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
print("EXACT FIELD NAMES IN YOUR TABLES")
print("="*70)

# VENDOR PORTAL
print("\n📋 VENDOR PORTAL TABLE:")
print("-"*70)
try:
    vp_table = base.table('VENDOR PORTAL')
    
    # Create a test record with minimal data
    test_record = vp_table.create({'Portal Name': '__TEST__'})
    
    # Get the record to see all field names
    record = vp_table.get(test_record['id'])
    
    # Delete test record
    vp_table.delete(test_record['id'])
    
    print(f"\nTotal fields: {len(record['fields'])}")
    print("\nField names (copy these exactly):")
    for i, field_name in enumerate(sorted(record['fields'].keys()), 1):
        print(f"   {i}. '{field_name}'")
        
except Exception as e:
    print(f"❌ Error: {e}")

# MINING TARGETS
print("\n\n📋 MINING TARGETS TABLE:")
print("-"*70)
try:
    mt_table = base.table('Mining Targets')
    
    # Create a test record
    test_record = mt_table.create({'Target Name': '__TEST__'})
    
    # Get the record
    record = mt_table.get(test_record['id'])
    
    # Delete test record
    mt_table.delete(test_record['id'])
    
    print(f"\nTotal fields: {len(record['fields'])}")
    print("\nField names (copy these exactly):")
    for i, field_name in enumerate(sorted(record['fields'].keys()), 1):
        print(f"   {i}. '{field_name}'")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
