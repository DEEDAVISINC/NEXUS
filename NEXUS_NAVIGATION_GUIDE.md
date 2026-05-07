# NEXUS NAVIGATION GUIDE
## Where Everything Lives and How to Find It

**Version:** 1.0 — May 4, 2026  
**Companion to:** `NEXUS_TRAINING_DOCUMENT.md`  
**Root Path:** `/Users/deedavis/NEXUS BACKEND/`

---

## HOW TO READ THIS GUIDE

Every folder and file in NEXUS has a job. This guide answers three questions:

1. **Where is it?** — Exact path
2. **What is it for?** — Purpose
3. **When do you go there?** — The trigger

Use `Cmd+P` in Cursor to open any file by name. Use the Grep or Glob tools to search inside files. Use this guide to know which directory to target first.

---

## QUICK LOOKUP TABLE — "I NEED TO FIND..."

| What You Need | Go To |
|---|---|
| Company contact info (phone, address, certs) | `COMPANY_INFO_MASTER.md` |
| Today's priorities | `TODAY_AGENDA.md` |
| Today's meetings and scheduled calls | `calendars/SCHEDULED_AGENDA.md` → find today's date section |
| Alexa morning briefing | `DAILY_BRIEFING.md` |
| Active bids and deadlines | `BID_TRACKER_DASHBOARD.md` |
| Full bid pipeline | `BID_TRACKER_COMPLETE.md` |
| Pipeline revenue tally | `PIPELINE_TALLY.md` |
| COs already emailed (don't re-email) | `CLIENT OUTREACH/FEDERAL CO OUTREACH PIPELINE/CO_OUTREACH_TRACKER.md` |
| COs queued for outreach | `CLIENT OUTREACH/FEDERAL CO OUTREACH PIPELINE/PENDING_COS_FOR_LATER.md` |
| Capability statement master template | `BIDS:RESOURCES/ESSENTIALS/DDI_CAP_STATEMENT_DONE.html` |
| Quote response template | `GENERATED_RESPONSES/QUOTE_RESPONSE_TEMPLATE.html` |
| Service pricing (what DDI charges) | `DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md` |
| TPA division reference | `DDI_TPA_DIVISIONS.md` |
| System acronyms | `NEXUS_SYSTEM_ACRONYMS.md` |
| Known system corrections / overrides | `NEXUS_SYSTEM_CORRECTIONS.md` |
| Drug testing compliance | `COMPLIANCE_KNOWLEDGE/DOT_DRUG_TESTING_QUICK_REFERENCE.md` |
| Fatal flaw checklist (drug tests) | `COMPLIANCE_KNOWLEDGE/FATAL_FLAW_CHECKLIST.md` |
| DNA testing reference | `COMPLIANCE_KNOWLEDGE/DNA_TESTING_REFERENCE.md` |
| Fingerprinting reference | `COMPLIANCE_KNOWLEDGE/FINGERPRINTING_REFERENCE.md` |
| Notary reference | `COMPLIANCE_KNOWLEDGE/NOTARY_REFERENCE.md` |
| Occupational health reference | `COMPLIANCE_KNOWLEDGE/OCCUPATIONAL_HEALTH_REFERENCE.md` |
| NAICS priority targets | `NEXUS_LEARNING/PRIORITY_TARGETS_INDEX.json` |
| Medical courier contract lanes | `NEXUS_LEARNING/MEDICAL_COURIER_CONTRACT_TARGETS.md` |
| Partner and supplier account status | `PARTNER_ACCOUNT_UPDATES.md` |
| All active rules | `.cursor/rules/` |
| System insights and lessons | `SYSTEM_INSIGHTS.md` |
| Adaptive bid learning data | `bid_learning_data.json` |

---

## WORKSPACE ROOT — `/Users/deedavis/NEXUS BACKEND/`

The root is the command center. Operational status files live here. Never email anything directly from root — it is all internal.

### Root-Level Status Files (Check These Every Session)

| File | Purpose | Read When |
|---|---|---|
| `TODAY_AGENDA.md` | Today's priorities and scheduled tasks | Every morning |
| `DAILY_BRIEFING.md` | Alexa-readable morning briefing | Every morning; update every night |
| `PIPELINE_TALLY.md` | Nightly pipeline revenue — source of truth | Every morning; rewrite every night |
| `BID_TRACKER_DASHBOARD.md` | Active bids with deadlines | Every session |
| `BID_TRACKER_COMPLETE.md` | Full bid pipeline including past bids | When reviewing full history |
| `PARTNER_ACCOUNT_UPDATES.md` | Status of all supplier/partner accounts | When sourcing or pricing |
| `SYSTEM_INSIGHTS.md` | Lessons learned and system-level notes | When troubleshooting or strategizing |
| `ADAPTIVE_FLOW_AGENDA.md` | Day-of adaptive workflow | Active sessions |

### Root-Level Reference Files

| File | Purpose |
|---|---|
| `COMPANY_INFO_MASTER.md` | Source of truth for all DDI contact info, certifications, and credentials |
| `DDI_TPA_DIVISIONS.md` | All 9 TPA divisions — partners, NAICS codes, pricing, targets |
| `DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md` | All services with DDI agency pricing |
| `NEXUS_SYSTEM_ACRONYMS.md` | Every subsystem defined (GPSS, PRISM, VERTEX, etc.) |
| `NEXUS_SYSTEM_CORRECTIONS.md` | Known corrections and overrides (SWFT denial, old contact info, etc.) |
| `NEXUS_TRAINING_DOCUMENT.md` | Master operator's guide |
| `NEXUS_NAVIGATION_GUIDE.md` | This file |
| `DDI_BUSINESS_MODEL.md` | Margin targets, pricing model, SBA subcontracting limits |
| `SUBCONTRACTOR_BENCH.md` | Pre-vetted subcontractor candidates by service type |

### Root-Level Data Files (Machine-Readable)

| File | Purpose |
|---|---|
| `bid_alerts.json` | Active bid alert cache from mining scripts |
| `bid_learning_data.json` | Adaptive bid system learning data |
| `scan_cache.json` | Last SAM.gov / portal scan results cache |
| `stale_alert_cache.json` | Expired alerts — do not re-trigger |

---

## FOLDER MAP — COMPLETE REFERENCE

---

### `BIDS:RESOURCES/`

**Purpose:** Every solicitation DDI has ever considered bidding. One folder per bid. This is the primary operational workspace.

**Path:** `/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES/`

#### Inside Each Bid Folder

```
BIDS:RESOURCES/[CLIENT] [BID TYPE]/
├── SEND_TO_SUPPLIER/         ← Supplier-safe RFQs and specs ONLY
├── SEND_TO_BUYER/            ← Final submission docs ONLY (cap statement, email, proposal)
├── SEND_TO_SUBCONTRACTOR/    ← Sub-safe scope docs ONLY
├── WORKFLOW_CHECKLIST.md     ← 10-step gated workflow for this bid
└── [Everything else = INTERNAL — original solicitation, strategy, scripts, analysis]
```

**Rule:** If you need to email something, it MUST be in the matching SEND_TO folder. Nothing in root goes out.

#### Special Folders Inside BIDS:RESOURCES/

| Folder | What It Contains |
|---|---|
| `ESSENTIALS/` | Master capability statement template, standard forms, company essentials |
| `ESSENTIALS/DDI_CAP_STATEMENT_DONE.html` | **THE master cap statement template** — 558KB, always use this |
| `CERTIFICATES FOR NEXUS REFERENCES/` | Certifications (EDWOSB, WOSB, SAM, etc.) for bid attachments |
| `COMPANY FORMS/` | W-9, insurance certs, standard bid forms |
| `MARKET RESEARCH LANE/` | Market research documents by service lane |
| `REFERENCE GUIDES/` | Research guides, sourcing templates, pricing guides |
| `PARTNERSHIP DOCUMENTATIONS/` | Teaming agreements, partner MOUs |
| `RCOC MASTER FILES/` | Road Commission for Oakland County — master vendor files |
| `MISCELLANEOUS/` | Overflow documents not assigned to a specific bid |
| `DRUG TESTING SUPPLIES/` | Active drug testing proposals (Macomb, Fulton, Kentucky, etc.) |
| `FEDERAL CO OUTREACH PIPELINE/` | Note: This is actually inside `CLIENT OUTREACH/` |

#### Active Bid Folders by Service Lane (Key Examples)

**Drug Testing:**
- `MACOMB COUNTY DRUG TESTING/`
- `FULTON COUNTY DRUG TESTING/`
- `KENTUCKY THVC DRUG TESTING/`
- `KENTUCKY DMS MINE DRUG TESTING/`
- `AFDW DRUG SCREENING/`
- `SMART DRUG TESTING/`
- `DDOT DRUG TESTING/`

**DNA / Genetic Testing:**
- `DNA PATERNITY TESTING/`
- `KENTUCKY OAG GENETIC TESTING/`
- `ILLINOIS HFS GENETIC TESTING/`
- `LOUISIANA DCFS GENETIC TESTING/`
- `DUTCHESS COUNTY DRUG TEST KITS/`

**Fingerprinting / Identity:**
- `DECA ELECTRONIC FINGERPRINTING/`
- `DHA FINGERPRINTING SUPPORT SERVICES/`
- `NC SBI APPLICANT FINGERPRINTING/`
- `NY DCJS FINGERPRINTING/`
- `OHIO AGO BCI OUT OF STATE FINGERPRINTING/`

**NEMT / Transportation:**
- `HAP CARESOURCE NEMT NETWORK/`
- `MDHHS NEMT BROKERAGE/`
- `REGION 10 MCO NEMT TPA/`
- `CT DIAL-A-RIDE/`
- `STATE DEPT RIDE SHARE/`
- `LAGUNA BEACH SENIOR TRANSPORTATION/`

**Courier / Delivery:**
- `MARYLAND MVA COURIER/`
- `OHIO DOH MEDICAL COURIER/`
- `NIH NCI LN2 DELIVERY/`

**Grounds / Facilities:**
- `FORT MCCOY GROUNDS/`
- `DOD GROUNDS MAINTENANCE MS/`
- `DECA FORT BRAGG LANDSCAPING/`
- `MICHIGAN ARMY RESERVE GROUNDS/`
- `MADISON HEIGHTS LAWN/`

**DLA / Defense Supply:**
- `DLA CABLE ASSEMBLY/`
- `DLA POWER CABLE/`
- `DLA SAFETY VALVE/`
- `DLA WARREN CIRCUIT CARD/`
- `DLA WARREN SHIPPING CONTAINER/`
- `DLA WARREN VALVE/`

**RCOC (Oakland County Road Commission):**
- `RCOC 7731 WIPERS/`
- `RCOC 7732 PAPER/`
- `RCOC 7734 FORESTRY/`
- `RCOC 7776 CHAIN ACCESSORIES/`
- `RCOC 7777 WELDING/`
- `RCOC 7790 SIGNS/`
- `RCOC 7797 AUTOMOTIVE/`
- `RCOC 7798 WIPER BLADES/`
- `RCOC 7799 GREASE AIR COUPLER/`
- `RCOC 7802 BUILDING TOOLS/`
- `RCOC 7803 HAMMERS TAPE LEVELS/`
- `RCOC 7814 TRUCKS/`
- `RCOC 7835 CRACK SEALING/`
- `RCOC 7842 SAFETY SUPPLIES/`
- `RCOC MASTER FILES/`

**SHIELD / MDHHS Program:**
- `MDHHS NEMT BROKERAGE/`
- `MDHHS CROSS-SELL/`

---

### `CLIENT OUTREACH/`

**Purpose:** All outreach to government buyers (COs, procurement officers, agency contacts). One folder per prospect or program.

**Path:** `/Users/deedavis/NEXUS BACKEND/CLIENT OUTREACH/`

**Critical distinction from BIDS:RESOURCES:** Outreach folders are for relationship-building before a bid exists. Bid folders are for active solicitations being pursued.

#### Most Important Subfolder

**`FEDERAL CO OUTREACH PIPELINE/`**  
Path: `CLIENT OUTREACH/FEDERAL CO OUTREACH PIPELINE/`

| File | Purpose |
|---|---|
| `CO_OUTREACH_TRACKER.md` | Every CO who has ALREADY been emailed. CHECK THIS BEFORE DRAFTING ANY NEW CO EMAIL. |
| `PENDING_COS_FOR_LATER.md` | COs identified but not yet emailed — pick up here in next session |

**Rule:** Never generate a CO outreach email without checking `CO_OUTREACH_TRACKER.md` first. Duplicate outreach is unprofessional and damages relationships.

#### Outreach Folder Structure (Inside Each Prospect Folder)

```
CLIENT OUTREACH/[AGENCY] [SERVICE]/
├── SEND_TO_BUYER/
│   ├── SEND_TO_BUYER_EMAIL_READY.md    ← Ready-to-copy email
│   └── [SolNumber]_[Type]_Capability_Statement.html
└── [Internal research, strategy, CO contact info]
```

#### Active Outreach Folders by Service Lane

**Drug Testing:**
- `AFDW DRUG TESTING/`, `BURNS HARBOR PORT DRUG TESTING/`
- `CATA DRUG TESTING/`, `CHOICE PARTNERS DRUG TESTING/`
- `CONSUMERS ENERGY DRUG TESTING/`, `COTA DRUG TESTING/`
- `DDOT DRUG TESTING/`, `DETROIT PORT DRUG TESTING/`
- `DTE DRUG TESTING/`, `DULUTH PORT DRUG TESTING/`
- `GEORGIA DOAS DRUG TESTING/`, `GLWA DRUG TESTING/`
- `ILLINOIS DVA DRUG TESTING/`, `INDIANA DVA DRUG TESTING/`
- `INDYGO DRUG TESTING/`, `LANSING BWL DRUG TESTING/`
- `MI DTMB DRUG TESTING/`, `MI VETERAN HOMES LAB TESTING/`
- `NEW JERSEY DMVA DRUG TESTING/`, `OHIO DVS DRUG TESTING/`
- `PENNSYLVANIA DMVA DRUG TESTING/`, `PORT OF CLEVELAND DRUG TESTING/`
- `PORT OF TOLEDO DRUG TESTING/`, `RTA CLEVELAND DRUG TESTING/`
- `SHASTA COUNTY DRUG TESTING/`, `SMART DRUG TESTING/`
- `TARTA DRUG TESTING/`, `THE RAPID DRUG TESTING/`
- `TIPS DRUG TESTING/`, `TSA DRUG TESTING/`
- `USSF JBA DRUG TESTING/`, `WISCONSIN DVA DRUG TESTING/`

**Fingerprinting / SWFT:**
- `BOP FCI MILAN SWFT/`, `BOP FMC LEXINGTON SWFT/`
- `CBP FINGERPRINTING BPA/`, `DOJ CRIMINAL FINGERPRINTING/`
- `FORT KNOX SWFT/`, `GREAT LAKES NAVAL SWFT/`
- `ICE DHS IDENTITY SERVICES/`, `MI LARA FINGERPRINTING/`
- `NSWC INDIAN HEAD SWFT/`, `OHIO AGO BCI OUT OF STATE FINGERPRINTING/`
- `SCOTT AFB SWFT/`, `SELFRIDGE ANGB FINGERPRINTING/`
- `TACOM FINGERPRINTING/`, `WRIGHT PATTERSON SWFT/`

**NEMT / Transportation:**
- `DC DHCF NEMT/`, `GEORGIA DCH NEMT/`
- `HAP CARESOURCE NEMT NETWORK/`, `MARYLAND DOH NEMT/`
- `MOLINA MICHIGAN NEMT/`, `NY DOH NEMT/`
- `REGION 10 MCO NEMT TPA/`

**Notary / Document Services:**
- `COVIUS NOTARY/`, `DETROIT LAND BANK NOTARY SIGNING/`
- `DHC NOTARY/`, `FLINT HOUSING NOTARY/`
- `GR HOUSING NOTARY/`, `HUD DETROIT NOTARY/`
- `MSHDA NOTARY/`, `PONTIAC HOUSING NOTARY/`
- `RUTKOWSKI LAW NOTARY/`, `SERVICELINK NOTARY/`
- `SE_MICHIGAN_LAW_FIRM_NOTARY/`

**DNA / Genetic Testing:**
- `ICE DNA TESTING/`, `USCIS DNA TESTING/`

**Medical Courier:**
- `COREWELL HEALTH LAB COURIER/`, `NIAID MEDICAL COURIER/`
- `VA CTX COURIER SERVICES/`

**Micro-Purchase Outreach:**
- `MICRO-PURCHASE OUTREACH/` — Templates and tracker for sub-$15K direct purchase outreach

---

### `COMPLIANCE_KNOWLEDGE/`

**Purpose:** Regulatory reference library. READ these files before answering any compliance question. Never guess.

**Path:** `/Users/deedavis/NEXUS BACKEND/COMPLIANCE_KNOWLEDGE/`

| File | What It Covers | When to Read |
|---|---|---|
| `49_CFR_PART_40_REFERENCE.md` | DOT drug testing full regulation breakdown | Detailed regulatory questions, proposal compliance sections |
| `DOT_DRUG_TESTING_QUICK_REFERENCE.md` | Drug testing cheat sheets (cutoffs, timelines, fatal flaws) | On calls, quick answers, pricing for drug testing RFPs |
| `FATAL_FLAW_CHECKLIST.md` | What voids a drug test | PRISM inspection workflows, reviewing scanbacks |
| `DNA_TESTING_REFERENCE.md` | AABB, chain of custody, legal vs. informational DNA | Any DNA testing question, proposal for DNA bids |
| `FINGERPRINTING_REFERENCE.md` | FBI CJIS, livescan vs. ink card, ORI codes, NFIQ quality | Fingerprinting bids, sub vetting for fingerprinting |
| `NOTARY_REFERENCE.md` | Notarial acts, RON, state requirements, journal rules | Notary service questions, RON setup, notary bids |
| `OCCUPATIONAL_HEALTH_REFERENCE.md` | DOT physicals, OSHA, respirators, audiometric testing | Occupational health bids, employer compliance proposals |

---

### `COMPANY_DOCUMENTS/`

**Purpose:** DDI's official company documents — certifications, insurance, tax/legal docs, capability statements.

**Path:** `/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS/`

| Subfolder | Contents |
|---|---|
| `CAPABILITY_STATEMENTS/` | Existing generated capability statements by service type |
| `CERTIFICATIONS/` | EDWOSB cert, WOSB cert, SAM registration, WBENC, MBE certs |
| `COMPANY_INFO/` | Articles of incorporation, registration docs, W-9 |
| `INSURANCE/` | COI, liability policy docs |
| `TAX_LEGAL/` | Tax documents, legal filings |

**When to go here:** When assembling a bid package and need to attach official DDI documents (W-9, certs, COI).

---

### `NEXUS_LEARNING/`

**Purpose:** Market intelligence, contract targeting strategies, and business development playbooks.

**Path:** `/Users/deedavis/NEXUS BACKEND/NEXUS_LEARNING/`

| File | Contents |
|---|---|
| `README.md` | How NEXUS uses intelligence files |
| `PRIORITY_TARGETS_INDEX.json` | Machine-readable priority NAICS codes, keywords, buying agencies |
| `MEDICAL_COURIER_CONTRACT_TARGETS.md` | 15 medical courier lanes, 3-tier prioritization, prime/sub strategy |

**When to go here:**
- Before mining SAM.gov: check priority NAICS codes
- When analyzing a new opportunity: cross-reference against contract lanes
- When generating capability statements: reference buyer pain points
- After a win or loss: update intelligence files

---

### `calendars/`

**Purpose:** All calendar files — .ics event files and the master scheduled agenda mirror.

**Path:** `/Users/deedavis/NEXUS BACKEND/calendars/`

| File | Purpose |
|---|---|
| `SCHEDULED_AGENDA.md` | **Master calendar mirror.** Every `.ics` event must have a matching entry here, organized by `## YYYY-MM-DD — [Weekday]` sections. This is what NEXUS reads for "today's meetings." |
| `[EVENT_NAME].ics` | Individual calendar events — imported into Apple Calendar via `pkill -x Calendar; sleep 2; open file.ics` |

**When to go here:**
- Every morning: read `SCHEDULED_AGENDA.md` for today's date section
- When creating a new event: write `.ics` → update `SCHEDULED_AGENDA.md`
- Goodnight check: verify all new `.ics` files have matching entries

---

### `SERVICE LANE STRATEGIES/`

**Purpose:** Research and strategy documents for each major service lane DDI operates in.

**Path:** `/Users/deedavis/NEXUS BACKEND/SERVICE LANE STRATEGIES/`

| Subfolder | What's Inside |
|---|---|
| `BACKGROUND CHECK SERVICES/` | Strategy for background check contracts |
| `COURIER SERVICES/` | Medical courier and delivery contract strategy |
| `DOCUMENT SHREDDING/` | Shredding service lane strategy |
| `FINGERPRINTING SERVICES/` | Fingerprinting contract targets and approach |
| `FREIGHT TRANSPORTATION/` | Freight brokerage and freight contract strategy |
| `MOVING SERVICES/` | Government moving contract approach |
| `OFFICE SUPPLIES/` | Office supply contract targets |
| `PRINTING SERVICES/` | Printing service contracts |
| `RECORDS MANAGEMENT/` | Records and document management contracts |
| `TRANSLATION SERVICES/` | Translation contract targets |
| `VA LAB SUPPLIES/` | VA-specific lab supply contracts |

**When to go here:** When pivoting into or analyzing a new service lane — read the strategy document before mining.

---

### `GENERATED_RESPONSES/`

**Purpose:** Templates and output storage for quote responses and proposals.

**Path:** `/Users/deedavis/NEXUS BACKEND/GENERATED_RESPONSES/`

| File/Folder | Contents |
|---|---|
| `QUOTE_RESPONSE_TEMPLATE.html` | **The master quote response template.** Copy this when responding to any solicitation. Fill in `{{PLACEHOLDER}}` values. |
| Generated response files | Completed responses — named `[SolNumber]_[Type]_Quote_Response.html` |

---

### `GENERATED_QUOTES/`

**Purpose:** Generated supplier RFQ documents.

**Path:** `/Users/deedavis/NEXUS BACKEND/GENERATED_QUOTES/`

Contains completed RFQ files in DDI-YYYY-### format, generated by `quote_generator.py`.

---

### `generated_capability_statements/`

**Purpose:** Programmatically generated capability statements (from the generator script).

**Path:** `/Users/deedavis/NEXUS BACKEND/generated_capability_statements/`

| Subfolder | Contents |
|---|---|
| `service_capstats/` | Capability statements organized by service type |

**Note:** The master template for manual generation is at `BIDS:RESOURCES/ESSENTIALS/DDI_CAP_STATEMENT_DONE.html`. These generated files are auto-output from the capability statement generator script.

---

### `GRANT_APPLICATION_PACKAGE/`

**Purpose:** Grant research, applications, and CWC (Community Wellness Connections) funding documents.

**Path:** `/Users/deedavis/NEXUS BACKEND/GRANT_APPLICATION_PACKAGE/`

| Subfolder/File | Contents |
|---|---|
| `01_GRANT_MASTER_PROFILE.md` | Master grant profile for DDI and CWC |
| `APPLICATIONS/` | Completed grant applications |
| `CWC_GRANTS/` | CWC-specific grant documents, MDHHS CSBG inquiry |
| `UPLOAD_READY/` | Finalized grant submissions ready to upload |

**Rule:** Before answering any grant eligibility question, read `COMPANY_INFO_MASTER.md` first — verify EIN, certifications, and entity structure against the master file.

---

### `ARCHIVE/`

**Purpose:** Closed bid folders — lost bids, passed opportunities, completed bids.

**Path:** `/Users/deedavis/NEXUS BACKEND/ARCHIVE/`

Contains: `OAKLAND COUNTY FLOW METERS/`, `OAKLAND COUNTY TREATED SALT/`, `OAKLAND UNIVERSITY VENDING/`, plus others as bids are archived.

**When to use:** When a bid is definitively lost or abandoned, move the folder here and rename to `[FOLDER NAME] - LOST`.

---

### `ESSENTIALS/`

**Purpose:** DDI's core collateral materials — the documents that go everywhere.

**Path:** `/Users/deedavis/NEXUS BACKEND/ESSENTIALS/`

| File | Purpose |
|---|---|
| `DDI_April30_Action_Plan.md` | Most recent strategic action plan |
| Broker registration docs | Forward-facing broker registration materials |

**Note:** The capability statement master template is at `BIDS:RESOURCES/ESSENTIALS/DDI_CAP_STATEMENT_DONE.html` — not in this folder.

---

### `PARTNER_OUTREACH/`

**Purpose:** Outreach to potential partners and teaming arrangements (not clients, not suppliers — partners and subcontractors DDI is building relationships with).

**Path:** `/Users/deedavis/NEXUS BACKEND/PARTNER_OUTREACH/`

---

### `MARKET_INTELLIGENCE/`

**Purpose:** Market research data, competitor analysis, and industry intelligence.

**Path:** `/Users/deedavis/NEXUS BACKEND/MARKET_INTELLIGENCE/`

---

### `photos_and_videos/`

**Purpose:** Supporting photos and videos for bids requiring visual evidence (condition reports, delivery confirmations, bid photos).

**Path:** `/Users/deedavis/NEXUS BACKEND/photos_and_videos/`

| Subfolder | Bid It Supports |
|---|---|
| `CPS ENERGY PADLOCKS/` | CPS Energy padlock bid documentation |
| `HCMA UTILITY VEHICLES/` | HCMA utility vehicle bid |
| `RCOC 7734 FORESTRY/` | RCOC forestry bid photos |
| `RCOC 7802 BUILDING TOOLS/` | RCOC building tools — includes submission confirmation |
| `SURGICAL SUPPLIES SOLE SOURCE/` | Surgical supplies sole source documentation |
| `VA ORLANDO COURIER/` | VA Orlando courier documentation |
| `WAYNE COUNTY BARRICADES/` | Wayne County barricade bid photos |
| `ZEP PARTS WASHER/` | ZEP parts washer documentation |

---

### `LBPC FRONT OFFICE FORMS/`

**Purpose:** Lead & Proposal Builder for Claims front office forms — surplus recovery and legal claims intake.

**Path:** `/Users/deedavis/NEXUS BACKEND/LBPC FRONT OFFICE FORMS/`

---

### `DROP_QUOTES_HERE/`

**Purpose:** Inbox for incoming supplier quotes. Suppliers send quotes, Dee drops PDFs here, NEXUS processes them.

**Path:** `/Users/deedavis/NEXUS BACKEND/DROP_QUOTES_HERE/`

**Workflow:** Quote arrives → drop in this folder → `assemble_bid_package.py` picks it up → logs to Airtable → updates opportunity status.

---

### `JOTFORM_ENTRIES/`

**Purpose:** Form submissions from JotForm (PRISM intake forms, client onboarding, etc.).

**Path:** `/Users/deedavis/NEXUS BACKEND/JOTFORM_ENTRIES/`

---

### `uploads/`

**Purpose:** Uploaded files organized by category — system uploads from PRISM, FleetFlow, compliance tracking.

**Path:** `/Users/deedavis/NEXUS BACKEND/uploads/`

| Subfolder | Contents |
|---|---|
| `calendar/` | Calendar-related uploads |
| `compliance/` | Compliance document uploads |
| `confirmations/` | Delivery and service confirmations |
| `fleetflow/` | FleetFlow logistics uploads |
| `inspection_reports/` | PRISM document inspection reports |
| `nexus/` | NEXUS system uploads |
| `notifications/` | System notification logs |
| `prism/` | PRISM field service uploads, scanbacks |
| `qc_reports/` | Quality control reports |
| `receipts/` | Supplier receipts and payment records |
| `regulatory_watch/` | Regulatory monitoring uploads |

---

### `nexus-frontend/`

**Purpose:** React frontend application for the NEXUS dashboard.

**Path:** `/Users/deedavis/NEXUS BACKEND/nexus-frontend/`

| Subfolder/File | Contents |
|---|---|
| `src/` | React source code |
| `src/api/client.ts` | API client configuration |
| `build/` | Production build output |
| `public/` | Static assets |
| `node_modules/` | Installed dependencies |

**When to touch this:** When updating the NEXUS web dashboard or fixing frontend issues.

---

### `scripts/`

**Purpose:** Utility scripts that don't belong to a specific module.

**Path:** `/Users/deedavis/NEXUS BACKEND/scripts/`

---

### `templates/`

**Purpose:** Email and document templates used by the system.

**Path:** `/Users/deedavis/NEXUS BACKEND/templates/`

---

### `email_templates/`

**Purpose:** Email templates organized by category for outreach campaigns.

**Path:** `/Users/deedavis/NEXUS BACKEND/email_templates/`

| Subfolder | Contents |
|---|---|
| `categories/` | Templates organized by email type |

---

### `data/`

**Purpose:** Data files used by automation scripts — lookups, reference tables, historical data.

**Path:** `/Users/deedavis/NEXUS BACKEND/data/`

---

### `logs/`

**Purpose:** System logs from automated scripts, cron jobs, and API calls.

**Path:** `/Users/deedavis/NEXUS BACKEND/logs/`

Check here when debugging automation failures.

---

### `assets/`

**Purpose:** Static assets — images, icons, logos used in templates and cap statements.

**Path:** `/Users/deedavis/NEXUS BACKEND/assets/`

---

### `alexa-skill/` and `alexa_skill_config/`

**Purpose:** Alexa skill configuration for the daily briefing voice integration.

**Path:** `/Users/deedavis/NEXUS BACKEND/alexa-skill/`

The briefing content it reads comes from `DAILY_BRIEFING.md` in root.

---

## THE RULES FOLDER — `.cursor/rules/`

**Purpose:** Every operational rule that governs how NEXUS operates. These are non-negotiable. When a rule covers a task — follow it.

**Path:** `/Users/deedavis/NEXUS BACKEND/.cursor/rules/`

### Rules by Category

**Session & Communication Rules:**
| Rule File | What It Governs |
|---|---|
| `goodnight-goodmorning-ritual.mdc` | Good morning/goodnight full protocol |
| `nexus-session-continuity.mdc` | Mandatory startup reads, session handoff |
| `dee-working-style.mdc` | Dee's communication preferences — direct, honest, push for action |
| `scheduling-preference.mdc` | No morning meetings. 12 PM ET or later, always. |
| `copyable-in-chat.mdc` | "Copyable" = triple-backtick code block |
| `direct-answers-no-fluff.mdc` | No padding, no cheerleading, get to the point |

**Document Generation Rules:**
| Rule File | What It Governs |
|---|---|
| `nexus-outbound-workflow.mdc` | **Master pipeline** — all outbound docs go through this |
| `capability-statement-template-lock.mdc` | Use `DDI_CAP_STATEMENT_DONE.html`. Never rebuild from scratch. |
| `cap-statement-colors.mdc` | Sector color schemes for capability statements |
| `quote-response-document.mdc` | Quote response document requirements |
| `presolicitation-auto-response.mdc` | Auto-generate cap statement + email for any presolicitation |
| `proposalbio-every-email.mdc` | ProposalBio must be applied to every buyer email |
| `human-touch-correspondence.mdc` | Buyer = warm/human. Supplier = business-only. |
| `unified-document-branding.mdc` | Branding consistency across all documents |

**Supplier & Buyer Protection Rules:**
| Rule File | What It Governs |
|---|---|
| `never-reveal-buyer-to-supplier.mdc` | Never include agency names in supplier communications |
| `never-reveal-end-buyer.mdc` | End buyer protection — full rule |
| `rfq-buyer-protection-checklist.mdc` | Mandatory checklist before sending any RFQ |
| `quote-generator-supplier-protection.mdc` | DDI-YYYY-### format, generic client references |
| `never-name-subvendors-network.mdc` | Do not name DDI's sub/vendor network publicly |

**Proposal Quality Rules:**
| Rule File | What It Governs |
|---|---|
| `proposal-readiness-gate.mdc` | 5-gate final check before any proposal is marked "ready" |
| `proposal-infrastructure-discipline.mdc` | Strategy, win theme, compliance tracking before writing |
| `rubric-mirroring-scoreability.mdc` | Mirror rubric language in every scored section |
| `six-second-skim-test.mdc` | Requirement + outcome + proof visible in 6 seconds |
| `clarity-as-strategy.mdc` | Concise = low-friction meaning extraction |
| `relevance-over-volume.mdc` | Relevance beats volume. No capability dumping. |
| `proof-first-delivery-evidence.mdc` | Claim → Proof → Process. Every major claim. |
| `evaluator-defensible-case.mdc` | Build the case evaluators can defend to leadership |
| `compliance-vs-comfort-selection.mdc` | Compliance gets scored. Comfort gets selected. Both required. |
| `executive-summary-selection-justification.mdc` | Executive summary = selection justification document |

**Company & Compliance Rules:**
| Rule File | What It Governs |
|---|---|
| `company-info-verification.mdc` | Correct phone, address, email, CAGE — verified on every document |
| `accuracy-first-protocol.mdc` | No fabrication. If not verified, say so. |
| `rule-compliance-enforcement.mdc` | All rules are active. All rules must be followed. |
| `dot-drug-testing-compliance.mdc` | Drug testing service line knowledge base |
| `grant-strategy-company-info-gate.mdc` | Read COMPANY_INFO_MASTER.md before any grant/strategy answer |

**Business Development Rules:**
| Rule File | What It Governs |
|---|---|
| `revenue-analysis.mdc` | Revenue analysis required before every GO/NO-GO |
| `diversity-inclusion-scanning.mdc` | EDWOSB advantage scan on every solicitation |
| `federal-contracting-learning-engine.mdc` | Learning loop, thresholds, set-aside prioritization |
| `always-ask-questions.mdc` | Draft and submit questions on every solicitation with Q period |
| `state-agency-vendor-status.mdc` | State/local agency contact = registered vendor follow-up tone |
| `bid-folder-organization.mdc` | Folder structure, SEND_TO rules, workflow checklist |
| `subcontractor-management.mdc` | 6 pillars, 12-step onboarding, USASpending check |

**Nightly Pipeline Rules:**
| Rule File | What It Governs |
|---|---|
| `nightly-pipeline-tally.mdc` | Pipeline revenue tally format and trigger |

**Calendar Rules:**
| Rule File | What It Governs |
|---|---|
| `auto-calendar-events.mdc` | .ics format, TZID requirement, pkill-then-open sequence |
| `nexus-calendar-reminder-system.mdc` | Calendar reminder system rules |
| `mandatory-calendar-followups.mdc` | Follow-up scheduling requirements |
| `always-add-contacts.mdc` | Contacts from every outreach must be logged |

**Cadence & Schedule Rules:**
| Rule File | What It Governs |
|---|---|
| `weekly-sector-schedule.mdc` | Weekly cadence for different service lane work |
| `saturday-build-day.mdc` | Saturday = build day protocol |
| `gbis-sunday-cadence.mdc` | Sunday = grant/GBIS work cadence |
| `forecast-hunting-schedule.mdc` | Forecast hunting schedule and frequency |
| `micro-purchase-outreach.mdc` | Micro-purchase outreach cadence and format |

---

## KEY PYTHON SCRIPTS — AUTOMATION ENGINE

All automation scripts live in the workspace root. These run the mining, scoring, and generation systems.

### Mining & Opportunity Scripts

| Script | What It Does |
|---|---|
| `auto_bid_manager.py` | Master bid management automation |
| `adaptive_bid_system.py` | Adaptive scoring and bid prioritization |
| `mine_sources_sought_presolicitation.py` (check scripts/) | Mines SAM.gov for sources sought and presolicitations |
| `federal_forecasts_system.py` (check scripts/) | Federal forecast mining |

### Scoring & Analysis Scripts

| Script | What It Does |
|---|---|
| `historical_pricing_scraper.py` | USASpending archive search — comparable contracts, competitor wins, pricing benchmarks |
| `proposalbio_module.py` | ProposalBio 10-biohack scoring engine (COMPASS™ backend) |

### Generation Scripts

| Script | What It Does |
|---|---|
| `capability_statement_generator.py` | Capability statement generator (Airtable integration) |
| `assemble_bid_package.py` | Assembles complete bid packages |
| `quote_generator.py` (check scripts/) | Supplier RFQ generator |

### Notification & Calendar Scripts

| Script | What It Does |
|---|---|
| `send_bid_notifications.py` | Email notifications when deadlines ≤ 3 days |
| `agenda_manager.py` | Agenda file management |

### API & Backend

| Script | What It Does |
|---|---|
| `api_server.py` | NEXUS backend API server (runs on port 8000) |
| `nexus_backend.py` | Core NEXUS backend logic — Airtable client, NDA generation, teaming agreement generation |

### System Maintenance

| Script | What It Does |
|---|---|
| `audit_nexus_systems.py` | Audits NEXUS system status |
| `audit_document_integration.py` | Audits document integration completeness |
| `CHECK_SYSTEM_NOW.sh` | Quick system status check — run when troubleshooting |
| `FIX_ALL_PROBLEMS.sh` | Fixes known system issues — run when something breaks |

---

## COMMON NAVIGATION SCENARIOS

### Scenario 1: Dee shares a new solicitation

```
1. Is it a presolicitation/sources sought?
   YES → Auto-respond: cap statement + email → no waiting
   NO → Analyze it

2. Find the service type → check if a matching outreach folder already exists
   in CLIENT OUTREACH/ — if yes, we have CO context

3. Create bid folder: BIDS:RESOURCES/[CLIENT] [BID TYPE]/
   mkdir -p "[CLIENT] [BID TYPE]"/{SEND_TO_SUPPLIER,SEND_TO_BUYER,SEND_TO_SUBCONTRACTOR}

4. Run revenue analysis + archive search (historical_pricing_scraper.py)

5. Generate WORKFLOW_CHECKLIST.md in the bid folder

6. Generate supplier RFQ → place in SEND_TO_SUPPLIER/

7. If buyer email needed → generate, apply ProposalBio → place in SEND_TO_BUYER/
```

### Scenario 2: Need to send a CO outreach email

```
1. Check CO_OUTREACH_TRACKER.md — is this CO already emailed?
   YES → Don't re-email. Find status and follow up appropriately.
   NO → Proceed

2. Is DDI a registered vendor with this agency?
   YES (state/local) → Registered vendor follow-up tone
   NO (federal CO found via SAM) → Cold EDWOSB intro tone

3. Check if we have an existing folder in CLIENT OUTREACH/[AGENCY]
   YES → Use existing research for the email
   NO → Create folder, do research first

4. Generate email + cap statement together (always a pair)
   Cap statement → BIDS:RESOURCES/ESSENTIALS/DDI_CAP_STATEMENT_DONE.html (master template)

5. Place both in CLIENT OUTREACH/[AGENCY]/SEND_TO_BUYER/

6. After sending → update CO_OUTREACH_TRACKER.md immediately
```

### Scenario 3: Need company certifications or W-9

```
Go to: COMPANY_DOCUMENTS/CERTIFICATIONS/
       COMPANY_DOCUMENTS/TAX_LEGAL/

Attach from there to bid package.
```

### Scenario 4: Sub-contractor needed for a service contract

```
1. Check SUBCONTRACTOR_BENCH.md — any pre-vetted subs for this service type?

2. If new sub needed → check their legal name on USASpending.gov
   They win contracts in our lane? → Disqualified

3. Draft outreach → SEND_TO_SUBCONTRACTOR/ (no buyer info, no solicitation numbers)

4. NDA → Non-Compete → COI → Teaming Agreement
   (in that order — nothing moves without each step)
```

### Scenario 5: Goodnight ritual

```
1. Git commit + push (all open work)

2. Check calendars/SCHEDULED_AGENDA.md — any orphaned events (ICS without entry)?

3. Write PIPELINE_TALLY.md → then present in chat

4. Build tomorrow's plan → save to TODAY_AGENDA.md

5. Update DAILY_BRIEFING.md (Alexa-friendly, under 60 seconds spoken)
```

### Scenario 6: Something isn't working right with the system

```
1. Run: ./CHECK_SYSTEM_NOW.sh

2. Check: logs/ folder for recent error logs

3. If backend down: lsof -i :8000 (check if api_server.py is running)
   Restart: pkill -f api_server.py && python3 api_server.py &

4. If cron jobs not running: crontab -l (verify jobs installed)

5. Read: NEXUS_SYSTEM_CORRECTIONS.md for known issues and overrides

6. If calendar import not working: pkill -x Calendar; sleep 2; open [file.ics]
   (Calendar MUST be fully closed before opening .ics)
```

---

## NAMING CONVENTIONS QUICK REFERENCE

### Bid Folders

```
Format:  [CLIENT] [BID TYPE]
Case:    ALL CAPS
Example: MACOMB COUNTY DRUG TESTING
         VA ILLIANA COURIER
         RCOC 7842 SAFETY SUPPLIES
```

### Supplier RFQ Numbers

```
Format:  DDI-YYYY-###
Example: DDI-2026-001
         DDI-2026-047
NEVER:   Government's solicitation number
NEVER:   Client name in the number
```

### Capability Statement Files

```
Format:  [SolNumber]_[Type]_Capability_Statement.html
Example: W912DR25QA005_Grounds_Capability_Statement.html
         36C25226Q0235_Courier_Capability_Statement.html
```

### Quote Response Files

```
Format:  [SolNumber]_[Type]_Quote_Response.html
Example: RFQ-2026-007_DrugTesting_Quote_Response.html
```

### Buyer Email Files

```
Always named: SEND_TO_BUYER_EMAIL_READY.md
Location:     Inside each bid or outreach folder's SEND_TO_BUYER/ subfolder
```

### Calendar Event Files

```
Format:   [EVENT_NAME].ics
Example:  PSS_SIGNING_RACHOCKI_2026-05-05.ics
          MACOMB_DRUG_TESTING_DEADLINE_2026-05-15.ics
```

### Bid Folder Status Suffixes

```
Active:   MACOMB COUNTY DRUG TESTING
Won:      MACOMB COUNTY DRUG TESTING - WON
Lost:     MACOMB COUNTY DRUG TESTING - LOST
Archive:  Move to ARCHIVE/ folder
```

---

## FILE SEARCH CHEAT SHEET

When you don't know exactly where something is:

| What to do | How to do it |
|---|---|
| Find a file by name | Glob tool: `*.html` or `*DRUG_TESTING*` |
| Search for text inside files | Grep tool: pattern + directory |
| Find all buyer emails ready to send | Grep: `SEND_TO_BUYER_EMAIL_READY.md` |
| Find all active WORKFLOW_CHECKLIST files | Glob: `WORKFLOW_CHECKLIST.md` in `BIDS:RESOURCES/` |
| Find all .ics calendar files | Glob: `*.ics` in `calendars/` |
| Check if a CO was already emailed | Read `CO_OUTREACH_TRACKER.md` or Grep CO's name in it |
| Find the latest bid for a specific agency | Glob: `*[AGENCY]*` in `BIDS:RESOURCES/` |

---

*This guide exists so no time is wasted asking "where does that live?" Every folder has a job. Every file has a home. Know the map and operate with confidence.*

**Last Updated:** May 4, 2026
