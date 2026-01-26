# 🚀 LOCAL PROVIDER SYSTEM - QUICK START

**3-Minute Setup → Start Finding Subcontractors**

---

## ⚡ SETUP (One Time - 10 Minutes):

### 1. Create Airtable Tables

**Go to your NEXUS Airtable base:**

**Table 1: `GPSS SERVICE PROVIDERS`**
```
Required fields (copy/paste these names):
- COMPANY NAME (text)
- SERVICE TYPE (text)
- CITY (text)
- STATE (text)
- PHONE (phone)
- EMAIL (email)
- WEBSITE (url)
- DISCOVERY METHOD (text)
- RELATIONSHIP STATUS (text)
- RELIABILITY RATING (rating 0-5)
- NOTES (long text)
```

**Table 2: `GPSS QUOTES`**
```
Required fields:
- QUOTE ID (autonumber)
- OPPORTUNITY (link to Opportunities table)
- PROVIDER (link to GPSS SERVICE PROVIDERS)
- STATUS (text)
- QUOTE AMOUNT (currency)
- AI SCORE (number)
- SELECTED (checkbox)
- FINAL BID AMOUNT (currency)
```

### 2. Deploy Backend

```bash
# Local:
cd ~/nexus-backend
git add .
git commit -m "Add local provider system"
git push

# PythonAnywhere:
# Go to Web tab → Reload deedavis.pythonanywhere.com
```

---

## 🎯 USAGE (Every Time):

### **Example: Aircraft Wash Contract in Virginia Beach**

#### **Step 1: Find Local Providers** (60 seconds)

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/local-providers/find \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "aircraft wash",
    "location": "Virginia Beach VA",
    "max_results": 8
  }'
```

**Result:** 8 local companies automatically added to Airtable

#### **Step 2: Generate RFQs** (2 minutes)

Go to Airtable `GPSS SERVICE PROVIDERS`:
- Note the record IDs of 4-5 best companies (e.g., rec123, rec456, rec789)

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/local-providers/rfq/send-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "YOUR_OPP_ID",
    "provider_ids": ["rec123", "rec456", "rec789", "rec890"],
    "scope": "Wash 200 aircraft per year at NAS Oceana. Services include exterior cleaning, degreasing, and waxing. 12-month contract."
  }'
```

**Result:** 4 professional RFQ emails generated → Copy/paste and send

#### **Step 3: Collect Quotes**

Providers email you back. For each response:
1. Go to Airtable `GPSS QUOTES`
2. Find the quote record
3. Paste their response into `RESPONSE TEXT` field
4. Enter their quote amount in `QUOTE AMOUNT` field

#### **Step 4: AI Score All Quotes** (30 seconds)

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/local-providers/quotes/score-all \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "YOUR_OPP_ID"
  }'
```

**Result:** Each quote scored 0-100, ranked best to worst

#### **Step 5: Calculate Final Bid** (10 seconds)

Check Airtable → Note the record ID of the top-scored quote

```bash
curl -X POST https://deedavis.pythonanywhere.com/gpss/local-providers/bid/summary \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "YOUR_OPP_ID",
    "selected_quote_id": "BEST_QUOTE_ID",
    "markup_percentage": 20
  }'
```

**Result:** Complete bid summary:
- Subcontractor cost: $150,000
- Your markup: $30,000
- **Final bid: $180,000**
- Profit: $22,000

#### **Step 6: Submit Proposal**

Use the final bid amount ($180,000) in your proposal!

---

## 📋 REAL EXAMPLE OUTPUT:

### Step 1 Response:
```json
{
  "success": true,
  "providers_found": 8,
  "providers": [
    {
      "COMPANY NAME": "ABC Aircraft Cleaning",
      "CITY": "Virginia Beach",
      "STATE": "VA",
      "WEBSITE": "https://abcaircraft.com",
      "PHONE": "(757) 555-0100"
    },
    ...
  ]
}
```

### Step 4 Response:
```json
{
  "success": true,
  "quotes_scored": 4,
  "ranked_quotes": [
    {
      "provider": "ABC Aircraft Cleaning",
      "quote_amount": 150000,
      "score": 92,
      "recommendation": "Recommend",
      "reasoning": "Excellent value, demonstrated experience at NAS Oceana..."
    },
    {
      "provider": "Coastal Aviation Services",
      "quote_amount": 155000,
      "score": 87,
      "recommendation": "Consider",
      "reasoning": "Good quote, slightly higher price but strong credentials..."
    }
  ]
}
```

### Step 5 Response:
```json
{
  "success": true,
  "opportunity_name": "Aircraft Wash Services - NAS Oceana",
  "selected_provider": "ABC Aircraft Cleaning",
  "subcontractor_quote": 150000,
  "your_markup": 30000,
  "final_bid": 180000,
  "estimated_profit": 22000,
  "profit_margin_pct": 12.2
}
```

---

## 💡 PRO TIPS:

### **Finding Providers:**
- Be specific with location (city + state)
- Use exact service name from RFP
- Search multiple locations if contract allows

### **Sending RFQs:**
- Send to 4-5 providers (get competitive quotes)
- Include full scope from RFP
- Highlight LOCAL partnership benefit

### **Scoring:**
- Let AI do initial scoring
- Review top 2-3 quotes manually
- Consider both score AND your gut feeling

### **Markup:**
- Start with 20% markup
- Adjust based on:
  - How competitive the bid needs to be
  - Your management overhead
  - Contract complexity

---

## 🎯 TIME COMPARISON:

| Task | Manual | With NEXUS | Savings |
|------|--------|------------|---------|
| Find providers | 2-3 hours | 60 sec | 99% |
| Generate RFQs | 1 hour | 2 min | 97% |
| Score quotes | 1-2 hours | 30 sec | 99% |
| Calculate bid | 30 min | 10 sec | 99% |
| **TOTAL** | **4-6 hours** | **5 minutes** | **98%** |

---

## 🚨 TROUBLESHOOTING:

**No providers found?**
- Try broader service term (e.g., "cleaning services" vs "aircraft wash")
- Try nearby cities
- Add manually if you know local companies

**RFQ emails not generating?**
- Check opportunity has SERVICE TYPE and LOCATION fields
- Verify provider has EMAIL field
- Check API error message

**Quotes not scoring?**
- Ensure RESPONSE TEXT field is filled
- Ensure QUOTE AMOUNT is entered
- Check quote record has link to opportunity

**Bid calculation seems wrong?**
- Verify QUOTE AMOUNT is correct
- Check markup_percentage parameter (default 20)
- Review for typos in numbers

---

## 📞 QUICK REFERENCE:

**API Base URL:**
```
https://deedavis.pythonanywhere.com
```

**Endpoints:**
```
POST /gpss/local-providers/find           - Find providers
POST /gpss/local-providers/rfq/send-bulk  - Generate RFQs
POST /gpss/local-providers/quotes/score-all - Score quotes
POST /gpss/local-providers/bid/summary    - Calculate final bid
```

**Airtable Tables:**
```
GPSS SERVICE PROVIDERS  - Provider database
GPSS QUOTES            - Quote tracking
```

---

## ✅ SUCCESS CHECKLIST:

- [ ] Airtable tables created
- [ ] Backend deployed to PythonAnywhere
- [ ] Tested finding providers
- [ ] Generated first RFQ
- [ ] Collected and scored quotes
- [ ] Calculated first final bid
- [ ] Submitted first proposal using system

---

**You're ready to bid on contracts nationwide!** 🎉

**For detailed documentation:** See `LOCAL_PROVIDER_SYSTEM_COMPLETE.md`
