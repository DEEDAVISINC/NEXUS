# ✅ CORRECT OPPORTUNITY FILTERS - EDWOSB NATIONWIDE

**Date:** February 5, 2026  
**Correction:** Location doesn't matter - SET-ASIDE TYPE matters!  

---

## 🎯 THE REAL STRATEGY:

**"As long as there's diversity inclusion, we need to be working with buyers that have NO CHOICE but to do business with companies like ours."**

### **Translation:**
- ✅ **EDWOSB set-aside** (ANY STATE) - Buyer MUST use EDWOSB company
- ✅ **WOSB set-aside** (ANY STATE) - Buyer MUST use WOSB company
- ✅ **Michigan local government** (ANY SET-ASIDE) - Geographic advantage
- ❌ **Unrestricted bids** - Too much competition
- ❌ **Other set-asides** (8(a), HUBZone, SDVOSB) - You don't qualify

---

## 🔍 CORRECT FILTERS:

### **Priority 1: EDWOSB (NATIONWIDE)**
```
Set-Aside Type: EDWOSB
State: ANY
Contract Value: $20K+
```

**Why:**
- Buyer HAS NO CHOICE - must award to EDWOSB
- Least competition (most restrictive set-aside)
- You qualify!
- Alabama, Wyoming, California - DOESN'T MATTER

**Current Count:** 2 opportunities (NEED MORE!)

---

### **Priority 2: WOSB (NATIONWIDE)**
```
Set-Aside Type: WOSB
State: ANY
Contract Value: $20K+
```

**Why:**
- Buyer must award to woman-owned business
- More competition than EDWOSB (but still restricted)
- You qualify!
- Geographic location irrelevant

**Current Count:** 10 opportunities

---

### **Priority 3: Michigan Local Government**
```
State: Michigan
Agency: RCOC, Wayne County, Detroit, Canton, etc.
Set-Aside: ANY
```

**Why:**
- Geographic advantage (local delivery, relationships)
- Lower shipping costs
- Existing relationships
- Even without set-aside, still good

**Current Count:** 19 opportunities

---

## 📊 EXPECTED OPPORTUNITY COUNT:

**WITH CORRECT FILTERS:**
- EDWOSB (nationwide): 2-10 opportunities
- WOSB (nationwide): 10-30 opportunities
- Michigan local: 19 opportunities
- **TOTAL: 31-59 focused opportunities**

