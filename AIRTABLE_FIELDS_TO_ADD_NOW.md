# AIRTABLE FIELDS TO ADD - FEDERAL FORECASTS SYSTEM

**Table:** `GPSS OPPORTUNITIES`  
**Current Fields:** 5  
**Fields to Add:** 20+

---

## ✅ CURRENT FIELDS (Keep These)

1. **Name** - Single line text
2. **RFP NUMBER** - Single line text
3. **Deadline** - Date
4. **Source Status** - Single line text
5. **HIGH VALUE FLAG** - Checkbox

---

## ➕ FIELDS TO ADD

### **Basic Information**

6. **Agency Name** - Single line text
   - Example: "Department of Defense", "GSA", "NASA"

7. **Sub Agency** - Single line text
   - Example: "Army Corps of Engineers", "GSA Region 5"

8. **Description** - Long text
   - Full description of the opportunity

9. **Posted Date** - Date
   - When the forecast/opportunity was posted

10. **Category** - Single select
    - Options: Federal Forecast, State/Local, Pre-Solicitation, Active Bid
    - Default: Federal Forecast

---

### **Classification & Requirements**

11. **NAICS Code** - Single line text
    - Example: "541330", "334111"

12. **Set-Aside Type** - Single select
    - Options: 
      - Unrestricted
      - WOSB
      - EDWOSB
      - 8(a)
      - HUBZone
      - SDVOSB
      - Small Business
    - Default: Unrestricted

13. **Estimated Value** - Currency
    - Estimated contract value
    - Format: $0.00

14. **Value Range** - Single select
    - Options: $0-$100K, $100K-$500K, $500K-$1M, $1M-$5M, $5M+
    - Auto-calculated based on Estimated Value

---

### **Location & Contact**

15. **State** - Single line text
    - Place of performance state
    - Example: "Michigan", "Illinois", "Federal"

16. **City** - Single line text
    - Place of performance city

17. **Contact Name** - Single line text
    - Primary contact for the opportunity

18. **Contact Email** - Email
    - Contact email address

19. **Contact Phone** - Phone number
    - Contact phone number

---

### **Source & Tracking**

20. **Source URL** - URL
    - Direct link to the opportunity
    - Example: https://sam.gov/opp/12345

21. **Notice Type** - Single select
    - Options:
      - Pre-Solicitation
      - Sources Sought
      - Forecast
      - Contract Renewal
      - Solicitation
      - Amendment
    - Default: Forecast

22. **Forecast Type** - Single line text
    - Specific type from source
    - Example: "Near-Term Pre-Solicitation", "Contract Renewal Forecast"

---

### **Dates & Deadlines**

23. **Response Deadline** - Date
    - For pre-solicitations that have response dates

24. **Estimated Solicitation Date** - Date
    - When the actual solicitation is expected to be posted

25. **Date Added to NEXUS** - Created time
    - Auto-populated when record is created

26. **Last Updated** - Last modified time
    - Auto-updated when record changes

---

### **Analysis & Workflow**

27. **AI Fit Score** - Number (0-100)
    - AI-calculated fit score for Dee Davis Inc
    - 0-100 scale

28. **Win Probability** - Percent
    - Estimated win probability
    - 0-100%

29. **Pursuit Status** - Single select
    - Options:
      - New
      - Reviewing
      - Pursuing
      - Preparing Bid
      - Submitted
      - Won
      - Lost
      - Passed
    - Default: New

30. **Priority** - Single select
    - Options: 🔥 High, ⚡ Medium, 📋 Low
    - Default: Medium

31. **Assigned To** - Single line text
    - Who's responsible for this opportunity

32. **Notes** - Long text
    - Internal notes and strategy

---

### **Supplier & Bidding**

33. **Suppliers Identified** - Checkbox
    - Whether suppliers have been identified

34. **Quotes Requested** - Checkbox
    - Whether quotes have been requested

35. **Quotes Received** - Number
    - How many quotes received

36. **Bid Prepared** - Checkbox
    - Whether bid package is ready

37. **Submitted Date** - Date
    - When bid was submitted

---

### **Financial Tracking**

38. **Estimated Profit** - Currency
    - Estimated profit if won
    - Format: $0.00

39. **Profit Margin** - Percent
    - Estimated profit margin
    - Example: 15%

40. **Our Bid Amount** - Currency
    - Amount we bid
    - Format: $0.00

---

### **Links & Relationships**

41. **Related Documents** - Attachment
    - RFP PDFs, bid documents, etc.

42. **Supplier Quotes** - Link to another record
    - Links to "Suppliers" table (if you have one)

43. **Prime Contractor** - Single line text
    - If bidding as sub, who's the prime?

---

## 📊 RECOMMENDED VIEWS TO CREATE

### 1. **Federal Forecasts View**
- Filter: `Source Status` contains "SAM.gov" OR "USASpending"
- Sort: `Posted Date` (newest first)
- Group by: `Agency Name`

