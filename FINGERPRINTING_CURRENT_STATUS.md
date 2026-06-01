# DDI FINGERPRINTING — CURRENT STATUS
## Single Source of Truth | Updated May 28, 2026

**READ THIS BEFORE ANY FINGERPRINTING DOCUMENT, EMAIL, OR PROPOSAL IS GENERATED.**

---

## THE MODEL: DDI + LAKOTA NATIONWIDE FINGERPRINTING PLATFORM

**DDI and Lakota are building a nationwide fingerprinting platform — the only open-network alternative to Fieldprint in the federal market.**

| Role | Who | What They Bring |
|---|---|---|
| **Prime Contractor / TPA** | DDI (EDWOSB) | Contract management, compliance, reporting, QA, network recruitment & management |
| **Technology Partner** | Lakota Software Solutions | SWFT submission capability, WHORL livescan software, EFT Creator, portal/scheduling technology |
| **Collection Network** | Independent livescan operators (to be recruited) | Physical fingerprinting locations across all 50 states + territories |

**This is the same TPA model DDI uses for drug testing (PRISM network) and NEMT (Uber Health). DDI manages the contract and network. Lakota provides the technology. Independent operators provide the boots on the ground.**

**Competitive landscape:** Only Fieldprint (2,200+ sites) currently covers all 50 states + territories for federal SWFT contracts. IdentoGO (IDEMIA) is the other major player. There is NO open-network platform connecting independent operators to federal SWFT work. DDI + Lakota fill that gap.

**Sam Cilento at Lakota is ON BOARD with this platform concept. Lakota provides the technology — DDI builds and manages the network.**

---

## WHAT DDI ACTUALLY HAS RIGHT NOW

| Component | Status | Notes |
|---|---|---|
| **Kojak Scanner** | CONFIRM | Kojak 10-Print Roll Scanner listed in Feb 2026 strategy. Verify hardware in hand. |
| **WHORL Software** | PENDING UPGRADE | Lakota relationship exists. WHORL license not yet purchased. Pricing TBD from Sam. |
| **DDI SWFT Access (Direct)** | DENIED | Applied March 2026. DCSA denied — requires interim Secret clearance + FCL. Requires DD Form 254 from contract award. |
| **Lakota SWFT Access** | LAKOTA HAS SWFT | Lakota holds SWFT authorization. Under DDI+Lakota platform model, Lakota handles SWFT submission as technology partner. DDI does NOT need its own SWFT. |
| **FBI Appendix F** | Via Kojak | Certified through hardware (if Kojak confirmed) |
| **FD-258 Ink Cards** | AVAILABLE | Traditional rolled prints — can be done now |
| **ATF EFT Files** | CONFIRMED | Active in DDI's system. NFA Form 4, FFL applications, ATF eForms. |
| **Lakota Partnership** | ACTIVE | EFT Creator — $85/month. Sam Cilento — scilento@lakotasoftware.com — 304-816-4804 |
| **Federal EDOs** | PENDING | Lakota built FBI eDO system. Confirm WHORL + channel with Sam. |
| **Nationwide Collection Network** | RECRUITING | Infrastructure built. Tracker, outreach templates, and scraper tool ready. Targeting individual operators from state registries (FL: 439+, CA: hundreds). See `FINGERPRINT_OPERATOR_RECRUITMENT/` |

---

## WHAT DDI CAN SAY RIGHT NOW

**YES — Say this:**
- "DDI provides biometric fingerprinting services through our technology partnership with Lakota Software Solutions, the company that built the FBI's NGI, DoD ABIS, and DHS HART systems."
- "Electronic fingerprints are submitted to DCSA via SWFT through our technology partner's authorized channel."
- "We offer FD-258 ink card collection for federal and ATF submissions."
- "We create ATF EFT files for NFA Form 4 applications, FFL submissions, and ATF eForms."
- "DDI operates a managed network model — we recruit, credential, and oversee collection site operators nationwide."

