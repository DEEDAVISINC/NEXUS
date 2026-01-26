#!/usr/bin/env python3
"""
MOVE PRODUCT SUPPLIERS FROM SUBCONTRACTORS TO SUPPLIERS
These companies sell products (not services), so they should be suppliers
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
suppliers_table = api.table(base_id, 'GPSS SUPPLIERS')

print("🚚 MOVING PRODUCT SUPPLIERS FROM SUBCONTRACTORS TO SUPPLIERS")
print("=" * 70)

# Companies selling products (not services)
companies_to_move = [
    'Detroit Salt Company',
    'Fisher Sand & Gravel', 
    'Fastenal',
    'Sunbelt Mill Supply'
]

for company_name in companies_to_move:
    print(f"\n📦 Processing: {company_name}")
    
    # Find in subcontractors
    subcontractor_records = subcontractors_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
    
    if not subcontractor_records:
        print(f"   ⚠️  Not found in SUBCONTRACTORS table")
        continue
    
    for record in subcontractor_records:
        sub_fields = record['fields']
        print(f"   ✓ Found in SUBCONTRACTORS: {record['id']}")
        
        # Check if already exists in suppliers
        existing = suppliers_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
        
        if existing:
            print(f"   ℹ️  Already exists in SUPPLIERS - skipping")
            continue
        
        # Create new supplier record - only use safe fields
        supplier_fields = {
            'COMPANY NAME': company_name,
            'PRODUCT KEYWORDS': f"{sub_fields.get('SERVICE TYPE', '')} - {sub_fields.get('DESCRIPTION', '')}"
        }
        
        # Add discovery date if available
        if sub_fields.get('DISCOVERY DATE'):
            supplier_fields['DISCOVERY DATE'] = sub_fields['DISCOVERY DATE']
        
        # Add rating if it's a valid number 0-5
        rating = sub_fields.get('RELIABILITY RATING', 0)
        if rating and isinstance(rating, (int, float)) and 0 <= rating <= 5:
            supplier_fields['OVERALL RATING'] = int(rating)
        
        # Add contact info if available
        if sub_fields.get('PRIMARY CONTACT EMAIL'):
            supplier_fields['PRIMARY CONTACT EMAIL'] = sub_fields['PRIMARY CONTACT EMAIL']
        if sub_fields.get('PRIMARY CONTACT PHONE'):
            supplier_fields['PRIMARY CONTACT PHONE'] = sub_fields['PRIMARY CONTACT PHONE']
        if sub_fields.get('WEBSITE'):
            supplier_fields['WEBSITE'] = sub_fields['WEBSITE']
        
        try:
            new_record = suppliers_table.create(supplier_fields)
            print(f"   ✅ Created in SUPPLIERS: {new_record['id']}")
            
            # Delete from subcontractors
            subcontractors_table.delete(record['id'])
            print(f"   🗑️  Removed from SUBCONTRACTORS")
            print(f"   ✨ {company_name} is now correctly categorized as a SUPPLIER!")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ MIGRATION COMPLETE")
print("\n💡 These companies now correctly categorized as SUPPLIERS:")
print("   (They sell products to resell, not services to perform)")
print("\n   Product Suppliers:")
print("   • Detroit Salt Company - Road salt / de-icing products")
print("   • Fisher Sand & Gravel - Aggregate materials (sand, gravel, limestone)")
print("   • Fastenal - Industrial supplies, MRO products")
print("   • Sunbelt Mill Supply - Industrial wipers, shop towels")
