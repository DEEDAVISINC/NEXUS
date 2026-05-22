# PRISM TPA UNIVERSAL BLUEPRINT
## The 8-Layer Architecture — Every TPA Division, Same Structure

**Created:** May 21, 2026
**Owner:** Dee Davis Inc.
**Status:** MASTER ARCHITECTURE
**Rule:** Every TPA division in PRISM follows this exact 8-layer framework. No shortcuts. No "we'll add it later." If a layer is missing, the TPA is not complete.

---

## THE PRINCIPLE

PRISM is DDI's "Uber for field services." Every TPA division operates the same way:

1. A request comes in
2. The nearest qualified agent gets dispatched
3. The work gets done with compliance tracking
4. Quality gets verified
5. Results flow to the client
6. DDI manages everything. The client sees ONE company.

**The 8 layers below make this happen. They are the same for every TPA — only the service type, credentials, and partner integrations change.**

---

## THE 7 LAYERS

### LAYER 1: DISPATCH ENGINE
**What it does:** Finds the nearest available, credentialed agent and sends them the job.

| Component | Description |
|---|---|
| Proximity matching | GPS/zip-based — closest qualified agent gets first shot |
| Credential gating | No dispatch without active certs, insurance, background |
| Accept/Decline window | Agent has X minutes to accept before it goes to next |
| Cascade logic | Declined → next nearest → next nearest → admin alert if no one accepts |
| Priority routing | Emergency/STAT → wider radius, higher pay, bypass queue |
| Scheduling | On-demand (now) OR scheduled (future date/time) |

### LAYER 2: FIELD AGENT MOBILE APP
**What the agent sees on their phone:**

| Feature | Description |
|---|---|
| Online/Offline toggle | "I'm available" — like Uber driver mode |
| New job notification | Push notification with location, service type, pay |
| Accept / Decline | Tap to accept, auto-routes to next if declined |
| Navigation | Built-in directions to site |
| Service checklist | Step-by-step for the specific service type |
| Document capture | Photo/scan upload (CCF, COC, scanback, BOL, POD) |
| Mark complete | Timestamps, GPS confirmation |
| Payment tracking | See earnings, pending payments, history |

### LAYER 3: PROGRAM MANAGEMENT MODULE
**What makes each TPA's workflow unique:**

| TPA | Program Type | How It Works |
|---|---|---|
| Drug Testing | Randomized testing pools (employer + court) | Daily selection engine, call-in hotline, web check-in, fail-to-call alerts |
| Fingerprinting | Batch credentialing schedules | Agency uploads roster, PRISM schedules appointments |
| DNA Testing | Court-ordered / immigration appointments | Court sets schedule, PRISM coordinates collection |
| Notary | Recurring signing schedules | Title companies / law firms schedule through portal |
| NEMT | Standing orders + on-demand rides | MCO trip requests, recurring dialysis/therapy rides |
| Logistics/Freight | Load management + route optimization | FleetFlow integration, carrier matching |
| Background Checks | Recurring screening programs | Employer sets cadence, PRISM auto-triggers |
| Medical Credentialing | License/cert tracking + renewal | Automated monitoring, expiration alerts, re-verification |
| Workforce Compliance | DQ file + training management | Unified employer compliance dashboard |

### LAYER 4: REAL-TIME AVAILABILITY MAP
**What admin sees:**

| Component | Description |
|---|---|
| Live agent locations | Map showing all online agents by service type |
| Coverage heat map | Where DDI has coverage vs. gaps |
| Credential overlay | Filter by cert type (DOT collector, BAT, livescan, notary, CDL) |
| Equipment overlay | Filter by equipment (livescan device, collection kit, vehicle type) |
| Recruiting alerts | "No coverage in [area]" → triggers recruiting action |

### LAYER 5: CLIENT SELF-SERVICE PORTAL
**What the client (court, employer, MCO, title company) sees:**

