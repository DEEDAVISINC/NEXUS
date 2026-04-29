# NEXUS LEARNING — MARKET INTELLIGENCE & TARGETING KNOWLEDGE BASE

**Purpose:** This directory contains curated market intelligence, contract targeting strategies, and business development playbooks that NEXUS uses to identify opportunities, prioritize lanes, and recommend strategic actions.

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

**NEXUS_LEARNING files are referenced by:**

- `auto_mine.py` — Prioritizes NAICS codes from intelligence files
- `mine_sources_sought_presolicitation.py` — Matches keywords to documented lanes
- `federal_forecasts_system.py` — Cross-references buying agencies
- `historical_pricing_scraper.py` — Validates typical contract values for each lane
- `capability_statement_generator.py` — Uses entry points for positioning language
- ProposalBio — References buyer pain points and DDI differentiators

---

*This directory is the institutional memory of DDI's market intelligence. Every pattern, every lane, every lesson learned goes here so NEXUS gets smarter with every bid.*
