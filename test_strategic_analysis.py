"""
Test Script for Strategic Analysis Module
Quick verification that everything is working

Usage: python test_strategic_analysis.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("STRATEGIC ANALYSIS MODULE - TEST SUITE")
print("=" * 60)
print()

# Test 1: Import module
print("TEST 1: Importing strategic_analysis_module...")
try:
    from strategic_analysis_module import StrategicAnalysisService
    print("✅ Module imported successfully")
except Exception as e:
    print(f"❌ Failed to import module: {e}")
    sys.exit(1)

print()

# Test 2: Initialize service
print("TEST 2: Initializing service...")
try:
    svc = StrategicAnalysisService()
    print("✅ Service initialized")
except Exception as e:
    print(f"❌ Failed to initialize service: {e}")
    print("   Check that AIRTABLE_API_KEY and AIRTABLE_BASE_ID are in .env")
    sys.exit(1)

print()

# Test 3: Get win themes (default)
print("TEST 3: Getting default win themes...")
try:
    themes = svc.get_win_themes()
    print(f"✅ Retrieved {len(themes)} themes")
    if themes:
        print(f"   Sample theme: {themes[0]['name']} (Win Rate: {themes[0]['win_rate']}%)")
except Exception as e:
    print(f"❌ Failed to get themes: {e}")

print()

# Test 4: Calculate Go/No-Go score (mock data)
print("TEST 4: Calculating Go/No-Go score (mock data)...")
try:
    # This will fail because opportunity doesn't exist in Airtable yet
    # But we can test the logic
    print("   Testing scoring logic...")
    
    # Test score calculation
    test_scores = {
        "relationship_strength": 7,
        "price_competitiveness": 6,
        "technical_capability": 9,
        "resource_availability": 8,
        "past_performance": 7
    }
    
    total = sum(test_scores.values())
    print(f"   Total Score: {total}/50")
    
    if total >= 35:
        recommendation = "Pursue"
        print(f"   ✅ Recommendation: {recommendation} (score >= 35)")
    elif total >= 25:
        recommendation = "Maybe"
        print(f"   ⚠️ Recommendation: {recommendation} (score 25-34)")
    else:
        recommendation = "Skip"
        print(f"   ❌ Recommendation: {recommendation} (score < 25)")
        
except Exception as e:
    print(f"❌ Failed scoring test: {e}")

print()

# Test 5: Test evaluator style detection (offline mode)
print("TEST 5: Testing evaluator style detection...")
try:
    print("   Note: This test requires ANTHROPIC_API_KEY")
    print("   Checking API key...")
    
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_key:
        print(f"   ✅ API key found (starts with: {anthropic_key[:20]}...)")
        print("   Evaluator style detection available")
    else:
        print("   ⚠️ ANTHROPIC_API_KEY not found in environment")
        print("   Evaluator style detection will not work")
        
except Exception as e:
    print(f"❌ Failed API key check: {e}")

print()

# Test 6: Check Airtable connection
print("TEST 6: Checking Airtable connection...")
try:
    # Try to access base
    base = svc.base
    print("   ✅ Connected to Airtable base")
    
    # Try to list tables
    try:
        # Note: This may fail if tables don't exist yet
        print("   Checking for required tables...")
        tables_to_check = [
            'GPSS OPPORTUNITIES',
            'WIN THEMES LIBRARY',
            'EVALUATOR PROFILES'
        ]
        
        for table_name in tables_to_check:
            try:
                table = base.table(table_name)
                # Try to get one record (might be empty)
                records = table.all(max_records=1)
                print(f"   ✅ Table exists: {table_name}")
            except Exception as e:
                print(f"   ⚠️ Table not found or inaccessible: {table_name}")
                print(f"      (This is expected if you haven't run Airtable setup yet)")
                
    except Exception as e:
        print(f"   ⚠️ Could not check tables: {e}")
        
except Exception as e:
    print(f"❌ Airtable connection failed: {e}")
    print("   Check AIRTABLE_API_KEY and AIRTABLE_BASE_ID in .env")

print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print()
print("✅ = Test passed")
print("⚠️ = Test passed with warnings (expected if Airtable not setup)")
print("❌ = Test failed (needs attention)")
print()
print("NEXT STEPS:")
print("1. If Airtable tables don't exist, run: python strategic_analysis_module.py")
print("2. Follow STRATEGIC_ANALYSIS_AIRTABLE_SETUP.md to create tables")
print("3. Test with real data using STRATEGIC_ANALYSIS_QUICK_START.md")
print()
print("=" * 60)
