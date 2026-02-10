#!/usr/bin/env python3
"""
Check EXACT status of ALL RCOC bids in Airtable RIGHT NOW
"""

import os
from pyairtable import Api

# Initialize
AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("🔍 Checking ALL RCOC bids in Airtable...")

all_opportunities = opportunities_table.all()

rcoc_bids = []

for opp in all_opportunities:
    fields = opp['fields']
    name = fields.get('Name', '')
    rfp_number = fields.get('RFP NUMBER', '')
    
    # Check if this is an RCOC bid
    if 'RCOC' in name.upper() or 'RCOC' in rfp_number.upper() or any(x in rfp_number for x in ['7731', '7732', '7734', '7777', '7797', '7798', '7799', '7802', '7803', '7814', '7842', '7790']):
        rcoc_bids.append({
            'id': opp['id'],
            'name': name,
            'rfp_number': rfp_number,
            'status': fields.get('Source Status', 'NO STATUS'),
            'deadline': fields.get('Deadline', 'NO DEADLINE'),
            'notes': fields.get('Notes', ''),
        })

# Sort by RFP number
rcoc_bids.sort(key=lambda x: x['rfp_number'])

print(f"\n✅ Found {len(rcoc_bids)} RCOC bids in Airtable\n")
print("="*80)
print("CURRENT STATUS IN AIRTABLE:")
print("="*80)

for bid in rcoc_bids:
    print(f"\n📋 {bid['name']}")
    print(f"   RFP#: {bid['rfp_number']}")
    print(f"   Status: {bid['status']}")
    print(f"   Deadline: {bid['deadline']}")
    if bid['notes']:
        print(f"   Notes: {bid['notes'][:200]}")
    print(f"   Record ID: {bid['id']}")

print("\n" + "="*80)
print("WHICH BIDS NEED STATUS UPDATES?")
print("="*80)
print("\nUser says 7803, 7802, and 7799 were SUBMITTED.")
print("Let me check their current status...")

for bid in rcoc_bids:
    if any(x in bid['rfp_number'] for x in ['7803', '7802', '7799']):
        if 'submitted' not in bid['status'].lower():
            print(f"\n⚠️ {bid['rfp_number']} - Current status: '{bid['status']}'")
            print(f"   NEEDS UPDATE TO: 'Submitted - Awaiting Award'")
            print(f"   Record ID: {bid['id']}")