| Feature | Description |
|---|---|
| Request service | On-demand or scheduled, by service type |
| Track status | Real-time order status (dispatched, in progress, complete) |
| View results | After QC/specialist review — results delivered here |
| Compliance reports | Monthly/quarterly reports, audit-ready |
| Roster management | Upload/manage participants (employees, defendants, drivers) |
| Billing/invoicing | View invoices, payment history |
| Program dashboard | Random pool status, testing rates, compliance percentages |

#### EMAIL-AS-IDENTITY MODEL (No Logins)

The client portal and intake form use **email address as the primary identifier** — no accounts, no passwords, no login walls.

| Principle | Implementation |
|---|---|
| **Email = Identity** | Client's email is the unique key for all CRM records, results delivery, receipts, and invoices |
| **No Login Required** | Intake form collects email upfront. No registration, no passwords, no "forgot password" friction |
| **Returning Client Recognition** | When a returning email is entered, PRISM auto-fills company, name, phone, address from CRM |
| **Results Delivery** | Results, receipts, and invoices route to the client's email by default, plus optional CC recipients (supervisor, HR, court officer) |
| **CRM Auto-Link** | Every submission creates or updates a CRM contact record keyed by email |
| **Delivery Preferences** | Client chooses: Email Only, Email + Fax, or Secure Portal Link |
| **CC Recipients** | Up to 2 additional email recipients per request — supervisor/HR/court officer |

**Why no logins:** Logins add backend complexity (auth, sessions, password resets, security) that DDI doesn't need at this stage. Email-as-identity gives non-anonymity (we know who they are) without login friction. A full auth portal can layer on top later if contract volume justifies it.

**Backend flow:**
```
Client enters email → PRISM /crm/lookup checks CRM contacts
  → FOUND: auto-fill form fields, flag as returning client
  → NOT FOUND: create new CRM contact on submission
Submission → results/receipts route to email + any CC addresses
```

### LAYER 6: PARTNER API INTEGRATION
**The "Uber partner" for each TPA — direct digital connection:**

| TPA | Partner | Integration |
|---|---|---|
| Drug Testing | Quest Diagnostics / eScreen | eCCF electronic chain of custody, automated result pull-back |
| Drug Testing | 12PanelNow | Supply ordering, inventory management |
| Fingerprinting | Lakota Software | EFT Creator, livescan submission, EDO (FBI background checks) |
| Background | Lakota Software | EDO — FBI background check processing |
| DNA Testing | DDC Laboratories | Kit ordering, result delivery, AABB compliance |
| Notary | Snapdocs / signing platforms | Order intake, agent matching |
| NEMT | Uber Health / Lyft Healthcare | Ride dispatch API, trip tracking |
| Logistics | FleetFlow / Bankers Factoring | Load management, carrier pay |
| Background | NCS | Screening API, result delivery |
| Occ Health | Concentra | Referral routing, result intake |
| Medical Cred | CAQH / NPDB / state boards | Primary source verification |
| Workforce | E-Verify / training platforms | I-9 automation, compliance tracking |

### LAYER 7: SPECIALIST ROUTING
**Automated handoff to the human expert when needed:**

| TPA | Specialist | When It Triggers |
|---|---|---|
| Drug Testing | MRO (AMRO) | Positive, invalid, or substituted result → MRO reviews, contacts donor, makes determination |
| Drug Testing | SAP | Positive DOT result → return-to-duty process requires SAP evaluation |
| Fingerprinting | Rejection handler | FBI/state rejection → re-roll or ink card fallback |
| Fingerprinting | Lakota EDO processing | Fingerprint capture → Lakota EDO → FBI background check result |
| DNA Testing | AABB reviewer | Chain of custody discrepancy → manual review |
| Notary | QC Inspector (PRISM engine) | Scanback errors → correction request to agent |
| NEMT | Trip authorization | MCO pre-auth required → automated or manual approval |
| Logistics | Compliance check | Driver DOT status, CDL verification, drug test current |
| Background | Adverse action handler | Negative result → FCRA adverse action letter process |
| Medical Cred | Credentialing committee | Flags → committee review for privileges |

