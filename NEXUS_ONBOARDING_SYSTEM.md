# NEXUS ONBOARDING & COMPLIANCE SYSTEM
## One Pipeline for Everyone Who Works for DDI

**Created:** February 14, 2026
**Owner:** Dee Davis Inc.
**Status:** ARCHITECTURE — Ready for Build
**Replaces:** `GPSS SUBCONTRACTOR COMPLIANCE` (expanded to cover all person types)

---

## THE RULE

**Anyone who works for DDI — supplier, subcontractor, or field agent — goes through the same pipeline:**

```
INTAKE → DOCS REQUIRED → COLLECTION → VERIFICATION → ACTIVE → WORK → PAY
```

The documents change based on who they are. The flow doesn't.

---

## FOUR PERSON TYPES

| Type | What They Do | Example | System |
|------|-------------|---------|--------|
| **Supplier** | Sells us products/materials | Grainger, Zoro, local distributors | GPSS |
| **Subcontractor** | Performs services under DDI contract | Landscaping crew, HVAC company, janitorial | GPSS |
| **Field Agent** | Performs mobile field services for DDI | Notary signing agent, drug test collector, fingerprint tech | PRISM |
| **Employee/Contractor (Internal)** | Works inside DDI's own operation, not dispatched to a client site | NEMT coordinator, HAVEN/SHIELD navigator, corporate admin | **HR** |

**Key insight:** A subcontractor and a field agent are both doing work *for* DDI, external to the company. Employees and internal 1099 contractors work *inside* DDI's operation — they run the divisions (DEPOINTE, HAVEN, SHIELD, VITAL, ARENA/PRIME, 3D Ink/CNTDA, Freight 1st Direct, DEPOINTE DNA, Corporate/HR/Admin) that dispatch field agents and manage subs. Suppliers just sell us stuff.

**Do not confuse internal HR onboarding with PRISM/GPSS onboarding.** A NEMT coordinator hired to run DEPOINTE's dispatch desk goes through **HR** (this section). A driver dispatched to actually run a trip goes through **PRISM Field Agents**. Different compliance spine, different system, same "no work until compliant" principle.

---

## THE 4TH TRACK — HR (EMPLOYEE & CONTRACTOR ONBOARDING)

**System:** `HR` (ViewType `'hr'` in the frontend) — separate from GPSS/PRISM because the compliance requirements are fundamentally different:

| Requirement | Suppliers/Subs/Field Agents (GPSS/PRISM) | Employees/Internal Contractors (HR) |
|---|---|---|
| Identity verification | W-9, business license, SAM.gov | **Form I-9 + E-Verify** (employees only — not contractors) |
| Government screening | SAM.gov exclusion (suppliers/subs) | **OIG LEIE + GSA SAM.gov exclusion — at hire AND monthly** |
| Required training | Service-specific certs (DOT collector, notary, LiveScan) | **CMS FDR training curriculum** (FWA/General Compliance within 90 days + annual, HIPAA, PII, Recipient Rights, Code of Conduct, etc.) |
| Why it exists | Protect the contract, protect the client relationship | **DDI is a First Tier, Downstream, and Related (FDR) entity under 42 CFR 422.504(d)** because DDI performs work under MCO/Medicaid contracts (CareSource, HIDE SNP — see `CLIENT OUTREACH/MICHIGAN MICH HIDE SNP/`). CMS requires health plans to flow these training/screening obligations down to every entity — including DDI's own internal staff — that touches that work. |

**Two worker sub-types inside HR, each with its own phase checklist (not the same as employee vs field agent):**
- **Employee (W-2):** Pre-Boarding → Day 1 → Week 1 → 30 Days (incl. 30-Day Check-In Agenda sub-checklist) → 60/90-Day Check-ins. Includes I-9/E-Verify.
- **Contractor (1099, internal/office role):** Pre-Engagement → Engagement Start → Ongoing → Renewal/Extension/Termination. No I-9/E-Verify (worker-classification risk — hard-excluded from the training catalog). Check-ins reference contract deliverables, not calendar-based performance reviews.

