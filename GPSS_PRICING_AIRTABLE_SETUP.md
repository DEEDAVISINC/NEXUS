# GPSS INTELLIGENT PRICING - AIRTABLE SETUP GUIDE

## 🎯 **OVERVIEW:**
You'll create **3 new tables** in your GPSS Airtable base:
1. **Pricing History** (20 min)
2. **Cost Templates** (10 min)
3. **Market Intelligence** (10 min)

**Total Time: ~40 minutes**

---

# TABLE 1: PRICING HISTORY

## **Step 1: Create the Table**
1. In your GPSS Airtable base, click **"+ Add or import"**
2. Select **"Create empty table"**
3. Name it: **`Pricing History`**

## **Step 2: Rename First Field**
1. Click on "Name" field → **Rename to:** `Pricing ID`
2. Change type to: **Autonumber**

## **Step 3: Add All Fields**

### **Field 1: Opportunity**
- Type: **Link to another record**
- Link to table: **Opportunities**
- Allow linking to multiple records: **No**

### **Field 2: Proposal**
- Type: **Link to another record**
- Link to table: **GPSS Proposals**
- Allow linking to multiple records: **No**

### **Field 3: Contract Type**
- Type: **Single select**
- Options (add these 5):
  - `Fixed Price`
  - `Time & Materials`
  - `Cost Plus`
  - `IDIQ`
  - `BPA`

### **Field 4: Service Category**
- Type: **Single select**
- Options (add these 9):
  - `Project Management & Consulting`
  - `Healthcare Transportation & Diagnostics`
  - `Compliance & Credentialing`
  - `Notary & Settlement Services`
  - `Document Preparation & Corporate Services`
  - `Freight Brokerage & Logistics`
  - `Staffing & Recruitment`
  - `Emergency Equipment & Supplies (GPSS)`
  - `Technology & Software Development`

### **Field 5: Total Bid Amount**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 6: Estimated Costs**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 7: Labor Costs**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 8: Materials Costs**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 9: Overhead Rate**
- Type: **Percent**
- Precision: **2 decimal places**

### **Field 10: Profit Margin**
- Type: **Percent**
- Precision: **2 decimal places**

### **Field 11: Calculated Profit**
- Type: **Formula**
- Formula: `{Total Bid Amount} - {Estimated Costs}`
- Formatting: **Currency (USD)**

### **Field 12: Actual Profit Margin %**
- Type: **Formula**
- Formula: `IF({Total Bid Amount}, ({Calculated Profit} / {Total Bid Amount}) * 100, 0)`
- Formatting: **Percent (2 decimals)**

### **Field 13: Competitor Count**
- Type: **Number**
- Format: **Integer**

### **Field 14: Winning Bid Amount**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 15: Our Rank**
- Type: **Number**
- Format: **Integer**
- Description: "1 = We won"

### **Field 16: Win/Loss**
- Type: **Single select**
- Options (add these 4):
  - `Won` (green)
  - `Lost` (red)
  - `Pending` (yellow)
  - `No Bid` (gray)

### **Field 17: Win Probability Score**
- Type: **Number**
- Format: **Decimal (1 decimal place)**
- Description: "AI-calculated (0-100)"

### **Field 18: Price Competitiveness**
- Type: **Formula**
- Formula: `IF({Winning Bid Amount}, ({Total Bid Amount} / {Winning Bid Amount}) * 100, 0)`
- Formatting: **Percent (1 decimal)**

### **Field 19: Market Rate (per unit)**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **2 decimal places**

### **Field 20: Our Rate (per unit)**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **2 decimal places**

### **Field 21: Rate Variance %**
- Type: **Formula**
- Formula: `IF({Market Rate (per unit)}, (({Our Rate (per unit)} - {Market Rate (per unit)}) / {Market Rate (per unit)}) * 100, 0)`
- Formatting: **Percent (1 decimal)**