### LAYER 8: CRM — RELATIONSHIP MANAGEMENT (Collective + By Sector)
**The relationship engine that turns contacts into contracts.**

Right now DDI tracks COs in markdown files and partner follow-ups in scattered notes. Layer 8 puts every person, every interaction, every follow-up into ONE system — viewable collectively across all TPAs OR filtered by sector.

#### TWO VIEWS — Same Data

| View | What You See | When You Use It |
|---|---|---|
| **COLLECTIVE** | Every contact across all 9 TPAs. Full pipeline. All follow-ups. | Morning briefing, weekly review, "who haven't I talked to?" |
| **BY SECTOR** | Contacts filtered to one TPA division. Sector-specific pipeline. | Working a drug testing bid, building NEMT relationships, fingerprinting outreach |

#### CONTACT TYPES

| Type | Who They Are | Examples |
|---|---|---|
| **Buyer** | The person who signs the contract or influences the award | Contracting officers, procurement directors, court administrators, MCO program managers |
| **Decision Influencer** | People who don't sign but shape the decision | Agency end-users, facility managers, HR directors, probation officers |
| **Partner** | Fulfillment partners DDI works through | Quest, AMRO, Lakota, Uber Health, Roadie, NCS, DDC, Concentra, 12PanelNow |
| **Agent** | 1099 field agents in DDI's network | Collectors, notaries, print techs, couriers, drivers |
| **Prospect** | Potential clients not yet under contract | Leads from SAM mining, portal finds, cold outreach, referrals |
| **Referral Source** | People who send DDI business | SBA counselors, PTAC advisors, prime contractors, chamber contacts |

#### CONTACT RECORD — What's Stored Per Person

| Field | Description |
|---|---|
| Name | Full name |
| Title / Role | Contracting Officer, HR Director, Procurement Specialist, etc. |
| Organization | Agency, company, court, MCO, etc. |
| Organization Type | Federal / State / Local / Commercial / MCO / Court / Hospital |
| Email | Primary contact email |
| Phone | Direct phone |
| TPA Sectors | Which DDI divisions they're relevant to (multi-select) |
| Contact Type | Buyer / Decision Influencer / Partner / Agent / Prospect / Referral |
| Source | How DDI found them (SAM mining, vendor portal, referral, conference, cold outreach) |
| Relationship Stage | New / Introduced / Engaged / Active Client / Dormant / Lost |
| Last Contact Date | When DDI last reached out or heard from them |
| Next Follow-Up | Scheduled follow-up date |
| Follow-Up Cadence | 7 / 14 / 21 / 30 / 60 / 90 days |
| Interaction Log | Every email, call, meeting — timestamped with notes |
| Linked Opportunities | Solicitations, bids, contracts tied to this person |
| Linked Documents | Emails sent, cap statements delivered, proposals submitted |
| Tags | Custom tags (EDWOSB-friendly, micro-purchase authority, set-aside champion, etc.) |
| Notes | Free text — personality, preferences, what they care about |
| Sentiment | Hot / Warm / Neutral / Cold — based on last interaction |

#### INTERACTION LOG — Every Touchpoint

| Field | Description |
|---|---|
| Date | When it happened |
| Type | Email Sent / Email Received / Call / Meeting / Portal Message / LinkedIn / Voicemail |
| Direction | Outbound (DDI initiated) / Inbound (they reached out) |
| Summary | 1-2 sentences — what was discussed |
| Outcome | Connected / Left VM / No Response / Meeting Set / Sent Materials / Contract Discussed |
| Follow-Up Action | What DDI needs to do next |
| Follow-Up Date | When to do it |
| Linked Opportunity | Which bid/contract this relates to |
| Attachments | Cap statement sent, email copy, meeting notes |

#### PIPELINE BY SECTOR — What the Sector CRM View Shows

Each TPA division gets its own pipeline view:

| Stage | Meaning | Action |
|---|---|---|
| **Lead** | Contact identified, no outreach yet | Research, prepare intro |
| **Contacted** | First email/call sent | Wait for response, set 7-day follow-up |
| **Engaged** | They responded, conversation happening | Send cap statement, ask smart questions |
| **Opportunity** | Specific solicitation or need identified | Build bid, prepare proposal |
| **Proposal Sent** | DDI submitted response | Follow up, monitor award |
| **Negotiation** | Award discussion, pricing, terms | Finalize contract details |
| **Won — Active Client** | Contract awarded, services being delivered | Deliver, manage, build past performance |
| **Lost** | Didn't win this one | Debrief, stay in touch, try next opportunity |
| **Dormant** | Haven't heard from them in 60+ days | Re-engage or deprioritize |

#### SECTOR CRM VIEWS — What Each TPA Sees

| TPA | Key Contact Types | Pipeline Focus |
|---|---|---|
| Drug Testing | Court admins, probation officers, HR directors, transit safety managers, DER contacts | Court contracts, employer programs, random pool clients |
| Fingerprinting | Agency credentialing officers, licensing board staff, security managers | Federal credentialing, state licensing, healthcare onboarding |
| DNA Testing | Family court clerks, child support agency directors, immigration attorneys | Court-ordered paternity, USCIS immigration, private cases |
| Notary | Title company ops managers, law firm office managers, lender contacts | Signing service contracts, law firm retainers, lender accounts |
| NEMT | MCO transportation directors, Medicaid program managers, hospital discharge planners | MCO brokerage contracts, hospital partnerships, state Medicaid |
| Logistics | Federal contracting officers, FEMA coordinators, USPS route managers | Federal freight, FEMA TSP, USPS HCR, commercial loads |
| Background | HR directors, staffing agency owners, property managers, school district HR | Pre-employment programs, tenant screening, volunteer screening |
| Med Credentialing | Hospital CMOs, telehealth ops directors, VA credentialing staff | Credentialing contracts, telehealth programs, IHS/VA |
| Workforce | Federal contractor HR, fleet safety directors, school district superintendents | Compliance programs, DQ file management, training contracts |

#### AUTOMATED CRM ACTIONS

| Trigger | Action |
|---|---|
| Follow-up date reached | Alert Dee: "[Name] at [Org] — 14-day follow-up due" |
| No contact in 30 days | Flag as "cooling off" — suggest re-engagement |
| No contact in 60 days | Flag as "dormant" — suggest check-in or archive |
| New SAM opportunity matches contact's agency | Alert: "[Agency] just posted [solicitation] — you know [Name] there" |
| Contact responds to email | Auto-update Last Contact Date + move to "Engaged" |
| Bid submitted to contact's agency | Link opportunity to contact, set award follow-up |
| Contract won | Move contact to "Active Client," create PRISM client record |
| Contact birthday / agency anniversary | Optional: send personalized note (human touch) |

#### DASHBOARDS

**Collective Dashboard (All Sectors):**
- Total contacts by type (buyers, prospects, partners, agents)
- Follow-ups due today / this week / overdue
- Pipeline value by stage
- Contacts by relationship stage (New → Active Client)
- Sector distribution chart
- "Cold" contacts — haven't been touched in 30+ days
- Recent interactions timeline

**Sector Dashboard (Per TPA):**
- Same metrics, filtered to one division
- Top opportunities by value
- Key relationships with notes
- Sector-specific pipeline

#### REPLACES THESE CURRENT FILES

| Current File | Replaced By |
|---|---|
| `CO_OUTREACH_TRACKER.md` | CRM → Buyer contacts, Federal sector |
| `PENDING_COS_FOR_LATER.md` | CRM → Lead stage contacts |
| `PARTNER_ACCOUNT_UPDATES.md` | CRM → Partner contact records |
| `PARTNERSHIPS/PARTNERSHIPS_INDEX.md` | CRM → Partner records with interaction logs |
| Scattered follow-up notes | CRM → Automated follow-up cadence |
| Manual morning briefing lookups | CRM → Dashboard: "Follow-ups due today" |

