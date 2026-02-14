# PRISM — MASTER DOCUMENT
## Professional Resource Inspection & Service Management
## NEXUS Module #8 — Field Service Dispatch, Order Management & Document Verification

**Created:** February 13, 2026
**Owner:** Dee Davis Inc.
**Status:** ARCHITECTURE — Ready for Build
**Tagline:** "See every detail. Miss nothing."

---

# TABLE OF CONTENTS

1. [What PRISM Is](#what-prism-is)
2. [The Core Flow](#the-core-flow)
3. [Service Types & Colors](#service-types--colors)
4. [Vendor Types (Suppliers vs Subs vs Field Agents)](#three-vendor-types)
5. [Field Agent Types & Certifications](#field-agent-types)
6. [Order Lifecycle & Statuses](#order-lifecycle)
7. [Client Rules Engine](#client-rules-engine)
8. [Document Inspection Engine](#document-inspection-engine)
9. [Adaptive Learning System](#adaptive-learning)
10. [Admin Dashboard (What Dee Sees)](#admin-dashboard)
11. [Field Agent Portal (What Agents See)](#field-agent-portal)
12. [NEXUS Integration Map](#nexus-integrations)
13. [Pricing & Fees](#pricing--fees)
14. [Notifications](#notifications)
15. [Shipping & Lab Tracking](#shipping--tracking)
16. [Airtable Schema (11 Tables)](#airtable-schema)
17. [API Endpoints](#api-endpoints)
18. [Build Phases](#build-phases)
19. [Saved Names for Future Use](#saved-names)

---

# 1. WHAT PRISM IS

PRISM is the **service delivery engine** inside NEXUS. It manages the entire lifecycle of field service orders — from the moment a client needs a notary, drug test, DNA collection, fingerprinting, or courier, through dispatch, execution, document verification, and completion.

**In one sentence:** An order comes in, a field agent gets assigned, documents flow through, the work gets done, quality gets verified, and nobody ships a bad package.

**The gap it fills:**
```
DDCSS closes Blueprint contract
        ↓
PRISM schedules, dispatches, executes, and verifies the services
        ↓
VERTEX invoices (retainer + per-unit billing)
        ↓
ATLAS tracks the overall contract
```

---

# 2. THE CORE FLOW

```
1.  Order comes in
2.  Field agent assigned
3.  Documents + rules sent to agent's portal
4.  Agent confirms — "Got it, I accept"
5.  Agent confirms appointment with signer/subject
6.  Agent downloads documents, goes to appointment
7.  Service happens
8.  Agent marks order "Complete"
9.  Agent scans completed documents into system (scanback)
10. System inspects scans for errors
11a. CLEAN → Verified → Ship / submit / close
11b. ERRORS → Message to agent: "Fix these" → Back to 9
```

**That's the whole product.** Everything else is built on top of this.

---

# 3. SERVICE TYPES & COLORS

### DDI Brand Colors (Portal & Agent-Facing UI)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| **Deep Blue** | Navy | `#1B2A4A` | Backgrounds, headers, cards, primary dark |
| **Teal** | Cyan/Teal | `#2DD4BF` | Accent, highlights, links, active states, borders |
| **Pink** | Hot Pink | `#EC4899` | CTAs, buttons, DDI logo badge, energy accents |
| **Gold** | Amber | `#F59E0B` | Certifications, premium touches, warm highlights |

**These are the DDI brand colors from the logo/website, used across the Agent Portal, Login, and Registration pages. Service-type colors below are separate — used for order identification across both admin and agent views.**

### Service Type Colors

Every service type has a distinct color. You know what an order is without reading a word.

| Service | Color | Hex | Background |
|---------|-------|-----|------------|
| **Notary** | 🟠 Orange | `#F97316` | `#FFF7ED` |
| **Notary (RON)** | 🟣 Indigo | `#6366F1` | `#EEF2FF` |
| **Drug Test (DOT)** | 🔴 Red | `#EF4444` | `#FEF2F2` |
| **Drug Test (Non-DOT)** | 🔴 Rose | `#F43F5E` | `#FFF1F2` |
| **DNA Collection** | 🟣 Purple | `#A855F7` | `#FAF5FF` |
| **Fingerprinting / EFT** | 🟢 Green | `#22C55E` | `#F0FDF4` |
| **Courier/Runner** | 🔵 Blue | `#3B82F6` | `#EFF6FF` |
| **Background Check** | ⚫ Slate | `#64748B` | `#F8FAFC` |
| **Apostille** | 🟡 Gold | `#EAB308` | `#FEFCE8` |
| **Process Serving** | 🟢 Teal | `#14B8A6` | `#F0FDFA` |

**All notary work is mobile.** DDI goes TO the signer. The only split is in-person (orange) vs. remote/digital RON (indigo) — different workflows.

**How colors appear:** Order card left border stripe + tinted background, kanban cards, calendar events, dispatch timeline blocks, analytics charts, agent specialty badges, dropdown menus.

### Service-to-Document Mapping

| Service | Documents In | The Service | Scanback |
|---------|-------------|-------------|----------|
| Notary | Loan package or docs to notarize | Signer signs, agent notarizes (always mobile) | Scan of all signed/notarized pages |
| Drug Test (DOT) | CCF form + kit instructions | Donor provides specimen, collector completes CCF | Photo/scan of completed CCF |
| Drug Test (Non-DOT) | Collection form + kit | Same as DOT, different form | Photo/scan of completed form |
| DNA Collection | Chain of custody + kit | Subject provides sample, collector documents | Photo/scan of completed COC |
| Fingerprinting / EFT | Print cards, EFT scans, submission forms | Subject gets printed (ink or electronic) | Scan of completed cards or EFT confirmation |
| Background Check | Authorization/consent forms | Subject signs consent | Scan of signed authorization |
| Courier/Runner | Pickup/delivery instructions | Agent picks up or delivers | Confirmation photo / signature of receipt |
| Apostille | Documents for authentication | Agent submits to SOS | Scan of apostilled documents |

---

# 4. THREE VENDOR TYPES

| Role | System | What They Do | Examples |
|------|--------|-------------|----------|
| **Suppliers** | GPSS | Sell products, provide quotes | Grainger, Fastenal, Master Lock |
| **Subcontractors** | Sub Portal | Project work under DDI as prime | Pressure washers, landscapers, janitorial |
| **Field Agents** | PRISM | Accept orders, execute services, upload scanbacks | Notaries, collectors, techs, couriers |

Three different words. Three different tables. Three different portals. Zero confusion.

---

# 5. FIELD AGENT TYPES

| Specialty | Color | What They Do | Required Certs |
|-----------|-------|-------------|----------------|
| **Signing Agent** | 🟠 | Notary work, loan signings, RON | Notary commission, E&O, NNA (preferred) |
| **Collection Agent** | 🔴/🟣 | Drug testing, DNA collection | Collector cert, DOT cert, AABB training |
| **Print Technician** | 🟢 | Fingerprinting — ink cards, LiveScan, EFT scans (ATF, FBI, state agencies) | LiveScan cert, FBI channeling, EFT authorization |
| **Courier** | 🔵 | Pickup/delivery, court filing, process serving | Valid license, vehicle insurance |
| **Background Specialist** | ⚫ | Background check processing | FCRA certification |

One person can hold multiple specialties. PRISM tracks certs and only assigns orders the agent is qualified for.

---

# 6. ORDER LIFECYCLE

```
NEW → ASSIGNED → CONFIRMED → IN PROGRESS → COMPLETED → SCANNED BACK → VERIFIED → CLOSED
                                                              ↓
                                                        ERRORS FOUND → CORRECTION REQUESTED → RE-SCANNED → VERIFIED → CLOSED
```

| Status | Meaning |
|--------|---------|
| New | Created, no agent yet |
| Assigned | Agent selected, awaiting their confirmation |
| Confirmed | Agent accepted, appointment scheduled |
| In Progress | Agent at appointment, service happening |
| Completed | Service done, scanback pending |
| Scanned Back | Documents uploaded |
| Under Review | System/human reviewing |
| Errors Found | Inspection flagged issues |
| Correction Requested | Agent notified with specific errors |
| Re-scanned | Agent uploaded corrected docs |
| Verified | Passed inspection — clean |
| Closed | Shipped/submitted, VERTEX invoiced |
| Cancelled | Order cancelled |

---

# 7. CLIENT RULES ENGINE

When an order is created, client requirements auto-attach from their profile:

**Standard Flags:**
- Scanback required
- Blue pen only / Black pen only
- Legal paper for deed
- Two copies (one for signer)
- ID copies must be uploaded
- Witness required (state-specific auto-applied)
- Single-sided printing
- Ship same day
- FedEx ship center only (no CVS/Walgreens)
- Lab submission by next business day
- Chain of custody photos required
- Temperature reading required (drug test)
- Photo of sealed specimen (drug test / DNA)

**Custom Notes:** Free-text for anything that doesn't fit flags.
**Per-Client Profiles:** Blueprint clients have saved rules — auto-apply to every order.

---

# 8. DOCUMENT INSPECTION ENGINE

### The 7 Fundamentals (Never Change)

1. Is every required **signature** present?
2. Is every required **initial** present?
3. Is every required **date** filled in?
4. Is the **notary seal/stamp** present where required?
5. Are all required **pages/forms** included?
6. Is the **ID copy** included (when required)?
7. Are there **markings where there shouldn't be**?

### How It Works

```
Scanback uploaded → Page count check → Signature/mark detection (AI vision)
→ Client/order rules applied → Error classification → Result
```

**Error Classification:**
- **CRITICAL** — Will be rejected, must fix before shipping
- **WARNING** — Possible issue, human should verify
- **INFO** — Minor note, doesn't block

### Error Report Example
```
CRITICAL ERRORS (2):
  Page 12 — Signature line 2 appears unsigned
  Page 37 — Missing borrower initial (statement 3/5)

WARNINGS (1):
  Page 3 — Signature on possible wrong line

STATUS: HOLD — Correct before shipping.
```

---

# 9. ADAPTIVE LEARNING

**Level 1 — Rule-Based:** What you program. "Every notarized page needs a seal." Never changes.

**Level 2 — Pattern Recognition:** What it learns from volume. "98% of accepted packages have ink here. This one doesn't. Flag." Nobody taught it — derived from data.

**Level 3 — Anomaly Detection:** What it discovers on its own. "This scanback looks different from every other one of this type."

**The Feedback Loop:**
```
Scanback → System inspects → Document ships → Accepted or Rejected?
→ Outcome feeds back → System adjusts → Next inspection smarter
```

Start with human + system. System earns autonomy over time through demonstrated accuracy.

---

# 10. ADMIN DASHBOARD (What Dee Sees)

### 9 Tabs:

```
🎯 Command Center | 📋 Orders | 🚀 Dispatch | 📸 Scanbacks | 👤 Field Agents
🏢 Clients | 🔍 Inspection | 💰 Payments | 📊 Analytics
```

### Command Center (Landing Page)
**Top row cards:** Active Orders | Today's Appointments | Awaiting Scanback | Errors Found
**Second row:** Orders This Month | Active Field Agents | First-Pass Clean Rate | Revenue This Week

**Needs Your Attention:** Red/yellow alerts — errors found, unassigned orders, expiring certs

**Today's Schedule:** Color-coded by service type
```
9:00 AM  │ 🔴 DOT Drug Test    │ Champion Homes, Auburn Hills │ Marcus Brown
10:30 AM │ 🟢 Fingerprinting   │ Staffing Solutions, Southfield │ Dee Davis
1:00 PM  │ 🟠 Notary           │ Troy, MI │ Sarah Chen
3:00 PM  │ 🟣 DNA Collection   │ Law Office, Royal Oak │ Dee Davis
4:30 PM  │ 🟠 Notary           │ Farmington Hills │ Lisa Park
```

**Order Pipeline:** Live status counts across all stages
**Agent Leaderboard:** Top agents by performance this month

### Orders Tab
- List view, Kanban view, Calendar view
- Color-coded rows/cards by service type
- Create new order modal with color-coded dropdown
- Filter by status, type, agent, client, date

### Dispatch Tab
- Unassigned orders with qualified agents ranked by distance/availability/score
- Agent timeline (schedule blocks colored by service type)
- One-click assign

### Scanbacks Tab
- Filter: Needs Review | Clean | Errors
- Document viewer with red/green highlights on flagged pages
- Override, send correction, re-inspect actions

### Field Agents Tab
- Agent cards with specialties, performance scores, cert status
- Certification expiration alerts (90-day, 30-day, expired)
- Auto-suspend if critical cert expires

### Clients Tab
- Blueprint clients with retainer info, saved rules, order volume
- Title companies, one-offs, government agencies

### Inspection Tab
- Active rules with accuracy rates
- Learned patterns with confidence scores
- Recent misses (post-ship rejections) → create new rules

### Payments Tab
- Agent payouts: pending, processing, paid
- Margin report: revenue vs agent cost by service type
- Export to VERTEX

### Analytics Tab
- Volume by service type (color-coded bars)
- Quality metrics: first-pass rate, rejection rate, correction time
- Revenue/margin breakdowns
- Agent utilization
- Geographic distribution

---

# 11. FIELD AGENT PORTAL

**Dashboard:** My Active Orders | My Upcoming | Action Required | My Performance

**Order View:**
- Order details, client rules, special instructions
- Download documents
- Accept/Decline assignment
- Mark complete
- Upload scanback
- View correction messages (specific page/location)

**My Profile:** Service area, availability, certifications (with expiration tracking), insurance, equipment, payment info

**My Payments:** Completed orders, fees, payment status, history

---

# 12. NEXUS INTEGRATIONS

```
NEXUS (Brain Hub)
├── GPSS — Find government opportunities → Won service contracts → PRISM
├── DDCSS — Sell Blueprints → Blueprint clients → PRISM client profiles
├── PRISM — Schedule, dispatch, execute, verify services
├── ATLAS — Complex engagements from PRISM → project tracking
├── VERTEX — PRISM verified orders → auto-invoice; agent payments → expenses
├── GBIS — Grant discovery
├── LBPC — Surplus recovery
└── COMPASS — Proposal quality assurance
```

---

# 13. PRICING & FEES

### Agent Fees (What DDI Pays)

| Service | Base Fee | Notes |
|---------|----------|-------|
| Notary — Standard | $75-$150 | Package size/location |
| Notary — Reverse mortgage | $125-$200 | More complex |
| Notary — General | $50-$100 | Per appointment |
| Notary (RON) | $25-$50 | Per session |
| Drug Test (Non-DOT) | $35-$60 | Per collection |
| Drug Test (DOT) | $50-$75 | Higher cert required |
| DNA Collection | $50-$75 | Per collection |
| Fingerprinting / EFT | TBD | Pricing TBD |
| Courier/Runner | $25-$65 | Distance-based |
| Apostille | $40-$60 | Per document |

### Travel Fees
| Zone | Distance | Fee |
|------|----------|-----|
| Zone 1 | 0-15 mi | $20 |
| Zone 2 | 15-30 mi | $40 |
| Zone 3 | 30-50 mi | $60 |
| Zone 4 | 50+ mi | $80+ |

### Surcharges
| Type | Fee |
|------|-----|
| After-Hours | +$50-$75 |
| Weekend | +$40-$50 |
| Holiday | +$75-$100 |
| Emergency (<2 hr) | +$75-$100 |

**DDI Margin:** Client pays retail/contract rate. Agent gets base fee. Spread = DDI margin. VERTEX tracks both sides.

---

# 14. NOTIFICATIONS

**Agent:** New order available, order assigned, confirmation reminder, scanback required, correction needed, payment sent, cert expiring

**Admin (Dee):** Order created, agent declined, scanback uploaded, errors detected, order verified, agent performance alert

**Client:** Service scheduled, service completed, results available, compliance report

---

# 15. SHIPPING & TRACKING

| Service | Where It Goes | Track With |
|---------|--------------|------------|
| Notary | Title company via FedEx/UPS | Shipping tracking # |
| Drug Test | Lab (Quest, LabCorp) | Lab accession # |
| DNA | Lab (DDC) | Chain of custody ID |
| Fingerprints / EFT | FBI, ATF, state agencies (LiveScan, EFT electronic, or ink mail) | TCN / EFT submission ID |

---

# 16. AIRTABLE SCHEMA

## 11 Tables (2 are shared NEXUS tables)

| # | Table | Purpose | Scope |
|---|-------|---------|-------|
| 1 | PRISM Orders | Every service order (central table) | PRISM only |
| 2 | **PRISM FIELD AGENTS** | Agent profiles, specialties, performance | **Shared — see `NEXUS_ONBOARDING_SYSTEM.md`** |
| 3 | **NEXUS COMPLIANCE DOCUMENTS** | W-9s, certs, insurance, NDA — all person types | **Shared — replaces PRISM Agent Certifications AND GPSS Subcontractor Compliance** |
| 4 | PRISM Clients | Client profiles with saved rules | PRISM only |
| 5 | PRISM Scanbacks | Uploaded document scans | PRISM only |
| 6 | PRISM Inspection Results | Inspection reports | PRISM only |
| 7 | PRISM Inspection Rules | Rule engine | PRISM only |
| 8 | PRISM Corrections | Error correction tracking | PRISM only |
| 9 | PRISM Agent Payments | Payment tracking | PRISM only |
| 10 | PRISM Service Types | Master service reference | PRISM only |
| 11 | PRISM Shipping/Tracking | Post-verification shipping/lab | PRISM only |

> **IMPORTANT:** Field Agent profiles and compliance documents are part of the unified **NEXUS Onboarding & Compliance System** — one pipeline for suppliers, subcontractors, and field agents. Full schema in `NEXUS_ONBOARDING_SYSTEM.md`.

### TABLE 1: PRISM ORDERS (48 fields)

| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | Order Number | Auto Number | PRISM-2026-XXXX |
| 2 | Order Type | Single Select | Notary, Notary (RON), Drug Test (DOT), Drug Test (Non-DOT), DNA Collection, Fingerprinting/EFT, Courier/Runner, Apostille, Background Check, Process Serving |
| 3 | Status | Single Select | New, Assigned, Confirmed, In Progress, Completed, Scanned Back, Under Review, Errors Found, Correction Requested, Re-scanned, Verified, Closed, Cancelled |
| 4 | Priority | Single Select | Standard, Rush, Emergency |
| 5 | Assigned Agent | Linked Record | → Field Agents |
| 6 | Client | Linked Record | → Clients |
| 7 | DDCSS Blueprint | Linked Record | → DDCSS Prospects |
| 8 | Signer/Subject Name | Short Text | |
| 9 | Signer/Subject Phone | Phone | |
| 10 | Signer/Subject Email | Email | |
| 11 | Appointment Date | Date | |
| 12 | Appointment Time | Short Text | |
| 13 | Appointment Address | Long Text | |
| 14 | City | Short Text | |
| 15 | State | Short Text | |
| 16 | ZIP | Short Text | |
| 17 | County | Short Text | Witness requirement lookup |
| 18 | Documents Attached | Attachment | Original docs for agent |
| 19 | Document Page Count | Number | Expected count |
| 20 | Client Rules | Long Text | Auto from profile |
| 21 | Special Instructions | Long Text | |
| 22 | Scanback Required | Checkbox | |
| 23 | Pen Color | Single Select | Blue, Black, No Preference |
| 24 | Paper Size | Single Select | Letter, Legal, Mixed |
| 25 | Copies Required | Number | |
| 26 | Witness Required | Checkbox | Auto by state |
| 27 | Witness Count | Number | |
| 28 | ID Copies Required | Checkbox | |
| 29 | Agent Fee | Currency | |
| 30 | Travel Fee | Currency | |
| 31 | Surcharges | Currency | |
| 32 | Total Agent Cost | Formula | Fee + Travel + Surcharges |
| 33 | Client Billing Amount | Currency | |
| 34 | DDI Margin | Formula | Billing - Cost |
| 35 | Scanback Files | Attachment | Completed scans |
| 36 | Scanback Upload Date | Date | |
| 37 | Inspection Status | Single Select | Pending, Clean, Errors Found, Corrected, Verified |
| 38 | Inspection Report | Linked Record | → Inspection Results |
| 39 | Shipping Tracking | Linked Record | → Shipping/Tracking |
| 40 | VERTEX Invoice | Linked Record | → VERTEX |
| 41 | Agent Confirmed Date | Date | |
| 42 | Appointment Confirmed | Date | |
| 43 | Completed Date | Date | |
| 44 | Verified Date | Date | |
| 45 | Closed Date | Date | |
| 46 | Notes | Long Text | |
| 47 | Created Date | Created Time | |
| 48 | Last Modified | Last Modified Time | |

### TABLE 2: PRISM FIELD AGENTS → See `NEXUS_ONBOARDING_SYSTEM.md`

28 fields. Part of the unified NEXUS onboarding pipeline. Key fields: Agent ID, name, contact, specialties, service area, onboarding status, compliance link, performance metrics, payment method.

**Onboarding Status:** `New → Docs Required → Under Review → Active → Suspended → Inactive`

No agent gets dispatched unless `ONBOARDING_STATUS = Active` and `COMPLIANCE_READY = TRUE`.

### TABLE 3: NEXUS COMPLIANCE DOCUMENTS → See `NEXUS_ONBOARDING_SYSTEM.md`

21 fields. Unified compliance table for ALL person types (suppliers, subcontractors, field agents). Replaces the old `GPSS SUBCONTRACTOR COMPLIANCE` table. Tracks W-9s, NDAs, insurance, certifications, background checks — everything. Auto-generates required doc checklists based on person type and specialties.

**Document Status:** `Missing → Submitted → Under Review → Approved / Rejected / Expired`

### TABLE 4: PRISM CLIENTS (33 fields)

Company info, client type (Blueprint tier / title co / retail), DDCSS link, contacts, default rules (scanback, pen color, paper, copies, ID, custom), shipping prefs, lab preference, retainer amount, contract dates, order stats, revenue.

### TABLE 5: PRISM SCANBACKS (15 fields)

Order link, agent link, files, page counts, attempt number, inspection link, status.

### TABLE 6: PRISM INSPECTION RESULTS (17 fields)

Order/scanback links, method (AI/human/both), result, error counts, error details, confidence score, human override, **outcome after ship** (for adaptive learning feedback loop).

### TABLE 7: PRISM INSPECTION RULES (17 fields)

Rule name, service type, document type, category, severity, detection method, source, accuracy rate, false positive rate, active flag.

### TABLE 8: PRISM CORRECTIONS (16 fields)

Order/agent/inspection links, error type, severity, page number, location, description, dates, resolution time, return trip tracking.

### TABLE 9: PRISM AGENT PAYMENTS (15 fields)

Agent/order links, fees breakdown, deductions, total, payment status/date/method/reference, VERTEX link.

### TABLE 10: PRISM SERVICE TYPES (17 fields)

Master reference: service name, category, required certs/equipment, default docs, rates, inspection rules link, chain of custody/lab/shipping flags.

### TABLE 11: PRISM SHIPPING/TRACKING (15 fields)

Order link, shipping type, tracking number, destination, dates, delivery confirmation, lab specimen ID, results tracking.

### Relationship Map
```
Clients ── Orders ── Field Agents
               │              │
          Scanbacks    Certifications
               │
        Inspections
               │
         Corrections

Orders → Agent Payments → VERTEX (expenses)
Orders → Shipping/Tracking
Orders → VERTEX Invoices (revenue)
```

### Key Automations
1. New Order → Notify qualified agents
2. Agent Assigned → Send order details
3. Scanback Uploaded → Trigger inspection
4. Errors Found → Notify agent
5. Order Verified → Create VERTEX invoice
6. Order Verified → Notify client
7. Cert Expiring → Alert agent (90/30 days)
8. Cert Expired → Auto-suspend agent
9. Order Closed → Update agent stats
10. DDCSS Blueprint Created → Create PRISM client

---

# 17. API ENDPOINTS

**Orders:** CRUD + assign, confirm, complete, close
**Scanbacks:** Upload, get, inspect, report
**Field Agents:** CRUD + orders, performance
**Clients:** List, orders, compliance
**Rules:** List, add, view learned patterns

---

# 18. BUILD PHASES

**Phase 1 — Core Orders:** Create, assign, track. Basic agent database. Agent portal (view, accept, complete). Manual scanback review.

**Phase 2 — Inspection Engine:** Scanback upload/storage. AI vision detection. Error classification. Automated error reports.

**Phase 3 — Agent Network:** Registration/onboarding. Cert tracking + expiration alerts. Matching algorithm. Performance scoring.

**Phase 4 — Adaptive Learning:** Feedback loop. Pattern recognition. Anomaly detection. Confidence scoring.

**Phase 5 — Integrations:** DDCSS → PRISM clients. PRISM → VERTEX invoicing. PRISM → ATLAS projects. Client portal. Shipping/lab tracking.

**Phase 6 — Scale:** Open platform (SaaS). Public agent recruitment. Multi-state. Advanced analytics.

---

# 19. SAVED NAMES FOR FUTURE USE

| Name | Meaning | Potential Use |
|------|---------|---------------|
| VECTOR | Vendor Execution, Compliance, Tracking & Order Routing | Future logistics system |
| SENTRY | Service Execution, Notarization & Testing Review System | Inspection engine name |
| ORBIT | Order Routing, Booking & Inspection Tracker | Dispatch component |
| RELAY | Resource Execution, Logistics, Assignment & Verification | Courier tracking |
| SENTINEL | Service Execution, Notary Tracking, Inspection, Network & Logistics | AI inspection layer |
| FORGE | Field Order, Routing & Document Verification Engine | Order engine |

---

# THE BOTTOM LINE

DDCSS sells the contract. PRISM delivers the service. VERTEX collects the money. ATLAS manages the project.

The document inspection engine — catching errors before agents leave — is the competitive moat. Nobody else has it. Snapdocs doesn't. ZigSig doesn't. SigningOrder doesn't. Drug testing companies don't.

Build the basics first. Adaptive learning comes later. But the foundation has to be rock solid.

**PRISM: See every detail. Miss nothing.**

---

*Master Document — February 13, 2026*
*This is the SINGLE SOURCE OF TRUTH for PRISM. All other PRISM docs are superseded by this file.*
