# 🚀 SUBCONTRACTOR COMPLIANCE - QUICK START GUIDE

**Get compliance tracking running in 20 minutes**

---

## ⚡ SETUP (One Time - 15 Minutes)

### Step 1: Create Airtable Tables (10 min)

Follow the detailed guide: `SUBCONTRACTOR_COMPLIANCE_SETUP.md`

**Quick Summary:**
1. Create table: `GPSS SUBCONTRACTOR COMPLIANCE` (14 fields)
2. Update table: `GPSS SUBCONTRACTORS` (add 4 new fields)
3. Create 8 views across both tables
4. Add test data to verify formulas work

### Step 2: Deploy Backend (5 min)

```bash
cd ~/NEXUS\ BACKEND
git add .
git commit -m "Add subcontractor compliance document tracking system"
git push origin main

# On PythonAnywhere:
# 1. Go to Web tab
# 2. Click "Reload deedavis.pythonanywhere.com"
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Check Compliance Before Sending RFQ

**Scenario:** You want to send an RFQ to a subcontractor, but first check if they're compliant.

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123ABC/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "required_documents": [
      "W-9",
      "General Liability Insurance",
      "Subcontractor Agreement"
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "company_name": "ABC Services Inc",
  "compliant": false,
  "required_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "approved_documents": ["W-9"],
  "compliance_issues": [
    "General Liability Insurance: Status = Expired",
    "Missing: Subcontractor Agreement"
  ],
  "expiring_soon": [],
  "expired_documents": ["General Liability Insurance"],
  "compliance_percentage": 33
}
```

**Action:** Don't send RFQ yet. Request missing/expired documents first.

---

### Example 2: Get All Compliance Documents for a Subcontractor

```bash
curl https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123ABC/compliance
```

**Response:**
```json
{
  "success": true,
  "subcontractor_id": "rec123ABC",
  "documents_found": 3,
  "documents": [
    {
      "id": "recDOC001",
      "document_type": "W-9",
      "status": "Approved",
      "date_received": "2025-12-15",
      "date_approved": "2025-12-15",
      "expiration_date": "",
      "days_until_expiration": "No Expiration",
      "alert_status": "✅ Current"
    },
    {
      "id": "recDOC002",
      "document_type": "General Liability Insurance",
      "status": "Approved",
      "date_received": "2025-06-01",
      "date_approved": "2025-06-01",
      "expiration_date": "2026-01-15",
      "days_until_expiration": "-7",
      "alert_status": "⚠️ EXPIRED",
      "insurance_amount": 1000000,
      "policy_number": "GL-789456"
    },
    {
      "id": "recDOC003",
      "document_type": "Subcontractor Agreement",
      "status": "Missing",
      "alert_status": "❌ Missing"
    }
  ]
}
```

---

### Example 3: Add New Compliance Document

**Scenario:** New subcontractor added, create placeholder records for required docs.

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123ABC/compliance/add \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "W-9",
    "status": "Missing",
    "notes": "Requested via email on 2026-01-22"
  }'
```

**Response:**
```json
{
  "success": true,
  "record_id": "recNEWDOC123",
  "document_type": "W-9",
  "status": "Missing"
}
```

---

### Example 4: Update Document When Received

**Scenario:** Subcontractor sends their insurance certificate.

```bash
curl -X PUT https://deedavis.pythonanywhere.com/gpss/compliance/recDOC002 \
  -H "Content-Type: application/json" \
  -d '{
    "DOCUMENT_STATUS": "Approved",
    "DATE_RECEIVED": "2026-01-22",
    "DATE_APPROVED": "2026-01-22",
    "EXPIRATION_DATE": "2027-01-22",
    "INSURANCE_AMOUNT": 1000000,
    "POLICY_NUMBER": "GL-123456-2027",
    "NOTES": "Certificate received via email, verified coverage amounts"
  }'
