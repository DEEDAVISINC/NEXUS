# NEXUS CURRENT SESSION STATE

**Purpose:** Persistent record of session findings, active work, and system corrections. Cursor reads this at session start.

**Last Updated:** 2026-03-24

---

## CRITICAL SYSTEM ISSUE — PAST PERFORMANCE DATA

**Problem identified 03/24/2026:** The system has NO centralized past performance file. Client/contract data is scattered across 6+ files and some of it is FABRICATED.

### CONFIRMED FABRICATION — MUST BE REMOVED:
- **`DEE_DAVIS_CAPABILITY_STATEMENT.md`** — Lists RCOC (Road Commission for Oakland County) as past performance with specific dollar amounts ($3,977.60 tools package, etc.) and claims like "on-time delivery, full compliance." **DDI NEVER BID ON RCOC. This is fabricated.** Dee confirmed 03/24/2026.
- **`DRAFT_Technical_Capability_Narrative.md`** — Contains generic federal past performance claims (Army, DLA, GSA, VA) with "strong CPARS" and "100% on-time." These are **AI-generated placeholders, NOT real past performance.**
- **`GENERATED_RESPONSES/NSWC_SWFT_Response_v*.json`** — Contains fabricated dollar figures ("$2.1M contract value", "99.7% uptime", "1,456 successful collections"). **AI-generated, NOT real.**

### CONFIRMED REAL CLIENTS/WORK (from VENDOR_CLIENT_CONTACTS.md + Dee's confirmation):

| Client | Contact | Work DDI Performs | Location in System |
|--------|---------|-------------------|--------------------|
| **Gideon Logistics** | Makibla Gideon, 313-407-1936 | Courier services, logistics docs, regulatory filings, biometric fingerprinting, workforce management, DOT compliance & drug testing (Jan 2023–Present) | VENDOR_CLIENT_CONTACTS.md line 860, capability_statement_generator.py, nexus_opportunity_hunter_api.py |
| **The P58 Trust (Penei & Isabella Sewell)** | Joe Palumbo, Esq., 858.688.3610 | CLIENT — Private wealth agent services: estate documentation, notarization, legal document prep, trust administration, certified document courier for high-profile clients | VENDOR_CLIENT_CONTACTS.md line 866 |
| **JMT Docs** | Lloyd Pace, 855-325-3565 | Document preparation and document delivery services | VENDOR_CLIENT_CONTACTS.md line 873 |
| **Perry Johnson Mortgage Co.** | Compliance Dept, 800-800-0450 | CLIENT — Biometric fingerprinting for NMLS and regulatory compliance. Executive credentialing. | VENDOR_CLIENT_CONTACTS.md line 878 |
| **United Wholesale Mortgage (UWM)** | Danielle Doebel, Licensing Dept | CLIENT — Biometric fingerprinting for CEO Mat Ishbia and top executives for financial/security licensing | VENDOR_CLIENT_CONTACTS.md line 886 |
| **Champion Homes** | In building (755 W Big Beaver) | Fingerprinting / compliance services | Referenced in outreach emails, DDCSS plan |
| **Empora Title** | Partnership | Licensed title agent partnership — title work across multiple states | capability_statement_generator.py |
| **State of Michigan** | N/A (program ended) | Immigration Clerical Assistant (ICA) — state government contract, now phased out | COMPANY_INFO_MASTER.md line 663 |
| **Notary / Signing Agency** | DDI is the agency | 20+ years Michigan Notary, CNTDA certified, nationwide signing agency network, 2,000+ documented closings | COMPANY_INFO_MASTER.md line 669 |

### STILL NEEDS FROM DEE:
- Specific contract values/periods for each client
- Whether DDI is prime or sub on each engagement
- Specific deliverables and outcomes for each
- Any clients completely missing from the system
- Details on JMT, P58, and Gideon work scope beyond what's listed above

### ACTION REQUIRED:
1. Build `PAST_PERFORMANCE.md` — single source of truth for all real client work
2. Remove fabricated RCOC past performance from `DEE_DAVIS_CAPABILITY_STATEMENT.md`
3. Flag all AI-generated past performance claims across the system
4. Every future cap statement and proposal pulls ONLY from `PAST_PERFORMANCE.md`

---

## ACTIVE CONVERSATIONS

### Tracy Riley — ICE DHS (PRIORITY)
- **Status:** Tracy replied 03/24 asking for past performance / prior experience in courier services (government or non-government)
- **DDI sent:** Full capabilities email (courier, notary, apostille, DNA, fingerprinting) on 03/24
- **Tracy's follow-up:** "Do you have any contracts with other industry partners for which you supply courier services? Non-government customers?"
- **BLOCKER:** DDI needs to respond with real past performance. The system couldn't surface it properly — this is what triggered the past performance audit.
- **What DDI CAN cite:** Gideon Logistics (courier/logistics since Jan 2023), P58 Trust (certified document courier for high-profile clients), JMT Docs (document delivery)
- **POCs introduced:** Mark R. Gonzales, Marilyn L. Doty, Jennifer Doran (program office)
- **CO contact:** Tracy Riley, Section Chief/CO, 469-858-2855, Tracy.Riley@ice.dhs.gov

### OMNIA Partners — CLOSED
- **Status:** Done. No supplier registration exists. DDI submitted mailing list form multiple times. Strategy: watch for drug testing contract rebid (Accurate/First Advantage expires Dec 2027). No more chasing.

---

## OPEN LOOPS

| Item | Context | Due Date | Priority |
|------|---------|----------|----------|
| Respond to Tracy Riley (ICE) | Past performance for courier services | ASAP | HIGH |
| Build PAST_PERFORMANCE.md | Centralized source of truth | ASAP | CRITICAL |
| Remove fabricated RCOC data | DEE_DAVIS_CAPABILITY_STATEMENT.md | ASAP | CRITICAL |
| Lisa TerMorshuizen call prep | Choice Partners — drug testing | Check calendar | HIGH |
| CMS EUS Help Desk call | Fix NPI login for NPPES | TBD | MEDIUM |
| Jean Saporita — National Drug Screening | Confirm call, 321-608-0409 | If no response by Monday noon — call | MEDIUM |
| CHAMPS NEMT application | Monitor weekly (App #20260323058125) | Weekly | MEDIUM |

---

## MEDICAL TOURISM TRANSPORTATION — NEW SERVICE LINE (Documented 03/22/2026)
- Added to `DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md`
- Added to `DDCSS_PROFESSIONAL_SERVICES_EXECUTION_PLAN.md`
- DDCSS play — private sector, cash pay, premium market
- Phase 1: Uber Black fulfillment, Phase 2: Uber partnership pitch
- DDI Certified Medical Transport Specialist = the moat
- Pilot city: Miami
- Status: DOCUMENTED — launch when ready

---

*This file is the handoff document. Next session reads this FIRST.*
