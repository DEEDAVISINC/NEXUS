# SUBCONTRACTING & TEAMING STRATEGY
## The "Middleman" Mastery Guide for Service Contracts

**Created:** January 20, 2026  
**Purpose:** Master the art of winning service contracts and subbing out portions while staying compliant

---

## 🎯 THE CORE CONCEPT

**You act as the PRIME CONTRACTOR:**
- Win the government contract
- Manage the overall project
- Sub out specialized portions to partners
- Take margin on the whole contract value

**Example:**
- Contract: $500K IT consulting (12 months)
- You perform: $250K (project management, reporting, 50%)
- Subcontractor: $200K (specialized coding, 40%)
- **Your profit:** $50K margin (10%) + your own labor = $100K total

---

## 📋 FAR SUBCONTRACTING LIMITATIONS BY CONTRACT TYPE

### **1. SMALL BUSINESS SET-ASIDE (Most Common)**

**Rule:** Prime must perform **at least 50%** of the contract cost with its own employees.

**What This Means:**
- $500K contract → You must do $250K yourself
- Can sub out: Up to $250K (50%)
- Compliance: Track labor hours, not just dollars

**Best Strategy:**
- You do: PM, reporting, client meetings, oversight
- Sub does: Technical work, specialized tasks
- Your role: "Manage and control" the project

---

### **2. 8(a) BUSINESS DEVELOPMENT CONTRACTS**

**Rule:** 
- **Services:** Prime must perform at least **50%** with own employees
- **General construction:** Prime must perform at least **15%**
- **Special trade construction:** Prime must perform at least **25%**

**Additional Rules:**
- Can't subcontract to non-8(a) firms without approval
- "Ostensible subcontractor" rule - can't have subs doing all the work
- Must show capability to perform prime portion

---

### **3. HUBZONE CONTRACTS**

**Rule:** 
- **Services:** Prime must perform at least **50%**
- At least **50% of personnel** must reside in HUBZone
- Can sub to other small businesses

**Key Point:** If YOU are HUBZone-certified, you must keep that advantage while subbing.

---

### **4. WOMEN-OWNED SMALL BUSINESS (WOSB)**

**Rule:** 
- **Services:** Prime must perform at least **50%**
- Can sub to any size business
- Must maintain WOSB certification

---

### **5. VETERAN-OWNED SMALL BUSINESS (VOSB/SDVOSB)**

**Rule:** 
- **Services:** Prime must perform at least **50%**
- Can sub to anyone
- Must maintain VOSB certification and veteran ownership/control

---

### **6. FULL AND OPEN (No Set-Aside)**

**Rule:** **NO LIMITATIONS!** 🎉
- Can sub out 100% if you want (though not recommended)
- Only requirement: Must show you can manage the contract
- Most flexibility for teaming

---

## 🔑 KEY COMPLIANCE REQUIREMENTS

### **What Counts as "You Performing":**

✅ **YES, This Counts:**
- Your W-2 employees doing the work
- Your project managers overseeing subs
- Your QA team reviewing deliverables
- Your admin team handling reporting

❌ **NO, This Doesn't Count:**
- 1099 contractors (considered subcontractors)
- Freelancers on short-term contracts
- "Body shop" staff augmentation
- Your cousin "helping out"

### **How to Calculate the 50%:**

**Method 1: Cost Incurred (Most Common)**
```
Your Performance % = (Your Labor Cost) / (Total Contract Cost)

Example:
Total Contract: $500,000
Your Labor: $280,000 (salaries, benefits, overhead)
Sub Labor: $180,000
Your Materials: $40,000

Your %: $280K / $500K = 56% ✅ COMPLIANT
```

**Method 2: Personnel (for certain contracts)**
```
Your Performance % = (Your Hours) / (Total Hours)

Example:
Total Hours: 2,080 (1 FTE for 1 year)
Your Hours: 1,100
Sub Hours: 980

Your %: 1,100 / 2,080 = 53% ✅ COMPLIANT
```

---

## 💰 THE BUSINESS MODEL

### **How You Make Money:**

**Revenue Streams:**
1. **Your own labor:** Bill at market rate ($100-200/hr)
2. **Management fee:** 10-20% markup on sub work
3. **Risk premium:** You hold the contract, you get paid for that risk

