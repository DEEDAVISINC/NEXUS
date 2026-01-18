# ProposalBio™ Airtable Setup Guide
## Excel-Style Step-by-Step Instructions

**Base Location:** NEXUS Command Center (Your Existing Airtable Base)  
**Total Setup Time:** 25-30 minutes  
**Tables to Modify:** 1 (GPSS Proposals)  
**Tables to Create:** 2 (ProposalBio Scores, ProposalBio Learning)

---

## 📋 STEP 1: Add Fields to "GPSS Proposals" Table (15 minutes)

**Instructions:** Open your **NEXUS Command Center** base → Navigate to **GPSS Proposals** table → Click "+" to add each field below

### Fields to Add:

| # | Field Name | Field Type | Configuration | Notes |
|---|------------|------------|---------------|-------|
| 1 | ProposalBio Composite Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)**<br>• Allow negative: **No** | Stores overall quality score (0-100) |
| 2 | ProposalBio Status | **Single select** | • Options (add these):<br>&nbsp;&nbsp;- `APPROVED` (green)<br>&nbsp;&nbsp;- `REVISE` (yellow)<br>&nbsp;&nbsp;- `REDRAFT` (orange)<br>&nbsp;&nbsp;- `REJECT` (red) | Overall quality status |
| 3 | ProposalBio Last Analyzed | **Date** | • Include time: **✓ Yes**<br>• Time zone: **GMT**<br>• Date format: **US (M/D/YYYY)**<br>• Time format: **12 hour** | Timestamp of last analysis |
| 4 | ProposalBio Gate | **Single select** | • Options (add these):<br>&nbsp;&nbsp;- `LOCKED` (red)<br>&nbsp;&nbsp;- `UNLOCKED` (green) | Submission quality gate |
| 5 | ProposalBio Biohack Scores JSON | **Long text** | • Enable rich text: **No**<br>• Enable markdown: **No** | Stores all 10 biohack scores |
| 6 | ProposalBio Critical Issues JSON | **Long text** | • Enable rich text: **No**<br>• Enable markdown: **No** | Stores issues (score < 6) |
| 7 | ProposalBio Priority Improvements JSON | **Long text** | • Enable rich text: **No**<br>• Enable markdown: **No** | Stores improvement suggestions |
| 8 | ProposalBio Revision Count | **Number** | • Precision: **Integer**<br>• Default value: **0**<br>• Allow negative: **No** | Tracks analysis revisions |
| 9 | ProposalBio Approved By | **Single line text** | • No special config | Name of person who approved |
| 10 | ProposalBio Approved Date | **Date** | • Include time: **✓ Yes**<br>• Time zone: **GMT** | When approved for submission |

### Optional Fields (If Not Already Present):

| # | Field Name | Field Type | Configuration | Notes |
|---|------------|------------|---------------|-------|
| 11 | Agency Type | **Single select** | • Options:<br>&nbsp;&nbsp;- `Federal`<br>&nbsp;&nbsp;- `State`<br>&nbsp;&nbsp;- `Local`<br>&nbsp;&nbsp;- `Cooperative` | Type of government agency |
| 12 | Region | **Single select** | • Options:<br>&nbsp;&nbsp;- `Northeast`<br>&nbsp;&nbsp;- `Mid_Atlantic`<br>&nbsp;&nbsp;- `Southeast`<br>&nbsp;&nbsp;- `Midwest`<br>&nbsp;&nbsp;- `Southwest`<br>&nbsp;&nbsp;- `West_Coast` | Geographic region |
| 13 | RFP Text | **Long text** | • Enable rich text: **No** | Full RFP text for analysis |

**✅ Checkpoint:** You should now see 10-13 new fields in your GPSS Proposals table

---

## 📋 STEP 2: Create "GPSS ProposalBio Scores" Table (10 minutes)

**Instructions:** In your **NEXUS Command Center** base → Click "Add or import" → "Create empty table" → Name it **"GPSS ProposalBio Scores"**

### Table Configuration:

**Rename the default first field to:** `Score ID` (Autonumber)

### Fields to Add:

