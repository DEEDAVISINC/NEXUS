# 🎯 PRIME CONTRACTOR MINING SYSTEM

## Find Companies That MUST Use You

**Status:** ✅ LIVE AND READY  
**Cost:** 100% FREE (uses USASpending.gov + your SAM.gov API)  
**Time:** 2-5 minutes to run  
**Output:** 20-50 high-quality prospects automatically added to DDCSS

---

## 🚀 WHAT IT DOES

Automatically finds companies with $10M+ in federal contracts who are **LEGALLY REQUIRED** to meet diversity subcontracting goals.

These companies:
- ✅ Have $10M-$1B+ in active federal contracts
- ✅ MUST have subcontracting plans with diversity goals
- ✅ Are REQUIRED to report % diverse spend to the government
- ✅ NEED EDWOSB/WOSB suppliers like you to meet their goals
- ✅ Have budgets and authority to hire consultants
- ✅ Face penalties if they don't meet goals

---

## 💰 WHY THIS IS GOLD

### The Federal Requirement:

Any company with a federal contract over $750K **MUST** submit a subcontracting plan showing:
- Small Business Goal: 23%
- WOSB Goal: 5%
- EDWOSB Goal: 3%+
- HUBZone, VOSB, SDVOSB goals

### Their Pain Point:

Most companies are BELOW their goals:
- **Example:** Defense contractor with $50M in contracts
  - Required WOSB spend: $2.5M (5%)
  - Current WOSB spend: $800K (1.6%)
  - **GAP: $1.7M they NEED to spend with WOSB suppliers!**

### Your Opportunity:

You can:
1. **Supply products/services** directly (your EDWOSB advantage)
2. **Consult on supplier diversity** (help them meet goals)
3. **Both!** Supply AND advise

---

## 🎯 HOW TO RUN IT

