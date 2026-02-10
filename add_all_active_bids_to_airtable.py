#!/usr/bin/env python3
"""
ADD ALL ACTIVE BIDS TO AIRTABLE
Comprehensive script to add every bid we're working on
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

# Initialize Airtable
api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')
api = Api(api_key)
table = api.table(base_id, 'GPSS OPPORTUNITIES')

# ALL ACTIVE BIDS with deadlines
all_active_bids = [
    # HENRY FORD COLLEGE
    {
        'Name': 'Henry Ford College - Battery Safety Cabinets ($20K-$30K) - Cheryl Ebben',
        'RFP NUMBER': '24515',
        'Deadline': '2026-02-11',
        'Source Status': 'Active'
    },
    
    # CPS ENERGY PADLOCKS
    {
        'Name': 'CPS Energy - Padlocks 3-Year Contract ($30K-$50K) - Amber Salas',
        'RFP NUMBER': 'RFQ 7000205019',
        'Deadline': '2026-02-11',
        'Source Status': 'Active'
    },
    
    # LIVONIA MATERIALS
    {
        'Name': 'Livonia DPW - Topsoil, Sand, Gravel Bundle (~$50K) - Mary Ann Ervin',
        'RFP NUMBER': 'RFP 2026-03',
        'Deadline': '2026-02-23',
        'Source Status': 'Active'
    },
    
    # ROCK ISLAND PAPER BAGS
    {
        'Name': 'Rock Island - Paper Yard Waste Bags (71,280 bags) - Rick Cook',
        'RFP NUMBER': 'Rock Island Paper Bags',
        'Deadline': '2026-04-14',
        'Source Status': 'Active'
    },
    
    # JACKSON COUNTY SALT
    {
        'Name': 'Jackson County - Road Salt (Oct 2026 - Mar 2027) - URGENT DECISION',
        'RFP NUMBER': 'Jackson County Salt',
        'Deadline': '2026-02-02',
        'Source Status': 'Active'
    },
    
    # MADISON HEIGHTS LAWN (Deadline TBD)
    {
        'Name': 'Madison Heights - Lawn Service (CDBG-Funded) - CHECK BIDNET FOR DEADLINE',
        'RFP NUMBER': 'ITB MH 26-03',
        'Deadline': '2026-02-15',  # Placeholder - need to check BidNet
        'Source Status': 'Active'
    },
    
    # WAYNE COUNTY BARRICADES
    {
        'Name': 'Wayne County - Traffic Barricades & Cones - CHECK DEADLINE',
        'RFP NUMBER': 'IFB 37-26-020',
        'Deadline': '2026-02-28',  # Placeholder - need to verify
        'Source Status': 'Active'
    },
    
    # OAKLAND COUNTY BODY BAGS (SUBMITTED)
    {
        'Name': 'Oakland County ME - Body Bags ($95K-$150K) - BID SUBMITTED JAN 27',
        'RFP NUMBER': 'RFQ Oak-0000001089',
        'Deadline': '2026-01-29',
        'Source Status': 'Submitted'
    },
    
    # CPS ENERGY INDUSTRIAL WIPES (MISSED)
    {
        'Name': 'CPS Energy - Industrial Wipes 3-Year ($2.77M) - DEADLINE MISSED',
        'RFP NUMBER': 'RFQ 7000205103',
        'Deadline': '2026-01-27',
        'Source Status': 'Missed'
    },
    
    # WARREN DDA LANDSCAPE (MISSED)
    {
        'Name': 'Warren DDA - Landscape Services - DEADLINE MISSED',
        'RFP NUMBER': 'Warren DDA Landscape',
        'Deadline': '2026-01-28',
        'Source Status': 'Missed'
    },
    
    # ALASKA STEEL CONTAINERS (MISSED)
    {
        'Name': 'Alaska - Steel Containers ($5K-$10K) - DEADLINE MISSED',
        'RFP NUMBER': 'Alaska Steel',
        'Deadline': '2026-01-27',
        'Source Status': 'Missed'
    }
]

print(f'📋 Adding {len(all_active_bids)} bids to NEXUS Airtable...\n')

added = 0
skipped = 0
errors = 0

for bid in all_active_bids:
    try:
        result = table.create(bid)
        print(f'✅ Added: {bid["Name"]}')
        print(f'   Deadline: {bid["Deadline"]} | Status: {bid["Source Status"]}')
        added += 1
    except Exception as e:
        error_msg = str(e)
        if 'DUPLICATE' in error_msg.upper() or 'already exists' in error_msg.lower():
            print(f'⏭️  Skipped (already exists): {bid["Name"]}')
            skipped += 1
        else:
            print(f'❌ Error adding {bid["Name"]}: {error_msg}')
            errors += 1

print(f'\n🎉 RESULTS:')
print(f'   ✅ Added: {added}')
print(f'   ⏭️  Skipped (duplicates): {skipped}')
print(f'   ❌ Errors: {errors}')
print(f'   📊 Total processed: {len(all_active_bids)}')

print(f'\n📅 These will now appear in:')
print(f'   - Daily deadline reports (7 AM email)')
print(f'   - Calendar automation')
print(f'   - Urgent alerts (if within 24 hours)')
print(f'\n🚀 ALL ACTIVE BIDS NOW TRACKED IN NEXUS!')
