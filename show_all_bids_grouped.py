#!/usr/bin/env python3
"""
SHOW ALL OPPORTUNITIES - GROUPED BY URGENCY
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

all_records = table.all()

# Group by days until deadline
today = []  # 0 days
this_week = []  # 1-7 days  
next_week = []  # 8-14 days
two_weeks = []  # 15-21 days
month = []  # 22-30 days
beyond = []  # 31-90 days

for r in all_records:
    fields = r['fields']
    deadline = fields.get('Deadline', '')
    status = fields.get('Status', 'New')
    
    if status in ['Lost', 'Won', 'Not Pursuing']:
        continue
    
    if deadline:
        try:
            due_date = datetime.strptime(deadline, '%Y-%m-%d')
            days_until = (due_date - datetime.now()).days
            
            if days_until == 0:
                today.append((r, days_until))
            elif 1 <= days_until <= 7:
                this_week.append((r, days_until))
            elif 8 <= days_until <= 14:
                next_week.append((r, days_until))
            elif 15 <= days_until <= 21:
                two_weeks.append((r, days_until))
            elif 22 <= days_until <= 30:
                month.append((r, days_until))
            elif 31 <= days_until <= 90:
                beyond.append((r, days_until))
        except:
            pass

print("=" * 100)
print("ALL OPPORTUNITIES - GROUPED BY URGENCY")
print("=" * 100)
print()
print(f"📊 DUE TODAY (Feb 6): {len(today)} opportunities")
print(f"🔥 DUE THIS WEEK (Feb 7-12): {len(this_week)} opportunities")
print(f"🟡 DUE NEXT WEEK (Feb 13-20): {len(next_week)} opportunities")
print(f"🟢 DUE IN 2-3 WEEKS (Feb 21-27): {len(two_weeks)} opportunities")
print(f"🔵 DUE IN 3-4 WEEKS (Feb 28-Mar 7): {len(month)} opportunities")
print(f"⚪ DUE 1-3 MONTHS (Mar 8-May 6): {len(beyond)} opportunities")
print()
total = len(today) + len(this_week) + len(next_week) + len(two_weeks) + len(month) + len(beyond)
print(f"TOTAL ACTIVE: {total}")
print()
print("=" * 100)
print()

# Show THIS WEEK opportunities (1-7 days) - ALL OF THEM
print("🔥 DUE THIS WEEK (NEXT 1-7 DAYS) - ALL OPPORTUNITIES:")
print("=" * 100)
print()

this_week.sort(key=lambda x: x[1])

for i, (r, days_until) in enumerate(this_week, 1):
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    value = fields.get('Estimated Value', 0)
    set_aside = fields.get('Set-Aside Type', 'None')
    rfp = fields.get('RFP NUMBER', '')
    
    print(f"{i}. {name[:85]}")
    print(f"   ⏰ DUE: {deadline} ({days_until} DAYS)")
    if value:
        print(f"   💰 ${value:,.0f}")
    if set_aside and set_aside not in ['None', 'NONE', '']:
        print(f"   🎯 {set_aside}")
    if rfp:
        print(f"   #{rfp}")
    print()

print()
print("=" * 100)
print()

# Show NEXT WEEK opportunities (8-14 days) - ALL OF THEM  
print("🟡 DUE NEXT WEEK (8-14 DAYS) - ALL OPPORTUNITIES:")
print("=" * 100)
print()

next_week.sort(key=lambda x: x[1])

for i, (r, days_until) in enumerate(next_week, 1):
    fields = r['fields']
    name = fields.get('Name', 'Untitled')
    deadline = fields.get('Deadline', 'Unknown')
    value = fields.get('Estimated Value', 0)
    set_aside = fields.get('Set-Aside Type', 'None')
    
    print(f"{i}. {name[:85]}")
    print(f"   ⏰ DUE: {deadline} ({days_until} DAYS)")
    if value:
        print(f"   💰 ${value:,.0f}")
    if set_aside and set_aside not in ['None', 'NONE', '']:
        print(f"   🎯 {set_aside}")
    print()

print()
print(f"✅ COMPLETE! Showing {len(this_week)} this week + {len(next_week)} next week")
print()
print(f"📄 Full list (all 1,410): ALL_OPPORTUNITIES_COMPLETE_LIST.md")
print()
