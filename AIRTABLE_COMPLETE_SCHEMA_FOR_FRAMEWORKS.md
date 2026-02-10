# COMPLETE AIRTABLE SCHEMA FOR ALL FRAMEWORKS
**All tables needed for Officer Outreach, Auto CapStat, Service Subs, Transformation, and ProposalBio**

---

## 📊 REQUIRED TABLES (10 Total)

### **EXISTING TABLES** (You likely already have these)
1. ✅ **Opportunities** (or GPSS Opportunities)
2. ✅ **CapabilityStatements**

### **NEW TABLES NEEDED** (Create these)
3. ⭐ **OFFICER_OUTREACH_TRACKING**
4. ⭐ **SUBCONTRACTORS**
5. ⭐ **SUB_OUTREACH_TRACKING**
6. ⭐ **SUB_PERFORMANCE**
7. ⭐ **GPSS ProposalBio Scores**
8. ⭐ **GPSS ProposalBio Learning**

---

## 🔧 TABLE SCHEMAS (Copy/Paste Ready)

### **TABLE 1: Opportunities** (Should exist)

**If missing, add these fields:**

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| Title | Single line text | |
| SolicitationNumber | Single line text | |
| ClientName | Single line text | |
| Agency | Single line text | |
| ServiceType | Single select | Landscaping, Pressure Washing, NEMT, Supplies, etc. |
| Category | Single select | Services, Products, Construction, Professional Services |
| Location | Single line text | |
| GeneralLocation | Single line text | County/region only (protect buyer!) |
| Description | Long text | |
| DueDate | Date | |
| StartDate | Date | |
| ContractLength | Single line text | "7 months", "1 year", etc. |
| EstimatedValue | Currency | |
| Status | Single select | New, Pursuing, Submitted, Won, Lost |
| SetAsideType | Single select | EDWOSB, WOSB, 8(a), HUBZone, Unrestricted |
| ProcurementOfficer | Single line text | |
| ProcurementOfficerEmail | Email | |
| Notes | Long text | |

---

### **TABLE 2: CapabilityStatements** (Should exist)

**If missing, add these fields:**

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| OpportunityID | Link to Opportunities | |
| Title | Single line text | |
| Template | Single select | Standard, Federal, Construction, Services |
| HTMLPath | Single line text | File path to HTML |
| PDFPath | Single line text | File path to PDF |
| ConfigPath | Single line text | File path to config JSON |
| Generated | Checkbox | |
| GeneratedDate | Date with time | |
| NAICSCodes | Multiple select | List of NAICS codes |
| AccentColor | Single line text | Hex color code |

---

### **TABLE 3: OFFICER_OUTREACH_TRACKING** ⭐ NEW

**Purpose:** Track introduction letters sent to procurement officers

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| OpportunityID | Link to Opportunities | |
| OfficerName | Single line text | |
| OfficerTitle | Single line text | |
| OfficerEmail | Email | |
| OfficerPhone | Phone number | |
| AgencyName | Single line text | |
| SolicitationNumber | Single line text | |
| OpportunityTitle | Single line text | |
| OpportunityType | Single select | Sources Sought, RFP, RFQ, IFB |
| OutreachDate | Date with time | |
| EmailSubject | Long text | |
| EmailBody | Long text | |
| LetterSent | Checkbox | |
| CAPSTATGENERATED | Checkbox | CapStat generated for this outreach? |
| CapStatID | Link to CapabilityStatements | |
| ResponseReceived | Checkbox | |
| ResponseDate | Date with time | |
| ResponseType | Single select | Interested, Added to Vendor List, Not Interested, No Response |
| FollowUpNeeded | Checkbox | |
| FollowUpDate | Date | |
| FollowUpSent | Checkbox | |
| AddedToVendorList | Checkbox | |
| FutureOpportunities | Long text | |
| Notes | Long text | |
| Status | Single select | Sent, Pending Response, Responded, Follow-up Sent, Closed |

**Formula fields (optional but useful):**
- DaysSinceOutreach: `DATETIME_DIFF(NOW(), {OutreachDate}, 'days')`
- NeedsFollowUp: `AND({FollowUpNeeded}, NOT({FollowUpSent}), {DaysSinceOutreach}>7)`

