#!/usr/bin/env python3
"""
Get AI Recommendation for Any Opportunity
Usage: python get_ai_recommendation.py "opportunity name or keyword"
"""
import sys
from pyairtable import Api
import os
from dotenv import load_dotenv

load_dotenv()

# Get search term from command line
if len(sys.argv) < 2:
    print("❌ Please provide an opportunity name or keyword")
    print("   Example: python get_ai_recommendation.py 'CPS Energy'")
    print("   Example: python get_ai_recommendation.py 'RCOC 7731'")
    sys.exit(1)

search_term = ' '.join(sys.argv[1:]).upper()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opps_table = api.table(base_id, 'GPSS OPPORTUNITIES')
ai_table = api.table(base_id, 'AI RECOMMENDATIONS')

# Find the opportunity
print(f"🔍 Searching for opportunities matching: '{search_term}'...")
print()

all_opps = opps_table.all()
matching = []
for opp in all_opps:
    name = opp['fields'].get('Name', '').upper()
    rfp_num = opp['fields'].get('RFP NUMBER', '').upper()
    if search_term in name or search_term in rfp_num:
        matching.append(opp)

if not matching:
    print(f"❌ No opportunities found matching '{search_term}'")
    print()
    print("💡 Try searching for:")
    print("   - Client name (e.g., 'RCOC', 'CPS Energy')")
    print("   - RFP number (e.g., '7731', '7000205019')")
    print("   - Product type (e.g., 'Wipers', 'Padlocks')")
    sys.exit(1)

if len(matching) > 1:
    print(f"✅ Found {len(matching)} matching opportunities:")
    print()
    for i, opp in enumerate(matching, 1):
        print(f"{i}. {opp['fields'].get('Name')}")
    print()
    choice = input("Which one? (enter number): ")
    try:
        selected = matching[int(choice) - 1]
    except (ValueError, IndexError):
        print("❌ Invalid choice")
        sys.exit(1)
else:
    selected = matching[0]

print(f"✅ Selected: {selected['fields'].get('Name')}")
print()

# Check if recommendation already exists
existing = ai_table.all(formula=f"{{OPPORTUNITY}}='{selected['fields']['Name']}'")
if existing:
    print("⚠️  AI recommendation already exists for this opportunity!")
    print()
    print(f"📋 Existing Recommendation:")
    print(f"   Type: {existing[0]['fields'].get('TYPE')}")
    print(f"   Confidence: {existing[0]['fields'].get('CONFIDENCE')}/100")
    print(f"   Status: {existing[0]['fields'].get('STATUS')}")
    print()
    print(f"   {existing[0]['fields'].get('RECOMMENDATION', '')[:200]}...")
    print()
    create_new = input("Create a new recommendation anyway? (y/n): ")
    if create_new.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)

# Create AI recommendation
print("🤖 ANALYZING OPPORTUNITY...")
print()

# Simple AI logic based on opportunity characteristics
name = selected['fields'].get('Name', '').upper()
rfp_num = selected['fields'].get('RFP NUMBER', '').upper()

# Determine if self-perform or partner needed
needs_partner = False
partner_reason = ""

if any(keyword in name for keyword in ['CONSTRUCTION', 'INSTALLATION', 'ENGINEERING', 'DESIGN', 'CYBERSECURITY', 'IT SERVICES']):
    needs_partner = True
    partner_reason = "Requires specialized services outside distributor/reseller model"

# Calculate confidence
if needs_partner:
    confidence = 75
    recommendation_text = f"⚠️ PARTNER RECOMMENDED (Score: {confidence}/100)\n\nThis opportunity requires specialized capabilities. Consider teaming with qualified partners."
else:
    confidence = 85
    recommendation_text = f"✅ SELF-PERFORM RECOMMENDED (Score: {confidence}/100)\n\nThis opportunity matches your distributor/reseller business model. You can bid this directly."

# Add details
recommendation_text += f"\n\n🎯 Opportunity Details:\n"
recommendation_text += f"- Name: {selected['fields'].get('Name')}\n"
recommendation_text += f"- RFP #: {selected['fields'].get('RFP NUMBER', 'N/A')}\n"
recommendation_text += f"- Deadline: {selected['fields'].get('Deadline', 'N/A')}\n"

recommendation_text += "\n\n💡 Next Steps:\n"
recommendation_text += "1. Review full solicitation documents\n"
recommendation_text += "2. Identify product specifications\n"
recommendation_text += "3. Request supplier quotes\n"
recommendation_text += "4. Calculate pricing with appropriate markup\n"
recommendation_text += "5. Submit bid before deadline"

reasoning = f"AI analysis based on opportunity name and characteristics.\n\n"
reasoning += f"Business Model Match: {'LOW - needs partners' if needs_partner else 'HIGH - matches your model'}\n"
reasoning += f"Confidence: {confidence}/100\n\n"
if needs_partner:
    reasoning += f"Reason for partnering: {partner_reason}"

# Create the recommendation
rec = {
    'OPPORTUNITY': [selected['id']],
    'TYPE': 'CAPABILITY GAP ANALYSIS',
    'RECOMMENDATION': recommendation_text,
    'CONFIDENCE': confidence,
    'REASONING': reasoning,
    'STATUS': 'PENDING APPROVAL'
}

result = ai_table.create(rec)

print("✅ AI RECOMMENDATION CREATED!")
print()
print("=" * 80)
print(recommendation_text)
print("=" * 80)
print()
print(f"📋 Record ID: {result['id']}")
print(f"📊 Confidence: {confidence}/100")
print()
print("📧 GO TO AIRTABLE:")
print("   1. Open AI RECOMMENDATIONS table")
print("   2. Find the new recommendation")
print("   3. Review and approve/deny")
print()
print("🚀 AI does the analysis, you make the decision!")
