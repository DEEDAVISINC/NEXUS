# 💳 Factoring Requirements for VERTEX Invoices

**Date:** January 13, 2026  
**Priority:** HIGH  
**Requested By:** Dee Davis  

---

## 🎯 **Business Need**

**User's Exact Quote:**
> "Invoicing needs to have a factoring section, because we will use factoring for our contracts until we are financially able to cover them ourselves, 'Factoring with Directed Payment' or 'Three-Party Payment'"

---

## 📊 **What is Factoring?**

### **Definition:**
Invoice factoring is a financial arrangement where a business sells its invoices to a factoring company at a discount to receive immediate cash instead of waiting 30-90 days for payment.

### **How It Works:**
```
1. You complete government contract work
2. You invoice government for $100,000
3. Factoring company advances you $85,000 immediately (85%)
4. Government pays factoring company $100,000 in 60 days
5. Factoring company pays you remaining $12,000 ($15,000 minus $3,000 fee)
```

### **Types of Factoring:**

#### **Recourse Factoring:**
- You're responsible if government doesn't pay
- Lower fees (1-3% of invoice value)
- More common for government contracts

#### **Non-Recourse Factoring:**
- Factoring company assumes payment risk
- Higher fees (3-5% of invoice value)
- Rare for government contracts

#### **Directed Payment / Three-Party Payment:**
- Government pays factoring company directly
- Most secure for factoring company
- Required by most factors for government work
- Needs proper documentation (UCC filings, notices)

---

## 🏗️ **Implementation Requirements**

### **VERTEX Invoices Table - New Fields Needed:**

#### **Factoring Status:**
1. `factoring_enabled` (checkbox) - Is this invoice being factored?
2. `factoring_status` (single select)
   - Options: "Not Factored", "Pending Approval", "Approved", "Funded", "Paid to Factor", "Completed"

#### **Factoring Company Information:**
3. `factoring_company` (linked record → new "Factoring Companies" table)
4. `factoring_contact_name` (text)
5. `factoring_contact_email` (email)
6. `factoring_contact_phone` (phone)

#### **Financial Terms:**
7. `invoice_face_value` (currency) - Full invoice amount
8. `advance_percentage` (number, 0-100) - Usually 80-90%
9. `advance_amount` (formula) - `invoice_face_value * advance_percentage / 100`
10. `factoring_fee_percentage` (number, 0-100) - Usually 1-5%
11. `factoring_fee_amount` (formula) - `invoice_face_value * factoring_fee_percentage / 100`
12. `reserve_amount` (formula) - `invoice_face_value - advance_amount - factoring_fee_amount`
13. `net_to_you` (formula) - `invoice_face_value - factoring_fee_amount`

#### **Payment Tracking:**
14. `advance_received_date` (date) - When you got advance payment
15. `advance_received_amount` (currency) - Actual amount received
16. `government_paid_factor_date` (date) - When government paid factoring company
17. `government_paid_factor_amount` (currency) - Amount government paid
18. `reserve_released_date` (date) - When factoring company paid you the reserve
19. `reserve_released_amount` (currency) - Actual reserve payment

#### **Documentation:**
20. `factoring_agreement_link` (attachment) - Contract with factoring company
21. `ucc_filing_number` (text) - UCC-1 financing statement number
22. `notice_of_assignment` (attachment) - NOA sent to government agency
23. `directed_payment_authorization` (attachment) - Government's approval to pay factor

#### **Accounting:**
24. `factoring_fees_expense` (linked record → VERTEX Expenses)
25. `cash_flow_impact_date` (date) - When cash actually hit your account
26. `effective_interest_rate` (formula) - Annualized cost of factoring

---

## 🏢 **New Table: Factoring Companies**

**Purpose:** Store information about factoring companies you work with

