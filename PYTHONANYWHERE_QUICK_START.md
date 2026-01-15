# NEXUS PythonAnywhere Quick Start

## 15-Minute Deployment Checklist

### Prerequisites (Have These Ready)
- [ ] PythonAnywhere account (free or $5/month)
- [ ] GitHub account with NEXUS BACKEND repo
- [ ] Airtable API Key
- [ ] Airtable Base ID
- [ ] Anthropic API Key

---

## PART 1: Deploy Backend to PythonAnywhere (10 minutes)

### Step 1: Create Account (2 minutes)
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up (Free or Hacker $5/month)
3. Verify email and log in

### Step 2: Clone Repository (2 minutes)
```bash
# Click "Consoles" → "Bash"
git clone https://github.com/YOUR_USERNAME/NEXUS-BACKEND.git
cd NEXUS-BACKEND
```

### Step 3: Set Up Environment (3 minutes)
```bash
# Create virtual environment
mkvirtualenv nexus --python=/usr/bin/python3.10

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

Add your keys:
```
AIRTABLE_API_KEY=your_key
AIRTABLE_BASE_ID=your_base_id
ANTHROPIC_API_KEY=your_key
JWT_SECRET=random_secret_string
```

Press `Ctrl+X`, `Y`, `Enter` to save.

### Step 4: Create Web App (3 minutes)

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose domain: `yourusername.pythonanywhere.com`
4. Select **"Manual configuration"**
5. Choose **Python 3.10**

### Step 5: Configure Web App (2 minutes)

**Source code:**
```
/home/YOUR_USERNAME/NEXUS-BACKEND
```

**Working directory:**
```
/home/YOUR_USERNAME/NEXUS-BACKEND
```

**WSGI configuration file:**
Click the link, delete everything, and paste:

```python
import sys
import os
from dotenv import load_dotenv

project_home = '/home/YOUR_USERNAME/NEXUS-BACKEND'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

load_dotenv(os.path.join(project_home, '.env'))

from api_server import app as application
```

**Replace YOUR_USERNAME with your actual username!**

**Virtualenv:**
```
/home/YOUR_USERNAME/.virtualenvs/nexus
```

**Click the green "Reload" button!**

### Step 6: Test Backend (1 minute)

Visit: `https://yourusername.pythonanywhere.com/health`

Should see:
```json
{"status": "healthy"}
```

✅ **Backend Done!**

**Your Backend URL:** `https://yourusername.pythonanywhere.com`

---

## PART 2: Deploy Frontend to Netlify (5 minutes)

### Step 1: Update Config (1 minute)

Edit `nexus-frontend/netlify.toml`:

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"
```

Commit and push:
```bash
git add nexus-frontend/netlify.toml
git commit -m "Configure PythonAnywhere backend"
git push origin main
```

### Step 2: Deploy to Netlify (3 minutes)

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Select your **NEXUS BACKEND** repo
5. Settings auto-detected from `netlify.toml`
6. Click **"Deploy site"**
7. Wait 3-4 minutes

✅ **Frontend Done!**

**Your Frontend URL:** `https://your-site.netlify.app`

### Step 3: Update CORS (1 minute)

Back in PythonAnywhere Bash console:

```bash
cd ~/NEXUS-BACKEND
nano api_server.py
```

Find the CORS line and update:
```python
CORS(app, origins=[
    "https://your-actual-netlify-site.netlify.app",
    "http://localhost:3000"
])
```

Save, then reload web app on Web tab.

---

## PART 3: Test Everything (2 minutes)

1. Visit your Netlify URL
2. Open browser console (F12)
3. Test systems:
   - GPSS → Fetch opportunities
   - ATLAS → Create task
   - AI Copilot → Ask question

✅ **Everything Works!**

---

## Troubleshooting Quick Fixes

### CORS Errors
```python
# In api_server.py
CORS(app)  # Allow all (for testing)
```
Then reload web app.

### 500 Errors
Check PythonAnywhere error log:
- Web tab → "Error log"
- Fix Python errors
- Reload web app

### Backend Won't Start
```bash
# Test imports
workon nexus
cd ~/NEXUS-BACKEND
python -c "from api_server import app; print('OK')"
```

---

## Cost

**Free Tier:** $0/month (both services)  
**Production:** $5/month (PythonAnywhere Hacker + Netlify free)

---

## You're Live! 🚀

**Backend:** https://yourusername.pythonanywhere.com  
**Frontend:** https://your-site.netlify.app

**Total Time:** ~15 minutes  
**Total Cost:** $0-5/month

Now go win those government contracts! 💰
