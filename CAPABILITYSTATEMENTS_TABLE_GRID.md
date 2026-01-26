# CapabilityStatements TABLE - FIELD GRID
**Complete setup reference**

---

## 📋 **QUICK SPECS**

**Table name:** `CapabilityStatements` (exact case)  
**Total fields:** 15  
**Setup time:** 10 minutes  
**Purpose:** Track generated capability statement PDFs/HTML

---

## 🗂️ **FIELD-BY-FIELD GRID**

| # | Field Name | Field Type | Configuration | Notes |
|---|------------|------------|---------------|-------|
| 1 | `RecordID` | **Formula** | Formula: `RECORD_ID()` | Auto-generates unique ID |
| 2 | `OpportunityID` | **Link to another record** | Link to: `Opportunities` table<br>Allow linking to multiple records: **NO** | Links to the bid/opportunity |
| 3 | `ClientName` | **Single line text** | - | Who you're submitting to |
| 4 | `RFQNumber` | **Single line text** | - | RFP/RFQ/Solicitation number |
| 5 | `GeneratedDate` | **Date** | Include a time field: **YES** ✓<br>Time format: 12 hour<br>Date format: US (M/D/YYYY) | When PDF/HTML was created |
| 6 | `HTMLPath` | **Long text** | Enable rich text formatting: **NO** | Full path to .html file |
| 7 | `PDFPath` | **Long text** | Enable rich text formatting: **NO** | Full path to .pdf file |
| 8 | `ConfigJSON` | **Long text** | Enable rich text formatting: **NO** | Stores the JSON config used |
| 9 | `Status` | **Single select** | **Options:**<br>• Generated (🟢 Green)<br>• Submitted (🔵 Blue)<br>• Accepted (🟣 Purple)<br>• Rejected (🔴 Red)<br>• Archived (⚫ Gray)<br><br>**Default:** `Generated` | Current status of statement |
| 10 | `Template` | **Single select** | **Options:**<br>• default<br>• va_medical<br>• construction<br>• custom<br><br>**No default** | Which template was used |
| 11 | `SubmittedDate` | **Date** | Include a time field: **YES** ✓<br>Time format: 12 hour<br>Date format: US (M/D/YYYY) | When you submitted to client |
| 12 | `SubmittedBy` | **Single line text** | - | Who submitted it (your name) |
| 13 | `Notes` | **Long text** | Enable rich text formatting: **YES** ✓ | Any notes about this statement |
| 14 | `OpportunityName` | **Lookup** | Look up records from: `OpportunityID`<br>Look up field: `Name` (or `Title`) | Auto-pulls opportunity name |
| 15 | `OpportunityStatus` | **Lookup** | Look up records from: `OpportunityID`<br>Look up field: `Status` | Auto-pulls opportunity status |

---

## 🎨 **RECOMMENDED VIEWS**

### **View 1: All Statements** (Default Grid View)
- **Sort:** `GeneratedDate` (newest first)
- **Fields shown:** All 15 fields
- **Filter:** None

---

### **View 2: Recent (Last 30 Days)**
- **Filter:** `GeneratedDate` is within the last 30 days
- **Sort:** `GeneratedDate` (newest first)
- **Fields shown:** ClientName, RFQNumber, GeneratedDate, Status, Template

---

### **View 3: Submitted**
- **Filter:** `Status` is `Submitted` OR `Accepted`
- **Sort:** `SubmittedDate` (newest first)
- **Fields shown:** ClientName, RFQNumber, SubmittedDate, SubmittedBy, Status, OpportunityName

---

### **View 4: By Client**
- **Group by:** `ClientName`
- **Sort:** `GeneratedDate` (newest first)
- **Fields shown:** ClientName, RFQNumber, GeneratedDate, Status, Template

---

### **View 5: Win Rate Analysis**
- **Filter:** `Status` is `Accepted` OR `Rejected`
- **Group by:** `Template`
- **Sort:** `GeneratedDate` (newest first)
- **Fields shown:** Template, ClientName, Status, SubmittedDate

---

## 📊 **EXAMPLE RECORDS**

### **Record 1: Recently Generated**
```
RecordID: rec123abc456def
OpportunityID: [Link to "CPS Energy RFQ 7000205103"]
ClientName: CPS Energy
RFQNumber: 7000205103
GeneratedDate: 1/25/2026 2:30 PM
HTMLPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_CPS_Energy_7000205103.html
PDFPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_CPS_Energy_7000205103.pdf
ConfigJSON: {"client_name": "CPS Energy", "rfq_number": "7000205103", ...}
Status: Generated
Template: default
SubmittedDate: [blank]
SubmittedBy: [blank]
Notes: Generated for electrical supplies RFQ
OpportunityName: CPS Energy - Electrical Supplies
OpportunityStatus: Qualified
```

