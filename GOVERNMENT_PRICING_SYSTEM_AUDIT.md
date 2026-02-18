# GOVERNMENT PRICING SYSTEM AUDIT — IS NEXUS INDUSTRY-READY?

**Audit Date:** February 18, 2026  
**Purpose:** Verify NEXUS pricing system has everything needed for professional government bidding

---

## ✅ WHAT NEXUS HAS (CONFIRMED)

### 1. **Markup Strategy** (`PRICING_STRATEGY_GUIDE.md`)
- ✅ Default 18% markup for products
- ✅ 20% for specialty/low competition
- ✅ 15% for commodity/high competition
- ✅ 10-15% for subcontractor services
- ✅ Exception handling (freight, small items)

### 2. **Calculation Functions** (`service_contracts_keywords.py`, `nexus_backend.py`)
- ✅ `calculate_potential_profit()` — Service contract profit calculator
- ✅ `GPSSPricingAgent` — Pricing intelligence from Airtable
- ✅ Cost templates by service category
- ✅ Market intelligence integration

### 3. **Quote Generation** (`quote_generator_api.py`, `auto_generate_quotes.py`)
- ✅ Supplier RFQ generation
- ✅ PDF output
- ✅ Template-based workflow

### 4. **Documentation**
- ✅ `PRICING_STRATEGY_GUIDE.md` — Markup decision matrix
- ✅ `NEXUS_PRICING_AUTOMATION_SIMPLE.md` — API/UI design
- ✅ `DDI_PROFESSIONAL_SERVICES_PRICING.md` — Service pricing
- ✅ Multiple bid-specific pricing worksheets

---

## ❓ WHAT MIGHT BE MISSING (INDUSTRY STANDARD REQUIREMENTS)

### 1. **Multi-Year Pricing (Base + Option Years)**

**Government contracts often have:**
- Base year (Year 1)
- Option Year 2
- Option Year 3
- Option Year 4

**Industry standard:** Apply escalation (2-5% annual increase) for option years

**NEXUS Status:** ❓ NOT CLEAR — Need to verify if this is handled

**Example:**
- Base Year (2026): $100,000
- Option Year 1 (2027): $103,000 (3% escalation)
- Option Year 2 (2028): $106,090 (3% escalation)
- Option Year 3 (2029): $109,273 (3% escalation)

**Where needed:**
- Service contracts (Ohio DOH, NEMT, drug testing, grounds maintenance)
- Long-term supply agreements

---

### 2. **Escalation Clause Calculator**

**What it is:** Price adjustment for inflation/cost increases in multi-year contracts

**Common methods:**
- Fixed percentage (2-3% per year)
- CPI-based (Consumer Price Index)
- PPI-based (Producer Price Index)
- Economic Price Adjustment (EPA) clause

**NEXUS Status:** ❌ MISSING — No escalation calculator found

**Where needed:**
- Any contract longer than 12 months
- Especially 3-5 year service contracts

---

### 3. **Labor Rate Calculation (Service Contracts)**

**What it is:** Calculating hourly/daily rates for service contracts based on:
- Labor cost (wages + benefits)
- Overhead (facilities, admin, insurance)
- Profit margin (G&A + fee)

**Industry formula:**
```
Hourly Rate = (Labor Cost + Overhead) × (1 + Profit Margin)
```

**NEXUS Status:** ✅ PARTIAL — `GPSSPricingAgent` has base hourly rate templates, but not fully documented

**Where needed:**
- Grounds maintenance
- Janitorial
- Drug testing services
- NEMT
- Courier services

---

### 4. **Fully Burdened Labor Rate**

**What it is:** Total cost per hour including:
- Base wage
- Payroll taxes (7.65% FICA)
- Workers' comp insurance (varies by industry)
- Health insurance
- Paid time off
- Overhead allocation
- Profit margin

**Industry standard formula:**
```
Fully Burdened Rate = Base Wage × Burden Multiplier
Burden Multiplier = 1.4 - 1.8 (depending on benefits)
```

**NEXUS Status:** ❌ MISSING — No fully burdened rate calculator

