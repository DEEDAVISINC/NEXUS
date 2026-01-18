"""
Verify what fields were actually added to both tables
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

print("🔍 Checking what fields you added...\n")
print("="*60)

# Check VENDOR PORTAL
print("\n📋 VENDOR PORTAL TABLE:")
print("="*60)
try:
    vp_table = base.table('VENDOR PORTAL')
    
    # Add a dummy record to see what fields exist
    try:
        test_record = vp_table.create({'Portal Name': '__TEST__'})
        vp_table.delete(test_record['id'])
        print("✅ 'Portal Name' field exists")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
    
    # Try to get existing records to see fields
    records = vp_table.all()
    if records:
        print(f"\n✅ Found {len(records)} existing records")
        print("\nCurrent fields in table:")
        for field_name in records[0]['fields'].keys():
            print(f"   ✓ {field_name}")
    else:
        print("\n⚠️  Table is empty, can't determine fields")
        
except Exception as e:
    print(f"❌ Error accessing VENDOR PORTAL: {e}")

# Check Mining Targets
print("\n\n📋 MINING TARGETS TABLE:")
print("="*60)
try:
    mt_table = base.table('Mining Targets')
    
    # Try to get existing records
    records = mt_table.all()
    if records:
        print(f"\n✅ Found {len(records)} existing records")
        print("\nCurrent fields in table:")
        for field_name in records[0]['fields'].keys():
            print(f"   ✓ {field_name}")
    else:
        print("\n⚠️  Table is empty")
        print("\nTrying to add test record to see what fields exist...")
        try:
            test = mt_table.create({'Target Name': '__TEST__'})
            mt_table.delete(test['id'])
            print("✅ 'Target Name' field exists")
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
        
except Exception as e:
    print(f"❌ Error accessing Mining Targets: {e}")

print("\n" + "="*60)
print("💡 NEXT STEPS:")
print("="*60)
print("\nBased on the errors, you need to add:")
print("\nVENDOR PORTAL missing:")
print("  - Portal URL (type: URL)")
print("\nMining Targets missing:")
print("  - Source Type (type: Single select)")
print("\nAdd these fields in Airtable, then run the script again!")
