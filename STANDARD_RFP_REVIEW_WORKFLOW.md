# STANDARD RFP REVIEW WORKFLOW
**Dee Davis Inc. - Bidding Process**

---

## 🎯 PURPOSE

This document establishes a standardized workflow for reviewing RFPs/RFQs/ITBs to ensure we:
1. Check existing supplier relationships FIRST
2. Research new suppliers when needed
3. Get competitive quotes
4. Submit quality bids on time

---

## 📋 STANDARD WORKFLOW (7 STEPS)

### STEP 1: INITIAL RFP REVIEW (Day 1)
**Time Required:** 30-60 minutes

#### Actions:
- [ ] Read complete RFP document
- [ ] Extract critical dates (question deadline, bid deadline)
- [ ] Calculate days until bid due
- [ ] Identify product/service scope
- [ ] Note special requirements (certifications, insurance, etc.)
- [ ] Check submission method (portal, email, mail)

#### Deliverable:
Create `[PROJECT_NAME]_BID_STRATEGY.md` with:
- Critical dates
- Scope summary
- Requirements checklist
- Timeline breakdown

---

### STEP 2: CHECK EXISTING SUPPLIERS ⭐ CRITICAL
**Time Required:** 15-30 minutes

#### Actions:
- [ ] **Search GPSS SUPPLIERS table** in Airtable
  - Filter by product category
  - Filter by service type
  - Search by keywords
  - Check geographic coverage

- [ ] **Review NEXUS CONTACTS** for:
  - Past suppliers we've worked with
  - Vendors from similar bids
  - Subcontractors in related fields

- [ ] **Check previous bid documents** for:
  - Similar RFPs
  - Supplier lists used
  - Pricing history

#### Search Keywords by Category:

**Construction/Landscaping:**
- Contractors, subcontractors, landscape, concrete, asphalt, aggregate, materials

**Chemicals/Supplies:**
- Chemical, chlorine, sodium, cleaning, industrial, distribution

**Equipment:**
- Equipment, machinery, rental, tools, vehicles

**Services:**
- Service, maintenance, repair, professional, consulting

**Office/Paper:**
- Paper, office supply, stationery, wholesale

#### Python Query Template:
```python
# Search existing suppliers
suppliers = airtable.get_all_records('GPSS SUPPLIERS')

# Filter by keywords
keywords = ['your', 'keywords', 'here']
matches = [s for s in suppliers if 
    any(kw in str(s.get('CATEGORIES', '')).lower() or
        kw in str(s.get('PRODUCTS', '')).lower() or
        kw in str(s.get('COMPANY NAME', '')).lower()
        for kw in keywords)]

# Display results
for match in matches:
    print(f"{match['COMPANY NAME']} - {match.get('PHONE')}")
```

#### Deliverable:
- List of existing suppliers who can provide scope
- Contact information for immediate outreach
- If NONE found → Proceed to Step 3

---

### STEP 3: SUPPLIER RESEARCH (If Needed)
**Time Required:** 1-2 hours

#### Actions:
- [ ] Google search: "[product/service] suppliers Michigan"
- [ ] Google search: "[product/service] distributors [region]"
- [ ] Check industry associations
- [ ] Review manufacturer websites for distributors
- [ ] Search Thomasnet.com
- [ ] Check GSA Schedule suppliers
- [ ] Search BidNet Direct vendor list (if applicable)

#### Compile Supplier List With:
- Company name
- Phone number
- Email address
- Website
- Location
- Products/services offered
- Notes on capabilities

#### Target: 7-10 potential suppliers minimum

#### Deliverable:
Create `[PROJECT_NAME]_SUPPLIER_QUOTES.md` with:
- Supplier contact list
- Quote tracking table
- Evaluation criteria

---

### STEP 4: SUPPLIER OUTREACH
**Time Required:** 2-3 hours (spread over 2-3 days)

#### Contact Priority:
1. **Existing suppliers** (fastest response, known quality)
2. **Local/regional suppliers** (may offer better service)
3. **National suppliers** (often have best pricing)

#### Contact Method:
1. **Phone first** (immediate response, can clarify questions)
2. **Email follow-up** (with RFP details/specifications)
3. **Portal submission** (if supplier has online quote system)

#### Phone Script Template:
```
"Hi, this is Dee Davis with Dee Davis Inc. We're bidding on 
a [contract type] with [agency name] for [product/service]. 

Requirements: [brief scope summary]
Contract term: [duration]
Location: [delivery/work location]

Can you provide pricing? We need quotes by [date] for a 
bid due [deadline]."
```

#### Information to Request:
- [ ] Pricing (itemized if applicable)
- [ ] Delivery/shipping costs
- [ ] Lead times
- [ ] Minimum order requirements
- [ ] Payment terms
- [ ] References (similar projects)
- [ ] Certifications/licenses
- [ ] Insurance coverage

#### Deliverable:
- 3-7 quotes received
- Quote comparison spreadsheet
- Supplier capabilities verified