**This is a live automation of two source SOPs** — the DDI New Hire Onboarding SOP and the DDI Independent Contractor Onboarding SOP — not a generic tracker. `hr_onboarding_api.py` encodes:

- **10-item training catalog with real per-item recurrence:** refresher every 2 years (PII, Cultural Competence, Anti-Harassment), annual refresher (HIPAA), **annual reassigned at 11 months, not 12** (General Compliance/FWA, Medicare Fraud & Abuse, Code of Conduct/COI re-attestation), annual **only if the record is marked member-facing** (Recipient Rights, Abuse & Neglect), one-time employees-only (E-Verify/I-9 — contractors are hard-excluded).
- **Two-tier training deadline:** every item has a 30-day DDI internal target; General Compliance/FWA and Medicare Fraud & Abuse additionally carry a 90-day CMS regulatory hard floor. Missing the 30-day target is a `warning`; missing the 90-day floor is a `critical` compliance event that **blocks the `can-work` gate**.
- **Contractor training is scoped, not blanket-assigned** — each item carries an `applicable: yes/no/pending` tri-state the Engagement Manager sets per engagement, matching the contractor SOP's trigger table (e.g. HIPAA only if the scope involves PHI).
- **Monthly OIG LEIE + GSA SAM.gov exclusion screening cadence**, computed from the last logged screening date (`add_months` helper) — not a flat 30-day window. Never-screened and overdue-monthly-rescreen both block `can-work`.
- **Annual FDR Compliance Attestation** (SOP Section 6) — a separate Airtable table (`NEXUS HR FDR ATTESTATION`), calendar-year cycle, independent of individual hire dates. Surfaced on the HR dashboard and in `/alerts`.
- **Worker-classification documentation** (contractor track, SOP Section 10.1 / contractor SOP Section 8) — bounded scope, own tools/schedule, other clients, no supervisory integration, deliverable-based pay, plus a "routed to counsel" flag for genuinely unclear cases. Documentation, not legal advice.

**Backend:** `hr_onboarding_api.py` (Flask blueprint `hr_onboarding`), Airtable tables `NEXUS HR ONBOARDING` + `NEXUS HR FDR ATTESTATION` (primary) with automatic local-JSON fallback (`uploads/hr_onboarding/roster.json` + `fdr_attestation.json`) if Airtable isn't set up yet — same fallback pattern as `prism_compliance_api.py`. Writes use `typecast=True` so new single-select values (real DDI divisions, worker types) are accepted without a manual Airtable schema edit.

