# ✅ NEXUS DEPLOYMENT CHECKLIST

Use this checklist to deploy NEXUS to production!

---

## 📦 PRE-DEPLOYMENT

- [ ] All code committed to Git
- [ ] GitHub repository created and pushed
- [ ] `.env` file NOT committed (check .gitignore)
- [ ] Have all API keys ready:
  - [ ] Airtable API Key
  - [ ] Airtable Base ID
  - [ ] Anthropic (Claude) API Key
  - [ ] Google API Key (optional)
  - [ ] Google CSE ID (optional)

---

## 🔧 BACKEND DEPLOYMENT (Render)

- [ ] Render account created
- [ ] Connected GitHub to Render
- [ ] Created new Web Service
- [ ] Selected Python runtime
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `gunicorn api_server:app`
- [ ] Added all environment variables
- [ ] Clicked "Create Web Service"
- [ ] Build completed successfully
- [ ] Tested `/health` endpoint
- [ ] Saved backend URL: `_________________________`

---

## 🎨 FRONTEND DEPLOYMENT (Netlify)

- [ ] Updated `netlify.toml` with backend URL
- [ ] Committed and pushed changes
- [ ] Netlify account created
- [ ] Connected GitHub to Netlify
- [ ] Selected repository
- [ ] Verified build settings:
  - [ ] Base directory: `nexus-frontend`
  - [ ] Build command: `npm run build`
  - [ ] Publish directory: `build`
- [ ] Clicked "Deploy site"
- [ ] Build completed successfully
- [ ] Site is live
- [ ] Changed site name (optional)
- [ ] Saved frontend URL: `_________________________`

---

## ✅ POST-DEPLOYMENT TESTING

- [ ] Frontend loads without errors
- [ ] No console errors (F12 developer tools)
- [ ] Can navigate between systems
- [ ] GPSS system loads
- [ ] Can fetch opportunities from Airtable
- [ ] ATLAS system loads
- [ ] Can create tasks
- [ ] DDCSS system loads
- [ ] Invoice system loads
- [ ] AI Copilot button appears
- [ ] AI Copilot opens and responds
- [ ] Calendar export works
- [ ] All systems connect to backend successfully

---

## 🔐 SECURITY

- [ ] CORS configured in backend
- [ ] Environment variables set (not hardcoded)
- [ ] `.env` file in .gitignore
- [ ] HTTPS working on both sites
- [ ] API keys not exposed in frontend code

---

## 💰 BILLING

Current Plan:
- [ ] Netlify: Free
- [ ] Render: Free (with spin-down) OR $7/month (always-on)

Plan to upgrade Render when:
- [ ] First contract won
- [ ] Need always-on reliability
- [ ] Spin-down delay is annoying

---

## 📝 NOTES

**Frontend URL:** ___________________________________________

**Backend URL:** ___________________________________________

**Deployment Date:** ___________________________________________

**Issues Encountered:** 




**Next Steps:**




---

## 🎉 DEPLOYMENT COMPLETE!

Once all boxes are checked, you're live! 🚀

Share your NEXUS URL with your team and start winning contracts!
