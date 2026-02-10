#!/usr/bin/env python3
from pyairtable import Api
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api = Api(os.getenv('AIRTABLE_API_KEY'))
opps = api.table(os.getenv('AIRTABLE_BASE_ID'), 'GPSS OPPORTUNITIES')

all_records = opps.all()
today = datetime.now()

# Check recent opportunities with deadlines in next 30 days
recent = []
for r in all_records:
    fields = r.get('fields', {})
    deadline_str = fields.get('Deadline')
    if not deadline_str:
        continue
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - today).days
        if -3 <= days_left <= 30:  # Within 30 days
            name = fields.get('Name', 'Unknown')[:60]
            value = fields.get('VALUE', 0) or 0
            recent.append({
                'name': name,
                'deadline': deadline_str,
                'days': days_left,
                'value': value,
                'status': fields.get('STATUS', '')
            })
    except:
        pass

# Sort by deadline
recent.sort(key=lambda x: x['days'])

print(f'Found {len(recent)} opportunities with deadlines in next 30 days:')
print()
for opp in recent[:15]:
    val_str = f"${opp['value']:,.0f}" if opp['value'] > 0 else "$0"
    print(f"{opp['days']:3d} days | {val_str:>12s} | {opp['name']}")