---

### **TABLE 4: SUBCONTRACTORS** ⭐ NEW

**Purpose:** Master database of all subcontractors

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| CompanyName | Single line text | PRIMARY FIELD |
| ContactName | Single line text | |
| Email | Email | |
| Phone | Phone number | |
| Website | URL | |
| Address | Single line text | |
| City | Single line text | |
| State | Single select | All 50 states + DC |
| Zip | Number | |
| ServiceTypes | Multiple select | Landscaping, Pressure Washing, NEMT, Janitorial, HVAC, Plumbing, Electrical, Painting, Snow Removal, Construction, IT, Security, Other |
| CoverageArea | Single line text | "Oakland County, MI" or "Southeast Michigan" |
| GoogleRating | Number | 1 decimal place |
| YelpRating | Number | 1 decimal place |
| TotalReviews | Number | |
| YearsInBusiness | Number | |
| CommercialExperience | Checkbox | |
| GovernmentExperience | Checkbox | |
| Insurance_Liability | Single line text | "$1M", "$2M", etc. |
| Insurance_WorkersComp | Checkbox | |
| License_Number | Single line text | |
| License_State | Single select | All 50 states + DC |
| Certifications | Multiple select | MNLA, ISA, MBE, WBE, SBE, etc. |
| GoogleMapsURL | URL | |
| YelpURL | URL | |
| FirstContactDate | Date | |
| LastContactDate | Date | |
| Status | Single select | New, Active, Inactive, Blacklist |
| AvgResponseTime_Hours | Number | 1 decimal |
| AvgQuoteTime_Hours | Number | 1 decimal |
| UsedBefore | Checkbox | |
| WouldUseAgain | Checkbox | |
| OverallRating | Rating | 1-5 stars |
| Strengths | Long text | |
| Weaknesses | Long text | |
| Notes | Long text | |
| Source | Single select | Google Maps, Yelp, Referral, Past Project, Other |
| TimesContacted | Number | Count from SUB_OUTREACH_TRACKING |
| TimesUsed | Number | Count from SUB_PERFORMANCE |

**Linked fields:**
- Outreach (Link to SUB_OUTREACH_TRACKING)
- Performance (Link to SUB_PERFORMANCE)

---

### **TABLE 5: SUB_OUTREACH_TRACKING** ⭐ NEW

**Purpose:** Track every outreach to subcontractors

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| OpportunityID | Link to Opportunities | |
| SubcontractorID | Link to SUBCONTRACTORS | |
| OutreachDate | Date with time | |
| EmailSubject | Long text | |
| EmailBody | Long text | |
| EmailSent | Checkbox | |
| EmailOpened | Checkbox | (SendGrid webhook) |
| EmailOpenedDate | Date with time | |
| EmailClicked | Checkbox | (SendGrid webhook) |
| ResponseStatus | Single select | Pending, Interested, Declined, No Response |
| ResponseDate | Date with time | |
| ResponseMethod | Single select | Email, Phone, Text |
| QuoteAmount | Currency | |
| QuoteDetails | Long text | |
| Available | Checkbox | |
| AvailabilityNotes | Long text | |
| FollowUpNeeded | Checkbox | |
| FollowUpDate | Date | |
| FollowUpSent | Checkbox | |
| LOI_Requested | Checkbox | Letter of Intent requested? |
| LOI_Received | Checkbox | |
| LOI_ReceivedDate | Date | |
| InsuranceCert_Requested | Checkbox | |
| InsuranceCert_Received | Checkbox | |
| InsuranceCert_ReceivedDate | Date | |
| References_Requested | Checkbox | |
| References_Received | Checkbox | |
| Selected | Checkbox | Selected for this project? |
| SelectionReason | Long text | |
| DeclineReason | Long text | If declined, why? |
| Notes | Long text | |

**Formula fields:**
- ResponseTime_Hours: `DATETIME_DIFF({ResponseDate}, {OutreachDate}, 'hours')`
- DaysSinceOutreach: `DATETIME_DIFF(NOW(), {OutreachDate}, 'days')`
- NeedsFollowUp: `AND({FollowUpNeeded}, NOT({FollowUpSent}), {DaysSinceOutreach}>3)`

