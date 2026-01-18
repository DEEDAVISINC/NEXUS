"""
Quick script to check what tables exist in your Airtable base
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

print("🔍 Checking Airtable Base...")
print(f"Base ID: {AIRTABLE_BASE_ID}")
print()

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Try to get base schema (list all tables)
try:
    # The pyairtable library doesn't have a direct "list tables" method,
    # but we can try common table names from documentation
    
    test_tables = [
        'VENDOR PORTALS',
        'Vendor Portals',
        'Mining Targets',
        'MINING TARGETS',
        'GPSS OPPORTUNITIES',
        'GPSS Opportunities',
        'GPSS CONTACTS',
        'GPSS Contacts',
        'ATLAS PROJECTS',
        'LBPC Leads',
        'Invoices'
    ]
    
    print("📋 Testing common table names...\n")
    
    existing_tables = []
    
    for table_name in test_tables:
        try:
            table = base.table(table_name)
            records = table.all(max_records=1)  # Just get 1 record to test
            record_count = len(table.all())
            existing_tables.append((table_name, record_count))
            print(f"✅ Found: '{table_name}' ({record_count} records)")
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'NOT_FOUND' in error_msg:
                print(f"❌ Not found: '{table_name}'")
            elif '403' in error_msg or 'FORBIDDEN' in error_msg:
                print(f"🔒 No permission: '{table_name}'")
            else:
                print(f"⚠️  Error with '{table_name}': {error_msg[:50]}...")
    
    print()
    print("=" * 60)
    print("📊 SUMMARY:")
    print("=" * 60)
    
    if existing_tables:
        print(f"\n✅ Found {len(existing_tables)} tables:\n")
        for table_name, count in existing_tables:
            print(f"   - {table_name} ({count} records)")
    else:
        print("\n❌ No tables found! Either:")
        print("   1. Tables haven't been created yet in Airtable")
        print("   2. API key doesn't have permission to this base")
        print("   3. Base ID is incorrect")
    
    print()
    print("💡 NEXT STEPS:")
    if not any('VENDOR' in t[0] or 'Vendor' in t[0] for t in existing_tables):
        print("   - Need to create 'VENDOR PORTALS' table in Airtable")
    if not any('Mining' in t[0] for t in existing_tables):
        print("   - Need to create 'Mining Targets' table in Airtable")
    
    if existing_tables:
        print("   - Tables exist! Ready to populate with data")
    
except Exception as e:
    print(f"❌ Fatal error: {e}")
    print("\nCheck your .env file:")
    print(f"  AIRTABLE_API_KEY = {AIRTABLE_API_KEY[:10]}..." if AIRTABLE_API_KEY else "  AIRTABLE_API_KEY = MISSING")
    print(f"  AIRTABLE_BASE_ID = {AIRTABLE_BASE_ID}")
