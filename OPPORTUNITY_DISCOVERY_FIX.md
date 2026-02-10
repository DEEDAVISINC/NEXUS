# 🔧 OPPORTUNITY DISCOVERY FIX - ACTION PLAN

**Date:** February 5, 2026  
**Problem:** 2,867 opportunities, ALL showing state = "UNKNOWN"  
**Root Cause:** Mining scripts not extracting/storing state data  

---

## 🚨 THE PROBLEM:

### **Current State:**
- ✅ Mining pulls opportunities from SAM.gov
- ❌ State field not being extracted from API response
- ❌ All 2,867 opportunities show "Place of Performance State" = UNKNOWN
- ❌ Can't filter by Michigan because no state data
- ❌ You see Alaska, Wyoming, Alabama opportunities (irrelevant!)

### **What You See:**
```
GPSS OPPORTUNITIES Table:
- 2,867 total opportunities
- 0 with state = "MI"
- 2,867 with state = "UNKNOWN"
- Result: CAN'T FILTER BY STATE!
```

---

## ✅ THE SOLUTION:

### **Step 1: Fix Mining Script (DONE)**
Updated `mine_real_federal_forecasts.py`:
- ✅ Added `&state=MI` filter to SAM.gov API calls
- ✅ Added `&typeOfSetAside=EDWOSB` filter
- ✅ Future mining will ONLY pull Michigan + EDWOSB

### **Step 2: Extract State from Existing Opportunities**
Need to:
1. Loop through all 2,867 existing opportunities
2. Re-fetch SAM.gov data for each
3. Extract Place of Performance State
4. Update Airtable record with state

### **Step 3: Add Frontend Filters**
Need to:
1. Add "State" filter dropdown (default: Michigan)
2. Add "Set-Aside" filter dropdown (default: EDWOSB)
3. Add "Hide Irrelevant" toggle (hides non-Michigan, non-EDWOSB)

---

## 🎯 IMMEDIATE WORKAROUND:

Since state data is missing, use **keyword filtering**:

### **Michigan Keywords:**
```python
michigan_keywords = [
    'rcoc',
    'wayne county',
    'oakland county',
    'macomb county',
    'detroit',
    'canton township',
    'warren',
    'sterling heights',
    'troy',
    'dearborn',
    'livonia',
    'westland',
    'farmington hills',
    'bloomfield',
    'auburn hills'
]
```

### **Current Michigan Opportunities:**
- 19 identified by keyword matching
- RCOC bids (Road Commission Oakland County)
- Detroit city bids
- Canton Township bids

---

## 🔧 WHAT TO DO NOW:

### **Option 1: Clean Slate (RECOMMENDED)**
```bash
# Delete all non-Michigan opportunities
# Keep only 19 Michigan local government bids
# Start fresh with Michigan + EDWOSB mining only

python3 clean_airtable_michigan_only.py
```

**Result:**
- 19 Michigan opportunities
- All future mining = Michigan + EDWOSB only
- Clean, focused system

---

### **Option 2: Backfill State Data**
```bash
# Re-fetch state data for all 2,867 opportunities
# WARNING: Will take 2-3 hours (API rate limits)

python3 backfill_opportunity_states.py
```

**Result:**
- All opportunities have state data
- Can filter by Michigan
- Still need to manually filter 2,867 → 19

---

### **Option 3: Frontend-Only Filter**
```bash
# Add Michigan keyword filter to frontend
# Hides non-Michigan opportunities
# Doesn't delete data, just hides it

# Update nexus-frontend/src/components/systems/OpportunitySystem.tsx
```

**Result:**
- Quick fix (10 minutes)
- No data cleanup required
- Can toggle "Show All" vs "Michigan Only"

---

## 💡 RECOMMENDATION:

**DO ALL THREE:**

### **Phase 1: NOW (Frontend Filter)**
Add frontend filter using Michigan keywords:
- Quick (10 minutes)
- Immediate relief
- User can toggle Michigan vs All