### Method 1: Quick Run (Recommended)

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python mine_prime_contractors.py
```

**That's it!** Wait 2-5 minutes and check your DDCSS Prospects table.

---

### Method 2: Customize Parameters

Edit `mine_prime_contractors.py` to adjust:

```python
results = handle_ddcss_mine_prime_contractors(
    min_contract_value=25000000,  # Find companies with $25M+ (bigger fish)
    limit=100  # Find up to 100 prospects (more is better!)
)
```

**Parameters:**
- `min_contract_value`: Minimum total federal contract value
  - `10000000` = $10M (default - good starting point)
  - `25000000` = $25M (larger companies, bigger budgets)
  - `50000000` = $50M (major primes only)
  
- `limit`: Max number of prospects to find
  - `50` = default (good for weekly runs)
  - `100` = more prospects (good for monthly runs)
  - `200` = maximum (comprehensive search)

---

## 📊 WHAT YOU GET

### Airtable Records Created:

Each prospect includes:
- **Company Name** - e.g., "Lockheed Martin Corporation"
- **Total Contract Value** - e.g., $500M
- **AI Score** - 0-100 qualification score
- **Priority** - HIGH (85+) or MEDIUM (70-84)
- **Pain Point** - "Estimated $40M gap in small business subcontracting"
- **Diversity Gap %** - e.g., 8% below goal
- **Gap Dollar Value** - e.g., $40M opportunity
- **Awarding Agencies** - DOD, VA, NASA, etc.
- **Contract Count** - How many active contracts
- **Notes** - Full context about their situation

### Automatic Filtering:

- ✅ Only companies with AI score 70+ are added
- ✅ Duplicates automatically skipped
- ✅ Companies sorted by priority (HIGH/MEDIUM)

---

## 🎯 AFTER MINING - NEXT STEPS

### 1. Review Prospects in Airtable

**Go to:** Airtable → DDCSS Prospects table

**Filter:**
- Status = "New Lead"
- Source = "USASpending.gov Auto-Mining"
- AI Score ≥ 85 (HIGH priority)

**Sort by:** AI Score (descending)

---

### 2. Review Top 10-20 Prospects

Look for:
- ✅ Companies in industries you can serve (defense, healthcare, construction, etc.)
- ✅ Large contract values ($25M+)
- ✅ Big diversity gaps (>5%)
- ✅ Agencies you've worked with before
- ✅ Companies in your geographic area (if relevant)

---

### 3. Research Before Outreach

For your top 5 prospects:

**Quick Research (5 min per company):**
1. Google: "[Company Name] supplier diversity"
2. Check their website for Supplier Diversity page
3. Look for Supplier Diversity Manager contact
4. Note their current programs/initiatives
5. Check LinkedIn for Supplier Diversity VP/Director

**What You're Looking For:**
- Supplier diversity contact person (name + email)
- Their stated diversity goals
- Application process
- Current suppliers (to avoid conflicts)
- Recent initiatives (perfect timing!)

---

### 4. Outreach Templates

Use these approaches:

#### **Approach A: Direct Supplier Application**

"Hi [Supplier Diversity Manager],

I'm Dee Davis with Dee Davis Inc., a certified EDWOSB supplier. I noticed [Company] has significant federal contracts and I'd love to explore opportunities to support your supplier diversity goals.

We provide [your products/services] and are SAM.gov registered with GSA access. 

Could we schedule 15 minutes to discuss how we might support your subcontracting plan goals?

[Your signature]"

#### **Approach B: Consulting on Diversity Goals**

"Hi [Procurement/Supply Chain VP],

I help federal prime contractors optimize their small business subcontracting plans and achieve their diversity spend goals.

I noticed [Company] has [contract value] in active federal contracts. Many companies in your position face challenges meeting the 23% small business and 5% WOSB goals.

I'd love to share some strategies that have helped similar defense contractors improve their compliance and performance.

Available for a brief call?

[Your signature]"

#### **Approach C: Both (Supplier + Consultant)**

"Hi [Name],

I'm reaching out regarding [Company]'s supplier diversity program. Dee Davis Inc. is a certified EDWOSB that both:

1. Provides [products/services] as a direct supplier
2. Consults with primes on optimizing their subcontracting plans

Given your federal contract portfolio, I believe we could support your goals in multiple ways. 

Could we schedule a conversation to explore?

[Your signature]"

---

## 📅 RECOMMENDED SCHEDULE

### Weekly Run (Recommended):
```bash
# Every Monday morning
python mine_prime_contractors.py
```

**Result:** 20-50 new prospects per week = 80-200/month

### Monthly Deep Run:
```python
# First Monday of each month
# Increase limit to 100-200 for comprehensive search
```

---

## 🔄 AUTOMATION SETUP

### Option 1: Manual (Start Here)
- Run script weekly on Monday mornings
- Takes 2-5 minutes
- Review prospects Tuesday/Wednesday
- Start outreach Thursday/Friday

### Option 2: Cron Job (Future)
```bash
# Add to crontab (runs every Monday at 6am)
0 6 * * 1 cd "/Users/deedavis/NEXUS BACKEND" && python mine_prime_contractors.py
```

---

## 📊 SUCCESS METRICS

Track these in Airtable:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Prospects Added | 50+/week | Count new records |
| High Quality (85+) | 10+/week | Filter AI Score ≥85 |
| Response Rate | 10-20% | Track emails sent vs responses |
| Meetings Booked | 2-5/week | Calendar entries |
| Deals Closed | 1/quarter | DDCSS → ATLAS projects |

---

## 💡 PRO TIPS

### 1. **Target Defense Contractors First**
Defense has the STRICTEST diversity requirements. Start here.

### 2. **Look for Recent Award Winners**
Companies that just won new contracts have fresh budgets and urgency.

### 3. **Focus on $25M-$100M Range**
- Big enough to have budget
- Small enough to need help
- Not so large they have huge internal teams

### 4. **Leverage Agency Relationships**
If you've worked with VA before, target companies who work with VA.

### 5. **Time Your Outreach**
Best times:
- Q1 (Jan-Mar): Planning for the year
- Q3 (Jul-Sep): Mid-year push to meet goals
- Avoid: Q4 (too late for current year)

---

## 🆘 TROUBLESHOOTING

### "No prospects created"

**Possible causes:**
1. ❌ AIRTABLE_API_KEY not set → Check .env file
2. ❌ AIRTABLE_BASE_ID not set → Check .env file
3. ❌ "DDCSS Prospects" table doesn't exist → Create in Airtable
4. ❌ Internet connection issue → Check connectivity
5. ❌ USASpending.gov API down → Try again later

**Fix:** Verify .env file has:
```bash
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
```

---

### "Only low scores / all skipped"

**Cause:** Search parameters too narrow

**Fix:** Adjust in `mine_prime_contractors.py`:
```python
# Lower the minimum to find more companies
min_contract_value=5000000,  # $5M instead of $10M
```

---

### "Duplicates skipped"

**Good news!** System is working - these companies are already in your database.

**Action:** Focus on outreach to existing prospects, or increase search limit to find new ones.

---

## 🎯 THE BOTTOM LINE

**This system finds companies who:**
- ✅ Have budget ($10M-$1B in federal contracts)
- ✅ Have authority (prime contractors)
- ✅ Have pain (below diversity goals)
- ✅ Are LEGALLY REQUIRED to solve it
- ✅ Face penalties if they don't

**You offer the solution they MUST have.**

**Your EDWOSB certification is literally what they're required to buy.**

---

## 🚀 READY TO START?

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python mine_prime_contractors.py
```

**Expected time:** 2-5 minutes  
**Expected output:** 20-50 qualified prospects  
**Expected value:** $1M-$10M+ in potential opportunities

---

**Built:** January 28, 2026  
**Status:** LIVE  
**Cost:** FREE (USASpending.gov + SAM.gov APIs)  
**ROI:** One $50K deal pays for 200+ years of operation 🎯
