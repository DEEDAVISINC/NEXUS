"""
Check GPSS OPPORTUNITIES schema for buyer contact fields
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

print("🔍 CHECKING GPSS OPPORTUNITIES SCHEMA\n")

try:
    from pyairtable.api.base import Base
    base = Base(api, base_id)
    schema = base.schema()
    
    for table in schema.tables:
        if table.name == 'GPSS OPPORTUNITIES':
            print(f"✅ Table: {table.name}\n")
            print("ALL FIELDS:")
            for field in table.fields:
                print(f"  - '{field.name}' ({field.type})")
            break
except Exception as e:
    print(f"Error: {e}")