#### CRM SCHEMA (Airtable)

**TABLE: PRISM CRM CONTACTS**

| # | Field | Type |
|---|---|---|
| 1 | Contact ID | Auto Number (CRM-XXXX) |
| 2 | Full Name | Short Text |
| 3 | Title | Short Text |
| 4 | Organization | Short Text |
| 5 | Organization Type | Single Select (Federal / State / Local / Commercial / MCO / Court / Hospital / Staffing / Other) |
| 6 | Email | Email |
| 7 | Phone | Phone |
| 8 | TPA Sectors | Multiple Select (Drug Testing / Fingerprinting / DNA / Notary / NEMT / Logistics / Background / Med Cred / Workforce) |
| 9 | Contact Type | Single Select (Buyer / Decision Influencer / Partner / Agent / Prospect / Referral) |
| 10 | Source | Single Select (SAM Mining / Vendor Portal / Referral / Conference / Cold Outreach / Website / LinkedIn / RADAR) |
| 11 | Relationship Stage | Single Select (New / Introduced / Engaged / Active Client / Dormant / Lost) |
| 12 | Sentiment | Single Select (Hot / Warm / Neutral / Cold) |
| 13 | Last Contact Date | Date |
| 14 | Next Follow-Up | Date |
| 15 | Follow-Up Cadence | Single Select (7 / 14 / 21 / 30 / 60 / 90 days) |
| 16 | Linked Opportunities | Linked Record → Bid Tracker |
| 17 | Tags | Multiple Select (custom) |
| 18 | Notes | Long Text |
| 19 | Created Date | Created Time |
| 20 | Last Modified | Last Modified Time |

**TABLE: PRISM CRM INTERACTIONS**

| # | Field | Type |
|---|---|---|
| 1 | Interaction ID | Auto Number |
| 2 | Contact | Linked Record → CRM Contacts |
| 3 | Date | Date |
| 4 | Type | Single Select (Email Sent / Email Received / Call / Meeting / Portal / LinkedIn / Voicemail / Text) |
| 5 | Direction | Single Select (Outbound / Inbound) |
| 6 | Summary | Long Text |
| 7 | Outcome | Single Select (Connected / Left VM / No Response / Meeting Set / Sent Materials / Contract Discussed / Referred) |
| 8 | Follow-Up Action | Short Text |
| 9 | Follow-Up Date | Date |
| 10 | Linked Opportunity | Linked Record → Bid Tracker |
| 11 | Attachments | Attachment (email copy, cap statement, etc.) |
| 12 | Created By | Short Text |
| 13 | Created Date | Created Time |

---

## TPA DIVISION IMPLEMENTATION STATUS

| TPA | L1 Dispatch | L2 Mobile App | L3 Program Mgmt | L4 Availability | L5 Client Portal | L6 Partner API | L7 Specialist | L8 CRM | Overall |
|---|---|---|---|---|---|---|---|---|---|
| 1 - Drug Testing | ❌ Build | ❌ Build | ⚠️ Random pools exist, need court module | ❌ Build | ❌ Build | ⚠️ eScreen pending | ⚠️ AMRO manual | ❌ Build | **35%** |
| 2 - Fingerprinting | ❌ Build | ❌ Build | ⚠️ Basic | ❌ Build | ❌ Build | ⚠️ Lakota pending | ⚠️ Manual | ❌ Build | **25%** |
| 3 - DNA Testing | ❌ Build | ❌ Build | ⚠️ Basic | ❌ Build | ❌ Build | ✅ DDC working | ⚠️ Manual | ❌ Build | **20%** |
| 4 - Notary | ❌ Build | ❌ Build | ⚠️ Law firm channel exists | ❌ Build | ❌ Build | ⚠️ Snapdocs pending | ✅ QC engine built | ❌ Build | **30%** |
| 5 - NEMT | ⚠️ Uber/Lyft dispatch exists | ❌ Build | ⚠️ Basic | ❌ Build | ❌ Build | ✅ Uber/Lyft working | ⚠️ Manual | ❌ Build | **30%** |
| 6 - Logistics | ❌ Build | ❌ Build | ❌ Missing | ❌ Build | ❌ Build | ❌ Missing | ❌ Missing | ❌ Build | **10%** |
| 7 - Background | ❌ Build | N/A (digital) | ❌ Missing | N/A | ❌ Build | ⚠️ NCS + Lakota EDO | ❌ Missing | ❌ Build | **15%** |
| 8 - Med Cred | ❌ Build | N/A | ❌ Missing | N/A | ❌ Build | ❌ Missing | ❌ Missing | ❌ Build | **5%** |
| 9 - Workforce | ❌ Build | N/A | ❌ Missing | N/A | ❌ Build | ❌ Missing | ❌ Missing | ❌ Build | **5%** |

