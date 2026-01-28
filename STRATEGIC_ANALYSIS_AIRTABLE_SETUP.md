# Strategic Analysis Module - Airtable Setup Guide

**Purpose:** Add fields and tables to support RFP Success® Strategic Intelligence  
**Estimated Time:** 15-20 minutes  
**Created:** January 27, 2026

---

## 📋 OVERVIEW

This guide walks you through adding the Strategic Analysis fields and tables to your NEXUS Airtable base. This will enable:

- ✅ Go/No-Go bid decision scoring
- ✅ Evaluator behavioral style detection
- ✅ Win themes library management
- ✅ Strategic positioning reports
- ✅ Post-bid debrief tracking

---

## 🔧 PART 1: UPDATE EXISTING TABLE (GPSS OPPORTUNITIES)

### **Table:** `GPSS OPPORTUNITIES`

**Add these 14 new fields:**

| Field Name | Type | Configuration |
|-----------|------|---------------|
| **Go/No-Go Score** | Number | Integer, 0-50 range |
| **Relationship Strength** | Number | Integer, 0-10 range |
| **Price Competitiveness** | Number | Integer, 0-10 range |
| **Technical Capability** | Number | Integer, 0-10 range |
| **Resource Availability** | Number | Integer, 0-10 range |
| **Past Performance Score** | Number | Integer, 0-10 range |
| **Strategic Recommendation** | Single Select | Options: Skip, Maybe, Pursue |
| **Win Probability** | Percent | 0-100% |
| **Evaluator Style Primary** | Single Select | Options: Analytical, Driver, Expressive, Amiable |
| **Evaluator Style Secondary** | Single Select | Options: Analytical, Driver, Expressive, Amiable |
| **Evaluator Confidence** | Number | Integer, 0-100 |
| **Selected Win Themes** | Multiple Select | Options: (will be populated from library) |
| **Strategic Notes** | Long Text | Auto-generated strategy recommendations |
| **Strategic Analysis Date** | Date | Auto-populated timestamp |

---

### **Step-by-Step Instructions:**

1. **Open your NEXUS Airtable base**
2. **Navigate to GPSS OPPORTUNITIES table**
3. **Click the "+" button** to add new fields
4. **Create each field** according to the table above

**Example for "Go/No-Go Score":**
- Field Name: `Go/No-Go Score`
- Field Type: Number
- Number Format: Integer
- Precision: 0 decimal places
- Allow negative numbers: No

**Example for "Strategic Recommendation":**
- Field Name: `Strategic Recommendation`
- Field Type: Single Select
- Options:
  - Skip (red)
  - Maybe (yellow)
  - Pursue (green)

**Example for "Evaluator Style Primary":**
- Field Name: `Evaluator Style Primary`
- Field Type: Single Select
- Options:
  - Analytical
  - Driver
  - Expressive
  - Amiable

---

## 🆕 PART 2: CREATE NEW TABLE (WIN THEMES LIBRARY)

### **Table:** `WIN THEMES LIBRARY`

**Create this new table with 13 fields:**

| Field Name | Type | Configuration | Description |
|-----------|------|---------------|-------------|
| **Theme ID** | Auto Number | Starting at 1 | Unique identifier |
| **Theme Name** | Single Line Text | Required | e.g., "Michigan EDWOSB" |
| **Theme Description** | Long Text | Rich text | Full explanation |
| **Theme Category** | Single Select | Options below | Type of advantage |
| **Talking Points** | Long Text | Rich text | Bullet points to weave in |
| **Strength Rating** | Rating | 1-5 stars | How strong is this advantage? |
| **Applicable Industries** | Multiple Select | Options below | Which industries? |
| **Active** | Checkbox | Default: checked | Is theme currently active? |
| **Created Date** | Created Time | Auto | When was theme created? |
| **Last Used** | Date | Manual update | When last used in bid? |
| **Times Used** | Number | Integer | Count of uses |
| **Win Rate When Used** | Percent | 0-100% | % of wins when this theme used |
| **Notes** | Long Text | Optional | Internal notes |

