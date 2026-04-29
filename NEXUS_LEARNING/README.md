# NEXUS LEARNING — MARKET INTELLIGENCE & TARGETING KNOWLEDGE BASE

**Purpose:** This directory contains curated market intelligence, contract targeting strategies, and business development playbooks that NEXUS uses to identify opportunities, prioritize lanes, and recommend strategic actions.

---

## ⚡ RELATIONSHIP WITH NEXUS AUTO-LEARNING AI

**NEXUS has TWO learning systems that work together:**

### **1. STATIC INTELLIGENCE (This Directory)**
**What:** Documented market research, known contract lanes, priority NAICS codes  
**Source:** Manual research, market analysis, strategic decisions  
**Purpose:** Provides the STARTING POINT — what to look for before outcomes exist  
**Files:** `PRIORITY_TARGETS_INDEX.json`, `MEDICAL_COURIER_CONTRACT_TARGETS.md`  
**Example:** "NAICS 492110 lab courier contracts are Tier 1 priority for DDI"

### **2. DYNAMIC LEARNING ENGINE (`nexus_learning_engine.py`)**
**What:** Tracks every action Dee takes, analyzes outcomes, adjusts scoring weights  
**Source:** Real bid outcomes (won/lost), response rates, actual margins  
**Purpose:** REFINES priorities based on what actually works  
**Storage:** `nexus_learning_db.json`, `bid_learning_data.json`  
**Example:** "Lab courier bids have 60% win rate → increase weight by +5"

### **How They Work Together:**

```
STEP 1: Static Intelligence Seeds the System
├─ Mining script searches SAM.gov for NAICS 492110 (from PRIORITY_TARGETS_INDEX.json)
├─ Scores it as Tier 1 priority (from MEDICAL_COURIER_CONTRACT_TARGETS.md)
└─ Initial score: 75/100 (based on documented strategy)

STEP 2: Dynamic Learning Refines Over Time
├─ DDI bids on 5 lab courier contracts
├─ Outcome: 3 wins, 2 losses (60% win rate)
├─ Learning engine adjusts weight: lab_courier priority +5
└─ New score for next lab courier opportunity: 82/100

STEP 3: Continuous Improvement
├─ After 20 lab courier bids, pattern emerges:
│   - State health labs: 80% win rate → weight +10
│   - County clinics: 40% win rate → weight -5
├─ Static intelligence updated with findings
└─ Next time, prioritize state health labs over county clinics
```

### **Integration Points:**

| Static Intelligence Provides | Dynamic Learning Adjusts |
|---|---|
| Priority NAICS codes to search | Which NAICS codes have highest win rates |
| Documented entry points | Which entry points actually work |
| Estimated margins (40-50%) | Actual margins achieved (55% avg) |
| Priority buying agencies | Which agencies respond/award most |
| Sub requirements | Which subs actually perform well |

---

## HOW NEXUS USES THIS INTELLIGENCE

**1. Opportunity Mining:**
- When scanning SAM.gov, BidNet, or other sources, NEXUS cross-references NAICS codes, keywords, and buying agencies from these intelligence files
- Prioritizes opportunities that match DDI's proven lanes and credentials
- Flags high-value contract types identified in targeting documents

**2. Strategic Recommendations:**
- When analyzing a new opportunity, NEXUS checks if it matches a documented contract lane
- Provides context on typical margins, entry points, and sub requirements
- Suggests teaming partners based on service type

**3. Capability Statement Generation:**
- References contract-specific language and buyer pain points from intelligence files
- Tailors past performance and credentials to match the contract lane
- Uses documented entry points to position DDI's value proposition

**4. Learning & Pattern Recognition:**
- Tracks which lanes generate wins vs. losses
- Updates priority tiers based on actual results
- Identifies new lanes based on emerging market patterns

---

## INTELLIGENCE FILES

### **MEDICAL_COURIER_CONTRACT_TARGETS.md**
**Added:** April 29, 2026  
**Source:** Market research — nationwide medical courier contract landscape

**Contains:**
- 15 specific medical courier contract types
- Buying agencies for each lane (state health depts, hospitals, corrections, etc.)
- NAICS codes and entry points
- DDI credentials alignment
- Prime/sub strategy for all 15 lanes
- 3-tier prioritization (Tier 1 = ready now, Tier 2 = 6-12 months, Tier 3 = 12-24 months)

**NEXUS Mining Use Cases:**
- SAM.gov searches for NAICS 492110 contracts
- Prioritize State Public Health Lab, County Clinic, and Jail Medical Unit buyers
- Flag any "specimen pickup," "vaccine transport," "medication delivery" keywords
- Recommend lab courier lane for any state health department RFPs

---

## ADDING NEW INTELLIGENCE

When new market intelligence is identified:

1. **Create a new .md file** in this directory with clear naming:
   - `[SERVICE_LINE]_CONTRACT_TARGETS.md`
   - `[INDUSTRY]_BUYING_PATTERNS.md`
   - `[NAICS]_MARKET_INTELLIGENCE.md`

