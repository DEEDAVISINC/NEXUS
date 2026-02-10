#!/usr/bin/env python3
"""
Find Michigan/Local RFPs - actual solicitations, not federal forecasts
"""

from pyairtable import Api
from datetime import datetime, timedelta

AIRTABLE_API_KEY = "patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa"
BASE_ID = "appaJZqKVUn3yJ7ma"

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

all_records = table.all()

print(f'\n📊 Total NEXUS opportunities: {len(all_records)}\n')

# Look for actual RFPs (not forecasts) with actionable deadlines
michigan_rfps = []
midwest_rfps = []
product_rfps = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    source_status = fields.get('Source Status', '').lower()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    rfp_number = fields.get('RFP NUMBER', '')
    
    # Skip if already working
    if status in ['Pursuing', 'Submitted', 'Won', 'Lost', 'Not Pursuing']:
        continue
    
    # Must have deadline
    if not deadline:
        continue
    
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days
        
        # Reasonable timeline (3-45 days)
        if not (3 <= days_until_due <= 45):
            continue
    except:
        continue
    
    # Check for Michigan/Local
    is_michigan = any(word in source_status or word in name for word in [
        'michigan', 'detroit', 'oakland', 'wayne', 'macomb', 'lansing',
        'flint', 'grand rapids', 'sterling', 'troy', 'pontiac', 'rcoc',
        'bloomfield', 'birmingham', 'royal oak', 'warren', 'dearborn'
    ])
    
    # Check for Midwest states
    is_midwest = any(word in source_status or word in name for word in [
        'illinois', 'ohio', 'indiana', 'wisconsin', 'chicago', 'cleveland',
        'columbus', 'milwaukee', 'indianapolis'
    ])
    
    # Check for product opportunities
    is_product = any(word in name for word in [
        'supplies', 'equipment', 'materials', 'tools', 'parts', 'furniture',
        'paper', 'vehicles', 'truck', 'cleaning supplies'
    ])
    
    # Skip sources sought and forecasts (want actual RFPs)
    if 'sources sought' in source_status or 'forecast' in source_status:
        continue
    
    if is_michigan:
        michigan_rfps.append((r, days_until_due, 'MI'))
    elif is_midwest:
        midwest_rfps.append((r, days_until_due, 'MW'))
    elif is_product:
        product_rfps.append((r, days_until_due, 'PROD'))

# Sort all by deadline
michigan_rfps.sort(key=lambda x: x[1])
midwest_rfps.sort(key=lambda x: x[1])
product_rfps.sort(key=lambda x: x[1])

print("="*80)
print("🌟 MICHIGAN OPPORTUNITIES (Priority #1):")
print("="*80 + "\n")

if michigan_rfps:
    for i, (r, days, _) in enumerate(michigan_rfps[:5], 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')}")
        print(f"   Due: {fields.get('Deadline')} ({days} days)")
        print(f"   RFP#: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Source: {fields.get('Source Status', 'Unknown')}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("   No Michigan opportunities found with current criteria\n")

print("="*80)
print("📍 MIDWEST OPPORTUNITIES (Priority #2):")
print("="*80 + "\n")

if midwest_rfps:
    for i, (r, days, _) in enumerate(midwest_rfps[:5], 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')}")
        print(f"   Due: {fields.get('Deadline')} ({days} days)")
        print(f"   RFP#: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Source: {fields.get('Source Status', 'Unknown')}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("   No Midwest opportunities found\n")

print("="*80)
print("📦 PRODUCT RESALE OPPORTUNITIES (Priority #3):")
print("="*80 + "\n")

if product_rfps:
    for i, (r, days, _) in enumerate(product_rfps[:10], 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')}")
        print(f"   Due: {fields.get('Deadline')} ({days} days)")
        print(f"   RFP#: {fields.get('RFP NUMBER', 'N/A')}")
        print(f"   Source: {fields.get('Source Status', 'Unknown')[:50]}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("   No product opportunities found\n")

# Combined top 3
all_viable = michigan_rfps + midwest_rfps + product_rfps
all_viable.sort(key=lambda x: (-10 if x[2] == 'MI' else -5 if x[2] == 'MW' else -1, x[1]))

print("="*80)
print("🔥 TOP 3 NEW OPPORTUNITIES TO REVIEW:")
print("="*80 + "\n")

if len(all_viable) >= 3:
    for i, (r, days, type_) in enumerate(all_viable[:3], 1):
        fields = r['fields']
        print(f"✅ #{i}: {fields.get('Name', 'Untitled')}")
        print(f"     Due: {fields.get('Deadline')} ({days} days)")
        print(f"     Type: {type_}")
        print(f"     Record ID: {r['id']}")
        print()
else:
    print(f"   Only found {len(all_viable)} viable opportunities\n")
    print("   💡 NEXUS may need RSS feeds for:")
    print("      - BidNet Direct (Michigan local)")
    print("      - DemandStar (Midwest)")
    print("      - PlanetBids (Michigan cities)")
    print("      - BuySpeed (County/local)")
