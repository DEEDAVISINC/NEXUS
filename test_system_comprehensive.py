#!/usr/bin/env python3
"""
NEXUS COMPREHENSIVE SYSTEM TEST
Tests all critical endpoints with correct paths
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test(name, method, endpoint, data=None):
    """Test endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=data or {}, timeout=10)
        
        if r.status_code == 200:
            try:
                result = r.json()
                if isinstance(result, dict):
                    if 'opportunities' in result:
                        return f"✅ {name}: {len(result['opportunities'])} items"
                    elif 'prospects' in result:
                        return f"✅ {name}: {len(result['prospects'])} items"
                    elif 'invoices' in result:
                        return f"✅ {name}: {len(result['invoices'])} items"
                    elif 'portals' in result:
                        return f"✅ {name}: {len(result['portals'])} items"
                    elif 'leads' in result:
                        return f"✅ {name}: {len(result['leads'])} items"
                    else:
                        return f"✅ {name}: OK"
                elif isinstance(result, list):
                    return f"✅ {name}: {len(result)} items"
                else:
                    return f"✅ {name}: OK"
            except:
                return f"✅ {name}: Non-JSON OK"
        else:
            return f"❌ {name}: HTTP {r.status_code}"
    except Exception as e:
        return f"❌ {name}: {str(e)[:40]}"

print("=" * 80)
print("NEXUS COMPREHENSIVE SYSTEM TEST")
print("=" * 80)
print()

print("🔧 CORE SYSTEM")
print("-" * 80)
print(test("Health", "GET", "/health"))
print(test("Dashboard Stats", "GET", "/dashboard/stats"))
print(test("Dashboard Activity", "GET", "/dashboard/activity"))
print(test("Dashboard Alerts", "GET", "/dashboard/alerts"))
print()

print("📊 GPSS - GOVERNMENT PROCUREMENT")
print("-" * 80)
print(test("GPSS Opportunities", "GET", "/gpss/opportunities"))
print(test("GPSS Contacts", "GET", "/gpss/contacts"))
print(test("GPSS Stats", "GET", "/gpss/stats"))
print(test("GPSS Proposals", "GET", "/gpss/proposals"))
print(test("GPSS Suppliers", "GET", "/gpss/suppliers"))
print(test("GPSS Products", "GET", "/gpss/products"))
print(test("Mine GovCon", "POST", "/gpss/mining/search-govcon-api"))
print(test("Mine SAM.gov", "POST", "/gpss/mining/search-sam-api"))
print(test("Check RSS Feeds", "POST", "/gpss/mining/check-rss-feeds"))
print()

print("🏗️ ATLAS PM - PROJECT MANAGEMENT")
print("-" * 80)
print(test("ATLAS Tasks", "GET", "/atlas/tasks"))
print(test("ATLAS Projects", "GET", "/atlas/projects"))
print(test("ATLAS RFPs", "GET", "/atlas/rfps"))
print(test("ATLAS Change Orders", "GET", "/atlas/change-orders"))
print()

print("💼 DDCSS - DIRECT CLIENT SALES")
print("-" * 80)
print(test("DDCSS Prospects", "GET", "/ddcss/prospects"))
print(test("DDCSS Client Avatars", "GET", "/ddcss/client-avatars"))
print()

print("💰 VERTEX - FINANCIAL MANAGEMENT")
print("-" * 80)
print(test("VERTEX Invoices", "GET", "/vertex/invoices"))
print(test("VERTEX Expenses", "GET", "/vertex/expenses"))
print(test("AR Aging Report", "GET", "/vertex/invoices/aging"))
print()

print("📋 LBPC - LEAD & PROPOSAL BUILDER")
print("-" * 80)
print(test("LBPC Leads", "GET", "/lbpc/leads"))
print(test("LBPC Documents", "GET", "/lbpc/documents"))
print(test("LBPC Tasks", "GET", "/lbpc/tasks"))
print(test("LBPC Analytics", "GET", "/lbpc/analytics"))
print()

print("🔍 GBIS - GRANT/BID INTELLIGENCE")
print("-" * 80)
print(test("GBIS Opportunities", "GET", "/gbis/opportunities"))
print(test("GBIS Applications", "GET", "/gbis/applications"))
print(test("GBIS Pipeline", "GET", "/gbis/pipeline"))
print(test("GBIS Story Library", "GET", "/gbis/story-library"))
print(test("GBIS Stats", "GET", "/gbis/stats"))
print()

print("🌐 VENDOR PORTALS")
print("-" * 80)
print(test("Vendor Portals", "GET", "/vendor-portals"))
print(test("Mining Targets", "GET", "/gpss/mining/targets"))
print()

print("🧪 INVOICING")
print("-" * 80)
print(test("All Invoices", "GET", "/invoices"))
print()

print("=" * 80)
print("COMPREHENSIVE TEST COMPLETE")
print("=" * 80)
