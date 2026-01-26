# 🧪 SUBCONTRACTOR COMPLIANCE - TESTING GUIDE

**Verify the complete compliance system works correctly**

---

## 🎯 PRE-TEST SETUP

### 1. Verify Airtable Tables Exist

Go to your NEXUS Airtable base and confirm:

- [ ] `GPSS SUBCONTRACTOR COMPLIANCE` table exists (14 fields)
- [ ] `GPSS SUBCONTRACTORS` has new fields: COMPLIANCE_DOCUMENTS, COMPLIANCE_STATUS, LAST_COMPLIANCE_CHECK, COMPLIANCE_READY
- [ ] Views created in both tables

### 2. Create Test Subcontractor

In `GPSS SUBCONTRACTORS` table, create:

```
COMPANY NAME: Test Compliance LLC
SERVICE TYPE: Testing
CITY: Detroit
STATE: MI
EMAIL: test@compliance.com
PHONE: (555) 123-4567
RELATIONSHIP STATUS: Active Partner
```

**Note the record ID (starts with "rec")** - you'll need this for testing!

Example: `rec1234TEST` (use your actual record ID)

---

## 🧪 TEST SUITE

### TEST 1: Add Compliance Documents

**Objective:** Create compliance document records for test subcontractor

**Step 1: Add W-9**
```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "W-9",
    "status": "Missing",
    "notes": "Test document 1"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "record_id": "recDOC1",
  "document_type": "W-9",
  "status": "Missing"
}
```

**Step 2: Add Insurance (with expiration)**
```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "General Liability Insurance",
    "status": "Approved",
    "expiration_date": "2026-12-31",
    "insurance_amount": 1000000,
    "notes": "Test insurance"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "record_id": "recDOC2",
  "document_type": "General Liability Insurance",
  "status": "Approved"
}
```

**Step 3: Add Subcontractor Agreement**
```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "Subcontractor Agreement",
    "status": "Missing",
    "notes": "Test agreement"
  }'
```

**Verification:**
- [ ] All 3 API calls returned success
- [ ] Check Airtable: 3 records in GPSS SUBCONTRACTOR COMPLIANCE
- [ ] All 3 linked to Test Compliance LLC
- [ ] DAYS_UNTIL_EXPIRATION formula shows days for insurance record

---

### TEST 2: Get All Compliance Documents

**Objective:** Retrieve all documents for subcontractor

```bash
curl http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance
```

**Expected Response:**
```json
{
  "success": true,
  "subcontractor_id": "rec1234TEST",
  "documents_found": 3,
  "documents": [
    {
      "id": "recDOC1",
      "document_type": "W-9",
      "status": "Missing",
      "alert_status": "❌ Missing"
    },
    {
      "id": "recDOC2",
      "document_type": "General Liability Insurance",
      "status": "Approved",
      "expiration_date": "2026-12-31",
      "days_until_expiration": 343,
      "alert_status": "✅ Current",
      "insurance_amount": 1000000
    },
    {
      "id": "recDOC3",
      "document_type": "Subcontractor Agreement",
      "status": "Missing",
      "alert_status": "❌ Missing"
    }
  ]
}
```

**Verification:**
- [ ] Returns 3 documents
- [ ] Document types match what was added
- [ ] Statuses are correct
- [ ] Insurance shows expiration date and amount
- [ ] Alert statuses are correct

---

### TEST 3: Check Compliance (Should FAIL - missing docs)

**Objective:** Verify compliance check correctly identifies missing documents

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "required_documents": [
      "W-9",
      "General Liability Insurance",
      "Subcontractor Agreement"
    ]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "company_name": "Test Compliance LLC",
  "compliant": false,
  "required_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "approved_documents": ["General Liability Insurance"],
  "compliance_issues": [
    "W-9: Status = Missing",
    "Subcontractor Agreement: Status = Missing"
  ],
  "expiring_soon": [],
  "expired_documents": [],
  "compliance_percentage": 33
}
```

**Verification:**
- [ ] compliant = false (correct - 2 docs missing)
- [ ] compliance_percentage = 33 (1 out of 3 = 33%)
- [ ] compliance_issues lists the 2 missing documents
- [ ] approved_documents only includes insurance

---

### TEST 4: Update Documents to Approved

**Objective:** Approve the missing documents

**Step 1: Approve W-9**

First, get the document ID from TEST 2 response (recDOC1), then:

```bash
curl -X PUT http://localhost:5000/gpss/compliance/recDOC1 \
  -H "Content-Type: application/json" \
  -d '{
    "DOCUMENT_STATUS": "Approved",
    "DATE_RECEIVED": "2026-01-22",
    "DATE_APPROVED": "2026-01-22",
    "NOTES": "W-9 received and verified"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "document_id": "recDOC1",
  "updated_fields": ["DOCUMENT_STATUS", "DATE_RECEIVED", "DATE_APPROVED", "NOTES"]
}
```

**Step 2: Approve Subcontractor Agreement**

```bash
curl -X PUT http://localhost:5000/gpss/compliance/recDOC3 \
  -H "Content-Type: application/json" \
  -d '{
    "DOCUMENT_STATUS": "Approved",
    "DATE_RECEIVED": "2026-01-22",
    "DATE_APPROVED": "2026-01-22",
    "NOTES": "Agreement signed and received"
  }'
