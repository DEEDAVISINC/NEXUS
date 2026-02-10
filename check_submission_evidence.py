#!/usr/bin/env python3
"""
Check for EVIDENCE of submission in Airtable - confirmation numbers, notes, etc.
"""

from pyairtable import Api

AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("🔍 CHECKING FOR SUBMISSION EVIDENCE...")
print("="*80)

# Get the three bids in question
bids_to_check = ['7799', '7802', '7803']

all_opportunities = opportunities_table.all()

for bid_num in bids_to_check:
    print(f"\n📋 RCOC {bid_num}:")
    
    for opp in all_opportunities:
        fields = opp['fields']
        rfp = fields.get('RFP NUMBER', '')
        name = fields.get('Name', '')
        
        if bid_num in rfp or bid_num in name:
            status = fields.get('Source Status', 'NO STATUS')
            notes = fields.get('Notes', 'NO NOTES')
            
            print(f"   Name: {name}")
            print(f"   Status: {status}")
            print(f"   Notes: {notes}")
            
            # Look for evidence
            evidence = []
            if 'confirmation' in notes.lower() or 'conf' in notes.lower():
                evidence.append("✅ HAS CONFIRMATION NUMBER")
            if 'submitted' in status.lower() and 'conf' in status.lower():
                evidence.append("✅ STATUS HAS CONFIRMATION")
            if status == 'Active' or status == 'NO STATUS':
                evidence.append("❌ NO SUBMISSION EVIDENCE")
            
            if evidence:
                print(f"   Evidence: {', '.join(evidence)}")
            
            break

print("\n" + "="*80)
print("❌ I CANNOT DETERMINE FROM THE SYSTEM WHICH WAS ACTUALLY SUBMITTED")
print("="*80)
print("\nThe system does NOT have BidNet submission records.")
print("I can only see what's in Airtable, which was manually entered.")
print("\nYOU need to tell me which ones were submitted to BidNet!")