---

## WHAT PRISM ALREADY HAS (Foundation — 65%)

These are SHARED across all TPAs and don't need to be rebuilt per division:

| Component | Status | File |
|---|---|---|
| Service router (45 services, pricing, routing) | ✅ Done | `prism_service_router.py` |
| Order lifecycle (new → closed) | ✅ Done | `prism_orders_api.py` |
| Credential gating (no dispatch without certs) | ✅ Done | `prism_service_router.py` |
| Credential bundles (DDI Agent Baseline, etc.) | ✅ Done | `prism_service_router.py` |
| QC / document inspection engine | ✅ Done | `prism_inspection_engine.py` |
| Adaptive learning (pattern recognition) | ✅ Done | `prism_qc_learning.py` |
| Document AI | ✅ Done | `prism_document_ai.py` |
| Notifications | ✅ Done | `prism_notifications_api.py` |
| Compliance API | ✅ Done | `prism_compliance_api.py` |
| DOT drug testing compliance | ✅ Done | `prism_dot_compliance.py` |
| Clearinghouse integration | ✅ Done | `prism_clearinghouse.py` |
| Random pool management | ✅ Done | `prism_random_pool.py` |
| BAT / breath alcohol | ✅ Done | `prism_bat.py` |
| POCT / instant cups | ✅ Done | `prism_poct.py` |
| DNA compliance | ✅ Done | `prism_dna_compliance.py` |
| Fingerprinting compliance | ✅ Done | `prism_fingerprinting_compliance.py` |
| Notary compliance | ✅ Done | `prism_notary_compliance.py` |
| Occ health compliance | ✅ Done | `prism_occupational_health_compliance.py` |
| NEMT dispatch | ✅ Done | `prism_nemt.py` |
| Uber Health API | ✅ Done | `prism_uber_health.py` |
| Lyft Healthcare API | ✅ Done | `prism_lyft_healthcare.py` |
| Airtable schema (11 tables) | ✅ Defined | `PRISM_MASTER.md` |

---

## BUILD PRIORITY — WHAT COMPLETES THE BLUEPRINT

### UNIVERSAL BUILDS (Apply to ALL TPAs)

These are built ONCE and shared across every division:

| # | Build | What It Creates | Impact |
|---|---|---|---|
| U1 | **Dispatch Engine** | `prism_collection_dispatch.py` → generic dispatch for any agent type | Unlocks L1 for ALL TPAs |
| U2 | **Agent Mobile App** | React Native or PWA — agent-facing mobile interface | Unlocks L2 for ALL TPAs |
| U3 | **Availability System** | Real-time online/offline, GPS, coverage map | Unlocks L4 for ALL TPAs |
| U4 | **Client Portal** | Web portal — request services, view results, compliance reports | Unlocks L5 for ALL TPAs |
| U5 | **CRM** | Contact management, interaction tracking, pipeline by sector, follow-up automation | Unlocks L8 for ALL TPAs — replaces markdown trackers |