**Theme Category Options:**
- Certification (EDWOSB, HUBZone, etc.)
- Location (Local, Michigan-based, etc.)
- Service (Responsive, flexible, etc.)
- Experience (Past performance, expertise, etc.)
- Pricing (Competitive, value-based, etc.)

**Applicable Industries Options:**
- Government
- Federal
- State
- Municipal
- Construction
- Industrial
- Healthcare
- All

---

### **Step-by-Step Instructions:**

1. **Click "+ Add or Import" button** in left sidebar
2. **Select "Create empty table"**
3. **Name it:** `WIN THEMES LIBRARY`
4. **Delete default fields** (keep only "Name" field initially)
5. **Rename "Name"** field to **"Theme Name"**
6. **Add remaining 12 fields** according to table above

---

## 🆕 PART 3: CREATE NEW TABLE (EVALUATOR PROFILES)

### **Table:** `EVALUATOR PROFILES`

**Create this new table with 8 fields:**

| Field Name | Type | Configuration | Description |
|-----------|------|---------------|-------------|
| **Profile ID** | Auto Number | Starting at 1 | Unique identifier |
| **Agency Name** | Single Line Text | Required | e.g., "City of Detroit" |
| **Officer Name** | Single Line Text | Optional | Procurement officer if known |
| **Detected Style** | Single Select | See options below | AI-detected style |
| **Confidence Score** | Number | Integer, 0-100 | How confident in detection? |
| **RFP Text Analyzed** | Long Text | First 5000 chars | Sample of RFP analyzed |
| **Detection Date** | Created Time | Auto | When was analysis run? |
| **Linked Opportunity** | Link to GPSS OPPORTUNITIES | Multiple allowed | Which opportunity(ies)? |

**Detected Style Options:**
- Analytical
- Driver
- Expressive
- Amiable
- Mixed

---

## 🆕 PART 4: CREATE NEW TABLE (BID DEBRIEFS)

### **Table:** `BID DEBRIEFS`

**Create this new table with 19 fields:**

| Field Name | Type | Configuration | Description |
|-----------|------|---------------|-------------|
| **Debrief ID** | Auto Number | Starting at 1 | Unique identifier |
| **Opportunity** | Link to GPSS OPPORTUNITIES | Single link | Which opportunity? |
| **Outcome** | Single Select | Won, Lost | Bid result |
| **Award Amount** | Currency | USD | Actual contract value |
| **Our Bid Amount** | Currency | USD | What we bid |
| **Price Difference %** | Percent | Formula | Calculated difference |
| **Win/Loss Factors** | Long Text | Rich text | What went right/wrong? |
| **Procurement Feedback** | Long Text | Rich text | Feedback from officer |
| **Pricing Feedback** | Long Text | Optional | Comments on price |
| **Proposal Quality Feedback** | Long Text | Optional | Comments on proposal |
| **Relationship Factor** | Single Select | See options | How important was relationship? |
| **ProposalBio Score** | Number | 0-100 | From linked proposal |
| **Strategic Score** | Number | 0-50 | From linked opportunity |
| **Lessons Learned** | Long Text | Rich text | Key takeaways |
| **Debrief Date** | Date | Manual | When debrief conducted |
| **Debrief Source** | Single Select | See options | Who provided feedback? |
| **Follow-up Actions** | Long Text | Optional | Next steps from debrief |
| **Tags** | Multiple Select | Custom tags | For categorization |
| **Created** | Created Time | Auto | When record created |

