#!/usr/bin/env python3
"""
Add ALL 9 RCOC BIDS to NEXUS Airtable
So they show up in calendar automation and notifications
"""

import os
from pyairtable import Api
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Airtable
api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')
api = Api(api_key)

# Get the GPSS OPPORTUNITIES table
table = api.table(base_id, 'GPSS OPPORTUNITIES')

# All 9 RCOC bids - only fields we can set (not computed fields)
rcoc_bids = [
    {
        'Name': 'RCOC 7731 - Industrial Wipers ($63,948) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7731',
        'Deadline': '2026-02-02',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7732 - Disposable Paper Products ($81,478) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'IFB 7732',
        'Deadline': '2026-02-10',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7734 - Forestry Supplies ($6,500) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7734',
        'Deadline': '2026-02-02',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7777 - Welding Supplies ($12,338) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7777',
        'Deadline': '2026-02-02',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7797 - Small Automotive Tools ($4,464) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7797',
        'Deadline': '2026-02-04',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7798 - Wiper Blades ($1,521) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7798',
        'Deadline': '2026-02-02',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7799 - Grease and Air Couplers ($6,128) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7799',
        'Deadline': '2026-02-06',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7802 - Building Tools ($6,720) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7802',
        'Deadline': '2026-02-06',
        'Source Status': 'Active'
    },
    {
        'Name': 'RCOC 7803 - Hammers, Tape Measures, Levels ($2,641) - Shari Graves (248) 858-4780',
        'RFP NUMBER': 'RFQ 7803',
        'Deadline': '2026-02-06',
        'Source Status': 'Active'
    }
]

print(f'📋 Adding {len(rcoc_bids)} RCOC bids to NEXUS Opportunities...\n')

added = 0
for bid in rcoc_bids:
    try:
        result = table.create(bid)
        print(f'✅ Added: {bid["Name"]}')
        print(f'   Deadline: {bid["Deadline"]} | RFP #: {bid["RFP NUMBER"]}')
        added += 1
    except Exception as e:
        print(f'❌ Error adding {bid["Name"]}: {str(e)}')

print(f'\n🎉 Successfully added {added}/{len(rcoc_bids)} RCOC bids to NEXUS!')
print(f'\n📅 These will now appear in:')
print(f'   - Daily deadline reports (7 AM email)')
print(f'   - Calendar automation')
print(f'   - Urgent alerts (if within 24 hours)')
print(f'\n🚀 Calendar notifications are NOW ACTIVE for all RCOC bids!')
