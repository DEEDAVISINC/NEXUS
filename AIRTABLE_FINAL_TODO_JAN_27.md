# 📋 AIRTABLE - FINAL TODO LIST (35-45 minutes)

**Date:** January 27, 2026  
**Status:** Fields to add + 1 table to create  
**Time:** 35-45 minutes total

---

## ✅ WHAT YOU ALREADY HAVE (No Work Needed)

You have 69 tables including:
- ✅ GPSS Suppliers
- ✅ GPSS Supplier Quotes
- ✅ GPSS Supplier Orders
- ✅ GPSS Proposals
- ✅ CapabilityStatements
- ✅ GPSS SUBCONTRACTOR COMPLIANCE
- ✅ GPSS SUBCONTRACTORS
- ✅ AI RECOMMENDATIONS
- ✅ COMPANY CAPABILITIES

**Good news: Most tables exist!**

---

## 🎯 WHAT YOU NEED TO DO TOMORROW

### **TASK 1: Add Fields to VENDOR PORTAL** (5 minutes)

**Table:** VENDOR PORTAL (already exists)  
**Current:** Portal Name only  
**Add these 8 fields:**

| # | Field Name | Type | Options |
|---|------------|------|---------|
| 1 | Portal URL | URL | - |
| 2 | Portal Type | Single select | High Priority, Prime Contractor, Federal Specialty, Cooperative, Agency-Specific |
| 3 | Status | Single select | Active, Inactive, Testing |
| 4 | Last Checked | Date/Time | Include time |
| 5 | Opportunities Found | Number | Integer |
| 6 | Keywords | Long text | - |
| 7 | Win Rate | Percent | 0-100% |
| 8 | Notes | Long text | - |

---

### **TASK 2: Add Fields to Mining Targets** (5 minutes)

**Table:** Mining Targets (already exists)  
**Current:** Target Name only  
**Add these 9 fields:**

| # | Field Name | Type | Options |
|---|------------|------|---------|
| 1 | Target URL | URL | - |
| 2 | Target Type | Single select | Intelligence, Forecasting, Competitive Intel |
| 3 | Status | Single select | Active, Inactive, Testing |
| 4 | Last Checked | Date/Time | Include time |
| 5 | Opportunities Found | Number | Integer |
| 6 | Mining Frequency | Single select | Hourly, Daily, Weekly, Manual |
| 7 | Priority | Single select | High, Medium, Low |
| 8 | Data Type | Single select | Historical Contracts, Spending Data, Forecasts, Pricing, Market Intelligence |
| 9 | Notes | Long text | - |

---

### **TASK 3: Add Document Fields to Opportunities** (3 minutes)

**Table:** Opportunities (already exists)  
**Add these 5 fields:**

| # | Field Name | Type | Options |
|---|------------|------|---------|
| 1 | Documents Package | Attachment | - |
| 2 | Documents Checklist | Multiple Select | W-9, EDWOSB, WOSB, Insurance, SAM, CAGE, CapStatement, References, Banking, WorkersComp, MBE |
| 3 | Package Status | Single Select | Not Needed, Incomplete, Ready, Attached |
| 4 | Package Assembled Date | Date | - |
| 5 | Package Assembled By | Single Line Text | - |

**Purpose:** Enable one-click bid document assembly from NEXUS

---

### **TASK 4: Add Capability Statement Fields to Opportunities** (2 minutes)

**Table:** Opportunities (already exists)  
**Add these 3 fields:**

| # | Field Name | Type | Purpose |
|---|------------|------|---------|
| 1 | CapabilityStatement | Link to another record | Link to CapabilityStatements table |
| 2 | CapStatGenerated | Checkbox | Quick status |
| 3 | CapStatDate | Date | When generated |

**Purpose:** Link opportunities to their capability statements

---

### **TASK 5: Add Compliance Fields to SUBCONTRACTORS** (3 minutes)

**Table:** GPSS SUBCONTRACTORS (already exists)  
**Add these 4 fields:**

| # | Field Name | Type | Purpose |
|---|------------|------|---------|
| 1 | COMPLIANCE_DOCUMENTS | Link to another record | Link to GPSS SUBCONTRACTOR COMPLIANCE |
| 2 | COMPLIANCE_STATUS | Formula | `COUNTA({COMPLIANCE_DOCUMENTS}) & " docs"` |
| 3 | LAST_COMPLIANCE_CHECK | Date | Last verification |
| 4 | COMPLIANCE_READY | Checkbox | All docs approved? |

**Purpose:** See compliance status when selecting subcontractors

---

### **TASK 6: Create Quote Requests Table** (15-20 minutes)