| # | Field Name | Field Type | Configuration | Purpose |
|---|------------|------------|---------------|---------|
| 1 | Score ID | **Autonumber** | (Default first field - just rename) | Primary key |
| 2 | Proposal | **Link to another record** | • Link to table: **GPSS Proposals**<br>• Allow linking to multiple records: **Yes**<br>• In GPSS Proposals, create field: `ProposalBio Score Records` | Links back to proposal |
| 3 | Revision | **Number** | • Precision: **Integer**<br>• Format: **Integer**<br>• Allow negative: **No** | Which analysis revision (1, 2, 3...) |
| 4 | Biohack Number | **Number** | • Precision: **Integer**<br>• Format: **Integer**<br>• Range: **1-10** | Which biohack (1-10) |
| 5 | Biohack Name | **Single line text** | • No special config | Name (e.g., "Mirror Neuron") |
| 6 | Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)**<br>• Range: **0-10** | Score for this biohack |
| 7 | PassFail | **Single select** | • Options:<br>&nbsp;&nbsp;- `Pass` (green)<br>&nbsp;&nbsp;- `Fail` (red) | Pass = score ≥ 6 |
| 8 | Details JSON | **Long text** | • Enable rich text: **No** | (Optional - for future expansion) |
| 9 | Recommendations | **Long text** | • Enable rich text: **No** | (Optional - specific improvement tips) |
| 10 | Analyzed Date | **Date** | • Include time: **✓ Yes**<br>• Time zone: **GMT** | When this score was calculated |

### Views to Create:

| View Name | Type | Configuration |
|-----------|------|---------------|
| **All Scores** | Grid view | • Sort: Analyzed Date (newest first)<br>• Group: None |
| **Failed Biohacks** | Grid view | • Filter: PassFail = `Fail`<br>• Group by: Biohack Name<br>• Sort: Score (lowest first) |
| **By Proposal** | Grid view | • Group by: Proposal<br>• Sort: Revision (newest first) |
| **Recent Analysis** | Grid view | • Filter: Analyzed Date is within `last 7 days`<br>• Sort: Analyzed Date (newest first) |

**✅ Checkpoint:** Create a test record to verify the Proposal link works

---

## 📋 STEP 3: Create "GPSS ProposalBio Learning" Table (10 minutes)

**Instructions:** In your **NEXUS Command Center** base → Click "Add or import" → "Create empty table" → Name it **"GPSS ProposalBio Learning"**

### Table Configuration:

**Rename the default first field to:** `Learning ID` (Autonumber)

### Fields to Add:

| # | Field Name | Field Type | Configuration | Purpose |
|---|------------|------------|---------------|---------|
| 1 | Learning ID | **Autonumber** | (Default first field - just rename) | Primary key |
| 2 | Proposal | **Link to another record** | • Link to table: **GPSS Proposals**<br>• Allow linking to multiple records: **No**<br>• In GPSS Proposals, create field: `Outcome Record` | Links to proposal |
| 3 | Outcome | **Single select** | • Options:<br>&nbsp;&nbsp;- `Won` (green)<br>&nbsp;&nbsp;- `Lost` (red)<br>&nbsp;&nbsp;- `No Decision` (gray) | Win/loss result |
| 4 | Win Value | **Currency** | • Currency: **USD ($)**<br>• Precision: **2 decimals** | Contract value (if won) |
| 5 | Agency Type | **Single select** | • Options:<br>&nbsp;&nbsp;- `Federal`<br>&nbsp;&nbsp;- `State`<br>&nbsp;&nbsp;- `Local`<br>&nbsp;&nbsp;- `Cooperative` | Agency type for correlation |
| 6 | Region | **Single select** | • Options:<br>&nbsp;&nbsp;- `Northeast`<br>&nbsp;&nbsp;- `Mid_Atlantic`<br>&nbsp;&nbsp;- `Southeast`<br>&nbsp;&nbsp;- `Midwest`<br>&nbsp;&nbsp;- `Southwest`<br>&nbsp;&nbsp;- `West_Coast` | Region for correlation |
| 7 | Composite Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Overall score at time of submission |
| 8 | Biohack 1 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Mirror Neuron score |
| 9 | Biohack 2 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Cognitive Ease score |
| 10 | Biohack 3 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Story Arc score |
| 11 | Biohack 4 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Reciprocity score |
| 12 | Biohack 5 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Yes Stacking score |
| 13 | Biohack 6 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Familiarity score |
| 14 | Biohack 7 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Name Recognition score |
| 15 | Biohack 8 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Sensory Language score |
| 16 | Biohack 9 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Rhythm score |
| 17 | Biohack 10 Score | **Number** | • Precision: **2 decimals**<br>• Format: **Decimal (0.00)** | Eye Tracking score |
| 18 | Recorded Date | **Date** | • Include time: **✓ Yes**<br>• Time zone: **GMT** | When outcome was recorded |

### Views to Create:

| View Name | Type | Configuration |
|-----------|------|---------------|
| **All Outcomes** | Grid view | • Sort: Recorded Date (newest first) |
| **Won Proposals** | Grid view | • Filter: Outcome = `Won`<br>• Sort: Win Value (highest first) |
| **Lost Proposals** | Grid view | • Filter: Outcome = `Lost`<br>• Sort: Composite Score (lowest first) |
| **By Agency Type** | Grid view | • Group by: Agency Type<br>• Summary: Count, Average Composite Score |
| **By Region** | Grid view | • Group by: Region<br>• Summary: Count, Average Composite Score |
| **High Score Winners** | Grid view | • Filter: Outcome = `Won` AND Composite Score ≥ 90<br>• Sort: Composite Score (highest first) |

**✅ Checkpoint:** Verify all 18 fields are created with correct types

---

## 📋 STEP 4: Verification Checklist

### Before Testing, Verify:

| Item | Check | Status |
|------|-------|--------|
| 1. GPSS Proposals table has 10+ new ProposalBio fields | [ ] | |
| 2. "ProposalBio Gate" has LOCKED/UNLOCKED options (with colors) | [ ] | |
| 3. "ProposalBio Status" has all 4 options (APPROVED, REVISE, REDRAFT, REJECT) | [ ] | |
| 4. "GPSS ProposalBio Scores" table exists with 10 fields | [ ] | |
| 5. "Proposal" link field works in ProposalBio Scores table | [ ] | |
| 6. "GPSS ProposalBio Learning" table exists with 18 fields | [ ] | |
| 7. All Number fields are set to 2 decimal precision | [ ] | |
| 8. All Date fields include time and use GMT | [ ] | |
| 9. All Single Select fields have options configured | [ ] | |
| 10. All Long Text fields have rich text disabled | [ ] | |

**✅ If all boxes checked, you're ready to test!**

---

## 📋 STEP 5: Quick Test

### Test in This Order:

**5.1 Create a Test Proposal**
1. Go to **GPSS Proposals** table
2. Create a new record:
   - Proposal Name: `TEST - ProposalBio Setup`
   - Executive Summary: `This is a test proposal to verify ProposalBio integration.`
   - Technical Approach: `We will deliver quality services.`
   - Agency Type: `Federal`
   - Region: `Mid_Atlantic`
   - Status: `Draft`
3. Note the record ID (starts with `rec...`)

