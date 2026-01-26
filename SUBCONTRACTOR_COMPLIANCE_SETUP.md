# 🔒 SUBCONTRACTOR COMPLIANCE DOCUMENT TRACKING SYSTEM

**Purpose:** Track W-9s, insurance certificates, NDAs, and other compliance documents for all subcontractors

**Setup Time:** 15 minutes  
**Impact:** Ensures compliance-ready subcontractors, prevents contract delays

---

## 📋 TABLE 1: `GPSS SUBCONTRACTOR COMPLIANCE`

**Purpose:** Store and track all compliance documents for each subcontractor

### Fields to Create (14 fields):

| # | Field Name | Field Type | Settings/Options |
|---|-----------|-----------|------------------|
| 1 | **COMPLIANCE_ID** | Auto-number | Primary field - Auto-generated |
| 2 | **SUBCONTRACTOR** | Link to another record | Link to: `GPSS SUBCONTRACTORS` |
| 3 | **DOCUMENT_TYPE** | Single select | Options: `W-9`, `General Liability Insurance`, `Professional Liability Insurance`, `Workers Compensation Insurance`, `Subcontractor Agreement`, `NDA/Confidentiality Agreement`, `Performance Bond`, `Payment Bond`, `Background Check`, `Security Clearance`, `Other` |
| 4 | **DOCUMENT_STATUS** | Single select | Options: `Missing` (red), `Submitted` (yellow), `Under Review` (orange), `Approved` (green), `Expired` (red), `Rejected` (red) |
| 5 | **DATE_RECEIVED** | Date | When document was received |
| 6 | **DATE_APPROVED** | Date | When document was approved |
| 7 | **EXPIRATION_DATE** | Date | When document expires (leave blank if no expiration) |
| 8 | **DAYS_UNTIL_EXPIRATION** | Formula | `IF({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days'), "No Expiration")` |
| 9 | **ALERT_STATUS** | Formula | `IF(AND({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days') < 0), "⚠️ EXPIRED", IF(AND({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days') <= 30), "⏰ Expiring Soon", IF({DOCUMENT_STATUS} = "Approved", "✅ Current", "❌ " & {DOCUMENT_STATUS})))` |
| 10 | **DOCUMENT_FILE** | Attachment | Upload PDF/image of document |
| 11 | **INSURANCE_AMOUNT** | Currency | For insurance documents - coverage amount |
| 12 | **POLICY_NUMBER** | Single line text | Insurance policy or document reference number |
| 13 | **NOTES** | Long text | Additional information or requirements |
| 14 | **CREATED** | Created time | Auto-generated timestamp |

---

## 📋 TABLE 2: UPDATE `GPSS SUBCONTRACTORS`

**Add these 4 new fields to your existing GPSS SUBCONTRACTORS table:**

| Field Name | Field Type | Configuration |
|-----------|-----------|---------------|
| **COMPLIANCE_DOCUMENTS** | Link to another record | Link to: `GPSS SUBCONTRACTOR COMPLIANCE` (allows linking to multiple records) |
| **COMPLIANCE_STATUS** | Formula | `IF(LEN({COMPLIANCE_DOCUMENTS}), CONCATENATE(COUNTA({COMPLIANCE_DOCUMENTS}), " docs tracked"), "No docs")` |
| **LAST_COMPLIANCE_CHECK** | Date | Manual field - last time compliance was verified |
| **COMPLIANCE_READY** | Checkbox | TRUE = All required docs approved, ready to work |

---

## 🎨 VIEWS TO CREATE

### In `GPSS SUBCONTRACTOR COMPLIANCE` Table:

**View 1: "⚠️ Expiring Soon (30 days)"**
- Filter: DAYS_UNTIL_EXPIRATION ≤ 30 AND DAYS_UNTIL_EXPIRATION > 0
- Sort: DAYS_UNTIL_EXPIRATION (ascending)
- Purpose: Proactive renewal reminders

**View 2: "❌ Expired Documents"**
- Filter: ALERT_STATUS contains "EXPIRED"
- Sort: EXPIRATION_DATE (descending)
- Purpose: Immediate action items

**View 3: "📋 By Subcontractor"**
- Group by: SUBCONTRACTOR
- Sort: DOCUMENT_TYPE
- Purpose: See all docs for each sub at a glance