```

**Verification:**
- [ ] Both updates returned success
- [ ] Check Airtable: Both documents now show "Approved" status
- [ ] DATE_RECEIVED and DATE_APPROVED are set
- [ ] Alert statuses changed to "✅ Current"

---

### TEST 5: Check Compliance (Should PASS - all docs approved)

**Objective:** Verify compliance check now passes

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "required_documents": [
      "W-9",
      "General Liability Insurance",
      "Subcontractor Agreement"
    ]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "company_name": "Test Compliance LLC",
  "compliant": true,
  "required_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "approved_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "compliance_issues": [],
  "expiring_soon": [],
  "expired_documents": [],
  "compliance_percentage": 100
}
```

**Verification:**
- [ ] compliant = true ✅
- [ ] compliance_percentage = 100 ✅
- [ ] compliance_issues = [] (empty)
- [ ] All 3 documents in approved_documents

---

### TEST 6: Mark Subcontractor Compliance Ready

**Objective:** Mark subcontractor as ready to work

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/mark-ready \
  -H "Content-Type: application/json" \
  -d '{
    "ready": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "subcontractor_id": "rec1234TEST",
  "compliance_ready": true
}
```

**Verification:**
- [ ] API returns success
- [ ] Check Airtable GPSS SUBCONTRACTORS table
- [ ] Test Compliance LLC has COMPLIANCE_READY = checked ✅
- [ ] LAST_COMPLIANCE_CHECK = today's date
- [ ] Subcontractor appears in "✅ Compliance Ready" view

---

### TEST 7: Test Expiring Documents Alert (Create expiring doc)

**Objective:** Verify expiring document detection works

**Step 1: Create document expiring in 20 days**

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "Workers Compensation Insurance",
    "status": "Approved",
    "expiration_date": "2026-02-11",
    "insurance_amount": 500000,
    "notes": "Test expiring soon"
  }'
```

**Step 2: Get compliance alerts**

```bash
curl http://localhost:5000/gpss/compliance/alerts?days_threshold=30
```

**Expected Response:**
```json
{
  "success": true,
  "expired_count": 0,
  "expiring_soon_count": 1,
  "expired_documents": [],
  "expiring_soon_documents": [
    {
      "id": "recDOC4",
      "subcontractor": ["rec1234TEST"],
      "document_type": "Workers Compensation Insurance",
      "expiration_date": "2026-02-11",
      "days_until_expiration": 20,
      "alert": "EXPIRING_SOON"
    }
  ],
  "total_alerts": 1
}
```

**Verification:**
- [ ] expiring_soon_count = 1
- [ ] Document shows in expiring_soon_documents
- [ ] days_until_expiration is approximately 20
- [ ] Check Airtable: Document shows "⏰ Expiring Soon" alert status

---

### TEST 8: Test Expired Document Alert (Create expired doc)

**Objective:** Verify expired document detection works

**Step 1: Create expired document**

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "Professional Liability Insurance",
    "status": "Approved",
    "expiration_date": "2026-01-01",
    "insurance_amount": 1000000,
    "notes": "Test expired"
  }'
```

**Step 2: Get compliance alerts**

```bash
curl http://localhost:5000/gpss/compliance/alerts
```

**Expected Response:**
```json
{
  "success": true,
  "expired_count": 1,
  "expiring_soon_count": 1,
  "expired_documents": [
    {
      "id": "recDOC5",
      "subcontractor": ["rec1234TEST"],
      "document_type": "Professional Liability Insurance",
      "expiration_date": "2026-01-01",
      "days_overdue": 21,
      "alert": "EXPIRED"
    }
  ],
  "expiring_soon_documents": [...],
  "total_alerts": 2
}
```

**Verification:**
- [ ] expired_count = 1
- [ ] Document shows in expired_documents
- [ ] days_overdue is approximately 21
- [ ] Check Airtable: Document shows "⚠️ EXPIRED" alert status

---

### TEST 9: Check Compliance After Expired Doc Added

**Objective:** Verify compliance check detects expired documents

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "required_documents": [
      "W-9",
      "General Liability Insurance",
      "Subcontractor Agreement",
      "Professional Liability Insurance"
    ]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "company_name": "Test Compliance LLC",
  "compliant": false,
  "compliance_percentage": 75,
  "approved_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "compliance_issues": [
    "Professional Liability Insurance: EXPIRED"
  ],
  "expired_documents": ["Professional Liability Insurance"]
}
```

**Verification:**
- [ ] compliant = false (expired doc counts as non-compliant)
- [ ] compliance_percentage = 75 (3 out of 4)
- [ ] expired_documents includes Professional Liability Insurance
- [ ] compliance_issues lists the expired document

