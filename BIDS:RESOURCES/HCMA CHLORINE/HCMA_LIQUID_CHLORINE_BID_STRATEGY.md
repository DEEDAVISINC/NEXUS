# HCMA LIQUID CHLORINE BID STRATEGY
**ITB #2026-004 - Turtle Cove Aquatic Center**

---

## 📅 CRITICAL DATES

- **Issue Date:** January 21, 2026
- **Question Deadline:** February 4, 2026, 1:00 PM (12 days)
- **Bid Deadline:** February 18, 2026, 1:00 PM (26 days)
- **Days Until Bid:** 26 days ✅ Adequate time

---

## 📋 BID REQUIREMENTS SUMMARY

### Product Specifications
- **Product:** Sodium Hypochlorite 12.5% (Liquid Chlorine)
- **Annual Volume:** ~13,000 gallons/year
- **Delivery Size:** 900-1200 gallons per delivery
- **Deliveries per Season:** ~15 deliveries
- **Delivery Method:** Tanker truck (pumped/metered preferred)
- **Delivery Timeline:** 24-48 hours from order

### Delivery Location
**Lower Huron Metropark**  
40151 East Huron River Dr.  
Belleville, MI 48111

### Contract Terms
- **Duration:** 2 years firm pricing
- **Renewals:** Up to three 1-year options
- **Price Adjustments:** Only during renewal periods (must request within 3 months of renewal date)

### Submission Requirements
- **Platform:** BidNet Direct portal ONLY (www.bidnetdirect.com)
- **Contact:** Patty Barthelmes - patty.barthelmes@metroparks.com - (810) 644-6062
- **No email or hardcopy accepted**

---

## 🔍 STEP 1: CHECK EXISTING SUPPLIERS

### Action Items
- [ ] Query GPSS SUPPLIERS table for:
  - Chemical suppliers
  - Pool/aquatic suppliers
  - Industrial chemical distributors
  - Sodium hypochlorite suppliers
  
- [ ] Search existing contacts for:
  - Water treatment companies
  - Pool supply companies
  - Chemical distributors

### Query to Run
```python
# Check our existing supplier database
suppliers = airtable.get_all_records('GPSS SUPPLIERS')
chemical_suppliers = [s for s in suppliers if 
    'chemical' in s.get('CATEGORIES', '').lower() or
    'pool' in s.get('CATEGORIES', '').lower() or
    'water treatment' in s.get('CATEGORIES', '').lower()]
```

---

## 🏢 STEP 2: LIQUID CHLORINE SUPPLIER RESEARCH

### National Suppliers (Likely to Service Michigan)

#### 1. **Univar Solutions**
- **Type:** Major chemical distributor
- **Products:** Sodium hypochlorite, pool chemicals
- **Website:** univarsolutions.com
- **Contact:** Find local Michigan branch
- **Notes:** National distributor, bulk delivery capabilities

#### 2. **Brenntag North America**
- **Type:** Chemical distribution
- **Products:** Industrial chemicals including sodium hypochlorite
- **Website:** brenntag.com
- **Michigan Locations:** Multiple branches
- **Notes:** Large-scale bulk delivery

#### 3. **Hawkins Water Treatment Group**
- **Type:** Water treatment chemicals
- **Products:** Sodium hypochlorite, pool chemicals
- **Website:** hawkinsinc.com
- **Notes:** Municipal/commercial focus

#### 4. **Jones-Hamilton Co.**
- **Type:** Aquatic chemical manufacturer
- **Products:** Pool and spa chemicals
- **Website:** jones-hamilton.com
- **Notes:** Commercial aquatic facilities specialist

### Regional/Michigan Suppliers

#### 5. **Hasa Inc. (Michigan Distributor)**
- **Type:** Liquid chlorine specialist
- **Products:** Sodium hypochlorite for pools
- **Notes:** Need to find MI distributor

#### 6. **Superior Pool Products**
- **Location:** Novi, MI
- **Type:** Commercial pool supply
- **Products:** Bulk chemicals for commercial facilities
- **Phone:** Research needed