**View 4: "🔴 Missing Documents"**
- Filter: DOCUMENT_STATUS = "Missing"
- Group by: SUBCONTRACTOR
- Purpose: Track what needs to be collected

**View 5: "📄 By Document Type"**
- Group by: DOCUMENT_TYPE
- Filter: DOCUMENT_STATUS = "Approved"
- Purpose: See which subs have which docs

**View 6: "✅ Fully Compliant"**
- Filter: DOCUMENT_STATUS = "Approved" AND (EXPIRATION_DATE is empty OR DAYS_UNTIL_EXPIRATION > 30)
- Group by: SUBCONTRACTOR
- Purpose: See compliance-ready subcontractors

### In `GPSS SUBCONTRACTORS` Table:

**View 7: "✅ Compliance Ready"**
- Filter: COMPLIANCE_READY = TRUE
- Sort: RELIABILITY_RATING (descending)
- Purpose: Filter to compliant subs when sending RFQs

**View 8: "⚠️ Compliance Issues"**
- Filter: COMPLIANCE_READY = FALSE AND RELATIONSHIP_STATUS ≠ "Cold"
- Purpose: Active partners who need compliance attention

---

## ⚙️ QUICK SETUP STEPS

### Step 1: Create Compliance Table (5 min)

1. Go to your NEXUS Airtable base
2. Click **"+"** to add new table
3. Name it: **GPSS SUBCONTRACTOR COMPLIANCE** (exact name)
4. Delete default fields
5. Add all 14 fields from Table 1 above
6. Set field types carefully (Formula fields need exact formulas)

**CRITICAL:** Copy formulas exactly as written above!

### Step 2: Update GPSS SUBCONTRACTORS Table (2 min)

1. Open `GPSS SUBCONTRACTORS` table
2. Add 4 new fields from Table 2 above
3. Link COMPLIANCE_DOCUMENTS to new compliance table

### Step 3: Create Views (3 min)

1. In `GPSS SUBCONTRACTOR COMPLIANCE`: Create 6 views listed above
2. In `GPSS SUBCONTRACTORS`: Create 2 new views listed above

### Step 4: Add Sample Data (5 min)

**Test with one subcontractor:**

1. Pick any subcontractor from `GPSS SUBCONTRACTORS`
2. Go to `GPSS SUBCONTRACTOR COMPLIANCE` table
3. Create 3 sample records:

**Record 1: W-9 (Current)**
```
SUBCONTRACTOR: [Select your test subcontractor]
DOCUMENT_TYPE: W-9
DOCUMENT_STATUS: Approved
DATE_RECEIVED: [Today's date]
DATE_APPROVED: [Today's date]
EXPIRATION_DATE: [Leave blank - W-9s don't expire]
NOTES: "Received via email"
```

**Record 2: General Liability Insurance (Expiring Soon)**
```
SUBCONTRACTOR: [Same test subcontractor]
DOCUMENT_TYPE: General Liability Insurance
DOCUMENT_STATUS: Approved
DATE_RECEIVED: [30 days ago]
DATE_APPROVED: [29 days ago]
EXPIRATION_DATE: [20 days from today]
INSURANCE_AMOUNT: $1,000,000
POLICY_NUMBER: GL-123456
NOTES: "Renewal needed soon"
```

**Record 3: NDA (Missing)**
```
SUBCONTRACTOR: [Same test subcontractor]
DOCUMENT_TYPE: NDA/Confidentiality Agreement
DOCUMENT_STATUS: Missing
NOTES: "Need to request"
```

4. Check that formulas are working:
   - DAYS_UNTIL_EXPIRATION should show "20" for Record 2
   - ALERT_STATUS should show "⏰ Expiring Soon" for Record 2
   - ALERT_STATUS should show "✅ Current" for Record 1

5. Go back to `GPSS SUBCONTRACTORS` table
   - Find your test subcontractor
   - COMPLIANCE_STATUS field should show "3 docs tracked"

---

## 🔄 TYPICAL WORKFLOW

### When Adding a New Subcontractor:

