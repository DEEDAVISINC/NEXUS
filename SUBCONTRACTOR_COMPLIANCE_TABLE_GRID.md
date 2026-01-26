# GPSS SUBCONTRACTOR COMPLIANCE TABLE - FIELD GRID
**Complete setup reference**

---

## 📋 **QUICK SPECS**

**Table name:** `GPSS SUBCONTRACTOR COMPLIANCE` (all caps with spaces)  
**Total fields:** 14  
**Setup time:** 15 minutes  
**Purpose:** Track W-9s, insurance, NDAs, and compliance documents

---

## 🗂️ **FIELD-BY-FIELD GRID**

| # | Field Name | Field Type | Configuration | Notes |
|---|------------|------------|---------------|-------|
| 1 | `COMPLIANCE_ID` | **Autonumber** | Prefix: `C-`<br>Number of digits: `4` | Auto-generates: C-0001, C-0002, etc. |
| 2 | `SUBCONTRACTOR` | **Link to another record** | Link to: `GPSS SUBCONTRACTORS` table<br>Allow multiple: **NO** | Links to the subcontractor |
| 3 | `DOCUMENT_TYPE` | **Single select** | **Options:**<br>• W-9<br>• General Liability Insurance<br>• Workers Comp Insurance<br>• Auto Insurance<br>• NDA<br>• Certificate of Insurance<br>• Business License<br>• Bond<br>• Other | Type of compliance document |
| 4 | `DOCUMENT_STATUS` | **Single select** | **Options:**<br>• Missing (🔴 Red)<br>• Submitted (🟡 Yellow)<br>• Approved (🟢 Green)<br>• Expired (🔴 Red)<br>• Rejected (🔴 Red)<br><br>**Default:** `Missing` | Current status |
| 5 | `DATE_RECEIVED` | **Date** | Include a time field: **YES** ✓<br>Time format: 12 hour<br>Date format: US (M/D/YYYY) | When document received |
| 6 | `DATE_APPROVED` | **Date** | Include a time field: **YES** ✓<br>Time format: 12 hour<br>Date format: US (M/D/YYYY) | When document approved |
| 7 | `EXPIRATION_DATE` | **Date** | Include a time field: **NO**<br>Date format: US (M/D/YYYY) | When document expires |
| 8 | `DAYS_UNTIL_EXPIRATION` | **Formula** | Formula: `IF(EXPIRATION_DATE, DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days'), "")` | Auto-calculates days left |
| 9 | `ALERT_STATUS` | **Formula** | Formula: See below ⬇️ | Shows: ⚠️ EXPIRED, ⏰ Expiring Soon, ✅ Current |
| 10 | `DOCUMENT_FILE` | **Attachment** | - | Upload PDF/image of document |
| 11 | `INSURANCE_AMOUNT` | **Currency** | Currency: $ USD<br>Precision: 2 decimals | Insurance coverage amount |
| 12 | `POLICY_NUMBER` | **Single line text** | - | Insurance/document policy # |
| 13 | `NOTES` | **Long text** | Enable rich text: **YES** ✓ | Any notes about document |
| 14 | `CREATED` | **Created time** | Include a time field: **YES** ✓<br>Time format: 12 hour | When record was created |

---

## 📐 **FORMULA FOR FIELD #9: ALERT_STATUS**

Copy and paste this formula exactly:

```
IF(
  EXPIRATION_DATE,
  IF(
    DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days') < 0,
    "⚠️ EXPIRED (" & ABS(DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days')) & " days ago)",
    IF(
      DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days') <= 30,
      "⏰ Expiring Soon (" & DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days') & " days)",
      "✅ Current (" & DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days') & " days)"
    )
  ),
  ""
)
```

**What it does:**
- **Expired:** Shows red warning if date passed
- **Expiring Soon:** Shows yellow warning if < 30 days left
- **Current:** Shows green checkmark if > 30 days left

---

## 🎨 **RECOMMENDED VIEWS**

### **View 1: All Compliance** (Default Grid View)
- **Sort:** `CREATED` (newest first)
- **Fields shown:** All 14 fields
- **Filter:** None

---

### **View 2: Alerts (Expired or Expiring)**
- **Filter:** `ALERT_STATUS` contains "EXPIRED" OR "Expiring Soon"
- **Sort:** `DAYS_UNTIL_EXPIRATION` (ascending - soonest first)
- **Fields shown:** SUBCONTRACTOR, DOCUMENT_TYPE, EXPIRATION_DATE, ALERT_STATUS, DOCUMENT_STATUS

