#!/usr/bin/env python3
"""
PRIME CONTRACTOR MINING SYSTEM
Automatically finds companies with $10M+ federal contracts who NEED diversity suppliers

Run this to find 20-50 high-quality prospects who are LEGALLY REQUIRED 
to meet diversity subcontracting goals.

FREE - Uses USASpending.gov (no cost) + your existing SAM.gov API key
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from nexus_backend import handle_ddcss_mine_prime_contractors

print("=" * 70)
print("🎯 PRIME CONTRACTOR MINING SYSTEM")
print("=" * 70)
print()
print("Finding companies with $10M+ in federal contracts...")
print("These companies MUST meet diversity subcontracting goals.")
print("They NEED EDWOSB/WOSB suppliers like Dee Davis Inc!")
print()

# Check if SAM.gov API key is set
api_key = os.environ.get('SAM_GOV_API_KEY')
if api_key:
    print("✅ SAM.gov API key found - will get detailed company info")
else:
    print("⚠️  SAM.gov API key not set - using basic info only")
    print("   Get free API key at: https://sam.gov/data-services/")

print()
print("Starting mining...")
print()

# Run the mining
# Customize these parameters:
# - min_contract_value: Minimum total contract value (default: $10M)
# - limit: Max number of prospects to find (default: 50)

results = handle_ddcss_mine_prime_contractors(
    min_contract_value=10000000,  # $10M minimum
    limit=50  # Find up to 50 prospects
)

if results.get('success'):
    print()
    print("=" * 70)
    print("✅ MINING COMPLETE!")
    print("=" * 70)
    print()
    print("📊 RESULTS:")
    print(f"   • Prime contractors analyzed: {results.get('total_found', 0)}")
    print(f"   • High-quality prospects created: {results.get('prospects_created', 0)}")
    print(f"   • Duplicates skipped: {results.get('duplicates_skipped', 0)}")
    print(f"   • Low scores skipped: {results.get('low_scores_skipped', 0)}")
    print()
    print("=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Open Airtable → DDCSS Prospects table")
    print("2. View prospects sorted by AI Score (highest first)")
    print("3. Filter: Status = 'New Lead', Source = 'USASpending.gov Auto-Mining'")
    print("4. Review top 10-20 prospects")
    print("5. Start outreach to HIGH priority prospects (score 85+)")
    print()
    print("💡 TIP: These companies are LEGALLY REQUIRED to use diverse suppliers!")
    print("   They have subcontracting plans with goals they MUST meet.")
    print("   Your EDWOSB certification is exactly what they need.")
    print()
    print("=" * 70)
    
else:
    print()
    print("=" * 70)
    print("❌ MINING FAILED")
    print("=" * 70)
    print()
    print(f"Error: {results.get('error', 'Unknown error')}")
    print()
    print("💡 TROUBLESHOOTING:")
    print("   1. Check internet connection")
    print("   2. Verify AIRTABLE_API_KEY in .env file")
    print("   3. Verify AIRTABLE_BASE_ID in .env file")
    print("   4. Check that 'DDCSS Prospects' table exists in Airtable")
    print()
    print("=" * 70)

print()
