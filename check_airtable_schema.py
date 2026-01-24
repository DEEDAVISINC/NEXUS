"""
Check actual field names in Airtable tables
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

print("🔍 CHECKING AIRTABLE SCHEMA...\n")

# Check GPSS OPPORTUNITIES
try:
    print("=" * 70)
    print("📊 GPSS OPPORTUNITIES TABLE\n")
    opportunities = api.table(base_id, 'GPSS OPPORTUNITIES')
    records = opportunities.all(max_records=1)
    if records:
        print("✅ Table exists!")
        print(f"\nAvailable fields:")
        for field_name in sorted(records[0]['fields'].keys()):
            print(f"  - {field_name}")
    else:
        print("⚠️  Table exists but is empty")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Check GPSS SUBCONTRACTORS
try:
    print("\n" + "=" * 70)
    print("👥 GPSS SUBCONTRACTORS TABLE\n")
    subs = api.table(base_id, 'GPSS SUBCONTRACTORS')
    records = subs.all(max_records=1)
    if records:
        print("✅ Table exists!")
        print(f"\nAvailable fields:")
        for field_name in sorted(records[0]['fields'].keys()):
            print(f"  - {field_name}")
    else:
        print("⚠️  Table exists but is empty - need to check schema another way")
        print("Creating a test record to see required fields...")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Check GPSS SUBCONTRACTOR QUOTES
try:
    print("\n" + "=" * 70)
    print("💬 GPSS SUBCONTRACTOR QUOTES TABLE\n")
    quotes = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')
    records = quotes.all(max_records=1)
    if records:
        print("✅ Table exists!")
        print(f"\nAvailable fields:")
        for field_name in sorted(records[0]['fields'].keys()):
            print(f"  - {field_name}")
    else:
        print("⚠️  Table exists but is empty")
except Exception as e:
    print(f"❌ ERROR: {e}")

# List all tables in base
try:
    print("\n" + "=" * 70)
    print("📋 ALL TABLES IN BASE\n")
    from pyairtable import Base
    base = Base(os.environ.get('AIRTABLE_API_KEY'), base_id)
    # Note: pyairtable doesn't have direct base.tables() method
    # We'll try common table names
    common_tables = [
        'GPSS OPPORTUNITIES',
        'GPSS CONTACTS',
        'GPSS PRODUCTS',
        'GPSS SUPPLIERS',
        'GPSS SUBCONTRACTORS',
        'GPSS SUBCONTRACTOR QUOTES',
        'ATLAS Projects',
        'Invoices',
        'Vendor Portals'
    ]
    
    print("Checking for common tables:")
    for table_name in common_tables:
        try:
            t = api.table(base_id, table_name)
            count = len(t.all(max_records=1))
            print(f"  ✅ {table_name} - {count} record(s)")
        except:
            print(f"  ❌ {table_name} - Not found")
            
except Exception as e:
    print(f"Error: {e}")