**Example Breakdown:**
```
Contract Value: $500,000

YOUR WORK:
- Project Manager (you): 500 hrs × $150/hr = $75,000
- Technical Lead (employee): 800 hrs × $125/hr = $100,000
- Admin/Reporting: $25,000
YOUR TOTAL: $200,000

SUBCONTRACTOR WORK:
- Specialized Developer: $150,000 (your cost)
- You markup 20%: Bill to contract at $180,000

CONTRACT EXPENSES:
- Materials/Software: $40,000
- Travel: $10,000
- Total Expenses: $50,000

MATH:
Revenue: $500,000
Your Labor Cost: $150,000 (actual cost to you)
Sub Cost: $150,000
Expenses: $50,000
PROFIT: $150,000 (30% margin!)

Plus you performed 60% yourself ($280K / $500K) ✅
```

---

## 🤝 TYPES OF SUBCONTRACTING RELATIONSHIPS

### **1. Traditional Subcontractor**
- You win contract, hire them after award
- You control scope, pricing, deliverables
- Most flexible, highest margin

### **2. Teaming Agreement (Pre-Award)**
- Form team BEFORE bidding
- Submit joint proposal
- Negotiate workshare/pricing upfront
- Lower risk, lower margin

### **3. Joint Venture**
- Create new legal entity together
- Share ownership, liability, profit
- For LARGE contracts ($5M+)
- Complex but powerful

### **4. Mentor-Protégé**
- You're the protégé, large firm mentors
- Get access to their past performance
- Split work, but they help you grow
- SBA-approved programs (8(a), All Small)

---

## 🎯 NEXUS SUBCONTRACTOR SYSTEM (What We Need to Build)

### **New Airtable Table: `GPSS SUBCONTRACTORS`**

**Fields:**
```
COMPANY NAME (text) - Primary key
BUSINESS TYPE (single select) - Small Business, 8(a), HUBZone, WOSB, VOSB, Large
CORE CAPABILITIES (multi-select) - IT Support, Software Dev, Cybersecurity, PM, etc.
PAST PERFORMANCE (long text) - Their relevant contracts
SAM.GOV CAGE CODE (text) - Required for subbing
SAM.GOV STATUS (single select) - Active, Expired, Not Registered
CERTIFICATIONS (multi-select) - ISO 9001, CMMI, security clearances
PRIMARY CONTACT (text)
EMAIL (email)
PHONE (phone)
HOURLY RATES (long text) - By role (PM: $100/hr, Dev: $125/hr)
AVAILABILITY (single select) - Available, Busy, Not Available
RELATIONSHIP STAGE (single select) - Prospect, Teaming Partner, Active Sub, Past Sub
TEAMING AGREEMENTS (attachment) - Signed agreements
PAST PROJECTS TOGETHER (number) - How many times worked together
PERFORMANCE RATING (rating 1-5) - How well they delivered
COMPLIANCE RISK (single select) - Low, Medium, High
NOTES (long text)
CREATED DATE (date)
LAST CONTACTED (date)
```

### **New Table: `GPSS TEAMING ARRANGEMENTS`**

**Fields:**
```
OPPORTUNITY ID (linked to Opportunities)
PRIME CONTRACTOR (single select) - Us or Them
SUBCONTRACTOR (linked to GPSS SUBCONTRACTORS)
WORKSHARE % (number) - What % they're doing
CONTRACT VALUE (currency) - Total opportunity value
SUB VALUE (currency) - Their portion
OUR VALUE (currency) - Our portion
TEAMING AGREEMENT (attachment) - Signed document
STATUS (single select) - Proposed, Agreed, Active, Complete
COMPLIANCE CHECK (checkbox) - Meets 50% rule?
NOTES (long text)
```

---

## 🔄 UPDATED SERVICE CONTRACT FLOW

### **NEW FLOW: Service Contract with Subcontracting**

```
START: GPSS finds service RFP
    ↓
1. AI analyzes RFP
   - Type: IT consulting, 12 months, $500K
   - Requirements: Project management, software dev, cybersecurity
   - Set-Aside: Small Business (50% rule applies)
    ↓
2. Capability Analysis (NEW):
   - What can WE do? PM, reporting, oversight
   - What do we NEED to sub? Specialized cybersecurity
   - Calculate: Can we meet 50% rule?
    ↓
3. Search Subcontractor Database (NEW):
   - Query: GPSS SUBCONTRACTORS table
   - Filter: Cybersecurity capability, available, good rating
   - Find: 5-10 potential partners
    ↓
4. Cost Estimation (NEW):
   - Our portion: $280K (56% - compliant!)
   - Sub portion: $180K (34%)
   - Profit margin: $40K (8%)
    ↓
5. Contact subcontractor:
   - Send teaming agreement
   - Get their commitment, rates, past performance
   - Store in: GPSS Teaming Arrangements
    ↓
6. Generate proposal:
   - Include: Our qualifications + sub qualifications
   - Show: Combined past performance
   - Price: $500K with compliant workshare
    ↓
7. Submit (with SF 1420 if required)
    ↓
8. If won:
   - Sign: Prime contract with government
   - Sign: Subcontract with partner
   - Execute: Project with compliant workshare tracking
    ↓
9. Track in VERTEX:
   - Revenue: $500K from government
   - COGS: $150K (sub cost) + $150K (our labor cost)
   - Profit: $200K (40%!)
    ↓
END: Contract complete, relationship strengthened
```

