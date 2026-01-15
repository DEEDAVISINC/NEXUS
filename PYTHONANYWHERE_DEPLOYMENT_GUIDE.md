# NEXUS PythonAnywhere Deployment Guide

## Overview
This guide will walk you through deploying the NEXUS backend to PythonAnywhere and frontend to Netlify.

**Architecture:**
- **PythonAnywhere** for the Python/Flask backend API (free or paid)
- **Netlify** for the React frontend (free)

---

## Architecture

```
┌─────────────────────┐
│   USER'S BROWSER    │
└──────────┬──────────┘
           │
           │ HTTPS
           │
┌──────────▼──────────┐
│  NETLIFY (Frontend) │  ← React App (nexus-frontend/)
│  Global CDN         │  ← Free, Fast, Always On
└──────────┬──────────┘
           │
           │ API Calls (CORS enabled)
           │
┌──────────▼──────────┐
│  PYTHONANYWHERE     │  ← Python/Flask API (api_server.py)
│  (Backend)          │  ← Free or $5/month
└──────────┬──────────┘
           │
           │ Data Storage
           │
┌──────────▼──────────┐
│      AIRTABLE       │  ← Your Database
│   All Systems       │
└─────────────────────┘
```

---

## Prerequisites

Before starting, ensure you have:

1. **PythonAnywhere Account** - Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Netlify Account** - Sign up at [netlify.com](https://netlify.com)
3. **GitHub Account** - Your code repository
4. **API Keys Ready:**
   - Airtable API Key
   - Airtable Base ID
   - Anthropic (Claude) API Key
   - Google API Key (optional)
   - Google CSE ID (optional)

---

## PART 1: Deploy Backend to PythonAnywhere

### Step 1: Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Pricing & signup"
3. Choose a plan:
   - **Beginner (Free)** - Good for testing, limited to pythonanywhere.com domain
   - **Hacker ($5/month)** - Recommended, allows custom domains, more CPU
4. Sign up and verify your email

### Step 2: Clone Your Repository

1. Once logged in, click **"Consoles"** → **"Bash"**
2. Clone your repository:

```bash
git clone https://github.com/YOUR_USERNAME/NEXUS-BACKEND.git
cd NEXUS-BACKEND
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
mkvirtualenv nexus --python=/usr/bin/python3.10

# Activate it (should auto-activate after creation)
workon nexus

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you get any errors about missing packages, you may need to install them individually.

### Step 4: Set Up Environment Variables

PythonAnywhere doesn't use `.env` files directly. You'll configure these in the web app settings.

For now, create a `.env` file for testing:

```bash
nano .env
```

Add your environment variables:

```
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
JWT_SECRET=your_random_secret_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 5: Create WSGI Configuration File

PythonAnywhere uses WSGI to run Flask apps. Create a WSGI configuration:

```bash
nano wsgi.py
```

Add this content:

```python
import sys
import os
from dotenv import load_dotenv

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/NEXUS-BACKEND'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from api_server import app as application
```

**Important:** Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 6: Create Web App

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose your domain:
   - Free: `yourusername.pythonanywhere.com`
   - Paid: Custom domain or `yourusername.pythonanywhere.com`
4. Select **"Manual configuration"**
5. Choose **Python 3.10**

### Step 7: Configure Web App

On the Web tab, configure these settings:

#### A. Source Code
```
Source code: /home/YOUR_USERNAME/NEXUS-BACKEND
Working directory: /home/YOUR_USERNAME/NEXUS-BACKEND
```

#### B. WSGI Configuration File

Click on the WSGI configuration file link (it will be something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)

Delete everything in the file and replace with:

```python
import sys
import os
from dotenv import load_dotenv

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/NEXUS-BACKEND'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from api_server import app as application

# Enable CORS for your Netlify domain
# You'll update this after deploying frontend
```

**Important:** Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

Save the file.

#### C. Virtualenv

In the "Virtualenv" section, enter:
```
/home/YOUR_USERNAME/.virtualenvs/nexus
```

Replace `YOUR_USERNAME` with your actual username.

#### D. Static Files

You don't need to configure static files for the API server.

### Step 8: Environment Variables in PythonAnywhere

Since PythonAnywhere's free tier doesn't support setting environment variables in the dashboard, we'll use the `.env` file approach.

Your `.env` file should already be created in Step 4.

### Step 9: Reload Web App

1. Scroll to the top of the Web tab
2. Click the big green **"Reload yourusername.pythonanywhere.com"** button
3. Wait a few seconds

### Step 10: Test Backend

Visit: `https://yourusername.pythonanywhere.com/health`

You should see:
```json
{
  "service": "NEXUS Backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

If you get an error:
1. Click **"Error log"** link on Web tab
2. Check for Python errors
3. Fix issues and reload

✅ **Backend is live!**

**Your Backend URL:** `https://yourusername.pythonanywhere.com`

---

## PART 2: Configure CORS for Netlify

Before deploying the frontend, update CORS in your backend.

### Option 1: Allow All Origins (Easiest for Testing)

Your `api_server.py` already has this:
```python
CORS(app)  # Allows all origins
```

This is fine for testing, but less secure.

### Option 2: Restrict to Netlify Domain (Recommended)

Edit `api_server.py` on PythonAnywhere:

```bash
cd ~/NEXUS-BACKEND
nano api_server.py
```

Find the CORS line and update it:

```python
from flask_cors import CORS

app = Flask(__name__)

# Allow your Netlify domain and localhost
CORS(app, origins=[
    "https://your-site.netlify.app",  # Update after deploying frontend
    "http://localhost:3000"  # For local development
])
```

You'll update this with your actual Netlify URL after deploying the frontend.

---

## PART 3: Deploy Frontend to Netlify

### Step 1: Update Frontend Configuration

Edit `nexus-frontend/netlify.toml` locally:

```toml
[build]
  base = "nexus-frontend"
  command = "npm run build"
  publish = "build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"

[context.deploy-preview.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"
```

**Replace** `yourusername.pythonanywhere.com` with your actual PythonAnywhere domain!

### Step 2: Commit and Push Changes

```bash
cd "/Users/deedavis/NEXUS BACKEND"
git add nexus-frontend/netlify.toml
git commit -m "Configure PythonAnywhere backend URL"
git push origin main
```

### Step 3: Create Netlify Site

1. Go to [netlify.com](https://netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"Deploy with GitHub"**
4. Authorize Netlify if prompted
5. Select your **NEXUS BACKEND** repository

### Step 4: Configure Build Settings

Netlify should auto-detect settings from `netlify.toml`:

**Verify these settings:**
- **Base directory:** `nexus-frontend`
- **Build command:** `npm run build`
- **Publish directory:** `nexus-frontend/build`

### Step 5: Deploy Frontend

1. Click **"Deploy site"**
2. Wait 3-4 minutes for build
3. You'll get a URL like: `https://amazing-site-123abc.netlify.app`

### Step 6: Customize Domain (Optional)

1. Go to **Site settings** → **Domain management**
2. Click **"Options"** → **"Edit site name"**
3. Choose: `nexus-command.netlify.app` (or your preferred name)

✅ **Frontend is live!**

### Step 7: Update CORS (If You Restricted It)

If you restricted CORS in Step 2 of Part 2:

1. Go back to PythonAnywhere
2. Open Bash console
3. Edit `api_server.py`:

```bash
cd ~/NEXUS-BACKEND
nano api_server.py
```

Update CORS with your actual Netlify URL:

```python
CORS(app, origins=[
    "https://nexus-command.netlify.app",  # Your actual Netlify URL
    "http://localhost:3000"
])
```

4. Save and reload your PythonAnywhere web app

---

## PART 4: Test Your Deployment

### 4.1 Open Your Netlify Site

Visit: `https://your-site.netlify.app`

### 4.2 Test Checklist

1. ✅ Landing page loads correctly
2. ✅ No console errors (press F12 to check)
3. ✅ Navigate to GPSS system
4. ✅ Try to fetch opportunities (tests backend connection)
5. ✅ Test AI Copilot (tests Claude API)
6. ✅ Navigate to ATLAS system
7. ✅ Create a test task
8. ✅ Try DDCSS prospect qualification
9. ✅ Test invoice generation

### 4.3 Check Browser Console

Press **F12** → **Console** tab

**Good signs:**
- No red errors
- API calls show 200 status
- Data loads successfully

**Bad signs (and fixes):**
- **CORS errors** → Update CORS in `api_server.py` and reload
- **404 on API calls** → Check REACT_APP_API_BASE in `netlify.toml`
- **500 errors** → Check PythonAnywhere error logs

---

## Troubleshooting

### Backend Issues

**Problem:** 500 Internal Server Error

**Solution:**
1. Go to PythonAnywhere **Web** tab
2. Click **"Error log"** link
3. Read the Python error messages
4. Common issues:
   - Missing environment variables (check `.env` file)
   - Import errors (check `requirements.txt`)
   - Airtable/Anthropic API key issues

**Problem:** Web app won't start

**Solution:**
1. Check WSGI configuration file
2. Verify virtualenv path is correct
3. Ensure all imports work:
   ```bash
   workon nexus
   cd ~/NEXUS-BACKEND
   python -c "from api_server import app; print('OK')"
   ```
4. Check error log for details

**Problem:** Environment variables not working

**Solution:**
1. Verify `.env` file exists in `/home/YOUR_USERNAME/NEXUS-BACKEND/`
2. Check file contents with: `cat ~/.env`
3. Ensure `python-dotenv` is installed: `pip install python-dotenv`
4. Reload web app

### Frontend Issues

**Problem:** Build fails on Netlify

**Solution:**
- Check build logs in Netlify dashboard
- Verify `package.json` has all dependencies
- Ensure Node version is 18+

**Problem:** Blank page after deployment

**Solution:**
- Check browser console for errors
- Verify `netlify.toml` has correct redirects
- Check that `build` folder was created

**Problem:** API calls failing

**Solution:**
- Verify `REACT_APP_API_BASE` in `netlify.toml`
- Check that PythonAnywhere URL is correct
- Test backend directly: `https://yourusername.pythonanywhere.com/health`

### CORS Issues

**Problem:** CORS errors in browser console

**Solution:**
1. Edit `api_server.py` on PythonAnywhere:
   ```python
   CORS(app, origins=[
       "https://your-actual-netlify-site.netlify.app",
       "http://localhost:3000"
   ])
   ```
2. Reload PythonAnywhere web app
3. Clear browser cache and refresh

---

## Cost Breakdown

### Free Tier (Perfect for Testing)
```
Netlify:         $0/month
PythonAnywhere:  $0/month (Beginner account)
─────────────────────────────────────────
TOTAL:           $0/month
```

**Free Tier Limitations:**
- PythonAnywhere domain only (yourusername.pythonanywhere.com)
- Limited CPU seconds per day
- Slower performance
- One web app only

### Paid Tier (Recommended for Production)
```
Netlify:         $0/month (still free!)
PythonAnywhere:  $5/month (Hacker account)
─────────────────────────────────────────
TOTAL:           $5/month
```

**Hacker Account Benefits:**
- Custom domain support
- More CPU seconds
- Better performance
- Multiple web apps
- SSH access

---

## Updating Your Deployment

### Update Backend

1. SSH into PythonAnywhere or use Bash console
2. Pull latest changes:
   ```bash
   cd ~/NEXUS-BACKEND
   git pull origin main
   ```
3. Install any new dependencies:
   ```bash
   workon nexus
   pip install -r requirements.txt
   ```
4. Reload web app (green button on Web tab)

### Update Frontend

Simply push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Netlify will automatically rebuild and redeploy!

---

## Monitoring

### PythonAnywhere

**Access Logs:**
- Web tab → "Access log" link
- Shows all HTTP requests

**Error Logs:**
- Web tab → "Error log" link
- Shows Python errors and exceptions

**Server Logs:**
- Web tab → "Server log" link
- Shows web app startup/reload logs

### Netlify

**Build Logs:**
- Deploys tab → Click on a deploy
- Shows build output and errors

**Function Logs:**
- Functions tab (if using)

---

## Security Best Practices

### PythonAnywhere

1. **Protect your `.env` file:**
   ```bash
   chmod 600 ~/.env
   ```

2. **Don't commit `.env` to git:**
   - Already in `.gitignore`

3. **Use strong API keys:**
   - Rotate periodically
   - Different keys for dev/prod

4. **Restrict CORS:**
   ```python
   CORS(app, origins=["https://your-netlify-site.netlify.app"])
   ```

### Netlify

1. **Environment variables in `netlify.toml`:**
   - Not sensitive data
   - Visible in git repository
   - Only contains backend URL

2. **HTTPS automatic:**
   - Netlify provides free SSL

---

## Advanced Configuration

### Custom Domain on PythonAnywhere (Hacker Account)

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Enter your custom domain
4. Update DNS records:
   - CNAME: `www` → `webapp-XXXXX.pythonanywhere.com`
   - A Record: `@` → PythonAnywhere IP
5. Wait for DNS propagation (up to 24 hours)

### Environment Variables Best Practices

For better security on paid accounts, you can use a secrets management approach:

```python
# In api_server.py
import os

# Try to load from environment first, then .env
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
if not AIRTABLE_API_KEY:
    from dotenv import load_dotenv
    load_dotenv()
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
```

---

## Quick Reference Commands

### PythonAnywhere Bash

```bash
# Navigate to project
cd ~/NEXUS-BACKEND

# Activate virtualenv
workon nexus

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Check logs
tail -f ~/logs/yourusername.pythonanywhere.com.error.log

# Test app locally
python api_server.py
```

### Local Development

```bash
# Start backend locally
cd "/Users/deedavis/NEXUS BACKEND"
python api_server.py

# Start frontend locally
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

---

## Success Checklist

Before going live with clients:

- [ ] Backend deployed to PythonAnywhere
- [ ] Backend health check returns 200
- [ ] Frontend deployed to Netlify
- [ ] Frontend loads without errors
- [ ] All environment variables set correctly
- [ ] CORS configured properly
- [ ] All systems tested (GPSS, DDCSS, ATLAS, LBPC, GBIS)
- [ ] AI Copilot working
- [ ] Invoice generation working
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Error logs reviewed

---

## Support Resources

### PythonAnywhere
- **Help:** [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Forums:** [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)
- **Status:** [status.pythonanywhere.com](https://status.pythonanywhere.com)

### Netlify
- **Docs:** [docs.netlify.com](https://docs.netlify.com)
- **Support:** [community.netlify.com](https://community.netlify.com)

---

## Congratulations!

Your NEXUS system is now:
- ✅ Live on PythonAnywhere (backend)
- ✅ Live on Netlify (frontend)
- ✅ Accessible from anywhere
- ✅ Secure with HTTPS
- ✅ Professional and reliable
- ✅ Ready to win government contracts!

**Backend:** https://yourusername.pythonanywhere.com  
**Frontend:** https://your-site.netlify.app

**Now go land those RFPs!** 🚀💰