---

### **TABLE 6: SUB_PERFORMANCE** ⭐ NEW

**Purpose:** Track subcontractor performance on actual projects

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| OpportunityID | Link to Opportunities | |
| SubcontractorID | Link to SUBCONTRACTORS | |
| ProjectName | Single line text | |
| ProjectStartDate | Date | |
| ProjectEndDate | Date | |
| ServiceType | Single select | Same as SUBCONTRACTORS ServiceTypes |
| NumberOfServices | Number | Total scheduled |
| CompletedServices | Number | Actually completed |
| MissedServices | Number | No-shows |
| CompletionRate | Percent | Formula: CompletedServices / NumberOfServices |
| AvgResponseTime_Hours | Number | 1 decimal |
| QualityIssues | Number | Count of issues |
| ClientSatisfaction | Rating | 1-5 stars |
| OnTimePerformance | Percent | |
| CommunicationRating | Rating | 1-5 stars |
| SafetyIncidents | Number | |
| WouldUseAgain | Checkbox | |
| Strengths | Long text | |
| WeaknessesImprovements | Long text | |
| OverallRating | Rating | 1-5 stars |
| Notes | Long text | |
| DateRecorded | Date with time | |

**Formula fields:**
- CompletionRate: `{CompletedServices}/{NumberOfServices}`
- MissedRate: `{MissedServices}/{NumberOfServices}`

---

### **TABLE 7: GPSS ProposalBio Scores** ⭐ NEW

**Purpose:** Store ProposalBio analysis scores for proposals

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| Proposal | Link to Opportunities | (or GPSS Proposals table) |
| BiohackNumber | Number | 1-10 |
| BiohackName | Single line text | Mirror Neuron, Cognitive Ease, etc. |
| Score | Number | 2 decimals (0-10) |
| PassFail | Single select | Pass, Fail |
| Threshold | Number | Usually 6.0 |
| AnalyzedDate | Date with time | |
| Notes | Long text | |

**The 10 Biohacks:**
1. Mirror Neuron (tone match)
2. Cognitive Ease (readability)
3. Story Arc (challenge-solution-result)
4. Reciprocity (value upfront)
5. Yes Stacking (affirmations)
6. Familiarity (mirror RFP language)
7. Name Recognition (agency mentions)
8. Sensory Language (concrete terms)
9. Rhythm (sentence variety)
10. Eye Tracking (visual hierarchy)

---

### **TABLE 8: GPSS ProposalBio Learning** ⭐ NEW

**Purpose:** Track proposal outcomes for continuous learning

| Field Name | Type | Options/Details |
|------------|------|-----------------|
| Proposal | Link to Opportunities | |
| Outcome | Single select | Won, Lost, No Decision |
| WinValue | Currency | Contract value if won |
| CompositeScore | Number | 2 decimals (0-100) |
| TransformationScore | Number | From Transformation Checklist (0-50) |
| AllBiohacksAbove6 | Checkbox | Quality gate passed? |
| AgencyType | Single select | Federal, State, Local, Cooperative |
| Region | Single select | Northeast, Southeast, Midwest, Southwest, West |
| SetAsideType | Single select | EDWOSB, WOSB, 8(a), Unrestricted |
| RecordedDate | Date with time | |
| LessonsLearned | Long text | |
| Notes | Long text | |

**Formula fields (for analytics):**
- WinRate: Calculated across all records
- AvgScoreForWins: Average CompositeScore where Outcome=Won
- AvgScoreForLosses: Average CompositeScore where Outcome=Lost

---

## 🔗 TABLE RELATIONSHIPS (How They Connect)

```
OPPORTUNITIES (Main Hub)
├─ Links to → OFFICER_OUTREACH_TRACKING (many)
│  └─ Links to → CapabilityStatements (one per outreach)
│
├─ Links to → SUB_OUTREACH_TRACKING (many)
│  └─ Links to → SUBCONTRACTORS (one)
│     └─ Links back to → SUB_PERFORMANCE (many)
│
├─ Links to → GPSS ProposalBio Scores (many - 10 per proposal)
│
└─ Links to → GPSS ProposalBio Learning (one per proposal)

SUBCONTRACTORS (Master List)
├─ Links to → SUB_OUTREACH_TRACKING (many times contacted)
└─ Links to → SUB_PERFORMANCE (many projects worked on)
```

