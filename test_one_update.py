"""
Test updating ONE record to see the full error message
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

vp_table = base.table('VENDOR PORTAL')

# Get first record
records = vp_table.all(max_records=1)

if records:
    record = records[0]
    print("Testing with record:")
    print(f"  Portal Name: {record['fields'].get('Portal Name', 'N/A')}")
    print(f"  Record ID: {record['id']}")
    print()
    
    # Test each field individually
    test_fields = {
        'Portal Type': 'HIGH PRIORITY',
        'Category': 'GOVERNMENT',
        'Status': 'ACTIVE'
    }
    
    for field_name, value in test_fields.items():
        print(f"Testing '{field_name}' = '{value}'...")
        try:
            vp_table.update(record['id'], {field_name: value})
            print(f"  ✅ SUCCESS!")
            # Clean up
            vp_table.update(record['id'], {field_name: None})
        except Exception as e:
            print(f"  ❌ FAILED!")
            print(f"  Full error: {e}")
            print()
