# NEXUS TROUBLESHOOTING GUIDE

## 🔧 Common Issues & Solutions

---

## Issue #1: Backend Can't Find Tables (404 Errors)

### Symptoms:
```
❌ VERTEX INVOICES - NOT FOUND
404 Client Error: Not Found for url: https://api.airtable.com/...
```

### Causes & Solutions:

**1. Table Name Mismatch**
- ✅ **Check:** Table names in Airtable are ALL CAPS with SPACES
- ✅ **Check:** Table names in code match exactly
- ✅ **Example:** `VERTEX INVOICES` not `Vertex Invoices` or `VERTEX_INVOICES`

**2. Wrong Base ID**
- ✅ **Check:** `.env` file has correct `AIRTABLE_BASE_ID`
- ✅ **Correct ID:** `appaJZqKVUn3yJ7ma`
- ✅ **Fix:** Update `.env` and restart backend

**3. .env File Not Loading**
- ✅ **Check:** `.env` file is in `/Users/deedavis/NEXUS BACKEND/`
- ✅ **Check:** File is named `.env` (not `env.txt` or `.env.bak`)
- ✅ **Fix:** Restart backend after changing `.env`

**4. API Key Expired/Invalid**
- ✅ **Check:** Go to Airtable → Account → API
- ✅ **Check:** Create new personal access token if needed
- ✅ **Fix:** Update `AIRTABLE_API_KEY` in `.env`

---

## Issue #2: Port Already in Use

### Symptoms:
```
OSError: [Errno 48] Address already in use
Error: listen EADDRINUSE: address already in use :::8000
```

### Solution:

**Backend (Port 8000):**
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
lsof -ti:3000 | xargs kill -9
```

Then restart the service.

---

## Issue #3: AI Not Responding / Anthropic Errors

### Symptoms:
```
anthropic.AuthenticationError
anthropic.RateLimitError
Claude response empty or timeout
```

### Solutions:

**1. API Key Issue**
```bash
# Check if key is set
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:20])"
```
- Should show: `sk-ant-api03-...`
- If empty: Add to `.env`

**2. Rate Limit Reached**
- Wait 60 seconds and retry
- Check usage at: https://console.anthropic.com/

**3. Model Name Incorrect**
- Check `nexus_backend.py` line 100
- Should be: `claude-sonnet-4-20250514`

---

## Issue #4: Frontend Won't Connect to Backend

### Symptoms:
```
Failed to fetch
Network Error
CORS policy blocked
```

### Solutions:

**1. Backend Not Running**
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health
```
- If fails: Start backend

**2. Wrong Port/URL**
- Check `nexus-frontend/src/api/client.ts`
- `baseURL` should be: `http://127.0.0.1:8000` (local) or production URL

**3. CORS Issue**
- Check `api_server.py` has `CORS(app)` enabled
- Should allow all origins for development

---

## Issue #5: Python Module Not Found

### Symptoms:
```
ModuleNotFoundError: No module named 'anthropic'
ModuleNotFoundError: No module named 'flask'
```

### Solution:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
pip3 install -r requirements.txt

# Or install individually:
pip3 install anthropic
pip3 install flask flask-cors
pip3 install pyairtable
pip3 install python-dotenv
pip3 install PyJWT
```

---

## Issue #6: Frontend Build/Start Errors

### Symptoms:
```
npm ERR! missing script: start
Module not found: Can't resolve '@/components/...'
```

### Solutions:

**1. Dependencies Not Installed**
```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm install
```

**2. Wrong Directory**
- Must be in `/nexus-frontend/` folder
- Not root project directory

**3. Node Version Issue**
```bash
node --version  # Should be v16+ 
npm --version   # Should be v8+
```

---

## Issue #7: Airtable Permissions Error

### Symptoms:
```
403 Forbidden
Invalid permissions, or the requested model was not found
```

### Solutions:

**1. API Key Lacks Permissions**
- Go to: https://airtable.com/create/tokens
- Create new token with:
  - `data.records:read`
  - `data.records:write`
  - `schema.bases:read`
- Select correct base(s)

**2. Base ID Wrong**
- Verify: `appaJZqKVUn3yJ7ma`
- Check URL in Airtable browser

---

## Issue #8: Automation Not Triggering

### Symptoms:
- Record created but no automation runs
- Email not sent
- No AI response

### Causes:

**1. Free Tier Limitation**
- ⚠️ Free tier doesn't support:
  - "Run script" actions
  - "Make a request to webhook" actions
- ✅ **Fix:** Upgrade to Team plan ($20/month)

**2. Automation Not Enabled**
- Check Airtable → Automations tab
- Toggle should be ON (blue)

**3. Trigger Conditions Not Met**
- Check automation trigger settings
- Verify field values match conditions

---

## Issue #9: Environment Variables Not Working

### Symptoms:
```
Base ID: 
API Key: 
# Empty values when printing
```

### Solution:

**Check .env file exists:**
```bash
ls -la "/Users/deedavis/NEXUS BACKEND/.env"
```

**Check .env file contents:**
```bash
cat "/Users/deedavis/NEXUS BACKEND/.env"
```

**Verify loading in Python:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Base ID:', os.getenv('AIRTABLE_BASE_ID'))
print('API Key:', os.getenv('AIRTABLE_API_KEY')[:20] if os.getenv('AIRTABLE_API_KEY') else 'MISSING')
"
```