**NO — Never say this:**
- "DDI is SWFT authorized" — DDI was denied; Lakota holds SWFT
- "DDI is SWFT certified" — DDI does not have its own SWFT access
- "Direct FBI submission" — not confirmed for DDI directly
- "Federal EDO capable" — pending confirmation with Sam

**Key distinction:** DDI primes the contract. Lakota provides SWFT submission technology. Say "our technology partner" or "our SWFT-authorized biometric technology partner" — never claim DDI holds SWFT directly.

---

## ACTIVE FEDERAL FINGERPRINTING OPPORTUNITIES (Joint DDI + Lakota)

| Solicitation | Agency | Type | Due | Status | Blocker |
|---|---|---|---|---|---|
| **HT001126QE014** | Defense Health Agency (DHA) | RFQ — WOSB set-aside | Questions: Jun 8 / Offer: TBD (~late Jun) | ACTIVE — Full RFQ dropped May 28 | Need nationwide collection network (50 states + territories) |
| **HQC00526QE015** | Defense Commissary Agency (DeCA) | Sources Sought | Closed Apr 15 | Monitoring for follow-on RFQ | Same network gap |
| **28321326RI0000015** | Social Security Administration (SSA) | RFI | Closed May 19 | Monitoring for follow-on RFQ | Same network gap |

### DHA HT001126QE014 — Key Details
- **Volume:** 3,600 electronic + 1,200 hard copy = 4,800/year
- **Coverage:** All 50 states, Guam, PR, USVI
- **Period:** Sep 2026 – Sep 2031 (base + 4 options)
- **Evaluation:** Best Value (Tech + PP > Price)
- **Set-Aside:** WOSB — limited competition
- **CO:** Cherish D. Young (cherish.d.young2.civ@health.mil)
- **COR:** Vanessa Conklin (vanessa.conklin.civ@health.mil)
- **Contract Specialist:** Mary Anne Young (mary.a.young138.ctr@health.mil)
- **Submission:** Via email (5 separate documents, 15-page limit total for tech)

---

## PLATFORM BUILD — WHAT NEEDS TO HAPPEN

### Phase 1: Technology Confirmation (NOW)
- [ ] Confirm Lakota SWFT capability scope (how many SONs, volume capacity, geographic limits)
- [ ] Confirm WHORL upgrade pricing and timeline
- [ ] Confirm portal/scheduling capability (does Lakota have applicant-facing scheduling?)
- [ ] Confirm reporting/dashboard capability (DHA requires electronic portal for queries)
- [ ] Confirm federal EDO processing capability

### Phase 2: Network Recruitment (PRIORITY — IN PROGRESS)

**Full recruitment infrastructure:** `FINGERPRINT_OPERATOR_RECRUITMENT/`
- `RECRUITMENT_TRACKER.md` — State-by-state tracker with 53 coverage areas, sources, priorities
- `OPERATOR_OUTREACH_TEMPLATE.md` — Email, phone, LinkedIn, Facebook, NLSA outreach templates
- `fingerprint_operator_scraper.py` — Scraper tool for state operator registries

**Recruitment Sources (Individual Operators, NOT Companies):**
1. **State livescan operator registries** — FL has 439+, CA has hundreds. Every state maintains a list.
2. **NLSA (National Live Scan Association)** — Industry network, member community, conferences
3. **Mobile notaries who also fingerprint** — NNA, Snapdocs, NotaryGadget crossover
4. **Google Maps / Yelp / Thumbtack** — Independent operators searchable by metro area
5. **LinkedIn direct outreach** — "livescan operator", "mobile fingerprinting"
6. **Facebook groups** — "Mobile Fingerprinting", "Live Scan Operators"
7. **Existing DDI contacts** — 3D Ink Signatures, notary network referrals

