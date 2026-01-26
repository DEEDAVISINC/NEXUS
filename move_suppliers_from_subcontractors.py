#!/usr/bin/env python3
"""
MOVE GRAINGER AND MOPEC FROM SUBCONTRACTORS TO SUPPLIERS
They are wholesalers (suppliers), not service providers (subcontractors)
"""

import os
from pyairtable import Api
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
suppliers_table = api.table(base_id, 'GPSS SUPPLIERS')

print("🚚 MOVING SUPPLIERS FROM SUBCONTRACTORS TABLE")
print("=" * 70)

# Companies to move
companies_to_move = ['Grainger', 'Mopec']

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
            print(f"   ℹ️  Already exists in SUPPLIERS - updating instead")
            supplier_id = existing[0]['id']
            
            # Update with additional info from subcontractor record - use only safe fields
            update_fields = {
                'PRODUCT KEYWORDS': sub_fields.get('DESCRIPTION', ''),
                'OVERALL RATING': sub_fields.get('RELIABILITY RATING', 0)
            }
            
            # Add discovery date if available
            if sub_fields.get('DISCOVERY DATE'):
                update_fields['DISCOVERY DATE'] = sub_fields['DISCOVERY DATE']
            
            suppliers_table.update(supplier_id, update_fields)
            print(f"   ✅ Updated in SUPPLIERS: {supplier_id}")
        
        else:
            # Create new supplier record - use only safe fields
            supplier_fields = {
                'COMPANY NAME': company_name,
                'PRODUCT KEYWORDS': sub_fields.get('DESCRIPTION', ''),
                'OVERALL RATING': sub_fields.get('RELIABILITY RATING', 0)
            }
            
            # Add discovery date if available
            if sub_fields.get('DISCOVERY DATE'):
                supplier_fields['DISCOVERY DATE'] = sub_fields['DISCOVERY DATE']
            
            # Add contact info if available
            if sub_fields.get('PRIMARY CONTACT EMAIL'):
                supplier_fields['PRIMARY CONTACT EMAIL'] = sub_fields['PRIMARY CONTACT EMAIL']
            if sub_fields.get('PRIMARY CONTACT PHONE'):
                supplier_fields['PRIMARY CONTACT PHONE'] = sub_fields['PRIMARY CONTACT PHONE']
            if sub_fields.get('WEBSITE'):
                supplier_fields['WEBSITE'] = sub_fields['WEBSITE']
            
            new_record = suppliers_table.create(supplier_fields)
            print(f"   ✅ Created in SUPPLIERS: {new_record['id']}")
        
        # Delete from subcontractors
        subcontractors_table.delete(record['id'])
        print(f"   🗑️  Removed from SUBCONTRACTORS")
        
        print(f"   ✨ {company_name} is now a SUPPLIER!")

print("\n" + "=" * 70)
print("✅ MIGRATION COMPLETE")
print("\n💡 These companies are now properly categorized as SUPPLIERS")
print("   (wholesalers you purchase from to resell)")
