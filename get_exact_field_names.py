"""
Get EXACT field names from a record with the most fields populated
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
print("GETTING EXACT FIELD NAMES FROM YOUR VENDOR PORTAL TABLE")
print("="*70)

vp_table = base.table('VENDOR PORTAL')
all_records = vp_table.all()

print(f"\nAnalyzing {len(all_records)} records...")

# Collect ALL unique field names across ALL records
all_field_names = set()
field_usage_count = {}

for record in all_records:
    for field_name in record['fields'].keys():
        all_field_names.add(field_name)
        field_usage_count[field_name] = field_usage_count.get(field_name, 0) + 1

print(f"\n✅ Found {len(all_field_names)} unique fields across all records:\n")

# Sort by usage count (most used first)
sorted_fields = sorted(field_usage_count.items(), key=lambda x: x[1], reverse=True)

for i, (field_name, count) in enumerate(sorted_fields, 1):
    percentage = (count / len(all_records)) * 100
    print(f"   {i:2}. '{field_name}' - used in {count}/{len(all_records)} records ({percentage:.0f}%)")

# Find the record with the most fields
record_with_most_fields = max(all_records, key=lambda r: len(r['fields']))

print("\n" + "="*70)
print(f"RECORD WITH MOST FIELDS: {record_with_most_fields['fields'].get('Portal Name', 'Unknown')}")
print("="*70)
print(f"\nThis record has {len(record_with_most_fields['fields'])} fields:\n")

for field_name, value in sorted(record_with_most_fields['fields'].items()):
    # Show field name and first 50 chars of value
    if isinstance(value, str):
        display_value = value[:50] + ("..." if len(value) > 50 else "")
    else:
        display_value = str(value)
    print(f"   '{field_name}': {display_value}")

print("\n" + "="*70)
print("COPY THESE EXACT FIELD NAMES FOR YOUR CODE:")
print("="*70)
for field_name in sorted(all_field_names):
    print(f"'{field_name}'")

print("\n" + "="*70)
