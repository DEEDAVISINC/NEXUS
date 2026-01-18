# 🚀 NEXUS NETLIFY DEPLOYMENT - READY TO LAUNCH

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. Code Repository Status
- [x] Git repository initialized
- [ ] All changes committed
- [ ] Pushed to GitHub
- [ ] Repository is public OR Netlify has access

### 2. Frontend Configuration Files
- [x] `netlify.toml` exists in `nexus-frontend/`
- [x] `package.json` with build scripts
- [ ] Backend API URL configured in `netlify.toml`
- [x] Node version specified (Node 18)

### 3. Backend Deployment (Deploy First!)
- [ ] Backend deployed to Render (or PythonAnywhere)
- [ ] Backend URL obtained (e.g., `https://nexus-backend-xyz.onrender.com`)
- [ ] Backend `/health` endpoint tested and working
- [ ] All environment variables set on backend
- [ ] CORS configured to allow Netlify domain

### 4. Environment Variables
- [ ] Backend URL ready to add to `netlify.toml`
- [ ] No sensitive data in frontend code
- [ ] `.env` files in `.gitignore`

---

## 🎯 STEP-BY-STEP DEPLOYMENT GUIDE

### STEP 1: Deploy Backend First (Critical!)

You **MUST** deploy your backend before deploying to Netlify.

#### Option A: Render (Recommended)
```bash
# 1. Create account at render.com
# 2. New Web Service → Connect GitHub repo
# 3. Configure:
#    - Name: nexus-backend
#    - Root Directory: .
#    - Build Command: pip install -r requirements.txt
#    - Start Command: gunicorn api_server:app
#    - Add environment variables (see below)
```

**Required Environment Variables for Render:**
```
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
ANTHROPIC_API_KEY=your_anthropic_key
JWT_SECRET=your_random_secret_string
PORT=8000
```

**Optional (for full functionality):**
```
GOOGLE_API_KEY=your_google_key
GOOGLE_CSE_ID=your_cse_id
ALEXA_SKILL_ID=your_skill_id
```

#### Test Your Backend:
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "service": "NEXUS Backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### STEP 2: Update netlify.toml with Backend URL

**CRITICAL:** Update this file before deploying to Netlify!

Edit: `nexus-frontend/netlify.toml`

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://YOUR-ACTUAL-BACKEND-URL.onrender.com"

[context.deploy-preview.environment]
  REACT_APP_API_BASE = "https://YOUR-ACTUAL-BACKEND-URL.onrender.com"
```

**Replace** `YOUR-ACTUAL-BACKEND-URL` with your real Render URL!

Example:
```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://nexus-backend-abc123.onrender.com"
```

---

### STEP 3: Commit and Push Changes

```bash
cd "/Users/deedavis/NEXUS BACKEND"

# Check git status
git status

# Add modified netlify.toml
git add nexus-frontend/netlify.toml

# Commit
git commit -m "Configure backend URL for Netlify production"

# Push to GitHub
git push origin main
```

---

### STEP 4: Deploy to Netlify

#### 4.1 Create Netlify Account
1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Authorize Netlify to access your repositories

#### 4.2 Create New Site
1. Click **"Add new site"** → **"Import an existing project"**
2. Choose **"Deploy with GitHub"**
3. Select your repository: **`nexus-backend`** (or whatever you named it)
4. Click **"Configure"** if needed

#### 4.3 Configure Build Settings

Netlify should auto-detect from `netlify.toml`, but verify:

**Build Settings:**
- **Base directory:** `nexus-frontend`
- **Build command:** `npm run build`
- **Publish directory:** `build`
- **Node version:** 18 (from netlify.toml)

**Environment variables:**
- ✅ Already configured in `netlify.toml`
- No additional variables needed in Netlify dashboard

#### 4.4 Deploy!
1. Click **"Deploy site"**
2. Wait 2-3 minutes for build
3. Watch build logs for any errors
4. Get your URL: `https://random-name-123456.netlify.app`

