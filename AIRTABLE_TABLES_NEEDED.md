# AIRTABLE TABLES NEEDED - QUICK REFERENCE

---

## ✅ WHAT YOU NEED

**8 Tables Total** (2 existing + 6 new)

---

## 📊 THE TABLES

### **1. Opportunities** ✅ (Should already exist)
Where your bids/opportunities live

**If missing, create with:** Title, Solicitation #, Client, Due Date, Status

---

### **2. CapabilityStatements** ✅ (Should already exist)
Where auto-generated capability statements are stored

**If missing, create with:** OpportunityID (link), PDFPath, GeneratedDate

---

### **3. OFFICER_OUTREACH_TRACKING** ⭐ CREATE THIS

**Purpose:** Track introduction letters to procurement officers

**Key fields:**
- OpportunityID (link to Opportunities)
- OfficerName
- OfficerEmail
- OutreachDate
- LetterSent (checkbox)
- CAPSTATGENERATED (checkbox)
- ResponseReceived (checkbox)
- Status (Sent, Pending, Responded)

**Used by:** Officer Outreach Framework, Auto CapStat

---

### **4. SUBCONTRACTORS** ⭐ CREATE THIS

**Purpose:** Master database of all subcontractors

**Key fields:**
- CompanyName (primary)
- ContactName
- Email
- Phone
- ServiceTypes (multiple select: Landscaping, Pressure Washing, NEMT, etc.)
- GoogleRating
- YelpRating
- Status (New, Active, Inactive)

**Used by:** Automated Sub Sourcing, Service Sub Framework

---

### **5. SUB_OUTREACH_TRACKING** ⭐ CREATE THIS

**Purpose:** Track outreach to subs for each opportunity

**Key fields:**
- OpportunityID (link to Opportunities)
- SubcontractorID (link to SUBCONTRACTORS)
- OutreachDate
- ResponseStatus (Pending, Interested, Declined)
- QuoteAmount (currency)
- Available (checkbox)
- Selected (checkbox)

**Used by:** Automated Sub Sourcing, Transformation Framework

---

### **6. SUB_PERFORMANCE** ⭐ CREATE THIS

**Purpose:** Track actual performance on projects (builds transformation metrics)

**Key fields:**
- OpportunityID (link)
- SubcontractorID (link)
- ProjectStartDate
- CompletionRate (%)
- ClientSatisfaction (1-5 stars)
- WouldUseAgain (checkbox)

**Used by:** Transformation Framework (proof/metrics), Sub database

---

### **7. GPSS ProposalBio Scores** ⭐ CREATE THIS

**Purpose:** Store ProposalBio quality scores

**Key fields:**
- Proposal (link to Opportunities)
- BiohackNumber (1-10)
- BiohackName (Mirror Neuron, Cognitive Ease, etc.)
- Score (0-10)
- PassFail (Pass/Fail)

**Used by:** ProposalBio Framework

---

### **8. GPSS ProposalBio Learning** ⭐ CREATE THIS

**Purpose:** Track proposal outcomes for learning

**Key fields:**
- Proposal (link to Opportunities)
- Outcome (Won, Lost, No Decision)
- WinValue (currency)
- CompositeScore (0-100)
- TransformationScore (0-50)

**Used by:** ProposalBio Framework, continuous improvement

---

## 🎯 PRIORITY ORDER

**Create in this order:**

### **Week 1: Officer Outreach** (if using that framework)
1. OFFICER_OUTREACH_TRACKING

### **Week 2: Sub Sourcing** (before first service bid)
2. SUBCONTRACTORS
3. SUB_OUTREACH_TRACKING

### **Week 3: Performance Tracking** (after first project)
4. SUB_PERFORMANCE

### **Week 4: Proposal Quality** (when writing proposals)
5. GPSS ProposalBio Scores
6. GPSS ProposalBio Learning

---

## ⏱️ SETUP TIME

**Per table:**
- OFFICER_OUTREACH_TRACKING: 5 minutes
- SUBCONTRACTORS: 7 minutes
- SUB_OUTREACH_TRACKING: 5 minutes
- SUB_PERFORMANCE: 5 minutes
- ProposalBio Scores: 3 minutes
- ProposalBio Learning: 3 minutes

