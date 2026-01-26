# GPSS SUBCONTRACTOR MINING SYSTEM
## Complete Build Plan - Auto-Find Service Partners

**Created:** January 20, 2026  
**Purpose:** Build automated system to find, qualify, and manage subcontractors for service contracts

---

## 🎯 SYSTEM OVERVIEW

**What It Does:**
- Automatically finds subcontractors on SAM.gov by capability/NAICS
- Extracts contact info, certifications, past performance
- AI-powered qualification scoring (0-100)
- Auto-imports high-quality prospects
- Matches subs to RFP requirements
- Calculates compliance with 50% rule
- Tracks teaming relationships

**Similar to supplier mining, but for SERVICE contractors instead of product suppliers.**

---

## 🗂️ AIRTABLE TABLES

### **Table 1: `GPSS SUBCONTRACTORS`**

**Required Fields (ALL CAPS):**
```
COMPANY NAME (text) - Primary identifier
CAGE CODE (text) - SAM.gov unique ID
NAICS CODES (multi-select) - Primary capabilities
CAPABILITIES (multi-select) - IT Support, Software Dev, Cybersecurity, PM, etc.
BUSINESS TYPE (single select) - Small Business, 8(a), HUBZone, WOSB, VOSB, SDVOSB, Large
SAM.GOV STATUS (single select) - Active, Expired, Not Registered
CERTIFICATIONS (multi-select) - ISO 9001, CMMI, Security Clearance, etc.
PRIMARY CONTACT (text)
EMAIL (email)
PHONE (phone)
WEBSITE (url)
ADDRESS (text)
CITY (text)
STATE (single select) - All 50 states + DC
ZIP CODE (text)
EMPLOYEE COUNT (number)
ANNUAL REVENUE (currency)
SOCIOECONOMIC CERTS (multi-select) - 8(a), HUBZone, WOSB, VOSB, SDVOSB, etc.
PSC CODES (multi-select) - Product Service Codes they work in
PAST PERFORMANCE SUMMARY (long text)
KEY CONTRACTS (long text) - Notable government contracts
HOURLY RATES (long text) - By role: PM: $100/hr, Dev: $125/hr, etc.
AVAILABILITY (single select) - Available, Busy, Not Available
RELATIONSHIP STAGE (single select) - Prospect, Contacted, Teaming Partner, Active Sub, Past Sub
FIRST CONTACTED (date)
LAST CONTACTED (date)
TEAMING AGREEMENTS (attachment)
PAST PROJECTS TOGETHER (number)
PERFORMANCE RATING (rating 1-5)
COMPLIANCE RISK (single select) - Low, Medium, High
AI SCORE (number) - 0-100 qualification score
DISCOVERY METHOD (single select) - SAM.gov, LinkedIn, Referral, Industry Event, Manual Entry
DISCOVERY DATE (date)
DISCOVERED BY (single select) - NEXUS Auto-Mining, User Name
SOURCE NOTES (long text)
NOTES (long text)

**FPDS ENRICHMENT FIELDS (NEW):** ⭐
PAST CONTRACTS COUNT (number) - Total contracts won (last 3 years)
RECENT CONTRACTS (long text) - JSON of last 5 contracts with details
TOTAL CONTRACT VALUE (currency) - Sum of all FPDS awards
PRIMARY AGENCIES (multi-select) - VA, DOD, DHS, GSA, etc.
LAST CONTRACT DATE (date) - Most recent contract award
AVERAGE CONTRACT SIZE (currency) - Total value / count
CONTRACT TYPES (multi-select) - FFP, T&M, Cost-Plus, IDIQ

**USASPENDING ENRICHMENT FIELDS (NEW):** ⭐
AGENCY PREFERENCE (text) - "Works primarily with VA (78% of contracts)"
GEOGRAPHIC FOCUS (text) - "Strong in Mid-Atlantic region"
SMALL BUSINESS UTILIZATION (percentage) - % of work as prime vs sub

CREATED DATE (date) - Auto
LAST MODIFIED (date) - Auto
```

---

### **Table 2: `GPSS TEAMING ARRANGEMENTS`**

