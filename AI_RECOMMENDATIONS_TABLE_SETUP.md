# AI RECOMMENDATIONS TABLE - SETUP GUIDE
**⏱️ Time: 3 minutes**

---

## 🎯 WHAT THIS TABLE DOES

Stores AI suggestions for:
- Capability gap analysis ("You can't do this, partner with someone who can")
- Subcontractor recommendations ("Use ABC Company - they're perfect for this")
- Supplier recommendations ("Buy from XYZ - best price/quality")
- Compliance checks ("This requirement needs attention")

You review and approve/deny each recommendation.

---

## 📋 STEP-BY-STEP SETUP

### **Step 1: Create Table**

1. Go to your NEXUS Airtable base
2. Click the **"+"** button to add a new table
3. Name it exactly: **`AI RECOMMENDATIONS`** (all caps, with space)
4. Click "Create table"

---

### **Step 2: Add Fields**

Airtable creates a default first field. Rename it and add the rest:

---

#### **FIELD 1: OPPORTUNITY** (Link to record)

- Click the field name (probably says "Name")
- Rename to: **`OPPORTUNITY`** (all caps)
- Change type: **Link to another record**
- Link to table: Select **"GPSS OPPORTUNITIES"** (or just "Opportunities")
- Click "Save"

---

#### **FIELD 2: TYPE** (Single select)

- Click **"+"** to add new field
- Name: **`TYPE`** (all caps)
- Type: **Single select**
- Add these 4 options:
  - `Capability Gap Analysis`
  - `Subcontractor Recommendation`
  - `Supplier Recommendation`
  - `Compliance Check`
- Click "Save"

---

#### **FIELD 3: RECOMMENDATION** (Long text)

- Click **"+"** to add new field
- Name: **`RECOMMENDATION`** (all caps)
- Type: **Long text**
- Leave settings default
- Click "Save"

---

#### **FIELD 4: CONFIDENCE** (Number)

- Click **"+"** to add new field
- Name: **`CONFIDENCE`** (all caps)
- Type: **Number**
- Format: **Integer**
- In "Number" settings:
  - Allow negative numbers: **OFF**
  - Precision: **0 decimal places**
- Click "Save"

**Note:** This will be 0-100 (AI confidence percentage)

---

#### **FIELD 5: REASONING** (Long text)

- Click **"+"** to add new field
- Name: **`REASONING`** (all caps)
- Type: **Long text**
- Leave settings default
- Click "Save"

---

#### **FIELD 6: STATUS** (Single select)

- Click **"+"** to add new field
- Name: **`STATUS`** (all caps)
- Type: **Single select**
- Add these 4 options (in this order):
  - `Pending Approval` ⭐ (set as default)
  - `Approved`
  - `Denied`
  - `Modified`
- Click "Save"

---

#### **FIELD 7: USER_DECISION** (Single select)

- Click **"+"** to add new field
- Name: **`USER_DECISION`** (all caps with underscore)
- Type: **Single select**
- Add these 3 options:
  - `APPROVED`
  - `DENIED`
  - `MODIFIED`
- Click "Save"

---

#### **FIELD 8: USER_NOTES** (Long text)

- Click **"+"** to add new field
- Name: **`USER_NOTES`** (all caps with underscore)
- Type: **Long text**
- Leave settings default
- Click "Save"

---

#### **FIELD 9: SELECTED_OPTION** (Single line text)

- Click **"+"** to add new field
- Name: **`SELECTED_OPTION`** (all caps with underscore)
- Type: **Single line text**
- Leave settings default
- Click "Save"

---

#### **FIELD 10: CREATED** (Created time)

- Click **"+"** to add new field
- Name: **`CREATED`** (all caps)
- Type: **Created time**
- Format: Select **"Include time"**
- Click "Save"

---

#### **FIELD 11: DECIDED_AT** (Date)

- Click **"+"** to add new field
- Name: **`DECIDED_AT`** (all caps with underscore)
- Type: **Date**
- Format: Select **"Include a time field"**
- Click "Save"

---

## ✅ VERIFICATION CHECKLIST

Your table should now have exactly 11 fields:

- [ ] OPPORTUNITY (Link to GPSS OPPORTUNITIES)
- [ ] TYPE (Single select - 4 options)
- [ ] RECOMMENDATION (Long text)
- [ ] CONFIDENCE (Number)
- [ ] REASONING (Long text)
- [ ] STATUS (Single select - 4 options)
- [ ] USER_DECISION (Single select - 3 options)
- [ ] USER_NOTES (Long text)
- [ ] SELECTED_OPTION (Single line text)
- [ ] CREATED (Created time with time)
- [ ] DECIDED_AT (Date with time)

---

## 🎨 CREATE VIEWS (OPTIONAL - 2 minutes)

### **View 1: "Pending Review"**