### TPA-SPECIFIC BUILDS (Customize per division)

| # | Build | TPA | What It Creates |
|---|---|---|---|
| S1 | Court Randomized Testing | TPA 1 (Drug Testing) | Call-in system, random selection, fail-to-call alerts |
| S2 | eScreen/Quest API pipe | TPA 1 (Drug Testing) | eCCF, automated results |
| S3 | AMRO digital handoff | TPA 1 (Drug Testing) | MRO routing, result verification |
| S4 | NCS API integration | TPA 7 (Background) | Screening orders, result delivery |
| S5 | Lakota API integration | TPA 2 (Fingerprinting) | EFT submission, livescan routing |
| S6 | FleetFlow integration | TPA 6 (Logistics) | Load management, carrier dispatch |
| S7 | CAQH/NPDB integration | TPA 8 (Med Cred) | Primary source verification |
| S8 | E-Verify automation | TPA 9 (Workforce) | I-9 compliance |

### BUILD ORDER

```
PHASE 1 — FOUNDATION (Unlocks everything)
├── U1: Dispatch Engine ← BUILD THIS FIRST
├── U2: Agent Mobile App
└── S1: Court Randomized Testing (Oakland County needs this NOW)

PHASE 2 — PARTNER PIPES
├── S2: eScreen/Quest API
├── S3: AMRO digital handoff
├── S4: NCS API
└── S5: Lakota API

PHASE 3 — CLIENT EXPERIENCE + CRM
├── U3: Availability System
├── U4: Client Portal
├── U5: CRM (Collective + By Sector)
└── S6: FleetFlow integration

PHASE 4 — BUILDING TPAs
├── S7: CAQH/NPDB (Medical Credentialing)
└── S8: E-Verify (Workforce Compliance)
```

---

## THE COMPETITIVE MOAT

When all 7 layers are built across all 9 TPAs, PRISM becomes:

**The only platform that combines:**
- Multi-service dispatch (drug testing + fingerprinting + DNA + notary + NEMT + courier + background + credentialing + workforce)
- Compliance brain per service type (DOT, AABB, FBI CJIS, state notary, MCO, FMCSA)
- QC inspection engine (catches errors before they ship)
- Adaptive learning (gets smarter with volume)
- Client portal (one login, all services)
- Partner API mesh (Quest, DDC, Lakota, NCS, Uber Health, eScreen, Concentra)
- Sector CRM with collective view (every contact, every interaction, every follow-up — across all 9 TPAs)

Nobody else has this stack. Not READI Collect. Not FieldWare. Not NexaScreen. Not any single competitor. They each do ONE thing. PRISM does ALL of them under one roof.

**And when PRISM is mature enough — it becomes a SaaS product DDI can license to other TPAs.** That's the long game.

---

## RULES

1. **Every TPA division MUST have all 8 layers before it's considered "complete."**
2. **Universal builds (U1-U5) are built ONCE and shared.** Don't rebuild dispatch or CRM for every TPA.
3. **TPA-specific builds customize the universal layers.** Drug testing gets court randomization. Notary gets signing platform integration. NEMT gets MCO trip auth. Same framework, different config.
4. **"Uber-First" strategy still applies.** While PRISM is being built, use partner platforms (DATCS, Uber Health, Roadie, etc.) for immediate fulfillment. PRISM replaces them over time as each layer comes online.
5. **The agent mobile app is ONE app for ALL services.** A collector who is also a notary sees both service types in the same app. One login, multiple specialties.
6. **Client portal is ONE portal for ALL services.** An employer who needs drug testing AND background checks AND physicals logs into one DDI portal. One contract. One invoice. One point of contact.

---

*This blueprint exists because DDI's competitive advantage is not performing the service — it's managing the contract and the relationships. PRISM is the engine that makes that management scalable across 9 TPA divisions, hundreds of agents, thousands of orders, and every contact DDI has ever talked to.*

*Build it once. Run it everywhere. Own the stack. Know everyone.*
