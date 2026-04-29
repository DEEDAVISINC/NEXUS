# HOW TO USE NEXUS_LEARNING INTELLIGENCE IN MINING SCRIPTS

**For AI/NEXUS sessions working on opportunity mining, SAM.gov searches, or bid prioritization.**

---

## QUICK START: Load Priority Targets

```python
import json

# Load priority NAICS and keywords
with open('/Users/deedavis/NEXUS BACKEND/NEXUS_LEARNING/PRIORITY_TARGETS_INDEX.json', 'r') as f:
    targets = json.load(f)

# Get Tier 1 NAICS codes (DDI ready now)
tier1_naics = [lane['naics'] for lane in targets['priority_naics']['tier_1_ready_now']]
# Result: ['492110', '621511', '812990']

# Get all priority keywords
keywords = targets['priority_keywords_global']
# Result: ['EDWOSB', 'WOSB', 'specimen', 'courier', 'lab', 'drug testing', ...]

# Get buying agencies to monitor
agencies = targets['buying_agencies_priority']
# Result: ['State Public Health Laboratories', 'County Health Departments', ...]
```

---

## USE CASE 1: Prioritizing SAM.gov Search Results

**Problem:** SAM.gov returns 500 results. Which ones should DDI pursue first?

**Solution:**
1. Load `PRIORITY_TARGETS_INDEX.json`
2. For each SAM.gov result:
   - Check if NAICS matches Tier 1 → **HIGH PRIORITY**
   - Check if keywords match priority keywords → **FLAG FOR REVIEW**
   - Check if buying agency matches priority list → **STRONG FIT**
3. Rank results: Tier 1 NAICS + Priority Agency + EDWOSB set-aside = **IMMEDIATE PURSUIT**

**Example:**
```python
def score_opportunity(opp_naics, opp_keywords, opp_agency, is_edwosb):
    score = 0
    
    # Tier 1 NAICS = +10 points
    if opp_naics in tier1_naics:
        score += 10
    
    # Priority keywords = +2 per match
    for kw in opp_keywords:
        if kw.lower() in [k.lower() for k in keywords]:
            score += 2
    
    # Priority agency = +5 points
    if any(agency.lower() in opp_agency.lower() for agency in agencies):
        score += 5
    
    # EDWOSB set-aside = +15 points
    if is_edwosb:
        score += 15
    
    return score

# Opportunity 1: Lab courier for State Health Lab, NAICS 492110, EDWOSB
score1 = score_opportunity('492110', ['lab', 'specimen'], 'Michigan State Public Health Laboratory', True)
# Score: 10 (Tier 1) + 4 (keywords) + 5 (agency) + 15 (EDWOSB) = 34 → **TOP PRIORITY**

# Opportunity 2: IT services, NAICS 541519, Full & Open
score2 = score_opportunity('541519', ['software', 'cloud'], 'GSA', False)
# Score: 0 (not Tier 1) + 0 (no keyword match) + 0 (not priority agency) + 0 (not EDWOSB) = 0 → **LOW PRIORITY**
```

---

## USE CASE 2: Generating Capability Statement Content

**Problem:** Need to write a capability statement for a lab courier RFP.

**Solution:**
1. Open `MEDICAL_COURIER_CONTRACT_TARGETS.md`
2. Find the "Lab Courier Services" lane
3. Use documented entry points, DDI advantages, and buyer pain points

**Example:**
```python
# Read the medical courier intelligence
with open('/Users/deedavis/NEXUS BACKEND/NEXUS_LEARNING/MEDICAL_COURIER_CONTRACT_TARGETS.md', 'r') as f:
    intel = f.read()

# Extract key phrases for lab courier lane
if 'Lab Courier Services' in intel:
    # Intelligence says:
    # - Entry point: "HIPAA-compliant specimen transport + cold chain"
    # - DDI advantage: "Uber Health partnership + CHAMPS Medicaid provider"
    # - Buyer pain point: "Delayed specimen pickup = lab result delays"
    
    # Use this in capability statement:
    cap_statement_intro = """
    Dee Davis Inc. provides HIPAA-compliant specimen transport with documented 
    cold chain integrity, leveraging our Uber Health partnership and CHAMPS 
    Medicaid provider status. Our 24/7 dispatch capability eliminates specimen 
    pickup delays, ensuring lab results are never held up by courier gaps.
    """
```

