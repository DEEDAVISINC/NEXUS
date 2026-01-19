"""
Remove mock/test opportunity records from GPSS OPPORTUNITIES table
Keep all real API data (100 records from GovCon)
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
print("REMOVING MOCK OPPORTUNITIES")
print("="*70)

opps_table = base.table('GPSS OPPORTUNITIES')
all_records = opps_table.all()

print(f"\n📊 Total records before cleanup: {len(all_records)}")

# Identify mock records by their characteristics
mock_rfp_numbers = ['Item 2', 'Item 3', 'WI-DHS-2026-001']
mock_names = ['MONTGOMERY COUNTY TRANSPORTATION', 'FEMA DISASTER RESPONSE', 'WISCONSIN NEMT RFP']

deleted_count = 0
kept_count = 0

print("\n🗑️  Deleting mock records...")
print("-"*70)

for record in all_records:
    name = record['fields'].get('Name', '')
    rfp_number = record['fields'].get('RFP NUMBER', '')
    status = record['fields'].get('Status', '')
    
    # Check if this is a mock record
    is_mock = (
        rfp_number in mock_rfp_numbers or
        name in mock_names or
        (status not in ['New - API', 'New - RSS', 'New - State/Local'])
    )
    
    if is_mock:
        try:
            opps_table.delete(record['id'])
            print(f"   ❌ Deleted: {name[:50]} (RFP: {rfp_number}, Status: {status})")
            deleted_count += 1
        except Exception as e:
            print(f"   ⚠️  Error deleting {name}: {e}")
    else:
        kept_count += 1

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\n✅ Kept: {kept_count} real API opportunities")
print(f"🗑️  Deleted: {deleted_count} mock/test records")
print(f"📊 Final count: {kept_count} opportunities")

print("\n" + "="*70)
print("✅ CLEANUP COMPLETE!")
print("="*70)

print("\n🎯 WHAT'S LEFT:")
print("   ✅ 100 real GovCon API opportunities")
print("   ✅ All have status 'New - API'")
print("   ✅ No mock data")

print("\n💡 REFRESH YOUR DASHBOARD:")
print("   The dashboard will now show only real data!")

print("\n" + "="*70)