---

### TEST 10: Unmark Compliance Ready (Due to Expired Doc)

**Objective:** Remove compliance ready status

```bash
curl -X POST http://localhost:5000/gpss/subcontractors/rec1234TEST/compliance/mark-ready \
  -H "Content-Type: application/json" \
  -d '{
    "ready": false
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "subcontractor_id": "rec1234TEST",
  "compliance_ready": false
}
```

**Verification:**
- [ ] Check Airtable: COMPLIANCE_READY is now unchecked
- [ ] Subcontractor NO LONGER appears in "✅ Compliance Ready" view
- [ ] Appears in "⚠️ Compliance Issues" view

---

## 📊 AIRTABLE VERIFICATION CHECKLIST

After running all tests, verify in Airtable:

### In `GPSS SUBCONTRACTOR COMPLIANCE` table:

**All Documents view:**
- [ ] 5 documents exist for Test Compliance LLC
- [ ] Document types: W-9, General Liability, Subcontractor Agreement, Workers Comp, Professional Liability
- [ ] Statuses show correctly (Approved for all 5)
- [ ] Dates populated correctly

**⏰ Expiring Soon view:**
- [ ] Shows Workers Compensation Insurance
- [ ] DAYS_UNTIL_EXPIRATION shows ~20

**❌ Expired Documents view:**
- [ ] Shows Professional Liability Insurance
- [ ] DAYS_UNTIL_EXPIRATION shows negative number
- [ ] ALERT_STATUS shows "⚠️ EXPIRED"

**📋 By Subcontractor view:**
- [ ] All 5 documents grouped under Test Compliance LLC

### In `GPSS SUBCONTRACTORS` table:

**Main view:**
- [ ] Test Compliance LLC exists
- [ ] COMPLIANCE_STATUS shows "5 docs tracked"
- [ ] LAST_COMPLIANCE_CHECK shows today's date
- [ ] COMPLIANCE_READY is unchecked (we unmarked it in TEST 10)

**✅ Compliance Ready view:**
- [ ] Test Compliance LLC does NOT appear (correctly)

**⚠️ Compliance Issues view:**
- [ ] Test Compliance LLC appears (because COMPLIANCE_READY = false)

---

## 🚨 TROUBLESHOOTING

### Test fails with "Table not found"
- **Solution:** Create Airtable tables first (see SUBCONTRACTOR_COMPLIANCE_SETUP.md)

### Test fails with "Subcontractor not found"
- **Solution:** Create test subcontractor in GPSS SUBCONTRACTORS table
- **Solution:** Use correct record ID (starts with "rec")

### Formulas not calculating
- **Solution:** Verify formulas copied exactly from setup guide
- **Solution:** Check field names match exactly (case-sensitive)
- **Solution:** Ensure EXPIRATION_DATE field exists and is type "Date"

### API returns 500 error
- **Solution:** Check backend logs for Python errors
- **Solution:** Verify Airtable API key is set in environment
- **Solution:** Reload backend: `git pull && reload on PythonAnywhere`

### Documents not linking to subcontractor
- **Solution:** Verify subcontractor_id is correct
- **Solution:** Check SUBCONTRACTOR field is type "Link to another record"
- **Solution:** Ensure link points to GPSS SUBCONTRACTORS table

---

## ✅ SUCCESS CRITERIA

**All tests passed when:**
- [ ] All 10 test API calls returned success
- [ ] Airtable shows 5 documents for test subcontractor
- [ ] Compliance check correctly identifies missing/expired docs
- [ ] Compliance check passes when all docs approved
- [ ] Alert system detects expiring/expired documents
- [ ] Formula fields calculate correctly
- [ ] Views filter correctly
- [ ] Compliance ready status updates correctly

---

## 🧹 CLEANUP (After Testing)

**Option 1: Keep test data**
- Useful for demonstrations
- Can use as template for real subcontractors

**Option 2: Delete test data**
1. Go to GPSS SUBCONTRACTOR COMPLIANCE
2. Delete all 5 test documents
3. Go to GPSS SUBCONTRACTORS
4. Delete Test Compliance LLC record

---

## 📋 TEST RESULTS SUMMARY

**Run Date:** _______________  
**Tested By:** _______________

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Add compliance documents | ⬜ | |
| 2 | Get all documents | ⬜ | |
| 3 | Check compliance (fail) | ⬜ | |
| 4 | Update documents | ⬜ | |
| 5 | Check compliance (pass) | ⬜ | |
| 6 | Mark compliance ready | ⬜ | |
| 7 | Expiring document alert | ⬜ | |
| 8 | Expired document alert | ⬜ | |
| 9 | Check with expired doc | ⬜ | |
| 10 | Unmark compliance ready | ⬜ | |

**Overall Status:** ⬜ PASS  ⬜ FAIL  

**Issues Found:**


**Notes:**


---

**Testing complete! System ready for production use!** ✅
