# 🚀 NEXUS Deployment - Netlify + PythonAnywhere

**Backend:** PythonAnywhere  
**Frontend:** Netlify (deedavis.biz account)  
**Target URL:** nexus.deedavis.biz

---

## 🎯 DEPLOYMENT OVERVIEW

```
User Browser
     ↓
Netlify Frontend (nexus.deedavis.biz)
     ↓
PythonAnywhere Backend (yourusername.pythonanywhere.com)
     ↓
Airtable Database
```

---

## 📋 QUICK DEPLOYMENT STEPS

### STEP 1: Deploy Backend to PythonAnywhere (15 minutes)

#### 1.1 Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account (or use existing)
3. Choose username (will be part of URL)

#### 1.2 Upload Code to PythonAnywhere

**Option A: Git Clone (Recommended)**
```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/YOUR_USERNAME/nexus-backend.git
cd nexus-backend
```

**Option B: Upload Files**
1. Use PythonAnywhere's "Files" tab
2. Upload zip of your project
3. Extract in your home directory

#### 1.3 Set Up Virtual Environment
```bash
# In PythonAnywhere Bash console:
cd ~/nexus-backend
mkvirtualenv --python=/usr/bin/python3.10 nexus-env
pip install -r requirements.txt
```

#### 1.4 Configure Web App

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (NOT Flask wizard)
4. Select **Python 3.10**

#### 1.5 Configure WSGI File

1. In Web tab, click on **WSGI configuration file** link
2. Delete everything and replace with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/nexus-backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from api_server import app as application
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

#### 1.6 Set Up Environment Variables

**Create .env file:**
```bash
# In PythonAnywhere Bash console:
cd ~/nexus-backend
nano .env
```

**Add your environment variables:**
```bash
AIRTABLE_API_KEY=your_airtable_key_here
AIRTABLE_BASE_ID=your_base_id_here
ANTHROPIC_API_KEY=your_anthropic_key_here
JWT_SECRET=your_random_secret_here
GOOGLE_API_KEY=your_google_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

**Secure the file:**
```bash
chmod 600 .env
```

#### 1.7 Configure Static Files (Optional)

In Web tab, add static files mapping:
- **URL:** `/media`
- **Directory:** `/home/YOUR_USERNAME/nexus-backend/photos_and_videos`

#### 1.8 Set Virtual Environment Path

In Web tab, under **"Virtualenv"** section:
```
/home/YOUR_USERNAME/.virtualenvs/nexus-env
```

#### 1.9 Reload Web App

1. Scroll to top of Web tab
2. Click green **"Reload yourusername.pythonanywhere.com"** button
3. Wait 10 seconds

#### 1.10 Test Your Backend

Visit: `https://yourusername.pythonanywhere.com/health`

Expected response:
```json
{
  "service": "NEXUS Backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

**Your backend URL:** `https://yourusername.pythonanywhere.com`

---

### STEP 2: Update Frontend Configuration

Edit `nexus-frontend/netlify.toml`:

**Find lines 14, 19, and 24 and replace with your PythonAnywhere URL:**

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"

