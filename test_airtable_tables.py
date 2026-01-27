#!/usr/bin/env python3
"""
Test which Airtable tables actually exist in your base
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print("❌ Missing Airtable credentials in .env file!")
    print("Need: AIRTABLE_API_KEY and AIRTABLE_BASE_ID")
    exit(1)

print("=" * 60)
print("🔍 AIRTABLE TABLE CHECKER")
print("=" * 60)
print()
print(f"Base ID: {base_id[:8]}...{base_id[-4:]}")
print()
print("Testing which tables actually exist...")
print()

# Tables that NEXUS code references
test_tables = [
    ("GPSS Opportunities", "Core - RFPs and solicitations"),
    ("GPSS Suppliers", "Core - Supplier database"),
    ("GPSS Contacts", "Core - Government contacts"),
    ("GPSS Products", "Core - Services/products offered"),
    ("GPSS Proposals", "AI-generated proposals"),
    ("Pricing History", "Pricing intelligence"),
    ("Cost Templates", "Service pricing templates"),
    
    ("ATLAS Projects", "Project management"),
    ("ATLAS Tasks", "Project tasks"),
    ("ATLAS Change Orders", "Change requests"),
    ("ATLAS RFPs", "RFP tracking"),
    
    ("DDCSS Prospects", "Corporate prospects"),
    ("DDCSS Client Avatars", "Ideal customer profiles"),
    
    ("LBPC Leads", "Surplus recovery leads"),
    ("LBPC Documents", "Generated documents"),
    ("LBPC Tasks", "Automated workflows"),
    ("LBPC Templates", "Document templates"),
    
    ("Invoices", "Universal billing"),
    ("Contacts", "Shared contacts"),
    
    ("AI RECOMMENDATIONS", "AI suggestions"),
    ("AI Conversations", "Conversation storage"),
    ("Company Capabilities", "What you can do"),
    
    ("CapabilityStatements", "Generated cap statements"),
    ("Officer Outreach Tracking", "Contracting officer relationships"),
    
    ("GPSS Subcontractors", "Subcontractor database"),
    ("GPSS Subcontractor Quotes", "Sub quotes"),
    ("GPSS Subcontractor Compliance", "Compliance docs"),
    
    ("Quote Requests", "Supplier quote tracking"),
    
    ("Contracts", "Post-award contracts"),
    ("Purchase Orders", "Supplier POs"),
    ("Contract Deliveries", "Delivery tracking"),
    ("Contract Interactions", "Communications log"),
    ("Contract Issues", "Problem tracking"),
]

existing = []
missing = []

for table_name, description in test_tables:
    try:
        api_instance = Api(api_key)
        table = api_instance.table(base_id, table_name)
        
        # Try to fetch one record to verify access
        records = table.all(max_records=1)
        
        existing.append((table_name, description, len(records) if records else 0))
        print(f"✅ {table_name:<35} - {description}")
    except Exception as e:
        missing.append((table_name, description))
        error_msg = str(e)
        if "NOT_FOUND" in error_msg or "Could not find table" in error_msg:
            print(f"❌ {table_name:<35} - NOT CREATED YET")
        else:
            print(f"⚠️  {table_name:<35} - ERROR: {str(e)[:40]}")

print()
print("=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print()
print(f"✅ Tables that EXIST: {len(existing)}")
print(f"❌ Tables that are MISSING: {len(missing)}")
print()

if existing:
    print("✅ EXISTING TABLES:")
    for name, desc, count in existing:
        record_text = f"({count} record)" if count == 1 else f"({count} records)" if count > 0 else "(empty)"
        print(f"   • {name} {record_text}")
    print()

if missing:
    print("❌ MISSING TABLES (Need to create these):")
    for name, desc in missing:
        print(f"   • {name} - {desc}")
    print()
    print("👉 These tables have schemas written but aren't created yet!")
    print("👉 You need to manually create them in Airtable.com")
    print()

print("=" * 60)
print()

if len(existing) == 0:
    print("🚨 NO TABLES FOUND!")
    print()
    print("This means either:")
    print("1. You haven't created any tables yet in Airtable")
    print("2. Your AIRTABLE_BASE_ID is wrong")
    print("3. Your AIRTABLE_API_KEY doesn't have access")
    print()
    print("Next steps:")
    print("1. Go to https://airtable.com")
    print("2. Check your base")
    print("3. Verify tables exist")
    print("4. Check .env has correct Base ID")
    
elif len(existing) < 10:
    print("⚠️  PARTIAL SETUP")
    print()
    print(f"You have {len(existing)} tables but NEXUS needs {len(test_tables)} total.")
    print()
    print("Recommendation:")
    print("1. Focus on core tables first (Opportunities, Suppliers, Invoices)")
    print("2. Add other tables as needed")
    print("3. Follow schema documentation to create missing tables")
    
elif len(missing) > 0:
    print("🎯 GOOD PROGRESS!")
    print()
    print(f"You have {len(existing)} tables created!")
    print(f"Still need {len(missing)} more for complete system.")
    print()
    print("Missing tables are documented in:")
    print("• CONTRACT_COMMAND_CENTER_SPEC.md (5 tables)")
    print("• QUOTE_REQUESTS_AIRTABLE_SCHEMA.md (1 table)")
    
else:
    print("🎉 COMPLETE!")
    print()
    print("All tables exist! NEXUS is ready to use!")

print()
print("=" * 60)
