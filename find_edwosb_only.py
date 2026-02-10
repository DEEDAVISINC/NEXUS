#!/usr/bin/env python3
"""
Find EDWOSB (Economically Disadvantaged Woman-Owned) set-asides specifically
These have EVEN LESS competition than regular WOSB!
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

all_records = table.all()

print(f'\n📊 Total opportunities in NEXUS: {len(all_records)}\n')

# Find EDWOSB specifically (not just WOSB)
edwosb_opportunities = []
wosb_opportunities = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    set_aside = fields.get('Set-Aside Type', '').upper()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    source_status = fields.get('Source Status', '').lower()
    
    # Skip if already working
    if status in ['Pursuing', 'Submitted', 'Won', 'Lost', 'Not Pursuing']:
        continue
    
    # Skip manually added local
    if any(word in name for word in ['rcoc', 'wayne county', 'bloomfield', 'rock island']):
        continue
    
    # Skip renewals/forecasts
    if 'potential renewal' in name or 'forecast' in name:
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
        
        # 3-60 day window
        if not (3 <= days_until_due <= 60):
            continue
    except:
        continue
    
    # Check for EDWOSB specifically
    is_edwosb = 'EDWOSB' in set_aside
    is_wosb = 'WOSB' in set_aside and 'EDWOSB' not in set_aside
    
    if not (is_edwosb or is_wosb):
        continue
    
    # Prefer product opportunities
    is_supplies = any(word in name for word in [
        'supplies', 'equipment', 'materials', 'parts', 'furniture',
        'tools', 'paper', 'medical', 'office', 'laboratory', 'safety'
    ])
    
    is_service = any(word in name for word in [
        'cleaning', 'janitorial', 'maintenance', 'transportation', 'service'
    ])
    
    score = 0
    if is_edwosb:
        score += 25  # EDWOSB gets highest priority
    elif is_wosb:
        score += 20
    
    if is_supplies:
        score += 10
    if is_service:
        score += 5
    
    if 5 <= days_until_due <= 20:
        score += 5
    
    opp = {
        'record': r,
        'days': days_until_due,
        'score': score,
        'is_supplies': is_supplies,
        'is_service': is_service,
        'is_edwosb': is_edwosb
    }
    
    if is_edwosb:
        edwosb_opportunities.append(opp)
    else:
        wosb_opportunities.append(opp)

# Sort by score
edwosb_opportunities.sort(key=lambda x: (-x['score'], x['days']))
wosb_opportunities.sort(key=lambda x: (-x['score'], x['days']))

print(f'🌟 EDWOSB SET-ASIDE OPPORTUNITIES: {len(edwosb_opportunities)}')
print(f'🌟 WOSB SET-ASIDE OPPORTUNITIES: {len(wosb_opportunities)}\n')

if edwosb_opportunities:
    print("="*80)
    print("🔥 EDWOSB OPPORTUNITIES (HIGHEST PRIORITY - LEAST COMPETITION!):")
    print("="*80 + "\n")
    
    for i, opp in enumerate(edwosb_opportunities[:10], 1):
        r = opp['record']
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        rfp_number = fields.get('RFP NUMBER', 'N/A')
        days = opp['days']
        
        print(f"{i}. {name[:75]}")
        print(f"   Due: {deadline} ({days} days)")
        print(f"   RFP#: {rfp_number}")
        print(f"   Type: {'📦 SUPPLIES' if opp['is_supplies'] else '🏢 SERVICE' if opp['is_service'] else '❓ OTHER'}")
        print(f"   Score: {opp['score']}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("❌ NO EDWOSB SET-ASIDES FOUND\n")

if wosb_opportunities:
    print("="*80)
    print("🟡 WOSB OPPORTUNITIES (GOOD, BUT NOT AS EXCLUSIVE AS EDWOSB):")
    print("="*80 + "\n")
    
    for i, opp in enumerate(wosb_opportunities[:5], 1):
        r = opp['record']
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        rfp_number = fields.get('RFP NUMBER', 'N/A')
        days = opp['days']
        
        print(f"{i}. {name[:75]}")
        print(f"   Due: {deadline} ({days} days)")
        print(f"   RFP#: {rfp_number}")
        print(f"   Type: {'📦 SUPPLIES' if opp['is_supplies'] else '🏢 SERVICE' if opp['is_service'] else '❓ OTHER'}")
        print(f"   Score: {opp['score']}")
        print(f"   ID: {r['id']}")
        print()

print("\n" + "="*80)
print("💡 KEY DIFFERENCE:")
print("="*80)
print("\n✅ EDWOSB = Economically Disadvantaged Woman-Owned Small Business")
print("   - MOST RESTRICTIVE set-aside")
print("   - LEAST competition")
print("   - Must meet economic disadvantage criteria (you do!)")
print("\n🟡 WOSB = Woman-Owned Small Business")
print("   - Less restrictive than EDWOSB")
print("   - More competition (all woman-owned, not just economically disadvantaged)")
print("   - Still good, but EDWOSB is better!\n")