---

### **View 3: Missing Documents**
- **Filter:** `DOCUMENT_STATUS` is `Missing`
- **Group by:** `SUBCONTRACTOR`
- **Fields shown:** SUBCONTRACTOR, DOCUMENT_TYPE, DOCUMENT_STATUS, NOTES

---

### **View 4: Approved & Current**
- **Filter:** `DOCUMENT_STATUS` is `Approved` AND `ALERT_STATUS` contains "Current"
- **Group by:** `SUBCONTRACTOR`
- **Fields shown:** SUBCONTRACTOR, DOCUMENT_TYPE, DATE_APPROVED, EXPIRATION_DATE, INSURANCE_AMOUNT

---

### **View 5: By Document Type**
- **Group by:** `DOCUMENT_TYPE`
- **Sort:** `EXPIRATION_DATE` (soonest first)
- **Fields shown:** DOCUMENT_TYPE, SUBCONTRACTOR, DOCUMENT_STATUS, EXPIRATION_DATE, ALERT_STATUS

---

## 📊 **EXAMPLE RECORDS**

### **Record 1: Current Insurance**
```
COMPLIANCE_ID: C-0001
SUBCONTRACTOR: [Link to "ABC Janitorial Services"]
DOCUMENT_TYPE: General Liability Insurance
DOCUMENT_STATUS: Approved
DATE_RECEIVED: 1/15/2026 10:30 AM
DATE_APPROVED: 1/16/2026 2:00 PM
EXPIRATION_DATE: 7/15/2026
DAYS_UNTIL_EXPIRATION: 171
ALERT_STATUS: ✅ Current (171 days)
DOCUMENT_FILE: [PDF attachment]
INSURANCE_AMOUNT: $2,000,000.00
POLICY_NUMBER: GL-123456789
NOTES: Certificate of insurance on file
CREATED: 1/15/2026 10:30 AM
```

---

### **Record 2: Expiring Soon**
```
COMPLIANCE_ID: C-0002
SUBCONTRACTOR: [Link to "XYZ Construction"]
DOCUMENT_TYPE: Workers Comp Insurance
DOCUMENT_STATUS: Approved
DATE_RECEIVED: 12/1/2025 9:00 AM
DATE_APPROVED: 12/1/2025 3:00 PM
EXPIRATION_DATE: 2/10/2026
DAYS_UNTIL_EXPIRATION: 16
ALERT_STATUS: ⏰ Expiring Soon (16 days)
DOCUMENT_FILE: [PDF attachment]
INSURANCE_AMOUNT: $1,000,000.00
POLICY_NUMBER: WC-987654321
NOTES: Renewal reminder sent to vendor
CREATED: 12/1/2025 9:00 AM
```

---

### **Record 3: Expired**
```
COMPLIANCE_ID: C-0003
SUBCONTRACTOR: [Link to "LMN Electrical"]
DOCUMENT_TYPE: Certificate of Insurance
DOCUMENT_STATUS: Expired
DATE_RECEIVED: 1/10/2025 11:00 AM
DATE_APPROVED: 1/11/2025 4:00 PM
EXPIRATION_DATE: 1/10/2026
DAYS_UNTIL_EXPIRATION: -15
ALERT_STATUS: ⚠️ EXPIRED (15 days ago)
DOCUMENT_FILE: [PDF attachment]
INSURANCE_AMOUNT: $5,000,000.00
POLICY_NUMBER: COI-555666777
NOTES: URGENT: Request updated certificate
CREATED: 1/10/2025 11:00 AM
```

---

### **Record 4: Missing W-9**
```
COMPLIANCE_ID: C-0004
SUBCONTRACTOR: [Link to "New Vendor LLC"]
DOCUMENT_TYPE: W-9
DOCUMENT_STATUS: Missing
DATE_RECEIVED: [blank]
DATE_APPROVED: [blank]
EXPIRATION_DATE: [blank]
DAYS_UNTIL_EXPIRATION: [blank]
ALERT_STATUS: [blank]
DOCUMENT_FILE: [blank]
INSURANCE_AMOUNT: [blank]
POLICY_NUMBER: [blank]
NOTES: W-9 requested 1/20/2026 via email
CREATED: 1/20/2026 3:00 PM
```

---

## 🔗 **HOW IT CONNECTS TO OTHER TABLES**

