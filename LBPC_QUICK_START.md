# LBPC SYSTEM - QUICK START GUIDE 🚀

## **✅ DEPENDENCIES INSTALLED - SYSTEM READY!**

---

## **🎯 WHAT'S READY TO TEST:**

### ✅ Backend Code
- All Python files compile without errors
- Lead mining system complete
- 17 API endpoints ready

### ✅ Frontend Code  
- TypeScript compiles successfully
- All 6 tabs built
- Mining tab with 3 methods ready

### ✅ Test Data
- `test_leads.csv` created with 10 sample leads
- Ready to test CSV import

---

## **🚀 OPTION 1: TEST WITHOUT AIRTABLE (Quick Demo)**

### **Just Want to See the UI?**

**1. Start Backend** (Terminal 1):
```bash
cd "NEXUS BACKEND"
python3 api_server.py
```

**2. Start Frontend** (Terminal 2):
```bash
cd "NEXUS BACKEND/nexus-frontend"
npm start
```

**3. Open Browser:**
- Go to: http://localhost:3000
- Click "LBPC" system card
- Explore all 6 tabs
- See the Mining tab with 3 methods

**Note:** Without Airtable configured, data won't save, but you'll see the UI!

---

## **🗄️ OPTION 2: FULL SETUP WITH AIRTABLE (Recommended)**

### **Step 1: Create Airtable Base** (30 minutes)

**Follow:** `LBPC_AIRTABLE_SCHEMA.md`

**Quick Steps:**
1. Go to airtable.com
2. Create new base: "LBPC System"
3. Create 4 tables:
   - LBPC Leads (30 fields)
   - LBPC Documents (11 fields)
   - LBPC Tasks (12 fields)
   - LBPC Templates (10 fields)
4. Pre-populate 7 templates (copy from doc)

**Time:** ~30 minutes first time

---

### **Step 2: Configure .env File**

**Create/Update:** `.env` file in `/Users/deedavis/NEXUS BACKEND/`

```env
# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_base_id_here

# Anthropic AI (for document enhancement)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Flask Settings
FLASK_ENV=development
```

**Get Keys:**
- Airtable: airtable.com/account → Generate API key
- Anthropic: console.anthropic.com → API keys
- Base ID: In Airtable URL after airtable.com/

---

### **Step 3: Start Backend** (Terminal 1)

```bash
cd "NEXUS BACKEND"
python3 api_server.py
```

**Should See:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### **Step 4: Start Frontend** (Terminal 2)

```bash
cd "NEXUS BACKEND/nexus-frontend"
npm start
```

**Should Open:** http://localhost:3000 automatically

---

### **Step 5: Test Lead Mining** 🔍

**Method 1: Quick CSV Import**

1. Go to LBPC system
2. Click "Mining" tab
3. Under "Method 1: Quick CSV Import"
4. Click "Choose File"
5. Select: `/Users/deedavis/NEXUS BACKEND/test_leads.csv`
6. Should see: "Imported 10 leads, skipped 0 duplicates"
7. Go to "Leads" tab - see your 10 test leads!

**Method 2: Try It Again (Duplicate Detection)**

1. Upload same CSV again
2. Should see: "Imported 0 leads, skipped 10 duplicates"
3. Proves duplicate detection works!

---

### **Step 6: Test Document Generation** 📄

1. Go to "Leads" tab
2. Find "John Smith" lead
3. Click "🚀 Initial Notice → RL"
4. **Should see:**
   - Document generates
   - Beautiful instruction modal appears
   - Rocket Lawyer opens in new tab
   - Document copied to clipboard

5. Close modal
6. Go to "Documents" tab
7. See generated document listed
8. Click "Preview" to view full document

---

### **Step 7: Test Priority Scoring** ⭐

**Check Lead Cards:**
- John Smith: $15,000 → Score: 65-75
- Maria Garcia: $25,000 + email + phone → Score: 80-90
- Michael Brown: $45,000 + email + phone → Score: 95-100

**System Auto-Calculates:**
- Surplus amount (0-40 pts)
- Contact info (0-30 pts)
- Home state (0-10 pts)
- Case number (0-10 pts)

---

### **Step 8: Test Status Tracking** 📊

1. Find any lead
2. Click status dropdown
3. Change to "Contacted"
4. Go to "Dashboard" tab
5. See statistics update
6. Go to "Analytics" tab
7. See "Leads by Status" chart update

---

## **🎯 WHAT TO TEST NEXT:**

### **Advanced Features:**

**1. County PDF/CSV Upload**
- Find real county surplus list online
- Download PDF
- Go to Mining → Method 2
- Select county & state
- Upload PDF
- Watch it parse automatically

**2. Automated Web Scraping**
- Go to Mining → Method 3
- Click "🔍 Wayne, MI"
- Wait 30-60 seconds
- See leads imported

**3. Workflow Automation**
- Create new lead manually
- Watch system auto-generate tasks
- Go to "Tasks" tab
- See follow-up tasks created

**4. AI Document Enhancement**
- Generate document with use_ai=true
- Compare to non-AI version
- See personalization

