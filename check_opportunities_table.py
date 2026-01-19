"""
Check what opportunities are in the GPSS OPPORTUNITIES table
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
print("GPSS OPPORTUNITIES - ALL RECORDS")
print("="*70)

opps_table = base.table('GPSS OPPORTUNITIES')
all_records = opps_table.all()

print(f"\n✅ Total records: {len(all_records)}")

if all_records:
    print("\nAll opportunities:")
    print("-"*70)
    
    for i, record in enumerate(all_records, 1):
        name = record['fields'].get('Name', 'Unknown')
        rfp_number = record['fields'].get('RFP NUMBER', 'N/A')
        source = record['fields'].get('Source', 'N/A')
        status = record['fields'].get('Status', 'N/A')
        
        print(f"{i:3}. {name[:50]}")
        print(f"     RFP: {rfp_number} | Source: {source} | Status: {status}")

print("\n" + "="*70)
