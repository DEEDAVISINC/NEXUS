# COMBINED SUB-SOURCING IMPLEMENTATION PLAN
**Immediate Results + Long-Term Automation**

**Created:** February 8, 2026  
**Strategy:** Start manual → Build database → Add automation → Launch vendor portal  
**Timeline:** 4-week sprint to fully operational system

---

## 🎯 THE COMBINED APPROACH

```
TODAY → Build foundation (manual database)
WEEK 1 → Add Google/Yelp automation
WEEK 2 → Add automated outreach
WEEK 3 → Build NEXUS integration
WEEK 4 → Launch vendor portal (passive growth)

Result: Tactical wins NOW + Strategic system LATER
```

---

## 📅 TODAY (SUNDAY, FEB 8) - FOUNDATION SPRINT
**Time: 2 hours | Result: 50+ vendors in database**

### **Step 1: Create Airtable Tables** (15 minutes)

**TABLE 1: SUBCONTRACTORS**

Go to your Airtable base and create a new table called **SUBCONTRACTORS** with these fields:

```
BASIC INFO:
1. Company Name (Single line text) - PRIMARY FIELD
2. Contact Name (Single line text)
3. Email (Email)
4. Phone (Phone number)
5. Website (URL)

SERVICE & LOCATION:
6. Service Types (Multiple select)
   Options: Landscaping, HVAC, Plumbing, Electrical, Janitorial, 
            Pressure Washing, Security, IT Services, Construction, 
            Snow Removal, Painting, Roofing, Concrete, Fencing, 
            Pest Control, Other

7. Service Area (Multiple select)
   Options: Wayne County, Oakland County, Macomb County, 
            Metro Detroit, All Michigan, Illinois, Ohio, 
            Indiana, Wisconsin, National

QUALITY INDICATORS:
8. Google Rating (Number - 0.0 to 5.0)
9. Yelp Rating (Number - 0.0 to 5.0)
10. Total Reviews (Number)
11. Years in Business (Number)

CERTIFICATIONS & INSURANCE:
12. Liability Insurance (Single select)
    Options: $1M+, $500K-$1M, Under $500K, Unknown
13. Workers Comp (Checkbox)
14. License Number (Single line text)
15. Business Certifications (Multiple select)
    Options: Woman-Owned, Minority-Owned, Veteran-Owned, 
             Small Business, SAM.gov Registered

EXPERIENCE:
16. Government Experience (Checkbox)
17. Commercial Experience (Checkbox)
18. Residential Only (Checkbox)

TRACKING:
19. Source (Single select)
    Options: Vendor Portal, Google Search, Yelp, Referral, 
             Past Bid, Manual Entry, LinkedIn, Industry Directory
20. Status (Single select)
    Options: Active, Inactive, Do Not Use, Preferred
    Colors: Green, Gray, Red, Blue

PERFORMANCE (Fill after working with them):
21. Times Used (Number - default: 0)
22. Performance Rating (Rating - 1 to 5 stars)
23. Would Use Again (Checkbox)
24. Response Time Avg (Number - in hours)
25. Pricing Tier (Single select)
    Options: Very Competitive, Competitive, Average, High, Unknown

DATES:
26. First Contact Date (Date)
27. Last Contact Date (Date)
28. Created Date (Created time - auto)

NOTES:
29. Notes (Long text)
30. Tags (Multiple select)
    Options: Responsive, Reliable, Affordable, Quality Work, 
             Slow Response, Expensive, Difficult, Preferred, 
             Do Not Use Again
```

**TABLE 2: SUB_OUTREACH_TRACKING**

Create second table called **SUB_OUTREACH_TRACKING**:

```
LINKS:
1. Outreach ID (Autonumber) - PRIMARY FIELD
2. Opportunity (Link to Opportunities table)
3. Subcontractor (Link to SUBCONTRACTORS table)

OUTREACH:
4. Outreach Date (Date with time)
5. Outreach Method (Single select)
   Options: Email, Phone, Portal, Text, In-Person
6. Email Sent (Checkbox)
7. Email Opened (Checkbox)
8. Email Clicked (Checkbox)

RESPONSE:
9. Response Status (Single select)
   Options: Pending, Interested, Declined, No Response, Unavailable
   Colors: Yellow, Green, Red, Gray, Orange
10. Response Date (Date with time)
11. Response Time Hours (Formula)
    Formula: DATETIME_DIFF({Response Date}, {Outreach Date}, 'hours')
12. Quote Amount (Currency)
13. Quote Details (Long text)
14. Available (Checkbox)
15. Availability Notes (Long text)

FOLLOW-UP:
16. Follow-Up Needed (Checkbox)
17. Follow-Up Date (Date)
18. Follow-Up Sent (Checkbox)

SELECTION:
19. Selected (Checkbox)
20. Decline Reason (Long text)
21. LOI Sent (Checkbox)
22. LOI Received (Checkbox)
23. Insurance Cert Received (Checkbox)

NOTES:
24. Notes (Long text)
25. Created Date (Created time - auto)
```

---

### **Step 2: Seed Database with Known Vendors** (20 minutes)

**Add vendors you already know or have worked with:**

```
MOPEC (Oakland County Body Bags contact):
- Company: MOPEC
- Contact: Joseph Schembari
- Email: jschembari@mopec.com
- Phone: +1 (947) 282-4168
- Service: Medical Supplies
- Area: Michigan
- Source: Past Bid
- Status: Active
- Tags: Responsive, Used Before

[Add 5-10 more if you have them]
```

**Don't have many? That's fine - move to Step 3.**

---

### **Step 3: RAPID DATABASE BUILD** (90 minutes)

**Use this systematic approach to add 50 vendors quickly:**

#### **3A: Top 5 Service Categories** (15 min each = 75 min)

For each category, spend 15 minutes:

**CATEGORY 1: PRESSURE WASHING (Oakland County)**

1. Google search: "pressure washing Oakland County MI"
2. Open top 10 results
3. For each company, add to Airtable:
   - Company name
   - Phone (from website)
   - Email (contact form or info@)
   - Google rating (if shown)
   - Service Type: Pressure Washing
   - Service Area: Oakland County
   - Source: Google Search
   - Status: Active

**Target: 10 vendors in 15 minutes**

**CATEGORY 2: LANDSCAPING (Oakland County)**

1. Yelp search: "landscaping Oakland County MI"
2. Open top 10 results
3. Add to Airtable (same process)

**Target: 10 vendors in 15 minutes**

**CATEGORY 3: HVAC (Metro Detroit)**

1. Google: "HVAC Metro Detroit commercial"
2. Add top 10

**Target: 10 vendors in 15 minutes**

**CATEGORY 4: JANITORIAL (Michigan)**

1. Google: "commercial cleaning Michigan government"
2. Add top 10

**Target: 10 vendors in 15 minutes**

**CATEGORY 5: SALT/DEICING (Michigan)** ← FOR OAKLAND COUNTY SALT BID!

1. Google: "treated salt Michigan road maintenance"
2. Add companies like:
   - Detroit Salt Company
   - Morton Salt
   - Cargill
   - Compass Minerals
   - Michigan Salt
   - etc.

**Target: 10 vendors in 15 minutes**

---

#### **3B: Quick Import from SAM.gov** (15 minutes)

