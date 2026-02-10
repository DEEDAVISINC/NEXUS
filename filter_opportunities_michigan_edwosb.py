#!/usr/bin/env python3
"""
FILTER OPPORTUNITIES: MICHIGAN + EDWOSB ONLY
Show only relevant opportunities for Dee Davis Inc.

Created: February 5, 2026
"""

from pyairtable import Api
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

print("=" * 80)
print("🔍 FILTERING OPPORTUNITIES: MICHIGAN + EDWOSB ONLY")
print("=" * 80)
print()

all_records = table.all()
print(f"📊 Total opportunities in system: {len(all_records)}")
print()

# Filter criteria
michigan_keywords = ['michigan', 'mi', 'detroit', 'grand rapids', 'lansing', 'ann arbor', 
                     'flint', 'dearborn', 'warren', 'sterling heights', 'troy', 
                     'rcoc', 'wayne county', 'oakland county', 'macomb county']

filtered_opportunities = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    agency = fields.get('Agency Name', '').lower()
    location = fields.get('Place of Performance City', '').lower() + ' ' + fields.get('Place of Performance State', '').lower()
    set_aside = fields.get('Set-Aside Type', '').upper()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    
    # Skip if already decided
    if status in ['Lost', 'Won', 'Not Pursuing']:
        continue
    
    # Skip if no deadline or expired
    if not deadline:
        continue
    
    try:
        due_date = datetime.strptime(deadline, '%Y-%m-%d')
        if due_date < datetime.now():
            continue  # Expired
    except:
        pass
    
    # Check filters
    is_michigan = False
    is_edwosb = False
    
    # Michigan check
    for keyword in michigan_keywords:
        if keyword in name or keyword in agency or keyword in location:
            is_michigan = True
            break
    
    # EDWOSB check
    if 'EDWOSB' in set_aside:
        is_edwosb = True
    
    # Include if:
    # 1. Michigan + EDWOSB (BEST)
    # 2. Michigan local government (any set-aside)
    # 3. EDWOSB anywhere if high value
    
    reason = None
    priority = 0
    
    if is_michigan and is_edwosb:
        reason = "✅ Michigan + EDWOSB (PERFECT MATCH)"
        priority = 100
    elif is_michigan:
        reason = "✅ Michigan-based (local advantage)"
        priority = 80
    elif is_edwosb:
        # Only include EDWOSB outside Michigan if high value
        estimated_value = fields.get('Estimated Value', 0)
        if estimated_value and estimated_value >= 100000:
            reason = "🟡 EDWOSB (high value, out of state)"
            priority = 50
        else:
            continue  # Skip low-value out-of-state EDWOSB
    else:
        continue  # Skip everything else
    
    filtered_opportunities.append({
        'record': r,
        'fields': fields,
        'reason': reason,
        'priority': priority
    })

# Sort by priority
filtered_opportunities.sort(key=lambda x: -x['priority'])

print(f"🎯 FILTERED RESULTS: {len(filtered_opportunities)} opportunities")
print()

# Categorize
michigan_edwosb = [o for o in filtered_opportunities if o['priority'] == 100]
michigan_only = [o for o in filtered_opportunities if o['priority'] == 80]
edwosb_only = [o for o in filtered_opportunities if o['priority'] == 50]

print(f"🏆 Michigan + EDWOSB: {len(michigan_edwosb)}")
print(f"🟢 Michigan (any set-aside): {len(michigan_only)}")
print(f"🟡 EDWOSB (out of state, high value): {len(edwosb_only)}")
print()

if michigan_edwosb:
    print("=" * 80)
    print("🏆 MICHIGAN + EDWOSB (HIGHEST PRIORITY):")
    print("=" * 80)
    print()
    
    for i, opp in enumerate(michigan_edwosb[:10], 1):
        fields = opp['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:75]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Location: {fields.get('Place of Performance City', '')}, {fields.get('Place of Performance State', '')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Value: ${fields.get('Estimated Value', 0):,.0f}" if fields.get('Estimated Value') else "   Value: Unknown")
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   ID: {opp['record']['id']}")
        print()

if michigan_only:
    print("=" * 80)
    print("🟢 MICHIGAN LOCAL GOVERNMENT (ALL BID TYPES):")
    print("=" * 80)
    print()
    
    for i, opp in enumerate(michigan_only[:10], 1):
        fields = opp['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:75]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Value: ${fields.get('Estimated Value', 0):,.0f}" if fields.get('Estimated Value') else "   Value: Unknown")
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   ID: {opp['record']['id']}")
        print()

if edwosb_only:
    print("=" * 80)
    print("🟡 EDWOSB OUT-OF-STATE (HIGH VALUE ONLY):")
    print("=" * 80)
    print()
    
    for i, opp in enumerate(edwosb_only[:5], 1):
        fields = opp['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:75]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Location: {fields.get('Place of Performance City', '')}, {fields.get('Place of Performance State', '')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   Value: ${fields.get('Estimated Value', 0):,.0f}" if fields.get('Estimated Value') else "   Value: Unknown")
        print(f"   ID: {opp['record']['id']}")
        print()

print("=" * 80)
print("💡 RECOMMENDATION:")
print("=" * 80)
print()
print("Focus on:")
print(f"  1. {len(michigan_edwosb)} Michigan + EDWOSB opportunities (PERFECT)")
print(f"  2. {len(michigan_only)} Michigan local government bids (GOOD)")
print()
print("Ignore:")
print(f"  • {len(all_records) - len(filtered_opportunities)} opportunities outside filters")
print()
print("Next step:")
print("  Update NEXUS frontend to ONLY display these filtered opportunities")
print()
print("=" * 80)