```

**Response:**
```json
{
  "success": true,
  "document_id": "recDOC002",
  "updated_fields": ["DOCUMENT_STATUS", "DATE_RECEIVED", "DATE_APPROVED", "EXPIRATION_DATE", "INSURANCE_AMOUNT", "POLICY_NUMBER", "NOTES"]
}
```

---

### Example 5: Get All Expiring/Expired Documents

**Scenario:** Monday morning - check what needs attention this week.

```bash
curl https://deedavis.pythonanywhere.com/gpss/compliance/alerts?days_threshold=30
```

**Response:**
```json
{
  "success": true,
  "expired_count": 2,
  "expiring_soon_count": 3,
  "expired_documents": [
    {
      "id": "recDOC002",
      "subcontractor": ["rec123ABC"],
      "document_type": "General Liability Insurance",
      "expiration_date": "2026-01-15",
      "days_overdue": 7,
      "alert": "EXPIRED"
    },
    {
      "id": "recDOC008",
      "subcontractor": ["rec456DEF"],
      "document_type": "Workers Compensation Insurance",
      "expiration_date": "2026-01-10",
      "days_overdue": 12,
      "alert": "EXPIRED"
    }
  ],
  "expiring_soon_documents": [
    {
      "id": "recDOC010",
      "subcontractor": ["rec789GHI"],
      "document_type": "Professional Liability Insurance",
      "expiration_date": "2026-02-15",
      "days_until_expiration": 24,
      "alert": "EXPIRING_SOON"
    }
  ],
  "total_alerts": 5
}
```

**Action:** Send renewal requests to affected subcontractors.

---

### Example 6: Mark Subcontractor as Compliance Ready

**Scenario:** All documents approved, mark them ready to work.

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123ABC/compliance/mark-ready \
  -H "Content-Type: application/json" \
  -d '{
    "ready": true
  }'
```

**Response:**
```json
{
  "success": true,
  "subcontractor_id": "rec123ABC",
  "compliance_ready": true
}
```

Now this subcontractor appears in the "✅ Compliance Ready" view in Airtable!

---

## 🔄 COMPLETE WORKFLOW: NEW SUBCONTRACTOR

### Scenario: You just found a new subcontractor via Google search

**Step 1: Subcontractor is added to GPSS SUBCONTRACTORS**
```
(Already done by /gpss/subcontractors/find endpoint)
Record ID: rec123NEW
Company: XYZ Contractors LLC
```

**Step 2: Create compliance document records**
```bash
# W-9
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123NEW/compliance/add \
  -H "Content-Type: application/json" \
  -d '{"document_type": "W-9", "status": "Missing"}'

# Insurance
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123NEW/compliance/add \
  -H "Content-Type: application/json" \
  -d '{"document_type": "General Liability Insurance", "status": "Missing"}'

# Agreement
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123NEW/compliance/add \
  -H "Content-Type: application/json" \
  -d '{"document_type": "Subcontractor Agreement", "status": "Missing"}'
```

**Step 3: Email subcontractor requesting documents**
```
To: contact@xyzcontractors.com
Subject: Document Request - Partnership Opportunity

Hi XYZ Contractors,

We're interested in partnering with you on upcoming government contracts 
in your area. To proceed, we need the following documents:

1. W-9 Form
2. Certificate of Insurance (General Liability, $1M minimum)
3. Signed Subcontractor Agreement (attached)

Please send these at your earliest convenience.

Best regards,
Dee Davis Inc
```

**Step 4: They respond with documents**
```
(Receive email with attachments)
```

**Step 5: Upload and approve documents**

Go to Airtable:
1. Open `GPSS SUBCONTRACTOR COMPLIANCE` table
2. Find the 3 records for XYZ Contractors
3. For each document:
   - Change STATUS to "Approved"
   - Upload PDF to DOCUMENT_FILE field
   - Set DATE_RECEIVED and DATE_APPROVED to today
   - For insurance: Set EXPIRATION_DATE, INSURANCE_AMOUNT, POLICY_NUMBER

**Step 6: Mark compliance ready**
```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123NEW/compliance/mark-ready \
  -H "Content-Type: application/json" \
  -d '{"ready": true}'
```

**Step 7: Verify compliance**
```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/subcontractors/rec123NEW/compliance/check
```

**Result:**
```json
{
  "success": true,
  "company_name": "XYZ Contractors LLC",
  "compliant": true,
  "compliance_percentage": 100,
  "approved_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"],
  "compliance_issues": []
}
```

**Step 8: Subcontractor is now ready to receive RFQs!** ✅

---

## 📋 WEEKLY COMPLIANCE ROUTINE

### Every Monday Morning (10 minutes):

**1. Check for alerts**
```bash
curl https://deedavis.pythonanywhere.com/gpss/compliance/alerts
```

**2. Review expiring documents (30 days)**
- Send renewal requests to subcontractors
- Set calendar reminders for follow-up

**3. Review expired documents**
- Send urgent renewal requests
- If no response in 48 hours: Uncheck COMPLIANCE_READY

**4. Follow up on missing documents**
- Go to Airtable: "🔴 Missing Documents" view
- Send reminder emails to subcontractors