---

### STEP 5: QUOTE ANALYSIS & SUPPLIER SELECTION
**Time Required:** 2-3 hours

#### Actions:
- [ ] Create pricing comparison table
- [ ] Calculate total project costs (all years)
- [ ] Factor in delivery/shipping
- [ ] Check hidden costs (fees, surcharges)
- [ ] Verify supplier capabilities match requirements
- [ ] Check supplier references
- [ ] Assess reliability/responsiveness

#### Selection Criteria:
1. **Price** (competitive but not always lowest)
2. **Reliability** (can they deliver on time?)
3. **Quality** (meets specifications?)
4. **Service** (responsive, easy to work with?)
5. **References** (good track record?)
6. **Location** (local preference if applicable)
7. **Capacity** (can handle contract volume?)

#### Deliverable:
- Primary supplier selected
- Backup supplier identified
- Cost basis for bid pricing

---

### STEP 6: BID PRICING STRATEGY
**Time Required:** 1-2 hours

#### Pricing Calculation:
```
COST BASIS (from supplier):       $______

ADD:
+ Margin (10-25% typical):        $______
+ Contingency (3-5%):             $______
+ Overhead allocation:            $______

TOTAL BID PRICE:                  $______
```

#### Margin Guidelines by Type:
- **Products/Supplies:** 15-25%
- **Equipment/Materials:** 10-20%
- **Services (with labor):** 20-35%
- **Professional Services:** 30-50%
- **Subcontracting:** 10-15%

#### Considerations:
- [ ] Market rates (are we competitive?)
- [ ] Government budget (do they have funds?)
- [ ] Competition (how many bidders?)
- [ ] Relationship value (worth thin margin?)
- [ ] Risk factors (volatility, complexity)

#### Deliverable:
- Final bid price calculated
- Pricing justification documented
- Margin analysis complete

---

### STEP 7: BID PREPARATION & SUBMISSION
**Time Required:** 2-4 hours

#### Document Checklist:
- [ ] All bid forms completed
- [ ] Pricing schedules filled out
- [ ] References provided (usually 3)
- [ ] Company registration forms
- [ ] Certifications/licenses attached
- [ ] Insurance certificates included
- [ ] Required statements signed
- [ ] Addenda acknowledged
- [ ] Submission checklist reviewed

#### Quality Check:
- [ ] All required fields completed
- [ ] Calculations verified (unit × quantity = total)
- [ ] Authorized signature obtained
- [ ] Contact information accurate
- [ ] Submission deadline confirmed
- [ ] Submission method verified (portal, email, mail)

#### Submission:
- [ ] Submit 2-3 days before deadline (if possible)
- [ ] Get confirmation receipt
- [ ] Save submission confirmation
- [ ] Calendar follow-up date (award announcement)

#### Deliverable:
- Complete bid package submitted
- Confirmation received
- Bid tracking updated

---

## ⏱️ TIMELINE PLANNING

### 30-Day Bid Timeline
- **Days 1-2:** Steps 1-2 (Review RFP, check suppliers)
- **Days 3-7:** Steps 3-4 (Research suppliers, get quotes)
- **Days 8-10:** Step 5 (Analyze quotes, select supplier)
- **Days 11-12:** Step 6 (Calculate bid pricing)
- **Days 13-25:** Step 7 (Prepare bid documents)
- **Days 26-28:** Final review & submission
- **Days 29-30:** Buffer (safety margin)

### 20-Day Bid Timeline
- **Days 1-2:** Steps 1-2 (Review, check suppliers)
- **Days 3-5:** Steps 3-4 (Research, quotes)
- **Days 6-7:** Step 5 (Analysis)
- **Days 8-9:** Step 6 (Pricing)
- **Days 10-17:** Step 7 (Preparation)
- **Days 18-20:** Submission & buffer

### 10-Day Bid Timeline (Rush)
- **Day 1:** Steps 1-2 (Review, check suppliers)
- **Days 2-3:** Steps 3-4 (Research, quotes)
- **Day 4:** Step 5 (Analysis)
- **Day 5:** Step 6 (Pricing)
- **Days 6-8:** Step 7 (Preparation)
- **Days 9-10:** Submission & buffer

---

## 📊 TRACKING & DOCUMENTATION

### Required Documents per Bid:
1. **`[PROJECT]_BID_STRATEGY.md`**
   - RFP summary
   - Requirements
   - Timeline
   - Risk assessment

2. **`[PROJECT]_SUPPLIER_QUOTES.md`**
   - Supplier contact log
   - Quote comparison table
   - Selection justification

3. **`[PROJECT]_BID_SUBMISSION/`** (folder)
   - All bid forms (completed)
   - Supporting documents
   - Submission confirmation
   - Follow-up notes

### Airtable Updates:
- [ ] Add opportunity to BID TRACKING table
- [ ] Update supplier contacts in GPSS SUPPLIERS
- [ ] Log quotes received
- [ ] Track bid status
- [ ] Record outcome (win/loss)

