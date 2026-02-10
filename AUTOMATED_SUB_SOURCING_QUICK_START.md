# AUTOMATED SUB SOURCING - QUICK START
**Find subs in 2 minutes instead of 4 hours**

---

## ⚡ THE FASTEST PATH

### **Step 1: Set Up API Keys** (One-Time - 10 minutes)

```bash
# Add to your .env file or environment
export GOOGLE_MAPS_API_KEY="your_key_here"
export YELP_API_KEY="your_key_here"
export AIRTABLE_API_KEY="your_key_here"
export AIRTABLE_BASE_ID="your_base_id_here"
```

**Get API Keys:**
- Google Maps: https://console.cloud.google.com/ (enable Places API)
- Yelp: https://www.yelp.com/developers/v3/manage_app
- Airtable: Already have these!

---

### **Step 2: Create Airtable Tables** (One-Time - 5 minutes)

**Table 1: SUBCONTRACTORS**
Required fields:
- CompanyName (Single line text)
- Phone (Phone number)
- Email (Email)
- Website (URL)
- GoogleRating (Number, 1 decimal)
- YelpRating (Number, 1 decimal)
- TotalReviews (Number)
- ServiceTypes (Multiple select)
- CoverageArea (Single line text)
- Status (Single select: New, Active, Inactive)
- FirstContactDate (Date)

**Table 2: SUB_OUTREACH_TRACKING**
Required fields:
- OpportunityID (Link to Opportunities table)
- SubcontractorID (Link to SUBCONTRACTORS table)
- OutreachDate (Date with time)
- ResponseStatus (Single select: Pending, Interested, Declined, No Response)
- QuoteAmount (Currency)
- Available (Checkbox)

---

### **Step 3: Find Subs** (2 minutes)

```bash
cd "/Users/deedavis/NEXUS BACKEND"

python3 automated_sub_sourcing.py find \
  --service "lawn care" \
  --location "Oakland County, MI" \
  --radius 25 \
  --limit 20
```

**Output:**
```
============================================================
🔍 SEARCHING FOR SUBCONTRACTORS
============================================================
Service: lawn care
Location: Oakland County, MI
Radius: 25 miles

✓ Google Maps: Found 34 businesses
✓ Yelp: Found 28 businesses
✓ Merged results: 47 unique businesses
✓ Qualified contractors: 18
✓ Returning top 18 results
✓ Saved 15 new contractors to Airtable

============================================================
✅ SEARCH COMPLETE
============================================================
```

**That's it! You now have 15 qualified subs in your database.**

---

## 📋 COMMON USE CASES

### **Use Case 1: Finding Subs for Madison Heights Lawn Care**

```bash
python3 automated_sub_sourcing.py find \
  --service "lawn care landscaping" \
  --location "Oakland County, Michigan" \
  --radius 30
```

---

### **Use Case 2: Finding Pressure Washing Subs**

```bash
python3 automated_sub_sourcing.py find \
  --service "pressure washing" \
  --location "Wayne County, MI" \
  --radius 25
```

---

### **Use Case 3: Finding NEMT/Transportation Subs**

```bash
python3 automated_sub_sourcing.py find \
  --service "medical transportation NEMT" \
  --location "Detroit, Michigan" \
  --radius 50
```

---

### **Use Case 4: Finding Janitorial Subs**

```bash
python3 automated_sub_sourcing.py find \
  --service "janitorial cleaning commercial" \
  --location "San Antonio, Texas" \
  --radius 25
```

---

## 📊 VIEWING YOUR SUBS

### **List All Subs:**

```bash
python3 automated_sub_sourcing.py list
```

### **Filter by Service:**

```bash
python3 automated_sub_sourcing.py list --service "lawn care"
```

### **Filter by Location:**

```bash
python3 automated_sub_sourcing.py list --location "Oakland County"
```

---

## 📧 GENERATING OUTREACH EMAILS

### **Step 1: Get Record IDs**

Go to Airtable:
- Find your Opportunity record → Copy record ID (recXYZ...)
- Find the Subcontractor record → Copy record ID (recABC...)

### **Step 2: Generate Email Template**

```bash
python3 automated_sub_sourcing.py email-template \
  --opportunity-id recXYZ123 \
  --subcontractor-id recABC456
```

**Output:**
```
============================================================
EMAIL TEMPLATE
============================================================

SUBJECT: Government Contract Opportunity - Lawn Care in Oakland County, MI

BODY:
Hi John,

I'm Dee Davis with DEE DAVIS INC, a certified EDWOSB prime contractor. 
I found ABC Lawn Care and was impressed by your 4.8-star rating.

I'm bidding on a Lawn Care contract for a municipal client in Oakland County 
and looking for a qualified subcontractor partner.

...
```

### **Step 3: Copy/Paste into Gmail**

Copy the generated email and send manually (for now).

**Future:** Full automation with SendGrid integration (coming soon!)

---

## 📊 COMPARING QUOTES

### **After subs respond with pricing:**

```bash
python3 automated_sub_sourcing.py compare \
  --opportunity-id recXYZ123
```