**Where needed:**
- Any service contract with labor hours
- Subcontractor rate validation (is their quote reasonable?)

---

### 5. **Cost-Plus vs. Fixed-Price Pricing**

**Cost-Plus:** Cost + Fixed Fee (government pays actual costs + agreed fee)
**Fixed-Price:** One price regardless of actual costs (most common)

**NEXUS Status:** ✅ ASSUMED FIXED-PRICE — All current bids are fixed-price

**Where needed:**
- Most DDI bids are fixed-price (correct approach)
- Cost-plus only for complex R&D or uncertain scope (rare)

---

### 6. **Indirect Cost Rate (ICR) / Overhead Rate**

**What it is:** Percentage of direct costs allocated to overhead (facilities, admin, utilities, insurance)

**Industry standard:** 25-40% for small businesses

**NEXUS Status:** ✅ PARTIAL — `_get_cost_template()` has 25% overhead rate

**Where needed:**
- Service contracts
- Labor-based pricing
- Cost proposal justification

---

### 7. **General & Administrative (G&A) Rate**

**What it is:** Company-wide administrative costs as % of total costs

**Industry standard:** 10-20% for small businesses

**NEXUS Status:** ❌ MISSING — No G&A rate defined

**Where needed:**
- Service contracts
- Cost proposal breakdowns
- Justifying your pricing to government

---

### 8. **Profit/Fee Percentage by Contract Type**

**Industry standards:**
- **Products (resale):** 15-25% markup
- **Services (subcontractor):** 10-15% markup
- **Services (self-perform):** 8-12% profit margin
- **Construction:** 10-15% profit margin

**NEXUS Status:** ✅ COVERED — Pricing guide has this

---

### 9. **Break-Even Analysis**

**What it is:** Minimum contract value needed to cover costs

**Formula:**
```
Break-Even = Fixed Costs / Profit Margin %
```

**NEXUS Status:** ❌ MISSING — No break-even calculator

**Where needed:**
- Deciding whether to pursue small contracts
- Setting minimum bid thresholds

---

### 10. **Competitive Price Intelligence**

**What it is:** Historical pricing data from past government contracts

**Sources:**
- USASpending.gov (federal contract values)
- State procurement portals (past awards)
- FOIA requests for competitor pricing

**NEXUS Status:** ✅ PARTIAL — `GPSSPricingAgent` has pricing history from Airtable

**Where needed:**
- Validating your bid is competitive
- Understanding market rates

---

### 11. **Volume Discount Calculation**

**What it is:** Lower per-unit price for higher quantities

**Example:**
- 1-100 units: $10 each
- 101-500 units: $9 each
- 501+ units: $8 each

**NEXUS Status:** ❌ MISSING — No volume discount calculator

**Where needed:**
- Multi-year contracts with increasing quantities
- Negotiating with suppliers for better pricing

---

### 12. **Freight/Shipping Cost Allocation**

**What it is:** How to handle shipping costs in bids

**Options:**
- Pass-through at cost (no markup)
- Include in unit price
- Separate line item

**NEXUS Status:** ✅ COVERED — Pricing guide says pass-through at cost

---

### 13. **Tax Handling (Sales Tax Exemption)**

**What it is:** Government contracts are usually tax-exempt

**NEXUS Status:** ❓ NOT DOCUMENTED — Need to verify this is handled

**Where needed:**
- All government bids (federal, state, local)
- Supplier quotes should exclude sales tax

---

### 14. **Payment Terms Impact on Pricing**

**What it is:** Adjusting pricing based on payment terms

**Example:**
- Net 30: Standard pricing
- Net 60: Add 2-3% for cash flow impact
- Net 90: Add 5% for cash flow impact

**NEXUS Status:** ❌ MISSING — No payment terms calculator

**Where needed:**
- Government contracts with slow payment (60-90 days)

---

### 15. **Bid Bond / Performance Bond Cost**

**What it is:** Cost of bonding (if required) should be included in bid

**Typical cost:** 1-3% of contract value