**Find past contract winners (they're qualified!):**

1. Go to SAM.gov
2. Search: "Pressure washing" + State: Michigan
3. Click on awarded contracts
4. See who won
5. Add those companies to your database

**Why this works:**
- They're already SAM.gov registered
- They've won government contracts
- They're qualified and vetted
- Ready to work with primes

**Target: 5-10 more vendors**

---

### **Step 4: Test the System** (10 minutes)

**Tomorrow morning, you'll use this database:**

1. Open Oakland County Salt opportunity
2. Filter SUBCONTRACTORS table:
   - Service Type = "Salt" or "Deicing" or "Materials"
   - Status = "Active"
3. You should see 5-10 salt suppliers
4. Call/email them for quotes

**You now have a working database!**

---

## 🚀 WEEK 1 (FEB 9-15) - AUTOMATION PHASE 1
**Add Google/Yelp API automation**

### **Monday-Tuesday: Get API Keys** (30 min)

**Google Maps Places API:**
1. Go to: https://console.cloud.google.com/
2. Create project: "DEE DAVIS SUB SOURCING"
3. Enable: Places API
4. Create API key
5. Cost: $0-$200/month (within free tier for your volume)

**Yelp Fusion API:**
1. Go to: https://www.yelp.com/developers
2. Create app: "DEE DAVIS SUB SEARCH"
3. Get API key
4. Cost: FREE (500 requests/day)

---

### **Wednesday-Friday: Build Search Script** (4 hours)

**File: `automated_sub_search.py`**

I'll help you build this - it will:
- Search Google Maps for contractors
- Search Yelp for contractors
- Filter by rating (≥4.0 stars)
- Filter by reviews (≥10)
- Auto-save to Airtable
- Deduplicate

**Result:** Click one button → Find 10-30 subs in 30 seconds

---

## 🔄 WEEK 2 (FEB 16-22) - AUTOMATION PHASE 2
**Add automated outreach**

### **Monday-Wednesday: Email Automation** (4 hours)

**Set up SendGrid:**
1. Free tier: 100 emails/day
2. Connect to Python script
3. Create email templates
4. Test sending

**Build email system:**
- Personalized emails to each sub
- Auto-tracking in Airtable
- Auto follow-ups after 3 days

**Result:** Send 10 RFQs instantly, track automatically

---

### **Thursday-Friday: Build Tracking Dashboard** (4 hours)

**Simple tracking interface:**
- Who responded
- What they quoted
- Response times
- Quote comparison

---

## 🖥️ WEEK 3 (FEB 23-MAR 1) - NEXUS INTEGRATION
**Build the UI in NEXUS**

### **Add "Find Subs" Button**

In NEXUS frontend, add new feature:

```typescript
// In Opportunity detail page

<Button onClick={findSubcontractors}>
  🔍 Find Subcontractors
</Button>

// This triggers:
1. Search Airtable database
2. Search Google Maps API (if needed)
3. Search Yelp API (if needed)
4. Display results
5. User selects vendors
6. Click "Send RFQs"
7. Automated emails sent
```

**Result:** Complete workflow in NEXUS interface

---

## 🌐 WEEK 4 (MAR 2-8) - VENDOR PORTAL
**Launch public vendor registration**

### **Build deedavis.biz/vendors**

**Simple landing page:**

```
╔════════════════════════════════════════════════════════╗
║               DEE DAVIS INC                            ║
║        VENDOR PARTNERSHIP OPPORTUNITIES                ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  🤝 REGISTER AS A SUBCONTRACTOR                       ║
║                                                        ║
║  Work with a certified EDWOSB prime contractor on     ║
║  government and commercial contracts in Michigan.     ║
║                                                        ║
║  [Register Now] [View Open RFQs]                      ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

**Registration Form:**
- Company info
- Services offered
- Coverage areas
- Insurance/certifications
- Saves directly to Airtable

**RFQ Board:**
- Public page showing open opportunities
- Vendors can download RFQ PDFs
- Submit quotes online

**Result:** Vendors register themselves, database grows passively

---

## 🔄 THE COMPLETE WORKFLOW (After 4 Weeks)

```
USER FINDS OPPORTUNITY
↓
Clicks "Find Subs" in NEXUS
↓
SYSTEM SEARCHES (3-layer fail-safe):
  Layer 1: Airtable database (5 sec)
  Layer 2: Google Maps + Yelp APIs (30 sec)
  Layer 3: Manual fallback (if needed)
↓
DISPLAYS RESULTS:
  • 5-20 from database (used before)
  • 10-30 from APIs (new)
  • Combined: 15-50 qualified vendors
↓
USER SELECTS 10 VENDORS
↓
Clicks "Send RFQs"
↓
SYSTEM AUTO-SENDS:
  • 10 personalized emails
  • Creates tracking records
  • Schedules follow-ups
↓
VENDORS RESPOND
↓
SYSTEM TRACKS:
  • Response times
  • Quote amounts
  • Availability
↓
USER COMPARES QUOTES
↓
Selects winner
↓
SYSTEM GENERATES:
  • Letter of Intent
  • Subcontract agreement
↓
USER BUILDS PROPOSAL:
  • Uses sub's ratings as proof
  • Uses response times as metrics
  • Uses performance data as case study
↓
SUBMITS BID
↓
AFTER PROJECT:
  System tracks performance
  Updates database
  Builds metrics library
```

---

## 📊 METRICS TO TRACK

**Week 1 (Manual):**
- Vendors in database: Target 50+
- Time to find subs: 15-30 minutes
- Response rate: 20-30%

**Week 2 (API Automation):**
- Time to find subs: 2-3 minutes
- Vendors found per search: 10-30
- Database growth rate: 50+ per week

**Week 3 (Outreach Automation):**
- Time to send 10 RFQs: <1 minute
- Email open rate: 40-60%
- Response rate: 30-40%

**Week 4 (Vendor Portal):**
- Vendor registrations: 5-10 per week
- Passive database growth: 20-40 per month
- RFQ board views: Track traffic

**Month 2-3:**
- Database size: 200+ vendors
- Coverage: 10+ service categories
- Response times: <24 hours average
- Quote quality: 80%+ usable

---

## 💰 COST BREAKDOWN

**API Costs:**
- Google Maps API: $0-$200/month (within free tier initially)
- Yelp API: FREE (500 requests/day)
- SendGrid Email: FREE tier (100 emails/day)

**Total: $0-$200/month**

**ROI:**
- Time saved: 4-5 hours per service bid
- More bids: 2-3x increase (have subs ready)
- Win rate increase: 15-25% (better quotes, faster response)
- **Value: $50K-$200K additional revenue per year**

---

## ✅ SUCCESS MILESTONES

**TODAY (Feb 8):**
- [x] Airtable tables created
- [x] 50+ vendors in database
- [x] Ready for Oakland County salt bid

**Week 1 (Feb 15):**
- [ ] Google/Yelp APIs working
- [ ] Can find 10-30 subs in 30 seconds
- [ ] Database at 100+ vendors

**Week 2 (Feb 22):**
- [ ] Automated email outreach working
- [ ] Can send 10 RFQs in <1 minute
- [ ] Response tracking automated

**Week 3 (Mar 1):**
- [ ] NEXUS integration complete
- [ ] "Find Subs" button working
- [ ] Full workflow operational

**Week 4 (Mar 8):**
- [ ] Vendor portal live
- [ ] First vendor registrations
- [ ] RFQ board operational

**Month 2 (Apr 1):**
- [ ] 200+ vendors in database
- [ ] Using system for all service bids
- [ ] 30-40% response rate achieved

---

## 🎯 IMMEDIATE ACTIONS (RIGHT NOW)

**Your next 2 hours:**

1. **Create Airtable Tables** (15 min)
   - SUBCONTRACTORS table
   - SUB_OUTREACH_TRACKING table
   - Use schema above

2. **Add Known Vendors** (15 min)
   - MOPEC (medical supplies)
   - Any pressure washing companies you know
   - Any landscaping companies
   - Any salt suppliers

3. **Rapid Database Build** (90 min)
   - 5 service categories × 10 vendors = 50 vendors
   - Google/Yelp search method
   - Focus on: Salt, Landscaping, Pressure Washing, HVAC, Janitorial

**Tomorrow morning:**
- Use database to find salt suppliers
- Email 5-10 for Oakland County salt bid
- Test the system in real time

**This week:**
- Continue building database (1 hour/day)
- Get API keys
- Start automation build

---

## 🚀 THE VISION (4 Weeks from Now)

**When you find a service opportunity:**

1. Click "Find Subs"
2. System searches database + APIs
3. 15-50 qualified vendors appear
4. Select 10 vendors
5. Click "Send RFQs"
6. 10 personalized emails sent automatically
7. Track responses in real-time
8. Compare quotes
9. Select winner
10. Auto-generate LOI
11. Build proposal with transformation proof
12. Submit bid

**Total time: 20 minutes (vs. 4-6 hours manually)**

**You'll have:**
- ✅ 200+ pre-qualified vendors
- ✅ Automated search (30 seconds)
- ✅ Automated outreach (instant)
- ✅ Real-time tracking
- ✅ Vendor portal (passive growth)
- ✅ Never scramble for subs again

---

## 💡 KEY INSIGHT

**The database is the foundation. Everything else builds on it.**

- Manual today → Automated tomorrow
- 50 vendors this weekend → 200 vendors in 4 weeks
- Tactical wins now → Strategic system later

**Start manually, automate incrementally, scale exponentially.**

---

**Ready to create those Airtable tables and start building your database?** 

I can walk you through each field or you can copy the schema above and start adding vendors!

---

*Created: February 8, 2026*  
*Timeline: 4-week sprint to fully operational*  
*Strategy: Manual → Automated → Scaled*
