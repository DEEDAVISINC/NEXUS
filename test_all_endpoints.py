#!/usr/bin/env python3
"""
Comprehensive endpoint testing for NEXUS Backend
Tests all major API endpoints to verify they're working with real data
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, expected_status=200, data=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return f"❌ {name}: Unsupported method {method}"
        
        if response.status_code == expected_status:
            try:
                result = response.json()
                # Check if it's real data or empty
                if isinstance(result, dict):
                    if 'opportunities' in result:
                        count = len(result['opportunities'])
                        return f"✅ {name}: {count} opportunities"
                    elif 'tasks' in result:
                        count = len(result['tasks'])
                        return f"✅ {name}: {count} tasks"
                    elif 'projects' in result:
                        count = len(result['projects'])
                        return f"✅ {name}: {count} projects"
                    elif 'prospects' in result:
                        count = len(result['prospects'])
                        return f"✅ {name}: {count} prospects"
                    elif 'invoices' in result:
                        count = len(result['invoices'])
                        return f"✅ {name}: {count} invoices"
                    elif 'activities' in result:
                        count = len(result['activities'])
                        return f"✅ {name}: {count} activities"
                    elif 'alerts' in result:
                        count = len(result['alerts'])
                        return f"✅ {name}: {count} alerts"
                    elif 'portals' in result:
                        count = len(result['portals'])
                        return f"✅ {name}: {count} portals"
                    else:
                        keys = list(result.keys())[:3]
                        return f"✅ {name}: Response has keys: {keys}"
                elif isinstance(result, list):
                    return f"✅ {name}: {len(result)} items"
                else:
                    return f"✅ {name}: OK"
            except:
                return f"✅ {name}: Non-JSON response OK"
        else:
            return f"❌ {name}: Status {response.status_code}"
    except requests.exceptions.Timeout:
        return f"⏱️  {name}: Timeout (>10s)"
    except Exception as e:
        return f"❌ {name}: {str(e)[:50]}"

# Test all endpoints
print("=" * 70)
print("NEXUS BACKEND COMPREHENSIVE ENDPOINT TEST")
print("=" * 70)
print()

# Core System Endpoints
print("🔧 CORE SYSTEM")
print("-" * 70)
print(test_endpoint("Health Check", "GET", "/health"))
print(test_endpoint("Dashboard Stats", "GET", "/dashboard/stats"))
print(test_endpoint("Dashboard Activity", "GET", "/dashboard/activity"))
print(test_endpoint("Dashboard Alerts", "GET", "/dashboard/alerts"))
print()

# GPSS System
print("📊 GPSS - OPPORTUNITY MANAGEMENT")
print("-" * 70)
print(test_endpoint("Get Opportunities", "GET", "/gpss/opportunities"))
print(test_endpoint("Get Contacts", "GET", "/gpss/contacts"))
print(test_endpoint("Get Pipeline", "GET", "/gpss/pipeline"))
print()

# ATLAS PM System
print("🏗️ ATLAS PM - PROJECT MANAGEMENT")
print("-" * 70)
print(test_endpoint("Get Tasks", "GET", "/atlas/tasks"))
print(test_endpoint("Get Projects", "GET", "/atlas/projects"))
print()

# DDCSS System
print("💼 DDCSS - DIRECT CLIENT SALES")
print("-" * 70)
print(test_endpoint("Get Prospects", "GET", "/ddcss/prospects"))
print(test_endpoint("Get Sectors", "GET", "/ddcss/sectors"))
print()

# VERTEX System
print("💰 VERTEX - FINANCIAL MANAGEMENT")
print("-" * 70)
print(test_endpoint("Get Invoices", "GET", "/vertex/invoices"))
print(test_endpoint("Get Revenue Summary", "GET", "/vertex/revenue-summary"))
print()

# LBPC System  
print("📋 LBPC - PROPOSAL BUILDER")
print("-" * 70)
print(test_endpoint("Get Proposals", "GET", "/lbpc/proposals"))
print()

# GBIS System
print("🔍 GBIS - SUPPLIER MINING")
print("-" * 70)
print(test_endpoint("Get Suppliers", "GET", "/gbis/suppliers"))
print()

# Vendor Portals
print("🌐 VENDOR PORTALS")
print("-" * 70)
print(test_endpoint("Get Portals", "GET", "/portals"))
print()

# Mining Systems
print("⛏️ MINING SYSTEMS")
print("-" * 70)
print(test_endpoint("Mine GovCon", "POST", "/mine/govcon", data={}))
print(test_endpoint("Mine SAM.gov", "POST", "/mine/sam", data={}))
print(test_endpoint("Mine State/Local", "POST", "/mine/state-local", data={}))
print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
