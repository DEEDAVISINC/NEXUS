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

## THREE PERSON TYPES

| Type | What They Do | Example | System |
|------|-------------|---------|--------|
| **Supplier** | Sells us products/materials | Grainger, Zoro, local distributors | GPSS |
| **Subcontractor** | Performs services under DDI contract | Landscaping crew, HVAC company, janitorial | GPSS |
| **Field Agent** | Performs mobile field services for DDI | Notary signing agent, drug test collector, fingerprint tech | PRISM |

**Key insight:** A subcontractor and a field agent are both doing work *for* DDI. The difference is that field agents are dispatched through PRISM (individual mobile assignments), while subcontractors are scoped through GPSS (project-based contracts). Suppliers just sell us stuff.

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