---

## ⚠️ COMPLIANCE RISKS TO AVOID

### **🚨 VIOLATION #1: "Ostensible Subcontractor"**

**What It Is:** 
- Sub does all the work, you just put your name on it
- You're basically a pass-through
- SEVERE consequences (debarment, fines)

**How to Avoid:**
- Actually manage the project
- Have your PMs involved daily
- Control quality, deliverables, client relationship

---

### **🚨 VIOLATION #2: Failure to Meet 50% Rule**

**What It Is:** 
- You sub out 60% of a small business contract
- Doesn't matter if you didn't mean to
- Can lose contract + face penalties

**How to Avoid:**
- Track labor hours in real-time
- Build in 10% buffer (target 60% if rule is 50%)
- Use NEXUS to auto-calculate compliance

---

### **🚨 VIOLATION #3: Bait and Switch**

**What It Is:** 
- Propose one sub in bid
- Switch to different sub after award (without approval)
- Or sub doesn't actually do the work

**How to Avoid:**
- Honor commitments in proposal
- If must change, get CO (Contracting Officer) approval
- Document everything

---

### **🚨 VIOLATION #4: Affiliation Issues**

**What It Is:** 
- You and your "sub" are actually one company (common owner, shared resources)
- Tries to get around small business rules
- SBA will disqualify you

**How to Avoid:**
- Use legitimate, independent subs
- Don't use your spouse's company as a sub
- Don't share employees/office space

---

## 🎯 FINDING SUBCONTRACTORS

### **Where to Find Them:**

1. **SAM.gov Dynamic Small Business Search**
   - Search by: NAICS, capabilities, certifications
   - Filter: Active registrations only
   - Export: Contact info

2. **Industry Associations**
   - NDIA (National Defense Industrial Association)
   - PSC (Professional Services Council)
   - Local chambers of commerce

3. **Reverse Industry Days**
   - Large primes looking for small business subs
   - Great for building relationships

4. **LinkedIn / Networking**
   - Search: "Government contractor + [capability]"
   - Join: GovCon groups

5. **Past Proposal Losers**
   - Lost a bid? Contact winning team's subs from their proposal
   - Or team with other losers for next bid

---

## 🏗️ NEXUS FEATURES TO BUILD

### **Phase 1: Subcontractor Database (Similar to Suppliers)**

**New API Endpoints:**
```python
POST /gpss/subcontractors/search
- Search by capability, certification, availability

POST /gpss/subcontractors/create
- Add new subcontractor to database

POST /gpss/subcontractors/mine-sam-gov
- Auto-import from SAM.gov by NAICS/capability

GET /gpss/subcontractors/{id}
- Get subcontractor details

PUT /gpss/subcontractors/{id}/rate
- Rate their performance after project
```

---

### **Phase 2: Teaming Automation**

**Features:**
```
1. Auto-calculate compliance:
   - Input: Contract value, your hours, sub hours
   - Output: "58% self-performance ✅ COMPLIANT"

2. Cost calculator:
   - Input: Sub hourly rates, hours needed
   - Output: Total cost, markup, final price

3. Teaming agreement generator:
   - Template: Standard teaming agreement
   - Auto-fill: Company names, percentages, scope
   - Output: PDF ready to sign

4. Compliance tracker:
   - During contract: Log hours by employee vs sub
   - Alert: "Warning: Approaching 50% limit"
   - Report: Generate for CO audits
```

---

### **Phase 3: Smart Matching**

**AI-Powered Subcontractor Recommendations:**
```
Input: RFP for "Cybersecurity assessment, $300K"
Output:
  1. CyberShield Inc. (92% match)
     - Capability: Cybersecurity ✅
     - Availability: Available ✅
     - Past performance: 4.8/5 stars
     - Estimated cost: $120K
     - Your margin: $30K

  2. SecureNet Solutions (87% match)
     - Capability: Cybersecurity ✅
     - Availability: Partially available
     - Past performance: 4.5/5 stars
     - Estimated cost: $135K
     - Your margin: $22K

  3. ...
```

