#!/usr/bin/env python3
"""
DIAGNOSE SUPPLIERS ISSUE ON PYTHONANYWHERE
"""

import os
import sys

print("=" * 70)
print("SUPPLIER DIAGNOSIS")
print("=" * 70)

# Test 1: Check environment variables
print("\n1️⃣  CHECKING ENVIRONMENT VARIABLES...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    airtable_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    
    if airtable_key:
        print(f"   ✓ AIRTABLE_API_KEY: {airtable_key[:10]}...")
    else:
        print("   ❌ AIRTABLE_API_KEY: NOT FOUND")
    
    if base_id:
        print(f"   ✓ AIRTABLE_BASE_ID: {base_id}")
    else:
        print("   ❌ AIRTABLE_BASE_ID: NOT FOUND")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check pyairtable connection
print("\n2️⃣  TESTING AIRTABLE CONNECTION...")
try:
    from pyairtable import Api
    api = Api(os.environ.get('AIRTABLE_API_KEY'))
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    table = api.table(base_id, 'GPSS SUPPLIERS')
    
    records = table.all()
    print(f"   ✓ Connected to Airtable")
    print(f"   ✓ Found {len(records)} total records")
    
    # Count records with company names
    with_names = [r for r in records if r['fields'].get('COMPANY NAME')]
    print(f"   ✓ {len(with_names)} records have company names")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Test the filter logic
print("\n3️⃣  TESTING FILTER LOGIC...")
try:
    filtered = []
    for supplier in records:
        fields = supplier.get('fields', {})
        
        # Filter out explicitly inactive suppliers only
        status = fields.get('BUSINESS STATUS', '')
        if status in ['Inactive', 'Blocked', 'Rejected']:
            continue
        
        # Skip if no company name
        if not fields.get('COMPANY NAME'):
            continue
        
        filtered.append({
            'id': supplier.get('id'),
            'company_name': fields.get('COMPANY NAME', ''),
            'website': fields.get('WEBSITE', ''),
            'business_status': fields.get('BUSINESS STATUS', ''),
        })
    
    print(f"   ✓ Filter logic works")
    print(f"   ✓ {len(filtered)} suppliers pass filter")
    
    if len(filtered) > 0:
        print(f"\n   📋 Filtered suppliers:")
        for s in filtered[:5]:
            print(f"      • {s['company_name']}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test the actual backend function
print("\n4️⃣  TESTING BACKEND FUNCTION...")
try:
    from nexus_backend import handle_search_suppliers
    
    filters = {
        'category': None,
        'keywords': [],
        'min_rating': 0
    }
    
    result = handle_search_suppliers(filters)
    print(f"   ✓ handle_search_suppliers() works")
    print(f"   ✓ Returned {len(result)} suppliers")
    
    if len(result) == 0:
        print(f"   ❌ PROBLEM: Function returns empty list!")
    else:
        print(f"\n   📋 Returned suppliers:")
        for s in result[:5]:
            print(f"      • {s.get('company_name', 'NO NAME')}")
    
except Exception as e:
    print(f"   ❌ Error calling backend function: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ DIAGNOSIS COMPLETE")
print("=" * 70)