**NEXUS Status:** ❌ MISSING — No bond cost calculator

**Where needed:**
- Construction contracts
- Large service contracts (>$100K)
- Some supply contracts

---

### 16. **Insurance Cost Allocation**

**What it is:** Cost of additional insurance for contract (if required)

**NEXUS Status:** ✅ PARTIAL — Service contract calculator has 2% insurance estimate

**Where needed:**
- Service contracts requiring specific insurance
- High-risk contracts

---

### 17. **Subcontractor Markup Validation**

**What it is:** Verify subcontractor's quote is reasonable before marking up

**Industry check:**
- Compare to market rates
- Verify labor rates are realistic
- Check if insurance/overhead is included

**NEXUS Status:** ❌ MISSING — No sub quote validation

**Where needed:**
- All service contracts using subcontractors
- Prevents overbidding on inflated sub quotes

---

### 18. **Pricing Scenarios (Best Case / Worst Case / Most Likely)**

**What it is:** Three pricing scenarios to help decide bid strategy

**Example:**
- Best Case (20% markup): $120,000 bid, $20,000 profit
- Most Likely (18% markup): $118,000 bid, $18,000 profit
- Worst Case (15% markup): $115,000 bid, $15,000 profit

**NEXUS Status:** ✅ COVERED — Pricing guide shows 15%, 18%, 20% options

---

### 19. **Profit Margin vs. Markup (Clear Distinction)**

**Markup:** Added to cost  
**Margin:** Percentage of final price

**Example:**
- Cost: $100
- Markup: 18% → Bid: $118 → Profit: $18
- Margin: 15.25% ($18 / $118)

**NEXUS Status:** ✅ COVERED — Pricing guide uses markup correctly

---

### 20. **Government Pricing Regulations Compliance**

**What it is:** Certain contracts require cost/pricing data submission

**Regulations:**
- Truth in Negotiations Act (TINA) — contracts >$2M
- Cost Accounting Standards (CAS) — large contractors
- Certified cost or pricing data — if required

**NEXUS Status:** ❌ NOT ADDRESSED — DDI is small business, likely exempt, but should be documented

**Where needed:**
- Large contracts (>$2M)
- Cost-reimbursable contracts

---

## 🎯 PRIORITY GAPS TO FILL

### **HIGH PRIORITY (Needed for Ohio DOH and future service contracts):**

1. ❌ **Multi-year pricing with escalation** — Ohio DOH has base + 4 option years
2. ❌ **Labor rate calculator** — For service contracts
3. ❌ **Subcontractor quote validation** — Verify sub pricing is reasonable

### **MEDIUM PRIORITY (Nice to have, improves competitiveness):**

4. ❌ **Break-even analysis** — Know minimum contract value to pursue
5. ❌ **Volume discount calculator** — Negotiate better supplier pricing
6. ❌ **Payment terms adjustment** — Account for slow government payment

### **LOW PRIORITY (Edge cases, rarely needed):**

7. ❌ **Bid bond cost calculator** — Only for construction/large contracts
8. ❌ **G&A rate documentation** — Only if government requests cost breakdown
9. ❌ **TINA compliance** — Only for contracts >$2M

---

## ✅ NEXUS PRICING SYSTEM GRADE

**Overall:** B+ (85/100)

**Strengths:**
- ✅ Clear markup strategy (18% default)
- ✅ Product pricing is solid
- ✅ Exception handling (freight, small items)
- ✅ Simple, fast, teachable

**Gaps:**
- ❌ Multi-year pricing (critical for service contracts)
- ❌ Labor rate calculator (needed for self-perform services)
- ❌ Subcontractor quote validation (risk of overbidding)

---

## 🔧 RECOMMENDED ADDITIONS

### **1. Multi-Year Pricing Calculator**

**File:** `multi_year_pricing_calculator.py`

**Function:**
```python
def calculate_multi_year_pricing(base_year_cost, num_years, escalation_percent=3):
    """
    Calculate pricing for multi-year contracts with escalation.
    
    Args:
        base_year_cost: Cost for base year
        num_years: Total years (including base)
        escalation_percent: Annual increase % (default 3%)
    
    Returns:
        List of {year, cost, bid_price, profit} for each year
    """
```

