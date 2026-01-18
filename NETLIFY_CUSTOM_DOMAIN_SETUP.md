# 🚀 NEXUS Deployment - Using Your Existing Netlify Account

**Your Domain:** deedavis.biz  
**Account:** Existing Netlify account

---

## 🎯 DEPLOYMENT OPTIONS

You have two options for deploying NEXUS:

### Option 1: Subdomain (Recommended)
Deploy NEXUS as a subdomain of your existing domain:
- **URL:** `nexus.deedavis.biz` or `app.deedavis.biz`
- **Benefit:** Professional URL, maintains brand consistency
- **Setup:** Easiest, just add DNS record

### Option 2: Separate Site
Keep NEXUS as a separate Netlify site:
- **URL:** `nexus-command.netlify.app`
- **Benefit:** Completely separate from main site
- **Setup:** No DNS changes needed

**Recommendation:** Use Option 1 (subdomain) for a more professional setup.

---

## 🚀 QUICK DEPLOYMENT TO YOUR ACCOUNT

### STEP 1: Deploy Backend to PythonAnywhere (If Not Done)

**See detailed guide:** `NETLIFY_PYTHONANYWHERE_DEPLOY.md`

**Quick steps:**
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create account (free or Hacker $5/month for custom domains)
3. Upload code via git: `git clone https://github.com/YOUR_USERNAME/nexus-backend.git`
4. Create virtual environment: `mkvirtualenv --python=/usr/bin/python3.10 nexus-env`
5. Install dependencies: `pip install -r requirements.txt`
6. Configure Web App (Manual configuration, Python 3.10)
7. Edit WSGI file to point to your app
8. Create `.env` file with environment variables:
   ```
   AIRTABLE_API_KEY=your_key
   AIRTABLE_BASE_ID=your_base_id
   ANTHROPIC_API_KEY=your_anthropic_key
   JWT_SECRET=random_secret_string
   ```
9. Reload web app
10. Get URL: `https://yourusername.pythonanywhere.com`

---

### STEP 2: Update Frontend Config

Edit `nexus-frontend/netlify.toml` (lines 14, 19, 24):

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"