**Output:**
```
============================================================
📊 COMPARING QUOTES
============================================================

Company                        Rating     Quote           Response     Available
------------------------------ ---------- --------------- ------------ ----------
ABC Lawn Care                  4.8★ (340) $4,500.00       4.2          Yes
XYZ Landscaping                4.6★ (156) $4,750.00       26.5         Yes
123 Maintenance                4.5★ (89)  $5,200.00       72.3         Yes

============================================================
```

---

## 🔄 THE COMPLETE WORKFLOW

### **Start to Finish (Service Bid):**

```bash
# 1. Find subs (2 minutes)
python3 automated_sub_sourcing.py find \
  --service "lawn care" \
  --location "Oakland County, MI"

# 2. Review results in Airtable (5 minutes)
# - Check ratings
# - Check contact info
# - Select 5-10 to contact

# 3. Generate emails for each (30 seconds each)
python3 automated_sub_sourcing.py email-template \
  --opportunity-id recOPP123 \
  --subcontractor-id recSUB001

python3 automated_sub_sourcing.py email-template \
  --opportunity-id recOPP123 \
  --subcontractor-id recSUB002

# ... repeat for 5-10 subs

# 4. Send emails manually via Gmail (5 minutes total)

# 5. Track responses in Airtable (as they come in)
# - Update ResponseStatus field
# - Add QuoteAmount
# - Mark Available

# 6. Compare quotes (30 seconds)
python3 automated_sub_sourcing.py compare \
  --opportunity-id recOPP123

# 7. Select best sub, request LOI, proceed with bid
```

**Total time: ~20 minutes** (vs 4-6 hours manually!)

---

## 🎯 SEARCH TIPS

### **Be Specific with Service Type:**

**❌ Too generic:**
- "services"
- "contractor"

**✅ Specific:**
- "lawn care landscaping"
- "pressure washing exterior cleaning"
- "medical transportation NEMT"
- "janitorial cleaning commercial"

### **Use Multiple Keywords:**
- "lawn care landscaping maintenance" (better than just "lawn care")
- "pressure washing power washing" (catches both terms)

### **Adjust Radius Based on Density:**
- Urban areas: 10-15 miles
- Suburban: 25-30 miles
- Rural: 50+ miles

---

## 💡 PRO TIPS

**1. Run searches early**
- Don't wait for RFP to drop
- Build sub database proactively
- Have 10-20 subs per category ready

**2. Quality over quantity**
- Focus on 4+ star ratings
- Minimum 10+ reviews
- Check "commercial" in business description

**3. Track everything**
- Use Airtable to track all outreach
- Note response times
- Build performance history

**4. Personalize emails**
- Mention their specific rating
- Reference their website or reviews
- Show you did research

**5. Build relationships**
- Don't just contact when you need them
- Check in quarterly
- Share wins and opportunities

---

## 🚨 TROUBLESHOOTING

### **"No results found"**
**Cause:** API keys not configured or wrong location  
**Fix:** Check API keys, try different search terms, expand radius

### **"Could not connect to Airtable"**
**Cause:** Tables don't exist or wrong names  
**Fix:** Create SUBCONTRACTORS and SUB_OUTREACH_TRACKING tables

### **"Google Maps search failed"**
**Cause:** API key invalid or Places API not enabled  
**Fix:** Enable Places API in Google Cloud Console

### **"Yelp search failed"**
**Cause:** API key invalid or rate limit exceeded  
**Fix:** Check Yelp API key, wait if rate limited

---

## 📁 FILES

**Main Script:**
- `automated_sub_sourcing.py`

**Documentation:**
- `AUTOMATED_SUB_SOURCING_SYSTEM.md` (complete design)
- `AUTOMATED_SUB_SOURCING_QUICK_START.md` (this file)
- `SERVICE_CONTRACT_SUB_FRAMEWORK.md` (manual process)

**Integration:**
- `MASTER_FRAMEWORKS_INTEGRATION.md`
- `SERVICE_VS_SUPPLY_DECISION_GUIDE.md`

---

## 🚀 NEXT STEPS

**This Week:**
1. Set up API keys
2. Create Airtable tables
3. Run first search test
4. Generate first email template

**Next Week:**
5. Build sub database (5-10 subs per category)
6. Use for real service bid
7. Track response rates
8. Refine process

**Future Automation:**
- Auto-send emails via SendGrid
- Auto-track responses via webhook
- Auto-send follow-ups
- Full NEXUS frontend integration

---

## ⏱️ TIME COMPARISON

| Task | Manual | Automated | Savings |
|------|--------|-----------|---------|
| **Find subs** | 2-3 hours | 2 minutes | 118-178 min |
| **Email each** | 1-2 hours | 10 minutes | 50-110 min |
| **Track responses** | 30 min | Automatic | 30 min |
| **Compare quotes** | 30 min | 30 seconds | 29.5 min |
| **TOTAL** | **4-6 hours** | **20 minutes** | **4-5 hours** |

**Efficiency gain: 12-18x faster!**

---

**Start using it today! Find subs in 2 minutes instead of 4 hours.**

---

**Last Updated:** February 4, 2026  
**Owner:** Dee Davis
