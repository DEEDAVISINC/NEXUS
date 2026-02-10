#!/usr/bin/env python3
"""
COMPREHENSIVE NEXUS SYSTEMS AUDIT
Tests everything to see what's actually working
"""
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv
import requests
from datetime import datetime

print("=" * 80)
print("🔍 NEXUS SYSTEMS AUDIT - COMPREHENSIVE CHECK")
print("=" * 80)
print()

# Load environment
try:
    load_dotenv()
    print("✅ Environment variables loaded")
except Exception as e:
    print(f"❌ Environment variables failed: {e}")
    sys.exit(1)

print()
print("-" * 80)
print("1. AIRTABLE CONNECTION")
print("-" * 80)

try:
    api_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    
    if not api_key:
        print("❌ AIRTABLE_API_KEY not found in environment")
    elif not base_id:
        print("❌ AIRTABLE_BASE_ID not found in environment")
    else:
        api = Api(api_key)
        base = api.base(base_id)
        schema = base.schema()
        
        print(f"✅ Connected to Airtable")
        print(f"   Base ID: {base_id}")
        print(f"   Total Tables: {len(schema.tables)}")
        
        # List all tables
        print()
        print("   📋 Available Tables:")
        for table in schema.tables:
            print(f"      - {table.name}")
            
except Exception as e:
    print(f"❌ Airtable connection failed: {e}")

print()
print("-" * 80)
print("2. CRITICAL TABLES CHECK")
print("-" * 80)

critical_tables = [
    'GPSS OPPORTUNITIES',
    'GPSS PRODUCTS',
    'GPSS SUPPLIERS',
    'AI RECOMMENDATIONS',
    'GPSS SUBCONTRACTORS'
]

try:
    for table_name in critical_tables:
        try:
            table = api.table(base_id, table_name)
            records = table.all(max_records=1)
            record_count = len(table.all(max_records=100))
            print(f"✅ {table_name}: {record_count} records")
        except Exception as e:
            print(f"❌ {table_name}: {str(e)}")
except:
    print("❌ Cannot check tables - connection failed")

print()
print("-" * 80)
print("3. CALENDAR AUTOMATION")
print("-" * 80)

# Check if calendar_automation.py exists
calendar_file = "/Users/deedavis/NEXUS BACKEND/calendar_automation.py"
if os.path.exists(calendar_file):
    print(f"✅ calendar_automation.py exists")
    
    # Try to import it
    try:
        sys.path.insert(0, "/Users/deedavis/NEXUS BACKEND")
        from calendar_automation import CalendarAutomation
        
        ca = CalendarAutomation()
        deadlines = ca.get_upcoming_deadlines(14)
        print(f"✅ Calendar automation loads: {len(deadlines)} deadlines found")
        
    except Exception as e:
        print(f"❌ Calendar automation failed to load: {e}")
else:
    print(f"❌ calendar_automation.py not found")

# Check cron jobs
print()
print("   Checking cron jobs:")
try:
    import subprocess
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if 'calendar_automation' in result.stdout:
        print("   ✅ Calendar automation cron jobs installed")
        lines = [line for line in result.stdout.split('\n') if 'calendar_automation' in line and not line.startswith('#')]
        print(f"      Found {len(lines)} active cron jobs")
    else:
        print("   ❌ No calendar automation cron jobs found")
except Exception as e:
    print(f"   ❌ Cannot check cron jobs: {e}")

# Check log file
log_file = "/Users/deedavis/NEXUS BACKEND/calendar_automation.log"
if os.path.exists(log_file):
    print(f"   ✅ Log file exists")
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            
            has_errors = any('error' in line.lower() or 'traceback' in line.lower() for line in recent_lines)
            has_success = any('sent' in line.lower() or 'success' in line.lower() for line in recent_lines)
            
            if has_errors:
                print("   ⚠️  Recent errors found in log")
            if has_success:
                print("   ✅ Recent successful runs in log")
            if not has_errors and not has_success:
                print("   ⚠️  Log exists but unclear status")
                
    except Exception as e:
        print(f"   ⚠️  Cannot read log file: {e}")
