#!/usr/bin/env python3
"""
Add 8 Liquid Chlorine Suppliers to GPSS SUPPLIERS
For HCMA ITB #2026-004
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
suppliers_table = api.table(AIRTABLE_BASE_ID, 'GPSS SUPPLIERS')

# 8 Liquid Chlorine Suppliers
chlorine_suppliers = [
    {
        "COMPANY NAME": "Elite Chlorine",
        "PRIMARY CONTACT EMAIL": "info@elitechlorine.com",
        "PRIMARY CONTACT PHONE": "Contact via website"
    },
    {
        "COMPANY NAME": "Chemtrade Logistics - River Rouge",
        "PRIMARY CONTACT EMAIL": "sales@chemtradelogistics.com",
        "PRIMARY CONTACT PHONE": "(866) 416-4404"
    },
    {
        "COMPANY NAME": "Brenntag North America - Grand Rapids",
        "PRIMARY CONTACT EMAIL": "Check website or call",
        "PRIMARY CONTACT PHONE": "(616) 656-9555"
    },
    {
        "COMPANY NAME": "Horizon Commercial Pool Supply",
        "PRIMARY CONTACT EMAIL": "Check website",
        "PRIMARY CONTACT PHONE": "Check website"
    },
    {
        "COMPANY NAME": "Hawkins Water Treatment Group",
        "PRIMARY CONTACT EMAIL": "Check website",
        "PRIMARY CONTACT PHONE": "Check website for MI location"
    },
    {
        "COMPANY NAME": "Univar Solutions",
        "PRIMARY CONTACT EMAIL": "SDSNA@univarsolutions.com",
        "PRIMARY CONTACT PHONE": "1-800-531-7106"
    },
    {
        "COMPANY NAME": "BulkChlorine.com",
        "PRIMARY CONTACT EMAIL": "Check website",
        "PRIMARY CONTACT PHONE": "Check website"
    },
    {
        "COMPANY NAME": "Waterline Technologies",
        "PRIMARY CONTACT EMAIL": "Check website",
        "PRIMARY CONTACT PHONE": "1-800-464-7762"
    }
]

print("=" * 80)
print("🧪 ADDING LIQUID CHLORINE SUPPLIERS TO GPSS SUPPLIERS TABLE")
print("=" * 80)
print()

try:
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, supplier in enumerate(chlorine_suppliers, 1):
        company_name = supplier.get("COMPANY NAME")
        print(f"{i}. Processing: {company_name}")
        
        try:
            # Check if supplier already exists
            existing = suppliers_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
            
            if existing:
                print(f"   ⏭️  Already exists - Skipping")
                skipped_count += 1
                continue
            
            # Add supplier to table
            record = suppliers_table.create(supplier)
            print(f"   ✅ Added successfully!")
            
            # Show what was added
            if i <= 3:  # Show details for first 3 (the ones you emailed today)
                print(f"      📧 Email: {supplier.get('PRIMARY CONTACT EMAIL')}")
                print(f"      📞 Phone: {supplier.get('PRIMARY CONTACT PHONE')}")
            
            added_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
    
    print()
    print("=" * 80)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successfully added: {added_count} suppliers")
    if skipped_count > 0:
        print(f"   ⏭️  Already existed: {skipped_count} suppliers")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    print("=" * 80)
    print()
    
    if added_count > 0:
        print("🎯 SUCCESS! Suppliers added to NEXUS GPSS SUPPLIERS table!")
        print()
        print("✅ QUOTE REQUESTS SENT TODAY:")
        print("   1. Elite Chlorine - info@elitechlorine.com")
        print("   2. Chemtrade Logistics - sales@chemtradelogistics.com")
        print("   3. Brenntag (pending)")
        print()
        print("📅 FOLLOW-UP:")
        print("   - Check for responses in 2-3 days")
        print("   - Follow up if no response by January 26")
        print("   - Send to remaining 5 suppliers tomorrow")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Send 3rd email today (Brenntag)")
        print("   2. Send 3 more emails tomorrow")
        print("   3. Track quotes in HCMA_CHLORINE_SUPPLIER_QUOTES.md")
        print()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Possible issues:")
    print("   - GPSS SUPPLIERS table name incorrect")
    print("   - Field names don't match exactly")
    print("   - Airtable API credentials issue")

print()
