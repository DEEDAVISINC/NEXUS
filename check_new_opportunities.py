#!/usr/bin/env python3
"""
Check NEXUS for new opportunities
"""

from pyairtable import Api
import os

# Use credentials directly
AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Get all recent records (no sort to avoid field name errors)
records = table.all(max_records=50)

print(f'\n🎯 MOST RECENT OPPORTUNITIES IN NEXUS ({len(records)} found):\n')

# Show the last 20 (most recent)
for i, r in enumerate(records[-20:], 1):
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    agency = fields.get('Agency', 'Unknown')
    due = fields.get('Deadline', fields.get('Due Date', 'Unknown'))
    status = fields.get('Status', 'Unknown')
    added = fields.get('Date Added', 'Unknown')
    source = fields.get('Source', 'Unknown')
    
    print(f'{i}. {name}')
    print(f'   Agency: {agency}')
    print(f'   Due: {due}')
    print(f'   Status: {status}')
    print(f'   Source: {source}')
    print(f'   Added: {added}')
    print()

print("\n" + "="*60)
print("Looking for opportunities added in last 3 days...")
print("="*60 + "\n")

from datetime import datetime, timedelta
three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

recent = [r for r in records if r['fields'].get('Date Added', '') >= three_days_ago]

print(f"\n📅 OPPORTUNITIES ADDED SINCE {three_days_ago}: {len(recent)}\n")

for i, r in enumerate(recent, 1):
    fields = r['fields']
    print(f'{i}. {fields.get("Name", "Untitled")}')
    print(f'   Status: {fields.get("Status", "Unknown")}')
    print(f'   Added: {fields.get("Date Added", "Unknown")}')
    print()
