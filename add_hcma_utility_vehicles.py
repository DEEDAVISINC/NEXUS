#!/usr/bin/env python3
"""
Add HCMA Utility Vehicles opportunity to Airtable
ITB 2026-007 - Cushman utility vehicles for Michigan Metroparks
"""

import os
from pyairtable import Api
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# HCMA Utility Vehicles opportunity - using only writable Airtable fields
opportunity = {
    'Name': 'HCMA Utility Vehicles - ITB 2026-007 ($150K) - Patty Barthelmes (810) 644-6062',
    'RFP NUMBER': 'ITB 2026-007',
    'Deadline': '2026-02-25',
    'Source Status': 'Active'
}

print("Adding HCMA Utility Vehicles to Airtable...")
record = table.create(opportunity)
print(f"✅ Added successfully! Record ID: {record['id']}")
print(f"✅ Opportunity: {record['fields']['Name']}")
print(f"✅ Deadline: {record['fields']['Deadline']}")
print(f"✅ RFP#: {record['fields']['RFP NUMBER']}")
print(f"✅ Status: {record['fields']['Source Status']}")
print("\n🎯 Next: Open NEXUS frontend and generate RFQ from this opportunity!")