[context.deploy-preview.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"

[context.branch-deploy.environment]
  REACT_APP_API_BASE = "https://yourusername.pythonanywhere.com"
```

**Replace `yourusername` with your actual PythonAnywhere username!**

---

### STEP 3: Run Pre-Flight Check

```bash
cd "/Users/deedavis/NEXUS BACKEND"
./preflight_check.sh
```

This verifies everything is ready.

---

### STEP 4: Commit and Push

```bash
cd "/Users/deedavis/NEXUS BACKEND"

# Add all new files
git add nexus-frontend/netlify.toml
git add nexus-frontend/_redirects
git add preflight_check.sh
git add *.md

# Commit
git commit -m "Configure NEXUS for Netlify with custom domain"

# Push to GitHub
git push origin main
```

---

### STEP 5: Deploy to Your Netlify Account

#### Using Netlify Dashboard:

1. **Log in to Netlify** at [app.netlify.com](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"Deploy with GitHub"**
4. Select your **nexus-backend** repository
5. Netlify detects settings from `netlify.toml`:
   - Base directory: `nexus-frontend` ✅
   - Build command: `npm run build` ✅
   - Publish directory: `build` ✅
6. Click **"Deploy site"**
7. Wait 2-3 minutes for build

You'll get a temporary URL like: `https://random-name-123456.netlify.app`

---

### STEP 6: Set Up Custom Domain

#### Option A: Subdomain (nexus.deedavis.biz) - RECOMMENDED

1. In Netlify dashboard, go to your new NEXUS site
2. Click **"Domain settings"**
3. Click **"Add custom domain"**
4. Enter: `nexus.deedavis.biz` (or `app.deedavis.biz`)
5. Netlify will prompt you to add a DNS record

**Add DNS Record:**
- **Type:** CNAME
- **Name:** nexus (or app)
- **Value:** [your-site-name].netlify.app
- **TTL:** 3600

**Where to add DNS:**
- If DNS is managed by Netlify: Add in Netlify DNS dashboard
- If DNS is with another provider (GoDaddy, Namecheap, etc.): Add there

6. Wait 5-30 minutes for DNS to propagate
7. Netlify automatically provisions SSL certificate
8. Done! Your site will be at `https://nexus.deedavis.biz`

#### Option B: Separate Site (nexus-command.netlify.app)

1. In Netlify dashboard, go to **"Domain settings"**
2. Click **"Change site name"**
3. Choose: `nexus-command` or `deedavis-nexus`
4. Your site will be at: `https://nexus-command.netlify.app`
5. No DNS changes needed!

---

### STEP 7: Update Backend CORS

After deployment, update your backend to only accept requests from your domain.

Edit `api_server.py` (around line 65):

**For custom domain:**
```python
CORS(app, origins=[
    "https://nexus.deedavis.biz",  # Your custom domain
    "https://deedavis.biz",        # Main site (if needed)
])
```

**Or for Netlify subdomain:**
```python
CORS(app, origins=[
    "https://nexus-command.netlify.app",
])
```

**Or allow both during transition:**
```python
CORS(app, origins=[
    "https://nexus.deedavis.biz",
    "https://nexus-command.netlify.app",  # temporary URL
])
```

Then commit and push:
```bash
git add api_server.py
git commit -m "Configure CORS for production domain"
git push
```

**Then update PythonAnywhere:**
```bash
# In PythonAnywhere Bash console:
cd ~/nexus-backend
git pull origin main
# Click "Reload" button in Web tab
```

---

## 🎨 BRANDING OPTIONS

### Custom Subdomain Ideas
- `nexus.deedavis.biz` - Clean and clear
- `app.deedavis.biz` - Generic app subdomain
- `command.deedavis.biz` - NEXUS Command Center
- `portal.deedavis.biz` - Business portal
- `system.deedavis.biz` - System platform

### Favicon & Branding
Update your branding in `nexus-frontend/public/`:
- Replace `favicon.ico` with your logo
- Update `manifest.json` with your company name
- Add your logo files to `public/` folder

---

## 📊 DNS SETUP GUIDE

### If DNS is with Netlify

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click on **"Domains"** → **"deedavis.biz"**
3. Scroll to **"DNS settings"**
4. Click **"Add new record"**
5. Add CNAME record:
   ```
   Type: CNAME
   Name: nexus
   Value: [your-nexus-site].netlify.app
   ```
6. Save and wait for propagation

### If DNS is with Another Provider

**GoDaddy:**
1. Go to DNS Management
2. Add Record → CNAME
3. Name: `nexus`, Points to: `[your-site].netlify.app`

**Namecheap:**
1. Advanced DNS
2. Add New Record → CNAME
3. Host: `nexus`, Value: `[your-site].netlify.app`

**Cloudflare:**
1. DNS Management
2. Add Record → CNAME
3. Name: `nexus`, Target: `[your-site].netlify.app`
4. Proxy status: Proxied (orange cloud)

---

## 🔐 SSL CERTIFICATE

**Good news:** Netlify automatically provides free SSL certificates!

- Custom domain: Certificate provisions automatically (takes 5-30 minutes)
- No configuration needed
- Auto-renews
- Supports HTTP/2 and TLS 1.3

---

## 🧪 TESTING YOUR DEPLOYMENT

### After Deployment

1. **Visit your URL:**
   - Custom: `https://nexus.deedavis.biz`
   - Or: `https://nexus-command.netlify.app`

2. **Open browser console (F12)**
   - Check for errors
   - Verify API calls are working

3. **Test all systems:**
   - [ ] GPSS - Load opportunities
   - [ ] ATLAS - Create a task
   - [ ] DDCSS - View prospects
   - [ ] VERTEX - Check dashboard
   - [ ] GBIS - View grants
   - [ ] LBPC - View leads
   - [ ] ProposalBio - View checklists

4. **Test AI Copilot:**
   - Click floating AI button
   - Ask a question
   - Should get response from Claude

5. **Check mobile:**
   - Open on phone
   - Test touch interactions
   - Verify responsive design

---

## 🚨 TROUBLESHOOTING

### DNS Not Resolving
**Symptoms:** Site not accessible at custom domain
**Solutions:**
- Wait longer (DNS can take up to 48 hours, usually 30 minutes)
- Check DNS record is correct: `dig nexus.deedavis.biz`
- Verify CNAME points to correct Netlify URL
- Check DNS provider's status page

### SSL Certificate Pending
**Symptoms:** "Not secure" warning in browser
**Solutions:**
- Wait 5-30 minutes for Netlify to provision certificate
- Check DNS is properly configured
- Verify domain ownership in Netlify
- Check Netlify's status: [netlifystatus.com](https://netlifystatus.com)

### API Calls Failing
**Symptoms:** Features don't work, console shows errors
**Solutions:**
1. Check backend is running: `curl https://yourusername.pythonanywhere.com/health`
2. Verify CORS includes your domain in `api_server.py`
3. Check backend environment variables in PythonAnywhere (`.env` file)
4. Check PythonAnywhere error logs in Web tab
5. Test backend directly: `curl https://yourusername.pythonanywhere.com/gpss/opportunities`

### Build Failing
**Symptoms:** Netlify deploy fails
**Solutions:**
1. Check build logs in Netlify dashboard
2. Test locally: `cd nexus-frontend && npm run build`
3. Verify Node version (should be 18)
4. Check all dependencies are in `package.json`

---

## 💰 COSTS

### Your Setup
- **Netlify:** Already have account ✅
  - Free tier includes: 100GB bandwidth, 300 build minutes/month
  - Custom domain: Free on any plan
  - SSL: Free
- **PythonAnywhere Backend:** $0-5/month
  - Free: Basic hosting, no custom domain
  - Hacker ($5): Custom domains, more resources, always on
- **Custom Domain:** Already have ✅

**Total new cost:** $0-5/month (just for backend)

---

## 🔄 CONTINUOUS DEPLOYMENT

Once set up, updates are automatic:

```bash
# Make changes to your code
# Edit any files...

# Commit and push
git add .
git commit -m "Update feature"
git push

# Netlify automatically:
# 1. Detects push
# 2. Builds frontend
# 3. Deploys to nexus.deedavis.biz
# 4. Takes 2-3 minutes
```

---

## 📱 SHARE YOUR URL

After deployment, share with your team:

```
🚀 NEXUS Command Center
https://nexus.deedavis.biz

Access all systems:
• GPSS - Government Sales
• ATLAS - Project Management
• DDCSS - Consulting Sales
• VERTEX - Financial System
• GBIS - Grant Intelligence
• LBPC - Lead Pipeline
• ProposalBio - Quality Assurance
```

---

## 🎯 POST-DEPLOYMENT CHECKLIST

- [ ] Backend deployed to Render
- [ ] Backend URL updated in `netlify.toml`
- [ ] Changes committed and pushed to GitHub
- [ ] Site deployed to Netlify
- [ ] Custom domain configured (nexus.deedavis.biz)
- [ ] DNS record added
- [ ] SSL certificate provisioned
- [ ] CORS updated in backend
- [ ] All systems tested
- [ ] Mobile responsive verified
- [ ] Team notified of new URL
- [ ] Bookmark added to browser
- [ ] URL added to company documentation

---

## 🎉 NEXT STEPS

1. **Deploy backend** (if not done)
2. **Update netlify.toml** with backend URL
3. **Run preflight check:** `./preflight_check.sh`
4. **Commit and push** to GitHub
5. **Deploy to Netlify** from your account dashboard
6. **Add custom domain:** `nexus.deedavis.biz`
7. **Test everything**
8. **Update CORS** in backend
9. **Share with team!**

---

## 🆘 NEED HELP?

### Quick Commands
```bash
# Run preflight check
./preflight_check.sh

# Test backend
curl https://your-backend-url.onrender.com/health

# Test local build
cd nexus-frontend && npm run build

# Check DNS
dig nexus.deedavis.biz

# Check git status
git status
```

### Documentation
- **Quick deploy:** `NETLIFY_QUICK_DEPLOY.md`
- **Complete guide:** `NETLIFY_DEPLOYMENT_READY.md`
- **Environment vars:** `PRODUCTION_ENV_VARS.md`
- **Troubleshooting:** `TROUBLESHOOTING_GUIDE.md`

---

## 🌟 PROFESSIONAL SETUP COMPLETE

Your NEXUS Command Center will be accessible at:

**`https://nexus.deedavis.biz`** 🚀

Professional, secure, and ready for business!

**Start deployment now:** Run `./preflight_check.sh` to verify everything is ready.