**Fields:**
1. `company_name` (primary, text) - e.g., "Factor King", "Triumph Business Capital"
2. `contact_name` (text)
3. `contact_email` (email)
4. `contact_phone` (phone)
5. `website` (URL)
6. `advance_rate` (number, %) - Standard advance percentage (80-90%)
7. `fee_rate` (number, %) - Standard fee percentage (1-5%)
8. `minimum_invoice_amount` (currency) - Won't factor below this
9. `maximum_invoice_amount` (currency) - Won't factor above this
10. `payment_speed` (text) - "Same day", "1-2 days", "3-5 days"
11. `government_contracts_accepted` (checkbox) - Do they factor government invoices?
12. `recourse_or_nonrecourse` (single select) - "Recourse", "Non-Recourse", "Both"
13. `ucc_filing_required` (checkbox)
14. `contract_link` (attachment) - Your agreement with them
15. `notes` (long text)
16. `status` (single select) - "Active", "Inactive", "Under Review"

---

## 🔄 **Integration with Existing Systems**

### **GPSS → VERTEX with Factoring:**

```
Government Contract Won (GPSS)
  ↓
Create VERTEX Invoice
  ↓
[Decision Point] Need factoring?
  ↓ YES
  ├─ Enable factoring on invoice
  ├─ Select factoring company
  ├─ Calculate advance & fees
  ├─ Submit invoice to factor
  ├─ Factor reviews & approves
  ├─ Receive advance payment (80-90%)
  ├─ Record advance in VERTEX Revenue
  ├─ Send Notice of Assignment to government
  ├─ Government pays factor (30-90 days)
  ├─ Factor releases reserve minus fees
  ├─ Record final payment
  └─ Calculate effective cost of financing
  ↓ NO
  └─ Standard invoice workflow (wait for government payment)
```

### **Cash Flow Forecast Impact:**

**Without Factoring:**
- Invoice: $100,000
- Payment in: 60 days
- Cash available: Day 60

**With Factoring:**
- Invoice: $100,000
- Advance (85%): $85,000 - Day 2
- Reserve (12%): $12,000 - Day 65
- Fee (3%): $3,000 - Cost of capital
- Net to you: $97,000
- Cash available: Day 2 (immediate)

**Impact on VERTEX Dashboard:**
- "Current Cash" increases immediately
- "Pending Revenue" decreases
- "Factoring Fees" tracked as expense
- "Effective Capital Cost" calculated

---

## 📋 **Document Requirements**

### **For Each Factored Invoice:**

1. **UCC-1 Financing Statement**
   - Filed with Secretary of State
   - Gives factoring company legal claim on receivable
   - Lasts 5 years, can be renewed

2. **Notice of Assignment (NOA)**
   - Letter to government agency
   - Informs them to pay factoring company, not you
   - Must include: factor's bank info, invoice details, your authorization

3. **Schedule of Accounts**
   - List of invoices being factored
   - Updated regularly with factor

4. **Directed Payment Authorization**
   - Government's acknowledgment to pay factor
   - Required by most factors
   - Can take 30-60 days to get approved

---

## 💡 **Business Rules**

### **When to Use Factoring:**
✅ Large government contracts ($50K+)
✅ Need immediate cash for operations/payroll
✅ 30-90 day payment terms from government
✅ Strong government credit (federal > state > local)

### **When NOT to Use Factoring:**
❌ Small invoices (under $10K) - fees too high
❌ You have sufficient cash reserves
❌ Fast-paying clients (under 30 days)
❌ Disputable invoices (contract issues, incomplete work)

### **Factoring vs. Other Options:**
- **Bank Line of Credit:** Cheaper (6-12% APR) but harder to qualify
- **SBA Loan:** Lower rates but slow approval
- **Factoring:** Fast (1-2 days) but expensive (12-60% APR equivalent)

---

## 🎯 **Dashboard Metrics to Add**

**New VERTEX Dashboard KPIs:**

