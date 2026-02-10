#!/usr/bin/env python3
"""Check actual field names in GPSS OPPORTUNITIES"""
import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
base = api.base(os.getenv('AIRTABLE_BASE_ID'))
schema = base.schema()

opportunities_table = next((t for t in schema.tables if t.name == 'GPSS OPPORTUNITIES'), None)

if opportunities_table:
    print("All fields in GPSS OPPORTUNITIES:")
    print()
    for field in opportunities_table.fields:
        print(f"  - {field.name} ({field.type})")
        # Check if it's document-related
        if any(word in field.name.upper() for word in ['DOCUMENT', 'PACKAGE', 'ASSEMBLED']):
            print(f"    → DOCUMENT FIELD FOUND!")
