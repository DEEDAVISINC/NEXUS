#!/usr/bin/env python3
"""
CLEAN AIRTABLE: MICHIGAN ONLY
Delete all non-Michigan opportunities to reduce clutter

WARNING: This deletes 2,800+ records!
Creates backup first.

Created: February 5, 2026
"""

from pyairtable import Api
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS OPPORTUNITIES')

print("=" * 80)
print("🧹 CLEAN AIRTABLE: MICHIGAN OPPORTUNITIES ONLY")
print("=" * 80)
print()

print("⚠️  WARNING: This will DELETE non-Michigan opportunities!")
print()

# 1. Backup first
print("📦 Creating backup...")
all_records = table.all()
backup_file = f"airtable_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

backup_data = {
    'timestamp': datetime.now().isoformat(),
    'record_count': len(all_records),
    'records': [{'id': r['id'], 'fields': r['fields']} for r in all_records]
}

with open(backup_file, 'w') as f:
    json.dump(backup_data, f, indent=2)

print(f"✅ Backup saved: {backup_file}")
print(f"📊 Backed up {len(all_records)} records")
print()

# 2. Identify Michigan opportunities
michigan_keywords = [
    'rcoc',
    'road commission',
    'wayne county',
    'oakland county',
    'macomb county',
    'detroit',
    'canton township',
    'canton twp',
    'warren',
    'sterling heights',
    'troy',
    'dearborn',
    'livonia',
    'westland',
    'farmington hills',
    'farmington',
    'bloomfield',
    'auburn hills',
    'novi',
    'southfield',
    'pontiac',
    'royal oak',
    'michigan',
    ' mi ',
    'shelby township',
    'macomb township',
    'clinton township'
]

keep_records = []
delete_records = []

print("🔍 Analyzing opportunities...")
print()

for r in all_records:
    fields = r['fields']
    name = fields.get('Name', '').lower()
    agency = fields.get('Agency Name', '').lower()
    location = f"{fields.get('Place of Performance City', '')} {fields.get('Place of Performance State', '')}".lower()
    set_aside = fields.get('Set-Aside Type', '').upper()
    status = fields.get('Status', 'New')
    
    # Keep if Michigan-related or EDWOSB
    is_michigan = any(keyword in name or keyword in agency or keyword in location 
                      for keyword in michigan_keywords)
    is_edwosb = 'EDWOSB' in set_aside
    is_active = status in ['New', 'Pursuing', 'Submitted']
    
    if is_michigan and is_active:
        keep_records.append(r)
    elif is_edwosb and is_active:
        keep_records.append(r)
    else:
        delete_records.append(r)

print(f"✅ Keep: {len(keep_records)} Michigan/EDWOSB opportunities")
print(f"❌ Delete: {len(delete_records)} irrelevant opportunities")
print()

# Show what we're keeping
print("=" * 80)
print("📋 KEEPING THESE OPPORTUNITIES:")
print("=" * 80)
print()

for i, r in enumerate(keep_records[:20], 1):  # Show first 20
    fields = r['fields']
    print(f"{i}. {fields.get('Name', 'Untitled')[:75]}")
    print(f"   Status: {fields.get('Status', 'New')}")
    print(f"   Set-Aside: {fields.get('Set-Aside Type', 'None')}")
    print()

if len(keep_records) > 20:
    print(f"... and {len(keep_records) - 20} more")
    print()

# Confirm deletion
print("=" * 80)
print("⚠️  CONFIRMATION REQUIRED")
print("=" * 80)
print()
print(f"This will DELETE {len(delete_records)} opportunities.")
print(f"This will KEEP {len(keep_records)} Michigan/EDWOSB opportunities.")
print()
print("Backup saved to:", backup_file)
print()
print("Type 'DELETE' to proceed (or anything else to cancel):")
confirmation = input("> ")

if confirmation.strip() != 'DELETE':
    print()
    print("❌ Cancelled. No records deleted.")
    print()
    exit(0)

# 3. Delete non-Michigan opportunities
print()
print("🗑️  Deleting non-Michigan opportunities...")
print()

deleted_count = 0
batch_size = 10  # Delete in batches to avoid rate limits

for i in range(0, len(delete_records), batch_size):
    batch = delete_records[i:i+batch_size]
    record_ids = [r['id'] for r in batch]
    
    try:
        for record_id in record_ids:
            table.delete(record_id)
            deleted_count += 1
            
            if deleted_count % 100 == 0:
                print(f"   Deleted {deleted_count}/{len(delete_records)}...")
    except Exception as e:
        print(f"   ⚠️  Error deleting batch: {e}")
        continue

print()
print("=" * 80)
print("✅ CLEANUP COMPLETE!")
print("=" * 80)
print()
print(f"✅ Deleted: {deleted_count} opportunities")
print(f"✅ Kept: {len(keep_records)} Michigan/EDWOSB opportunities")
print(f"✅ Backup: {backup_file}")
print()
print("🎯 Your GPSS OPPORTUNITIES table now shows only Michigan-relevant bids!")
print()
print("=" * 80)