---

## ✅ QUICK SETUP CHECKLIST

### **Step 1: Check Existing Tables** (5 minutes)
- [ ] Do you have **Opportunities** table? (or GPSS Opportunities)
- [ ] Do you have **CapabilityStatements** table?
- [ ] If yes to both, add any missing fields from above
- [ ] If no, create them first

### **Step 2: Create Officer Outreach Table** (5 minutes)
- [ ] Create table: **OFFICER_OUTREACH_TRACKING**
- [ ] Add all fields from schema above
- [ ] Link to Opportunities table
- [ ] Link to CapabilityStatements table

### **Step 3: Create Subcontractor Tables** (10 minutes)
- [ ] Create table: **SUBCONTRACTORS**
- [ ] Add all fields from schema above
- [ ] Create table: **SUB_OUTREACH_TRACKING**
- [ ] Add all fields, link to Opportunities and SUBCONTRACTORS
- [ ] Create table: **SUB_PERFORMANCE**
- [ ] Add all fields, link to Opportunities and SUBCONTRACTORS

### **Step 4: Create ProposalBio Tables** (5 minutes)
- [ ] Create table: **GPSS ProposalBio Scores**
- [ ] Add all fields, link to Opportunities
- [ ] Create table: **GPSS ProposalBio Learning**
- [ ] Add all fields, link to Opportunities

### **Step 5: Test Connections** (5 minutes)
- [ ] Create test Opportunity record
- [ ] Create test Outreach record linked to it
- [ ] Create test Subcontractor record
- [ ] Verify links work properly

---

## 📋 COPY-PASTE FIELD SETUP

### **For Officer Outreach Tracking:**

```
Name: OpportunityID | Type: Link to Opportunities
Name: OfficerName | Type: Single line text
Name: OfficerEmail | Type: Email
Name: OutreachDate | Type: Date with time
Name: LetterSent | Type: Checkbox
Name: CAPSTATGENERATED | Type: Checkbox
Name: ResponseReceived | Type: Checkbox
Name: Status | Type: Single select | Options: Sent, Pending Response, Responded, Follow-up Sent, Closed
```

### **For Subcontractors:**

```
Name: CompanyName | Type: Single line text (PRIMARY)
Name: ContactName | Type: Single line text
Name: Email | Type: Email
Name: Phone | Type: Phone number
Name: ServiceTypes | Type: Multiple select | Options: Landscaping, Pressure Washing, NEMT, Janitorial, HVAC, Plumbing, Electrical, Other
Name: GoogleRating | Type: Number | Format: 1 decimal
Name: YelpRating | Type: Number | Format: 1 decimal
Name: Status | Type: Single select | Options: New, Active, Inactive, Blacklist
```

### **For Sub Outreach Tracking:**

```
Name: OpportunityID | Type: Link to Opportunities
Name: SubcontractorID | Type: Link to SUBCONTRACTORS
Name: OutreachDate | Type: Date with time
Name: EmailSent | Type: Checkbox
Name: ResponseStatus | Type: Single select | Options: Pending, Interested, Declined, No Response
Name: QuoteAmount | Type: Currency
Name: Available | Type: Checkbox
Name: Selected | Type: Checkbox
```

---

## 🎯 WHAT EACH TABLE ENABLES

### **OFFICER_OUTREACH_TRACKING:**
✅ Track introduction letters sent  
✅ Monitor response rates  
✅ Schedule follow-ups automatically  
✅ Build vendor list relationships  
✅ Links to auto-generated capability statements

### **SUBCONTRACTORS:**
✅ Master database of all subs  
✅ Track ratings, reviews, contact info  
✅ Monitor performance over time  
✅ Build preferred sub list  
✅ Quick access for future bids

### **SUB_OUTREACH_TRACKING:**
✅ Track every sub contacted per opportunity  
✅ Monitor response rates and times  
✅ Compare quotes side-by-side  
✅ Track LOI and insurance status  
✅ Document selection decisions

