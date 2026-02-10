#!/usr/bin/env python3
"""
Audit Document System Integration
Check what fields/tables are expected vs what exists
"""
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv
import json

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)

print("=" * 80)
print("DOCUMENT SYSTEM INTEGRATION AUDIT")
print("=" * 80)
print()

# ============================================================================
# 1. CHECK OPPORTUNITIES TABLE FOR DOCUMENT FIELDS
# ============================================================================

print("-" * 80)
print("1. GPSS OPPORTUNITIES TABLE - DOCUMENT FIELDS CHECK")
print("-" * 80)
print()

try:
    schema = base.schema()
    opportunities_table = next((t for t in schema.tables if t.name == 'GPSS OPPORTUNITIES'), None)
    
    if opportunities_table:
        print("✅ GPSS OPPORTUNITIES table exists")
        
        # Expected fields for document assembly
        expected_document_fields = {
            'Documents Package': 'Attachment',
            'Documents Checklist': 'Multiple Select',
            'Package Status': 'Single Select',
            'Package Assembled Date': 'Date',
            'Package Assembled By': 'Single Line Text'
        }
        
        print()
        print("Expected Document Fields:")
        
        existing_field_names = [f.name for f in opportunities_table.fields]
        
        missing_fields = []
        present_fields = []
        
        for field_name, field_type in expected_document_fields.items():
            if field_name in existing_field_names:
                actual_field = next(f for f in opportunities_table.fields if f.name == field_name)
                actual_type = actual_field.type
                print(f"   ✅ {field_name} ({field_type}) - EXISTS (actual: {actual_type})")
                present_fields.append(field_name)
            else:
                print(f"   ❌ {field_name} ({field_type}) - MISSING")
                missing_fields.append({'name': field_name, 'type': field_type})
        
        print()
        print(f"Summary: {len(present_fields)}/{len(expected_document_fields)} document fields exist")
        
        if missing_fields:
            print()
            print("⚠️  MISSING FIELDS - Add these to GPSS OPPORTUNITIES:")
            print()
            for field in missing_fields:
                print(f"Field Name: {field['name']}")
                print(f"Field Type: {field['type']}")
                if field['type'] == 'Multiple Select':
                    print("Options: W-9, EDWOSB, WOSB, Insurance, SAM, CAGE, CapStatement, References, Banking, WorkersComp, MBE")
                elif field['type'] == 'Single Select':
                    print("Options: Not Needed, Incomplete, Ready, Attached")
                print()
    
    else:
        print("❌ GPSS OPPORTUNITIES table not found")

except Exception as e:
    print(f"❌ Error checking OPPORTUNITIES table: {e}")

print()

# ============================================================================
# 2. CHECK FOR SUPPLIER_RFPS TABLE
# ============================================================================

print("-" * 80)
print("2. SUPPLIER_RFPS TABLE CHECK")
print("-" * 80)
print()

try:
    supplier_rfps_table = next((t for t in schema.tables if t.name == 'SUPPLIER_RFPS'), None)
    
    if supplier_rfps_table:
        print("✅ SUPPLIER_RFPS table exists")
        print()
        print("   Fields:")
        for field in supplier_rfps_table.fields:
            print(f"      - {field.name} ({field.type})")
    else:
        print("❌ SUPPLIER_RFPS table MISSING")
        print()
        print("⚠️  RFP Generator expects SUPPLIER_RFPS table with fields:")
        print("   - ddi_rfp_number (Single Line Text)")
        print("   - project_name (Single Line Text)")
        print("   - category (Single Select)")
        print("   - sanitized_location (Single Line Text)")
        print("   - scope_of_work (Long Text)")
        print("   - contract_value_min (Number)")
        print("   - contract_value_max (Number)")
        print("   - quote_due_date (Date)")
        print("   - contract_period (Single Line Text)")
        print("   - service_locations_count (Number)")
        print("   - insurance_requirements (Long Text)")
        print("   - status (Single Select: draft, sent, responses received)")
        print("   - pdf_generated_path (Single Line Text)")
        print("   - buyer_name (Single Line Text) - CONFIDENTIAL")
        print("   - buyer_rfp_number (Single Line Text) - CONFIDENTIAL")

except Exception as e:
    print(f"❌ Error checking SUPPLIER_RFPS table: {e}")

print()

# ============================================================================
# 3. CHECK FOR DOCUMENT GENERATOR INTEGRATION
# ============================================================================

print("-" * 80)
print("3. DOCUMENT GENERATOR INTEGRATION CHECK")
print("-" * 80)
print()

# Check if DocumentGenerator component exists
doc_gen_path = "/Users/deedavis/NEXUS BACKEND/nexus-frontend/src/components/systems/DocumentGenerator.tsx"
if os.path.exists(doc_gen_path):
    print("✅ DocumentGenerator.tsx exists")
else:
    print("❌ DocumentGenerator.tsx MISSING")

