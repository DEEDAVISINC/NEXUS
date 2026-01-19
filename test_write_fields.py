"""
Test if Portal URL, Portal Type, and Status fields exist by trying to write to them
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
print("TESTING IF FIELDS EXIST IN VENDOR PORTAL")
print("="*70)

vp_table = base.table('VENDOR PORTAL')

# Get first record to test with
records = vp_table.all(max_records=1)

if records:
    test_record = records[0]
    record_id = test_record['id']
    portal_name = test_record['fields'].get('Portal Name', 'Unknown')
    
    print(f"\nTesting with record: {portal_name}")
    print(f"Record ID: {record_id}\n")
    
    # Try to update with the fields that should exist
    fields_to_test = {
        'Portal URL': 'https://test.com',
        'Portal Type': 'High Priority',
        'Status': 'Active'
    }
    
    for field_name, test_value in fields_to_test.items():
        try:
            print(f"Testing '{field_name}'... ", end="")
            vp_table.update(record_id, {field_name: test_value})
            print("✅ EXISTS and writable!")
        except Exception as e:
            error_msg = str(e)
            if "Unknown field name" in error_msg:
                print("❌ DOES NOT EXIST")
            elif "invalid" in error_msg.lower():
                print(f"⚠️  EXISTS but value invalid: {error_msg}")
            else:
                print(f"⚠️  Error: {error_msg[:50]}...")
    
    # Clean up - remove test values
    print("\nCleaning up test data...")
    try:
        vp_table.update(record_id, {
            'Portal URL': None,
            'Portal Type': None,
            'Status': None
        })
        print("✅ Test data removed")
    except:
        pass

else:
    print("❌ No records found to test with")

print("\n" + "="*70)
