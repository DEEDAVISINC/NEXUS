#!/usr/bin/env python3
"""
Fix RCOC Bid Deadlines in Airtable
Add proper Response Deadline dates so NEXUS shows urgent alerts
"""

from pyairtable import Api
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Airtable
api = Api(os.getenv('AIRTABLE_API_KEY'))
base = api.base(os.getenv('AIRTABLE_BASE_ID'))
table = base.table('GPSS OPPORTUNITIES')

# RCOC bid deadlines (from your tracker documents)
# Format: YYYY-MM-DD (Airtable date field format)
RCOC_DEADLINES = {
    'RCOC 7798': '2026-02-04',  # Wiper Blades - Feb 4 @ 10am
    'RCOC 7732': '2026-02-10',  # Paper Products - Feb 10 @ 2:30pm
    'RCOC 7842': '2026-02-17',  # Safety Supplies - Feb 17 @ 2:30pm
    # Already passed:
    'RCOC 7731': '2026-02-02',  # Industrial Wipers - SUBMITTED
    'RCOC 7777': '2026-02-02',  # Welding Supplies - SUBMITTED
    'RCOC 7734': '2026-02-02',  # Forestry - MISSED
    # Need confirmation (estimated from portfolio docs):
    'RCOC 7797': '2026-02-04',  # Small Auto Tools
    'RCOC 7799': '2026-02-06',  # Grease & Air Couplers
    'RCOC 7802': '2026-02-06',  # Building Tools
    'RCOC 7803': '2026-02-06',  # Hammers, Tape, Levels
}

def main():
    print("🔧 Fixing RCOC bid deadlines in Airtable...\n")
    
    # Get all RCOC bids
    records = table.all()
    rcoc_bids = [r for r in records if 'RCOC' in r['fields'].get('Name', '')]
    
    print(f"Found {len(rcoc_bids)} RCOC bids\n")
    
    updated_count = 0
    
    for record in rcoc_bids:
        name = record['fields'].get('Name', '')
        
        # Find matching deadline
        deadline = None
        for key, value in RCOC_DEADLINES.items():
            if key in name:
                deadline = value
                break
        
        if deadline:
            try:
                # Update the record
                table.update(record['id'], {
                    'Deadline': deadline
                })
                
                # Calculate days until deadline
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                now = datetime.now()
                days = (deadline_date - now).days
                
                if days < 0:
                    status = "❌ PASSED"
                elif days <= 2:
                    status = "🔴 URGENT"
                elif days <= 7:
                    status = "🟡 THIS WEEK"
                else:
                    status = "🟢 UPCOMING"
                
                print(f"{status} {name}")
                print(f"   Set deadline: {deadline_date.strftime('%b %d, %Y')}")
                print(f"   Days remaining: {days}")
                print()
                
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Error updating {name}: {e}\n")
        else:
            print(f"⚠️  No deadline found for: {name}\n")
    
    print(f"\n✅ Updated {updated_count} RCOC bids with deadlines!")
    print("\n🎯 NEXUS will now show urgent alerts for these bids!")

if __name__ == '__main__':
    main()
