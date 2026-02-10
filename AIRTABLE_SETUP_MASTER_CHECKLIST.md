# 📋 AIRTABLE SETUP - MASTER CHECKLIST

**Created:** January 27, 2026  
**Purpose:** Complete list of all pending Airtable setup tasks  
**Status:** Ready to complete tomorrow  
**Estimated Total Time:** 60-75 minutes

---

## 🎯 OVERVIEW

You have **3 major Airtable tasks** to complete:

| Task | Type | Time | Priority | Status |
|------|------|------|----------|--------|
| **1. Create 3 New Tables** | New Tables | 45-60 min | High | ⏳ Pending |
| **2. Add Fields to 2 Tables** | Add Fields | 10-15 min | Medium | ⏳ Pending |
| **3. Add Document Fields** | Add Fields | 3-5 min | Medium | ⏳ Pending |

**TOTAL TIME:** 60-75 minutes (can do in one session tomorrow)

---

## 📊 TASK 1: CREATE 3 NEW SUPPLIER TABLES (45-60 minutes)

**Why:** Enable full supplier management and quote tracking in NEXUS

### **Table 1: GPSS Suppliers** (15-20 min)

**Fields to create:**

| # | Field Name | Type | Settings |
|---|------------|------|----------|
| 1 | Supplier ID | Autonumber | PRIMARY FIELD |
| 2 | Company Name | Single line text | |
| 3 | Website | URL | |
| 4 | Primary Contact Email | Email | |
| 5 | Primary Contact Phone | Phone number | |
| 6 | Product Keywords | Long text | |
| 7 | Net 30 Available | Checkbox | |
| 8 | Net 45 Available | Checkbox | |
| 9 | Business Status | Single select | Options: Active, Prospective, Inactive, Blacklisted |
| 10 | Typical Margin (%) | Number | Precision: 0, Format: Decimal |
| 11 | Overall Rating | Rating | Max: 5, Icon: Star, Color: Yellow |
| 12 | Discovery Method | Single select | Options: AI Mining, Google Search, Manual Entry, Referral, GSA Mining, Cold Outreach |
| 13 | Discovery Date | Date | Include time: No |
| 14 | Discovered By | Single select | Options: AI Mining, Manual Entry, Dee Davis |

**Total: 14 fields**

---

### **Table 2: GPSS Supplier Quotes** (15-20 min)

**Fields to create:**

| # | Field Name | Type | Settings |
|---|------------|------|----------|
| 1 | Quote Request ID | Autonumber | PRIMARY FIELD |
| 2 | Opportunity | Link to another record | Table: Opportunities |
| 3 | Supplier | Link to another record | Table: GPSS Suppliers |
| 4 | Product/Service Requested | Long text | |
| 5 | Quantity | Single line text | |
| 6 | Supplier Quote Amount | Currency | Precision: 2, Symbol: $ |
| 7 | Request Sent Date | Date | Include time: Yes |
| 8 | Quote Received Date | Date | Include time: Yes |
| 9 | Request Status | Single select | Options: Draft, Sent, Received, Declined, No Response, Expired |
| 10 | Our Markup (%) | Number | Precision: 0, Format: Decimal |
| 11 | Quoted Lead Time (Days) | Number | Precision: 0, Format: Integer |
| 12 | Selected for Quote | Checkbox | |
| 13 | Contract Awarded | Checkbox | |
| 14 | AI Recommendation | Long text | |

**Total: 14 fields**

---

### **Table 3: GPSS Supplier Orders** (15-20 min)

**Fields to create:**

| # | Field Name | Type | Settings |
|---|------------|------|----------|
| 1 | Order ID | Autonumber | PRIMARY FIELD |
| 2 | PO Number | Single line text | |
| 3 | Opportunity | Link to another record | Table: Opportunities |
| 4 | Supplier | Link to another record | Table: GPSS Suppliers |
| 5 | Product Details | Long text | |
| 6 | Order Date | Date | Include time: No |
| 7 | Order Amount | Currency | Precision: 2, Symbol: $ |
| 8 | Customer Invoice Amount | Currency | Precision: 2, Symbol: $ |
| 9 | Order Status | Single select | Options: Ordered, Confirmed, Shipped, Delivered, Completed, Cancelled |
| 10 | Expected Delivery Date | Date | Include time: No |
| 11 | Actual Delivery Date | Date | Include time: No |
| 12 | Payment Method | Single select | Options: Net 30, Net 45, Net 60, Factor Direct Payment, Check, ACH, Credit Card |
| 13 | Factoring Used | Checkbox | |
| 14 | Quality Rating | Rating | Max: 5, Icon: Star, Color: Yellow |