**Required Fields:**
```
ARRANGEMENT ID (autonumber)
OPPORTUNITY ID (linked to Opportunities table)
OPPORTUNITY NAME (lookup from Opportunities)
CONTRACT VALUE (currency)
PRIME CONTRACTOR (single select) - Us, Them
OUR COMPANY ROLE (single select) - Prime, Subcontractor, Joint Venture
SUBCONTRACTOR (linked to GPSS SUBCONTRACTORS)
SUB COMPANY NAME (lookup)
WORKSHARE PERCENTAGE (number) - What % they're doing
OUR PERCENTAGE (number) - What % we're doing
SUB VALUE (currency) - Their portion
OUR VALUE (currency) - Our portion
SET ASIDE TYPE (single select) - Small Business, 8(a), HUBZone, WOSB, VOSB, Full & Open
COMPLIANCE RULE (single select) - 50%, 15%, 25%, No Limit
COMPLIANT (checkbox) - Meets the rule?
COMPLIANCE CALCULATION (long text) - Show the math
TEAMING AGREEMENT STATUS (single select) - Draft, Signed, Active, Complete, Cancelled
TEAMING AGREEMENT (attachment)
DATE FORMED (date)
CONTRACT AWARD DATE (date)
CONTRACT COMPLETE DATE (date)
OUR ESTIMATED COST (currency)
SUB ESTIMATED COST (currency)
TOTAL ESTIMATED COST (currency)
ESTIMATED MARGIN (currency)
ESTIMATED MARGIN % (formula) - Calculated
ACTUAL COST (currency) - After completion
ACTUAL MARGIN (currency) - After completion
STATUS (single select) - Proposed, Negotiating, Agreed, Bidding, Won, Lost, Active, Complete
NOTES (long text)
CREATED DATE (date)
LAST MODIFIED (date)
```

---

## 🔧 BACKEND IMPLEMENTATION

### **New Class: `GPSSSubcontractorMiner`**

**Location:** `nexus_backend.py` (around line 4800, after `GPSSSupplierMiner`)

**Methods to Build:**

#### **1. `search_sam_gov(naics_code: str, state: str = None, certifications: list = None, max_results: int = 50)`**
```python
Purpose: Search SAM.gov Entity Management API for contractors
Inputs: 
  - naics_code: "541512" (Computer Systems Design)
  - state: "VA" (optional, limit to state)
  - certifications: ["8(a)", "SDVOSB"] (optional)
  - max_results: 50
Process:
  1. Build SAM.gov API query
  2. Filter by active registration, size, certifications
  3. Extract: company name, CAGE, NAICS, contact, certs
  4. Return: List of subcontractors
Output: [{"COMPANY NAME": "...", "CAGE CODE": "...", ...}]
```

#### **2. `enrich_with_fpds(subcontractors: List[Dict]) -> List[Dict]`** ⭐ NEW - PHASE 1
```python
Purpose: Enrich subcontractors with past performance data from FPDS
Inputs: List of subcontractors from SAM.gov
Process:
  1. For each subcontractor, query FPDS by CAGE code or company name
  2. Extract: Contract history (last 3 years)
    - Contract titles
    - Award amounts
    - Agencies (VA, DOD, etc.)
    - Contract dates
    - Total number of contracts
  3. Calculate:
    - Total contract value won
    - Average contract size
    - Primary agencies they work with
    - Most recent contract date
  4. Add to subcontractor record
Output: Enriched subcontractors with past performance data
API: https://api.fpds.gov/prod/api/v1/contracts
Query: ?awardee_duns=[DUNS]&award_date=[last_3_years]
```

#### **3. `enrich_with_usaspending(subcontractors: List[Dict]) -> List[Dict]`** ⭐ NEW - PHASE 1
```python
Purpose: Add agency spending patterns and preferences
Inputs: List of subcontractors
Process:
  1. Query USAspending.gov API by contractor DUNS
  2. Extract:
    - Top agencies by spending volume
    - Contract types (FFP, T&M, Cost-Plus)
    - Small business utilization
    - Geographic concentration
  3. Analyze patterns:
    - "Works primarily with VA (78% of contracts)"
    - "Specializes in T&M contracts"
    - "Strong in Mid-Atlantic region"
Output: Enriched with agency preference data
API: https://api.usaspending.gov/api/v2/search/spending_by_award/
```