#### 7. **Chemtrade Chemicals**
- **Type:** Industrial chemical manufacturer
- **Products:** Sodium hypochlorite (bulk)
- **Website:** chemtradechemicals.com
- **Notes:** May have direct delivery to Michigan

#### 8. **Carus LLC**
- **Location:** Illinois (services Michigan)
- **Type:** Water treatment chemicals
- **Products:** Sodium hypochlorite
- **Website:** carusllc.com

### Local Pool/Aquatic Supply Companies

#### 9. **Spear Corporation**
- **Location:** Michigan
- **Type:** Pool equipment & chemicals
- **Products:** Commercial pool chemicals
- **Notes:** May have bulk delivery

#### 10. **Pentair Aquatic Systems**
- **Type:** Pool equipment & chemicals
- **Michigan Presence:** Yes
- **Products:** Commercial aquatics

---

## 📞 STEP 3: SUPPLIER OUTREACH STRATEGY

### Phase 1: Initial Contact (Days 1-5)
**Target: Get 5-7 quotes**

#### Contact Method
1. **Phone calls first** (faster response)
2. **Email follow-up** with specifications
3. **Request quotes within 48 hours**

#### Contact Script
```
Hi, this is Dee Davis with Dee Davis Inc. We're bidding on a 
2-year contract to supply liquid chlorine (Sodium Hypochlorite 
12.5%) to a municipal aquatic center in Belleville, Michigan.

Requirements:
- 13,000 gallons annually
- 900-1200 gallon deliveries
- 15 deliveries per season
- 24-48 hour delivery time
- Tanker truck, pumped/metered

Can you provide pricing for this volume? We need quotes by 
[DATE] for a bid due February 18th.
```

#### Information to Request
- [ ] Price per gallon (at volume)
- [ ] Delivery fees (if any)
- [ ] Minimum order requirements
- [ ] Delivery capabilities/equipment
- [ ] Lead time guarantees
- [ ] Available delivery days/times
- [ ] Payment terms
- [ ] References (commercial aquatic facilities)

### Phase 2: Quote Comparison (Days 6-10)
- [ ] Create pricing spreadsheet
- [ ] Calculate total 2-year costs
- [ ] Factor in delivery reliability
- [ ] Check supplier references
- [ ] Verify Michigan service capability

### Phase 3: Final Selection (Days 11-15)
- [ ] Select primary supplier
- [ ] Negotiate best pricing
- [ ] Get written quote confirmation
- [ ] Build margin strategy
- [ ] Prepare bid documents

---

## 💰 PRICING STRATEGY

### Cost Analysis Framework
```
Supplier Cost per Gallon:     $____
Delivery Fee (if separate):   $____
Total Cost per Delivery:      $____
Annual Cost (13K gallons):    $____

2-Year Contract Total:        $____
```

### Margin Strategy
- **Target Margin:** 15-25% (chemicals typically allow this)
- **Competitive Positioning:** Research market rates
- **Value-Adds to Justify Pricing:**
  - Reliable 24-48 hour delivery
  - Dedicated account management
  - Emergency delivery capability
  - Quality assurance/testing
  - Metered delivery (accurate billing)

### Bid Price Calculation
```
Cost Basis:                   $____
+ Margin (__%):               $____
+ Contingency (3-5%):         $____
= BID PRICE PER GALLON:       $____

Total 2-Year Bid:             $____
```

---

## 📝 BID PREPARATION CHECKLIST

### Required Documents
- [ ] Bid Form (completed)
- [ ] Reference Form (3 references)
- [ ] Offer and Agreement Form (signed)
- [ ] Vendor Registration Sheet
- [ ] Bidder Disclosure Statement
- [ ] **✅ Vendor Verification Form - CRITICAL!**
  - **Claim LOCAL PREFERENCE (we qualify!)**
  - Check if we qualify for DEI plan discount
  - Check if we qualify for living wage discount ($15+/hour)

