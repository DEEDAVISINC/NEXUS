#!/usr/bin/env python3
"""
SHOW ALL DIVERSITY SET-ASIDE OPPORTUNITIES
EDWOSB, WOSB, MBE, DBE, WBE - Buyers MUST use certified companies!

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
print("🎯 ALL DIVERSITY SET-ASIDE OPPORTUNITIES")
print("Buyers MUST use EDWOSB/WOSB/MBE/DBE/WBE certified companies!")
print("=" * 80)
print()

all_records = table.all()
print(f"📊 Total opportunities in system: {len(all_records)}")
print()

# Michigan local government keywords
michigan_keywords = ['rcoc', 'wayne county', 'oakland county', 'detroit', 'canton']

# Diversity set-aside keywords
diversity_keywords = ['EDWOSB', 'WOSB', 'MBE', 'DBE', 'WBE', 'MINORITY', 'WOMAN-OWNED', 'WOMAN OWNED']

# Categorize opportunities
edwosb = []
wosb = []
mbe = []
dbe = []
wbe = []
michigan_local = []
other = []

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').upper()
    agency = fields.get('Agency Name', '').upper()
    set_aside = fields.get('Set-Aside Type', '').upper()
    description = fields.get('Description', '').upper()
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
    
    # Check all fields for diversity keywords
    all_text = f"{name} {agency} {set_aside} {description}"
    
    # Categorize by set-aside type
    matched = False
    
    if 'EDWOSB' in set_aside or 'EDWOSB' in all_text:
        edwosb.append(r)
        matched = True
    elif 'WOSB' in set_aside or 'WOSB' in all_text:
        wosb.append(r)
        matched = True
    
    # Check for MBE/DBE/WBE
    if 'MBE' in all_text or 'MINORITY BUSINESS' in all_text:
        mbe.append(r)
        matched = True
    elif 'DBE' in all_text or 'DISADVANTAGED BUSINESS' in all_text:
        dbe.append(r)
        matched = True
    elif 'WBE' in all_text or 'WOMAN BUSINESS ENTERPRISE' in all_text:
        wbe.append(r)
        matched = True
    
    # Michigan local (even without set-aside)
    if not matched and any(kw in name or kw in agency for kw in michigan_keywords):
        michigan_local.append(r)
        matched = True
    
    if not matched:
        other.append(r)

# Calculate totals
diversity_total = len(edwosb) + len(wosb) + len(mbe) + len(dbe) + len(wbe)
focus_total = diversity_total + len(michigan_local)

print("=" * 80)
print("📊 OPPORTUNITY BREAKDOWN:")
print("=" * 80)
print()
print("🏆 DIVERSITY SET-ASIDES (Buyers MUST use certified companies):")
print(f"   • EDWOSB: {len(edwosb)}")
print(f"   • WOSB: {len(wosb)}")
print(f"   • MBE (Minority Business Enterprise): {len(mbe)}")
print(f"   • DBE (Disadvantaged Business Enterprise): {len(dbe)}")
print(f"   • WBE (Woman Business Enterprise): {len(wbe)}")
print(f"   TOTAL DIVERSITY: {diversity_total}")
print()
print(f"🔵 Michigan Local Government: {len(michigan_local)}")
print()
print(f"🎯 FOCUS ON: {focus_total} opportunities")
print(f"❌ IGNORE: {len(other)} unrestricted/other set-asides")
print()

# Show EDWOSB
if edwosb:
    print("=" * 80)
    print("🏆 EDWOSB OPPORTUNITIES:")
    print("=" * 80)
    print()
    for i, r in enumerate(edwosb, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        print(f"   ID: {r['id']}")
        print()

# Show WOSB
if wosb:
    print("=" * 80)
    print("🟢 WOSB OPPORTUNITIES:")
    print("=" * 80)
    print()
    for i, r in enumerate(wosb, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        print(f"   ID: {r['id']}")
        print()

# Show MBE
if mbe:
    print("=" * 80)
    print("🟡 MBE (MINORITY BUSINESS ENTERPRISE) OPPORTUNITIES:")
    print("=" * 80)
    print()
    for i, r in enumerate(mbe, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("❌ NO MBE OPPORTUNITIES FOUND IN CURRENT DATA")
    print()

# Show DBE
if dbe:
    print("=" * 80)
    print("🟠 DBE (DISADVANTAGED BUSINESS ENTERPRISE) OPPORTUNITIES:")
    print("=" * 80)
    print()
    for i, r in enumerate(dbe, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("❌ NO DBE OPPORTUNITIES FOUND IN CURRENT DATA")
    print()

# Show WBE
if wbe:
    print("=" * 80)
    print("🔵 WBE (WOMAN BUSINESS ENTERPRISE) OPPORTUNITIES:")
    print("=" * 80)
    print()
    for i, r in enumerate(wbe, 1):
        fields = r['fields']
        print(f"{i}. {fields.get('Name', 'Untitled')[:70]}")
        print(f"   Agency: {fields.get('Agency Name', 'Unknown')}")
        print(f"   Deadline: {fields.get('Deadline', 'Unknown')}")
        value = fields.get('Estimated Value', 0)
        if value:
            print(f"   Value: ${value:,.0f}")
        print(f"   ID: {r['id']}")
        print()
else:
    print("❌ NO WBE OPPORTUNITIES FOUND IN CURRENT DATA")
    print()

print("=" * 80)
print("💡 WHAT THESE MEAN:")
print("=" * 80)
print()
print("FEDERAL CERTIFICATIONS:")
print("  • EDWOSB = Economically Disadvantaged Woman-Owned Small Business")
print("  • WOSB = Woman-Owned Small Business")
print("  • Used on federal contracts (SAM.gov)")
print()
print("STATE/LOCAL CERTIFICATIONS:")
print("  • MBE = Minority Business Enterprise")
print("  • DBE = Disadvantaged Business Enterprise")
print("  • WBE = Woman Business Enterprise")
print("  • Used on state/local/municipal contracts")
print()
print("YOU QUALIFY FOR ALL OF THESE! ✅")
print()
print("=" * 80)
print("🚀 NEXT ACTIONS:")
print("=" * 80)
print()
print("1. Update mining script to search for MBE/DBE/WBE opportunities")
print("2. Check if you have MBE/DBE/WBE certifications for Michigan")
print("3. Apply for MBE/DBE/WBE certifications if not already certified")
print("4. Focus on diversity set-aside opportunities (any state!)")
print()
print("=" * 80)