#### **4. `search_by_capability(capability: str, max_results: int = 30)`**
```python
Purpose: Search for subs by human-readable capability
Inputs: 
  - capability: "cybersecurity" or "software development"
Process:
  1. Map capability to NAICS codes (using AI or lookup table)
  2. Call search_sam_gov() for each relevant NAICS
  3. Deduplicate results
  4. Return ranked list
Output: [{"COMPANY NAME": "...", "CAPABILITIES": ["Cybersecurity"], ...}]
```

#### **5. `search_existing(capability: str = None, naics: str = None, state: str = None, certification: str = None, availability: str = None)`**
```python
Purpose: Search existing Airtable GPSS SUBCONTRACTORS table
Inputs: Flexible filters
Process:
  1. Build Airtable formula filter
  2. Query GPSS SUBCONTRACTORS
  3. Return matches sorted by rating/score
Output: [{"COMPANY NAME": "...", "AI SCORE": 92, ...}]
```

#### **6. `_ai_qualify_subcontractor(sub: dict) -> int`** ⭐ UPDATED WITH FPDS DATA
```python
Purpose: AI scores subcontractor 0-100 using enriched data
Inputs: Subcontractor data (including FPDS + USAspending)
Prompt: "Score this subcontractor for government contracting:
  - Has valid CAGE code? (+10)
  - Active SAM.gov registration? (+10)
  - Has socioeconomic certifications? (+10)
  - Has contact info (email/phone)? (+10)
  - Has website? (+5)
  - **Won similar contracts (FPDS)? (+30)** ⭐ NEW
  - **Recent wins (last 12 months)? (+10)** ⭐ NEW
  - **Works with target agency? (+10)** ⭐ NEW
  - **Good contract size match? (+5)** ⭐ NEW
  
  Return just the number 0-100."
Output: 92 (much more accurate with past performance!)
```

#### **7. `mine_all_sources(capability: str, naics: str = None, state: str = None, certifications: list = None, auto_import_threshold: int = 80)`** ⭐ UPDATED
```python
Purpose: Master function - search everywhere, enrich, and auto-import
Process:
  1. Search existing database
  2. If insufficient results (< 10), search SAM.gov
  3. **Enrich with FPDS (past performance)** ⭐ NEW
  4. **Enrich with USAspending (agency patterns)** ⭐ NEW
  5. AI qualify all new subs (using enriched data)
  6. Auto-import if score >= threshold
  7. Return combined ranked list (sorted by AI score)
Output: {
  "existing": [...],
  "new_found": [...],
  "new_found_enriched": true,  ⭐ NEW
  "fpds_data_added": 15,  ⭐ NEW
  "auto_imported": [...],
  "review_queue": [...],
  "total": 45
}
```

#### **8. `find_subcontractors_for_rfp(rfp_data: dict, auto_mine: bool = True)`**
```python
Purpose: Match subcontractors to RFP requirements
Inputs: 
  rfp_data: {
    "title": "Cybersecurity Assessment",
    "requirements": "penetration testing, risk assessment",
    "naics": "541512",
    "value": 300000,
    "set_aside": "Small Business"
  }
Process:
  1. Extract capabilities from requirements (AI)
  2. Search existing subs by capability
  3. If auto_mine and insufficient, mine SAM.gov
  4. Rank by: score, availability, certs matching set-aside
  5. Return top matches
Output: [
  {
    "COMPANY NAME": "CyberShield Inc.",
    "AI SCORE": 92,
    "MATCH REASON": "Cybersecurity, Active SAM, SDVOSB",
    "ESTIMATED COST": 120000,
    "AVAILABILITY": "Available"
  },
  ...
]
```

#### **9. `calculate_compliance(contract_value: float, our_work: float, sub_work: float, set_aside: str)`**
```python
Purpose: Check if workshare meets FAR rules
Inputs:
  - contract_value: 500000
  - our_work: 280000
  - sub_work: 180000
  - set_aside: "Small Business"
Process:
  1. Determine rule: Small Business = 50%, 8(a) = 50%, etc.
  2. Calculate our %: our_work / (our_work + sub_work)
  3. Check: our % >= required %?
Output: {
  "compliant": True,
  "our_percentage": 60.9,
  "required_percentage": 50,
  "buffer": 10.9,
  "rule": "Small Business 50% Self-Performance",
  "recommendation": "✅ COMPLIANT with 10.9% buffer"
}
```

