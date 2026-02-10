#!/usr/bin/env python3
"""
Get details for top 5 additional opportunities
"""

from pyairtable import Api

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Top 5 record IDs
top_5 = {
    '1. Kitchen Exhaust Duct Cleaning (8 days)': 'recYLILp70kJtXeHS',
    '2. Hose Assembly (22 days)': 'recN7zkyO3gc9S4Ta',
    '3. Valve Globe Stop (22 days)': 'recraoHC4NGu0zhka',
    '4. Seat Valve (25 days)': 'recPbkd3Bi8p3mIls',
    '5. Solenoid Valve (39 days)': 'recRPsw04LJETECHR',
}

print("\n" + "="*80)
print("🔍 TOP 5 ADDITIONAL OPPORTUNITIES - FULL DETAILS")
print("="*80 + "\n")

for name, rec_id in top_5.items():
    try:
        record = table.get(rec_id)
        fields = record['fields']
        
        print(f"{'='*80}")
        print(f"{name}")
        print(f"{'='*80}\n")
        
        full_name = fields.get('Name', 'Untitled')
        print(f"📋 {full_name}\n")
        
        print("📊 KEY INFO:")
        print(f"   RFP: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Due: {fields.get('Deadline', 'Unknown')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Status: {fields.get('Status', 'New')}")
        
        if 'State' in fields:
            print(f"   State: {fields.get('State')}")
        
        if 'NAISC Codes' in fields:
            print(f"   NAICS: {fields.get('NAISC Codes')}")
        
        if 'CONTRACTING OFFICER' in fields:
            co = fields.get('CONTRACTING OFFICER', '')
            if 'Email:' in co:
                email = co.split('Email:')[1].strip().split()[0]
                print(f"   Contact: {email}")
        
        if 'Source URL' in fields:
            print(f"   SAM.gov: {fields.get('Source URL')}")
        
        print(f"   Record ID: {rec_id}\n")
        
    except Exception as e:
        print(f"Error: {e}\n")

print("="*80)
print("✅ TOP 5 OPTIONS RETRIEVED")
print("="*80 + "\n")