[context.deploy-preview.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"

[context.branch-deploy.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"
```

**Example:**
```toml
REACT_APP_API_BASE = "https://deedavis.pythonanywhere.com"
```

---

### STEP 3: Run Pre-Flight Check

```bash
cd "/Users/deedavis/NEXUS BACKEND"
./preflight_check.sh
```

This verifies:
- Backend URL is configured
- Local build works
- Backend is responding
- Git is ready

---

### STEP 4: Commit and Push

```bash
cd "/Users/deedavis/NEXUS BACKEND"

git add nexus-frontend/netlify.toml
git add nexus-frontend/_redirects
git add preflight_check.sh
git add *.md

git commit -m "Configure NEXUS for Netlify + PythonAnywhere deployment"
git push origin main
```

---

### STEP 5: Deploy to Netlify (Your Existing Account)

1. **Log in to Netlify:** [app.netlify.com](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** → Select your repository
4. Netlify auto-detects from `netlify.toml`:
   - Base directory: `nexus-frontend`
   - Build command: `npm run build`
   - Publish directory: `build`
5. Click **"Deploy site"**
6. Wait 2-3 minutes

You'll get: `https://random-name-123456.netlify.app`

---

### STEP 6: Set Up Custom Domain (nexus.deedavis.biz)

1. In Netlify, go to **"Domain settings"**
2. Click **"Add custom domain"**
3. Enter: **`nexus.deedavis.biz`**
4. Netlify will prompt for DNS configuration

**Add DNS Record:**

Go to your DNS provider (where deedavis.biz is managed):

- **Type:** CNAME
- **Name:** nexus
- **Value:** [your-random-name-123456].netlify.app
- **TTL:** 3600

**If DNS is managed by Netlify:**
1. Go to Domains → deedavis.biz → DNS settings
2. Add CNAME record as above

**Wait 10-30 minutes** for DNS to propagate.

Netlify will automatically provision SSL certificate.

**Your site will be live at:** `https://nexus.deedavis.biz` 🚀

---

### STEP 7: Update Backend CORS

Edit `api_server.py` (line ~65):

**Change from:**
```python
CORS(app)  # Allows all origins
```

**Change to:**
```python
CORS(app, origins=[
    "https://nexus.deedavis.biz",
    "https://deedavis.biz",  # If main site needs access
])
```

**Commit and push:**
```bash
git add api_server.py
git commit -m "Configure CORS for production domains"
git push
```

**Update PythonAnywhere:**
```bash
# In PythonAnywhere Bash console:
cd ~/nexus-backend
git pull origin main

# Reload web app from Web tab
```

---

## 🔧 PYTHONANYWHERE SPECIFIC TIPS

### Viewing Logs
1. Go to **Web** tab
2. Scroll to **"Log files"** section
3. Click on **Error log** to see Python errors
4. Click on **Server log** to see access logs

### Updating Code
```bash
# In PythonAnywhere Bash console:
cd ~/nexus-backend
git pull origin main
pip install -r requirements.txt  # If dependencies changed

# Then reload web app from Web tab
```

### Checking Environment Variables
```bash
cd ~/nexus-backend
cat .env
```

### Restarting App
- Go to Web tab → Click green **"Reload"** button
- Or use API: `POST` to reload URL (shown in Web tab)

### Debugging
```bash
# View recent errors
tail -f ~/nexus-backend/error.log

# Check Python path
which python

# Check installed packages
pip list
```

---

## 💰 PYTHONANYWHERE COSTS

### Free Tier (Beginner)
- **Cost:** $0/month
- **Limits:**
  - 1 web app
  - 512 MB storage
  - yourusername.pythonanywhere.com only
  - No always-on tasks
- **Perfect for:** Testing and development

### Hacker Plan (Recommended for Production)
- **Cost:** $5/month
- **Benefits:**
  - Custom domains (nexus.deedavis.biz)
  - 2 web apps
  - More storage
  - Always-on tasks
  - No ads

### Web Developer Plan
- **Cost:** $12/month
- **Benefits:**
  - Everything in Hacker
  - More web apps
  - More storage
  - Priority support

**Recommendation for Production:** Hacker plan ($5/month) + Netlify free = **$5/month total**

---

## 🚨 TROUBLESHOOTING

### "ImportError" or Module Not Found
**Problem:** Dependencies not installed
**Solution:**
```bash
cd ~/nexus-backend
workon nexus-env
pip install -r requirements.txt
# Reload web app
```

### "500 Internal Server Error"
**Problem:** App configuration error
**Solution:**
1. Check error log in Web tab
2. Verify WSGI configuration
3. Check .env file exists and has correct values
4. Verify virtual environment path

### "Connection Refused" from Frontend
**Problem:** CORS or backend not running
**Solution:**
1. Test backend directly: `curl https://yourusername.pythonanywhere.com/health`
2. Check CORS settings in `api_server.py`
3. Verify backend URL in `netlify.toml`

### Environment Variables Not Loading
**Problem:** .env file not found or not loaded
**Solution:**
1. Check file exists: `ls -la ~/nexus-backend/.env`
2. Verify WSGI config loads dotenv
3. Check file permissions: `chmod 600 .env`
4. Reload web app

### Static Files (Videos) Not Loading
**Problem:** Static files mapping not configured
**Solution:**
1. In Web tab, add static files mapping
2. URL: `/media`
3. Directory: `/home/YOUR_USERNAME/nexus-backend/photos_and_videos`
4. Reload web app

### Custom Domain Not Working
**Problem:** DNS not configured or SSL pending
**Solution:**
1. Verify CNAME record: `dig nexus.deedavis.biz`
2. Wait for DNS propagation (up to 48 hours, usually 30 minutes)
3. Check Netlify domain settings
4. Verify SSL certificate status in Netlify

---

## 🧪 TESTING CHECKLIST

- [ ] Backend `/health` endpoint works
- [ ] Frontend loads without errors
- [ ] Browser console (F12) shows no errors
- [ ] API calls work (check Network tab)
- [ ] GPSS system loads opportunities
- [ ] AI Copilot responds to queries
- [ ] ATLAS system works
- [ ] All 7 systems tested
- [ ] Mobile responsive works
- [ ] Custom domain resolves
- [ ] SSL certificate active

---

## 📊 PYTHONANYWHERE DASHBOARD QUICK REFERENCE

### Important Tabs
- **Dashboard:** Overview and quick actions
- **Consoles:** Access Bash terminals
- **Files:** Browse/edit files
- **Web:** Configure web app
- **Tasks:** Schedule tasks (paid plans)
- **Databases:** MySQL databases (if needed)

### Key Locations
- **Your code:** `/home/YOUR_USERNAME/nexus-backend/`
- **Virtual env:** `/home/YOUR_USERNAME/.virtualenvs/nexus-env/`
- **WSGI config:** `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`
- **Error log:** Check in Web tab
- **Server log:** Check in Web tab

---

## 🔄 CONTINUOUS DEPLOYMENT

### Automatic Updates
Since PythonAnywhere doesn't auto-deploy on git push, use this workflow:

```bash
# On your local machine:
git add .
git commit -m "Update feature"
git push origin main

# On PythonAnywhere Bash console (or automate this):
cd ~/nexus-backend
git pull origin main
# Click Reload button in Web tab
```

### Semi-Automatic Option
Create a script: `~/nexus-backend/deploy.sh`
```bash
#!/bin/bash
cd ~/nexus-backend
git pull origin main
pip install -r requirements.txt
touch /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py
```

Run when you push changes:
```bash
bash ~/nexus-backend/deploy.sh
```

### Future: Full Automation
Consider setting up a webhook or scheduled task to check for updates.

---

## 🔐 SECURITY CHECKLIST

- [ ] `.env` file has correct permissions (600)
- [ ] `.env` file not in git repository
- [ ] CORS configured with specific domains
- [ ] JWT_SECRET is random and strong
- [ ] API keys are valid and secured
- [ ] PythonAnywhere account has 2FA enabled
- [ ] GitHub repository access controlled

---

## 📱 SHARE YOUR DEPLOYMENT

Your NEXUS Command Center is live at:

**`https://nexus.deedavis.biz`** 🚀

**Backend API:** `https://yourusername.pythonanywhere.com`

Share with your team:
```
🚀 NEXUS Command Center
https://nexus.deedavis.biz

7 Integrated Systems:
• GPSS - Government Procurement Sales
• ATLAS - Advanced Task & Labor Allocation
• DDCSS - Discovery-Driven Consulting Sales
• VERTEX - Financial Management
• GBIS - Grant Business Intelligence
• LBPC - Lead Pipeline & Client Acquisition
• ProposalBio - Proposal Quality Assurance
```

---

## 🎯 DEPLOYMENT SUMMARY

### What You Deployed

**Backend (PythonAnywhere):**
- URL: `https://yourusername.pythonanywhere.com`
- Cost: $0-5/month
- Technology: Flask + Python 3.10
- Database: Airtable (external)

**Frontend (Netlify):**
- URL: `https://nexus.deedavis.biz`
- Cost: $0/month
- Technology: React + TypeScript
- Hosting: Netlify CDN

**Total Monthly Cost:** $0-5

---

## 🆘 NEED HELP?

### PythonAnywhere Support
- **Help Pages:** [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Forums:** [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)
- **Email:** support@pythonanywhere.com

### Netlify Support
- **Docs:** [docs.netlify.com](https://docs.netlify.com)
- **Community:** [answers.netlify.com](https://answers.netlify.com)

### Your Documentation
- `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` - Detailed PythonAnywhere guide
- `PRODUCTION_ENV_VARS.md` - Environment variables
- `TROUBLESHOOTING_GUIDE.md` - Common issues

---

## ✅ NEXT STEPS

1. **Deploy backend to PythonAnywhere** (follow STEP 1 above)
2. **Get your PythonAnywhere URL**
3. **Update `netlify.toml`** with PythonAnywhere URL
4. **Run preflight check:** `./preflight_check.sh`
5. **Commit and push**
6. **Deploy to Netlify**
7. **Set up nexus.deedavis.biz**
8. **Test everything**
9. **Update CORS in backend**
10. **Go live!** 🎉

---

**Your professional NEXUS Command Center at nexus.deedavis.biz is ready to deploy!**
