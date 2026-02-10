#!/usr/bin/env python3
"""
Add RCOC 7797 & 7798 Bids to NEXUS Airtable
Submitted Feb 3, 2026
"""

import os
from pyairtable import Api
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

# RFQ 7797 - Small Automotive Tools
rfq_7797 = {
    'Name': 'RCOC RFQ 7797 - Small Automotive Tools - SUBMITTED',
    'RFP NUMBER': '7797',
    'Source Status': 'RCOC - Submitted $3,977.60 - Conf: 0000377157',
    'Deadline': '2026-02-04'
}

# RFQ 7798 - Wiper Blades
rfq_7798 = {
    'Name': 'RCOC RFQ 7798 - Wiper Blades - SUBMITTED',
    'RFP NUMBER': '7798',
    'Source Status': 'RCOC - Submitted $1,521.00 - Conf: 0000377182',
    'Deadline': '2026-02-04'
}

print("Adding RCOC 7797 & 7798 to NEXUS...")
print()

try:
    # Add RFQ 7797
    print("Adding RFQ 7797 - Small Automotive Tools...")
    record_7797 = table.create(rfq_7797)
    print(f"✅ RFQ 7797 added! Record ID: {record_7797['id']}")
    print(f"   Name: {rfq_7797['Name']}")
    print(f"   Status: {rfq_7797['Source Status']}")
    print()
    
    # Add RFQ 7798
    print("Adding RFQ 7798 - Wiper Blades...")
    record_7798 = table.create(rfq_7798)
    print(f"✅ RFQ 7798 added! Record ID: {record_7798['id']}")
    print(f"   Name: {rfq_7798['Name']}")
    print(f"   Status: {rfq_7798['Source Status']}")
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Bids Submitted: 2")
    print(f"Total Bid Value: $5,498.60")
    print(f"Total Estimated Profit: $616.00")
    print(f"Agency: Road Commission for Oakland County")
    print(f"Deadline: February 4, 2026 at 10:00 AM EST")
    print(f"Status: SUBMITTED")
    print()
    print("✅ Both bids successfully saved to NEXUS!")
    
except Exception as e:
    print(f"❌ Error adding records to Airtable: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
