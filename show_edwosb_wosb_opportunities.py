#!/usr/bin/env python3
"""
SHOW EDWOSB + WOSB OPPORTUNITIES (NATIONWIDE)
Focus on opportunities where buyers MUST use certified woman-owned businesses

Created: February 5, 2026
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
print("🎯 EDWOSB + WOSB OPPORTUNITIES - BUYERS MUST USE YOU!")
print("=" * 80)
print()

all_records = table.all()
print(f"📊 Total opportunities in system: {len(all_records)}")
print()

# Michigan local government keywords
michigan_keywords = ['rcoc', 'wayne county', 'oakland county', 'detroit', 'canton']

# Categorize opportunities
edwosb_opportunities = []
wosb_opportunities = []
michigan_local = []
other = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    agency = fields.get('Agency Name', '').lower()
    set_aside = fields.get('Set-Aside Type', '').upper()
    status = fields.get('Status', 'New')
    deadline = fields.get('Deadline', '')
    
    # Skip closed opportunities
    if status in ['Lost', 'Won', 'Not Pursuing']:
        continue
    
    # Skip expired
    if deadline:
        try:
            due_date = datetime.strptime(deadline, '%Y-%m-%d')
            if due_date < datetime.now():
                continue
        except:
            pass
    
    # Categorize
    if 'EDWOSB' in set_aside:
        edwosb_opportunities.append(r)
    elif 'WOSB' in set_aside:
        wosb_opportunities.append(r)
    elif any(kw in name or kw in agency for kw in michigan_keywords):
        michigan_local.append(r)
    else:
        other.append(r)

print("=" * 80)
print("📊 OPPORTUNITY BREAKDOWN:")
print("=" * 80)
print()
print(f"🏆 EDWOSB (Buyers MUST use EDWOSB companies): {len(edwosb_opportunities)}")
print(f"🟢 WOSB (Buyers MUST use woman-owned companies): {len(wosb_opportunities)}")
print(f"🔵 Michigan Local Government (Geographic advantage): {len(michigan_local)}")
print(f"⚪ Other (Unrestricted/Other set-asides): {len(other)}")
print()
print(f"🎯 FOCUS ON: {len(edwosb_opportunities) + len(wosb_opportunities) + len(michigan_local)} opportunities")
print(f"❌ IGNORE: {len(other)} opportunities (too competitive or don't qualify)")
print()

# Show EDWOSB opportunities
if edwosb_opportunities:
    print("=" * 80)
    print("🏆 EDWOSB OPPORTUNITIES (HIGHEST PRIORITY - BUYERS MUST USE YOU!):")
    print("=" * 80)
    print()
    
    for i, r in enumerate(edwosb_opportunities, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        
        # Show location if available
        city = fields.get('Place of Performance City', '')
        state = fields.get('Place of Performance State', '')
        if city or state:
            print(f"   Location: {city}, {state}")
        
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        
        print(f"   Status: {fields.get('Status', 'New')}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("❌ NO EDWOSB OPPORTUNITIES FOUND")
    print("   → Need to run mining script to find more!")
    print()

# Show WOSB opportunities
if wosb_opportunities:
    print("=" * 80)
    print("🟢 WOSB OPPORTUNITIES (BUYERS MUST USE WOMAN-OWNED BUSINESSES):")
    print("=" * 80)
    print()
    
    for i, r in enumerate(wosb_opportunities[:10], 1):  # Show first 10
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        
        city = fields.get('Place of Performance City', '')
        state = fields.get('Place of Performance State', '')
        if city or state:
            print(f"   Location: {city}, {state}")
        
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        
        print(f"   ID: {r['id']}")
        print()
    
    if len(wosb_opportunities) > 10:
        print(f"... and {len(wosb_opportunities) - 10} more WOSB opportunities")
        print()
else:
    print("❌ NO WOSB OPPORTUNITIES FOUND")
    print()

# Show Michigan local
if michigan_local:
    print("=" * 80)
    print("🔵 MICHIGAN LOCAL GOVERNMENT (GEOGRAPHIC ADVANTAGE):")
    print("=" * 80)
    print()
    
    for i, r in enumerate(michigan_local[:10], 1):  # Show first 10
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        print(f"   ID: {r['id']}")
        print()
    
    if len(michigan_local) > 10:
        print(f"... and {len(michigan_local) - 10} more Michigan opportunities")
        print()

print("=" * 80)
print("💡 NEXT STEPS:")
print("=" * 80)
print()
print("1. Review EDWOSB opportunities (HIGHEST PRIORITY)")
print("   → Buyers MUST award to EDWOSB companies")
print("   → Least competition")
print("   → Location doesn't matter!")
print()
print("2. Review WOSB opportunities (GOOD)")
print("   → Buyers MUST award to woman-owned businesses")
print("   → More competition than EDWOSB, but still restricted")
print()
print("3. Review Michigan local opportunities (GOOD)")
print("   → Geographic advantage (lower shipping, local relationships)")
print("   → Pursue even without set-aside")
print()
print("4. IGNORE unrestricted bids")
print(f"   → {len(other)} opportunities = too competitive")
print()
print("🚀 Run mining script to find more EDWOSB/WOSB opportunities:")
print("   python3 mine_real_federal_forecasts.py")
print()
print("=" * 80)