### Company Information Needed
- [ ] Full legal business name
- [ ] Business address
- [ ] Contact information
- [ ] Michigan incorporation/Certificate of Authority
- [ ] Business license (copy)
- [ ] Insurance certificates

### Supplier Information to Include
- [ ] Supplier name and contact
- [ ] Delivery capabilities verification
- [ ] Product specifications (12.5% sodium hypochlorite)
- [ ] Delivery equipment details
- [ ] Emergency contact procedures

---

## 🎯 COMPETITIVE ADVANTAGES

### What Makes Us Competitive
1. **✅ LOCAL PREFERENCE - WE QUALIFY!** 
   - Dee Davis Inc. is located in the 5-county HCMA service region
   - This gives us bid evaluation advantage over non-local bidders
   - **MUST complete Vendor Verification Form to claim this benefit!**
   
2. **Responsive Service:** Dedicated account management

3. **Reliability:** Backup suppliers if needed

4. **Local Supplier Partnerships:** Working with Michigan-based suppliers
   - Chemtrade (River Rouge, MI - 25 min from Belleville)
   - Elite Chlorine (Michigan-only operation)
   - Brenntag (Grand Rapids, MI)

5. **Experience:** (List any relevant chemical/municipal experience)

6. **Technology:** Order tracking, delivery notifications

### Value Proposition
"Dee Davis Inc. is a LOCAL Michigan-based government contractor providing 
reliable, responsive chemical supply services with guaranteed delivery 
timelines, dedicated account support, and competitive pricing backed by 
proven supplier relationships. As a local business serving the HCMA 
5-county region, we understand the unique needs of Michigan municipal 
facilities."

---

## ⚠️ RISK ASSESSMENT

### Potential Challenges
1. **Supplier Availability:** May be limited in MI
   - **Mitigation:** Contact 7-10 suppliers, establish backup
   
2. **Delivery Equipment:** Tanker truck requirement
   - **Mitigation:** Verify supplier has proper equipment
   
3. **Price Volatility:** Chemical prices can fluctuate
   - **Mitigation:** 2-year firm pricing required, build cushion
   
4. **Seasonal Demand:** Aquatic center (seasonal?)
   - **Mitigation:** Clarify delivery schedule expectations
   
5. **Storage Requirements:** Customer must have proper storage
   - **Mitigation:** Site visit? (If allowed/needed)

---

## ❓ QUESTIONS TO ASK (Before Feb 4 Deadline)

### Operational Questions
- [ ] What are the typical delivery times/days preferred?
- [ ] Is the aquatic center seasonal or year-round?
- [ ] What is the current storage tank capacity?
- [ ] Are there any specific delivery access requirements?
- [ ] Is there a current supplier? (To understand expectations)

### Contract Questions
- [ ] Are emergency deliveries required (< 24 hours)?
- [ ] Can deliveries be scheduled in advance?
- [ ] What happens if weather prevents delivery?
- [ ] Are there penalties for late delivery?

### Pricing Questions
- [ ] Should fuel surcharges be included or separate?
- [ ] Are there any delivery fees in addition to product cost?
- [ ] How is quantity verified (metered vs estimated)?

---

## 📊 EVALUATION CRITERIA (HCMA Considers)

1. **Price** (Primary factor)
2. **Qualifications** of bidder
3. **Delivery capability**
4. **Performance data** (if available)
5. **References** from similar facilities
6. **✅ Local preference** (5-county region) - **WE QUALIFY!**
7. **Diversity/Inclusion plan** (if applicable)
8. **Living wage payment** ($15+/hour)

### Vendor Verification Form Benefits
- **✅ LOCAL PREFERENCE - WE QUALIFY!** 
  - Dee Davis Inc. is in the 5-county region (Livingston, Macomb, Oakland, Washtenaw, Wayne)
  - This gives us bid evaluation advantage
  
- **Bid Discount:** If we have diversity/inclusion plan (check if applicable)
- **Bid Discount:** If we pay $15+/hour living wage (check if applicable)

