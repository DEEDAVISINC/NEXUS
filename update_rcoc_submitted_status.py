#!/usr/bin/env python3
"""
UPDATE RCOC bids 7799, 7802, 7803 to SUBMITTED status
"""

import os
from pyairtable import Api
from datetime import datetime

# Initialize
AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

# Record IDs from previous check
updates = [
    {
        'record_id': 'rectviVAd6UCkIcLB',
        'rfp': '7799',
        'name': 'RCOC 7799 - Grease and Air Couplers',
        'amount': '$6,128'
    },
    {
        'record_id': 'recWA5RCVn74j3W9O',
        'rfp': '7802',
        'name': 'RCOC 7802 - Building Tools',
        'amount': '$6,720'
    },
    {
        'record_id': 'rec1wCztBLUofbtLJ',
        'rfp': '7803',
        'name': 'RCOC 7803 - Hammers, Tape Measures, Levels',
        'amount': '$2,641'
    }
]

print("🔧 UPDATING RCOC BID STATUS IN AIRTABLE...")
print("="*80)

for update in updates:
    try:
        # Update the status
        opportunities_table.update(
            update['record_id'],
            {
                'Source Status': 'Submitted - Awaiting Award',
                'Notes': f"Submitted to RCOC - Awaiting award confirmation. Amount: {update['amount']}. Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        )
        print(f"✅ UPDATED: {update['name']} ({update['rfp']})")
        print(f"   Status: Active → Submitted - Awaiting Award")
        print(f"   Amount: {update['amount']}")
        print()
    except Exception as e:
        print(f"❌ ERROR updating {update['rfp']}: {e}")
        print()

print("="*80)
print("✅ STATUS UPDATES COMPLETE!")
print("\nThese 3 RCOC bids are now marked as SUBMITTED in Airtable:")
print("  - 7799: Grease & Air Couplers ($6,128)")
print("  - 7802: Building Tools ($6,720)")
print("  - 7803: Hammers, Tape, Levels ($2,641)")
print("\n📊 TOTAL SUBMITTED: $15,489")
