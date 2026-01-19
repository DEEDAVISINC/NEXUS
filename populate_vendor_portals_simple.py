"""
VENDOR PORTAL - Simple Population (Only Known Working Fields)
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Portal data with ONLY the fields that definitely work
PORTALS_SIMPLE = [
    # HIGH PRIORITY
    {
        'Portal Name': 'GSA eBuy - Quick Response Opportunities',
        'URL': 'https://www.ebuy.gsa.gov/ebuy/',
        'Keywords': 'gsa, schedule, rfq, quick response, EDWOSB, women-owned, 24-48hr'
    },
    {
        'Portal Name': 'SBA SubNet - Subcontracting Network',
        'URL': 'https://web.sba.gov/subnet/',
        'Keywords': 'subcontracting, small business, prime, partner, EDWOSB, women-owned'
    },
    {
        'Portal Name': 'VA VETS2 Business Center',
        'URL': 'https://www.va.gov/osdbu/',
        'Keywords': 'veterans affairs, healthcare, services, SDVOSB, EDWOSB, medical'
    },
    {
        'Portal Name': 'Unison Marketplace (GSA)',
        'URL': 'https://unison.gsa.gov/',
        'Keywords': 'gsa, marketplace, technology, services, EDWOSB, innovation'
    },
    {
        'Portal Name': 'SAM.gov - Federal Opportunities',
        'URL': 'https://sam.gov/search/?index=opp',
        'Keywords': 'federal, rfp, rfq, solicitation, government, baseline'
    },
    
    # PRIME CONTRACTORS
    {
        'Portal Name': 'Lockheed Martin Small Business',
        'URL': 'https://www.lockheedmartin.com/en-us/suppliers/small-business.html',
        'Keywords': 'defense, aerospace, IT, subcontracting, EDWOSB, lockheed'
    },
    {
        'Portal Name': 'Raytheon Technologies Suppliers',
        'URL': 'https://www.rtx.com/suppliers/small-business',
        'Keywords': 'defense systems, cybersecurity, subcontracting, raytheon'
    },
    {
        'Portal Name': 'Northrop Grumman Small Business',
        'URL': 'https://www.northropgrumman.com/suppliers/small-business/',
        'Keywords': 'aerospace, defense, cyber, subcontracting, northrop'
    },
    {
        'Portal Name': 'Boeing Supplier Diversity',
        'URL': 'https://www.boeing.com/company/about-bca/washington/supplier-diversity',
        'Keywords': 'aerospace, manufacturing, services, subcontracting, boeing'
    },
    {
        'Portal Name': 'General Dynamics Suppliers',
        'URL': 'https://www.gd.com/our-businesses/supplier-information',
        'Keywords': 'defense, IT, shipbuilding, subcontracting, general dynamics'
    },
    {
        'Portal Name': 'L3Harris Technologies Small Business',
        'URL': 'https://www.l3harris.com/suppliers/small-business',
        'Keywords': 'communications, electronics, defense, subcontracting, l3harris'
    },
    {
        'Portal Name': 'Booz Allen Hamilton Suppliers',
        'URL': 'https://www.boozallen.com/about/suppliers.html',
        'Keywords': 'consulting, professional services, IT, subcontracting, booz allen'
    },
    
    # FEDERAL SPECIALTY
    {
        'Portal Name': 'DIBBS - Defense Logistics Agency',
        'URL': 'https://www.dibbs.dla.mil/',
        'Keywords': 'defense, military, dod, logistics, equipment, maintenance, services'
    },
    {
        'Portal Name': 'NASA SEWP - Technology Solutions',
        'URL': 'https://www.sewp.nasa.gov/',
        'Keywords': 'technology, IT equipment, software, hardware, NASA, innovation'
    },
    {
        'Portal Name': 'DOE EERE Exchange',
        'URL': 'https://eere-exchange.energy.gov/',
        'Keywords': 'energy, research, consulting, professional services, innovation, grants'
    },
    
    # COOPERATIVE
    {
        'Portal Name': 'NECO Cooperative Purchasing',
        'URL': 'https://www.neco.org/',
        'Keywords': 'cooperative, state purchasing, local government, multi-state, piggyback'
    },
    
    # AGENCY-SPECIFIC
    {
        'Portal Name': 'CDC Contracts',
        'URL': 'https://www.cdc.gov/contracts/',
        'Keywords': 'health, public health, cdc, consulting, services, medical'
    },
    {
        'Portal Name': 'NIH Grants & Contracts',
        'URL': 'https://www.nih.gov/grants-funding/grants-contracts',
        'Keywords': 'health, research, nih, consulting, medical, grants'
    },
    {
        'Portal Name': 'DOT Small Business',
        'URL': 'https://www.transportation.gov/osdbu',
        'Keywords': 'transportation, infrastructure, logistics, consulting, dot'
    },
    {
        'Portal Name': 'DHS Small Business',
        'URL': 'https://www.dhs.gov/publication/small-business-contracting',
        'Keywords': 'homeland security, emergency, disaster, consulting, services, dhs'
    },
    {
        'Portal Name': 'DOJ Small Business',
        'URL': 'https://www.justice.gov/osdbu',
        'Keywords': 'justice, law enforcement, consulting, professional services, doj'
    }
]

def populate_simple():
    """Populate with only working fields"""
    
    print("="*70)
    print("VENDOR PORTAL - SIMPLE POPULATION")
    print("Using only: Portal Name, URL, Keywords")
    print("="*70)
    
    vp_table = base.table('VENDOR PORTAL')
    
    print(f"\n📝 Creating {len(PORTALS_SIMPLE)} portals...")
    print("="*70)
    
    created = 0
    failed = 0
    
    for portal in PORTALS_SIMPLE:
        try:
            vp_table.create(portal)
            print(f"   ✅ {portal['Portal Name']}")
            created += 1
        except Exception as e:
            print(f"   ❌ Failed: {portal['Portal Name']}")
            print(f"      Error: {str(e)[:100]}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\n✅ Successfully created: {created} portals")
    if failed > 0:
        print(f"❌ Failed: {failed} portals")
    
    print("\n📊 PORTAL BREAKDOWN:")
    print("   High Priority: 5")
    print("   Prime Contractors: 7")
    print("   Federal Specialty: 3")
    print("   Cooperative: 1")
    print("   Agency-Specific: 5")
    print("   TOTAL: 21 portals")
    
    print("\n" + "="*70)
    print("✅ PORTALS CREATED WITH URLS AND KEYWORDS!")
    print("="*70)
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Check Airtable - should see 21 portals with URLs")
    print("   2. Manually set Portal Type, Category, Status in Airtable")
    print("   3. Or tell me the EXACT select options and I'll populate them")
    
    print("\n💡 TIP:")
    print("   You can now manually fill in Portal Type and Status columns")
    print("   by clicking through your Airtable interface")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    populate_simple()