**5.2 Test Backend API (Terminal)**
```bash
# Navigate to backend folder
cd "/Users/deedavis/NEXUS BACKEND"

# Test the analyze endpoint
curl -X POST http://localhost:5000/gpss/proposalbio/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "recXXXXXXXXXXXXXX",
    "metadata": {
      "agency_type": "Federal",
      "region": "Mid_Atlantic"
    }
  }'
```
*(Replace `recXXXXXXXXXXXXXX` with your test proposal's actual record ID)*

**Expected Response:**
```json
{
  "status": "success",
  "proposal_id": "recXXXXXXXXXXXXXX",
  "composite_score": 65.5,
  "submission_gate": "LOCKED",
  "overall_status": "REDRAFT",
  "biohack_scores": [...],
  "critical_issues": [...],
  "priority_improvements": [...]
}
```

**5.3 Verify Airtable Updates**
1. Refresh **GPSS Proposals** table
2. Find your test proposal
3. Verify these fields are now populated:
   - ✅ ProposalBio Composite Score (should show a number like 65.50)
   - ✅ ProposalBio Status (should show REDRAFT, REVISE, or APPROVED)
   - ✅ ProposalBio Gate (should show LOCKED or UNLOCKED)
   - ✅ ProposalBio Last Analyzed (should show current date/time)

**5.4 Check ProposalBio Scores Table**
1. Open **GPSS ProposalBio Scores** table
2. You should see 10 new records (one for each biohack)
3. Each should be linked to your test proposal
4. Verify scores are between 0-10
5. Verify PassFail shows "Pass" or "Fail"

**✅ If all tests pass, your ProposalBio™ system is ready!**

---

## 📋 STEP 6: Optional Enhancements

### Add Color Coding (Recommended)

**In GPSS Proposals table:**

1. Click on **ProposalBio Gate** field header → Click "Customize field type"
2. Set colors:
   - `LOCKED` → Red
   - `UNLOCKED` → Green

3. Click on **ProposalBio Status** field header → Click "Customize field type"
4. Set colors:
   - `APPROVED` → Green
   - `REVISE` → Yellow
   - `REDRAFT` → Orange
   - `REJECT` → Red

**In GPSS ProposalBio Scores table:**

1. Click on **PassFail** field header → Click "Customize field type"
2. Set colors:
   - `Pass` → Green
   - `Fail` → Red

**In GPSS ProposalBio Learning table:**

1. Click on **Outcome** field header → Click "Customize field type"
2. Set colors:
   - `Won` → Green
   - `Lost` → Red
   - `No Decision` → Gray

### Add Views (Optional but Helpful)

**In GPSS Proposals table, add a ProposalBio view:**
- Name: "ProposalBio Dashboard"
- Show fields: Proposal Name, Agency, ProposalBio Composite Score, ProposalBio Status, ProposalBio Gate, ProposalBio Last Analyzed
- Filter: ProposalBio Last Analyzed is not empty
- Sort: ProposalBio Last Analyzed (newest first)
- Group by: ProposalBio Status

---

## 🎯 Regional Definitions (For Reference)

When setting Region field, use these definitions:

| Region | States Included | Writing Style |
|--------|----------------|---------------|
| **Northeast** | NY, NJ, CT, MA, RI, NH, VT, ME, PA | Direct, fast-paced, data-heavy |
| **Mid_Atlantic** | DC, MD, VA, WV, DE | Policy-focused, formal (federal influence) |
| **Southeast** | FL, GA, SC, NC, TN, AL, MS, LA, AR, KY | Relationship-oriented, warm |
| **Midwest** | OH, MI, IN, IL, WI, MN, IA, MO, ND, SD, NE, KS | Practical, straightforward, humble |
| **Southwest** | TX, OK, NM, AZ | Confident, independent, results-oriented |
| **West_Coast** | CA, WA, OR, NV, HI, AK | Collaborative, innovation-focused |

---

## 📊 The 10 Biohacks (Quick Reference)

| # | Biohack Name | What It Measures | Target Score |
|---|--------------|------------------|--------------|
| 1 | Mirror Neuron | Regional & agency tone matching | ≥ 6.0 |
| 2 | Cognitive Ease | Reading level, simplicity, white space | ≥ 6.0 |
| 3 | Story Arc | Challenge-solution-result narratives | ≥ 6.0 |
| 4 | Reciprocity | Give-first value (insights, checklists) | ≥ 6.0 |
| 5 | Yes Stacking | Affirming statements before asks | ≥ 6.0 |
| 6 | Familiarity | RFP language mirroring | ≥ 6.0 |
| 7 | Name Recognition | Agency name frequency & placement | ≥ 6.0 |
| 8 | Sensory Language | Concrete vs vague terms | ≥ 6.0 |
| 9 | Rhythm | Sentence variety & cadence | ≥ 6.0 |
| 10 | Eye Tracking | Visual hierarchy, headings, white space | ≥ 6.0 |

**Composite Score Target:** 75+ to unlock submission gate

---

## 🚨 Troubleshooting

### Common Issues:

| Issue | Solution |
|-------|----------|
| **"Proposal not found" error** | Verify you're using the Airtable record ID (starts with "rec...") |
| **Scores not saving to Airtable** | Check your `.env` file has correct `AIRTABLE_BASE_ID` and `AIRTABLE_API_KEY` |
| **Link fields not working** | When creating link field, make sure to select the correct table to link to |
| **JSON fields show weird formatting** | Make sure "Enable rich text" is OFF for all JSON fields |
| **Date fields not showing time** | Edit field → Make sure "Include a time field" is checked |
| **Backend API returns 500 error** | Check backend logs for missing fields or incorrect field names (case-sensitive!) |

---

## ✅ Setup Complete Checklist

- [ ] Added 10 fields to GPSS Proposals table
- [ ] Created GPSS ProposalBio Scores table (10 fields)
- [ ] Created GPSS ProposalBio Learning table (18 fields)
- [ ] Configured all Single Select options
- [ ] Set all Number fields to 2 decimals
- [ ] Set all Date fields to include time + GMT
- [ ] Disabled rich text on Long Text fields
- [ ] Added color coding to status fields
- [ ] Created recommended views
- [ ] Tested with a sample proposal
- [ ] Verified scores appear in Airtable
- [ ] Checked ProposalBio Scores table populated

**✅ Total Setup Time: 25-35 minutes**

---

## 📞 Next Steps After Setup

1. **Restart Backend** (if running): `python api_server.py`
2. **Test Frontend**: Navigate to GPSS → Generate a proposal → See ProposalBio panel
3. **Review Scores**: Check what scores your proposals get
4. **Make Improvements**: Use priority improvements list to enhance proposals
5. **Record Outcomes**: After proposals win/lose, record outcomes for learning

---

**🎉 ProposalBio™ Airtable Setup Complete!**

**Questions?** Refer to `PROPOSALBIO_README.md` for full documentation.

**Last Updated:** January 15, 2026