#### **10. `create_teaming_arrangement(opportunity_id: str, subcontractor: dict, our_work: float, sub_work: float)`**
```python
Purpose: Create teaming arrangement record in Airtable
Process:
  1. Get opportunity data
  2. Calculate workshare %
  3. Run compliance check
  4. Create record in GPSS Teaming Arrangements
  5. Update opportunity status
Output: {
  "arrangement_id": "rec123456",
  "compliant": True,
  "status": "Created"
}
```

---

## 🌐 API ENDPOINTS

### **Add to `api_server.py`:**

```python
# Subcontractor Mining Endpoints

@app.route('/gpss/subcontractors/search-sam-gov', methods=['POST'])
def mine_subcontractors_sam_gov():
    """Mine SAM.gov for subcontractors by NAICS/capability"""
    data = request.json
    naics = data.get('naics')
    capability = data.get('capability')
    state = data.get('state')
    certifications = data.get('certifications', [])
    max_results = data.get('max_results', 30)
    
    miner = nexus.gpss.subcontractor_miner
    
    if capability:
        results = miner.search_by_capability(capability, max_results)
    else:
        results = miner.search_sam_gov(naics, state, certifications, max_results)
    
    return jsonify({
        "success": True,
        "source": "sam.gov",
        "capability": capability,
        "naics": naics,
        "subcontractors_found": len(results),
        "subcontractors": results
    })

@app.route('/gpss/subcontractors/mine-all', methods=['POST'])
def mine_subcontractors_all():
    """Mine all sources for subcontractors"""
    data = request.json
    capability = data.get('capability')
    naics = data.get('naics')
    state = data.get('state')
    certifications = data.get('certifications')
    auto_import_threshold = data.get('auto_import_threshold', 80)
    
    miner = nexus.gpss.subcontractor_miner
    results = miner.mine_all_sources(
        capability=capability,
        naics=naics,
        state=state,
        certifications=certifications,
        auto_import_threshold=auto_import_threshold
    )
    
    return jsonify({
        "success": True,
        "results": results
    })

@app.route('/gpss/subcontractors/find-for-rfp', methods=['POST'])
def find_subcontractors_for_rfp():
    """Find matching subcontractors for an RFP"""
    data = request.json
    rfp_data = {
        "title": data.get('title'),
        "requirements": data.get('requirements'),
        "naics": data.get('naics'),
        "value": data.get('value'),
        "set_aside": data.get('set_aside')
    }
    auto_mine = data.get('auto_mine', True)
    
    miner = nexus.gpss.subcontractor_miner
    matches = miner.find_subcontractors_for_rfp(rfp_data, auto_mine)
    
    return jsonify({
        "success": True,
        "rfp_title": rfp_data['title'],
        "matches_found": len(matches),
        "matches": matches
    })

@app.route('/gpss/teaming/calculate-compliance', methods=['POST'])
def calculate_teaming_compliance():
    """Calculate if workshare meets FAR rules"""
    data = request.json
    result = nexus.gpss.subcontractor_miner.calculate_compliance(
        contract_value=data.get('contract_value'),
        our_work=data.get('our_work'),
        sub_work=data.get('sub_work'),
        set_aside=data.get('set_aside')
    )
    return jsonify(result)

@app.route('/gpss/teaming/create', methods=['POST'])
def create_teaming_arrangement():
    """Create a teaming arrangement"""
    data = request.json
    result = nexus.gpss.subcontractor_miner.create_teaming_arrangement(
        opportunity_id=data.get('opportunity_id'),
        subcontractor=data.get('subcontractor'),
        our_work=data.get('our_work'),
        sub_work=data.get('sub_work')
    )
    return jsonify(result)

@app.route('/gpss/subcontractors/search', methods=['POST'])
def search_subcontractors():
    """Search existing subcontractors in database"""
    data = request.json
    miner = nexus.gpss.subcontractor_miner
    results = miner.search_existing(
        capability=data.get('capability'),
        naics=data.get('naics'),
        state=data.get('state'),
        certification=data.get('certification'),
        availability=data.get('availability')
    )
    return jsonify({
        "success": True,
        "subcontractors_found": len(results),
        "subcontractors": results
    })
```

---

## 🎨 FRONTEND IMPLEMENTATION

### **New Component: `SubcontractorsTab.tsx`**

