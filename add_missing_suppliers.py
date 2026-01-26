#!/usr/bin/env python3
"""
ADD MISSING SUPPLIERS
Companies user has reached out to that aren't in the system yet
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

suppliers_table = api.table(base_id, 'GPSS SUPPLIERS')

print("📦 ADDING MISSING SUPPLIERS")
print("=" * 70)

# Suppliers to add
missing_suppliers = [
    {
        'COMPANY NAME': 'Compass Minerals',
        'WEBSITE': 'https://www.compassminerals.com',
        'PRIMARY CONTACT PHONE': '913-344-9200',
        'PRODUCT KEYWORDS': 'Road salt, de-icing products, sodium chloride, bulk salt delivery. Major supplier with Michigan operations. For Jackson County RFB #188.',
        'DISCOVERY DATE': '2026-01-22'
    }
]

for supplier in missing_suppliers:
    company_name = supplier['COMPANY NAME']
    
    # Check if already exists
    existing = suppliers_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
    
    if existing:
        print(f"\n⏭️  {company_name} - Already exists")
        continue
    
    try:
        record = suppliers_table.create(supplier)
        print(f"\n✅ ADDED: {company_name}")
        print(f"   ID: {record['id']}")
        print(f"   Product: {supplier.get('PRODUCT KEYWORDS', '')[:60]}...")
    except Exception as e:
        print(f"\n❌ ERROR adding {company_name}: {e}")

print("\n" + "=" * 70)
print("✅ COMPLETE")
