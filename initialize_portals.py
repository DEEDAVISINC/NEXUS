"""
NEXUS Portal Initialization Script
Automatically populates Vendor Portals and Mining Targets with all major government sources
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# Government Portals to Add
VENDOR_PORTALS = [
    {
        'Portal Name': 'SAM.gov - Federal Opportunities',
        'URL': 'https://sam.gov/search/?index=opp',
        'Keywords': 'federal, rfp, rfq, solicitation, government',
    },
    {
        'Portal Name': 'GSA eBuy',
        'URL': 'https://www.ebuy.gsa.gov/ebuy/',
        'Keywords': 'gsa, schedule, rfq, quick response',
    },
    {
        'Portal Name': 'DIBBS - Defense Logistics',
        'URL': 'https://www.dibbs.dla.mil/',
        'Keywords': 'defense, military, dod, logistics',
    },
    {
        'Portal Name': 'Unison Marketplace',
        'URL': 'https://unison.gsa.gov/',
        'Keywords': 'gsa, marketplace, technology, services',
    },
    {
        'Portal Name': 'SBA SubNet',
        'URL': 'https://web.sba.gov/subnet/',
        'Keywords': 'subcontracting, small business, prime, partner',
    },
    {
        'Portal Name': 'NECO Cooperative',
        'URL': 'https://www.neco.org/',
        'Keywords': 'cooperative, state, local, piggyback',
    }
]

MINING_TARGETS = [
    {
        'Target Name': 'FPDS - Federal Procurement Data',
        'Target URL': 'https://www.fpds.gov/fpdsng_cms/index.php/en/',
    },
    {
        'Target Name': 'USASpending.gov - Contract Intelligence',
        'Target URL': 'https://www.usaspending.gov/',
    },
    {
        'Target Name': 'Acquisition.gov - Procurement Forecasts',
        'Target URL': 'https://www.acquisition.gov',
    },
    {
        'Target Name': 'FedBizOpps Archive',
        'Target URL': 'https://www.fbo.gov/',
    },
    {
        'Target Name': 'GSA Advantage',
        'Target URL': 'https://www.gsaadvantage.gov/',
    }
]

def populate_portals():
    """Populate Vendor Portals table"""
    print("🚀 Populating Vendor Portals...")
    
    try:
        vendor_portals_table = base.table('VENDOR PORTAL')
        
        # Check if portals already exist
        existing = vendor_portals_table.all()
        existing_names = [record['fields'].get('Portal Name', '') for record in existing]
        
        added = 0
        skipped = 0
        
        for portal in VENDOR_PORTALS:
            if portal['Portal Name'] in existing_names:
                print(f"  ⏭️  Skipping {portal['Portal Name']} (already exists)")
                skipped += 1
            else:
                vendor_portals_table.create(portal)
                print(f"  ✅ Added {portal['Portal Name']}")
                added += 1
        
        print(f"\n✅ Vendor Portals: {added} added, {skipped} skipped")
        return True
        
    except Exception as e:
        print(f"❌ Error populating Vendor Portals: {e}")
        return False

def populate_mining_targets():
    """Populate Mining Targets table"""
    print("\n🎯 Populating Mining Targets...")
    
    try:
        mining_targets_table = base.table('Mining Targets')
        
        # Check if targets already exist
        existing = mining_targets_table.all()
        existing_names = [record['fields'].get('Target Name', '') for record in existing]
        
        added = 0
        skipped = 0
        
        for target in MINING_TARGETS:
            if target['Target Name'] in existing_names:
                print(f"  ⏭️  Skipping {target['Target Name']} (already exists)")
                skipped += 1
            else:
                mining_targets_table.create(target)
                print(f"  ✅ Added {target['Target Name']}")
                added += 1
        
        print(f"\n✅ Mining Targets: {added} added, {skipped} skipped")
        return True
        
    except Exception as e:
        print(f"❌ Error populating Mining Targets: {e}")
        print(f"Note: If 'Mining Targets' table doesn't exist, create it in Airtable first")
        return False

def main():
    """Main initialization function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║  NEXUS Portal Initialization Script                      ║
║  Populating government opportunity sources...            ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ Error: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID")
        print("Make sure .env file is configured correctly")
        return
    
    # Populate both tables
    portals_success = populate_portals()
    targets_success = populate_mining_targets()
    
    # Summary
    print("""
╔══════════════════════════════════════════════════════════╗
║  INITIALIZATION COMPLETE!                                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if portals_success:
        print("✅ Vendor Portals: Ready for mining")
        print("   - SAM.gov, GSA eBuy, DIBBS, Unison, SubNet, NECO")
    
    if targets_success:
        print("✅ Mining Targets: Ready for intelligence gathering")
        print("   - FPDS, USASpending, Acquisition.gov, GSA Advantage")
    
    print("""
🚀 NEXT STEPS:
1. Go to NEXUS → GPSS System
2. Click "Start Auto-Mining"
3. System will scan all portals automatically
4. New opportunities will appear in your feed

💡 TIP: Mining runs 24/7 once started. Check daily for new opps!
    """)

if __name__ == "__main__":
    main()
