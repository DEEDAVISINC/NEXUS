#!/usr/bin/env python3
"""
Find EDWOSB/WOSB SET-ASIDE opportunities specifically
These are where Dee Davis Inc has MAJOR competitive advantage!
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

all_records = table.all()

print(f'\n📊 Total opportunities in NEXUS: {len(all_records)}\n')

# Filter for EDWOSB/WOSB SET-ASIDES specifically
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
    
    # Skip manually added local bids
    if 'rcoc' in name or 'wayne county' in name:
        continue
    
    # Must have deadline
    if not deadline:
        continue
    
    # Parse deadline
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days
        
        # Looking for 3-60 day window
        if not (3 <= days_until_due <= 60):
            continue
    except:
        continue
    
    # MUST be WOSB or EDWOSB set-aside
    is_wosb = any(keyword in set_aside for keyword in [
        'WOSB', 'EDWOSB', 'WOMEN', 'WOMAN-OWNED', 'WOMAN OWNED'
    ])
    
    # Also check in name and source status
    if not is_wosb:
        is_wosb = any(keyword in name for keyword in ['wosb', 'edwosb', 'women-owned']) or \
                  any(keyword in source_status for keyword in ['wosb', 'edwosb', 'women-owned'])
    
    if is_wosb:
        # Skip sources sought and forecasts (want actual RFPs)
        if 'sources sought' in source_status or 'forecast' in source_status:
            continue
        
        # Prefer product opportunities
        is_supplies = any(word in name for word in [
            'supplies', 'equipment', 'materials', 'parts', 'furniture',
            'tools', 'paper', 'medical', 'office', 'laboratory', 'safety'
        ])
        
        is_service = any(word in name for word in [
            'cleaning', 'janitorial', 'maintenance', 'transportation', 'service'
        ])
        
        score = 20  # Base score for WOSB
        if is_supplies:
            score += 10
        if is_service:
            score += 5
        if 5 <= days_until_due <= 20:
            score += 5
        
        wosb_opportunities.append({
            'record': r,
            'days': days_until_due,
            'score': score,
            'is_supplies': is_supplies,
            'is_service': is_service
        })

# Sort by score
wosb_opportunities.sort(key=lambda x: (-x['score'], x['days']))

print(f'🌟 EDWOSB/WOSB SET-ASIDE OPPORTUNITIES: {len(wosb_opportunities)}\n')

if wosb_opportunities:
    print("="*80)
    print("🔥 WOMAN-OWNED BUSINESS SET-ASIDES (YOUR COMPETITIVE ADVANTAGE!):")
    print("="*80 + "\n")
    
    for i, opp in enumerate(wosb_opportunities[:15], 1):
        r = opp['record']
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        rfp_number = fields.get('RFP NUMBER', 'N/A')
        set_aside = fields.get('Set-Aside Type', 'Unknown')
        days = opp['days']
        score = opp['score']
        
        print(f"{i}. {name[:75]}")
        print(f"   Due: {deadline} ({days} days)")
        print(f"   RFP#: {rfp_number}")
        print(f"   Set-Aside: {set_aside}")
        print(f"   Type: {'📦 SUPPLIES' if opp['is_supplies'] else '🏢 SERVICE' if opp['is_service'] else '❓ OTHER'}")
        print(f"   Score: {score}")
        print(f"   Record ID: {r['id']}")
        print()
    
    print("\n" + "="*80)
    print("🎯 TOP 3 WOSB SET-ASIDE OPPORTUNITIES:")
    print("="*80 + "\n")
    
    for i, opp in enumerate(wosb_opportunities[:3], 1):
        r = opp['record']
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        days = opp['days']
        set_aside = fields.get('Set-Aside Type', 'Unknown')
        
        print(f"✅ #{i}: {name}")
        print(f"     Due: {deadline} ({days} days)")
        print(f"     Set-Aside: {set_aside}")
        print(f"     Why: WOSB SET-ASIDE = Limited competition to woman-owned businesses!")
        print(f"     Type: {'Products' if opp['is_supplies'] else 'Service' if opp['is_service'] else 'Other'}")
        print(f"     Record ID: {r['id']}")
        print()
else:
    print("❌ NO EDWOSB/WOSB SET-ASIDE OPPORTUNITIES FOUND")
    print("\nThis means:")
    print("  - NEXUS hasn't pulled any woman-owned set-asides recently")
    print("  - May need to search SAM.gov directly for WOSB opportunities")
    print("  - These are the BEST opportunities for your EDWOSB certification!")
