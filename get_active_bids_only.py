#!/usr/bin/env python3
"""
Get ACTIVE BIDS ONLY - Bids we're actually pursuing, submitted, or won
"""

import os
from datetime import datetime
from pyairtable import Api

# Load environment variables
AIRTABLE_PAT = os.getenv('AIRTABLE_API_KEY', 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appaJZqKVUn3yJ7ma')

# Initialize Airtable
api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("📊 Fetching ACTIVE BIDS from NEXUS...")

# Get all opportunities
all_opportunities = opportunities_table.all()

# Filter for ACTIVE bids only
active_statuses = [
    'Submitted',
    'In Progress',
    'Awaiting Response',
    'Waiting on Quotes',
    'Quotes Received',
    'Preparing Submission',
    'Won',
    'Awarded',
    'Active Contract',
    'Sources Sought Submitted',
    'Capability Statement Submitted',
    'Under Review',
    'Shortlisted',
    'Negotiating',
    'Pricing Phase',
]

active_bids = []

for opp in all_opportunities:
    fields = opp['fields']
    source_status = fields.get('Source Status', '')
    priority = fields.get('Priority', '')
    name = fields.get('Name', 'Unnamed')
    deadline = fields.get('Deadline')
    
    # Check if this is an active bid
    is_active = False
    
    # Check source status
    for status in active_statuses:
        if status.lower() in source_status.lower():
            is_active = True
            break
    
    # Also check for high priority with upcoming deadlines
    if priority == 'High' and deadline:
        try:
            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            now = datetime.now(deadline_date.tzinfo)
            days_remaining = (deadline_date - now).days
            if 0 <= days_remaining <= 14:  # High priority with deadline in next 2 weeks
                is_active = True
        except:
            pass
    
    # Check if name indicates active work
    active_keywords = ['RCOC', 'Canton', 'NIH', 'VA Illiana', 'Guardrail', 'Rock Island', 
                       'Madison Heights', 'Oakland County', 'Livonia', 'Jackson County',
                       'CPS Energy', 'Fort Novosel']
    for keyword in active_keywords:
        if keyword.lower() in name.lower():
            is_active = True
            break
    
    if is_active:
        active_bids.append({
            'name': name,
            'deadline': deadline,
            'status': source_status,
            'priority': priority,
            'rfp_number': fields.get('RFP NUMBER', ''),
            'agency': fields.get('AGENCY NAME', ''),
            'set_aside': fields.get('Set-Aside Type', ''),
            'notes': fields.get('Notes', ''),
        })

# Sort by deadline
active_bids.sort(key=lambda x: x['deadline'] if x['deadline'] else '9999-12-31')

print(f"\n✅ Found {len(active_bids)} ACTIVE BIDS")
print("\n" + "="*80)
print("📋 ACTIVE BIDS - Dee Davis Inc. is Working On")
print("="*80)

for idx, bid in enumerate(active_bids, 1):
    deadline_str = ""
    if bid['deadline']:
        try:
            deadline_date = datetime.fromisoformat(bid['deadline'].replace('Z', '+00:00'))
            formatted_date = deadline_date.strftime('%A, %B %d, %Y')
            
            now = datetime.now(deadline_date.tzinfo)
            days_remaining = (deadline_date - now).days
            
            if days_remaining < 0:
                status_emoji = "⚠️ PAST DUE"
            elif days_remaining == 0:
                status_emoji = "🚨 DUE TODAY"
            elif days_remaining == 1:
                status_emoji = "🔥 DUE TOMORROW"
            elif days_remaining <= 7:
                status_emoji = f"⚡ {days_remaining} DAYS"
            else:
                status_emoji = f"📅 {days_remaining} days"
            
            deadline_str = f"{formatted_date} {status_emoji}"
        except:
            deadline_str = bid['deadline']
    else:
        deadline_str = "No deadline set"
    
    print(f"\n{idx}. {bid['name']}")
    print(f"   Deadline: {deadline_str}")
    print(f"   Status: {bid['status']}")
    print(f"   Priority: {bid['priority']}")
    print(f"   Set-Aside: {bid['set_aside']}")
    print(f"   RFP#: {bid['rfp_number']}")
    print(f"   Agency: {bid['agency']}")
    if bid['notes']:
        # Truncate notes if too long
        notes = bid['notes'][:200] + "..." if len(bid['notes']) > 200 else bid['notes']
        print(f"   Notes: {notes}")

print("\n" + "="*80)
print(f"✅ Total Active Bids: {len(active_bids)}")
print("="*80)

# Create markdown file
markdown = f"""# 📋 ACTIVE BIDS - DEE DAVIS INC.
## Bids We're Actually Working On

**Generated:** {datetime.now().strftime('%A, %B %d, %Y @ %I:%M %p')}  
**Total Active Bids:** {len(active_bids)}

---

"""

# Group by urgency
urgent = []  # 0-7 days
upcoming = []  # 8-14 days
future = []  # 15+ days
no_deadline = []

for bid in active_bids:
    if not bid['deadline']:
        no_deadline.append(bid)
        continue
    
    try:
        deadline_date = datetime.fromisoformat(bid['deadline'].replace('Z', '+00:00'))
        now = datetime.now(deadline_date.tzinfo)
        days_remaining = (deadline_date - now).days
        
        if days_remaining < 0:
            continue  # Skip past due
        elif days_remaining <= 7:
            urgent.append((bid, days_remaining))
        elif days_remaining <= 14:
            upcoming.append((bid, days_remaining))
        else:
            future.append((bid, days_remaining))
    except:
        no_deadline.append(bid)

# Urgent section
markdown += "## 🚨 URGENT (Next 7 Days)\n\n"
if urgent:
    for bid, days in urgent:
        deadline_date = datetime.fromisoformat(bid['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        if days == 0:
            status = "🚨 DUE TODAY!"
        elif days == 1:
            status = "🔥 DUE TOMORROW!"
        else:
            status = f"⚡ {days} DAYS"
        
        markdown += f"""### {bid['name']} {status}

**Deadline:** {formatted}  
**Status:** {bid['status']}  
**Priority:** {bid['priority']}  
**Set-Aside:** {bid['set_aside']}  
**RFP Number:** {bid['rfp_number']}  
**Agency:** {bid['agency']}

"""
        if bid['notes']:
            markdown += f"**Notes:** {bid['notes'][:300]}...\n\n"
        markdown += "---\n\n"
else:
    markdown += "*No urgent bids in next 7 days.*\n\n"

# Upcoming section
markdown += "## 📅 UPCOMING (8-14 Days)\n\n"
if upcoming:
    for bid, days in upcoming:
        deadline_date = datetime.fromisoformat(bid['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        markdown += f"""### {bid['name']} ({days} days)

**Deadline:** {formatted}  
**Status:** {bid['status']}  
**Set-Aside:** {bid['set_aside']}  
**RFP Number:** {bid['rfp_number']}

---

"""
else:
    markdown += "*No upcoming bids in 8-14 days.*\n\n"

# Future section
markdown += "## 🔮 FUTURE (15+ Days)\n\n"
if future:
    for bid, days in future:
        deadline_date = datetime.fromisoformat(bid['deadline'].replace('Z', '+00:00'))
        formatted = deadline_date.strftime('%A, %B %d, %Y')
        
        markdown += f"""### {bid['name']} ({days} days)

**Deadline:** {formatted}  
**Status:** {bid['status']}  
**Set-Aside:** {bid['set_aside']}

---

"""
else:
    markdown += "*No future active bids beyond 14 days.*\n\n"

# No deadline section
if no_deadline:
    markdown += "## 📝 ONGOING (No Specific Deadline)\n\n"
    for bid in no_deadline:
        markdown += f"""### {bid['name']}

**Status:** {bid['status']}  
**Set-Aside:** {bid['set_aside']}  
**RFP Number:** {bid['rfp_number']}

---

"""

markdown += f"""

---

## 📊 SUMMARY

**Total Active Bids:** {len(active_bids)}  
**Urgent (0-7 days):** {len(urgent)}  
**Upcoming (8-14 days):** {len(upcoming)}  
**Future (15+ days):** {len(future)}  
**Ongoing (No deadline):** {len(no_deadline)}

---

*This is your ACTIVE WORKLOAD - bids you're actually pursuing or have submitted.*
"""

# Write to file
with open('/Users/deedavis/NEXUS BACKEND/ACTIVE_BIDS_ONLY.md', 'w') as f:
    f.write(markdown)

print("\n✅ Created: ACTIVE_BIDS_ONLY.md")
