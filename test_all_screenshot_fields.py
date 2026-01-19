"""
Test all the fields visible in the screenshot
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
print("TESTING FIELDS FROM SCREENSHOT")
print("="*70)

vp_table = base.table('VENDOR PORTAL')

# Get first record with Portal Name
records = vp_table.all(max_records=5)
test_record = None
for r in records:
    if r['fields'].get('Portal Name'):
        test_record = r
        break

if test_record:
    record_id = test_record['id']
    portal_name = test_record['fields'].get('Portal Name', 'Unknown')
    
    print(f"\nTesting with: {portal_name}")
    print(f"Record ID: {record_id}\n")
    
    # Fields visible in screenshot
    screenshot_fields = {
        'Portal Name': 'TEST',
        'URL': 'https://test.com',
        'Category': 'Test Category',
        'Portal Type': 'High Priority',
        'AUTO-MINING': True,
        'Keywords': 'test, keywords',
        'Search Enabled': True,
        'Search URL': 'https://search.test.com',
        'Status': 'Active'
    }
    
    results = {}
    
    for field_name in screenshot_fields.keys():
        try:
            print(f"Testing '{field_name}'... ", end="")
            # Try with simple test value
            test_val = 'test_value'
            vp_table.update(record_id, {field_name: test_val})
            print("✅ EXISTS")
            results[field_name] = 'EXISTS'
            
            # Clean up
            vp_table.update(record_id, {field_name: None})
        except Exception as e:
            error_msg = str(e)
            if "Unknown field name" in error_msg:
                print("❌ DOES NOT EXIST")
                results[field_name] = 'MISSING'
            else:
                # Field exists but value was wrong
                print(f"⚠️  EXISTS (but test value wrong)")
                results[field_name] = 'EXISTS'
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    existing = [f for f, status in results.items() if status == 'EXISTS']
    missing = [f for f, status in results.items() if status == 'MISSING']
    
    if existing:
        print(f"\n✅ EXISTING FIELDS ({len(existing)}):")
        for f in existing:
            print(f"   - {f}")
    
    if missing:
        print(f"\n❌ MISSING FIELDS ({len(missing)}):")
        for f in missing:
            print(f"   - {f}")

else:
    print("❌ No test record found")

print("\n" + "="*70)