```
1. Create subcontractor in GPSS SUBCONTRACTORS table
   ↓
2. Go to GPSS SUBCONTRACTOR COMPLIANCE
   ↓
3. Create records for REQUIRED documents:
   - W-9 (status: Missing)
   - General Liability Insurance (status: Missing)
   - Subcontractor Agreement (status: Missing)
   - [Any other required docs]
   ↓
4. Email subcontractor requesting documents
   ↓
5. As docs arrive, update:
   - DOCUMENT_STATUS → "Submitted"
   - Upload to DOCUMENT_FILE field
   - Add DATE_RECEIVED
   ↓
6. Review documents:
   - If good: DOCUMENT_STATUS → "Approved"
   - Add DATE_APPROVED
   - Add EXPIRATION_DATE (if applicable)
   ↓
7. When all required docs approved:
   - Go to GPSS SUBCONTRACTORS
   - Check COMPLIANCE_READY = TRUE
   ↓
8. Subcontractor now appears in "Compliance Ready" view
   ↓
9. System will auto-alert 30 days before any doc expires
```

---

## 📊 REQUIRED DOCUMENTS BY CATEGORY

### **Essential (All Subcontractors):**
- ✅ W-9 Form
- ✅ General Liability Insurance ($1M minimum)
- ✅ Subcontractor Agreement (signed)

### **Service Subcontractors:**
- ✅ Workers Compensation Insurance (if employees)
- ✅ Professional Liability Insurance (for professional services)

### **High-Value Contracts ($100K+):**
- ✅ Performance Bond
- ✅ Payment Bond

### **Sensitive/Cleared Work:**
- ✅ Background Checks (all personnel)
- ✅ Security Clearances (if required)
- ✅ NDA/Confidentiality Agreement

### **As Needed:**
- Industry-specific certifications
- Licenses (contractor license, professional license)
- Proof of DBE/MBE/WBE certification

---

## 🚨 COMPLIANCE ALERTS

### Automated Alert System (via NEXUS Backend):

**30 Days Before Expiration:**
- Email notification: "Insurance expiring soon for [Subcontractor]"
- Creates task: "Request renewal documents"

**At Expiration:**
- Email alert: "Document EXPIRED for [Subcontractor]"
- Automatically unchecks COMPLIANCE_READY in GPSS SUBCONTRACTORS
- Blocks subcontractor from RFQ distribution (if enabled)

**Weekly Digest:**
- Every Monday: List of all docs expiring in next 30 days
- List of all expired docs requiring attention

---

## 🎯 BACKEND INTEGRATION

### New API Endpoints (Built in this system):

```
GET /gpss/subcontractors/{id}/compliance
  - Get all compliance docs for subcontractor

POST /gpss/subcontractors/{id}/compliance/check
  - Check if subcontractor is compliance-ready
  - Returns: list of missing/expired docs

POST /gpss/subcontractors/{id}/compliance/add
  - Add new compliance document record

PUT /gpss/subcontractors/compliance/{doc_id}
  - Update document status/details

GET /gpss/compliance/alerts
  - Get all expiring/expired documents

POST /gpss/compliance/send-reminder/{doc_id}
  - Send renewal reminder email to subcontractor
```

### Integration with Existing Workflows:

**When Sending RFQs:**
```python
# Before sending RFQ, check compliance
compliance_check = miner.check_compliance(subcontractor_id)

if not compliance_check['compliant']:
    print(f"⚠️ Warning: {subcontractor['name']} has compliance issues:")
    for issue in compliance_check['issues']:
        print(f"  - {issue}")
    
    # Option 1: Skip this subcontractor
    # Option 2: Send RFQ with compliance request
    # Option 3: Alert user to resolve compliance first
```

**When Creating Teaming Arrangement:**
```python
# Require compliance before teaming
if not subcontractor_is_compliant:
    return {
        "error": "Cannot create teaming arrangement",
        "reason": "Subcontractor missing required compliance documents",
        "missing_docs": ["W-9", "Insurance Certificate"]
    }
```

---

## 📈 REPORTING & DASHBOARDS

### Compliance Metrics to Track:

**Overall Health:**
- % of subcontractors fully compliant
- Average docs per subcontractor
- Time to compliance (from first contact to all docs approved)

