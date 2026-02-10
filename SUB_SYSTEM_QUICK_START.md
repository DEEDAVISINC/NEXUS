# 🚀 SUBCONTRACTOR SYSTEM - QUICK START

**Built:** February 8, 2026  
**Status:** 90% Complete - UI + API Ready  
**Time to operational:** 35 minutes

---

## ✅ WHAT'S READY

**YOU CAN USE TODAY (No API keys needed):**
- ✅ View all 18 existing subcontractors in NEXUS UI
- ✅ Add new subcontractors manually
- ✅ Edit subcontractor details
- ✅ Search/filter by service, location, status
- ✅ Track insurance, compliance, ratings

**READY AFTER API KEYS (30 minutes):**
- ✅ Auto-find subcontractors via Google Maps + Yelp
- ✅ Get 10-20 qualified subs in seconds
- ✅ See ratings, reviews, distance
- ✅ One-click add to database

---

## 🎯 HOW TO START (Choose Path)

### **PATH A: Use Manual Entry Right Now** (5 min)

```bash
# Terminal 1:
cd nexus-frontend && npm start

# Terminal 2:
python3 api_server.py

# Then:
# 1. Open browser: http://localhost:3000
# 2. Click "GPSS" system
# 3. Click "👷 Subcontractors" tab
# 4. Click "➕ Add Manually"
# 5. Enter sub details and save
```

**Use for:** Adding subs you already know about

---

### **PATH B: Enable Automated Search** (35 min)

**Step 1: Get API Keys (30 min)**

**Google Maps Places API:**
1. Go to: https://console.cloud.google.com/
2. Create project: "Dee Davis Nexus"
3. Enable "Places API"
4. Create API key
5. Restrict to "Places API"

**Yelp Fusion API:**
1. Go to: https://www.yelp.com/developers/v3/manage_app
2. Create app: "Dee Davis Nexus Sub Sourcing"
3. Copy API key

**Step 2: Add to .env (2 min)**
```bash
# Add these lines to .env:
GOOGLE_MAPS_API_KEY=AIzaSyC_your_key_here
YELP_API_KEY=your_yelp_key_here
```

**Step 3: Test (3 min)**
```bash
python3 automated_sub_sourcing.py find \
  --service "lawn care" \
  --location "Oakland County, MI" \
  --limit 10
```

**Use for:** Finding qualified subs for any service opportunity

---

## 🎬 DEMO WORKFLOW

### **Scenario: Need lawn care subs for Madison Heights bid**

**Old way (Manual - 2 hours):**
1. Google search "lawn care Oakland County"
2. Open 20 websites
3. Copy contact info to spreadsheet
4. Look up reviews on Google
5. Call each one individually

**New way (Automated - 5 minutes):**
1. Open NEXUS → GPSS → 👷 Subcontractors
2. Click "🔍 Find Subcontractors"
3. Enter: "lawn care" + "Oakland County, MI"
4. Click "🔍 Search Now"
5. Get 20 qualified subs with ratings instantly
6. Click "➕ Add" on top 5
7. Done - they're in your database

**Result:**
- 5 qualified subs added in 5 minutes
- All have ratings, reviews, phone numbers
- Ready to call for quotes

---

## 📋 TESTING CHECKLIST

**Test 1: View Database** ✅
```
[ ] Start NEXUS
[ ] Go to GPSS → 👷 Subcontractors
[ ] See existing 18 subcontractors
[ ] Filter by "Active" status
[ ] Search for "lawn" - see lawn care companies
```

**Test 2: Add Manually** ✅
```
[ ] Click "➕ Add Manually"
[ ] Enter: "Test Sub LLC", "pressure washing", "(248) 555-1234"
[ ] Click "Add Subcontractor"
[ ] See success notification
[ ] Find in table
```

**Test 3: Automated Search** (After API keys)
```
[ ] Click "🔍 Find Subcontractors"
[ ] Enter: "pressure washing" + "Oakland County, MI"
[ ] Click "🔍 Search Now"
[ ] See 10-20 results with ratings
[ ] Click "➕ Add" on one
[ ] See in table
```

---

## 🔥 FOR EDWOSB SERVICE OPPORTUNITIES

**Why this matters:**
- EDWOSB eligibility requires service contracts
- You can't self-perform all services
- Need qualified subcontractors FAST

