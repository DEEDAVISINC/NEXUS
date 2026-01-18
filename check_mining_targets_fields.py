"""
Check what fields actually exist in Mining Targets table
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

print("🔍 Checking Mining Targets table...\n")

# Try both variations
for name in ['Mining Targets', 'MINING TARGETS']:
    try:
        table = base.table(name)
        
        # Try to get schema by creating a dummy record
        print(f"✅ Found: '{name}'\n")
        
        # Get all records to see structure
        all_records = table.all()
        
        print(f"📊 Total records: {len(all_records)}")
        
        if len(all_records) > 0:
            print(f"\n📋 CURRENT FIELDS IN TABLE:")
            sample_record = all_records[0]
            fields = sample_record['fields']
            
            for i, field_name in enumerate(fields.keys(), 1):
                field_value = fields[field_name]
                field_type = type(field_value).__name__
                print(f"   {i}. {field_name} ({field_type})")
                
        else:
            print("\n⚠️  Table is EMPTY (0 records)")
            print("   Cannot determine fields without data.")
            print("\n💡 Try adding ONE test record manually in Airtable,")
            print("   then I can see what fields you have.")
            
        break
        
    except Exception as e:
        if '404' not in str(e) and 'NOT_FOUND' not in str(e):
            print(f"⚠️  Error with '{name}': {str(e)}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("\nSince the table is empty, here are the fields you SHOULD have")
print("for the mining system to work:\n")

required_fields = [
    ("Target Name", "Single line text", "PRIMARY"),
    ("Target URL", "URL", ""),
    ("Source Type", "Single select", "Intelligence, Marketplace, Archive, News, Portal"),
    ("Active", "Checkbox", ""),
    ("Description", "Long text", ""),
    ("Keywords", "Long text", ""),
    ("Scraping Method", "Single select", "API, Web Scraping, RSS Feed, Manual"),
    ("Last Scraped", "Date & time", ""),
    ("Scraping Frequency", "Single select", "Hourly, Daily, Twice Daily, Weekly, Manual Only"),
    ("Opportunities Found", "Number", "Integer"),
]

for i, (name, field_type, options) in enumerate(required_fields, 1):
    if options:
        print(f"{i:2d}. {name:25s} → {field_type:20s} ({options})")
    else:
        print(f"{i:2d}. {name:25s} → {field_type}")
