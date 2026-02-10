"""
Simple script to populate Airtable with existing bids
Uses ONLY the fields that actually exist in the tables
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opportunities_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subcontractors_table = api.table(base_id, 'GPSS SUBCONTRACTORS')

print("🚀 POPULATING AIRTABLE WITH EXISTING BIDS...\n")

# Sample opportunities using ONLY fields that exist
opportunities = [
    {
        "Name": "NIH Surgical Supplies - Sole Source",
        "RFP NUMBER": "NOI-CC-26-002571",
        "Deadline": "2026-02-14",
        "Source Status": "Active"
    },
    {
        "Name": "RCOC 7790 - Road Traffic Signs",
        "RFP NUMBER": "RCOC 7790",
        "Deadline": "2026-02-28",
        "Source Status": "Active"
    },
    {
        "Name": "Rock Island Yard Waste Bags",
        "RFP NUMBER": "ROCK-ISLAND-2026",
        "Deadline": "2026-03-15",
        "Source Status": "Active"
    }
]

# Sample subcontractors using ONLY fields that exist
subcontractors = [
    {"COMPANY NAME": "McKesson Medical Surgical"},
    {"COMPANY NAME": "Grainger"},
    {"COMPANY NAME": "Paper Mart"},
    {"COMPANY NAME": "Interstate Packaging"},
    {"COMPANY NAME": "Uline"}
]

print("📊 Creating Opportunities...")
for opp in opportunities:
    try:
        result = opportunities_table.create(opp)
        print(f"   ✅ Created: {opp['Name']}")
    except Exception as e:
        print(f"   ❌ Error with {opp['Name']}: {e}")

print("\n👥 Creating Subcontractors...")
for sub in subcontractors:
    try:
        result = subcontractors_table.create(sub)
        print(f"   ✅ Created: {sub['COMPANY NAME']}")
    except Exception as e:
        print(f"   ❌ Error with {sub['COMPANY NAME']}: {e}")

print("\n✅ DONE! Check your Airtable and NEXUS frontend Activity Feed!\n")
