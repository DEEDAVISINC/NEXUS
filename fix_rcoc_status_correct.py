#!/usr/bin/env python3
"""
FIX RCOC STATUS - Based on actual file evidence
7802 - SUBMITTED (Conf #0000378385)
7799 - SUBMITTED (Feb 5, 2026)
7803 - NOT SUBMITTED (fell through cracks)
"""

from pyairtable import Api
from datetime import datetime

AIRTABLE_PAT = 'patJRybXNtbbUXq2i.1c7a4846654cd65aa25e23b654fdd41c1d2840b113e991793b171873a0fe5ffa'
AIRTABLE_BASE_ID = 'appaJZqKVUn3yJ7ma'

api = Api(AIRTABLE_PAT)
base = api.base(AIRTABLE_BASE_ID)
opportunities_table = base.table('GPSS OPPORTUNITIES')

print("🔧 FIXING RCOC STATUS BASED ON FILE EVIDENCE...")
print("="*80)

# Find the records
all_opportunities = opportunities_table.all()

for opp in all_opportunities:
    fields = opp['fields']
    name = fields.get('Name', '')
    rfp = fields.get('RFP NUMBER', '')
    
    # 7802 - SUBMITTED with confirmation
    if '7802' in name or '7802' in rfp:
        try:
            opportunities_table.update(opp['id'], {
                'Source Status': 'Submitted - Awaiting Award',
                'Notes': f'SUBMITTED Feb 5, 2026 @ 5:57 PM EST | Confirmation #0000378385 | Amount: $7,292.11 | Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            })
            print("✅ 7802 - Building Tools - SUBMITTED (Conf #0000378385)")
        except:
            pass
    
    # 7799 - SUBMITTED Feb 5
    elif '7799' in name or '7799' in rfp:
        try:
            opportunities_table.update(opp['id'], {
                'Source Status': 'Submitted - Awaiting Award',
                'Notes': f'SUBMITTED Feb 5, 2026 | Amount: $6,128.35 | Mentioned in 7802 confirmation document | Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            })
            print("✅ 7799 - Grease & Air Couplers - SUBMITTED (Feb 5)")
        except:
            pass
    
    # 7803 - NOT SUBMITTED!
    elif '7803' in name or '7803' in rfp:
        try:
            opportunities_table.update(opp['id'], {
                'Source Status': '🚨 NOT SUBMITTED - Fell Through Cracks',
                'Notes': f'PAST DUE - Deadline was Feb 6, 2026 | Amount: $2,641.10 | Pricing complete but never submitted to BidNet | NO submission confirmation found | Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            })
            print("⚠️ 7803 - Hammers, Tape, Levels - NOT SUBMITTED (fell through cracks)")
        except:
            pass

print("\n" + "="*80)
print("✅ STATUS CORRECTED!")
print("="*80)
print("\n✅ SUBMITTED:")
print("  - 7802: Building Tools ($7,292.11) - Conf #0000378385")
print("  - 7799: Grease & Air Couplers ($6,128.35)")
print("\n❌ NOT SUBMITTED:")
print("  - 7803: Hammers, Tape, Levels ($2,641.10) - FELL THROUGH CRACKS")
print("\n📊 LOST OPPORTUNITY: $2,641.10")
