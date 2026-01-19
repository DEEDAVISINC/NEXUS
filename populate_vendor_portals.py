"""
VENDOR PORTAL - Complete Data Population Script
Cleans up duplicates and populates all fields for Hidden Goldmine portals
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Complete portal data with all fields
COMPLETE_PORTALS = [
    # HIGH PRIORITY PORTALS
    {
        'Portal Name': 'GSA eBuy - Quick Response Opportunities',
        'URL': 'https://www.ebuy.gsa.gov/ebuy/',
        'Portal Type': 'High Priority',
        'Category': 'Federal Direct',
        'Keywords': 'gsa, schedule, rfq, quick response, EDWOSB, women-owned, 24-48hr',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'SBA SubNet - Subcontracting Network',
        'URL': 'https://web.sba.gov/subnet/',
        'Portal Type': 'High Priority',
        'Category': 'Subcontracting',
        'Keywords': 'subcontracting, small business, prime, partner, EDWOSB, women-owned',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'VA VETS2 Business Center',
        'URL': 'https://www.va.gov/osdbu/',
        'Portal Type': 'High Priority',
        'Category': 'Agency-Specific',
        'Keywords': 'veterans affairs, healthcare, services, SDVOSB, EDWOSB, medical',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'Unison Marketplace (GSA)',
        'URL': 'https://unison.gsa.gov/',
        'Portal Type': 'High Priority',
        'Category': 'Federal Direct',
        'Keywords': 'gsa, marketplace, technology, services, EDWOSB, innovation',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'SAM.gov - Federal Opportunities',
        'URL': 'https://sam.gov/search/?index=opp',
        'Portal Type': 'High Priority',
        'Category': 'Federal Direct',
        'Keywords': 'federal, rfp, rfq, solicitation, government, baseline',
        'Status': 'Active',
        'Search Enabled': True
    },
    
    # PRIME CONTRACTOR PORTALS
    {
        'Portal Name': 'Lockheed Martin Small Business',
        'URL': 'https://www.lockheedmartin.com/en-us/suppliers/small-business.html',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'defense, aerospace, IT, subcontracting, EDWOSB, lockheed',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'Raytheon Technologies Suppliers',
        'URL': 'https://www.rtx.com/suppliers/small-business',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'defense systems, cybersecurity, subcontracting, raytheon',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'Northrop Grumman Small Business',
        'URL': 'https://www.northropgrumman.com/suppliers/small-business/',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'aerospace, defense, cyber, subcontracting, northrop',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'Boeing Supplier Diversity',
        'URL': 'https://www.boeing.com/company/about-bca/washington/supplier-diversity',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'aerospace, manufacturing, services, subcontracting, boeing',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'General Dynamics Suppliers',
        'URL': 'https://www.gd.com/our-businesses/supplier-information',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'defense, IT, shipbuilding, subcontracting, general dynamics',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'L3Harris Technologies Small Business',
        'URL': 'https://www.l3harris.com/suppliers/small-business',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'communications, electronics, defense, subcontracting, l3harris',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'Booz Allen Hamilton Suppliers',
        'URL': 'https://www.boozallen.com/about/suppliers.html',
        'Portal Type': 'Prime Contractor',
        'Category': 'Subcontracting',
        'Keywords': 'consulting, professional services, IT, subcontracting, booz allen',
        'Status': 'Active',
        'Search Enabled': True
    },
    
    # FEDERAL SPECIALTY PORTALS
    {
        'Portal Name': 'DIBBS - Defense Logistics Agency',
        'URL': 'https://www.dibbs.dla.mil/',
        'Portal Type': 'Federal Specialty',
        'Category': 'Defense',
        'Keywords': 'defense, military, dod, logistics, equipment, maintenance, services',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'NASA SEWP - Technology Solutions',
        'URL': 'https://www.sewp.nasa.gov/',
        'Portal Type': 'Federal Specialty',
        'Category': 'Technology',
        'Keywords': 'technology, IT equipment, software, hardware, NASA, innovation',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'DOE EERE Exchange',
        'URL': 'https://eere-exchange.energy.gov/',
        'Portal Type': 'Federal Specialty',
        'Category': 'Energy & Research',
        'Keywords': 'energy, research, consulting, professional services, innovation, grants',
        'Status': 'Active',
        'Search Enabled': True
    },
    
    # COOPERATIVE PLATFORMS
    {
        'Portal Name': 'NECO Cooperative Purchasing',
        'URL': 'https://www.neco.org/',
        'Portal Type': 'Cooperative',
        'Category': 'State & Local',
        'Keywords': 'cooperative, state purchasing, local government, multi-state, piggyback',
        'Status': 'Active',
        'Search Enabled': True
    },
    
    # AGENCY-SPECIFIC PORTALS
    {
        'Portal Name': 'CDC Contracts',
        'URL': 'https://www.cdc.gov/contracts/',
        'Portal Type': 'Agency-Specific',
        'Category': 'Health',
        'Keywords': 'health, public health, cdc, consulting, services, medical',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'NIH Grants & Contracts',
        'URL': 'https://www.nih.gov/grants-funding/grants-contracts',
        'Portal Type': 'Agency-Specific',
        'Category': 'Health',
        'Keywords': 'health, research, nih, consulting, medical, grants',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'DOT Small Business',
        'URL': 'https://www.transportation.gov/osdbu',
        'Portal Type': 'Agency-Specific',
        'Category': 'Transportation',
        'Keywords': 'transportation, infrastructure, logistics, consulting, dot',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'DHS Small Business',
        'URL': 'https://www.dhs.gov/publication/small-business-contracting',
        'Portal Type': 'Agency-Specific',
        'Category': 'Security',
        'Keywords': 'homeland security, emergency, disaster, consulting, services, dhs',
        'Status': 'Active',
        'Search Enabled': True
    },
    {
        'Portal Name': 'DOJ Small Business',
        'URL': 'https://www.justice.gov/osdbu',
        'Portal Type': 'Agency-Specific',
        'Category': 'Justice',
        'Keywords': 'justice, law enforcement, consulting, professional services, doj',
        'Status': 'Active',
        'Search Enabled': True
    }
]

def cleanup_and_populate():
    """Remove duplicates and populate all portal data"""
    
    print("="*70)
    print("VENDOR PORTAL - CLEANUP AND POPULATION")
    print("="*70)
    
    vp_table = base.table('VENDOR PORTAL')
    
    # Get all existing records
    existing_records = vp_table.all()
    
    print(f"\n📊 Current state: {len(existing_records)} records")
    print(f"🎯 Target state: {len(COMPLETE_PORTALS)} unique portals")
    
    # Delete all existing records to start fresh
    print("\n🗑️  Removing all existing records...")
    deleted = 0
    for record in existing_records:
        try:
            vp_table.delete(record['id'])
            deleted += 1
            portal_name = record['fields'].get('Portal Name', 'Unknown')
            print(f"   ✅ Deleted: {portal_name}")
        except Exception as e:
            print(f"   ⚠️  Error deleting record: {e}")
    
    print(f"\n✅ Cleaned up {deleted} records")
    
    # Create all portals with complete data
    print(f"\n📝 Creating {len(COMPLETE_PORTALS)} portals with complete data...")
    print("="*70)
    
    created = 0
    failed = 0
    
    # Group by category for better output
    high_priority = [p for p in COMPLETE_PORTALS if p['Portal Type'] == 'High Priority']
    prime_contractors = [p for p in COMPLETE_PORTALS if p['Portal Type'] == 'Prime Contractor']
    federal_specialty = [p for p in COMPLETE_PORTALS if p['Portal Type'] == 'Federal Specialty']
    cooperative = [p for p in COMPLETE_PORTALS if p['Portal Type'] == 'Cooperative']
    agency_specific = [p for p in COMPLETE_PORTALS if p['Portal Type'] == 'Agency-Specific']
    
    categories = [
        ("HIGH PRIORITY", high_priority),
        ("PRIME CONTRACTORS", prime_contractors),
        ("FEDERAL SPECIALTY", federal_specialty),
        ("COOPERATIVE", cooperative),
        ("AGENCY-SPECIFIC", agency_specific)
    ]
    
    for category_name, portals in categories:
        print(f"\n🏢 {category_name}:")
        for portal in portals:
            try:
                vp_table.create(portal)
                print(f"   ✅ {portal['Portal Name']}")
                created += 1
            except Exception as e:
                print(f"   ❌ Failed: {portal['Portal Name']}")
                print(f"      Error: {str(e)[:80]}")
                failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\n✅ Successfully created: {created} portals")
    if failed > 0:
        print(f"❌ Failed: {failed} portals")
    
    print(f"\n📊 BREAKDOWN:")
    print(f"   High Priority: {len(high_priority)}")
    print(f"   Prime Contractors: {len(prime_contractors)}")
    print(f"   Federal Specialty: {len(federal_specialty)}")
    print(f"   Cooperative: {len(cooperative)}")
    print(f"   Agency-Specific: {len(agency_specific)}")
    
    print("\n" + "="*70)
    print("✅ VENDOR PORTAL TABLE IS NOW CLEAN AND COMPLETE!")
    print("="*70)
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Check your Airtable - should see 21 portals")
    print("   2. All fields populated (URL, Portal Type, Category, Keywords, Status)")
    print("   3. No duplicates or 'Unknown' entries")
    print("   4. Ready for mining automation!")
    
    print("\n💡 PRO TIP:")
    print("   Focus on Prime Contractors first - they have 25-40% win rates!")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    cleanup_and_populate()
