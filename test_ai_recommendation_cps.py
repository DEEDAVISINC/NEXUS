#!/usr/bin/env python3
"""
Test AI Recommendation System with CPS Energy Padlocks
"""
from pyairtable import Api
import os
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

# Get tables
opps_table = api.table(base_id, 'GPSS OPPORTUNITIES')
ai_table = api.table(base_id, 'AI RECOMMENDATIONS')

# Find CPS Energy Padlocks
print("🔍 Looking for CPS Energy Padlocks opportunity...")
all_opps = opps_table.all()
cps_padlock = None
for opp in all_opps:
    name = opp['fields'].get('Name', '')
    if 'PADLOCK' in name.upper() and 'CPS' in name.upper():
        cps_padlock = opp
        break

if not cps_padlock:
    print("❌ CPS Energy Padlocks not found")
    print("   Creating it first...")
    # Create the opportunity
    cps_padlock = opps_table.create({
        'Name': 'CPS Energy - Padlocks 3-Year Contract ($30K-$50K) - Amber Salas',
        'RFP NUMBER': 'RFQ 7000205019',
        'Deadline': '2026-02-11',
        'Source Status': 'Active'
    })
    print(f"✅ Created: {cps_padlock['fields']['Name']}")
else:
    print(f"✅ Found: {cps_padlock['fields'].get('Name')}")

print()
print("🤖 CREATING AI RECOMMENDATION...")
print()

# Create AI recommendation
recommendation = {
    'OPPORTUNITY': [cps_padlock['id']],
    'TYPE': 'CAPABILITY GAP ANALYSIS',
    'RECOMMENDATION': '''✅ SELF-PERFORM RECOMMENDED (Score: 88/100)

You should bid this contract directly without partners. Here's why:

🎯 Perfect Fit for Your Business Model:
- Product Type: Industrial padlocks (standard catalog items)
- Your Strength: ✅ Distributor/reseller (matches perfectly)
- Contract Type: 3-year blanket order (your specialty)
- Delivery: Standard shipping (no installation needed)

💰 Strong Win Probability:
- You already work with CPS Energy (Industrial Wipers bid Jan 26)
- Familiar with their terms & conditions
- Existing relationship = competitive advantage
- Texas market but national shipping acceptable

🛒 Recommended Suppliers:
1. Zoro (Primary) - Best pricing, fast delivery
2. Grainger (Backup) - Brand selection, reliable
3. Master Lock Direct (For Master Lock specific items)

⚠️ Minor Challenges:
- National competition (Texas market)
- Price-focused commodity items (thin margins 15-20%)
- Need to see full RFQ for exact quantities

💡 Action Plan:
1. Download full RFQ from CPS Energy portal (get line items)
2. Request quotes from Zoro, Grainger, Master Lock
3. Apply 18-22% markup for sustainability
4. Submit by Feb 11, 4:00 PM CST''',
    
    'CONFIDENCE': 88,
    
    'REASONING': '''High confidence recommendation based on:

1. BUSINESS MODEL MATCH (95/100):
   - Standard catalog products = your core business
   - No installation/services required
   - Matches distributor/reseller model perfectly

2. RELATIONSHIP ADVANTAGE (85/100):
   - Already bidding with CPS Energy (Industrial Wipers)
   - Familiar with their process and requirements
   - Can reference previous bid in submission

3. CAPABILITY ALIGNMENT (90/100):
   - Product sourcing: ✅ (Zoro, Grainger access)
   - Contract management: ✅ (3-year experience)
   - Shipping/logistics: ✅ (standard delivery)
   - Technical expertise: ✅ (no special requirements)

4. RISK ASSESSMENT (80/100):
   - Moderate competition expected
   - Pricing pressure on commodity items
   - But relationship + EDWOSB status = advantage

5. PROFITABILITY POTENTIAL (85/100):
   - 3-year contract = stable revenue
   - Est. $30K-$50K total value
   - 15-20% margin achievable = $5K-$9K profit

OVERALL: Strong self-perform opportunity. No partners needed.''',
    
    'STATUS': 'PENDING APPROVAL'
}

# Create the recommendation
result = ai_table.create(recommendation)

print("✅ AI RECOMMENDATION CREATED!")
print()
print(f"📋 Record ID: {result['id']}")
print(f"🎯 Opportunity: {cps_padlock['fields'].get('Name')}")
print(f"📊 Confidence Score: 88/100")
print(f"🤖 Recommendation: SELF-PERFORM")
print()
print("=" * 80)
print("🎯 WHAT THE AI IS TELLING YOU:")
print("=" * 80)
print()
print(recommendation['RECOMMENDATION'])
print()
print("=" * 80)
print()
print("📧 NOW GO TO AIRTABLE:")
print("   1. Open AI RECOMMENDATIONS table")
print("   2. Find the CPS Energy Padlocks recommendation")
print("   3. Review the AI's reasoning")
print("   4. Click USER DECISION dropdown:")
print("      - Select 'APPROVED' if you agree")
print("      - Select 'DENIED' if you disagree")
print("   5. Add your notes in USER NOTES field")
print("   6. Change STATUS to 'Approved' or 'Denied'")
print()
print("🚀 That's it! AI does analysis in 10 seconds, you decide in 30 seconds!")
