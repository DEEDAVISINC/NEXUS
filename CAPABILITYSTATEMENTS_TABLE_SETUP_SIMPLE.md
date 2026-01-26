# CapabilityStatements TABLE - SIMPLE SETUP
**⏱️ Time: 10 minutes**

---

## 🎯 WHAT THIS TABLE DOES

Tracks every capability statement PDF/HTML you generate:
- Which client it was for
- When it was created
- Where the files are saved
- Whether it was submitted
- Status tracking

---

## 📋 CREATE THE TABLE

### **Step 1: Create Table**

1. Go to your NEXUS Airtable base
2. Click the **"+"** button to add a new table
3. Name it exactly: **`CapabilityStatements`** (exact case)
4. Click "Create table"

---

### **Step 2: Add 15 Fields**

I'll list them in order. Just add each one:

---

#### **FIELD 1: RecordID** (Formula)

- Rename the first field to: **`RecordID`**
- Change type: **Formula**
- Formula: `RECORD_ID()`
- Click "Save"

---

#### **FIELD 2: OpportunityID** (Link to record)

- Click **"+"** to add field
- Name: **`OpportunityID`**
- Type: **Link to another record**
- Link to: **"Opportunities"** (or "GPSS OPPORTUNITIES")
- Allow multiple: **NO**
- Click "Save"

---

#### **FIELD 3: ClientName** (Single line text)

- Click **"+"** to add field
- Name: **`ClientName`**
- Type: **Single line text**
- Click "Save"

---

#### **FIELD 4: RFQNumber** (Single line text)

- Click **"+"** to add field
- Name: **`RFQNumber`**
- Type: **Single line text**
- Click "Save"

---

#### **FIELD 5: GeneratedDate** (Date)

- Click **"+"** to add field
- Name: **`GeneratedDate`**
- Type: **Date**
- Include time: **YES** ✓
- Click "Save"

---

#### **FIELD 6: HTMLPath** (Long text)

- Click **"+"** to add field
- Name: **`HTMLPath`**
- Type: **Long text**
- Click "Save"

---

#### **FIELD 7: PDFPath** (Long text)

- Click **"+"** to add field
- Name: **`PDFPath`**
- Type: **Long text**
- Click "Save"

---

#### **FIELD 8: ConfigJSON** (Long text)

- Click **"+"** to add field
- Name: **`ConfigJSON`**
- Type: **Long text**
- Click "Save"

---

#### **FIELD 9: Status** (Single select)

- Click **"+"** to add field
- Name: **`Status`**
- Type: **Single select**
- Add these 5 options:
  - `Generated` (Green)
  - `Submitted` (Blue)
  - `Accepted` (Purple)
  - `Rejected` (Red)
  - `Archived` (Gray)
- Set default: **`Generated`**
- Click "Save"

---

#### **FIELD 10: Template** (Single select)

- Click **"+"** to add field
- Name: **`Template`**
- Type: **Single select**
- Add these 4 options:
  - `default`
  - `va_medical`
  - `construction`
  - `custom`
- Click "Save"

---

#### **FIELD 11: SubmittedDate** (Date)

- Click **"+"** to add field
- Name: **`SubmittedDate`**
- Type: **Date**
- Include time: **YES** ✓
- Click "Save"

---

#### **FIELD 12: SubmittedBy** (Single line text)

- Click **"+"** to add field
- Name: **`SubmittedBy`**
- Type: **Single line text**
- Click "Save"

---

#### **FIELD 13: Notes** (Long text)

- Click **"+"** to add field
- Name: **`Notes`**
- Type: **Long text**
- Click "Save"

---

#### **FIELD 14: OpportunityName** (Lookup)

- Click **"+"** to add field
- Name: **`OpportunityName`**
- Type: **Lookup**
- Look up field from: **OpportunityID** (the link field you created)
- Select field: **Name** (or **Title** - whatever your opportunities table calls it)
- Click "Save"

---

#### **FIELD 15: OpportunityStatus** (Lookup)

- Click **"+"** to add field
- Name: **`OpportunityStatus`**
- Type: **Lookup**
- Look up field from: **OpportunityID**
- Select field: **Status**
- Click "Save"

---

## ✅ VERIFICATION

Your table should now have exactly 15 fields:

- [ ] RecordID (Formula)
- [ ] OpportunityID (Link)
- [ ] ClientName (Text)
- [ ] RFQNumber (Text)
- [ ] GeneratedDate (Date with time)
- [ ] HTMLPath (Long text)
- [ ] PDFPath (Long text)
- [ ] ConfigJSON (Long text)
- [ ] Status (Single select - 5 options)
- [ ] Template (Single select - 4 options)
- [ ] SubmittedDate (Date with time)
- [ ] SubmittedBy (Text)
- [ ] Notes (Long text)
- [ ] OpportunityName (Lookup)
- [ ] OpportunityStatus (Lookup)

---

## 🧪 ADD TEST RECORD

Let's test it works!

Click the **"+"** at the bottom, then fill in:

### **Field Values:**

**ClientName:** `Test Client`

**RFQNumber:** `TEST-123`

**GeneratedDate:** Today's date (with time)

**HTMLPath:** `/path/to/test.html`

**PDFPath:** `/path/to/test.pdf`

**Status:** `Generated`

**Template:** `default`

**Notes:** `This is a test record`

**Leave these blank:**
- OpportunityID (optional)
- ConfigJSON (optional)
- SubmittedDate (blank)
- SubmittedBy (blank)
- OpportunityName (auto-fills if you link opportunity)
- OpportunityStatus (auto-fills if you link opportunity)

Press **Enter** to save.

---

## ✅ SUCCESS CHECK

**Can you see your test record?**

If yes, your table is working! ✅

The RecordID field should show something like `recXXXXXXXXXX`

---

## 🎯 WHAT HAPPENS NEXT

When you generate capability statements using NEXUS:

1. System generates HTML and PDF files
2. Automatically creates record in this table
3. Stores file paths
4. Links to the opportunity
5. You can track status (Generated → Submitted → Accepted)

---

## 📊 EXAMPLE WORKFLOW

```
1. You generate capability statement for CPS Energy
   ↓
2. System creates files:
   - capstat_CPS_Energy_7000205103.html
   - capstat_CPS_Energy_7000205103.pdf
   ↓
3. System creates record in CapabilityStatements table:
   - ClientName: "CPS Energy"
   - RFQNumber: "7000205103"
   - HTMLPath: "/path/to/capstat_CPS_Energy_7000205103.html"
   - PDFPath: "/path/to/capstat_CPS_Energy_7000205103.pdf"
   - Status: "Generated"
   - Template: "default"
   ↓
4. You submit the PDF to client
   ↓
5. Update record:
   - Status: "Submitted"
   - SubmittedDate: Today
   - SubmittedBy: "Dee Davis"
   ↓
6. Track outcome:
   - If won: Status = "Accepted"
   - If lost: Status = "Rejected"
```

---

## 🎨 OPTIONAL VIEWS (2 minutes)

### **View 1: "Recent Statements"**
- Filter: GeneratedDate is within last 30 days
- Sort: GeneratedDate (newest first)

### **View 2: "Submitted"**
- Filter: Status is "Submitted" OR "Accepted"
- Sort: SubmittedDate (newest first)

### **View 3: "By Client"**
- Group by: ClientName
- Sort: GeneratedDate (newest first)

---

## ✅ YOU'RE DONE!

**Setup time:** 10 minutes  
**Table ready!** ✅

Now when you run:
```bash
python3 capability_statement_generator.py
```

It will automatically track everything in this table!

---

**Ready to test? Type "done" when you've created the table!** 🎯
