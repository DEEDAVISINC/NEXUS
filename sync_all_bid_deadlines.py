#!/usr/bin/env python3
"""
Sync All Bid Deadlines to Calendar and Agenda
Queries NEXUS for all opportunities with deadlines and creates calendar entries
"""

import os
from datetime import datetime, timedelta
from pyairtable import Api
from pathlib import Path

# Load environment variables
AIRTABLE_PAT = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not AIRTABLE_PAT or not AIRTABLE_BASE_ID:
    print("ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID in environment")
    exit(1)

# Initialize Airtable
api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

# Get all opportunities with deadlines
print("📊 Fetching all opportunities from NEXUS...")

try:
    all_opportunities = opportunities_table.all()
    print(f"✅ Found {len(all_opportunities)} total opportunities in NEXUS")
except Exception as e:
    print(f"❌ Error fetching opportunities: {e}")
    exit(1)

# Filter opportunities with deadlines
opportunities_with_deadlines = []

for opp in all_opportunities:
    fields = opp['fields']
    deadline = fields.get('Deadline')
    name = fields.get('Name', 'Unnamed Opportunity')
    set_aside = fields.get('Set-Aside Type', '')
    
    if deadline:
        opportunities_with_deadlines.append({
            'id': opp['id'],
            'name': name,
            'deadline': deadline,
            'set_aside': set_aside,
            'rfp_number': fields.get('RFP NUMBER', ''),
            'agency': fields.get('AGENCY NAME', ''),
            'priority': fields.get('Priority', ''),
            'source_status': fields.get('Source Status', ''),
        })

print(f"✅ Found {len(opportunities_with_deadlines)} opportunities with deadlines")

# Sort by deadline
opportunities_with_deadlines.sort(key=lambda x: x['deadline'])

# Print all opportunities with deadlines
print("\n" + "="*80)
print("📅 ALL OPPORTUNITIES WITH DEADLINES (Sorted by Date)")
print("="*80)

for idx, opp in enumerate(opportunities_with_deadlines, 1):
    deadline_str = opp['deadline']
    try:
        deadline_date = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        formatted_date = deadline_date.strftime('%A, %B %d, %Y')
        
        # Calculate days remaining
        now = datetime.now(deadline_date.tzinfo)
        days_remaining = (deadline_date - now).days
        
        if days_remaining < 0:
            status = "⚠️ PAST DUE"
        elif days_remaining == 0:
            status = "🚨 DUE TODAY"
        elif days_remaining <= 3:
            status = f"🔥 {days_remaining} DAYS"
        elif days_remaining <= 7:
            status = f"⚡ {days_remaining} days"
        else:
            status = f"📅 {days_remaining} days"
            
    except:
        formatted_date = deadline_str
        status = "📅"
    
    print(f"\n{idx}. {opp['name']}")
    print(f"   Deadline: {formatted_date} {status}")
    print(f"   Set-Aside: {opp['set_aside']}")
    print(f"   RFP#: {opp['rfp_number']}")
    print(f"   Agency: {opp['agency']}")
    print(f"   Priority: {opp['priority']}")

# Create calendar entries
print("\n" + "="*80)
print("📅 CREATING CALENDAR ENTRIES")
print("="*80)

calendars_dir = Path("/Users/deedavis/NEXUS BACKEND/calendars")
calendars_dir.mkdir(exist_ok=True)

created_calendars = []

for opp in opportunities_with_deadlines:
    try:
        deadline_str = opp['deadline']
        deadline_date = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        
        # Calculate days remaining
        now = datetime.now(deadline_date.tzinfo)
        days_remaining = (deadline_date - now).days
        
        # Skip if past due
        if days_remaining < 0:
            continue
        
        # Format for filename (safe characters only)
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in opp['name'])
        safe_name = safe_name[:50]  # Limit length
        
        deadline_formatted = deadline_date.strftime('%Y-%m-%d')
        filename = f"{opp['rfp_number']}_{safe_name}_{deadline_formatted}.ics"
        filepath = calendars_dir / filename
        
        # Create ICS content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Dee Davis Inc//NEXUS Bid Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:NEXUS Bid Deadlines
X-WR-TIMEZONE:America/Detroit

BEGIN:VEVENT
UID:{opp['id']}@nexus.deedavis.biz
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{deadline_date.strftime('%Y%m%d')}
SUMMARY:🎯 BID DUE: {opp['name']}
DESCRIPTION:RFP Number: {opp['rfp_number']}\\nAgency: {opp['agency']}\\nSet-Aside: {opp['set_aside']}\\nPriority: {opp['priority']}\\n\\nDays Remaining: {days_remaining}
LOCATION:{opp['agency']}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-P3D
DESCRIPTION:3 days until {opp['name']} deadline
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
DESCRIPTION:1 day until {opp['name']} deadline
ACTION:DISPLAY
END:VALARM
END:VEVENT

END:VCALENDAR"""
        
        # Write calendar file
        with open(filepath, 'w') as f:
            f.write(ics_content)
        
        created_calendars.append({
            'name': opp['name'],
            'deadline': deadline_formatted,
            'days': days_remaining,
            'file': filename
        })
        
        print(f"✅ Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error creating calendar for {opp['name']}: {e}")

print(f"\n✅ Created {len(created_calendars)} calendar entries in {calendars_dir}")

# Create agenda summary
print("\n" + "="*80)
print("📋 CREATING AGENDA SUMMARY")
print("="*80)

agenda_content = f"""# 📅 COMPLETE BID DEADLINES AGENDA
## All Active Opportunities in NEXUS

