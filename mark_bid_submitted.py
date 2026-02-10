#!/usr/bin/env python3
"""
QUICK BID SUBMISSION TRACKER
Use this when you submit ANY bid to immediately update NEXUS

Usage: python3 mark_bid_submitted.py "RFP_NUMBER" "AMOUNT" "CONFIRMATION"

Example: python3 mark_bid_submitted.py "7799" "$6,128" "Conf #0000377183"
"""

import sys
import os
from pyairtable import Api
from datetime import datetime

if len(sys.argv) < 3:
    print("❌ ERROR: Missing arguments!")
    print("\nUsage:")
    print('  python3 mark_bid_submitted.py "RFP_NUMBER" "AMOUNT" ["CONFIRMATION"]')
    print("\nExample:")
    print('  python3 mark_bid_submitted.py "7799" "$6,128" "Conf #0000377183"')
    sys.exit(1)

rfp_number = sys.argv[1]
amount = sys.argv[2]
confirmation = sys.argv[3] if len(sys.argv) > 3 else ""

# Initialize Airtable
AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print(f"🔍 Searching for RFP: {rfp_number}...")

# Find the opportunity
all_opportunities = opportunities_table.all()
found = None

for opp in all_opportunities:
    fields = opp['fields']
    name = fields.get('Name', '')
    rfp = fields.get('RFP NUMBER', '')
    
    if rfp_number.upper() in name.upper() or rfp_number.upper() in rfp.upper():
        found = opp
        break

if not found:
    print(f"❌ ERROR: Could not find opportunity with RFP# {rfp_number}")
    print("\nSearching for similar opportunities...")
    
    similar = []
    for opp in all_opportunities:
        fields = opp['fields']
        name = fields.get('Name', '')
        rfp = fields.get('RFP NUMBER', '')
        if rfp_number[:4] in name or rfp_number[:4] in rfp:
            similar.append(f"  - {name} (RFP#: {rfp})")
    
    if similar:
        print("\nDid you mean one of these?")
        for s in similar[:5]:
            print(s)
    
    sys.exit(1)

# Update the opportunity
fields = found['fields']
name = fields.get('Name', '')

try:
    update_data = {
        'Source Status': f'Submitted - Awaiting Award',
    }
    
    # Build notes
    notes_parts = [f"Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    if amount:
        notes_parts.append(f"Amount: {amount}")
    if confirmation:
        notes_parts.append(f"Confirmation: {confirmation}")
    
    existing_notes = fields.get('Notes', '')
    if existing_notes and 'Submitted' not in existing_notes:
        notes_parts.append(f"Previous: {existing_notes}")
    
    update_data['Notes'] = " | ".join(notes_parts)
    
    opportunities_table.update(found['id'], update_data)
    
    print(f"\n✅ SUCCESS! Updated in NEXUS:")
    print(f"   Opportunity: {name}")
    print(f"   RFP#: {fields.get('RFP NUMBER', 'N/A')}")
    print(f"   Status: → Submitted - Awaiting Award")
    print(f"   Amount: {amount}")
    if confirmation:
        print(f"   Confirmation: {confirmation}")
    print(f"\n📋 This bid is now tracked as SUBMITTED in NEXUS!")
    
except Exception as e:
    print(f"❌ ERROR updating Airtable: {e}")
    sys.exit(1)
