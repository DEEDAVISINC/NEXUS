# NEXUS SYSTEM CORRECTIONS & CLARIFICATIONS

**Fixing system boundaries and manual usability.**

---

## CORRECTION 0e: STALE BID CALENDAR / ALERT SPAM (Jul 27, 2026)

**Problem:** `calendars/` held **6,000+** past BID DEADLINE `.ics` files; `deadline_alerts.json` held **24,000+** EXPIRED rows. Dashboard + Apple Calendar feed kept showing the same dead opportunities. Hourly calendar automation was also **rewriting DTSTAMP** on past files.

**Fix:**
1. Run `python3 cleanup_stale_nexus_deadlines.py --apply` (archives past auto-bid ICS → `calendars/ARCHIVE_EXPIRED/`, prunes expired alerts)
2. `calendar_automation.py` skips past deadlines; does not regenerate them
3. `nexus_autonomous.py` deadline watch **omits EXPIRED** from `deadline_alerts.json` (grace learning only ≤14 days)
4. `/calendar/feed.ics` and `/calendar/events` skip ARCHIVE + past bid events

**Do not** re-import `ARCHIVE_EXPIRED` into Apple Calendar. Refresh the live NEXUS feed after cleanup.

---

## CORRECTION 0d: MOLINA = NMT/NEMT **AND** CTS (Jul 2026)

**Molina Healthcare of Michigan** (HIDE SNP LTSS PSA) is **not** a single NEMT queue.

| Lane | Code | Meaning |
|------|------|---------|
| NMT / NEMT | `MOLN` Ⓜ️ | Transportation / trip dispatch |
| **CTS** | `CTS` 🏠 | Community Transition Services (Attachment B / T2038) — NF-to-home case management; **separate PRISM lifecycle** |

OPS: GATEWAY Molina assignment opens **MOLN + CTS**. CTS-only stays CTS-scoped. Never describe Molina work as NEMT-only.

---

## CORRECTION 0c: PHONE ON EMAIL vs WEB — NOT THE SAME RULE (Jun 2026)

**248.376.4550** = **President & CEO personal cell** (Dieasha D. Davis). Stays on email signatures and business documents — **do not change Dee's signature number.**

**248.376.4550 is NOT forwarded to Twilio** — personal line only. Member/public call path = **855** (+ GV **248.270** → **855**).

**248.376.4550 must NOT appear on websites** — portal.deedavis.biz, deedavis.biz, CWC proof HTML, any public web page.

| Channel | Number |
|---------|--------|
| **Email / PDF / CO correspondence** | **248.376.4550** (CEO personal) |
| **Websites (all public HTML)** | **855.773.0035** — never 248.376.4550 |
| **Google Voice 248.270.8490** | Forward to **+1 855-773-0035** (Twilio) |
| **Twilio** | **855-773-0035** — PRISM voice webhooks |

Setup: `deploy/PHONE_ROUTING_TWILIO.md`

NEXUS: grep generated **HTML/website** output for `248.376` before publish. Email and Word/PDF outbound still use **248.376.4550** per `COMPANY_INFO_MASTER.md`.

---

## CORRECTION 0b: HAVEN ≠ HAP POPULATION (AUTHORITATIVE — Jun 2026)

**HAVEN** = MOB-B disaster/displacement continuity for **displaced plan members** — national program (hurricane-prone states, FEMA/state EM, MCO disaster riders). **Not** a Michigan-specific program. **Not** the HAP CareSource enrolled member pool.

**HAP CareSource NEMT** = MOB-A — ~4,500 dual-eligible members, Wayne + Macomb, Vendor 100000469269. That is **live plan NEMT proof for DDI as TPA**, not HAVEN's defined end population.

**Do not** put HAP member counts, Wayne/Macomb geography, or "HAP baseline" on HAVEN program definition cards, population tables, or grant copy. HAP may appear under **operational proof** or **entity routing** (live MCO contract) — separate from HAVEN population lane.