**Generated:** {datetime.now().strftime('%A, %B %d, %Y @ %I:%M %p')}  
**Total Opportunities:** {len(opportunities_with_deadlines)}  
**Active (Not Past Due):** {len([o for o in opportunities_with_deadlines if (datetime.fromisoformat(o['deadline'].replace('Z', '+00:00')) - datetime.now(datetime.fromisoformat(o['deadline'].replace('Z', '+00:00')).tzinfo)).days >= 0])}

---

## 🚨 URGENT (Next 7 Days)

"""

# Group by urgency
urgent = []  # 0-7 days
upcoming = []  # 8-14 days
future = []  # 15+ days
past_due = []  # Past deadline

for opp in opportunities_with_deadlines:
    try:
        deadline_date = datetime.fromisoformat(opp['deadline'].replace('Z', '+00:00'))
        now = datetime.now(deadline_date.tzinfo)
        days_remaining = (deadline_date - now).days
        
        if days_remaining < 0:
            past_due.append((opp, days_remaining))
        elif days_remaining <= 7:
            urgent.append((opp, days_remaining))
        elif days_remaining <= 14:
            upcoming.append((opp, days_remaining))
        else:
            future.append((opp, days_remaining))
    except:
        continue

# Urgent opportunities
if urgent:
    for opp, days in urgent:
        deadline_date = datetime.fromisoformat(opp['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        if days == 0:
            status = "🚨 DUE TODAY!"
        elif days == 1:
            status = "🔥 DUE TOMORROW!"
        else:
            status = f"⚡ {days} DAYS"
        
        agenda_content += f"""
### {opp['name']} {status}

**Deadline:** {formatted}  
**Set-Aside:** {opp['set_aside']}  
**RFP Number:** {opp['rfp_number']}  
**Agency:** {opp['agency']}  
**Priority:** {opp['priority']}  
**Status:** {opp['source_status']}

---
"""
else:
    agenda_content += "\n*No urgent deadlines in the next 7 days.*\n"

# Upcoming opportunities
agenda_content += "\n## 📅 UPCOMING (8-14 Days)\n\n"

if upcoming:
    for opp, days in upcoming:
        deadline_date = datetime.fromisoformat(opp['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        agenda_content += f"""
### {opp['name']} ({days} days)

**Deadline:** {formatted}  
**Set-Aside:** {opp['set_aside']}  
**RFP Number:** {opp['rfp_number']}  
**Agency:** {opp['agency']}

---
"""
else:
    agenda_content += "\n*No opportunities due in 8-14 days.*\n"

# Future opportunities
agenda_content += "\n## 🔮 FUTURE (15+ Days)\n\n"

if future:
    for opp, days in future:
        deadline_date = datetime.fromisoformat(opp['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        agenda_content += f"""
### {opp['name']} ({days} days)

**Deadline:** {formatted}  
**Set-Aside:** {opp['set_aside']}  
**RFP Number:** {opp['rfp_number']}  
**Agency:** {opp['agency']}

---
"""
else:
    agenda_content += "\n*No future opportunities beyond 14 days.*\n"

# Past due
if past_due:
    agenda_content += "\n## ⚠️ PAST DUE\n\n"
    for opp, days in past_due:
        deadline_date = datetime.fromisoformat(opp['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        agenda_content += f"""
### {opp['name']} (PAST DUE by {abs(days)} days)

**Deadline:** {formatted}  
**Set-Aside:** {opp['set_aside']}  
**RFP Number:** {opp['rfp_number']}  
**Agency:** {opp['agency']}

---
"""

# Summary stats
agenda_content += f"""

---

## 📊 SUMMARY

**Total Opportunities:** {len(opportunities_with_deadlines)}  
**Urgent (0-7 days):** {len(urgent)}  
**Upcoming (8-14 days):** {len(upcoming)}  
**Future (15+ days):** {len(future)}  
**Past Due:** {len(past_due)}

---

*Generated by NEXUS Bid Tracking System*  
*Synced with Airtable GPSS OPPORTUNITIES table*
"""

# Write agenda file
agenda_file = Path("/Users/deedavis/NEXUS BACKEND/COMPLETE_BID_DEADLINES_AGENDA.md")
with open(agenda_file, 'w') as f:
    f.write(agenda_content)

print(f"✅ Created agenda: {agenda_file}")

# Summary
print("\n" + "="*80)
print("✅ SYNC COMPLETE!")
print("="*80)
print(f"📊 Total Opportunities: {len(opportunities_with_deadlines)}")
print(f"🚨 Urgent (0-7 days): {len(urgent)}")
print(f"📅 Upcoming (8-14 days): {len(upcoming)}")
print(f"🔮 Future (15+ days): {len(future)}")
print(f"⚠️ Past Due: {len(past_due)}")
print(f"📅 Calendar Entries Created: {len(created_calendars)}")
print(f"📋 Agenda File: {agenda_file}")
print("\n✅ All deadlines synced to calendar and agenda!")
