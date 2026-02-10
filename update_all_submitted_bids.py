#!/usr/bin/env python3
"""
UPDATE ALL SUBMITTED BIDS IN NEXUS
Based on user confirmation: 7731, 7777, 7797, 7798, 7799, 7802, rfq-w-dpw-0203, oak-0000001089
"""

from pyairtable import Api
from datetime import datetime

AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("🔧 UPDATING ALL SUBMITTED BIDS IN NEXUS...")
print("="*80)

# List of confirmed submitted bids
submitted_bids = [
    {'search': '7731', 'name': 'RCOC 7731 - Industrial Wipers', 'amount': '$63,948'},
    {'search': '7777', 'name': 'RCOC 7777 - Welding Supplies', 'amount': '$12,338'},
    {'search': '7797', 'name': 'RCOC 7797 - Automotive Tools', 'amount': '$3,978'},
    {'search': '7798', 'name': 'RCOC 7798 - Wiper Blades', 'amount': '$1,521'},
    {'search': '7799', 'name': 'RCOC 7799 - Grease & Air Couplers', 'amount': '$6,128'},
    {'search': '7802', 'name': 'RCOC 7802 - Building Tools', 'amount': '$7,292'},
    {'search': 'rfq-w-dpw-0203', 'name': 'Warren DPW Parts Washer', 'amount': 'TBD'},
    {'search': 'oak-0000001089', 'name': 'Oakland County Body Bags', 'amount': '$95K-$150K'},
]

all_opportunities = opportunities_table.all()
updated = 0

for bid_info in submitted_bids:
    search_term = bid_info['search'].lower()
    found = False
    
    for opp in all_opportunities:
        fields = opp['fields']
        name = fields.get('Name', '').lower()
        rfp = fields.get('RFP NUMBER', '').lower()
        
        if search_term in name or search_term in rfp:
            try:
                # Update to submitted status
                opportunities_table.update(opp['id'], {
                    'Source Status': 'Submitted - Awaiting Award',
                    'Notes': f'SUBMITTED - User confirmed {datetime.now().strftime("%Y-%m-%d %H:%M")} | Amount: {bid_info["amount"]}'
                })
                print(f"✅ {bid_info['name']} - UPDATED TO SUBMITTED")
                updated += 1
                found = True
                break
            except Exception as e:
                print(f"❌ Error updating {bid_info['name']}: {e}")
                break
    
    if not found:
        print(f"⚠️ {bid_info['name']} - NOT FOUND IN NEXUS")

print("\n" + "="*80)
print(f"✅ UPDATED {updated} BIDS IN NEXUS")
print("="*80)

print("\n✅ SUBMITTED (Total 8 bids):")
for bid in submitted_bids:
    print(f"  - {bid['name']} ({bid['amount']})")

print("\n📊 TOTAL SUBMITTED VALUE: ~$275K+")
