# 🎯 NEXUS MINING TABLES - AIRTABLE SETUP GUIDE

**Time to complete:** 45-60 minutes  
**Tables to create:** 2 tables (VENDOR PORTALS + verify Mining Targets)

---

## 📋 **TABLE 1: VENDOR PORTALS** (NEW - Must Create)

**Purpose:** Track registered government portals where NEXUS can mine opportunities

### **STEP 1: Create the Table**
1. Go to your Airtable base (appaJZqKVUn3yJ7ma)
2. Click **"Add or import"** → **"Create table"**
3. Name it: **VENDOR PORTALS** (all caps)
4. Delete the default fields except the first one

---

### **STEP 2: Add These Fields (Copy This Grid)**

**PRIMARY FIELD (Rename the default first field):**

| Field Name | Field Type |
|------------|-----------|
| **Portal Name** | Single line text |

---

**BASIC INFO (Add these 6 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 1 | **Portal URL** | URL | |
| 2 | **Portal Type** | Single select | Options: `Federal`, `State`, `Local`, `Cooperative`, `Enterprise` |
| 3 | **Description** | Long text | |
| 4 | **Keywords** | Long text | Comma-separated search terms |
| 5 | **Category** | Single select | Options: `Government`, `Commercial`, `Cooperative`, `Industry` |
| 6 | **Icon** | Single line text | Emoji icon (e.g., 🦅, ⚡, 🛡️) |

---

**AUTOMATION SETTINGS (Add these 5 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 7 | **Auto-Mining Enabled** | Checkbox | |
| 8 | **Search Enabled** | Checkbox | |
| 9 | **Mining Frequency** | Single select | Options: `Hourly`, `Daily`, `Twice Daily`, `Weekly`, `Manual Only` |
| 10 | **Last Checked** | Date & time | |
| 11 | **Scraping Method** | Single select | Options: `API`, `Web Scraping`, `RSS Feed`, `Manual`, `Email Alerts` |

---

**REGISTRATION STATUS (Add these 5 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 12 | **Registration Status** | Single select | Options: `Active`, `Pending`, `Expired`, `Renewal Needed`, `Not Registered` |
| 13 | **Login URL** | URL | |
| 14 | **Registration Date** | Date | |
| 15 | **Expiration Date** | Date | |
| 16 | **Username** | Single line text | |

---

**PERFORMANCE TRACKING (Add these 5 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 17 | **Opportunities Found (Total)** | Number | Integer |
| 18 | **Opportunities This Month** | Number | Integer |
| 19 | **Success Rate** | Percent | |
| 20 | **Priority Level** | Single select | Options: `Critical`, `High`, `Medium`, `Low` |
| 21 | **Total Awarded Value** | Currency | USD |

---

**FILTERS & TARGETING (Add these 5 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 22 | **Geographic Focus** | Single select | Options: `National`, `MI`, `OH`, `IL`, `IN`, `WI`, `Multi-State`, `Regional` |
| 23 | **Primary Industry** | Single select | Options: `All Industries`, `Healthcare`, `Transportation`, `IT/Tech`, `Professional Services`, `Facilities`, `Education` |
| 24 | **Set-Aside Filter** | Multiple select | Options: `EDWOSB`, `WOSB`, `8(a)`, `HUBZone`, `SDVOSB`, `Small Business`, `All` |
| 25 | **Min Contract Value** | Currency | USD |
| 26 | **Max Contract Value** | Currency | USD |

---

**CONTACT INFO (Add these 3 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 27 | **Contact Name** | Single line text | Portal support contact |
| 28 | **Contact Email** | Email | |
| 29 | **Contact Phone** | Phone number | |

---

**TECHNICAL (Add these 3 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 30 | **API Available** | Checkbox | |
| 31 | **Auto-Login Working** | Checkbox | |
| 32 | **Scraping Issues** | Long text | Track technical problems |

---

**METADATA (Add these 3 fields):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 33 | **Notes** | Long text | Special instructions |
| 34 | **Tags** | Multiple select | Options: `High-Value`, `Easy-Win`, `EDWOSB-Friendly`, `Quick-Turnaround`, `Relationship-Based` |
| 35 | **Created Date** | Created time | Auto-generated |

---

### **✅ VENDOR PORTALS SUMMARY:**
- **Total Fields:** 36 (1 primary + 35 additional)
- **Time:** 30-40 minutes
- **Status:** ❌ Must create from scratch

---

---

## 📋 **TABLE 2: MINING TARGETS** (VERIFY - Should Already Exist)

**Purpose:** Track ANY website to scrape for opportunities (registered OR not)

### **STEP 1: Find the Table**
1. Look for table named **"Mining Targets"** in your base
2. If it exists but is empty, verify it has these fields below
3. If fields are missing, add them

---

### **STEP 2: Required Fields (Copy This Grid)**

**PRIMARY FIELD:**

| Field Name | Field Type |
|------------|-----------|
| **Target Name** | Single line text |

---

**BASIC INFO (Add if missing):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 1 | **Target URL** | URL | Page to scrape |
| 2 | **Source Type** | Single select | Options: `Intelligence`, `Marketplace`, `Archive`, `News`, `Portal` |
| 3 | **Description** | Long text | |
| 4 | **Keywords** | Long text | Comma-separated |

---

**SCRAPING CONFIG (Add if missing):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 5 | **Scraping Method** | Single select | Options: `API`, `Web Scraping`, `RSS Feed`, `Email Parsing`, `Manual` |
| 6 | **Scraping Frequency** | Single select | Options: `Hourly`, `Daily`, `Twice Daily`, `Weekly`, `Manual Only` |
| 7 | **Last Scraped** | Date & time | |
| 8 | **Active** | Checkbox | Is this target currently active? |

---

**PERFORMANCE (Add if missing):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 9 | **Opportunities Found** | Number | Integer |
| 10 | **Data Quality** | Single select | Options: `Excellent`, `Good`, `Fair`, `Poor` |
| 11 | **Reliability Score** | Number | 1-10 scale |

---

**METADATA (Add if missing):**

| # | Field Name | Field Type | Options/Configuration |
|---|------------|-----------|----------------------|
| 12 | **Notes** | Long text | |
| 13 | **Priority** | Single select | Options: `Critical`, `High`, `Medium`, `Low`, `Research Only` |
| 14 | **Created Date** | Created time | Auto-generated |

---

### **✅ MINING TARGETS SUMMARY:**
- **Total Fields:** 15 (1 primary + 14 additional)
- **Time:** 15-20 minutes (if needs fields added)
- **Status:** ✅ Table exists (0 records) - just verify fields

---

---

## 🎯 **QUICK SETUP CHECKLIST**

### **Before You Start:**
- [ ] Log into Airtable (airtable.com)
- [ ] Open base: **NEXUS Command Center** (ID: appaJZqKVUn3yJ7ma)
- [ ] Have this guide open in another window

---

### **Table 1: VENDOR PORTALS**
- [ ] Create new table named "VENDOR PORTALS"
- [ ] Rename first field to "Portal Name"
- [ ] Add 6 Basic Info fields
- [ ] Add 5 Automation Settings fields
- [ ] Add 5 Registration Status fields
- [ ] Add 5 Performance Tracking fields
- [ ] Add 5 Filters & Targeting fields
- [ ] Add 3 Contact Info fields
- [ ] Add 3 Technical fields
- [ ] Add 3 Metadata fields
- [ ] **Total: 36 fields ✓**

---

### **Table 2: MINING TARGETS**
- [ ] Find existing "Mining Targets" table
- [ ] Verify "Target Name" is primary field
- [ ] Check if 14 additional fields exist
- [ ] Add any missing fields from the grid above
- [ ] **Total: 15 fields ✓**

---

## 🚀 **AFTER SETUP - POPULATE WITH DATA**

Once tables are created, run this command:

```bash
cd /Users/deedavis/NEXUS\ BACKEND
python3 initialize_portals.py
```

**This will automatically add:**
- ✅ 6 Major Government Portals (SAM.gov, GSA eBuy, DIBBS, Unison, SubNet, NECO)
- ✅ 5 Intelligence Sources (FPDS, USASpending, Acquisition.gov, etc.)

---

## 📊 **VIEWS TO CREATE (OPTIONAL)**

### **For VENDOR PORTALS:**
1. **All Portals** (default grid view)
2. **Active Mining** - Filter: Auto-Mining Enabled = TRUE
3. **By Portal Type** - Group by: Portal Type
4. **High Priority** - Filter: Priority Level = Critical or High
5. **Needs Renewal** - Filter: Expiration Date < 30 days from today

### **For MINING TARGETS:**
1. **All Targets** (default grid view)
2. **Active Targets** - Filter: Active = TRUE
3. **By Source Type** - Group by: Source Type
4. **High Priority** - Filter: Priority = Critical or High

---

## ⏱️ **TIME ESTIMATES**

| Task | Time |
|------|------|
| Create VENDOR PORTALS table | 35 min |
| Verify/Fix Mining Targets table | 10 min |
| Run populate script | 2 min |
| **TOTAL** | **~45-50 minutes** |

---

## 💡 **PRO TIPS**

1. **Use Airtable Templates:** Airtable allows you to duplicate field configurations
2. **Create in Sections:** Follow the groups above (Basic Info → Automation → etc.)
3. **Test as You Go:** Add a test portal record after creating fields
4. **Don't Skip Fields:** All fields are used by the backend API
5. **Copy Field Names Exactly:** Case and spacing matter for API integration

---

## ❓ **COMMON QUESTIONS**

**Q: Do I need ALL 36 fields for VENDOR PORTALS?**  
A: No, but recommended. Minimum viable: Portal Name, Portal URL, Portal Type, Auto-Mining Enabled, Mining Frequency

**Q: What if Mining Targets already has different fields?**  
A: That's fine! Just add the missing required fields. Existing data won't be affected.

**Q: Can I change field names?**  
A: Not recommended - the backend code expects exact field names. If you must, you'll need to update `api_server.py` and `nexus_backend.py`

**Q: How do I know if it's working?**  
A: After creating tables and running the populate script, you should see 6 portals in VENDOR PORTALS and 5 targets in Mining Targets

---

## 🎉 **READY TO START?**

Open Airtable now and follow this guide field-by-field!

**Start with VENDOR PORTALS → Takes 35 minutes → Most important table**

---

**Questions? Stuck on a field type? Let me know and I'll help!** 🚀