### Cross-document rule (funder + MCO copy)

| Lane | Definition | Use in copy |
|------|------------|-------------|
| **MOB-A** | HAP NEMT daily medical trips — live contract proof for DDI as MCO TPA operator | **DDI credentialing proof only** — Vendor 100000469269 · CHAMPS 6309049 · Wayne + Macomb |
| **MOB-B** | HAVEN displacement continuity — national program; activates when housing or disaster breaks care | **HAVEN population** = displaced plan members — not HAP enrollees |

**Never** put HAP member counts on HAVEN population figures. **Never** merge MOB-A and MOB-B in any funder or MCO copy.

### VITAL buyer split (Jun 2026)

| Track | Use for | Never send to |
|-------|---------|---------------|
| **VITAL-HS** | Health system hospital courier consolidation (`VITAL_Master_Proposal.html`) | MCO evaluators, grant funders, MDHHS |
| **VITAL-MCO** | Homebound MICH dual-eligible lab/Rx/DME (`THREE_PROGRAM_PITCH_PACKAGE`) | N/A — default for all funder/MCO outreach |

Do not mix hospital $950K savings model with MCO pitch. See `NEXUS_LEARNING/DDI_SERVICE_POPULATION_LANES.md`.

### Logo consistency (unified stack)

SHIELD = blue · HAVEN = gold/amber · VITAL = teal — **single program color per lettermark**. No rainbow per-letter lettermarks on standalone documents.

### WBENC badge (May 2026 lapse)

Remove WBENC or note: **WBE recertification in progress — Great Lakes WBC** on HAVEN, VITAL, SHIELD materials, and unified pitch.

**Source:** Dee correction Jun 2026 · `HAVEN/STRATEGY/HAVEN_DISASTER_RECOVERY_TPA_STRATEGY.md` (HAP = credibility for pitches, not HAVEN geography).

### SHIELD revenue tiering (Jun 2026 — authoritative)

**Source:** `SHIELD_PROGRAM_COMPLETE_FRAMEWORK.md` · `SHIELD_REVENUE_MODEL.md` · `LEAD_TESTING_STRATEGY.md`

| Tier | Figure | Meaning |
|------|--------|---------|
| **Y1 Wayne pilot** | **$612,770–$1,165,480** | 1,500–2,000 screening referrals dispatched · 50% capture model |
| **Wayne full scale** | **~$6.1M** | 50% mandatory-test capture (~19,730 tests/yr) |
| **Four-county Y1** | **~$13.8M** | Wayne + Oakland + Macomb + Genesee at scale (model) |
| **3-year lifetime** | **~$41.5M** | Four counties · stacked SHIELD billing (model) |

**Do not** cite $6.1M as Year 1 pilot revenue. **Retired:** "25 families" pilot sizing and $125–$200 all-in mobile rates (below market — use $175–$350/person per `LEAD_TESTING_STRATEGY.md`).

**SHIELD population:** All children under 4 in Michigan (MCL 333.5474d) — Wayne pilot first. Not limited to elevated-BLL cases at intake.

**SHIELD billing:** CHW codes **98960, 98961, 98962** through CHAMPS **6309049** — DDI bills MCOs and Medicaid FFS directly, not MDHHS.

---

## CORRECTION 0: SWFT / DCSA — DDI vs LAKOTA (AUTHORITATIVE)

**Source of truth:** `COMPANY_INFO_MASTER.md` (Federal/Compliance section) · `PARTNERSHIPS/LAKOTA_SOFTWARE_PARTNERSHIP_SUMMARY.md`

### DDI — DO NOT CLAIM SWFT

- **~~SWFT Authorized~~** is **incorrect for Dee Davis Inc.** on marketing, signatures, capability statements, emails, and code defaults.
- **DDI's SWFT access was denied by DCSA (March 2026).** DCSA indicated requirements including **minimum interim Secret clearance** and **Facility Clearance Level (FCL)** for that path.
- **Do not** list “SWFT Authorized,” “SWFT-approved,” or “DCSA SWFT-authorized” **on DDI outbound documents**.

