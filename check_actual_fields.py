"""
Check ALL actual fields in VENDOR PORTAL table
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
print("ALL FIELDS IN VENDOR PORTAL TABLE")
print("="*70)

vp_table = base.table('VENDOR PORTAL')

# Get ALL records to see all possible fields
records = vp_table.all()

# Collect all unique field names across all records
all_fields = set()
for record in records:
    all_fields.update(record['fields'].keys())

print(f"\n✅ Found {len(all_fields)} fields in VENDOR PORTAL:\n")

for i, field in enumerate(sorted(all_fields), 1):
    print(f"   {i:2}. '{field}'")

# Show sample data
print("\n" + "="*70)
print("SAMPLE RECORD WITH ALL FIELDS")
print("="*70)

# Find a record that has the most fields populated
best_record = max(records, key=lambda r: len(r['fields']))

print(f"\nShowing record: {best_record['fields'].get('Portal Name', 'Unknown')}")
print(f"This record has {len(best_record['fields'])} fields populated:\n")

for field, value in sorted(best_record['fields'].items()):
    # Truncate long values
    if isinstance(value, str) and len(value) > 60:
        value = value[:60] + "..."
    print(f"   {field}: {value}")

print("\n" + "="*70)