**5. Update compliance status**
- As documents arrive, update status to "Approved"
- Mark subcontractors as compliance ready when all docs complete

---

## 🎯 INTEGRATION WITH RFQ WORKFLOW

### Modified RFQ Workflow (with compliance check):

```python
# Before sending RFQs (in your frontend or script)

# Step 1: Find subcontractors
subcontractors = find_subcontractors(service_type, location)

# Step 2: Check compliance for each
compliant_subs = []
non_compliant_subs = []

for sub in subcontractors:
    compliance = check_compliance(sub['id'])
    
    if compliance['compliant']:
        compliant_subs.append(sub)
    else:
        non_compliant_subs.append({
            'subcontractor': sub,
            'issues': compliance['compliance_issues']
        })

# Step 3: Send RFQs only to compliant subs
if compliant_subs:
    send_bulk_rfqs(opportunity_id, compliant_subs)
    print(f"✅ Sent RFQs to {len(compliant_subs)} compliant subcontractors")

# Step 4: Handle non-compliant subs
if non_compliant_subs:
    print(f"\n⚠️ {len(non_compliant_subs)} subcontractors have compliance issues:")
    for item in non_compliant_subs:
        print(f"  • {item['subcontractor']['name']}: {', '.join(item['issues'])}")
    print("\nOptions:")
    print("1. Request missing documents before sending RFQs")
    print("2. Send RFQs with compliance requirements included")
    print("3. Skip these subcontractors for this opportunity")
```

---

## 🚨 TROUBLESHOOTING

### "Document not found" error
- Check that GPSS SUBCONTRACTOR COMPLIANCE table exists
- Verify document_id is correct (starts with "rec")
- Ensure record exists in Airtable

### "Subcontractor not found" error
- Check that subcontractor_id is correct
- Verify subcontractor exists in GPSS SUBCONTRACTORS table
- Check Airtable API key permissions

### Formulas not working in Airtable
- Verify formulas copied exactly as written in setup guide
- Check field names match exactly (case-sensitive)
- DAYS_UNTIL_EXPIRATION requires EXPIRATION_DATE field to exist

### Compliance check always returns "non-compliant"
- Verify DOCUMENT_STATUS = "Approved" (exact spelling, case-sensitive)
- Check that documents are linked to correct subcontractor
- Ensure required document types match exactly (case-sensitive)

---

## 📞 QUICK REFERENCE

### API Endpoints:

```
POST /gpss/subcontractors/{id}/compliance/check
GET  /gpss/subcontractors/{id}/compliance
POST /gpss/subcontractors/{id}/compliance/add
PUT  /gpss/compliance/{doc_id}
GET  /gpss/compliance/alerts
POST /gpss/subcontractors/{id}/compliance/mark-ready
```

### Required Documents (Minimum):
- W-9 Form
- General Liability Insurance ($1M)
- Subcontractor Agreement

### Document Statuses:
- Missing (red) - Not received yet
- Submitted (yellow) - Received, needs review
- Under Review (orange) - Being verified
- Approved (green) - Verified and current
- Expired (red) - Past expiration date
- Rejected (red) - Did not meet requirements

### Alert Thresholds:
- ⚠️ EXPIRED: Expiration date passed
- ⏰ Expiring Soon: 30 days or less until expiration
- ✅ Current: Approved and >30 days until expiration

---

## ✅ SUCCESS CHECKLIST

### Setup Complete:
- [ ] Airtable tables created and verified
- [ ] Backend deployed to PythonAnywhere
- [ ] Test API calls successful
- [ ] Views created in Airtable
- [ ] Formulas working correctly

### Operational:
- [ ] Required documents identified
- [ ] Email templates created
- [ ] Weekly compliance check scheduled
- [ ] Team trained on document verification
- [ ] Compliance integrated into RFQ workflow

### First Subcontractor:
- [ ] Compliance records created
- [ ] Documents requested
- [ ] Documents received and uploaded
- [ ] Documents approved
- [ ] Subcontractor marked compliance ready
- [ ] RFQ sent successfully

---

**You now have enterprise-grade compliance tracking!** 🔒

**Next Steps:**
1. Create the Airtable tables (15 min)
2. Test with one subcontractor
3. Integrate into your RFQ workflow
4. Scale to all subcontractors

**For detailed setup:** See `SUBCONTRACTOR_COMPLIANCE_SETUP.md`  
**For backend details:** See updated `nexus_backend.py` and `api_server.py`
