# AIRTABLE SETUP FOR AI RECOMMENDATION SYSTEM
## Quick Setup Guide

**Purpose:** Create the necessary Airtable tables for the AI Recommendation & Approval System  
**Time Required:** 10-15 minutes  
**Status:** Follow these exact steps

---

## 📋 TABLE 1: AI RECOMMENDATIONS (Required)

This table tracks all AI suggestions and your decisions.

### **Create Table:**
1. Go to your Airtable base
2. Click "Add or import" → "Create empty table"
3. Name it: **AI RECOMMENDATIONS** (exactly, all caps)

### **Add These Fields:**

| Field Name | Field Type | Options/Settings |
|------------|-----------|------------------|
| `OPPORTUNITY` | Link to another record | Link to: GPSS OPPORTUNITIES |
| `TYPE` | Single select | Options: "Capability Gap Analysis", "Subcontractor Recommendation", "Supplier Recommendation", "Compliance Check" |
| `RECOMMENDATION` | Long text | Plain text |
| `CONFIDENCE` | Number | Integer, Min: 0, Max: 100 |
| `REASONING` | Long text | Plain text |
| `STATUS` | Single select | Options: "Pending Approval", "Approved", "Denied", "Modified" |
| `USER_DECISION` | Single select | Options: "APPROVED", "DENIED", "MODIFIED" |
| `USER_NOTES` | Long text | Plain text |
| `SELECTED_OPTION` | Single line text | - |
| `CREATED` | Date | Include time |
| `DECIDED_AT` | Date | Include time |

### **Field Order (Recommended):**
1. OPPORTUNITY (link)
2. TYPE
3. RECOMMENDATION
4. CONFIDENCE
5. REASONING
6. STATUS
7. USER_DECISION
8. USER_NOTES
9. SELECTED_OPTION
10. CREATED
11. DECIDED_AT

---

## 📋 TABLE 2: COMPANY CAPABILITIES (Optional but Recommended)

This table stores your company's skills and capabilities for better AI analysis.

### **Create Table:**
1. Click "Add or import" → "Create empty table"
2. Name it: **COMPANY CAPABILITIES** (exactly, all caps)

### **Add These Fields:**

| Field Name | Field Type | Options/Settings |
|------------|-----------|------------------|
| `CAPABILITY_NAME` | Single line text | - |
| `SKILL_LEVEL` | Single select | Options: "Expert", "Intermediate", "Beginner", "None" |
| `CAPACITY` | Single select | Options: "High", "Medium", "Low" |
| `HOURLY_RATE` | Currency | USD, Precision: 2 decimals |
| `TEAM_SIZE` | Number | Integer |
| `CERTIFICATIONS` | Long text | Plain text |
| `NOTES` | Long text | Plain text |

### **Populate with Your Capabilities:**

Add records like:

| CAPABILITY_NAME | SKILL_LEVEL | CAPACITY | HOURLY_RATE |
|----------------|------------|----------|-------------|
| Project Management | Expert | High | $150 |
| Government Contracting | Expert | High | $150 |
| Proposal Writing | Expert | High | $125 |
| Product Sourcing | Expert | High | $100 |
| IT Support | Intermediate | Medium | $100 |
| Cybersecurity | Beginner | Low | $0 |
| Software Development | None | Low | $0 |

**Note:** Setting "None" for capabilities you DON'T have helps AI identify gaps!

---

## 📋 TABLE 3: AI LEARNING (Optional - Advanced)

This table tracks patterns for the learning system.

### **Create Table:**
1. Click "Add or import" → "Create empty table"
2. Name it: **AI LEARNING** (exactly, all caps)

### **Add These Fields:**

| Field Name | Field Type | Options/Settings |
|------------|-----------|------------------|
| `RECOMMENDATION_ID` | Single line text | - |
| `DECISION` | Single select | Options: "APPROVED", "DENIED", "MODIFIED" |
| `TYPE` | Single line text | - |
| `AI_CONFIDENCE` | Number | Integer, Min: 0, Max: 100 |
| `TIMESTAMP` | Date | Include time |
| `NOTES` | Long text | Plain text |

**Note:** This table is auto-populated by the system. You don't need to add data manually.

---

## 📋 VERIFY EXISTING TABLES

Make sure these tables exist (they should already):

### **GPSS SUBCONTRACTORS**
Required for subcontractor recommendations.

**Key fields needed:**
- `COMPANY_NAME`
- `CAPABILITIES`
- `PAST_PERFORMANCE`
- `RATING` (Number 0-5)
- `LOCATION`
- `CONTACT_EMAIL`
- `STATUS` (Active, Available, Inactive)
- `CERTIFICATIONS`

### **GPSS SUPPLIERS**
Required for supplier recommendations.

