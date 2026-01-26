#!/usr/bin/env python3
"""
Check what fields exist for the suppliers we just added
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
table = api.table(os.getenv('AIRTABLE_BASE_ID'), 'GPSS SUPPLIERS')

print("Checking fields in GPSS SUPPLIERS...")
records = table.all(max_records=5)

if records:
    print(f"\nFound {len(records)} records")
    print("\nFields in first record:")
    for field_name in records[0]['fields'].keys():
        print(f"  • {field_name}")
    
    print("\nIs WEBSITE field available?")
    if 'WEBSITE' in records[0]['fields'].keys():
        print("  ✅ YES - WEBSITE field exists!")
    else:
        print("  ❌ NO - WEBSITE field does not exist")
        print("  We should add it!")
