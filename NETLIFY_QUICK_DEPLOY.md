# ⚡ NEXUS NETLIFY - QUICK DEPLOY

> **Copy-paste commands to deploy NEXUS to Netlify in 10 minutes**

---

## 🎯 DEPLOYMENT SEQUENCE

### 1️⃣ DEPLOY BACKEND FIRST
**Platform:** Render.com (recommended)

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   ```
   Name: nexus-backend
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn api_server:app
   ```
5. Add environment variables (click "Add Environment Variable"):
   ```
   AIRTABLE_API_KEY = your_key_here
   AIRTABLE_BASE_ID = your_base_id_here
   ANTHROPIC_API_KEY = your_anthropic_key_here
   JWT_SECRET = random_secret_string_here
   PORT = 8000
   ```
6. Click **"Create Web Service"** and wait for deployment
7. **SAVE YOUR URL:** `https://nexus-backend-XXXXX.onrender.com`

---

### 2️⃣ TEST BACKEND
```bash
# Replace with your actual URL
curl https://your-backend-url.onrender.com/health
```

**Expected response:**
```json
{"service":"NEXUS Backend","status":"healthy","version":"1.0.0"}
```

---

### 3️⃣ UPDATE FRONTEND CONFIG

Edit file: `nexus-frontend/netlify.toml`

**Find this line:**
```toml
REACT_APP_API_BASE = "https://your-backend-url-here.com"
```

**Replace with your actual backend URL:**
```toml
REACT_APP_API_BASE = "https://nexus-backend-XXXXX.onrender.com"
```

---

### 4️⃣ RUN PRE-FLIGHT CHECK

```bash
cd "/Users/deedavis/NEXUS BACKEND"
./preflight_check.sh
```

This script will:
- ✅ Check all required files exist
- ✅ Verify backend URL is configured
- ✅ Test local build
- ✅ Check git status
- ✅ Test backend connectivity

---

### 5️⃣ COMMIT & PUSH

```bash
cd "/Users/deedavis/NEXUS BACKEND"

# Check what changed
git status

# Add your changes
git add nexus-frontend/netlify.toml
git add NETLIFY_DEPLOYMENT_READY.md
git add NETLIFY_QUICK_DEPLOY.md
git add preflight_check.sh
git add nexus-frontend/_redirects

# Commit
git commit -m "Configure NEXUS for Netlify deployment"

# Push to GitHub
git push origin main
```

---

### 6️⃣ DEPLOY TO NETLIFY

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Choose **GitHub** → Select your repository
5. Netlify auto-detects settings from `netlify.toml`:
   - Base directory: `nexus-frontend`
   - Build command: `npm run build`
   - Publish directory: `build`
6. Click **"Deploy site"**
7. Wait 2-3 minutes for build
8. **GET YOUR URL:** `https://random-name-123456.netlify.app`

---

### 7️⃣ CUSTOMIZE DOMAIN (Optional)

1. In Netlify dashboard, go to **Site settings**
2. Click **Domain management**
3. Click **"Change site name"**
4. Choose a name:
   - `nexus-command.netlify.app`
   - `your-company-nexus.netlify.app`

---

### 8️⃣ UPDATE BACKEND CORS

Edit: `api_server.py` (line ~65)

**Change from:**
```python
CORS(app)  # Allows all origins
```

**Change to:**
```python
CORS(app, origins=[
    "https://nexus-command.netlify.app",  # Your Netlify URL
])
```

**Then push:**
```bash
git add api_server.py
git commit -m "Configure CORS for Netlify"
git push
```

Render will auto-redeploy.

---

## 🧪 TEST YOUR DEPLOYMENT

Visit your Netlify URL and test:

1. ✅ Homepage loads
2. ✅ Open browser console (F12) - no errors
3. ✅ Navigate to GPSS system
4. ✅ Try loading opportunities
5. ✅ Test AI Copilot chat
6. ✅ Navigate to ATLAS
7. ✅ Create a test task

---

## 🚨 TROUBLESHOOTING

### Build Fails on Netlify
```bash
# Test build locally first
cd nexus-frontend
npm install
npm run build

# If it works locally, check Netlify build logs
# for specific error messages
```

### API Calls Not Working
```bash
# 1. Check backend is running
curl https://your-backend.onrender.com/health

# 2. Check browser console (F12) for CORS errors

# 3. Verify backend URL in netlify.toml
cat nexus-frontend/netlify.toml | grep REACT_APP_API_BASE

# 4. Check backend logs in Render dashboard
```

### Backend Sleeping (Render Free Tier)
- First request takes 30+ seconds
- **Solution:** Upgrade to Render Starter ($7/month)
- **Or:** Use UptimeRobot to ping every 5 min (free)

---

## 📝 QUICK REFERENCE

### Important URLs
```
GitHub Repo: https://github.com/YOUR_USERNAME/nexus-backend
Render Backend: https://nexus-backend-XXXXX.onrender.com
Netlify Frontend: https://your-site-name.netlify.app
```

### Environment Variables Needed
**Render Backend:**
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`
- `ANTHROPIC_API_KEY`
- `JWT_SECRET`
- `PORT=8000`

**Netlify Frontend:**
- `REACT_APP_API_BASE` (in netlify.toml)

### Key Files
```
nexus-frontend/
├── netlify.toml         # Netlify config
├── package.json         # Dependencies
└── src/
    └── api/client.ts    # API calls

api_server.py            # Backend server
requirements.txt         # Python dependencies
preflight_check.sh       # Pre-deploy check
```

---

## 💰 COSTS

### Free Tier
- Netlify: **$0/month**
- Render: **$0/month** (sleeps after 15 min idle)
- **Total: $0/month**

### Production
- Netlify: **$0/month**
- Render Starter: **$7/month** (always on)
- **Total: $7/month**

---

## 🎉 DONE!

Your NEXUS Command Center is now live and accessible from anywhere!

**Share your URL:**
```
🚀 NEXUS Command Center: https://your-site.netlify.app
```

---

## 📚 MORE HELP

- **Full Guide:** `NETLIFY_DEPLOYMENT_READY.md`
- **Environment Vars:** `PRODUCTION_ENV_VARS.md`
- **Troubleshooting:** `TROUBLESHOOTING_GUIDE.md`
- **General Deployment:** `DEPLOYMENT_GUIDE.md`

---

**Questions?** Check the docs or test locally first with:
```bash
cd nexus-frontend
npm start
```

**Everything working locally?** Then it will work on Netlify! 🚀