**Table:** Quote Requests (NEW - doesn't exist yet)  
**Purpose:** Track supplier quote requests and follow-ups

| # | Field Name | Type | Options/Formula |
|---|------------|------|-----------------|
| 1 | Name | Formula | `{Opportunity} & " → " & {Supplier}` (PRIMARY) |
| 2 | Opportunity | Link to another record | Table: Opportunities |
| 3 | Supplier | Link to another record | Table: GPSS Suppliers |
| 4 | Sent Date | Date & Time | Include time |
| 5 | Sent Method | Single Select | Email, Fax, Phone, Portal |
| 6 | Sent To | Single Line Text | Email/fax/phone |
| 7 | Status | Single Select | Sent, Received, Quoted, Declined, No Response, Failed |
| 8 | PDF Path | Single Line Text | Path to generated PDF |
| 9 | Due Date | Date | When we need quote by |
| 10 | Quote Received Date | Date & Time | Include time |
| 11 | Quote Amount | Currency | $ |
| 12 | Follow-up Needed | Checkbox | Auto-check if no response |
| 13 | Follow-up Date | Date | When to follow up |
| 14 | Follow-up Count | Number | Integer - how many sent |
| 15 | Last Follow-up | Date & Time | Include time |
| 16 | Notes | Long Text | Internal notes |
| 17 | Response Time | Formula | `DATETIME_DIFF({Quote Received Date}, {Sent Date}, 'days')` |

---

## ✅ SUMMARY CHECKLIST

**Fields to ADD to existing tables:**
- [ ] VENDOR PORTAL: Add 8 fields (5 min)
- [ ] Mining Targets: Add 9 fields (5 min)
- [ ] Opportunities: Add 5 document fields (3 min)
- [ ] Opportunities: Add 3 capability statement fields (2 min)
- [ ] SUBCONTRACTORS: Add 4 compliance fields (3 min)

**New table to CREATE:**
- [ ] Quote Requests: Create table with 17 fields (15-20 min)

**TOTAL TIME: 35-45 minutes**

---

## 🎯 WHAT THESE ENABLE

**VENDOR PORTAL & Mining Targets fields:**
- ✅ Automated portal mining
- ✅ Track which sources are most valuable
- ✅ Intelligence gathering from FPDS, USASpending

**Document fields (Opportunities):**
- ✅ One-click bid package assembly
- ✅ Never forget documents
- ✅ Track what's included in each bid

**Capability Statement fields (Opportunities):**
- ✅ Link capability statements to opportunities
- ✅ Track which statements were generated
- ✅ Measure win rates by template

**Compliance fields (SUBCONTRACTORS):**
- ✅ See subcontractor compliance status at a glance
- ✅ Track W-9s, insurance, NDAs
- ✅ Verify compliance before sending RFQs

**Quote Requests table:**
- ✅ Track all supplier quote requests
- ✅ Automated follow-up reminders
- ✅ Measure supplier response times
- ✅ See which suppliers are most responsive

---

## 📊 FIELD COUNT

**Total fields to add:** 29 fields across 3 tables  
**New table:** 1 table with 17 fields  
**Time:** 35-45 minutes

---

## 🚀 QUICK START GUIDE

### **How to Add Fields:**
1. Open Airtable → Your NEXUS base
2. Go to the table (e.g., VENDOR PORTAL)
3. Click "+" next to last column
4. Select field type
5. Name it exactly as shown
6. Configure options if needed (Single select, etc.)
7. Click "Create field"
8. Repeat for remaining fields

### **How to Create Quote Requests Table:**
1. Click "+" next to your tables
2. Select "Start from scratch"
3. Name it: "Quote Requests"
4. Add all 17 fields from the list above
5. For Formula fields, copy the formula exactly
6. For Link fields, select the target table

---

## ✅ VERIFICATION

After you're done, you should have:
- ✅ VENDOR PORTAL table with 9+ fields
- ✅ Mining Targets table with 10+ fields
- ✅ Opportunities table with 8 new fields (docs + capstats)
- ✅ SUBCONTRACTORS table with 4 new fields
- ✅ Quote Requests table (brand new, 17 fields)

---

## 💪 WHAT HAPPENS AFTER

Once you complete this:

1. **Document assembly integration** will work
   - Click "Assemble Package" in NEXUS → Documents attached

2. **Portal mining** will be automated
   - System tracks which portals are most valuable

3. **Quote tracking** will be automated
   - All supplier requests tracked automatically
   - Follow-ups scheduled automatically

4. **Compliance** will be visible
   - See which subcontractors are compliant before sending RFQs

---

## 📞 WHEN YOU'RE DONE

Message: **"Fields added"**

Then I'll:
- ✅ Verify everything is set up correctly
- ✅ Run initialization scripts if needed
- ✅ Test all integrations
- ✅ You're ready to use everything!

---

**STATUS:** ✅ Final checklist ready  
**TIME:** 35-45 minutes tomorrow  
**BENEFIT:** Full NEXUS automation unlocked!

---

*This is the FINAL, ACCURATE list. You already have most tables - just need to add these fields + create Quote Requests!*
