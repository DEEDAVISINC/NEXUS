"""
Count all portals in VENDOR PORTAL table
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
print("VENDOR PORTAL - ALL RECORDS")
print("="*70)

vp_table = base.table('VENDOR PORTAL')
all_records = vp_table.all()

print(f"\n✅ Total records in VENDOR PORTAL: {len(all_records)}")
print("\nAll portals:")
print("-"*70)

for i, record in enumerate(all_records, 1):
    portal_name = record['fields'].get('Portal Name', 'Unknown')
    record_id = record['id']
    print(f"{i:2}. {portal_name}")

print("\n" + "="*70)
print("MINING TARGETS - ALL RECORDS")
print("="*70)

mt_table = base.table('Mining Targets')
all_targets = mt_table.all()

print(f"\n✅ Total records in Mining Targets: {len(all_targets)}")
print("\nAll targets:")
print("-"*70)

for i, record in enumerate(all_targets, 1):
    target_name = record['fields'].get('Target Name', 'Unknown')
    print(f"{i}. {target_name}")

print("\n" + "="*70)
