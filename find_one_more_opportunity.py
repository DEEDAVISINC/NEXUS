#!/usr/bin/env python3
"""
Find 1 more viable opportunity to complete the 3 new opportunities
Exclude: Shipping & Storage (already selected), Lab Buret, Equipment Support Guam, Fire Protection
Look for: Product resale or simple services, reasonable timeline, not too remote
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

all_records = table.all()

# Record IDs to exclude (already selected)
exclude_ids = [
    'recTY3QfOammWyJIu',  # Shipping & Storage (WOSB)
    'recTyd4hDlRAmYnPQ',  # Lab Buret
    'recy53yXR6aKBwmFv',  # Equipment Support Guam
    'recXLEZjNgNsyfujK',  # Fire Protection
]

viable = []

for r in all_records:
    # Skip if already selected
    if r['id'] in exclude_ids:
        continue
    
    fields = r['fields']
    name = fields.get('Name', '').lower()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    source_status = fields.get('Source Status', '').lower()
    set_aside = fields.get('Set-Aside Type', '').upper()
    
    # Skip if already working
    if status in ['Pursuing', 'Submitted', 'Won', 'Lost', 'Not Pursuing']:
        continue
    
    # Skip manually added local (user already found these)
    if any(word in name for word in ['rcoc', 'wayne county', 'bloomfield', 'rock island', 'canton', 'oakland county']):
        continue
    
    # Skip renewals and forecasts
    if 'potential renewal' in name or 'forecast' in name or 'contract renewal' in name:
        continue
    
    # Skip sources sought
    if 'sources sought' in source_status or 'forecast' in source_status:
        continue
    
    # Must have deadline
    if not deadline:
        continue
    
    # Parse deadline
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days
        
        # 7-45 day window
        if not (7 <= days_until_due <= 45):
            continue
    except:
        continue
    
    # Look for supplies/equipment (easier to bid)
    is_supplies = any(word in name for word in [
        'supplies', 'equipment', 'materials', 'parts', 'furniture',
        'tools', 'paper', 'medical', 'office', 'laboratory', 'safety',
        'valve', 'pump', 'filter', 'bearing', 'kit', 'assembly'
    ])
    
    # Or simple services
    is_service = any(word in name for word in [
        'cleaning', 'janitorial', 'maintenance', 'transportation', 'delivery'
    ])
    
    # Skip if neither
    if not (is_supplies or is_service):
        continue
    
    # Score it
    score = 0
    if is_supplies:
        score += 15
    if is_service:
        score += 8
    
    # Prefer good timeline
    if 10 <= days_until_due <= 25:
        score += 5
    elif 7 <= days_until_due <= 9 or 26 <= days_until_due <= 35:
        score += 3
    
    # Bonus for set-asides
    if 'WOSB' in set_aside or 'WOMEN' in set_aside or 'EDWOSB' in set_aside:
        score += 20
    elif 'SBA' in set_aside or 'SMALL BUSINESS' in set_aside:
        score += 10
    
    viable.append({
        'record': r,
        'days': days_until_due,
        'score': score,
        'is_supplies': is_supplies,
        'is_service': is_service,
        'set_aside': set_aside
    })

# Sort by score
viable.sort(key=lambda x: (-x['score'], x['days']))

print(f'\n🔍 ADDITIONAL VIABLE OPPORTUNITIES: {len(viable)}\n')
print("="*80)
print("TOP 10 ADDITIONAL OPPORTUNITIES:")
print("="*80 + "\n")

for i, opp in enumerate(viable[:10], 1):
    r = opp['record']
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    rfp_number = fields.get('RFP NUMBER', 'N/A')
    set_aside = opp['set_aside'] if opp['set_aside'] else 'None'
    days = opp['days']
    score = opp['score']
    
    print(f"{i}. {name[:70]}")
    print(f"   Due: {deadline} ({days} days)")
    print(f"   RFP#: {rfp_number}")
    print(f"   Type: {'📦 SUPPLIES' if opp['is_supplies'] else '🏢 SERVICE'}")
    print(f"   Set-Aside: {set_aside}")
    print(f"   Score: {score}")
    print(f"   ID: {r['id']}")
    print()

print("\n" + "="*80)
print("🎯 RECOMMENDED #3 OPPORTUNITY:")
print("="*80 + "\n")

if viable:
    top = viable[0]
    r = top['record']
    fields = r['fields']
    
    print(f"✅ {fields.get('Name', 'Untitled')}")
    print(f"   Due: {fields.get('Deadline')} ({top['days']} days)")
    print(f"   RFP#: {fields.get('RFP NUMBER', 'N/A')}")
    print(f"   Set-Aside: {top['set_aside'] if top['set_aside'] else 'None'}")
    print(f"   Type: {'Product resale' if top['is_supplies'] else 'Service contract'}")
    print(f"   Score: {top['score']}")
    print(f"   Record ID: {r['id']}")
    print()
else:
    print("No additional viable opportunities found with current criteria")