**Total: 14 fields**

---

## 📊 TASK 2: ADD FIELDS TO 2 MINING TABLES (10-15 minutes)

**Why:** Enable automated portal mining and intelligence tracking

### **Table: VENDOR PORTAL** (5-8 min)

**Current status:** ✅ Portal Name already exists  
**Add these 8 fields:**

| # | Field Name | Type | Options/Format |
|---|------------|------|----------------|
| 1 | Portal URL | URL | - |
| 2 | Portal Type | Single select | High Priority, Prime Contractor, Federal Specialty, Cooperative, Agency-Specific |
| 3 | Status | Single select | Active, Inactive, Testing |
| 4 | Last Checked | Date/Time | Include time |
| 5 | Opportunities Found | Number | Integer |
| 6 | Keywords | Long text | - |
| 7 | Win Rate | Percent | Format: 0-100% |
| 8 | Notes | Long text | - |

---

### **Table: Mining Targets** (5-7 min)

**Current status:** ✅ Target Name already exists  
**Add these 9 fields:**

| # | Field Name | Type | Options/Format |
|---|------------|------|----------------|
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

## 📊 TASK 3: ADD DOCUMENT PACKAGE FIELDS (3-5 minutes)

**Why:** Enable one-click bid document assembly from NEXUS dashboard

### **Table: Opportunities** (3-5 min)

**Current status:** ✅ Table exists with all opportunity fields  
**Add these 5 fields:**

| # | Field Name | Type | Options |
|---|------------|------|---------|
| 1 | Documents Package | Attachment | - |
| 2 | Documents Checklist | Multiple Select | W-9, EDWOSB, WOSB, Insurance, SAM, CAGE, CapStatement, References, Banking, WorkersComp, MBE |
| 3 | Package Status | Single Select | Not Needed, Incomplete, Ready, Attached |
| 4 | Package Assembled Date | Date | - |
| 5 | Package Assembled By | Single Line Text | - |

**What this enables:**
- Click "Assemble Package" button in NEXUS
- System gathers documents from COMPANY_DOCUMENTS/
- Uploads to Airtable automatically
- Tracks what's included and when

---

## ✅ COMPLETE SETUP CHECKLIST

### **Tomorrow's Airtable Session:**

**⏰ Time Block: 60-75 minutes**

#### **TASK 1: Create Supplier Tables (45-60 min)**
- [ ] Create "GPSS Suppliers" table (14 fields)
- [ ] Create "GPSS Supplier Quotes" table (14 fields)
- [ ] Create "GPSS Supplier Orders" table (14 fields)
- [ ] Verify linked record relationships work

#### **TASK 2: Add Mining Fields (10-15 min)**
- [ ] Add 8 fields to "VENDOR PORTAL" table
- [ ] Add 9 fields to "Mining Targets" table
- [ ] Set all Status fields to "Active"

#### **TASK 3: Add Document Fields (3-5 min)**
- [ ] Add 5 fields to "Opportunities" table
- [ ] Verify field names match exactly

#### **Verification:**
- [ ] All tables created
- [ ] All fields added
- [ ] Field types correct
- [ ] Single select options configured
- [ ] Ready to use!

---

## 📋 FIELD TOTALS

**New Tables:**
- 3 tables × 14 fields = **42 fields**

**Field Additions:**
- VENDOR PORTAL: **8 fields**
- Mining Targets: **9 fields**
- Opportunities: **5 fields**

**GRAND TOTAL: 64 new fields across 5 tables**

---

## 🎯 BENEFITS AFTER COMPLETION

### **Supplier Tables:**
- ✅ Track all suppliers in one place
- ✅ Request and compare quotes
- ✅ Track orders and delivery
- ✅ Rate supplier performance
- ✅ Know payment terms (Net 30/45)

### **Mining Tables:**
- ✅ Automated portal monitoring
- ✅ Track which sources are most valuable
- ✅ Intelligence gathering from FPDS, USASpending
- ✅ Know when each portal was last checked
- ✅ Customize keywords per portal

