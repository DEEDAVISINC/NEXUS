#!/usr/bin/env python3
"""
Update liquid chlorine suppliers with WEBSITE information
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
table = api.table(os.getenv('AIRTABLE_BASE_ID'), 'GPSS SUPPLIERS')

# Supplier websites to add
supplier_websites = {
    "Elite Chlorine": "https://elitechlorine.com/michigan",
    "Chemtrade Logistics - River Rouge": "https://www.chemtradelogistics.com",
    "Brenntag North America - Grand Rapids": "https://www.brenntag.com/en-us/",
    "Horizon Commercial Pool Supply": "https://www.horizonpoolsupply.com",
    "Hawkins Water Treatment Group": "https://www.hawkinsinc.com/groups/water-treatment/",
    "Univar Solutions": "https://www.univarsolutions.com",
    "BulkChlorine.com": "https://bulkchlorine.com",
    "Waterline Technologies": "https://waterlinetechnologies.com"
}

print("=" * 80)
print("🌐 UPDATING SUPPLIERS WITH WEBSITE INFORMATION")
print("=" * 80)
print()

updated_count = 0
not_found_count = 0

for company_name, website in supplier_websites.items():
    print(f"Updating: {company_name}")
    
    try:
        # Find the supplier
        records = table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
        
        if records:
            record_id = records[0]['id']
            
            # Update with website
            table.update(record_id, {"WEBSITE": website})
            
            print(f"   ✅ Added website: {website}")
            updated_count += 1
        else:
            print(f"   ⚠️  Not found in table")
            not_found_count += 1
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print()
print("=" * 80)
print(f"📊 SUMMARY:")
print(f"   ✅ Updated: {updated_count} suppliers")
if not_found_count > 0:
    print(f"   ⚠️  Not found: {not_found_count}")
print("=" * 80)
print()
print("🎯 NOW YOUR SUPPLIERS HAVE:")
print("   • COMPANY NAME")
print("   • PRIMARY CONTACT EMAIL")
print("   • PRIMARY CONTACT PHONE")
print("   • WEBSITE ✅")
print()