**Key fields needed:**
- `COMPANY_NAME`
- `PRODUCTS`
- `CATEGORY`
- `RATING` (Number 0-5)
- `PAYMENT_TERMS`
- `GSA_SCHEDULE`
- `CONTACT_EMAIL`

### **GPSS OPPORTUNITIES**
Already exists - used to link recommendations.

---

## ✅ SETUP CHECKLIST

### **Step 1: Create Tables**
- [ ] Create AI RECOMMENDATIONS table with all 11 fields
- [ ] Create COMPANY CAPABILITIES table with all 7 fields
- [ ] Create AI LEARNING table with all 6 fields (optional)

### **Step 2: Populate Data**
- [ ] Add your company's capabilities to COMPANY CAPABILITIES
- [ ] Mark what you CAN do (Expert/Intermediate)
- [ ] Mark what you CAN'T do (None) - this helps AI identify gaps!

### **Step 3: Verify Existing Tables**
- [ ] GPSS SUBCONTRACTORS exists and has data
- [ ] GPSS SUPPLIERS exists and has data
- [ ] GPSS OPPORTUNITIES exists and has data

### **Step 4: Test the System**
- [ ] Start Flask server: `python api_server.py`
- [ ] Run test script: `python test_ai_recommendations.py`
- [ ] Verify data appears in AI RECOMMENDATIONS table
- [ ] Test approve/deny workflow

---

## 🔧 QUICK TEST

Once tables are created, test with curl:

```bash
# Test 1: Capability Gap Analysis (replace recXYZ with real opportunity ID)
curl -X POST http://localhost:5000/ai/recommendations/capability-gap \
  -H "Content-Type: application/json" \
  -d '{"opportunity_id": "recXYZ123"}'

# Test 2: Check pending recommendations
curl http://localhost:5000/ai/recommendations/pending

# Test 3: Compliance calculator
curl -X POST http://localhost:5000/ai/compliance/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "contract_value": 500000,
    "your_work_value": 280000,
    "subcontractor_work_value": 180000
  }'
```

---

## 📊 SAMPLE DATA FOR TESTING

### **Sample Company Capabilities:**

```
1. Project Management - Expert - High capacity - $150/hr
2. Government Contracting - Expert - High capacity - $150/hr
3. Proposal Writing - Expert - High capacity - $125/hr
4. Product Sourcing - Expert - High capacity - $100/hr
5. Financial Management - Intermediate - Medium capacity - $100/hr
6. IT Support - Intermediate - Medium capacity - $100/hr
7. Cybersecurity - None - Low capacity - $0/hr
8. Software Development - None - Low capacity - $0/hr
9. Engineering - None - Low capacity - $0/hr
```

### **Sample Subcontractors (if you don't have any):**

```
1. Name: CyberSec Experts LLC
   Capabilities: Cybersecurity, Penetration Testing, Compliance
   Rating: 4.8
   Status: Active
   Location: Washington, DC
   
2. Name: DevOps Solutions Inc
   Capabilities: Software Development, DevOps, Cloud Infrastructure
   Rating: 4.5
   Status: Active
   Location: Arlington, VA
   
3. Name: Engineering Partners Co
   Capabilities: Structural Engineering, MEP Design, CAD
   Rating: 4.6
   Status: Active
   Location: Baltimore, MD
```

---

## 🚨 COMMON ISSUES

### **Issue 1: "Table not found"**
- **Cause:** Table name doesn't match exactly
- **Fix:** Ensure table is named **AI RECOMMENDATIONS** (all caps, space between words)

### **Issue 2: "Field not found"**
- **Cause:** Field name typo or wrong case
- **Fix:** All field names must be UPPERCASE (e.g., `CONFIDENCE` not `confidence`)

### **Issue 3: "No capabilities found"**
- **Cause:** COMPANY CAPABILITIES table is empty
- **Fix:** Add at least 5-10 capabilities (what you CAN do and CAN'T do)

### **Issue 4: "No subcontractors/suppliers found"**
- **Cause:** Those tables are empty
- **Fix:** Add sample data or run supplier mining first

---

## ✅ VERIFICATION

After setup, verify in Airtable:

1. **AI RECOMMENDATIONS table:**
   - Has 11 fields
   - Linked to GPSS OPPORTUNITIES
   - STATUS field has 4 options

2. **COMPANY CAPABILITIES table:**
   - Has 7 fields
   - Contains 5-10+ capability records
   - Includes both strengths AND gaps

3. **GPSS SUBCONTRACTORS:**
   - Has at least 3-5 subcontractors
   - All have ratings and capabilities

4. **GPSS SUPPLIERS:**
   - Has at least 10-20 suppliers
   - All have ratings and product info

---

**Setup complete! You're ready to use the AI Recommendation System.** 🎉

**Next step:** Run `python test_ai_recommendations.py` to test the full workflow!