**Location:** `/nexus-frontend/src/components/SubcontractorsTab.tsx`

**Features:**
```typescript
1. Subcontractor List View
   - Table showing all subs with key info
   - Columns: Name, Capabilities, Certs, Rating, Status
   - Sort by: Score, Rating, Recent

2. Search & Filter
   - Search by: Capability, NAICS, State
   - Filter by: Certification type, Availability, Business type
   - Button: "Find New Subcontractors"

3. Mining Interface
   - Form: "What capability do you need?"
   - Options: NAICS code, State preference, Certifications
   - Button: "Search SAM.gov"
   - Results: Shows new subs with AI scores
   - Action: "Import" or "Skip"

4. Compliance Calculator (popup/modal)
   - Input: Contract value, Your work $, Sub work $, Set-aside type
   - Output: "✅ COMPLIANT - 62% self-performance (need 50%)"
   - Visual: Progress bar showing compliance

5. Teaming Builder
   - Select opportunity from dropdown
   - Select subcontractor
   - Enter: Our work value, Their work value
   - Auto-calculate: Compliance, margins
   - Button: "Create Teaming Arrangement"
   - Output: Saved to Airtable

6. Subcontractor Profile View
   - Full details: Contact, certs, past performance
   - Past teaming history
   - Performance ratings
   - Notes section
   - Actions: "Contact", "Create Teaming", "Rate"
```

---

### **Integration into `GPSSSystem.tsx`**

**Add tab:**
```typescript
{ id: 'subcontractors', label: '🤝 Subcontractors' }
```

**Add render:**
```typescript
{activeTab === 'subcontractors' && (
  <SubcontractorsTab />
)}
```

---

## 🔑 SAM.GOV API DETAILS

### **Endpoint:**
```
GET https://api.sam.gov/entity-information/v3/entities
```

### **Query Parameters:**
```
api_key: YOUR_SAM_GOV_API_KEY (you already have this!)
samRegistered: Yes
registrationStatus: Active
primaryNaics: 541512
businessTypeDesc: 8(a) (optional)
stateOrProvinceCode: VA (optional)
```

### **Response Extract:**
```json
{
  "entityData": [
    {
      "entityRegistration": {
        "legalBusinessName": "CyberShield Inc.",
        "cageCode": "1A2B3",
        "samRegistered": "Yes"
      },
      "coreData": {
        "mailingAddress": {...},
        "physicalAddress": {...},
        "congressionalDistrict": "VA-10"
      },
      "assertionsData": {
        "naicsCodes": [...],
        "businessTypeList": ["8(a)", "SDVOSB"]
      },
      "repsAndCertsData": {
        "certifications": [...]
      }
    }
  ]
}
```

**Key:** You already have `SAM_GOV_API_KEY` in your .env - we'll reuse it!

---

## 📊 NAICS TO CAPABILITY MAPPING

**Common mappings for quick search:**

```python
CAPABILITY_TO_NAICS = {
    "software development": ["541511", "541512"],
    "cybersecurity": ["541512", "541519"],
    "it support": ["541512", "541519"],
    "project management": ["541618"],
    "consulting": ["541611", "541618"],
    "data analytics": ["541512", "541720"],
    "cloud services": ["518210", "541512"],
    "network engineering": ["541512", "541513"],
    "systems integration": ["541512"],
    "training": ["611420", "611430"]
}

PSC_TO_CAPABILITY = {
    "D302": "IT and Telecom - Systems Development",
    "D307": "IT and Telecom - IT Strategy and Architecture",
    "D310": "IT and Telecom - Cybersecurity",
    "R408": "Support - Program Management",
    # Add more as needed
}
```

---

## 🧪 TESTING PLAN

### **Test 1: Find Subcontractors by Capability**
```bash
curl -X POST http://localhost:5001/gpss/subcontractors/search-sam-gov \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "cybersecurity",
    "state": "VA",
    "max_results": 10
  }'
```

**Expected:** 10 Virginia-based cybersecurity firms from SAM.gov

---

### **Test 2: Compliance Calculator**
```bash
curl -X POST http://localhost:5001/gpss/teaming/calculate-compliance \
  -H "Content-Type: application/json" \
  -d '{
    "contract_value": 500000,
    "our_work": 280000,
    "sub_work": 180000,
    "set_aside": "Small Business"
  }'
```

