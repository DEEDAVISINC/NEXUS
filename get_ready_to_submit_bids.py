#!/usr/bin/env python3
"""
Get bids that are READY TO SUBMIT
"""

from pyairtable import Api
from datetime import datetime

AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("🎯 BIDS READY FOR SUBMISSION")
print("="*80)

all_opportunities = opportunities_table.all()

ready_to_submit = []

for opp in all_opportunities:
    fields = opp['fields']
    status = fields.get('Source Status', '').lower()
    name = fields.get('Name', '')
    deadline = fields.get('Deadline')
    
    # Look for "ready" status indicators
    if any(word in status for word in ['ready', 'preparing', 'awaiting quotes', 'quotes received']):
        if deadline:
            try:
                deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                now = datetime.now(deadline_date.tzinfo)
                days_remaining = (deadline_date - now).days
                
                if days_remaining >= 0:  # Not past due
                    ready_to_submit.append({
                        'name': name,
                        'deadline': deadline_date,
                        'days': days_remaining,
                        'status': fields.get('Source Status', ''),
                        'rfp': fields.get('RFP NUMBER', ''),
                        'notes': fields.get('Notes', ''),
                    })
            except:
                pass

# Sort by deadline
ready_to_submit.sort(key=lambda x: x['deadline'])

print(f"\nFound {len(ready_to_submit)} bids ready for submission:\n")

for idx, bid in enumerate(ready_to_submit, 1):
    formatted_date = bid['deadline'].strftime('%A, %B %d, %Y')
    
    if bid['days'] == 0:
        urgency = "🚨 DUE TODAY!"
    elif bid['days'] == 1:
        urgency = "🔥 DUE TOMORROW!"
    elif bid['days'] <= 3:
        urgency = f"⚡ {bid['days']} DAYS"
    elif bid['days'] <= 7:
        urgency = f"📅 {bid['days']} days"
    else:
        urgency = f"📅 {bid['days']} days"
    
    print(f"{idx}. {bid['name']}")
    print(f"   Deadline: {formatted_date} {urgency}")
    print(f"   Status: {bid['status']}")
    print(f"   RFP#: {bid['rfp']}")
    if bid['notes']:
        print(f"   Notes: {bid['notes'][:150]}...")
    print()

print("="*80)