### **Links TO:**
- **GPSS SUBCONTRACTORS** (via `SUBCONTRACTOR` field)
  - Each compliance record belongs to one subcontractor
  - You can see all docs for a specific subcontractor

### **Links FROM:**
- **GPSS SUBCONTRACTORS** should have field: `COMPLIANCE_DOCUMENTS`
  - Link back to this table
  - Shows all compliance docs for each subcontractor
  - Add field: `COMPLIANCE_READY` (Checkbox) to track if fully compliant

---

## 🔄 **TYPICAL WORKFLOW**

```
Step 1: Request Document
├─ Create record in this table
├─ SUBCONTRACTOR: Select vendor
├─ DOCUMENT_TYPE: What you need (W-9, Insurance, etc.)
├─ DOCUMENT_STATUS: "Missing"
└─ NOTES: "Requested via email [date]"

Step 2: Document Received
├─ Update record
├─ DATE_RECEIVED: Today's date
├─ DOCUMENT_STATUS: "Submitted"
├─ DOCUMENT_FILE: Upload the PDF
└─ Fill in: EXPIRATION_DATE, INSURANCE_AMOUNT, POLICY_NUMBER

Step 3: Review & Approve
├─ Review document
├─ DATE_APPROVED: Today's date
├─ DOCUMENT_STATUS: "Approved"
└─ ALERT_STATUS: Auto-calculates (✅ Current)

Step 4: Monitor Expiration
├─ Check "Alerts" view regularly
├─ When ALERT_STATUS shows "⏰ Expiring Soon":
│  ├─ Contact vendor for renewal
│  └─ Add note in NOTES field
│
└─ When renewed:
   ├─ Upload new document
   ├─ Update EXPIRATION_DATE
   └─ ALERT_STATUS auto-updates to "✅ Current"

Step 5: Handle Expired Docs
├─ When ALERT_STATUS shows "⚠️ EXPIRED":
│  ├─ DOCUMENT_STATUS: Change to "Expired"
│  ├─ URGENT: Stop sending RFQs to this vendor
│  └─ Request updated document immediately
```

---

## 🎯 **KEY BENEFITS**

✅ **Never work with non-compliant subcontractors**  
✅ **Get alerts 30 days before documents expire**  
✅ **Store all compliance docs in one place**  
✅ **Verify compliance before sending RFQs**  
✅ **Avoid contract delays from missing documents**  
✅ **Track insurance coverage amounts**  
✅ **Automated expiration tracking**

---

## ✅ **FIELD CHECKLIST (Copy/Paste Names)**

When creating table, use these exact field names:

```
COMPLIANCE_ID
SUBCONTRACTOR
DOCUMENT_TYPE
DOCUMENT_STATUS
DATE_RECEIVED
DATE_APPROVED
EXPIRATION_DATE
DAYS_UNTIL_EXPIRATION
ALERT_STATUS
DOCUMENT_FILE
INSURANCE_AMOUNT
POLICY_NUMBER
NOTES
CREATED
```

---

## 🔧 **AUTOMATION IDEAS**

### **Automation 1: Expiration Alert Email**
**Trigger:** When `ALERT_STATUS` changes to contain "Expiring Soon"  
**Action:** Send email: "⏰ [SUBCONTRACTOR] - [DOCUMENT_TYPE] expires in [DAYS_UNTIL_EXPIRATION] days"

---

### **Automation 2: Expired Document Alert**
**Trigger:** When `ALERT_STATUS` changes to contain "EXPIRED"  
**Action:** 
- Send email: "⚠️ URGENT: [SUBCONTRACTOR] - [DOCUMENT_TYPE] expired!"
- Auto-update DOCUMENT_STATUS to "Expired"

---

### **Automation 3: Document Approved Notification**
**Trigger:** When `DOCUMENT_STATUS` changes to "Approved"  
**Action:** Send email: "✅ [SUBCONTRACTOR] - [DOCUMENT_TYPE] approved"

---

### **Automation 4: Missing Document Reminder**
**Trigger:** When record created with DOCUMENT_STATUS = "Missing" for 7 days  
**Action:** Send email: "📋 Reminder: Still need [DOCUMENT_TYPE] from [SUBCONTRACTOR]"

---

## 📱 **MOBILE VIEW (Optional)**

Create a simplified mobile view:

**Name:** "Mobile: Compliance Alerts"

