#!/usr/bin/env python3
"""
EXPORT ALL OPPORTUNITIES - SORTED BY DUE DATE
Every single opportunity in strict chronological order
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

print("Fetching all opportunities from Airtable...")
all_records = table.all()
print(f"✅ Fetched {len(all_records)} total records")
print()

# Filter to opportunities with deadlines in next 90 days
active = []
for r in all_records:
    fields = r['fields']
    deadline = fields.get('Deadline', '')
    status = fields.get('Status', 'New')
    
    # Skip if already decided not to pursue
    if status in ['Lost', 'Won', 'Not Pursuing']:
        continue
    
    if deadline:
        try:
            due_date = datetime.strptime(deadline, '%Y-%m-%d')
            days_until = (due_date - datetime.now()).days
            if days_until >= 0 and days_until <= 90:
                active.append((r, days_until, due_date))
        except:
            pass

# Sort by due date (strict chronological order)
active.sort(key=lambda x: x[2])

print(f"✅ Found {len(active)} active opportunities (next 90 days)")
print()
print("Creating chronological list...")

# Write to file
with open('ALL_OPPORTUNITIES_BY_DATE.md', 'w') as f:
    f.write('# 📋 ALL ACTIVE OPPORTUNITIES - SORTED BY DUE DATE\n\n')
    f.write(f'**Generated:** {datetime.now().strftime("%B %d, %Y %I:%M %p")}\n')
    f.write(f'**Total Active Opportunities:** {len(active)}\n')
    f.write(f'**Sorted By:** Deadline (earliest first)\n\n')
    f.write('---\n\n')
    
    current_date = None
    
    for i, (r, days_until, due_date) in enumerate(active, 1):
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        status = fields.get('Status', 'New')
        value = fields.get('Estimated Value', 0)
        set_aside = fields.get('Set-Aside Type', 'None')
        rfp_num = fields.get('RFP NUMBER', '')
        agency = fields.get('Agency Name', 'Unknown')
        
        # Add date header when date changes
        if deadline != current_date:
            current_date = deadline
            f.write(f'\n## 📅 DUE: {deadline} ({days_until} days)\n\n')
            f.write('---\n\n')
        
        f.write(f'### {i}. {name}\n\n')
        f.write(f'- **Deadline:** {deadline} (⏰ **{days_until} DAYS**)\n')
        f.write(f'- **Status:** {status}\n')
        if value:
            f.write(f'- **Value:** ${value:,.0f}\n')
        if set_aside and set_aside not in ['None', 'NONE', '']:
            f.write(f'- **Set-Aside:** {set_aside}\n')
        if rfp_num:
            f.write(f'- **RFP#:** {rfp_num}\n')
        if agency and agency != 'Unknown':
            f.write(f'- **Agency:** {agency}\n')
        f.write(f'- **Record ID:** {r["id"]}\n')
        f.write('\n')

print('✅ COMPLETE!')
print()
print(f'📄 File created: ALL_OPPORTUNITIES_BY_DATE.md')
print(f'📊 {len(active)} opportunities in strict chronological order')
print()
