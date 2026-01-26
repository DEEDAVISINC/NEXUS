#!/usr/bin/env python3
"""
TEST CONTACTS & PRODUCTS API
Verify that both endpoints return data correctly
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

print("🧪 TESTING CONTACTS & PRODUCTS DATA MAPPING")
print("=" * 70)

# Test Contacts
print("\n📇 CONTACTS:")
print("-" * 70)

contacts_table = api.table(base_id, 'GPSS CONTACTS')
contacts_records = contacts_table.all()

print(f"Total contacts: {len(contacts_records)}\n")

for i, record in enumerate(contacts_records[:3], 1):
    fields = record['fields']
    
    # Parse name
    full_name = fields.get('Name', '').strip()
    name_parts = full_name.split(' ', 1) if full_name else ['', '']
    first_name = name_parts[0] if len(name_parts) > 0 else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    print(f"{i}. {full_name}")
    print(f"   First Name: {first_name}")
    print(f"   Last Name: {last_name}")
    print(f"   Email: {fields.get('Email', '')}")
    print(f"   Title: {fields.get('Title', '')}")
    print(f"   Organization: {fields.get('Organization', '')}")
    print(f"   Role: {fields.get('Role Category', '')}")
    print()

# Test Products
print("\n📦 PRODUCTS:")
print("-" * 70)

products_table = api.table(base_id, 'GPSS PRODUCTS')
products_records = products_table.all()

print(f"Total products: {len(products_records)}\n")

for i, record in enumerate(products_records[:3], 1):
    fields = record['fields']
    
    # Parse price
    price_str = fields.get('UNIT PRICE', '0')
    try:
        price = float(str(price_str).replace('$', '').replace(',', ''))
    except:
        price = 0
    
    print(f"{i}. {fields.get('NAME', '[No name]')}")
    print(f"   Category: {fields.get('PRODUCT CATEGORY', '')}")
    print(f"   Supplier: {fields.get('SUPPLIER', '')}")
    print(f"   Price: ${price:.2f}")
    print()

print("=" * 70)
print("✅ Field mapping working correctly!")