**Retention rule:** Records are **never hard-deleted**. "Archive" sets `STATUS = Archived` and keeps the full checklist/training/screening/audit history — required by the 10-year CMS FDR retention standard (42 CFR 422.504(d)). The audit log is server-side and append-only (every checklist toggle, training update, screening entry, classification edit, and agenda update writes an audit row automatically — this isn't just client-side decoration).

**Compliance gate:** `GET /nexus/hr/onboarding/<id>/can-work` mirrors PRISM's field-agent `can-work` check — returns `false` until the first onboarding phase is fully checked off, exclusion screening is current (not never-screened, not overdue on the monthly cadence, no open flagged match), and neither CMS-hard-floor training item (General Compliance/FWA, Medicare Fraud & Abuse) has missed its 90-day deadline. **Any system assigning an internal person to MCO/HIDE SNP-facing work (SHIELD, HAVEN, DDCSS) should check this gate first**, the same way PRISM checks `can-work` before dispatching a field agent.

**Frontend:** `nexus-frontend/src/components/systems/HRSystem.tsx` — Dashboard (compliance alerts + annual attestation panel), Roster (add/list/archive), Detail (phase checklist incl. 30-day agenda + worker classification form for contractors, training table with recurrence/compliance badges, exclusion screening log with computed cadence banner, append-only audit log, CSV export). Tile lives in the NEXUS landing page under Support Systems.

**System connections (see also `NEXUS_SYSTEM_INTEGRATION_MAP.md`):**
- **COMPASS** — HR is the source of CMS FDR audit evidence (training completion + exclusion screening) that COMPASS surfaces when a buyer/MCO requests FDR compliance proof for a contract.
- **VERTEX** — Active W-2 employees represent internal labor cost/overhead; VERTEX's expense/P&L views should be able to see HR's active headcount by division.
- **SHIELD / HAVEN / DDCSS** — Before assigning internal staff to MCO-facing casework, check `can-work` first.

---

## UNIFIED ONBOARDING FLOW

### The Pipeline (Same for Everyone)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   INTAKE     │ →  │ DOCS         │ →  │ COLLECTION   │ →  │ VERIFICATION │ →  │   ACTIVE     │ →  │   WORKING    │
│              │    │ REQUIRED     │    │              │    │              │    │              │    │              │
│ Person added │    │ System auto- │    │ Person       │    │ DDI reviews  │    │ All docs     │    │ Gets orders/ │
│ to Airtable  │    │ creates doc  │    │ uploads docs │    │ each doc     │    │ approved     │    │ RFQs/scopes  │
│ via portal   │    │ checklist    │    │ via portal   │    │ approve/     │    │ Compliance   │    │ Assigned     │
│ or manual    │    │ based on     │    │ or email     │    │ reject       │    │ Ready = TRUE │    │ work through │
│ entry        │    │ person type  │    │              │    │              │    │              │    │ PRISM/GPSS   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Onboarding Status Field (On Every Person Record)

| Status | Meaning | What Happens |
|--------|---------|-------------|
| `New` | Just entered the system | Compliance checklist gets auto-created |
| `Docs Required` | Checklist created, waiting on documents | Person gets email/portal notification |
| `Under Review` | All docs submitted, DDI reviewing | Dee or team verifies each document |
| `Active` | All docs approved, ready to work | Appears in dispatch/RFQ pools |
| `Suspended` | Doc expired or issue found | Blocked from new work until resolved |
| `Inactive` | No longer working with DDI | Archived, not in active pools |

**Rule:** No one gets work until `ONBOARDING_STATUS = Active`. Period.

---

## REQUIRED DOCUMENTS BY PERSON TYPE

### Supplier (Product Vendors)

| Document | Required? | Expires? | Notes |
|----------|-----------|----------|-------|
| W-9 | **YES** | No | Need before first payment |
| NDA | If sensitive | No | For government/classified products |
| Tax Exempt Certificate | If applicable | Yes (annual) | For tax-exempt government orders |
| Vendor Agreement | **YES** | No | Terms of business |

### Subcontractor (Service Providers)

| Document | Required? | Expires? | Notes |
|----------|-----------|----------|-------|
| W-9 | **YES** | No | Need before first payment |
| NDA / Confidentiality Agreement | **YES** | No | Always — protects client info |
| Subcontractor Agreement | **YES** | No | Signed terms, scope, rates |
| General Liability Insurance | **YES** | Yes (annual) | $1M minimum per occurrence |
| Workers Compensation Insurance | If has employees | Yes (annual) | Statutory limits |
| Professional Liability Insurance | If professional services | Yes (annual) | $1M minimum |
| Performance Bond | If contract >$100K | Per contract | Required by buyer |
| Payment Bond | If contract >$100K | Per contract | Required by buyer |
| Background Check | If sensitive work | Yes (annual) | Government/cleared work |
| Security Clearance | If required | Yes | Federal cleared work |
| Industry Certifications | As applicable | Varies | Contractor license, DBE cert, etc. |

### Field Agent (PRISM Mobile Services)

| Document | Required? | Expires? | Notes |
|----------|-----------|----------|-------|
| W-9 | **YES** | No | Independent contractor — need before first payment |
| NDA / Confidentiality Agreement | **YES** | No | Signer info, document contents are confidential |
| Independent Contractor Agreement | **YES** | No | Not an employee — this is critical |
| Background Check | **YES** | Yes (annual) | Required for all field agents — non-negotiable |
| E&O Insurance | **YES** (notary) | Yes (annual) | Errors & Omissions — protects against signing errors |
| Notary Commission | If notary | Yes (4-6 yr) | State-issued, commission number + expiration |
| NNA Certification | If signing agent | Yes (annual) | National Notary Association certified signing agent |
| DOT Collector Certification | If drug test | Yes (annual) | 49 CFR Part 40 certified collector |
| LiveScan / EFT Certification | If fingerprint | Yes (varies) | Electronic fingerprint authorization |
| FCRA Certification | If background check | Yes (annual) | Fair Credit Reporting Act certified |
| Vehicle Insurance | If mobile | Yes (annual) | Proof of reliable transportation |
| Photo ID | **YES** | Yes | Government-issued ID on file |

---

## AIRTABLE SCHEMA

### Table: `NEXUS COMPLIANCE DOCUMENTS`

**Replaces:** `GPSS SUBCONTRACTOR COMPLIANCE`
**Connects to:** `GPSS SUPPLIERS`, `GPSS SUBCONTRACTORS`, `PRISM FIELD AGENTS`

| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | COMPLIANCE_ID | Auto-number | Primary field |
| 2 | PERSON_TYPE | Single Select | `Supplier`, `Subcontractor`, `Field Agent` |
| 3 | SUPPLIER | Link | Link to `GPSS SUPPLIERS` (if Supplier) |
| 4 | SUBCONTRACTOR | Link | Link to `GPSS SUBCONTRACTORS` (if Subcontractor) |
| 5 | FIELD_AGENT | Link | Link to `PRISM FIELD AGENTS` (if Field Agent) |
| 6 | PERSON_NAME | Formula | Pulls name from whichever linked record exists |
| 7 | DOCUMENT_TYPE | Single Select | See Document Types below |
| 8 | DOCUMENT_STATUS | Single Select | `Missing`, `Submitted`, `Under Review`, `Approved`, `Expired`, `Rejected` |
| 9 | DATE_RECEIVED | Date | When document was received |
| 10 | DATE_APPROVED | Date | When DDI approved it |
| 11 | EXPIRATION_DATE | Date | When it expires (blank if never) |
| 12 | DAYS_UNTIL_EXPIRATION | Formula | `IF({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days'), "No Expiration")` |
| 13 | ALERT_STATUS | Formula | See formula below |
| 14 | DOCUMENT_FILE | Attachment | PDF/image upload |
| 15 | INSURANCE_AMOUNT | Currency | Coverage amount (insurance docs only) |
| 16 | POLICY_NUMBER | Single line text | Policy/document reference number |
| 17 | COMMISSION_NUMBER | Single line text | Notary commission number (notary docs only) |
| 18 | COMMISSIONING_STATE | Single line text | State of commission (notary docs only) |
| 19 | NOTES | Long text | Additional info |
| 20 | UPLOADED_BY | Single Select | `DDI Admin`, `Portal Upload`, `Email` |
| 21 | CREATED | Created time | Auto timestamp |

**ALERT_STATUS Formula:**
```
IF(
  AND({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days') < 0),
  "EXPIRED",
  IF(
    AND({EXPIRATION_DATE}, DATETIME_DIFF({EXPIRATION_DATE}, TODAY(), 'days') <= 30),
    "EXPIRING SOON",
    IF(
      {DOCUMENT_STATUS} = "Approved",
      "CURRENT",
      {DOCUMENT_STATUS}
    )
  )
)
```

**Document Types (Single Select Options):**
```
── Universal ──
W-9
NDA / Confidentiality Agreement
Photo ID

── Agreements ──
Vendor Agreement
Subcontractor Agreement
Independent Contractor Agreement

── Insurance ──
General Liability Insurance
Professional Liability Insurance
Workers Compensation Insurance
E&O Insurance (Errors & Omissions)
Vehicle Insurance

── Bonds ──
Performance Bond
Payment Bond

── Certifications ──
Notary Commission
NNA Signing Agent Certification
DOT Collector Certification (49 CFR Part 40)
LiveScan / EFT Certification
FCRA Certification
Security Clearance
Background Check
Tax Exempt Certificate

── Industry ──
Contractor License
DBE/MBE/WBE Certification
Other Certification
```

---

### Table: `PRISM FIELD AGENTS`

**New table — agents dispatched through PRISM**

| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | AGENT_ID | Auto-number | FA-0001, FA-0002... |
| 2 | FIRST_NAME | Single line text | |
| 3 | LAST_NAME | Single line text | |
| 4 | EMAIL | Email | |
| 5 | PHONE | Phone | |
| 6 | ADDRESS | Single line text | |
| 7 | CITY | Single line text | |
| 8 | STATE | Single line text | |
| 9 | ZIP | Single line text | |
| 10 | SPECIALTIES | Multiple Select | `Signing Agent`, `RON Notary`, `DOT Collector`, `Non-DOT Collector`, `DNA Collector`, `Fingerprint/EFT Tech`, `Courier/Runner`, `Background Check Specialist`, `Process Server` |
| 11 | SERVICE_RADIUS | Number | Miles from home base |
| 12 | SERVICE_ZIPS | Long text | Additional ZIP codes served |
| 13 | YEARS_EXPERIENCE | Number | |
| 14 | HAS_VEHICLE | Checkbox | |
| 15 | ONBOARDING_STATUS | Single Select | `New`, `Docs Required`, `Under Review`, `Active`, `Suspended`, `Inactive` |
| 16 | COMPLIANCE_DOCUMENTS | Link | Link to `NEXUS COMPLIANCE DOCUMENTS` |
| 17 | COMPLIANCE_READY | Checkbox | TRUE = all required docs approved |
| 18 | RATING | Number (1-5) | Performance rating |
| 19 | COMPLETION_RATE | Percent | % of orders completed |
| 20 | ON_TIME_RATE | Percent | % of orders on time |
| 21 | ERROR_RATE | Percent | % of scanbacks with errors |
| 22 | ORDERS_COMPLETED | Number | Lifetime total |
| 23 | TOTAL_EARNED | Currency | Lifetime earnings |
| 24 | DATE_JOINED | Date | When they became active |
| 25 | LAST_ACTIVE | Date | Last completed order |
| 26 | PAYMENT_METHOD | Single Select | `Direct Deposit`, `Check`, `Zelle` |
| 27 | NOTES | Long text | |
| 28 | CREATED | Created time | |

---

### Updates to Existing Tables

**Add to `GPSS SUPPLIERS`:**

| Field | Type | Notes |
|-------|------|-------|
| ONBOARDING_STATUS | Single Select | `New`, `Docs Required`, `Under Review`, `Active`, `Suspended`, `Inactive` |
| COMPLIANCE_DOCUMENTS | Link | Link to `NEXUS COMPLIANCE DOCUMENTS` |
| COMPLIANCE_READY | Checkbox | TRUE = all required docs approved |

**Add to `GPSS SUBCONTRACTORS`:**

| Field | Type | Notes |
|-------|------|-------|
| ONBOARDING_STATUS | Single Select | `New`, `Docs Required`, `Under Review`, `Active`, `Suspended`, `Inactive` |

*(Already has COMPLIANCE_DOCUMENTS link and COMPLIANCE_READY — just rename the link target from `GPSS SUBCONTRACTOR COMPLIANCE` to `NEXUS COMPLIANCE DOCUMENTS`)*

---

## VIEWS (NEXUS COMPLIANCE DOCUMENTS)

### Priority Views:

| View | Filter | Purpose |
|------|--------|---------|
| **EXPIRED** | ALERT_STATUS = "EXPIRED" | Urgent — fix now |
| **Expiring Soon (30 days)** | ALERT_STATUS = "EXPIRING SOON" | Proactive renewals |
| **Missing Documents** | DOCUMENT_STATUS = "Missing" | Onboarding blockers |
| **Under Review** | DOCUMENT_STATUS = "Under Review" | Dee's review queue |
| **By Person** | Group by PERSON_NAME | See all docs per person |
| **By Person Type** | Group by PERSON_TYPE | Suppliers vs Subs vs Agents |
| **By Document Type** | Group by DOCUMENT_TYPE | All W-9s, all insurance, etc. |
| **Fully Compliant** | DOCUMENT_STATUS = "Approved" AND (no expiration OR >30 days) | Green across the board |

### Person-Specific Views:

| View | Filter | Purpose |
|------|--------|---------|
| **Supplier Compliance** | PERSON_TYPE = "Supplier" | All supplier docs |
| **Subcontractor Compliance** | PERSON_TYPE = "Subcontractor" | All sub docs |
| **Field Agent Compliance** | PERSON_TYPE = "Field Agent" | All agent docs |

---

## AUTO-GENERATION RULES

**When a new person is created, the system auto-creates compliance records based on type:**

### New Supplier → Auto-create:
```
- W-9 (status: Missing)
- Vendor Agreement (status: Missing)
```

### New Subcontractor → Auto-create:
```
- W-9 (status: Missing)
- NDA / Confidentiality Agreement (status: Missing)
- Subcontractor Agreement (status: Missing)
- General Liability Insurance (status: Missing)
```

### New Field Agent → Auto-create based on specialties:

**All agents get:**
```
- W-9 (status: Missing)
- NDA / Confidentiality Agreement (status: Missing)
- Independent Contractor Agreement (status: Missing)
- Background Check (status: Missing)
- Photo ID (status: Missing)
```

**If specialty includes Signing Agent or RON Notary, also add:**
```
- Notary Commission (status: Missing)
- NNA Signing Agent Certification (status: Missing)
- E&O Insurance (status: Missing)
```

**If specialty includes DOT Collector, also add:**
```
- DOT Collector Certification (status: Missing)
```

**If specialty includes Fingerprint/EFT Tech, also add:**
```
- LiveScan / EFT Certification (status: Missing)
```

**If specialty includes Background Check Specialist, also add:**
```
- FCRA Certification (status: Missing)
```

**If agent has vehicle, also add:**
```
- Vehicle Insurance (status: Missing)
```

---

## PORTAL INTEGRATION

### What the Portal Shows (Field Agents & Subcontractors)

**Profile → Compliance Tab:**
```
┌──────────────────────────────────────────────┐
│  My Documents                    3/7 Complete │
│  ─────────────────────────────────────────── │
│  ✅ W-9                          Approved     │
│  ✅ NDA                          Approved     │
│  ✅ Background Check             Approved     │
│  ⏰ E&O Insurance               Expiring 3/15│
│  ❌ Notary Commission           Missing       │  [Upload]
│  ❌ NNA Certification           Missing       │  [Upload]
│  🔄 IC Agreement                Under Review  │
│  ─────────────────────────────────────────── │
│  ⚠️ Upload missing docs to start receiving   │
│     orders.                                   │
└──────────────────────────────────────────────┘
```

**Upload Flow:**
1. Agent clicks [Upload] on a missing document
2. Selects file (PDF, JPEG, PNG)
3. File uploads to `DOCUMENT_FILE` in Airtable
4. `DOCUMENT_STATUS` changes to `Submitted`
5. DDI gets notification: "New document uploaded — review needed"
6. DDI reviews → Approves or Rejects
7. Agent gets notification of result
8. When all required docs approved → `ONBOARDING_STATUS = Active`

### What DDI Sees (Admin Dashboard)

**NEXUS Dashboard → Compliance Widget:**
```
┌──────────────────────────────────────────────┐
│  COMPLIANCE OVERVIEW                          │
│  ─────────────────────────────────────────── │
│  🟢 Active:     24 people (fully compliant)   │
│  🟡 Onboarding: 6 people (docs needed)        │
│  🔴 Expired:    3 documents (action needed)    │
│  ⏰ Expiring:   5 docs in next 30 days        │
│                                               │
│  [View All]  [Expiring Soon]  [Missing Docs]  │
└──────────────────────────────────────────────┘
```

---

## API ENDPOINTS

### Unified Compliance API

```
── Read ──
GET  /nexus/compliance/{person_type}/{person_id}
     Get all compliance docs for a person

GET  /nexus/compliance/alerts
     Get all expired + expiring documents

GET  /nexus/compliance/onboarding
     Get all people in onboarding (not yet Active)

── Write ──
POST /nexus/compliance/{person_type}/{person_id}/generate
     Auto-create required doc checklist for new person

POST /nexus/compliance/{doc_id}/upload
     Upload document file (from portal)

PUT  /nexus/compliance/{doc_id}/review
     Approve or reject a document (DDI admin)

── Checks ──
GET  /nexus/compliance/{person_type}/{person_id}/check
     Returns: { compliant: true/false, missing: [], expired: [] }

GET  /nexus/compliance/{person_type}/{person_id}/can-work
     Returns: true/false — is this person cleared to receive work?
```

### Integration Points

| System | How It Uses Compliance |
|--------|----------------------|
| **PRISM** | Before dispatching order → check `can-work`. If false, skip agent. |
| **GPSS** | Before sending RFQ → check `can-work`. If false, flag warning. |
| **VERTEX** | Before issuing payment → check W-9 on file. If missing, hold payment. |
| **Portal** | Shows compliance status, allows document upload |

---

## NOTIFICATION SYSTEM

### Auto-Notifications:

| Trigger | Who Gets It | Message |
|---------|-------------|---------|
| New person created | DDI Admin | "[Name] added — compliance checklist created" |
| Document uploaded | DDI Admin | "[Name] uploaded [Doc Type] — review needed" |
| Document approved | Person (agent/sub) | "Your [Doc Type] has been approved" |
| Document rejected | Person | "Your [Doc Type] was rejected — [reason]. Please re-upload." |
| 30 days before expiration | Person + DDI | "[Doc Type] expires on [date] — please renew" |
| Document expired | Person + DDI | "[Doc Type] has EXPIRED — [Name] suspended from new work" |
| All docs approved | Person + DDI | "Congratulations! You're now active and can receive work." |

### Auto-Actions:

| Trigger | What Happens |
|---------|-------------|
| All required docs approved | `ONBOARDING_STATUS → Active`, `COMPLIANCE_READY → TRUE` |
| Any doc expires | `ONBOARDING_STATUS → Suspended`, `COMPLIANCE_READY → FALSE` |
| Expired doc renewed + approved | `ONBOARDING_STATUS → Active`, `COMPLIANCE_READY → TRUE` |

---

## MIGRATION PLAN

### From Current State to Unified System:

**Step 1: Create `NEXUS COMPLIANCE DOCUMENTS` table**
- Copy structure from existing `GPSS SUBCONTRACTOR COMPLIANCE`
- Add new fields: `PERSON_TYPE`, `SUPPLIER`, `FIELD_AGENT`, `COMMISSION_NUMBER`, `COMMISSIONING_STATE`, `UPLOADED_BY`
- Add new document types to `DOCUMENT_TYPE` single select

**Step 2: Migrate existing data**
- Copy all records from `GPSS SUBCONTRACTOR COMPLIANCE` into new table
- Set `PERSON_TYPE = Subcontractor` for all migrated records
- Re-link `SUBCONTRACTOR` field

**Step 3: Create `PRISM FIELD AGENTS` table**
- Build table with 28 fields as specified above
- Link `COMPLIANCE_DOCUMENTS` to `NEXUS COMPLIANCE DOCUMENTS`

**Step 4: Update existing tables**
- Add `ONBOARDING_STATUS` and `COMPLIANCE_DOCUMENTS` link to `GPSS SUPPLIERS`
- Update `GPSS SUBCONTRACTORS` link to point to new compliance table
- Add `ONBOARDING_STATUS` to `GPSS SUBCONTRACTORS`

**Step 5: Create views**
- Build all views listed above in `NEXUS COMPLIANCE DOCUMENTS`
- Add "Compliance Ready" views to all person tables

**Step 6: Retire old table**
- Once verified, archive `GPSS SUBCONTRACTOR COMPLIANCE`
- Update all API endpoints to use new table

---

## SUMMARY

| Before | After |
|--------|-------|
| Compliance only for subcontractors | Compliance for everyone |
| Manual doc checklist creation | Auto-generated based on person type |
| No portal upload | Portal upload with auto-notification |
| No supplier compliance tracking | Suppliers tracked too |
| Field agents disconnected | Field agents in same pipeline |
| Separate flows per person type | One flow, different doc requirements |
| Manual status tracking | Auto status changes based on doc state |
| No work gating | Can't get work without compliance |

**One pipeline. One compliance table. One portal. Three person types. Zero excuses for missing documents.**

---

*Last updated: February 14, 2026*