1. Click the dropdown next to "Grid view"
2. Click "Create new view"
3. Name: **"Pending Review"**
4. Type: Grid
5. Add filter: **STATUS** is **Pending Approval**
6. Sort by: **CREATED** (newest first)
7. Click "Save"

### **View 2: "High Confidence"**

1. Create new view: **"High Confidence"**
2. Add filter 1: **STATUS** is **Pending Approval**
3. Add filter 2: **CONFIDENCE** is greater than **80**
4. Sort by: **CONFIDENCE** (descending)
5. Click "Save"

### **View 3: "Approved"**

1. Create new view: **"Approved"**
2. Add filter: **USER_DECISION** is **APPROVED**
3. Sort by: **DECIDED_AT** (newest first)
4. Click "Save"

---

## 🧪 TEST IT (1 minute)

Add a test record to verify everything works:

1. Click **"+"** to add new record
2. Fill in:
   - **OPPORTUNITY:** (select any opportunity from your list)
   - **TYPE:** `Capability Gap Analysis`
   - **RECOMMENDATION:** `You lack cybersecurity certification. Consider partnering with SecureIT Solutions (8(a) certified, DOD experience).`
   - **CONFIDENCE:** `85`
   - **REASONING:** `RFP requires CMMC Level 2 certification which you don't have. SecureIT has certification and past performance with DOD.`
   - **STATUS:** `Pending Approval`
   - Leave other fields blank for now

3. Hit Enter to save

**If you can see the record, you're done!** ✅

---

## 🎯 HOW IT WORKS

### **Workflow:**

```
1. AI analyzes RFP
   ↓
2. AI identifies gaps/opportunities
   ↓
3. AI creates record in AI RECOMMENDATIONS table
   - TYPE: What kind of recommendation
   - RECOMMENDATION: The actual suggestion
   - CONFIDENCE: How sure AI is (0-100)
   - REASONING: Why AI suggests this
   - STATUS: "Pending Approval"
   ↓
4. You review in NEXUS dashboard
   ↓
5. You decide:
   - ✅ APPROVE: Set USER_DECISION = "APPROVED"
   - ❌ DENY: Set USER_DECISION = "DENIED"
   - ✏️ MODIFY: Set USER_DECISION = "MODIFIED" + add USER_NOTES
   ↓
6. AI learns from your decisions over time
```

---

## 📊 EXAMPLE RECOMMENDATIONS

**Example 1: Capability Gap**
```
TYPE: Capability Gap Analysis
RECOMMENDATION: "RFP requires software development (NAICS 541511). 
                 Consider teaming with TechCorp Solutions."
CONFIDENCE: 92
REASONING: "You have no software development capabilities. 
            TechCorp has 15 years DOD experience in NAICS 541511."
STATUS: Pending Approval
```

**Example 2: Subcontractor Match**
```
TYPE: Subcontractor Recommendation
RECOMMENDATION: "Use ABC Janitorial (Detroit) - they're perfect for this."
CONFIDENCE: 88
REASONING: "Local to contract area, 8(a) certified, 10 VA contracts 
            completed, average quote 15% below market."
STATUS: Pending Approval
```

**Example 3: Compliance Alert**
```
TYPE: Compliance Check
RECOMMENDATION: "This RFP requires EDWOSB certification - you qualify! 
                 Ensure cert is current in SAM.gov."
CONFIDENCE: 95
REASONING: "EDWOSB set-aside. You're certified. Verification required 
            before bid submission."
STATUS: Pending Approval
```

---

## 🚀 WHAT'S NEXT

Once this table is set up, the AI system can:

1. ✅ Analyze every new opportunity
2. ✅ Identify capability gaps automatically
3. ✅ Suggest specific partners/suppliers
4. ✅ Alert you to compliance requirements
5. ✅ Learn from your approve/deny decisions

**This table is the "brain" of your AI recommendation system!**

---

## ✅ YOU'RE DONE!

**Setup time:** 3 minutes  
**Impact:** AI can now suggest actions for every opportunity  

**Next step:** Set up COMPANY CAPABILITIES table (so AI knows YOUR skills)

---

## 🔗 RELATED TABLES

This table works with:
- **GPSS OPPORTUNITIES** (linked via OPPORTUNITY field)
- **COMPANY CAPABILITIES** (AI needs this to identify YOUR gaps)
- **GPSS SUBCONTRACTORS** (AI suggests partners from here)
- **GPSS Suppliers** (AI suggests suppliers from here)

---

## 📞 QUICK REFERENCE

**Table name:** `AI RECOMMENDATIONS` (exactly, all caps)  
**Number of fields:** 11  
**Setup time:** 3 minutes  
**Test:** Add 1 sample record  

**Field names to copy/paste:**
```
OPPORTUNITY
TYPE
RECOMMENDATION
CONFIDENCE
REASONING
STATUS
USER_DECISION
USER_NOTES
SELECTED_OPTION
CREATED
DECIDED_AT
```

---

**Table complete! Ready for AI recommendations!** 🤖✨
