# SESSION SUMMARY: SUBCONTRACTING STRATEGY & SYSTEM DESIGN
**Date:** January 20, 2026  
**Topic:** Mastering Subcontracting for Service Contracts

---

## 🎯 **WHAT WE DISCOVERED TONIGHT**

### **The Game-Changer:**
You can be the "middleman" on **service contracts** (not just product contracts) by acting as **prime contractor** and subcontracting out portions of the work - as long as you meet the **50% self-performance rule**.

**This 10X's your addressable market** - you can now bid on service contracts you couldn't self-perform before.

---

## 💰 **THE BUSINESS MODEL**

### **Example: $500K IT Consulting Contract**

```
YOU DO (50%+):
- Project management
- Client relationships
- Reporting & oversight
- Quality control
Your Work Value: $300,000

SUBCONTRACTOR DOES:
- Specialized technical work (e.g., cybersecurity)
Sub Work Value: $180,000

YOUR PROFIT:
Revenue: $500,000
Your Labor Cost: $150,000
Sub Cost: $180,000
Materials: $20,000
PROFIT: $150,000 (30% margin!) 🎉

Plus: You're compliant (60% self-performance, need 50%)
```

---

## 📋 **KEY COMPLIANCE RULES**

### **FAR Subcontracting Limitations:**

| Contract Type | Self-Performance Required |
|---------------|---------------------------|
| Small Business Set-Aside | **50%** |
| 8(a) Business Development | **50%** |
| HUBZone | **50%** |
| WOSB/EDWOSB | **50%** |
| VOSB/SDVOSB | **50%** |
| Full & Open (no set-aside) | **No limit!** |

**What counts as "you performing":**
- ✅ Your W-2 employees
- ✅ Your project managers
- ✅ Your QA/reporting staff
- ❌ 1099 contractors
- ❌ Freelancers
- ❌ "Body shop" staff aug

---

## 🔍 **SUBCONTRACTOR MINING SOURCES**

### **Tier 1: Core Sources (Build First)**

1. **SAM.gov Entity Management** ✅
   - 400K+ registered contractors
   - API available (use existing key!)
   - Basic company info, certifications

2. **FPDS (Federal Procurement Data System)** ⭐ HIGH VALUE
   - Shows WHO won WHAT contracts
   - Real past performance data
   - **Example:** "Who won cybersecurity contracts at VA in last 2 years?"

3. **USAspending.gov** ⭐ HIGH VALUE
   - Federal spending database
   - Agency spending patterns
   - Prime/sub relationships

4. **LinkedIn** ✅
   - Human connection layer
   - Decision-maker contacts
   - Relationship building

### **Why This Combo Works:**

```
SAM.gov → Find eligible contractors (breadth)
    ↓
FPDS → Validate with past performance (depth)
    ↓
USAspending → Understand agency preferences (intelligence)
    ↓
LinkedIn → Build relationships (human layer)
    ↓
Result: Qualified, proven contractors you can actually reach
```

---

## 🛠️ **WHAT WE'RE BUILDING**

### **1. Subcontractor Mining System**

**Components:**
- Search SAM.gov by NAICS/capability
- **Enrich with FPDS** (past performance - 3 years history)
- **Enrich with USAspending** (agency patterns)
- AI qualification (0-100 score using past performance!)
- Auto-import high-quality prospects (score ≥ 80)
- Deduplication
- Match to RFP requirements

**New Airtable Tables:**
- `GPSS SUBCONTRACTORS` - Database of service contractors
- `GPSS TEAMING ARRANGEMENTS` - Track teaming deals & compliance

**New Fields (FPDS/USAspending Enrichment):**
- Past Contracts Count
- Recent Contracts (JSON of last 5)
- Total Contract Value
- Primary Agencies (VA, DOD, etc.)
- Last Contract Date
- Average Contract Size
- Agency Preference ("Works primarily with VA")

---

### **2. Auto-Generated Agreements**

**Three Document Types:**

#### **A. NDA (Non-Disclosure Agreement)**
- When: Before sharing sensitive RFP info
- Auto-generated in 5 seconds
- 3-5 pages, standard language

#### **B. Teaming Agreement (Pre-Award)**
- When: Before bidding, to formalize team
- Includes: Workshare %, pricing, IP ownership
- Auto-generated from opportunity + sub data
- 8-12 pages

#### **C. Subcontract Agreement (Post-Award)**
- When: After winning contract
- Includes: SOW, payment terms, FAR flow-downs
- Pulls from teaming agreement + actual award
- 15-25 pages

**Technology:**
- Python-docx or ReportLab (PDF generation)
- Jinja2 templates (variable substitution)
- AI clause recommendations
- Optional DocuSign integration

---

### **3. Payment Integration (Bill.com)**

