#!/usr/bin/env python3
"""Check actual field names in GPSS OPPORTUNITIES"""

import os
import requests

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/GPSS%20OPPORTUNITIES"
headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

response = requests.get(f"{AIRTABLE_URL}?maxRecords=1", headers=headers)
if response.status_code == 200:
    data = response.json()
    if data.get('records'):
        fields = data['records'][0]['fields']
        print("Available fields in GPSS OPPORTUNITIES:")
        for field in sorted(fields.keys()):
            print(f"  - {field}")