### **Field 22: Contract Duration (months)**
- Type: **Number**
- Format: **Integer**

### **Field 23: Annual Value**
- Type: **Formula**
- Formula: `IF({Contract Duration (months)}, {Total Bid Amount} / ({Contract Duration (months)} / 12), 0)`
- Formatting: **Currency (USD)**

### **Field 24: Agency**
- Type: **Single line text**

### **Field 25: Set-Aside Type**
- Type: **Single select**
- Options (add these 5):
  - `EDWOSB`
  - `8(a)`
  - `HUBZone`
  - `SDVOSB`
  - `Unrestricted`

### **Field 26: Geographic Region**
- Type: **Single select**
- Options (add these 7):
  - `Federal`
  - `MI`
  - `OH`
  - `IL`
  - `IN`
  - `WI`
  - `Other`

### **Field 27: Bid Date**
- Type: **Date**
- Include time: **No**

### **Field 28: Award Date**
- Type: **Date**
- Include time: **No**

### **Field 29: Pricing Strategy Used**
- Type: **Single select**
- Options (add these 5):
  - `Aggressive`
  - `Competitive`
  - `Premium`
  - `Cost-Plus`
  - `Market Rate`

### **Field 30: Pricing Notes**
- Type: **Long text**

### **Field 31: Lessons Learned**
- Type: **Long text**

### **Field 32: AI Pricing Recommendation**
- Type: **Long text**

### **Field 33: Followed AI Recommendation**
- Type: **Checkbox**

### **Field 34: Created Date**
- Type: **Created time**
- Include time: **Yes**

---

# TABLE 2: COST TEMPLATES

## **Step 1: Create the Table**
1. Click **"+ Add or import"** → **"Create empty table"**
2. Name it: **`Cost Templates`**

## **Step 2: Rename First Field**
1. Click on "Name" field → **Rename to:** `Template ID`
2. Change type to: **Autonumber**

## **Step 3: Add All Fields**

### **Field 1: Template Name**
- Type: **Single line text**
- Example: "NEMT - Full Service"

### **Field 2: Service Category**
- Type: **Single select**
- Options (add these 9 - same as Pricing History):
  - `Project Management & Consulting`
  - `Healthcare Transportation & Diagnostics`
  - `Compliance & Credentialing`
  - `Notary & Settlement Services`
  - `Document Preparation & Corporate Services`
  - `Freight Brokerage & Logistics`
  - `Staffing & Recruitment`
  - `Emergency Equipment & Supplies (GPSS)`
  - `Technology & Software Development`

### **Field 3: Base Hourly Rate**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **2 decimal places**

### **Field 4: Labor Cost per Hour**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **2 decimal places**

### **Field 5: Materials Cost %**
- Type: **Percent**
- Precision: **1 decimal place**

### **Field 6: Overhead Rate %**
- Type: **Percent**
- Precision: **1 decimal place**

### **Field 7: Target Profit Margin %**
- Type: **Percent**
- Precision: **1 decimal place**

### **Field 8: Minimum Margin %**
- Type: **Percent**
- Precision: **1 decimal place**

### **Field 9: Vehicles Required**
- Type: **Number**
- Format: **Integer**

### **Field 10: Staff Required**
- Type: **Number**
- Format: **Integer**
- Description: "FTE count"

### **Field 11: Certifications Needed**
- Type: **Long text**

### **Field 12: Typical Contract Duration**
- Type: **Number**
- Format: **Integer**
- Description: "Months"

### **Field 13: Pricing Formula**
- Type: **Long text**

### **Field 14: Last Updated**
- Type: **Last modified time**
- Include time: **Yes**

### **Field 15: Times Used**
- Type: **Number**
- Format: **Integer**
- Default: **0**

### **Field 16: Win Rate %**
- Type: **Number**
- Format: **Decimal (1 decimal place)**

---

# TABLE 3: MARKET INTELLIGENCE

