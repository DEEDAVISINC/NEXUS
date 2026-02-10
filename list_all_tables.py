#!/usr/bin/env python3
"""List all tables in Airtable to see what exists"""
import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
base = api.base(os.getenv('AIRTABLE_BASE_ID'))
schema = base.schema()

print("ALL TABLES IN NEXUS BASE:")
print("=" * 60)
for table in schema.tables:
    print(f"  - {table.name}")
    if 'SUPPLIER' in table.name.upper() and 'RFP' in table.name.upper():
        print(f"    ✅ FOUND SUPPLIER RFP TABLE!")
        print(f"    Fields: {len(table.fields)}")
