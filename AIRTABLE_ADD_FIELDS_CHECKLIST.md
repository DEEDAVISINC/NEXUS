# ✅ AIRTABLE FIELDS - SIMPLE ADD CHECKLIST

**Table:** GPSS OPPORTUNITIES  
**Goal:** Add fields to support federal forecasts system

---

## 🎯 PRIORITY 1 FIELDS (Add These First - 15 fields)

### Basic Info
- [ ] **Agency Name** → Single line text
- [ ] **Description** → Long text  
- [ ] **Posted Date** → Date

### Classification
- [ ] **NAICS Code** → Single line text
- [ ] **Set-Aside Type** → Single select
  - Add options: Unrestricted, WOSB, EDWOSB, 8(a), HUBZone, SDVOSB, Small Business
- [ ] **Estimated Value** → Currency

### Location
- [ ] **State** → Single line text
- [ ] **Contact Email** → Email

### Source
- [ ] **Source URL** → URL
- [ ] **Notice Type** → Single select
  - Add options: Pre-Solicitation, Sources Sought, Forecast, Contract Renewal, Solicitation
- [ ] **Forecast Type** → Single line text

### Analysis
- [ ] **AI Fit Score** → Number (0-100)
- [ ] **Pursuit Status** → Single select
  - Add options: New, Reviewing, Pursuing, Preparing Bid, Submitted, Won, Lost, Passed
- [ ] **Priority** → Single select
  - Add options: 🔥 High, ⚡ Medium, 📋 Low
- [ ] **Notes** → Long text

---

## 📋 PRIORITY 2 FIELDS (Add These Next - 10 fields)

### More Details
- [ ] **Sub Agency** → Single line text
- [ ] **Category** → Single select
  - Add options: Federal Forecast, State/Local, Pre-Solicitation, Active Bid
- [ ] **City** → Single line text
- [ ] **Contact Name** → Single line text

### More Dates
- [ ] **Response Deadline** → Date
- [ ] **Estimated Solicitation Date** → Date
- [ ] **Date Added to NEXUS** → Created time (auto-populated)
- [ ] **Last Updated** → Last modified time (auto-populated)

### More Analysis
- [ ] **Win Probability** → Percent
- [ ] **Assigned To** → Single line text

---

## 🔧 PRIORITY 3 FIELDS (Add When Ready - 10 fields)

### Supplier Tracking
- [ ] **Suppliers Identified** → Checkbox
- [ ] **Quotes Requested** → Checkbox
- [ ] **Quotes Received** → Number
- [ ] **Bid Prepared** → Checkbox
- [ ] **Submitted Date** → Date

### Financial
- [ ] **Estimated Profit** → Currency
- [ ] **Profit Margin** → Percent
- [ ] **Our Bid Amount** → Currency
- [ ] **Value Range** → Single select
  - Add options: $0-$100K, $100K-$500K, $500K-$1M, $1M-$5M, $5M+

### Other
- [ ] **Prime Contractor** → Single line text

---

## 📱 HOW TO ADD FIELDS IN AIRTABLE

1. Open your Airtable base
2. Go to `GPSS OPPORTUNITIES` table
3. Click **+** button at the right side of the last column
4. Choose field type
5. Name the field (exact name from checklist)
6. For Single select fields:
   - Click "Add option"
   - Add each option listed
   - Set default if specified
7. Click **Create field**
8. Repeat for each field

---

## 🎨 RECOMMENDED VIEWS TO CREATE AFTER

Once fields are added, create these views:

### 1. Federal Forecasts
- Filter: `Source Status` contains "SAM.gov"
- Sort: `Posted Date` (newest first)
- Group by: `Agency Name`

### 2. High Priority
- Filter: `Priority` = 🔥 High
- Sort: `Deadline` (soonest first)

### 3. EDWOSB Only
- Filter: `Set-Aside Type` = EDWOSB OR WOSB
- Sort: `Estimated Value` (highest first)

### 4. Pursuing Now
- Filter: `Pursuit Status` = Reviewing OR Pursuing
- Sort: `Deadline` (soonest first)

---

## ⚡ QUICK START (Minimal Setup)

**If you want to start FAST, add just these 8 fields:**

1. Agency Name (Single line text)
2. Description (Long text)
3. Set-Aside Type (Single select: Unrestricted, WOSB, EDWOSB)
4. Estimated Value (Currency)
5. Source URL (URL)
6. Pursuit Status (Single select: New, Pursuing, Passed)
7. Priority (Single select: High, Medium, Low)
8. Notes (Long text)

**Then run the miner and you'll have enough to work with!**

---

## 🔄 UPDATE THE MINER AFTER ADDING FIELDS

Once you've added the fields, update this file:

`/Users/deedavis/NEXUS BACKEND/mine_real_federal_forecasts.py`

Find the `store_forecasts` method and update the field mapping to include the new fields you added.

---

**Questions? Check:** `AIRTABLE_FIELDS_TO_ADD_NOW.md` for full details.
