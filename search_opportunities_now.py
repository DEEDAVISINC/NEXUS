#!/usr/bin/env python3
"""
QUICK OPPORTUNITY SEARCH
Search SAM.gov and import opportunities matching your keywords
Run this now to find 2 more opportunities!
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Import from nexus_backend
from nexus_backend import handle_sam_api_search

print("=" * 70)
print("🔍 SEARCHING FOR OPPORTUNITIES")
print("=" * 70)
print()

# Keywords you have suppliers for
keywords = [
    'copy paper',
    'office supplies',
    'industrial wipers',
    'shop towels',
    'road salt',
    'sodium chloride',
    'aggregate',
    'sand',
    'gravel',
    'limestone',
    'chlorine',
    'water treatment',
    'first aid',
    'emergency kits',
    'medical supplies'
]

print("📋 SEARCHING FOR:")
for kw in keywords[:5]:
    print(f"   • {kw}")
print(f"   ... and {len(keywords) - 5} more product categories\n")

# Check if API key is set
api_key = os.environ.get('SAM_GOV_API_KEY')
if not api_key:
    print("⚠️  SAM_GOV_API_KEY not set in .env file")
    print("   Using public access (limited results)")
    print("   Get free API key at: https://sam.gov/data-services/\n")

# Search parameters
# Looking for recent opportunities with WOSB/EDWOSB preference
search_params = {
    'limit': 100,  # Get more results
    'postedFrom': '01/19/2026',  # Last week
    'postedTo': '01/26/2026'     # Today
}

print("🔍 Searching SAM.gov for recent opportunities...")
print(f"   Date range: {search_params['postedFrom']} to {search_params['postedTo']}")
print(f"   Looking for: Products you have suppliers for")
print(f"   Preference: EDWOSB/WOSB set-asides\n")

try:
    result = handle_sam_api_search(search_params)
    
    if result.get('success'):
        print("\n" + "=" * 70)
        print("✅ SEARCH COMPLETE")
        print("=" * 70)
        print(f"\n📊 RESULTS:")
        print(f"   • Total found: {result.get('total_found', 0)}")
        print(f"   • Imported to NEXUS: {result.get('imported', 0)}")
        print(f"   • Duplicates skipped: {result.get('duplicates', 0)}")
        print(f"   • Low quality skipped: {result.get('low_scores', 0)}")
        
        if result.get('imported', 0) > 0:
            print(f"\n✅ {result.get('imported')} NEW OPPORTUNITIES added to NEXUS!")
            print("   Go to NEXUS → GPSS → Opportunities to review them")
        else:
            print("\n💡 No new opportunities matched your criteria this week.")
            print("   Try:")
            print("   1. Expand date range (last 2 weeks)")
            print("   2. Search BidNet for Michigan local opportunities")
            print("   3. Check SIGMA VSS (Michigan state portal)")
    else:
        print(f"\n❌ Search failed: {result.get('error', 'Unknown error')}")
        print("\n💡 ALTERNATIVE:")
        print("   1. Go to SAM.gov manually")
        print("   2. Search keywords: 'copy paper', 'office supplies', etc.")
        print("   3. Filter: EDWOSB set-aside, Due in 10-30 days")
        print("   4. Add to NEXUS manually")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 MANUAL SEARCH RECOMMENDED:")
    print("   • SAM.gov → Search → Filter by EDWOSB")
    print("   • BidNet → Michigan → Search your keywords")
    print("   • SIGMA VSS → State of Michigan opportunities")

print("\n" + "=" * 70)
print("💡 QUICK WIN SOURCES:")
print("=" * 70)
print("\n1. SAM.gov (Federal)")
print("   https://sam.gov/search/?index=opp")
print("   Search: 'copy paper EDWOSB' or 'office supplies WOSB'")
print("\n2. BidNet (Local Michigan)")
print("   https://www.bidnetdirect.com/michigan")
print("   You're registered - check daily digest")
print("\n3. Michigan SIGMA")
print("   https://sigma.michigan.gov/")
print("   State contracts for your product categories")
print()
