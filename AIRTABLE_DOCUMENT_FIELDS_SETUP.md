# 📋 AIRTABLE DOCUMENT FIELDS SETUP - STEP BY STEP
**Time:** 25 minutes total  
**Result:** Document system fully connected to NEXUS

---

## 🎯 PART 1: ADD 5 FIELDS TO GPSS OPPORTUNITIES TABLE
**Time:** 10 minutes

### **Step 1: Open Airtable**
1. Go to https://airtable.com
2. Sign in
3. Open your **NEXUS** base
4. Click on **GPSS OPPORTUNITIES** table

---

### **Step 2: Add Field #1 - Documents Package**

1. **Click the "+" button** at the end of your fields (top right)
2. **Field Name:** `Documents Package`
3. **Field Type:** Click dropdown → Select **"Attachment"**
4. **Click "Create field"**

✅ Done! This field will store assembled PDF packages.

---

### **Step 3: Add Field #2 - Documents Checklist**

1. **Click the "+" button** again
2. **Field Name:** `Documents Checklist`
3. **Field Type:** Select **"Multiple select"**
4. **Add these 11 options** (click "Add option" for each):
   - `W-9`
   - `EDWOSB`
   - `WOSB`
   - `Insurance`
   - `SAM`
   - `CAGE`
   - `CapStatement`
   - `References`
   - `Banking`
   - `WorkersComp`
   - `MBE`
5. **Click "Create field"**

✅ Done! This tracks which documents are in the package.

---

### **Step 4: Add Field #3 - Package Status**

1. **Click the "+" button**
2. **Field Name:** `Package Status`
3. **Field Type:** Select **"Single select"**
4. **Add these 4 options:**
   - `Not Needed`
   - `Incomplete`
   - `Ready`
   - `Attached`
5. **Optional:** Color code them:
   - Not Needed = Gray
   - Incomplete = Yellow
   - Ready = Blue
   - Attached = Green
6. **Click "Create field"**

✅ Done! This shows package readiness.

---

### **Step 5: Add Field #4 - Package Assembled Date**

1. **Click the "+" button**
2. **Field Name:** `Package Assembled Date`
3. **Field Type:** Select **"Date"**
4. **Format:** Choose your preferred date format
5. **Include time:** Check this box (helpful for tracking)
6. **Click "Create field"**

✅ Done! Records when package was created.

---

### **Step 6: Add Field #5 - Package Assembled By**

1. **Click the "+" button**
2. **Field Name:** `Package Assembled By`
3. **Field Type:** Select **"Single line text"**
4. **Click "Create field"**

✅ Done! Tracks who/what created the package (e.g., "NEXUS API" or your name).

---

### **✅ PART 1 COMPLETE!**

Your GPSS OPPORTUNITIES table now has all 5 document fields.

**Quick Check:**
- [ ] Documents Package (Attachment)
- [ ] Documents Checklist (Multiple Select - 11 options)
- [ ] Package Status (Single Select - 4 options)
- [ ] Package Assembled Date (Date)
- [ ] Package Assembled By (Single Line Text)

---

## 🎯 PART 2: CREATE SUPPLIER_RFPS TABLE
**Time:** 15 minutes

### **Step 1: Create New Table**

1. In your NEXUS base, look at the left sidebar (list of tables)
2. **Click the "+" button** next to table names
3. **Name:** `SUPPLIER_RFPS`
4. **Click "Add table"**

Airtable will create a new table with default fields. We'll replace these.

---

### **Step 2: Delete Default Fields**

