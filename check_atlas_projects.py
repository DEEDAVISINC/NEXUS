"""
Check what projects are in the ATLAS PROJECTS table
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

print("="*70)
print("ATLAS PROJECTS - ALL RECORDS")
print("="*70)

try:
    projects_table = base.table('ATLAS PROJECTS')
    all_records = projects_table.all()
    
    print(f"\n✅ Total records: {len(all_records)}")
    
    if all_records:
        print("\nAll projects:")
        print("-"*70)
        
        for i, record in enumerate(all_records, 1):
            name = record['fields'].get('Project Name', 'Unknown')
            status = record['fields'].get('Status', 'N/A')
            budget = record['fields'].get('Budget', 0)
            
            print(f"{i:2}. {name}")
            print(f"    Status: {status} | Budget: ${budget:,.0f}")
    else:
        print("\n⚠️  No projects found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("   ATLAS PROJECTS table might not exist yet")

print("\n" + "="*70)
