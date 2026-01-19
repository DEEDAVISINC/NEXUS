#!/usr/bin/env python3
"""
Delete incomplete opportunities and re-import with FULL data
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

api = Api(API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

print("=" * 70)
print("RE-IMPORTING OPPORTUNITIES WITH FULL DATA")
print("=" * 70)
print()

# Get all records
records = table.all()
print(f"Found {len(records)} existing opportunities")
print()

# Delete all existing (they're incomplete)
print("Deleting incomplete opportunities...")
for record in records:
    table.delete(record['id'])
    
print(f"✅ Deleted {len(records)} incomplete opportunities")
print()

print("=" * 70)
print("NOW RUN GOVCON MINING TO RE-IMPORT WITH FULL DATA")
print("=" * 70)
print()
print("Run this command:")
print('python3 -c "import requests; r = requests.post(\'http://localhost:8000/gpss/mining/search-govcon-api\', json={}, timeout=30); print(r.json())"')