---

## **📋 COMMON ISSUES & SOLUTIONS:**

### **"Connection refused on port 5000"**
**Solution:** Backend not running. Start it:
```bash
cd "NEXUS BACKEND"
python3 api_server.py
```

### **"Cannot find module" errors in frontend**
**Solution:** Install dependencies:
```bash
cd nexus-frontend
npm install
```

### **"Airtable error: Invalid API key"**
**Solution:** 
1. Check `.env` file has correct key
2. Restart backend server
3. Key format: `keyXXXXXXXXXXXXXX`

### **"No leads showing up after import"**
**Solution:**
1. Check backend terminal for errors
2. Verify Airtable base ID is correct
3. Check CSV has required columns
4. Try manual lead creation first

### **"Document generation fails"**
**Solution:**
1. Check if templates pre-populated in Airtable
2. Verify lead has all required fields
3. Check backend logs for errors

---

## **💡 PRO TIPS:**

### **Development Workflow:**

**Keep 3 Terminals Open:**
1. Backend: `python3 api_server.py`
2. Frontend: `npm start`
3. Testing: For running commands

**Quick Restart:**
- Backend: Ctrl+C, then up arrow, Enter
- Frontend: Ctrl+C, then `npm start`

### **Testing Tips:**

**Create Test Leads with Different Scenarios:**
- High value ($50K+) with contact info
- Low value ($5K) without contact
- Different states (MI, GA, TX, CA)
- With/without case numbers

**Watch for:**
- Priority scores calculate correctly
- Duplicates detected on re-import
- Status changes trigger task creation
- Analytics update in real-time

### **Debugging:**

**Backend Issues:**
```bash
# Check if backend is running
curl http://localhost:5000/lbpc/leads

# Should return JSON (even if empty)
```

**Frontend Issues:**
```bash
# Check React dev server
# Browser should auto-open to localhost:3000
# Check browser console for errors (F12)
```

---

## **📊 EXPECTED RESULTS:**

### **After Full Setup:**

**Dashboard Should Show:**
- Total Leads: 10 (from test CSV)
- Total Surplus: $288,000
- Potential Fees: $86,400
- Tasks: Auto-generated for each lead
- Leads by State: MI (3), GA (2), TX (2), etc.

**Leads Tab Should Show:**
- 10 lead cards with full info
- Priority scores displayed
- 4 Rocket Lawyer buttons on each
- Status dropdown working
- Search/filter functional

**Documents Tab:**
- Empty initially
- Populates when you generate docs
- Preview and copy buttons work

**Tasks Tab:**
- Auto-generated tasks for new leads
- "Contact within 24 hours"
- "Send initial notice"
- "Follow up if no response"

**Mining Tab:**
- 3 methods visible
- File upload buttons active
- County scrapers ready

**Analytics Tab:**
- Lead distribution charts
- Key metrics calculated
- Revenue potential shown

---

## **🚀 READY TO LAUNCH!**

### **You Can Now:**

✅ Import leads from any CSV  
✅ Parse county PDFs automatically  
✅ Scrape county websites (3 ready)  
✅ Generate 7 document types  
✅ Send via Rocket Lawyer  
✅ Track complete workflows  
✅ View real-time analytics  
✅ Manage 100+ leads easily  

### **Next Actions:**

**Today:**
- [ ] Set up Airtable (30 min)
- [ ] Configure .env file (5 min)
- [ ] Start backend & frontend (2 min)
- [ ] Import test_leads.csv (1 min)
- [ ] Generate first document (2 min)

**This Week:**
- [ ] Find real county surplus list
- [ ] Upload and process it
- [ ] Review imported leads
- [ ] Generate actual documents
- [ ] Test Rocket Lawyer workflow (when you have account)

**This Month:**
- [ ] Process first real lead end-to-end
- [ ] Get attorney template review
- [ ] Build weekly mining schedule
- [ ] Scale to 20-50 leads/month

---

## **📞 NEED HELP?**

### **Documentation Available:**

**Setup & Configuration:**
- `LBPC_AIRTABLE_SCHEMA.md` - Database setup
- `LBPC_COMPLETE_BUILD_SUMMARY.md` - Full system overview

**Features:**
- `LBPC_ROCKET_LAWYER_INTEGRATION.md` - E-signature workflow
- `LBPC_LEAD_MINING_COMPLETE.md` - All mining methods

**Reference:**
- `LBPC_TEMPLATE_UPDATES_COMPLETE.md` - Document templates
- `LBPC_COMPLETE_SUMMARY.md` - System features

---

## **🎉 START TESTING NOW!**

**Simplest Path (5 minutes):**

```bash
# Terminal 1
cd "NEXUS BACKEND"
python3 api_server.py

# Terminal 2  
cd "NEXUS BACKEND/nexus-frontend"
npm start

# Browser opens automatically
# Click LBPC → Mining → Upload test_leads.csv
# Go to Leads tab → See your imported leads!
```

**That's it! You're mining leads!** 🔍💰

---

**Questions? Check the documentation files listed above!**

**Good luck building your surplus recovery business!** 🚀✨