---

## USE CASE 3: Identifying Subcontractor Needs

**Problem:** DDI wins a Tier 2 contract (Regulated Medical Waste Transport). Do we have the capability in-house?

**Solution:**
1. Check `PRIORITY_TARGETS_INDEX.json` → Tier 2 means "build capability"
2. Check `sub_requirement` field → "EPA/DOT hazmat certified carrier"
3. **Conclusion:** DDI needs a qualified sub for this lane

**Example:**
```python
# Check if a NAICS requires a sub
def needs_sub(naics_code):
    for tier in ['tier_2_build_capability', 'tier_3_specialized']:
        for lane in targets['priority_naics'][tier]:
            if lane['naics'] == naics_code:
                return lane.get('sub_requirement', None)
    return None

sub_needed = needs_sub('562112')  # Medical waste NAICS
# Returns: "EPA/DOT hazmat certified carrier"
# Action: Search for hazmat carrier subs in Michigan
```

---

## USE CASE 4: Updating Intelligence After a Win/Loss

**Problem:** DDI just won a lab courier contract with a 55% margin. Should we prioritize more lab courier bids?

**Solution:**
1. Open `MEDICAL_COURIER_CONTRACT_TARGETS.md`
2. Update the "Lab Courier Services" section with actual results
3. If win rate > 50%, confirm it as Tier 1 priority
4. Update `PRIORITY_TARGETS_INDEX.json` with refined margin expectations

**Example Update:**
```markdown
### Lab Courier Services — CONTRACT HISTORY UPDATE

| Date | Buyer | NAICS | DDI Margin | Outcome | Notes |
|------|-------|-------|------------|---------|-------|
| 2026-04-29 | Michigan State Public Health Lab | 492110 | 55% | WON | Uber Health + DePointe lab credibility sealed it |

**Win Rate:** 1 out of 1 (100%) — CONFIRM TIER 1 PRIORITY
**Actual Margin:** 55% (better than projected 40-50%)
**Key Success Factor:** DePointe DNA lab operations = credible medical courier
**Replicate For:** All state public health labs, county health departments
```

---

## USE CASE 5: Mining Script Integration

**For automated mining scripts like `auto_mine.py` or `mine_sources_sought_presolicitation.py`:**

```python
# At the top of the mining script:
import json

with open('/Users/deedavis/NEXUS BACKEND/NEXUS_LEARNING/PRIORITY_TARGETS_INDEX.json', 'r') as f:
    intel = json.load(f)

# Use priority NAICS in SAM.gov search
priority_naics = []
for tier in ['tier_1_ready_now', 'tier_2_build_capability']:
    for lane in intel['priority_naics'][tier]:
        priority_naics.append(lane['naics'])

# Search SAM.gov with these NAICS codes first
for naics in priority_naics:
    results = search_sam_gov(naics=naics, set_aside='EDWOSB')
    # Process results...
```

---

## CHECKLIST: Using Intelligence Correctly

Before running a mining script or analyzing an opportunity:
- [ ] Load `PRIORITY_TARGETS_INDEX.json` for NAICS codes, keywords, agencies
- [ ] Check if opportunity NAICS matches Tier 1 (ready now) or Tier 2 (build capability)
- [ ] If Tier 1, mark as **HIGH PRIORITY** and fast-track
- [ ] If Tier 2, note sub requirement and begin sub identification
- [ ] If Tier 3, flag as **FUTURE OPPORTUNITY** (not ready yet)
- [ ] Cross-reference buying agency against priority list
- [ ] Use documented DDI advantages in capability statement positioning
- [ ] After bid outcome, update intelligence file with results

---

## WHEN TO UPDATE INTELLIGENCE FILES

**Triggers for updating `NEXUS_LEARNING/` files:**
1. **After a win:** Document what worked, actual margin, key success factors
2. **After a loss:** Document why we lost, what was missing, lessons learned
3. **New market intelligence:** Identified a new contract lane or buying agency pattern
4. **After 10+ bids in a lane:** Adjust priority tier based on actual win rate
5. **Partner change:** New sub identified, new fulfillment partner, new pricing data
6. **Credential change:** New certification obtained (e.g., 8(a) certified = unlock Tier 3 lanes)

---

*NEXUS_LEARNING files are the institutional memory. Use them on every opportunity, update them with every outcome, and DDI gets smarter with every bid.*
