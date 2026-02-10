#!/usr/bin/env python3
"""Add 3 new Oakland County opportunities to NEXUS"""

import os
import requests

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/GPSS%20OPPORTUNITIES"
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

opportunities = [
    {
        "RFP NUMBER": "Oak-0000001099",
        "Name": "Truck Service Bodies and Snow Plows - Oakland County",
        "Deadline": "2026-02-17",
        "Source Status": "Active - Analyzing"
    },
    {
        "RFP NUMBER": "Oak-0000001081",
        "Name": "Flow Meter Equipment & Maintenance - Oakland County WRC",
        "Deadline": "2026-02-12",
        "Source Status": "Active - Analyzing"
    },
    {
        "RFP NUMBER": "Oak-0000001080",
        "Name": "Ice B Gone Magic Treated Salt - Oakland County",
        "Deadline": "2026-02-12",
        "Source Status": "Active - Analyzing"
    }
]

print("🔍 Adding 3 NEW Oakland County Opportunities to NEXUS...")
print("=" * 60)

added_count = 0
for opp in opportunities:
    try:
        response = requests.post(
            AIRTABLE_URL,
            headers=headers,
            json={"fields": opp}
        )
        
        if response.status_code == 200:
            added_count += 1
            print(f"✅ Added: {opp['RFP NUMBER']}")
            print(f"   Title: {opp['Name']}")
            print(f"   Deadline: {opp['Deadline']}")
            print()
        else:
            print(f"❌ Failed: {opp['RFP NUMBER']}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {opp['RFP NUMBER']}: {e}")

print("=" * 60)
print(f"✅ Successfully added {added_count}/3 opportunities to NEXUS!")
print("\n📋 Next Steps:")
print("1. Download solicitations from BidNet Direct")
print("2. Create folders for each opportunity")
print("3. Analyze GO/NO-GO")
print("4. Source suppliers and price")
