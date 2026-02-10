# AIRTABLE - WHAT YOU ACTUALLY NEED TO CREATE
**Corrected based on what already exists**

---

## ✅ TABLES YOU ALREADY HAVE

### **1. Opportunities** ✅ (or GPSS OPPORTUNITIES)
Exists - where your bids/opportunities live

### **2. CapabilityStatements** ✅
Exists - where auto-generated capability statements are stored

### **3. OFFICER_OUTREACH_TRACKING** ✅
**EXISTS!** Already being used for:
- Federal Forecasts outreach
- EDWOSB sources sought responses
- Closed opportunity outreach
- Tracks officer responses

### **4. Federal Forecasts** ✅
**EXISTS!** Already mining real government forecasts

### **5. GPSS Proposals** ✅
Exists - where your proposals are stored

---

## ⭐ TABLES YOU NEED TO CREATE (Only 4!)

### **1. SUBCONTRACTORS** ⭐ CREATE THIS

**Purpose:** Master database of all subcontractors

**Why you need it:** Automated sub sourcing stores subs here

**Key fields:**
- CompanyName (primary)
- ContactName, Email, Phone
- ServiceTypes (multiple select: Landscaping, Pressure Washing, NEMT, Janitorial, etc.)
- GoogleRating, YelpRating, TotalReviews
- CoverageArea
- Status (New, Active, Inactive)
- Insurance info, licenses

**Time to create:** 7 minutes

---

### **2. SUB_OUTREACH_TRACKING** ⭐ CREATE THIS

**Purpose:** Track outreach to subs for each opportunity

**Why you need it:** Automated sub sourcing tracks responses here

**Key fields:**
- OpportunityID (link to Opportunities)
- SubcontractorID (link to SUBCONTRACTORS)
- OutreachDate
- ResponseStatus (Pending, Interested, Declined)
- QuoteAmount (currency)
- Available (checkbox)
- Selected (checkbox)

**Time to create:** 5 minutes

---

### **3. SUB_PERFORMANCE** ⭐ CREATE THIS

**Purpose:** Track actual performance on projects (builds transformation metrics!)

**Why you need it:** This becomes your transformation proof library

**Key fields:**
- OpportunityID (link)
- SubcontractorID (link)
- ProjectStartDate, ProjectEndDate
- NumberOfServices, CompletedServices, MissedServices
- CompletionRate (%)
- ClientSatisfaction (1-5 stars)
- OnTimePerformance (%)
- WouldUseAgain (checkbox)

**Time to create:** 5 minutes

---

### **4. GPSS ProposalBio Scores** ⭐ CREATE THIS

**Purpose:** Store ProposalBio quality scores (10 biohacks per proposal)

**Why you need it:** ProposalBio stores analysis here

**Key fields:**
- Proposal (link to Opportunities or GPSS Proposals)
- BiohackNumber (1-10)
- BiohackName (Mirror Neuron, Cognitive Ease, etc.)
- Score (0-10, 2 decimals)
- PassFail (Pass/Fail)
- AnalyzedDate

**Time to create:** 3 minutes

---

### **5. GPSS ProposalBio Learning** ⭐ CREATE THIS (Optional but recommended)

**Purpose:** Track proposal outcomes for continuous learning

**Why you need it:** Correlates scores with wins/losses

**Key fields:**
- Proposal (link)
- Outcome (Won, Lost, No Decision)
- WinValue (currency)
- CompositeScore (0-100)
- TransformationScore (0-50)
- RecordedDate

**Time to create:** 3 minutes

---

## 📊 SUMMARY

**YOU ALREADY HAVE:**
- ✅ Opportunities
- ✅ CapabilityStatements
- ✅ OFFICER_OUTREACH_TRACKING (being used for forecasts & sources sought!)
- ✅ Federal Forecasts
- ✅ GPSS Proposals

**YOU NEED TO CREATE:**
- ⭐ SUBCONTRACTORS (for automated sub sourcing)
- ⭐ SUB_OUTREACH_TRACKING (for sub quotes)
- ⭐ SUB_PERFORMANCE (for transformation metrics)
- ⭐ GPSS ProposalBio Scores (for proposal quality)
- ⭐ GPSS ProposalBio Learning (optional - for win/loss tracking)

**Total new tables needed: 4-5**
**Time to create: 20-25 minutes**

---

