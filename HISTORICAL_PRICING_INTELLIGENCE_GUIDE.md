# HISTORICAL PRICING INTELLIGENCE — NEXUS GUIDE

**How to find pricing from previous government contracts to validate your bids**

---

## 🎯 WHY THIS MATTERS

**You need historical pricing to:**
- ✅ Validate subcontractor quotes (are they reasonable?)
- ✅ Ensure your bid is competitive (not too high, not suspiciously low)
- ✅ Understand market rates for similar contracts
- ✅ Learn what incumbents charged (if rebidding)
- ✅ Benchmark your pricing against competitors
- ✅ Identify pricing trends over time

**Without historical pricing, you're bidding blind.**

---

## 📊 5 SOURCES FOR HISTORICAL PRICING

### **1. USASpending.gov** (Federal Contracts)

**What you can find:**
- ✅ Total contract value
- ✅ Contractor name (who won)
- ✅ Agency
- ✅ Award date
- ✅ Contract description
- ✅ NAICS/PSC codes

**What you CAN'T find:**
- ❌ Line-item pricing (not public)
- ❌ Unit prices (not public)
- ❌ Losing bids (only winners shown)

**How to use:**
```python
# Use NEXUS historical_pricing_scraper.py
python3 historical_pricing_scraper.py

# Or search manually:
# 1. Go to usaspending.gov
# 2. Search by NAICS code, PSC code, or keywords
# 3. Filter by value range, date range, agency
# 4. Export results to CSV
```

**Example:**
- Search: "Medical courier services, NAICS 492110, $50K-$150K, 2021-2026"
- Find: 50 similar contracts
- Estimate: $70K/year ÷ 1000 shipments = ~$70/shipment

**NEXUS Tool:** `historical_pricing_scraper.py`

---

### **2. FOIA Requests** (Federal — Detailed Pricing)

**What you can get:**
- ✅ **Winning bid pricing (line-item detail)**
- ✅ **ALL bid pricing (winning + losing bids)**
- ✅ Evaluation scores
- ✅ Bid tabulations
- ✅ Technical proposals

**How to request:**
1. Identify the contract (solicitation number, agency, date)
2. Submit FOIA request to the agency
3. Request: "All bids received for Solicitation #XXXXX including pricing"
4. Wait 10-30 days for response

**Cost:** Usually free or minimal ($0-50 for copies)

**Best for:**
- Contracts you lost (learn why)
- Contracts you're rebidding (see what won last time)
- Understanding competitor pricing strategies

**NEXUS Tool:** `historical_pricing_scraper.py` generates FOIA templates

**Example FOIA Request:**
```
FREEDOM OF INFORMATION ACT (FOIA) REQUEST

To: [Agency Name]
    FOIA Officer / Procurement Department

Date: [Today's Date]

Subject: FOIA Request for Bid Pricing — Solicitation [Number]

Dear FOIA Officer,

Pursuant to the Freedom of Information Act (5 U.S.C. § 552), I am requesting 
copies of the following records:

**Solicitation Number:** [Number]
**Contract Title:** [Title]

**Records Requested:**

1. All bids/proposals received in response to this solicitation, including:
   - Technical proposals
   - Cost proposals / pricing sheets
   - Line-item pricing for all bidders
   
2. Bid tabulation sheet showing:
   - All bidders
   - Bid amounts
   - Evaluation scores (if applicable)
   
3. Contract award documentation:
   - Award letter
   - Final negotiated pricing
   - Contract terms and conditions

**Purpose:** Market research for competitive pricing analysis.

**Preferred Format:** Electronic (PDF) via email to info@deedavis.biz

**Fee Waiver Request:** As a small business conducting market research, I 
request a waiver of any fees associated with this request. If fees cannot be 
waived, please notify me if costs will exceed $50 before processing.

Sincerely,

Dee Davis
President & CEO
Dee Davis Inc.
248.376.4550
info@deedavis.biz
```

---

### **3. Public Records Requests** (State/Local — Detailed Pricing)

**What you can get:**
- Same as FOIA but for state/local agencies
- Bid tabulations, pricing sheets, evaluation results
- Incumbent contract pricing