### 2. **High Priority View**
- Filter: `Priority` = 🔥 High AND `Pursuit Status` ≠ Lost, Passed
- Sort: `Deadline` (soonest first)

### 3. **EDWOSB Opportunities**
- Filter: `Set-Aside Type` = EDWOSB OR WOSB
- Sort: `Estimated Value` (highest first)

### 4. **Needs Action View**
- Filter: `Pursuit Status` = Reviewing OR Pursuing
- Sort: `Deadline` (soonest first)

### 5. **Won Bids**
- Filter: `Pursuit Status` = Won
- Sort: `Submitted Date` (newest first)

### 6. **By State View**
- Group by: `State`
- Sort: `Deadline` (soonest first)

---

## 🔄 AUTOMATIONS TO CREATE

### 1. **New Forecast Alert**
When: Record created
Condition: `Source Status` contains "Forecast"
Action: Send email notification

### 2. **Deadline Reminder (7 days)**
When: 7 days before `Deadline`
Condition: `Pursuit Status` = Pursuing
Action: Send reminder email

### 3. **Deadline Reminder (48 hours)**
When: 2 days before `Deadline`
Condition: `Pursuit Status` = Preparing Bid
Action: Send urgent reminder

### 4. **High Value Alert**
When: Record created
Condition: `Estimated Value` > $500,000
Action: Send priority email

### 5. **Auto-assign Priority**
When: Record created or `AI Fit Score` updated
Condition: 
- `AI Fit Score` > 80 → Priority = High
- `AI Fit Score` 50-80 → Priority = Medium
- `AI Fit Score` < 50 → Priority = Low

---

## 📝 QUICK SETUP CHECKLIST

In Airtable, for `GPSS OPPORTUNITIES` table:

### Step 1: Add Basic Fields
- [ ] Agency Name (Single line text)
- [ ] Sub Agency (Single line text)
- [ ] Description (Long text)
- [ ] Posted Date (Date)
- [ ] Category (Single select)

### Step 2: Add Classification Fields
- [ ] NAICS Code (Single line text)
- [ ] Set-Aside Type (Single select with options)
- [ ] Estimated Value (Currency)
- [ ] Value Range (Single select)

### Step 3: Add Location & Contact
- [ ] State (Single line text)
- [ ] City (Single line text)
- [ ] Contact Name (Single line text)
- [ ] Contact Email (Email)
- [ ] Contact Phone (Phone)

### Step 4: Add Source & Tracking
- [ ] Source URL (URL)
- [ ] Notice Type (Single select)
- [ ] Forecast Type (Single line text)
- [ ] Date Added to NEXUS (Created time)
- [ ] Last Updated (Last modified time)

### Step 5: Add Analysis Fields
- [ ] AI Fit Score (Number, 0-100)
- [ ] Win Probability (Percent)
- [ ] Pursuit Status (Single select with options)
- [ ] Priority (Single select)
- [ ] Assigned To (Single line text)
- [ ] Notes (Long text)

### Step 6: Add Supplier & Bid Tracking
- [ ] Suppliers Identified (Checkbox)
- [ ] Quotes Requested (Checkbox)
- [ ] Quotes Received (Number)
- [ ] Bid Prepared (Checkbox)
- [ ] Submitted Date (Date)

### Step 7: Add Financial Fields
- [ ] Estimated Profit (Currency)
- [ ] Profit Margin (Percent)
- [ ] Our Bid Amount (Currency)

### Step 8: Add Relationships
- [ ] Related Documents (Attachment)
- [ ] Prime Contractor (Single line text)

### Step 9: Create Views
- [ ] Federal Forecasts View
- [ ] High Priority View
- [ ] EDWOSB Opportunities View
- [ ] Needs Action View
- [ ] Won Bids View
- [ ] By State View

### Step 10: Set Up Automations
- [ ] New Forecast Alert
- [ ] Deadline Reminder (7 days)
- [ ] Deadline Reminder (48 hours)
- [ ] High Value Alert
- [ ] Auto-assign Priority

---

## 🎯 PRIORITY FIELDS (Add These First)

If you want to start simple, add these 15 essential fields first:

1. **Agency Name** - Single line text
2. **Description** - Long text
3. **NAICS Code** - Single line text
4. **Set-Aside Type** - Single select
5. **Estimated Value** - Currency
6. **State** - Single line text
7. **Contact Email** - Email
8. **Source URL** - URL
9. **Notice Type** - Single select
10. **Forecast Type** - Single line text
11. **AI Fit Score** - Number
12. **Pursuit Status** - Single select
13. **Priority** - Single select
14. **Posted Date** - Date
15. **Notes** - Long text

Then add the rest as needed.

---

**Once these fields are added, the federal forecasts miner will automatically populate them!**
