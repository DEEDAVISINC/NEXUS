# 🚀 NEXUS DEPLOYMENT GUIDE
## Netlify (Frontend) + Render (Backend)

---

## 📋 PREREQUISITES

Before deploying, you need:

1. ✅ **GitHub Account** - Your code must be on GitHub
2. ✅ **Netlify Account** - Free at [netlify.com](https://netlify.com)
3. ✅ **Render Account** - Free at [render.com](https://render.com)
4. ✅ **API Keys:**
   - Airtable API Key
   - Airtable Base ID
   - Anthropic (Claude) API Key
   - Google API Key (optional, for mining)
   - Google CSE ID (optional, for mining)

---

## 🎯 DEPLOYMENT OVERVIEW

```
┌─────────────────────┐
│   USER'S BROWSER    │
└──────────┬──────────┘
           │
           │ HTTPS
           │
┌──────────▼──────────┐
│  NETLIFY (Frontend) │  ← React App
│  nexus.netlify.app  │  ← Free, Fast, Always On
└──────────┬──────────┘
           │
           │ API Calls
           │
┌──────────▼──────────┐
│   RENDER (Backend)  │  ← Python/Flask API
│  nexus-api.onrender │  ← Free or $7/month
└──────────┬──────────┘
           │
           │ Data Storage
           │
┌──────────▼──────────┐
│      AIRTABLE       │  ← Your Database
│   Your Data Safe   │
└─────────────────────┘
```

---

## 📦 STEP 1: PUSH CODE TO GITHUB

### If you haven't already:

```bash
# In your NEXUS BACKEND folder
cd "/Users/deedavis/NEXUS BACKEND"

# Initialize git (if not already done)
git init

# Create .gitignore if it doesn't exist
cat > .gitignore << 'EOF'
.env
node_modules/
__pycache__/
*.pyc
.DS_Store
build/
.vscode/
EOF

# Add all files
git add .

# Commit
git commit -m "Initial NEXUS deployment setup"

# Create GitHub repo (do this on github.com)
# Then add remote and push:
git remote add origin https://github.com/YOUR_USERNAME/nexus-backend.git
git branch -M main
git push -u origin main
```

---

## 🔧 STEP 2: DEPLOY BACKEND TO RENDER

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your **nexus-backend** repository
3. Render will auto-detect it as Python

### 2.3 Configure Service

**Basic Settings:**
- **Name:** `nexus-backend` (or whatever you want)
- **Region:** Oregon (or closest to you)
- **Branch:** `main`
- **Root Directory:** Leave blank (or `.` if in subdirectory)
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn api_server:app`

**Instance Type:**
- **Free** (with spin-down after 15 min of inactivity)
- OR **Starter** ($7/month - always on)

### 2.4 Add Environment Variables

Click **"Environment"** and add these:

```
AIRTABLE_API_KEY = your_actual_api_key
AIRTABLE_BASE_ID = your_actual_base_id
ANTHROPIC_API_KEY = your_actual_anthropic_key
GOOGLE_API_KEY = your_google_key (optional)
GOOGLE_CSE_ID = your_google_cse_id (optional)
PORT = 8000
```

### 2.5 Deploy!

1. Click **"Create Web Service"**
2. Wait 2-5 minutes for build
3. You'll get a URL like: `https://nexus-backend-abc123.onrender.com`
4. **SAVE THIS URL** - you need it for frontend!

### 2.6 Test Backend

Visit: `https://your-backend-url.onrender.com/health`

Should see:
```json
{"service":"NEXUS Backend","status":"healthy","version":"1.0.0"}
```

✅ **Backend is live!**

---

## 🎨 STEP 3: DEPLOY FRONTEND TO NETLIFY

### 3.1 Update netlify.toml

Before deploying, update `nexus-frontend/netlify.toml`:

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://YOUR-ACTUAL-BACKEND-URL.onrender.com"
```

Replace with your actual Render backend URL!

### 3.2 Commit and Push Changes

```bash
cd "/Users/deedavis/NEXUS BACKEND"
git add nexus-frontend/netlify.toml
git commit -m "Update backend URL for production"
git push
```

### 3.3 Create Netlify Site

1. Go to [netlify.com](https://netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to GitHub
4. Select your **nexus-backend** repository

### 3.4 Configure Build Settings

Netlify should auto-detect from `netlify.toml`, but verify:

- **Base directory:** `nexus-frontend`
- **Build command:** `npm run build`
- **Publish directory:** `build`
- **Environment variables:** (should be in netlify.toml)

### 3.5 Deploy!

1. Click **"Deploy site"**
2. Wait 2-3 minutes for build
3. You'll get a URL like: `https://amazing-site-123abc.netlify.app`

### 3.6 Customize Domain (Optional)

1. Go to **Site settings** → **Domain management**
2. Click **"Change site name"**
3. Choose: `nexus-command.netlify.app` (or whatever you want)

✅ **Frontend is live!**

---

## 🔐 STEP 4: SECURITY CHECK

### Update CORS on Backend (Render)

Your backend needs to know it's okay to accept requests from Netlify.

**Option A: Allow Your Netlify Domain Only**

Edit `api_server.py`:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://nexus-command.netlify.app"])
```

**Option B: Allow Any Origin (Less Secure)**
```python
CORS(app)  # Current setup - allows all
```

Push changes and Render will auto-deploy.

---

## ✅ STEP 5: TEST YOUR LIVE DEPLOYMENT

### Test Checklist:

1. ✅ Visit your Netlify URL
2. ✅ See NEXUS landing page load
3. ✅ Check browser console (F12) for errors
4. ✅ Click into GPSS system
5. ✅ Try to fetch opportunities (should connect to backend)
6. ✅ Try AI Copilot (should talk to Claude)
7. ✅ Create a test task in ATLAS
8. ✅ Export calendar

### If Something Breaks:

**Frontend not loading?**
- Check Netlify build logs
- Verify build command and publish directory

**API calls failing?**
- Check Render backend logs
- Verify environment variables are set
- Test backend directly: `https://your-backend.onrender.com/health`

**CORS errors?**
- Update CORS settings in `api_server.py`
- Add your Netlify domain to allowed origins

---

## 💰 COST BREAKDOWN

### Free Tier (Testing/Light Use):
- **Netlify:** $0/month
- **Render:** $0/month (with 15-min spin-down)
- **Total:** **$0/month**

### Paid Tier (Production/Business Use):
- **Netlify:** $0/month (still free!)
- **Render:** $7/month (always-on, no spin-down)
- **Total:** **$7/month**

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Bookmark your Netlify URL**
2. **Share with your team**
3. **Load real RFPs and test everything**
4. **When you land a contract, upgrade Render to $7/month**
5. **Consider custom domain:** nexus.yourdomain.com

---

## 🆘 TROUBLESHOOTING

### Backend Sleeping (Free Tier)
**Problem:** First request takes 30 seconds
**Solution:** 
- Upgrade to $7/month on Render
- OR use a "ping service" to keep it awake

### Environment Variables Not Working
**Problem:** 500 errors, AI not working
**Solution:**
- Double-check all API keys in Render dashboard
- Make sure no extra spaces or quotes
- Restart service after adding vars

### Build Failing
**Problem:** Deployment fails
**Solution:**
- Check build logs on Netlify/Render
- Verify `requirements.txt` and `package.json`
- Make sure Node 18+ for frontend

---

## 🎉 YOU'RE LIVE!

Your NEXUS system is now:
- ✅ Accessible from anywhere
- ✅ Secure with HTTPS
- ✅ Auto-deploys on git push
- ✅ Professional and reliable

**Start winning government contracts!** 🚀💰