**HIDE:**
- Unrestricted bids (2,800+ opportunities)
- 8(a) set-asides (you don't qualify)
- HUBZone set-asides (you don't qualify)
- SDVOSB set-asides (you don't qualify)

---

## 🔧 WHAT TO UPDATE:

### **1. Mining Script Filters:**

**OLD (WRONG):**
```python
# Only Michigan + EDWOSB
state=MI&typeOfSetAside=EDWOSB
```

**NEW (CORRECT):**
```python
# EDWOSB + WOSB nationwide
typeOfSetAside=EDWOSB,WOSB
# NO STATE FILTER - search all states!
```

---

### **2. Frontend Display Filters:**

**Show by default:**
- ✅ EDWOSB (any state)
- ✅ WOSB (any state)
- ✅ Michigan local government (any set-aside)

**Hide by default:**
- ❌ Unrestricted bids
- ❌ 8(a), HUBZone, SDVOSB
- ❌ "Sources Sought" (too early)
- ❌ Expired opportunities

**Add toggle:**
- "Show All" vs "EDWOSB/WOSB Only"

---

## 💡 KEY INSIGHT:

**SHIPPING DOESN'T MATTER FOR PRODUCTS!**

### **Example: Alabama Contract**
- ✅ EDWOSB set-aside
- ✅ Product resale (office supplies)
- ✅ Can ship from supplier directly to Alabama
- ✅ Your supplier (Grainger, Zoro) handles logistics
- ✅ **YOU ADD VALUE THROUGH EDWOSB CERTIFICATION, NOT GEOGRAPHY**

### **Your Role:**
1. Find EDWOSB opportunities
2. Source products from suppliers (Grainger, Zoro, etc.)
3. Submit bid with your EDWOSB pricing
4. Supplier ships directly to buyer
5. You earn margin + EDWOSB advantage

**Location = IRRELEVANT for product resale!**

---

## 🚀 UPDATED MINING STRATEGY:

### **SAM.gov Search Parameters:**
```
typeOfSetAside=EDWOSB,WOSB
ptype=o,k,p  (Solicitations, Combined Synopsis, Pre-solicitations)
postedFrom=last 30 days
postedTo=today
limit=1000
```

**NO STATE FILTER!** Search nationwide for EDWOSB/WOSB.

---

### **Local Search (Separate):**
```
Michigan municipal portals:
- BidNet Direct (RCOC, etc.)
- MiDeal (Michigan state procurement)
- Detroit procurement portal
- Wayne County portal
- MITN (Michigan Intergovernmental Trade Network)
```

---

## 📋 IDEAL OPPORTUNITY PROFILE:

### **Perfect Match:**
- ✅ EDWOSB set-aside
- ✅ Product resale (supplies, equipment, materials)
- ✅ $20K-$500K contract value
- ✅ 5-30 days until deadline
- ✅ Familiar product category
- ⚪ **State doesn't matter!**

### **Good Match:**
- ✅ WOSB set-aside
- ✅ Product resale or service (with subcontractor)
- ✅ Any contract value over $10K
- ✅ 3-60 days until deadline
- ⚪ **State doesn't matter!**

---

## ✅ WHAT TO DO NOW:

### **1. Update Mining Script:**
Remove Michigan-only filter, add WOSB to search:

```python
# File: mine_real_federal_forecasts.py
# OLD:
full_url = f"{url}?api_key={key}&state=MI&typeOfSetAside=EDWOSB"

# NEW:
full_url = f"{url}?api_key={key}&typeOfSetAside=EDWOSB,WOSB"
```

---

### **2. Update Frontend Display:**
Show EDWOSB + WOSB opportunities by default:

```typescript
// Default filter
const defaultFilters = {
  setAside: ['EDWOSB', 'WOSB', 'LOCAL_MICHIGAN'],
  hideUnrestricted: true
};
```

---

### **3. Run New Search:**
```bash
python3 mine_real_federal_forecasts.py
```

Expected results:
- Find 20-50 EDWOSB/WOSB opportunities nationwide
- Keep 19 Michigan local government bids
- Total: 39-69 focused opportunities

---

## 📊 PRIORITY RANKING:

**Tier 1: MUST PURSUE** (100 points)
- EDWOSB set-aside
- Product resale
- $50K+ contract value
- 7-30 days until deadline

**Tier 2: STRONG OPPORTUNITY** (80 points)
- WOSB set-aside
- Product resale
- $20K+ contract value
- 5-30 days until deadline

**Tier 3: GOOD OPPORTUNITY** (60 points)
- Michigan local government (any set-aside)
- Product resale or service
- $10K+ contract value

**Tier 4: CONSIDER** (40 points)
- WOSB set-aside
- Service contract (need subcontractor)
- Any value

---

## 🎯 GOAL:

**Show 30-60 opportunities total:**
- 5-15 EDWOSB (nationwide)
- 10-30 WOSB (nationwide)
- 15-25 Michigan local government

**Hide 2,800+ opportunities:**
- Unrestricted bids
- Other set-asides you don't qualify for
- Expired opportunities

---

## 💼 YOUR COMPETITIVE ADVANTAGE:

**EDWOSB Certification = Buyers MUST use you!**

**Example conversations:**
- "We have an EDWOSB set-aside - can you bid?"
- "We need at least 3 EDWOSB quotes - are you certified?"
- "This contract requires EDWOSB - you qualify!"

**YOU:** "Yes! Dee Davis Inc. is EDWOSB certified. We specialize in [product category]. Here's our capability statement..."

**Location doesn't matter - certification does!**

---

*Focus on EDWOSB/WOSB set-asides. Location is irrelevant. Buyers have no choice but to use certified companies like yours!*
