#!/usr/bin/env python3
"""Show the newly added EDWOSB/WOSB opportunity"""

from pyairtable import Api
from dotenv import load_dotenv
import os

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# Get all opportunities
all_opps = table.all()

print("=" * 80)
print("🆕 NEWLY AUTO-MINED EDWOSB/WOSB OPPORTUNITIES")
print("=" * 80)
print()

count = 0
for r in all_opps:
    fields = r['fields']
    notes = fields.get('Notes', '')
    
    # Check if it was auto-mined today
    if 'Auto-Mined 2026-02' in notes:
        count += 1
        name = fields.get('Name', 'Untitled')
        set_aside = fields.get('Set-Aside Type', 'Unknown')
        agency = fields.get('AGENCY NAME', 'Unknown')
        deadline = fields.get('Deadline', 'Unknown')
        url = fields.get('Source URL', 'No URL')
        rfp = fields.get('RFP NUMBER', 'N/A')
        
        print(f"✅ OPPORTUNITY #{count}:")
        print(f"   Title: {name}")
        print(f"   Agency: {agency}")
        print(f"   Set-Aside: {set_aside}")
        print(f"   Deadline: {deadline}")
        print(f"   RFP/Notice ID: {rfp[:50]}")
        print(f"   SAM.gov URL: {url}")
        print()
        
        # Show description from notes
        desc_start = notes.find('\n\n') + 2 if '\n\n' in notes else 0
        description = notes[desc_start:desc_start+300] if desc_start > 0 else notes[:300]
        print(f"   Description: {description}...")
        print()
        print("=" * 80)
        print()

if count == 0:
    print("❌ No auto-mined opportunities found from today")
    print("   This might mean the opportunity was a duplicate")
else:
    print(f"✅ TOTAL AUTO-MINED TODAY: {count}")
