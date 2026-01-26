"""
Transfer all active bids and supplier contacts to NEXUS Airtable
FIXED VERSION - Uses correct field names from actual Airtable schema
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opportunities_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
quotes_table = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')

print("🚀 TRANSFERRING ALL BID DATA TO NEXUS AIRTABLE...\n")

# =====================================================================
# ACTIVE BIDS DATA - Transfer to GPSS OPPORTUNITIES
# =====================================================================

active_bids = [
    {
        "Name": "ITB 4614 - Annual Bituminous Materials (Midland)",
        "RFP NUMBER": "ITB 4614",
        "Deadline": "2026-01-27T14:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "City of Midland",
        "Estimated Value": 242000,
        "Est Profit": 113000,
        "Priority": "CRITICAL",
        "Suppliers Contacted": "Bit Mat Products (faxed 1/24)",
        "Quotes Status": "0/1"
    },
    {
        "Name": "ITB 4617 - Annual Sand & Black Dirt (Midland)",
        "RFP NUMBER": "ITB 4617",
        "Deadline": "2026-01-27T14:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "City of Midland",
        "Estimated Value": 207000,
        "Est Profit": 76000,
        "Priority": "CRITICAL",
        "Suppliers Contacted": "Fisher Sand & Gravel (faxed 1/24)",
        "Quotes Status": "0/1"
    },
    {
        "Name": "ITB 4616 - Annual Crushed Limestone (Midland)",
        "RFP NUMBER": "ITB 4616",
        "Deadline": "2026-01-27T14:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "City of Midland",
        "Estimated Value": 117000,
        "Est Profit": 45000,
        "Priority": "CRITICAL",
        "Suppliers Contacted": "Fisher Sand & Gravel (faxed 1/24)",
        "Quotes Status": "0/1"
    },
    {
        "Name": "ITB 4615 - Annual Concrete Supply (Midland)",
        "RFP NUMBER": "ITB 4615",
        "Deadline": "2026-01-27T14:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "City of Midland",
        "Estimated Value": 220000,
        "Est Profit": 145000,
        "Priority": "CRITICAL",
        "Suppliers Contacted": "Fisher Sand & Gravel (faxed 1/24)",
        "Quotes Status": "0/1"
    },
    {
        "Name": "RFQ W912D0-26-Q-025982 - Steel Storage Containers (Alaska JBER)",
        "RFP NUMBER": "W912D0-26-Q-025982",
        "Deadline": "2026-01-27T16:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "U.S. Army Corps of Engineers - Alaska",
        "Estimated Value": 52000,
        "Est Profit": 10500,
        "Priority": "HIGH",
        "Suppliers Contacted": "5 container companies (all emailed 1/24)",
        "Quotes Status": "0/5"
    },
    {
        "Name": "ITB W-1699 - Warren DDA Landscape Maintenance (5 years)",
        "RFP NUMBER": "ITB W-1699",
        "Deadline": "2026-01-27T12:30:00.000Z",
        "Status": "Conditional - May Skip",
        "Agency": "City of Warren Downtown Development Authority",
        "Estimated Value": 600000,
        "Est Profit": 87000,
        "Priority": "CONDITIONAL",
        "Suppliers Contacted": "5 landscape companies (emailed 1/23)",
        "Quotes Status": "0/5 - Need 10+ yr municipal exp"
    },
    {
        "Name": "ITB MH 26-03 - Madison Heights Yard & Lawn Services",
        "RFP NUMBER": "ITB MH 26-03",
        "Deadline": "2026-01-28T13:00:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "City of Madison Heights",
        "Estimated Value": 53000,
        "Est Profit": 13000,
        "Priority": "HIGH",
        "Suppliers Contacted": "Cut King, Under Cutters, Ley's (emailed 1/22)",
        "Quotes Status": "0/3 - Must notarize Sunday"
    },
    {
        "Name": "RFQ Oak-0000001089 - Oakland County Body Bags (Cadaver Bags)",
        "RFP NUMBER": "Oak-0000001089",
        "Deadline": "2026-01-29T11:00:00.000Z",
        "Status": "Ready to Bid",
        "Agency": "Oakland County Medical Examiner",
        "Estimated Value": 25000,
        "Est Profit": 4000,
        "Priority": "READY",
        "Suppliers Contacted": "Mopec (quote received)",
        "Quotes Status": "1/1 - $762.92 + shipping"
    },
    {
        "Name": "RFQ 7000205103 - CPS Energy Industrial Wipers (3 years)",
        "RFP NUMBER": "7000205103",
        "Deadline": "2026-01-31T12:00:00.000Z",
        "Status": "Ready to Bid",
        "Agency": "CPS Energy - San Antonio, TX",
        "Estimated Value": 419000,
        "Est Profit": 42500,
        "Priority": "READY",
        "Suppliers Contacted": "Grainger (quote), Sunbelt (pending), Fastenal (declined)",
        "Quotes Status": "1/3 - $419,188 from Grainger"
    },
    {
        "Name": "RFB #188 - Jackson County Road Salt (2026-2027 season)",
        "RFP NUMBER": "RFB #188",
        "Deadline": "2026-02-03T10:15:00.000Z",
        "Status": "Awaiting Quotes",
        "Agency": "Jackson County Road Commission",
        "Estimated Value": 1800000,
        "Est Profit": 236000,
        "Priority": "HIGH",
        "Suppliers Contacted": "Detroit Salt Company (faxed 1/22)",
        "Quotes Status": "0/1"
    },
    {
        "Name": "ITB SH26-002 - Sterling Heights Bulk Aggregate Materials",
        "RFP NUMBER": "ITB SH26-002",
        "Deadline": "2026-02-03T14:30:00.000Z",
        "Status": "No Contact Yet",
        "Agency": "City of Sterling Heights",
        "Estimated Value": 103000,
        "Est Profit": 32000,
        "Priority": "URGENT - NO CONTACT",
        "Suppliers Contacted": "None yet - NEED TO CONTACT TODAY",
        "Quotes Status": "0/1 needed"
    },
    {
        "Name": "ITB 2026-004 - HCMA Liquid Chlorine (2 years)",
        "RFP NUMBER": "ITB 2026-004",
        "Deadline": "2026-02-18T13:00:00.000Z",
        "Status": "Not Started",
        "Agency": "Housing Commission of Macomb County",
        "Estimated Value": 58500,
        "Est Profit": 10000,
        "Priority": "Future - Start Next Week",
        "Suppliers Contacted": "None yet",
        "Quotes Status": "0/3 needed - Questions due 2/4"
    }
]

print("📊 CREATING OPPORTUNITIES IN AIRTABLE...\n")

created_count = 0
opportunity_records = {}

for bid in active_bids:
    try:
        result = opportunities_table.create(bid)
        print(f"✅ CREATED: {bid['Name']}")
        created_count += 1
        opportunity_records[bid['RFP NUMBER']] = result['id']
    except Exception as e:
        print(f"❌ ERROR with {bid['Name']}: {str(e)}")

print(f"\n📊 OPPORTUNITIES: {created_count} created\n")

# =====================================================================
# SUPPLIERS/SUBCONTRACTORS - Transfer to GPSS SUBCONTRACTORS
# =====================================================================

print("=" * 70)
print("👥 CREATING SUBCONTRACTORS/SUPPLIERS IN AIRTABLE...\n")

suppliers_data = [
    {
        "Company Name": "Bit Mat Products Company",
        "Service Type": "Asphalt/Bituminous Materials",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Faxed quote request on 1/24/2026 for ITB 4614 (Midland asphalt). Awaiting response."
    },
    {
        "Company Name": "Fisher Sand & Gravel",
        "Service Type": "Aggregate Materials (sand, gravel, limestone, concrete)",
        "Location": "Michigan (serves Midland, Livonia)",
        "Status": "Active",
        "Notes": "Faxed quote request on 1/24 for ITB 4617, 4616, 4615. Open till 12:30 PM Saturdays."
    },
    {
        "Company Name": "National Site Materials",
        "Service Type": "Bulk Aggregates",
        "Location": "Sterling Heights, MI",
        "Status": "Not Yet Contacted",
        "Notes": "PRIMARY TARGET for ITB SH26-002 Sterling Heights - URGENT CONTACT NEEDED"
    },
    {
        "Company Name": "Container Specialties Alaska",
        "Service Type": "Steel Storage Containers",
        "Location": "Anchorage, Alaska",
        "Email": "info@containerspecialtiesak.com",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ. Need quote by Sunday."
    },
    {
        "Company Name": "Cascade Container",
        "Service Type": "Steel Storage Containers",
        "Location": "Pacific Northwest",
        "Email": "sales@cascadecontainer.com",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ"
    },
    {
        "Company Name": "American Cargo Containers",
        "Service Type": "Steel Storage Containers",
        "Location": "Nationwide",
        "Email": "quotes@americancargo.com",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ"
    },
    {
        "Company Name": "Marine Container Solutions",
        "Service Type": "Steel Storage Containers",
        "Location": "Alaska & Pacific",
        "Email": "sales@marinecontainers.com",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ"
    },
    {
        "Company Name": "Container Alliance",
        "Service Type": "Steel Storage Containers",
        "Location": "West Coast",
        "Email": "info@containeralliance.com",
        "Status": "Active",
        "Notes": "Emailed 1/24 for Alaska RFQ"
    },
    {
        "Company Name": "Cut King Lawn Care",
        "Service Type": "Lawn Maintenance",
        "Location": "Madison Heights, MI area",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03 Madison Heights lawn care"
    },
    {
        "Company Name": "The Under Cutters",
        "Service Type": "Lawn Maintenance",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03"
    },
    {
        "Company Name": "Ley's Lawn Care",
        "Service Type": "Lawn Maintenance",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Emailed 1/22 for ITB MH 26-03"
    },
    {
        "Company Name": "Excel Landscaping",
        "Service Type": "Commercial Landscaping",
        "Location": "Warren, MI area",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699. Need 10+ years municipal experience."
    },
    {
        "Company Name": "Berns Landscape",
        "Service Type": "Commercial Landscaping",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699"
    },
    {
        "Company Name": "Warren Lawns",
        "Service Type": "Lawn & Landscape Maintenance",
        "Location": "Warren, MI",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699"
    },
    {
        "Company Name": "JC Lawnscaping",
        "Service Type": "Lawn & Landscape Maintenance",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699"
    },
    {
        "Company Name": "Excell Landscaping",
        "Service Type": "Commercial Landscaping",
        "Location": "Michigan",
        "Status": "Active",
        "Notes": "Emailed 1/23 for ITB W-1699"
    },
    {
        "Company Name": "Mopec",
        "Service Type": "Medical/Morgue Supplies",
        "Location": "National",
        "Rating": 5,
        "Status": "Active - Quote Received",
        "Notes": "Quote received by 1/22: $762.92 + shipping for Oak-0000001089. Quote expires 3/22/2026."
    },
    {
        "Company Name": "Grainger",
        "Service Type": "Industrial Supplies",
        "Location": "National",
        "Rating": 5,
        "Status": "Active - Quote Received",
        "Notes": "Quote received: $419,188 for 3-year CPS Energy wipers (RFQ 7000205103)"
    },
    {
        "Company Name": "Sunbelt Mill Supply",
        "Service Type": "Industrial Textiles",
        "Location": "National",
        "Status": "Active",
        "Notes": "Emailed 1/22 for CPS Energy RFQ. Awaiting response."
    },
    {
        "Company Name": "Fastenal",
        "Service Type": "Industrial Supplies",
        "Location": "National",
        "Status": "Declined",
        "Notes": "Declined to quote on CPS Energy wipers"
    },
    {
        "Company Name": "Detroit Salt Company",
        "Service Type": "Road Salt / De-icing",
        "Location": "Detroit, MI",
        "Status": "Active",
        "Notes": "Faxed 1/22 for Jackson County RFB #188. Need quote by Jan 31."
    }
]

supplier_records = {}
supplier_created = 0

for supplier in suppliers_data:
    try:
        result = subcontractors_table.create(supplier)
        print(f"✅ CREATED: {supplier['Company Name']}")
        supplier_created += 1
        supplier_records[supplier['Company Name']] = result['id']
    except Exception as e:
        print(f"❌ ERROR with {supplier['Company Name']}: {str(e)}")

print(f"\n👥 SUPPLIERS: {supplier_created} created\n")

# =====================================================================
# QUOTE TRACKING
# =====================================================================

print("=" * 70)
print("💬 CREATING QUOTE TRACKING RECORDS...\n")

quotes_data = []

# Link opportunities to suppliers with quote status
quote_links = [
    ("ITB 4614", "Bit Mat Products Company", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4617", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4616", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4615", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("Oak-0000001089", "Mopec", "Received", "2026-01-20", "2026-01-27", 762.92),
    ("7000205103", "Grainger", "Received", "2026-01-20", "2026-01-28", 419188),
    ("7000205103", "Sunbelt Mill Supply", "Pending", "2026-01-22", "2026-01-29"),
    ("RFB #188", "Detroit Salt Company", "Pending", "2026-01-22", "2026-01-31"),
]

# Alaska containers (5 suppliers)
for supplier_name in ["Container Specialties Alaska", "Cascade Container", "American Cargo Containers", "Marine Container Solutions", "Container Alliance"]:
    quote_links.append(("W912D0-26-Q-025982", supplier_name, "Pending", "2026-01-24", "2026-01-26"))

# Madison Heights lawn (3 subs)
for supplier_name in ["Cut King Lawn Care", "The Under Cutters", "Ley's Lawn Care"]:
    quote_links.append(("ITB MH 26-03", supplier_name, "Pending", "2026-01-22", "2026-01-27"))

# Warren DDA landscape (5 subs)
for supplier_name in ["Excel Landscaping", "Berns Landscape", "Warren Lawns", "JC Lawnscaping", "Excell Landscaping"]:
    quote_links.append(("ITB W-1699", supplier_name, "Pending", "2026-01-23", "2026-01-26"))

quotes_created = 0

for link in quote_links:
    rfp_num = link[0]
    supplier_name = link[1]
    status = link[2]
    sent_date = link[3]
    due_date = link[4]
    quote_amount = link[5] if len(link) > 5 else None
    
    try:
        opp_id = opportunity_records.get(rfp_num)
        sup_id = supplier_records.get(supplier_name)
        
        if opp_id and sup_id:
            quote_data = {
                "Opportunity": [opp_id],
                "Subcontractor": [sup_id],
                "Status": status,
                "RFQ Sent Date": sent_date,
                "Quote Due Date": due_date
            }
            if quote_amount:
                quote_data["Quote Amount"] = quote_amount
            
            result = quotes_table.create(quote_data)
            quotes_created += 1
            print(f"✅ LINKED: {supplier_name} → {rfp_num}")
        else:
            print(f"⚠️  SKIPPED: {supplier_name} → {rfp_num} (missing IDs)")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print(f"\n💬 QUOTES: {quotes_created} quote links created\n")

# =====================================================================
# FINAL SUMMARY
# =====================================================================

print("=" * 70)
print("\n🎉 TRANSFER COMPLETE!\n")
print(f"📊 Opportunities: {created_count} created")
print(f"👥 Suppliers: {supplier_created} created")
print(f"💬 Quote Links: {quotes_created} created")
print(f"\n✅ All bid tracking data is now in NEXUS Airtable!")
print(f"✅ View your Airtable base to see all opportunities, suppliers, and quotes")
print(f"✅ Data will automatically sync with NEXUS backend and frontend\n")
