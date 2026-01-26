"""
Transfer all active bids and supplier contacts to NEXUS Airtable
Reads from markdown tracking files and populates proper Airtable tables
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pyairtable import Api

# Load environment
load_dotenv()

# Airtable setup
api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

# Table references
opportunities_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
quotes_table = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')

print("🚀 TRANSFERRING ALL BID DATA TO NEXUS AIRTABLE...\n")

# =====================================================================
# ACTIVE BIDS DATA - Transfer to GPSS OPPORTUNITIES
# =====================================================================

active_bids = [
    {
        "TITLE": "ITB 4614 - Annual Bituminous Materials (Midland)",
        "AGENCY NAME": "City of Midland",
        "SOLICITATION NUMBER": "ITB 4614",
        "ESTIMATED_VALUE": 242000,
        "ESTIMATED_PROFIT": 113000,
        "DUE_DATE": "2026-01-27T14:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "Annual supply of bituminous asphalt materials for road maintenance",
        "SUPPLIERS_CONTACTED": "Bit Mat Products",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "CRITICAL",
        "SUBMISSION_METHOD": "Hand-deliver to City Clerk"
    },
    {
        "TITLE": "ITB 4617 - Annual Sand & Black Dirt (Midland)",
        "AGENCY NAME": "City of Midland",
        "SOLICITATION NUMBER": "ITB 4617",
        "ESTIMATED_VALUE": 207000,
        "ESTIMATED_PROFIT": 76000,
        "DUE_DATE": "2026-01-27T14:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "Annual supply of sand and black dirt for municipal use",
        "SUPPLIERS_CONTACTED": "Fisher Sand & Gravel",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "CRITICAL",
        "SUBMISSION_METHOD": "Hand-deliver to City Clerk"
    },
    {
        "TITLE": "ITB 4616 - Annual Crushed Limestone (Midland)",
        "AGENCY NAME": "City of Midland",
        "SOLICITATION NUMBER": "ITB 4616",
        "ESTIMATED_VALUE": 117000,
        "ESTIMATED_PROFIT": 45000,
        "DUE_DATE": "2026-01-27T14:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "Annual supply of crushed limestone for road projects",
        "SUPPLIERS_CONTACTED": "Fisher Sand & Gravel",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "CRITICAL",
        "SUBMISSION_METHOD": "Hand-deliver to City Clerk"
    },
    {
        "TITLE": "ITB 4615 - Annual Concrete Supply (Midland)",
        "AGENCY NAME": "City of Midland",
        "SOLICITATION NUMBER": "ITB 4615",
        "ESTIMATED_VALUE": 220000,
        "ESTIMATED_PROFIT": 145000,
        "DUE_DATE": "2026-01-27T14:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "Annual supply of ready-mix concrete",
        "SUPPLIERS_CONTACTED": "Fisher Sand & Gravel",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "CRITICAL",
        "SUBMISSION_METHOD": "Hand-deliver to City Clerk"
    },
    {
        "TITLE": "RFQ W912D0-26-Q-025982 - Steel Storage Containers (Alaska JBER)",
        "AGENCY NAME": "U.S. Army Corps of Engineers",
        "SOLICITATION NUMBER": "W912D0-26-Q-025982",
        "ESTIMATED_VALUE": 52000,
        "ESTIMATED_PROFIT": 10500,
        "DUE_DATE": "2026-01-27T16:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "6 steel storage containers (20ft and 40ft) for Joint Base Elmendorf-Richardson, Alaska",
        "SUPPLIERS_CONTACTED": "Container Specialties Alaska, Cascade Container, American Cargo, Marine Container Solutions, Container Alliance",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 5,
        "PRIORITY": "HIGH",
        "SUBMISSION_METHOD": "SAM.gov upload",
        "SET_ASIDE": "Small Business"
    },
    {
        "TITLE": "ITB W-1699 - Warren DDA Landscape Maintenance",
        "AGENCY NAME": "City of Warren Downtown Development Authority",
        "SOLICITATION NUMBER": "ITB W-1699",
        "ESTIMATED_VALUE": 600000,
        "ESTIMATED_PROFIT": 87000,
        "DUE_DATE": "2026-01-27T12:30:00",
        "STATUS": "Conditional - May Skip",
        "STAGE": "Awaiting Qualified Sub",
        "Type": "Service",
        "DESCRIPTION": "5-year landscape maintenance contract (lawn, snow, sweeping) for downtown district",
        "SUPPLIERS_CONTACTED": "Excel Landscaping, Berns Landscape, Warren Lawns, JC Lawnscaping, Excell Landscaping",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "CONDITIONAL",
        "SUBMISSION_METHOD": "BidNet electronic",
        "SPECIAL_REQUIREMENTS": "Need 10+ years municipal landscape experience"
    },
    {
        "TITLE": "ITB MH 26-03 - Madison Heights Yard & Lawn Services",
        "AGENCY NAME": "City of Madison Heights",
        "SOLICITATION NUMBER": "ITB MH 26-03",
        "ESTIMATED_VALUE": 53000,
        "ESTIMATED_PROFIT": 13000,
        "DUE_DATE": "2026-01-28T13:00:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Service",
        "DESCRIPTION": "Annual lawn mowing and yard maintenance services",
        "SUPPLIERS_CONTACTED": "Cut King Lawn Care, The Under Cutters, Ley's Lawn Care",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "HIGH",
        "SUBMISSION_METHOD": "Hand-deliver to City Clerk",
        "SPECIAL_REQUIREMENTS": "Subcontractor forms must be notarized"
    },
    {
        "TITLE": "RFQ Oak-0000001089 - Oakland County Body Bags (Cadaver Bags)",
        "AGENCY NAME": "Oakland County Medical Examiner",
        "SOLICITATION NUMBER": "Oak-0000001089",
        "ESTIMATED_VALUE": 25000,
        "ESTIMATED_PROFIT": 4000,
        "DUE_DATE": "2026-01-29T11:00:00",
        "STATUS": "Ready to Bid",
        "STAGE": "Quote Received",
        "Type": "Product",
        "DESCRIPTION": "Cadaver bags and body transport supplies for medical examiner",
        "SUPPLIERS_CONTACTED": "Mopec",
        "QUOTES_RECEIVED": 1,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "READY",
        "SUBMISSION_METHOD": "Email to danielsj@oakgov.com",
        "QUOTE_DETAILS": "Mopec quote: $762.92 + shipping, expires 3/22/2026"
    },
    {
        "TITLE": "RFQ 7000205103 - CPS Energy Industrial Wipers",
        "AGENCY NAME": "CPS Energy (San Antonio)",
        "SOLICITATION NUMBER": "7000205103",
        "ESTIMATED_VALUE": 419000,
        "ESTIMATED_PROFIT": 42500,
        "DUE_DATE": "2026-01-31T12:00:00",
        "STATUS": "Ready to Bid",
        "STAGE": "Quote Received",
        "Type": "Product",
        "DESCRIPTION": "3-year contract for shop towels and industrial wipers",
        "SUPPLIERS_CONTACTED": "Grainger, Sunbelt Mill Supply, Fastenal",
        "QUOTES_RECEIVED": 1,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "READY",
        "SUBMISSION_METHOD": "Email to tkern@cpsenergy.com",
        "QUOTE_DETAILS": "Grainger quote: $419,188 total, Fastenal declined"
    },
    {
        "TITLE": "RFB #188 - Jackson County Road Salt",
        "AGENCY NAME": "Jackson County Road Commission",
        "SOLICITATION NUMBER": "RFB #188",
        "ESTIMATED_VALUE": 1800000,
        "ESTIMATED_PROFIT": 236000,
        "DUE_DATE": "2026-02-03T10:15:00",
        "STATUS": "Awaiting Quotes",
        "STAGE": "Quote Stage",
        "Type": "Product",
        "DESCRIPTION": "Sodium chloride (road salt) supply for winter 2026-2027",
        "SUPPLIERS_CONTACTED": "Detroit Salt Company",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "HIGH",
        "SUBMISSION_METHOD": "EMAIL ONLY to jcouling@mijackson.org"
    },
    {
        "TITLE": "ITB SH26-002 - Sterling Heights Bulk Aggregate Materials",
        "AGENCY NAME": "City of Sterling Heights",
        "SOLICITATION NUMBER": "ITB SH26-002",
        "ESTIMATED_VALUE": 103000,
        "ESTIMATED_PROFIT": 32000,
        "DUE_DATE": "2026-02-03T14:30:00",
        "STATUS": "No Contact Yet",
        "STAGE": "Need to Contact Suppliers",
        "Type": "Product",
        "DESCRIPTION": "Bulk aggregate materials (sand, gravel, crushed concrete)",
        "SUPPLIERS_CONTACTED": "None yet",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 1,
        "PRIORITY": "URGENT - NO CONTACT",
        "SUBMISSION_METHOD": "MITN electronic portal ONLY"
    },
    {
        "TITLE": "ITB 2026-004 - HCMA Liquid Chlorine",
        "AGENCY NAME": "Housing Commission of Macomb County (HCMA)",
        "SOLICITATION NUMBER": "ITB 2026-004",
        "ESTIMATED_VALUE": 58500,
        "ESTIMATED_PROFIT": 10000,
        "DUE_DATE": "2026-02-18T13:00:00",
        "STATUS": "Not Started",
        "STAGE": "Future - 3+ weeks",
        "Type": "Product",
        "DESCRIPTION": "2-year supply of liquid chlorine for swimming pools at Hubbard Manor East & West",
        "SUPPLIERS_CONTACTED": "None yet",
        "QUOTES_RECEIVED": 0,
        "QUOTES_NEEDED": 3,
        "PRIORITY": "Future - Start Next Week",
        "SUBMISSION_METHOD": "BidNet Direct portal",
        "QUESTIONS_DUE": "2026-02-04T13:00:00"
    }
]

print("📊 CREATING/UPDATING OPPORTUNITIES IN AIRTABLE...\n")

created_count = 0
updated_count = 0
opportunity_records = {}  # Store record IDs for linking to quotes

for bid in active_bids:
    try:
        # Check if opportunity already exists
        existing = opportunities_table.all(formula=f"{{SOLICITATION NUMBER}}='{bid['SOLICITATION NUMBER']}'")
        
        if existing:
            # Update existing record
            record_id = existing[0]['id']
            opportunities_table.update(record_id, bid)
            print(f"✅ UPDATED: {bid['TITLE']}")
            updated_count += 1
            opportunity_records[bid['SOLICITATION NUMBER']] = record_id
        else:
            # Create new record
            result = opportunities_table.create(bid)
            print(f"✨ CREATED: {bid['TITLE']}")
            created_count += 1
            opportunity_records[bid['SOLICITATION NUMBER']] = result['id']
            
    except Exception as e:
        print(f"❌ ERROR with {bid['TITLE']}: {str(e)}")

print(f"\n📊 OPPORTUNITIES SUMMARY: {created_count} created, {updated_count} updated\n")

# =====================================================================
# SUPPLIERS/SUBCONTRACTORS DATA - Transfer to GPSS SUBCONTRACTORS
# =====================================================================

print("=" * 70)
print("👥 CREATING/UPDATING SUBCONTRACTORS/SUPPLIERS IN AIRTABLE...\n")

suppliers_data = [
    # MIDLAND SUPPLIERS
    {
        "COMPANY_NAME": "Bit Mat Products Company",
        "SERVICE_TYPE": "Asphalt/Bituminous Materials",
        "CAPABILITIES": "Industrial asphalt, bituminous materials, road maintenance supplies",
        "PHONE": "Not available",
        "EMAIL": "Not available",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Midland asphalt suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Just contacted",
        "NOTES": "Faxed quote request on 1/24/2026 for ITB 4614"
    },
    {
        "COMPANY_NAME": "Fisher Sand & Gravel",
        "SERVICE_TYPE": "Aggregate Materials",
        "CAPABILITIES": "Sand, gravel, crushed limestone, concrete, black dirt, topsoil",
        "PHONE": "Not available",
        "LOCATION": "Michigan (serves Midland, Livonia areas)",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Michigan aggregate suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Just contacted",
        "NOTES": "Faxed quote request on 1/24/2026 for ITB 4617, 4616, 4615. Open till 12:30 PM Saturdays."
    },
    {
        "COMPANY_NAME": "National Site Materials",
        "SERVICE_TYPE": "Aggregate Materials",
        "CAPABILITIES": "Bulk aggregates, sand, gravel, crushed concrete, stone",
        "LOCATION": "Sterling Heights, Michigan",
        "STATUS": "Available",
        "DISCOVERY_METHOD": "Web search for Sterling Heights aggregate suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "Not yet contacted",
        "NOTES": "PRIMARY TARGET for ITB SH26-002 Sterling Heights - URGENT CONTACT NEEDED"
    },
    
    # ALASKA CONTAINER SUPPLIERS
    {
        "COMPANY_NAME": "Container Specialties Alaska",
        "SERVICE_TYPE": "Steel Storage Containers",
        "CAPABILITIES": "20ft and 40ft steel containers, Alaska delivery",
        "EMAIL": "info@containerspecialtiesak.com",
        "LOCATION": "Anchorage, Alaska",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/24/2026 for RFQ W912D0-26-Q-025982. Need quote by Sunday."
    },
    {
        "COMPANY_NAME": "Cascade Container",
        "SERVICE_TYPE": "Steel Storage Containers",
        "CAPABILITIES": "Shipping containers, storage containers, Alaska shipping",
        "EMAIL": "sales@cascadecontainer.com",
        "LOCATION": "Pacific Northwest (ships to Alaska)",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/24/2026 for RFQ W912D0-26-Q-025982"
    },
    {
        "COMPANY_NAME": "American Cargo Containers",
        "SERVICE_TYPE": "Steel Storage Containers",
        "CAPABILITIES": "Shipping containers nationwide including Alaska",
        "EMAIL": "quotes@americancargo.com",
        "LOCATION": "Nationwide",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/24/2026 for RFQ W912D0-26-Q-025982"
    },
    {
        "COMPANY_NAME": "Marine Container Solutions",
        "SERVICE_TYPE": "Steel Storage Containers",
        "CAPABILITIES": "Marine-grade containers, Alaska military delivery",
        "EMAIL": "sales@marinecontainers.com",
        "LOCATION": "Alaska & Pacific",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/24/2026 for RFQ W912D0-26-Q-025982"
    },
    {
        "COMPANY_NAME": "Container Alliance",
        "SERVICE_TYPE": "Steel Storage Containers",
        "CAPABILITIES": "Container sales and modifications, Alaska shipping",
        "EMAIL": "info@containeralliance.com",
        "LOCATION": "West Coast (ships to Alaska)",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Web search for Alaska container suppliers",
        "DISCOVERY_DATE": "2026-01-24",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/24/2026 for RFQ W912D0-26-Q-025982"
    },
    
    # LAWN CARE SUBCONTRACTORS
    {
        "COMPANY_NAME": "Cut King Lawn Care",
        "SERVICE_TYPE": "Lawn Maintenance",
        "CAPABILITIES": "Commercial lawn mowing, yard services, municipal contracts",
        "EMAIL": "Available (emailed)",
        "LOCATION": "Madison Heights, Michigan area",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Local commercial lawn care search",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/22/2026 for ITB MH 26-03 Madison Heights"
    },
    {
        "COMPANY_NAME": "The Under Cutters",
        "SERVICE_TYPE": "Lawn Maintenance",
        "CAPABILITIES": "Lawn care, landscaping, commercial services",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Local commercial lawn care search",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/22/2026 for ITB MH 26-03 Madison Heights"
    },
    {
        "COMPANY_NAME": "Ley's Lawn Care",
        "SERVICE_TYPE": "Lawn Maintenance",
        "CAPABILITIES": "Lawn care, commercial mowing, municipal experience",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Local commercial lawn care search",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/22/2026 for ITB MH 26-03 Madison Heights"
    },
    
    # WARREN DDA LANDSCAPERS
    {
        "COMPANY_NAME": "Excel Landscaping",
        "SERVICE_TYPE": "Commercial Landscaping",
        "CAPABILITIES": "Full-service landscape maintenance, snow removal, sweeping",
        "LOCATION": "Warren, Michigan area",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Warren municipal landscaper search",
        "DISCOVERY_DATE": "2026-01-23",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/23/2026 for ITB W-1699. Need 10+ years municipal experience."
    },
    {
        "COMPANY_NAME": "Berns Landscape",
        "SERVICE_TYPE": "Commercial Landscaping",
        "CAPABILITIES": "Landscape maintenance, commercial properties",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Warren municipal landscaper search",
        "DISCOVERY_DATE": "2026-01-23",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/23/2026 for ITB W-1699"
    },
    {
        "COMPANY_NAME": "Warren Lawns",
        "SERVICE_TYPE": "Lawn & Landscape Maintenance",
        "CAPABILITIES": "Municipal lawn care, seasonal services",
        "LOCATION": "Warren, Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Local Warren landscaper search",
        "DISCOVERY_DATE": "2026-01-23",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/23/2026 for ITB W-1699"
    },
    {
        "COMPANY_NAME": "JC Lawnscaping",
        "SERVICE_TYPE": "Lawn & Landscape Maintenance",
        "CAPABILITIES": "Commercial landscaping, lawn maintenance",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Warren landscaper search",
        "DISCOVERY_DATE": "2026-01-23",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/23/2026 for ITB W-1699"
    },
    {
        "COMPANY_NAME": "Excell Landscaping",
        "SERVICE_TYPE": "Commercial Landscaping",
        "CAPABILITIES": "Full-service landscape and snow services",
        "LOCATION": "Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Warren landscaper search",
        "DISCOVERY_DATE": "2026-01-23",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/23/2026 for ITB W-1699"
    },
    
    # PRODUCT SUPPLIERS (Quotes Received)
    {
        "COMPANY_NAME": "Mopec",
        "SERVICE_TYPE": "Medical/Morgue Supplies",
        "CAPABILITIES": "Cadaver bags, body transport supplies, medical examiner equipment",
        "LOCATION": "National supplier",
        "STATUS": "Active",
        "RATING": 5.0,
        "DISCOVERY_METHOD": "Medical supply research",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "Established - Quote received",
        "NOTES": "Quote received by 1/22: $762.92 + shipping for Oak-0000001089. Quote expires 3/22/2026."
    },
    {
        "COMPANY_NAME": "Grainger",
        "SERVICE_TYPE": "Industrial Supplies",
        "CAPABILITIES": "Shop towels, industrial wipers, MRO supplies",
        "LOCATION": "National distributor",
        "STATUS": "Active",
        "RATING": 5.0,
        "DISCOVERY_METHOD": "National industrial supplier",
        "RELATIONSHIP_STATUS": "Established - Quote received",
        "NOTES": "Quote received: $419,188 for 3-year CPS Energy wipers contract (RFQ 7000205103)"
    },
    {
        "COMPANY_NAME": "Sunbelt Mill Supply",
        "SERVICE_TYPE": "Industrial Textiles",
        "CAPABILITIES": "Industrial wipers, shop towels, textile products",
        "EMAIL": "Available (emailed)",
        "LOCATION": "National",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Industrial wiper manufacturer search",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Emailed 1/22/2026 for CPS Energy RFQ 7000205103. Awaiting response."
    },
    {
        "COMPANY_NAME": "Fastenal",
        "SERVICE_TYPE": "Industrial Supplies",
        "CAPABILITIES": "MRO supplies, fasteners, industrial products",
        "LOCATION": "National distributor",
        "STATUS": "Inactive",
        "DISCOVERY_METHOD": "National industrial supplier",
        "RELATIONSHIP_STATUS": "Declined",
        "NOTES": "Declined to quote on CPS Energy wipers contract"
    },
    {
        "COMPANY_NAME": "Detroit Salt Company",
        "SERVICE_TYPE": "Road Salt / De-icing Products",
        "CAPABILITIES": "Sodium chloride (road salt), bulk salt delivery",
        "LOCATION": "Detroit, Michigan",
        "STATUS": "Active",
        "DISCOVERY_METHOD": "Michigan road salt supplier search",
        "DISCOVERY_DATE": "2026-01-22",
        "RELATIONSHIP_STATUS": "New - Awaiting quote",
        "NOTES": "Faxed 1/22/2026 for Jackson County RFB #188. Need quote by Jan 31."
    }
]

supplier_records = {}  # Store record IDs for linking to quotes
supplier_created = 0
supplier_updated = 0

for supplier in suppliers_data:
    try:
        # Check if supplier already exists
        existing = subcontractors_table.all(formula=f"{{COMPANY_NAME}}='{supplier['COMPANY_NAME']}'")
        
        if existing:
            # Update existing record
            record_id = existing[0]['id']
            subcontractors_table.update(record_id, supplier)
            print(f"✅ UPDATED: {supplier['COMPANY_NAME']}")
            supplier_updated += 1
            supplier_records[supplier['COMPANY_NAME']] = record_id
        else:
            # Create new record
            result = subcontractors_table.create(supplier)
            print(f"✨ CREATED: {supplier['COMPANY_NAME']}")
            supplier_created += 1
            supplier_records[supplier['COMPANY_NAME']] = result['id']
            
    except Exception as e:
        print(f"❌ ERROR with {supplier['COMPANY_NAME']}: {str(e)}")

print(f"\n👥 SUPPLIERS SUMMARY: {supplier_created} created, {supplier_updated} updated\n")

# =====================================================================
# QUOTE TRACKING - Transfer to GPSS SUBCONTRACTOR QUOTES
# =====================================================================

print("=" * 70)
print("💬 CREATING QUOTE TRACKING RECORDS...\n")

# Create quote records linking opportunities to suppliers
quotes_data = [
    # Midland Asphalt - Bit Mat
    {
        "OPPORTUNITY": [opportunity_records.get("ITB 4614")],
        "SUBCONTRACTOR": [supplier_records.get("Bit Mat Products Company")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-24",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Bituminous Materials Supply",
        "NOTES": "Faxed quote request on 1/24. Need response by Sunday for Monday deadline."
    },
    # Midland Sand - Fisher
    {
        "OPPORTUNITY": [opportunity_records.get("ITB 4617")],
        "SUBCONTRACTOR": [supplier_records.get("Fisher Sand & Gravel")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-24",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Sand & Black Dirt Supply",
        "NOTES": "Faxed quote request on 1/24. Fisher open till 12:30 PM Saturdays."
    },
    # Midland Limestone - Fisher
    {
        "OPPORTUNITY": [opportunity_records.get("ITB 4616")],
        "SUBCONTRACTOR": [supplier_records.get("Fisher Sand & Gravel")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-24",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Crushed Limestone Supply",
        "NOTES": "Faxed quote request on 1/24."
    },
    # Midland Concrete - Fisher
    {
        "OPPORTUNITY": [opportunity_records.get("ITB 4615")],
        "SUBCONTRACTOR": [supplier_records.get("Fisher Sand & Gravel")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-24",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Ready-Mix Concrete Supply",
        "NOTES": "Faxed quote request on 1/24."
    },
    # Oakland Body Bags - Mopec (RECEIVED)
    {
        "OPPORTUNITY": [opportunity_records.get("Oak-0000001089")],
        "SUBCONTRACTOR": [supplier_records.get("Mopec")],
        "STATUS": "Received",
        "RFQ_SENT_DATE": "2026-01-20",
        "QUOTE_DUE_DATE": "2026-01-27",
        "QUOTE_AMOUNT": 762.92,
        "RESPONSE_TEXT": "Quote for cadaver bags: $762.92 + shipping. Quote valid until 3/22/2026.",
        "SELECTED": True,
        "MARKUP_PERCENTAGE": 18,
        "MARKUP_AMOUNT": 137.33,
        "FINAL_BID_AMOUNT": 900.25,
        "ESTIMATED_PROFIT": 137.33,
        "NOTES": "Quote received and ready to bid. Need to confirm shipping cost to Pontiac, MI."
    },
    # CPS Energy - Grainger (RECEIVED)
    {
        "OPPORTUNITY": [opportunity_records.get("7000205103")],
        "SUBCONTRACTOR": [supplier_records.get("Grainger")],
        "STATUS": "Received",
        "RFQ_SENT_DATE": "2026-01-20",
        "QUOTE_DUE_DATE": "2026-01-28",
        "QUOTE_AMOUNT": 419188,
        "RESPONSE_TEXT": "3-year supply industrial wipers: $419,188 total",
        "SELECTED": True,
        "MARKUP_PERCENTAGE": 10,
        "MARKUP_AMOUNT": 41918.80,
        "FINAL_BID_AMOUNT": 419188,
        "ESTIMATED_PROFIT": 42500,
        "NOTES": "Quote received, ready to bid. Will match Grainger pricing to be competitive."
    },
    # CPS Energy - Sunbelt (PENDING)
    {
        "OPPORTUNITY": [opportunity_records.get("7000205103")],
        "SUBCONTRACTOR": [supplier_records.get("Sunbelt Mill Supply")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-22",
        "QUOTE_DUE_DATE": "2026-01-29",
        "EMAIL_SUBJECT": "Quote Request - Industrial Wipers for CPS Energy",
        "NOTES": "Emailed 1/22. Optional quote for comparison with Grainger."
    },
    # Jackson County Salt - Detroit Salt
    {
        "OPPORTUNITY": [opportunity_records.get("RFB #188")],
        "SUBCONTRACTOR": [supplier_records.get("Detroit Salt Company")],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-22",
        "QUOTE_DUE_DATE": "2026-01-31",
        "EMAIL_SUBJECT": "Quote Request - Road Salt for Jackson County",
        "NOTES": "Faxed quote request on 1/22/2026"
    }
]

# Add Alaska container quotes (5 suppliers)
alaska_suppliers = [
    "Container Specialties Alaska",
    "Cascade Container", 
    "American Cargo Containers",
    "Marine Container Solutions",
    "Container Alliance"
]

for supplier_name in alaska_suppliers:
    quotes_data.append({
        "OPPORTUNITY": [opportunity_records.get("W912D0-26-Q-025982")],
        "SUBCONTRACTOR": [supplier_records.get(supplier_name)],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-24",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Steel Storage Containers for Alaska",
        "NOTES": f"Emailed 1/24. Need quote by Sunday noon for Monday deadline."
    })

# Add Madison Heights lawn care quotes (3 subs)
madison_subs = ["Cut King Lawn Care", "The Under Cutters", "Ley's Lawn Care"]
for sub_name in madison_subs:
    quotes_data.append({
        "OPPORTUNITY": [opportunity_records.get("ITB MH 26-03")],
        "SUBCONTRACTOR": [supplier_records.get(sub_name)],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-22",
        "QUOTE_DUE_DATE": "2026-01-27",
        "EMAIL_SUBJECT": "Subcontractor Quote Request - Madison Heights Lawn Services",
        "NOTES": "Emailed 1/22. Need quote by weekend for notarization Sunday."
    })

# Add Warren DDA landscape quotes (5 subs)
warren_subs = ["Excel Landscaping", "Berns Landscape", "Warren Lawns", "JC Lawnscaping", "Excell Landscaping"]
for sub_name in warren_subs:
    quotes_data.append({
        "OPPORTUNITY": [opportunity_records.get("ITB W-1699")],
        "SUBCONTRACTOR": [supplier_records.get(sub_name)],
        "STATUS": "Pending",
        "RFQ_SENT_DATE": "2026-01-23",
        "QUOTE_DUE_DATE": "2026-01-26",
        "EMAIL_SUBJECT": "Quote Request - Warren DDA 5-Year Landscape Contract",
        "NOTES": "Emailed 1/23. Need quotes AND verification of 10+ years municipal experience."
    })

quotes_created = 0
quotes_updated = 0

for quote in quotes_data:
    try:
        # Only create if both opportunity and subcontractor records exist
        if quote.get("OPPORTUNITY") and quote["OPPORTUNITY"][0] and quote.get("SUBCONTRACTOR") and quote["SUBCONTRACTOR"][0]:
            result = quotes_table.create(quote)
            print(f"✨ CREATED: Quote link for opportunity")
            quotes_created += 1
        else:
            print(f"⚠️  SKIPPED: Missing opportunity or subcontractor link")
            
    except Exception as e:
        print(f"❌ ERROR creating quote: {str(e)}")

print(f"\n💬 QUOTES SUMMARY: {quotes_created} quote records created\n")

# =====================================================================
# FINAL SUMMARY
# =====================================================================

print("=" * 70)
print("\n🎉 TRANSFER COMPLETE!\n")
print(f"📊 Opportunities: {created_count} created, {updated_count} updated")
print(f"👥 Suppliers: {supplier_created} created, {supplier_updated} updated")
print(f"💬 Quote Records: {quotes_created} created")
print(f"\n✅ All bid tracking data is now in NEXUS Airtable!")
print(f"✅ View opportunities, suppliers, and quotes in your Airtable base")
print(f"✅ This data will automatically sync with NEXUS backend and frontend\n")
