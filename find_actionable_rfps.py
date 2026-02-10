#!/usr/bin/env python3
"""
Find NEW actionable RFPs in NEXUS (not forecasts/renewals)
"""

from pyairtable import Api
from datetime import datetime, timedelta

# Use credentials directly
AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Get all records
all_records = table.all()

print(f'\n📊 TOTAL OPPORTUNITIES IN NEXUS: {len(all_records)}\n')

# Check what fields actually exist
if all_records:
    print("Available fields in first record:")
    print(list(all_records[0]['fields'].keys()))
    print("\n" + "="*60 + "\n")

# Filter for actionable RFPs (has deadline, not "Potential Renewal", not "Forecast")
actionable = []
for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '')
    deadline = fields.get('Deadline', fields.get('Due Date', ''))
    
    # Skip forecasts and renewals
    if 'Potential Renewal' in name or 'Forecast' in name or '[Contract Renewal' in name:
        continue
    
    # Must have a deadline
    if not deadline:
        continue
    
    # Parse deadline
    try:
        if isinstance(deadline, str):
            due_date = datetime.strptime(deadline, '%Y-%m-%d')
        else:
            continue
            
        # Only include if deadline is in the next 60 days
        days_until_due = (due_date - datetime.now()).days
        if 0 <= days_until_due <= 60:
            actionable.append((r, days_until_due))
    except:
        pass

# Sort by deadline (soonest first)
actionable.sort(key=lambda x: x[1])

print(f'🎯 ACTIONABLE RFPS WITH DEADLINES IN NEXT 60 DAYS: {len(actionable)}\n')

for i, (r, days) in enumerate(actionable[:20], 1):
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    agency = fields.get('Agency', 'Unknown')
    deadline = fields.get('Deadline', fields.get('Due Date', 'Unknown'))
    status = fields.get('Status', 'New')
    source = fields.get('Source', 'Unknown')
    value = fields.get('Estimated Value', 'Unknown')
    
    print(f'{i}. {name}')
    print(f'   Agency: {agency}')
    print(f'   Due: {deadline} ({days} days)')
    print(f'   Status: {status}')
    print(f'   Value: {value}')
    print(f'   Source: {source}')
    print()

print("\n" + "="*60)
print("🆕 Looking for NEW opportunities (status = 'New' or blank)...")
print("="*60 + "\n")

new_opportunities = [x for x in actionable if x[0]['fields'].get('Status', 'New') in ['New', '', None]]

print(f'Found {len(new_opportunities)} NEW opportunities:\n')

for i, (r, days) in enumerate(new_opportunities[:10], 1):
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', fields.get('Due Date', 'Unknown'))
    
    print(f'{i}. {name}')
    print(f'   Due: {deadline} ({days} days)')
    print()