**Fields to show:**
- SUBCONTRACTOR
- DOCUMENT_TYPE
- EXPIRATION_DATE
- ALERT_STATUS

**Filter:** ALERT_STATUS contains "EXPIRED" OR "Expiring Soon"  
**Sort:** DAYS_UNTIL_EXPIRATION (ascending)

---

## 🚀 **AFTER CREATING THIS TABLE**

### **Add these 4 fields to GPSS SUBCONTRACTORS table:**

1. **COMPLIANCE_DOCUMENTS** (Link to another record)
   - Link to: `GPSS SUBCONTRACTOR COMPLIANCE`
   - Allow multiple: **YES** ✓
   - Shows all compliance docs for this subcontractor

2. **COMPLIANCE_STATUS** (Formula)
   - Formula: `COUNTA({COMPLIANCE_DOCUMENTS}) & " docs on file"`
   - Shows: "5 docs on file"

3. **LAST_COMPLIANCE_CHECK** (Date)
   - Manual update when you review their documents
   - No time needed

4. **COMPLIANCE_READY** (Checkbox)
   - Check this box when vendor has ALL required docs approved
   - Use this to filter "compliant vendors only" when sending RFQs

**This links everything together!** ✅

---

## 📊 **METRICS TO TRACK**

After you have records, analyze:

### **Compliance Rate by Subcontractor**
- Count: How many docs "Approved" vs "Missing" per vendor
- **Question:** Which vendors are fully compliant?

### **Expiration Management**
- Count: How many docs expire in next 30 days
- **Question:** Do you need to request renewals?

### **Document Processing Time**
- Calculate: `DATE_APPROVED` - `DATE_RECEIVED`
- **Question:** How fast do you review/approve docs?

### **Critical Gaps**
- Filter: DOCUMENT_TYPE = "W-9" OR "Insurance", STATUS = "Missing"
- **Question:** Who can't you work with right now?

---

## 🎯 **READY TO CREATE?**

### **Step 1: Create Table**
1. Go to Airtable
2. Click "+" for new table
3. Name: `GPSS SUBCONTRACTOR COMPLIANCE` (all caps with spaces)
4. Click "Create table"

### **Step 2: Add 14 Fields**
Use the grid above as reference!  
**Important:** Fields #8 and #9 are formulas - copy them exactly!

### **Step 3: Create Views**
Create the 5 recommended views listed above.

### **Step 4: Test**
Add one test record (insurance document example).

---

## ✅ **SUCCESS CRITERIA**

You'll know it's working when:
- [ ] Table created with 14 fields
- [ ] COMPLIANCE_ID shows `C-0001`, `C-0002`, etc.
- [ ] SUBCONTRACTOR links to your GPSS SUBCONTRACTORS table
- [ ] DOCUMENT_TYPE dropdown has 9 options
- [ ] DOCUMENT_STATUS dropdown has 5 options
- [ ] DAYS_UNTIL_EXPIRATION formula calculates automatically
- [ ] ALERT_STATUS formula shows emojis (⚠️, ⏰, ✅)
- [ ] Test record saves successfully

---

## 🧪 **TEST RECORD VALUES**

Add this test record to verify everything works:

**SUBCONTRACTOR:** (Select any subcontractor from your list)  
**DOCUMENT_TYPE:** `General Liability Insurance`  
**DOCUMENT_STATUS:** `Approved`  
**DATE_RECEIVED:** `1/15/2026 10:30 AM`  
**DATE_APPROVED:** `1/16/2026 2:00 PM`  
**EXPIRATION_DATE:** `7/15/2026` (no time)  
**INSURANCE_AMOUNT:** `$2,000,000`  
**POLICY_NUMBER:** `GL-TEST-123456`  
**NOTES:** `Test insurance record`

**Leave blank:**
- COMPLIANCE_ID (auto-fills)
- DAYS_UNTIL_EXPIRATION (formula auto-calculates)
- ALERT_STATUS (formula auto-calculates)
- DOCUMENT_FILE (optional)
- CREATED (auto-fills)

**After saving, check:**
- COMPLIANCE_ID = `C-0001` ✓
- DAYS_UNTIL_EXPIRATION = Shows number (171 or similar) ✓
- ALERT_STATUS = Shows `✅ Current (171 days)` ✓

---

**Total setup time: 15 minutes** ⏱️  
**Difficulty: Medium** (2 formulas to copy/paste) ✅

---

**Ready to create? Type "creating table" when you start!** 🚀
