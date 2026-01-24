"""
Link opportunities to suppliers via GPSS SUBCONTRACTOR QUOTES
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opps_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
quotes_table = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')

print("💬 LINKING OPPORTUNITIES TO SUPPLIERS...\n")

# Get all opportunities
print("📊 Fetching opportunities...")
all_opps = opps_table.all()
opp_lookup = {}
for opp in all_opps:
    rfp_num = opp['fields'].get('RFP NUMBER')
    if rfp_num:
        opp_lookup[rfp_num] = opp['id']

print(f"   Found {len(opp_lookup)} opportunities")

# Get all subcontractors
print("👥 Fetching subcontractors...")
all_subs = subs_table.all()
sub_lookup = {}
for sub in all_subs:
    company_name = sub['fields'].get('COMPANY NAME')
    if company_name:
        sub_lookup[company_name] = sub['id']

print(f"   Found {len(sub_lookup)} subcontractors")

# Define all the links
quote_links = [
    ("ITB 4614", "Bit Mat Products Company", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4617", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4616", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB 4615", "Fisher Sand & Gravel", "Pending", "2026-01-24", "2026-01-26"),
    ("W912D0-26-Q-025982", "Container Specialties Alaska", "Pending", "2026-01-24", "2026-01-26"),
    ("W912D0-26-Q-025982", "Cascade Container", "Pending", "2026-01-24", "2026-01-26"),
    ("W912D0-26-Q-025982", "American Cargo Containers", "Pending", "2026-01-24", "2026-01-26"),
    ("W912D0-26-Q-025982", "Marine Container Solutions", "Pending", "2026-01-24", "2026-01-26"),
    ("W912D0-26-Q-025982", "Container Alliance", "Pending", "2026-01-24", "2026-01-26"),
    ("ITB W-1699", "Excel Landscaping", "Pending", "2026-01-23", "2026-01-26"),
    ("ITB W-1699", "Berns Landscape", "Pending", "2026-01-23", "2026-01-26"),
    ("ITB W-1699", "Warren Lawns", "Pending", "2026-01-23", "2026-01-26"),
    ("ITB W-1699", "JC Lawnscaping", "Pending", "2026-01-23", "2026-01-26"),
    ("ITB W-1699", "Excell Landscaping", "Pending", "2026-01-23", "2026-01-26"),
    ("ITB MH 26-03", "Cut King Lawn Care", "Pending", "2026-01-22", "2026-01-27"),
    ("ITB MH 26-03", "The Under Cutters", "Pending", "2026-01-22", "2026-01-27"),
    ("ITB MH 26-03", "Ley's Lawn Care", "Pending", "2026-01-22", "2026-01-27"),
    ("Oak-0000001089", "Mopec", "Received", "2026-01-20", "2026-01-27", 762.92),
    ("7000205103", "Grainger", "Received", "2026-01-20", "2026-01-28", 419188),
    ("7000205103", "Sunbelt Mill Supply", "Pending", "2026-01-22", "2026-01-29"),
    ("RFB #188", "Detroit Salt Company", "Pending", "2026-01-22", "2026-01-31"),
]

print(f"\n💬 Creating {len(quote_links)} quote links...\n")

created = 0
failed = []

# Try different possible field names for the links
field_combos = [
    ("Opportunity", "Subcontractor", "Status"),
    ("OPPORTUNITY", "SUBCONTRACTOR", "STATUS"),
    ("Opportunities", "Subcontractors", "Status"),
    ("RFP", "Supplier", "Status"),
]

for rfp_num, supplier_name, status, sent_date, due_date, *quote_amt in quote_links:
    opp_id = opp_lookup.get(rfp_num)
    sub_id = sub_lookup.get(supplier_name)
    
    if not opp_id:
        print(f"⚠️  No opportunity found for: {rfp_num}")
        continue
    if not sub_id:
        print(f"⚠️  No subcontractor found for: {supplier_name}")
        continue
    
    # Try to create the link
    linked = False
    for opp_field, sub_field, status_field in field_combos:
        try:
            data = {
                opp_field: [opp_id],
                sub_field: [sub_id],
                status_field: status
            }
            
            result = quotes_table.create(data)
            print(f"✅ {supplier_name} → {rfp_num}")
            created += 1
            linked = True
            break
        except Exception as e:
            continue
    
    if not linked:
        failed.append((rfp_num, supplier_name))
        print(f"❌ Failed: {supplier_name} → {rfp_num}")

print(f"\n🎉 SUMMARY: {created}/{len(quote_links)} quote links created")

if failed:
    print(f"\n⚠️  Failed to link: {len(failed)} records")
    print("\nMost likely need to add these fields to GPSS SUBCONTRACTOR QUOTES:")
    print("  - Opportunity (Link to GPSS OPPORTUNITIES)")
    print("  - Subcontractor (Link to GPSS SUBCONTRACTORS)")
    print("  - Status (Single select)")

print("\n✅ Check your GPSS SUBCONTRACTOR QUOTES table in Airtable!")