**Total: 30 minutes to create all 6 new tables**

---

## 📋 QUICK SETUP INSTRUCTIONS

**For each table:**

1. **Go to your Airtable base**
2. **Click "+" to add table**
3. **Name it exactly** (e.g., "SUBCONTRACTORS")
4. **Add fields from schema** (see `AIRTABLE_COMPLETE_SCHEMA_FOR_FRAMEWORKS.md`)
5. **Set up links** to other tables
6. **Done!**

---

## 🔗 HOW THEY CONNECT

```
YOU ALREADY HAVE:
Opportunities → Links everything together

CREATE THESE:
├─ OFFICER_OUTREACH_TRACKING → Links to Opportunities
│  └─ CapabilityStatements → Links to Outreach records
│
├─ SUBCONTRACTORS → Master list of all subs
│  ├─ SUB_OUTREACH_TRACKING → Links to Opportunities + SUBCONTRACTORS
│  └─ SUB_PERFORMANCE → Links to Opportunities + SUBCONTRACTORS
│
└─ ProposalBio tables → Link to Opportunities
   ├─ GPSS ProposalBio Scores (10 per proposal)
   └─ GPSS ProposalBio Learning (1 per proposal)
```

---

## 💡 WHICH FRAMEWORKS NEED WHICH TABLES?

| Framework | Tables Needed |
|-----------|---------------|
| **Officer Outreach** | Opportunities, OFFICER_OUTREACH_TRACKING |
| **Auto CapStat** | Opportunities, CapabilityStatements, OFFICER_OUTREACH_TRACKING |
| **Grainger Script** | None (just negotiation, no tracking) |
| **Service Sub** | Opportunities, SUBCONTRACTORS, SUB_OUTREACH_TRACKING, SUB_PERFORMANCE |
| **Automated Sub Sourcing** | SUBCONTRACTORS, SUB_OUTREACH_TRACKING |
| **Transformation** | Opportunities, SUB_PERFORMANCE (for metrics) |
| **ProposalBio** | Opportunities, GPSS ProposalBio Scores, GPSS ProposalBio Learning |

---

## 🚨 CRITICAL FIELDS (Don't Skip These)

### **OFFICER_OUTREACH_TRACKING:**
- OpportunityID (link)
- OfficerEmail
- OutreachDate
- CAPSTATGENERATED

### **SUBCONTRACTORS:**
- CompanyName (primary)
- Email
- Phone
- ServiceTypes
- GoogleRating

### **SUB_OUTREACH_TRACKING:**
- OpportunityID (link)
- SubcontractorID (link)
- ResponseStatus
- QuoteAmount

### **SUB_PERFORMANCE:**
- OpportunityID (link)
- SubcontractorID (link)
- CompletionRate
- ClientSatisfaction

---

## 📖 FULL DOCUMENTATION

**See complete schemas with all fields:**
→ `AIRTABLE_COMPLETE_SCHEMA_FOR_FRAMEWORKS.md`

**Contains:**
- Every field name
- Field types
- Options/selections
- Formula fields
- Linking instructions

---

## ✅ SETUP CHECKLIST

**Before using frameworks:**

- [ ] Opportunities table exists (or create it)
- [ ] CapabilityStatements table exists (or create it)

**Before using Officer Outreach:**
- [ ] OFFICER_OUTREACH_TRACKING table created

**Before using Automated Sub Sourcing:**
- [ ] SUBCONTRACTORS table created
- [ ] SUB_OUTREACH_TRACKING table created
- [ ] Tables linked properly

**Before tracking sub performance:**
- [ ] SUB_PERFORMANCE table created

**Before using ProposalBio:**
- [ ] GPSS ProposalBio Scores table created
- [ ] GPSS ProposalBio Learning table created

---

## 🎯 BOTTOM LINE

**To use all frameworks, you need:**
- ✅ 2 existing tables (Opportunities, CapabilityStatements)
- ⭐ 6 new tables (30 minutes to create)

**Then all automations will work!**

---

**Create tables as you need them. Start with Officer Outreach if you're doing outreach, or Sub tables if you have a service bid coming up.**

---

**Last Updated:** February 4, 2026
