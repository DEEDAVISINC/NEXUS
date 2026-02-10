#!/usr/bin/env python3
"""
CONFIGURE OPPORTUNITY DISCOVERY FILTERS
Set Michigan + EDWOSB as default filters

Created: February 5, 2026
Purpose: Stop flooding system with irrelevant opportunities
"""

from pyairtable import Api
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

print("=" * 80)
print("🔍 ANALYZING OPPORTUNITIES BY STATE + SET-ASIDE")
print("=" * 80)
print()

all_records = table.all()
print(f"📊 Total opportunities: {len(all_records)}")
print()

# Count by state
states = {}
edwosb_count = 0
wosb_count = 0
michigan_local = 0

for r in all_records:
    fields = r['fields']
    state = fields.get('Place of Performance State', 'Unknown').upper()
    set_aside = fields.get('Set-Aside Type', 'None').upper()
    name = fields.get('Name', '').lower()
    status = fields.get('Status', 'New')
    
    # Skip closed opportunities
    if status in ['Lost', 'Won', 'Not Pursuing']:
        continue
    
    # Count Michigan local government (RCOC, Wayne County, etc.)
    if any(x in name for x in ['rcoc', 'wayne county', 'oakland county', 'detroit', 'canton']):
        michigan_local += 1
    
    # Count by state
    if state not in states:
        states[state] = 0
    states[state] += 1
    
    # Count EDWOSB
    if 'EDWOSB' in set_aside:
        edwosb_count += 1
    if 'WOSB' in set_aside:
        wosb_count += 1

# Sort states by count
sorted_states = sorted(states.items(), key=lambda x: -x[1])

print("📍 TOP 10 STATES BY OPPORTUNITY COUNT:")
print()
for i, (state, count) in enumerate(sorted_states[:10], 1):
    pct = (count / len(all_records)) * 100
    marker = "✅" if state == "MI" else "  "
    print(f"{marker} {i}. {state}: {count} opportunities ({pct:.1f}%)")
print()

print("=" * 80)
print("🎯 SET-ASIDE ANALYSIS:")
print("=" * 80)
print()
print(f"EDWOSB: {edwosb_count} opportunities")
print(f"WOSB: {wosb_count} opportunities")
print(f"Michigan Local Government: {michigan_local} opportunities")
print()

print("=" * 80)
print("💡 RECOMMENDED FILTERS:")
print("=" * 80)
print()
print("PRIMARY SEARCH:")
print("  🎯 State: Michigan (MI)")
print("  🎯 Set-Aside: EDWOSB")
print("  🎯 Expected results: 0-5 opportunities (highly targeted)")
print()
print("SECONDARY SEARCH:")
print("  🟢 State: Michigan (MI)")
print("  🟢 Set-Aside: ANY (includes local government)")
print(f"  🟢 Expected results: {states.get('MI', 0)} opportunities")
print()
print("TERTIARY SEARCH:")
print("  🟡 State: ANY")
print("  🟡 Set-Aside: EDWOSB")
print("  🟡 Value: > $100K")
print(f"  🟡 Expected results: {edwosb_count} opportunities")
print()

print("=" * 80)
print("🔧 WHAT TO DO:")
print("=" * 80)
print()
print("1. Update SAM.gov mining to use:")
print("   • state=MI")
print("   • typeOfSetAside=EDWOSB")
print()
print("2. Update NEXUS frontend filter defaults:")
print("   • Default state filter: Michigan")
print("   • Default set-aside filter: EDWOSB + Local Government")
print()
print("3. Add 'Hide Irrelevant' toggle:")
print("   • Hides all non-Michigan, non-EDWOSB opportunities")
print("   • Reduces 2,867 → ~140 opportunities")
print()
print("=" * 80)