### **Phase 2: TONIGHT (Clean Slate)**
Delete non-Michigan opportunities:
- Clean system
- Fast performance
- Focused on relevant bids

### **Phase 3: ONGOING (Filtered Mining)**
Use updated mining script:
- Michigan + EDWOSB only
- No more irrelevant opportunities
- System stays clean

---

## 📋 STEP-BY-STEP IMPLEMENTATION:

### **NOW: Add Frontend Filter**

1. Open `nexus-frontend/src/components/systems/OpportunitySystem.tsx`

2. Add filter toggle:
```typescript
const [showMichiganOnly, setShowMichiganOnly] = useState(true);

const michiganKeywords = [
  'rcoc', 'wayne county', 'oakland county', 'detroit', 'canton'
];

const filteredOpportunities = opportunities.filter(opp => {
  if (!showMichiganOnly) return true; // Show all
  
  const name = opp.Name?.toLowerCase() || '';
  const agency = opp['Agency Name']?.toLowerCase() || '';
  
  return michiganKeywords.some(keyword => 
    name.includes(keyword) || agency.includes(keyword)
  );
});
```

3. Add toggle button:
```typescript
<button onClick={() => setShowMichiganOnly(!showMichiganOnly)}>
  {showMichiganOnly ? '🎯 Michigan Only' : '🌎 Show All'}
</button>
```

**Result:** User sees 19 Michigan opportunities instead of 2,867!

---

### **TONIGHT: Clean Airtable**

1. Create cleanup script:
```bash
python3 clean_airtable_michigan_only.py
```

2. Script logic:
- Keep Michigan local government (19 records)
- Keep EDWOSB set-asides (2 records)
- Delete everything else (2,846 records)

3. Backup before deleting:
```bash
python3 backup_opportunities.py
```

**Result:** Clean Airtable with only relevant opportunities!

---

### **ONGOING: Filtered Mining**

Already done! ✅

`mine_real_federal_forecasts.py` now searches:
- Michigan only (`state=MI`)
- EDWOSB only (`typeOfSetAside=EDWOSB`)

Next time mining runs:
- Only Michigan + EDWOSB opportunities added
- System stays clean
- No manual cleanup needed

---

## ✅ EXPECTED RESULTS:

### **BEFORE:**
```
GPSS OPPORTUNITIES:
- 2,867 total opportunities
- Alaska, Wyoming, Alabama, etc.
- Impossible to find Michigan bids
- Information overload
```

### **AFTER:**
```
GPSS OPPORTUNITIES:
- 19-25 Michigan opportunities
- All EDWOSB or local government
- Easy to review
- Actionable and relevant
```

---

## 🚀 NEXT ACTIONS:

**RIGHT NOW:**
1. ✅ Updated mining script (DONE)
2. ⏳ Add frontend filter (10 minutes)
3. ⏳ Test filter (5 minutes)

**TONIGHT:**
4. ⏳ Backup Airtable
5. ⏳ Clean out non-Michigan opportunities
6. ⏳ Verify system shows only Michigan

**ONGOING:**
7. ⏳ Run filtered mining daily
8. ⏳ Review new Michigan + EDWOSB opportunities
9. ⏳ Maintain clean, focused system

---

## 📊 SUCCESS METRICS:

**Week 1:**
- Reduce opportunities from 2,867 → ~25
- All opportunities Michigan-based
- 90% EDWOSB or local government

**Month 1:**
- Find 2-3 EDWOSB opportunities per week
- Pursue 1-2 Michigan local government bids per week
- Win rate: 20-30% (realistic for focused bidding)

**Month 3:**
- Consistent Michigan + EDWOSB pipeline
- 5-10 active bids at any time
- $50K monthly profit target achievable

---

*Focus on Michigan. Focus on EDWOSB. Ignore the rest.*
