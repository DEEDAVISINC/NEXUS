# 🔍 NEXUS OPPORTUNITY FILTERS - CONFIGURATION

**Date:** February 5, 2026  
**Status:** FILTERS ACTIVATED  
**Goal:** Only show relevant opportunities  

---

## 🎯 ACTIVE FILTERS:

### **1. Geographic Filter**
**HOME STATE:** Michigan (MI)

**Why:**
- ✅ Lower shipping costs
- ✅ Local relationships
- ✅ Easier site visits
- ✅ Faster delivery
- ✅ Michigan-based certifications

**Applied To:**
- SAM.gov searches (`state=MI`)
- Federal forecast mining
- Local opportunity mining

---

### **2. Set-Aside Filter**
**CERTIFICATION:** EDWOSB ONLY

**Why:**
- ✅ LEAST competition (most restrictive)
- ✅ You qualify (economically disadvantaged)
- ✅ Higher win rate
- ✅ Often sole-source or limited competition

**NOT Searching:**
- ❌ WOSB (more competition)
- ❌ 8(a) (you don't qualify)
- ❌ HUBZone (you don't qualify)
- ❌ SDVOSB (you don't qualify)
- ❌ Unrestricted (too much competition)

**Applied To:**
- SAM.gov searches (`typeOfSetAside=EDWOSB`)
- Federal forecast mining
- Opportunity qualification

---

## 📊 EXCEPTIONS (STILL INCLUDE):

### **Local Government Bids (Always Include)**
Even if not EDWOSB set-aside:
- ✅ RCOC (Road Commission for Oakland County)
- ✅ Wayne County
- ✅ City of Detroit
- ✅ Canton Township
- ✅ Other Michigan municipalities

**Why:** Local relationships, good margins, familiar buyers

### **High-Value Opportunities (Manual Review)**
If opportunity is:
- $500K+ contract value
- Michigan-based
- Perfect product fit

**Action:** Flag for manual review even if not EDWOSB

---

## 🔧 WHERE FILTERS ARE APPLIED:

### **1. SAM.gov API Searches**
**File:** `mine_real_federal_forecasts.py`

**Filter Parameters:**
```python
url = f"{sam_url}?api_key={key}&state=MI&typeOfSetAside=EDWOSB"
```

### **2. Airtable Opportunity Display**
**File:** `nexus_backend.py` → `get_opportunities()`

**Filter Logic:**
```python
# Show only:
if opportunity['state'] == 'MI' and opportunity['set_aside'] == 'EDWOSB':
    display_opportunities.append(opportunity)
```

### **3. Email Automation**
**File:** `nexus_email_automation.py`

**Filter Logic:**
```python
# Auto-send diversity inquiry only if:
if 'EDWOSB' in set_aside and state == 'MI':
    send_inquiry()
```

---

## 📋 SEARCH KEYWORDS (EDWOSB + MICHIGAN):

**Product Categories to Search:**
- Office supplies
- Industrial supplies
- Janitorial/cleaning supplies
- Medical supplies
- Laboratory equipment
- Safety equipment
- Tools and hardware
- Paper products
- Landscaping materials
- Construction materials

**Service Categories to Search:**
- Janitorial services
- Landscaping services
- Cleaning services
- Transportation/logistics
- Warehousing

**Geographic Terms:**
- Michigan
- Detroit
- Grand Rapids
- Lansing
- Ann Arbor
- Metro Detroit
- Southeast Michigan
- Great Lakes region

---

## ⚠️ WHAT TO EXCLUDE:

### **States to SKIP:**
- All states except Michigan (MI)
- Exception: If contract > $500K and perfect fit

### **Set-Asides to SKIP:**
- WOSB (unless Michigan local government)
- 8(a)
- HUBZone
- SDVOSB
- SBA
- Unrestricted

### **Opportunity Types to SKIP:**
- "Sources Sought" (too early)
- "Notice of Intent" (too early)
- "Pre-Solicitation" > 90 days out
- Renewals/modifications (existing contracts)
- "Potential Renewal" (not guaranteed)

---

## 🎯 IDEAL OPPORTUNITY PROFILE:

**Perfect Match:**
- ✅ Michigan-based (MI)
- ✅ EDWOSB set-aside
- ✅ Product resale (not service)
- ✅ $20K-$500K contract value
- ✅ 5-30 days until deadline
- ✅ Familiar product category

**Good Match:**
- ✅ Michigan-based
- ✅ EDWOSB set-aside
- ✅ Service contract (if you have subcontractor)
- ✅ Any contract value
- ✅ 3-60 days until deadline

---

## 📊 EXPECTED RESULTS:

### **Before Filters:**
- 1,291+ opportunities displayed
- All states, all set-asides
- Information overload

### **After Filters:**
- 5-20 opportunities displayed
- Michigan + EDWOSB only
- Focused and actionable

---

## 🔧 HOW TO UPDATE FILTERS:

### **Add Another State:**
Edit `mine_real_federal_forecasts.py`:
```python
# Change from:
state=MI

# To:
state=MI,OH,IN  # Michigan, Ohio, Indiana
```

### **Add WOSB Set-Asides:**
Edit filter:
```python
# Change from:
typeOfSetAside=EDWOSB

# To:
typeOfSetAside=EDWOSB,WOSB  # Include both
```

### **Expand Search Radius:**
Add neighboring states where you have contacts/relationships

---

## ✅ WHAT THIS FIXES:

**BEFORE:**
- ❌ 1,291 opportunities (overwhelming)
- ❌ Alaska, Wyoming, Alabama contracts (irrelevant)
- ❌ Unrestricted bids (too competitive)
- ❌ Can't find the good opportunities

**AFTER:**
- ✅ 5-20 focused opportunities
- ✅ Michigan only (home state)
- ✅ EDWOSB only (least competition)
- ✅ Easy to review and pursue

---

## 🚀 TO ACTIVATE FILTERS:

### **1. Update Mining Script:**
```bash
# Already updated:
mine_real_federal_forecasts.py
```

### **2. Run Filtered Search:**
```bash
python3 mine_real_federal_forecasts.py
```

### **3. Verify Results:**
Check Airtable - should see far fewer opportunities, all Michigan + EDWOSB

---

## 📧 AUTO-INQUIRY RULES:

**Send diversity inquiry if:**
- ✅ Michigan-based
- ✅ EDWOSB set-aside
- ✅ Contract value ≥ $20K
- ✅ Buyer email available
- ✅ Fit score ≥ 70

**Do NOT send inquiry if:**
- ❌ Outside Michigan (unless >$500K)
- ❌ Not EDWOSB set-aside
- ❌ Too small (<$20K)
- ❌ Wrong product category

---

## 💡 NEXT ENHANCEMENTS:

### **Priority 1: Adjacent States**
Add Ohio, Indiana if opportunity is:
- Large ($200K+)
- Perfect product fit
- Border region (Detroit area → Toledo, South Bend)

### **Priority 2: WOSB Backup**
If no EDWOSB opportunities in Michigan:
- Expand to WOSB set-asides
- Still Michigan only

### **Priority 3: Local Government**
Better mining of:
- MiDeal (Michigan state procurement)
- BidNet Michigan opportunities
- Michigan municipal portals

---

## ✅ RESULT:

**You will now see:**
- ONLY Michigan opportunities
- ONLY EDWOSB set-asides
- Far fewer, far more relevant

**No more:**
- ❌ Alaska contracts
- ❌ Wyoming opportunities
- ❌ Unrestricted bids
- ❌ Information overload

---

*Focused. Relevant. Actionable.*