---

## 🎯 SUCCESS METRICS

### Minimum Bid Standards:
✅ RFP fully reviewed before submitting  
✅ Existing suppliers checked FIRST  
✅ At least 2 quotes obtained  
✅ Pricing verified for accuracy  
✅ All required forms completed  
✅ Submitted before deadline  

### Ideal Bid Standards:
✅ 3+ quotes compared  
✅ Supplier references checked  
✅ Competitive pricing (market analysis done)  
✅ Backup supplier identified  
✅ Submitted 2+ days early  
✅ Questions asked (if needed)  

---

## 💡 BEST PRACTICES

### DO:
✅ Check existing suppliers FIRST (saves time, leverages relationships)  
✅ Get multiple quotes (improves pricing, reduces risk)  
✅ Read the ENTIRE RFP (don't miss requirements)  
✅ Ask questions before deadline (shows engagement)  
✅ Submit early if possible (shows professionalism)  
✅ Keep organized records (helps with future bids)  
✅ Follow up after submission (shows interest)  

### DON'T:
❌ Skip supplier research (rushing leads to bad pricing)  
❌ Rely on one quote only (no leverage, high risk)  
❌ Wait until last minute (no time for quality)  
❌ Guess at pricing (leads to losses or being non-competitive)  
❌ Ignore submission requirements (gets you disqualified)  
❌ Forget to track bids (lose follow-up opportunities)  

---

## 🔧 TOOLS & RESOURCES

### Airtable Tables:
- **GPSS SUPPLIERS** - Supplier database
- **NEXUS CONTACTS** - All contacts (officers, suppliers, etc.)
- **BID TRACKING** - Active bids and history
- **OPPORTUNITY MINING** - New opportunities

### Scripts:
- `check_chemical_suppliers.py` - Search suppliers by keywords
- `add_contacts_to_nexus.py` - Add new suppliers to system
- `nexus_backend.py` - Full system functionality

### Document Templates:
- `[PROJECT]_BID_STRATEGY.md` - Bid planning template
- `[PROJECT]_SUPPLIER_QUOTES.md` - Quote tracking template

### External Resources:
- **BidNet Direct** - Municipal bid portal
- **Thomasnet.com** - Supplier directory
- **GSA Advantage** - Federal suppliers
- **SAM.gov** - Federal contractors

---

## 📞 QUICK REFERENCE: SUPPLIER CATEGORIES

### Common Bid Categories & Where to Find Suppliers:

**Aggregate Materials (Sand, Gravel, Stone)**
- Local quarries/mines
- Construction material suppliers
- MITA (Michigan Infrastructure & Transportation Association)

**Asphalt/Concrete**
- Local ready-mix plants
- Paving contractors
- Material suppliers

**Chemicals (Industrial, Pool, Cleaning)**
- Univar Solutions
- Brenntag
- Hawkins Water Treatment
- Local chemical distributors

**Construction Services**
- Local general contractors
- Specialty subcontractors
- Construction associations

**Equipment Rental**
- United Rentals
- Sunbelt Rentals
- Local equipment dealers

**Landscape/Lawn Services**
- Local landscape contractors
- Lawn care companies
- Nurseries/suppliers

**Office Supplies/Paper**
- Regional paper wholesalers
- Office supply distributors
- National chains (Staples, Office Depot)

**Professional Services (A&E, Consulting)**
- Professional associations (AIA, ACEC)
- Local firms
- Online directories

**Road Salt**
- Detroit Salt Company
- Compass Minerals
- Cargill Salt

---

## 🚀 IMPLEMENTATION CHECKLIST

### One-Time Setup:
- [ ] Create document templates folder
- [ ] Set up Airtable supplier tracking
- [ ] Compile favorite supplier list by category
- [ ] Create bid calendar system
- [ ] Train on BidNet Direct portal

### Per-Bid Process:
- [ ] Follow 7-step workflow
- [ ] Check suppliers FIRST
- [ ] Get multiple quotes
- [ ] Document everything
- [ ] Update Airtable
- [ ] Learn from each bid

---

## 📈 CONTINUOUS IMPROVEMENT

### After Each Bid:
- [ ] Document lessons learned
- [ ] Add new suppliers to database
- [ ] Update pricing benchmarks
- [ ] Note what worked/didn't work
- [ ] Refine timeline estimates

### Monthly Review:
- [ ] Review win/loss ratio
- [ ] Analyze pricing competitiveness
- [ ] Assess supplier relationships
- [ ] Update supplier database
- [ ] Improve processes

### Quarterly Review:
- [ ] Major process improvements
- [ ] Supplier performance review
- [ ] Category analysis (what are we good at?)
- [ ] Strategic planning (what to pursue?)

---

**Version:** 1.0  
**Last Updated:** January 23, 2026  
**Owner:** Dee Davis  
**Status:** ✅ Active Standard
