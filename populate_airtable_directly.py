"""
Populate Airtable directly with bid data
First adds records with existing fields, then we can add more fields as needed
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opportunities_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
quotes_table = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')

print("🚀 ADDING ALL BID DATA DIRECTLY TO AIRTABLE...\n")

# First, let's see what fields already exist
print("=" * 70)
print("📊 CHECKING EXISTING FIELDS IN GPSS OPPORTUNITIES\n")

try:
    existing_opps = opportunities_table.all(max_records=1)
    if existing_opps:
        print("Current fields:")
        for field in existing_opps[0]['fields'].keys():
            print(f"  ✅ {field}")
except:
    print("  (Table is empty, will create first record)")

print("\n" + "=" * 70)
print("👥 CHECKING EXISTING FIELDS IN GPSS SUBCONTRACTORS\n")

try:
    existing_subs = subcontractors_table.all(max_records=1)
    if existing_subs:
        print("Current fields:")
        for field in existing_subs[0]['fields'].keys():
            print(f"  ✅ {field}")
except:
    print("  (Table is empty, will create first record)")

print("\n" + "=" * 70)
print("💬 CHECKING EXISTING FIELDS IN GPSS SUBCONTRACTOR QUOTES\n")

try:
    existing_quotes = quotes_table.all(max_records=1)
    if existing_quotes:
        print("Current fields:")
        for field in existing_quotes[0]['fields'].keys():
            print(f"  ✅ {field}")
except:
    print("  (Table is empty, will create first record)")

# Now let's add data using ONLY the fields that exist
# Start with a minimal approach - just the fields we know exist

print("\n" + "=" * 70)
print("📊 ADDING OPPORTUNITIES (using existing fields only)...\n")

# Minimal data for opportunities using only confirmed fields
minimal_opportunities = [
    {
        "Name": "ITB 4614 - Annual Bituminous Materials (Midland)",
        "RFP NUMBER": "ITB 4614",
        "Deadline": "2026-01-27",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "ITB 4617 - Annual Sand & Black Dirt (Midland)",
        "RFP NUMBER": "ITB 4617",
        "Deadline": "2026-01-27",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "ITB 4616 - Annual Crushed Limestone (Midland)",
        "RFP NUMBER": "ITB 4616",
        "Deadline": "2026-01-27",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "ITB 4615 - Annual Concrete Supply (Midland)",
        "RFP NUMBER": "ITB 4615",
        "Deadline": "2026-01-27",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "RFQ W912D0-26-Q-025982 - Steel Storage Containers (Alaska JBER)",
        "RFP NUMBER": "W912D0-26-Q-025982",
        "Deadline": "2026-01-27",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "ITB W-1699 - Warren DDA Landscape Maintenance (5 years)",
        "RFP NUMBER": "ITB W-1699",
        "Deadline": "2026-01-27",
        "Status": "Conditional - May Skip"
    },
    {
        "Name": "ITB MH 26-03 - Madison Heights Yard & Lawn Services",
        "RFP NUMBER": "ITB MH 26-03",
        "Deadline": "2026-01-28",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "RFQ Oak-0000001089 - Oakland County Body Bags",
        "RFP NUMBER": "Oak-0000001089",
        "Deadline": "2026-01-29",
        "Status": "Ready to Bid - Quote Received from Mopec"
    },
    {
        "Name": "RFQ 7000205103 - CPS Energy Industrial Wipers (3 years)",
        "RFP NUMBER": "7000205103",
        "Deadline": "2026-01-31",
        "Status": "Ready to Bid - Quote from Grainger"
    },
    {
        "Name": "RFB #188 - Jackson County Road Salt",
        "RFP NUMBER": "RFB #188",
        "Deadline": "2026-02-03",
        "Status": "Awaiting Quotes"
    },
    {
        "Name": "ITB SH26-002 - Sterling Heights Bulk Aggregate Materials",
        "RFP NUMBER": "ITB SH26-002",
        "Deadline": "2026-02-03",
        "Status": "No Contact Yet - URGENT"
    },
    {
        "Name": "ITB 2026-004 - HCMA Liquid Chlorine (2 years)",
        "RFP NUMBER": "ITB 2026-004",
        "Deadline": "2026-02-18",
        "Status": "Not Started"
    }
]

created_opps = 0
opp_records = {}

for opp in minimal_opportunities:
    try:
        result = opportunities_table.create(opp)
        print(f"✅ Created: {opp['Name']}")
        created_opps += 1
        opp_records[opp['RFP NUMBER']] = result['id']
    except Exception as e:
        print(f"❌ Error: {opp['Name']}: {str(e)}")

print(f"\n📊 Created {created_opps} opportunities")

print("\n" + "=" * 70)
print("👥 ADDING SUBCONTRACTORS...\n")

# Try adding subcontractors - we need to figure out what the primary field is called
# Let's try different possible names

suppliers_to_add = [
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

created_subs = 0
sub_records = {}

# Try different possible field names for the primary field
possible_primary_fields = ["Name", "Company Name", "COMPANY_NAME", "Company", "Subcontractor Name"]

for supplier_name in suppliers_to_add:
    created = False
    for field_name in possible_primary_fields:
        try:
            result = subcontractors_table.create({field_name: supplier_name})
            print(f"✅ Created: {supplier_name} (using field: {field_name})")
            created_subs += 1
            sub_records[supplier_name] = result['id']
            created = True
            break
        except:
            continue
    
    if not created:
        print(f"⚠️  Could not create: {supplier_name} (need to add fields manually)")

print(f"\n👥 Created {created_subs} subcontractors")

print("\n" + "=" * 70)
print("💬 ADDING QUOTE LINKS...\n")

# Only add quote links if we have both opportunity and subcontractor IDs
quote_links = [
    ("ITB 4614", "Bit Mat Products Company"),
    ("ITB 4617", "Fisher Sand & Gravel"),
    ("ITB 4616", "Fisher Sand & Gravel"),
    ("ITB 4615", "Fisher Sand & Gravel"),
    ("W912D0-26-Q-025982", "Container Specialties Alaska"),
    ("W912D0-26-Q-025982", "Cascade Container"),
    ("W912D0-26-Q-025982", "American Cargo Containers"),
    ("W912D0-26-Q-025982", "Marine Container Solutions"),
    ("W912D0-26-Q-025982", "Container Alliance"),
    ("ITB W-1699", "Excel Landscaping"),
    ("ITB W-1699", "Berns Landscape"),
    ("ITB W-1699", "Warren Lawns"),
    ("ITB W-1699", "JC Lawnscaping"),
    ("ITB W-1699", "Excell Landscaping"),
    ("ITB MH 26-03", "Cut King Lawn Care"),
    ("ITB MH 26-03", "The Under Cutters"),
    ("ITB MH 26-03", "Ley's Lawn Care"),
    ("Oak-0000001089", "Mopec"),
    ("7000205103", "Grainger"),
    ("7000205103", "Sunbelt Mill Supply"),
    ("RFB #188", "Detroit Salt Company"),
]

created_quotes = 0

# Try different possible field names for the links
possible_opp_fields = ["Opportunity", "OPPORTUNITY", "Opportunities", "RFP"]
possible_sub_fields = ["Subcontractor", "SUBCONTRACTOR", "Supplier", "Company"]

for rfp_num, supplier_name in quote_links:
    opp_id = opp_records.get(rfp_num)
    sub_id = sub_records.get(supplier_name)
    
    if opp_id and sub_id:
        created = False
        for opp_field in possible_opp_fields:
            for sub_field in possible_sub_fields:
                try:
                    result = quotes_table.create({
                        opp_field: [opp_id],
                        sub_field: [sub_id]
                    })
                    print(f"✅ Linked: {supplier_name} → {rfp_num}")
                    created_quotes += 1
                    created = True
                    break
                except:
                    continue
            if created:
                break
        
        if not created:
            print(f"⚠️  Could not link: {supplier_name} → {rfp_num}")
    else:
        print(f"⚠️  Skipped: {supplier_name} → {rfp_num} (missing IDs)")

print(f"\n💬 Created {created_quotes} quote links")

print("\n" + "=" * 70)
print("\n🎉 SUMMARY\n")
print(f"📊 Opportunities: {created_opps}/12 created")
print(f"👥 Subcontractors: {created_subs}/21 created")
print(f"💬 Quote Links: {created_quotes}/21 created")
print("\n✅ Check your Airtable base to see the data!")
print("\n💡 To add the remaining fields (Agency, Est Value, etc.), you'll need to:")
print("   1. Go to Airtable web interface")
print("   2. Click '+' to add fields to each table")
print("   3. Use the CSV files to bulk update with additional data")
