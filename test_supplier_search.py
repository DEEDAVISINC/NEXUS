#!/usr/bin/env python3
"""
TEST SUPPLIER SEARCH
Test the actual search function that the API uses
"""

import sys
sys.path.insert(0, '/Users/deedavis/NEXUS BACKEND')

from nexus_backend import handle_search_suppliers

print("🧪 TESTING SUPPLIER SEARCH FUNCTION")
print("=" * 70)

# Test with no filters (should return all non-blocked suppliers)
print("\n📊 Testing search with no filters...")
filters = {
    'category': None,
    'keywords': [],
    'min_rating': 0
}

suppliers = handle_search_suppliers(filters)

print(f"\n✅ Found {len(suppliers)} suppliers\n")

if len(suppliers) == 0:
    print("❌ NO SUPPLIERS RETURNED")
    print("   This is why the frontend shows 'No suppliers found'")
else:
    print("✅ SUPPLIERS BEING RETURNED:")
    for i, supplier in enumerate(suppliers[:5], 1):
        print(f"\n   {i}. {supplier.get('company_name', 'NO NAME')}")
        print(f"      ID: {supplier.get('id')}")
        print(f"      Status: {supplier.get('business_status', 'Empty')}")
        print(f"      Rating: {supplier.get('overall_rating', 0)}/5")
        print(f"      Net 30: {supplier.get('net_30_available', False)}")

print("\n" + "=" * 70)
