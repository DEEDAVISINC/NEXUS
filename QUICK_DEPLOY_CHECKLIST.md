# ✅ NEXUS Quick Deploy Checklist

**Backend:** PythonAnywhere  
**Frontend:** Netlify (deedavis.biz)  
**Time:** ~30 minutes

---

## 🎯 PHASE 1: PYTHONANYWHERE BACKEND (15 min)

### 1. Create Account
- [ ] Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- [ ] Sign up (Hacker plan $5/month for custom domains)
- [ ] Note your username: `___________________`

### 2. Upload Code
```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/YOUR_USERNAME/nexus-backend.git
cd nexus-backend
```

### 3. Set Up Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 nexus-env
pip install -r requirements.txt
```

### 4. Configure Web App
- [ ] Web tab → "Add a new web app"
- [ ] Manual configuration → Python 3.10
- [ ] Click WSGI configuration file link

**Replace entire WSGI file with:**
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/nexus-backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from api_server import app as application
```

### 5. Add Environment Variables
```bash
# In Bash console:
cd ~/nexus-backend
nano .env
```

**Add these lines:**
```
AIRTABLE_API_KEY=your_key_here
AIRTABLE_BASE_ID=your_base_id_here
ANTHROPIC_API_KEY=your_anthropic_key_here
JWT_SECRET=random_secret_string_here
```

**Save:** `Ctrl+X`, `Y`, `Enter`

### 6. Set Virtual Environment Path
- [ ] In Web tab, find "Virtualenv" section
- [ ] Enter: `/home/YOUR_USERNAME/.virtualenvs/nexus-env`

### 7. Reload & Test
- [ ] Click green "Reload" button
- [ ] Test: Visit `https://YOUR_USERNAME.pythonanywhere.com/health`
- [ ] Should see: `{"service":"NEXUS Backend","status":"healthy"}`

**✅ Backend URL:** `https://_____________________.pythonanywhere.com`

---

## 🎨 PHASE 2: NETLIFY FRONTEND (10 min)

### 1. Update Configuration
Edit `nexus-frontend/netlify.toml`:

**Line 14:**
```toml
REACT_APP_API_BASE = "https://YOUR_USERNAME.pythonanywhere.com"
```

**Line 19:**
```toml
REACT_APP_API_BASE = "https://YOUR_USERNAME.pythonanywhere.com"
```

**Line 24:**
```toml
REACT_APP_API_BASE = "https://YOUR_USERNAME.pythonanywhere.com"
```

### 2. Run Preflight Check
```bash
cd "/Users/deedavis/NEXUS BACKEND"
./preflight_check.sh
```

- [ ] All checks pass

### 3. Commit & Push
```bash
git add .
git commit -m "Configure for PythonAnywhere + Netlify deployment"
git push origin main
```

### 4. Deploy to Netlify
- [ ] Log in: [app.netlify.com](https://app.netlify.com)
- [ ] "Add new site" → "Import an existing project"
- [ ] Choose GitHub → Select your repository
- [ ] Settings auto-detected from `netlify.toml`
- [ ] Click "Deploy site"
- [ ] Wait 2-3 minutes

**✅ Temporary URL:** `https://_____________________.netlify.app`

---

## 🌐 PHASE 3: CUSTOM DOMAIN (5 min)

### 1. Add Domain in Netlify
- [ ] Domain settings → "Add custom domain"
- [ ] Enter: `nexus.deedavis.biz`

### 2. Configure DNS
**Add CNAME record in your DNS provider:**

```
Type:  CNAME
Name:  nexus
Value: [your-random-name].netlify.app
TTL:   3600
```

- [ ] DNS record added
- [ ] Wait 10-30 minutes for propagation
- [ ] SSL certificate will auto-provision

### 3. Update CORS
Edit `api_server.py` (line ~65):

```python
CORS(app, origins=[
    "https://nexus.deedavis.biz",
])
```

**Update backend:**
```bash
# Locally:
git add api_server.py
git commit -m "Configure CORS for production"
git push

# On PythonAnywhere Bash console:
cd ~/nexus-backend
git pull origin main
# Click "Reload" in Web tab
```

**✅ Final URL:** `https://nexus.deedavis.biz`

---

## 🧪 TESTING (5 min)

### Backend Tests
```bash
curl https://YOUR_USERNAME.pythonanywhere.com/health
curl https://YOUR_USERNAME.pythonanywhere.com/dashboard/stats
```

### Frontend Tests
- [ ] Visit `https://nexus.deedavis.biz`
- [ ] Open browser console (F12) - no errors
- [ ] Check Network tab - API calls working
- [ ] Navigate to GPSS - loads opportunities
- [ ] Test AI Copilot - responds
- [ ] Navigate to ATLAS - loads tasks
- [ ] Test on mobile - responsive

### All Systems Check
- [ ] GPSS - Government Sales
- [ ] ATLAS - Project Management
- [ ] DDCSS - Consulting Sales
- [ ] VERTEX - Financial
- [ ] GBIS - Grants
- [ ] LBPC - Lead Pipeline
- [ ] ProposalBio - QA

---

## 📋 ENVIRONMENT VARIABLES NEEDED

### PythonAnywhere (.env file)
```bash
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX     # From airtable.com/account
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX     # From your base URL
ANTHROPIC_API_KEY=sk-ant-api03-XXXX    # From console.anthropic.com
JWT_SECRET=random_secret_here          # Generate random string
```

**Optional:**
```bash
GOOGLE_API_KEY=your_google_key         # For opportunity mining
GOOGLE_CSE_ID=your_cse_id             # For opportunity mining
```

---

## 🚨 TROUBLESHOOTING QUICK FIXES

### Backend 500 Error
```bash
# Check error log in PythonAnywhere Web tab
# Verify .env file:
cat ~/nexus-backend/.env
```

### Frontend Won't Load
- Check backend URL in `netlify.toml`
- Test backend: `curl https://username.pythonanywhere.com/health`
- Check browser console (F12)

### API Calls Failing
- Verify CORS in `api_server.py`
- Check PythonAnywhere error logs
- Test backend endpoints directly

### DNS Not Working
- Wait 30 minutes minimum
- Check record: `dig nexus.deedavis.biz`
- Verify CNAME value is correct

---

## 💰 TOTAL COST

| Item | Cost |
|------|------|
| PythonAnywhere Hacker | $5/month |
| Netlify | $0/month |
| **Total** | **$5/month** |

---

## 📚 NEED MORE HELP?

**Complete guide:** `NETLIFY_PYTHONANYWHERE_DEPLOY.md`

**Quick commands:**
```bash
# Read complete guide
cat NETLIFY_PYTHONANYWHERE_DEPLOY.md

# Run preflight check
./preflight_check.sh

# Test backend
curl https://username.pythonanywhere.com/health
```

---

## ✅ DONE!

When complete, you'll have:
- ✅ Backend at `https://username.pythonanywhere.com`
- ✅ Frontend at `https://nexus.deedavis.biz`
- ✅ Professional, secure, always-on
- ✅ $5/month total cost

**Share with team:**
```
🚀 NEXUS Command Center
https://nexus.deedavis.biz

Access all 7 business systems 24/7!
```

---

**Print this checklist and check off items as you go!** ✅