**Expected:** 
```json
{
  "compliant": true,
  "our_percentage": 60.9,
  "required_percentage": 50,
  "buffer": 10.9,
  "recommendation": "✅ COMPLIANT"
}
```

---

### **Test 3: Find Subs for RFP**
```bash
curl -X POST http://localhost:5001/gpss/subcontractors/find-for-rfp \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Network Security Assessment",
    "requirements": "penetration testing, vulnerability scanning, risk assessment",
    "naics": "541512",
    "value": 300000,
    "set_aside": "SDVOSB"
  }'
```

**Expected:** Ranked list of matching SDVOSB cybersecurity firms

---

## ⏱️ BUILD TIMELINE

### **Phase 1: Backend Core with FPDS/USAspending (3-4 hours)** ⭐ UPDATED
- [ ] Create `GPSSSubcontractorMiner` class
- [ ] Implement `search_sam_gov()`
- [ ] **Implement `enrich_with_fpds()` - Past performance data** ⭐ NEW
- [ ] **Implement `enrich_with_usaspending()` - Agency patterns** ⭐ NEW
- [ ] Implement `search_by_capability()`
- [ ] Implement `_ai_qualify_subcontractor()` (updated with FPDS scoring)
- [ ] Test SAM.gov + FPDS + USAspending integration

### **Phase 2: Advanced Features (2 hours)**
- [ ] Implement `mine_all_sources()`
- [ ] Implement `find_subcontractors_for_rfp()`
- [ ] Implement `calculate_compliance()`
- [ ] Implement `create_teaming_arrangement()`

### **Phase 3: API Endpoints (1 hour)**
- [ ] Add all 6 API endpoints
- [ ] Test each endpoint
- [ ] Deploy to PythonAnywhere

### **Phase 4: Frontend (3-4 hours)**
- [ ] Create `SubcontractorsTab.tsx`
- [ ] Build search/filter UI
- [ ] Build mining interface
- [ ] Build compliance calculator UI
- [ ] Build teaming builder
- [ ] Integrate into `GPSSSystem.tsx`

### **Phase 5: Testing & Polish (1 hour)**
- [ ] End-to-end test: Find RFP → Find sub → Check compliance → Create teaming
- [ ] Create Airtable setup guide
- [ ] Documentation

**TOTAL: 9-11 hours of build time**

---

## 🎯 MVP vs FULL BUILD

### **MVP (Can build in 5-6 hours):** ⭐ UPDATED
✅ SAM.gov search by NAICS  
✅ **FPDS enrichment (past performance)** ⭐ CORE FEATURE NOW
✅ **USAspending enrichment (agency patterns)** ⭐ CORE FEATURE NOW
✅ Enhanced AI qualification (with past performance scoring)  
✅ Compliance calculator  
✅ Simple subcontractor list UI  
✅ Manual teaming creation  

### **Full Build (11-13 hours):**
✅ Everything in MVP, plus:  
✅ Smart capability-to-NAICS mapping  
✅ Auto-mining when finding subs for RFP  
✅ Full teaming workflow  
✅ Performance tracking  
✅ Advanced filtering  
✅ Bill.com payment integration  

---

## 💡 ROI CALCULATION

**Manual Process:**
- Finding 10 qualified subs: 4-6 hours of research
- Checking compliance: 30 min per arrangement
- Tracking relationships: 1 hour per project

**With NEXUS:**
- Finding 30 qualified subs: 60 seconds
- Checking compliance: 5 seconds (instant calculator)
- Tracking relationships: Automatic

**Time Saved Per Contract:** ~5-7 hours  
**Contracts Per Year:** 20  
**Hours Saved:** 100-140 hours/year  
**At $150/hr:** $15,000-$21,000 value  

**Plus:** Access to 10X more opportunities (service contracts you couldn't bid before)

---

## 📋 NEXT STEPS

### **Decision Time:**

**Option 1: Build it NOW**
- I'll implement the full system
- Backend + API + Frontend
- Test on PythonAnywhere
- Ready to use tomorrow

**Option 2: Build MVP First**
- Core features only (4-5 hours)
- Test with real RFPs
- Expand based on what you actually need

**Option 3: Save for Later**
- I'll create the detailed guide
- You review and decide timing
- Build when you're ready to pursue service contracts

**What do you want to do?** 🤔
