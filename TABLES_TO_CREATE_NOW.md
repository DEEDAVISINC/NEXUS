# 📋 TABLES TO CREATE NOW
**2 tables missing from your Airtable base**

---

## 🎯 **TABLE 1: CapabilityStatements**

**Purpose:** Track every capability statement PDF/HTML you generate  
**Time to create:** 10 minutes  
**Setup guide:** `CAPABILITYSTATEMENTS_TABLE_SETUP_SIMPLE.md`

### **15 Fields:**

| # | Field Name | Type | Options/Details |
|---|------------|------|-----------------|
| 1 | `RecordID` | Formula | `RECORD_ID()` |
| 2 | `OpportunityID` | Link to another record | Link to: "Opportunities" table |
| 3 | `ClientName` | Single line text | |
| 4 | `RFQNumber` | Single line text | |
| 5 | `GeneratedDate` | Date | Include time ✓ |
| 6 | `HTMLPath` | Long text | |
| 7 | `PDFPath` | Long text | |
| 8 | `ConfigJSON` | Long text | |
| 9 | `Status` | Single select | Generated, Submitted, Accepted, Rejected, Archived |
| 10 | `Template` | Single select | default, va_medical, construction, custom |
| 11 | `SubmittedDate` | Date | Include time ✓ |
| 12 | `SubmittedBy` | Single line text | |
| 13 | `Notes` | Long text | |
| 14 | `OpportunityName` | Lookup | From OpportunityID → Name |
| 15 | `OpportunityStatus` | Lookup | From OpportunityID → Status |

### **Why you need this:**
✅ Track which capability statements you've generated  
✅ Know which ones were submitted and won  
✅ Find files later when you need them  
✅ Measure which templates work best  

### **Example record:**
```
ClientName: "CPS Energy"
RFQNumber: "7000205103"
GeneratedDate: 1/25/2026 2:30 PM
HTMLPath: "/path/to/capstat_CPS_Energy_7000205103.html"
PDFPath: "/path/to/capstat_CPS_Energy_7000205103.pdf"
Status: "Generated"
Template: "default"
```

---

## 🎯 **TABLE 2: GPSS SUBCONTRACTOR COMPLIANCE**

**Purpose:** Track W-9s, insurance certificates, NDAs, and compliance documents  
**Time to create:** 15 minutes  
**Setup guide:** `SUBCONTRACTOR_COMPLIANCE_SETUP.md`

### **14 Fields:**

| # | Field Name | Type | Options/Details |
|---|------------|------|-----------------|
| 1 | `COMPLIANCE_ID` | Autonumber | Format: C-{0000} |
| 2 | `SUBCONTRACTOR` | Link to another record | Link to: "GPSS SUBCONTRACTORS" table |
| 3 | `DOCUMENT_TYPE` | Single select | W-9, General Liability Insurance, Workers Comp, Auto Insurance, NDA, Certificate of Insurance, Business License, Bond, Other |
| 4 | `DOCUMENT_STATUS` | Single select | Missing, Submitted, Approved, Expired, Rejected |
| 5 | `DATE_RECEIVED` | Date | Include time ✓ |
| 6 | `DATE_APPROVED` | Date | Include time ✓ |
| 7 | `EXPIRATION_DATE` | Date | No time needed |
| 8 | `DAYS_UNTIL_EXPIRATION` | Formula | `IF(EXPIRATION_DATE, DATETIME_DIFF(EXPIRATION_DATE, TODAY(), 'days'), "")` |
| 9 | `ALERT_STATUS` | Formula | Shows: ⚠️ EXPIRED, ⏰ Expiring Soon, ✅ Current |
| 10 | `DOCUMENT_FILE` | Attachment | Upload PDFs here |
| 11 | `INSURANCE_AMOUNT` | Currency | $ USD |
| 12 | `POLICY_NUMBER` | Single line text | |
| 13 | `NOTES` | Long text | |
| 14 | `CREATED` | Created time | Include time ✓ |

### **Why you need this:**
✅ Track which subcontractors have current documents  
✅ Get alerts when insurance is expiring  
✅ Verify compliance before sending RFQs  
✅ Store all compliance documents in one place  
✅ Avoid contract delays from missing documents  

### **Example record:**
```
SUBCONTRACTOR: "ABC Janitorial Services"
DOCUMENT_TYPE: "General Liability Insurance"
DOCUMENT_STATUS: "Approved"
DATE_RECEIVED: 1/15/2026
DATE_APPROVED: 1/16/2026
EXPIRATION_DATE: 7/15/2026
DAYS_UNTIL_EXPIRATION: 171
ALERT_STATUS: "✅ Current (171 days)"
INSURANCE_AMOUNT: $2,000,000
POLICY_NUMBER: "GL-123456789"
```

---

## 🔗 **AFTER CREATING THESE TABLES:**

### **Add these fields to existing tables:**

#### **To GPSS OPPORTUNITIES table:**
- [ ] `CapabilityStatement` (Link to CapabilityStatements)
- [ ] `CapStatGenerated` (Checkbox)
- [ ] `CapStatDate` (Date)

#### **To GPSS SUBCONTRACTORS table:**
- [ ] `COMPLIANCE_DOCUMENTS` (Link to GPSS SUBCONTRACTOR COMPLIANCE)
- [ ] `COMPLIANCE_STATUS` (Formula: count of approved docs)
- [ ] `LAST_COMPLIANCE_CHECK` (Date)
- [ ] `COMPLIANCE_READY` (Checkbox)

This links everything together! ✅

---

## 📝 **QUICK REFERENCE:**

**Table names to create (exact spelling):**
1. `CapabilityStatements` (exact case)
2. `GPSS SUBCONTRACTOR COMPLIANCE` (all caps with space)

**Setup guides in your folder:**
- `CAPABILITYSTATEMENTS_TABLE_SETUP_SIMPLE.md` (step-by-step)
- `SUBCONTRACTOR_COMPLIANCE_SETUP.md` (step-by-step)

---

## ✅ **CHECKLIST:**

- [ ] Create CapabilityStatements table (10 min)
- [ ] Create GPSS SUBCONTRACTOR COMPLIANCE table (15 min)
- [ ] Add 3 fields to GPSS OPPORTUNITIES table (3 min)
- [ ] Add 4 fields to GPSS SUBCONTRACTORS table (5 min)

**Total time: 33 minutes to complete foundation** 🚀

---

**Ready to create these? I'll walk you through one at a time!**
