"""
Update all suppliers with complete information using CORRECT field names (ALL CAPS)
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("📝 UPDATING ALL 21 SUPPLIERS WITH COMPLETE INFORMATION...\n")

# Complete supplier data with CORRECT field names
complete_suppliers = {
    "Bit Mat Products Company": {
        "SERVICE TYPE": "Asphalt/Bituminous Materials",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Industrial asphalt, bituminous materials, road maintenance supplies",
        "DISCOVERY METHOD": "Web search for Midland asphalt suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Just contacted",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Faxed quote request on 1/24/2026 for ITB 4614 (Midland asphalt). Awaiting response."
    },
    "Fisher Sand & Gravel": {
        "SERVICE TYPE": "Aggregate Materials",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Sand, gravel, crushed limestone, concrete, black dirt, topsoil",
        "DISCOVERY METHOD": "Web search for Michigan aggregate suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Just contacted",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Faxed quote request on 1/24 for ITB 4617, 4616, 4615. Open till 12:30 PM Saturdays."
    },
    "National Site Materials": {
        "SERVICE TYPE": "Bulk Aggregates",
        "CITY": "Sterling Heights",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Bulk aggregates, sand, gravel, crushed concrete, stone",
        "DISCOVERY METHOD": "Web search for Sterling Heights aggregate suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "Not yet contacted",
        "NOTES": "PRIMARY TARGET for ITB SH26-002 Sterling Heights - URGENT CONTACT NEEDED"
    },
    "Container Specialties Alaska": {
        "SERVICE TYPE": "Steel Storage Containers",
        "CITY": "Anchorage",
        "STATE": "AK",
        "PHONE": "",
        "EMAIL": "info@containerspecialtiesak.com",
        "WEBSITE": "",
        "DESCRIPTION": "20ft and 40ft steel containers, Alaska delivery",
        "DISCOVERY METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Emailed 1/24 for RFQ W912D0-26-Q-025982. Need quote by Sunday."
    },
    "Cascade Container": {
        "SERVICE TYPE": "Steel Storage Containers",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "sales@cascadecontainer.com",
        "WEBSITE": "",
        "DESCRIPTION": "Shipping containers, storage containers, Alaska shipping",
        "DISCOVERY METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Emailed 1/24 for RFQ W912D0-26-Q-025982"
    },
    "American Cargo Containers": {
        "SERVICE TYPE": "Steel Storage Containers",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "quotes@americancargo.com",
        "WEBSITE": "",
        "DESCRIPTION": "Shipping containers nationwide including Alaska",
        "DISCOVERY METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Emailed 1/24 for RFQ W912D0-26-Q-025982"
    },
    "Marine Container Solutions": {
        "SERVICE TYPE": "Steel Storage Containers",
        "CITY": "",
        "STATE": "AK",
        "PHONE": "",
        "EMAIL": "sales@marinecontainers.com",
        "WEBSITE": "",
        "DESCRIPTION": "Marine-grade containers, Alaska military delivery",
        "DISCOVERY METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Emailed 1/24 for RFQ W912D0-26-Q-025982"
    },
    "Container Alliance": {
        "SERVICE TYPE": "Steel Storage Containers",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "info@containeralliance.com",
        "WEBSITE": "",
        "DESCRIPTION": "Container sales and modifications, Alaska shipping",
        "DISCOVERY METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY DATE": "2026-01-24",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-24",
        "NOTES": "Emailed 1/24 for RFQ W912D0-26-Q-025982"
    },
    "Cut King Lawn Care": {
        "SERVICE TYPE": "Lawn Maintenance",
        "CITY": "Madison Heights",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Commercial lawn mowing, yard services, municipal contracts",
        "DISCOVERY METHOD": "Local commercial lawn care search",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Emailed 1/22 for ITB MH 26-03 Madison Heights"
    },
    "The Under Cutters": {
        "SERVICE TYPE": "Lawn Maintenance",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Lawn care, landscaping, commercial services",
        "DISCOVERY METHOD": "Local commercial lawn care search",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Emailed 1/22 for ITB MH 26-03 Madison Heights"
    },
    "Ley's Lawn Care": {
        "SERVICE TYPE": "Lawn Maintenance",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Lawn care, commercial mowing, municipal experience",
        "DISCOVERY METHOD": "Local commercial lawn care search",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Emailed 1/22 for ITB MH 26-03 Madison Heights"
    },
    "Excel Landscaping": {
        "SERVICE TYPE": "Commercial Landscaping",
        "CITY": "Warren",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Full-service landscape maintenance, snow removal, sweeping",
        "DISCOVERY METHOD": "Warren municipal landscaper search",
        "DISCOVERY DATE": "2026-01-23",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-23",
        "NOTES": "Emailed 1/23 for ITB W-1699. Need 10+ years municipal experience."
    },
    "Berns Landscape": {
        "SERVICE TYPE": "Commercial Landscaping",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Landscape maintenance, commercial properties",
        "DISCOVERY METHOD": "Warren municipal landscaper search",
        "DISCOVERY DATE": "2026-01-23",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-23",
        "NOTES": "Emailed 1/23 for ITB W-1699"
    },
    "Warren Lawns": {
        "SERVICE TYPE": "Lawn & Landscape Maintenance",
        "CITY": "Warren",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Municipal lawn care, seasonal services",
        "DISCOVERY METHOD": "Local Warren landscaper search",
        "DISCOVERY DATE": "2026-01-23",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-23",
        "NOTES": "Emailed 1/23 for ITB W-1699"
    },
    "JC Lawnscaping": {
        "SERVICE TYPE": "Lawn & Landscape Maintenance",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Commercial landscaping, lawn maintenance",
        "DISCOVERY METHOD": "Warren landscaper search",
        "DISCOVERY DATE": "2026-01-23",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-23",
        "NOTES": "Emailed 1/23 for ITB W-1699"
    },
    "Excell Landscaping": {
        "SERVICE TYPE": "Commercial Landscaping",
        "CITY": "",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Full-service landscape and snow services",
        "DISCOVERY METHOD": "Warren landscaper search",
        "DISCOVERY DATE": "2026-01-23",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-23",
        "NOTES": "Emailed 1/23 for ITB W-1699"
    },
    "Mopec": {
        "SERVICE TYPE": "Medical/Morgue Supplies",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Cadaver bags, body transport supplies, medical examiner equipment",
        "DISCOVERY METHOD": "Medical supply research",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "Established - Quote received",
        "RELIABILITY RATING": 5,
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Quote received by 1/22: $762.92 + shipping for Oak-0000001089. Quote expires 3/22/2026."
    },
    "Grainger": {
        "SERVICE TYPE": "Industrial Supplies",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Shop towels, industrial wipers, MRO supplies",
        "DISCOVERY METHOD": "National industrial supplier",
        "RELATIONSHIP STATUS": "Established - Quote received",
        "RELIABILITY RATING": 5,
        "LAST CONTACTED": "2026-01-20",
        "NOTES": "Quote received: $419,188 for 3-year CPS Energy wipers contract (RFQ 7000205103)"
    },
    "Sunbelt Mill Supply": {
        "SERVICE TYPE": "Industrial Textiles",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Industrial wipers, shop towels, textile products",
        "DISCOVERY METHOD": "Industrial wiper manufacturer search",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Emailed 1/22 for CPS Energy RFQ 7000205103. Awaiting response."
    },
    "Fastenal": {
        "SERVICE TYPE": "Industrial Supplies",
        "CITY": "",
        "STATE": "",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "MRO supplies, fasteners, industrial products",
        "DISCOVERY METHOD": "National industrial supplier",
        "RELATIONSHIP STATUS": "Declined",
        "LAST CONTACTED": "2026-01-20",
        "NOTES": "Declined to quote on CPS Energy wipers contract"
    },
    "Detroit Salt Company": {
        "SERVICE TYPE": "Road Salt / De-icing Products",
        "CITY": "Detroit",
        "STATE": "MI",
        "PHONE": "",
        "EMAIL": "",
        "WEBSITE": "",
        "DESCRIPTION": "Sodium chloride (road salt), bulk salt delivery",
        "DISCOVERY METHOD": "Michigan road salt supplier search",
        "DISCOVERY DATE": "2026-01-22",
        "RELATIONSHIP STATUS": "New - Awaiting quote",
        "LAST CONTACTED": "2026-01-22",
        "NOTES": "Faxed 1/22 for Jackson County RFB #188. Need quote by Jan 31."
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

for company_name, details in complete_suppliers.items():
    record_id = sub_lookup.get(company_name)
    
    if not record_id:
        print(f"⚠️  No record found for: {company_name}")
        continue
    
    try:
        subs_table.update(record_id, details)
        print(f"✅ {company_name}")
        updated += 1
    except Exception as e:
        print(f"❌ {company_name}: {str(e)}")

print(f"\n🎉 UPDATED: {updated}/21 suppliers with complete information")
print("\n✅ Check your GPSS SUBCONTRACTORS table in Airtable!")