# Check if api_server has document endpoints
api_server_path = "/Users/deedavis/NEXUS BACKEND/api_server.py"
if os.path.exists(api_server_path):
    with open(api_server_path, 'r') as f:
        api_content = f.read()
        
    if 'assemble-package' in api_content:
        print("✅ Document assembly endpoint exists in api_server.py")
    else:
        print("❌ Document assembly endpoint MISSING from api_server.py")
        print("   Expected: POST /api/gpss/opportunities/:id/assemble-package")
    
    if '/api/gpss/documents/status' in api_content:
        print("✅ Document status endpoint exists in api_server.py")
    else:
        print("❌ Document status endpoint MISSING from api_server.py")
        print("   Expected: GET /api/gpss/documents/status")

print()

# ============================================================================
# 4. CHECK COMPANY_DOCUMENTS FOLDER
# ============================================================================

print("-" * 80)
print("4. COMPANY_DOCUMENTS FOLDER CHECK")
print("-" * 80)
print()

company_docs_path = "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS"
if os.path.exists(company_docs_path):
    print("✅ COMPANY_DOCUMENTS folder exists")
    print()
    
    required_docs = [
        "TAX_LEGAL/W-9_Form_2026.pdf",
        "CERTIFICATIONS/EDWOSB_Certificate.pdf",
        "CERTIFICATIONS/WOSB_Certificate.pdf",
        "INSURANCE/General_Liability_Certificate.pdf"
    ]
    
    print("   Required Documents:")
    for doc in required_docs:
        full_path = os.path.join(company_docs_path, doc)
        if os.path.exists(full_path):
            print(f"      ✅ {doc}")
        else:
            print(f"      ❌ {doc} - MISSING")
else:
    print("❌ COMPANY_DOCUMENTS folder MISSING")

print()

# ============================================================================
# 5. CHECK RFP GENERATOR API
# ============================================================================

print("-" * 80)
print("5. RFP GENERATOR API CHECK")
print("-" * 80)
print()

rfp_gen_path = "/Users/deedavis/NEXUS BACKEND/rfp_generator_api.py"
if os.path.exists(rfp_gen_path):
    print("✅ rfp_generator_api.py exists")
    
    # Check if it's running
    import subprocess
    result = subprocess.run(['lsof', '-ti', ':5002'], capture_output=True, text=True)
    if result.stdout.strip():
        print("✅ RFP Generator API is RUNNING on port 5002")
    else:
        print("❌ RFP Generator API is NOT running")
        print("   Start with: python3 rfp_generator_api.py")
else:
    print("❌ rfp_generator_api.py MISSING")

print()

# ============================================================================
# 6. CHECK QUOTE GENERATOR API
# ============================================================================

print("-" * 80)
print("6. QUOTE GENERATOR API CHECK")
print("-" * 80)
print()

quote_gen_files = [
    "/Users/deedavis/NEXUS BACKEND/auto_generate_quotes.py",
    "/Users/deedavis/NEXUS BACKEND/generate_enhanced_pdf.py",
    "/Users/deedavis/NEXUS BACKEND/generate_rfq_pdf.py"
]

for file_path in quote_gen_files:
    if os.path.exists(file_path):
        print(f"✅ {os.path.basename(file_path)} exists")
    else:
        print(f"❌ {os.path.basename(file_path)} MISSING")

# Check if running on port 5001
result = subprocess.run(['lsof', '-ti', ':5001'], capture_output=True, text=True)
if result.stdout.strip():
    print("✅ Quote Generator API is RUNNING on port 5001")
else:
    print("❌ Quote Generator API is NOT running")

print()

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================

print("=" * 80)
print("INTEGRATION GAPS SUMMARY")
print("=" * 80)
print()

print("CRITICAL MISSING INTEGRATIONS:")
print()

if missing_fields:
    print(f"1. ⚠️  GPSS OPPORTUNITIES missing {len(missing_fields)} document fields")
    print("   Impact: Document assembly won't work")
    print("   Fix: Add fields to Airtable (5 minutes)")
    print()

if not supplier_rfps_table:
    print("2. ⚠️  SUPPLIER_RFPS table doesn't exist")
    print("   Impact: RFP Generator can't save to database")
    print("   Fix: Create table in Airtable (10 minutes)")
    print()

if 'assemble-package' not in api_content:
    print("3. ⚠️  Document assembly endpoints not in api_server.py")
    print("   Impact: Frontend can't assemble packages")
    print("   Fix: Add endpoints to api_server.py (5 minutes)")
    print()

print()
print("RECOMMENDED ACTIONS:")
print()
print("1. Add missing fields to GPSS OPPORTUNITIES table")
print("2. Create SUPPLIER_RFPS table in Airtable")
print("3. Add document endpoints to api_server.py")
print("4. Upload required company documents")
print("5. Start RFP Generator API (if needed)")
print("6. Test end-to-end document workflows")
print()

print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
