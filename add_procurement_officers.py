#!/usr/bin/env python3
"""
ADD ALL PROCUREMENT OFFICERS TO CONTACTS
Extract from PROCUREMENT_OFFICERS_LIST.md and add to GPSS CONTACTS
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
contacts_table = api.table(base_id, 'GPSS CONTACTS')

print("📇 ADDING PROCUREMENT OFFICERS TO CONTACTS")
print("=" * 70)

# All procurement officers from active RFPs
procurement_officers = [
    {
        'Name': 'Mark Rozinsky',
        'Email': 'mrozinsky@dearborn.gov',
        'Title': 'Purchasing Manager',
        'Organization': 'City of Dearborn',
        'Role Category': 'Procurement Officer',
        'Notes': 'ITB #161219 - Emergency Generator Replacement. O\'Reilly Manor & Sareini Manor. Phase 2 generator supply ($120K-$180K). Contact: (313) 943-2375. Department: Purchasing Division. Dearborn, MI. Action: Email Jan 27 to get on vendor list.'
    },
    {
        'Name': 'Tina Marie Kern',
        'Email': 'tkern@cpsenergy.com',
        'Title': 'Buyer #108',
        'Organization': 'CPS Energy',
        'Role Category': 'Procurement Officer',
        'Notes': 'RFQ 7000205103 - Industrial Wipers 3-year contract. Our bid: $504,141. Due Jan 31, 2026. Phone: 210-935-5988. Alt email: BidSubmittal@cpsenergy.com. Address: PO Box 2906, San Antonio, TX 78299-2906. Portal: cpsenergy.diversitycompliance.com'
    },
    {
        'Name': 'Joan E. Daniels',
        'Email': 'danielsj@oakgov.com',
        'Title': 'Procurement Contact',
        'Organization': 'Oakland County Medical Examiner',
        'Role Category': 'Procurement Officer',
        'Notes': 'RFQ Oak-0000001089 - Medical Examiner Body Bags. Due Jan 29, 2026 at 11:00 AM. Phone: 248-326-8391. Medical Examiner\'s Office. Pontiac, MI. Local preference (15 min from Troy). Diversity weighting. Reference #0000408601'
    },
    {
        'Name': 'Madison Heights City Clerk',
        'Email': 'Contact via city website',
        'Title': 'City Clerk',
        'Organization': 'City of Madison Heights',
        'Role Category': 'Procurement Officer',
        'Notes': 'Specifications MH 26-03 - Senior Citizen Yard & Lawn Services. CDBG/OLHSA funded. Due Jan 28, 2026 at 1:00 PM - HAND DELIVERY REQUIRED. Notary required. EDWOSB/WOSB advantage. Address: 300 W 13 Mile Rd, Madison Heights, MI 48071'
    },
    {
        'Name': 'Warren DDA Purchasing',
        'Email': 'Via BidNet Portal',
        'Title': 'Purchasing Department',
        'Organization': 'City of Warren - Downtown Development Authority',
        'Role Category': 'Procurement Officer',
        'Notes': 'ITB-W-1699 - Commercial Landscape Maintenance (7 DDA locations). Due Jan 27, 2026 at 12:30 PM. Critical: 10+ years municipal experience required. Warren, MI. Portal: BidNet (MITN)'
    },
    {
        'Name': 'Jackson County Purchasing',
        'Email': 'jcouling@mijackson.org',
        'Title': 'Department of Transportation Contact',
        'Organization': 'Jackson County',
        'Role Category': 'Procurement Officer',
        'Notes': 'RFB #188 - 2026 Sodium Chloride (Road Salt) - 21,000 tons. Due Feb 2, 2026 at 10:15 AM. EMAIL ONLY submission (DO NOT use BidNet). Value: $1.8M+ LARGEST OPPORTUNITY! Jackson, MI. Questions due Jan 26, answers Jan 27.'
    },
    {
        'Name': 'Sonoma State University Purchasing',
        'Email': 'Via purchasing portal',
        'Title': 'Purchasing Department',
        'Organization': 'Sonoma State University',
        'Role Category': 'Procurement Officer',
        'Notes': 'RFQ #2005793 - Copy Paper (10 pallets). Quote submitted Jan 9, 2026 ($29,687). Deadline Jan 23, 2026 (EXPIRED). Rohnert Park, CA. Status: Awaiting response - follow up needed.'
    }
]

added = 0
skipped = 0

for officer in procurement_officers:
    name = officer['Name']
    email = officer['Email']
    
    # Check if already exists
    try:
        existing = contacts_table.all(formula=f"AND({{Name}}='{name}', {{Email}}='{email}')")
        if existing:
            print(f"\n⏭️  {name} - Already exists")
            skipped += 1
            continue
    except:
        pass
    
    try:
        # Create contact
        record = contacts_table.create(officer)
        print(f"\n✅ ADDED: {name}")
        print(f"   Organization: {officer['Organization']}")
        print(f"   Email: {email}")
        print(f"   Role: {officer.get('Role Category', 'Contact')}")
        added += 1
    except Exception as e:
        print(f"\n❌ ERROR adding {name}: {e}")

print("\n" + "=" * 70)
print(f"✅ Added: {added} procurement officers")
print(f"⏭️  Skipped: {skipped} (already exist)")
print("\n💡 All procurement officers from active RFPs are now in CONTACTS")
