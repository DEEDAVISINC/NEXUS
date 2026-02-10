#!/usr/bin/env python3
"""
Get full details for the 3 Michigan opportunities
"""

from pyairtable import Api

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# The 3 record IDs from search
record_ids = [
    'recoLTYNi6B6an5G2',  # Cattle Handling Equipment
    'recvdpuZOqIzFlKdI',  # RCOC 7842 Safety Supplies
    'reclcdojz7ETnV0op',  # Wayne County Barricades
]

print("\n" + "="*80)
print("🔍 FULL DETAILS FOR 3 NEW MICHIGAN OPPORTUNITIES")
print("="*80 + "\n")

for i, rec_id in enumerate(record_ids, 1):
    try:
        record = table.get(rec_id)
        fields = record['fields']
        
        print(f"{'='*80}")
        print(f"OPPORTUNITY #{i}")
        print(f"{'='*80}\n")
        
        print(f"📋 NAME: {fields.get('Name', 'Untitled')}\n")
        
        print("📊 KEY DETAILS:")
        print(f"   RFP Number: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   Source: {fields.get('Source Status', 'Unknown')}")
        
        if 'Agency' in fields:
            print(f"   Agency: {fields.get('Agency')}")
        
        if 'Estimated Value' in fields:
            print(f"   Estimated Value: {fields.get('Estimated Value')}")
        
        if 'HIGH VALUE FLAG' in fields:
            print(f"   High Value: {fields.get('HIGH VALUE FLAG')}")
        
        # Get all field names
        print(f"\n📝 ALL AVAILABLE FIELDS:")
        for key in sorted(fields.keys()):
            if key not in ['Name', 'RFP NUMBER', 'Deadline', 'Status', 'Source Status', 'Agency', 'Estimated Value', 'HIGH VALUE FLAG']:
                value = fields[key]
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        
        print(f"\n🔗 Record ID: {rec_id}")
        print()
        
    except Exception as e:
        print(f"Error getting record {rec_id}: {e}\n")

print("="*80)
print("✅ Review complete - 3 Michigan opportunities detailed above")
print("="*80 + "\n")
