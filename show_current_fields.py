"""
Show exactly what fields exist in both tables right now
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
print("CURRENT FIELDS IN YOUR AIRTABLE TABLES")
print("="*70)

# VENDOR PORTAL
print("\n📋 VENDOR PORTAL TABLE:")
print("-"*70)
try:
    vp_table = base.table('VENDOR PORTAL')
    
    # Create a test record with all the fields we need
    test_data = {
        'Portal Name': '__FIELD_TEST__'
    }
    
    # Try each field
    fields_to_test = [
        'Portal URL',
        'Portal Type', 
        'Auto-Mining Enabled',
        'Search Enabled',
        'Description',
        'Keywords',
        'Category',
        'Icon'
    ]
    
    existing_fields = ['Portal Name', 'Added Date']  # We know these exist
    
    for field in fields_to_test:
        try:
            test = vp_table.create({field: 'test'})
            vp_table.delete(test['id'])
            existing_fields.append(field)
        except:
            pass
    
    print(f"\n✅ Fields that EXIST ({len(existing_fields)}):")
    for f in existing_fields:
        print(f"   ✓ {f}")
    
    missing = [f for f in fields_to_test if f not in existing_fields]
    if missing:
        print(f"\n❌ Fields that are MISSING ({len(missing)}):")
        for f in missing:
            print(f"   ✗ {f}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# MINING TARGETS
print("\n\n📋 MINING TARGETS TABLE:")
print("-"*70)
try:
    mt_table = base.table('Mining Targets')
    
    fields_to_test = [
        'Target URL',
        'Source Type',
        'Active',
        'Description',
        'Keywords',
        'Scraping Method',
        'Last Scraped',
        'Scraping Frequency',
        'Opportunities Found'
    ]
    
    existing_fields = ['Target Name']  # We know this exists
    
    for field in fields_to_test:
        try:
            test = mt_table.create({field: 'test' if field != 'Active' else True})
            mt_table.delete(test['id'])
            existing_fields.append(field)
        except:
            pass
    
    print(f"\n✅ Fields that EXIST ({len(existing_fields)}):")
    for f in existing_fields:
        print(f"   ✓ {f}")
    
    missing = [f for f in fields_to_test if f not in existing_fields]
    if missing:
        print(f"\n❌ Fields that are MISSING ({len(missing)}):")
        for f in missing:
            print(f"   ✗ {f}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\nIf you see missing fields above, you need to add them in Airtable.")
print("Once all fields exist, the populate script will work!")
