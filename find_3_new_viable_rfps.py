#!/usr/bin/env python3
"""
Find 3 NEW VIABLE RFPs for Dee Davis Inc business model
- Product resale opportunities
- Service contracts (cleaning, maintenance, transportation)
- Michigan/Regional preferred
- Reasonable deadlines (5-45 days out)
- Status: New or blank
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Get all records
all_records = table.all()

print(f'\n📊 Total opportunities in NEXUS: {len(all_records)}\n')

# Keywords for viable opportunities
PRODUCT_KEYWORDS = ['supplies', 'equipment', 'materials', 'products', 'tools', 'parts', 'vehicles', 'furniture', 'paper']
SERVICE_KEYWORDS = ['cleaning', 'maintenance', 'janitorial', 'transportation', 'logistics', 'delivery', 'hauling', 'pressure washing']
MICHIGAN_KEYWORDS = ['michigan', 'detroit', 'MI', 'oakland', 'wayne', 'macomb', 'lansing']

viable_rfps = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    source_status = fields.get('Source Status', '').lower()
    
    # Skip if already working/pursuing
    if status in ['Pursuing', 'Submitted', 'Won', 'Lost', 'Not Pursuing']:
        continue
    
    # Skip renewals and forecasts
    if 'potential renewal' in name or 'forecast' in name or 'contract renewal' in name:
        continue
    
    # Must have deadline
    if not deadline:
        continue
    
    # Parse deadline
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days
        
        # Only include if 5-45 days out (reasonable time to bid)
        if not (5 <= days_until_due <= 45):
            continue
            
    except:
        continue
    
    # Check if it's a viable opportunity type
    is_product = any(keyword in name for keyword in PRODUCT_KEYWORDS)
    is_service = any(keyword in name for keyword in SERVICE_KEYWORDS)
    is_michigan = any(keyword in source_status or keyword in name for keyword in MICHIGAN_KEYWORDS)
    
    if is_product or is_service:
        score = 0
        if is_michigan:
            score += 10
        if is_product:
            score += 5
        if is_service:
            score += 7  # Services are higher margin
        if 10 <= days_until_due <= 30:
            score += 3  # Good timing window
        
        viable_rfps.append({
            'record': r,
            'days_until_due': days_until_due,
            'score': score,
            'is_michigan': is_michigan,
            'is_product': is_product,
            'is_service': is_service
        })

# Sort by score (highest first), then by deadline (soonest)
viable_rfps.sort(key=lambda x: (-x['score'], x['days_until_due']))

print(f'🎯 VIABLE OPPORTUNITIES FOUND: {len(viable_rfps)}\n')
print("="*80)
print("TOP 10 OPPORTUNITIES FOR DEE DAVIS INC:")
print("="*80 + "\n")

for i, opp in enumerate(viable_rfps[:10], 1):
    r = opp['record']
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    agency = fields.get('Agency', 'Unknown')
    deadline = fields.get('Deadline', 'Unknown')
    source_status = fields.get('Source Status', '')
    rfp_number = fields.get('RFP NUMBER', '')
    days = opp['days_until_due']
    score = opp['score']
    
    print(f"{i}. {name}")
    print(f"   Agency: {agency}")
    print(f"   Due: {deadline} ({days} days)")
    print(f"   RFP#: {rfp_number}")
    print(f"   Source: {source_status}")
    print(f"   Type: {'🏢 SERVICE' if opp['is_service'] else '📦 PRODUCT'}")
    print(f"   Location: {'🌟 MICHIGAN' if opp['is_michigan'] else 'Other'}")
    print(f"   Score: {score}")
    print(f"   Record ID: {r['id']}")
    print()

print("\n" + "="*80)
print("🔥 TOP 3 RECOMMENDATIONS:")
print("="*80 + "\n")

for i, opp in enumerate(viable_rfps[:3], 1):
    r = opp['record']
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    days = opp['days_until_due']
    
    print(f"✅ OPPORTUNITY #{i}: {name}")
    print(f"   Due: {deadline} ({days} days)")
    print(f"   Why: ", end='')
    
    reasons = []
    if opp['is_michigan']:
        reasons.append("LOCAL MICHIGAN")
    if opp['is_service']:
        reasons.append("SERVICE CONTRACT (higher margin)")
    if opp['is_product']:
        reasons.append("PRODUCT RESALE")
    if 10 <= days <= 20:
        reasons.append("IDEAL TIMELINE")
        
    print(", ".join(reasons))
    print()
