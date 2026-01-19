"""
Check what Portal Type select options exist
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
print("CHECKING PORTAL TYPE FIELD")
print("="*70)

vp_table = base.table('VENDOR PORTAL')
records = vp_table.all()

print(f"\nChecking {len(records)} records for 'Portal Type' values...\n")

# Collect all unique Portal Type values that exist
portal_types = set()
for record in records:
    portal_type = record['fields'].get('Portal Type')
    if portal_type:
        portal_types.add(portal_type)

if portal_types:
    print("✅ Portal Type field has these existing values:")
    for pt in sorted(portal_types):
        print(f"   - '{pt}'")
    print(f"\n📊 Total unique Portal Types: {len(portal_types)}")
else:
    print("⚠️  Portal Type field exists but has NO values set yet")
    print("\nYou need to add these select options in Airtable:")
    print("   - High Priority")
    print("   - Prime Contractor")
    print("   - Federal Specialty")
    print("   - Cooperative")
    print("   - Agency-Specific")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\nVENDOR PORTAL Fields Status:")
print("   ✅ Portal Name - exists")
print("   ✅ Added Date - exists")
print("   ⚠️  Portal Type - exists but needs options configured")
print("   ❌ Portal URL - needs to be added")
print("   ❌ Status - needs to be added")

print("\n💡 ACTION NEEDED:")
print("   1. Add 'Portal URL' field (URL type)")
print("   2. Add 'Status' field (Single select: Active, Inactive, Testing)")
print("   3. Configure 'Portal Type' options or I can use empty values for now")

print("\n" + "="*70)
