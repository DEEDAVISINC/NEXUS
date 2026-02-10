#!/usr/bin/env python3
"""
Find REAL NEW opportunities that NEXUS discovered automatically
(NOT manually added RCOC or local bids the user already found)
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

all_records = table.all()

print(f'\n📊 Total opportunities in NEXUS: {len(all_records)}\n')

# Filter for NEW opportunities that NEXUS auto-discovered
# Exclude: RCOC, Wayne County, anything user manually added
auto_discovered = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    source_status = fields.get('Source Status', '').lower()
    source = fields.get('SOURCE', '').upper()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    
    # Skip if already working
    if status in ['Pursuing', 'Submitted', 'Won', 'Lost', 'Not Pursuing']:
        continue
    
    # Skip manually added local bids (these are ones user found)
    if 'rcoc' in name or 'wayne county' in name or 'bloomfield' in name:
        continue
    if 'rock island' in name or 'canton' in name or 'oakland county' in name:
        continue
    
    # Skip if no deadline
    if not deadline:
        continue
    
    # Skip renewals and forecasts
    if 'potential renewal' in name or 'contract renewal' in name:
        continue
    
    # Parse deadline
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days
        
        # Looking for 5-45 day window (actionable)
        if not (5 <= days_until_due <= 45):
            continue
    except:
        continue
    
    # Must be from SAM.gov (auto-discovered federal opportunities)
    if 'sam.gov' not in source_status and source != 'FEDERAL':
        continue
    
    # Skip sources sought and forecasts (want actual solicitations)
    if 'sources sought' in source_status or 'forecast' in source_status:
        continue
    
    # Look for product/supply opportunities (our sweet spot)
    is_supplies = any(word in name for word in [
        'supplies', 'equipment', 'materials', 'parts', 'furniture',
        'tools', 'paper', 'medical', 'office', 'laboratory', 'safety'
    ])
    
    # Or service opportunities we can subcontract
    is_service = any(word in name for word in [
        'cleaning', 'janitorial', 'maintenance', 'repair', 'transportation'
    ])
    
    if is_supplies or is_service:
        score = 0
        
        # Prefer supplies (easier to bid)
        if is_supplies:
            score += 10
        if is_service:
            score += 5
        
        # Prefer closer deadlines (more urgent)
        if 5 <= days_until_due <= 15:
            score += 5
        elif 16 <= days_until_due <= 30:
            score += 3
        
        # Check for set-aside opportunities (EDWOSB advantage)
        set_aside = fields.get('Set-Aside Type', '').upper()
        if 'WOSB' in set_aside or 'EDWOSB' in set_aside or 'WOMEN' in set_aside:
            score += 15  # BIG bonus
        elif 'SBA' in set_aside or 'SMALL BUSINESS' in set_aside:
            score += 8
        
        auto_discovered.append({
            'record': r,
            'days': days_until_due,
            'score': score,
            'is_supplies': is_supplies,
            'is_service': is_service,
            'set_aside': set_aside
        })

# Sort by score (highest first)
auto_discovered.sort(key=lambda x: (-x['score'], x['days']))

print(f'🎯 AUTO-DISCOVERED OPPORTUNITIES (Federal/SAM.gov): {len(auto_discovered)}\n')
print("="*80)
print("TOP 15 OPPORTUNITIES NEXUS FOUND:")
print("="*80 + "\n")

for i, opp in enumerate(auto_discovered[:15], 1):
    r = opp['record']
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    rfp_number = fields.get('RFP NUMBER', 'N/A')
    set_aside = opp['set_aside']
    days = opp['days']
    score = opp['score']
    
    print(f"{i}. {name[:80]}")
    print(f"   Due: {deadline} ({days} days)")
    print(f"   RFP#: {rfp_number}")
    print(f"   Type: {'📦 SUPPLIES' if opp['is_supplies'] else '🏢 SERVICE'}")
    print(f"   Set-Aside: {set_aside if set_aside else 'None'}")
    print(f"   Score: {score}")
    print(f"   Record ID: {r['id']}")
    print()

print("\n" + "="*80)
print("🔥 TOP 3 NEXUS-DISCOVERED OPPORTUNITIES:")
print("="*80 + "\n")

for i, opp in enumerate(auto_discovered[:3], 1):
    r = opp['record']
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    days = opp['days']
    
    print(f"✅ #{i}: {name}")
    print(f"     Due: {deadline} ({days} days)")
    print(f"     Set-Aside: {opp['set_aside'] if opp['set_aside'] else 'None'}")
    print(f"     Why: ", end='')
    
    reasons = []
    if opp['is_supplies']:
        reasons.append("SUPPLIES/PRODUCTS")
    if opp['is_service']:
        reasons.append("SERVICE CONTRACT")
    if 'WOSB' in opp['set_aside'] or 'WOMEN' in opp['set_aside']:
        reasons.append("WOSB SET-ASIDE (PERFECT FOR YOU!)")
    elif 'SBA' in opp['set_aside']:
        reasons.append("SMALL BUSINESS SET-ASIDE")
    if 5 <= days <= 15:
        reasons.append("URGENT")
    
    print(", ".join(reasons))
    print()

if len(auto_discovered) < 3:
    print("\n⚠️ NEXUS only found", len(auto_discovered), "viable opportunities")
    print("\n💡 NEXUS needs more RSS feeds for:")
    print("   - Local Michigan procurement portals")
    print("   - State of Michigan procurement (MiDEAL)")
    print("   - Midwest regional opportunities")
