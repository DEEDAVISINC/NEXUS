#!/usr/bin/env python3
"""
Check what fields exist in GPSS OPPORTUNITIES table
So we can build proper status tracking
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
TABLE_NAME = 'GPSS OPPORTUNITIES'

def check_schema():
    """Get first few records and show all fields"""
    
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'maxRecords': 5,
        'view': 'Grid view'
    }
    
    print("🔍 Checking GPSS OPPORTUNITIES schema...\n")
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        
        if records:
            print(f"✅ Found {len(records)} sample records\n")
            print("=" * 80)
            print("AVAILABLE FIELDS IN GPSS OPPORTUNITIES:")
            print("=" * 80)
            
            # Get all unique field names
            all_fields = set()
            for record in records:
                fields = record.get('fields', {})
                all_fields.update(fields.keys())
            
            for field in sorted(all_fields):
                print(f"  - {field}")
            
            print("\n" + "=" * 80)
            print("SAMPLE RECORD:")
            print("=" * 80)
            
            sample = records[0]['fields']
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
            
            # Check for status-related fields
            print("\n" + "=" * 80)
            print("STATUS TRACKING FIELDS:")
            print("=" * 80)
            
            status_fields = [f for f in all_fields if any(x in f.lower() for x in ['status', 'stage', 'phase', 'quote', 'submit', 'deadline', 'due'])]
            
            if status_fields:
                print("\n✅ Found these status-related fields:")
                for field in status_fields:
                    print(f"  - {field}")
            else:
                print("\n⚠️ NO status tracking fields found!")
                print("   We need to add: Status, Quote_Status, Submission_Status, etc.")
        else:
            print("❌ No records found")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_schema()