else:
    print(f"   ❌ Log file not found")

print()
print("-" * 80)
print("4. API SERVER")
print("-" * 80)

api_file = "/Users/deedavis/NEXUS BACKEND/api_server.py"
if os.path.exists(api_file):
    print(f"✅ api_server.py exists")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=2)
        print(f"✅ API server is RUNNING (port 5000)")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ API server is NOT running")
        print(f"   To start: cd '/Users/deedavis/NEXUS BACKEND' && python api_server.py")
    except Exception as e:
        print(f"❌ API server check failed: {e}")
else:
    print(f"❌ api_server.py not found")

print()
print("-" * 80)
print("5. NEXUS BACKEND")
print("-" * 80)

backend_file = "/Users/deedavis/NEXUS BACKEND/nexus_backend.py"
if os.path.exists(backend_file):
    print(f"✅ nexus_backend.py exists")
    
    # Check file size
    size = os.path.getsize(backend_file)
    print(f"   File size: {size:,} bytes")
    
    # Try to import
    try:
        from nexus_backend import AIRecommendationAgent
        print(f"✅ AIRecommendationAgent can be imported")
    except Exception as e:
        print(f"❌ Cannot import AIRecommendationAgent: {e}")
else:
    print(f"❌ nexus_backend.py not found")

print()
print("-" * 80)
print("6. EMAIL CONFIGURATION")
print("-" * 80)

email = os.environ.get('NEXUS_EMAIL')
email_password = os.environ.get('NEXUS_EMAIL_PASSWORD')
user_email = os.environ.get('USER_EMAIL')

if email:
    print(f"✅ NEXUS_EMAIL configured: {email}")
else:
    print(f"❌ NEXUS_EMAIL not set")

if email_password:
    print(f"✅ NEXUS_EMAIL_PASSWORD configured")
else:
    print(f"❌ NEXUS_EMAIL_PASSWORD not set")

if user_email:
    print(f"✅ USER_EMAIL configured: {user_email}")
else:
    print(f"❌ USER_EMAIL not set")

print()
print("-" * 80)
print("7. AI RECOMMENDATION SYSTEM")
print("-" * 80)

ai_script = "/Users/deedavis/NEXUS BACKEND/get_ai_recommendation.py"
if os.path.exists(ai_script):
    print(f"✅ get_ai_recommendation.py exists")
else:
    print(f"❌ get_ai_recommendation.py not found")

# Check AI RECOMMENDATIONS table
try:
    ai_table = api.table(base_id, 'AI RECOMMENDATIONS')
    ai_records = ai_table.all(max_records=10)
    print(f"✅ AI RECOMMENDATIONS table accessible")
    print(f"   Records: {len(ai_records)}")
    
    if ai_records:
        pending = [r for r in ai_records if r['fields'].get('STATUS') == 'PENDING APPROVAL']
        approved = [r for r in ai_records if r['fields'].get('STATUS') == 'APPROVED']
        print(f"   Pending: {len(pending)}, Approved: {len(approved)}")
except Exception as e:
    print(f"❌ AI RECOMMENDATIONS table issue: {e}")

print()
print("-" * 80)
print("8. PYTHON ENVIRONMENT")
print("-" * 80)

print(f"✅ Python version: {sys.version.split()[0]}")
print(f"✅ Python executable: {sys.executable}")

# Check key packages
packages = ['pyairtable', 'python-dotenv', 'icalendar', 'flask', 'requests']
for package in packages:
    try:
        __import__(package)
        print(f"✅ {package} installed")
    except ImportError:
        print(f"❌ {package} NOT installed")

print()
print("-" * 80)
print("9. FILE STRUCTURE")
print("-" * 80)

important_files = [
    'api_server.py',
    'nexus_backend.py',
    'calendar_automation.py',
    'get_ai_recommendation.py',
    '.env',
    'requirements.txt'
]

base_dir = "/Users/deedavis/NEXUS BACKEND"
for filename in important_files:
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {filename}: {size:,} bytes")
    else:
        print(f"❌ {filename}: NOT FOUND")

print()
print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
print()
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