---

## 📊 WORKSHARE CALCULATOR (Build This)

**Input:**
- Contract value: $500,000
- Contract type: Small Business Set-Aside
- Your labor hours: 1,200
- Sub labor hours: 880
- Your hourly rate: $125
- Sub hourly rate: $100

**Calculation:**
```
Your cost: 1,200 × $125 = $150,000
Sub cost: 880 × $100 = $88,000
Total labor: $238,000

Your %: $150K / $238K = 63% ✅ COMPLIANT (need 50%)

Profit available: $500K - $238K = $262K
Minus expenses (10%): $50K
Net profit: $212K (42% margin!)
```

**Output:**
✅ COMPLIANT with 50% rule (performing 63%)  
💰 Estimated profit: $212,000  
⚠️ Buffer: 13% above minimum (safe zone)

---

## 🎓 STRATEGIES FOR MAXIMUM PROFIT

### **Strategy 1: "Lead-Manage-Collect"**
- You: Do the PM, reporting, client-facing work (lightweight)
- Sub: Do the heavy lifting (technical work)
- Margin: 15-25%

### **Strategy 2: "Core + Specialized"**
- You: Do 70% (core work you're good at)
- Sub: Do 30% (specialized niche you don't have)
- Margin: 10-15%
- Benefit: Build your team's capabilities

### **Strategy 3: "Multiple Small Subs"**
- You: 50% PM and coordination
- Sub A: 20% (database work)
- Sub B: 15% (frontend)
- Sub C: 15% (testing)
- Margin: 12-18%
- Benefit: Not dependent on one sub

### **Strategy 4: "Past Performance Borrowing"**
- You: New to this agency/work
- Sub: Has 10 years of past performance
- You: Lead with their credentials in proposal
- Margin: Lower (10%) but you WIN
- Benefit: Build YOUR past performance for next time

---

## 📋 DOCUMENTS YOU NEED

### **1. Teaming Agreement (Before Award)**
- Who does what
- Workshare %
- Pricing
- IP ownership
- Termination clauses

### **2. Subcontract Agreement (After Award)**
- Legal contract with sub
- Flow-down clauses (FAR requirements)
- Payment terms
- Performance metrics

### **3. SF 1420 (Performance & Payment Bonds)**
- Required for construction contracts
- Sometimes required for large service contracts

### **4. Small Business Subcontracting Plan**
- Required for contracts > $750K
- Shows how you'll use small business subs

---

## 🚀 IMMEDIATE ACTION ITEMS

### **This Week:**
1. ✅ Read this guide fully
2. [ ] Identify 3-5 service contracts you want to pursue
3. [ ] List capabilities YOU can do vs need to sub
4. [ ] Find 5 potential subcontractors on SAM.gov
5. [ ] Add them to a spreadsheet (we'll import to NEXUS)

### **Next Week:**
1. [ ] Build GPSS SUBCONTRACTORS table in Airtable
2. [ ] Import your 5 subs
3. [ ] Build compliance calculator (50% rule checker)
4. [ ] Create teaming agreement template

### **This Month:**
1. [ ] Find 10 more subcontractors across different capabilities
2. [ ] Send intro emails to start relationships
3. [ ] Test full flow: Find RFP → Find sub → Calculate compliance → Bid
4. [ ] Win first contract using this strategy

---

## 💡 THE BIG PICTURE

**This changes everything:**

**Before:** 
- Only bid on contracts you can 100% self-perform
- Limited to your current capabilities
- Miss out on $500K+ contracts

**After:**
- Bid on ANY contract where you can manage 50%+
- Partner with specialists for gaps
- Win $500K-$5M contracts
- Build relationships for future work

**The key:** You're not a "middleman" - you're a **prime contractor** who assembles best-of-breed teams to deliver excellence to the government.

---

## ✅ MASTER CHECKLIST

- [ ] Understand 50% rule for your certification type
- [ ] Build subcontractor database (20+ contacts)
- [ ] Create standard teaming agreement template
- [ ] Build compliance calculator in NEXUS
- [ ] Track workshare on every contract
- [ ] Rate subcontractors after each project
- [ ] Build long-term relationships (not transactional)
- [ ] Always have backups (2-3 subs per capability)
- [ ] Document EVERYTHING (for CO audits)
- [ ] Consult lawyer for first few teaming agreements

---

**You're about to unlock 10X more opportunities. This is how you scale.** 🚀