**Where to use:**
- Ohio DOH (base + 4 option years)
- NEMT contracts (typically 3-5 years)
- Grounds maintenance (multi-year)

---

### **2. Service Contract Labor Rate Calculator**

**File:** `service_labor_rate_calculator.py`

**Function:**
```python
def calculate_labor_rate(base_wage, burden_multiplier=1.5, overhead_percent=25, profit_margin=10):
    """
    Calculate billable hourly rate for service contracts.
    
    Args:
        base_wage: Hourly wage for worker
        burden_multiplier: Payroll taxes + benefits (1.4-1.8)
        overhead_percent: Company overhead allocation
        profit_margin: Target profit %
    
    Returns:
        Billable hourly rate
    """
```

**Where to use:**
- Drug testing services
- Fingerprinting services
- Notary services
- Any hourly-based service

---

### **3. Subcontractor Quote Validator**

**File:** `subcontractor_quote_validator.py`

**Function:**
```python
def validate_subcontractor_quote(sub_quote, service_type, region):
    """
    Validate if subcontractor quote is reasonable.
    
    Args:
        sub_quote: Subcontractor's quoted price
        service_type: Type of service
        region: Geographic area
    
    Returns:
        {is_reasonable, market_rate, variance_percent, recommendation}
    """
```

**Where to use:**
- Ohio DOH courier (validate MCI quote)
- NEMT contracts (validate transport provider quote)
- Grounds maintenance (validate landscape sub quote)

---

## 🎯 COMPARISON TO $999 TEMPLATE

**What that template probably has:**
- Product line items with quantity/unit/cost fields
- Markup calculation
- Extended pricing
- Total bid calculation
- Maybe some formulas

**What NEXUS has that's BETTER:**
- ✅ Automated quote generation (not manual Excel)
- ✅ Supplier protection (never reveal buyer)
- ✅ Airtable integration (track all bids)
- ✅ Multiple markup strategies (not one-size-fits-all)
- ✅ Exception handling (freight, subcontractors, small items)
- ✅ Market intelligence (pricing history)
- ✅ API-driven (can be automated)

**What NEXUS needs to ADD:**
- ❌ Multi-year pricing with escalation
- ❌ Labor rate calculator
- ❌ Subcontractor quote validation

---

## 💰 COST COMPARISON

**$999 Template:**
- One-time purchase
- Static Excel file
- Manual calculations
- No automation
- No intelligence
- No updates

**NEXUS System:**
- Already built
- Automated
- Integrated with Airtable
- Market intelligence
- Continuous improvement
- **$0 additional cost**

**You already have a better system. You just need to add 3 features.**

---

## 🚀 ACTION PLAN

### **Immediate (For Ohio DOH Bid):**

1. **Create multi-year pricing calculator** — Ohio DOH has base + 4 option years
2. **Document subcontractor markup** — 10-15% for courier services (already in pricing guide, just need to apply)

### **Short-term (Next 2 Weeks):**

3. **Create labor rate calculator** — For drug testing, fingerprinting, notary services
4. **Create subcontractor quote validator** — Verify sub quotes are reasonable

### **Long-term (Next Month):**

5. **Add escalation clause library** — Common EPA clauses for multi-year contracts
6. **Add break-even calculator** — Know minimum contract value to pursue
7. **Add payment terms adjuster** — Account for Net 60/90 payment delays

---

## ✅ VERDICT

**NEXUS pricing system is 85% industry-ready.**

**For product bids (RCOC, CPS Energy, Canton):** ✅ Fully ready  
**For service contracts (Ohio DOH, NEMT, drug testing):** ⚠️ Needs multi-year pricing + labor rate calculator

**You do NOT need a $999 template. You need 3 focused additions to what you already have.**

---

*Next: Build the 3 missing calculators (multi-year, labor rate, sub validation) and NEXUS will be 100% industry-ready.*