1. **Total Factored Invoices** (month/year)
2. **Total Factoring Fees Paid** (expense tracking)
3. **Average Advance Rate** (optimize over time)
4. **Average Factoring Fee %** (compare between companies)
5. **Effective Annual Rate** (true cost of capital)
6. **Days to Cash** (average time to get advance)
7. **Reserve Aging** (how long until reserve released)

**Cash Flow Improvements:**
- "Immediate Cash Available" (via factoring)
- "Factoring Capacity" (how much more can we factor)
- "Cash Velocity" (how fast money moves)

---

## 🚨 **Risks & Mitigation**

### **Risks:**
1. **High Cost** - Can be 20-60% APR equivalent
2. **Notification to Client** - Government knows you're factoring
3. **UCC Filings** - Public record, affects credit rating
4. **Recourse Risk** - If government doesn't pay, you're liable
5. **Contract Terms** - May be locked in for period of time

### **Mitigation:**
1. Only factor when necessary (not every invoice)
2. Compare multiple factoring companies (get best rates)
3. Negotiate advance rates and fees
4. Use for large contracts only (optimize cost/benefit)
5. Build cash reserves to avoid long-term dependence

---

## 📊 **Example Calculation**

**Scenario:** $100,000 government contract, 60-day payment terms

| Item | Amount | Notes |
|------|--------|-------|
| Invoice Amount | $100,000 | Face value |
| Advance Rate | 85% | Industry standard |
| Advance Amount | $85,000 | You get this in 2 days |
| Factoring Fee | 3% | Monthly rate |
| Factoring Fee Amount | $3,000 | Cost of service |
| Reserve | 12% | Held until government pays |
| Reserve Amount | $12,000 | Released later |
| Net to You | $97,000 | Total after fees |
| Effective Cost | 18% APR | Annualized cost |

**Time Value Analysis:**
- Without factoring: Wait 60 days for $100,000
- With factoring: Get $85,000 in 2 days, $12,000 in 65 days
- Cost: $3,000 (3% of invoice)
- Benefit: Immediate liquidity for operations

---

## 🔧 **Implementation Checklist**

### **Phase 1: Database (Week 1)**
- [ ] Add factoring fields to VERTEX Invoices table
- [ ] Create Factoring Companies table
- [ ] Create factoring views and filters
- [ ] Test formulas (advance, fees, reserve calculations)

### **Phase 2: Workflow (Week 2)**
- [ ] Add factoring decision point to invoice creation
- [ ] Build factoring company selection interface
- [ ] Create advance payment recording flow
- [ ] Build reserve payment tracking

### **Phase 3: Integration (Week 3)**
- [ ] Connect GPSS → VERTEX factoring workflow
- [ ] Update cash flow forecasting to include factoring
- [ ] Add factoring metrics to dashboard
- [ ] Create factoring expense tracking

### **Phase 4: Documentation (Week 4)**
- [ ] Create factoring SOP (Standard Operating Procedure)
- [ ] Template: Notice of Assignment
- [ ] Template: Directed Payment Authorization
- [ ] Training: When to use factoring

---

## 📞 **Recommended Factoring Companies**

**For Government Contracts:**

1. **Triumph Business Capital**
   - Specializes in government contracts
   - 85-90% advance rate
   - 1.5-3% monthly fee
   - Fast approval (24-48 hours)

2. **Fundbox**
   - Tech-forward platform
   - Up to 90% advance
   - 2-3% fee
   - Same-day funding

3. **BlueVine**
   - Government & commercial
   - 85-95% advance rate
   - Transparent pricing
   - Strong online portal

4. **Porter Capital**
   - 30+ years in government factoring
   - Directed payment specialists
   - Flexible terms
   - High approval rate

**Next Step:** Research and establish relationships with 2-3 companies before needed.

---

**Status:** DESIGN PHASE  
**Next Action:** User approval to implement in VERTEX  
**Timeline:** 2-4 weeks to fully implement  
**Dependencies:** None - can start immediately
