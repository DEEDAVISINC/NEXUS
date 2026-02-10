#!/usr/bin/env python3
"""
Get full details for top 3 NEXUS-discovered opportunities
"""

from pyairtable import Api

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Top 3 record IDs
record_ids = [
    'recy53yXR6aKBwmFv',  # Equipment Support Services Naval Base Guam
    'recTyd4hDlRAmYnPQ',  # BURET,LABORATORY
    'recXLEZjNgNsyfujK',  # Fire Prevention & Protection Systems
]

print("\n" + "="*80)
print("🎯 TOP 3 NEXUS-DISCOVERED OPPORTUNITIES - FULL DETAILS")
print("="*80 + "\n")

for i, rec_id in enumerate(record_ids, 1):
    try:
        record = table.get(rec_id)
        fields = record['fields']
        
        print(f"{'='*80}")
        print(f"OPPORTUNITY #{i}")
        print(f"{'='*80}\n")
        
        name = fields.get('Name', 'Untitled')
        print(f"📋 {name}\n")
        
        print("📊 KEY DETAILS:")
        print(f"   RFP Number: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   Source: {fields.get('SOURCE', 'Unknown')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        
        if 'AGENCY NAME' in fields:
            print(f"   Agency: {fields.get('AGENCY NAME')}")
        
        if 'State' in fields:
            print(f"   State: {fields.get('State')}")
        
        if 'NAISC Codes' in fields:
            print(f"   NAICS: {fields.get('NAISC Codes')}")
        
        if 'CONTRACTING OFFICER' in fields:
            co = fields.get('CONTRACTING OFFICER', '')
            if 'Email:' in co:
                email = co.split('Email:')[1].strip() if 'Email:' in co else 'N/A'
                print(f"   Contact: {email}")
        
        if 'Source URL' in fields:
            print(f"   SAM.gov: {fields.get('Source URL')}")
        
        if 'Notes' in fields:
            notes_url = fields.get('Notes', '')
            if 'sam.gov' in notes_url:
                print(f"   Details: {notes_url}")
        
        print(f"\n🔗 Record ID: {rec_id}\n")
        
    except Exception as e:
        print(f"Error getting record {rec_id}: {e}\n")

print("="*80)
print("✅ Details retrieved for top 3 NEXUS opportunities")
print("="*80 + "\n")