**The new workflow:**
```
1. Find EDWOSB service opportunity on SAM.gov
   Example: "Janitorial Services - VA Hospital"

2. Click "Find Subcontractors" in NEXUS
   Search: "janitorial services" + "Virginia Beach, VA"
   Get: 15 qualified janitorial companies instantly

3. Click "Add" on top 5 (highest rated)
   They're now in your database

4. Call them for quotes
   "Hi, we're bidding on VA Hospital janitorial contract.
    Need quote for [scope]. Can you provide?"

5. Get 3-5 quotes back
   Use best pricing in your bid

6. Submit bid with sub quotes
   Include subs as teaming partners

7. WIN CONTRACT 🎉
   Execute with qualified sub
```

**Before this system:** 2-3 days to find and vet subs  
**After this system:** 30 minutes to find and vet subs  
**Impact:** Can apply to 10x more service opportunities

---

## 💡 PRO TIPS

**TIP 1: Build Database BEFORE You Need It**
Don't wait for opportunities. Search now:
- Lawn care (Oakland, Wayne, Macomb counties)
- Janitorial (all Michigan)
- Pressure washing (SE Michigan)
- HVAC (Tri-county)
- IT support (Michigan)

**TIP 2: Vet Compliance Early**
When you add a sub, immediately:
- Request W-9
- Request insurance certificate
- Request licenses/certs
- Mark "Compliance Ready" in NEXUS
- When opportunity comes, you're READY

**TIP 3: Track Performance**
After each project, update NEXUS:
- Rating (1-5 stars)
- Response time (fast/slow)
- Quality (excellent/good/poor)
- Reliability (on-time/late)

Build your A-list of top performers

---

## 🚨 TROUBLESHOOTING

**"No subcontractors found"**
→ Database empty. Add manually first.

**"Search failed - check API keys"**
→ API keys not in .env or incorrect.

**"Failed to load subcontractors"**
→ API server not running. Start: `python3 api_server.py`

**"Connection refused"**
→ Frontend not running. Start: `cd nexus-frontend && npm start`

**Search returns 0 results**
→ Try broader terms: "lawn care" not "residential lawn edging"

---

## 📂 KEY FILES

**Frontend:**
- `nexus-frontend/src/components/SubcontractorsTab.tsx` - The UI
- `nexus-frontend/src/api/client.ts` - API methods

**Backend:**
- `api_server.py` - API endpoints (lines 4111-4560)
- `automated_sub_sourcing.py` - Search automation
- `nexus_backend.py` - Core sub functions

**Guides:**
- `GET_API_KEYS_NOW.md` - API key setup
- `SUBCONTRACTOR_SYSTEM_BUILT_FEB_8.md` - Full documentation

---

## 🎯 YOUR ACTION PLAN

**TODAY (30 minutes):**
```
[ ] Read GET_API_KEYS_NOW.md
[ ] Get Google Maps API key
[ ] Get Yelp API key
[ ] Add to .env file
[ ] Test: python3 automated_sub_sourcing.py find --service "lawn care" --location "Oakland County, MI"
```

**TOMORROW (1 hour):**
```
[ ] Start NEXUS + API server
[ ] Test SubcontractorsTab UI
[ ] Add 5 subcontractors manually
[ ] Test automated search
[ ] Add 10 subs from search results
```

**THIS WEEK (3 hours):**
```
[ ] Build sub database (50+ subs across 5 service types)
[ ] Search SAM.gov for EDWOSB service opportunities
[ ] Find 2-3 good opportunities
[ ] Use "Find Subs" to get quotes
[ ] Submit first service bid
```

---

## ✅ SUCCESS = EDWOSB SERVICE CONTRACTS

**The goal:** Win service contracts to maintain EDWOSB eligibility

**The blocker:** Finding qualified subcontractors fast

**The solution:** This system (built today!)

**The result:** 
- Apply to 10x more service opportunities
- Get quotes in minutes not days
- Build database of vetted subs
- Win service contracts
- Maintain EDWOSB status
- Grow business

---

*Get the API keys, test the system, start applying to service opportunities! 🚀*

**Questions? Everything is documented in:**
- `SUBCONTRACTOR_SYSTEM_BUILT_FEB_8.md` (detailed guide)
- `GET_API_KEYS_NOW.md` (API setup)
- `SUPPLIER_SUB_SYSTEM_STATUS_FEB_8.md` (system status)
