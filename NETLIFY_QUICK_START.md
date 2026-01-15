# NEXUS Netlify Quick Start

## 5-Minute Deployment Checklist

### Prerequisites (Have These Ready)
- [ ] GitHub account with NEXUS BACKEND repo
- [ ] Airtable API Key
- [ ] Airtable Base ID
- [ ] Anthropic API Key

---

## Step 1: Deploy Backend (5 minutes)

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select **NEXUS BACKEND** repo
4. Configure:
   - Name: `nexus-backend`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn api_server:app --bind 0.0.0.0:$PORT`
   - Plan: Free (or $7/month Starter)
5. Add Environment Variables:
   ```
   AIRTABLE_API_KEY = your_key
   AIRTABLE_BASE_ID = your_base_id
   ANTHROPIC_API_KEY = your_key
   PORT = 8000
   ```
6. Click **"Create Web Service"**
7. Wait 3-5 minutes
8. **COPY YOUR URL:** `https://nexus-backend-xxxxx.onrender.com`
9. Test: Visit `https://your-url.onrender.com/health`

✅ Backend Done!

---

## Step 2: Update Frontend Config (1 minute)

1. Edit `nexus-frontend/netlify.toml`
2. Replace this line:
   ```toml
   REACT_APP_API_BASE = "https://your-backend-app.onrender.com"
   ```
   With your actual Render URL:
   ```toml
   REACT_APP_API_BASE = "https://nexus-backend-xxxxx.onrender.com"
   ```
3. Save and commit:
   ```bash
   git add nexus-frontend/netlify.toml
   git commit -m "Configure production backend URL"
   git push origin main
   ```

✅ Config Updated!

---

## Step 3: Deploy Frontend (3 minutes)

1. Go to [netlify.com](https://netlify.com) → Sign up with GitHub
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"Deploy with GitHub"**
4. Select **NEXUS BACKEND** repo
5. Netlify auto-detects settings from `netlify.toml`:
   - Base: `nexus-frontend`
   - Build: `npm run build`
   - Publish: `build`
6. Click **"Deploy site"**
7. Wait 3-4 minutes
8. **YOUR SITE IS LIVE!** `https://amazing-site-xxxxx.netlify.app`

✅ Frontend Done!

---

## Step 4: Test (2 minutes)

1. Visit your Netlify URL
2. Open browser console (F12)
3. Click through systems:
   - GPSS → Fetch opportunities
   - ATLAS → Create task
   - AI Copilot → Ask a question
4. Check for errors in console

✅ Everything Works!

---

## Optional: Custom Domain (2 minutes)

1. In Netlify: **Site settings** → **Domain management**
2. Click **"Options"** → **"Edit site name"**
3. Choose: `nexus-command.netlify.app`

✅ Professional URL!

---

## Troubleshooting

### CORS Errors?
Edit `api_server.py`:
```python
CORS(app, origins=["https://your-netlify-site.netlify.app"])
```
Push to GitHub, Render auto-redeploys.

### Backend Slow?
Free tier spins down after 15 min. First request takes 30-60 seconds.
Upgrade to $7/month for always-on.

### Build Fails?
Check logs in Netlify/Render dashboard.

---

## You're Live! 🚀

**Frontend:** https://your-site.netlify.app  
**Backend:** https://your-backend.onrender.com

**Total Time:** ~10 minutes  
**Total Cost:** $0/month (or $7/month for always-on backend)

Now go win those government contracts! 💰