**How to request:**
- Each state has its own process
- **Ohio:** Submit through OhioBuys portal
- **Michigan:** FOIA request to specific agency (online form or email)
- **Illinois:** Submit to agency FOIA officer
- **Texas:** Open Records Request

**Example for Ohio DOH:**
- The Q&A said: "For incumbent contract information, submit a Public Records Request through OhioBuys"
- This would give you the current contract pricing
- See: `BIDS:RESOURCES/OHIO DOH MEDICAL COURIER/FOIA_REQUEST_INCUMBENT_PRICING.txt`

**State-Specific Portals:**
| State | Portal | Records Request Process |
|---|---|---|
| Ohio | OhioBuys | Submit through portal |
| Michigan | SIGMA / MITN | Email agency FOIA officer |
| Illinois | BidBuy | Email agency procurement |
| Texas | ESBD | Open Records Request form |

---

### **4. State Procurement Portals** (Some Show Pricing Publicly)

**What you can find:**
- Bid tabulation sheets (some states post publicly)
- Award amounts
- Winning bidder names
- Sometimes line-item pricing

**Where to look:**

**Ohio:**
- OhioBuys → "Contract Awards" section
- Some agencies post bid tabs publicly

**Michigan:**
- SIGMA (State of Michigan procurement)
- MITN (Michigan Inter-governmental Trade Network)
- Some counties post bid tabulations on their websites

**Federal:**
- FedBizOpps / SAM.gov → Award notices (total value only)

**How to use:**
1. Search for similar past contracts
2. Download bid tabulation sheets (if available)
3. See winning prices vs. losing prices
4. Identify pricing trends

---

### **5. GSA Advantage / GSA Schedule Pricing** (Federal Pre-Negotiated)

**What it is:**
- Pre-negotiated pricing for products/services on GSA Schedule
- Publicly available on GSA Advantage website
- Government-approved pricing

**How to use:**
1. Go to: gsaadvantage.gov
2. Search for similar products/services
3. See GSA contract pricing
4. Use as benchmark for your bids

**Example:**
- Search "medical courier services" on GSA Advantage
- See what GSA-approved vendors charge
- Use as pricing reference (GSA pricing is typically competitive)

**Note:** GSA pricing is often 10-20% lower than commercial pricing (volume discount)

---

## 🤖 NEXUS AUTOMATION

### **Tool: `historical_pricing_scraper.py`**

**What it does:**
1. Searches USASpending.gov for similar contracts
2. Filters by NAICS, PSC, value range, date range
3. Estimates per-unit pricing from total contract value
4. Generates FOIA request templates

**How to use:**

```python
from historical_pricing_scraper import HistoricalPricingScraper

scraper = HistoricalPricingScraper()

# Search for similar contracts
results = scraper.search_similar_contracts(
    service_type="medical courier",
    naics_code="492110",
    min_value=50000,
    max_value=150000,
    years_back=3
)

# Estimate per-unit pricing
estimate = scraper.estimate_unit_pricing(
    total_contract_value=350000,
    contract_duration_years=5,
    estimated_annual_volume=1000,
    service_type='medical courier'
)

# Generate FOIA request
foia = scraper.generate_foia_request_template(
    solicitation_number="DOH59579",
    agency_name="Ohio Department of Health",
    contract_title="Medical Courier Services"
)
```

**Example Output:**
```
✅ Found 50 similar contracts

1. CROSSTOWN COURIER SERVICE INC
   Agency: Veterans Affairs
   Amount: $1,469,655.10
   Period: 2019-11-01 to 2026-02-28
   Estimated: $489.89 per shipment (if 1000/year)

2. DALYWORKS, LLC
   Agency: Department of Defense
   Amount: $1,894,060.32
   Period: 2019-03-01 to 2024-08-31
   Estimated: $631.35 per shipment (if 1000/year)
```

---

## 📋 WORKFLOW: Using Historical Pricing in Your Bid

### **Step 1: Identify Similar Contracts**
- Use `historical_pricing_scraper.py` to search USASpending
- Filter by NAICS/PSC code, value range, date range
- Export top 10-20 similar contracts

### **Step 2: Estimate Market Rates**
- Calculate average per-unit pricing from total contract values
- Adjust for:
  - Geographic differences (Ohio vs. California)
  - Contract size (larger contracts = lower per-unit cost)
  - Service complexity (rural routes vs. urban)
  - Time period (adjust for inflation)

