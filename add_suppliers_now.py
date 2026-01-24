"""
Add all 21 suppliers to GPSS SUBCONTRACTORS using COMPANY NAME field
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("👥 ADDING ALL 21 SUPPLIERS TO GPSS SUBCONTRACTORS...\n")

suppliers = [
    "Bit Mat Products Company",
    "Fisher Sand & Gravel",
    "National Site Materials",
    "Container Specialties Alaska",
    "Cascade Container",
    "American Cargo Containers",
    "Marine Container Solutions",
    "Container Alliance",
    "Cut King Lawn Care",
    "The Under Cutters",
    "Ley's Lawn Care",
    "Excel Landscaping",
    "Berns Landscape",
    "Warren Lawns",
    "JC Lawnscaping",
    "Excell Landscaping",
    "Mopec",
    "Grainger",
    "Sunbelt Mill Supply",
    "Fastenal",
    "Detroit Salt Company"
]

created = 0
failed = []

for supplier_name in suppliers:
    try:
        # Try with "COMPANY NAME" as user says it exists
        result = subs_table.create({"COMPANY NAME": supplier_name})
        print(f"✅ {supplier_name}")
        created += 1
    except Exception as e:
        print(f"❌ {supplier_name}: {str(e)}")
        failed.append((supplier_name, str(e)))

print(f"\n🎉 SUMMARY: {created}/21 suppliers added")

if failed:
    print(f"\n⚠️  FAILED: {len(failed)} suppliers")
    print("\nTrying different field name variations for failed ones...")
    
    # Try alternate field names for failed ones
    alt_names = ["Company Name", "Name", "COMPANY_NAME", "Company", "Subcontractor"]
    
    for supplier_name, error in failed:
        added = False
        for field_name in alt_names:
            try:
                result = subs_table.create({field_name: supplier_name})
                print(f"✅ {supplier_name} (used field: {field_name})")
                added = True
                break
            except:
                continue
        
        if not added:
            print(f"❌ Still failed: {supplier_name}")

print("\n✅ Check your GPSS SUBCONTRACTORS table in Airtable!")
