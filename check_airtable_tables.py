"""
Check what tables exist in the Airtable base
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

print("="*70)
print("AIRTABLE BASE VERIFICATION")
print("="*70)
print(f"\nBase ID from .env: {AIRTABLE_BASE_ID}")
print(f"Base ID from your link: appaJZqKVUn3yJ7ma")
print()

if AIRTABLE_BASE_ID == "appaJZqKVUn3yJ7ma":
    print("✅ Base IDs MATCH!")
else:
    print("⚠️  Base IDs DON'T MATCH!")
    print(f"   .env has: {AIRTABLE_BASE_ID}")
    print(f"   Link has: appaJZqKVUn3yJ7ma")

print("\n" + "="*70)
print("CHECKING TABLES IN THIS BASE")
print("="*70)

try:
    api = Api(AIRTABLE_API_KEY)
    base = api.base(AIRTABLE_BASE_ID)
    
    # Try to list common table names
    table_names_to_try = [
        'VENDOR PORTAL',
        'VENDOR PORTALS',
        'Vendor Portal',
        'Vendor Portals',
        'Mining Targets',
        'MINING TARGETS',
        'Mining targets',
        'GPSS OPPORTUNITIES',
        'GPSS Opportunities',
        'Opportunities'
    ]
    
    found_tables = []
    
    for table_name in table_names_to_try:
        try:
            table = base.table(table_name)
            records = table.all(max_records=1)  # Just get 1 record to test
            found_tables.append(table_name)
            print(f"✅ Found table: '{table_name}'")
        except Exception as e:
            # Table doesn't exist or error
            pass
    
    if found_tables:
        print(f"\n✅ Found {len(found_tables)} tables in base {AIRTABLE_BASE_ID}")
        print("\nTables found:")
        for table in found_tables:
            print(f"   - {table}")
    else:
        print(f"\n⚠️  No tables found (or wrong base/API key)")
        
    # Check the specific table from the URL
    print("\n" + "="*70)
    print("CHECKING TABLE FROM YOUR URL")
    print("="*70)
    print(f"Table ID from URL: tblWO4yncFrkI5WpW")
    
    # Try to access by table name from found tables
    if 'VENDOR PORTAL' in found_tables:
        vp_table = base.table('VENDOR PORTAL')
        records = vp_table.all(max_records=3)
        print(f"\n✅ VENDOR PORTAL table has {len(records)} records (showing max 3)")
        if records:
            print("\nSample records:")
            for i, record in enumerate(records[:3], 1):
                portal_name = record['fields'].get('Portal Name', 'Unknown')
                print(f"   {i}. {portal_name}")
                
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThis could mean:")
    print("   1. Wrong AIRTABLE_BASE_ID in .env")
    print("   2. Wrong AIRTABLE_API_KEY")
    print("   3. Tables don't exist yet")

print("\n" + "="*70)