### **SUB_PERFORMANCE:**
✅ Track actual project performance  
✅ Build transformation metrics library  
✅ Calculate completion rates, quality scores  
✅ Identify best subs to use again  
✅ Prove outcomes for proposals

### **ProposalBio Tables:**
✅ Store quality scores for every proposal  
✅ Track which proposals win vs. lose  
✅ Correlate scores with outcomes  
✅ Continuous learning system  
✅ Improve over time

---

## 💡 PRO TIPS

### **1. Start Small**
Create tables one at a time:
- Week 1: OFFICER_OUTREACH_TRACKING
- Week 2: SUBCONTRACTORS + SUB_OUTREACH_TRACKING
- Week 3: SUB_PERFORMANCE
- Week 4: ProposalBio tables

### **2. Use Views**
Create filtered views:
- "Active Outreach" (status = Sent, Pending Response)
- "Need Follow-up" (FollowUpNeeded = true, FollowUpSent = false)
- "Top Subs" (Rating ≥4.5, WouldUseAgain = true)
- "Interested Subs" (ResponseStatus = Interested)

### **3. Automate with Airtable Automations**
- When OutreachDate is 7 days ago → Set FollowUpNeeded = true
- When ResponseStatus = Interested → Send notification
- When Selected = true → Create SUB_PERFORMANCE record

### **4. Use Interfaces**
Create Airtable interfaces for:
- Officer outreach dashboard
- Sub sourcing workflow
- Quote comparison view
- Performance tracking

---

## 🚀 INTEGRATION WITH FRAMEWORKS

**These tables power:**

✅ **Officer Outreach Framework**  
→ OFFICER_OUTREACH_TRACKING table

✅ **Auto CapStat Framework**  
→ Links CapabilityStatements to Outreach records

✅ **Service Sub Framework**  
→ SUBCONTRACTORS + SUB_OUTREACH_TRACKING + SUB_PERFORMANCE

✅ **Transformation Framework**  
→ Uses SUB_PERFORMANCE data for metrics

✅ **ProposalBio Framework**  
→ GPSS ProposalBio Scores + Learning tables

---

## 📊 SCHEMA DIAGRAM

```
┌─────────────────────────┐
│     OPPORTUNITIES       │ ← Main hub
│  (or GPSS Opportunities)│
└───────────┬─────────────┘
            │
            ├─────────────────────────────────┐
            │                                 │
            ↓                                 ↓
┌──────────────────────────┐   ┌──────────────────────────┐
│ OFFICER_OUTREACH_TRACKING│   │  CAPABILITY_STATEMENTS   │
└──────────────────────────┘   └──────────────────────────┘
            │
            ↓
┌──────────────────────────┐
│ SUB_OUTREACH_TRACKING    │
└───────────┬──────────────┘
            │
            ↓
┌──────────────────────────┐
│    SUBCONTRACTORS        │ ← Master list
└───────────┬──────────────┘
            │
            ↓
┌──────────────────────────┐
│   SUB_PERFORMANCE        │ ← Builds metrics
└──────────────────────────┘

OPPORTUNITIES also links to:
┌──────────────────────────┐
│ GPSS ProposalBio Scores  │ ← 10 records per proposal
└──────────────────────────┘
            │
            ↓
┌──────────────────────────┐
│ GPSS ProposalBio Learning│ ← Win/loss tracking
└──────────────────────────┘
```

---

## 🔧 AIRTABLE BASE SETUP

### **Option A: Add to Existing Base**
If you have a base with Opportunities:
- Add the 6 new tables to that base
- Link them to existing Opportunities table
- Keeps everything in one place

### **Option B: Create New Base**
If starting fresh:
- Create new base: "DEE DAVIS INC Operations"
- Create all 8 tables
- Import existing opportunities if you have them

**Recommendation: Option A** (add to existing base)

---

## ⏱️ TIME TO SET UP

**Total setup time: 30-60 minutes**

- Create tables: 20 minutes
- Add all fields: 20 minutes
- Set up links: 10 minutes
- Create test records: 10 minutes

**Then you're ready to automate!**

---

**Need help setting this up? Start with Officer Outreach table first, then add Sub tables when you get your first service bid.**

---

**Last Updated:** February 4, 2026  
**Owner:** Dee Davis