### **Step 3: Request Detailed Pricing (if needed)**
- Submit FOIA/Public Records Request for incumbent contract
- Request bid tabulations from previous solicitations
- Wait 10-30 days for response

### **Step 4: Validate Subcontractor Quotes**
- Compare sub's quote to market rates
- Use `subcontractor_quote_validator.py` to flag outliers
- If sub's quote is >20% higher than market → negotiate or find new sub
- If sub's quote is >30% lower than market → red flag (can they deliver?)

### **Step 5: Price Your Bid**
- Use market rates as floor (don't go below market)
- Apply your markup (15-20% for products, 10-15% for services)
- Ensure your bid is competitive but profitable

---

## 💡 PRICING INTELLIGENCE BEST PRACTICES

### **1. Build a Pricing Database**
- Store historical pricing in Airtable "Market Intelligence" table
- Update quarterly
- Track by service type, region, agency type

### **2. Track Competitors**
- Note who wins similar contracts
- Track their pricing patterns
- Identify their strengths/weaknesses

### **3. Adjust for Context**
| Factor | Adjustment |
|---|---|
| **Rural vs. Urban** | Rural +10-20% (longer routes) |
| **High-volume** | -5-10% (economies of scale) |
| **Specialized service** | +15-25% (HIPAA, BBP, etc.) |
| **Multi-year contract** | +3% per year (escalation) |
| **Small business set-aside** | +5-10% (less competition) |

### **4. Use Multiple Sources**
- Don't rely on one data point
- Cross-reference USASpending + FOIA + GSA
- Look for patterns, not outliers

### **5. Document Your Pricing Rationale**
- Keep notes on where pricing came from
- If audited, you can justify your rates
- Shows due diligence to contracting officers

---

## 🚨 RED FLAGS IN HISTORICAL PRICING

**Be cautious if:**
- ❌ Only one data point available (not enough to validate)
- ❌ Pricing is 50%+ higher/lower than market (outlier)
- ❌ Contract was terminated early (performance issues?)
- ❌ No similar contracts in past 5 years (new service?)
- ❌ All contracts go to one company (sole source? incumbent advantage?)

---

## 📊 EXAMPLE: Ohio DOH Medical Courier Pricing

### **USASpending Search Results:**
- 50 similar contracts found (NAICS 492110, $50K-$150K)
- Average: $489-$631 per shipment (estimated at 1000/year)
- Range: $159-$631 per shipment

### **Subcontractor Quote Validation:**
- Sub quotes: $45-$75 per shipment
- Market rate: $489-$631 per shipment
- **Assessment:** Sub quotes are MUCH lower than federal market
- **Reason:** Federal contracts include overhead, profit, admin
- **Action:** Sub quotes are reasonable for direct service provider

### **DDI Bid Calculation:**
- Sub quote: $60/shipment
- DDI markup: 18%
- DDI bid: $70.80/shipment
- **Assessment:** Competitive (well below federal market of $489+)

### **Next Step:**
- Submit FOIA request to Ohio DOH for incumbent pricing
- Validate that $70.80/shipment is competitive for state contract
- Adjust if needed based on incumbent data

---

## 🎯 QUICK REFERENCE

| Need | Tool | Timeline |
|---|---|---|
| **Quick market check** | USASpending search | 5 minutes |
| **Detailed pricing** | FOIA request | 10-30 days |
| **GSA benchmark** | GSA Advantage | 10 minutes |
| **State contract pricing** | Public Records Request | 10-30 days |
| **Competitor analysis** | USASpending + FOIA | 2-4 weeks |

---

## 📁 NEXUS FILES

| File | Purpose |
|---|---|
| `historical_pricing_scraper.py` | Search USASpending, generate FOIA templates |
| `subcontractor_quote_validator.py` | Validate sub quotes against market rates |
| `multi_year_pricing_calculator.py` | Calculate multi-year pricing with escalation |
| `GOVERNMENT_PRICING_SYSTEM_COMPLETE.md` | Master pricing guide |

---

*Historical pricing = competitive intelligence. Use it to win more bids at better margins.*