### Lakota — SWFT ACTIVE (partner)

- **Lakota Software IS SWFT-authorized** — Lakota can submit to DCSA SWFT.
- **Internal / ops docs:** “Lakota/SWFT (active)” is correct.
- **DDI primes; Lakota provides SWFT technology and submission** under the platform model.

### Buyer-facing fingerprinting positioning (DDI)

- FD-258 / LiveScan **capture** by DDI
- Electronic submission via **SWFT-authorized technology partner (Lakota)** where contract requires — do not say “DDI is SWFT authorized”
- **Path to future DDI-direct SWFT (if pursued):** win applicable contract → **DD Form 254** → FCL triggers per security process — see master file.

**NEXUS / agents must read `COMPANY_INFO_MASTER.md` before asserting who holds SWFT authority — Lakota yes, DDI no.**

---

## OPERATIONAL NOTE: FMCSA CLEARINGHOUSE IDENTITY VERIFICATION (JUNE 2026)

**Source:** FMCSA Clearinghouse News, posted June 1, 2026 · FMCSA subscriber email to info@deedavis.biz

**NEXUS knowledge:** Existing registered **C/TPAs** (including DDI), MROs, SAPs, and certain employers must complete **identity verification by July 6, 2026** or lose Clearinghouse access until completed.

**DDI path:** clearinghouse.fmcsa.dot.gov → Log in → **My Dashboard → My Profile** → **Begin Identity Verification**

**Full reference:** `COMPLIANCE_KNOWLEDGE/CLEARINGHOUSE_IDENTITY_VERIFICATION.md`

**When NEXUS should surface this:** Clearinghouse emails/news, drug testing compliance questions, C/TPA program setup, active DOT/FMCSA bids (VIA, Oakland DTC, Yonkers, etc.) — not on unrelated tasks.

---

## CORRECTION 1: VERTEX Scope

### ❌ WRONG: Forecasting in VERTEX

**VERTEX** = Financial Excellence & Revenue Tracking Executive System

**What VERTEX Actually Does:**
- ✅ Invoice generation from all systems
- ✅ Payment tracking
- ✅ Expense management (subs, suppliers, field agents)
- ✅ Cash flow tracking (actuals, not forecasts)
- ✅ Revenue reconciliation
- ✅ Profitability analysis by business line