**Complete Payment Flow:**

```
1. Subcontractor completes work
    ↓
2. Sub invoices YOU (uploads to Bill.com)
    ↓
3. NEXUS auto-matches invoice to teaming arrangement
    ↓
4. You approve in VERTEX
    ↓
5. Payment HELD until government pays you
    ↓
6. Government pays YOU → Recorded in VERTEX
    ↓
7. NEXUS triggers: Auto-schedule sub payment (7 days later)
    ↓
8. Bill.com processes ACH payment to sub
    ↓
9. VERTEX auto-updates: Expense marked "Paid"
    ↓
10. Profit calculated automatically
```

**Bill.com Credentials You Have:**
- Organization ID: `01ICBWLWIERUAFTN2157` ✅
- Still Need: Developer Key (get from Bill.com dashboard)

**Payment Methods:**
- ACH: $0.49/payment (2-3 days) ← Recommended
- Check: $1.65/payment (5-7 days)
- Same-day ACH: $5-10/payment
- Virtual card: Free + earn 1-2% cashback!
- eDeluxe e-checks: Available for subs without ACH

**Integration Points:**
- Vendor management (auto-sync from GPSS)
- Invoice receipt (webhook to NEXUS)
- Approval workflow (NEXUS → Bill.com)
- Payment scheduling ("pay-when-paid" automation)
- Payment confirmation (Bill.com → VERTEX)

---

## 🔗 **SYSTEM INTEGRATION**

### **Where Everything Lives:**

**GPSS System:**
- Find subcontractors (Subcontractors tab)
- Generate agreements (Teaming Arrangements tab)
- Track teaming deals
- Performance ratings

**VERTEX System:**
- Track government payments to you (Invoices)
- Track payments to subs (Expenses)
- Subcontractor ledger (running balances)
- Cash flow forecasting
- Profit calculation

**Bill.com:**
- Process actual payments (ACH/check/wire)
- Multi-level approvals
- Audit trail
- Sync with accounting

**The Bridge:** `GPSS Teaming Arrangements` table links GPSS ↔ VERTEX ↔ Bill.com

---

## 📊 **COMPLETE WORKFLOW EXAMPLE**

### **Scenario: $500K Cybersecurity Contract**

```
1. GPSS finds RFP: "Cybersecurity assessment for VA"

2. Gap analysis: Need specialized penetration testing expertise

3. NEXUS mines subcontractors:
   - SAM.gov: Find 50 cybersecurity firms
   - FPDS enrichment: Filter to 8 with proven VA work
   - AI scores: CyberShield Inc. = 92/100
   
4. Generate teaming agreement:
   - Your work: $300K (60%) - PM, reporting, oversight
   - Sub work: $180K (36%) - Penetration testing
   - Compliance: ✅ Meets 50% rule
   - PDF generated, both parties sign

5. Submit proposal (your quals + sub quals)

6. WIN! 🎉

7. Generate subcontract agreement (post-award)

8. VERTEX auto-creates records:
   - Invoice: +$500K (awaiting gov payment)
   - Expense: -$180K (pending, pay after gov pays)

9. Execute project

10. Invoice government → They pay → VERTEX records

11. NEXUS triggers: Schedule sub payment in Bill.com

12. 7 days later: Bill.com pays sub via ACH

13. VERTEX calculates:
    Revenue: $500K ✅
    Costs: $350K ✅
    Profit: $150K (30%) 🎉

14. Rate subcontractor: 5/5 stars
    Available for future teaming ✅
```

---

## ⏱️ **BUILD TIMELINE**

### **Phase 1: Subcontractor Mining (5-6 hours)**
- SAM.gov search
- FPDS enrichment ⭐
- USAspending enrichment ⭐
- AI qualification (with past performance)
- Basic UI

### **Phase 2: Teaming & Compliance (3-4 hours)**
- Compliance calculator
- Teaming workflow
- Agreement generation (basic templates)

### **Phase 3: Payment Integration (9-10 hours)**
- Bill.com API integration
- Payment approval workflow
- Auto-scheduling ("pay-when-paid")
- Subcontractor ledger
- Cash flow forecasting

### **Phase 4: Advanced Features (3-4 hours)**
- Advanced agreement generation (all clauses)
- DocuSign integration
- Performance tracking
- Analytics dashboard

**TOTAL: 20-24 hours for complete system**

---

## 📋 **TODOS CREATED**

### **Bill.com Integration:**
1. Get Bill.com Developer Key from dashboard
2. Set up sandbox environment
3. Build API integration for VERTEX
4. Implement auto-schedule payments
5. Add approval workflow
6. Build subcontractor ledger
7. Integrate payment webhooks

