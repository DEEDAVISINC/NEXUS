#!/usr/bin/env python3
"""
EXPORT ALL ACTIVE OPPORTUNITIES TO MARKDOWN
Complete list of all opportunities with future deadlines

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

print("Fetching all opportunities from Airtable...")
all_records = table.all()
print(f"✅ Fetched {len(all_records)} total records")
print()

# Filter to ACTIVE opportunities only (deadline in future)
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

# Sort by deadline
active.sort(key=lambda x: x[2])

print(f"✅ Found {len(active)} active opportunities (next 90 days)")
print()
print("Creating markdown file...")

# Write to file
with open('ALL_OPPORTUNITIES_COMPLETE_LIST.md', 'w') as f:
    f.write('# 📋 ALL ACTIVE OPPORTUNITIES - COMPLETE LIST\n\n')
    f.write(f'**Generated:** {datetime.now().strftime("%B %d, %Y %I:%M %p")}\n')
    f.write(f'**Total Active Opportunities:** {len(active)}\n')
    f.write(f'**Timeframe:** Next 90 days\n\n')
    f.write('---\n\n')
    
    for i, (r, days_until, due_date) in enumerate(active, 1):
        fields = r['fields']
        name = fields.get('Name', 'Untitled')
        deadline = fields.get('Deadline', 'Unknown')
        status = fields.get('Status', 'New')
        value = fields.get('Estimated Value', 0)
        set_aside = fields.get('Set-Aside Type', 'None')
        rfp_num = fields.get('RFP NUMBER', '')
        agency = fields.get('Agency Name', 'Unknown')
        
        f.write(f'## {i}. {name}\n\n')
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
        f.write('\n---\n\n')

print('✅ COMPLETE!')
print()
print(f'📄 File created: ALL_OPPORTUNITIES_COMPLETE_LIST.md')
print(f'📊 {len(active)} opportunities listed')
print()