## ⏱️ PRIORITY ORDER

### **BEFORE YOUR FIRST SERVICE BID:**
1. Create SUBCONTRACTORS
2. Create SUB_OUTREACH_TRACKING
   → Enables automated sub sourcing

### **AFTER YOUR FIRST PROJECT:**
3. Create SUB_PERFORMANCE
   → Starts building transformation metrics library

### **BEFORE WRITING PROPOSALS:**
4. Create GPSS ProposalBio Scores
5. Create GPSS ProposalBio Learning (optional)
   → Enables proposal quality checking

---

## 🎯 WHAT EACH FRAMEWORK NEEDS

| Framework | Tables Needed | Status |
|-----------|---------------|--------|
| **Officer Outreach** | OFFICER_OUTREACH_TRACKING | ✅ Already have! |
| **Auto CapStat** | CapabilityStatements, OFFICER_OUTREACH_TRACKING | ✅ Already have! |
| **Grainger Script** | None (just negotiation) | ✅ Ready! |
| **Service Sub (Manual)** | SUBCONTRACTORS, SUB_OUTREACH_TRACKING, SUB_PERFORMANCE | ⭐ Need to create |
| **Automated Sub Sourcing** | SUBCONTRACTORS, SUB_OUTREACH_TRACKING | ⭐ Need to create |
| **Transformation Framework** | SUB_PERFORMANCE (for metrics) | ⭐ Need to create |
| **ProposalBio** | GPSS ProposalBio Scores, Learning | ⭐ Need to create |

---

## 💡 WHAT YOU'RE ALREADY DOING

### **Officer Outreach System:**
You're already tracking:
- Federal Forecasts officer outreach ✅
- EDWOSB sources sought responses ✅
- Closed opportunity outreach ✅
- Officer responses and follow-ups ✅

**This is working!** Don't recreate it.

### **Federal Forecasts:**
You're already mining:
- Real government forecasts ✅
- Officer contact info ✅
- Opportunity details ✅

**This is working!** Don't recreate it.

---

## 🚀 WHAT'S NEW (Sub Sourcing & ProposalBio)

### **NEW: Automated Sub Sourcing**
Requires 2 new tables:
- SUBCONTRACTORS
- SUB_OUTREACH_TRACKING

Then you can:
- Find 15 subs in 2 minutes (vs. 4 hours)
- Auto-generate outreach emails
- Track quotes automatically
- Compare pricing

### **NEW: Sub Performance Tracking**
Requires 1 new table:
- SUB_PERFORMANCE

Then you can:
- Track completion rates
- Build transformation metrics
- Prove outcomes with data
- Build case studies

### **NEW: ProposalBio Quality Scoring**
Requires 2 new tables:
- GPSS ProposalBio Scores
- GPSS ProposalBio Learning

Then you can:
- Score proposals before submitting
- Quality gate (75/100 minimum)
- Track which proposals win
- Continuous improvement

---

## ✅ CORRECTED SETUP CHECKLIST

**Check what you have:**
- [x] Opportunities table exists
- [x] CapabilityStatements table exists
- [x] OFFICER_OUTREACH_TRACKING table exists
- [x] Federal Forecasts table exists
- [x] GPSS Proposals table exists

**Create these for sub sourcing:**
- [ ] SUBCONTRACTORS table
- [ ] SUB_OUTREACH_TRACKING table
- [ ] SUB_PERFORMANCE table

**Create these for proposal quality:**
- [ ] GPSS ProposalBio Scores table
- [ ] GPSS ProposalBio Learning table (optional)

---

## 📖 FULL SCHEMAS

**For complete field details, see:**
- `AIRTABLE_COMPLETE_SCHEMA_FOR_FRAMEWORKS.md` (all fields)

**Quick reference:**
- `AIRTABLE_TABLES_NEEDED.md` (overview - now outdated, use this file instead!)

---

## 🎯 BOTTOM LINE

**You DON'T need to create Officer Outreach or Federal Forecasts tables - you already have them and they're working!**

**You ONLY need 4 new tables:**
1. SUBCONTRACTORS
2. SUB_OUTREACH_TRACKING
3. SUB_PERFORMANCE
4. GPSS ProposalBio Scores (+Learning optional)

**Time: 20-25 minutes total**

---

**Last Updated:** February 4, 2026  
**Corrected based on existing system**
