#!/usr/bin/env python3
"""
Pull full details for selected opportunities:
1. Shipping & Storage (WOSB)
2. Lab Buret (SBA)
3. Equipment Support Services (SBA)
4. Fire Protection Systems (SBA)
"""

from pyairtable import Api
import requests

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Record IDs for selected opportunities
selected = {
    'Shipping & Storage (WOSB)': 'recTY3QfOammWyJIu',
    'Lab Buret (SBA)': 'recTyd4hDlRAmYnPQ',
    'Equipment Support Guam (SBA)': 'recy53yXR6aKBwmFv',
    'Fire Protection (SBA)': 'recXLEZjNgNsyfujK'
}

print("\n" + "="*80)
print("🎯 SELECTED OPPORTUNITIES - FULL DETAILS")
print("="*80 + "\n")

for name, rec_id in selected.items():
    try:
        record = table.get(rec_id)
        fields = record['fields']
        
        print(f"{'='*80}")
        print(f"{name}")
        print(f"{'='*80}\n")
        
        full_name = fields.get('Name', 'Untitled')
        print(f"📋 FULL TITLE: {full_name}\n")
        
        print("📊 BASIC INFO:")
        print(f"   RFP Number: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Status: {fields.get('Status', 'New')}")
        
        if 'State' in fields:
            print(f"   State: {fields.get('State')}")
        
        if 'NAISC Codes' in fields:
            print(f"   NAICS: {fields.get('NAISC Codes')}")
        
        print(f"\n📧 CONTACT:")
        if 'CONTRACTING OFFICER' in fields:
            co = fields.get('CONTRACTING OFFICER', '')
            print(f"   {co}")
        
        print(f"\n🔗 LINKS:")
        if 'Source URL' in fields:
            sam_url = fields.get('Source URL', '')
            print(f"   SAM.gov: {sam_url}")
        
        if 'Notes' in fields:
            notes = fields.get('Notes', '')
            if 'sam.gov' in notes.lower():
                print(f"   Details API: {notes}")
        
        # Additional fields
        print(f"\n📝 ADDITIONAL INFO:")
        if 'AGENCY NAME' in fields:
            print(f"   Agency: {fields.get('AGENCY NAME')}")
        if 'Opportunity Category' in fields:
            print(f"   Category: {fields.get('Opportunity Category')}")
        if 'Priority' in fields:
            print(f"   Priority: {fields.get('Priority')}")
        if 'Win Probability' in fields:
            print(f"   Win Probability: {fields.get('Win Probability')}")
        
        print(f"\n🆔 Record ID: {rec_id}")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error getting {name}: {e}\n\n")

print("="*80)
print("✅ SELECTED OPPORTUNITIES RETRIEVED")
print("="*80 + "\n")

print("🎯 NEXT STEPS:\n")
print("1. Visit SAM.gov links above to review full solicitations")
print("2. Check quantities, specifications, delivery locations")
print("3. Assess if viable for bidding (cost, timeline, capabilities)")
print("4. Make go/no-go decision by end of day")
print()
