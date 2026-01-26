"""
Update all suppliers with complete information
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("🔍 CHECKING WHAT FIELDS EXIST IN GPSS SUBCONTRACTORS...\n")

# Get all existing records to see what fields we have
all_subs = subs_table.all()
if all_subs:
    print("Current fields in table:")
    sample_record = all_subs[0]
    for field_name in sample_record['fields'].keys():
        print(f"  ✅ {field_name}")
    print()

print("📝 UPDATING ALL SUPPLIERS WITH COMPLETE INFORMATION...\n")

# Complete supplier data
complete_suppliers = {
    "Bit Mat Products Company": {
        "Service Type": "Asphalt/Bituminous Materials",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Faxed quote request on 1/24/2026 for ITB 4614 (Midland asphalt). Awaiting response.",
        "Contact Date": "2026-01-24"
    },
    "Fisher Sand & Gravel": {
        "Service Type": "Aggregate Materials",
        "Location": "Michigan (serves Midland, Livonia)",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Faxed quote request on 1/24 for ITB 4617, 4616, 4615. Open till 12:30 PM Saturdays.",
        "Contact Date": "2026-01-24"
    },
    "National Site Materials": {
        "Service Type": "Bulk Aggregates",
        "Location": "Sterling Heights, MI",
        "City": "Sterling Heights",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Not Yet Contacted",
        "Notes": "PRIMARY TARGET for ITB SH26-002 Sterling Heights - URGENT CONTACT NEEDED"
    },
    "Container Specialties Alaska": {
        "Service Type": "Steel Storage Containers",
        "Location": "Anchorage, Alaska",
        "City": "Anchorage",
        "State": "AK",
        "Phone": "",
        "Email": "info@containerspecialtiesak.com",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ W912D0-26-Q-025982. Need quote by Sunday.",
        "Contact Date": "2026-01-24"
    },
    "Cascade Container": {
        "Service Type": "Steel Storage Containers",
        "Location": "Pacific Northwest",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "sales@cascadecontainer.com",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ",
        "Contact Date": "2026-01-24"
    },
    "American Cargo Containers": {
        "Service Type": "Steel Storage Containers",
        "Location": "Nationwide",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "quotes@americancargo.com",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ",
        "Contact Date": "2026-01-24"
    },
    "Marine Container Solutions": {
        "Service Type": "Steel Storage Containers",
        "Location": "Alaska & Pacific",
        "City": "",
        "State": "AK",
        "Phone": "",
        "Email": "sales@marinecontainers.com",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ",
        "Contact Date": "2026-01-24"
    },
    "Container Alliance": {
        "Service Type": "Steel Storage Containers",
        "Location": "West Coast",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "info@containeralliance.com",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ",
        "Contact Date": "2026-01-24"
    },
    "Cut King Lawn Care": {
        "Service Type": "Lawn Maintenance",
        "Location": "Madison Heights, MI area",
        "City": "Madison Heights",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03 Madison Heights lawn care",
        "Contact Date": "2026-01-22"
    },
    "The Under Cutters": {
        "Service Type": "Lawn Maintenance",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03",
        "Contact Date": "2026-01-22"
    },
    "Ley's Lawn Care": {
        "Service Type": "Lawn Maintenance",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03",
        "Contact Date": "2026-01-22"
    },
    "Excel Landscaping": {
        "Service Type": "Commercial Landscaping",
        "Location": "Warren, MI area",
        "City": "Warren",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699. Need 10+ years municipal experience.",
        "Contact Date": "2026-01-23"
    },
    "Berns Landscape": {
        "Service Type": "Commercial Landscaping",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699",
        "Contact Date": "2026-01-23"
    },
    "Warren Lawns": {
        "Service Type": "Lawn & Landscape Maintenance",
        "Location": "Warren, MI",
        "City": "Warren",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699",
        "Contact Date": "2026-01-23"
    },
    "JC Lawnscaping": {
        "Service Type": "Lawn & Landscape Maintenance",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699",
        "Contact Date": "2026-01-23"
    },
    "Excell Landscaping": {
        "Service Type": "Commercial Landscaping",
        "Location": "Michigan",
        "City": "",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699",
        "Contact Date": "2026-01-23"
    },
    "Mopec": {
        "Service Type": "Medical/Morgue Supplies",
        "Location": "National",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active - Quote Received",
        "Rating": 5,
        "Notes": "Quote received by 1/22: $762.92 + shipping for Oak-0000001089. Quote expires 3/22/2026.",
        "Contact Date": "2026-01-22"
    },
    "Grainger": {
        "Service Type": "Industrial Supplies",
        "Location": "National",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active - Quote Received",
        "Rating": 5,
        "Notes": "Quote received: $419,188 for 3-year CPS Energy wipers (RFQ 7000205103)",
        "Contact Date": "2026-01-20"
    },
    "Sunbelt Mill Supply": {
        "Service Type": "Industrial Textiles",
        "Location": "National",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Emailed 1/22 for CPS Energy RFQ 7000205103. Awaiting response.",
        "Contact Date": "2026-01-22"
    },
    "Fastenal": {
        "Service Type": "Industrial Supplies",
        "Location": "National",
        "City": "",
        "State": "",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Declined",
        "Notes": "Declined to quote on CPS Energy wipers",
        "Contact Date": "2026-01-20"
    },
    "Detroit Salt Company": {
        "Service Type": "Road Salt / De-icing",
        "Location": "Detroit, MI",
        "City": "Detroit",
        "State": "MI",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Status": "Active",
        "Notes": "Faxed 1/22 for Jackson County RFB #188. Need quote by Jan 31.",
        "Contact Date": "2026-01-22"
    }
}

# Get all existing supplier records
all_subs = subs_table.all()
sub_lookup = {}
for sub in all_subs:
    company_name = sub['fields'].get('COMPANY NAME')
    if company_name:
        sub_lookup[company_name] = sub['id']

updated = 0
errors = []

for company_name, details in complete_suppliers.items():
    record_id = sub_lookup.get(company_name)
    
    if not record_id:
        print(f"⚠️  No record found for: {company_name}")
        continue
    
    try:
        # Try to update with all fields
        subs_table.update(record_id, details)
        print(f"✅ Updated: {company_name}")
        updated += 1
    except Exception as e:
        print(f"❌ Error updating {company_name}: {str(e)}")
        errors.append((company_name, str(e)))

print(f"\n🎉 SUMMARY: {updated}/21 suppliers updated with complete information")

if errors:
    print(f"\n⚠️  ERRORS: {len(errors)} suppliers had issues")
    print("\nMost likely these fields don't exist in the table yet:")
    
    # Extract field names from errors
    missing_fields = set()
    for company, error_msg in errors:
        if "Unknown field name" in error_msg:
            # Extract field name from error
            import re
            match = re.search(r'"([^"]*)"', error_msg)
            if match:
                missing_fields.add(match.group(1))
    
    if missing_fields:
        print("\nFields that need to be added to GPSS SUBCONTRACTORS:")
        for field in sorted(missing_fields):
            print(f"  - {field}")
        print("\nAdd these fields in Airtable, then run this script again.")

print("\n✅ Check GPSS SUBCONTRACTORS table in Airtable to see updated data!")