**What VERTEX Does NOT Do:**
- ❌ Opportunity forecasting (that's GPSS pipeline)
- ❌ Win probability scoring (that's GPSS AI)
- ❌ Revenue projections (that's GPSS pipeline value)

### ✅ CORRECT: Forecasting Lives in GPSS (Pipeline)

**GPSS** already has:
- Win Probability field (0-100%)
- Pipeline Stage tracking
- Estimated contract values
- AI scoring for likelihood

**Forecasting Report (GPSS generates):**
```
Pipeline Forecast (Next 90 Days)
├── Stage 5 (Submitted): $X (high probability)
├── Stage 4 (Development): $Y (medium probability)
└── Stage 3 (Resourcing): $Z (low probability)

Weighted Forecast: $[X + (Y×0.6) + (Z×0.3)]
```

**VERTEX receives actuals:**
- Won contracts → VERTEX invoices
- Paid invoices → VERTEX tracks cash

---

## CORRECTION 2: DOCUMENTS System Scope

### ❌ WRONG: Documents = Just Storage

**OLD THINKING:**
- DOCUMENTS = File repository
- Generation happens "somewhere else"

### ✅ CORRECT: DOCUMENTS = Generation Engine + Repository

**DOCUMENTS System Actually Does:**

#### 1. **DOCUMENT GENERATION** (Primary Function)
```
INPUT: RFP/Solicitation + Parameters
OUTPUT: Generated documents

Capabilities:
├── Generate Capability Statement
│   ├── Auto-extract logo (base64)
│   ├── Auto-select sector colors
│   ├── Apply ProposalBio (all 10 biohacks)
│   └── Output: HTML → PDF
├── Generate Quote Response/Proposal
│   ├── Compliance matrix auto-built
│   ├── Pricing tables from data
│   ├── Technical approach (AI-written)
│   └── Output: Full proposal package
├── Generate RFQ (Supplier-facing)
│   ├── Buyer protection applied
│   ├── DDI-2026-### numbering
│   └── Output: Safe-to-send RFQ
├── Generate Subcontractor Outreach
│   ├── 6-pillar vetting framework
│   ├── NDA/Agreement templates
│   └── Output: Sub package
└── Generate All Templates
    ├── Workflows use DOCUMENTS API
    └── Unified generation engine
```

#### 2. **DOCUMENT STORAGE** (Secondary Function)
```
All generated docs stored:
├── BIDS:RESOURCES/[BID]/SEND_TO_BUYER/
├── BIDS:RESOURCES/[BID]/SEND_TO_SUPPLIER/
├── CLIENTS/[CLIENT]/CONTRACTS/
└── Archive/retrieval via API
```

#### 3. **DOCUMENT RETRIEVAL**
```
Query: "Get cap statement for VA Dry Ice bid"
├── Searches file system
├── Returns path + content
└── Can regenerate if needed
```

---

## CRITICAL ISSUE: Manual NEXUS Usage (Outside Cursor)

### The Problem

**Current State:**
- NEXUS workflows require Cursor conversation
- "I found a solicitation" → Cursor interprets → executes
- No direct interface to trigger DOCUMENTS generation
- No self-service for manual RFP processing

**User Experience:**
```
❌ Current: Upload RFP → "Can you generate a cap statement?" 
             → Wait for AI → Get document
             
❌ Problem: Requires conversation, not tool-like
```

### The Solution: NEXUS Manual Interface

#### Option 1: **Command-Line Interface (CLI)**

```bash
# Trigger full workflow from terminal
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_cli.py --command intake --file "RFP_36C25626R0057.pdf"

# Output:
# ✅ Opportunity scored: 85/100 🔴 BID NOW
# ✅ Folder created: BIDS:RESOURCES/VA DRY ICE/
# ✅ Cap statement generated: SEND_TO_BUYER/...
# ✅ Next: Review and submit

# Generate specific document only
python3 nexus_cli.py --command generate --type capability_statement \
  --agency "VA" --service "Dry Ice Delivery" --sol "36C25626R0057"

# Check status
python3 nexus_cli.py --command status --bid "VA Dry Ice"

# Get today's priorities
python3 nexus_cli.py --command dashboard
```

#### Option 2: **Web Interface (Simple HTML Form)**

```html
<!-- Local web UI - nexus_local.html -->
<form id="generateForm">
  <h2>NEXUS Document Generator</h2>
  
  <select name="document_type">
    <option value="capability_statement">Capability Statement</option>
    <option value="quote_response">Quote Response</option>
    <option value="rfq">Supplier RFQ</option>
    <option value="sub_outreach">Subcontractor Outreach</option>
  </select>
  
  <input type="text" name="agency" placeholder="VA, USACE, DLA, etc.">
  <input type="text" name="service" placeholder="Drug Testing, Courier, etc.">
  <input type="text" name="sol_number" placeholder="36C25626R0057">
  
  <input type="file" name="rfp_file" accept=".pdf,.doc,.txt">
  
  <button type="submit">Generate</button>
</form>

<!-- On submit: Calls nexus_backend.py API, returns generated file path -->
```

#### Option 3: **Keyboard Shortcuts / Quick Actions in Cursor**

```
# .cursor/rules/nexus-quick-commands.mdc

## Magic Commands (Type in chat, no conversation needed)

/intake [file]
→ Triggers full opportunity intake
→ No "Do you want me to...?"
→ Just executes

/cap [agency] [service] [sol#]
→ Generates capability statement only
→ Immediate output

/quote [bid_name]
→ Generates quote response
→ Uses existing bid folder data

/status [bid_name]
→ Returns stage/status instantly
→ No conversational fluff

/dashboard
→ Returns morning brief instantly
→ Lists priorities
```

---

## PROPOSED: NEXUS API ENDPOINTS

### Backend API Structure

```python
# nexus_api.py - Flask/FastAPI endpoints

@app.route('/api/intake', methods=['POST'])
def opportunity_intake():
    """Full workflow: score → folder → docs → airtable"""
    file = request.files['rfp']
    result = execute_full_workflow(file)
    return jsonify({
        'score': result.score,
        'tier': result.tier,
        'folder': result.folder_path,
        'documents': result.generated_files,
        'airtable_id': result.record_id
    })

@app.route('/api/generate/capability', methods=['POST'])
def generate_capability():
    """Generate cap statement only"""
    params = request.json
    doc = documents.generate_capability_statement(
        agency=params['agency'],
        service=params['service'],
        sector=params.get('sector'),  # Auto-detect if not provided
        logo=params.get('logo_base64')  # Auto-extract if not provided
    )
    return jsonify({
        'html_path': doc.html_path,
        'pdf_path': doc.pdf_path,
        'preview_url': doc.preview_url
    })

@app.route('/api/generate/quote', methods=['POST'])
def generate_quote():
    """Generate quote response"""
    params = request.json
    doc = documents.generate_quote_response(
        solicitation=params['sol_data'],
        pricing=params['pricing_data'],
        past_performance=params['pp_data']
    )
    return jsonify({
        'document_path': doc.path,
        'page_count': doc.page_count,
        'compliance_matrix': doc.compliance_matrix
    })

@app.route('/api/status/<bid_id>', methods=['GET'])
def get_status(bid_id):
    """Get current stage and status"""
    status = airtable.get_bid_status(bid_id)
    return jsonify({
        'stage': status.stage,
        'step': status.current_step,
        'deadline': status.deadline,
        'days_remaining': status.days_left,
        'next_action': status.next_action
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Morning brief data"""
    return jsonify({
        'active_bids_by_stage': get_stage_counts(),
        'this_week_deadlines': get_week_deadlines(),
        'attention_needed': get_attention_items(),
        'recommendations': get_recommendations()
    })
```

---

## REVISED SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXUS PLATFORM                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   REVENUE   │  │   REVENUE   │  │   REVENUE   │        │
│  │   GPSS      │  │   DDCSS     │  │   GBIS      │        │
│  │  (Govt)     │  │ (Corporate) │  │  (Grants)   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │               │
│         └────────────────┼────────────────┘               │
│                          │                                 │
│              ┌───────────┴───────────┐                    │
│              │      COMPASS™         │                    │
│              │  (Quality Assurance)  │                    │
│              │   ProposalBio Scoring │                    │
│              └───────────┬───────────┘                    │
│                          │                                 │
│  ┌───────────────────────┼───────────────────────┐          │
│  │                       │                       │          │
│  ▼                       ▼                       ▼          │
│ ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│ │  ATLAS   │    │   PRISM    │    │   LBPC     │        │
│ │(Projects)│    │(Field Svcs)│    │ (Surplus)  │        │
│ └────┬─────┘    └────┬─────┘    └────┬─────┘        │
│      │               │               │                   │
│      └───────────────┼───────────────┘                   │
│                      │                                     │
│  ┌───────────────────┴───────────────────┐                │
│  │            VERTEX                     │                │
│  │      (Financial Center)               │                │
│  │  • Invoicing (actuals, not forecasts) │                │
│  │  • Payment tracking                   │                │
│  │  • Expense management                 │                │
│  │  • Cash flow (actuals)                │                │
│  └───────────────────┬───────────────────┘                │
│                      │                                     │
│  ┌───────────────────┴───────────────────┐                │
│  │          DOCUMENTS                  │                │
│  │    (Generation + Storage)           │                │
│  │                                     │                │
│  │  ┌───────────────────────────────┐  │                │
│  │  │     GENERATION ENGINE         │  │                │
│  │  │  • Capability Statements      │  │                │
│  │  │  • Quote Responses            │  │                │
│  │  │  • Proposals                  │  │                │
│  │  │  • RFQs                       │  │                │
│  │  │  • Sub Agreements             │  │                │
│  │  └───────────────────────────────┘  │                │
│  │                                     │                │
│  │  ┌───────────────────────────────┐  │                │
│  │  │     REPOSITORY                │  │                │
│  │  │  • All generated files          │  │                │
│  │  │  • Version history              │  │                │
│  │  │  • Archive/retrieval            │  │                │
│  │  └───────────────────────────────┘  │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │     AIRTABLE (Data Backbone)        │                │
│  │  • 69 tables across all systems     │                │
│  │  • Status tracking                  │                │
│  │  • Forecasting (GPSS pipeline)      │                │
│  │  • Not in VERTEX                    │                │
│  └─────────────────────────────────────┘                │
└───────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              INTERFACES (How You Use NEXUS)               │
│                                                              │
│  1. Cursor AI Chat (Conversational)                        │
│     └── Natural language: "I found a solicitation"          │
│                                                              │
│  2. CLI (Command Line)                                      │
│     └── python3 nexus_cli.py --intake RFP.pdf             │
│                                                              │
│  3. Web Form (Self-Service)                                │
│     └── Upload RFP → Select doc type → Generate           │
│                                                              │
│  4. API (Programmatic)                                     │
│     └── POST /api/generate/capability                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## KEY CHANGES SUMMARY

| Element | Old | New |
|---------|-----|-----|
| **VERTEX** | Had forecasting | ❌ Removed forecasting |
| **GPSS** | Just opportunities | ✅ Now includes pipeline forecasting |
| **DOCUMENTS** | Just storage | ✅ Generation engine + storage |
| **NEXUS Usage** | Cursor chat only | ✅ CLI + Web + API + Chat |

---

## NEXT STEPS

1. **Confirm system boundaries** (this correction)
2. **Build CLI interface** for manual NEXUS usage
3. **Build simple web form** for document generation
4. **Update all system documentation** with corrected scopes

**Does this correction align with your vision?**

---

## CORRECTION: CHAMPS PROVIDER ID — 6309049 (NOT 6309069)

**Date:** May 9, 2026
**Source of truth:** `COMPANY_INFO_MASTER.md` — Michigan CHAMPS section

- **Correct CHAMPS Provider ID:** **6309049**
- **Wrong ID that was in multiple files:** ~~6309069~~
- **Approved:** 03/23/2026, Active through 12/31/2999
- **Application #:** 20260323058125

**Files corrected May 9, 2026:**
- `NEMT_TPA_EXPANSION_STRATEGY.md`
- `HAVEN/STRATEGY/HAVEN_MEDICAID_ENROLLMENT_BY_STATE.md` (3 occurrences) — canonical path; ~~`NEXUS_LEARNING/HAVEN_MEDICAID_ENROLLMENT_BY_STATE.md`~~ superseded May 2026
- `NEXUS_TRAINING_DOCUMENT.md` (2 occurrences)
- `DDI_TPA_DIVISIONS.md` (1 occurrence)

**Files already correct:** `COMPANY_INFO_MASTER.md`, `PARTNER_ACCOUNT_UPDATES.md`, `HAP_CARESOURCE_OPERATIONS.md`, `SHIELD_SERVICE_FULFILLMENT_MAP.md`, `MDHHS_SHIELD_PILOT_PROPOSAL.md`, `ESSENTIALS/DDI_CONTRACT_MANAGEMENT_TPA_POSITIONING.md`, `CLIENT OUTREACH/MCO_MEDICAL_LAB_PHARMACY_COURIER_TARGETS.md`

**Rule:** Always pull CHAMPS ID from `COMPANY_INFO_MASTER.md`. It is **6309049**.