**CRITICAL ACTION:** 
✅ **MUST complete Vendor Verification Form to claim local preference!**
✅ Check if we qualify for additional benefits (DEI plan, living wage)
✅ Complete form even for benefits we don't claim (required acknowledgment)

---

## 📅 EXECUTION TIMELINE

### Week 1 (Jan 23-29)
- [ ] Day 1-2: Search existing GPSS SUPPLIERS database
- [ ] Day 2-3: Research and compile supplier contact list
- [ ] Day 3-5: Call/email all suppliers for quotes
- [ ] Day 5-7: Follow up on quote requests

### Week 2 (Jan 30 - Feb 5)
- [ ] Day 8-9: Analyze all quotes received
- [ ] Day 10: Select primary supplier, negotiate
- [ ] Day 11: Calculate bid pricing with margin
- [ ] Day 12: Prepare questions for HCMA (submit by Feb 4)

### Week 3 (Feb 6-12)
- [ ] Day 13-14: Review Q&A addendum (if issued)
- [ ] Day 15-16: Finalize pricing strategy
- [ ] Day 17: Complete all bid forms
- [ ] Day 18: Gather references
- [ ] Day 19: Collect company documents

### Week 4 (Feb 13-18)
- [ ] Day 20-22: Final bid package review
- [ ] Day 23: Register on BidNet Direct (if not already)
- [ ] Day 24: Upload complete bid package
- [ ] Day 25: Verify submission confirmation
- [ ] **Day 26: BID DEADLINE - Feb 18, 1:00 PM**

---

## 🎯 SUCCESS CRITERIA

### Minimum Requirements to Submit
✅ At least 2 qualified supplier quotes  
✅ Competitive pricing (within market range)  
✅ Delivery capability verified (tanker truck, 24-48 hrs)  
✅ All bid forms completed and signed  
✅ 3 references provided  
✅ BidNet Direct registration complete  

### Ideal Position
✅ 3-5 supplier quotes for comparison  
✅ Pricing 5-15% below market average (if possible)  
✅ Local supplier (5-county region) if available  
✅ Past aquatic/municipal experience to reference  
✅ Backup supplier identified  

---

## 📁 FILE LOCATIONS

- **RFP PDF:** `photos_and_videos/ITB 2026-004 Liquid Chlorine.pdf`
- **Bid Strategy:** `HCMA_LIQUID_CHLORINE_BID_STRATEGY.md` (this file)
- **Supplier Quotes:** Create `HCMA_CHLORINE_SUPPLIER_QUOTES.md`
- **Bid Package:** Create `HCMA_CHLORINE_BID_SUBMISSION/` folder

---

## 🚀 NEXT IMMEDIATE ACTIONS

### TODAY (Jan 23, 2026)
1. ✅ Review complete RFP (DONE)
2. 🔄 **Search GPSS SUPPLIERS table for chemical suppliers**
3. 🔄 **Create supplier contact list (10 companies)**
4. 🔄 **Begin calling suppliers for quotes**

### TOMORROW (Jan 24, 2026)
5. Continue supplier outreach
6. Create pricing comparison spreadsheet
7. Register on BidNet Direct portal

---

## 💡 LESSONS LEARNED / PROCESS IMPROVEMENT

### Standard RFP Review Process (Going Forward)
1. **Extract key dates and requirements**
2. **Check existing GPSS SUPPLIERS table first** ⭐ 
3. **Research new suppliers if needed**
4. **Create supplier outreach list**
5. **Get multiple quotes**
6. **Analyze pricing and build margin**
7. **Submit competitive bid**

### System Integration Ideas
- Add "Chemical Suppliers" category to GPSS SUPPLIERS
- Track supplier response times
- Build supplier relationship scores
- Automate RFP alert system
- Create bid templates by category

---

**STATUS:** 📋 Ready to Begin Supplier Search  
**OWNER:** Dee Davis  
**PRIORITY:** Medium (26 days available)  
**WIN PROBABILITY:** TBD after supplier research
