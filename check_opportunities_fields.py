#!/usr/bin/env python3
"""Check fields in GPSS OPPORTUNITIES table"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
table = api.table(base_id, 'GPSS OPPORTUNITIES')

# Get one record to see fields
records = table.all(max_records=1)

if records:
    print("Current fields in GPSS OPPORTUNITIES:")
    print("-" * 60)
    for field_name in records[0]['fields'].keys():
        print(f"  • {field_name}")
else:
    print("No records found in GPSS OPPORTUNITIES table")