## **Step 1: Create the Table**
1. Click **"+ Add or import"** → **"Create empty table"**
2. Name it: **`Market Intelligence`**

## **Step 2: Rename First Field**
1. Click on "Name" field → **Rename to:** `Intelligence ID`
2. Change type to: **Autonumber**

## **Step 3: Add All Fields**

### **Field 1: Service Type**
- Type: **Single select**
- Options (add these 9 - same as before):
  - `Project Management & Consulting`
  - `Healthcare Transportation & Diagnostics`
  - `Compliance & Credentialing`
  - `Notary & Settlement Services`
  - `Document Preparation & Corporate Services`
  - `Freight Brokerage & Logistics`
  - `Staffing & Recruitment`
  - `Emergency Equipment & Supplies (GPSS)`
  - `Technology & Software Development`

### **Field 2: Geographic Region**
- Type: **Single select**
- Options (add these 7 - same as Pricing History):
  - `Federal`
  - `MI`
  - `OH`
  - `IL`
  - `IN`
  - `WI`
  - `Other`

### **Field 3: Market Rate (Low)**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 4: Market Rate (Average)**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 5: Market Rate (High)**
- Type: **Currency**
- Format: **US Dollar (USD)**
- Precision: **0 decimal places**

### **Field 6: Data Source**
- Type: **Single line text**

### **Field 7: Competitor Name**
- Type: **Single line text**

### **Field 8: Date Observed**
- Type: **Date**
- Include time: **No**

### **Field 9: Contract Size**
- Type: **Single select**
- Options (add these 4):
  - `Small (<$250K)`
  - `Medium ($250K-$1M)`
  - `Large ($1M-$10M)`
  - `Mega (>$10M)`

### **Field 10: Set-Aside Type**
- Type: **Single select**
- Options (add these 5 - same as Pricing History):
  - `EDWOSB`
  - `8(a)`
  - `HUBZone`
  - `SDVOSB`
  - `Unrestricted`

### **Field 11: Notes**
- Type: **Long text**

### **Field 12: Confidence Level**
- Type: **Single select**
- Options (add these 3):
  - `High` (green)
  - `Medium` (yellow)
  - `Low` (red)

### **Field 13: Last Verified**
- Type: **Date**
- Include time: **No**

---

## 🎯 **CREATE VIEWS:**

### **For Pricing History Table:**
1. **All Bids** (default - already created)
2. **Wins Only**
   - Filter: Win/Loss = Won
3. **Losses Only**
   - Filter: Win/Loss = Lost
4. **By Service Category**
   - Group by: Service Category
5. **High Win Rate**
   - Filter: Win Probability Score > 70

### **For Cost Templates Table:**
1. **All Templates** (default - already created)
2. **High Win Rate**
   - Filter: Win Rate % > 60
3. **By Service**
   - Group by: Service Category

### **For Market Intelligence Table:**
1. **All Data** (default - already created)
2. **Recent (Last 6 Months)**
   - Filter: Date Observed is within the last 6 months
3. **High Confidence**
   - Filter: Confidence Level = High
4. **By Region**
   - Group by: Geographic Region

---

## ✅ **COMPLETION CHECKLIST:**

- [ ] Created **Pricing History** table (34 fields)
- [ ] Created **Cost Templates** table (16 fields)
- [ ] Created **Market Intelligence** table (13 fields)
- [ ] Set up all views for each table
- [ ] Verified all formulas work correctly
- [ ] Added sample data to test (optional but recommended)

---

## 🎉 **NEXT STEPS:**
Once you've completed these tables, we'll:
1. ✅ Build the AI Pricing Agent
2. ✅ Create the Pricing Calculator UI
3. ✅ Integrate with Proposal Generation
4. ✅ Add Pricing Analytics Dashboard

**Estimated time for Airtable setup: 40 minutes**
**Let me know when you're done and I'll start building the AI agent!** 🚀

