"""
List all tables and their fields in the base
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
print("ALL TABLES IN BASE: appaJZqKVUn3yJ7ma")
print("="*70)

# List of table names we know exist
known_tables = [
    'VENDOR PORTAL',
    'Vendor Portal',
    'VENDOR PORTALS',
    'Vendor Portals',
    'Mining Targets',
    'GPSS OPPORTUNITIES',
    'GPSS PRODUCTS',
    'GPSS CONTACTS',
    'QUOTES',
    'CONTRACTS',
    'MANUFACTURERS',
    'APPROVALS',
    'CUSTOMERS',
    'COMPETITORS',
    'PRODUCT PIPELINE',
    'PRODUCT RESEARCH',
    'MANUFACTURER OUTREACH'
]

found_tables = {}

for table_name in known_tables:
    try:
        table = base.table(table_name)
        records = table.all(max_records=1)
        
        # Get field names from the first record
        if records:
            fields = list(records[0]['fields'].keys())
            record_count = len(table.all())
            found_tables[table_name] = {
                'fields': fields,
                'count': record_count
            }
    except:
        pass

if found_tables:
    print(f"\n✅ Found {len(found_tables)} tables:\n")
    
    for table_name, info in found_tables.items():
        print(f"\n📋 TABLE: {table_name}")
        print(f"   Records: {info['count']}")
        print(f"   Fields: {', '.join(info['fields'][:5])}" + 
              (f" ... and {len(info['fields'])-5} more" if len(info['fields']) > 5 else ""))

print("\n" + "="*70)
