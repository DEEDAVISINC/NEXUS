#!/usr/bin/env python3
"""
Check GPSS SUPPLIERS table for existing chemical suppliers
Part of standard RFP review process
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

print("=" * 80)
print("🔍 SEARCHING EXISTING SUPPLIERS FOR CHEMICAL CAPABILITIES")
print("=" * 80)
print()

# Keywords to search for
chemical_keywords = [
    'chemical', 'chlorine', 'sodium', 'hypochlorite',
    'pool', 'aquatic', 'water treatment', 'industrial chemical',
    'chemical distribution', 'chemical supply'
]

try:
    # Get all suppliers
    all_suppliers = suppliers_table.all()
    print(f"📊 Total suppliers in database: {len(all_suppliers)}")
    print()
    
    # Search for chemical-related suppliers
    matches = []
    
    for record in all_suppliers:
        fields = record.get('fields', {})
        company_name = fields.get('COMPANY NAME', '').lower()
        website = fields.get('WEBSITE', '').lower()
        categories = fields.get('CATEGORIES', '').lower()
        products = fields.get('PRODUCTS', '').lower()
        description = fields.get('DESCRIPTION', '').lower()
        
        # Search all text fields
        searchable_text = f"{company_name} {website} {categories} {products} {description}"
        
        # Check for keyword matches
        found_keywords = [kw for kw in chemical_keywords if kw in searchable_text]
        
        if found_keywords:
            matches.append({
                'record': record,
                'keywords': found_keywords
            })
    
    # Display results
    if matches:
        print(f"✅ FOUND {len(matches)} POTENTIAL CHEMICAL SUPPLIER(S)")
        print("=" * 80)
        
        for i, match in enumerate(matches, 1):
            fields = match['record'].get('fields', {})
            print(f"\n{i}. {fields.get('COMPANY NAME', 'Unknown')}")
            print(f"   Website: {fields.get('WEBSITE', 'N/A')}")
            print(f"   Categories: {fields.get('CATEGORIES', 'N/A')}")
            print(f"   Products: {fields.get('PRODUCTS', 'N/A')[:100]}...")
            print(f"   Matched Keywords: {', '.join(match['keywords'])}")
            
            # Contact info if available
            if fields.get('PHONE'):
                print(f"   📞 Phone: {fields.get('PHONE')}")
            if fields.get('EMAIL'):
                print(f"   📧 Email: {fields.get('EMAIL')}")
    else:
        print("❌ NO CHEMICAL SUPPLIERS FOUND IN DATABASE")
        print()
        print("📋 RECOMMENDATION:")
        print("   Need to research and add new liquid chlorine suppliers to system")
        print()
        print("   Suggested suppliers to research:")
        print("   • Univar Solutions")
        print("   • Brenntag North America")
        print("   • Hawkins Water Treatment Group")
        print("   • Chemtrade Chemicals")
        print("   • Jones-Hamilton Co.")
        print("   • Local Michigan pool/chemical suppliers")
    
    print()
    print("=" * 80)
    print("📝 NEXT STEPS:")
    print("   1. Contact any existing suppliers found above")
    print("   2. Research additional suppliers from bid strategy document")
    print("   3. Get quotes from 5-7 suppliers minimum")
    print("   4. Add new suppliers to GPSS SUPPLIERS table")
    print("=" * 80)
    print()

except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("The GPSS SUPPLIERS table may not exist or may have different field names.")
    print("Check the table structure in Airtable.")