**Common fixes:**
- Remove quotes around values in `.env`
- No spaces around `=` sign
- Restart backend after changes

---

## Issue #10: Slow API Responses

### Symptoms:
- Requests take 10+ seconds
- Timeout errors
- Claude responses slow

### Solutions:

**1. Too Many Records**
- Add pagination to queries
- Use `maxRecords` parameter
- Filter before fetching

**2. Claude Model Too Large**
- Currently using: `claude-sonnet-4`
- For faster responses, could use `claude-3-haiku` (cheaper/faster)
- Trade-off: Quality vs. Speed

**3. Network Issues**
- Check internet connection
- Airtable API status: https://status.airtable.com/
- Anthropic API status: https://status.anthropic.com/

---

## Issue #11: Tables Not Showing in Airtable

### Symptoms:
- Can't see tables in left sidebar
- "Table not found" errors
- 57 tables should exist but showing fewer

### Solutions:

**1. Wrong Base Open**
- Verify URL: `https://airtable.com/appaJZqKVUn3yJ7ma`
- Should be: "NEXUS Command Center"

**2. Tables Hidden**
- Airtable has table visibility settings
- Check if tables are hidden (not deleted)

**3. Permissions Issue**
- If shared base: Check your access level
- Need "Creator" or "Owner" role

---

## 🔍 Diagnostic Commands

### Check Backend Status:
```bash
# Is backend running?
curl -s http://127.0.0.1:8000/health | python3 -m json.tool

# Test VERTEX connection:
curl -s http://127.0.0.1:8000/vertex/invoices | python3 -m json.tool | head -20

# Test GBIS connection:
curl -s http://127.0.0.1:8000/gbis/opportunities | python3 -m json.tool | head -20
```

### Check Airtable Connection:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "
from nexus_backend import AirtableClient
airtable = AirtableClient()
print('Testing connection...')
records = airtable.get_all_records('VERTEX INVOICES')
print(f'✅ Found {len(records)} invoices')
"
```

### Check Environment:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Python Version:', os.sys.version)
print('Base ID:', os.getenv('AIRTABLE_BASE_ID'))
print('Has Anthropic Key:', 'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No')
print('Has Airtable Key:', 'Yes' if os.getenv('AIRTABLE_API_KEY') else 'No')
"
```

### List All Airtable Tables:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()

base_id = os.getenv('AIRTABLE_BASE_ID')
api_key = os.getenv('AIRTABLE_API_KEY')
url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
headers = {'Authorization': f'Bearer {api_key}'}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    tables = response.json()['tables']
    print(f'Found {len(tables)} tables:')
    for t in sorted(tables, key=lambda x: x['name']):
        print(f'  - {t[\"name\"]}')
else:
    print(f'Error: {response.status_code}')
"
```

---

## 📞 When All Else Fails

### Reset Everything:

**1. Stop all services:**
```bash
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

**2. Verify .env file:**
```bash
cat "/Users/deedavis/NEXUS BACKEND/.env"
# Should show all API keys
```

**3. Restart backend:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
PORT=8000 python3 api_server.py
```

**4. Test health:**
```bash
curl http://127.0.0.1:8000/health
```

**5. If still broken, check logs:**
- Backend prints errors to terminal
- Look for red text with "Error" or "Exception"

---

## 🆘 Quick Fixes Reference

| Problem | Quick Fix |
|---------|-----------|
| Port in use | `lsof -ti:8000 \| xargs kill -9` |
| Backend won't start | Check `.env` file exists |
| 404 table errors | Verify ALL CAPS table names |
| 403 permission errors | Check Airtable API token |
| AI not working | Check Anthropic API key |
| Frontend won't connect | Check backend is running on 8000 |
| Slow responses | Check internet + API status pages |
| Module not found | `pip3 install -r requirements.txt` |

---

## 📚 Additional Resources

- **Airtable API Docs:** https://airtable.com/developers/web/api/introduction
- **Anthropic API Docs:** https://docs.anthropic.com/
- **Flask Docs:** https://flask.palletsprojects.com/
- **React Docs:** https://react.dev/

---

**Last Updated:** January 18, 2026  
**Status:** Current ✅
