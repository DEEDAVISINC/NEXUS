#!/usr/bin/env python3
"""
Check what fields actually exist in GPSS SUPPLIERS table
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
SUPPLIERS_TABLE = 'GPSS SUPPLIERS'

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, SUPPLIERS_TABLE)

print("=" * 80)
print("🔍 CHECKING GPSS SUPPLIERS TABLE FIELDS")
print("=" * 80)
print()

try:
    # Get one record to see fields
    records = table.all(max_records=1)
    
    if records:
        print(f"✅ Table exists with {len(records)} record(s)")
        print()
        print("📋 AVAILABLE FIELDS:")
        print("-" * 80)
        
        fields = records[0].get('fields', {})
        for field_name in sorted(fields.keys()):
            field_value = fields[field_name]
            field_type = type(field_value).__name__
            print(f"  • {field_name} ({field_type})")
        
        print()
        print("=" * 80)
    else:
        print("⚠️  Table exists but is empty (no records)")
        print()
        print("Creating a test supplier to see what fields are accepted...")
        
        # Try with minimal fields
        test_supplier = {
            "COMPANY NAME": "Test Supplier (DELETE ME)",
            "WEBSITE": "https://example.com"
        }
        
        try:
            record = table.create(test_supplier)
            print("✅ Test record created successfully!")
            print()
            print("📋 ACCEPTED FIELDS:")
            print("-" * 80)
            for field in test_supplier.keys():
                print(f"  • {field}")
            
            # Delete test record
            table.delete(record['id'])
            print()
            print("🗑️  Test record deleted")
            
        except Exception as e:
            print(f"❌ Error creating test record: {e}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("The GPSS SUPPLIERS table may not exist yet in your Airtable base.")
    print("Please create it first using the GPSS_VENDOR_MANAGEMENT_SCHEMA.md guide.")

print()