**Relationship Factor Options:**
- Critical (relationship was deciding factor)
- Helpful (relationship helped but not deciding)
- Neutral (relationship didn't matter)
- Not Factor (no relationship existed)

**Debrief Source Options:**
- Procurement Officer
- Internal Team Only
- Both
- Third Party

**Price Difference % Formula:**
```
IF(
  AND({Our Bid Amount}, {Award Amount}),
  ({Our Bid Amount} - {Award Amount}) / {Award Amount},
  0
)
```

---

## 🔗 PART 5: UPDATE RELATIONSHIPS

### **Update Multiple Select in GPSS OPPORTUNITIES:**

1. Go back to **GPSS OPPORTUNITIES** table
2. Find **"Selected Win Themes"** field
3. Click to edit field
4. Add these options (or sync with WIN THEMES LIBRARY):
   - Michigan EDWOSB Certified
   - Local Michigan Supplier
   - Responsive Direct Communication
   - Government Compliance Expert
   - Small Business Flexibility
   - Proven Past Performance
   - (Add more as themes are created)

---

## 🎨 PART 6: CREATE VIEWS (OPTIONAL BUT RECOMMENDED)

### **In GPSS OPPORTUNITIES:**

**View 1: "Strategic Pipeline"**
- Filter: `Strategic Recommendation` = "Pursue"
- Sort: `Go/No-Go Score` (highest first)
- Group by: `Strategic Recommendation`
- Show: Opportunity Name, Agency, Go/No-Go Score, Win Probability, Deadline

**View 2: "High Confidence Bids"**
- Filter: `Go/No-Go Score` >= 35 AND `Evaluator Confidence` >= 70
- Sort: `Win Probability` (highest first)

**View 3: "Need Strategic Analysis"**
- Filter: `Strategic Analysis Date` is empty
- Sort: `Deadline` (soonest first)

---

### **In WIN THEMES LIBRARY:**

**View 1: "Active Themes"**
- Filter: `Active` is checked
- Sort: `Win Rate When Used` (highest first)
- Group by: `Theme Category`

**View 2: "Most Effective"**
- Filter: `Active` is checked AND `Times Used` >= 3
- Sort: `Win Rate When Used` (highest first)

---

### **In BID DEBRIEFS:**

**View 1: "Recent Debriefs"**
- Sort: `Debrief Date` (newest first)
- Group by: `Outcome` (Won/Lost)

**View 2: "Lessons Learned Dashboard"**
- Sort: `Created` (newest first)
- Show: Opportunity, Outcome, Win/Loss Factors, Lessons Learned

---

## ✅ PART 7: INITIALIZE WIN THEMES LIBRARY

**Option A: Automatic (Recommended)**

Run the initialization script:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python strategic_analysis_module.py
```

This will automatically create 6 default win themes for Dee Davis Inc.

**Option B: Manual**

Create these 6 records manually in WIN THEMES LIBRARY:

### **Theme 1: Michigan EDWOSB Certified**
- **Theme Name:** Michigan EDWOSB Certified
- **Description:** Certified woman-owned small business (EDWOSB) based in Michigan with federal certifications
- **Category:** Certification
- **Talking Points:**
  ```
  - EDWOSB certified - eligible for federal set-asides and preferences
  - Supports small business and diversity goals
  - Michigan-based for local/regional preference
  - Registered in SAM.gov with active certifications
  ```
- **Strength Rating:** 5 stars
- **Applicable Industries:** Government, Federal, State, Municipal
- **Active:** ✅ Checked

### **Theme 2: Local Michigan Supplier**
- **Theme Name:** Local Michigan Supplier
- **Description:** Michigan-based supplier providing faster delivery and lower freight costs
- **Category:** Location
- **Talking Points:**
  ```
  - Lower freight costs than out-of-state suppliers (15-30% savings)
  - Faster delivery times - 1-3 days vs 1-2 weeks
  - Support local Michigan economy and jobs
  - Available for in-person meetings and site visits
  ```
- **Strength Rating:** 4 stars
- **Applicable Industries:** Government, Construction, Industrial
- **Active:** ✅ Checked

### **Theme 3: Responsive Direct Communication**
- **Theme Name:** Responsive Direct Communication
- **Description:** Direct access to business owner with no corporate bureaucracy
- **Category:** Service
- **Talking Points:**
  ```
  - Direct communication with business ownership
  - No corporate red tape or multiple approval layers
  - Quick decisions and rapid problem resolution
  - Personal accountability and relationship continuity
  ```
- **Strength Rating:** 4 stars
- **Applicable Industries:** Government, All
- **Active:** ✅ Checked

### **Theme 4: Government Compliance Expert**
- **Theme Name:** Government Compliance Expert
- **Description:** Deep understanding of public sector procurement requirements
- **Category:** Experience
- **Talking Points:**
  ```
  - Experienced with government contracting requirements
  - SAM.gov registered and fully compliant
  - Understand public procurement processes and timelines
  - Familiar with federal, state, and municipal regulations
  ```
- **Strength Rating:** 4 stars
- **Applicable Industries:** Government, Federal, State, Municipal
- **Active:** ✅ Checked

### **Theme 5: Small Business Flexibility**
- **Theme Name:** Small Business Flexibility
- **Description:** Agile and adaptable to accommodate unique agency requirements
- **Category:** Service
- **Talking Points:**
  ```
  - Flexible to accommodate special requirements
  - Not locked into rigid corporate policies
  - Can customize solutions to specific needs
  - Willing to work with agency processes and preferences
  ```
- **Strength Rating:** 3 stars
- **Applicable Industries:** Government, All
- **Active:** ✅ Checked

### **Theme 6: Proven Past Performance**
- **Theme Name:** Proven Past Performance
- **Description:** Track record of successful contract delivery to similar agencies
- **Category:** Experience
- **Talking Points:**
  ```
  - Successfully delivered similar contracts
  - Positive references from government clients
  - On-time delivery and budget compliance
  - Lessons learned from past projects applied to new work
  ```
- **Strength Rating:** 5 stars
- **Applicable Industries:** Government, All
- **Active:** ✅ Checked

---

## ✅ VERIFICATION CHECKLIST

After completing setup, verify:

- [ ] GPSS OPPORTUNITIES has all 14 new strategic fields
- [ ] WIN THEMES LIBRARY table exists with 13 fields
- [ ] EVALUATOR PROFILES table exists with 8 fields
- [ ] BID DEBRIEFS table exists with 19 fields
- [ ] WIN THEMES LIBRARY has 6 default themes created
- [ ] Selected Win Themes options populated in GPSS OPPORTUNITIES
- [ ] Views created for easier navigation
- [ ] All link fields properly connected between tables

---

## 🚀 NEXT STEPS

Once Airtable setup is complete:

1. ✅ **Test the system** with a real opportunity
2. ✅ **Run Go/No-Go analysis** on upcoming bids
3. ✅ **Analyze evaluator styles** from recent RFPs
4. ✅ **Review and customize** win themes for your business
5. ✅ **Start collecting** debrief data after bids

---

## 📚 RELATED DOCUMENTATION

- `RFP_SUCCESS_STRATEGIC_MODULE_IMPLEMENTATION.md` - Full implementation details
- `strategic_analysis_module.py` - Backend service code
- `api_server.py` - API endpoints (lines 4160-4360)

---

## 🆘 TROUBLESHOOTING

**Problem:** "Can't find GPSS OPPORTUNITIES table"
- **Solution:** Check base name - should be your main NEXUS base

**Problem:** "Script says 'table not found'"
- **Solution:** Table names are case-sensitive. Match exactly: `WIN THEMES LIBRARY`

**Problem:** "Link field not connecting"
- **Solution:** Ensure both tables exist before creating link. Re-create link field if needed.

**Problem:** "Views not showing correct data"
- **Solution:** Check filter formulas. Ensure field names match exactly.

---

## 💡 TIPS

1. **Start with GPSS OPPORTUNITIES fields first** - These are the most critical
2. **Use automatic initialization** for win themes - Saves time and ensures consistency
3. **Create views as you go** - Makes it easier to verify setup is working
4. **Test with one opportunity** before rolling out to all bids
5. **Customize win themes** to match YOUR unique advantages

---

**Setup Time:** 15-20 minutes  
**Complexity:** Medium (straightforward if following step-by-step)  
**Impact:** HIGH - Transforms NEXUS from tactical tool to strategic system

---

*Ready to start? Begin with Part 1: Update GPSS OPPORTUNITIES table!*