#### 4.5 Customize Domain (Optional)
1. Go to **Site settings** → **Domain management**
2. Click **"Change site name"**
3. Choose something memorable:
   - `nexus-command.netlify.app`
   - `nexus-system.netlify.app`
   - `your-company-nexus.netlify.app`

---

### STEP 5: Update Backend CORS (Security)

After deploying to Netlify, update your backend to only accept requests from your Netlify domain.

Edit `api_server.py` (around line 65):

**Before (development):**
```python
CORS(app)  # Allows all origins
```

**After (production):**
```python
CORS(app, origins=[
    "https://nexus-command.netlify.app",  # Your actual Netlify URL
    "https://random-name-123456.netlify.app"  # Your Netlify URL
])
```

Then commit and push - Render will auto-deploy:
```bash
git add api_server.py
git commit -m "Configure CORS for Netlify production"
git push
```

---

## 🧪 TESTING YOUR DEPLOYMENT

### Test Checklist

1. **Homepage Loads**
   - [ ] Visit your Netlify URL
   - [ ] Page loads without errors
   - [ ] No console errors (F12)

2. **Backend Connection**
   - [ ] Open browser console (F12)
   - [ ] Check Network tab
   - [ ] API calls should go to your Render backend
   - [ ] Should see 200 OK responses

3. **Core Features**
   - [ ] Navigate to GPSS system
   - [ ] Try to load opportunities
   - [ ] Test AI Copilot chat
   - [ ] Navigate to ATLAS system
   - [ ] Create a test task

4. **Performance**
   - [ ] Page loads in < 3 seconds
   - [ ] No infinite loading states
   - [ ] Smooth navigation

5. **Mobile Responsive**
   - [ ] Test on phone browser
   - [ ] UI adapts to small screens
   - [ ] Touch interactions work

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: "Build failed" on Netlify

**Symptoms:**
- Netlify build logs show errors
- Site doesn't deploy

**Solutions:**
1. Check Node version in `netlify.toml` (should be 18)
2. Verify `package.json` has all dependencies
3. Test build locally first:
   ```bash
   cd nexus-frontend
   npm install
   npm run build
   ```
4. Check Netlify build logs for specific error

---

### Issue: "API calls failing" or "Network Error"

**Symptoms:**
- Frontend loads but features don't work
- Console shows `Failed to fetch` errors
- 404 or CORS errors

**Solutions:**
1. Verify backend URL in `netlify.toml`
2. Test backend directly:
   ```bash
   curl https://your-backend.onrender.com/health
   ```
3. Check CORS configuration in `api_server.py`
4. Verify environment variables in Render dashboard
5. Check Render logs for backend errors

---

### Issue: "Page not found" on refresh

**Symptoms:**
- Works on homepage
- Breaks when refreshing on any other page (e.g., `/gpss`)

**Solutions:**
Already fixed! Your `netlify.toml` has this redirect rule:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

This ensures React Router works correctly.

---

### Issue: Backend "sleeping" (slow first load)

**Symptoms:**
- First API call takes 30+ seconds
- Subsequent calls are fast
- Using Render free tier

