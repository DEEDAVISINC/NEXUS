#!/usr/bin/env python3
"""
Add ALL missing contacts from recent solicitations, suppliers, and subs
CRITICAL BUSINESS DEVELOPMENT ACTIVITY
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

# Load environment
load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
contacts_table = api.table(BASE_ID, 'GPSS CONTACTS')

# All contacts to add
contacts = [
    # SOLICITATION CONTACTS
    {
        'Name': 'Noah Cohen',
        'Email': 'ncohen@bayareametro.gov',
        'Title': 'Contract Specialist',
        'Organization': 'Association of Bay Area Governments (ABAG)',
        'Role Category': 'Procurement',
        'Notes': '''Phone: 415-778-5215
Location: San Francisco, CA

Contacted regarding Energy Programs Grant Application Support Services RFQ (Feb 4, 2026). 
Not pursued - specialized grant writing outside core services.

Future opportunities in Bay Area for:
- Transportation services
- Project management
- Emergency services
- Administrative support

Pre-submittal conference: Feb 11, 2026
Proposal due: March 11, 2026'''
    },
    {
        'Name': 'Tracy McDonald',
        'Email': 'tmcdonald@rcoc.org',
        'Title': 'Procurement Specialist',
        'Organization': 'Road Commission for Oakland County (RCOC)',
        'Role Category': 'Procurement',
        'Notes': '''Phone: 248-858-4796
Location: Oakland County, Michigan

PRIMARY CONTACT for multiple RCOC solicitations:
- IFB 7814: Pickup Trucks ($640K-$800K) - IN PROGRESS
- IFB 7732: Paper Products ($81K) - Ready to bid
- IFB 7799: Grease & Air Couplers ($6K) - Submitting
- IFB 7803: Hammers/Tape/Levels ($2.6K) - Submitting
- IFB 7835: Crack Sealing Program
- IFB 7842: Safety Supplies

EXCELLENT RELATIONSHIP - Multiple active opportunities
Opportunities: Municipal equipment, supplies, vehicles, services
Portal: BidNet Direct / MITN'''
    },
    
    # SUPPLIER CONTACTS - TRUCKS
    {
        'Name': 'National Auto Fleet Group - Sales',
        'Email': 'quotes@nationalautofleetgroup.com',
        'Title': 'Fleet Sales Department',
        'Organization': 'National Auto Fleet Group',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 855-289-6572
Fax: 831-480-8497
Location: National coverage
Website: nationalautofleetgroup.com

PRIMARY supplier for RCOC 7814 Trucks RFQ (Feb 4, 2026)
RFQ: DDI-2026-TRUCKS-001 (16 pickup trucks, $640K-$800K)
Quote due: Feb 10, 2026

Supplies: Fleet vehicles, commercial upfitting, turnkey truck solutions
Services: Ford, Chevy, GMC, Ram trucks with complete upfitting
Capabilities: Full-service fleet dealer with upfitting
Account activated: Feb 5, 2026

EXCELLENT for future fleet opportunities'''
    },
    {
        'Name': 'Monroe Truck Equipment - Sales',
        'Email': 'sales@monroetruck.com',
        'Title': 'Commercial Sales',
        'Organization': 'Monroe Truck Equipment',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 800-356-8134
Location: Monroe, WI (national coverage)
Website: monroetruck.com

BACKUP supplier for RCOC 7814 Trucks RFQ (Feb 4, 2026)
RFQ sent via email Feb 4, 2026

Supplies: Work truck bodies, upfitting equipment, commercial truck solutions
Specialties: Dump bodies, service bodies, platform bodies, tow bodies
Partnership: Landstar system, major upfitter

Good for future truck/upfitting opportunities'''
    },
    
    # SUPPLIER CONTACTS - GENERAL
    {
        'Name': 'Grainger - Government Sales',
        'Email': 'government@grainger.com',
        'Title': 'Government Sales Team',
        'Organization': 'W.W. Grainger, Inc.',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 1-800-GRAINGER
Location: National coverage

Active quotes:
- CPS Energy Padlocks (Case #94978198, Quote #2063448396) - $490K contract
- RCOC various items (forestry, welding, automotive tools)

Supplies: Industrial supplies, safety equipment, tools, facilities supplies
Capabilities: Government pricing, large-scale orders, custom stamping, special keying
Account: Active government account

PRIMARY supplier for industrial/municipal supplies
EXCELLENT for future supply contracts'''
    },
    {
        'Name': 'Zoro Tools - Government Sales',
        'Email': 'governmentsales@zoro.com',
        'Title': 'Government Sales',
        'Organization': 'Zoro Tools (Grainger company)',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 855-289-9676
Website: zoro.com

Used for RCOC competitive pricing:
- RCOC 7731: Industrial wipers
- RCOC 7732: Disposable paper products
- Various RCOC supply bids

Supplies: Tools, industrial supplies, safety equipment, facilities supplies
Advantage: Competitive pricing, government discounts
Relationship: Grainger company (lower prices, similar products)

Good for competitive bidding on supply contracts'''
    },
    
    # WATER INFRASTRUCTURE SUPPLIERS
    {
        'Name': 'Ferguson Waterworks - Sales',
        'Email': 'customersupport@ferguson.com',
        'Title': 'Municipal Sales',
        'Organization': 'Ferguson Waterworks',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 1-866-423-7476
Location: National coverage

Contacted for: Canton Township Water Main Parts (Feb 5, 2026 deadline)
Products: Water infrastructure, pipes, fittings, valves, hydrants

Supplies: Municipal water/wastewater supplies, underground utilities
Capabilities: Government pricing, municipal infrastructure projects

PRIMARY for water infrastructure opportunities'''
    },
    {
        'Name': 'HD Supply Waterworks - Sales',
        'Email': 'customercare@hdsupply.com',
        'Title': 'Municipal Sales',
        'Organization': 'HD Supply Waterworks',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 1-800-431-3000
Location: National coverage

Contacted for: Canton Township Water Main Parts (Feb 5, 2026 deadline)
Products: Water infrastructure supplies

Supplies: Water/wastewater supplies, underground utilities, municipal infrastructure
Capabilities: Government pricing, large orders

Good for municipal infrastructure bids'''
    },
    {
        'Name': 'Core & Main - Sales',
        'Email': 'customerservice@coreandmain.com',
        'Title': 'Municipal Sales',
        'Organization': 'Core & Main',
        'Role Category': 'Supplier',
        'Notes': '''Phone: 1-855-CORE-MAIN
Location: National coverage

Contacted for: Canton Township Water Main Parts (Feb 5, 2026 deadline)
Products: Water infrastructure supplies

Supplies: Water distribution, wastewater, storm drainage, fire protection
Specialties: Municipal infrastructure, underground utilities

Good for water/sewer infrastructure bids'''
    }
]

print("="*60)
print("ADDING ALL MISSING CONTACTS TO GPSS CONTACTS")
print("="*60)
print(f"Total contacts to add: {len(contacts)}")
print()

added = 0
skipped = 0
errors = 0

for contact in contacts:
    try:
        print(f"Adding: {contact['Name']} ({contact['Organization']})")
        
        # Check if contact already exists by email
        existing = contacts_table.all(formula=f"{{Email}}='{contact['Email']}'")
        
        if existing:
            print(f"  ⚠️  Already exists - skipping")
            skipped += 1
        else:
            # Create contact
            record = contacts_table.create(contact)
            print(f"  ✅ Added successfully (ID: {record['id']})")
            added += 1
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors += 1
    
    print()

print("="*60)
print("SUMMARY")
print("="*60)
print(f"✅ Added: {added}")
print(f"⚠️  Skipped (already exists): {skipped}")
print(f"❌ Errors: {errors}")
print(f"📇 Total in database: {added + skipped}")
print()
print("🎯 These contacts can now be used for:")
print("   - Capability statement distribution")
print("   - Future opportunity sourcing")
print("   - Quick supplier quotes")
print("   - Relationship building")
print("   - Business intelligence")
print()
print("=" * 60)
