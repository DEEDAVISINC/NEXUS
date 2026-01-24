"""
Check the ACTUAL field names in GPSS SUBCONTRACTORS (with exact capitalization)
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

# First check if there's a record with data
subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("🔍 CHECKING ACTUAL FIELD NAMES IN GPSS SUBCONTRACTORS\n")

# Get the table schema by fetching the base schema
try:
    from pyairtable.api.base import Base
    base = Base(api, base_id)
    schema = base.schema()
    
    # Find GPSS SUBCONTRACTORS table in schema
    for table in schema.tables:
        if table.name == 'GPSS SUBCONTRACTORS':
            print(f"✅ Found table: {table.name}\n")
            print("ALL FIELDS IN TABLE (exact spelling):")
            for field in table.fields:
                print(f"  - '{field.name}' ({field.type})")
            break
except Exception as e:
    print(f"Could not get schema: {e}")
    print("\nTrying alternative method - fetching records...\n")
    
    # Alternative: get from existing record with most fields populated
    all_records = subs_table.all()
    if all_records:
        # Get the record with the most fields
        record_with_most_fields = max(all_records, key=lambda r: len(r['fields']))
        
        print("ALL FIELDS FROM EXISTING RECORDS:")
        for field_name in sorted(record_with_most_fields['fields'].keys()):
            value = record_with_most_fields['fields'][field_name]
            print(f"  - '{field_name}' = {value}")