**Solutions:**
1. **Upgrade to Render Starter** ($7/month) - instant wake-up
2. **Use UptimeRobot** (free) to ping every 5 minutes:
   - Sign up at [uptimerobot.com](https://uptimerobot.com)
   - Add monitor for: `https://your-backend.onrender.com/health`
   - Interval: 5 minutes
3. **Accept the delay** for free tier (testing only)

---

### Issue: "Invalid API Key" or "Authentication Failed"

**Symptoms:**
- AI features not working
- Airtable data not loading
- 401 or 403 errors

**Solutions:**
1. Check environment variables in Render:
   - Go to Render dashboard
   - Select your service
   - Click "Environment"
   - Verify all keys are correct
2. No extra spaces in keys
3. Test keys directly:
   - Airtable: [airtable.com/account](https://airtable.com/account)
   - Anthropic: [console.anthropic.com](https://console.anthropic.com)
4. Restart Render service after updating env vars

---

## 💰 COST BREAKDOWN

### Free Tier (Perfect for Testing)
- **Netlify:** $0/month
  - 100GB bandwidth
  - 300 build minutes/month
  - Automatic deployments
  - SSL included
- **Render (Free):** $0/month
  - 750 hours/month
  - 15-minute spin-down when idle
  - SSL included
- **Total:** **$0/month**

### Production Tier (Business Use)
- **Netlify:** $0/month (still free!)
- **Render (Starter):** $7/month
  - Always on (no spin-down)
  - Faster performance
  - 512MB RAM
- **Total:** **$7/month**

---

## 🔄 CONTINUOUS DEPLOYMENT

Once set up, deployments are automatic:

```bash
# Make changes to your code
vim nexus-frontend/src/App.tsx

# Commit and push
git add .
git commit -m "Add new feature"
git push

# Netlify automatically:
# 1. Detects push to GitHub
# 2. Runs build
# 3. Deploys to production
# 4. Takes 2-3 minutes
```

**Frontend updates:** Automatic on push to GitHub  
**Backend updates:** Automatic on push to GitHub (if using Render)

---

## 📊 MONITORING YOUR DEPLOYMENT

### Netlify Dashboard
- **Build logs:** See each deployment
- **Analytics:** Page views, load times
- **Forms:** Track form submissions (if using)
- **Functions:** Monitor serverless functions

### Render Dashboard
- **Logs:** Real-time backend logs
- **Metrics:** CPU, memory, response times
- **Events:** Deployment history

### Browser Console (F12)
- **Console tab:** JavaScript errors
- **Network tab:** API calls, load times
- **Application tab:** Storage, cache

---

## 🎯 POST-DEPLOYMENT CHECKLIST

After successful deployment:

- [ ] Bookmark your Netlify URL
- [ ] Test all 7 systems (GPSS, ATLAS, DDCSS, VERTEX, GBIS, LBPC, ProposalBio)
- [ ] Set up UptimeRobot (if using Render free tier)
- [ ] Share URL with team
- [ ] Update CORS in backend with actual Netlify domain
- [ ] Set up custom domain (optional)
- [ ] Load real data and test end-to-end
- [ ] Document any custom configurations
- [ ] Set calendar reminder to rotate API keys (90 days)

---

## 🆘 NEED HELP?

### Documentation
- **Netlify Docs:** [docs.netlify.com](https://docs.netlify.com)
- **Render Docs:** [render.com/docs](https://render.com/docs)
- **React Build:** [create-react-app.dev](https://create-react-app.dev)

### Support
- **Netlify Community:** [answers.netlify.com](https://answers.netlify.com)
- **Render Community:** [community.render.com](https://community.render.com)

### Your NEXUS Documentation
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `PRODUCTION_ENV_VARS.md` - Environment variables reference
- `TROUBLESHOOTING_GUIDE.md` - Common issues
- `QUICK_REFERENCE.md` - Quick commands

---

## 🎉 YOU'RE READY TO DEPLOY!

### Quick Command Summary

```bash
# 1. Deploy backend to Render (via dashboard)
#    Get your backend URL

# 2. Update netlify.toml
# Edit: nexus-frontend/netlify.toml
# Set REACT_APP_API_BASE to your Render URL

# 3. Commit and push
cd "/Users/deedavis/NEXUS BACKEND"
git add nexus-frontend/netlify.toml
git commit -m "Configure backend URL for production"
git push origin main

# 4. Deploy to Netlify (via dashboard)
#    - Import from GitHub
#    - Base directory: nexus-frontend
#    - Build command: npm run build
#    - Publish directory: build

# 5. Test your deployment!
#    Visit your Netlify URL and try all features
```

---

**Your NEXUS Command Center will be live in ~10 minutes! 🚀**
