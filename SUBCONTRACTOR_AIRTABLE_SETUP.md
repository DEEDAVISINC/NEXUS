# SUBCONTRACTOR SYSTEM - AIRTABLE SETUP

**Purpose:** Set up tables for finding, quoting, and managing subcontractors in each contract area

---

## 📋 TABLE 1: `GPSS SUBCONTRACTORS`

**Purpose:** Database of subcontractors in various locations you can partner with

### Required Fields:

```
COMPANY NAME (Single line text) - Primary field
SERVICE TYPE (Single select or text) - e.g., "Aircraft Wash", "Janitorial", "IT Support"
CITY (Single line text)
STATE (Single select) - All 50 states
PHONE (Phone number)
EMAIL (Email)
WEBSITE (URL)
DESCRIPTION (Long text)
DISCOVERY METHOD (Single select)
  - Google Search
  - Referral
  - LinkedIn
  - Manual Entry
DISCOVERY DATE (Date)
DISCOVERED BY (Single select)
  - NEXUS Auto-Mining
  - [Your name]
RELATIONSHIP STATUS (Single select)
  - Cold (not contacted yet)
  - Contacted (RFQ sent)
  - Active Partner (working together)
  - Preferred (great experience)
RELIABILITY RATING (Rating 0-5 stars)
RESPONSE RATE (%) (Number - percentage)
CONTRACTS WON TOGETHER (Number)
LAST CONTACTED (Date)
SOURCE NOTES (Long text)
NOTES (Long text)
CREATED DATE (Created time) - Auto
LAST MODIFIED (Last modified time) - Auto
```

---

## 📋 TABLE 2: `GPSS SUBCONTRACTOR QUOTES`

**Purpose:** Track quote requests and responses from subcontractors

### Required Fields:

```
QUOTE ID (Auto number) - Primary field
OPPORTUNITY (Link to Opportunities table)
PROVIDER (Link to GPSS SERVICE PROVIDERS table)
STATUS (Single select)
  - RFQ Sent
  - Quote Received
  - Selected
  - Rejected
  - Expired
RFQ SENT DATE (Date)
QUOTE DUE DATE (Date)
EMAIL SUBJECT (Single line text)
EMAIL BODY (Long text)
RESPONSE TEXT (Long text) - Their quote response
QUOTE AMOUNT (Currency)
RESPONSE TIME (DAYS) (Number)
AI SCORE (Number 0-100)
SCORE REASONING (Long text)
RECOMMENDATION (Single select)
  - Recommend
  - Consider
  - Pass
SELECTED (Checkbox) - Mark the winning quote
MARKUP PERCENTAGE (Number)
MARKUP AMOUNT (Currency)
FINAL BID AMOUNT (Currency)
ESTIMATED PROFIT (Currency)
NOTES (Long text)
CREATED DATE (Created time) - Auto
```

---

## 📋 TABLE 3 (OPTIONAL): Update `Opportunities` Table

**Add these fields to your existing Opportunities table:**

```
SERVICE TYPE (Single line text) - e.g., "Aircraft Wash", "Janitorial Services"
LOCATION (Single line text) - e.g., "Virginia Beach, VA"
SCOPE OF WORK (Long text) - What needs to be done
```

---

## ⚙️ QUICK SETUP STEPS:

### Step 1: Create Tables

1. Go to your NEXUS Airtable base
2. Click "+" to add new table
3. Name it: `GPSS SUBCONTRACTORS`
4. Add all fields listed above (copy/paste field names)
5. Set field types correctly (Single line text, Number, Date, etc.)
6. Repeat for `GPSS SUBCONTRACTOR QUOTES`

### Step 2: Link Tables

1. In `GPSS SUBCONTRACTOR QUOTES`:
   - The "OPPORTUNITY" field should link to your `Opportunities` table
   - The "SUBCONTRACTOR" field should link to `GPSS SUBCONTRACTORS` table

### Step 3: Test

1. Manually add one test subcontractor to `GPSS SUBCONTRACTORS`:
   ```
   Company Name: Test Subcontractor Inc
   Service Type: Janitorial
   City: Detroit
   State: MI
   Email: test@example.com
   Discovery Method: Manual Entry
   Relationship Status: Cold
   ```

2. Save and verify you can see the record

---

## 🎯 WHAT EACH TABLE DOES:

### `GPSS SUBCONTRACTORS`
- Stores all subcontractors you've found in various locations
- Built automatically by Google search OR manually added
- Tracks relationship history (how many contracts won together, reliability rating)

### `GPSS SUBCONTRACTOR QUOTES`
- One record per subcontractor per opportunity
- Tracks RFQ emails sent
- Stores their quote responses
- AI scores each quote 0-100
- Marks which quote you selected
- Calculates final bid with your markup

---

## 🔄 TYPICAL WORKFLOW:

```
1. NEXUS finds opportunity in Virginia Beach
   ↓
2. System searches Google for "aircraft wash Virginia Beach"
   ↓
3. Finds 8 subcontractors → Auto-adds to GPSS SUBCONTRACTORS
   ↓
4. You select 4-5 to contact
   ↓
5. System generates RFQ emails → Creates records in GPSS SUBCONTRACTOR QUOTES
   ↓
6. Subcontractors respond (you paste their responses into RESPONSE TEXT field)
   ↓
7. AI scores all quotes 0-100 → Updates AI SCORE in GPSS SUBCONTRACTOR QUOTES
   ↓
8. You select best quote → Mark SELECTED = true
   ↓
9. System calculates markup → Updates FINAL BID AMOUNT
   ↓
10. You submit bid using final amount
```

---

## 📊 VIEWS TO CREATE:

### In `GPSS SUBCONTRACTORS`:

**View 1: "Active Partners"**
- Filter: RELATIONSHIP STATUS = "Active Partner" OR "Preferred"
- Sort: CONTRACTS WON TOGETHER (descending)

**View 2: "By Location"**
- Group by: STATE
- Sort: RELIABILITY RATING (descending)

**View 3: "By Service Type"**
- Group by: SERVICE TYPE
- Sort: CONTRACTS WON TOGETHER (descending)

### In `GPSS SUBCONTRACTOR QUOTES`:

**View 1: "Pending Quotes"**
- Filter: STATUS = "RFQ Sent"
- Sort: QUOTE DUE DATE (ascending)

**View 2: "Scored Quotes"**
- Filter: AI SCORE > 0
- Sort: AI SCORE (descending)

**View 3: "Selected Quotes"**
- Filter: SELECTED = true
- Sort: CREATED DATE (descending)

---

## 🚀 READY TO USE!

Once tables are set up, you can:

1. **Find Subcontractors:** Use `/gpss/subcontractors/find` API
2. **Send RFQs:** Use `/gpss/subcontractors/rfq/send-bulk` API
3. **Score Quotes:** Use `/gpss/subcontractors/quotes/score-all` API
4. **Calculate Bid:** Use `/gpss/subcontractors/bid/summary` API

**All accessible from NEXUS frontend (coming next!)**

---

**Setup time: 10-15 minutes**  
**Payoff: Find and quote subcontractors in minutes instead of hours**