**Risk Indicators:**
- Number of expired documents
- Number of docs expiring in next 30 days
- Active partners with compliance issues

**Process Efficiency:**
- Average time from "Submitted" to "Approved"
- Document rejection rate
- Compliance request response rate by subcontractor

---

## ✅ SUCCESS CHECKLIST

### Setup:
- [ ] `GPSS SUBCONTRACTOR COMPLIANCE` table created (14 fields)
- [ ] 4 new fields added to `GPSS SUBCONTRACTORS`
- [ ] 8 views created across both tables
- [ ] Test data added and formulas verified
- [ ] Backend compliance endpoints deployed

### Operational:
- [ ] Required documents identified for your business
- [ ] Email templates created for document requests
- [ ] Compliance check integrated into RFQ workflow
- [ ] Weekly alert system configured
- [ ] Team trained on compliance verification

### Long-term:
- [ ] Compliance status reviewed monthly
- [ ] Expired docs followed up within 48 hours
- [ ] New subcontractors have compliance check before first contract
- [ ] Compliance requirements updated as regulations change

---

## 💡 PRO TIPS

### Document Collection:
- **Request early:** Ask for compliance docs BEFORE you need them
- **Be specific:** Tell subs exactly what you need (format, coverage amounts, etc.)
- **Digital only:** Don't accept paper docs - require scanned PDFs
- **Name consistently:** Save files as "[Company]-[DocType]-[Date].pdf"

### Insurance Requirements:
- **General Liability:** Minimum $1M per occurrence, $2M aggregate
- **Workers Comp:** Statutory limits for state where work is performed
- **Professional Liability:** $1M minimum (for consulting/professional services)
- **Certificate Holder:** Should list YOUR company (not government)

### Expiration Management:
- **Request renewals 45 days early** (gives time for subcontractor to act)
- **Set calendar reminders** for high-value partners
- **Batch requests** (ask for all expiring docs at once)

### Common Mistakes to Avoid:
- ❌ Accepting expired documents "temporarily"
- ❌ Not checking certificate holder name
- ❌ Missing expiration dates on insurance certificates
- ❌ Not verifying coverage amounts meet requirements
- ❌ Accepting "we'll send it later" promises

---

## 🚀 NEXT STEPS

### Immediate (Today):
1. Create the Airtable tables (15 min)
2. Add test data to verify formulas work
3. Deploy backend compliance endpoints
4. Test compliance check API

### This Week:
1. Review existing subcontractors, identify missing docs
2. Create document request email templates
3. Send compliance requests to active partners
4. Set up weekly alert system

### This Month:
1. Achieve 100% compliance for active partners
2. Build compliance check into RFQ workflow
3. Create compliance requirement checklist for each service type
4. Train team on compliance verification

---

## 📞 QUICK REFERENCE

**Airtable Tables:**
- `GPSS SUBCONTRACTOR COMPLIANCE` - Document tracking
- `GPSS SUBCONTRACTORS` - Updated with compliance fields

**Key Views:**
- "⚠️ Expiring Soon" - Proactive action items
- "❌ Expired Documents" - Urgent issues
- "✅ Compliance Ready" - Subs ready to work

**API Endpoints:**
- `/gpss/subcontractors/{id}/compliance/check` - Verify compliance
- `/gpss/compliance/alerts` - Get expiring/expired docs

**Required Documents (Minimum):**
- W-9
- General Liability Insurance ($1M+)
- Subcontractor Agreement (signed)

---

## 🎉 EXPECTED RESULTS

**Before Compliance Tracking:**
- ❌ Discover missing W-9 during contract execution
- ❌ Insurance expired without notice
- ❌ Manual tracking in spreadsheets
- ❌ Risk of non-compliant subcontractor work
- ❌ Contract delays due to compliance issues

**After Compliance Tracking:**
- ✅ All docs verified BEFORE sending RFQs
- ✅ Auto-alerts 30 days before expiration
- ✅ One-click compliance status check
- ✅ Government-ready documentation
- ✅ Professional subcontractor management
- ✅ Zero compliance-related contract delays

---

**Total Setup Time:** 15 minutes  
**Payoff:** Risk mitigation, professional operation, zero compliance delays

**You're now equipped for enterprise-grade subcontractor compliance management!** 🔒
