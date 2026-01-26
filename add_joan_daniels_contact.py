#!/usr/bin/env python3
"""
Add Joan E. Daniels (Oakland County) to GPSS CONTACTS
Extracted from Q&A Document 5 review
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CONTACTS_TABLE = 'GPSS CONTACTS'

api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)

print("="*80)
print("📋 ADDING JOAN E. DANIELS TO GPSS CONTACTS")
print("="*80)
print()

# Check if contact already exists
email = "danielsj@oakgov.com"
formula = f"{{Email}} = '{email}'"
existing = table.all(formula=formula, max_records=1)

contact_data = {
    'Name': 'Joan E. Daniels',
    'Email': 'danielsj@oakgov.com',
    'Phone': '248-326-8391',
    'Organization': 'Oakland County',
    'Title': 'Procurement Contact',
    'Department': 'Medical Examiner\'s Office',
    'Role': 'Procurement Officer',
    'Location': 'Pontiac, MI',
    'Notes': '''RFQ Oak-0000001089 - ME: Body Bags
Due: January 29, 2026 at 11:00 AM EST
Value: $95K-$150K (3-year contract)

Answered Q&A Document 5 questions (Q7, Q8, Q9) same day.
Very responsive and helpful.

KEY INSIGHTS:
- White bags = backup protection (low volume, infrequent use)
- Focus on black cadaver bags (Items 1-6) for main contract
- Diversity certifications preferred (EDWOSB/WOSB/MBE)
- Local preference (15 min from Troy)
- BidNet registration sufficient for certs

RELATIONSHIP STATUS: Engaged
- Submitted questions: Jan 22, 2026
- Received answers: Jan 22, 2026 (same day)
- Next contact: After bid submission Jan 29

FOLLOW-UP: Contact after award to discuss ongoing contract''',
    'Source': 'RFP/RFQ',
    'Contact Type': 'Government',
    'Agency Level': 'County',
    'Status': 'Active',
    'Priority': 'High'
}

if existing:
    # Update existing contact
    record_id = existing[0]['id']
    table.update(record_id, contact_data)
    print(f"✅ UPDATED: Joan E. Daniels")
    print(f"   Record ID: {record_id}")
    print(f"   Email: {email}")
    print(f"   Organization: Oakland County")
    print(f"   Added Q&A Document 5 insights")
else:
    # Create new contact
    record = table.create(contact_data)
    print(f"✅ ADDED: Joan E. Daniels")
    print(f"   Record ID: {record['id']}")
    print(f"   Email: {email}")
    print(f"   Organization: Oakland County")
    print(f"   Department: Medical Examiner's Office")

print()
print("="*80)
print("📊 CONTACT ADDED TO GPSS CONTACTS")
print("="*80)
print()
print("💡 KEY INSIGHTS FROM Q&A DOCUMENT 5:")
print("   - White bags = low priority (infrequent use)")
print("   - Focus on Items 1-6 (black cadaver bags)")
print("   - BidNet handles cert verification")
print("   - Very responsive buyer (answered same day)")
print()
print("✅ Next: Submit bid by January 29, 2026")
print()