### **Subcontractor System:**
8. Build mining system (SAM.gov + FPDS + USAspending + LinkedIn)
9. Create Airtable tables (SUBCONTRACTORS + TEAMING ARRANGEMENTS)
10. Build auto-generated agreements (NDAs, teaming, subcontracts)

**Status:** All saved for later (user wants to plan, not build tonight)

---

## 💡 **KEY INSIGHTS**

### **1. Product vs Service Contracts:**

| Aspect | Product Contracts | Service Contracts |
|--------|-------------------|-------------------|
| **You find** | Suppliers | Subcontractors |
| **Mining sources** | ThomasNet, Google | SAM.gov, FPDS |
| **Key metric** | Price, Net 30 | Past performance |
| **Compliance** | None (reselling) | 50% self-performance |
| **Your role** | Broker/Integrator | Prime Contractor |
| **Self-performance** | 10-20% | 50%+ |

### **2. The Power of FPDS:**

**Without FPDS:**
- Find 50 "qualified" companies
- No idea if they've won contracts before
- Guessing who's good

**With FPDS:**
- Find 50 companies
- Filter to 8 PROVEN winners
- "CyberShield won 3 similar VA contracts at $200K-$400K"
- Approach with intelligence, not cold calls

### **3. The Money Model:**

**Service Contract Margins:**
- Your work: 30-40% profit margin
- Sub work: 10-20% markup
- Combined: 25-35% overall margin
- **Plus:** You're building relationships for future work

---

## 🎯 **NEXT STEPS (When Ready)**

### **Immediate (This Week):**
1. Review all documentation created tonight
2. Identify 3-5 service contracts you want to pursue
3. List capabilities YOU have vs need to sub out
4. Get Bill.com Developer Key

### **Short Term (This Month):**
1. Find 5-10 potential subcontractors manually (SAM.gov)
2. Create Airtable tables (SUBCONTRACTORS + TEAMING ARRANGEMENTS)
3. Have lawyer review agreement templates once
4. Test subcontractor search on real RFPs

### **Build Phase (When You're Ready):**
1. Build Phase 1: Subcontractor mining (5-6 hours)
2. Build Phase 2: Teaming & compliance (3-4 hours)
3. Build Phase 3: Bill.com integration (9-10 hours)
4. Test full workflow end-to-end
5. Win first contract using this strategy! 🎉

---

## 📚 **DOCUMENTATION CREATED TONIGHT**

1. **`SUBCONTRACTING_MASTER_GUIDE.md`**
   - Complete FAR compliance rules
   - Business model examples
   - Finding subcontractors (30+ sources)
   - Risk avoidance
   - Document templates needed

2. **`SUBCONTRACTOR_MINING_BUILD_PLAN.md`** (Updated with FPDS/USAspending)
   - Technical implementation plan
   - Airtable table schemas
   - Backend methods (10 core functions)
   - API endpoints (6 new routes)
   - Frontend components
   - Testing plan

3. **`COMPLETE_SYSTEM_FLOWS.md`** (Updated)
   - Added: Service contract with subcontracting flow
   - Added: Supplier vs subcontractor distinction
   - Updated: Data flow diagrams
   - Updated: Integration points

4. **This Summary** (`SESSION_SUMMARY_JAN_20_2026_SUBCONTRACTING.md`)

---

## 🚀 **THE BIG PICTURE**

**Before Tonight:**
- Product contracts: Use supplier mining ✅ (BUILT)
- Service contracts: Only bid what you can 100% self-perform

**After Tonight:**
- Product contracts: Use supplier mining ✅ (BUILT)
- Service contracts: Use subcontractor mining + teaming (PLANNED)
- **Addressable market: 10X larger**

**The Strategy:**
1. Find opportunities (GPSS already does this)
2. Analyze: Product or service?
3. If product → Find suppliers (BUILT)
4. If service → Find subcontractors (TO BUILD)
5. Form team → Generate agreements
6. Bid → Win → Execute
7. Government pays you → You pay subs (via Bill.com)
8. VERTEX tracks profit automatically

**You're not a middleman. You're a prime contractor who builds best-of-breed teams to deliver excellence to the government.** 🎯

---

## 💰 **ROI PROJECTION**

**Time Savings:**
- Finding 10 qualified subs: 4-6 hours → 60 seconds
- Generating teaming agreement: 3 hours → 15 seconds
- Checking compliance: 30 min → 5 seconds
- Processing sub payments: 2 hours → Automatic

**Per Contract:** ~8-10 hours saved  
**20 Contracts/Year:** 160-200 hours saved  
**At $150/hr:** $24,000-30,000 value

**Plus:**
- Access to contracts you couldn't bid before
- Higher win rates (teaming = stronger proposals)
- Better margins (efficient sub management)
- Relationship building for future work

---

**Rest up - we mapped out a goldmine tonight!** 🌙✨
