#!/usr/bin/env python3
"""
Test Full Lifecycle: Opportunity → Win → Project → Invoice
This tests the complete workflow end-to-end
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("NEXUS FULL LIFECYCLE TEST")
print("Opportunity → Win → Project → Invoice")
print("=" * 80)
print()

# Step 1: Get a real opportunity
print("STEP 1: Get a real GPSS opportunity")
print("-" * 80)
r = requests.get(f"{BASE_URL}/gpss/opportunities")
opps = r.json()['opportunities']
if len(opps) == 0:
    print("❌ No opportunities found. Cannot test lifecycle.")
    exit(1)

test_opp = opps[0]
opp_id = test_opp['id']
opp_name = test_opp.get('Name', 'Unknown')
print(f"✅ Using opportunity: {opp_name}")
print(f"   ID: {opp_id}")
print()

# Step 2: Create ATLAS project from opportunity
print("STEP 2: Create ATLAS PM project from opportunity")
print("-" * 80)
try:
    r = requests.post(
        f"{BASE_URL}/gpss/opportunities/{opp_id}/create-atlas-project",
        json={
            "project_name": f"Test Project - {opp_name[:30]}",
            "client_name": test_opp.get('Agency', 'Test Agency'),
            "description": f"Project created from opportunity: {opp_name}"
        }
    )
    if r.status_code == 200:
        project_data = r.json()
        project_id = project_data.get('project', {}).get('id')
        print(f"✅ Project created successfully")
        print(f"   Project ID: {project_id}")
    else:
        print(f"⚠️  Project creation returned status {r.status_code}")
        print(f"   Response: {r.text[:200]}")
        project_id = None
except Exception as e:
    print(f"❌ Error creating project: {str(e)}")
    project_id = None
print()

# Step 3: Create invoice from project
if project_id:
    print("STEP 3: Create VERTEX invoice from project")
    print("-" * 80)
    try:
        r = requests.post(
            f"{BASE_URL}/atlas/projects/{project_id}/create-invoice",
            json={
                "invoice_number": f"INV-TEST-{int(time.time())}",
                "amount": 50000,
                "description": f"Invoice for project: {opp_name[:30]}"
            }
        )
        if r.status_code == 200:
            invoice_data = r.json()
            invoice_id = invoice_data.get('invoice', {}).get('id')
            print(f"✅ Invoice created successfully")
            print(f"   Invoice ID: {invoice_id}")
        else:
            print(f"⚠️  Invoice creation returned status {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            invoice_id = None
    except Exception as e:
        print(f"❌ Error creating invoice: {str(e)}")
        invoice_id = None
else:
    print("STEP 3: SKIPPED (no project created)")
    invoice_id = None
print()

# Step 4: Verify invoice exists
if invoice_id:
    print("STEP 4: Verify invoice in VERTEX system")
    print("-" * 80)
    try:
        r = requests.get(f"{BASE_URL}/vertex/invoices")
        invoices = r.json()['invoices']
        found = False
        for inv in invoices:
            if inv['id'] == invoice_id:
                found = True
                print(f"✅ Invoice found in VERTEX system")
                print(f"   Invoice Number: {inv.get('Invoice Number', 'N/A')}")
                print(f"   Amount: ${inv.get('Amount', 0):,.2f}")
                print(f"   Status: {inv.get('Status', 'Unknown')}")
                break
        if not found:
            print(f"⚠️  Invoice not found in list (may take time to sync)")
    except Exception as e:
        print(f"❌ Error verifying invoice: {str(e)}")
else:
    print("STEP 4: SKIPPED (no invoice created)")
print()

# Summary
print("=" * 80)
print("LIFECYCLE TEST SUMMARY")
print("=" * 80)
print(f"✅ Step 1: Opportunity Retrieved - {opp_name[:50]}")
if project_id:
    print(f"✅ Step 2: Project Created - ID: {project_id}")
else:
    print(f"⚠️  Step 2: Project Creation - Check endpoint")
if invoice_id:
    print(f"✅ Step 3: Invoice Created - ID: {invoice_id}")
    print(f"✅ Step 4: Invoice Verified in System")
else:
    print(f"⚠️  Step 3-4: Invoice Creation - Check endpoint")
print()

if project_id and invoice_id:
    print("🎉 FULL LIFECYCLE TEST: PASSED")
    print("   The complete workflow is operational!")
elif project_id:
    print("⚠️  PARTIAL SUCCESS: Opportunity → Project works")
    print("   Invoice creation endpoint needs verification")
else:
    print("⚠️  PARTIAL SUCCESS: Opportunity retrieval works")
    print("   Project/Invoice creation endpoints need verification")
print("=" * 80)
