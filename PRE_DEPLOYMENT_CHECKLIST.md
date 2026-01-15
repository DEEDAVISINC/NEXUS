# NEXUS Pre-Deployment Checklist

## Before You Deploy - Complete This Checklist

---

## 1. Code Repository

- [ ] All code committed to git
- [ ] No uncommitted changes (`git status` is clean)
- [ ] Pushed to GitHub (`git push origin main`)
- [ ] Repository is accessible (not private, or deployment service has access)

**Verify:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
git status
git push origin main
```

---

## 2. Backend Files

- [ ] `requirements.txt` includes all dependencies
- [ ] `requirements.txt` includes `gunicorn`
- [ ] `api_server.py` exists and is working
- [ ] `nexus_backend.py` exists
- [ ] `render.yaml` is configured
- [ ] `.gitignore` excludes `.env` files

**Verify:**
```bash
# Check requirements.txt includes gunicorn
grep "gunicorn" requirements.txt

# Check api_server.py exists
ls -la api_server.py

# Check render.yaml exists
ls -la render.yaml
```

---

## 3. Frontend Files

- [ ] `nexus-frontend/package.json` exists
- [ ] `nexus-frontend/netlify.toml` exists
- [ ] `netlify.toml` has correct build settings
- [ ] All React dependencies are listed in `package.json`
- [ ] Frontend builds successfully locally

**Verify:**
```bash
cd nexus-frontend
npm install
npm run build
# Should complete without errors
```

---

## 4. API Keys Ready

- [ ] Airtable API Key obtained
- [ ] Airtable Base ID obtained
- [ ] Anthropic (Claude) API Key obtained
- [ ] JWT Secret generated (random string)
- [ ] Google API Key (optional, for mining)
- [ ] Google CSE ID (optional, for mining)

**Where to get keys:**
- Airtable: [airtable.com/account](https://airtable.com/account)
- Anthropic: [console.anthropic.com](https://console.anthropic.com)
- Google: [console.cloud.google.com](https://console.cloud.google.com)

---

## 5. Accounts Created

- [ ] GitHub account (with NEXUS BACKEND repo)
- [ ] Render account created
- [ ] Netlify account created
- [ ] Render authorized to access GitHub
- [ ] Netlify authorized to access GitHub

**Create accounts:**
- Render: [render.com](https://render.com)
- Netlify: [netlify.com](https://netlify.com)

---

## 6. Local Testing Complete

- [ ] Backend runs locally (`python api_server.py`)
- [ ] Frontend runs locally (`npm start`)
- [ ] Health endpoint works: `http://localhost:8000/health`
- [ ] Frontend connects to backend
- [ ] All systems tested (GPSS, ATLAS, DDCSS, etc.)
- [ ] No console errors in browser

**Test locally:**
```bash
# Terminal 1: Start backend
cd "/Users/deedavis/NEXUS BACKEND"
python api_server.py

# Terminal 2: Start frontend
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start

# Visit: http://localhost:3000
# Check browser console (F12) for errors
```

---

## 7. Configuration Files

### Backend (render.yaml)

- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn api_server:app`
- [ ] Environment variables listed
- [ ] Region set (e.g., oregon)
- [ ] Plan set (free or starter)

### Frontend (netlify.toml)

- [ ] Base directory: `nexus-frontend`
- [ ] Build command: `npm run build`
- [ ] Publish directory: `build`
- [ ] Node version: 18
- [ ] Redirects configured for SPA
- [ ] Environment variables section exists

---

## 8. Security

- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in source code
- [ ] No hardcoded secrets
- [ ] JWT_SECRET is random and strong
- [ ] CORS will be configured for production domain

**Check:**
```bash
# Verify .env is ignored
grep "\.env" .gitignore

