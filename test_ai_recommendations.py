"""
Test script for AI Recommendation & Approval System
Demonstrates the full workflow: AI suggests → You decide → System learns
"""

import requests
import json
from typing import Dict

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_result(result: Dict):
    """Print API response in readable format"""
    print(json.dumps(result, indent=2))

def test_capability_gap_analysis(opportunity_id: str):
    """Test 1: AI analyzes capability gap and recommends approach"""
    print_section("TEST 1: Capability Gap Analysis")
    
    print("📊 AI analyzing opportunity...")
    print(f"Opportunity ID: {opportunity_id}\n")
    
    response = requests.post(
        f"{BASE_URL}/ai/recommendations/capability-gap",
        headers=HEADERS,
        json={"opportunity_id": opportunity_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ AI Analysis Complete!\n")
        
        analysis = result.get('analysis', {})
        print(f"🤖 AI RECOMMENDATION: {analysis.get('recommendation', '').upper()}")
        print(f"📊 Confidence: {analysis.get('confidence', 0)}%")
        print(f"\n💡 Reasoning:\n{analysis.get('reasoning', '')}\n")
        
        print(f"✅ We can do ({analysis.get('we_can_do_percentage', 0)}%):")
        for skill in analysis.get('we_can_do', []):
            print(f"   - {skill}")
        
        print(f"\n⚠️  We need:")
        for skill in analysis.get('we_need', []):
            print(f"   - {skill}")
        
        compliance = analysis.get('compliance_check', {})
        print(f"\n🔍 Compliance: {'✅' if compliance.get('meets_50_percent_rule') else '❌'} {compliance.get('notes', '')}")
        
        recommendation_id = result.get('recommendation_id')
        print(f"\n📝 Recommendation ID: {recommendation_id}")
        print("\n👤 YOUR TURN: Review and decide (approve/deny)")
        
        return recommendation_id
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return None

def test_approve_recommendation(recommendation_id: str, decision: str = "approved", notes: str = ""):
    """Test 2: User approves/denies recommendation"""
    print_section(f"TEST 2: User Decision - {decision.upper()}")
    
    print(f"📝 Your decision: {decision}")
    print(f"💬 Your notes: {notes}\n")
    
    response = requests.post(
        f"{BASE_URL}/ai/recommendations/{recommendation_id}/approve",
        headers=HEADERS,
        json={
            "decision": decision,
            "notes": notes
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Decision recorded!")
        print(f"\n{result.get('message', '')}\n")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return False

def test_subcontractor_recommendations(opportunity_id: str, needed_skills: list):
    """Test 3: AI recommends subcontractors"""
    print_section("TEST 3: Subcontractor Recommendations")
    
    print(f"🔍 AI searching for subcontractors...")
    print(f"Needed skills: {', '.join(needed_skills)}\n")
    
    response = requests.post(
        f"{BASE_URL}/ai/recommendations/subcontractors",
        headers=HEADERS,
        json={
            "opportunity_id": opportunity_id,
            "needed_skills": needed_skills,
            "contract_value": 500000
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ AI Analysis Complete!\n")
        
        subs = result.get('recommended_subcontractors', [])
        print(f"📊 Found {result.get('total_found', 0)} subcontractors")
        print(f"🎯 Top {len(subs)} recommendations:\n")
        
        for i, sub in enumerate(subs[:3], 1):  # Show top 3
            print(f"{i}. {sub['name']} - Score: {sub['score']}/100")
            print(f"   💡 {sub['reason']}")
            print(f"   ⭐ Rating: {sub.get('rating', 'N/A')}")
            print(f"   📍 {sub.get('location', 'Unknown')}\n")
        
        top_pick = result.get('ai_top_pick', {})
        print(f"🤖 AI TOP PICK: {top_pick.get('name', 'N/A')} (Score: {top_pick.get('score', 0)}/100)")
        print(f"   {top_pick.get('reason', '')}\n")
        
        recommendation_id = result.get('recommendation_id')
        print(f"📝 Recommendation ID: {recommendation_id}")
        print("\n👤 YOUR TURN: Pick your preferred subcontractor")
        
        return recommendation_id, subs
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return None, []

def test_supplier_recommendations(opportunity_id: str, product: str):
    """Test 4: AI recommends suppliers"""
    print_section("TEST 4: Supplier Recommendations")
    
    print(f"🔍 AI searching for suppliers...")
    print(f"Product: {product}\n")
    
    response = requests.post(
        f"{BASE_URL}/ai/recommendations/suppliers",
        headers=HEADERS,
        json={
            "opportunity_id": opportunity_id,
            "product_description": product
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ AI Analysis Complete!\n")
        
        suppliers = result.get('recommended_suppliers', [])
        print(f"📊 Found {result.get('total_found', 0)} suppliers")
        print(f"🎯 Top {len(suppliers)} recommendations:\n")
        
        for i, sup in enumerate(suppliers[:5], 1):  # Show top 5
            print(f"{i}. {sup['name']} - Score: {sup['score']}/100")
            print(f"   💡 {sup['reason']}")
            print(f"   ⭐ Rating: {sup.get('rating', 'N/A')}")
            print(f"   💳 Terms: {sup.get('payment_terms', 'Unknown')}")
            print(f"   🏛️  GSA: {sup.get('gsa_schedule', 'No')}\n")
        
        top_pick = result.get('ai_top_pick', {})
        print(f"🤖 AI TOP PICK: {top_pick.get('name', 'N/A')} (Score: {top_pick.get('score', 0)}/100)")
        print(f"   {top_pick.get('reason', '')}\n")
        
        return result.get('recommendation_id'), suppliers
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return None, []

def test_compliance_calculator():
    """Test 5: Calculate compliance"""
    print_section("TEST 5: Compliance Calculator")
    
    print("📊 Calculating workshare compliance...")
    print("Contract: $500,000")
    print("Your work: $280,000")
    print("Subcontractor work: $180,000\n")
    
    response = requests.post(
        f"{BASE_URL}/ai/compliance/calculate",
        headers=HEADERS,
        json={
            "contract_value": 500000,
            "your_work_value": 280000,
            "subcontractor_work_value": 180000
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        compliance = result.get('compliance', {})
        
        print("✅ Compliance Check Complete!\n")
        print(f"📊 Your work: ${compliance['your_work']:,} ({compliance['your_percentage']}%)")
        print(f"📊 Subcontractor: ${compliance['subcontractor_work']:,} ({compliance['subcontractor_percentage']}%)")
        print(f"💰 Your margin: ${compliance['margin']:,} ({compliance['margin_percentage']}%)")
        print(f"\n{compliance['status']}")
        print(f"   {compliance['message']}\n")
        
        return compliance['compliant']
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return False

def test_pending_recommendations():
    """Test 6: Get pending recommendations"""
    print_section("TEST 6: Pending Recommendations")
    
    print("📋 Fetching pending AI recommendations...\n")
    
    response = requests.get(f"{BASE_URL}/ai/recommendations/pending")
    
    if response.status_code == 200:
        result = response.json()
        pending = result.get('pending_recommendations', [])
        
        print(f"📊 Found {result.get('count', 0)} pending recommendations\n")
        
        for rec in pending:
            print(f"📝 {rec.get('TYPE', 'Unknown')}")
            print(f"   ID: {rec.get('id', 'N/A')}")
            print(f"   Recommendation: {rec.get('RECOMMENDATION', 'N/A')}")
            print(f"   Confidence: {rec.get('CONFIDENCE', 0)}%")
            print(f"   Status: {rec.get('STATUS', 'Unknown')}")
            print(f"   Created: {rec.get('CREATED', 'Unknown')}\n")
        
        return pending
    else:
        print(f"❌ Error: {response.status_code}")
        print_result(response.json())
        return []

def main():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("  AI RECOMMENDATION & APPROVAL SYSTEM - TEST SUITE")
    print("🚀"*35)
    
    # Note: Replace with actual opportunity ID from your Airtable
    TEST_OPPORTUNITY_ID = "recTEST123"
    
    print("\n⚠️  NOTE: Replace TEST_OPPORTUNITY_ID with a real opportunity ID from Airtable")
    print(f"Current test ID: {TEST_OPPORTUNITY_ID}\n")
    
    try:
        # Test 1: Capability Gap Analysis
        rec_id = test_capability_gap_analysis(TEST_OPPORTUNITY_ID)
        
        if rec_id:
            input("\n⏸️  Press Enter to approve this recommendation...")
            
            # Test 2: Approve Recommendation
            test_approve_recommendation(
                rec_id,
                decision="approved",
                notes="AI recommendation looks good, let's partner on this"
            )
        
        input("\n⏸️  Press Enter to test subcontractor recommendations...")
        
        # Test 3: Subcontractor Recommendations
        rec_id, subs = test_subcontractor_recommendations(
            TEST_OPPORTUNITY_ID,
            ["Cybersecurity", "Penetration Testing"]
        )
        
        if rec_id and subs:
            input("\n⏸️  Press Enter to approve top subcontractor...")
            
            test_approve_recommendation(
                rec_id,
                decision="approved",
                notes=f"Going with AI's top pick: {subs[0]['name']}",
                selected_id=subs[0]['id']
            )
        
        input("\n⏸️  Press Enter to test supplier recommendations...")
        
        # Test 4: Supplier Recommendations
        test_supplier_recommendations(
            TEST_OPPORTUNITY_ID,
            "Dell Latitude 5520 Laptops"
        )
        
        input("\n⏸️  Press Enter to test compliance calculator...")
        
        # Test 5: Compliance Calculator
        test_compliance_calculator()
        
        input("\n⏸️  Press Enter to check pending recommendations...")
        
        # Test 6: Pending Recommendations
        test_pending_recommendations()
        
        print_section("✅ ALL TESTS COMPLETE")
        print("The AI Recommendation & Approval System is working!\n")
        print("Next steps:")
        print("1. Create the required Airtable tables (see AI_RECOMMENDATION_SYSTEM.md)")
        print("2. Test with real opportunity IDs")
        print("3. Integrate into your frontend")
        print("4. Start making faster, better decisions! 🚀\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the Flask server is running:")
        print("  python api_server.py\n")
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