**Phase 2 Steps:**
- [ ] Scrape FL FDLE operator list (439+ operators with contact info)
- [ ] Scrape CA DOJ operator list (hundreds of independents)
- [ ] Start cold outreach to independent operators in HIGH-priority states
- [ ] Determine operator compensation model (per-transaction, $25-50/session target)
- [ ] Build operator onboarding process (equipment verification, WHORL install, test submission)
- [ ] Build coverage map — track which states are covered
- [ ] Target: 53 coverage areas (50 states + GU, PR, USVI)

### Phase 3: First Contract Win
- [ ] DHA HT001126QE014 is the first target — submit questions by June 8
- [ ] Use DHA as proof of concept for the platform
- [ ] After award: scale network, pursue SSA recompete, DeCA follow-on, other DoD contracts

---

## WHAT CHANGES THIS STATUS

| Event | What It Unlocks |
|---|---|
| Lakota SWFT scope confirmed | Can claim SWFT submission in proposals via Lakota |
| WHORL license purchased | Full livescan collection + EBTS + federal EDO |
| First 10 operators recruited (10 states) | Partial coverage — enough for smaller contracts |
| 50-state coverage achieved | DHA, SSA, DeCA, and all nationwide contracts viable |
| Win a contract with DD Form 254 | DDI gets its OWN SWFT access via FCL (long-term) |

---

## THREE REVENUE LANES

**Full strategy:** `FINGERPRINTING_THREE_LANES.md`

| Lane | Status | Gate |
|---|---|---|
| **Lane 1: Interstate Professional Licensure** | Partial | FD-258 cards available now. Electronic submission pending WHORL. |
| **Lane 2: ATF / NFA Firearms** | ACTIVE | FD-258 cards + ATF EFT file creation confirmed. |
| **Lane 3: Federal Contracts (DHA, DeCA, SSA, DoD)** | BUILDING | Lakota provides SWFT technology. DDI building collection network. DHA is target contract. |

---

## OUTREACH EMAILS ALREADY SENT CLAIMING SWFT

Emails sent pre-March 2026 claiming DDI SWFT authorization (before denial). Cannot be recalled.

Folders with sent SWFT outreach:
- `CLIENT OUTREACH/BOP FMC LEXINGTON SWFT/`
- `CLIENT OUTREACH/BOP FCI MILAN SWFT/`
- `CLIENT OUTREACH/ATF CHICAGO SWFT/`
- `CLIENT OUTREACH/ATF COLUMBUS SWFT/`
- `CLIENT OUTREACH/SCOTT AFB SWFT/`
- `CLIENT OUTREACH/GREAT LAKES NAVAL SWFT/`
- `CLIENT OUTREACH/FORT KNOX SWFT/`
- `CLIENT OUTREACH/WRIGHT PATTERSON SWFT/`
- `CLIENT OUTREACH/ATF DETROIT FINGERPRINTING/`
- `CLIENT OUTREACH/TACOM FINGERPRINTING/`
- `CLIENT OUTREACH/DOJ CRIMINAL FINGERPRINTING/`
- `CLIENT OUTREACH/SELFRIDGE ANGB FINGERPRINTING/`

**If any CO responds:** Do NOT confirm DDI SWFT capability. Say services are provided through our SWFT-authorized biometric technology partner (Lakota). Confirm scheduling and availability before committing.

---

## FBI BIOMETRIC SERVICES SECTION — INBOUND CORRESPONDENCE (LOG)

| Date (received) | From | Summary | Meaning |
|---|---|---|---|
| **~Apr 2026** | **Identity@FBI.gov** (Terri — Biometric Services Section) | Documentation forwarded to proper unit for review. | Routing receipt only — no action unless deadline. |

**Follow-up:** FBI Biometric Services — **304-625-5590** — Mon–Fri, 8–5 ET.

---

*This document supersedes all prior fingerprinting capability claims. When in doubt, check here first.*
*Owner: Dieasha D. Davis | Updated: May 28, 2026*
