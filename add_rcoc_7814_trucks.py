#!/usr/bin/env python3
"""
Add RCOC 7814 Pickup Trucks opportunity to NEXUS
Major opportunity - $640K-800K value
"""

import os
from pyairtable import Api
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Airtable setup
api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
table = api.table(base_id, 'GPSS OPPORTUNITIES')

# RCOC 7814 Pickup Trucks Opportunity
# GPSS OPPORTUNITIES table only has 4 writable fields: Name, Source Status, Deadline, RFP NUMBER
# HIGH VALUE FLAG is computed field, don't set it
opportunity = {
    'Name': 'RCOC IFB 7814 - Pickup Trucks Fleet (16 Units) - $640K-800K - EDWOSB Prime Contractor Opportunity',
    'Source Status': 'BidNet Direct / MITN - Active Quoting - National Auto Fleet Group (855-289-6572) PRIMARY - Monroe Truck (800-356-8134) BACKUP - Quote by Feb 10 - Bid 11-12% markup - Est profit $77K-90K',
    'Deadline': '2026-02-17',  # Feb 17, 2026
    'RFP NUMBER': 'IFB 7814'
}

print("Adding RCOC 7814 Pickup Trucks to NEXUS...")
print(f"Opportunity: {opportunity['Name']}")
print(f"Due: {opportunity['Deadline']}")
print(f"RFP Number: {opportunity['RFP NUMBER']}")

try:
    record = table.create(opportunity)
    print(f"\n✅ SUCCESS! Added to NEXUS")
    print(f"Record ID: {record['id']}")
    print(f"\nView in Airtable: https://airtable.com/{base_id}/")
    print(f"\nNext steps:")
    print(f"1. Call National Auto Fleet Group (855-289-6572)")
    print(f"2. Request quotes by Feb 10")
    print(f"3. Calculate 11-12% markup")
    print(f"4. Submit bid by Feb 17 @ 2:30 PM")
    print(f"\nEstimated profit: $77,000-90,000")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Checking available fields...")
    # Try to get schema
    try:
        all_records = table.all(max_records=1)
        if all_records:
            print(f"Available fields: {list(all_records[0]['fields'].keys())}")
    except:
        pass