2. **Use this structure:**
   ```
   # [TITLE]
   Source: [where this came from]
   Date: [when identified]
   
   ## CONTRACT TYPE MATRIX
   [Table with contract types, buyers, NAICS, entry points]
   
   ## DDI CREDENTIALS ALIGNMENT
   [What DDI already has that fits]
   
   ## STRATEGIC TARGETS BY PRIORITY
   [Tier 1, 2, 3 prioritization]
   
   ## BUSINESS DEVELOPMENT STRATEGY
   [Actionable next steps]
   ```

3. **Update this README** with a new entry in the "Intelligence Files" section

4. **Tag relevant NAICS codes** for NEXUS mining scripts to prioritize

---

## NAICS CODES TO MONITOR (MASTER LIST)

This list grows as new intelligence is added. NEXUS mining scripts prioritize these:

**Transport & Courier:**
- **492110** — Couriers and Express Delivery Services ⭐ PRIMARY
- **621511** — Medical Laboratories (specimen pickup)
- **621610** — Home Health Care Services (DME delivery)
- **562112** — Hazardous Waste Collection (medical waste)
- **621512** — Diagnostic Imaging Centers (equipment logistics)
- **541714** — Research and Development in Biotechnology (clinical trials)
- **621420** — Outpatient Mental Health Centers (behavioral health)
- **621991** — Blood and Organ Banks (OPO transport)

**Drug Testing & Occupational Health:**
- **812990** — All Other Personal Services (drug testing)
- **621511** — Medical Laboratories (toxicology)
- **621399** — Offices of All Other Miscellaneous Health Practitioners

**Fingerprinting & Background:**
- **561611** — Investigation & Background Check Services
- **541930** — Translation and Interpretation Services (document verification)

**DNA Testing:**
- **621511** — Medical Laboratories (DNA/paternity testing)
- **541380** — Testing Laboratories (forensic DNA)

**Notary & Legal Services:**
- **541110** — Offices of Lawyers (notary support)
- **561410** — Document Preparation Services

---

## NEXUS LEARNING LOOP

**How NEXUS improves over time:**

1. **Opportunity Identified** → NEXUS flags an RFP that matches intelligence
2. **DDI Pursues** → Bid submitted using documented strategy
3. **Outcome Tracked** → Win/loss recorded
4. **Intelligence Updated** → If win, confirm strategy works; if loss, analyze why
5. **Pattern Recognition** → After 10+ data points, NEXUS adjusts priority tiers

**Example:**
- Initial intelligence says "Lab Courier = Tier 1 — DDI ready now"
- DDI wins 3 out of 5 lab courier bids (60% win rate)
- NEXUS confirms: Lab Courier = HIGH PRIORITY lane
- Future lab courier RFPs auto-flagged as "strong fit, pursue immediately"

---

## INTEGRATION WITH EXISTING SYSTEMS

### **A. Static Intelligence (This Directory) Referenced By:**

- `auto_mine.py` — Prioritizes NAICS codes from intelligence files
- `mine_sources_sought_presolicitation.py` — Matches keywords to documented lanes
- `federal_forecasts_system.py` — Cross-references buying agencies
- `historical_pricing_scraper.py` — Validates typical contract values for each lane
- `capability_statement_generator.py` — Uses entry points for positioning language
- ProposalBio — References buyer pain points and DDI differentiators

### **B. Dynamic Learning Engine Integration:**

**When an opportunity is discovered:**
```python
from nexus_learning_engine import nxlearn

# Load static priority from NEXUS_LEARNING
with open('NEXUS_LEARNING/PRIORITY_TARGETS_INDEX.json') as f:
    priorities = json.load(f)
    
# Score opportunity using static intelligence
if opp_naics in tier1_naics:
    base_score = 75  # High priority from static intelligence

# Get learned weights from dynamic engine
from nexus_learning_engine import get_engine
engine = get_engine()
learned_weights = engine.get_weights('opportunities')

# Apply learned adjustments
if 'naics_match' in learned_weights:
    adjusted_score = base_score + learned_weights['naics_match']
```

**When an outcome occurs:**
```python
# Log outcome to learning engine (auto-updates weights)
nxlearn('opportunities', opp_id, 'won', {
    'naics': '492110',
    'agency': 'Michigan State Public Health Lab',
    'set_aside': 'EDWOSB',
    'value_range': '$100K-$500K',
    'source': 'SAM.gov'
})

# After 10+ outcomes, analyze patterns
engine.analyze('opportunities')  # Adjusts weights automatically

# Check for insights
insights = engine.get_insights('opportunities')
# Example insight: "NAICS 492110 + State Health Labs = 80% win rate"
```

**Updating static intelligence with learned patterns:**
```python
# After significant data (20+ bids in a lane), update static files
status = engine.get_status()
if status['domains']['opportunities']['level'] == 'mature':
    # Get learned patterns
    insights = engine.get_insights('opportunities', limit=50)
    
    # Update MEDICAL_COURIER_CONTRACT_TARGETS.md with:
    # - Actual win rates by lane
    # - Actual margins achieved
    # - Agency-specific success patterns
    # - Which subs performed best
```

---

*This directory is the institutional memory of DDI's market intelligence. Every pattern, every lane, every lesson learned goes here so NEXUS gets smarter with every bid.*
