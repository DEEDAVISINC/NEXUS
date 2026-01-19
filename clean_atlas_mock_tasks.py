#!/usr/bin/env python3
"""
Delete empty/mock task records from ATLAS TASKS table
"""
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

api = Api(API_KEY)
table = api.table(BASE_ID, 'ATLAS TASKS')

print("=" * 70)
print("CLEANING ATLAS TASKS - Removing Mock/Empty Records")
print("=" * 70)
print()

# Get all records
records = table.all()
print(f"Found {len(records)} task records")
print()

# Delete empty/mock records
deleted_count = 0
for record in records:
    fields = record['fields']
    
    # Check if it's an empty/mock record (only has Last Updated or no important fields)
    important_fields = ['Task Name', 'Title', 'Description', 'Status', 'Owner', 'Project']
    has_important_data = any(fields.get(field) for field in important_fields)
    
    if not has_important_data:
        print(f"Deleting empty record: {record['id']}")
        table.delete(record['id'])
        deleted_count += 1

print()
print(f"✅ Deleted {deleted_count} empty/mock task records")
print()
print("=" * 70)
print("ATLAS TASKS CLEANED")
print("=" * 70)