### **Document Fields:**
- ✅ One-click bid package assembly
- ✅ Never forget documents
- ✅ Track what's included
- ✅ Save 2-5 hours per month

---

## 🚀 QUICK START GUIDE (For Tomorrow)

### **Step 1: Open Airtable**
1. Go to airtable.com
2. Open your NEXUS base

### **Step 2: Create Tables (45-60 min)**
1. Click "+ Add or import" → "Create empty table"
2. Name: "GPSS Suppliers"
3. Add all 14 fields from Task 1
4. Repeat for "GPSS Supplier Quotes" and "GPSS Supplier Orders"

### **Step 3: Add Mining Fields (10-15 min)**
1. Go to "VENDOR PORTAL" table
2. Click "+" to add field
3. Add all 8 fields from Task 2
4. Repeat for "Mining Targets" (9 fields)

### **Step 4: Add Document Fields (3-5 min)**
1. Go to "Opportunities" table
2. Click "+" to add field
3. Add all 5 fields from Task 3

### **Step 5: Message "Tables created"**
- I'll verify everything is set up correctly
- Run initialization scripts if needed
- Test all integrations

---

## 📚 REFERENCE DOCUMENTS

**Detailed guides:**
- Task 1: `CREATE_THESE_TABLES.md`
- Task 2: `AIRTABLE_FIELDS_SETUP_GUIDE.md`
- Task 3: `NEXUS_DOCUMENT_INTEGRATION_COMPLETE.md`

**This master checklist:** `AIRTABLE_SETUP_MASTER_CHECKLIST.md`

---

## 💡 PRO TIPS

### **Tip 1: Work in Order**
Do Task 1 first (supplier tables) because Tasks 2 and 3 are quick wins after!

### **Tip 2: Copy Field Settings**
- Single select options: copy-paste from this doc
- Saves typing time
- Ensures consistency

### **Tip 3: Take Breaks**
- Task 1: 20 min → Break
- Task 1: 20 min → Break
- Task 1: 20 min → Done
- Tasks 2-3: 15 min → Done! 🎉

### **Tip 4: Verify as You Go**
After each table, add a test record to verify fields work correctly.

---

## 🎯 WHAT YOU'LL HAVE AFTER

**Before Tomorrow:**
- Basic NEXUS with Opportunities tracking
- Manual document hunting
- No supplier database
- No automated mining

**After Tomorrow:**
- ✅ Full supplier management
- ✅ Quote comparison system
- ✅ Order tracking
- ✅ Automated portal mining
- ✅ Intelligence gathering
- ✅ One-click document packages

**Time investment:** 60-75 minutes  
**Time saved forever:** 5-10 hours per month  
**ROI:** Incredible! 🚀

---

## ✅ FINAL CHECKLIST

**Before starting tomorrow:**
- [ ] Read this master checklist
- [ ] Have Airtable open and logged in
- [ ] Set aside 75 minutes uninterrupted
- [ ] Have CREATE_THESE_TABLES.md handy for reference

**During setup:**
- [ ] Complete Task 1: Create 3 supplier tables
- [ ] Complete Task 2: Add fields to 2 mining tables
- [ ] Complete Task 3: Add fields to Opportunities table
- [ ] Test: Add sample record to each new table

**After setup:**
- [ ] Message "Tables created"
- [ ] I'll verify everything
- [ ] Run initialization scripts
- [ ] Start using immediately!

---

## 📞 NEED HELP?

**If you get stuck:**
1. Check the detailed reference docs (listed above)
2. Message me what you're stuck on
3. I'll guide you through it

**Most common issues:**
- Misspelled field names → Just rename the field
- Wrong field type → Delete and recreate
- Missing options → Edit field and add them

**It's okay to not be perfect!** We can fix any issues quickly.

---

**STATUS:** ✅ Ready for tomorrow  
**PRIORITY:** High (unlocks major NEXUS features)  
**ESTIMATED TIME:** 60-75 minutes  
**DIFFICULTY:** Easy (just follow the tables)

---

**You've got this! Tomorrow you'll knock out all 64 fields and NEXUS will be fully operational!** 💪

**After setup, you'll have:**
- Complete supplier management
- Automated opportunity mining
- One-click bid packages
- Full NEXUS power unlocked! 🚀

---

**Created:** January 27, 2026  
**Updated:** January 27, 2026  
**Version:** 1.0  
**Status:** Ready for execution tomorrow ✅