1. Airtable creates default fields (Name, Notes, etc.)
2. **Right-click each field** → **"Delete field"**
3. Delete all except keep one for now (we'll edit it)

---

### **Step 3: Add RFP Fields (14 total)**

**FIELD #1:**
- **Name:** `ddi_rfp_number`
- **Type:** Single line text
- **Purpose:** DDI-2026-PW-001 format

**FIELD #2:**
- **Name:** `project_name`
- **Type:** Single line text
- **Purpose:** Project title

**FIELD #3:**
- **Name:** `category`
- **Type:** Single select
- **Options:** Add these:
  - `Pressure Washing`
  - `Landscaping`
  - `Janitorial`
  - `Construction`
  - `Supplies`
  - `HVAC`
  - `Plumbing`
  - `Electrical`
  - `General Services`
  - `Painting`
  - `Maintenance`

**FIELD #4:**
- **Name:** `sanitized_location`
- **Type:** Single line text
- **Purpose:** Generic location (Oakland County, not specific address)

**FIELD #5:**
- **Name:** `scope_of_work`
- **Type:** Long text
- **Enable rich text formatting:** ✅ Check this

**FIELD #6:**
- **Name:** `contract_value_min`
- **Type:** Number
- **Format:** Currency → USD
- **Precision:** 2 decimal places

**FIELD #7:**
- **Name:** `contract_value_max`
- **Type:** Number
- **Format:** Currency → USD
- **Precision:** 2 decimal places

**FIELD #8:**
- **Name:** `quote_due_date`
- **Type:** Date
- **Include time:** ✅ Check this

**FIELD #9:**
- **Name:** `contract_period`
- **Type:** Single line text
- **Purpose:** e.g., "March 2026 - December 2026"

**FIELD #10:**
- **Name:** `service_locations_count`
- **Type:** Number
- **Format:** Integer (no decimals)

**FIELD #11:**
- **Name:** `insurance_requirements`
- **Type:** Long text
- **Enable rich text formatting:** ✅ Check this

**FIELD #12:**
- **Name:** `status`
- **Type:** Single select
- **Options:**
  - `draft`
  - `sent`
  - `responses received`
- **Colors:**
  - draft = Gray
  - sent = Blue
  - responses received = Green

**FIELD #13:**
- **Name:** `pdf_generated_path`
- **Type:** Single line text
- **Purpose:** Where PDF is stored

**FIELD #14:**
- **Name:** `buyer_name`
- **Type:** Single line text
- **Purpose:** **CONFIDENTIAL** - actual end buyer name

**FIELD #15:**
- **Name:** `buyer_rfp_number`
- **Type:** Single line text
- **Purpose:** **CONFIDENTIAL** - buyer's actual solicitation number

---

### **✅ PART 2 COMPLETE!**

Your SUPPLIER_RFPS table is ready!

**Quick Check (15 fields total):**
- [ ] ddi_rfp_number
- [ ] project_name
- [ ] category (11 options)
- [ ] sanitized_location
- [ ] scope_of_work
- [ ] contract_value_min
- [ ] contract_value_max
- [ ] quote_due_date
- [ ] contract_period
- [ ] service_locations_count
- [ ] insurance_requirements
- [ ] status (3 options)
- [ ] pdf_generated_path
- [ ] buyer_name
- [ ] buyer_rfp_number

---

## 🎯 PART 3: VERIFY SETUP
**Time:** 2 minutes

### **Test Command:**

Open Terminal and run:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 audit_document_integration.py
```

**Expected Output:**
```
✅ GPSS OPPORTUNITIES: 5/5 document fields exist
✅ SUPPLIER_RFPS table exists
```

If you see ❌ for any fields, go back and add them.

---

## 🎉 YOU'RE DONE!

### **What You Just Fixed:**

**BEFORE:**
- ❌ Document system can't update Airtable
- ❌ RFP Generator can't save to database
- ❌ No document tracking

**AFTER:**
- ✅ Document assembly can update opportunities
- ✅ RFP Generator can save all RFPs
- ✅ Full document tracking in NEXUS
- ✅ Frontend will work when APIs connected

---

## 📝 NEXT STEPS:

**Still needed (but not Airtable):**

1. **Upload Company Documents** (10 min)
   - W-9, EDWOSB cert, WOSB cert, Insurance cert
   - Put in COMPANY_DOCUMENTS/ folder

2. **Connect API Endpoints** (5 min)
   - Add document endpoints to api_server.py
   - Restart API server

3. **Start Quote Generator API** (2 min)
   - Run the quote generation API on port 5001

**But the Airtable integration is NOW COMPLETE!** ✅

---

## 🆘 TROUBLESHOOTING:

### **"Can't find the + button to add fields"**
- You might be in view mode
- Click table name → "Open table"
- Should see all fields at top

### **"Multiple select not showing all options"**
- You need to click "Add option" 11 times for Documents Checklist
- Copy-paste each option name exactly

### **"Field names matter?"**
- YES! Use EXACT names (case-sensitive)
- `Documents Package` ≠ `Document Package`
- Copy-paste from this guide to be safe

### **"Created wrong field type, how to fix?"**
- Right-click field → "Delete field"
- Add new field with correct type
- Airtable doesn't let you change field types easily

---

## ⏱️ TIME BREAKDOWN:

- **GPSS OPPORTUNITIES:** 5 fields × 2 min = 10 minutes
- **SUPPLIER_RFPS:** 15 fields × 1 min = 15 minutes
- **Total:** 25 minutes

**If you know Airtable well:** Can do in 15 minutes  
**If first time:** Might take 30 minutes (that's okay!)

---

## ✅ COMPLETION CHECKLIST:

**GPSS OPPORTUNITIES Table:**
- [ ] Documents Package field added
- [ ] Documents Checklist field added (11 options)
- [ ] Package Status field added (4 options)
- [ ] Package Assembled Date field added
- [ ] Package Assembled By field added

**SUPPLIER_RFPS Table:**
- [ ] Table created
- [ ] All 15 fields added
- [ ] category field has 11 service types
- [ ] status field has 3 statuses
- [ ] Value fields formatted as currency

**Verification:**
- [ ] Ran audit_document_integration.py
- [ ] Got ✅ for all fields and table

---

**ONCE THESE ARE DONE, YOUR DOCUMENT SYSTEM CAN TALK TO NEXUS!** 🎉

---

*Setup guide created: February 1, 2026*  
*Estimated time: 25 minutes*  
*Difficulty: Easy (just follow steps)*