---

### **Record 2: Submitted & Won**
```
RecordID: rec789ghi012jkl
OpportunityID: [Link to "VA Detroit Medical Center"]
ClientName: VA Detroit Medical Center
RFQNumber: 36C24625Q0045
GeneratedDate: 1/10/2026 10:15 AM
HTMLPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_VA_Detroit_36C24625Q0045.html
PDFPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_VA_Detroit_36C24625Q0045.pdf
ConfigJSON: {"client_name": "VA Detroit Medical Center", ...}
Status: Accepted
Template: va_medical
SubmittedDate: 1/10/2026 4:00 PM
SubmittedBy: Dee Davis
Notes: Won contract! $250K annual janitorial services.
OpportunityName: VA Detroit - Janitorial Services
OpportunityStatus: Awarded
```

---

### **Record 3: Submitted & Lost**
```
RecordID: recmnopqr345stu
OpportunityID: [Link to "Oakland County Buildings"]
ClientName: Oakland County
RFQNumber: ITB-2026-150
GeneratedDate: 12/15/2025 9:00 AM
HTMLPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_Oakland_County_ITB_2026_150.html
PDFPath: /Users/deedavis/NEXUS BACKEND/capability_statements/capstat_Oakland_County_ITB_2026_150.pdf
ConfigJSON: {"client_name": "Oakland County", ...}
Status: Rejected
Template: construction
SubmittedDate: 12/15/2025 3:00 PM
SubmittedBy: Dee Davis
Notes: Lost to local competitor. Price too high.
OpportunityName: Oakland County - Construction Materials
OpportunityStatus: Lost
```

---

## 🔗 **HOW IT CONNECTS TO OTHER TABLES**

### **Links TO:**
- **Opportunities** (via `OpportunityID` field)
  - You can see which opportunity this statement was for
  - Auto-pulls opportunity name and status

### **Links FROM:**
- **Opportunities** table should have field: `CapabilityStatement`
  - Link back to this table
  - Shows which statements were generated for each opportunity

---

## 📥 **HOW RECORDS GET CREATED**

### **Method 1: Automatic (via Python script)**
When you run:
```bash
python3 capability_statement_generator.py
```

The script:
1. Generates HTML and PDF files
2. Creates a record in this Airtable table
3. Populates all fields automatically
4. Sets Status = "Generated"

---

### **Method 2: Manual (in Airtable)**
1. Click "+" to add record
2. Fill in ClientName and RFQNumber
3. Upload PDF to an attachment field (if you want)
4. Set Status and Template
5. Add Notes

---

## 🔄 **TYPICAL WORKFLOW**

```
Step 1: Generate Statement
├─ Run: python3 capability_statement_generator.py
├─ System creates HTML + PDF files
├─ System creates record in CapabilityStatements table
└─ Status: "Generated"

Step 2: Review & Submit
├─ Review PDF in Airtable or file system
├─ Submit PDF to client
├─ Update record:
│  ├─ Status → "Submitted"
│  ├─ SubmittedDate → Today's date
│  └─ SubmittedBy → "Dee Davis"

Step 3: Track Outcome
├─ If you win:
│  ├─ Status → "Accepted"
│  └─ Notes → "Won! $XXX contract value"
│
└─ If you lose:
   ├─ Status → "Rejected"
   └─ Notes → "Lost to competitor. Reason: pricing"

Step 4: Analysis
├─ Use "Win Rate Analysis" view
├─ See which templates win most
└─ Optimize future statements
```

---

## 🎯 **KEY METRICS TO TRACK**

After you have 10+ records, analyze:

### **Win Rate by Template**
- Group by: `Template`
- Count: How many `Accepted` vs `Rejected`
- **Question:** Which template wins most often?

### **Response Time**
- Calculate: `SubmittedDate` - `GeneratedDate`
- **Question:** How fast do you submit after generating?

### **Client Success**
- Group by: `ClientName`
- Count: How many `Accepted` per client
- **Question:** Which clients accept most statements?

### **Template Usage**
- Count records by `Template`
- **Question:** Which template do you use most?

---

## ✅ **FIELD CHECKLIST (Copy/Paste Names)**

When creating table, use these exact field names:

```
RecordID
OpportunityID
ClientName
RFQNumber
GeneratedDate
HTMLPath
PDFPath
ConfigJSON
Status
Template
SubmittedDate
SubmittedBy
Notes
OpportunityName
OpportunityStatus
```

---

## 🎨 **CONDITIONAL FORMATTING (Optional)**

### **Status Field Colors**
- 🟢 **Green:** Generated (new statement ready)
- 🔵 **Blue:** Submitted (waiting for response)
- 🟣 **Purple:** Accepted (won!)
- 🔴 **Red:** Rejected (lost)
- ⚫ **Gray:** Archived (old/not used)

### **Row Colors (in Grid view)**
Set up in Airtable:
- **Purple background:** Status = "Accepted"
- **Yellow background:** Status = "Submitted" AND SubmittedDate > 7 days ago
- **Gray background:** Status = "Archived"

---

## 🔧 **AUTOMATION IDEAS**

### **Automation 1: Status Update Notification**
**Trigger:** When `Status` changes to "Accepted"  
**Action:** Send email: "🎉 You won! [ClientName] accepted your capability statement!"

---

### **Automation 2: Auto-Archive Old Statements**
**Trigger:** When `GeneratedDate` is more than 1 year ago  
**Condition:** Status = "Generated" (never submitted)  
**Action:** Change Status → "Archived"

---

### **Automation 3: Follow-up Reminder**
**Trigger:** When `Status` = "Submitted" for 7 days  
**Action:** Send email: "⏰ Follow up with [ClientName] about RFQ [RFQNumber]"

---

## 📱 **MOBILE VIEW (Optional)**

Create a simplified mobile view:

**Fields to show:**
- ClientName
- RFQNumber
- GeneratedDate
- Status

**Filter:** Status ≠ "Archived"  
**Sort:** GeneratedDate (newest first)

---

## 🚀 **ADVANCED FEATURES (Later)**

### **Add these fields eventually:**
- [ ] `VIEW_COUNT` (Number) - How many times accessed
- [ ] `DOWNLOAD_COUNT` (Number) - How many times downloaded
- [ ] `CONTRACT_VALUE` (Currency) - Value of opportunity
- [ ] `WIN_PROBABILITY` (Number 0-100) - AI-calculated chance of winning
- [ ] `COMPETITOR_COUNT` (Number) - How many competitors
- [ ] `PAGES` (Number) - How many pages in PDF
- [ ] `GENERATION_TIME` (Number) - Seconds to generate
- [ ] `LAST_MODIFIED` (Last modified time)

---

## 📊 **FORMULAS TO ADD LATER**

### **Days Since Generated**
```
DATETIME_DIFF(TODAY(), GeneratedDate, 'days')
```

### **Submitted On Time?**
```
IF(
  AND(SubmittedDate, GeneratedDate),
  IF(
    DATETIME_DIFF(SubmittedDate, GeneratedDate, 'days') <= 1,
    "✅ Quick",
    "⏰ Delayed"
  ),
  ""
)
```

### **Win Rate % (requires multiple records)**
This would be in a summary/dashboard view, not per-record.

---

## 🎯 **READY TO CREATE?**

### **Step 1: Create Table**
1. Go to Airtable
2. Click "+" for new table
3. Name: `CapabilityStatements`
4. Click "Create table"

### **Step 2: Add 15 Fields**
Use the grid above as reference!  
Follow the field types and configurations exactly.

### **Step 3: Create Views**
Create the 5 recommended views listed above.

### **Step 4: Test**
Add one test record to verify everything works.

---

## ✅ **SUCCESS CRITERIA**

You'll know it's working when:
- [ ] Table created with 15 fields
- [ ] RecordID shows `recXXXXX` for new records
- [ ] OpportunityID links to your Opportunities table
- [ ] Status dropdown has 5 options
- [ ] Template dropdown has 4 options
- [ ] Lookup fields (OpportunityName, OpportunityStatus) show data when opportunity linked
- [ ] Test record saves successfully

---

## 📞 **NEED HELP?**

**For step-by-step instructions:**  
Use: `CAPABILITYSTATEMENTS_TABLE_SETUP_SIMPLE.md`

**For automation setup:**  
Reference this grid for field names and types.

**For testing:**  
Add one record manually, then run the Python script to test auto-creation.

---

**Total setup time: 10 minutes** ⏱️  
**Difficulty: Easy** (same as AI Recommendations table) ✅

---

**Ready? Type "creating table now" when you start!** 🚀
