#!/usr/bin/env python3
"""
Get full details for EDWOSB/WOSB set-aside opportunities
"""

from pyairtable import Api

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# 3 WOSB/EDWOSB opportunities
record_ids = [
    'recrVYgjPZSAqY1zF',  # Cultural Resources Inspection
    'recDvngedImEPBf0E',  # IDIQ JOC Specialty Trade
    'recTY3QfOammWyJIu',  # Shipping and Storage
]

print("\n" + "="*80)
print("🌟 EDWOSB/WOSB SET-ASIDE OPPORTUNITIES - FULL DETAILS")
print("="*80 + "\n")

for i, rec_id in enumerate(record_ids, 1):
    try:
        record = table.get(rec_id)
        fields = record['fields']
        
        print(f"{'='*80}")
        print(f"WOSB OPPORTUNITY #{i}")
        print(f"{'='*80}\n")
        
        name = fields.get('Name', 'Untitled')
        print(f"📋 {name}\n")
        
        print("📊 KEY DETAILS:")
        print(f"   RFP Number: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   ⭐ Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   Source: {fields.get('SOURCE', 'Unknown')}")
        
        if 'AGENCY NAME' in fields:
            print(f"   Agency: {fields.get('AGENCY NAME')}")
        
        if 'State' in fields:
            print(f"   State: {fields.get('State')}")
        
        if 'NAISC Codes' in fields:
            print(f"   NAICS: {fields.get('NAISC Codes')}")
        
        if 'CONTRACTING OFFICER' in fields:
            co = fields.get('CONTRACTING OFFICER', '')
            if 'Email:' in co:
                email = co.split('Email:')[1].strip().split()[0] if 'Email:' in co else co
                print(f"   Contact: {email}")
            else:
                print(f"   Contact: {co[:50]}")
        
        if 'Source URL' in fields:
            url = fields.get('Source URL', '')
            if url:
                print(f"   SAM.gov: {url}")
        
        if 'Notes' in fields:
            notes = fields.get('Notes', '')
            if 'sam.gov' in notes.lower():
                print(f"   Details: {notes}")
        
        if 'Opportunity Category' in fields:
            print(f"   Category: {fields.get('Opportunity Category')}")
        
        print(f"\n🔗 Record ID: {rec_id}\n")
        
    except Exception as e:
        print(f"Error getting record {rec_id}: {e}\n")

print("="*80)
print("✅ WOSB set-aside opportunities detailed above")
print("="*80 + "\n")
