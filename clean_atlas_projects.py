"""
Clean up empty/mock records from ATLAS PROJECTS table
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
print("CLEANING ATLAS PROJECTS TABLE")
print("="*70)

try:
    projects_table = base.table('ATLAS PROJECTS')
    all_records = projects_table.all()
    
    print(f"\n📊 Total records before cleanup: {len(all_records)}")
    
    deleted = 0
    
    print("\n🗑️  Deleting empty/mock records...")
    print("-"*70)
    
    for record in all_records:
        name = record['fields'].get('Project Name', '')
        
        # Delete if name is empty or "Unknown"
        if not name or name == 'Unknown':
            try:
                projects_table.delete(record['id'])
                print(f"   ❌ Deleted empty record (ID: {record['id']})")
                deleted += 1
            except Exception as e:
                print(f"   ⚠️  Error deleting record: {e}")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\n🗑️  Deleted: {deleted} empty records")
    print(f"📊 Remaining: {len(all_records) - deleted} projects")
    
    print("\n✅ ATLAS PROJECTS table is now clean!")
    print("   Projects will be auto-created when opportunities are won")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70)