# Search for any hardcoded keys (should find none in source)
grep -r "sk-ant-api" . --exclude-dir=node_modules --exclude-dir=.git
```

---

## 9. Airtable Setup

- [ ] Airtable base exists
- [ ] All required tables created:
  - [ ] GPSS_Opportunities
  - [ ] GPSS_Proposals
  - [ ] GPSS_Contacts
  - [ ] GPSS_Products
  - [ ] ATLAS_Projects
  - [ ] ATLAS_Tasks
  - [ ] DDCSS_Prospects
  - [ ] Invoices
  - [ ] LBPC_Leads
  - [ ] GBIS_Opportunities
- [ ] API access enabled
- [ ] Base ID copied

**Verify:**
- Open Airtable base
- Check all tables exist
- Test API key works

---

## 10. Documentation Review

- [ ] Read `NETLIFY_DEPLOYMENT_GUIDE.md`
- [ ] Read `NETLIFY_QUICK_START.md`
- [ ] Read `PRODUCTION_ENV_VARS.md`
- [ ] Understand deployment process
- [ ] Know how to check logs

---

## 11. Deployment Plan

- [ ] Understand backend deploys first (to get URL)
- [ ] Know how to update frontend with backend URL
- [ ] Know how to add environment variables
- [ ] Understand auto-deployment on git push
- [ ] Know where to find logs

---

## 12. Backup Plan

- [ ] Airtable data backed up
- [ ] Local copy of all code
- [ ] API keys stored securely (password manager)
- [ ] Know how to rollback if needed

---

## 13. Testing Plan

After deployment, test:

- [ ] Landing page loads
- [ ] No console errors
- [ ] GPSS system works
- [ ] ATLAS system works
- [ ] DDCSS system works
- [ ] LBPC system works
- [ ] GBIS system works
- [ ] AI Copilot responds
- [ ] Invoice generation works
- [ ] Data saves to Airtable

---

## 14. Post-Deployment

- [ ] Backend URL saved
- [ ] Frontend URL saved
- [ ] URLs bookmarked
- [ ] Team members notified
- [ ] Monitoring set up
- [ ] Ready to share with clients

---

## Quick Pre-Flight Check

Run these commands to verify everything is ready:

```bash
# 1. Check git status
cd "/Users/deedavis/NEXUS BACKEND"
git status

# 2. Verify requirements.txt has gunicorn
grep "gunicorn" requirements.txt

# 3. Test backend locally
python api_server.py &
sleep 5
curl http://localhost:8000/health
kill %1

# 4. Test frontend build
cd nexus-frontend
npm install
npm run build

# 5. Check netlify.toml exists
ls -la netlify.toml

# 6. Verify no .env in git
git ls-files | grep "\.env$"
# Should return nothing
```

---

## Ready to Deploy?

If all checkboxes are checked:

✅ **You're ready to deploy!**

Follow these guides in order:
1. `NETLIFY_QUICK_START.md` - Fast deployment
2. `NETLIFY_DEPLOYMENT_GUIDE.md` - Detailed instructions
3. `PRODUCTION_ENV_VARS.md` - Environment variables reference

---

## Not Ready Yet?

Missing items? Here's what to do:

### Missing Dependencies
```bash
cd "/Users/deedavis/NEXUS BACKEND"
pip install -r requirements.txt
cd nexus-frontend
npm install
```

### Missing API Keys
- Get Airtable key: [airtable.com/account](https://airtable.com/account)
- Get Anthropic key: [console.anthropic.com](https://console.anthropic.com)

### Build Errors
- Check error messages
- Verify all imports work
- Test locally first

### Git Issues
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

---

## Support

If you get stuck:
- Review deployment guides
- Check Render/Netlify documentation
- Look at build logs for errors
- Test each component individually

---

## You've Got This! 🚀

Once this checklist is complete, deployment should be smooth and straightforward.

**Estimated deployment time:** 10-15 minutes  
**Total cost:** $0/month (or $7/month for always-on backend)

Let's deploy NEXUS! 💪
