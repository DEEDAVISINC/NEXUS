#!/usr/bin/env python3
"""
TEST SUPPLIER FILTER LOGIC
Directly test the filtering without importing nexus_backend
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
table = api.table(base_id, 'GPSS SUPPLIERS')

print("🧪 TESTING SUPPLIER FILTER LOGIC")
print("=" * 70)

# Get all suppliers
print("\n📊 Fetching all suppliers from Airtable...")
all_records = table.all()
print(f"   Total records in Airtable: {len(all_records)}")

# Apply the FIXED filter logic
print("\n🔍 Applying NEW filter (exclude only Inactive/Blocked/Rejected)...")
filtered = []

for supplier in all_records:
    fields = supplier.get('fields', {})
    
    # Filter out explicitly inactive suppliers only
    status = fields.get('BUSINESS STATUS', '')
    if status in ['Inactive', 'Blocked', 'Rejected']:
        print(f"   ❌ Skipping: {fields.get('COMPANY NAME', 'No name')} (Status: {status})")
        continue
    
    # Skip if no company name
    if not fields.get('COMPANY NAME'):
        print(f"   ⚠️  Skipping empty record (ID: {supplier.get('id')})")
        continue
    
    filtered.append({
        'id': supplier.get('id'),
        'company_name': fields.get('COMPANY NAME', ''),
        'status': fields.get('BUSINESS STATUS', 'Not Set'),
        'rating': fields.get('OVERALL RATING', 0),
        'net_30': fields.get('NET 30', False)
    })
    
    print(f"   ✅ Included: {fields.get('COMPANY NAME')} (Status: {status or 'Empty'})")

print(f"\n" + "=" * 70)
print(f"✅ RESULT: {len(filtered)} suppliers would be shown")
print("=" * 70)

if len(filtered) > 0:
    print("\n📋 Suppliers that WILL display:")
    for s in filtered:
        print(f"   • {s['company_name']}")
        print(f"     Status: {s['status']}, Rating: {s['rating']}, Net 30: {s['net_30']}")
else:
    print("\n❌ No suppliers would display!")
    print("   Problem: All suppliers are being filtered out")
