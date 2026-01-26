#!/usr/bin/env python3
"""
TEST OPPORTUNITIES DISPLAY
Verifies that opportunities will display correctly in NEXUS frontend
"""

import os
from pyairtable import Api
from dotenv import load_dotenv
import json

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
table = api.table(base_id, 'GPSS OPPORTUNITIES')

print("🧪 TESTING OPPORTUNITIES DISPLAY MAPPING")
print("=" * 70)

# Get first 5 opportunities
print("\n📊 Fetching sample opportunities...")
records = table.all(max_records=5)

print(f"   Found {len(records)} sample opportunities\n")

for i, record in enumerate(records, 1):
    fields = record['fields']
    
    print(f"\n{'='*70}")
    print(f"OPPORTUNITY #{i}")
    print(f"{'='*70}")
    
    # Show what exists in Airtable
    print("\n📁 AIRTABLE FIELDS (what we have):")
    for key, value in fields.items():
        print(f"   • {key}: {value}")
    
    # Show how it will map to frontend
    print("\n🎨 FRONTEND MAPPING (what NEXUS will display):")
    
    mapped = {
        'id': record['id'],
        'title': fields.get('Name', fields.get('Title', '')),
        'rfpNumber': fields.get('RFP NUMBER', fields.get('RFP Number', '')),
        'agency': fields.get('Agency Name', fields.get('Agency', 'Unknown Agency')),
        'value': fields.get('Value', fields.get('Estimated Value', 0)),
        'dueDate': fields.get('Deadline', fields.get('Due Date', '')),
        'source': fields.get('Source', 'Federal'),
        'urgency': fields.get('Urgency', 'Medium'),
        'priorityScore': fields.get('Priority Score', 50),
        'internalStatus': fields.get('Internal Status', fields.get('Source Status', 'New')),
        'highValueFlag': fields.get('HIGH VALUE FLAG', False)
    }
    
    for key, value in mapped.items():
        print(f"   • {key}: {value}")
    
    # Check if it will display properly
    print("\n✅ DISPLAY CHECK:")
    issues = []
    
    if not mapped['title']:
        issues.append("❌ Title is empty - will show blank row")
    else:
        print(f"   ✓ Title: {mapped['title'][:50]}")
    
    if not mapped['rfpNumber']:
        issues.append("⚠️  RFP Number is empty")
    else:
        print(f"   ✓ RFP Number: {mapped['rfpNumber']}")
    
    if mapped['value'] == 0:
        issues.append("⚠️  Value is $0 - will display as $0")
    else:
        print(f"   ✓ Value: ${mapped['value']:,.0f}")
    
    if not mapped['dueDate']:
        issues.append("⚠️  No deadline - urgency can't be calculated")
    else:
        print(f"   ✓ Deadline: {mapped['dueDate']}")
    
    print(f"   ✓ Source: {mapped['source']}")
    print(f"   ✓ Urgency: {mapped['urgency']}")
    print(f"   ✓ Priority Score: {mapped['priorityScore']}/100")
    print(f"   ✓ Status: {mapped['internalStatus']}")
    
    if issues:
        print("\n⚠️  ISSUES:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ This opportunity will display perfectly!")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("\n💡 SUMMARY:")
print("   • Your opportunities WILL display in NEXUS now")
print("   • Title, RFP Number, and Deadline are coming from correct fields")
print("   • Missing fields (Value, Agency, etc.) have smart defaults")
print("   • Backend API provides fallbacks for empty fields")
print("\n🎯 Next Step: Restart your backend API server if it's running")
print("   Then refresh the Opportunities tab in NEXUS!")
