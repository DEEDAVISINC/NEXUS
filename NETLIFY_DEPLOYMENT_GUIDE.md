# NEXUS Netlify Deployment Guide

## Overview
This guide will walk you through deploying the NEXUS system to production using:
- **Netlify** for the React frontend (free, fast, global CDN)
- **Render** for the Python backend API (free tier or $7/month)

---

## Prerequisites

Before starting, ensure you have:

1. **GitHub Account** - Your code repository
2. **Netlify Account** - Sign up at [netlify.com](https://netlify.com)
3. **Render Account** - Sign up at [render.com](https://render.com)
4. **API Keys Ready:**
   - Airtable API Key
   - Airtable Base ID
   - Anthropic (Claude) API Key
   - Google API Key (optional)
   - Google CSE ID (optional)

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
│   RENDER (Backend)  │  ← Python/Flask API (api_server.py)
│  Python Runtime     │  ← Free or $7/month
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

## Step 1: Prepare Your Code

### 1.1 Ensure Git Repository is Clean

```bash
cd "/Users/deedavis/NEXUS BACKEND"
git status
```

### 1.2 Commit Any Pending Changes

```bash
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

### 1.3 Verify Files Are Ready

Ensure these files exist:
- ✅ `nexus-frontend/netlify.toml` (already configured)
- ✅ `requirements.txt` (includes gunicorn)
- ✅ `render.yaml` (backend config)
- ✅ `api_server.py` (backend entry point)

---

## Step 2: Deploy Backend to Render (First!)

**Important:** Deploy the backend FIRST so you have the API URL for the frontend.

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Get Started" and sign up with GitHub
3. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. From Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Find and select your **NEXUS BACKEND** repository
4. Click **"Connect"**

### 2.3 Configure Service Settings

Render should auto-detect from `render.yaml`, but verify:

**Basic Settings:**
- **Name:** `nexus-backend` (or your preferred name)
- **Region:** Oregon (or closest to you)
- **Branch:** `main`
- **Root Directory:** Leave blank (deploys from root)
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn api_server:app --bind 0.0.0.0:$PORT`

**Instance Type:**
- **Free** - Spins down after 15 min inactivity (good for testing)
- **Starter ($7/month)** - Always on, no spin-down (recommended for production)

### 2.4 Add Environment Variables

Click **"Environment"** tab and add these variables:

```
AIRTABLE_API_KEY = your_actual_airtable_api_key
AIRTABLE_BASE_ID = your_actual_base_id
ANTHROPIC_API_KEY = your_actual_anthropic_api_key
GOOGLE_API_KEY = your_google_api_key (optional)
GOOGLE_CSE_ID = your_google_cse_id (optional)
JWT_SECRET = your_random_secret_key
PORT = 8000
```

**How to find your keys:**
- **Airtable API Key:** [airtable.com/account](https://airtable.com/account)
- **Airtable Base ID:** Open your base, look in URL: `airtable.com/appXXXXXXXXXXXXXX`
- **Anthropic API Key:** [console.anthropic.com](https://console.anthropic.com)

### 2.5 Deploy Backend

1. Click **"Create Web Service"**
2. Wait 2-5 minutes for build and deployment
3. Once deployed, you'll see a URL like: `https://nexus-backend-abc123.onrender.com`
4. **COPY THIS URL** - you'll need it for the frontend!

### 2.6 Test Backend

Visit: `https://your-backend-url.onrender.com/health`

You should see:
```json
{
  "service": "NEXUS Backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

✅ **Backend is live!**

---

## Step 3: Update Frontend Configuration

### 3.1 Update netlify.toml with Your Backend URL

Edit `nexus-frontend/netlify.toml` and replace the placeholder URL:

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://YOUR-ACTUAL-BACKEND-URL.onrender.com"

[context.deploy-preview.environment]
  REACT_APP_API_BASE = "https://YOUR-ACTUAL-BACKEND-URL.onrender.com"
```

**Example:**
```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://nexus-backend-abc123.onrender.com"
```

### 3.2 Commit and Push Changes

```bash
cd "/Users/deedavis/NEXUS BACKEND"
git add nexus-frontend/netlify.toml
git commit -m "Update backend URL for production deployment"
git push origin main
```

---

## Step 4: Deploy Frontend to Netlify

### 4.1 Create Netlify Account
1. Go to [netlify.com](https://netlify.com)
2. Click "Sign up" and choose "GitHub"
3. Authorize Netlify to access your repositories

### 4.2 Import Your Project
1. From Netlify dashboard, click **"Add new site"** → **"Import an existing project"**
2. Choose **"Deploy with GitHub"**
3. Authorize Netlify if prompted
4. Select your **NEXUS BACKEND** repository

### 4.3 Configure Build Settings

Netlify should auto-detect settings from `netlify.toml`:

**Verify these settings:**
- **Base directory:** `nexus-frontend`
- **Build command:** `npm run build`
- **Publish directory:** `nexus-frontend/build`
- **Node version:** 18 (set in netlify.toml)

**Environment Variables:**
These are already in `netlify.toml`, but you can verify in Netlify UI:
- `REACT_APP_API_BASE` = Your Render backend URL

### 4.4 Deploy Frontend

1. Click **"Deploy site"**
2. Netlify will:
   - Clone your repo
   - Install dependencies (`npm install`)
   - Build React app (`npm run build`)
   - Deploy to global CDN
3. Wait 2-4 minutes for build
4. You'll get a URL like: `https://amazing-site-123abc.netlify.app`

### 4.5 Customize Your Domain (Optional)

1. Go to **Site settings** → **Domain management**
2. Click **"Options"** → **"Edit site name"**
3. Choose a custom subdomain: `nexus-command.netlify.app`
4. Or add your own custom domain

✅ **Frontend is live!**

---

## Step 5: Configure CORS (Security)

Your backend needs to accept requests from your Netlify domain.

### 5.1 Update api_server.py

Find the CORS configuration in `api_server.py` and update it:

```python
from flask_cors import CORS

app = Flask(__name__)

# Option A: Secure - Allow only your Netlify domain
CORS(app, origins=[
    "https://nexus-command.netlify.app",  # Your production URL
    "http://localhost:3000"  # For local development
])

# Option B: Less secure but easier - Allow all origins
# CORS(app)
```

### 5.2 Push Changes

```bash
git add api_server.py
git commit -m "Update CORS for Netlify domain"
git push origin main
```

Render will automatically redeploy your backend.

---

## Step 6: Test Your Live Deployment

### 6.1 Open Your Netlify Site

Visit your Netlify URL: `https://your-site.netlify.app`

### 6.2 Test Checklist

1. ✅ Landing page loads correctly
2. ✅ No console errors (press F12 to check)
3. ✅ Navigate to GPSS system
4. ✅ Try to fetch opportunities (tests backend connection)
5. ✅ Test AI Copilot (tests Claude API)
6. ✅ Navigate to ATLAS system
7. ✅ Create a test task
8. ✅ Try DDCSS prospect qualification
9. ✅ Test invoice generation

### 6.3 Check Browser Console

Press **F12** → **Console** tab

**Good signs:**
- No red errors
- API calls show 200 status
- Data loads successfully

**Bad signs (and fixes):**
- **CORS errors** → Update CORS in api_server.py
- **404 on API calls** → Check REACT_APP_API_BASE in netlify.toml
- **500 errors** → Check Render logs, verify environment variables

---

## Step 7: Monitor and Maintain

### 7.1 Netlify Dashboard
- **Deploys:** See build history and logs
- **Functions:** Monitor serverless functions (if any)
- **Analytics:** Track site traffic (free basic analytics)

### 7.2 Render Dashboard
- **Logs:** Real-time backend logs
- **Metrics:** CPU, memory, response times
- **Environment:** Update API keys anytime

### 7.3 Automatic Deployments

Both platforms auto-deploy on git push:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

- Netlify rebuilds frontend automatically
- Render redeploys backend automatically

---

## Troubleshooting

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
- Verify `REACT_APP_API_BASE` in netlify.toml
- Check that backend URL is correct and accessible
- Test backend directly: `https://your-backend.onrender.com/health`

### Backend Issues

**Problem:** Backend not responding (Free tier)
**Solution:**
- First request may take 30-60 seconds (cold start)
- Upgrade to $7/month Starter plan for always-on
- Or use a ping service to keep it awake

**Problem:** 500 Internal Server Error
**Solution:**
- Check Render logs for Python errors
- Verify all environment variables are set correctly
- Test Airtable and Anthropic API keys

**Problem:** CORS errors
**Solution:**
- Update CORS origins in `api_server.py`
- Add your Netlify domain to allowed origins
- Restart backend service after changes

### Environment Variable Issues

**Problem:** API keys not working
**Solution:**
- Double-check keys in Render dashboard
- No extra spaces or quotes around values
- Restart service after adding/updating variables

---

## Cost Breakdown

### Free Tier (Perfect for Testing)
- **Netlify:** $0/month
  - 100 GB bandwidth
  - 300 build minutes/month
  - Automatic HTTPS
  - Global CDN
- **Render:** $0/month
  - 750 hours/month
  - Spins down after 15 min inactivity
  - 30-60 second cold start
- **Total:** **$0/month**

### Production Tier (Recommended for Business)
- **Netlify:** $0/month (still free!)
- **Render Starter:** $7/month
  - Always on, no spin-down
  - Instant response times
  - Better performance
- **Total:** **$7/month**

### Pro Tier (High Traffic)
- **Netlify Pro:** $19/month
  - 400 GB bandwidth
  - 1000 build minutes
  - Advanced features
- **Render Standard:** $25/month
  - More CPU/RAM
  - Better scaling
- **Total:** **$44/month**

---

## Next Steps

### Immediate Actions
1. ✅ Bookmark your Netlify URL
2. ✅ Share with your team
3. ✅ Test all systems thoroughly
4. ✅ Load real data and RFPs

### When You Land Your First Contract
1. Upgrade Render to $7/month (no more spin-down)
2. Consider custom domain: `nexus.yourdomain.com`
3. Set up monitoring and alerts
4. Enable Netlify Analytics

### Future Enhancements
1. **Custom Domain:** Point your own domain to Netlify
2. **Email Notifications:** Set up alerts for new opportunities
3. **Backup Strategy:** Regular Airtable backups
4. **Team Access:** Add team members to Netlify/Render
5. **CI/CD Pipeline:** Automated testing before deploy

---

## Security Best Practices

### API Keys
- ✅ Never commit API keys to git
- ✅ Use environment variables only
- ✅ Rotate keys periodically
- ✅ Use different keys for dev/prod

### CORS
- ✅ Restrict to specific domains in production
- ✅ Don't use wildcard (*) in production
- ✅ Test thoroughly after CORS changes

### HTTPS
- ✅ Netlify provides automatic HTTPS
- ✅ Render provides automatic HTTPS
- ✅ Never use HTTP in production

### Access Control
- ✅ Limit who has access to Netlify/Render dashboards
- ✅ Use strong passwords
- ✅ Enable 2FA on all accounts

---

## Support Resources

### Netlify
- **Docs:** [docs.netlify.com](https://docs.netlify.com)
- **Support:** [community.netlify.com](https://community.netlify.com)
- **Status:** [netlifystatus.com](https://netlifystatus.com)

### Render
- **Docs:** [render.com/docs](https://render.com/docs)
- **Support:** [community.render.com](https://community.render.com)
- **Status:** [status.render.com](https://status.render.com)

### NEXUS System
- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** All MD files in this repo

---

## Quick Reference Commands

### Local Development
```bash
# Start backend locally
cd "/Users/deedavis/NEXUS BACKEND"
python api_server.py

# Start frontend locally
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

### Deploy Updates
```bash
# From NEXUS BACKEND directory
git add .
git commit -m "Your update message"
git push origin main

# Both Netlify and Render will auto-deploy!
```

### View Logs
```bash
# Netlify: Check dashboard → Deploys → Deploy log
# Render: Check dashboard → Logs tab
```

---

## Success Checklist

Before going live with clients:

- [ ] Backend deployed to Render
- [ ] Backend health check returns 200
- [ ] Frontend deployed to Netlify
- [ ] Frontend loads without errors
- [ ] All environment variables set correctly
- [ ] CORS configured properly
- [ ] All systems tested (GPSS, DDCSS, ATLAS, LBPC, GBIS)
- [ ] AI Copilot working
- [ ] Invoice generation working
- [ ] Custom domain configured (optional)
- [ ] Team members have access
- [ ] Monitoring set up
- [ ] Backup strategy in place

---

## Congratulations!

Your NEXUS system is now:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Secure with HTTPS
- ✅ Auto-deploys on git push
- ✅ Professional and reliable
- ✅ Ready to win government contracts!

**Now go land those RFPs!** 🚀💰
